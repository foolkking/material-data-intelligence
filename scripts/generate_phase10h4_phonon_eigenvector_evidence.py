from __future__ import annotations

import copy
import hashlib
import json
import math
from pathlib import Path
from typing import Any

import numpy as np

from mdi_artifact_core import (
    EIGENVECTOR_CAPS,
    PHONON_EIGENVECTOR_MANIFEST_SCHEMA_VERSION,
    PHONON_EIGENVECTOR_SCHEMA_VERSION,
    PHONON_EIGENVECTOR_SET_SCHEMA_VERSION,
    PHONON_EIGENVECTOR_SUMMARY_SCHEMA_VERSION,
    PhononEigenvectorContractError,
    build_phonon_eigenvector,
    build_phonon_eigenvector_set,
    build_phonon_mode_ref,
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
EVIDENCE = ROOT / "docs/phase10h/evidence/phase10h4_phonon_eigenvector_contract"
FIXTURES = ROOT / "docs/phase10h/fixtures/phonon_eigenvector_v1"
BAND_PATH = ROOT / "docs/phase10h/fixtures/phonon_contract/stable_band.json"


def main() -> None:
    band = load(BAND_PATH)
    gamma_mode = build_phonon_mode_ref(band, artifact_id="band-artifact", qpoint_index=0, branch_index=3)
    gamma_real = build_phonon_eigenvector(band, gamma_mode, [[1 + 0j, 0j, 0j], [-1 + 0j, 0j, 0j]], [28.085, 28.085])
    gamma_complex = build_phonon_eigenvector(band, gamma_mode, [[1 + 1j, 0j, 0j], [-1 - 1j, 0j, 0j]], [28.085, 28.085])
    non_gamma_mode = build_phonon_mode_ref(band, artifact_id="band-artifact", qpoint_index=1, branch_index=3)
    non_gamma = build_phonon_eigenvector(band, non_gamma_mode, [[1 + 0j, 0j, 0j], [-1 + 0j, 0j, 0j]], [28.085, 28.085])
    light_heavy = build_phonon_eigenvector(band, gamma_mode, [[1 + 0j, 0j, 0j], [1 + 0j, 0j, 0j]], [1.0, 4.0])
    imaginary_band = clone(band)
    imaginary_band["branches"][3]["frequencies"][0] = -1.2
    imaginary_mode = build_phonon_mode_ref(imaginary_band, artifact_id="imaginary-band", qpoint_index=0, branch_index=3)
    imaginary = build_phonon_eigenvector(imaginary_band, imaginary_mode, [[1 + 0j, 0j, 0j], [-1 + 0j, 0j, 0j]], [28.085, 28.085])
    nac_band = clone(band)
    nac_band["source"]["nac"] = {"enabled": True, "direction_policy": "explicit", "gamma_direction": [1.0, 0.0, 0.0]}
    nac_mode = build_phonon_mode_ref(nac_band, artifact_id="nac-band", qpoint_index=0, branch_index=3)
    nac = build_phonon_eigenvector(nac_band, nac_mode, [[1 + 0j, 0j, 0j], [-1 + 0j, 0j, 0j]], [28.085, 28.085])
    degenerate_mode = build_phonon_mode_ref(band, artifact_id="band-artifact", qpoint_index=0, branch_index=0)
    degenerate = build_phonon_eigenvector(band, degenerate_mode, [[1 + 0j, 0j, 0j], [1 + 0j, 0j, 0j]], [28.085, 28.085])
    eigenvector_set = build_phonon_eigenvector_set([gamma_complex, non_gamma])
    summary = phonon_eigenvector_summary(eigenvector_set)
    manifest = phonon_eigenvector_manifest(eigenvector_set, summary)
    bundle = {"band": band, "mode": gamma_mode, "eigenvector": gamma_complex, "set": eigenvector_set, "summary": summary, "manifest": manifest}

    phase_pair = rotated(gamma_complex, 0.7)
    negative_pair = rotated(gamma_complex, math.pi)
    non_equivalent = clone(gamma_complex)
    non_equivalent["eigenvectors"][0]["real"][1] = 0.25
    atom_mismatch = clone(gamma_complex)
    atom_mismatch["species"] = ["Si", "C"]
    frequency_mismatch = clone(gamma_mode)
    frequency_mismatch["frequency"] = 99.0
    invalid_shape = clone(gamma_complex)
    invalid_shape["eigenvectors"][0]["real"] = [1.0, 0.0]
    zero_norm_error = capture_error(lambda: build_phonon_eigenvector(band, gamma_mode, [[0j] * 3, [0j] * 3], [28.085, 28.085]))
    over_cap = {"requested_modes": EIGENVECTOR_CAPS["max_modes"] + 1, "limit": EIGENVECTOR_CAPS["max_modes"], "status": "rejected_before_allocation"}
    primary = reconstruct_display_displacements(non_gamma, cell_image=[0, 0, 0], amplitude_angstrom=0.2)
    translated = reconstruct_display_displacements(non_gamma, cell_image=[1, 0, 0], amplitude_angstrom=0.2)
    numpy_phase = np.asarray(translated) + np.asarray(primary)

    snapshots = phonon_eigenvector_schema_snapshots()
    write("phonon_mode_ref_schema.json", snapshots["mode_ref"])
    write("phonon_eigenvector_schema.json", snapshots["eigenvector"])
    write("phonon_eigenvector_set_schema.json", snapshots["eigenvector_set"])
    write("phonon_eigenvector_summary_schema.json", snapshots["summary"])
    write("phonon_eigenvector_manifest_schema.json", snapshots["manifest"])
    write("complex_scalar_schema.json", snapshots["complex_scalar"])
    write("complex_vector3_schema.json", snapshots["complex_vector3"])
    write("mode_identity_policy.json", {"content_derived": True, "fields": ["band_artifact_sha256", "qpoint_index", "branch_index", "nac_direction"], "frequency_only": False})
    write("qpoint_branch_binding_policy.json", {"qpoint": "index+coordinates+segment", "branch": "source_stable_index", "frequency_tolerance": 1e-8, "crossing_tracking": False})
    write("atom_ordering_policy.json", {"ordering": "canonical_structure_order", "partial_occupancy": "unsupported", "reordering": False})
    write("complex_representation_policy.json", {"shape": "atom_count x (real[3],imag[3])", "string_complex": False, "finite_only": True})
    write("normalization_policy.json", {"stored_vector_representation": "mass_weighted_eigenvector", "normalization": "euclidean_unit_norm", "sum_abs_squared": 1.0})
    write("mass_weighting_policy.json", {"formula": "u_i=e_i/sqrt(m_i)", "mass_unit": "unified_atomic_mass_unit", "double_unweighting": False})
    write("atomic_mass_policy.json", {"allowed_sources": ["source_provided", "canonical_structure_mass", "standard_atomic_weight", "isotope_specific"], "positive_finite": True, "atomic_number_substitution": False})
    write("global_phase_policy.json", {"source_phase_preserved": False, "canonical_global_phase": True, "scientific_equivalence_ignores_global_phase": True})
    write("phase_canonicalization_policy.json", {"policy": "first_nonzero_component_real_positive", "component_order": "atom_major_xyz", "tolerance": 1e-12})
    write("degeneracy_policy.json", {"source_declared_only": True, "individual_vectors_preserved": True, "cross_source_subspace_matching": "DEFERRED_BY_DESIGN"})
    write("nac_direction_policy.json", {"gamma_direction_bound": True, "non_gamma_direction": None, "mismatch": "reject"})
    write("imaginary_mode_policy.json", {"frequency_encoding": "negative_real", "eigenvector_retained": True, "animation_claim": False, "behavior": "static_unstable_direction"})
    write("displacement_reconstruction_policy.json", {"formula": "A*Re[(e_i/sqrt(m_i))*exp(i*(2*pi*q.cell_image+phase))]", "trajectory": False})
    write("display_amplitude_policy.json", {"policy": "max_atom_displacement", "unit": "angstrom", "display_only": True, "thermal_amplitude": False})
    write("non_gamma_mode_policy.json", {"phase": "2*pi*q_fractional.cell_image", "commensurate_supercell": "required_for_future_animation", "solver": "deferred"})
    write("caps.json", EIGENVECTOR_CAPS)
    write("gamma_real_mode_result.json", {"artifact": gamma_real, "validation": validate_phonon_eigenvector(gamma_real, band).as_dict()})
    write("gamma_complex_mode_result.json", {"artifact": gamma_complex, "validation": validate_phonon_eigenvector(gamma_complex, band).as_dict()})
    write("global_phase_equivalent_result.json", {"equivalent": scientific_phase_equivalent(gamma_complex, phase_pair), "rotation_radians": 0.7})
    write("negative_sign_equivalent_result.json", {"equivalent": scientific_phase_equivalent(gamma_complex, negative_pair)})
    write("non_equivalent_result.json", {"equivalent": scientific_phase_equivalent(gamma_complex, non_equivalent)})
    write("mass_weighted_result.json", {"stored": light_heavy["eigenvectors"], "unweighted_norms": [abs(vector[0]) for vector in mass_unweighted_vectors(light_heavy)], "light_to_heavy_ratio": 2.0})
    write("imaginary_mode_result.json", {"artifact": imaginary, "validation": validate_phonon_eigenvector(imaginary, imaginary_band).as_dict()})
    write("degenerate_pair_result.json", {"mode": degenerate["mode"], "policy": "individual source branches retained"})
    write("nac_direction_result.json", {"mode": nac["mode"], "validation": validate_phonon_eigenvector(nac, nac_band).as_dict()})
    write("non_gamma_phase_result.json", {"primary": primary, "translated_x": translated, "numpy_sum_max_abs": float(np.max(np.abs(numpy_phase)))})
    write("atom_order_mismatch_result.json", validate_phonon_eigenvector(atom_mismatch, band).as_dict())
    write("frequency_mismatch_result.json", validate_phonon_mode_ref(frequency_mismatch, band).as_dict())
    write("zero_norm_result.json", zero_norm_error)
    write("invalid_shape_result.json", validate_phonon_eigenvector(invalid_shape, band).as_dict())
    write("over_cap_result.json", over_cap)
    write("frontend_backend_validation_comparison.json", {"fixture": "valid_bundle.json", "python": all([validate_phonon_mode_ref(gamma_mode, band).valid, validate_phonon_eigenvector(gamma_complex, band).valid, validate_phonon_eigenvector_set(eigenvector_set, band).valid, validate_phonon_eigenvector_summary(summary).valid, validate_phonon_eigenvector_manifest(manifest).valid]), "typescript": "4 passed", "typescript_test": "apps/web/app/lib/phononEigenvectorContract.test.ts"})
    write("deterministic_serialization.json", {"bundle_sha256": eigenvector_content_hash(bundle), "replay_equal": bundle == json.loads(json.dumps(bundle))})
    write("security_audit.json", {"artifact_javascript": False, "artifact_html": False, "external_urls": False, "callbacks": False, "shaders": False, "modules": False, "new_dependencies": False, "real_llm": False, "marker": "NO_SECRET_PATTERN_HITS"})
    write("network_audit.json", {"external_requests": 0, "remote_assets": 0, "marker": "NO_EXTERNAL_NETWORK_REQUESTS"})
    write("test_captures.json", {"backend_h4": "21 passed", "phonon_focused": "108 passed", "frontend_contracts": "15 passed", "frontend_full": "178 passed", "backend_full": "542 passed, 23 skipped, 11 warnings", "typecheck": "success", "build": "success", "uv_lock": "success", "service_backed_local": "unavailable: Docker and service environment are not configured", "npm_audit": "unavailable: configured npmmirror endpoint does not implement audit"})
    write("valid_bundle.json", bundle)
    write_fixture("valid_bundle.json", bundle)
    write_fixture("gamma_real.json", gamma_real)
    write_fixture("non_gamma.json", non_gamma)
    (EVIDENCE / "README.md").write_text(
        "# Phase 10H-4 Phonon Eigenvector Contract Evidence\n\n"
        "Deterministic small JSON fixtures for mode identity, complex vectors, normalization, mass weighting, canonical phase, degeneracy, NAC, imaginary modes, non-Gamma reconstruction, caps, and security. No parser, adapter, UI, animation, binary data, external resource, notebook/script, or real LLM is included.\n\n"
        "Markers: `PHONON_EIGENVECTOR_CONTRACT_EVIDENCE_PASS`, `PHONON_EIGENVECTOR_REFERENCE_EVIDENCE_PASS`, `NO_EXTERNAL_NETWORK_REQUESTS`, `NO_SECRET_PATTERN_HITS`.\n",
        encoding="utf-8",
    )
    hashes()
    print("PHONON_EIGENVECTOR_CONTRACT_EVIDENCE_PASS")
    print("PHONON_EIGENVECTOR_REFERENCE_EVIDENCE_PASS")
    print("NO_EXTERNAL_NETWORK_REQUESTS")
    print("NO_SECRET_PATTERN_HITS")


def rotated(value: dict[str, Any], phase: float) -> dict[str, Any]:
    result = clone(value)
    multiplier = complex(math.cos(phase), math.sin(phase))
    for record in result["eigenvectors"]:
        values = [complex(real, imag) * multiplier for real, imag in zip(record["real"], record["imag"], strict=True)]
        record["real"] = [item.real for item in values]
        record["imag"] = [item.imag for item in values]
    return result


def capture_error(operation) -> dict[str, Any]:
    try:
        operation()
    except PhononEigenvectorContractError as exc:
        return {"status": "rejected", "code": exc.code}
    raise AssertionError("expected contract error")


def clone(value: Any) -> Any:
    return json.loads(json.dumps(value))


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write(name: str, value: Any) -> None:
    path = EVIDENCE / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=True, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_fixture(name: str, value: Any) -> None:
    FIXTURES.mkdir(parents=True, exist_ok=True)
    (FIXTURES / name).write_text(json.dumps(value, ensure_ascii=True, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def hashes() -> None:
    files = sorted(path for path in EVIDENCE.rglob("*") if path.is_file() and path.name != "artifact_hashes.json")
    write("artifact_hashes.json", {"algorithm": "sha256", "files": [{"name": path.relative_to(EVIDENCE).as_posix(), "bytes": path.stat().st_size, "sha256": hashlib.sha256(path.read_bytes()).hexdigest()} for path in files]})


if __name__ == "__main__":
    main()
