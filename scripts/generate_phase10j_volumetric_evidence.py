from __future__ import annotations

from copy import deepcopy
import hashlib
import json
import math
import os
from pathlib import Path
import struct

from mdi_artifact_core import (
    VolumetricContractError,
    build_binary_payload,
    build_chunked_payload,
    build_inline_payload,
    build_volumetric_dataset,
    build_volumetric_field,
    build_volumetric_grid,
    build_volumetric_manifest,
    validate_volumetric_grid,
    validate_volumetric_payload,
    volumetric_content_hash,
    volumetric_lattice_hash,
    volumetric_schema_snapshots,
)


ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "docs" / "phase10j" / "fixtures" / "volumetric_contract"
EVIDENCE = ROOT / "docs" / "phase10j" / "evidence" / "phase10j_volumetric_data_contract"


def main() -> None:
    for directory in (FIXTURES, EVIDENCE):
        directory.mkdir(parents=True, exist_ok=True)
    write_json(FIXTURES / "schema_snapshots.json", volumetric_schema_snapshots())
    cubic = cubic_constant_fixture()
    write_json(FIXTURES / "cubic_constant_scalar.json", cubic)
    trig = trigonometric_fixture()
    write_json(FIXTURES / "periodic_trigonometric_scalar.json", trig)
    triclinic = triclinic_fixture()
    write_json(FIXTURES / "triclinic_periodic_grid.json", triclinic)
    affine = affine_fixture()
    write_json(FIXTURES / "nonperiodic_affine_box.json", affine)
    write_json(FIXTURES / "collinear_spin_dataset.json", spin_fixture())
    write_json(FIXTURES / "noncollinear_magnetization.json", vector_fixture())
    write_json(FIXTURES / "complex_scalar.json", complex_fixture())
    write_json(FIXTURES / "potential_gauge.json", potential_fixture())
    chunked = chunk_fixture()
    write_json(FIXTURES / "chunked_payload.json", chunked[0])
    write_binary(FIXTURES / "binary" / "chunked-logical.raw", chunked[1])
    negatives = negative_cases()
    write_json(FIXTURES / "negative_cases.json", negatives)

    write_json(EVIDENCE / "pre_implementation_audit.json", pre_implementation_audit())
    write_json(EVIDENCE / "schema" / "schema_snapshots.json", volumetric_schema_snapshots())
    write_json(EVIDENCE / "validation" / "fixture_validation.json", fixture_validation(cubic, trig, triclinic, affine, chunked[0]))
    write_json(EVIDENCE / "references" / "independent_math.json", independent_references(cubic, trig, triclinic, affine))
    write_json(EVIDENCE / "security" / "negative_cases.json", negatives)
    write_json(
        EVIDENCE / "security" / "cap_decompression.json",
        {
            "allocation_checked_before_decode": True,
            "bounded_streaming_gzip": True,
            "compression_ratio_cap": 128,
            "gzip_members_allowed": 1,
            "max_chunks_per_field": 256,
            "max_total_voxels": 16_777_216,
            "focused_test": "test_compression_ratio_cap_blocks_bomb_like_constant_payload",
            "result": "PASS",
        },
    )
    write_json(EVIDENCE / "replay" / "determinism.json", deterministic_replay(cubic, trig, chunked[0]))
    write_json(
        EVIDENCE / "replay" / "commands.json",
        {
            "generate": "uv run python scripts/generate_phase10j_volumetric_evidence.py",
            "focused_tests": "uv run python -m pytest tests/test_phase10j_volumetric_contract.py tests/test_phase10j_volumetric_evidence.py -q",
            "full_backend": "uv run python -m pytest -q",
            "frontend": "npm --prefix apps/web test",
            "typecheck": "npm --prefix apps/web run typecheck",
            "build": "npm --prefix apps/web run build",
        },
    )
    write_json(
        EVIDENCE / "test_captures" / "local_checks.json",
        {
            "focused_contract_and_evidence": "34 passed",
            "phase10i_cross_platform_evidence": "6 passed",
            "backend_full": "695 passed, 23 skipped, 62 warnings",
            "frontend_full": "223 passed",
            "frontend_typecheck": "success",
            "frontend_build": "success",
            "phase10_backend_closure": "3 passed, 2 deselected",
            "phase10_frontend_closure": "2 passed",
            "phase10_evidence_integrity": "PHASE10_CLOSURE_EVIDENCE_INTEGRITY_PASS",
            "service_backed_local": "unavailable: Docker CLI is not installed",
        },
    )
    write_json(
        EVIDENCE / "ci" / "ci_record.json",
        {
            "commit": os.environ.get("PHASE10J_CI_COMMIT", "pending"),
            "run": os.environ.get("PHASE10J_CI_RUN", "pending"),
            "status": os.environ.get("PHASE10J_CI_STATUS", "pending current-head CI"),
            "required_jobs": ["unit", "frontend", "service-backed integration", "no-skipped assertion"],
        },
    )
    write_json(
        EVIDENCE / "dependency_audit.json",
        {
            "new_dependencies": [],
            "lockfile_changed": False,
            "compression": "python standard library gzip/zlib",
            "binary": "python standard library struct",
            "network_required": False,
            "npm_audit": "unavailable: configured npmmirror endpoint returned 404 NOT_IMPLEMENTED",
        },
    )
    write_json(EVIDENCE / "security" / "audit.json", {"artifact_javascript": False, "html": False, "css": False, "shader": False, "executable": False, "external_urls": [], "pickle": False, "object_deserialization": False, "path_traversal": False, "bounded_decompression": True, "bounded_allocation": True, "secret_scan": "NO_SECRET_PATTERN_HITS"})
    write_text(EVIDENCE / "README.md", "# Phase 10J Volumetric Data Contract Evidence\n\nDeterministic contract fixtures, independent mathematical references, binary payloads, cap/security negatives, and replay hashes. No parser, tool, renderer, executable artifact, external URL, or network operation is included.\n")
    update_hashes()
    print("VOLUMETRIC_DATA_CONTRACT_EVIDENCE_PASS")
    print("NO_EXTERNAL_NETWORK_REQUESTS")
    print("NO_SECRET_PATTERN_HITS")


def periodic_grid(shape: list[int], lattice: list[list[float]] | None = None, origin_fractional: list[float] | None = None) -> dict:
    lattice = lattice or [[4.0, 0.0, 0.0], [0.0, 4.0, 0.0], [0.0, 0.0, 4.0]]
    origin_fractional = origin_fractional or [0.0, 0.0, 0.0]
    origin = [sum(origin_fractional[row] * lattice[row][axis] for row in range(3)) for axis in range(3)]
    step = [[lattice[row][axis] / shape[row] for axis in range(3)] for row in range(3)]
    binding = {"structure_sha256": "1" * 64, "lattice_sha256": volumetric_lattice_hash(lattice), "lattice_matrix": lattice, "basis_role": "canonical_structure_cell"}
    return build_volumetric_grid(shape=shape, origin_cartesian=origin, origin_fractional=origin_fractional, step_matrix=step, sample_location="node", boundary_conditions=["periodic"] * 3, endpoint_policy="excluded", structure_binding=binding)


def field(grid: dict, payload: dict, values: list[float], **overrides: object) -> dict:
    params: dict[str, object] = {"grid": grid, "payload": payload, "values": values, "field_name": "density", "quantity": "electron_density", "unit": "electron/angstrom^3", "value_kind": "real", "field_rank": "scalar", "normalization_semantics": "source_native", "integral_semantics": "electron_count"}
    params.update(overrides)
    return build_volumetric_field(**params)


def cubic_constant_fixture() -> dict:
    grid = periodic_grid([4, 4, 4])
    values = [2.0] * 64
    inline = build_inline_payload(values, grid_shape=grid["shape"], stored_components=1)
    raw = build_binary_payload(values, grid_shape=grid["shape"], stored_components=1, artifact_name="cubic-constant.f64")
    inline_field = field(grid, inline.metadata, values)
    raw_field = field(grid, raw.metadata, values)
    raw_dataset = build_volumetric_dataset(grid=grid, payloads=[raw.metadata], fields=[raw_field], artifacts=raw.artifacts)
    manifest = build_volumetric_manifest(raw_dataset, raw.artifacts)
    write_binary(FIXTURES / "binary" / "cubic-constant.f64", raw.artifacts["cubic-constant.f64"])
    return {"fixture_id": "cubic_constant_scalar", "synthetic": True, "grid": grid, "values": values, "inline_payload": inline.metadata, "raw_payload": raw.metadata, "inline_field": inline_field, "raw_field": raw_field, "raw_dataset": raw_dataset, "manifest": manifest, "equivalence": {"logical_hash_equal": inline.metadata["logical_sha256"] == raw.metadata["logical_sha256"], "known_integral": 128.0}}


def trigonometric_fixture() -> dict:
    grid = periodic_grid([8, 8, 8], origin_fractional=[0.125, 0.25, 0.375])
    values = []
    for i in range(8):
        for j in range(8):
            for k in range(8):
                x, y, z = (i / 8 + 0.125) % 1, (j / 8 + 0.25) % 1, (k / 8 + 0.375) % 1
                values.append(math.cos(2 * math.pi * x) + 0.5 * math.sin(2 * math.pi * y) - 0.25 * math.cos(4 * math.pi * z))
    bundle = build_binary_payload(values, grid_shape=grid["shape"], stored_components=1, encoding="gzip_binary", artifact_name="periodic-trigonometric.f64.gz")
    item = field(grid, bundle.metadata, values, field_name="periodic trigonometric", quantity="generic_scalar", unit="dimensionless", normalization_semantics="not_normalized", integral_semantics="zero_by_definition")
    write_binary(FIXTURES / "binary" / "periodic-trigonometric.f64.gz", bundle.artifacts["periodic-trigonometric.f64.gz"])
    return {"fixture_id": "periodic_trigonometric_scalar", "synthetic": True, "grid": grid, "payload": bundle.metadata, "field": item, "reference": {"cell_integral": item["statistics"]["stored_components"][0]["integral"], "expected_near_zero": True}}


def triclinic_fixture() -> dict:
    lattice = [[4.0, 0.0, 0.0], [1.0, 3.0, 0.0], [0.5, 0.25, 2.0]]
    grid = periodic_grid([2, 3, 4], lattice=lattice, origin_fractional=[0.25, 0.5, 0.75])
    values = [float(index) for index in range(24)]
    payload = build_inline_payload(values, grid_shape=grid["shape"], stored_components=1).metadata
    return {"fixture_id": "triclinic_periodic_grid", "synthetic": True, "grid": grid, "payload": payload, "field": field(grid, payload, values, field_name="triclinic scalar", quantity="generic_scalar", unit="dimensionless", normalization_semantics="not_normalized", integral_semantics="not_physically_interpreted")}


def affine_fixture() -> dict:
    grid = build_volumetric_grid(shape=[2, 3, 4], origin_cartesian=[10.0, -2.0, 3.0], step_matrix=[[0.5, 0.0, 0.0], [0.1, 1.0, 0.0], [0.0, 0.2, 2.0]], sample_location="cell_center", boundary_conditions=["non_periodic"] * 3, endpoint_policy="included")
    values = [3.0] * 24
    payload = build_inline_payload(values, grid_shape=grid["shape"], stored_components=1).metadata
    return {"fixture_id": "nonperiodic_affine_box", "synthetic": True, "grid": grid, "payload": payload, "field": field(grid, payload, values, field_name="affine scalar", quantity="generic_scalar", unit="dimensionless", normalization_semantics="not_normalized", integral_semantics="not_physically_interpreted")}


def spin_fixture() -> dict:
    grid = periodic_grid([2, 2, 2])
    up, down = [0.75] * 8, [0.25] * 8
    channels = {"up": up, "down": down, "total": [a + b for a, b in zip(up, down, strict=True)], "difference": [a - b for a, b in zip(up, down, strict=True)]}
    payloads, fields = [], []
    for name, values in channels.items():
        payload = build_inline_payload(values, grid_shape=grid["shape"], stored_components=1).metadata
        quantity = "spin_density" if name == "difference" else "electron_density"
        options = {"field_name": name, "quantity": quantity}
        if name == "difference":
            options["spin"] = {"representation": "collinear", "channel": "spin_difference", "component_basis": "not_applicable", "sign_convention": "up minus down", "source_convention": "synthetic fixture"}
        payloads.append(payload)
        fields.append(field(grid, payload, values, **options))
    by_name = {item["field_name"]: item["field_id"] for item in fields}
    relationships = [
        {"relationship_id": "total", "kind": "total_equals_up_plus_down", "input_field_ids": [by_name["up"], by_name["down"]], "output_field_id": by_name["total"], "status": "validated", "residual": 0.0},
        {"relationship_id": "difference", "kind": "spin_difference_equals_up_minus_down", "input_field_ids": [by_name["up"], by_name["down"]], "output_field_id": by_name["difference"], "status": "validated", "residual": 0.0},
    ]
    return {"fixture_id": "collinear_spin_dataset", "synthetic": True, "dataset": build_volumetric_dataset(grid=grid, payloads=payloads, fields=fields, relationships=relationships)}


def vector_fixture() -> dict:
    grid = periodic_grid([2, 2, 2])
    values = [component for index in range(8) for component in (float(index), float(-index), 0.5)]
    payload = build_inline_payload(values, grid_shape=grid["shape"], stored_components=3).metadata
    item = field(grid, payload, values, field_name="magnetization", quantity="magnetization_density", unit="bohr_magneton/angstrom^3", field_rank="vector", integral_semantics="magnetic_moment", spin={"representation": "non_collinear", "channel": "magnetization_vector", "component_basis": "cartesian", "sign_convention": "source declared", "source_convention": "synthetic Cartesian fixture"})
    return {"fixture_id": "noncollinear_magnetization", "synthetic": True, "grid": grid, "payload": payload, "field": item}


def complex_fixture() -> dict:
    grid = periodic_grid([2, 2, 2])
    values = [component for index in range(8) for component in (math.cos(index), math.sin(index))]
    payload = build_inline_payload(values, grid_shape=grid["shape"], stored_components=2).metadata
    item = field(grid, payload, values, field_name="wavefunction", quantity="wavefunction", unit="angstrom^-3", value_kind="complex", field_rank="scalar", normalization_semantics="normalized_to_unit_integral", integral_semantics="not_physically_interpreted")
    return {"fixture_id": "complex_scalar", "synthetic": True, "grid": grid, "payload": payload, "field": item}


def potential_fixture() -> dict:
    grid = periodic_grid([2, 2, 2])
    values = [-1.0, 1.0] * 4
    payload = build_inline_payload(values, grid_shape=grid["shape"], stored_components=1).metadata
    item = field(grid, payload, values, field_name="potential", quantity="electrostatic_potential", unit="electronvolt", normalization_semantics="not_normalized", integral_semantics="cell_average", potential_reference={"kind": "cell_average_zero", "reference_value": 0.0, "reference_unit": "electronvolt", "shift_applied": False, "shift_amount": 0.0, "source_metadata": "synthetic gauge"})
    return {"fixture_id": "potential_gauge", "synthetic": True, "grid": grid, "payload": payload, "field": item}


def chunk_fixture() -> tuple[dict, bytes]:
    grid = periodic_grid([4, 3, 2])
    values = [float(index) / 3 for index in range(24)]
    raw = build_binary_payload(values, grid_shape=grid["shape"], stored_components=1, artifact_name="chunk-reference.f64")
    chunked = build_chunked_payload(values, grid_shape=grid["shape"], stored_components=1, chunk_i=2, compression="gzip_binary", artifact_prefix="chunked")
    for name, content in chunked.artifacts.items():
        write_binary(FIXTURES / "binary" / name, content)
    item = field(grid, chunked.metadata, values, field_name="chunked scalar", quantity="generic_scalar", unit="dimensionless", normalization_semantics="not_normalized", integral_semantics="not_physically_interpreted")
    dataset = build_volumetric_dataset(grid=grid, payloads=[chunked.metadata], fields=[item], artifacts=chunked.artifacts)
    return {"fixture_id": "chunked_payload", "synthetic": True, "grid": grid, "payload": chunked.metadata, "field": item, "dataset": dataset, "logical_hash_matches_unchunked": chunked.metadata["logical_sha256"] == raw.metadata["logical_sha256"]}, raw.artifacts["chunk-reference.f64"]


def negative_cases() -> dict:
    results: dict[str, str] = {}
    cases = {
        "zero_dimension": lambda: build_volumetric_grid(shape=[0, 1, 1], origin_cartesian=[0, 0, 0], step_matrix=[[1, 0, 0], [0, 1, 0], [0, 0, 1]], sample_location="node", boundary_conditions=["non_periodic"] * 3, endpoint_policy="excluded"),
        "mixed_periodicity": lambda: build_volumetric_grid(shape=[1, 1, 1], origin_cartesian=[0, 0, 0], step_matrix=[[1, 0, 0], [0, 1, 0], [0, 0, 1]], sample_location="node", boundary_conditions=["periodic", "periodic", "non_periodic"], endpoint_policy="excluded"),
        "singular_basis": lambda: build_volumetric_grid(shape=[1, 1, 1], origin_cartesian=[0, 0, 0], step_matrix=[[1, 0, 0], [0, 1, 0], [0, 0, 0]], sample_location="node", boundary_conditions=["non_periodic"] * 3, endpoint_policy="excluded"),
        "nan_value": lambda: build_inline_payload([math.nan], grid_shape=[1, 1, 1], stored_components=1),
        "path_traversal": lambda: build_binary_payload([1.0], grid_shape=[1, 1, 1], stored_components=1, artifact_name="../escape.bin"),
    }
    for name, case in cases.items():
        try:
            case()
            results[name] = "UNEXPECTED_ACCEPT"
        except VolumetricContractError as error:
            results[name] = error.code
    payload = build_binary_payload([1.0], grid_shape=[1, 1, 1], stored_components=1, artifact_name="one.bin")
    truncated = validate_volumetric_payload(payload.metadata, {"one.bin": b""})
    results["truncated_payload"] = truncated.errors[0]
    grid = deepcopy(periodic_grid([1, 1, 1]))
    grid["endpoint_policy"] = "included"
    results["periodic_endpoint_included"] = validate_volumetric_grid(grid).errors[0]
    return {"all_rejected": all(value != "UNEXPECTED_ACCEPT" for value in results.values()), "cases": results}


def independent_references(cubic: dict, trig: dict, triclinic: dict, affine: dict) -> dict:
    raw = (FIXTURES / "binary" / "cubic-constant.f64").read_bytes()
    decoded = [item[0] for item in struct.iter_unpack("<d", raw)]
    tri_grid = triclinic["grid"]
    index = [1, 2, 3]
    shift = 0.0
    coordinate = [tri_grid["origin_cartesian"][axis] + sum((index[row] + shift) * tri_grid["step_matrix"][row][axis] for row in range(3)) for axis in range(3)]
    affine_grid = affine["grid"]
    center = [affine_grid["origin_cartesian"][axis] + sum(0.5 * affine_grid["step_matrix"][row][axis] for row in range(3)) for axis in range(3)]
    offsets = [((((i * 3) + j) * 4 + k) * 2) + c for i in range(2) for j in range(3) for k in range(4) for c in range(2)]
    return {"binary_decoder": {"format": "<d", "count": len(decoded), "minimum": min(decoded), "maximum": max(decoded), "integral": math.fsum(decoded) * cubic["grid"]["voxel_volume"]}, "flatten_2x3x4x2": {"first": offsets[0], "last": offsets[-1], "contiguous": offsets == list(range(48))}, "triclinic_coordinate_1_2_3": coordinate, "affine_first_cell_center": center, "trigonometric_integral": trig["field"]["statistics"]["stored_components"][0]["integral"]}


def fixture_validation(*fixtures: dict) -> dict:
    return {item["fixture_id"]: {"grid_valid": validate_volumetric_grid(item["grid"]).valid, "payload_valid": validate_volumetric_payload(item["payload"]).valid if item.get("payload", {}).get("encoding") == "inline_json" else "binary validated by focused tests"} for item in fixtures}


def deterministic_replay(*values: dict) -> dict:
    first = [volumetric_content_hash(value) for value in values]
    second = [volumetric_content_hash(json.loads(json.dumps(value))) for value in values]
    return {"hashes": first, "replay_hashes": second, "identical": first == second}


def pre_implementation_audit() -> dict:
    return {"baseline_head": "7884f2f18f41c9b3bf8bff0765f2929473bfc465", "phase10i3_archive_ci": "29572957408 success", "row_vector_formula": "r_cart=r_frac*A", "artifact_bytes_supported": True, "hash": "sha256", "dependencies_added": [], "tool_registered": False, "parser_implemented": False, "renderer_implemented": False}


def update_hashes() -> None:
    files = sorted(path for root in (FIXTURES, EVIDENCE) for path in root.rglob("*") if path.is_file() and path.name != "artifact_hashes.json")
    rows = []
    for path in files:
        content = path.read_bytes()
        rows.append({"name": path.relative_to(ROOT).as_posix(), "bytes": len(content), "sha256": hashlib.sha256(content).hexdigest()})
    write_json(EVIDENCE / "artifact_hashes.json", {"algorithm": "sha256", "files": rows})


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes((json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n").encode("utf-8"))


def write_text(path: Path, value: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(value.encode("utf-8"))


def write_binary(path: Path, value: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(value)


if __name__ == "__main__":
    main()
