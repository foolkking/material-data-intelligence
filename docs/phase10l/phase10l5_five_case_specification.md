# Phase 10L-5 Five-Case Specification

The machine-readable source is `docs/phase10l/evidence/phase10l5_natural_language_closure/case_specs.json`.
Each case has exact Profile/resource scope, an approved tool domain, forbidden
fallbacks, and a required execution/interpretation outcome.

| Case | Domain | Required real path | Forbidden behavior |
|---|---|---|---|
| 1 | Dataset composition, property coverage, anomaly candidates | `dataset.materials_explorer` | ML metrics or composition-space substitution |
| 2 | Crystal structure reasonableness facts | `structure.summary` | Viewer selection or correctness/stability claim |
| 3 | Materials ML model performance | `ml.regression_evaluation` | Generic metrics substitution |
| 4 | Phonon calculation | `phonon.band` + `phonon.dos` -> `phonon.band_dos` | Missing dependency or unrelated tool fallback |
| 5 | Volumetric charge density | `structure.volumetric_data` | Structure viewer substitution, Bader or charge-transfer claim |

The five cases are executed with deterministic Mock in default CI and with
DeepSeek in the local gated verification. The live gate requires every case to
produce a READY Intent, a PLAN_READY selection, a persisted plan/job, actual
Runtime artifacts, grounded evidence, and a successful interpretation. A live
case is independently capped at twelve real calls.
