from __future__ import annotations

import json

from jsonschema import Draft202012Validator

from mdi_adapters import ADAPTER_CLASSES
from mdi_schemas import ArtifactType, DisplayTarget, ImplementationSource
from mdi_tool_registry import load_manifests


def as_json(model):
    if hasattr(model, "model_dump"):
        return model.model_dump(mode="json")
    return model.dict()


def test_loads_three_manifests_and_expected_tool_counts(repo_root):
    registry = load_manifests()
    tools = registry.list_tools()

    assert len([tool for tool in tools if tool.source.get("manifest") == "pymatviz_manifest.yaml"]) == 23
    assert len([tool for tool in tools if tool.source.get("manifest") == "matterviz_manifest.yaml"]) == 1
    assert len([tool for tool in tools if tool.source.get("manifest") == "platform_builtin_manifest.yaml"]) == 31
    assert len({tool.toolId for tool in tools}) == len(tools)


def test_manifest_values_match_shared_enums():
    registry = load_manifests()

    for tool in registry.list_tools():
        assert tool.stage in {"mvp", "v1", "v2"}
        assert tool.implementationSource in set(ImplementationSource)
        assert tool.outputSchema.displayTarget in set(DisplayTarget)
        assert all(artifact_type in set(ArtifactType) for artifact_type in tool.artifactTypes)
        assert tool.adapter.endswith("Adapter")


def test_registry_filters_and_lookup():
    registry = load_manifests()

    assert registry.get_tool_by_id("composition.ptable_heatmap").adapter == "PTableHeatmapAdapter"
    assert len(registry.list_tools_by_stage("mvp")) == 43
    assert {tool.toolId for tool in registry.list_tools_by_domain("dataset")} == {
        "dataset.composition_space",
        "dataset.materials_explorer",
    }
    assert {tool.toolId for tool in registry.list_tools_by_domain("structure")} >= {
        "structure.summary",
        "structure.lattice_summary",
        "structure.spacegroup_summary",
        "structure.composition_from_structure",
        "structure.preview_metadata",
        "structure.viewer_scene",
        "structure.viewer_scene_metadata",
        "structure.viewer_export_package",
        "structure.trajectory_import",
        "structure.xrd",
        "structure.rdf",
        "structure.structure_3d",
        "structure.viewer_3d",
        "structure.brillouin_zone",
    }
    assert {tool.toolId for tool in registry.list_mvp_tools()} >= {
        "composition.ptable_heatmap",
        "composition.elements_hist",
        "composition.chem_sys_treemap",
        "composition.chem_sys_sunburst",
        "composition.formula_statistics",
        "structure.structure_3d",
        "structure.viewer_3d",
        "structure.summary",
        "structure.lattice_summary",
        "structure.spacegroup_summary",
        "structure.composition_from_structure",
        "structure.preview_metadata",
        "structure.viewer_scene",
        "structure.viewer_scene_metadata",
        "structure.viewer_export_package",
        "structure.trajectory_import",
        "structure.xrd",
        "structure.rdf",
        "structure.brillouin_zone",
        "table.numeric_summary",
        "table.distribution_summary",
        "viz.scatter",
        "viz.histogram",
        "viz.correlation",
        "composition.summary",
    }
    assert {tool.toolId for tool in registry.list_tools_by_domain("viz")} >= {
        "viz.scatter",
        "viz.histogram",
        "viz.correlation",
    }


def test_mvp_adapter_classes_are_registered():
    registry = load_manifests()

    for tool in registry.list_mvp_tools():
        assert tool.adapter in ADAPTER_CLASSES


def test_mvp_tools_reject_unregistered_params():
    registry = load_manifests()

    for tool in registry.list_mvp_tools():
        assert tool.paramsSchema["additionalProperties"] is False
        validator = Draft202012Validator(tool.paramsSchema)
        errors = sorted(validator.iter_errors({"unknownParam": True}), key=lambda error: error.path)
        assert errors, tool.toolId
        assert "Additional properties are not allowed" in errors[0].message


def test_registered_tools_validate_against_json_schema(repo_root):
    schema_path = repo_root / "packages" / "schemas" / "json" / "registered-tool.schema.json"
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    validator = Draft202012Validator(schema)

    for tool in load_manifests().list_tools():
        errors = sorted(validator.iter_errors(as_json(tool)), key=lambda error: error.path)
        assert errors == []
