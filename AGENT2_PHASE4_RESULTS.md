# Agent 2.0 Phase 4 Results

Date: 2026-08-23
Starting HEAD: `eaa343a66fb5ab7086e43334d49c3ae654e20aa7`
Verdict: `PARTIAL` (implementation complete; current-HEAD CI pending)

## Scope

Implemented the deterministic bridge from an immutable `PLAN_READY`
ResearchTurn to the existing Job/QueueWorkerRuntime execution path, exact
ScientificObjectVersion source hydration in a fresh Worker, Turn/Job lifecycle
supervision, immutable terminal ExecutionSummary projection, cancellation
reconciliation, bounded product progress/SSE, incremental declared Artifact
availability, and a compact responsive Research activity surface.

The execution path never reruns the Orchestrator or Capability Planner, never
changes the attached AnalysisPlan, and never calls an LLM. Success and partial
execution stop at `RESULT_PENDING`; no ScientificResult or final assistant
answer is produced.

## Migration

`0020_agent2_execution_integration` follows
`0019_agent2_capability_planning`. It adds `CANCELING` and `RESULT_PENDING` to
the ResearchTurn status check, enforces one Agent2 Turn per existing Job, and
creates `research_execution_summaries`. The table has unique Turn and Job
constraints, an execution-outcome check, stable source fingerprint, projector
version and immutable summary JSON.

## Job Bridge

The dispatcher loads the exact attached AnalysisPlan and CapabilityPlan,
reauthorizes exact source versions, creates one existing Job, atomically
attaches it to the Turn, commits `PLAN_READY -> QUEUED`, and only then publishes
the existing `job_id` to Redis/RQ. Repeated and concurrent dispatch reuse the
same Job. Queue publication failure remains recoverable without creating a
second Job.

The existing Job repository, QueueWorkerRuntime, dependency execution,
ToolCall persistence, ArtifactStorage and JobEvent sequence remain
authoritative. A fresh Worker reconstructs normalized object inputs from
PostgreSQL and MinIO/S3 using the exact version and verified checksum; a later
logical current version is never substituted.

## State Transitions

Implemented `PLAN_READY -> QUEUED`, real Job-backed `QUEUED -> RUNNING`, and
terminal `SUCCESS/PARTIAL -> RESULT_PENDING`. Fast Jobs may recover directly
from `QUEUED` to `RESULT_PENDING`. Complete failure maps to `FAILED`.
`QUEUED/RUNNING -> CANCELING` records only cancellation intent;
`CANCELING -> CANCELED` requires confirmed runtime cancellation, while a
terminal success/partial race is preserved as `RESULT_PENDING` with a warning.

## ExecutionSummary

`ResearchExecutionSummary 1.0` records exact Turn, AnalysisPlan and Job
identities, deterministic step statuses, declared output Artifacts, warnings,
terminal timestamps, source fingerprint and projector version. Outcome
classification uses required AnalysisPlan steps and usable declared outputs,
not the Job status string alone. Replaying identical terminal facts is
idempotent; a conflicting fingerprint fails closed.

## Scientific Progress

Registered capability progress projectors map CapabilityPlan steps through the
persisted AnalysisPlan to real ToolCalls and declared Artifacts. The product
view exposes scientific labels and step/output state, while omitting Tool,
ToolCall, Job, queue, worker and provider internals. SSE supports reconnect by
ResearchTurnEvent sequence. Incremental output is emitted only after the
Artifact commit and may be visible before Job terminal.

## Canonical Executions

- RDF: real Agent2 Phase 2 -> Phase 3 -> dispatch -> fresh subprocess Worker
  against PostgreSQL, Redis and MinIO; exact source hydration, real ToolCall,
  Artifacts and `RESULT_PENDING` verified.
- XRD: real Phase 2 -> Phase 3 -> dispatch -> fresh subprocess Worker execution
  against PostgreSQL, Redis and MinIO. The two-step theoretical-XRD/comparison
  DAG completed successfully, and the first-step Artifact was observed while
  the Job was still `running` behind a test-only synchronization barrier.
- ML regression, trajectory and phonon: existing runtime suites remain the
  scientific execution authority; Phase 4 adds generic registered progress and
  lifecycle coverage without fabricating new datasets or algorithms.

Incremental Artifact/output observed before Job terminal: `YES`. The real XRD
fresh-worker qualification observed the committed theoretical-pattern output
before releasing the Worker to execute comparison step 2. At that observation
point the persisted Job remained non-terminal and no `RESULT_PENDING` event
existed.

## No-LLM and No-Early-Result Evidence

The Phase 4 dispatcher, Worker, supervisor, progress and cancellation paths do
not resolve or invoke StructuredLLMClient. Execution-stage LLM calls: `0`.
The fresh-worker acceptance asserts Agent2 ScientificResultSnapshot delta `0`
and `assistant_final_message_id = null` after success.

## Tests

- Focused Phase 4 backend/API/exact-source: `21 passed`.
- Phase 2 context/processor regression after multi-selection correction:
  `27 passed`.
- Complete non-integration backend: `1671 passed, 6 skipped, 86 deselected`.
- Fresh PostgreSQL/Redis/MinIO service-backed CI selection: `54 passed,
  14 deselected`, with zero selected tests skipped.
- Complete frontend Vitest: `85 files, 568 passed`.
- Frontend typecheck and isolated production build: passed.
- Python compileall, `uv lock --check`, scientific replay and
  `git diff --check`: passed.
- Browser evidence: 1440x900 and 390x844 passed, including one mobile panel,
  44px cancel control and no horizontal overflow.

Current-HEAD GitHub Actions remains pending, so this report does not claim the
Phase complete yet. `npm run lint` remains an obsolete interactive `next lint`
command and is not declared passing.

## Known Limitations / Not Implemented in Phase 4

Production ScientificResult projection; ScientificFact/Figure/Table and
Artifact semantic result roles; result relevance recalculation; Scientific
Interpreter; grounding validator; assistant final scientific response; Report
Composer; long-session semantic memory; Phase 2 ORCHESTRATING lease/reaper;
Data Management mutations; full 62-Tool capability mapping; professional
Viewer/link-selection expansion; and Tool/plugin ecosystem are not implemented.
Phase 5 begins from `RESULT_PENDING` and owns deterministic ScientificResult
projection.
