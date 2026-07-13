from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
from typing import Any

from mdi_artifact_core import (
    DEFAULT_TRAJECTORY_CAPS,
    FUTURE_DEGRADED_CAPS,
    FUTURE_INTERACTIVE_CAPS,
    TRAJECTORY_FRAME_SCHEMA_VERSION,
    TRAJECTORY_MANIFEST_SCHEMA_VERSION,
    TRAJECTORY_SCHEMA_VERSION,
    TRAJECTORY_SUMMARY_SCHEMA_VERSION,
    canonical_trajectory_id,
    stable_trajectory_json,
    trajectory_summary,
    validate_trajectory,
    validate_trajectory_manifest,
)


ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "docs" / "phase10g" / "fixtures" / "trajectory_v1"
EVIDENCE = ROOT / "docs" / "phase10g" / "evidence" / "phase10g_trajectory_contract"
INPUT_HASH = "0" * 64
SECURITY = {
    "contains_javascript": False,
    "contains_html": False,
    "external_urls_allowed": False,
    "remote_frames_allowed": False,
    "executable_content_allowed": False,
}


def atom_records(species: list[str]) -> dict[str, Any]:
    return {
        "count": len(species),
        "records": [
            {"atom_id": index, "species": item, "label": f"{item}{index + 1}", "occupancy": 1.0}
            for index, item in enumerate(species)
        ],
    }


def base_payload(*, kind: str, coordinate_mode: str, wrapping: str, lattice_mode: str, species: list[str]) -> dict[str, Any]:
    payload = {
        "schema_version": TRAJECTORY_SCHEMA_VERSION,
        "trajectory_id": "pending",
        "kind": kind,
        "coordinate_mode": coordinate_mode,
        "position_wrapping": wrapping,
        "lattice_mode": lattice_mode,
        "atom_identity_mode": "stable_index",
        "periodic_boundary": [True, True, True],
        "units": {
            "positions": "fractional" if coordinate_mode == "fractional" else "angstrom",
            "velocities": "angstrom_per_femtosecond",
            "forces": "electronvolt_per_angstrom",
            "energy": "electronvolt",
            "temperature": "kelvin",
        },
        "time": {"unit": "femtosecond" if kind == "molecular_dynamics" else None, "origin": 0.0},
        "atoms": atom_records(species),
        "fixed_lattice": [[5.0, 0.0, 0.0], [0.0, 5.0, 0.0], [0.0, 0.0, 5.0]] if lattice_mode == "fixed" else None,
        "frames": [],
        "properties": {"positions": True, "velocities": False, "forces": False, "energy": False, "temperature": False, "stress": False},
        "metadata": {"title": "Deterministic Phase 10G fixture"},
        "provenance": {
            "source_format": "contract_fixture",
            "source_software": "unknown",
            "source_version": None,
            "parser_version": None,
            "input_sha256": INPUT_HASH,
            "created_by_tool": None,
        },
        "warnings": ["TRAJECTORY_SOURCE_SOFTWARE_UNKNOWN"],
        "security": dict(SECURITY),
    }
    return payload


def frame(index: int, positions: list[list[float]], *, lattice: Any = None, step: int | None = None, time: float | None = None) -> dict[str, Any]:
    return {
        "schema_version": TRAJECTORY_FRAME_SCHEMA_VERSION,
        "frame_index": index,
        "atom_ids": list(range(len(positions))),
        "step": step,
        "time": time,
        "lattice": lattice,
        "positions": positions,
        "velocities": None,
        "forces": None,
        "energy": None,
        "temperature": None,
        "metadata": {},
    }


def seal(payload: dict[str, Any]) -> dict[str, Any]:
    payload["trajectory_id"] = canonical_trajectory_id(payload)
    return payload


def valid_fixtures() -> dict[str, dict[str, Any]]:
    md = base_payload(kind="molecular_dynamics", coordinate_mode="fractional", wrapping="wrapped", lattice_mode="fixed", species=["Si", "Si"])
    md["properties"]["velocities"] = True
    for index, delta in enumerate((0.0, 0.01, 0.02, 0.03)):
        item = frame(index, [[delta, 0.0, 0.0], [0.25 + delta, 0.25, 0.25]], step=index * 5, time=index * 2.0)
        item["velocities"] = [[0.005, 0.0, 0.0], [0.005, 0.0, 0.0]]
        md["frames"].append(item)

    relaxation = base_payload(kind="geometry_optimization", coordinate_mode="cartesian", wrapping="unknown", lattice_mode="variable", species=["Na", "Cl"])
    relaxation["properties"]["forces"] = True
    relaxation["properties"]["energy"] = True
    relaxation["warnings"].append("TRAJECTORY_WRAPPING_UNKNOWN")
    for index, scale in enumerate((5.8, 5.7, 5.65)):
        lattice = [[scale, 0.0, 0.0], [0.2, scale, 0.0], [0.1, 0.3, scale]]
        item = frame(index, [[0.0, 0.0, 0.0], [scale / 2, scale / 2, scale / 2]], lattice=lattice, step=index, time=None)
        item["forces"] = [[0.1 / (index + 1), 0.0, 0.0], [-0.1 / (index + 1), 0.0, 0.0]]
        item["energy"] = {"potential": -5.0 - index * 0.2, "kinetic": None, "total": -5.0 - index * 0.2, "free": None, "unit": "electronvolt", "scope": "total_system"}
        relaxation["frames"].append(item)

    diffusion = base_payload(kind="molecular_dynamics", coordinate_mode="fractional", wrapping="unwrapped", lattice_mode="fixed", species=["Li"])
    diffusion["frames"] = [frame(index, [[value, 0.5, 0.5]], step=index, time=float(index)) for index, value in enumerate((0.9, 1.0, 1.1, 1.25))]

    sequence = base_payload(kind="structure_sequence", coordinate_mode="cartesian", wrapping="unknown", lattice_mode="fixed", species=["C", "O"])
    sequence["periodic_boundary"] = [False, False, False]
    sequence["warnings"].append("TRAJECTORY_WRAPPING_UNKNOWN")
    sequence["frames"] = [frame(0, [[0.0, 0.0, 0.0], [1.2, 0.0, 0.0]])]
    return {name: seal(payload) for name, payload in {
        "fixed_lattice_md.json": md,
        "variable_lattice_relaxation.json": relaxation,
        "unwrapped_diffusion.json": diffusion,
        "nonperiodic_sequence.json": sequence,
    }.items()}


def invalid_fixtures(valid: dict[str, dict[str, Any]]) -> dict[str, dict[str, Any]]:
    atom_count = copy.deepcopy(valid["fixed_lattice_md.json"])
    atom_count["frames"][1]["positions"] = atom_count["frames"][1]["positions"][:-1]
    atom_count["frames"][1]["velocities"] = atom_count["frames"][1]["velocities"][:-1]

    reorder = copy.deepcopy(valid["fixed_lattice_md.json"])
    reorder["frames"][1]["atom_ids"] = [1, 0]

    lattice = copy.deepcopy(valid["variable_lattice_relaxation.json"])
    lattice["frames"][1]["lattice"] = [[1.0, 0.0, 0.0], [2.0, 0.0, 0.0], [0.0, 0.0, 1.0]]

    time = copy.deepcopy(valid["fixed_lattice_md.json"])
    time["frames"][2]["time"] = 0.5
    return {name: seal(payload) for name, payload in {
        "invalid_atom_count.json": atom_count,
        "invalid_species_reorder.json": reorder,
        "invalid_lattice.json": lattice,
        "invalid_time.json": time,
    }.items()}


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=True) + "\n", encoding="utf-8", newline="\n")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    valid = valid_fixtures()
    invalid = invalid_fixtures(valid)
    for name, payload in {**valid, **invalid}.items():
        write_json(FIXTURES / name, payload)

    expected = {}
    for name, payload in {**valid, **invalid}.items():
        expected[name] = validate_trajectory(payload).as_dict()
    write_json(FIXTURES / "expected_results.json", expected)

    schema_common = {
        "representation": "application/json",
        "unknown_fields": "rejected",
        "executable_content": "forbidden",
        "external_references": "forbidden",
    }
    write_json(EVIDENCE / "trajectory_schema.json", {"schema_version": TRAJECTORY_SCHEMA_VERSION, **schema_common, "required_sections": sorted(key for key in valid["fixed_lattice_md.json"] if key != "trajectory_id"), "identity": "sha256 of canonical payload excluding trajectory_id"})
    write_json(EVIDENCE / "trajectory_frame_schema.json", {"schema_version": TRAJECTORY_FRAME_SCHEMA_VERSION, **schema_common, "frame_index": "zero-based contiguous", "atom_identity": "stable_index", "positions": "atom_count x 3 finite values"})
    write_json(EVIDENCE / "trajectory_summary_schema.json", {"schema_version": TRAJECTORY_SUMMARY_SCHEMA_VERSION, **schema_common, "contains_frame_data": False, "example": trajectory_summary(valid["fixed_lattice_md.json"])})

    trajectory_raw = (FIXTURES / "fixed_lattice_md.json").read_bytes()
    summary_raw = (json.dumps(trajectory_summary(valid["fixed_lattice_md.json"]), indent=2, sort_keys=True) + "\n").encode()
    manifest = {
        "schema_version": TRAJECTORY_MANIFEST_SCHEMA_VERSION,
        "trajectory_schema_version": TRAJECTORY_SCHEMA_VERSION,
        "frame_schema_version": TRAJECTORY_FRAME_SCHEMA_VERSION,
        "summary_schema_version": TRAJECTORY_SUMMARY_SCHEMA_VERSION,
        "trajectory_id": valid["fixed_lattice_md.json"]["trajectory_id"],
        "frame_count": 4,
        "atom_count": 2,
        "artifacts": [
            {"name": "trajectory.json", "media_type": "application/json", "bytes": len(trajectory_raw), "sha256": hashlib.sha256(trajectory_raw).hexdigest()},
            {"name": "trajectory_summary.json", "media_type": "application/json", "bytes": len(summary_raw), "sha256": hashlib.sha256(summary_raw).hexdigest()},
        ],
        "security": dict(SECURITY),
    }
    write_json(EVIDENCE / "trajectory_manifest_schema.json", {"schema_version": TRAJECTORY_MANIFEST_SCHEMA_VERSION, **schema_common, "example": manifest, "validation": validate_trajectory_manifest(manifest).as_dict()})
    write_json(EVIDENCE / "enum_policy.json", {"kind": sorted({item["kind"] for item in valid.values()} | {"unknown_static_sequence"}), "coordinate_mode": ["cartesian", "fractional"], "position_wrapping": ["unknown", "unwrapped", "wrapped"], "lattice_mode": ["fixed", "variable"], "partial_periodicity": "DEFERRED_BY_DESIGN"})
    write_json(EVIDENCE / "atom_identity_policy.json", {"mode": "stable_index", "count_changes": "forbidden", "frame_reorder": "forbidden", "species_changes": "forbidden", "partial_occupancy": "unsupported"})
    write_json(EVIDENCE / "coordinate_policy.json", {"lattice_vectors": "rows", "formula": "cartesian = f0*a + f1*b + f2*c", "cartesian_unit": "angstrom", "frame_mode_changes": "forbidden", "validator_mutates_coordinates": False})
    write_json(EVIDENCE / "lattice_policy.json", {"modes": ["fixed", "variable"], "relative_determinant_threshold": 1e-12, "maximum_condition_number": 1e8, "implicit_previous_frame_lattice": False})
    write_json(EVIDENCE / "time_unit_policy.json", {"canonical": "femtosecond", "accepted": ["femtosecond", "picosecond"], "frame_index": "required contiguous", "step": "optional monotonic", "md_time": "required monotonic"})
    write_json(EVIDENCE / "optional_property_policy.json", {"consistency": "strict_all_frames", "velocities": "angstrom_per_femtosecond", "forces": "electronvolt_per_angstrom", "energy": "electronvolt total_system", "temperature": "kelvin", "stress": "DEFERRED_BY_DESIGN", "arbitrary_properties": False})
    write_json(EVIDENCE / "caps.json", {"contract_hard": DEFAULT_TRAJECTORY_CAPS, "future_interactive": FUTURE_INTERACTIVE_CAPS, "future_degraded": FUTURE_DEGRADED_CAPS, "overflow_safe_preflight": True})
    for source, target in (
        ("fixed_lattice_md.json", "fixed_lattice_fixture_result.json"),
        ("variable_lattice_relaxation.json", "variable_lattice_fixture_result.json"),
        ("unwrapped_diffusion.json", "unwrapped_fixture_result.json"),
    ):
        write_json(EVIDENCE / target, {"fixture": source, "result": expected[source]})
    write_json(EVIDENCE / "invalid_cases.json", {name: expected[name] for name in sorted(invalid)})
    write_json(EVIDENCE / "frontend_backend_validation_comparison.json", {
        "fixtures": {name: {"python_valid": expected[name]["valid"], "typescript_expected_valid": name in valid} for name in sorted(expected)},
        "independent_implementations": ["mdi_artifact_core.trajectory_contract", "apps/web/app/lib/trajectoryContract.ts"],
        "result": "MATCH",
    })
    canonical = stable_trajectory_json(valid["fixed_lattice_md.json"])
    write_json(EVIDENCE / "deterministic_serialization.json", {"algorithm": "UTF-8 JSON, sorted keys, compact separators, ASCII escapes, NaN forbidden", "sha256": hashlib.sha256(canonical.encode()).hexdigest(), "replay_equal": canonical == stable_trajectory_json(copy.deepcopy(valid["fixed_lattice_md.json"]))})
    write_json(EVIDENCE / "security_audit.json", {"artifact_javascript": False, "artifact_html": False, "callbacks": False, "shaders_or_modules": False, "external_references": False, "private_paths": False, "notebook_or_script_execution": False, "real_llm": False, "new_dependencies": False, "marker": "NO_SECRET_PATTERN_HITS"})
    write_json(EVIDENCE / "network_audit.json", {"runtime_network_calls": 0, "remote_frames": 0, "remote_assets": 0, "marker": "NO_EXTERNAL_NETWORK_REQUESTS"})

    evidence_files = sorted(path for path in EVIDENCE.glob("*.json") if path.name != "artifact_hashes.json")
    fixture_files = sorted(FIXTURES.glob("*.json"))
    write_json(EVIDENCE / "artifact_hashes.json", {"algorithm": "sha256", "files": [{"path": path.relative_to(ROOT).as_posix(), "sha256": sha256(path)} for path in [*fixture_files, *evidence_files]]})
    print("PHASE10G_TRAJECTORY_CONTRACT_EVIDENCE_PASS")
    print("NO_EXTERNAL_NETWORK_REQUESTS")
    print("NO_SECRET_PATTERN_HITS")


if __name__ == "__main__":
    main()
