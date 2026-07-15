from __future__ import annotations

import copy
import hashlib
import json
import math
from pathlib import Path

import numpy as np
import pytest
from scipy.spatial import ConvexHull

from mdi_artifact_core import (
    BRILLOUIN_CAPS,
    BRILLOUIN_SECURITY,
    BRILLOUIN_TOLERANCES,
    BRILLOUIN_ZONE_MANIFEST_SCHEMA_VERSION,
    BRILLOUIN_ZONE_SCHEMA_VERSION,
    KPATH_SCHEMA_VERSION,
    RECIPROCAL_LATTICE_SCHEMA_VERSION,
    BrillouinContractError,
    brillouin_content_hash,
    brillouin_schema_snapshots,
    build_basis_transformation,
    build_kpath_contract,
    build_reciprocal_lattice_contract,
    bz_reciprocal_fractional_to_cartesian,
    canonicalize_brillouin_zone,
    lattice_content_hash,
    reciprocal_cartesian_to_fractional,
    stable_brillouin_json,
    validate_brillouin_zone,
    validate_brillouin_zone_manifest,
    validate_kpath,
    validate_phonon_kpath_compatibility,
    validate_reciprocal_lattice,
)
from mdi_tool_registry import load_manifests


ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "docs" / "phase10i" / "fixtures" / "brillouin_zone_v1"
PHONON_FIXTURES = ROOT / "docs" / "phase10h" / "fixtures" / "phonon_contract"
FIXTURE_NAMES = (
    "simple_cubic",
    "bcc",
    "fcc",
    "hexagonal",
    "triclinic",
    "conventional_bcc",
)


def _load(name: str, artifact: str) -> dict[str, object]:
    return json.loads((FIXTURES / name / f"{artifact}.json").read_text(encoding="utf-8"))


def _structure_hash(name: str) -> str:
    return hashlib.sha256(f"phase10i:{name}".encode()).hexdigest()


def _provider(source_hash: str) -> dict[str, object]:
    return {
        "name": "internal_fixture_reference",
        "version": "1",
        "convention": "internal_fixture_reference",
        "symprec_angstrom": 1e-5,
        "angle_tolerance_degrees": 5.0,
        "time_reversal_used": True,
        "standardization_status": "validated_fixture",
        "warnings": [],
        "input_structure_sha256": source_hash,
    }


def _raw_faces(zone: dict[str, object]) -> list[dict[str, object]]:
    vertices = {
        vertex["vertex_id"]: vertex["cartesian_coordinates"]
        for vertex in zone["vertices"]
    }
    return [
        {
            "generator_hkl": face["generator_hkl"],
            "vertices": [vertices[vertex_id] for vertex_id in face["vertex_ids"]],
        }
        for face in zone["faces"]
    ]


def _phonon_band_for(reciprocal: dict[str, object], kpath: dict[str, object]) -> dict[str, object]:
    source = json.loads((PHONON_FIXTURES / "stable_band.json").read_text(encoding="utf-8"))
    selected = next(variant for variant in kpath["path_variants"] if variant["selected"])
    segment = next(item for item in kpath["segments"] if item["segment_id"] == selected["segment_ids"][0])
    points = {point["point_id"]: point for point in kpath["points"]}
    start = points[segment["start_point_id"]]
    end = points[segment["end_point_id"]]
    source["structure_identity"] = reciprocal["real_lattice_binding"]["source_structure_sha256"]
    source["real_space_lattice_angstrom"] = reciprocal["real_lattice_binding"]["primitive_real_lattice"]
    source["qpoints"] = [
        {
            "index": 0,
            "coordinates": start["fractional_coordinates"],
            "label": start["display_label"],
            "source_label": start["label_key"],
            "segment_index": 0,
            "distance": 0.0,
        },
        {
            "index": 1,
            "coordinates": end["fractional_coordinates"],
            "label": end["display_label"],
            "source_label": end["label_key"],
            "segment_index": 0,
            "distance": segment["length"],
        },
    ]
    source["segments"] = [
        {
            "segment_index": 0,
            "start_qpoint_index": 0,
            "end_qpoint_index": 1,
            "start_label": start["display_label"],
            "end_label": end["display_label"],
            "discontinuous_from_previous": False,
        }
    ]
    for branch in source["branches"]:
        branch["frequencies"] = branch["frequencies"][:2]
    source["degeneracy_groups"] = []
    return source


def test_schema_family_caps_security_and_registration_boundary() -> None:
    snapshots = brillouin_schema_snapshots()
    assert snapshots["versions"] == {
        "reciprocal_lattice": RECIPROCAL_LATTICE_SCHEMA_VERSION,
        "brillouin_zone": BRILLOUIN_ZONE_SCHEMA_VERSION,
        "kpath": KPATH_SCHEMA_VERSION,
        "manifest": BRILLOUIN_ZONE_MANIFEST_SCHEMA_VERSION,
        "tolerances": "phase10i.tolerance_policy.v1",
    }
    assert snapshots["convention"] == {
        "real_lattice": "row_vectors",
        "real_cartesian": "r_cart=r_frac*A",
        "reciprocal_lattice": "B=2*pi*A^-T",
        "reciprocal_cartesian": "k_cart=k_frac*B",
        "duality": "A*B^T=2*pi*I",
        "units": "angstrom^-1",
    }
    assert snapshots["tool_registration"] == "REGISTERED_DATA_ADAPTER"
    assert snapshots["renderer"] == "NOT_INCLUDED"
    assert BRILLOUIN_CAPS["max_vertices"] == 256
    assert BRILLOUIN_CAPS["max_edges"] == 512
    assert BRILLOUIN_CAPS["max_faces"] == 256
    assert len(set(BRILLOUIN_TOLERANCES.values())) > 5
    assert BRILLOUIN_SECURITY["renderer_included"] is False
    assert BRILLOUIN_SECURITY["external_urls"] == []
    tool_ids = {tool.toolId for tool in load_manifests().list_tools()}
    assert "structure.brillouin_zone" in tool_ids
    assert "structure.kpath" not in tool_ids


@pytest.mark.parametrize("name", FIXTURE_NAMES)
def test_fixture_family_validates_and_replays_byte_identically(name: str) -> None:
    reciprocal = _load(name, "reciprocal_lattice")
    zone = _load(name, "brillouin_zone")
    kpath_path = FIXTURES / name / "kpath.json"
    kpath = json.loads(kpath_path.read_text(encoding="utf-8")) if kpath_path.exists() else None
    manifest = _load(name, "manifest")

    assert validate_reciprocal_lattice(reciprocal).valid
    assert validate_brillouin_zone(zone, reciprocal).valid
    if kpath is not None:
        assert validate_kpath(kpath, reciprocal).valid
    assert validate_brillouin_zone_manifest(manifest, reciprocal, zone, kpath).valid
    for payload in (reciprocal, zone, manifest, *(() if kpath is None else (kpath,))):
        assert payload["content_hash"] == brillouin_content_hash(payload)
        assert stable_brillouin_json(json.loads(stable_brillouin_json(payload))) == stable_brillouin_json(payload)


@pytest.mark.parametrize(
    "lattice",
    (
        [[4.0, 0.0, 0.0], [0.0, 4.0, 0.0], [0.0, 0.0, 4.0]],
        [[3.0, 0.0, 0.0], [0.0, 4.0, 0.0], [0.0, 0.0, 5.0]],
        [[4.1, 0.0, 0.0], [0.7, 3.8, 0.0], [0.0, 0.0, 5.2]],
        [[4.1, 0.0, 0.0], [1.2, 3.8, 0.0], [0.4, 0.7, 5.2]],
    ),
    ids=("cubic", "orthorhombic", "monoclinic", "triclinic"),
)
def test_reciprocal_duality_volume_and_coordinate_round_trip(lattice: list[list[float]]) -> None:
    source_hash = hashlib.sha256(stable_brillouin_json(lattice).encode()).hexdigest()
    reciprocal = build_reciprocal_lattice_contract(
        source_structure_id="fixture:math",
        source_structure_sha256=source_hash,
        source_real_lattice=lattice,
        primitive_real_lattice=lattice,
    )
    a = np.asarray(lattice)
    b = np.asarray(reciprocal["matrix"])
    expected = 2.0 * np.pi * np.linalg.inv(a).T
    assert np.allclose(b, expected, rtol=1e-11, atol=1e-11)
    assert np.allclose(a @ b.T, 2.0 * np.pi * np.eye(3), rtol=1e-11, atol=1e-11)
    assert math.isclose(abs(np.linalg.det(b)), (2.0 * np.pi) ** 3 / abs(np.linalg.det(a)), rel_tol=1e-11)
    fractional = [0.137, -0.271, 0.419]
    cartesian = bz_reciprocal_fractional_to_cartesian(fractional, reciprocal["matrix"])
    assert np.allclose(cartesian, np.asarray(fractional) @ b, atol=1e-11)
    assert np.allclose(reciprocal_cartesian_to_fractional(cartesian, reciprocal["matrix"]), fractional, atol=1e-11)


def test_non_gamma_phase_uses_exactly_one_physics_2pi_factor() -> None:
    reciprocal = _load("triclinic", "reciprocal_lattice")
    a = np.asarray(reciprocal["real_lattice_binding"]["primitive_real_lattice"])
    b = np.asarray(reciprocal["matrix"])
    q_fractional = np.asarray([0.17, 0.31, -0.23])
    image = np.asarray([2, -1, 3])
    q_cartesian = q_fractional @ b
    translation = image @ a
    assert math.isclose(float(q_cartesian @ translation), 2.0 * math.pi * float(q_fractional @ image), rel_tol=1e-11, abs_tol=1e-11)


def test_lattice_singularity_condition_and_non_finite_values_are_rejected() -> None:
    base = dict(
        source_structure_id="fixture:invalid",
        source_structure_sha256="a" * 64,
    )
    with pytest.raises(BrillouinContractError, match="singular") as singular:
        build_reciprocal_lattice_contract(
            **base,
            source_real_lattice=[[1, 0, 0], [0, 1, 0], [0, 0, 0]],
            primitive_real_lattice=[[1, 0, 0], [0, 1, 0], [0, 0, 0]],
        )
    assert singular.value.code == "BZ_REAL_LATTICE_SINGULAR"
    ill_conditioned = [[1, 0, 0], [0, 1, 0], [0, 0, 1e-8]]
    with pytest.raises(BrillouinContractError) as condition:
        build_reciprocal_lattice_contract(
            **base,
            source_real_lattice=ill_conditioned,
            primitive_real_lattice=ill_conditioned,
        )
    assert condition.value.code == "BZ_REAL_LATTICE_ILL_CONDITIONED"
    with pytest.raises(BrillouinContractError) as non_finite:
        build_reciprocal_lattice_contract(
            **base,
            source_real_lattice=[[1, 0, 0], [0, math.inf, 0], [0, 0, 1]],
            primitive_real_lattice=[[1, 0, 0], [0, 1, 0], [0, 0, 1]],
        )
    assert non_finite.value.code == "BZ_REAL_LATTICE_SHAPE_INVALID"


def test_source_to_primitive_basis_transformation_direction_and_round_trip() -> None:
    reciprocal = _load("conventional_bcc", "reciprocal_lattice")
    transform = reciprocal["transformations"][0]
    m = np.asarray(transform["matrix"])
    a_old = np.asarray(reciprocal["real_lattice_binding"]["source_real_lattice"])
    a_new = np.asarray(reciprocal["real_lattice_binding"]["primitive_real_lattice"])
    b_old = 2.0 * np.pi * np.linalg.inv(a_old).T
    b_new = np.asarray(reciprocal["matrix"])
    assert np.allclose(m @ a_old, a_new, atol=1e-12)
    assert np.allclose(np.linalg.inv(m).T @ b_old, b_new, atol=1e-11)
    real_old = np.asarray([0.19, 0.31, 0.47])
    real_new = real_old @ np.linalg.inv(m)
    assert np.allclose(real_old @ a_old, real_new @ a_new, atol=1e-12)
    k_old = np.asarray([0.17, -0.23, 0.41])
    k_new = k_old @ m.T
    assert np.allclose(k_old @ b_old, k_new @ b_new, atol=1e-11)
    assert transform == build_basis_transformation(
        transform["matrix"], old_basis="source_cell", new_basis="standardized_primitive_cell"
    )
    primitive_zone = _load("bcc", "brillouin_zone")
    conventional_zone = _load("conventional_bcc", "brillouin_zone")
    for field in ("vertices", "edges", "faces", "volume", "surface_area", "topology"):
        assert conventional_zone[field] == primitive_zone[field]


@pytest.mark.parametrize("c_axis", (4.2, 7.4))
def test_hexagonal_c_over_a_variation_preserves_contract_identity_policy(c_axis: float) -> None:
    lattice = [[3.0, 0.0, 0.0], [-1.5, 3.0 * math.sqrt(3.0) / 2.0, 0.0], [0.0, 0.0, c_axis]]
    source_hash = hashlib.sha256(stable_brillouin_json(lattice).encode()).hexdigest()
    reciprocal = build_reciprocal_lattice_contract(
        source_structure_id=f"fixture:hexagonal:{c_axis}",
        source_structure_sha256=source_hash,
        source_real_lattice=lattice,
        primitive_real_lattice=lattice,
    )
    kpath = build_kpath_contract(
        reciprocal,
        point_specs=[
            {"label_key": "GAMMA", "display_label": "Γ", "aliases": ["G"], "fractional_coordinates": [0, 0, 0]},
            {"label_key": "M", "display_label": "M", "aliases": [], "fractional_coordinates": [0.5, 0, 0]},
            {"label_key": "K", "display_label": "K", "aliases": [], "fractional_coordinates": [1 / 3, 1 / 3, 0]},
            {"label_key": "A", "display_label": "A", "aliases": [], "fractional_coordinates": [0, 0, 0.5]},
            {"label_key": "L", "display_label": "L", "aliases": [], "fractional_coordinates": [0.5, 0, 0.5]},
            {"label_key": "H", "display_label": "H", "aliases": [], "fractional_coordinates": [1 / 3, 1 / 3, 0.5]},
        ],
        variant_specs=[
            {
                "variant_key": "primary",
                "description": "Hexagonal reference",
                "branches": [["GAMMA", "M", "K", "GAMMA", "A", "L", "H", "A"]],
            }
        ],
        selected_variant_key="primary",
        provider=_provider(source_hash),
        path_convention="internal_fixture_reference",
        time_reversal_used=True,
    )
    assert validate_reciprocal_lattice(reciprocal).valid
    assert validate_kpath(kpath, reciprocal).valid
    assert {point["label_key"] for point in kpath["points"]} == {"GAMMA", "M", "K", "A", "L", "H"}


@pytest.mark.parametrize(
    ("name", "expected"),
    (
        ("simple_cubic", (8, 12, 6)),
        ("bcc", (14, 24, 12)),
        ("fcc", (24, 36, 14)),
        ("hexagonal", (12, 18, 8)),
        ("triclinic", (24, 36, 14)),
    ),
)
def test_polyhedron_topology_planes_convexity_volume_and_central_symmetry(
    name: str, expected: tuple[int, int, int]
) -> None:
    reciprocal = _load(name, "reciprocal_lattice")
    zone = _load(name, "brillouin_zone")
    topology = zone["topology"]
    assert (topology["vertex_count"], topology["edge_count"], topology["face_count"]) == expected
    assert topology["euler_characteristic"] == expected[0] - expected[1] + expected[2] == 2
    assert all(topology[key] for key in ("closed", "convex", "manifold", "connected", "centrally_symmetric"))
    vertices = {vertex["vertex_id"]: np.asarray(vertex["cartesian_coordinates"]) for vertex in zone["vertices"]}
    all_coordinates = np.asarray(list(vertices.values()))
    for face in zone["faces"]:
        generator = np.asarray(face["generator_cartesian"])
        normal = np.asarray(face["outward_normal"])
        points = [vertices[vertex_id] for vertex_id in face["vertex_ids"]]
        assert np.allclose(normal, generator / np.linalg.norm(generator), atol=1e-10)
        assert all(math.isclose(float(point @ generator), float(generator @ generator) / 2.0, abs_tol=1e-8) for point in points)
        assert np.all(all_coordinates @ generator <= float(generator @ generator) / 2.0 + 1e-8)
        newell = sum((np.cross(points[index], points[(index + 1) % len(points)]) for index in range(len(points))), np.zeros(3))
        assert float(newell @ normal) > 0
    for coordinate in all_coordinates:
        assert any(np.allclose(-coordinate, candidate, atol=1e-8) for candidate in all_coordinates)
    independent_volume = ConvexHull(all_coordinates).volume
    assert math.isclose(independent_volume, zone["volume"], rel_tol=1e-8)
    assert math.isclose(zone["volume"], abs(np.linalg.det(np.asarray(reciprocal["matrix"]))), rel_tol=1e-8)
    assert all(len(edge["incident_face_ids"]) == 2 for edge in zone["edges"])


def test_bcc_fcc_reciprocal_duality_reference_is_not_swapped() -> None:
    bcc = _load("bcc", "brillouin_zone")["topology"]
    fcc = _load("fcc", "brillouin_zone")["topology"]
    assert (bcc["vertex_count"], bcc["edge_count"], bcc["face_count"]) == (14, 24, 12)
    assert (fcc["vertex_count"], fcc["edge_count"], fcc["face_count"]) == (24, 36, 14)


def test_polyhedron_canonicalization_is_input_order_independent() -> None:
    reciprocal = _load("simple_cubic", "reciprocal_lattice")
    zone = _load("simple_cubic", "brillouin_zone")
    faces = _raw_faces(zone)
    for face in faces:
        face["vertices"] = list(reversed(face["vertices"]))
    replay = canonicalize_brillouin_zone(
        reciprocal,
        list(reversed(faces)),
        provider_method="pymatgen_lattice_wigner_seitz_fixture_only",
    )
    assert stable_brillouin_json(replay) == stable_brillouin_json(zone)


@pytest.mark.parametrize(
    ("mutation", "error"),
    (
        (
            lambda value: value["vertices"][1].__setitem__(
                "cartesian_coordinates", copy.deepcopy(value["vertices"][0]["cartesian_coordinates"])
            ),
            "BZ_DUPLICATE_VERTEX",
        ),
        (lambda value: value["faces"].pop(), "BZ_NON_MANIFOLD_POLYHEDRON"),
        (lambda value: value["faces"][0].__setitem__("outward_normal", [1.0, 0.0, 0.0]), "BZ_FACE_WINDING_INVALID"),
        (lambda value: value["topology"].__setitem__("euler_characteristic", 1), "BZ_TOPOLOGY_INVALID"),
    ),
)
def test_polyhedron_tampering_is_rejected(mutation, error: str) -> None:
    reciprocal = _load("simple_cubic", "reciprocal_lattice")
    zone = _load("simple_cubic", "brillouin_zone")
    mutation(zone)
    zone["content_hash"] = brillouin_content_hash(zone)
    result = validate_brillouin_zone(zone, reciprocal)
    assert not result.valid
    assert error in result.errors


def test_kpath_points_aliases_variants_discontinuities_and_distances() -> None:
    reciprocal = _load("simple_cubic", "reciprocal_lattice")
    kpath = _load("simple_cubic", "kpath")
    result = validate_kpath(kpath, reciprocal)
    assert result.valid, result.as_dict()
    assert result.counts == {"points": 4, "variants": 1, "segments": 6, "discontinuities": 1}
    assert next(point for point in kpath["points"] if point["label_key"] == "GAMMA")["aliases"] == ["G"]
    selected = next(variant for variant in kpath["path_variants"] if variant["selected"])
    segments = {segment["segment_id"]: segment for segment in kpath["segments"]}
    ordered = [segments[segment_id] for segment_id in selected["segment_ids"]]
    for index, segment in enumerate(ordered):
        assert segment["order_index"] == index
        assert math.isclose(segment["distance_end"] - segment["distance_start"], segment["length"], abs_tol=1e-9)
        if index:
            assert math.isclose(segment["distance_start"], ordered[index - 1]["distance_end"], abs_tol=1e-9)
    assert sum(segment["discontinuity_before"] for segment in ordered) == 1
    assert sum(segment["discontinuity_after"] for segment in ordered) == 1
    assert kpath["time_reversal_used"] is True
    assert kpath["provider"]["name"] == "internal_fixture_reference"


def test_kpath_builder_merges_coincident_labels_and_supports_multiple_variants() -> None:
    reciprocal = _load("simple_cubic", "reciprocal_lattice")
    points = [
        {"label_key": "GAMMA", "display_label": "Γ", "aliases": ["G"], "fractional_coordinates": [0, 0, 0]},
        {"label_key": "G", "display_label": "G", "aliases": [], "fractional_coordinates": [0, 0, 0]},
        {"label_key": "X", "display_label": "X", "aliases": [], "fractional_coordinates": [0, 0.5, 0]},
        {"label_key": "M", "display_label": "M", "aliases": [], "fractional_coordinates": [0.5, 0.5, 0]},
    ]
    variants = [
        {"variant_key": "primary", "description": "Primary", "branches": [["GAMMA", "X", "M"]]},
        {"variant_key": "alternate", "description": "Alternate", "branches": [["G", "M"]]},
    ]
    kpath = build_kpath_contract(
        reciprocal,
        point_specs=points,
        variant_specs=variants,
        selected_variant_key="primary",
        provider=_provider(reciprocal["real_lattice_binding"]["source_structure_sha256"]),
        path_convention="internal_fixture_reference",
        time_reversal_used=True,
    )
    assert validate_kpath(kpath, reciprocal).valid
    assert len(kpath["points"]) == 3
    gamma = next(point for point in kpath["points"] if point["label_key"] == "GAMMA")
    assert gamma["metadata"]["coincident_labels_merged"] is True
    assert gamma["provider_identity"]["source_label_keys"] == ["G", "GAMMA"]
    assert len(kpath["path_variants"]) == 2
    assert sum(variant["selected"] for variant in kpath["path_variants"]) == 1


@pytest.mark.parametrize(
    ("artifact", "mutation", "error"),
    (
        ("kpath", lambda value: value["points"][0].__setitem__("display_label", "<script>alert(1)</script>"), "BZ_LABEL_INVALID"),
        ("kpath", lambda value: value["points"][0].__setitem__("display_label", "https://example.invalid"), "BZ_EXTERNAL_OR_EXECUTABLE_CONTENT_FORBIDDEN"),
        ("kpath", lambda value: value["points"][0].__setitem__("display_label", "X" * 65), "BZ_LABEL_INVALID"),
        ("kpath", lambda value: value["points"][0]["metadata"].__setitem__("callback", "run"), "BZ_EXECUTABLE_CONTENT_FORBIDDEN"),
        ("kpath", lambda value: value["points"][0].__setitem__("fractional_coordinates", [math.nan, 0, 0]), "BZ_HIGH_SYMMETRY_POINT_INVALID"),
        ("zone", lambda value: value.__setitem__("shader", "void main(){}"), "BZ_EXECUTABLE_CONTENT_FORBIDDEN"),
    ),
)
def test_inert_security_and_label_validation(artifact: str, mutation, error: str) -> None:
    reciprocal = _load("simple_cubic", "reciprocal_lattice")
    value = _load("simple_cubic", "kpath" if artifact == "kpath" else "brillouin_zone")
    mutation(value)
    try:
        value["content_hash"] = brillouin_content_hash(value)
    except ValueError:
        pass
    result = validate_kpath(value, reciprocal) if artifact == "kpath" else validate_brillouin_zone(value, reciprocal)
    assert not result.valid
    assert error in result.errors


def test_payload_caps_content_hash_and_manifest_capability_are_enforced() -> None:
    reciprocal = _load("simple_cubic", "reciprocal_lattice")
    kpath = _load("simple_cubic", "kpath")
    assert "BZ_PAYLOAD_TOO_LARGE" in validate_kpath(
        kpath, reciprocal, raw_size_bytes=BRILLOUIN_CAPS["max_json_bytes"] + 1
    ).errors
    kpath["content_hash"] = "0" * 64
    assert "BZ_CONTENT_HASH_MISMATCH" in validate_kpath(kpath, reciprocal).errors
    manifest = _load("simple_cubic", "manifest")
    manifest["capabilities"]["renderer_included"] = True
    manifest["content_hash"] = brillouin_content_hash(manifest)
    assert "BZ_MANIFEST_CAPABILITY_INVALID" in validate_brillouin_zone_manifest(
        manifest,
        reciprocal,
        _load("simple_cubic", "brillouin_zone"),
        _load("simple_cubic", "kpath"),
    ).errors


def test_validators_return_typed_errors_for_malformed_types_without_raising() -> None:
    reciprocal = _load("simple_cubic", "reciprocal_lattice")
    kpath = _load("simple_cubic", "kpath")
    kpath["segments"][0]["distance_start"] = "not-a-number"
    kpath["content_hash"] = brillouin_content_hash(kpath)
    result = validate_kpath(kpath, reciprocal)
    assert not result.valid
    assert "BZ_PATH_DISTANCE_INVALID" in result.errors

    zone = _load("simple_cubic", "brillouin_zone")
    zone["faces"][0]["generator_hkl"] = "not-an-offset"
    zone["content_hash"] = brillouin_content_hash(zone)
    zone_result = validate_brillouin_zone(zone, reciprocal)
    assert not zone_result.valid
    assert "BZ_FACE_GENERATOR_INVALID" in zone_result.errors

    manifest = _load("simple_cubic", "manifest")
    manifest_result = validate_brillouin_zone_manifest(
        manifest,
        reciprocal_lattice="not-an-artifact",
        zone=["not-an-artifact"],
        kpath="not-an-artifact",
    )
    assert not manifest_result.valid
    assert "BZ_MANIFEST_INVALID" in manifest_result.errors

    malformed_band = _phonon_band_for(reciprocal, _load("simple_cubic", "kpath"))
    malformed_band["segments"] = ["not-a-segment"]
    compatibility = validate_phonon_kpath_compatibility(
        malformed_band,
        reciprocal,
        _load("simple_cubic", "kpath"),
    )
    assert not compatibility.compatible
    assert "BZ_PHONON_BAND_INVALID" in compatibility.errors


def test_phonon_kpath_compatibility_and_mismatch_classification() -> None:
    primitive = [[5.43, 0.0, 0.0], [0.0, 5.43, 0.0], [0.0, 0.0, 5.43]]
    source_hash = "a" * 64
    reciprocal = build_reciprocal_lattice_contract(
        source_structure_id="fixture:phonon",
        source_structure_sha256=source_hash,
        source_real_lattice=primitive,
        primitive_real_lattice=primitive,
    )
    kpath = build_kpath_contract(
        reciprocal,
        point_specs=[
            {"label_key": "GAMMA", "display_label": "Γ", "aliases": ["G"], "fractional_coordinates": [0, 0, 0]},
            {"label_key": "L", "display_label": "L", "aliases": [], "fractional_coordinates": [0.5, 0.5, 0.5]},
        ],
        variant_specs=[{"variant_key": "primary", "description": "Gamma to L", "branches": [["GAMMA", "L"]]}],
        selected_variant_key="primary",
        provider=_provider(source_hash),
        path_convention="internal_fixture_reference",
        time_reversal_used=True,
    )
    band = _phonon_band_for(reciprocal, kpath)
    result = validate_phonon_kpath_compatibility(band, reciprocal, kpath)
    assert result.compatible, result.as_dict()
    assert "BZ_PHONON_TIME_REVERSAL_UNDECLARED" in result.warnings

    bad_structure = copy.deepcopy(band)
    bad_structure["structure_identity"] = "b" * 64
    assert "BZ_PHONON_STRUCTURE_MISMATCH" in validate_phonon_kpath_compatibility(
        bad_structure, reciprocal, kpath
    ).errors
    bad_convention = copy.deepcopy(band)
    bad_convention["reciprocal_convention"] = "crystallographic_no_2pi"
    assert "BZ_PHONON_CONVENTION_MISMATCH" in validate_phonon_kpath_compatibility(
        bad_convention, reciprocal, kpath
    ).errors
    bad_path = copy.deepcopy(band)
    bad_path["qpoints"][-1]["coordinates"] = [0.25, 0.25, 0.25]
    assert "BZ_PHONON_PATH_MISMATCH" in validate_phonon_kpath_compatibility(
        bad_path, reciprocal, kpath
    ).errors


def test_primitive_lattice_hash_is_basis_specific_and_stable() -> None:
    source = _load("conventional_bcc", "reciprocal_lattice")
    primitive = source["real_lattice_binding"]["primitive_real_lattice"]
    conventional = source["real_lattice_binding"]["source_real_lattice"]
    assert source["real_lattice_binding"]["primitive_lattice_sha256"] == lattice_content_hash(primitive)
    assert source["real_lattice_binding"]["source_lattice_sha256"] == lattice_content_hash(conventional)
    assert lattice_content_hash(primitive) != lattice_content_hash(conventional)
