from __future__ import annotations

import copy
import json
import shutil
from pathlib import Path
from typing import Any

from mdi_adapters.platform_builtin import (
    TRAJECTORY_VIEWER_BUDGETS,
    TRAJECTORY_VIEWER_CAPABILITIES,
    TRAJECTORY_VIEWER_TOOL_ID,
)
from mdi_api.repositories import InMemoryRepositoryBundle
from mdi_api.routers.planner import (
    PlannerJobsRequest,
    get_planner_analysis_plan,
    get_planner_job,
    get_planner_job_artifacts,
    get_planner_job_events,
    get_planner_job_result,
    get_planner_job_tool_calls,
    planner_jobs,
)
from mdi_artifact_core import canonical_trajectory_id, validate_trajectory
from mdi_llm import MockLLMProvider, PlannerRequest
from mdi_material_parsers import parse_file
from mdi_schemas import DataProfile
from mdi_tool_registry import load_manifests
from mdi_tool_registry.plan_validator import validate_plan
from mdi_workers import QueueWorkerRuntime


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "docs" / "phase10g" / "evidence" / "phase10g3_trajectory_performance_browser"
FIXTURES = ROOT / "docs" / "phase10g" / "fixtures" / "trajectory_import"
FORMAL_PROMPT = "Play this molecular dynamics trajectory."


def main() -> None:
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    shutil.rmtree(EVIDENCE / ".runtime", ignore_errors=True)
    registry = load_manifests()
    tool = registry.get_tool_by_id(TRAJECTORY_VIEWER_TOOL_ID)
    fixed = parse_file(
        FIXTURES / "fixed_lattice_md.extxyz",
        dataset_id="dataset_g3_fixed",
        file_id="trajectory",
    ).objects[0]
    variable = parse_file(
        FIXTURES / "variable_lattice_relaxation.extxyz",
        dataset_id="dataset_g3_variable",
        file_id="trajectory",
    ).objects[0]
    fixed_payload = copy.deepcopy(_trajectory_payload(fixed))
    many_frames = _many_frame_trajectory(fixed_payload, frame_count=64)
    degraded = _sized_trajectory(fixed_payload, atom_count=400)
    refused = copy.deepcopy(degraded)
    invalid = copy.deepcopy(fixed_payload)
    invalid["frames"][0]["atom_ids"] = list(reversed(invalid["frames"][0]["atom_ids"]))
    invalid["trajectory_id"] = canonical_trajectory_id(invalid)

    _write("formal_tool_registration.json", {
        "tool_id": tool.toolId,
        "adapter": "TrajectoryViewerAdapter",
        "unique_count": sum(item.toolId == TRAJECTORY_VIEWER_TOOL_ID for item in registry.list_tools()),
        "stage": "mvp",
        "display_target": tool.outputSchema.displayTarget.value,
        "artifact_types": [item.value for item in tool.artifactTypes],
        "input_object_type": tool.inputSchema.inputOptions[0].requiredObjectTypes[0].value,
        "params_schema": tool.paramsSchema,
        "resource_limits": tool.resourceLimits,
        "network_access": False,
        "deterministic": True,
    })
    _write("capability_contract.json", TRAJECTORY_VIEWER_CAPABILITIES)
    _write("performance_budget_contract.json", TRAJECTORY_VIEWER_BUDGETS)

    profile = _profile("fixed", frames=3, atoms=2)
    routing = {}
    for prompt in (
        FORMAL_PROMPT,
        "Inspect this relaxation trajectory frame by frame.",
        "Show the atomic motion in this extxyz trajectory.",
        "Calculate ensemble RDF from this trajectory.",
        "Compute diffusion coefficient and MSD.",
        "Infer changing chemical bonds in every frame.",
        "Edit frame 20 and trim this trajectory.",
    ):
        plan = _plan(prompt, profile)
        routing[prompt] = plan["steps"][0]["toolId"]
    _write("planner_routing.json", routing)

    validator_cases = {}
    base_plan = _plan(FORMAL_PROMPT, profile)
    for name, params in {
        "approved_defaults": base_plan["steps"][0]["params"],
        "dynamic_bonds": {"dynamicBonds": True},
        "editing": {"editing": True},
        "external_frame": {"frameSourceUrl": "external-frame-forbidden"},
        "arbitrary_renderer": {"rendererConfig": {"callback": "forbidden"}},
        "supercell_over_cap": {"supercell": [4, 1, 1]},
    }.items():
        candidate = copy.deepcopy(base_plan)
        candidate["steps"][0]["params"] = params
        result = validate_plan(candidate, registry=registry)
        validator_cases[name] = {"ok": result.ok, "errors": [error.code for error in result.errors]}
    _write("plan_validator_results.json", validator_cases)

    cases = {
        "api_valid_fixed.json": (fixed, _profile("fixed", frames=3, atoms=2)),
        "api_many_frames.json": (many_frames, _profile("many_frames", frames=64, atoms=2)),
        "api_valid_variable.json": (variable, _profile("variable", frames=3, atoms=2)),
        "api_degraded.json": (degraded, _profile("degraded", frames=2, atoms=400)),
        "api_refused.json": (refused, _profile("refused", frames=2, atoms=400)),
        "api_invalid.json": (invalid, _profile("invalid", frames=3, atoms=2)),
    }
    for filename, (trajectory, case_profile) in cases.items():
        _write(filename, _run_case(filename.removesuffix(".json").removeprefix("api_"), trajectory, case_profile))

    _write("performance_tier_matrix.json", {
        "fixed": {"atoms": 2, "frames": 3, "desktop": "interactive", "mobile": "interactive"},
        "many_frames": {"atoms": 2, "frames": 64, "desktop": "interactive", "mobile": "interactive", "purpose": "rapid_seek_and_cache_stress"},
        "variable": {"atoms": 2, "frames": 3, "desktop": "interactive", "mobile": "interactive"},
        "degraded": {"atoms": 400, "frames": 2, "desktop": "degraded", "mobile": "refused"},
        "refused": {"atoms": 400, "frames": 2, "supercell": [3, 3, 3], "displayed_instances": 10_800, "desktop": "refused", "mobile": "refused"},
        "chunked_indexed_storage": "DEFERRED_BY_DESIGN",
    })
    shutil.rmtree(EVIDENCE / ".runtime", ignore_errors=True)
    print("TRAJECTORY_FORMAL_API_EVIDENCE_PASS")


def _run_case(name: str, trajectory: Any, profile: DataProfile) -> dict[str, Any]:
    registry = load_manifests()
    plan = _plan(FORMAL_PROMPT, profile)
    if name == "refused":
        plan["steps"][0]["params"]["supercell"] = [3, 3, 3]
    validation = validate_plan(plan, registry=registry)
    if not validation.ok:
        raise RuntimeError(f"formal plan failed validation: {[error.code for error in validation.errors]}")
    repos = InMemoryRepositoryBundle.create()
    artifact_root = EVIDENCE / ".runtime" / name
    runtime = QueueWorkerRuntime(repositories=repos, registry=registry, artifact_root=artifact_root)
    request = PlannerJobsRequest(
        userPrompt=FORMAL_PROMPT,
        projectId=f"project_g3_{name}",
        datasetId=profile.datasetId,
        profileId=profile.profileId,
        enqueue=True,
    )
    created = planner_jobs(
        request,
        provider=MockLLMProvider(fixed_plan=plan),
        repositories=repos,
        queue_runtime=runtime,
        registry=registry,
    )
    if not created.ok or not created.job_id or not created.plan_id:
        raise RuntimeError("planner job was not persisted")
    worker = runtime.handle_job(created.job_id, object_store={"trajectory": trajectory})
    tool_call_records = get_planner_job_tool_calls(created.job_id, repositories=repos)
    tool_call_id = tool_call_records[0]["id"] if tool_call_records else ""
    artifact_records = get_planner_job_artifacts(created.job_id, repositories=repos)
    artifacts = []
    for record in artifact_records:
        stored = artifact_root / record["storageKey"]
        content = json.loads(stored.read_text(encoding="utf-8")) if stored.suffix == ".json" else stored.read_text(encoding="utf-8")
        artifacts.append({
            "id": f"artifact_{name}_{record['name'].replace('.', '_')}",
            "artifactId": f"artifact_{name}_{record['name'].replace('.', '_')}",
            "jobId": f"job_g3_{name}",
            "toolCallId": f"call_g3_{name}",
            "type": record["type"],
            "name": record["name"],
            "storageProvider": "local_evidence_capture",
            "contentHash": record["contentHash"],
            "sizeBytes": record["sizeBytes"],
            "metadata": _normalize_ids(
                _stable_metadata(record.get("metadata")),
                created.job_id,
                created.plan_id,
                name,
                tool_call_id,
            ),
            "content": content,
        })
    captured = {
        "capture_kind": "real_in_memory_planner_job_runtime",
        "request": request.model_dump(mode="json"),
        "create": {
            "ok": created.ok,
            "job_id": f"job_g3_{name}",
            "plan_id": f"plan_g3_{name}",
            "enqueued": created.enqueued,
            "executed": created.executed,
        },
        "analysis_plan": _normalize_ids(
            get_planner_analysis_plan(created.plan_id, repositories=repos),
            created.job_id,
            created.plan_id,
            name,
            tool_call_id,
        ),
        "job": _normalize_ids(
            get_planner_job(created.job_id, repositories=repos),
            created.job_id,
            created.plan_id,
            name,
            tool_call_id,
        ),
        "events": [
            _normalize_ids(
                _stable_event(event),
                created.job_id,
                created.plan_id,
                name,
                tool_call_id,
            )
            for event in get_planner_job_events(created.job_id, repositories=repos)
        ],
        "tool_calls": [_stable_tool_call(call, name) for call in tool_call_records],
        "artifacts": artifacts,
        "result": _normalize_ids(
            get_planner_job_result(created.job_id, repositories=repos),
            created.job_id,
            created.plan_id,
            name,
            tool_call_id,
        ),
        "worker": {"status": worker.status, "tool_call_count": worker.tool_call_count, "artifact_count": worker.artifact_count},
        "plan_validation": {"ok": validation.ok, "errors": []},
        "input_validation": validate_trajectory(_trajectory_payload(trajectory)).as_dict(),
    }
    expected_status = "failed" if name == "invalid" else "completed"
    if captured["worker"]["status"] != expected_status:
        raise RuntimeError(f"unexpected worker status for {name}: {captured['worker']['status']}")
    if name != "invalid" and (not artifacts or captured["tool_calls"][0]["toolId"] != TRAJECTORY_VIEWER_TOOL_ID):
        raise RuntimeError(f"formal artifacts missing for {name}")
    if name == "invalid" and artifacts:
        raise RuntimeError("invalid trajectory emitted artifacts")
    return captured


def _plan(prompt: str, profile: DataProfile) -> dict[str, Any]:
    registry = load_manifests()
    response = MockLLMProvider().generate_plan(
        PlannerRequest(
            user_prompt=prompt,
            dataset_id=profile.datasetId,
            profile_id=profile.profileId,
            tool_registry_version=registry.version,
        ),
        tools=registry.list_mvp_tools(),
        data_profile=profile,
    )
    if response.raw_json is None:
        raise RuntimeError("mock planner returned no plan")
    return response.raw_json


def _profile(name: str, *, frames: int, atoms: int) -> DataProfile:
    return DataProfile(
        profileId=f"profile_g3_{name}",
        datasetId=f"dataset_g3_{name}",
        version="1",
        datasetType="trajectory",
        objects=[{"id": "trajectory", "objectType": "Trajectory"}],
        trajectorySummary={"frames": frames, "atoms": atoms},
        createdAt="2026-07-13T00:00:00Z",
    )


def _sized_trajectory(source: dict[str, Any], *, atom_count: int) -> dict[str, Any]:
    payload = copy.deepcopy(source)
    payload["atoms"] = {
        "count": atom_count,
        "records": [
            {"atom_id": index, "species": "H", "label": f"H{index + 1}", "occupancy": 1.0}
            for index in range(atom_count)
        ],
    }
    positions = [
        [round((index % 17) / 17, 8), round((index // 17 % 17) / 17, 8), round((index // 289 % 17) / 17, 8)]
        for index in range(atom_count)
    ]
    frames = []
    for frame_index in range(2):
        frame = copy.deepcopy(source["frames"][frame_index])
        frame["frame_index"] = frame_index
        frame["atom_ids"] = list(range(atom_count))
        frame["positions"] = positions
        frame["velocities"] = None
        frame["forces"] = None
        frame["energy"] = None
        frame["temperature"] = None
        frames.append(frame)
    payload["frames"] = frames
    payload["properties"] = {"positions": True, "velocities": False, "forces": False, "energy": False, "temperature": False, "stress": False}
    payload["trajectory_id"] = canonical_trajectory_id(payload)
    result = validate_trajectory(payload)
    if not result.valid:
        raise RuntimeError(f"synthetic trajectory failed validation: {result.errors}")
    return payload


def _many_frame_trajectory(source: dict[str, Any], *, frame_count: int) -> dict[str, Any]:
    payload = copy.deepcopy(source)
    frames = []
    for frame_index in range(frame_count):
        frame = copy.deepcopy(source["frames"][frame_index % len(source["frames"])])
        frame["frame_index"] = frame_index
        frame["step"] = frame_index * 5
        frame["time"] = float(frame_index)
        shift = (frame_index % 50) / 500
        frame["positions"] = [
            [round((position[0] + shift) % 1.0, 8), position[1], position[2]]
            for position in frame["positions"]
        ]
        frames.append(frame)
    payload["frames"] = frames
    payload["trajectory_id"] = canonical_trajectory_id(payload)
    result = validate_trajectory(payload)
    if not result.valid:
        raise RuntimeError(f"many-frame trajectory failed validation: {result.errors}")
    return payload


def _trajectory_payload(value: Any) -> dict[str, Any]:
    payload = getattr(value, "payload", value)
    if isinstance(payload, dict) and isinstance(payload.get("trajectory"), dict):
        payload = payload["trajectory"]
    if not isinstance(payload, dict):
        raise RuntimeError("trajectory evidence input is not a canonical object")
    return payload


def _stable_metadata(value: Any) -> dict[str, Any]:
    if not isinstance(value, dict):
        return {}
    return {key: item for key, item in value.items() if key not in {"createdAt", "storageKey"}}


def _stable_event(event: dict[str, Any]) -> dict[str, Any]:
    return {key: event.get(key) for key in ("seq", "eventType", "status", "message", "progress", "payload")}


def _stable_tool_call(call: dict[str, Any], name: str) -> dict[str, Any]:
    return {
        "id": f"call_g3_{name}",
        "jobId": f"job_g3_{name}",
        "stepId": call.get("stepId"),
        "toolId": call.get("toolId"),
        "status": call.get("status"),
        "params": call.get("params"),
        "inputSummary": call.get("inputSummary"),
        "outputSummary": call.get("outputSummary"),
        "error": call.get("error"),
    }


def _normalize_ids(
    value: Any,
    job_id: str,
    plan_id: str,
    name: str,
    tool_call_id: str,
) -> Any:
    if isinstance(value, dict):
        return {
            key: _normalize_ids(item, job_id, plan_id, name, tool_call_id)
            for key, item in value.items()
            if key not in {"createdAt", "updatedAt", "created_at", "updated_at"}
        }
    if isinstance(value, list):
        return [
            _normalize_ids(item, job_id, plan_id, name, tool_call_id)
            for item in value
        ]
    if isinstance(value, str):
        replacements = (
            (tool_call_id, f"call_g3_{name}"),
            (job_id, f"job_g3_{name}"),
            (plan_id, f"plan_g3_{name}"),
        )
        for source, target in replacements:
            if source:
                value = value.replace(source, target)
    return value


def _write(name: str, payload: Any) -> None:
    (EVIDENCE / name).write_text(
        json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )


if __name__ == "__main__":
    main()
