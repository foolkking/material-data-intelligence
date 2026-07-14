from __future__ import annotations

import hashlib
import json
import math
import re
from dataclasses import dataclass
from typing import Any, Iterable, Sequence

from .phonon_contract import (
    RECIPROCAL_CONVENTION,
    reciprocal_lattice_physics_2pi,
    validate_phonon_band,
)


RECIPROCAL_LATTICE_SCHEMA_VERSION = "phase10i.reciprocal_lattice.v1"
BRILLOUIN_ZONE_SCHEMA_VERSION = "phase10i.brillouin_zone.v1"
KPATH_SCHEMA_VERSION = "phase10i.kpath.v1"
BRILLOUIN_ZONE_MANIFEST_SCHEMA_VERSION = "phase10i.brillouin_zone_manifest.v1"
BRILLOUIN_TOLERANCE_SCHEMA_VERSION = "phase10i.tolerance_policy.v1"

RECIPROCAL_UNITS = "angstrom^-1"
REAL_UNITS = "angstrom"
RECIPROCAL_BASIS = "standardized_primitive_reciprocal"
SUPPORTED_PROVIDER_NAMES = frozenset(
    {
        "internal_fixture_reference",
        "pymatgen_highsymmkpath",
        "seekpath_hpkot",
        "spglib_standardization",
        "explicit_validated_input",
    }
)
SUPPORTED_PATH_CONVENTIONS = frozenset(
    {"internal_fixture_reference", "setyawan_curtarolo", "hpkot", "explicit_validated"}
)
BASIS_ROLES = frozenset(
    {"source_cell", "primitive_cell", "conventional_cell", "standardized_primitive_cell"}
)

BRILLOUIN_CAPS: dict[str, int] = {
    "max_vertices": 256,
    "max_edges": 512,
    "max_faces": 256,
    "max_vertices_per_face": 64,
    "max_high_symmetry_points": 128,
    "max_aliases_per_point": 16,
    "max_path_variants": 8,
    "max_path_segments": 256,
    "max_discontinuities": 64,
    "max_label_length": 64,
    "max_warnings": 32,
    "max_provider_metadata_bytes": 16_384,
    "max_json_bytes": 8_000_000,
    "max_transformations": 8,
    "max_generator_search_radius": 4,
    "max_candidate_planes": 728,
    "max_numeric_magnitude": 1_000_000_000_000,
    "max_scan_depth": 32,
    "max_scan_nodes": 100_000,
}

BRILLOUIN_TOLERANCES: dict[str, float | str] = {
    "schema_version": BRILLOUIN_TOLERANCE_SCHEMA_VERSION,
    "real_lattice_determinant_relative": 1e-12,
    "real_lattice_condition_max": 1e8,
    "reciprocal_duality_absolute": 1e-9,
    "transformation_roundtrip_absolute": 1e-9,
    "symmetry_symprec_angstrom": 1e-5,
    "symmetry_angle_tolerance_degrees": 5.0,
    "vertex_merge_angstrom_inverse": 1e-8,
    "plane_absolute": 1e-8,
    "coplanarity_angstrom_inverse": 1e-8,
    "edge_length_angstrom_inverse": 1e-10,
    "volume_relative": 1e-8,
    "central_symmetry_angstrom_inverse": 1e-8,
    "label_coordinate_absolute": 1e-8,
    "path_endpoint_absolute": 1e-8,
    "rationalization_absolute": 1e-10,
}

BRILLOUIN_SECURITY: dict[str, Any] = {
    "contains_javascript": False,
    "contains_html": False,
    "contains_css": False,
    "external_urls": [],
    "external_urls_allowed": False,
    "renderer_included": False,
    "executable_assets": [],
    "remote_assets": [],
    "shader_sources": [],
    "executable_content_allowed": False,
}

_FORBIDDEN_KEYS = {
    "__proto__", "callback", "callbacks", "code", "constructor", "css", "eval", "expression",
    "function", "glsl", "html", "iframe", "module", "onload", "prototype", "script", "shader",
    "src", "texture", "url", "urls", "wasm", "worker",
}
_FORBIDDEN_MARKERS = (
    "http://", "https://", "javascript:", "file://", "data:text/html", "<script", "<iframe",
    "eval(", "new function",
)
_PRIVATE_PATH = (re.compile(r"^[a-zA-Z]:[\\/]"), re.compile(r"^/(?:home|users|root|etc)/"))
_LABEL_KEY = re.compile(r"^[A-Z][A-Z0-9_]{0,31}$")
_SAFE_TEXT = re.compile(r"^[\w .,:+()'\-/ΓΔΣΛΩ_|]+$", re.UNICODE)
_SHA256 = re.compile(r"^[0-9a-f]{64}$")


@dataclass(frozen=True)
class BrillouinValidationResult:
    valid: bool
    errors: tuple[str, ...]
    warnings: tuple[str, ...]
    counts: dict[str, int]
    caps: dict[str, int]

    def as_dict(self) -> dict[str, Any]:
        return {
            "valid": self.valid,
            "errors": list(self.errors),
            "warnings": list(self.warnings),
            "counts": dict(self.counts),
            "caps": dict(self.caps),
        }


@dataclass(frozen=True)
class ReciprocalCompatibilityResult:
    compatible: bool
    errors: tuple[str, ...]
    warnings: tuple[str, ...]
    checks: tuple[dict[str, Any], ...]

    def as_dict(self) -> dict[str, Any]:
        return {
            "compatible": self.compatible,
            "errors": list(self.errors),
            "warnings": list(self.warnings),
            "checks": [dict(item) for item in self.checks],
        }


class BrillouinContractError(ValueError):
    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code


def stable_brillouin_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=True, allow_nan=False, sort_keys=True, separators=(",", ":"))


def brillouin_content_hash(value: Any) -> str:
    payload = dict(value) if isinstance(value, dict) else value
    if isinstance(payload, dict):
        payload.pop("content_hash", None)
    return hashlib.sha256(stable_brillouin_json(payload).encode("utf-8")).hexdigest()


def lattice_content_hash(matrix: Sequence[Sequence[float]]) -> str:
    return hashlib.sha256(stable_brillouin_json(_canonical_matrix(matrix)).encode("utf-8")).hexdigest()


def reciprocal_fractional_to_cartesian(
    coordinates: Sequence[float], reciprocal_matrix: Sequence[Sequence[float]]
) -> list[float]:
    vector = _validated_vector(coordinates, "BZ_RECIPROCAL_COORDINATE_INVALID")
    matrix = _validated_matrix(reciprocal_matrix, "BZ_RECIPROCAL_LATTICE_INVALID")
    return _canonical_vector(_vector_matrix(vector, matrix))


def reciprocal_cartesian_to_fractional(
    coordinates: Sequence[float], reciprocal_matrix: Sequence[Sequence[float]]
) -> list[float]:
    vector = _validated_vector(coordinates, "BZ_RECIPROCAL_COORDINATE_INVALID")
    matrix = _validated_matrix(reciprocal_matrix, "BZ_RECIPROCAL_LATTICE_INVALID")
    inverse = _inverse_checked(matrix, "BZ_RECIPROCAL_LATTICE_SINGULAR")
    return _canonical_vector(_vector_matrix(vector, inverse))


def build_basis_transformation(
    matrix: Sequence[Sequence[float]], *, old_basis: str, new_basis: str,
    origin_shift: Sequence[float] = (0.0, 0.0, 0.0),
    cartesian_rotation: Sequence[Sequence[float]] | None = None,
) -> dict[str, Any]:
    if old_basis not in BASIS_ROLES or new_basis not in BASIS_ROLES or old_basis == new_basis:
        raise BrillouinContractError("BZ_TRANSFORMATION_INVALID", "Basis roles are invalid.")
    transform = _validated_matrix(matrix, "BZ_TRANSFORMATION_INVALID")
    determinant = _determinant(transform)
    _inverse_checked(transform, "BZ_TRANSFORMATION_INVALID")
    rotation = _identity_matrix() if cartesian_rotation is None else _validated_matrix(
        cartesian_rotation, "BZ_TRANSFORMATION_INVALID"
    )
    shift = _validated_vector(origin_shift, "BZ_TRANSFORMATION_INVALID")
    payload = {
        "transformation_id": f"{old_basis}_to_{new_basis}",
        "old_basis": old_basis,
        "new_basis": new_basis,
        "matrix_representation": "finite_decimal",
        "matrix": _canonical_matrix(transform),
        "determinant": _canonical_number(determinant),
        "real_lattice_formula": "A_new=M*A_old",
        "real_fractional_formula": "r_new=r_old*M^-1",
        "reciprocal_basis_formula": "B_new=M^-T*B_old",
        "reciprocal_fractional_formula": "k_new=k_old*M^T",
        "origin_shift": _canonical_vector(shift),
        "cartesian_rotation": _canonical_matrix(rotation),
    }
    return payload


def build_reciprocal_lattice_contract(
    *,
    source_structure_id: str,
    source_structure_sha256: str,
    source_real_lattice: Sequence[Sequence[float]],
    primitive_real_lattice: Sequence[Sequence[float]],
    transformations: Sequence[dict[str, Any]] = (),
    conventional_real_lattice: Sequence[Sequence[float]] | None = None,
    provider: dict[str, Any] | None = None,
    ordered: bool = True,
    partial_occupancy: bool = False,
    magnetic: bool = False,
) -> dict[str, Any]:
    source = _validated_real_lattice(source_real_lattice)
    primitive = _validated_real_lattice(primitive_real_lattice)
    conventional = None if conventional_real_lattice is None else _validated_real_lattice(conventional_real_lattice)
    reciprocal = _canonical_matrix(reciprocal_lattice_physics_2pi(primitive))
    dual = _canonical_matrix(_matrix_multiply(primitive, _transpose(reciprocal)))
    real_volume = abs(_determinant(primitive))
    reciprocal_volume = abs(_determinant(reciprocal))
    provider_value = _normalize_provider(
        provider
        or {
            "name": "internal_fixture_reference",
            "version": "1",
            "convention": "internal_fixture_reference",
            "symprec_angstrom": BRILLOUIN_TOLERANCES["symmetry_symprec_angstrom"],
            "angle_tolerance_degrees": BRILLOUIN_TOLERANCES["symmetry_angle_tolerance_degrees"],
            "time_reversal_used": True,
            "standardization_status": "validated_fixture",
            "warnings": [],
        },
        source_structure_sha256,
    )
    normalized_transformations = [dict(item) for item in transformations]
    binding = {
        "source_structure_id": _safe_text(source_structure_id, "BZ_STRUCTURE_IDENTITY_INVALID"),
        "source_structure_sha256": _validated_sha(source_structure_sha256, "BZ_STRUCTURE_IDENTITY_INVALID"),
        "source_lattice_sha256": lattice_content_hash(source),
        "primitive_lattice_sha256": lattice_content_hash(primitive),
        "conventional_lattice_sha256": None if conventional is None else lattice_content_hash(conventional),
        "source_basis_role": "source_cell",
        "primitive_basis_role": "standardized_primitive_cell",
        "source_real_lattice": _canonical_matrix(source),
        "primitive_real_lattice": _canonical_matrix(primitive),
        "conventional_real_lattice": None if conventional is None else _canonical_matrix(conventional),
        "periodic_dimension": 3,
        "ordered": bool(ordered),
        "partial_occupancy": bool(partial_occupancy),
        "magnetic": bool(magnetic),
    }
    payload: dict[str, Any] = {
        "schema_version": RECIPROCAL_LATTICE_SCHEMA_VERSION,
        "content_hash": "",
        "convention": RECIPROCAL_CONVENTION,
        "units": RECIPROCAL_UNITS,
        "basis_orientation": "row_vectors",
        "basis_role": "standardized_primitive_reciprocal",
        "real_lattice_binding": binding,
        "matrix": reciprocal,
        "dual_product": dual,
        "determinant": _canonical_number(_determinant(reciprocal)),
        "cell_volume": _canonical_number(reciprocal_volume),
        "real_cell_volume": _canonical_number(real_volume),
        "transformations": normalized_transformations,
        "tolerances": dict(BRILLOUIN_TOLERANCES),
        "provider": provider_value,
        "provenance": {
            "producer": "phase10i.contract",
            "producer_version": "1.0.0",
            "deterministic": True,
            "geometry_generated": False,
        },
        "security": _security_copy(),
    }
    payload["content_hash"] = brillouin_content_hash(payload)
    result = validate_reciprocal_lattice(payload)
    if not result.valid:
        raise BrillouinContractError(result.errors[0], "The reciprocal lattice contract is invalid.")
    return payload


def canonicalize_brillouin_zone(
    reciprocal_lattice: dict[str, Any], raw_faces: Sequence[dict[str, Any]], *, provider_method: str
) -> dict[str, Any]:
    reciprocal_result = validate_reciprocal_lattice(reciprocal_lattice)
    if not reciprocal_result.valid:
        raise BrillouinContractError(reciprocal_result.errors[0], "The reciprocal lattice binding is invalid.")
    if not _valid_safe_text(provider_method, 64):
        raise BrillouinContractError("BZ_PROVIDER_METADATA_INVALID", "The geometry method is invalid.")
    if not isinstance(raw_faces, Sequence) or not raw_faces:
        raise BrillouinContractError("BZ_POLYHEDRON_INVALID", "At least four faces are required.")
    reciprocal = reciprocal_lattice["matrix"]
    merge_tolerance = float(BRILLOUIN_TOLERANCES["vertex_merge_angstrom_inverse"])
    unique_points: list[list[float]] = []
    normalized_faces: list[tuple[list[int], tuple[int, int, int], list[float]]] = []
    for raw_face in raw_faces:
        if not isinstance(raw_face, dict) or set(raw_face) != {"generator_hkl", "vertices"}:
            raise BrillouinContractError("BZ_FACE_INVALID", "Face input is invalid.")
        hkl_value = raw_face["generator_hkl"]
        if not _integer_triplet(hkl_value, BRILLOUIN_CAPS["max_generator_search_radius"]) or hkl_value == [0, 0, 0]:
            raise BrillouinContractError("BZ_FACE_GENERATOR_INVALID", "The face generator is invalid.")
        vertices_value = raw_face["vertices"]
        if not isinstance(vertices_value, list) or not 3 <= len(vertices_value) <= BRILLOUIN_CAPS["max_vertices_per_face"]:
            raise BrillouinContractError("BZ_FACE_INVALID", "The face vertex count is invalid.")
        face_points = [_validated_vector(point, "BZ_VERTEX_INVALID") for point in vertices_value]
        if len(face_points) > 3 and _near_vector(face_points[0], face_points[-1], merge_tolerance):
            face_points.pop()
        indices: list[int] = []
        for point in face_points:
            index = next((i for i, existing in enumerate(unique_points) if _near_vector(point, existing, merge_tolerance)), None)
            if index is None:
                unique_points.append(_canonical_vector(point))
                index = len(unique_points) - 1
            if index in indices:
                raise BrillouinContractError("BZ_DUPLICATE_VERTEX", "A face contains a duplicate vertex.")
            indices.append(index)
        generator = reciprocal_fractional_to_cartesian(hkl_value, reciprocal)
        normal = _normalize(generator, "BZ_FACE_GENERATOR_INVALID")
        if _dot(_newell([unique_points[index] for index in indices]), normal) < 0:
            indices.reverse()
        normalized_faces.append((indices, tuple(int(value) for value in hkl_value), generator))
    if len(unique_points) > BRILLOUIN_CAPS["max_vertices"]:
        raise BrillouinContractError("BZ_CAP_EXCEEDED", "The vertex cap is exceeded.")
    order = sorted(range(len(unique_points)), key=lambda index: tuple(unique_points[index]))
    old_to_new = {old: new for new, old in enumerate(order)}
    sorted_points = [unique_points[index] for index in order]
    canonical_faces: list[dict[str, Any]] = []
    face_keys: set[tuple[str, ...]] = set()
    for indices, hkl, generator in normalized_faces:
        loop = [f"v{old_to_new[index]:03d}" for index in indices]
        loop = _rotate_to_minimum(loop)
        key = tuple(sorted(loop))
        if key in face_keys:
            raise BrillouinContractError("BZ_DUPLICATE_FACE", "Duplicate faces are not allowed.")
        face_keys.add(key)
        points = [sorted_points[int(vertex_id[1:])] for vertex_id in loop]
        normal = _normalize(generator, "BZ_FACE_GENERATOR_INVALID")
        if _dot(_newell(points), normal) < 0:
            loop = _rotate_to_minimum(list(reversed(loop)))
            points = [sorted_points[int(vertex_id[1:])] for vertex_id in loop]
        area, centroid = _polygon_area_centroid(points)
        plane_offset = _norm(generator) / 2.0
        canonical_faces.append(
            {
                "face_id": "",
                "order_index": -1,
                "vertex_ids": loop,
                "edge_ids": [],
                "outward_normal": _canonical_vector(normal),
                "plane_offset": _canonical_number(plane_offset),
                "generator_hkl": list(hkl),
                "generator_cartesian": _canonical_vector(generator),
                "area": _canonical_number(area),
                "centroid": _canonical_vector(centroid),
                "winding": "ccw_from_outside",
            }
        )
    canonical_faces.sort(key=lambda face: (tuple(face["generator_hkl"]), tuple(face["vertex_ids"])))
    for index, face in enumerate(canonical_faces):
        face["face_id"] = f"f{index:03d}"
        face["order_index"] = index
    edge_faces: dict[tuple[str, str], list[str]] = {}
    for face in canonical_faces:
        loop = face["vertex_ids"]
        keys = [_edge_key(loop[index], loop[(index + 1) % len(loop)]) for index in range(len(loop))]
        for key in keys:
            edge_faces.setdefault(key, []).append(face["face_id"])
    if len(edge_faces) > BRILLOUIN_CAPS["max_edges"] or len(canonical_faces) > BRILLOUIN_CAPS["max_faces"]:
        raise BrillouinContractError("BZ_CAP_EXCEEDED", "The topology cap is exceeded.")
    sorted_edge_keys = sorted(edge_faces)
    edge_id_by_key = {key: f"e{index:03d}" for index, key in enumerate(sorted_edge_keys)}
    edges = []
    for index, key in enumerate(sorted_edge_keys):
        start, end = (sorted_points[int(vertex_id[1:])] for vertex_id in key)
        edges.append(
            {
                "edge_id": edge_id_by_key[key],
                "order_index": index,
                "vertex_ids": list(key),
                "incident_face_ids": sorted(edge_faces[key]),
                "length": _canonical_number(_distance(start, end)),
            }
        )
    for face in canonical_faces:
        loop = face["vertex_ids"]
        face["edge_ids"] = [edge_id_by_key[_edge_key(loop[index], loop[(index + 1) % len(loop)])] for index in range(len(loop))]
    incident_faces: dict[str, list[str]] = {f"v{index:03d}": [] for index in range(len(sorted_points))}
    for face in canonical_faces:
        for vertex_id in face["vertex_ids"]:
            incident_faces[vertex_id].append(face["face_id"])
    inverse_reciprocal = _inverse_checked(reciprocal, "BZ_RECIPROCAL_LATTICE_SINGULAR")
    vertices = [
        {
            "vertex_id": f"v{index:03d}",
            "order_index": index,
            "cartesian_coordinates": point,
            "fractional_coordinates": _canonical_vector(_vector_matrix(point, inverse_reciprocal)),
            "incident_face_ids": sorted(incident_faces[f"v{index:03d}"]),
        }
        for index, point in enumerate(sorted_points)
    ]
    surface_area = sum(float(face["area"]) for face in canonical_faces)
    volume = _polyhedron_volume(canonical_faces, sorted_points)
    binding = {
        "reciprocal_lattice_sha256": reciprocal_lattice["content_hash"],
        "primitive_lattice_sha256": reciprocal_lattice["real_lattice_binding"]["primitive_lattice_sha256"],
        "source_structure_sha256": reciprocal_lattice["real_lattice_binding"]["source_structure_sha256"],
        "convention": RECIPROCAL_CONVENTION,
        "units": RECIPROCAL_UNITS,
    }
    payload: dict[str, Any] = {
        "schema_version": BRILLOUIN_ZONE_SCHEMA_VERSION,
        "content_hash": "",
        "reciprocal_lattice_binding": binding,
        "definition": "wigner_seitz",
        "center": [0.0, 0.0, 0.0],
        "vertices": vertices,
        "edges": edges,
        "faces": canonical_faces,
        "volume": _canonical_number(volume),
        "surface_area": _canonical_number(surface_area),
        "topology": {
            "vertex_count": len(vertices),
            "edge_count": len(edges),
            "face_count": len(canonical_faces),
            "euler_characteristic": len(vertices) - len(edges) + len(canonical_faces),
            "closed": True,
            "convex": True,
            "manifold": True,
            "connected": True,
            "centrally_symmetric": True,
        },
        "tolerances": dict(BRILLOUIN_TOLERANCES),
        "warnings": [],
        "provenance": {
            "producer": "phase10i.contract",
            "producer_version": "1.0.0",
            "geometry_method": provider_method,
            "deterministic": True,
        },
        "security": _security_copy(),
    }
    payload["content_hash"] = brillouin_content_hash(payload)
    result = validate_brillouin_zone(payload, reciprocal_lattice)
    if not result.valid:
        raise BrillouinContractError(result.errors[0], "The Brillouin-zone contract is invalid.")
    return payload


def build_kpath_contract(
    reciprocal_lattice: dict[str, Any], *, point_specs: Sequence[dict[str, Any]],
    variant_specs: Sequence[dict[str, Any]], selected_variant_key: str,
    provider: dict[str, Any], path_convention: str, time_reversal_used: bool,
) -> dict[str, Any]:
    reciprocal_result = validate_reciprocal_lattice(reciprocal_lattice)
    if not reciprocal_result.valid:
        raise BrillouinContractError(reciprocal_result.errors[0], "The reciprocal lattice binding is invalid.")
    if path_convention not in SUPPORTED_PATH_CONVENTIONS or type(time_reversal_used) is not bool:
        raise BrillouinContractError("BZ_PROVIDER_METADATA_INVALID", "The path policy is invalid.")
    source_hash = reciprocal_lattice["real_lattice_binding"]["source_structure_sha256"]
    provider_value = _normalize_provider(provider, source_hash)
    if provider_value["time_reversal_used"] is not time_reversal_used:
        raise BrillouinContractError("BZ_TIME_REVERSAL_POLICY_UNSUPPORTED", "Provider time reversal is inconsistent.")
    reciprocal = reciprocal_lattice["matrix"]
    coordinate_tolerance = float(BRILLOUIN_TOLERANCES["label_coordinate_absolute"])
    canonical_specs: list[dict[str, Any]] = []
    alias_to_canonical: dict[str, str] = {}
    for spec in point_specs:
        if not isinstance(spec, dict) or set(spec) != {"label_key", "display_label", "aliases", "fractional_coordinates"}:
            raise BrillouinContractError("BZ_HIGH_SYMMETRY_POINT_INVALID", "Point input is invalid.")
        label_key = _validated_label_key(spec["label_key"])
        display = _safe_label(spec["display_label"])
        aliases = [_safe_label(alias) for alias in spec["aliases"]]
        coordinates = _validated_vector(spec["fractional_coordinates"], "BZ_HIGH_SYMMETRY_POINT_INVALID")
        existing = next(
            (item for item in canonical_specs if _near_vector(item["fractional_coordinates"], coordinates, coordinate_tolerance)),
            None,
        )
        if existing is None:
            canonical_specs.append(
                {
                    "label_key": label_key,
                    "display_label": display,
                    "aliases": sorted(set(aliases)),
                    "source_label_keys": [label_key],
                    "fractional_coordinates": _canonical_vector(coordinates),
                }
            )
            alias_to_canonical[label_key] = label_key
        else:
            existing["source_label_keys"] = sorted(set(existing["source_label_keys"] + [label_key]))
            existing["aliases"] = sorted(set(existing["aliases"] + aliases + [label_key, display]))
            alias_to_canonical[label_key] = existing["label_key"]
    if len(canonical_specs) > BRILLOUIN_CAPS["max_high_symmetry_points"]:
        raise BrillouinContractError("BZ_CAP_EXCEEDED", "The high-symmetry point cap is exceeded.")
    canonical_specs.sort(key=lambda item: (item["label_key"], tuple(item["fractional_coordinates"])))
    points: list[dict[str, Any]] = []
    point_by_key: dict[str, dict[str, Any]] = {}
    for spec in canonical_specs:
        identity = {
            "provider": provider_value["name"],
            "convention": path_convention,
            "primitive_lattice_sha256": reciprocal_lattice["real_lattice_binding"]["primitive_lattice_sha256"],
            "fractional_coordinates": spec["fractional_coordinates"],
            "label_key": spec["label_key"],
            "namespace": selected_variant_key,
        }
        point = {
            "point_id": f"kp-{brillouin_content_hash(identity)[:16]}",
            "label_key": spec["label_key"],
            "display_label": spec["display_label"],
            "aliases": spec["aliases"],
            "fractional_coordinates": spec["fractional_coordinates"],
            "cartesian_coordinates": reciprocal_fractional_to_cartesian(spec["fractional_coordinates"], reciprocal),
            "basis": RECIPROCAL_BASIS,
            "provider_identity": {
                "provider": provider_value["name"],
                "namespace": selected_variant_key,
                "source_label_keys": spec["source_label_keys"],
            },
            "metadata": {"coincident_labels_merged": len(spec["source_label_keys"]) > 1},
        }
        points.append(point)
        for key in spec["source_label_keys"]:
            point_by_key[key] = point
        point_by_key[spec["label_key"]] = point
    if not isinstance(variant_specs, Sequence) or not 1 <= len(variant_specs) <= BRILLOUIN_CAPS["max_path_variants"]:
        raise BrillouinContractError("BZ_CAP_EXCEEDED", "The path variant cap is exceeded.")
    variants: list[dict[str, Any]] = []
    segments: list[dict[str, Any]] = []
    discontinuities: list[dict[str, Any]] = []
    seen_variant_keys: set[str] = set()
    for variant_spec in sorted(variant_specs, key=lambda item: str(item.get("variant_key", ""))):
        if not isinstance(variant_spec, dict) or set(variant_spec) != {"variant_key", "description", "branches"}:
            raise BrillouinContractError("BZ_PATH_SEGMENT_INVALID", "The path variant input is invalid.")
        variant_key = _safe_text(variant_spec["variant_key"], "BZ_PATH_SEGMENT_INVALID")
        if variant_key in seen_variant_keys:
            raise BrillouinContractError("BZ_PATH_SEGMENT_INVALID", "Duplicate path variants are not allowed.")
        seen_variant_keys.add(variant_key)
        branches = variant_spec["branches"]
        if not isinstance(branches, list) or not branches:
            raise BrillouinContractError("BZ_PATH_SEGMENT_INVALID", "A path variant must contain branches.")
        variant_id = f"variant-{brillouin_content_hash({'provider': provider_value['name'], 'key': variant_key})[:12]}"
        variant_segment_ids: list[str] = []
        distance = 0.0
        prior_segment: dict[str, Any] | None = None
        order_index = 0
        for branch_index, branch in enumerate(branches):
            if not isinstance(branch, list) or len(branch) < 2:
                raise BrillouinContractError("BZ_PATH_SEGMENT_INVALID", "Each path branch needs two points.")
            for pair_index in range(len(branch) - 1):
                source_key = _validated_label_key(branch[pair_index])
                target_key = _validated_label_key(branch[pair_index + 1])
                source = point_by_key.get(source_key)
                target = point_by_key.get(target_key)
                if source is None or target is None:
                    raise BrillouinContractError("BZ_PATH_ENDPOINT_MISSING", "A path endpoint is missing.")
                length = _distance(source["cartesian_coordinates"], target["cartesian_coordinates"])
                discontinuity_before = branch_index > 0 and pair_index == 0
                segment_identity = {
                    "variant_id": variant_id,
                    "order_index": order_index,
                    "source": source["point_id"],
                    "target": target["point_id"],
                    "source_label": source_key,
                    "target_label": target_key,
                }
                segment = {
                    "segment_id": f"ks-{brillouin_content_hash(segment_identity)[:16]}",
                    "variant_id": variant_id,
                    "order_index": order_index,
                    "start_point_id": source["point_id"],
                    "end_point_id": target["point_id"],
                    "start_label_key": source_key,
                    "end_label_key": target_key,
                    "length": _canonical_number(length),
                    "distance_start": _canonical_number(distance),
                    "distance_end": _canonical_number(distance + length),
                    "discontinuity_before": discontinuity_before,
                    "discontinuity_after": False,
                    "source_branch_identity": f"{variant_key}:branch-{branch_index}",
                }
                if discontinuity_before and prior_segment is not None:
                    prior_segment["discontinuity_after"] = True
                    discontinuities.append(
                        {
                            "discontinuity_id": f"kd-{len(discontinuities):03d}",
                            "variant_id": variant_id,
                            "after_segment_id": prior_segment["segment_id"],
                            "before_segment_id": segment["segment_id"],
                        }
                    )
                segments.append(segment)
                variant_segment_ids.append(segment["segment_id"])
                prior_segment = segment
                distance += length
                order_index += 1
        variants.append(
            {
                "variant_id": variant_id,
                "provider_variant_key": variant_key,
                "selected": variant_key == selected_variant_key,
                "segment_ids": variant_segment_ids,
                "description": _safe_text(variant_spec["description"], "BZ_PATH_SEGMENT_INVALID"),
            }
        )
    if sum(1 for variant in variants if variant["selected"]) != 1:
        raise BrillouinContractError("BZ_PATH_VARIANT_INVALID", "Exactly one path variant must be selected.")
    if len(segments) > BRILLOUIN_CAPS["max_path_segments"] or len(discontinuities) > BRILLOUIN_CAPS["max_discontinuities"]:
        raise BrillouinContractError("BZ_CAP_EXCEEDED", "The path cap is exceeded.")
    binding = {
        "reciprocal_lattice_sha256": reciprocal_lattice["content_hash"],
        "primitive_lattice_sha256": reciprocal_lattice["real_lattice_binding"]["primitive_lattice_sha256"],
        "source_structure_sha256": source_hash,
        "convention": RECIPROCAL_CONVENTION,
        "units": RECIPROCAL_UNITS,
    }
    payload: dict[str, Any] = {
        "schema_version": KPATH_SCHEMA_VERSION,
        "content_hash": "",
        "reciprocal_lattice_binding": binding,
        "provider": provider_value,
        "path_convention": path_convention,
        "selected_variant_id": next(variant["variant_id"] for variant in variants if variant["selected"]),
        "time_reversal_used": time_reversal_used,
        "magnetic_policy": "non_magnetic_only",
        "points": points,
        "path_variants": variants,
        "segments": segments,
        "discontinuities": discontinuities,
        "distance_policy": {
            "unit": RECIPROCAL_UNITS,
            "accumulation": "per_variant_cumulative_without_discontinuity_jump",
            "metric": "euclidean_reciprocal_cartesian",
        },
        "tolerances": dict(BRILLOUIN_TOLERANCES),
        "warnings": [],
        "provenance": {
            "producer": "phase10i.contract",
            "producer_version": "1.0.0",
            "deterministic": True,
            "geometry_independent": True,
        },
        "security": _security_copy(),
    }
    payload["content_hash"] = brillouin_content_hash(payload)
    result = validate_kpath(payload, reciprocal_lattice)
    if not result.valid:
        raise BrillouinContractError(result.errors[0], "The k-path contract is invalid.")
    return payload


def build_brillouin_zone_manifest(
    reciprocal_lattice: dict[str, Any], zone: dict[str, Any], kpath: dict[str, Any] | None = None
) -> dict[str, Any]:
    artifacts = [
        {
            "name": "reciprocal_lattice.json",
            "schema_version": RECIPROCAL_LATTICE_SCHEMA_VERSION,
            "sha256": reciprocal_lattice.get("content_hash"),
            "media_type": "application/json",
        },
        {
            "name": "brillouin_zone.json",
            "schema_version": BRILLOUIN_ZONE_SCHEMA_VERSION,
            "sha256": zone.get("content_hash"),
            "media_type": "application/json",
        },
    ]
    if kpath is not None:
        artifacts.append(
            {
                "name": "kpath.json",
                "schema_version": KPATH_SCHEMA_VERSION,
                "sha256": kpath.get("content_hash"),
                "media_type": "application/json",
            }
        )
    identity = {
        "structure": reciprocal_lattice["real_lattice_binding"]["source_structure_sha256"],
        "artifacts": artifacts,
        "provider": reciprocal_lattice["provider"],
    }
    payload: dict[str, Any] = {
        "schema_version": BRILLOUIN_ZONE_MANIFEST_SCHEMA_VERSION,
        "content_hash": "",
        "package_id": f"bzpkg-{brillouin_content_hash(identity)[:20]}",
        "structure_identity": reciprocal_lattice["real_lattice_binding"]["source_structure_sha256"],
        "entry_artifact": "brillouin_zone.json",
        "artifacts": artifacts,
        "provider": reciprocal_lattice["provider"],
        "convention": RECIPROCAL_CONVENTION,
        "units": RECIPROCAL_UNITS,
        "capabilities": {
            "reciprocal_lattice": True,
            "brillouin_zone_geometry": True,
            "high_symmetry_kpath": kpath is not None,
            "renderer_included": False,
            "webgl_artifact_included": False,
            "preview_mode": "json_only",
        },
        "provenance": {
            "producer": "phase10i.contract",
            "producer_version": "1.0.0",
            "deterministic": True,
            "production_adapter_registered": False,
        },
        "security": _security_copy(),
    }
    payload["content_hash"] = brillouin_content_hash(payload)
    result = validate_brillouin_zone_manifest(payload, reciprocal_lattice, zone, kpath)
    if not result.valid:
        raise BrillouinContractError(result.errors[0], "The Brillouin-zone manifest is invalid.")
    return payload


def validate_reciprocal_lattice(value: Any, *, raw_size_bytes: int | None = None) -> BrillouinValidationResult:
    errors: set[str] = set()
    warnings: set[str] = set()
    counts: dict[str, int] = {"transformations": 0}
    fields = {
        "schema_version", "content_hash", "convention", "units", "basis_orientation", "basis_role",
        "real_lattice_binding", "matrix", "dual_product", "determinant", "cell_volume", "real_cell_volume",
        "transformations", "tolerances", "provider", "provenance", "security",
    }
    if not isinstance(value, dict):
        return _result({"BZ_SCHEMA_VALIDATION_FAILED"}, warnings, counts)
    if set(value) != fields:
        errors.add("BZ_SCHEMA_VALIDATION_FAILED")
    if value.get("schema_version") != RECIPROCAL_LATTICE_SCHEMA_VERSION:
        errors.add("BZ_SCHEMA_UNSUPPORTED")
    _validate_common(value, errors, raw_size_bytes)
    if value.get("convention") != RECIPROCAL_CONVENTION or value.get("units") != RECIPROCAL_UNITS:
        errors.add("BZ_RECIPROCAL_CONVENTION_MISMATCH")
    if value.get("basis_orientation") != "row_vectors" or value.get("basis_role") != "standardized_primitive_reciprocal":
        errors.add("BZ_RECIPROCAL_BASIS_INVALID")
    binding = value.get("real_lattice_binding")
    primitive: list[list[float]] | None = None
    source: list[list[float]] | None = None
    if not _validate_real_lattice_binding(binding, errors):
        errors.add("BZ_STRUCTURE_BINDING_INVALID")
    else:
        primitive = binding["primitive_real_lattice"]
        source = binding["source_real_lattice"]
    try:
        matrix = _validated_matrix(value.get("matrix"), "BZ_RECIPROCAL_LATTICE_INVALID")
        reciprocal_det = _determinant(matrix)
        _inverse_checked(matrix, "BZ_RECIPROCAL_LATTICE_SINGULAR")
    except BrillouinContractError as exc:
        errors.add(exc.code)
        matrix = []
        reciprocal_det = math.nan
    if primitive is not None and matrix:
        expected = reciprocal_lattice_physics_2pi(primitive)
        dual = _matrix_multiply(primitive, _transpose(matrix))
        if not _near_matrix(matrix, expected, float(BRILLOUIN_TOLERANCES["reciprocal_duality_absolute"])):
            errors.add("BZ_RECIPROCAL_DUALITY_FAILED")
        if not _near_matrix(value.get("dual_product"), dual, float(BRILLOUIN_TOLERANCES["reciprocal_duality_absolute"])):
            errors.add("BZ_RECIPROCAL_DUALITY_FAILED")
        expected_dual = [[2 * math.pi if row == column else 0.0 for column in range(3)] for row in range(3)]
        if not _near_matrix(dual, expected_dual, float(BRILLOUIN_TOLERANCES["reciprocal_duality_absolute"])):
            errors.add("BZ_RECIPROCAL_DUALITY_FAILED")
        real_volume = abs(_determinant(primitive))
        reciprocal_volume = abs(reciprocal_det)
        expected_volume = (2 * math.pi) ** 3 / real_volume
        if not _relative_near(reciprocal_volume, expected_volume, float(BRILLOUIN_TOLERANCES["volume_relative"])):
            errors.add("BZ_VOLUME_INVARIANT_FAILED")
        if not _number_near(value.get("real_cell_volume"), real_volume, 1e-10) or not _number_near(value.get("cell_volume"), reciprocal_volume, 1e-10):
            errors.add("BZ_VOLUME_INVARIANT_FAILED")
        if not _number_near(value.get("determinant"), reciprocal_det, 1e-10):
            errors.add("BZ_VOLUME_INVARIANT_FAILED")
    transformations = value.get("transformations")
    if not isinstance(transformations, list):
        errors.add("BZ_TRANSFORMATION_INVALID")
        transformations = []
    counts["transformations"] = len(transformations)
    if len(transformations) > BRILLOUIN_CAPS["max_transformations"]:
        errors.add("BZ_CAP_EXCEEDED")
    _validate_transformations(transformations, source, primitive, errors)
    _validate_provider(value.get("provider"), binding.get("source_structure_sha256") if isinstance(binding, dict) else None, errors)
    _validate_tolerances(value.get("tolerances"), errors)
    return _result(errors, warnings, counts)


def validate_brillouin_zone(
    value: Any, reciprocal_lattice: dict[str, Any] | None = None, *, raw_size_bytes: int | None = None
) -> BrillouinValidationResult:
    errors: set[str] = set()
    warnings: set[str] = set()
    counts = {"vertices": 0, "edges": 0, "faces": 0}
    fields = {
        "schema_version", "content_hash", "reciprocal_lattice_binding", "definition", "center", "vertices",
        "edges", "faces", "volume", "surface_area", "topology", "tolerances", "warnings", "provenance", "security",
    }
    if not isinstance(value, dict):
        return _result({"BZ_SCHEMA_VALIDATION_FAILED"}, warnings, counts)
    if set(value) != fields:
        errors.add("BZ_SCHEMA_VALIDATION_FAILED")
    if value.get("schema_version") != BRILLOUIN_ZONE_SCHEMA_VERSION:
        errors.add("BZ_SCHEMA_UNSUPPORTED")
    _validate_common(value, errors, raw_size_bytes)
    if value.get("definition") != "wigner_seitz" or not _near_vector(value.get("center"), [0, 0, 0], 0.0):
        errors.add("BZ_ORIGIN_OUTSIDE")
    _validate_tolerances(value.get("tolerances"), errors)
    vertices = value.get("vertices") if isinstance(value.get("vertices"), list) else []
    edges = value.get("edges") if isinstance(value.get("edges"), list) else []
    faces = value.get("faces") if isinstance(value.get("faces"), list) else []
    counts.update(vertices=len(vertices), edges=len(edges), faces=len(faces))
    if not isinstance(value.get("vertices"), list) or not isinstance(value.get("edges"), list) or not isinstance(value.get("faces"), list):
        errors.add("BZ_POLYHEDRON_INVALID")
    if len(vertices) > BRILLOUIN_CAPS["max_vertices"] or len(edges) > BRILLOUIN_CAPS["max_edges"] or len(faces) > BRILLOUIN_CAPS["max_faces"]:
        errors.add("BZ_CAP_EXCEEDED")
    binding = value.get("reciprocal_lattice_binding")
    reciprocal: list[list[float]] | None = None
    if not _validate_reciprocal_binding(binding, errors):
        errors.add("BZ_RECIPROCAL_BINDING_INVALID")
    if reciprocal_lattice is not None:
        reciprocal_result = validate_reciprocal_lattice(reciprocal_lattice)
        if not reciprocal_result.valid:
            errors.add("BZ_RECIPROCAL_BINDING_INVALID")
        elif not isinstance(binding, dict) or binding.get("reciprocal_lattice_sha256") != reciprocal_lattice.get("content_hash"):
            errors.add("BZ_RECIPROCAL_BINDING_INVALID")
        else:
            reciprocal = reciprocal_lattice["matrix"]
    _validate_polyhedron(value, vertices, edges, faces, reciprocal, errors)
    warning_values = value.get("warnings")
    if not isinstance(warning_values, list) or len(warning_values) > BRILLOUIN_CAPS["max_warnings"] or any(not _valid_safe_text(item, 128) for item in warning_values):
        errors.add("BZ_WARNING_INVALID")
    return _result(errors, warnings, counts)


def validate_kpath(
    value: Any, reciprocal_lattice: dict[str, Any] | None = None, *, raw_size_bytes: int | None = None
) -> BrillouinValidationResult:
    errors: set[str] = set()
    warnings: set[str] = set()
    counts = {"points": 0, "variants": 0, "segments": 0, "discontinuities": 0}
    fields = {
        "schema_version", "content_hash", "reciprocal_lattice_binding", "provider", "path_convention",
        "selected_variant_id", "time_reversal_used", "magnetic_policy", "points", "path_variants", "segments",
        "discontinuities", "distance_policy", "tolerances", "warnings", "provenance", "security",
    }
    if not isinstance(value, dict):
        return _result({"BZ_SCHEMA_VALIDATION_FAILED"}, warnings, counts)
    if set(value) != fields:
        errors.add("BZ_SCHEMA_VALIDATION_FAILED")
    if value.get("schema_version") != KPATH_SCHEMA_VERSION:
        errors.add("BZ_SCHEMA_UNSUPPORTED")
    _validate_common(value, errors, raw_size_bytes)
    binding = value.get("reciprocal_lattice_binding")
    if not _validate_reciprocal_binding(binding, errors):
        errors.add("BZ_RECIPROCAL_BINDING_INVALID")
    reciprocal = None
    if reciprocal_lattice is not None:
        reciprocal_result = validate_reciprocal_lattice(reciprocal_lattice)
        if not reciprocal_result.valid or not isinstance(binding, dict) or binding.get("reciprocal_lattice_sha256") != reciprocal_lattice.get("content_hash"):
            errors.add("BZ_RECIPROCAL_BINDING_INVALID")
        else:
            reciprocal = reciprocal_lattice["matrix"]
    source_hash = binding.get("source_structure_sha256") if isinstance(binding, dict) else None
    _validate_provider(value.get("provider"), source_hash, errors)
    if value.get("path_convention") not in SUPPORTED_PATH_CONVENTIONS:
        errors.add("BZ_PROVIDER_METADATA_INVALID")
    if type(value.get("time_reversal_used")) is not bool or value.get("magnetic_policy") != "non_magnetic_only":
        errors.add("BZ_TIME_REVERSAL_POLICY_UNSUPPORTED")
    if isinstance(value.get("provider"), dict) and value["provider"].get("time_reversal_used") is not value.get("time_reversal_used"):
        errors.add("BZ_TIME_REVERSAL_POLICY_UNSUPPORTED")
    _validate_tolerances(value.get("tolerances"), errors)
    points = value.get("points") if isinstance(value.get("points"), list) else []
    variants = value.get("path_variants") if isinstance(value.get("path_variants"), list) else []
    segments = value.get("segments") if isinstance(value.get("segments"), list) else []
    discontinuities = value.get("discontinuities") if isinstance(value.get("discontinuities"), list) else []
    counts.update(points=len(points), variants=len(variants), segments=len(segments), discontinuities=len(discontinuities))
    if len(points) > BRILLOUIN_CAPS["max_high_symmetry_points"] or len(variants) > BRILLOUIN_CAPS["max_path_variants"] or len(segments) > BRILLOUIN_CAPS["max_path_segments"] or len(discontinuities) > BRILLOUIN_CAPS["max_discontinuities"]:
        errors.add("BZ_CAP_EXCEEDED")
    point_by_id = _validate_points(points, reciprocal, errors)
    variant_by_id = _validate_variants(variants, value.get("selected_variant_id"), errors)
    segment_by_id = _validate_segments(segments, point_by_id, variant_by_id, errors)
    _validate_discontinuities(discontinuities, segment_by_id, errors)
    distance_policy = value.get("distance_policy")
    if not isinstance(distance_policy, dict) or set(distance_policy) != {"unit", "accumulation", "metric"} or distance_policy.get("unit") != RECIPROCAL_UNITS or distance_policy.get("accumulation") != "per_variant_cumulative_without_discontinuity_jump" or distance_policy.get("metric") != "euclidean_reciprocal_cartesian":
        errors.add("BZ_PATH_DISTANCE_INVALID")
    warning_values = value.get("warnings")
    if not isinstance(warning_values, list) or len(warning_values) > BRILLOUIN_CAPS["max_warnings"] or any(not _valid_safe_text(item, 128) for item in warning_values):
        errors.add("BZ_WARNING_INVALID")
    return _result(errors, warnings, counts)


def validate_brillouin_zone_manifest(
    value: Any, reciprocal_lattice: dict[str, Any] | None = None,
    zone: dict[str, Any] | None = None, kpath: dict[str, Any] | None = None,
    *, raw_size_bytes: int | None = None,
) -> BrillouinValidationResult:
    errors: set[str] = set()
    counts = {"artifacts": 0}
    fields = {
        "schema_version", "content_hash", "package_id", "structure_identity", "entry_artifact", "artifacts",
        "provider", "convention", "units", "capabilities", "provenance", "security",
    }
    if not isinstance(value, dict):
        return _result({"BZ_SCHEMA_VALIDATION_FAILED"}, set(), counts)
    if set(value) != fields:
        errors.add("BZ_SCHEMA_VALIDATION_FAILED")
    if value.get("schema_version") != BRILLOUIN_ZONE_MANIFEST_SCHEMA_VERSION:
        errors.add("BZ_SCHEMA_UNSUPPORTED")
    _validate_common(value, errors, raw_size_bytes)
    if not isinstance(value.get("package_id"), str) or not value["package_id"].startswith("bzpkg-"):
        errors.add("BZ_MANIFEST_INVALID")
    if not _sha(value.get("structure_identity")) or value.get("entry_artifact") != "brillouin_zone.json" or value.get("convention") != RECIPROCAL_CONVENTION or value.get("units") != RECIPROCAL_UNITS:
        errors.add("BZ_MANIFEST_INVALID")
    _validate_provider(value.get("provider"), value.get("structure_identity"), errors)
    capabilities = value.get("capabilities")
    expected_capabilities = {
        "reciprocal_lattice": True,
        "brillouin_zone_geometry": True,
        "high_symmetry_kpath": kpath is not None,
        "renderer_included": False,
        "webgl_artifact_included": False,
        "preview_mode": "json_only",
    }
    if capabilities != expected_capabilities:
        errors.add("BZ_MANIFEST_CAPABILITY_INVALID")
    if reciprocal_lattice is not None and (
        not isinstance(reciprocal_lattice, dict)
        or not validate_reciprocal_lattice(reciprocal_lattice).valid
    ):
        errors.add("BZ_MANIFEST_INVALID")
    if zone is not None and (
        not isinstance(zone, dict)
        or not validate_brillouin_zone(
            zone,
            reciprocal_lattice if isinstance(reciprocal_lattice, dict) else None,
        ).valid
    ):
        errors.add("BZ_MANIFEST_INVALID")
    if kpath is not None and (
        not isinstance(kpath, dict)
        or not validate_kpath(
            kpath,
            reciprocal_lattice if isinstance(reciprocal_lattice, dict) else None,
        ).valid
    ):
        errors.add("BZ_MANIFEST_INVALID")
    artifacts = value.get("artifacts")
    if not isinstance(artifacts, list):
        errors.add("BZ_MANIFEST_INVALID")
        artifacts = []
    counts["artifacts"] = len(artifacts)
    expected = {
        "reciprocal_lattice.json": (
            RECIPROCAL_LATTICE_SCHEMA_VERSION,
            reciprocal_lattice.get("content_hash") if isinstance(reciprocal_lattice, dict) else None,
        ),
        "brillouin_zone.json": (
            BRILLOUIN_ZONE_SCHEMA_VERSION,
            zone.get("content_hash") if isinstance(zone, dict) else None,
        ),
    }
    if kpath is not None:
        expected["kpath.json"] = (
            KPATH_SCHEMA_VERSION,
            kpath.get("content_hash") if isinstance(kpath, dict) else None,
        )
    if [item.get("name") for item in artifacts if isinstance(item, dict)] != list(expected):
        errors.add("BZ_MANIFEST_INVALID")
    for artifact in artifacts:
        if not isinstance(artifact, dict) or set(artifact) != {"name", "schema_version", "sha256", "media_type"}:
            errors.add("BZ_MANIFEST_INVALID")
            continue
        schema_hash = expected.get(artifact.get("name"))
        if schema_hash is None or artifact.get("schema_version") != schema_hash[0] or artifact.get("media_type") != "application/json" or not _sha(artifact.get("sha256")):
            errors.add("BZ_MANIFEST_INVALID")
        if schema_hash is not None and schema_hash[1] is not None and artifact.get("sha256") != schema_hash[1]:
            errors.add("BZ_CONTENT_HASH_MISMATCH")
    return _result(errors, set(), counts)


def validate_phonon_kpath_compatibility(
    phonon_band: Any, reciprocal_lattice: Any, kpath: Any
) -> ReciprocalCompatibilityResult:
    errors: list[str] = []
    warnings: list[str] = []
    checks: list[dict[str, Any]] = []

    def check(name: str, condition: bool, code: str, left: Any, right: Any) -> None:
        checks.append({"name": name, "compatible": condition, "left": left, "right": right})
        if not condition:
            errors.append(code)

    band_result = validate_phonon_band(phonon_band)
    reciprocal_result = validate_reciprocal_lattice(reciprocal_lattice)
    kpath_result = validate_kpath(kpath, reciprocal_lattice if reciprocal_result.valid else None)
    check("phonon_band_valid", band_result.valid, "BZ_PHONON_BAND_INVALID", band_result.valid, True)
    check("reciprocal_valid", reciprocal_result.valid, "BZ_RECIPROCAL_BINDING_INVALID", reciprocal_result.valid, True)
    check("kpath_valid", kpath_result.valid, "BZ_KPATH_INVALID", kpath_result.valid, True)
    if not (isinstance(phonon_band, dict) and isinstance(reciprocal_lattice, dict) and isinstance(kpath, dict)):
        return ReciprocalCompatibilityResult(False, tuple(sorted(set(errors))), tuple(warnings), tuple(checks))
    binding = reciprocal_lattice.get("real_lattice_binding", {})
    check("structure_identity", phonon_band.get("structure_identity") == binding.get("source_structure_sha256"), "BZ_PHONON_STRUCTURE_MISMATCH", phonon_band.get("structure_identity"), binding.get("source_structure_sha256"))
    check("reciprocal_convention", phonon_band.get("reciprocal_convention") == RECIPROCAL_CONVENTION, "BZ_PHONON_CONVENTION_MISMATCH", phonon_band.get("reciprocal_convention"), RECIPROCAL_CONVENTION)
    check("coordinate_system", phonon_band.get("qpoint_coordinate_system") == "reciprocal_fractional", "BZ_PHONON_BASIS_MISMATCH", phonon_band.get("qpoint_coordinate_system"), "reciprocal_fractional")
    # Phase 10H names reciprocal path length as radian/angstrom. Under the
    # shared physics_2pi convention this is dimensionally the same Cartesian
    # reciprocal length represented here as angstrom^-1; the schema spellings
    # remain intentionally distinct and are matched explicitly.
    check(
        "path_distance_unit",
        phonon_band.get("path_distance_unit") == "radian_per_angstrom",
        "BZ_PHONON_UNIT_MISMATCH",
        phonon_band.get("path_distance_unit"),
        "radian_per_angstrom",
    )
    band_lattice = phonon_band.get("real_space_lattice_angstrom")
    primitive_hash = None
    try:
        primitive_hash = lattice_content_hash(band_lattice)
    except (BrillouinContractError, TypeError, ValueError):
        pass
    check("primitive_lattice", primitive_hash == binding.get("primitive_lattice_sha256"), "BZ_PHONON_PRIMITIVE_LATTICE_MISMATCH", primitive_hash, binding.get("primitive_lattice_sha256"))
    selected_variant = next((item for item in kpath.get("path_variants", []) if item.get("selected") is True), None)
    segment_by_id = {item.get("segment_id"): item for item in kpath.get("segments", []) if isinstance(item, dict)}
    selected_segments = [segment_by_id.get(identifier) for identifier in selected_variant.get("segment_ids", [])] if isinstance(selected_variant, dict) else []
    band_segments = phonon_band.get("segments") if isinstance(phonon_band.get("segments"), list) else []
    segment_match = len(selected_segments) == len(band_segments)
    if segment_match:
        point_by_id = {item.get("point_id"): item for item in kpath.get("points", []) if isinstance(item, dict)}
        qpoints = phonon_band.get("qpoints", [])
        for band_segment, path_segment in zip(band_segments, selected_segments, strict=True):
            if not isinstance(band_segment, dict) or not isinstance(path_segment, dict):
                segment_match = False
                break
            start_point = point_by_id.get(path_segment.get("start_point_id"))
            end_point = point_by_id.get(path_segment.get("end_point_id"))
            start_index, end_index = band_segment.get("start_qpoint_index"), band_segment.get("end_qpoint_index")
            if not isinstance(start_index, int) or not isinstance(end_index, int) or not (0 <= start_index < len(qpoints) and 0 <= end_index < len(qpoints)):
                segment_match = False
                break
            if not _near_vector(qpoints[start_index].get("coordinates"), start_point.get("fractional_coordinates") if isinstance(start_point, dict) else None, float(BRILLOUIN_TOLERANCES["path_endpoint_absolute"])) or not _near_vector(qpoints[end_index].get("coordinates"), end_point.get("fractional_coordinates") if isinstance(end_point, dict) else None, float(BRILLOUIN_TOLERANCES["path_endpoint_absolute"])):
                segment_match = False
                break
    check("selected_path_segments", segment_match, "BZ_PHONON_PATH_MISMATCH", len(band_segments), len(selected_segments))
    warnings.append("BZ_PHONON_TIME_REVERSAL_UNDECLARED")
    return ReciprocalCompatibilityResult(not errors, tuple(sorted(set(errors))), tuple(sorted(set(warnings))), tuple(checks))


def brillouin_schema_snapshots() -> dict[str, Any]:
    return {
        "versions": {
            "reciprocal_lattice": RECIPROCAL_LATTICE_SCHEMA_VERSION,
            "brillouin_zone": BRILLOUIN_ZONE_SCHEMA_VERSION,
            "kpath": KPATH_SCHEMA_VERSION,
            "manifest": BRILLOUIN_ZONE_MANIFEST_SCHEMA_VERSION,
            "tolerances": BRILLOUIN_TOLERANCE_SCHEMA_VERSION,
        },
        "convention": {
            "real_lattice": "row_vectors",
            "real_cartesian": "r_cart=r_frac*A",
            "reciprocal_lattice": "B=2*pi*A^-T",
            "reciprocal_cartesian": "k_cart=k_frac*B",
            "duality": "A*B^T=2*pi*I",
            "units": RECIPROCAL_UNITS,
        },
        "caps": dict(BRILLOUIN_CAPS),
        "tolerances": dict(BRILLOUIN_TOLERANCES),
        "security": _security_copy(),
        "tool_registration": "NOT_REGISTERED",
        "renderer": "NOT_INCLUDED",
    }


def _validate_common(value: dict[str, Any], errors: set[str], raw_size_bytes: int | None) -> None:
    computed_hash: str | None = None
    if raw_size_bytes is None:
        try:
            encoded = stable_brillouin_json(value).encode("utf-8")
            raw_size_bytes = len(encoded)
            hash_payload = dict(value)
            hash_payload.pop("content_hash", None)
            computed_hash = hashlib.sha256(stable_brillouin_json(hash_payload).encode("utf-8")).hexdigest()
        except (TypeError, ValueError, OverflowError, RecursionError):
            errors.add("BZ_NONFINITE_VALUE")
    else:
        try:
            computed_hash = brillouin_content_hash(value)
        except (TypeError, ValueError, OverflowError, RecursionError):
            errors.add("BZ_NONFINITE_VALUE")
    if raw_size_bytes is not None and raw_size_bytes > BRILLOUIN_CAPS["max_json_bytes"]:
        errors.add("BZ_PAYLOAD_TOO_LARGE")
    if not _sha(value.get("content_hash")) or computed_hash is None or value.get("content_hash") != computed_hash:
        errors.add("BZ_CONTENT_HASH_MISMATCH")
    if value.get("security") != BRILLOUIN_SECURITY:
        errors.add("BZ_SECURITY_INVALID")
    _scan_inert(value, errors)
    provenance = value.get("provenance")
    if not isinstance(provenance, dict) or provenance.get("deterministic") is not True:
        errors.add("BZ_PROVENANCE_INVALID")


def _validate_real_lattice_binding(value: Any, errors: set[str]) -> bool:
    fields = {
        "source_structure_id", "source_structure_sha256", "source_lattice_sha256", "primitive_lattice_sha256",
        "conventional_lattice_sha256", "source_basis_role", "primitive_basis_role", "source_real_lattice",
        "primitive_real_lattice", "conventional_real_lattice", "periodic_dimension", "ordered",
        "partial_occupancy", "magnetic",
    }
    if not isinstance(value, dict) or set(value) != fields:
        return False
    if not _valid_safe_text(value.get("source_structure_id"), 128) or not _sha(value.get("source_structure_sha256")):
        return False
    if value.get("source_basis_role") != "source_cell" or value.get("primitive_basis_role") != "standardized_primitive_cell":
        return False
    if value.get("periodic_dimension") != 3 or type(value.get("ordered")) is not bool or type(value.get("partial_occupancy")) is not bool or type(value.get("magnetic")) is not bool:
        return False
    if not value["ordered"] or value["partial_occupancy"] or value["magnetic"]:
        errors.add("BZ_STRUCTURE_SCOPE_UNSUPPORTED")
    try:
        source = _validated_real_lattice(value.get("source_real_lattice"))
        primitive = _validated_real_lattice(value.get("primitive_real_lattice"))
        conventional = value.get("conventional_real_lattice")
        if conventional is not None:
            conventional = _validated_real_lattice(conventional)
    except BrillouinContractError as exc:
        errors.add(exc.code)
        return False
    if value.get("source_lattice_sha256") != lattice_content_hash(source) or value.get("primitive_lattice_sha256") != lattice_content_hash(primitive):
        errors.add("BZ_STRUCTURE_BINDING_INVALID")
    expected_conventional = None if conventional is None else lattice_content_hash(conventional)
    if value.get("conventional_lattice_sha256") != expected_conventional:
        errors.add("BZ_STRUCTURE_BINDING_INVALID")
    return True


def _validate_reciprocal_binding(value: Any, errors: set[str]) -> bool:
    fields = {"reciprocal_lattice_sha256", "primitive_lattice_sha256", "source_structure_sha256", "convention", "units"}
    if not isinstance(value, dict) or set(value) != fields:
        return False
    if not all(_sha(value.get(key)) for key in ("reciprocal_lattice_sha256", "primitive_lattice_sha256", "source_structure_sha256")):
        return False
    if value.get("convention") != RECIPROCAL_CONVENTION or value.get("units") != RECIPROCAL_UNITS:
        errors.add("BZ_RECIPROCAL_CONVENTION_MISMATCH")
    return True


def _validate_transformations(
    transformations: list[Any], source: list[list[float]] | None, primitive: list[list[float]] | None,
    errors: set[str],
) -> None:
    fields = {
        "transformation_id", "old_basis", "new_basis", "matrix_representation", "matrix", "determinant",
        "real_lattice_formula", "real_fractional_formula", "reciprocal_basis_formula",
        "reciprocal_fractional_formula", "origin_shift", "cartesian_rotation",
    }
    ids: set[str] = set()
    found_source_to_primitive = False
    for item in transformations:
        if not isinstance(item, dict) or set(item) != fields:
            errors.add("BZ_TRANSFORMATION_INVALID")
            continue
        if item.get("transformation_id") in ids or item.get("old_basis") not in BASIS_ROLES or item.get("new_basis") not in BASIS_ROLES or item.get("old_basis") == item.get("new_basis"):
            errors.add("BZ_TRANSFORMATION_INVALID")
            continue
        ids.add(item["transformation_id"])
        if item.get("matrix_representation") != "finite_decimal" or item.get("real_lattice_formula") != "A_new=M*A_old" or item.get("real_fractional_formula") != "r_new=r_old*M^-1" or item.get("reciprocal_basis_formula") != "B_new=M^-T*B_old" or item.get("reciprocal_fractional_formula") != "k_new=k_old*M^T":
            errors.add("BZ_TRANSFORMATION_INVALID")
        try:
            matrix = _validated_matrix(item.get("matrix"), "BZ_TRANSFORMATION_INVALID")
            determinant = _determinant(matrix)
            _inverse_checked(matrix, "BZ_TRANSFORMATION_INVALID")
            _validated_vector(item.get("origin_shift"), "BZ_TRANSFORMATION_INVALID")
            _validated_matrix(item.get("cartesian_rotation"), "BZ_TRANSFORMATION_INVALID")
            if not _number_near(item.get("determinant"), determinant, 1e-10):
                errors.add("BZ_TRANSFORMATION_INVALID")
            if item.get("old_basis") == "source_cell" and item.get("new_basis") == "standardized_primitive_cell":
                found_source_to_primitive = True
                if source is not None and primitive is not None and not _near_matrix(_matrix_multiply(matrix, source), primitive, float(BRILLOUIN_TOLERANCES["transformation_roundtrip_absolute"])):
                    errors.add("BZ_TRANSFORMATION_INVALID")
                if source is not None and primitive is not None:
                    source_reciprocal = reciprocal_lattice_physics_2pi(source)
                    transformed_reciprocal = _matrix_multiply(_transpose(_inverse_checked(matrix, "BZ_TRANSFORMATION_INVALID")), source_reciprocal)
                    if not _near_matrix(transformed_reciprocal, reciprocal_lattice_physics_2pi(primitive), float(BRILLOUIN_TOLERANCES["transformation_roundtrip_absolute"])):
                        errors.add("BZ_TRANSFORMATION_INVALID")
        except (BrillouinContractError, TypeError, ValueError, OverflowError):
            errors.add("BZ_TRANSFORMATION_INVALID")
    if source is not None and primitive is not None and not _near_matrix(source, primitive, float(BRILLOUIN_TOLERANCES["transformation_roundtrip_absolute"])) and not found_source_to_primitive:
        errors.add("BZ_TRANSFORMATION_INVALID")


def _validate_provider(value: Any, source_hash: Any, errors: set[str]) -> None:
    fields = {
        "name", "version", "convention", "input_structure_sha256", "symprec_angstrom",
        "angle_tolerance_degrees", "time_reversal_used", "standardization_status", "warnings",
    }
    if not isinstance(value, dict) or set(value) != fields:
        errors.add("BZ_PROVIDER_METADATA_INVALID")
        return
    if value.get("name") not in SUPPORTED_PROVIDER_NAMES or not _valid_safe_text(value.get("version"), 64) or not _valid_safe_text(value.get("convention"), 64) or value.get("input_structure_sha256") != source_hash:
        errors.add("BZ_PROVIDER_METADATA_INVALID")
    if not _finite(value.get("symprec_angstrom")) or not 0 < float(value["symprec_angstrom"]) <= 1 or not _finite(value.get("angle_tolerance_degrees")) or not 0 < float(value["angle_tolerance_degrees"]) <= 30:
        errors.add("BZ_PROVIDER_METADATA_INVALID")
    if type(value.get("time_reversal_used")) is not bool or value.get("standardization_status") not in {"validated_fixture", "standardized", "explicit_validated", "unavailable"}:
        errors.add("BZ_PROVIDER_METADATA_INVALID")
    warnings = value.get("warnings")
    if not isinstance(warnings, list) or len(warnings) > BRILLOUIN_CAPS["max_warnings"] or any(not _valid_safe_text(item, 128) for item in warnings):
        errors.add("BZ_PROVIDER_METADATA_INVALID")
    try:
        if len(stable_brillouin_json(value).encode("utf-8")) > BRILLOUIN_CAPS["max_provider_metadata_bytes"]:
            errors.add("BZ_CAP_EXCEEDED")
    except (TypeError, ValueError, RecursionError):
        errors.add("BZ_PROVIDER_METADATA_INVALID")


def _normalize_provider(value: dict[str, Any], source_hash: str) -> dict[str, Any]:
    payload = {
        "name": value.get("name"),
        "version": value.get("version"),
        "convention": value.get("convention"),
        "input_structure_sha256": source_hash,
        "symprec_angstrom": value.get("symprec_angstrom"),
        "angle_tolerance_degrees": value.get("angle_tolerance_degrees"),
        "time_reversal_used": value.get("time_reversal_used"),
        "standardization_status": value.get("standardization_status"),
        "warnings": sorted(set(value.get("warnings", []))),
    }
    errors: set[str] = set()
    _validate_provider(payload, source_hash, errors)
    if errors:
        raise BrillouinContractError(sorted(errors)[0], "Provider metadata is invalid.")
    return payload


def _validate_tolerances(value: Any, errors: set[str]) -> None:
    if value != BRILLOUIN_TOLERANCES:
        errors.add("BZ_TOLERANCE_POLICY_INVALID")


def _validate_polyhedron(
    value: dict[str, Any], vertices: list[Any], edges: list[Any], faces: list[Any],
    reciprocal: list[list[float]] | None, errors: set[str],
) -> None:
    vertex_fields = {"vertex_id", "order_index", "cartesian_coordinates", "fractional_coordinates", "incident_face_ids"}
    edge_fields = {"edge_id", "order_index", "vertex_ids", "incident_face_ids", "length"}
    face_fields = {"face_id", "order_index", "vertex_ids", "edge_ids", "outward_normal", "plane_offset", "generator_hkl", "generator_cartesian", "area", "centroid", "winding"}
    merge_tol = float(BRILLOUIN_TOLERANCES["vertex_merge_angstrom_inverse"])
    vertex_by_id: dict[str, dict[str, Any]] = {}
    coordinates: list[list[float]] = []
    for index, vertex in enumerate(vertices):
        if not isinstance(vertex, dict) or set(vertex) != vertex_fields or vertex.get("vertex_id") != f"v{index:03d}" or vertex.get("order_index") != index:
            errors.add("BZ_VERTEX_INVALID")
            continue
        try:
            cartesian = _validated_vector(vertex.get("cartesian_coordinates"), "BZ_VERTEX_INVALID")
            fractional = _validated_vector(vertex.get("fractional_coordinates"), "BZ_VERTEX_INVALID")
        except BrillouinContractError:
            errors.add("BZ_VERTEX_INVALID")
            continue
        if coordinates and tuple(cartesian) < tuple(coordinates[-1]):
            errors.add("BZ_CANONICAL_ORDER_INVALID")
        if any(_near_vector(cartesian, other, merge_tol) for other in coordinates):
            errors.add("BZ_DUPLICATE_VERTEX")
        coordinates.append(cartesian)
        if reciprocal is not None and not _near_vector(reciprocal_fractional_to_cartesian(fractional, reciprocal), cartesian, float(BRILLOUIN_TOLERANCES["reciprocal_duality_absolute"])):
            errors.add("BZ_VERTEX_INVALID")
        if not isinstance(vertex.get("incident_face_ids"), list) or vertex["incident_face_ids"] != sorted(set(vertex["incident_face_ids"])):
            errors.add("BZ_VERTEX_INCIDENCE_INVALID")
        vertex_by_id[vertex["vertex_id"]] = vertex
    face_by_id: dict[str, dict[str, Any]] = {}
    edge_occurrences: dict[tuple[str, str], list[str]] = {}
    face_sort_keys: list[tuple[Any, ...]] = []
    for index, face in enumerate(faces):
        if not isinstance(face, dict) or set(face) != face_fields or face.get("face_id") != f"f{index:03d}" or face.get("order_index") != index:
            errors.add("BZ_FACE_INVALID")
            continue
        loop = face.get("vertex_ids")
        if not isinstance(loop, list) or not 3 <= len(loop) <= BRILLOUIN_CAPS["max_vertices_per_face"] or len(loop) != len(set(loop)) or any(vertex_id not in vertex_by_id for vertex_id in loop):
            errors.add("BZ_FACE_INVALID")
            continue
        if loop != _rotate_to_minimum(loop):
            errors.add("BZ_CANONICAL_ORDER_INVALID")
        try:
            normal = _validated_vector(face.get("outward_normal"), "BZ_FACE_INVALID")
            generator = _validated_vector(face.get("generator_cartesian"), "BZ_FACE_INVALID")
            hkl = face.get("generator_hkl")
            if not _integer_triplet(hkl, BRILLOUIN_CAPS["max_generator_search_radius"]) or hkl == [0, 0, 0]:
                raise BrillouinContractError("BZ_FACE_GENERATOR_INVALID", "Invalid generator.")
            expected_normal = _normalize(generator, "BZ_FACE_GENERATOR_INVALID")
            expected_offset = _norm(generator) / 2
            if reciprocal is not None and not _near_vector(reciprocal_fractional_to_cartesian(hkl, reciprocal), generator, float(BRILLOUIN_TOLERANCES["plane_absolute"])):
                errors.add("BZ_FACE_GENERATOR_INVALID")
            if not _near_vector(normal, expected_normal, float(BRILLOUIN_TOLERANCES["plane_absolute"])) or not _number_near(face.get("plane_offset"), expected_offset, float(BRILLOUIN_TOLERANCES["plane_absolute"])):
                errors.add("BZ_FACE_PLANE_INVALID")
            points = [vertex_by_id[vertex_id]["cartesian_coordinates"] for vertex_id in loop]
            if _dot(_newell(points), normal) <= 0:
                errors.add("BZ_FACE_WINDING_INVALID")
            area, centroid = _polygon_area_centroid(points)
            if area <= float(BRILLOUIN_TOLERANCES["edge_length_angstrom_inverse"]) or not _number_near(face.get("area"), area, 1e-9) or not _near_vector(face.get("centroid"), centroid, 1e-9):
                errors.add("BZ_FACE_INVALID")
            if face.get("winding") != "ccw_from_outside":
                errors.add("BZ_FACE_WINDING_INVALID")
            for point in coordinates:
                if _dot(normal, point) > expected_offset + float(BRILLOUIN_TOLERANCES["plane_absolute"]):
                    errors.add("BZ_NON_CONVEX_POLYHEDRON")
            for point in points:
                if abs(_dot(normal, point) - expected_offset) > float(BRILLOUIN_TOLERANCES["coplanarity_angstrom_inverse"]):
                    errors.add("BZ_FACE_NOT_COPLANAR")
            if expected_offset <= float(BRILLOUIN_TOLERANCES["plane_absolute"]):
                errors.add("BZ_ORIGIN_OUTSIDE")
        except BrillouinContractError as exc:
            errors.add(exc.code)
        expected_edge_keys = [_edge_key(loop[position], loop[(position + 1) % len(loop)]) for position in range(len(loop))]
        for key in expected_edge_keys:
            edge_occurrences.setdefault(key, []).append(face["face_id"])
        if not isinstance(face.get("edge_ids"), list) or len(face["edge_ids"]) != len(loop):
            errors.add("BZ_FACE_INCIDENCE_INVALID")
        face_by_id[face["face_id"]] = face
        sort_hkl = face.get("generator_hkl")
        canonical_hkl = (
            tuple(sort_hkl)
            if _integer_triplet(sort_hkl, BRILLOUIN_CAPS["max_generator_search_radius"])
            else (BRILLOUIN_CAPS["max_generator_search_radius"] + 1,) * 3
        )
        face_sort_keys.append((canonical_hkl, tuple(loop)))
    if face_sort_keys != sorted(face_sort_keys):
        errors.add("BZ_CANONICAL_ORDER_INVALID")
    edge_by_key: dict[tuple[str, str], dict[str, Any]] = {}
    for index, edge in enumerate(edges):
        if not isinstance(edge, dict) or set(edge) != edge_fields or edge.get("edge_id") != f"e{index:03d}" or edge.get("order_index") != index:
            errors.add("BZ_EDGE_INVALID")
            continue
        vertex_ids = edge.get("vertex_ids")
        if not isinstance(vertex_ids, list) or len(vertex_ids) != 2 or vertex_ids != sorted(vertex_ids) or vertex_ids[0] == vertex_ids[1] or any(vertex_id not in vertex_by_id for vertex_id in vertex_ids):
            errors.add("BZ_EDGE_INVALID")
            continue
        key = tuple(vertex_ids)
        if key in edge_by_key:
            errors.add("BZ_DUPLICATE_EDGE")
        expected_length = _distance(vertex_by_id[vertex_ids[0]]["cartesian_coordinates"], vertex_by_id[vertex_ids[1]]["cartesian_coordinates"])
        if expected_length <= float(BRILLOUIN_TOLERANCES["edge_length_angstrom_inverse"]) or not _number_near(edge.get("length"), expected_length, 1e-9):
            errors.add("BZ_EDGE_INVALID")
        incident = edge.get("incident_face_ids")
        if not isinstance(incident, list) or incident != sorted(set(incident)) or len(incident) != 2 or incident != sorted(edge_occurrences.get(key, [])):
            errors.add("BZ_NON_MANIFOLD_POLYHEDRON")
        edge_by_key[key] = edge
    if set(edge_by_key) != set(edge_occurrences):
        errors.add("BZ_OPEN_POLYHEDRON")
    for vertex_id, vertex in vertex_by_id.items():
        expected_faces = sorted(face_id for face_id, face in face_by_id.items() if vertex_id in face["vertex_ids"])
        if vertex.get("incident_face_ids") != expected_faces:
            errors.add("BZ_VERTEX_INCIDENCE_INVALID")
    for face in face_by_id.values():
        expected_edge_ids = [edge_by_key.get(_edge_key(face["vertex_ids"][position], face["vertex_ids"][(position + 1) % len(face["vertex_ids"])]), {}).get("edge_id") for position in range(len(face["vertex_ids"]))]
        if face.get("edge_ids") != expected_edge_ids:
            errors.add("BZ_FACE_INCIDENCE_INVALID")
    topology = value.get("topology")
    expected_topology = {
        "vertex_count": len(vertices), "edge_count": len(edges), "face_count": len(faces),
        "euler_characteristic": len(vertices) - len(edges) + len(faces),
        "closed": True, "convex": True, "manifold": True, "connected": True,
        "centrally_symmetric": True,
    }
    if topology != expected_topology or expected_topology["euler_characteristic"] != 2:
        errors.add("BZ_TOPOLOGY_INVALID")
    if coordinates:
        symmetry_tolerance = float(BRILLOUIN_TOLERANCES["central_symmetry_angstrom_inverse"])
        for point in coordinates:
            if not any(_near_vector([-value for value in point], candidate, symmetry_tolerance) for candidate in coordinates):
                errors.add("BZ_CENTRAL_SYMMETRY_FAILED")
        for face in faces:
            hkl = face.get("generator_hkl") if isinstance(face, dict) else None
            if not _integer_triplet(hkl, BRILLOUIN_CAPS["max_generator_search_radius"]):
                errors.add("BZ_FACE_GENERATOR_INVALID")
                continue
            if not any(
                isinstance(other, dict)
                and other.get("generator_hkl") == [-component for component in hkl]
                for other in faces
            ):
                errors.add("BZ_CENTRAL_SYMMETRY_FAILED")
    coordinate_by_id = {
        vertex_id: vertex["cartesian_coordinates"] for vertex_id, vertex in vertex_by_id.items()
    }
    valid_faces = [
        face
        for face in faces
        if isinstance(face, dict)
        and isinstance(face.get("vertex_ids"), list)
        and all(vertex_id in coordinate_by_id for vertex_id in face["vertex_ids"])
    ]
    volume = _polyhedron_volume(valid_faces, coordinate_by_id) if coordinate_by_id and face_by_id else 0.0
    surface = sum(float(face.get("area", 0)) for face in faces if isinstance(face, dict) and _finite(face.get("area")))
    if volume <= 0 or not _number_near(value.get("volume"), volume, max(1e-9, volume * float(BRILLOUIN_TOLERANCES["volume_relative"]))) or not _number_near(value.get("surface_area"), surface, 1e-8):
        errors.add("BZ_VOLUME_MISMATCH")
    if reciprocal is not None and not _relative_near(volume, abs(_determinant(reciprocal)), float(BRILLOUIN_TOLERANCES["volume_relative"])):
        errors.add("BZ_VOLUME_MISMATCH")


def _validate_points(points: list[Any], reciprocal: list[list[float]] | None, errors: set[str]) -> dict[str, dict[str, Any]]:
    fields = {"point_id", "label_key", "display_label", "aliases", "fractional_coordinates", "cartesian_coordinates", "basis", "provider_identity", "metadata"}
    by_id: dict[str, dict[str, Any]] = {}
    by_label: set[str] = set()
    coordinates: list[list[float]] = []
    for point in points:
        if not isinstance(point, dict) or set(point) != fields or not isinstance(point.get("point_id"), str) or not point["point_id"].startswith("kp-"):
            errors.add("BZ_HIGH_SYMMETRY_POINT_INVALID")
            continue
        if point["point_id"] in by_id or point.get("label_key") in by_label:
            errors.add("BZ_DUPLICATE_POINT_IDENTITY")
        try:
            _validated_label_key(point.get("label_key"))
            _safe_label(point.get("display_label"))
            aliases = point.get("aliases")
            if not isinstance(aliases, list) or len(aliases) > BRILLOUIN_CAPS["max_aliases_per_point"] or aliases != sorted(set(aliases)):
                raise BrillouinContractError("BZ_LABEL_INVALID", "Aliases are invalid.")
            for alias in aliases:
                _safe_label(alias)
            fractional = _validated_vector(point.get("fractional_coordinates"), "BZ_HIGH_SYMMETRY_POINT_INVALID")
            cartesian = _validated_vector(point.get("cartesian_coordinates"), "BZ_HIGH_SYMMETRY_POINT_INVALID")
            if any(_near_vector(fractional, prior, float(BRILLOUIN_TOLERANCES["label_coordinate_absolute"])) for prior in coordinates):
                errors.add("BZ_DUPLICATE_POINT_COORDINATE")
            coordinates.append(fractional)
            if reciprocal is not None and not _near_vector(reciprocal_fractional_to_cartesian(fractional, reciprocal), cartesian, float(BRILLOUIN_TOLERANCES["path_endpoint_absolute"])):
                errors.add("BZ_HIGH_SYMMETRY_POINT_INVALID")
            if point.get("basis") != RECIPROCAL_BASIS:
                errors.add("BZ_HIGH_SYMMETRY_POINT_INVALID")
            provider_identity = point.get("provider_identity")
            if not isinstance(provider_identity, dict) or set(provider_identity) != {"provider", "namespace", "source_label_keys"} or provider_identity.get("provider") not in SUPPORTED_PROVIDER_NAMES or not _valid_safe_text(provider_identity.get("namespace"), 64) or not isinstance(provider_identity.get("source_label_keys"), list):
                errors.add("BZ_HIGH_SYMMETRY_POINT_INVALID")
            metadata = point.get("metadata")
            if not isinstance(metadata, dict) or set(metadata) != {"coincident_labels_merged"} or type(metadata.get("coincident_labels_merged")) is not bool:
                errors.add("BZ_HIGH_SYMMETRY_POINT_INVALID")
        except BrillouinContractError as exc:
            errors.add(exc.code)
        by_id[point["point_id"]] = point
        by_label.add(point.get("label_key"))
    return by_id


def _validate_variants(variants: list[Any], selected_variant_id: Any, errors: set[str]) -> dict[str, dict[str, Any]]:
    fields = {"variant_id", "provider_variant_key", "selected", "segment_ids", "description"}
    by_id: dict[str, dict[str, Any]] = {}
    selected = 0
    for variant in variants:
        if not isinstance(variant, dict) or set(variant) != fields or not isinstance(variant.get("variant_id"), str) or not variant["variant_id"].startswith("variant-") or variant["variant_id"] in by_id:
            errors.add("BZ_PATH_VARIANT_INVALID")
            continue
        if not _valid_safe_text(variant.get("provider_variant_key"), 64) or not _valid_safe_text(variant.get("description"), 128) or type(variant.get("selected")) is not bool or not isinstance(variant.get("segment_ids"), list) or not variant["segment_ids"]:
            errors.add("BZ_PATH_VARIANT_INVALID")
        selected += int(variant.get("selected") is True)
        by_id[variant["variant_id"]] = variant
    if selected != 1 or selected_variant_id not in by_id or by_id.get(selected_variant_id, {}).get("selected") is not True:
        errors.add("BZ_PATH_VARIANT_INVALID")
    return by_id


def _validate_segments(segments: list[Any], points: dict[str, dict[str, Any]], variants: dict[str, dict[str, Any]], errors: set[str]) -> dict[str, dict[str, Any]]:
    fields = {"segment_id", "variant_id", "order_index", "start_point_id", "end_point_id", "start_label_key", "end_label_key", "length", "distance_start", "distance_end", "discontinuity_before", "discontinuity_after", "source_branch_identity"}
    by_id: dict[str, dict[str, Any]] = {}
    per_variant: dict[str, list[dict[str, Any]]] = {}
    for segment in segments:
        if not isinstance(segment, dict) or set(segment) != fields or not isinstance(segment.get("segment_id"), str) or not segment["segment_id"].startswith("ks-") or segment["segment_id"] in by_id:
            errors.add("BZ_PATH_SEGMENT_INVALID")
            continue
        if segment.get("variant_id") not in variants or segment.get("start_point_id") not in points or segment.get("end_point_id") not in points:
            errors.add("BZ_PATH_ENDPOINT_MISSING")
            continue
        try:
            _validated_label_key(segment.get("start_label_key"))
            _validated_label_key(segment.get("end_label_key"))
        except BrillouinContractError as exc:
            errors.add(exc.code)
        if not isinstance(segment.get("order_index"), int) or segment["order_index"] < 0 or type(segment.get("discontinuity_before")) is not bool or type(segment.get("discontinuity_after")) is not bool or not _valid_safe_text(segment.get("source_branch_identity"), 128):
            errors.add("BZ_PATH_SEGMENT_INVALID")
        start, end = points[segment["start_point_id"]], points[segment["end_point_id"]]
        start_coordinates = start.get("cartesian_coordinates")
        end_coordinates = end.get("cartesian_coordinates")
        distance_start = segment.get("distance_start")
        if not _near_vector(start_coordinates, start_coordinates, 0.0) or not _near_vector(end_coordinates, end_coordinates, 0.0):
            errors.add("BZ_PATH_DISTANCE_INVALID")
            continue
        expected_length = _distance(start_coordinates, end_coordinates)
        if (
            expected_length <= 0
            or not _number_near(segment.get("length"), expected_length, 1e-9)
            or not _finite(distance_start)
            or not _number_near(segment.get("distance_end"), float(distance_start) + expected_length, 1e-9)
        ):
            errors.add("BZ_PATH_DISTANCE_INVALID")
        by_id[segment["segment_id"]] = segment
        per_variant.setdefault(segment["variant_id"], []).append(segment)
    for variant_id, variant in variants.items():
        ordered = sorted(per_variant.get(variant_id, []), key=lambda item: item.get("order_index", -1))
        if [item.get("order_index") for item in ordered] != list(range(len(ordered))) or [item.get("segment_id") for item in ordered] != variant.get("segment_ids"):
            errors.add("BZ_PATH_SEGMENT_INVALID")
        prior_end = 0.0
        for item in ordered:
            if not _number_near(item.get("distance_start"), prior_end, 1e-9):
                errors.add("BZ_PATH_DISTANCE_INVALID")
            if _finite(item.get("distance_end")):
                prior_end = float(item["distance_end"])
            else:
                errors.add("BZ_PATH_DISTANCE_INVALID")
    return by_id


def _validate_discontinuities(discontinuities: list[Any], segments: dict[str, dict[str, Any]], errors: set[str]) -> None:
    fields = {"discontinuity_id", "variant_id", "after_segment_id", "before_segment_id"}
    seen: set[str] = set()
    expected: set[tuple[str, str]] = set()
    for segment in segments.values():
        if segment.get("discontinuity_after"):
            following = next((item for item in segments.values() if item.get("variant_id") == segment.get("variant_id") and item.get("order_index") == segment.get("order_index") + 1), None)
            if following is not None and following.get("discontinuity_before"):
                expected.add((segment["segment_id"], following["segment_id"]))
    actual: set[tuple[str, str]] = set()
    for item in discontinuities:
        if not isinstance(item, dict) or set(item) != fields or not isinstance(item.get("discontinuity_id"), str) or item["discontinuity_id"] in seen:
            errors.add("BZ_PATH_DISCONTINUITY_INVALID")
            continue
        seen.add(item["discontinuity_id"])
        before, after = segments.get(item.get("before_segment_id")), segments.get(item.get("after_segment_id"))
        if before is None or after is None or before.get("variant_id") != item.get("variant_id") or after.get("variant_id") != item.get("variant_id"):
            errors.add("BZ_PATH_DISCONTINUITY_INVALID")
            continue
        actual.add((item["after_segment_id"], item["before_segment_id"]))
    if actual != expected:
        errors.add("BZ_PATH_DISCONTINUITY_INVALID")


def _validated_real_lattice(value: Any) -> list[list[float]]:
    matrix = _validated_matrix(value, "BZ_REAL_LATTICE_SHAPE_INVALID")
    determinant = _determinant(matrix)
    scale = max(_norm(row) for row in matrix)
    if scale == 0 or abs(determinant) <= float(BRILLOUIN_TOLERANCES["real_lattice_determinant_relative"]) * scale**3:
        raise BrillouinContractError("BZ_REAL_LATTICE_SINGULAR", "The real-space lattice is singular.")
    inverse = _inverse(matrix, determinant)
    condition = _frobenius(matrix) * _frobenius(inverse)
    if not math.isfinite(condition) or condition > float(BRILLOUIN_TOLERANCES["real_lattice_condition_max"]):
        raise BrillouinContractError("BZ_REAL_LATTICE_ILL_CONDITIONED", "The real-space lattice is ill-conditioned.")
    return matrix


def _validated_matrix(value: Any, code: str) -> list[list[float]]:
    if not isinstance(value, (list, tuple)) or len(value) != 3:
        raise BrillouinContractError(code, "A 3x3 matrix is required.")
    rows = [_validated_vector(row, code) for row in value]
    return rows


def _validated_vector(value: Any, code: str) -> list[float]:
    if not isinstance(value, (list, tuple)) or len(value) != 3 or any(not _finite(item) for item in value):
        raise BrillouinContractError(code, "A finite vector is required.")
    return [float(item) for item in value]


def _inverse_checked(matrix: list[list[float]], code: str) -> list[list[float]]:
    determinant = _determinant(matrix)
    scale = max(_norm(row) for row in matrix)
    if scale == 0 or abs(determinant) <= 1e-12 * scale**3:
        raise BrillouinContractError(code, "The matrix is singular.")
    inverse = _inverse(matrix, determinant)
    condition = _frobenius(matrix) * _frobenius(inverse)
    if not math.isfinite(condition) or condition > 1e8:
        raise BrillouinContractError(code, "The matrix is ill-conditioned.")
    return inverse


def _inverse(matrix: list[list[float]], determinant: float) -> list[list[float]]:
    (a, b, c), (d, e, f), (g, h, i) = matrix
    return [
        [(e * i - f * h) / determinant, (c * h - b * i) / determinant, (b * f - c * e) / determinant],
        [(f * g - d * i) / determinant, (a * i - c * g) / determinant, (c * d - a * f) / determinant],
        [(d * h - e * g) / determinant, (b * g - a * h) / determinant, (a * e - b * d) / determinant],
    ]


def _determinant(matrix: Sequence[Sequence[float]]) -> float:
    (a, b, c), (d, e, f), (g, h, i) = matrix
    return a * (e * i - f * h) - b * (d * i - f * g) + c * (d * h - e * g)


def _transpose(matrix: Sequence[Sequence[float]]) -> list[list[float]]:
    return [[float(matrix[column][row]) for column in range(3)] for row in range(3)]


def _matrix_multiply(left: Sequence[Sequence[float]], right: Sequence[Sequence[float]]) -> list[list[float]]:
    return [[sum(float(left[row][index]) * float(right[index][column]) for index in range(3)) for column in range(3)] for row in range(3)]


def _vector_matrix(vector: Sequence[float], matrix: Sequence[Sequence[float]]) -> list[float]:
    return [sum(float(vector[row]) * float(matrix[row][column]) for row in range(3)) for column in range(3)]


def _identity_matrix() -> list[list[float]]:
    return [[1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]]


def _canonical_matrix(value: Sequence[Sequence[float]]) -> list[list[float]]:
    return [_canonical_vector(row) for row in value]


def _canonical_vector(value: Sequence[float]) -> list[float]:
    return [_canonical_number(item) for item in value]


def _canonical_number(value: float) -> float:
    number = round(float(value), 12)
    return 0.0 if abs(number) < 5e-13 else number


def _norm(value: Sequence[float]) -> float:
    return math.sqrt(sum(float(component) ** 2 for component in value))


def _normalize(value: Sequence[float], code: str) -> list[float]:
    length = _norm(value)
    if not math.isfinite(length) or length <= 1e-15:
        raise BrillouinContractError(code, "A nonzero vector is required.")
    return [float(component) / length for component in value]


def _frobenius(matrix: Sequence[Sequence[float]]) -> float:
    return math.sqrt(sum(float(value) ** 2 for row in matrix for value in row))


def _dot(left: Sequence[float], right: Sequence[float]) -> float:
    return sum(float(left[index]) * float(right[index]) for index in range(3))


def _cross(left: Sequence[float], right: Sequence[float]) -> list[float]:
    return [left[1] * right[2] - left[2] * right[1], left[2] * right[0] - left[0] * right[2], left[0] * right[1] - left[1] * right[0]]


def _subtract(left: Sequence[float], right: Sequence[float]) -> list[float]:
    return [float(left[index]) - float(right[index]) for index in range(3)]


def _distance(left: Sequence[float], right: Sequence[float]) -> float:
    return _norm(_subtract(left, right))


def _newell(points: Sequence[Sequence[float]]) -> list[float]:
    normal = [0.0, 0.0, 0.0]
    for index, current in enumerate(points):
        following = points[(index + 1) % len(points)]
        normal[0] += (current[1] - following[1]) * (current[2] + following[2])
        normal[1] += (current[2] - following[2]) * (current[0] + following[0])
        normal[2] += (current[0] - following[0]) * (current[1] + following[1])
    return normal


def _polygon_area_centroid(points: Sequence[Sequence[float]]) -> tuple[float, list[float]]:
    origin = points[0]
    area = 0.0
    weighted = [0.0, 0.0, 0.0]
    for index in range(1, len(points) - 1):
        triangle_area = _norm(_cross(_subtract(points[index], origin), _subtract(points[index + 1], origin))) / 2
        centroid = [(origin[axis] + points[index][axis] + points[index + 1][axis]) / 3 for axis in range(3)]
        area += triangle_area
        for axis in range(3):
            weighted[axis] += triangle_area * centroid[axis]
    if area <= 1e-15:
        raise BrillouinContractError("BZ_FACE_INVALID", "A face has zero area.")
    return area, [value / area for value in weighted]


def _polyhedron_volume(
    faces: Sequence[dict[str, Any]],
    coordinates: Sequence[Sequence[float]] | dict[str, Sequence[float]],
) -> float:
    volume = 0.0
    for face in faces:
        if isinstance(coordinates, dict):
            points = [coordinates[identifier] for identifier in face["vertex_ids"]]
        else:
            points = [coordinates[int(identifier[1:])] for identifier in face["vertex_ids"]]
        origin = points[0]
        for index in range(1, len(points) - 1):
            volume += _dot(origin, _cross(points[index], points[index + 1])) / 6.0
    return abs(volume)


def _edge_key(left: str, right: str) -> tuple[str, str]:
    return (left, right) if left < right else (right, left)


def _rotate_to_minimum(values: list[str]) -> list[str]:
    if not values:
        return values
    index = min(range(len(values)), key=lambda position: values[position])
    return values[index:] + values[:index]


def _finite(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(float(value)) and abs(float(value)) <= BRILLOUIN_CAPS["max_numeric_magnitude"]


def _sha(value: Any) -> bool:
    return isinstance(value, str) and _SHA256.fullmatch(value) is not None


def _validated_sha(value: Any, code: str) -> str:
    if not _sha(value):
        raise BrillouinContractError(code, "A sha256 identity is required.")
    return value


def _safe_text(value: Any, code: str) -> str:
    if not _valid_safe_text(value, 128):
        raise BrillouinContractError(code, "Plain text is required.")
    return value


def _safe_label(value: Any) -> str:
    if not _valid_safe_text(value, BRILLOUIN_CAPS["max_label_length"]):
        raise BrillouinContractError("BZ_LABEL_INVALID", "The label is invalid.")
    return value


def _validated_label_key(value: Any) -> str:
    if not isinstance(value, str) or _LABEL_KEY.fullmatch(value) is None:
        raise BrillouinContractError("BZ_LABEL_INVALID", "The label key is invalid.")
    return value


def _valid_safe_text(value: Any, limit: int) -> bool:
    if not isinstance(value, str) or not 0 < len(value) <= limit or _SAFE_TEXT.fullmatch(value) is None:
        return False
    lowered = value.lower()
    return not any(marker in lowered for marker in _FORBIDDEN_MARKERS) and not any(pattern.match(value) for pattern in _PRIVATE_PATH)


def _integer_triplet(value: Any, bound: int) -> bool:
    return isinstance(value, list) and len(value) == 3 and all(isinstance(item, int) and not isinstance(item, bool) and abs(item) <= bound for item in value)


def _near_vector(left: Any, right: Any, tolerance: float) -> bool:
    return isinstance(left, (list, tuple)) and isinstance(right, (list, tuple)) and len(left) == len(right) == 3 and all(_finite(item) for item in list(left) + list(right)) and all(abs(float(left[index]) - float(right[index])) <= tolerance for index in range(3))


def _near_matrix(left: Any, right: Any, tolerance: float) -> bool:
    return isinstance(left, (list, tuple)) and isinstance(right, (list, tuple)) and len(left) == len(right) == 3 and all(_near_vector(left[index], right[index], tolerance) for index in range(3))


def _number_near(left: Any, right: Any, tolerance: float) -> bool:
    return _finite(left) and _finite(right) and abs(float(left) - float(right)) <= tolerance


def _relative_near(left: float, right: float, tolerance: float) -> bool:
    return math.isfinite(left) and math.isfinite(right) and abs(left - right) <= max(1e-12, tolerance * max(abs(left), abs(right), 1.0))


def _security_copy() -> dict[str, Any]:
    return {key: list(value) if isinstance(value, list) else value for key, value in BRILLOUIN_SECURITY.items()}


def _scan_inert(value: Any, errors: set[str]) -> None:
    stack: list[tuple[Any, int]] = [(value, 0)]
    nodes = 0
    while stack:
        current, depth = stack.pop()
        nodes += 1
        if nodes > BRILLOUIN_CAPS["max_scan_nodes"] or depth > BRILLOUIN_CAPS["max_scan_depth"]:
            errors.add("BZ_PAYLOAD_TOO_LARGE")
            return
        if isinstance(current, dict):
            for key, child in current.items():
                if str(key).lower() in _FORBIDDEN_KEYS:
                    errors.add("BZ_EXECUTABLE_CONTENT_FORBIDDEN")
                stack.append((child, depth + 1))
        elif isinstance(current, list):
            stack.extend((child, depth + 1) for child in current)
        elif isinstance(current, str):
            lowered = current.lower()
            if any(marker in lowered for marker in _FORBIDDEN_MARKERS) or any(pattern.match(current) for pattern in _PRIVATE_PATH):
                errors.add("BZ_EXTERNAL_OR_EXECUTABLE_CONTENT_FORBIDDEN")


def _result(
    errors: Iterable[str], warnings: Iterable[str], counts: dict[str, int]
) -> BrillouinValidationResult:
    return BrillouinValidationResult(
        valid=not tuple(errors),
        errors=tuple(sorted(set(errors))),
        warnings=tuple(sorted(set(warnings))),
        counts=dict(counts),
        caps=dict(BRILLOUIN_CAPS),
    )
