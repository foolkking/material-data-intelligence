from __future__ import annotations

import json

from mdi_adapters import PTableHeatmapAdapter, ToolExecutionContext
from mdi_artifact_core import LocalArtifactExporter
from mdi_schemas import ArtifactType, ToolExecutionRequest
from mdi_tool_registry import load_manifests


def test_artifact_paths_metadata_and_recipe_are_stable(tmp_path):
    tool = load_manifests().get_tool_by_id("composition.ptable_heatmap")
    context = ToolExecutionContext(
        job_id="job_artifact",
        project_id="project_artifact",
        dataset_id="dataset_artifact",
        tool_id=tool.toolId,
        tool_version=tool.version,
        adapter_version="0.1.0",
        registry_version="0.1.0",
        artifact_root=tmp_path,
        tool_call_id="call_artifact",
        object_store={"formulas": ["Fe2O3", "LiFePO4"]},
        resource_limits=tool.resourceLimits,
    )
    request = ToolExecutionRequest(
        jobId="job_artifact",
        stepId="step_artifact",
        toolId=tool.toolId,
        inputRefs=[{"refType": "normalized_object", "ref": "formulas", "objectType": "Composition"}],
        params={"normalize": True},
        artifactTypes=["plotly_json", "summary_md", "recipe_json"],
    )

    artifacts = PTableHeatmapAdapter().execute(context, request)
    storage_keys = {artifact.type: artifact.storageKey for artifact in artifacts}

    assert storage_keys[ArtifactType.plotly_json] == (
        "projects/project_artifact/jobs/job_artifact/tool_calls/call_artifact/ptable_heatmap.json"
    )
    assert storage_keys[ArtifactType.recipe_json] == (
        "projects/project_artifact/jobs/job_artifact/tool_calls/call_artifact/recipe.json"
    )
    for artifact in artifacts:
        assert artifact.metadata.toolId == "composition.ptable_heatmap"
        assert artifact.metadata.toolVersion == "0.1.0"
        assert artifact.metadata.inputHashes
        assert artifact.metadata.paramsHash
        assert artifact.sizeBytes > 0

    recipe_path = tmp_path / storage_keys[ArtifactType.recipe_json]
    recipe = json.loads(recipe_path.read_text(encoding="utf-8"))
    assert recipe["schemaVersion"] == "0.1"
    assert recipe["steps"][0]["toolId"] == "composition.ptable_heatmap"


def test_normalized_object_storage_is_stable(tmp_path, repo_root):
    from mdi_material_parsers import parse_file

    result = parse_file(
        repo_root / "tests" / "fixtures" / "structures" / "si.cif",
        dataset_id="dataset_norm",
        file_id="file_norm",
    )
    draft = result.objects[0]

    exported = LocalArtifactExporter(tmp_path).export_normalized_object(
        object_id=draft.id,
        storage_key=draft.storage_key,
        payload=draft.payload,
        metadata=draft.metadata,
        project_id="project_norm",
        dataset_id="dataset_norm",
        provenance={"detectedFormat": "cif"},
    )

    assert exported.storage_key == (
        f"projects/project_norm/datasets/dataset_norm/{draft.storage_key}"
    )
    assert exported.metadata_key.endswith("/metadata.json")
    assert (tmp_path / exported.storage_key).exists()
    assert (tmp_path / exported.metadata_key).exists()
