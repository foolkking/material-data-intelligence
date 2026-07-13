from __future__ import annotations

import copy
import json
from pathlib import Path

from mdi_artifact_core import canonical_trajectory_id, validate_trajectory

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "docs" / "phase10g" / "fixtures" / "trajectory_v1"
TARGET = ROOT / "docs" / "phase10g" / "fixtures" / "trajectory_viewer"


def load(name: str) -> dict:
    return json.loads((SOURCE / name).read_text(encoding="utf-8"))


def seal(payload: dict) -> dict:
    payload["trajectory_id"] = canonical_trajectory_id(payload)
    result = validate_trajectory(payload)
    if not result.valid:
        raise ValueError(result.errors)
    return payload


def fixed_fixture(wrapping: str = "wrapped") -> dict:
    payload = load("fixed_lattice_md.json")
    payload["position_wrapping"] = wrapping
    payload["atoms"] = {
        "count": 4,
        "records": [
            {"atom_id": 0, "label": "Si1", "species": "Si", "occupancy": 1.0},
            {"atom_id": 1, "label": "Si2", "species": "Si", "occupancy": 1.0},
            {"atom_id": 2, "label": "O3", "species": "O", "occupancy": 1.0},
            {"atom_id": 3, "label": "O4", "species": "O", "occupancy": 1.0},
        ],
    }
    frames = []
    for index in range(12):
        shift = index * 0.01
        positions = [[shift, 0.0, 0.0], [0.25 + shift, 0.25, 0.25], [0.5, 0.5 + shift, 0.5], [0.75, 0.75, 0.75 + shift]]
        if wrapping == "unwrapped":
            positions[0][0] = 0.92 + index * 0.08
        frames.append({
            **copy.deepcopy(payload["frames"][0]),
            "frame_index": index,
            "atom_ids": [0, 1, 2, 3],
            "positions": positions,
            "velocities": [[0.005, 0.0, 0.0], [0.005, 0.0, 0.0], [0.0, 0.005, 0.0], [0.0, 0.0, 0.005]],
            "time": float(index),
            "step": index * 5,
        })
    payload["frames"] = frames
    payload["metadata"] = {"title": f"Phase 10G-2 {wrapping} fixed-lattice viewer fixture"}
    return seal(payload)


def variable_fixture() -> dict:
    payload = load("variable_lattice_relaxation.json")
    payload["atoms"] = {
        "count": 4,
        "records": [
            {"atom_id": 0, "label": "Na1", "species": "Na", "occupancy": 1.0},
            {"atom_id": 1, "label": "Cl2", "species": "Cl", "occupancy": 1.0},
            {"atom_id": 2, "label": "Na3", "species": "Na", "occupancy": 1.0},
            {"atom_id": 3, "label": "Cl4", "species": "Cl", "occupancy": 1.0},
        ],
    }
    frames = []
    for index in range(6):
        length = 5.8 - index * 0.05
        force = 0.1 / (index + 1)
        frames.append({
            **copy.deepcopy(payload["frames"][0]),
            "frame_index": index,
            "atom_ids": [0, 1, 2, 3],
            "positions": [[0.0, 0.0, 0.0], [length / 2, length / 2, length / 2], [length / 2, 0.0, length / 2], [0.0, length / 2, 0.0]],
            "lattice": [[length, 0.0, 0.0], [0.2, length, 0.0], [0.1, 0.3, length]],
            "forces": [[force, 0.0, 0.0], [-force, 0.0, 0.0], [0.0, force, 0.0], [0.0, -force, 0.0]],
            "energy": {"potential": -5.0 - index * 0.2, "kinetic": None, "total": -5.0 - index * 0.2, "free": None, "scope": "total_system", "unit": "electronvolt"},
            "step": index,
        })
    payload["frames"] = frames
    payload["metadata"] = {"title": "Phase 10G-2 variable triclinic viewer fixture"}
    return seal(payload)


def write(name: str, payload: dict) -> None:
    (TARGET / name).write_text(json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=True) + "\n", encoding="utf-8")


def main() -> None:
    TARGET.mkdir(parents=True, exist_ok=True)
    write("fixed_lattice_md_12_frames.json", fixed_fixture())
    write("variable_lattice_relaxation_6_frames.json", variable_fixture())
    write("unwrapped_diffusion_12_frames.json", fixed_fixture("unwrapped"))
    write("unknown_wrapping_12_frames.json", fixed_fixture("unknown"))
    write("synthetic_budget_policy.json", {
        "schema_version": "phase10g2.synthetic_budget_policy.v1",
        "degraded_generator": {"atoms": 400, "frames": 260, "persist_payload": False},
        "refused_generator": {"displayed_instances": 769, "hard_cap": 768, "persist_payload": False},
        "static_reference_bonds": "PARTIAL_READY_NOT_EMITTED",
    })
    print("PHASE10G2_TRAJECTORY_VIEWER_FIXTURES_PASS")


if __name__ == "__main__":
    main()
