from __future__ import annotations

import json
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Any


VIEWER_SCENE_KIND = "viewer_scene"
VIEWER_SCENE_VERSION = "viewer_scene.v1"
VIEWER_SCENE_SCHEMA_VERSION = "phase10f8.viewer_scene.v1"
VIEWER_SCENE_MANIFEST_SCHEMA_VERSION = "phase10f9.viewer_scene_manifest.v1"

DEFAULT_VIEWER_SCENE_CAPS: dict[str, Any] = {
    "max_sites": 256,
    "max_bonds": 2048,
    "max_species": 32,
    "max_cell_expansion": [1, 1, 1],
    "max_scene_json_bytes": 1_000_000,
}

REQUIRED_TOP_LEVEL_FIELDS = {
    "kind",
    "version",
    "schema_version",
    "source",
    "metadata",
    "scene",
    "validation",
    "caps",
    "warnings",
    "provenance",
    "security",
}

SECURITY_REQUIRED_FLAGS = {
    "contains_javascript": False,
    "external_urls_allowed": False,
    "artifact_supplied_js_allowed": False,
    "renderer_required": False,
    "remote_assets_allowed": False,
    "html_allowed": False,
}

EXECUTABLE_PLACEHOLDERS = {
    "EXTERNAL_RESOURCE_PLACEHOLDER_REJECTED_BY_CONTRACT": "VIEWER_SCENE_EXTERNAL_RESOURCE_REFERENCE",
    "EXECUTABLE_FIELD_PLACEHOLDER_REJECTED_BY_CONTRACT": "VIEWER_SCENE_EXECUTABLE_FIELD",
}

FORBIDDEN_STRING_MARKERS = (
    "http://",
    "https://",
    "javascript:",
    "<script",
    "</script",
    "eval(",
    "function(",
    "onload=",
    "onerror=",
)


@dataclass(frozen=True)
class ViewerSceneValidationResult:
    valid: bool
    errors: list[str]
    warnings: list[str]
    caps: dict[str, Any]

    def as_dict(self) -> dict[str, Any]:
        return {
            "valid": self.valid,
            "errors": self.errors,
            "warnings": self.warnings,
            "caps": self.caps,
        }


def load_viewer_scene_json(path: str | Path) -> dict[str, Any]:
    raw = Path(path).read_text(encoding="utf-8")
    return json.loads(raw, parse_constant=_reject_non_json_number)


def validate_viewer_scene(payload: dict[str, Any], *, raw_size_bytes: int | None = None) -> ViewerSceneValidationResult:
    errors: list[str] = []
    warnings: list[str] = []

    _require_top_level_fields(payload, errors)
    _validate_identity(payload, errors)
    _validate_security(payload.get("security"), errors)
    _scan_for_forbidden_content(payload, errors)

    caps = _effective_caps(payload.get("caps"))
    if raw_size_bytes is not None and raw_size_bytes > caps["max_scene_json_bytes"]:
        errors.append("VIEWER_SCENE_JSON_SIZE_LIMIT_EXCEEDED")

    scene = payload.get("scene")
    if not isinstance(scene, dict):
        errors.append("VIEWER_SCENE_SCENE_REQUIRED")
    else:
        _validate_scene(scene, caps, errors)

    for warning in _warning_codes(payload.get("warnings")):
        if warning not in warnings:
            warnings.append(warning)

    return ViewerSceneValidationResult(
        valid=not errors,
        errors=sorted(set(errors)),
        warnings=sorted(set(warnings)),
        caps=caps,
    )


def validate_viewer_scene_manifest(payload: dict[str, Any]) -> ViewerSceneValidationResult:
    errors: list[str] = []
    warnings = _warning_codes(payload.get("expected_warnings"))

    if payload.get("artifact_kind") != VIEWER_SCENE_KIND:
        errors.append("VIEWER_SCENE_MANIFEST_KIND_INVALID")
    if payload.get("artifact_version") != VIEWER_SCENE_VERSION:
        errors.append("VIEWER_SCENE_MANIFEST_VERSION_INVALID")
    if payload.get("schema_version") != VIEWER_SCENE_MANIFEST_SCHEMA_VERSION:
        errors.append("VIEWER_SCENE_MANIFEST_SCHEMA_VERSION_INVALID")
    if payload.get("preview_mode") != "json_only":
        errors.append("VIEWER_SCENE_MANIFEST_PREVIEW_MODE_INVALID")
    if payload.get("renderer_required") is not False:
        errors.append("VIEWER_SCENE_MANIFEST_RENDERER_REQUIRED")
    if payload.get("executable_assets") != "none":
        errors.append("VIEWER_SCENE_MANIFEST_EXECUTABLE_ASSETS_PRESENT")
    if payload.get("external_resources") != "none":
        errors.append("VIEWER_SCENE_MANIFEST_EXTERNAL_RESOURCES_PRESENT")
    if not isinstance(payload.get("expected_errors"), list):
        errors.append("VIEWER_SCENE_MANIFEST_EXPECTED_ERRORS_INVALID")
    if not isinstance(payload.get("expected_caps"), dict):
        errors.append("VIEWER_SCENE_MANIFEST_EXPECTED_CAPS_INVALID")

    _scan_for_forbidden_content(payload, errors, allow_manifest_placeholders=True)
    return ViewerSceneValidationResult(
        valid=not errors,
        errors=sorted(set(errors)),
        warnings=sorted(set(warnings)),
        caps=dict(payload.get("expected_caps") or {}),
    )


def _reject_non_json_number(value: str) -> None:
    raise ValueError(f"Non-standard JSON number is not allowed: {value}")


def _require_top_level_fields(payload: dict[str, Any], errors: list[str]) -> None:
    missing = REQUIRED_TOP_LEVEL_FIELDS - set(payload)
    if missing:
        errors.append("VIEWER_SCENE_REQUIRED_FIELD_MISSING")


def _validate_identity(payload: dict[str, Any], errors: list[str]) -> None:
    if payload.get("kind") != VIEWER_SCENE_KIND:
        errors.append("VIEWER_SCENE_KIND_INVALID")
    if payload.get("version") != VIEWER_SCENE_VERSION:
        errors.append("VIEWER_SCENE_VERSION_INVALID")
    if payload.get("schema_version") != VIEWER_SCENE_SCHEMA_VERSION:
        errors.append("VIEWER_SCENE_SCHEMA_VERSION_INVALID")


def _validate_security(security: Any, errors: list[str]) -> None:
    if not isinstance(security, dict):
        errors.append("VIEWER_SCENE_SECURITY_REQUIRED")
        return
    for key, expected in SECURITY_REQUIRED_FLAGS.items():
        if security.get(key) is not expected:
            errors.append("VIEWER_SCENE_SECURITY_FLAG_INVALID")
    if security.get("external_urls") != []:
        errors.append("VIEWER_SCENE_EXTERNAL_URLS_NOT_EMPTY")


def _effective_caps(caps_payload: Any) -> dict[str, Any]:
    caps = dict(DEFAULT_VIEWER_SCENE_CAPS)
    if isinstance(caps_payload, dict):
        for key in ("max_sites", "max_bonds", "max_species", "max_scene_json_bytes"):
            value = caps_payload.get(key)
            if isinstance(value, int) and value > 0:
                caps[key] = min(value, DEFAULT_VIEWER_SCENE_CAPS[key])
        expansion = caps_payload.get("max_cell_expansion")
        if _is_cell_expansion(expansion):
            caps["max_cell_expansion"] = [
                min(int(expansion[index]), DEFAULT_VIEWER_SCENE_CAPS["max_cell_expansion"][index])
                for index in range(3)
            ]
    return caps


def _validate_scene(scene: dict[str, Any], caps: dict[str, Any], errors: list[str]) -> None:
    if scene.get("coordinate_basis") != "cartesian_angstrom":
        errors.append("VIEWER_SCENE_COORDINATE_BASIS_INVALID")

    sites = scene.get("sites")
    if not isinstance(sites, list) or not sites:
        errors.append("VIEWER_SCENE_SITES_REQUIRED")
        sites = []
    if len(sites) > caps["max_sites"]:
        errors.append("VIEWER_SCENE_SITE_LIMIT_EXCEEDED")

    site_indices: set[int] = set()
    species: set[str] = set()
    for site in sites:
        if not isinstance(site, dict):
            errors.append("VIEWER_SCENE_SITE_SHAPE_INVALID")
            continue
        if not isinstance(site.get("index"), int):
            errors.append("VIEWER_SCENE_SITE_INDEX_INVALID")
        else:
            site_indices.add(site["index"])
        element = site.get("element")
        if not isinstance(element, str) or not element:
            errors.append("VIEWER_SCENE_SITE_ELEMENT_INVALID")
        else:
            species.add(element)
        if not isinstance(site.get("label"), str) or not site["label"]:
            errors.append("VIEWER_SCENE_SITE_LABEL_INVALID")
        if not _is_finite_triplet(site.get("xyz")):
            errors.append("VIEWER_SCENE_COORDINATE_NON_FINITE")
        if "frac" in site and not _is_finite_triplet(site.get("frac")):
            errors.append("VIEWER_SCENE_FRACTIONAL_COORDINATE_NON_FINITE")

    if len(species) > caps["max_species"]:
        errors.append("VIEWER_SCENE_SPECIES_LIMIT_EXCEEDED")

    lattice = scene.get("lattice")
    if not isinstance(lattice, dict):
        errors.append("VIEWER_SCENE_LATTICE_REQUIRED")
    elif not _is_finite_matrix_3x3(lattice.get("vectors")):
        errors.append("VIEWER_SCENE_LATTICE_VECTOR_INVALID")

    bonds = scene.get("bonds", [])
    if bonds is None:
        bonds = []
    if not isinstance(bonds, list):
        errors.append("VIEWER_SCENE_BONDS_SHAPE_INVALID")
        bonds = []
    if len(bonds) > caps["max_bonds"]:
        errors.append("VIEWER_SCENE_BOND_LIMIT_EXCEEDED")
    for bond in bonds:
        if not isinstance(bond, dict):
            errors.append("VIEWER_SCENE_BOND_SHAPE_INVALID")
            continue
        if bond.get("from") not in site_indices or bond.get("to") not in site_indices:
            errors.append("VIEWER_SCENE_BOND_ENDPOINT_INVALID")
        if "distance" in bond and not _is_finite_number(bond.get("distance")):
            errors.append("VIEWER_SCENE_BOND_DISTANCE_INVALID")

    expansion = scene.get("cell_expansion", [1, 1, 1])
    if not _is_cell_expansion(expansion):
        errors.append("VIEWER_SCENE_CELL_EXPANSION_INVALID")
    else:
        for value, cap in zip(expansion, caps["max_cell_expansion"], strict=True):
            if value > cap:
                errors.append("VIEWER_SCENE_CELL_EXPANSION_LIMIT_EXCEEDED")


def _scan_for_forbidden_content(
    value: Any,
    errors: list[str],
    *,
    allow_manifest_placeholders: bool = False,
) -> None:
    if isinstance(value, dict):
        for key, child in value.items():
            lowered_key = str(key).lower()
            if key in {"invalid_external_resource_reference"}:
                errors.append("VIEWER_SCENE_EXTERNAL_RESOURCE_REFERENCE")
            if key in {"invalid_executable_field"}:
                errors.append("VIEWER_SCENE_EXECUTABLE_FIELD")
            if any(marker in lowered_key for marker in ("callback", "eval", "onload", "onerror", "onclick")):
                errors.append("VIEWER_SCENE_EXECUTABLE_FIELD")
            _scan_for_forbidden_content(child, errors, allow_manifest_placeholders=allow_manifest_placeholders)
    elif isinstance(value, list):
        for child in value:
            _scan_for_forbidden_content(child, errors, allow_manifest_placeholders=allow_manifest_placeholders)
    elif isinstance(value, str):
        lowered_value = value.lower()
        if any(marker in lowered_value for marker in FORBIDDEN_STRING_MARKERS):
            errors.append("VIEWER_SCENE_FORBIDDEN_STRING_CONTENT")
        placeholder_code = EXECUTABLE_PLACEHOLDERS.get(value)
        if placeholder_code and not allow_manifest_placeholders:
            errors.append(placeholder_code)


def _warning_codes(warnings_payload: Any) -> list[str]:
    if not isinstance(warnings_payload, list):
        return []
    codes: list[str] = []
    for warning in warnings_payload:
        if isinstance(warning, str) and warning:
            codes.append(warning.split(":", 1)[0])
        elif isinstance(warning, dict) and isinstance(warning.get("code"), str):
            codes.append(warning["code"])
    return codes


def _is_finite_triplet(value: Any) -> bool:
    return isinstance(value, list) and len(value) == 3 and all(_is_finite_number(item) for item in value)


def _is_finite_matrix_3x3(value: Any) -> bool:
    return isinstance(value, list) and len(value) == 3 and all(_is_finite_triplet(row) for row in value)


def _is_finite_number(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)


def _is_cell_expansion(value: Any) -> bool:
    return (
        isinstance(value, list)
        and len(value) == 3
        and all(isinstance(item, int) and not isinstance(item, bool) and item >= 1 for item in value)
    )
