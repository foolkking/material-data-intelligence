from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

from mdi_adapters import ToolExecutionContext
from mdi_adapters.platform_builtin import (
    TRAJECTORY_VIEWER_BUDGETS,
    TRAJECTORY_VIEWER_CAPABILITIES,
    TRAJECTORY_VIEWER_TOOL_ID,
    TrajectoryViewerAdapter,
)
from mdi_api.repositories import InMemoryRepositoryBundle
from mdi_api.routers.planner import PlannerJobsRequest, planner_jobs
from mdi_artifact_core import (
    validate_trajectory,
    validate_trajectory_manifest,
    validate_trajectory_summary,
)
from mdi_llm import MockLLMProvider, PlannerRequest
from mdi_material_parsers import parse_file
from mdi_schemas import DataProfile, MaterialObjectType, ToolExecutionRequest
from mdi_tool_registry import load_manifests
from mdi_tool_registry.plan_validator import validate_plan
from mdi_workers import QueueWorkerRuntime


ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "docs" / "phase10g" / "fixtures" / "trajectory_import" / "fixed_lattice_md.extxyz"
ARTIFACT_TYPES = [
    "trajectory_json",
    "trajectory_summary_json",
    "trajectory_report_json",
    "trajectory_manifest_json",
]
ARTIFACT_NAMES = [
    "trajectory.json",
    "trajectory_summary.json",
    "trajectory_parse_report.json",
    "trajectory_manifest.json",
]


def _trajectory_profile() -> DataProfile:
    return DataProfile(
        profileId="profile_trajectory_viewer",
        datasetId="dataset_trajectory_viewer",
        version="1",
        datasetType="trajectory",
        objects=[{"id": "trajectory", "objectType": "Trajectory"}],
        trajectorySummary={"frames": 3, "atoms": 2},
        createdAt="2026-07-13T00:00:00Z",
    )


def _structure_profile() -> DataProfile:
    return DataProfile(
        profileId="profile_structure",
        datasetId="dataset_structure",
        version="1",
        datasetType="structure_collection",
        objects=[{"id": "structure", "objectType": "Structure"}],
        structureSummary={"nStructures": 1},
        createdAt="2026-07-13T00:00:00Z",
    )


def _planner_plan(prompt: str, profile: DataProfile | None = None) -> dict:
    registry = load_manifests()
    selected_profile = profile or _trajectory_profile()
    response = MockLLMProvider().generate_plan(
        PlannerRequest(
            user_prompt=prompt,
            dataset_id=selected_profile.datasetId,
            profile_id=selected_profile.profileId,
            tool_registry_version=registry.version,
        ),
        tools=registry.list_mvp_tools(),
        data_profile=selected_profile,
    )
    assert response.raw_json is not None
    return response.raw_json


def _viewer_context(tmp_path: Path, object_store: dict[str, object]) -> ToolExecutionContext:
    registry = load_manifests()
    tool = registry.get_tool_by_id(TRAJECTORY_VIEWER_TOOL_ID)
    return ToolExecutionContext(
        job_id="job_trajectory_viewer",
        project_id="project_trajectory_viewer",
        dataset_id="dataset_trajectory_viewer",
        tool_id=tool.toolId,
        tool_version=tool.version,
        adapter_version="1.0.0",
        registry_version=registry.version,
        artifact_root=tmp_path / "artifacts",
        tool_call_id="call_trajectory_viewer",
        object_store=object_store,
        resource_limits=tool.resourceLimits,
    )


def _viewer_request(params: dict | None = None) -> ToolExecutionRequest:
    return ToolExecutionRequest(
        jobId="job_trajectory_viewer",
        stepId="step_trajectory_viewer",
        toolId=TRAJECTORY_VIEWER_TOOL_ID,
        inputRefs=[{"refType": "normalized_object", "ref": "trajectory", "objectType": "Trajectory"}],
        params=params or {},
        artifactTypes=ARTIFACT_TYPES,
    )


def _read_artifact(tmp_path: Path, artifacts: list, name: str) -> dict:
    artifact = next(item for item in artifacts if item.name == name)
    return json.loads((tmp_path / "artifacts" / artifact.storageKey).read_text(encoding="utf-8"))


def test_formal_trajectory_viewer_registry_identity_is_unique_strict_and_truthful() -> None:
    registry = load_manifests()
    ids = [tool.toolId for tool in registry.list_tools()]
    assert ids.count(TRAJECTORY_VIEWER_TOOL_ID) == 1
    tool = registry.get_tool_by_id(TRAJECTORY_VIEWER_TOOL_ID)
    assert tool in registry.list_mvp_tools()
    assert [item.value for item in tool.artifactTypes] == ARTIFACT_TYPES
    assert tool.outputSchema.displayTarget.value == "trajectory"
    assert tool.inputSchema.inputOptions[0].requiredObjectTypes == [MaterialObjectType.Trajectory]
    assert tool.paramsSchema["additionalProperties"] is False
    assert tool.paramsSchema["properties"]["performanceMode"] == {"const": "auto"}
    assert tool.paramsSchema["properties"]["bondMode"] == {"const": "none"}
    assert tool.resourceLimits["maxPendingFrameRequests"] == 1
    assert tool.resourceLimits["maxPlaybackFps"] == 30
    description = tool.description.lower()
    for supported in ("play", "stable atom", "variable lattice", "picking", "supercell", "clipping"):
        assert supported in description
    for unsupported in ("dynamic bonds", "analytics", "editing", "video export", "external network"):
        assert unsupported in description


@pytest.mark.parametrize(
    "prompt",
    (
        "Play this molecular dynamics trajectory.",
        "Inspect this relaxation trajectory frame by frame.",
        "Show the atomic motion in this extxyz trajectory.",
        "打开这个轨迹查看器并逐帧查看原子运动。",
    ),
)
def test_mock_planner_routes_viewer_intent_to_formal_tool(prompt: str) -> None:
    registry = load_manifests()
    plan = _planner_plan(prompt)
    assert plan["steps"][0]["toolId"] == TRAJECTORY_VIEWER_TOOL_ID
    assert plan["steps"][0]["params"] == {
        "playbackSpeed": 1,
        "loop": False,
        "supercell": [1, 1, 1],
        "showCell": True,
        "clipping": False,
        "performanceMode": "auto",
        "bondMode": "none",
    }
    assert [item["type"] for item in plan["expectedArtifacts"]] == ARTIFACT_TYPES
    assert validate_plan(plan, registry=registry).ok


@pytest.mark.parametrize(
    "prompt",
    (
        "Calculate ensemble RDF from this trajectory.",
        "Compute the diffusion coefficient and MSD.",
        "Infer changing chemical bonds in every frame.",
        "Edit frame 20 and trim this trajectory.",
        "Export this trajectory as MP4 video.",
    ),
)
def test_mock_planner_does_not_route_unsupported_analysis_or_editing(prompt: str) -> None:
    assert _planner_plan(prompt)["steps"][0]["toolId"] != TRAJECTORY_VIEWER_TOOL_ID


def test_static_structure_viewer_and_trajectory_viewer_remain_separate() -> None:
    static = _planner_plan("Open this crystal in the interactive 3D viewer.", _structure_profile())
    assert static["steps"][0]["toolId"] == "structure.viewer_3d"
    trajectory = _planner_plan("Play this trajectory frame by frame.")
    assert trajectory["steps"][0]["toolId"] == TRAJECTORY_VIEWER_TOOL_ID
    assert trajectory["steps"][0]["toolId"] != "structure.viewer_3d"


@pytest.mark.parametrize(
    "invalid_params",
    (
        {"dynamicBonds": True},
        {"editing": True},
        {"frameSourceUrl": "https://example.invalid/trajectory.json"},
        {"rendererConfig": {"callback": "alert(1)"}},
        {"playbackSpeed": 8},
        {"supercell": [4, 1, 1]},
        {"bondMode": "dynamic"},
    ),
)
def test_plan_validator_rejects_unapproved_viewer_options(invalid_params: dict) -> None:
    registry = load_manifests()
    plan = _planner_plan("Play this molecular dynamics trajectory.")
    plan["steps"][0]["params"] = invalid_params
    result = validate_plan(plan, registry=registry)
    assert not result.ok
    assert any(error.code == "PARAMS_SCHEMA_INVALID" for error in result.errors)


def test_formal_adapter_emits_canonical_artifacts_and_inert_product_provenance(tmp_path: Path) -> None:
    parsed = parse_file(FIXTURE, dataset_id="dataset_trajectory_viewer", file_id="trajectory").objects[0]
    artifacts = TrajectoryViewerAdapter().execute(
        _viewer_context(tmp_path, {"trajectory": parsed}),
        _viewer_request({"playbackSpeed": 2, "loop": True, "supercell": [2, 1, 1]}),
    )
    assert [item.name for item in artifacts] == ARTIFACT_NAMES
    assert all(item.metadata.toolId == TRAJECTORY_VIEWER_TOOL_ID for item in artifacts)
    trajectory = _read_artifact(tmp_path, artifacts, "trajectory.json")
    summary = _read_artifact(tmp_path, artifacts, "trajectory_summary.json")
    manifest = _read_artifact(tmp_path, artifacts, "trajectory_manifest.json")
    assert validate_trajectory(trajectory).valid
    assert validate_trajectory_summary(summary).valid
    assert validate_trajectory_manifest(manifest).valid
    provenance = artifacts[0].metadata.provenance
    assert provenance["formalViewerToolId"] == TRAJECTORY_VIEWER_TOOL_ID
    assert provenance["rendererIncluded"] is False
    assert provenance["externalAssets"] == "none"
    assert provenance["viewerLaunch"] == {
        "trajectoryId": trajectory["trajectory_id"],
        "initialFrame": 0,
        "performanceMode": "interactive",
        "displayedInstances": 4,
        "coordinateValues": 18,
        "options": {
            "playbackSpeed": 2,
            "loop": True,
            "supercell": [2, 1, 1],
            "showCell": True,
            "clipping": False,
            "performanceMode": "auto",
            "bondMode": "none",
        },
    }
    assert provenance["viewerCapabilities"] == TRAJECTORY_VIEWER_CAPABILITIES
    assert provenance["viewerBudgets"] == TRAJECTORY_VIEWER_BUDGETS
    assert provenance["viewerCapabilities"]["dynamic_bonds"] is False
    assert provenance["viewerCapabilities"]["ensemble_rdf"] is False


def test_formal_product_job_is_persisted_executed_and_deterministic(tmp_path: Path) -> None:
    registry = load_manifests()
    plan = _planner_plan("Play this molecular dynamics trajectory.")
    assert validate_plan(plan, registry=registry).ok
    parsed = parse_file(FIXTURE, dataset_id="dataset_trajectory_viewer", file_id="trajectory").objects[0]

    outputs: list[dict[str, dict]] = []
    for suffix in ("first", "second"):
        repos = InMemoryRepositoryBundle.create()
        root = tmp_path / suffix
        runtime = QueueWorkerRuntime(repositories=repos, registry=registry, artifact_root=root)
        created = planner_jobs(
            PlannerJobsRequest(
                userPrompt="Play this molecular dynamics trajectory.",
                projectId="project_trajectory_viewer",
                datasetId="dataset_trajectory_viewer",
                profileId="profile_trajectory_viewer",
                enqueue=True,
            ),
            provider=MockLLMProvider(fixed_plan=plan),
            repositories=repos,
            queue_runtime=runtime,
            registry=registry,
        )
        assert created.ok and created.job_id and created.plan_id and created.enqueued
        result = runtime.handle_job(created.job_id, object_store={"trajectory": parsed})
        records = repos.artifacts.list_for_job(created.job_id)
        calls = repos.tool_calls.list_for_job(created.job_id)
        assert result.status == "completed"
        assert len(calls) == 1 and calls[0]["toolId"] == TRAJECTORY_VIEWER_TOOL_ID
        assert [item["name"] for item in records] == ARTIFACT_NAMES
        persisted_provenance = records[0]["metadata"]["provenance"]
        assert persisted_provenance["formalViewerToolId"] == TRAJECTORY_VIEWER_TOOL_ID
        assert persisted_provenance["viewerLaunch"]["performanceMode"] == "interactive"
        assert persisted_provenance["viewerCapabilities"]["dynamic_bonds"] is False
        assert persisted_provenance["viewerBudgets"]["max_pending_requests"] == 1
        assert persisted_provenance["toolId"] == TRAJECTORY_VIEWER_TOOL_ID
        assert persisted_provenance["planId"] == created.plan_id
        contents = {
            record["name"]: json.loads((root / record["storageKey"]).read_text(encoding="utf-8"))
            for record in records
        }
        outputs.append(contents)

    assert outputs[0] == outputs[1]
