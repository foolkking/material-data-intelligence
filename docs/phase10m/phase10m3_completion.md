# Phase 10M-3 Completion State

Corrected implementation `fe5353f25e45eb10d3a78fa148727071e84d89e2`
passed exact-SHA CI run `30734974889`. Unit, Frontend typecheck/build and
L4/L5/M2/M3 browser replay, plus PostgreSQL/Redis/MinIO service-backed
integration with 39 passed and zero skipped, all succeeded. Completion-record
and queue-archive exact-SHA CI remain required before this document may state
archived.

Implemented surfaces: strict URL codec, Workspace-scoped store, formal panel
declarations, exact compatibility, origin-aware propagation, active-panel
navigation, Inspector, explicit Pin, typed stale/unsupported states, tests,
browser runner, and sanitized evidence.

Unchanged: Workspace contracts/version, migration head 0007, database schema,
API endpoints, Planner, AnalysisIntent, Eligibility, AnalysisPlan, Runtime,
Registry, Adapters, scientific calculations, interpretation, dependencies, and
lockfiles.
Phase 10M-4 remains reviewer-gated.

Failed implementation attempts remain part of the audit trail:

- `41c2d23ca5f1f29fccce07d06f7aceb676a26ae5` / `30733804796`: M2 browser
  semantic comparison included a nonsemantic DOM count, and the M3 service
  fixture omitted the ToolCall referenced by its Artifact.
- `c3c029effdd2f77ce5aac1b60041c582bc477e54` / `30734288153`: the Artifact FK
  was fixed, but the source Job was intentionally projected read-only because
  it lacked current 0.2 source identities.
- `9cb8fbc76d7d4808fd764196b9b4e5af0247fb54` / `30734708819`: integration
  reached the stale-selection assertion, which expected an obsolete status/code
  pair instead of the production `422 SELECTION_SCOPE_MISMATCH` contract.
