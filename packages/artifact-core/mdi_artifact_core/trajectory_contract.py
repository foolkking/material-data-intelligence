from __future__ import annotations

import hashlib
import json
import math
import re
from dataclasses import dataclass
from typing import Any


TRAJECTORY_SCHEMA_VERSION = "phase10g.trajectory.v1"
TRAJECTORY_FRAME_SCHEMA_VERSION = "phase10g.trajectory_frame.v1"
TRAJECTORY_SUMMARY_SCHEMA_VERSION = "phase10g.trajectory_summary.v1"
TRAJECTORY_MANIFEST_SCHEMA_VERSION = "phase10g.trajectory_manifest.v1"

TRAJECTORY_KINDS = frozenset(
    {"molecular_dynamics", "geometry_optimization", "structure_sequence", "unknown_static_sequence"}
)
COORDINATE_MODES = frozenset({"fractional", "cartesian"})
POSITION_WRAPPING_MODES = frozenset({"wrapped", "unwrapped", "unknown"})
LATTICE_MODES = frozenset({"fixed", "variable"})
TIME_UNITS = frozenset({"femtosecond", "picosecond"})

DEFAULT_TRAJECTORY_CAPS: dict[str, int] = {
    "max_atoms": 4096,
    "max_frames": 10_000,
    "max_total_coordinate_values": 12_000_000,
    "max_json_bytes": 64_000_000,
    "max_metadata_bytes": 16_384,
    "max_frame_metadata_bytes": 4096,
    "max_property_arrays": 2,
    "max_property_keys": 6,
    "max_label_length": 128,
    "max_warnings": 32,
    "max_provenance_fields": 6,
    "max_numeric_magnitude": 1_000_000_000_000,
}

FUTURE_INTERACTIVE_CAPS = {"max_atoms": 256, "max_frames": 200}
FUTURE_DEGRADED_CAPS = {"max_atoms": 2048, "max_frames": 2000}
LATTICE_RELATIVE_DETERMINANT_THRESHOLD = 1e-12
LATTICE_MAX_CONDITION_NUMBER = 1e8
WRAPPED_COORDINATE_TOLERANCE = 1e-9

_TOP_LEVEL_FIELDS = {
    "schema_version", "trajectory_id", "kind", "coordinate_mode", "position_wrapping",
    "lattice_mode", "atom_identity_mode", "periodic_boundary", "units", "time", "atoms",
    "fixed_lattice", "frames", "properties", "metadata", "provenance", "warnings", "security",
}
_FRAME_FIELDS = {
    "schema_version", "frame_index", "atom_ids", "step", "time", "lattice", "positions",
    "velocities", "forces", "energy", "temperature", "metadata",
}
_PROPERTY_FIELDS = {"positions", "velocities", "forces", "energy", "temperature", "stress"}
_PROVENANCE_FIELDS = {
    "source_format", "source_software", "source_version", "parser_version", "input_sha256",
    "created_by_tool",
}
_SECURITY_FLAGS = {
    "contains_javascript": False,
    "contains_html": False,
    "external_urls_allowed": False,
    "remote_frames_allowed": False,
    "executable_content_allowed": False,
}
_FORBIDDEN_KEYS = {
    "callback", "callbacks", "code", "eval", "function", "html", "iframe", "module", "script",
    "shader", "src", "texture", "url", "urls", "__proto__", "constructor", "prototype",
}
_FORBIDDEN_MARKERS = (
    "http://", "https://", "javascript:", "<script", "<iframe", "eval(", "new function",
    "file://", "data:text/html",
)
_PRIVATE_PATH_PATTERNS = (re.compile(r"^[a-zA-Z]:[\\/]"), re.compile(r"^/(?:home|users|root|etc)/"))


@dataclass(frozen=True)
class TrajectoryValidationResult:
    valid: bool
    errors: tuple[str, ...]
    warnings: tuple[str, ...]
    caps: dict[str, int]
    frame_count: int
    atom_count: int

    def as_dict(self) -> dict[str, Any]:
        return {
            "valid": self.valid,
            "errors": list(self.errors),
            "warnings": list(self.warnings),
            "caps": dict(self.caps),
            "frame_count": self.frame_count,
            "atom_count": self.atom_count,
        }


def stable_trajectory_json(payload: Any) -> str:
    return json.dumps(payload, ensure_ascii=True, allow_nan=False, sort_keys=True, separators=(",", ":"))


def canonical_trajectory_id(payload: dict[str, Any]) -> str:
    identity_payload = {key: value for key, value in payload.items() if key != "trajectory_id"}
    digest = hashlib.sha256(stable_trajectory_json(identity_payload).encode("utf-8")).hexdigest()
    return f"sha256:{digest}"


def validate_trajectory(payload: Any, *, raw_size_bytes: int | None = None) -> TrajectoryValidationResult:
    errors: set[str] = set()
    warnings: set[str] = set()
    if not isinstance(payload, dict):
        return _result({"TRAJECTORY_SCHEMA_INVALID"}, set(), 0, 0)

    if set(payload) != _TOP_LEVEL_FIELDS:
        errors.add("TRAJECTORY_TOP_LEVEL_FIELDS_INVALID")
    if payload.get("schema_version") != TRAJECTORY_SCHEMA_VERSION:
        errors.add("TRAJECTORY_SCHEMA_UNSUPPORTED")
    if payload.get("kind") not in TRAJECTORY_KINDS:
        errors.add("TRAJECTORY_KIND_UNSUPPORTED")
    if payload.get("coordinate_mode") not in COORDINATE_MODES:
        errors.add("TRAJECTORY_COORDINATE_MODE_INVALID")
    if payload.get("position_wrapping") not in POSITION_WRAPPING_MODES:
        errors.add("TRAJECTORY_POSITION_WRAPPING_INVALID")
    elif payload.get("position_wrapping") == "unknown":
        warnings.add("TRAJECTORY_WRAPPING_UNKNOWN")
    if payload.get("lattice_mode") not in LATTICE_MODES:
        errors.add("TRAJECTORY_LATTICE_MODE_INVALID")
    if payload.get("atom_identity_mode") != "stable_index":
        errors.add("TRAJECTORY_ATOM_IDENTITY_MODE_INVALID")
    if payload.get("periodic_boundary") not in ([True, True, True], [False, False, False]):
        errors.add("TRAJECTORY_PERIODIC_BOUNDARY_INVALID")

    if raw_size_bytes is None:
        try:
            raw_size_bytes = len(stable_trajectory_json(payload).encode("utf-8"))
        except (TypeError, ValueError, RecursionError):
            errors.add("TRAJECTORY_NONFINITE_VALUE")
    if raw_size_bytes is not None and raw_size_bytes > DEFAULT_TRAJECTORY_CAPS["max_json_bytes"]:
        errors.add("TRAJECTORY_BYTE_LIMIT_EXCEEDED")

    _validate_security(payload.get("security"), errors)
    _scan_inert_content(payload, errors)
    _validate_units(payload.get("units"), payload.get("coordinate_mode"), errors)
    _validate_time_contract(payload.get("time"), payload.get("kind"), errors)
    atom_count, atom_ids = _validate_atoms(payload.get("atoms"), errors)
    frames = payload.get("frames")
    frame_count = len(frames) if isinstance(frames, list) else 0
    if not isinstance(frames, list) or not frames:
        errors.add("TRAJECTORY_EMPTY")
        frames = []
    if atom_count > DEFAULT_TRAJECTORY_CAPS["max_atoms"]:
        errors.add("TRAJECTORY_ATOM_LIMIT_EXCEEDED")
    if frame_count > DEFAULT_TRAJECTORY_CAPS["max_frames"]:
        errors.add("TRAJECTORY_FRAME_LIMIT_EXCEEDED")
    if _product_exceeds(frame_count, atom_count, 3, DEFAULT_TRAJECTORY_CAPS["max_total_coordinate_values"]):
        errors.add("TRAJECTORY_COORDINATE_VALUE_LIMIT_EXCEEDED")

    properties = _validate_properties(payload.get("properties"), errors)
    _validate_lattice_policy(payload.get("fixed_lattice"), payload.get("lattice_mode"), errors)
    _validate_frames(
        frames, atom_count, atom_ids, payload.get("kind"), payload.get("coordinate_mode"),
        payload.get("position_wrapping"), payload.get("lattice_mode"), properties, errors, warnings,
    )
    _validate_flat_metadata(payload.get("metadata"), DEFAULT_TRAJECTORY_CAPS["max_metadata_bytes"], errors)
    _validate_provenance(payload.get("provenance"), errors, warnings)
    _validate_warning_codes(payload.get("warnings"), errors, warnings)

    trajectory_id = payload.get("trajectory_id")
    try:
        expected_id = canonical_trajectory_id(payload)
    except (TypeError, ValueError, RecursionError):
        expected_id = None
    if not isinstance(trajectory_id, str) or trajectory_id != expected_id:
        errors.add("TRAJECTORY_ID_INVALID")
    return _result(errors, warnings, frame_count, atom_count)


def trajectory_summary(payload: dict[str, Any]) -> dict[str, Any]:
    result = validate_trajectory(payload)
    if not result.valid:
        raise ValueError("trajectory must validate before summary generation")
    frames = payload["frames"]
    available = [key for key in ("positions", "velocities", "forces", "energy", "temperature") if payload["properties"][key]]
    times = [frame["time"] for frame in frames if frame["time"] is not None]
    return {
        "schema_version": TRAJECTORY_SUMMARY_SCHEMA_VERSION,
        "trajectory_id": payload["trajectory_id"],
        "kind": payload["kind"],
        "frames": len(frames),
        "atoms": payload["atoms"]["count"],
        "coordinate_mode": payload["coordinate_mode"],
        "position_wrapping": payload["position_wrapping"],
        "lattice_mode": payload["lattice_mode"],
        "periodic_boundary": payload["periodic_boundary"],
        "time_start": times[0] if times else None,
        "time_end": times[-1] if times else None,
        "time_unit": payload["time"]["unit"],
        "available_properties": available,
        "warnings": list(result.warnings),
    }


def validate_trajectory_summary(payload: Any) -> TrajectoryValidationResult:
    errors: set[str] = set()
    if not isinstance(payload, dict):
        return _result({"TRAJECTORY_SUMMARY_INVALID"}, set(), 0, 0)
    fields = {
        "schema_version", "trajectory_id", "kind", "frames", "atoms", "coordinate_mode",
        "position_wrapping", "lattice_mode", "periodic_boundary", "time_start", "time_end",
        "time_unit", "available_properties", "warnings",
    }
    if set(payload) != fields:
        errors.add("TRAJECTORY_SUMMARY_FIELDS_INVALID")
    if payload.get("schema_version") != TRAJECTORY_SUMMARY_SCHEMA_VERSION:
        errors.add("TRAJECTORY_SUMMARY_SCHEMA_UNSUPPORTED")
    if payload.get("kind") not in TRAJECTORY_KINDS or payload.get("coordinate_mode") not in COORDINATE_MODES:
        errors.add("TRAJECTORY_SUMMARY_ENUM_INVALID")
    if payload.get("position_wrapping") not in POSITION_WRAPPING_MODES or payload.get("lattice_mode") not in LATTICE_MODES:
        errors.add("TRAJECTORY_SUMMARY_ENUM_INVALID")
    if payload.get("periodic_boundary") not in ([True, True, True], [False, False, False]):
        errors.add("TRAJECTORY_SUMMARY_ENUM_INVALID")
    frames = payload.get("frames")
    atoms = payload.get("atoms")
    if not _positive_int(frames) or not _positive_int(atoms):
        errors.add("TRAJECTORY_SUMMARY_COUNT_INVALID")
    properties = payload.get("available_properties")
    allowed_properties = ["positions", "velocities", "forces", "energy", "temperature"]
    if not isinstance(properties, list) or properties != [item for item in allowed_properties if item in properties]:
        errors.add("TRAJECTORY_SUMMARY_PROPERTIES_INVALID")
    start, end = payload.get("time_start"), payload.get("time_end")
    if (start is None) != (end is None) or (start is not None and (not _finite_number(start) or not _finite_number(end) or end < start)):
        errors.add("TRAJECTORY_SUMMARY_TIME_INVALID")
    if payload.get("time_unit") is not None and payload.get("time_unit") not in TIME_UNITS:
        errors.add("TRAJECTORY_TIME_UNIT_UNSUPPORTED")
    if start is not None and payload.get("time_unit") not in TIME_UNITS:
        errors.add("TRAJECTORY_TIME_UNIT_UNSUPPORTED")
    _validate_warning_codes(payload.get("warnings"), errors, set())
    _scan_inert_content(payload, errors)
    return _result(errors, set(), int(frames) if _positive_int(frames) else 0, int(atoms) if _positive_int(atoms) else 0)


def validate_trajectory_manifest(payload: Any) -> TrajectoryValidationResult:
    errors: set[str] = set()
    if not isinstance(payload, dict):
        return _result({"TRAJECTORY_MANIFEST_INVALID"}, set(), 0, 0)
    expected_fields = {
        "schema_version", "trajectory_schema_version", "frame_schema_version", "summary_schema_version",
        "trajectory_id", "frame_count", "atom_count", "artifacts", "security",
    }
    if set(payload) != expected_fields:
        errors.add("TRAJECTORY_MANIFEST_FIELDS_INVALID")
    if payload.get("schema_version") != TRAJECTORY_MANIFEST_SCHEMA_VERSION:
        errors.add("TRAJECTORY_MANIFEST_SCHEMA_UNSUPPORTED")
    if payload.get("trajectory_schema_version") != TRAJECTORY_SCHEMA_VERSION:
        errors.add("TRAJECTORY_MANIFEST_SCHEMA_MISMATCH")
    if payload.get("frame_schema_version") != TRAJECTORY_FRAME_SCHEMA_VERSION:
        errors.add("TRAJECTORY_MANIFEST_SCHEMA_MISMATCH")
    if payload.get("summary_schema_version") != TRAJECTORY_SUMMARY_SCHEMA_VERSION:
        errors.add("TRAJECTORY_MANIFEST_SCHEMA_MISMATCH")
    artifacts = payload.get("artifacts")
    expected_names = ["trajectory.json", "trajectory_summary.json"]
    if not isinstance(artifacts, list) or [item.get("name") for item in artifacts if isinstance(item, dict)] != expected_names:
        errors.add("TRAJECTORY_MANIFEST_ARTIFACT_ORDER_INVALID")
    else:
        for item in artifacts:
            if set(item) != {"name", "media_type", "bytes", "sha256"}:
                errors.add("TRAJECTORY_MANIFEST_ARTIFACT_INVALID")
            if item.get("media_type") != "application/json" or not _positive_int(item.get("bytes")):
                errors.add("TRAJECTORY_MANIFEST_ARTIFACT_INVALID")
            if not _sha256(item.get("sha256")):
                errors.add("TRAJECTORY_MANIFEST_ARTIFACT_INVALID")
    if not isinstance(payload.get("trajectory_id"), str) or not re.fullmatch(r"sha256:[0-9a-f]{64}", payload["trajectory_id"]):
        errors.add("TRAJECTORY_MANIFEST_ID_INVALID")
    if not _positive_int(payload.get("frame_count")) or not _positive_int(payload.get("atom_count")):
        errors.add("TRAJECTORY_MANIFEST_COUNT_INVALID")
    _validate_security(payload.get("security"), errors)
    _scan_inert_content(payload, errors)
    frame_count = payload.get("frame_count") if _positive_int(payload.get("frame_count")) else 0
    atom_count = payload.get("atom_count") if _positive_int(payload.get("atom_count")) else 0
    return _result(errors, set(), frame_count, atom_count)


def _validate_atoms(atoms: Any, errors: set[str]) -> tuple[int, tuple[int, ...]]:
    if not isinstance(atoms, dict) or set(atoms) != {"count", "records"}:
        errors.add("TRAJECTORY_ATOMS_INVALID")
        return 0, ()
    count = atoms.get("count")
    records = atoms.get("records")
    if not _positive_int(count) or not isinstance(records, list) or len(records) != count:
        errors.add("TRAJECTORY_ATOM_COUNT_MISMATCH")
        return int(count) if _positive_int(count) else 0, ()
    ids: list[int] = []
    labels: set[str] = set()
    for index, atom in enumerate(records):
        if not isinstance(atom, dict) or set(atom) != {"atom_id", "species", "label", "occupancy"}:
            errors.add("TRAJECTORY_ATOM_RECORD_INVALID")
            continue
        if atom.get("atom_id") != index:
            errors.add("TRAJECTORY_ATOM_ID_INVALID")
        else:
            ids.append(index)
        species = atom.get("species")
        label = atom.get("label")
        if not isinstance(species, str) or not species or len(species) > 16:
            errors.add("TRAJECTORY_SPECIES_INVALID")
        if not isinstance(label, str) or not label or len(label) > DEFAULT_TRAJECTORY_CAPS["max_label_length"]:
            errors.add("TRAJECTORY_LABEL_INVALID")
        elif label in labels:
            errors.add("TRAJECTORY_LABEL_DUPLICATE")
        else:
            labels.add(label)
        if atom.get("occupancy") != 1.0:
            errors.add("TRAJECTORY_PARTIAL_OCCUPANCY_UNSUPPORTED")
    return count, tuple(ids)


def _validate_frames(
    frames: list[Any], atom_count: int, atom_ids: tuple[int, ...], kind: Any, coordinate_mode: Any,
    wrapping: Any, lattice_mode: Any, properties: dict[str, bool], errors: set[str], warnings: set[str],
) -> None:
    indices = [frame.get("frame_index") for frame in frames if isinstance(frame, dict)]
    integer_indices = [item for item in indices if isinstance(item, int) and not isinstance(item, bool)]
    if len(integer_indices) != len(set(integer_indices)):
        errors.add("TRAJECTORY_FRAME_INDEX_DUPLICATE")
    last_step: int | None = None
    last_time: float | None = None
    for index, frame in enumerate(frames):
        if not isinstance(frame, dict) or set(frame) != _FRAME_FIELDS:
            errors.add("TRAJECTORY_FRAME_FIELDS_INVALID")
            continue
        if frame.get("schema_version") != TRAJECTORY_FRAME_SCHEMA_VERSION:
            errors.add("TRAJECTORY_FRAME_SCHEMA_UNSUPPORTED")
        if frame.get("frame_index") != index:
            errors.add("TRAJECTORY_FRAME_INDEX_INVALID")
        if frame.get("atom_ids") != list(atom_ids):
            errors.add("TRAJECTORY_SPECIES_MISMATCH")
        _validate_frame_lattice(frame.get("lattice"), lattice_mode, errors)
        _validate_vector_array(frame.get("positions"), atom_count, "TRAJECTORY_POSITION", errors)
        if wrapping == "wrapped" and coordinate_mode == "fractional" and isinstance(frame.get("positions"), list):
            for vector in frame["positions"]:
                if _triplet(vector) and any(value < -WRAPPED_COORDINATE_TOLERANCE or value >= 1 + WRAPPED_COORDINATE_TOLERANCE for value in vector):
                    errors.add("TRAJECTORY_WRAPPED_POSITION_OUT_OF_RANGE")
        for name, prefix in (("velocities", "TRAJECTORY_VELOCITY"), ("forces", "TRAJECTORY_FORCE")):
            present = frame.get(name) is not None
            if present != properties.get(name, False):
                errors.add("TRAJECTORY_PROPERTY_AVAILABILITY_INCONSISTENT")
            if present:
                _validate_vector_array(frame[name], atom_count, prefix, errors)
        _validate_energy(frame.get("energy"), properties.get("energy", False), errors)
        _validate_temperature(frame.get("temperature"), properties.get("temperature", False), errors)
        step = frame.get("step")
        if step is not None and (not isinstance(step, int) or isinstance(step, bool) or step < 0):
            errors.add("TRAJECTORY_STEP_INVALID")
        elif step is not None and last_step is not None and step < last_step:
            errors.add("TRAJECTORY_STEP_NONMONOTONIC")
        elif step is not None:
            last_step = step
        time = frame.get("time")
        if time is not None and not _finite_number(time):
            errors.add("TRAJECTORY_TIME_INVALID")
        elif time is not None and last_time is not None and time < last_time:
            errors.add("TRAJECTORY_TIME_NONMONOTONIC")
        elif time is not None:
            last_time = float(time)
        if kind == "molecular_dynamics" and time is None:
            errors.add("TRAJECTORY_TIME_MISSING")
        if kind == "molecular_dynamics" and len(frames) < 2:
            errors.add("TRAJECTORY_MD_FRAME_COUNT_INVALID")
        if kind == "geometry_optimization" and step is None:
            warnings.add("TRAJECTORY_STEP_MISSING")
        _validate_flat_metadata(frame.get("metadata"), DEFAULT_TRAJECTORY_CAPS["max_frame_metadata_bytes"], errors)


def _validate_properties(value: Any, errors: set[str]) -> dict[str, bool]:
    if not isinstance(value, dict) or set(value) != _PROPERTY_FIELDS or any(type(flag) is not bool for flag in value.values()):
        errors.add("TRAJECTORY_PROPERTIES_INVALID")
        return {key: False for key in _PROPERTY_FIELDS}
    if value.get("positions") is not True:
        errors.add("TRAJECTORY_POSITIONS_REQUIRED")
    if value.get("stress") is not False:
        errors.add("TRAJECTORY_STRESS_DEFERRED")
    if sum(bool(value.get(key)) for key in ("velocities", "forces")) > DEFAULT_TRAJECTORY_CAPS["max_property_arrays"]:
        errors.add("TRAJECTORY_PROPERTY_LIMIT_EXCEEDED")
    return value


def _validate_units(units: Any, coordinate_mode: Any, errors: set[str]) -> None:
    expected = {
        "positions": "fractional" if coordinate_mode == "fractional" else "angstrom",
        "velocities": "angstrom_per_femtosecond", "forces": "electronvolt_per_angstrom",
        "energy": "electronvolt", "temperature": "kelvin",
    }
    if units != expected:
        errors.add("TRAJECTORY_UNITS_INVALID")


def _validate_time_contract(value: Any, kind: Any, errors: set[str]) -> None:
    if not isinstance(value, dict) or set(value) != {"unit", "origin"}:
        errors.add("TRAJECTORY_TIME_CONTRACT_INVALID")
        return
    unit = value.get("unit")
    if kind == "molecular_dynamics" and unit not in TIME_UNITS:
        errors.add("TRAJECTORY_TIME_UNIT_UNSUPPORTED")
    elif unit is not None and unit not in TIME_UNITS:
        errors.add("TRAJECTORY_TIME_UNIT_UNSUPPORTED")
    if not _finite_number(value.get("origin")):
        errors.add("TRAJECTORY_TIME_ORIGIN_INVALID")


def _validate_lattice_policy(lattice: Any, mode: Any, errors: set[str]) -> None:
    if mode == "fixed":
        _validate_lattice(lattice, errors)
    elif mode == "variable" and lattice is not None:
        errors.add("TRAJECTORY_LATTICE_UNEXPECTED")


def _validate_frame_lattice(lattice: Any, mode: Any, errors: set[str]) -> None:
    if mode == "fixed" and lattice is not None:
        errors.add("TRAJECTORY_LATTICE_UNEXPECTED")
    elif mode == "variable":
        if lattice is None:
            errors.add("TRAJECTORY_LATTICE_REQUIRED")
        else:
            _validate_lattice(lattice, errors)


def _validate_lattice(value: Any, errors: set[str]) -> None:
    if not isinstance(value, list) or len(value) != 3 or any(not _triplet(row) for row in value):
        errors.add("TRAJECTORY_LATTICE_INVALID")
        return
    if any(abs(float(component)) > DEFAULT_TRAJECTORY_CAPS["max_numeric_magnitude"] for row in value for component in row):
        errors.add("TRAJECTORY_LATTICE_MAGNITUDE_EXCEEDED")
        return
    rows = [[float(component) for component in row] for row in value]
    scale = max(math.sqrt(sum(component * component for component in row)) for row in rows)
    determinant = _determinant(rows)
    if scale == 0 or abs(determinant) <= LATTICE_RELATIVE_DETERMINANT_THRESHOLD * scale**3:
        errors.add("TRAJECTORY_LATTICE_SINGULAR")
        return
    inverse = _inverse(rows, determinant)
    norm = math.sqrt(sum(component * component for row in rows for component in row))
    inverse_norm = math.sqrt(sum(component * component for row in inverse for component in row))
    if norm * inverse_norm > LATTICE_MAX_CONDITION_NUMBER:
        errors.add("TRAJECTORY_LATTICE_ILL_CONDITIONED")


def _validate_vector_array(value: Any, count: int, prefix: str, errors: set[str]) -> None:
    if isinstance(value, list) and len(value) != count:
        errors.add("TRAJECTORY_ATOM_COUNT_MISMATCH")
    if not isinstance(value, list) or len(value) != count or any(not _triplet(vector) for vector in value):
        errors.add(f"{prefix}_SHAPE_INVALID")
        return
    if any(abs(float(component)) > DEFAULT_TRAJECTORY_CAPS["max_numeric_magnitude"] for vector in value for component in vector):
        errors.add(f"{prefix}_MAGNITUDE_EXCEEDED")


def _validate_energy(value: Any, required: bool, errors: set[str]) -> None:
    if (value is not None) != required:
        errors.add("TRAJECTORY_PROPERTY_AVAILABILITY_INCONSISTENT")
        return
    if value is None:
        return
    if not isinstance(value, dict) or set(value) != {"potential", "kinetic", "total", "free", "unit", "scope"}:
        errors.add("TRAJECTORY_ENERGY_INVALID")
        return
    if value.get("unit") != "electronvolt" or value.get("scope") != "total_system":
        errors.add("TRAJECTORY_ENERGY_INVALID")
    numbers = [value.get(key) for key in ("potential", "kinetic", "total", "free")]
    if not any(item is not None for item in numbers) or any(item is not None and not _finite_number(item) for item in numbers):
        errors.add("TRAJECTORY_ENERGY_INVALID")


def _validate_temperature(value: Any, required: bool, errors: set[str]) -> None:
    if (value is not None) != required:
        errors.add("TRAJECTORY_PROPERTY_AVAILABILITY_INCONSISTENT")
    elif value is not None and (not _finite_number(value) or float(value) < -1e-9):
        errors.add("TRAJECTORY_TEMPERATURE_INVALID")


def _validate_security(value: Any, errors: set[str]) -> None:
    if not isinstance(value, dict) or set(value) != set(_SECURITY_FLAGS) or value != _SECURITY_FLAGS:
        errors.add("TRAJECTORY_SECURITY_INVALID")


def _validate_flat_metadata(value: Any, byte_cap: int, errors: set[str]) -> None:
    if not isinstance(value, dict) or len(value) > DEFAULT_TRAJECTORY_CAPS["max_property_keys"]:
        errors.add("TRAJECTORY_METADATA_LIMIT_EXCEEDED")
        return
    if any(not isinstance(key, str) or not key or len(key) > 64 for key in value):
        errors.add("TRAJECTORY_METADATA_INVALID")
    for item in value.values():
        if not (item is None or type(item) in {str, int, float, bool} or (isinstance(item, list) and all(isinstance(x, str) for x in item))):
            errors.add("TRAJECTORY_METADATA_INVALID")
    try:
        if len(stable_trajectory_json(value).encode("utf-8")) > byte_cap:
            errors.add("TRAJECTORY_METADATA_LIMIT_EXCEEDED")
    except (TypeError, ValueError, RecursionError):
        errors.add("TRAJECTORY_METADATA_INVALID")


def _validate_provenance(value: Any, errors: set[str], warnings: set[str]) -> None:
    if not isinstance(value, dict) or set(value) != _PROVENANCE_FIELDS:
        errors.add("TRAJECTORY_PROVENANCE_INVALID")
        return
    if len(value) > DEFAULT_TRAJECTORY_CAPS["max_provenance_fields"]:
        errors.add("TRAJECTORY_PROVENANCE_INVALID")
    if not isinstance(value.get("source_format"), str) or not value["source_format"]:
        errors.add("TRAJECTORY_PROVENANCE_INVALID")
    if value.get("source_software") == "unknown":
        warnings.add("TRAJECTORY_SOURCE_SOFTWARE_UNKNOWN")
    if not _sha256(value.get("input_sha256")):
        errors.add("TRAJECTORY_PROVENANCE_INVALID")
    for key in ("source_software", "source_version", "parser_version", "created_by_tool"):
        if value.get(key) is not None and not isinstance(value.get(key), str):
            errors.add("TRAJECTORY_PROVENANCE_INVALID")


def _validate_warning_codes(value: Any, errors: set[str], warnings: set[str]) -> None:
    allowed = {
        "TRAJECTORY_STEP_MISSING", "TRAJECTORY_WRAPPING_UNKNOWN", "TRAJECTORY_SOURCE_SOFTWARE_UNKNOWN",
    }
    if (
        not isinstance(value, list)
        or len(value) > DEFAULT_TRAJECTORY_CAPS["max_warnings"]
        or any(item not in allowed for item in value)
        or value != sorted(set(value))
    ):
        errors.add("TRAJECTORY_WARNING_INVALID")
        return
    warnings.update(value)


def _scan_inert_content(
    value: Any,
    errors: set[str],
    *,
    key: str = "",
    depth: int = 0,
    budget: list[int] | None = None,
) -> None:
    if budget is None:
        budget = [10_000]
    budget[0] -= 1
    if budget[0] < 0 or depth > 8:
        errors.add("TRAJECTORY_NESTING_LIMIT_EXCEEDED")
        return
    if key.lower() in _FORBIDDEN_KEYS:
        errors.add("TRAJECTORY_EXECUTABLE_FIELD_FORBIDDEN")
    if isinstance(value, dict):
        for child_key, child in value.items():
            _scan_inert_content(child, errors, key=str(child_key), depth=depth + 1, budget=budget)
    elif isinstance(value, list):
        for child in value:
            _scan_inert_content(child, errors, key=key, depth=depth + 1, budget=budget)
    elif isinstance(value, str):
        lowered = value.lower()
        if any(marker in lowered for marker in _FORBIDDEN_MARKERS):
            errors.add("TRAJECTORY_EXTERNAL_REFERENCE_FORBIDDEN")
        if any(pattern.search(value) for pattern in _PRIVATE_PATH_PATTERNS):
            errors.add("TRAJECTORY_PRIVATE_PATH_FORBIDDEN")


def _result(errors: set[str], warnings: set[str], frame_count: int, atom_count: int) -> TrajectoryValidationResult:
    return TrajectoryValidationResult(
        valid=not errors, errors=tuple(sorted(errors)), warnings=tuple(sorted(warnings)),
        caps=dict(DEFAULT_TRAJECTORY_CAPS), frame_count=frame_count, atom_count=atom_count,
    )


def _finite_number(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(float(value))


def _triplet(value: Any) -> bool:
    return isinstance(value, list) and len(value) == 3 and all(_finite_number(item) for item in value)


def _positive_int(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool) and value > 0


def _sha256(value: Any) -> bool:
    return isinstance(value, str) and re.fullmatch(r"[0-9a-f]{64}", value) is not None


def _product_exceeds(a: int, b: int, c: int, cap: int) -> bool:
    if min(a, b, c) < 0:
        return True
    return a != 0 and (b > cap // a or c > cap // (a * b))


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
