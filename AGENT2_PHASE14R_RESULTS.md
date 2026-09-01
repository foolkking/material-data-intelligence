# Agent-2.0 Phase 14-R Results

Date: 2026-08-28
Status: `PARTIAL` — this document records current evidence without
claiming the mature-product release gate.

## 2026-09-01 shared context control and exact reuse requalification

The authenticated Research page exposed a cross-component consistency defect:
removing an exact source from the left `本会话上下文` strip updated PostgreSQL,
but the right Scientific Presentation action retained a stale
`取消固定来源版本` label. `ResearchPages` now owns one shared
`Agent2SessionMemory` projection and passes it to
`Agent2ScientificPresentation`; mutations from either surface update the same
state instead of maintaining independent caches.

Canonical browser evidence:

```text
project = project_0002_1a0af866391f412d
session = research_88d4afe6d1de4459a32a364c68fc7f46
turn = fb72c2ad-bed1-47d7-b557-f398f04a8ede
result = 26127c48-d736-4983-b035-b68db238f6a7
object = f834e358-9944-4fe8-a3ab-f85d68041f54
version = a22745f2-17b6-434f-ba4c-3fe6bd244841

source pin removed → both left strip and right action changed
source pin restored → both surfaces changed back
Result pin created → left chip and right action changed
Result pin removed from the left chip → right action changed immediately
final state = exact source pinned, Result unpinned (original state restored)
```

Scientific state remained unchanged:

```text
ContextSnapshots for exact Turn = 1
Jobs = 301
ToolCalls = 395
Artifacts = 1565
ScientificResults = 203
```

Fresh verification:

```text
Context/access/history backend = 30 passed
Presentation/Research/Product frontend = 104 passed
shared-memory focused frontend = 73 passed
frontend typecheck = PASS
isolated PostgreSQL/Redis/MinIO Phase 7 reuse = 4 passed, 0 skipped
```

The first Phase 7 invocation incorrectly targeted the existing qualification
database and stopped at duplicate migration DDL before product logic. It did
not change or restart the product stack. The valid rerun used isolated
database `mdi_phase14r_reuse_20260901_1132`, unique Redis queues and the same
MinIO service.

## 2026-09-01 ContextManifest budget/replay and persisted recovery closure

`ContextBudgetPolicy 2.0` now has explicit deterministic coverage for all five
provider operations at well-below, near, exact, over and significantly-over
budget payloads. Non-critical overflow is compacted and recorded; an
over-budget `SCIENTIFIC_RESULT` remains fail-closed. Focused result:
`11 passed`.

The current PostgreSQL qualification database contains `458` immutable
operation manifests. Maximum observed estimates remain bounded:

```text
ORCHESTRATOR 241 / 12000
PLANNER 476 / 10000
INTERPRETER 1157 / 12000
REPORT 1802 / 10000
truncated manifests = 0
```

The authenticated historical Research page for Turn
`fb72c2ad-bed1-47d7-b557-f398f04a8ede` exposed all recorded stages and the
exact trajectory version. The expanded audit UI reported manifest
`c4785024-6027-42af-9a1f-52143afd7303`, policy 2.0, budget `12000`,
estimate `60` and the persisted context fingerprint.

The second retained browser tab requalified the global persisted-state
surfaces without disturbing the Research tab:

```text
Task Center: 60 total, 0 live, 12 attention, 15 authorized projects
Notification Center: 45 total, 8 attention, 33 completed, 4 canceled
bounded visible rows: 30
```

Exact ResearchTurn routes, partial/failure/canceled semantics and manual
reload remain available. Existing offline/reconnect evidence and isolated
Redis/worker recovery drills prove that browser disconnection does not mark
server work failed or create new scientific state.

## 2026-09-01 context-control and bulk-selection batch

- Research session memory now renders bounded chips for pinned objects and
  Results. Each pinned Result can be removed through the existing authorized
  `DELETE .../memory/pinned-results/{result_id}` operation; a pinned source
  version exposes the same control only when its exact object/version binding
  is available. Internal identifiers stay out of normal UI and mutation
  failures use an accessible alert.
- Data Platform selection mode now offers “全选数据/清空数据” and
  “全选对象/清空对象” for the active status filter. Existing server-side
  bulk lifecycle and dependency-impact preview semantics are unchanged.
- Focused frontend regression after the batch: ResearchPages `2 passed`
  targeted (full file remains green at `65` tests), ProductPages bulk
  regression `2 passed`, Agent2/ProductShell `18 passed`, and TypeScript
  typecheck `PASS`. This is implementation evidence; authenticated destructive
  bulk and memory-mutation browser campaigns remain open.

Authenticated in-app browser inspection on `3000` also showed the exact pinned
trajectory source with a reachable “取消固定对象 …” control, and Data
Platform selection mode showed “全选数据/全选对象” alongside the existing
lifecycle actions. These are read-only reachability checks; no persistent user
memory or scientific object was mutated during the check.

## 2026-09-01 multi-family presentation and Report browser qualification

Authenticated Chromium on the current-worktree frontend (`3000`) opened
seven persisted Reports against the live PostgreSQL/Redis/MinIO-backed API:
Structure (`agent2_report_401cfb...`: 2 findings, 2 tables), Dataset
(`agent2_report_c919723...`: 1 finding, 1 table), Electronic
(`agent2_report_e7fa88...`: 3 findings, 2 figures, 2 tables), Phonon
(`agent2_report_a015ca...`: 3 findings, 3 figures, 6 tables), Diffusion
(`agent2_report_e546810...`: 3 findings, 2 figures, 2 tables), Composition
(`agent2_report_9b6943...`: 2 findings, 2 tables), and RDF
(`agent2_report_55692c...`: 5 findings, 1 figure, 1 table). All seven routes
contained the expected exact source-version token, evidence and limitations;
raw capability IDs and raw JSON were absent. A mobile Dataset report at
`390x844` measured `document/body=390/390` with zero overflow. Browser
collection saw only the expected initial authentication `401`; critical
responses were zero. This closes a broad presentation/report evidence batch
but does not by itself close the remaining mature-product lifecycle,
context-stress, operations, or release-CI gates.

## 2026-08-31 trajectory diffusion and production-navigation batch

- Dataset `dataset_0001_441637edf69740aa`, trajectory resource
  `obj_trajectory_b0949ed50ff8`, Plan
  `plan_acb197e27b464ddca83157bd` and Job
  `job_dc63f3f5d57742009c6be09e` completed real `trajectory.msd` and
  `trajectory.diffusion` ToolCalls with eight persisted Artifacts.
- Interpretation `interpretation_a115c2ced38a7586161370b7994fec88`,
  bundle `bundle_d6ddf767fde0753fce41dd9ba943bf5d`, projects ten grounded
  evidence items: exact `1–6 ps`, 11 points, `R²=0.970301847945`,
  `α=0.924032310013`, accepted status and
  `D=0.038618084156 Å²/ps`.
- Before/after counts for this Job were
  `jobs/tool_calls/artifacts/scientific_result_snapshots/interpretations =
  1/2/8/0/1 → 1/2/8/0/2`; re-interpretation created no scientific work.
- Known Plot/summary/Recipe presentation companions no longer create a false
  incomplete-evidence warning when their completed ToolCall already has an
  approved authoritative Artifact projector. Unknown or genuinely unsupported
  sources remain fail-closed.
- Research and legacy Report reopening now select the newest immutable
  interpretation snapshot. Browser Research displays the exact fit window and
  ten evidence items instead of the older generic-window narrative.
- The trajectory diagnostic UI now uses coherent Chinese scientific labels,
  persisted/read-only disclosure, bounded table actions and responsive
  `390x844` layout (`390/390`, no global overflow).
- An isolated current-worktree production build on `3002` completed
  successfully. Eight authenticated project navigation transitions generated
  zero document requests and preserved the exact ProductShell node. Warm URL
  latency was `33–93 ms`; warm usable latency was Data `97 ms`, Research
  `866 ms`, Reports `59 ms`, Overview `872 ms`.
- Valid post-auth browser sampling reported zero console errors, page errors,
  critical responses and failed API requests.
- Focused regression: backend `26 passed`; frontend `65 passed`; touched Ruff,
  typecheck and production build `PASS`.

Truthful boundary: `trajectory.diffusion = PARTIAL`, because this legacy
Planner lineage has no Agent2 ScientificResultSnapshot and the remaining
historical/archived exact-version acceptance is not yet complete. Overall
Phase 14-R remains `PARTIAL`; P14R-A/P14R-B are not created.

## 2026-08-30 current-worktree fluency and control evidence

- Missing Reports now use authorized `report-status` with
  `NOT_REQUESTED/REQUESTED/COMPOSING/READY/FAILED`; normal absence is `200`,
  no longer a valid-path `404` polling loop.
- Live Turn `c94850bb-33cf-49d2-9d07-32b17ca319b6` showed the idle
  `生成报告` action through that status projection with zero browser
  errors/warnings.
- Re-interpret child `c94850bb-33cf-49d2-9d07-32b17ca319b6` reused Result
  `15fc4d39-d2d7-5ac3-907a-cb06ed6b7a3f`; Job, ToolCall, Artifact and
  ScientificResult deltas were all `0`.
- Edit child `7a2f5367-3984-4fa3-9a10-05599079b68b` retained parent Turn
  `8382c443-f9ca-4c90-9aa3-444fea683807`; historical state was not mutated.
- Main project, Planner and Workspace internal navigation now use the Next App
  Router. A warm Research-to-Data request was `89 ms`, retained the browser
  marker and made zero document/icon reload requests. Cold development
  transitions remain subject to route compilation and are not misreported as
  production SLO evidence.
- Mobile global overflow is closed at the effective `375 px` layout viewport
  (`document/body/header = 375/375/375`); desktop Data Navigator overflow is
  closed (`248/248`, controls `208/208`, rows `224/224`).
- Focused evidence: Report backend `22 passed / 4 historical provider skips`;
  grouped Report/Planner/Workspace/route frontend `68 passed`; typecheck and
  touched diff-check `PASS`.
- Failed Turn `8080a173-5e9f-4aef-89b7-78fed81316c8` now exposes recovery
  actions below its terminal status. `修改问题` restores that exact question,
  not the session tail. `重新研究（新运行）` created child
  `f6441688-5404-4a0f-aa9f-31e7692ef8de` with exact Dataset version
  `be02266a-7d4f-4ebb-9f28-3132855167d0` and sample `mat-2`.
- Retry count delta: Turn `+1`; Job `0`; ToolCall `0`; Artifact `0`;
  ScientificResult `0`. The router correctly selected `ANSWER`.
- The 50-message acceptance session now renders five messages around the
  selected Turn by default, hides 45 unrelated historical messages, expands to
  50 on request, and collapses back to five. Mobile document width is
  `390/390`.
- Recovery/history regression is `56 passed`; ContextManifest budget
  regression is `6 passed`; typecheck `PASS`.

## A. Incoming Phase 14 Seal

- Historical Phase 14 seal: `d03b0a2e86e50d834a774cf823cfe055c91cf10c`
- Phase 14 remains sealed; no Phase 15 was created or started.
- Current Phase 14-R worktree head: `7809996ce84393cfb0f222fc0bd187f8ca942171`
- Latest evidence commits: `814f850`, `2141fb1`, `456d0a9`, `c398f65`,
  `739074d`, `26ad220`, `196c223`, `ee0bda5`, `1840ca8`, `08d7ec4`,
  `9ecbce5`
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

### Agent-2.0 Phase 14-R authenticated Dataset archive/restore browser proof (2026-08-29)

Using the preserved authenticated in-app browser against the live
PostgreSQL/Redis/MinIO API, the `Phase13 Canonical Dataset`
(`dataset_0003_1e42d834bfa64961`) was archived from the normal Data Platform
action menu and then restored from the `已归档` view. While archived it was
removed from the current dataset list and remained readable in the archived
filter with the explicit `恢复数据集` action. After restore it returned to the
current list with the same three typed rows (`mat-1`, `mat-2`, `mat-3`) and
the same exact scientific object/version route. No destructive delete was
performed and no scientific version was created by either lifecycle action.
This is fresh browser evidence for the reversible archive/restore path; the
protected Trash/retention/purge contract remains unqualified.

### Agent-2.0 Phase 14-R service campaign environment diagnosis (2026-08-29)

An initial attempt to enable the full Phase 10 service-backed collection set
set `DATABASE_URL` but omitted the repository's explicit `MDI_RUN_INTEGRATION=1`
gate, producing `21` intentional skips. A second attempt set the integration
gate without loading the PostgreSQL alias and produced the expected
configuration failures. The corrected invocation loads the repository runtime
environment and sets both `MDI_RUN_INTEGRATION=1` and
`MDI_TEST_DATABASE_URL`/`DATABASE_URL`; its result is tracked separately
below. This confirms the earlier skip/failure was command-environment setup,
not evidence that PostgreSQL, Redis or MinIO were unavailable.

The corrected current-worktree collection covered Phase 10L–10N dependency,
interpretation, natural-language, workspace, recovery, report/recipe,
coordination, local-environment, XRD, trajectory, electronic and professional
closure paths: `21 passed`, `0 failed`, `0 errors`, `0 skipped` in `85.84s`
against the live stack. The explicit integration gate was enabled and the
PostgreSQL alias was loaded from `.phase13-start-api.ps1`; no mocks or SQLite
were used for this run.

### Agent-2.0 Phase 14-R stale task visibility guard (2026-08-29)

The global Task Center now keeps persisted active-task semantics unchanged but
adds a bounded, truthful attention notice when an active/queued task has no
status update for 15 minutes. It does not relabel the task as failed, cancel
it, or infer identity from a Job name; the user is directed to open the task
to read the latest persisted state. The focused Task Center test passes and
the browser remains able to load the same task list. This improves recovery
clarity without introducing a new task state authority.

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

### Agent-2.0 Phase 14-R explicit Result/Snapshot identity and reuse presentation (2026-08-28)

The authenticated same-stack Research route exposed a narrow identity seam:
the presentation API returned the immutable bundle `result_id`, while
context/memory and reuse APIs require the persisted
`scientific_result_snapshots.id`. The frontend consequently submitted a
logical result UUID as `explicit_result_ids`, causing worker context assembly
to fail. The API now returns `result_snapshot_id`; reinterpret, continue and
pin/unpin controls use that snapshot identity while retaining `result_id` for
scientific presentation.

The assembler treats explicit snapshot selections as authoritative and does
not mix them with recency-derived candidates. The result route resolves an
`INTERPRET_RESULT` Turn to its explicitly referenced immutable source snapshot
instead of creating a duplicate ScientificResult.

Live same-stack evidence:

- Reinterpret Turn: `4460fc2c-98f8-4129-8fd5-0615f08dc5a7`
- Source snapshot reused: `2809dcd1-243e-4323-8538-0a5fe81780d9`
- Decision: `INTERPRET_RESULT`, `reusable_result_ref_keys = ["result_1"]`
- Interpretation: `bf7ef3ec-0567-4c2f-80b6-9b584984c45f`, `grounding_status=VALID`
- Final Turn: `COMPLETED`
- Browser presentation rendered exact Dataset version
  `be02266a-7d4f-4ebb-9f28-3132855167d0` and `mat-2` facts.
- Persisted scientific counts remained unchanged:
  `jobs=117`, `tool_calls=158`, `artifacts=637`,
  `scientific_result_snapshots=88`.

Focused regressions: frontend `15 passed`; backend API/result focused
`1 passed`; compileall `PASS`. This closes the explicit reuse seam only;
the mature-product release gate remains open.

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

## N. Structure report browser follow-up

Authenticated same-stack browser opened the legacy-compatible Structure report
`job_agent2_17b67e68b7db475bbb4c3b336cb2ba15` and rendered persisted
CrystalNN/VoronoiNN output, exact site/neighbor tables, algorithm warnings and
reproducibility details. The read-only reopen left scientific state counts
unchanged (`analysis_plans=133`, `jobs=117`, `tool_calls=158`,
`artifacts=637`, `scientific_result_snapshots=88`). This strengthens the
Structure report/viewer evidence only; full capability-family browser coverage,
Trash/retention/export, recovery and P14R release CI remain open.

## O. Same-stack fresh-worker MinIO environment repair (2026-08-28)

The mandatory PostgreSQL/Redis/MinIO reuse campaign initially failed in the
fresh subprocess worker with `Exact ScientificObjectVersion payload is
unavailable`. The persisted source was valid; the harness worker had not
received the MinIO endpoint/credential aliases used by the fixture process.
The repair is limited to `_worker_environment()` in
`tests/integration/test_agent2_phase4_service_backed.py`, propagating the
repository-supported `MINIO_ENDPOINT`, `MINIO_ACCESS_KEY`,
`MINIO_SECRET_KEY`, and `MINIO_BUCKET` values. No worker or scientific
authority behavior changed.

Fresh service-backed rerun:

```text
tests/integration/test_agent2_phase7_service_backed.py
4 passed
0 failed
0 errors
0 skipped
```

This closes the demonstrated fresh-worker MinIO harness defect. The broader
Phase 14-R mature-product gates remain open.

## P. Current-worktree regression refresh (2026-08-28)

After the snapshot identity and worker-environment repairs, the current
worktree was rechecked without restarting the live API, workers, MinIO, Redis,
PostgreSQL or authenticated browser tab:

```text
frontend full: 96 files / 613 tests passed
backend full: 1825 passed / 83 skipped
Phase 7 service-backed: 4 passed / 0 failed / 0 errors / 0 skipped
focused backend Agent2/Report/Viewer: 88 passed / 5 historical skips
typecheck: PASS
production build: PASS
compileall: PASS
git diff --check: PASS
```

The 83 backend skips remain historical or explicitly optional tests; the
mandatory Phase 7 service campaign has zero skips. This refresh strengthens
the current baseline but does not convert unqualified mature-product surfaces
into PASS.

Post-campaign PostgreSQL activity remained bounded:

```text
active = 1
idle = 7
idle-in-transaction = 0
pool timeouts = 0 observed
```

## Q. Authorized global-search lifecycle filters (2026-08-28)

The global product search now supports bounded type and lifecycle filters
without introducing a new search authority. `GET /search` accepts
`status=active|archived|all`, derives project archive state from
`project_configs`, and continues to scope every result through project
membership. The authenticated search dialog exposes the existing `kind`
filter plus the lifecycle selector and sends options only when selected.

Evidence:

```text
backend tests/test_project_access.py -k "product_search": 2 passed
frontend ProductShell.test.tsx: 6 passed
authenticated /console browser: Phase13 + scientific_object + active
  returned 3 authorized objects and no archived rows
invalid status: HTTP 422
scientific execution/mutation from search: none
```

This is a narrow R7 discoverability improvement. Trash/retention and the
broader mature-product release gate remain open.

## R. ScientificResult search continuity (2026-08-28)

Result search hits now prefer the persisted `ScientificResultSnapshot →
ResearchTurn` relation and link directly to `/research?turn=<id>`. The
`result=` fallback remains only for historical rows without a resolvable
ResearchTurn. This removes frontend identity guessing from the global-search
continuation path.

Evidence:

```text
snapshot = 2809dcd1-243e-4323-8538-0a5fe81780d9
researchTurn = 8382c443-f9ca-4c90-9aa3-444fea683807
browser /console result search href =
  /projects/project_0002_1a0af866391f412d/research?turn=8382c443-f9ca-4c90-9aa3-444fea683807
fallback helper regression = PASS
```

The API was restarted once to load the current worktree code; PostgreSQL,
Redis, MinIO, frontend and the authenticated browser session were preserved.

## S. Scientific Report export transport hardening (2026-08-28)

The modern Scientific Report Markdown export now appends its bounded Blob
anchor to the document before clicking, then removes it and revokes the object
URL. This makes the existing export action reliable in browser runtimes that
require an attached download target; it remains read-only and preserves exact
report/source provenance.

Regression: `ScientificReportRoute.test.tsx` `6 passed`, including attached
anchor click and object URL cleanup. The broader export-package and retention
gates remain open.

## T. Current-worktree regression refresh (2026-08-28)

Fresh current-head checks after the latest search/result/export changes:

```text
frontend full: 96 files / 615 tests passed
backend full: 1827 passed / 83 skipped
production build: PASS
typecheck: PASS
compileall: PASS
uv lock --check: PASS
touched Ruff: PASS
git diff --check: PASS
```

Runtime health remained PostgreSQL, Redis, MinIO, Redis worker, and configured
DeepSeek (`deepseek-v4-flash`). The Phase 14-R mature-product release gate is
still open because capability-wide browser coverage, lifecycle/trash
governance, recovery, operations, and exact-SHA P14R-A/P14R-B sealing remain
unqualified.

## U. Current same-stack service campaign (2026-08-28)

Fresh current-worktree service-backed checks:

```text
tests/test_phase14r_context_manifest.py
tests/integration/test_agent2_phase3_service_backed.py
tests/integration/test_agent2_phase7_service_backed.py

selected = 8
passed = 8
failed = 0
errors = 0
skipped = 0
PostgreSQL = PASS
Redis = PASS
MinIO = PASS
```

Post-campaign PostgreSQL activity was `active=1`, `idle=4`, with no
`idle-in-transaction` rows observed. This is service-backed regression
evidence, not a claim that every Phase 14-R mature-product path is qualified.

## V. Current authenticated browser continuity (2026-08-28)

The existing in-app browser tab remains open and authenticated at
`http://127.0.0.1:3000/console`. The live search dialog is still usable and
shows the ScientificResult snapshot
`2809dcd1-243e-4323-8538-0a5fe81780d9` opening through its persisted
ResearchTurn
`8382c443-f9ca-4c90-9aa3-444fea683807` via the exact `/research?turn=...`
route. No service or browser process was closed during this refresh.

## W. Lifecycle audit: archive/delete boundary (2026-08-28)

The current repository exposes authorized ACTIVE/ARCHIVED transitions for
Projects, Datasets and ScientificObjects, plus dependency-preview-protected
physical deletion only for empty Projects/Datasets. The audit found no
persisted `TRASHED`/`PURGED` contract, Trash surface, retention policy or
provenance-aware export package. Existing delete operations therefore remain
intentionally narrow and fail closed when dependencies exist; no destructive
lifecycle implementation was added without a complete authority contract.

## X. Exact ResearchTurn continuity from task surfaces (2026-08-28)

Task Center and Notification Center previously opened non-Workspace jobs with
only `run=<jobId>`. When a persisted ResearchTurn existed, that could route
the user through a compatibility history path instead of the exact Turn.
Both surfaces now include `run=<jobId>&turn=<researchTurnId>` when the
authoritative relation is present. Workspace-backed links and run-only legacy
fallbacks remain unchanged.

Evidence:

```text
TaskCenterPage.test.tsx: 1 passed
NotificationCenterPage.test.tsx: 1 passed
```

This is a focused continuity repair only. Capability-wide browser acceptance,
Trash/retention/export governance, recovery campaigns, operations maturity
and P14R-A/P14R-B release sealing remain open.

## Y. Current-head verification after exact Turn navigation repair (2026-08-28)

Authenticated Chromium verification against the running local product showed
the repaired links in both durable surfaces:

```text
/tasks
  /projects/project_0002_1a0af866391f412d/research?run=job_agent2_8382c443f9ca4c909aa3444fea683807&turn=8382c443-f9ca-4c90-9aa3-444fea683807
  /projects/project_0002_1a0af866391f412d/research?run=job_agent2_17b67e68b7db475bbb4c3b336cb2ba15&turn=17b67e68-b7db-475b-bb4c-3b336cb2ba15

/notifications
  same exact run + turn links for the two ResearchTurn-backed jobs
```

No browser console errors or page errors were captured on those paths.

Current-head regression after the repair:

```text
frontend full: 96 files / 615 tests passed
typecheck: PASS
production build: PASS
git diff --check: PASS
```

The Phase 14-R release verdict remains intentionally `PARTIAL`; this repair
does not establish capability-wide live Viewer coverage, Trash/retention,
recovery, operations maturity, or exact-SHA release commits.

## Z. Task/notification state presentation and pin mutation race (2026-08-28)

Task Center and Notification Center now translate the persisted Turn relation
into the user-facing `可恢复研究会话` label. A true legacy run without a
ResearchTurn is the only case rendered as `历史运行 · 仅查看`; the internal
`LEGACY_READ_ONLY` value is no longer shown for modern Agent2 work.

`Agent2ScientificPresentation` now uses a mutation sequence guard and
optimistic state for pin/unpin. A stale `getAgent2SessionMemory` response
cannot revert a newer user action, while a real pin API failure restores the
previous state.

Fresh verification:

```text
TaskCenterPage.test.tsx: PASS
NotificationCenterPage.test.tsx: PASS
Agent2ScientificPresentation.test.tsx: 5 passed
frontend full: 96 files / 615 tests passed
typecheck: PASS
production build: PASS
backend touched integration/API: 31 passed, 3 skipped
git diff --check: PASS
```

Authenticated Chromium on the running product confirmed that `/tasks` and
`/notifications` preserve exact `run` + `turn` navigation and do not expose
`LEGACY_READ_ONLY`. This is a narrow continuity/UX repair; the mature-product
gate remains `PARTIAL` and no P14R release commit was created.

## AA. Current same-stack regression after stale-error guard (2026-08-28)

The stale-session-memory guard now covers both successful and failed reads, so
an obsolete request cannot reset the optimistic pin state after a newer user
mutation. Fresh verification:

```text
Agent2ScientificPresentation + TaskCenter + NotificationCenter:
3 files / 7 tests passed
frontend full: 96 files / 615 tests passed
backend full: 1827 passed / 83 skipped
typecheck: PASS
production build: PASS
compileall: PASS
uv lock --check: PASS
touched Ruff: PASS
git diff --check: PASS
```

`/health/runtime` remains backed by PostgreSQL, Redis, MinIO (`mdi-artifacts`),
Redis worker execution and configured DeepSeek. This confirms current-worktree
regression health; it does not close the outstanding capability-wide browser,
retention/export, recovery, operations or exact-SHA release gates.

## AB. Authenticated desktop/mobile surface sweep (2026-08-28)

Using the requested Chromium executable and the authenticated acceptance
account, the current runtime was checked at both `1280x720` and `390x844` for
the project shell, Data, Research, Reports, Task Center and Notification
Center routes.

```text
routes checked: 6
viewports: 2
global horizontal overflow: 0 on all 12 checks
key route content: present on all checks
LEGACY_READ_ONLY exposed: no
page errors: 0
```

The only console 401 was the expected unauthenticated bootstrap request
before the scripted login. The only failed request was an aborted
`GET /api/datasets/dataset_0003_1e42d834bfa64961/object-store` initiated by
the Data route while navigating away; it did not produce a page error or
scientific-state mutation and is classified as an expected cancellation.
This closes a bounded responsive/navigation sweep, not the still-open
capability-wide Viewer or mature-product acceptance campaign.

## AC. Project History direct ResearchTurn continuity (2026-08-28)

The browser-facing API was restarted with the repository-supported
PostgreSQL/Redis/MinIO environment and `/health/runtime` now reports the
actual same-stack services (`postgresql`, `redis`, `minio`, Redis-backed
worker, bucket `mdi-artifacts`).

Authenticated live history evidence confirms that modern Agent2 jobs resolve
their exact persisted ResearchTurn directly from `research_turns`, even when
no legacy `research_session_runs` row exists:

```text
job_agent2_8382c443f9ca4c909aa3444fea683807
  → researchTurnId 8382c443-f9ca-4c90-9aa3-444fea683807
  → researchContextKind RESEARCH_TURN

job_agent2_17b67e68b7db475bbb4c3b336cb2ba15
  → researchTurnId 17b67e68-b7db-475b-bb4c-3b336cb2ba15
  → researchContextKind RESEARCH_TURN
```

The bridge is implemented in `apps/api/mdi_api/routers/project_history.py`;
`tests/test_project_history_research_context.py` reports `4 passed`, and
touched Ruff plus `git diff --check` pass. This closes the demonstrated
modern-history identity defect only; capability-wide Viewer qualification,
trash/retention/export governance, recovery, operations maturity and exact
P14R release commits remain open.

## AD. Session list → exact ResearchTurn browser continuity (2026-08-28)

The first history repair exposed a second, real product seam: the project
history endpoint returned modern Turn identities, but the
`research-sessions` projection still listed only legacy compatibility rows.
As a result, a valid task link could show the result while incorrectly saying
that no recoverable conversation existed.

`apps/api/mdi_api/routers/research.py` now merges direct, project-scoped
`research_turns.research_session_id`/`job_id` bindings into
`runIds`/`runReferences`, preserving legacy fallback behavior and server-side
authorization. The authenticated Chromium path was re-run after an API
reload:

```text
/tasks
  → /projects/project_0002_1a0af866391f412d/research
     ?run=job_agent2_8382c443f9ca4c909aa3444fea683807
     &turn=8382c443-f9ca-4c90-9aa3-444fea683807

result: recoverable conversation warning absent
context disclosure: present
exact Dataset result: present
console/page errors: 0
critical failed requests: 0
horizontal overflow: 0
```

Focused regression now reports `19 passed` across Project Access and history
continuity; touched Ruff and `git diff --check` pass. The mature-product
release remains `PARTIAL` because capability-wide viewer, lifecycle,
recovery, operations and exact-SHA gates are still open.

## AE. Modern terminal projection reconciliation (2026-08-28)

Terminal interpretation reconciliation now prefers the persisted
`research_turns.research_session_id` relation for a Job and only falls back
to `research_session_runs` for legacy deployments. This prevents a modern
Agent2 result from losing its assistant projection merely because the legacy
compatibility row is absent; no new identity authority was introduced.

Focused verification:

```text
Project Access + history/reconciliation: 20 passed
touched Ruff: PASS
git diff --check: PASS
```

Phase 14-R remains `PARTIAL`; this is an additional continuity repair, not a
mature-product release seal.

## AF. Result reuse browser proof after queue-worker recovery (2026-08-28)

Authenticated Chromium replayed `重新解释（不重算科学结果）` against the
current PostgreSQL/Redis/MinIO runtime. Turn
`cc704d3f-dcfc-4a49-a971-2cda6282039c` initially remained `RECEIVED` because
the five repository-supported queue workers had exited. Starting the existing
`.phase13-start-workers.ps1` launcher restored queue consumption without any
API, route, or scientific-authority change.

```text
action = INTERPRET_RESULT
status = COMPLETED
ContextSnapshot = 01ff8edd-2751-490a-9558-f7ad690b54a8
ContextManifest = da2d4f02-1dac-4d53-aa9f-8987a8ab6147
reused ScientificResultSnapshot = 2809dcd1-243e-4323-8538-0a5fe81780d9
logical result = 15fc4d39-d2d7-5ac3-907a-cb06ed6b7a3f
Interpretation = ce8c820d-2f42-4a82-9593-714971b5ad09
grounding = VALID
execution = SUCCESS
analysis-job count before/after = 4 / 4
```

The manifest retained exact Dataset object/version
`8a425466-b697-4c85-9a43-199414a22865` /
`be02266a-7d4f-4ebb-9f28-3132855167d0`, semantic selection `mat-2`, and the
explicit prior Result reference. No new Job, ToolCall, Artifact, or
ScientificResult snapshot was created by reinterpretation. The initial delay
is classified as `WORKER_PROCESS_NOT_RUNNING`; broader mature-product,
recovery, retention, and exact-SHA release gates remain open.

## AG. Edit-branch context isolation and fresh browser proof (2026-08-28)

The first fresh edit branch exposed a genuine orchestration defect: the
child turn had no explicit `explicit_result_ids`, but the candidate assembler
still injected recent historical Results. The router selected
`INTERPRET_RESULT`, and grounding correctly failed. The narrow fix is in
`apps/api/mdi_api/research_agent/context/assembler.py`: child turns with a
`parent_turn_id` no longer receive recency-derived Result candidates unless
the UI explicitly binds Result snapshot IDs. Explicit reinterpret/continue
flows remain unchanged.

The API and all five repository-supported workers were reloaded on the same
PostgreSQL/Redis/MinIO stack. The next authenticated edit action created:

```text
parent Turn = 8382c443-f9ca-4c90-9aa3-444fea683807
child Turn = 1176df48-b0a4-4611-bf42-970ef2c6d181
parent relation = preserved
ContextSnapshot = 6d7f8505-0adc-46ef-a09b-bffb4e9757f0
Dataset object/version = 8a425466-b697-4c85-9a43-199414a22865 /
  be02266a-7d4f-4ebb-9f28-3132855167d0
DATASET_SAMPLE = mat-2
Result candidates in context manifest = 0
router action = ANSWER
terminal state = ANSWERED
child Result snapshots = 0
```

The edited request was a bounded explanation of the selected Dataset value,
so `ANSWER` is the correct action
(`REQUEST_DID_NOT_REQUIRE_SCIENTIFIC_EXECUTION`); it did not fabricate a new
Job or scientific Result. Parent Turn remained `COMPLETED` and unchanged. A
deterministic regression
`test_child_branch_does_not_inherit_recent_results_without_explicit_binding`
now protects this boundary; the Phase 14-R context manifest suite reports
`4 passed`, and the broader focused API/access/history suite reports
`40 passed`.

This closes the demonstrated edit-branch context contamination seam. The
overall Phase 14-R status remains `PARTIAL`: mature lifecycle,
capability-wide surface, recovery, retention/export, performance,
evaluation, operations, and exact-SHA release gates are still not all
qualified.

## AH. Dataset semantic constraint binding and fresh execution (2026-08-28)

Fresh browser replay exposed a planning defect: valid Dataset semantic
selectors (`sample=mat-2`, `property=band_gap`) were copied into the strict
`dataset.materials_explorer` executable parameter object. The bounded fix in
`apps/api/mdi_api/research_agent/planning/binder.py` removes only these two
known semantic-only keys before Tool schema validation; arbitrary unknown
parameters remain fail-closed.

After API and worker reload on the same PostgreSQL/Redis/MinIO stack, fresh
authenticated execution completed:

```text
Turn = 3b85fa42-dcc8-42b3-ac68-f5f54b610df4
ContextSnapshot = 95b01789-f26d-426a-9e57-73304ce048be
AnalysisPlan = plan_4d7388c0464c4311af4dcd02
Job = job_agent2_3b85fa42dcc842b3ac68f5f54b610df4
ScientificResult = e2587ca6-9b1f-5532-9e79-0ae6a89d6777
ResultSnapshot = 8ac5b6d2-c5d7-4f31-8b19-4776149106bc
Interpretation = 70e03e81-2185-4870-abfa-c2a18565a026
execution = SUCCESS
grounding = VALID
terminal = COMPLETED
```

The persisted Result contains `dataset.sample.band_gap(mat-2)=2.5`, four
artifacts, and exact Dataset object/version
`8a425466-b697-4c85-9a43-199414a22865` /
`be02266a-7d4f-4ebb-9f28-3132855167d0`. Deterministic planning coverage is
`21 passed, 1 skipped`; touched Ruff passes. This closes the demonstrated
Dataset planner/execution seam; the broader Phase 14-R mature-product gate
remains `PARTIAL`.

## AI. Scientific presentation pin-state race and full regression (2026-08-28)

The full frontend run exposed a real product-control race in
`Agent2ScientificPresentation`: a delayed session-memory read could overwrite
the server-confirmed result of a pin/unpin mutation. The existing
`pinMutationSeq` guard is now advanced after both successful and failed
mutations, invalidating stale reads without changing session-memory authority.

```text
Agent2ScientificPresentation focused = 6 passed
frontend full = 96 files / 615 tests passed
backend full (SQLite-isolated default) = 1833 passed / 83 skipped
service-backed Phase 3/4/5 with explicit PostgreSQL/Redis/MinIO env = 4 passed
Ruff (touched files) = PASS
compileall (touched Python) = PASS
git diff --check = PASS
```

The earlier backend invocation that forced `DATABASE_URL` globally is not
qualification evidence: it redirected temporary SQLite migration tests to the
shared PostgreSQL database and produced `DuplicateTable` errors. The clean
SQLite-isolated rerun above passed. Phase 14-R remains `PARTIAL`; this closes
one user-control race and strengthens regression evidence but does not claim
mature-product or release-seal completion.

## AJ. Same-stack authenticated presentation replay (2026-08-28)

Using the requested Chromium executable against the live API/frontend, the
authenticated Research route reopened the exact Dataset result and rendered
its presentation, table, Viewer reference, evidence path and control surface.
The route used project
`project_0002_1a0af866391f412d` and historical session
`research_fbf038934dc84ffeaa5aed9e7c906095`; the visible result retained
Dataset version
`be02266a-7d4f-4ebb-9f28-3132855167d0`, sample `mat-2`, and value `2.5`.
The browser captured zero page errors and no critical 5xx responses; the only
console error was the expected pre-login bootstrap `401`.

This is authenticated same-stack presentation evidence, not a claim that the
unqualified capability-family, recovery, retention/export, operations, or
release gates are complete.

The same authenticated route at `390x844` retained
`innerWidth=doc=body=390`, exposed the Dataset query and Research handoff, and
 kept exact source identity visible. No page errors occurred; the same
pre-login `401` was the only console error.

## AK. Authenticated edit-to-branch browser proof (2026-08-28)

The real Chromium edit composer created a new immutable child Turn from the
completed parent `8382c443-f9ca-4c90-9aa3-444fea683807`:

```text
child Turn = dc76de32-4675-4b6a-91fd-ef102602c905
parent relation = preserved
final state = ANSWERED
ContextSnapshot = e58057b5-b88b-495e-a855-29dd46a4c953
Dataset object/version = 8a425466-b697-4c85-9a43-199414a22865 /
  be02266a-7d4f-4ebb-9f28-3132855167d0
DATASET_SAMPLE = mat-2
child Job/Result = none (correct for the bounded QUERY_DATA answer)
parent state = COMPLETED and unchanged
```

The browser recorded no page errors or 5xx responses. Transient
`SCIENTIFIC_RESULT_NOT_READY` 409 reads were the expected fail-closed result
endpoint behavior while the child was an `ANSWERED` non-scientific turn.

## AL. Scientific report narrative quality extension (2026-08-29)

The existing immutable Report contract has been extended at the
communication layer with optional bounded `discussion`, `conclusion`, and
`next_steps` sections. Each section retains `fact_refs` and `evidence_refs`;
the Report grounding validator rejects unsupported numeric or unit claims in
these sections. The provider-facing `ReportContextBundle` remains bounded and
does not gain raw Artifacts, Tool logs, credentials, or unrelated
conversation.

```text
backend Report focused = 18 passed / 4 compatibility skips
frontend Report + presentation focused = 16 passed
frontend typecheck = PASS
touched Ruff = PASS
```

The Report route and Markdown export now render the mature scientific
hierarchy without re-running science. This closes one R2 contract/UI seam;
multi-family real Report evaluation, revision lifecycle, retention,
capability-wide Viewer acceptance, operations drills and exact-SHA P14R
release gates remain open. Phase 14-R therefore remains `PARTIAL`.

## AM. Pre-execution cancellation control (2026-08-29)

The authenticated Research UI now exposes the existing server-authoritative
cancel action during `ORCHESTRATING`, `READY_TO_PLAN`, `PLANNING`, and
`PLAN_READY`, not only after a Job is queued or running. This closes the
control gap where a user could not stop a planning request before Job
creation; cancellation still follows the existing ResearchTurn state machine
and does not fabricate or delete scientific output.

```text
ResearchExecutionActivity + ResearchPages focused = 43 passed
frontend typecheck = PASS
```

Phase 14-R remains `PARTIAL`; queued/running recovery, lifecycle trash,
capability-wide viewer acceptance, operations and exact-SHA release gates
remain open.

## AN. Scientific Object lifecycle action wiring (2026-08-29)

The Data Platform now exposes archive/restore for Scientific Objects through
the existing managed-row action menu and the authoritative
`PATCH /api/scientific-objects/{object_id}` client. Active objects are removed
from the active-filtered list after archive; archived objects are removed from
the archived-filtered list after restore. Read-only project members retain
view-only actions and exact object/version routes. Product Pages focused
coverage is `20 passed`; this closes the missing object action bridge and its
read-only authorization regression but does
not claim trash/purge, bulk, or full lifecycle maturity.

Authenticated Chromium proof (requested executable) exercised object
`dc3c3eee-f254-4edf-a0fa-c955402b3069` / version
`8859cb49-0766-48cd-8a56-e44f5332e0c5`: the Scientific Object action menu
exposed archive, the object returned as archived, then restore returned it to
`ACTIVE` with the same current version. Browser response audit recorded no
5xx responses; the only console error was the expected pre-login bootstrap
`401`. The qualification object is currently `ACTIVE`.

## AO. Current-worktree regression after lifecycle/report controls (2026-08-29)

Fresh current-worktree checks after the Report 2.0 narrative contract,
pre-execution cancellation control, and Scientific Object lifecycle action
bridge are green:

```text
frontend full = 96 files / 619 tests passed
focused backend (Report/context/history/API) = 44 passed / 4 compatibility skips
Phase 8 PostgreSQL/Redis/MinIO report service campaign = 4 passed / 0 skipped
frontend typecheck = PASS
compileall = PASS
git diff --check = PASS
```

The service campaign initially exposed a local qualification-database
migration marker drift (`alembic_version=0006` while post-0006 tables existed);
the local database was stamped to the existing repository head
`0025_agent2_scientific_selection`, after which all four service tests passed.
No application service was stopped, and no Phase 14-R release commit or CI
seal was created.

## AP. Full regression and production build (2026-08-29)

The current worktree passed the fresh broad regression after the lifecycle
action and Report 2.0 changes:

```text
full backend = 1836 passed / 83 historical skips
full frontend = 96 files / 619 tests passed
production build = PASS
frontend typecheck = PASS
compileall = PASS
uv lock --check = PASS
touched Ruff = PASS
git diff --check = PASS
```

The 83 skips are pre-existing historical/optional compatibility tests; the
mandatory Phase 14-R focused and service-backed paths exercised in this run
were not converted to skips.

The explicit same-stack Agent2 service subset was rerun after the migration
marker correction:

```text
Phase 3/4/5 service-backed = 4 passed / 0 skipped
PostgreSQL = 127.0.0.1:55433/mdi
Redis = 127.0.0.1:6379/13
MinIO = http://127.0.0.1:9000 / mdi-artifacts
```

## AQ. ContextManifest budget truthfulness repair (2026-08-29)

The context manifest builder now computes the bounded inclusion set before
persisting its audit record. Scientific objects, semantic selections and
explicit Result references are critical and are preserved first; lower-priority
constraints/goals are excluded with stable item ids when the operation budget
requires compaction. If critical scientific context cannot fit, resolution
fails closed instead of silently dropping exact identity.

```text
ContextManifest focused = 5 passed
Ruff (touched context files) = PASS
```

Affected API/authorization/context/Report regression after this repair:

```text
61 passed / 4 compatibility skips
same-stack runtime = PostgreSQL + Redis + MinIO + Redis worker + DeepSeek
```

## AR. Operations backup/recovery qualification (2026-08-29)

The same-stack services remained online while isolated recovery drills
exercised each authority boundary.

```text
PostgreSQL:
  pg_dump → mdi_phase14r_restore_20260829_01 → pg_restore
  dump bytes = 1,359,213
  11 core authority table counts matched
  Alembic source/restored = 0025_agent2_scientific_selection
  orphan ScientificObjectVersion = 0
  invalid current-version pointers = 0

MinIO:
  qualification bucket = mdi-phase14r-recovery-20260829-01
  source/backup/restored/post-source SHA-256 matched
  missing object = fail-closed 404

Redis:
  primary 6379/13 remained online
  isolated 6380 transient key disappeared after forced restart
  PostgreSQL authority counts remained unchanged
  same-Job queue publish recovery regression = 2 passed
```

After the campaign, PostgreSQL reported `active=1`, `idle=10`,
`idle-in-transaction=0`; the five canonical workers were idle and
`/health/runtime` reported PostgreSQL/Redis/MinIO/Redis-worker/DeepSeek
healthy. Historical test queue registrations remain in transient Redis, and
alert thresholds, resource governance and production runbook automation are
not yet fully qualified. R11 therefore advances from `NOT_QUALIFIED` to
`PARTIAL`; Phase 14-R remains `PARTIAL`.

## AS. Queue lifecycle and worker availability repair (2026-08-29)

The Phase 2–8 service-backed fixtures now remove their unique RQ queue
registrations in successful/finally cleanup paths. Phase 4 also defaults
Result projection off at its `RESULT_PENDING` boundary, while Phase 5
explicitly enables its own unique Result queue; this prevents a live
canonical worker from crossing the fixture boundary.

```text
Phase 2–5 same-stack = 5 passed
Phase 6–8 same-stack = 10 passed
test queue registry before/after campaign = 208 / 208
Ruff = PASS
```

The 208 pre-existing strict test queue registrations were then inspected:
started/scheduled/deferred were all zero. The only queued wakeup pointed to a
PostgreSQL Job/Turn already `FAILED`, so the transient test registrations and
orphan wakeup were removed while PostgreSQL/MinIO authority remained intact.
Test queue registrations are now zero.

The old two-hour worker launcher had allowed planning and execution workers
to exit while idle. A no-secret launcher restored only those missing worker
roles. Final canonical state is five idle workers, five queues at depth zero,
and all runtime services healthy. Monitoring thresholds, quotas and release
seal remain open; overall Phase 14-R remains `PARTIAL`.

## AT. Dataset-list product fluency repair (2026-08-29)

An authenticated 25-sample same-stack API campaign isolated `/datasets` as
the bounded-read performance outlier:

```text
Projects p95 = 48.0 ms
Search p95 = 45.3 ms
Scientific Objects p95 = 17.5 ms
Project History p95 = 175.3 ms
Scientific Reports p95 = 31.2 ms
Datasets p95 = 936.9 ms (5,258-byte payload)
```

The durable Dataset listing queried Datasets once per Project and Profiles
once per Dataset. Current data contained 129 Dataset rows, yielding 265 SQL
statements per request. The repository read contract now supports bounded
batch listing and the projection uses three total queries for Projects,
Datasets and Profiles while retaining identical row count, visibility, and
latest-Profile selection.

```text
old direct path: 129 rows / 265 SQL / p50 312.0 ms / p95 324.6 ms
new direct path: 129 rows /   3 SQL / p50  19.7 ms / p95  20.5 ms
focused regression: 2 passed
touched Ruff: PASS
diff check: PASS
```

The existing browser API was left running as requested, so its pre-reload
measurement remains explicitly labeled. This closes one R6 performance defect
but not the cold/warm browser, Viewer, cancellation, mobile, and resource
budget campaign. Phase 14-R remains `PARTIAL`.

## AU. Redacted operations snapshot and truthful attention state (2026-08-29)

A repository-supported operations snapshot now combines PostgreSQL, Redis/RQ,
worker, and MinIO health without projecting connection URLs, credentials,
provider secrets, or filesystem paths. It distinguishes recent RQ failures
from retained historical diagnostics and automatic-stage Turn stalls from
explicit waiting boundaries.

```text
PostgreSQL connections = active 1 / idle 8 / idle-in-transaction 0
pool = size 5 / checked-out 0 / overflow -4
canonical workers = 5 idle
canonical queue depth = 0
recent RQ failures (15 minutes) = 0
retained historical RQ failures = 15
MinIO = OK
stale automatic-stage Turns = 9
stale queued/running Jobs = 1
```

The nine Turns belong to historical Agent2 service-qualification Projects.
The Job is `job_p6_1`, created by `test_user` for `Phase 6 #1`. No persisted
record was silently deleted or rewritten. The snapshot correctly reports
`attention`; recovery drill authority remains `PASS`, while alert delivery,
qualification-data reconciliation, concurrency/provider quotas, and the
production runbook remain open.

```text
operations focused = 3 passed
touched Ruff = PASS
```

R11 and overall Phase 14-R remain `PARTIAL`.

## AV. Final same-stack operations recheck (2026-08-29)

After restoring the missing `mdi-agent-turns` worker with the existing
repository launcher (without restarting PostgreSQL, Redis, MinIO, API,
frontend, or the authenticated browser), the current redacted snapshot is:

```text
PostgreSQL = active 1 / idle 7 / idle-in-transaction 0
pool = size 5 / checked-out 0 / overflow -4
Redis queues = depth 0
canonical workers = 5 idle
MinIO = OK
recent RQ failures (15 minutes) = 0
retained historical RQ failures = 15
stale automatic-stage Turns = 9
stale queued/running Jobs = 1
overall snapshot = attention
```

The attention state is intentional: the stale qualification rows remain
persisted historical data and are not silently deleted or rewritten. This
recheck confirms the runtime stack and worker floor are healthy, but it does
not close the open data-hygiene/reconciliation and mature-production gates.

## AW. Recoverable Project and Dataset Trash (2026-08-29)

Phase 14-R now exposes a recoverable Trash lifecycle for Projects and
Datasets without modifying scientific identity/version authority or released
Dataset status constraints.

```text
Project Trash authority = project_configs.config_json
Dataset Trash authority = datasets.metadata_json
Dataset persisted status while trashed = archived
outward Project/Dataset status = trashed
pre-Trash lifecycle retained = YES
restore to prior active/archived lifecycle = PASS
new ScientificObjectVersion = 0
scientific provenance deletion = 0
```

The Project and Data product surfaces provide explicit Trash filters,
dependency-impact previews, per-row Trash/Restore actions and bounded bulk
Trash/Restore. Trashed Projects no longer expose Upload, and trashed Datasets
do not expose Upload or Research actions. Global search accepts authorized
`status=trashed`; invalid `purged` filtering remains fail-closed. Owner/write
authorization and protected permanent-delete rules remain server-authoritative.

```text
backend lifecycle/access/history = 20 passed
frontend Project/Data lifecycle = 28 passed
frontend typecheck = PASS
frontend production build = PASS
touched Ruff = PASS
git diff --check = PASS
```

During current-stack restoration, the MinIO launcher was found to pass a
space-containing absolute data directory as multiple drive arguments. MinIO
was restarted with the same repository-supported credentials and a relative
qualification data directory; the `mdi-artifacts` bucket was created and
`/health/runtime` now reports PostgreSQL/Redis/MinIO/Redis-worker/DeepSeek all
`ok`. PostgreSQL, Redis, API, frontend and five worker queues remain online.

R3/R9 and overall Phase 14-R remain `PARTIAL`: ScientificObject, Research
Session and Report Trash, retention expiry/purge/export policy, full browser
Trash acceptance, capability-wide Viewer/Report quality, operations
governance and P14R-A/P14R-B exact-SHA release gates are still open.

## AX. Recoverable Research Session lifecycle (2026-08-29)

The existing `sessions.status` field now provides the bounded Research
Session management projection. `PATCH /research-sessions/{session_id}` is
project-write authorized and supports `TRASHED`/`ACTIVE`; archived/trashed
sessions remain readable for exact historical research, while new Messages and
ResearchTurns fail closed until restoration. A running/non-terminal Turn blocks
Trash. The Research Records popover exposes a reversible action with a
retention-aware confirmation. No scientific Turn, Result, Artifact, Evidence,
ScientificObject or ScientificObjectVersion is deleted or mutated.

```text
backend lifecycle = 17 passed
frontend ResearchPages = 37 passed
typecheck = PASS
compileall = PASS
prettier = PASS
git diff --check = PASS
```

This closes a narrow R3/R4 lifecycle seam only. Report/ScientificObject Trash,
retention/purge/export, broad browser acceptance, capability-wide Viewer
qualification, and P14R-A/P14R-B remain open; Phase 14-R stays `PARTIAL`.
## 2026-08-29 13:55 Report lifecycle and same-stack runtime closure

- 同栈 API 已切换到完整资格库 `.phase13-postgres-data2` 的 PostgreSQL 55434，迁移头 `0025_agent2_scientific_selection`；Redis 6379/13、MinIO 9000、5 个 Redis worker 保持运行。
- 认证登录接口在切换前因旧库缺少 `users` 表返回 500；切换后 `POST /auth/login` 返回 200，用户 `user_local`。
- 内置浏览器已登录并进入 `/tasks`，任务中心显示 10 项进行中、5 项已结束、15 个授权项目。
- Report lifecycle focused frontend: `2 passed`; Report/service backend: `45 passed, 4 historical compatibility skips`; same-stack Phase 8 Report service: `4 passed, 0 skipped`.
- 浏览器报告列表显示真实科学报告 `agent2_report_819f458171ba2d3219717895bf12eaf9`，状态筛选与“移入回收站”入口均可见；路由/服务未关闭。
- 当前工作树仍含大量既有用户/Phase 14-R 修改，未执行提交、推送或删除；本次新增的 Report 生命周期回归测试已通过。

### Report immutable-snapshot lifecycle evidence

The Report management bridge is now covered at both layers:

```text
frontend lifecycle = 2 passed
backend Report lifecycle = 20 passed / 4 historical compatibility skips
affected Report/access/domain = 45 passed / 4 skips
PostgreSQL/Redis/MinIO Phase 8 Report = 4 passed / 0 skipped
```

The backend regression proves `ACTIVE → TRASHED → ACTIVE` changes only the
project-scoped lifecycle overlay. `report_id`, immutable Report snapshot ID,
ScientificResultSnapshot ID, grounded content and exact source references do
not change. Before and after the authenticated report-list/read checks, the
complete qualification database remained:

```text
Jobs = 194 → 194
ToolCalls = 250 → 250
Artifacts = 995 → 995
ScientificResultSnapshots = 127 → 127
```

This closes the demonstrated Report Trash/Restore seam. It does not yet close
retention expiry/purge, broad browser destructive-action acceptance,
capability-wide Viewer quality, operations governance or the final P14R-A/B
release gates; Phase 14-R therefore remains `PARTIAL`.

### Report lifecycle authenticated browser golden path (2026-08-29)

Using the already authenticated same-stack browser tab at
`/projects/project_0002_1a0af866391f412d/reports`, the real report
`agent2_report_819f458171ba2d3219717895bf12eaf9` was moved from the active
filter to `回收站`, opened successfully from that filter, and its exact
Dataset source/version content remained readable. The browser then restored
the report and the `当前` filter showed it again. The lifecycle PATCH uses the
same project-authorized API and now sends the required JSON content type.

```text
browser archive/trash = PASS
browser historical report read while trashed = PASS
browser restore = PASS
browser active rediscovery after restore = PASS
scientific recomputation during lifecycle = NO
Jobs = 194 → 194
ToolCalls = 250 → 250
Artifacts = 995 → 995
ScientificResultSnapshots = 127 → 127
```

### Current-worktree frontend regression (2026-08-29)

The first full frontend invocation was stopped by the host C: volume
returning `0` free bytes (`ENOSPC` while Vitest wrote its temporary transform
files). No assertion failures were reported by that run. The same unchanged
test campaign was rerun with `TEMP`/`TMP` redirected to the available E:
qualification volume and completed successfully:

```text
frontend test files = 96 passed
frontend tests = 624 passed
```

This is an environment-capacity finding, not a product regression. The
qualification services and authenticated browser tab remained running.

After the report archive-action extension, the fresh full frontend campaign
also completed successfully:

```text
frontend test files = 96 passed
frontend tests = 625 passed
typecheck = PASS
git diff --check = PASS
```

### Report archive distinction (2026-08-29)

The report list now exposes the existing lifecycle contract without adding a
second authority: ACTIVE reports offer both `归档报告` and `移入回收站`,
ARCHIVED/TRASHED reports offer `恢复报告`, and all actions use the existing
project-authorized lifecycle endpoint. The focused UI regression is now
`4/4` passed, including visible failure recovery. The JSON content type is added in the shared API request helper
so browser PATCH calls are parsed consistently by the API.

The same authenticated browser tab also completed ACTIVE → `已归档` →
`恢复报告` and verified the report returned to the `当前` filter. The report
detail remained available through the archived route, preserving the exact
Dataset version.

Lifecycle failures are now surfaced as a bounded page alert
(`报告状态更新失败，请检查服务连接后重试。`) instead of being silently
ignored; this preserves the existing immutable report snapshot and gives the
user a recoverable action.

### Global search authenticated browser evidence (2026-08-29)

From the same authenticated project shell, the `搜索项目` dialog loaded and a
query for `mat-2` returned only authorized project-scoped results, including
the exact modern report and its Research session. The result links preserve
the project and report/Research route identities; opening the search itself
created no Job, ToolCall, Artifact or ScientificResult.

The corresponding authorization/bounds regression is `7 passed` in
`tests/test_project_access.py -k search`, including cross-project denial,
lifecycle filters, bounded query input and authoritative Result route
resolution.

### Runtime health after current qualification (2026-08-29)

`GET /health/runtime` continues to report API/database/Redis/MinIO/worker/LLM
as `ok` with PostgreSQL, Redis, MinIO bucket `mdi-artifacts`, Redis-backed
workers, and configured DeepSeek. PostgreSQL `pg_stat_activity` for the
qualification database reports `active=1`, `idle=5`, and no
`idle-in-transaction` connections.

### Research continuity browser evidence (2026-08-29)

The authenticated Research route rebuilt its timeline from persisted state and
showed completed Dataset and Structure runs with exact `run`/`turn` links,
while retaining the active project data scope and a disabled composer until a
new question is entered. This confirms leave/return continuity for completed
work; the broader edit/branch/stop/retry campaign remains open.

### Report dependency-impact preview (2026-08-29)

Report Trash now has an explicit, project-authorized dependency preview before
the lifecycle mutation. `GET /api/scientific-reports/{report_id}/dependency-impact`
derives a bounded list from the immutable Report snapshot and its authoritative
ScientificResult bundle (ResearchTurn, ScientificResult, Interpretation,
Artifacts, Evidence and exact source versions). The browser asks for explicit
confirmation after displaying the preview; canceling leaves the report ACTIVE.
The focused frontend suite is `4 passed`, and the Report backend lifecycle
suite is `20 passed / 4 historical compatibility skips`. The preview reports
`historicalProvenanceProtected=true` and `scientificSnapshotMutated=false`.

This closes the Report-specific dependency-preview seam only. Retention expiry,
purge governance, broad lifecycle browser coverage, capability-wide Viewer
acceptance, operations governance and exact P14R-A/P14R-B release CI remain
open; Phase 14-R remains `PARTIAL`.

### Browser qualification runtime isolation (2026-08-29)

The same-stack API remained healthy while the browser frontend briefly served
`500` because Next development and production build artifacts shared
`apps/web/.next`. The qualification launcher `.phase14r-start-web.ps1` now
uses the isolated `MDI_NEXT_DIST_DIR=.next-dev-phase14r` with the existing API
proxy. The current Chrome executable opened a fresh authenticated product tab
at `http://127.0.0.1:3000/` and received the normal Material Data Intelligence
shell (`200`). Existing API, PostgreSQL, Redis, MinIO, workers and user tabs
were kept running. This removes the runtime collision but does not claim
mature-product browser closure.

### Exact-source viewer fail-closed handling (2026-08-29)

The current-stack Structure browser probe found a persisted historical version
whose MinIO source key was absent. The viewer projection previously returned a
generic `500`; it now returns an explicit `SOURCE_MISSING` metadata projection
for not-found storage errors while retaining exact object/version identity and
limitations. Non-not-found storage failures and checksum mismatches remain
errors. `tests/test_agent2_phase9_viewers.py` passes `6/6`, and the fresh
Chromium object-action probe reports no critical 5xx responses. This closes the
missing-source error-handling seam only; capability-wide live acceptance and
the overall mature-product release gate remain `PARTIAL`.

### Fresh Dataset scientific execution and Report grounding repair (2026-08-29)

A fresh authenticated same-stack Dataset run completed after the projector and
runtime repairs. Dataset `dataset_0002_53c12dddfa984a80` was promoted
idempotently to object `723cf740-f178-4ca8-aa80-3edc708396cc`, version
`809a6825-5bfe-4820-81fc-b589ba447abc`. New ResearchTurn
`9c3a8278-69cf-4f9e-973a-e0b5d0e46779` preserved exact object/version and
`DATASET_SAMPLE` locator `mat-2` in ContextSnapshot
`a42d0089-eb20-4832-be57-40423eed4e11`.

The run completed `ANALYZE → PLAN_READY → JOB_ATTACHED → RESULT_READY →
INTERPRETATION_READY → TURN_COMPLETED`. CapabilityPlan
`18d3ec48-35fc-422f-9139-ba9b29c50506`, Job
`job_agent2_9c3a827869cf4f9e973ae0b5d0e46779`, ToolCall
`call_job_agent2_9c3a827869cf4f9e973ae0b5d0e46779_step_1`, and Artifact
`call_job_agent2_9c3a827869cf4f9e973ae0b5d0e46779_step_1-table_json` were
persisted. ScientificResult snapshot
`c73dd037-07bd-447e-a049-a97e5426d371` contains 16 authoritative facts,
including `dataset.sample_id = mat-2` and `dataset.sample.band_gap = 2.5`;
Interpretation `a674095b-7349-4d4f-9db7-e9008c0e0b8e` is `VALID`.

The first report attempt exposed a narrow validator defect:
`REPORT_GROUNDING_FAILED` treated numeric substrings inside opaque
UUID/version identifiers as scientific claims. The fix is confined to
`scientific_reports/grounding.py`: embedded numeric tokens in opaque
alphanumeric identifiers are ignored, while ordinary scientific numbers and
scientific notation remain fail-closed. Focused report coverage is `21 passed,
4 skipped`, including a negative unsupported-claim regression. After the
report worker was restarted with current code, generation
`474ebaeb-0e02-5610-ad70-7d4cb7be7cf5` reached `READY`; Report
`agent2_report_c91972312383616a6503acd6be76e233` opened in the authenticated
browser with exact Result/version, findings, methods, limitations and
conclusion. Repeated reproducibility-manifest export left Jobs `198`,
ToolCalls `255`, Artifacts `1014`, and ScientificResult snapshots `130`
unchanged (delta `0`).

Current-worktree verification records frontend `96 files / 631 tests passed`,
backend `1848 passed / 83 skipped / 0 failed / 0 errors`, typecheck,
compileall, `uv lock --check`, touched Ruff and `git diff --check` all PASS.
The same-stack mandatory integration subset completed `11 passed / 0 failed /
0 errors / 0 skipped`; `/health/runtime` reports PostgreSQL, Redis, MinIO,
Redis workers and configured DeepSeek. Capability-wide mature-product,
retention/recovery, and exact-SHA release gates remain open, so Phase 14-R
remains `PARTIAL`.

### Explicit Dataset handoff and real-worker qualification (2026-08-29)

The authenticated Data Platform → Research deep link now preserves its
explicit `datasetId`, avoids selecting the first historical session, and binds
new sessions/messages to the selected Dataset. Focused frontend coverage is
`ResearchPages 38/38` and `product-api 4/4`.

The same-stack browser probe used a fresh CSV uploaded through the real product
path. PostgreSQL/MinIO persistence completed and, after five repository Redis
workers were started, Job `job_9a63cc82cf574e25a88529c7` completed with one
ToolCall and three Artifacts. The direct Planner route still does not
automatically materialize a ResearchTurn / ScientificResult interpretation;
this is concrete remaining Research → Result integration debt, so
Phase 14-R remains `PARTIAL`.

### Authenticated Report reproducibility export (2026-08-29)

The authenticated Chrome path opened Report
`agent2_report_819f458171ba2d3219717895bf12eaf9` in Project
`project_0002_1a0af866391f412d` and downloaded
`mat-2-band_gap-数值分析-reproducibility.json` through the normal
`导出复现清单` action. The downloaded
`mdi.reproducibility-manifest/1.0` preserves snapshot
`bd1a3fad-eb49-5212-b6bf-e1f92fac03a8`, ResearchTurn
`8382c443-f9ca-4c90-9aa3-444fea683807`, ScientificResult snapshot
`2809dcd1-243e-4323-8538-0a5fe81780d9`, Interpretation
`efccf7a2-6666-429e-be92-20cb2cf659de`, Dataset object
`8a425466-b697-4c85-9a43-199414a22865`, and exact version
`be02266a-7d4f-4ebb-9f28-3132855167d0`. Content checks found no credential,
provider-prompt, raw Tool-log, script, or JavaScript payload.

Persisted scientific counts were identical before and after the browser
export: Jobs `196`, ToolCalls `253`, Artifacts `1007`, and ScientificResult
snapshots `129`. Chrome console warnings/errors were empty. This closes the
Report-level browser/export and no-recompute seam; cross-entity retention and
export governance remain `PARTIAL`.

### Bounded Report reproducibility manifest (2026-08-29)

Scientific Report presentation now offers `导出复现清单` in addition to
Markdown. The deterministic JSON manifest preserves authorized Report,
snapshot, ResearchTurn, ScientificResult, Interpretation, exact
ScientificObjectVersion, Figure Artifact, Evidence and limitation references.
It is non-executable and omits provider prompts, credentials, raw Tool logs and
unbounded payloads. `ScientificReportRoute.test.tsx` passes `8/8`; opening or
exporting the report remains read-only with no scientific recomputation.

### Current frontend regression after viewer repair (2026-08-29)

The current worktree frontend campaign completed on the E: qualification
volume with Vitest's single-fork pool:

```text
test files = 96 passed
tests = 630 passed
```

The campaign includes Research, Data Platform, Report, Scientific Presentation,
Viewer, Task Center, Notifications, accessibility and no-recompute suites.
Typecheck and production build also pass on the same worktree. No services or
user Chrome tabs were closed during the campaign.

### Current backend/static regression after viewer repair (2026-08-29)

The current worktree backend campaign completed with:

```text
backend = 1847 passed / 83 skipped / 0 failed / 0 errors
compileall = PASS
uv lock --check = PASS
touched Ruff = PASS
git diff --check = PASS
```

The skips are the repository's existing optional or historical compatibility
cases; no new Phase 14-R mandatory test was converted into a skip.

### Operations snapshot direct invocation (2026-08-29)

`scripts/phase14r_operations_snapshot.py` now resolves the monorepo API and
schema/adapter package roots from its own path, so the redacted operational
diagnostic is runnable from a clean shell without a hidden `PYTHONPATH` prerequisite. With
the same-stack environment explicitly configured, the current snapshot reports
PostgreSQL/Redis/MinIO healthy and five idle workers; it also truthfully
reports `status=attention` because persisted historical turns/jobs exceed the
staleness threshold. This is an operations-diagnostic improvement, not a
closure claim; Phase 14-R remains `PARTIAL`.

### ScientificObject recoverable Trash lifecycle (2026-08-29)

Added Alembic `0026_scientific_object_trash_lifecycle`, widening only the
ScientificObject lifecycle check to include `TRASHED` and adding the nullable
`pre_trash_lifecycle_status` management marker. The existing authorized PATCH
endpoint accepts `lifecycle=TRASHED|ACTIVE|ARCHIVED` alongside the legacy
`archived` boolean. Restore deterministically returns an object to its
pre-Trash ACTIVE/ARCHIVED state. Data Navigator now queries the authoritative
`TRASHED` list and exposes reversible Trash/Restore actions.

Evidence: `tests/test_agent2_domain.py` 10 passed, `tests/test_agent2_api.py`
17 passed, `apps/web/app/components/ProductPages.test.tsx` 22 passed; touched
Ruff, compileall and diff check passed. Same-stack PostgreSQL migration applied
and live object `f6cdd30c-4797-4484-ab61-77010f8783cb` completed
`ACTIVE → TRASHED → ACTIVE` with one unchanged version and current-version
identity. Phase 14-R remains `PARTIAL`: retention/purge/export, broad Viewer
and real-user acceptance, recovery/performance, and exact-SHA release gates
remain open.

### ScientificObject dependency-impact preview (2026-08-29)

ScientificObject Trash now uses a bounded server-derived dependency preview
before the existing lifecycle PATCH. `GET
/api/scientific-objects/{object_id}/dependency-impact` resolves authorized
exact-version references from ScientificResult bundles, ResearchTurns, and
Report snapshots and reports protected historical provenance without mutating
scientific snapshots or versions. The Data Navigator confirmation dialog
displays the preview and only then enables the explicit Trash action. Focused
coverage is `tests/test_agent2_api.py: 17 passed` and
`apps/web/app/components/ProductPages.test.tsx: 24 passed`; this is a narrow
lifecycle safety improvement, not closure of the broader retention, purge, or
real-user acceptance gates.

### Exact-source viewer fail-closed handling (2026-08-29)

The current-stack Structure browser probe found a persisted historical version
whose MinIO source key was absent. The viewer projection previously returned a
generic `500`; it now returns an explicit `SOURCE_MISSING` metadata projection
for not-found storage errors while retaining exact object/version identity and
limitations. Non-not-found storage failures and checksum mismatches remain
errors. `tests/test_agent2_phase9_viewers.py` passes `7/7`, and the fresh
Chromium object-action probe reports no critical 5xx responses. This closes the
missing-source error-handling seam only; capability-wide live acceptance and
the overall mature-product release gate remain `PARTIAL`.

### QUERY_DATA terminal browser orchestration repair (2026-08-29)

The fresh authenticated browser probe exposed a runtime-only orchestration
seam. The backend router correctly classified query-only work as `QUERY_DATA`,
but the Turn worker was still running the pre-repair code and persisted
`ORCHESTRATION_COMPLETED.dispatch_status=READY_FOR_DOWNSTREAM`, leaving the
Turn in `ORCHESTRATING` with no downstream consumer. The stale worker registry
was cleaned for the exact worker name and `phase14r-turns-55434` was relaunched
from the current worktree; PostgreSQL/Redis/MinIO and the existing browser tab
were left running.

The fresh post-restart browser Turn
`ddad0068-144e-4377-abe3-44a0e2601592` now persists
`status=ANSWERED`, `action_type=QUERY_DATA`, no Plan/Job/ToolCall/Artifact/
ScientificResult, and `ORCHESTRATION_COMPLETED.dispatch_status=COMPLETED`.
The page renders `数据查询已完成` and the direct acknowledgement
`已识别为数据查询请求。请在数据平台查看或调整筛选条件；本次未创建科学分析运行。`
without showing a scientific execution state. Frontend focused coverage is
`46` tests after adding the `ANSWERED` progress regression; the browser probe
has zero fatal/unhandled/critical errors. This closes the demonstrated
QUERY_DATA worker/runtime and frontend terminal-state seam only. Phase 14-R
remains `PARTIAL`; capability-wide real-user acceptance, retention/export,
recovery/operations qualification, full surface coverage, and exact-SHA
P14R-A/P14R-B release gates remain open.
### Batch product qualification: Report lifecycle, search and recovery entry points (2026-08-29)

The existing authenticated Chrome tab stayed open while one grouped campaign
covered several related mature-product seams:

1. Report `agent2_report_c91972312383616a6503acd6be76e233` moved
   ACTIVE -> ARCHIVED -> ACTIVE, remained readable in the archived filter, and
   preserved Dataset source `723cf740-f178-4ca8-aa80-3edc708396cc` /
   `809a6825-5bfe-4820-81fc-b589ba447abc` and Result snapshot
   `c73dd037-07bd-447e-a049-a97e5426d371`.
2. The Report Trash confirmation showed a bounded server-derived preview with
   six protected dependencies (ResearchTurn, ScientificResult, Interpretation,
   exact source version, evidence, and data source); the action was canceled.
3. Global search for `mat-2` returned authorized Report and Research-session
   links only.
4. `/tasks` and `/notifications` loaded from the same product shell and expose
   persisted-state reload/recovery entry points.

Focused backend lifecycle/report coverage is `39 passed, 4 historical skips`;
the same-stack integration subset is `11 passed, 0 skipped`. No scientific
authority or Result was mutated and no recomputation was triggered. Phase 14-R
remains `PARTIAL`; capability-wide Viewer acceptance, complete lifecycle and
retention governance, recovery/operations qualification, and P14R-A/P14R-B
exact-SHA release gates remain open.

### Batch product qualification: bounded bulk Report lifecycle (2026-08-29)

The Report list now exposes bounded multi-select lifecycle operations for
ACTIVE and ARCHIVED scientific reports. Bulk Archive and Bulk Restore reuse the
existing lifecycle API; bulk Trash remains intentionally unavailable because
Trash requires per-report server-derived dependency impact and explicit
confirmation. The authenticated Chrome proof selected
`agent2_report_c91972312383616a6503acd6be76e233`, archived it, verified it
under the archived filter, and restored it to ACTIVE. Dataset object/version
and ScientificResult snapshot provenance remained unchanged. Opening the
archived report now displays an explicit archived-state notice and an exact
`ResearchTurn` link:
`/projects/project_0002_1a0af866391f412d/research?turn=9c3a8278-69cf-4f9e-973a-e0b5d0e46779`.
The report remained scientifically readable while archived and the final
browser state was restored to two ACTIVE reports.

Focused frontend coverage for this grouped product batch is `37 passed`; the
same-stack service subset remains `11 passed, 0 failed, 0 errors, 0 skipped`.
Phase 14-R remains `PARTIAL`: capability-wide surface acceptance,
retention/export governance, recovery/operations qualification, and exact-SHA
P14R-A/P14R-B release gates are still open.

### Batch product quality: lifecycle toolbar states and report provenance (2026-08-29)

The Report list lifecycle toolbar now groups selected reports by their actual
ACTIVE/ARCHIVED status, so the `全部` filter remains actionable when a
selection mixes states. Partial `Promise.allSettled` outcomes update successful
rows immediately, retain only failed report IDs selected, and expose a
retryable Chinese error instead of implying an all-or-nothing success. Filter
changes clear stale selection and lifecycle errors. The report reader now
surfaces explicit ARCHIVED/TRASHED notices and links back to the exact
ResearchTurn that produced the report.

The UI uses the existing scientific workbench tokens: quiet bordered toolbar,
one accent for actions, a 4/8px spacing rhythm, and a two-column mobile action
layout that keeps row navigation and lifecycle controls reachable. Focused
frontend coverage is `40 passed`; typecheck passes. This is a bounded product
quality improvement and does not close the wider capability, retention,
recovery, real-user, or exact-SHA release gates.

### Batch product quality: task center and notification status surfaces (2026-08-29)

Task Center and Notification Center now share a restrained status vocabulary
with semantic badges for active, pending, success, warning, danger, and muted
terminal states. Persisted job identifiers remain visible as secondary
metadata, while action groups expose exact open/retry/stop links with an
accessible status-specific label. At widths below 960px the action group
expands to the row width so stop and retry controls remain reachable without
horizontal scrolling. This preserves the existing real-job authority:
opening, retrying, or stopping still routes through the persisted ResearchTurn
and cancellation API; no browser-side scientific execution was added.

The focused frontend campaign is `5 files / 58 tests passed` for Research,
Report, Task Center, and Notification surfaces; `apps/web` typecheck passed;
`git diff --check` reported no whitespace errors (only normal CRLF conversion
warnings). Same-stack runtime remained PostgreSQL/Redis/MinIO with existing
workers and Chrome tab left running. This closes a bounded control-surface
quality seam only; Phase 14-R remains `PARTIAL` for capability-wide viewer
acceptance, retention/export governance, recovery/operations qualification,
real-user acceptance, and P14R-A/P14R-B exact-SHA release gates.

### Runtime and task-center consistency repair (2026-08-29)

The same-stack runtime was re-established after the frontend regression
process had released the long-running local services. PostgreSQL `55434`,
Memurai Redis `6379/13`, MinIO `9000` and the API/frontend/workers are running
again. The MinIO launch root cause was proven to be Windows argument splitting:
the workspace path contained spaces and was passed as multiple server volumes,
leaving MinIO in `XMinioServerNotInitialized`. Relaunching with one explicitly
quoted volume initialized a single-node server; the API health probe now
reports `database=postgresql`, `redis=redis`, `artifactStorage=minio`,
`worker=redis`, and configured DeepSeek.

The live authenticated Task Center then showed `0` active and `17` ended
tasks. Legacy rows with `workspaceProjectionStatus=LEGACY_READ_ONLY` remain
available as historical read-only records but no longer inflate the active
count. The exact task links and stale-state notices remain visible. Focused
Task/Notification tests are `2 passed`; the full frontend regression is
`96 files / 638 passed`; the Context Manifest/operations backend checks are
`9 passed`; typecheck passes. No scientific records were mutated.
Phase 14-R remains `PARTIAL` because capability-wide viewer validation,
retention/export governance, recovery/operations campaign, real-user
acceptance, and exact-SHA P14R-A/P14R-B release gates remain open.

### Batch product quality: Research result control hierarchy (2026-08-29)

Completed-result Research presentation actions are now grouped under the
explicit heading `继续这项研究`. The five existing operations—edit question,
continue, deliberate new rerun, no-recompute reinterpretation, and pin/unpin
result—share one bounded action region with a short explanation of their
semantics. Pending operations expose a polite live status stating that the
scientific result itself is not overwritten. The layout uses five columns on
wide workbench screens, two columns at tablet widths, and one full-width
touch-safe column on mobile; it keeps the existing mineral-green/quiet-neutral
tokens and avoids a card wall.

Focused Research/presentation/execution coverage is `52 passed`; the full
frontend baseline remains `96 files / 638 passed`; typecheck and touched
Python Ruff checks pass. The authenticated in-app browser remains open on the
local product; services remain same-stack and healthy. Phase 14-R is still
`PARTIAL` for the unqualified capability-family, retention/export, recovery,
real-user and exact-SHA release gates.

### Batch product quality: global search keyboard and result hierarchy (2026-08-29)

The existing authorized global search now has a predictable keyboard entry point
(`Ctrl/⌘ K`), an explicit clear control that restores focus to the query field,
and an accessible result-count announcement. Each result keeps its bounded kind
and lifecycle status visible as a quiet semantic badge, while the explanatory
helper text makes the authorization boundary explicit. The dialog remains
single-instance, focus-trapped, and responsive under the existing scientific
workbench tokens; no search authority or cross-project behavior changed.

`apps/web/app/components/ProductShell.test.tsx` passes `7/7`, and the grouped Research/Report/Task/Search campaign passes `8 files / 79 tests`; typecheck passes. Coverage includes shortcut,
clear/focus, result-count, and bounded kind/status-filter coverage. This is a
small R7 organization/fluency improvement only. Phase 14-R remains `PARTIAL`:
capability-wide real-user acceptance, retention/export, recovery/operations,
and exact-SHA P14R-A/P14R-B release gates are still open.

### Current-worktree UI/source recovery addendum (2026-08-30)

The current same-stack runtime was rechecked without closing the API, workers,
MinIO, Redis or authenticated browser tab. The XRD Data Platform surface for
`dataset_0001_a3f92a7657f4493e` rendered one validated chart series with 9 values
and the linked Si Structure Viewer after repository-owned normalized objects were
restored to the existing `mdi-artifacts` bucket. No database scientific rows were
changed. Browser error/warning logs were empty.

The missing normalized-source branch now fails closed with a typed retryable
`SOURCE_RESOURCE_UNAVAILABLE` 409 response; the Viewer offers `重试加载` and
`查看来源与属性` while keeping raw infrastructure details out of the normal UI.
Resource controls use one clear label plus current/switch state. At `390x844`,
the data navigator defaults to an explicit `显示数据` collapse control and the
exercised page had no horizontal overflow (`body.scrollWidth=388`).

The Report index kicker labels were aligned to the Chinese workbench hierarchy:
`项目报告` / `已验证结果` / `历史运行`. Focused frontend coverage for this batch
is 41 passed, backend project-access coverage is 18 passed, and frontend
typecheck passes. These are bounded quality improvements; Phase 14-R remains
`PARTIAL` pending capability-wide real-user acceptance, retention/export,
recovery/operations, and exact-SHA release gates.

### Completed ResearchTurn presentation convergence (2026-08-30)

The live canonical Dataset route exposed two presentation projections for one
completed ResearchTurn: the exact-turn `Agent2ScientificPresentation` followed
by the legacy run-level workbench projection. The latter also displayed a false
empty-result message. The current worktree now treats the exact completed/partial
ResearchTurn presentation as the single workbench result surface while retaining
legacy/in-progress rendering for their valid cases. Focused Research and
presentation coverage is `46 passed`; frontend typecheck passes. No scientific
authority or persisted result was changed.

### Task and notification identity hierarchy (2026-08-30)

Task Center and Notification Center now keep implementation identity out of
the primary scan path. Persisted status plus a bounded product label is shown
first; exact Job IDs remain available through a collapsed `技术身份`
disclosure. Exact Workspace/Research links, explicit ResearchTurn cancellation,
retry eligibility and polling/reconnect behavior were not changed. The
five-file Task/Notification/Research/Report focused campaign is `55 passed`;
 frontend typecheck passes.

### Batch product quality: task filters and action hierarchy (2026-08-30)

Task Center now presents each task exactly once under a compact tabbed filter:
`全部` / `进行中` / `需要关注` / `已结束`. This removes duplicate retry entries
from the prior grouped view while preserving persisted status, exact
Workspace/Research navigation, cancellation and retry semantics. Each row places
the primary `打开` action beside the status/product label and keeps the raw Job
ID under progressive disclosure (`技术身份`).

Completed Research presentation actions retain their scientific semantics but make
`继续研究` the single primary action; explicit rerun, reinterpretation, question
editing and context pinning remain secondary controls. On mobile all five actions
remain full-width and touch-safe.

Real same-stack Playwright verification (2026-08-30) recorded one canonical
Dataset `科学呈现`, no false empty-result state, and five action controls;
Task Center 17 persisted tasks with four filters, 17 technical disclosures and
17 primary open actions; Notification Center 7 persisted notifications with
7 technical disclosures and 7 primary open actions. Desktop widths were
`1280/1280`; mobile Research at `390x844` had five `390px` controls,
`body.scrollWidth=390`, and a reachable reinterpret action.

The only observed `401` was the expected pre-login `/auth/me` bootstrap request;
authenticated paths had no page errors or critical 4xx/5xx responses. Focused
frontend coverage is `47 passed`; typecheck passes. Phase 14-R remains
`PARTIAL` because capability-wide real-user acceptance, lifecycle/recovery/
retention/operations gates and P14R-A/P14R-B exact-SHA release gates remain open.

### Batch product quality: Report mobile overflow and current fluency baseline (2026-08-30)

The current-worktree Chromium matrix found a 30 px transient mobile overflow in
the Report Evidence list: long evidence/result/version identifiers forced a
grid item to retain min-content width. Evidence items now explicitly shrink and
wrap long identifiers. A fresh same-stack matrix with a 250 ms render-settle
window recorded `maxOverflow=0` for Data, Research, Viewer, Report, Tasks and
Notifications on desktop and for Data, Research and Report at `390x844`.

Warm usable-time p50/p95 (ms) was: Data desktop `1144/1253`, mobile
`1077/1141`; Research desktop `1275/1438`, mobile `1224/1272`; Viewer desktop
`1197/1251`; Report desktop `969/1173`, mobile `867/887`; Tasks desktop
`1144/1939`; Notifications desktop `1079/1249`. Maximum transfer was about
2.57 MB and all measured routes had no page errors or critical 5xx responses.
This closes the demonstrated mobile layout defect and advances R6 evidence;
provider-scale context, submit/cancel latency and full real-user acceptance
remain open.

### Batch product quality: context transparency and global search hierarchy (2026-08-30)

The ContextManifest contract is unchanged, but the Research timeline now
projects it in two deliberate layers. Normal users first see the operation,
included scientific context, inclusion reason, authority class and exact
object/version or Result reference. Manifest ID, policy version, input budget,
actual token estimate and fingerprint remain available under `审计详情`.
Canonical authenticated Turn
`9c3a8278-69cf-4f9e-973a-e0b5d0e46779` displayed two included context items and
the exact Dataset version `809a6825-5bfe-4820-81fc-b589ba447abc`; desktop
`1280x720` and mobile `390x844` both had zero overflow and zero browser errors.

Global search now exposes the accurate `搜索科学工作` entry, Chinese scientific
Result/lifecycle labels and one primary `打开` action. The backend projection
uses the earliest authorized user question as a Research Session title instead
of exposing `research_<id>`; the exact Session ID remains unchanged in the
authorized route. Authenticated `mat-2` search returned six results, zero raw
Session-ID titles and zero mobile overflow. Backend access/search coverage is
`19 passed`; the grouped frontend batch is `5 files / 59 tests`; typecheck and
touched diff-check pass. Phase 14-R remains `PARTIAL` pending full scientific
surface acceptance, retention/operations closure, complete regression and
P14R-A/P14R-B exact-SHA release gates.
### Batch product quality: Research session lifecycle and historical read-only placement (2026-08-30)

Research session management now uses the existing `sessions` authority with
bounded organizational metadata from migration `0027_research_session_management`:
`title_override`, `is_pinned`, and `pre_trash_status`. Project-write users can
rename, pin, archive, trash and restore a session; a non-terminal Turn blocks
Trash. Archived/trashed sessions remain readable and exact historical
identities remain unchanged, while server-side Message and ResearchTurn writes
fail closed until restoration.

The Research Records popover is organized as `当前 / 已归档 / 回收站`, with
pinned records first and row actions in the existing overflow menu. The selected
session header now carries the human title and lifecycle badge; Restore is
placed next to the Records action. On archived/trashed routes the composer is
replaced by an explicit read-only explanation and retry is withheld, so the
layout communicates that historical science is available but new work requires
restoration. This keeps lifecycle actions beside the conversation they govern
without competing with the scientific workbench.

Evidence: backend `tests/test_project_access.py` `19 passed`; frontend
`ResearchPages.test.tsx` `40 passed`; typecheck `PASS`; touched Ruff `PASS`;
`git diff --check` `PASS`. The authenticated same-stack research-management
browser harness exercised pin → rename → archive → trash → restore on an empty
acceptance session without creating or mutating scientific Turns, Results or
source versions, and recorded desktop/mobile screenshots with no overflow or
browser errors. Phase 14-R remains `PARTIAL`; no P14R-A/P14R-B commit has been
created.

### Batch product quality: Report management action hierarchy (2026-08-30)

The Reports index now preserves the scientific reading hierarchy: report title
and context remain the dominant row content; Archive, Trash and Restore are
owned by the row overflow menu rather than displayed as a permanent button
wall. Batch checkboxes and Archive/Restore controls appear only after an
explicit `批量管理` action. Bulk Trash remains unavailable because the existing
contract requires a server-derived dependency impact and confirmation for each
immutable report snapshot.

The dependency preview now uses the shared focus-managed modal rather than an
inline pseudo-dialog. Escape closes the modal and returns focus to the
originating report action. The authenticated same-stack Chromium campaign
resolved duplicate human titles through the exact Report link identity,
archived and restored
`agent2_report_c91972312383616a6503acd6be76e233`, and inspected six persisted
dependencies without mutation. Mobile evidence at `390x844` recorded
`document/body = 390/390`, `overflowCount = 0`, and a reachable explicit
selection mode.

Evidence: `ScientificReportsIndexPage.test.tsx` `8 passed`; grouped
Report/Research/ProductShell/Task/Notification regression `6 files / 68
tests`; frontend typecheck `PASS`; touched Ruff `PASS`; `git diff --check`
`PASS`. The only browser console error was the expected pre-login `/auth/me`
bootstrap `401`; authenticated report navigation had no critical response
failure. Phase 14-R remains `PARTIAL`; P14R-A/P14R-B do not yet exist.

### Batch product quality: App Router navigation fluency (2026-08-30)

The reported “every page reloads” behavior was investigated with authenticated
click navigation. `数据 → 研究 → 报告 → 概览` produced zero document requests
on every transition and retained a browser window marker, so the framework was
already using Next App Router client navigation. The actual UX defect was
route data latency combined with no visible transition state.

The browser auth request is now coalesced/cached for the session, eliminating
post-login `/auth/me` requests during measured transitions. ProductShell
prefetches sibling project routes on pointer/focus intent. Native Next
loading boundaries were added for project/data/research/report/tasks/
notifications with the same shell hierarchy and an explicit
`正在保留当前研究上下文…` status.

Current same-stack Chromium navigation evidence:

```text
cold usable: Data 481ms · Research 991ms · Reports 1659ms · Overview 952ms
warm usable: Data 131ms · Research 967ms · Reports 95ms · Overview 922ms
document requests: 0 on all transitions
post-login /auth/me requests: 0
window marker preserved: YES
critical responses: 0
```

Under a controlled 600 ms RSC-delay diagnostic, the persistent root-layout
transition indicator was observed on every route change, so slow server
navigation is no longer presented as an unexplained blank/full reload.

Frontend typecheck and grouped focused tests pass. The broader performance
gate remains `PARTIAL`; this batch does not claim provider-scale or full
mobile timing closure.

The project route group now owns a persistent `ProductRouteFrame`; nested page
wrappers reuse one shell/auth frame across project navigation. Query-aware
transition state is behind Suspense, and the production build generates all
application routes successfully.

Fresh full frontend regression after the navigation/layout changes is
`97 files / 649 tests passed`. Next production build passes with all 17
application routes generated; the project route shells are `175–178 B` each
and heavy Dataset work remains isolated to its own route chunk. The report
mobile fix and root layout change introduced no frontend regressions.

### Batch product quality: Dataset query continuity and repeated presentation IDs (2026-08-30)

The Data workbench had a real client-navigation defect: after a Next
App-Router query transition, an older `selectedId` remained valid in the
visible list and short-circuited URL selection, so the address bar changed
while the main Viewer stayed on the previous Dataset. `ProjectDataPage` now
gives a valid `dataset` query authoritative priority and falls back to the
existing selection only when no valid route selection exists.

Fresh authenticated Chromium evidence against the running same-stack API:

```text
Phase14R Band Gap Acceptance
  → Phase14R XRD Validation
  → Phase14R Band Gap Acceptance

main heading/active row: changed on every transition
document requests: 0
RSC requests: 2
window marker preserved: YES
```

The same batch hardened `ScientificPresentationBlocks` accessibility by using
React `useId` whenever no explicit presentation instance identity is supplied.
Repeated presentation instances now have distinct `aria-labelledby` targets.
Focused frontend coverage is `87 passed`; typecheck and optimized production
build pass. No scientific authority, version, or execution contract changed.

Same-stack runtime verification at the end of this batch:

```text
GET /health/runtime = 200
database = postgresql
redis = redis
artifactStorage = minio (mdi-artifacts)
worker = redis
llmProvider = deepseek (configured)
```

The redacted operations snapshot reported `workerCount = 6`, all workers idle,
zero queued jobs, zero recent failed jobs, and `idleInTransaction = 0`.
It remains `attention` because historical stale ResearchTurn/Job records are
still visible to the diagnostic threshold (`13` stale active Turns and `1`
stale Job); this is intentionally not converted to a false PASS.

Authenticated XRD presentation browser proof on the same stack:

```text
Dataset: dataset_0001_a3f92a7657f4493e
desktop: 1280/1280 document/body
mobile: 390/390 document/body
professional XRD panel: visible
table alternative: opened (9 rows)
mutating scientific requests while loading/opening: 0
critical responses: 0
browser errors: expected pre-login /auth/me 401 only
```

The XRD pair is now selected by exact producer identity, so the product
surface renders the persisted experimental XRD plot and its authoritative
comparison table instead of a generic plot-only fallback.

The preserved authenticated in-app browser tab was also used for the same
qualification: the XRD URL transition changed the active Dataset row and
Viewer content without a full reload; after renderer settling it showed
`已渲染 1 个数据系列和 9 个数值`, `实验 XRD 与结构上下文`, and an interactive
Structure canvas. The in-app tab's captured error/warning log was empty and
the tab was marked for handoff rather than closed.

Focused backend regression after the browser batch is `68 passed`. An initial
attempt injected the shared PostgreSQL variables into the historical
`test_phase2_product_loop` temporary-runtime test and correctly failed on its
fixed project-name uniqueness constraint; rerunning under that test's isolated
runtime contract passed all `68` cases. This is recorded as test-environment
separation evidence, not a production API regression.

### Batch product quality: Multi-family Report quality and mobile closure (2026-08-30)

A real same-stack Report worker was restored on `mdi-agent-reports`; a fresh
Structure Report was generated from the existing exact Result without creating
new scientific execution state. The first provider attempt correctly failed
closed with `REPORT_GROUNDING_FAILED`; the worker retry produced VALID Report
`agent2_report_401cfb421fcab8a9366e06fedb3acb6d` / snapshot
`a6e1d02e-6672-5f9f-b4e1-3397ed0c84f0` for Turn
`17b67e68-b7db-475b-bb4c-3b336cb2ba15`, retaining exact version
`8859cb49-0766-48cd-8a56-e44f5332e0c5` and independent CrystalNN/VoronoiNN
findings. Scientific counts before/after were unchanged: Jobs `208`, ToolCalls
`269`, Artifacts `1070`, ScientificResults `140`; only one Report snapshot was
added.

The same browser campaign opened the existing Dataset Report
`agent2_report_c91972312383616a6503acd6be76e233`, retaining version
`809a6825-5bfe-4820-81fc-b589ba447abc`, sample `mat-2` and three findings.
Both reports expose research question, method, discussion/limitations,
conclusion and bounded next steps; browser text contained no raw capability IDs
or raw JSON. A long `fact.*` reference had caused a real 45 px mobile document
expansion; wrapping the findings column closed it at `390/390` with no
overflowing nodes.

`ScientificReportRoute.test.tsx` is `11 passed`; Report quality browser evidence
has zero critical responses and only the expected pre-login `/auth/me` `401`.
Phase 14-R remains `PARTIAL` pending capability-wide surface acceptance and
release gates.

### Result reuse / re-interpret browser proof and grounding repair (2026-08-30)

An authenticated browser run exposed a real R4 defect in the existing
``重新解释（不重算科学结果）`` action: it correctly created a child
`INTERPRET_RESULT` turn with no Plan/Job/ToolCall/Artifact/Result growth, but
the interpretation worker rejected a provider lead sentence that introduced a
number not repeated in the Finding text. The authoritative Dataset facts and
Finding references were valid; the rejection was limited to presentation
prose. The repair is in the interpretation boundary: when the only rejection
is `answer_lead introduces an unsupported quantitative claim`, the service
deterministically projects the lead from the first already-grounded Finding
and re-runs the unchanged validator. Unsupported Finding numbers, references,
units and evidence still fail closed.

After a no-downtime worker replacement using the current worktree, the fresh
browser action completed child Turn
`fddca13a-9fde-4469-94b7-7c8c424ea7d2` with `COMPLETED` and
`grounding_status=VALID`, reusing Result snapshot
`c73dd037-07bd-447e-a049-a97e5426d371`. PostgreSQL deltas were:
`research_turns +1` (presentation-only child), `analysis_plans +0`,
`jobs +0`, `tool_calls +0`, `artifacts +0`, `scientific_result_snapshots +0`.
Focused interpretation regression is now `15 passed, 1 skipped`; the negative
unsupported-claim test remains green. This closes the demonstrated
re-interpretation zero-recompute seam, but does not close capability-wide
qualification or the remaining release gates.

### Current-worktree frontend regression after stale-response repair (2026-08-30)

The full frontend suite was rerun with Vitest temporary files redirected to
the workspace E: volume because the host C: temporary volume had only about
22 MB free and caused `ENOSPC` during the prior attempt. The fresh run
completed successfully: `98` test files and `670` tests passed. API,
frontend, PostgreSQL, Redis and MinIO listeners were rechecked and remained
available. This is current regression evidence only; capability-wide
qualification, recovery, retention/export, real-user acceptance and exact-SHA
Phase 14-R release gates remain open.

### Search stale-response guard (2026-08-30)

The global search surface now ignores late responses from superseded query or
filter requests and invalidates pending sequences when the dialog closes.
This is a small product-fluency repair with no authority change. The focused
ProductShell suite passed `9/9`; the authenticated same-stack browser search
continued to return bounded authorized exact routes.

Post-change backend authority regression is `45 passed / 4 historical
compatibility skips` across Report grounding, ContextManifest and project
authorization. PostgreSQL Alembic verification with
`DATABASE_URL=postgresql+psycopg://mdi@127.0.0.1:55434/mdi` reports
`0027_research_session_management (head)`; the default SQLite config was not
used as service evidence.

### Canonical Structure Presentation → Evidence → Viewer continuity (2026-08-30)

Turn `17b67e68-b7db-475b-bb4c-3b336cb2ba15` now has authenticated browser
proof for one non-duplicated Presentation, independent CrystalNN/VoronoiNN
content, two Evidence references, exact source version
`8859cb49-0766-48cd-8a56-e44f5332e0c5`, and an exact Viewer handoff to object
`dc3c3eee-f254-4edf-a0fa-c955402b3069`.

The Evidence inspector exposes source object and Artifact provenance; the
Viewer renders the Structure canvas and now offers a progressive `精确版本`
disclosure containing the full immutable version ID. The header remains
concise. The browser recorded no scientific mutation request while opening
Presentation, Evidence or Viewer, and the mobile Research route remained
`390/390` with zero overflow. Focused Viewer/Presentation regression is
`3 files / 6 tests`; typecheck and diff-check pass.

### App Router production navigation and mobile layout evidence (2026-08-30)

The reported full-page reload behavior was disproved with request and DOM
identity evidence. Authenticated navigation across Data, Research, Reports and
Overview produced `documentRequests=0`; a window marker and the exact global
shell DOM node survived every transition. The browser runtime now uses the
same-origin `/api` proxy. Bounded three-second Project History and Research
session promise caches coalesce navigation prewarm reads and invalidate after
related mutations.

The optimized Next build runs independently on port `3001`, leaving the
same-stack development service and authenticated browser tab available.
Production cold usable times were Data `59 ms`, Research `372 ms`, Reports
`356 ms`, Overview `43 ms`; warm usable times were `34/43/32/32 ms`.
There were zero repeated `/auth/me` reads and one persistent shell.

At `390x844`, authenticated Data, Research and Reports each had zero global
horizontal overflow; the scientific table, Research timeline, report filters
and report rows remained reachable, and Reports had no duplicate DOM IDs.
Focused frontend regression is `5 files / 85 tests`; frontend typecheck,
optimized production build and diff check pass. This closes the demonstrated
navigation defect but does not change the truthful overall Phase 14-R
`PARTIAL` verdict.
### Batch product quality: bulk lifecycle dependency preview (2026-08-30)

The Data Platform batch `移入回收站` action no longer bypasses dependency
impact protection. For every selected ScientificObject the browser now waits
for the server-derived dependency projection, aggregates the protected
scientific dependencies, and enables `确认移入回收站` only when the complete
selection has been resolved. Existing archive/restore bulk actions remain
reversible and do not create scientific versions.

Evidence: `ProductPages.test.tsx` `29 passed`; web typecheck `PASS`.
Authenticated same-stack browser selected `Phase13 Fresh Structure` and
`Si Structure Presentation`, opened the bounded bulk dialog, and displayed
five protected dependencies across versions, ScientificResult, ResearchTurn
and report. The dialog was cancelled, so no mutation was sent; browser
warnings/errors were empty and the existing authenticated tab stayed open.
This closes the R3 batch-safety seam only; Phase 14-R remains `PARTIAL` for
capability-wide qualification, retention/export, recovery and release CI.

### Batch Dataset lifecycle dependency preview (2026-08-30)

Dataset batch Trash now uses a server-derived dependency-impact preview before
mutation. The bounded dialog summarizes protected dependencies for the full
selection, blocks confirmation on incomplete/failed previews, and only closes
after the existing batch API succeeds. `ProductPages.test.tsx` passed `30/30`;
the four-file focused frontend run passed `47/47`; web typecheck passed. No
browser mutation was issued during the authenticated preview proof. This is a
targeted R3 safety improvement; no overall Phase 14-R completion claim is made.

The follow-up failure regression keeps the Dataset preview open when the
existing batch endpoint rejects (`ProductPages.test.tsx` `31/31`). This closes
the false-success UI seam while preserving the truthful overall `PARTIAL`
status and leaving services/browser tabs running.

### Same-stack search and task-center browser evidence (2026-08-30)

The preserved authenticated browser tab opened global search from Data and
received 40 bounded authorized results with exact routes across research,
Dataset, ScientificObject, ScientificResult and Report entities. The same
tab transitioned client-side to `/tasks` without closing the session; the
persisted task center showed resumable and historical rows, explicit Turn
links, stale-state notices and no browser errors. This is additional R7/R8
evidence, not a completion claim for the still-open recovery, performance and
release gates.
### Result reuse service-backed qualification (2026-08-30)

The Phase 7 fresh-process campaign was rerun with `MDI_RUN_INTEGRATION=1`,
PostgreSQL `127.0.0.1:55434`, Redis DB 13 and MinIO `mdi-artifacts`; it
executed rather than skipping. The campaign passed `4/4` tests and emitted
`selected_skip=0`. It proved RDF and XRD reuse, continuation execution,
stale exact-version follow-up, and isolated worker processes. The continuation
retained exact prior Turn `da385a5d-5dd2-4cdb-ad48-4fea852d59b4` and produced
Result snapshot `17fcaa94-92b8-4157-9c87-dcdb2d1d21f2`; stale follow-up
preserved exact source version `4c728fdc-4341-4dbc-aba6-85335685d2f5` while
current version was `ed38a49a-9bd0-440d-8100-7c058dc23b1e`. The reuse
assertion reported `no_recompute=true`, with `Job/ToolCall/Artifact/
ScientificResult` unchanged for the reuse branch.

### Research continuity and loading-shell repair (2026-08-30)

Fresh exact Structure handoff evidence identified and repaired a real product
continuity defect: implicit `items[0]` session selection could reopen an
archived Research session. Exact object/version and Dataset handoffs now use
a clean route; `?new=1` is an explicit fresh route; historical `sessionId`
routes remain authoritative. Archived sessions expose `开始新的研究` and
`恢复原会话` without changing historical messages or source versions.

The authenticated browser reached the new Research composer in `593 ms`,
preserved the exact handoff parameters, and measured `507/507` effective
viewport width. The archived-session action navigated to
`/projects/project_0002_1a0af866391f412d/research?new=1` and did not select
archived history. Overview, Data, Research and Reports now share a
workbench-preserving App Router loading skeleton. Focused route/research
coverage is `49/49` for this batch, full frontend is `99 files / 675 tests`,
typecheck is `PASS`, and touched diff validation is `PASS`.

This is a bounded R3/R4/R6 continuity improvement. It does not close the
remaining capability-wide qualification, cancellation/recovery stress,
retention/export, operations, real-user or P14R exact-SHA release gates;
the truthful Phase 14-R status remains `PARTIAL`.

### Grounded communication and report authority browser closure (2026-08-30)

The current-worktree API now applies one deterministic communication boundary
to both newly generated and historically reopened scientific output:

* a persisted Interpretation remains immutable audit evidence;
* user-facing scientific findings remove exact internal fact/evidence ID
  echoes and redundant wording without changing references or values;
* the visible lead is reconstructed only from already-grounded Findings;
* a Report provider response is schema/grounding validated and then projected
  back to the validated Interpretation plus exact ScientificResult authority;
* Report summary, findings, discussion, conclusion, methods, limitations,
  sources, evidence and reproducibility metadata therefore cannot introduce
  a second scientific authority.

Authenticated same-stack browser evidence used:

```text
Project = project_0002_1a0af866391f412d
parent ResearchTurn = 1c57db79-7a3b-4f20-bd9a-f883cf29d54b
re-interpret ResearchTurn = 7c65deb0-5791-4340-b6e6-ead5a8733445
ScientificResultSnapshot = 14ce2fd1-e5bc-4798-906f-3333df2f7a91
Interpretation = 6005f096-19d9-4a35-9e22-0d79e47e8a63
Report = agent2_report_4f8320601e99ec9e3a78597f9973aa4c
ScientificObject = dc3c3eee-f254-4edf-a0fa-c955402b3069
ScientificObjectVersion = 8859cb49-0766-48cd-8a56-e44f5332e0c5
```

The Research page exposed `理解问题`, `解释结果`, and `整理报告` in the
Used Context disclosure, with the exact version and Result IDs above,
`无需压缩`, and `关键上下文完整`. The historical and re-interpreted visible
findings contained no internal fact IDs; the re-interpreted finding read
`成功识别出 1 个配位位点`, while the grounding validator remained
fail-closed.

The Report opened through the normal App Router link and displayed:

```text
title = CrystalNN 与 VoronoiNN 局部配位环境比较
exact source count = 1
exact source version = 8859cb49-0766-48cd-8a56-e44f5332e0c5
independent findings = 2
method summaries = CrystalNN + VoronoiNN
limitation = ScientificResult 未提供额外方法限制；报告不补充未来源的算法常识。
unsupported “有效且可靠” conclusion = absent
browser console errors/warnings = 0
```

The runtime reported PostgreSQL, Redis, MinIO, Redis workers and configured
DeepSeek all healthy. Focused evidence after the repair is:

```text
interpretation/report backend = 46 passed, 5 historical live skips
API/history/Viewer backend = 33 passed
Report/Research/Presentation frontend = 65 passed
touched Ruff = PASS
git diff --check = PASS
```

This closes the current grounded communication/report-quality seam. It does
not close capability-wide Viewer acceptance, running cancellation/recovery,
retention/export, R12 real-user acceptance, full regression or P14R-A/P14R-B;
the Phase 14-R verdict remains `PARTIAL`.

### Current-worktree scientific-surface same-stack batch (2026-08-30)

After restoring the long-running services, `/health/runtime` reported the
actual PostgreSQL, Redis, MinIO, Redis-worker and configured DeepSeek topology.
Direct PostgreSQL, Redis `PING`, MinIO live-health, API and both frontend
checks also passed.

The grouped mandatory integration campaign used PostgreSQL
`127.0.0.1:55434/mdi`, Redis DB 13 and MinIO `mdi-artifacts` with the
integration gate enabled. It executed rather than skipping:

```text
Agent2 Phase 4/5 + Coordination + XRD = 5 passed
Agent2 Phase 6/8 + professional closure = 7 passed
selected = 12
passed = 12
failed = 0
errors = 0
skipped = 0
```

Focused frontend scientific-surface evidence passed:

```text
Viewer/Evidence exact-product run = 10/10
Dataset/Coordination/XRD/registry run = 38/38
```

The authoritative surface matrix now records Dataset, CrystalNN, VoronoiNN,
theoretical XRD and experimental/theoretical XRD comparison as `PASS` for
their exercised current-worktree paths. RDF advances to `PARTIAL` because its
real same-stack Result and reuse authority exist but its authenticated
scientific-content browser path is still open. Renderer-only families remain
`NOT_QUALIFIED`; this batch therefore does not overstate the overall Phase
14-R verdict.

### Authenticated queued/running cancellation and Continue recovery (2026-08-30)

The current-worktree browser and PostgreSQL evidence closes the R4
queued/running control gap:

```text
queued Turn = 76e51edf-f798-4771-930a-2011027ade96
queued Job = job_agent2_76e51edff7984771930a2011027ade96
queued final = CANCELED / cancelled

running Turn = e2789fe7-9322-4e0d-b43b-23981408e70c
running Job = job_agent2_e2789fe793224e0db43b23981408e70c
running final = CANCELED / cancelled

each case ToolCall/Artifact/ScientificResult = 0/0/0
```

Fast-race Turn `77129519-3449-4ae8-887a-beb88a23459d` correctly remained
`COMPLETED`, demonstrating that a late cancellation request cannot overwrite
durable success.

The terminal UI now separates `继续研究`, `修改问题`, and
`重新研究（新运行）`. The authenticated `继续研究` action focused the
existing composer and displayed a no-automatic-recompute explanation. Before
and after the click, the canceled session retained one Turn, the same canceled
Job and zero ToolCalls/Artifacts/Results. Browser warnings/errors were zero.
Focused frontend coverage passed `2 files / 61 tests`.

This closes the queued/running cancellation and non-executing Continue seam.
Phase 14-R remains `PARTIAL` for the remaining scientific surface, lifecycle/
retention/export, context-stress, operations, R12, full regression and
exact-SHA release gates.
## Current batch — persistent navigation and canonical RDF (2026-08-30)

### Product-shell navigation

The main product routes now preserve one root ProductShell through Next App
Router transitions. Login return navigation no longer performs
`window.location.assign`, and the global Task/Notification surfaces reuse one
bounded, short-lived task feed. The authenticated browser proved:

```text
Project → Tasks = 504 ms, 0 document requests
Notifications → Tasks history = 54 ms, 0 document requests
Tasks → Project history = 26 ms, 0 document requests
global shell DOM identity retained = YES
shared feed duplicate project/job API requests = 0
```

The only slower measured transition was the first
Tasks → Notifications development route compilation at `2550 ms`; it still
used one RSC request and no document reload. Focused frontend checks pass
`7 files / 52 tests`, plus typecheck and diff-check.

### Canonical RDF scientific presentation

The RDF projector now emits the complete bounded fact set required by its
authoritative Artifact: structure count, bin count, maximum radius, bin width
and number density. A narrow grounding normalization recognizes equivalent
inverse-cubic angstrom notation while preserving rejection of different units
and unsupported peak claims.

Fresh same-stack evidence:

```text
ScientificObject = dc3c3eee-f254-4edf-a0fa-c955402b3069
ScientificObjectVersion = 8859cb49-0766-48cd-8a56-e44f5332e0c5
ResearchTurn = 54fdeada-af1e-4e65-8a8a-855fb52ae76c
Plan = plan_a615abc9895649ab9b812912
Job = job_agent2_54fdeadaaf1e4e658a8a855fb52ae76c
ScientificResultSnapshot = a65dfde6-47f5-42fc-972c-66da77a27aa2
ScientificResult = 51baaff9-59ea-5a2e-8cad-931bbbd8586d
Interpretation = 87680594-fe78-46d6-8816-3e8a33993b09
grounding_status = VALID
Turn = COMPLETED
```

The Result contains five facts:

```text
rdf.structure_count = 1 count
rdf.bin_count = 80 count
rdf.r_max = 8.0 angstrom
rdf.bin_width = 0.1 angstrom
rdf.number_density = 0.037037 angstrom^-3
```

The authenticated browser rendered the grounded summary, all five metric
blocks, persisted RDF Figure and Table actions, the exact-version Viewer,
two Evidence references and the explicit limitation that peaks and
coordination shells are not inferred. Focused backend coverage is
`39 passed, 1 historical skip`; touched Ruff and diff-check pass.

This closes the canonical RDF desktop scientific-content path. Phase 14-R
remains `PARTIAL`: other declared capability families, mobile/historical RDF,
retention/export, context stress, R12, full regression and P14R-A/P14R-B are
still open.

## 2026-08-31 — Report grounding and framework navigation batch

Fresh Phonon Band + DOS Turn `4fbfcc49-db9f-4fb8-af29-9ee11e39fc8b` remained
`COMPLETED`, with Result `405ee6b6-9cb8-4ebc-bc8a-7d7332feb46b` and
Interpretation `f6b8a955-4fc3-4139-903f-2f3f3362bcb3` (`VALID`). Report
generation initially rejected the equivalent `terahertz`/`THz` unit spelling;
the bounded validator alias now passes this pair while unrelated `eV` remains
rejected.

Generation `fc93b717-b386-5c03-9c0a-a06d5da2023b` was retried by the real
Report worker and reached `READY`, producing
`agent2_report_a015ca23c3a9bceee669c9725da408a1`. Browser output now shows
the joined title `声子能带与态密度分析结果`, fact-backed discussion, three
figures, nine evidence refs and two exact source versions. Retry caused no
scientific recomputation: `Job/ToolCall/Artifact/ScientificResult` remained
`245/322/1291/170`; only Report snapshots changed `30 → 31`.

The Report read model now returns `research_session_id`, so source navigation
opens the exact session/Turn route. ProductLink preserves native Next App
Router navigation; command-style Research actions use the same pending
feedback. Focused backend coverage is `30 passed / 4 historical skips`;
focused frontend coverage is `85/85`; Ruff and typecheck pass. Phase 14-R
remains `PARTIAL`; capability-wide qualification, context stress,
retention/export, R12, full regression and P14R-A/P14R-B remain open.

## 2026-08-31 — Current-worktree regression and read-only surface verification

The current-worktree frontend regression completed with `101 files / 693 tests
passed`. The focused backend report/viewer/context batch completed with
`47 passed / 4 historical compatibility skips`; touched Ruff, `uv lock
--check`, compileall, typecheck and `git diff --check` passed. An isolated
Next production build completed successfully for all `17` routes; the
temporary generated TypeScript include was removed after the build so
`apps/web/tsconfig.json` retains no build-specific path.

The authenticated same-stack browser tab remains open on the exact Phonon
Viewer route. The Viewer rendered the persisted band/DOS content and exact
source navigation without a document reload. At the verification point,
`document.documentElement.clientWidth == document.documentElement.scrollWidth`
and `document.body.scrollWidth` matched the viewport, so no global desktop
overflow was present. Persisted scientific counts remained unchanged across
Report → Research → Viewer navigation:
`Job/ToolCall/Artifact/ScientificResult = 245/322/1291/170`.

The service-backed runtime continues to report PostgreSQL, Redis, MinIO,
Redis-backed workers and configured DeepSeek as healthy. A same-stack
operations snapshot reported `workerCount=6`, zero queued jobs, zero
idle-in-transaction connections and zero recent queue failures, but retained
historical stale ResearchTurn/Job records (`staleActiveResearchTurns=13`,
`staleJobs=1`); this is recorded as an operations attention item rather than
silently treating the snapshot as a clean maturity PASS. The overall
Phase 14-R verdict remains `PARTIAL`.

The current PostgreSQL/Redis/MinIO mandatory service selection also executed
`21/21` tests across Agent2 Phase 2–8, Coordination, local environment,
experimental XRD, trajectory analytics, electronic structure and professional
closure. It recorded `failed=0`, `errors=0`, `skipped=0`. Full backend
regression is `1892 passed / 83 historical or optional skips`; no mandatory
Phase 14-R service case in the selected campaign was hidden behind a skip.

An authenticated browser reread then exposed one presentation-only quality
defect in the persisted Phonon report: fallback discussion sentences were
joined as `。；`. The deterministic composer now joins complete sentences
without duplicate punctuation, and the frontend reader normalizes the same
legacy pattern for already-persisted snapshots. Backend Report tests pass
`30/30` with `4` historical skips; the Report route passes `14/14`. The live
report now reads as three clean semicolon-separated verified findings without
rerunning any science.

## Current Project-state and navigation evidence — 2026-08-31

The Project Overview now projects the persisted ResearchTurn terminal state
instead of allowing a stale compatibility Job state to say that failed work
is still running. The exact historical route remains
`/projects/{project}/research/{session}?run={job}&turn={turn}`.

Authenticated evidence:

```text
Turn = ec298988-0b32-4e5e-a3c0-8bbb22725818
Job = job_agent2_ec2989880b324e5ea3c08bbb22725818
visible status = 分析失败
exact session/run/Turn route = PASS
```

The App Router navigation campaign recorded zero document requests and
preserved one ProductShell DOM identity across Overview, Data, Research and
Reports. Warm URL response was 95–115 ms. The full desktop/mobile matrix
recorded zero horizontal overflow, zero browser errors and zero critical
responses; mobile Data and Report p95 were 948 ms and 903 ms, while mobile
Research p95 was 2,178 ms.

Focused frontend status/navigation coverage is `38 passed`; typecheck and
diff-check pass. These results close this bounded UI/navigation batch but do
not close capability-wide Viewer, context stress, retention/export, R12,
full regression or P14R-A/P14R-B.

## 2026-08-31 — Phonon/Electronic presentation readability and Viewer batch

Same-stack authenticated browser evidence:

```text
Phonon ResultSnapshot = 405ee6b6-9cb8-4ebc-bc8a-7d7332feb46b
Phonon ScientificResult = 980afdc5-5f6b-5023-923a-974b9961bdd0
Phonon Interpretation = f6b8a955-4fc3-4139-903f-2f3f3362bcb3 (VALID)
Phonon Report = agent2_report_a015ca23c3a9bceee669c9725da408a1
```

The Report route now reuses the deterministic Research limitation mapping.
The Report visibly contains a concise summary, fact-backed discussion,
three persisted figures, two exact-version Viewer links, nine evidence refs
and two exact source versions. The Phonon Band Viewer renders six branches
across three q-points with the authoritative `0–5 THz` range. Electronic Band
and DOS exact-version Viewers render their real typed tables, eV/state-density
units and explicit unavailable/partial boundaries. At 390x844 all tested
Viewer routes measured zero global overflow and browser logs contained no
errors or unhandled rejections.

The legacy Research timeline no longer renders a complete machine-readable
`ASSISTANT_FINAL` as one oversized paragraph. A bounded display projection
retains the first two grounded sentences and directs users to the structured
Workbench for full Findings/Evidence/Limitations; the stored message and
scientific authority are unchanged. Focused frontend tests passed
`ResearchPages 54/54`, Report/Presentation `31/31`. PostgreSQL counts before
and after read-only Report → Research → Viewer navigation remained
`258/339/1359/181/33` for Jobs/ToolCalls/Artifacts/ResultSnapshots/Reports.
Overall Phase 14-R remains `PARTIAL`; capability-wide, retention/export,
context-stress, R12 and release gates remain open.

## 2026-08-31 — Report Figure provenance, export and trajectory RDF batch

The Electronic report `agent2_report_e7fa88beeb9a92cd8d46e44182ec46f9` was
reloaded against the current API and now binds its Band Figure to exact
version `7f7f1008-4d67-4592-a501-41d9a7d9a5cc` and its DOS Figure to exact
version `087f93c4-2a5b-4c1e-b4e4-916c368801d0`. The backend projection derives
these bindings from the immutable Result figure type; the frontend Report
compiler uses them for Figure/Viewer links. Markdown and reproducibility
manifest exports now retain the Figure object/version binding alongside
Artifact IDs.

The authenticated same-stack browser generated and opened trajectory RDF
Report `agent2_report_55692c117165c20c3da272ef75e28118` from
ResearchTurn `321db606-efeb-41af-9333-3709fa07e9ee`. It retained exact
trajectory version `052d3a8e-8a35-48ac-9e65-b95a86b42c99`, displayed five
bounded findings, a persisted RDF Figure, two evidence refs and the exact
trajectory Viewer; mobile overflow was `0`.

The shared ProductShell now coalesces repeated project-history,
research-session and task-feed prefetch reads. The live navigation campaign
still records `documentRequests=0`, one RSC request per route,
`shellCount=1`, and warm route usability in the sub-second to ~1 second
range for common Data/Report paths. Focused frontend batch is `41 passed`;
backend Report coverage is `32 passed / 4 historical compatibility skips`.
Phase 14-R remains `PARTIAL`; MSD/Diffusion, composition/ML, lifecycle,
context-stress, operations and exact-SHA release gates remain open.

## 2026-08-31 — Trajectory MSD real-source product qualification

Exact same-stack identities:

```text
Dataset = dataset_0001_b7f22cb1bb074f1a
Profile = profile_dataset_0001_b7f22cb1bb074f1a_v2
Source object = obj_trajectory_990aa1224948
Source SHA-256 = 3424c71e0df3137e72529a868b8596769017f18dc3a6e5696e8a28855a138649
Plan = plan_72e81c4f236b4510b8d23450
Job = job_f2b56ba7d4a34c9288600852
Interpretation = interpretation_fed32da21ee465e9e18d19048d559e93
Grounding = VALID
```

The repository-owned explicit-unwrapped EXTXYZ source used the normal
upload-session, MinIO, parser and Profile path. The completed Job persisted
table, Plotly, summary and recipe artifacts. The product displayed three
authoritative lag rows and final MSD `0.0009 Å² @ 0.003 ps`; the limitation
truthfully states that the short run does not estimate a diffusion
coefficient.

The authenticated Data surface initially exposed two independent projection
defects. The API serialized the normalized trajectory wrapper instead of its
canonical payload, so the Viewer rejected the schema. The Research
presentation also appended an RDF frame-count sentence to MSD-only output and
rendered `NaN`. The API now unwraps only the dataclass payload at the read
boundary, and the UI includes RDF coverage only when the authoritative fact
exists. No scientific authority, worker contract or grounding rule changed.

The trajectory Viewer renders four real frames with unwrapped position,
time/lattice, playback, selection/measurement and supercell controls. The
Report route shows the exact prompt, three-row table, `0.0009 Å²` finding,
source checksum/contract and no-diffusion limitation. Report → Research →
Report reopening kept persisted
Jobs/ToolCalls/Artifacts/Interpretations/Reports at
`261/341/1363/17/36`.

Verification:

```text
capability planner = 64 passed
trajectory parser = 24 passed
backend object-store/parser = 27 passed
frontend Research + Trajectory Viewer = 70 passed
typecheck = PASS
diff check = PASS
```

This upgrades `trajectory.msd` from `NOT_QUALIFIED` to `PARTIAL`. The
legacy planner path did not create an Agent2 ResearchTurn or
ScientificResultSnapshot, and mobile/historical MSD evidence remains open.
`trajectory.diffusion` remains `NOT_QUALIFIED`. Phase 14-R and P14R-A/P14R-B
remain open.

# Agent-2.0 Phase 14-R — 2026-08-31 Report language and mobile action-bar batch

状态：已完成（呈现层批次；总体仍为 PARTIAL）

修改摘要：
- Scientific Report 与 Scientific Presentation 的残留英文产品标签统一为中文：
  `科学呈现`、`精确源版本`、`精确版本`、`查看器`、`材料数据表`；技术 ID、
  契约版本、Result/Artifact 绑定保持原样。
- Report 的已持久化复现摘要在展示层将 `exact source version(s)` 归一为
  `精确源版本`，并按受控白名单映射 `materials.table` 等对象类型。
- Report 顶部返回、来源研究、Markdown 与复现清单操作允许窄屏换行，保持
  单一科学文档阅读流，不改变 App Router 或报告快照。

验证：
- ScientificReportRoute / ScientificPresentation / scientific-presentation
  focused tests：`37 passed`。
- `npm run typecheck`：PASS。
- Report `agent2_report_9b6943b7b3a9eaecd594ecf9bde7e806` 继续绑定
  ResearchTurn `fbbb0c51-4f39-4c97-ad7a-69ee089884a2`、ScientificResult
  snapshot `d984bb18-acc6-4d55-90e1-2097b0305a69`、Interpretation
  `432e6775-7590-4fc4-906e-e535c23809e8`，grounding `VALID`。
- Report 打开前后 PostgreSQL 计数保持
  `jobs/tool_calls/artifacts/results = 278/365/1450/184`，无科学重算。

提交/CI 状态：未提交；P14R-A/P14R-B 仍等待 Phase 14-R 强制门全部闭合。

# Agent-2.0 Phase 14-R — 2026-08-31 exact Result reuse browser batch

状态：已完成（零重算复用批次；总体仍为 PARTIAL）

同栈认证浏览器从 Report 的“打开来源研究”进入精确 Dataset ResearchTurn，
使用现有“重新解释（不重算科学结果）”控制创建：

```text
parent Turn = fbbb0c51-4f39-4c97-ad7a-69ee089884a2
child Turn = 219e8d7f-1c62-4566-a05b-e9563efce407
child status = COMPLETED
child action_type = INTERPRET_RESULT
parent_turn_id = fbbb0c51-4f39-4c97-ad7a-69ee089884a2
```

PostgreSQL persisted delta：

```text
Interpretations: 188 → 189
Jobs:             278 → 278
ToolCalls:        365 → 365
Artifacts:        1450 → 1450
ScientificResults:184 → 184
```

新解释仍绑定原 Dataset 精确对象/版本与 `sample-fe2o3` 事实；浏览器页面展示
科学呈现、Finding、Evidence 与结果入口，没有新建科学执行链。该证据关闭了
当前桌面 Result reuse / reinterpret 零重算路径；移动端、跨能力复用和完整
历史/归档复用矩阵仍保持 PARTIAL，未提前宣称整体成熟度完成。

390×844 同一子 Turn 页面也保持 `bodyWidth=390`、`documentWidth=390`，
并可达“继续研究 / 编辑问题 / 重新解释 / 重新研究 / 固定到研究上下文”五个
控制；本次仅做只读布局与控制可达性核验，未重复触发科学执行。

同一认证浏览器继续验证 Global Search：从研究页打开“全局搜索”，输入
`mat-2` 后当前 API 返回 `7` 项授权结果（研究会话、科学报告及项目内数据），
结果均保留精确实体入口；未出现跨项目记录、原始凭据或内部基础设施信息。

# Agent-2.0 Phase 14-R — 2026-08-31 same-stack service availability recheck

状态：已完成（运行时连续性批次；总体仍为 PARTIAL）

用户要求重新打开本地服务后，未关闭现有认证浏览器标签页，也未停止仍在工作的
进程。`2026-08-31T21:44:41+08:00` 读到 frontend `3000`、API
`8000/8002`、PostgreSQL `55434`、Redis `6379`、MinIO `9000/9001` 监听；
`GET http://127.0.0.1:8002/health/runtime` 返回 `200`，真实报告：

```text
database.backend = postgresql
redis.backend = redis
artifactStorage.backend = minio
artifactStorage.bucket = mdi-artifacts
worker.backend = redis
llmProvider.configured = true
```

认证浏览器 tab `15` 保持打开；Report → Data 的项目内导航完成 URL 与内容
切换，没有回到登录恢复态，也没有残留导航进度。该记录只证明同栈服务可用与
路由连续性，不提前把仍未完成的成熟产品矩阵宣称为 PASS。

补充 UI 检查：当前报告/数据项目壳在浏览器视口 `1205×880` 下
`documentWidth=1190`、`overflow=0`，重复 `id` 数量为 `0`；这支持当前桌面
项目导航与无障碍关系没有出现新的布局或 ID 回归。

同批回归重新执行：Phase 14-R 重点后端
`65 passed / 4 historical compatibility skips`；前端
RouteTransition/ProductShell/ProductPages/Research/Presentation/Report
控制与生命周期集合 `127 passed`。服务健康探针仍为真实
PostgreSQL/Redis/MinIO，未改变运行时或关闭浏览器。

认证浏览器继续完成 Task/Notification 连续导航：项目页 → `/tasks` 载入
“任务中心”（持久化任务概览显示 `48` 条记录、`0` 进行中、`10` 需关注），
再由全局栏进入 `/notifications`，标题“通知中心”可见；两次切换均未触发
登录恢复态或错误页。此次补强了后台任务/通知的真实产品入口证据，但完整
网络中断、worker 重启恢复与 push 通知仍保持 PARTIAL。
# Agent-2.0 Phase 14-R — 2026-08-31 archive/restore browser and navigation fluency batch

状态：已完成（真实认证 UI 归档/恢复与应用内导航批次；总体仍为 PARTIAL）

同栈认证浏览器 tab `15` 在 Data Platform 使用真实产品操作验证了科研对象
`55648f55-51e4-4c94-b4fe-72cae944a54c`（`Phase14R Phonon Band`）：

```text
ACTIVE 当前列表
→ 管理 Phase14R Phonon Band
→ 归档科研对象
→ 已归档列表可见，状态 = 已归档
→ 管理菜单出现 恢复科研对象
→ 恢复科研对象
→ 当前列表重新可见，状态 = ACTIVE
```

归档前后对象链接始终指向同一精确版本：
`53037b6a-7a68-43ac-85de-6e920dfd4420`。恢复后的对象详情页显示
`版本 1`，精确版本入口、Phonon band 内容、频率单位 `THz` 和已知限制均可读；
本次没有直接 API/数据库替代浏览器操作，也没有新建科学版本。

本批补强应用内导航体验：`ProductLink` 对同源产品路由默认启用 Next
预取，同时保留现有持久化 ProductShell 与过渡进度条。认证浏览器从 Data
通过项目导航进入 Research，约 `2234 ms` 完成首屏；页面无“正在恢复登录状态”
或“正在切换工作区”残留，URL 为
`/projects/project_0002_1a0af866391f412d/research`。对应前端
`RouteTransitionProgress/ProductShell/ProductPages` 回归仍为 `46 passed`，
typecheck 通过。该批改善了产品内导航反馈与缓存预取，但尚未把整个
Phase 14-R 的 capability-wide、恢复、保留/导出和 release seal 门宣称为 PASS。

补充回归：当前工作树全前端 `102 test files / 718 passed`；本批涉及的
`ProductPages`、`ScientificReportsIndexPage`、`RouteTransitionProgress` 为
`45 passed`，并清理了 Next `prefetch` 测试替身的非布尔属性噪声。后端
Phase 14-R 集合保持 `65 passed / 4 historical compatibility skips`，
`compileall`、`uv lock --check`、`git diff --check` 与 typecheck 均通过。
以独立目录 `.next-prod-phase14r-batch` 完成生产构建，Next 产物含
`17` 个路由，构建 PASS；构建自动将该目录的类型声明加入 `tsconfig`，
沿用现有独立构建目录策略，未停止当前开发服务。
另外，项目壳在进入项目后会在短暂空闲窗口预热受授权的 Research session
inventory，与 history ledger 共用现有 30 秒 TTL；这使 Data → Research
不必等到路由提交后才发起第二轮会话列表请求，且所有会话生命周期 mutation
仍会触发既有失效逻辑。
在同一认证浏览器等待预热后复测 Data → Research，转换约 `1314 ms` 完成，
页面宽度保持 `1205/1205`、无登录恢复态和切换残留；这是温启动体验改善，
不是把科学执行耗时伪装成导航耗时。

本批最终后端全量回归为 `1916 passed / 84 skipped / 168 warnings`
（`279.60s`）。skip 仍是既有服务/兼容性分类；本批强制 Phase 14-R focused
测试实际执行且未跳过。前端全量为 `718 passed`，生产构建、typecheck、
compileall、lock 与 diff check 均通过。

## 2026-08-31 composition-space / regression Viewer, Evidence and Report batch

The authenticated same-stack browser qualified the exact completed scientific
lineage:

```text
ResearchTurn = fbbb0c51-4f39-4c97-ad7a-69ee089884a2
Job = job_agent2_fbbb0c514f394c97ad7a69ee089884a2
ScientificResultSnapshot = d984bb18-acc6-4d55-90e1-2097b0305a69
ScientificResult = f9f4fb16-edbe-53bc-9516-ebd3d7ba5b0a
Interpretation = 432e6775-7590-4fc4-906e-e535c23809e8
Report = agent2_report_9b6943b7b3a9eaecd594ecf9bde7e806
Dataset version = cf2aeeea-53ad-452a-a4ef-7b61555004e5
grounding = VALID
```

The Research Workbench rendered the persisted composition-space Figure/Table,
the persisted regression diagnostic Table, six grounded findings, ten
authoritative metrics, stable sample identity `sample-fe2o3`, two Evidence
references and the exact Dataset Viewer link. Evidence inspection resolved the
completed `dataset.composition_space` ToolCall and Artifact checksum
`32adca799412da69b2fbf2204f635bdd4b52c801673a933ecec0fc9dacef5ea2`.

The corresponding Report rendered the research question, exact source,
methods, discussion, findings, limitations, conclusion, next steps and bounded
Markdown/reproducibility export actions. At `390x844`, both Report and Research
had zero global overflow; the mobile Workbench displayed the regression Table
and `sample-fe2o3`. Browser warnings/errors and duplicate IDs were zero.

Opening Figure, Tables, Evidence, Report and source Research kept persisted
`Jobs/ToolCalls/Artifacts/ScientificResults/Reports` at
`278/365/1450/184/36`; `idle-in-transaction=0`. Focused frontend
presentation/report/ML tests passed `34/34`. This upgrades the exercised
`data.composition_space` and `ml.regression_evaluation` paths to `PASS`.
Phase 14-R overall remains `PARTIAL` because other capability, retention,
context-stress, operations, R12 and P14R-A/P14R-B gates remain open.

## 2026-08-31 coordination-histogram Viewer/Evidence/Report batch

The same authenticated browser qualified:

```text
ResearchTurn = 63d21ee3-6e18-49b3-ad6b-b3fb578563c5
Job = job_agent2_63d21ee36e1849b3ad6bb3fb578563c5
ScientificResultSnapshot = 2382b0eb-b056-42b2-b6a7-d2e8a4ca398c
Interpretation = ee6b7667-d217-4a1e-82f9-b4be9152a93c
Structure version = 8859cb49-0766-48cd-8a56-e44f5332e0c5
Report = agent2_report_19a0d0c261c28577101de81532464893
Report snapshot = c8cc6fcb-1f0b-50c6-b6db-049374f7de6e
grounding = VALID
```

The Workbench displayed the real persisted coordination Figure and Table:
one Si site, coordination number 6, `3 Å` fixed-distance cutoff and the
fixed-cutoff scientific limitation. Evidence inspection resolved completed
ToolCall `structure.coordination_hist`, the exact Structure version and
Plotly checksum
`0a595462eddb86b474ef9aba7ca17d78abc6d388c85fd67a8f55cf67aaeaeb0d`.

The normal “生成报告” product action created only one Report snapshot. Persisted
counts changed from `278/365/1450/184/36` to
`278/365/1450/184/37`; therefore Job, ToolCall, Artifact and ScientificResult
deltas were all zero. The resulting Report contains the exact source, method,
Figure, findings, limitation, conclusion and next steps. At `390x844` it had
zero overflow, duplicate IDs, browser warnings and errors. Focused frontend
coordination/presentation/report tests passed `29/29`.

This upgrades `structure.coordination_hist` to `PASS`. Broader Phase 14-R
maturity and release gates remain open.

## 2026-08-31 trajectory diffusion Presentation / Viewer / Evidence / Report batch

The authenticated same-stack product path closed the current-version
trajectory-diffusion communication loop with these exact identities:

```text
ResearchTurn = fb72c2ad-bed1-47d7-b557-f398f04a8ede
ContextSnapshot = 67318562-ad12-4623-bbe2-210d751f6ad2
Plan = plan_9a34470b87c6461480b254f0
Job = job_agent2_fb72c2adbed147d7b557f398f04a8ede
ScientificResultSnapshot = 26127c48-d736-4983-b035-b68db238f6a7
Interpretation = 4d1f2f06-ac66-4878-9ee5-bf79c53b3229
Report = agent2_report_e54681009a0e49abe371247d9053ce61
Report snapshot = d541785b-63d9-5e62-8f48-0e7d92420c47
ScientificObjectVersion = a22745f2-17b6-434f-ba4c-3fe6bd244841
grounding = VALID
```

The Workbench rendered ten authoritative diffusion/MSD facts, including
`D=0.038618084156 Å²/ps`, the exact `1–6 ps` fit window, 11 fit points,
`R²=0.970301847945` and `RMSE=0.064094868867 Å²`. Evidence inspection
traversed the exact source version, completed `trajectory.diffusion`
ToolCall, persisted Artifact and checksum. The trajectory Viewer rendered
24 real frames and advanced from frame 1 to frame 2 through the product
control.

The first Report composition attempt exposed a real deterministic defect:
Report grounding split `Å²/ps`, treated the unit exponent as a numeric claim,
and ignored persisted Evidence/ResultItem support edges. The validator now
normalizes composite units without conversion, removes recognized units before
numeric tokenization, and follows only authoritative fact/evidence/result-item/
interpretation support edges. It remains fail-closed: the new regression
accepts the real `1–6 ps` diffusion claims but rejects a forged `1–8 ps`
window and an unsupported `m²/s` unit.

After rolling only the Report worker, the same generation became `READY`.
The Report contains question, methods, two persisted figures, three findings,
discussion, limitations, conclusion, next steps, exact source and Evidence
links. Report and Research both measured zero global overflow at `390x844`;
the mobile Evidence chain remained reachable.

Read-only Presentation, Evidence, Viewer and Report operations preserved
project counts at:

```text
Jobs / ToolCalls / Artifacts / ScientificResults = 42 / 57 / 214 / 28
```

No scientific recomputation occurred. The duplicate legacy
`分析完成 · 0 个步骤` summary is also suppressed whenever the authoritative
Agent2 progress projection is present, leaving one truthful 2/2 progress
region.

Regression evidence:

```text
Result / Interpretation / Report backend = 79 passed, 5 historical skips
Phase 8 Report service-backed = 4 passed, 0 skipped
Research / Presentation / Report frontend = 96 passed
touched Ruff = PASS
git diff --check = PASS
runtime = PostgreSQL + Redis + MinIO + 6 idle workers
idle-in-transaction = 0
queued = 0
recent failed queue items = 0
```

This closes the current exact diffusion Presentation/Viewer/Evidence/Report
path. Capability-wide historical/archive, remaining lifecycle/retention,
context stress, R12 and P14R-A/P14R-B gates remain open, so the overall Phase
14-R verdict remains `PARTIAL`.

## 2026-08-31 archived diffusion Report / Evidence / Viewer continuity

The same authenticated PostgreSQL/Redis/MinIO stack exercised the normal Data
Platform lifecycle for ScientificObject
`f834e358-9944-4fe8-a3ab-f85d68041f54`.

Before archive and after restore:

```text
ScientificObjectVersion = a22745f2-17b6-434f-ba4c-3fe6bd244841
version count = 1
current_version_id = a22745f2-17b6-434f-ba4c-3fe6bd244841
```

While `ARCHIVED`, Report
`agent2_report_e54681009a0e49abe371247d9053ce61` remained readable and now
rendered the bounded source disclosure:

```text
trajectory.atomic
· 版本 a22745f2-17b6-434f-ba4c-3fe6bd244841
· 当前版本
· 来源对象已归档
```

This repairs a communication gap without changing data authority. The Report
viewer-source projection derives lifecycle from the authoritative
ScientificObject row and carries it into the UI, Markdown export and
non-executable reproducibility manifest. Version relevance and lifecycle stay
independent.

All four Evidence entries resolved Result
`26127c48-d736-4983-b035-b68db238f6a7` and the same exact version. The archived
trajectory Viewer loaded 24 frames and moved from frame 1 to frame 2. Global
scientific counts before/after those read-only operations were identical:

```text
Jobs = 285
ToolCalls = 377
Artifacts = 1493
ScientificResults = 191
```

The normal `恢复科研对象` product action returned the object to `ACTIVE`,
cleared `archived_at`, and did not create a version or scientific execution
state. Browser errors/warnings were zero.

Regression evidence:

```text
Report backend = 33 passed / 4 historical live-provider skips
Report frontend + presentation = 33 passed
Phase 8 Report service-backed = 4 passed / 0 skipped
typecheck = PASS
Ruff = PASS
git diff --check = PASS
PostgreSQL = active 1 / idle 9 / idle-in-transaction 0
Redis = 6 idle workers / queued 0 / recent failures 0
MinIO = PASS
```

This closes archive/restore continuity for the exact diffusion
Report/Evidence/Viewer path. Phase 14-R remains `PARTIAL`: the capability's
dedicated diagnostic Table browser proof, broader context/retention/R12 gates,
full regression and P14R-A/P14R-B exact-SHA seals remain open.

## 2026-08-31 Report tables / navigation / operations batch

The Report read model now exposes bounded `table_sources` projected from the
immutable `ScientificResultBundle.tables`. Authenticated Report
`agent2_report_e54681009a0e49abe371247d9053ce61` rendered the persisted
trajectory tables `轨迹扩散性质` and `轨迹均方位移`, with stable table
references, exact Artifact links and source version
`a22745f2-17b6-434f-ba4c-3fe6bd244841`. The page explicitly states that the
table is read-only persisted data and cannot trigger scientific recomputation.

Product navigation remains inside the mounted Next App Router shell: internal
links prefetch on pointer/keyboard intent, pending transitions expose
`aria-busy`, and heavy scientific viewers are lazy-loaded with a truthful
persisted-data loading state. The authenticated report route had zero browser
errors, duplicate IDs or horizontal overflow.

The standalone operations snapshot now supports `--same-stack`, selecting the
local qualification topology explicitly. Its real run returned
`status=ok`, PostgreSQL `active=1/idle=9/idleInTransaction=0`,
`staleJobs=0`, `staleResearchTurns=0`, Redis `workerCount=6/queued=0`, and
MinIO `status=ok`. Direct `--help` invocation also works with an empty
`PYTHONPATH`.

Regression evidence for this batch: backend `49 passed / 4 historical
compatibility skips`; frontend Report/Navigation/ProductShell/Research
`99 passed`; typecheck, compileall, Ruff and diff checks pass. No services or
the authenticated browser tab were closed. The overall Phase 14-R verdict
remains truthfully `PARTIAL`; no P14R release commit was created.

## 2026-08-31 Research timeline duplicate replay repair

`ResearchPages` now performs a narrow adjacent-message deduplication pass over
persisted timeline records. It merges only consecutive entries with identical
role/content, so deliberate repeated user questions separated by an assistant
response remain visible and auditable. This prevents replay/import duplication
from presenting one scientific question multiple times without changing the
immutable message IDs or scientific authorities.

Fresh authenticated browser verification on
`/projects/project_0002_1a0af866391f412d/research` now reports four canonical
`data-message-id` nodes (two user messages and two assistant responses), no
browser errors, and no horizontal overflow (`documentWidth=731`,
`viewportWidth=731`). Focused frontend regression is `94 passed`; typecheck,
compileall, Ruff and `git diff --check` pass. Services remain live on
PostgreSQL/Redis/MinIO and the Chrome tab remains open.

This is a product-quality repair only. Phase 14-R remains `PARTIAL`; broader
capability-wide acceptance, retention/export, recovery stress, full regression
and exact-SHA P14R release gates are still open.

## 2026-08-31 Current-worktree regression confirmation

The full frontend suite now passes `102 test files / 728 tests` after the
timeline deduplication and lazy-viewer changes. The targeted backend campaign
passes `46 tests / 4 historical compatibility skips`; the standalone
same-stack operations snapshot remains `status=ok` with PostgreSQL
`active=1/idle=11/idleInTransaction=0`, Redis `workerCount=6/queued=0`, and
MinIO `status=ok`. A fresh authenticated browser transition from Data to
Research used the mounted App Router shell, returned to the exact Research
route without a document reload, and retained `documentWidth=731` equal to
`viewportWidth=731` with zero captured errors.

These are regression and product-fluency improvements only. Phase 14-R remains
truthfully `PARTIAL`; release commits and exact-SHA CI have not been created.

## 2026-08-31 Navigation pending-state cleanup

The shared ProductNavigation provider now clears a pending navigation intent
as soon as the App Router commits the exact target pathname/query, instead of
waiting for the 15-second safety timeout. This keeps the mounted workbench
responsive and prevents stale “正在切换工作区” state from making a completed
transition appear slow. Regression coverage includes route/query commits and
all prior same-origin/API/external-link rules; `RouteTransitionProgress` and
`ProductShell` focused tests pass `18/18`, and typecheck passes.

No scientific state is touched by this shell-only repair. Phase 14-R remains
`PARTIAL`; no release commit or CI seal has been created.

The first implementation attempt exposed a production-build constraint:
`useSearchParams()` in the shared provider caused the static
`/settings/models` page to require a Suspense boundary. The provider now uses a
bounded 50 ms URL commit check only while a navigation intent is pending,
preserving query-route cleanup without introducing a static-rendering bailout.
The focused tests remain `18/18`, production build now passes all `17` routes,
and typecheck passes.

The authenticated Research route was rechecked after Fast Refresh: no pending
navigation marker remained after commit, browser errors were `[]`, and layout
width remained bounded at `731/731`.

The exact historical trajectory Turn
`fb72c2ad-bed1-47d7-b557-f398f04a8ede` was reopened through Project History.
The mobile conversation panel exposed the bounded “本次上下文” disclosure;
its manifest showed one exact source/version item, `context_manifest_id`
`c4785024-6027-42af-9a1f-52143afd7303`, policy
`agent2.context-policy/2.0`, `12000` token input budget, `60` estimated input
tokens, and exact version
`a22745f2-17b6-434f-ba4c-3fe6bd244841`. Expanded context remained within
`731/731` and duplicate DOM IDs remained zero.

## 2026-08-31 Report navigation and source-context controls

The Report reader now has a stable report-scoped chapter bar. The authenticated
Report `agent2_report_e54681009a0e49abe371247d9053ce61` rendered eight chapter
links; the `主要发现` anchor resolved in place with no document navigation and
layout remained bounded at `715/715`.

Scientific Presentation now separates `固定到研究上下文` for an immutable
Result snapshot from `固定来源版本` for its exact
ScientificObject/ScientificObjectVersion pair. The latter uses the existing
authorized Session Memory `pinned-objects` endpoint. A real authenticated
trajectory Result pinned source version
`a22745f2-17b6-434f-ba4c-3fe6bd244841`; no scientific Job, ToolCall, Artifact
or ScientificResult was created. Focused frontend tests passed `26/26`;
typecheck, production build, compileall and diff checks passed. Phase 14-R
remains `PARTIAL`; no release commit or exact-SHA CI was created.

The fresh full frontend regression completed at `102 test files / 730 tests
passed`. Same-stack operations snapshot remained `status=ok` with PostgreSQL
`active=1/idle=12/idleInTransaction=0`, Redis `workerCount=6/queued=0`,
MinIO `status=ok`, and no stale active or queued work. This confirms the
batch did not regress the wider UI/runtime surface.

## 2026-08-31 Directory request continuity

`listProjects()` and `listDatasets()` now use a bounded 20-second shared
promise/cache window with explicit invalidation on write mutations. This
reduces duplicate directory requests during App Router navigation while
retaining mutation freshness. Planner/Data focused tests passed `66/66`;
typecheck and `git diff --check` passed. Overall Phase 14-R remains `PARTIAL`
because the capability-wide, lifecycle/export, recovery, evaluation,
operations and exact-SHA release gates are still open.

## 2026-08-31 Research control visibility

The `编辑问题` and `继续研究` actions now switch narrow layouts to the
conversation panel before routing/focusing the composer; `?edit=` routes retain
that conversation-first state after the route effect runs. Authenticated
browser proof showed `selectedTab=对话`, editing guidance visible, bounded
`731/731` layout and no alerts. Research/Presentation focused tests passed
`71/71`. This closes a mobile control-visibility defect but does not claim
full browser edit submission/branch persistence or overall Phase 14-R closure.

## 2026-08-31 Browser edit branch and historical switch

Authenticated browser submission through the immutable edit composer created
Turn `17c0b9d1-b5c0-47f9-b93c-c5f8a1cb19df`, reached two completed analysis
outputs and rendered branch `2/2`. The branch switcher then returned to
historical Turn `fb72c2ad-bed1-47d7-b557-f398f04a8ede`, preserving its original
question/result. No alert or layout overflow was observed. Full stop/retry and
true 390px browser qualification remain open; overall Phase 14-R is still
`PARTIAL`.

## 2026-08-31 Failed-run recovery visibility

For history routes carrying `run=`, the mobile panel now moves to the
conversation surface when durable progress is `FAILED` or `CANCELED`, exposing
the existing `继续研究` and `重新研究` controls. Browser proof showed both
labels, `selectedTab=对话`, bounded `731/731` layout and no alerts. Focused
ResearchPages tests passed `64/64`; full cancellation/retry stress remains
unqualified and overall Phase 14-R stays `PARTIAL`.

## 2026-08-31 Grounding display-rounding repair and live retry

The remaining interpretation failure was isolated to the quantitative grounding
normalizer. Authoritative trajectory facts persisted full precision
(`0.038618084156 Å²/ps`, `0.064094868867 Å²`, `0.970301847945`), while the
provider's grounded answer used bounded display values (`0.0386`, `0.0641`,
`0.9703`). Exact references, evidence edges and units were already valid; the
validator compared only exact numeric strings and therefore rejected legitimate
presentation rounding.

`apps/api/mdi_api/interpretation/grounding.py` now accepts only lexical decimal
rounding derived from the claim's resolution, capped at 1% of the authoritative
magnitude. Unit normalization and evidence/reference checks remain unchanged.
The regression accepts the three bounded rounded values and rejects an
unrelated quantitative value. Interpretation focused coverage is `26 passed /
1 historical skip`; Report plus interpretation coverage is `60 passed / 5
historical skips`; touched Ruff and `git diff --check` pass.

After restarting only the interpretation worker to load the current worktree
(PostgreSQL, Redis, MinIO, API, frontend and the authenticated Chrome tab stayed
running), the real browser retry created child Turn
`b82c5758-fac8-4f30-b0ab-5df94dd68369` from failed Turn
`17c0b9d1-b5c0-47f9-b93c-c5f8a1cb19df`. It completed with Job
`job_agent2_b82c5758fac84f30b0ab5df94dd68369`, Result snapshot
`8d506aa2-0247-4ea8-ae39-0c629ad3b991`, `10` authoritative facts, two
ToolCalls, eight Artifacts, `grounding_status=VALID`, and terminal Turn
`COMPLETED`. Exact source remained object
`f834e358-9944-4fe8-a3ab-f85d68041f54` / version
`a22745f2-17b6-434f-ba4c-3fe6bd244841`. The only browser console error was an
expected unauthenticated bootstrap request from the standalone fresh context;
no 5xx or critical API response occurred.

Two fresh Dataset edit attempts were correctly routed as `ANSWERED` because
their requests were answerable from the selected persisted Dataset facts; no
Job/Result was created. This confirms `QUERY_DATA != ANALYZE` remains intact,
rather than indicating a dispatch or service failure. Same-stack operations
snapshot remains `status=ok`: PostgreSQL `active=1/idle=12`,
`idleInTransaction=0`, Redis `6` idle workers with queue depth `0`, MinIO
`status=ok`. Phase 14-R remains `PARTIAL`; capability-wide qualification,
retention/export, recovery stress, full regression and P14R exact-SHA release
gates are still open.

## 2026-08-31 Structure Viewer, XRD table and Report quality batch

The authenticated Structure presentation campaign now resolves the real Viewer
entry instead of stopping at a descriptor. For exact Structure version
`8859cb49-0766-48cd-8a56-e44f5332e0c5`, the presentation exposed
`/projects/project_0002_1a0af866391f412d/data?object=dc3c3eee-f254-4edf-a0fa-c955402b3069&version=8859cb49-0766-48cd-8a56-e44f5332e0c5`;
the Viewer rendered a Canvas, showed the exact version and Structure content,
and recorded no non-GET scientific mutations. CrystalNN and VoronoiNN findings,
evidence inspection and exact-source disclosure remained present. The isolated
browser context again showed only the expected bootstrap `401`, with no 5xx.

The real XRD Data Platform path displayed the experimental XRD surface and
opened its persisted numeric table with `9` rows. Desktop and mobile widths
were bounded at `1280/1280` and `390/390`; loading and table opening recorded
zero non-auth mutations. The Report quality campaign also passed the current
Structure and Dataset reports: exact versions and expected findings were
visible, chapter headings included methods/discussion/figures/tables/
limitations/conclusion, and raw capability IDs/JSON were absent. On mobile the
Report chapter strip is intentionally horizontally scrollable inside the
viewport (`document/body=390`); it does not create global page overflow.

## 2026-08-31 Service recovery, mobile reinterpretation and navigation batch

After a service-stop report, the same-stack runtime was rechecked without
closing the authenticated Chrome tab. PostgreSQL `55434`, Redis `6379`,
MinIO `9000/9001`, API `8000/8002` and frontend `3000` were listening;
`GET /health/runtime` truthfully reported PostgreSQL, Redis, MinIO and the
Redis-backed worker. No existing Chrome tab or service was closed.

The authenticated 390x844 Research path reached the Workbench tab and the
scoped `重新解释（不重算科学结果）` action. A real browser run created
`INTERPRET_RESULT` Turn `89037298-7fb1-4c48-bbd3-5407d3f93f41` from parent
`fb72c2ad-bed1-47d7-b557-f398f04a8ede`; it completed with
`grounding_status=VALID`, exact trajectory source
`f834e358-9944-4fe8-a3ab-f85d68041f54` /
`a22745f2-17b6-434f-ba4c-3fe6bd244841`, and no attached Job or execution
Result. This is a read-only scientific reuse proof, not a new computation.
The standalone browser context reported only the expected unauthenticated
bootstrap `401`; no 5xx or critical response occurred and overflow was
`390/390`.

The same-stack authenticated navigation campaign measured zero document
reloads and preserved the mounted ProductShell. Cold transitions were
`120–267 ms` to URL commit and `137–628 ms` to usable content; warm
transitions were `102–141 ms` and `120–163 ms`, respectively. The evidence
supports the current App Router continuity work and does not claim the
broader Phase 14-R maturity gates are closed.

## 2026-08-31 Task/notification recovery and full regression batch

The authenticated Task Center/Notification path read `30` persisted task rows,
with `8` items requiring attention and `4` canceled records; no live stop
control was exposed because no persisted task was currently running. The
offline banner appeared with the truthful message that server research may
continue, and cleared after the browser returned online. Mobile layout stayed
bounded at `390/390` with zero overflowing elements. The isolated context again
reported only the expected bootstrap `401`; no 5xx or critical response was
observed.

The current frontend full regression passed `102 test files / 730 tests`, and
the Phase 14-R backend/service subset passed `10` with `8` historical skips.
Operations remained healthy with PostgreSQL `active=1/idle=12`,
`idle-in-transaction=0`, Redis queue depth `0` and six idle workers, and MinIO
`status=ok`. `compileall` and `git diff --check` passed; typecheck also passed.

## 2026-08-31 Global Search same-stack browser proof

The authenticated global search modal queried `mat-2` against the current
PostgreSQL-backed API and returned `8` authorized results. Desktop and mobile
layouts stayed bounded at `1280/1280` and `390/390`; no non-auth mutation,
5xx response or critical browser error occurred. Search remains a navigation
read model, not scientific authority. The remaining row is `PARTIAL` only for
broader historical/organization coverage.
Static closure for the current batch also passed: touched Ruff `All checks
passed`, `uv lock --check` resolved `111` packages without drift, production
Next build compiled successfully with `17` routes and shared first-load JS
`104 kB`, and `compileall`/`git diff --check` remained green.

## 2026-08-31 Context disclosure and edit continuity browser proof

Using a fresh authenticated Chromium context against the same-stack runtime,
the canonical Dataset Research result route rendered the persisted result and
exact Dataset version `be02266a-7d4f-4ebb-9f28-3132855167d0`. The user-facing
context disclosure was opened through its real `<details>` control and its
nested `审计详情` disclosure; the page exposed the bounded input budget
(`12000` tokens), manifest identity, policy version and context fingerprint.
The evidence disclosure was also opened. The same run exposed `编辑问题`,
`继续研究`, `重新研究（新运行）` and `重新解释（不重算科学结果）`;
editing preserved the original Turn route and displayed `正在编辑上一条问题`.
Scientific presentation heading IDs were Turn-scoped and duplicate-free. The
isolated browser context reported only the expected unauthenticated bootstrap
`401`; there were no 5xx/critical API responses. This closes the context
disclosure browser evidence seam, while provider-scale context stress/replay
and broader message lifecycle qualification remain open.

## 2026-08-31 Fresh same-stack service regression

With the running API configured through
`postgresql+psycopg://mdi@127.0.0.1:55434/mdi`, Redis-backed workers and MinIO
left online, the current-worktree service/context regression completed with
`26 passed`, `0 failed`, `0 errors` and `0 skipped` in `425.80s`. The selected
paths covered Phase 6/7/8 service-backed execution plus Context Manifest,
recovery and operations checks. A post-run operations snapshot remained
`status=ok`: PostgreSQL `active=1/idle=12`,
`idle-in-transaction=0`, pool checked-out `0`, Redis `workerCount=6` and
queue depth `0`, MinIO `status=ok`, and no stale active Jobs/Turns. Historical
qualification rows remain retained diagnostics and were not treated as live
work. This strengthens current service evidence but does not close the
capability-wide, retention/export, recovery-stress or exact-SHA release gates.

## 2026-08-31 Current-worktree frontend regression after UI repair

The complete frontend suite was rerun from the current worktree after the
context disclosure accessibility change: `102 test files / 730 tests passed`.
This includes the Research context, ProductShell navigation/search, Report,
Viewer, Data Platform, Task Center and responsive surface tests. No new
failure or mandatory skip was introduced. This is fresh regression evidence;
the broader mature-product and P14R release gates remain open.

## 2026-08-31 Context disclosure accessibility repair

The Research context manifest and nested audit disclosure now expose stable
accessible names (`本次研究使用的上下文` and `上下文审计详情`) while retaining
native keyboard-toggle behavior and the existing progressive disclosure
layout. `apps/web/app/components/ResearchPages.test.tsx` verifies both names;
the full `ResearchPages` suite passed `64/64`. This is a bounded accessibility
repair only; broader mature-product gaps remain unchanged.

## 2026-08-31 Mobile Report chapter navigation repair

The authenticated Report quality browser campaign identified and repaired a
real mobile UI defect. At `390x844`, the chapter navigation previously had
`scrollWidth=422px` inside a `358px` box; it now wraps into bounded rows with
touch-sized links and `overflowCount=0` while preserving all eight chapter
anchors and exact source-version content. The focused
`ScientificReportRoute`/`ScientificReportsIndexPage` suites passed `27/27`.
This change is CSS-only and does not alter Result, Report, provenance or
scientific execution semantics. Phase 14-R remains `PARTIAL` for the
unqualified broader product gates.

## 2026-08-31 Correctly isolated full backend baseline

The full non-integration backend suite was rerun without the service-only
`DATABASE_URL` override so temporary SQLite migration fixtures remained
isolated from the live PostgreSQL qualification stack. Result:
`1919 passed, 32 skipped, 170 warnings` in `231.89s`; no test failed. The
earlier 40 failures were environment contamination rather than product
regressions.
## 2026-08-31 Post-repair frontend/build verification

After the mobile Report chapter navigation repair, the current frontend suite
completed with `102 test files / 730 tests passed`. TypeScript typecheck passed,
the local Next production build completed successfully for all `17` routes
with `104 kB` shared first-load JavaScript, `uv lock --check` resolved `111`
packages, `compileall` passed, and `git diff --check` returned cleanly.
The broad repository Ruff scan still reports pre-existing historical debt in
unrelated legacy/evidence files; no new touched-code Python lint was added by
this CSS-only repair.

## 2026-08-31 Report export feedback and browser proof

Report Markdown and reproducibility exports now use one bounded browser download
helper with an accessible live status. Successful clicks announce that the
artifact is prepared for download; unavailable Blob URL support fails closed
with a visible retry message. This is presentation-only and does not mutate
the immutable Report snapshot, Result, source version or scientific execution.

The authenticated Chromium run opened Report
`agent2_report_401cfb421fcab8a9366e06fedb3acb6d` and observed two browser-created
export Blobs: Markdown (`2529` bytes) and reproducibility JSON (`1403` bytes).
Both status messages were visible, Report content included the validated report
heading and reproducibility disclosure, and no 5xx/critical response occurred.
The isolated browser context emitted only the expected bootstrap `401`.
Focused `ScientificReportRoute` coverage passed `20/20`.

## 2026-08-31 Project history navigation cache repair

Project Home no longer forces a full history read on every project selection.
The existing bounded history cache is reused, and lifecycle/data/session
mutations continue to invalidate it explicitly. This removes an unnecessary
full-ledger round trip from App Router back-navigation while preserving exact
Project/ResearchTurn/Result identity.

Evidence:

- `ProjectHome.test.tsx`: `3/3` passed, including a two-project switch-away/
  switch-back case with exactly one history request per project.
- Related ProductShell/ProductPages/planner upload regression: `49/49`
  passed.
- Full frontend regression after the repair: `102 test files / 732 tests
  passed`.
- Typecheck, `git diff --check`, and Next production build passed; build
  emitted `17` routes with `104 kB` shared first-load JavaScript.
- Same-stack health remained PostgreSQL/Redis/MinIO, six idle workers, zero
  queued work, and `idle-in-transaction=0`.

The Phase 14-R release gate remains `PARTIAL`; no P14R commit or CI was
created in this batch.

## 2026-08-31 Report lifecycle browser recheck

Authenticated Chromium reopened Report
`agent2_report_e54681009a0e49abe371247d9053ce61`, exposed the existing action
menu and server-derived 11-dependency impact preview, archived and restored
the report without identity mutation, and retained mobile layout at
`390/390` with `overflowCount=0`. Only the expected isolated bootstrap `401`
was observed; no 5xx or critical browser response occurred.

## 2026-08-31 Task/notification refresh continuity

Task Center and Notification Center now keep the current persisted rows and
actions visible during timer, visibility, and online refreshes. Only the first
load uses the full loading state; later refreshes expose a bounded
`正在同步最新状态…` status instead of flashing the entire page back to
loading. This directly addresses the reported “page feels slow/reloads”
experience without changing any Job, ToolCall, Artifact, Result, or
provenance authority. Focused Task Center/Notification Center coverage passed
`5/5`, and typecheck passed. Overall Phase 14-R remains `PARTIAL`; no release
commit or CI was created.

Authenticated Chromium rechecked `/tasks` and `/notifications` on the same
stack: 30 task rows were readable, notification filters responded, the
390x844 notification surface stayed at `390/390` with `overflowCount=0`, and
the offline banner cleared after reconnect. The isolated browser emitted only
the expected bootstrap `401`; no 5xx/critical response occurred.

Background refresh failures now keep the last authorized task/notification
rows visible and expose `同步失败，当前显示上次结果`; only the initial load
uses the full error state. Focused Task Center/Notification Center coverage
passed `6/6`, with no change to scientific execution or provenance authority.

The latest current-worktree frontend regression completed with `102 test files
/ 734 tests passed`; typecheck and production build passed (`17` routes,
`104 kB` shared first-load JavaScript). Same-stack PostgreSQL/Redis/MinIO
health remains green with six idle workers and zero queued work. Phase 14-R is
still truthfully `PARTIAL`; no P14R commit or CI was created.

Authenticated Chromium mobile qualification of `/tasks` read 30 task rows at
`390x844`, with document/body widths `390/390` and `overflowCount=0`. The
isolated context emitted only the expected bootstrap `401`; no 5xx/critical
response occurred.

### 2026-08-31 — Scientific table mobile interaction repair

The real Data Platform table at `390x844` had a bounded internal content width
of `400px` while the document/body stayed at `390px`; this was an internal
scientific-table scrolling affordance gap, not page-level overflow. The
`workspace-table-scroll` wrapper now has a keyboard-focusable `role="region"`,
an explicit accessible label, `overflow-x: auto`, inline overscroll containment
and stable scrollbar space. Authenticated Chromium confirmed
`clientWidth=390`, `scrollWidth=400`, `pageOverflow=false`, one verified table,
and no unexpected errors beyond the expected bootstrap `401`. Focused
Dataset/Product/Workspace tests passed `70/70`. Phase 14-R remains `PARTIAL`;
 no release commit/CI was created.

### 2026-08-31 — Modern report lifecycle in global search

The authorized `/search` projection now resolves lifecycle state for modern
Scientific Report snapshots from the existing `project_configs` lifecycle map
instead of treating every legacy `reports` row as active. Archived and trashed
modern reports therefore remain discoverable only through their explicit
lifecycle filter, while project authorization and bounded result limits remain
unchanged. The regression inserts a modern report snapshot, archives it through
the existing lifecycle authority, and proves `status=archived` returns exactly
that report while `status=active` returns none. Focused backend
`tests/test_project_access.py -k product_search` passed `4/4`. Phase 14-R
remains `PARTIAL`; no release commit/CI was created.

### 2026-08-31 — Global search modern-report browser proof

Authenticated Chromium at `390x844` opened the real Reports surface and the
global search dialog, queried `Li 扩散性质评估`, and resolved the modern report
`agent2_report_e54681009a0e49abe371247d9053ce61` to the exact in-app route
`/projects/project_0002_1a0af866391f412d/reports/agent2_report_e54681009a0e49abe371247d9053ce61`.
The result was labeled `当前 · 科学报告`; document/body width remained
`390/390` with no overflow. The only console error was the expected auth
bootstrap `401`; there were no critical `5xx` responses. This confirms the
modern report lifecycle search fix is reachable through the product UI while
preserving the existing report route authority. Phase 14-R remains `PARTIAL`;
no release commit/CI was created.

### 2026-08-31 — Task/notification browser requalification after state-copy fix

Authenticated Chromium rechecked `/tasks` and `/notifications` on the live
stack: 30 persisted task rows, 8 attention notifications, and 4 canceled
notifications. The notification tabs remained bounded and the mobile
`390x844` document/body widths were both `390` with zero overflow. Offline
banner and online resynchronization still worked; only the expected auth
bootstrap `401` appeared and there were no critical `5xx` responses. The task
center's canceled-state copy is now covered at both component and browser
surfaces. Phase 14-R remains `PARTIAL`; no release commit/CI was created.

### 2026-08-31 — Task Center canceled-state copy

Task Center already classified both `cancelled` and `canceled` as terminal
attention states, but the user-facing label map only covered the British
spelling. The UI now renders either persisted spelling as `已取消`, preserving
the existing retry/open semantics. The focused Task Center regression passed
`4/4`; no scientific state or queue behavior changed. Phase 14-R remains
`PARTIAL`; no release commit/CI was created.

### 2026-09-01 — Notification Center bounded history disclosure

Notification Center now applies the same bounded-window disclosure for
terminal-state notifications: filters with more than 30 visible rows say that
only the recent 30 are rendered and direct the user back to project history
for older records. This is a read-only UX truthfulness improvement and does
not alter task or scientific authority. The affected focused notification
regression passes with the existing Task Center suite.

The shared task feed also propagates the backend `nextCursor` signal. Thus a
feed with fewer than 30 rows still discloses a bounded window when the service
has older records, rather than presenting a page boundary as complete history.
`task-center-data` focused coverage is `3/3`, including cursor propagation and
partial-project authorization behavior.

### 2026-08-31 — Truthful bounded global-search counts

The authorized `/search` projection now keeps the payload bounded while
explicitly returning `truncated` when a category reaches its bounded query
window. The UI then says “at least N” instead of implying an exact total that
would require unbounded loading. Cross-project authorization is unchanged.
Focused backend product-search coverage passed `4/4`, including a `limit=1`
assertion with `truncated=true`. Phase 14-R remains `PARTIAL`; no release
commit/CI was created.

### 2026-09-01 — Task Center stop confirmation and bounded feed disclosure

The Task Center now requires an explicit, reversible confirmation before
calling the existing ResearchTurn cancellation authority. The dialog states
that already committed valid Artifacts remain available and incomplete work is
not reported as scientific success. This is a product-control improvement only:
no Job, ToolCall, Artifact or ScientificResult authority changed.

The global feed still renders a bounded recent window of 30 rows. When the
current filter contains more rows, the UI now says `当前筛选显示最近 30 项；
更早任务仍保留在项目历史中。` so the bounded projection is not mistaken for
complete history. Focused Task Center coverage is `5/5`; ProductShell and
ScientificReportsIndex coverage is `19/19`; the complete frontend remains
`102 files / 737 tests passed`. NotificationCenter bounded-window coverage is
`3/3`. Phase 14-R remains `PARTIAL`; no release
commit/CI was created.

### 2026-08-31 — Research history management browser proof

Authenticated Chromium created and managed research session
`research_bb889efa3b584759bb81c059efafd90f` in project
`project_0002_1a0af866391f412d`, exercising rename, pin, archive and restore.
The final projection retained the renamed title, `finalPinned=true`, and
`finalStatus=archived`; the restored record remained visible. The mobile
`390x844` check reported `bodyWidth=390`, `documentWidth=390`,
`overflowCount=0`, with empty browser error and critical arrays. This validates
session organization only and does not mutate ResearchTurn/Result authority.
Phase 14-R remains `PARTIAL`; no release commit/CI was created.

### 2026-08-31 — Reinterpret zero-delta persistence proof

Mobile Chromium completed child Turn `4a2256df-6d41-4725-baa4-884a4b49384f`
with `INTERPRET_RESULT`, `COMPLETED`, and `VALID`, reusing the exact parent
MSD/Diffusion Result from `fb72c2ad-bed1-47d7-b557-f398f04e8ede`. PostgreSQL
project counts were identical before and after the action:
`jobs=45`, `tool_calls=63`, `artifacts=237`, and
`scientific_result_snapshots=31`, proving `0/0/0/0` scientific recomputation
delta. The `390x844` page had zero overflow; only the expected bootstrap
`401` appeared. Phase 14-R remains `PARTIAL`; no release commit/CI was created.

### 2026-08-31 — Mobile reinterpretation clean rerun

Authenticated Chromium at `390x844` returned from Report to the source Research
surface, showed the real `重新解释（不重算科学结果）` action, and completed
child Turn `2c5b6646-d521-4e9d-a939-f9318efdb557` with
`action=INTERPRET_RESULT`, `status=COMPLETED`, and `grounding=VALID`. The exact
source remained object `f834e358-9944-4fe8-a3ab-f85d68041f54`, version
`a22745f2-17b6-434f-ba4c-3fe6bd244841`; ContextSnapshot
`fd138518-efb3-475f-8dc8-0f2aa13a13fe`. The mobile page had zero overflow and
no scientific Job/ToolCall/Artifact/Result creation; the only client failure
was the expected bootstrap `401 GET /api/auth/me`. Phase 14-R remains
`PARTIAL`; no release commit/CI was created.

### 2026-08-31 — Exact Result reuse browser recheck

Authenticated Chromium reopened Dataset ResearchTurn
`8382c443-f9ca-4c90-9aa3-444fea683807`; persisted status was `COMPLETED` with
`SUCCESS`, exact Result `15fc4d39-d2d7-5ac3-907a-cb06ed6b7a3f`, snapshot
`2809dcd1-243e-4323-8538-0a5fe81780d9`, and interpretation `VALID`. The exact
Dataset source remained object `8a425466-b697-4c85-9a43-199414a22865`,
version `be02266a-7d4f-4ebb-9f28-3132855167d0`, including mat-2 facts. This
was a read-only historical reopen; no new scientific work was submitted and
the only browser error was the expected bootstrap `401`. Phase 14-R remains
`PARTIAL`; no release commit/CI was created.

### 2026-08-31 — Scientific table interaction regression

The Workspace shell focused regression now asserts the real table's accessible
scroll-region contract (`role="region"`, stable label and exact table semantics).
Dataset/Product/Workspace focused coverage passed `71/71`; the complete frontend
suite remains `102 files / 734 tests passed`, with typecheck and production
build green (`17` routes, `104 kB` shared first-load). Phase 14-R remains
`PARTIAL`; no release commit/CI was created.

### 2026-08-31 — Same-stack navigation/performance requalification

Authenticated Chromium against the live PostgreSQL/Redis/MinIO stack rechecked
App Router transitions. Overview/Data/Research/Reports all recorded
`documentRequests=0` with the ProductShell marker preserved; warm usable times
were `188/192/254/139 ms`. Independent page-load baselines remained bounded
with zero overflow (Data desktop/mobile p50/p95 `2139/5184` /
`1462/1490 ms`; Research `1866/1931` / `1874/1901 ms`; Report `850/1403` /
`844/856 ms`). Runtime diagnostics remained healthy:
PostgreSQL `active=1 idle=12 idle-in-transaction=0`, checked-out `0`, Redis six
idle workers with queue `0`, and MinIO `ok`. Phase 14-R remains `PARTIAL`;
no release commit/CI was created.

### 2026-09-01 — production navigation and edit-branch acceptance

The current-worktree Next App Router shell is now production-qualified from
an immutable build directory rather than a development/HMR server. Desktop
`1280x720` project transitions were `61–118 ms` cold and `33–70 ms` warm;
mobile `390x844` transitions were `66–102 ms` cold and `41–68 ms` warm.
Across sixteen Overview/Data/Research/Reports transitions:

```text
documentRequests = 0
post-login auth requests = 0
ProductShell count = 1
exact shell marker/node preserved = YES
```

Repeated pointer/focus intent is coalesced before App Router prefetch, and the
redundant 50 ms `window.location` completion poll was removed. Navigation
completion now follows the committed App Router pathname/search state. The
previous non-hydrated `3005` tab was diagnosed as a mismatched local build
directory (old cached HTML/manifest plus overwritten hashed chunks), not a
PostgreSQL/Redis/MinIO or application-auth failure. The latest immutable
production runtime `3008` authenticated and rendered the Research workbench
with no captured browser errors.

Authenticated edit submission created child Turn
`92fcd73e-3803-4dcf-bc7a-a63fbcf2a70e` from parent
`8382c443-f9ca-4c90-9aa3-444fea683807`. It completed with Result
`a6769b88-abbb-54e5-867d-8a12562c6062` and 17 facts, retained exact Dataset
object/version `8a425466-b697-4c85-9a43-199414a22865` /
`be02266a-7d4f-4ebb-9f28-3132855167d0`, and reopened through the persisted
`26 / 26` branch switcher. Desktop and mobile had no global overflow or
unexpected critical response.

Focused navigation/ProductShell/Research regression: `85 passed`; typecheck
and production build: `PASS`. Phase 14-R remains `PARTIAL` for the remaining
capability-wide, retention/export, recovery, operations and final release
gates; no P14R release commit/CI is claimed by this batch.

### 2026-09-01 — lifecycle, export, recovery and current regression batch

Same-stack authenticated Chromium opened Structure Report
`agent2_report_401cfb421fcab8a9366e06fedb3acb6d` and prepared both the
Markdown export (`text/markdown;charset=utf-8`, 2529 bytes) and bounded
reproducibility manifest (`application/json;charset=utf-8`, 1403 bytes).
The report remained read-only; only the expected initial authentication
`401` appeared and critical responses were zero.

Fresh Research Session `research_dcbdfb7f879a46da80baec79ddf32140` exercised
pin → rename → archive → Trash → restore → current → archive. The final
persisted state was `archived`, title `硅结构研究管理验收 mti0ey21`,
`pinned=true`; desktop and `390x844` checks had zero page/console/critical
failures and mobile widths `390/390` with zero overflow.

Task/Notification browser recovery showed 30 bounded task rows, 8 attention
notifications and 4 cancelled terminal rows. Terminal tasks exposed no stop
action, filters remained usable, the offline banner appeared and cleared
after reconnect, mobile widths were `390/390` with zero overflow, and
critical responses were zero. The only console error was the expected
bootstrap `401`.

Fresh current-worktree regression completed with `102` frontend test files and
`739` tests passing. Phase14-R context/operations/recovery backend coverage
completed with `16 passed`; typecheck, isolated production build, compileall
and touched static checks remain green.

Same-stack navigation/performance sampling (PostgreSQL + Redis + MinIO +
real workers + configured provider) recorded zero overflow and zero critical
responses across Data, Research, Viewer, Report, Tasks and Notifications at
desktop and mobile. Warm usable p50/p95 were Research `1952/2044 ms`,
Viewer `1593/2435 ms`, Report `871/884 ms`, Tasks `1358/1488 ms`,
Notifications `1353/1460 ms`; mobile Research `1704/1908 ms` and mobile
Report `899/958 ms`. Development Data timings were variable due to route
compilation; immutable production navigation remains the authoritative
fluency evidence.

The Report index now mirrors Data Platform selection ergonomics: batch mode
shows the current-filter scope, keeps the accessible checkbox, and adds
explicit “全选报告 / 清空报告 / 清除选择” controls that remain usable on
mobile. The focused `ScientificReportsIndexPage` regression is `9 passed`;
no lifecycle API or scientific identity was changed.

The Report index root now uses a labelled section inside the persistent
ProductShell main landmark instead of emitting a nested `<main>`. This keeps
the Phase 9C single-work-surface structure valid for assistive technology;
the combined Report/ProductShell focused regression remains `20 passed`.

The full current-worktree Python regression is now green after synchronizing
the legacy Phase10K3 evidence manifest with its already-modified evidence
files: `1924 passed, 84 skipped, 185 warnings`. The previously failing
manifest test passes independently (`3 passed`). An isolated PostgreSQL
database `mdi_phase14r_service_20260901` with real Redis DB 14 and MinIO
backed the Agent2 Phase2/3 and Phase10L4 interpretation campaign: `5 passed`,
with no skips or failures; the primary product database remained untouched.

The same-stack operations snapshot after these campaigns reports PostgreSQL
`active=1`, `idle=12`, `idle-in-transaction=0`, pool `checkedOut=0`, six idle
Redis workers with queue depth `0`, MinIO `ok`, and zero stale active/waiting
ResearchTurns or Jobs.

### 2026-09-01 — canonical MSD surface and App Router report continuity

The stale `trajectory.msd = PARTIAL` classification is closed by the existing
canonical Agent2 trajectory lineage rather than by inventing another execution:

```text
ResearchTurn = fb72c2ad-bed1-47d7-b557-f398f04a8ede
ScientificResult = 26127c48-d736-4983-b035-b68db238f6a7
Report = agent2_report_e54681009a0e49abe371247d9053ce61
ScientificObjectVersion = a22745f2-17b6-434f-ba4c-3fe6bd244841
```

The normal authenticated Reports-list path rendered two independently
attributable trajectory outputs. `轨迹均方位移` retained its persisted Figure,
Table `table.527203220b6850b18d5eef4295bd7181`, exact Artifact/version,
limitations and Evidence beside the downstream diffusion result. The same
immutable path already has mobile, archived-source, Viewer and restore
evidence. Read-only PostgreSQL counts remained exactly:

```text
Jobs / ToolCalls / Artifacts / ScientificResultSnapshots
before = 301 / 395 / 1565 / 203
after  = 301 / 395 / 1565 / 203
```

The Report route now remains inside the single ProductShell main landmark,
uses a labelled report-reader region, opens at document scroll position zero
after pathname navigation and leaves query-only Research navigation
untouched. Shared App Router prefetch is no longer duplicated by ProductShell.
The authenticated page had no duplicate IDs or global overflow.

This closes the declared supported scientific Surface/Viewer matrix, including
`trajectory.msd`. Broader Phase 14-R release closure still depends on the
remaining lifecycle/retention, recovery/operations, final regression and
P14R-A/P14R-B exact-SHA gates.

### 2026-09-01 — ScientificObject batch lifecycle browser closure

The authenticated Data Platform batch UI selected exact ScientificObject
`cbfd4a9f-6659-4196-be2b-60f118bfa12f` and executed the reversible product
flow:

```text
ACTIVE
→ batch Archive
→ explicit archived discovery
→ row-owned Restore
→ ACTIVE
```

Before, during and after the flow:

```text
current version = cf2aeeea-53ad-452a-a4ef-7b61555004e5
version count = 1
ScientificResult references = 3
```

No scientific version or Result was created or deleted. After Restore the
archived filter was empty and current discovery again contained the exact
object. The Data route had one main landmark, no duplicate IDs and no global
overflow. Trash was intentionally not executed; its existing UI remains
guarded by the server-derived dependency-impact confirmation.

Focused evidence:

```text
ProductPages = 32 passed
ScientificObject atomic bulk API = 1 passed
Project/Dataset dependency and lifecycle = 4 passed
```

### 2026-09-01 — Same-stack service availability recheck

The previously running qualification stack was revalidated after an
accidental stop concern without closing the authenticated browser tabs or
starting duplicate listeners. Both browser-facing API instances
(`127.0.0.1:8000` and `127.0.0.1:8002`) returned `200` from
`/health/runtime` and reported the actual configured backends:

```text
database = postgresql
redis = redis
artifactStorage = minio (bucket=mdi-artifacts)
worker = redis
llmProvider = deepseek / deepseek-v4-flash / configured=true
```

Frontend development (`3000`), immutable production (`3008`), PostgreSQL
(`55434`), Redis (`6379`), MinIO API/console (`9000`/`9001`) all remained
listening and returned HTTP `200` where applicable. The six Phase 14-R RQ
worker processes (turns, plans, jobs, results, interpretations, reports) were
also present. No service restart, browser-tab close, data mutation, or
qualification-state change was performed in this recheck. A direct `psql`
probe using the generic `postgres` role was rejected because that role is not
defined in the isolated qualification cluster; this is not a service outage
and does not contradict the authoritative API health response.

### 2026-09-01 — Project organization tags, tag discovery and bulk pinning

Project organization is now usable from the existing Projects catalog without
introducing a new scientific model. Owners can edit bounded non-scientific
tags in the existing project dialog, filter the catalog by tag, and search
authorized projects by tag through the existing global search read model.
Projects can be pinned/unpinned individually or in the existing bounded
selection toolbar; server mutations persist only
`project_configs.config_json.pinnedProject/projectTags`.

The secured catalog now loads member roles and project configuration in
set-based queries, avoiding per-row metadata/config N+1 while preserving the
legacy owner-only fallback. Read-only members remain server-denied for all
organization mutations.

Fresh focused evidence:

```text
ProductPages = 36 passed
tests/test_project_access.py = 24 passed
touched Ruff = PASS
typecheck = PASS
production build = PASS
compileall = PASS
git diff --check = PASS
```

The full frontend regression after this organization batch is now
`103 test files / 750 tests passed`.

The authenticated `/projects` tab remained open on the same-stack frontend;
the project catalog rendered the existing search/status/selection hierarchy
and no extra page reload or critical browser error was observed. Phase 14-R
remains `PARTIAL`: organization metadata is closed for Projects, while the
broader retention, provider-scale performance, monitoring/alerting, and final
real-user release gates remain open.

### 2026-09-01 — Project provenance export and current-runtime correction

The Projects catalog now exposes `导出项目清单` from the existing row action
menu. The server projection is authorized and bounded under
`mdi.project-reproducibility-manifest/1.0`, marks `executable=false`, preserves
exact identity/source references, and explicitly excludes raw scientific
payloads, Provider prompts/responses, credentials and infrastructure internals.
The authenticated browser tab on `http://127.0.0.1:3000/projects` opened the
menu for `Phase 3 Project` and displayed the success status
`已导出“Phase 3 Project”的有界复现清单…`.

During live verification the browser initially received `404` because the
3000 development proxy targets 8002 and that API process predated the route.
The current worktree API was reloaded in persistent sessions on 8000 and 8002;
`/health/runtime` now reports PostgreSQL, Redis, MinIO (`mdi-artifacts`), Redis
worker and configured DeepSeek on both endpoints. PostgreSQL/Redis/MinIO and
all existing workers/browser tabs remained open.

Fresh evidence for this batch:

```text
tests/test_project_access.py = 25 passed
ProductPages focused = 37 passed
Phase14-R operations/recovery/context = 21 passed
full frontend = 103 files / 750 tests passed
typecheck = PASS
production build = PASS
compileall = PASS
git diff --check = PASS
touched new-scope Ruff = PASS
uv lock --check = PASS
```

This is an additive organization/portability closure only. Phase 14-R remains
`PARTIAL`; capability-wide live acceptance, retention/purge governance,
provider-scale performance, monitoring/alerting, final regression and
P14R-A/P14R-B exact-SHA CI remain open.

The fresh current-worktree full regression completed after the runtime refresh:

```text
full backend = 1935 passed, 84 skipped, 170 warnings
full frontend = 103 files / 751 tests passed
```

The same-stack operations snapshot remained healthy:

```text
PostgreSQL active=1 idle=8 idle-in-transaction=0
pool checkedOut=0
Redis workers=6, queue depth=0
MinIO=ok
stale product turns/jobs=0
```

The same authenticated browser session also qualified the global search
surface against the current 3000→8002 proxy: querying `mat-2` returned
`找到 8 项，显示前 8 项` with exact authorized Research/Report routes and no
browser warning/error logs. The Search/organization service-backed dimension is
now evidenced as `PASS`; the overall row remains `PARTIAL` for historical
cross-project and saved-view/collection coverage.

The archived-search filter was then exercised in the same authenticated tab
with query `硅结构`: the dialog returned eight authorized historical Research
sessions, each marked `已归档` and linked to an exact project-scoped route.
No warning or error entries were emitted. This is additional browser evidence
for status-filtered discovery; saved-view/collection and broader historical
cross-project coverage remain open.

### Scientific Report organization and immutable-snapshot proof

Report `agent2_report_19a0d0c261c28577101de81532464893` now demonstrates the
bounded management contract:

```text
source_title = 配位数分布统计结果
display title = 结构配位数分布统计报告
pinned = true
snapshot = c8cc6fcb-1f0b-50c6-b6db-049374f7de6e
Result = 2382b0eb-b056-42b2-b6a7-d2e8a4ca398c
route = /projects/project_0002_1a0af866391f412d/reports/agent2_report_19a0d0c261c28577101de81532464893
```

The existing report-row overflow menu exposes Rename, Pin/Unpin, Archive and
Trash. Pinning moved the report to the top; rename preserved the exact route;
Global Search found one authorized report under the display title. Mobile
Chromium was `390/390` with zero overflow and the immutable-snapshot notice
visible. The only console error was the expected isolated pre-login `401`;
critical failures were zero.

The live UI Unpin→Pin cycle retained:

```text
Jobs/ToolCalls/Artifacts/ScientificResults/Report snapshots
= 301/395/1565/203/44 before and after
snapshot SHA-256
= 10a9b50ccd1e4276f50ed94432454dd35f6ad442ca62e34d980804d6302ec555
```

Focused service/UI and authorization tests pass; broader Report revision
comparison and final P14R release qualification remain open.

## 2026-09-01 current-worktree release-candidate reconciliation

Earlier entries intentionally preserve historical checkpoint verdicts. The
following is the current authoritative reconciliation for the release
candidate:

```text
API = 8005
Frontend = 3013 (immutable production build)
PostgreSQL = 55434
Redis = 6379
MinIO = 9000/9001, bucket mdi-artifacts
Workers = 6 idle
DeepSeek = configured
```

Fresh same-stack mandatory campaign:

```text
selected = 70
passed = 70
failed = 0
errors = 0
skipped = 0
deselected = 14 (unmarked optional tests)
```

Fresh current-worktree regression:

```text
backend = 1948 passed, 32 historical optional skips, 0 failed
frontend = 105 files / 764 tests passed
ARIA/product focused = 116 tests passed
compileall = PASS
uv lock --check = PASS
touched Ruff = PASS (115 files)
git diff --check = PASS
production build = PASS
```

Live operations remained healthy after the campaigns:

```text
alerts = 0
DB active / idle / idle-in-transaction = 1 / 5 / 0
pool checkedOut = 0
stale jobs / turns = 0 / 0
canonical queue depth = 0
MinIO = ok
```

The authenticated read-only browser audit covered desktop `1280x720` and
mobile `390x844` Project/Data/Research/Viewer/Evidence/Report/Search/Tasks/
Notifications/Trash surfaces with duplicate IDs `0`, global overflow `0`,
console/page errors `0`, unexpected critical 4xx/5xx `0`, and authorization
failures `0`. App Router transitions retained the ProductShell and recorded
`documentRequests=0`. The follow-up ARIA patch removes closed-menu
`aria-controls` references and names the previously unnamed controls.

Implementation and qualification gates are green in the current worktree.
Exact P14R-A/P14R-B commit and CI provenance remains the only release action
not yet recorded here; Phase 15 remains uncreated and unstarted.

The final immutable-bundle browser re-audit is
`docs/agent2/phase14r/evidence/browser_final_aria_reaudit_2026-09-01_r2.json`.
It confirms the rebuilt frontend (PID `29668`, dist
`.next-prod-phase14r-final-20260901`) has zero broken ARIA references, zero
unnamed visible inputs, zero duplicate IDs, zero overflow, zero console
errors/warnings and zero critical HTTP failures across the audited routes.

## P14R-A exact-SHA release qualification

The final P14R-A candidate is:

```text
SHA = 8607b1c1f1cb4afbcbf777b69129a0055a141791
CI run = 33501524613
CI tested SHA = 8607b1c1f1cb4afbcbf777b69129a0055a141791
result = PASS
```

Required jobs all passed:

```text
Unit Tests (Python 3.11) = PASS
Frontend Typecheck & Build = PASS
Service-backed Integration (PostgreSQL + Redis + MinIO) = PASS
Phase 11-3 Scientific Replay (Linux) = PASS
Phase 11-3 Scientific Replay (Windows) = PASS
```

The frontend job included the pinned Chromium/Firefox/WebKit browser
qualification, responsive/accessibility checks, production build and the
Phase 12-7 cross-product UX harness. The service-backed job completed against
real PostgreSQL/Redis/MinIO with no mandatory skips. P14R-B evidence sealing
and its exact-current-head CI remain the only release actions pending.
