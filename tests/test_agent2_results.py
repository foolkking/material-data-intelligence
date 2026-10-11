from __future__ import annotations

from uuid import uuid4
import json
from pathlib import Path
from dataclasses import replace

import pytest
from pydantic import ValidationError


def test_xrd_peak_facts_keep_strongest_retained_peak_identity_and_saved_values():
    from mdi_api.application.scientific_results.projectors.canonical import _xrd_peak_facts
    peaks = [{"two_theta_deg": 10 + i, "intensity": i + 1, "d_spacing_angstrom": 3.5,
              "structureId": "s", "hkls": [{"hkl": [1, -1, i]}]} for i in range(7)]
    payload = {"pattern": {"peaks": peaks}}
    before = json.dumps(payload)
    facts = _xrd_peak_facts({"id": "owned-artifact"}, payload)
    positions = [f for f in facts if f.predicate == "xrd.peak.two_theta"]
    assert [f.value for f in positions] == [16, 15, 14, 13, 12]
    assert positions[0].subject_ref == "owned-artifact:retained-peak-6"
    for fact in facts:
        assert resolve_json_pointer(payload, fact.source.artifact_locator) == fact.value
        assert fact.source.artifact_id == "owned-artifact"
    assert json.dumps(payload) == before
    assert _xrd_peak_facts({"id": "a"}, {"pattern": {"peaks": [{"intensity": float("nan")}, {"intensity": True}]}}) == []

from mdi_api.agent2_errors import ScientificResultProjectionFailed
from mdi_api.scientific_objects.schemas import ScientificObjectRef
from mdi_api.scientific_results.artifact_loader import load_committed_json_artifact
from mdi_api.scientific_results.fingerprint import ScientificResultSourceFingerprint
from mdi_api.scientific_results.projectors.base import ScientificResultProjectionContext
from mdi_api.scientific_results.projectors.canonical import build_canonical_result_projectors, resolve_json_pointer
from mdi_api.scientific_results.schemas import FactSourceLocator, ScientificResultBundle
from mdi_api.scientific_results.service import ScientificResultProjectionService
from mdi_artifact_core import (
    BRILLOUIN_ZONE_SCHEMA_VERSION,
    KPATH_SCHEMA_VERSION,
    RECIPROCAL_LATTICE_SCHEMA_VERSION,
)


ROOT = Path(__file__).resolve().parents[1]


def _persisted_projection():
    from tests.test_research_result_loss_recovery import _completed_execution

    factory, turn_id, job_id = _completed_execution()
    payload = {
        "artifactType": "structure.xrd", "schema_version": "phase10e4.xrd_pattern.v1",
        "radiation": {"wavelength_angstrom": 1.54184},
        "pattern": {"peaks": [{"two_theta_deg": 28.4}], "peak_count": 1},
    }
    service = ScientificResultProjectionService(factory, artifact_loader=lambda _: payload)
    return factory, turn_id, job_id, service


def test_result_provenance_preserves_persisted_plan_identities():
    factory, turn_id, job_id, service = _persisted_projection()
    with factory.session() as session:
        summary = session.agent2.research_execution_summaries.get_for_turn(turn_id)
        cap = session.agent2.research_capability_plans.get_for_turn(turn_id)
    assert "analysis_plan_id" not in summary
    assert summary["summary_json"]["analysis_plan_id"] == "plan_phase4"
    context, _ = service._load_projection_context(turn_id)
    bundle = service.project_context(context)
    assert bundle.provenance.analysis_plan_id == "plan_phase4"
    assert bundle.provenance.capability_plan_id == str(cap["id"])
    assert bundle.provenance.job_id == job_id
    assert bundle.provenance.execution_summary_id == str(summary["id"])
    # Derived identity must not change immutable fingerprint inputs.
    assert context.execution_summary == summary


@pytest.mark.parametrize("target,key,value", [
    ("turn", "analysis_plan_id", "foreign-plan"),
    ("turn", "job_id", "foreign-job"),
    ("summary", "research_turn_id", "foreign-turn"),
    ("payload", "research_turn_id", "foreign-turn"),
    ("payload", "analysis_plan_id", "foreign-plan"),
    ("payload", "analysis_plan_id", None),
    ("payload", "job_id", "foreign-job"),
    ("plan", "planId", "foreign-plan"),
    ("plan", "projectId", "foreign-project"),
    ("job", "planId", "foreign-plan"),
    ("job", "id", "foreign-job"),
    ("job", "projectId", "foreign-project"),
    ("cap", "research_turn_id", "foreign-turn"),
    ("cap", "id", None),
])
def test_result_projection_rejects_conflicting_persisted_identity(monkeypatch, target, key, value):
    factory, turn_id, job_id, service = _persisted_projection()
    with factory.session() as session:
        turn = session.agent2.research_turns.get(turn_id)
        summary = session.agent2.research_execution_summaries.get_for_turn(turn_id)
        plan = session.repositories.analysis_plans.get_plan(turn["analysis_plan_id"])
        job = session.repositories.jobs.get(job_id)
        cap = session.agent2.research_capability_plans.get_for_turn(turn_id)
        rows = {"turn": turn, "summary": summary, "payload": summary["summary_json"],
                "plan": plan, "job": job, "cap": cap}
        rows[target][key] = value
        monkeypatch.setattr(session.repositories.analysis_plans, "get_plan", lambda _: plan)
        monkeypatch.setattr(session.repositories.jobs, "get", lambda _: job)
        monkeypatch.setattr(session.agent2.research_capability_plans, "get_for_turn", lambda _: cap)
        with pytest.raises(ScientificResultProjectionFailed, match="execution provenance is inconsistent"):
            service._context_from_rows(session, turn, summary)
        assert session.agent2.scientific_result_snapshots.list_for_turn(turn_id) == []


def test_legacy_result_provenance_and_fingerprint_stay_immutable(monkeypatch):
    from sqlalchemy import update
    from mdi_api.db import scientific_result_snapshots
    from mdi_api.scientific_results.service import ScientificResultSnapshotService

    factory, turn_id, _, service = _persisted_projection()
    monkeypatch.setattr(service, "_enqueue_interpretation", lambda _: None)
    first = service.project_turn(turn_id)
    legacy_bundle = ScientificResultBundle.model_validate(first["bundle_json"])
    legacy_bundle.provenance.analysis_plan_id = ""
    legacy_bundle.provenance.capability_plan_id = None
    legacy_json = legacy_bundle.model_dump(mode="json")
    with factory.engine.begin() as connection:
        connection.execute(update(scientific_result_snapshots).where(
            scientific_result_snapshots.c.id == first["id"],
        ).values(bundle_json=legacy_json))
    assert ScientificResultSnapshotService(factory).get_latest_for_turn(turn_id) == legacy_bundle
    # Re-delivery computes the same fingerprint and returns the saved bundle.
    second = service.project_turn(turn_id)
    assert second["id"] == first["id"]
    assert second["source_fingerprint"] == first["source_fingerprint"]
    assert second["bundle_json"] == legacy_json
    with factory.session() as session:
        assert len(session.agent2.scientific_result_snapshots.list_for_turn(turn_id)) == 1


@pytest.mark.parametrize("question", ["  请解释所选能带点。\n保留原始问题。", "Explain the selected band point."])
def test_projection_preserves_original_question_instead_of_model_goal(question):
    from types import SimpleNamespace as NS
    turn = {"id": uuid4(), "project_id": "project", "research_session_id": "session", "user_message_id": "message", "analysis_plan_id": "plan", "job_id": "job"}
    message = {"role": "user", "session_id": "session", "content_summary": question}
    session = NS(
        agent2=NS(
            research_turns=NS(get_message=lambda key: message),
            research_capability_plans=NS(get_for_turn=lambda key: {"id": uuid4(), "research_turn_id": turn["id"], "plan_json": {}}),
            research_capability_resolutions=NS(get_for_turn=lambda key: None),
            research_context_snapshots=NS(get_for_turn=lambda key: {"research_goal": "Normalized English goal"}),
        ),
        repositories=NS(
            analysis_plans=NS(get_plan=lambda key: {"planId": "plan", "projectId": "project", "analysisPlan": {"goal": "Another English goal"}}),
            jobs=NS(get=lambda key: {"id": "job", "projectId": "project", "planId": "plan"}), tool_calls=NS(list_for_job=lambda key: []),
            artifacts=NS(list_for_job=lambda key: []),
        ),
    )
    summary = {"job_id": "job", "research_turn_id": turn["id"], "summary_json": {
        "job_id": "job", "research_turn_id": str(turn["id"]), "analysis_plan_id": "plan",
    }}
    context = ScientificResultProjectionService(None)._context_from_rows(session, turn, summary)
    assert context.research_question == question


@pytest.mark.parametrize("override", [{"role": "agent"}, {"session_id": "foreign"}, {"content_summary": "  "}, {"content_summary": None}])
def test_projection_rejects_missing_or_foreign_original_question(override):
    from types import SimpleNamespace as NS
    message = {"role": "user", "session_id": "session", "content_summary": "Original", **override}
    session = NS(agent2=NS(research_turns=NS(get_message=lambda key: message)))
    with pytest.raises(ScientificResultProjectionFailed, match="original research question"):
        ScientificResultProjectionService(None)._context_from_rows(
            session, {"user_message_id": "message", "research_session_id": "session"}, {},
        )


def _selected_electronic_context(tmp_path, kind="band", projection=False):
    from tests.test_electronic_band_dos import band_resource, dos_resource, _execute
    tool = "electronic.band_structure" if kind == "band" else "electronic.dos"
    resource = band_resource() if kind == "band" else dos_resource()
    payload = _execute(tmp_path, tool, resource)
    context = _context([payload], projector_id=f"agent2.{tool}")
    ref = context.source_object_refs[0].model_copy(update={"object_type": tool})
    locator = {"spin_channel_id": "none", "energy_ev": 999999, "dos_value": 999999}
    locator.update({"band_id": "v1", "kpoint_id": "kp_x", "kpoint_index": 1} if kind == "band" else
        {"dos_channel_id": "si_s" if projection else "total", "channel_kind": "projection" if projection else "total", "energy_point_index": 1, **({"projection_kind": "orbital"} if projection else {})})
    return replace(context, source_object_refs=(ref,), artifacts=({**context.artifacts[0], "toolCallId": "electronic-call"},),
        tool_calls=({"id": "electronic-call", "stepId": "step_1", "toolId": tool},),
        analysis_plan={"steps": [{"stepId": "step_1", "inputRefs": [{"refType": "normalized_object", "ref": str(ref.version_id)}]}]},
        scientific_selections=({"object_ref": ref.model_dump(mode="json"), "selection_type": "ELECTRONIC_BAND_STATE" if kind == "band" else "ELECTRONIC_DOS_POINT", "semantic_locator": locator},))


def _project_electronic(context, kind="band"):
    name = "agent2.electronic.band_structure" if kind == "band" else "agent2.electronic.dos"
    return next(item for item in build_canonical_result_projectors() if item.projector_id == name).project(context)


@pytest.mark.parametrize("kind,projection,expected", [("band", False, -0.5), ("dos", False, 0.1), ("dos", True, 0.04)])
def test_electronic_selected_values_are_committed_facts(tmp_path, kind, projection, expected):
    context = _selected_electronic_context(tmp_path, kind, projection)
    result = _project_electronic(context, kind)
    facts = {fact.predicate: fact for fact in result.bundle.facts}
    assert result.projector_version == "1.2"
    assert facts["electronic.selected_energy"].value == (-0.5 if kind == "band" else 0)
    assert facts["electronic.selected_energy"].unit == "eV"
    assert facts["electronic.selected_spin_channel"].value == "none"
    if kind == "band":
        assert facts["electronic.selected_band_id"].value == "v1"
        assert facts["electronic.selected_kpoint_id"].value == "kp_x"
    else:
        assert facts["electronic.selected_dos_value"].value == expected
        assert facts["electronic.selected_dos_value"].unit == "states_per_ev_cell"
    for fact in facts.values():
        assert resolve_json_pointer(context.artifact_payloads["artifact-1"], fact.source.artifact_locator) == fact.value
    assert "999999" not in result.bundle.model_dump_json()


@pytest.mark.parametrize("kind,field,value", [("band", "spin_channel_id", "down"), ("band", "kpoint_index", True), ("band", "kpoint_index", 99), ("band", "kpoint_id", "kp_g"), ("band", "band_id", "missing"), ("dos", "energy_point_index", -1), ("dos", "energy_point_index", False), ("dos", "channel_kind", "unknown"), ("dos", "dos_channel_id", "missing")])
def test_electronic_conflicting_selection_fails_explicitly(tmp_path, kind, field, value):
    context = _selected_electronic_context(tmp_path, kind)
    selection = context.scientific_selections[0]
    context = replace(context, scientific_selections=({**selection, "semantic_locator": {**selection["semantic_locator"], field: value}},))
    with pytest.raises(ScientificResultProjectionFailed):
        _project_electronic(context, kind)


@pytest.mark.parametrize("kind", ["band", "dos"])
def test_electronic_selection_cannot_cross_executed_source_versions(tmp_path, kind):
    context = _selected_electronic_context(tmp_path, kind)
    context = replace(context, analysis_plan={"steps": [{"stepId": "step_1", "inputRefs": [{"refType": "normalized_object", "ref": str(uuid4())}]}]})
    assert not any("selected_" in fact.predicate for fact in _project_electronic(context, kind).bundle.facts)


def test_electronic_same_band_id_uses_selected_spin_and_output_energy_reference(tmp_path):
    from copy import deepcopy
    from tests.test_electronic_band_dos import band_resource, _execute, _seal
    context = _selected_electronic_context(tmp_path / "base")
    resource = band_resource()
    up = deepcopy(resource["bands"])
    down = deepcopy(resource["bands"])
    for band in up:
        band["spinChannel"] = "up"
    for band in down:
        band["spinChannel"] = "down"
        band["energiesEv"] = [value + 4 for value in band["energiesEv"]]
    resource.update(spinMode="spin_polarized", bands=up + down, fermiEnergyEv=1)
    payload = _execute(tmp_path / "spin", "electronic.band_structure", _seal(resource), {"energy_reference": "fermi"})
    selection = context.scientific_selections[0]
    context = replace(context, artifact_payloads={"artifact-1": payload}, scientific_selections=({**selection,
        "semantic_locator": {**selection["semantic_locator"], "spin_channel_id": "down"}},))
    facts = {fact.predicate: fact for fact in _project_electronic(context).bundle.facts}
    assert facts["electronic.selected_energy"].value == 2.5
    assert facts["electronic.selected_spin_channel"].value == "down"
    assert facts["electronic.energy_reference"].value == payload["energy"]["reference"]
    for fact in facts.values():
        assert resolve_json_pointer(payload, fact.source.artifact_locator) == fact.value


def _selected_phonon_context():
    payload = json.loads((ROOT / "tests/fixtures/phonon_contract/stable_band.json").read_text())
    context = _context([payload], projector_id="agent2.phonon.band")
    ref = context.source_object_refs[0].model_copy(update={"object_type": "phonon.band_structure"})
    return replace(context, source_object_refs=(ref,),
        artifacts=({**context.artifacts[0], "toolCallId": "call-band"},),
        tool_calls=({"id": "call-band", "stepId": "step_1", "toolId": "phonon.band"},),
        analysis_plan={"steps": [{"stepId": "step_1", "inputRefs": [{"refType": "normalized_object", "ref": str(ref.version_id)}]}]},
        scientific_selections=({"object_ref": ref.model_dump(mode="json"), "selection_type": "PHONON_Q_POINT",
            "semantic_locator": {"qpoint_index": 0, "branch_index": 5, "q_point_id": "q:0", "branch_id": "branch:5", "frequency_thz": 999999}},))


def test_selected_phonon_facts_read_saved_mode_not_client_frequency():
    context = _selected_phonon_context()
    projector = next(item for item in build_canonical_result_projectors() if item.projector_id == "agent2.phonon.band")
    result = projector.project(context)
    assert result.projector_version == "1.3"
    assert result.bundle.tables == []
    facts = {fact.predicate: fact for fact in result.bundle.facts}
    assert facts["phonon.atom_count"].value == 2
    assert facts["phonon.selected_frequency"].value == 4.2
    assert facts["phonon.selected_frequency"].unit == "terahertz"
    assert facts["phonon.selected_qpoint_index"].value == 0
    assert facts["phonon.selected_branch_index"].value == 5
    for fact in facts.values():
        assert resolve_json_pointer(context.artifact_payloads["artifact-1"], fact.source.artifact_locator) == fact.value
    assert "999999" not in result.bundle.model_dump_json()


@pytest.mark.parametrize("field,value", [("qpoint_index", -1), ("qpoint_index", 3), ("qpoint_index", True), ("branch_index", 6), ("branch_index", False), ("q_point_id", "q:1"), ("branch_id", "branch:0")])
def test_selected_phonon_invalid_indices_and_identities_fail(field, value):
    context = _selected_phonon_context()
    selection = context.scientific_selections[0]
    context = replace(context, scientific_selections=({**selection, "semantic_locator": {**selection["semantic_locator"], field: value}},))
    projector = next(item for item in build_canonical_result_projectors() if item.projector_id == "agent2.phonon.band")
    with pytest.raises(ScientificResultProjectionFailed):
        projector.project(context)


def test_selected_phonon_does_not_use_sibling_input_version():
    context = replace(_selected_phonon_context(), analysis_plan={"steps": [{"stepId": "step_1", "inputRefs": [{"refType": "normalized_object", "ref": str(uuid4())}]}]})
    projector = next(item for item in build_canonical_result_projectors() if item.projector_id == "agent2.phonon.band")
    assert not any("selected_" in fact.predicate for fact in projector.project(context).bundle.facts)


def test_selected_phonon_requires_registered_source_type_not_result_type():
    context = _selected_phonon_context()
    context = replace(context, source_object_refs=(context.source_object_refs[0].model_copy(update={"object_type": "phonon.band"}),))
    projector = next(item for item in build_canonical_result_projectors() if item.projector_id == "agent2.phonon.band")
    assert not any("selected_" in fact.predicate for fact in projector.project(context).bundle.facts)


def _selected_volumetric_context(tmp_path, source_name="CHGCAR.collinear", channel=1, params=None):
    from tests.test_volumetric_parser_adapter import _context as adapter_context, _request, _read, FIXTURES
    from mdi_material_parsers import parse_file
    from mdi_adapters import VolumetricDataAdapter
    source = parse_file(FIXTURES / source_name, dataset_id="dataset_volume").objects[0]
    artifacts = VolumetricDataAdapter().execute(adapter_context(tmp_path, source), _request(params))
    payload = _read(tmp_path, artifacts, "volumetric_dataset.json")
    context = _context([payload], projector_id="agent2.volumetric.data")
    ref = context.source_object_refs[0].model_copy(update={"object_type": "volumetric.field"})
    return replace(context, source_object_refs=(ref,), artifacts=({**context.artifacts[0], "toolCallId": "volume-call"},),
        tool_calls=({"id": "volume-call", "stepId": "step_1", "toolId": "structure.volumetric_data"},),
        analysis_plan={"steps": [{"stepId": "step_1", "inputRefs": [{"refType": "normalized_object", "ref": str(ref.version_id)}]}]},
        scientific_selections=({"object_ref": ref.model_dump(mode="json"), "selection_type": "VOLUMETRIC_FIELD",
            "semantic_locator": {"field_id": f"channel:{channel}", "source_channel_index": channel, "field_locator": f"/channels/{channel}", "minimum": 999999}},))


@pytest.mark.parametrize("source,channel,field_name", [("CHGCAR.collinear", 1, "spin_difference"), ("CHGCAR.noncollinear", 2, "magnetization_vector"), ("orthogonal.cube", 0, "scalar")])
def test_selected_volumetric_facts_follow_saved_component_mapping(tmp_path, source, channel, field_name):
    context = _selected_volumetric_context(tmp_path, source, channel)
    projector = next(item for item in build_canonical_result_projectors() if item.projector_id == "agent2.volumetric.data")
    result = projector.project(context)
    facts = {fact.predicate: fact for fact in result.bundle.facts if ".selected_" in fact.predicate}
    assert facts["volumetric.selected_field_name"].value == field_name
    for fact in facts.values():
        assert resolve_json_pointer(context.artifact_payloads["artifact-1"], fact.source.artifact_locator) == fact.value
    assert "999999" not in result.bundle.model_dump_json()


@pytest.mark.parametrize("failure", ["filtered", "wrong_id", "wrong_type", "negative", "missing_mapping", "duplicate_mapping"])
def test_selected_volumetric_missing_or_ambiguous_channels_fail(tmp_path, failure):
    context = _selected_volumetric_context(tmp_path, params={"field_selection": "total_only"} if failure == "filtered" else None)
    if failure in {"wrong_id", "wrong_type", "negative"}:
        selection = context.scientific_selections[0]
        change = {"field_id": "channel:0"} if failure == "wrong_id" else {"source_channel_index": True if failure == "wrong_type" else -1}
        context = replace(context, scientific_selections=({**selection, "semantic_locator": {**selection["semantic_locator"], **change}},))
    elif failure in {"missing_mapping", "duplicate_mapping"}:
        payload = context.artifact_payloads["artifact-1"]
        field = next(item for item in payload["fields"] if item["field_name"] == "spin_difference")
        mappings = field["provenance"]["transformations"]
        mapping = next(item for item in mappings if item["detail"].startswith("SOURCE_CHANNEL_V1:"))
        if failure == "missing_mapping": mappings.remove(mapping)
        else: mappings.append(dict(mapping))
    projector = next(item for item in build_canonical_result_projectors() if item.projector_id == "agent2.volumetric.data")
    with pytest.raises(ScientificResultProjectionFailed):
        projector.project(context)


def test_selected_volumetric_does_not_bind_a_sibling_version(tmp_path):
    context = replace(_selected_volumetric_context(tmp_path), analysis_plan={"steps": [{"stepId": "step_1", "inputRefs": [{"refType": "normalized_object", "ref": str(uuid4())}]}]})
    projector = next(item for item in build_canonical_result_projectors() if item.projector_id == "agent2.volumetric.data")
    assert not any("selected_" in fact.predicate for fact in projector.project(context).bundle.facts)


def test_volumetric_dataset_projects_grid_facts_from_validated_saved_metadata():
    fixture = json.loads((ROOT / "tests/fixtures/volumetric_contract/cubic_constant_scalar.json").read_text())
    payload = fixture["raw_dataset"]
    context = _context([payload], projector_id="agent2.volumetric.data")
    projector = next(item for item in build_canonical_result_projectors() if item.projector_id == "agent2.volumetric.data")
    result = projector.project(context)
    assert result.projector_version == "1.9"
    assert result.bundle.tables == []
    assert result.bundle.result_items[0].artifact_ids == ["artifact-1"]
    facts = {fact.predicate: fact for fact in result.bundle.facts}
    assert facts["volumetric.grid_size_a"].value == 4
    assert facts["volumetric.grid_size_b"].value == 4
    assert facts["volumetric.grid_size_c"].value == 4
    assert facts["volumetric.length_unit"].value == "angstrom"
    assert facts["volumetric.boundary_a"].value == "periodic"
    assert facts["volumetric.endpoint_policy"].value == "excluded"
    assert not any(item.code.startswith("ELF_") for item in result.bundle.limitations)
    assert not any(item.code.startswith("PARTIAL_DENSITY_") for item in result.bundle.limitations)
    for fact in facts.values():
        assert fact.source.artifact_id == "artifact-1"
        assert resolve_json_pointer(payload, fact.source.artifact_locator) == fact.value


def test_volumetric_field_only_does_not_invent_missing_grid_dimensions():
    fixture = json.loads((ROOT / "tests/fixtures/volumetric_contract/cubic_constant_scalar.json").read_text())
    context = _context([fixture["raw_dataset"]["fields"][0]], projector_id="agent2.volumetric.data")
    projector = next(item for item in build_canonical_result_projectors() if item.projector_id == "agent2.volumetric.data")
    facts = projector.project(context).bundle.facts
    assert any(fact.predicate == "volumetric.minimum" for fact in facts)
    assert not any(fact.predicate.startswith("volumetric.grid_size") for fact in facts)


@pytest.mark.parametrize("converted", [True, False, None])
def test_volumetric_conversion_history_is_explicit_not_inferred_from_units(converted):
    from mdi_api.application.scientific_results.projectors.canonical import _volumetric_facts

    payload = {"normalization_semantics": "source_native", "unit": {"source_unit": "electron/angstrom^3", "canonical_unit": "electron/angstrom^3"}}
    if converted is not None:
        payload["unit"]["conversion_applied"] = converted
    before = json.dumps(payload)
    facts = {fact.predicate: fact for fact in _volumetric_facts({"id": "a"}, payload)}
    if converted is None:
        assert "volumetric.unit_conversion_applied" not in facts
    else:
        assert facts["volumetric.unit_conversion_applied"].value is converted
    assert "volumetric.unit_conversion_factor" not in facts
    assert "volumetric.statistics_authority" not in facts
    assert json.dumps(payload) == before


@pytest.mark.parametrize("source", ["CHGCAR.collinear", "ELFCAR"])
def test_volumetric_integrals_keep_the_saved_physical_meaning(tmp_path, source):
    from tests.test_charge_spin_density import _execute

    _, dataset, _ = _execute(tmp_path, source)
    projector = next(item for item in build_canonical_result_projectors() if item.projector_id == "agent2.volumetric.data")
    for field in dataset["fields"]:
        facts = {fact.predicate: fact for fact in projector.project(_context([field], projector_id="agent2.volumetric.data")).bundle.facts}
        assert facts["volumetric.integral_semantics"].value == field["integral_semantics"]
        assert facts["volumetric.normalization_semantics"].value == field["normalization_semantics"]
        for predicate, pointer in (
            ("volumetric.source_unit", "/unit/source_unit"),
            ("volumetric.unit_conversion_applied", "/unit/conversion_applied"),
            ("volumetric.unit_conversion_factor", "/unit/conversion_factor"),
            ("volumetric.statistics_authority", "/statistics/authority"),
        ):
            fact = facts[predicate]
            assert fact.value == resolve_json_pointer(field, pointer)
            assert fact.source.artifact_locator == pointer
        assert type(facts["volumetric.unit_conversion_applied"].value) is bool
        if source == "CHGCAR.collinear":
            integral = facts["volumetric.integral"]
            assert integral.value == field["statistics"]["stored_components"][0]["integral"]
            assert integral.unit == ("bohr_magneton" if field["quantity"] == "magnetization_density" else "electron")
            assert resolve_json_pointer(field, integral.source.artifact_locator) == integral.value
        else:
            assert "volumetric.integral" not in facts


@pytest.mark.parametrize("source, hint, unit", [("LOCPOT", "auto", "electronvolt"), ("orthogonal.cube", "electrostatic_potential", "hartree")])
def test_potential_statistics_preserve_saved_mean_volume_integral_and_reference(tmp_path, source, hint, unit):
    from tests.test_electrostatic_potential import _execute

    _, dataset, _ = _execute(tmp_path, source, hint)
    field = dataset["fields"][0]
    before = json.dumps(field)
    projector = next(item for item in build_canonical_result_projectors() if item.projector_id == "agent2.volumetric.data")
    facts = {fact.predicate: fact for fact in projector.project(_context([field], projector_id="agent2.volumetric.data")).bundle.facts}
    for predicate, pointer, expected_unit in (
        ("volumetric.mean", "/statistics/stored_components/0/mean", unit),
        ("volumetric.volume_integral", "/statistics/stored_components/0/integral", f"{unit}*angstrom^3"),
        ("volumetric.potential_reference", "/potential_reference/kind", None),
        ("volumetric.potential_shift", "/potential_reference/shift_amount", unit),
    ):
        fact = facts[predicate]
        assert fact.value == resolve_json_pointer(field, pointer)
        assert fact.source.artifact_locator == pointer
        assert fact.unit == expected_unit
    assert "volumetric.integral" not in facts
    assert facts["volumetric.mean"].value != facts["volumetric.volume_integral"].value
    assert json.dumps(field) == before


@pytest.mark.parametrize("dataset_only", [False, True])
def test_elf_saved_statistics_retain_numeric_integral_and_specific_scientific_limits(tmp_path, dataset_only):
    from tests.test_charge_spin_density import _execute

    _, dataset, _ = _execute(tmp_path, "ELFCAR")
    field = dataset["fields"][0]
    payload = dataset if dataset_only else field
    before = json.dumps(payload)
    projector = next(item for item in build_canonical_result_projectors() if item.projector_id == "agent2.volumetric.data")
    bundle = projector.project(_context([payload], projector_id="agent2.volumetric.data")).bundle
    codes = {limitation.code for limitation in bundle.limitations}
    assert "ELF_INTEGRAL_NOT_POPULATION" in codes
    assert "ELF_CONTOURS_NOT_TOPOLOGY" in codes
    if not dataset_only:
        facts = {fact.predicate: fact for fact in bundle.facts}
        integral = facts["volumetric.volume_integral"]
        assert integral.value == pytest.approx(3.1)
        assert integral.unit == "angstrom^3"
        assert integral.source.artifact_locator == "/statistics/stored_components/0/integral"
        assert resolve_json_pointer(field, integral.source.artifact_locator) == integral.value
        assert facts["volumetric.mean"].value == pytest.approx(0.3875)
        assert facts["volumetric.mean"].unit == "dimensionless"
        assert "volumetric.integral" not in facts
    assert json.dumps(payload) == before


@pytest.mark.parametrize("dataset_only", [False, True])
def test_partial_density_preserves_statistics_without_inventing_orbital_identity(tmp_path, dataset_only):
    from tests.test_charge_spin_density import _execute
    from mdi_api.application.interpretation.assembler import InterpreterInputAssembler
    from mdi_api.application.scientific_reports.assembler import ReportComposerInputAssembler

    _, dataset, _ = _execute(tmp_path, "PARCHG")
    field = dataset["fields"][0]
    payload = dataset if dataset_only else field
    before = json.dumps(payload)
    projector = next(item for item in build_canonical_result_projectors() if item.projector_id == "agent2.volumetric.data")
    bundle = projector.project(_context([payload], projector_id="agent2.volumetric.data")).bundle
    limits = {item.code: item for item in bundle.limitations}
    assert "PARTIAL_DENSITY_IDENTITY_NOT_ESTABLISHED" in limits
    assert "PARTIAL_DENSITY_INTEGRAL_NOT_OCCUPANCY" in limits
    assert not any(code.startswith("ELF_") for code in limits)
    for code in ("PARTIAL_DENSITY_IDENTITY_NOT_ESTABLISHED", "PARTIAL_DENSITY_INTEGRAL_NOT_OCCUPANCY"):
        assert limits[code].source_ref == "artifact-1"
    interpretation_input, _ = InterpreterInputAssembler().assemble(
        bundle=bundle, question="Explain this partial density", relevance_status="CURRENT",
    )
    report_input, _ = ReportComposerInputAssembler().assemble(
        bundle=bundle, interpretation={}, relevance_status="CURRENT",
    )
    for limit in limits.values():
        assert limit.message in interpretation_input.model_dump_json()
        assert limit.message in json.dumps(report_input)
    if not dataset_only:
        facts = {item.predicate: item for item in bundle.facts}
        for predicate, value, unit in (
            ("volumetric.minimum", 0.5, "electron/angstrom^3"),
            ("volumetric.maximum", 4.0, "electron/angstrom^3"),
            ("volumetric.mean", 2.25, "electron/angstrom^3"),
            ("volumetric.integral", 18.0, "electron"),
            ("volumetric.unit_conversion_factor", 0.125, None),
        ):
            fact = facts[predicate]
            assert fact.value == pytest.approx(value)
            assert fact.unit == unit
            assert resolve_json_pointer(field, fact.source.artifact_locator) == fact.value
        assert facts["volumetric.normalization_semantics"].value == "source_native"
        assert facts["volumetric.integral_semantics"].value == "electron_count"
        assert not any("occupancy" in name or "orbital_id" in name for name in facts)
    assert json.dumps(payload) == before


def _selected_trajectory_context():
    payload = json.loads((ROOT / "tests/fixtures/trajectory_viewer/fixed_lattice_md_12_frames.json").read_text())
    context = _context([payload], projector_id="agent2.trajectory.viewer_scene")
    ref = context.source_object_refs[0].model_copy(update={"object_type": "trajectory.atomic"})
    return replace(context,
        source_object_refs=(ref,),
        artifacts=({**context.artifacts[0], "toolCallId": "call-trajectory"},),
        tool_calls=({"id": "call-trajectory", "stepId": "step_1", "toolId": "trajectory.trajectory_viewer"},),
        analysis_plan={"steps": [{"stepId": "step_1", "inputRefs": [{"refType": "normalized_object", "ref": str(ref.version_id)}]}]},
        scientific_selections=({
            "object_ref": ref.model_dump(mode="json"), "selection_type": "TRAJECTORY_ATOM",
            "semantic_locator": {"frame_index": 11, "frame_id": "frame:11", "atom_index": 1,
                                 "species": "FAKE", "source_x": 999999, "position_unit": "FAKE"},
        },),
    )


def test_trajectory_facts_use_exact_committed_positions_and_units_not_ui_values():
    context = _selected_trajectory_context()
    projector = next(item for item in build_canonical_result_projectors() if item.projector_id == "agent2.trajectory.viewer_scene")
    bundle = projector.project(context).bundle
    assert projector.version == projector.project(context).projector_version == "1.3"
    assert bundle.tables == []
    assert bundle.result_items[0].artifact_ids == ["artifact-1"]
    assert bundle.evidence
    facts = {fact.predicate: fact for fact in bundle.facts}
    assert facts["trajectory.frame_count"].value == 12
    assert facts["trajectory.selected_frame_number"].value == 12
    assert facts["trajectory.selected_atom_number"].value == 2
    assert facts["trajectory.selected_atom_species"].value == "Si"
    assert facts["trajectory.selected_frame_time"].value == 11
    assert facts["trajectory.selected_frame_time"].unit == "femtosecond"
    assert facts["trajectory.periodic_boundary_a"].value is True
    for axis in "xyz":
        fact = facts[f"trajectory.selected_atom_source_{axis}"]
        assert fact.value == resolve_json_pointer(context.artifact_payloads["artifact-1"], fact.source.artifact_locator)
        assert fact.unit == "fractional"
    assert "999999" not in bundle.model_dump_json()
    assert "FAKE" not in bundle.model_dump_json()
    assert set(fact.fact_id for fact in bundle.facts).issubset(bundle.result_items[0].fact_refs)


def test_trajectory_selection_does_not_attach_to_a_different_executed_version():
    context = _selected_trajectory_context()
    from mdi_api.application.scientific_results.projectors.trajectory import trajectory_view_facts
    context = replace(context, analysis_plan={"steps": [{"stepId": "step_1", "inputRefs": [{"refType": "normalized_object", "ref": str(uuid4())}]}]})
    facts = trajectory_view_facts(context, context.artifacts[0], context.artifact_payloads["artifact-1"])
    assert not any("selected_" in fact.predicate for fact in facts)


@pytest.mark.parametrize("field,value", [("frame_index", 12), ("frame_index", -1), ("frame_index", True), ("frame_id", "frame:0"), ("atom_index", 4), ("atom_id", "atom:0:0.0.0")])
def test_trajectory_selection_requires_a_real_frame_and_atom(field, value):
    context = _selected_trajectory_context()
    selection = context.scientific_selections[0]
    context = replace(context, scientific_selections=({**selection, "semantic_locator": {**selection["semantic_locator"], field: value}},))
    from mdi_api.application.scientific_results.projectors.trajectory import trajectory_view_facts
    with pytest.raises(ScientificResultProjectionFailed):
        trajectory_view_facts(context, context.artifacts[0], context.artifact_payloads["artifact-1"])


ML_REGRESSION_COMPANION_TOOLS = (
    "ml.basic_metrics",
    "ml.density_scatter",
    "ml.error_distribution",
    "ml.outlier_table",
)


def test_regression_figures_use_the_exact_committed_producer_title():
    projector_id, payload, _ = next(item for item in CASES if item[0] == "agent2.ml.regression_evaluation")
    context = _context([payload], projector_id=projector_id, companion_tool_ids=ML_REGRESSION_COMPANION_TOOLS)
    context = replace(context,
        artifacts=tuple({**a, "jobId": "job-1", "projectId": "project",
                         **({"type": "plotly_json"} if a.get("toolCallId") in {"tool-call-2", "tool-call-3"} else {})}
                        for a in context.artifacts),
        tool_calls=tuple({**c, "jobId": "job-1"} for c in context.tool_calls))
    before = json.dumps(context.artifacts)
    result = next(p for p in build_canonical_result_projectors() if p.projector_id == projector_id).project(context)
    assert {tuple(f.artifact_ids): f.title for f in result.bundle.figures} == {
        ("companion-artifact-2",): "真实值与预测值", ("companion-artifact-3",): "残差分布",
    }
    assert json.dumps(context.artifacts) == before


@pytest.mark.parametrize("tool,kind,expected", [
    ("ml.basic_metrics", "metrics_json", "回归评估指标"),
    ("ml.error_distribution", "metrics_json", "回归评估指标（残差分析）"),
    ("ml.error_distribution", "table_json", "高误差样本（残差分析）"),
    ("ml.outlier_table", "table_json", "高误差样本"),
    ("ml.outlier_table", "table_csv", "高误差样本"),
    ("ml.regression_evaluation", "table_json", "材料属性回归评估"),
    ("ml.outlier_table", "metrics_json", "材料回归评估"),
])
def test_regression_table_titles_depend_on_the_exact_tool_and_artifact_type(tool, kind, expected):
    from mdi_api.application.scientific_results.figure_titles import scientific_table_title
    artifacts = [{"id": "a", "projectId": "p", "jobId": "j", "toolCallId": "c", "type": kind}]
    calls = [{"id": "c", "jobId": "j", "toolId": tool}]
    assert scientific_table_title("材料回归评估", ["a"], artifacts=artifacts, calls=calls, job_id="j", project_id="p") == expected
    assert scientific_table_title("用户自定义表名", ["a"], artifacts=artifacts, calls=calls, job_id="j", project_id="p") == "用户自定义表名"
    assert scientific_table_title("材料回归评估", ["a"], artifacts=artifacts, calls=calls+calls, job_id="j", project_id="p") == "材料回归评估"


@pytest.mark.parametrize("invalid", ["foreign_artifact", "foreign_call", "missing_call", "duplicate_call", "duplicate_artifact", "multiple_artifacts", "unknown_tool", "nonfigure", "authored_title"])
@pytest.mark.parametrize("family", ["regression", "table"])
def test_scientific_figure_title_never_guesses_from_names_or_ambiguous_sources(invalid, family):
    from mdi_api.application.scientific_results.figure_titles import scientific_figure_title
    artifacts = [{"id": "density_scatter_named_file", "jobId": "job", "projectId": "project", "type": "plotly_json", "toolCallId": "call"}]
    calls = [{"id": "call", "jobId": "job", "toolId": "ml.density_scatter" if family == "regression" else "viz.correlation", "state": "COMPLETED", "paramsJson": {}}]
    ids, title = [artifacts[0]["id"]], "材料回归评估" if family == "regression" else "数值表格分布与相关性分析"
    if invalid == "foreign_artifact": artifacts[0]["projectId"] = "foreign"
    if invalid == "foreign_call": calls[0]["jobId"] = "foreign"
    if invalid == "missing_call": calls = []
    if invalid == "duplicate_call": calls *= 2
    if invalid == "duplicate_artifact": artifacts *= 2
    if invalid == "multiple_artifacts": ids *= 2
    if invalid == "unknown_tool": calls[0]["toolId"] = "unknown"
    if invalid == "nonfigure": artifacts[0]["type"] = "table_json"
    if invalid == "authored_title": title = "已验证的真实值和预测值，保留限定说明"
    assert scientific_figure_title(title, ids, artifacts=artifacts, calls=calls, job_id="job", project_id="project") == title


def _context(
    payloads,
    *,
    projector_id: str,
    content_types: list[str] | None = None,
    companion_tool_ids: tuple[str, ...] = (),
):
    turn_id = uuid4()
    ref = ScientificObjectRef(object_id=uuid4(), version_id=uuid4(), project_id="project", object_type="structure.crystal")
    content_types = content_types or ["application/json"] * len(payloads)
    primary_artifacts = tuple(
        {"id": f"artifact-{index}", "contentType": content_type, "filename": "rmse_0.2.json"}
        for index, content_type in enumerate(content_types, start=1)
    )
    tool_calls = tuple(
        {
            "id": f"tool-call-{index}",
            "toolId": tool_id,
            "state": "COMPLETED",
        }
        for index, tool_id in enumerate(companion_tool_ids, start=1)
    )
    companion_artifacts = tuple(
        {
            "id": f"companion-artifact-{index}",
            "contentType": "application/json",
            "filename": f"{tool_id.replace('.', '_')}.json",
            "toolCallId": f"tool-call-{index}",
        }
        for index, tool_id in enumerate(companion_tool_ids, start=1)
    )
    artifacts = primary_artifacts + companion_artifacts
    artifact_payloads = {
        artifact["id"]: payload
        for artifact, payload in zip(primary_artifacts, payloads, strict=True)
    }
    artifact_payloads.update(
        {
            artifact["id"]: {
                "toolId": tool_id,
                "status": "COMPLETED",
                "payload": {"bounded": True},
            }
            for artifact, tool_id in zip(
                companion_artifacts,
                companion_tool_ids,
                strict=True,
            )
        }
    )
    return ScientificResultProjectionContext(
        project_id="project", research_session_id="session", research_turn_id=str(turn_id),
        research_question="Canonical scientific projection",
        execution_summary={"outcome": "SUCCESS", "job_id": "job-1", "analysis_plan_id": "plan-1"},
        capability_plan={"steps": [{"step_id": "step_1", "capability_id": projector_id.removeprefix("agent2."), "capability_version": "1.0", "parameters": {}}]},
        analysis_plan={"schemaVersion": "0.2"},
        tool_calls=tool_calls,
        artifacts=artifacts,
        artifact_payloads=artifact_payloads,
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
        "trajectory.msd_first_total", "trajectory.msd_last_total", "trajectory.msd_atom_count",
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
    companion_tool_ids = (
        ML_REGRESSION_COMPANION_TOOLS
        if projector_id == "agent2.ml.regression_evaluation"
        else ()
    )
    bundle = projector.project(
        _context(
            [payload],
            projector_id=projector_id,
            companion_tool_ids=companion_tool_ids,
        )
    ).bundle
    assert {fact.predicate for fact in bundle.facts} == expected_predicates
    assert bundle.result_items
    if projector_id == "agent2.phonon.band":
        assert bundle.tables == []  # A summary is not a row/column table.
    else:
        assert bundle.tables
    for fact in bundle.facts:
        assert fact.source.artifact_id == "artifact-1"
        assert fact.source.artifact_locator
        assert resolve_json_pointer(payload, fact.source.artifact_locator) == fact.value


def test_msd_endpoint_facts_keep_exact_saved_values_and_do_not_claim_interior_curve():
    projector = next(item for item in build_canonical_result_projectors() if item.projector_id == "agent2.trajectory.msd")
    payload = {
        "artifactType": "trajectory.msd", "schema_version": "phase10n4.trajectory_msd.v1",
        "lagTimesPs": [0.002, 0.004, 0.006], "totalMsdAngstrom2": [0.0006, 0.0012, 0.0018],
        "directionalMsdAngstrom2": {"x": [0.0001, 0.0002, 0.0003], "y": [0.0002, 0.0004, 0.0006], "z": [0.0003, 0.0006, 0.0009]},
        "originCounts": [199, 198, 197], "species": "Li", "coverage": {"frames": 200, "atoms": 128, "validLags": 3},
    }
    bundle = projector.project(_context([payload], projector_id=projector.projector_id)).bundle
    facts = {fact.predicate: fact for fact in bundle.facts}
    assert facts["trajectory.msd_atom_count"].value == 128
    assert facts["trajectory.msd_first_total"].unit == "angstrom^2"
    assert facts["trajectory.msd_last_origin_count"].value == 197
    assert facts["trajectory.msd_last_z"].source.artifact_locator == "/directionalMsdAngstrom2/z/2"
    for fact in bundle.facts:
        assert resolve_json_pointer(payload, fact.source.artifact_locator) == fact.value
    assert not any(fact.source.artifact_locator.endswith("/1") for fact in bundle.facts)
    from mdi_api.interpretation.grounding import validate_interpretation
    from mdi_api.interpretation.schemas import ScientificInterpretationOutput
    output = ScientificInterpretationOutput.model_validate({
        "contract_version": "1.0", "title": "MSD", "answer_lead": "MSD 结果已保存。",
        "primary_findings": [{"finding_id": "msd", "statement": "128 个 Li 原子的首个滞后时间为 0.002 ps，总 MSD 为 0.0006 Å²，时间原点数为 199。", "importance": "HIGH", "confidence": "HIGH", "fact_refs": list(f.fact_id for f in facts.values()), "evidence_refs": [], "result_item_refs": [bundle.result_items[0].id]}],
        "supporting_findings": [], "limitations": [], "primary_result_refs": [bundle.result_items[0].id], "supporting_result_refs": [], "follow_up_suggestions": [],
    })
    assert validate_interpretation(output, bundle).valid


@pytest.mark.parametrize("change", [{"totalMsdAngstrom2": [0.1]}, {"totalMsdAngstrom2": [0.1, float("nan")]}])
def test_msd_endpoint_projection_rejects_misaligned_or_nonfinite_arrays(change):
    projector_id, payload, _ = next(item for item in CASES if item[0] == "agent2.trajectory.msd")
    projector = next(item for item in build_canonical_result_projectors() if item.projector_id == projector_id)
    with pytest.raises(ScientificResultProjectionFailed):
        projector.project(_context([{**payload, **change}], projector_id=projector_id))


def test_rejected_diffusion_exposes_saved_thresholds_without_a_coefficient():
    projector = next(item for item in build_canonical_result_projectors() if item.projector_id == "agent2.trajectory.diffusion")
    payload = {
        "artifactType": "trajectory.diffusion", "schema_version": "phase10n4.trajectory_diffusion.v1",
        "diffusionEstimate": {"available": False, "value": None, "unit": "angstrom^2/picosecond"},
        "fitWindow": {"startPs": 0.02, "endPs": 0.1, "pointCount": 41, "durationPs": 0.08},
        "fit": {"rSquared": 0.9998, "rmseAngstrom2": 0.00009},
        "regimeDiagnostic": {"status": "INSUFFICIENT_DURATION", "originCoverage": 0.75, "alpha": 1.01},
        "resolvedParameters": {"minimum_fit_duration_ps": 1.0, "minimum_fit_points": 5, "minimum_origin_coverage": 0.2, "minimum_r_squared": 0.9, "alpha_min": 0.8, "alpha_max": 1.2},
    }
    bundle = projector.project(_context([payload], projector_id=projector.projector_id)).bundle
    facts = {fact.predicate: fact for fact in bundle.facts}
    assert "trajectory.diffusion_coefficient" not in facts
    assert facts["trajectory.diffusion_minimum_duration"].value == 1.0
    assert facts["trajectory.diffusion_minimum_duration"].unit == "picosecond"
    assert facts["trajectory.diffusion_regime"].value == "INSUFFICIENT_DURATION"
    assert facts["trajectory.diffusion_fit_duration"].value == 0.08
    for fact in bundle.facts:
        assert resolve_json_pointer(payload, fact.source.artifact_locator) == fact.value


def test_regression_projects_saved_undefined_r2_status_without_a_numeric_fact() -> None:
    import copy
    projector_id, example, _ = next(item for item in CASES if item[0] == "agent2.ml.regression_evaluation")
    payload = copy.deepcopy(example)
    payload["evaluations"][0]["metrics"].update(r2=None, r2Status="undefined_constant_target")
    before = json.dumps(payload)
    projector = next(item for item in build_canonical_result_projectors() if item.projector_id == projector_id)
    projection = projector.project(_context([payload], projector_id=projector_id, companion_tool_ids=ML_REGRESSION_COMPANION_TOOLS))
    facts = {fact.predicate: fact for fact in projection.bundle.facts}
    assert projection.projector_version == "1.2"
    assert "ml.r2" not in facts
    status = facts["ml.r2_status"]
    assert status.value == "undefined_constant_target" and status.unit is None
    assert resolve_json_pointer(payload, status.source.artifact_locator) == status.value
    assert json.dumps(payload) == before


def test_mandatory_tool_coverage_projection_rejects_missing_tool_output() -> None:
    projector_id, payload, _expected_predicates = next(
        item for item in CASES if item[0] == "agent2.ml.regression_evaluation"
    )
    projector = next(
        item
        for item in build_canonical_result_projectors()
        if item.projector_id == projector_id
    )

    with pytest.raises(
        ScientificResultProjectionFailed,
        match="missing required committed Tool outputs: ml.outlier_table",
    ):
        projector.project(
            _context(
                [payload],
                projector_id=projector_id,
                companion_tool_ids=ML_REGRESSION_COMPANION_TOOLS[:-1],
            )
        )

    bundle = projector.project(
        _context(
            [payload],
            projector_id=projector_id,
            companion_tool_ids=ML_REGRESSION_COMPANION_TOOLS,
        )
    ).bundle
    assert {
        evidence.artifact_id for evidence in bundle.evidence
    } >= {
        "companion-artifact-1",
        "companion-artifact-2",
        "companion-artifact-3",
        "companion-artifact-4",
    }


def test_brillouin_zone_projector_requires_complete_verified_triad_and_projects_kpath_count() -> None:
    fixture_root = (
        ROOT
        / "tests"
        / "fixtures"
        / "brillouin_zone_v1"
        / "simple_cubic"
    )
    payloads = [
        json.loads((fixture_root / name).read_text(encoding="utf-8"))
        for name in (
            "reciprocal_lattice.json",
            "brillouin_zone.json",
            "kpath.json",
        )
    ]
    projector_id = "agent2.structure.brillouin_zone"
    projector = next(
        item
        for item in build_canonical_result_projectors()
        if item.projector_id == projector_id
    )

    bundle = projector.project(
        _context(payloads, projector_id=projector_id)
    ).bundle
    facts = {fact.predicate: fact for fact in bundle.facts}

    assert bundle.result_items[0].result_type == "reciprocal.brillouin_zone"
    assert facts["reciprocal.high_symmetry_point_count"].value == len(
        payloads[2]["points"]
    )
    assert (
        facts["reciprocal.high_symmetry_point_count"].source.artifact_locator
        == "/points"
    )

    schemas = {
        RECIPROCAL_LATTICE_SCHEMA_VERSION,
        BRILLOUIN_ZONE_SCHEMA_VERSION,
        KPATH_SCHEMA_VERSION,
    }
    for missing_schema in schemas:
        incomplete = [
            payload
            for payload in payloads
            if (payload.get("schema_version") or payload.get("schemaVersion"))
            != missing_schema
        ]
        with pytest.raises(
            ScientificResultProjectionFailed,
            match="missing required verified Artifact schemas",
        ):
            projector.project(_context(incomplete, projector_id=projector_id))


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


@pytest.mark.parametrize("count,partial", [(2, False), (3, False), (3, True)])
def test_repeated_capability_results_keep_material_and_call_identity(count, partial):
    _, payload, _ = CASES[0]
    context = _context([payload] * count, projector_id="agent2.structure.rdf")
    sources = tuple(ScientificObjectRef(object_id=uuid4(), version_id=uuid4(), project_id="project",
        object_type="structure.crystal", display_name=name) for name in ["Si", "Cu", "NaCl"][:count])
    steps = [{"step_id": f"step_{i}", "capability_id": "structure.rdf", "capability_version": "1.0"} for i in range(1, count + 1)]
    analysis = [{"stepId": f"step_{i}", "toolId": "structure.rdf", "inputRefs": [{"refType": "normalized_object", "ref": str(source.version_id)}]} for i, source in enumerate(sources, 1)]
    calls = tuple({"id": f"call-{i}", "stepId": f"step_{i}", "toolId": "structure.rdf"} for i in range(1, count + 1))
    artifacts = tuple({**artifact, "toolCallId": f"call-{i}"} for i, artifact in enumerate(context.artifacts, 1))
    summary = {**context.execution_summary, "outcome": "PARTIAL" if partial else "SUCCESS",
        "successful_step_ids": [f"step_{i}" for i in range(1, count if partial else count + 1)]}
    context = replace(context, source_object_refs=sources, capability_plan={"steps": steps}, analysis_plan={"steps": analysis},
        tool_calls=calls, artifacts=artifacts, execution_summary=summary)
    bundle = ScientificResultProjectionService(None).project_context(context)
    expected_count = count - int(partial)
    assert len(bundle.result_items) == expected_count
    assert len({item.id for item in bundle.result_items}) == expected_count
    for i, source in enumerate(sources[:expected_count], 1):
        artifact_id = f"artifact-{i}"
        item = next(item for item in bundle.result_items if artifact_id in item.artifact_ids)
        assert item.scientific_object_refs == [source]
        assert source.display_name in item.title
        assert [e.scientific_object_refs for e in bundle.evidence if e.artifact_id == artifact_id] == [[source]]
        assert all(f.source.artifact_id == artifact_id for f in bundle.facts if f.fact_id in item.fact_refs)
        assert any(method.source_object_refs == [source] for method in bundle.methods)
    assert not partial or f"artifact-{count}" not in bundle.provenance.artifact_ids


@pytest.mark.parametrize("mismatch", [None, "profile", "resource", "file"])
def test_material_label_follows_exact_resource_file_provenance(mismatch):
    version = {"semantic_profile_ref_json": {"profileId": "p", "datasetId": "d", "semanticHash": "h", "resourceId": "r", "resourceHash": "rh"}}
    profile = {"profileId": "p", "datasetId": "d", "semanticHash": "h",
        "objects": [{"objectId": "r", "objectHash": "rh", "sourceFileIds": ["f2"]}],
        "files": [{"fileId": "f1", "fileName": "Si.cif"}, {"fileId": "f2", "fileName": "Cu.cif"}]}
    if mismatch == "profile":
        profile["semanticHash"] = "stale"
    elif mismatch == "resource":
        profile["objects"][0]["objectHash"] = "other"
    elif mismatch == "file":
        profile["files"][1]["fileId"] = "missing"
    assert ScientificResultProjectionService._source_file_label(version, profile) == (None if mismatch else "Cu.cif")


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


@pytest.mark.parametrize("invalid", [None, "foreign_version", "foreign_project", "wrong_tool", "missing_site", "wrong_species", "invalid_scene"])
def test_selected_structure_facts_use_owned_scene_coordinates(invalid):
    from tests.test_viewer_scene_adapter import _execute_adapter, _artifact_payload, _si_structure
    from mdi_api.application.scientific_results.projectors.structure import structure_selection_facts
    payload = _artifact_payload(_execute_adapter(object_store={"structures": [_si_structure()]}), "viewer_scene.json")
    context = _context([payload], projector_id="agent2.structure.viewer_scene")
    ref = context.source_object_refs[0]
    artifact = {"id": "scene", "projectId": "project", "jobId": "job-1", "toolCallId": "call"}
    call = {"id": "call", "jobId": "job-1", "stepId": "step", "toolId": "structure.viewer_scene"}
    selection = {"selection_type": "PERIODIC_SITE", "object_ref": ref.model_dump(mode="json"),
        "semantic_locator": {"site_index": 0, "species": "Si", "xyz": [999, 999, 999]}}
    if invalid == "foreign_version": selection["object_ref"]["version_id"] = str(uuid4())
    if invalid == "foreign_project": artifact["projectId"] = "foreign"
    if invalid == "wrong_tool": call["toolId"] = "other"
    if invalid == "missing_site": selection["semantic_locator"]["site_index"] = 999
    if invalid == "wrong_species": selection["semantic_locator"]["species"] = "Li"
    if invalid == "invalid_scene": payload["scene"]["coordinate_basis"] = "unknown"
    context = replace(context, tool_calls=(call,), scientific_selections=(selection,), analysis_plan={"steps": [
        {"stepId": "step", "toolId": "structure.viewer_scene", "inputRefs": [{"refType": "normalized_object", "ref": str(ref.version_id)}]}
    ]})
    if invalid in {"missing_site", "wrong_species"}:
        with pytest.raises(ScientificResultProjectionFailed, match="Selected structure site"):
            structure_selection_facts(context, artifact, payload)
        return
    facts = structure_selection_facts(context, artifact, payload)
    if invalid:
        assert facts == []
        return
    assert len(facts) == 9
    projector = next(p for p in build_canonical_result_projectors() if p.projector_id == "agent2.structure.viewer_scene")
    projected = projector.project(replace(context, artifacts=(artifact,), artifact_payloads={"scene": payload})).bundle
    assert len(projected.facts) == 9
    assert len(projected.figures) == 1
    assert projected.tables == []
    for fact in facts:
        assert resolve_json_pointer(payload, fact.source.artifact_locator) == fact.value
        assert fact.value != 999
    assert {fact.predicate: fact.value for fact in facts}["structure.selected_site_index"] == 0
