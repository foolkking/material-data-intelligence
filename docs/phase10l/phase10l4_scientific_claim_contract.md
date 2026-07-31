# ScientificClaim 1.0

Claims are limited to `OBSERVATION`, `COMPARISON`, `ANOMALY`, `WARNING`,
`LIMITATION`, `RECOMMENDATION`, and `NO_SUPPORTED_CONCLUSION`. Predicates are
allowlisted and each claim carries exact supporting, limiting, or contradicting
evidence IDs, subject scope, structured payload, rendered text, and one of
`DIRECT`, `QUALIFIED`, or `LIMITED`.

Recommendations are non-executable: they contain no tool ID, parameters,
path, URL, code, Plan, Job, or enqueue authority. Narrative text cannot add a
number, unit, entity, threshold, or scientific conclusion absent from evidence.
