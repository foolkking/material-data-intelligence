# Agent-2.0 Phase 14-R Results

Date: 2026-08-28
Status: `PARTIAL` — this document records current evidence without
claiming the mature-product release gate.

## A. Incoming Phase 14 Seal

- Historical Phase 14 seal: `d03b0a2e86e50d834a774cf823cfe055c91cf10c`
- Phase 14 remains sealed; no Phase 15 was created or started.
- Current Phase 14-R worktree head: `739074d`
- Latest evidence commits: `814f850`, `2141fb1`, `456d0a9`, `c398f65`,
  `739074d`
- `PHASE14R_REOPENED = NO`

## B. Product Reality Audit

The authoritative audit is
`docs/agent2/phase14r/PHASE14R_PRODUCT_REALITY_AUDIT.md`.
Scientific identity/version and Result authority remain frozen. The remaining
gaps are mature-product qualification gaps, not a replacement data model.

## C. Scientific Surface / Presentation

The bounded Scientific Presentation compiler and existing viewers are reused.
Evidence inspection is read-only and resolves through the secured planner route.
Current Dataset proof:

- Result: `15fc4d39-d2d7-5ac3-907a-cb06ed6b7a3f`
- Interpretation: `efccf7a2-6666-429e-be92-20cb2cf659de`
- exact object/version:
  `8a425466-b697-4c85-9a43-199414a22865` /
  `be02266a-7d4f-4ebb-9f28-3132855167d0`
- Evidence: `evidence.bf3896f29ae3554e977725d327b4ebba`
- Artifact checksum:
  `879396a3bc0bfdef2d31387b3eb73df309fa228d95f9cf2fb2c92eca6c119708`
- ToolCall:
  `call_job_agent2_8382c443f9ca4c909aa3444fea683807_step_1`
  (`dataset.materials_explorer`, completed)

The authenticated browser evidence inspector displays all of the above,
including the exact source, Artifact checksum and completed ToolCall.
Structure/Electronic/full scientific-surface campaigns remain `PARTIAL`.

## D. Report and Result Reuse

The authenticated modern Dataset report
`agent2_report_819f458171ba2d3219717895bf12eaf9` now carries its persisted
interpretation identity into every bounded report presentation block. Its
evidence inspector resolves:

- Result snapshot: `2809dcd1-243e-4323-8538-0a5fe81780d9`
- Interpretation: `efccf7a2-6666-429e-be92-20cb2cf659de`
- exact Dataset version: `be02266a-7d4f-4ebb-9f28-3132855167d0`
- Artifact checksum:
  `879396a3bc0bfdef2d31387b3eb73df309fa228d95f9cf2fb2c92eca6c119708`
- ToolCall: `dataset.materials_explorer` (`completed`)

Persisted scientific-state counts before and after opening the report and its
evidence inspector were unchanged:

```text
jobs = 96 → 96
tool_calls = 131 → 131
artifacts = 529 → 529
scientific_result_snapshots = 68 → 68
```

### Agent-2.0 Phase 14-R explicit session fallback continuity (2026-08-28)

The authenticated Research route had a narrow continuity defect when a URL
contained both an explicit `sessionId` and a historical `runId` that was not
yet normalized onto that session. `ResearchPage` selected only the run-bound
session and ignored the explicit target, producing a false
`研究会话不存在或已不可访问` state despite an authorized persisted session.
The minimal repair preserves the explicit session as a fallback while keeping
run-only orphan routes fail-closed.

The new deterministic regression covers an unbound historical run plus an
explicit session and verifies `getResearchSession("session_explicit")`. The
focused `ResearchPages` suite is now `35 passed`; web typecheck is `PASS`.
After refreshing the preserved authenticated browser tab, the historical
conversation loads, the context disclosure remains visible, and the previous
session-unreadable error is absent. API logs show the authoritative
`GET /research-sessions/research_fbf038934dc84ffeaa5aed9e7c906095` returning
`200 OK`. The only browser warning observed was Next Fast Refresh's development
full-reload notice; no console errors or unhandled rejections occurred.

### Agent-2.0 Phase 14-R session-list ResearchTurn projection (2026-08-28)

The authorized `GET /research-sessions/{session_id}` projection now includes
the persisted `researchTurnId` alongside each `runReferences` entry whenever a
ResearchTurn row is linked to the Job. The relation is read-only and
project-scoped; legacy sessions without a turn continue returning a null
value. This removes another opportunity for clients to reconstruct Turn
identity from Job strings. Project-access/history regression: `11 passed`;
Ruff and web typecheck are `PASS`.

### Agent-2.0 Phase 14-R Research follow-up controls (2026-08-28)

The authenticated Scientific Presentation now exposes explicit follow-up
actions for a completed Result: `继续研究`, `重新研究（新运行）`, and the
existing `重新解释（不重算科学结果）`. All three actions reuse the secured
ResearchTurn creation boundary and preserve exact source object/version
references. Continuation sends the prior Result identity as an explicit
reusable reference; rerun deliberately omits that reference and states that a
new execution lineage is requested; reinterpret remains the no-recompute path.
The focused `Agent2ScientificPresentation` suite passes `3/3` and the full
frontend regression passes `94 files / 603 tests`; typecheck remains `PASS`.
This closes the basic result-page control affordance but does not yet qualify
message revision/branching, queued/running cancellation recovery, or the
browser-level zero-delta reuse campaign.

### Agent-2.0 Phase 14-R immutable ResearchTurn branching (2026-08-28)

The existing `research_turns.parent_turn_id` relation now supports a bounded
branch from any terminal ResearchTurn, not only clarification turns. The
service still enforces same-project and same-session authorization and rejects
non-terminal parents; the parent message/Result remains immutable while the
new child Turn receives its own user message and lifecycle. Follow-up actions
now pass the exact parent Turn ID, so continue, rerun and reinterpret retain an
auditable lineage without inferring identity from Job names. Domain regression:
`tests/test_agent2_domain.py` `9 passed`; frontend follow-up regression `3
passed`. Message text editing and revision UI are still not fully qualified.

### Agent-2.0 Phase 14-R last-question edit branch (2026-08-28)

Completed Result presentation now exposes `编辑问题`. The action routes to an
explicit edit composer carrying `turn=<parent>&edit=<parent>`. The composer
loads the parent Result's original research question and exact source refs;
submission creates a new ResearchTurn with `reply_to_turn_id` pointing to the
terminal parent and never mutates the historical message, ContextSnapshot or
ScientificResult. The service/domain branch regression remains `9 passed`,
frontend presentation regression is `4 passed`, ResearchPages regression is
`35 passed`, and web typecheck is `PASS`. Full browser text-edit submission
and branch switching remain to be qualified.

### Agent-2.0 Phase 14-R historical ContextManifest compatibility (2026-08-28)

Historical ResearchTurns whose `CONTEXT_RESOLVED` event predates embedded
ContextManifest payloads now receive a deterministic, read-only compatibility
projection from the persisted immutable `research_context_snapshots` row. The
projection preserves exact object/version refs, semantic selections, prior
Result refs, constraints and bounded fingerprints while exposing only opaque
provider refs. Newer turns continue returning their persisted manifest
unchanged. Focused API/context regression: `20 passed`; no scientific
authority or historical snapshot was mutated.

After refreshing the same authenticated browser Research route with the
current API process, the `本次研究使用的上下文` disclosure is present and the
historical Dataset presentation still resolves the exact object/version and
evidence chain. The page continues to show a separate legacy conversation
reload warning for that old session, so browser-level full conversation resume
remains `PARTIAL`; this compatibility repair itself is verified by the focused
API regression and the visible context disclosure.

`tests/integration/test_agent2_phase7_service_backed.py` passed `4` cases in
`114.25s` against real PostgreSQL/Redis worker infrastructure. Interpretation
reuse asserted zero aggregate growth for plans, jobs, ToolCalls, Artifacts and
ScientificResult snapshots; continuation retained the explicit prior Result
identity. Browser-level reuse controls remain unqualified.

## E. Runtime / Service-backed

`GET /health/runtime` reports:

- PostgreSQL (`database.backend=postgresql`)
- Redis (`redis.backend=redis`)
- MinIO (`artifactStorage.backend=minio`, bucket `mdi-artifacts`)
- Redis worker backend
- configured DeepSeek provider

Recent service evidence:

- Phase 7 reuse campaign: `4 passed`, `0 failed`, `0 errors`, `0 skipped`
- Earlier Phase 3/7 combined service campaign: `5 passed`, `0 failed`,
  `0 errors`, `0 skipped`
- DB sample after campaign: `active=1`, `idle=5`,
  `idle-in-transaction=0`; no pool timeout observed.

## F. Tests

- `tests/test_phase10l4_api_persistence.py`: `14 passed`
- Frontend scientific presentation/identity tests: `12 passed`
- Report/presentation focused tests after report-evidence binding: `14 passed`
- Frontend typecheck: `PASS`
- touched Ruff (`apps/api/mdi_api/routers/planner.py`): `PASS`
- `git diff --check`: `PASS`
- Previously recorded current-worktree regression: frontend `93 files / 597
  passed`; backend `1820 passed / 83 skipped`
- Latest frontend full regression after explicit-session fallback:
  `94 files / 601 passed`; web typecheck `PASS`.

## G. Security / Provenance

Evidence and Artifact reads remain authorized by owning Job/project. The Agent2
compatibility adapter is read-only, bounded, accepts historical source-field
spellings, and does not expose credentials, queue URLs, filesystem paths or
provider payloads. Scientific values continue to come from persisted Result
snapshots; no latest-version substitution was introduced.

## H. Browser

The preserved authenticated in-app browser tab remains open. The Dataset
presentation route was reloaded after the API restart and the evidence
inspector showed:

`Phase13 Canonical Dataset · be02266a-7d4f-4ebb-9f28-3132855167d0`
Artifact checksum `879396…119708`
ToolCall `dataset.materials_explorer · completed`

Full capability-family, archive/history, mobile, report-quality and recovery
browser campaigns are not yet complete.

## I. Git / CI

- `c165212`: Agent2 evidence-chain compatibility adapter
- `4726be9`: exact Result reuse qualification evidence
- No `P14R-A` or `P14R-B` has been created; this remains evidence-only Phase
  14-R work and is not a mature-product release seal.
- No Phase 14-R release CI has been claimed.

## J. Remaining Gaps

The following mandatory mature-product gates remain open:

- full live Structure/Electronic/Dataset and all declared viewer-family
  acceptance;
- multi-family Report quality/browser evaluation;
- browser-level exact Result reuse controls;
- complete edit/branch/stop/continue/rerun/retry product campaign;
- Trash/retention/purge/export governance;
- organization metadata/collections and saved views;
- background task center and network recovery;
- provider-scale context/performance benchmark;
- backup/restore/monitoring/resource-governance qualification;
- final real-user acceptance and P14R exact-SHA release commits.

### Agent-2.0 Phase 14-R authorized global search projection (2026-08-28)

The former project-only search entry point was extended through the existing
ProductShell action to a bounded server-side `/search` projection (with the
`/api/search` compatibility route). It searches only projects visible through
the authenticated user's ownership/membership boundary and returns navigation
records for projects, datasets, scientific objects, Research sessions, Reports
and ScientificResult snapshots. Each item carries its owning project, status
and a product route; no scientific values, raw artifacts, credentials or
cross-project records are copied into the search response.

Deterministic authorization coverage: `tests/test_project_access.py` now
passes `12` cases, including viewer-scoped dataset/project search and a
cross-project `404` denial. Frontend `ProductShell` and `ResearchPages`
focused regression passes `38` tests and web typecheck is `PASS`.

Authenticated browser evidence on the preserved same-stack tab shows the
global search dialog returning real authorized records including
`Phase13 Canonical Dataset`, `ScientificResult 2809dcd1-243`,
`Phase13 Fresh Structure`, and the exact Research session
`research_fbf038934dc84ffeaa5aed9e7c906095`, each with a bounded `打开` route.
The API was reloaded against PostgreSQL/Redis/MinIO; `/health/runtime` remains
green. This closes the global search navigation gate, while organization
metadata/collections, task recovery, retention/export, performance and the
broader mature-product acceptance campaign remain open.

### Agent-2.0 Phase 14-R persisted task center bridge (2026-08-28)

The product now exposes a bounded global `/tasks` surface backed by the
existing authorized `listWorkspaceAnalysisJobs` projection. It aggregates
jobs from every visible project without copying scientific facts, separates
active (`created`, `queued`, `running`, `cancel_requested`) from terminal
records, and opens either the exact persisted Workspace route or the existing
project Research run route. No new job state or scientific authority is
created in the frontend.

Evidence:

- `apps/web/app/components/TaskCenterPage.tsx` and
  `apps/web/app/tasks/page.tsx` implement the user-facing route.
- `TaskCenterPage.test.tsx` verifies two authorized projects, status grouping,
  and exact Workspace/Research navigation (`1` test passed).
- Task center now also exposes a bounded `重新加载` action. It re-reads the
  same authorized persisted job projection after a connection failure or
  return-to-page event; the focused test verifies a second backend read.
- The authorized job projection now includes the persisted `researchTurnId`
  when one exists. Active rows with that explicit relation expose `停止研究`
  and call the existing `/api/research/turns/{turn_id}/cancel` authority;
  legacy rows without a relation remain read-only instead of guessing from a
  Job name. Focused UI and workspace projection tests cover this boundary.
- `ProductShell.test.tsx` and the full frontend regression pass after the
  bridge (`95` files, `606` tests); web typecheck passes.
- Authenticated browser tab `11` at `http://127.0.0.1:3000/tasks` rendered the
  persisted task center with `2` active tasks, `4` terminal tasks and `4`
  authorized projects. Each row exposed an exact `打开` route to its
  Workspace or Research run; no frontend scientific state was created.
- The current-worktree service-backed smoke collection completed against
  PostgreSQL/Redis/MinIO with `5 passed, 0 failed, 0 errors, 0 skipped`.
- The affected Workspace service-backed integration suite also passed
  `3 passed, 0 skipped` against the same PostgreSQL/Redis/MinIO stack after
  the explicit Turn projection change.
- `/health/runtime` remained green after the campaign: PostgreSQL database,
  Redis queue/worker, MinIO bucket `mdi-artifacts`, and configured DeepSeek.
- The task center intentionally remains `PARTIAL` for Phase 14-R because
  retry, durable notifications and full network-recovery semantics are not
  yet qualified.

## K. Final Verdict

```text
PHASE14 = SEALED
PHASE14_REOPENED = NO
FUNCTIONAL_PHASE14R_CLOSURE = FAIL
AGENT2_PHASE14R = PARTIAL
SCIENTIFIC_SURFACE_COMPLETENESS = PARTIAL
SCIENTIFIC_REPORT_QUALITY = PARTIAL
USER_LIFECYCLE_MANAGEMENT = PARTIAL
CHAT_RESEARCH_CONTROL = PARTIAL
CONTEXT_PROVENANCE_2_0 = PARTIAL
PRODUCT_FLUENCY = PARTIAL
REAL_USER_PRODUCT_ACCEPTANCE = NOT_QUALIFIED
MATURE_PRODUCT_GAPS = PRESENT
READY_FOR_MATURE_PRODUCTION_USE = NO
PHASE15_CREATED = NO
PHASE15_STARTED = NO
```

## L. Figure Artifact bridge follow-up

The report Figure projection now derives bounded `figure_sources` from the
immutable ScientificResult bundle, retaining each Figure reference, persisted
Artifact IDs and source Job. Report and shared Presentation readers open the
existing secured Artifact content route when available; no report rendering
creates a Job, ToolCall, Artifact or ScientificResult.

Evidence after the bridge:

- `tests/test_agent2_phase8_reports.py`: `16 passed`, `4` historical live-LLM
  skips.
- `apps/web/app/components/ScientificReportRoute.test.tsx`: `5 passed`.
- `apps/web/app/lib/scientific-presentation.test.ts`: `10 passed`.
- PostgreSQL/Redis/MinIO report/planning campaign: `9 passed`, `0 skipped`.
- Frontend full regression: `96 files / 612 tests passed`.
- Typecheck, production build, compileall, touched Ruff and diff checks pass.

The mature-product release gate remains open for full capability-family
browser acceptance, report-quality/revision review, protected Trash/retention/
export governance, context-stress/recovery campaigns, operations maturity and
P14R-A/P14R-B exact-SHA CI.

Current fix-forward commits are `814f850`, `2141fb1`, `456d0a9`, and
`c398f65`; no P14R release candidate or push has been claimed.

## M. Structure Viewer browser proof

Authenticated same-stack Data Platform route:

```text
object = dc3c3eee-f254-4edf-a0fa-c955402b3069
version = 8859cb49-0766-48cd-8a56-e44f5332e0c5
```

The Viewer rendered formula `Si`, one display site, lattice vectors, an
interactive canvas, camera presets, bounded supercell controls and measurement
controls. After isometric/`2 × 2 × 2`/reset navigation, persisted counts
remained unchanged:

```text
jobs = 117
tool_calls = 158
artifacts = 637
scientific_result_snapshots = 88
```

This closes the Structure-specific Viewer no-recompute proof only; all-family
Viewer qualification is still open.
