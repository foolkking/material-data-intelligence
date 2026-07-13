from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path

import pytest

from mdi_artifact_core import (
    DEFAULT_TRAJECTORY_CAPS,
    TRAJECTORY_FRAME_SCHEMA_VERSION,
    TRAJECTORY_MANIFEST_SCHEMA_VERSION,
    TRAJECTORY_SCHEMA_VERSION,
    TRAJECTORY_SUMMARY_SCHEMA_VERSION,
    canonical_trajectory_id,
    stable_trajectory_json,
    trajectory_summary,
    validate_trajectory,
    validate_trajectory_manifest,
    validate_trajectory_summary,
)
from mdi_artifact_core import trajectory_contract as contract


ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "docs" / "phase10g" / "fixtures" / "trajectory_v1"
VALID = ("fixed_lattice_md.json", "variable_lattice_relaxation.json", "unwrapped_diffusion.json", "nonperiodic_sequence.json")


def load(name: str) -> dict:
    return json.loads((FIXTURES / name).read_text(encoding="utf-8"))


def reseal(payload: dict) -> dict:
    payload["trajectory_id"] = canonical_trajectory_id(payload)
    return payload


def mutate(name: str = "fixed_lattice_md.json") -> dict:
    return copy.deepcopy(load(name))


@pytest.mark.parametrize("name", VALID)
def test_reference_fixtures_validate(name: str) -> None:
    payload = load(name)
    result = validate_trajectory(payload)
    assert result.valid, result.errors
    assert payload["trajectory_id"] == canonical_trajectory_id(payload)


def test_expected_fixture_results_are_independent_and_complete() -> None:
    expected = load("expected_results.json")
    names = {path.name for path in FIXTURES.glob("*.json")} - {"expected_results.json"}
    assert set(expected) == names
    for name, result in expected.items():
        assert validate_trajectory(load(name)).as_dict() == result


@pytest.mark.parametrize(
    ("name", "error"),
    (("invalid_atom_count.json", "TRAJECTORY_POSITION_SHAPE_INVALID"), ("invalid_species_reorder.json", "TRAJECTORY_SPECIES_MISMATCH"), ("invalid_lattice.json", "TRAJECTORY_LATTICE_SINGULAR"), ("invalid_time.json", "TRAJECTORY_TIME_NONMONOTONIC")),
)
def test_invalid_fixtures_have_typed_errors(name: str, error: str) -> None:
    result = validate_trajectory(load(name))
    assert not result.valid
    assert error in result.errors


def test_schema_and_enum_fields_are_closed() -> None:
    payload = mutate()
    payload["unknown"] = "value"
    assert "TRAJECTORY_TOP_LEVEL_FIELDS_INVALID" in validate_trajectory(reseal(payload)).errors
    for field, value, error in (
        ("schema_version", "future", "TRAJECTORY_SCHEMA_UNSUPPORTED"),
        ("kind", "reaction", "TRAJECTORY_KIND_UNSUPPORTED"),
        ("coordinate_mode", "mixed", "TRAJECTORY_COORDINATE_MODE_INVALID"),
        ("position_wrapping", "guess", "TRAJECTORY_POSITION_WRAPPING_INVALID"),
        ("lattice_mode", "implicit", "TRAJECTORY_LATTICE_MODE_INVALID"),
    ):
        candidate = mutate(); candidate[field] = value
        assert error in validate_trajectory(reseal(candidate)).errors


def test_atom_identity_is_stable_and_partial_occupancy_is_rejected() -> None:
    payload = mutate(); payload["atoms"]["records"][1]["atom_id"] = 0
    assert "TRAJECTORY_ATOM_ID_INVALID" in validate_trajectory(reseal(payload)).errors
    payload = mutate(); payload["atoms"]["records"][1]["label"] = "Si1"
    assert "TRAJECTORY_LABEL_DUPLICATE" in validate_trajectory(reseal(payload)).errors
    payload = mutate(); payload["atoms"]["records"][0]["occupancy"] = 0.5
    assert "TRAJECTORY_PARTIAL_OCCUPANCY_UNSUPPORTED" in validate_trajectory(reseal(payload)).errors


def test_frame_indices_must_be_contiguous_and_unique() -> None:
    payload = mutate(); payload["frames"][1]["frame_index"] = 0
    errors = validate_trajectory(reseal(payload)).errors
    assert "TRAJECTORY_FRAME_INDEX_INVALID" in errors
    assert "TRAJECTORY_FRAME_INDEX_DUPLICATE" in errors
    payload = mutate(); payload["frames"] = []
    assert "TRAJECTORY_EMPTY" in validate_trajectory(reseal(payload)).errors


def test_wrapped_and_unwrapped_coordinates_preserve_semantics() -> None:
    payload = mutate(); payload["frames"][0]["positions"][0][0] = 1.01
    assert "TRAJECTORY_WRAPPED_POSITION_OUT_OF_RANGE" in validate_trajectory(reseal(payload)).errors
    unwrapped = load("unwrapped_diffusion.json")
    assert unwrapped["frames"][-1]["positions"][0][0] == 1.25
    assert validate_trajectory(unwrapped).valid


def test_fixed_variable_and_triclinic_lattices() -> None:
    fixed = mutate(); fixed["frames"][0]["lattice"] = fixed["fixed_lattice"]
    assert "TRAJECTORY_LATTICE_UNEXPECTED" in validate_trajectory(reseal(fixed)).errors
    variable = mutate("variable_lattice_relaxation.json"); variable["frames"][0]["lattice"] = None
    assert "TRAJECTORY_LATTICE_REQUIRED" in validate_trajectory(reseal(variable)).errors
    triclinic = load("variable_lattice_relaxation.json")
    assert validate_trajectory(triclinic).valid
    ill = mutate(); ill["fixed_lattice"] = [[1.0, 0.0, 0.0], [0.0, 1e-9, 0.0], [0.0, 0.0, 1e-9]]
    assert set(validate_trajectory(reseal(ill)).errors) & {"TRAJECTORY_LATTICE_SINGULAR", "TRAJECTORY_LATTICE_ILL_CONDITIONED"}


def test_time_step_and_kind_policies() -> None:
    payload = mutate(); payload["frames"][1]["time"] = None
    assert "TRAJECTORY_TIME_MISSING" in validate_trajectory(reseal(payload)).errors
    payload = mutate(); payload["time"]["unit"] = "second"
    assert "TRAJECTORY_TIME_UNIT_UNSUPPORTED" in validate_trajectory(reseal(payload)).errors
    payload = mutate(); payload["frames"][2]["step"] = 1
    assert "TRAJECTORY_STEP_NONMONOTONIC" in validate_trajectory(reseal(payload)).errors
    optimization = load("variable_lattice_relaxation.json")
    assert all(item["time"] is None for item in optimization["frames"])
    assert validate_trajectory(optimization).valid


def test_optional_properties_are_strict_and_units_are_canonical() -> None:
    payload = mutate(); payload["frames"][1]["velocities"] = None
    assert "TRAJECTORY_PROPERTY_AVAILABILITY_INCONSISTENT" in validate_trajectory(reseal(payload)).errors
    payload = mutate("variable_lattice_relaxation.json"); payload["frames"][0]["energy"]["scope"] = "per_atom"
    assert "TRAJECTORY_ENERGY_INVALID" in validate_trajectory(reseal(payload)).errors
    payload = mutate(); payload["properties"]["stress"] = True
    assert "TRAJECTORY_STRESS_DEFERRED" in validate_trajectory(reseal(payload)).errors
    payload = mutate(); payload["units"]["forces"] = "newton"
    assert "TRAJECTORY_UNITS_INVALID" in validate_trajectory(reseal(payload)).errors


def test_caps_and_overflow_preflight_do_not_require_large_payloads() -> None:
    payload = mutate()
    result = validate_trajectory(payload, raw_size_bytes=DEFAULT_TRAJECTORY_CAPS["max_json_bytes"] + 1)
    assert "TRAJECTORY_BYTE_LIMIT_EXCEEDED" in result.errors
    assert contract._product_exceeds(10_000, 4096, 3, DEFAULT_TRAJECTORY_CAPS["max_total_coordinate_values"])
    assert not contract._product_exceeds(10, 10, 3, DEFAULT_TRAJECTORY_CAPS["max_total_coordinate_values"])


def test_security_rejects_executable_urls_paths_and_nested_metadata() -> None:
    for field, value, error in (
        ("callback", "run", "TRAJECTORY_EXECUTABLE_FIELD_FORBIDDEN"),
        ("note", "javascript:run", "TRAJECTORY_EXTERNAL_REFERENCE_FORBIDDEN"),
        ("note", "C:\\private\\trajectory.xyz", "TRAJECTORY_PRIVATE_PATH_FORBIDDEN"),
    ):
        payload = mutate(); payload["metadata"][field] = value
        assert error in validate_trajectory(reseal(payload)).errors
    payload = mutate(); payload["metadata"]["nested"] = {"deep": {"value": 1}}
    assert "TRAJECTORY_METADATA_INVALID" in validate_trajectory(reseal(payload)).errors


def test_security_handles_deep_and_nonfinite_payloads_without_throwing() -> None:
    payload = mutate()
    nested: dict = {}
    cursor = nested
    for _ in range(20):
        cursor["nested"] = {}
        cursor = cursor["nested"]
    payload["metadata"]["nested"] = nested
    result = validate_trajectory(payload, raw_size_bytes=100)
    assert not result.valid
    assert "TRAJECTORY_NESTING_LIMIT_EXCEEDED" in result.errors
    payload = mutate(); payload["frames"][0]["positions"][0][0] = float("nan")
    result = validate_trajectory(payload, raw_size_bytes=100)
    assert not result.valid
    assert "TRAJECTORY_ID_INVALID" in result.errors


def test_lattice_magnitude_is_rejected_before_matrix_arithmetic() -> None:
    payload = mutate(); payload["fixed_lattice"][0][0] = 1e100
    assert "TRAJECTORY_LATTICE_MAGNITUDE_EXCEEDED" in validate_trajectory(reseal(payload)).errors


def test_warning_order_and_identity_are_canonical() -> None:
    payload = mutate("variable_lattice_relaxation.json")
    payload["warnings"] = list(reversed(payload["warnings"]))
    assert "TRAJECTORY_WARNING_INVALID" in validate_trajectory(reseal(payload)).errors
    original = load("fixed_lattice_md.json")
    assert stable_trajectory_json(original) == stable_trajectory_json(copy.deepcopy(original))
    assert hashlib.sha256(stable_trajectory_json(original).encode()).hexdigest() == hashlib.sha256(stable_trajectory_json(copy.deepcopy(original)).encode()).hexdigest()


def test_summary_and_manifest_are_small_inert_and_valid() -> None:
    payload = load("fixed_lattice_md.json")
    summary = trajectory_summary(payload)
    assert "frames" in summary and "positions" not in summary
    assert validate_trajectory_summary(summary).valid
    trajectory_bytes = stable_trajectory_json(payload).encode()
    summary_bytes = stable_trajectory_json(summary).encode()
    manifest = {
        "schema_version": TRAJECTORY_MANIFEST_SCHEMA_VERSION,
        "trajectory_schema_version": TRAJECTORY_SCHEMA_VERSION,
        "frame_schema_version": TRAJECTORY_FRAME_SCHEMA_VERSION,
        "summary_schema_version": TRAJECTORY_SUMMARY_SCHEMA_VERSION,
        "trajectory_id": payload["trajectory_id"],
        "frame_count": 4,
        "atom_count": 2,
        "artifacts": [
            {"name": "trajectory.json", "media_type": "application/json", "bytes": len(trajectory_bytes), "sha256": hashlib.sha256(trajectory_bytes).hexdigest()},
            {"name": "trajectory_summary.json", "media_type": "application/json", "bytes": len(summary_bytes), "sha256": hashlib.sha256(summary_bytes).hexdigest()},
        ],
        "security": {"contains_javascript": False, "contains_html": False, "external_urls_allowed": False, "remote_frames_allowed": False, "executable_content_allowed": False},
    }
    assert validate_trajectory_manifest(manifest).valid
    manifest["artifacts"].reverse()
    assert "TRAJECTORY_MANIFEST_ARTIFACT_ORDER_INVALID" in validate_trajectory_manifest(manifest).errors
