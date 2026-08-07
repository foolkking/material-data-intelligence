# Phase 10N-1 Algorithm Parameters

The checked schema is `packages/schemas/json/phase10n1-coordination-contracts.schema.json`.
Both parameter objects use `additionalProperties: false`, finite-number validation,
bounded integer/number ranges, deterministic defaults and canonical serialization.

CrystalNN owns `distance_cutoff_low`, `distance_cutoff_high`, `x_diff_weight`,
`porous_adjustment`, `cation_anion`, `weighted_cn`, `max_structures`, `max_sites`,
`max_neighbors_per_site` and `max_retained_rows`. VoronoiNN owns
`tol`, `cutoff`, `allow_pathological`, `max_structures`, `max_sites`,
`max_neighbors_per_site` and `max_retained_rows`. The runtime stores resolved values
and their SHA-256 parameter hash in every artifact.

Upstream kwargs are not exposed. Unknown, negative, non-finite, reversed or unbounded
values are rejected before the scientific library is called.
