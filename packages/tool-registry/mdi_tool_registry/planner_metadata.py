from __future__ import annotations

from collections.abc import Iterable
from typing import Any

from mdi_schemas import (
    CapabilityNeed,
    DesiredOutput,
    PlannerAvailability,
    PlannerBindingSource,
    PlannerParameterBinding,
    PlannerRegistrySnapshot,
    RegistrySnapshotEntry,
    ScientificIntent,
    ToolPlannerMetadata,
    capability_semantic_hash,
    deterministic_capability_id,
)


PLANNER_METADATA_VERSION = "1.0"
PLANNER_HIDDEN_TOOL_IDS = frozenset(
    {
        "structure.viewer_scene_metadata",
        "structure.viewer_export_package",
        "structure.trajectory_import",
    }
)


def _intents(tool_id: str) -> list[ScientificIntent]:
    if tool_id == "structure.composition_from_structure":
        return [ScientificIntent.composition_analysis, ScientificIntent.structure_analysis]
    if tool_id == "dataset.materials_explorer":
        return [
            ScientificIntent.dataset_overview,
            ScientificIntent.composition_analysis,
            ScientificIntent.property_distribution,
            ScientificIntent.dataset_comparison,
            ScientificIntent.comparison,
            ScientificIntent.anomaly_candidate_review,
            ScientificIntent.sample_inspection,
        ]
    if tool_id == "dataset.composition_space" or tool_id.startswith("composition.cluster_"):
        return [
            ScientificIntent.composition_space,
            ScientificIntent.comparison,
            ScientificIntent.sample_inspection,
            ScientificIntent.visualization,
        ]
    exact = {
        "ml.regression_evaluation": ScientificIntent.ml_regression_evaluation,
        "ml.uncertainty_evaluation": ScientificIntent.ml_uncertainty_evaluation,
        "ml.classification_evaluation": ScientificIntent.ml_classification_evaluation,
    }
    if tool_id in exact:
        values = [exact[tool_id], ScientificIntent.sample_inspection, ScientificIntent.comparison, ScientificIntent.visualization]
        if tool_id == "ml.uncertainty_evaluation":
            values.insert(1, ScientificIntent.ml_regression_evaluation)
        return values
    low_level_ml = {
        "ml.basic_metrics": [ScientificIntent.comparison],
        "ml.density_scatter": [ScientificIntent.comparison, ScientificIntent.visualization],
        "ml.error_distribution": [
            ScientificIntent.property_distribution,
            ScientificIntent.anomaly_candidate_review,
            ScientificIntent.visualization,
        ],
        "ml.outlier_table": [ScientificIntent.sample_inspection, ScientificIntent.anomaly_candidate_review],
    }
    if tool_id in low_level_ml:
        return low_level_ml[tool_id]
    if tool_id.startswith("ml."):
        return [ScientificIntent.ml_regression_evaluation, ScientificIntent.visualization]
    if tool_id.startswith("table."):
        return [ScientificIntent.dataset_overview, ScientificIntent.property_distribution]
    if tool_id.startswith("viz."):
        return [ScientificIntent.property_distribution, ScientificIntent.visualization]
    if tool_id.startswith("composition."):
        return [ScientificIntent.composition_analysis, ScientificIntent.visualization]
    if tool_id == "structure.brillouin_zone":
        return [ScientificIntent.reciprocal_space_analysis, ScientificIntent.visualization]
    if tool_id in {"structure.trajectory_viewer", "structure.trajectory_import", "trajectory.viewer"}:
        return [ScientificIntent.trajectory_analysis, ScientificIntent.visualization]
    if tool_id == "structure.volumetric_data":
        return [ScientificIntent.volumetric_analysis, ScientificIntent.visualization]
    if tool_id.startswith("phonon."):
        return [ScientificIntent.phonon_analysis, ScientificIntent.visualization]
    if tool_id.startswith("structure."):
        values = [ScientificIntent.structure_analysis]
        if tool_id in {
            "structure.structure_3d",
            "structure.viewer_scene",
            "structure.viewer_3d",
            "structure.coordination_hist",
            "structure.coordination_crystalnn",
            "structure.coordination_voronoinn",
            "structure.local_environment_polyhedra",
            "structure.experimental_xrd_comparison",
            "structure.xrd",
            "structure.rdf",
        }:
            values.append(ScientificIntent.visualization)
        return values
    raise ValueError(f"Planner metadata is not defined for tool: {tool_id}")


def _needs(tool_id: str) -> list[CapabilityNeed]:
    if tool_id == "dataset.composition_space" or tool_id.startswith("composition.cluster_"):
        return [CapabilityNeed.tabular_data, CapabilityNeed.composition_data]
    if tool_id == "dataset.materials_explorer":
        return [CapabilityNeed.tabular_data]
    if tool_id == "ml.regression_evaluation":
        return [CapabilityNeed.tabular_data, CapabilityNeed.regression_semantics]
    if tool_id == "ml.uncertainty_evaluation":
        return [CapabilityNeed.tabular_data, CapabilityNeed.regression_semantics, CapabilityNeed.uncertainty_semantics]
    if tool_id == "ml.classification_evaluation":
        return [CapabilityNeed.tabular_data, CapabilityNeed.classification_semantics]
    if tool_id.startswith("ml."):
        return [CapabilityNeed.tabular_data, CapabilityNeed.regression_semantics]
    if tool_id.startswith(("table.", "viz.")):
        return [CapabilityNeed.tabular_data]
    if tool_id.startswith("composition."):
        return [CapabilityNeed.composition_data]
    if tool_id == "structure.brillouin_zone":
        return [CapabilityNeed.structure_resource, CapabilityNeed.reciprocal_space_resource]
    if tool_id in {"structure.trajectory_viewer", "structure.trajectory_import", "trajectory.viewer"}:
        return [CapabilityNeed.trajectory_resource]
    if tool_id == "structure.volumetric_data":
        return [CapabilityNeed.volumetric_resource]
    if tool_id.startswith("phonon."):
        return [CapabilityNeed.phonon_resource]
    if tool_id == "structure.experimental_xrd_comparison":
        return [CapabilityNeed.structure_resource, CapabilityNeed.tabular_data]
    if tool_id.startswith("structure."):
        return [CapabilityNeed.structure_resource]
    raise ValueError(f"Planner capability needs are not defined for tool: {tool_id}")


def _supported_needs(tool_id: str) -> list[CapabilityNeed]:
    values = set(_needs(tool_id))
    if tool_id == "structure.composition_from_structure":
        values.add(CapabilityNeed.composition_data)
    if tool_id in {"dataset.materials_explorer", "dataset.composition_space"}:
        values.update({CapabilityNeed.composition_data, CapabilityNeed.material_property_data, CapabilityNeed.comparison_groups, CapabilityNeed.sample_identity})
    if tool_id == "ml.regression_evaluation":
        values.update({CapabilityNeed.material_property_data, CapabilityNeed.sample_identity, CapabilityNeed.composition_data, CapabilityNeed.comparison_groups})
    if tool_id == "ml.uncertainty_evaluation":
        values.update({CapabilityNeed.material_property_data, CapabilityNeed.sample_identity})
    if tool_id == "ml.classification_evaluation":
        values.update({CapabilityNeed.sample_identity})
    if tool_id.startswith(("table.", "viz.")):
        values.add(CapabilityNeed.material_property_data)
    return sorted(values, key=lambda item: item.value)


def _desired_outputs(tool: Any) -> list[DesiredOutput]:
    artifacts = {item.value for item in tool.artifactTypes}
    outputs: set[DesiredOutput] = {DesiredOutput.downloadable_artifact}
    if artifacts & {"summary_md", "phonon_summary_json", "trajectory_summary_json"}:
        outputs.update({DesiredOutput.summary, DesiredOutput.warnings})
    if artifacts & {"metrics_json"}:
        outputs.add(DesiredOutput.metrics)
    if artifacts & {"table_json", "table_csv", "quality_issues_json"}:
        outputs.add(DesiredOutput.table)
    if artifacts & {"plotly_json", "plotly_html", "preview_png", "matterviz_html"}:
        outputs.add(DesiredOutput.plot)
    if "recipe_json" in artifacts:
        outputs.add(DesiredOutput.recipe)
    if "report_md" in artifacts or "report_html" in artifacts:
        outputs.add(DesiredOutput.report)
    if tool.toolId in {
        "structure.structure_3d", "structure.viewer_scene", "structure.viewer_3d",
        "structure.trajectory_viewer", "structure.volumetric_data", "phonon.animation",
        "structure.brillouin_zone",
    }:
        outputs.update({DesiredOutput.three_dimensional_view, DesiredOutput.plot})
    if tool.toolId == "dataset.materials_explorer":
        outputs.update({DesiredOutput.comparison, DesiredOutput.linked_samples, DesiredOutput.warnings})
    if tool.toolId == "dataset.composition_space":
        outputs.update({DesiredOutput.comparison, DesiredOutput.linked_samples, DesiredOutput.plot})
    if tool.toolId in {"ml.regression_evaluation", "ml.uncertainty_evaluation", "ml.classification_evaluation"}:
        outputs.update({DesiredOutput.metrics, DesiredOutput.linked_samples, DesiredOutput.table})
    if tool.toolId == "ml.error_distribution":
        outputs.update({DesiredOutput.metrics, DesiredOutput.plot, DesiredOutput.table})
    if tool.toolId == "ml.outlier_table":
        outputs.update({DesiredOutput.linked_samples, DesiredOutput.table})
    return sorted(outputs, key=lambda item: item.value)


def _bindings(tool_id: str) -> list[PlannerParameterBinding]:
    if tool_id in {"dataset.materials_explorer", "dataset.composition_space"}:
        return [PlannerParameterBinding(parameter="tableObjectId", source=PlannerBindingSource.resource_id)]
    if tool_id in {"ml.regression_evaluation", "ml.uncertainty_evaluation", "ml.classification_evaluation"}:
        return [PlannerParameterBinding(parameter="groupIds", source=PlannerBindingSource.target_group_ids)]
    if tool_id in {"ml.basic_metrics", "ml.density_scatter", "ml.outlier_table", "ml.error_distribution"}:
        return [
            PlannerParameterBinding(parameter="targetColumn", source=PlannerBindingSource.target_column, targetRoles=["regression_target"]),
            PlannerParameterBinding(parameter="predictionColumn", source=PlannerBindingSource.target_column, targetRoles=["regression_prediction"]),
        ]
    if tool_id == "viz.histogram":
        return [PlannerParameterBinding(parameter="column", source=PlannerBindingSource.target_column, targetRoles=["material_property"], required=True)]
    if tool_id == "table.numeric_summary" or tool_id == "table.distribution_summary" or tool_id == "viz.correlation":
        return [PlannerParameterBinding(parameter="numericColumns", source=PlannerBindingSource.semantic_columns, targetRoles=["material_property"], required=True, multiple=True)]
    if tool_id == "viz.scatter":
        return [
            PlannerParameterBinding(parameter="xColumn", source=PlannerBindingSource.target_column, targetRoles=["regression_target", "material_property"]),
            PlannerParameterBinding(parameter="yColumn", source=PlannerBindingSource.target_column, targetRoles=["regression_prediction", "material_property"]),
        ]
    if tool_id == "phonon.animation":
        return [PlannerParameterBinding(parameter="mode_id", source=PlannerBindingSource.resource_fact, objectTypes=["PhononEigenvector"], factKeys=["modeId"])]
    if tool_id in {
        "composition.formula_statistics",
        "composition.ptable_heatmap",
        "composition.elements_hist",
        "composition.chem_sys_treemap",
        "composition.chem_sys_sunburst",
        "composition.summary",
    }:
        return [
            PlannerParameterBinding(
                parameter="formulaColumn",
                source=PlannerBindingSource.semantic_columns,
                targetRoles=["material_formula"],
                required=False,
            )
        ]
    return []


def _input_type_options(tool: Any) -> list[list[str]]:
    raw_options = [
        sorted({item.value for item in option.requiredObjectTypes})
        for option in tool.inputSchema.inputOptions
    ]
    # The historical composition schema encodes alternatives in one list while
    # phonon band/DOS and animation encode required co-inputs in one list.
    if tool.toolId.startswith("composition."):
        return [[item] for item in raw_options[0]] if raw_options else [["RawUnsupported"]]
    return raw_options or [["RawUnsupported"]]


def _required_roles(tool_id: str) -> list[str]:
    if tool_id in {"ml.regression_evaluation", "ml.basic_metrics", "ml.density_scatter", "ml.outlier_table", "ml.error_distribution"}:
        return ["regression_target", "regression_prediction"]
    if tool_id == "ml.uncertainty_evaluation":
        return ["regression_target", "regression_prediction", "regression_uncertainty"]
    if tool_id == "ml.classification_evaluation":
        return ["classification_target", "classification_prediction"]
    return []


def build_tool_planner_metadata(tool: Any) -> ToolPlannerMetadata:
    input_options = _input_type_options(tool)
    object_types = sorted({item for option in input_options for item in option})
    availability = (
        PlannerAvailability.deployment_unavailable
        if tool.toolId in PLANNER_HIDDEN_TOOL_IDS
        else PlannerAvailability.available
    )
    if tool.stage != "mvp":
        availability = PlannerAvailability.future
    cardinalities = [len(option) for option in input_options] or [1]
    return ToolPlannerMetadata(
        toolId=tool.toolId,
        toolName=tool.name,
        toolVersion=tool.version,
        availability=availability,
        scientificIntents=_intents(tool.toolId),
        capabilityNeeds=_supported_needs(tool.toolId),
        desiredOutputs=_desired_outputs(tool),
        acceptedObjectTypes=object_types or ["RawUnsupported"],
        inputObjectTypeOptions=input_options or [["RawUnsupported"]],
        requiredProfileCapabilities=[need.value for need in _needs(tool.toolId)],
        requiredTargetRoles=_required_roles(tool.toolId),
        minInputs=min(cardinalities),
        maxInputs=max(cardinalities),
        minTargets=len(_required_roles(tool.toolId)),
        maxTargets=32,
        parameterBindings=_bindings(tool.toolId),
        declaredArtifactTypes=[item.value for item in tool.artifactTypes],
        costClass=1 if tool.toolId == "structure.summary" else {"low": 1, "medium": 2, "high": 3}[tool.costLevel],
        independentComposable=availability is PlannerAvailability.available,
        collisionGroup="primary_interactive_structure_view" if tool.toolId in {"structure.structure_3d", "structure.viewer_scene", "structure.viewer_3d"} else None,
    )


def validate_tool_planner_metadata(tool: Any, metadata: ToolPlannerMetadata) -> None:
    if metadata.toolId != tool.toolId or metadata.toolVersion != tool.version:
        raise ValueError("Planner metadata tool identity does not match the Registry tool.")
    actual_options = _input_type_options(tool)
    actual_types = {item for option in actual_options for item in option}
    if not set(metadata.acceptedObjectTypes).issubset(actual_types or {"RawUnsupported"}):
        raise ValueError(f"Planner metadata inputs exceed the tool contract: {tool.toolId}")
    if metadata.inputObjectTypeOptions != actual_options:
        raise ValueError(f"Planner metadata input options do not match the tool contract: {tool.toolId}")
    actual_params = set((tool.paramsSchema.get("properties") or {}).keys())
    for binding in metadata.parameterBindings:
        if binding.parameter not in actual_params:
            raise ValueError(f"Planner binding references an unknown parameter for {tool.toolId}: {binding.parameter}")
    actual_artifacts = [item.value for item in tool.artifactTypes]
    if metadata.declaredArtifactTypes != actual_artifacts:
        raise ValueError(f"Planner metadata artifacts do not match the tool contract: {tool.toolId}")
    if metadata.availability is PlannerAvailability.available:
        try:
            from mdi_adapters.registry import ADAPTER_CLASSES
        except Exception as exc:  # pragma: no cover - import configuration is tested at integration level
            raise ValueError("Planner metadata adapter registry is unavailable.") from exc
        if tool.adapter not in ADAPTER_CLASSES:
            raise ValueError(f"Selectable planner tool is not invocable: {tool.toolId}")


def build_registry_snapshot(registry: Any) -> tuple[PlannerRegistrySnapshot, dict[str, ToolPlannerMetadata]]:
    if len(registry.tools) > 64:
        raise ValueError("Registry exceeds the capability-planning candidate cap.")
    metadata_by_id: dict[str, ToolPlannerMetadata] = {}
    entries: list[RegistrySnapshotEntry] = []
    for tool in sorted(registry.tools, key=lambda item: (item.toolId, item.version)):
        metadata = build_tool_planner_metadata(tool)
        validate_tool_planner_metadata(tool, metadata)
        if metadata.toolId in metadata_by_id:
            raise ValueError(f"Duplicate planner metadata identity: {metadata.toolId}")
        metadata_by_id[metadata.toolId] = metadata
        entries.append(
            RegistrySnapshotEntry(
                toolId=metadata.toolId,
                toolVersion=metadata.toolVersion,
                metadataHash=capability_semantic_hash(metadata, identity_fields=()),
            )
        )
    draft = {"schemaVersion": PLANNER_METADATA_VERSION, "registryVersion": registry.version, "tools": [item.model_dump(mode="json") for item in entries]}
    snapshot_hash = capability_semantic_hash(draft, identity_fields=())
    snapshot = PlannerRegistrySnapshot(
        snapshotId=deterministic_capability_id("registry", snapshot_hash),
        snapshotHash=snapshot_hash,
        registryVersion=registry.version,
        tools=entries,
    )
    return snapshot, metadata_by_id


def planner_visible_tools(registry: Any) -> list[Any]:
    _snapshot, metadata = build_registry_snapshot(registry)
    return [
        tool for tool in sorted(registry.tools, key=lambda item: item.toolId)
        if metadata[tool.toolId].availability is PlannerAvailability.available
    ]


__all__ = [
    "PLANNER_HIDDEN_TOOL_IDS", "PLANNER_METADATA_VERSION", "build_registry_snapshot",
    "build_tool_planner_metadata", "planner_visible_tools", "validate_tool_planner_metadata",
]
