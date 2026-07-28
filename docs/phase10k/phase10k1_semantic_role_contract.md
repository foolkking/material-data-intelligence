# Phase 10K-1 Semantic Role Contract

## Authority Order

1. `explicit_metadata`: trusted normalized-object metadata with an allowlisted
   role and compatible dtype.
2. `user_declared`: an explicit declaration passed through a reviewed ingestion
   contract, also dtype-validated.
3. `canonical_name`: an exact canonical column name.
4. `alias_match`: an exact member of the central bounded alias registry.
5. `bounded_pattern`: one anchored regex with length limits for model/property
   series or class probabilities.
6. unknown: no role is assigned.

No numerical confidence score is produced. Multiple valid targets or multiple
formula candidates are disclosed as ambiguity instead of being silently
ranked. All role strings are enum-like application-owned values.

## Roles

| Role | Meaning | Dtype / value guard | Grouping |
| --- | --- | --- | --- |
| `material_formula` | parseable composition/formula candidate | string; pymatgen parsing is bounded | no model group |
| `material_property` | conservative approved property column | numeric; no unit inference | no model group |
| `sample_identity` | candidate stable row identity | any scalar; must be unique and complete to become authority | no model group |
| `regression_target` | numeric reference value | numeric and finite sample | regression group |
| `regression_prediction` | numeric model prediction | numeric and finite sample | regression group |
| `regression_uncertainty` | source-defined numeric uncertainty | numeric and finite sample | regression group |
| `classification_target` | source class label | scalar | classification group |
| `classification_prediction` | predicted class label | scalar | classification group |
| `class_probability` | probability for one source-defined class | numeric, finite, [0,1], row sum tolerance `1e-6` | classification group |

## Central Alias Registry

The implementation owns one canonical-name table and one alias table in
`semantic_profile.py`. Representative aliases are:

| Alias | Role | Constraint |
| --- | --- | --- |
| `composition`, `chemical_formula`, `pretty_formula`, `reduced_formula` | `material_formula` | string |
| `target`, `actual` | `regression_target` | numeric |
| `prediction`, `pred`, `predicted` | `regression_prediction` | numeric |
| `uncertainty`, `std`, `sigma` | `regression_uncertainty` | numeric |
| `label`, `class_label`, `true_label` | `classification_target` | scalar |
| `predicted_label` | `classification_prediction` | scalar |
| `material_id`, `structure_id`, `id` | `sample_identity` | complete + unique for identity authority |

Anchored patterns recognize `<series>_(true|target|pred|prediction|std|sigma|uncertainty)`
and `prob[_:.-]<class>`. Names are capped at 256 characters. Strings such as
`prediction_date`, `target_temperature`, and `formula_notes` do not match.

## Group Rules

- canonical `y_true`, `y_pred`, and `y_std` share the default regression group;
- a bounded series or property prefix such as `model_a_pred`/`model_a_std` or
  `band_gap_true`/`band_gap_pred` creates a distinct object-scoped group;
- one canonical target may be shared by deterministic model-series groups;
- `seriesBindings` retains each prediction/uncertainty pairing, while generic
  unscoped uncertainty is not guessed onto multiple models;
- multiple prediction groups are retained in stable order;
- more than one target in one group yields `AMBIGUOUS`;
- missing target or prediction yields `INCOMPLETE`;
- probability columns augment the classification group but do not invent class
  labels, normalization, or a prediction column.

The old `tableSummary.inferredRole` allowlist is deliberately frozen and is not
expanded by these Profile 2.0 rules, preserving existing Planner behavior.

Explicit group IDs and units are bounded to 128 and 64 characters respectively;
invalid metadata is disclosed and cannot create cross-object group collisions.
