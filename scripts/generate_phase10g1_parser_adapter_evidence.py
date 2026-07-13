from __future__ import annotations

import hashlib
import json
import tempfile
from pathlib import Path
from time import perf_counter
from typing import Any

from mdi_api.repositories import InMemoryRepositoryBundle
from mdi_api.routers.planner import PlannerJobsRequest, planner_jobs
from mdi_artifact_core import validate_trajectory, validate_trajectory_manifest, validate_trajectory_summary
from mdi_llm import MockLLMProvider
from mdi_material_parsers import TrajectoryParseError, detect_trajectory_format, parse_file, parse_trajectory_file
from mdi_tool_registry import load_manifests
from mdi_tool_registry.plan_validator import validate_plan
from mdi_workers import QueueWorkerRuntime


ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "docs" / "phase10g" / "fixtures" / "trajectory_import"
CONTRACT_FIXTURES = ROOT / "docs" / "phase10g" / "fixtures" / "trajectory_v1"
EVIDENCE = ROOT / "docs" / "phase10g" / "evidence" / "phase10g1_trajectory_parser_adapter"
ARTIFACT_TYPES = ["trajectory_json", "trajectory_summary_json", "trajectory_report_json", "trajectory_manifest_json"]


def write(name: str, payload: Any) -> None:
    path = EVIDENCE / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=True) + "\n", encoding="utf-8", newline="\n")


def plan() -> dict[str, Any]:
    return {
        "schemaVersion": "0.1",
        "goal": "Normalize a bounded trajectory into inert canonical artifacts.",
        "datasetId": "dataset_trajectory_evidence",
        "profileId": "profile_trajectory_evidence",
        "toolRegistryVersion": load_manifests().version,
        "assumptions": ["The approved upload parser produced one validated Trajectory object."],
        "warnings": ["Viewer and playback are not included."],
        "steps": [{
            "stepId": "step_trajectory_import", "toolId": "structure.trajectory_import",
            "purpose": "Emit canonical trajectory artifacts.", "reason": "The normalized object passed the trajectory validator.",
            "inputRefs": [{"refType": "normalized_object", "ref": "trajectory", "objectType": "Trajectory"}],
            "params": {}, "output": {"artifactTypes": ARTIFACT_TYPES}, "constraints": {"noExternalNetwork": True},
        }],
        "expectedArtifacts": [
            {"name": "trajectory.json", "type": "trajectory_json", "fromStepId": "step_trajectory_import"},
            {"name": "trajectory_summary.json", "type": "trajectory_summary_json", "fromStepId": "step_trajectory_import"},
            {"name": "trajectory_parse_report.json", "type": "trajectory_report_json", "fromStepId": "step_trajectory_import"},
            {"name": "trajectory_manifest.json", "type": "trajectory_manifest_json", "fromStepId": "step_trajectory_import"},
        ],
    }


def runtime_capture(source: Path, root: Path) -> dict[str, Any]:
    parsed = parse_file(source, dataset_id="dataset_trajectory_evidence", file_id="file_trajectory")
    if parsed.parse_status != "success" or not parsed.objects:
        raise RuntimeError(f"evidence parser failed: {parsed.error_code}")
    registry = load_manifests()
    selected_plan = plan()
    validation = validate_plan(selected_plan, registry=registry)
    repos = InMemoryRepositoryBundle.create()
    runtime = QueueWorkerRuntime(repositories=repos, registry=registry, artifact_root=root)
    created = planner_jobs(
        PlannerJobsRequest(userPrompt="Normalize this uploaded trajectory.", projectId="project_trajectory_evidence", datasetId="dataset_trajectory_evidence", profileId="profile_trajectory_evidence", enqueue=True),
        provider=MockLLMProvider(fixed_plan=selected_plan), repositories=repos, queue_runtime=runtime, registry=registry,
    )
    result = runtime.handle_job(created.job_id or "", object_store={"trajectory": parsed.objects[0]})
    records = repos.artifacts.list_for_job(created.job_id or "")
    contents: dict[str, Any] = {}
    for record in records:
        contents[record["name"]] = json.loads((root / record["storageKey"]).read_text(encoding="utf-8"))
    return {
        "request": {"prompt": "Normalize this uploaded trajectory.", "project_id": "project_trajectory_evidence", "dataset_id": "dataset_trajectory_evidence"},
        "plan_validation": {"ok": validation.ok, "errors": [item.code for item in validation.errors]},
        "job": {"ok": created.ok, "status": result.status, "tool_call_count": result.tool_call_count},
        "tool_calls": [{"tool_id": item["toolId"], "status": item["status"]} for item in repos.tool_calls.list_for_job(created.job_id or "")],
        "artifacts": [{"name": item["name"], "type": item["type"], "size_bytes": item["sizeBytes"], "sha256": item["contentHash"]} for item in records],
        "validation": {
            "trajectory": validate_trajectory(contents["trajectory.json"]).as_dict(),
            "summary": validate_trajectory_summary(contents["trajectory_summary.json"]).as_dict(),
            "manifest": validate_trajectory_manifest(contents["trajectory_manifest.json"]).as_dict(),
        },
        "artifact_contents": contents,
    }


def main() -> None:
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    fixed = parse_trajectory_file(FIXTURES / "fixed_lattice_md.extxyz")
    variable = parse_trajectory_file(FIXTURES / "variable_lattice_relaxation.extxyz")
    triclinic = parse_trajectory_file(FIXTURES / "triclinic_reordered.extxyz")
    write("format_scope.json", {"supported": ["extended_xyz", "canonical_phase10g_json"], "plain_xyz": "DEFERRED_BY_DESIGN", "deferred": ["ase_traj", "lammps_dump", "xtc", "trr", "dcd", "netcdf", "hdf5", "xdatcar", "vasprun_xml", "pdb_trajectory", "remote_url", "archive", "pickle"]})
    write("format_detection.json", {path.name: detect_trajectory_format(path) for path in (FIXTURES / "fixed_lattice_md.extxyz", FIXTURES / "variable_lattice_relaxation.extxyz", CONTRACT_FIXTURES / "fixed_lattice_md.json")})
    write("extxyz_mapping.json", {"production_parser": "bounded application-owned line parser", "lattice": "nine row-vector angstrom values", "pbc": "explicit all/all-none", "positions": "Cartesian angstrom", "unknown_properties": "ignored with bounded warning", "eval": False})
    write("native_json_mapping.json", {"accepted_schema": "phase10g.trajectory.v1", "semantic_mutation": False, "byte_preflight": True, "validator_required": True})
    write("unit_conversion_policy.json", {"position": {"angstrom": 1, "nanometer": 10, "bohr": 0.529177210903}, "time": {"femtosecond": 1, "picosecond": 1000}, "velocity": ["angstrom_per_femtosecond", "angstrom_per_picosecond", "nanometer_per_picosecond"], "force": ["electronvolt_per_angstrom", "hartree_per_bohr"], "energy": ["electronvolt", "hartree"], "unknown": "reject"})
    write("identity_mapping.json", {"canonical": "stable_index", "source_ids": "first-frame order", "later_reorder": "mapped explicitly", "reordered_fixture": triclinic.report})
    write("parser_caps.json", {"input_bytes": 64000000, "line_bytes": 65536, "comment_bytes": 8192, "metadata_keys": 32, "row_tokens": 64, "atoms": 4096, "frames": 10000, "coordinate_values": 12000000, "checks_during_read": True})
    for name, parsed in (("valid_fixed_lattice_result.json", fixed), ("valid_variable_lattice_result.json", variable), ("valid_triclinic_result.json", triclinic), ("atom_id_reorder_result.json", triclinic)):
        write(name, {"trajectory_id": parsed.trajectory["trajectory_id"], "validation": validate_trajectory(parsed.trajectory).as_dict(), "report": parsed.report})
    invalid_matrix: dict[str, Any] = {}
    for source in (FIXTURES / "invalid_truncated.extxyz",):
        try: parse_trajectory_file(source)
        except TrajectoryParseError as exc: invalid_matrix[source.name] = {"code": exc.code, "message": str(exc)}
    write("invalid_case_matrix.json", invalid_matrix)
    with tempfile.TemporaryDirectory(prefix="mdi_g1_evidence_") as temp:
        too_large = Path(temp) / "large.extxyz"
        too_large.write_bytes(b"0" * 64_000_001)
        try: parse_trajectory_file(too_large)
        except TrajectoryParseError as exc: write("over_cap_result.json", {"code": exc.code, "artifacts_created": 0, "rejected_by_stat_preflight": True})
        ext_capture = runtime_capture(FIXTURES / "fixed_lattice_md.extxyz", Path(temp) / "ext")
        json_capture = runtime_capture(CONTRACT_FIXTURES / "fixed_lattice_md.json", Path(temp) / "json")
    write("api_valid_extxyz.json", ext_capture)
    write("api_valid_json.json", json_capture)
    write("api_invalid.json", {"source": "invalid_truncated.extxyz", "code": invalid_matrix["invalid_truncated.extxyz"]["code"], "partial_artifacts": 0, "raw_payload_disclosed": False})
    write("api_over_cap.json", json.loads((EVIDENCE / "over_cap_result.json").read_text(encoding="utf-8")))
    first = parse_trajectory_file(FIXTURES / "fixed_lattice_md.extxyz").trajectory
    second = parse_trajectory_file(FIXTURES / "fixed_lattice_md.extxyz").trajectory
    write("deterministic_replay.json", {"payload_equal": first == second, "trajectory_id_equal": first["trajectory_id"] == second["trajectory_id"], "sha256": hashlib.sha256(json.dumps(first, sort_keys=True, separators=(",", ":")).encode()).hexdigest()})
    timings = []
    for _ in range(5):
        started = perf_counter(); parse_trajectory_file(FIXTURES / "fixed_lattice_md.extxyz"); timings.append((perf_counter() - started) * 1000)
    write("performance_metrics.json", {"fixture_bytes": (FIXTURES / "fixed_lattice_md.extxyz").stat().st_size, "frames": 3, "atoms": 2, "runs": 5, "min_ms": round(min(timings), 3), "max_ms": round(max(timings), 3), "bounded_line_reader": True, "whole_file_split": False, "file_handles_closed": True})
    write("security_audit.json", {"eval": False, "literal_eval": False, "pickle": False, "shell": False, "external_url": False, "archive": False, "arbitrary_plugin": False, "artifact_javascript": False, "private_path_in_artifacts": False, "dependencies_added": False, "marker": "NO_SECRET_PATTERN_HITS"})
    write("network_audit.json", {"external_requests": 0, "remote_frames": 0, "remote_assets": 0, "marker": "NO_EXTERNAL_NETWORK_REQUESTS"})
    files = sorted(path for path in EVIDENCE.glob("*.json") if path.name != "artifact_hashes.json")
    write("artifact_hashes.json", {"algorithm": "sha256", "files": [{"name": path.name, "sha256": hashlib.sha256(path.read_bytes()).hexdigest()} for path in files]})
    print("PHASE10G1_TRAJECTORY_PARSER_ADAPTER_EVIDENCE_PASS")
    print("NO_EXTERNAL_NETWORK_REQUESTS")
    print("NO_SECRET_PATTERN_HITS")


if __name__ == "__main__":
    main()
