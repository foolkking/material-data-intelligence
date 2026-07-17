from __future__ import annotations

import gzip
import hashlib
import io
import json
import math
import re
import struct
import unicodedata
import zlib
from dataclasses import dataclass
from typing import Any, Iterable, Mapping, Sequence


VOLUMETRIC_GRID_SCHEMA_VERSION = "phase10j.volumetric_grid.v1"
VOLUMETRIC_PAYLOAD_SCHEMA_VERSION = "phase10j.volumetric_payload.v1"
VOLUMETRIC_FIELD_SCHEMA_VERSION = "phase10j.volumetric_field.v1"
VOLUMETRIC_DATASET_SCHEMA_VERSION = "phase10j.volumetric_dataset.v1"
VOLUMETRIC_MANIFEST_SCHEMA_VERSION = "phase10j.volumetric_manifest.v1"
VOLUMETRIC_TOLERANCE_SCHEMA_VERSION = "phase10j.volumetric_tolerances.v1"

VOLUMETRIC_TOLERANCES: dict[str, float | str] = {
    "schema_version": VOLUMETRIC_TOLERANCE_SCHEMA_VERSION,
    "matrix_absolute": 1e-9,
    "relative": 1e-9,
    "endpoint": 1e-10,
    "determinant_relative_minimum": 1e-12,
    "maximum_condition_number": 1e8,
}

VOLUMETRIC_CAPS: dict[str, int] = {
    "max_grid_dimension": 512,
    "max_total_voxels": 16_777_216,
    "max_stored_values": 50_331_648,
    "max_fields_per_dataset": 8,
    "max_chunks_per_field": 256,
    "max_uncompressed_bytes_per_field": 268_435_456,
    "max_compressed_bytes_per_field": 134_217_728,
    "max_dataset_bytes": 536_870_912,
    "max_compression_ratio": 128,
    "max_inline_values": 262_144,
    "max_inline_json_bytes": 4_194_304,
    "max_metadata_bytes": 65_536,
    "max_name_length": 96,
    "max_unit_length": 64,
    "max_warnings": 32,
    "max_histogram_bins": 256,
    "max_provenance_entries": 32,
}

VOLUMETRIC_SECURITY = {
    "contains_javascript": False,
    "contains_html": False,
    "contains_css": False,
    "contains_shader": False,
    "contains_executable": False,
    "external_urls_allowed": False,
    "renderer_included": False,
}

DTYPE_FORMATS = {"float32": ("f", 4), "float64": ("d", 8)}
SAMPLE_LOCATIONS = frozenset({"node", "cell_center"})
ENDPOINT_POLICIES = frozenset({"excluded", "included", "not_applicable"})
BOUNDARY_CONDITIONS = frozenset({"periodic", "non_periodic"})
PAYLOAD_ENCODINGS = frozenset({"inline_json", "raw_binary", "gzip_binary", "chunked_binary"})
FIELD_QUANTITIES = frozenset(
    {
        "generic_scalar",
        "charge_density",
        "electron_density",
        "spin_density",
        "magnetization_density",
        "electrostatic_potential",
        "local_potential",
        "electron_localization_function",
        "orbital_density",
        "wavefunction",
        "custom_declared",
    }
)
UNITS = frozenset(
    {
        "dimensionless",
        "electron/angstrom^3",
        "elementary_charge/angstrom^3",
        "electron/bohr^3",
        "volt",
        "electronvolt",
        "hartree",
        "hartree/elementary_charge",
        "angstrom^-3",
        "bohr_magneton/angstrom^3",
        "custom_declared",
    }
)
NORMALIZATION_SEMANTICS = frozenset(
    {
        "source_native",
        "normalized_to_unit_integral",
        "normalized_to_electron_count",
        "normalized_to_charge",
        "not_normalized",
        "unknown",
    }
)
INTEGRAL_SEMANTICS = frozenset(
    {
        "electron_count",
        "elementary_charge",
        "magnetic_moment",
        "cell_average",
        "zero_by_definition",
        "not_physically_interpreted",
        "unknown",
    }
)
POTENTIAL_REFERENCES = frozenset(
    {"absolute_declared", "cell_average_zero", "vacuum_reference", "fermi_reference", "source_defined", "unknown"}
)
SPIN_REPRESENTATIONS = frozenset({"collinear", "non_collinear"})
SPIN_CHANNELS = frozenset(
    {
        "total",
        "spin_up",
        "spin_down",
        "spin_difference",
        "magnetization_x",
        "magnetization_y",
        "magnetization_z",
        "magnetization_vector",
    }
)

_SAFE_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,95}$")
_SHA256 = re.compile(r"^[0-9a-f]{64}$")
_FORBIDDEN_KEYS = frozenset(
    {
        "__proto__",
        "callback",
        "code",
        "constructor",
        "eval",
        "function",
        "html",
        "iframe",
        "module",
        "prototype",
        "script",
        "shader",
        "src",
        "texture",
        "url",
        "urls",
    }
)
_FORBIDDEN_MARKERS = ("http://", "https://", "javascript:", "<script", "<iframe", "file://", "new function", "eval(")


class VolumetricContractError(ValueError):
    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code


@dataclass(frozen=True)
class VolumetricValidationResult:
    valid: bool
    errors: tuple[str, ...]
    warnings: tuple[str, ...] = ()


@dataclass(frozen=True)
class VolumetricPayloadBundle:
    metadata: dict[str, Any]
    artifacts: dict[str, bytes]


def _canonical_value(value: Any) -> Any:
    if isinstance(value, dict):
        return {unicodedata.normalize("NFC", str(key)): _canonical_value(item) for key, item in sorted(value.items())}
    if isinstance(value, (list, tuple)):
        return [_canonical_value(item) for item in value]
    if isinstance(value, float):
        if not math.isfinite(value):
            raise VolumetricContractError("VOLUME_NON_FINITE_VALUE", "A finite numeric value is required.")
        return 0.0 if value == 0 else value
    return value


def stable_volumetric_json(value: Any) -> str:
    return json.dumps(_canonical_value(value), ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def volumetric_content_hash(value: bytes | str | Any) -> str:
    if isinstance(value, bytes):
        raw = value
    elif isinstance(value, str):
        raw = value.encode("utf-8")
    else:
        raw = stable_volumetric_json(value).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def volumetric_lattice_hash(matrix: Sequence[Sequence[float]]) -> str:
    return volumetric_content_hash(_matrix3(matrix, "VOLUME_LATTICE_INVALID"))


def _finite(value: Any) -> bool:
    return type(value) in {int, float} and math.isfinite(float(value))


def _positive_int(value: Any) -> bool:
    return type(value) is int and value > 0


def _safe_id(value: Any) -> bool:
    return isinstance(value, str) and _SAFE_ID.fullmatch(value) is not None


def _safe_text(value: Any, limit: int) -> bool:
    if not isinstance(value, str) or not value or len(value) > limit or any(ord(char) < 32 for char in value):
        return False
    lowered = value.lower()
    return not any(marker in lowered for marker in _FORBIDDEN_MARKERS)


def _safe_product(values: Sequence[int], cap: int, code: str) -> int:
    product = 1
    for value in values:
        if not _positive_int(value) or value > cap or product > cap // value:
            raise VolumetricContractError(code, "A bounded positive shape is required.")
        product *= value
    return product


def _vector3(value: Any, code: str) -> list[float]:
    if not isinstance(value, (list, tuple)) or len(value) != 3 or not all(_finite(item) for item in value):
        raise VolumetricContractError(code, "A finite three-vector is required.")
    return [0.0 if float(item) == 0 else float(item) for item in value]


def _matrix3(value: Any, code: str) -> list[list[float]]:
    if not isinstance(value, (list, tuple)) or len(value) != 3:
        raise VolumetricContractError(code, "A finite 3x3 row matrix is required.")
    return [_vector3(row, code) for row in value]


def determinant3(matrix: Sequence[Sequence[float]]) -> float:
    a, b, c = _matrix3(matrix, "VOLUME_GRID_BASIS_INVALID")
    return (
        a[0] * (b[1] * c[2] - b[2] * c[1])
        - a[1] * (b[0] * c[2] - b[2] * c[0])
        + a[2] * (b[0] * c[1] - b[1] * c[0])
    )


def inverse3(matrix: Sequence[Sequence[float]]) -> list[list[float]]:
    m = _matrix3(matrix, "VOLUME_GRID_BASIS_INVALID")
    determinant = determinant3(m)
    scale = max(abs(item) for row in m for item in row)
    threshold = float(VOLUMETRIC_TOLERANCES["determinant_relative_minimum"]) * max(scale**3, 1.0)
    if not math.isfinite(determinant) or abs(determinant) <= threshold:
        raise VolumetricContractError("VOLUME_GRID_BASIS_SINGULAR", "The grid basis is singular or near singular.")
    a, b, c = m
    inverse = [
        [(b[1] * c[2] - b[2] * c[1]) / determinant, (a[2] * c[1] - a[1] * c[2]) / determinant, (a[1] * b[2] - a[2] * b[1]) / determinant],
        [(b[2] * c[0] - b[0] * c[2]) / determinant, (a[0] * c[2] - a[2] * c[0]) / determinant, (a[2] * b[0] - a[0] * b[2]) / determinant],
        [(b[0] * c[1] - b[1] * c[0]) / determinant, (a[1] * c[0] - a[0] * c[1]) / determinant, (a[0] * b[1] - a[1] * b[0]) / determinant],
    ]
    norm = max(sum(abs(item) for item in row) for row in m)
    inverse_norm = max(sum(abs(item) for item in row) for row in inverse)
    if norm * inverse_norm > float(VOLUMETRIC_TOLERANCES["maximum_condition_number"]):
        raise VolumetricContractError("VOLUME_GRID_BASIS_ILL_CONDITIONED", "The grid basis is ill conditioned.")
    return inverse


def row_vector_multiply(vector: Sequence[float], matrix: Sequence[Sequence[float]]) -> list[float]:
    v = _vector3(vector, "VOLUME_COORDINATE_INVALID")
    m = _matrix3(matrix, "VOLUME_GRID_BASIS_INVALID")
    return [sum(v[row] * m[row][axis] for row in range(3)) for axis in range(3)]


def cartesian_to_grid_coordinates(cartesian: Sequence[float], grid: Mapping[str, Any]) -> list[float]:
    origin = _vector3(grid.get("origin_cartesian"), "VOLUME_ORIGIN_INVALID")
    inverse = inverse3(grid.get("step_matrix"))
    return row_vector_multiply([float(cartesian[i]) - origin[i] for i in range(3)], inverse)


def grid_sample_cartesian(grid: Mapping[str, Any], index: Sequence[int]) -> list[float]:
    if not isinstance(index, (list, tuple)) or len(index) != 3 or any(type(item) is not int for item in index):
        raise VolumetricContractError("VOLUME_GRID_INDEX_INVALID", "A three-dimensional integer index is required.")
    shape = grid.get("shape")
    if not isinstance(shape, list) or any(item < 0 or item >= shape[axis] for axis, item in enumerate(index)):
        raise VolumetricContractError("VOLUME_GRID_INDEX_INVALID", "The index is outside the grid.")
    shift = 0.5 if grid.get("sample_location") == "cell_center" else 0.0
    local = [float(item) + shift for item in index]
    step = _matrix3(grid.get("step_matrix"), "VOLUME_GRID_BASIS_INVALID")
    origin = _vector3(grid.get("origin_cartesian"), "VOLUME_ORIGIN_INVALID")
    translated = row_vector_multiply(local, step)
    return [origin[axis] + translated[axis] for axis in range(3)]


def wrap_fractional(value: Sequence[float]) -> list[float]:
    result: list[float] = []
    tolerance = float(VOLUMETRIC_TOLERANCES["endpoint"])
    for item in _vector3(value, "VOLUME_COORDINATE_INVALID"):
        wrapped = item - math.floor(item)
        if abs(wrapped) <= tolerance or abs(wrapped - 1.0) <= tolerance:
            wrapped = 0.0
        result.append(wrapped)
    return result


def flatten_offset(
    index: Sequence[int], component: int, shape: Sequence[int], stored_component_count: int
) -> int:
    if not isinstance(index, (list, tuple)) or len(index) != 3 or type(component) is not int:
        raise VolumetricContractError("VOLUME_FLATTEN_INDEX_INVALID", "A valid grid/component index is required.")
    if not isinstance(shape, (list, tuple)) or len(shape) != 3 or not _positive_int(stored_component_count):
        raise VolumetricContractError("VOLUME_LOGICAL_SHAPE_INVALID", "A valid logical shape is required.")
    i, j, k = index
    nx, ny, nz = shape
    if any(type(item) is not int for item in index) or not (0 <= i < nx and 0 <= j < ny and 0 <= k < nz and 0 <= component < stored_component_count):
        raise VolumetricContractError("VOLUME_FLATTEN_INDEX_INVALID", "The index is outside the payload.")
    return ((((i * ny) + j) * nz + k) * stored_component_count) + component


def _grid_identity_payload(grid: Mapping[str, Any]) -> dict[str, Any]:
    return {key: grid[key] for key in grid if key not in {"grid_id", "content_hash"}}


def build_volumetric_grid(
    *,
    shape: Sequence[int],
    origin_cartesian: Sequence[float],
    step_matrix: Sequence[Sequence[float]],
    sample_location: str,
    boundary_conditions: Sequence[str],
    endpoint_policy: str,
    structure_binding: Mapping[str, Any] | None = None,
    origin_fractional: Sequence[float] | None = None,
) -> dict[str, Any]:
    dimensions = list(shape)
    if len(dimensions) != 3 or any(not _positive_int(item) or item > VOLUMETRIC_CAPS["max_grid_dimension"] for item in dimensions):
        raise VolumetricContractError("VOLUME_GRID_SHAPE_INVALID", "A bounded three-dimensional shape is required.")
    _safe_product(dimensions, VOLUMETRIC_CAPS["max_total_voxels"], "VOLUME_VOXEL_CAP_EXCEEDED")
    if sample_location not in SAMPLE_LOCATIONS or endpoint_policy not in ENDPOINT_POLICIES:
        raise VolumetricContractError("VOLUME_GRID_SAMPLING_INVALID", "Sample and endpoint policies must be explicit.")
    boundaries = list(boundary_conditions)
    if len(boundaries) != 3 or any(item not in BOUNDARY_CONDITIONS for item in boundaries):
        raise VolumetricContractError("VOLUME_BOUNDARY_INVALID", "Three boundary conditions are required.")
    if len(set(boundaries)) != 1:
        raise VolumetricContractError("VOLUME_MIXED_PERIODICITY_UNSUPPORTED", "Mixed periodicity is not supported.")
    origin = _vector3(origin_cartesian, "VOLUME_ORIGIN_INVALID")
    steps = _matrix3(step_matrix, "VOLUME_GRID_BASIS_INVALID")
    inverse3(steps)
    periodic = boundaries[0] == "periodic"
    binding: dict[str, Any] | None = None
    fractional: list[float] | None = None
    if periodic:
        if endpoint_policy != "excluded" or not isinstance(structure_binding, Mapping):
            raise VolumetricContractError("VOLUME_PERIODIC_GRID_INVALID", "Periodic grids require excluded endpoints and structure binding.")
        required = {"structure_sha256", "lattice_sha256", "lattice_matrix", "basis_role"}
        if set(structure_binding) != required or not _SHA256.fullmatch(str(structure_binding.get("structure_sha256"))) or not _SHA256.fullmatch(str(structure_binding.get("lattice_sha256"))):
            raise VolumetricContractError("VOLUME_STRUCTURE_BINDING_INVALID", "A canonical structure/lattice binding is required.")
        lattice = _matrix3(structure_binding.get("lattice_matrix"), "VOLUME_LATTICE_INVALID")
        inverse3(lattice)
        if structure_binding.get("basis_role") != "canonical_structure_cell" or structure_binding.get("lattice_sha256") != volumetric_lattice_hash(lattice):
            raise VolumetricContractError("VOLUME_STRUCTURE_BINDING_INVALID", "The lattice basis role is invalid.")
        expected = [[dimensions[row] * steps[row][axis] for axis in range(3)] for row in range(3)]
        if not _matrix_near(expected, lattice):
            raise VolumetricContractError("VOLUME_GRID_LATTICE_MISMATCH", "Grid steps do not span the bound lattice.")
        fractional = wrap_fractional(origin_fractional if origin_fractional is not None else row_vector_multiply(origin, inverse3(lattice)))
        if not _vector_near(row_vector_multiply(fractional, lattice), origin):
            shifted = [origin[axis] - row_vector_multiply(fractional, lattice)[axis] for axis in range(3)]
            if not _lattice_translation(shifted, lattice):
                raise VolumetricContractError("VOLUME_ORIGIN_INVALID", "Cartesian and fractional origins are inconsistent.")
        binding = {
            "structure_sha256": str(structure_binding["structure_sha256"]),
            "lattice_sha256": str(structure_binding["lattice_sha256"]),
            "lattice_matrix": lattice,
            "basis_role": "canonical_structure_cell",
        }
    elif structure_binding is not None or origin_fractional is not None:
        raise VolumetricContractError("VOLUME_NONPERIODIC_BINDING_INVALID", "Non-periodic affine grids cannot claim periodic structure binding.")
    extent = [[dimensions[row] * steps[row][axis] for axis in range(3)] for row in range(3)]
    grid: dict[str, Any] = {
        "schema_version": VOLUMETRIC_GRID_SCHEMA_VERSION,
        "grid_id": "",
        "coordinate_space": "real_cartesian",
        "length_unit": "angstrom",
        "shape": dimensions,
        "origin_cartesian": origin,
        "origin_fractional": fractional,
        "step_matrix": steps,
        "sample_location": sample_location,
        "boundary_conditions": boundaries,
        "endpoint_policy": endpoint_policy,
        "structure_binding": binding,
        "domain_extent_matrix": extent,
        "voxel_volume": abs(determinant3(steps)),
        "tolerance_policy": dict(VOLUMETRIC_TOLERANCES),
        "security": dict(VOLUMETRIC_SECURITY),
        "content_hash": "",
    }
    digest = volumetric_content_hash(_grid_identity_payload(grid))
    grid["grid_id"] = f"grid:{digest}"
    grid["content_hash"] = digest
    result = validate_volumetric_grid(grid)
    if not result.valid:
        raise VolumetricContractError(result.errors[0], "Generated volumetric grid is invalid.")
    return grid


def validate_volumetric_grid(value: Any) -> VolumetricValidationResult:
    errors: set[str] = set()
    fields = {
        "schema_version", "grid_id", "coordinate_space", "length_unit", "shape", "origin_cartesian",
        "origin_fractional", "step_matrix", "sample_location", "boundary_conditions", "endpoint_policy",
        "structure_binding", "domain_extent_matrix", "voxel_volume", "tolerance_policy", "security", "content_hash",
    }
    if not isinstance(value, dict) or set(value) != fields:
        return VolumetricValidationResult(False, ("VOLUME_GRID_SCHEMA_INVALID",))
    try:
        if value.get("schema_version") != VOLUMETRIC_GRID_SCHEMA_VERSION or value.get("coordinate_space") != "real_cartesian" or value.get("length_unit") != "angstrom":
            errors.add("VOLUME_GRID_SCHEMA_INVALID")
        shape = value.get("shape")
        if not isinstance(shape, list) or len(shape) != 3 or any(not _positive_int(item) or item > VOLUMETRIC_CAPS["max_grid_dimension"] for item in shape):
            errors.add("VOLUME_GRID_SHAPE_INVALID")
            shape = [1, 1, 1]
        _safe_product(shape, VOLUMETRIC_CAPS["max_total_voxels"], "VOLUME_VOXEL_CAP_EXCEEDED")
        _vector3(value.get("origin_cartesian"), "VOLUME_ORIGIN_INVALID")
        steps = _matrix3(value.get("step_matrix"), "VOLUME_GRID_BASIS_INVALID")
        inverse3(steps)
        boundaries = value.get("boundary_conditions")
        if not isinstance(boundaries, list) or len(boundaries) != 3 or any(item not in BOUNDARY_CONDITIONS for item in boundaries):
            errors.add("VOLUME_BOUNDARY_INVALID")
            boundaries = ["non_periodic"] * 3
        if len(set(boundaries)) != 1:
            errors.add("VOLUME_MIXED_PERIODICITY_UNSUPPORTED")
        if value.get("sample_location") not in SAMPLE_LOCATIONS or value.get("endpoint_policy") not in ENDPOINT_POLICIES:
            errors.add("VOLUME_GRID_SAMPLING_INVALID")
        if boundaries[0] == "periodic":
            if value.get("endpoint_policy") != "excluded":
                errors.add("VOLUME_ENDPOINT_POLICY_INVALID")
            binding = value.get("structure_binding")
            if not isinstance(binding, dict) or set(binding) != {"structure_sha256", "lattice_sha256", "lattice_matrix", "basis_role"}:
                errors.add("VOLUME_STRUCTURE_BINDING_INVALID")
            else:
                lattice = _matrix3(binding.get("lattice_matrix"), "VOLUME_LATTICE_INVALID")
                if not _SHA256.fullmatch(str(binding.get("structure_sha256"))) or binding.get("lattice_sha256") != volumetric_lattice_hash(lattice) or binding.get("basis_role") != "canonical_structure_cell":
                    errors.add("VOLUME_STRUCTURE_BINDING_INVALID")
                expected = [[shape[row] * steps[row][axis] for axis in range(3)] for row in range(3)]
                if not _matrix_near(expected, lattice):
                    errors.add("VOLUME_GRID_LATTICE_MISMATCH")
                fractional = _vector3(value.get("origin_fractional"), "VOLUME_ORIGIN_INVALID")
                if not _vector_near(fractional, wrap_fractional(fractional)):
                    errors.add("VOLUME_ORIGIN_INVALID")
        elif value.get("structure_binding") is not None or value.get("origin_fractional") is not None:
            errors.add("VOLUME_NONPERIODIC_BINDING_INVALID")
        expected_extent = [[shape[row] * steps[row][axis] for axis in range(3)] for row in range(3)]
        if not _matrix_near(_matrix3(value.get("domain_extent_matrix"), "VOLUME_GRID_BASIS_INVALID"), expected_extent):
            errors.add("VOLUME_DOMAIN_EXTENT_INVALID")
        if not _number_near(value.get("voxel_volume"), abs(determinant3(steps))):
            errors.add("VOLUME_VOXEL_VOLUME_INVALID")
        if value.get("tolerance_policy") != VOLUMETRIC_TOLERANCES or value.get("security") != VOLUMETRIC_SECURITY:
            errors.add("VOLUME_SECURITY_INVALID")
        digest = volumetric_content_hash(_grid_identity_payload(value))
        if value.get("content_hash") != digest or value.get("grid_id") != f"grid:{digest}":
            errors.add("VOLUME_CONTENT_HASH_MISMATCH")
        _scan_inert(value)
    except VolumetricContractError as error:
        errors.add(error.code)
    except (TypeError, ValueError, OverflowError, RecursionError):
        errors.add("VOLUME_GRID_SCHEMA_INVALID")
    return VolumetricValidationResult(not errors, tuple(sorted(errors)))


def _matrix_near(left: Sequence[Sequence[float]], right: Sequence[Sequence[float]]) -> bool:
    return all(_number_near(left[row][axis], right[row][axis]) for row in range(3) for axis in range(3))


def _vector_near(left: Sequence[float], right: Sequence[float]) -> bool:
    return all(_number_near(left[index], right[index]) for index in range(3))


def _number_near(left: Any, right: Any) -> bool:
    if not _finite(left) or not _finite(right):
        return False
    absolute = float(VOLUMETRIC_TOLERANCES["matrix_absolute"])
    relative = float(VOLUMETRIC_TOLERANCES["relative"])
    return abs(float(left) - float(right)) <= absolute + relative * max(abs(float(left)), abs(float(right)), 1.0)


def _lattice_translation(vector: Sequence[float], lattice: Sequence[Sequence[float]]) -> bool:
    fractional = row_vector_multiply(vector, inverse3(lattice))
    return all(abs(item - round(item)) <= float(VOLUMETRIC_TOLERANCES["endpoint"]) for item in fractional)


def _scan_inert(value: Any, depth: int = 0) -> None:
    if depth > 32:
        raise VolumetricContractError("VOLUME_METADATA_CAP_EXCEEDED", "Metadata nesting is too deep.")
    if isinstance(value, dict):
        for key, item in value.items():
            if str(key).lower() in _FORBIDDEN_KEYS:
                raise VolumetricContractError("VOLUME_EXECUTABLE_METADATA_FORBIDDEN", "Executable metadata is forbidden.")
            _scan_inert(item, depth + 1)
    elif isinstance(value, list):
        for item in value:
            _scan_inert(item, depth + 1)
    elif isinstance(value, str):
        lowered = value.lower()
        if any(marker in lowered for marker in _FORBIDDEN_MARKERS):
            raise VolumetricContractError("VOLUME_EXTERNAL_REFERENCE_FORBIDDEN", "External or executable references are forbidden.")


def stored_component_count(value_kind: str, field_rank: str) -> int:
    if value_kind == "real" and field_rank == "scalar":
        return 1
    if value_kind == "real" and field_rank == "vector":
        return 3
    if value_kind == "complex" and field_rank == "scalar":
        return 2
    raise VolumetricContractError("VOLUME_FIELD_KIND_UNSUPPORTED", "Only real scalar/vector and complex scalar fields are supported.")


def _pack_values(values: Iterable[float], dtype: str) -> bytes:
    if dtype not in DTYPE_FORMATS:
        raise VolumetricContractError("VOLUME_DTYPE_UNSUPPORTED", "Only float32 and float64 are supported.")
    format_code, _ = DTYPE_FORMATS[dtype]
    packed = bytearray()
    for value in values:
        if not _finite(value):
            raise VolumetricContractError("VOLUME_NON_FINITE_VALUE", "Payload values must be finite.")
        packed.extend(struct.pack(f"<{format_code}", 0.0 if float(value) == 0 else float(value)))
    return bytes(packed)


def _unpack_values(raw: bytes, dtype: str) -> list[float]:
    if dtype not in DTYPE_FORMATS:
        raise VolumetricContractError("VOLUME_DTYPE_UNSUPPORTED", "Only float32 and float64 are supported.")
    format_code, size = DTYPE_FORMATS[dtype]
    if len(raw) % size:
        raise VolumetricContractError("VOLUME_PAYLOAD_BYTE_MISMATCH", "Payload bytes do not align to dtype.")
    values = [item[0] for item in struct.iter_unpack(f"<{format_code}", raw)]
    if not all(math.isfinite(item) for item in values):
        raise VolumetricContractError("VOLUME_NON_FINITE_VALUE", "Payload values must be finite.")
    return values


def deterministic_gzip(raw: bytes) -> bytes:
    output = io.BytesIO()
    with gzip.GzipFile(filename="", mode="wb", fileobj=output, compresslevel=9, mtime=0) as stream:
        stream.write(raw)
    return output.getvalue()


def _bounded_gzip_decompress(compressed: bytes, expected_bytes: int) -> bytes:
    if len(compressed) > VOLUMETRIC_CAPS["max_compressed_bytes_per_field"]:
        raise VolumetricContractError("VOLUME_COMPRESSED_CAP_EXCEEDED", "Compressed payload exceeds the hard cap.")
    if expected_bytes > VOLUMETRIC_CAPS["max_uncompressed_bytes_per_field"]:
        raise VolumetricContractError("VOLUME_DECOMPRESSION_CAP_EXCEEDED", "Uncompressed payload exceeds the hard cap.")
    if not compressed or expected_bytes > max(1, len(compressed)) * VOLUMETRIC_CAPS["max_compression_ratio"]:
        raise VolumetricContractError("VOLUME_COMPRESSION_RATIO_EXCEEDED", "Compression ratio exceeds the hard cap.")
    try:
        decoder = zlib.decompressobj(wbits=31)
        raw = decoder.decompress(compressed, expected_bytes + 1)
        raw += decoder.flush()
    except zlib.error as error:
        raise VolumetricContractError("VOLUME_DECOMPRESSION_FAILED", "Gzip payload could not be decoded.") from error
    if decoder.unused_data or decoder.unconsumed_tail:
        raise VolumetricContractError("VOLUME_GZIP_MEMBER_INVALID", "Nested or multi-member gzip payloads are forbidden.")
    if len(raw) != expected_bytes:
        raise VolumetricContractError("VOLUME_DECOMPRESSED_BYTE_MISMATCH", "Decompressed payload length is invalid.")
    return raw


def _payload_base(
    *,
    encoding: str,
    dtype: str,
    grid_shape: Sequence[int],
    components: int,
    logical_sha256: str,
    uncompressed_bytes: int,
) -> dict[str, Any]:
    shape = list(grid_shape)
    voxels = _safe_product(shape, VOLUMETRIC_CAPS["max_total_voxels"], "VOLUME_VOXEL_CAP_EXCEEDED")
    value_count = _safe_product([voxels, components], VOLUMETRIC_CAPS["max_stored_values"], "VOLUME_VALUE_CAP_EXCEEDED")
    if dtype not in DTYPE_FORMATS or uncompressed_bytes != value_count * DTYPE_FORMATS[dtype][1]:
        raise VolumetricContractError("VOLUME_PAYLOAD_BYTE_MISMATCH", "Payload byte length is invalid.")
    if uncompressed_bytes > VOLUMETRIC_CAPS["max_uncompressed_bytes_per_field"]:
        raise VolumetricContractError("VOLUME_PAYLOAD_CAP_EXCEEDED", "Payload exceeds the uncompressed byte cap.")
    return {
        "schema_version": VOLUMETRIC_PAYLOAD_SCHEMA_VERSION,
        "payload_id": "",
        "encoding": encoding,
        "dtype": dtype,
        "endianness": "little",
        "stored_component_count": components,
        "flatten_order": "ijkc_component_fastest",
        "grid_shape": shape,
        "logical_shape": [*shape, components],
        "value_count": value_count,
        "uncompressed_bytes": uncompressed_bytes,
        "compressed_bytes": 0,
        "media_type": None,
        "artifact_name": None,
        "inline_values": None,
        "chunks": [],
        "compression": {"codec": "none", "deterministic": True, "mtime": None, "filename": None},
        "logical_sha256": logical_sha256,
        "storage_sha256": None,
        "storage_layout_hash": "",
        "security": dict(VOLUMETRIC_SECURITY),
    }


def _finish_payload(payload: dict[str, Any]) -> dict[str, Any]:
    identity = {key: payload[key] for key in payload if key not in {"payload_id", "storage_layout_hash"}}
    layout_hash = volumetric_content_hash(identity)
    payload["payload_id"] = f"payload:{payload['logical_sha256']}"
    payload["storage_layout_hash"] = layout_hash
    return payload


def build_inline_payload(
    values: Sequence[float], *, grid_shape: Sequence[int], stored_components: int, dtype: str = "float64"
) -> VolumetricPayloadBundle:
    raw = _pack_values(values, dtype)
    payload = _payload_base(
        encoding="inline_json",
        dtype=dtype,
        grid_shape=grid_shape,
        components=stored_components,
        logical_sha256=volumetric_content_hash(raw),
        uncompressed_bytes=len(raw),
    )
    if payload["value_count"] > VOLUMETRIC_CAPS["max_inline_values"]:
        raise VolumetricContractError("VOLUME_INLINE_CAP_EXCEEDED", "Inline value count exceeds the hard cap.")
    normalized = [0.0 if float(value) == 0 else float(value) for value in values]
    if len(stable_volumetric_json(normalized).encode("utf-8")) > VOLUMETRIC_CAPS["max_inline_json_bytes"]:
        raise VolumetricContractError("VOLUME_INLINE_CAP_EXCEEDED", "Inline JSON exceeds the hard cap.")
    payload["inline_values"] = normalized
    payload["compressed_bytes"] = len(raw)
    payload["media_type"] = "application/json"
    payload["storage_sha256"] = volumetric_content_hash(stable_volumetric_json(normalized))
    return VolumetricPayloadBundle(_finish_payload(payload), {})


def build_binary_payload(
    values: Sequence[float],
    *,
    grid_shape: Sequence[int],
    stored_components: int,
    dtype: str = "float64",
    encoding: str = "raw_binary",
    artifact_name: str = "field.bin",
) -> VolumetricPayloadBundle:
    if encoding not in {"raw_binary", "gzip_binary"}:
        raise VolumetricContractError("VOLUME_ENCODING_UNSUPPORTED", "Binary payload encoding is unsupported.")
    if not _safe_artifact_name(artifact_name):
        raise VolumetricContractError("VOLUME_ARTIFACT_NAME_INVALID", "Artifact names must be safe logical names.")
    raw = _pack_values(values, dtype)
    payload = _payload_base(
        encoding=encoding,
        dtype=dtype,
        grid_shape=grid_shape,
        components=stored_components,
        logical_sha256=volumetric_content_hash(raw),
        uncompressed_bytes=len(raw),
    )
    stored = raw if encoding == "raw_binary" else deterministic_gzip(raw)
    if len(stored) > VOLUMETRIC_CAPS["max_compressed_bytes_per_field"]:
        raise VolumetricContractError("VOLUME_COMPRESSED_CAP_EXCEEDED", "Stored payload exceeds the hard cap.")
    if encoding == "gzip_binary" and len(raw) > max(1, len(stored)) * VOLUMETRIC_CAPS["max_compression_ratio"]:
        raise VolumetricContractError("VOLUME_COMPRESSION_RATIO_EXCEEDED", "Compression ratio exceeds the hard cap.")
    payload["artifact_name"] = artifact_name
    payload["compressed_bytes"] = len(stored)
    payload["media_type"] = "application/gzip" if encoding == "gzip_binary" else f"application/vnd.mdi.volumetric+{dtype}"
    payload["storage_sha256"] = volumetric_content_hash(stored)
    if encoding == "gzip_binary":
        payload["compression"] = {"codec": "gzip", "deterministic": True, "mtime": 0, "filename": None}
    return VolumetricPayloadBundle(_finish_payload(payload), {artifact_name: stored})


def build_chunked_payload(
    values: Sequence[float],
    *,
    grid_shape: Sequence[int],
    stored_components: int,
    dtype: str = "float64",
    chunk_i: int = 1,
    compression: str = "raw_binary",
    artifact_prefix: str = "field",
) -> VolumetricPayloadBundle:
    shape = list(grid_shape)
    if len(shape) != 3 or not _positive_int(chunk_i) or chunk_i > shape[0] or compression not in {"raw_binary", "gzip_binary"} or not _safe_id(artifact_prefix):
        raise VolumetricContractError("VOLUME_CHUNK_POLICY_INVALID", "Chunk policy is invalid.")
    raw = _pack_values(values, dtype)
    payload = _payload_base(
        encoding="chunked_binary",
        dtype=dtype,
        grid_shape=shape,
        components=stored_components,
        logical_sha256=volumetric_content_hash(raw),
        uncompressed_bytes=len(raw),
    )
    bytes_per_i = shape[1] * shape[2] * stored_components * DTYPE_FORMATS[dtype][1]
    artifacts: dict[str, bytes] = {}
    chunks: list[dict[str, Any]] = []
    for chunk_index, i_start in enumerate(range(0, shape[0], chunk_i)):
        if chunk_index >= VOLUMETRIC_CAPS["max_chunks_per_field"]:
            raise VolumetricContractError("VOLUME_CHUNK_CAP_EXCEEDED", "Chunk count exceeds the hard cap.")
        i_end = min(shape[0], i_start + chunk_i)
        logical = raw[i_start * bytes_per_i : i_end * bytes_per_i]
        stored = logical if compression == "raw_binary" else deterministic_gzip(logical)
        name = f"{artifact_prefix}.chunk-{chunk_index:04d}.{'gz' if compression == 'gzip_binary' else 'bin'}"
        artifacts[name] = stored
        chunks.append(
            {
                "chunk_id": f"chunk:{chunk_index:04d}",
                "i_start": i_start,
                "i_end": i_end,
                "logical_shape": [i_end - i_start, shape[1], shape[2], stored_components],
                "artifact_name": name,
                "encoding": compression,
                "media_type": "application/gzip" if compression == "gzip_binary" else f"application/vnd.mdi.volumetric+{dtype}",
                "uncompressed_bytes": len(logical),
                "compressed_bytes": len(stored),
                "logical_sha256": volumetric_content_hash(logical),
                "storage_sha256": volumetric_content_hash(stored),
            }
        )
    payload["chunks"] = chunks
    payload["compressed_bytes"] = sum(len(item) for item in artifacts.values())
    payload["media_type"] = "application/vnd.mdi.volumetric-chunks+json"
    payload["storage_sha256"] = volumetric_content_hash(
        [{"artifact_name": item["artifact_name"], "storage_sha256": item["storage_sha256"]} for item in chunks]
    )
    return VolumetricPayloadBundle(_finish_payload(payload), artifacts)


def _safe_artifact_name(value: Any) -> bool:
    return (
        isinstance(value, str)
        and 0 < len(value) <= 128
        and "/" not in value
        and "\\" not in value
        and ".." not in value
        and _SAFE_ID.fullmatch(value) is not None
    )


def decode_volumetric_payload(payload: Mapping[str, Any], artifacts: Mapping[str, bytes] | None = None) -> list[float]:
    result = validate_volumetric_payload(payload, artifacts)
    if not result.valid:
        raise VolumetricContractError(result.errors[0], "Volumetric payload validation failed.")
    if payload["encoding"] == "inline_json":
        return [float(item) for item in payload["inline_values"]]
    source = artifacts or {}
    if payload["encoding"] in {"raw_binary", "gzip_binary"}:
        stored = source[payload["artifact_name"]]
        raw = stored if payload["encoding"] == "raw_binary" else _bounded_gzip_decompress(stored, payload["uncompressed_bytes"])
    else:
        pieces: list[bytes] = []
        for chunk in payload["chunks"]:
            stored = source[chunk["artifact_name"]]
            logical = stored if chunk["encoding"] == "raw_binary" else _bounded_gzip_decompress(stored, chunk["uncompressed_bytes"])
            pieces.append(logical)
        raw = b"".join(pieces)
    return _unpack_values(raw, payload["dtype"])


def validate_volumetric_payload(value: Any, artifacts: Mapping[str, bytes] | None = None) -> VolumetricValidationResult:
    errors: set[str] = set()
    fields = {
        "schema_version", "payload_id", "encoding", "dtype", "endianness", "stored_component_count",
        "flatten_order", "grid_shape", "logical_shape", "value_count", "uncompressed_bytes", "compressed_bytes",
        "media_type", "artifact_name", "inline_values", "chunks", "compression", "logical_sha256",
        "storage_sha256", "storage_layout_hash", "security",
    }
    if not isinstance(value, dict) or set(value) != fields:
        return VolumetricValidationResult(False, ("VOLUME_PAYLOAD_SCHEMA_INVALID",))
    try:
        if value.get("schema_version") != VOLUMETRIC_PAYLOAD_SCHEMA_VERSION or value.get("encoding") not in PAYLOAD_ENCODINGS:
            errors.add("VOLUME_PAYLOAD_SCHEMA_INVALID")
        dtype = value.get("dtype")
        if dtype not in DTYPE_FORMATS or value.get("endianness") != "little" or value.get("flatten_order") != "ijkc_component_fastest":
            errors.add("VOLUME_PAYLOAD_LAYOUT_INVALID")
            dtype = "float64"
        shape = value.get("grid_shape")
        components = value.get("stored_component_count")
        if not isinstance(shape, list) or len(shape) != 3 or not _positive_int(components) or components not in {1, 2, 3}:
            errors.add("VOLUME_LOGICAL_SHAPE_INVALID")
            shape, components = [1, 1, 1], 1
        count = _safe_product([*shape, components], VOLUMETRIC_CAPS["max_stored_values"], "VOLUME_VALUE_CAP_EXCEEDED")
        expected_bytes = count * DTYPE_FORMATS[dtype][1]
        if value.get("logical_shape") != [*shape, components] or value.get("value_count") != count or value.get("uncompressed_bytes") != expected_bytes:
            errors.add("VOLUME_PAYLOAD_BYTE_MISMATCH")
        if not _SHA256.fullmatch(str(value.get("logical_sha256"))) or value.get("payload_id") != f"payload:{value.get('logical_sha256')}":
            errors.add("VOLUME_CONTENT_HASH_MISMATCH")
        if value.get("security") != VOLUMETRIC_SECURITY:
            errors.add("VOLUME_SECURITY_INVALID")
        encoding = value.get("encoding")
        source = artifacts or {}
        raw: bytes | None = None
        if encoding == "inline_json":
            inline = value.get("inline_values")
            if not isinstance(inline, list) or len(inline) != count or count > VOLUMETRIC_CAPS["max_inline_values"] or any(not _finite(item) for item in inline):
                errors.add("VOLUME_INLINE_PAYLOAD_INVALID")
            else:
                raw = _pack_values(inline, dtype)
                if value.get("storage_sha256") != volumetric_content_hash(
                    stable_volumetric_json(inline)
                ):
                    errors.add("VOLUME_PAYLOAD_HASH_MISMATCH")
            if value.get("artifact_name") is not None or value.get("chunks") != [] or value.get("media_type") != "application/json":
                errors.add("VOLUME_INLINE_PAYLOAD_INVALID")
            if value.get("compression") != {"codec": "none", "deterministic": True, "mtime": None, "filename": None}:
                errors.add("VOLUME_COMPRESSION_METADATA_INVALID")
        elif encoding in {"raw_binary", "gzip_binary"}:
            name = value.get("artifact_name")
            if not _safe_artifact_name(name) or value.get("inline_values") is not None or value.get("chunks") != []:
                errors.add("VOLUME_BINARY_PAYLOAD_INVALID")
            elif name not in source:
                errors.add("VOLUME_PAYLOAD_MISSING")
            else:
                stored = source[name]
                if len(stored) != value.get("compressed_bytes") or volumetric_content_hash(stored) != value.get("storage_sha256"):
                    errors.add("VOLUME_PAYLOAD_HASH_MISMATCH")
                else:
                    raw = stored if encoding == "raw_binary" else _bounded_gzip_decompress(stored, expected_bytes)
            expected_media = "application/gzip" if encoding == "gzip_binary" else f"application/vnd.mdi.volumetric+{dtype}"
            expected_compression = {"codec": "gzip", "deterministic": True, "mtime": 0, "filename": None} if encoding == "gzip_binary" else {"codec": "none", "deterministic": True, "mtime": None, "filename": None}
            if value.get("media_type") != expected_media or value.get("compression") != expected_compression:
                errors.add("VOLUME_COMPRESSION_METADATA_INVALID")
        elif encoding == "chunked_binary":
            raw = _validate_chunks(value, source, errors, shape, components, dtype)
            chunks = value.get("chunks")
            if isinstance(chunks, list):
                aggregate_storage_hash = volumetric_content_hash(
                    [
                        {
                            "artifact_name": chunk.get("artifact_name"),
                            "storage_sha256": chunk.get("storage_sha256"),
                        }
                        for chunk in chunks
                        if isinstance(chunk, dict)
                    ]
                )
                if value.get("storage_sha256") != aggregate_storage_hash:
                    errors.add("VOLUME_PAYLOAD_HASH_MISMATCH")
            if value.get("media_type") != "application/vnd.mdi.volumetric-chunks+json" or value.get("compression") != {"codec": "none", "deterministic": True, "mtime": None, "filename": None}:
                errors.add("VOLUME_COMPRESSION_METADATA_INVALID")
        if not _positive_int(value.get("compressed_bytes")) or value.get("compressed_bytes") > VOLUMETRIC_CAPS["max_compressed_bytes_per_field"]:
            errors.add("VOLUME_COMPRESSED_CAP_EXCEEDED")
        if raw is not None:
            if len(raw) != expected_bytes:
                errors.add("VOLUME_PAYLOAD_BYTE_MISMATCH")
            elif volumetric_content_hash(raw) != value.get("logical_sha256"):
                errors.add("VOLUME_PAYLOAD_HASH_MISMATCH")
            else:
                _unpack_values(raw, dtype)
        expected_layout = volumetric_content_hash({key: value[key] for key in value if key not in {"payload_id", "storage_layout_hash"}})
        if value.get("storage_layout_hash") != expected_layout:
            errors.add("VOLUME_STORAGE_LAYOUT_HASH_MISMATCH")
        _scan_inert(value)
    except VolumetricContractError as error:
        errors.add(error.code)
    except (TypeError, ValueError, OverflowError, RecursionError, KeyError):
        errors.add("VOLUME_PAYLOAD_SCHEMA_INVALID")
    return VolumetricValidationResult(not errors, tuple(sorted(errors)))


def _validate_chunks(
    payload: Mapping[str, Any], source: Mapping[str, bytes], errors: set[str], shape: list[int], components: int, dtype: str
) -> bytes | None:
    chunks = payload.get("chunks")
    if not isinstance(chunks, list) or not chunks or len(chunks) > VOLUMETRIC_CAPS["max_chunks_per_field"]:
        errors.add("VOLUME_CHUNK_CAP_EXCEEDED")
        return None
    expected_i = 0
    pieces: list[bytes] = []
    fields = {
        "chunk_id", "i_start", "i_end", "logical_shape", "artifact_name", "encoding", "media_type",
        "uncompressed_bytes", "compressed_bytes", "logical_sha256", "storage_sha256",
    }
    bytes_per_i = shape[1] * shape[2] * components * DTYPE_FORMATS[dtype][1]
    for index, chunk in enumerate(chunks):
        if not isinstance(chunk, dict) or set(chunk) != fields or chunk.get("chunk_id") != f"chunk:{index:04d}":
            errors.add("VOLUME_CHUNK_ORDER_INVALID")
            continue
        start, end = chunk.get("i_start"), chunk.get("i_end")
        if type(start) is not int or type(end) is not int or start != expected_i or not start < end <= shape[0]:
            errors.add("VOLUME_CHUNK_GAP_OR_OVERLAP")
            continue
        expected_i = end
        expected = (end - start) * bytes_per_i
        if chunk.get("logical_shape") != [end - start, shape[1], shape[2], components] or chunk.get("uncompressed_bytes") != expected:
            errors.add("VOLUME_CHUNK_SHAPE_INVALID")
        name = chunk.get("artifact_name")
        if not _safe_artifact_name(name) or name not in source:
            errors.add("VOLUME_PAYLOAD_MISSING")
            continue
        stored = source[name]
        if len(stored) != chunk.get("compressed_bytes") or volumetric_content_hash(stored) != chunk.get("storage_sha256"):
            errors.add("VOLUME_PAYLOAD_HASH_MISMATCH")
            continue
        if chunk.get("encoding") == "raw_binary":
            logical = stored
        elif chunk.get("encoding") == "gzip_binary":
            logical = _bounded_gzip_decompress(stored, expected)
        else:
            errors.add("VOLUME_ENCODING_UNSUPPORTED")
            continue
        if volumetric_content_hash(logical) != chunk.get("logical_sha256"):
            errors.add("VOLUME_PAYLOAD_HASH_MISMATCH")
        pieces.append(logical)
    if expected_i != shape[0]:
        errors.add("VOLUME_CHUNK_GAP_OR_OVERLAP")
    return b"".join(pieces) if not errors else None


def compute_volumetric_statistics(
    values: Sequence[float], *, stored_components: int, voxel_volume: float, value_kind: str
) -> dict[str, Any]:
    if not values or not _positive_int(stored_components) or len(values) % stored_components or not _finite(voxel_volume) or float(voxel_volume) <= 0:
        raise VolumetricContractError("VOLUME_STATISTICS_INPUT_INVALID", "Statistics input is invalid.")
    if any(not _finite(item) for item in values):
        raise VolumetricContractError("VOLUME_NON_FINITE_VALUE", "Statistics require finite values.")
    components: list[dict[str, float | int]] = []
    for component in range(stored_components):
        channel = [float(values[index]) for index in range(component, len(values), stored_components)]
        mean = math.fsum(channel) / len(channel)
        variance = math.fsum((item - mean) ** 2 for item in channel) / len(channel)
        components.append(
            {
                "count": len(channel),
                "minimum": min(channel),
                "maximum": max(channel),
                "mean": mean,
                "variance": variance,
                "standard_deviation": math.sqrt(variance),
                "rms": math.sqrt(math.fsum(item * item for item in channel) / len(channel)),
                "integral": math.fsum(channel) * float(voxel_volume),
                "absolute_integral": math.fsum(abs(item) for item in channel) * float(voxel_volume),
            }
        )
    result: dict[str, Any] = {
        "authority": "computed_from_payload",
        "accumulation_dtype": "float64",
        "finite_count": len(values),
        "stored_components": components,
        "histogram": None,
    }
    if value_kind == "complex" and stored_components == 2:
        magnitudes = [math.hypot(float(values[index]), float(values[index + 1])) for index in range(0, len(values), 2)]
        result["complex_magnitude"] = {
            "minimum": min(magnitudes),
            "maximum": max(magnitudes),
            "mean": math.fsum(magnitudes) / len(magnitudes),
            "norm_integral": math.fsum(item * item for item in magnitudes) * float(voxel_volume),
        }
    else:
        result["complex_magnitude"] = None
    return _canonical_value(result)


_QUANTITY_UNITS = {
    "generic_scalar": UNITS,
    "charge_density": frozenset({"elementary_charge/angstrom^3"}),
    "electron_density": frozenset({"electron/angstrom^3", "electron/bohr^3"}),
    "spin_density": frozenset({"electron/angstrom^3", "electron/bohr^3"}),
    "magnetization_density": frozenset({"bohr_magneton/angstrom^3"}),
    "electrostatic_potential": frozenset({"volt", "electronvolt", "hartree", "hartree/elementary_charge"}),
    "local_potential": frozenset({"volt", "electronvolt", "hartree", "hartree/elementary_charge"}),
    "electron_localization_function": frozenset({"dimensionless"}),
    "orbital_density": frozenset({"electron/angstrom^3", "angstrom^-3"}),
    "wavefunction": frozenset({"angstrom^-3", "custom_declared"}),
    "custom_declared": frozenset({"custom_declared"}),
}


def _field_identity_payload(field: Mapping[str, Any]) -> dict[str, Any]:
    return {key: field[key] for key in field if key not in {"field_id", "content_hash"}}


def build_volumetric_field(
    *,
    grid: Mapping[str, Any],
    payload: Mapping[str, Any],
    values: Sequence[float],
    field_name: str,
    quantity: str,
    unit: str,
    value_kind: str,
    field_rank: str,
    normalization_semantics: str,
    integral_semantics: str,
    component_labels: Sequence[str] | None = None,
    custom_quantity: Mapping[str, Any] | None = None,
    spin: Mapping[str, Any] | None = None,
    potential_reference: Mapping[str, Any] | None = None,
    provenance: Mapping[str, Any] | None = None,
    warnings: Sequence[str] = (),
) -> dict[str, Any]:
    grid_result = validate_volumetric_grid(dict(grid))
    if not grid_result.valid:
        raise VolumetricContractError(grid_result.errors[0], "Field grid is invalid.")
    if not _safe_text(field_name, VOLUMETRIC_CAPS["max_name_length"]):
        raise VolumetricContractError("VOLUME_FIELD_NAME_INVALID", "Field name is invalid.")
    components = stored_component_count(value_kind, field_rank)
    labels = list(component_labels or ({1: ["value"], 2: ["real", "imag"], 3: ["x", "y", "z"]}[components]))
    if components == 1 and labels != ["value"] or components == 2 and labels != ["real", "imag"] or components == 3 and labels != ["x", "y", "z"]:
        raise VolumetricContractError("VOLUME_COMPONENT_LABELS_INVALID", "Canonical component labels are required.")
    if payload.get("stored_component_count") != components or payload.get("grid_shape") != grid.get("shape"):
        raise VolumetricContractError("VOLUME_FIELD_PAYLOAD_MISMATCH", "Payload layout does not match the field/grid.")
    if quantity not in FIELD_QUANTITIES or unit not in UNITS or unit not in _QUANTITY_UNITS[quantity]:
        raise VolumetricContractError("VOLUME_QUANTITY_UNIT_MISMATCH", "Quantity and unit are incompatible.")
    if quantity in {"electron_density", "charge_density", "spin_density", "electrostatic_potential", "local_potential", "electron_localization_function", "orbital_density"} and (value_kind, field_rank) != ("real", "scalar"):
        raise VolumetricContractError("VOLUME_FIELD_KIND_UNSUPPORTED", "Quantity requires a real scalar field.")
    if quantity == "magnetization_density" and (value_kind, field_rank) not in {("real", "scalar"), ("real", "vector")}:
        raise VolumetricContractError("VOLUME_FIELD_KIND_UNSUPPORTED", "Magnetization requires a real scalar or vector field.")
    if quantity == "wavefunction" and (value_kind, field_rank) != ("complex", "scalar"):
        raise VolumetricContractError("VOLUME_FIELD_KIND_UNSUPPORTED", "Wavefunction requires a complex scalar field.")
    if normalization_semantics not in NORMALIZATION_SEMANTICS or integral_semantics not in INTEGRAL_SEMANTICS:
        raise VolumetricContractError("VOLUME_NORMALIZATION_INVALID", "Normalization and integral semantics are required.")
    custom = _normalize_custom_quantity(custom_quantity, quantity)
    spin_value = _normalize_spin(spin, quantity, field_rank)
    potential = _normalize_potential_reference(potential_reference, quantity, unit)
    warning_list = sorted(set(warnings))
    if len(warning_list) > VOLUMETRIC_CAPS["max_warnings"] or any(not _safe_text(item, 160) for item in warning_list):
        raise VolumetricContractError("VOLUME_WARNING_INVALID", "Warnings must be bounded inert text.")
    provenance_value = _normalize_provenance(provenance)
    field: dict[str, Any] = {
        "schema_version": VOLUMETRIC_FIELD_SCHEMA_VERSION,
        "field_id": "",
        "field_name": field_name,
        "grid_id": grid["grid_id"],
        "grid_content_hash": grid["content_hash"],
        "payload_id": payload["payload_id"],
        "payload_logical_sha256": payload["logical_sha256"],
        "quantity": quantity,
        "custom_quantity": custom,
        "value_kind": value_kind,
        "field_rank": field_rank,
        "logical_component_count": 1 if value_kind == "complex" else components,
        "stored_component_count": components,
        "component_labels": labels,
        "component_basis": "cartesian" if field_rank == "vector" else "not_applicable",
        "unit": {
            "source_unit": unit,
            "canonical_unit": unit,
            "conversion_factor": 1.0,
            "conversion_applied": False,
            "conversion_provenance": "identity",
        },
        "normalization_semantics": normalization_semantics,
        "integral_semantics": integral_semantics,
        "spin": spin_value,
        "potential_reference": potential,
        "complex_semantics": {
            "representation": "real_imag_interleaved",
            "phase_semantics": "source_defined",
            "derived_density_included": False,
        } if value_kind == "complex" else None,
        "statistics": compute_volumetric_statistics(
            values, stored_components=components, voxel_volume=float(grid["voxel_volume"]), value_kind=value_kind
        ),
        "provenance": provenance_value,
        "warnings": warning_list,
        "security": dict(VOLUMETRIC_SECURITY),
        "content_hash": "",
    }
    digest = volumetric_content_hash(_field_identity_payload(field))
    field["field_id"] = f"field:{digest}"
    field["content_hash"] = digest
    result = validate_volumetric_field(field, grid=grid, payload=payload)
    if not result.valid:
        raise VolumetricContractError(result.errors[0], "Generated volumetric field is invalid.")
    return field


def _normalize_custom_quantity(value: Mapping[str, Any] | None, quantity: str) -> dict[str, str] | None:
    if quantity != "custom_declared":
        if value is not None:
            raise VolumetricContractError("VOLUME_CUSTOM_QUANTITY_INVALID", "Custom metadata is only allowed for custom quantities.")
        return None
    if not isinstance(value, Mapping) or set(value) != {"identity", "display_name", "value_semantics"}:
        raise VolumetricContractError("VOLUME_CUSTOM_QUANTITY_INVALID", "Custom quantity metadata is required.")
    if not _safe_id(value.get("identity")) or not all(_safe_text(value.get(key), 128) for key in ("display_name", "value_semantics")):
        raise VolumetricContractError("VOLUME_CUSTOM_QUANTITY_INVALID", "Custom quantity metadata is invalid.")
    return {key: str(value[key]) for key in ("identity", "display_name", "value_semantics")}


def _normalize_spin(value: Mapping[str, Any] | None, quantity: str, field_rank: str) -> dict[str, Any] | None:
    if quantity not in {"spin_density", "magnetization_density"}:
        if value is not None:
            raise VolumetricContractError("VOLUME_SPIN_SEMANTICS_INVALID", "Spin metadata is not applicable.")
        return None
    fields = {"representation", "channel", "component_basis", "sign_convention", "source_convention"}
    if not isinstance(value, Mapping) or set(value) != fields:
        raise VolumetricContractError("VOLUME_SPIN_SEMANTICS_INVALID", "Spin metadata is required.")
    representation = value.get("representation")
    channel = value.get("channel")
    basis = value.get("component_basis")
    if representation not in SPIN_REPRESENTATIONS or channel not in SPIN_CHANNELS:
        raise VolumetricContractError("VOLUME_SPIN_SEMANTICS_INVALID", "Spin representation/channel is invalid.")
    if representation == "non_collinear" and (field_rank != "vector" or channel != "magnetization_vector" or basis != "cartesian"):
        raise VolumetricContractError("VOLUME_SPIN_SEMANTICS_INVALID", "Non-collinear magnetization requires a Cartesian vector.")
    if representation == "collinear" and field_rank == "vector":
        raise VolumetricContractError("VOLUME_SPIN_SEMANTICS_INVALID", "Collinear spin channels must be scalar.")
    if not _safe_text(value.get("sign_convention"), 128) or not _safe_text(value.get("source_convention"), 128):
        raise VolumetricContractError("VOLUME_SPIN_SEMANTICS_INVALID", "Spin conventions must be bounded inert text.")
    return {key: value[key] for key in fields}


def _normalize_potential_reference(value: Mapping[str, Any] | None, quantity: str, unit: str) -> dict[str, Any] | None:
    if quantity not in {"electrostatic_potential", "local_potential"}:
        if value is not None:
            raise VolumetricContractError("VOLUME_POTENTIAL_REFERENCE_INVALID", "Potential reference is not applicable.")
        return None
    fields = {"kind", "reference_value", "reference_unit", "shift_applied", "shift_amount", "source_metadata"}
    if not isinstance(value, Mapping) or set(value) != fields or value.get("kind") not in POTENTIAL_REFERENCES:
        raise VolumetricContractError("VOLUME_POTENTIAL_REFERENCE_INVALID", "Potential reference metadata is required.")
    if value.get("reference_unit") != unit or not _finite(value.get("reference_value")) or type(value.get("shift_applied")) is not bool or not _finite(value.get("shift_amount")) or not _safe_text(value.get("source_metadata"), 128):
        raise VolumetricContractError("VOLUME_POTENTIAL_REFERENCE_INVALID", "Potential reference metadata is invalid.")
    if not value["shift_applied"] and float(value["shift_amount"]) != 0:
        raise VolumetricContractError("VOLUME_POTENTIAL_REFERENCE_INVALID", "Unapplied shifts must be zero.")
    return {key: value[key] for key in fields}


def _normalize_provenance(value: Mapping[str, Any] | None) -> dict[str, Any]:
    default = {
        "source_kind": "synthetic_fixture",
        "source_format": "canonical_contract",
        "source_sha256": "0" * 64,
        "producer": "mdi_artifact_core",
        "producer_version": "phase10j",
        "transformations": [],
    }
    result = dict(default if value is None else value)
    fields = {"source_kind", "source_format", "source_sha256", "producer", "producer_version", "transformations"}
    if set(result) != fields or not _SHA256.fullmatch(str(result.get("source_sha256"))):
        raise VolumetricContractError("VOLUME_PROVENANCE_INVALID", "Provenance is invalid.")
    if not all(_safe_text(result.get(key), 96) for key in ("source_kind", "source_format", "producer", "producer_version")):
        raise VolumetricContractError("VOLUME_PROVENANCE_INVALID", "Provenance text is invalid.")
    transformations = result.get("transformations")
    if not isinstance(transformations, list) or len(transformations) > VOLUMETRIC_CAPS["max_provenance_entries"]:
        raise VolumetricContractError("VOLUME_PROVENANCE_INVALID", "Provenance transformations are invalid.")
    allowed = {"axis_permutation", "axis_reversal", "origin_shift", "endpoint_removal", "unit_conversion", "dtype_conversion", "endian_conversion", "component_remapping"}
    for item in transformations:
        if not isinstance(item, dict) or set(item) != {"kind", "detail"} or item.get("kind") not in allowed or not _safe_text(item.get("detail"), 160):
            raise VolumetricContractError("VOLUME_PROVENANCE_INVALID", "Provenance transformation is invalid.")
    return _canonical_value(result)


def validate_volumetric_field(
    value: Any, *, grid: Mapping[str, Any] | None = None, payload: Mapping[str, Any] | None = None
) -> VolumetricValidationResult:
    errors: set[str] = set()
    fields = {
        "schema_version", "field_id", "field_name", "grid_id", "grid_content_hash", "payload_id",
        "payload_logical_sha256", "quantity", "custom_quantity", "value_kind", "field_rank",
        "logical_component_count", "stored_component_count", "component_labels", "component_basis", "unit",
        "normalization_semantics", "integral_semantics", "spin", "potential_reference", "complex_semantics",
        "statistics", "provenance", "warnings", "security", "content_hash",
    }
    if not isinstance(value, dict) or set(value) != fields:
        return VolumetricValidationResult(False, ("VOLUME_FIELD_SCHEMA_INVALID",))
    try:
        if value.get("schema_version") != VOLUMETRIC_FIELD_SCHEMA_VERSION or not _safe_text(value.get("field_name"), VOLUMETRIC_CAPS["max_name_length"]):
            errors.add("VOLUME_FIELD_SCHEMA_INVALID")
        components = stored_component_count(str(value.get("value_kind")), str(value.get("field_rank")))
        expected_labels = {1: ["value"], 2: ["real", "imag"], 3: ["x", "y", "z"]}[components]
        if value.get("stored_component_count") != components or value.get("component_labels") != expected_labels or value.get("logical_component_count") != (1 if value.get("value_kind") == "complex" else components):
            errors.add("VOLUME_COMPONENT_LABELS_INVALID")
        if value.get("component_basis") != ("cartesian" if value.get("field_rank") == "vector" else "not_applicable"):
            errors.add("VOLUME_COMPONENT_BASIS_INVALID")
        quantity, unit_value = value.get("quantity"), value.get("unit")
        if quantity not in FIELD_QUANTITIES or not isinstance(unit_value, dict) or set(unit_value) != {"source_unit", "canonical_unit", "conversion_factor", "conversion_applied", "conversion_provenance"}:
            errors.add("VOLUME_QUANTITY_UNIT_MISMATCH")
        else:
            unit = unit_value.get("canonical_unit")
            if unit not in _QUANTITY_UNITS[quantity] or unit_value.get("source_unit") not in UNITS or not _finite(unit_value.get("conversion_factor")) or float(unit_value["conversion_factor"]) <= 0 or type(unit_value.get("conversion_applied")) is not bool or not _safe_text(unit_value.get("conversion_provenance"), 128):
                errors.add("VOLUME_QUANTITY_UNIT_MISMATCH")
        _normalize_custom_quantity(value.get("custom_quantity"), str(quantity))
        _normalize_spin(value.get("spin"), str(quantity), str(value.get("field_rank")))
        _normalize_potential_reference(value.get("potential_reference"), str(quantity), str(unit_value.get("canonical_unit") if isinstance(unit_value, dict) else ""))
        if value.get("normalization_semantics") not in NORMALIZATION_SEMANTICS or value.get("integral_semantics") not in INTEGRAL_SEMANTICS:
            errors.add("VOLUME_NORMALIZATION_INVALID")
        if value.get("value_kind") == "complex":
            if value.get("complex_semantics") != {"representation": "real_imag_interleaved", "phase_semantics": "source_defined", "derived_density_included": False}:
                errors.add("VOLUME_COMPLEX_SEMANTICS_INVALID")
        elif value.get("complex_semantics") is not None:
            errors.add("VOLUME_COMPLEX_SEMANTICS_INVALID")
        _validate_statistics(value.get("statistics"), components, value.get("value_kind"), errors)
        _normalize_provenance(value.get("provenance"))
        warnings = value.get("warnings")
        if not isinstance(warnings, list) or warnings != sorted(set(warnings)) or len(warnings) > VOLUMETRIC_CAPS["max_warnings"] or any(not _safe_text(item, 160) for item in warnings):
            errors.add("VOLUME_WARNING_INVALID")
        if value.get("security") != VOLUMETRIC_SECURITY:
            errors.add("VOLUME_SECURITY_INVALID")
        if grid is not None and (value.get("grid_id") != grid.get("grid_id") or value.get("grid_content_hash") != grid.get("content_hash")):
            errors.add("VOLUME_FIELD_GRID_MISMATCH")
        if payload is not None and (value.get("payload_id") != payload.get("payload_id") or value.get("payload_logical_sha256") != payload.get("logical_sha256") or value.get("stored_component_count") != payload.get("stored_component_count")):
            errors.add("VOLUME_FIELD_PAYLOAD_MISMATCH")
        digest = volumetric_content_hash(_field_identity_payload(value))
        if value.get("content_hash") != digest or value.get("field_id") != f"field:{digest}":
            errors.add("VOLUME_CONTENT_HASH_MISMATCH")
        _scan_inert(value)
    except VolumetricContractError as error:
        errors.add(error.code)
    except (TypeError, ValueError, OverflowError, RecursionError):
        errors.add("VOLUME_FIELD_SCHEMA_INVALID")
    return VolumetricValidationResult(not errors, tuple(sorted(errors)))


def _validate_statistics(value: Any, components: int, value_kind: Any, errors: set[str]) -> None:
    fields = {"authority", "accumulation_dtype", "finite_count", "stored_components", "histogram", "complex_magnitude"}
    component_fields = {"count", "minimum", "maximum", "mean", "variance", "standard_deviation", "rms", "integral", "absolute_integral"}
    if not isinstance(value, dict) or set(value) != fields or value.get("authority") != "computed_from_payload" or value.get("accumulation_dtype") != "float64" or not _positive_int(value.get("finite_count")) or value.get("histogram") is not None:
        errors.add("VOLUME_STATISTICS_INVALID")
        return
    rows = value.get("stored_components")
    if not isinstance(rows, list) or len(rows) != components:
        errors.add("VOLUME_STATISTICS_INVALID")
        return
    for row in rows:
        if not isinstance(row, dict) or set(row) != component_fields or not _positive_int(row.get("count")) or any(not _finite(row.get(key)) for key in component_fields - {"count"}):
            errors.add("VOLUME_STATISTICS_INVALID")
    magnitude = value.get("complex_magnitude")
    if value_kind == "complex":
        if not isinstance(magnitude, dict) or set(magnitude) != {"minimum", "maximum", "mean", "norm_integral"} or any(not _finite(item) for item in magnitude.values()):
            errors.add("VOLUME_STATISTICS_INVALID")
    elif magnitude is not None:
        errors.add("VOLUME_STATISTICS_INVALID")


def _dataset_identity_payload(dataset: Mapping[str, Any]) -> dict[str, Any]:
    return {key: dataset[key] for key in dataset if key not in {"dataset_id", "content_hash"}}


def build_volumetric_dataset(
    *,
    grid: Mapping[str, Any],
    payloads: Sequence[Mapping[str, Any]],
    fields: Sequence[Mapping[str, Any]],
    relationships: Sequence[Mapping[str, Any]] = (),
    provenance: Mapping[str, Any] | None = None,
    warnings: Sequence[str] = (),
    artifacts: Mapping[str, bytes] | None = None,
) -> dict[str, Any]:
    ordered_payloads = sorted((dict(item) for item in payloads), key=lambda item: item["payload_id"])
    ordered_fields = sorted((dict(item) for item in fields), key=lambda item: item["field_id"])
    if not ordered_fields or len(ordered_fields) > VOLUMETRIC_CAPS["max_fields_per_dataset"] or len(ordered_payloads) != len(ordered_fields):
        raise VolumetricContractError("VOLUME_DATASET_CAP_EXCEEDED", "Dataset fields are invalid or exceed caps.")
    relation_values = _normalize_relationships(relationships, ordered_fields)
    warning_values = sorted(set(warnings))
    dataset: dict[str, Any] = {
        "schema_version": VOLUMETRIC_DATASET_SCHEMA_VERSION,
        "dataset_id": "",
        "grid": dict(grid),
        "payloads": ordered_payloads,
        "fields": ordered_fields,
        "relationships": relation_values,
        "provenance": _normalize_provenance(provenance),
        "warnings": warning_values,
        "caps": dict(VOLUMETRIC_CAPS),
        "security": dict(VOLUMETRIC_SECURITY),
        "content_hash": "",
    }
    digest = volumetric_content_hash(_dataset_identity_payload(dataset))
    dataset["dataset_id"] = f"volume-dataset:{digest}"
    dataset["content_hash"] = digest
    result = validate_volumetric_dataset(dataset, artifacts)
    if not result.valid:
        raise VolumetricContractError(result.errors[0], "Generated volumetric dataset is invalid.")
    return dataset


def _normalize_relationships(values: Sequence[Mapping[str, Any]], fields: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    field_ids = {item["field_id"] for item in fields}
    result: list[dict[str, Any]] = []
    for value in values:
        if not isinstance(value, Mapping) or set(value) != {"relationship_id", "kind", "input_field_ids", "output_field_id", "status", "residual"}:
            raise VolumetricContractError("VOLUME_RELATIONSHIP_INVALID", "Field relationship is invalid.")
        if not _safe_id(value.get("relationship_id")) or value.get("kind") not in {"total_equals_up_plus_down", "spin_difference_equals_up_minus_down", "vector_magnitude", "complex_norm_density"} or value.get("status") not in {"declared", "validated", "unverified"}:
            raise VolumetricContractError("VOLUME_RELATIONSHIP_INVALID", "Field relationship is invalid.")
        inputs = value.get("input_field_ids")
        if not isinstance(inputs, list) or not inputs or any(item not in field_ids for item in inputs) or value.get("output_field_id") not in field_ids or not _finite(value.get("residual")):
            raise VolumetricContractError("VOLUME_RELATIONSHIP_INVALID", "Field relationship references are invalid.")
        result.append(dict(value))
    return sorted(result, key=lambda item: item["relationship_id"])


def validate_volumetric_dataset(value: Any, artifacts: Mapping[str, bytes] | None = None) -> VolumetricValidationResult:
    errors: set[str] = set()
    fields = {"schema_version", "dataset_id", "grid", "payloads", "fields", "relationships", "provenance", "warnings", "caps", "security", "content_hash"}
    if not isinstance(value, dict) or set(value) != fields:
        return VolumetricValidationResult(False, ("VOLUME_DATASET_SCHEMA_INVALID",))
    try:
        if value.get("schema_version") != VOLUMETRIC_DATASET_SCHEMA_VERSION:
            errors.add("VOLUME_DATASET_SCHEMA_INVALID")
        grid = value.get("grid")
        grid_result = validate_volumetric_grid(grid)
        errors.update(grid_result.errors)
        payloads = value.get("payloads")
        field_values = value.get("fields")
        if not isinstance(payloads, list) or not isinstance(field_values, list) or not field_values or len(field_values) > VOLUMETRIC_CAPS["max_fields_per_dataset"] or len(payloads) != len(field_values):
            errors.add("VOLUME_DATASET_CAP_EXCEEDED")
            payloads, field_values = [], []
        if payloads != sorted(payloads, key=lambda item: item.get("payload_id", "")) or field_values != sorted(field_values, key=lambda item: item.get("field_id", "")):
            errors.add("VOLUME_CANONICAL_ORDER_INVALID")
        payload_by_id: dict[str, Mapping[str, Any]] = {}
        total_bytes = 0
        for payload in payloads:
            result = validate_volumetric_payload(payload, artifacts)
            errors.update(result.errors)
            if isinstance(payload, dict):
                payload_by_id[str(payload.get("payload_id"))] = payload
                total_bytes += int(payload.get("uncompressed_bytes", 0)) if _positive_int(payload.get("uncompressed_bytes")) else 0
        if total_bytes > VOLUMETRIC_CAPS["max_dataset_bytes"]:
            errors.add("VOLUME_DATASET_CAP_EXCEEDED")
        for field in field_values:
            payload = payload_by_id.get(str(field.get("payload_id"))) if isinstance(field, dict) else None
            result = validate_volumetric_field(field, grid=grid if isinstance(grid, dict) else None, payload=payload)
            errors.update(result.errors)
        _normalize_relationships(value.get("relationships", []), field_values)
        _normalize_provenance(value.get("provenance"))
        if value.get("warnings") != sorted(set(value.get("warnings", []))) or value.get("caps") != VOLUMETRIC_CAPS or value.get("security") != VOLUMETRIC_SECURITY:
            errors.add("VOLUME_DATASET_METADATA_INVALID")
        digest = volumetric_content_hash(_dataset_identity_payload(value))
        if value.get("content_hash") != digest or value.get("dataset_id") != f"volume-dataset:{digest}":
            errors.add("VOLUME_CONTENT_HASH_MISMATCH")
        _scan_inert(value)
    except VolumetricContractError as error:
        errors.add(error.code)
    except (TypeError, ValueError, OverflowError, RecursionError):
        errors.add("VOLUME_DATASET_SCHEMA_INVALID")
    return VolumetricValidationResult(not errors, tuple(sorted(errors)))


def build_volumetric_manifest(dataset: Mapping[str, Any], artifacts: Mapping[str, bytes]) -> dict[str, Any]:
    dataset_result = validate_volumetric_dataset(dict(dataset), artifacts)
    if not dataset_result.valid:
        raise VolumetricContractError(dataset_result.errors[0], "Dataset must validate before manifest generation.")
    entries = [
        {
            "name": name,
            "kind": "numeric_payload",
            "media_type": _artifact_media_type(name, dataset),
            "bytes": len(content),
            "sha256": volumetric_content_hash(content),
            "schema_version": VOLUMETRIC_PAYLOAD_SCHEMA_VERSION,
        }
        for name, content in sorted(artifacts.items())
    ]
    for name, kind, schema, payload in (
        ("volumetric_grid.json", "grid", VOLUMETRIC_GRID_SCHEMA_VERSION, dataset["grid"]),
        ("volumetric_dataset.json", "dataset", VOLUMETRIC_DATASET_SCHEMA_VERSION, dataset),
    ):
        content = stable_volumetric_json(payload).encode("utf-8")
        entries.append({"name": name, "kind": kind, "media_type": "application/json", "bytes": len(content), "sha256": volumetric_content_hash(content), "schema_version": schema})
    entries.sort(key=lambda item: item["name"])
    manifest: dict[str, Any] = {
        "schema_version": VOLUMETRIC_MANIFEST_SCHEMA_VERSION,
        "manifest_id": "",
        "dataset_id": dataset["dataset_id"],
        "dataset_content_hash": dataset["content_hash"],
        "schema_versions": {
            "grid": VOLUMETRIC_GRID_SCHEMA_VERSION,
            "payload": VOLUMETRIC_PAYLOAD_SCHEMA_VERSION,
            "field": VOLUMETRIC_FIELD_SCHEMA_VERSION,
            "dataset": VOLUMETRIC_DATASET_SCHEMA_VERSION,
            "manifest": VOLUMETRIC_MANIFEST_SCHEMA_VERSION,
        },
        "artifacts": entries,
        "capabilities": {
            "metadata_preview": True,
            "parser_included": False,
            "renderer_included": False,
            "isosurface_included": False,
            "slice_included": False,
        },
        "external_resources": [],
        "executable_assets": [],
        "preview_mode": "metadata_json_only",
        "caps": dict(VOLUMETRIC_CAPS),
        "security": dict(VOLUMETRIC_SECURITY),
        "content_hash": "",
    }
    identity = {key: manifest[key] for key in manifest if key not in {"manifest_id", "content_hash"}}
    digest = volumetric_content_hash(identity)
    manifest["manifest_id"] = f"volume-manifest:{digest}"
    manifest["content_hash"] = digest
    result = validate_volumetric_manifest(manifest, dataset=dataset, artifacts=artifacts)
    if not result.valid:
        raise VolumetricContractError(result.errors[0], "Generated volumetric manifest is invalid.")
    return manifest


def _artifact_media_type(name: str, dataset: Mapping[str, Any]) -> str:
    for payload in dataset["payloads"]:
        if payload.get("artifact_name") == name:
            return str(payload["media_type"])
        for chunk in payload.get("chunks", []):
            if chunk.get("artifact_name") == name:
                return str(chunk["media_type"])
    raise VolumetricContractError("VOLUME_MANIFEST_REFERENCE_INVALID", "Manifest artifact is not referenced by a payload.")


def validate_volumetric_manifest(
    value: Any, *, dataset: Mapping[str, Any] | None = None, artifacts: Mapping[str, bytes] | None = None
) -> VolumetricValidationResult:
    errors: set[str] = set()
    fields = {"schema_version", "manifest_id", "dataset_id", "dataset_content_hash", "schema_versions", "artifacts", "capabilities", "external_resources", "executable_assets", "preview_mode", "caps", "security", "content_hash"}
    if not isinstance(value, dict) or set(value) != fields:
        return VolumetricValidationResult(False, ("VOLUME_MANIFEST_SCHEMA_INVALID",))
    try:
        if value.get("schema_version") != VOLUMETRIC_MANIFEST_SCHEMA_VERSION or value.get("schema_versions") != {"grid": VOLUMETRIC_GRID_SCHEMA_VERSION, "payload": VOLUMETRIC_PAYLOAD_SCHEMA_VERSION, "field": VOLUMETRIC_FIELD_SCHEMA_VERSION, "dataset": VOLUMETRIC_DATASET_SCHEMA_VERSION, "manifest": VOLUMETRIC_MANIFEST_SCHEMA_VERSION}:
            errors.add("VOLUME_MANIFEST_SCHEMA_INVALID")
        if value.get("capabilities") != {"metadata_preview": True, "parser_included": False, "renderer_included": False, "isosurface_included": False, "slice_included": False} or value.get("external_resources") != [] or value.get("executable_assets") != [] or value.get("preview_mode") != "metadata_json_only" or value.get("caps") != VOLUMETRIC_CAPS or value.get("security") != VOLUMETRIC_SECURITY:
            errors.add("VOLUME_MANIFEST_SECURITY_INVALID")
        entries = value.get("artifacts")
        entry_fields = {"name", "kind", "media_type", "bytes", "sha256", "schema_version"}
        if not isinstance(entries, list) or entries != sorted(entries, key=lambda item: item.get("name", "")):
            errors.add("VOLUME_MANIFEST_REFERENCE_INVALID")
            entries = []
        elif len({entry.get("name") for entry in entries if isinstance(entry, dict)}) != len(entries):
            errors.add("VOLUME_MANIFEST_REFERENCE_INVALID")
        for entry in entries:
            if not isinstance(entry, dict) or set(entry) != entry_fields or not _safe_artifact_name(entry.get("name")) or not _positive_int(entry.get("bytes")) or not _SHA256.fullmatch(str(entry.get("sha256"))):
                errors.add("VOLUME_MANIFEST_REFERENCE_INVALID")
                continue
            if entry.get("kind") == "numeric_payload" and artifacts is not None:
                content = artifacts.get(entry["name"])
                if content is None or len(content) != entry["bytes"] or volumetric_content_hash(content) != entry["sha256"]:
                    errors.add("VOLUME_MANIFEST_REFERENCE_INVALID")
        if dataset is not None and (value.get("dataset_id") != dataset.get("dataset_id") or value.get("dataset_content_hash") != dataset.get("content_hash")):
            errors.add("VOLUME_MANIFEST_DATASET_MISMATCH")
        digest = volumetric_content_hash({key: value[key] for key in value if key not in {"manifest_id", "content_hash"}})
        if value.get("content_hash") != digest or value.get("manifest_id") != f"volume-manifest:{digest}":
            errors.add("VOLUME_CONTENT_HASH_MISMATCH")
        _scan_inert(value)
    except VolumetricContractError as error:
        errors.add(error.code)
    except (TypeError, ValueError, OverflowError, RecursionError):
        errors.add("VOLUME_MANIFEST_SCHEMA_INVALID")
    return VolumetricValidationResult(not errors, tuple(sorted(errors)))


def is_isosurface_compatible(
    field: Mapping[str, Any], grid: Mapping[str, Any], payload: Mapping[str, Any]
) -> tuple[bool, tuple[str, ...]]:
    reasons: list[str] = []
    if not validate_volumetric_grid(dict(grid)).valid:
        reasons.append("grid_invalid")
    if (field.get("value_kind"), field.get("field_rank"), field.get("stored_component_count")) != ("real", "scalar", 1):
        reasons.append("real_scalar_required")
    if field.get("grid_id") != grid.get("grid_id") or field.get("payload_id") != payload.get("payload_id"):
        reasons.append("binding_mismatch")
    statistics = field.get("statistics")
    if not isinstance(statistics, dict) or not statistics.get("stored_components"):
        reasons.append("statistics_missing")
    if payload.get("uncompressed_bytes", VOLUMETRIC_CAPS["max_uncompressed_bytes_per_field"] + 1) > VOLUMETRIC_CAPS["max_uncompressed_bytes_per_field"]:
        reasons.append("payload_over_cap")
    return not reasons, tuple(reasons)


def volumetric_schema_snapshots() -> dict[str, Any]:
    return {
        "schemas": {
            "grid": VOLUMETRIC_GRID_SCHEMA_VERSION,
            "payload": VOLUMETRIC_PAYLOAD_SCHEMA_VERSION,
            "field": VOLUMETRIC_FIELD_SCHEMA_VERSION,
            "dataset": VOLUMETRIC_DATASET_SCHEMA_VERSION,
            "manifest": VOLUMETRIC_MANIFEST_SCHEMA_VERSION,
        },
        "flatten_order": "ijkc_component_fastest",
        "coordinate_formula": "r_cart=origin+(i+sample_shift)*step_0+(j+sample_shift)*step_1+(k+sample_shift)*step_2",
        "row_vector_lattice_formula": "r_cart=r_frac*A",
        "periodic_endpoint_policy": "excluded",
        "dtypes": sorted(DTYPE_FORMATS),
        "encodings": sorted(PAYLOAD_ENCODINGS),
        "caps": dict(VOLUMETRIC_CAPS),
        "security": dict(VOLUMETRIC_SECURITY),
    }
