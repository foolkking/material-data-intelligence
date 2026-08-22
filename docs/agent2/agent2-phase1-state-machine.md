# Agent 2.0 Phase 1 State Machine

The database is canonical. Redis and future queues may carry only a `turn_id`;
they do not own state. Every transition uses expected status and expected
`row_version`, then increments the version with a compare-and-set update.

## Allowed graph

```text
RECEIVED -> RESOLVING_CONTEXT -> ORCHESTRATING
ORCHESTRATING -> NEEDS_CLARIFICATION | ANSWERED | UNSUPPORTED | READY_TO_PLAN
READY_TO_PLAN -> PLANNING
PLANNING -> PLAN_REJECTED | QUEUED
QUEUED -> RUNNING
RUNNING -> INTERPRETING
INTERPRETING -> COMPLETED | PARTIAL
```

`RECEIVED`, `RESOLVING_CONTEXT`, `ORCHESTRATING`, `READY_TO_PLAN`, and
`PLANNING` may also fail with an explicit infrastructure error. Cancellable
non-terminal states may move to `CANCELED`. All terminal states reject revival.

## Events

Phase 1 emits only persisted lifecycle evidence that exists today:
`TURN_RECEIVED`, `CONTEXT_RESOLUTION_STARTED`, `CONTEXT_RESOLVED`,
`TURN_CANCELED`, and `TURN_FAILED` (plus state-machine test fixtures). It does
not masquerade as an LLM, Job, ToolCall, Artifact, or interpretation event.

## Registries

Object types, requirements, capabilities, result projectors, and progress
projectors each have a small explicit registry. Startup validates only
registered capability manifests: requirement/object type/ToolBinding/projector
references, duplicate IDs, and active capability bindings. Existing platform
Tools are not rewritten as Agent 2.0 capabilities in this phase.

## Not implemented in Phase 1

Orchestrator LLM, `ResearchTurnDecision`, semantic reference resolution,
capability eligibility/planning, capability-to-AnalysisPlan binding, Job
attachment, production result projection, interpretation, grounding,
assistant response composition, full backfill, and professional Viewer
integration are intentionally deferred.
