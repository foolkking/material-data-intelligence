from __future__ import annotations

import math
from dataclasses import dataclass
from fractions import Fraction
from typing import Any, Sequence

from .phonon_contract import stable_phonon_json
from .phonon_eigenvector_contract import (
    PhononEigenvectorContractError,
    eigenvector_content_hash,
    mass_unweighted_vectors,
    reconstruct_display_displacements,
    validate_phonon_eigenvector,
    validate_phonon_eigenvector_set,
)


PHONON_ANIMATION_SCHEMA_VERSION = "phase10h5.phonon_animation.v1"
PHONON_ANIMATION_SUMMARY_SCHEMA_VERSION = "phase10h5.phonon_animation_summary.v1"
PHONON_ANIMATION_MANIFEST_SCHEMA_VERSION = "phase10h5.phonon_animation_manifest.v1"
PHONON_ANIMATION_RECIPE_SCHEMA_VERSION = "phase10h5.phonon_animation_recipe.v1"
PHONON_ANIMATION_CAPS = {
    "max_atoms": 512,
    "max_displayed_atoms": 768,
    "max_supercell_axis": 3,
    "max_vectors": 768,
    "max_trail_points": 32,
    "max_artifact_bytes": 16_000_000,
}
_SECURITY = {
    "contains_html": False,
    "contains_javascript": False,
    "executable_content_allowed": False,
    "external_assets": [],
    "external_urls_allowed": False,
    "renderer_owned_by_application": True,
}
_PACKAGE_FIELDS = {
    "schema_version", "tool_id", "source", "structure", "band_binding",
    "eigenvector_binding", "mode", "supercell", "display", "playback",
    "limits", "warnings", "security", "provenance",
}


class PhononAnimationContractError(ValueError):
    def __init__(self, code: str, message: str):
        super().__init__(message)
        self.code = code


@dataclass(frozen=True)
class PhononAnimationValidationResult:
    valid: bool
    errors: tuple[str, ...]
    warnings: tuple[str, ...] = ()


def normalize_animation_params(params: dict[str, Any]) -> dict[str, Any]:
    allowed = {
        "mode_id", "display_scale", "initial_phase_radians",
        "playback_cycles_per_second", "autoplay", "loop", "supercell_mode",
        "supercell", "show_vectors", "show_trails", "trail_length",
        "show_bonds", "show_unit_cell", "show_axes", "representation",
    }
    if not isinstance(params, dict) or set(params) - allowed:
        raise PhononAnimationContractError("PHONON_ANIMATION_PARAM_INVALID", "Unknown animation parameters are not accepted.")
    mode_id = params.get("mode_id")
    if not isinstance(mode_id, str) or len(mode_id) != 64 or any(char not in "0123456789abcdef" for char in mode_id):
        raise PhononAnimationContractError("PHONON_ANIMATION_MODE_REQUIRED", "A canonical mode_id is required.")
    display_scale = _bounded_float(params.get("display_scale", 0.15), 0.01, 1.0)
    phase = _bounded_float(params.get("initial_phase_radians", 0.0), -1e6, 1e6) % (2.0 * math.pi)
    speed = _bounded_float(params.get("playback_cycles_per_second", 0.5), 0.05, 2.0)
    repeat = params.get("supercell", [1, 1, 1])
    if not _repeat(repeat):
        raise PhononAnimationContractError("PHONON_ANIMATION_SUPERCELL_INVALID", "supercell must contain three integers in [1, 3].")
    bool_fields = {
        "autoplay": False, "loop": True, "show_vectors": True,
        "show_trails": False, "show_bonds": True, "show_unit_cell": True,
        "show_axes": True,
    }
    normalized_bools: dict[str, bool] = {}
    for key, default in bool_fields.items():
        value = params.get(key, default)
        if not isinstance(value, bool):
            raise PhononAnimationContractError("PHONON_ANIMATION_PARAM_INVALID", f"{key} must be boolean.")
        normalized_bools[key] = value
    trail_length = params.get("trail_length", 12)
    if not isinstance(trail_length, int) or isinstance(trail_length, bool) or not 1 <= trail_length <= PHONON_ANIMATION_CAPS["max_trail_points"]:
        raise PhononAnimationContractError("PHONON_ANIMATION_PARAM_INVALID", "trail_length is outside the approved bound.")
    if params.get("supercell_mode", "auto") not in {"auto", "manual"} or params.get("representation", "ball_and_stick") != "ball_and_stick":
        raise PhononAnimationContractError("PHONON_ANIMATION_PARAM_INVALID", "The requested animation policy is unsupported.")
    return {
        "mode_id": mode_id,
        "display_scale": display_scale,
        "initial_phase_radians": phase,
        "playback_cycles_per_second": speed,
        "supercell_mode": params.get("supercell_mode", "auto"),
        "supercell": [int(value) for value in repeat],
        "trail_length": trail_length,
        "representation": "ball_and_stick",
        **normalized_bools,
    }


def commensurate_diagonal_supercell(qpoint: Sequence[float], requested: Sequence[int] | None = None) -> list[int]:
    if not _triplet(qpoint):
        raise PhononAnimationContractError("PHONON_ANIMATION_QPOINT_INVALID", "The q-point is invalid.")
    if requested is not None:
        if not _repeat(requested) or any(abs(float(qpoint[i]) * int(requested[i]) - round(float(qpoint[i]) * int(requested[i]))) > 1e-8 for i in range(3)):
            raise PhononAnimationContractError("PHONON_ANIMATION_NONCOMMENSURATE", "The requested supercell is not commensurate with the mode q-point.")
        return [int(value) for value in requested]
    result: list[int] = []
    for value in qpoint:
        fraction = Fraction(float(value)).limit_denominator(PHONON_ANIMATION_CAPS["max_supercell_axis"])
        if abs(float(fraction) - float(value)) > 1e-8:
            raise PhononAnimationContractError("PHONON_ANIMATION_NONCOMMENSURATE", "No bounded diagonal supercell represents this q-point.")
        result.append(fraction.denominator)
    return result


def build_phonon_animation(
    structure: dict[str, Any],
    band: dict[str, Any],
    eigenvector_set: dict[str, Any],
    params: dict[str, Any],
) -> dict[str, Any]:
    normalized = normalize_animation_params(params)
    validation = validate_phonon_eigenvector_set(eigenvector_set, band)
    if not validation.valid:
        raise PhononAnimationContractError(validation.errors[0], "The eigenvector set is incompatible with the band artifact.")
    validated_structure = _validate_structure(structure)
    if validated_structure["structure_identity"] != band.get("structure_identity") or validated_structure["structure_identity"] != eigenvector_set.get("structure_identity"):
        raise PhononAnimationContractError("PHONON_ANIMATION_STRUCTURE_MISMATCH", "Structure identities do not match.")
    modes = [item for item in eigenvector_set["modes"] if item["mode"]["mode_id"] == normalized["mode_id"]]
    if len(modes) != 1:
        raise PhononAnimationContractError("PHONON_ANIMATION_MODE_NOT_FOUND", "The selected canonical mode is unavailable.")
    eigenvector = modes[0]
    if eigenvector["atom_count"] != len(validated_structure["sites"]) or eigenvector["species"] != [site["species"] for site in validated_structure["sites"]]:
        raise PhononAnimationContractError("PHONON_ANIMATION_ATOM_ORDER_MISMATCH", "Structure atom ordering is incompatible with the eigenvector.")
    requested = normalized["supercell"] if normalized["supercell_mode"] == "manual" else None
    repeat = commensurate_diagonal_supercell(eigenvector["mode"]["qpoint_coordinates"], requested)
    displayed_atoms = len(validated_structure["sites"]) * math.prod(repeat)
    if displayed_atoms > PHONON_ANIMATION_CAPS["max_displayed_atoms"]:
        raise PhononAnimationContractError("PHONON_ANIMATION_CAP_EXCEEDED", "The derived animation exceeds the displayed-atom cap.")
    imaginary = bool(eigenvector["provenance"]["imaginary_mode"])
    warnings = []
    if imaginary:
        warnings.append("PHONON_ANIMATION_IMAGINARY_MODE_STATIC_DIRECTION")
    if eigenvector["mode"].get("degeneracy") is not None:
        warnings.append("PHONON_ANIMATION_DEGENERATE_BASIS_ARBITRARY")
    package = {
        "schema_version": PHONON_ANIMATION_SCHEMA_VERSION,
        "tool_id": "phonon.animation",
        "source": {"band_sha256": eigenvector_set["band_artifact"]["sha256"], "eigenvector_set_sha256": eigenvector_content_hash(eigenvector_set)},
        "structure": validated_structure,
        "band_binding": eigenvector_set["band_artifact"],
        "eigenvector_binding": {"schema_version": eigenvector_set["schema_version"], "sha256": eigenvector_content_hash(eigenvector_set)},
        "mode": eigenvector,
        "supercell": {"mode": normalized["supercell_mode"], "repeat": repeat, "displayed_atom_count": displayed_atoms, "commensurate": True, "renderer_local": True},
        "display": {key: normalized[key] for key in ("display_scale", "show_vectors", "show_trails", "trail_length", "show_bonds", "show_unit_cell", "show_axes", "representation")},
        "playback": {"initial_phase_radians": normalized["initial_phase_radians"], "cycles_per_second": normalized["playback_cycles_per_second"], "autoplay": normalized["autoplay"], "loop": normalized["loop"], "default_state": "paused", "reduced_motion_forces_paused": True},
        "limits": dict(PHONON_ANIMATION_CAPS),
        "warnings": warnings,
        "security": dict(_SECURITY),
        "provenance": {"deterministic": True, "frames_persisted": False, "display_only": True, "phonon_calculation_performed": False, "formula": "Re[(e_i/sqrt(m_i))*exp(i*(2*pi*q.R+phase))]"},
    }
    result = validate_phonon_animation(package)
    if not result.valid:
        raise PhononAnimationContractError(result.errors[0], "Generated animation package failed validation.")
    return package


def animation_displacements(package: dict[str, Any], phase_radians: float, cell_image: Sequence[int]) -> list[list[float]]:
    validation = validate_phonon_animation(package)
    if not validation.valid:
        raise PhononAnimationContractError(validation.errors[0], "Animation package is invalid.")
    if not _triplet(cell_image) or any(not isinstance(item, int) or isinstance(item, bool) for item in cell_image) or not _finite(phase_radians):
        raise PhononAnimationContractError("PHONON_DISPLACEMENT_REQUEST_INVALID", "Animation displacement inputs are invalid.")
    eigenvector = package["mode"]
    vectors = mass_unweighted_vectors(eigenvector)
    envelope = max((math.sqrt(sum(abs(component) ** 2 for component in vector)) for vector in vectors), default=0.0)
    if envelope <= 1e-12:
        raise PhononAnimationContractError("PHONON_DISPLACEMENT_DEGENERATE", "The mode displacement envelope is zero.")
    qpoint = eigenvector["mode"]["qpoint_coordinates"]
    spatial_phase = 2.0 * math.pi * sum(float(qpoint[index]) * int(cell_image[index]) for index in range(3))
    rotation = complex(math.cos(spatial_phase + float(phase_radians)), math.sin(spatial_phase + float(phase_radians)))
    scale = float(package["display"]["display_scale"]) / envelope
    return [[float((component * rotation).real * scale) for component in vector] for vector in vectors]


def validate_phonon_animation(value: Any) -> PhononAnimationValidationResult:
    errors: set[str] = set()
    if not isinstance(value, dict) or set(value) != _PACKAGE_FIELDS or value.get("schema_version") != PHONON_ANIMATION_SCHEMA_VERSION or value.get("tool_id") != "phonon.animation":
        return _result({"PHONON_ANIMATION_SCHEMA_UNSUPPORTED"})
    if value.get("security") != _SECURITY or value.get("limits") != PHONON_ANIMATION_CAPS:
        errors.add("PHONON_ANIMATION_SECURITY_INVALID")
    structure = value.get("structure")
    try:
        validated_structure = _validate_structure(structure)
    except PhononAnimationContractError as exc:
        errors.add(exc.code)
        validated_structure = None
    mode = value.get("mode") if isinstance(value.get("mode"), dict) else {}
    errors.update(validate_phonon_eigenvector(mode).errors)
    mode_ref = mode.get("mode") if isinstance(mode.get("mode"), dict) else {}
    if validated_structure and (mode.get("structure_identity") != validated_structure["structure_identity"] or mode.get("atom_count") != len(validated_structure["sites"])):
        errors.add("PHONON_ANIMATION_STRUCTURE_MISMATCH")
    supercell = value.get("supercell") if isinstance(value.get("supercell"), dict) else {}
    repeat = supercell.get("repeat")
    try:
        commensurate_diagonal_supercell(mode_ref.get("qpoint_coordinates", []), repeat)
    except PhononAnimationContractError as exc:
        errors.add(exc.code)
    expected_displayed = len(validated_structure["sites"]) * math.prod(repeat) if validated_structure and _repeat(repeat) else None
    if set(supercell) != {"mode", "repeat", "displayed_atom_count", "commensurate", "renderer_local"} or supercell.get("mode") not in {"auto", "manual"} or supercell.get("commensurate") is not True or supercell.get("renderer_local") is not True or supercell.get("displayed_atom_count") != expected_displayed:
        errors.add("PHONON_ANIMATION_SUPERCELL_INVALID")
    if validated_structure and _repeat(repeat) and len(validated_structure["sites"]) * math.prod(repeat) > PHONON_ANIMATION_CAPS["max_displayed_atoms"]:
        errors.add("PHONON_ANIMATION_CAP_EXCEEDED")
    playback = value.get("playback") if isinstance(value.get("playback"), dict) else {}
    if playback.get("autoplay") not in {True, False} or playback.get("default_state") != "paused" or playback.get("reduced_motion_forces_paused") is not True:
        errors.add("PHONON_ANIMATION_PLAYBACK_INVALID")
    serialized = stable_phonon_json(value)
    if len(serialized.encode("utf-8")) > PHONON_ANIMATION_CAPS["max_artifact_bytes"]:
        errors.add("PHONON_ANIMATION_CAP_EXCEEDED")
    _scan_inert(value, errors)
    return _result(errors, value.get("warnings", []))


def phonon_animation_summary(package: dict[str, Any]) -> dict[str, Any]:
    mode = package["mode"]["mode"]
    return {
        "schema_version": PHONON_ANIMATION_SUMMARY_SCHEMA_VERSION,
        "mode_id": mode["mode_id"], "qpoint_index": mode["qpoint_index"],
        "branch_index": mode["branch_index"], "frequency": mode["frequency"],
        "frequency_unit": mode["frequency_unit"],
        "imaginary_mode": bool(package["mode"]["provenance"]["imaginary_mode"]),
        "atom_count": package["mode"]["atom_count"],
        "displayed_atom_count": package["supercell"]["displayed_atom_count"],
        "supercell": package["supercell"]["repeat"], "default_state": "paused",
        "display_only": True, "warnings": list(package["warnings"]),
    }


def phonon_animation_manifest(package: dict[str, Any], summary: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": PHONON_ANIMATION_MANIFEST_SCHEMA_VERSION,
        "tool_id": "phonon.animation", "mode_id": package["mode"]["mode"]["mode_id"],
        "artifacts": [
            {"name": "phonon_animation.json", "schema_version": PHONON_ANIMATION_SCHEMA_VERSION, "sha256": eigenvector_content_hash(package)},
            {"name": "phonon_animation_summary.json", "schema_version": PHONON_ANIMATION_SUMMARY_SCHEMA_VERSION, "sha256": eigenvector_content_hash(summary)},
        ],
        "renderer": {"included": False, "application_owned": True, "external_assets": []},
        "security": dict(_SECURITY),
    }


def _validate_structure(value: Any) -> dict[str, Any]:
    fields = {"structure_identity", "formula", "lattice", "sites", "bonds"}
    if not isinstance(value, dict) or set(value) != fields or not _sha(value.get("structure_identity")) or not isinstance(value.get("formula"), str):
        raise PhononAnimationContractError("PHONON_ANIMATION_STRUCTURE_INVALID", "The canonical structure binding is invalid.")
    lattice = value.get("lattice")
    sites = value.get("sites")
    if not isinstance(lattice, list) or len(lattice) != 3 or any(not _triplet(row) for row in lattice) or not isinstance(sites, list) or not sites or len(sites) > PHONON_ANIMATION_CAPS["max_atoms"]:
        raise PhononAnimationContractError("PHONON_ANIMATION_STRUCTURE_INVALID", "The structure lattice or site count is invalid.")
    normalized_sites = []
    for index, site in enumerate(sites):
        if not isinstance(site, dict) or set(site) != {"site_index", "species", "fractional", "cartesian"} or site.get("site_index") != index or not isinstance(site.get("species"), str) or not _triplet(site.get("fractional")) or not _triplet(site.get("cartesian")):
            raise PhononAnimationContractError("PHONON_ANIMATION_ATOM_ORDER_MISMATCH", "Canonical structure sites must be contiguous and finite.")
        normalized_sites.append({"site_index": index, "species": site["species"], "fractional": [float(x) for x in site["fractional"]], "cartesian": [float(x) for x in site["cartesian"]]})
    bonds = value.get("bonds")
    if not isinstance(bonds, list) or len(bonds) > 2048:
        raise PhononAnimationContractError("PHONON_ANIMATION_STRUCTURE_INVALID", "Structure bonds exceed the approved bound.")
    return {"structure_identity": value["structure_identity"], "formula": value["formula"], "lattice": [[float(x) for x in row] for row in lattice], "sites": normalized_sites, "bonds": bonds}


def _scan_inert(value: Any, errors: set[str], key: str = "") -> None:
    forbidden = {"html", "javascript", "script", "callback", "shader", "module", "url", "uri", "texture", "iframe", "code"}
    if isinstance(value, dict):
        for child_key, child in value.items():
            if str(child_key).lower() in forbidden:
                errors.add("PHONON_ANIMATION_EXECUTABLE_CONTENT_FORBIDDEN")
            _scan_inert(child, errors, str(child_key))
    elif isinstance(value, list):
        for child in value:
            _scan_inert(child, errors, key)
    elif isinstance(value, str):
        lowered = value.lower()
        if "<script" in lowered or "javascript:" in lowered or "http://" in lowered or "https://" in lowered:
            errors.add("PHONON_ANIMATION_EXTERNAL_CONTENT_FORBIDDEN")


def _result(errors: set[str], warnings: Sequence[str] = ()) -> PhononAnimationValidationResult:
    return PhononAnimationValidationResult(not errors, tuple(sorted(errors)), tuple(sorted(str(item) for item in warnings)))


def _bounded_float(value: Any, minimum: float, maximum: float) -> float:
    if not _finite(value) or not minimum <= float(value) <= maximum:
        raise PhononAnimationContractError("PHONON_ANIMATION_PARAM_INVALID", "A numeric animation parameter is outside the approved bound.")
    return float(value)


def _finite(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(float(value))


def _triplet(value: Any) -> bool:
    return isinstance(value, (list, tuple)) and len(value) == 3 and all(_finite(item) for item in value)


def _repeat(value: Any) -> bool:
    return isinstance(value, (list, tuple)) and len(value) == 3 and all(isinstance(item, int) and not isinstance(item, bool) and 1 <= item <= PHONON_ANIMATION_CAPS["max_supercell_axis"] for item in value)


def _sha(value: Any) -> bool:
    return isinstance(value, str) and len(value) == 64 and all(char in "0123456789abcdef" for char in value)
