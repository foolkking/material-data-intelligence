from __future__ import annotations

import json
import math
import tempfile
from pathlib import Path
from typing import Any

import pytest
from pymatgen.core import Lattice, Structure

from mdi_adapters import StructureViewerSceneAdapter, execute_tool_request
from mdi_adapters.context import ToolExecutionContext
from mdi_adapters.errors import ToolExecutionError
from mdi_api.repositories import InMemoryRepositoryBundle
from mdi_api.routers.planner import PlannerJobsRequest, planner_jobs
from mdi_artifact_core import validate_viewer_scene, validate_viewer_scene_manifest
from mdi_llm import MockLLMProvider, PlannerRequest
from mdi_schemas import AnalysisPlan, ArtifactType, DataProfile
from mdi_tool_registry import load_manifests
from mdi_tool_registry.plan_validator import validate_plan
from mdi_workers import QueueWorkerRuntime


def test_viewer_scene_adapter_generates_canonical_scene_manifest_summary_and_recipe() -> None:
    artifacts = _execute_adapter(object_store={"structures": [_si_structure()]})

    scene = _artifact_payload(artifacts, "viewer_scene.json")
    manifest = _artifact_payload(artifacts, "viewer_scene_manifest.json")
    summary = _artifact_text(artifacts, "summary.md")
    recipe = _artifact_payload(artifacts, "recipe.json")

    assert {artifact.name for artifact in artifacts["artifacts"]} == {
        "viewer_scene.json",
        "viewer_scene_manifest.json",
        "summary.md",
        "recipe.json",
    }
    assert scene["kind"] == "viewer_scene"
    assert scene["version"] == "viewer_scene.v1"
    assert scene["schema_version"] == "phase10f8.viewer_scene.v1"
    assert scene["metadata"]["formula"] == "Si"
    assert scene["scene"]["coordinate_basis"] == "cartesian_angstrom"
    assert scene["scene"]["lattice"]["vectors"] == [[5.43, 0.0, 0.0], [0.0, 5.43, 0.0], [0.0, 0.0, 5.43]]
    assert scene["scene"]["sites"][0]["xyz"] == [0.0, 0.0, 0.0]
    assert scene["security"]["renderer_required"] is False
    assert validate_viewer_scene(scene, raw_size_bytes=len(json.dumps(scene).encode("utf-8"))).valid
    assert manifest["schema_version"] == "phase10f9.viewer_scene_manifest.v1"
    assert manifest["preview_mode"] == "json_only"
    assert manifest["renderer_required"] is False
    assert manifest["executable_assets"] == "none"
    assert validate_viewer_scene_manifest(manifest).valid
    assert "# Viewer Scene Artifact" in summary
    assert "renderer not included" in summary
    assert "no interactive 3D rendering claimed" in summary
    assert recipe["schema_version"] == "phase10f12.viewer_scene.recipe.v1"
    assert recipe["tool_id"] == "structure.viewer_scene"
    assert recipe["deterministic"] is True
    assert recipe["renderer_included"] is False
    assert recipe["dependencies"]["new_dependencies_added"] is False


def test_viewer_scene_adapter_supports_multi_species_and_is_deterministic() -> None:
    first = _artifact_payload(_execute_adapter(object_store={"structures": [_nacl_structure()]}), "viewer_scene.json")
    second = _artifact_payload(_execute_adapter(object_store={"structures": [_nacl_structure()]}), "viewer_scene.json")

    assert first == second
    assert first["metadata"]["species"] == ["Cl", "Na"]
    assert [site["element"] for site in first["scene"]["sites"]] == ["Na", "Cl"]
    assert first["metadata"]["species_count"] == 2


def test_viewer_scene_adapter_bonds_can_be_disabled_or_bounded() -> None:
    disabled = _artifact_payload(
        _execute_adapter(object_store={"structures": [_nacl_structure()]}, params={"include_bonds": False}),
        "viewer_scene.json",
    )
    bounded = _artifact_payload(
        _execute_adapter(object_store={"structures": [_nacl_structure()]}, params={"include_bonds": True, "bond_cutoff_angstrom": 5.0}),
        "viewer_scene.json",
    )

    assert disabled["scene"]["bonds"] == []
    assert "VIEWER_SCENE_BONDS_SKIPPED" in _warning_codes(disabled)
    assert bounded["scene"]["bonds"][0]["policy"] == "distance_cutoff_non_authoritative"
    assert "VIEWER_SCENE_BONDS_NON_AUTHORITATIVE" in _warning_codes(bounded)


def test_viewer_scene_adapter_warning_caps_behavior() -> None:
    payload = _artifact_payload(
        _execute_adapter(
            object_store={"structures": [_nacl_structure()]},
            params={"max_sites": 2, "max_bonds": 0, "include_bonds": True, "bond_cutoff_angstrom": 5.0},
        ),
        "viewer_scene.json",
    )

    assert payload["validation"]["status"] == "passed_with_warnings"
    assert payload["caps"]["max_sites"] == 2
    assert payload["caps"]["max_bonds"] == 0
    assert {"VIEWER_SCENE_CAP_NEAR_LIMIT", "VIEWER_SCENE_BONDS_TRUNCATED"} <= set(_warning_codes(payload))
    assert validate_viewer_scene(payload).valid


def test_viewer_scene_adapter_rejects_invalid_params_and_numeric_values() -> None:
    with pytest.raises(ToolExecutionError) as unknown_error:
        _execute_adapter(object_store={"structures": [_si_structure()]}, params={"renderer_config": "nope"})
    assert unknown_error.value.details["errorType"] == "viewer_scene_invalid_params"

    with pytest.raises(ToolExecutionError) as cap_error:
        _execute_adapter(object_store={"structures": [_si_structure()]}, params={"max_sites": 999})
    assert cap_error.value.details["errorType"] == "viewer_scene_invalid_params"

    with pytest.raises(ToolExecutionError) as basis_error:
        _execute_adapter(object_store={"structures": [_si_structure()]}, params={"coordinate_basis": "fractional"})
    assert basis_error.value.details["errorType"] == "viewer_scene_coordinate_basis_invalid"

    bad_structure = Structure(Lattice.cubic(4.0), ["Si"], [[math.nan, 0.0, 0.0]], coords_are_cartesian=True)
    with pytest.raises(ToolExecutionError) as numeric_error:
        _execute_adapter(object_store={"structures": [bad_structure]})
    assert numeric_error.value.details["errorType"] == "viewer_scene_non_finite_numeric_value"


def test_viewer_scene_adapter_rejects_unsupported_malformed_and_multi_structure_inputs() -> None:
    with pytest.raises(ToolExecutionError) as unsupported_error:
        _execute_adapter(object_store={"structures": object()})
    assert unsupported_error.value.details["errorType"] == "unsupported_structure_format"

    with pytest.raises(ToolExecutionError) as malformed_error:
        _execute_adapter(object_store={"structures": "not a structure"})
    assert malformed_error.value.details["errorType"] == "unsupported_structure_format"

    with pytest.raises(ToolExecutionError) as multi_error:
        _execute_adapter(object_store={"structures": [_si_structure(), _nacl_structure()]})
    assert multi_error.value.details["errorType"] == "multiple_structures_unsupported"


def test_viewer_scene_adapter_artifacts_are_inert_and_url_free() -> None:
    artifacts = _execute_adapter(object_store={"structures": [_nacl_structure()]})
    combined = "\n".join(
        (artifacts["root"] / artifact.storageKey).read_text(encoding="utf-8")
        for artifact in artifacts["artifacts"]
    ).lower()
    payload_combined = "\n".join(
        (artifacts["root"] / artifact.storageKey).read_text(encoding="utf-8")
        for artifact in artifacts["artifacts"]
        if artifact.name != "summary.md"
    ).lower()

    for marker in (
        "<script",
        "</script",
        "javascript:",
        "http://",
        "https://",
        "<canvas",
        "<iframe",
        "dangerouslysetinnerhtml",
        "callback",
        "eval(",
        "function(",
    ):
        assert marker not in combined
    assert "three.js" not in payload_combined
    assert "webgl" not in payload_combined


def test_viewer_scene_tool_registered_with_strict_schema_and_no_renderer_capabilities() -> None:
    registry = load_manifests()
    tool = registry.get_tool_by_id("structure.viewer_scene")
    ids = [item.toolId for item in registry.list_tools()]

    assert ids.count("structure.viewer_scene") == 1
    assert tool in registry.list_mvp_tools()
    assert tool.domain == "structure"
    assert tool.adapter == "StructureViewerSceneAdapter"
    assert tool.paramsSchema["additionalProperties"] is False
    assert set(tool.paramsSchema["properties"]) >= {
        "include_bonds",
        "bond_cutoff_angstrom",
        "max_sites",
        "max_bonds",
        "coordinate_basis",
        "include_cartesian_positions",
        "include_fractional_positions",
        "cell_expansion",
        "style_preset",
        "camera_preset",
    }
    assert tool.resourceLimits["maxSites"] == 256
    assert tool.resourceLimits["maxBonds"] == 2048
    assert tool.artifactTypes == [
        ArtifactType.structure_json,
        ArtifactType.table_json,
        ArtifactType.summary_md,
        ArtifactType.recipe_json,
    ]
    description = tool.description.lower()
    assert "viewer_scene.v1" in description
    assert "json-only" in description
    assert "no interactive 3d viewer" in description
    assert "webgl" in description
    assert "javascript" in description
    assert "external resources" in description


def test_viewer_scene_plan_validator_accepts_registered_params() -> None:
    plan = _valid_viewer_scene_plan()
    result = validate_plan(plan.model_dump(mode="json"), registry=load_manifests())

    assert result.ok


@pytest.mark.parametrize(
    "prompt",
    [
        "生成这个结构的 viewer scene JSON",
        "创建 viewer_scene.v1 artifact",
        "导出这个晶体的 viewer scene 数据",
        "Build an inert viewer scene artifact for this structure",
        "Create JSON scene data for a future structure renderer",
    ],
)
def test_mock_planner_routes_minimal_viewer_scene_prompts(prompt: str) -> None:
    plan = _mock_plan(prompt)

    assert plan["steps"][0]["toolId"] == "structure.viewer_scene"
    assert plan["steps"][0]["params"]["coordinate_basis"] == "cartesian_angstrom"
    assert plan["expectedArtifacts"][0]["name"] == "viewer_scene.json"
    assert any(item["name"] == "viewer_scene_manifest.json" for item in plan["expectedArtifacts"])


@pytest.mark.parametrize(
    "prompt",
    [
        "打开交互式 3D viewer",
        "用 WebGL 显示这个晶体",
        "Render this crystal with Three.js",
        "显示可旋转的真实 3D 晶体",
        "生成 Brillouin zone 3D",
        "播放结构轨迹",
        "显示 phonon animation",
        "Generate XRD pattern",
        "Create RDF plot",
        "Create a coordination number histogram",
    ],
)
def test_mock_planner_does_not_route_full_viewer_or_existing_tools_to_viewer_scene(prompt: str) -> None:
    plan = _mock_plan(prompt)

    assert plan["steps"][0]["toolId"] != "structure.viewer_scene"


def test_execute_tool_request_runs_viewer_scene_through_registry_adapter_path(tmp_path: Path) -> None:
    context = _context(tmp_path, object_store={"structures": [_si_structure()]})
    result = execute_tool_request(context, _tool_request())

    assert result.tool.toolId == "structure.viewer_scene"
    assert not result.cache_hit
    assert {artifact.name for artifact in result.artifacts} == {
        "viewer_scene.json",
        "viewer_scene_manifest.json",
        "summary.md",
        "recipe.json",
    }
    scene = _read_artifact(tmp_path, result.artifacts, "viewer_scene.json")
    manifest = _read_artifact(tmp_path, result.artifacts, "viewer_scene_manifest.json")
    assert validate_viewer_scene(scene).valid
    assert validate_viewer_scene_manifest(manifest).valid
    assert result.artifacts[0].metadata.provenance["adapter"] == "structure.viewer_scene"


def test_persisted_viewer_scene_plan_executes_exactly_one_tool_call(tmp_path: Path) -> None:
    repos = InMemoryRepositoryBundle.create()
    plan = _valid_viewer_scene_plan()
    provider = MockLLMProvider(fixed_plan=plan.model_dump(mode="json"))
    result = planner_jobs(
        PlannerJobsRequest(
            userPrompt="Build an inert viewer scene artifact for this structure.",
            projectId="project_10f12",
            datasetId="dataset_structure",
            profileId="profile_structure",
            enqueue=True,
        ),
        provider=provider,
        repositories=repos,
        queue_runtime=QueueWorkerRuntime(repositories=repos, registry=load_manifests(), artifact_root=tmp_path / "artifacts"),
        registry=load_manifests(),
    )

    assert result.ok
    runtime = QueueWorkerRuntime(repositories=repos, registry=load_manifests(), artifact_root=tmp_path / "artifacts")
    worker_result = runtime.handle_job(result.job_id or "", object_store={"structures": [_si_structure()]})

    tool_calls = repos.tool_calls.list_for_job(result.job_id or "")
    artifacts = repos.artifacts.list_for_job(result.job_id or "")
    assert worker_result.status == "completed"
    assert worker_result.tool_call_count == 1
    assert tool_calls[0]["toolId"] == "structure.viewer_scene"
    assert {artifact["name"] for artifact in artifacts} >= {
        "viewer_scene.json",
        "viewer_scene_manifest.json",
        "summary.md",
        "recipe.json",
    }
    assert next(artifact for artifact in artifacts if artifact["name"] == "viewer_scene.json")["type"] == "structure_json"


def _execute_adapter(
    *,
    object_store: dict[str, Any],
    params: dict[str, Any] | None = None,
    artifact_types: list[ArtifactType] | None = None,
) -> dict[str, Any]:
    artifact_root = Path(tempfile.mkdtemp(prefix="mdi_phase10f12_artifacts_"))
    context = _context(artifact_root, object_store=object_store)
    return {
        "root": artifact_root,
        "artifacts": StructureViewerSceneAdapter().execute(context, _tool_request(params=params, artifact_types=artifact_types)),
    }


def _context(root: Path, *, object_store: dict[str, Any]) -> ToolExecutionContext:
    return ToolExecutionContext(
        job_id="job_10f12",
        project_id="project_10f12",
        dataset_id="dataset_structure",
        tool_id="structure.viewer_scene",
        tool_version="0.1.0",
        adapter_version="0.1.0",
        registry_version=load_manifests().version,
        artifact_root=root,
        object_store=object_store,
        resource_limits={"maxAtomsPerStructure": 256, "maxStructures": 1, "maxSites": 256, "maxBonds": 2048},
    )


def _tool_request(
    *,
    params: dict[str, Any] | None = None,
    artifact_types: list[ArtifactType] | None = None,
) -> dict[str, Any]:
    return {
        "jobId": "job_10f12",
        "stepId": "step_001",
        "toolId": "structure.viewer_scene",
        "inputRefs": [{"refType": "normalized_object", "ref": "structures", "objectType": "Structure"}],
        "params": params or {},
        "artifactTypes": [
            artifact_type.value
            for artifact_type in (
                artifact_types
                or [
                    ArtifactType.structure_json,
                    ArtifactType.table_json,
                    ArtifactType.summary_md,
                    ArtifactType.recipe_json,
                ]
            )
        ],
    }


def _artifact_payload(result: dict[str, Any], name: str) -> dict[str, Any]:
    artifact = next(item for item in result["artifacts"] if item.name == name)
    return json.loads((result["root"] / artifact.storageKey).read_text(encoding="utf-8"))


def _artifact_text(result: dict[str, Any], name: str) -> str:
    artifact = next(item for item in result["artifacts"] if item.name == name)
    return (result["root"] / artifact.storageKey).read_text(encoding="utf-8")


def _read_artifact(root: Path, artifacts: list[Any], name: str) -> dict[str, Any]:
    artifact = next(item for item in artifacts if item.name == name)
    return json.loads((root / artifact.storageKey).read_text(encoding="utf-8"))


def _warning_codes(payload: dict[str, Any]) -> list[str]:
    codes: list[str] = []
    for warning in payload.get("warnings") or []:
        codes.append(str(warning.get("code")) if isinstance(warning, dict) else str(warning).split(":", 1)[0])
    return codes


def _mock_plan(prompt: str) -> dict[str, Any]:
    response = MockLLMProvider().generate_plan(
        PlannerRequest(
            user_prompt=prompt,
            dataset_id="dataset_structure",
            profile_id="profile_structure",
            tool_registry_version=load_manifests().version,
        ),
        tools=load_manifests().list_mvp_tools(),
        data_profile=_structure_profile(),
    )
    assert response.raw_json is not None
    return response.raw_json


def _valid_viewer_scene_plan() -> AnalysisPlan:
    return AnalysisPlan.model_validate(
        {
            "schemaVersion": "0.1",
            "goal": "viewer scene",
            "datasetId": "dataset_structure",
            "profileId": "profile_structure",
            "toolRegistryVersion": load_manifests().version,
            "assumptions": [],
            "warnings": [],
            "steps": [
                {
                    "stepId": "step_001",
                    "toolId": "structure.viewer_scene",
                    "purpose": "Create inert viewer_scene.v1 JSON.",
                    "reason": "test",
                    "inputRefs": [{"refType": "normalized_object", "ref": "structures", "objectType": "Structure"}],
                    "params": {
                        "include_bonds": True,
                        "bond_cutoff_angstrom": 3.0,
                        "max_sites": 256,
                        "max_bonds": 2048,
                        "coordinate_basis": "cartesian_angstrom",
                        "include_cartesian_positions": True,
                        "include_fractional_positions": True,
                        "cell_expansion": [1, 1, 1],
                        "style_preset": "default",
                        "camera_preset": "auto",
                    },
                    "output": {"artifactTypes": ["structure_json", "table_json", "summary_md", "recipe_json"]},
                }
            ],
            "expectedArtifacts": [
                {"name": "viewer_scene.json", "type": "structure_json", "fromStepId": "step_001"},
                {"name": "viewer_scene_manifest.json", "type": "table_json", "fromStepId": "step_001"},
                {"name": "summary.md", "type": "summary_md", "fromStepId": "step_001"},
                {"name": "recipe.json", "type": "recipe_json", "fromStepId": "step_001"},
            ],
        }
    )


def _si_structure() -> Structure:
    return Structure(
        Lattice.cubic(5.43),
        ["Si", "Si"],
        [[0.0, 0.0, 0.0], [0.25, 0.25, 0.25]],
    )


def _nacl_structure() -> Structure:
    return Structure(
        Lattice.cubic(5.64),
        ["Na", "Cl"],
        [[0.0, 0.0, 0.0], [0.5, 0.5, 0.5]],
    )


def _structure_profile() -> DataProfile:
    return DataProfile.model_validate(
        {
            "schemaVersion": "0.1",
            "profileId": "profile_structure",
            "datasetId": "dataset_structure",
            "version": "1",
            "datasetType": "structure_collection",
            "files": [{"path": "simple_cubic.cif", "format": "cif", "sizeBytes": 512}],
            "objects": [{"objectType": "Structure", "count": 1, "source": "simple_cubic.cif"}],
            "structureSummary": {
                "nStructures": 1,
                "elements": ["Si"],
                "formulaStats": {"total": 1, "uniqueCount": 1},
            },
            "qualityIssues": [],
            "recommendedTasks": [],
            "createdAt": "2026-07-11T00:00:00+00:00",
        }
    )
