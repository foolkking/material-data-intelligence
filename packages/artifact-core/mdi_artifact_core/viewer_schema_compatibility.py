from __future__ import annotations

from copy import deepcopy
from typing import Any

from .viewer_scene_contract import validate_viewer_scene, validate_viewer_scene_manifest


VIEWER_SCHEMA_COMPATIBILITY: dict[str, dict[str, Any]] = {
    "phase10d1.viewer_scene.v1": {
        "kind": "scene",
        "status": "deprecated_read_only",
        "preview_mode": "json_only",
        "preview_supported": True,
        "renderer_supported": False,
        "periodic_topology_supported": False,
        "migration_target": None,
        "migration_policy": "regenerate_from_source_only",
        "warnings": ["VIEWER_SCENE_LEGACY_PHASE10D_SCHEMA"],
        "producer_status": "deprecated_direct_compatibility_only",
        "new_artifact_generation_allowed": False,
    },
    "phase10f8.viewer_scene.v1": {
        "kind": "scene",
        "status": "supported_legacy_same_cell",
        "preview_mode": "json_or_renderer",
        "preview_supported": True,
        "renderer_supported": True,
        "periodic_topology_supported": False,
        "migration_target": None,
        "migration_policy": "regenerate_from_source_only",
        "warnings": ["VIEWER_SCENE_LEGACY_SAME_CELL_TOPOLOGY"],
        "producer_status": "fixtures_and_compatibility_only",
        "new_artifact_generation_allowed": False,
    },
    "phase10f18.viewer_scene.v2": {
        "kind": "scene",
        "status": "current",
        "preview_mode": "json_or_renderer",
        "preview_supported": True,
        "renderer_supported": True,
        "periodic_topology_supported": True,
        "migration_target": None,
        "migration_policy": "not_required",
        "warnings": [],
        "producer_status": "current_default",
        "new_artifact_generation_allowed": True,
    },
}

VIEWER_MANIFEST_COMPATIBILITY: dict[str, dict[str, Any]] = {
    "phase10d1.viewer_assets_manifest.v1": {
        "kind": "manifest",
        "status": "deprecated_read_only",
        "preview_mode": "json_only",
        "renderer_included": False,
        "periodic_topology_supported": False,
        "warnings": ["VIEWER_MANIFEST_LEGACY_PHASE10D_SCHEMA"],
        "paired_scene_schema": "phase10d1.viewer_scene.v1",
    },
    "phase10f9.viewer_scene_manifest.v1": {
        "kind": "manifest",
        "status": "supported_legacy",
        "preview_mode": "json_only",
        "renderer_included": False,
        "periodic_topology_supported": False,
        "warnings": ["VIEWER_MANIFEST_LEGACY_V1_SCHEMA"],
        "paired_scene_schema": "phase10f8.viewer_scene.v1",
    },
    "phase10f19.viewer_assets_manifest.v2": {
        "kind": "manifest",
        "status": "current",
        "preview_mode": "json_only",
        "renderer_included": False,
        "periodic_topology_supported": True,
        "warnings": [],
        "paired_scene_schema": "phase10f18.viewer_scene.v2",
    },
}


def viewer_schema_compatibility_result(payload: Any) -> dict[str, Any]:
    schema = payload.get("schema_version") if isinstance(payload, dict) else None
    policy = VIEWER_SCHEMA_COMPATIBILITY.get(str(schema))
    if policy is None:
        return {
            "schema_version": str(schema or "unknown"),
            "status": "unsupported",
            "preview_supported": False,
            "renderer_supported": False,
            "periodic_topology_supported": False,
            "migration_policy": "unsupported",
            "warnings": ["VIEWER_SCENE_SCHEMA_UNSUPPORTED"],
            "valid": False,
            "errors": ["VIEWER_SCENE_SCHEMA_UNSUPPORTED"],
        }
    errors = _validate_phase10d_scene(payload) if schema == "phase10d1.viewer_scene.v1" else validate_viewer_scene(payload).errors
    return {
        "schema_version": schema,
        "status": policy["status"],
        "preview_supported": policy["preview_supported"],
        "renderer_supported": policy["renderer_supported"],
        "periodic_topology_supported": policy["periodic_topology_supported"],
        "migration_policy": policy["migration_policy"],
        "warnings": list(policy["warnings"]),
        "valid": not errors,
        "errors": sorted(set(errors)),
    }


def viewer_manifest_compatibility_result(payload: Any, *, scene_schema: str | None = None) -> dict[str, Any]:
    schema = payload.get("schema_version") if isinstance(payload, dict) else None
    policy = VIEWER_MANIFEST_COMPATIBILITY.get(str(schema))
    if policy is None:
        return {"schema_version": str(schema or "unknown"), "status": "unsupported", "valid": False, "warnings": ["VIEWER_MANIFEST_SCHEMA_UNSUPPORTED"], "errors": ["VIEWER_MANIFEST_SCHEMA_UNSUPPORTED"]}
    errors = _validate_phase10d_manifest(payload) if schema == "phase10d1.viewer_assets_manifest.v1" else validate_viewer_scene_manifest(payload).errors
    if scene_schema is not None and scene_schema != policy["paired_scene_schema"]:
        errors = [*errors, "VIEWER_MANIFEST_SCENE_SCHEMA_MISMATCH"]
    return {
        "schema_version": schema,
        "status": policy["status"],
        "preview_mode": policy["preview_mode"],
        "renderer_included": policy["renderer_included"],
        "periodic_topology_supported": policy["periodic_topology_supported"],
        "paired_scene_schema": policy["paired_scene_schema"],
        "warnings": list(policy["warnings"]),
        "valid": not errors,
        "errors": sorted(set(errors)),
    }


def compatibility_matrix_snapshot() -> dict[str, Any]:
    return {"scenes": deepcopy(VIEWER_SCHEMA_COMPATIBILITY), "manifests": deepcopy(VIEWER_MANIFEST_COMPATIBILITY)}


def _validate_phase10d_scene(payload: Any) -> list[str]:
    errors: list[str] = []
    if not isinstance(payload, dict) or payload.get("schema_version") != "phase10d1.viewer_scene.v1":
        return ["VIEWER_SCENE_LEGACY_SHAPE_INVALID"]
    if payload.get("artifactType") != "structure.viewer_scene_metadata":
        errors.append("VIEWER_SCENE_LEGACY_KIND_INVALID")
    if not isinstance(payload.get("structure"), dict) or not isinstance(payload.get("security"), dict):
        errors.append("VIEWER_SCENE_LEGACY_SHAPE_INVALID")
    security = payload.get("security") or {}
    if security.get("contains_javascript") is not False or security.get("external_urls") != []:
        errors.append("VIEWER_SCENE_LEGACY_SECURITY_INVALID")
    if _contains_executable_content(payload):
        errors.append("VIEWER_SCENE_LEGACY_EXECUTABLE_CONTENT")
    return errors


def _validate_phase10d_manifest(payload: Any) -> list[str]:
    errors: list[str] = []
    if not isinstance(payload, dict) or payload.get("schema_version") != "phase10d1.viewer_assets_manifest.v1":
        return ["VIEWER_MANIFEST_LEGACY_SHAPE_INVALID"]
    if payload.get("artifactType") != "structure.viewer_export_package":
        errors.append("VIEWER_MANIFEST_LEGACY_KIND_INVALID")
    renderer = payload.get("renderer")
    security = payload.get("security")
    if not isinstance(renderer, dict) or renderer.get("included") is not False:
        errors.append("VIEWER_MANIFEST_LEGACY_RENDERER_INVALID")
    if not isinstance(security, dict) or security.get("contains_javascript") is not False or security.get("external_urls") != []:
        errors.append("VIEWER_MANIFEST_LEGACY_SECURITY_INVALID")
    if _contains_executable_content(payload):
        errors.append("VIEWER_MANIFEST_LEGACY_EXECUTABLE_CONTENT")
    return errors


def _contains_executable_content(value: Any) -> bool:
    if isinstance(value, dict):
        return any(str(key).lower() in {"callback", "script", "shader", "module", "html"} or _contains_executable_content(child) for key, child in value.items())
    if isinstance(value, list):
        return any(_contains_executable_content(child) for child in value)
    if isinstance(value, str):
        lowered = value.lower()
        return any(marker in lowered for marker in ("javascript:", "<script", "http://", "https://", "eval(", "function("))
    return False
