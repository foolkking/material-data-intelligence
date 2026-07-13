from __future__ import annotations

import hashlib
import json
import math
import re
import shlex
from dataclasses import dataclass
from pathlib import Path
from time import perf_counter
from typing import Any, Callable, TextIO

from mdi_artifact_core import (
    DEFAULT_TRAJECTORY_CAPS,
    TRAJECTORY_FRAME_SCHEMA_VERSION,
    TRAJECTORY_SCHEMA_VERSION,
    canonical_trajectory_id,
    stable_trajectory_json,
    validate_trajectory,
)


TRAJECTORY_PARSE_REPORT_SCHEMA_VERSION = "phase10g.trajectory_parse_report.v1"
TRAJECTORY_PARSER_VERSION = "1.0.0"
MAX_INPUT_BYTES = DEFAULT_TRAJECTORY_CAPS["max_json_bytes"]
MAX_LINE_BYTES = 65_536
MAX_COMMENT_BYTES = 8192
MAX_METADATA_KEYS = 32
MAX_METADATA_VALUE_LENGTH = 4096
MAX_ROW_TOKENS = 64
LATTICE_EQUAL_TOLERANCE = 1e-12
BOHR_TO_ANGSTROM = 0.529177210903
HARTREE_TO_EV = 27.211386245988

CancelCheck = Callable[[], bool]


class TrajectoryParseError(ValueError):
    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code


@dataclass(frozen=True)
class ParsedTrajectory:
    trajectory: dict[str, Any]
    report: dict[str, Any]
    input_bytes: int
    parse_ms: float


def detect_trajectory_format(path: str | Path) -> str:
    file_path = Path(path)
    _preflight_file(file_path)
    suffix = file_path.suffix.lower()
    head = _read_bounded_head(file_path, 4096)
    if suffix == ".json":
        if f'"schema_version"' in head and TRAJECTORY_SCHEMA_VERSION in head:
            return "canonical_json"
        raise TrajectoryParseError("TRAJECTORY_FORMAT_UNSUPPORTED", "JSON is not a canonical trajectory contract.")
    if suffix in {".extxyz", ".xyz"}:
        lines = head.splitlines()
        if len(lines) < 2 or not re.fullmatch(r"[1-9][0-9]*", lines[0].strip()):
            raise TrajectoryParseError("TRAJECTORY_FRAME_HEADER_INVALID", "Trajectory atom-count header is invalid.")
        if "Properties=" in lines[1] or "Lattice=" in lines[1]:
            return "extxyz"
        raise TrajectoryParseError("TRAJECTORY_FORMAT_UNSUPPORTED", "Plain XYZ trajectory import is deferred by contract.")
    raise TrajectoryParseError("TRAJECTORY_FORMAT_UNSUPPORTED", "Trajectory format is not allowlisted.")


def parse_trajectory_file(path: str | Path, *, cancel_check: CancelCheck | None = None) -> ParsedTrajectory:
    file_path = Path(path)
    size = _preflight_file(file_path)
    detected = detect_trajectory_format(file_path)
    started = perf_counter()
    if detected == "canonical_json":
        trajectory = _parse_canonical_json(file_path, cancel_check=cancel_check)
        report = _parse_report(trajectory, detected, input_sha256=_sha256_file(file_path), parser_warnings=[])
    else:
        trajectory, parser_warnings = _parse_extxyz(file_path, cancel_check=cancel_check)
        report = _parse_report(trajectory, detected, input_sha256=_sha256_file(file_path), parser_warnings=parser_warnings)
    elapsed = (perf_counter() - started) * 1000
    return ParsedTrajectory(trajectory=trajectory, report=report, input_bytes=size, parse_ms=elapsed)


def _parse_canonical_json(path: Path, *, cancel_check: CancelCheck | None) -> dict[str, Any]:
    _cancel(cancel_check)
    raw = path.read_bytes()
    if len(raw) > MAX_INPUT_BYTES:
        raise TrajectoryParseError("TRAJECTORY_INPUT_TOO_LARGE", "Trajectory input exceeds the byte cap.")
    try:
        text = raw.decode("utf-8-sig", errors="strict")
    except UnicodeDecodeError as exc:
        raise TrajectoryParseError("TRAJECTORY_TEXT_ENCODING_INVALID", "Trajectory input must be valid UTF-8.") from exc
    try:
        payload = json.loads(text, parse_constant=lambda _value: (_ for _ in ()).throw(ValueError("nonfinite")))
    except (json.JSONDecodeError, ValueError, RecursionError) as exc:
        raise TrajectoryParseError("TRAJECTORY_CANONICAL_JSON_INVALID", "Canonical trajectory JSON could not be decoded safely.") from exc
    result = validate_trajectory(payload, raw_size_bytes=len(raw))
    if not result.valid:
        raise TrajectoryParseError("TRAJECTORY_CONTRACT_INVALID", f"Canonical trajectory validation failed: {','.join(result.errors[:8])}")
    return json.loads(stable_trajectory_json(payload))


def _parse_extxyz(path: Path, *, cancel_check: CancelCheck | None) -> tuple[dict[str, Any], list[str]]:
    input_hash = _sha256_file(path)
    frames: list[dict[str, Any]] = []
    raw_frames: list[dict[str, Any]] = []
    parser_warnings: set[str] = set()
    total_values = 0
    with path.open("r", encoding="utf-8-sig", errors="strict", newline="") as handle:
        while True:
            _cancel(cancel_check)
            header = _bounded_readline(handle)
            if header == "":
                break
            if not header.strip():
                raise TrajectoryParseError("TRAJECTORY_FRAME_HEADER_INVALID", "Blank lines are not valid frame boundaries.")
            if not re.fullmatch(r"[1-9][0-9]*", header.strip()):
                raise TrajectoryParseError("TRAJECTORY_FRAME_HEADER_INVALID", "Frame atom count must be a positive integer.")
            atom_count = int(header.strip())
            if atom_count > DEFAULT_TRAJECTORY_CAPS["max_atoms"]:
                raise TrajectoryParseError("TRAJECTORY_ATOM_LIMIT_EXCEEDED", "Frame atom count exceeds the contract cap.")
            if len(raw_frames) >= DEFAULT_TRAJECTORY_CAPS["max_frames"]:
                raise TrajectoryParseError("TRAJECTORY_FRAME_LIMIT_EXCEEDED", "Trajectory frame count exceeds the contract cap.")
            comment = _bounded_readline(handle, cap=MAX_COMMENT_BYTES)
            if comment == "":
                raise TrajectoryParseError("TRAJECTORY_FRAME_TRUNCATED", "Frame comment line is missing.")
            metadata = _parse_metadata(comment.rstrip("\r\n"))
            descriptor = _parse_properties(str(metadata.get("Properties", "")))
            if any(name.startswith("ignored:") for name, _data_type, _count in descriptor):
                parser_warnings.add("TRAJECTORY_UNKNOWN_PROPERTY_IGNORED")
            rows = [_parse_atom_row(_bounded_atom_line(handle), descriptor) for _ in range(atom_count)]
            total_values += atom_count * 3
            if total_values > DEFAULT_TRAJECTORY_CAPS["max_total_coordinate_values"]:
                raise TrajectoryParseError("TRAJECTORY_COORDINATE_VALUE_LIMIT_EXCEEDED", "Trajectory coordinate values exceed the contract cap.")
            raw_frames.append({"metadata": metadata, "rows": rows, "descriptor": descriptor})
    if not raw_frames:
        raise TrajectoryParseError("TRAJECTORY_EMPTY", "Trajectory contains no complete frames.")

    first_rows = raw_frames[0]["rows"]
    atom_count = len(first_rows)
    has_ids = all(row["source_id"] is not None for row in first_rows)
    if any((all(row["source_id"] is not None for row in item["rows"])) != has_ids for item in raw_frames):
        raise TrajectoryParseError("TRAJECTORY_ATOM_ID_SET_MISMATCH", "Atom IDs must be present consistently in every frame.")
    source_order = [row["source_id"] for row in first_rows] if has_ids else list(range(atom_count))
    if len(set(source_order)) != atom_count:
        raise TrajectoryParseError("TRAJECTORY_ATOM_ID_DUPLICATE", "First frame contains duplicate atom IDs.")
    first_species = [row["species"] for row in first_rows]

    lattices: list[list[list[float]]] = []
    pbc_values: list[list[bool]] = []
    property_presence: dict[str, bool] | None = None
    time_values: list[float | None] = []
    step_values: list[int | None] = []
    energy_scopes: list[str | None] = []
    conversions: set[str] = set()
    reordered = False
    for frame_index, raw_frame in enumerate(raw_frames):
        metadata = raw_frame["metadata"]
        rows = raw_frame["rows"]
        if len(rows) != atom_count:
            raise TrajectoryParseError("TRAJECTORY_ATOM_COUNT_MISMATCH", "Atom count changes across frames.")
        if has_ids:
            by_id = {row["source_id"]: row for row in rows}
            if len(by_id) != atom_count:
                raise TrajectoryParseError("TRAJECTORY_ATOM_ID_DUPLICATE", "Frame contains duplicate atom IDs.")
            if set(by_id) != set(source_order):
                raise TrajectoryParseError("TRAJECTORY_ATOM_ID_SET_MISMATCH", "Atom ID set changes across frames.")
            ordered = [by_id[source_id] for source_id in source_order]
            reordered = reordered or [row["source_id"] for row in rows] != source_order
        else:
            ordered = rows
        if [row["species"] for row in ordered] != first_species:
            raise TrajectoryParseError("TRAJECTORY_SPECIES_MISMATCH", "Species identity changes across frames.")
        lattice = _metadata_lattice(metadata)
        pbc = _metadata_pbc(metadata)
        if lattice is None:
            raise TrajectoryParseError("TRAJECTORY_LATTICE_METADATA_INVALID", "EXTXYZ trajectory frames require explicit Lattice metadata.")
        lattices.append(lattice)
        pbc_values.append(pbc)
        presence = {name: all(row[name] is not None for row in ordered) for name in ("velocities", "forces")}
        if any(any(row[name] is None for row in ordered) for name in ("velocities", "forces") if presence[name]):
            raise TrajectoryParseError("TRAJECTORY_PROPERTY_SHAPE_INVALID", "Optional vectors are incomplete.")
        if property_presence is None:
            property_presence = presence
        elif property_presence != presence:
            raise TrajectoryParseError("TRAJECTORY_PROPERTY_AVAILABILITY_INCONSISTENT", "Optional property availability changes across frames.")

        position_factor = _unit_factor(metadata.get("position_unit", "angstrom"), "position")
        velocity_factor = _unit_factor(metadata.get("velocity_unit"), "velocity") if presence["velocities"] else 1.0
        force_factor = _unit_factor(metadata.get("force_unit"), "force") if presence["forces"] else 1.0
        if position_factor != 1.0: conversions.add(f"positions:{metadata.get('position_unit')}->angstrom")
        if velocity_factor != 1.0: conversions.add(f"velocities:{metadata.get('velocity_unit')}->angstrom_per_femtosecond")
        if force_factor != 1.0: conversions.add(f"forces:{metadata.get('force_unit')}->electronvolt_per_angstrom")
        time_value, time_conversion = _metadata_time(metadata)
        if time_conversion: conversions.add(time_conversion)
        step_value = _metadata_step(metadata)
        energy, energy_scope = _metadata_energy(metadata, parser_warnings, conversions)
        temperature = _metadata_temperature(metadata)
        time_values.append(time_value)
        step_values.append(step_value)
        energy_scopes.append(energy_scope)
        frames.append({
            "schema_version": TRAJECTORY_FRAME_SCHEMA_VERSION,
            "frame_index": frame_index,
            "atom_ids": list(range(atom_count)),
            "step": step_value,
            "time": time_value,
            "lattice": lattice,
            "positions": [[_clean(value * position_factor) for value in row["positions"]] for row in ordered],
            "velocities": [[_clean(value * velocity_factor) for value in row["velocities"]] for row in ordered] if presence["velocities"] else None,
            "forces": [[_clean(value * force_factor) for value in row["forces"]] for row in ordered] if presence["forces"] else None,
            "energy": energy,
            "temperature": temperature,
            "metadata": {},
        })

    if any(value != pbc_values[0] for value in pbc_values):
        raise TrajectoryParseError("TRAJECTORY_PBC_INVALID", "PBC changes across frames.")
    fixed_lattice = all(_matrix_close(lattices[0], item) for item in lattices[1:])
    lattice_mode = "fixed" if fixed_lattice else "variable"
    if fixed_lattice:
        for item in frames: item["lattice"] = None
    else:
        parser_warnings.discard("TRAJECTORY_IDENTICAL_VARIABLE_LATTICE_NORMALIZED")
    kind = _trajectory_kind(raw_frames, time_values, step_values)
    if kind == "molecular_dynamics" and any(value is None for value in time_values):
        raise TrajectoryParseError("TRAJECTORY_TIME_METADATA_INVALID", "MD frames require physical time.")
    properties = {
        "positions": True,
        "velocities": bool(property_presence and property_presence["velocities"]),
        "forces": bool(property_presence and property_presence["forces"]),
        "energy": all(frame["energy"] is not None for frame in frames),
        "temperature": all(frame["temperature"] is not None for frame in frames),
        "stress": False,
    }
    if any((frame["energy"] is not None) != properties["energy"] for frame in frames) or any((frame["temperature"] is not None) != properties["temperature"] for frame in frames):
        raise TrajectoryParseError("TRAJECTORY_PROPERTY_AVAILABILITY_INCONSISTENT", "Scalar property availability changes across frames.")
    trajectory_warnings = ["TRAJECTORY_SOURCE_SOFTWARE_UNKNOWN", "TRAJECTORY_WRAPPING_UNKNOWN"]
    if reordered: parser_warnings.add("TRAJECTORY_ATOMS_REORDERED_BY_ID")
    payload: dict[str, Any] = {
        "schema_version": TRAJECTORY_SCHEMA_VERSION,
        "trajectory_id": "pending",
        "kind": kind,
        "coordinate_mode": "cartesian",
        "position_wrapping": "unknown",
        "lattice_mode": lattice_mode,
        "atom_identity_mode": "stable_index",
        "periodic_boundary": pbc_values[0],
        "units": {"positions": "angstrom", "velocities": "angstrom_per_femtosecond", "forces": "electronvolt_per_angstrom", "energy": "electronvolt", "temperature": "kelvin"},
        "time": {"unit": "femtosecond" if kind == "molecular_dynamics" else None, "origin": 0.0},
        "atoms": {"count": atom_count, "records": [{"atom_id": index, "species": species, "label": f"{species}{index + 1}", "occupancy": 1.0} for index, species in enumerate(first_species)]},
        "fixed_lattice": lattices[0] if fixed_lattice else None,
        "frames": frames,
        "properties": properties,
        "metadata": {
            "title": "Imported EXTXYZ trajectory",
            "parser_detected_format": "extxyz",
            "parser_reordered_by_atom_id": reordered,
            "parser_unit_conversions": sorted(conversions),
            "parser_warnings": sorted(parser_warnings),
        },
        "provenance": {"source_format": "extxyz", "source_software": "unknown", "source_version": None, "parser_version": TRAJECTORY_PARSER_VERSION, "input_sha256": input_hash, "created_by_tool": None},
        "warnings": sorted(trajectory_warnings),
        "security": {"contains_javascript": False, "contains_html": False, "external_urls_allowed": False, "remote_frames_allowed": False, "executable_content_allowed": False},
    }
    payload["trajectory_id"] = canonical_trajectory_id(payload)
    encoded = stable_trajectory_json(payload).encode()
    result = validate_trajectory(payload, raw_size_bytes=len(encoded))
    if not result.valid:
        raise TrajectoryParseError("TRAJECTORY_CONTRACT_INVALID", f"Normalized trajectory validation failed: {','.join(result.errors[:8])}")
    return payload, sorted(parser_warnings)


def _parse_metadata(comment: str) -> dict[str, str]:
    if len(comment.encode("utf-8")) > MAX_COMMENT_BYTES:
        raise TrajectoryParseError("TRAJECTORY_COMMENT_METADATA_INVALID", "Frame comment exceeds its byte cap.")
    try:
        tokens = shlex.split(comment, posix=True)
    except ValueError as exc:
        raise TrajectoryParseError("TRAJECTORY_COMMENT_METADATA_INVALID", "Frame metadata quoting is invalid.") from exc
    if len(tokens) > MAX_METADATA_KEYS:
        raise TrajectoryParseError("TRAJECTORY_COMMENT_METADATA_INVALID", "Frame metadata has too many keys.")
    result: dict[str, str] = {}
    for token in tokens:
        if "=" not in token:
            continue
        key, value = token.split("=", 1)
        if not re.fullmatch(r"[A-Za-z][A-Za-z0-9_]{0,63}", key) or len(value) > MAX_METADATA_VALUE_LENGTH:
            raise TrajectoryParseError("TRAJECTORY_COMMENT_METADATA_INVALID", "Frame metadata key or value is invalid.")
        if key in result:
            raise TrajectoryParseError("TRAJECTORY_COMMENT_METADATA_INVALID", "Frame metadata contains duplicate keys.")
        if any(marker in value.lower() for marker in ("http://", "https://", "javascript:", "<script", "<iframe")):
            raise TrajectoryParseError("TRAJECTORY_EXTERNAL_REFERENCE_FORBIDDEN", "External or executable frame metadata is forbidden.")
        result[key] = value
    return result


def _parse_properties(value: str) -> list[tuple[str, str, int]]:
    parts = value.split(":") if value else []
    if not parts or len(parts) % 3:
        raise TrajectoryParseError("TRAJECTORY_PROPERTIES_DESCRIPTOR_INVALID", "EXTXYZ Properties descriptor is required and must use triplets.")
    fields: list[tuple[str, str, int]] = []
    seen: set[str] = set()
    aliases = {"species": "species", "pos": "positions", "positions": "positions", "vel": "velocities", "velocity": "velocities", "velocities": "velocities", "force": "forces", "forces": "forces", "id": "source_id", "atom_id": "source_id"}
    for index in range(0, len(parts), 3):
        raw_name, data_type, raw_count = parts[index:index + 3]
        if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]{0,63}", raw_name) or data_type not in {"S", "R", "I"} or not raw_count.isdigit():
            raise TrajectoryParseError("TRAJECTORY_PROPERTIES_DESCRIPTOR_INVALID", "EXTXYZ property descriptor component is invalid.")
        count = int(raw_count)
        if count < 1 or count > 9:
            raise TrajectoryParseError("TRAJECTORY_PROPERTIES_DESCRIPTOR_INVALID", "EXTXYZ property component count is invalid.")
        name = aliases.get(raw_name.lower(), f"ignored:{raw_name}")
        if name in seen:
            raise TrajectoryParseError("TRAJECTORY_PROPERTY_DUPLICATE", "EXTXYZ property is duplicated.")
        seen.add(name)
        fields.append((name, data_type, count))
    required = {(name, data_type, count) for name, data_type, count in fields}
    if ("species", "S", 1) not in required or ("positions", "R", 3) not in required:
        raise TrajectoryParseError("TRAJECTORY_PROPERTIES_DESCRIPTOR_INVALID", "EXTXYZ requires species:S:1 and pos:R:3.")
    return fields


def _parse_atom_row(line: str, descriptor: list[tuple[str, str, int]]) -> dict[str, Any]:
    if line == "":
        raise TrajectoryParseError("TRAJECTORY_FRAME_TRUNCATED", "Frame ended before all atom rows were read.")
    tokens = line.split()
    expected = sum(field[2] for field in descriptor)
    if len(tokens) != expected or len(tokens) > MAX_ROW_TOKENS:
        raise TrajectoryParseError("TRAJECTORY_ATOM_ROW_INVALID", "Atom row token count does not match Properties.")
    result: dict[str, Any] = {"species": None, "positions": None, "velocities": None, "forces": None, "source_id": None}
    cursor = 0
    for name, data_type, count in descriptor:
        values = tokens[cursor:cursor + count]
        cursor += count
        if data_type == "R":
            parsed = [_finite_float(item) for item in values]
        elif data_type == "I":
            try: parsed = [int(item) for item in values]
            except ValueError as exc: raise TrajectoryParseError("TRAJECTORY_ATOM_ID_INVALID", "Integer atom property is invalid.") from exc
        else:
            parsed = values
        if name.startswith("ignored:"):
            continue
        value: Any = parsed[0] if count == 1 else parsed
        result[name] = value
    if not isinstance(result["species"], str) or not re.fullmatch(r"[A-Z][a-z]?", result["species"]):
        raise TrajectoryParseError("TRAJECTORY_ATOM_ROW_INVALID", "Atom species must be an element symbol.")
    return result


def _metadata_lattice(metadata: dict[str, str]) -> list[list[float]] | None:
    value = metadata.get("Lattice")
    if value is None: return None
    parts = value.split()
    if len(parts) != 9: raise TrajectoryParseError("TRAJECTORY_LATTICE_METADATA_INVALID", "Lattice requires nine values.")
    values = [_finite_float(item) for item in parts]
    return [values[0:3], values[3:6], values[6:9]]


def _metadata_pbc(metadata: dict[str, str]) -> list[bool]:
    raw = metadata.get("pbc") or metadata.get("PBC")
    if raw is None: raise TrajectoryParseError("TRAJECTORY_PBC_INVALID", "EXTXYZ trajectory requires explicit PBC.")
    values = raw.split()
    mapping = {"T": True, "F": False, "true": True, "false": False, "1": True, "0": False}
    if len(values) != 3 or any(value not in mapping for value in values): raise TrajectoryParseError("TRAJECTORY_PBC_INVALID", "PBC must contain three approved booleans.")
    result = [mapping[value] for value in values]
    if result not in ([True, True, True], [False, False, False]): raise TrajectoryParseError("TRAJECTORY_PBC_INVALID", "Partial periodicity is deferred.")
    return result


def _metadata_time(metadata: dict[str, str]) -> tuple[float | None, str | None]:
    raw = metadata.get("Time", metadata.get("time"))
    if raw is None: return None, None
    unit = metadata.get("time_unit")
    factor = _unit_factor(unit, "time")
    value = _clean(_finite_float(raw) * factor)
    return value, None if factor == 1.0 else f"time:{unit}->femtosecond"


def _metadata_step(metadata: dict[str, str]) -> int | None:
    raw = metadata.get("Step", metadata.get("step"))
    if raw is None: return None
    try: value = int(raw)
    except ValueError as exc: raise TrajectoryParseError("TRAJECTORY_TIME_METADATA_INVALID", "Step must be an integer.") from exc
    if value < 0: raise TrajectoryParseError("TRAJECTORY_TIME_METADATA_INVALID", "Step must be nonnegative.")
    return value


def _metadata_energy(metadata: dict[str, str], warnings: set[str], conversions: set[str]) -> tuple[dict[str, Any] | None, str | None]:
    raw = metadata.get("energy")
    if raw is None: return None, None
    scope = metadata.get("energy_scope")
    if scope not in {"potential", "total"}:
        warnings.add("TRAJECTORY_ENERGY_FIELD_IGNORED_AMBIGUOUS")
        return None, None
    unit = metadata.get("energy_unit")
    factor = _unit_factor(unit, "energy")
    if factor != 1.0: conversions.add(f"energy:{unit}->electronvolt")
    value = _clean(_finite_float(raw) * factor)
    result = {"potential": None, "kinetic": None, "total": None, "free": None, "unit": "electronvolt", "scope": "total_system"}
    result[scope] = value
    return result, scope


def _metadata_temperature(metadata: dict[str, str]) -> float | None:
    raw = metadata.get("temperature")
    if raw is None: return None
    if metadata.get("temperature_unit") != "kelvin": raise TrajectoryParseError("TRAJECTORY_UNIT_UNKNOWN", "Temperature unit must be kelvin.")
    value = _finite_float(raw)
    if value < 0: raise TrajectoryParseError("TRAJECTORY_ATOM_ROW_INVALID", "Temperature must be nonnegative.")
    return _clean(value)


def _trajectory_kind(raw_frames: list[dict[str, Any]], times: list[float | None], steps: list[int | None]) -> str:
    explicit = raw_frames[0]["metadata"].get("trajectory_kind")
    if explicit is not None:
        if explicit not in {"molecular_dynamics", "geometry_optimization", "structure_sequence", "unknown_static_sequence"}: raise TrajectoryParseError("TRAJECTORY_KIND_UNSUPPORTED", "Trajectory kind is unsupported.")
        return explicit
    if all(value is not None for value in times): return "molecular_dynamics"
    if all(value is not None for value in steps) and any(
        frame["metadata"].get("energy") is not None
        or any(name == "forces" for name, _data_type, _count in frame["descriptor"])
        for frame in raw_frames
    ):
        return "geometry_optimization"
    return "structure_sequence"


def _unit_factor(value: Any, quantity: str) -> float:
    tables = {
        "position": {"angstrom": 1.0, "nanometer": 10.0, "bohr": BOHR_TO_ANGSTROM},
        "time": {"femtosecond": 1.0, "picosecond": 1000.0},
        "velocity": {"angstrom_per_femtosecond": 1.0, "angstrom_per_picosecond": 0.001, "nanometer_per_picosecond": 0.01},
        "force": {"electronvolt_per_angstrom": 1.0, "hartree_per_bohr": HARTREE_TO_EV / BOHR_TO_ANGSTROM},
        "energy": {"electronvolt": 1.0, "hartree": HARTREE_TO_EV},
    }
    if value not in tables[quantity]: raise TrajectoryParseError("TRAJECTORY_UNIT_UNKNOWN", f"{quantity} unit is missing or unsupported.")
    return tables[quantity][value]


def _parse_report(trajectory: dict[str, Any], detected: str, *, input_sha256: str, parser_warnings: list[str]) -> dict[str, Any]:
    metadata = trajectory.get("metadata", {})
    return {
        "schema_version": TRAJECTORY_PARSE_REPORT_SCHEMA_VERSION,
        "detected_format": detected,
        "frames_read": len(trajectory["frames"]),
        "atoms_per_frame": trajectory["atoms"]["count"],
        "lattice_mode": trajectory["lattice_mode"],
        "coordinate_mode": trajectory["coordinate_mode"],
        "properties_detected": [key for key in ("positions", "velocities", "forces", "energy", "temperature") if trajectory["properties"][key]],
        "unit_conversions": list(metadata.get("parser_unit_conversions", [])),
        "reordered_by_atom_id": bool(metadata.get("parser_reordered_by_atom_id", False)),
        "warnings": sorted(set(parser_warnings or metadata.get("parser_warnings", []))),
        "input_sha256": input_sha256,
        "deterministic": True,
    }


def _preflight_file(path: Path) -> int:
    try: size = path.stat().st_size
    except OSError as exc: raise TrajectoryParseError("TRAJECTORY_FORMAT_UNSUPPORTED", "Trajectory input is not readable.") from exc
    if size <= 0: raise TrajectoryParseError("TRAJECTORY_EMPTY", "Trajectory input is empty.")
    if size > MAX_INPUT_BYTES: raise TrajectoryParseError("TRAJECTORY_INPUT_TOO_LARGE", "Trajectory input exceeds the byte cap.")
    return size


def _read_bounded_head(path: Path, cap: int) -> str:
    with path.open("rb") as handle: raw = handle.read(cap + 1)
    try: return raw[:cap].decode("utf-8-sig", errors="strict")
    except UnicodeDecodeError as exc: raise TrajectoryParseError("TRAJECTORY_TEXT_ENCODING_INVALID", "Trajectory input must be UTF-8.") from exc


def _bounded_readline(handle: TextIO, *, cap: int = MAX_LINE_BYTES) -> str:
    line = handle.readline(cap + 1)
    if len(line.encode("utf-8")) > cap: raise TrajectoryParseError("TRAJECTORY_LINE_TOO_LONG", "Trajectory line exceeds its byte cap.")
    return line


def _bounded_atom_line(handle: TextIO) -> str:
    line = _bounded_readline(handle)
    if line == "": raise TrajectoryParseError("TRAJECTORY_FRAME_TRUNCATED", "Frame ended before all atom rows were read.")
    return line


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(65_536), b""): digest.update(chunk)
    return digest.hexdigest()


def _finite_float(value: str) -> float:
    try: result = float(value)
    except ValueError as exc: raise TrajectoryParseError("TRAJECTORY_ATOM_ROW_INVALID", "Numeric trajectory value is invalid.") from exc
    if not math.isfinite(result) or abs(result) > DEFAULT_TRAJECTORY_CAPS["max_numeric_magnitude"]: raise TrajectoryParseError("TRAJECTORY_ATOM_ROW_INVALID", "Numeric trajectory value is outside safe bounds.")
    return result


def _clean(value: float) -> float:
    return float(f"{value:.12g}")


def _matrix_close(left: list[list[float]], right: list[list[float]]) -> bool:
    return all(abs(a - b) <= LATTICE_EQUAL_TOLERANCE for row_a, row_b in zip(left, right, strict=True) for a, b in zip(row_a, row_b, strict=True))


def _cancel(check: CancelCheck | None) -> None:
    if check is not None and check(): raise TrajectoryParseError("TRAJECTORY_PARSE_CANCELLED", "Trajectory parsing was cancelled.")
