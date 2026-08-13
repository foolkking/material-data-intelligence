# Demo 6: Volumetric

## Goal and prompt

> Inspect this supplied volumetric grid and show its supported slice and volume views.

Prompt SHA-256: `1615a4f2a5e83f1c3bbfeea8d3cd77c30e291102caa8cdd4d0cfb9e09bc476ff`.

## Current user entry

Use the product Data/import surface for each fixture, then enter the prompt in the Planner. Normal users do not supply Tool, Plan, Job, Artifact, Workspace, or storage IDs.

- `docs/phase10j/fixtures/volumetric_parser/CHGCAR` | `1ea8ada56bec22e6b1f4caf3d24f048c980f3ea5ad5d355b8c7af36b152c953d` | 114 bytes | `parse`

## Required semantic coverage

- `structure.volumetric_data`

Every selected Tool must be individually eligible. Plan 0.2 is used only for real producer-Artifact-to-consumer dependencies; independent tools may remain Plan 0.1.

## Deterministic reproduction

1. Follow the [clean-checkout setup](README.md#mode-a-deterministic-reproduction).
2. Verify this contract with `uv run python scripts/generate_phase13_3_documentation_reproducibility.py`.
3. Run `uv run python -m pytest -q tests/test_phase13_3_documentation_reproducibility.py`.
4. For service-backed product replay, use the retained Attempt 6 harness and current contract inputs; this package does not create a second E2E authority.

Expected product closure: persisted Artifacts, one Job-derived Workspace, exact typed viewers/Gallery, explicit Report Preview and UI Finalize, and a paired non-executable Recipe.

## Limits and negative boundary

- Persisted bounded views do not imply Bader analysis, topological charge analysis, or browser-side scientific extraction.

- Negative: The frontend does not extract new scientific values from the grid.
- This demonstrates current product-path reproducibility. It does not independently validate every numerical output.
