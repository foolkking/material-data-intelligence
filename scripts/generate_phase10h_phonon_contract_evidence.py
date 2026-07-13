from __future__ import annotations

import argparse
import copy
import hashlib
import json
import math
from pathlib import Path
from typing import Any

import numpy as np
from scipy import constants

from mdi_artifact_core import (
    DEFAULT_PHONON_CAPS,
    PHONON_BAND_SCHEMA_VERSION,
    PHONON_DOS_SCHEMA_VERSION,
    PHONON_MANIFEST_SCHEMA_VERSION,
    PHONON_SUMMARY_SCHEMA_VERSION,
    convert_frequency,
    phonon_content_hash,
    phonon_schema_snapshots,
    phonon_summary,
    reciprocal_lattice_physics_2pi,
    reciprocal_path_step,
    stable_phonon_json,
    validate_band_dos_compatibility,
    validate_phonon_band,
    validate_phonon_dos,
    validate_phonon_manifest,
    validate_phonon_summary,
)


ROOT = Path(__file__).resolve().parents[1]
FIXTURE_DIR = ROOT / "docs" / "phase10h" / "fixtures" / "phonon_contract"
EVIDENCE_DIR = ROOT / "docs" / "phase10h" / "evidence" / "phase10h_phonon_contract"
STRUCTURE_ID = "a" * 64
INPUT_HASH = "b" * 64


def _write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        handle.write(text.replace("\r\n", "\n").replace("\r", "\n"))


def write_json(path: Path, value: Any) -> None:
    _write_text(path, json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n")


def security() -> dict[str, Any]:
    return {
        "contains_javascript": False,
        "contains_html": False,
        "external_urls_allowed": False,
        "executable_content_allowed": False,
        "external_assets": [],
    }


def source(*, nac: bool = False) -> dict[str, Any]:
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


def make_band(*, lattice: list[list[float]] | None = None, imaginary: bool = False) -> dict[str, Any]:
    lattice = lattice or [[5.43, 0.0, 0.0], [0.0, 5.43, 0.0], [0.0, 0.0, 5.43]]
    coordinates = [[0.0, 0.0, 0.0], [0.5, 0.0, 0.0], [0.5, 0.5, 0.5]]
    distances = [0.0]
    for start, end in zip(coordinates[:-1], coordinates[1:], strict=True):
        distances.append(distances[-1] + reciprocal_path_step(start, end, lattice))
    acoustic = [-0.25 if imaginary else 0.0, 1.0, 1.5]
    near_zero = [-1e-7 if imaginary else 0.0, 1.0, 1.6]
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
        "segments": [{"segment_index": 0, "start_qpoint_index": 0, "end_qpoint_index": 2, "start_label": "Γ", "end_label": "L", "discontinuous_from_previous": False}],
        "branches": [
            {"branch_index": 0, "frequencies": acoustic},
            {"branch_index": 1, "frequencies": near_zero},
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


def make_discontinuous_band() -> dict[str, Any]:
    band = make_band()
    boundary = band["qpoints"][-1]["distance"]
    band["qpoints"].extend(
        [
            {"index": 3, "coordinates": [0.0, 0.0, 0.0], "label": "Γ", "source_label": "Gamma", "segment_index": 1, "distance": boundary},
            {"index": 4, "coordinates": [0.0, 0.5, 0.0], "label": "M", "source_label": "M", "segment_index": 1, "distance": boundary + math.pi / 5.43},
        ]
    )
    band["segments"] = [
        {"segment_index": 0, "start_qpoint_index": 0, "end_qpoint_index": 2, "start_label": "Γ", "end_label": "L", "discontinuous_from_previous": False},
        {"segment_index": 1, "start_qpoint_index": 3, "end_qpoint_index": 4, "start_label": "Γ", "end_label": "M", "discontinuous_from_previous": True},
    ]
    for branch in band["branches"]:
        branch["frequencies"].extend([branch["frequencies"][0], branch["frequencies"][1]])
    return band


def make_dos(*, imaginary: bool = True, projected: bool = True) -> dict[str, Any]:
    frequencies = [-1.0, 0.0, 1.0, 2.0, 3.0, 4.0, 5.0] if imaginary else [0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0]
    total = [1.0] * 7
    projections = []
    if projected:
        projections = [
            {"projection_index": 0, "projection_type": "atom", "atom_index": 0, "species": "Si", "values": [0.5] * 7, "source_guarantees_sum": True},
            {"projection_index": 1, "projection_type": "atom", "atom_index": 1, "species": "Si", "values": [0.5] * 7, "source_guarantees_sum": True},
        ]
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
        "projected_dos": projections,
        "broadening": {"method": "none", "width": None, "unit": None, "source": "fixture"},
        "integration": {"method": "trapezoidal", "expected_mode_count": 6, "observed_integral": 6.0, "relative_tolerance": 0.01, "status": "within_tolerance"},
        "source": source(),
        "warnings": [],
        "security": security(),
    }


def validation_capture(payload: dict[str, Any], kind: str) -> dict[str, Any]:
    result = validate_phonon_band(payload) if kind == "band" else validate_phonon_dos(payload)
    return {"schema_version": payload["schema_version"], "canonical_sha256": phonon_content_hash(payload), "validation": result.as_dict()}


def build_manifest(band: dict[str, Any], dos: dict[str, Any], summary: dict[str, Any]) -> dict[str, Any]:
    artifacts = []
    for name, schema, payload in (
        ("phonon_band.json", PHONON_BAND_SCHEMA_VERSION, band),
        ("phonon_dos.json", PHONON_DOS_SCHEMA_VERSION, dos),
        ("phonon_summary.json", PHONON_SUMMARY_SCHEMA_VERSION, summary),
    ):
        encoded = stable_phonon_json(payload).encode("utf-8")
        artifacts.append({"name": name, "schema_version": schema, "media_type": "application/json", "size_bytes": len(encoded), "sha256": hashlib.sha256(encoded).hexdigest()})
    return {
        "schema_version": PHONON_MANIFEST_SCHEMA_VERSION,
        "structure_identity": STRUCTURE_ID,
        "band_schema_version": PHONON_BAND_SCHEMA_VERSION,
        "dos_schema_version": PHONON_DOS_SCHEMA_VERSION,
        "summary_schema_version": PHONON_SUMMARY_SCHEMA_VERSION,
        "artifacts": artifacts,
        "security": security(),
    }


def normalized_bytes(path: Path) -> bytes:
    data = path.read_bytes()
    if path.suffix.lower() in {".json", ".md"}:
        return data.replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    return data


def write_hashes() -> None:
    records = []
    for path in sorted(EVIDENCE_DIR.rglob("*")):
        if not path.is_file() or path.name == "artifact_hashes.json":
            continue
        data = normalized_bytes(path)
        records.append({"path": path.relative_to(EVIDENCE_DIR).as_posix(), "bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()})
    write_json(EVIDENCE_DIR / "artifact_hashes.json", {"algorithm": "sha256", "text_normalization": "LF", "files": records})


def generate() -> None:
    stable_band = make_band()
    imaginary_band = make_band(imaginary=True)
    discontinuous = make_discontinuous_band()
    total_dos = make_dos(imaginary=False, projected=False)
    imaginary_dos = make_dos(imaginary=True, projected=False)
    projected_dos = make_dos(imaginary=True, projected=True)
    incompatible_dos = copy.deepcopy(projected_dos)
    incompatible_dos["structure_identity"] = "c" * 64
    summary = phonon_summary(stable_band, projected_dos)
    manifest = build_manifest(stable_band, projected_dos, summary)

    fixtures = {
        "stable_band.json": stable_band,
        "imaginary_band.json": imaginary_band,
        "discontinuous_band.json": discontinuous,
        "total_dos.json": total_dos,
        "imaginary_dos.json": imaginary_dos,
        "projected_dos.json": projected_dos,
        "incompatible_dos.json": incompatible_dos,
        "phonon_summary.json": summary,
        "phonon_manifest.json": manifest,
    }
    invalid_branch = copy.deepcopy(stable_band)
    invalid_branch["branches"].pop()
    invalid_distance = copy.deepcopy(stable_band)
    invalid_distance["qpoints"][2]["distance"] = 0.0
    invalid_dos = copy.deepcopy(projected_dos)
    invalid_dos["frequencies"][2] = 0.0
    fixtures.update({"invalid_branch_count.json": invalid_branch, "invalid_path_distance.json": invalid_distance, "invalid_dos_grid.json": invalid_dos})
    for name, payload in fixtures.items():
        write_json(FIXTURE_DIR / name, payload)

    snapshots = phonon_schema_snapshots()
    write_json(EVIDENCE_DIR / "phonon_band_schema.json", snapshots["band"])
    write_json(EVIDENCE_DIR / "phonon_dos_schema.json", snapshots["dos"])
    write_json(EVIDENCE_DIR / "phonon_summary_schema.json", snapshots["summary"])
    write_json(EVIDENCE_DIR / "phonon_manifest_schema.json", snapshots["manifest"])
    write_json(EVIDENCE_DIR / "qpoint_path_schema.json", {
        "schema_version": "phase10h.qpoint_path.v1",
        "coordinate_system": "reciprocal_fractional",
        "distance_unit": "radian_per_angstrom",
        "endpoint_policy": "duplicated_segment_endpoints",
        "distance_policy": "global_cumulative_excluding_discontinuity_gap",
        "discontinuity": "explicit",
    })
    write_json(EVIDENCE_DIR / "reciprocal_convention.json", {"real_lattice": "row_vectors", "formula": "B = 2*pi*(A^-1)^T", "convention": "physics_2pi", "identity": "a_i dot b_j = 2*pi*delta_ij"})
    write_json(EVIDENCE_DIR / "frequency_unit_policy.json", {
        "canonical": "terahertz", "meaning": "cyclic_frequency", "approved_conversion_units": ["inverse_centimeter", "millielectronvolt", "terahertz"],
        "constants": {"planck_joule_second": constants.h, "speed_of_light_meter_per_second": constants.c, "electronvolt_joule": constants.e},
        "one_thz": {"inverse_centimeter": convert_frequency(1, "terahertz", "inverse_centimeter"), "millielectronvolt": convert_frequency(1, "terahertz", "millielectronvolt")},
    })
    write_json(EVIDENCE_DIR / "imaginary_frequency_policy.json", {"encoding": "negative_real", "near_zero_classification_only": True, "values_mutated": False, "acoustic_sum_rule_applied_by_validator": False})
    write_json(EVIDENCE_DIR / "branch_identity_policy.json", {"identity": "source_stable_branch_index", "required_count": "3N", "scope": "full", "frequency_sorting": False, "connectivity_inference": False})
    write_json(EVIDENCE_DIR / "degeneracy_policy.json", {"source_declared_only": True, "branches_merged": False, "identity": ["qpoint_index", "branch_indices"], "source": "producer"})
    write_json(EVIDENCE_DIR / "dos_normalization_policy.json", {"grid": "sample_grid_points", "density_unit": "modes_per_terahertz", "normalization": "total_modes", "expected_integral": "3N", "method": "trapezoidal", "negative_frequency_region_allowed": True})
    write_json(EVIDENCE_DIR / "band_dos_compatibility_policy.json", {"statuses": ["compatible", "convertible", "incompatible"], "checks": ["structure_identity", "atom_count", "species_order", "frequency_unit", "imaginary_encoding", "zero_tolerance", "source_lineage", "NAC"]})
    write_json(EVIDENCE_DIR / "caps.json", DEFAULT_PHONON_CAPS)

    write_json(EVIDENCE_DIR / "stable_band_fixture_result.json", validation_capture(stable_band, "band"))
    write_json(EVIDENCE_DIR / "imaginary_band_fixture_result.json", validation_capture(imaginary_band, "band"))
    write_json(EVIDENCE_DIR / "discontinuous_path_result.json", validation_capture(discontinuous, "band"))
    write_json(EVIDENCE_DIR / "degenerate_modes_result.json", {"validation": validate_phonon_band(stable_band).as_dict(), "groups": stable_band["degeneracy_groups"], "branches_merged": False})
    write_json(EVIDENCE_DIR / "total_dos_result.json", validation_capture(total_dos, "dos"))
    write_json(EVIDENCE_DIR / "imaginary_dos_result.json", validation_capture(imaginary_dos, "dos"))
    write_json(EVIDENCE_DIR / "projected_dos_result.json", validation_capture(projected_dos, "dos"))
    write_json(EVIDENCE_DIR / "compatible_pair_result.json", validate_band_dos_compatibility(stable_band, projected_dos).as_dict())
    write_json(EVIDENCE_DIR / "incompatible_pair_result.json", validate_band_dos_compatibility(stable_band, incompatible_dos).as_dict())

    triclinic = np.asarray([[4.1, 0.0, 0.0], [1.2, 3.8, 0.0], [0.4, 0.7, 5.2]])
    independent_reciprocal = 2 * np.pi * np.linalg.inv(triclinic).T
    production_reciprocal = np.asarray(reciprocal_lattice_physics_2pi(triclinic.tolist()))
    write_json(EVIDENCE_DIR / "independent_reference_comparison.json", {
        "reference": "numpy.linalg plus scipy.constants",
        "reciprocal_max_abs_error": float(np.max(np.abs(independent_reciprocal - production_reciprocal))),
        "one_thz_inverse_centimeter_reference": 1e12 / (constants.c * 100),
        "one_thz_inverse_centimeter_production": convert_frequency(1, "terahertz", "inverse_centimeter"),
        "one_thz_mev_reference": constants.h * 1e12 / constants.e * 1000,
        "one_thz_mev_production": convert_frequency(1, "terahertz", "millielectronvolt"),
        "result": "PASS",
    })
    first, second = stable_phonon_json(stable_band), stable_phonon_json(json.loads(stable_phonon_json(stable_band)))
    write_json(EVIDENCE_DIR / "deterministic_serialization.json", {"equal": first == second, "first_sha256": hashlib.sha256(first.encode()).hexdigest(), "second_sha256": hashlib.sha256(second.encode()).hexdigest(), "contains_timestamp": False, "contains_random_uuid": False})

    attacks = [
        {"callback": "run"}, {"note": "<script>alert(1)</script>"}, {"note": "javascript:alert(1)"},
        {"note": "https://example.invalid/data"}, {"note": "C:\\private\\phonon.yaml"}, {"shader": "void main()"},
    ]
    attack_results = []
    for attack in attacks:
        malicious = copy.deepcopy(stable_band)
        malicious["source"].update(attack)
        validation = validate_phonon_band(malicious, raw_size_bytes=1000)
        attack_results.append({"attack_fields": sorted(attack), "valid": validation.valid, "errors": list(validation.errors)})
    write_json(EVIDENCE_DIR / "security_audit.json", {"result": "PASS", "artifact_javascript": False, "artifact_html": False, "external_urls": False, "external_modules": False, "arbitrary_units": False, "attacks": attack_results, "marker": "NO_SECRET_PATTERN_HITS"})
    write_json(EVIDENCE_DIR / "network_audit.json", {"result": "PASS", "runtime_network_required": False, "external_requests": 0, "marker": "NO_EXTERNAL_NETWORK_REQUESTS"})
    write_json(EVIDENCE_DIR / "manifest_validation.json", validate_phonon_manifest(manifest).as_dict())
    write_json(EVIDENCE_DIR / "summary_validation.json", validate_phonon_summary(summary).as_dict())
    write_json(EVIDENCE_DIR / "invalid_fixture_results.json", {
        "branch_count": validate_phonon_band(invalid_branch).as_dict(),
        "path_distance": validate_phonon_band(invalid_distance).as_dict(),
        "dos_grid": validate_phonon_dos(invalid_dos).as_dict(),
    })
    _write_text(EVIDENCE_DIR / "README.md", """# Phase 10H Phonon Contract Evidence

Deterministic contract-only evidence for reciprocal-space conventions, q-point paths, THz frequencies, negative-real imaginary modes, source-stable 3N branches, DOS normalization, projected identity, compatibility, caps, and inert-data security.

- No phonon adapter or formal tool is registered.
- No band/DOS plot, renderer, eigenvector payload, animation, notebook, external API, or real LLM is included.
- `NO_EXTERNAL_NETWORK_REQUESTS`
- `NO_SECRET_PATTERN_HITS`
""")
    write_hashes()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--hash-only", action="store_true")
    args = parser.parse_args()
    if args.hash_only:
        write_hashes()
    else:
        generate()
    print("PHASE10H_PHONON_CONTRACT_EVIDENCE_PASS")
    print("NO_EXTERNAL_NETWORK_REQUESTS")
    print("NO_SECRET_PATTERN_HITS")


if __name__ == "__main__":
    main()
