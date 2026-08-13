# Demo 3: Structure + coordination + local environment + polyhedra + experimental XRD

## Goal and prompt

> Inspect this crystal structure, map its CrystalNN local environment and coordination polyhedra, then compare the supplied experimental XRD peaks with its theoretical pattern.

Prompt SHA-256: `f7c06c5b1d7d1f1ceb55bbe48696fa16e45fe5707077d81f8b8a03583e20629e`.

## Current user entry

Use the product Data/import surface for each fixture, then enter the prompt in the Planner. Normal users do not supply Tool, Plan, Job, Artifact, Workspace, or storage IDs.

- `tests/fixtures/structures/simple_cubic.cif` | `cb832812e186173117b59fb0beb629375d89b2452679aa9a1a1070a7dcdb0f5e` | 382 bytes | `parse`
- `tests/fixtures/experimental_xrd/phase13_demo3_xrd.json` | `b62b79e7e580c772d7dce563fa8eeb0d1d15d0cc3db6fa614c4f1eb3008e4ae3` | 763 bytes | `parse`

## Required semantic coverage

- `structure.coordination_crystalnn`
- `structure.experimental_xrd_comparison`
- `structure.local_environment_polyhedra`
- `structure.xrd`

Every selected Tool must be individually eligible. Plan 0.2 is used only for real producer-Artifact-to-consumer dependencies; independent tools may remain Plan 0.1.

## Deterministic reproduction

1. Follow the [clean-checkout setup](README.md#mode-a-deterministic-reproduction).
2. Verify this contract with `uv run python scripts/generate_phase13_3_documentation_reproducibility.py`.
3. Run `uv run python -m pytest -q tests/test_phase13_3_documentation_reproducibility.py`.
4. For service-backed product replay, use the retained Attempt 6 harness and current contract inputs; this package does not create a second E2E authority.

Expected product closure: persisted Artifacts, one Job-derived Workspace, exact typed viewers/Gallery, explicit Report Preview and UI Finalize, and a paired non-executable Recipe.

## Limits and negative boundary

- Coordination and local environments are algorithm-derived. XRD is peak correspondence under wavelength/tolerance policy, not phase confirmation or Rietveld refinement.

- Negative: A wavelength mismatch is rejected; it is not reprojected or converted.
- This demonstrates current product-path reproducibility. It does not independently validate every numerical output.
