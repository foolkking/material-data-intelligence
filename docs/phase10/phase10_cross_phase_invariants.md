# Phase 10 Cross-Phase Invariants

| Invariant | Producer | Enforcement | Evidence |
| --- | --- | --- | --- |
| formal viewer ID is unique | Tool Registry | manifest and closure tests | registry/runtime snapshot |
| natural viewer intent selects `structure.viewer_3d` | Mock Planner | routing and negative tests | live planner capture |
| executable plans are persisted and validated | Planner/PlanValidator | runtime closure | plan/job/events capture |
| current viewer output is scene v2/manifest v2 | adapter | canonical validators | artifact closure |
| periodic endpoint and bond ordering is stable | adapter contract | deterministic replay | replay snapshot |
| legacy never regains current periodic semantics | compatibility registry | backend/frontend gates | legacy matrix |
| renderer-local state does not mutate science | frontend mapper | composition tests | export/view-state snapshots |
| over-budget scenes stop before allocation | performance policy | frontend/browser assertions | fallback matrix |
| artifacts provide no viewer execution authority | schemas/security | strict mapping and scans | security audit |
| three-browser/mobile product path remains viable | browser runner | evidence integrity checker | browser/mobile matrix |

The machine-readable matrix is committed under the closure evidence directory
and is validated in CI. Candidate XRD/RDF/coordination results remain candidate
scientific outputs; this pack does not promote them to benchmark certification.
