from __future__ import annotations

import json
from pathlib import Path
import shutil

from pymatgen.core import Lattice, Structure

from mdi_adapters import BrillouinZoneAdapter, ToolExecutionContext
from mdi_api.repositories import InMemoryRepositoryBundle
from mdi_api.routers.planner import PlannerJobsRequest, planner_jobs
from mdi_artifact_core import (
    build_phonon_animation,
    build_phonon_eigenvector,
    build_phonon_eigenvector_set,
    build_phonon_mode_ref,
    reciprocal_path_step,
    validate_phonon_kpath_compatibility,
)
from mdi_llm import MockLLMProvider, PlannerRequest
from mdi_schemas import DataProfile, ToolExecutionRequest
from mdi_tool_registry import load_manifests
from mdi_workers import QueueWorkerRuntime


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "docs" / "phase10i" / "evidence" / "phase10i3_band_bz_linked_view"
RUNTIME_ROOT = ROOT / ".tmp_phase10i3_runtime"


def main() -> None:
    if RUNTIME_ROOT.exists():
        shutil.rmtree(RUNTIME_ROOT)
    (EVIDENCE / "api").mkdir(parents=True, exist_ok=True)
    (EVIDENCE / "artifacts").mkdir(parents=True, exist_ok=True)
    structure = Structure(Lattice.cubic(4.0), ["Fe", "Fe"], [[0, 0, 0], [0.5, 0.5, 0.5]])
    registry = load_manifests()
    preview = preview_bz(registry, structure)
    band = band_for_kpath(preview["reciprocal_lattice.json"], preview["kpath.json"])
    band["species"] = ["Fe", "Fe"]
    profile = profile_payload()
    provider = MockLLMProvider()
    planner_request = PlannerRequest("Link the phonon band chart to the 3D BZ", "dataset_link", "profile_link", registry.version)
    generated = provider.generate_plan(planner_request, tools=registry.list_mvp_tools(), data_profile=DataProfile.model_validate(profile))
    if generated.raw_json is None:
        raise RuntimeError("linked plan was not generated")
    repositories = InMemoryRepositoryBundle.create()
    runtime = QueueWorkerRuntime(repositories=repositories, registry=registry, artifact_root=RUNTIME_ROOT / "runtime")
    created = planner_jobs(
        PlannerJobsRequest(userPrompt=planner_request.user_prompt, projectId="project_link", datasetId="dataset_link", profileId="profile_link", enqueue=True),
        provider=MockLLMProvider(fixed_plan=generated.raw_json), repositories=repositories, queue_runtime=runtime, registry=registry,
    )
    if not created.ok or not created.job_id:
        raise RuntimeError("linked planner job was not created")
    result = runtime.handle_job(created.job_id, object_store={"phonon_band": band, "structures": [structure]})
    if result.status != "completed":
        raise RuntimeError(f"linked runtime failed: {result.status}")
    calls = repositories.tool_calls.list_for_job(created.job_id)
    records = repositories.artifacts.list_for_job(created.job_id)
    selected_names = {"phonon_band.json", "reciprocal_lattice.json", "brillouin_zone.json", "kpath.json", "brillouin_zone_manifest.json"}
    payloads: dict[str, dict] = {}
    for record in records:
        if record["name"] not in selected_names:
            continue
        source = RUNTIME_ROOT / "runtime" / record["storageKey"]
        payloads[record["name"]] = json.loads(source.read_text(encoding="utf-8"))
        write_json(EVIDENCE / "artifacts" / record["name"], payloads[record["name"]])
    compatibility = validate_phonon_kpath_compatibility(payloads["phonon_band.json"], payloads["reciprocal_lattice.json"], payloads["kpath.json"])
    if not compatibility.compatible:
        raise RuntimeError(f"runtime artifacts are incompatible: {compatibility.as_dict()}")
    write_json(EVIDENCE / "api" / "analysis_plan.json", generated.raw_json)
    write_json(EVIDENCE / "api" / "job.json", {"jobId": "[runtime-job-redacted]", "status": result.status, "planId": "[runtime-plan-redacted]", "planHash": created.plan_hash, "artifactCount": len(records), "toolCallCount": len(calls), "realLLM": False, "externalNetworkRequests": 0})
    write_json(EVIDENCE / "api" / "tool_calls.json", [{"stepId": item["stepId"], "toolId": item["toolId"], "status": item["status"]} for item in calls])
    step_by_call = {item["id"]: item["stepId"] for item in calls}
    write_json(EVIDENCE / "api" / "artifact_inventory.json", [{"name": item["name"], "type": item["type"], "contentHash": item.get("contentHash"), "stepId": step_by_call.get(item.get("toolCallId"), "unknown")} for item in records])
    write_json(EVIDENCE / "compatibility" / "backend_validation.json", compatibility.as_dict())
    animation = animation_for_band(payloads["phonon_band.json"])
    write_json(EVIDENCE / "artifacts" / "phonon_animation.json", animation)
    write_json(EVIDENCE / "compatibility" / "animation_handoff.json", {"modeId": animation["mode"]["mode"]["mode_id"], "qpointIndex": animation["mode"]["mode"]["qpoint_index"], "branchIndex": animation["mode"]["mode"]["branch_index"], "bandSha256": animation["source"]["band_sha256"], "status": "exact_canonical_mode"})
    write_json(EVIDENCE / "runtime_source.json", {"source": "QueueWorkerRuntime", "tools": ["phonon.band", "structure.brillouin_zone"], "structure": "bounded BCC Fe fixture", "bandInput": "canonical phase10h.phonon_band.v1", "status": "completed", "externalNetworkRequests": 0})
    if RUNTIME_ROOT.exists():
        shutil.rmtree(RUNTIME_ROOT)
    print("PHASE10I3_RUNTIME_ARTIFACTS_PASS")


def preview_bz(registry, structure: Structure) -> dict[str, dict]:
    tool = registry.get_tool_by_id("structure.brillouin_zone")
    root = RUNTIME_ROOT / "preview"
    context = ToolExecutionContext(job_id="preview", project_id="project_link", dataset_id="dataset_link", tool_id=tool.toolId, tool_version=tool.version, adapter_version="1.0.0", registry_version=registry.version, artifact_root=root, tool_call_id="preview_call", object_store={"structures": [structure]}, resource_limits=tool.resourceLimits)
    request = ToolExecutionRequest(jobId="preview", stepId="step_bz", toolId=tool.toolId, inputRefs=[{"refType": "normalized_object", "ref": "structures", "objectType": "Structure"}], params={"include_reciprocal_lattice": True, "include_brillouin_zone": True, "include_kpath": True, "standardization": "contract_default", "kpath_provider": "contract_default", "time_reversal": True, "symmetry_tolerance_angstrom": 1e-5, "angle_tolerance_degrees": 5.0, "include_alternative_path_variants": False}, artifactTypes=["reciprocal_lattice_json", "brillouin_zone_json", "kpath_json", "brillouin_zone_manifest_json", "summary_md", "recipe_json"])
    artifacts = BrillouinZoneAdapter().execute(context, request)
    return {item.name: json.loads((root / item.storageKey).read_text(encoding="utf-8")) for item in artifacts if item.name.endswith(".json")}


def band_for_kpath(reciprocal: dict, kpath: dict) -> dict:
    band = json.loads((ROOT / "docs" / "phase10h" / "fixtures" / "phonon_contract" / "stable_band.json").read_text(encoding="utf-8"))
    selected = next(item for item in kpath["path_variants"] if item["selected"])
    segment_by_id = {item["segment_id"]: item for item in kpath["segments"]}
    point_by_id = {item["point_id"]: item for item in kpath["points"]}
    lattice = reciprocal["real_lattice_binding"]["primitive_real_lattice"]
    qpoints, segments, distance = [], [], 0.0
    for segment_index, segment_id in enumerate(selected["segment_ids"]):
        segment = segment_by_id[segment_id]
        start, end = point_by_id[segment["start_point_id"]], point_by_id[segment["end_point_id"]]
        start_index = len(qpoints)
        qpoints.append({"index": start_index, "coordinates": start["fractional_coordinates"], "label": start["display_label"], "source_label": start["label_key"], "segment_index": segment_index, "distance": distance})
        step = reciprocal_path_step(start["fractional_coordinates"], end["fractional_coordinates"], lattice)
        midpoint = [(float(start["fractional_coordinates"][axis]) + float(end["fractional_coordinates"][axis])) / 2 for axis in range(3)]
        distance += step / 2
        qpoints.append({"index": len(qpoints), "coordinates": midpoint, "label": None, "source_label": None, "segment_index": segment_index, "distance": distance})
        distance += step / 2
        end_index = len(qpoints)
        qpoints.append({"index": end_index, "coordinates": end["fractional_coordinates"], "label": end["display_label"], "source_label": end["label_key"], "segment_index": segment_index, "distance": distance})
        segments.append({"segment_index": segment_index, "start_qpoint_index": start_index, "end_qpoint_index": end_index, "start_label": start["display_label"], "end_label": end["display_label"], "discontinuous_from_previous": bool(segment_index and segment["discontinuity_before"])})
    band.update({"structure_identity": reciprocal["real_lattice_binding"]["source_structure_sha256"], "real_space_lattice_angstrom": lattice, "qpoints": qpoints, "segments": segments, "degeneracy_groups": [], "species": ["Fe", "Fe"]})
    for branch in band["branches"]:
        branch["frequencies"] = [float(branch["branch_index"] + index * 0.125 - (0.5 if branch["branch_index"] == 0 and index == 1 else 0.0)) for index in range(len(qpoints))]
    return band


def animation_for_band(band: dict) -> dict:
    qpoint_index, branch_index = 0, 3
    mode_ref = build_phonon_mode_ref(band, artifact_id="runtime-band", qpoint_index=qpoint_index, branch_index=branch_index)
    eigenvector = build_phonon_eigenvector(band, mode_ref, [[1 + 0j, 0j, 0j], [-1 + 0j, 0j, 0j]], [55.845, 55.845])
    eigenvectors = build_phonon_eigenvector_set([eigenvector])
    lattice = band["real_space_lattice_angstrom"]
    fractional = [[0.0, 0.0, 0.0], [0.5, 0.5, 0.5]]
    sites = []
    for index, coordinates in enumerate(fractional):
        cartesian = [sum(float(coordinates[row]) * float(lattice[row][axis]) for row in range(3)) for axis in range(3)]
        sites.append({"site_index": index, "species": "Fe", "fractional": coordinates, "cartesian": cartesian})
    structure = {"structure_identity": band["structure_identity"], "formula": "Fe2", "lattice": lattice, "sites": sites, "bonds": []}
    return build_phonon_animation(structure, band, eigenvectors, {"mode_id": mode_ref["mode_id"]})


def profile_payload() -> dict:
    return {"schemaVersion": "0.1", "profileId": "profile_link", "datasetId": "dataset_link", "version": "1", "datasetType": "structure_phononband", "objects": [{"objectType": "Structure", "count": 1}, {"objectType": "PhononBand", "count": 1}], "structureSummary": {"nStructures": 1, "elements": ["Fe"], "formulaStats": {"total": 1, "uniqueCount": 1}}, "qualityIssues": [], "recommendedTasks": [], "createdAt": "2026-07-16T00:00:00Z"}


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    content = json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n"
    path.write_bytes(content.encode("utf-8"))


if __name__ == "__main__":
    main()
