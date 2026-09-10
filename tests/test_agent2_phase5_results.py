from __future__ import annotations

from uuid import uuid4

import pytest
from pydantic import ValidationError

from mdi_api.agent2_errors import ScientificResultProjectionFailed
from mdi_api.scientific_objects.schemas import ScientificObjectRef
from mdi_api.scientific_results.artifact_loader import load_committed_json_artifact
from mdi_api.scientific_results.fingerprint import ScientificResultSourceFingerprint
from mdi_api.scientific_results.projectors.base import ScientificResultProjectionContext
from mdi_api.scientific_results.projectors.canonical import build_canonical_result_projectors, resolve_json_pointer
from mdi_api.scientific_results.schemas import FactSourceLocator, ScientificResultBundle
from mdi_api.scientific_results.service import ScientificResultProjectionService


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
        "parameters": {"r_max_angstrom": 8.0, "bin_width_angstrom": 0.1, "normalization": "number_density"},
        "rdf": {"r_angstrom": [0.25, 0.75], "g_r": [0.0, 1.2], "normalization": {"number_density_per_angstrom3": 0.05}},
        "limits": {"bin_count": 2},
    }, {"rdf.structure_count", "rdf.bin_count", "rdf.r_max", "rdf.bin_width", "rdf.number_density"}),
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
                         "highErrorSamples": [{
                             "sampleRef": "s3", "sampleKey": "dataset-object:s3",
                             "objectId": "dataset-object", "rowIndex": 2, "formula": "LiF",
                             "reducedFormula": "LiF", "chemicalSystem": "F-Li",
                             "target": 1.2, "prediction": 1.5, "residual": 0.3,
                             "absoluteError": 0.3,
                         }]}],
    }, {
        "ml.sample_count", "ml.mae", "ml.rmse", "ml.r2", "ml.mean_signed_error",
        "ml.median_absolute_error", "ml.high_error_sample_id", "ml.high_error_formula",
        "ml.high_error_target", "ml.high_error_prediction", "ml.high_error_residual",
        "ml.high_error_absolute_error",
    }),
    ("agent2.trajectory.msd", {
        "artifactType": "trajectory.msd", "schema_version": "phase10n4.trajectory_msd.v1",
        "lagTimesPs": [1.0, 2.0], "totalMsdAngstrom2": [0.1, 0.4],
        "coverage": {"frames": 20, "atoms": 4, "validLags": 2},
    }, {
        "trajectory.frame_count",
        "trajectory.msd_lag_count",
        "trajectory.msd_first_lag_time",
        "trajectory.msd_last_lag_time",
    }),
    ("agent2.trajectory.rdf", {
        "artifactType": "trajectory.rdf", "schema_version": "phase10n4.trajectory_rdf.v1",
        "trajectory": {"frameCount": 20, "atomCount": 4},
        "coverage": {"includedFrames": 18, "pairSamples": 108},
        "resolvedParameters": {
            "r_min_angstrom": 0.0, "r_max_angstrom": 8.0, "bin_count": 200,
        },
    }, {
        "trajectory.frame_count", "trajectory.atom_count",
        "trajectory.rdf_included_frames", "trajectory.rdf_pair_samples",
        "trajectory.rdf_r_min", "trajectory.rdf_r_max", "trajectory.rdf_bin_count",
    }),
    ("agent2.trajectory.diffusion", {
        "artifactType": "trajectory.diffusion", "schema_version": "phase10n4.trajectory_diffusion.v1",
        "diffusionEstimate": {"available": True, "value": 0.004, "unit": "angstrom^2/picosecond"},
        "fitWindow": {"startPs": 1.0, "endPs": 6.0, "pointCount": 11, "durationPs": 5.0},
        "fit": {"rSquared": 0.98, "rmseAngstrom2": 0.03}, "regimeDiagnostic": {"status": "DIFFUSIVE"},
    }, {
        "trajectory.diffusion_coefficient",
        "trajectory.diffusion_fit_start_time",
        "trajectory.diffusion_fit_end_time",
        "trajectory.diffusion_fit_point_count",
        "trajectory.diffusion_fit_duration",
        "trajectory.diffusion_fit_r2",
        "trajectory.diffusion_fit_rmse",
        "trajectory.diffusion_regime",
    }),
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


def test_materials_explorer_projects_bounded_sample_and_property_facts() -> None:
    payload = {
        "artifactType": "dataset.materials_explorer",
        "schemaVersion": "phase10k2.dataset_materials_explorer.v1",
        "overview": {"sampleCount": 3, "propertyCount": 2},
        "coverage": {"totalRows": 3, "totalColumns": 4},
        "composition": {
            "uniqueFormulaCount": 3,
            "coverage": {"valid": 3, "invalid": 0},
        },
        "quality": {"invalidFormulaCount": 0},
        "sampleIndex": [
            {
                "sampleRef": "mat-2",
                "sampleKey": "dataset-object:mat-2",
                "formula": "NaCl",
                "properties": {"band_gap": 5.6, "density": 2.16},
            }
        ],
        "properties": {
            "properties": [
                {
                    "column": "band_gap",
                    "unit": None,
                    "statistics": {"min": 1.1, "max": 5.6, "mean": 2.93, "median": 2.1},
                }
            ]
        },
    }
    projector = next(item for item in build_canonical_result_projectors() if item.projector_id == "agent2.data.materials_explorer")
    bundle = projector.project(_context([payload], projector_id=projector.projector_id)).bundle
    facts = {fact.predicate: fact for fact in bundle.facts}
    assert facts["dataset.sample_id"].value == "mat-2"
    assert facts["dataset.sample.band_gap"].value == 5.6
    assert facts["dataset.property.band_gap.max"].value == 5.6
    assert all(fact.source.artifact_locator for fact in bundle.facts)
    assert bundle.result_items[0].fact_refs


def test_rdf_curve_is_not_expanded_into_scalar_facts_and_replay_is_deterministic():
    projector_id, payload, _expected = CASES[0]
    projector = next(item for item in build_canonical_result_projectors() if item.projector_id == projector_id)
    first = projector.project(_context([payload], projector_id=projector_id)).bundle
    second = projector.project(_context([payload], projector_id=projector_id)).bundle
    assert len(first.facts) == 5
    assert first.model_dump(mode="json")["facts"] == second.model_dump(mode="json")["facts"]


def test_rdf_projects_authoritative_range_and_bin_width_with_units() -> None:
    projector_id, payload, _expected = CASES[0]
    projector = next(item for item in build_canonical_result_projectors() if item.projector_id == projector_id)

    bundle = projector.project(_context([payload], projector_id=projector_id)).bundle
    facts = {fact.predicate: fact for fact in bundle.facts}

    assert facts["rdf.r_max"].value == 8.0
    assert facts["rdf.r_max"].unit == "angstrom"
    assert facts["rdf.r_max"].source.artifact_locator == "/parameters/r_max_angstrom"
    assert facts["rdf.bin_width"].value == 0.1
    assert facts["rdf.bin_width"].unit == "angstrom"
    assert facts["rdf.bin_width"].source.artifact_locator == "/parameters/bin_width_angstrom"


def test_partial_execution_projects_only_successful_capability_outputs() -> None:
    payload = {
        "artifactType": "structure.rdf",
        "schema_version": "phase10e7.rdf.v1",
        "structureCount": 1,
        "parameters": {
            "r_max_angstrom": 8.0,
            "bin_width_angstrom": 0.1,
            "normalization": "number_density",
        },
        "rdf": {
            "r_angstrom": [0.25, 0.75],
            "g_r": [0.0, 1.2],
            "normalization": {"number_density_per_angstrom3": 0.05},
        },
        "limits": {"bin_count": 2},
    }
    context = _context([payload], projector_id="agent2.structure.rdf")
    context = ScientificResultProjectionContext(
        **{
            **context.__dict__,
            "execution_summary": {
                "execution_outcome": "PARTIAL",
                "summary_json": {
                    "outcome": "PARTIAL",
                    "successful_step_ids": ["step_2"],
                    "failed_step_ids": ["step_1"],
                    "steps": [
                        {"step_id": "step_1", "status": "FAILED"},
                        {"step_id": "step_2", "status": "SUCCEEDED"},
                    ],
                },
            },
            "capability_plan": {
                "steps": [
                    {
                        "step_id": "step_1",
                        "capability_id": "trajectory.msd",
                        "capability_version": "1.0",
                        "parameters": {},
                    },
                    {
                        "step_id": "step_2",
                        "capability_id": "structure.rdf",
                        "capability_version": "1.0",
                        "parameters": {},
                    },
                ]
            },
        }
    )

    bundle = ScientificResultProjectionService(
        repository_factory=None  # type: ignore[arg-type]
    ).project_context(context)

    assert bundle.execution_status.value == "PARTIAL"
    assert {fact.predicate for fact in bundle.facts} == {
        "rdf.structure_count",
        "rdf.bin_count",
        "rdf.r_max",
        "rdf.bin_width",
        "rdf.number_density",
    }
    assert {warning.code for warning in bundle.warnings} == {"PARTIAL_EXECUTION"}


def test_multi_capability_projection_keeps_per_artifact_exact_source_versions() -> None:
    turn_id = uuid4()
    band_ref = ScientificObjectRef(
        object_id=uuid4(),
        version_id=uuid4(),
        project_id="project",
        object_type="phonon.band",
        display_name="Phonon band",
    )
    dos_ref = ScientificObjectRef(
        object_id=uuid4(),
        version_id=uuid4(),
        project_id="project",
        object_type="phonon.dos",
        display_name="Phonon DOS",
    )
    context = ScientificResultProjectionContext(
        project_id="project",
        research_session_id="session",
        research_turn_id=str(turn_id),
        research_question="Compare the phonon band and DOS.",
        execution_summary={
            "outcome": "SUCCESS",
            "job_id": "job-phonon",
            "analysis_plan_id": "plan-phonon",
        },
        capability_plan={
            "steps": [
                {
                    "step_id": "step_1",
                    "capability_id": "phonon.band",
                    "capability_version": "1.0",
                    "parameters": {},
                },
                {
                    "step_id": "step_2",
                    "capability_id": "phonon.dos",
                    "capability_version": "1.0",
                    "parameters": {},
                },
            ]
        },
        analysis_plan={
            "schemaVersion": "0.2",
            "steps": [
                {
                    "stepId": "step_1",
                    "inputRefs": [
                        {
                            "refType": "normalized_object",
                            "ref": str(band_ref.version_id),
                        }
                    ],
                },
                {
                    "stepId": "step_2",
                    "inputRefs": [
                        {
                            "refType": "normalized_object",
                            "ref": str(dos_ref.version_id),
                        }
                    ],
                },
            ],
        },
        tool_calls=(
            {
                "id": "call-band",
                "stepId": "step_1",
                "toolId": "phonon.band",
            },
            {
                "id": "call-dos",
                "stepId": "step_2",
                "toolId": "phonon.dos",
            },
        ),
        artifacts=(
            {
                "id": "artifact-band",
                "toolCallId": "call-band",
                "stepId": "step_1",
                "contentType": "application/json",
                "filename": "phonon_band.json",
            },
            {
                "id": "artifact-dos",
                "toolCallId": "call-dos",
                "stepId": "step_2",
                "contentType": "application/json",
                "filename": "phonon_dos.json",
            },
        ),
        artifact_payloads={
            "artifact-band": {
                "schema_version": "phase10h.phonon_summary.v1",
                "branch_count": 6,
                "qpoint_count": 12,
                "frequency_unit": "terahertz",
                "frequency_min": -0.2,
                "frequency_max": 15.0,
                "imaginary_mode_count": 1,
            },
            "artifact-dos": {
                "schema_version": "phase10h2.phonon_dos_summary.v1",
                "frequency_unit": "terahertz",
                "frequency_min": -0.1,
                "frequency_max": 15.0,
                "observed_integral": 5.99,
                "projection_count": 2,
            },
        },
        source_object_refs=(band_ref, dos_ref),
    )

    bundle = ScientificResultProjectionService(
        repository_factory=None  # type: ignore[arg-type]
    ).project_context(context)

    assert {ref.version_id for ref in bundle.source_object_refs} == {
        band_ref.version_id,
        dos_ref.version_id,
    }
    items = {item.result_type: item for item in bundle.result_items}
    assert items["phonon.band"].scientific_object_refs == [band_ref]
    assert items["phonon.dos"].scientific_object_refs == [dos_ref]
    evidence_by_artifact = {
        item.artifact_id: item
        for item in bundle.evidence
        if item.artifact_id
    }
    assert evidence_by_artifact["artifact-band"].scientific_object_refs == [
        band_ref
    ]
    assert evidence_by_artifact["artifact-dos"].scientific_object_refs == [
        dos_ref
    ]
    assert set(bundle.provenance.source_object_version_ids) == {
        band_ref.version_id,
        dos_ref.version_id,
    }


def test_image_prose_and_filename_never_create_numeric_fact():
    projector_id, payload, expected = CASES[0]
    projector = next(item for item in build_canonical_result_projectors() if item.projector_id == projector_id)
    context = _context([payload, None, {"text": "band gap = 2.3 eV", "rmse": 0.2}], projector_id=projector_id,
                       content_types=["application/json", "image/png", "application/json"])
    bundle = projector.project(context).bundle
    assert {fact.predicate for fact in bundle.facts} == expected
    assert all(fact.source.artifact_id == "artifact-1" for fact in bundle.facts)


def test_committed_json_loader_ignores_mislabeled_markdown_and_checksums_json():
    class Storage:
        def __init__(self, payloads):
            self.payloads = payloads

        def get_bytes(self, key):
            return self.payloads[key]

    valid = b'{"schema_version":"fixture.v1","value":2}'
    storage = Storage({"valid": valid, "summary": b"# Summary"})
    assert load_committed_json_artifact(
        storage,
        {
            "type": "table_json",
            "contentType": "application/json",
            "storageKey": "valid",
            "sha256": __import__("hashlib").sha256(valid).hexdigest(),
        },
    ) == {"schema_version": "fixture.v1", "value": 2}
    assert load_committed_json_artifact(
        storage,
        {
            "type": "summary_md",
            "contentType": "application/json",
            "storageKey": "summary",
        },
    ) is None
    with pytest.raises(ValueError, match="checksum"):
        load_committed_json_artifact(
            storage,
            {
                "type": "table_json",
                "contentType": "application/json",
                "storageKey": "valid",
                "sha256": "0" * 64,
            },
        )


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
