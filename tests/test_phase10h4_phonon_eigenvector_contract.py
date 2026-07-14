from __future__ import annotations

import copy
import json
import math
from pathlib import Path

import numpy as np
import pytest

from mdi_artifact_core import (
    EIGENVECTOR_CAPS,
    MODE_FREQUENCY_TOLERANCE,
    PHONON_EIGENVECTOR_MANIFEST_SCHEMA_VERSION,
    PHONON_EIGENVECTOR_SCHEMA_VERSION,
    PHONON_EIGENVECTOR_SET_SCHEMA_VERSION,
    PHONON_EIGENVECTOR_SUMMARY_SCHEMA_VERSION,
    PhononEigenvectorContractError,
    build_phonon_eigenvector,
    build_phonon_eigenvector_set,
    build_phonon_mode_ref,
    canonicalize_global_phase,
    eigenvector_content_hash,
    mass_unweighted_vectors,
    phonon_eigenvector_manifest,
    phonon_eigenvector_schema_snapshots,
    phonon_eigenvector_summary,
    reconstruct_display_displacements,
    scientific_phase_equivalent,
    validate_phonon_eigenvector,
    validate_phonon_eigenvector_manifest,
    validate_phonon_eigenvector_set,
    validate_phonon_eigenvector_summary,
    validate_phonon_mode_ref,
)


ROOT = Path(__file__).resolve().parents[1]
BAND = ROOT / "docs/phase10h/fixtures/phonon_contract/stable_band.json"


def band() -> dict[str, object]:
    return json.loads(BAND.read_text(encoding="utf-8"))


def mode(source: dict[str, object] | None = None, qpoint: int = 0, branch: int = 3) -> dict[str, object]:
    source = source or band()
    return build_phonon_mode_ref(source, artifact_id="band-artifact", qpoint_index=qpoint, branch_index=branch)


def vector(source: dict[str, object] | None = None, qpoint: int = 0, branch: int = 3) -> dict[str, object]:
    source = source or band()
    return build_phonon_eigenvector(
        source,
        mode(source, qpoint, branch),
        [[1 + 1j, 0j, 0j], [-1 - 1j, 0j, 0j]],
        [28.085, 28.085],
    )


def test_mode_reference_is_content_bound_and_validates_against_band() -> None:
    source = band()
    value = mode(source)
    assert validate_phonon_mode_ref(value, source).valid
    assert value["frequency"] == source["branches"][3]["frequencies"][0]
    assert value["frequency_tolerance"] == MODE_FREQUENCY_TOLERANCE
    assert value["mode_id"] == build_phonon_mode_ref(source, artifact_id="band-artifact", qpoint_index=0, branch_index=3)["mode_id"]


def test_mode_reference_rejects_stale_artifact_qpoint_branch_and_frequency() -> None:
    source = band()
    for field, replacement, code in (
        ("mode_id", "f" * 64, "PHONON_MODE_REFERENCE_STALE"),
        ("qpoint_coordinates", [0.1, 0.0, 0.0], "PHONON_MODE_QPOINT_MISMATCH"),
        ("frequency", 99.0, "PHONON_MODE_FREQUENCY_MISMATCH"),
    ):
        value = mode(source)
        value[field] = replacement
        assert code in validate_phonon_mode_ref(value, source).errors
    stale = mode(source)
    stale["band_artifact"]["sha256"] = "f" * 64
    assert "PHONON_MODE_REFERENCE_STALE" in validate_phonon_mode_ref(stale, source).errors


def test_degeneracy_is_source_declared_without_branch_merging() -> None:
    value = mode(branch=0)
    assert value["degeneracy"]["branch_indices"] == [0, 1, 2]
    assert value["degeneracy"]["basis_arbitrary_within_subspace"] is True
    assert validate_phonon_mode_ref(value, band()).valid


def test_nac_direction_binds_gamma_only() -> None:
    source = band()
    source["source"]["nac"] = {"enabled": True, "direction_policy": "explicit", "gamma_direction": [1.0, 0.0, 0.0]}
    assert mode(source, 0, 3)["nac_direction"] == [1.0, 0.0, 0.0]
    assert mode(source, 1, 3)["nac_direction"] is None


def test_canonical_phase_rotates_one_global_phase_only() -> None:
    values = canonicalize_global_phase([[1j, 1 + 0j, 0j], [-1j, 0j, 0j]])
    assert values[0][0].real == pytest.approx(1.0)
    assert values[0][0].imag == pytest.approx(0.0)
    assert values[0][1] == pytest.approx(-1j)
    assert values[1][0] == pytest.approx(-1.0)


def test_eigenvector_validates_shape_order_norm_mass_and_phase() -> None:
    source = band()
    value = vector(source)
    result = validate_phonon_eigenvector(value, source)
    assert result.valid, result.as_dict()
    assert value["schema_version"] == PHONON_EIGENVECTOR_SCHEMA_VERSION
    assert value["stored_vector_representation"] == "mass_weighted_eigenvector"
    norm = sum(real * real + imag * imag for item in value["eigenvectors"] for real, imag in zip(item["real"], item["imag"], strict=True))
    assert norm == pytest.approx(1.0)


@pytest.mark.parametrize(
    ("mutation", "code"),
    [
        (lambda value: value["eigenvectors"].pop(), "PHONON_EIGENVECTOR_SHAPE_INVALID"),
        (lambda value: value["eigenvectors"][0].update(atom_index=1), "PHONON_EIGENVECTOR_SHAPE_INVALID"),
        (lambda value: value["atomic_masses"]["values"].__setitem__(0, 0.0), "PHONON_EIGENVECTOR_MASS_INVALID"),
        (lambda value: value["eigenvectors"][0]["real"].__setitem__(0, 2.0), "PHONON_EIGENVECTOR_NORMALIZATION_INVALID"),
        (lambda value: value["eigenvectors"][0]["imag"].__setitem__(0, 0.5), "PHONON_EIGENVECTOR_PHASE_INVALID"),
        (lambda value: value.update(species=["Si", "C"]), "PHONON_EIGENVECTOR_ATOM_ORDER_MISMATCH"),
    ],
)
def test_eigenvector_rejects_invalid_contract_fields(mutation, code: str) -> None:
    value = vector()
    mutation(value)
    assert code in validate_phonon_eigenvector(value, band()).errors


def test_builder_rejects_zero_norm_nonfinite_shape_and_invalid_mass() -> None:
    source = band()
    selected = mode(source)
    with pytest.raises(PhononEigenvectorContractError, match="zero norm"):
        build_phonon_eigenvector(source, selected, [[0j] * 3, [0j] * 3], [28.0, 28.0])
    with pytest.raises(PhononEigenvectorContractError):
        build_phonon_eigenvector(source, selected, [[complex(math.nan, 0)] * 3, [0j] * 3], [28.0, 28.0])
    with pytest.raises(PhononEigenvectorContractError):
        build_phonon_eigenvector(source, selected, [[1 + 0j] * 2, [0j] * 3], [28.0, 28.0])
    with pytest.raises(PhononEigenvectorContractError):
        build_phonon_eigenvector(source, selected, [[1 + 0j] * 3, [0j] * 3], [0.0, 28.0])


def test_global_phase_and_negative_sign_are_scientifically_equivalent() -> None:
    left = vector()
    right = copy.deepcopy(left)
    phase = complex(math.cos(0.7), math.sin(0.7))
    for record in right["eigenvectors"]:
        values = [complex(real, imag) * phase for real, imag in zip(record["real"], record["imag"], strict=True)]
        record["real"] = [item.real for item in values]
        record["imag"] = [item.imag for item in values]
    assert scientific_phase_equivalent(left, right)
    negative = copy.deepcopy(left)
    for record in negative["eigenvectors"]:
        record["real"] = [-item for item in record["real"]]
        record["imag"] = [-item for item in record["imag"]]
    assert scientific_phase_equivalent(left, negative)
    different = copy.deepcopy(left)
    different["eigenvectors"][0]["real"][1] = 0.2
    assert not scientific_phase_equivalent(left, different)


def test_mass_unweighting_gives_lighter_atom_larger_direction() -> None:
    source = band()
    value = build_phonon_eigenvector(source, mode(source), [[1 + 0j, 0j, 0j], [1 + 0j, 0j, 0j]], [1.0, 4.0])
    unweighted = mass_unweighted_vectors(value)
    assert abs(unweighted[0][0]) == pytest.approx(2 * abs(unweighted[1][0]))


def test_non_gamma_cell_phase_and_display_amplitude_match_numpy_reference() -> None:
    source = band()
    value = vector(source, qpoint=1, branch=3)
    primary = np.asarray(reconstruct_display_displacements(value, cell_image=[0, 0, 0], phase_radians=0.0, amplitude_angstrom=0.2))
    translated = np.asarray(reconstruct_display_displacements(value, cell_image=[1, 0, 0], phase_radians=0.0, amplitude_angstrom=0.2))
    assert np.max(np.linalg.norm(primary, axis=1)) == pytest.approx(0.2)
    assert translated == pytest.approx(-primary)
    with pytest.raises(PhononEigenvectorContractError):
        reconstruct_display_displacements(value, cell_image=[17, 0, 0])


def test_imaginary_mode_preserves_negative_frequency_and_static_warning() -> None:
    source = band()
    source["branches"][3]["frequencies"][0] = -1.2
    value = vector(source)
    assert value["mode"]["frequency"] == -1.2
    assert value["provenance"]["imaginary_mode"] is True
    assert value["warnings"] == ["PHONON_EIGENVECTOR_IMAGINARY_MODE_STATIC_ONLY"]
    assert validate_phonon_eigenvector(value, source).valid


def test_set_summary_manifest_and_deterministic_serialization() -> None:
    source = band()
    first = vector(source, 0, 3)
    second = vector(source, 1, 3)
    value = build_phonon_eigenvector_set([second, first])
    assert value["schema_version"] == PHONON_EIGENVECTOR_SET_SCHEMA_VERSION
    assert [item["mode"]["qpoint_index"] for item in value["modes"]] == [0, 1]
    assert validate_phonon_eigenvector_set(value, source).valid
    summary = phonon_eigenvector_summary(value)
    assert summary["schema_version"] == PHONON_EIGENVECTOR_SUMMARY_SCHEMA_VERSION
    assert validate_phonon_eigenvector_summary(summary).valid
    manifest = phonon_eigenvector_manifest(value, summary)
    assert manifest["schema_version"] == PHONON_EIGENVECTOR_MANIFEST_SCHEMA_VERSION
    assert validate_phonon_eigenvector_manifest(manifest).valid
    assert eigenvector_content_hash(value) == eigenvector_content_hash(json.loads(json.dumps(value)))


def test_set_rejects_duplicates_order_drift_and_cap() -> None:
    value = vector()
    with pytest.raises(PhononEigenvectorContractError):
        build_phonon_eigenvector_set([value, value])
    over_cap = {"schema_version": PHONON_EIGENVECTOR_SET_SCHEMA_VERSION, "structure_identity": "a" * 64, "band_artifact": value["mode"]["band_artifact"], "set_scope": "subset", "mode_count": EIGENVECTOR_CAPS["max_modes"] + 1, "ordering": "qpoint_then_branch", "modes": [value] * (EIGENVECTOR_CAPS["max_modes"] + 1), "security": value["security"]}
    assert "PHONON_EIGENVECTOR_CAP_EXCEEDED" in validate_phonon_eigenvector_set(over_cap).errors


def test_security_rejects_executable_url_prototype_and_deep_payloads() -> None:
    for key, payload in (
        ("url", "https://example.invalid/vector"),
        ("callback", "alert(1)"),
        ("shader", "void main(){}"),
        ("__proto__", {"polluted": True}),
    ):
        value = vector()
        value["provenance"][key] = payload
        result = validate_phonon_eigenvector(value)
        assert "PHONON_EIGENVECTOR_EXTERNAL_REFERENCE_FORBIDDEN" in result.errors or "PHONON_EIGENVECTOR_PROVENANCE_INVALID" in result.errors


def test_schema_snapshots_are_closed_and_animation_free() -> None:
    snapshots = phonon_eigenvector_schema_snapshots()
    assert set(snapshots) == {"complex_scalar", "complex_vector3", "mode_ref", "eigenvector", "eigenvector_set", "summary", "manifest"}
    assert "animation" not in json.dumps(snapshots).lower()
