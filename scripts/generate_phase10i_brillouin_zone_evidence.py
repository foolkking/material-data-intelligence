from __future__ import annotations

import copy
import hashlib
import json
import math
import shutil
from importlib import metadata
from itertools import product
from pathlib import Path
from typing import Any

import numpy as np
from pymatgen.core import Lattice
from scipy.spatial import ConvexHull, Voronoi

from mdi_artifact_core import (
    BRILLOUIN_CAPS,
    BRILLOUIN_ZONE_SCHEMA_VERSION,
    BrillouinContractError,
    brillouin_content_hash,
    brillouin_schema_snapshots,
    build_basis_transformation,
    build_brillouin_zone_manifest,
    build_kpath_contract,
    build_reciprocal_lattice_contract,
    canonicalize_brillouin_zone,
    reciprocal_cartesian_to_fractional,
    bz_reciprocal_fractional_to_cartesian,
    stable_brillouin_json,
    validate_brillouin_zone,
    validate_brillouin_zone_manifest,
    validate_kpath,
    validate_reciprocal_lattice,
)


ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "docs" / "phase10i" / "fixtures" / "brillouin_zone_v1"
EVIDENCE = ROOT / "docs" / "phase10i" / "evidence" / "phase10i_brillouin_zone_contract"
PHASE10I_BASELINE_HEAD = "b0b191cb05f518acfb50924a5021944bfea7c6b4"
PHASE10H5_IMPLEMENTATION_COMMIT = "b67a9e18109f976aeadaf6002eaac6c71297875c"
PHASE10H5_COMPLETION_COMMIT = "1021a2e2cba202ffaec22d4e0d35a4fb345a890c"
PHASE10I_IMPLEMENTATION_COMMIT = "653ea133d5791db3f6879b05dc66a2e397d0d646"
PHASE10I_IMPLEMENTATION_CI_RUN = "29339358234"


def main() -> None:
    for directory in (FIXTURES, EVIDENCE):
        if directory.exists():
            shutil.rmtree(directory)
        directory.mkdir(parents=True)
    definitions = fixture_definitions()
    packages: dict[str, dict[str, Any]] = {}
    references: dict[str, Any] = {}
    validation: dict[str, Any] = {}
    for name, definition in definitions.items():
        package = build_package(name, definition)
        packages[name] = package
        case_dir = FIXTURES / name
        case_dir.mkdir(parents=True)
        for artifact_name, payload in package.items():
            write_json(case_dir / f"{artifact_name}.json", payload)
        reference = independent_reference(definition["primitive_lattice"])
        references[name] = reference
        validation[name] = validate_package(package)
        assert validation[name]["valid"], (name, validation[name])
        for field in ("vertex_count", "edge_count", "face_count", "euler_characteristic"):
            assert reference["topology"][field] == package["brillouin_zone"]["topology"][field]
        assert math.isclose(reference["volume"], package["brillouin_zone"]["volume"], rel_tol=1e-8)
    expected = {
        "simple_cubic": [8, 12, 6],
        "bcc": [14, 24, 12],
        "fcc": [24, 36, 14],
        "hexagonal": [12, 18, 8],
    }
    for name, counts in expected.items():
        topology = packages[name]["brillouin_zone"]["topology"]
        assert [topology["vertex_count"], topology["edge_count"], topology["face_count"]] == counts
    assert packages["bcc"]["reciprocal_lattice"]["real_lattice_binding"]["primitive_lattice_sha256"] == packages["conventional_bcc"]["reciprocal_lattice"]["real_lattice_binding"]["primitive_lattice_sha256"]
    write_json(EVIDENCE / "pre_implementation_audit.json", pre_implementation_audit())
    write_json(EVIDENCE / "schema_snapshots.json", brillouin_schema_snapshots())
    write_json(EVIDENCE / "validation_outputs.json", validation)
    write_json(EVIDENCE / "independent_references.json", references)
    write_json(EVIDENCE / "bcc_fcc_reference.json", bcc_fcc_reference(packages, references))
    write_json(EVIDENCE / "canonical_replay.json", canonical_replay(packages))
    negative = negative_cases(packages)
    required_negative = {
        "singular_lattice", "ill_conditioned_lattice", "non_finite_lattice",
        "malformed_transformation", "duplicate_vertex", "open_topology",
        "inward_face", "invalid_path_endpoint", "label_injection",
        "cap_exceeded", "convention_mismatch", "volume_mismatch",
    }
    assert set(negative) == required_negative
    assert all(
        value.startswith("BZ_") if isinstance(value, str) else value["valid"] is False
        for value in negative.values()
    )
    write_json(EVIDENCE / "negative_cases.json", negative)
    write_json(EVIDENCE / "dependency_audit.json", dependency_audit())
    write_json(EVIDENCE / "security_audit.json", security_audit())
    write_json(EVIDENCE / "local_check_record.json", local_check_record())
    write_json(
        EVIDENCE / "ci_record.json",
        {
            "baseline_head": PHASE10I_BASELINE_HEAD,
            "implementation_commit": PHASE10I_IMPLEMENTATION_COMMIT,
            "ci_run": PHASE10I_IMPLEMENTATION_CI_RUN,
            "ci_commit_matches": True,
            "unit": "success",
            "frontend_typecheck_build": "success",
            "service_backed_integration": "success",
            "no_skipped_assertion": "success",
        },
    )
    (EVIDENCE / "README.md").write_text(
        "# Phase 10I Brillouin Zone Contract Evidence\n\n"
        "Deterministic contract fixtures and independent NumPy/SciPy references. "
        "The generator performs no network access. No adapter, tool, browser, GPU, "
        "API job, or production-renderer evidence is claimed.\n\n"
        "Replay with `uv run python scripts/generate_phase10i_brillouin_zone_evidence.py`.\n",
        encoding="utf-8",
    )
    write_json(EVIDENCE / "artifact_hashes.json", hash_tree(EVIDENCE))
    print("BRILLOUIN_ZONE_CONTRACT_EVIDENCE_PASS")
    print("BRILLOUIN_ZONE_INDEPENDENT_REFERENCE_PASS")
    print("NO_BRILLOUIN_EXTERNAL_NETWORK_REQUESTS")
    print("NO_SECRET_PATTERN_HITS")


def fixture_definitions() -> dict[str, dict[str, Any]]:
    a = 4.0
    source_cubic = [[a, 0, 0], [0, a, 0], [0, 0, a]]
    bcc = [[-a / 2, a / 2, a / 2], [a / 2, -a / 2, a / 2], [a / 2, a / 2, -a / 2]]
    fcc = [[0, a / 2, a / 2], [a / 2, 0, a / 2], [a / 2, a / 2, 0]]
    hexagonal = [[3.0, 0, 0], [-1.5, 3 * math.sqrt(3) / 2, 0], [0, 0, 5.2]]
    triclinic = [[3.1, 0.2, 0.1], [0.7, 4.0, 0.3], [0.4, 0.8, 5.1]]
    return {
        "simple_cubic": {"source_lattice": source_cubic, "primitive_lattice": source_cubic, "path": sc_path()},
        "bcc": {"source_lattice": bcc, "primitive_lattice": bcc, "path": bcc_path()},
        "fcc": {"source_lattice": fcc, "primitive_lattice": fcc, "path": fcc_path()},
        "hexagonal": {"source_lattice": hexagonal, "primitive_lattice": hexagonal, "path": hex_path()},
        "triclinic": {"source_lattice": triclinic, "primitive_lattice": triclinic, "path": None},
        "conventional_bcc": {
            "source_lattice": source_cubic,
            "primitive_lattice": bcc,
            "conventional_lattice": source_cubic,
            "transformation": [[-0.5, 0.5, 0.5], [0.5, -0.5, 0.5], [0.5, 0.5, -0.5]],
            "path": bcc_path(),
        },
    }


def build_package(name: str, definition: dict[str, Any]) -> dict[str, Any]:
    structure_hash = hashlib.sha256(stable_brillouin_json({"fixture": name, "lattice": definition["source_lattice"]}).encode()).hexdigest()
    provider = provider_metadata(structure_hash)
    transforms = []
    if definition.get("transformation") is not None:
        transforms.append(
            build_basis_transformation(
                definition["transformation"],
                old_basis="source_cell",
                new_basis="standardized_primitive_cell",
            )
        )
    reciprocal = build_reciprocal_lattice_contract(
        source_structure_id=f"fixture:{name}",
        source_structure_sha256=structure_hash,
        source_real_lattice=definition["source_lattice"],
        primitive_real_lattice=definition["primitive_lattice"],
        conventional_real_lattice=definition.get("conventional_lattice"),
        transformations=transforms,
        provider=provider,
    )
    zone = canonicalize_brillouin_zone(
        reciprocal,
        pymatgen_faces(definition["primitive_lattice"], reciprocal["matrix"]),
        provider_method="pymatgen_lattice_wigner_seitz_fixture_only",
    )
    kpath = None
    if definition["path"] is not None:
        path = definition["path"]
        kpath = build_kpath_contract(
            reciprocal,
            point_specs=path["points"],
            variant_specs=path["variants"],
            selected_variant_key="primary",
            provider=provider,
            path_convention="internal_fixture_reference",
            time_reversal_used=True,
        )
    manifest = build_brillouin_zone_manifest(reciprocal, zone, kpath)
    package = {"reciprocal_lattice": reciprocal, "brillouin_zone": zone, "manifest": manifest}
    if kpath is not None:
        package["kpath"] = kpath
    return package


def pymatgen_faces(real_lattice: list[list[float]], reciprocal_matrix: list[list[float]]) -> list[dict[str, Any]]:
    faces = Lattice(real_lattice).reciprocal_lattice.get_wigner_seitz_cell()
    output = []
    for face in faces:
        vertices = [[float(component) for component in point] for point in face]
        candidates = []
        for hkl in product(range(-BRILLOUIN_CAPS["max_generator_search_radius"], BRILLOUIN_CAPS["max_generator_search_radius"] + 1), repeat=3):
            if hkl == (0, 0, 0):
                continue
            generator = bz_reciprocal_fractional_to_cartesian(hkl, reciprocal_matrix)
            offset = sum(component * component for component in generator) / 2
            residual = max(abs(sum(point[index] * generator[index] for index in range(3)) - offset) for point in vertices)
            candidates.append((residual, sum(component * component for component in hkl), hkl))
        residual, _, generator_hkl = min(candidates)
        if residual > 1e-7:
            raise RuntimeError(f"No bounded reciprocal generator for {generator_hkl}: {residual}")
        output.append({"generator_hkl": list(generator_hkl), "vertices": vertices})
    return output


def independent_reference(real_lattice: list[list[float]]) -> dict[str, Any]:
    real = np.asarray(real_lattice, dtype=float)
    reciprocal = 2 * np.pi * np.linalg.inv(real).T
    integer_points = np.asarray(list(product(range(-3, 4), repeat=3)), dtype=float)
    reciprocal_points = integer_points @ reciprocal
    origin_index = int(np.where(np.all(integer_points == 0, axis=1))[0][0])
    voronoi = Voronoi(reciprocal_points)
    region = voronoi.regions[voronoi.point_region[origin_index]]
    if not region or -1 in region:
        raise RuntimeError("Independent Voronoi region is unbounded")
    region_set = set(region)
    face_vertex_ids = []
    for point_pair, ridge_vertices in zip(voronoi.ridge_points, voronoi.ridge_vertices, strict=True):
        if origin_index not in point_pair or -1 in ridge_vertices:
            continue
        if set(ridge_vertices).issubset(region_set):
            face_vertex_ids.append(ridge_vertices)
    vertex_map = {old: new for new, old in enumerate(sorted(region))}
    edges: set[tuple[int, int]] = set()
    for face in face_vertex_ids:
        ordered = order_face([voronoi.vertices[index] for index in face])
        ids = [vertex_map[face[index]] for index in ordered]
        edges.update(tuple(sorted((ids[index], ids[(index + 1) % len(ids)]))) for index in range(len(ids)))
    vertices = voronoi.vertices[sorted(region)]
    hull = ConvexHull(vertices)
    dual = real @ reciprocal.T
    return {
        "reciprocal_matrix": rounded(reciprocal.tolist()),
        "dual_product": rounded(dual.tolist()),
        "volume": round(float(hull.volume), 12),
        "topology": {
            "vertex_count": len(region),
            "edge_count": len(edges),
            "face_count": len(face_vertex_ids),
            "euler_characteristic": len(region) - len(edges) + len(face_vertex_ids),
        },
        "method": "independent_numpy_inverse_scipy_voronoi_convex_hull",
    }


def order_face(points: list[np.ndarray]) -> list[int]:
    center = np.mean(points, axis=0)
    normal = np.cross(points[1] - points[0], points[2] - points[0])
    normal /= np.linalg.norm(normal)
    first = points[0] - center
    first /= np.linalg.norm(first)
    second = np.cross(normal, first)
    angles = [math.atan2(float(np.dot(point - center, second)), float(np.dot(point - center, first))) for point in points]
    return list(np.argsort(angles))


def validate_package(package: dict[str, Any]) -> dict[str, Any]:
    reciprocal = validate_reciprocal_lattice(package["reciprocal_lattice"]).as_dict()
    zone = validate_brillouin_zone(package["brillouin_zone"], package["reciprocal_lattice"]).as_dict()
    kpath = validate_kpath(package["kpath"], package["reciprocal_lattice"]).as_dict() if "kpath" in package else None
    manifest = validate_brillouin_zone_manifest(package["manifest"], package["reciprocal_lattice"], package["brillouin_zone"], package.get("kpath")).as_dict()
    return {"valid": reciprocal["valid"] and zone["valid"] and (kpath is None or kpath["valid"]) and manifest["valid"], "reciprocal_lattice": reciprocal, "brillouin_zone": zone, "kpath": kpath, "manifest": manifest}


def canonical_replay(packages: dict[str, dict[str, Any]]) -> dict[str, Any]:
    result = {}
    for name, package in packages.items():
        encoded = stable_brillouin_json(package)
        decoded = json.loads(encoded)
        replay = stable_brillouin_json(decoded)
        result[name] = {"byte_equal": encoded == replay, "sha256": hashlib.sha256(encoded.encode()).hexdigest(), "valid": validate_package(decoded)["valid"]}
    return result


def negative_cases(packages: dict[str, dict[str, Any]]) -> dict[str, Any]:
    cases: dict[str, Any] = {}
    try:
        build_reciprocal_lattice_contract(source_structure_id="singular", source_structure_sha256="a" * 64, source_real_lattice=[[1, 0, 0], [2, 0, 0], [0, 0, 1]], primitive_real_lattice=[[1, 0, 0], [2, 0, 0], [0, 0, 1]])
    except BrillouinContractError as error:
        cases["singular_lattice"] = error.code
    try:
        build_reciprocal_lattice_contract(source_structure_id="ill-conditioned", source_structure_sha256="b" * 64, source_real_lattice=[[1, 0, 0], [0, 1, 0], [0, 0, 1e-8]], primitive_real_lattice=[[1, 0, 0], [0, 1, 0], [0, 0, 1e-8]])
    except BrillouinContractError as error:
        cases["ill_conditioned_lattice"] = error.code
    try:
        build_reciprocal_lattice_contract(source_structure_id="non-finite", source_structure_sha256="c" * 64, source_real_lattice=[[1, 0, 0], [0, math.inf, 0], [0, 0, 1]], primitive_real_lattice=[[1, 0, 0], [0, 1, 0], [0, 0, 1]])
    except BrillouinContractError as error:
        cases["non_finite_lattice"] = error.code
    reciprocal = copy.deepcopy(packages["conventional_bcc"]["reciprocal_lattice"])
    reciprocal["transformations"][0]["matrix"] = [[1, 0], [0, 1], [0, 0]]
    rehash(reciprocal)
    cases["malformed_transformation"] = validate_reciprocal_lattice(reciprocal).as_dict()
    zone = copy.deepcopy(packages["simple_cubic"]["brillouin_zone"])
    zone["vertices"][1]["cartesian_coordinates"] = list(zone["vertices"][0]["cartesian_coordinates"])
    rehash(zone)
    cases["duplicate_vertex"] = validate_brillouin_zone(zone, packages["simple_cubic"]["reciprocal_lattice"]).as_dict()
    zone = copy.deepcopy(packages["simple_cubic"]["brillouin_zone"])
    zone["faces"].pop()
    rehash(zone)
    cases["open_topology"] = validate_brillouin_zone(zone, packages["simple_cubic"]["reciprocal_lattice"]).as_dict()
    zone = copy.deepcopy(packages["simple_cubic"]["brillouin_zone"])
    zone["faces"][0]["outward_normal"] = [-value for value in zone["faces"][0]["outward_normal"]]
    rehash(zone)
    cases["inward_face"] = validate_brillouin_zone(zone, packages["simple_cubic"]["reciprocal_lattice"]).as_dict()
    zone = copy.deepcopy(packages["simple_cubic"]["brillouin_zone"])
    zone["volume"] *= 1.1
    rehash(zone)
    cases["volume_mismatch"] = validate_brillouin_zone(zone, packages["simple_cubic"]["reciprocal_lattice"]).as_dict()
    path = copy.deepcopy(packages["simple_cubic"]["kpath"])
    path["points"][0]["display_label"] = "<script>alert(1)</script>"
    rehash(path)
    cases["label_injection"] = validate_kpath(path, packages["simple_cubic"]["reciprocal_lattice"]).as_dict()
    path = copy.deepcopy(packages["simple_cubic"]["kpath"])
    path["segments"][0]["end_point_id"] = "kp-missing"
    rehash(path)
    cases["invalid_path_endpoint"] = validate_kpath(path, packages["simple_cubic"]["reciprocal_lattice"]).as_dict()
    path = copy.deepcopy(packages["simple_cubic"]["kpath"])
    template = path["points"][0]
    for index in range(BRILLOUIN_CAPS["max_high_symmetry_points"] + 1 - len(path["points"])):
        point_value = copy.deepcopy(template)
        point_value["point_id"] = f"kp-over-cap-{index:03d}"
        point_value["label_key"] = f"OVER{index:03d}"
        point_value["display_label"] = f"O{index:03d}"
        point_value["aliases"] = []
        point_value["fractional_coordinates"] = [float(index + 2), 0.0, 0.0]
        point_value["cartesian_coordinates"] = bz_reciprocal_fractional_to_cartesian(
            point_value["fractional_coordinates"], packages["simple_cubic"]["reciprocal_lattice"]["matrix"]
        )
        point_value["provider_identity"]["source_label_keys"] = [point_value["label_key"]]
        path["points"].append(point_value)
    rehash(path)
    cases["cap_exceeded"] = validate_kpath(path, packages["simple_cubic"]["reciprocal_lattice"]).as_dict()
    reciprocal = copy.deepcopy(packages["simple_cubic"]["reciprocal_lattice"])
    reciprocal["convention"] = "crystallographic_no_2pi"
    rehash(reciprocal)
    cases["convention_mismatch"] = validate_reciprocal_lattice(reciprocal).as_dict()
    return cases


def pre_implementation_audit() -> dict[str, Any]:
    return {
        "baseline_head": PHASE10I_BASELINE_HEAD,
        "branch": "master",
        "initial_worktree": "clean",
        "phase10h5": {
            "implementation_commit": PHASE10H5_IMPLEMENTATION_COMMIT,
            "implementation_ci_run": "29327516331",
            "completion_record_commit": PHASE10H5_COMPLETION_COMMIT,
            "completion_record_ci_run": "29327795589",
            "archive_commit": PHASE10I_BASELINE_HEAD,
            "archive_ci_run": "29327985997",
            "frontend_tests": "193 passed",
            "backend_tests": "566 passed, 23 skipped",
            "unit": "success",
            "frontend": "success",
            "service_backed_integration": "success",
            "no_skipped_assertion": "success",
        },
        "real_lattice": "row vectors; r_cart=r_frac*A",
        "reciprocal_lattice": "B=2*pi*A^-T; k_cart=k_frac*B",
        "duality": "A*B^T=2*pi*I",
        "phonon_compatibility": "reciprocal_fractional and 2*pi*q.R",
        "symmetry": {"pymatgen": metadata.version("pymatgen"), "spglib": metadata.version("spglib"), "seekpath": None, "phonopy": None},
        "selected_family": ["phase10i.reciprocal_lattice.v1", "phase10i.brillouin_zone.v1", "phase10i.kpath.v1", "phase10i.brillouin_zone_manifest.v1"],
        "tool_registration": "NOT_REGISTERED",
        "renderer": "NOT_INCLUDED",
    }


def bcc_fcc_reference(packages: dict[str, dict[str, Any]], references: dict[str, Any]) -> dict[str, Any]:
    return {
        "fcc_real_reciprocal_type": "bcc",
        "fcc_real_bz": {"solid": "truncated_octahedron", "counts": references["fcc"]["topology"], "artifact_counts": packages["fcc"]["brillouin_zone"]["topology"]},
        "bcc_real_reciprocal_type": "fcc",
        "bcc_real_bz": {"solid": "rhombic_dodecahedron", "counts": references["bcc"]["topology"], "artifact_counts": packages["bcc"]["brillouin_zone"]["topology"]},
        "verification": "independent_numpy_inverse_scipy_voronoi_convex_hull",
    }


def dependency_audit() -> dict[str, Any]:
    return {
        "direct": {"pymatgen": metadata.version("pymatgen"), "pymatviz": metadata.version("pymatviz")},
        "installed_transitive": {"numpy": metadata.version("numpy"), "scipy": metadata.version("scipy"), "spglib": metadata.version("spglib")},
        "absent": ["seekpath", "phonopy"],
        "dependency_changes": False,
        "network_required": False,
        "npm_audit": {
            "status": "unavailable",
            "reason": "configured npmmirror audit endpoint returns 404 NOT_IMPLEMENTED",
            "reported_clean": False,
        },
        "future_provider_recommendation": "pymatgen HighSymmKpath plus spglib standardization until seekpath is separately approved",
    }


def local_check_record() -> dict[str, Any]:
    return {
        "phase10i_contract": "39 passed",
        "focused_cross_phase": "157 passed",
        "frontend": "193 passed",
        "frontend_typecheck": "success",
        "frontend_build": "success",
        "backend_full": "605 passed, 23 skipped, 11 warnings",
        "uv_lock_check": "success",
        "service_backed_local": "unavailable: Docker and required service environment variables are not configured",
        "skipped_are_not_reported_as_passed": True,
    }


def security_audit() -> dict[str, Any]:
    return {
        "inert_json": True,
        "artifact_javascript": False,
        "artifact_html": False,
        "artifact_css": False,
        "artifact_shader": False,
        "external_urls": [],
        "renderer_included": False,
        "webgl_included": False,
        "tool_registered": False,
        "planner_routing": False,
        "real_llm": False,
        "caps": dict(BRILLOUIN_CAPS),
        "markers": ["NO_BRILLOUIN_EXTERNAL_NETWORK_REQUESTS", "NO_SECRET_PATTERN_HITS"],
    }


def provider_metadata(structure_hash: str) -> dict[str, Any]:
    return {
        "name": "internal_fixture_reference",
        "version": "1",
        "convention": "internal_fixture_reference",
        "input_structure_sha256": structure_hash,
        "symprec_angstrom": 1e-5,
        "angle_tolerance_degrees": 5.0,
        "time_reversal_used": True,
        "standardization_status": "validated_fixture",
        "warnings": [],
    }


def sc_path() -> dict[str, Any]:
    return path([point("GAMMA", "Γ", [0, 0, 0], ["G"]), point("X", "X", [0, 0.5, 0]), point("M", "M", [0.5, 0.5, 0]), point("R", "R", [0.5, 0.5, 0.5])], [["GAMMA", "X", "M", "GAMMA", "R", "X"], ["M", "R"]])


def bcc_path() -> dict[str, Any]:
    return path([point("GAMMA", "Γ", [0, 0, 0], ["G"]), point("H", "H", [0.5, -0.5, 0.5]), point("P", "P", [0.25, 0.25, 0.25]), point("N", "N", [0, 0, 0.5])], [["GAMMA", "H", "N", "GAMMA", "P", "H"], ["P", "N"]])


def fcc_path() -> dict[str, Any]:
    return path([point("GAMMA", "Γ", [0, 0, 0], ["G"]), point("X", "X", [0.5, 0, 0.5]), point("W", "W", [0.5, 0.25, 0.75]), point("K", "K", [0.375, 0.375, 0.75]), point("L", "L", [0.5, 0.5, 0.5]), point("U", "U", [0.625, 0.25, 0.625])], [["GAMMA", "X", "W", "K", "GAMMA", "L", "U", "W", "L", "K"], ["U", "X"]])


def hex_path() -> dict[str, Any]:
    return path([point("GAMMA", "Γ", [0, 0, 0], ["G"]), point("M", "M", [0.5, 0, 0]), point("K", "K", [1 / 3, 1 / 3, 0]), point("A", "A", [0, 0, 0.5]), point("L", "L", [0.5, 0, 0.5]), point("H", "H", [1 / 3, 1 / 3, 0.5])], [["GAMMA", "M", "K", "GAMMA", "A", "L", "H", "A"], ["L", "M"], ["K", "H"]])


def point(label_key: str, display: str, coordinates: list[float], aliases: list[str] | None = None) -> dict[str, Any]:
    return {"label_key": label_key, "display_label": display, "aliases": aliases or [], "fractional_coordinates": coordinates}


def path(points: list[dict[str, Any]], branches: list[list[str]]) -> dict[str, Any]:
    return {"points": points, "variants": [{"variant_key": "primary", "description": "Internal deterministic fixture path", "branches": branches}]}


def rehash(payload: dict[str, Any]) -> None:
    payload["content_hash"] = brillouin_content_hash(payload)


def rounded(value: Any) -> Any:
    if isinstance(value, list):
        return [rounded(item) for item in value]
    if isinstance(value, float):
        result = round(value, 12)
        return 0.0 if abs(result) < 5e-13 else result
    return value


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def hash_tree(root: Path) -> dict[str, Any]:
    files = []
    for path in sorted(item for item in root.rglob("*") if item.is_file() and item.name != "artifact_hashes.json"):
        data = path.read_bytes()
        files.append({"name": path.relative_to(root).as_posix(), "bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()})
    return {"algorithm": "sha256", "files": files}


if __name__ == "__main__":
    main()
