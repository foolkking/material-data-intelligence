from __future__ import annotations

import copy
import hashlib
import json
import math
from pathlib import Path

import numpy as np
import pytest
from scipy import constants

from mdi_artifact_core import (
    DEFAULT_PHONON_CAPS,
    PHONON_BAND_SCHEMA_VERSION,
    PHONON_DOS_SCHEMA_VERSION,
    PHONON_MANIFEST_SCHEMA_VERSION,
    PHONON_SUMMARY_SCHEMA_VERSION,
    classify_frequency,
    convert_frequency,
    normalize_high_symmetry_label,
    phonon_content_hash,
    phonon_schema_snapshots,
    phonon_summary,
    reciprocal_fractional_to_cartesian,
    reciprocal_lattice_physics_2pi,
    reciprocal_path_step,
    stable_phonon_json,
    trapezoidal_integral,
    validate_band_dos_compatibility,
    validate_phonon_band,
    validate_phonon_dos,
    validate_phonon_manifest,
    validate_phonon_summary,
)


STRUCTURE_ID = "a" * 64
INPUT_HASH = "b" * 64
ROOT = Path(__file__).resolve().parents[1]


def security() -> dict[str, object]:
    return {
        "contains_javascript": False,
        "contains_html": False,
        "external_urls_allowed": False,
        "executable_content_allowed": False,
        "external_assets": [],
    }


def source(*, nac: bool = False) -> dict[str, object]:
    return {
        "producer": "fixture",
        "producer_version": "1.0",
        "calculation_method": "finite_displacement",
        "force_constants_source": "force_constants",
        "supercell_matrix": [[2, 0, 0], [0, 2, 0], [0, 0, 2]],
        "primitive_matrix": [[1, 0, 0], [0, 1, 0], [0, 0, 1]],
        "nac": {
            "enabled": nac,
            "gamma_direction": [1.0, 0.0, 0.0] if nac else None,
            "direction_policy": "explicit" if nac else None,
        },
        "input_sha256": INPUT_HASH,
        "adapter_version": "phase10h-fixture-v1",
    }


def valid_band(*, lattice: list[list[float]] | None = None) -> dict[str, object]:
    lattice = lattice or [[5.43, 0.0, 0.0], [0.0, 5.43, 0.0], [0.0, 0.0, 5.43]]
    coordinates = [[0.0, 0.0, 0.0], [0.5, 0.0, 0.0], [0.5, 0.5, 0.5]]
    distances = [0.0]
    for start, end in zip(coordinates[:-1], coordinates[1:], strict=True):
        distances.append(distances[-1] + reciprocal_path_step(start, end, lattice))
    return {
        "schema_version": PHONON_BAND_SCHEMA_VERSION,
        "structure_identity": STRUCTURE_ID,
        "atom_count": 2,
        "species": ["Si", "Si"],
        "atom_ordering": "canonical_structure_order",
        "real_space_lattice_angstrom": lattice,
        "reciprocal_convention": "physics_2pi",
        "qpoint_coordinate_system": "reciprocal_fractional",
        "path_distance_unit": "radian_per_angstrom",
        "frequency_unit": "terahertz",
        "imaginary_frequency_encoding": "negative_real",
        "frequency_zero_tolerance": 1e-6,
        "branch_scope": "full",
        "qpoints": [
            {"index": 0, "coordinates": coordinates[0], "label": "Γ", "source_label": "GAMMA", "segment_index": 0, "distance": distances[0]},
            {"index": 1, "coordinates": coordinates[1], "label": "X", "source_label": "X", "segment_index": 0, "distance": distances[1]},
            {"index": 2, "coordinates": coordinates[2], "label": "L", "source_label": "L", "segment_index": 0, "distance": distances[2]},
        ],
        "segments": [
            {"segment_index": 0, "start_qpoint_index": 0, "end_qpoint_index": 2, "start_label": "Γ", "end_label": "L", "discontinuous_from_previous": False},
        ],
        "branches": [
            {"branch_index": 0, "frequencies": [0.0, 1.0, 1.5]},
            {"branch_index": 1, "frequencies": [0.0, 1.0, 1.6]},
            {"branch_index": 2, "frequencies": [0.0, 1.2, 1.7]},
            {"branch_index": 3, "frequencies": [4.0, 4.4, 4.8]},
            {"branch_index": 4, "frequencies": [4.0, 4.5, 4.9]},
            {"branch_index": 5, "frequencies": [4.2, 4.6, 5.0]},
        ],
        "degeneracy_groups": [
            {"qpoint_index": 0, "branch_indices": [0, 1, 2], "source": "producer"},
            {"qpoint_index": 0, "branch_indices": [3, 4], "source": "producer"},
        ],
        "acoustic_sum_rule": {"applied": False, "method": None},
        "source": source(),
        "warnings": [],
        "security": security(),
    }


def discontinuous_band() -> dict[str, object]:
    band = valid_band()
    qpoints = band["qpoints"]
    assert isinstance(qpoints, list)
    boundary_distance = qpoints[-1]["distance"]
    qpoints.extend(
        [
            {"index": 3, "coordinates": [0.0, 0.0, 0.0], "label": "Γ", "source_label": "Gamma", "segment_index": 1, "distance": boundary_distance},
            {"index": 4, "coordinates": [0.0, 0.5, 0.0], "label": "M", "source_label": "M", "segment_index": 1, "distance": boundary_distance + math.pi / 5.43},
        ]
    )
    band["segments"] = [
        {"segment_index": 0, "start_qpoint_index": 0, "end_qpoint_index": 2, "start_label": "Γ", "end_label": "L", "discontinuous_from_previous": False},
        {"segment_index": 1, "start_qpoint_index": 3, "end_qpoint_index": 4, "start_label": "Γ", "end_label": "M", "discontinuous_from_previous": True},
    ]
    for branch in band["branches"]:
        branch["frequencies"].extend([branch["frequencies"][0], branch["frequencies"][1]])
    return band


def valid_dos() -> dict[str, object]:
    frequencies = [-1.0, 0.0, 1.0, 2.0, 3.0, 4.0, 5.0]
    total = [1.0] * len(frequencies)
    return {
        "schema_version": PHONON_DOS_SCHEMA_VERSION,
        "structure_identity": STRUCTURE_ID,
        "atom_count": 2,
        "species": ["Si", "Si"],
        "atom_ordering": "canonical_structure_order",
        "frequency_unit": "terahertz",
        "imaginary_frequency_encoding": "negative_real",
        "frequency_zero_tolerance": 1e-6,
        "density_unit": "modes_per_terahertz",
        "normalization": "total_modes",
        "frequency_grid_semantics": "sample_grid_points",
        "frequencies": frequencies,
        "total_dos": total,
        "projected_dos": [
            {"projection_index": 0, "projection_type": "atom", "atom_index": 0, "species": "Si", "values": [0.5] * len(frequencies), "source_guarantees_sum": True},
            {"projection_index": 1, "projection_type": "atom", "atom_index": 1, "species": "Si", "values": [0.5] * len(frequencies), "source_guarantees_sum": True},
        ],
        "broadening": {"method": "none", "width": None, "unit": None, "source": "fixture"},
        "integration": {"method": "trapezoidal", "expected_mode_count": 6, "observed_integral": 6.0, "relative_tolerance": 0.01, "status": "within_tolerance"},
        "source": source(),
        "warnings": [],
        "security": security(),
    }


def test_valid_band_dos_summary_manifest_and_schema_snapshots() -> None:
    band = valid_band()
    dos = valid_dos()
    band_result = validate_phonon_band(band)
    dos_result = validate_phonon_dos(dos)
    assert band_result.valid, band_result.as_dict()
    assert dos_result.valid, dos_result.as_dict()
    assert band_result.atom_count == 2
    assert band_result.branch_count == 6
    assert band_result.qpoint_count == 3
    assert dos_result.dos_point_count == 7
    assert dos_result.projected_series_count == 2
    assert validate_band_dos_compatibility(band, dos).status == "compatible"

    summary = phonon_summary(band, dos)
    assert validate_phonon_summary(summary).valid
    artifacts = []
    for name, schema, value in (
        ("phonon_band.json", PHONON_BAND_SCHEMA_VERSION, band),
        ("phonon_dos.json", PHONON_DOS_SCHEMA_VERSION, dos),
        ("phonon_summary.json", PHONON_SUMMARY_SCHEMA_VERSION, summary),
    ):
        encoded = stable_phonon_json(value).encode()
        artifacts.append({"name": name, "schema_version": schema, "media_type": "application/json", "size_bytes": len(encoded), "sha256": hashlib.sha256(encoded).hexdigest()})
    manifest = {
        "schema_version": PHONON_MANIFEST_SCHEMA_VERSION,
        "structure_identity": STRUCTURE_ID,
        "band_schema_version": PHONON_BAND_SCHEMA_VERSION,
        "dos_schema_version": PHONON_DOS_SCHEMA_VERSION,
        "summary_schema_version": PHONON_SUMMARY_SCHEMA_VERSION,
        "artifacts": artifacts,
        "security": security(),
    }
    assert validate_phonon_manifest(manifest).valid
    assert set(phonon_schema_snapshots()) == {"band", "dos", "summary", "manifest"}


def test_reciprocal_lattice_row_vector_and_triclinic_reference() -> None:
    lattice = [[4.1, 0.0, 0.0], [1.2, 3.8, 0.0], [0.4, 0.7, 5.2]]
    expected = 2.0 * np.pi * np.linalg.inv(np.asarray(lattice)).T
    actual = np.asarray(reciprocal_lattice_physics_2pi(lattice))
    assert np.allclose(actual, expected, rtol=1e-13, atol=1e-13)
    fractional = np.asarray([0.13, 0.27, 0.41])
    assert np.allclose(reciprocal_fractional_to_cartesian(fractional.tolist(), lattice), fractional @ expected)
    assert reciprocal_path_step([0, 0, 0], fractional.tolist(), lattice) == pytest.approx(np.linalg.norm(fractional @ expected), rel=1e-13)


def test_reciprocal_lattice_rejects_singular_and_ill_conditioned() -> None:
    with pytest.raises(ValueError, match="PHONON_RECIPROCAL_CONVENTION_UNSUPPORTED"):
        reciprocal_lattice_physics_2pi([[1, 0, 0], [2, 0, 0], [0, 0, 1]])
    band = valid_band()
    band["real_space_lattice_angstrom"] = [[1, 0, 0], [2, 0, 0], [0, 0, 1]]
    assert "PHONON_RECIPROCAL_CONVENTION_UNSUPPORTED" in validate_phonon_band(band).errors


def test_frequency_conversion_uses_independent_scipy_constants() -> None:
    expected_cm = 1e12 / (constants.c * 100.0)
    expected_mev = constants.h * 1e12 / constants.e * 1000.0
    assert convert_frequency(1, "terahertz", "inverse_centimeter") == pytest.approx(expected_cm, rel=1e-15)
    assert convert_frequency(1, "terahertz", "millielectronvolt") == pytest.approx(expected_mev, rel=1e-15)
    assert convert_frequency(expected_cm, "inverse_centimeter", "terahertz") == pytest.approx(1.0)
    assert convert_frequency(expected_mev, "millielectronvolt", "terahertz") == pytest.approx(1.0)
    with pytest.raises(ValueError, match="PHONON_FREQUENCY_UNIT_UNSUPPORTED"):
        convert_frequency(1, "radian_per_second", "terahertz")


@pytest.mark.parametrize(
    ("value", "expected"),
    [(-0.1, "imaginary"), (-1e-7, "near_zero"), (0.0, "near_zero"), (1e-7, "near_zero"), (0.1, "real")],
)
def test_frequency_classification_preserves_negative_real(value: float, expected: str) -> None:
    assert classify_frequency(value, 1e-6) == expected


def test_label_normalization_and_discontinuous_path() -> None:
    assert normalize_high_symmetry_label("GAMMA") == "Γ"
    assert normalize_high_symmetry_label("Gamma") == "Γ"
    assert normalize_high_symmetry_label("\\Gamma") == "Γ"
    result = validate_phonon_band(discontinuous_band())
    assert result.valid, result.as_dict()
    assert "PHONON_HIGH_SYMMETRY_LABEL_NORMALIZED" in result.warnings


@pytest.mark.parametrize(
    ("mutation", "error"),
    [
        (lambda payload: payload.update(schema_version="bad"), "PHONON_SCHEMA_UNSUPPORTED"),
        (lambda payload: payload.update(structure_identity="bad"), "PHONON_STRUCTURE_IDENTITY_REQUIRED"),
        (lambda payload: payload["qpoints"][0].update(coordinates=[0, 0]), "PHONON_QPOINT_SHAPE_INVALID"),
        (lambda payload: payload["qpoints"][1].update(index=4), "PHONON_QPOINT_INDEX_INVALID"),
        (lambda payload: payload["qpoints"][2].update(distance=0.0), "PHONON_QPOINT_DISTANCE_NONMONOTONIC"),
        (lambda payload: payload["qpoints"][0].update(label="<b>G</b>"), "PHONON_PATH_LABEL_INVALID"),
        (lambda payload: payload.update(frequency_unit="radian_per_second"), "PHONON_FREQUENCY_UNIT_UNSUPPORTED"),
        (lambda payload: payload["branches"][0].update(frequencies=[0.0]), "PHONON_FREQUENCY_SHAPE_INVALID"),
        (lambda payload: payload["branches"][0].update(branch_index=2), "PHONON_BRANCH_INDEX_INVALID"),
        (lambda payload: payload["branches"].pop(), "PHONON_BRANCH_COUNT_MISMATCH"),
        (lambda payload: payload["degeneracy_groups"][0].update(branch_indices=[0, 0]), "PHONON_DEGENERACY_GROUP_INVALID"),
    ],
)
def test_band_validation_errors(mutation, error: str) -> None:
    payload = valid_band()
    mutation(payload)
    assert error in validate_phonon_band(payload).errors


def test_band_nonfinite_is_rejected_without_serialization_crash() -> None:
    payload = valid_band()
    payload["branches"][0]["frequencies"][1] = math.nan
    result = validate_phonon_band(payload, raw_size_bytes=100)
    assert "PHONON_FREQUENCY_NONFINITE" in result.errors


def test_degeneracy_groups_cannot_overlap_or_reorder() -> None:
    payload = valid_band()
    payload["degeneracy_groups"].append({"qpoint_index": 0, "branch_indices": [2, 5], "source": "producer"})
    assert "PHONON_DEGENERACY_GROUP_INVALID" in validate_phonon_band(payload).errors
    payload = valid_band()
    payload["degeneracy_groups"].reverse()
    assert "PHONON_DEGENERACY_GROUP_INVALID" in validate_phonon_band(payload).errors


def test_dos_grid_integral_negative_region_and_projection_identity() -> None:
    dos = valid_dos()
    assert trapezoidal_integral(dos["frequencies"], dos["total_dos"]) == pytest.approx(6.0)
    assert any(value < 0 for value in dos["frequencies"])
    assert validate_phonon_dos(dos).valid
    dos["frequencies"][2] = 0.0
    assert "PHONON_DOS_GRID_INVALID" in validate_phonon_dos(dos).errors


@pytest.mark.parametrize(
    ("mutation", "error"),
    [
        (lambda payload: payload["total_dos"].pop(), "PHONON_DOS_SHAPE_INVALID"),
        (lambda payload: payload["total_dos"].__setitem__(0, math.inf), "PHONON_DOS_NONFINITE"),
        (lambda payload: payload.update(normalization="unit_area"), "PHONON_DOS_NORMALIZATION_UNSUPPORTED"),
        (lambda payload: payload["integration"].update(observed_integral=5.0), "PHONON_DOS_INTEGRAL_MISMATCH"),
        (lambda payload: payload["projected_dos"][0].update(atom_index=3), "PHONON_PROJECTED_DOS_IDENTITY_INVALID"),
        (lambda payload: payload["projected_dos"][1].update(atom_index=0), "PHONON_PROJECTED_DOS_DUPLICATE"),
        (lambda payload: payload["projected_dos"][0]["values"].pop(), "PHONON_DOS_SHAPE_INVALID"),
    ],
)
def test_dos_validation_errors(mutation, error: str) -> None:
    payload = valid_dos()
    mutation(payload)
    assert error in validate_phonon_dos(payload, raw_size_bytes=1000).errors


def test_projected_sum_mismatch_is_warning_not_inference() -> None:
    payload = valid_dos()
    payload["projected_dos"][0]["values"][0] = 0.25
    result = validate_phonon_dos(payload)
    assert result.valid
    assert "PHONON_PROJECTED_DOS_SUM_MISMATCH" in result.warnings


def test_band_dos_compatibility_statuses() -> None:
    band, dos = valid_band(), valid_dos()
    assert validate_band_dos_compatibility(band, dos).as_dict() == {"status": "compatible", "reasons": []}
    converted = copy.deepcopy(dos)
    converted["frequency_unit"] = "inverse_centimeter"
    converted["frequencies"] = [convert_frequency(value, "terahertz", "inverse_centimeter") for value in converted["frequencies"]]
    assert validate_band_dos_compatibility(band, converted).status == "convertible"
    mismatch = copy.deepcopy(dos)
    mismatch["structure_identity"] = "c" * 64
    result = validate_band_dos_compatibility(band, mismatch)
    assert result.status == "incompatible"
    assert result.reasons == ("PHONON_BAND_DOS_STRUCTURE_MISMATCH",)
    mismatch = copy.deepcopy(dos)
    mismatch["source"]["nac"] = source(nac=True)["nac"]
    assert "PHONON_BAND_DOS_SOURCE_INCOMPATIBLE" in validate_band_dos_compatibility(band, mismatch).reasons


def test_caps_preflight_and_raw_byte_limit() -> None:
    payload = valid_band()
    payload["qpoints"] = payload["qpoints"] * (DEFAULT_PHONON_CAPS["max_qpoints"] // 3 + 1)
    assert "PHONON_CAP_EXCEEDED" in validate_phonon_band(payload, raw_size_bytes=1).errors
    assert "PHONON_CAP_EXCEEDED" in validate_phonon_band(valid_band(), raw_size_bytes=DEFAULT_PHONON_CAPS["max_artifact_bytes"] + 1).errors
    dos = valid_dos()
    dos["projected_dos"] = dos["projected_dos"] * (DEFAULT_PHONON_CAPS["max_projected_dos_series"] // 2 + 1)
    assert "PHONON_CAP_EXCEEDED" in validate_phonon_dos(dos, raw_size_bytes=1).errors


def test_projected_dos_order_and_nac_metadata_are_strict() -> None:
    dos = valid_dos()
    dos["projected_dos"].reverse()
    dos["projected_dos"][0]["projection_index"] = 0
    dos["projected_dos"][1]["projection_index"] = 1
    assert "PHONON_PROJECTED_DOS_IDENTITY_INVALID" in validate_phonon_dos(dos).errors
    band = valid_band()
    band["source"]["nac"]["gamma_direction"] = [1.0, 0.0, 0.0]
    assert "PHONON_METADATA_LIMIT_EXCEEDED" in validate_phonon_band(band).errors


@pytest.mark.parametrize(
    "attack",
    [
        {"callback": "run"},
        {"note": "<script>alert(1)</script>"},
        {"note": "javascript:alert(1)"},
        {"note": "https://example.invalid/data"},
        {"note": "C:\\private\\phonon.yaml"},
        {"shader": "void main()"},
        {"module": "external"},
        {"__proto__": {"polluted": True}},
    ],
)
def test_security_rejects_executable_external_and_private_content(attack: dict[str, object]) -> None:
    payload = valid_band()
    payload["source"] = {**payload["source"], **attack}
    result = validate_phonon_band(payload, raw_size_bytes=1000)
    assert "PHONON_EXTERNAL_REFERENCE_FORBIDDEN" in result.errors or "PHONON_METADATA_LIMIT_EXCEEDED" in result.errors


def test_exact_fields_and_security_flags_are_closed() -> None:
    payload = valid_band()
    payload["arbitrary_metadata"] = "x"
    assert "PHONON_SCHEMA_UNSUPPORTED" in validate_phonon_band(payload).errors
    payload = valid_dos()
    payload["security"]["external_urls_allowed"] = True
    assert "PHONON_EXTERNAL_REFERENCE_FORBIDDEN" in validate_phonon_dos(payload).errors


def test_serialization_hash_is_deterministic_and_input_is_immutable() -> None:
    payload = valid_band()
    original = copy.deepcopy(payload)
    first = stable_phonon_json(payload)
    second = stable_phonon_json(json.loads(first))
    assert first == second
    assert phonon_content_hash(payload) == hashlib.sha256(first.encode()).hexdigest()
    assert payload == original
    assert "\\u0393" in first


@pytest.mark.parametrize(
    "mutation",
    [
        lambda payload: payload["qpoints"].__setitem__(0, None),
        lambda payload: payload["segments"].__setitem__(0, None),
        lambda payload: payload["branches"].__setitem__(0, None),
        lambda payload: payload.update(source=[]),
        lambda payload: payload.update(security=[]),
        lambda payload: payload.update(species=None),
    ],
)
def test_band_validator_never_raises_for_malformed_nested_values(mutation) -> None:
    payload = valid_band()
    mutation(payload)
    assert not validate_phonon_band(payload, raw_size_bytes=1000).valid


def test_summary_and_manifest_never_raise_for_malformed_nested_values() -> None:
    summary = phonon_summary(valid_band(), valid_dos())
    summary["atom_count"] = None
    assert not validate_phonon_summary(summary).valid
    manifest = {
        "schema_version": PHONON_MANIFEST_SCHEMA_VERSION,
        "structure_identity": STRUCTURE_ID,
        "band_schema_version": PHONON_BAND_SCHEMA_VERSION,
        "dos_schema_version": None,
        "summary_schema_version": PHONON_SUMMARY_SCHEMA_VERSION,
        "artifacts": [None, 7],
        "security": security(),
    }
    assert not validate_phonon_manifest(manifest).valid


def test_committed_fixtures_and_evidence_are_current() -> None:
    fixture_dir = ROOT / "docs" / "phase10h" / "fixtures" / "phonon_contract"
    evidence_dir = ROOT / "docs" / "phase10h" / "evidence" / "phase10h_phonon_contract"
    for name in ("stable_band.json", "imaginary_band.json", "discontinuous_band.json"):
        assert validate_phonon_band(json.loads((fixture_dir / name).read_text(encoding="utf-8"))).valid
    for name in ("total_dos.json", "imaginary_dos.json", "projected_dos.json"):
        assert validate_phonon_dos(json.loads((fixture_dir / name).read_text(encoding="utf-8"))).valid
    assert not validate_phonon_band(json.loads((fixture_dir / "invalid_branch_count.json").read_text(encoding="utf-8"))).valid
    assert not validate_phonon_dos(json.loads((fixture_dir / "invalid_dos_grid.json").read_text(encoding="utf-8"))).valid
    assert validate_phonon_summary(json.loads((fixture_dir / "phonon_summary.json").read_text(encoding="utf-8"))).valid
    assert validate_phonon_manifest(json.loads((fixture_dir / "phonon_manifest.json").read_text(encoding="utf-8"))).valid

    inventory = json.loads((evidence_dir / "artifact_hashes.json").read_text(encoding="utf-8"))
    expected = {item["path"]: item for item in inventory["files"]}
    actual_paths = sorted(path for path in evidence_dir.rglob("*") if path.is_file() and path.name != "artifact_hashes.json")
    assert sorted(path.relative_to(evidence_dir).as_posix() for path in actual_paths) == sorted(expected)
    for path in actual_paths:
        relative = path.relative_to(evidence_dir).as_posix()
        data = path.read_bytes()
        if path.suffix.lower() in {".json", ".md"}:
            data = data.replace(b"\r\n", b"\n").replace(b"\r", b"\n")
        assert len(data) == expected[relative]["bytes"]
        assert hashlib.sha256(data).hexdigest() == expected[relative]["sha256"]
