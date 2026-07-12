from __future__ import annotations

import json
from pathlib import Path

import pytest
from pymatgen.core import Lattice, Structure

from mdi_adapters import StructureViewer3DAdapter
from mdi_adapters.context import ToolExecutionContext
from mdi_api.repositories import InMemoryRepositoryBundle
from mdi_api.routers.planner import PlannerJobsRequest, planner_jobs
from mdi_artifact_core import validate_viewer_scene, validate_viewer_scene_manifest
from mdi_llm import MockLLMProvider, PlannerRequest
from mdi_schemas import AnalysisPlan, ArtifactType, DataProfile, ToolExecutionRequest
from mdi_tool_registry import load_manifests
from mdi_tool_registry.plan_validator import validate_plan
from mdi_workers import QueueWorkerRuntime


CANONICAL_PARAMS = {
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
}


def test_formal_viewer_registry_identity_is_unique_and_canonical() -> None:
    registry = load_manifests()
    tool = registry.get_tool_by_id("structure.viewer_3d")
    ids = [item.toolId for item in registry.list_tools()]

    assert ids.count("structure.viewer_3d") == 1
    assert tool.adapter == "StructureViewer3DAdapter"
    assert tool.artifactTypes == [ArtifactType.structure_json, ArtifactType.table_json, ArtifactType.summary_md, ArtifactType.recipe_json]
    assert tool.paramsSchema["additionalProperties"] is False
    assert tool.paramsSchema == registry.get_tool_by_id("structure.viewer_scene").paramsSchema
    assert tool.resourceLimits["maxSites"] == 256
    assert tool.resourceLimits["maxBonds"] == 2048
    assert "canonical inert viewer_scene.v1" in tool.description
    assert "trajectories" in tool.description.lower()
    assert "editing" in tool.description.lower()


@pytest.mark.parametrize("prompt", [
    "打开这个晶体的 3D 查看器",
    "交互查看这个晶体结构",
    "显示这个结构的三维模型",
    "Render this crystal in the structure viewer",
    "Open an interactive 3D view of this CIF",
])
def test_natural_viewer_prompts_route_to_formal_tool(prompt: str) -> None:
    plan = _mock_plan(prompt)
    assert plan["steps"][0]["toolId"] == "structure.viewer_3d"
    assert plan["steps"][0]["params"] == CANONICAL_PARAMS
    assert [item["name"] for item in plan["expectedArtifacts"]] == [
        "viewer_scene.json", "viewer_scene_manifest.json", "summary.md", "recipe.json",
    ]


def test_explicit_json_and_legacy_prompts_remain_separate() -> None:
    assert _mock_plan("Build inert viewer scene data")["steps"][0]["toolId"] == "structure.viewer_scene"
    assert _mock_plan("Create viewer scene metadata for this CIF")["steps"][0]["toolId"] == "structure.viewer_scene_metadata"
    assert _mock_plan("Create a static viewer export package for this structure")["steps"][0]["toolId"] == "structure.viewer_export_package"


@pytest.mark.parametrize("prompt", [
    "Show a phonon animation", "Render the Brillouin zone", "Animate this trajectory",
    "Show charge density isosurfaces", "Edit this structure", "Generate XRD pattern",
    "Create RDF plot", "Create a coordination number histogram",
])
def test_unsupported_and_existing_domains_do_not_route_to_formal_viewer(prompt: str) -> None:
    assert _mock_plan(prompt)["steps"][0]["toolId"] != "structure.viewer_3d"


def test_formal_adapter_generates_valid_inert_artifacts(tmp_path: Path) -> None:
    artifacts = StructureViewer3DAdapter().execute(_context(tmp_path), _request())
    assert {item.name for item in artifacts} == {"viewer_scene.json", "viewer_scene_manifest.json", "summary.md", "recipe.json"}
    scene = _read(tmp_path, artifacts, "viewer_scene.json")
    manifest = _read(tmp_path, artifacts, "viewer_scene_manifest.json")
    recipe = _read(tmp_path, artifacts, "recipe.json")
    assert validate_viewer_scene(scene).valid
    assert validate_viewer_scene_manifest(manifest).valid
    assert scene["provenance"]["tool_id"] == "structure.viewer_3d"
    assert manifest["tool_id"] == "structure.viewer_3d"
    assert recipe["tool_id"] == "structure.viewer_3d"
    assert recipe["renderer_included"] is False
    assert all(item.type != ArtifactType.matterviz_html for item in artifacts)


def test_formal_plan_validator_and_queue_runtime_complete_independently_of_browser(tmp_path: Path) -> None:
    plan = _plan()
    assert validate_plan(plan.model_dump(mode="json"), registry=load_manifests()).ok
    repos = InMemoryRepositoryBundle.create()
    runtime = QueueWorkerRuntime(repositories=repos, registry=load_manifests(), artifact_root=tmp_path / "runtime")
    created = planner_jobs(
        PlannerJobsRequest(
            userPrompt="Open an interactive 3D view of this CIF", projectId="project_10f15",
            datasetId="dataset_structure", profileId="profile_structure", enqueue=True,
        ),
        provider=MockLLMProvider(fixed_plan=plan.model_dump(mode="json")), repositories=repos,
        queue_runtime=runtime, registry=load_manifests(),
    )
    assert created.ok and created.job_id
    result = runtime.handle_job(created.job_id, object_store={"structures": [_structure()]})

    assert result.status == "completed"
    calls = repos.tool_calls.list_for_job(created.job_id)
    stored = repos.artifacts.list_for_job(created.job_id)
    assert calls[0]["toolId"] == "structure.viewer_3d"
    assert {item["name"] for item in stored} == {"viewer_scene.json", "viewer_scene_manifest.json", "summary.md", "recipe.json"}


def _context(root: Path) -> ToolExecutionContext:
    tool = load_manifests().get_tool_by_id("structure.viewer_3d")
    return ToolExecutionContext(
        job_id="job_10f15", project_id="project_10f15", dataset_id="dataset_structure",
        tool_id=tool.toolId, tool_version=tool.version, adapter_version="1.0.0",
        registry_version=load_manifests().version, artifact_root=root,
        tool_call_id="call_10f15", object_store={"structures": [_structure()]}, resource_limits=tool.resourceLimits,
    )


def _request() -> ToolExecutionRequest:
    return ToolExecutionRequest(
        jobId="job_10f15", stepId="step_001", toolId="structure.viewer_3d",
        inputRefs=[{"refType": "normalized_object", "ref": "structures", "objectType": "Structure"}],
        params=CANONICAL_PARAMS, artifactTypes=["structure_json", "table_json", "summary_md", "recipe_json"],
    )


def _plan() -> AnalysisPlan:
    return AnalysisPlan.model_validate({
        "schemaVersion": "0.1", "goal": "Open the minimal structure viewer", "datasetId": "dataset_structure",
        "profileId": "profile_structure", "toolRegistryVersion": load_manifests().version,
        "assumptions": [], "warnings": [],
        "steps": [{"stepId": "step_001", "toolId": "structure.viewer_3d", "purpose": "Generate canonical viewer artifacts.",
            "reason": "A periodic structure is available.", "inputRefs": [{"refType": "normalized_object", "ref": "structures", "objectType": "Structure"}],
            "params": CANONICAL_PARAMS, "output": {"artifactTypes": ["structure_json", "table_json", "summary_md", "recipe_json"]}}],
        "expectedArtifacts": [
            {"name": "viewer_scene.json", "type": "structure_json", "fromStepId": "step_001"},
            {"name": "viewer_scene_manifest.json", "type": "table_json", "fromStepId": "step_001"},
            {"name": "summary.md", "type": "summary_md", "fromStepId": "step_001"},
            {"name": "recipe.json", "type": "recipe_json", "fromStepId": "step_001"},
        ],
    })


def _mock_plan(prompt: str) -> dict:
    response = MockLLMProvider().generate_plan(
        PlannerRequest(user_prompt=prompt, dataset_id="dataset_structure", profile_id="profile_structure", tool_registry_version=load_manifests().version),
        tools=load_manifests().list_mvp_tools(), data_profile=_profile(),
    )
    assert response.raw_json is not None
    return response.raw_json


def _profile() -> DataProfile:
    return DataProfile.model_validate({
        "schemaVersion": "0.1", "profileId": "profile_structure", "datasetId": "dataset_structure", "version": "1",
        "datasetType": "structure_collection", "files": [{"path": "si.cif", "format": "cif", "sizeBytes": 512}],
        "objects": [{"objectType": "Structure", "count": 1, "source": "si.cif"}],
        "structureSummary": {"nStructures": 1, "elements": ["Si"], "formulaStats": {"total": 1, "uniqueCount": 1}},
        "qualityIssues": [], "recommendedTasks": [], "createdAt": "2026-07-12T00:00:00+00:00",
    })


def _structure() -> Structure:
    return Structure(Lattice.cubic(5.43), ["Si", "Si"], [[0, 0, 0], [0.25, 0.25, 0.25]])


def _read(root: Path, artifacts: list, name: str) -> dict:
    artifact = next(item for item in artifacts if item.name == name)
    return json.loads((root / artifact.storageKey).read_text(encoding="utf-8"))
