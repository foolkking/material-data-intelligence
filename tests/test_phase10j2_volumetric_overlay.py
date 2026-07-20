from __future__ import annotations

from copy import deepcopy

from mdi_artifact_core.volumetric_contract import (
    build_volumetric_grid,
    build_volumetric_structure_overlay,
    validate_volumetric_structure_overlay,
)


def _non_periodic_grid():
    return build_volumetric_grid(
        shape=(2, 2, 2),
        origin_cartesian=(0.0, 0.0, 0.0),
        step_matrix=((1.0, 0.0, 0.0), (0.0, 1.0, 0.0), (0.0, 0.0, 1.0)),
        sample_location="node",
        boundary_conditions=("non_periodic", "non_periodic", "non_periodic"),
        endpoint_policy="included",
    )


def test_non_periodic_structure_overlay_is_deterministic_and_validated():
    grid = _non_periodic_grid()
    atoms = ({"atomic_number": 14, "cartesian_angstrom": [0.0, 0.0, 0.0]},)
    first = build_volumetric_structure_overlay(grid=grid, atom_records=atoms)
    second = build_volumetric_structure_overlay(grid=grid, atom_records=atoms)
    assert first == second
    assert first["schema_version"] == "phase10j2.volumetric_structure_overlay.v1"
    assert validate_volumetric_structure_overlay(first, grid=grid).valid
    assert first["security"]["contains_executable"] is False


def test_structure_overlay_rejects_grid_rebinding_and_executable_metadata():
    grid = _non_periodic_grid()
    overlay = build_volumetric_structure_overlay(grid=grid, atom_records=({"atomic_number": 8, "cartesian_angstrom": [0.0, 0.0, 0.0]},))
    rebound = deepcopy(overlay); rebound["grid_content_hash"] = "0" * 64
    assert "VOLUME_OVERLAY_GRID_MISMATCH" in validate_volumetric_structure_overlay(rebound, grid=grid).errors
    injected = deepcopy(overlay); injected["unavailable_reason"] = "<script>alert(1)</script>"
    assert not validate_volumetric_structure_overlay(injected, grid=grid).valid
