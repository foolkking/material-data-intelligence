from __future__ import annotations

import math
import hashlib
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Iterable

from pymatgen.io.vasp import Poscar

from mdi_artifact_core import VOLUMETRIC_CAPS, volumetric_content_hash


MAX_SOURCE_BYTES = min(VOLUMETRIC_CAPS["max_dataset_bytes"], 268_435_456)
MAX_HEADER_BYTES = 131_072
MAX_LINE_BYTES = 1_048_576
MAX_PARSER_VOXELS = 2_097_152
BOHR_TO_ANGSTROM = 0.529177210903
VASP_NAMES = frozenset({"CHGCAR", "CHG", "LOCPOT", "ELFCAR", "PARCHG"})


class VolumetricParseError(ValueError):
    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code


@dataclass(frozen=True)
class ParsedVolumetricSource:
    source: dict[str, Any]
    report: dict[str, Any]


def detect_volumetric_format(path: str | Path) -> str:
    file_path = Path(path)
    size = _source_size(file_path)
    if size > MAX_SOURCE_BYTES:
        raise VolumetricParseError("VOLUME_SOURCE_CAP_EXCEEDED", "Volumetric source exceeds the bounded source-byte cap.")
    head = _read_head(file_path)
    lines = head.splitlines()
    cube = _looks_like_cube(lines)
    vasp = _looks_like_vasp(lines)
    if cube == vasp:
        raise VolumetricParseError("VOLUME_FORMAT_AMBIGUOUS", "Source is not an unambiguous supported VASP volumetric or CUBE file.")
    return "gaussian_cube" if cube else "vasp_volumetric"


def parse_volumetric_file(
    path: str | Path,
    *,
    source_format: str = "auto",
    quantity_hint: str = "auto",
    cancel_check: Callable[[], bool] | None = None,
) -> ParsedVolumetricSource:
    file_path = Path(path)
    source_bytes = _source_size(file_path)
    if source_bytes > MAX_SOURCE_BYTES:
        raise VolumetricParseError("VOLUME_SOURCE_CAP_EXCEEDED", "Volumetric source exceeds the bounded source-byte cap.")
    detected = detect_volumetric_format(file_path)
    if source_format not in {"auto", "vasp_volumetric", "gaussian_cube"}:
        raise VolumetricParseError("VOLUME_FORMAT_UNSUPPORTED", "Source format must be an approved enum value.")
    if source_format != "auto" and source_format != detected:
        raise VolumetricParseError("VOLUME_FORMAT_MISMATCH", "Explicit format does not match bounded content detection.")
    if cancel_check and cancel_check():
        raise VolumetricParseError("VOLUME_PARSE_CANCELLED", "Volumetric parsing was cancelled.")
    if detected == "vasp_volumetric":
        source, details = _parse_vasp_stream(file_path, file_path.name, quantity_hint)
    else:
        source, details = _parse_cube_stream(file_path, file_path.name, quantity_hint)
    source_hash = _stream_sha256(file_path)
    source["source_sha256"] = source_hash
    report = {
        "schema_version": "phase10j1.volumetric_parse_report.v1",
        "detected_format": detected,
        "detector_confidence": "high",
        "detector_reasons": details.pop("detector_reasons"),
        "source_bytes": source_bytes,
        "source_sha256": source_hash,
        "shape": source["shape"],
        "expected_values_per_channel": math.prod(source["shape"]),
        "channel_count": len(source["channels"]),
        "estimated_canonical_bytes": math.prod(source["shape"]) * len(source["channels"]) * 8,
        "warnings": sorted(set(source.get("warnings", []))),
        **details,
    }
    return ParsedVolumetricSource(source=source, report=report)


def _parse_vasp_stream(path: Path, source_name: str, quantity_hint: str) -> tuple[dict[str, Any], dict[str, Any]]:
    try:
        with path.open("r", encoding="utf-8", errors="strict", newline=None) as handle:
            header = [_bounded_readline(handle) for _ in range(6)]
            if any(line == "" for line in header):
                raise VolumetricParseError("VOLUME_VASP_STRUCTURE_INVALID", "VASP header is truncated.")
            species_or_counts = header[5].split()
            counts_in_header = bool(species_or_counts and all(_is_int(item) for item in species_or_counts))
            counts_line = header[5] if counts_in_header else _bounded_readline(handle)
            if not counts_in_header:
                header.append(counts_line)
            counts = counts_line.split()
            if not counts or not all(_is_int(item) and int(item) >= 0 for item in counts):
                raise VolumetricParseError("VOLUME_VASP_STRUCTURE_INVALID", "VASP atom counts are invalid.")
            atom_count = sum(int(item) for item in counts)
            if atom_count > 100_000:
                raise VolumetricParseError("VOLUME_ATOM_CAP_EXCEEDED", "VASP atom count exceeds parser caps.")
            coordinate_line = _bounded_readline(handle)
            header.append(coordinate_line)
            if coordinate_line.strip().lower().startswith("s"):
                coordinate_line = _bounded_readline(handle)
                header.append(coordinate_line)
            if not coordinate_line.strip().lower().startswith(("d", "c", "k")):
                raise VolumetricParseError("VOLUME_VASP_STRUCTURE_INVALID", "VASP coordinate mode is invalid.")
            for _ in range(atom_count):
                line = _bounded_readline(handle)
                if not line:
                    raise VolumetricParseError("VOLUME_VASP_STRUCTURE_INVALID", "VASP coordinate rows are truncated.")
                header.append(line)
            grid_line = _next_stream_nonempty(handle)
            shape = _parse_shape(grid_line, "VOLUME_VASP_GRID_INVALID")
            _check_shape(shape)
            value_count = math.prod(shape)
            blocks = [_vasp_to_canonical(_read_stream_values(handle, value_count), shape)]
            augmentation_seen = False
            while len(blocks) < 4:
                line = handle.readline()
                if line == "":
                    break
                _check_line(line)
                stripped = line.strip()
                if not stripped:
                    continue
                parts = stripped.split()
                if len(parts) == 3 and all(_is_int(item) for item in parts) and [int(item) for item in parts] == shape:
                    blocks.append(_vasp_to_canonical(_read_stream_values(handle, value_count), shape))
                else:
                    augmentation_seen = True
    except UnicodeDecodeError as exc:
        raise VolumetricParseError("VOLUME_TEXT_ENCODING_INVALID", "Volumetric source must be valid UTF-8 compatible text.") from exc
    try:
        structure = Poscar.from_str("".join(header)).structure
    except Exception as exc:
        raise VolumetricParseError("VOLUME_VASP_STRUCTURE_INVALID", "VASP structure header is invalid.") from exc
    volume = float(structure.lattice.volume)
    if not math.isfinite(volume) or volume <= 0:
        raise VolumetricParseError("VOLUME_VASP_STRUCTURE_INVALID", "VASP lattice volume must be finite and positive.")
    family = source_name.upper().split(".", 1)[0]
    if family not in VASP_NAMES:
        family = "CHGCAR" if quantity_hint in {"electron_density", "charge_density", "spin_density", "magnetization_density"} else "UNKNOWN"
    channels, warnings = _vasp_channels(blocks, family, quantity_hint, volume)
    if augmentation_seen:
        warnings.append("VOLUME_VASP_AUGMENTATION_NOT_INCLUDED")
    lattice = [[float(x) for x in row] for row in structure.lattice.matrix]
    structure_payload = structure.as_dict()
    return {
        "source_format": "vasp_volumetric", "source_name": _safe_name(source_name), "source_sha256": "", "shape": shape,
        "origin_cartesian": [0.0, 0.0, 0.0], "step_matrix": [[lattice[i][j] / shape[i] for j in range(3)] for i in range(3)],
        "boundary_conditions": ["periodic"] * 3, "endpoint_policy": "excluded", "sample_location": "node",
        "structure": structure_payload, "structure_sha256": volumetric_content_hash(structure_payload), "lattice_matrix": lattice,
        "atom_records": [], "channels": channels, "warnings": sorted(set(warnings)),
    }, {"detector_reasons": ["POSCAR-compatible header", "bounded grid dimensions", "finite scalar payload"], "atom_count": atom_count, "source_family": family, "augmentation_section_present": augmentation_seen, "source_order": "x_fastest_then_y_then_z", "canonical_order": "ijkc_component_fastest", "streaming": True}


def _parse_cube_stream(path: Path, source_name: str, quantity_hint: str) -> tuple[dict[str, Any], dict[str, Any]]:
    try:
        with path.open("r", encoding="utf-8", errors="strict", newline=None) as handle:
            comments = [_bounded_readline(handle), _bounded_readline(handle)]
            if any(line == "" for line in comments):
                raise VolumetricParseError("VOLUME_CUBE_HEADER_INVALID", "CUBE header is truncated.")
            origin_row = _float_tokens(_bounded_readline(handle), 4, "VOLUME_CUBE_HEADER_INVALID")
            atom_count_signed = int(origin_row[0]) if origin_row[0].is_integer() else 0
            if atom_count_signed < 0:
                raise VolumetricParseError("VOLUME_CUBE_MULTI_ORBITAL_UNSUPPORTED", "Multi-orbital CUBE datasets are explicitly unsupported.")
            atom_count = atom_count_signed
            axis_rows = [_float_tokens(_bounded_readline(handle), 4, "VOLUME_CUBE_AXIS_INVALID") for _ in range(3)]
            counts = [int(row[0]) if row[0].is_integer() else 0 for row in axis_rows]
            if any(value == 0 for value in counts) or len({value > 0 for value in counts}) != 1:
                raise VolumetricParseError("VOLUME_CUBE_AXIS_INVALID", "CUBE axis counts must be nonzero integers with consistent unit signs.")
            source_unit = "bohr" if counts[0] > 0 else "angstrom"
            factor = BOHR_TO_ANGSTROM if source_unit == "bohr" else 1.0
            shape = [abs(value) for value in counts]
            _check_shape(shape)
            atoms = []
            for _ in range(atom_count):
                row = _float_tokens(_bounded_readline(handle), 5, "VOLUME_CUBE_ATOM_INVALID")
                atomic_number = int(row[0]) if row[0].is_integer() else -1
                if atomic_number < 0 or atomic_number > 118:
                    raise VolumetricParseError("VOLUME_CUBE_ATOM_INVALID", "CUBE atomic number is invalid.")
                atoms.append({"atomic_number": atomic_number, "source_charge": row[1], "cartesian_angstrom": [row[i] * factor for i in range(2, 5)]})
            values = _read_stream_values(handle, math.prod(shape))
            for line in handle:
                _check_line(line)
                if line.strip():
                    raise VolumetricParseError("VOLUME_CUBE_TRAILING_DATA", "CUBE contains unexpected trailing or additional dataset values.")
    except UnicodeDecodeError as exc:
        raise VolumetricParseError("VOLUME_TEXT_ENCODING_INVALID", "Volumetric source must be valid UTF-8 compatible text.") from exc
    quantity = quantity_hint if quantity_hint != "auto" else "generic_scalar"
    if quantity not in {"electron_density", "charge_density", "spin_density", "magnetization_density", "electrostatic_potential", "orbital_density", "generic_scalar"}:
        raise VolumetricParseError("VOLUME_QUANTITY_HINT_INVALID", "CUBE quantity hint is unsupported.")
    canonical_unit, value_factor, integral = _cube_quantity_policy(quantity, source_unit)
    channel = {"name": "scalar", "quantity": quantity, "source_unit": canonical_unit if value_factor == 1.0 else "electron/bohr^3", "canonical_unit": canonical_unit, "conversion_factor": value_factor, "values": [value * value_factor for value in values], "normalization_semantics": "source_native", "integral_semantics": integral, "spin_channel": None}
    return {
        "source_format": "gaussian_cube", "source_name": _safe_name(source_name), "source_sha256": "", "shape": shape,
        "origin_cartesian": [origin_row[i] * factor for i in range(1, 4)], "step_matrix": [[row[i] * factor for i in range(1, 4)] for row in axis_rows],
        "boundary_conditions": ["non_periodic"] * 3, "endpoint_policy": "not_applicable", "sample_location": "node",
        "structure": None, "structure_sha256": None, "lattice_matrix": None, "atom_records": atoms,
        "source_spatial_unit": source_unit, "channels": [channel], "warnings": [],
    }, {"detector_reasons": ["CUBE atom/origin row", "three bounded affine axes", "finite scalar payload"], "atom_count": atom_count, "source_spatial_unit": source_unit, "source_order": "i_outer_j_middle_k_fastest", "canonical_order": "ijkc_component_fastest", "streaming": True}


def _parse_vasp(text: str, source_name: str, quantity_hint: str) -> tuple[dict[str, Any], dict[str, Any]]:
    lines = text.splitlines()
    header_end, atom_count = _vasp_header_end(lines)
    grid_line = _next_nonempty(lines, header_end)
    shape = _parse_shape(lines[grid_line], "VOLUME_VASP_GRID_INVALID")
    _check_shape(shape)
    try:
        structure = Poscar.from_str("\n".join(lines[:header_end])).structure
    except Exception as exc:
        raise VolumetricParseError("VOLUME_VASP_STRUCTURE_INVALID", "VASP structure header is invalid.") from exc
    volume = float(structure.lattice.volume)
    if not math.isfinite(volume) or volume <= 0:
        raise VolumetricParseError("VOLUME_VASP_STRUCTURE_INVALID", "VASP lattice volume must be finite and positive.")
    value_count = math.prod(shape)
    blocks: list[list[float]] = []
    cursor = grid_line + 1
    values, cursor = _read_numeric_values(lines, cursor, value_count)
    blocks.append(_vasp_to_canonical(values, shape))
    augmentation_seen = False
    while cursor < len(lines) and len(blocks) < 4:
        candidate = _find_matching_shape(lines, cursor, shape)
        if candidate is None:
            if any(line.strip() for line in lines[cursor:]):
                augmentation_seen = True
            break
        if any(line.strip() for line in lines[cursor:candidate]):
            augmentation_seen = True
        values, cursor = _read_numeric_values(lines, candidate + 1, value_count)
        blocks.append(_vasp_to_canonical(values, shape))
    family = source_name.upper().split(".", 1)[0]
    if family not in VASP_NAMES:
        family = "CHGCAR" if quantity_hint in {"electron_density", "charge_density", "spin_density", "magnetization_density"} else "UNKNOWN"
    channels, warnings = _vasp_channels(blocks, family, quantity_hint, volume)
    if augmentation_seen:
        warnings.append("VOLUME_VASP_AUGMENTATION_NOT_INCLUDED")
    lattice = [[float(x) for x in row] for row in structure.lattice.matrix]
    structure_payload = structure.as_dict()
    return {
        "source_format": "vasp_volumetric",
        "source_name": _safe_name(source_name),
        "source_sha256": "",
        "shape": shape,
        "origin_cartesian": [0.0, 0.0, 0.0],
        "step_matrix": [[lattice[i][j] / shape[i] for j in range(3)] for i in range(3)],
        "boundary_conditions": ["periodic"] * 3,
        "endpoint_policy": "excluded",
        "sample_location": "node",
        "structure": structure_payload,
        "structure_sha256": volumetric_content_hash(structure_payload),
        "lattice_matrix": lattice,
        "atom_records": [],
        "channels": channels,
        "warnings": sorted(set(warnings)),
    }, {
        "detector_reasons": ["POSCAR-compatible header", "bounded grid dimensions", "finite scalar payload"],
        "atom_count": atom_count,
        "source_family": family,
        "augmentation_section_present": augmentation_seen,
        "source_order": "x_fastest_then_y_then_z",
        "canonical_order": "ijkc_component_fastest",
    }


def _vasp_channels(blocks: list[list[float]], family: str, hint: str, volume: float) -> tuple[list[dict[str, Any]], list[str]]:
    warnings: list[str] = []
    if family in {"CHGCAR", "CHG", "PARCHG"}:
        quantity = "orbital_density" if family == "PARCHG" else "electron_density"
        if hint not in {"auto", "electron_density", "charge_density", "orbital_density", "spin_density", "magnetization_density"}:
            warnings.append("VOLUME_QUANTITY_HINT_CONFLICT")
        names = ["total", "spin_difference", "magnetization_y", "magnetization_z"]
        if len(blocks) not in {1, 2, 4}:
            raise VolumetricParseError("VOLUME_VASP_SPIN_LAYOUT_UNSUPPORTED", "VASP density source has an unsupported channel layout.")
        channels = []
        for idx, block in enumerate(blocks):
            channel_quantity = quantity if idx == 0 else "magnetization_density"
            channels.append({
                "name": names[idx],
                "quantity": channel_quantity,
                "source_unit": "electron/angstrom^3",
                "canonical_unit": "electron/angstrom^3" if idx == 0 else "bohr_magneton/angstrom^3",
                "conversion_factor": 1.0 / volume,
                "values": [value / volume for value in block],
                "normalization_semantics": "source_native",
                "integral_semantics": "electron_count" if idx == 0 else "magnetic_moment",
                "spin_channel": "total" if idx == 0 else ("spin_difference" if len(blocks) == 2 else ["magnetization_x", "magnetization_y", "magnetization_z"][idx - 1]),
            })
        return channels, warnings
    if len(blocks) != 1:
        raise VolumetricParseError("VOLUME_VASP_CHANNEL_LAYOUT_UNSUPPORTED", "This VASP volumetric family requires one scalar grid.")
    if family == "LOCPOT":
        return [{"name": "local_potential", "quantity": "local_potential", "source_unit": "electronvolt", "canonical_unit": "electronvolt", "conversion_factor": 1.0, "values": blocks[0], "normalization_semantics": "source_native", "integral_semantics": "cell_average", "spin_channel": None}], warnings
    if family == "ELFCAR":
        return [{"name": "electron_localization_function", "quantity": "electron_localization_function", "source_unit": "dimensionless", "canonical_unit": "dimensionless", "conversion_factor": 1.0, "values": blocks[0], "normalization_semantics": "source_native", "integral_semantics": "not_physically_interpreted", "spin_channel": None}], warnings
    raise VolumetricParseError("VOLUME_VASP_QUANTITY_REQUIRED", "Unknown VASP volumetric filename requires a supported quantity hint.")


def _parse_cube(text: str, source_name: str, quantity_hint: str) -> tuple[dict[str, Any], dict[str, Any]]:
    lines = text.splitlines()
    if len(lines) < 7:
        raise VolumetricParseError("VOLUME_CUBE_HEADER_INVALID", "CUBE header is truncated.")
    origin_row = _float_tokens(lines[2], 4, "VOLUME_CUBE_HEADER_INVALID")
    atom_count_signed = int(origin_row[0]) if origin_row[0].is_integer() else 0
    if atom_count_signed == 0:
        atom_count = 0
    elif atom_count_signed < 0:
        raise VolumetricParseError("VOLUME_CUBE_MULTI_ORBITAL_UNSUPPORTED", "Multi-orbital CUBE datasets are explicitly unsupported.")
    else:
        atom_count = atom_count_signed
    axis_rows = [_float_tokens(lines[3 + i], 4, "VOLUME_CUBE_AXIS_INVALID") for i in range(3)]
    counts = [int(row[0]) if row[0].is_integer() else 0 for row in axis_rows]
    if any(value == 0 for value in counts) or len({value > 0 for value in counts}) != 1:
        raise VolumetricParseError("VOLUME_CUBE_AXIS_INVALID", "CUBE axis counts must be nonzero integers with consistent unit signs.")
    source_unit = "bohr" if counts[0] > 0 else "angstrom"
    factor = BOHR_TO_ANGSTROM if source_unit == "bohr" else 1.0
    shape = [abs(value) for value in counts]
    _check_shape(shape)
    origin = [origin_row[i] * factor for i in range(1, 4)]
    steps = [[row[i] * factor for i in range(1, 4)] for row in axis_rows]
    atoms: list[dict[str, Any]] = []
    for idx in range(atom_count):
        row = _float_tokens(lines[6 + idx], 5, "VOLUME_CUBE_ATOM_INVALID")
        atomic_number = int(row[0]) if row[0].is_integer() else -1
        if atomic_number < 0 or atomic_number > 118:
            raise VolumetricParseError("VOLUME_CUBE_ATOM_INVALID", "CUBE atomic number is invalid.")
        atoms.append({"atomic_number": atomic_number, "source_charge": row[1], "cartesian_angstrom": [row[i] * factor for i in range(2, 5)]})
    value_count = math.prod(shape)
    values, cursor = _read_numeric_values(lines, 6 + atom_count, value_count)
    if any(line.strip() for line in lines[cursor:]):
        raise VolumetricParseError("VOLUME_CUBE_TRAILING_DATA", "CUBE contains unexpected trailing or additional dataset values.")
    quantity = quantity_hint if quantity_hint != "auto" else "generic_scalar"
    if quantity not in {"electron_density", "charge_density", "spin_density", "magnetization_density", "electrostatic_potential", "orbital_density", "generic_scalar"}:
        raise VolumetricParseError("VOLUME_QUANTITY_HINT_INVALID", "CUBE quantity hint is unsupported.")
    canonical_unit, value_factor, integral = _cube_quantity_policy(quantity, source_unit)
    channel = {"name": "scalar", "quantity": quantity, "source_unit": canonical_unit if value_factor == 1.0 else "electron/bohr^3", "canonical_unit": canonical_unit, "conversion_factor": value_factor, "values": [value * value_factor for value in values], "normalization_semantics": "source_native", "integral_semantics": integral, "spin_channel": None}
    return {
        "source_format": "gaussian_cube", "source_name": _safe_name(source_name), "source_sha256": "", "shape": shape,
        "origin_cartesian": origin, "step_matrix": steps, "boundary_conditions": ["non_periodic"] * 3,
        "endpoint_policy": "not_applicable", "sample_location": "node", "structure": None, "structure_sha256": None,
        "lattice_matrix": None, "atom_records": atoms, "source_spatial_unit": source_unit, "channels": [channel], "warnings": [],
    }, {"detector_reasons": ["CUBE atom/origin row", "three bounded affine axes", "finite scalar payload"], "atom_count": atom_count, "source_spatial_unit": source_unit, "source_order": "i_outer_j_middle_k_fastest", "canonical_order": "ijkc_component_fastest"}


def _cube_quantity_policy(quantity: str, spatial_unit: str) -> tuple[str, float, str]:
    if quantity in {"electron_density", "orbital_density"}:
        factor = (1.0 / BOHR_TO_ANGSTROM**3) if spatial_unit == "bohr" else 1.0
        return "electron/angstrom^3", factor, "electron_count"
    if quantity == "charge_density":
        factor = (1.0 / BOHR_TO_ANGSTROM**3) if spatial_unit == "bohr" else 1.0
        return "elementary_charge/angstrom^3", factor, "elementary_charge"
    if quantity in {"spin_density", "magnetization_density"}:
        factor = (1.0 / BOHR_TO_ANGSTROM**3) if spatial_unit == "bohr" else 1.0
        return "bohr_magneton/angstrom^3", factor, "magnetic_moment"
    if quantity == "electrostatic_potential":
        return "hartree", 1.0, "cell_average"
    return "dimensionless", 1.0, "not_physically_interpreted"


def _vasp_header_end(lines: list[str]) -> tuple[int, int]:
    if len(lines) < 8:
        raise VolumetricParseError("VOLUME_VASP_STRUCTURE_INVALID", "VASP header is truncated.")
    species_or_counts = lines[5].split()
    counts_index = 5 if species_or_counts and all(_is_int(item) for item in species_or_counts) else 6
    if counts_index >= len(lines):
        raise VolumetricParseError("VOLUME_VASP_STRUCTURE_INVALID", "VASP atom counts are missing.")
    counts = lines[counts_index].split()
    if not counts or not all(_is_int(item) and int(item) >= 0 for item in counts):
        raise VolumetricParseError("VOLUME_VASP_STRUCTURE_INVALID", "VASP atom counts are invalid.")
    atom_count = sum(int(item) for item in counts)
    coordinate_index = counts_index + 1
    if lines[coordinate_index].strip().lower().startswith("s"):
        coordinate_index += 1
    end = coordinate_index + 1 + atom_count
    if end > len(lines):
        raise VolumetricParseError("VOLUME_VASP_STRUCTURE_INVALID", "VASP coordinate rows are truncated.")
    return end, atom_count


def _read_numeric_values(lines: list[str], start: int, count: int) -> tuple[list[float], int]:
    values: list[float] = []
    cursor = start
    while cursor < len(lines) and len(values) < count:
        parts = lines[cursor].split()
        cursor += 1
        for part in parts:
            try:
                value = float(part.replace("D", "E").replace("d", "e"))
            except ValueError as exc:
                raise VolumetricParseError("VOLUME_NUMERIC_INVALID", "Volumetric payload contains a malformed number.") from exc
            if not math.isfinite(value):
                raise VolumetricParseError("VOLUME_NUMERIC_NONFINITE", "Volumetric payload values must be finite.")
            values.append(value)
            if len(values) > count:
                raise VolumetricParseError("VOLUME_VALUE_COUNT_MISMATCH", "Volumetric payload contains too many values before a section boundary.")
    if len(values) != count:
        raise VolumetricParseError("VOLUME_VALUE_COUNT_MISMATCH", "Volumetric payload is truncated.")
    return values, cursor


def _vasp_to_canonical(values: list[float], shape: list[int]) -> list[float]:
    nx, ny, nz = shape
    return [values[i + nx * (j + ny * k)] for i in range(nx) for j in range(ny) for k in range(nz)]


def _find_matching_shape(lines: list[str], start: int, shape: list[int]) -> int | None:
    for idx in range(start, len(lines)):
        parts = lines[idx].split()
        if len(parts) == 3 and all(_is_int(item) for item in parts) and [int(item) for item in parts] == shape:
            return idx
    return None


def _next_nonempty(lines: list[str], start: int) -> int:
    for idx in range(start, len(lines)):
        if lines[idx].strip():
            return idx
    raise VolumetricParseError("VOLUME_GRID_MISSING", "Volumetric grid dimensions are missing.")


def _parse_shape(line: str, code: str) -> list[int]:
    parts = line.split()
    if len(parts) != 3 or not all(_is_int(item) for item in parts):
        raise VolumetricParseError(code, "Grid shape must contain exactly three positive integers.")
    return [int(item) for item in parts]


def _check_shape(shape: list[int]) -> None:
    if any(item <= 0 or item > VOLUMETRIC_CAPS["max_grid_dimension"] for item in shape) or math.prod(shape) > min(VOLUMETRIC_CAPS["max_total_voxels"], MAX_PARSER_VOXELS):
        raise VolumetricParseError("VOLUME_GRID_CAP_EXCEEDED", "Volumetric grid exceeds canonical caps.")


def _bounded_readline(handle: Any) -> str:
    line = handle.readline(MAX_LINE_BYTES + 1)
    _check_line(line)
    return line


def _check_line(line: str) -> None:
    if len(line.encode("utf-8")) > MAX_LINE_BYTES:
        raise VolumetricParseError("VOLUME_LINE_TOO_LONG", "Volumetric source line exceeds parser caps.")
    if "\x00" in line:
        raise VolumetricParseError("VOLUME_TEXT_ENCODING_INVALID", "Volumetric source contains a null byte.")


def _next_stream_nonempty(handle: Any) -> str:
    while True:
        line = _bounded_readline(handle)
        if line == "":
            raise VolumetricParseError("VOLUME_GRID_MISSING", "Volumetric grid dimensions are missing.")
        if line.strip():
            return line


def _read_stream_values(handle: Any, count: int) -> list[float]:
    values: list[float] = []
    while len(values) < count:
        line = _bounded_readline(handle)
        if line == "":
            raise VolumetricParseError("VOLUME_VALUE_COUNT_MISMATCH", "Volumetric payload is truncated.")
        for part in line.split():
            if len(part) > 128:
                raise VolumetricParseError("VOLUME_NUMERIC_TOKEN_TOO_LONG", "Volumetric numeric token exceeds parser caps.")
            try:
                value = float(part.replace("D", "E").replace("d", "e"))
            except ValueError as exc:
                raise VolumetricParseError("VOLUME_NUMERIC_INVALID", "Volumetric payload contains a malformed number.") from exc
            if not math.isfinite(value):
                raise VolumetricParseError("VOLUME_NUMERIC_NONFINITE", "Volumetric payload values must be finite.")
            values.append(value)
            if len(values) > count:
                raise VolumetricParseError("VOLUME_VALUE_COUNT_MISMATCH", "Volumetric payload contains too many values before a section boundary.")
    return values


def _stream_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while True:
            chunk = handle.read(1_048_576)
            if not chunk:
                break
            digest.update(chunk)
    return digest.hexdigest()


def _float_tokens(line: str, minimum: int, code: str) -> list[float]:
    parts = line.split()
    if len(parts) < minimum:
        raise VolumetricParseError(code, "Required numeric row is missing values.")
    try:
        values = [float(item.replace("D", "E").replace("d", "e")) for item in parts[:minimum]]
    except ValueError as exc:
        raise VolumetricParseError(code, "Required numeric row is malformed.") from exc
    if not all(math.isfinite(value) for value in values):
        raise VolumetricParseError(code, "Required numeric row contains non-finite values.")
    return values


def _looks_like_cube(lines: list[str]) -> bool:
    try:
        if len(lines) < 6:
            return False
        _float_tokens(lines[2], 4, "x")
        for idx in range(3, 6):
            row = _float_tokens(lines[idx], 4, "x")
            if not row[0].is_integer() or int(row[0]) == 0:
                return False
        return True
    except VolumetricParseError:
        return False


def _looks_like_vasp(lines: list[str]) -> bool:
    try:
        end, _ = _vasp_header_end(lines)
        idx = _next_nonempty(lines, end)
        shape = _parse_shape(lines[idx], "x")
        return all(value > 0 for value in shape)
    except (VolumetricParseError, IndexError):
        return False


def _source_size(path: Path) -> int:
    try:
        if not path.is_file():
            raise OSError
        return path.stat().st_size
    except OSError as exc:
        raise VolumetricParseError("VOLUME_SOURCE_UNAVAILABLE", "Volumetric source file is unavailable.") from exc


def _read_head(path: Path) -> str:
    with path.open("rb") as handle:
        raw = handle.read(MAX_HEADER_BYTES)
    try:
        return raw.decode("utf-8", errors="strict")
    except UnicodeDecodeError as exc:
        raise VolumetricParseError("VOLUME_TEXT_ENCODING_INVALID", "Volumetric source header is not valid text.") from exc


def _is_int(value: str) -> bool:
    try:
        return str(int(value)) == value or int(value) == float(value)
    except ValueError:
        return False


def _safe_name(value: str) -> str:
    name = Path(value).name[:96]
    return "".join(char if char.isalnum() or char in "._-" else "_" for char in name) or "volumetric-source"
