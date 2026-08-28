# Agent-2.0 Phase 14-R — Post-Seal Product Quality Remediation

Date: 2026-08-28

This file is the repository-authoritative execution contract for the user-
authorized Phase 14-R prompt. Phase 14 remains historically sealed at
`d03b0a2e86e50d834a774cf823cfe055c91cf10c`; this work is additive/fix-forward
and does not create or begin Phase 15.

## Mission and final state

Phase 14-R closes the gap between a technically qualified platform and a
mature scientific product that a researcher can understand, control, organize,
resume, audit and trust.

Required tracks, in dependency order:

1. R5 Context / Memory / Scientific Message Provenance 2.0.
2. R3 User Content and Lifecycle Management.
3. R4 Chat / Research Control.
4. R1 complete scientific surfaces and Viewer coverage.
5. R2 professional scientific Report quality.
6. R6 performance and product fluency.
7. R7 global search and organization.
8. R8 background tasks, notifications and recovery.
9. R9 privacy, Trash, retention and export.
10. R10 Agent and Report quality evaluation.
11. R11 operations, backup, monitoring and resource governance.
12. R12 real-user same-stack acceptance.
13. Full regression and P14R-A/P14R-B exact-SHA release seal.

Only after every mandatory P0 gate and every release gate passes may the
repository record:

```text
PHASE14 = SEALED
PHASE14_REOPENED = NO
FUNCTIONAL_PHASE14R_CLOSURE = PASS
AGENT2_PHASE14R = COMPLETE
SCIENTIFIC_SURFACE_COMPLETENESS = PASS
SCIENTIFIC_REPORT_QUALITY = PASS
USER_LIFECYCLE_MANAGEMENT = COMPLETE
CHAT_RESEARCH_CONTROL = COMPLETE
CONTEXT_PROVENANCE_2_0 = COMPLETE
PRODUCT_FLUENCY = PASS
GLOBAL_PRODUCT_ORGANIZATION = COMPLETE
BACKGROUND_TASK_RECOVERY = COMPLETE
RETENTION_EXPORT_GOVERNANCE = COMPLETE
AGENT_REPORT_QUALITY_EVALUATION = PASS
OPERATIONS_MATURITY = PASS
REAL_USER_PRODUCT_ACCEPTANCE = PASS
MATURE_PRODUCT_GAPS = NONE
READY_FOR_MATURE_PRODUCTION_USE = YES
PHASE15_CREATED = NO
PHASE15_STARTED = NO
```

## Frozen authorities

```text
ScientificObject = stable logical scientific identity
ScientificObjectVersion = immutable scientific state
ScientificResult = scientific fact authority
Presentation / Report = derived communication authority
Viewer = read-only exact-version projection
LLM = orchestrator/explainer, never numeric or provenance authority
```

No in-place scientific mutation, silent latest substitution, duplicate
scientific authority, arbitrary Python/shell/network execution, unbounded
Provider context, arbitrary Pack UI, remote executable plugins or scientific
facts created by the frontend.

## Stage 0 — product reality audit

Create and maintain:

```text
docs/agent2/phase14r/PHASE14R_PRODUCT_REALITY_AUDIT.md
```

Inventory actual ScientificObject types, version semantics, Artifact contracts,
Tools, Capability Packs, Result projectors, Presentation mappings, Viewer
renderers, Evidence, Reports, conversation/context, lifecycle operations,
background tasks, search, performance, recovery and operations. Status is
strictly `PASS`, `PARTIAL`, `FAIL`, `NOT_QUALIFIED` or `N/A`.

## R1 — scientific surface completeness

Create:

```text
docs/agent2/phase14r/SCIENTIFIC_SURFACE_COVERAGE_MATRIX.md
```

Derive the matrix from current Registry, Packs, Artifact contracts and Viewer
registry. Cover all declared Dataset/table/composition/ML, Structure and
coordination, RDF/MSD/diffusion/trajectory, XRD, phonon/BZ, volumetric,
electronic Band/DOS and all other declared families. For every capability
record input/profile/readiness, Tool, Artifact, Result projector, Presentation,
Viewer/Figure/Table/Evidence/Report, desktop/mobile, historical/archive,
performance, security and status.

Every supported user-visible surface requires a real same-stack product path.
A route returning 200, a registry entry or renderer unit test is not sufficient.
Viewer scientific content, labels, units, series, selection, warnings,
limitations, exact source, historical behavior, mobile behavior and
interactions must be verified. Viewer navigation must yield zero Job,
ToolCall, scientific Artifact and Result deltas.

## R2 — scientific Report quality

Create:

```text
docs/agent2/phase14r/SCIENTIFIC_REPORT_QUALITY_RUBRIC.md
```

The rubric covers question/background, objective, exact data scope, methods,
findings, metrics, Figures, Tables, Evidence, synthesis, discussion,
limitations/uncertainty, conclusion, next steps, readability/coherence, no raw
dump, no unsupported claim and exact version preservation.

Define a bounded operation-specific `ReportContextBundle` containing authorized
intent/question/objective, exact sources, selected Results/Findings/Metrics,
Figures/Tables/Viewer/Evidence refs, methods summary, validated interpretations,
limitations/warnings, relevant comparisons and user-selected scope. Never pass
the raw full conversation, raw Tool logs, unbounded Artifacts or secrets.

Report lifecycle supports `DRAFT`, `FINALIZED`, `ARCHIVED`, `TRASHED`.
Finalized snapshots are immutable; editing creates a revision/new draft.
Where appropriate provide rename, pin, duplicate, revision, archive, trash,
restore, export, source Research/Result navigation and revision comparison.
Report quality improvements reuse the same Result with zero scientific
recomputation.

## R3 — lifecycle management

Use coherent states:

```text
ACTIVE
ARCHIVED
TRASHED
PURGED
```

Audit entity actions for Project, Dataset/ScientificObject, immutable Version,
Research Session/Conversation, immutable ResearchTurn/ScientificResult and
Report. Provide safe rename/pin/archive/trash/restore/duplicate/branch/export/
bulk operations where appropriate.

Before destructive operations, return a server-derived dependency impact
preview. Permanent deletion is fail-closed and requires authorization,
dependency scan, irreversibility warning and explicit confirmation. Referenced
immutable scientific versions remain protected. Garbage collection deletes
only genuinely orphaned records. Organizational tags, collections, pins and
saved views remain non-scientific metadata.

Create:

```text
docs/agent2/phase14r/USER_LIFECYCLE_MANAGEMENT_CONTRACT.md
```

## R4 — chat/research control

Create:

```text
docs/agent2/phase14r/CHAT_RESEARCH_CONTROL_CONTRACT.md
```

Support latest-user-message edit through immutable revision/branch semantics,
conversation branching and exact branch restoration. Do not mutate historical
messages or ResearchTurns with descendants.

Support truthful cancellation across orchestration/planning, queued and running
execution with `CANCELING`, `CANCELED` or `PARTIAL` semantics. Preserve already
committed valid independent outputs and clearly identify incomplete branches.
After stop expose distinct Continue, Modify, and Rerun actions.

`Continue` reuses authorized exact context/results when valid. `Rerun` creates
new execution lineage. `Re-interpret` changes only grounded interpretation and
must create zero Job/ToolCall/Artifact/Result deltas. Retry preserves failed
evidence and makes new lineage/reuse explicit. Conversational regenerate and
scientific reinterpret/rerun must remain distinct.

## R5 — context provenance 2.0

Create:

```text
docs/agent2/phase14r/RESEARCH_CONTEXT_PROVENANCE_2_0.md
```

Before each meaningful Provider call persist an auditable server-side
`ContextManifest` with operation, project/session/turn, policy version,
included/excluded items, token estimates/budgets, output reserve, repair
margin, compaction/truncation state, fingerprint and timestamp.

Each `ContextItem` records kind, server identity, opaque Provider ref,
authority class, exact object/version, Result/Finding/message revision refs,
inclusion reason and selection mode, authorization, fingerprint/tokens,
compaction/truncation and supersession.

Authority classes distinguish user assertions/preferences/constraints,
conversational narrative, scientific data/result/finding/evidence, runtime
state and derived summary. Repeated user text never becomes a Result.

Use operation-specific Orchestrator, Planner, Worker, Interpreter, Data and
Report contexts. Define checked-in ContextBudgetPolicy 2.0 from actual provider
limits and measured payloads. Preserve current request, exact scientific IDs,
critical constraints, quantitative facts, units and evidence under overflow.
Compact only safe narrative; disclose inability to fit critical context.

Provide bounded Used Context UX, pin/unpin/use/remove/compare controls, explicit
fresh-vs-continue semantics, immutable message revision provenance and
historical context replay without exposing prompts or chain-of-thought.

## R6 — performance/product fluency

Create:

```text
docs/agent2/phase14r/PERFORMANCE_PRODUCT_FLUENCY_BASELINE.md
```

Measure cold/warm navigation, lists, Dataset query, Research acknowledgement,
first truthful progress, planning, queue wait, Viewer metadata/usable, Report,
History, search, cancel and mobile. Establish evidence-based SLOs. Use
metadata-first/lazy loading, bounded payloads, virtualization, progressive
disclosure, truthful persisted progress and correct WebGL/request cleanup.
Add stable timing/payload/query/render/resource budgets without relying solely
on noisy microbenchmarks.

## R7 — search/organization

Provide authorized unified search over appropriate Projects, Datasets,
ScientificObjects, formula/sample identity, Research, Results, Findings and
Reports. Support type/project/date/status/object-type/archive filters and
appropriate tags/pins/collections/saved searches. Search is navigation, never
scientific authority; cross-project metadata leakage is forbidden.

## R8 — background tasks/recovery

Provide a global task center distinct from Research Timeline for Research,
import and Report work, using actual Queued/Running/Canceling/Completed/Partial/
Failed/Canceled state. Provide bounded persistent notifications. Leaving and
returning rebuilds state from the backend. Network/SSE/API/worker/Redis/MinIO
interruptions expose truthful reconnect/recovery without marking server work
failed merely because the browser disconnected.

## R9 — privacy/retention/export

Define retention and deletion policy for Trash, Projects, conversations,
Reports, Artifacts, scientific provenance and audit records. Provide Trash
inspection/restore/permanent-delete where allowed. Distinguish workspace
deletion from protected provenance. Support useful source, Result table,
Figure, Report, transcript, provenance-manifest and analysis-metadata export.
Where feasible produce a non-executable reproducibility package with exact
refs, versions, parameters, checksums and limitations.

## R10 — Agent/Report quality evaluation

Create:

```text
docs/agent2/phase14r/AGENT_REPORT_QUALITY_EVALUATION.md
```

Maintain a versioned representative materials-science evaluation set spanning
major capability families, ambiguity, multi-step work, continuation/reuse,
history, partial failure, unsupported requests, wrong assumptions, large data,
synthesis and stop/edit/rerun. Evaluate intent/context/clarification/capability/
plan/over- and under-analysis/grounding/usefulness/relevance/limitations/
naturalness/latency. Evaluate several real Reports with the R2 rubric.
LLM-as-judge is supplemental only.

## R11 — operations/recovery/resource governance

Create:

```text
docs/agent2/phase14r/OPERATIONS_AND_RECOVERY_QUALIFICATION.md
```

Qualify safe PostgreSQL backup/restore and post-restore identity, MinIO backup/
restore/checksum/missing-object behavior, Redis restart semantics, API/DB/queue/
worker/job/artifact/provider/SSE/latency/error monitoring, bounded correlation
from Turn through Report, upload/Dataset/Artifact/concurrency/LLM/queue limits,
and typed user-facing quota messages. Run drills only in safe qualification
environments.

## R12 — real-user acceptance

Use authenticated browser, real frontend/API, PostgreSQL, Redis, MinIO, real
workers and configured provider. Exercise every R1-supported capability and the
canonical product journeys: Project/data/ingestion/discovery/Data→Research,
Structure/coordination/XRD/trajectory/RDF/MSD/diffusion/phonon/BZ/volumetric/
electronic/Dataset/ML/composition as actually supported, Viewer/Evidence/Report,
historical v1/v2, archive/restore, reuse, edit/branch, stop/continue/rerun/
reinterpret/retry, lifecycle/dependency/bulk, search, task center, reconnect,
context transparency/fresh/continue, Report revision/export, mobile and
near-limit performance.

Every claim must carry exact persisted IDs where applicable. Desktop is
1280×720; mobile is 390×844. Real-user review covers project/source/context/
progress/control/history/lifecycle/provenance/Result/Viewer/Report/warnings/
responsiveness/recovery/trust. Read-only Presentation/Viewer/Evidence/Report/
History/Search/Context disclosure must create zero scientific records.

Create:

```text
docs/agent2/phase14r/PHASE14R_MATURE_PRODUCT_COVERAGE_MATRIX.md
```

## Required tests and qualification

Add deterministic coverage for message revisions/branching/edit, cancellation
at every stage and partial output preservation, continue/rerun/reinterpret/
retry, lifecycle/dependency/bulk/hard-delete safety, ContextManifest/items/
authorization/priority/compaction/overflow/fresh/continue, ReportContextBundle/
quality/revision, search authorization, task/reconnect recovery, quotas and
Viewer surface mappings.

Run fresh:

```text
Phase 1–14 regression
Phase 14-R focused
Agent2 / Data Platform / lifecycle / context / Packs
Viewer / Presentation / Evidence / Report / History / security
real PostgreSQL/Redis/MinIO service-backed campaign (mandatory skipped = 0)
full backend
full frontend
typecheck
production build
compileall
uv lock --check
touched Ruff
git diff --check
```

Repeat representative flows and inspect DB connections, memory/resources,
duplicate API requests/Jobs/ToolCalls/Results, listeners/WebGL, queues and
orphans. After campaigns record DB pool, queue, workers, stuck jobs and MinIO
errors.

## Required artifacts

Maintain all of:

```text
docs/agent2/phase14r/PHASE14R_PRODUCT_REALITY_AUDIT.md
docs/agent2/phase14r/SCIENTIFIC_SURFACE_COVERAGE_MATRIX.md
docs/agent2/phase14r/SCIENTIFIC_REPORT_QUALITY_RUBRIC.md
docs/agent2/phase14r/RESEARCH_CONTEXT_PROVENANCE_2_0.md
docs/agent2/phase14r/USER_LIFECYCLE_MANAGEMENT_CONTRACT.md
docs/agent2/phase14r/CHAT_RESEARCH_CONTROL_CONTRACT.md
docs/agent2/phase14r/PERFORMANCE_PRODUCT_FLUENCY_BASELINE.md
docs/agent2/phase14r/AGENT_REPORT_QUALITY_EVALUATION.md
docs/agent2/phase14r/OPERATIONS_AND_RECOVERY_QUALIFICATION.md
docs/agent2/phase14r/PHASE14R_MATURE_PRODUCT_COVERAGE_MATRIX.md
AGENT2_PHASE14R_RESULTS.md
```

`AGENT2_PHASE14R_RESULTS.md` uses sections A–T from Incoming Seal through Final
Verdict. Every PASS requires exact evidence; NOT VERIFIED cannot become PASS.

## Release gates

Do not create P14R-A until all mandatory functional boxes are green. Stage only
intended Phase 14-R code/tests/docs and preserve unrelated files. Push normally
and require exact-SHA CI including real service-backed integration:

```text
P14R_A_CI_SHA == P14R_A_SHA
```

After it passes, finalize evidence, create P14R-B, push and require:

```text
HEAD == origin/master
P14R_B_CI_SHA == HEAD
required jobs = PASS
```

If a later evidence-only commit is necessary, it must also receive exact-current
HEAD CI. Phase 15 remains uncreated and unstarted.

## Safety and stop rule

Do not reset/clean, stage blindly, overwrite user files, weaken tests, use
SQLite/mock/skip as final evidence, or delete scientific provenance. Solve
ordinary code/schema/runtime/UI/test/operations defects autonomously. Stop only
for a genuine external credential/infrastructure/permission or irreversible
product-authority decision blocker, with exact evidence and minimum requested
input.

