# Agent 2.0 Phase 1 Results

Date: 2026-08-22
Verdict: `PARTIAL` pending current-HEAD CI and archival closure

## Scope

Implemented the deterministic domain foundation without adding an Agent-2.0
LLM call or changing the existing Planner, Job, QueueWorkerRuntime, Tool
Registry, Adapter, Artifact, Viewer, Report, or Recipe execution kernel.

- Scientific Object logical identity, immutable versions, exact historical
  refs, relationships, project authorization, and service/repository layer.
- ResearchTurn, immutable explicit context snapshots, persisted lifecycle
  events, session sequence allocation, CAS state machine, receive/cancel/read
  services, and SSE projection.
- Pydantic v2 contracts with `extra="forbid"` for objects, context,
  requirements, capabilities, and results.
- Separate object-type, requirement, capability, result-projector, and
  progress-projector registries with startup validation of registered manifests.
- ScientificResultBundle validation and idempotent snapshot persistence.
- Additive REST APIs and regression tests; no UI redesign or new scientific
  capability.

## Migrations

The pre-change Alembic head was verified as `0014_research_session_run_bindings`.
The three ordered revisions are:

| Revision | Down revision | Tables |
|---|---|---|
| `0015_agent2_scientific_objects` | `0014_research_session_run_bindings` | `scientific_objects`, `scientific_object_versions`, `scientific_object_relationships` |
| `0016_agent2_research_turns` | `0015_agent2_scientific_objects` | `research_turns`, `research_context_snapshots`, `research_turn_events` |
| `0017_agent2_scientific_results` | `0016_agent2_research_turns` | `scientific_result_snapshots` |

The object migration creates the circular `current_version_id` FK after the
version table. The turn migration reuses real Session/Message/Planner/Job /
Interpretation/Report tables and conditionally omits only legacy FKs whose
parent table is genuinely absent in a partial SQLite fixture. Complete
production schemas receive all applicable FKs.

## Domain contracts

`ScientificObject` has UUID identity, string Project scope, stable `kind`,
namespaced `object_type`, lifecycle, current version, and row version.
`ScientificObjectVersion` has immutable version number, source and parent refs,
schema/payload refs, content and semantic hashes, metadata, and availability.
`ResearchTurn` stores Session sequence, exact message refs, action/status,
context/result/execution refs, error fields, and optimistic row version.
`ResearchContextSnapshot` is unique per Turn and immutable. `ScientificResultBundle`
uses independent execution/relevance statuses and validates fact locators,
result/fact IDs, Project scope, and object references.

New identity keys are UUIDs; existing project/session/user and execution IDs
retain their repository string types for compatibility.

## State machine

Implemented legal edges:

```text
RECEIVED -> RESOLVING_CONTEXT -> ORCHESTRATING
ORCHESTRATING -> NEEDS_CLARIFICATION | ANSWERED | UNSUPPORTED | READY_TO_PLAN
READY_TO_PLAN -> PLANNING -> PLAN_REJECTED | QUEUED
QUEUED -> RUNNING -> INTERPRETING -> COMPLETED | PARTIAL
```

Infrastructure failure is allowed from the early non-terminal states; supported
non-terminal states can be canceled. Terminal states cannot be revived. Every
transition requires expected status plus expected row version and increments
the row version atomically.

## API

- `POST /api/projects/{project_id}/research/sessions/{session_id}/turns` — 202 receive boundary.
- `GET /api/research/turns/{turn_id}` — bounded authorized turn view.
- `GET /api/projects/{project_id}/research/sessions/{session_id}/turns` — ordered cursor list.
- `POST /api/research/turns/{turn_id}/cancel` — authorized cancellation.
- `GET /api/research/turns/{turn_id}/events` — authorized persisted-turn SSE with `Last-Event-ID`.
- Read-only Scientific Object list/detail/version/relationship endpoints under `/api/projects/{project_id}/scientific-objects` and `/api/scientific-objects/{object_id}`.

The receive transaction writes exactly one existing user Message, one
`RECEIVED` Turn, and one `TURN_RECEIVED` event. No provider, Plan, Job,
ToolCall, or Artifact is created.

## Registry

The default ObjectType registry contains the ten existing-platform fixture
types listed in the implementation tests. Requirement, Capability, Result
Projector, and Progress Projector registries are usable skeletons; no claim is
made that all existing scientific Tools have been migrated to Agent 2.0
capabilities.

## Tests

| Check | Result |
|---|---:|
| Focused Agent2 contracts/migrations/domain/API | 21 passed |
| SQLite migration upgrade/downgrade/re-upgrade | 2 passed |
| Isolated PostgreSQL migration + service-backed concurrency/receive | 1 passed |
| Full Python non-integration regression | 1607 passed, 1 skipped |
| Full frontend Vitest suite | 84 files, 565 passed |
| Frontend typecheck | passed |
| Frontend production build (isolated output) | passed |
| Python compileall | passed |
| `git diff --check` | passed |

The isolated PostgreSQL check executed `0014 -> 0017 -> 0014 -> 0017`, then
verified all seven new tables, indexes, full production FK set, concurrent
version allocation, concurrent session sequences, CAS winner/loser behavior,
and the no-LLM/no-Job receive boundary. The first full-suite run found and
the implementation fixed a PostgreSQL 63-character constraint-name defect;
the second found only this report's then-missing link; the final rerun is
1607/1/0 (passed/skipped/failed) after the report link was added.

## Regression

Legacy Research Session, Message, Planner, Job, Worker, Tool Registry, Artifact,
authorization, and scientific tests remain in the full suite. Existing API
routes and execution authority were not removed or redirected.

## Explicitly not implemented in Phase 1

`NOT IMPLEMENTED IN PHASE 1`: Orchestrator LLM; ResearchTurnDecision;
DeepSeek/OpenAI structured output; semantic reference resolution; capability
eligibility/planner; capability-to-AnalysisPlan binding; Job attachment;
production result projector; Scientific Interpreter; grounding validator;
assistant final scientific response; Report Composer; complete historical Data
backfill; and professional Viewer integration.

## Risks / open items

- Current CI must run the newly included service-backed test on the pushed HEAD.
- Task archival is intentionally deferred until current-HEAD CI is green and
  the results record is committed.
- The compatibility branch for partial SQLite fixtures deliberately does not
  invent legacy parent tables; a fully upgraded production database retains
  the complete FK set.

## Verdict

`PARTIAL` — implementation and local verification are complete; CI/push and
TASKS archival remain open acceptance steps.
