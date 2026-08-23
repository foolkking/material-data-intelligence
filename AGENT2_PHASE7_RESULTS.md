# AGENT2_PHASE7_RESULTS

## Verdict

COMPLETE

## Starting State

- Starting HEAD and `origin/master`:
  `d0dc8768838fdd883067bc13a412d78bfe87bcfa`.
- Starting Alembic head: `0022_agent2_scientific_interpretation`.
- Phase 6 final closure CI was independently verified as run `32621739291`
  for `d0dc8768838fdd883067bc13a412d78bfe87bcfa`; all five jobs passed.
- Final Phase 7 closure head is `61553dadb28f9a40d07684edcba1e51e1da457d5`;
  `HEAD == origin/master` and current-head CI run `32656452081` passed all
  required jobs.

## Migration And Persistence

- Added `0023_agent2_research_memory`.
- Added durable `research_session_states` and auditable
  `research_session_context_items` tables.
- Session state uses optimistic versions; context items retain source-message,
  explicit-request, active/inactive, scope, and timestamp evidence.
- SQLite `0022 -> 0023 -> 0022 -> 0023` and fresh base-to-head passed.
- Final local Alembic heads/current: one head at
  `0023_agent2_research_memory`.

## Session Memory Model

`ResearchSessionMemoryService` persists explicit session constraints, goals,
and authorized pinned object/result references. Turn-only parameters are not
promoted to session state. Constraint override/clear deactivates the previous
auditable item. PostgreSQL-compatible repositories, not Redis, browser state,
or process globals, own the state.

## Context Compiler

The compiler preserves the current request, explicit references, effective
session constraints, pinned results, exact source identities, prior findings,
and unresolved questions before lower-value conversation prose. Provider views
use opaque `obj_N`, `result_N`, and `finding_N` keys; result database UUIDs are
excluded from the serialized compact context.

## Reference Resolution

The deterministic candidate order is explicit reference, UI selection,
current scope, previous-turn result, pinned context, recent context, then
bounded long-session retrieval. Same-priority ambiguous result selection is
rejected for clarification. Explicit result IDs are authorized against the
current project/session before they enter provider input.

Closure debugging fixed a cross-type priority defect: an explicit result now
outranks lower-priority historical object candidates, and same-priority result
ambiguity deterministically requires clarification.

## Long-session Retrieval

The v1 retriever is deterministic and reference-first. It filters by project,
authorization, lexical family/identity, pin state, and recency. Candidate
assembly reads at most 500 prior turns and exposes at most 16 result and 16
finding candidates; the compiler budget removes old prose before protected
constraints/references. No vector database or semantic SaaS was introduced.

## Result Reuse

Non-adjacent authorized results can enter the existing `INTERPRET_RESULT`
path. That Phase 6 path reuses the immutable snapshot and creates no Plan,
Job, ToolCall, Artifact, or ScientificResultSnapshot. Deterministic/unit
coverage confirms the zero-computation contract; a fresh service-backed
multi-turn measurement was not completed.

## Continuation

`CONTINUE_ANALYSIS` creates a new immutable ResearchTurn, records
`continuation_of_turn_id`, preserves explicit parameter overrides, and enters
the existing validated Phase 3-6 path. It does not patch an old AnalysisPlan or
replace an old Result. The dedicated fresh service-backed continuation run was
not completed.

## Clarification Continuation

A child turn can inherit only resolved/unresolved parent snapshot references.
A unique label match is elevated deterministically; otherwise candidates stay
in scope and ambiguity remains a clarification condition. Historical context
snapshots remain immutable.

## Exact-Version / Staleness Semantics

ScientificObject candidates retain exact version references and never upgrade
to the current version implicitly. Historical result candidates carry their
persisted relevance/staleness signal. A complete dynamic relevance replay for
all memory candidates remains part of the service-backed closure gap.

## Authorization Boundary

Session state, pin/unpin, explicit result references, and object references are
project-authorized before persistence or provider assembly. Cross-project
objects/results are rejected without exposing their details.

## Provider Boundary

The context is bounded and opaque. Raw Artifact payloads, provider transcripts,
secrets, Job/worker/Redis identities, and chain-of-thought are not included.
No new provider transport was added. Gated live DeepSeek qualification passed:
previous-result `INTERPRET_RESULT` and parameter-change `CONTINUE_ANALYSIS` each
used one provider call; same-priority ambiguity returned `CLARIFY` before any
provider call.

## Frontend Product Path

The existing Research page reads the bounded session-memory API and shows a
compact session-context strip for goal, constraints, and pinned item counts.
It does not expose UUIDs or runtime internals. Component tests cover the state;
authenticated browser checks passed at 1280x720 and 390x844 with document/body
scroll width equal to viewport width.

## No-Recompute Evidence

For the deterministic previous-result interpretation qualification:

```text
AnalysisPlan delta = 0
Job delta = 0
ToolCall delta = 0
Artifact delta = 0
ScientificResultSnapshot delta = 0
```

The fresh PostgreSQL/Redis/MinIO multi-process version of this measurement was
completed during Closure Round 2 and is promoted below.

## Closure Root Cause

The isolated fresh worker timeout was diagnosed with a DB-backed timeline and
`py-spy`: the Job was queued, but the child process blocked in
`psycopg.connect()` before any ToolCall or Artifact. Windows resolved
`localhost` to `::1` while the Docker PostgreSQL publication listened on IPv4.
The test-only URL helper now normalizes Windows PostgreSQL `localhost` to
`127.0.0.1`; the 180-second bound was not increased. The minimal fresh Phase 4
`127.0.0.1`; the 180-second bound was not increased. The minimal fresh Phase 4
case then passed and persisted the real ToolCall and Artifacts.

## Interpretation Closure Root Cause

- Failure stage: fresh Phase 6 interpretation worker schema validation, after
  the RQ task was consumed and after the persisted Result was reloaded.
- Exact violation: the Phase 7 `_safe_interpreter_fixture` supplied zero
  findings and zero primary/supporting ResultItem references. The frozen Phase
  6 contract requires at least one grounded finding and at least one ResultItem
  reference; this produced `INTERPRETATION_SCHEMA_INVALID`.
- Classification: fixture defect, not a Phase 6 production regression and not
  a Research Memory identity/persistence defect.
- Fix: the fixture now selects an actual persisted Fact and ResultItem from the
  loaded ScientificResultBundle, emits a non-quantitative statement, and
  references those persisted identities. No validator, schema, provider
  boundary, or raw Artifact path was weakened or changed.
- Phase 6 fresh RDF/XRD interpretation qualification after the fix: `2 passed`.

## Fresh Worker Timing

The old `177.98s / 180s` wall time included cold Windows process startup and
database/service initialization. The fresh execution helper now writes an
auditable readiness marker and measures the execution bound only after that
marker. A representative isolated RDF run recorded:

```text
startup/readiness: 6.844s
QUEUED -> RUNNING: 0.360s
RUNNING -> ToolCall: 0.765s
first Artifact: 1.360s
QUEUED -> terminal after readiness: 2.688s
execution timeout bound: 180.0s (unchanged)
```

No timeout inflation was used.

## Fresh Service-backed Golden Path

- RDF/XRD Phase 4 and Phase 5 fresh-process execution reached real committed
  Results after the loopback fix.
- Dedicated Phase 7 service selection now passes `4 passed, 0 skipped`: RDF
  non-adjacent reuse, XRD reuse, RDF real continuation, and stale exact-version
  interpretation.
- Independent interpretation workers consume identity-only RQ tasks and
  persist grounded final messages through PostgreSQL. No interpretation row is
  inserted by the fixture.

## Fresh Service-backed No-Recompute Evidence

RDF previous-result reuse:

```text
AnalysisPlan delta = 0
Job delta = 0
ToolCall delta = 0
Artifact delta = 0
ScientificResultSnapshot delta = 0
```

XRD previous-result reuse:

```text
AnalysisPlan delta = 0
Job delta = 0
ToolCall delta = 0
Artifact delta = 0
ScientificResultSnapshot delta = 0
```

Both paths created a new ResearchTurn and one grounded interpretation only.

## Fresh Service-backed Continuation Evidence

The RDF continuation qualification created a new child ResearchTurn with
`continuation_of_turn_id` set to the original RDF Turn. The validated plan
carried `cutoff_angstrom = 8.0` into the bound Tool parameter
`r_max_angstrom = 8.0`, then executed a real ToolCall, persisted a new Result
Snapshot, and completed interpretation. The original Turn, Plan, and Result
were reloaded unchanged.

## Exact-version / STALE Service Qualification

The stale case created a new current Structure version while retaining the
historical Result's exact source version. The fresh follow-up resolved the
historical Result, did not auto-upgrade to the new version, and retained the
`STALE` effective relevance status with zero computation delta.

## Tests

- Phase 7 deterministic memory: `8 passed`; live-gated contract tests with
  the credential: `3 passed`.
- Agent2 focused regression: `119 passed, 6 skipped`.
- Full backend after the final service-fixture rewrite:
  `1739 passed, 72 skipped`.
- Frontend: `85 files, 571 passed`.
- Typecheck: passed.
- Isolated production build: passed.
- `compileall`, `uv lock --check`, and `git diff --check`: passed.
- Migration round-trip and fresh SQLite base-to-head: passed.
- Dedicated Phase 6 service selection: `2 passed, 0 skipped`.
- Dedicated Phase 7 service selection: `4 passed, 0 skipped`.
- Current-head CI service-backed selection: `62 passed, 0 skipped, 0 failed,
  0 errors`, including all four dedicated Phase 7 service cases.
- Minimal fresh Phase 4 isolated execution: `1 passed`; readiness and execution
  timing are recorded above.
- Browser: authenticated Research view at 1280x720 and 390x844; no horizontal
  overflow (`document/body scrollWidth = innerWidth`).
- `npm run lint` is not claimed because the repository still invokes the
  deprecated interactive `next lint` path.

## Current-head CI

- Final SHA: `61553dadb28f9a40d07684edcba1e51e1da457d5`.
- Current-head run: `32656452081`.
- CI SHA exactly matched the final HEAD and all five required jobs passed.
- The service-backed selection included Phase 7 RDF reuse, XRD reuse, RDF
  continuation, and stale exact-version cases with zero selected skips.

## Not Implemented In Phase 7

Report Composer; Data Management mutations; full 62-tool capability mapping;
professional Viewer expansion; linked-selection expansion; Tool/plugin
ecosystem; global/cross-project personal memory; unbounded vector memory; and
the Phase 2 ORCHESTRATING lease/reaper.

## Exact Closure Gaps

None. The Windows IPv6 service-fixture defect and the Phase 6 fixture
grounding/schema defect were both fixed without increasing the scientific
execution timeout or weakening Phase 6 validators. Dedicated service,
deterministic, live-provider, regression, frontend, browser, migration and
current-head CI evidence is recorded above.

## Post-closure compatibility hardening

The current migration chain intentionally reserves `project_members` without
creating it. Authorization, login-role loading and secured project listing now
check table existence before issuing optional membership queries, eliminating
known PostgreSQL `relation does not exist` error noise while preserving the
owner-only fallback and savepoint protection for migration races. Focused access
and Agent2 API tests remain green (`20 passed`); no schema or authority change
was introduced.
