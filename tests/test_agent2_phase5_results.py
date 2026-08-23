from __future__ import annotations

from uuid import uuid4

import pytest
from pydantic import ValidationError

from mdi_api.agent2_errors import ScientificResultProjectionFailed
from mdi_api.scientific_objects.schemas import ScientificObjectRef
from mdi_api.scientific_results.fingerprint import ScientificResultSourceFingerprint
from mdi_api.scientific_results.projectors.base import ScientificResultProjectionContext
from mdi_api.scientific_results.projectors.canonical import build_canonical_result_projectors, resolve_json_pointer
from mdi_api.scientific_results.schemas import FactSourceLocator, ScientificResultBundle


def _context(payloads, *, projector_id: str, content_types: list[str] | None = None):
    turn_id = uuid4()
    ref = ScientificObjectRef(object_id=uuid4(), version_id=uuid4(), project_id="project", object_type="structure.crystal")
    content_types = content_types or ["application/json"] * len(payloads)
    artifacts = tuple(
        {"id": f"artifact-{index}", "contentType": content_type, "filename": "rmse_0.2.json"}
        for index, content_type in enumerate(content_types, start=1)
    )
    return ScientificResultProjectionContext(
        project_id="project", research_session_id="session", research_turn_id=str(turn_id),
        research_question="Canonical scientific projection",
        execution_summary={"outcome": "SUCCESS", "job_id": "job-1", "analysis_plan_id": "plan-1"},
        capability_plan={"steps": [{"step_id": "step_1", "capability_id": projector_id.removeprefix("agent2."), "capability_version": "1.0", "parameters": {}}]},
        analysis_plan={"schemaVersion": "0.2"}, tool_calls=(), artifacts=artifacts,
        artifact_payloads={artifact["id"]: payload for artifact, payload in zip(artifacts, payloads, strict=True)},
        source_object_refs=(ref,),
    )


CASES = (
    ("agent2.structure.rdf", {
        "artifactType": "structure.rdf", "schema_version": "phase10e7.rdf.v1", "structureCount": 1,
        "rdf": {"r_angstrom": [0.25, 0.75], "g_r": [0.0, 1.2], "normalization": {"number_density_per_angstrom3": 0.05}},
        "limits": {"bin_count": 2},
    }, {"rdf.structure_count", "rdf.bin_count", "rdf.number_density"}),
    ("agent2.diffraction.theoretical_xrd", {
        "artifactType": "structure.xrd", "schema_version": "phase10e4.xrd_pattern.v1",
        "radiation": {"wavelength_angstrom": 1.54184},
        "pattern": {"peaks": [{"two_theta_deg": 28.4}], "peak_count": 1},
    }, {"xrd.peak_count", "xrd.wavelength"}),
    ("agent2.diffraction.experimental_theoretical_comparison", {
        "artifactType": "structure.experimental_xrd_comparison", "schemaVersion": "phase10n3.experimental_xrd_comparison.v1",
        "residualSummary": {"matchedCount": 2, "meanSignedDeltaTwoTheta": 0.01, "maeDeltaTwoTheta": 0.02,
                            "rmseDeltaTwoTheta": 0.025, "maxAbsoluteDeltaTwoTheta": 0.03,
                            "medianAbsoluteDeltaTwoTheta": 0.02, "unit": "degree"},
        "coverage": {"unmatchedExperimentalPeaks": 1, "unmatchedTheoreticalPeaks": 0},
    }, {"xrd.matched_peak_count", "xrd.unmatched_experimental_peak_count", "xrd.unmatched_theoretical_peak_count",
        "xrd.mean_peak_shift", "xrd.peak_shift_mae", "xrd.peak_shift_rmse", "xrd.max_peak_shift"}),
    ("agent2.ml.regression_evaluation", {
        "artifactType": "ml.regression_evaluation", "schemaVersion": "phase10k3.materials_ml_regression.v1",
        "evaluations": [{"taskId": "formation-energy:model-a", "unit": "eV/atom",
                         "metrics": {"sampleCount": 5, "mae": 0.1, "rmse": 0.2, "r2": 0.9,
                                     "meanSignedError": -0.01, "medianAbsoluteError": 0.08},
                         "highErrorSamples": [{"sampleKey": "dataset-object:s3"}]}],
    }, {"ml.sample_count", "ml.mae", "ml.rmse", "ml.r2", "ml.mean_signed_error", "ml.median_absolute_error"}),
    ("agent2.trajectory.msd", {
        "artifactType": "trajectory.msd", "schema_version": "phase10n4.trajectory_msd.v1",
        "lagTimesPs": [1.0, 2.0], "totalMsdAngstrom2": [0.1, 0.4],
        "coverage": {"frames": 20, "atoms": 4, "validLags": 2},
    }, {"trajectory.frame_count", "trajectory.msd_lag_count"}),
    ("agent2.trajectory.diffusion", {
        "artifactType": "trajectory.diffusion", "schema_version": "phase10n4.trajectory_diffusion.v1",
        "diffusionEstimate": {"available": True, "value": 0.004, "unit": "angstrom^2/picosecond"},
        "fit": {"rSquared": 0.98, "rmseAngstrom2": 0.03}, "regimeDiagnostic": {"status": "DIFFUSIVE"},
    }, {"trajectory.diffusion_coefficient", "trajectory.diffusion_fit_r2", "trajectory.diffusion_fit_rmse", "trajectory.diffusion_regime"}),
    ("agent2.phonon.band", {
        "schema_version": "phase10h.phonon_summary.v1", "branch_count": 6, "qpoint_count": 12,
        "frequency_unit": "terahertz", "frequency_min": -0.2, "frequency_max": 15.0, "imaginary_mode_count": 1,
    }, {"phonon.branch_count", "phonon.qpoint_count", "phonon.frequency_min", "phonon.frequency_max", "phonon.imaginary_mode_count"}),
    ("agent2.phonon.dos", {
        "schema_version": "phase10h2.phonon_dos_summary.v1", "frequency_unit": "terahertz",
        "frequency_min": -0.1, "frequency_max": 15.0, "observed_integral": 5.99, "projection_count": 2,
    }, {"phonon.dos_frequency_min", "phonon.dos_frequency_max", "phonon.dos_integral", "phonon.dos_projection_count"}),
    ("agent2.phonon.band_dos", {
        "schema_version": "phase10h.phonon_band_dos_summary.v1", "frequency_unit": "terahertz",
        "frequency_min": -0.2, "frequency_max": 15.0, "dos_integral": 5.99, "imaginary_band_mode_count": 1,
    }, {"phonon.frequency_min", "phonon.frequency_max", "phonon.dos_integral", "phonon.imaginary_mode_count"}),
)


@pytest.mark.parametrize(("projector_id", "payload", "expected_predicates"), CASES)
def test_canonical_projector_uses_verified_production_contract_and_grounded_facts(projector_id, payload, expected_predicates):
    projector = next(item for item in build_canonical_result_projectors() if item.projector_id == projector_id)
    bundle = projector.project(_context([payload], projector_id=projector_id)).bundle
    assert {fact.predicate for fact in bundle.facts} == expected_predicates
    assert bundle.result_items and bundle.tables
    for fact in bundle.facts:
        assert fact.source.artifact_id == "artifact-1"
        assert fact.source.artifact_locator
        assert resolve_json_pointer(payload, fact.source.artifact_locator) == fact.value


def test_rdf_curve_is_not_expanded_into_scalar_facts_and_replay_is_deterministic():
    projector_id, payload, _expected = CASES[0]
    projector = next(item for item in build_canonical_result_projectors() if item.projector_id == projector_id)
    first = projector.project(_context([payload], projector_id=projector_id)).bundle
    second = projector.project(_context([payload], projector_id=projector_id)).bundle
    assert len(first.facts) == 3
    assert first.model_dump(mode="json")["facts"] == second.model_dump(mode="json")["facts"]


def test_image_prose_and_filename_never_create_numeric_fact():
    projector_id, payload, expected = CASES[0]
    projector = next(item for item in build_canonical_result_projectors() if item.projector_id == projector_id)
    context = _context([payload, None, {"text": "band gap = 2.3 eV", "rmse": 0.2}], projector_id=projector_id,
                       content_types=["application/json", "image/png", "application/json"])
    bundle = projector.project(context).bundle
    assert {fact.predicate for fact in bundle.facts} == expected
    assert all(fact.source.artifact_id == "artifact-1" for fact in bundle.facts)


def test_unknown_or_malformed_primary_schema_fails_closed():
    projector = next(item for item in build_canonical_result_projectors() if item.projector_id == "agent2.structure.rdf")
    with pytest.raises(ScientificResultProjectionFailed):
        projector.project(_context([{"artifactType": "wrong", "schema_version": "phase10e7.rdf.v1", "structureCount": 1}],
                                   projector_id="agent2.structure.rdf"))


def test_fingerprint_is_order_independent():
    left = ScientificResultSourceFingerprint.compute(artifacts=[{"id": "a"}, {"id": "b"}], tool_calls=[{"id": "t"}], projector_ids=["p"])
    right = ScientificResultSourceFingerprint.compute(projector_ids=["p"], tool_calls=[{"id": "t"}], artifacts=[{"id": "a"}, {"id": "b"}])
    assert left == right


def test_invalid_fact_source_rejected():
    with pytest.raises(ValidationError):
        FactSourceLocator()


def test_dangling_bundle_fact_reference_rejected():
    ref = ScientificObjectRef(object_id=uuid4(), version_id=uuid4(), project_id="project", object_type="structure.crystal")
    with pytest.raises(ValidationError):
        ScientificResultBundle(
            schema_version="1.0", result_id=uuid4(), project_id="project", research_session_id="session", research_turn_id=uuid4(),
            research_question="x", source_object_refs=[ref], execution_status="SUCCESS", relevance_status="CURRENT",
            result_items=[{"id": "item", "result_type": "rdf", "role": "PRIMARY", "title": "RDF", "artifact_ids": [],
                           "scientific_object_refs": [ref], "fact_refs": ["missing"], "evidence_refs": []}],
            facts=[], figures=[], tables=[], output_object_refs=[], evidence=[], methods=[], limitations=[], warnings=[],
            provenance={}, projection_version="agent2.result/1.0",
        )
