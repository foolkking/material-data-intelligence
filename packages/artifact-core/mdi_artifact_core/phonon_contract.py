from __future__ import annotations

import hashlib
import json
import math
import re
from dataclasses import dataclass
from typing import Any, Literal


PHONON_BAND_SCHEMA_VERSION = "phase10h.phonon_band.v1"
PHONON_DOS_SCHEMA_VERSION = "phase10h.phonon_dos.v1"
PHONON_SUMMARY_SCHEMA_VERSION = "phase10h.phonon_summary.v1"
PHONON_MANIFEST_SCHEMA_VERSION = "phase10h.phonon_manifest.v1"
PHONON_DOS_SUMMARY_SCHEMA_VERSION = "phase10h2.phonon_dos_summary.v1"
PHONON_DOS_MANIFEST_SCHEMA_VERSION = "phase10h2.phonon_dos_manifest.v1"
QPOINT_PATH_SCHEMA_VERSION = "phase10h.qpoint_path.v1"
FREQUENCY_AXIS_SCHEMA_VERSION = "phase10h.frequency_axis.v1"
PHONON_SOURCE_SCHEMA_VERSION = "phase10h.phonon_source.v1"
PHONON_MODE_REF_SCHEMA_VERSION = "phase10h.phonon_mode_ref.v1"

RECIPROCAL_CONVENTION = "physics_2pi"
QPOINT_COORDINATE_SYSTEM = "reciprocal_fractional"
PATH_DISTANCE_UNIT = "radian_per_angstrom"
FREQUENCY_UNIT = "terahertz"
IMAGINARY_FREQUENCY_ENCODING = "negative_real"
DENSITY_UNIT = "modes_per_terahertz"
DOS_NORMALIZATION = "total_modes"

# Exact SI defining constants (2019 SI), used without rounded conversion factors.
PLANCK_CONSTANT_JOULE_SECOND = 6.62607015e-34
SPEED_OF_LIGHT_METER_PER_SECOND = 299_792_458.0
ELECTRONVOLT_JOULE = 1.602176634e-19

DEFAULT_PHONON_CAPS: dict[str, int] = {
    "max_atoms": 512,
    "max_branches": 1536,
    "max_qpoints": 4096,
    "max_segments": 256,
    "max_labels": 512,
    "max_label_length": 64,
    "max_dos_points": 100_000,
    "max_projected_dos_series": 512,
    "max_total_numeric_values": 4_000_000,
    "max_metadata_bytes": 16_384,
    "max_warnings": 32,
    "max_artifact_bytes": 64_000_000,
    "max_degeneracy_groups": 4096,
    "max_nesting_depth": 10,
    "max_visited_nodes": 5_000_000,
    "max_numeric_magnitude": 1_000_000_000_000,
}

PHONON_ERROR_CODES = frozenset(
    {
        "PHONON_SCHEMA_UNSUPPORTED",
        "PHONON_STRUCTURE_IDENTITY_REQUIRED",
        "PHONON_ATOM_COUNT_INVALID",
        "PHONON_SPECIES_ORDER_INVALID",
        "PHONON_RECIPROCAL_CONVENTION_UNSUPPORTED",
        "PHONON_QPOINT_COORDINATE_SYSTEM_UNSUPPORTED",
        "PHONON_QPOINT_SHAPE_INVALID",
        "PHONON_QPOINT_NONFINITE",
        "PHONON_QPOINT_INDEX_INVALID",
        "PHONON_QPOINT_DISTANCE_NONMONOTONIC",
        "PHONON_PATH_SEGMENT_INVALID",
        "PHONON_PATH_LABEL_INVALID",
        "PHONON_FREQUENCY_UNIT_UNSUPPORTED",
        "PHONON_FREQUENCY_NONFINITE",
        "PHONON_FREQUENCY_SHAPE_INVALID",
        "PHONON_BRANCH_COUNT_MISMATCH",
        "PHONON_BRANCH_INDEX_INVALID",
        "PHONON_IMAGINARY_ENCODING_UNSUPPORTED",
        "PHONON_ZERO_TOLERANCE_INVALID",
        "PHONON_DEGENERACY_GROUP_INVALID",
        "PHONON_DOS_GRID_INVALID",
        "PHONON_DOS_NONFINITE",
        "PHONON_DOS_SHAPE_INVALID",
        "PHONON_DOS_NORMALIZATION_UNSUPPORTED",
        "PHONON_DOS_INTEGRAL_MISMATCH",
        "PHONON_PROJECTED_DOS_IDENTITY_INVALID",
        "PHONON_PROJECTED_DOS_DUPLICATE",
        "PHONON_BAND_DOS_STRUCTURE_MISMATCH",
        "PHONON_BAND_DOS_UNIT_MISMATCH",
        "PHONON_BAND_DOS_SOURCE_INCOMPATIBLE",
        "PHONON_CAP_EXCEEDED",
        "PHONON_METADATA_LIMIT_EXCEEDED",
        "PHONON_EXTERNAL_REFERENCE_FORBIDDEN",
    }
)

PHONON_WARNING_CODES = frozenset(
    {
        "PHONON_SMALL_IMAGINARY_FREQUENCY",
        "PHONON_ACOUSTIC_MODES_NOT_CORRECTED",
        "PHONON_SOURCE_SOFTWARE_UNKNOWN",
        "PHONON_NAC_STATUS_UNKNOWN",
        "PHONON_DEGENERACY_SOURCE_UNAVAILABLE",
        "PHONON_DOS_INTEGRAL_APPROXIMATE",
        "PHONON_PROJECTED_DOS_SUM_MISMATCH",
        "PHONON_BAND_CONNECTIVITY_SOURCE_ORDER_ONLY",
        "PHONON_HIGH_SYMMETRY_LABEL_NORMALIZED",
    }
)

_BAND_FIELDS = {
    "schema_version",
    "structure_identity",
    "atom_count",
    "species",
    "atom_ordering",
    "real_space_lattice_angstrom",
    "reciprocal_convention",
    "qpoint_coordinate_system",
    "path_distance_unit",
    "frequency_unit",
    "imaginary_frequency_encoding",
    "frequency_zero_tolerance",
    "branch_scope",
    "qpoints",
    "segments",
    "branches",
    "degeneracy_groups",
    "acoustic_sum_rule",
    "source",
    "warnings",
    "security",
}
_DOS_FIELDS = {
    "schema_version",
    "structure_identity",
    "atom_count",
    "species",
    "atom_ordering",
    "frequency_unit",
    "imaginary_frequency_encoding",
    "frequency_zero_tolerance",
    "density_unit",
    "normalization",
    "frequency_grid_semantics",
    "frequencies",
    "total_dos",
    "projected_dos",
    "broadening",
    "integration",
    "source",
    "warnings",
    "security",
}
_QPOINT_FIELDS = {"index", "coordinates", "label", "source_label", "segment_index", "distance"}
_SEGMENT_FIELDS = {
    "segment_index",
    "start_qpoint_index",
    "end_qpoint_index",
    "start_label",
    "end_label",
    "discontinuous_from_previous",
}
_BRANCH_FIELDS = {"branch_index", "frequencies"}
_DEGENERACY_FIELDS = {"qpoint_index", "branch_indices", "source"}
_SOURCE_FIELDS = {
    "producer",
    "producer_version",
    "calculation_method",
    "force_constants_source",
    "supercell_matrix",
    "primitive_matrix",
    "nac",
    "input_sha256",
    "adapter_version",
}
_NAC_FIELDS = {"enabled", "gamma_direction", "direction_policy"}
_ASR_FIELDS = {"applied", "method"}
_PROJECTION_FIELDS = {
    "projection_index",
    "projection_type",
    "atom_index",
    "species",
    "values",
    "source_guarantees_sum",
}
_BROADENING_FIELDS = {"method", "width", "unit", "source"}
_INTEGRATION_FIELDS = {"method", "expected_mode_count", "observed_integral", "relative_tolerance", "status"}
_SECURITY_FLAGS = {
    "contains_javascript": False,
    "contains_html": False,
    "external_urls_allowed": False,
    "executable_content_allowed": False,
    "external_assets": [],
}
_FORBIDDEN_KEYS = {
    "callback",
    "callbacks",
    "code",
    "eval",
    "formula",
    "function",
    "html",
    "iframe",
    "module",
    "script",
    "shader",
    "src",
    "texture",
    "url",
    "urls",
    "__proto__",
    "constructor",
    "prototype",
}
_FORBIDDEN_MARKERS = (
    "http://",
    "https://",
    "javascript:",
    "<script",
    "<iframe",
    "eval(",
    "new function",
    "file://",
    "data:text/html",
)
_PRIVATE_PATH_PATTERNS = (re.compile(r"^[a-zA-Z]:[\\/]"), re.compile(r"^/(?:home|users|root|etc)/"))
_ELEMENT_RE = re.compile(r"[A-Z][a-z]?")
_SAFE_TEXT_RE = re.compile(r"[A-Za-z0-9_.:+() /-]+")


@dataclass(frozen=True)
class PhononValidationResult:
    valid: bool
    errors: tuple[str, ...]
    warnings: tuple[str, ...]
    caps: dict[str, int]
    atom_count: int
    qpoint_count: int
    branch_count: int
    dos_point_count: int
    projected_series_count: int

    def as_dict(self) -> dict[str, Any]:
        return {
            "valid": self.valid,
            "errors": list(self.errors),
            "warnings": list(self.warnings),
            "caps": dict(self.caps),
            "atom_count": self.atom_count,
            "qpoint_count": self.qpoint_count,
            "branch_count": self.branch_count,
            "dos_point_count": self.dos_point_count,
            "projected_series_count": self.projected_series_count,
        }


@dataclass(frozen=True)
class PhononCompatibilityResult:
    status: Literal["compatible", "convertible", "incompatible"]
    reasons: tuple[str, ...]

    def as_dict(self) -> dict[str, Any]:
        return {"status": self.status, "reasons": list(self.reasons)}


def stable_phonon_json(payload: Any) -> str:
    return json.dumps(payload, ensure_ascii=True, allow_nan=False, sort_keys=True, separators=(",", ":"))


def phonon_content_hash(payload: Any) -> str:
    return hashlib.sha256(stable_phonon_json(payload).encode("utf-8")).hexdigest()


def normalize_high_symmetry_label(label: str | None) -> str | None:
    if label is None:
        return None
    normalized = label.strip()
    if normalized.lower() in {"gamma", "\\gamma", "g"} or normalized == "Γ":
        return "Γ"
    return normalized.upper() if len(normalized) == 1 and normalized.isascii() else normalized


def reciprocal_lattice_physics_2pi(real_lattice: list[list[float]]) -> list[list[float]]:
    rows = _validated_matrix(real_lattice)
    determinant = _determinant(rows)
    scale = max(math.sqrt(sum(component * component for component in row)) for row in rows)
    if scale == 0 or abs(determinant) <= 1e-12 * scale**3:
        raise ValueError("PHONON_RECIPROCAL_CONVENTION_UNSUPPORTED")
    inverse = _inverse(rows, determinant)
    condition = _frobenius(rows) * _frobenius(inverse)
    if not math.isfinite(condition) or condition > 1e8:
        raise ValueError("PHONON_RECIPROCAL_CONVENTION_UNSUPPORTED")
    return [[2.0 * math.pi * inverse[column][row] for column in range(3)] for row in range(3)]


def reciprocal_fractional_to_cartesian(
    coordinates: list[float], real_lattice: list[list[float]]
) -> list[float]:
    if not _triplet(coordinates):
        raise ValueError("PHONON_QPOINT_SHAPE_INVALID")
    reciprocal = reciprocal_lattice_physics_2pi(real_lattice)
    return [sum(float(coordinates[row]) * reciprocal[row][axis] for row in range(3)) for axis in range(3)]


def reciprocal_path_step(
    start: list[float], end: list[float], real_lattice: list[list[float]]
) -> float:
    start_cart = reciprocal_fractional_to_cartesian(start, real_lattice)
    end_cart = reciprocal_fractional_to_cartesian(end, real_lattice)
    return math.sqrt(sum((end_cart[axis] - start_cart[axis]) ** 2 for axis in range(3)))


def convert_frequency(value: float, source_unit: str, target_unit: str) -> float:
    if not _finite_number(value):
        raise ValueError("PHONON_FREQUENCY_NONFINITE")
    approved = {"terahertz", "inverse_centimeter", "millielectronvolt"}
    if source_unit not in approved or target_unit not in approved:
        raise ValueError("PHONON_FREQUENCY_UNIT_UNSUPPORTED")
    if source_unit == "terahertz":
        thz = float(value)
    elif source_unit == "inverse_centimeter":
        thz = float(value) * SPEED_OF_LIGHT_METER_PER_SECOND * 100.0 / 1e12
    else:
        thz = float(value) * ELECTRONVOLT_JOULE / (PLANCK_CONSTANT_JOULE_SECOND * 1e15)
    if target_unit == "terahertz":
        return thz
    if target_unit == "inverse_centimeter":
        return thz * 1e12 / (SPEED_OF_LIGHT_METER_PER_SECOND * 100.0)
    return thz * PLANCK_CONSTANT_JOULE_SECOND * 1e15 / ELECTRONVOLT_JOULE


def classify_frequency(value: float, zero_tolerance: float) -> Literal["imaginary", "near_zero", "real"]:
    if not _finite_number(value) or not _finite_number(zero_tolerance) or float(zero_tolerance) < 0:
        raise ValueError("PHONON_ZERO_TOLERANCE_INVALID")
    if float(value) < -float(zero_tolerance):
        return "imaginary"
    if abs(float(value)) <= float(zero_tolerance):
        return "near_zero"
    return "real"


def trapezoidal_integral(x: list[float], y: list[float]) -> float:
    if len(x) != len(y) or len(x) < 2 or any(not _finite_number(item) for item in x + y):
        raise ValueError("PHONON_DOS_SHAPE_INVALID")
    return sum((float(x[index + 1]) - float(x[index])) * (float(y[index + 1]) + float(y[index])) / 2.0 for index in range(len(x) - 1))


def validate_phonon_band(payload: Any, *, raw_size_bytes: int | None = None) -> PhononValidationResult:
    errors: set[str] = set()
    warnings: set[str] = set()
    if not isinstance(payload, dict):
        return _result({"PHONON_SCHEMA_UNSUPPORTED"}, warnings)
    if set(payload) != _BAND_FIELDS or payload.get("schema_version") != PHONON_BAND_SCHEMA_VERSION:
        errors.add("PHONON_SCHEMA_UNSUPPORTED")
    _validate_raw_size(payload, raw_size_bytes, errors)
    _scan_inert_content(payload, errors)
    _validate_security(payload.get("security"), errors)
    atom_count, species = _validate_structure_identity(payload, errors)
    lattice = _validate_band_conventions(payload, errors)
    _validate_source(payload.get("source"), errors, warnings)
    _validate_warnings(payload.get("warnings"), errors, warnings)
    tolerance = payload.get("frequency_zero_tolerance")
    if not _finite_number(tolerance) or not (0 <= float(tolerance) <= 1.0):
        errors.add("PHONON_ZERO_TOLERANCE_INVALID")

    qpoints_value = payload.get("qpoints")
    segments_value = payload.get("segments")
    branches_value = payload.get("branches")
    degeneracy_value = payload.get("degeneracy_groups")
    qpoints = qpoints_value if isinstance(qpoints_value, list) else []
    segments = segments_value if isinstance(segments_value, list) else []
    branches = branches_value if isinstance(branches_value, list) else []
    degeneracy = degeneracy_value if isinstance(degeneracy_value, list) else []
    if not isinstance(qpoints_value, list) or not qpoints:
        errors.add("PHONON_QPOINT_SHAPE_INVALID")
    if not isinstance(segments_value, list) or not segments:
        errors.add("PHONON_PATH_SEGMENT_INVALID")
    if not isinstance(branches_value, list) or not branches:
        errors.add("PHONON_FREQUENCY_SHAPE_INVALID")
    if not isinstance(degeneracy_value, list):
        errors.add("PHONON_DEGENERACY_GROUP_INVALID")
    if len(qpoints) > DEFAULT_PHONON_CAPS["max_qpoints"] or len(segments) > DEFAULT_PHONON_CAPS["max_segments"]:
        errors.add("PHONON_CAP_EXCEEDED")
    if len(branches) > DEFAULT_PHONON_CAPS["max_branches"] or len(degeneracy) > DEFAULT_PHONON_CAPS["max_degeneracy_groups"]:
        errors.add("PHONON_CAP_EXCEEDED")
    if _product_exceeds(len(qpoints), len(branches), DEFAULT_PHONON_CAPS["max_total_numeric_values"]):
        errors.add("PHONON_CAP_EXCEEDED")
    degeneracy_numeric_count = 0
    for group in degeneracy:
        indices = group.get("branch_indices") if isinstance(group, dict) else None
        degeneracy_numeric_count += len(indices) if isinstance(indices, list) else 0
        if degeneracy_numeric_count > DEFAULT_PHONON_CAPS["max_total_numeric_values"]:
            errors.add("PHONON_CAP_EXCEEDED")
            break
    band_numeric_count = 9 + len(qpoints) * 4 + len(qpoints) * len(branches) + degeneracy_numeric_count
    if band_numeric_count > DEFAULT_PHONON_CAPS["max_total_numeric_values"]:
        errors.add("PHONON_CAP_EXCEEDED")

    if len(branches) != atom_count * 3 or payload.get("branch_scope") != "full":
        errors.add("PHONON_BRANCH_COUNT_MISMATCH")
    _validate_qpoints(qpoints, lattice, errors, warnings)
    _validate_segments(segments, qpoints, errors)
    if lattice:
        _validate_path_distances(qpoints, segments, lattice, errors)
    _validate_branches(branches, len(qpoints), errors, warnings, float(tolerance) if _finite_number(tolerance) else 0.0)
    _validate_degeneracy(degeneracy, len(qpoints), len(branches), errors)
    _validate_asr(payload.get("acoustic_sum_rule"), errors, warnings)
    if atom_count and len(species) != atom_count:
        errors.add("PHONON_SPECIES_ORDER_INVALID")
    warnings.add("PHONON_BAND_CONNECTIVITY_SOURCE_ORDER_ONLY")
    return _result(errors, warnings, atom_count=atom_count, qpoints=len(qpoints), branches=len(branches))


def validate_phonon_dos(payload: Any, *, raw_size_bytes: int | None = None) -> PhononValidationResult:
    errors: set[str] = set()
    warnings: set[str] = set()
    if not isinstance(payload, dict):
        return _result({"PHONON_SCHEMA_UNSUPPORTED"}, warnings)
    if set(payload) != _DOS_FIELDS or payload.get("schema_version") != PHONON_DOS_SCHEMA_VERSION:
        errors.add("PHONON_SCHEMA_UNSUPPORTED")
    _validate_raw_size(payload, raw_size_bytes, errors)
    _scan_inert_content(payload, errors)
    _validate_security(payload.get("security"), errors)
    atom_count, _ = _validate_structure_identity(payload, errors)
    _validate_frequency_policy(payload, errors)
    _validate_source(payload.get("source"), errors, warnings)
    _validate_warnings(payload.get("warnings"), errors, warnings)
    if payload.get("density_unit") != DENSITY_UNIT or payload.get("normalization") != DOS_NORMALIZATION:
        errors.add("PHONON_DOS_NORMALIZATION_UNSUPPORTED")
    if payload.get("frequency_grid_semantics") != "sample_grid_points":
        errors.add("PHONON_DOS_GRID_INVALID")

    frequencies_value = payload.get("frequencies")
    total_value = payload.get("total_dos")
    projected_value = payload.get("projected_dos")
    frequencies = frequencies_value if isinstance(frequencies_value, list) else []
    total = total_value if isinstance(total_value, list) else []
    projected = projected_value if isinstance(projected_value, list) else []
    if not isinstance(frequencies_value, list) or len(frequencies) < 2:
        errors.add("PHONON_DOS_GRID_INVALID")
    if len(frequencies) > DEFAULT_PHONON_CAPS["max_dos_points"] or len(projected) > DEFAULT_PHONON_CAPS["max_projected_dos_series"]:
        errors.add("PHONON_CAP_EXCEEDED")
    if _product_exceeds(len(frequencies), len(projected) + 2, DEFAULT_PHONON_CAPS["max_total_numeric_values"]):
        errors.add("PHONON_CAP_EXCEEDED")
    if any(not _finite_number(item) for item in frequencies):
        errors.add("PHONON_DOS_NONFINITE")
    elif any(float(frequencies[index]) >= float(frequencies[index + 1]) for index in range(len(frequencies) - 1)):
        errors.add("PHONON_DOS_GRID_INVALID")
    if not isinstance(total_value, list) or len(total) != len(frequencies):
        errors.add("PHONON_DOS_SHAPE_INVALID")
    elif any(not _finite_number(item) or float(item) < 0 for item in total):
        errors.add("PHONON_DOS_NONFINITE")
    _validate_projected_dos(projected_value, len(frequencies), atom_count, payload.get("species"), total, errors, warnings)
    _validate_broadening(payload.get("broadening"), errors)
    _validate_integration(payload.get("integration"), frequencies, total, atom_count, errors, warnings)
    return _result(errors, warnings, atom_count=atom_count, dos_points=len(frequencies), projections=len(projected))


def validate_band_dos_compatibility(band: Any, dos: Any) -> PhononCompatibilityResult:
    reasons: set[str] = set()
    convertible = False
    if not isinstance(band, dict) or not isinstance(dos, dict):
        return PhononCompatibilityResult("incompatible", ("PHONON_SCHEMA_UNSUPPORTED",))
    if band.get("structure_identity") != dos.get("structure_identity") or band.get("atom_count") != dos.get("atom_count") or band.get("species") != dos.get("species") or band.get("atom_ordering") != dos.get("atom_ordering"):
        reasons.add("PHONON_BAND_DOS_STRUCTURE_MISMATCH")
    band_unit, dos_unit = band.get("frequency_unit"), dos.get("frequency_unit")
    if band_unit != dos_unit:
        if band_unit in {"terahertz", "inverse_centimeter", "millielectronvolt"} and dos_unit in {"terahertz", "inverse_centimeter", "millielectronvolt"}:
            convertible = True
            reasons.add("PHONON_BAND_DOS_UNIT_MISMATCH")
        else:
            reasons.add("PHONON_BAND_DOS_UNIT_MISMATCH")
    if band.get("imaginary_frequency_encoding") != dos.get("imaginary_frequency_encoding"):
        reasons.add("PHONON_BAND_DOS_UNIT_MISMATCH")
    if band.get("frequency_zero_tolerance") != dos.get("frequency_zero_tolerance"):
        reasons.add("PHONON_BAND_DOS_UNIT_MISMATCH")
    band_source = band.get("source") if isinstance(band.get("source"), dict) else {}
    dos_source = dos.get("source") if isinstance(dos.get("source"), dict) else {}
    source_keys = ("producer", "calculation_method", "force_constants_source", "supercell_matrix", "primitive_matrix", "input_sha256")
    if any(band_source.get(key) != dos_source.get(key) for key in source_keys) or band_source.get("nac") != dos_source.get("nac"):
        reasons.add("PHONON_BAND_DOS_SOURCE_INCOMPATIBLE")
    band_values = [value for branch in band.get("branches", []) if isinstance(branch, dict) for value in branch.get("frequencies", []) if _finite_number(value)]
    dos_values = [value for value in dos.get("frequencies", []) if _finite_number(value)] if isinstance(dos.get("frequencies"), list) else []
    if band_values and dos_values and band_unit in {"terahertz", "inverse_centimeter", "millielectronvolt"} and dos_unit in {"terahertz", "inverse_centimeter", "millielectronvolt"}:
        band_min = convert_frequency(min(band_values), str(band_unit), "terahertz")
        band_max = convert_frequency(max(band_values), str(band_unit), "terahertz")
        dos_min = convert_frequency(min(dos_values), str(dos_unit), "terahertz")
        dos_max = convert_frequency(max(dos_values), str(dos_unit), "terahertz")
        if dos_min > band_min + 1e-8 or dos_max < band_max - 1e-8:
            reasons.add("PHONON_BAND_DOS_SOURCE_INCOMPATIBLE")
    if dos.get("normalization") != DOS_NORMALIZATION or dos.get("density_unit") != DENSITY_UNIT:
        reasons.add("PHONON_BAND_DOS_SOURCE_INCOMPATIBLE")
    if not reasons:
        return PhononCompatibilityResult("compatible", ())
    if convertible and reasons == {"PHONON_BAND_DOS_UNIT_MISMATCH"}:
        return PhononCompatibilityResult("convertible", tuple(sorted(reasons)))
    return PhononCompatibilityResult("incompatible", tuple(sorted(reasons)))


def phonon_summary(band: dict[str, Any], dos: dict[str, Any] | None = None) -> dict[str, Any]:
    band_result = validate_phonon_band(band)
    if not band_result.valid:
        raise ValueError("phonon band must validate before summary generation")
    if dos is not None:
        dos_result = validate_phonon_dos(dos)
        compatibility = validate_band_dos_compatibility(band, dos)
        if not dos_result.valid or compatibility.status != "compatible":
            raise ValueError("phonon DOS must validate and be compatible before summary generation")
    all_frequencies = [float(value) for branch in band["branches"] for value in branch["frequencies"]]
    tolerance = float(band["frequency_zero_tolerance"])
    return {
        "schema_version": PHONON_SUMMARY_SCHEMA_VERSION,
        "structure_identity": band["structure_identity"],
        "atom_count": band["atom_count"],
        "branch_count": len(band["branches"]),
        "qpoint_count": len(band["qpoints"]),
        "segment_count": len(band["segments"]),
        "frequency_unit": FREQUENCY_UNIT,
        "frequency_min": min(all_frequencies),
        "frequency_max": max(all_frequencies),
        "imaginary_mode_count": sum(value < -tolerance for value in all_frequencies),
        "near_zero_mode_count": sum(abs(value) <= tolerance for value in all_frequencies),
        "dos_available": dos is not None,
        "projected_dos_available": bool(dos and dos["projected_dos"]),
        "nac_enabled": band["source"]["nac"]["enabled"],
        "warnings": list(band_result.warnings),
    }


def validate_phonon_summary(payload: Any) -> PhononValidationResult:
    errors: set[str] = set()
    fields = {
        "schema_version", "structure_identity", "atom_count", "branch_count", "qpoint_count",
        "segment_count", "frequency_unit", "frequency_min", "frequency_max", "imaginary_mode_count",
        "near_zero_mode_count", "dos_available", "projected_dos_available", "nac_enabled", "warnings",
    }
    if not isinstance(payload, dict) or set(payload) != fields or payload.get("schema_version") != PHONON_SUMMARY_SCHEMA_VERSION:
        return _result({"PHONON_SCHEMA_UNSUPPORTED"}, set())
    _scan_inert_content(payload, errors)
    if not _sha256(payload.get("structure_identity")):
        errors.add("PHONON_STRUCTURE_IDENTITY_REQUIRED")
    counts = [payload.get(key) for key in ("atom_count", "branch_count", "qpoint_count", "segment_count", "imaginary_mode_count", "near_zero_mode_count")]
    if any(not _nonnegative_int(item) for item in counts) or not _positive_int(payload.get("atom_count")):
        errors.add("PHONON_ATOM_COUNT_INVALID")
    atom_count_value = payload.get("atom_count") if _positive_int(payload.get("atom_count")) else 0
    if payload.get("branch_count") != 3 * atom_count_value:
        errors.add("PHONON_BRANCH_COUNT_MISMATCH")
    if payload.get("frequency_unit") != FREQUENCY_UNIT:
        errors.add("PHONON_FREQUENCY_UNIT_UNSUPPORTED")
    minimum, maximum = payload.get("frequency_min"), payload.get("frequency_max")
    if not _finite_number(minimum) or not _finite_number(maximum) or float(minimum) > float(maximum):
        errors.add("PHONON_FREQUENCY_NONFINITE")
    if any(type(payload.get(key)) is not bool for key in ("dos_available", "projected_dos_available", "nac_enabled")) or payload.get("projected_dos_available") and not payload.get("dos_available"):
        errors.add("PHONON_SCHEMA_UNSUPPORTED")
    warnings: set[str] = set()
    _validate_warnings(payload.get("warnings"), errors, warnings)
    return _result(errors, warnings, atom_count=int(payload.get("atom_count", 0) or 0), qpoints=int(payload.get("qpoint_count", 0) or 0), branches=int(payload.get("branch_count", 0) or 0))


def validate_phonon_manifest(payload: Any) -> PhononValidationResult:
    errors: set[str] = set()
    fields = {"schema_version", "structure_identity", "band_schema_version", "dos_schema_version", "summary_schema_version", "artifacts", "security"}
    if not isinstance(payload, dict) or set(payload) != fields or payload.get("schema_version") != PHONON_MANIFEST_SCHEMA_VERSION:
        return _result({"PHONON_SCHEMA_UNSUPPORTED"}, set())
    _scan_inert_content(payload, errors)
    _validate_security(payload.get("security"), errors)
    if not _sha256(payload.get("structure_identity")):
        errors.add("PHONON_STRUCTURE_IDENTITY_REQUIRED")
    if payload.get("band_schema_version") != PHONON_BAND_SCHEMA_VERSION or payload.get("summary_schema_version") != PHONON_SUMMARY_SCHEMA_VERSION:
        errors.add("PHONON_SCHEMA_UNSUPPORTED")
    if payload.get("dos_schema_version") not in {None, PHONON_DOS_SCHEMA_VERSION}:
        errors.add("PHONON_SCHEMA_UNSUPPORTED")
    artifacts = payload.get("artifacts")
    expected_names = ["phonon_band.json"] + (["phonon_dos.json"] if payload.get("dos_schema_version") else []) + ["phonon_summary.json"]
    if not isinstance(artifacts, list) or len(artifacts) != len(expected_names) or any(not isinstance(item, dict) for item in artifacts) or [item.get("name") for item in artifacts] != expected_names:
        errors.add("PHONON_SCHEMA_UNSUPPORTED")
    else:
        schema_by_name = {
            "phonon_band.json": PHONON_BAND_SCHEMA_VERSION,
            "phonon_dos.json": PHONON_DOS_SCHEMA_VERSION,
            "phonon_summary.json": PHONON_SUMMARY_SCHEMA_VERSION,
        }
        for artifact in artifacts:
            if set(artifact) != {"name", "schema_version", "media_type", "size_bytes", "sha256"} or artifact.get("schema_version") != schema_by_name.get(artifact.get("name")) or artifact.get("media_type") != "application/json" or not _positive_int(artifact.get("size_bytes")) or artifact["size_bytes"] > DEFAULT_PHONON_CAPS["max_artifact_bytes"] or not _sha256(artifact.get("sha256")):
                errors.add("PHONON_SCHEMA_UNSUPPORTED")
    return _result(errors, set())


def phonon_dos_summary(
    dos: dict[str, Any],
    *,
    projection_completeness: Literal["complete", "partial", "unknown"],
) -> dict[str, Any]:
    result = validate_phonon_dos(dos)
    if not result.valid:
        raise ValueError("phonon DOS must validate before summary generation")
    frequencies = [float(value) for value in dos["frequencies"]]
    total = [float(value) for value in dos["total_dos"]]
    tolerance = float(dos["frequency_zero_tolerance"])
    return {
        "schema_version": PHONON_DOS_SUMMARY_SCHEMA_VERSION,
        "structure_identity": dos["structure_identity"],
        "atom_count": dos["atom_count"],
        "frequency_min": min(frequencies),
        "frequency_max": max(frequencies),
        "frequency_unit": FREQUENCY_UNIT,
        "density_unit": DENSITY_UNIT,
        "normalization": DOS_NORMALIZATION,
        "expected_mode_count": dos["integration"]["expected_mode_count"],
        "observed_integral": dos["integration"]["observed_integral"],
        "normalization_status": dos["integration"]["status"],
        "imaginary_region_integral": _integral_below_zero(frequencies, total),
        "near_zero_point_count": sum(abs(value) <= tolerance for value in frequencies),
        "total_dos_available": True,
        "projected_dos_available": bool(dos["projected_dos"]),
        "projection_count": len(dos["projected_dos"]),
        "projection_completeness": projection_completeness,
        "broadening": dos["broadening"],
        "source": dos["source"],
        "warnings": list(result.warnings),
    }


def validate_phonon_dos_summary(payload: Any) -> PhononValidationResult:
    errors: set[str] = set()
    fields = {
        "schema_version", "structure_identity", "atom_count", "frequency_min", "frequency_max",
        "frequency_unit", "density_unit", "normalization", "expected_mode_count", "observed_integral",
        "normalization_status", "imaginary_region_integral", "near_zero_point_count", "total_dos_available",
        "projected_dos_available", "projection_count", "projection_completeness", "broadening", "source", "warnings",
    }
    if not isinstance(payload, dict) or set(payload) != fields or payload.get("schema_version") != PHONON_DOS_SUMMARY_SCHEMA_VERSION:
        return _result({"PHONON_SCHEMA_UNSUPPORTED"}, set())
    _scan_inert_content(payload, errors)
    if not _sha256(payload.get("structure_identity")):
        errors.add("PHONON_STRUCTURE_IDENTITY_REQUIRED")
    atom_count = payload.get("atom_count")
    if not _positive_int(atom_count) or atom_count > DEFAULT_PHONON_CAPS["max_atoms"]:
        errors.add("PHONON_ATOM_COUNT_INVALID")
        atom_count = 0
    if payload.get("frequency_unit") != FREQUENCY_UNIT or payload.get("density_unit") != DENSITY_UNIT or payload.get("normalization") != DOS_NORMALIZATION:
        errors.add("PHONON_DOS_NORMALIZATION_UNSUPPORTED")
    minimum, maximum = payload.get("frequency_min"), payload.get("frequency_max")
    numeric = [minimum, maximum, payload.get("observed_integral"), payload.get("imaginary_region_integral")]
    if any(not _finite_number(value) for value in numeric) or (_finite_number(minimum) and _finite_number(maximum) and float(minimum) > float(maximum)):
        errors.add("PHONON_DOS_NONFINITE")
    if payload.get("expected_mode_count") != 3 * atom_count or payload.get("normalization_status") not in {"within_tolerance", "approximate"}:
        errors.add("PHONON_DOS_INTEGRAL_MISMATCH")
    if any(not _nonnegative_int(payload.get(key)) for key in ("near_zero_point_count", "projection_count")):
        errors.add("PHONON_DOS_SHAPE_INVALID")
    if payload.get("projection_completeness") not in {"complete", "partial", "unknown"}:
        errors.add("PHONON_PROJECTED_DOS_IDENTITY_INVALID")
    if type(payload.get("total_dos_available")) is not bool or payload.get("total_dos_available") is not True or type(payload.get("projected_dos_available")) is not bool:
        errors.add("PHONON_SCHEMA_UNSUPPORTED")
    _validate_broadening(payload.get("broadening"), errors)
    warnings: set[str] = set()
    _validate_source(payload.get("source"), errors, warnings)
    _validate_warnings(payload.get("warnings"), errors, warnings)
    return _result(errors, warnings, atom_count=int(atom_count or 0), projections=int(payload.get("projection_count", 0) or 0))


def validate_phonon_dos_manifest(payload: Any) -> PhononValidationResult:
    errors: set[str] = set()
    fields = {"schema_version", "structure_identity", "dos_schema_version", "summary_schema_version", "artifacts", "security"}
    if not isinstance(payload, dict) or set(payload) != fields or payload.get("schema_version") != PHONON_DOS_MANIFEST_SCHEMA_VERSION:
        return _result({"PHONON_SCHEMA_UNSUPPORTED"}, set())
    _scan_inert_content(payload, errors)
    _validate_security(payload.get("security"), errors)
    if not _sha256(payload.get("structure_identity")):
        errors.add("PHONON_STRUCTURE_IDENTITY_REQUIRED")
    if payload.get("dos_schema_version") != PHONON_DOS_SCHEMA_VERSION or payload.get("summary_schema_version") != PHONON_DOS_SUMMARY_SCHEMA_VERSION:
        errors.add("PHONON_SCHEMA_UNSUPPORTED")
    artifacts = payload.get("artifacts")
    expected = ["phonon_dos.json", "phonon_dos_summary.json"]
    if not isinstance(artifacts, list) or [item.get("name") for item in artifacts if isinstance(item, dict)] != expected or len(artifacts) != 2:
        errors.add("PHONON_SCHEMA_UNSUPPORTED")
    else:
        schemas = {"phonon_dos.json": PHONON_DOS_SCHEMA_VERSION, "phonon_dos_summary.json": PHONON_DOS_SUMMARY_SCHEMA_VERSION}
        for artifact in artifacts:
            if (
                not isinstance(artifact, dict)
                or set(artifact) != {"name", "schema_version", "media_type", "size_bytes", "sha256"}
                or artifact.get("schema_version") != schemas.get(artifact.get("name"))
                or artifact.get("media_type") != "application/json"
                or not _positive_int(artifact.get("size_bytes"))
                or artifact["size_bytes"] > DEFAULT_PHONON_CAPS["max_artifact_bytes"]
                or not _sha256(artifact.get("sha256"))
            ):
                errors.add("PHONON_SCHEMA_UNSUPPORTED")
    return _result(errors, set())


def _integral_below_zero(frequencies: list[float], values: list[float]) -> float:
    integral = 0.0
    for left in range(len(frequencies) - 1):
        x0, x1 = frequencies[left], frequencies[left + 1]
        y0, y1 = values[left], values[left + 1]
        if x0 >= 0:
            break
        if x1 <= 0:
            integral += (x1 - x0) * (y0 + y1) / 2.0
        else:
            y_at_zero = y0 + (y1 - y0) * ((0.0 - x0) / (x1 - x0))
            integral += (0.0 - x0) * (y0 + y_at_zero) / 2.0
            break
    return integral


def phonon_schema_snapshots() -> dict[str, Any]:
    return {
        "band": {"schema_version": PHONON_BAND_SCHEMA_VERSION, "required_fields": sorted(_BAND_FIELDS)},
        "dos": {"schema_version": PHONON_DOS_SCHEMA_VERSION, "required_fields": sorted(_DOS_FIELDS)},
        "summary": {"schema_version": PHONON_SUMMARY_SCHEMA_VERSION, "required_fields": [
            "atom_count", "branch_count", "dos_available", "frequency_max", "frequency_min",
            "frequency_unit", "imaginary_mode_count", "nac_enabled", "near_zero_mode_count",
            "projected_dos_available", "qpoint_count", "schema_version", "segment_count",
            "structure_identity", "warnings",
        ]},
        "manifest": {"schema_version": PHONON_MANIFEST_SCHEMA_VERSION, "artifact_order": [
            "phonon_band.json", "phonon_dos.json", "phonon_summary.json",
        ]},
    }


def _validate_structure_identity(payload: dict[str, Any], errors: set[str]) -> tuple[int, list[Any]]:
    if not _sha256(payload.get("structure_identity")):
        errors.add("PHONON_STRUCTURE_IDENTITY_REQUIRED")
    atom_count = payload.get("atom_count")
    if not _positive_int(atom_count) or atom_count > DEFAULT_PHONON_CAPS["max_atoms"]:
        errors.add("PHONON_ATOM_COUNT_INVALID")
        atom_count = 0
    species = payload.get("species")
    if not isinstance(species, list) or len(species) != atom_count or any(not isinstance(item, str) or _ELEMENT_RE.fullmatch(item) is None for item in species):
        errors.add("PHONON_SPECIES_ORDER_INVALID")
        species = []
    if payload.get("atom_ordering") != "canonical_structure_order":
        errors.add("PHONON_SPECIES_ORDER_INVALID")
    return int(atom_count), species


def _validate_band_conventions(payload: dict[str, Any], errors: set[str]) -> list[list[float]]:
    if payload.get("reciprocal_convention") != RECIPROCAL_CONVENTION or payload.get("path_distance_unit") != PATH_DISTANCE_UNIT:
        errors.add("PHONON_RECIPROCAL_CONVENTION_UNSUPPORTED")
    if payload.get("qpoint_coordinate_system") != QPOINT_COORDINATE_SYSTEM:
        errors.add("PHONON_QPOINT_COORDINATE_SYSTEM_UNSUPPORTED")
    _validate_frequency_policy(payload, errors)
    lattice = payload.get("real_space_lattice_angstrom")
    try:
        reciprocal_lattice_physics_2pi(lattice)
    except (TypeError, ValueError, OverflowError):
        errors.add("PHONON_RECIPROCAL_CONVENTION_UNSUPPORTED")
        return []
    return lattice


def _validate_frequency_policy(payload: dict[str, Any], errors: set[str]) -> None:
    if payload.get("frequency_unit") != FREQUENCY_UNIT:
        errors.add("PHONON_FREQUENCY_UNIT_UNSUPPORTED")
    if payload.get("imaginary_frequency_encoding") != IMAGINARY_FREQUENCY_ENCODING:
        errors.add("PHONON_IMAGINARY_ENCODING_UNSUPPORTED")
    tolerance = payload.get("frequency_zero_tolerance")
    if not _finite_number(tolerance) or not 0 <= float(tolerance) <= 1.0:
        errors.add("PHONON_ZERO_TOLERANCE_INVALID")


def _validate_qpoints(qpoints: list[Any], lattice: list[list[float]], errors: set[str], warnings: set[str]) -> None:
    label_count = 0
    previous_distance = -1.0
    for index, item in enumerate(qpoints):
        if not isinstance(item, dict) or set(item) != _QPOINT_FIELDS:
            errors.add("PHONON_QPOINT_SHAPE_INVALID")
            continue
        if item.get("index") != index or not _nonnegative_int(item.get("segment_index")):
            errors.add("PHONON_QPOINT_INDEX_INVALID")
        coordinates = item.get("coordinates")
        if not isinstance(coordinates, list) or len(coordinates) != 3:
            errors.add("PHONON_QPOINT_SHAPE_INVALID")
        elif any(not _finite_number(value) for value in coordinates):
            errors.add("PHONON_QPOINT_NONFINITE")
        distance = item.get("distance")
        if not _finite_number(distance) or float(distance) < 0:
            errors.add("PHONON_QPOINT_NONFINITE")
        elif float(distance) < previous_distance - 1e-10:
            errors.add("PHONON_QPOINT_DISTANCE_NONMONOTONIC")
        else:
            previous_distance = float(distance)
        label, source_label = item.get("label"), item.get("source_label")
        if label is not None:
            label_count += 1
        if not _valid_label(label) or not _valid_label(source_label) or (label is not None and normalize_high_symmetry_label(label) != label):
            errors.add("PHONON_PATH_LABEL_INVALID")
        if source_label is not None and label == "Γ" and normalize_high_symmetry_label(source_label) == "Γ" and source_label != label:
            warnings.add("PHONON_HIGH_SYMMETRY_LABEL_NORMALIZED")
    if label_count > DEFAULT_PHONON_CAPS["max_labels"]:
        errors.add("PHONON_CAP_EXCEEDED")


def _validate_segments(segments: list[Any], qpoints: list[Any], errors: set[str]) -> None:
    previous_end = -1
    for index, segment in enumerate(segments):
        if not isinstance(segment, dict) or set(segment) != _SEGMENT_FIELDS:
            errors.add("PHONON_PATH_SEGMENT_INVALID")
            continue
        start, end = segment.get("start_qpoint_index"), segment.get("end_qpoint_index")
        if segment.get("segment_index") != index or not _nonnegative_int(start) or not _nonnegative_int(end) or start > end or end >= len(qpoints) or start != previous_end + 1:
            errors.add("PHONON_PATH_SEGMENT_INVALID")
            continue
        if type(segment.get("discontinuous_from_previous")) is not bool or (index == 0 and segment.get("discontinuous_from_previous")):
            errors.add("PHONON_PATH_SEGMENT_INVALID")
        if not _valid_label(segment.get("start_label")) or not _valid_label(segment.get("end_label")):
            errors.add("PHONON_PATH_LABEL_INVALID")
        if qpoints and (
            not isinstance(qpoints[start], dict)
            or not isinstance(qpoints[end], dict)
            or qpoints[start].get("segment_index") != index
            or qpoints[end].get("segment_index") != index
            or qpoints[start].get("label") != segment.get("start_label")
            or qpoints[end].get("label") != segment.get("end_label")
        ):
            errors.add("PHONON_PATH_SEGMENT_INVALID")
        if index > 0 and qpoints and isinstance(qpoints[previous_end], dict) and isinstance(qpoints[start], dict):
            prior_distance = float(qpoints[previous_end].get("distance", math.nan))
            start_distance = float(qpoints[start].get("distance", math.nan))
            if not math.isfinite(prior_distance) or not math.isfinite(start_distance) or abs(start_distance - prior_distance) > 1e-8:
                errors.add("PHONON_QPOINT_DISTANCE_NONMONOTONIC")
            if not segment["discontinuous_from_previous"] and qpoints[start].get("coordinates") != qpoints[previous_end].get("coordinates"):
                errors.add("PHONON_PATH_SEGMENT_INVALID")
        for qpoint_index in range(start + 1, end + 1):
            current = qpoints[qpoint_index]
            if isinstance(current, dict) and current.get("segment_index") != index:
                errors.add("PHONON_PATH_SEGMENT_INVALID")
        previous_end = end
    if segments and previous_end != len(qpoints) - 1:
        errors.add("PHONON_PATH_SEGMENT_INVALID")


def _validate_path_distances(qpoints: list[Any], segments: list[Any], lattice: list[list[float]], errors: set[str]) -> None:
    for segment in segments:
        if not isinstance(segment, dict):
            continue
        start, end = segment.get("start_qpoint_index"), segment.get("end_qpoint_index")
        if not _nonnegative_int(start) or not _nonnegative_int(end) or end >= len(qpoints):
            continue
        for index in range(start + 1, end + 1):
            previous, current = qpoints[index - 1], qpoints[index]
            try:
                expected = reciprocal_path_step(previous["coordinates"], current["coordinates"], lattice)
                actual = float(current["distance"]) - float(previous["distance"])
            except (TypeError, ValueError, KeyError, OverflowError):
                continue
            if abs(actual - expected) > max(1e-8, expected * 1e-8):
                errors.add("PHONON_QPOINT_DISTANCE_NONMONOTONIC")


def _validate_branches(branches: list[Any], qpoint_count: int, errors: set[str], warnings: set[str], tolerance: float) -> None:
    for index, branch in enumerate(branches):
        if not isinstance(branch, dict) or set(branch) != _BRANCH_FIELDS:
            errors.add("PHONON_FREQUENCY_SHAPE_INVALID")
            continue
        if branch.get("branch_index") != index:
            errors.add("PHONON_BRANCH_INDEX_INVALID")
        values = branch.get("frequencies")
        if not isinstance(values, list) or len(values) != qpoint_count:
            errors.add("PHONON_FREQUENCY_SHAPE_INVALID")
            continue
        if any(not _finite_number(value) for value in values):
            errors.add("PHONON_FREQUENCY_NONFINITE")
        elif any(-tolerance <= float(value) < 0 for value in values):
            warnings.add("PHONON_SMALL_IMAGINARY_FREQUENCY")


def _validate_degeneracy(groups: list[Any], qpoint_count: int, branch_count: int, errors: set[str]) -> None:
    seen_members: set[tuple[int, int]] = set()
    previous_key: tuple[int, tuple[int, ...]] | None = None
    for group in groups:
        if not isinstance(group, dict) or set(group) != _DEGENERACY_FIELDS or group.get("source") != "producer":
            errors.add("PHONON_DEGENERACY_GROUP_INVALID")
            continue
        qpoint_index, indices = group.get("qpoint_index"), group.get("branch_indices")
        if not _nonnegative_int(qpoint_index) or qpoint_index >= qpoint_count or not isinstance(indices, list) or len(indices) < 2 or indices != sorted(set(indices)) or any(not _nonnegative_int(item) or item >= branch_count for item in indices):
            errors.add("PHONON_DEGENERACY_GROUP_INVALID")
            continue
        key = (qpoint_index, tuple(indices))
        if previous_key is not None and key <= previous_key:
            errors.add("PHONON_DEGENERACY_GROUP_INVALID")
        if any((qpoint_index, branch) in seen_members for branch in indices):
            errors.add("PHONON_DEGENERACY_GROUP_INVALID")
        seen_members.update((qpoint_index, branch) for branch in indices)
        previous_key = key


def _validate_asr(value: Any, errors: set[str], warnings: set[str]) -> None:
    if not isinstance(value, dict) or set(value) != _ASR_FIELDS or type(value.get("applied")) is not bool or (value.get("applied") and not _safe_optional_text(value.get("method"))) or (not value.get("applied") and value.get("method") is not None):
        errors.add("PHONON_SCHEMA_UNSUPPORTED")
    elif not value.get("applied"):
        warnings.add("PHONON_ACOUSTIC_MODES_NOT_CORRECTED")


def _validate_projected_dos(value: Any, count: int, atom_count: int, species_order: Any, total: list[Any], errors: set[str], warnings: set[str]) -> None:
    if not isinstance(value, list):
        errors.add("PHONON_DOS_SHAPE_INVALID")
        return
    identities: set[tuple[str, Any]] = set()
    projected_values: list[list[float]] = []
    previous_order_key: tuple[int, Any] | None = None
    guarantees_sum = bool(value) and all(isinstance(item, dict) and item.get("source_guarantees_sum") is True for item in value)
    for index, projection in enumerate(value):
        if not isinstance(projection, dict) or set(projection) != _PROJECTION_FIELDS or projection.get("projection_index") != index:
            errors.add("PHONON_PROJECTED_DOS_IDENTITY_INVALID")
            continue
        projection_type = projection.get("projection_type")
        atom_index, species = projection.get("atom_index"), projection.get("species")
        if projection_type == "atom":
            valid_identity = _nonnegative_int(atom_index) and atom_index < atom_count and isinstance(species_order, list) and species == species_order[atom_index]
            identity = ("atom", atom_index)
            order_key = (0, atom_index if _nonnegative_int(atom_index) else -1)
        elif projection_type == "species":
            valid_identity = atom_index is None and isinstance(species, str) and isinstance(species_order, list) and species in species_order
            identity = ("species", species)
            order_key = (1, species if isinstance(species, str) else "")
        else:
            valid_identity = False
            identity = ("invalid", index)
            order_key = (2, index)
        if not valid_identity or type(projection.get("source_guarantees_sum")) is not bool:
            errors.add("PHONON_PROJECTED_DOS_IDENTITY_INVALID")
        if identity in identities:
            errors.add("PHONON_PROJECTED_DOS_DUPLICATE")
        identities.add(identity)
        if previous_order_key is not None and order_key <= previous_order_key:
            errors.add("PHONON_PROJECTED_DOS_IDENTITY_INVALID")
        previous_order_key = order_key
        values = projection.get("values")
        if not isinstance(values, list) or len(values) != count:
            errors.add("PHONON_DOS_SHAPE_INVALID")
        elif any(not _finite_number(item) or float(item) < 0 for item in values):
            errors.add("PHONON_DOS_NONFINITE")
        else:
            projected_values.append([float(item) for item in values])
    if guarantees_sum and len(projected_values) == len(value) and len(total) == count and all(_finite_number(item) for item in total):
        for point in range(count):
            projection_sum = sum(series[point] for series in projected_values)
            if abs(projection_sum - float(total[point])) > max(1e-8, abs(float(total[point])) * 1e-5):
                warnings.add("PHONON_PROJECTED_DOS_SUM_MISMATCH")
                break


def _validate_broadening(value: Any, errors: set[str]) -> None:
    if not isinstance(value, dict) or set(value) != _BROADENING_FIELDS or value.get("method") not in {"none", "gaussian", "source_defined"} or not _safe_optional_text(value.get("source")):
        errors.add("PHONON_SCHEMA_UNSUPPORTED")
        return
    width = value.get("width")
    if value.get("method") == "none":
        if width is not None or value.get("unit") is not None:
            errors.add("PHONON_SCHEMA_UNSUPPORTED")
    elif not _finite_number(width) or float(width) <= 0 or value.get("unit") != FREQUENCY_UNIT:
        errors.add("PHONON_SCHEMA_UNSUPPORTED")


def _validate_integration(value: Any, frequencies: list[Any], total: list[Any], atom_count: int, errors: set[str], warnings: set[str]) -> None:
    if not isinstance(value, dict) or set(value) != _INTEGRATION_FIELDS or value.get("method") != "trapezoidal" or value.get("status") not in {"within_tolerance", "approximate"}:
        errors.add("PHONON_DOS_NORMALIZATION_UNSUPPORTED")
        return
    expected = value.get("expected_mode_count")
    observed = value.get("observed_integral")
    tolerance = value.get("relative_tolerance")
    if expected != atom_count * 3 or not _finite_number(observed) or not _finite_number(tolerance) or not 0 < float(tolerance) <= 0.05:
        errors.add("PHONON_DOS_INTEGRAL_MISMATCH")
        return
    try:
        calculated = trapezoidal_integral(frequencies, total)
    except ValueError:
        return
    if abs(float(observed) - calculated) > max(1e-8, abs(calculated) * 1e-8):
        errors.add("PHONON_DOS_INTEGRAL_MISMATCH")
    relative_error = abs(calculated - float(expected)) / max(float(expected), 1.0)
    if relative_error > float(tolerance):
        errors.add("PHONON_DOS_INTEGRAL_MISMATCH")
    elif relative_error > 1e-10 or value.get("status") == "approximate":
        warnings.add("PHONON_DOS_INTEGRAL_APPROXIMATE")


def _validate_source(value: Any, errors: set[str], warnings: set[str]) -> None:
    if not isinstance(value, dict) or set(value) != _SOURCE_FIELDS:
        errors.add("PHONON_METADATA_LIMIT_EXCEEDED")
        return
    producer = value.get("producer")
    if not _safe_text(producer):
        errors.add("PHONON_METADATA_LIMIT_EXCEEDED")
    elif producer == "unknown":
        warnings.add("PHONON_SOURCE_SOFTWARE_UNKNOWN")
    for key in ("producer_version", "calculation_method", "force_constants_source", "adapter_version"):
        if not _safe_optional_text(value.get(key)):
            errors.add("PHONON_METADATA_LIMIT_EXCEEDED")
    if not _sha256(value.get("input_sha256")):
        errors.add("PHONON_STRUCTURE_IDENTITY_REQUIRED")
    for key in ("supercell_matrix", "primitive_matrix"):
        matrix = value.get(key)
        if matrix is not None and (not isinstance(matrix, list) or len(matrix) != 3 or any(not isinstance(row, list) or len(row) != 3 or any(not _finite_number(item) for item in row) for row in matrix)):
            errors.add("PHONON_METADATA_LIMIT_EXCEEDED")
        elif key == "supercell_matrix" and matrix is not None and any(not isinstance(item, int) or isinstance(item, bool) for row in matrix for item in row):
            errors.add("PHONON_METADATA_LIMIT_EXCEEDED")
    nac = value.get("nac")
    if (
        not isinstance(nac, dict)
        or set(nac) != _NAC_FIELDS
        or type(nac.get("enabled")) is not bool
        or nac.get("direction_policy") not in {None, "source_defined", "explicit"}
        or (nac.get("gamma_direction") is not None and not _triplet(nac.get("gamma_direction")))
        or (nac.get("enabled") and nac.get("direction_policy") is None)
        or (not nac.get("enabled") and (nac.get("gamma_direction") is not None or nac.get("direction_policy") is not None))
        or (nac.get("enabled") and nac.get("direction_policy") == "explicit" and nac.get("gamma_direction") is None)
    ):
        errors.add("PHONON_METADATA_LIMIT_EXCEEDED")
        warnings.add("PHONON_NAC_STATUS_UNKNOWN")
    try:
        if len(stable_phonon_json(value).encode("utf-8")) > DEFAULT_PHONON_CAPS["max_metadata_bytes"]:
            errors.add("PHONON_METADATA_LIMIT_EXCEEDED")
    except (TypeError, ValueError, RecursionError):
        errors.add("PHONON_METADATA_LIMIT_EXCEEDED")


def _validate_warnings(value: Any, errors: set[str], warnings: set[str]) -> None:
    if not isinstance(value, list) or len(value) > DEFAULT_PHONON_CAPS["max_warnings"] or value != sorted(set(value)) or any(item not in PHONON_WARNING_CODES for item in value):
        errors.add("PHONON_METADATA_LIMIT_EXCEEDED")
        return
    warnings.update(value)


def _validate_security(value: Any, errors: set[str]) -> None:
    if not isinstance(value, dict) or set(value) != set(_SECURITY_FLAGS) or value != _SECURITY_FLAGS:
        errors.add("PHONON_EXTERNAL_REFERENCE_FORBIDDEN")


def _validate_raw_size(payload: Any, raw_size_bytes: int | None, errors: set[str]) -> None:
    if raw_size_bytes is None:
        try:
            raw_size_bytes = len(stable_phonon_json(payload).encode("utf-8"))
        except (TypeError, ValueError, RecursionError):
            errors.add("PHONON_FREQUENCY_NONFINITE")
            return
    if raw_size_bytes > DEFAULT_PHONON_CAPS["max_artifact_bytes"]:
        errors.add("PHONON_CAP_EXCEEDED")


def _scan_inert_content(value: Any, errors: set[str]) -> None:
    queue: list[tuple[Any, str, int]] = [(value, "", 0)]
    visited = 0
    while queue:
        item, key, depth = queue.pop()
        visited += 1
        if visited > DEFAULT_PHONON_CAPS["max_visited_nodes"] or depth > DEFAULT_PHONON_CAPS["max_nesting_depth"]:
            errors.add("PHONON_CAP_EXCEEDED")
            return
        if key.lower() in _FORBIDDEN_KEYS:
            errors.add("PHONON_EXTERNAL_REFERENCE_FORBIDDEN")
        if isinstance(item, dict):
            queue.extend((child, str(child_key), depth + 1) for child_key, child in item.items())
        elif isinstance(item, list):
            queue.extend((child, key, depth + 1) for child in item)
        elif isinstance(item, str):
            lowered = item.lower()
            if any(marker in lowered for marker in _FORBIDDEN_MARKERS) or any(pattern.search(item) for pattern in _PRIVATE_PATH_PATTERNS):
                errors.add("PHONON_EXTERNAL_REFERENCE_FORBIDDEN")


def _result(
    errors: set[str], warnings: set[str], *, atom_count: int = 0, qpoints: int = 0,
    branches: int = 0, dos_points: int = 0, projections: int = 0,
) -> PhononValidationResult:
    return PhononValidationResult(
        valid=not errors,
        errors=tuple(sorted(errors)),
        warnings=tuple(sorted(warnings)),
        caps=dict(DEFAULT_PHONON_CAPS),
        atom_count=atom_count,
        qpoint_count=qpoints,
        branch_count=branches,
        dos_point_count=dos_points,
        projected_series_count=projections,
    )


def _finite_number(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(float(value)) and abs(float(value)) <= DEFAULT_PHONON_CAPS["max_numeric_magnitude"]


def _nonnegative_int(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool) and value >= 0


def _positive_int(value: Any) -> bool:
    return _nonnegative_int(value) and value > 0


def _triplet(value: Any) -> bool:
    return isinstance(value, list) and len(value) == 3 and all(_finite_number(item) for item in value)


def _sha256(value: Any) -> bool:
    return isinstance(value, str) and re.fullmatch(r"[0-9a-f]{64}", value) is not None


def _safe_text(value: Any) -> bool:
    return isinstance(value, str) and 0 < len(value) <= 128 and _SAFE_TEXT_RE.fullmatch(value) is not None


def _safe_optional_text(value: Any) -> bool:
    return value is None or _safe_text(value)


def _valid_label(value: Any) -> bool:
    if value is None:
        return True
    return isinstance(value, str) and 0 < len(value) <= DEFAULT_PHONON_CAPS["max_label_length"] and "<" not in value and ">" not in value and not any(marker in value.lower() for marker in _FORBIDDEN_MARKERS)


def _product_exceeds(a: int, b: int, cap: int) -> bool:
    return min(a, b) < 0 or (a != 0 and b > cap // a)


def _validated_matrix(value: Any) -> list[list[float]]:
    if not isinstance(value, list) or len(value) != 3 or any(not _triplet(row) for row in value):
        raise ValueError("PHONON_RECIPROCAL_CONVENTION_UNSUPPORTED")
    return [[float(component) for component in row] for row in value]


def _determinant(matrix: list[list[float]]) -> float:
    a, b, c = matrix
    return a[0] * (b[1] * c[2] - b[2] * c[1]) - a[1] * (b[0] * c[2] - b[2] * c[0]) + a[2] * (b[0] * c[1] - b[1] * c[0])


def _inverse(matrix: list[list[float]], determinant: float) -> list[list[float]]:
    a, b, c = matrix
    return [
        [(b[1] * c[2] - b[2] * c[1]) / determinant, (a[2] * c[1] - a[1] * c[2]) / determinant, (a[1] * b[2] - a[2] * b[1]) / determinant],
        [(b[2] * c[0] - b[0] * c[2]) / determinant, (a[0] * c[2] - a[2] * c[0]) / determinant, (a[2] * b[0] - a[0] * b[2]) / determinant],
        [(b[0] * c[1] - b[1] * c[0]) / determinant, (a[1] * c[0] - a[0] * c[1]) / determinant, (a[0] * b[1] - a[1] * b[0]) / determinant],
    ]


def _frobenius(matrix: list[list[float]]) -> float:
    return math.sqrt(sum(component * component for row in matrix for component in row))
