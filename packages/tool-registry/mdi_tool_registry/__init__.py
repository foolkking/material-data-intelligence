"""Manifest-backed Tool Registry."""

from .loader import (
    ManifestValidationError,
    ToolRegistry,
    getToolById,
    get_tool_by_id,
    listMvpTools,
    listTools,
    listToolsByDomain,
    listToolsByStage,
    list_mvp_tools,
    list_tools,
    list_tools_by_domain,
    list_tools_by_stage,
    loadManifests,
    load_manifests,
    validateManifest,
    validate_manifest,
)
from .planner_metadata import (
    PLANNER_HIDDEN_TOOL_IDS,
    PLANNER_METADATA_VERSION,
    build_registry_snapshot,
    build_tool_planner_metadata,
    planner_visible_tools,
    validate_tool_planner_metadata,
)
from .dependency_ports import (
    build_artifact_compatibility_matrix,
    build_artifact_port_inventory,
    build_tool_artifact_port_metadata,
    validate_tool_artifact_port_metadata,
)
from .dependency_validator import DependencyValidationResult, validate_dependency_plan

__all__ = [
    "ManifestValidationError",
    "DependencyValidationResult",
    "PLANNER_HIDDEN_TOOL_IDS",
    "PLANNER_METADATA_VERSION",
    "ToolRegistry",
    "getToolById",
    "get_tool_by_id",
    "build_registry_snapshot",
    "build_artifact_compatibility_matrix",
    "build_artifact_port_inventory",
    "build_tool_artifact_port_metadata",
    "build_tool_planner_metadata",
    "listMvpTools",
    "listTools",
    "listToolsByDomain",
    "listToolsByStage",
    "list_mvp_tools",
    "list_tools",
    "list_tools_by_domain",
    "list_tools_by_stage",
    "loadManifests",
    "load_manifests",
    "planner_visible_tools",
    "validateManifest",
    "validate_manifest",
    "validate_tool_planner_metadata",
    "validate_tool_artifact_port_metadata",
    "validate_dependency_plan",
]

