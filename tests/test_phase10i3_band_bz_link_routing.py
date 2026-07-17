from __future__ import annotations

import json
from pathlib import Path

from pymatgen.core import Lattice, Structure

from mdi_adapters import BrillouinZoneAdapter, ToolExecutionContext
from mdi_api.repositories import InMemoryRepositoryBundle
from mdi_api.routers.planner import PlannerJobsRequest, planner_jobs
from mdi_artifact_core import reciprocal_path_step, validate_phonon_kpath_compatibility
from mdi_llm import MockLLMProvider, PlannerRequest
from mdi_schemas import DataProfile, ToolExecutionRequest
from mdi_tool_registry import load_manifests
from mdi_tool_registry.plan_validator import validate_plan
from mdi_workers import QueueWorkerRuntime


ROOT = Path(__file__).resolve().parents[1]


def _profile() -> DataProfile:
    return DataProfile.model_validate(
        {
            "schemaVersion": "0.1",
            "profileId": "profile_link",
            "datasetId": "dataset_link",
            "version": "1",
            "datasetType": "structure_phononband",
            "objects": [
                {"objectType": "Structure", "count": 1, "source": "crystal.cif"},
                {"objectType": "PhononBand", "count": 1, "id": "band_artifact"},
            ],
            "structureSummary": {"nStructures": 1, "elements": ["Si"], "formulaStats": {"total": 1, "uniqueCount": 1}},
            "qualityIssues": [],
            "recommendedTasks": [],
            "createdAt": "2026-07-16T00:00:00Z",
        }
    )


def _plan(prompt: str) -> dict:
    registry = load_manifests()
    response = MockLLMProvider().generate_plan(
        PlannerRequest(prompt, "dataset_link", "profile_link", registry.version),
        tools=registry.list_mvp_tools(),
        data_profile=_profile(),
    )
    assert response.raw_json is not None
    return response.raw_json


def test_explicit_linked_view_prompt_composes_existing_tools_without_a_link_tool() -> None:
    plan = _plan("Link the phonon band chart to the 3D BZ")
    assert [step["toolId"] for step in plan["steps"]] == ["phonon.band", "structure.brillouin_zone"]
    assert {item["name"] for item in plan["expectedArtifacts"]} == {
        "phonon_band.json", "reciprocal_lattice.json", "brillouin_zone.json", "kpath.json", "brillouin_zone_manifest.json"
    }
    assert validate_plan(plan, registry=load_manifests()).ok
    assert "reciprocal.band_bz_link" not in {tool.toolId for tool in load_manifests().tools}


def test_linked_view_routing_requires_both_approved_inputs() -> None:
    profile = _profile().model_copy(update={"datasetType": "structure_collection", "objects": [{"objectType": "Structure", "count": 1}]})
    registry = load_manifests()
    response = MockLLMProvider().generate_plan(
        PlannerRequest("Link the phonon band chart to the 3D BZ", "dataset_link", "profile_link", registry.version),
        tools=registry.list_mvp_tools(),
        data_profile=profile,
    )
    assert response.raw_json is not None
    assert [step["toolId"] for step in response.raw_json["steps"]] != ["phonon.band", "structure.brillouin_zone"]


def test_electronic_and_mutating_requests_do_not_claim_linked_phonon_capability() -> None:
    for prompt in ("Calculate electronic bands and link them to the BZ", "Edit k-path in the linked view", "Generate a Fermi surface"):
        plan = _plan(prompt)
        assert [step["toolId"] for step in plan["steps"]] != ["phonon.band", "structure.brillouin_zone"]


def test_two_step_runtime_emits_compatible_persisted_band_and_bz_artifacts(tmp_path: Path) -> None:
    registry = load_manifests()
    structure = Structure(Lattice.cubic(4.0), ["Fe", "Fe"], [[0, 0, 0], [0.5, 0.5, 0.5]])
    bz_tool = registry.get_tool_by_id("structure.brillouin_zone")
    preview_root = tmp_path / "preview"
    preview_context = ToolExecutionContext(
        job_id="preview", project_id="project_link", dataset_id="dataset_link",
        tool_id=bz_tool.toolId, tool_version=bz_tool.version, adapter_version="1.0.0",
        registry_version=registry.version, artifact_root=preview_root, tool_call_id="preview_call",
        object_store={"structures": [structure]}, resource_limits=bz_tool.resourceLimits,
    )
    preview_request = ToolExecutionRequest(
        jobId="preview", stepId="step_bz", toolId="structure.brillouin_zone",
        inputRefs=[{"refType": "normalized_object", "ref": "structures", "objectType": "Structure"}],
        params={"include_reciprocal_lattice": True, "include_brillouin_zone": True, "include_kpath": True, "standardization": "contract_default", "kpath_provider": "contract_default", "time_reversal": True, "symmetry_tolerance_angstrom": 1e-5, "angle_tolerance_degrees": 5.0, "include_alternative_path_variants": False},
        artifactTypes=["reciprocal_lattice_json", "brillouin_zone_json", "kpath_json", "brillouin_zone_manifest_json", "summary_md", "recipe_json"],
    )
    preview_artifacts = BrillouinZoneAdapter().execute(preview_context, preview_request)
    preview_payloads = {item.name: json.loads((preview_root / item.storageKey).read_text(encoding="utf-8")) for item in preview_artifacts if item.name.endswith(".json")}
    band = _band_for_kpath(preview_payloads["reciprocal_lattice.json"], preview_payloads["kpath.json"])
    band["species"] = ["Fe", "Fe"]
    plan = _plan("Link the phonon band chart to the 3D BZ")
    repositories = InMemoryRepositoryBundle.create()
    artifact_root = tmp_path / "runtime"
    runtime = QueueWorkerRuntime(repositories=repositories, registry=registry, artifact_root=artifact_root)
    created = planner_jobs(
        PlannerJobsRequest(userPrompt="Link the phonon band chart to the 3D BZ", projectId="project_link", datasetId="dataset_link", profileId="profile_link", enqueue=True),
        provider=MockLLMProvider(fixed_plan=plan), repositories=repositories, queue_runtime=runtime, registry=registry,
    )
    assert created.ok and created.job_id
    result = runtime.handle_job(created.job_id, object_store={"phonon_band": band, "structures": [structure]})
    assert result.status == "completed"
    calls = repositories.tool_calls.list_for_job(created.job_id)
    assert [(item["toolId"], item["status"]) for item in calls] == [("phonon.band", "completed"), ("structure.brillouin_zone", "completed")]
    records = repositories.artifacts.list_for_job(created.job_id)
    payloads = {item["name"]: json.loads((artifact_root / item["storageKey"]).read_text(encoding="utf-8")) for item in records if item["name"] in {"phonon_band.json", "reciprocal_lattice.json", "kpath.json"}}
    compatibility = validate_phonon_kpath_compatibility(payloads["phonon_band.json"], payloads["reciprocal_lattice.json"], payloads["kpath.json"])
    assert compatibility.compatible, compatibility.as_dict()
    assert "BZ_PHONON_TIME_REVERSAL_UNDECLARED" in compatibility.warnings


def _band_for_kpath(reciprocal: dict, kpath: dict) -> dict:
    band = json.loads((ROOT / "docs" / "phase10h" / "fixtures" / "phonon_contract" / "stable_band.json").read_text(encoding="utf-8"))
    selected = next(item for item in kpath["path_variants"] if item["selected"])
    segment_by_id = {item["segment_id"]: item for item in kpath["segments"]}
    point_by_id = {item["point_id"]: item for item in kpath["points"]}
    lattice = reciprocal["real_lattice_binding"]["primitive_real_lattice"]
    qpoints, segments = [], []
    distance = 0.0
    for segment_index, segment_id in enumerate(selected["segment_ids"]):
        segment = segment_by_id[segment_id]
        start, end = point_by_id[segment["start_point_id"]], point_by_id[segment["end_point_id"]]
        start_index = len(qpoints)
        qpoints.append({"index": start_index, "coordinates": start["fractional_coordinates"], "label": start["display_label"], "source_label": start["label_key"], "segment_index": segment_index, "distance": distance})
        distance += reciprocal_path_step(start["fractional_coordinates"], end["fractional_coordinates"], lattice)
        end_index = len(qpoints)
        qpoints.append({"index": end_index, "coordinates": end["fractional_coordinates"], "label": end["display_label"], "source_label": end["label_key"], "segment_index": segment_index, "distance": distance})
        segments.append({"segment_index": segment_index, "start_qpoint_index": start_index, "end_qpoint_index": end_index, "start_label": start["display_label"], "end_label": end["display_label"], "discontinuous_from_previous": bool(segment_index and segment["discontinuity_before"])})
    band.update({"structure_identity": reciprocal["real_lattice_binding"]["source_structure_sha256"], "real_space_lattice_angstrom": lattice, "qpoints": qpoints, "segments": segments, "degeneracy_groups": []})
    for branch in band["branches"]:
        branch["frequencies"] = [float(branch["branch_index"] + index * 0.125) for index in range(len(qpoints))]
    return band
