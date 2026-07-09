# Fixture Pack Provenance Policy

This fixture pack follows the Phase 10F-3 provenance policy.

## Labels

| Label | Meaning | Official PASS Eligible |
|---|---|---:|
| `official_direct` | Direct local input from an official pack, uploadable without transformation. | only after direct replay |
| `official_derived_manual` | Manually extracted official-derived input, no notebooks/scripts/API/network, reviewer approval required. | only after approval and direct replay |
| `official_like_curated` | Curated small fixture inspired by official semantics but not official. | false |
| `internal_regression` | Project-local fixture used for deterministic regression. | false |
| `mapping_only` | Conceptual mapping without direct-uploadable input. | false |
| `future_scope` | Deferred capability such as viewer, WebGL, Brillouin-zone, or phonon. | false |
| `unsupported` | Outside this fixture pack scope. | false |
| `unknown` | Provenance cannot be determined. | false |

## Phase 10F-4 Labels Used

All constructed Phase 10F-4 cases use `internal_regression`.

## Official PASS Rule

Only `official_direct` and reviewer-approved `official_derived_manual` can become official PASS after direct replay verification. `internal_regression` and `official_like_curated` are never official PASS by themselves.

