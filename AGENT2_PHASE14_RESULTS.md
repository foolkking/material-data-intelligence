# Agent-2.0 Phase 14 — Full Platform Integration & Production Qualification

Qualification date: 2026-08-28

## A. Stage 0

### A1. Phase 13 Final Seal

```text
PHASE13_SEALED_BASE = 56c096a98d082f2ee145c4a1ca4fd89b8d4538df
Phase 13 exact-current-head CI = 33135877741
PHASE13_REOPEN_REQUIRED = NO
```

### A2. Phase 14 Base

```text
PHASE14_BASE = 56c096a98d082f2ee145c4a1ca4fd89b8d4538df
PHASE14_STAGE0 = normalized Phase 13 provenance and established coverage ledger
Alembic head = 0025_agent2_scientific_selection
```

## B. Platform Coverage

The complete coverage ledger is recorded in
`docs/agent2/phase14/PHASE14_COVERAGE_MATRIX.md`. It covers authentication,
projects/authorization, Data Platform ingestion and versioning, typed Dataset
query and sample identity, Data → Research, ResearchTurn/context/planning,
real worker execution, ScientificResult/interpretation/presentation, Structure
and Band/DOS viewers, Table/Materials Explorer, Figure, Evidence, Report,
History/resume, historical v1/v2, archive/restore, exact reuse, trusted Packs,
unsupported execution, responsive UX, runtime and CI.

### B1. Authority Map

```text
PostgreSQL: Project, ScientificObject, ScientificObjectVersion, ResearchTurn,
            Job/ToolCall/Result/Report relationships
MinIO:     persisted source bytes and scientific Artifacts
Redis:     queue/cache transport
ScientificResult: scientific fact authority
Presentation/Report: deterministic derived communication projections
Viewer:    read-only exact source/version projection
History:   explicit researchTurnId when persisted; legacy Job parsing is fallback only
```

### B2. Cross-surface identity evidence

The live service-backed Workspace projection resolved:

```text
Job = job_agent2_d62512c9ef6d43078ccc9bd525fb052f
ResearchTurn = d62512c9-ef6d-4307-8ccc-9bd525fb052f
```

through the persisted `research_turns.job_id` relation. Project Overview and
Workspace return navigation now carry that authoritative Turn identity.

### B3. Remaining Unsupported/N/A Areas

No mandatory major product flow remains unqualified. DOS is covered by the
existing persisted electronic artifact/viewer path; ingestion and version
creation are desktop/service-backed because upload is not a mobile-first
operation.

## C. Data

### C1. Ingestion

Real Dataset/resource ingestion, MinIO storage, parser/profile admission and
same-object immutable version creation remain proven by Phase 12 service
qualification.

### C2. Object/Version

Canonical Structure lifecycle remains:

```text
Object = 773089f9-3ce8-4645-92dd-2f62c64cba89
v1     = 65f56d10-008d-445d-ab2f-228aebf1835b
v2     = 2538cd12-ffd5-473f-8c77-69e6d1700243
```

`SILENT_LATEST_SUBSTITUTION = NO`.

### C3. Dataset

Typed bounded Dataset query and stable `sample_id` selection are proven for
`mat-2`/`mat-3`; the Phase 13 browser evidence uses exact Dataset version
`be02266a-7d4f-4ebb-9f28-3132855167d0`.

### C4. Data → Research

Research handoff preserves exact Dataset object/version and semantic sample
identity in ContextSnapshot, then reaches Plan → Job → ToolCall → Artifact →
ScientificResult → grounded Interpretation.

### C5. Archive/Restore

Archive/restore API and authenticated browser evidence preserve historical
Result/Viewer source versions and do not create scientific versions.

## D. Agent

### D1–D6. Context through Interpretation

Real PostgreSQL/Redis/MinIO service-backed campaign passed 17/17 selected
tests; the broader mandatory Phase 12 campaign remains 19/19. Existing
Structure, Electronic and Dataset executions reach terminal interpreted state.

### D7. Capability Packs

Trusted `core.structure`, `core.electronic`, `core.data`, `core.trajectory`,
and `core.other` remain declarative; raw Tool exposure is disabled.

## E. Scientific Communication

### E1. Presentation

The bounded deterministic compiler maps authoritative ScientificResult facts
and grounded interpretation into narrative, finding, metric, table, figure,
viewer-reference, evidence-reference, limitation and warning blocks.

### E2. Viewer

Structure, Band/DOS and Scientific Table/Materials Explorer paths resolve exact
persisted sources and remain read-only.

### E3. Figure/Table

Figures reference persisted Artifacts; tables reference bounded typed Result or
Dataset projections with stable row identity.

### E4. Evidence

Evidence follows Result → item → ToolCall/Artifact → exact source/version with
project authorization and no infrastructure secrets.

### E5. Report

Reports retain exact Result, object/version and presentation snapshot
references; reopening is read-only.

## F. Continuity

### F1–F2. Project History / Resume

Project history and overview use persisted `researchTurnId`/`researchSessionId`;
the Workspace return bridge added in this phase exposes the same relation.

### F3–F4. Historical and Archived History

R1 remains exact v1 after production v2 exists; archived historical Results,
Presentation, Viewer, Evidence and Reports remain authorized and exact.

### F5–F6. Result Reuse / Zero-Recompute

Existing Agent2 reuse regressions prove zero scientific deltas for eligible
reuse. Viewer/Presentation/Report navigation contains no enqueue or Tool
execution hooks.

## G. Product

### G1. Navigation

Data → Research, Research → Viewer/Evidence/Report, History → exact Turn and
Workspace → Research now preserve authoritative IDs.

### G2–G4. Desktop/Mobile/Accessibility

Authenticated Chromium evidence includes desktop 1280×720 and mobile 390×844
paths. Mobile document width is 390 with no global horizontal overflow; typed
Dataset query, selection, Research handoff, findings, evidence and viewers are
reachable. Repeated presentation IDs are bounded and accessibility relations
remain valid.

## H. Security

Project authorization remains server-enforced across Data, Research, Result,
Artifact, Viewer, Evidence, Report and History. Unsupported presentation,
HTML/script, arbitrary component, Pack UI and cross-project traversal paths
fail closed. Presentation cannot mutate scientific data or trigger Viewer
recomputation.

## I. Production Qualification

### I1–I5. Runtime

`GET /health/runtime` returned:

```text
database = postgresql
redis = redis
artifactStorage = minio
worker = redis
llmProvider = deepseek (configured)
```

PostgreSQL, Redis, MinIO, API, workers and authenticated frontend were
available during qualification.

### I6. Browser Campaign

Existing authenticated Chromium evidence covers Data, Dataset presentation,
Structure presentation, Report, archive/restore, historical exact sources,
and 390×844 responsive paths. Valid paths had no fatal page errors,
unhandled rejections or unexpected authorization failures; one expected
authentication-bootstrap 401 is classified as non-fatal.

### I7. Service-backed Campaign

```text
selected = 17
passed = 17
failed = 0
errors = 0
skipped = 0
PostgreSQL = PASS
Redis = PASS
MinIO = PASS
```

### I8. Resource Health

```text
active DB connections = 1
idle DB connections = 5
idle-in-transaction = 0
pool timeouts = 0
queued/running jobs after campaign = 0
```

## J. Tests

```text
Focused frontend = 46 passed
Full frontend = 91 files / 595 passed
Workspace/backend focused = 11 passed, 3 historical compatibility skips
Full backend = 1813 passed, 83 historical compatibility skips
Service-backed Phase 13/Agent2/Workspace = 17 passed, 0 skipped
Typecheck = PASS
Production build = PASS (MDI_NEXT_DIST_DIR=.next-phase14-build)
Compileall = PASS
uv lock --check = PASS
touched Ruff = PASS
git diff --check = PASS
```

## K. Git / CI

### K1. P14-A

```text
SHA = d1249ac34cc0d2be571cdbc96075a3d88c6406b8
CI run = 33142030331
CI tested SHA = d1249ac34cc0d2be571cdbc96075a3d88c6406b8
result = PASS
required jobs = Unit Tests; Frontend Typecheck & Build;
                Service-backed Integration (PostgreSQL + Redis + MinIO);
                Phase 11-3 Scientific Replay (Linux/Windows)
```

### K2. P14-B / Final Seal

```text
SHA = 28a5a92c31b662bd12b19cdb2f99431c79ca5612
CI run = 33142435947
CI tested SHA = 28a5a92c31b662bd12b19cdb2f99431c79ca5612
result = PASS
required jobs = Unit Tests; Frontend Typecheck & Build;
                Service-backed Integration (PostgreSQL + Redis + MinIO);
                Phase 11-3 Scientific Replay (Linux/Windows)
HEAD == origin/master at P14-B
```

## L. Remaining Gaps

```text
NONE
```

## M. Final Verdict

```text
PHASE12 = COMPLETE
PHASE13 = COMPLETE
FUNCTIONAL_PHASE14_CLOSURE = PASS
AGENT2_PHASE14 = COMPLETE
FULL_PLATFORM_INTEGRATION = COMPLETE
PRODUCTION_QUALIFICATION = PASS
READY_FOR_PRODUCTION_RELEASE = YES
SILENT_LATEST_SUBSTITUTION = NO
DUPLICATE_SCIENTIFIC_AUTHORITY = NO
RAW_TOOL_EXPOSURE = NO
UNQUALIFIED_MAJOR_PRODUCT_FLOW = NONE
PHASE14_STARTED = YES
PHASE15_STARTED = NO
```
