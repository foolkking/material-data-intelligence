from __future__ import annotations

from copy import deepcopy
import math
import struct

import pytest

from mdi_artifact_core import (
    VOLUMETRIC_CAPS,
    VOLUMETRIC_DATASET_SCHEMA_VERSION,
    VOLUMETRIC_FIELD_SCHEMA_VERSION,
    VOLUMETRIC_GRID_SCHEMA_VERSION,
    VOLUMETRIC_MANIFEST_SCHEMA_VERSION,
    VOLUMETRIC_PAYLOAD_SCHEMA_VERSION,
    VolumetricContractError,
    build_binary_payload,
    build_chunked_payload,
    build_inline_payload,
    build_volumetric_dataset,
    build_volumetric_field,
    build_volumetric_grid,
    build_volumetric_manifest,
    cartesian_to_grid_coordinates,
    decode_volumetric_payload,
    flatten_offset,
    grid_sample_cartesian,
    inverse3,
    is_isosurface_compatible,
    row_vector_multiply,
    stable_volumetric_json,
    validate_volumetric_dataset,
    validate_volumetric_grid,
    validate_volumetric_manifest,
    validate_volumetric_payload,
    volumetric_content_hash,
    volumetric_lattice_hash,
    volumetric_schema_snapshots,
    wrap_fractional,
)


def _binding(lattice: list[list[float]]) -> dict:
    return {
        "structure_sha256": "1" * 64,
        "lattice_sha256": volumetric_lattice_hash(lattice),
        "lattice_matrix": lattice,
        "basis_role": "canonical_structure_cell",
    }


def _periodic_grid(shape: list[int] | None = None) -> dict:
    shape = shape or [4, 4, 4]
    lattice = [[4.0, 0.0, 0.0], [0.0, 4.0, 0.0], [0.0, 0.0, 4.0]]
    steps = [[lattice[row][axis] / shape[row] for axis in range(3)] for row in range(3)]
    return build_volumetric_grid(
        shape=shape,
        origin_cartesian=[0.0, 0.0, 0.0],
        origin_fractional=[0.0, 0.0, 0.0],
        step_matrix=steps,
        sample_location="node",
        boundary_conditions=["periodic"] * 3,
        endpoint_policy="excluded",
        structure_binding=_binding(lattice),
    )


def _field(grid: dict, payload: dict, values: list[float], **overrides: object) -> dict:
    params: dict[str, object] = {
        "grid": grid,
        "payload": payload,
        "values": values,
        "field_name": "density",
        "quantity": "electron_density",
        "unit": "electron/angstrom^3",
        "value_kind": "real",
        "field_rank": "scalar",
        "normalization_semantics": "source_native",
        "integral_semantics": "electron_count",
    }
    params.update(overrides)
    return build_volumetric_field(**params)


def _refresh_payload_layout(payload: dict) -> None:
    identity = {key: payload[key] for key in payload if key not in {"payload_id", "storage_layout_hash"}}
    payload["storage_layout_hash"] = volumetric_content_hash(identity)


def test_schema_family_and_security_snapshot_are_exact() -> None:
    snapshot = volumetric_schema_snapshots()
    assert snapshot["schemas"] == {
        "grid": VOLUMETRIC_GRID_SCHEMA_VERSION,
        "payload": VOLUMETRIC_PAYLOAD_SCHEMA_VERSION,
        "field": VOLUMETRIC_FIELD_SCHEMA_VERSION,
        "dataset": VOLUMETRIC_DATASET_SCHEMA_VERSION,
        "manifest": VOLUMETRIC_MANIFEST_SCHEMA_VERSION,
    }
    assert snapshot["flatten_order"] == "ijkc_component_fastest"
    assert snapshot["periodic_endpoint_policy"] == "excluded"
    assert snapshot["security"]["renderer_included"] is False


def test_periodic_cubic_grid_coordinates_and_integral() -> None:
    grid = _periodic_grid()
    assert validate_volumetric_grid(grid).valid
    assert grid_sample_cartesian(grid, [3, 2, 1]) == pytest.approx([3.0, 2.0, 1.0])
    assert cartesian_to_grid_coordinates([3.0, 2.0, 1.0], grid) == pytest.approx([3.0, 2.0, 1.0])
    values = [2.0] * 64
    payload = build_inline_payload(values, grid_shape=grid["shape"], stored_components=1).metadata
    field = _field(grid, payload, values)
    stats = field["statistics"]["stored_components"][0]
    assert stats["minimum"] == stats["maximum"] == stats["mean"] == 2.0
    assert stats["integral"] == pytest.approx(128.0)


def test_triclinic_shifted_origin_uses_row_vectors() -> None:
    lattice = [[4.0, 0.0, 0.0], [1.0, 3.0, 0.0], [0.5, 0.25, 2.0]]
    shape = [2, 3, 4]
    steps = [[lattice[row][axis] / shape[row] for axis in range(3)] for row in range(3)]
    fractional = [0.25, 0.5, 0.75]
    origin = [sum(fractional[row] * lattice[row][axis] for row in range(3)) for axis in range(3)]
    grid = build_volumetric_grid(
        shape=shape,
        origin_cartesian=origin,
        origin_fractional=fractional,
        step_matrix=steps,
        sample_location="node",
        boundary_conditions=["periodic"] * 3,
        endpoint_policy="excluded",
        structure_binding=_binding(lattice),
    )
    expected = [origin[axis] + steps[0][axis] + 2 * steps[1][axis] + 3 * steps[2][axis] for axis in range(3)]
    assert grid_sample_cartesian(grid, [1, 2, 3]) == pytest.approx(expected)
    assert grid["voxel_volume"] == pytest.approx(abs(24.0) / 24)


def test_nonperiodic_cell_center_affine_grid() -> None:
    grid = build_volumetric_grid(
        shape=[2, 3, 4],
        origin_cartesian=[10.0, -2.0, 3.0],
        step_matrix=[[0.5, 0.0, 0.0], [0.1, 1.0, 0.0], [0.0, 0.2, 2.0]],
        sample_location="cell_center",
        boundary_conditions=["non_periodic"] * 3,
        endpoint_policy="included",
    )
    assert grid_sample_cartesian(grid, [0, 0, 0]) == pytest.approx([10.3, -1.4, 4.0])
    assert grid["structure_binding"] is None
    assert grid["origin_fractional"] is None


@pytest.mark.parametrize(
    ("mutation", "code"),
    [
        (lambda value: value.update(endpoint_policy="included"), "VOLUME_ENDPOINT_POLICY_INVALID"),
        (lambda value: value["step_matrix"].__setitem__(2, [0.0, 0.0, 0.0]), "VOLUME_GRID_BASIS_SINGULAR"),
        (lambda value: value["structure_binding"]["lattice_matrix"][0].__setitem__(0, 5.0), "VOLUME_STRUCTURE_BINDING_INVALID"),
        (lambda value: value.update(content_hash="0" * 64), "VOLUME_CONTENT_HASH_MISMATCH"),
    ],
)
def test_grid_tampering_is_rejected(mutation, code: str) -> None:
    grid = deepcopy(_periodic_grid())
    mutation(grid)
    assert code in validate_volumetric_grid(grid).errors


def test_mixed_periodicity_and_dimension_caps_are_rejected_before_allocation() -> None:
    with pytest.raises(VolumetricContractError, match="Mixed periodicity"):
        build_volumetric_grid(
            shape=[2, 2, 2], origin_cartesian=[0, 0, 0], step_matrix=[[1, 0, 0], [0, 1, 0], [0, 0, 1]],
            sample_location="node", boundary_conditions=["periodic", "periodic", "non_periodic"], endpoint_policy="excluded",
        )
    with pytest.raises(VolumetricContractError) as error:
        build_volumetric_grid(
            shape=[VOLUMETRIC_CAPS["max_grid_dimension"] + 1, 1, 1], origin_cartesian=[0, 0, 0],
            step_matrix=[[1, 0, 0], [0, 1, 0], [0, 0, 1]], sample_location="node",
            boundary_conditions=["non_periodic"] * 3, endpoint_policy="excluded",
        )
    assert error.value.code == "VOLUME_GRID_SHAPE_INVALID"


def test_inverse_and_fractional_wrap_have_deterministic_endpoint_policy() -> None:
    matrix = [[2.0, 0.0, 0.0], [0.5, 3.0, 0.0], [0.25, 0.1, 4.0]]
    inverse = inverse3(matrix)
    vector = [0.2, 0.3, 0.4]
    assert row_vector_multiply(row_vector_multiply(vector, matrix), inverse) == pytest.approx(vector)
    assert wrap_fractional([-0.0, 1.0, -0.25]) == pytest.approx([0.0, 0.0, 0.75])


def test_flatten_order_matches_handwritten_reference_for_2x3x4() -> None:
    shape = [2, 3, 4]
    offsets = []
    for i in range(2):
        for j in range(3):
            for k in range(4):
                for component in range(3):
                    reference = ((((i * 3) + j) * 4 + k) * 3) + component
                    assert flatten_offset([i, j, k], component, shape, 3) == reference
                    offsets.append(reference)
    assert offsets == list(range(72))
    with pytest.raises(VolumetricContractError):
        flatten_offset([2, 0, 0], 0, shape, 3)


@pytest.mark.parametrize("dtype", ["float32", "float64"])
def test_raw_binary_payload_matches_independent_struct_reference(dtype: str) -> None:
    values = [float(index) / 7 for index in range(24)]
    bundle = build_binary_payload(values, grid_shape=[2, 3, 4], stored_components=1, dtype=dtype, artifact_name=f"values-{dtype}.bin")
    assert validate_volumetric_payload(bundle.metadata, bundle.artifacts).valid
    raw = bundle.artifacts[bundle.metadata["artifact_name"]]
    code = "f" if dtype == "float32" else "d"
    independent = [item[0] for item in struct.iter_unpack(f"<{code}", raw)]
    assert decode_volumetric_payload(bundle.metadata, bundle.artifacts) == pytest.approx(independent)
    assert bundle.metadata["logical_shape"] == [2, 3, 4, 1]


def test_deterministic_gzip_roundtrip_and_header_policy() -> None:
    values = [math.sin(index) for index in range(64)]
    first = build_binary_payload(values, grid_shape=[4, 4, 4], stored_components=1, encoding="gzip_binary", artifact_name="values.gz")
    second = build_binary_payload(values, grid_shape=[4, 4, 4], stored_components=1, encoding="gzip_binary", artifact_name="values.gz")
    assert first.artifacts == second.artifacts
    stored = first.artifacts["values.gz"]
    assert stored[0:2] == b"\x1f\x8b"
    assert stored[4:8] == b"\0\0\0\0"
    assert decode_volumetric_payload(first.metadata, first.artifacts) == pytest.approx(values)


def test_chunked_i_slabs_are_complete_and_logically_chunk_independent() -> None:
    values = [float(index) for index in range(2 * 3 * 4 * 3)]
    raw = build_binary_payload(values, grid_shape=[2, 3, 4], stored_components=3, artifact_name="vector.bin")
    chunks = build_chunked_payload(values, grid_shape=[2, 3, 4], stored_components=3, chunk_i=1, artifact_prefix="vector")
    assert validate_volumetric_payload(chunks.metadata, chunks.artifacts).valid
    assert chunks.metadata["logical_sha256"] == raw.metadata["logical_sha256"]
    assert chunks.metadata["storage_layout_hash"] != raw.metadata["storage_layout_hash"]
    assert decode_volumetric_payload(chunks.metadata, chunks.artifacts) == values
    assert [(item["i_start"], item["i_end"]) for item in chunks.metadata["chunks"]] == [(0, 1), (1, 2)]


def test_payload_truncation_trailing_hash_and_chunk_gap_are_rejected() -> None:
    values = [float(index) for index in range(24)]
    bundle = build_binary_payload(values, grid_shape=[2, 3, 4], stored_components=1, artifact_name="values.bin")
    truncated = {"values.bin": bundle.artifacts["values.bin"][:-1]}
    assert "VOLUME_PAYLOAD_HASH_MISMATCH" in validate_volumetric_payload(bundle.metadata, truncated).errors
    trailing_payload = deepcopy(bundle.metadata)
    trailing = bundle.artifacts["values.bin"] + b"\0"
    trailing_payload["compressed_bytes"] = len(trailing)
    trailing_payload["storage_sha256"] = volumetric_content_hash(trailing)
    _refresh_payload_layout(trailing_payload)
    assert "VOLUME_PAYLOAD_BYTE_MISMATCH" in validate_volumetric_payload(trailing_payload, {"values.bin": trailing}).errors
    chunked = build_chunked_payload(values, grid_shape=[2, 3, 4], stored_components=1, chunk_i=1)
    gap = deepcopy(chunked.metadata)
    gap["chunks"][1]["i_start"] = 0
    _refresh_payload_layout(gap)
    assert "VOLUME_CHUNK_GAP_OR_OVERLAP" in validate_volumetric_payload(gap, chunked.artifacts).errors


def test_payload_rejects_inline_and_chunk_aggregate_storage_hash_tampering() -> None:
    inline = build_inline_payload(
        [1.0, 2.0], grid_shape=[2, 1, 1], stored_components=1
    ).metadata
    broken_inline = deepcopy(inline)
    broken_inline["storage_sha256"] = "0" * 64
    _refresh_payload_layout(broken_inline)
    assert "VOLUME_PAYLOAD_HASH_MISMATCH" in validate_volumetric_payload(
        broken_inline
    ).errors

    chunked = build_chunked_payload(
        [1.0, 2.0],
        grid_shape=[2, 1, 1],
        stored_components=1,
        chunk_i=1,
    )
    broken_chunked = deepcopy(chunked.metadata)
    broken_chunked["storage_sha256"] = "0" * 64
    _refresh_payload_layout(broken_chunked)
    assert "VOLUME_PAYLOAD_HASH_MISMATCH" in validate_volumetric_payload(
        broken_chunked, chunked.artifacts
    ).errors


def test_compression_ratio_cap_blocks_bomb_like_constant_payload() -> None:
    values = [0.0] * 100_000
    with pytest.raises(VolumetricContractError) as error:
        build_binary_payload(values, grid_shape=[100, 100, 10], stored_components=1, encoding="gzip_binary", artifact_name="zeros.gz")
    assert error.value.code == "VOLUME_COMPRESSION_RATIO_EXCEEDED"


def test_real_vector_and_complex_scalar_component_semantics() -> None:
    grid = _periodic_grid([2, 2, 2])
    vectors = [float(index) for index in range(24)]
    vector_payload = build_inline_payload(vectors, grid_shape=grid["shape"], stored_components=3).metadata
    vector = _field(
        grid, vector_payload, vectors, field_name="magnetization", quantity="magnetization_density",
        unit="bohr_magneton/angstrom^3", field_rank="vector",
        spin={"representation": "non_collinear", "channel": "magnetization_vector", "component_basis": "cartesian", "sign_convention": "source declared", "source_convention": "synthetic Cartesian fixture"},
        integral_semantics="magnetic_moment",
    )
    assert vector["component_labels"] == ["x", "y", "z"]
    complex_values = [item for index in range(8) for item in (math.cos(index), math.sin(index))]
    complex_payload = build_inline_payload(complex_values, grid_shape=grid["shape"], stored_components=2).metadata
    complex_field = _field(
        grid, complex_payload, complex_values, field_name="psi", quantity="wavefunction", unit="angstrom^-3",
        value_kind="complex", field_rank="scalar", normalization_semantics="normalized_to_unit_integral",
        integral_semantics="not_physically_interpreted",
    )
    assert complex_field["component_labels"] == ["real", "imag"]
    assert complex_field["statistics"]["complex_magnitude"]["norm_integral"] == pytest.approx(64.0)


def test_collinear_spin_and_potential_reference_are_explicit() -> None:
    grid = _periodic_grid([2, 2, 2])
    values = [0.5] * 8
    payload = build_inline_payload(values, grid_shape=grid["shape"], stored_components=1).metadata
    spin = _field(
        grid, payload, values, quantity="spin_density", field_name="spin difference",
        spin={"representation": "collinear", "channel": "spin_difference", "component_basis": "not_applicable", "sign_convention": "up minus down", "source_convention": "synthetic fixture"},
    )
    assert spin["spin"]["channel"] == "spin_difference"
    potential = _field(
        grid, payload, values, quantity="electrostatic_potential", field_name="potential", unit="electronvolt",
        normalization_semantics="not_normalized", integral_semantics="cell_average",
        potential_reference={"kind": "cell_average_zero", "reference_value": 0.0, "reference_unit": "electronvolt", "shift_applied": False, "shift_amount": 0.0, "source_metadata": "synthetic gauge"},
    )
    assert potential["potential_reference"]["kind"] == "cell_average_zero"
    with pytest.raises(VolumetricContractError) as error:
        _field(grid, payload, values, quantity="electrostatic_potential", field_name="invalid potential", unit="electronvolt")
    assert error.value.code == "VOLUME_POTENTIAL_REFERENCE_INVALID"


@pytest.mark.parametrize(
    ("quantity", "unit"),
    [("electron_density", "volt"), ("charge_density", "electron/angstrom^3"), ("electron_localization_function", "electronvolt")],
)
def test_quantity_unit_mismatch_is_rejected(quantity: str, unit: str) -> None:
    grid = _periodic_grid([2, 2, 2])
    values = [1.0] * 8
    payload = build_inline_payload(values, grid_shape=grid["shape"], stored_components=1).metadata
    with pytest.raises(VolumetricContractError) as error:
        _field(grid, payload, values, quantity=quantity, unit=unit)
    assert error.value.code == "VOLUME_QUANTITY_UNIT_MISMATCH"


def test_dataset_relationship_manifest_and_isosurface_handoff() -> None:
    grid = _periodic_grid([2, 2, 2])
    values = [1.0] * 8
    bundle = build_binary_payload(values, grid_shape=grid["shape"], stored_components=1, artifact_name="density.bin")
    field = _field(grid, bundle.metadata, values)
    dataset = build_volumetric_dataset(grid=grid, payloads=[bundle.metadata], fields=[field], artifacts=bundle.artifacts)
    assert validate_volumetric_dataset(dataset, bundle.artifacts).valid
    manifest = build_volumetric_manifest(dataset, bundle.artifacts)
    assert validate_volumetric_manifest(manifest, dataset=dataset, artifacts=bundle.artifacts).valid
    assert manifest["capabilities"]["renderer_included"] is False
    assert manifest["external_resources"] == []
    compatible, reasons = is_isosurface_compatible(field, grid, bundle.metadata)
    assert compatible and reasons == ()


def test_manifest_detects_dataset_and_binary_hash_mismatch() -> None:
    grid = _periodic_grid([2, 2, 2])
    values = [1.0] * 8
    bundle = build_binary_payload(values, grid_shape=grid["shape"], stored_components=1, artifact_name="density.bin")
    field = _field(grid, bundle.metadata, values)
    dataset = build_volumetric_dataset(grid=grid, payloads=[bundle.metadata], fields=[field], artifacts=bundle.artifacts)
    manifest = build_volumetric_manifest(dataset, bundle.artifacts)
    assert "VOLUME_MANIFEST_REFERENCE_INVALID" in validate_volumetric_manifest(manifest, dataset=dataset, artifacts={"density.bin": b"bad"}).errors
    other = deepcopy(dataset)
    other["dataset_id"] = "volume-dataset:" + "0" * 64
    assert "VOLUME_MANIFEST_DATASET_MISMATCH" in validate_volumetric_manifest(manifest, dataset=other, artifacts=bundle.artifacts).errors
    duplicate = deepcopy(manifest)
    duplicate["artifacts"].append(deepcopy(duplicate["artifacts"][0]))
    duplicate["artifacts"].sort(key=lambda item: item["name"])
    identity = {
        key: duplicate[key]
        for key in duplicate
        if key not in {"manifest_id", "content_hash"}
    }
    duplicate["content_hash"] = volumetric_content_hash(identity)
    duplicate["manifest_id"] = f"volume-manifest:{duplicate['content_hash']}"
    assert "VOLUME_MANIFEST_REFERENCE_INVALID" in validate_volumetric_manifest(
        duplicate, dataset=dataset, artifacts=bundle.artifacts
    ).errors


def test_inert_metadata_and_path_traversal_are_rejected() -> None:
    with pytest.raises(VolumetricContractError) as error:
        build_binary_payload([1.0], grid_shape=[1, 1, 1], stored_components=1, artifact_name="../escape.bin")
    assert error.value.code == "VOLUME_ARTIFACT_NAME_INVALID"
    grid = _periodic_grid([1, 1, 1])
    values = [1.0]
    payload = build_inline_payload(values, grid_shape=grid["shape"], stored_components=1).metadata
    with pytest.raises(VolumetricContractError) as error:
        _field(
            grid, payload, values, quantity="custom_declared", unit="custom_declared", field_name="custom",
            custom_quantity={"identity": "custom", "display_name": "<script>alert(1)</script>", "value_semantics": "safe"},
        )
    assert error.value.code == "VOLUME_CUSTOM_QUANTITY_INVALID"


def test_stable_serialization_normalizes_negative_zero_and_replay() -> None:
    assert stable_volumetric_json({"b": -0.0, "a": [1.0]}) == '{"a":[1.0],"b":0.0}'
    grid = _periodic_grid()
    assert volumetric_content_hash(grid) == volumetric_content_hash(deepcopy(grid))
