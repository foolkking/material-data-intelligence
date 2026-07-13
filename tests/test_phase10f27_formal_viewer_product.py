from __future__ import annotations

import json
from pathlib import Path

from pymatgen.core import Lattice, Structure

from mdi_adapters import StructureViewer3DAdapter
from mdi_adapters.context import ToolExecutionContext
from mdi_api.routers.tools import list_mvp_tools
from mdi_artifact_core import validate_viewer_scene, validate_viewer_scene_manifest
from mdi_llm import MockLLMProvider, PlannerRequest
from mdi_schemas import AnalysisPlan, DataProfile, ToolExecutionRequest
from mdi_tool_registry import load_manifests
from mdi_tool_registry.plan_validator import validate_plan


PARAMS = {
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


def test_formal_viewer_is_owned_by_platform_registry_and_catalogued_once() -> None:
    registry = load_manifests()
    tools = registry.list_tools()
    viewer = registry.get_tool_by_id("structure.viewer_3d")

    assert sum(tool.toolId == "structure.viewer_3d" for tool in tools) == 1
    assert viewer.source["manifest"] == "platform_builtin_manifest.yaml"
    assert viewer.implementationSource.value == "platform_builtin"
    assert viewer.adapter == "StructureViewer3DAdapter"
    assert viewer.paramsSchema["additionalProperties"] is False
    assert viewer.resourceLimits == registry.get_tool_by_id("structure.viewer_scene").resourceLimits
    assert "scientific export" in viewer.description
    for unsupported in ("Trajectories", "phonons", "Brillouin", "volumetric", "editing"):
        assert unsupported.lower() in viewer.description.lower()

    api_viewer = next(tool for tool in list_mvp_tools()["tools"] if tool["toolId"] == "structure.viewer_3d")
    assert api_viewer["source"]["manifest"] == "platform_builtin_manifest.yaml"
    assert api_viewer["artifactTypes"] == ["structure_json", "table_json", "summary_md", "recipe_json"]


def test_natural_viewer_intent_routes_to_formal_tool_and_json_intent_stays_separate() -> None:
    assert _plan_for("Open an interactive 3D view of this CIF")["steps"][0]["toolId"] == "structure.viewer_3d"
    assert _plan_for("Render this crystal in the structure viewer")["steps"][0]["toolId"] == "structure.viewer_3d"
    assert _plan_for("Build inert viewer scene data")["steps"][0]["toolId"] == "structure.viewer_scene"
    for prompt in ("Animate this trajectory", "Show phonon animation", "Render the Brillouin zone", "Edit this structure"):
        assert _plan_for(prompt)["steps"][0]["toolId"] != "structure.viewer_3d"


def test_plan_validator_accepts_exact_contract_and_rejects_unknown_params() -> None:
    plan = _analysis_plan()
    assert validate_plan(plan.model_dump(mode="json"), registry=load_manifests()).ok
    invalid = plan.model_dump(mode="json")
    invalid["steps"][0]["params"]["renderer_module"] = "remote"
    result = validate_plan(invalid, registry=load_manifests())
    assert not result.ok
    assert any(error.code == "PARAMS_SCHEMA_INVALID" for error in result.errors)


def test_formal_adapter_emits_current_inert_scene_and_manifest(tmp_path: Path) -> None:
    registry = load_manifests()
    tool = registry.get_tool_by_id("structure.viewer_3d")
    context = ToolExecutionContext(
        job_id="job_10f27", project_id="project_10f27", dataset_id="dataset_structure",
        tool_id=tool.toolId, tool_version=tool.version, adapter_version="1.0.0",
        registry_version=registry.version, artifact_root=tmp_path, tool_call_id="call_10f27",
        object_store={"structures": [_structure()]}, resource_limits=tool.resourceLimits,
    )
    request = ToolExecutionRequest(
        jobId="job_10f27", stepId="step_001", toolId=tool.toolId,
        inputRefs=[{"refType": "normalized_object", "ref": "structures", "objectType": "Structure"}],
        params=PARAMS, artifactTypes=["structure_json", "table_json", "summary_md", "recipe_json"],
    )
    artifacts = StructureViewer3DAdapter().execute(context, request)
    payloads = {item.name: json.loads((tmp_path / item.storageKey).read_text(encoding="utf-8")) for item in artifacts if item.name.endswith(".json")}
    scene = payloads["viewer_scene.json"]
    manifest = payloads["viewer_scene_manifest.json"]
    assert scene["schema_version"] == "phase10f18.viewer_scene.v2"
    assert manifest["schema_version"] == "phase10f19.viewer_assets_manifest.v2"
    assert scene["provenance"]["tool_id"] == "structure.viewer_3d"
    assert manifest["tool_id"] == "structure.viewer_3d"
    assert manifest["capabilities"]["renderer_included"] is False
    assert validate_viewer_scene(scene).valid
    assert validate_viewer_scene_manifest(manifest).valid


def _plan_for(prompt: str) -> dict:
    registry = load_manifests()
    response = MockLLMProvider().generate_plan(
        PlannerRequest(user_prompt=prompt, dataset_id="dataset_structure", profile_id="profile_structure", tool_registry_version=registry.version),
        tools=registry.list_mvp_tools(), data_profile=_profile(),
    )
    assert response.raw_json is not None
    return response.raw_json


def _analysis_plan() -> AnalysisPlan:
    return AnalysisPlan.model_validate({
        "schemaVersion":"0.1", "goal":"Open structure viewer", "datasetId":"dataset_structure",
        "profileId":"profile_structure", "toolRegistryVersion":load_manifests().version,
        "assumptions":[], "warnings":[],
        "steps":[{"stepId":"step_001", "toolId":"structure.viewer_3d", "purpose":"Generate viewer artifacts.",
            "reason":"One periodic structure is available.",
            "inputRefs":[{"refType":"normalized_object", "ref":"structures", "objectType":"Structure"}],
            "params":PARAMS, "output":{"artifactTypes":["structure_json","table_json","summary_md","recipe_json"]}}],
        "expectedArtifacts":[
            {"name":"viewer_scene.json","type":"structure_json","fromStepId":"step_001"},
            {"name":"viewer_scene_manifest.json","type":"table_json","fromStepId":"step_001"},
            {"name":"summary.md","type":"summary_md","fromStepId":"step_001"},
            {"name":"recipe.json","type":"recipe_json","fromStepId":"step_001"}],
    })


def _profile() -> DataProfile:
    return DataProfile.model_validate({
        "schemaVersion":"0.1", "profileId":"profile_structure", "datasetId":"dataset_structure", "version":"1",
        "datasetType":"structure_collection", "files":[{"path":"si.cif","format":"cif","sizeBytes":512}],
        "objects":[{"objectType":"Structure","count":1,"source":"si.cif"}],
        "structureSummary":{"nStructures":1,"elements":["Si"],"formulaStats":{"total":1,"uniqueCount":1}},
        "qualityIssues":[],"recommendedTasks":[],"createdAt":"2026-07-13T00:00:00+00:00",
    })


def _structure() -> Structure:
    return Structure(Lattice.cubic(5.43), ["Si", "Si"], [[0,0,0], [0.25,0.25,0.25]])
