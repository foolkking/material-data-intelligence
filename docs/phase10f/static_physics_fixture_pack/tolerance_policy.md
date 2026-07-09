# Fixture Pack Numeric Tolerance Policy

This fixture pack follows `docs/phase10f/phase10f3_numeric_tolerance_policy.md`.

## Exact Checks

- `tool_id`
- schema version
- artifact filenames
- chart type
- security fields
- coordination histogram integer counts
- RDF integer counts
- deterministic resource-limit fields

## Tool Tolerances

| Tool | Field | Tolerance |
|---|---|---:|
| `structure.coordination_hist` | site count and histogram counts | exact |
| `structure.xrd` | selected `two_theta_deg` | `+-0.02` |
| `structure.xrd` | selected relative intensity | `+-0.5` |
| `structure.xrd` | selected d-spacing | `+-0.000001` |
| `structure.rdf` | `r_angstrom` grid | `+-0.000001` |
| `structure.rdf` | `bin_edges_angstrom` | `+-0.000001` |
| `structure.rdf` | selected `g_r` values | `+-0.000001` |

## Pending Numeric Values

Phase 10F-4 does not run replay verification. Numeric expected values in this pack are marked `pending_replay_generation` where they depend on platform replay output.

Tolerance must not be used to hide semantic changes. Any tolerance change requires explicit reviewer approval.

