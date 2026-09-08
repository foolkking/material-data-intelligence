# DESIGN_PROGRESS

## 2026-09-07 — Autonomous architecture migration milestone

Batch 0 canonical ownership preparation reached the pre-physical-migration
milestone in the active `mdi-b0-5a1` worktree. Project/Data, planning,
jobs, artifacts, reports, interpretation, workspace and repository-bundle
persistence now have canonical application/infrastructure modules while old
`mdi_api.repositories` paths remain compatibility exports. The legacy
runtime, database composition and frontend aggregators remain explicitly
physical-move-later authorities; no second singleton, schema, queue or
scientific authority was introduced.

B0-6 added a deterministic AST-based canonical import guard with explicit
transition allowlists. B0-7 added a read-only deterministic architecture
report covering import edges, cycles, dynamic references, public symbols,
worker handlers/queues, Tool/Adapter identities, launchers and frontend
dynamic imports. Guard and report status are PASS. Physical migration remains
unauthorized pending reviewer approval.

## 2026-09-02 — Scientific viewer unavailable-state recovery

Scientific object viewers now expose a bounded `重新读取来源` action plus a
project-scoped `查看来源与属性` escape hatch when an exact source payload is
temporarily unavailable. Retry re-fetches the existing authoritative viewer
projection only; it does not substitute a newer version or trigger scientific
execution. Focused regression: `ScientificObjectViewer.test.tsx` 1 passed.

Repeated Viewer shells now generate unique limitation-heading IDs, preserving
`aria-labelledby` relationships when multiple scientific surfaces are rendered
on one page. Focused Viewer regressions: 3 passed.

## 2026-09-01 — Payload recovery entry UX

Confirmed missing scientific payloads now expose a direct project-scoped
`重新导入源文件` recovery action while preserving exact source/version
metadata and fail-closed semantics. Scientific fallback headings use
Dataset/data-kind scoped IDs so repeated data surfaces remain accessible
without duplicate DOM identifiers.

## 2026-09-01 — Product data reachability and exact payload recovery

- Verified that the browser-facing runtime is genuinely backed by PostgreSQL,
  Redis, MinIO and Redis workers; the reported unavailable pages were not a
  service outage.
- Corrected the secured Dataset object-store projection so a Dataset with zero
  files and zero objects is a valid `EMPTY` state instead of a storage error.
  The Data surface now distinguishes empty, unavailable and ready states and
  does not offer Research for absent scientific payload.
- Reconstructed one leaked transport-test Dataset only after exact raw and
  normalized SHA-256, parser object ID/hash, schema, row and resolver checks
  passed. Three existing MinIO keys were conditionally created; no scientific
  identity, Result or Report was changed.
- Authenticated inventory now reports 28/28 Dataset routes available
  (17 READY, 11 EMPTY) and 13/13 visible ScientificObjectVersion Viewer
  projections as `READY + PROFESSIONAL`, with no `SOURCE_MISSING`.
- The exact trajectory object from the reported unavailable surface renders
  three frames with professional interaction controls and empty browser logs.
- Full frontend regression is 106 files / 773 tests; typecheck and production
  build pass. Backend/service-backed final reruns are recorded in the active
  Product Maturity task evidence.

## 2026-09-01 — Runtime entry compatibility and project governance

- Rechecked the user-visible runtime after reports of unavailable payloads:
  PostgreSQL, Redis, MinIO, API, six Redis workers and the production frontend
  are healthy; 13 acceptance-visible ScientificObject Viewers and canonical
  Dataset/Report routes return successful readable projections.
- Added a small inert `127.0.0.1:3000 → 127.0.0.1:3013` compatibility alias
  so older bookmarks reach the current production frontend without changing
  scientific/API authority or stopping the retained services.
- Added platform-admin project catalog/member governance over the existing
  `project_members` authority, with owner protection, server authorization and
  sanitized audit events. The Admin Center now exposes the responsive project
  member surface; no ScientificObject/Version/Result/Artifact/Report authority
  changed.

## 2026-09-01 — Context controls and bulk selection

- Added bounded remove controls to the Research session-memory strip for
  pinned Results and exact pinned source versions. Labels remain human
  readable; internal IDs are not exposed in normal UI.
- Added current-filter “select all / clear” controls to Data Platform batch
  selection, with wrapping action groups that preserve the dense scientific
  workbench layout on mobile.
- Focused frontend tests and typecheck pass. Phase 14-R remains partial until
  the broader browser/service maturity campaign is complete.

## 2026-08-31 — Trajectory diffusion evidence, latest interpretation and production navigation

- Closed the real persisted MSD → diffusion evidence seam for Job
  `job_dc63f3f5d57742009c6be09e`: exact `1–6 ps`, 11 points,
  `R²=0.970301847945`, `α=0.924032310013` and bounded
  `D=0.038618084156 Å²/ps` are now projected.
- Re-interpretation
  `interpretation_a115c2ced38a7586161370b7994fec88` increased only the
  immutable interpretation count (`1 → 2`); Job, ToolCall, Artifact and
  ScientificResultSnapshot counts did not change.
- Corrected evidence completeness so known Plot/summary/Recipe presentation
  companions do not masquerade as missing science when the same ToolCall
  already has approved authoritative evidence.
- Research and Report readers now reopen the newest immutable interpretation,
  not the oldest snapshot.
- Reworked the trajectory diagnostic surface into the scientific-instrument
  design language: coherent Chinese labels, persisted/read-only explanation,
  restrained hierarchy, explicit selection semantics and bounded mobile table.
- Isolated production navigation on port `3002` preserved one ProductShell
  with zero document requests across eight route transitions. Warm URL
  response was `33–93 ms`; mobile Research was `390/390` with no post-auth
  browser failures.
- Focused regression: backend `26 passed`, frontend `65 passed`, Ruff,
  typecheck and production build PASS. `trajectory.diffusion` is PARTIAL until
  Agent2 ScientificResultSnapshot plus historical/archived exact-version
  qualification closes.

## 2026-08-30 — Exact failed-Turn recovery and bounded Research history

- Retry/Edit now read the selected persisted ResearchTurn message and exact
  context instead of the session's latest user message.
- Recovery actions are placed under terminal failed/canceled progress:
  `修改问题` and `重新研究（新运行）`; the active control is `停止研究`.
- Browser retry parent `8080a173…` → child `f6441688…` retained exact Dataset
  version `be02266a…` and `mat-2`. Only the Turn count changed; scientific
  execution/result deltas were all zero and the router correctly answered
  without over-computation.
- The 50-message session now renders five messages around the selected branch
  by default, with explicit full-history expansion/collapse. Mobile is
  `390/390`.
- Frontend recovery/history tests are `56 passed`; ContextManifest budget
  tests are `6 passed`; typecheck passes. Phase 14-R remains partial.

## 2026-08-30 — Product navigation, report availability and responsive shell

- Replaced the remaining Planner/Workspace same-origin hard navigations with
  Next App Router links/pushes; project routes keep the persistent shell.
- A warm authenticated Research-to-Data transition used one route request in
  `89ms`, retained the browser marker and made no document/icon reload request.
  Cold development-route compilation remains visible but is not a full reload.
- Added an authorized Report status projection so a normal missing Report is a
  bounded `NOT_REQUESTED` state rather than a repeated `404`; READY still
  opens the exact persisted Report.
- Closed measured mobile global overflow (`375/375`) and desktop Data Navigator
  horizontal overflow (`248/248`, controls `208/208`, rows `224/224`) while
  keeping global actions and 44px lifecycle targets accessible.
- Live edit/branch and re-interpret proof retains immutable parent/result
  identity; re-interpret scientific deltas are all zero.
- Focused backend Report coverage is `22 passed / 4 historical provider
  skips`; grouped frontend coverage is `68 passed`; typecheck passes.
  Phase 14-R remains partial.

## 2026-08-30 — App Router navigation fluency

## 2026-08-30 — Query navigation selection continuity and presentation accessibility

- Fixed a real client-navigation defect in `ProjectDataPage`: when a Dataset
  URL changed between two still-visible datasets, the old `selectedId` was
  considered valid and prevented the URL selection from taking effect. URL
  `dataset` now has priority; selection state falls back only when no valid
  route selection exists.
- Authenticated Chromium proof now switches
  `Phase14R Band Gap Acceptance → Phase14R XRD Validation → Phase14R Band Gap
  Acceptance` without a document request, while the main Viewer heading and
  active row change on each transition.
- Repeated `ScientificPresentationBlocks` now receive unique accessible
  heading IDs via React `useId` when no explicit instance identity is supplied;
  duplicate presentation instances no longer share `aria-labelledby` targets.
- Focused frontend regression: `87 tests passed` across ProductPages,
  ResearchPages, ScientificViewerAdapter, ScientificPresentation and Agent2
  presentation suites; typecheck and production build pass.
- Same-stack services remain running: PostgreSQL `55434`, Redis `6379/13`,
  MinIO `9000`, API `8000`, frontend `3000/3001`, and six workers. Phase 14-R
  remains partial pending capability-wide qualification, resource-health
  cleanup, full regression, and exact-SHA release gates.

- Confirmed through real click navigation that project route changes use Next
  App Router (`documentRequests=0`, window marker preserved), not full browser
  reloads.
- Added a browser-session auth request cache so ProductShell and
  RequireProductAuth coalesce `/auth/me`; post-login measured transitions made
  zero additional auth requests.
- Added pointer/focus prefetch for sibling project routes and native segment
  loading boundaries with the same research-workbench hierarchy.
- Current same-stack warm usable times: Data `131ms`, Research `967ms`,
  Reports `95ms`, Overview `922ms`; cold Report `1659ms`. No critical response
  failures. Phase 14-R remains partial pending broader provider-scale and
  mobile real-user performance gates.
- The project route group now owns a persistent `ProductRouteFrame`, so nested
  page wrappers reuse one shell/auth frame across route transitions. Query-aware
  root transition state is wrapped in Suspense and production build passes.

## 2026-08-30 — Multi-family Report quality

- A durable Report worker generated a VALID Structure Report from the existing
  CrystalNN/VoronoiNN Result; the first unsupported numeric summary was
  fail-closed and the bounded repair succeeded without science recomputation.
- Dataset and Structure reports both pass exact-version, finding,
  discussion/limitation/conclusion and no-raw-JSON browser checks.
- Human-facing report prose now hides implementation capability IDs while
  preserving technical identity in progressive audit/reproducibility details.
- Long fact references now wrap inside the mobile findings grid; Report
  `document/body = 390/390`.
- Post-change backend Report/Context/authorization checks are `45 passed / 4
  historical compatibility skips`; PostgreSQL Alembic head is `0027`.

## 2026-08-30 — Structure Presentation/Evidence/Viewer continuity

- Canonical Structure Turn renders one Presentation with independent
  CrystalNN/VoronoiNN content and two Evidence references.
- Evidence resolves persisted source/Artifact identity and the Viewer link
  preserves exact object/version.
- Viewer adds a progressive full-version disclosure; header remains concise.
- Browser emitted zero scientific mutation requests; canvas rendered and
  mobile Research is `390/390`.

## 2026-08-30 — Task/notification recovery hierarchy

- Stop is now rendered only for live persisted ResearchTurns; terminal and
  legacy task rows cannot offer an invalid cancellation action.
- Task and Notification aggregation expose partial project synchronization
  instead of silently dropping failed project reads.
- Notification Center adds bounded `全部 / 需要关注 / 已完成 / 已取消` filters
  between its overview and event list; row actions remain state-specific.
- The PostgreSQL/Redis/MinIO/API/frontend/worker stack was restored from
  retained state after process loss. Runtime health is fully OK.
- Authenticated Chromium recorded 17 tasks, 7 notifications, zero invalid Stop
  controls, zero mobile overflow and a truthful offline/reconnect banner.
- Focused/grouped frontend coverage is `4 passed` / `60 passed`; typecheck and
  diff-check pass. Phase 14-R remains partial.

## 2026-08-30 — Report management action hierarchy

- Kept the Report itself as the dominant list target and moved row lifecycle
  actions into the existing managed-object overflow menu.
- Made batch selection an explicit mode; bulk Archive/Restore are available,
  while bulk Trash remains prohibited because destructive lifecycle requires a
  per-Report dependency preview.
- Replaced the inline dependency overlay with the shared focus-managed modal;
  Escape closes it and focus returns to the originating Report action.
- Authenticated Chromium resolved duplicate report titles by exact report ID,
  exercised Archive/Restore and the non-mutating dependency preview, and
  recorded zero mobile overflow at `390x844`.
- Focused/grouped frontend regression is `8 passed` / `68 passed`; typecheck,
  touched Ruff and diff-check pass. Phase 14-R remains partial.

## 2026-08-29 — Report dependency-impact confirmation

- Added a secured, read-only Report dependency-impact projection derived from
  the immutable Report snapshot and ScientificResult bundle.
- Report Trash now requires explicit confirmation after showing bounded
  ResearchTurn, ScientificResult, Interpretation, Artifact, Evidence and exact
  source-version dependencies; canceling leaves the snapshot unchanged.
- Focused Report backend/frontend regressions pass. Phase 14-R remains partial
  because retention/purge, broad surface acceptance and release CI are open.

## 2026-08-29 — Phase 14-R operations snapshot

- Added a redacted, read-only operations snapshot for PostgreSQL pool/state,
  stale active versus waiting ResearchTurns, stale Jobs, canonical RQ queues,
  worker availability, recent-versus-retained failures, and MinIO health.
- The current stack is healthy for queue depth/workers/MinIO/transactions but
  correctly reports attention for nine historical automatic-stage
  qualification Turns and one `test_user` queued Job.
- No qualification evidence was deleted or silently terminalized.
- Focused tests and touched Ruff pass; R11 remains partial pending alert
  delivery, data reconciliation policy, concurrency/provider quotas, and the
  production runbook.

## 2026-08-29 — Phase 14-R Dataset-list fluency

- Measured authenticated same-stack API projections over 25 samples.
- Found the 129-row Dataset list issuing 265 SQL statements through
  per-Project Dataset and per-Dataset Profile reads.
- Added batch repository reads and deterministic Profile association, reducing
  the current-worktree path to three SQL statements while preserving Dataset
  visibility and identity.
- Direct PostgreSQL p50 improved from 312.0 ms to 19.7 ms; focused tests and
  touched Ruff pass.
- Phase 14-R remains partial pending the browser cold/warm matrix, Viewer
  timing, lifecycle/retention, operations governance, full surface acceptance,
  and exact-SHA release gates.

## 2026-08-29 — RQ queue lifecycle and durable worker roles

Agent2 Phase 2–8 service-backed fixtures now remove their unique RQ queue
registrations, including nested fixture cleanup. Phase 4 isolates its
RESULT_PENDING boundary from live canonical Result workers unless Phase 5
explicitly opts into its unique Result queue. Fresh same-stack coverage passed
15/15 without registry growth. Historical strict test queues were removed
only after active/scheduled/deferred counts were zero; PostgreSQL failure
evidence was preserved. Missing planning/execution worker roles were restored
without restarting the current stack, leaving five canonical queues empty and
five workers idle.

## 2026-08-29 — Phase 14-R authority recovery qualification

PostgreSQL backup/restore now has a current isolated drill with exact
ScientificObject/Version/Turn/Job/ToolCall/Artifact/Result/Report count
parity, Alembic parity and zero broken identity pointers. MinIO backup/restore
preserved byte checksums and failed closed for a missing object. Redis
transient-loss semantics were proven on an isolated process while the primary
queue and five workers stayed online; queue publication recovery preserves the
same persisted Job. Operations maturity remains partial pending alert,
resource-governance and transient test-queue lifecycle closure.

## 2026-08-29 — Scientific Object lifecycle action wiring

The Data Platform Scientific Object list now uses the existing lifecycle API
for archive/restore actions in the standard managed-row menu. Active and
archived filters update immediately after mutation while exact object/version
viewer navigation remains unchanged. This is a UI bridge only; scientific
identity and version authority are unchanged.

## 2026-08-28 — Task state labels and pin mutation race

Task Center and Notification Center now expose the persisted
`researchTurnId` as a user-facing recoverable-session label and reserve the
legacy read-only label for genuinely unresolvable historical jobs. Scientific
Presentation pin/unpin now guards against stale session-memory responses and
reconciles optimistic state with the authoritative API. Full frontend
regression (96 files / 615 tests), typecheck and production build pass.

The same mutation-sequence guard also covers stale memory-read errors, so an
old failed read cannot undo a newer pin/unpin action. Full backend regression
remains green at 1827 passed / 83 skipped.

Authenticated Chromium also swept the project, Data, Research, Reports, Tasks
and Notifications routes at desktop `1280x720` and mobile `390x844`: all 12
checks had zero horizontal overflow and no page errors. The pre-login 401 and
one aborted Data object-store request were classified as expected bootstrap/
navigation cancellations.

## 2026-08-28 — Exact Turn continuity from task surfaces

Task Center and Notification Center now preserve the authoritative
`researchTurnId` when opening non-Workspace jobs, carrying both `run` and
`turn` query parameters. This keeps durable background-task navigation on the
exact ResearchTurn path and leaves Workspace and legacy run-only fallbacks
unchanged. Focused tests pass.

## 2026-08-28 — Authorized global-search lifecycle filters

The existing project-scoped global search now supports bounded type and
lifecycle filters (`active`, `archived`, `all`). Project archive state is
derived from the authoritative `project_configs` flag and all rows remain
membership-scoped. The UI reuses the current search dialog and only sends
filter options when selected; this is a navigation/organization projection,
not scientific authority. Trash/retention remains outside this narrow repair.

## 2026-08-28 — ScientificResult search continuity

Result search hits now prefer the persisted ScientificResultSnapshot
`research_turn_id` relation and route directly to the exact ResearchTurn.
Rows without a resolvable relation retain the bounded `result=` fallback.
This keeps navigation on the existing authoritative relation and does not
create a second Result identity.

## 2026-08-28 — Scientific Report export transport

The modern Markdown report export now attaches its hidden Blob anchor before
dispatch, removes it after click, and revokes the URL. This hardens browser
download behavior without changing immutable report/scientific state.

## 2026-08-28 — Same-stack worker MinIO environment parity

Fresh service-backed worker subprocesses now inherit the same repository-
supported MinIO endpoint, credential aliases and bucket as the fixture
process. This fixes exact-version payload hydration failures in the Phase 7
reuse campaign without changing scientific authority or worker execution
contracts; the rerun passed 4/4 with no skips.

## 2026-08-28 — ScientificResult logical/snapshot identity bridge

Reuse controls now preserve the distinction between the ScientificResult
bundle `result_id` and the persisted `scientific_result_snapshots.id`. The API
exposes `result_snapshot_id`; frontend reinterpret/continue/pin controls use
it for context/memory operations; explicit snapshot selections are isolated
from recency candidates; and `INTERPRET_RESULT` presentation resolves the
existing immutable snapshot without duplicate scientific execution. Live proof:
Turn `4460fc2c-98f8-4129-8fd5-0615f08dc5a7`, source snapshot
`2809dcd1-243e-4323-8538-0a5fe81780d9`, interpretation
`bf7ef3ec-0567-4c2f-80b6-9b584984c45f` VALID/COMPLETED; counts unchanged
(`117/158/637/88`). Phase 14-R remains PARTIAL.

## 2026-08-28 Agent-2.0 Phase 14-R Agent2 evidence compatibility adapter

- The secured planner evidence route now adapts durable Agent2
  interpretations through the immutable ScientificResult snapshot.
  Historical snake_case/camelCase source bindings are normalized so the
  read-only inspector exposes the exact object/version, Artifact checksum,
  and ToolCall without creating a new scientific authority or execution path.
  Persistence regression: 14 passed; same-stack browser evidence confirms the
  chain is inspectable.

## 2026-08-28 Agent-2.0 Phase 14-R Result reuse qualification

- Re-ran `tests/integration/test_agent2_phase7_service_backed.py` against the
  real PostgreSQL/Redis stack. All 4 cases passed in 114.25s. Interpretation
  reuse preserved the existing Result lineage with zero aggregate
  plan/job/tool-call/artifact/result-snapshot growth; continuation cases
  retained explicit prior-result identity. No browser or scientific authority
  changes were made.

## 2026-08-28 Agent-2.0 Phase 14-R interpretation identity bridge

- Presentation compilation now receives the persisted outer
  `interpretation_id` explicitly, keeping evidence references resolvable even
  when the nested grounded interpretation omits database identity fields.
  This preserves the existing secured evidence endpoint and does not add a
  scientific authority or execution path. Targeted frontend tests: 12 passed.

## 2026-08-28 Agent-2.0 Phase 14-R evidence inspector

- Scientific Presentation evidence references now provide a bounded
  `检查证据链` disclosure backed by the secured interpretation-evidence API.
  It resolves exact source object/version, Result evidence field/value,
  persisted Artifact checksum and ToolCall status without adding a provenance
  authority or any execution path. The UI keeps raw infrastructure details
  out of the normal scientific surface and preserves the existing authorized
  Artifact content route.

## 2026-08-28 Agent-2.0 Phase 14-R legacy history identity clarification

- Project history now labels each persisted run binding as either
  `RESEARCH_TURN` (an authoritative `research_turns` relation) or
  `LEGACY_SESSION_RUN` (the compatibility-only `research_session_runs`
  projection).
- This is read-only metadata derived from existing joins; it does not create a
  second Turn authority, infer identity from Job names, or rewrite historical
  runs. A legacy run remains safely resumable through its explicit session
  route while modern runs retain their exact Turn route.

## 2026-08-28 Agent-2.0 Phase 14-R evidence traversal bridge

- Scientific Presentation evidence references now retain the originating
  `interpretationId` and prefer the existing secured
  `/planner/interpretations/{interpretation_id}/evidence` route.
- This keeps the evidence disclosure tied to the existing authorized
  Result/interpretation bundle instead of exposing decorative labels only; it
  remains read-only and does not create Jobs, Artifacts, or Results.

## 2026-08-28 Agent-2.0 Phase 14-R reinterpret control

- Modern Agent2 scientific presentations now expose a bounded
  `重新解释（不重算科学结果）` action when opened from an authorized Research
  Session.
- The action creates a new ResearchTurn with the prior exact
  `ScientificResult` in `explicit_result_ids`; it does not mutate the old Turn
  and does not itself create a Job, ToolCall, Artifact, or new scientific
  Result. The normal Agent2 router remains authoritative for deciding whether
  reuse is eligible.

## 2026-08-28 Agent-2.0 Phase 14-R context budget policy

- Added checked-in operation-specific `ContextBudgetPolicy 2.0` for
  orchestrator, planner, interpreter, and data contexts.
- Effective budgets derive from provider/product/operation limits after
  reserving output and structured-repair space; scientific identities remain
  server-side and compaction stays deterministic.
- Real-user performance benchmarking remains an open qualification item.

## 2026-08-28 Agent-2.0 Phase 14-R context provenance baseline

- Added the first bounded `ContextManifest 2.0` projection over the existing
  immutable `CONTEXT_RESOLVED` ResearchTurn event. It preserves exact
  object/version and Result identities, authorization status, inclusion
  reasons, content fingerprints, and bounded budget metadata without creating
  a second scientific authority or database model.
- Added a deterministic regression for manifest identity/fingerprint
  preservation. User-facing context disclosure and message-revision controls
  remain open until separately qualified.

## 2026-08-28 Agent-2.0 Phase 14 integration qualification

- Phase 13 remains sealed at `56c096a98d082f2ee145c4a1ca4fd89b8d4538df`;
  Phase 14 qualification uses the real PostgreSQL/Redis/MinIO runtime.
- Project overview history links now propagate the persisted
  `researchTurnId` and `researchSessionId` to the Research route. This closes
  a cross-surface History → Resume identity seam without changing scientific
  authority; the legacy Job-name resolver remains compatibility-only.
- A complete Phase 14 coverage matrix is recorded at
  `docs/agent2/phase14/PHASE14_COVERAGE_MATRIX.md`.

## 2026-08-25 Phase 10 canonical fixture recheck

- Fresh current-profile Structure coordination execution now proves exact
  object/version through ContextSnapshot, deterministic two-capability Plan,
  real Job/ToolCalls/Artifacts/Result and grounded DeepSeek interpretation.
- Fresh electronic Band execution and grounded follow-up also pass. The
  interpreter grounding boundary now ignores opaque provenance digits and
  lower-case `k` point labels without weakening scientific fact validation.
- Materials Explorer remains blocked at the typed input boundary: the current
  requirement accepts `materials.dataset` while the canonical promoted table
  is `materials.table`. Eligibility remains fail-closed; no substitution or
  schema weakening was made. Phase 10 remains PARTIAL and Phase 11 is not
  started.

## 2026-08-19 Scientific result projection closure

- [x] Replaced persisted pre-run machine `purpose`/`reason` text with a bounded
      tool-to-human Chinese step projection; raw execution contract remains in the
      technical record only.
- [x] Filtered persisted and displayed interpretation claims/limitations that
      contain backend counters, artifact/projector/schema/contract identifiers.
- [x] Added a compatibility display sanitizer for older retained assistant
      messages; historical messages remain preserved while default UI hides legacy
      machine leakage.
- [x] Routed `structure.summary` and unregistered structured result objects to
      a readable scientific table summary instead of the 3D viewer or raw JSON.
- [x] Chrome rechecked the retained XRD Research Run and a new real structure
      summary run: no raw plan/claim leakage, no scene validation error, and the
      result/report show a readable verified-data table.
- [x] Historical Workspace API reads/writes now resolve the authenticated
      account through the shared Project authorization service; runtime-only
      compatibility remains test-scoped.

## 2026-08-19 Local browser service consistency

- Browser API calls use the Web origin's `/api/*` rewrite; Next proxies to
  `127.0.0.1:8000`, avoiding Chrome client blocking on direct cross-port calls
  and keeping the session cookie same-origin.
- The disposable local acceptance account owns the retained local projects;
  Chrome verified login and protected `/console`; no production credentials or
  CI configuration changed.

## 2026-08-18 UX-V1.3 Design Documentation + High-Fidelity Prototype

- [x] Reconcile the current Product Architecture Code Audit with the frozen
      Project -> Data -> Research -> Run/Result product model and current backend
      capability boundary.
- [x] Perform browser-observed reference research for EnvForge, Linear, Hex,
      VS Code, NOMAD, Materials Project documentation, GitHub Actions and eLife.
- [x] Establish `.interface-design/system.md` as the durable Scientific
      Research Workbench visual-system authority.
- [x] Produce UX-V1.3 page, viewer, research-workbench, result/Inspector,
      state, responsive/accessibility and design-reality documentation.
- [x] Build and Chrome-review an isolated high-fidelity prototype; it is not
      bundled into production and requires no production API, DB or Queue.
- [x] Validate no default raw internal ID/infrastructure terminology, no fake
      percent progress or fake streaming, and intentional incremental-result,
      limitation and evidence presentation.
- [x] Record the remaining Product Owner decisions without reopening any
      qualification or changing production authority.

No production frontend, backend, API, schema, parser, Planner, Tool Registry,
Queue/Worker, route behavior, qualification authority, or deployment state was
changed by UX-V1.3.

## 2026-08-17 R1.7 Capability Resolution Repair

The capability planner now routes a provider-returned stale `resolutionId`
through the existing single repair budget. The stale identity is never
accepted or rewritten; the provider must return the exact current resolution
on the repair call, otherwise planning remains validation-failed. Focused
regression coverage preserves the existing strict JSON, redundancy, dependency,
and explicit electronic Band/DOS selection behavior.

## 2026-08-16 Q-TABLE Property-Target Closure / R1.6 / Phase D R1.6

- [x] Add the bounded AnalysisIntent 1.1 exact current-Profile material-property target contract.
- [x] Preserve AnalysisIntent 1.0 readability and reject invented, ambiguous, stale, cross-dataset, and non-property targets.
- [x] Prove four natural Q-TABLE turns bind only their required existing Tools.
- [x] Re-run the deterministic all-16 Case/26-turn preflight: PASS with one valid expected rejection.
- [x] Freeze the content-and-contract R1.6 authority with a 16-Case sorted inventory and no active qualification digest artifacts.
- [x] Pass a new Phase D re-seal using a fresh migrated PostgreSQL namespace, Redis, MinIO, API, Worker, provider configuration, and browser readiness.
- [x] Keep real LLM calls, formal qualification submissions, Jobs, ToolCalls, Artifacts, Reports, and Recipes at zero.
- [ ] Phase E remains a separate Reviewer authorization and is not queued by this work.

## 2026-08-16 Phase B/C-R1.5 Comprehensive Authority Reconciliation

- [x] Classify all seven R1.4 blockers before implementing corrections.
- [x] Reconcile the ML fixture/question paths, XRD planned dependency model,
      trajectory parser implementation defect, phonon ordering metadata, and the
      stale seven-demo preflight expectation without scientific support expansion.
- [x] Rerun the non-LLM all-16 Case/26-turn preflight: 15 Cases pass.
- [ ] R1.5 refreeze and Phase D re-seal: blocked only by the Q-TABLE
      normal-user material-property target-binding contract gap requiring Reviewer
      authority.

No live provider call, formal qualification Job, ToolCall, Artifact, Phase D,
or Phase E execution occurred.

## 2026-08-16 Phase B/C-R1.4 Full Executability Preflight

- [x] Replace active qualification digest gates with content-and-contract validation policy.
- [x] Reproduce the old R1.2 Q-TABLE failure and test the JARVIS candidate with explicit natural-language property targets.
- [x] Run the non-LLM, non-formal preflight over all 16 Cases and one expected-rejection contract.
- [ ] R1.4 refreeze and Phase D re-seal: blocked by seven current authority conflicts.

No production semantic authority, frozen package, live provider path, Job, or
Artifact changed during the preflight.

## 2026-08-16 Phase B/C-R1.1 Qualification Authority Hygiene

- [x] Preserve the R1 package and verify its exact SHA-256.
- [x] Confirm the single stale report alias in `Q-ATOMIC-VIEW-001`.
- [x] Define `required*` as canonical and retained `expected*` as exact mirrors.
- [x] Audit all 16 Cases for alias, turn-union, count, Plan-cap, and rejection consistency.
- [x] Harden the non-production validator with the six requested contradiction classes.
- [x] Preserve six multi-turn scenarios and publish ordered live-submission authority.
- [x] Build and extract-verify the deterministic R1.1 package with protected bytes unchanged.
- [x] Reproduce and classify the same 20 unrelated historical full-suite failures.
- [ ] Phase D reseal and Phase E execution remain separately authorized.

## 2026-08-16 Phase B/C-R1 Qualification Authority Reconciliation

- [x] Reproduce `PHASE_E-AUTH-001` from the CSV/Structure input mismatch and 7/4 Plan-cap contradiction.
- [x] Audit all 16 primary Cases against current Registry, Planner, input, Artifact, Renderer, Report, and Recipe authority.
- [x] Separate `requiredExecutionTools`, `allowedExecutionTools`, `forbiddenExecutionTools`, and campaign coverage contributions.
- [x] Preserve all Phase B scientific/source/upload/provenance/license bytes.
- [x] Add a static executable-contract validator with input, companion, cap, Artifact, Renderer, support, identity, and drift gates.
- [x] Freeze a deterministic schema-1.1 package with zero case/root hash mismatches and a distinct external SHA-256.
- [x] Retain Phase E discovery evidence without counting it as final qualification evidence.

The 16 primary Cases are ready for future qualification: 15 supported analyses
and one expected pre-Plan rejection. Primary campaign potential is 45 of 47
Planner-available Tools; `phonon.animation` and
`structure.composition_from_structure` require separately authorized
supplemental scenarios rather than distorted primary Cases. Phase E was not run.

## 2026-08-16 Phase E Discovery and Authority Stop

- [x] Run real-browser discovery through `Q-DATASET-001` and `Q-COMPOSITION-001`.
- [x] Add focused regressions for six observed routing/planning/interpretation defects.
- [x] Preserve each runtime candidate as an immutable local commit.
- [x] Verify `Q-DATASET-001` discovery end to end on candidate `8768f54`.
- [x] Classify the Case 2 CSV/Structure and seven-step/four-step contradictions.
- [x] Stop under `BLOCKED_AUTHORITY_CONFLICT` without mutating Phase B/C inputs.
- [x] Reviewer authorized and Phase B/C-R1 produced a separately versioned corrected authority.
- [ ] A new Phase E campaign remains separately reviewer-gated.

## 2026-08-16 Phase D-R1 Durable Namespace Migration/Bootstrap

- [x] Compare SQLAlchemy metadata and production repository requirements with a database upgraded through Alembic 0007.
- [x] Identify missing `users`/`organizations`, Project foreign keys/index, and process-local Project route wiring.
- [x] Add forward migration `0008_phase_d_r1_namespace` with existing-project identity backfill.
- [x] Route PostgreSQL-mode Project create/list through the production SQL repository.
- [x] Verify empty-db base-to-head and 0007-to-head PostgreSQL migration paths.
- [x] Verify durable Project reload, empty Workspace history, and process-restart survival.
- [x] Remove service-test actor-table DDL workarounds and bind current service assertions to 0008.

No scientific, qualification fixture, Registry, parser, Planner, Adapter,
Artifact, renderer, Report/Recipe, provider, dependency, or lockfile authority
changed. Phase D Attempt 5 and Phase E remain unexecuted.

## 2026-08-10 Phase 12-5 Report/Recipe Implementation

- [x] Verify Phase 12-4 implementation and exact-SHA CI.
- [x] Preserve ReportComposition and RecipeReplayManifest 1.0 authority.
- [x] Present source eligibility, session-only draft, no-write preview, and explicit immutable finalization.
- [x] Present a human-readable non-executable Recipe before exact raw JSON.
- [x] Close only `UX-005`; retain `UX-006`, `UX-009`, and `UX-010` ownership.
- [x] Verify implementation `d20d0a1` in exact-SHA CI `31386432220`.

## 2026-08-10 Phase 12-4 Findings/Evidence Implementation

- [x] Verify Phase 12-3 implementation `9b38a753` and CI `31370240101`.
- [x] Preserve ScientificEvidenceBundle/Item, ScientificClaim and interpretation 1.0 contracts.
- [x] Implement persisted Finding hierarchy and exact evidence membership roles.
- [x] Implement exact Evidence-to-Artifact source selection and provenance chain.
- [x] Implement Summary / Scientific details / Provenance Inspector layers.
- [x] Keep recommendations non-executable and limitations first-class.
- [x] Generate deterministic evidence and close `UX-004` without new P0/P1.
- [x] Verify implementation `9fac62bbb2cc9069da62370ee9d02cf3150e987a` in exact-SHA CI `31379672528` and record completion.

## 2026-08-09 Phase 11-0 Validation Baseline Reconciliation

- [x] Verify the N6 implementation/completion/archive authority and clean entry baseline.
- [x] Admit exactly one Phase 11-0 audit task with no future task creation.
- [x] Inventory all 62 Registry Tools with separate validation axes.
- [x] Inventory parser/resource/input support without claiming library-only formats.
- [x] Index retained evidence, references, fixtures, official examples, tolerances, and gaps.
- [x] Seal Phase 11-1 through 11-5, Phase 12 UI/UX, and Phase 13 closure boundaries.
- [x] Verify implementation `312fd4445d404f0f89c061fbdc055789912dc552` in exact-SHA CI `31324356338`.
- [x] Write the Phase 11-0 completion record; queue archive remains the final direct commit.
- [x] Remove only the Phase 11-0 task; leave Phase 11-1, Phase 12, and Phase 13 non-executable.

No new science, Tool, Artifact family, Profile/Plan version, migration, API,
dependency, renderer, Planner capability, Runtime behavior, or LLM authority is introduced.

## 2026-08-06 Phase 10N-0 Scope Seal Complete

- Current Registry/Adapter/Artifact/Profile/Viewer/Report foundations audited.
- N1-N6 identity, units, wording, fixture, tolerance, cap and security proposals sealed.
- Exact N0 acceptance set: 12/12; decisions N-D001 through N-D033.
- Audit/planning `8f12bdc` passed exact-SHA CI `31074886038`.
- Status: `COMPLETE / REVIEWER_APPROVAL_REQUIRED`; N1 remains reviewer-gated.

## 2026-08-06 Phase 10M-7 Implementation CI Verified

- Evidence-only implementation `21ea4559e097cec649515b35c7f45b63f8eb8511`
  passed exact-SHA CI `31065250027` attempt 2.
- PostgreSQL/Redis/MinIO completed `42 passed, 0 skipped, 0 failed, 0 errors`;
  Unit, frontend, typecheck, build, all browser replays, migration, acceptance,
  evidence, and security gates passed.
- Attempt 1 was cancelled after browser dependency download stalled; attempt 2
  ran the unchanged coverage successfully.
- Completion-record and queue-archive CI remain. Phase 10N-0 is not executable.

## 2026-08-06 Phase 10M-7 Local Closure Complete

- Reconciled the exact M7-A01 through M7-A08 canonical registry across the
  acceptance plan, backlog, execution lock, and execution manifest using a
  marker-scoped validator.
- Added an exact retained-DeepSeek replay test that preserves Profile, Intent,
  Eligibility, Decision, Plan 0.2 graph, ToolCalls, Artifact checksums,
  interpretation/evidence, Workspace Save/reopen, and Report/Recipe identity.
- Added the M7 four-target browser aggregate, PostgreSQL/Redis/MinIO aggregate
  service gate, evidence generator, manifest validation, final capability
  matrix, and explicit limits.
- Production behavior and sealed contracts are unchanged. Exact-SHA CI remains.

## 2026-08-05 Phase 10M-6 Implementation Verified

- Corrected implementation `65e80ba915140e29db08dc053c1d218206daaa03`
  passed exact-SHA CI `31020968546`: Unit, frontend typecheck/build, all Phase
  10 browser replays, migration, evidence, and PostgreSQL/Redis/MinIO service
  integration succeeded.
- Service-backed summary is `41 passed, 0 skipped, 0 failed, 0 errors`.
- M6 is complete awaiting completion-record and verified queue-archive CI;
  M7 remains reviewer-gated and has no executable task.

## 2026-08-05 Phase 10M-6 CI Fixture Corrections

- Initial implementation `3bae949559c1049e0bcfd5de21d4d375e1a488aa`
  passed Unit and Frontend in CI `31017695192`; service-backed detected a
  fixture-only missing `organizations/users` support-table setup before the M6
  assertions. Correction `c7db3ca4a651847b49a994eb7e4ad9a21d32eca7`
  / CI `31018789969` then confirmed Plan 0.1 is correctly projected as
  `LEGACY_READ_ONLY`, not `RUNNING`. The current-source recovery fixture now
  uses the established M1 Profile/Intent/Eligibility/Decision/Plan 0.2 setup.
  Commit `ec2a7e572510be08a7d02c5fcd338807b39ba9e3` / CI `31019983444`
  then exposed a fixture actor mismatch with TestClient's `user_local`
  authorization context; the fixture now uses that exact existing actor. No
  production schema, migration, projection rule, or authorization rule changed.

## 2026-08-05 Phase 10M-6 Workspace Recovery Locally Implemented

- Added canonical durable draft comparison, explicit PATCH/If-Match Save,
  no-op suppression, request abort, success state, typed 412 conflict with
  explicit server reload, and revision-cap read-only behavior.
- Added deterministic URL/persisted fallback resolution, bounded running-Job
  GET revalidation, visibility refresh, stale-response protection, and no
  hidden writes or execution growth.
- Added explicit session-only Report draft disclosure and navigation warning,
  finalized Report/Recipe reload, mobile drawer/sheet focus behavior, 44px
  controls, long-text wrapping, and first-time Workspace guidance.
- Focused frontend `34 passed`, full frontend `411 passed`, evidence `4 passed`, and local Chromium,
  Firefox, WebKit, and Chromium 390x844 recovery replay pass with zero
  unexpected console/page/network failures and zero overflow.
- No schema/migration/API/dependency/contract/science/LLM authority changed.
  Full regression and exact-SHA lifecycle remain; M7 is reviewer-gated.

## 2026-08-05 Phase 10M-5 Scientific Report/Recipe Locally Implemented

- Added strict Python/JSON Schema/TypeScript composition contracts, canonical
  hashes, duplicate-key/depth/size/cap validation, and immutable pair identity.
- Reused existing Report/Recipe repositories and Unit of Work for atomic,
  idempotent snapshots; preview writes nothing and Recipes cannot execute.
- Added exact Workspace source eligibility, 12-section deterministic Reports,
  Plan 0.1/0.2 Recipe projection, seven APIs, JSON/Markdown export, and legacy
  read-only behavior without payload copying or latest rebinding.
- Added Workspace source picker, session draft, preview/finalize, history,
  Recipe detail, exports, keyboard reorder, and mobile focus/overflow behavior.
- Local focused tests and Chromium/Firefox/WebKit/390x844 evidence pass with
  zero external/page/console failures. Full regression/exact-SHA CI remain.
- `NEW_LLM_CALL_SITES = 0`, `REAL_LLM_CALLS = 0`; M6 is reviewer-gated.

## 2026-08-02 Phase 10M-4 Typed Artifact Gallery Complete, Awaiting Archive

- Added a complete exact type/version registry for all 42 shared Artifact
  types, including renderer classification, payload mode, heavy/WebGL flags,
  selection declarations, accessibility fallback, caps, and inert security.
- Added metadata-first Gallery behavior and active-only payload loading with
  exact Workspace/Project/Job/Artifact scope, content length, checksum,
  contract/version, bounded JSON/text, cancellation, and stale suppression.
- Adapted existing Dataset, ML, Composition, Structure, Trajectory, Phonon,
  Brillouin-zone, Volumetric, generic table/plot/text/JSON surfaces without
  frontend scientific recomputation or filename/MIME renderer guessing.
- Reused M3 selection authority. Dataset and Composition emit exact sample
  identity; specialized scientific viewers remain consumer-only for identities
  they cannot formally emit. Whole Artifact selection remains exact.
- Enforced one active heavy viewer and strengthened Three.js context disposal.
  Local Chromium/Firefox/WebKit/mobile replay passes; Chromium covers context
  loss/recovery and 50 heavy switches.
- No migration, database schema, dependency, lockfile, scientific Adapter,
  algorithm, or LLM call-site change. `REAL_LLM_CALLS = 0`. Corrected
  implementation `6287785c` passed exact-SHA CI `30751689618`, including
  browser and service-backed zero-skip gates; completion/archive CI remain.

## 2026-08-02 Phase 10M-3 Canonical Selection Complete, Awaiting Archive

- Added strict canonical base64url parsing, duplicate-key/depth/cap rejection,
  exact semantic equality, 16-item bounded multi-selection, and typed stale or
  unsupported handling over unchanged `WorkspaceSelectionContext 1.0`.
- Added a 32-subscriber Workspace-scoped store, origin-aware deliveries,
  renderer-contract declarations, exact source compatibility, URL/history,
  Inspector, whole Artifact selection, and explicit ETag Pin.
- Chromium, Firefox, WebKit, and Chromium 390x844 evidence pass with zero
  external requests or console errors. Corrected implementation `fe5353f`
  passed exact-SHA CI `30734974889`; service-backed PostgreSQL/Redis/MinIO is
  `39 passed, 0 skipped`. Local service-backed remains unavailable.
- Findings/evidence payload emitters and typed scientific renderers remain M4;
  M3 does not fabricate missing site/frame/q-point/claim identities.
- `NEW_LLM_CALL_SITES = 0`, `REAL_LLM_CALLS = 0`. Future real calls remain
  DeepSeek-only with `DEEPSEEK_KEY`; selection has no provider authority.
- Completion-record and verified queue-archive CI remain. M4 is reviewer-gated.

## 2026-08-02 Phase 10M-2 Workspace Shell Complete, Awaiting Archive

- Added `/workspaces/{workspaceId}` with cancellable metadata loading, stale
  response prevention, the sealed nine navigation groups, one active panel,
  exact `panel` history state, desktop data rail, and overlay inspector.
- Added mobile context/panel drawer and inspector bottom sheet, visible typed
  running/partial/failed/stale/legacy/unsupported states, inert audit JSON,
  and PlannerWorkspace history/idempotent current-Job entry points.
- Focused/full frontend and backend regressions pass. Browser evidence passes
  Chromium/Firefox/WebKit/390x844 with zero overflow and external requests.
  Corrected implementation `d180971` passed exact-SHA CI `30729180057`,
  including PostgreSQL/Redis/MinIO `38 passed, 0 skipped, 0 failed, 0 errors`.
  Completion-record and verified queue archive remain open.

## 2026-08-01 Phase 10M-1 Complete, Awaiting Verified Archive

- Implemented the sealed Workspace domain contracts across Python, checked-in
  JSON Schema, and TypeScript, including strict identity, caps, selection, and
  inert-content validation.
- Added Alembic `0007_phase10m1_workspace_domain`, in-memory/SQLAlchemy
  repositories, explicit historical Job projection, optimistic layout
  revisions, and additive Workspace metadata APIs.
- Focused/full tests, fresh SQLite migration, constant-query project listing,
  browser regression, and evidence checks pass. Corrected implementation
  `27c5aa9` passed exact-SHA CI `30705503707`; service-backed integration is
  `37 passed, 0 skipped, 0 failed, 0 errors`. Completion-record and queue
  archive remain open.
- Workspace UI, panel renderers, selection propagation, and M2 behavior remain
  explicitly deferred.

## 2026-08-01 Phase 10M-0 Audit and IA Seal Complete / Reviewer Approval Required

- Direct reviewer authorization admitted a documentation-only Workspace audit
  without changing `TASKS.md`; task-block count remains zero.
- Current product maturity is `WORKSPACE_LIKE_SINGLE_PAGE`: PlannerWorkbench
  presents the complete chain but has no Workspace entity, route, history,
  aggregate API, saved layout, or global exact selection context.
- M-D001 through M-D025 seal a first-class one-per-Job Workspace, migration
  `0007`, additive APIs, `/workspaces/{workspaceId}`, strict Panel/Selection
  contracts, historical lazy projection, and M1-M7 ordering for reviewer approval.
- Production source, dependencies, lockfiles, current scientific contracts,
  Runtime, Registry, and `TASKS.md` remain unchanged. Audit/planning commit
  `4c5d25e` passed exact-SHA CI run `30698489359`; the separate completion
  record is accepted only after its own exact-SHA CI and is identified in the
  final reviewer return.

## 2026-08-01 Phase 10L Complete / Ready With Explicit Limits

- Phase 10L-4 verified queue archive `58ee943` passed exact-SHA CI run
  `30608078520`: Unit, Frontend/browser/build, and PostgreSQL/Redis/MinIO
  service-backed/no-skipped jobs all succeeded. L4 is
  `ARCHIVED_BY_VERIFIED_QUEUE_COMMIT`.
- Reviewer-approved Phase 10L-5 is the sole active TASKS block. Entry audit
  confirms the canonical Profile -> Intent -> Eligibility -> Plan -> Runtime ->
  Artifact -> Interpretation chain and five required current capability
  families are available. The controlled process uses `DEEPSEEK_KEY` only.
- L5 is implementing a DeepSeek-only real-provider boundary, five genuine
  natural-language closure cases, provider/browser/security evidence, and the
  final Phase 10L lifecycle. Phase 10M-0 remains reviewer-gated.

### Live verification update

- All five frozen natural-language cases passed the real DeepSeek gate.
- Per-case real calls were `3, 3, 3, 4, 3`; total `16`; other real providers
  `0`.
- Each case completed exact Profile -> Intent -> eligibility -> plan -> Job ->
  QueueWorkerRuntime -> artifacts/lineage -> grounded interpretation.
- Dataset and phonon failures from earlier live attempts remain sanitized under
  the evidence directory as regression provenance; they were fixed by strict
  intent disambiguation and exact dependency proposal schema/template context.
- Browser evidence is capture-backed and separately proves the five-case
  UI/API replay across Chromium, Firefox, WebKit, and 390x844 mobile.
- The expanded historical audit is also complete: 40 supplemental semantic
  browser/Mock-LLM cases passed with 92 real DeepSeek calls, for 45/45 total
  current-plus-historical cases. Exclusions are documented by reason and are
  not counted as live LLM coverage.
- Implementation `bfc43bd39d7cc2fa319b9e88f9a4d37eec57ee37` passed
  exact-SHA CI run `30693848581`: Unit Tests, Frontend typecheck/build/browser
  replay, and PostgreSQL/Redis/MinIO service-backed `36 passed, 0 skipped,
0 failed`. Completion record `e4b0a8f5619cbb1001ef64809db6400729a99d8d`
  passed exact-SHA CI run `30694747664`. The verified queue-archive commit
  removes the completed task; Phase 10M-0 remains reviewer-gated.

## 2026-07-31 Phase 10L-4 Grounded Interpretation Complete, Awaiting Archive

- Corrected implementation `02a9e33b93f96aa99413dc49ca2dabca652679c9`
  passed exact-SHA CI run `30606774006`: unit `955 passed, 1 skipped,
32 deselected`, service-backed `31 passed, 0 skipped, 0 failed`, and
  Frontend typecheck/build plus committed Chromium/Firefox/WebKit/mobile replay.
- The ML projector now validates the real six-field `ml.basic_metrics` payload
  (`n`, MAE, RMSE, R2, mean error, max absolute error) and a non-service real
  Adapter/Runtime regression prevents fixture-only drift.
- Two failed CI runs remain in provenance: `3336d9f` / `30604842478` exposed a
  missing service fixture import and honest phonon limited outcome;
  `0d37ea9` / `30605450973` exposed the real ML payload mismatch and a test-only
  unsupported-count assertion. Both root causes are corrected without history
  rewrite.
- Completion record `45af09e` passed exact-SHA CI run `30607509775`, including
  all required Unit, Frontend/browser/build, PostgreSQL/Redis/MinIO, and
  no-skipped jobs. L4 is `COMPLETE / AWAITING_ARCHIVE_CI`; L5 remains
  reviewer-supplied and blocked until the verified L4 queue archive.

## 2026-07-30 Phase 10L-4 Grounded Interpretation Implementation Candidate

- Added strict ScientificEvidenceBundle/Item/Ref, ScientificClaim,
  GroundedScientificInterpretation, and InterpretationExecutionRecord 1.0
  contracts across Python, checked-in JSON Schema, and TypeScript.
- Added deterministic, contract-specific projection for dataset/property, ML,
  structure, phonon, and volumetric Artifacts. The real L3
  `phonon.band + phonon.dos -> phonon.band_dos` chain is included; raw Artifact
  text, filenames, paths, URLs, `summary.md`, and failed/blocked outputs are not
  scientific authority.
- Added deterministic and strict OpenAI-compatible interpretation modes, one
  interpretation-only repair, provider-safe evidence isolation, and independent
  numeric/unit/entity/forbidden-conclusion grounding. Default evidence uses
  `REAL_LLM_CALLS = 0` and has no deterministic fallback after provider failure.
- Added Alembic 0006 immutable bundle/run/claim/evidence-link persistence,
  additive interpretation API routes, and an accessible responsive
  PlannerWorkbench findings/evidence surface. Interpretation cannot mutate or
  create Intent, Plan, Job, ToolCall, queue work, Artifact, or Runtime state.
- Focused backend/frontend, evidence integrity, Chromium/Firefox/WebKit, and
  390x844 mobile checks pass locally. Full regression and implementation,
  completion-record, and archive exact-SHA CI remain required before L4 can be
  complete. Reviewer-supplied L5 remains queued and blocked by the L4 archive.

## 2026-07-30 Phase 10L-3 Bounded Dependency Execution Complete and Archived

- Added strict additive AnalysisPlan 0.2 with one authoritative typed
  `dependencyBindings` representation, deterministic binding/graph/plan
  identities, and hard caps of four steps, six bindings, depth four, and three
  incoming/outgoing bindings. AnalysisPlan 0.1 remains unchanged.
- Audited all 38 available tools and admitted only the existing typed phonon
  chain: `phonon.band` and `phonon.dos` produce canonical artifacts consumed by
  `phonon.band_dos`. ToolPlannerMetadata 1.0 remains valid; explicit 1.1 ports
  alone grant dependency composition eligibility.
- Added exact compatible-pair composition, one shared L2/L3 repair budget,
  dependency validation, Alembic 0005 persistence, serial topological
  QueueWorkerRuntime execution, platform-created resolved artifact refs,
  immutable binding/execution/lineage records, and minimal partial semantics.
- Added additive API and PlannerWorkbench dependency/lineage surfaces. Real
  registered-adapter runtime captures and Chromium/Firefox/WebKit/390x844
  browser evidence pass with zero unapproved network and inert artifact
  content.
- Implementation `d395db2a4f59e2f5fb72e0b33b45161b2bcb5670` passed exact-SHA
  CI run `30542148803`: Unit, Frontend, PostgreSQL/Redis/MinIO migration and
  integration, evidence integrity, and no-skipped all succeeded. The local
  service environment remains honestly `UNAVAILABLE`.
- Completion record `2bd06f22562a9fb1baf65730d30682c1d0ca6c54` passed
  exact-SHA CI run `30542844246`, including Unit, Frontend, service-backed,
  migration, and no-skipped. The completed L3 TASKS block is archived by the
  verified queue commit; Phase 10L-4 remains `REVIEWER_GATE / AWAITING
REVIEWER PROMPT` and has no executable task.

## 2026-07-30 Phase 10L-2 Capability-Aware Planner Complete and Archived

- Added strict planner metadata for all 53 Registry entries; 38 current
  available entries can be considered, while deployment-unavailable and
  Future entries remain non-selectable.
- Added deterministic Registry snapshot, Eligibility Resolution 1.0,
  eligible-only provider projection, structured ranking, exact parameter
  binding/provenance, Capability Decision 1.0, and independent context
  validation. Only `PLAN_READY` can create a plan/job or enqueue.
- Added strict optional OpenAI-compatible selection over eligible candidates,
  one validation-guided repair, no Mock fallback, and default
  `REAL_LLM_CALLS = 0` evidence.
- Added immutable external resolution/decision/execution associations through
  Alembic 0004, additive API summaries, and an accessible PlannerWorkbench
  capability surface. AnalysisIntent remains 1.0; AnalysisPlan remains 0.1;
  PlanValidator and QueueWorkerRuntime semantics are unchanged.
- Focused contract/backend/frontend, browser matrix, performance, security,
  and evidence-integrity checks pass locally. Corrected implementation HEAD
  `9786e405f1938b514b95ccbeb1cdb6d4b26dde18` passed exact-SHA CI run
  `30511654404`: Unit, Frontend typecheck/build, PostgreSQL/Redis/MinIO
  migration/integration, and no-skipped all succeeded. Completion record
  `f62630bef53fc797705683753fbc8d5eca595c98` passed exact-SHA CI run
  `30513319990`; the verified TASKS block is archived and the permanent result
  remains in `results.md`. Phase 10L-3 is still
  `REVIEWER_GATE / AWAITING REVIEWER PROMPT`.

## 2026-07-29 Phase 10L-1 Analysis Intent Implementation Complete

- Added independent `AnalysisIntent` schema `1.0` across Python, checked-in JSON
  Schema, and TypeScript with deterministic semantic hash/ID, exact Profile 2.0
  dataset/resource/target binding, bounded vocabulary, desired outputs,
  constraints, diagnostics, and strict READY/NEEDS_CLARIFICATION/UNSUPPORTED
  consistency.
- Added deterministic and strict OpenAI-compatible Intent builders, an
  independent validator, one-round/three-question Profile-derived
  clarification, immutable revision, and typed Future/Not Planned/execution
  rejection. Default tests make zero real LLM calls and perform no silent
  repair or Mock fallback.
- Added in-memory/SQL repositories, Alembic revision 0003, additive Intent API,
  and an upstream Planner Gate. Non-READY states stop before plan/job/enqueue;
  READY passes the preserved goal to the existing Planner path and stores the
  association outside AnalysisPlan 0.1.
- Added the minimal PlannerWorkbench summary, clarification, unsupported, Run
  gate, and inert audit JSON. Chromium, Firefox, WebKit, and 390x844 mobile
  evidence pass with zero external requests and console/page errors.
- Corrected implementation HEAD `844eb149a4c528d28db9fdf70dddfaf015e91d5a`
  passed exact-SHA CI run `30425804801`: Unit, Frontend typecheck/build,
  PostgreSQL/Redis/MinIO migration/integration, and no-skipped all succeeded.
- Completion record `b4cd656e1c03bb7d6ea406ed0f2dbd828dfb2dd9`
  passed exact-SHA CI run `30426248141` with the same required gates. The
  completed queue block is archived; Phase 10L-2 remains a reviewer gate and
  is not queued.

## 2026-07-29 Phase 10L-0 Agent / Planner Capability Audit

- Audited the real Mock and optional OpenAI-compatible Planner paths,
  AnalysisPlan 0.1, Tool Registry, PlanValidator, persisted job boundary,
  QueueWorkerRuntime, PlannerWorkbench, and representative cross-domain
  prompts. This phase changes no production behavior.
- Classified the current system as `PROFILE_AWARE_SINGLE_TOOL_PLANNER` with one
  narrow sequential-independent two-tool composition. It is maturity Level 3:
  Profile-aware selection exists, but it is uneven and is not capability-aware
  multi-tool planning.
- Confirmed reusable foundations: deterministic Profile 2.0, strict Registry
  execution metadata, validated/persisted plans and hashes, sequential Runtime,
  events, artifacts, summaries, and recipes.
- Confirmed gaps: no structured Analysis Intent, no uniform Profile-to-tool
  eligibility/ranking model, no explicit step dependency or produced-artifact
  binding, no plan complexity caps, no clarification/repair contract, no
  bounded result interpretation, and no pre-execution approval/edit flow.
- Phase 10L-1 remains behind `REVIEWER_GATE / AWAITING REVIEWER PROMPT`; this
  audit does not freeze an implementation architecture or queue the next task.
- Audit commit `a7f8b14` passed exact-SHA CI run `30414233888`, including Unit,
  Frontend typecheck/build, service-backed integration, and the no-skipped
  assertion. Completion record `ee86745` passed exact-SHA CI run `30414599167`
  with the same gates. The verified Phase 10L-0 queue block is archived and
  Phase 10L-1 remains `REVIEWER_GATE / AWAITING REVIEWER PROMPT`.

## 2026-07-29 Phase 10K Material Intelligence Layer Complete

- Integrated the completed Profile 2.0, Dataset Explorer, Materials ML, and
  Composition Space products without adding a run-everything tool or moving
  scientific calculation into the browser.
- Froze one exact cross-product binding over dataset/version, Profile 2.0,
  semantic hash, full dataset content hash, and canonical resource hashes.
  Stable linked-sample identity is `objectId:sampleRef`; row/plot position is
  never used as scientific identity.
- Queue execution now resolves the exact AnalysisPlan Profile revision before
  tool execution. K4 accepts only bounded, exact-binding K3 artifacts and
  preserves source units and coverage. Ambiguous ML intent is safely exposed as
  a diagnostic state instead of falling back to guessed legacy columns.
- Added typed product states, stale-artifact rejection, settled partial refresh,
  runtime/API A-H cases, Chromium/Firefox/WebKit/mobile evidence, deterministic
  replay, near-cap performance, accessibility, network, and security evidence.
- Local full/focused checks and the browser matrix pass. Implementation commit
  `e4639a1` passed exact-SHA CI run `30382233569`; completion record `81d4446`
  passed exact-SHA CI run `30382583135`, including Unit, Frontend,
  service-backed integration, and no-skipped. The verified K5 queue block is
  archived and Phase 10K is `COMPLETE` with explicit limits. Phase 10L-0 then
  entered its audit-only gate; the dated record above supersedes the old NEXT
  status without changing the Phase 10K result.

## 2026-07-28 Phase 10K-4 Composition Space Implementation Complete

- Added the formal `dataset.composition_space` product over Profile 2.0
  formula/property semantics and explicitly bound canonical DataFrames.
- The backend builds atomic-number-ordered normalized atomic-fraction vectors,
  deterministic center-only two-dimensional PCA, optional bounded KMeans in
  feature space, explicit group/resource comparison, descriptive outlier
  candidates, property coloring, and Phase 10K-3 artifact-linked ML coloring.
- Stable identity is `objectId + sampleRef`; projection coordinates and array
  positions are never identity. Invalid formulas and partial color coverage are
  disclosed rather than silently removed.
- Added strict Registry parameters/caps, an explicit Mock Planner route,
  persisted runtime integration, an application-owned SVG/table explorer, and
  inert JSON fallback. UMAP, t-SNE, model training, scientific cluster naming,
  frontend PCA/KMeans, real LLM, external services, and Phase 10L behavior are
  unchanged.
- Runtime/API, Chromium/Firefox/WebKit/mobile, accessibility, performance,
  security, and deterministic evidence are retained. Full backend completed at
  `826 passed, 26 skipped`; frontend completed at `314 passed` with typecheck
  and build success. Implementation/evidence HEAD `fb9d720` passed exact-SHA CI
  run `30372914960`, including service-backed/no-skipped. Completion record
  `97a0781` passed exact-SHA CI run `30373474557`; the verified task block is
  archived and Phase 10K-5 remains next but unstarted.

## 2026-07-28 Phase 10K-3 Materials ML Evaluation Implementation

- Added three product-level Registry/Adapter capabilities for regression,
  uncertainty, and classification evaluation over complete Profile 2.0 semantic
  groups and one explicitly bound canonical table.
- Delivered deterministic aligned-sample metrics, fixed prediction-minus-target
  residuals, stable high-error and misclassification links, overlapping element
  and exact chemical-system diagnostics, common-sample model comparison,
  equal-count uncertainty reliability, retained-error curves, raw confusion
  counts, per-class metrics, and guarded explicit-positive binary ROC/PR.
- Added strict params and layered row/model/class/group/point/bin/artifact caps,
  Mock Planner routes, persisted runtime execution, responsive SVG/table
  products, Dataset Explorer readiness integration, and inert fallback.
- Real API/runtime evidence covers all three tools; Chromium, Firefox, WebKit,
  and mobile evidence records zero console/page errors and external requests.
  Performance evidence covers 4, 5,000, and 100,000 rows without unbounded
  display arrays. Current implementation/evidence-closure HEAD
  `a1e05ee5b0f1affa91183e681b1678d4419cedc4` passed exact-SHA CI run
  `30363719393`, including Unit, Frontend Typecheck & Build,
  PostgreSQL/Redis/MinIO service-backed integration, and the no-skipped gate.
  Completion record `c5483d6` passed exact-SHA CI run `30364098180` with the
  same gates. The verified queue task is archived; Phase 10K-4 remains next.
- No model training, embedding/clustering, real LLM, arbitrary code, dependency,
  external service, Phase 10L orchestration, or workspace redesign was added.

## 2026-07-28 Phase 10K-2 Dataset Materials Explorer Implementation

- Added the coherent `dataset.materials_explorer` product over exactly one
  Profile 2.0 plus explicitly bound table/Structure resources. It emits one
  bounded explorer bundle, quality artifact, summary, and recipe through the
  existing validated Planner/Runtime/Registry/Adapter path.
- Delivered deterministic dataset overview, composition occurrence/system
  statistics, canonical structure summaries, finite-only property
  distributions, factual quality findings, exact formula/structure duplicate
  classes, explicit group/resource comparison, and stable sample links.
- Added seven frontend result tabs with numeric/table fallbacks, responsive
  mobile layout, keyboard/accessibility coverage, and inert JSON fallback. No
  new workspace architecture or browser execution authority was introduced.
- Real persisted runtime/API evidence and Chromium/Firefox/WebKit/mobile replay
  cover mixed composition/structure/property data, partial states, explicit
  train/test comparison, 4/5,000/100,000-row performance, network isolation,
  and security. Current implementation HEAD `35c0fc6` passed exact-SHA CI run
  `30355075439`, including Unit, Frontend, service-backed, and no-skipped gates.
- Completion record `8dc2545` passed exact-SHA CI run `30355282590`; Unit,
  Frontend Typecheck & Build, service-backed integration, and no-skipped all
  succeeded. The permanent result is retained and the verified 10K-2 queue
  block is archived; 10K-3 remains not started.
- ML evaluation remains Phase 10K-3, composition space remains Phase 10K-4,
  and capability-aware planning remains Phase 10L.

## 2026-07-28 Phase 10K-1 Material Data Profile 2.0 Implementation

- Extended the existing `DataProfile schemaVersion=0.1` additively with a
  `profileContractVersion=2.0` deterministic fact layer; no parallel profile,
  new dependency, tool, Planner route, PlanValidator rule, or Runtime behavior
  was introduced.
- Centralized bounded semantic roles for formula, approved numeric properties,
  stable sample identity, regression/multiple predictions/multi-target/
  uncertainty, classification labels, and class probabilities. The old
  Planner-facing `tableSummary.inferredRole` allowlist remains exact.
- Added immutable resource semantics for table, structure/composition,
  trajectory, phonon, and volumetric normalized objects and separated data
  readiness from actual platform implementation availability.
- Added deterministic semantic hashing, dataset-version/object-hash sample
  fallback, typed ambiguity/missing reasons, explicit coverage disclosure, and
  caps of 4096 rows, 512 columns, 1024 formula values, 64 probability columns,
  and 256 resources.
- Existing upload/profile endpoints and persistence serialize the contract. A
  compact read-only frontend surface displays semantics, readiness, planned
  capabilities, coverage, and warnings.
- Focused API/unit/component checks, full local backend/frontend regression,
  typecheck/build, Phase 10 closure, and API/performance plus
  Chromium/Firefox/WebKit/mobile evidence pass. Implementation `92a8e98` passed
  exact-SHA CI run `30346512968`, including service-backed/no-skipped.
  Completion record `b5a464e` passed exact-SHA CI run `30346686652`; the
  verified 10K-1 queue block is archived and 10K-2 remains unstarted.

## 2026-07-27 Phase 10K-0 Material Intelligence Capability Gap Audit

- Audited the real parser/normalizer, `DataProfile 0.1`, Registry and adapter
  closure, Planner routing, frontend profile/results surface, artifacts,
  dependencies, caps, tests, and Phase 10A-C evidence. No product code, schema,
  tool, dependency, Planner, runtime, or frontend behavior changed.
- Classified the current profile as `MINIMAL`: table/structure summaries are a
  reusable foundation, but trajectory/phonon/volumetric discovery, material
  property semantics, model-task semantics, stable sample identity, and
  available/unavailable analyses are absent.
- Classified the Planner as `PARTIAL_PROFILE_AWARE / MOSTLY_PROMPT_ROUTED`.
  Capability-aware multi-tool planning and interpretation remain Phase 10L.
- Confirmed real executable foundations for table summaries, composition
  aggregation, lightweight structure statistics, and basic regression. Several
  historical V1 Manifest identities have no matching runtime adapter and are
  not counted as implemented.
- Froze the implementation order as 10K-1 Profile 2.0, 10K-2 Dataset Explorer,
  10K-3 ML Evaluation, 10K-4 Composition Space, and 10K-5 integration/evidence.
  Phase 10K-1 has not started.
- Audit commit `cada6fb` passed exact-SHA CI run `30270323576`, including unit,
  frontend typecheck/build, PostgreSQL/Redis/MinIO service-backed integration,
  and the no-skipped assertion. Completion record `ab5a69a` passed exact-SHA CI
  run `30270636913`; the verified 10K-0 queue block is archived and 10K-1 remains
  unstarted.

## 2026-07-27 Gate J6-R Product Roadmap Correction

- Phase 10J-6 implementation (`9cd0c69`), completion record (`75cec5f`), and
  queue archive (`16c4c18`) remain verified by successful exact-SHA CI. Its
  product readiness remains `READY_WITH_EXPLICIT_LIMITS` and its evidence and
  result history are unchanged.
- Gate J6-R supersedes the short-lived post-J6 J-7 through J-12
  electronic/Fermi roadmap without rewriting history. No scientific feature,
  schema, tool, route, runtime behavior, renderer, or dependency changed.
- The unique current route is 10K Material Intelligence, 10L Intelligent
  Analysis Agent, 10M Unified Scientific Workspace, 10N Professional Scientific
  Completion, Phase 11 validation, and Phase 12 final closure.
- CrystalNN/VoronoiNN, local environments/polyhedra, experimental XRD,
  trajectory analytics, and Electronic Band/DOS are initial-release work.
  Fermi Surface and advanced research products are Future Scope. Enterprise
  SaaS, deployment productization, and plugin marketplace are Not Planned.
- Phase 10K-0 is the next approved direction but remains unstarted until its
  complete executable prompt is supplied.

## 2026-07-27 Gate J6-A / Post-J6 Roadmap Reconciliation (Superseded)

- Phase 10J-6 implementation (`9cd0c69`), completion record (`75cec5f`), and queue archive (`16c4c18`) each have successful exact-SHA CI; its retained result and evidence establish `READY_WITH_EXPLICIT_LIMITS`.
- Repository audit confirms electronic band/DOS and Fermi Surface remain unimplemented. Existing band/DOS products are phonon-specific, and Phase 10I BZ/link contracts reserve no electronic semantics.
- At that time, continuation was frozen as J-7 through J-12. Gate J6-R later
  superseded this current-roadmap decision while retaining it as history.
- Historical J-5 ELF/Orbital and J-6 Slice/Volume names remain unchanged.

## 2026-07-26 Phase 10J-6 Volumetric Slice / Volume Rendering Completed

- Added validated three-axis exact/interpolated lattice slices with periodic wrap/non-periodic bounds, an application-owned cancellable Worker, deterministic hashes, quantitative 2D heatmap/probe/table, and true affine Three.js planes.
- Added a lazy WebGL2 Direct Volume path with canonical `width=nz,height=ny,depth=nx` R32F mapping, explicit float64 display conversion audit, bounded static ray marcher, application palettes/transfers, affine/triclinic mapping, PNG, fallback, and context/lifecycle handling.
- Added one-scene structure depth prepass and shared affine clipping for volume, atoms, bonds, and cell. Real Runtime cases cover CHGCAR charge/spin, LOCPOT, ELFCAR, PARCHG, and triclinic CUBE; Chromium near-cap `128^3` evidence uses an 8 MiB generated payload without committing it.
- Added source-native Slice decoding, true Worker termination on supersession, exact legend/table/keyboard probes, lazy perspective/orthographic 3D Slice, shader compile/link preflight, and annotated bounded Slice/Volume PNGs.
- Local closure passes 294 frontend tests, 760 backend tests with 24 intentional service-gated skips, 98 Phase 10J tests, typecheck/build, all required historical viewer runners, and real Chromium/Firefox/WebKit/mobile evidence with zero external requests. Implementation CI `30197771307` and completion-record CI `30197900247` passed unit, frontend dependency install/typecheck/build, PostgreSQL/Redis/MinIO service-backed integration, and no-skipped assertion. Queue archival was verified.

## 2026-07-24 Phase 10J-5 ELF / Orbital Product Implemented

- Added strict application-owned ELF and orbital/partial-density product mapping over unchanged Phase 10J artifacts, with decoded-value range/non-negativity validation, exact units/isovalues, full-cell statistics/integrals, source identity completeness, and no-clamp/no-renormalization boundaries.
- Reused the Phase 10J-2 Worker/Three.js renderer and added a bounded renderer-local `2x2x2` periodic structure overlay, hidden-object picking guard, scientific inspector/warnings, clipping, PNG, mobile/accessibility, and one-canvas lifecycle evidence.
- Real Mock Planner -> QueueWorkerRuntime evidence covers ELFCAR, PARCHG, and an explicitly identified CUBE; Chromium, Firefox, and WebKit all rendered WebGL2 with zero console/page errors and zero external requests. Signed amplitude, multi-orbital CUBE, ELF topology, complex phase, orbital reconstruction, and electronic identity inference remain deferred.

## 2026-07-17 Phase 10I-3 Band-BZ Linked View Completed

- Added the strict frontend-only `phase10i3.reciprocal_band_bz_link.v1` model over existing `phonon.band` and `structure.brillouin_zone` runtime artifacts; no public tool, persisted link artifact, scientific recomputation, dependency, or canonical schema was added.
- Added exact structure/primitive-lattice/convention/unit/path/discontinuity compatibility, point occurrence, segment direction, sampled q-point `t`, branch separation, bounded mapping, typed mismatch fallback, and stable provider/time-reversal warnings. Display labels are never mapping identity.
- Added one transaction-safe hover/pinned reducer, bidirectional Band/BZ selection, shared inspector/table, exact animation handoff, artifact cleanup, desktop/mobile composition, and controlled reuse of the Phase 10I-2 BZ engine.
- Closure passed 20 focused frontend link/BZ lifecycle tests, seven backend routing/runtime/evidence tests, 223 full frontend tests, and `661 passed, 23 skipped, 62 warnings` backend tests, plus typecheck/build, real Chromium 150/Firefox 128/WebKit 18 WebGL2 evidence, mobile canvas lifecycle, accessibility, near-cap mapping, zero external requests, and secret scan. Implementation/fix commits `f81aedb`, `5b5873e`, and `f3fa177` culminated in current-HEAD CI run `29572530288`, where unit, frontend/typecheck/build, service-backed integration, and no-skipped gates all succeeded.
- Completion record `02c550b67afa479ec711b45c1e9db0d61ff148b0` passed current-HEAD CI run `29572771301`; the result record was verified and the completed queue block was archived.

## 2026-07-15 Phase 10I-2 Brillouin Renderer / Evidence

- Added a strict frontend bundle mapper and outward-normal bounded face triangulation over unchanged Phase 10I artifacts; reciprocal Cartesian `angstrom^-1` values use one uniform visual scale and no repeated `2*pi` conversion.
- Added a lazy application-owned Three.js BZ engine with translucent faces, canonical edges/vertices, primitive reciprocal axes, high-symmetry points/labels/path, canonical point/face/vertex/segment picking, inspector, text tables, reciprocal-basis cameras, projection, layer/opacity/variant controls, fixed-camera PNG, fallback, context reinitialization, and complete demand-render lifecycle.
- Kept `structure.brillouin_zone` as the sole product identity and expanded explicit interactive English/Chinese routing while retaining electronic/phonon/trajectory/Fermi/mesh/magnetic/surface/editing exclusions. Artifacts still contain no renderer, shader, module, URL, texture, or network authority.
- Real PlannerWorkbench evidence passed Chromium 150, Firefox 128, WebKit 18, portrait/landscape mobile, point/face picking, PNG, context loss, accessibility, nonblank canvas, performance, console, and zero-external-network checks.
- Local closure passed 209 frontend tests, `654 passed, 23 skipped` backend tests, focused Phase 10I replay, typecheck/build, Ruff, lock/tree checks, and the historical Phase 10 three-browser product pack. Implementation commit `b5469c35cc39f096037036309a37aab160c9593c` passed CI run `29420821864`; completion record `28a3cfa934a350e5a704d9f7b35b080b354eef83` passed run `29421142527`. Unit, frontend build, service-backed integration, and no-skipped gates are closed, so the verified queue block may be archived. The configured npm audit endpoint returned `404 NOT_IMPLEMENTED`.

## 2026-07-14 Phase 10I-1 Brillouin Zone Adapter

- Registered the unique JSON-only `structure.brillouin_zone` data tool with strict single ordered/non-magnetic 3D Structure input, fixed provider policy, six inert output types, and Phase 10I caps.
- Implemented local pymatgen/spglib primitive standardization, physics-`2*pi` reciprocal construction, bounded Wigner-Seitz generator binding, Setyawan-Curtarolo paths, production provenance, validation, hashes, summary, and recipe.
- Added explicit English/Chinese planner routing, negative capability routing, PlanValidator coverage, persisted QueueWorkerRuntime replay, scientific references, typed rejection, and sanitized evidence.
- Added a fixed application-owned reciprocal/BZ/k-path/manifest JSON preview using real adapter evidence, with no canvas, graphics context, artifact execution, or renderer claim. No dependency, network, external asset, real LLM, Three.js/WebGL renderer, browser GPU evidence, or interactive BZ product was added; those remain Phase 10I-2 scope.
- Local closure passed 88 focused tests, 194 frontend tests, `648 passed, 23 skipped` backend tests, typecheck/build, Ruff, evidence replay, and the Phase 10 browser regression pack. Implementation commit `08d7742ddc6d1574a79c99baf90f019f3635aa3f` passed current-HEAD CI run `29384696711`; completion record `4defa6f4d40b074364395404451201dff21b64b5` passed run `29384954078`. Unit, frontend typecheck/build, service-backed integration, and no-skipped gates are closed, so the completed queue block is archived. The configured npm audit endpoint remains unavailable; no dependency or lockfile changed.

## 2026-07-14 Phase 10I Brillouin Zone Contract

- Added the inert `phase10i.reciprocal_lattice.v1`, `phase10i.brillouin_zone.v1`, `phase10i.kpath.v1`, `phase10i.brillouin_zone_manifest.v1`, and versioned tolerance contracts.
- Fixed row-vector physics-`2*pi` reciprocal mathematics, source/primitive/conventional transform direction, first reciprocal Wigner-Seitz topology, deterministic point/path identity, provider/time-reversal metadata, caps, hashes, and typed security validation.
- Added simple-cubic, BCC, FCC, hexagonal, triclinic, and conventional/primitive fixtures plus independent NumPy/SciPy Voronoi/ConvexHull references and Phase 10H compatibility checks.
- No production adapter, Tool Registry entry, planner route, runtime job, frontend component, Three.js/WebGL renderer, dependency, external service, or real LLM path was added.
- Local closure passed `39` Phase 10I tests, `157` focused cross-phase tests, `193` frontend tests, and `605 passed, 23 skipped` backend tests. Implementation commit `653ea133d5791db3f6879b05dc66a2e397d0d646` passed CI run `29339358234`; completion record `3fe1913b53814ef0df31f85baafa265c8ba0df97` passed CI run `29339658353`. Unit, frontend, service-backed, and no-skipped gates are closed, so the completed queue block is archived.

## 2026-07-14 Phase 10H-5 Phonon Animation

- Added formal `phonon.animation` registration and strict structure/band/eigenvector role binding through PlanValidator and QueueWorkerRuntime.
- Added inert frame-free animation package/summary/manifest/recipe, exact mode compatibility, bounded diagonal commensurate supercells, and fixed-envelope complex displacement reconstruction.
- Added app-owned Three.js phase playback, instanced periodic atoms, vectors/trails, picking inspector, exact band handoff, reduced motion, mobile, context-loss, and Chromium/Firefox/WebKit evidence.
- Completed local full regression (`193` frontend tests; `566 passed, 23 skipped` backend), typecheck/build, historical trajectory browser replay, dependency/lock review, and final security scans. The configured npm audit endpoint remains unavailable and is not reported as clean.
- Implementation commit `b67a9e18109f976aeadaf6002eaac6c71297875c` passed current-HEAD CI run `29327516331`; completion record `1021a2e2cba202ffaec22d4e0d35a4fb345a890c` passed current-HEAD CI run `29327795589`. Unit, frontend, service-backed integration, and no-skipped gates are closed, so the completed queue block is archived.

## 2026-07-14 Phase 10H-4 Phonon Eigenvector Contract

- Added inert mode/eigenvector/set/summary/manifest contracts with band hash, structure/calculation, q-point, branch, frequency, atom-order, and NAC binding.
- Fixed Cartesian complex `real[3]+imag[3]`, mass-weighted Euclidean unit norm, explicit atomic masses, canonical global phase, and phase-insensitive scientific equivalence.
- Added mass unweighting, bounded Gamma/non-Gamma static displacement reconstruction, display-only amplitude policy, small Python/NumPy/TypeScript fixtures, security, and evidence.
- Parser, adapter, tool, mode UI, commensurate-supercell solver, animation, thermal science, dependencies, network, and real LLM remain deferred.

## 2026-07-14 Phase 10H-3 Combined Band + DOS

- Added formal `phonon.band_dos` composition over validated band and DOS artifacts with ordered compatibility, source hashes, and no source mutation.
- Added exact frequency conversion, DOS density Jacobian/integral invariance, structure/atom/cell/lineage/NAC/normalization checks, and a shared union THz axis.
- Added six inert product artifacts, validated local Plotly combined preview, projection selector, tables, export, responsive accessibility, and three-browser evidence.
- Eigenvectors, animation, thermal properties, calculations, scripts, remote artifacts, dependencies, and real LLM execution remain deferred.

## 2026-07-14 Phase 10H Phonon Contract

- Added closed `phase10h.phonon_band.v1`, `phonon_dos.v1`, `phonon_summary.v1`, and `phonon_manifest.v1` contracts with deterministic Python validation and independent TypeScript consumer validation.
- Fixed row-vector `B = 2*pi*(A^-1)^T`, reciprocal-fractional q-points, explicit discontinuities, global path distance, canonical THz, negative-real imaginary modes, source-stable full `3N` branches, source-declared degeneracy, and canonical atom ordering.
- Added total/projected DOS identity and trapezoidal `3N` normalization, band/DOS compatibility, NAC/ASR provenance, application caps, inertness checks, small fixtures, independent NumPy/SciPy comparison, and reproducible evidence hashes.
- No phonon parser, adapter, formal tool, planner route, plot, renderer, eigenvector, animation, dependency, network, notebook/script, or real LLM path was added.

## 2026-07-13 Phase 10G-3 Trajectory Performance / Browser Evidence

- Registered formal `structure.trajectory_viewer` with strict planner routing, PlanValidator inputs, bounded launch options, canonical trajectory artifacts, and capability-truth metadata.
- Hardened trajectory-scoped LRU caching, one-slot seek coalescing, interactive/degraded/refused preflight, context retry, renderer metrics, mobile landscape detection, and bounded fallback output.
- Captured deterministic real parser/planner/persisted-runtime artifacts and Chromium 150, Firefox 128, WebKit 18, portrait/landscape, accessibility, lifecycle, context-loss, and rapid-seek evidence.
- Confirmed one canvas/context, bounded GPU resources and pending work, zero external requests, and no artifact execution; static-reference bonds remain `PARTIAL_READY` and indexed/chunked local storage remains deferred.

## 2026-07-13 Phase 10G-2 Trajectory Viewer

- Added validated trajectory artifact preview with real Three.js frame navigation/playback and dynamic instanced-matrix/lattice-buffer updates.
- Added stable atom/periodic instance identity, committed-frame picking/measurement and velocity/force inspection, renderer-local supercells, camera/clipping integration, bounded cache/stale guards, typed fallback, accessibility and detected mobile controls.
- Chromium, Firefox, WebKit and mobile browser smoke pass with nonblank composited-canvas checks and per-page zero-error/network audits; frontend 132 passed and backend 413 passed / 22 skipped locally.
- Static-reference bonds remain `PARTIAL_READY`; formal product registration and final bounded performance evidence were closed by Phase 10G-3.

## 2026-07-13 Phase 10G-1 Trajectory Parser / Adapter

- Added bounded streaming EXTXYZ and byte-capped canonical trajectory JSON parsers with strict UTF-8, identity, units, lattice/PBC, property, cancellation, and security checks.
- Multi-frame inputs normalize to validated `Trajectory`; single-frame EXTXYZ remains the static Structure path and plain XYZ trajectory is deferred without lattice fabrication.
- Added planner-hidden `structure.trajectory_import` validated runtime path and four inert JSON artifacts with API evidence.
- Viewer, playback, dynamic bonds, analytics, browser evidence, and formal trajectory product registration remain NOT_READY.

## 2026-07-13 Phase 10G Trajectory Contract

- Defined inert `phase10g.trajectory.v1`, frame, summary, and manifest contracts with content-derived identity and deterministic JSON.
- Fixed stable atom/frame identity, row-vector lattice math, coordinate/wrapping/time/unit semantics, strict optional properties, and application-owned caps.
- Added canonical Python validation, independent TypeScript fixture comparison, deterministic evidence, and security/network audits.
- Trajectory parsing, chunking, adapter/runtime execution, formal registration, playback, rendering, and browser/performance evidence remain NOT_READY.

## 2026-07-13 Phase 10F-25 Clipping, Cell, and Camera Controls

- Added bounded application-owned X/Y/Z clipping with shared Three.js materials and matching raycast visibility checks.
- Added independent canonical-cell, outer-supercell-boundary, and lattice-axis display with textual vector equivalents.
- Added deterministic default/top/front/side/isometric camera presets and inert `phase10f25.viewer_view_state.v1` serialization/replay validation.
- Chromium, Firefox, WebKit, and mobile evidence passed without dependency, canonical schema, topology, or backend runtime changes.

## 2026-07-13 Phase 10F-24 Supercell Productization

- Productized strict renderer-local 1x1x1 through 3x3x3 expansion with preflight, presets, outer boundary, degraded/refused states, picking, and measurement provenance.
- Added deterministic inert `phase10f24.viewer_supercell_state.v1` download/replay without canonical structure or topology mutation.
- Reused one WebGL context for expansion buffer replacement; Chromium, Firefox, and WebKit passed 20 lifecycle cycles with no console/network errors.
- Internal grid, clipping, camera presets, persisted structure supercells, trajectory, phonon, Brillouin zone, and volumetric rendering remain deferred.

## 2026-07-12 Phase 10F-15 Production Minimal Structure Viewer

- Consolidated the formal product identity on `structure.viewer_3d`; it now generates canonical inert `viewer_scene.v1` artifacts through the existing validated runtime path.
- Retained `structure.viewer_scene` for explicit JSON export and marked Phase 10D metadata/export tools as legacy direct-purpose compatibility paths.
- Replaced the active MatterViz/fallback-HTML viewer adapter behavior; formal viewer artifacts contain no HTML or executable renderer assets.
- Implemented species-grouped Three.js `InstancedMesh` atoms, bounded single-geometry bonds, renderer metrics, lazy chunk failure/retry, responsive touch controls, scene text summary, species legend, and live accessibility state.
- Aligned canonical, adapter, and renderer caps at 256 sites, 2048 bonds, 32 species, and 1 MB JSON; no renderer truncation is allowed.
- Captured live formal-tool Chromium 149, Firefox 128, and WebKit 18 WebGL 2 evidence, plus mobile, near-cap, legacy, invalid, chunk failure, unsupported, context-loss, console, network, performance, and accessibility evidence.
- Confirmed `NO_PRODUCTION_VIEWER_EXTERNAL_NETWORK_REQUESTS`.
- Corrected the Phase 10F-14 note: the attempted 3050 port drift was reverted before that phase committed; the product default port was not changed by Phase 10F-14.
- Full scientific viewer, trajectory, phonon, Brillouin-zone, volumetric rendering, editing, and advanced measurement remain deferred.

## 2026-07-11 Phase 10F-14 Validated Viewer Scene Renderer Foundation

- Selected and pinned direct `three@0.185.1` with `@types/three@0.185.1`, both MIT.
- Implemented a frontend canonical validation gate, whitelist mapper, geometry/camera utilities, Three.js renderer engine, React surface, typed fallback states, demand rendering, controls and complete disposal.
- Rendered atoms, unit cell and optional bounded bonds from live `structure.viewer_scene` artifacts.
- Added rotate, zoom, pan, deterministic reset, unit-cell toggle and bond toggle while retaining Scene JSON and Manifest preview.
- Added invalid, unsupported and context-loss fallbacks; old Phase 10D schemas remain JSON-only.
- Added mapper, geometry, component, lifecycle, security, integration and near-cap tests.
- Captured real Chrome 149 WebGL 2 evidence, interaction snapshots, live adapter API artifacts and 14 screenshots under `docs/phase10f/evidence/phase10f14_viewer_scene_renderer_foundation/`.
- Confirmed `NO_RENDERER_EXTERNAL_NETWORK_REQUESTS` and no artifact JavaScript/HTML/URL/texture/module/shader path.
- Full `structure.viewer_3d`, production-complete viewer, trajectory, phonon and Brillouin zone remain unimplemented.
- The active product frontend default port was not changed; an intermediate 3050 experiment was reverted before commit.

## 2026-07-11 Phase 10F-13 Viewer Scene Live Adapter Browser/API Evidence

- Added live adapter-backed browser/API evidence for `structure.viewer_scene`.
- Added a Python evidence generator that drives `planner_jobs`, persisted `AnalysisPlan`, `QueueWorkerRuntime.handle_job`, Tool Registry lookup, adapter execution, artifact listing, and canonical validators.
- Added a real Chrome runner that opens the existing PlannerWorkbench JSON-only preview surface using captured live adapter API responses.
- Captured live evidence for valid minimal crystal, multi-species crystal, warning/caps behavior, invalid multi-structure rejection, and manifest preview.
- Captured screenshots, DOM snapshot, console snapshot, network snapshot, API transcript, job execution audit, artifact contract audit, security audit, and schema compatibility audit under `docs/phase10f/evidence/phase10f13_viewer_scene_live_adapter_browser/`.
- Added pytest coverage for live API/runtime evidence, invalid request rejection, old/new schema routing separation, and inert/security evidence payloads.
- Confirmed old Phase 10D viewer tools remain registered and unchanged while canonical `structure.viewer_scene` remains the only `viewer_scene.v1` adapter path.
- Confirmed `NO_LIVE_ADAPTER_EXTERNAL_NETWORK_REQUESTS` for the live Chrome evidence run.
- No full `structure.viewer_3d`, WebGL renderer, Three.js integration, MatterViz renderer, renderer bundle, canvas viewer, iframe viewer, external API, notebook/script execution, real LLM path, new dependency, phonon, Brillouin-zone 3D, or artifact JavaScript was added.

## 2026-07-11 Phase 10F-12 Viewer Scene Minimal Adapter Implementation

- Implemented the canonical, renderer-free `structure.viewer_scene` adapter.
- Added Tool Registry registration with strict params and Phase 10F caps for `viewer_scene.v1`.
- Generated canonical artifacts: `viewer_scene.json`, `viewer_scene_manifest.json`, `summary.md`, and `recipe.json`.
- Reused the existing lightweight structure parser and artifact exporter; the adapter accepts exactly one periodic structure and rejects multi-structure inputs.
- Validated generated scene and manifest artifacts with the Phase 10F canonical validators before export.
- Added Mock Planner routing only for explicit inert viewer-scene JSON prompts; full viewer, WebGL, Three.js, RDF, XRD, coordination, Brillouin-zone, phonon, and trajectory prompts do not route to this adapter.
- Added adapter, registry, PlanValidator, routing, direct execution, persisted queue-runtime execution, deterministic replay, and frontend preview-regression tests.
- Added generated execution, validator, deterministic replay, preview compatibility, no-renderer, and security evidence under `docs/phase10f/evidence/phase10f12_viewer_scene_minimal_adapter/`.
- Preserved Phase 10D `structure.viewer_scene_metadata` and `structure.viewer_export_package` schemas; no silent migration or replacement was performed.
- No full `structure.viewer_3d`, WebGL renderer, Three.js integration, renderer bundle, 3D viewer component, notebook/script execution, external API, real LLM path, new dependency, phonon, Brillouin-zone 3D, or advanced local environment classifier was added.

## 2026-07-09 Phase 10F-10 Viewer Scene JSON-only Preview Surface Implementation / Evidence

- Implemented JSON-only `viewer_scene.v1` preview support in the existing PlannerWorkbench Results/export artifact preview surface.
- Added manifest preview support for Phase 10F-9 `phase10f9.viewer_scene_manifest.v1` fixtures.
- Added stable frontend evidence selectors for kind, version, schema version, validation state, error codes, warning codes, caps, scene summary, and manifest metadata.
- Added fixture-backed frontend tests covering valid, warning/caps, and invalid `viewer_scene.v1` samples.
- Added automated inertness assertions for no canvas, no script element, no iframe, no real external URL markers, no WebGL markers, and no Three.js markers.
- Added Phase 10F-10 implementation, evidence, security, browser/API boundary, readiness, and next-scope docs.
- Kept JSON-only preview evidence distinct from renderer evidence; real browser screenshot evidence remains optional future hardening.
- No full `structure.viewer_3d`, WebGL renderer, Three.js integration, renderer bundle, 3D viewer component, new adapter, planner routing change, Tool Registry runtime change, production runtime route, notebook execution, external script, external API, artifact JS, HTML renderer, phonon, Brillouin-zone 3D, or advanced local environment classifier was added.

## 2026-07-09 Phase 10F-9 Viewer Scene Contract Fixture / Validator Implementation

- Implemented a renderer-free `viewer_scene.v1` contract fixture pack under `docs/phase10f/fixtures/viewer_scene_v1/`.
- Added valid, invalid, and warning/caps fixtures for minimal crystal, multi-species crystal, optional bonds, non-finite coordinates, external-resource placeholder rejection, executable-field placeholder rejection, cap violations, and unsupported schema version.
- Added manifest fixtures and `expected_results.json` for expected validation states, error codes, warning codes, caps behavior, JSON-only preview expectation, and deferred renderer expectation.
- Added isolated contract validation utilities in `packages/artifact-core/mdi_artifact_core/viewer_scene_contract.py`.
- Added `tests/test_viewer_scene_contract_fixtures.py` to replay fixtures against the validator and manifest expectations.
- Updated shared schema notes with the implemented Phase 10F-9 validator result shape, error codes, warning codes, and fixture-pack location.
- JSON-only browser evidence remains deferred to a later evidence phase; no browser/API evidence is claimed here.
- Renderer evidence, renderer implementation, and full `structure.viewer_3d` implementation remain `NOT_READY`.
- No full viewer, WebGL renderer, Three.js integration, renderer bundle, frontend 3D runtime, new adapter, planner routing change, Tool Registry runtime change, runtime route, notebook execution, external script, external API, artifact JS, HTML renderer, external URL dependency, phonon, Brillouin-zone 3D, or advanced local environment classifier was added.

## 2026-07-09 Phase 10F-8 Viewer Scene Artifact Contract Planning

- Planned the inert `viewer_scene` artifact contract after Phase 10F-7 readiness approved a contract-before-renderer path.
- Fixed artifact identity for planning: artifact kind `viewer_scene`, contract version `viewer_scene.v1`, and schema version `phase10f8.viewer_scene.v1`.
- Planned top-level JSON fields: `kind`, `version`, `schema_version`, `source`, `metadata`, `scene`, `validation`, `caps`, `warnings`, `provenance`, and `security`.
- Planned a viewer scene manifest contract while preserving Phase 10D `viewer_assets_manifest.json` as existing static export-package evidence.
- Converted Phase 10F-7 input caps into validation-contract draft caps: `max_sites: 256`, `max_bonds: 2048`, `max_unit_cell_edges: 12`, `max_species: 32`, `max_cell_expansion: [1, 1, 1]`, and `max_scene_json_bytes: 1000000`.
- Fixed the security boundary: artifacts are inert data, with no artifact JS, no HTML, no external URLs, no remote textures, no renderer-required JSON phase, and no hidden execution path.
- Planned JSON-only browser evidence for static artifact preview; renderer screenshot evidence remains deferred and requires explicit approval.
- Decided viewer_scene artifact contract planning is `READY`.
- Decided JSON-only preview planning is `READY`.
- Decided renderer handoff is `PARTIAL_READY`.
- Decided renderer implementation is `NOT_READY`.
- Decided full `structure.viewer_3d` implementation is `NOT_READY`.
- Recommended Phase 10F-9 scope: Viewer Scene JSON Preview Evidence / Contract Fixture Planning.
- No `structure.viewer_3d`, full interactive viewer, WebGL renderer, Three.js integration, renderer bundle, frontend 3D runtime, new adapter, planner routing change, Tool Registry runtime change, notebook execution, external script, external API, artifact JS, external URL, phonon, Brillouin-zone 3D, or advanced local environment classifier was added.

## 2026-07-09 Phase 10F-7 Advanced Structure Viewer Readiness Planning

- Assessed readiness for future advanced structure viewer work after static physics implementation, browser/API evidence, and fixture-pack replay closure.
- Confirmed the static physics stack remains closed for `structure.coordination_hist`, `structure.xrd`, and `structure.rdf`.
- Used Phase 10D static `viewer_scene.json` metadata and static preview evidence as the baseline for an inert scene-artifact path.
- Proposed a future `viewer_scene.json`, `viewer_summary.md`, and `viewer_recipe.json` artifact contract path.
- Decided `viewer_scene` artifact-contract planning is ready for Phase 10F-8.
- Decided renderer implementation is `NOT_READY`.
- Decided full `structure.viewer_3d` implementation is `NOT_READY` and not approved for direct implementation.
- Kept WebGL and Three.js as future scope requiring explicit approval, sandboxing, dependency review, browser security tests, and console/network evidence.
- Kept phonon bands/DOS, Brillouin-zone 3D, and advanced local environment classification as separate future scopes.
- Official PASS claims remain none.
- Recommended Phase 10F-8 scope: Viewer Scene Artifact Contract Planning.
- No official PASS claim, notebook execution, external script, external API, network workflow, real LLM path, dependency installation, new adapter, adapter semantic change, Tool Registry semantic change, QueueWorkerRuntime change, AnalysisPlanRepository change, `/planner/jobs` change, PlanValidator relaxation, full viewer implementation, WebGL renderer, Three.js integration, renderer bundle, Brillouin-zone 3D, phonon, or advanced local environment classification was added.

## 2026-07-09 Phase 10F-6 Static Physics Fixture Pack Evidence Closure

- Closed the Phase 10F-5 fixture-pack replay evidence for `structure.coordination_hist`, `structure.xrd`, and `structure.rdf`.
- Retained fixture-pack replay result as `PASS`: `coordination_hist_small_crystal`, `xrd_small_crystal`, and `rdf_small_crystal` all replayed successfully through the platform/job flow.
- Confirmed candidate replay values are present in the expected contracts for selected coordination histogram, XRD, and RDF numeric checks.
- Documented the evidence boundary: fixture-pack PASS is allowed, but official examples PASS remains none because all replayed cases have `internal_regression` provenance.
- Added Phase 10F-6 closure docs, evidence boundary matrix, next-scope decision matrix, and Phase 10F-7 next-scope prompt.
- Recommended Phase 10F-7 scope: Advanced Structure Viewer Readiness Planning.
- No official PASS verification, official PASS claim, notebook execution, external script, benchmark extraction script, external API, network workflow, real LLM path, dependency installation, new adapter, adapter semantic change, Tool Registry semantic change, QueueWorkerRuntime change, AnalysisPlanRepository change, `/planner/jobs` change, PlanValidator relaxation, full viewer, WebGL renderer, Three.js, Brillouin-zone 3D, phonon, or advanced local environment classification was added.

## 2026-07-09 Phase 10F-5 Static Physics Fixture Pack Replay Verification

- Replayed the Phase 10F-4 static physics fixture pack through the validated platform/job flow.
- Confirmed selected tools:
  - `coordination_hist_small_crystal` -> `structure.coordination_hist`
  - `xrd_small_crystal` -> `structure.xrd`
  - `rdf_small_crystal` -> `structure.rdf`
- Verified all expected artifacts and static no-JS/no-external-URL security fields.
- Generated candidate replay values in the expected contracts while keeping every `official_pass_claim` false.
- Recorded fixture-pack replay result as `PASS`.
- Retained official PASS claims as none because all cases are `internal_regression`.
- No official PASS verification, official PASS claim, notebook execution, external script, benchmark extraction script, external API, network workflow, real LLM path, dependency installation, new adapter, adapter semantic change, Tool Registry semantic change, QueueWorkerRuntime change, AnalysisPlanRepository change, `/planner/jobs` change, PlanValidator relaxation, full viewer, WebGL renderer, Three.js, Brillouin-zone 3D, phonon, or advanced local environment classification was added.

## 2026-07-09 Phase 10F-4 Static Physics Direct-Uploadable Fixture Pack Construction

- Constructed a small candidate direct-uploadable fixture pack for future replay of `structure.coordination_hist`, `structure.xrd`, and `structure.rdf`.
- Added `docs/phase10f/static_physics_fixture_pack/` with a pack README, manifest, local schemas, provenance policy, tolerance policy, and three bounded case directories.
- Added candidate cases:
  - `coordination_hist_small_crystal`
  - `xrd_small_crystal`
  - `rdf_small_crystal`
- Each case includes a small text input, `input_manifest.json`, `expected_contract.json`, `provenance.json`, and `README.md`.
- Provenance labels are `internal_regression`; all `official_pass_claim` / `official_pass_claims` fields remain `false`.
- Numeric expected values remain `pending_replay_generation` until Phase 10F-5 replays the pack through the platform/job flow.
- Added `docs/phase10f/phase10f4_static_physics_fixture_pack_construction.md` and `docs/phase10f/phase10f5_next_scope_prompt.md`.
- Recommended Phase 10F-5 scope: Static Physics Fixture Pack Replay Verification.
- No official PASS verification, official PASS claim, notebook execution, external script, benchmark extraction script, external API, network workflow, real LLM path, dependency installation, new adapter, adapter semantic change, Tool Registry semantic change, QueueWorkerRuntime change, AnalysisPlanRepository change, `/planner/jobs` change, PlanValidator relaxation, full viewer, WebGL renderer, Three.js, Brillouin-zone 3D, phonon, or advanced local environment classification was added.

## 2026-07-09 Phase 10F-3 Static Physics Direct-Uploadable Fixture Pack Planning

- Planned a small direct-uploadable static physics fixture pack for future replay of `structure.coordination_hist`, `structure.xrd`, and `structure.rdf`.
- Retained Phase 10F-2 status as `PASS` and Phase 10F-1 status as `PARTIAL_PASS`; the current official benchmark pack still has zero direct-uploadable static physics official cases and no official static physics PASS claims.
- Added fixture-pack layout planning, fixture candidate matrix, provenance policy, expected-contract templates, numeric tolerance policy, fixture replay protocol, and Phase 10F-4 next-scope prompt under `docs/phase10f/`.
- Defined provenance labels for `official_direct`, `official_derived_manual`, `official_like_curated`, `internal_regression`, `mapping_only`, `future_scope`, `unsupported`, and `unknown`.
- Recorded that only `official_direct` and reviewer-approved `official_derived_manual` cases can become official PASS after direct platform replay; `official_like_curated` and `internal_regression` remain non-official regression evidence.
- Recommended Phase 10F-4 scope: Static Physics Direct-Uploadable Fixture Pack Construction.
- No fixture official PASS was generated; no notebook, external script, benchmark extraction script, external API, network workflow, real LLM path, dependency installation, new adapter, adapter semantic change, Tool Registry semantic change, QueueWorkerRuntime change, AnalysisPlanRepository change, `/planner/jobs` change, PlanValidator relaxation, full viewer, WebGL renderer, Three.js, Brillouin-zone 3D, phonon, or advanced local environment classification was added.

## 2026-07-09 Phase 10F-2 Official Examples Coverage Gap Closure

- Planned closure for the official static physics coverage gap found in Phase 10F-1.
- Retained Phase 10F-1 status as `PARTIAL_PASS`: the benchmark pack is present and classified, but no direct-uploadable official static physics case exists for `structure.coordination_hist`, `structure.xrd`, or `structure.rdf`.
- Added the coverage-gap analysis, gap matrix, direct-uploadable fixture proposal, expected-contract authoring plan, and Phase 10F-3 next-scope prompt under `docs/phase10f/`.
- Recommended Phase 10F-3 scope: Static Physics Direct-Uploadable Fixture Pack Planning.
- No official static physics PASS claim was added; mapping-only, notebook-only, script-heavy, external-API, and future-scope cases remain non-PASS.
- No notebook, external script, benchmark extraction script, external API, network workflow, real LLM path, dependency installation, new adapter, adapter semantic change, Tool Registry semantic change, QueueWorkerRuntime change, AnalysisPlanRepository change, `/planner/jobs` change, PlanValidator relaxation, full viewer, WebGL renderer, Three.js, Brillouin-zone 3D, phonon, or advanced local environment classification was added.

## 2026-07-09 Phase 10F-1 Official Examples Direct Verification

- Audited the local official examples benchmark pack for direct static structure physics verification of `structure.coordination_hist`, `structure.xrd`, and `structure.rdf`.
- Benchmark pack status: present, 61 total cases, 2 `DIRECT_VERIFIED`, 20 `MAPPING_ONLY`, 27 `EXTRACTION_REQUIRED`, and 12 `FUTURE_SCOPE`; audit status `ok: true`.
- Applied a strict direct-uploadable gate requiring local uploadable input, no notebook/script/API/network/new dependency, bounded input size, deterministic artifact comparison, and a tool mapping to one of the three completed static physics tools.
- Found no direct-uploadable official example case for `structure.coordination_hist`, `structure.xrd`, or `structure.rdf`; no official static physics PASS claim was made.
- Recorded the two existing direct-verified official cases (`matpes_atomic_energies_csv` and `ward_metallic_glasses_csv_xz`) as unsupported for Phase 10F-1 because they are table/ML/composition cases, not static structure physics.
- Recorded structure-adjacent README/widget/Brillouin/phonon cases as mapping/future/extraction references only, not PASS.
- Added Phase 10F-1 verification docs under `docs/phase10f/official_examples_direct_verification/` and generated the Phase 10F-2 coverage-gap prompt.
- Recommended Phase 10F-2 scope: Official Examples Coverage Gap Closure.
- No new adapter, adapter semantic change, Tool Registry semantic change, Planner semantic change, QueueWorkerRuntime change, AnalysisPlanRepository change, `/planner/jobs` change, PlanValidator relaxation, full viewer, WebGL renderer, Three.js, phonon, notebook/script execution, external API workflow, real LLM path, artifact JS, or external URL loading was added.

## 2026-07-09 Phase 10F Static Structure Physics Closure

- Closed the Phase 10E static structure physics family at the implementation + browser/API evidence level.
- Completed static physics tools are `structure.coordination_hist`, `structure.xrd`, and `structure.rdf`.
- Verified closure across Tool Registry registration, strict params validation, deterministic static artifacts, Mock Planner routing, negative routing, browser/API evidence, no-JS/no-external-URL security posture, and CI.
- Added Phase 10F closure docs under `docs/phase10f/`, including the closure audit, next-scope decision matrix, and copyable Phase 10F-1 prompt.
- Recommended Phase 10F-1 scope: Official Examples Direct Verification for Static Structure Physics.
- No new adapter, full interactive 3D viewer, WebGL renderer, Three.js, Brillouin-zone 3D, phonon, advanced local environment classification, experimental fitting, notebook/script execution, external API workflow, runtime semantic change, real LLM path, artifact JS, or external URL loading was added.

## 2026-07-09 Phase 10E-8 RDF Browser/API Evidence

- Added browser/API evidence for `structure.rdf` under `docs/phase10e/browser_api_evidence/phase10e8_rdf/`.
- Verified two small periodic structure inputs through local FastAPI `/planner/jobs`, deterministic Mock Planner, persisted AnalysisPlan, QueueWorkerRuntime, Tool Registry validation, and adapter execution.
- Confirmed `rdf.json`, `rdf_plot.json`, `summary.md`, and `recipe.json` were generated with Phase 10E-7 schema versions, deterministic ordering, limits/warnings, and no-JS/no-external-URL security flags.
- Captured six real browser-rendered frontend screenshots with system Chrome and Playwright `executablePath`; the frontend shows the completed RDF job, summary/recipe previews, artifact gallery entries, and `structure.rdf` ToolCall.
- Negative routing evidence confirms XRD, coordination histogram, full viewer, WebGL, Brillouin-zone, phonon, experimental PDF fitting, neutron scattering refinement, Voronoi, and CrystalNN prompts did not misroute to `structure.rdf`.
- No new adapter, full 3D viewer, WebGL renderer, Three.js, phonon, advanced local environment classification, experimental fitting, notebook/script extraction, external API workflow, runtime semantic change, real LLM path, artifact JS, or external URL loading was added.

## 2026-07-09 Phase 10E-7 RDF Implementation

- Implemented `structure.rdf` as the third Phase 10E static structure physics adapter after coordination histogram and XRD.
- The adapter uses periodic `pymatgen Structure.get_all_neighbors(r_max)` distances, fixed radial bins, `number_density` shell-volume normalization, and ordered partial RDF pairs.
- Registered strict Tool Registry params for `r_max_angstrom`, `bin_width_angstrom`, `normalization`, `include_partial_pairs`, `max_partial_pairs`, `max_sites`, `max_bins`, `max_neighbors_total`, and `plot_kind`.
- Artifacts are static and deterministic: `rdf.json`, `rdf_plot.json`, `summary.md`, and `recipe.json`.
- Mock Planner now routes RDF / radial-distribution / pair-distribution prompts to `structure.rdf`; XRD prompts remain `structure.xrd`, coordination prompts remain `structure.coordination_hist`, and full viewer / WebGL / phonon / fitting prompts remain deferred.
- Added unit, fixture, registry, planner-routing, artifact-contract, persisted execution, and safety tests for the adapter.
- No browser/API evidence was added; Phase 10E-8 remains responsible for end-to-end evidence.
- No full 3D viewer, WebGL renderer, Three.js, Brillouin-zone 3D, phonon, advanced local environment classification, experimental fitting, notebook/script extraction, external API workflow, QueueWorkerRuntime semantic change, AnalysisPlanRepository semantic change, `/planner/jobs` semantic change, PlanValidator boundary change, new dependency, real LLM path, artifact JS, or external URL loading was added.

## 2026-07-08 Phase 10E-1 Coordination Histogram Implementation

- Implemented `structure.coordination_hist` as the first static structure physics adapter from Phase 10E planning.
- The adapter uses the existing Phase 10C/10D structure parsing path and a conservative deterministic `distance_cutoff` neighbor policy.
- Registered the tool through Tool Registry with a strict params schema for `neighbor_policy`, `cutoff_angstrom`, `max_sites`, `max_neighbors_per_site`, `include_site_details`, `group_by_element`, `include_pair_counts`, and `plot_kind`.
- Artifacts are static and deterministic: `coordination_hist.json`, `coordination_hist_plot.json`, `summary.md`, and `recipe.json`.
- Mock Planner now routes coordination-number / neighbor-count prompts to `structure.coordination_hist`; XRD, RDF, full viewer, WebGL, Brillouin-zone, phonon, Voronoi, and CrystalNN prompts remain deferred.
- Added unit, fixture, registry, planner-routing, artifact-contract, persisted execution, and safety tests for the adapter.
- No browser/API evidence was added; Phase 10E-2 remains responsible for end-to-end evidence.
- No XRD, RDF, full 3D viewer, WebGL renderer, Three.js, Brillouin-zone, phonon, notebook/script extraction, external API workflow, QueueWorkerRuntime semantic change, AnalysisPlanRepository semantic change, `/planner/jobs` semantic change, PlanValidator boundary change, new dependency, real LLM path, artifact JS, or external URL loading was added.

## 2026-07-07 Phase 10C-1 Lightweight Structure Adapter Implementation

- Implemented the lightweight structure adapter batch recommended by Phase 10C:
  `structure.summary`, `structure.lattice_summary`, `structure.spacegroup_summary`,
  `structure.composition_from_structure`, and `structure.preview_metadata`.
- Registered all five tools through the Tool Registry manifest, params schemas,
  adapter exports, and adapter class registry. Execution remains
  AnalysisPlan -> PlanValidator -> persisted plan/job -> QueueWorkerRuntime ->
  Tool Registry -> Adapter -> Artifact/Result provenance.
- Dependency decision: `pymatgen`, `spglib`, and `ase` are available in the
  current environment. Structure parsing uses pymatgen `Structure` where
  possible; space-group detection uses pymatgen/spglib when available and
  returns typed dependency/detection errors instead of fabricating symmetry.
- Supported input/resource forms for this phase are bounded to platform-passed
  structure objects or text/dict payloads: pymatgen Structure, pymatgen
  Structure dict/JSON, normalized structure dict, CIF text, POSCAR/CONTCAR text,
  and small structure collections. Adapters do not read arbitrary local paths.
- Added deterministic small structure fixtures and tests for CIF, POSCAR,
  normalized dict, malformed input, missing/invalid structure handling,
  deterministic artifacts, registry schemas, planner routing, persisted job
  execution, and the 3D-viewer future-scope boundary.
- Mock Planner now routes structure prompts before generic composition/table/viz
  routing, including summary, lattice, space group, composition extraction, and
  preview metadata prompts. Explicit 3D viewer prompts are not falsely routed to
  an implemented `structure.viewer_3d`; they use preview metadata with a future
  scope rationale when appropriate.
- Generated lightweight adapter evidence under `docs/phase10c/adapter_evidence/`.
  Evidence level is Tool Registry + Adapter execution only; browser/API evidence
  is intentionally deferred to Phase 10C-2.
- No real LLM was used. No QueueWorkerRuntime main semantics,
  AnalysisPlanRepository semantics, `/planner/jobs` main semantics, or Phase 9D
  live LLM gating behavior were changed.

## 2026-07-06 Phase 10C Lightweight Structure Adapter Planning

- Completed a docs-only planning pass for lightweight structure adapters on top of the Phase 10B-2 baseline (`4a5e780`).
- Added `docs/phase10c/phase10c_lightweight_structure_adapter_planning.md` as the canonical Phase 10C planning document.
- Added `docs/phase10c/phase10c_candidate_adapter_matrix.md` to separate lightweight structure summaries from advanced structure, physics, phonon, and Brillouin zone candidates.
- Added `docs/phase10c/phase10c1_lightweight_structure_adapter_implementation_prompt.md` as the follow-on implementation prompt for Phase 10C-1.
- Recommendation: Phase 10C-1 should implement `structure.summary`, `structure.lattice_summary`, `structure.spacegroup_summary`, `structure.composition_from_structure`, and `structure.preview_metadata`.
- Reasoning: lightweight structure metadata and summaries are lower risk than 3D viewers, XRD/RDF, coordination analysis, phonon plots, and Brillouin zone rendering because they can be deterministic JSON/Markdown/recipe artifacts with bounded parser dependencies and stable CI behavior.
- Official benchmark pack remains scoped: 61 total cases, 2 `DIRECT_VERIFIED`, 27 `EXTRACTION_REQUIRED`, 20 `MAPPING_ONLY`, 12 `FUTURE_SCOPE`, audit ok with 0 issues / 0 warnings. Structure-related official examples are currently mapping-only or future-scope, not direct PASS evidence.
- No adapter implementation, runtime behavior, QueueWorkerRuntime, AnalysisPlanRepository, `/planner/jobs`, PlanValidator security boundary, Tool Registry execution boundary, or live LLM behavior changed in this planning phase.

## 2026-07-06 Phase 10B Second Batch pymatviz Adapter Planning

- Completed a docs-only planning pass for the second pymatviz adapter batch on top of the Phase 10A-2 baseline (`65d0c80` / `phase10a2-browser-api-evidence-baseline`).
- Added `docs/phase10b/phase10b_second_batch_adapter_planning.md` as the canonical Phase 10B planning document.
- Added `docs/phase10b/phase10b_candidate_adapter_matrix.md` to separate composition, lightweight structure, advanced structure/physics, phonon, Brillouin zone, and later ML/materials adapter candidates.
- Added `docs/phase10b/phase10b1_composition_adapter_implementation_prompt.md` as the follow-on implementation prompt for Phase 10B-1.
- Recommendation: Phase 10B-1 should focus on composition visualization adapters: `composition.ptable_heatmap`, `composition.elements_hist`, `composition.chem_sys_treemap`, `composition.chem_sys_sunburst`, and `composition.formula_statistics`.
- Reasoning: composition visualization is closer to pymatviz's materials-informatics identity than the Phase 10A table/viz batch, while remaining lower risk than WebGL structure viewers, XRD/RDF, phonon, Brillouin zone, notebook extraction, or external API workflows.
- Official benchmark pack remains `PARTIAL_BENCHMARK_READY`: 61 total cases, 2 `DIRECT_VERIFIED`, 27 `EXTRACTION_REQUIRED`, 20 `MAPPING_ONLY`, 12 `FUTURE_SCOPE`, audit ok with 0 issues / 0 warnings.
- No adapter implementation, runtime behavior, QueueWorkerRuntime, AnalysisPlanRepository, `/planner/jobs`, Tool Registry execution boundary, or live LLM behavior changed in this planning phase.

## 2026-07-06 Phase 10A-2 Browser/API Evidence for First Batch Adapters

- Added project-local evidence under `docs/phase10a/browser_api_evidence/` for the Phase 10A-1 first-batch adapters.
- Verified six scoped official direct-case scenarios with evidence level `browser_api_artifact`: MatPES scatter, MatPES histogram, Ward distribution summary, Ward histogram, Ward correlation, and Ward composition summary.
- Each scenario has redacted API captures, downloaded platform artifacts, browser-rendered Phase 9C UI screenshots, execution logs, platform summaries, artifact manifests, and evidence manifests.
- Evidence totals: 6 PASS scenarios, 60 redacted API capture JSON files, 30 PNG screenshots, and 23 artifact files. Security scanning found no `sk-`, `Bearer`, `Authorization`, `MDI_LLM_API_KEY`, `api_key`, `access_token`, or `refresh_token` hits in the evidence directory.
- Fixed the `viz.scatter` and `viz.histogram` Plotly JSON artifact contract so `scatter.json` / `histogram.json` include top-level chart metadata required by the benchmark evidence while retaining nested Plotly figure payloads.
- Tightened Mock Planner routing so composition distribution prompts route to `composition.summary` before the generic histogram/distribution branch.
- No real LLM was used for Phase 10A-2 evidence. The default CI path remains real-LLM-free.
- Phase 8B persisted-plan exact execution, QueueWorkerRuntime, AnalysisPlanRepository, `/planner/jobs` validate/persist/enqueue semantics, and Phase 9D live LLM gating remain unchanged.
- Remaining boundaries: the other 59 official examples are not verified by this evidence phase; browser evidence is presentation/demo evidence and is not a default CI gate; multi-step DAG/data-dependency scheduling remains future work.

## 2026-07-06 Phase 10A-1 First Batch Adapter Implementation

- Implemented the first adapter batch for the two `DIRECT_VERIFIED` official pymatviz direct cases only: `matpes_atomic_energies_csv` and `ward_metallic_glasses_csv_xz`.
- Added registry-gated tools and adapters for `table.distribution_summary`, `viz.scatter`, `viz.histogram`, `viz.correlation`, and `composition.summary`.
- MatPES routing can now produce `viz.scatter` for PBE vs r2SCAN scatter prompts and `viz.histogram` for PBE/r2SCAN distribution prompts. MatPES `ml.basic_metrics` remains unchanged for explicit numeric comparison/error-metric prompts.
- Ward routing can now produce `table.distribution_summary`, `viz.histogram`, and `viz.correlation`. `composition.summary` is available only when a stable formula/composition field is present; it must not fabricate composition results.
- Updated shared schemas to include the `viz` ToolDomain and updated frontend results rendering so new plot/table/composition artifacts appear in the Phase 9C `结果与导出` tab without changing the top/left/main-tab layout.
- Added Phase 10A-1 adapter, manifest, planner-routing, persisted-plan execution, and frontend result-display tests.
- Phase 8B persisted AnalysisPlan execution, QueueWorkerRuntime, AnalysisPlanRepository, `/planner/jobs` validate/persist/enqueue semantics, and Phase 9D live LLM gating remain unchanged.
- Default CI still does not call a real LLM. No API keys or external network access are introduced by these adapters.
- Remaining boundaries: browser evidence for the new tools, full official suite execution, extraction-required examples, richer report generation, multi-step DAG/data-dependency scheduling, and additional pymatviz adapters.

## 2026-07-05 Phase 9D True LLM Live Verification

- Captured redacted live-provider evidence for the OpenAI-compatible Gemini path under `docs/llm-live-verification/phase9d/`: the provider returned AnalysisPlan JSON, the plan passed PlanValidator, persisted as an AnalysisPlan, bound through `jobs.plan_id`, loaded through QueueWorkerRuntime, and executed through Tool Registry + Adapter.
- Browser evidence shows the Phase 9C UI using the live OpenAI-compatible provider, a completed job, `plan.loaded` / `data.loaded` / `tool.completed` / `job.completed`, and metrics/report artifacts. The API key was read from user environment / SecretStore only and was not recorded in docs, events, artifacts, plans, or test output.
- Live testing found that LLM output can use wrong parameter aliases even when the selected tool is valid. PlanValidator now validates each step's `params` against the registered tool `paramsSchema` before persistence; prompt tool summaries now list allowed parameter names.
- Gemini/OpenAI-compatible compatibility was tightened by omitting `response_format` for `generativelanguage.googleapis.com`, because the endpoint returned HTTP 400 for that field.
- Final gated full-chain rerun passed with Gemini 3 Flash Preview through the OpenAI-compatible Gemini endpoint: `python -m pytest -q -m llm_integration` -> `1 passed, 165 deselected`. This verified live provider JSON -> PlanValidator -> persisted AnalysisPlan -> queued worker execution -> ToolCall/Artifact/Result.
- Gemini 2.5 Flash Lite was reachable but the full-chain test returned a safe provider-side HTTP 503 during one attempt; Gemini 3 Flash Preview is the Phase 9D verified Gemini model for the current evidence.
- The user-requested Antigravity model was checked through the same Gemini AI Studio OpenAI-compatible chat/completions path. The provider returned HTTP 400 with safe message "This model only supports Interactions API", so it is not usable for the current OpenAI-compatible provider path.
- Default CI remains real-LLM-free because it does not set `MDI_RUN_LLM_INTEGRATION`.
- Redaction scans over the Phase 9D evidence found no API key, auth token header, provider key env name, or key prefix leakage.
- Remaining boundaries: production KMS/envelope encryption, multi-step DAG/data-dependency scheduling, worker supervision/dead-letter policy, and broader pymatviz adapter coverage.

## 2026-07-05 Phase 9D LLM Configuration Path Repair

- Implemented the Phase 9D configuration-chain repair without running a live LLM: explicit UI/request `PlannerUserConfig` now wins over environment model/timeout/token/temperature settings, while env-only integration tests still read `MDI_LLM_*` / `OPENAI_*`.
- Added a no-network provider resolve path for the current UI configuration. It reports whether the current planner job configuration will use Mock Planner or an OpenAI-compatible live provider, whether the selected secret exists, the effective model, and a redacted status message.
- Updated the Planner workspace model status to use the current UI provider resolution instead of treating the default env provider status as the selected task provider.
- Added a gated full-chain live LLM test path that, when env is configured, uploads a tiny metrics CSV, requests a live OpenAI-compatible plan, persists the validated AnalysisPlan, runs the queued job, and verifies ToolCall/Artifact/Result provenance.
- The live test was not executed locally because live LLM env is not configured; the default run correctly skips it.
- No QueueWorkerRuntime, AnalysisPlanRepository, Tool Registry manifest, adapter implementation, migration, or `/planner/jobs` persistence/enqueue semantics changed.

## 2026-07-05 Phase 9C Browser Visual QA and Official Direct Re-verification

- Ran a real browser-controlled Phase 9C visual QA against the local workspace at `http://127.0.0.1:3000` with API `http://127.0.0.1:8000`, local SQLite/runtime queue, local ArtifactStorage, and Mock Planner only.
- Saved Phase 9C browser QA screenshots under `docs/ui-redesign/phase9c_browser_qa/`:
  `01_workspace_default.png`, `02_data_context_viewer.png`, `03_agent_process_tab.png`,
  `04_chat_plan_tab.png`, `05_results_export_tab.png`, and `06_developer_mode.png`.
- Verified the UI visually follows the Phase 9C baseline: top global dataset/model/job bar, left data-context viewer, and exactly one active main tab among `Agent 过程`, `对话与 Plan`, and `结果与导出`. No independent right result panel, right Agent panel, or bottom result tabs were used.
- Re-deleted and regenerated fresh Desktop evidence for the two official direct-uploadable pymatviz cases using the Phase 9C UI:
  - `matpes_atomic_energies_csv`: dataset `dataset_0004`, profile `profile_dataset_0004_v1`, job `job_c6e8034a138f469da0d72f2e`, plan `plan_202acca0e0c74d5fa7a0f794`, planHash `a205a4de5017e47c47358d1f97ca919d5d5db926920520a3430468c7867e0dfe`, tool `ml.basic_metrics`, artifact `metrics.json`, verdict `PASS_WITH_CURRENT_PLATFORM_SCOPE`.
  - `ward_metallic_glasses_csv_xz`: dataset `dataset_0005`, profile `profile_dataset_0005_v1`, job `job_3c6b5797a14e4732bf19c64d`, plan `plan_017cf930f0224728bb3850b5`, planHash `4c16e617ea4c6efc727f81d7b0915fe6ee6e92191b98ae41a558713c1bbde9c2`, tool `table.numeric_summary`, artifacts `numeric_summary.json`, `summary.md`, and `recipe.json`, verdict `PASS_WITH_CURRENT_PLATFORM_SCOPE`.
- The official example evidence pack was updated at `C:\Users\86182\Desktop\pymatviz_official_examples_test_suite`, but that Desktop evidence pack is not part of the project Git commit. Only the Phase 9C QA screenshots under `docs/ui-redesign/phase9c_browser_qa/` are intended for commit.
- True LLM was not used; no API key was entered or captured.

## 2026-07-05 Phase 9C UI/UX Redesign Implementation Baseline

- Implemented the Phase 9C frontend layout in `apps/web/app/components/PlannerWorkbench.tsx`: top `GlobalContextBar`, resizable/collapsible left `DataContextViewer`, and a main workspace with exactly three mutually exclusive tabs.
- Top bar now opens dataset/profile and model/provider dialogs. Dataset dialog supports dataset selection, manual IDs, demo dataset loading, upload, and profile generation. Model dialog supports Mock/OpenAI-compatible mode, provider preset/config fields, Secret selection/creation/deletion, and safe provider test.
- Left `DataContextViewer` is now a viewer rather than a control column. It adapts rendered profile content for table, structure, archive/object, and unsupported/partial states, and supports collapse plus drag resize.
- Main workspace tabs are `Agent 过程`, `对话与 Plan`, and `结果与导出`; only the active tab is rendered. There is no independent right status/result column and no bottom result tab strip in the Phase 9C implementation.
- Conversation uses selectable chunks for user request, Plan Preview, validation, run status, and result references. Chunk selection drives the result context used by `结果与导出`.
- Results/export tab now owns report/recipe summary, 3D material result placeholder, metrics result, table/numeric summary, Artifact Gallery, ToolCalls, and export/download controls. It shows `请选择一个分析步骤或结果 chunk` when no chunk is selected.
- Agent process tab shows structured JobEvents including `plan.loaded`, `data.loaded`, `tool.started`, `tool.completed`, and `job.completed`, with safe payload disclosure and persisted-plan/Tool Registry/no-fallback provenance.
- Updated frontend tests to cover the strict top/left/main-tab layout, dataset/model top dialogs, Secret no-leak behavior, left data viewer, mutually exclusive main tabs, Agent process evidence, results/export evidence, validation-failure no plan/job/enqueue, and no broad `Not available yet` UI.
- Phase 8B/9A execution boundaries remain unchanged: no backend route, QueueWorkerRuntime, AnalysisPlanRepository, Tool Registry, Adapter, provider security, migration, or CI behavior was changed.

Verification so far:

- `npm run typecheck` in `apps/web`: passed.
- `npm test` in `apps/web`: 6 passed.
- `npm run build` in `apps/web`: passed.
- `uv lock --check`: passed.
- `python -m pytest tests/test_phase7_llm_planner.py -q`: 32 passed.
- `python -m pytest tests/test_phase8b_persisted_plan_queue.py -q`: 9 passed / 1 skipped locally.
- `python -m pytest tests/test_phase8c_planner_read_api.py -q`: 2 passed.
- `python -m pytest tests/test_phase9b_demo_workspace_api.py -q`: 15 passed.
- `python -m pytest -q`: 138 passed / 21 skipped.
- `git diff --check`: passed with Windows line-ending warnings only.

## 2026-07-05 Phase 9C UI/UX Redesign Docs Baseline

- Updated the frontend design baseline to the user-specified AI assistant workspace layout: top global dataset/model context bar, collapsible/resizable left data-context viewer, and a main workspace with exactly three mutually exclusive tabs.
- The three main tabs are now canonical: `Agent 过程`, `对话与 Plan`, and `结果与导出`. The independent right-side Result Inspector, legacy right Agent panel, and bottom result panel are no longer recommended implementation targets.
- Results are now documented as part of the main `结果与导出` tab: report summary, 3D material view, metrics, table/numeric summary, Artifact Gallery, Recipe/provenance, report export, and artifact download all live there.
- Added UI-only view model names for `MainWorkspaceTab`, `ConversationChunkView`, `DataContextViewerState`, and `SelectedResultContext` in the shared schema document without changing backend persistence schema.
- Preserved core execution boundaries: LLMs still produce JSON AnalysisPlans only; valid plans still pass PlanValidator, persist as AnalysisPlans, bind through jobs, load in QueueWorkerRuntime, and execute through Tool Registry + Adapter.
- This round is docs-only. No API, Worker, Tool Registry, Adapter, frontend implementation code, tests, migrations, or CI configuration were changed.

## 2026-07-05 Phase 9B Official Direct Examples Semantic Refinement

- Added a minimal `table.numeric_summary` MVP tool and adapter for semantically correct table statistics on official direct-uploadable tabular examples.
- Ward metallic glasses now routes through `table.numeric_summary` for independent numeric column summaries (`D_max`, `dTx`) plus categorical summaries (`material_id`, `composition`, `gfa_type`) instead of treating `D_max` and `dTx` as target/prediction regression columns.
- MatPES remains routed through `ml.basic_metrics` with DataProfile-bound `targetColumn=PBE` and `predictionColumn=r2SCAN`; fresh browser evidence no longer contains the stale `y_true` / `y_pred` prompt.
- Re-generated fresh browser evidence for `matpes_atomic_energies_csv` and `ward_metallic_glasses_csv_xz` after deleting each case's old `results/` directory. Both runs used Mock Planner only, created fresh persisted AnalysisPlans, loaded plans through QueueWorkerRuntime, emitted `plan.loaded` / `data.loaded` / `tool.completed` / `job.completed`, and saved API responses, artifacts, screenshots, and summaries.
- Phase 8B/9A boundaries remain unchanged: no QueueWorkerRuntime redesign, no AnalysisPlanRepository change, no `/planner/jobs` persistence/enqueue bypass, no real LLM call, and no execution outside Tool Registry + Adapter.

## 2026-07-04 Phase 9B Official MatPES Example Blocker Repair

- Fixed the blocker found by the official pymatviz examples evidence pack: `matpes_atomic_energies_csv` uploaded and profiled correctly, but Mock Planner hard-coded `targetColumn=y_true` / `predictionColumn=y_pred`, causing `ml.basic_metrics` to fail for the official MatPES columns `element`, `PBE`, and `r2SCAN`.
- Updated `MockLLMProvider` so default mock plans bind `ml.basic_metrics` params from the real `DataProfile`: target/prediction role columns win first, and tables with no explicit roles fall back to the first two numeric columns. The provider still emits only structured AnalysisPlan JSON; it does not execute code or bypass validation.
- Added a regression proving a MatPES-style uploaded CSV (`element,PBE,r2SCAN`) goes through `/planner/jobs`, persists an AnalysisPlan with `targetColumn=PBE` and `predictionColumn=r2SCAN`, runs through QueueWorkerRuntime, executes one real `ml.basic_metrics` ToolCall, creates one metrics artifact, and reaches `completed`.
- Re-ran the failed browser evidence case with the full official MatPES CSV: 89 rows, columns `element`, `PBE`, `r2SCAN`, `job_b81c14bde6c3479599e19312`, `plan_4117360927074c8fad3ec8f3`, `planHash=ce6322d32f52b25913e9d4ae14aa535eb91704648eb5ea3ca684db0e8620bef8`, one completed ToolCall, one `metrics_json` artifact, and timeline events `plan.loaded`, `data.loaded`, `tool.started`, `artifact.ready`, `tool.completed`, `job.completed`.
- Evidence pack updated under `C:\Users\86182\Desktop\pymatviz_official_examples_test_suite`: `matpes_atomic_energies_csv` now has four browser screenshots and `platform_result_summary.md` is PASS. The full 61-case official suite is still not claimed complete; this repair verifies the previously failed blocker.
- Verification: `uv lock --check` passed; Phase 7 targeted 32 passed; Phase 8B targeted 9 passed / 1 skipped locally; Phase 8C targeted 2 passed; Phase 9B targeted 14 passed; backend full 136 passed / 21 skipped; frontend `npm test` 6 passed; frontend typecheck passed; frontend build passed after stopping the old dev server that held `.next/trace`.
- Remaining follow-up: continue the rest of the official examples suite separately.

## 2026-07-04 Phase 9B Browser + Durable Worker Resolver Closure

- Completed the browser click-through that was previously blocked by the browser native bridge. The in-app browser now loaded `http://127.0.0.1:3000`, loaded the backend demo dataset, created and ran a Mock Planner job, and showed `completed` status with persisted-plan provenance.
- Browser evidence: the UI displayed `Demo metrics dataset`, profile columns `formula, y_true, y_pred`, `planId`, `planHash`, `jobs.plan_id -> analysis_plans.id`, `Loaded from persisted AnalysisPlan`, `Executed through Tool Registry + Adapter`, `No deterministic fallback used`, `plan.loaded`, `data.loaded`, `tool.started`, `artifact.ready`, `tool.completed`, and `job.completed`.
- Browser result panels were verified: Artifact Gallery showed one `metrics.json` artifact, Report / Recipe Summary showed a system-generated summary and reproducibility fields, and Tool Calls showed one completed `ml.basic_metrics` call with `stepId=llm_step_1` and plan provenance.
- Added a durable worker object-store resolver for out-of-process queue workers. It rebuilds `ml_table`, `structures`, and `formulas` from persisted dataset `metadata.normalizedExports` plus ArtifactStorage, instead of relying on API-process memory.
- Added settings-driven worker runtime construction for `run_queued_job(job_id)`: it now builds SQLAlchemy repositories from `DATABASE_URL`, artifact storage from `MDI_ARTIFACT_BACKEND` / `MDI_ARTIFACT_ROOT`, and the durable resolver before executing `QueueWorkerRuntime.handle_job(job_id)`.
- Connected the same durable resolver into the PostgreSQL planner runtime path so local PostgreSQL/in-memory-queue development and Redis enqueue paths use the same dataset-object loading seam.
- Added `MDI_ARTIFACT_ROOT` config support and a shared `create_artifact_storage_from_settings()` helper.
- Added a regression proving `run_queued_job(job_id)` can run as a separate settings-driven worker against a persisted SQLite repository and local ArtifactStorage: it reconstructs `ml_table` from normalized exports, loads the persisted AnalysisPlan, executes exactly one real `ml.basic_metrics` adapter call, emits `data.loaded` / `plan.loaded`, writes one artifact, and completes the job.
- Verification: browser UI assertions passed with no console errors and no `Not available yet` in the rendered page; Phase 9B targeted passed with 13 tests; Phase 9B + Phase 8B targeted passed with 22 passed / 1 skipped; Phase 7 + Phase 8C targeted passed with 34 tests; backend full passed with 135 passed / 21 skipped; frontend `npm test` passed with 6 tests; frontend typecheck and build passed.
- Live true-LLM verification is still not claimed; no API key was entered during the browser run and no external LLM call was made.
- Remaining production boundary is narrowed: worker-side durable loading is implemented, but a fully production upload service that writes normalized exports directly through SQL/MinIO rather than the Phase2 in-memory runtime remains future hardening.

## 2026-07-04 Phase 9B Runtime Data Binding Follow-up

- Closed the practical demo gap found during full Planner workspace testing: in the local in-memory development path, `enqueue=true` created and enqueued a planner job but no separate worker drained the queue, so the UI could remain in the queued state even though the plan/job APIs were valid.
- Added a narrow local-only auto-drain path for `/planner/jobs`: when the app is using the default in-memory repositories/runtime and no Redis queue URL is configured, the planner route enqueues the job and then immediately runs `QueueWorkerRuntime.handle_job(job_id)`. This does not affect the PostgreSQL/Redis production path, injected test runtimes, or Phase 8B service-backed queue semantics.
- Added dataset object binding from the Phase2 runtime into `QueueWorkerRuntime`. The worker can now resolve uploaded/demo dataset objects by `dataset_id`, inject them as the execution `object_store`, and emit a `data.loaded` JobEvent before loading the persisted plan.
- Added Phase2 runtime accessors for the real uploaded `DataProfile` and normalized dataset object store. Planner preview/jobs now prefer the real Phase2 profile instead of a minimal synthetic profile when the dataset exists.
- Tightened planner validation for executable uploaded datasets: ML plans must bind `ml_table`, structure plans must bind `structures`, and composition plans must bind `formulas` when those normalized objects exist. Missing or unresolved inputRefs are rejected before any AnalysisPlan persistence, Job creation, or enqueue.
- Updated the planner prompt to describe the normalized inputRef conventions (`ml_table`, `structures`, `formulas`) so real OpenAI-compatible providers are steered toward executable plans without relying on prompt text as a security boundary.
- Added regression coverage proving an uploaded CSV dataset can create an enqueued local planner job, auto-run through the persisted AnalysisPlan path, produce exactly one `ml.basic_metrics` ToolCall, emit `data.loaded`/`plan.loaded`, create an artifact/result, and reach `completed`.
- Added regression coverage proving a valid-looking plan with missing `inputRefs` is rejected for an uploaded dataset and creates no plan, no job, and no enqueue.
- Reorganized supported pymatviz sample cases under `C:\Users\86182\Desktop\pymatviz-web-test-cases`, with each case split into `raw_data/` and `results/`. Four true data samples were evaluated successfully through the platform path: MatPES CSV metrics, MP structure JSON, experimental Bi2Zr2O7 CIF, and MP Zr2Bi2O7 CIF.
- Verification for this follow-up: Phase 9B API targeted passed with 12 tests; Phase 8B targeted passed with 9 passed / 1 skipped locally; Phase 7 + Phase 8C + Phase 9B targeted passed with 46 tests; backend full passed with 134 passed / 21 skipped; frontend `npm test` passed with 6 tests; frontend typecheck and build passed after restarting the old dev server that held `.next/trace`.
- Post-restart API smoke verified CORS preflight, `/health/runtime`, provider APIs, demo dataset creation, and `/planner/jobs` local enqueue execution. A demo planner job returned `enqueued=true`, `executed=true`, status `completed`, exactly one ToolCall, one artifact, and a completed result.
- Browser plugin control was unavailable in this Codex environment after restart, so the final UI click-through was not claimed. Verification is based on API E2E, frontend tests, and backend tests.

## 2026-07-04 Phase 9B Frontend/API Follow-up

- Re-audited the Planner workspace API calls against backend route registration after browser logs showed `OPTIONS ... 405 Method Not Allowed`.
- Confirmed the affected API routes existed; the failure was missing CORS preflight handling for cross-port browser access, not missing GET/POST implementations.
- Added FastAPI `CORSMiddleware` with configurable local/demo origins and coverage for the Phase 9B workspace routes.
- Hardened `/health/runtime` so runtime status is based on safe light probes where configured instead of static configuration inference only. Failed database, Redis, or MinIO probes return `unknown` with class-level safe reasons and no credential-bearing URLs or keys.
- Tightened `/planner/jobs` validation-failure behavior so rejected raw plans are not returned in the response. Invalid plans still create no AnalysisPlan, no Job, and no enqueue, and now also avoid echoing credential-like params.
- Completed the Phase 9B i18n cleanup follow-up by moving remaining user-facing Chinese labels from `PlannerWorkbench.tsx` into message dictionaries and adding English-mode assertions.
- Verification after the follow-up: `python -m pytest tests/test_phase9b_demo_workspace_api.py -q` passed with 10 tests; Phase 7 targeted passed with 32 tests; Phase 8B targeted passed with 9 passed / 1 skipped locally; Phase 8C targeted passed with 2 tests; backend full passed with 132 passed / 21 skipped; frontend `npm test` passed with 6 tests; frontend `npm run typecheck` and `npm run build` passed.

## 2026-07-04 Phase 9B Demo-ready AI Planner Workspace

- Upgraded the Planner workspace from an engineering/debug view into a demo-ready product workspace while preserving the Phase 8B persisted-plan execution contract and the Phase 9A gated provider safety boundary.
- Added a default `zh-CN` frontend i18n layer with an English toggle. The main workspace now uses localized labels, empty states, error guidance, timeline labels, provider/health labels, artifact labels, and report/recipe labels instead of broad `Not available yet` placeholders.
- Added a productized Planner layout: top runtime/status strip, left data/provider controls, central prompt/plan/run area, right health/provenance/timeline area, and bottom tabs for result overview, artifact gallery, report/recipe summary, tool calls, and developer audit.
- Added API-backed runtime health, dataset detail, demo dataset/profile, provider catalog/status/test, and extended Secret UX support. The demo dataset/profile path is generated through the backend Phase2 runtime, not faked in the frontend.
- Added `LLMProviderSettingsPanel` behavior for mock vs OpenAI-compatible modes, OpenAI/DeepSeek/custom presets, Secret save/list/delete, and safe provider connection tests that use `secretId` server-side. API keys are not stored in localStorage/sessionStorage and are cleared from the input after save.
- Added a Chinese Error Explainer and validation failure UX that clearly states: no AnalysisPlan was saved, no Job was created, and nothing was enqueued.
- Added user/developer mode layering. User mode shows task-oriented plan/result summaries; developer mode exposes raw AnalysisPlan JSON, JobEvents, ToolCalls, Artifacts, API responses, `planId`, `planHash`, and storage/provenance identifiers.
- Productized results: Artifact Gallery is grouped by chart, JSON metrics, table, structure, report file, and other; Report/Recipe Summary is a separate system-generated summary tied to dataset/profile/AnalysisPlan/tool calls/artifacts/provenance.
- Added Phase 9B backend tests for runtime health, demo dataset/profile, provider catalog/status/test, Secret list no plaintext, provider error redaction, and planner validation failure no plan/job/enqueue.
- Added Phase 9B frontend tests for default Chinese rendering, language switch, region-specific empty states, demo dataset loading, profile summary, provider settings, Secret UX no key leakage, provider test success/failure, SSE timeline, artifact grouping, report/recipe summary, developer audit, and validation-failure no plan/job/enqueue.
- Local verification before commit: `uv lock --check` passed; Phase 7 targeted 32 passed; Phase 8B targeted 9 passed / 1 skipped locally; Phase 8C read API targeted 2 passed; Phase 9B API targeted 7 passed; backend full 129 passed / 21 skipped; frontend `npm test` 6 passed; `npm run typecheck` passed; `npm run build` passed.
- Live LLM verification is still not claimed; no `MDI_RUN_LLM_INTEGRATION=1` live-provider run was executed in this Phase 9B work.
- Remaining boundaries after Phase 9B: production secret encryption/KMS, multi-step DAG/data-dependency execution, worker supervision/dead-letter policy, advanced material viewer polish, and live true-LLM verification when env is explicitly configured.

## 2026-07-03 Phase 9A True LLM Provider Gated Integration

- Added a gated OpenAI-compatible LLM provider path for planner generation. The default planner path remains `MockLLMProvider`; real network calls require explicit `provider="openai_compatible"` or `MDI_LLM_PROVIDER=openai_compatible`.
- OpenAI-compatible provider configuration is resolved at call time from `MDI_LLM_BASE_URL`, `MDI_LLM_API_KEY`, `MDI_LLM_MODEL`, `MDI_LLM_TIMEOUT_SECONDS`, `MDI_LLM_MAX_TOKENS`, and `MDI_LLM_TEMPERATURE` (with legacy `OPENAI_*` fallbacks for compatibility).
- Provider outputs still parse to JSON first and then pass through the existing strict `PlanValidator`; invalid schema, non-JSON completion, unknown/non-MVP tools, duplicate/empty steps, and credential-like params remain rejected before any plan/job/queue mutation.
- `/planner/jobs` keeps the Phase 8B persisted-plan contract: validation success persists the exact validated `AnalysisPlan`, creates a `job.plan_id` binding, and optionally enqueues only `job_id`; validation/provider failure returns no `plan_id`, no `job_id`, and no enqueue.
- Safe provider errors now cover missing key, timeout, network failure, HTTP 401/429/5xx, and malformed provider response without exposing API keys or raw environment details. Raw prompt/completion is not persisted to `analysis_plans`, JobEvents, Artifacts, or Results.
- Added fake-transport tests for OpenAI-compatible success, markdown-fenced JSON, non-JSON completion, HTTP errors, timeout, missing key, default no-network behavior, provider validation failure no-op, and valid provider output entering the persisted-plan path.
- Added a gated `llm_integration` pytest marker and live test. It only runs when `MDI_RUN_LLM_INTEGRATION=1` and required `MDI_LLM_*` env vars are present; otherwise it skips with a clear reason. Default CI does not require or call a real LLM.
- Local verification: `uv lock --check` passed; `python -m pytest tests/test_phase7_llm_planner.py -q` passed with 32 tests; `python -m pytest tests/test_phase8b_persisted_plan_queue.py -q` passed with 9 passed / 1 skipped; `python -m pytest tests/test_phase8c_planner_read_api.py -q` passed with 2 tests; `python -m pytest -q` passed with 122 passed / 21 skipped; `npm ci`, `npm test`, `npm run typecheck`, and `npm run build` passed in `apps/web`.
- Local live LLM verification was not run because `MDI_RUN_LLM_INTEGRATION` and provider credentials are not configured. `python -m pytest -q -m llm_integration` skipped 1 test and made no external LLM call.
- Local machine has no Docker CLI, so service-backed PostgreSQL + Redis + MinIO integration remains CI-backed for this phase until the Phase 9A commit is pushed.
- Remaining boundaries after Phase 9A: production secret encryption/KMS, multi-step DAG/data-dependency execution, worker supervision/dead-letter policy, and advanced material viewer polish.

## 2026-07-03 Phase 8C-P1 Frontend Planner UX Compliance Closure

- Closed the Phase 8C P1 docs-compliance gaps without entering Phase 9 and without changing QueueWorkerRuntime, AnalysisPlanRepository, or the core `/planner/jobs` validate/persist/enqueue semantics.
- Added an EventSource-backed planner timeline path using the read-only SSE endpoint `/planner/jobs/{job_id}/events/stream`. The UI still keeps polling as a fallback, but the primary timeline transport now uses persisted JobEvents and highlights `plan.loaded`.
- Added an independent `Report / Recipe Summary` panel. Artifact gallery is now separate from report/result/recipe summary; the summary panel displays result summary, report artifacts, recipe artifacts, artifact references, `planId`, `planHash`, and persisted-plan provenance.
- Upgraded the Planner workbench data context entry from raw IDs only to an API-backed Dataset/Profile selector using existing `/datasets` and `/datasets/{dataset_id}/profile` reads, while preserving manual ID fallback and avoiding fake dataset/profile records.
- Added read-only SSE replay support for planner JobEvents. The endpoint replays persisted events only; it does not mutate jobs/plans, enqueue work, execute tools, or call deterministic fallback planning.
- Frontend tests now cover EventSource/SSE timeline behavior, Report/Recipe Summary rendering, Dataset/Profile selector behavior, validation-failure no-save/no-job/no-enqueue semantics, loading state, and API error state.
- Local verification for this closure: `uv lock --check` passed; `python -m pytest tests/test_phase8c_planner_read_api.py -q` passed with 2 tests; `python -m pytest tests/test_phase8b_persisted_plan_queue.py -q` passed with 9 passed / 1 skipped; `python -m pytest -q` passed with 112 passed / 20 skipped; `npm test` passed with 5 frontend tests; `npm run typecheck` and `npm run build` passed in `apps/web`.
- Phase 8C-P1 implementation commit `4d0c241` passed GitHub Actions run `28664159687`: Unit Tests, Frontend Typecheck & Build, and Service-backed Integration all succeeded. The integration job reported 19 passed, 0 skipped, 0 failed.
- Phase 8C-P1 status: PASS / compliance closure accepted after CI-backed verification.
- Remaining boundaries are unchanged: true LLM integration, advanced multi-step DAG/data-dependency execution, production secret encryption, worker supervision/dead-letter policy, and advanced material viewer polish.

## 2026-07-03 Phase 8C Frontend Planner UX Update

- Phase 8B is the frozen baseline for this work: final freeze commit `03d1915` (`Record phase 8B acceptance freeze`) after Phase 8B code commits `75386cf`, `9b62fa1`, `336fd8b`, and `962c429`; GitHub Actions run `28637798200` succeeded.
- Added a real frontend Planner workbench entry point instead of the previous static shell. Users can enter `projectId`, dataset/profile identifiers, a natural-language analysis request, and choose whether to enqueue the planner job.
- Added a typed frontend planner API client for `POST /planner/jobs` plus read-only planner detail endpoints for persisted AnalysisPlan, job detail, JobEvents, ToolCalls, Artifacts, and result summary.
- Added minimal read-only backend planner endpoints under `/planner/...` so the frontend can display persisted-plan provenance without mutating plans/jobs, enqueueing work, or triggering execution.
- The success UI now shows the validated persisted plan preview, `job_id`, `plan_id`, backend `plan_hash`, `job.plan_id -> analysis_plans.id`, step count, `stepId`, `toolId`, validation status, and plan source.
- The provenance UI now displays persisted-plan binding, `plan.loaded` JobEvent when present, ToolCall `planId`/`planHash`, Artifact `planId`/`planHash`, Result `planId`/`planHash`, and the statements "Loaded from persisted AnalysisPlan", "Executed through Tool Registry + Adapter", and "No deterministic fallback used" only when backed by returned API data.
- The validation failure UI now clearly states: "Plan validation failed", "No AnalysisPlan was saved", "No Job was created", "Nothing was enqueued", and "Please fix the request and try again"; it clears job state and does not start status polling.
- No true LLM integration, multi-step DAG execution, production secret encryption, QueueWorkerRuntime redesign, AnalysisPlanRepository redesign, or Tool Registry redesign was introduced.
- Local verification for the Phase 8C implementation: `uv lock --check` passed; `python -m pytest tests/test_phase8c_planner_read_api.py -q` passed with 2 tests; `python -m pytest tests/test_phase8c_planner_read_api.py tests/test_phase8b_persisted_plan_queue.py -q` passed with 11 passed / 1 skipped; `python -m pytest -q` passed with 112 passed / 20 skipped; `npm ci`, `npm test`, `npm run typecheck`, and `npm run build` passed in `apps/web`.
- Phase 8C implementation commit `9967c5b` passed GitHub Actions run `28646226271`: Unit Tests, Frontend Typecheck & Build, and Service-backed Integration all succeeded. The integration job reported 19 passed, 0 skipped, 0 failed.
- Phase 8C status: PASS / baseline frozen after CI-backed verification.
- Remaining boundaries after this update: true LLM integration, advanced multi-step DAG/data-dependency execution, production secret encryption, worker process supervision/dead-letter policy, and deeper material-specific viewer polish.

## 2026-07-03 Phase 8B Persisted Plans + Queue Worker Update

- Added PostgreSQL-backed `analysis_plans` persistence and `jobs.plan_id` linkage through Alembic revision `0002_phase8b_plans`.
- Added `AnalysisPlanRepository` to both in-memory and SQLAlchemy repository bundles, including `save_plan`, `get_plan`, `get_plan_for_job`, `attach_plan_to_job`, AnalysisPlan JSON round-trip, canonical SHA-256 `plan_hash`, and credential-key rejection before persistence.
- Upgraded `POST /planner/jobs` to validate first, persist the exact validated `AnalysisPlan`, create a Job linked by `plan_id`, and optionally enqueue only `job_id`; it no longer synchronously executes in the planner route.
- Upgraded `QueueWorkerRuntime.handle_job(job_id)` so the main path loads `job.plan_id`, reconstructs the persisted `AnalysisPlan`, executes exactly `plan.steps`, and writes ToolCall, JobEvent, Artifact, and completed Job status with `planId`/`planHash` provenance.
- Preserved explicit fallback only for dev/test jobs without a persisted plan. When `plan_id` exists, persisted plan loading wins and `build_phase2_plan` is not used.
- Core evidence: `tests/test_phase8b_persisted_plan_queue.py` proves persisted 1-step plan -> exactly 1 ToolCall, `toolId=ml.basic_metrics`, `stepId=llm_step_1`, Artifact generated, `plan.loaded` JobEvent includes `planId`/`planHash`, and Job reaches `completed`. The targeted suite also covers the real `ml.basic_metrics` adapter path without a fake executor.
- Verification: `uv lock --check` passed; Phase 8B targeted 9 passed / 1 skipped; Phase 8A 11 passed; Phase 7 22 passed; backend full 110 passed / 20 skipped; frontend `npm ci`, `npm run typecheck`, and `npm run build` passed.
- Local machine has no Docker CLI, so service-backed Phase 8B integration could not be run locally. GitHub Actions run `28631817086` on Phase 8B code acceptance commit `962c429` passed all three jobs; the service-backed PostgreSQL + Redis + MinIO job reported 19 passed, 0 skipped, 0 failed, including the Phase 8B persisted-plan queue test.
- Phase 8B acceptance: PASS / frozen. Phase 8C frontend Planner UX may start next, but true LLM integration, multi-step DAG/data-dependency execution, production secret encryption, and worker process supervision/dead-letter policy remain out of scope.
- Remaining boundaries after Phase 8B: true LLM integration, frontend Planner UX (Phase 8C), multi-step DAG/data-dependency execution, production secret encryption, worker process supervision/dead-letter policy.

## 2026-06-27 Phase 8A LLM Plan Execution Bridge Update

- Closed the largest Phase 7 boundary: validated LLM AnalysisPlans now actually execute, instead of being discarded in favor of the deterministic plan.
- `Phase2ProductRuntime.create_job` gained two parameters: `analysis_plan` (use this EXACT validated plan instead of `build_phase2_plan`) and `execute` (False = planned-only, no ToolCalls run).
- `POST /planner/jobs` now: generates plan → validates → on success creates a job that executes the EXACT validated LLM plan; added an `execute` flag (default False = planned, True = run). Response includes `plan_source` and `executed`.
- The runtime execution loop was unchanged — it already iterated `plan.steps` through Tool Registry + Adapter (`run_tool_call_job`). Only the plan _source_ changed.
- MockLLMProvider's plan now references the conventional `ml_table` normalized object so the validated plan is executable end-to-end (no plan mutation/auto-repair by the bridge).
- Deterministic `build_phase2_plan` preserved as fallback: when no `analysis_plan` is provided, create_job uses it (Phase 2/3 product loop unchanged).
- **Key acceptance evidence**: `test_runtime_executes_exact_provided_plan_one_tool_call` proves a 1-step LLM plan produces EXACTLY 1 ToolCall (`ml.basic_metrics`, stepId `llm_step_1`), NOT the deterministic 5 ToolCalls. `test_runtime_deterministic_fallback_when_no_plan` proves fallback still works.
- Added `tests/test_phase8a_plan_execution.py` (11 tests). All execution still goes through Tool Registry + Adapter; unknown/V1/V2/invalid plans still rejected before job creation (Phase 7 validator unchanged).
- Baseline-freeze hardening added 4 tests covering exact-plan execution side effects: produces a `metrics_json` artifact, emits `tool.started`/`tool.completed`/`artifact.ready`/`plan.generated` events, job status reaches `completed`, and `execute=False` yields zero ToolCalls + no tool artifact + no tool events.
- Verification: backend 101 passed, 19 skipped, 0 failed; Phase 7 targeted 22 passed; frontend typecheck+build passed; uv lock + git diff clean.
- **Remaining boundary**: execution uses the in-memory `Phase2ProductRuntime` (synchronous local loop). Wiring the validated plan into the Redis `QueueWorkerRuntime` + PostgreSQL plan persistence is still future work (recorded in OPEN_QUESTIONS).

## 当前阶段

Phase 8A: LLM Plan Execution Bridge — **通过 (PASS) / baseline frozen**。validated LLM plan 现在真正执行（1-step → 恰好 1 ToolCall，非 deterministic 5），并验证了 Artifact/JobEvent/completed status 副作用 + execute=False 零 ToolCall。deterministic fallback 保留。backend 101 passed / 19 skipped / 0 failed。剩余边界：QueueWorkerRuntime + PostgreSQL plan persistence 待后续。

## 2026-06-27 Phase 7 LLM JSON Planner + BYOK Secret Management Update

- Implemented LLMPlannerProvider abstraction with 3 implementations:
  - MockLLMProvider: deterministic, no API key, returns valid AnalysisPlan for testing
  - OpenAICompatibleProvider: OpenAI/DeepSeek compatible with fake-transport support for testing
  - DeterministicPlannerAdapter: wraps existing build_phase2_plan() as fallback
- Added PlanValidator (strict mode, no auto-repair) in `packages/tool-registry/mdi_tool_registry/plan_validator.py`
  - Validates: JSON schema, step_id uniqueness, tool_id in ToolRegistry, MVP-only stage, no credentials in params, known artifact types, empty steps rejection, V1/V2 tool rejection
- Added planner prompt template in `services/llm/mdi_llm/planner_prompt.py` (JSON-only output, tool-aware system prompt)
- Added Planner API routes: POST /planner/preview, /planner/validate, /planner/jobs
  - /planner/preview: generates plan without creating job
  - /planner/validate: validates existing plan without creating job
  - /planner/jobs: plan → validate → create job (rejects invalid plans before job creation)
- Added SecretStore abstraction + InMemorySecretStore + EncryptedSecretStore placeholder
  - Secret list API never returns plaintext values
  - SecretStore creates/gets/deletes secrets internally
- Added secrets API routes: POST/GET/DELETE /me/secrets
- Added redaction helpers: credential key detection, secret value replacement in logs/params
- Added 19 Phase 7 tests: mock provider, schema validation, unknown tool rejection, V1/V2 rejection, duplicate step_id, empty steps, credential param rejection, preview no job, validate no job, plan→job flow, secret list no plaintext, secret CRUD, redaction, deterministic planner regression, OpenAI fake transport
- Security boundaries enforced:
  - LLM cannot execute Python/Shell, cannot bypass Tool Registry, cannot access secrets
  - Secret values never enter prompts, logs, JobEvents, Artifacts, Recipe, or Reports
  - params containing api_key/token/password are rejected at PlanValidator level
  - Preview and validate endpoints do not create jobs or enqueue work
- Verification: 87 passed, 19 skipped; frontend typecheck+build passed; git clean pending commit
- No real LLM key required for default pytest; MockLLMProvider + fake transport cover all test paths

## 2026-06-27 Phase 6B Live Integration Closeout Update

- GitHub Actions CI run [#28286885004](https://github.com/foolkking/material-data-intelligence/actions/runs/28286885004) completed with **full success**:
  - Unit Tests (Python 3.11): passed
  - Frontend Typecheck & Build: passed
  - Service-backed Integration (PostgreSQL + Redis + MinIO): **18 passed, 0 skipped, 0 failed**
- Alembic upgrade head ran against live PostgreSQL (CI service container) — 9 tables + 6 indexes verified
- MinIO bucket `mdi-artifacts` created and live-tested with put/get/exists/signed-url
- Redis queue live enqueue/handle tested against real Redis service container
- PostgreSQL repository live CRUD tested for all 9 entity types
- JobEvent seq monotonic/concurrent correctness verified on PostgreSQL with advisory lock strategy
- Service-backed product loop tested with real Tool Registry + BasicMetricsAdapter through execute_tool_request()
- CI workflow includes zero-skip enforcement: if any integration test skips, the job fails
- Added `httpx` to pyproject.toml dependencies (required by starlette.testclient)
- Fixed multiple P0 integration bugs: FK violations from shared project IDs, invalid job state transitions, ToolRegistry constructor mismatch
- **Final acceptance: PASS.** All 18 integration tests ran and passed on live Docker-backed PostgreSQL/Redis/MinIO via GitHub Actions. Phase 6 is live-verified.
- **Phase 6B closeout complete. Phase 7 may proceed.**

## 2026-06-26 Phase 6 Service-backed Runtime Smoke & Integration Hardening Update

- Re-read the required Phase 6 docs, Alembic baseline, persistent state, and docker-compose config before changes.
- Verified the Phase 5 baseline: clean Git status, `uv lock --check`, `python -m pytest -q`, `npm ci`, `npm run typecheck`, and `npm run build` all passed.
- Added 18 service-backed integration smoke tests in `tests/test_phase6_integration.py` covering:
  - Docker compose services reachability (PostgreSQL, Redis, MinIO).
  - Alembic live migration: real `alembic.command.upgrade(alembic_cfg, "head")` against PostgreSQL, plus downgrade+reupgrade cycle and index existence checks.
  - PostgreSQL repository live CRUD: Project, Dataset, Job, ToolCall, Artifact, Recipe, Report.
  - Transaction rollback and status transition rejection at repository boundary.
  - PostgreSQL JobEvent seq live: monotonic seq, advisory lock strategy, 30-event concurrent append correctness.
  - Redis queue live: enqueue/dequeue, QueueWorkerRuntime with PG repos + Redis backend.
  - Queue retry idempotency: duplicate job handle, crash+retry persistence.
  - MinIO live: put/get/exists/signed-url for json/text/bytes, signed URL structure validation.
  - Service-backed product-loop smoke: PG repos + Redis queue + MinIO storage + real Tool Registry + BasicMetricsAdapter (not fake executor).
- All 18 integration tests are gated with `@pytest.mark.integration` and skip cleanly when `MDI_RUN_INTEGRATION != 1` or Docker services are unreachable.
- Fixed `docker-compose.yml` MinIO healthcheck to use `mc ready local` for reliability.
- Updated `docs/16_RUNTIME_INFRASTRUCTURE_RUNBOOK.md` with integration test guide (sections 11-12), environment variables, category table, and troubleshooting for connection refused, migration failed, bucket not found, and signed URL invalid.
- Updated `.env.example` with `MDI_RUN_INTEGRATION` and `MDI_TEST_DATABASE_URL`.
- Verification:
  - `python -m pytest -q`: 68 passed, 19 skipped.
  - `python -m pytest tests/test_phase6_integration.py -q`: 18 skipped (Docker not available on this machine).
  - `python -m pytest -q -m integration`: all skipped (no Docker).
  - `uv lock --check`: passed.
  - `npm ci`: passed.
  - `npm run typecheck`: passed.
  - `npm run build`: passed.
- **Final acceptance**: CONDITIONAL PASS. Docker is not available on this machine; all 18 integration tests skip cleanly. Alembic test calls real `alembic.command.upgrade()`, service-backed loop test uses real Tool Registry + BasicMetricsAdapter, and git is clean at commit `e3c7a73`. Cannot enter Phase 7 until live Docker-backed integration is verified.

## 2026-06-26 Phase 5 PostgreSQL Runtime + Queue Worker + MinIO Integration Update

- Re-read the required Phase 5 project docs, Alembic baseline, and persistent state, then verified the Phase 4 baseline before changes: clean Git status, `uv lock --check`, `python -m pytest -q`, `npm ci`, `npm run typecheck`, and `npm run build` all passed.
- Added Phase 5 runtime configuration support for standard `DATABASE_URL`, `POSTGRES_*`, `REDIS_URL`, and `MINIO_*` variables while keeping existing `MDI_*` aliases.
- Added `mdi_api.database` engine/repository-factory helpers and made Alembic honor configured runtime database URLs while preserving the local SQLite fallback when no runtime DB env is set.
- Added `docs/16_RUNTIME_INFRASTRUCTURE_RUNBOOK.md` with Docker, Alembic, repository smoke, queue, MinIO, and integration-test operating notes.
- Extended `docker-compose.yml` and `.env.example` for one-command local infrastructure: PostgreSQL, Redis, and MinIO.
- Added live-capable `S3CompatibleArtifactStorage` behavior with optional boto3-compatible client support for `put_*`, `get_*`, `exists`, and real presigned URL generation; mapping/placeholder behavior remains unchanged when no client is configured.
- Added `QueueWorkerRuntime`, `InMemoryQueueBackend`, and `RedisRQQueueBackend`. The queue handler receives `job_id`, loads repository state, writes ToolCall status, JobEvents, Artifact metadata, and preserves idempotent retry behavior.
- Hardened SQLAlchemy JobEvent seq allocation for PostgreSQL with a transaction-scoped advisory lock keyed by `job_id`; SQLite/local tests continue to use the existing in-process lock.
- Verification:
  - `python -m pytest tests/test_phase5_runtime_infrastructure.py -q`: 7 passed, 1 skipped.
  - `python -m pytest -q`: 68 passed, 1 skipped, 50 third-party warnings.
  - `python -m pytest -q -m integration`: 1 skipped because external services were not enabled.
  - `uv lock --check`: passed.
  - `npm ci`: passed.
  - `npm run typecheck`: passed.
  - `npm run build`: passed.
  - `git diff --check`: passed with Windows line-ending notices only.

## 2026-06-26 Phase 4 Production Persistence Hardening Update

- Re-read the required project docs and persistent state, then verified the Phase 3 baseline before changes: clean Git status, `uv lock --check`, `python -m pytest -q`, `npm ci`, `npm run typecheck`, and `npm run build` all passed.
- Added an Alembic migration entrypoint and Phase 4 baseline revision for the PostgreSQL-oriented persistence schema while keeping SQLite-compatible SQLAlchemy metadata for tests.
- Hardened SQLAlchemy metadata for `jobs`, `tool_calls`, and `artifacts` with status checks, ToolCall idempotency fields, `(job_id, step_id)` uniqueness, artifact duplicate metadata detection, and storage-provider constraints.
- Added centralized `RepositorySession`, `UnitOfWork`, and `RepositoryFactory` transaction boundaries with rollback coverage.
- Added centralized Job/ToolCall status transition validation. The local synchronous worker keeps `created -> running` compatibility, while queued production flow can use `created -> queued -> running`.
- Added idempotent ToolCall and Artifact repository writes so repeated worker attempts reuse stable records instead of generating uncontrolled duplicates.
- Kept the Phase 2/3 product loop unchanged in scope: no real LLM, no V1/V2 tools, no Celery/Ray/Kubernetes, no production PostgreSQL runtime, no live MinIO/S3 client, and no frontend redesign.
- Verification after fixes:
  - `python -m pytest tests/test_phase4_persistence_hardening.py -q`: 8 passed.
  - `uv lock --check`: passed.
  - `python -m pytest -q`: 61 passed, 50 third-party warnings.
  - `npm ci`: passed.
  - `npm run typecheck`: passed.
  - `npm run build`: passed.
  - `git diff --check`: passed with Windows line-ending notices only.

## 2026-06-26 Phase 3 Acceptance Hardening Update

- Re-ran Phase 3 acceptance against the stricter handoff checklist: Phase 2 regression, repository coverage, database schema/indexes, JobEvent cursor semantics, SSE stream, ArtifactStorage mapping, API event/artifact routes, and reproducible frontend checks.
- Found and fixed P1 repository coverage gaps by adding `DataProfileRepository` and `ReportRepository` to both InMemory and SQLAlchemy repository bundles.
- Found and fixed a JobEvent cursor hardening gap by adding in-process append locks to the repository layer and `InMemoryJobStore`; tests now cover concurrent appends without duplicate seq values.
- Found and fixed P1 storage schema gaps by adding `storage_provider`, `bucket`, `content_type`, `sha256`, `size_bytes`, `preview_key`, and `created_at` metadata coverage across storage mapping, SQL metadata, migration draft, shared schemas, and artifact API summaries.
- Found and fixed a frontend P0 reproducibility issue where `npm run typecheck` depended on existing `.next/types`; added `apps/web/tsconfig.typecheck.json` so typecheck passes from a clean `.next` state.
- Kept scope unchanged: no real LLM, no V1/V2 tools, no Celery/Ray/Kubernetes, no production PostgreSQL/MinIO wiring, and no frontend feature expansion.
- Verification after fixes:
  - `npm ci`: passed.
  - `uv lock --check`: passed.
  - `python -m pytest -q`: 53 passed, 50 third-party deprecation warnings.
  - `npm run typecheck`: passed from a clean `.next` state.
  - `npm run build`: passed.

## 2026-06-26 Phase 3 Persistence Foundation Update

- Added Phase 3 persistence foundation without adding real LLM execution, V1/V2 tools, Celery/Ray/Kubernetes, full auth, or frontend expansion.
- Added repository abstraction for `ProjectRepository`, `DatasetRepository`, `JobRepository`, `JobEventRepository`, `ToolCallRepository`, `ArtifactRepository`, and `RecipeRepository`.
- Kept the Phase 2 local product loop on its InMemory path, while adding SQLAlchemy Core repositories that are SQLite-testable and PostgreSQL-oriented.
- Extended SQLAlchemy metadata and migration draft coverage for `projects`, `datasets`, `data_profiles`, `jobs`, `job_events`, `tool_calls`, `artifacts`, `visualization_recipes`, and `reports`.
- Added durable cursor semantics to job events: seq remains monotonic per job, `list_events_after_seq(job_id, after_seq)` exists, and `GET /jobs/{job_id}/events?after_seq=N` filters by cursor.
- Added `GET /jobs/{job_id}/stream` as an SSE smoke endpoint using the existing local runtime event stream.
- Added `ArtifactStorage` abstraction with local filesystem storage and an S3/MinIO-compatible mapping interface, including `storage_key`, `content_type`, `sha256`, `size_bytes`, and `preview_key` metadata.
- Added `GET /artifacts/{artifact_id}/download` as a local signed-url/download placeholder while preserving `GET /artifacts/{artifact_id}` for artifact detail.
- Added Phase 3 tests for repository interfaces, SQLAlchemy schema/cursor behavior, SSE smoke streaming, artifact storage mapping, and Phase 2 loop regression.
- Hardened frontend typecheck reproducibility by disabling stale incremental `tsconfig.tsbuildinfo` reuse in `npm run typecheck`.
- Verification:
  - `uv lock --check`: passed.
  - `python -m pytest -q`: 52 passed, 50 third-party deprecation warnings.
  - `npm run typecheck`: passed.
  - `npm run build`: passed.

## 2026-06-25 Phase 2 Acceptance Hardening Update

- Re-ran the Phase 2 acceptance audit against the current worktree after the local product loop implementation.
- Fixed a shared-schema alignment issue in generated `AnalysisPlan.expectedArtifacts`: Phase 1 and Phase 2 planners now emit `{name, type, fromStepId}` entries instead of step-level grouped artifact summaries.
- Fixed Phase 2 job-level Recipe generation to include per-step `toolVersion` and `inputBindings` as `Record<string, string>`, matching `docs/13_SHARED_SCHEMA_SPEC.md` and `packages/schemas/src/index.ts`.
- Added shared Python/TypeScript schema types for `ExpectedArtifact` and `VisualizationRecipeStep`, and validated Phase 2 Recipe JSON with the Pydantic `VisualizationRecipe` model before export.
- Changed Phase 2 local-path uploads to parse the copied raw file under the runtime artifact root, keeping the accepted dataset path independent from the caller's original local path.
- Updated `docs/01_PRODUCT_REQUIREMENTS.md` and `README.md` to remove stale schema/status wording.
- Verification:
  - `python -m pytest -q`: 48 passed, 45 third-party deprecation warnings.
  - `npm ci`: passed from `apps/web/package-lock.json`.
  - `npm run typecheck`: passed.
  - `npm run build`: passed.
  - Manifest audit: 3 manifests load, registry version `0.1.0`, 10 MVP tools.
  - Phase 2 loop audit: project -> dataset upload -> profile -> plan -> job -> 5 tool calls -> 25 artifacts completed.
- Scope guard remains unchanged: no real LLM execution, no V1/V2 tool execution, no Celery/PostgreSQL/MinIO runtime persistence, and no frontend expansion this round.

## 2026-06-25 Phase 2 Local Product Loop Update

- Added `apps/api/mdi_api/phase2_runtime.py` as the Phase 2 in-memory product loop.
- The runtime now covers project creation, dataset upload from local paths or inline small files, deterministic parsing, `DataProfile` generation, deterministic `AnalysisPlan` generation, local Worker execution, Adapter invocation, Artifact export, JobEvent recording, job-level Recipe generation, Markdown/HTML report generation, and API result queries.
- Added Phase 2 API routes:
  - `POST /projects`
  - `POST /datasets/upload`
  - `GET /datasets/{dataset_id}/profile`
  - `POST /jobs`
  - `GET /jobs/{job_id}`
  - `GET /jobs/{job_id}/events`
  - `GET /jobs/{job_id}/tool-calls`
  - `GET /jobs/{job_id}/artifacts`
  - `GET /artifacts/{artifact_id}`
- The deterministic Phase 2 planner selects 3-5 MVP tools and currently chooses this five-tool mixed-dataset path when structures and an ML table are present:
  `composition.ptable_heatmap`, `composition.chem_sys_treemap`, `structure.viewer_3d`, `ml.basic_metrics`, and `ml.outlier_table`.
- Added `LocalFileArtifactStore` over `LocalArtifactExporter` output so API routes can return artifact metadata and text/JSON content without introducing MinIO.
- Kept execution inside the existing validated boundary:
  `AnalysisPlan` -> `ToolExecutionRequest` -> Tool Registry lookup -> paramsSchema validation -> Adapter -> Artifact.
- Explicitly did not add real LLM API calls, full auth, V1/V2 tools, Celery, PostgreSQL, MinIO, or frontend feature expansion.
- Added `tests/test_phase2_product_loop.py` with coverage for data pipeline upload/profile, deterministic planner, local worker runtime, artifact store, API routes, and end-to-end product flow.
- Verification:
  - `python -m pytest -q`: 48 passed, 45 third-party deprecation warnings.
  - Frontend typecheck/build were not rerun because no frontend files changed in this Phase 2 implementation.
- `.gitignore` now ignores `material-data-intelligence-*.zip`, so the Phase 1 handoff archive can stay in the workspace without entering commits.

## 2026-06-25 Phase 1 Engineering Hardening Update

- Froze Python dependencies with `uv.lock`.
- Verified the Python test suite from an isolated uv-managed `.venv` using:
  `python -m pytest -q` -> 42 passed.
- Froze frontend dependencies with `apps/web/package-lock.json` because `pnpm` is not installed in the current environment.
- Verified frontend reproducibility from the lockfile with:
  - `npm ci`
  - `npm run typecheck`: passed
  - `npm run build`: passed
- Confirmed `.gitignore` covers generated dependency/build/cache outputs:
  `.venv/`, `*.egg-info/`, `node_modules/`, `.next/`, `.pytest_cache/`, `.pytest_tmp/`,
  `__pycache__/`, `*.pyc`, and `*.tsbuildinfo`.
- Phase 1 is now ready for a Git baseline commit and `git archive` handoff package after final cleanup.

## 2026-06-25 Phase 1 Product Acceptance Update

- Completed a docs/01 Phase 1 MVP acceptance pass against the current implementation.
- Added a deterministic Phase 1 product-flow runtime in `apps/api/mdi_api/phase1_demo.py`.
- The runtime covers: create project, parse upload set, Data Profile, natural-language request boundary, structured `AnalysisPlan`, registry-approved Worker execution, Artifact/Recipe generation, Markdown/HTML report, and JobEvent timeline.
- The demo flow validates all 10 MVP tools through Tool Registry + Adapter:
  `composition.ptable_heatmap`, `composition.elements_hist`, `composition.chem_sys_treemap`,
  `structure.structure_3d`, `structure.viewer_3d`, `structure.coordination_hist`,
  `ml.density_scatter`, `ml.error_distribution`, `ml.basic_metrics`, `ml.outlier_table`.
- Added API boundary routes for project creation, upload sessions, analysis requests, job events, event streaming, and artifact summaries.
- Expanded Phase 1 SQLAlchemy metadata to include the product-flow entities listed in docs/01: data profiles, field mappings, sessions/messages, jobs/events/tool calls/artifacts, recipes, configs, secrets, and audit logs.
- Updated the frontend shell so Agent Timeline, chart cards, 3D Viewer, Logs, Artifacts, Recipe, and Report surfaces are visible in the Phase 1 workspace.
- Verification passed:
  - `python -m pytest -q`: 42 passed, 25 third-party deprecation warnings.
  - `npm run typecheck`: passed.
  - `npm run build`: passed.
- Current Phase 1 caveats:
  - The product-flow runtime is deterministic/in-memory and intended for acceptance/demo, not a production repository or Celery deployment.
  - `preview_png` now has a minimal PNG fallback when Kaleido/Chromium is unavailable.
  - `structure.viewer_3d` may still emit a MatterViz-safe fallback HTML if widget rendering is unavailable.
  - Real object storage upload sessions, PostgreSQL repositories, Celery workers, and durable SSE cursors remain next-phase implementation work.

## 当前阶段

Phase 7: LLM JSON Planner + BYOK Secret Management — **通过 (PASS)**。90 passed, 19 skipped, 0 failed（22 个 Phase 7 tests + 68 个现有 tests）。MockLLMProvider + PlanValidator（严格，10 规则）+ SecretStore + Planner API 全部可测。**边界说明**：`/planner/jobs` 在 validate 成功后创建 job，但当前 job 实际运行的是 deterministic plan（`build_phase2_plan`），验证过的 LLM plan 尚未接入真实执行——「LLM→执行」闭环未打通，属已记录的后续工作（见 OPEN_QUESTIONS / ADR-075）。Secret 仅 InMemoryStore，生产 envelope encryption 未实现。

## 已完成阶段

- [x] Phase 0：项目目标与边界定义
- [x] Phase 1：产品需求与用户流程
- [x] Phase 2：总体系统架构
- [x] Phase 3：前端工作台设计
- [x] Phase 4：后端服务与数据库设计
- [x] Phase 5：Agent 编排设计
- [x] Phase 6：工具注册表与 Adapter
- [x] Phase 7：数据解析与 Data Profile
- [x] Phase 8：高并发任务系统
- [x] Phase 9：Artifact / Recipe / Report
- [x] Phase 10：用户配置、安全与扩展
- [x] Phase 11：MVP Roadmap

补充文件：

- [x] `docs/11_MATERIAL_DOMAIN_EXTENSIONS.md`：专业材料领域扩展设计
- [x] `docs/index.md`：文档索引
- [x] `docs/03A_FRONTEND_COMPONENT_SPEC.md`：前端组件规格
- [x] `docs/03B_FRONTEND_STATE_AND_INTERACTION.md`：前端状态与交互规格
- [x] `docs/13_SHARED_SCHEMA_SPEC.md`：共享 Schema 基线
- [x] `docs/14_PYMATVIZ_CAPABILITY_INVENTORY.md`：pymatviz 能力清单与平台 Tool ID 映射
- [x] `docs/15_ADAPTER_IMPLEMENTATION_PLAN.md`：Adapter 实现计划
- [x] `tool_registry/pymatviz_manifest.yaml`：pymatviz 原生能力 manifest
- [x] `tool_registry/matterviz_manifest.yaml`：MatterViz / widget 能力 manifest
- [x] `tool_registry/platform_builtin_manifest.yaml`：平台内置与自定义 Plotly 能力 manifest

当前新增设计重点：

本项目进一步明确为“以 pymatviz 为 primary visualization kernel 的材料数据智能分析与可视化平台”。当前补充了 pymatviz capability inventory、manifest-based tool registry 和 adapter implementation plan。

## 本轮完成

- 建立代码工程骨架：`apps/web`、`apps/api`、`services/workers`、`packages/schemas`、`packages/tool-registry`、`packages/adapters`、`packages/material-parsers`、`packages/artifact-core`、`tests/fixtures`。
- 新增根级 `pyproject.toml`，配置 Python 包发现、pytest 路径和核心材料依赖声明。
- 在 `packages/schemas` 中实现共享类型基线：
  - Python/Pydantic：`mdi_schemas.models`
  - JSON Schema：`packages/schemas/json/registered-tool.schema.json`
  - TypeScript 类型：`packages/schemas/src/index.ts`
- 在 `packages/tool-registry` 中实现 manifest loader：
  - `loadManifests()` / `load_manifests()`
  - `validateManifest()` / `validate_manifest()`
  - `getToolById()`、`listTools()`、`listToolsByStage()`、`listToolsByDomain()`、`listMvpTools()`
  - 校验 `tool_id` 唯一、`stage`、`implementation_source`、`display_target`、`artifact_types` 和 adapter class name。
- 在 `packages/artifact-core` 中实现本地文件系统 `LocalArtifactExporter`，输出稳定 storage key、content hash、Artifact metadata 和 provenance。
- 在 `packages/adapters` 中实现：
  - `BaseToolAdapter`
  - `ToolExecutionContext`
  - `ToolExecutionError` / error normalizer
  - Adapter class registry
  - Plotly export helper
- 实现 MVP 前 3 个 Adapter：
  - `composition.ptable_heatmap` -> `PTableHeatmapAdapter`
  - `structure.structure_3d` -> `Structure3DAdapter`
  - `structure.viewer_3d` -> `StructureViewer3DAdapter`
- 为 fixture 和测试补齐：
  - `tests/fixtures/structures/si.cif`
  - `tests/fixtures/tables/formulas.csv`
  - manifest loader、BaseToolAdapter、三个 Adapter、Artifact metadata/recipe 的最小测试。
- 真实环境核对并安装/升级运行依赖：`pymatviz 0.18.0`、`pymatgen 2026.5.4`、`ase 3.29.0`、`plotly 6.8.0`；为兼容 NumPy 2.x 同步升级 `xarray`、`pyarrow`、`numexpr`、`bottleneck`、`shapely`、`scikit-image`。
- 测试结果：`python -m pytest`，11 passed。
- 继续实现 Data Pipeline 最小库层：
  - 新增 `packages/material-parsers/mdi_material_parsers/detector.py`，支持 CIF、POSCAR/CONTCAR、CSV、JSON limited、ZIP、XYZ/EXTXYZ 的格式识别。
  - 新增 `packages/material-parsers/mdi_material_parsers/parsers.py`，支持 CIF/POSCAR -> `Structure`、CSV -> `DataFrame`、JSON limited -> `Structure` 或 simple table。
  - 新增 `packages/material-parsers/mdi_material_parsers/profile.py`，从 parse results 构建轻量 `DataProfile`、`structureSummary`、`tableSummary`、quality issues 和 recommended tasks。
  - 新增 normalized object draft 数据模型，记录 object id、object type、source file ids、storage key、metadata、hash 和 payload。
  - 补充 `tests/test_data_pipeline.py` 与 fixtures：`POSCAR`、`plain.xyz`、`ml_results.csv`。
  - 更新共享 `DataProfile` Pydantic model，补齐 `structureSummary`、`tableSummary`、`phononSummary`、`trajectorySummary` 可选字段。
  - 更新 `pyproject.toml`，显式加入 `pandas>=2.2`。
- 最新测试结果：`python -m pytest`，17 passed。
- 继续补齐剩余 7 个 MVP Adapter，并将 10 个 MVP 工具全部接入 adapter class registry：
  - `composition.elements_hist` -> `ElementsHistAdapter`
  - `composition.chem_sys_treemap` -> `ChemSysTreemapAdapter`
  - `structure.coordination_hist` -> `CoordinationHistAdapter`
  - `ml.density_scatter` -> `DensityScatterAdapter`
  - `ml.error_distribution` -> `ErrorDistributionAdapter`
  - `ml.basic_metrics` -> `BasicMetricsAdapter`
  - `ml.outlier_table` -> `OutlierTableAdapter`
- 新增 ML adapter 共用校验层，支持 DataFrame / records 输入、target/prediction 字段推断、数值列校验、metrics 和 outlier 计算。
- 新增测试覆盖全部 10 个 MVP Adapter，新增 manifest MVP adapter class registry 校验。
- 最新测试结果：`python -m pytest`，25 passed。
- 继续核验 Milestone 0/1 + 已实现库层闭环：
  - 将 pytest 临时目录固定到仓库内 `.pytest_tmp`，避免受限 sandbox 访问系统临时目录失败。
  - 将 plain XYZ Data Pipeline 语义对齐设计：解析为非周期 `Atoms` normalized object，并在 `DataProfile.qualityIssues` 中记录 `NON_PERIODIC_ATOMS` warning；它仍不会进入 `periodic_required` 的结构工具。
  - 新增 `.extxyz` 检测与 ASE->pymatgen 周期结构转换测试。
  - 新增 ZIP 安全解包回归测试，验证路径穿越 member 会被拒绝，保留 safe member 解析为 partial。
  - 新增 normalized object 稳定落盘 helper 测试，路径固定为 `projects/{project}/datasets/{dataset}/normalized/...`。
  - 最新测试结果：`python -m pytest`，25 passed。
- 继续核验共享 Schema 覆盖面：
  - 补齐 `packages/schemas/src/index.ts` 中的 TypeScript 核心类型导出：`JobStatus`、`JobEventStatus`、`ToolExecutionRequest`、`ToolCall`、`Artifact`、`AnalysisPlan`、`AnalysisStep`、`DataProfile`、`VisualizationRecipe` 等。
  - 在 Python/Pydantic schema 中新增 `JobEvent`，为后续 SSE / Agent Timeline 事件流复用同一共享类型。
  - 新增 `tests/test_shared_schemas.py`，校验 Python 和 TypeScript schema 入口暴露用户要求的核心类型。
  - 最新测试结果：`python -m pytest -q`，30 passed，20 warnings；warnings 来自当前 Anaconda 环境中的 matplotlib/Jupyter/ipywidgets 依赖弃用提示，不影响本阶段功能。
- 继续补齐受控执行库层入口：
  - 新增 `packages/adapters/mdi_adapters/executor.py`，提供 `execute_tool_request()`，执行顺序为 Tool Registry lookup -> input resolution / cache key -> paramsSchema validation -> optional in-memory cache lookup -> adapter instantiation -> adapter execution。
  - 新增 `ToolExecutionResult`，记录 `tool`、`artifacts`、`cache_key`、`cache_hit`，为后续 ToolCall 状态表和 JobEvent 持久化留出结构化结果。
  - 新增 `tests/test_tool_executor.py`，覆盖 registry 路由、非法参数拒绝、未注册 tool 拒绝和 cache hit。
  - 最新测试结果：`python -m pytest -q`，34 passed，20 warnings；warnings 仍为当前 Anaconda 第三方依赖弃用提示。
- 继续补齐 Worker 语义基线：
  - 新增 `services/workers/mdi_workers/runtime.py`，提供 `run_tool_call_job()` 和开发用 `InMemoryJobStore`。
  - `run_tool_call_job()` 会记录 Job status、ToolCall status、`tool.started`、`artifact.ready`、`tool.completed` / `tool.failed` JobEvent，并保留事件 `seq` 单调递增语义。
  - ToolCall 记录会对 secret-like params 做脱敏，失败路径不会保存明文 API key / BYOK。
  - 新增 `tests/test_worker_runtime.py`，覆盖成功事件流和失败脱敏路径。
  - 最新测试结果：`python -m pytest -q`，36 passed，20 warnings；warnings 仍为当前 Anaconda 第三方依赖弃用提示。
- 本轮恢复核验：
  - 已按新会话要求重新读取 `README.md`、`AGENTS.md`、`MASTER_PROMPT.md`、核心 `docs/`、3 个 manifest 和 `persistent/` 状态文件。
  - 已检查 `git status --short`，确认上一轮代码与文档仍处于未提交工作区中；本轮继续在该状态上增量推进，未回退既有变更。
  - 已检查配置，当前仅存在 Python `pyproject.toml` 测试配置，未发现前端 `package.json` / `pnpm-workspace.yaml`。
  - 已运行基线测试：`python -m pytest -q`，36 passed，20 warnings。
- 本轮补强 Tool Registry paramsSchema：
  - 将剩余 MVP 工具的 `paramsSchema` 从宽松 `additionalProperties: true` 收紧为平台批准参数白名单：
    `composition.elements_hist`、`composition.chem_sys_treemap`、`structure.coordination_hist`、`ml.density_scatter`、`ml.error_distribution`、`ml.basic_metrics`、`ml.outlier_table`。
  - 新增 `tests/test_manifest_loader.py::test_mvp_tools_reject_unregistered_params`，确保 10 个 MVP 工具均拒绝未注册参数。
  - 最新测试结果：`python -m pytest -q`，37 passed，20 warnings；warnings 仍为当前 Anaconda 第三方依赖弃用提示。
- 本轮完成 Milestone 1 scaffold：
  - 新增 `docker-compose.yml`，配置本地 PostgreSQL、Redis、MinIO 服务；新增 `.env.example` 并只保留占位符，不写入真实 Secret。
  - 新增 `apps/api/mdi_api` FastAPI app factory、配置加载、模块路由边界和 SQLAlchemy Core metadata。
  - 建立基础 Auth / Project / Dataset 表元数据：`users`、`organizations`、`projects`、`project_members`、`datasets`、`files`。
  - 新增 `/health`、`/auth/me`、`/projects`、`/datasets`、`/tools`、`/tools/mvp` API 边界，其中工具路由读取 Tool Registry。
  - 新增 `apps/web` Next.js App Router shell、三栏式工作台页面、底部面板、`package.json`、`tsconfig.json`、`next.config.mjs` 和 `pnpm-workspace.yaml`。
  - 更新 `pyproject.toml`，纳入 `apps/api` 包发现和 `fastapi`、`sqlalchemy`、`uvicorn`、`starlette>=0.40,<0.47` 依赖边界。
  - 修正当前 Anaconda 环境中 `starlette 1.0.0` 与 `fastapi 0.115.12` 不兼容的问题，将 Starlette 降级到 `0.46.2`。
  - 新增 `tests/test_phase1_scaffold.py`，验证 API route 边界、数据库表元数据、compose 服务和前端 shell 文件。
  - 最新测试结果：`python -m pytest -q`，41 passed，20 warnings；`npm run typecheck` passed；`npm run build` passed。

- 创建 `docs/00_PROJECT_GOAL.md`。
- 创建 `persistent/PROJECT_BRIEF.md`。
- 初始化持久化跟踪文件。
- 明确系统是材料数据智能分析与可视化平台，而不是 pymatviz 套壳。
- 明确 LLM 采用 JSON Plan + Tool Registry 的受控执行模式。
- 明确 MVP 优先覆盖文件上传、格式识别、Data Profile、Agent Plan、白名单工具调用、Artifact、Recipe 和报告基础链路。
- 补充独立系统定位：自然语言 + 材料数据文件 -> Plotly / MatterViz 图表、3D 模型、过程展示和可复现 Artifact。
- 补充 pymatviz / MatterViz 数据输入、可视化能力、3D 渲染路线和 MVP 工具集。
- 补充 Adapter 层决策：不 fork 大改 pymatviz，通过 Tool Registry 和 Visualization Service 隔离上游变化。
- 创建 `docs/01_PRODUCT_REQUIREMENTS.md`。
- 完成用户角色、用户故事、上传流程、Data Profile 流程、自然语言分析流程、图表生成流程、3D 模型查看流程、Agent Timeline、Artifact / Recipe / Report 流程定义。
- 明确 Phase 1 产品决策：MVP 仅登录用户、默认 Auto 模式、用户审查计划摘要但不编辑 JSON Plan、报告导出支持 Markdown/HTML。
- 创建 `docs/02_SYSTEM_ARCHITECTURE.md`。
- 明确 MVP 架构：Next.js 前端 + FastAPI 模块化应用 + Celery/Redis Worker + PostgreSQL + S3/MinIO。
- 明确逻辑服务边界：API Gateway、Data Service、Agent Service、Visualization Service、Worker Service、Artifact Service、Storage Layer、Queue Layer、Security Layer。
- 明确所有耗时任务必须通过 Job Queue 异步执行，前端通过 SSE/WebSocket 渐进展示 JobEvent。
- 创建 `docs/03_FRONTEND_WORKSPACE_DESIGN.md`。
- 明确前端采用三栏式工作台 + 底部面板：左侧数据资产、中央可视化画布、右侧 Agent 面板、底部 Logs/Code/Artifacts/Recipe/Warnings。
- 明确 MVP 使用固定响应式 Dashboard，MatterViz / heavy Plotly 优先通过 sandboxed artifact iframe 展示。
- 明确 Agent Plan 默认展示摘要，完整 JSON 和 ToolCall 细节可展开。
- 创建 `docs/04_BACKEND_SERVICE_DESIGN.md`。
- 明确后端模块边界：Auth、Project、Dataset、Profile、Jobs、Agent、Tools、Artifacts、Config、Secrets、Audit、Workers。
- 明确 MVP 上传采用对象存储预签名直传，不做分片/断点续传。
- 明确核心数据库实体、项目级 RBAC、数据隔离、统一错误模型和审计日志边界。
- 创建 `docs/05_AGENT_ORCHESTRATION_DESIGN.md`。
- 明确 Agent 职责：Intent Parser、Data-aware Planner、Tool Selector、Parameter Generator、Result Explainer、Report Writer。
- 明确 Agent 只能输出 JSON Analysis Plan，Execution Controller 校验后创建 ToolCall。
- 明确 MVP 不做自动多模型路由和完整工具文档 RAG；使用项目默认模型和静态 Tool Registry 摘要。
- 明确 Prompt injection 进入 Agent Timeline warning，并可阻止高风险计划执行。
- 创建 `docs/06_TOOL_REGISTRY_AND_ADAPTER.md`。
- 明确 Tool Registry 是唯一执行白名单，Adapter 隔离 pymatviz / MatterViz / Plotly 上游变化。
- 明确 MVP Tool Set、Tool Schema、Artifact 标准、ToolError、缓存 key 和插件扩展机制。
- 明确 MVP Phonon 工具推迟到 V1，当前只保留 Schema 和扩展点。
- 创建 `docs/07_DATA_PIPELINE_DESIGN.md`。
- 明确数据管线流程：格式识别、安全解析、标准化对象、Data Profile、质量检查、推荐任务。
- 明确 MVP 支持 CIF、POSCAR/CONTCAR、XYZ/EXTXYZ 基础解析、CSV、JSON、ZIP；phonon/trajectory 深度支持推迟到 V1，VASP/LAMMPS 推迟到 V2。
- 明确代表 3D 结构 MVP 采用规则采样，composition clustering 推迟到 V1。
- 创建 `docs/08_JOB_QUEUE_AND_CONCURRENCY.md`。
- 明确 MVP 使用 SSE 推送 JobEvent，WebSocket 协作能力推迟到 V1。
- 明确 Worker 按 parse/profile/llm/viz/render/export 队列拆分。
- 明确 PostgreSQL 是 Job/ToolCall/Artifact 状态事实源，Redis 只做 broker/cache/短期状态。
- 明确大数据降采样、3D LOD、资源限制、多用户并发和可观测性策略。
- 创建 `docs/09_ARTIFACT_AND_RECIPE_SYSTEM.md`。
- 明确 Plotly `figure.json`、MatterViz `viewer.html + metadata.json`、Report Markdown、Recipe JSON 的 canonical 地位。
- 明确 Artifact / Recipe / Report 默认不可变，重跑或编辑生成新 version。
- 明确 MVP 不支持公开分享，只支持项目成员访问和授权导出包。
- 创建 `docs/10_USER_CONFIG_AND_SECURITY.md`。
- 明确配置优先级：system defaults < user_config < project_config < recipe/job params。
- 明确 MVP 使用 Docker/容器化 Worker 沙箱，用户级 BYOK，组织级共享 Key 推迟到 V1。
- 明确 Secret envelope encryption、文件安全、Prompt injection MVP 防护、审计日志和插件默认最小权限。
- 创建 `docs/12_MVP_ROADMAP.md`。
- 明确 MVP / V1 / V2 范围、技术栈、开发里程碑、优先级、风险清单、验收标准和进入代码实现顺序。
- Phase 0-11 设计文档全部完成。
- 复核用户给定目标文件清单，补充创建 `docs/11_MATERIAL_DOMAIN_EXTENSIONS.md`。
- 修正 `docs/06_TOOL_REGISTRY_AND_ADAPTER.md` 中 phonon / trajectory 工具阶段归属，使其与 ADR 和 Roadmap 一致：V1 支持 phonon band/DOS 与 trajectory viewer，V2 支持 VASP/LAMMPS、电子结构、生成材料评估和外部生态插件。
- 更新 `docs/12_MVP_ROADMAP.md` 的设计完成标准，纳入 `docs/11_MATERIAL_DOMAIN_EXTENSIONS.md`。
- 完成逐文件审核，创建 `docs/index.md` 作为文档入口。
- 修正 `docs/01_PRODUCT_REQUIREMENTS.md` 中 MVP 示例混入 V1 `structure.spacegroup_bar` 的表述。
- 修正 `docs/03_FRONTEND_WORKSPACE_DESIGN.md` 中 TrajectoryWidget MVP 表述，明确 MVP 仅基于已解析结构集合展示首末帧/抽样帧，不提供完整 trajectory 工具。
- 更新 `persistent/TOOL_REGISTRY_NOTES.md`，补齐 `ml.parity_plot` 的 V1 归属，并区分 V1 phonon/trajectory 与 V2 VASP/LAMMPS。
- 完成 Design Review Fixes：修正 `.gitignore`，确保 `docs/` 和 `persistent/` 进入 Git 版本管理。
- 新增根目录 `README.md`、`AGENTS.md`、`MASTER_PROMPT.md`，作为新会话和 Coding Agent 入口。
- 新增 `docs/13_SHARED_SCHEMA_SPEC.md`，统一 `ArtifactType`、`DisplayTarget`、`ToolCategory`、`ToolDomain`、`ToolInputSchema`、`AnalysisPlan`、`JobEvent`、`Recipe`、`Config` 等跨模块 Schema。
- 新增 `docs/03A_FRONTEND_COMPONENT_SPEC.md` 和 `docs/03B_FRONTEND_STATE_AND_INTERACTION.md`，补齐前端组件树、状态切片、Artifact Loader、全屏/重试/错误态和 SSE 事件投影。
- 统一 MVP/V1 工具范围：MVP 为 composition/structure/ml 的 10 个核心工具；V1 扩展 parity、uncertainty、error-by-domain、phonon、trajectory、RDF/XRD、composition clustering。
- 修正 Tool Registry：`ToolInputSchema` 改为 `inputOptions` 多输入方案，增加 `implementationSource`、`ToolDomain` 和周期性结构约束。
- 增加 `metrics_json`、`table_json`、`table_csv`、`quality_issues_json`，将指标和表格结果作为一等 Artifact。
- 修正 JSON limited、ZIP 容器、plain XYZ / EXTXYZ 与周期结构工具的边界。
- 调整 MatterViz snapshot、SVG/PDF high-resolution export 的阶段归属，MVP 不把这些作为阻塞项。
- 明确 BYOK 多人项目规则：用户级 Secret 按 job runner 解析，Recipe 不保存具体 SecretRef。
- 补充 JobEvent 关键数据库索引和事件/日志保留策略。
- 更新 ADR-027、ADR-042，并新增 ADR-048 至 ADR-057。
- 完成第二轮实现前一致性修正：补全 `docs/13_SHARED_SCHEMA_SPEC.md` 中 `FileProfile`、`ObjectProfile`、`QualityIssue`、`RecommendedTask`、`InputRef`、`ToolExecutionRequest` 和 `Molecule`。
- 统一 `artifactTypes` 命名，移除旧的 format 语义残留。
- 删除 Phase 0 旧 Schema 草案，改为引用 `docs/13_SHARED_SCHEMA_SPEC.md`。
- 修正 Phase 3 `activeTab` 为 `DisplayTarget`，修正 Phase 4 `job_events.seq`，修正 Phase 12 10 个 MVP 工具与 Milestone 3 的冲突。
- 将推荐任务增加 `stage`、`availableNow`、`requiredTools` 和 `reason` 语义，避免 MVP Planner 自动选择 V1 工具。
- 统一 Redis 只作为 broker/cache/transient state 的表述；Celery result backend 若启用也不作为业务事实源。
- 在 `README.md` 增加对外分享压缩包排除 `.git/` 的建议。
- 完成第三轮一致性修正：统一 JobEvent status 为 `info/running/success/warning/error`，移除 retry 专用 JobStatus，修正用户配置导出格式为 download format，确认 Phase 0 只引用共享 Schema，确认 Tool Registry 执行流和 Markdown 代码块无重复/破损。
- 完成第四轮实现前一致性修正：拆分 MVP 10 个工具实现标准与 6 个工具端到端演示标准；统一 Plotly MVP 交互展示产物口径；Phase 2 `JobEvent` 补齐 `seq/progress` 并让 `ArtifactRecord` 引用共享 `Artifact`；Phase 4 表字段补齐索引依赖的时间字段；MVP Secret API 改为用户级 `/me/secrets`，项目级共享 Secret 推迟到 V1；Agent Timeline 状态与共享 `JobEvent.status` 对齐。
- 完成第五轮实现前小修：Phase 1 MVP 验收标准与 Phase 12 完全对齐；Phase 1 上传范围补齐 POSCAR/CONTCAR、JSON limited、XYZ/EXTXYZ 基础解析；Phase 6 / Phase 9 Artifact 元数据改为引用 `docs/13_SHARED_SCHEMA_SPEC.md` 的正式 `Artifact` / `ArtifactMetadata`；复核 Phase 6 缓存策略中 `refresh` 条目无重复。
- 完成 pymatviz 能力抽象基线补充：新增 `docs/14_PYMATVIZ_CAPABILITY_INVENTORY.md`，明确 Level 0-5 能力分层、9 类 pymatviz/MatterViz/Plotly 能力、原始函数到平台 Tool ID 的映射表，以及 3 个 MVP capability 完整示例。
- 新增 `tool_registry/pymatviz_manifest.yaml`、`tool_registry/matterviz_manifest.yaml`、`tool_registry/platform_builtin_manifest.yaml`，将 10 个 MVP 工具来源拆分为 pymatviz、MatterViz、plotly_custom 和 platform_builtin。
- 新增 `docs/15_ADAPTER_IMPLEMENTATION_PLAN.md`，明确 BaseToolAdapter 接口、执行流程、MVP Adapter 实现顺序和测试要求。
- 更新 `docs/06_TOOL_REGISTRY_AND_ADAPTER.md` 与 `docs/12_MVP_ROADMAP.md`，把 manifest-based Tool Registry 和 Milestone 0 纳入正式实现顺序。

## 当前阻塞

无架构方向阻塞。Milestone 1 scaffold 已完成：本地 infra 配置、FastAPI API 边界、基础 Auth/Project/Dataset 表元数据和 Next.js 工作台 shell 均已有测试或构建证据。当前仍有工程化后续项：建议建立隔离虚拟环境/锁文件，避免继续修改全局 Anaconda 环境；`preview_png` 因 Kaleido/Chromium 依赖仍按 MVP optional 处理；ZIP 解包已具备最小安全解析但仍需补更多安全测试；EXTXYZ with lattice 需要继续验证；当前 Worker runtime 仍是内存语义基线，尚未接入 Celery / PostgreSQL / SSE。

## 下一步

下一步按 Roadmap 继续进入 Milestone 2 / Milestone 4 的交界：建立隔离依赖/锁文件，补齐 parser artifact storage、上传/对象存储边界、更多 ZIP / EXTXYZ 回归测试；随后接 Celery Job Queue、PostgreSQL ToolCall/Artifact 状态持久化和 SSE 事件流。

## 2026-07-04 Phase 9B Official pymatviz Examples Evidence Pack

- Generated a global evidence pack for `C:\Users\86182\Desktop\pymatviz_official_examples_test_suite`.
- Audited all 61 manifest cases and wrote `GLOBAL_CASE_AUDIT.md`.
- Updated `OFFICIAL_BROWSER_VERIFICATION_SUMMARY.md` with honest verdicts:
  - 22 `PASS_WITH_CURRENT_PLATFORM_SCOPE`
  - 30 `PARTIAL_PASS`
  - 9 `FUTURE_SCOPE`
- Browser-verified the two direct-uploadable cases with Mock Planner only:
  - `matpes_atomic_energies_csv`
  - `ward_metallic_glasses_csv_xz`
- Both direct cases now have real upload/profile/job/event/tool-call/artifact/result API evidence, downloaded artifact files, and 4 required browser screenshots.
- Current direct evidence scope is metrics only: persisted AnalysisPlan -> `ml.basic_metrics` -> `metrics_json` artifact -> system-generated report/recipe summary.
- Official richer outputs such as histograms, composition plots, classification plots, phonon, Brillouin zone, and advanced widgets are preserved under `future_expected_*`; they are not claimed as completed.
- Platform fixes made during evidence repair:
  - CSV parser now coerces numeric-looking string columns when safe.
  - Mock Planner now ignores sparse `Unnamed:` columns for metrics selection and uses DataProfile numeric columns instead of hard-coded `y_true/y_pred`.
- True LLM was not used. This remains Mock Planner demo evidence, not live LLM verification.

## 2026-07-06 Phase 10B-1 Composition Visualization Adapter Implementation

- Implemented the second-batch composition visualization adapter set:
  - `composition.formula_statistics`
  - `composition.elements_hist`
  - `composition.ptable_heatmap`
  - `composition.chem_sys_treemap`
  - `composition.chem_sys_sunburst`
- Added shared deterministic composition parsing/statistics helpers for formula column detection, pymatgen-backed parsing, partial-failure warnings, element counts, chemical systems, arity labels, Plotly metadata, summaries, and recipes.
- Registered all five tools through the Tool Registry and adapter registry. Execution remains Tool Registry -> params schema -> adapter -> artifact exporter.
- Updated Mock Planner routing so explicit composition prompts route before generic histogram/correlation/table routing.
- Generated lightweight Ward official-example adapter evidence under `docs/phase10b/adapter_evidence/`.
- This phase did not run real LLM, did not create browser/API evidence, and did not modify QueueWorkerRuntime, AnalysisPlanRepository, or `/planner/jobs` semantics.
- Remaining next step: Phase 10B-2 browser/API/artifact evidence for these composition adapters.

## 2026-07-06 Phase 10B-2 Browser/API Evidence for Composition Visualization Adapters

- Generated end-to-end browser/API/artifact evidence for the five Phase 10B-1 composition adapters under `docs/phase10b/browser_api_evidence/`.
- Verified Ward direct-uploadable composition workflows through Phase 9C UI, Mock Planner, persisted AnalysisPlan, queue worker execution, Tool Registry, adapters, artifacts, reports, and recipes.
- Covered:
  - `ward_formula_statistics` -> `composition.formula_statistics`
  - `ward_elements_hist` -> `composition.elements_hist`
  - `ward_ptable_heatmap` -> `composition.ptable_heatmap`
  - `ward_chem_sys_treemap` -> `composition.chem_sys_treemap`
  - `ward_chem_sys_sunburst` -> `composition.chem_sys_sunburst`
- Evidence totals: 50 redacted API captures, 25 browser screenshots, 19 artifact files, and 5 evidence manifests.
- Security scan result: `NO_SECRET_PATTERN_HITS`.
- Made one evidence-contract fix: `composition.ptable_heatmap` now emits `ptable_heatmap.json` instead of a generic `figure.json`, matching the Phase 10B-1/10B-2 artifact contract.
- No real LLM was used, and default CI remains gated away from live LLM calls.
- QueueWorkerRuntime, AnalysisPlanRepository, `/planner/jobs`, and PlanValidator semantics were not changed.
- Remaining work: Phase 10C lightweight structure planning, structure viewer polish, XRD, RDF, phonon, Brillouin zone, and notebook/script extraction.

## 2026-07-07 Phase 10C-2 Browser/API Evidence for Lightweight Structure Adapters

- Generated end-to-end browser/API/artifact evidence for the five Phase 10C-1 lightweight structure adapters under `docs/phase10c/browser_api_evidence/`.
- Verified simple cubic structure workflows through Phase 9C UI, Mock Planner, persisted AnalysisPlan, QueueWorkerRuntime, Tool Registry, adapters, artifacts, reports, and recipes.
- Covered:
  - `simple_cubic_structure_summary` -> `structure.summary`
  - `simple_cubic_lattice_summary` -> `structure.lattice_summary`
  - `simple_cubic_spacegroup_summary` -> `structure.spacegroup_summary`
  - `simple_cubic_composition_from_structure` -> `structure.composition_from_structure`
  - `simple_cubic_preview_metadata` -> `structure.preview_metadata`
- Evidence totals: 45 redacted API captures, 25 browser screenshots, 15 artifact files, and 5 evidence manifests.
- Security scan result: `NO_SECRET_PATTERN_HITS`.
- Spacegroup evidence used the actual available symmetry path and did not fabricate fallback symmetry.
- No real LLM was used, and default CI remains gated away from live LLM calls.
- QueueWorkerRuntime, AnalysisPlanRepository, `/planner/jobs`, PlanValidator, and existing Phase 10A/10B adapter semantics were not changed.
- Remaining work: Phase 10D advanced structure visualization planning, 3D viewer, XRD, RDF, coordination histogram, phonon, Brillouin zone, and notebook/script extraction.

## 2026-07-07 Phase 10D Advanced Structure Visualization Planning

- Added Phase 10D planning docs under `docs/phase10d/`.
- Current confirmed structure baseline is Phase 10C-2: lightweight structure browser/API/artifact evidence is complete at commit `a20afb3`.
- Defined a four-layer advanced structure roadmap:
  - Layer 1: viewer scene metadata and static export package.
  - Layer 2: static physics plots such as XRD, RDF, and coordination histogram.
  - Layer 3: interactive 3D viewer and Brillouin-zone 3D.
  - Layer 4: phonon bands, DOS, and combined band/DOS.
- Recommended Phase 10D-1 scope is `structure.viewer_scene_metadata` and `structure.viewer_export_package`, with optional schema-only `structure.viewer_3d_contract`.
- Explicitly deferred full interactive `structure.viewer_3d`, WebGL renderer work, Brillouin-zone 3D, XRD/RDF implementation, phonon tools, notebook extraction, and script execution.
- No adapter, Tool Registry, QueueWorkerRuntime, AnalysisPlanRepository, `/planner/jobs`, or PlanValidator implementation was changed in this planning phase.

## 2026-07-07 Phase 10D-1 Viewer Scene Metadata / Export Package Implementation

- Implemented `structure.viewer_scene_metadata` and `structure.viewer_export_package`.
- Did not implement optional `structure.viewer_3d_contract`; the current contract is carried by `viewer_scene.json`.
- Added deterministic static artifacts: `viewer_scene.json`, `viewer_assets_manifest.json`, `summary.md`, and `recipe.json`.
- Registered both tools through Tool Registry with strict params validation and structure resource limits.
- Added Mock Planner routing for viewer scene metadata and static export package prompts.
- Full interactive `structure.viewer_3d`, WebGL renderer, Brillouin-zone 3D, XRD, RDF, coordination histogram, phonon tools, notebook extraction, and script execution remain deferred.
- Browser/API evidence is deferred to Phase 10D-2; Phase 10D-1 evidence is adapter-level only under `docs/phase10d/adapter_evidence/`.
- QueueWorkerRuntime, AnalysisPlanRepository, `/planner/jobs`, PlanValidator, and the default real-LLM gate were not changed.

## 2026-07-08 Phase 10D-2 Browser/API Evidence for Viewer Scene Metadata

- Generated Browser/API/artifact evidence for the Phase 10D-1 static viewer metadata tools under `docs/phase10d/browser_api_evidence/`.
- Covered both registered tools:
  - `structure.viewer_scene_metadata`
  - `structure.viewer_export_package`
- Covered three lightweight input forms: small CIF, small POSCAR, and generated pymatgen Structure JSON.
- Evidence totals: 99 redacted API captures, 30 browser-rendered static preview screenshots, 21 artifact files, and 6 case manifests.
- Verified each case through upload/profile, Mock Planner preview, PlanValidator, persisted AnalysisPlan, `/planner/jobs`, QueueWorkerRuntime, Tool Registry, Adapter execution, artifact generation, result readback, and static artifact preview.
- Security scan result: `NO_SECRET_PATTERN_HITS`.
- Artifacts remain static JSON/Markdown only: `viewer_scene.json`, `viewer_assets_manifest.json`, `summary.md`, and `recipe.json`.
- No real LLM was used, and default CI remains gated away from live LLM calls.
- QueueWorkerRuntime, AnalysisPlanRepository, `/planner/jobs`, PlanValidator, Phase 10A/10B/10C adapters, and the Phase 10D-1 artifact contract were not changed.
- Full interactive `structure.viewer_3d`, WebGL renderer, Brillouin-zone 3D, XRD, RDF, coordination histogram, phonon tools, notebook extraction, script execution, and unsupported official example claims remain deferred.

## 2026-07-08 Phase 10D-3 Viewer Static Preview Hardening

- Hardened the frontend artifact preview for static viewer metadata/export package artifacts.
- Added schema-aware static preview coverage for `viewer_scene.json`, including scene overview, lattice, atoms, bonds, display/camera metadata, limits, warnings, security badges, and raw JSON fallback.
- Added schema-aware static preview coverage for `viewer_assets_manifest.json`, including package overview, artifact list, renderer status, limits, warnings, security badges, and raw JSON fallback.
- Hardened `summary.md` and `recipe.json` previews so static text, deterministic recipe fields, steps, and raw JSON fallback are visible.
- Added browser-rendered Phase 10D-3 static preview evidence under `docs/phase10d/browser_api_evidence/phase10d3_static_preview_hardening/`.
- Evidence totals for this hardening phase: 10 browser-rendered static preview screenshots and 10 committed static browser pages; no new API captures because Phase 10D-2 already covered the API path.
- No new adapter was added, no Tool Registry semantics changed, and QueueWorkerRuntime, AnalysisPlanRepository, `/planner/jobs`, PlanValidator, and the Phase 10D-1 artifact contract were not changed.
- Full interactive `structure.viewer_3d`, WebGL renderer, Three.js, canvas-based rendering, Brillouin-zone 3D, XRD, RDF, coordination histogram, phonon tools, notebook extraction, script execution, and unsupported official example claims remain deferred.

## 2026-07-08 Phase 10E Static Structure Physics Plot Planning

- Added Phase 10E planning docs under `docs/phase10e/`.
- Planned static structure physics candidates:
  - `structure.xrd`
  - `structure.rdf`
  - `structure.coordination_hist`
- Dependency check found `pymatgen`, `pymatviz`, `numpy`, `scipy`, `matplotlib`, `plotly`, and `spglib` available, but Phase 10E does not add dependencies.
- Recommended Phase 10E-1 first target is `structure.coordination_hist` with a conservative deterministic distance-cutoff neighbor policy.
- `structure.xrd` is the second candidate if XRD fixture peak windows and tolerances are pinned before implementation.
- `structure.rdf` remains deferred until normalization, cutoff, binning, and periodic-boundary policies are fixed.
- Official examples for XRD/RDF are future-scope widget/script mappings, not direct-uploadable PASS evidence.
- No adapter, Tool Registry, QueueWorkerRuntime, AnalysisPlanRepository, `/planner/jobs`, PlanValidator, frontend runtime, browser/API evidence, or real LLM path was changed.
- Full interactive `structure.viewer_3d`, WebGL renderer, Brillouin-zone 3D, phonon tools, trajectory RDF, experimental XRD fitting, notebook extraction, script execution, and external API workflows remain deferred.

## 2026-07-08 Phase 10E-1 Coordination Histogram Implementation

- Implemented `structure.coordination_hist` as the first low-risk static physics adapter.
- The adapter uses a deterministic `distance_cutoff` neighbor policy with strict params validation.
- Generated deterministic artifacts: `coordination_hist.json`, `coordination_hist_plot.json`, `summary.md`, and `recipe.json`.
- Registered the tool through Tool Registry and added Mock Planner routing for coordination histogram prompts.
- Added adapter, fixture, registry, planner routing, artifact contract, security, and persisted execution tests.
- Browser/API evidence remains deferred to Phase 10E-2.
- No XRD, RDF, full interactive 3D viewer, WebGL renderer, Brillouin-zone 3D, phonon, notebook/script extraction, external API workflow, or advanced local environment classification was implemented.

## 2026-07-08 Phase 10E-2 Coordination Histogram Browser/API Evidence

- Added Browser/API/artifact evidence for `structure.coordination_hist` under `docs/phase10e/browser_api_evidence/phase10e2_coordination_hist/`.
- Covered three bounded structure inputs: small CIF, small POSCAR, and generated pymatgen Structure JSON.
- Evidence totals: 43 redacted API captures, 6 browser-rendered static preview screenshots, and 12 artifact capture files.
- Verified API/job flow through Mock Planner, PlanValidator, persisted AnalysisPlan, QueueWorkerRuntime, Tool Registry, adapter execution, artifact generation, result readback, and static browser preview.
- Verified artifacts: `coordination_hist.json`, `coordination_hist_plot.json`, `summary.md`, and `recipe.json`.
- Security scan result: `NO_SECRET_PATTERN_HITS`; artifact scan found no script, JavaScript URL, external URL, CDN, Three.js, or eval patterns.
- Negative routing evidence confirms XRD, RDF, full 3D viewer, WebGL, Brillouin-zone, phonon, Voronoi, and CrystalNN prompts do not route to `structure.coordination_hist`.
- No new adapter was implemented, and no runtime main semantics or Phase 10E-1 coordination policy were changed.

## 2026-07-08 Phase 10E-3 XRD / RDF Readiness Decision

- Added Phase 10E-3 readiness docs under `docs/phase10e/`.
- Confirmed `structure.coordination_hist` implementation and browser/API evidence are the current static physics baseline.
- Assessed `structure.xrd` and `structure.rdf` across dependency, fixture, determinism, tolerance, artifact contract, routing, evidence, CI, security, and official-example readiness gates.
- Local dependency check confirms `pymatgen`, `pymatviz`, `numpy`, `scipy`, `plotly`, `spglib`, `ase`, and `pymatgen.analysis.diffraction.xrd.XRDCalculator` are available without adding dependencies.
- Decision: recommend Phase 10E-4 implement `structure.xrd` only.
- Rationale: XRD has available dependencies, small crystalline fixtures, clear static JSON/chart artifact contracts, and manageable tolerance pinning work.
- RDF remains deferred because normalization, cutoff/binning, periodic-image handling, finite-size warnings, and partial-pair policy are not ready.
- Official examples remain mapping references only; no XRD/RDF official example is claimed as PASS evidence.
- No adapter, Tool Registry, QueueWorkerRuntime, AnalysisPlanRepository, `/planner/jobs`, PlanValidator, frontend runtime, browser/API evidence, or real LLM path was changed.
- Full interactive `structure.viewer_3d`, WebGL renderer, Brillouin-zone 3D, phonon tools, notebook extraction, script execution, and external API workflows remain deferred.

## 2026-07-08 Phase 10E-4 XRD Implementation

- Implemented `structure.xrd` as the second static physics adapter.
- The adapter uses existing `pymatgen.analysis.diffraction.xrd.XRDCalculator` with a deterministic CuKa-only policy.
- Generated deterministic artifacts: `xrd_pattern.json`, `xrd_plot.json`, `summary.md`, and `recipe.json`.
- Registered the tool through Tool Registry and added strict params validation for radiation, two-theta range, intensity threshold, peak tolerance metadata, peak limit, HKL inclusion, and stem plot output.
- Added Mock Planner routing for XRD / powder diffraction / diffraction peak prompts.
- Added negative routing coverage so RDF, coordination histogram, full 3D viewer, WebGL, Brillouin-zone, phonon, Rietveld, fitting, and broadening prompts do not route to `structure.xrd`.
- Added adapter, fixture, registry, planner routing, artifact contract, security, and persisted execution tests.
- Browser/API evidence remains deferred to Phase 10E-5.
- No RDF, full interactive 3D viewer, WebGL renderer, Three.js, Brillouin-zone 3D, phonon, notebook/script extraction, external API workflow, experimental XRD fitting, Rietveld refinement, or advanced local environment classification was implemented.

## 2026-07-08 Phase 10E-5 XRD Browser/API Evidence

- Added API/artifact/security/negative-routing evidence for `structure.xrd` under `docs/phase10e/browser_api_evidence/phase10e5_xrd/`.
- Covered three bounded crystalline inputs: small CIF, small POSCAR, and generated pymatgen Structure JSON.
- Evidence generated: 40 redacted API captures, 12 artifact capture files, 6 local static preview pages, and an evidence manifest.
- Verified API/job flow through Mock Planner, persisted AnalysisPlan, QueueWorkerRuntime, Tool Registry validation, adapter execution, artifact generation, result readback, and copied artifact audit.
- Verified artifacts: `xrd_pattern.json`, `xrd_plot.json`, `summary.md`, and `recipe.json`.
- Security scan result: `NO_SECRET_PATTERN_HITS`; generated artifacts and preview pages contain no artifact JavaScript, active script tags, external URLs, WebGL renderer, Three.js renderer, or renderer bundle.
- Negative routing evidence confirms RDF, coordination histogram, full 3D viewer, WebGL, Brillouin-zone, phonon, experimental fitting, Rietveld, Voronoi, and CrystalNN prompts do not route to `structure.xrd`.
- Browser screenshot capture is blocked in this local environment because no in-app browser Node REPL tool is exposed and no Chrome/Edge/Firefox/Playwright/Puppeteer runtime is installed. No screenshot was fabricated.
- No new adapter was implemented, and no runtime main semantics or Phase 10E-4 XRD calculation policy were changed.

## 2026-07-08 Phase 10E-5R2 XRD Browser Screenshot Repair

- Repaired the Phase 10E-5 screenshot gap and upgraded Phase 10E-5 from `PARTIAL_PASS` to `PASS`.
- Detected system Chrome at `C:/Program Files (x86)/Google/Chrome/Application/chrome.exe` and launched it through Playwright `executablePath`.
- Captured six real browser-rendered frontend screenshots under `docs/phase10e/browser_api_evidence/phase10e5_xrd/screenshots/`.
- Browser audit confirms completed job display, artifact list, `xrd_pattern.json`, `xrd_plot.json`, `summary.md`, and `recipe.json` previews.
- `xrd_plot.json` remains a static JSON / static chart metadata preview; rendered stem chart UI is deferred.
- No RDF, full viewer, WebGL renderer, Three.js, phonon, experimental fitting, or Rietveld refinement was implemented.
- No `structure.xrd` core semantics, schema version, runtime authority, Tool Registry semantics, QueueWorkerRuntime, AnalysisPlanRepository, `/planner/jobs`, or PlanValidator boundary was changed.

## 2026-07-09 Phase 10E-6 RDF Policy Hardening

- Added Phase 10E-6 RDF policy hardening docs under `docs/phase10e/`.
- Retained Phase 10E-5 final status as `PASS` after Phase 10E-5R2 screenshot repair at commit `4c7e392`.
- Fixed the first RDF implementation policy:
  - periodic structures only with `pbc == [true, true, true]`;
  - `r_max_angstrom = 8.0` default, bounded `0.5..30.0`;
  - `bin_width_angstrom = 0.1` default, bounded `0.01..1.0`;
  - `normalization = number_density`;
  - ordered center-element to neighbor-element partial RDF pairs;
  - site, bin, neighbor, and partial-pair caps;
  - deterministic sorting and 6-decimal rounding.
- Planned RDF artifacts: `rdf.json`, `rdf_plot.json`, `summary.md`, and `recipe.json`.
- RDF readiness decision: `READY` for a single-scope Phase 10E-7 implementation using existing pymatgen periodic neighbor APIs and small periodic fixtures.
- This phase did not implement `structure.rdf`, did not modify `structure.xrd` or `structure.coordination_hist`, and did not change runtime semantics.
- Full interactive 3D viewer, WebGL renderer, Three.js renderer, Brillouin-zone 3D, phonon, trajectory RDF, experimental fitting, notebook extraction, script execution, and external API workflows remain deferred.

## 2026-07-09 Phase 10F-5 Static Physics Fixture Pack Replay Verification

- Replayed the Phase 10F-4 static physics fixture pack through the platform planner/job/runtime path.
- Fixture-pack replay result: `PASS`.
- Replayed cases:
  - `coordination_hist_small_crystal` -> `structure.coordination_hist`
  - `xrd_small_crystal` -> `structure.xrd`
  - `rdf_small_crystal` -> `structure.rdf`
- Verified selected tool IDs, expected artifact filenames, artifact schemas, static chart artifacts, summaries, recipes, deterministic recipe metadata, and no-JS/no-external-URL security flags.
- Updated fixture pack expected contracts with Phase 10F-5 candidate replay numeric values while keeping `official_pass_claim` false.
- Official examples PASS claims remain none because all replayed cases use `internal_regression` provenance.
- No notebook, external script, benchmark extraction script, external API, real LLM, new adapter, full viewer, WebGL renderer, Three.js renderer, or phonon scope was introduced.
- Recommended next scope: Phase 10F-6 fixture-pack evidence closure.

## 2026-07-10 Phase 10F-11 Viewer Scene Real Browser Evidence Hardening

- Added real browser evidence for the existing `viewer_scene.v1` JSON-only preview surface.
- Added a Playwright/system Chrome evidence runner at `apps/web/test/viewer-scene-browser-evidence.mjs`.
- Captured five browser-rendered screenshots plus DOM and network audit artifacts under `docs/phase10f/evidence/phase10f11_viewer_scene_real_browser/`.
- Covered valid minimal, warning/caps, invalid external-resource placeholder, invalid executable placeholder, and invalid schema-version fixtures.
- Hardened the existing frontend JSON-only preview to show inert `viewer_scene` summary and validation details even when schema validation is expected to fail.
- No full `structure.viewer_3d`, WebGL renderer, Three.js integration, renderer bundle, new adapter, planner routing change, runtime route, notebook, external API, or artifact JavaScript was introduced.

## 2026-07-12 Phase 10F-16 Scientific Structure Inspection

- Added canonical InstancedMesh atom picking, bounded A/B/C/D highlights, site inspector, bounded-bond neighbor summary, distance/angle/signed-dihedral measurement, and local PNG/artifact downloads.
- Measurements use displayed canonical Cartesian positions; minimum-image periodic measurement remains deferred.
- Real Chromium, Firefox, and WebKit evidence uses formal `structure.viewer_3d` jobs and adapter-generated artifacts.
- Canonical schema, formal tool identity, planner/runtime authority, and Phase 10D legacy artifacts remain unchanged.
- npm audit remains seven documented findings with no newly introduced renderer-reachable issue.

## 2026-07-12 Phase 10F-17 Periodic Crystal Inspection

- Added stable canonical-site plus image-offset identity throughout instancing, picking, highlights, inspector, snapshots, and measurements.
- Added bounded exact minimum-image distance and anchored periodic angle/dihedral, independently cross-checked against pymatgen including triclinic input.
- Added renderer-local `1x1x1` through `3x3x3` supercells with 2048-site and 8192-bond derived caps.
- Canonical artifacts and backend runtime semantics remain unchanged; cross-boundary bonds remain a documented contract gap.

## 2026-07-12 Phase 10F-18 Canonical Periodic Bond Topology

- Added backward-compatible v2 scene evolution with explicit periodic bond endpoints, displacement, distance, source, and authority.
- Both canonical viewer adapters generate bounded deterministic pymatgen periodic topology, including orthogonal/triclinic and self-periodic edges.
- Renderer supercells now replicate complete cross-boundary edges; the inspector exposes periodic neighbor identity and highlight actions.
- v1 remains valid as legacy same-cell topology. Distance-cutoff graphs remain non-authoritative.

## 2026-07-12 Phase 10F-19 Periodic Scene Integration Hardening

- Added exact additive capability metadata to `viewer_scene.v2`; bond semantics remain unchanged and v1 remains untouched.
- Added `phase10f19.viewer_assets_manifest.v2` with accurate periodic topology and no-renderer/no-WebGL declarations.
- Unified JSON preview topology counts and endpoint identity with the adapter contract and inspector.
- No renderer, dependency, planner, PlanValidator, or QueueWorkerRuntime semantics changed.

## 2026-07-12 Phase 10F-20 Legacy Viewer Schema Compatibility

- Added executable scene and manifest compatibility matrices mirrored in the frontend.
- Phase 10D is deprecated read-only/JSON-only; canonical v1 remains supported same-cell; v2 is current.
- Mock Planner redirects historical viewer requests to current v2 producers while direct legacy replay remains available.
- Automatic migration is intentionally absent because missing periodic endpoint identity cannot be inferred.

## 2026-07-13 Phase 10F-21 Viewer Performance Hardening

- Added immutable interactive/degraded/refused renderer budgets and fixed resource proxies.
- Near-cap scenes retain all validated topology with DPR 1/no antialias; over-budget scenes stop before engine creation.
- Added explicit generation-token stale protection, context-loss retry, and auditable demand-based scheduling.
- Three-browser/mobile/periodic performance evidence passed without dependency or schema changes.

## 2026-07-13 Phase 10F-22 Viewer Accessibility and Mobile Hardening

- Added a focusable viewer region with bounded keyboard rotate, pan, zoom, reset, and selection-clear actions.
- Added a synchronized semantic scene/topology summary, bounded polite announcements, and a capped semantic neighbor table.
- Removed the mobile scroll trap with `touch-action: pan-y`, established 44px mobile targets, and added reduced-motion/forced-colors policies.
- Chromium, Firefox, and WebKit evidence covers keyboard camera changes, 200% zoom, mobile orientation, one-canvas lifecycle, and zero external requests.

## 2026-07-13 Phase 10F-23 Advanced Picking and Measurement

- Added shared-LineSegments bond raycasting with stable canonical bond identity and fixed selected-bond overlay.
- Added ordered bounded endpoint selection, undo, keyboard atom/bond selection, and exact periodic identity announcements.
- Added deterministic inert `phase10f23.viewer_measurement.v1` local JSON download without scene/topology mutation.
- Chromium, Firefox, WebKit, and mobile evidence covers atom/bond picking, distance/angle/dihedral, cross-boundary endpoints, lifecycle, and network isolation.

## 2026-07-13 Phase 10F-26 Scientific Export and Reporting Foundation

- Added strict bounded PNG/JSON/Markdown export requests and responsive controls.
- Added light, dark, transparent, and high-DPI current-view capture with full renderer restoration.
- Added inert view-state JSON, scientific Markdown, and ordered SHA-256 manifest.
- Added stale cancellation, one-export concurrency, Blob URL cleanup, and safe error codes.
- Chromium, Firefox, WebKit, and mobile evidence observed zero external requests.
- PDF and full report layout remain deferred pending dedicated contract and dependency review.

## 2026-07-13 Phase 10F-27 Formal structure.viewer_3d Product Registration

- Moved the unique `structure.viewer_3d` registry entry to the platform-owned manifest without changing its adapter or runtime semantics.
- Froze the strict product input/output and capability contract around canonical inert scene v2 artifacts.
- Added live planner/job/artifact, three-browser/mobile, accessibility, lifecycle, performance, network, and security evidence.
- Explicit scene JSON remains `structure.viewer_scene`; advanced trajectory, phonon, Brillouin, volumetric, editing, and authoritative chemistry remain unsupported.

## 2026-07-13 Phase 10 Closure Regression Pack

- Added bounded backend, frontend, and real three-browser product composition entries.
- Closed six representative adapter paths through registry, planner, PlanValidator, runtime, artifact persistence/retrieval, and validators.
- Added current/legacy, determinism, fallback, lifecycle, capability-truth, network, and secret evidence.
- Integrated exact closure gates into existing unit, frontend, and PostgreSQL/Redis/MinIO CI jobs without new dependencies.

## 2026-07-14 Phase 10H-1 Phonon Bands

- Implemented the unique planner-visible `phonon.band` adapter for validated canonical JSON and bounded static phonopy band.yaml.
- Added deterministic canonical band/summary/manifest, parse report, Plotly, table, and recipe artifacts through QueueWorkerRuntime.
- Added canonical-only lazy local Plotly preview with branch/segment preservation, negative values, refusal budgets, table/JSON fallback, and cleanup.
- Chromium, Firefox, WebKit, mobile, API, determinism, network, and security evidence passed without new dependencies.
- DOS, combined view, eigenvectors, animation, and phonon calculation remain deferred.

## 2026-07-14 Phase 10H-2 Phonon DOS

- Implemented the unique planner-visible `phonon.dos` adapter for canonical DOS and bounded phonopy total/projected text wrappers.
- Added exact THz/density-Jacobian conversion, explicit total-mode/unit-area normalization, negative-region preservation, and atom/species projection identity.
- Added DOS-specific summary/manifest extensions, report, plot, table, recipe, runtime persistence, and validated local Plotly preview.
- Chromium, Firefox, WebKit, mobile, accessibility, API, determinism, network, and security evidence passed without new dependencies.
- Combined band+DOS, pymatgen serialized input, directional projections, eigenvectors, animation, and calculation remain deferred.

## 2026-07-17 Phase 10J Volumetric Data Contract

- Added five strict inert contracts for grid, payload, field, dataset, and manifest.
- Fixed real-space row-vector affine math, endpoint-excluded periodic grids, `ijkc` component-fastest storage, and structure/lattice binding.
- Added little-endian float32/float64 inline, raw, deterministic gzip, and bounded whole-i-slab chunk payloads with layered SHA-256 identities.
- Added explicit quantity/unit, normalization/integral, collinear/non-collinear spin, complex scalar, potential gauge, statistics, caps, and typed validation.
- Added deterministic fixtures, independent standard-library references, binary payloads, replay hashes, and decompression/security evidence.
- No parser, adapter, tool, planner route, runtime execution, renderer, isosurface, external resource, or dependency was added.

## Phase 10J-1 - Volumetric Parser / Adapter

- Added bounded streaming VASP CHGCAR/CHG/LOCPOT/ELFCAR/PARCHG and single-scalar Gaussian CUBE parsing into the existing Phase 10J contracts.
- Added `VolumetricData`, formal `structure.volumetric_data`, strict params, planner routing, PlanValidator/runtime execution, deterministic binary artifacts, and JSON-only metadata preview.
- Verified canonical order, units, spin channels, affine grids, hashes, a 128-cubed bounded run, typed cap rejection, network isolation, and no artifact execution.
- Renderer, slice, isosurface, multi-orbital CUBE, and production-scale inputs above the parser cap remain deferred.

## 2026-07-20 Phase 10J-2 Isosurface Renderer

- Implementation commit `f6edcac347f2f7fffdbda47b1f72ad493c8edae8` passed local frontend `241` tests, backend `713 passed, 24 skipped`, typecheck/build, real Chromium/Firefox/WebKit WebGL2 and mobile evidence; current-head CI run `29744316126` passed unit, frontend/typecheck/build, PostgreSQL/Redis/MinIO service-backed integration, and no-skipped gates.
- Completion record `c7669619b1444076bc47e8f084ddc2d5df5ce783` passed current-head CI run `29745406355`; the result was verified and the completed Phase 10J-2 queue block is archived.

- Added strict frontend validation and bounded job-scoped raw/gzip/chunked payload retrieval with SHA-256 revalidation.
- Added application-owned Worker extraction using deterministic marching tetrahedra, periodic logical halo, affine/triclinic coordinates, gradient normals, welding, and mesh caps.
- Added lazy application-owned Three.js rendering, structure/cell overlay, layers, picking, clipping, projection, camera controls, PNG, fallbacks, and full disposal.
- Real Phase 10J-1 CHGCAR artifacts rendered in Chromium, Firefox, WebKit, and mobile with zero external requests.
- Slice, direct volume rendering, vector/complex derivation, and scientific field analysis remain deferred.

## 2026-07-20 Phase 10J-3 Charge / Spin Density Product

- Added source-native electron density and explicit signed charge-density product semantics over `structure.volumetric_data`.
- Added allowlisted collinear `spin_up`/`spin_down` fields with fixed formula IDs, source provenance, exact relationships, and full-cell integrals.
- Added product UI with total/spin-difference/up/down modes, paired signed isosurfaces, symmetric threshold lock, warnings, and mobile-safe layout.
- Closed real QueueWorkerRuntime-to-adapter artifacts, Chromium/Firefox/WebKit/mobile browser evidence, performance, accessibility, network, and secret-scan markers.
- Bader, atomic partitioning, non-collinear vector product, potential, slices, and direct volume remain deferred.

## 2026-07-22 Phase 10J-4 Electrostatic Potential Product

- Preserved real LOCPOT as source-defined `local_potential` in electronvolt; no electrostatic-component, vacuum, Fermi, or work-function inference.
- Added strict frontend potential reference/statistics mapping, source-native/cell-average-zero/selected-point-zero gauges, source-contour-preserving layer identity, trilinear point sampling, gauge-invariant point differences, and three Worker-reduced raw lattice-axis profiles with linked 3D planes.
- Reused the Phase 10J-2 Worker/Three.js renderer and captured Chromium/Firefox/WebKit/mobile runtime, profile, performance, accessibility, network, and security evidence.
- Vacuum/work-function/Fermi alignment, cross-calculation alignment, macroscopic averaging, arbitrary slice/path, and direct volume remain deferred.
- Local closure after the final runner hardening passed 258 frontend tests and `722 passed, 24 skipped, 62 warnings` backend tests, typecheck, production build, the historical volumetric/charge-spin/Phase 10 browser pack, and the Phase 10J-4 Chromium/Firefox/WebKit/mobile evidence. The live evidence records one WebGL2 canvas per browser, zero console/page errors, zero external requests, source-contour preservation, three profiles, point difference, PNG signature, and the bounded `128^3` float64 near-cap test. Docker-backed service integration remains a current-HEAD CI gate; the configured npm audit endpoint remains unavailable.

## 2026-08-05 Phase 10M-5 Scientific Report + Recipe Composition

- Strict composition contracts, canonical hashes, deterministic Report, and exact Plan 0.1/0.2 Recipe are implemented.
- Existing Report/Recipe persistence provides atomic, idempotent immutable pairs; no migration or new table was added.
- Workspace preview/finalize/history/Recipe/JSON/Markdown UI and APIs are implemented.
- Corrected implementation `f294fbd305385eb3fd129ab1f815daaca03d15fa` passed CI `30990265619`, including 40 service tests with zero skipped.
- Completion-record exact-SHA CI and verified queue archive remain; Phase 10M-6 is reviewer-gated.

## 2026-08-06 Phase 10N-1 CrystalNN / VoronoiNN Coordination

- N1-R0 exact contract closure is implemented: two stable registry tools, additive
  DataProfile 2.1 readiness, strict algorithm-specific parameters and separate
  coordination Artifact contracts.
- Backend Adapters execute locked pymatgen CrystalNN and VoronoiNN independently;
  periodic-image identity, checksums, bounded coverage and algorithm-qualified
  semantics are persisted through existing Runtime/Artifact authorities.
- Workspace coordination rendering is metadata-first and inert, with deterministic
  consumer-side comparison, exact site selection, Inspector and table fallback.
- Local closure: 1175 backend tests passed, 412 frontend tests passed, typecheck,
  build, lock check, N1 browser Chromium/Firefox/WebKit/mobile fixture replay and
  evidence integrity passed. Docker is unavailable locally; service-backed closure
  is an exact-SHA CI gate.

## 2026-08-07 Phase 10N-1 completion record

- Corrected implementation `08b5eec39bed4fcc93d0a4ef36eb385ba0e9ecc4` passed exact-SHA
  CI `31147539225`.
- CI service-backed closure passed `43/43` with zero skipped, failed, or error cases;
  browser replay and production build passed.
- Completion record is awaiting its exact-SHA CI; the N2 reviewer gate remains
  non-executable and no N2 task exists.

## 2026-08-08 Phase 10N-2 Local Environment + Coordination Polyhedra

- N1 is archived by verified queue commit `a9319c2da44f8794ef7a66347d8f7a0dffe4aa5b`.
- Added the sole approved `structure.local_environment_polyhedra@0.1.0` Tool;
  Registry count is 56.
- The backend Adapter consumes one exact persisted CrystalNN or VoronoiNN
  coordination Artifact through AnalysisPlan 0.2 binding metadata. It never
  discovers, substitutes, merges, or falls back between N1 neighbor sets.
- Added bounded angular-spectrum geometry classification, an allowlisted reference
  catalog, deterministic SciPy ConvexHull faces, explicit partial/ambiguous states,
  distortion metrics, exact lineage, inert artifacts, and declarative Recipe output.
- Added metadata-first Workspace rendering, persisted polyhedron SVG projection,
  exact site selection, Inspector, bounded interpretation, browser/mobile and
  lifecycle evidence. N3 remains reviewer-gated and absent from the queue.

## 2026-08-08 Phase 10N-2 completion record

- Initial implementation `6cb7a534faab5a63f1aa197dc9c202e62d8983aa` failed CI
  `31253016285` on additive-selection compatibility fixtures; no scientific
  contract or authority failed.
- Corrected implementation `2b4dacf400400f5d1a68352d358346b4638d6cb9` passed exact-SHA
  CI `31258820229`: backend 1196 passed, service-backed 44/44, browser matrix,
  typecheck and build passed.
- Completion-record CI and verified queue archive remain. N3 is not executable.

## 2026-08-09 Phase 10N-3 Experimental XRD Comparison

- Admitted one N3 task and reconciled the exact ten-ID acceptance registry.
- Froze R0 authority: existing `structure.xrd` Artifact, strict Resource v1,
  DataProfile 2.2, SciPy detector, deterministic one-to-one matcher and N3 v1
  Artifact.
- Implemented Registry/Adapter/Profile/Plan 0.2/Runtime/Workspace/selection/
  interpretation/Report-Recipe integration without theoretical recomputation.
- Initial implementation `1faa25582107ac3d34efea2e75b61ae3d0f9be13`
  failed CI `31269467363` on one stale service compatibility assertion.
- Corrected implementation `5aef027d312f462eea72a1ced10b33e4f4664a50`
  passed exact-SHA CI `31270117864`: backend 1210, frontend 430,
  service-backed 45/45, typecheck, build and all browser/mobile replays passed.
- Failed completion candidate `e805b8c8d41e69254da21b3209c600f8dce9aa34`
  / CI `31288217113` remains immutable history; corrected completion
  `c7547903faef191c97f35ca0ae2ad1ad1678193f` / CI `31288792343` passed.
- The N3 queue block is removed by the archive candidate; N4 remains reviewer-gated.

## 2026-08-09 Phase 10N-4 Trajectory RDF / MSD / Diffusion

- Verified N3 archive `0a33d84e` and admitted one N4 task.
- Closed N4-R0 with exact trajectory identity, time/cell/PBC, ASE geometric RDF minimum images, NumPy unwrapping/MSD/OLS algorithms, diagnostic thresholds, Artifact schemas, errors, tolerances and caps.
- Implemented three exact Tools, DataProfile 2.3, Eligibility/Planner metadata, typed MSD dependency, Runtime Adapters, Workspace/Selection, interpretation, Report/Recipe and evidence.
- Registry is 60; migration remains 0007; dependency and lockfiles are unchanged; N5 is not queued.
- Local closure passed backend `1221 passed`, frontend `438 passed`, typecheck, production build, Chromium/Firefox/WebKit/390x844 browser evidence, lock, evidence manifest and secret scan. Docker is unavailable locally; exact-SHA CI owns the required 46/46 PostgreSQL/Redis/MinIO result. The configured npm audit mirror remains unavailable with `404_NOT_IMPLEMENTED`.
- Failed implementation candidate `3ae66528a7bffa596793fe6d72ea0e600819be8b` / CI `31298574230` retained immutable history: service-backed 46/46 and frontend/browser passed, while the unit job found Windows CRLF versus Linux LF evidence-manifest hashing. The correction canonicalizes evidence bytes to LF.
- Corrected implementation `2965e585f22cb50ccae87f6d1e5860b5a1b5ba92` passed exact-SHA CI `31299086998`; the completion record is now the active lifecycle gate and the N4 task remains queued.
- Completion record `ca5208feec772e45397f4afbb80419aa6263978f` passed exact-SHA CI `31299648506`; the queue-archive candidate removes the N4 task and leaves N5 at its reviewer gate.

## 2026-08-09 - Phase 10N-5 Implementation Candidate

- Closed N5-R0 with 10/10 acceptance IDs and zero implementation-critical TBDs.
- Implemented strict supplied Band/DOS resources, two Adapters, Profile 2.4,
  Planner/Runtime/Artifact and electronic Workspace/selection/interpretation.
- Registry is 62; schema, migration, public API, dependencies and lockfile are unchanged.
- Implementation exact-SHA CI is the next lifecycle gate; N6 remains reviewer-only.

## 2026-08-09 - Phase 10N-5 Completion Record

- Implementation `34bcea5bd3672d91f3282e12dd5a0cb6b789f1ff` passed exact-SHA CI
  `31311023072`: backend 1242, service-backed 47/47 with zero skipped,
  N5 Chromium/Firefox/WebKit/390x844 replay, typecheck and build passed.
- The N5 task remains queued while completion-record and queue-archive exact-SHA
  CI close. N6 remains reviewer-gated and non-executable.
- Completion candidate `49da783610887c29ee01307884f45f2d9096b287` failed CI
  `31311662979` only on two retained queue-status compatibility assertions;
  service-backed and frontend/browser/build passed. The corrected candidate
  retains the immutable failed SHA/run.

## 2026-08-09 - Phase 10N-6 Integration Closure

- Verified N5 archive `2496d7a9` as entry authority, Registry 62, Profile 2.4 and a clean queue.
- Admitted exactly one N6 task and froze N6-A01 through N6-A10.
- Added aggregate matrices, cross-capability tests, service/browser gates and normalized evidence; no scientific contract changed.
- Failed implementation candidate `ea156ed8` / CI `31315296903` passed unit, 48/48
  services and every browser replay, but the final build was canceled after browser
  server resource accumulation. Linux process-group cleanup and build ordering are
  corrected forward without reducing coverage.
- Corrected implementation `eda7cda4d14207abaf97a0a88cc263b0d1ad3319` passed exact-SHA
  CI `31316556495`: backend 1252, frontend 449, service-backed 48/48 with zero
  skips/failures/errors, typecheck, build and all professional browser replays passed.
- N6 is complete and retains its sole queue task while completion-record CI is pending;
  Phase 11 remains reviewer-gated and non-executable.

## Phase 11-2 Golden Benchmark Completion

- Phase 11-3 admitted the eight invariant records and added locked Linux/Windows CI replay, exact identity/unit comparison, browser display-only variance, and a no-promotion Phase 11-4 handoff.
- Corrected implementation `e89dfaf` passed CI `31332350363`; no V4 promotion or numeric cross-platform claim was made.

- Implementation `5e2f5f07346b7c7d6b7e8d360289cce4ad95ac92` passed exact-SHA CI `31328760532`.
- The suite has 12 cases: 8 invariant passes and 4 explicit reference-limited N/A cases; no validation level was promoted.
- Phase 11-3 remains reviewer-gated and non-executable.

## Phase 11-1 Reference Provenance

Completed the deterministic provenance and fixture handoff pack and started bounded Phase 11-2 golden replay. No external source was downloaded and no production scientific behavior changed. The current suite records 8 invariant replays and 4 reference-limited N/A cases.

Phase 11-4 coverage matrices are now generated from the live Registry and retained evidence. The current
classification is intentionally conservative: Tool coverage is mapping-only, input-path coverage is
reported separately, and official/example records remain mapping-only pending governed extraction.

Phase 11-5 closed the scientific validation baseline from retained evidence.
Reference-limited cases, mapping-only coverage, and the absence of V4 numeric
cross-platform claims remain explicitly disclosed.

Phase 12-0 current UX reality audit is active. It classifies routes, surfaces,
components, viewer/state journeys, accessibility and UX debt only; no production
UI or scientific behavior is changed.

Phase 12-0 audit implementation is verified by exact-SHA CI `31354589883`.
All inventoried surfaces, components, canonical journeys and UX problems are
classified; the result proposes a reviewer-gated experience seal and preserves
all Phase 11 scientific authority.

Phase 12-1 is complete under the approved Design System 2.0 scope. It
consolidates the visual token/status/focus/density foundation and representative
shared presentation only. Implementation `60269556f70f07014224a801150f214887a56ee5`
passed exact-SHA CI `31358512349`. Planner flow, navigation, Workspace/viewer IA
and scientific semantics remain owned by later reviewer-gated phases.

Phase 12-2 is complete. Its implementation adds global navigation actions bound to
existing routes/dialogs/tabs/history, a human-readable Planner stage rail,
progressive plan summary and context-preserving error recovery. UX-001 and UX-008
are closed with evidence; implementation `d046acfcb7ea7741d7cc3567565c2cce9bcb6722`
passed exact-SHA CI `31365743510`. Phase 12-3 remains reviewer-gated.
Phase 12-3 implementation is active under reviewer authorization. The existing
nine panel kinds are presentation-grouped as Overview, Data, Analysis, Results,
Findings, Evidence, Report and Advanced/Provenance. Result summaries and shared
viewer framing are being added without changing scientific or Workspace
authority.

Phase 12-3 is complete. Implementation `9b38a753bda134e9c27425e1193d2980a0790731`
passed exact-SHA CI `31370240101`; result-first hierarchy and shared viewer
chrome are sealed, with UX-002/UX-003 closed and Phase 12-4 reviewer-gated.

Phase 12-4 is complete. Implementation
`9fac62bbb2cc9069da62370ee9d02cf3150e987a` passed exact-SHA CI
`31379672528`; persisted Findings now expose exact supporting, limiting and
contradicting Evidence, source Artifact and provenance paths, the Inspector uses
Summary / Scientific details / Provenance layers, and `UX-004` is closed.

Phase 12-5 implementation `d20d0a1437844a9a69e71fba52cdf57dfd5144db`
passed exact-SHA CI `31386432220`; completion and queue archive were recorded
directly. Phase 12-6 now closes responsive, mobile, keyboard, focus, terminology,
zoom, contrast and reduced-motion engineering for `UX-006` and `UX-009` without
changing scientific authority.

Phase 12-6 corrected implementation `e2beacb0d1e60e5bfccbcd07271f47f5736a221d`
passed exact-SHA CI `31393608850`. Responsive/accessibility engineering is
closed; Phase 12-7 remains reviewer-gated and unqueued.

Phase 12-7 local validation is complete. All eleven canonical journeys, ten UX
problems, twenty decisions and 68 acceptance IDs reconcile with zero authority
mutation. `UX-010` is closed by cross-product consistency evidence; the
deterministic product experience baseline awaits implementation exact-SHA CI.

Phase 12-7 implementation `8fb5dcbe54fbbcd32677107abb5f4117bd04948d`
passed exact-SHA CI `31397995499`. Phase 12 is complete as
`PRODUCT_EXPERIENCE_REDESIGN_VALIDATED_AND_SEALED`; Phase 13 remains at the
reviewer gate.

Phase 13-0 audit generation and governance closure are complete. The deterministic
fact model, scope baseline, claim/limitation registries, exact 62-Tool capability
mapping, 14-row input snapshot, seven demo contracts, fixture checksums,
no-injection policy and 56-ID acceptance registry passed implementation exact-SHA
CI `31451202923` at `6217d042d0190c43144e402e4479aa9810b8e9d0`. No
production UX, backend, scientific or authority change is included.

Phase 13-0 clarification correction generation is complete locally. All seven
demo contracts now inherit the production one-round/three-question limit and
typed second-round failure. Implementation `abe4bd68363f9eb9c357a840b17d0f2c216ebfee`
passed exact-SHA correction CI `31455125693`.

Phase 13-1 deterministic zero-gap preflight is complete locally. All 30 seams
are classified, 11/11 fixtures pass normalized checksum verification, and all
seven demo contracts are ready with explicit nonblocking limits. The seven
demos remain unexecuted pending their own reviewer-gated phase.

Phase 13-1 implementation `d1a60955a77aec000f1e6fd630f0770db545421d`
passed exact-SHA CI `31460352586`; completion and queue archive proceed directly.

Phase 13-2 did not reach UI demonstration execution. Deterministic probes using
the sealed fixtures and user prompts reproduced three P0 product-entry defects
and one P1 documentation-contract defect. Evidence is retained under
`docs/phase13/evidence/phase13_2_seven_real_user_e2e/`; no production UX or
scientific behavior was changed to bypass the failures.

Phase 13-1 fix-forward remediation implementation
`2e47263ac3042663cf901a7fcb8f44e203143e2e` passed exact-SHA CI
`31493208538`. RF-001..004 are closed by minimal product-entry corrections and a permanent
Level-C gate. All seven canonical parser/Profile/Intent/Eligibility/Planner/
PlanValidator slices select the intended existing Tools and validate; all
persistence counters remain zero. Negative Future Scope, unsupported input,
stale binding/profile and second-round clarification controls pass. No Phase
13-2 demonstration has been rerun; completion is recorded and the fix-forward
queue block is directly archived while the failed Phase 13-2 block remains.

The authorized Phase 13-2 rerun stopped during fresh seven-family runtime
preflight. Three new P0 product integration findings are retained as
`P13-RR-001..003`: missing exact runtime object-store bindings for parsed
phonon/electronic resources and an XRD wavelength authority mismatch. Full
service-backed demos remain unexecuted (`0/7`), `P13X2=0/8`, and no production
or scientific code was changed.

Phase 13-1 Fix-Forward #2 is active. A shared exact source-resource lifecycle
now registers all execution-eligible typed parser outputs for immediate and
durable Runtime resolution. Level C remains `7/7`; the new Level C2 resolves
all root refs and validates formal dependencies for `7/7`, with zero execution
object growth. XRD Branch B1 retains strict mismatch rejection and changes no
scientific algorithm. Exact-SHA CI remains required before completion.

## Phase 13-2 Attempt 3 Stop Authority

- `P13-R3-001` proves the real upload-to-fresh-worker boundary is not covered by
  Level C2's manually registered source-resource setup.
- Product upload, Intent, Eligibility, Planner and Redis enqueue pass; durable
  Runtime Profile resolution fails before ToolCall creation.
- Attempt 3 is failed with no production/scientific repair, no demo PASS claim,
  and no Phase 13-3 execution authority.

## Phase 13-1 Fix-Forward #3

- `P13-R3-001` is reproduced and classified at the upload-to-fresh-worker boundary.
- Existing PostgreSQL JSON fields and ArtifactStorage are sufficient; migration remains `0007`.
- Real HTTP upload now durably registers normalized source refs and DataProfile 2.4.
- Executable Planner jobs require durable root resolution before enqueue.
- Level C `7/7`, Level C2 `7/7`, and real service-backed D0 pass locally.
- Implementation `88103ff61584ba81a01ab0e5ebf2adbbc09275e1` passed exact-SHA CI
  `31553972770`; completion is recorded and the active Fix-Forward #3 task is archived.
  Phase 13-2 Attempt 4 passed its current authority, C/C2 and fresh-worker D0
  entry gates, then failed on fresh Demo 1. The canonical prompt planned only
  `dataset.materials_explorer`, omitting sealed Composition Space, and the Plan
  0.1 Workspace was `LEGACY_READ_ONLY`, blocking real-user Report finalization.
  `P13-R4-001` and `P13-R4-002` are open reviewer-action P0 findings. No
  production or scientific behavior changed.

Phase 13-1 Fix-Forward #4 is active. Seven canonical prompts now pass exact
semantic capability coverage (`7/7`) using the existing Intent/Eligibility/
Planner contracts. A fresh Demo 1 real-service smoke selected Composition Space
and Materials Explorer, executed through PostgreSQL/Redis/MinIO/fresh Worker,
and finalized a Report/Recipe through Chromium while the Plan 0.1 Workspace
remained scientifically read-only. Full regression and exact-SHA CI remain.

Phase 13-2 Attempt 5 stopped after five fresh starts and three completed full
product paths. Demos 1-3 passed through real UI Report/Recipe closure. Demo 4
failed at current Workspace Report source eligibility (`P13-R5-001`); Demo 5
failed before Plan/Job because the real upload Profile lacked canonical phonon
capability facts (`P13-R5-002`). Demo 6-7 and downstream suites remain
`NOT_EXECUTED_AFTER_P0_STOP`. No production or scientific repair was made.

Phase 13-1 Fix-Forward #5 is blocked by the Demo 5 user-ingestion authority.
R5-001 was isolated to inconsistent Profile dataset-version fallback in
Workspace currentness and received a bounded exact-identity correction with
29 focused tests passing. R5-002 selected Branch C: direct phonon upload is
Phase 11 `MAPPING_ONLY`, and no supported user-visible typed phonon resource
entry exists. No support promotion, Demo 5 smoke, Attempt 6 task, completion or
archive was created.

Phase 13-1 Release Scope Exception #1 is historically `FAILED / REVIEWER_ACTION_REQUIRED`.
The bounded typed Band/DOS import candidate reached Profile, Planner, real
PostgreSQL/Redis/MinIO, fresh Worker, four registered ToolCalls and 27 persisted
Artifacts. Fresh Demo 5 then failed before Workspace creation with
`PANEL_CAP_EXCEEDED`; deterministic projection exceeded the fixed 32-panel
contract (`P13-RSE1-001`). Fix-Forward #6 applies generic logical-surface/Gallery
projection without raising the cap, then closes fresh Demo 4 and Demo 5 Report/Recipe
smokes. The exception is sealed by FF6; Attempt 6 remains reviewer-gated.

Fix-Forward #6 implementation `0867a69a587bf8e0ddb5aaeec7a177808a69e6f1`
passed exact-SHA CI `31667748439`. Completion records `P13-RSE1-001`,
`P13-R5-001`, and `P13-R5-002` closed; only queue archive remains before the
Attempt 6 reviewer gate.

Phase 13-2 Attempt 6 has executed seven fresh canonical product paths. The
current run records 18 registered ToolCalls and 85 persisted Artifacts with
seven bounded Workspaces, seven Chromium UI finalizations, seven Reports, seven
paired Recipes, and zero unreachable Artifacts. Deterministic negative gates and
the one-call bounded DeepSeek supplemental pass; full regression and exact-SHA
CI remain.

Attempt 6 exact-SHA CI `31682863560` passed for implementation/evidence SHA
`5ddf2c0508a1f61642808a35774917fa3b54b0b0`. Completion is recorded; archive of
the six Phase 13-2 queue blocks remains.

The separate archive lifecycle is complete: Phase 13-2 has zero TASK blocks,
and Phase 13-3 remains an unqueued reviewer gate.

# 2026-08-13 Phase 13-3 Documentation and Reproducibility

Phase 13-2 Attempt 6 is verified and archived. Phase 13-3 is the sole active
task and reconciles current release-facing documentation, seven canonical demo
reproduction contracts, deterministic manifests, limitations, security,
provider, API, and setup guidance. Production and scientific behavior remain
frozen. Phase 13-4 remains reviewer-gated and is not queued.

Phase 13-3 implementation/evidence `c3aabd055e067c5a52a0c0238c625dbc035a96f0`
passed exact-SHA CI `31703805747`. The current release docs, deterministic
seven-demo contracts, clean-checkout verification, service proof, and Linux /
Windows manifest parity are complete. Phase 13-4 remains reviewer-gated.

Completion commit `f4e2bb324ec4c248869cdc022f926d6f40448522` is pushed.
Phase 13-3 is archived from `TASKS.md`; no Phase 13-4 task was created.

# 2026-08-13 Phase 13-4 Targeted Final Product Polish

The reviewer-authorized census contains two handoff items. `P13-POLISH-001` is
`ALREADY_RESOLVED` after a deterministic UTF-8 current-facing scan returned no
repository hits. `P13-POLISH-002` is selected: the existing top-bar Help control
now links to the current Initial Release documentation with localized accessible
naming, unchanged placement and sizing, keyboard activation, and `noreferrer`
external-link isolation. Backend and scientific behavior remain unchanged.

Focused component/i18n tests and Chromium desktop plus `390x844` before/after
evidence pass. Full regressions, cross-engine CI, exact-SHA CI, completion, and
queue archive remain pending. Phase 13-5 is handoff-only and not queued.

Implementation candidate `34f7cb7cea3db351edff0d3b39ff7fe39cd7e192`
failed CI run `31713598663` only in the Phase 13-4 evidence step because the
GitHub shallow checkout omitted sealed entry SHA `d415d05...` required by
canonical nonchange `git show` checks. Product unit tests, frontend/browser,
Linux/Windows replay, and PostgreSQL/Redis/MinIO jobs passed. The correction
fetches that exact historical object before evidence verification; product
behavior is unchanged.

Correction implementation `40403cfa19451cc9a473c41bddecfe053e1a5fea` passed
exact-SHA CI `31715231470`. Phase 13-4 closes only P13-POLISH-002 by turning the
existing top Help control into an accessible link to the current Initial Release
documentation. P13-POLISH-001 remains already resolved. Full backend (`1450
passed`), frontend (`460 passed`), Phase13 focused (`133 passed`), service-backed
CI, retained browser matrix, typecheck, build, lock/diff, Linux and Windows
replay pass. Fact, Scope, Phase12, the reproducibility manifest, canonical
prompts, fixtures, user entries, support matrix, and scientific authority remain
unchanged. Completion is recorded; only queue archive remains. Phase 13-5 stays
reviewer-gated and unqueued. The Phase 13-4 completion record is pushed and its
task block is archived; the queue is empty.

# 2026-08-14 Phase 13-5 Final Regression and Release Acceptance

Entry authority is `ff3f923330acede6c5442cc1226d3bce10b7c299`, with Phase13-4
implementation `40403cfa19451cc9a473c41bddecfe053e1a5fea` verified by exact-SHA
CI `31715231470`. The current Fact, Scope, Phase12, and reproducibility hashes
match their sealed values. Phase13-5 will reuse the established Attempt6 real
service/product runner under a new independent state/evidence root and will not
reuse Attempt6 runtime entities as current PASS. Production remediation is not
authorized. Phase13-6 remains handoff-only and unqueued.

## 2026-08-14 Phase 13-5 Completion

Evidence/validation commit `b60e048abbf366fdbd9fe72da27efd675fc50939` passed
exact-SHA CI `31728986993`. The fresh seven-demo release acceptance, retained
negative and browser gates, and Fact/Scope/reproducibility reconciliation passed
without product, scientific, or support-scope mutation. Phase13-6 remains
reviewer-gated and Initial Release remains incomplete.

## 2026-08-14 Phase 13-5 Queue Archive

The completed Phase13-5 task is archived. `TASK_BLOCK_COUNT = 0`; Phase13-6
remains reviewer-gated and Initial Release remains incomplete.

## 2026-08-14 Phase 13-6 Completion

Implementation/evidence `48b270c6d2c6191b5707f6ee1c4d81a6ab9c8987`
passed exact-SHA CI `31768285019`. The production surface hash is unchanged;
the InitialReleaseManifest and deterministic ZIP are sealed with complete
sanitization, extraction, provenance, claim, limitation, and evidence-index
checks. Phase 13 is complete, `INITIAL_RELEASE_COMPLETE = YES`, no Phase 14
task exists, and queue archive is the only remaining lifecycle action.

## 2026-08-14 Phase 13-6 Queue Archive

Completion commit `7159e0c16de514b73524ef158d6761897d94cf31` is pushed and
the completed Phase13-6 task block is archived. The queue is empty, the Initial
Release is complete, and no next executable phase is created.

# 2026-08-14 Phase A Repository Capability Census

The repository-only capability census is complete. It defines 18 user-level
capability families, mechanically inventories 62 Registry Tools and 42 renderer
contracts, and proposes 36 grounded qualification cases with a 16-case minimum
external-data set. Eight P2 qualification-design gaps remain explicit, chiefly
the lack of a normal-user execution-ready phonon eigenvector import and its
three animation Artifact/renderers. Phase B data research is ready but remains
unexecuted and unqueued.

## 2026-08-16 Phase D Live Qualification Environment Seal

Phase D closed on committed candidate
`54c66abc499c646dc27b612dbf28747b176177c8`. D-R1 migration commit
`d83cb5ffa4c164c01f31de3a181c2e28a51226f4` restores durable namespace
persistence, and the final remediation adds a cross-platform RQ worker
entrypoint. Attempt 6 independently reverified all 16 frozen qualification
contracts, durable services, fresh migration, empty durable namespace,
current-SHA backend/frontend/worker, provider configuration, and browser shell.
The environment is sealed and ready for Phase E; no qualification case or live
LLM call was executed.

## 2026-08-16 Phase D-R2.1 and R1.2 Re-Seal

Normal-user input transport now preserves bounded binary bytes and atomically
publishes parser/contract-identified companion resources into one Dataset. The
final committed product candidate is
`51e45c9436bef73f0c8ea1ccc5eb681dba1d21b8`; R1.2 package SHA-256 is
`7a77b1db55c93454b97914bae3ee9d30e0f08ccc38bfd986c5907f65e38d1d04`.
The R1.2 Phase D environment passed fresh migration, durable service, worker,
namespace, provider, and actual Chrome transport gates with zero formal
qualification execution or LLM calls. Phase E remains unstarted.

## 2026-08-16 Phase E-R1.2 Composition Routing Remediation

The fresh R1.2 discovery campaign passed Q-DATASET-001 and exposed a product
semantic-routing defect in Q-COMPOSITION-001. Source wording such as
"materials table" was incorrectly promoted to `dataset_overview`, allowing the
broad Dataset Materials Explorer to displace explicit formula, element, and
chemical-system analysis. The application-owned Intent reconciliation now
removes that overreach for composition-only table requests, and the Planner
routes the three explicit delivery forms to their already-registered composition
Tools. Registry, Plan versions/cap, scientific support, and the frozen R1.2
package remain unchanged.

## 2026-08-16 Phase E-R1.2 Authority Hard Stop

Q-TABLE-001 exposed `PHASE_E_R12_AUTH_001`: its frozen Case requires
material-property-bound table Tools, but its normal-user CSV produces no
`material_property` Profile columns and the product has no column-role mapping
entry. Correcting this would change qualification-relevant DataProfile or
ToolPlannerMetadata authority, or the frozen package itself. The campaign is
therefore blocked after two discovery PASS Cases; later Cases, final CI, final
Phase D, and final exact-SHA requalification were not started.

## 2026-08-16 Phase B/C-R1.3 Q-TABLE Binding Preflight

The fixture-only replacement route reached a second authority conflict rather
than a product defect. Current Profile semantics accept a real JARVIS table
projected to `formation_energy`, `band_gap`, and `density`, but the frozen
summary/distribution/correlation turns are not current deterministic Intent
phrases and the frozen scatter turn lacks exact distinct x/y target authority.
No semantic aliases, planner metadata, intent vocabulary, tool contracts, or
qualification package were altered. R1.3 is blocked pending Reviewer contract
reconciliation; Phase D and Phase E remain unstarted.

## 2026-08-17 Phase B/C-R1.7 and Phase D Re-Seal

The trajectory authority conflict was closed without expanding product science.
Registry resource-limit metadata now exposes the Adapter's existing 200-frame,
5000-atom trajectory analytics bounds. R1.7 replaces the incompatible positive
analytics fixture with a deterministic contiguous 15-frame source window that
also satisfies the 2,000,000 RDF pair-evaluation budget. No runtime truncation,
resampling, atom subsetting, or algorithm change was introduced.

The generic executability preflight now checks bound Tool parameters against
frame, atom, pair, bin, lag, origin, fit-point, input, and output limits and
models planned dependencies. It reproduces the R1.6 trajectory failure before
execution and passes the replacement fixture. The full 16-Case/26-turn preflight
and an independent Phase D rerun pass. Browser import readiness confirms the
new trajectory Profile; no formal qualification execution or real LLM call was
made. Phase E remains outside this task.

## 2026-08-17 Project History and Dataset Workbench

- Added a durable ProjectHistoryView read model linking imported files and
  normalized resources to DataProfile, analysis jobs, Workspaces, Artifacts,
  Interpretations, Reports, Recipes, and activity.
- Added the project home and a distinct selected-dataset workbench. The latter
  shows the four user-facing process stages, record summary, result/report
  counts, and retains the existing validated Planner entry.
- Removed duplicate run actions from the Planner surface and replaced repeated
  example labels with selectable natural-language examples. Internal statuses
  are translated at the UI boundary while API contracts remain stable.

## 2026-08-17 Release Closure — Complete

- [x] Reproduce and classify every former repository failure.
- [x] Replace live historical queue cardinality with current queue invariants.
- [x] Replace obsolete evidence byte/release-digest gates with semantic checks.
- [x] Pass backend `1563`, service-backed `50`, frontend `465`, typecheck/build,
      all configured browser families, migration, compile, lock, and diff checks.
- [x] Preserve Phase E-R1.7 authority and historical qualification evidence.
- [x] Push normally and verify all configured remote CI jobs in run `32024851926`.
- [x] Finalize and archive Release Closure; deployment remains `NOT_STARTED`.

## 2026-08-18 Production UI/UX Reconstruction

- Production routes now follow Landing → Console → Project → Data / Research /
  Reports while retaining compatibility entry points for historical Analysis
  and Workspace links.
- First-party session authentication and persistent Project research sessions
  are wired through the production API and migrations 0009/0010.
- The Data workbench uses the real upload pipeline, dense searchable scientific
  table controls, keyboard selection, detected-content disclosure, and a
  contextual Inspector without exposing internal IDs.
- Research preserves validated Planner and Tool Registry execution, polls real
  Job events and incremental Artifacts, restores historical runs, and exposes a
  keyboard-adjustable 30–45% conversation/workbench split.
- Current repository regression state: backend 1566 passed / 51 skipped,
  frontend 467 passed, typecheck and production build passed.

### Landing and responsive closure

- Expanded the production Landing beyond the hero and short workflow labels with
  full-width research-context and scientific-result bands using real material
  terminology and a publication-style result surface.
- Changed the Landing H1 to the product name (`材料智能平台`) while retaining
  the research outcome in supporting copy; increased the login modal to a
  560px desktop measure with 44px controls and a mobile-safe 24px inset.
- Disabled the visible Next development indicator with `devIndicators: false`;
  this is a development overlay setting and does not add product UI.
- Chrome geometry evidence confirms no horizontal overflow at 1440/1280/390;
  the final 1440 Landing screenshot was captured after these changes. A later
  Chrome extension overlay blocked the modal recapture and is recorded as a
  browser-tool verification limitation.
- Completed the Research ambiguity continuation: normalized scope candidates,
  persisted the user's selected dataset in the same session, and resumed the
  existing single-dataset Planner contract with the selected Profile.
- Report Reader now loads real run Artifacts and Interpretation
  claims/limitations through the shared scientific viewer; the product remains
  explicitly Run Report scoped.
- Data Inspector focus/Escape restoration, selection semantics, fallback viewer
  keyboard activation, and splitter ARIA/keyboard handling are covered by the
  current frontend regression suite (`74` files / `467` tests).
- Final Chrome evidence was recaptured after the extension overlay was dismissed:
  `design/ux-v1.3/evidence/production/landing-production-1440.png` and
  `landing-login-production-1440.png`. The login dialog measures about 560px
  wide with 44px controls; focus enters the email field, `Shift+Tab` remains
  inside the dialog, and `Escape` closes it with focus restored to the login
  trigger. 1280/390 responsive acceptance remains represented by the previously
  recorded geometry checks; the viewport override was not reliable for a new
  mobile screenshot in this browser session.
- Real local Browser golden-path checks then found and closed three production
  issues: the durable object-store route now imports its repository factory and
  resolves the configured artifact root; the Project Scope Resolver reads the
  current `semanticColumns`/`resourceSemantics`/`analysisReadiness` profile
  contract; and technical recipe/summary/CSV Artifacts are kept out of the
  default Result and Report reading flow. Successful analysis now writes a
  `run` deep-link, and refresh restores the completed run with its 3-row table
  and no internal IDs in the primary UI.
- 200% Chrome verification used an effective CSS viewport of approximately
  915x411 with devicePixelRatio 2.1. Landing, Data, Research, Report Reader,
  and the forced Login modal were checked for overflow, clipping, and readable
  controls. The real zoom-only defect was the 899px breakpoint: Landing minimum
  columns overflowed and the modal exceeded the short viewport. The responsive
  breakpoint is now 960px and the modal is bounded and scrollable. Final
  evidence is stored under
  `design/ux-v1.3/evidence/production/zoom-200/`.
- The user-provided Chrome device emulation was then directly claimed at a
  real CSS viewport of `390x845` (DPR 2). Landing, Login, Data, Research, and
  Run Report were visually checked with `scrollWidth=390`; the Data table and
  Report table retain intentional local horizontal scrolling without page
  overflow. Final mobile evidence is stored under
  `design/ux-v1.3/evidence/production/mobile-390/`.
- Scientific renderer acceptance was rechecked against the current source and
  result contracts. Backend electronic/XRD/trajectory/volumetric/phonon
  coverage passed `62` focused tests; frontend Electronic, Trajectory, Phonon,
  Brillouin Zone, and Volumetric renderer coverage passed `30` focused tests.
  Electronic, XRD, and Brillouin Zone source uploads remain intentionally
  distinct from their derived Result Artifact contracts; the production Data
  page does not claim a source viewer where only a validated result renderer
  exists.
- Console Quick Preview now loads the first real project source resource into
  the shared Scientific Viewer adapter instead of a text-only placeholder.
  Chrome evidence at the user-controlled `390x845` viewport shows the actual
  three-row table, `scrollWidth=390`, and the full-width mobile viewer at
  `design/ux-v1.3/evidence/production/mobile-390/console-quick-preview-390.png`.
  The close/focus behavior has a unit regression and deferred post-render focus
  restoration; repeated Chrome keyboard automation still returns focus to
  `body`, so browser-level focus restoration remains `NOT_VERIFIED` rather than
  being claimed as a PASS.
- Frontend full regression after the Quick Preview change passed `75` files and
  `469` tests. Typecheck and the focused ProductPages tests also pass.
- Project/Research IA discoverability closure (2026-08-18): added an
  authenticated global Project search dialog with Overview/Data/Research
  destinations, exposed the server-owned model status path through the user
  menu and Research configuration notice, made completed process history
  expandable, made unsupported alternatives repopulate the same Research
  composer, and added a direct Run Report link for completed runs. Removed the
  inert Data overflow control. These changes reuse existing APIs and do not add
  a new backend search or report contract.
- Closed two deep-link gaps found in the same audit: Project Overview dataset
  links now select the requested Data resource, and Research session switching
  updates the existing session route for refresh/share recovery.
- DeepSeek configuration audit (2026-08-18): the current process has a
  server-side `DEEPSEEK_KEY`, and `/planner/providers/status` reports the
  redacted provider state as `ready`. The live path is already wired through
  `DeepSeekProvider` for Planner and strict Interpretation; it is not exposed
  to the browser. `.env.example` now documents the optional server-only key,
  allowlisted model, and disabled-by-default test-provider gate. The existing
  `/me/secrets` in-memory API is not a live DeepSeek credential source because
  provider requests reject `secretId`; durable encrypted BYOK remains an open
  product/backend capability rather than being silently claimed as supported.
- Provider configuration is now exposed through a generic server-owned profile
  contract (`provider`, `kind`, `baseUrl`, model allowlist, status, execution,
  and secret-source category). The catalog remains honest: DeepSeek is the only
  `execution=live` profile today; unknown `MDI_LLM_PROVIDER` values report
  `unsupported` instead of silently falling back. No browser key or arbitrary
  endpoint is accepted.
- Production research result closure (2026-08-18): `ml.outlier_table` now emits
  an explicit versioned artifact contract and has a bounded Evidence projector
  for sample count, error values, and maximum/mean absolute error. The Research
  workbench loads persisted Interpretation and Evidence after terminal runs,
  renders grounded claims/limitations, and keeps Artifact results visible if
  interpretation is unavailable. The model service surface is a modal with
  progressive API details; it remains server-owned and provider-agnostic at the
  contract layer.
- Model settings visual closure (2026-08-18): widened the desktop dialog to an
  840px work surface with a two-column fact layout and responsive bottom-sheet
  behavior. Unsupported-provider errors now describe the server catalog rather
  than naming one vendor in the generic API contract. Default Evidence rows no
  longer expose tool or field identifiers; those remain progressively disclosed.
- Generic Provider configuration (2026-08-18): model settings now accepts a
  provider id, Base URL and write-only API Key. Saved keys are encrypted on the
  server and never returned; `/planner/providers/{provider}/models` discovers
  model ids. Research conversations choose the concrete model and neutral
  thinking depth (`quick`, `standard`, `deep`) per request.

## 2026-08-19 Research intelligence projection correction

Research now persists bounded server-owned assistant projections for pre-run,
clarification, unsupported and post-run states. These are observable research
messages and never hidden model reasoning. The default desktop composition puts
the process projection in the left Research Timeline; the right workbench is
reserved for context, data, result and report. Internal pages expose only a
`返回主页` account boundary; explicit login/logout remains on Landing.

The retained-data Viewer closure also resolves durable normalized source
resources after process restart. Q-XRD experimental peaks are rendered as a
single 2theta/Intensity scientific series, and non-periodic Atoms use the
existing structure surface rather than a generic fallback.

2026-08-19 compatibility closure: owner-only historical SQLite schemas without
`project_members` now keep authenticated sessions valid with an owner fallback;
server-side Project authorization remains enforced for protected data routes.
The non-test local API now also selects the durable SQLite repository for
Project History, so retained datasets appear in the new Data Navigator after
an API restart.

2026-08-19 incremental result contract closure: QueueWorkerRuntime persists
each Tool output and emits `artifact.ready` before the next Tool starts and
before the terminal Job event. Research Timeline step state now derives from
persisted `tool.started` / `tool.completed` event step IDs instead of event
counts; an already-ready Artifact remains readable while the Job is running.
A two-step worker regression covers this running-plus-artifact state. This
validates the server/frontend contract; a fresh Chrome observation of a live
non-terminal production run remains separate evidence.

2026-08-19 scientific viewer Chrome closure: fixed trajectory inert scanning so
bounded numeric coordinate matrices are not counted leaf-by-leaf against the
10,000-node metadata/security scan budget; scientific coordinate/value limits
remain unchanged. Added a production-sized 516-atom/15-frame regression and
verified `Q-TRAJECTORY-001` in Chrome with a real canvas, frame controls,
playback and current-frame inspector. The retained phonon route also opened
validated band and DOS panels; electronic source showed persisted eV band data;
volumetric source showed its truthful 125 x 72 x 60 field summary because the
full dataset/manifest 3D contract is not present.

2026-08-19 research presentation closure: after restarting the API with the
project's `uv run ... --app-dir apps/api` environment, a retained Q-TABLE
dataset completed real Research runs through scope resolution, persisted
assistant pre/post messages, Planner/Job/Artifact, strict interpretation and
result presentation. The correlation artifact now projects grounded pairwise
evidence into the user-facing sentence `formation_energy 与 band_gap 的
Pearson 相关系数为 -0.575069。`; the result title no longer exposes the
internal `correlation:<field>:<field>` subject. Chrome confirmed the chart,
numeric table, finding, limitation and evidence section on the production
route. Existing failed and completed turns remain preserved.

2026-08-19 account authorization closure: Project-derived Dataset, upload
session, Job, Artifact, Planner intent/plan/Interpretation, SSE stream and
provider configuration routes now require the authenticated session and inherit
`require_project_access`. `/me/secrets` is user-scoped in the in-memory store;
listing or deleting another user's secret is rejected. Direct upload, profile
generation and legacy demo entry points are authenticated as well. No data was
deleted and CI was unchanged.

2026-08-20 scientific presentation acceptance closure: the retained Phase 10
viewer/result surfaces were rechecked against current production code in Chrome.
Table selection and Inspector, 15-frame trajectory playback, persisted
electronic Band/DOS source projections, the volumetric 125 x 72 x 60 field,
phonon Band/DOS composite (54 band curves + 1 DOS series), Research
complete state, Report Reader and the generic provider model dialog all rendered
without horizontal overflow at the active desktop viewport. Electronic Viewer
chrome and generic scientific plot labels were localized to Simplified Chinese
while preserving canonical scientific identifiers and units. Final browser
evidence is stored under `design/ux-v1.3/evidence/production/desktop/`.

Current regression closure: full Python `1592 passed, 51 skipped`; full
frontend Vitest `79 files, 510 tests passed`; focused authorization/Research/
provider/interpretation/report suite `142 passed`; TypeScript, production build,
compileall and `git diff --check` pass. Incremental-before-terminal remains a
separate live observation debt. BZ source ingestion remains explicitly
unsupported because no normalized BZ source object exists; source volumetric
3D was subsequently closed by the final 2026-08-20 projection below.

2026-08-20 Research intelligence role wiring: the Research pre-run assistant
response now uses the configured Provider when requested by the production
composer, with a strict validated JSON contract over only the question,
selected Dataset and persisted human-readable Plan. Invalid/unavailable output
falls back to deterministic grounded copy and never changes the executable
Plan. Report finalization likewise runs an optional editorial Provider role;
all result/Evidence/Figure references, source identities and numeric statements
are checked against the deterministic Scientific Result projection before the
editorial view is persisted. The new Report Reader consumes that persisted
projection when available. Running remains deterministic with zero LLM calls.

2026-08-20 final volumetric production closure: recognized normalized
VolumetricData values are no longer truncated by the generic structured-preview
list cap. Valid source payloads now project into the strict Phase 10J
dataset/manifest/binary contracts and reuse the same Viewer as derived Results.
Current Chrome rendered the retained Gaussian-cube field at 125 x 72 x 60 as a
real isosurface (24,532 vertices / 47,242 triangles), an exact quantitative
lattice slice, and a WebGL2 direct-volume view. Generic scalar fields no longer
show an irrelevant unavailable charge/spin module or an internal error code;
the visible Viewer controls, states, tables and accessibility labels use
Simplified Chinese. Full regression after closure is Python `1599 passed, 51
skipped` and frontend Vitest `79 files, 510 tests passed`; typecheck, compileall
and the production build pass. After the final Research Turn / Report Composer
role wiring, the full Python result is `1599 passed, 51 skipped`; the frontend
remains `79 files, 510 tests passed`, with typecheck and build passing.

2026-08-20 Structure Viewer language closure: the production 3D structure
surface, controls, supercell, clipping, export, measurement and site/bond
Inspector now use zh-CN product chrome while preserving formulas, units,
scientific identifiers and contract codes. Fresh Chrome reload at the
structure Data route confirmed a real WebGL canvas, no horizontal overflow,
and no remaining primary English viewer labels. Evidence:
`design/ux-v1.3/evidence/production/desktop/data-structure-1829-final.jpg`.
Focused Structure Viewer regression is `25 tests passed`.

2026-08-20 200% production acceptance closure: Chrome remained at browser
zoom 200% while Data Table, row Inspector, Research Planning/Running,
Research Complete, Structure Viewer, Report Reader, and Landing were opened
from real production routes. Page-level `scrollWidth` matched `clientWidth`
for the checked routes; deliberate table/document vertical scrolling remained
available, essential controls stayed reachable, and the Research Complete
view exposed one completion summary rather than a duplicate mobile/zoom
summary. Evidence is stored under
`design/ux-v1.3/evidence/production/zoom-200/`. The production title
projection also strips internal `Current acceptance` labels and timestamp
suffixes from ordinary Project/Data headings without changing stored names or
audit identifiers.

The 200% run was authenticated, so Landing opened in the logged-in state;
fresh Login Modal interaction was not repeated in this pass to avoid logging
out the active session. Existing modal implementation and focus evidence
remain separate from this logged-in Landing check.

2026-08-20 Phase 10 retained-data IA reachability audit: the current production
routes were checked against the Phase 10F-N capability/evidence records and the
new Project/Data/Research/Reports IA. Table/DataFrame, periodic Structure and
non-periodic Atoms, Trajectory, experimental XRD, Electronic Band/DOS, and
Phonon Band/DOS are reachable from Project > Data through the authenticated
normalized-resource endpoint and shared ScientificViewerAdapter; companion
objects remain grouped by their scientific context. Result-only capabilities
(Trajectory analytics/RDF/MSD, XRD peak matching, coordination/local
environment, BZ, Volumetric, Materials ML and Composition Space) are reachable
from Research > scientific result through the persisted Artifact renderer
registry, Inspector/Evidence and Report Reader. Interpretation, Evidence and
Run Report are reachable from the Research result and Reports routes using the
same persisted run/artifact identity.

The audit found no route-level dead link requiring production code changes.
Two capability boundaries remain intentionally explicit: Brillouin-zone data
has no normalized source object type, so its source Data view is
`NOT_SUPPORTED` while `brillouin_zone_json` result artifacts use the dedicated
renderer; uploaded VolumetricData currently exposes the truthful bounded grid/
field summary because it does not contain the strict Phase 10J
`volumetric_dataset.v1` plus manifest bundle, while a validated result bundle
uses the full VolumetricPreviewPanel. These are documented capability limits,
not empty Viewer fallbacks. Historical Phase 10 evidence and qualification
records remain unchanged; no CI or qualification campaign was modified.

# 2026-08-19 — Scientific presentation and account-bound research closure

- The production Data route now passes a dataset-scoped normalized resource bundle through the shared scientific viewer adapter. Atomic structures, Electronic Band/DOS, Phonon Band/DOS, and experimental XRD plus structure context reuse existing renderer contracts; raw volumetric source remains an explicit grid/field summary until its dataset/manifest renderer contract exists.
- Research assistant messages are durable, bounded projections of persisted facts: pre-run copy is derived only from the validated plan and post-run copy only from a persisted scientific interpretation. Inline process remains a reconstruction of observable run state, never model private reasoning.
- Report composition requests now carry the authenticated browser session and enforce the same project authorization boundary as the rest of the product. Result evidence that is bound to a rendered artifact provides a user-facing route back to that artifact, without inventing a row/site/peak highlight where the underlying selection contract is absent.
- 2026-08-20 research intelligence closure: introduced strict Research Turn Orchestrator, Scientific Interpreter, and Report Composer projection contracts. They consume persisted scope/plan/interpretation/artifact facts only, reject private reasoning and credential-shaped text, and fail closed on dangling Evidence or result references. Existing Planner/Tool Registry execution remains unchanged.
- 2026-08-20 Research Timeline copy closure: retained Plans now project human-readable Chinese step labels from persisted scientific tool metadata (including XRD, trajectory, electronic, phonon, volumetric, composition, ML, table, and visualization capabilities). Unknown capabilities use a non-technical Chinese fallback; machine Plan contract text remains hidden without modifying historical Plans.
- 2026-08-20 incremental-result evidence closure: added an automated two-step registered-adapter observation that records persisted `artifact.ready` before terminal dependency completion, verifies the Artifact is readable at the event boundary, and confirms the Job is not yet terminal for those observations. No artificial delay or execution-semantic change was introduced; browser live observation remains unverified because the local worker completes synchronously.

- 2026-08-20 final scientific Viewer/browser closure: removed the generic
  100,000-item JSON truncation from recognized normalized volumetric channel
  values while keeping ordinary resource lists bounded. The retained
  `125 x 72 x 60` Gaussian-cube source now reaches the strict Phase 10J
  dataset/manifest/binary projection and rendered a real WebGL isosurface in
  the production Data route (24,532 vertices / 47,242 triangles). Source
  metadata is consumed from its attached, validated source Artifact instead of
  incorrectly requesting a synthetic `source-view` Job. Chrome 390 x 844
  checks for Landing, Table Data, Table Inspector, Research Complete, Report
  Reader, and Volumetric Data reported no page-level horizontal overflow;
  Research Complete exposes exactly one completion summary and its retained
  phonon result rendered three Plotly surfaces. A retained BZ result was also
  reopened from the new Research support-output disclosure and rendered one
  WebGL canvas. BZ source ingestion remains unsupported because no normalized
  BZ source object exists; this is distinct from the verified result renderer.

- 2026-08-20 Volumetric source Viewer closure: the Data SourceResourceAdapter
  now deterministically projects bounded normalized `VolumetricData` payloads
  (`shape`, affine origin/steps, boundary conditions, channels and finite
  values) into the existing Phase 10J dataset/manifest/payload contracts.
  Periodic VASP-like sources require the supplied structure/lattice hashes;
  non-periodic Gaussian cube sources remain unbound and do not receive
  fabricated structure metadata. The projection uses deterministic little-
  endian float64 hashes, uses inline payloads up to 262,144 values and exact
  hashed in-memory binary artifacts for larger retained fields within the
  16 MiB browser budget, rejects mixed boundaries, singular grids, non-finite
  values, unsafe metadata and browser-cap-exceeding voxel/value counts, then
  reuses the existing `VolumetricPreviewPanel` for source Data, slice,
  isosurface and volume modes. Focused adapter/contract coverage is `12 tests
passed`; ProductPages, VolumetricPreviewPanel and adapter effects are `20
tests passed` together; TypeScript typecheck passes. The prior raw grid/field
  summary remains the honest fallback when a source payload cannot satisfy
  this projection. The retained 125 x 72 x 60 source grid is covered by the
  binary projection test rather than falling back solely because it exceeds
  the inline-JSON cap.

2026-08-20 final debt classification: semantic accessibility is verified by
source and production-DOM audit, with the audit artifact at
`design/ux-v1.3/evidence/production/accessibility/semantic-audit.md`.
Real hardware screen-reader execution remains `NOT_VERIFIED`; this requires an
available NVDA/VoiceOver-equivalent device. Non-terminal incremental Artifact
ordering is verified by the two-step Worker regression but remains
`NOT_OBSERVED` in Chrome because the local Worker completes synchronously.
`npm run lint` remains an engineering-hygiene debt: the repository has no ESLint
configuration or installed ESLint CLI and Next's deprecated `next lint` opens an
interactive initializer. No product or accessibility defect is hidden behind
that status, and no unrelated tooling migration was introduced.

2026-08-20 batch acceptance closure: all 39 retained scientific Projects were
opened through the production Research/Data/Report routes with the configured
server-side provider. Current durable counts are 42 Projects, 39 Datasets,
109 Jobs, 615 Artifacts, 208 Messages and 42 Interpretations. Latest usable
Runs were kept visible; 35 superseded terminal Runs are reversibly archived.
Batch browser evidence is under
`design/ux-v1.3/evidence/production/batch-20260820/` and the companion JSON
records `batch-20260820-*.json`. Table, Structure, Trajectory, XRD, Electronic,
Phonon, Volumetric, Result and Report surfaces were inspected against retained
data. The three expected unsupported atomic cases and one corrupt legacy
dataset remain honest unsupported states rather than fabricated results.

Acceptance debt remains explicit: automated two-step artifact ordering is
verified but a non-terminal incremental result was not observable in Chrome
because the local worker completes synchronously; semantic accessibility is
verified while a physical screen-reader device is not available; BZ source
ingestion is unsupported while BZ result rendering is supported; full Phase E
live requalification is preserved historical evidence and was not reopened.

2026-08-20 Project discoverability correction: the retained scientific
Projects are qualification Case runs, not phase-owned Projects. Their primary
names now follow `Case NN · Q-ID · Run NN`; three message-only sessions and one
legacy dataset follow `其他 · title · Run NN`. Human-readable descriptions show
the demonstrated capability and Phase 10 lineage, for example phonon
dispersion/DOS/BZ linkage (`Phase 10H / 10I`) and volumetric isosurface/slice/
direct-volume rendering (`Phase 10J`). The Projects page groups Case, genuine
Phase and other records, sorts Case/Run names numerically, and searches names,
Q-IDs and capability descriptions. Chrome verified 42 records and a
`Phase 10H` search returning exactly the two Q-PHONON runs.

2026-08-20 run-history closure: added reversible project-scoped Run archival as
a visibility projection in the existing `project_configs` JSON document. Job,
Artifact, Message, Evidence and Report records are never deleted or relabelled;
Project History keeps archived Research runs reopenable and the default Reports
list excludes only explicitly archived terminal runs. Archive and restore are
authorized write endpoints. Focused `tests/test_project_history.py` passes 3.

2026-08-20 Project/Dataset management UX in progress: Console and Projects now
provide a single primary creation path with an immediate upload continuation.
Project and Data Navigator rows share a low-noise action menu reachable by
right-click, visible/focusable `More`, keyboard context-menu commands, and touch;
explicit selection mode introduces the only batch toolbar. Rename, reversible
archive/restore, and owner-only empty-object deletion are server-authorized.
Read-only Project History now projects the true membership role and omits
upload/mutation affordances. Focused backend access/history tests are 10/10,
focused Product/upload Vitest tests are 11/11, typecheck passes, and the current
full frontend suite is 80 files / 518 tests passed. Chrome validation awaits an
authenticated session in the user-selected Chrome surface.

2026-08-20 role-boundary closure: direct Dataset upload deep links now resolve
the Project History role before rendering a file input; viewer members receive
a readable read-only state instead of a doomed upload form. Research Session
creation and message writes now require Project write access server-side, while
read-only members retain timeline, result and report access. Research Composer,
session-history creation, and report archive controls follow the same explicit
role boundary. Focused Product/Research Vitest is 25/25, project access/history
regression is 19 passed, and typecheck/build remain green. Final Chrome
management evidence still requires a user-authenticated browser session.

2026-08-20 Project/Dataset management Chrome closure: authenticated Chrome
verified Console new-project modal entry and exact opener focus restoration;
Projects grouping (42 records / 38 Case runs); the shared More/context menu via
visible trigger, right-click, and Shift+F10; explicit selection mode with a
transient batch bar; and safe management affordances. The Data route verified
a real 64-row table, Dataset menu, row Inspector, Escape focus restoration,
and no material desktop horizontal overflow. Empty-project deletion was
exercised against a sparse historical schema; the server skips absent optional
metadata tables while retaining owner/write checks and all child blockers. No
non-empty scientific history was deleted. Full Vitest is now 80 files / 525
tests; Python and browser-independent gates remain green. Final 390px Chrome
verification also passed: Projects, the management bottom-sheet menu, the
creation dialog, the real 64-row Data table, and the Inspector all stayed
within the viewport; Inspector Escape restored the selected-row trigger.
2026-08-20 continuous product quality Wave 1: corrected a scientific-safety defect in
the Data property table so units are never inferred from field names; undeclared units
now read “未声明” and semantic roles use a bounded Chinese label map. Research now has
explicit loading/error/retry states instead of presenting a failed request as an empty
permission view. Research Records moves focus into its popup, localizes session status,
and restores the trigger on Escape. At <=960px Research uses one active panel at a time
(`对话` / `工作台`) with one primary scroll owner; Data table controls and management
targets are touch-safe and wrap without horizontal overflow. Reports now distinguish
loading/error/empty states, prioritize PRIMARY_FIGURE then PRIMARY_TABLE, and put the
primary result before conclusion/limitations in the reader. Focused frontend regression
is 27/27 and typecheck passes. Fresh Chrome visual evidence is pending reconnection to
the user Chrome tab after the local Web restart; no browser claim is made for this wave.
2026-08-20 Wave 1 follow-up: validated object types now take precedence over filename/profile heuristics, so phonon band/DOS cannot be routed to the electronic viewer. Result loading treats the selected Artifact as required and companion Artifacts as best-effort; a failed optional sibling no longer hides a readable primary result. Generic table previews now disclose the total row count and preview cap, and unknown source objects use an explicit unsupported state instead of a guessed recipe/JSON renderer. Desktop Chrome rechecked the real Q-TABLE-001 route (64 rows, source-owned units not guessed) and the trajectory Research timeline. Final 390×845 Chrome acceptance passed: Research owns one active 对话/工作台 panel with no viewport overflow, the Data table owns its 594px horizontal canvas inside a 390px scroll region, row selection and Model Settings close controls are 44px, Inspector Escape restores the exact selected-row trigger, and Report list/reader remain within the viewport.

2026-08-21 Continuous Product Quality Wave 2 closed: Research Run ownership is now a
normalized, project-scoped `research_session_runs` projection with Alembic backfill
from legacy assistant payloads, idempotent reassignment protection, and readable
pre-migration fallback. Planner requests carry the validated `researchSessionId` and
terminal interpretation reconciliation persists the post-run assistant projection
server-side; failed runs are bounded and deduplicated. Historical Run reopening now
keeps partial/error states honest, merges overlapping JobEvent/Artifact polling
responses, prevents orphan Runs from attaching to the first session, and links Result
to Data/Report/Research. Provider/session load failures expose retry states, while
mobile Research remains a single active panel. Chrome verified retained Case 11 /
Q-STRUCTURE-RDF-001 Run 02 at desktop and 390px: no document overflow, Data/Report
links remained actionable, and the historical result restored after asynchronous
loading. Full Vitest is 80 files / 539 tests; full Python is 1611 passed, 51 skipped;
typecheck, build, compileall, Alembic head, and diff-check pass. Plotly warnings remain
the existing dependency-level build warning; real screen-reader hardware and a
non-terminal incremental browser snapshot remain explicitly NOT_VERIFIED.

2026-08-21 Wave 2 copy refinement: the deterministic Research Turn projection now
frames the selected dataset as `数据集“…”` and uses a neutral “以数据集为范围”
sentence. The frontend also normalizes the same legacy pre-run prefix at display
time, so retained sessions improve immediately without rewriting historical Messages.
This keeps scientific dataset identifiers exact while removing awkward
Chinese/English grammar mixing in retained assistant messages. Unsupported-state copy
uses the same dataset framing.

2026-08-21 exact Structure research and workbench closure: the Chinese request
`查看当前结构的径向分布与局部环境` now stops before execution until the user
chooses CrystalNN or VoronoiNN, then preserves the exact coordination producer,
local-environment polyhedra consumer and RDF workflow. Composite local-environment
plus experimental-XRD prompts retain both dependency chains. Oversized approved
tables no longer erase smaller safe interpretation evidence; Research and Report
present coordination coverage/ranges and algorithm limitations in user-facing
Chinese. Authenticated browser acceptance created and completed real Run
`job_07f702a3c9af42259ec5d14f` with exactly three validated steps and rendered
5 RDF series / 400 values. Desktop geometry was measured at 1280x720: global bar
0-56, project nav 56-100, workbench 100-720; conversation and result panes remain
620 px high with independent scrolling and no root scroll. Pointer and keyboard
splitter controls are bounded to 320-640 px. Full Python is 1618 passed / 51
skipped; full Vitest is 82 files / 552 tests; build, typecheck, compileall,
Alembic head and diff-check pass. Existing Plotly/glslify build warnings remain.

2026-08-21 acceptance and CI closure in progress: Windows Narrator was started
and an independently focused Chrome product page exposed named banner/nav/main,
Research log, controls, adjustable separator, scientific chart region and live
status semantics. Browser keyboard traversal followed the visual order through
global/project navigation, Research records, completed runs, composer, model
control, splitter, Data/Report links and numerical disclosure. The Windows
automation safety layer could not retain a URL-qualified connection, so
captured speech output remains an explicit verification boundary; no auditory
claim is fabricated. A frontend regression now proves a persisted scientific
Artifact renders while its Job remains `running`, complementing the existing
threaded runtime test that proves `artifact.ready` precedes terminal completion.
The design-system split contract is aligned to the measured 420 px default,
320-640 px bounds and 480 px minimum result surface.

2026-08-21 CI experience refinement: current push gates now separate live
product protection from sealed qualification evidence. The default Python gate
excludes explicit `qualification` modules that require the ignored local
`_qualification/` workspace; those tests remain runnable on demand. The old
Phase 13-4 Help browser selector was removed from current gating after clean CI
showed it targeted the retired `/analysis` compatibility structure. All retained
Phase 10/12 historical browser replays are still available behind one manual
orchestrated step, reducing CI navigation noise without deleting evidence.

2026-08-21 current browser-gate correction: Phase 12-6 responsive/accessibility
and Phase 12-7 cross-product checks were aligned with the shipped project-scoped
Research workbench. Their deterministic browser fixtures now satisfy auth,
project history, session, dataset, and Provider reads while preserving the
read-only boundary; keyboard skip navigation targets `research-primary-content`
and the splitter assertion targets the Research workbench separator. The retired
`/analysis` compatibility page is no longer treated as the current product
surface.

2026-08-21 acceptance and CI closure completed: local current-HEAD equivalents
passed (default Python `1586 passed, 1 skipped, 82 deselected`, explicit
qualification `30 passed`, Vitest `83 files / 554 tests`, typecheck, build,
Phase 12 browser evidence, and evidence integrity). The pushed current HEAD
`0df1e97` passed remote CI run `32454012102` across all five jobs. The workflow
now keeps current product gates on push while exposing sealed Phase 10/12
browser replays as one explicit manual orchestration step; no scientific,
security, migration, service-backed, or accessibility coverage was removed.

2026-08-21 Research history navigation Wave 3 completed: the Research record
popover now supports local title search, bounded scrolling, explicit empty and
no-match states, a visible result count, current-session semantics, and robust
focus/close behavior for Escape, outside pointer input, and navigation. Mobile
search text is 16px. The UI now presents `sessions.status=active` as “可继续”
rather than incorrectly implying that a Planner Job is still running; actual
queued/running Job states continue to use “进行中”. The authenticated retained
Structure/RDF project was inspected at 1280x720: the overlay stayed within the
viewport, search received focus, no-match feedback was exposed, outside-click
closed the overlay, and document width remained 1280px.
Implementation commit `ca8a8b4` passed current-HEAD CI run `32463181783`,
including complete frontend tests, typecheck/build, current Phase 12 browser
gates, Python unit tests, service-backed integration, and scientific replay on
Linux and Windows.

2026-08-21 Mobile Research navigation Wave 4 completed: the single-panel mobile
switcher now has explicit tab/tabpanel IDs, roving tabindex, Arrow/Home/End
navigation and focus movement. A validated Planner job moves the mobile view to
the Workbench immediately after creation, so users see the real running process
instead of remaining on the composer. Phase 12-6 Chromium 390x844 evidence
asserts these semantics and confirms only one panel is visible; desktop dual-pane
behavior is unchanged. Implementation commit `3dccce8` passed current-HEAD CI
run `32464949831`, including complete frontend tests, typecheck/build, current
Phase 12 browser gates, Python unit tests, service-backed integration, and
scientific replay on Linux and Windows.

2026-08-21 Wave 5 completed: global navigation controls now remain available
on internal project routes. Account actions use a compact menu with explicit
menu semantics, Escape/outside dismissal, keyboard traversal, and focus
restoration; the mobile trigger and menu remain bounded at 390px. Scientific
result fallback previews now expose bounded JSON with a type/count summary and
honest empty/unavailable states. Research result technical details now show
auditable run/plan identity and output availability, while payload loading and
secret storage remain server-owned. Commit `e0b84e5` passed current-HEAD CI
run `32473415268` across Unit, Frontend, Service-backed Integration, and
Linux/Windows scientific replay.

2026-08-22 Research activation Wave 6 implementation: the empty Research
conversation now presents the authorized project-data count and up to three
stable starter questions derived only from Project History `datasetType`,
`readyCapabilities`, and `semanticRoles`. Suggestions fill and focus the
existing Composer without creating a Session, Message, Plan, or Job. Exact
formation-energy/band-gap comparison appears only when both semantics exist;
unknown capability sets fall back to a neutral project-data overview. Empty
write-capable Projects link to Upload instead of retaining a doomed Composer,
while read-only Projects expose no write action. The right workbench now owns
only project-data and recent-research context, eliminating duplicated static
suggestions. Suggestions selected from a mobile Workbench recovery state return
to the conversation panel before focusing the Composer. Local verification
passed Research Vitest `32`, complete Vitest
`84 files / 565 tests`, typecheck, production build, Phase 12-7 evidence
integrity `5`, and Chromium/Firefox/WebKit plus 1280x720 and 390x844 browser
checks. Implementation commit `1032d10` passed current-HEAD CI run
`32514219078` across Unit, Frontend, Service-backed Integration, and
Linux/Windows scientific replay.

2026-08-22 Agent 2.0 Phase 1 foundation: verified the prior Alembic head was
`0014_research_session_run_bindings` and added ordered `0015`/`0016`/`0017`
migrations for Scientific Objects, Research Turns, and Result Snapshots. Added
typed Pydantic contracts, explicit registries, repository/service boundaries,
immutable context snapshots, CAS state machine, authorized REST/SSE/object
reads, and receive-boundary No-LLM/No-Job tests. An isolated PostgreSQL
container passed `0014 -> 0017 -> 0014 -> 0017`, migration constraints,
version/turn concurrency, and service-backed receive. A compatibility defect
where old partial SQLite fixtures omit interpretation/report tables was fixed by
making legacy FKs conditional on real parent tables; complete production
schemas keep all applicable FKs.

2026-08-22 Agent 2.0 Phase 1 closure: implementation `1553183b` and the
dynamic-Alembic-head integration correction `9af205b8` are pushed. Current-HEAD
GitHub Actions run `32567895104` passed Unit Tests, Frontend Typecheck & Build
with current Phase 12-6/12-7 gates, PostgreSQL/Redis/MinIO integration (`51
passed, 0 skipped`), and Linux/Windows scientific replay. The deterministic
foundation is complete; no Phase 2 LLM, orchestration, capability planning,
production result projection, interpretation, or Viewer work was introduced.

2026-08-22 Agent 2.0 Phase 2 orchestration completed: added deterministic
candidate assembly from exact UI scope, recent terminal context and persisted
Results; immutable context compilation/fingerprint; opaque reference keys;
fixed source priority; pre-provider ambiguity clarification; versioned
`research-orchestrator/1.0`; existing-transport DeepSeek structured output;
one bounded repair; typed failure; immutable decision persistence; honest
action routing; Redis `turn_id` wakeup; product SSE; and strict C01-C15
evaluation. Focused, SQLite migration, isolated PostgreSQL/Redis, live DeepSeek,
complete backend/frontend regression and current-HEAD CI run `32573620585` pass;
the Phase 2 TASKS block is archived in `results.md`.

2026-08-22 Agent 2.0 Phase 3 completed: `PLAN_READY`,
immutable CapabilityResolution/CapabilityPlan evidence, nine capability
manifests, deterministic eligibility, real XRD/trajectory planned-output ports,
typed provider-facing port contracts, bounded alternative-strategy planning,
exact Tool binding and existing AnalysisPlan 0.2 validation are implemented.
Current Result bundles can be reused only through authorized exact-version
ScientificObject outputs. Deterministic, full backend, frontend, isolated
PostgreSQL/Redis and live DeepSeek gates pass; an end-to-end processor test
proves one Plan and zero Job/ToolCall/Artifact rows with duplicate delivery as
a NOOP. Implementation `855fe3f` passed current-HEAD CI run `32580235322`
across Unit, PostgreSQL/Redis/MinIO integration, Frontend with Phase 12-6/12-7,
and Linux/Windows scientific replay. The user-facing execution state remains
unchanged until Phase 4.

## 2026-08-23 Agent 2.0 Phase 4 execution activity

- Added a compact Research activity surface for `QUEUED`, `RUNNING`,
  `CANCELING`, `RESULT_PENDING`, `FAILED` and `CANCELED` without turning the
  conversation into a backend status wall.
- Scientific step labels come from registered capability metadata and actual
  runtime state. Product payloads omit Job, ToolCall, Tool, queue, worker and
  provider identifiers.
- Persisted, declared Artifacts may appear as incremental outputs before the
  Job is terminal; their presence never implies scientific interpretation.
- `RESULT_PENDING` uses explicit copy that execution has finished and
  scientific results are being prepared. It is not rendered as final research
  completion.
- The cancel control remains keyboard reachable with a 44px touch target;
  important status updates use bounded `aria-live` output and never steal
  focus from the composer.
- Browser evidence covers 1440x900 and 390x844, with no horizontal overflow,
  a single mobile panel, visible real-step state and stable composer ownership.
- Local Phase 4 verification now includes `1671 passed` non-integration backend
  tests, `54 passed` fresh PostgreSQL/Redis/MinIO service tests, and `568 passed`
  frontend tests. A real two-step XRD fresh Worker was paused after its first
  committed Artifact notification; the parent observed the Job still running
  and the incremental output already available before allowing step 2 to run.
- Implementation `4384db3` passed current-HEAD GitHub Actions run
  `32592517424` across Unit, PostgreSQL/Redis/MinIO integration, Frontend with
  Phase 12-6/12-7, and Linux/Windows scientific replay. Phase 4 is complete.

## 2026-08-23 Agent 2.0 Phase 5 result projection

- Added `RESULT_READY` after `RESULT_PENDING` and migration
  `0021_agent2_scientific_result_projection`; the existing snapshot table
  remains the only Agent 2 result authority.
- Replaced fixture result-projector registration with deterministic canonical
  projector registrations for RDF, XRD, ML regression, trajectory and phonon
  families. Numeric facts require committed artifact locators; image artifacts
  can only produce figures.
- Added immutable typed bundle components, source fingerprinting, relevance
  evaluation, authorized projection/result APIs, idempotent conflict-closed
  projection persistence, and the minimal `RESULT_READY` Research activity.
- Phase 5 still does not interpret results, call an LLM, create Jobs or
  ToolCalls, or generate an assistant final answer.

## 2026-08-23 Agent 2.0 Phase 5 closure qualification

- Added automatic identity-only Redis/RQ result projection after the committed
  Phase 4 `ExecutionSummary + RESULT_PENDING` boundary. A fresh result worker
  reloads PostgreSQL/MinIO authority and is recoverable by `turn_id`; the
  manual projection endpoint is no longer the normal production trigger.
- Replaced generic canonical payload wrapping with typed adapters for the nine
  current RDF, XRD, ML regression, trajectory and phonon production schemas.
  Numeric facts are restricted to declared summary fields with committed
  Artifact locators; curves remain structured Figure/Table data.
- Dedicated PostgreSQL/Redis/MinIO fresh-process qualification passed RDF and
  two-step XRD with zero selected skips, concurrent delivery convergence,
  owner/outsider API authorization, zero projection LLM/Job/ToolCall delta,
  and a 390x844 browser result-ready/no-overflow evidence capture.
- Local closure gates passed: Agent2 focused `105 passed, 5 skipped`; full
  backend non-integration `1691 passed, 6 skipped, 88 deselected`; frontend
  `569 passed`; typecheck/build/compileall/lock/diff-check/migration passed.
  Closure implementation `1fd18bf995ee6ffc38cbfacf6f5af1fca54a7b9f`
  passed authoritative pre-Phase-6 current-head CI run `32617347658`; all five jobs
  succeeded. Phase 5 closure verdict is COMPLETE.

## 2026-08-23 Agent 2.0 Phase 6 grounded interpretation

- Added bounded `ScientificInterpretationOutput 1.0` processing from
  `RESULT_READY` through deterministic grounding to the final assistant
  ResearchMessage. Raw Artifact content and hidden reasoning stay outside the
  interpreter input.
- Added exact fact/evidence/result-item reference validation, numeric value and
  unit grounding, one bounded repair, mandatory PARTIAL/relevance notices,
  immutable interpretation persistence, and previous-result zero-execution
  routing.
- Added automatic identity-only interpretation queueing and a fresh worker
  entry point. Fresh PostgreSQL/Redis/MinIO RDF and two-step XRD qualification
  passed with independent execution, result, and interpretation workers.
- Phase 6 local gates passed: deterministic `8 passed, 1 skipped`; Agent2
  focused `89 passed, 6 skipped`; live DeepSeek `1 passed`; service-backed `2
  passed` with zero selected skips; full backend `1731 passed, 65 skipped`;
  frontend `85 files / 570 passed`; typecheck, production build, compileall,
  lock, migration round-trip, diff-check, and authenticated 390x844 browser
  overflow verification passed.
- Implementation `2b9ad6155a7c63dfd3efe15868aeaae72e172116` passed current-head
  GitHub Actions run `32621337675`: all five retained jobs succeeded, including
  the dedicated Phase 6 PostgreSQL/Redis/MinIO fresh-process qualification
  with no selected integration skips. The Phase 6 verdict is COMPLETE.

## 2026-08-24 Agent 2.0 Phase 7 research memory (complete)

- Added durable, versioned ResearchSession state and auditable context items
  for explicit session constraints, pinned exact object/result references,
  goals, active scope/selection, and open questions.
- Extended Phase 2 candidate assembly with deterministic explicit/UI/current/
  previous/pinned/recent/long-session priority, bounded non-adjacent results,
  grounded finding references, and opaque provider keys.
- Extended the compact compiler budget so explicit constraints and pinned
  results survive low-value conversation trimming; raw Artifact payloads and
  internal database identities remain outside provider context.
- Existing Phase 6 zero-computation result interpretation and Phase 3–6
  continuation paths are reused. The Windows isolated-service `localhost -> ::1`
  connection defect was fixed with a test-only `127.0.0.1` normalization; worker
  readiness is measured separately from scientific execution and the 180-second
  execution bound is unchanged.
- The fresh interpretation fixture now references real persisted Fact/ResultItem
  identities and satisfies the frozen Phase 6 schema/grounding contract. Fresh
  RDF reuse, RDF continuation, XRD reuse and stale exact-version cases pass with
  independent PostgreSQL/Redis/MinIO processes. Phase 7 deterministic (`8
  passed`), live DeepSeek (`3 passed`), full backend (`1739 passed, 72 skipped`),
  frontend (`85 files / 571 passed`), browser and migration gates pass.
- Closure head `24dcfdb777a63b62a2537fdb081be12653fc3fc5` is pushed and
  current-head CI `32657590810` passes all five required jobs with service-backed
integration `62 passed, 0 skipped`. Phase 7 is COMPLETE; Phase 8 remains out of
scope for this record. A post-closure provider-boundary audit also replaced
database UUIDs in compact prior-turn context with stable opaque labels; focused
memory tests pass and server-side fingerprints remain unchanged.

## 2026-08-24 Agent 2.0 Phase 8 grounded scientific reports

- Reused the existing `reports` table as product Report identity and retained
  legacy Workspace Report/Recipe compatibility. Migration `0024` adds only the
  recoverable Agent2 generation lifecycle and immutable exact result/
  interpretation snapshot binding.
- Added bounded opaque Report Composer input, structured output 1.0, strict
  finding/fact/evidence/figure/result/source reference checks, numeric and unit
  grounding, one bounded repair, identity-only RQ processing, and zero-
  scientific-computation idempotency.
- Added authorized generate/read/list APIs, dynamic effective relevance on read,
  a completed-turn on-demand action, scientific Report list, and a four-level
  responsive reader with legacy fallback.
- Deterministic, live DeepSeek, real PostgreSQL/Redis/MinIO RDF/XRD, full backend
  and frontend gates are recorded in `AGENT2_PHASE8_RESULTS.md`.

## 2026-08-24 Agent 2.0 Phase 9 scientific viewers (in progress)

- Added deterministic exact-version ScientificViewerRegistry/projection APIs
  with bounded table, trajectory and volumetric payload handling and safe
  source-missing fallbacks.
- Added a shared ScientificViewerShell and product-level viewer registry that
  reuses existing structure, table, Plotly, electronic, phonon, BZ and
  volumetric renderers instead of creating a second scientific data model.
- Added `ScientificSelectionContext 1.0` and migration `0025` so semantic site,
  peak, frame and field locators are captured in immutable ResearchContext
  snapshots with repeated project/version authorization.
- Data Viewer research links now carry exact object/version and bounded
  selection context into the Agent2 ResearchTurn endpoint. Report figure links
  expose an authorized exact source viewer when one is available.
- Focused backend viewer/selection tests, frontend tests (90 files / 581
  tests), typecheck, compileall, Ruff and migration round-trip currently pass;
  browser and current-head CI closure remain outstanding.

### Phase 9 fixture/worker closure update (2026-08-24)

- A canonical scientific table is now produced through the normal upload,
  parser/profile, artifact manifest and `ScientificObjectService` promotion
  path; no database rows are fabricated. The authenticated table viewer shows
  bounded rows, scientific columns and semantic row selection.
- A fresh Windows RQ `SimpleWorker` consumed the authenticated selection turn
  and persisted immutable `ScientificSelectionContext` snapshots. A second
  selection produced a separate snapshot without mutating the first.
- Local SQLite and artifact defaults are now repository-absolute so API and
  worker processes started from different working directories share the same
  authority and viewer payloads.
- Phase 9 remains PARTIAL only for the grounded Report -> Figure/Evidence ->
  exact Viewer path: the legacy persisted RDF result has no valid exact source
  object refs, so the product correctly avoids same-name substitution.
### Phase 9 legacy history compatibility (2026-08-24)

Authenticated fixture rerun exposed an old `AnalysisPlan` row without
`analysis_plan_json`, which caused project history to fail with HTTP 500. The
read projection now degrades that legacy plan to an absent plan payload while
keeping strict validation for newly persisted plans. This preserves historical
job/result visibility without changing scientific authority.

### Phase 9 provenance-first closure rerun (2026-08-24)

The fresh PostgreSQL/Redis/MinIO Phase 5 pipeline produced current-generation
RDF and XRD results whose persisted `source_object_refs` contain the exact
ScientificObject and ScientificObjectVersion used by execution. A fresh Phase
8 report worker then produced a new grounded report whose viewer sources are
derived only from those result refs. Empty-ref legacy results intentionally
resolve to no viewer source; name, filename, latest-version and project-local
substitution remain forbidden. This closes the provenance root cause as
CASE_A, while authenticated browser verification against the fresh PostgreSQL
report still requires an environment exposing that service-backed dataset.

The subsequent Codex in-app-browser retry authenticated successfully and
re-ran the canonical local table at desktop and mobile sizes. The table showed
bounded rows, scientific columns and semantic row selection with no global
overflow or console errors. The local acceptance database still contains only
the legacy empty-provenance report, so the fresh PostgreSQL Report -> Viewer
browser path remains intentionally unclaimed.
### Phase 9 same-stack browser retry (2026-08-25)

The authenticated in-app browser was pointed at the PostgreSQL-backed API and
production frontend. A fresh grounded report opened its exact source Viewer;
the URL preserved object/version provenance and the Viewer showed the expected
historical-version warning. The same project also rendered the bounded
Scientific Table. The browser runtime exposed no viewport override, so fresh
390px evidence remains open; no SQLite evidence is being carried forward as
canonical.

The existing Playwright runner subsequently completed the fresh same-stack
390x844 Table gate with real authentication: 3/3 bounded rows, scientific
columns, semantic row selection, zero global overflow and zero runtime errors.
Only release C/D exact-SHA CI provenance remains open.

### Agent-2.0 Phase 10 Batch 1 capability expansion (2026-08-25)

Phase 10 Batch 1 freezes eight new semantic Agent2 capabilities over existing
production adapters: structure coordination (distance-cutoff, CrystalNN and
VoronoiNN), trajectory RDF, electronic band/DOS inspection, composition-space
exploration and bounded materials exploration. The existing nine Phase 3
capabilities remain active. New payload schema envelopes and canonical Result
projectors preserve exact source object/version refs and declared units; no
AnalysisPlan version, migration, Viewer architecture or execution path changed.

`tests/test_agent2_phase10_capabilities.py` passes 24 deterministic cases.
Live provider, service-backed execution, authenticated browser and release CI
remain unverified and are intentionally not claimed as Phase 10 completion.

### Phase 10 browser context retry (2026-08-25)

The real authenticated same-stack browser now submits deep-linked exact
object/version references through the explicit research context channel. The
fresh session snapshot retained only the exact Structure; the subsequent
coordination request was rejected by the existing typed eligibility gate
(`CAPABILITY_REQUIREMENT_UNSATISFIED`) because the persisted acceptance
fixture does not expose the capability's semantic input contract. No execution
records were fabricated and Phase 10 remains partial.

### Phase 10 canonical fixture readiness recheck (2026-08-25)

Fresh current-generation Structure, Electronic Band, and Materials Table
fixtures now satisfy their production DataProfile contracts. Structure and
Electronic have real PostgreSQL/Redis/MinIO execution and grounded Result
evidence; the final Dataset chain also completes with exact object/version
provenance and a valid grounded interpretation. The historical silicon object
remains a deliberate fail-closed negative case.

The existing Research UI now dispatches a `PLAN_READY` turn through the normal
API rather than leaving it queued in the browser. Authenticated Chromium smoke
passes Table mobile and Structure/Band desktop, and the Structure click path
reaches an exact ContextSnapshot plus a deterministic two-capability plan.
Repeated local diagnostic runs exhausted the API PostgreSQL connection pool
before a clean dispatched three-family browser execution could be recorded;
therefore Phase 10 remains PARTIAL and no completion commit/CI is claimed.

### Phase 10 Stage 0 pool diagnosis (2026-08-25)

The browser retry's PostgreSQL exhaustion was traced to the API database
factory: route handlers created a new SQLAlchemy Engine (and a fresh
5-connection pool with overflow) for every request. A live
`pg_stat_activity` snapshot showed 98 idle sessions after repeated polling,
with no idle-in-transaction accumulation. The fix is a process-scoped,
configuration-keyed Engine cache plus explicit teardown disposal; health-check
engines with special connect arguments remain isolated. The lifecycle regression
repeated engine creation eight times and verified one pool with no checked-out
connections after each request (`46 passed, 1 skipped` targeted suite).

The API/worker runtime was stopped after capturing the baseline, so a clean
post-fix authenticated three-family browser dispatch and current-head
service-backed rerun remain outstanding. Phase 10 is still PARTIAL; Phase 11
execution has not started.

### Phase 10 clean runtime closure attempt (2026-08-25)

The process-scoped engine fix was exercised in the live stack. PostgreSQL
settled at `active=1`, `idle=6`, with zero idle-in-transaction sessions after
the authenticated polling campaign. The terminal-progress supervisor now
reprojects completed turns idempotently instead of returning a false conflict.

Fresh authenticated Chromium execution then completed all three canonical
families against the same PostgreSQL/Redis/MinIO data plane:

- Structure Turn `21d40ce4-c299-485f-8b34-db29f1416dc8`, exact
  `773089f9-3ce8-4645-92dd-2f62c64cba89` /
  `65f56d10-008d-445d-ab2f-228aebf1835b`, CrystalNN + VoronoiNN, grounded
  Result and Structure Viewer.
- Electronic Band Turn `e96b22af-0bf5-4ef2-962e-05d20a5afe93`, exact
  `54017eba-e71e-4af0-8d79-763124bbd72d` /
  `0a389623-928d-4500-8dd3-b1759921a940`, grounded Result and Band Viewer.
- Dataset Turn `6d16ce68-6cf1-4d93-8147-6d76fa35a784`, exact
  `b8a1a55b-d32f-45f3-b421-df075dc3c05d` /
  `622ef3d7-301c-420a-aa75-7dda551cf7ef`, canonical typed source/Profile
  bridge, grounded Materials Explorer/Table result.

The fresh browser paths reported zero fatal errors, unhandled rejections,
critical API failures and authorization failures. Current verification is
`1791 passed / 83 skipped` backend, `582 passed` frontend, typecheck/build,
touched Ruff, compileall, lock and diff checks PASS; service-backed is
`12/12 PASS, 0 skipped`. Functional Stage 0 evidence is therefore complete,
but no P10-A/P10-B commit or exact-SHA CI has been created. Phase 10 remains
PARTIAL and Phase 11 has not started.

### Phase 11 trusted Capability Pack boundary (2026-08-25)

Phase 10 is sealed at `fd23073009f92120d32efc710d57e457ed4c92ea` with
exact-head CI. Phase 11 adds a repository-trusted declarative extension
boundary around the existing `CapabilityManifest` contracts. Default
capabilities are grouped into scientific-family Packs and validated
atomically against the existing requirement, object-type, Tool, Result
projector and progress-projector authorities. Contract and binding
fingerprints preserve stable capability identity while implementation
bindings evolve. The provider-facing catalog contains semantic capability
summaries only and never raw Tool IDs or executable metadata. No migration,
dynamic loader, or new scientific algorithm is introduced.

### Agent-2.0 Phase 12 data authority audit (2026-08-25)

Phase 12 execution is tracked in
`docs/agent2/phase12_data_platform/PHASE12_TASK.md`. The audit confirms that
`scientific_objects`, `scientific_object_versions`,
`scientific_object_relationships`, exact Result source refs, and
ArtifactStorage already form the single Agent2 data authority; no duplicate
ScientificObject model or migration is justified for the current increment.
The bounded `PATCH /api/scientific-objects/{object_id}` metadata/lifecycle
boundary was added with project write authorization. It changes labels and
archive/restore state only, preserving immutable version identity and exact
historical refs. Focused domain/API tests pass. Full authenticated browser,
service-backed Phase 12 campaign, and P12-A/P12-B exact-SHA CI remain open.

### Agent-2.0 Phase 12 continuation (2026-08-26)

The data-platform increment now also provides a typed, bounded Dataset query
for an exact ScientificObjectVersion, with checksum validation and stable row
identity. Touched Python files pass Ruff; Agent2/API/Viewer focused tests are
`25 passed, 4 skipped`, the full backend is `1802 passed, 83 skipped`, and
frontend tests/typecheck/build remain green.

Authenticated same-stack Chromium completed Structure Turn
`63e68fed-eb0f-4675-aaed-1bc1479efd81` for exact object/version
`773089f9-3ce8-4645-92dd-2f62c64cba89 /
65f56d10-008d-445d-ab2f-228aebf1835b`; the turn reached `COMPLETED` with
valid grounded interpretation and independent CrystalNN/VoronoiNN results.
A generic request lacking required semantic comparison was rejected as
`UNSUPPORTED` without execution, preserving fail-closed eligibility.

Phase 12 remains PARTIAL: the Data→Research version/archive browser lifecycle,
fresh mobile Data evidence, current-head service-backed campaign, and
P12-A/P12-B exact-SHA CI remain open. The current Phase 5 service-backed
result-worker does not reach terminal completion after queueing, which is the
confirmed runtime blocker preventing a COMPLETE claim.

### Agent-2.0 Phase 12 recovery (2026-08-26)

The result-worker symptom was reproduced against PostgreSQL/Redis/MinIO. The
execution worker completed successfully, persisted Artifacts and an immutable
ScientificResultSnapshot, and reached `RESULT_READY`. A shared interpretation
worker then consumed the wakeup without the Phase 5 provider fixture and moved
the Turn to `FAILED`; the initial fixture also read obsolete MinIO credential
variable names. The narrow test-only correction now aliases the supported
MinIO credential names and disables interpretation while the Result projection
gate is asserted. The service-backed Result projection test passed three
consecutive runs (`2 passed` each).

Authenticated Chromium also verified the exact Dataset query, archive/restore
metadata boundary, and the canonical Data page at `390x844` with no global
overflow. Full version-lifecycle browser evidence and P12-A/P12-B CI remain
open, so Phase 12 remains PARTIAL.

### Agent-2.0 Phase 13 scientific presentation foundation (2026-08-26)

Phase 12 is sealed at `b4cd4c025b05532f03d10b67108abd40c8c2b887` with
exact-head CI, so Phase 13 begins from that immutable baseline. The initial
presentation increment adds a bounded, read-only presentation compiler for
authorized Agent2 Results and Report snapshots. It consumes exact result
facts, evidence, artifacts, validated interpretations, and exact
ScientificObjectVersion references to emit semantic presentation blocks
(`narrative`, `finding`, `metric`, `table`, `figure`, `viewer_reference`,
`evidence_reference`, `limitation`, `warning`). It neither creates scientific
facts nor performs “latest” resolution, Tool execution, or dynamic UI loading.

The Agent2 Result endpoint now exposes only bounded, authorized exact Result
facts and source references needed for this projection. Research and Report
surfaces reuse this renderer while retaining the existing Viewer and Report
authorities. Numeric and unit display remains sourced from immutable facts;
unsafe HTML/script-like block content is rejected. Phase 13 functional,
browser, service-backed, and release qualification remains open.

### Agent-2.0 Phase 13 selection and historical Viewer verification (2026-08-26)

The presentation follow-up exposed and repaired a pre-existing generic-table
selection defect: Dataset rows with `sample_id` were falling back to formula
labels and visual row-derived keys. The selection runtime now prefers the
durable `sample_id`, binds the row to its Dataset identity, and disables
selection when no stable semantic locator exists. A focused runtime regression
passes and authenticated Chromium now displays and hands off
`DATASET_SAMPLE / mat-2` with the exact Dataset object/version token.

The same-stack browser path also verified the scientific-object lifecycle
action: canonical Structure object archive changed only lifecycle status,
historical exact v1 remained directly renderable with the historical-version
notice, and restore returned the object to ACTIVE without creating a version.

### Agent-2.0 Phase 13 presentation authority completion (2026-08-27)

The Agent2 result boundary now exposes bounded persisted `evidence` and
artifact descriptors in addition to exact source refs and facts. The
interpretation endpoint exposes the already-validated interpretation object,
allowing the shared deterministic presentation compiler to render claim-level
findings, metrics, evidence paths, figures/tables, limitations, and warnings
without treating assistant text as a second scientific authority. Artifact
payload bytes remain behind existing authorized artifact routes.

Focused presentation/runtime tests pass (`18 passed`), Agent2 API tests pass
(`14 passed`), frontend typecheck and production build pass, and the full
current backend/frontend suites remain green (`1807 passed / 85 skipped`,
`590 passed`). Release CI and final Phase 12/13 closure evidence are still
pending; no completion verdict is claimed from local checks alone.

### Agent-2.0 Phase 13 final-seal qualification (2026-08-27)

The current worktree was requalified without changing the frozen Phase 12
authority. The existing Scientific Object Viewer already exposes the
authorized archive/restore action; the Data Platform list now requests
`ACTIVE` or `ARCHIVED` objects explicitly for default discovery, while an
explicit object/version route bypasses that filter so historical Viewers
remain addressable. Authenticated Chromium verified ACTIVE → ARCHIVED →
ACTIVE with unchanged scientific version identity and exact historical
Viewer resolution.

Current local qualification is green: backend `1810 passed / 83 skipped`,
frontend `91 files / 591 tests passed`, typecheck, production build,
compileall, `uv lock --check`, touched Ruff and `git diff --check` pass.
P13-A/P13-B release commits and exact-head CI remain pending; no COMPLETE
verdict is claimed until those release gates are observed.

### Agent-2.0 Phase 13 detailed gap scan (2026-08-27)

P12-B exact-current-head CI completed successfully as run `33040374649` for
`49398ecfb630d83301a38a647b94ae5b97f55a59`. A fresh Phase 13 audit confirms
that the compiler/renderer foundation is present, but current-worktree
qualification is not yet a closure: the running browser API is still a local
SQLite/local-queue process, the visible acceptance projects expose legacy
planner runs rather than a current Agent2 Result presentation, and no
dedicated presentation service campaign, result-reuse delta proof, or
P13-A/P13-B exact-SHA CI exists. These are recorded in
`docs/agent2/phase13_scientific_presentation/PHASE13_GAP_SCAN.md`; Phase 13
remains `FAIL/PARTIAL`, with Phase 14 not authorized.

### Agent-2.0 Phase 13 second detailed scan (2026-08-27)

A code-level follow-up confirms the remaining Phase 13 debt is broader than
browser screenshots. Project history does not expose an explicit
`researchTurnId`, so historical presentation recovery relies on the fragile
`job_agent2_<32hex>` naming heuristic. The new Figure/Table blocks are still
descriptor-only, Evidence blocks are labels rather than a navigable bounded
Finding → Result → ToolCall/Artifact → exact-version path, and no current
Agent2 grounded Report snapshot has rendered in the authenticated browser.
The current browser API also reports SQLite/local/local backends despite the
real PostgreSQL/Redis/MinIO services being available. These findings are
recorded in the Agent2 Phase 13 gap scan; no Phase 13 COMPLETE or Phase 14
authorization is claimed.

### Agent-2.0 Phase 14-R context provenance increment (2026-08-28)

Phase 14-R now has a bounded ContextManifest 2.0 contract. Resolved research
context builds immutable per-item provenance (authority class, source identity,
opaque provider reference, inclusion reason, selection mode, exact object/version
and content fingerprint) plus bounded budget/compaction state. The manifest is
stored inside the immutable `CONTEXT_RESOLVED` event payload and is exposed only
through the authorized `GET /api/research/turns/{turn_id}/context-manifest`
projection. Research UI renders a bounded “本次研究使用的上下文” disclosure;
the normal Turn view does not leak provider-facing manifest internals. Focused
backend/context tests and frontend typecheck pass. Phase 14-R remains open for
the broader lifecycle, viewer, report, search, recovery, performance and
real-user qualification tracks.
### Agent-2.0 Phase 14-R historical identity hardening (2026-08-28)

Research history navigation no longer derives a scientific Turn from the
legacy `job_agent2_<32hex>` Job naming convention. When the server-projected
history contains an explicit persisted `researchTurnId`, the UI passes that
exact identity; otherwise a legacy run remains viewable through its run route
without guessing a scientific Turn. This preserves fail-closed historical
resolution for non-standard Job identifiers. ResearchPages focused tests and
typecheck pass.

### Agent-2.0 Phase 14-R report context hardening (2026-08-28)

Report generation now validates a frozen `ReportContextBundle` immediately
before the existing structured provider boundary. The bundle contains only the
bounded research question, Result projection, validated interpretation,
evidence references, opaque refs and omission ledger; raw conversation,
provider transcripts, credentials and unbounded Tool payloads remain outside
the contract. Existing Report Phase 8 tests (16 passed, 4 historical skips),
compileall, touched Ruff and diff checks pass. Full Report browser/service
quality remains open.

### Agent-2.0 Phase 14-R history message binding hardening (2026-08-28)

Project History now prefers the persisted `ResearchTurn.user_message_id` when
recovering a modern run's user question, while retaining the bounded
timestamp-based fallback for legacy `research_session_runs`. Exact-message
relations are checked against the bound session before use, so malformed
cross-session links cannot disclose another conversation's content. The
focused history suite passes (`7 passed`); Phase 14-R remains open for the
broader mature-product qualification tracks.

The same-stack historical/reuse service suite was rerun with the repository
`services/llm` package on subprocess `PYTHONPATH`: `4 passed`, `0 skipped`.
The earlier import error was test-environment configuration only.

The shared service-worker environment now includes `services/llm` directly,
so fresh subprocess qualification does not depend on a caller-provided
`PYTHONPATH` alias.

### Agent-2.0 Phase 14-R report history continuity (2026-08-28)

The Scientific Reports index now labels each compatibility/history entry as
either a recoverable persisted ResearchTurn session or a legacy session-run
projection. Existing report URLs and scientific authorities are unchanged;
the label makes the recovery boundary explicit to users. Focused frontend
test and typecheck pass.

### Agent-2.0 Phase 14-R dependency impact preview (2026-08-28)

Project and Dataset lifecycle dialogs now consume bounded, server-derived
dependency impact projections before permanent-delete actions. The secured API
enumerates persisted dependencies under the existing project-write
authorization boundary and keeps physical deletion fail-closed when references
exist; the UI explains that archive preserves historical provenance. No
lifecycle authority or scientific version semantics changed. Focused
project-access tests (`11 passed`) and ProductPages tests (`17 passed`) pass.

### Agent-2.0 Phase 14-R context compaction regression (2026-08-28)

Added deterministic coverage for the bounded context compiler under pressure:
historical conversation is compacted first while the exact UI-selected
ScientificObject/ScientificObjectVersion and current user request remain
present. The focused ContextManifest suite now passes (`3 passed`); browser-
scale provider performance benchmarking remains an explicit open qualification
item.

### Agent-2.0 Phase 14-R warm navigation measurement (2026-08-28)

The existing authenticated in-app browser measured a warm Research navigation
against the PostgreSQL/Redis/MinIO runtime: DOM-ready at `1442 ms`, with the
research composer visible after `1945 ms` including a `500 ms` settling window.
This is a baseline point only; the required p50/p95 and mobile performance
campaign remains open.

### Agent-2.0 Phase 14-R evidence traversal projection (2026-08-28)

Interpretation evidence remains an immutable bundle projection. The secured
read path now resolves bounded `sourceObjectRefs` from the persisted
ScientificResult snapshot for the owning Job and includes Job-scoped Artifact
and ToolCall descriptors for user inspection. Legacy bundles without a Result
snapshot remain readable without fabricated provenance. No scientific authority,
version semantics, or recomputation path changed.

### Agent-2.0 Phase 14-R report evidence continuity (2026-08-28)

The immutable Scientific Report presentation compiler now preserves the
report's persisted `scientific_interpretation_id` on every bounded block.
The authenticated Dataset report can therefore traverse the same authorized,
read-only Result → Evidence → Artifact → ToolCall → exact source-version path
as the Research presentation. Browser inspection resolved Result snapshot
`2809dcd1-243e-4323-8538-0a5fe81780d9`, exact Dataset version
`be02266a-7d4f-4ebb-9f28-3132855167d0`, the persisted Artifact checksum and
completed `dataset.materials_explorer` ToolCall. Jobs, ToolCalls, Artifacts and
ScientificResult snapshot counts remained `96/131/529/68` before and after
report/evidence navigation, proving this path is presentation-only.
## 2026-08-28 Phase 14-R history continuity

- Research session-history links now use the server-projected `ProjectHistory.analyses` relation to carry an exact `run` and persisted `turn` when available.
- Session-only links remain for sessions without a bound run; no Job-name parsing or scientific identity inference was added.
- Frontend ResearchPages regression: 34 passed; web typecheck: PASS.

## 2026-08-28 Phase 14-R historical context manifest compatibility

- The context-manifest endpoint now projects a bounded `ContextManifest 2.0`
  read model from legacy immutable `research_context_snapshots` when the
  historical `CONTEXT_RESOLVED` event contains only `context_snapshot_id`.
- Exact object/version refs, Dataset semantic selections, prior Result refs,
  constraints and context fingerprints remain sourced from the persisted
  snapshot; the compatibility manifest uses deterministic UUID5 identity and
  opaque provider refs.
- Focused API/context regression: 20 passed. This is a narrow provenance
  continuity repair; Phase 14-R remains PARTIAL because the broader mature
  product and release gates are not yet closed.

追加验证（2026-08-28）：修复 Research 路由在同时携带明确
`sessionId` 与尚未绑定到该会话的历史 `runId` 时错误显示“研究会话不存在”
的问题。现在优先使用持久化的 run 绑定，若绑定缺失则回退到明确的
`sessionId`；仅有 run 且无可验证绑定时仍保持 fail-closed，不会附着到第一条
无关会话。新增回归后 `ResearchPages` 聚焦套件为 `35 passed`，web
typecheck 通过。刷新保留的已认证浏览器标签页后，历史研究对话正常加载，
Context disclosure 可见，旧会话读取错误消失；API 的
`GET /research-sessions/research_fbf038934dc84ffeaa5aed9e7c906095` 返回
`200 OK`。随后完整前端回归为 `94 files / 601 passed`，web typecheck
通过。Phase 14-R 其余成熟产品门仍保持真实 `PARTIAL`。

追加验证（2026-08-28）：Research 会话详情接口现在在每个
`runReferences` 条目中投影已持久化的 `researchTurnId`，并保持项目授权和
legacy null 兼容；客户端无需从 Job 字符串重建 Turn 身份。项目授权/历史
回归 `11 passed`，Ruff 与 web typecheck 通过。

## 2026-08-28 Phase 14-R Research follow-up controls

- Scientific Presentation 结果页现在提供 `继续研究`、`重新研究（新运行）`
  和 `重新解释（不重算科学结果）` 三个明确动作。
- Continue 通过 `explicit_result_ids` 传递既有 Result，保持同一精确来源；
  rerun 不传既有 Result，明确建立新的运行 lineage；reinterpret 继续使用
  interpretation-only 路径。
- 聚焦前端测试 `3 passed`，前端全量 `94 files / 603 passed`，typecheck、
  `git diff --check` 通过。
- 该项只扩展用户控制，不改变 ScientificResult/ScientificObjectVersion
  authority；Phase 14-R 仍为 `PARTIAL`，未创建 P14R-A/P14R-B。

## 2026-08-28 Phase 14-R immutable ResearchTurn branching

- 复用既有 `research_turns.parent_turn_id`，允许从任意终态 ResearchTurn
  创建新的不可变子 Turn；同项目/同会话授权仍由服务端强制校验，非终态父
  Turn 继续拒绝。
- Continue、rerun、reinterpret 后续动作均显式携带父 Turn ID；旧消息、旧
  Result 与旧 ContextSnapshot 不被修改。
- `tests/test_agent2_domain.py`：9 passed；前端 follow-up：3 passed。
- 这项修复完成了可审计的分支 lineage，但完整消息编辑/修订 UI 仍未闭环。

## 2026-08-28 Phase 14-R last-question edit branch

- 完成结果页 `编辑问题` 入口，使用显式 `turn` 与 `edit` 参数进入编辑
  composer；原问题和 exact source refs 从父 Result 读取。
- 提交编辑会创建新的 ResearchTurn，并设置 `reply_to_turn_id` 指向终态父
  Turn；历史消息、ContextSnapshot、ScientificResult 均保持不可变。
- 域回归 `9 passed`，前端呈现回归 `4 passed`，ResearchPages `35 passed`，
  web typecheck `PASS`。完整浏览器编辑提交和分支切换仍待资格验证。

## 2026-08-28 Phase 14-R authorized global search

- ProductShell 全局搜索改为调用有界服务端搜索投影，覆盖项目、数据集、
  科学对象、Research 会话、ScientificResult 与科学报告，并为每项返回
  项目归属、状态和受控打开路径。
- 服务端复用项目 owner/member 授权；跨项目查询 fail-closed，不返回原始
  科学值、Artifact 内容、凭据或基础设施细节。
- `tests/test_project_access.py`：12 passed；ProductShell/ResearchPages：
  38 passed；web typecheck：PASS；同栈浏览器实际显示授权数据搜索结果。
- 组织标签、收藏/集合、保存视图等更高阶组织能力仍保持未完成，不将本次
  导航搜索修复误报为完整组织系统。

## 2026-08-28 Phase 14-R persisted task center

- 新增全局 `/tasks` 任务中心，复用现有授权的
  `listWorkspaceAnalysisJobs` 投影，跨可见项目聚合排队、运行和终态研究。
- 任务入口只导航到精确 Workspace 或 Research run，不在前端创建或复制
  科学状态；取消/重试、持久通知和断线恢复仍保持未完成。
- 增加显式“重新加载”操作，失败或离开后可重新读取持久化 Job 状态；
  不创建新的科学状态。
- Job 投影返回持久化 `researchTurnId`；有明确 Turn 关系的活动任务显示
  “停止研究”并调用既有取消 API，legacy 无 Turn 关系时保持只读，不通过
  Job 名称猜测身份。
- `TaskCenterPage.test.tsx` 及 ProductShell 回归通过，完整前端当前为
  `95 files / 606 tests passed`，web typecheck 通过。
- 已认证浏览器 `http://127.0.0.1:3000/tasks` 实际显示 `2` 个进行中任务、
  `4` 个已结束任务和 `4` 个授权项目；同栈服务 smoke 集合为
  PostgreSQL/Redis/MinIO `5 passed, 0 skipped`。
- 受影响的 Workspace service-backed 集成回归为 `3 passed, 0 skipped`，
  确认新增显式 Turn 投影未破坏同栈工作流。

## Agent-2.0 Phase 14-R explicit ResearchTurn branch navigation (2026-08-28)

- Research history now exposes persisted `parent_turn_id` and the client lists
  authorized turns for the current session through the existing API.
- The workbench shows a bounded branch switcher when sibling turns exist and
  links with the exact persisted Turn ID; it does not parse Job names.
- Legacy/unresolvable turns remain read-only for branching. Pure branch lineage
  regression, `ResearchPages` (36 tests), `agent2_api`/domain (26 tests), and
  web typecheck pass. Browser edit/branch qualification remains open.

## Agent-2.0 Phase 14-R persisted Result context control (2026-08-28)

- Completed Agent2 presentations now allow authorized users to pin/unpin the
  exact `ScientificResult` in the current Research session context.
- The control reuses the existing session-memory API and never mutates the
  scientific Result, source version, or execution lineage.
- `Agent2ScientificPresentation` focused tests: 5 passed; web typecheck PASS.
  Full browser context-control acceptance and budget stress coverage remain
  open.

## Agent-2.0 Phase 14-R task-center attention and refresh (2026-08-28)

- Task Center now refreshes on visibility return and every 30 seconds, with a
  persisted-state “需要关注” group for failed/partial/canceled jobs.
- The sync timestamp is only shown after an authorized server fetch; no fake
  progress or new scientific state is created.
- `TaskCenterPage.test.tsx` passed and web typecheck remains PASS. Retry,
  notifications, and full network-reconnect acceptance remain open.

## Agent-2.0 Phase 14-R explicit terminal retry (2026-08-28)

- Failed or canceled Research execution now exposes an explicit “重试研究”
  action only in terminal states.
- Retry creates a new immutable Turn under the existing session/parent relation
  using the original persisted user question; it does not overwrite the failed
  lineage or fabricate result reuse.
- `ResearchExecutionActivity` focused tests: 6 passed; web typecheck PASS.
  Full browser retry and worker-recovery qualification remain open.

## Agent-2.0 Phase 14-R notification center projection (2026-08-28)

- Added an authenticated `/notifications` route linked from the global shell.
- The page projects only terminal states from authorized persisted project/job
  reads and links each notification to the exact workspace or research route.
- Visibility/30-second refresh is bounded and read-only; no scientific work is
  created. Focused notification/task-center tests and web typecheck pass.
- Push preferences and network reconnect recovery remain open.

## Agent-2.0 Phase 14-R task-center retry handoff (2026-08-28)

- Terminal failed/canceled jobs with an authoritative `researchTurnId` now
  expose `打开并重试` and preserve both `run` and `turn` query identities.
- Workspace-backed jobs without a turn remain open-only; retry never mutates
  the prior execution lineage.
- Task-center, notification-center, and execution activity tests pass.

## Agent-2.0 Phase 14-R current-worktree regression refresh (2026-08-28)

- Same-stack runtime remains PostgreSQL/Redis/MinIO with Redis workers and
  configured DeepSeek.
- Service-backed focused campaign: `8 passed, 0 failed, 0 skipped`.
- Frontend full regression: `96 test files / 610 tests passed`; typecheck,
  production build, Python compileall, and diff check pass.
- Broad mature-product browser, retention, report-quality, operations, and
  real-user gates remain PARTIAL.

## Agent-2.0 Phase 14-R network interruption banner (2026-08-28)

- ProductShell now surfaces a bounded `连接已中断` status on browser offline
  events and clears it on reconnect.
- The status does not mutate persisted research state; users are directed to
  Task Center for server-backed resynchronization.
- ProductShell focused tests: 5 passed; web typecheck PASS. Full reconnect and
  worker-recovery browser qualification remains open.

## Agent-2.0 Phase 14-R task-center online resynchronization (2026-08-28)

- Task Center now refreshes immediately when the browser emits `online`, in
  addition to visibility-return and 30-second refresh boundaries.
- The refresh only re-reads authorized persisted project/job state; it does
  not mark jobs failed, cancel server work, or fabricate progress.
- TaskCenterPage focused regression passes, production build passes, and the
  broader network interruption/API restart/worker recovery browser campaign
  remains open.

## Agent-2.0 Phase 14-R notification-center online resynchronization (2026-08-28)

- Notification Center now refetches its authorized persisted notifications
  immediately after the browser emits `online`, matching Task Center recovery.
- The listener is bounded to the page lifecycle and remains read-only; it does
  not create jobs, alter terminal states, or fabricate notifications.
- Notification and Task Center focused tests pass; full browser reconnect/API
  restart/worker recovery qualification remains open.

## Agent-2.0 Phase 14-R report source/method presentation (2026-08-28)

- Scientific Report now presents the persisted method summary and authorized
  exact object/version sources in a visible `数据与方法` section.
- Historical/current version status is shown from the existing
  `viewer_sources.is_current_version` authority; no scientific values are
  recomputed or duplicated.
- Report route/action focused tests pass and web typecheck remains PASS.
  Multi-family report-quality and full browser acceptance remain open.

## Agent-2.0 Phase 14-R authenticated task/notification browser evidence (2026-08-28)

- In-app authenticated browser verification loaded `/notifications` with four
  persisted terminal notifications and `/tasks` with two active plus four
  ended jobs across four authorized projects.
- Exact project/run links and persisted sync timestamps were visible in both
  surfaces. The broader reconnect/API restart/worker recovery browser campaign
  remains open.

## Agent-2.0 Phase 14-R current-head same-stack regression (2026-08-28)

- The current PostgreSQL/Redis/MinIO service campaign completed
  `8 passed, 0 failed, 0 skipped` in `116.10s`.
- The tested paths included ContextManifest, PostgreSQL planning idempotency,
  and Redis-backed workspace/result behavior; runtime health remained on the
  real same-stack services with Redis workers and configured DeepSeek.

## Agent-2.0 Phase 14-R Research progress reconnect (2026-08-28)

- Active Agent2 Research progress polling now retries its existing persisted
  progress read on browser `online`, with lifecycle cleanup on turn change or
  unmount.
- No new ResearchTurn/Job/ToolCall/Artifact/Result is created and no progress
  is fabricated. ResearchPages regression (`36 passed`) and web typecheck pass;
  full network/API/worker recovery browser qualification remains open.

## Agent-2.0 Phase 14-R bounded Scientific Report export (2026-08-28)

- Scientific Report now exposes a deterministic Markdown export from the
  authorized immutable report view.
- The export retains report/snapshot/turn/result identities, exact source
  versions, findings, limitations, evidence refs and reproducibility text,
  while excluding provider/internal infrastructure details.
- Focused Report route regression and web typecheck pass. Full export-package
  and retention policy acceptance remain open.

## Agent-2.0 Phase 14-R authenticated Scientific Report browser evidence (2026-08-28)

- In-app authenticated browser opened the project Reports list and modern
  Dataset report. Exact Dataset version, method, findings, limitations,
  evidence disclosure, and `导出 Markdown` were visible with no captured
  console errors/warnings.
- The browser download event did not expose a completed Blob transfer; only
  route/action reachability is recorded. End-to-end export transport and
  retention policy acceptance remain open.

## Agent-2.0 Phase 14-R persisted Figure navigation (2026-08-28)

- Report Figure blocks now resolve bounded `figure_sources` derived from the
  immutable ScientificResult bundle, including persisted Artifact IDs and the
  source Job.
- Report and shared presentation readers use the existing secured Artifact
  content route when available, with exact-source Viewer fallback otherwise;
  rendering remains read-only and cannot enqueue scientific work.
- Backend report tests (`16`, with four historical live-LLM skips), frontend
  presentation/report tests (`15`), the PostgreSQL/Redis/MinIO report service
  campaign (`9 passed, 0 skipped`) typecheck and production build pass.
  Capability-wide same-stack Figure acceptance remains open.
- Markdown export now retains the bounded persisted Artifact IDs for primary
  Figures, keeping the export reproducible without exposing provider or
  infrastructure secrets; the route regression remains green.

## Agent-2.0 Phase 14-R results record (2026-08-28)

- Added `AGENT2_PHASE14R_RESULTS.md` as the current truthful evidence index.
- It records the sealed Phase 14 baseline, same-stack health, Figure/Artifact
  bridge, focused/full regression counts and explicit remaining mature-product
  gaps. Phase 14-R remains `PARTIAL`; no P14R release candidate was created.

## Agent-2.0 Phase 14-R Structure Viewer proof (2026-08-28)

- Authenticated same-stack browser rendered exact Structure object
  `dc3c3eee-f254-4edf-a0fa-c955402b3069` / version
  `8859cb49-0766-48cd-8a56-e44f5332e0c5`, including formula, lattice, canvas,
  camera and bounded supercell controls.
- Isometric/2×2×2/reset navigation left PostgreSQL counts unchanged:
  `jobs=117`, `tool_calls=158`, `artifacts=637`, `results=88`.
- This is a Structure-specific Viewer no-recompute proof; capability-wide
  Viewer acceptance remains open.

## Agent-2.0 Phase 14-R warm route performance baseline (2026-08-28)

- Same-stack authenticated browser timing samples: Data `175 ms`, Research
  `215 ms`, modern Report `259 ms`, Tasks `202 ms`, Notifications `189 ms`.
- These measurements establish a current baseline only; cold-start, p50/p95,
  payload/resource and mobile interaction SLO evidence remain open.

## Agent-2.0 Phase 14-R Structure report browser proof (2026-08-28)

- Authenticated report route
  `/projects/project_0002_1a0af866391f412d/reports/job_agent2_17b67e68b7db475bbb4c3b336cb2ba15`
  rendered persisted CrystalNN/VoronoiNN tables, site inspector, warnings and
  reproducibility details.
- Read-only reopen left PostgreSQL scientific counts unchanged:
  `analysis_plans=133`, `jobs=117`, `tool_calls=158`, `artifacts=637`,
  `scientific_result_snapshots=88`.

## Agent-2.0 Phase 14-R current-worktree regression refresh (2026-08-28)

- Fresh frontend regression: `96` files / `615` tests passed.
- Fresh backend regression: `1827` passed / `83` historical or optional skips.
- Production build, typecheck, compileall, `uv lock --check`, touched Ruff,
  and `git diff --check` passed.
- Runtime health remained PostgreSQL, Redis, MinIO, Redis workers, and
  configured DeepSeek. Mature-product closure remains `PARTIAL`; no P14R
  release candidate was created.

## Agent-2.0 Phase 14-R current same-stack service campaign (2026-08-28)

- Fresh Context Manifest, PostgreSQL planning, and Phase 7 reuse/execution
  campaign: `8 passed`, `0 failed`, `0 errors`, `0 skipped`.
- Runtime services: PostgreSQL, Redis, MinIO, Redis-backed workers, DeepSeek.
- PostgreSQL activity after the campaign: `active=1`, `idle=4`,
  `idle-in-transaction=0` observed. Mature-product closure remains
  `PARTIAL`.

## Agent-2.0 Phase 14-R authenticated browser continuity (2026-08-28)

- Kept the authenticated in-app browser tab open at `/console`.
- Live search still resolves ScientificResult snapshot
  `2809dcd1-243e-4323-8538-0a5fe81780d9` to persisted ResearchTurn
  `8382c443-f9ca-4c90-9aa3-444fea683807` through `/research?turn=...`.
- Services and browser remain running for the next qualification pass.

## Agent-2.0 Phase 14-R lifecycle audit (2026-08-28)

- Verified current lifecycle authority is ACTIVE/ARCHIVED plus protected
  empty-entity deletion with server-derived dependency impact.
- No persisted TRASHED/PURGED or retention/export contract exists yet.
- Kept this as an explicit mature-product gap instead of adding an unsafe
  partial deletion model.

## Agent-2.0 Phase 14-R direct Project History ResearchTurn relation (2026-08-28)

- Restarted the browser-facing API with the repository-supported same-stack
  environment; runtime health is PostgreSQL + Redis + MinIO with Redis-backed
  workers and `mdi-artifacts`.
- Project History now merges direct persisted `research_turns` bindings for
  modern Agent2 jobs that lack legacy session-run rows. Authenticated live
  evidence resolves `job_agent2_8382...` to Turn
  `8382c443-f9ca-4c90-9aa3-444fea683807` and `job_agent2_17b67...` to Turn
  `17b67e68-b7db-475b-bb4c-3b336cb2ba15`, both as `RESEARCH_TURN`.
- Focused regression: `tests/test_project_history_research_context.py` 4
  passed; touched Ruff and `git diff --check` pass. This continuity repair
  does not change the truthful Phase 14-R `PARTIAL` status.

## Agent-2.0 Phase 14-R session-list exact ResearchTurn continuity (2026-08-28)

- Fixed the follow-on seam where `/research-sessions` exposed only legacy
  `research_session_runs`, causing an exact modern task link to render a false
  “no recoverable conversation” warning.
- The session projection now merges authorized direct
  `research_turns.research_session_id`/`job_id` relations into
  `runIds`/`runReferences`; no Job-name inference or second identity source was
  introduced.
- Authenticated Chromium after API reload opened the exact Turn
  `8382c443-f9ca-4c90-9aa3-444fea683807`; warning absent, context disclosure
  and `mat-2` result present, no console/page/critical-request errors, and no
  overflow. Focused Project Access/history regression: 19 passed. Overall
Phase 14-R remains `PARTIAL`.

## Agent-2.0 Phase 14-R terminal projection direct Turn relation (2026-08-28)

- Terminal interpretation reconciliation now prefers direct persisted
  `research_turns.research_session_id`/`job_id` for modern Agent2 work, with
  the legacy `research_session_runs` fallback retained for rolling/old data.
- This keeps assistant projections attached to the exact Research Session even
  when no compatibility row exists; it does not create a second identity
  source.
- Focused Project Access/history/reconciliation regression: 20 passed; Ruff
  and diff checks pass. Phase 14-R remains `PARTIAL`.

## 2026-08-28 — Result reuse browser proof after worker recovery

The authenticated reinterpret action completed as `INTERPRET_RESULT` for Turn
`cc704d3f-dcfc-4a49-a971-2cda6282039c`, with `VALID` interpretation
`ce8c820d-2f42-4a82-9593-714971b5ad09`, reusing immutable Result snapshot
`2809dcd1-243e-4323-8538-0a5fe81780d9`. ContextManifest
`da2d4f02-1dac-4d53-aa9f-8987a8ab6147` preserved the exact Dataset version
and `mat-2`; analysis-job count stayed `4 → 4`. The Turn was initially
delayed because the existing queue workers had exited; starting the repository
launcher restored processing. This is a runtime availability finding, not an
authority change. Phase 14-R remains PARTIAL.

## 2026-08-28 — Edit branch context isolation

The context assembler now treats a child turn with `parent_turn_id` and no
explicit Result IDs as a fresh branch: recency-derived historical Results are
not injected into its orchestration context. Explicit reinterpret/continue
flows still bind the requested immutable Result snapshot. After reloading the
same-stack API and workers, authenticated edit child Turn
`1176df48-b0a4-4611-bf42-970ef2c6d181` preserved parent
`8382c443-f9ca-4c90-9aa3-444fea683807`, exact Dataset object/version, and
`mat-2`; its manifest contained zero Result candidates and the bounded
request completed as `ANSWER` without a Job or Result. This closes a
demonstrated orchestration seam while Phase 14-R remains PARTIAL.

## 2026-08-28 — Dataset semantic constraint binding

`sample`/`property` 是 Dataset 需求层的语义选择，不是
`dataset.materials_explorer` 的可执行 Tool 参数。`CapabilityBinder` 现仅
隔离这两个明确 key，任意其它未知参数仍由严格 schema 拒绝。规划器回归
为 `21 passed, 1 skipped`，touched Ruff PASS。

同栈 API 与五个 worker 重载后，认证浏览器新 Turn
`3b85fa42-dcc8-42b3-ac68-f5f54b610df4` 完成
`PLAN → Job → ToolCall → Artifact → ScientificResult →
VALID Interpretation → COMPLETED`。Result
`e2587ca6-9b1f-5532-9e79-0ae6a89d6777` 含 `mat-2` 的
`band_gap=2.5` 权威 fact，精确 Dataset object/version 保留。Phase 14-R
总体仍为 PARTIAL，服务和 Chrome 保持运行。

## 2026-08-28 — Presentation pin 状态竞态修复与回归

前端全量回归发现 `Agent2ScientificPresentation` 的旧 session-memory
读取可能在 pin/unpin 请求完成后覆盖新状态。修复沿用现有
`pinMutationSeq`，在 mutation 成功或失败结算时再次递增，使旧读失效，
不改变科学结果或上下文权威。

验证：

- 组件回归：6 passed；
- 前端全量：96 files / 615 passed；
- 后端默认 SQLite 隔离全量：1833 passed / 83 skipped；
- 显式 PostgreSQL/Redis/MinIO service-backed Phase 3/4/5：4 passed；
- touched Ruff、compileall、git diff --check：PASS。

Phase 14-R 仍为 `PARTIAL`，该修复只关闭一个真实用户控制竞态。

## 2026-08-28 — 编辑分支真实浏览器验收

认证 Chromium 通过编辑入口从父 Turn
`8382c443-f9ca-4c90-9aa3-444fea683807` 创建不可变子 Turn
`dc76de32-4675-4b6a-91fd-ef102602c905`。父 Turn 保持 `COMPLETED` 且未被
修改；子 ContextSnapshot
`e58057b5-b88b-495e-a855-29dd46a4c953` 保留精确 Dataset
object/version 与 `DATASET_SAMPLE=mat-2`，查询型请求最终
`ANSWERED`，无 Job/ScientificResult（符合 `QUERY_DATA` 语义）。
浏览器无 page error、无 5xx；轮询期间的
`SCIENTIFIC_RESULT_NOT_READY` 409 是无 Result 的 fail-closed 预期。
## 2026-08-29 — Phase 14-R grounded Report narrative sections

- Extended the immutable scientific Report communication contract with
  optional bounded `discussion`, `conclusion`, and `next_steps` sections.
- Each section carries Result `fact_refs`/`evidence_refs`; numeric and unit
  claims are validated by `ReportGroundingValidator`, preserving fail-closed
  scientific authority.
- Updated the Report route, deterministic presentation projection and
  Markdown export to expose the mature report hierarchy without creating a
  Job, ToolCall, Artifact or ScientificResult.
- Focused evidence: backend Report `18 passed, 4 compatibility skips`;
  frontend Report/presentation `16 passed`; typecheck and touched Ruff pass.
- Phase 14-R remains partial pending the broader capability, lifecycle,
  recovery, operations, real-user and exact-SHA release gates.
## 2026-08-29 — Phase 14-R archive/browser and same-stack service recheck

- Preserved the authenticated in-app browser tab and verified the reversible
  Dataset lifecycle action for `dataset_0003_1e42d834bfa64961`: active →
  archived filter → restore → active, with typed rows and exact object/version
  identity unchanged.
- Re-ran the Phase 10L–10N service-backed collection after loading the
  repository PostgreSQL/Redis/MinIO environment and explicit integration gate:
  21 passed, 0 failed, 0 errors, 0 skipped.
- The first two attempts were classified as command-environment defects
  (missing `MDI_RUN_INTEGRATION` or missing PostgreSQL alias), not service
  availability failures. Phase 14-R remains partial because protected Trash/
  retention/purge, capability-wide live browser coverage, recovery and
  release CI are still unqualified.

## 2026-08-29 — Phase 14-R task-center stale-state clarity

- Added a read-only 15-minute stale-status notice for active/queued tasks in
  the global Task Center. Persisted task status, cancellation authority and
  exact navigation identities are unchanged; the notice only directs users
  to inspect the latest server state instead of implying a failure.
- Focused Task Center regression passes. The mature task/recovery gate remains
  partial until live retry/reconnect and worker-recovery browser campaigns are
  qualified.

## 2026-08-29 — Phase 14-R final same-stack operations recheck

- Restored the missing `mdi-agent-turns` worker through the existing launcher
  while preserving PostgreSQL, Redis, MinIO, API, frontend, and browser state.
- Current redacted snapshot: PostgreSQL active=1/idle=7,
  idle-in-transaction=0, pool checked-out=0, Redis queue depth=0,
  canonical workers=5 idle, MinIO=OK, recent RQ failures=0.
- Snapshot remains `attention` because 9 historical automatic-stage Turns and
  1 stale qualification Job remain persisted; no records were deleted or
  rewritten.

## 2026-08-29 — Phase 14-R recoverable Project/Dataset Trash

- Added recoverable `TRASHED` lifecycle projection for Projects through
  `project_configs.config_json` and Datasets through
  `datasets.metadata_json`, retaining the pre-Trash lifecycle for deterministic
  restore.
- Kept Dataset database status inside the released constraint (`archived`)
  while API/history/search return the explicit outward `trashed` state.
- Added Project/Data Trash filters, dependency preview, per-row and bulk
  Trash/Restore, excluded Trash from normal new-work actions, and extended
  authorized global search to `status=trashed`.
- Focused evidence: backend lifecycle/access/history `20 passed`, frontend
  Project/Data lifecycle `28 passed`, typecheck/build/Ruff/diff check PASS.
- Restored the local same-stack runtime after process loss. MinIO required a
  relative data argument because the previous absolute path contained spaces;
  `/health/runtime` now reports PostgreSQL, Redis, MinIO, workers and DeepSeek
  `ok`.
- Phase 14-R remains partial pending the wider lifecycle/retention/export,
  Viewer/Report quality, same-stack browser and exact-SHA release gates.

## 2026-08-29 — Phase 14-R Research Session lifecycle

- Added project-authorized `PATCH /research-sessions/{session_id}` for
  recoverable `TRASHED`/`ACTIVE` session management using the existing
  `sessions.status` authority.
- Archived/trashed sessions remain readable for historical provenance but
  reject new Messages and ResearchTurns; Trash is rejected while a
  non-terminal Turn is running.
- Added Research Records popover Trash/Restore controls with explicit
  historical-retention confirmation. No Turn, Result, Artifact, or scientific
  object/version authority is mutated.
- Focused backend/frontend lifecycle tests pass; Phase 14-R remains partial.
## 2026-08-29 Phase 14-R recoverable Research and Report lifecycle

- Research Sessions now use the existing `sessions.status` authority for
  recoverable `ACTIVE`/`ARCHIVED`/`TRASHED` management. Only active sessions
  accept new messages or turns; non-terminal work blocks Trash; historical
  Results and exact source provenance remain readable.
- Immutable Scientific Reports now use a bounded project-config lifecycle
  overlay. The report list exposes current/archived/Trash filters and
  reversible Trash/Restore actions without mutating the Report snapshot or
  creating scientific execution state.
- Focused evidence: Report UI `2 passed`; Report lifecycle/backend
  `20 passed, 4 historical compatibility skips`; broader affected backend
  `45 passed, 4 skips`; same-stack Phase 8 report campaign
  `4 passed, 0 skipped`; Research Session backend/frontend
  `17 passed` / `37 passed`; typecheck, compileall, Ruff and diff check pass.
- The preserved authenticated in-app browser is logged in against the real
  PostgreSQL `55434` / Redis / MinIO stack. The report index renders
  `agent2_report_819f458171ba2d3219717895bf12eaf9` with the recoverable
  lifecycle action. Phase 14-R remains partial because capability-wide viewer,
  retention/purge/export, recovery/performance, full real-user and exact-SHA
  release gates are still open.
## 2026-08-29 Phase 14-R report lifecycle completion

Scientific Reports now expose distinct Archive, Trash, and Restore actions
through the existing project-authorized lifecycle endpoint. The shared
frontend request helper sends JSON content types for lifecycle PATCH calls.
Authenticated browser evidence covered Trash, historical report reopening while
trashed, Restore, and active rediscovery; immutable scientific counts remained
unchanged (`Jobs 194`, `ToolCalls 250`, `Artifacts 995`,
`ScientificResultSnapshots 127`). Phase 14-R remains PARTIAL because the
capability-wide real-user, retention/export, and release gates are not closed.
# Phase 14-R operations diagnostic entrypoint (2026-08-29)

`scripts/phase14r_operations_snapshot.py` now bootstraps the repository's
`apps/api` package from its own location. The redacted PostgreSQL/Redis/MinIO
operations snapshot can therefore be invoked directly from a clean shell;
qualification environment variables still remain explicit and are never
embedded in the script.

## 2026-08-29 — ScientificObject recoverable Trash lifecycle

Extended the existing ScientificObject lifecycle authority with a bounded
`TRASHED` state and `pre_trash_lifecycle_status` marker via Alembic
`0026_scientific_object_trash_lifecycle`. The service/API preserve the prior
ACTIVE or ARCHIVED state on restore, while the Data Navigator now queries and
renders a Trash filter and reversible object action. Domain/API/frontend tests
cover both active and archived pre-Trash cases; no scientific versions or
Results are created or mutated. Retention, purge, export and broad lifecycle
qualification remain open, so Phase 14-R stays PARTIAL.

## 2026-08-29 — ScientificObject dependency preview

ScientificObject recoverable Trash now requests the project-authorized
`GET /api/scientific-objects/{object_id}/dependency-impact` projection before
the existing lifecycle PATCH. The server derives bounded exact-version
dependencies from immutable ScientificResult bundles, ResearchTurns, and
Report snapshots; the UI presents protected historical-provenance flags and
requires explicit confirmation. Preview is read-only and does not mutate any
ScientificObjectVersion, ScientificResult, Artifact, or Report.
## Phase 14-R qualification runtime isolation (2026-08-29)

The browser qualification frontend now runs with an isolated Next build
directory (`MDI_NEXT_DIST_DIR=.next-dev-phase14r`) so production `next build`
cannot remove development route manifests. The process still targets the
same-stack API (`127.0.0.1:8000`) and does not move execution authority into
the browser. A fresh authenticated Chrome product tab returned the normal
shell after the fix. This is an operational qualification safeguard only;
Phase 14-R remains partial until the documented mature-product gates pass.

## Exact-source Viewer fail-closed behavior (2026-08-29)

Scientific Viewer projection now treats a not-found exact source object as
`SOURCE_MISSING` metadata plus an explicit limitation, preserving the
requested ScientificObject/ScientificObjectVersion. Integrity mismatches and
other storage failures still fail closed. This avoids a generic browser 500
without substituting a newer source or recomputing science.

## Bounded Report reproducibility export (2026-08-29)

Scientific Report pages expose a deterministic, non-executable JSON
reproducibility manifest derived from the authorized immutable report view.
It carries exact Result/Interpretation/source-version/Figure Artifact/Evidence
identities and limitations, but no provider prompts, credentials, raw Tool
logs or unbounded source data. This is a presentation export only and does not
change the scientific authority model.

Authenticated Chrome acceptance downloaded the manifest from Report
`agent2_report_819f458171ba2d3219717895bf12eaf9` and verified exact
Report/Turn/Result/Interpretation/Dataset-version provenance. Scientific state
counts remained `196/253/1007/129` for
Job/ToolCall/Artifact/ScientificResultSnapshot, proving the export does not
recompute science. Cross-entity retention/export governance remains open.

## Dataset handoff / same-stack worker qualification (2026-08-29)

An explicit Data Platform → Research deep link now preserves `datasetId`,
prevents stale-session auto-selection, and binds newly-created Research
sessions/messages to the selected Dataset. Focused tests pass (`38 + 4`).
The authenticated same-stack probe started the repository's five Redis
workers and completed real uploaded Dataset Job
`job_9a63cc82cf574e25a88529c7` with one ToolCall and three Artifacts.
The probe confirms a remaining legacy Planner integration seam: the direct
Planner route does not automatically materialize a ResearchTurn and
ScientificResult interpretation, so Phase 14-R remains PARTIAL.

## Fresh Dataset projector and report grounding qualification (2026-08-29)

The current same-stack runtime now proves a fresh Dataset-to-Research
execution with exact Dataset object/version/sample identity. Dataset promotion
is idempotent: repeated navigation reuses the existing admitted
`materials.table` object/version instead of creating duplicate scientific
authority. The fresh run persisted a new Job, ToolCall, Artifact and
ScientificResult containing authoritative sample and numeric facts, followed
by a `VALID` grounded interpretation and terminal completed Turn.

Report grounding was repaired at the narrow validator layer: numeric fragments
embedded in opaque UUID/version/resource identifiers are provenance labels, not
scientific claims. Ordinary numeric claims and scientific notation remain
fail-closed, with a negative unsupported-claim regression retained. The fresh
Report reached READY and opened/exported without any scientific-state delta.
Phase 14-R remains partial because broad mature-product acceptance and release
gates are not yet closed.

## QUERY_DATA terminal-state runtime repair (2026-08-29)

The fresh browser query-only path was initially stuck because the live
`phase14r-turns-55434` worker had not loaded the current router implementation.
After cleaning only that stale RQ registry entry and relaunching the worker from
the current worktree, Turn
`ddad0068-144e-4377-abe3-44a0e2601592` completed as `ANSWERED` with
`QUERY_DATA`/`dispatch_status=COMPLETED` and no scientific execution records.
The frontend now models `ANSWERED` explicitly and resets stale local planning
state when a Turn route changes. This closes the demonstrated query-only
runtime/UI seam while Phase 14-R remains partial for the broader mature-product
gates.
### 2026-08-29 — grouped Report/search/recovery product qualification

在保持 API、workers、PostgreSQL、Redis、MinIO 与 Chrome 标签页运行的前提下，
完成一组关联验证：Report
`agent2_report_c91972312383616a6503acd6be76e233` ACTIVE→ARCHIVED→ACTIVE，
归档筛选中仍可打开，Dataset exact object/version 与 Result snapshot 不变；
回收站依赖预览显示 6 项受保护依赖并在确认前取消；全局搜索 `mat-2` 返回
授权项目内的 Report/Research 入口；`/tasks`、`/notifications` 暴露持久化
状态重载/恢复入口。报告/生命周期定向回归为 39 passed、4 historical skips，
同栈服务子集为 11 passed、0 skipped。Phase 14-R 仍为 PARTIAL，未创建
P14R-A/P14R-B。

### 2026-08-29 — bounded bulk Report lifecycle controls

在保留现有 Report 依赖预览语义的前提下，报告列表新增 ACTIVE/ARCHIVED
范围内的受限多选归档/恢复；Trash 仍只允许逐份操作，以确保每份报告继续经过
服务端依赖影响预览。真实 Chrome 标签页中对
`agent2_report_c91972312383616a6503acd6be76e233` 完成
ACTIVE→ARCHIVED→ACTIVE，归档筛选可见，Dataset exact object/version 与
ScientificResult snapshot 不变；归档报告正文显示明确状态说明，并提供绑定
ResearchTurn `9c3a8278-69cf-4f9e-973a-e0b5d0e46779` 的来源研究入口。
前端定向回归 37 passed，同栈服务子集
11 passed、0 failed、0 errors、0 skipped。Phase 14-R 总体仍为 PARTIAL。

### 2026-08-29 — Report lifecycle toolbar quality

报告列表批量工具条按 ACTIVE/ARCHIVED 实际状态分组，因此在“全部”筛选下
混合选择仍有清晰的归档/恢复动作；批量请求使用 `Promise.allSettled`，
成功项即时更新，失败项保持选中并显示可重试提示。筛选切换会清理旧选择。
报告正文显示归档/回收站状态说明，并提供精确 ResearchTurn 来源研究入口。
同时按现有设计系统补齐桌面/移动端工具条与行操作布局。相关前端回归
40 passed，typecheck 通过；总体仍为 PARTIAL。

### 2026-08-29 — task/notification control surface quality

任务中心与通知中心采用统一的语义状态徽标（排队、运行、成功、警告、
失败、已取消），将 Job ID 降为次级元数据，并为每行操作区增加状态相关
的 aria-label。960px 以下操作区扩展到整行，保证“打开 / 重试 / 停止研究”
在移动端可触达；未改变真实 ResearchTurn、Job 或取消 API 权威。
相关前端回归 58 passed，typecheck 通过，diff check 无空白错误。
总体 Phase 14-R 仍为 PARTIAL。

### 2026-08-29 — runtime and legacy-task grouping repair

长时间前端回归释放本地进程后，重新启动 PostgreSQL `55434`、Memurai
Redis `6379/13`、MinIO `9000`、API、前端和 Redis workers。MinIO 的
`XMinioServerNotInitialized` 根因是 Windows 启动参数拆分了带空格的工作区
路径；使用显式引号的单 volume 后完成初始化，`/health/runtime` 恢复报告
真实 PostgreSQL/Redis/MinIO。

任务中心将 `LEGACY_READ_ONLY` 记录从“进行中”移到历史区域，即使旧 Job
状态仍为 `created` 也不再虚增活跃任务。真实页面显示 0 个进行中、17 个已结束，
旧记录与 stale 提示仍可查看。相关测试与全量前端回归通过，总体 Phase 14-R
仍为 PARTIAL。

### 2026-08-29 — Research result control hierarchy

完成结果页新增统一的“继续这项研究”控制区，将编辑问题、继续研究、
重新研究（新运行）、重新解释（不重算）和固定/取消固定结果分组呈现；
异步操作期间显示“科学结果本身不会被覆盖”的实时状态。桌面五列、平板
两列、手机单列，所有操作保持 44px 触控可达并沿用工作台安静边框视觉。
相关定向回归 52 passed，typecheck 通过；总体 Phase 14-R 仍为 PARTIAL。

### 2026-08-29 — Global search interaction quality

在现有全局授权搜索上补齐 `Ctrl/⌘ K` 打开/聚焦、清除后焦点恢复、结果数量
live status 和类型/生命周期语义徽标。搜索弹层仍是单实例并保留键盘焦点陷阱；
移动端沿用 44px 触控尺寸和安静边框层级，没有新增科学事实或跨项目搜索权限。
定向 ProductShell 回归 7 passed；总体 Phase 14-R 仍为 PARTIAL。

### 2026-08-30 — XRD source recovery and mobile context priority

The XRD Data Platform surface was requalified against the running PostgreSQL,
Redis and MinIO stack after restoring repository-owned normalized objects into the
existing artifact bucket. The page now visibly renders the validated XRD series
and linked Structure Viewer; this preserves the existing source authority rather
than introducing a fallback scientific payload.

For a missing normalized source, the API/UI pair now communicates a typed,
retryable recovery state and offers `重试加载` plus `查看来源与属性`. On narrow
screens the data navigator starts collapsed behind `显示数据`, keeping the
scientific viewer and its source context primary while preserving an explicit
expand path. The mobile evidence measured no horizontal overflow.

### 2026-08-30 — report index language hierarchy

The Scientific Reports index now uses consistent Chinese kicker labels
(`项目报告`, `已验证结果`, `历史运行`) alongside the existing Chinese headings.
This keeps the Research/Report navigation hierarchy readable for the target
workbench audience without changing report lifecycle semantics or provenance.
The report index focused regression remains green.

### 2026-08-30 — one authoritative completed-result surface

Completed Agent2 turns now render the exact ResearchTurn presentation as the
single primary workbench result. The legacy run-level workbench projection is
suppressed for the same completed/partial turn, removing a duplicate
`科学呈现` section and the misleading intermediary empty result state. Legacy
and in-progress runs retain their existing workbench rendering. The change is
presentation-only and does not alter Result, Artifact, Report or version
authority.

### 2026-08-30 — task and notification information hierarchy

Task Center and Notification Center no longer put raw Job identifiers in the
primary heading. Users first see the persisted status and a bounded product
label (`工作台研究`, `可恢复研究`, `历史研究`, or `研究状态更新`).
The exact Job ID remains available under a collapsed `技术身份` disclosure for
audit and support. Navigation, cancellation, retry and persisted-state
authorities are unchanged.

### 2026-08-30 — task filters and Research action hierarchy

Task Center now uses one compact tablist (`全部`、`进行中`、`需要关注`、`已结束`)
so a task is not repeated across multiple visual groups. The row-level primary
action is `打开`; technical Job identity remains progressive disclosure.
Completed Research keeps `继续研究` as the primary action and separates
explicit rerun, no-recompute reinterpretation, editing and context pinning as
secondary controls. Desktop and 390x844 browser checks show no overflow and
all controls remain reachable.

### 2026-08-30 — Report Evidence mobile overflow and fluency baseline

Evidence identifiers in the Report reader now shrink and wrap within the
scientific document grid instead of pushing the action row beyond a 390px
viewport. The current Chromium cold/warm matrix against PostgreSQL, Redis,
MinIO and real workers records zero overflow across Data, Research, Viewer,
Report, Tasks and Notifications; the bounded p50/p95 values are recorded in
`docs/agent2/phase14r/PERFORMANCE_PRODUCT_FLUENCY_BASELINE.md`.

### 2026-08-30 — context transparency and scientific search hierarchy

Research context now leads with what the researcher needs to trust the answer:
why an item was included, whether it is scientific data/result or a user
constraint, and the exact source version. Manifest identity, policy and
fingerprint remain under `审计详情`, preserving auditability without making
internal contracts the page focal point. The disclosure reflows to one column
at 390px and long versions/fingerprints wrap without overflow.

Global search now uses human research questions instead of internal Session IDs,
localized scientific Result/status labels, and one primary `打开` action. Project
shortcuts remain secondary. This preserves the global bar as navigation and
identity only while keeping search behavior inside one bounded modal.

### 2026-08-30 — Research session lifecycle placement

Research session organization is now grouped where users expect to manage a
conversation: the Research Timeline header opens one bounded `研究记录`
popover with `当前 / 已归档 / 回收站` filters, pinned records at the top, and
row-level overflow actions. The selected session header shows its title and
archive/trash state; Restore sits beside the Records entry point so the user
can recover a historical session without hunting through another page.

Archived and trashed sessions keep their historical conversation, Result,
Viewer, Evidence and Report routes, but the composer becomes an explicit
read-only panel and retry is withheld until restoration. This makes the
scientific workbench hierarchy truthful: lifecycle controls belong to the
session header, while scientific content remains in the workbench. The change
does not mutate Messages, ResearchTurns, ScientificResults or exact source
versions.

### 2026-08-30 — App Router production fluency and layout validation

The project shell now treats route changes as spatially continuous workbench
transitions. Fast transitions do not flash a banner: the bounded progress
affordance waits 180 ms and then uses a non-displacing 3 px mineral-green line.
Project-nav pointer/focus intent prefetches both Next route data and the
authoritative bounded history/session projections. Three-second promise caches
deduplicate only the navigation handoff and invalidate after related mutations.

The browser runtime uses same-origin `/api` routing. Optimized-build
authenticated navigation measured `32–372 ms` usable time across
Data/Research/Reports/Overview, with zero document requests and one preserved
ProductShell. At `390x844`, Data, Research and Reports had zero global overflow
and Reports had zero duplicate DOM IDs. The design review retains the Phase 9C
workbench hierarchy, IBM Plex/Noto type, single mineral accent, quiet borders,
one primary action, responsive progressive disclosure and touch-safe mobile
controls.

### 2026-08-30 — Dataset batch lifecycle safety

Dataset multi-select now opens a bounded dependency-impact preview before
`移入回收站`. The confirmation action is enabled only after every selected
Dataset has an authorized server response; failed mutations leave the dialog
open instead of implying success. This keeps destructive intent explicit while
preserving the Data Navigator's existing actions/menu hierarchy.

The failure path is explicit: if the batch endpoint rejects, the preview stays
open and exposes the error so the user can retry or cancel without losing the
dependency context.
### 2026-08-30 — Batch lifecycle safety and action hierarchy

Bulk ScientificObject `移入回收站` now follows the same dependency-protection
contract as the single-object action. The Data Navigator requests an
authorized impact projection for every selected object, shows a compact
aggregate confirmation, and keeps the confirm control disabled until all
previews resolve. Real authenticated browser verification showed two Structure
objects and five protected dependencies with no mutation; Data page regression
is `29/29`, and typecheck passes.

### 2026-08-30 — Search and task-center continuity proof

The authenticated Data route now has a verified path into global search and
the global task center without closing the App Router shell. Search returns a
bounded set of authorized scientific-work routes; Task Center presents
persisted project-scoped status, explicit resumable ResearchTurn links and
truthful stale-state notices. This preserves the workbench hierarchy while
keeping recovery controls in the dedicated task surface.

### 2026-08-30 — Search fluency and stale-response protection

Global search keeps the existing 180 ms debounce but now invalidates older
request sequences when the query, filters, or dialog state changes. A slower
response can no longer replace a newer result set, which preserves user
orientation and exact route identity during rapid typing.

### 2026-08-30 — Full frontend regression on workspace temp volume

The fresh current-worktree frontend suite completed with `98` files and
`670` tests passing after redirecting Vitest temporary files to the E:
workspace volume. This avoids the host C: temporary-volume `ENOSPC` seen in
the prior attempt without deleting user data. Service listeners remained
active throughout.

### 2026-08-30 — Re-interpretation control now completes without recomputation

The authenticated Research workbench revealed that a valid result could fail
the no-recompute re-interpretation branch when the provider's `answer_lead`
contained an extra unsupported number. The repair stays at the interpretation
boundary: only the exact lead-only grounding error is replaced with the first
already-grounded Finding statement, and the original validator still guards
all Finding claims, references and units. A fresh child Turn completed with
`grounding_status=VALID`; PostgreSQL showed zero new Plan/Job/ToolCall/Artifact/
ScientificResult rows. Focused interpretation tests are `15 passed, 1 skipped`.

### 2026-08-30 — Result reuse service qualification executed

The Phase 7 fresh-process service campaign was rerun with the integration gate
enabled instead of accepting its default skips. PostgreSQL/Redis/MinIO
execution passed `4/4` with `selected_skip=0`, covering RDF/XRD reuse,
continuation and stale exact-version follow-up. The campaign reported
`no_recompute=true` for the reuse branch and preserved the exact historical
source version while a newer current version existed.

### 2026-08-30 — Fresh Research continuity and route loading

Research now distinguishes a historical session route from a clean research
route. `?new=1`, exact object/version handoffs and Dataset handoffs no longer
implicitly reopen the first persisted session (which could be archived); the
default route selects the first active, non-trashed session. Archived sessions
show the existing lifecycle state with explicit `开始新的研究` and
`恢复原会话` controls. The route-loading boundary uses the existing
workbench skeleton for Data and Research so client transitions retain spatial
orientation instead of flashing a blank document state.

The same authenticated browser measured the exact Structure handoff's visible
composer at `593 ms`, with `507/507` effective viewport width. Focused
frontend tests passed `56/56`, typecheck passed, and the service/runtime
listeners remained active. This is a continuity/UI repair; broad
capability-wide qualification and release gates remain open.

The same route-loading shell now covers project Overview and Reports in
addition to Data and Research. All four surfaces retain a stable context/main
workbench skeleton during App Router transitions, reducing the perceived
“page reload” effect without loading scientific payloads early. Route-loading
focused coverage is `3/3`; the change remains presentation-only.

### 2026-08-30 — grounded communication and Report authority convergence

Historical and new scientific answers now share a deterministic grounded
communication projection. Persisted messages remain audit evidence; the
Research read model resolves the exact Interpretation/ScientificResult,
removes visible internal fact-reference echoes and redundant wording, and
accepts the projection only when the unchanged fail-closed grounding validator
passes.

Scientific Report provider output is now normalized back to the validated
Interpretation and ScientificResult for summary, findings, discussion,
conclusion, methods, limitations, exact source labels, evidence and
reproducibility. The authenticated Report
`agent2_report_4f8320601e99ec9e3a78597f9973aa4c` retained exact version
`8859cb49-0766-48cd-8a56-e44f5332e0c5`, displayed two independent coordination
findings and readable CrystalNN/VoronoiNN methods, and omitted the unsupported
“有效且可靠” conclusion. Its Used Context disclosure exposed the exact Result
`14ce2fd1-e5bc-4798-906f-3333df2f7a91`, the exact version, three operation
manifests, and truthful no-compaction state.

Focused evidence is backend `46 passed / 5 historical live skips` plus
`33 passed`, frontend `65 passed`, touched Ruff PASS and diff-check PASS.
PostgreSQL/Redis/MinIO/Redis-workers/DeepSeek were healthy after a bounded
API/Interpretation/Report worker restart; the existing browser tab was
preserved. Phase 14-R remains PARTIAL for capability-wide Viewer, running
cancellation/recovery, retention/export, R12 and exact-SHA release gates.
## 2026-08-30 Phase 14-R scientific-surface evidence reconciliation

The restored current-worktree same-stack campaign passed 12/12 service-backed
tests with zero skips across Agent2 Phase 4/5/6/8, Coordination, XRD and
professional closure. Focused scientific viewer/evidence frontend runs passed
10/10 and 38/38. The authoritative surface matrix now marks the exercised
Dataset, CrystalNN/VoronoiNN and XRD paths PASS, RDF PARTIAL pending its
authenticated scientific-content browser campaign, and leaves renderer-only
families NOT_QUALIFIED. No scientific authority or product behavior changed.

## 2026-08-30 Phase 14-R queued/running cancellation and Continue recovery

Real same-stack browser execution now proves both queued and running
cancellation. Turns `76e51edf-f798-4771-930a-2011027ade96` and
`e2789fe7-9322-4e0d-b43b-23981408e70c` reached durable `CANCELED`; their Jobs
ended `cancelled`, with ToolCall/Artifact/ScientificResult counts remaining
zero. A fast completion race correctly remained `COMPLETED`.

The terminal recovery surface separates Continue, Edit and explicit Rerun.
Continue focuses the existing composer and explains that exact authorized
context is preserved without automatically starting work. Browser and
PostgreSQL evidence confirms zero new Turn/Job/scientific state. Focused
frontend coverage passes 61/61 and browser warnings/errors are zero.
## 2026-08-30 Phase 14-R persistent navigation and RDF closure

The global product shell is now owned by a root App Router frame across the
project, Task Center and Notification Center surfaces. Login return navigation
uses the router, ProductShell prefetches the two global destinations, and a
bounded shared task feed removes duplicate project/job loads. Browser evidence
shows zero document reloads, stable shell DOM identity, warm history
transitions of `54 ms` and `26 ms`, and no duplicate task-feed API work.

The canonical RDF projector now exposes five authoritative facts, including
the configured radius and bin width. The grounding boundary recognizes only
equivalent `angstrom^-3` / `Å⁻³` notation; different units and unsupported RDF
peak claims remain rejected. Fresh exact Data-to-Research Turn
`54fdeada-af1e-4e65-8a8a-855fb52ae76c` completed with Result
`51baaff9-59ea-5a2e-8cad-931bbbd8586d`, Interpretation
`87680594-fe78-46d6-8816-3e8a33993b09`, `grounding_status=VALID`, persisted
Figure/Table links, Evidence and exact-version Viewer navigation.

Focused frontend evidence is `7 files / 52 tests`; focused RDF backend evidence
is `39 passed / 1 historical skip`; typecheck, Ruff and diff-check pass.
Phase 14-R remains `PARTIAL` for the broader capability, mobile/historical,
retention/export, context-stress, R12, regression and release gates.

### 2026-08-31 — Report quality and route continuity

The Report grounding boundary now accepts only the explicit physical-unit
alias `terahertz ↔ THz`; unrelated units remain fail-closed. Deterministic
Report projection preserves the validated interpretation title, readable
method sentences, and fact-backed discussion.

The navigation layer records pending intent while leaving ordinary Next
`<Link>` navigation native. Programmatic Research controls share that router
path, and Report source links carry the persisted session identity so users
open the exact ResearchTurn without an intermediate index lookup. These are
communication and navigation fixes only; scientific authority and execution
remain server-side.

### 2026-08-31 — current-worktree verification

本批次完成前端全量回归 `101 files / 693 tests passed`、后端关键回归
`47 passed / 4 historical skips`、production build `17 routes`、
typecheck、compileall、Ruff、lock 与 diff-check。真实浏览器标签页继续停留
在 exact Phonon Viewer；Report → Research → Viewer 导航没有 document reload，
科学状态计数 `245/322/1291/170` 保持不变。运行时健康为
PostgreSQL/Redis/MinIO/Redis worker/DeepSeek；运维快照仍暴露历史 stale
Turn/Job，因此 Phase 14-R 继续保持 `PARTIAL`，不可提前封板。

同一当前工作树的 PostgreSQL/Redis/MinIO mandatory selection 随后真实执行
`21/21`，覆盖 Agent2 Phase 2–8、Coordination、local environment、
experimental XRD、trajectory analytics、electronic structure 与
professional closure，`failed/errors/skipped = 0/0/0`。完整后端回归为
`1892 passed / 83 historical or optional skips`。

真实 Report 浏览器复核发现旧快照讨论段存在 `。；` 连写。确定性 composer
改为完整句连接，前端 reader 对已持久化旧快照做纯展示层标点归一化；不改变
Result、事实、单位或证据。Report 后端 `30 passed / 4 historical skips`，
Report route `14/14`，浏览器已显示为正常中文分号连接。

### 2026-08-31 — Project History 状态、客户端导航与移动 UI 批次

- Project Overview 与旧 Project Home 每次挂载读取一次当前 Project History，
  并以 `ResearchTurn.status` 覆盖陈旧 Job 展示状态；历史链接继续携带显式
  session/run/Turn 身份。
- 真实浏览器已将 Turn `ec298988-0b32-4e5e-a3c0-8bbb22725818` 显示为
  `分析失败`，不再误报为“分析进行中”。
- 390×844 项目局部导航隐藏 Windows 原生横向滚动条，但保留可滚动语义；
  Overview、Data、Research 的主要操作与 Composer 均可达。
- 导航探针覆盖 Overview/Data/Research/Reports：document requests=0，
  shell/marker preserved；暖态 URL 为 95–115 ms，Data/Reports 可用
  108–121 ms，Research/Overview 可用 929–946 ms。
- 完整桌面/移动性能矩阵所有路由 overflow=0、browser errors=0、
  critical 5xx=0。Research p95 仍约 2.2 s，是后续性能重点。
- 相关前端测试 `38/38`、typecheck 与 diff-check 通过。

### 2026-08-31 — 科学报告与研究时间线的信息层收敛

- Report 复用 Research 的确定性限制文案映射；旧持久化英文限制在中文产品
  中统一呈现，科学事实、单位、证据和 exact source version 不变。
- Research 时间线对 `ASSISTANT_FINAL` 采用有界摘要，只显示前两句已验证结论，
  详细 Findings/Evidence/Limitations 继续留在右侧 Workbench，避免 raw
  fact/evidence ID 和重复段落挤占主阅读区。
- Phonon Band/DOS 与 Electronic Band/DOS 的真实 Viewer 内容在桌面与
  390×844 均可达且无全局横向溢出；Report → Research → Viewer 读取保持
  零科学重算。
# 2026-08-31 Phase 14-R UI/product fluency batch

- 保持 Research Workbench 的 Next App Router 客户端导航与持久化
  `ProductShell`；补齐 `ProductShell` 的 hover/focus 预取去重，避免项目历史、
  研究会话和任务中心的重复权威读取。
- Scientific Report 的 Figure 入口现在按 Result 中的 `figure_type` 绑定精确
  ScientificObjectVersion；Electronic Band 与 DOS 不再错误共享首个来源版本。
- 报告正文继续使用可读科学文本，内部 fact/evidence/step 标识仅保留在可展开
  的 provenance disclosure 中；移动端报告无横向溢出。
- 轨迹 RDF 的真实 Report/Viewer 路径已复核，按精确轨迹版本展示 3 帧、2 原子、
  距离范围、分箱数与 RDF 限制；RDF 峰不会被自动解释为化学键或配位壳。

## 2026-08-31 — Real-source trajectory MSD, Viewer projection and narrative repair

- Added a scientifically explicit unwrapped EXTXYZ acceptance source with Å
  and Å/fs units; the normal parser preserves
  `position_wrapping=unwrapped` and rejects inconsistent frame declarations.
- Uploaded that source through the authenticated upload-session path into
  Dataset `dataset_0001_b7f22cb1bb074f1a`, Profile
  `profile_dataset_0001_b7f22cb1bb074f1a_v2` and object
  `obj_trajectory_990aa1224948`.
- Completed Plan `plan_72e81c4f236b4510b8d23450` and Job
  `job_f2b56ba7d4a34c9288600852`; four artifacts and grounded Interpretation
  `interpretation_fed32da21ee465e9e18d19048d559e93` report three lags and
  `0.0009 Å² @ 0.003 ps`, explicitly without estimating diffusion.
- Fixed the Dataset object-store read projection so the existing normalized
  dataclass remains worker/storage authority while the Viewer receives its
  canonical trajectory payload. The authenticated Viewer renders four real
  frames, unwrapped metadata, time/lattice and interactive controls.
- Fixed the MSD presentation so RDF frame coverage is optional and cannot
  render a false `NaN` sentence; the limitation now states that diffusion was
  not calculated.
- Read-only Report → Research → Report navigation kept
  Jobs/ToolCalls/Artifacts/Interpretations/Reports at
  `261/341/1363/17/36`.

Verification: planner `64 passed`; trajectory parser `24 passed`; backend
object-store/parser `27 passed`; frontend Research/Trajectory Viewer
`70 passed`; typecheck and touched diff-check pass. `trajectory.msd` advances
to `PARTIAL`; its Agent2 snapshot, mobile and historical gates and the
separate diffusion campaign remain open. Phase 14-R remains `PARTIAL`.

### 2026-08-31 — Report 文案与窄屏导航操作批次

- Scientific Report 与 Scientific Presentation 的产品标签改用统一中文语言层，
  保留精确版本、Result、Artifact、契约版本等技术身份供审计。
- Report 顶部返回、来源研究、Markdown 与复现清单操作允许窄屏换行，
  保持单一科学文档阅读流，不引入第二套导航。
- 本批 focused tests `37/37`、typecheck PASS；Report/Presentation 仍只读
  既有 ScientificResult，没有触发新的 Job、ToolCall、Artifact 或 Result。

### 2026-08-31 — 精确 Result 复用浏览器批次

- 从 Report 的精确来源研究进入真实同栈 Research 页面，触发“重新解释（不重算
  科学结果）”，创建 `INTERPRET_RESULT` 子 Turn `219e8d7f-1c62-4566-a05b-e9563efce407`。
- 父 Turn `fbbb0c51-4f39-4c97-ad7a-69ee089884a2` 保持不变；Interpretation
  `188→189`，Jobs/ToolCalls/Artifacts/ScientificResult 保持
  `278/365/1450/184`，证明复用只改变沟通层。
- 当前桌面复用路径已具备可审计零重算证据；整体 Phase 14-R 仍需移动、跨能力
  与完整历史/归档复用矩阵。
- Global Search 从研究页输入 `mat-2` 返回 7 项当前项目授权结果，保留研究、
  报告与数据实体入口；搜索仍是导航读模型，不升级为科学事实 authority。
## 2026-08-31 — Phase 14-R runtime continuity

本轮未关闭既有服务或认证浏览器标签页。frontend/API、PostgreSQL、Redis、MinIO
均保持运行，`/health/runtime` 真实返回 PostgreSQL/Redis/MinIO/Redis worker。
项目内 Report → Data 使用客户端路由完成切换，保留全局上下文栏与单一主工作区，
不回到登录恢复态。Phase 14-R 仍为 PARTIAL，成熟产品缺口与 release seal 未提前
宣称完成。
### Phase 14-R archive/navigation fluency batch (2026-08-31)

The authenticated Data Platform tab completed a real Archive → Archived list →
Restore cycle for `55648f55-51e4-4c94-b4fe-72cae944a54c`, retaining exact
version `53037b6a-7a68-43ac-85de-6e920dfd4420` and returning the object to the
active list. Product links now opt into Next same-origin prefetch while the
ProductShell stays mounted and marks the main workbench busy during a pending
transition. Focused frontend tests and typecheck pass; mature-product closure
remains PARTIAL.

### Phase 14-R composition-space/regression product batch (2026-08-31)

- Requalified exact ResearchTurn
  `fbbb0c51-4f39-4c97-ad7a-69ee089884a2` through Presentation, persisted
  composition Figure/Table, regression diagnostic Table, Evidence, exact
  Dataset Viewer and professional Report.
- Stable sample `sample-fe2o3`, exact Dataset version
  `cf2aeeea-53ad-452a-a4ef-7b61555004e5`, authoritative MAE/RMSE/R² and
  residual semantics remained visible on desktop and `390x844`.
- Evidence resolved the completed ToolCall and persisted Artifact checksum;
  browser warnings/errors, duplicate IDs and horizontal overflow were zero.
- Read-only navigation kept scientific persistence counts at
  `278/365/1450/184/36`; focused frontend coverage passed `34/34`.
- The exercised `data.composition_space` and `ml.regression_evaluation` paths
  advance to PASS. Phase 14-R remains PARTIAL for the still-open mature-product
  gates and release seal.

### Phase 14-R coordination-histogram product batch (2026-08-31)

- Reopened exact Turn `63d21ee3-6e18-49b3-ad6b-b3fb578563c5` and rendered its
  persisted coordination Figure/Table, exact Structure Viewer and Evidence.
- Preserved fixed-cutoff semantics (`3 Å`, one Si site, coordination number 6)
  and the boundary against CrystalNN/VoronoiNN/bond-order interpretation.
- Generated Report `agent2_report_19a0d0c261c28577101de81532464893`
  through the normal product action; only Report count changed `36→37`, with
  scientific persistence counts unchanged.
- Mobile Report was bounded with zero duplicate IDs or browser warnings/errors;
  focused frontend coverage passed `29/29`.
- `structure.coordination_hist` advances to PASS; Phase 14-R remains PARTIAL.

### Phase 14-R diffusion communication batch (2026-08-31)

- Closed the current exact diffusion path across Research Presentation,
  Evidence, 24-frame trajectory Viewer and Scientific Report for Turn
  `fb72c2ad-bed1-47d7-b557-f398f04a8ede`.
- Removed the duplicate legacy `0 个步骤` process summary when authoritative
  Agent2 progress exists; the Timeline now presents one truthful progress
  region.
- Repaired Report compound-unit/evidence grounding at the communication
  validator layer. Exact `Å²/ps` and `1–6 ps` claims pass only through the
  persisted fact/evidence/result-item graph; forged intervals and units remain
  rejected.
- Desktop and `390x844` Workbench/Report/Evidence remained bounded; Viewer
  interaction and all read-only scientific surfaces caused zero Job,
  ToolCall, Artifact or ScientificResult growth.
- Related regression: backend `79 passed / 5 historical skips`, service-backed
  Report `4 passed / 0 skipped`, frontend `96 passed`, Ruff/diff PASS.
- Remaining: capability-wide historical/archive coverage, lifecycle/
  retention/export, context stress, R12, full regression and P14R release CI.

### 2026-08-31 — 归档科学来源的 Report 生命周期披露

- 修复真实浏览器发现的沟通层缺口：Report 精确来源投影从权威
  `ScientificObject.lifecycle_status` 返回状态，与 `is_current_version`
  分开表达；归档对象可以同时保持其不可变当前版本。
- 对象 `f834e358-9944-4fe8-a3ab-f85d68041f54` 归档期间，Report
  `agent2_report_e54681009a0e49abe371247d9053ce61`、Result
  `26127c48-d736-4983-b035-b68db238f6a7`、4 条 Evidence 与 24 帧轨迹
  Viewer 均保持精确版本 `a22745f2-17b6-434f-ba4c-3fe6bd244841` 可读。
- Report 明确显示“当前版本 · 来源对象已归档”；Markdown 与非可执行复现清单
  同步保留该管理元数据。归档查看器从第 1 帧切换到第 2 帧，科学计数
  `285/377/1493/191` 零增量。
- 通过产品 `恢复科研对象` 返回 ACTIVE；版本数仍为 1、current pointer
  不变、`archived_at` 清空。后端 33 passed/4 historical skips，前端
  33 passed，Report service-backed 4 passed/0 skipped，typecheck/Ruff/diff
  PASS；PostgreSQL active 1/idle 9/idle-in-transaction 0，6 workers idle。
- 该精确 diffusion 路径的 archive/historical continuity 已闭合；Phase 14-R
  仍需诊断 Table、context/retention/R12、全回归和 P14R release seal。

### 2026-08-31 — Report Table 与应用内导航批次

- Report 从不可变 `ScientificResultBundle.tables` 投影有界
  `table_sources`，真实 Report 页面展示“轨迹扩散性质”和“轨迹均方位移”，
  每张表保留稳定引用、Artifact 链接和精确对象/版本来源；表格打开明确是
  只读持久化数据，不触发科学重算。
- 内部产品导航继续使用 Next App Router：指针/键盘意图预取、共享
  ProductShell 保持挂载、等待期间显示 `aria-busy`，重型 Viewer 延迟加载，
  避免页面级重新加载和空白闪烁。
- 运维快照脚本补齐独立命令导入路径，清空 `PYTHONPATH` 后仍可执行
  `--help`；后端 `49 passed / 4 historical compatibility skips`，前端相关
  `99 passed`。
- 运维快照新增显式 `--same-stack` 模式，直接选择本地
  PostgreSQL/Redis/MinIO 资格拓扑，避免干净 shell 静默落回 SQLite/local；
  实测 `status=ok`、6 workers idle、queued=0、idle-in-transaction=0。

### 2026-08-31 — Research 时间线重复消息修复

- 修复持久化重放导致的相邻重复消息：`ResearchPages` 现在只折叠相同
  `role/content` 的相邻副本，保留被助手消息隔开的有意重复提问。
- 真实认证 Research 页面复核从重复消息收敛为 4 条真实时间线消息，
  保留原始消息 ID；文档宽度 731px、视口宽度 731px、浏览器错误 0。
- 对应前端 Research/ProductShell/Report 回归为 `94 passed`，并通过
  typecheck、compileall、Ruff 与 `git diff --check`。服务和 Chrome 标签页
  保持运行。

- 全前端当前工作树回归已复核为 `102 test files / 728 tests passed`；
  后端 Phase 14-R 相关回归 `46 passed / 4 historical compatibility skips`。
  认证浏览器 Data→Research→Research 应用内切换保持 `documentWidth=731`
  与 `viewportWidth=731`、错误 0。

### 2026-08-31 — 导航提交后立即清理等待态

- `ProductNavigationProvider` 现在在 App Router 目标 pathname/query 提交后
  立即清理 pending intent，15 秒超时只作为异常兜底，不再让已完成页面继续
  显示切换中状态。
- `RouteTransitionProgress` + `ProductShell` 回归 `18 passed`，typecheck
  PASS；该修复只作用于壳层导航，不改变科学执行、版本或结果权威。
- 首次实现触发静态 `/settings/models` 的 Suspense 构建约束，已改为仅在
  pending 期间进行有界 URL 检查；生产构建恢复为全 17 路由 PASS。
- 精确历史轨迹 Turn `fb72c2ad-bed1-47d7-b557-f398f04a8ede` 的移动对话面板
  已展开“本次上下文”，显示 1 项精确来源、manifest
  `c4785024-6027-42af-9a1f-52143afd7303`、策略版本 `agent2.context-policy/2.0`
  与版本 `a22745f2-17b6-434f-ba4c-3fe6bd244841`；展开后仍无溢出或重复 ID。

### 2026-08-31 — 报告章节导航与精确来源上下文

- Scientific Report 增加稳定的报告章节导航，桌面端保持研究文档密度，
  移动端改为可横向滚动的紧凑导航，不引入第二套路由。
- Scientific Presentation 区分“固定结果”和“固定来源版本”两个上下文
  控件，均复用既有 Session Memory 授权 API，不触发科学重算。
- 认证浏览器 Report `agent2_report_e54681009a0e49abe371247d9053ce61`
  显示 8 个章节链接，布局 `715/715`；轨迹来源版本
  `a22745f2-17b6-434f-ba4c-3fe6bd244841` 固定成功。
- 前端 focused `26/26`、typecheck、production build、compileall 与
  `git diff --check` 通过；Phase 14-R 仍为 `PARTIAL`。
- 随后全前端回归完成 `102 test files / 730 tests passed`；同栈运维快照
  `status=ok`，PostgreSQL `active=1/idle=12/idleInTransaction=0`、
  Redis `6/0`、MinIO `ok`。

### 2026-08-31 — 目录请求连续性

- `listProjects()` 与 `listDatasets()` 增加 20 秒有界共享请求缓存，并在
  创建、更新、归档、回收站、上传等写操作后显式失效，减少 App Router
  返回导航期间的重复请求，同时保持写入后的数据新鲜度。
- Planner/Data focused `66/66`、typecheck、`git diff --check` 通过；Phase
  14-R 仍为 `PARTIAL`，未创建 release commit。

### 2026-08-31 — 研究控制在窄屏下的可见性

- 从科学呈现点击“编辑问题”或“继续研究”时，自动切换到“对话”面板；
  `?edit=` 路由也保持对话优先，避免移动端把不可变分支编辑器留在工作台
  后面。
- 认证浏览器确认 `selectedTab=对话`、编辑提示可见、布局 `731/731`、
  无 alert；Research/Presentation focused `71/71`。完整编辑提交与分支
  持久化仍待资格验证。

### 2026-08-31 — 编辑分支真实浏览器验证

- 认证浏览器通过不可变编辑器创建新 Turn
  `17c0b9d1-b5c0-47f9-b93c-c5f8a1cb19df`，显示 `2/2` 分支并完成两个真实
  分析输出。
- 使用“上一个研究分支”返回历史 Turn
  `fb72c2ad-bed1-47d7-b557-f398f04a8ede`，原问题与结果保持不变；无 alert
  或布局溢出。停止/重试与严格 390px 浏览器资格仍未完成。

### 2026-08-31 — 失败运行恢复入口可见性

- 历史 `run=` 路由在确认持久化状态为 `FAILED/CANCELED` 后，窄屏自动切换
  到“对话”面板，直接显示“继续研究”和“重新研究”。
- 认证浏览器确认 `selectedTab=对话`、恢复按钮可见、布局 `731/731`、无
  alert；ResearchPages focused `64/64`。完整停止/重试压力资格仍待完成。

### 2026-08-31 — Grounding 展示舍入与真实重试

- 解释器 grounding 原先按完整数字字符串比较，导致权威轨迹事实
  `0.038618084156`、`0.064094868867`、`0.970301847945` 在用户答案中以
  `0.0386`、`0.0641`、`0.9703` 展示时被误拒。现改为按声明小数分辨率、
  且不超过权威值 1% 的确定性舍入容差；单位、证据边和引用校验保持
  fail-closed。负向回归仍拒绝无关数值。
- 真实同栈重试创建 Turn `b82c5758-fac8-4f30-b0ab-5df94dd68369`，
  Result snapshot `8d506aa2-0247-4ea8-ae39-0c629ad3b991`，10 个权威
  facts、2 ToolCalls、8 Artifacts，`grounding_status=VALID`、终态
  `COMPLETED`；精确来源仍为 object `f834e358-9944-4fe8-a3ab-f85d68041f54`
  / version `a22745f2-17b6-434f-ba4c-3fe6bd244841`。
- 同栈快照保持 PostgreSQL `active=1/idle=12`、
  `idle-in-transaction=0`、Redis 6 idle workers/queued 0、MinIO ok。两个
  fresh Dataset 编辑请求按 `QUERY_DATA` 语义正确 `ANSWERED`，未强制创建
  科学 Job；整体 Phase 14-R 仍为 PARTIAL。
### 2026-08-31 — Service recovery and mobile scientific reinterpretation

After the local services were stopped and restored, the qualification topology
was verified without closing the existing authenticated Chrome tab:
PostgreSQL `55434`, Redis `6379`, MinIO `9000/9001`, API `8000/8002` and
frontend `3000` were listening; `/health/runtime` reported the real
PostgreSQL/Redis/MinIO/worker stack. The 390x844 Research Workbench now
reaches the scoped reinterpret action and created child Turn
`89037298-7fb1-4c48-bbd3-5407d3f93f41` with `VALID` grounding and no Job or
scientific Result recomputation. Navigation measurements showed zero document
reloads with cold `120–267/137–628 ms` and warm `102–141/120–163 ms`
URL/usable timings. Broader Phase 14-R gates remain open.

### 2026-08-31 — Structure Viewer and XRD table qualification

The authenticated Structure Presentation path now reaches the localized
`查看器` link and opens a real Canvas-backed exact-version Viewer for
`dc3c3eee-f254-4edf-a0fa-c955402b3069` /
`8859cb49-0766-48cd-8a56-e44f5332e0c5`, with CrystalNN/VoronoiNN findings and
evidence still visible. The XRD Data Platform path opens its persisted
nine-row numeric table at desktop and mobile widths without scientific
mutations. Report Structure/Dataset quality checks retain exact source
versions and bounded chapter sections; the mobile chapter strip is an
intentional internal scroller, not global page overflow.

### 2026-08-31 — Task/notification recovery and full regression

The authenticated Task Center/Notification surface read 30 persisted tasks,
8 attention items and 4 canceled records. With no live persisted task, Stop
was correctly absent; the offline banner stated that server research may
continue and cleared after reconnect. Mobile document/body widths were
390/390 with zero overflow. The current frontend full suite passed 730 tests;
the Phase 14-R backend/service subset passed 10 with 8 historical skips.
### 2026-08-31 — Global Search same-stack proof

The authenticated global search modal returned 8 authorized `mat-2` results
from the PostgreSQL-backed API. Desktop and 390x844 mobile widths stayed
bounded with no non-auth mutation; search remains a navigation read model,
while broader historical/organization coverage remains open.

### 2026-08-31 — Context disclosure and edit continuity

Fresh authenticated Research browser proof opened the real context disclosure
and nested audit details, exposing the persisted manifest identity, policy
version, `12000` token input budget, estimated input and context fingerprint.
Exact Dataset version `be02266a-7d4f-4ebb-9f28-3132855167d0` remained visible;
evidence and edit/continue/rerun/re-interpret controls remained available.
Editing preserved the original ResearchTurn route and presentation heading IDs
were Turn-scoped without duplicates. Provider-scale context stress/replay and
full message lifecycle acceptance remain open.

### 2026-08-31 — Fresh same-stack service regression

The current-worktree Phase 14-R service/context regression completed against
PostgreSQL/Redis/MinIO with `26 passed`, `0 failed`, `0 errors`, `0 skipped` in
`425.80s`. The follow-up operations snapshot remained healthy
(`active=1`, `idle=12`, `idle-in-transaction=0`, checked-out `0`, six idle
Redis workers, queue `0`, MinIO `ok`). Broader mature-product and release gates
remain open.

### 2026-08-31 — Current-worktree frontend regression

The full frontend suite passed `102 test files / 730 tests` after the
context disclosure accessibility repair. No new failure or mandatory skip was
introduced.

### 2026-08-31 — Mobile Report chapter navigation repair

报告章节导航在 390px 移动视口出现 `422px` 内容宽度的真实横向溢出。
现已改为多行、有界的移动布局，章节入口保留可点击触控高度，认证浏览器
复核 `overflowCount=0` 且 document/body 均为 `390px`；未改变 Report
快照、Result、来源版本或路由语义。Phase 14-R 仍保持 `PARTIAL`。

### 2026-08-31 — Full backend baseline environment correction

完整非 integration 后端回归在移除 service-only PostgreSQL 环境覆盖后重新
执行，临时 SQLite 迁移夹具与同栈服务资格被正确隔离：`1919 passed`、
`32 skipped`、`170 warnings`，0 failed。此前 40 项失败确认是测试环境污染，
不是当前工作树产品回归。

### 2026-08-31 — Context disclosure accessibility repair

Added stable accessible names to the Research context and nested audit
disclosures. The focused ResearchPages suite passed `64/64`; native details
behavior and exact source/version semantics are unchanged.

### 2026-08-31 — Project history navigation cache repair

Project Home no longer forces a complete history refresh on every project
selection. It reuses the existing bounded history cache, while lifecycle and
data mutations still invalidate that cache. This removes an unnecessary
full-ledger round trip from App Router back-navigation without changing
scientific identity or provenance. `ProjectHome.test.tsx` verifies one history
request per project when switching away and back.

The post-repair full frontend regression completed with `102 test files /
732 tests passed`; typecheck and the Next production build (17 routes, 104 kB
shared first-load JS) passed as well. Services and the authenticated browser
remain online.

### 2026-08-31 — Report export feedback and browser proof

报告 Markdown 与复现清单导出现在共用一个有界 Blob 下载 helper，并在
点击后显示可访问的 live status；浏览器不支持 Blob URL 时 fail-closed，
显示可重试错误，不改变 Report/Result/来源版本。认证 Chromium 真实打开
Report `agent2_report_401cfb421fcab8a9366e06fedb3acb6d`，记录 Markdown
`2529` bytes 与复现 JSON `1403` bytes 两个导出 Blob，报告标题与复现信息
均可见；只有预期 bootstrap `401`，无 5xx/critical。Focused
ScientificReportRoute `20/20` 通过。

### 2026-08-31 — Report lifecycle browser recheck

认证 Report 索引在同栈服务上重新验证了操作菜单、服务器依赖影响预览、
归档与恢复，以及移动端布局。Report
`agent2_report_e54681009a0e49abe371247d9053ce61` 显示 `11` 项依赖，归档/
恢复后身份不变；`390x844` 下 document/body 均为 `390/390`、溢出为 `0`。

## Agent-2.0 Phase 14-R — task/notification refresh continuity

- 状态：已完成本批次
- 完成时间：2026-08-31
- 修改文件：`apps/web/app/components/TaskCenterPage.tsx`、
  `apps/web/app/components/NotificationCenterPage.tsx` 及对应测试。
- 修改摘要：首次进入仍显示完整 loading；后续在线、可见性和定时刷新改为
  保留当前任务/通知内容并显示“正在同步最新状态…”，避免每 30 秒整页
  闪烁或暂时丢失可用操作。
- 测试结果：Task Center/Notification Center `5/5`；typecheck 已通过。
- 提交/CI：未提交，Phase 14-R 仍为 `PARTIAL`；服务与 Chrome 标签页保持运行。

认证 Chromium 在同栈上复核 `/tasks` 与 `/notifications`：读取 30 条任务、
通知筛选可用，390x844 下 document/body 均为 390、无横向溢出；断网提示在
恢复网络后清除。仅出现预期 bootstrap 401，无 5xx/critical。

后台同步失败时保留最近一次授权数据，并显示“同步失败，当前显示上次结果”；
首次加载失败仍进入原有错误态，避免将 stale data 静默伪装成实时状态。

最新工作树回归：前端 `102 test files / 734 tests passed`，typecheck 与
production build（17 routes、104 kB shared first-load）通过；同栈服务保持
PostgreSQL/Redis/MinIO、6 个 idle workers、队列 0。

任务中心移动端认证浏览器复核：`390x844` 下 30 条任务可读，
document/body `390/390`、无横向溢出；仅预期 bootstrap 401，无 critical。

### 2026-08-31 — Scientific table mobile interaction repair

真实 Data Platform 移动端表格内部内容宽度为 `400px`，但页面与 body 均保持
`390px`，因此这是 bounded table 的可操作性问题而非全局溢出。已为
`workspace-table-scroll` 增加键盘可聚焦 `role=region`、明确的横向滚动
accessible label、inline overscroll containment 与稳定滚动条空间。
认证 Chromium `390x844` 复核：`clientWidth=390`、`scrollWidth=400`、
`pageOverflow=false`、表格可发现且可横向查看；只有预期 bootstrap `401`。
Focused Dataset/Product/Workspace 测试 `70/70` 通过。

### 2026-08-31 — Scientific table interaction regression

Workspace shell focused test 已锁定真实数据表的可访问滚动区域契约
（`role=region`、稳定 label、准确 table 语义），防止后续移动布局改动退化
为无标签横向滚动。Dataset/Product/Workspace focused `71/71` 通过；完整前端
仍为 `102 files / 734 tests passed`，typecheck 与 production build 保持通过。

### 2026-08-31 — Global search lifecycle continuity

全局搜索的报告结果现在复用现代 Scientific Report snapshot 已有的项目级
生命周期映射；归档/回收站报告不会再被错误标成 active。搜索仍是有权限的
导航读模型，不改变 ScientificResult 或 Report 快照权威。新增后端回归覆盖
现代报告的 archived/active 筛选。

### 2026-08-31 — Task Center cancellation copy

任务中心统一 `cancelled` / `canceled` 两种后端终态拼写，避免已取消研究
在部分运行记录上误显示为“处理中”；保留已有停止、重试和只读历史语义。

### 2026-08-31 — Truthful bounded search counts

全局搜索继续限制返回 payload 大小，并在某类命中触及边界时返回
`truncated`；UI 会显示“至少 N 项”，避免把有界候选数误报为精确总数。
新增回归覆盖 limit 小于结果总数的情况。

### 2026-09-01 — Task Center stop confirmation and bounded feed disclosure

任务中心的“停止研究”现在先打开可撤销确认对话框，明确说明停止只影响
当前 ResearchTurn 的未完成分支，并保留已提交的有效 Artifact；只有确认后
才调用既有取消 API。任务列表超过 30 条时显示“当前筛选显示最近 30 项”，
并指向项目历史，避免有限展示被误解为完整历史。`TaskCenterPage` focused
回归为 `5/5`，NotificationCenter 回归为 `3/3`，完整前端回归为
`102 files / 737 tests passed`，未改变 Job/ToolCall/Artifact/ScientificResult
权威。

通知中心沿用同一 bounded-window 语义：筛选结果超过 30 条时明确提示最近
30 条，并保留对应项目历史作为完整读取入口；新增通知组件回归覆盖。

任务数据源的 `nextCursor` 现在也会进入共享 task feed；即使当前返回行数
不足 30，只要服务端仍有更早记录，任务/通知中心也会显示 bounded-window
提示，不再把分页边界误报为完整历史。

### 2026-09-01 — App Router navigation and branch-control closure

- 项目主导航继续采用 Phase 9C 的双层上下文：全局栏承载跨项目任务、
  通知、搜索与账户；项目栏仅承载概览/数据/研究/报告。研究后续操作仍
  留在 Result/时间线上下文，不上移为全局动作。
- Next 内部导航预取现在合并同一路径 1.5 秒内的 pointer/focus 意图；路由完成
  由 App Router 的 pathname/search 提交信号驱动，不再每 50ms 轮询 location。
- 不可变 production build `3008` 实测：桌面 cold/warm usable
  `61–118/33–70 ms`，移动 `66–102/41–68 ms`；16 次转换均为
  `documentRequests=0`、ProductShell 节点保持、登录态不重复读取。
- 编辑问题的真实 child Turn `92fcd73e-...` 保留 parent、精确 Dataset
  object/version 与 17 个 facts；桌面/390px 分支切换无全局溢出。
- Focused frontend `85/85`、typecheck、production build 均通过。

### 2026-09-01 — lifecycle/export/recovery evidence batch

- 同栈浏览器完成 Structure Report Markdown 与复现清单导出，验证报告仍为
只读科学投影。
- 新 Research Session 完成固定、重命名、归档、回收站、恢复和再次归档；
  桌面与 390x844 均无溢出或关键错误。
- Task/Notification 完成终态停止按钮隐藏、筛选、离线提示和重连恢复。
- 全前端回归 `102 files / 739 tests`，Phase14-R 后端
  Context/Operations/Recovery `16 passed`。总体仍保持 `PARTIAL`，未创建
P14R 发布提交或 CI。

### 2026-09-01 — Report batch management ergonomics

报告列表批量管理现在明确显示“当前筛选”，并提供“全选报告 / 清空报告 /
清除选择”按钮，同时保留无障碍 checkbox 与现有依赖预览生命周期动作。
`ScientificReportsIndexPage` focused 回归 `8/8`，未改变科学结果或报告快照
权威。`ScientificReportsIndexPage` focused 回归更新为 `9/9`。

报告页根节点改为 ProductShell 主工作区内的带标题 section，避免重复
`main` landmark；Report/ProductShell focused 回归 `20/20`。

完整 Python 回归在修复遗留 Phase10K3 manifest 字节/SHA 漂移后通过：
`1924 passed / 84 skipped`；独立 PostgreSQL/Redis/MinIO 资格库上的
Agent2 Phase2/3 + Phase10L4 campaign 为 `5 passed`。同栈运维快照保持
`active=1 idle=12 idle-in-transaction=0 checkedOut=0`、Redis 6 idle
workers/queue 0、MinIO ok。

### 2026-09-01 — canonical MSD surface and report-route continuity

- 通过正常报告列表重新打开 Agent2 轨迹报告
  `agent2_report_e54681009a0e49abe371247d9053ce61`，确认独立
  `轨迹均方位移` Figure/Table、Evidence、24 帧 Viewer 与精确版本
  `a22745f2-17b6-434f-ba4c-3fe6bd244841` 均可用。
- 报告只读打开前后 Jobs/ToolCalls/Artifacts/ScientificResultSnapshots
  均为 `301/395/1565/203`；`trajectory.msd` 从过期 `PARTIAL`
  校正为 `PASS`，standalone legacy planner 证据仍保留为兼容历史。
- ProductShell 不再重复 shared navigation provider 已执行的 route prefetch；
  pathname 切换会重置 document scroll，query-only ResearchTurn 切换保留
  workbench scroll。报告页保持单一 `main`、无重复 ID、无全局溢出。

### 2026-09-01 — ScientificObject 批量生命周期浏览器闭环

- Data Platform 批量选择真实对象
  `cbfd4a9f-6659-4196-be2b-60f118bfa12f`，完成
  `ACTIVE → ARCHIVED → ACTIVE`，并通过显式“已归档”视图和行级恢复入口
  验证发现语义。
- 精确版本 `cf2aeeea-53ad-452a-a4ef-7b61555004e5`、版本数 `1` 与
  3 个 Result 引用全程不变；未创建科学版本、未删除历史科学权威。
- ProductPages `32/32`、ScientificObject atomic bulk API `1/1`、
  Project/Dataset dependency/lifecycle `4/4` 通过。
## 2026-09-01 Phase 14-R shared Research context-state closure

- `ResearchPages` now owns the authoritative client projection of
  `Agent2SessionMemory` and passes it into Scientific Presentation. Removing or
  pinning a Result/source from either UI surface updates the same state; the
  left context strip and right action labels can no longer contradict each
  other.
- Authenticated browser proof used Turn
  `fb72c2ad-bed1-47d7-b557-f398f04a8ede`, Result
  `26127c48-d736-4983-b035-b68db238f6a7` and exact trajectory version
  `a22745f2-17b6-434f-ba4c-3fe6bd244841`. The original source-only pin state
  was restored.
- Scientific counts remained `Jobs=301`, `ToolCalls=395`, `Artifacts=1565`,
  `ScientificResults=203`; the exact ContextSnapshot count remained `1`.
- Current focused verification: backend `30 passed`, frontend `104 passed`,
  shared-memory frontend `73 passed`, typecheck PASS, real isolated
  PostgreSQL/Redis/MinIO reuse `4 passed / 0 skipped`.

## 2026-09-01 Phase 14-R ContextManifest budget/replay and recovery closure

- Added explicit boundary coverage for all five ContextBudgetPolicy operations:
  well below, near, exactly at, over and significantly over budget, plus
  critical-science fail-closed. Focused suite: `11 passed`.
- Inspected `458` real persisted operation manifests; maximum estimates remain
  `241/12000` Orchestrator, `476/10000` Planner, `1157/12000` Interpreter and
  `1802/10000` Report, with zero truncation.
- Authenticated historical Turn `fb72c2ad…` exposes manifest/policy/budget/
  fingerprint and exact version `a22745f2…` without prompts or chain-of-thought.
- Current Task Center shows `60` persisted tasks and Notification Center shows
  `45` persisted notifications, including partial/failure/canceled states and
  exact reopen routes. Existing offline/reconnect and isolated Redis recovery
  evidence remains valid.
## 2026-09-01 Phase 14-R Trash/resource batch

- Added a single account-menu entry to the unified `/trash` surface. The
  surface is a dense management list with type filters, server-derived
  dependency previews, exact-name confirmation for safe empty Project/Dataset
  purge, and responsive stacked actions at mobile widths.
- Kept lifecycle mutations in the existing project, dataset, scientific
  object, session and report authorities. No scientific version/result state
  is created or mutated by Trash restore/purge.
- Added the redacted `resourceGovernance` operations projection and a
  PostgreSQL-authoritative per-Project active ResearchTurn cap with typed 429
  frontend messaging. This is governance of bounded execution resources, not
  a second queue or scientific authority.

## 2026-09-01 Phase 14-R project organization batch

- Added bounded Project pinning as non-scientific organization metadata. The
  existing `project_configs` authority stores `pinnedProject`; the project
  directory and Project History expose the flag and lift pinned projects
  without changing scientific identity, lifecycle, or updated-at ordering.
- ProductPages exposes `固定到顶部` / `取消固定` in the existing row action
  menu and keeps the state visible in the row summary. Viewer/read-only users
  remain server-denied for the mutation.
- Verification: ProductPages `33 passed`, project access `13 passed`, touched
  Ruff PASS, typecheck PASS, production build PASS.

## 2026-09-01 Phase 14-R project tags and catalog discovery

- 项目组织标签已在既有 `project_configs` 非科学元数据边界内落地，编辑
  表单做 trim、大小写不敏感去重、12 个标签/单标签 40 字符限制。
- 项目目录提供与搜索、生命周期分段同层级的标签筛选；全局授权搜索在
  项目名称/说明之外匹配标签并回显组织摘要。该筛选只影响导航发现，不
  改变 ScientificObject、ScientificObjectVersion、Result 或上下文。
- Verification: ProductPages `35 passed`, project access `23 passed`,
  touched Ruff PASS, typecheck PASS.

## 2026-09-01 Phase 14-R project catalog query consolidation

- 项目目录的成员角色和组织元数据查询已改为对可见项目集合的批量读取，
  仍保留旧 schema fallback；项目固定/标签功能不会制造 per-row N+1。
- Verification: project access `23 passed`, touched Ruff PASS；同批次
  ProductPages `35 passed`, typecheck/build PASS。

## 2026-09-01 Phase 14-R bulk project organization

- Projects 选择模式现支持批量固定/取消固定，沿用已有归档/回收站事务和
  server authorization；组织操作只改变 `project_configs.pinnedProject`。
- Verification: ProductPages `36 passed`, project access `24 passed`, touched
  Ruff PASS。

## 2026-09-01 Phase 14-R project provenance export

- 项目目录继续复用现有 overflow action menu，增加“导出项目清单”。操作
  位于项目管理动作而不是主导航，避免把一次性可移植性操作与科学研究主
  CTA 混在一起；导出完成后在工具栏下方提供明确的非阻塞状态提示。
- 导出内容是服务端授权、有界、不可执行的 provenance manifest，只包含项目、
  数据集、对象/版本、研究会话/Turn、ScientificResult 与 Report 的身份和
  受限来源引用；不包含原始科学载荷、Provider prompt/response、凭据或存储
  内部信息。浏览器使用同栈 3000 → 8002 API 真实验证了成功状态。
- 该动作不触碰 ScientificObject、ScientificObjectVersion、Result 或 Report
  权威；标签/固定状态仍属于非科学项目组织元数据。桌面和移动布局继续沿用
  项目列表的紧凑操作密度与可折行摘要。

## 2026-09-01 Phase 14-R Report organization

- Report rename and pin actions live in the existing row overflow menu rather
  than adding primary-page controls or another management framework.
- Rename is explicitly described as a display-name change. The immutable
  snapshot title remains available as `source_title`, and the dialog explains
  that Result, Evidence and exact source bindings remain unchanged.
- Pinned Reports sort above chronological Reports and expose a compact
  `已固定 · <状态>` trailing label. This preserves the dense scientific
  workbench hierarchy and remains bounded at `390 px` without horizontal
  overflow.
- Search, list and direct Report reads share the same authorized organization
  projection; the frontend does not derive or mutate scientific identity.

## 2026-09-01 Phase 14-R release-candidate reconciliation

- Current same-stack runtime remains API `8005`, frontend `3013`,
  PostgreSQL `55434`, Redis `6379`, MinIO `9000/9001`, and six idle workers.
- Fresh mandatory service-backed campaign passed `70/70` with zero failures,
  errors or skips. Full current-worktree backend passed `1948` tests; frontend
  passed `764` tests across `105` files.
- Production navigation/browser evidence remains bounded: App Router
  `documentRequests=0`, desktop/mobile global overflow `0`, duplicate IDs `0`,
  console/page errors `0`; ARIA relation fixes are covered by `116` focused
  tests.
- Remaining release work is exact P14R-A/P14R-B commit and current-head CI only;
  Phase 15 remains uncreated and unstarted.

## 2026-09-01 Phase 14-R P14R-A exact-SHA qualification

- Final P14R-A candidate `8607b1c1f1cb4afbcbf777b69129a0055a141791` passed exact
  CI run `33501524613`. Unit, frontend typecheck/build/browser evidence,
  PostgreSQL/Redis/MinIO service-backed integration, and Linux/Windows replay
  jobs all passed.
- P14R-B is now limited to authoritative evidence finalization and exact-head
  CI; no product architecture remains open in this release candidate.

## 2026-09-01 Phase 14-R scientific payload availability remediation

- Diagnosed user-visible scientific 500/missing states as a split MinIO data
  root plus an unhandled `NoSuchKey`, not stopped PostgreSQL/Redis/MinIO
  services or a scientific identity defect.
- Recovered 1,551 exact/deterministically validated objects into the active
  bucket. The canonical diffusion Job now loads all 8 Artifacts with matching
  sizes and SHA-256 values; its trajectory exact-version Viewer is `READY`.
- Added typed 404/503 Artifact storage boundaries and separate professional UI
  states for confirmed missing payloads versus transient loading failures.
- Authenticated desktop/mobile Research, Report and Dataset validation has no
  unexpected 5xx, infinite scientific loading or horizontal overflow.
- Five historical references have no exact recoverable bytes and remain
  explicitly unavailable; no scientific payload or latest-version substitute
  was fabricated.

## 2026-09-01 Product maturity batch — same-stack runtime and shared UX seams

- Confirmed the retained browser-facing stack is actually PostgreSQL `55434`,
  Redis `6379/13`, MinIO `9000` and Redis-backed workers; `/health/runtime`
  reports the same truth.
- Applied migration `0029_product_maturity_platform_roles` to the live
  qualification PostgreSQL database. Provider mutations now require explicit
  `PLATFORM_ADMIN`; ordinary researchers receive a read-only model-service
  surface while server authorization remains authoritative.
- Rebuilt the frontend against API proxy target `8005`; this fixed the browser
  login/model-settings `500` caused by a production build still targeting the
  stale `8000` backend.
- Replaced the global task/notification project fan-out with one bounded,
  authorized task-feed request, and tightened blank global search behavior.
- Added monotonic persisted-result loading state, mobile project identity,
  and a current product reality audit at
  `docs/agent2/product_maturity/PRODUCT_REALITY_AUDIT.md`.

## 2026-09-01 Product maturity data visibility closure

- Confirmed the reported unavailable pages were not a service outage. The live
  runtime remains PostgreSQL/Redis/MinIO/API/six workers/frontend/DeepSeek.
- Recovered the only user-visible missing Dataset payload using exact
  byte/checksum/parser/object identity proof; no version, Result or Report was
  changed and no later source was substituted.
- Introduced the explicit `EMPTY` Dataset contract so zero-resource records show
  import guidance instead of a storage failure. Legacy Dataset detail routes
  now converge on the current Data Platform and cannot expose Planner execution
  for an empty source.
- Current authenticated inventory is 28/28 Datasets correctly classified,
  13/13 exact-version Viewers READY, 241/241 Artifact contents readable and
  11/11 Reports readable. The 70-route product sweep contains no 500 response.
- Verification: full backend `1970 passed`; full frontend `106 files / 773
  passed`; isolated PostgreSQL/Redis/MinIO campaign `70 passed / 0 skipped`;
  build/typecheck/compileall/lock/Ruff/diff PASS.

## 2026-09-01 Product maturity runtime reload and browser recheck

- The reported `/trash` and `/account` client failures were traced to a stale
  3013 Next process serving a chunk manifest from the default `.next` directory,
  not to PostgreSQL, Redis or MinIO availability.
- The API reload briefly used incorrect MinIO credentials; restoring the
  repository-documented `mdi-local` / `mdi-local-dev` pair returned
  `/health/runtime` to PostgreSQL/Redis/MinIO/Redis-worker/DeepSeek `ok`.
- A fresh authenticated browser tab now renders Trash, Account, scientific
  object detail, Report detail and the Acceptance Dataset with zero console
  errors. Existing browser tabs and all platform services remain open.

## 2026-09-01 Product maturity Dataset interaction batch (continued)

- Confirmed the retained API/frontend and PostgreSQL/Redis/MinIO services are
  live; `/health/runtime` truthfully reports PostgreSQL, Redis, MinIO,
  Redis-backed workers and configured DeepSeek.
- Re-projected DataFrame source rows with deterministic `objectId`,
  `sampleRef` and `sampleKey` provenance so a readable Dataset row is also
  semantically selectable.
- Verified the authenticated Data Platform tab after refresh: `Si / 1`,
  exact `objectId=obj_dataframe_60c91184df02`, stable sample reference
  `dataset_0001_a0b09e3324e44ca4@2:60c91184df022d34:0`, enabled `选择`, and
  zero browser warnings/errors.
- Kept the scientific table identity column visible and keyboard/mobile
  usable; no scientific values or authority records were mutated.
- Added the batch evidence record at
  `docs/agent2/product_maturity/PRODUCT_MATURITY_BATCH_2026-09-01.md`.
## 2026-09-01 Product maturity — payload failure UX clarification

- Data Platform source-read failures now present two truthful states:
  transient/retryable and confirmed missing payload.
- Confirmed missing states retain exact source/version metadata and explicitly
  prohibit replacement by another Dataset, ScientificObjectVersion or Artifact.
- The interaction keeps a bounded recovery action and avoids presenting a
  storage-contract 404 as an opaque Internal Server Error.

## 2026-09-01 Product maturity — route continuity batch

- Repaired the Dataset workbench's project breadcrumb, return action and
  secondary import action so all preserve the active project context.
- Repaired Project Home import actions to use the project-scoped Dataset
  upload route after project identity is loaded; `/analysis` remains only as
  a compatibility fallback when no project is available.
- Reused `ProductNavigation` client transitions, preserving the existing
  no-full-reload interaction model.

## 2026-09-01 Product maturity — table accessibility normalization

- Scientific table scroll regions keep one stable primary accessible name for
  predictable screen-reader navigation.
- The mobile interaction and fixed semantic sample-identity guidance remains
  available through a per-instance `aria-describedby` target, so repeated
  tables do not share a global DOM id or expose a misleadingly long role name.
- Full frontend regression is green at 108 files / 787 tests.

## 2026-09-01 Product maturity — admin route continuity

- Added `/admin` to the shared authenticated product-route boundary so the
  platform management surface receives the same global shell, session guard,
  transition behavior and scroll ownership as `/account`, `/tasks` and
  `/notifications`.
- Added explicit `返回控制台` actions to the Account Center and Admin Center
  headings, preventing deep account/admin pages from relying on browser Back
  or the landing page brand as their only exit.
- Scientific authority, project membership, account state and lifecycle APIs
  were not changed.

## 2026-09-01 Product maturity — shared UI and account fluency

- Shared shell boundaries now isolate accidental page-wide overflow while
  retaining explicit internal scrolling for scientific tables and viewers.
- Shared primary/secondary actions expose consistent hover, focus and disabled
  states; mobile controls retain the existing 44px touch target.
- Account sessions are bounded to the most recent eight entries by default
  with an explicit “显示全部会话” disclosure, reducing deep-page scroll cost
  without hiding session management.
- The active 3013 frontend was rebuilt from the current production output and
  restarted narrowly; API, PostgreSQL, Redis, MinIO, workers and browser tabs
  remained running.
- The legacy 3000 compatibility alias was also corrected to target the current
  3013 build. A fresh 3000 browser tab now resolves the same account page with
  eight bounded session rows, no Internal Server Error and no console errors.
- Task and notification filter controls now remain a single horizontally
  scrollable row on mobile, preserving clear filter semantics and 44px touch
  targets instead of wrapping into a visually ambiguous second row.
- 2026-09-02 产品成熟度实时科学表面复核：保持 PostgreSQL/Redis/MinIO、API、6 个 worker 与现有浏览器标签页不变，使用同栈认证浏览器完成 16 个项目数据入口、41 个精确 Dataset/Object 详情、10 个已验证 Report、10 个报告引用 Viewer 的真实回归。当前 acceptance 可见路径均无 Internal Server Error、SOURCE_MISSING、不可用 payload 或浏览器 error；轨迹精确版本 `d325a090-d53f-4980-8a5e-c466bf6470eb` / `052d3a8e-8a35-48ac-9e65-b95a86b42c99` 实际渲染 3 帧 canvas，Dataset 精确版本 `8a425466-b697-4c85-9a43-199414a22865` / `be02266a-7d4f-4ebb-9f28-3132855167d0` 实际渲染稳定样本表。新增证据 `docs/agent2/product_maturity/LIVE_SCIENTIFIC_SURFACE_REAUDIT_2026-09-02.md`。同时栈 operations snapshot `--same-stack --fail-on-attention` 为 PASS，idle-in-transaction=0，pool checkedOut=0，队列深度=0；此前截图对应的现行根因不是服务停止，而是过期前端构建/历史测试 payload 缺失，当前 acceptance 路径已闭合。
- 2026-09-02 P14R 结果文档一致性修复：`AGENT2_PHASE14R_RESULTS.md` 顶部状态从历史 `PARTIAL` 明确更新为当前 `COMPLETE`，并注明后续带日期的 PARTIAL 为历史 checkpoint，避免最终 P14R-A/P14R-B 已 PASS 但文档开头仍产生矛盾。未修改科学 authority、实现代码或服务。
- 2026-09-02 历史报告入口 P1 修复：`ScientificReportRoute` 现在在 legacy `job_*` / `run_*` 引用下直接进入只读兼容报告页，不再先探测必然 404 的现代报告接口，避免用户可见的错误噪声。补充回归 `ScientificReportRoute` 23 passed；重建 `.next-prod-maturity-20260902` 并重载 3013（3000 alias 保持指向当前实例）；认证浏览器对 `job_agent2_92fcd73e38034dcfbc7aa63fbcf2a70e` 实测无 ISE/console error，科学结果最终正常加载。详见 `docs/agent2/product_maturity/LIVE_SCIENTIFIC_SURFACE_REAUDIT_2026-09-02.md`。
- 2026-09-02 移动科学表格 P1/P2 可用性修复：保留现有横向滚动与稳定样本身份/选择固定逻辑，恢复 `.workspace-table-mobile-hint` 在移动断点的可见提示，避免用户将被裁切的右侧属性误判为 payload 丢失。`WorkspaceArtifactGallery`、`ScientificWorkspaceShell`、`ScientificReportRoute` 窄回归 53 passed；前端全量 108 files / 789 tests、production build、typecheck、compileall、静态资源与 diff check 均通过。未修改科学 authority、服务配置、数据库记录或浏览器标签页。
- 2026-09-02 筛选控件共享视觉层级修复：报告与回收站的 `product-filter-row` 不再继承全局 teal 主按钮；仅当前筛选使用填充强调，其他筛选使用描边胶囊，移动端保持 44px 触控高度。生产构建重载后浏览器报告页实测样式与页面内容正常，未改变筛选语义或科学数据。
- 2026-09-02 报告科学内容页内预览：现代科学报告的持久化 Figure/Table 不再只有描述牌和外链；新增按需、只读的 Artifact 预览，Figure 使用有限序列的确定性 SVG 投影，Table 使用最多 24 行/8 列的有界表格投影，保留权威 Artifact 外链与失败回退。认证同栈报告 `agent2_report_19a0d0c261c28577101de81532464893` 实测 Figure 2 点、Table 1 行、浏览器 error/warn 为空；相关测试 26 passed，typecheck/build PASS。

## 2026-09-03 Product maturity — exact payload recovery and runtime alignment

- 现有 PostgreSQL、Redis、MinIO、API、frontend 与 workers 均可达；问题不是
  服务整体停止，而是 acceptance scope 的 1 个 ScientificObjectVersion
  payload 与 10 个 MinIO Artifact 精确 key 缺失。
- 通过保留的同栈 MinIO 对象和 active bucket 的同字节副本执行清单驱动恢复；
  每项均按数据库权威 `size_bytes` 与 SHA-256 校验，目标 key readback 再校验。
  PostgreSQL 中的 Object、Version、Job、ToolCall、Artifact、Result、Report
  身份均未改变，也没有 latest/version 替换。
- 当前验收范围核验为 `ScientificObjectVersion 13/13 present`、
  `MinIO Artifact 241/241 present`、missing `0`。证据：
  `docs/agent2/product_maturity/evidence/exact_minio_reference_recovery_2026-09-03.json`
  与
  `docs/agent2/product_maturity/evidence/exact_minio_availability_verification_2026-09-03.json`。
- 新增 provider-aware 精确恢复工具
  `scripts/restore_exact_minio_references.py`；它只恢复已声明 provider、
  已存在权威 key 的 exact bytes，不写入科学数据库。
- 修复 S3 `exists()` 将 AccessDenied/连接错误误判为不存在的问题，并关闭
  `get_bytes()` response body，避免批量读取时连接泄漏；新增回归覆盖。
- Phase 14-R 同栈 Redis 权威为 `127.0.0.1:6379/13`。API 与 6 个 workers
  已受控重启至 DB 13，`phase14r_operations_snapshot.py --same-stack
  --fail-on-attention` 返回 `status=ok`, `workerCount=6`,
  `idleInTransaction=0`, `pool.checkedOut=0`, `totalQueued=0`。
- 受控浏览器标签页、PostgreSQL、Redis、MinIO、前端与临时恢复源服务均保持
  运行。综合 UX 审计记录：
  `docs/agent2/product_maturity/ux-audit-scientific-data-availability-2026-09-03.md`。
## 2026-09-03 — Scientific source-unavailable state refinement

- Exact acceptance-scope source bytes and MinIO Artifact payloads are now
  verified present (`13/13` versions, `241/241` artifacts) after restoring the
  original keys from the retained source store.
- The same-stack runtime is explicitly aligned to PostgreSQL, Redis DB 13,
  MinIO `mdi-artifacts`, and six Redis workers; `/health/runtime` and the
  operations snapshot both report healthy.
- The Viewer fallback now uses researcher-facing “原始科学数据” wording and
  makes “查看来源与属性” the primary escape hatch while retaining retry as a
  secondary action. This changes only UX copy/action priority; exact-version
  and fail-closed semantics remain unchanged.
## 2026-09-03 — Product maturity global audit and mobile Research scroll repair

- Added a current whole-product evidence audit at
  `docs/agent2/product_maturity/ux-audit-global-product-2026-09-03.md`.
- Reconfirmed the browser/API stack is healthy on PostgreSQL/Redis/MinIO; the
  remaining user-visible risk was mobile Research scroll ownership, not a
  stopped service.
- Adjusted mobile Research so the document owns vertical scrolling, the
  conversation history remains bounded and internally scrollable, and the
  composer/primary action cannot be clipped by the desktop fixed-height grid.
- Kept scientific table horizontal scrolling, sticky semantic identity and
  exact provenance unchanged.

## 2026-09-03 — Dataset source recovery and viewer route re-audit

- Restored the exact `si.cif` source (441 bytes, SHA-256
  `4aeaf0107a36ef4bf587da1e52d20ca2739063dd5a548dcb3dac29efc0331198`) and
  normalized metadata for `dataset_0002_cb403e1b78f54d32` from retained MinIO
  `9102` to active MinIO `9000`; no PostgreSQL scientific rows were changed.
- DurableObjectStoreResolver now resolves the Dataset structure from active
  storage. Authenticated desktop/mobile browser checks show the real Structure
  Viewer, with zero source-missing states, console errors, HTTP failures, or
  horizontal overflow.
- Scientific viewer API URL construction now preserves the repository's
  browser proxy contract for `/api/*` FastAPI routes while safely de-duplicating
  only full backend URLs.

## 2026-09-03 — Shared lifecycle and report navigation discoverability

- Added a direct global `回收站` entry beside Tasks/Notifications, while keeping
  the account-menu entry for users who prefer the identity menu. On mobile it
  collapses to a compact labeled control with a tooltip and accessible name.
- Added a mobile-only report chapter overflow cue (`左右滑动查看章节`) without
  creating a second scroll owner or changing report anchors/provenance.
- Verified report navigation and global lifecycle entry at `390×844` with zero
  horizontal overflow; focused ProductShell/ScientificReport tests remain green.

## 2026-09-03 — Shared list progressive disclosure and report action hierarchy

- Tasks/Notifications now expose a bounded initial window plus explicit
  “显示更早…” progressive loading, resetting to 30 items when filters change.
- Scientific Report actions now distinguish the primary “打开来源研究” path
  from return/export actions, with a deliberate mobile two-group layout.
- Admin forbidden state now offers a direct console recovery CTA while preserving
  the account-center path and server-side authorization boundary.
- Focused component tests and typecheck/build remain green; authenticated
  Chromium smoke checks show zero horizontal overflow and no console errors.
- Data 科学属性表补充移动端横向滚动提示，继续保留语义表格与稳定选择行为。
- Dataset 工作台增加数据资产上下文说明与术语折叠，明确导入容器、不可变科学
  版本、Profile、规范化资源及分析结果的职责边界。
- 认证浏览器实测 Data → Research 点击导航的 document request 增量为 `0`，
  保持框架内路由切换与预取，不退化为整页刷新。
- Account 移动端设置目录改为 `top: 56px` 吸顶，长页面滚动期间保持安全区段
  导航可见；不改变账户 API 或会话安全语义。
- Scientific Report Figure 预览改为有界多序列 SVG 线图，保留正负值基线、坐标
  语义、序列边界和只读 Artifact 声明；不触发科学重算。

## 2026-09-03 — Scientific figure legend clarity

- Figure 预览增加序列图例和每条序列的有限点数，特别处理只有少量数据点时
  的可理解性；继续从持久化 Artifact 做只读投影，不创建新的科学执行。
- 认证 Chromium 桌面真实报告预览显示 `All sites / 1 个点`、`Si / 1 个点`，
  SVG 仍为 1 个，页面无横向溢出、console errors 或 HTTP 5xx。

## 2026-09-03 — Global scientific semantic search and recovery

- Global search now matches bounded authoritative Dataset metadata (`sample_id`,
  formula and schema semantics), ScientificObject version metadata, and
  ScientificResult bundle/grounded-interpretation text within the existing
  project authorization boundary.
- Findings remain a projection of ScientificResult rather than a second search
  authority. Result links retain explicit `researchTurnId`; no Job-name parsing
  is used.
- Result search labels prefer the authoritative research question or first
  Result item title, with a short Result ID and schema version as secondary
  provenance metadata.
- Search and saved-search loading failures now expose in-place retry controls
  while preserving query, filters and project scope.
- Same-stack API refresh and authenticated browser search for `mat-2` returned
  14 authorized items and opened an exact ResearchTurn without 5xx, page/console
  errors or horizontal overflow.

## 2026-09-03 — Restored legacy browser aliases

- Kept the existing user tabs open and restored the two legacy frontend aliases
  at `127.0.0.1:3013` and `127.0.0.1:3016` using the current production build
  and API proxy to `8005`.
- Both aliases return HTTP 200; the historical report route opens with report
  title, revision navigation, chapters and source-research entry, with zero
  browser console errors. This distinguishes an unavailable old frontend
  process from a missing scientific payload.

## 2026-09-03 — 回收站空状态出口

- 回收站为空时提供“查看项目 / 返回控制台”明确路径，避免管理页死路。
- 移动端出口采用可换行、均分宽度的操作组，不增加新的导航框架。
- 真实认证浏览器在 390×844 与 1280×720 验证通过；构建后通过重启前端
  刷新旧静态 chunk，保留同栈服务与 Chrome 会话。

## 2026-09-03 — 前端构建刷新后的全路由回归

- 前端重启后对 12 个产品入口、2 个视口共 24 个组合重新验收；
  `24/24 HTTP 200`，页面级横向溢出 `0`，console/page errors 与 HTTP 5xx 均为 `0`。
- PostgreSQL、Redis、MinIO、API、workers 和 Chrome 标签页保持运行。

## 2026-09-03 — Mobile scientific scroll affordances

- 为通用科学表格、Dataset 验证表与报告章节导航补充移动端滚动阴影、稳定
  滚动条颜色和键盘聚焦反馈，强化“还有内容可横向查看”的可发现性。
- 保留完整列、稳定样本/语义身份、报告锚点和科学 authority；未引入新的滚动
  容器或科学计算路径。
- 定向 `68 passed`、全前端 `110 files / 796 tests passed`、typecheck/build
  均通过；认证 Chromium `390×844` Data 表横向内容 `759px`、报告章节
  横向内容 `573px`，页面级横向溢出均为 `0`，console errors=0、5xx=0。

## 2026-09-04 — Dataset authority boundary clarity

- Dataset 详情页增加可见的“从来源到结果：每一层负责什么”说明，明确 Dataset
  是导入范围、Profile 是语义档案、ScientificObject/Version 是科学身份与不可变
  状态、ScientificResult 是分析事实；没有引入第二科学权威或改变数据路由。
- 详情页将“表格行数/可用能力/结果”等容易误读的标签改为“记录数/可用分析/
  分析结果”，并将来源区分为来源文件、可查看的科学资源和语义档案。
- 聚焦 `DatasetWorkbenchPage` 测试 `1 passed`，前端 typecheck PASS，
  `git diff --check` PASS；尚未提交或推送，运行中的 API、前端、数据库、Redis、
  MinIO、workers 与浏览器标签页保持不变。

## 2026-09-04 — Dataset/Research recovery and exact-version navigation

- Dataset/Research 第二批交互审计发现两个可复现的恢复性缺口：Console 快速查看
  和项目数据读取失败时缺少原地重试；已补充“重新加载数据/重新加载项目数据”，
  保留当前项目与页面上下文，不改变 ScientificObject、Version 或 Result authority。
- Data 路由只带科研对象而未带不可变版本时，原来会落回 Dataset 面板；现改为
  明确的“需要指定科研对象版本”安全态，避免任何静默最新版本替换，并提供返回项目
  数据入口。
- 验证：`ProductPages.test.tsx` `43 passed`，前端 typecheck PASS，
  `git diff --check` PASS；未提交或推送，API、前端、PostgreSQL、Redis、MinIO、
  workers 与浏览器标签页保持运行。

## 2026-09-03 — Product maturity UX batch

- Rebuilt the current production frontend and kept API, PostgreSQL, Redis, MinIO,
  workers and retained browser tabs running.
- Added bounded Task/Notification search and stable sorting with no-match recovery.
- Added mobile report chapter navigation and clarified Dataset/Profile/
  ScientificObject/Version/ScientificResult boundaries.
- Expanded authorized search to Dataset/Object/Result semantic metadata and
  grounded finding content with human-readable Result titles.
- Verification: focused `44 passed`; full frontend `110 files / 803 tests
  passed`; typecheck/build/diff check PASS; same-stack runtime healthy.

- Project Home now exposes progressive “显示更多” controls for long dataset,
  analysis-history and recent-activity lists, and a bounded reload action for
  project-history errors while preserving exact routes.
- Authenticated Chromium route sweep covered 12 core routes across 3 frontend
  instances and 2 viewports (72/72 HTTP 200, no page/console errors, 5xx or
  global overflow). Current Data/Version/Viewer projections for 13 objects
  also passed 26/26 loads with READY payloads.

## 2026-09-03 — Account/Admin control-safety batch

- Account Center now preserves the loaded account surface when session inventory
  fails and offers in-place account/session retries.
- Platform Admin now confirms role/status mutations and project-member role/removal
  changes in an accessible inline confirmation region, explains the permission/
  provenance consequence, supports bounded “显示更多” pagination for users and
  projects, and exposes recovery when the initial admin read fails.
- Invitation token copy reports success/fallback instead of silently failing.
- No scientific identity, version, result, provenance, or authorization authority
  changed. Focused frontend tests: 13 passed; typecheck and diff check passed.
- Rebuilt production frontend after this batch; full frontend regression is now
  `110 files / 810 tests passed`, with authenticated core route matrix `24/24`
  HTTP 200 across desktop/mobile and no page/console errors, 5xx or overflow.

## 2026-09-04 — Scientific table and unavailable-view recovery clarity

- Dataset Explorer summary/sample tables now expose a mobile-only horizontal
  scrolling cue and keyboard-focusable semantic regions while retaining typed
  columns and stable sample identity. The cue is descriptive and does not alter
  row ordering or selection authority.
- Scientific Report keeps exact Report, snapshot, ResearchTurn, Result and
  object/version identities in a collapsed technical disclosure after the
  readable scientific content, so provenance remains inspectable without
  overwhelming the primary report hierarchy.
- Workspace unavailable/unsupported Artifact states now use researcher-facing
  Chinese copy, distinguish missing exact payload from unsupported renderer,
  preserve bounded diagnostic codes, and explicitly state that no alternate
  version or executable component is used.
- Focused frontend tests: 35 passed; typecheck and diff check passed. No
  scientific authority, storage, routing, or service configuration changed.

## Product maturity — 当前生产报告/表格复核（2026-09-03）

- 重载当前生产构建至 `3000`、`3013`、`3016` 后，认证报告详情页恢复稳定：
  版本历史、章节导航、持久化 Figure/Table 预览和精确对象版本均可读，浏览器
  console error/warn 为 `0`，不再出现旧 chunk/application error。
- `390x844` 数据工作台保留稳定 sample identity、typed columns 与显式横向滚动
  提示；页面无全局横向溢出。报告页将技术身份放在折叠 disclosure 后，主层级先
  呈现科学内容，符合研究工作台的信息密度与渐进披露原则。
- 当前全前端 `110 files / 813 tests passed`，后端关键回归 `56 passed /
  1 historical compatibility skip`，build/typecheck/compileall/lock/diff 均通过。

## Product maturity — 导航/研究控制/科学表面批量修复（2026-09-03）

- 登录后品牌入口与显式“控制台”入口统一回 `/console`；高频顶层
  `/projects`、`/console`、`/account`、`/admin` 增加一致的 loading frame，
  切换等待服务端数据时保留工作区层级和即时反馈。
- Research Continue 子 Turn 显式绑定父 Turn 的精确 Result snapshot；
  PLAN_READY 自动 dispatch 与 Stop 竞态以持久化终态为准，避免伪执行失败。
- Electronic/DOS、Phonon Band/DOS、Volumetric 大数组统计改为安全迭代，
  空数据显示可解释状态，科学表格补充列语义，避免合法 Artifact 在浏览器中
  因调用栈溢出而空白。
- 验证：相关前端聚焦 `99 passed`，`npm run typecheck`、`npm run build`、
  `compileall`、`uv lock --check`、`git diff --check` 均通过；同栈
  PostgreSQL/Redis/MinIO healthy，6 workers idle，queue depth 0，
  idle-in-transaction 0。
- 当前构建在保留既有端口和标签页的 `3018` 前端副本上复核：桌面核心路由
  `11/11`、移动 `11/11` 均无页面/console 错误和全局溢出；`390x844` 项目
  导航中的“控制台”标签保持单行可读。

## 2026-09-04 数据层级与导航感知性能批次

- Data Navigator 增加固定的“来源数据与科学身份”阅读提示，明确区分
  `Dataset`（导入范围、文件、记录与查询）和 `Scientific Object / Version`
  （解析后的科学身份与不可变精确状态），避免把 Dataset 当作科学版本入口。
- 项目历史新增已解析快照读取入口；项目概览、数据和研究路由优先使用
  ProductShell 预热后的快照，减少客户端导航后的重复等待与重复历史请求。
  Console 在展示首个活动项目后短延迟预热同一历史 ledger，并对“继续研究”
  主入口显式启用框架预取。
- 定向前端回归 `ProductPages + ProjectHome + ProductShell = 69 passed`；
  `npm run typecheck`、生产构建、`git diff --check` 通过。
- 当前构建独立运行在 `127.0.0.1:3020`（API `8005`），同栈 `/health/runtime`
  仍为 PostgreSQL / Redis / MinIO / Redis worker / DeepSeek `ok`；认证浏览器
  数据页桌面显示层级提示，移动端 `scrollWidth === clientWidth === 375`。
- 旧历史缺失 payload 继续保留 fail-closed 说明；本批没有用其他版本替代、
  没有改写 ScientificObject/Version/Result authority，也没有停止服务或关闭既有标签页。

## 2026-09-04 Research 上下文审计可见性批次

- 上下文清单此前在默认展示中只显示前 `8` 项，但摘要会报告完整纳入数量；
  对长上下文而言，这会让研究者无法从产品界面检查其余已授权上下文项。
- 现在仍默认采用有界八项预览，同时提供可访问的“查看全部上下文”切换，
  允许展开完整 `included_items` 清单；切换只改变通信层显示，不改变
  ContextManifest、科学来源、Result 或 Provider 负载。
- 清单切换在 ResearchTurn 变化时自动收起，`aria-expanded` / `aria-controls`
  与稳定列表 ID 配套，窄屏继续沿用有界布局。
- 验证：ResearchPages `69 passed`，`npm run typecheck` PASS，`git diff --check`
  PASS。没有新增 Job、ToolCall、Artifact 或 ScientificResult。

### 同栈科学对象逐页复核（2026-09-04）

- 使用当前生产构建 `127.0.0.1:3020` 重新打开活动项目的 `13/13` 个精确
  ScientificObject/Version 入口。Electronic DOS、Phonon Band/DOS、Dataset、
  ML 表格、Electronic Band、Structure、Trajectory 与 Diffusion 均在 hydration
  后到达声明的 renderer 或 bounded fallback。
- 未出现 `Internal Server Error`、`Application error`、`SOURCE_MISSING` 或
  alert；桌面 document/client width 均为 `1265`，全局 overflow 为 `0 px`。
  Structure/Trajectory 路径挂载真实 canvas；Structure 显示 `Si` 位点、晶胞和
  精确版本信息。
- 该检查仅验证读路径，不创建 Job/Result，也不改变历史 `SOURCE_MISSING`
  的 fail-closed 语义。

### Report / Artifact 展示批次与完整回归（2026-09-04）

- Report 阅读器为每条主要发现增加折叠式“查看科学依据”，只读展示
  ScientificResult snapshot、精确对象/版本、fact/evidence/finding refs；
  技术身份继续置于渐进披露层，避免污染正文。
- Artifact Gallery 对 `STATIC_METADATA` 与 `DOWNLOAD_ONLY` 契约提供明确的
  元数据/安全下载状态；`plotly_html`、图片和其他不可执行资源不会被猜测成
  可执行组件或伪装为科学图像。
- 当前生产构建 `127.0.0.1:3021` 同栈健康；认证报告桌面宽度
  `1265/1265`、移动宽度 `375/375`，报告主要发现依据入口可见，页面无
  alert 或全局 overflow。
- 回归：完整前端 `110 files / 823 tests passed`；完整后端
  `1983 passed / 84 skipped`；typecheck、production build、compileall、
  `uv lock --check`、`git diff --check` 均通过。
- Phase 14-R 仍保持 `PARTIAL`，因为 capability-wide real-user、retention/
  export/operations maturity 和 exact-SHA release gates 尚未全部证实；历史
  缺失 payload 仍 fail-closed。

### 2026-09-04 Research 上下文恢复性批次（第二批）

- ResearchTurn 的 ContextManifest 读取失败此前会静默清空上下文区域，长会话
  中研究者无法判断是“本次没有清单”还是“临时读取失败”。
- 现在记录有界的读取状态；临时失败会在研究时间线显示“本次研究的上下文
  清单暂时无法读取”和“重新读取上下文”原地恢复动作。重试只重新读取同一
  已持久化 ContextManifest，不会改变上下文选择、Result、ScientificResult
  或执行状态。
- ResearchPages 定向回归 `70 passed`；未停止 API、workers、PostgreSQL、
  Redis、MinIO 或浏览器标签页，未提交/推送。

### 2026-09-04 生命周期恢复性批次（第二批）

- 回收站库存读取失败此前只显示错误，没有原地恢复入口；现在提供
  “重新加载回收站”，重试只重新读取服务端回收站投影，不改变任何生命周期、
  科学版本或历史 provenance。
- TrashCenter 定向回归与 ResearchPages 合计 `75 passed`；未停止现有服务、
  workers 或浏览器标签页，未提交/推送。

### 2026-09-04 Research 主操作停止控制批次

- Research 运行期间，底部输入区的主操作此前会退化为不可点击的处理中按钮；
  停止入口只存在于上方过程卡片，长时间线和移动端用户不容易发现。
- 现在在已有精确 `ResearchTurn` 且处于 `planning/running` 时，输入区主操作
  明确切换为“停止研究”；它复用现有服务端持久化取消、部分 Artifact 保留和
  终态竞态对账逻辑，不创建第二套取消状态。
- 没有可取消 Turn 身份的旧式/过渡状态仍保持只读处理中，避免把无法持久化的
  前端动作伪装成取消成功。
- 验证：ResearchPages `71 passed`，`npm run typecheck` PASS。未停止 API、
  workers、PostgreSQL、Redis、MinIO 或浏览器标签页，未提交/推送。

### 2026-09-04 R7/R8 研究任务可查找身份批次

- 范围化审计确认 Global Search、已保存检索、Task Center、Notification Center
  与 online/visibility 恢复已经复用持久化授权投影，不需要第二套搜索索引或任务
  authority；审计记录位于
  `docs/agent2/phase14r/ux-audit-r7-r8-search-task-recovery-2026-09-04.md`。
- 真实缺口是 ResearchTurn-backed 任务仍显示通用“可恢复研究/研究会话更新”，
  并且本地查找不包含研究问题。现有 Job → ResearchTurn → user_message 外键现已
  在同一 bounded SQL task-feed projection 中增加 `researchQuestion` 显示元数据；
  它只用于标题与本地查找，不改变 Turn/Job/Result 权威。
- Task/Notification 行同时展示持久化 `updatedAt || createdAt` 的语义化
  `<time>`，让研究者能核对恢复后的任务是否是刚更新的运行；精确 Turn 路由、
  legacy read-only、停止/重试与断网恢复语义保持不变。
- 验证：Workspace/task-feed backend `15 passed`；Task/Notification/task-data
  frontend `16 passed`；typecheck、touched Ruff、diff check PASS。性能回归仍证明
  1 个与 5 个 Job 均为固定 `2` 次查询。

### 2026-09-04 Neat-freak knowledge/workspace closeout

- 在用户确认后，仅删除 12 个已核对旧项目日志，总计 `656,867` bytes；当前
  API、workers、PostgreSQL、Redis、MinIO、前端和浏览器标签页均保留。
- 删除后检查：API `8005`、前端 `3023`、PostgreSQL `5432/55434`、Redis
  `6379`、MinIO `9000` 仍在监听；同栈健康保持 PostgreSQL/Redis/MinIO/
  worker healthy。
- 已同步 `AGENT2_PHASE14R_RESULTS.md`、`persistent/TASK_BOARD.md`、`results.md`；
  未提交、未推送，Phase 14-R 仍为 `PARTIAL`。
- C 盘约剩 `80 MB`，只读报告位于
  `E:\storage-analysis-phase14r-20260904\storage-report.html`；未触碰
  Chrome/Codex/runtime/science data，其他临时目录需另行确认。

### 2026-09-05 Continuous optimization — Report Figure x-coordinate fidelity

- 建立 `120` 项有证据、可独立验证的持续优化池；首项选择科学呈现中的
  非均匀 x 坐标失真问题。
- Report 的持久化 Figure 预览现在按权威 numeric x-domain 映射 SVG，
  缺失/分类 x 才回退到序列位置；不改变 Artifact、ScientificResult 或单位。
- 非均匀 `[0, 0.1, 10]` 回归、聚焦前端 `7 passed`、typecheck 和 diff
  check 通过；同栈报告 `agent2_report_e54681009a0e49abe371247d9053ce61`
  页内预览真实加载 `92` 个点且 browser error 为 `0`。
- 下一项为 CO-002：消除 Report table preview 的视觉行号身份回退。

### 2026-09-05 Continuous optimization — Report Table stable row identity

- Report table preview 不再把视觉数组下标作为默认 React identity；唯一的
  `sample_id` 等语义字段优先，缺失时使用属性顺序无关的规范化行内容。
- 完全重复且科学上不可区分的行仅使用重复序号消歧；排序/刷新不会让不同内容
  的科学行发生 DOM identity 漂移。
- focused frontend `9 passed`、typecheck、diff check PASS。
- 下一项为 CO-003：Materials Explorer 通用 DataTable 的稳定行身份。

### 2026-09-05 Continuous optimization — Materials Explorer stable row identity

- composition、structure、quality、comparison 的通用表格从 `string[][]`
  升级为带上游语义 key 的 bounded rows，视觉数组下标不再承担科学身份。
- 重排和重复上游身份回归均通过；focused frontend `11 passed`、
  typecheck、diff check PASS。
- 下一项为 CO-005：Research polling 的取消和 stale-response 防护。

### 2026-09-05 Continuous optimization — Research polling lifecycle

- ResearchTurn progress 与 legacy Job polling API 均支持 `AbortSignal`；
  Turn/Job 切换或卸载会终止在途请求、清除 retry timer，并阻止 online 事件
  生成重叠 polling。
- legacy 终态 Interpretation/Evidence 回调增加 exact active-lineage guard，
  不会在切换研究后写入当前页面。
- ResearchPages focused `73 passed`、typecheck、diff check PASS。
- 下一项为 CO-004：同时存在 run/turn 身份时只允许 authoritative Turn
  驱动执行状态。

### 2026-09-05 Continuous optimization — one Research execution authority

- `run + turn` 历史链接继续保留 Job provenance，但 explicit ResearchTurn
  成为唯一 execution-state authority；不再 hydrate/poll legacy Job。
- run-only legacy 历史路径保持兼容；新增权威 Turn 回归后 Research
  `74 passed`、typecheck、diff check PASS。
- 下一项为 CO-036：检查并修复跨产品入口绕过共享 SPA 导航的问题。

### 2026-09-05 Continuous optimization — SPA navigation acceptance (CO-036)

- 通过独立 Chrome 认证浏览器验收确认 Data → Research → Report → 来源
  Research/历史 → Viewer 的六条内部转换均为同文档客户端路由：每条
  `documentRequests=0`，`performance.timeOrigin` 与运行时探针保持，
  暖态耗时 `37–139 ms`，console errors 与 server 5xx 均为 `0`。
- 新增 `apps/web/test/product-navigation-spa-acceptance.mjs` 及 npm
  入口，后续若出现 document reload、运行时状态丢失、console error 或
  5xx 会直接失败。
- 未修改科学 authority 或路由架构；CO-006（历史 Job → ResearchTurn
  权威 resolver）进入下一轮。

### 2026-09-05 Continuous optimization — historical Turn scope (CO-006)

- 历史兼容投影的 `research_session_runs` → `research_turns` 外连接现在同时
  约束 `job_id` 与请求项目；异常跨项目关系不会泄漏 `researchTurnId`，
  仅保留安全的 legacy run projection。
- 新增非标准 Job ID 与跨项目 Turn 回归；`test_project_history_research_context`
  `5 passed`、`test_project_access` `32 passed`、Ruff/diff PASS。
- 下一项为 CO-007：ContextManifest 预算与溢出压力验证。

### 2026-09-05 Continuous optimization — legacy ContextManifest budget (CO-007)

- 发现历史 ContextSnapshot 的兼容 Manifest 投影未应用 operation-specific
  budget，可能让回放上下文超过契约上限且错误标记为未压缩。
- `routers/agent2.py` 现在按科学身份优先确定性裁剪；非关键内容记录
  `excluded_items`，关键科学上下文超限直接 fail-closed。
- `tests/test_phase14r_context_manifest.py` `13 passed`；Ruff 与 diff check
  通过。下一项为 CO-008：上下文 pin/unpin/use/compare 持久化。

### 2026-09-05 Continuous optimization — context pin reload durability (CO-008)

- 增加真实 `ScientificResultSnapshot` 的 repository 生命周期回归：固定
  精确 Result、关闭事务、重新读取、取消固定、再次读取。
- memory focused `10 passed`，Ruff 与 diff check 通过；确认上下文控制
  只改变 session memory，不改变科学 Result authority。
- 下一项为 CO-009：归一化 malformed/missing context-memory reference 的
  用户可见错误。

### 2026-09-05 Continuous optimization — missing Result error normalization (CO-121)

- Agent2 `_http_error` 现在将 `ScientificResultSnapshotNotFound` 映射为稳定
  404，而不是泛化 500；API focused `27 passed`，Ruff/diff check 通过。
- 该错误路径不改变 ScientificResult 或 session memory authority。
- 下一项回到 backlog 的 CO-009：network/API/worker interruption recovery
  qualification。

### 2026-09-05 Continuous optimization — evidence provenance UI (CO-010)

- Research 依据条目现在显示字段定位、Artifact ID、ToolCall ID 与 SHA-256，
  并保留现有“在结果中查看”入口。
- ResearchPages focused `75 passed`，frontend typecheck 与 diff check 通过；
  未引入新的 provenance authority 或暴露运行时秘密。
- 下一项仍为 CO-009：network/API/worker interruption recovery qualification。

### 2026-09-05 Continuous optimization — recovery partition regression (CO-009)

- 为 stale recovery 增加数据库级分流回归：真实 product Turn 进入
  recovery candidates，资格项目保留在单独列表，不自动重发。
- `test_phase14r_recovery` `5 passed`，Ruff/diff check 通过；下一项为
  CO-011：XRD 报告科学讨论质量评估。

### 2026-09-05 Continuous optimization — XRD report quality guard (CO-011)

- 新增 XRD 报告回归，验证 discussion、conclusion 均绑定
  `xrd.matched_peak_count`，限制存在且 ReportGroundingValidator 通过。
- Reports focused `35 passed, 4 skipped`（既有 live-provider 条件 skip）；
  Ruff/diff check 通过。下一项为 CO-012：Registry/Pack/Viewer 能力覆盖矩阵。

### 2026-09-05 Continuous optimization — Registry/Pack surface drift guard (CO-012)

- 审计发现 live registry 当前有 `17` 个 ACTIVE capability，文档矩阵也有
  `17` 行，但 `ml.regression_evaluation` 的 Pack 标注错误：文档写作
  `core.data`，实际 `build_phase11_packs` 依据 `domain=ml` 放入
  `core.other`。
- 新增 `test_phase14r_surface_coverage.py`，从 live Registry 与 trusted
  Packs 自动派生 capability、Pack、ToolBinding、Result projector，并与
  `SCIENTIFIC_SURFACE_COVERAGE_MATRIX.md` 逐项校验；同时要求覆盖单元非空、
  状态值受控、projector 已注册。
- focused `1 passed`；Ruff 与 `git diff --check` 通过。下一项为 CO-013：
  扩展各 capability family 的历史/归档 Presentation 证据。

### 2026-09-05 Continuous optimization — historical Viewer family guard (CO-013)

- 为当前已注册的 `10` 个 ScientificObject-backed Viewer 类型增加参数化
  历史/归档回归：同一对象创建 v1/v2、切换 current 到 v2、归档、读取精确
  v1 Viewer、恢复，并校验版本计数与 current version 未漂移。
- `pytest tests/test_agent2_phase9_viewers.py -q` 为 `18 passed`；Ruff 与
  `git diff --check` 通过。
- `analysis.rdf` 与 `reciprocal.brillouin_zone` 虽有 Viewer descriptor，但
  当前不在 ScientificObject registry；已记录为新发现 CO-122，未将其伪装为
  已完成对象级历史覆盖。下一项为 CO-014：payload 临时/永久不可用恢复 UX。

### 2026-09-05 Continuous optimization — typed payload recovery states (CO-014)

- Viewer fallback 之前把 `SOURCE_MISSING`、`METADATA_ONLY` 与
  `INVALIDATED` 混成同一“来源不可用 + 重试”状态，导致超限预览和失效历史
  版本出现无效动作。
- 新增 `viewerPayloadRecovery` 状态映射：只有 `SOURCE_MISSING` 保留重新读取；
  `METADATA_ONLY` 明确交互预览上限，`INVALIDATED` 明确历史失效；三者都保留
  精确“查看来源与属性”入口。
- ScientificObjectViewer focused `3 passed`，frontend typecheck 与 diff
  check 通过。下一项为 CO-015：可信 Figure Artifact 打开/下载路径。
## 2026-09-04 — Product maturity recovery-control verification

- Research ContextManifest read failures now keep the exact persisted context
  identity visible and provide an in-place retry instead of silently removing
  the context disclosure.
- Trash Center inventory failures now provide an in-place retry without
  changing lifecycle or provenance.
- Focused frontend regression: Research `70` + Trash `5` = `75 passed`;
  TypeScript typecheck passed.
- Same-stack runtime and browser instances remain running. Current active
  project exact scientific object routes remain `13/13` readable; historical
  missing bytes continue to be represented as professional fail-closed states
  rather than fabricated replacement payloads.

## 2026-09-05 — Continuous optimization CO-015

Research 与 Report 的 Figure/Table 现在提供受信 Artifact 的打开与下载入口。
新增 `ArtifactDownloadLink` 仅接受项目授权的 planner Artifact 内容路径，
复用服务端大小、哈希和媒体类型校验；原生下载不触发 Job、ToolCall、Artifact
或 ScientificResult 创建。Focused `32 passed`，typecheck 与 diff check 通过。

## 2026-09-05 — Continuous optimization CO-016

授权 Viewer API 的 persisted zero-recompute 回归已扩展到全部 `11` 个已注册
ScientificObject-backed family。每类都验证 Viewer 返回、执行/结果相关表计数
不变以及跨项目 `403` fail-closed；`test_agent2_phase9_viewers.py` 为 `28 passed`。

## 2026-09-05 — Continuous optimization CO-122

`analysis.rdf` 与 `reciprocal.brillouin_zone` 已从 ScientificObject Viewer
registry 明确移入 `RESULT_ONLY_VIEWER_TYPES`。它们继续由 Result/Artifact
renderer 支持，但不再伪装成可版本化、可归档的 ScientificObject；对象与
result-only 集合互斥，focused registry/viewer tests `38 passed`。

## 2026-09-05 — Continuous optimization CO-034

Presentation block runtime now uses an explicit semantic allowlist. Unknown
types and executable-looking labels fail closed and are reported as a bounded
rejected-block status; no unknown component, HTML or script is rendered.
Focused presentation tests `23 passed`, typecheck PASS.

## 2026-09-05 — Continuous optimization CO-038

新增 `phase14r_start_stack.ps1` 作为同栈启动与 readiness 门禁：只启动缺失的
API、worker、frontend，不停止现有服务；等待 PostgreSQL/Redis/MinIO/API/
frontend 后再检查真实 `/health/runtime`。`-CheckOnly` 实测 PostgreSQL、
Redis、MinIO、Redis worker 与 DeepSeek provider 均正常。

## 2026-09-05 — Continuous optimization CO-017

生命周期留存策略已统一到后端 `mdi_api.lifecycle_policy`：自动清理明确禁用，
受引用 scientific provenance 永久保护，手动物理删除必须先由服务器确认
零依赖。Project/Dataset 依赖预览、物理删除与回收站检查共用同一判定逻辑；
不会新增科学 authority，也不会自动删除用户数据。

## 2026-09-05 — Continuous optimization CO-018

统一生命周期合同现在区分两类实体：Project/Dataset 只允许服务器确认
零依赖后的手动 purge；Research Session、ScientificObject、Scientific Report
明确标记 `NOT_SUPPORTED_FOR_ENTITY`。这消除了客户端把“暂无依赖”误解成
“所有历史/科学实体均可永久删除”的风险。

## 2026-09-05 — Continuous optimization CO-019

Research Session 现在提供受项目权限保护的 dependency-impact 只读端点，
按真实 `session_id/research_session_id` 关系统计消息、上下文、Turns、
历史结果与报告绑定，并明确 `canDelete = false`。生命周期实体的依赖
预览不再缺少服务器权威边界。

## 2026-09-05 — Continuous optimization CO-020

账户停用响应现在明确返回 `provenanceRetained = true` 与受保护留存策略；
项目物理删除仍只允许服务器确认零依赖的空项目。账户工作区访问与科学
provenance 保留边界已结构化表达，停用不会删除结果、版本或审计记录。

## 2026-09-05 — Continuous optimization CO-021

Job-event 并发回归已扩展到四个独立 SQLAlchemy repository bundle 和真实
PostgreSQL 多 writer；测试夹具改用每次调用唯一 ID，避免旧 Job 外键导致
跨运行清理冲突。生产 advisory lock 未改动；live `concurrent_seq` 测试
`2 passed`。

## 2026-09-05 — Continuous optimization CO-022

ToolCall persistence now converges after a losing PostgreSQL uniqueness race:
the committed idempotent row is reloaded, while conflicting bindings and
unrelated integrity failures remain fail-closed. Four independent repository
bundles with 12 concurrent writers produced one row; live focused campaign
`3 passed`.

## 2026-09-05 — Continuous optimization CO-123

Artifact persistence now converges after a losing PostgreSQL uniqueness race by
reloading the committed job/storage/checksum row. Four independent repository
bundles with 48 duplicate deliveries produced exactly one Artifact; live
focused campaign `4 passed`.

## 2026-09-05 — Continuous optimization CO-124

Operations snapshots now include a bounded, read-only authority consistency
projection for orphan ToolCall/Artifact/Result/Report references and broken
ScientificObject current-version pointers. Same-stack PostgreSQL qualification
reported `issueCount=0`, `readOnly=true`.

## 2026-09-05 — Continuous optimization CO-023

Added a real PostgreSQL pool pressure regression (8 concurrent workers × 40
transactions). The process-scoped engine is reused, checked-out connections
return to zero, and `idle in transaction` remains zero; live test `2 passed`.

## 2026-09-05 — Continuous optimization CO-024

The authority consistency scanner now has a deterministic seeded-orphan test:
one missing-Job ToolCall produces exactly `ORPHAN_TOOL_CALL_JOB`, and row counts
remain unchanged before/after scanning. Focused tests `2 passed`.

## 2026-09-05 — Continuous optimization CO-025

MinIO live qualification now verifies a server-side backup copy, exact
SHA-256/size fidelity, typed missing-source behavior, and successful restore
from the backup key; focused tests `2 passed`.

## 2026-09-05 — Continuous optimization CO-026

Stale Research recovery now treats Redis/RQ outage as a bounded
`QUEUE_UNAVAILABLE` attention outcome instead of aborting the recovery scan.
The exact durable Turn/Job state is left unchanged and can be republished
through the same identity after the queue recovers. Queue adapters are
injectable for outage/reconnect qualification; production continues to use
the settings-backed Redis queues. Recovery tests pass with no scientific
recomputation or authority mutation.

## 2026-09-05 — Continuous optimization CO-027

DeepSeek transport now absorbs one bounded transient 429/5xx/network/timeout
failure using a deterministic 250 ms backoff. Authentication, configuration
and invalid-response errors remain fail-fast. Every attempt is represented in
the existing redacted call audit, and the full provider regression reports
`67 passed`.

## 2026-09-05 — Continuous optimization CO-028

Direct Dataset uploads now enforce the same shared file-count, per-file byte
and total byte caps as upload sessions. Filesystem paths are size-preflighted
before the raw dataset directory is created, so oversized direct imports fail
with typed errors without leaving partial scientific bytes. Phase 2 product,
typed import and durable upload regressions remain green.

## 2026-09-05 — Continuous optimization CO-125

Secured Planner interpretation evidence now carries a bounded persisted
`projectId` and compares it with the authorized Job project. Cross-project
interpretation/snapshot relations fail closed with the same typed 404 as a
missing resource; same-project evidence remains readable. Deterministic
authorization, Planner read API and interpretation persistence regressions:
`26 passed`.

## 2026-09-05 — Continuous optimization CO-126

Agent2 Research read/create/dispatch fetches now emit the shared
`mdi:session-expired` event on 401 so ProductShell can return the user to
login without misclassifying auth loss as scientific failure. Frontend
regression: `7 passed`; typecheck PASS.
## Continuous optimization — Improvement #37 / CO-127 (2026-09-05)

- 状态：已完成并验证；持续优化总任务继续处理中。
- 问题：项目 provenance manifest 服务端按读取权限授权，但 Projects 操作菜单
  将导出入口错误地放在写权限分支中，共享 viewer 无法发现安全的只读导出。
- 修改：导出动作移入读取权限动作集合；归档、回收站、固定和项目信息编辑
  仍保持写权限门禁；新增 viewer 导出回归。
- 验证：`ProductPages.test.tsx` `46 passed`；viewer 调用授权 manifest API
  并触发下载，写操作入口仍不可见。
- 收益：只读项目成员可获取有界、非可执行 provenance 清单，不扩大生命周期
  或元数据修改权限。
## Continuous optimization — Improvement #38 / CO-128 (2026-09-05)

- 状态：已完成并验证；持续优化总任务继续处理中。
- 问题：已认证的旧 `/analysis-requests` 兼容接口忽略请求中的
  `projectId/project_id`，跨项目调用仍会收到无条件 accepted。
- 修改：当请求提供项目作用域时，先使用现有 `require_project_access(read)`
  校验；无项目的旧非执行调用保持兼容。
- 验证：`tests/test_project_access.py -k
  'legacy_analysis_request_scope or project_export_manifest'` `2 passed`；
  owner/viewer 通过，stranger 403，未创建科学执行记录。
- 收益：兼容接口不再绕过项目隔离，同时不破坏旧客户端。
## Continuous optimization — Improvement #39 / CO-129 (2026-09-05)

- 状态：已完成并验证；持续优化总任务继续处理中。
- 问题：直接文件上传的缺失路径会被 `_api_call` 原样写入 HTTP 400 detail，
  可能泄露用户名、工作区结构或敏感文件名。
- 修改：为 `FileNotFoundError` 增加独立类型化响应
  `UPLOAD_SOURCE_NOT_FOUND`，不再返回绝对路径；其他 `ValueError` 配额和
  校验错误保持原契约。
- 验证：Phase 2 子集 `2 passed`；响应不包含私有路径，上传大小预检仍通过。
- 收益：上传失败仍可理解和重试，同时消除了本地文件系统信息泄露。

## Continuous optimization — Improvement #40 / CO-091 (2026-09-05)

- 状态：已完成并验证；持续优化任务继续处理中。
- 科学 Viewer shell 为每个实例生成唯一标题 ID，并将外层 `article`
  通过 `aria-labelledby` 绑定到可见 `h2`；这只改进可访问性，不改变
  ScientificResult、Artifact 或 Viewer 数据权限。
- 验证：`ScientificViewerShell.test.tsx` `2 passed`；frontend typecheck
  通过；触及文件 diff check 通过。

## Continuous optimization — Improvement #41 / CO-130 (2026-09-05)

- 状态：已完成并验证；持续优化任务继续处理中。
- Artifact 下载 secured wrapper 增加跨项目测试：陌生用户在存储读取前
  收到 403，授权所有者仍可读取；未改变 Artifact 或项目授权模型。
- 验证：`tests/test_project_access.py -k
  artifact_download_denies_foreign_project` `1 passed`。

## Continuous optimization — Improvement #42 / CO-076 (2026-09-05)

- 状态：已完成并验证；持续优化任务继续处理中。
- Viewer 科学元数据维持前 16 项紧凑摘要；超过上限时显示准确剩余数量，
  并通过原生 `<details>` 展开全部追加字段，避免把“未显示”误导成
  “不存在”。
- 验证：`ScientificViewerShell` focused tests `3 passed`，typecheck 通过。

## Continuous optimization — Improvement #43 / CO-084 (2026-09-05)

- 状态：已完成并验证；持续优化任务继续处理中。
- Scientific Presentation Finding 卡片在存在匹配 Evidence reference 时提供
  直接 `查看证据链` 入口，以稳定 evidence id 定位现有 inspector；不复制
  ScientificResult，也不触发科学重算。
- 验证：focused presentation tests `7 passed`；typecheck 通过。

## Continuous optimization — Improvement #44 / CO-092 (2026-09-05)

- 状态：已完成并验证；持续优化任务继续处理中。
- Evidence inspector 增加 `aria-controls`、稳定 id 和焦点管理：打开时
  聚焦证据 region，关闭时返回触发按钮；不引入新的科学数据读取路径。
- 验证：ScientificPresentation focused tests `7 passed`，typecheck 通过。

## Continuous optimization — Improvement #45 / CO-072 (2026-09-05)

- 通用科学绘图增加容器级 `ResizeObserver`，并在卸载时断开；
  保留窗口 resize 兼容路径。
- focused tests `9 passed`；typecheck 通过。
- 目的：分栏/移动布局变化时保持图表可读、尺寸正确，不触发科学重算。

## Continuous optimization — Improvement #46 / CO-112 (2026-09-05)

- 回收站永久删除确认要求稳定 `类型:ID` 令牌，避免同名实体歧义；
  保留服务端依赖与留存保护。
- duplicate-title 回归 `6 passed`；typecheck 通过。

## Continuous optimization — Improvement #48 / CO-087 (2026-09-05)

- Figure 预览投影持久化 Artifact 的权威坐标轴范围、刻度、标题/单位；
  缺失时显式显示未提供，避免视觉层推断科学单位。
- focused tests `10 passed`；typecheck 通过。

## Continuous optimization — Improvement #49 / CO-089 (2026-09-05)

- 报告表格预览展示精确省略行/列数，并可展开查看隐藏列名；
  仍通过外层授权 Artifact 进入完整数据。
- focused tests `11 passed`；typecheck 通过。

## Continuous optimization — Improvement #50 / CO-078 (2026-09-05)

- Viewer 明确呈现辅助 Artifact 的部分失败与稳定错误码，并支持重试；
  主 Artifact 仍可读，避免“部分结果”被误认为完整。
- focused tests `8 passed`；typecheck 通过。

## Continuous optimization — Improvement #51 / CO-070 (2026-09-05)

- Generic Plot 抽样预览显示原始总点数与保真策略（端点/极值保留），
  避免将显示上限误读为科学数据规模。
- focused tests `10 passed`；typecheck 通过。

## Continuous optimization — Improvement #47 / CO-131 (2026-09-05)

- 增加 ResearchTurn/ScientificObject 精确 ID 的跨项目授权矩阵；
  覆盖读、写、query、Viewer、事件入口，陌生用户统一 403 且不泄露
  对象/版本标识。
- 授权子集 `1 passed, 27 deselected`。
## Continuous optimization — Improvement #52 / CO-079 (2026-09-05)

- 结构 Viewer 对超过 256 个站点的有界显示现在呈现权威的“当前显示前
  256 / 总数”警告，且明确完整结构仍保留在源数据中。
- 通过 mapper 保留经过校验的 payload warning message，surface 对代码与消息
  去重后只显示一个可访问状态提示；没有改变 ScientificResult 或源数据权威。
- 验证：viewer mapper/surface focused tests `43 passed`，typecheck PASS。
- 提交/CI：未提交、未推送；持续优化任务保持处理中。
## Continuous optimization — Improvement #53 / CO-082 (2026-09-05)

- 配位数直方图为每个有界 bin 增加绑定到图形的可访问文本摘要，包含配位数、
  位点数和占比；保留现有语义数值表作为详细替代。
- 使用 `useId` 生成实例稳定的 `aria-describedby` 关系，避免重复 DOM ID。
- 验证：focused tests `2 passed`，typecheck PASS；未改变科学权威。
## Continuous optimization — Improvements #54–#55 (CO-080 / CO-085, 2026-09-05)

- Dataset Explorer 与通用 Scientific Table 采用统一的有界分页/总量披露，
  保留 sample_id/sampleRef 稳定身份，focused tests `17 passed`。
- Report Figure/Table Artifact 预览将权限、缺失、过期、无效内容和大小边界
  映射到稳定安全状态，focused tests `12 passed`；typecheck PASS。
- 未改变科学事实权威或重算行为；未提交/未推送。

## Continuous optimization — Improvement #56 / CO-098 (2026-09-05)

- Research 生命周期菜单在 archive/restore 后恢复来源焦点；行被当前筛选
  隐藏时回退到状态筛选按钮，并提供 `aria-live` 成功播报。
- 修改文件：`apps/web/app/components/ResearchPages.tsx`、
  `apps/web/app/components/ResearchPages.test.tsx`及 CO-098 evidence。
- 验证：lifecycle focused test `1 passed, 74 skipped`；typecheck PASS。

## Continuous optimization — Improvement #57 / CO-132 (2026-09-05)

- Scientific Table 对共享 `objectId` 的多样本行使用对象作用域的稳定样本
  key，消除 duplicate React key warning，保持分页/筛选后的行身份稳定。
- 修改文件：`apps/web/app/components/workspace/WorkspaceArtifactGallery.tsx`、
  `apps/web/app/components/workspace/WorkspaceArtifactGallery.test.tsx`及
  CO-132 evidence。
- 验证：gallery focused tests `5 passed`且无 duplicate-key warning；typecheck PASS。

## Continuous optimization — Improvements #58–#61 (2026-09-05)

- CO-081：Dataset 样本引用与对象作用域稳定 ID 成为主要身份，源行明确为
  辅助定位；focused tests `12 passed`。
- CO-099：取消终态只由权威 execution card 呈现一次；cancel cases
  `3 passed`，execution activity `11 passed`。
- CO-090：重复 Presentation 的 Evidence/inspector/Finding ARIA 身份加入
  实例作用域；Presentation/Viewer/Report `35 passed`。
- CO-133：Workspace Gallery 主标题、分组和活动 Viewer 标题 ID 加入
  `useId` 实例作用域；gallery `6 passed`。
- 四项 typecheck PASS，未改变科学数据、Result 或版本权威。

## Continuous optimization — Improvement #62 / CO-108 (2026-09-05)

- Generic JSON Artifact 采用有界结构投影后再序列化，限制节点、层级、数组项、
  对象字段和长文本；完整 Artifact 保持权威且预览披露精确省略量。
- 10 万项回归证明尾部 getter 未被读取；focused test `1 passed`，
  typecheck PASS。

## Continuous optimization — Improvements #63–#66 (2026-09-05)

- CO-075：来源缺失 Viewer 保留有界身份/指纹/来源摘要并可安全导出元数据；
  Viewer focused tests `6 passed`。
- CO-093：Research 状态筛选支持命名组与方向键/Home/End；合并回归
  `77 passed`。
- CO-102：空 Research 状态提供授权正确的 Data Platform 入口，归档/回收
  项目不会误获写权限；合并回归 `77 passed`。
- CO-117：service-backed CI 使用 JUnit XML 确定性汇总，解析器 `2 passed`，
  JUnit smoke selected=2/passed=2/zero skip-fail-error。
- 合并 typecheck、Ruff 与 diff check PASS；未改变科学权威。

## Continuous optimization — Improvements #67–#69 (2026-09-05)

- CO-111：Viewer 重试增加进行中去重、可取消的有界退避和卸载清理；
  focused tests `4 passed`。
- CO-113：Trash Center 支持授权分组的批量恢复及 typed partial-failure；
  focused tests `8 passed`。
- CO-119：CI 始终上传 integration log/exit/JUnit/脱敏 runtime 快照；
  workflow parse PASS，operations `11 passed, 1 historical skip`。
- 合并 typecheck/diff PASS；同栈 PostgreSQL/Redis/MinIO 和 6 workers 正常。

## Continuous optimization — Improvement #70 / CO-104 (2026-09-05)

- Research session 预热缓存新增生命周期失效回归：缓存窗口内合并读取，
  archive/restore/rename 后强制重新访问授权 API。
- product-api `7 passed`；typecheck/diff PASS。

## Continuous optimization — Improvements #71–#75 (2026-09-05)

- CO-114：依赖影响条目使用服务端授权的 ProductLink 打开 exact Data、
  Research 和 Report；backend `37 passed, 4 historical skips`，
  frontend `66 passed`。
- CO-073：Viewer 区分场景校验、WebGL、chunk 和初始化失败；focused
  `25 passed`。
- CO-053：持久化停滞 RUNNING 任务进入“需要关注”，保持真实状态且只提供
  检查/停止动作；focused `7 passed`。
- CO-096：Edit-last-message 在原 Turn 读取失败时 UI 与提交合同双重
  fail closed；精确 focused `2 passed`。
- CO-095：Continue 仅对 Result 404 进入新执行；其他读取失败不创建新 Turn，
  exact snapshot 作为可见复用候选；合并 Research/API `89 passed`。
- 五项合并 typecheck/diff PASS；未改变 ScientificResult、版本或执行权威。

## Continuous optimization — Improvements #76–#78 (2026-09-05)

- CO-077：Viewer 生命周期控件显示权限/归档/回收站/服务状态的可访问禁用
  原因；focused `8 passed`。
- CO-094：Retry 创建新的持久化子 Turn，显示并链接原失败 Turn；
  focused `3 passed`，完整 Research `85 passed`。
- CO-100：运行中草稿按 exact Project/Session/Turn 保存在当前标签页并可
  刷新恢复；完整 Research `85 passed`。
- 合并 typecheck/diff PASS；无科学重算或历史 lineage 覆盖。

## Continuous optimization — Improvement #79 / CO-115 (2026-09-05)

- 将 Project、Research session 与 Report 的非科学组织语义统一为“列表置顶”；
  将 Result 与 exact source version 的科学上下文操作统一为“加入/移出本会话
  上下文”。
- Presentation 操作区增加简短权威说明：会话上下文可影响后续研究，列表
  置顶仅改变排序。
- frontend focused `151 passed`，typecheck/diff PASS；未修改科学事实、
  版本、执行或授权权威。

## Continuous optimization — Improvement #80 / CO-050 (2026-09-05)

- Task Center 与 Notification Center 的共享 feed 支持消费者级取消；只有
  全部可取消消费者退出才会中止底层请求。
- hidden/offline 会取消在途刷新并暂停轮询，恢复后从持久化权威重新读取；
  Abort 不再误报为同步失败。
- focused `21 passed`，合并 typecheck/diff PASS；未停止服务或浏览器。

## Continuous optimization — Improvements #81–#84 (2026-09-05)

- CO-083：Data 查询、排序、行选择和 canonical sample selection 写入
  bounded URL/history，保持 Dataset/Object/Version 精确身份；`48 passed`。
- CO-088：Plot 与 Report SVG 预览采用端点、全局极值、分桶局部极值采样，
  并披露 shown/total/strategy；`24 passed`。
- CO-097：Research 分支展示 persisted Turn/parent/message-revision 上下文、
  来源问题与 exact URL；Research `86 passed`。
- CO-049：Task/Notification 共享 feed snapshot、request、poller 和生命周期，
  双消费者请求去重；`22 passed`。
- 四项合并 typecheck PASS，diff check 仅既有 CRLF 警告；未改变科学权威。

## Continuous optimization — Improvement #85 / CO-103 (2026-09-05)

- ProductShell 的隔离/无项目 fallback 预取改为可取消的空闲队列，每个
  idle/timer 时隙只预取一个路由，切换/卸载时清理剩余队列。
- dedicated scheduler test `1 passed`，typecheck PASS，diff check 仅既有
  CRLF 警告；不影响首屏主导航或科学权威。

## Continuous optimization — Improvements #86–#87 / CO-048, CO-109 (2026-09-05)

- CO-048：saved-search 通过同页、storage 与 BroadcastChannel 只广播 opaque
  revision，跨标签刷新授权列表并去重；sync `5 passed`、ProductShell `21 passed`。
- CO-109：Workspace Artifact Gallery 对 Artifact identity 建 memoized O(1)
  索引，500-artifact focused `11 passed`，typecheck PASS。
- 两项均未改变科学、版本、执行或授权权威。

## Continuous optimization — Improvement #88 / CO-055 (2026-09-05)

- Research 与 Task Center 统一 `CANCELING`/`cancel_requested` 状态契约，
  取消中每 1.8s 从持久化任务刷新至终态，重复停止动作禁用。
- focused `25 passed`，typecheck PASS，diff check 仅既有 CRLF 警告；
  未伪造完成，也未改变后端取消权威。

## Continuous optimization — Improvement #89 / CO-134 (2026-09-05)

- ArtifactDownloadLink 对 caller-provided filename 移除控制字符、路径分隔符、
  前导点遍历并限制 120 字符；空/点文件名回退为浏览器默认命名。
- focused `3 passed`，typecheck PASS，diff check PASS；未改变内容路由、
  Artifact 权限或科学数据。

## Continuous optimization — Improvement #90 / CO-051 (2026-09-05)

- Task Center 保留服务端授权 `nextCursor`，按页加载更早任务，使用
  `projectId:jobId` 去重合并并保留 exact ResearchTurn 链接；后续页失败
  可重试且不触发科学计算。
- 1000-job/10-page 与 Task Center focused 共 `21 passed`，typecheck PASS，
  diff check PASS。

## Continuous optimization — Improvement #91 / CO-110 (2026-09-05)

- Scientific Viewer 将 metadata-ready 与 payload-loading 分层；重 payload
  延迟时仍展示 Artifact identity、ToolCall、SHA-256、来源入口与 retry。
- focused `8 passed`，typecheck PASS，diff check 仅既有 CRLF 警告；无科学重算。

## Continuous optimization — Improvement #92 / CO-054 (2026-09-05)

- Task Center 的 Open 仅恢复 exact ResearchTurn；Open-and-retry 通过
  `retry=1` 在失败/取消且可写时创建唯一 child Turn，`parent_turn_id` 指向
  原 Turn，旧证据保留。
- Research + Task Center 合并回归 `99 passed`，typecheck PASS，diff check
  仅既有 CRLF 警告。

## Continuous optimization — Improvement #93 / CO-037 (2026-09-05)

- Report/Presentation grid 子项设置 `min-width:0`/`max-width:100%`，宽表
  使用可聚焦独立滚动区，移动操作控件可换行，避免全局横向裁剪。
- Workspace Gallery focused `7 passed`，typecheck PASS，diff check 仅既有
  CRLF 警告。

## Continuous optimization — Improvement #94 / CO-056 (2026-09-05)

- Research remount/visibility/online recovery 从授权 Session 的 persisted Turn
  inventory 校验 exact Project/Session/Turn，缺失消息从 Turn 恢复，progress/
  Result 继续由现有后端 API 重建。
- focused recovery/reconnect PASS，typecheck PASS；完整 Research `88 passed`
  加 1 个顺序敏感 context retry case（单测独立通过）。

## Continuous optimization — Improvement #95 / CO-135 (2026-09-05)

- 复用现有 project-authorized Artifact content route；普通打开保持 inline，
  显式下载追加 `download=true` 并仅此时返回安全 attachment disposition。
- 后端 Artifact content `7 passed`；前端 Artifact/Presentation/Report
  `35 passed`；typecheck PASS。未新增 Artifact authority，未触发科学重算。

## Continuous optimization — Improvement #96 / CO-032 (2026-09-05)

- Provider request/error、Queue Job/Tool/依赖 failure event 与 Report failure
  summary 使用统一递归敏感信息脱敏和 sentinel scanner。
- 覆盖 credential、Bearer/API token、Redis/MinIO/S3 endpoint 与绝对路径，
  同时确定性保留科学数值、单位、sample/version identity 与 evidence refs。
- focused `37 passed`；Provider/scanner subset `11 passed`；compileall、Ruff、
  web typecheck 与 diff check PASS。

## Continuous optimization — Improvement #97 / CO-069 (2026-09-05)

- 修复 generic Plotly 异步创建完成晚于 unmount 时的重复 purge：释放路径
  现在幂等。
- Scene/Trajectory/Phonon/Volumetric viewer 已审计其 engine/worker/request/
  listener cleanup；focused renderer cleanup `60 passed`，typecheck PASS。

## Continuous optimization — Improvement #98 / CO-058 (2026-09-05)

- 复用现有 persisted relations，新增 project-authorized 只读 correlation
  endpoint，投影 Turn、Job、最多 64 个 ToolCall、Result 与 Report identity。
- 明确排除参数、路径、storage key、provider payload、queue internals 与
  credentials；focused API `2 passed`，Ruff/compileall/diff PASS。

## Continuous optimization — Improvement #99 / CO-045 (2026-09-05)

- Global search 使用绑定 user/query/project/type/status 的有界 continuation
  cursor；每页重做 project authorization，稳定排序与实体去重。
- ProductShell 增加 SPA 加载更多/重试与扫描上限披露；125 个授权结果六页
  唯一数 125、私有泄漏 0；后端 `9 passed`、前端 `22 passed`、typecheck PASS。

## Continuous optimization — Improvement #100 / CO-035 (2026-09-05)

- 新增最多 50 条、仅当前标签页、无 prompt/凭据的 Research performance
  ledger；双 animation frame 记录可见确认，并绑定 exact Turn 的首个
  persisted progress，跨 App Router route handoff 不丢失。
- 当前工作树独立 production 前端 `3024`、API `8005` 同栈五次采样：
  acknowledgement p50/p95 `26/29 ms`；first `RECEIVED` p50/p95
  `262/293 ms`；browser warn/error 0。
- helper `5 passed`、focused Research `1 passed`、typecheck/build PASS。

## Continuous optimization — Improvement #101 / CO-136 (2026-09-05)

- 清理旧 acceptance frontend 后，仅保留当前 immutable 3024；新增默认
  dry-run 的 health-gated rotation 工具。
- 工具仅接受本仓库 exact Next binary、`next start`、候选端口匹配的
  `node.exe` listener，排除当前端口及 API/workers/PostgreSQL/Redis/MinIO。
- live 3025 dry-run/apply 精确识别并停止 PID 26440；3024 和完整后端栈保持
  健康；focused `2 passed`，diff PASS。

## Continuous optimization — Improvement #102 / CO-071 (2026-09-05)

- Generic Plot 对 heatmap cell、mesh vertex、mesh triangle 分别设置 100,000
  hard cap；超限进入类型明确的 refused state，不把过重 payload 交给 Plotly。
- 完整 persisted Artifact 仍可授权打开/下载；未静默截断或触发科学重算。
- focused `13 passed`，typecheck/diff PASS。

## Continuous optimization — Improvement #103 / CO-030 (2026-09-05)

- Session-expired 统一恢复路径保留 `pathname + search + hash`，并向登录页传递
  有界 `session-expired` 原因；Research 本地草稿不因 401 被清除。
- 登录页明确说明重新认证后返回原页面，继续使用 Cookie/session authority，
  外部或歧义 return URL 仍 fail closed。
- ProductShell/LandingPage focused `27 passed`，typecheck/diff PASS。

## Continuous optimization — Improvement #104 / CO-052 (2026-09-05)

- Notification Center 的 read/unread 改为 `user_configs` 中非科学、用户私有
  的持久状态，绑定 user/project/Job/Job updated revision。
- Job 后续更新会自动重新未读；读写均重验项目权限与 Job/project 精确关系，
  撤权后不返回对应状态。
- 后端 `2 passed`、前端/API `14 passed`，typecheck、Ruff、compile/import、
  route registration 与 diff check PASS。

## Continuous optimization — Improvement #105 / CO-033 (2026-09-05)

- Scientific Presentation 改为逐 block 精确字段白名单，严格验证嵌套 source、
  reference、confidence 与 evidence，拒绝隐藏 component/module/HTML/URL 字段。
- Viewer registry 只接受有界声明式 token；Pack 注册原子拒绝动态、可执行或
  远程 viewer binding；后端 descriptor 标识符同步收紧。
- 后端 `44 passed`、前端 `29 passed`，typecheck、Ruff、diff PASS。

## Continuous optimization — Improvement #106 / CO-086 (2026-09-05)

- Planner Artifact browse/download 继续共享 exact Job/project 授权并在 storage
  read 前拒绝越权；inline 与 attachment disposition 保持分离。
- storage 临时缺失为 typed 404；metadata 保留但无 payload location 为 typed
  410；超过 64 MiB 浏览传输上限在读取 storage 前为 typed 413；完整性失败仍 422。
- Viewer/Report 显示对应专业状态且不伪造 retry/download；后端 `11 passed`、
  前端 `40 passed`，typecheck、Ruff、compileall、diff PASS。

## Continuous optimization — Improvement #107 / CO-105 (2026-09-05)

- Project History 增加 datasets/analyses/activity 各自有界 server cursor，
  保留未分页兼容调用；Project Home 首屏每区只取 8 条。
- “继续加载”按区追加稳定服务端页面，不复用旧全量 cache，保持 exact identity
  与 SPA route。
- 1000-item 回归；后端 `5 passed`、前端 `5 passed`，typecheck/diff PASS。

## Continuous optimization — Improvement #108 / CO-039 (2026-09-05)

- 新增 typed `local | same-stack` runtime profile；未知 backend、环境 alias 冲突、
  scheme 不符及缺失 PostgreSQL/Redis/MinIO/Agent 设置均在 serving 前 fail fast。
- Worker 消费前核对 API 的 exact Redis URL/DB namespace 与队列名；启动脚本
  明确选择 same-stack，不修改 health 文案来伪装运行时。
- runtime/worker/health focused `35 passed`，Ruff/diff PASS。

## Continuous optimization — Improvement #109 / CO-046 (2026-09-05)

- Global Search 增加 UTC inclusive date_from/date_to，全部筛选进入 cursor
  fingerprint，非法范围 typed 422。
- Result 使用权威 Turn→Session 关系生成 exact SPA destination，并同时核对
  Project；active/archived/trashed × 六类实体与 Finding 共 18 场景覆盖。
- 后端 `27 passed`、前端 `28 passed`，typecheck、Ruff、route/diff PASS。

## Continuous optimization — Improvement #110 / CO-029 (2026-09-05)

- 扩展 24-route HTTP 矩阵覆盖 Turn/Context/Correlation/Result/Report/History/
  Object/Version/Query/Viewer，并增加 exact Report/Evidence/Dataset/Artifact
  的投影与 storage 前拒绝测试。
- Project History pytest compatibility 不再吞 403；仅真正缺少 synthetic
  Project 才进入旧适配路径。
- HTTP matrix `1 passed`、Report/Evidence `3 passed`、Dataset/Artifact
  `2 passed`，Ruff/compileall/diff PASS。

## Continuous optimization — Improvement #111 / CO-107 (2026-09-05)

- ContextManifest 默认保持 8 项；展开后采用 32 项窗口与前后导航，不再将
  大清单一次性渲染进 DOM。
- 窗口切换保留服务端顺序、exact source/Result/scientific provenance，
  后端 128-item 权威上限不变。
- 10,000-item 前端压力回归、focused `3 passed`、后端 ContextManifest
  `13 passed`，typecheck/diff PASS。

## Continuous optimization — Improvement #112 / CO-031 (2026-09-05)

- 新增 Project role capability contract：owner 可 purge；admin/researcher
  可写、归档、研究；viewer 只读/导出；平台管理员不隐式获得 Project 权限。
- `projects.created_by` 保持唯一 owner；协作者不能被提升为 owner，历史重复
  owner membership 只按 admin 投影，避免 UI 展示服务端会拒绝的永久删除。
- 后端 `5 passed`；权限/Admin UI `12 passed`；Project/Research UI `9 passed`；
  typecheck、Ruff、compileall、diff PASS。

## Continuous optimization — Improvement #113 / CO-041 (2026-09-05)

- API、六类 Redis worker 与 frontend 启动统一接入 rotating log runner。
- 活动日志按 25 MiB/UTC 日切分；每流最多 8 个、14 天归档；只清理严格托管
  命名，活动日志、手工副本和其他文件不会进入删除集合。
- focused `5 passed`、Ruff、三个 PowerShell parser、diff PASS；当前服务未重启。

## Continuous optimization — Improvement #114 / CO-074 (2026-09-05)

- Volumetric mixed periodic/non-periodic boundary 保持科学数据有效，但以
  `mixed_boundary_conditions_unsupported` 明确标记当前 renderer 不支持。
- 损坏 boundary、payload/grid mismatch、越过声明范围的 inline data 分别返回
  typed invalid 状态，不再混成一个笼统 schema error。
- focused `7 passed`、typecheck/diff PASS。

## Continuous optimization — Improvement #115 / CO-047 (2026-09-05)

- Global Search continuation 从 offset 升级为绑定用户与全量筛选条件的 opaque
  keyset v2；权威排序为 `updatedAt/kind/id`，分页期间插入新记录不会造成既有
  continuation 重复或漏项。
- Project、membership、Dataset、Research Session、Report、
  ScientificObject、ScientificResult 增加迁移管理的复合搜索索引。
- 1,250 条语料（1,000 可见、250 私有）30 次采样 p95 `15.33 ms`，
  payload 小于 64 KiB，跨 Project 泄漏为 0。
- 后端 `27 passed`、迁移 `4 passed`、前端 `32 passed`，Ruff/diff PASS。

## Continuous optimization — Improvement #116 / CO-040 (2026-09-05)

- `/health/runtime` 新增 `RuntimeConfigurationFingerprint/1.0`，组合已声明
  拓扑与真实 SQL/Redis/MinIO 成功探测，不再只能比较易混淆的 backend 名称。
- 每个连接只暴露 SHA-256 指纹；密码/Access Key 不参与指纹输入，目标或
  backend 改变会改变身份，凭据轮换不会形成 secret comparison oracle。
- live same-stack 三个 `connectionBound=true`，组合指纹 `7e6302…7ad4`。
- 仅滚动 API `27560 → 26356`；数据库、Redis、MinIO、workers、frontend、
  browser tabs 均保持运行；focused `3 passed`，Ruff/compileall/diff PASS。

## Continuous optimization — Improvement #117 / CO-043 (2026-09-05)

- 同一跨平台只读磁盘策略现在覆盖 pytest session、npm test/typecheck/build、
  packaged Playwright evidence、CI 和 API/worker/frontend 启动。
- 默认 5/10 GiB critical/warning；capacity、path、configuration typed failure，
  `MDI_DISK_FALLBACK_PATH` 提供经验证的恢复卷信息。
- focused `11 passed`、前端 `5 passed`、typecheck 和独立 distDir production
  build PASS；Ruff、compileall、四个 PowerShell parser、diff PASS。
- 当前 E: 可用 `47,090,618,368` bytes；运行 frontend 保持 HTTP 200。

## Continuous optimization — Improvement #118 / CO-042 (2026-09-05)

- 新增 allowlisted cleanup：默认/显式 dry-run；apply 仅将已审查 regular file
  移入 `.cleanup_archive`，不做永久删除；symlink 和越界路径 fail closed。
- live 分类：0 自动候选、1 未过期临时文件、17 release-evidence roots、
  16 service-data roots、45 protected logs、1 recovery archive entry。
- `$neat-freak` 要求的复核现场保留：CO-043 独立 build 约 285 MB 已隔离，
  必须在完整汇报后取得明确清场确认再永久清除。
- focused `4 passed`，Ruff/compileall/diff PASS。

## Continuous optimization — Improvement #119 / CO-060 (2026-09-05)

- Alembic 自动门禁锁定单一线性 head `0031_product_search_keyset`，全部 revision
  必须可从 head 到达且同时定义 upgrade/downgrade。
- AST guard 阻止未经审查的 drop table/column、TRUNCATE、DELETE FROM；
  guard 自身包含负向检测样例。
- 0030→0031→0030→0031 数据往返保留 Project、ScientificObject、exact
  ScientificObjectVersion、ResearchTurn、ScientificResult 身份。
- migration/fresh/legacy `7 passed`，Ruff/compileall/diff PASS。

## 2026-09-05 — Continuous optimization CO-137

The continuous optimization ledger is now self-validating. Five stale duplicate
OPEN rows were removed while their completed records were retained, the
append-only result archive was reconciled for CO-027/CO-028, and a deterministic
guard now rejects duplicate/non-contiguous IDs, counter drift, invalid CURRENT
state and completed work without a result record. The live ledger reports
`137 discovered / 121 completed / 0 blocked / 16 remaining`, and focused
verification reports `5 passed`.

## 2026-09-05 — Continuous optimization CO-044

npm, Playwright, pytest, tool temporary files and Next output now use bounded,
configurable workspace-local caches. Overrides outside the repository fail with
typed configuration errors, and Next output is additionally constrained to the
web root. Focused routing reports `3 passed`; typecheck and two production
builds pass without interrupting the live frontend.

## 2026-09-05 — Continuous optimization CO-063

A checked-in `WorkerQueueManifest/1.0` now defines all six Agent2 queue roles,
names, settings attributes and handlers. API settings, producers, recovery,
operations, health and launchers consume that same authority. A live blue/green
rotation proved the new manifest on PostgreSQL/Redis/MinIO: new API PID 25628
and six generation-tagged workers were validated before all obsolete API/worker
processes were retired; frontend 3024 remained available.

## 2026-09-05 — Continuous optimization CO-106

Research conversations now use a 100-message navigable DOM window once a
session exceeds that size. Older/newer controls preserve persisted message IDs
and focus, while session/Turn changes reset the window safely. A 1,001-message
component regression keeps the DOM at 100 nodes, 20 projections remain under
the 100 ms budget, and the complete Research suite reports `92 passed`.

## 2026-09-05 — Continuous optimization CO-061

Same-stack API and worker admission now compares the connected database
revision with the repository's unique Alembic head. The real qualification
database was discovered at `0030_account_invitations`; a shadow API refused it
with `DATABASE_MIGRATION_HEAD_MISMATCH`. After a pg_dump backup and explicit
upgrade, API/worker startup verified `0031_product_search_keyset`. Alembic now
recognizes the launcher's `MDI_POSTGRES_HOST` alias. Startup remains read-only
and never auto-migrates. Final runtime has one API and six current workers;
obsolete and failed generations were retired.

## 2026-09-05 — Continuous optimization CO-057

Operations alerts now join queue depth, stale Jobs and actual worker
state/heartbeat health to bounded repository runbooks. The platform-admin
surface displays sanitized metrics and response guidance but cannot mutate
queues or scientific records. Focused backend reports `21 passed` plus one
separately executed same-stack integration PASS; frontend reports `8 passed`.
The live snapshot is healthy with 6/6 workers, empty queues and zero alerts.

## 2026-09-05 — Continuous optimization CO-059

API, worker and browser failures now share `OperationalExceptionEvent/1.0`.
The contract records release SHA and bounded request/scientific correlation
identities while excluding exception messages, stacks, prompts, credentials,
service URLs and filesystem paths. An authenticated live capture through
frontend 3023/API 8005 returned 202 and was recorded with request identity
`b7f5745f2d854e4d9907e891555cf959`; focused backend `16 passed`, frontend
`2 passed`, typecheck/Ruff/diff PASS.

## 2026-09-05 — Continuous optimization CO-101

Research and Task Center now consume one cancellation availability contract.
Only an explicit modern ResearchTurn may expose Stop; legacy Jobs remain
read-only and unresolved tasks fail closed. The contract regression reports
`3 passed` and the combined Task Center/status run reports `14 passed`; its one
unrelated brittle shared-feed assertion is tracked as CO-138.

## 2026-09-05 — Continuous optimization CO-062

API, worker and operations diagnostics now consume one
`SameStackRuntimeTopology` builder for PostgreSQL, Redis and MinIO aliases.
Changing the bounded Redis override reached API settings, worker resolution,
health probing and operations configuration identically. Focused runtime tests
report `38 passed` with one existing opt-in live skip; the real same-stack
snapshot remained healthy with 6 workers, queue depth 0 and
idle-in-transaction 0.

## 2026-09-05 — Continuous optimization CO-064

Runtime health and operations now share `ServiceFailure/1.0` for PostgreSQL,
Redis and MinIO. Authentication, configuration, missing resource, timeout,
unavailable and unknown failures have stable retry metadata and never include
raw exception messages. Focused classification reports `6 passed`; the live
same-stack services remain healthy. A separate stale Phase 5 source-text
assertion discovered during regression is tracked as CO-139.

## 2026-09-05 — Continuous optimization CO-066

Artifact storage now rejects writes above 256 MiB before Local or S3/MinIO
publication. Local writes use a same-directory `.part` file followed by atomic
replacement and remove temporary content after interruption. Artifact plus
upload/input-transport regressions report `22 passed`; existing upload-session
64/128 MiB limits and scientific authority remain unchanged.

## 2026-09-05 — Continuous optimization CO-065

Research submit now has a synchronous browser single-flight guard while the
PostgreSQL active-Turn limit remains authoritative and returns typed 429 plus a
bounded `Retry-After` hint. Global Search propagates `AbortSignal` and cancels
obsolete requests. A 24-request pressure run persisted exactly 3 Turns and
limited 21; backend `13 passed`, ProductShell/Search `29 passed`, complete
Research Pages `93 passed`, typecheck/Ruff/diff PASS.

## 2026-09-05 — Continuous optimization CO-116

CI third-party Actions now use full commit SHAs and PostgreSQL/Redis/MinIO
service images use immutable manifest digests. A checked-in provenance lock
records reviewed tags and resolved identities, while focused guards reject
floating references. The five official Action tags re-resolved exactly and the
focused suite reports `3 passed`.

## 2026-09-05 — Continuous optimization CO-118

Mandatory PostgreSQL/Redis/MinIO qualification now has one versioned manifest
for 29 test paths, 34 required identities, minimum 50 passed and zero
skip/failure. CI and local runbooks invoke the same runner, and enforcement
uses JUnit structure rather than terminal grep. Focused manifest/validator
regression reports `6 passed`.

## 2026-09-05 — Continuous optimization CO-138

The Task Center and Notification Center shared-feed regression now validates
one shared request/refresh transition plus each surface's semantic heading,
instead of requiring a duplicated project-name text node. The complete
Task/Notification/feed focused matrix reports `27 passed`.

## 2026-09-05 — Continuous optimization CO-139

The Phase 5 migration-environment regression now follows the current typed
database authority: `load_settings().database_url`, explicit configuration
detection and safe Alembic URL injection. The complete runtime infrastructure
file reports `9 passed, 1 existing skip`.

## 2026-09-05 — Continuous optimization CO-067

Qualification PostgreSQL/MinIO state now has an isolated run manifest,
ACTIVE/COMPLETED/FAILED lifecycle, active marker, 14-day TTL and indefinite
release-evidence protection. Retention defaults to read-only planning and an
explicit apply performs only recoverable moves. Existing legacy service
directories and current live services are intentionally outside its managed
scope. Focused tests report `7 passed`; the real repository dry-run found zero
candidates.

## 2026-09-05 — Continuous optimization CO-068

The operations projection now reports six bounded, read-only and redacted
storage categories. PostgreSQL uses `pg_database_size`, MinIO has a bounded
10,000-object scan, filesystem categories do not follow symlinks, and platform
admin output is allowlisted a second time. A real same-stack snapshot found
database, MinIO, logs and qualification profiles within budget; repository
build/test caches consume 40,349,971,256 bytes and exceed the 25 GiB budget.
Cleanup is deliberately separated into CO-140.

## 2026-09-05 — Continuous optimization CO-120

The canonical release quickstart now describes one lockfile-driven Windows
retained same-stack path. It builds the exact frontend artifact consumed by
the launcher, runs the current single Alembic head, validates the real
PostgreSQL/Redis/MinIO endpoints, uses `/health/runtime`, keeps services
running by default and limits automated old-process cleanup to the existing
repository-scoped frontend rotation contract. Focused tests report `5 passed`;
live `-CheckOnly` confirms the 3023/8005 same-stack topology.

## 2026-09-05 — Continuous optimization CO-140

A fingerprinted, dry-run-first cleanup authority now limits deletion to
untracked direct `apps/web/.next*` build directories and resolves the active
localhost frontend BUILD_ID before apply. The reviewed plan removed 105
historical generated builds / 38,056,000,111 bytes while preserving
`apps/web/.cache/next-live-20260905`, all source/service/profile/evidence data,
and the live PID 29664 frontend. Build-cache usage fell from 40.35 GB to
2.29 GB (8.55% of budget); focused tests report `14 passed`.

## 2026-09-05 — Continuous optimization CO-141

Provider connection authority now follows runtime topology. Local/test can use
an explicit process adapter; same-stack PostgreSQL uses the new
`provider_connections` table and requires a stable Fernet key before writing
ciphertext. Provider mutation is platform-admin-only, browser responses stay
redacted, and legacy `/me/secrets` fails closed with typed 503 outside
local/test instead of implying persistence. The live database was backed up
and migrated from 0031 to the single 0032 head. A shadow 8006 API proved the
real PostgreSQL/Redis/MinIO topology and authenticated legacy boundary before
the old 8005 API was replaced; the shadow and old process pairs were then
stopped. Final 8005 PID is 29280, frontend PID remains 29664, and no duplicate
API listener remains. Focused backend reports `84 passed`, frontend `40
passed`, with typecheck/Ruff/compileall/diff PASS.

## 2026-09-05 — Continuous optimization CO-142

FastAPI startup now uses one app-factory-scoped async lifespan rather than two
deprecated `on_event` registrations. Database migration-head validation
remains the first admission action and raises before recovery; interrupted
Research recovery remains bounded best-effort and logs failure without
claiming scientific completion. Multiple `create_app()` instances retain
their own immutable settings snapshot. Focused regression reports `49 passed`
and a strict deprecation gate reports `7 passed`. A real same-stack shadow
8006 emitted no warning before replacing canonical 8005. Final API PID is
20748; old and shadow process pairs are stopped, 8006 is closed, and frontend
PID 29664 remains active.

## 2026-09-05 — Continuous optimization CO-143

The Phase 14-R recovery regression now imports the `UUID` type used by its
queue annotations. This closes two Ruff F821 failures that pytest had masked
through postponed annotations, without changing recovery behavior. The
complete file reports `6 passed`; Ruff, compileall and diff check pass. The
live single-instance API/frontend/service topology remained unchanged.

## 2026-09-05 — Continuous optimization CO-144

API startup and replacement now have a repository-scoped process authority.
Each new instance writes an atomic manifest with exact child/runner identity,
release SHA and runtime fingerprint. Rotation is dry-run by default, validates
the shadow before stopping canonical, revalidates every PID before stopping
child then runner, checks the frontend proxy, and closes the shadow on success.

A real same-stack cutover replaced legacy API `20748/16260` with managed API
`18468/19620`. The old pair is absent, 8005 has one listener, 8006 has none,
and frontend PID `29664`, all six worker pairs, PostgreSQL, Redis and MinIO
remained unchanged. Focused regression reports `20 passed`; the post-rotation
operations snapshot has zero alerts, zero queue depth and zero checked-out DB
connections. CO-145 now tracks the MinIO scan approaching its bounded limit.

## 2026-09-05 — Continuous optimization CO-145

Bounded MinIO capacity diagnostics now distinguish complete measurements from
observed lower bounds. Hitting the object scan limit or losing a continuation
token produces a typed reason, keeps the count/bytes as bounded observations,
suppresses a false utilization percentage and emits a read-only operations
warning. The warning explicitly directs operators not to delete scientific
Artifacts merely to clear monitoring state.

Focused operations/storage/admin regression reports `29 passed` with one
existing opt-in integration skip. A bounded simulation proves keys are not
projected, while the real same-stack 8,739/10,000-object scan remains complete
and alert-free. The code was loaded through managed API rotation; old API
`18468/19620` exited, canonical is `25704/5060`, and 8006 is closed.
## Continuous optimization CO-146 (2026-09-06)

API runtime ownership now has an explicit protected path. A shared PowerShell
helper resolves `.runtime_services/managed/api`; startup writes its atomic
manifest there, and rotation first checks this path while retaining bounded
compatibility with the previous `.cache/runtime` location. Legacy metadata is
removed only after the exact child/runner pair is stopped. Repository cleanup
classifies `.runtime_services` as protected active service data.

Live same-stack rotation replaced API child/runner `25704/5060` with
`12044/19996`, retained the frontend and PostgreSQL/Redis/MinIO/workers, closed
8006, and left one canonical 8005 listener. Focused tests report `21 passed`;
PowerShell AST, Ruff and diff checks pass. CO-147 is the next open finding:
worker launchers lack equivalent repository-scoped identity manifests.
## Continuous optimization CO-147 (2026-09-06)

Stack startup now treats the checked-in worker queue manifest as the expected
topology rather than using an any-worker shortcut. It temporarily scopes
`packages/schemas` into `PYTHONPATH`, compares each expected queue with live
`mdi_workers.worker_entrypoint` command lines, and invokes the worker launcher
with `-OnlyQueue` only for missing queues. Requested queue names outside the
manifest fail closed.

The real same-stack startup command completed with all six queues present. The
12 runner/child process PIDs were identical before and after, so no duplicate
workers were created and no running service was stopped. Focused regression
reports `17 passed`; PowerShell AST, Ruff, compileall and diff checks pass.
CO-148 remains open for per-queue identity manifests and exact future worker
replacement.
## Continuous optimization CO-148 (2026-09-06)

Worker ownership now has a durable, protected per-queue manifest. The
discovery script reads the checked-in queue authority, pairs each
`worker_entrypoint` child with its log-runner parent by PID, and atomically
records queue/role/handler, Redis URL, creation FILETIMEs, executable paths,
command digests and release SHA under `.runtime_services/managed/workers`.

Live discovery wrote six records for the six expected queues without stopping
any of the existing twelve runner/child processes. Focused regression reports
`19 passed`; PowerShell AST, Ruff, compileall and diff checks pass. An
operations scan briefly returned `ARTIFACT_STORAGE_TIMEOUT` but an immediate
retry completed with zero alerts; CO-149 tracks bounded transient timeout
classification.
## Continuous optimization CO-149 (2026-09-06)

MinIO bounded usage diagnostics now retry once only for failures classified as
retryable by the shared service-failure contract. A 50 ms bounded delay absorbs
transient list latency; authentication, missing-resource and other
non-retryable failures remain typed fail-closed with no fabricated usage.

The focused operations/storage/service-failure regression reports `29 passed`
with one pre-existing opt-in skip. Live same-stack diagnostics now return zero
alerts with MinIO `8,739/10,000` complete, PostgreSQL/Redis healthy, six idle
workers and no pool timeout. CO-150 tracks redaction of credential-bearing
Redis URLs in worker runtime manifests.
## Continuous optimization CO-150 (2026-09-06)

Worker runtime manifests no longer persist the complete Redis URL. Discovery
stores only bounded `redisIdentity` data (scheme, host, optional port and
numeric database), excluding userinfo, password, query string and raw URL.
All six active manifests were atomically rewritten; a sentinel scan found zero
forbidden fields, and all twelve worker processes remained alive.

Focused identity/queue regression reports `14 passed`; PowerShell AST, Ruff,
compileall and diff checks pass. CO-151 tracks explicit stale-manifest state
without destructive deletion when a queue is temporarily absent.
## Continuous optimization CO-151 (2026-09-06)

Worker discovery now gives runtime identity an explicit lifecycle state.
Active records are `RUNNING` with a fresh `lastSeenAt` and null `staleSince`;
records for temporarily missing queues are atomically rewritten as `MISSING`
while preserving the old identity and a bounded stale timestamp. No record is
deleted merely because a worker is absent. Live discovery remains 6/6 and all
12 worker processes stay running. CO-152 is the next exact rotation-helper
candidate.
## Continuous optimization CO-152 (2026-09-06)

Worker replacement now has a manifest-authorized dry-run helper. It validates
repository token, release SHA, child/runner existence and parentage, creation
FILETIMEs, executable/command digests, exact queue command and redacted Redis
identity. Apply is constrained to one queue and explicit `ShouldProcess`;
current qualification remained dry-run only.

Live validation covered all six queue manifests with all twelve worker PIDs
unchanged and no service stopped. Focused regression reports `16 passed`;
PowerShell AST, Ruff, compileall and diff checks pass. CO-153 tracks the
remaining replacement-health gate before an old pair may be stopped.
## Continuous optimization CO-153 (2026-09-06)

Worker Apply rotation no longer relies on a fixed delay. A replacement must be
found through its exact generated worker name and queue, then pass runner/child
parentage, Redis identity and live-process checks before the old pair can be
stopped. Admission failure leaves the old pair intact; a replacement found
before a later failure is revalidated by command digest before rollback.

Focused regression reports `16 passed`; PowerShell AST, Ruff, compileall and
diff checks pass. Live dry-run preserved all twelve current worker PIDs.
CO-154 tracks Redis/RQ registration health as the next admission layer.
## Continuous optimization CO-154 (2026-09-06)

Worker replacement admission now requires a redacted Redis/RQ registration
probe: exact worker name, exact single queue, `idle|busy` state and heartbeat
age within the existing 900-second operations contract. Rotation cleans the
verified old registration with `register_death`; a replacement discovered
before cutover can be unregistered on rollback. A log-runner command-line
matcher bug was fixed so the runner is not mistaken for the child.

Real single-queue replacement succeeded for `mdi-jobs`, changing
`18684/26300` to `29512/2972`; Redis/RQ returned to six workers, queue depth
was zero, and no service was stopped. Focused registration/rotation tests
report `7 + 16 passed`; PowerShell AST, Ruff, compileall and diff checks pass.
CO-155 tracks bounded last-known-complete MinIO observation state.
## Continuous optimization CO-155 (2026-09-06)

MinIO operations now retain the latest complete aggregate scan in a
thread-safe, endpoint+bucket keyed in-process cache for five minutes. A later
timeout keeps the current count/bytes null and `usageScanComplete=false`, while
optionally exposing a clearly non-authoritative last-known reference with age.
Expired references expose only an expiry marker. Storage budgets therefore
remain unknown whenever the current scan is incomplete.

Focused operations/storage/service-failure regression reports `33 passed` with
one opt-in skip; Ruff, compileall and diff checks pass. The API remains
PostgreSQL/Redis/MinIO-backed with six healthy workers. CO-156 is complete:
standalone CLI invocations use a protected SHA-256 keyed, atomic, TTL-bound
runtime observation file for continuity, while timeout snapshots remain
current-unknown and stale values are never promoted.

## Autonomous physical relocation — database boundary (2026-09-08)

The first physical move group separated database engine lifecycle from repository
composition while preserving `mdi_api.database`. Focused pool/configuration,
durable namespace, architecture guard/checker, six worker handlers, queue names,
and Tool/Adapter inventories pass. Pre-move broad backend baseline is
`2185 passed, 76 failed, 75 skipped`; the 45 generated phase12/phase13 evidence
changes from that run were restored before implementation.

## Autonomous physical relocation — Workspace projection (2026-09-08)

Workspace request/error and snapshot contracts now live under
`mdi_api.domain.workspaces`; the metadata-only projection/application service
now lives under `mdi_api.application.workspaces.projection`. The old
`mdi_api.workspaces` module is a three-symbol identity-preserving facade. Pure
workspace tests pass (`34 passed`); three API-backed nodes remain the exact
pre-move PostgreSQL/environmental baseline failures and are not new regressions.

## Autonomous physical relocation — Project history (2026-09-08)

`ProjectHistoryService` and its pure projection helpers now live at
`mdi_api.application.projects.history`; `mdi_api.project_history` remains a
true compatibility re-export. Historical schema/version, fallback, ordering,
and job/run identity behavior are unchanged. Focused Project history tests pass.

## Autonomous physical relocation — Scientific objects (2026-09-08)

Scientific-object contracts were moved to `mdi_api.domain.scientific_objects`,
the type registry to `mdi_api.infrastructure.scientific_objects`, and the
concrete SQLAlchemy/artifact-backed service to
`mdi_api.infrastructure.scientific_objects.service`. The implementation's
concrete dependencies make infrastructure the correct current authority; no
application-to-infrastructure allowlist was added. Legacy schemas/registry/service
modules and package exports preserve symbol identity. Focused Agent2 object,
registry, planning, result, and dataset tests pass (`16 passed`, 87 deselected).

## Autonomous physical relocation — Scientific results (2026-09-08)

Scientific-result contracts, relevance policy, and fingerprint helpers were
moved to `mdi_api.domain.scientific_results`; projector implementations moved
to `mdi_api.application.scientific_results.projectors`; committed-artifact loading
and the concrete snapshot/projection service moved to infrastructure. Existing
`mdi_api.scientific_results.*` modules remain compatibility facades, including
the frozen `worker.run_queued_result_projection` path. Focused result, closure,
domain, registry, and queue tests pass (`55 passed`).

## Autonomous physical relocation — Scientific reports (2026-09-08)

Scientific-report contracts and errors were moved to domain, deterministic input
assembly/composition/grounding to application, and concrete LLM client, queue,
request, and repository-backed service implementations to infrastructure. Frozen
prompt files remain at their established path and the relocated client resolves
that exact authority. Legacy package modules and worker paths remain compatible.
Focused report/queue/worker tests pass (`48 passed, 4 skipped, 5 deselected`).
