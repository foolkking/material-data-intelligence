# Demo 2: Materials ML

## Goal and prompt

> Evaluate these materials-model predictions and explain the largest errors and limitations.

Prompt SHA-256: `47579983daf0c517282ca11ab79d302aed3f49b762053c6c5a1752974e3dd30d`.

## Current user entry

Use the product Data/import surface for each fixture, then enter the prompt in the Planner. Normal users do not supply Tool, Plan, Job, Artifact, Workspace, or storage IDs.

- `tests/fixtures/tables/ml_results.csv` | `9473b499a846608123be135e8527e2144191c02c92e9147b84a3608326d4df3d` | 64 bytes | `parse`

## Required semantic coverage

- `dataset.materials_explorer`
- `ml.regression_evaluation`

Every selected Tool must be individually eligible. Plan 0.2 is used only for real producer-Artifact-to-consumer dependencies; independent tools may remain Plan 0.1.

## Deterministic reproduction

1. Follow the [clean-checkout setup](README.md#mode-a-deterministic-reproduction).
2. Verify this contract with `uv run python scripts/generate_phase13_3_documentation_reproducibility.py`.
3. Run `uv run python -m pytest -q tests/test_phase13_3_documentation_reproducibility.py`.
4. For service-backed product replay, use the retained Attempt 6 harness and current contract inputs; this package does not create a second E2E authority.

Expected product closure: persisted Artifacts, one Job-derived Workspace, exact typed viewers/Gallery, explicit Report Preview and UI Finalize, and a paired non-executable Recipe.

## Limits and negative boundary

- This is bounded evaluation of supplied predictions, not training, AutoML, SHAP, or a generalization guarantee.

- Negative: Do not interpret evaluation as model training or guaranteed generalization.
- This demonstrates current product-path reproducibility. It does not independently validate every numerical output.
