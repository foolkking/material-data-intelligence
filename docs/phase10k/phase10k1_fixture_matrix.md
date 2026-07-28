# Phase 10K-1 Fixture and Evidence Matrix

| Case | Input | Expected semantic result | Evidence |
| --- | --- | --- | --- |
| A material table | formula + density + band gap | formula and numeric property roles | `api/material_property_table.json` |
| B regression | target + prediction | complete regression group, product not implemented | unit/API |
| C uncertainty | target + prediction + std | data-ready uncertainty, product not implemented | `api/regression_uncertainty.json` |
| D multiple models | two prediction/std pairs | stable multiple predictions, no schema lock-in | unit |
| E ambiguous target | `y_true` + `target` | `AMBIGUOUS`, no silent selection | `api/ambiguous_regression.json` |
| F classification | target/prediction + probabilities | complete classification group and normalized rows | `api/classification.json` |
| G invalid formula | one invalid formula value | retained rows plus typed warning | regression API capture |
| H false positives | date/temperature/notes names | no semantic role | unit |
| I structure | real Si CIF upload | composition + structure resource semantics | `api/periodic_structure.json` |
| J legacy profile | 0.1 profile without additive fields | validates with empty semantic defaults | unit |
| K duplicate/missing ID | non-unique or missing sample ID | object-hash/row-index fallback | unit |
| L near cap | 4112 x 516 synthetic table | inspect 4096 x 512 and disclose both caps | performance capture |

## Browser Matrix

The local Playwright runner loads the actual PlannerWorkbench, uses only local
intercepted API responses, and validates semantic/readiness/warning text,
accessibility labels, no horizontal overflow, no iframe/external script/inline
handler, and zero console/page/network errors.

| Browser | Viewport | Required result |
| --- | --- | --- |
| Chromium | 1440 x 1100 | PASS |
| Firefox | 1440 x 1100 | PASS |
| WebKit | 1440 x 1100 | PASS |
| Chromium mobile | 390 x 844 touch | PASS |

Evidence root:
`docs/phase10k/evidence/phase10k1_material_data_profile_2/`.
