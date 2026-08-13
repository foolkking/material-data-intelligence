# Demo 4: Trajectory + RDF + MSD + diffusion

## Goal and prompt

> Analyze this trajectory, show the RDF and MSD, and estimate diffusion over the full supplied time range with fit diagnostics.

Prompt SHA-256: `e189cd3c5025abdd68e6ad19b0e1c85ecbaacdf4142d62662d6be4c3d4b61076`.

## Current user entry

Use the product Data/import surface for each fixture, then enter the prompt in the Planner. Normal users do not supply Tool, Plan, Job, Artifact, Workspace, or storage IDs.

- `docs/phase10g/fixtures/trajectory_v1/fixed_lattice_md.json` | `7e0a46b2582b26d57aa4e82f9ab05a57aa1d80585ac54003ceceed83b6684e13` | 4326 bytes | `parse`

## Required semantic coverage

- `trajectory.diffusion`
- `trajectory.msd`
- `trajectory.rdf`

Every selected Tool must be individually eligible. Plan 0.2 is used only for real producer-Artifact-to-consumer dependencies; independent tools may remain Plan 0.1.

## Deterministic reproduction

1. Follow the [clean-checkout setup](README.md#mode-a-deterministic-reproduction).
2. Verify this contract with `uv run python scripts/generate_phase13_3_documentation_reproducibility.py`.
3. Run `uv run python -m pytest -q tests/test_phase13_3_documentation_reproducibility.py`.
4. For service-backed product replay, use the retained Attempt 6 harness and current contract inputs; this package does not create a second E2E authority.

Expected product closure: persisted Artifacts, one Job-derived Workspace, exact typed viewers/Gallery, explicit Report Preview and UI Finalize, and a paired non-executable Recipe.

## Limits and negative boundary

- Diffusion is an estimate over the selected fit window.

- Negative: A stale trajectory source is rejected as WORKSPACE_SOURCE_NOT_CURRENT.
- This demonstrates current product-path reproducibility. It does not independently validate every numerical output.
