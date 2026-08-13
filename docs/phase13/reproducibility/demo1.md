# Demo 1: Dataset Intelligence + Composition Space

## Goal and prompt

> Explore this materials dataset, summarize its quality, and map its compositions in composition space.

Prompt SHA-256: `f1a0ccdd06a9c1b02258a76247ae7e799388245b6bbca3e613444ae9d11cf0d0`.

## Current user entry

Use the product Data/import surface for each fixture, then enter the prompt in the Planner. Normal users do not supply Tool, Plan, Job, Artifact, Workspace, or storage IDs.

- `tests/fixtures/tables/formulas.csv` | `09f9d17fe6857e0ede385c9a442cacccc73e5a12f3b0b456201797f378fb2520` | 26 bytes | `parse`

## Required semantic coverage

- `dataset.composition_space`
- `dataset.materials_explorer`

Every selected Tool must be individually eligible. Plan 0.2 is used only for real producer-Artifact-to-consumer dependencies; independent tools may remain Plan 0.1.

## Deterministic reproduction

1. Follow the [clean-checkout setup](README.md#mode-a-deterministic-reproduction).
2. Verify this contract with `uv run python scripts/generate_phase13_3_documentation_reproducibility.py`.
3. Run `uv run python -m pytest -q tests/test_phase13_3_documentation_reproducibility.py`.
4. For service-backed product replay, use the retained Attempt 6 harness and current contract inputs; this package does not create a second E2E authority.

Expected product closure: persisted Artifacts, one Job-derived Workspace, exact typed viewers/Gallery, explicit Report Preview and UI Finalize, and a paired non-executable Recipe.

## Limits and negative boundary

- Composition-space PCA and clustering are descriptive, not material identity or scientific validation.

- Negative: A dataset-only goal must not force composition-space selection.
- This demonstrates current product-path reproducibility. It does not independently validate every numerical output.
