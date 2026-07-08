from __future__ import annotations

import json
import tempfile
from pathlib import Path
from typing import Any

import pytest
from pymatgen.core import Lattice, Structure

from mdi_adapters import StructureViewerExportPackageAdapter, StructureViewerSceneMetadataAdapter
from mdi_adapters.context import ToolExecutionContext
from mdi_api.repositories import InMemoryRepositoryBundle
from mdi_api.routers.planner import PlannerJobsRequest, planner_jobs
from mdi_llm import MockLLMProvider, PlannerRequest
from mdi_schemas import AnalysisPlan, ArtifactType, DataProfile
from mdi_tool_registry import load_manifests
from mdi_workers import QueueWorkerRuntime


def test_viewer_scene_metadata_generates_static_scene_summary_and_recipe() -> None:
    artifacts = _execute_adapter(
        StructureViewerSceneMetadataAdapter(),
        "structure.viewer_scene_metadata",
        object_store={"structures": [_bonded_si_structure()]},
        params={"inferBonds": True, "maxSites": 500, "maxBonds": 2000},
        artifact_types=[ArtifactType.structure_json, ArtifactType.summary_md, ArtifactType.recipe_json],
    )

    payload = _artifact_payload(artifacts, "viewer_scene.json")
    summary = _artifact_text(artifacts, "summary.md")
    recipe = _artifact_payload(artifacts, "recipe.json")

    assert {artifact.name for artifact in artifacts["artifacts"]} == {"viewer_scene.json", "summary.md", "recipe.json"}
    assert payload["artifactType"] == "structure.viewer_scene_metadata"
    assert payload["schema_version"] == "phase10d1.viewer_scene.v1"
    assert payload["scene_type"] == "structure_viewer_scene"
    assert payload["structure"]["formula"] == "Si"
    assert payload["structure"]["site_count"] == 2
    assert payload["structure"]["lattice"]["units"] == "angstrom"
    assert payload["atoms"][0]["element"] == "Si"
    assert payload["bonds"][0]["policy"] == "covalent_radius_sum_with_tolerance"
    assert payload["display"]["representation"] == "ball_and_stick"
    assert payload["camera"]["projection"] == "perspective"
    assert payload["style"]["element_colors"]["Si"]
    assert payload["limits"]["truncated"] is False
    assert payload["security"] == {
        "contains_javascript": False,
        "external_urls": [],
        "external_urls_allowed": False,
        "artifact_supplied_js_allowed": False,
    }
    assert "no artifact JavaScript" in summary
    assert recipe["schema_version"] == "phase10d1.recipe.v1"
    assert recipe["deterministic"] is True
    assert recipe["dependencies"]["new_dependencies_added"] is False


def test_viewer_scene_metadata_can_skip_bonds_and_truncate_sites() -> None:
    artifacts = _execute_adapter(
        StructureViewerSceneMetadataAdapter(),
        "structure.viewer_scene_metadata",
        object_store={"structures": [_bonded_si_structure()]},
        params={"infer_bonds": False, "max_sites": 1, "max_bonds": 0},
        artifact_types=[ArtifactType.structure_json],
    )

    payload = _artifact_payload(artifacts, "viewer_scene.json")
    assert payload["bonds"] == []
    assert payload["limits"]["truncated"] is True
    assert any("BONDS_SKIPPED_NO_POLICY" in warning for warning in payload["warnings"])
    assert any("SITES_TRUNCATED" in warning for warning in payload["warnings"])


def test_viewer_export_package_generates_manifest_without_renderer_or_external_urls() -> None:
    artifacts = _execute_adapter(
        StructureViewerExportPackageAdapter(),
        "structure.viewer_export_package",
        object_store={"structures": [_bonded_si_structure()]},
        artifact_types=[ArtifactType.structure_json, ArtifactType.table_json, ArtifactType.summary_md, ArtifactType.recipe_json],
    )

    scene = _artifact_payload(artifacts, "viewer_scene.json")
    manifest = _artifact_payload(artifacts, "viewer_assets_manifest.json")
    artifact_text = "\n".join(
        (artifacts["root"] / artifact.storageKey).read_text(encoding="utf-8")
        for artifact in artifacts["artifacts"]
    )

    assert {artifact.name for artifact in artifacts["artifacts"]} == {
        "viewer_scene.json",
        "viewer_assets_manifest.json",
        "summary.md",
        "recipe.json",
    }
    assert scene["artifactType"] == "structure.viewer_scene_metadata"
    assert manifest["artifactType"] == "structure.viewer_export_package"
    assert manifest["schema_version"] == "phase10d1.viewer_assets_manifest.v1"
    assert manifest["renderer"]["included"] is False
    assert manifest["renderer"]["renderer_type"] == "none"
    assert manifest["security"]["contains_javascript"] is False
    assert manifest["security"]["external_urls"] == []
    assert manifest["security"]["external_urls_allowed"] is False
    assert manifest["security"]["artifact_supplied_js_allowed"] is False
    assert "viewer_scene.json" in [item["path"] for item in manifest["artifacts"]]
    assert "VIEWER_RENDERER_NOT_INCLUDED" in " ".join(manifest["warnings"])
    assert "<script" not in artifact_text.lower()
    assert "javascript:" not in artifact_text.lower()
    assert "http://" not in artifact_text.lower()
    assert "https://" not in artifact_text.lower()


def test_viewer_scene_tools_are_registered_with_strict_params() -> None:
    registry = load_manifests()
    scene_tool = registry.get_tool_by_id("structure.viewer_scene_metadata")
    package_tool = registry.get_tool_by_id("structure.viewer_export_package")

    assert scene_tool.domain == "structure"
    assert package_tool.domain == "structure"
    assert scene_tool.paramsSchema["additionalProperties"] is False
    assert package_tool.paramsSchema["additionalProperties"] is False
    assert "maxBonds" in scene_tool.paramsSchema["properties"]
    assert "maxPackageBytes" in package_tool.paramsSchema["properties"]
    assert scene_tool.outputSchema.primaryArtifactType == ArtifactType.structure_json
    assert package_tool.artifactTypes == [
        ArtifactType.structure_json,
        ArtifactType.table_json,
        ArtifactType.summary_md,
        ArtifactType.recipe_json,
    ]
    assert "interactive" not in scene_tool.description.lower()
    assert "renderer" in package_tool.description.lower()


@pytest.mark.parametrize(
    ("prompt", "expected_tool"),
    [
        ("Create viewer scene metadata for this CIF.", "structure.viewer_scene_metadata"),
        ("Build a static structure viewer scene contract.", "structure.viewer_scene_metadata"),
        ("Create a static viewer export package for this structure.", "structure.viewer_export_package"),
        ("Package this structure for future 3D viewer rendering.", "structure.viewer_export_package"),
    ],
)
def test_mock_planner_routes_phase10d1_prompts(prompt: str, expected_tool: str) -> None:
    plan = _mock_plan(prompt, _structure_profile())

    assert plan["steps"][0]["toolId"] == expected_tool


@pytest.mark.parametrize(
    "prompt",
    [
        "Open an interactive 3D viewer for this crystal.",
        "Render this crystal with WebGL.",
        "Generate Brillouin zone 3D.",
        "Compute XRD pattern.",
        "Compute RDF.",
        "Plot phonon bands.",
        "Plot phonon DOS.",
    ],
)
def test_mock_planner_keeps_deferred_prompts_out_of_phase10d1_tools(prompt: str) -> None:
    plan = _mock_plan(prompt, _structure_profile())

    assert plan["steps"][0]["toolId"] not in {
        "structure.viewer_scene_metadata",
        "structure.viewer_export_package",
        "structure.viewer_3d",
        "structure.brillouin_zone_3d",
        "structure.xrd",
        "structure.rdf",
        "phonon.bands",
        "phonon.dos",
    }


def test_persisted_viewer_export_package_plan_executes_exactly_one_tool_call(tmp_path: Path) -> None:
    repos = InMemoryRepositoryBundle.create()
    plan = _valid_viewer_plan("structure.viewer_export_package")
    provider = MockLLMProvider(fixed_plan=plan.model_dump(mode="json"))
    result = planner_jobs(
        PlannerJobsRequest(
            userPrompt="Create a static viewer export package for this structure.",
            projectId="project_10d1",
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
    worker_result = runtime.handle_job(result.job_id or "", object_store={"structures": [_bonded_si_structure()]})

    tool_calls = repos.tool_calls.list_for_job(result.job_id or "")
    artifacts = repos.artifacts.list_for_job(result.job_id or "")
    assert worker_result.status == "completed"
    assert worker_result.tool_call_count == 1
    assert tool_calls[0]["toolId"] == "structure.viewer_export_package"
    assert {artifact["name"] for artifact in artifacts} >= {
        "viewer_scene.json",
        "viewer_assets_manifest.json",
        "summary.md",
        "recipe.json",
    }


def _execute_adapter(
    adapter: Any,
    tool_id: str,
    *,
    object_store: dict[str, Any],
    params: dict[str, Any] | None = None,
    artifact_types: list[ArtifactType],
) -> dict[str, Any]:
    artifact_root = Path(tempfile.mkdtemp(prefix="mdi_phase10d1_artifacts_"))
    context = ToolExecutionContext(
        job_id="job_10d1",
        project_id="project_10d1",
        dataset_id="dataset_structure",
        tool_id=tool_id,
        tool_version="0.1.0",
        adapter_version="0.1.0",
        registry_version=load_manifests().version,
        artifact_root=artifact_root,
        object_store=object_store,
        resource_limits={"maxAtomsPerStructure": 1000, "maxStructures": 100, "maxSites": 500, "maxBonds": 2000},
    )
    request = {
        "jobId": "job_10d1",
        "stepId": "step_001",
        "toolId": tool_id,
        "inputRefs": [{"refType": "normalized_object", "ref": "structures", "objectType": "Structure"}],
        "params": params or {},
        "artifactTypes": [artifact_type.value for artifact_type in artifact_types],
    }
    return {"root": artifact_root, "artifacts": adapter.execute(context, request)}


def _artifact_payload(result: dict[str, Any], name: str) -> dict[str, Any]:
    artifact = next(item for item in result["artifacts"] if item.name == name)
    return json.loads((result["root"] / artifact.storageKey).read_text(encoding="utf-8"))


def _artifact_text(result: dict[str, Any], name: str) -> str:
    artifact = next(item for item in result["artifacts"] if item.name == name)
    return (result["root"] / artifact.storageKey).read_text(encoding="utf-8")


def _mock_plan(prompt: str, profile: DataProfile) -> dict[str, Any]:
    response = MockLLMProvider().generate_plan(
        PlannerRequest(
            user_prompt=prompt,
            dataset_id=profile.datasetId,
            profile_id=profile.profileId,
            tool_registry_version=load_manifests().version,
        ),
        tools=load_manifests().list_mvp_tools(),
        data_profile=profile,
    )
    assert response.raw_json is not None
    return response.raw_json


def _valid_viewer_plan(tool_id: str) -> AnalysisPlan:
    expected = [
        {"name": "viewer_scene.json", "type": "structure_json", "fromStepId": "step_001"},
        {"name": "summary.md", "type": "summary_md", "fromStepId": "step_001"},
        {"name": "recipe.json", "type": "recipe_json", "fromStepId": "step_001"},
    ]
    artifact_types = ["structure_json", "summary_md", "recipe_json"]
    if tool_id == "structure.viewer_export_package":
        expected.insert(1, {"name": "viewer_assets_manifest.json", "type": "table_json", "fromStepId": "step_001"})
        artifact_types.insert(1, "table_json")
    return AnalysisPlan.model_validate(
        {
            "schemaVersion": "0.1",
            "goal": "viewer metadata",
            "datasetId": "dataset_structure",
            "profileId": "profile_structure",
            "toolRegistryVersion": load_manifests().version,
            "assumptions": [],
            "warnings": [],
            "steps": [
                {
                    "stepId": "step_001",
                    "toolId": tool_id,
                    "purpose": "viewer metadata",
                    "reason": "test",
                    "inputRefs": [{"refType": "normalized_object", "ref": "structures", "objectType": "Structure"}],
                    "params": {"inferBonds": True, "maxSites": 500, "maxBonds": 2000},
                    "output": {"artifactTypes": artifact_types},
                }
            ],
            "expectedArtifacts": expected,
        }
    )


def _bonded_si_structure() -> Structure:
    return Structure(Lattice.cubic(4.0), ["Si", "Si"], [[0, 0, 0], [0.25, 0.25, 0.25]])


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
            "createdAt": "2026-07-07T00:00:00+00:00",
        }
    )
