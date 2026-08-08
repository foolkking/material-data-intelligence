# Phase 10N-2 Parameter Contract

The checked JSON Schema is
`packages/schemas/json/phase10n2-local-environment-polyhedra.schema.json`. Python and
TypeScript contracts mirror the same snake-case runtime parameters. Unknown properties,
NaN, Infinity, duplicate site/reference values and out-of-range values are rejected.

Defaults: all sites, all catalog references, classification maximum distance `0.35`, tie
tolerance `0.01`, faces enabled, 5,000 sites, 64 neighbors/vertices, 32 reference checks,
128 faces and 16 MiB output. Canonical JSON of resolved defaults is SHA-256 hashed.
