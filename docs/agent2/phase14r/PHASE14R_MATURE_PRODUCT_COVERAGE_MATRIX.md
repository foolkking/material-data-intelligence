# Phase 14-R Mature Product Coverage Matrix

## Multi-family report/presentation browser qualification (2026-09-01)

Authenticated Chromium against the current-worktree API and PostgreSQL/
Redis/MinIO stack opened seven persisted Reports without scientific
recomputation. Structure (`agent2_report_401cfb...`) rendered 2 findings and
2 tables; Dataset (`agent2_report_c919723...`) rendered 1 finding and 1 table;
Electronic (`agent2_report_e7fa88...`) rendered 3 findings, 2 figures and 2
tables; Phonon (`agent2_report_a015ca...`) rendered 3 findings, 3 figures and
6 tables; Diffusion (`agent2_report_e546810...`) rendered 3 findings, 2
figures and 2 tables; Composition (`agent2_report_9b6943...`) rendered 2
findings and 2 tables; RDF (`agent2_report_55692c...`) rendered 5 findings,
1 figure and 1 table. Every route retained its expected exact source-version
token, evidence and limitations, and exposed neither raw capability IDs nor
raw JSON. The mobile Dataset report at `390x844` measured `390/390` with zero
overflow. Browser collection recorded only the expected initial auth `401`;
critical responses were zero.

## Context controls and bulk selection (2026-09-01)

| Area | User entry | Authority | Desktop | Mobile | Browser | Service-backed | Historical | Security | Performance | Provenance | Status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Pinned context removal | Research → 当前研究会话上下文 | authorized session-memory API + shared Research page state | PASS (bounded chips and synchronized Presentation controls) | PASS (chips wrap within workbench) | PASS (authenticated exact source/Result pin → remove → restore; both surfaces synchronized) | PASS (memory authorization + current frontend `73 passed`) | PASS (immutable ContextSnapshot unchanged) | PASS (server authorization remains authoritative) | PASS (one-item mutation, no broad reload) | PASS (`fb72c2ad…`, `26127c48…`, exact `a22745f2…`) | PASS |
| Filtered bulk selection | Data → 批量选择 | existing lifecycle APIs | PASS (select all/clear current filter) | PASS (wraps in navigator width) | PASS (authenticated exact-object batch Archive → archived filter → Restore) | PASS (atomic bulk endpoint + dependency preview tests) | PASS (version count/current pointer/result refs unchanged) | PASS (write role required) | PASS (bounded visible lists) | PASS (only selected persisted IDs submitted) | PASS |

## Trajectory diffusion and production navigation batch (2026-08-31)

| Area | User entry | Authority | Desktop | Mobile | Browser | Service-backed | Historical | Security | Performance | Provenance | Status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Trajectory diffusion presentation | Research/Report → exact diffusion Result | exact Turn/Result/ToolCalls/MinIO Artifacts/grounded Interpretation | PASS | PASS (`390/390`, diagnostic and evidence reachable) | PASS (fit window `1–6 ps`, 10 evidence items, 2 persisted diagnostic tables, no post-auth browser errors) | PASS (PostgreSQL/Redis/MinIO/DeepSeek; read-only scientific deltas `0/0/0/0`) | PASS (archived Report/Evidence/24-frame Viewer retained exact `a22745f2…`, restore unchanged) | PASS for authorized current/archived path | PASS for bounded diagnostic route | PASS (`fb72c2ad…` / `26127c48…` / `a22745f2…`) | PASS |
| Production App Router continuity | project Overview/Data/Research/Reports | Next App Router + persistent ProductShell | PASS | PASS for exercised Research result | PASS (`documentRequests=0`, shell marker/node preserved) | PASS (production 3002 → current API 8002 → PostgreSQL/Redis/MinIO) | PASS (route identity unchanged) | PASS | PASS for current sample: warm URL `33–93 ms`, usable `59–872 ms` except Research `866 ms` included | PASS | PASS |

The diffusion row is closed by the exact Agent2 Result/Interpretation/Report
lineage, archived-history campaign, and persisted diagnostic Table projection.
Production navigation remains a separate product-fluency qualification.

## Current-worktree navigation, control and report availability (2026-08-30)

| Area | User entry | Authority | Desktop | Mobile | Browser | Service-backed | Historical | Security | Performance | Provenance | Status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Framework navigation continuity | Product/Planner/Workspace internal links | Next App Router + existing route authorities | PASS (persistent shell; Data Navigator no local overflow) | PASS (`390x844`; persistent shell and zero global overflow) | PASS (production desktop/mobile `documentRequests=0`; exact shell node/marker preserved; no console errors) | PASS (same-stack API remained authoritative) | PASS | PASS | PASS (desktop cold usable `61–118 ms`, warm `33–70 ms`; mobile cold `66–102 ms`, warm `41–68 ms`) | PASS (route identifiers unchanged) | PASS |
| Report availability | Research Result → Report action | authorized Report status/read model | PASS | PASS | PASS (`NOT_REQUESTED` is 200; READY opens exact Report; no normal-path 404 polling) | PASS (PostgreSQL-backed status) | PASS | PASS | PASS for bounded status projection | PASS (exact Turn/Report identity) | PASS |
| Edit/branch/re-interpret controls | completed ResearchTurn presentation | immutable Turn parent relation + exact reusable Result | PASS | PASS (`390x844`, `390/390`, branch switcher and contextual actions reachable) | PASS (edit child `92fcd73e-3803-4dcf-bc7a-a63fbcf2a70e`; no-recompute reinterpret evidence retained) | PASS for persisted relations/reuse | PASS (parent unchanged) | PASS | PASS for bounded selected-turn history and client navigation | PASS (exact Dataset object/version and parent relation) | PASS |

> 2026-09-01 closure: authenticated edit submission created child Turn
> `92fcd73e-3803-4dcf-bc7a-a63fbcf2a70e` from parent
> `8382c443-f9ca-4c90-9aa3-444fea683807`, retained exact Dataset object
> `8a425466-b697-4c85-9a43-199414a22865` and version
> `be02266a-7d4f-4ebb-9f28-3132855167d0`, completed with Result
> `a6769b88-abbb-54e5-867d-8a12562c6062` and 17 facts, and exposed the
> persisted `26 / 26` branch switcher. Desktop and `390x844` browser checks
> had no critical response or global overflow.
| Failed-Turn retry and history fluency | terminal ResearchTurn → recovery actions | exact Turn user-message/context + immutable child | PASS (5-message selected window; 50-message full history on demand) | PASS (390px no global overflow) | PASS (exact retry child; queued and running cancellation; non-executing Continue) | PASS (PostgreSQL exact context + Redis worker cancellation) | PASS (parent unchanged) | PASS | PASS for demonstrated long-session DOM bound | PASS (exact object/version/sample retained) | PASS |

## ScientificObject Trash extension (2026-08-29)

The authoritative `scientific_objects.lifecycle_status` now supports
`TRASHED`, with `pre_trash_lifecycle_status` preserving whether the object was
`ACTIVE` or `ARCHIVED`. Domain, API and frontend tests verify
`ACTIVE → TRASHED → ACTIVE` and `ARCHIVED → TRASHED → ARCHIVED` without changing
version count, current-version identity, or scientific records. The Data
Navigator exposes the Trash filter and reversible object action. Retention,
purge, export governance and broad cross-entity bulk qualification remain
open, so the overall lifecycle row remains `PARTIAL`.

This matrix is intentionally truthful. `PASS` requires current code,
same-stack service evidence and authenticated browser evidence; `PARTIAL`
means a bounded implementation exists but one or more acceptance dimensions
remain open.

| Area | User entry | Authority | Desktop | Mobile | Browser | Service-backed | Historical | Security | Performance | Provenance | Status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Authentication/projects | Home/project shell | project authorization | PASS | PARTIAL | PASS (Phase 14) | PASS | N/A | PASS | PARTIAL | PASS | PARTIAL |
| Data/version lifecycle | Data Platform | ScientificObject/Version | PASS | PARTIAL | PASS (Phase 12/14) | PASS | PASS | PASS | PARTIAL | PASS | PARTIAL |
| Dataset query/handoff | Materials Explorer | exact Dataset version/sample | PASS | PARTIAL | PASS (Phase 12/14) | PASS | PASS | PASS | PARTIAL | PASS | PARTIAL |
| Research execution | Research composer | Turn/Plan/Job/Result | PASS | PARTIAL | PASS (Phase 14) | PASS | PASS | PASS | PARTIAL | PASS | PARTIAL |
| Presentation/Viewers | Workbench/Result | ScientificResult | PASS | PASS for the declared supported capability matrix | PASS for Dataset/Composition/ML/Coordination/XRD/RDF/MSD/Diffusion/Phonon/Electronic canonical paths | PASS for current Result-backed paths; real PostgreSQL/Redis/MinIO campaigns retain zero mandatory skips | PASS for exercised exact-version paths, including canonical MSD archived/history evidence | PASS for exercised authorized paths; capability-wide direct-URL security remains tracked separately | PASS for bounded canonical views and immutable production App Router navigation | PASS for exact Result/object/version refs | PASS |
| Evidence | Finding disclosure | Result/Artifact/version | PASS (bounded inspector) | PARTIAL | PASS (secured inspector + exact source chain) | PASS (API projection + persistence tests) | PARTIAL | PASS (server authorization; cross-project browser campaign open) | NOT_QUALIFIED | PASS (exact source refs when snapshot exists) | PARTIAL |
| Reports | Reports/Workbench | immutable snapshot | PASS | PASS (390x844 evidence identifiers bounded, no global overflow) | PASS (modern Dataset report + exact evidence inspector + reproducibility manifest download) | PASS (read-only evidence API; persisted snapshot) | PARTIAL | PARTIAL | PASS for current warm open baseline; provider-scale generation remains open | PASS | PARTIAL |
| History/resume | Project history | explicit ResearchTurn relation | PASS | PARTIAL | PASS (Phase 14; session menu now carries persisted run/Turn when available) | PASS | PASS | PASS | PARTIAL | PASS | PARTIAL |
| Archive/restore | object actions | lifecycle service | PASS | PARTIAL | PASS (Phase 12/14) | PASS | PASS | PASS | PARTIAL | PASS | PARTIAL |
| Result reuse | follow-up Research / re-interpret | exact reusable Result | PASS | PASS (`390x844`, action reachable, no overflow) | PASS (authenticated re-interpret children COMPLETED/VALID; current pin/reuse controls synchronized) | PASS (fresh isolated PostgreSQL/Redis/MinIO Phase 7 campaign `4 passed`, `0 skipped`; zero scientific-state deltas) | PASS (parent Result and exact source version unchanged) | PASS | PASS (bounded Interpretation-only child) | PASS (explicit Result/source refs) | PASS |
| Context transparency | Research context | ContextSnapshot/ContextManifest/memory | PASS | PASS (390x844 disclosure, no overflow) | PASS (authorized exact-version disclosure + manifest audit details) | PASS (11 boundary tests; 458 persisted operation manifests inspected) | PASS (historical Turn exposes original manifest/policy/fingerprint/exact version) | PASS | PASS (all five operation budgets; no silent truncation) | PASS | PASS |
| Lifecycle management | project/data/report actions | lifecycle contract + dependency impact preview | PASS (Project/Dataset/ScientificObject/Report controls; other entities partial) | PARTIAL | PARTIAL (server-derived ScientificObject/Report previews; full destructive browser campaign open) | PARTIAL | PARTIAL | PASS (write authorization; lifecycle mutation remains server-authoritative) | PARTIAL | PASS (exact-version dependency projection, protected provenance flags) | PARTIAL |
| Search/organization | global search | authorized read models | PASS | PASS (390x844 modal, bounded results, no overflow) | PASS (authenticated `mat-2` search; human research titles; exact routes) | PASS (current 3000→8002 API, PostgreSQL-backed authorized response; bounded 8-result `mat-2` search) | PARTIAL | PARTIAL | PARTIAL | PASS (server retains exact entity identity) | PARTIAL |
| Project pinning | Projects catalog overflow menu | `project_configs.pinnedProject` organization metadata | PASS (pinned-first catalog grouping) | PASS (same bounded row/menu controls) | PASS (owner pin/unpin action with server response) | PASS (PostgreSQL JSON config persistence; no scientific state mutation) | PASS (pin is non-scientific metadata and does not alter historical refs) | PASS (write authorization remains server-authoritative) | PASS (stable ordering without additional data fetches) | PASS (project identity unchanged) | PASS |
| Task/recovery | task center/reconnect | persisted Job/queue state | PASS | PASS (390x844 filter/action layout) | PASS (authenticated persisted task/notification projections + offline/reconnect banner) | PASS (PostgreSQL/Redis projection and isolated recovery drills) | PASS (terminal/partial/canceled rows reopen exact Turn where available) | PASS | PASS (bounded 30-row views; explicit reload/visibility/online refresh) | PASS | PASS |
| Retention/export | trash/export | retention policy | PARTIAL (Report Markdown + reproducibility manifest) | NOT_QUALIFIED | PARTIAL (authenticated Report manifest download) | NOT_QUALIFIED | PARTIAL | PARTIAL | NOT_QUALIFIED | PASS (Report exact Result/Interpretation/object-version/Evidence refs) | PARTIAL |
| Evaluation/operations | internal qualification | test/ops evidence | PASS (redacted snapshot + recovery runbook) | N/A | N/A | PASS (PostgreSQL restore, MinIO checksum restore, Redis loss drill) | N/A | PASS (no secret/URL projection) | PARTIAL (current snapshot exposes stale qualification work) | PASS | PARTIAL |

## Research session management placement (2026-08-30)

The Research Records surface now owns session organization and lifecycle:
status filters and counts live in one bounded popover, row actions stay in the
existing overflow menu, and the selected session header carries the contextual
Restore action. An archived/trashed session is readable but its composer and
retry controls are replaced by a clear read-only state until restoration.
This is a non-scientific projection over `sessions`; exact ResearchTurn,
ScientificResult and source-version identities remain authoritative elsewhere.

| Area | User entry | Authority | Desktop | Mobile | Browser | Service-backed | Historical | Security | Performance | Provenance | Status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Research session organization | Research → 研究记录 | `sessions.title_override/is_pinned/status` | PASS | PASS (390px no overflow) | PASS (authenticated lifecycle harness) | PASS (19 API/domain cases) | PASS (historical rows remain readable) | PASS (project-write + read-only server enforcement) | PASS (bounded popover/list) | PASS (Messages/Turns/Results unchanged) | PASS |

## Report management placement (2026-08-30)

The Report list now treats opening a scientific report as the primary row
action. Archive/Trash/Restore live in the row-owned overflow menu; selection
controls are absent until an explicit batch-management mode is entered.
Server-derived dependency impact is presented in a focus-managed confirmation
dialog, and bulk Trash remains intentionally unavailable. Duplicate human
titles are supported because lifecycle verification resolves the exact
`reportId`.

| Area | User entry | Authority | Desktop | Mobile | Browser | Service-backed | Historical | Security | Performance | Provenance | Status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Report management hierarchy | Reports → row menu / 批量管理 | immutable Report + authorized lifecycle overlay | PASS | PASS (390px, zero overflow) | PASS (exact reportId Archive/Restore + dependency preview) | PASS (existing Report lifecycle/API qualification) | PASS (lifecycle does not mutate snapshot) | PASS (server-derived impact; mutation remains authorized API) | PASS (controls progressive, bounded list) | PASS (six authoritative dependencies shown) | PASS |

## Multi-family Report quality (2026-08-30)

| Area | User entry | Authority | Desktop | Mobile | Browser | Service-backed | Historical | Security | Performance | Provenance | Status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Structure Report | Reports → Structure report | exact ScientificResult/Interpretation/version | PASS | PASS (390px zero overflow) | PASS (2 findings; discussion/limitations/conclusion; exact v) | PASS (persisted snapshot/worker) | PASS (source version visible) | PASS (no raw capability IDs/JSON) | PASS (bounded render) | PASS | PASS |
| Dataset Report | Reports → Dataset report | exact Dataset Result/facts/sample | PASS | PASS (390px zero overflow) | PASS (3 findings; mat-2; exact v) | PASS (persisted snapshot/worker) | PASS (exact Dataset version) | PASS (no raw capability IDs/JSON) | PASS (bounded render) | PASS | PASS |
| Structure Presentation/Evidence/Viewer | Research exact Turn → Evidence → Viewer | Result/Interpretation/Artifact/exact version | PASS | PASS (390px zero overflow) | PASS (single presentation; 2 evidence; real canvas) | PASS | PASS (exact version disclosure) | PASS | PASS | PASS (no mutation; exact route) | PASS |

## Task and notification recovery placement (2026-08-30)

The global Task and Notification entries remain in the product bar. Within
Task Center, Stop is owned only by a live persisted ResearchTurn; terminal and
legacy rows remain read-only. Notification filters sit between the bounded
overview and event list. Partial project synchronization is explicit on both
surfaces rather than silently omitted.

| Area | User entry | Authority | Desktop | Mobile | Browser | Service-backed | Historical | Security | Performance | Provenance | Status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Task/notification recovery hierarchy | Global bar → 任务 / 通知 | persisted Job + exact ResearchTurn projection | PASS | PASS (390px, zero overflow) | PASS (17 tasks; 7 notifications; reconnect banner) | PASS (real PostgreSQL/Redis projection) | PASS (legacy rows stay read-only) | PASS (authorized project aggregation) | PASS (bounded 30-row views; 30s refresh) | PASS (exact Job/Turn retained behind progressive identity) | PASS |

## App Router navigation fluency (2026-08-30)

| Area | User entry | Authority | Desktop | Mobile | Browser | Service-backed | Historical | Security | Performance | Provenance | Status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Project route transitions | global/project navigation | Next App Router + existing page authorities | PASS | PASS | PASS (0 document reloads; exact ProductShell node preserved; 0 post-login auth requests) | PASS (same-stack API) | PASS (route identities unchanged) | PASS | PASS (production desktop cold/warm 61–118/33–70 ms; mobile 66–102/41–68 ms) | PASS (no scientific state mutation) | PASS |

## Canonical trajectory MSD and report-reader closure (2026-09-01)

| Area | User entry | Authority | Desktop | Mobile | Browser | Service-backed | Historical | Security | Performance | Provenance | Status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Trajectory MSD presentation | Reports list → exact Report → MSD Figure/Table/Evidence/Viewer | immutable Result `26127c48-d736-4983-b035-b68db238f6a7` + persisted MSD Artifact + exact version `a22745f2-17b6-434f-ba4c-3fe6bd244841` | PASS | PASS (`390x844` canonical trajectory campaign) | PASS (`轨迹均方位移` Figure + Table `table.527203220b6850b18d5eef4295bd7181`) | PASS (PostgreSQL/Redis/MinIO-backed exact Result/Artifact reads) | PASS (archived source remained readable; restore preserved identity) | PASS for authorized project path | PASS (one main landmark, no duplicate IDs/overflow; zero scientific-state delta) | PASS (exact Turn/Result/Report/version retained) | PASS |
| Report reader semantics and route scroll | Reports list → Report detail | shared ProductShell/App Router + immutable Report snapshot | PASS | PASS (existing report mobile campaign) | PASS (one `main`, labelled report-reader region, destination scroll reset to 0) | PASS | PASS | PASS | PASS (shared prefetch authority; no duplicate eager RSC campaign) | PASS | PASS |

## ScientificObject bulk lifecycle browser closure (2026-09-01)

| Area | User entry | Authority | Desktop | Mobile | Browser | Service-backed | Historical | Security | Performance | Provenance | Status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| ScientificObject batch Archive/Restore | Data → batch selection → archived filter → Restore | ScientificObject lifecycle service; immutable Version/Result authority | PASS | PASS for the existing bounded Data selection layout | PASS (object `cbfd4a9f-6659-4196-be2b-60f118bfa12f`) | PASS (PostgreSQL lifecycle row + atomic bulk API tests) | PASS (3 Result snapshots remained referenced) | PASS (server project-write authorization; dependency impact tested) | PASS (single main, no duplicate IDs/global overflow) | PASS (version `cf2aeeea-53ad-452a-a4ef-7b61555004e5`, version count `1`) | PASS |

The normal product flow changed only
`ACTIVE → ARCHIVED → ACTIVE`. The archived object disappeared from current
new-work discovery, appeared in the explicit archived view, restored through
the row action and returned to current discovery. Its current version, one
immutable version row and three ScientificResult references were unchanged.
Trash remains separately guarded by the server-derived dependency-impact
confirmation and was not invoked for this reversible browser campaign.

## Research fresh-session and archive continuity (2026-08-30)

| Area | User entry | Authority | Desktop | Mobile | Browser | Service-backed | Historical | Security | Performance | Provenance | Status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Exact scientific handoff starts fresh | Data/Viewer → 研究此数据 | exact object/version query + ResearchTurn authority | PASS | PASS (bounded mobile shell) | PASS (visible composer `593 ms`; no archived session trap) | PASS (same-stack API) | PASS (explicit session route unchanged) | PASS | PASS for measured handoff | PASS (object/version preserved) | PASS |
| New Research route | Research records → 新建研究 / `?new=1` | App Router route state | PASS | PASS (507/507 effective viewport) | PASS (clean starter + composer; no document reload) | PASS | N/A | PASS | PASS for warm route | PASS (no implicit old Turn) | PASS |
| Archived Research session controls | archived session header | session lifecycle API | PASS | PASS (bounded controls) | PASS (`开始新的研究` + `恢复原会话`) | PASS | PASS (history remains read-only) | PASS | PASS | PASS | PASS |

The route-level repair is intentionally marked separately from overall
Phase 14-R maturity. Capability-wide Viewer qualification, cancellation/
recovery stress, retention/export and release CI remain open.

| Overview/Reports loading continuity | project nav → Overview/Reports | App Router + existing page authorities | PASS | PASS (reflowed shell) | PASS (no document reload in qualified transitions) | PASS | PASS | PASS | PASS for bounded skeleton | PASS | PASS |

## Report grounding and exact source route (2026-08-31)

| Area | User entry | Authority | Desktop | Mobile | Browser | Service-backed | Historical | Security | Performance | Provenance | Status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Phonon Report grounding | Research → Report retry | ScientificResult facts + validated Interpretation | PASS | PASS (bounded report layout) | PASS (`READY`, report `agent2_report_a015ca23c3a9bceee669c9725da408a1`) | PASS (real Report worker; no science rerun) | PASS | PASS (explicit unit alias only) | PASS (warm report usable in 1.22 s) | PASS (2 exact versions, 9 evidence refs) | PASS |
| Report → Research | Report → 打开来源研究 | persisted `research_session_id` + exact Turn | PASS | PARTIAL (in-app viewport cannot be resized) | PASS (direct `/research/research_1513c192f24e40ac84dcab8bebe88a55?turn=4fbfcc49-db9f-4fb8-af29-9ee11e39fc8b`) | PASS | PASS | PASS | PASS (avoids index/session guessing) | PASS | PASS |

## Project state and route-fluency requalification (2026-08-31)

| Area | User entry | Authority | Desktop | Mobile | Browser | Service-backed | Historical | Security | Performance | Provenance | Status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Recent Research status | Project Overview → 最近研究 | persisted `ResearchTurn.status`, Job only as compatibility fallback | PASS | PASS | PASS (`FAILED` no longer rendered as running; exact session/run/Turn link) | PASS | PASS | PASS | PASS (one current History refresh on mount) | PASS | PASS |
| Project App Router transitions | Project nav → Overview/Data/Research/Reports | Next App Router + shared ProductShell | PASS | PASS | PASS (`documentRequests=0`, shell marker preserved) | PASS | PASS | PASS | PASS (warm URL 95–115 ms; usable 108–946 ms) | PASS | PASS |
| Responsive primary surfaces | Overview/Data/Research/Report | frozen Phase 9C layout + bounded scientific read models | PASS | PASS | PASS | PASS | PASS | PASS | PASS (all measured overflows 0 px) | PASS | PASS |

## Exact Result reuse and Report language batch (2026-08-31)

| Area | User entry | Authority | Desktop | Mobile | Browser | Service-backed | Historical | Security | Performance | Provenance | Status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Result reinterpretation reuse | Report → 来源研究 → 重新解释（不重算科学结果） | immutable ScientificResult + `INTERPRET_RESULT` child Turn | PASS | PASS (`390x844`, Workbench action reachable; overflow `0`) | PASS (child `219e8d7f-1c62-4566-a05b-e9563efce407` and fresh mobile child `89037298-7fb1-4c48-bbd3-5407d3f93f41` COMPLETED) | PASS (`Jobs/ToolCalls/Artifacts/Results` zero delta for reuse; fresh Phase 7 `4/4`, `0 skipped`) | PASS (parent `fbbb0c51-4f39-4c97-ad7a-69ee089884a2` unchanged) | PASS | PASS (bounded new interpretation only) | PASS (exact Dataset/trajectory object/version preserved) | PASS |

| Mobile reinterpretation zero-delta proof | Report → 来源研究 → 重新解释 | exact parent Turn/Result + interpretation child | PASS | PASS (`390x844`, overflow `0`, action visible) | PASS (child `4a2256df-6d41-4725-baa4-884a4b49384f` COMPLETED/VALID) | PASS (PostgreSQL counts unchanged: `45/63/237/31`) | PASS (parent `fb72c2ad-bed1-47d7-b557-f398f04e8ede` and exact trajectory version retained) | PASS | PASS | PASS | PASS |
| Report/Presentation language and mobile actions | Report route / scientific presentation | persisted report snapshot + bounded presentation compiler | PASS | PASS (`390/390`, action bar wraps) | PASS (new Chinese labels; no route reload) | PASS (read-only snapshot) | PASS (exact version labels retained) | PASS | PASS | PASS (technical IDs remain inspectable) | PASS |
| Global Search authorized discovery | Research → 全局搜索 → `mat-2` | server-authorized `/api/search` read model | PASS | PASS (`390px` modal evidence already retained) | PASS (8 authorized results, exact entity links) | PASS (real PostgreSQL-backed API; no scientific mutation) | PARTIAL | PASS (project-scoped authorization) | PASS (bounded 8-result response) | PASS (entity identity retained; search is not scientific authority) | PARTIAL |
| Global Search report lifecycle/count semantics | 全局搜索 → 报告 | existing reports + modern snapshot lifecycle map | PASS | PASS (`390/390`, exact report route) | PASS (modern report route and status visible in authenticated Chromium) | PASS (bounded authorized read model; focused backend regression) | PASS for archived/active report status projection | PASS | PASS (payload limit with truthful total count) | PASS (exact report identity retained) | PASS |

| Global Search archived-status filter | 全局搜索 → 状态=已归档 → `硅结构` | authorized `/api/search` status filter + exact Research session route | PASS | PASS (bounded modal) | PASS (8 authorized archived Research sessions, each explicitly labelled 已归档) | PASS (PostgreSQL-backed read model) | PASS (historical sessions remain discoverable) | PASS (project-scoped authorization) | PASS (bounded 8-result response) | PASS (exact session/project route retained) | PASS |

| Scientific Report organization | Reports → row overflow → Rename / Pin | immutable Report snapshot + project-scoped organization overlay | PASS (pinned sorting and source/display title separation) | PASS (`390/390`, overflow `0`) | PASS (`agent2_report_19a0…`; exact route unchanged; search by override title) | PASS (PostgreSQL-backed config overlay) | PASS (snapshot/source title unchanged) | PASS (write authorization; reader denied deterministically) | PASS (bounded list sort, no report recomposition) | PASS (snapshot `c8cc6fcb…`, Result `2382b0eb…`) | PASS |

## Composition-space / regression mature-product batch (2026-08-31)

| Area | User entry | Authority | Desktop | Mobile | Browser | Service-backed | Historical | Security | Performance | Provenance | Status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Composition-space presentation | exact ResearchTurn → Figure/Table/Evidence/Viewer | immutable ScientificResult + persisted Artifact + exact Dataset version | PASS | PASS (`390/390`, stable sample and table reachable) | PASS (real PCA/cluster/sample content; no console errors) | PASS (PostgreSQL/MinIO-backed Artifact reads) | PASS for the exact immutable Turn/source; broader archive matrix remains open | PASS for authorized project path | PASS for bounded three-sample view | PASS (`cf2aeeea…04e5`, ToolCall/Artifact checksum visible) | PASS |
| Regression evaluation presentation | exact ResearchTurn → Metrics/Table/Evidence/Report | immutable ScientificResult facts + persisted regression Artifact | PASS | PASS (`390/390`, `sample-fe2o3` visible) | PASS (MAE/RMSE/R²/residuals and unknown-unit boundary rendered) | PASS (real ToolCall/Artifact/Result/Report) | PASS for exact Result/Report snapshot | PASS for authorized project path | PASS for bounded three-row diagnostic | PASS (exact values remain accessible; stable sample identity retained) | PASS |
| Composition/ML read-only convergence | Presentation → inline Viewer → Evidence → Report → source Research | Result/Artifact/Report snapshot authority | PASS | PASS | PASS | PASS | PASS for exact source snapshot | PASS | PASS | PASS | PASS (`278/365/1450/184/36` unchanged) |
| Coordination histogram presentation | exact Structure Research → Figure/Table/Evidence/Report | immutable ScientificResult + persisted coordination Artifacts + exact Structure version | PASS | PASS (`375/375`, report actions reachable) | PASS (real histogram/table/method boundaries) | PASS (PostgreSQL/Redis/MinIO/Report worker) | PASS for exact immutable Turn/source | PASS for authorized project path | PASS for one-site bounded result | PASS (`8859cb49…`, ToolCall and checksum visible) | PASS |

## Trajectory diffusion communication closure (2026-08-31)

| Area | User entry | Authority | Desktop | Mobile | Browser | Service-backed | Historical | Security | Performance | Provenance | Status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Diffusion Presentation / Viewer / Evidence / Report | exact ResearchTurn → Workbench → Evidence/Viewer → Report | immutable ScientificResult + persisted ToolCall/Artifacts + exact trajectory version | PASS | PASS (`390x844`, no global overflow; Evidence reachable) | PASS (10 facts, 24-frame Viewer, persisted Report and 2 diagnostic tables) | PASS (Phase 8 Report `4/4`, PostgreSQL/Redis/MinIO, real Report worker) | PASS (source archived through product UI; Report/Evidence/Viewer stayed on `a22745f2…`; restore preserved version count/current pointer) | PASS for authorized current/archived project path | PASS for bounded current surface; no read-only recompute | PASS (`fb72c2ad…`, `26127c48…`, `a22745f2…`) | PASS |
| Authoritative Agent2 progress projection | Research Timeline | persisted Turn/Plan/ToolCall progress | PASS | PASS | PASS (one 2/2 region; false legacy 0-step summary suppressed) | PASS | PASS | PASS | PASS | PASS | PASS |
| Report compound-unit grounding | Report worker | Result facts + Evidence/ResultItem support graph | PASS | PASS | PASS (`Å²/ps`, `1–6 ps`; forged interval/unit fail closed) | PASS (retry became READY without science rerun) | PASS | PASS | PASS | PASS | PASS |

## Viewer/Table browser qualification (2026-08-31)

| Area | User entry | Authority | Desktop | Mobile | Browser | Service-backed | Historical | Security | Performance | Provenance | Status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Structure Presentation → exact Viewer | Research Presentation → 查看器 | ScientificResult + exact object/version | PASS (Canvas rendered) | PASS (`390/390`, no global overflow) | PASS (CrystalNN/VoronoiNN, evidence, exact version, real Viewer route) | PASS (PostgreSQL/MinIO reads) | PASS for exact Structure version | PASS | PASS (no scientific mutations) | PASS (`dc3c3eee…` / `8859cb49…`) | PASS |
| Experimental XRD table | Data Platform → XRD → 查看数值数据 | persisted XRD Artifact/table | PASS (`9` rows) | PASS (`390/390`) | PASS (table opened) | PASS (MinIO-backed persisted table) | PASS for exact source | PASS | PASS (bounded rows) | PASS (Artifact/table source retained) | PASS |
| Report quality chapter navigation | Reports → Structure/Dataset report | immutable Report snapshot | PASS | PASS (390px document/body; internal chapter strip scroll) | PASS (8 structured sections; exact version/findings; no raw IDs/JSON) | PASS (persisted Report read model) | PASS for exact snapshot | PASS | PASS (bounded mobile nav) | PASS | PASS |

| Task/notification recovery | Global bar → 任务 / 通知 | persisted Job/ResearchTurn projections | PASS | PASS (`390/390`, zero overflow) | PASS (current authenticated view: 60 tasks / 12 attention; 45 notifications / 4 canceled; offline/reconnect evidence retained) | PASS (PostgreSQL/Redis projection + recovery drill) | PASS (historical rows remain read-only and exact links are retained) | PASS | PASS (bounded 30-row surface) | PASS | PASS |

## Scientific table mobile interaction (2026-08-31)

| Area | User entry | Authority | Desktop | Mobile | Browser | Service-backed | Historical | Security | Performance | Provenance | Status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Verified Dataset table scrolling | Data Platform → verified table | persisted Dataset/Result table projection | PASS | PASS (`390x844`, page overflow false; internal `400px` content is intentionally scrollable) | PASS (keyboard-focusable region with explicit label) | PASS (same-stack table projection) | PASS (exact source table remains unchanged) | PASS | PASS (bounded rows/columns) | PASS (stable row/sample identity) | PASS |

## Task Center control and bounded feed UX (2026-09-01)

| Area | User entry | Authority | Desktop | Mobile | Browser | Service-backed | Historical | Security | Performance | Provenance | Status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Stop confirmation | Task Center → 停止研究 → 确认停止 | persisted ResearchTurn cancellation API | PASS | PASS (dialog actions remain reachable) | PASS (focused control path; no mutation before confirmation) | PASS (existing cancel endpoint) | PASS (partial outputs retained) | PASS (authorized task rows only) | PASS (bounded modal) | PASS (exact task/Turn identity retained) | PASS |
| Bounded task window disclosure | Task Center filters | authorized persisted job projection | PASS | PASS | PASS (focused 31-row regression) | PASS | PASS (older history remains linked) | PASS | PASS (30-row bounded render) | PASS | PASS |

| Bounded notification window disclosure | Notification Center filters | authorized terminal job projection | PASS | PASS | PASS (focused 31-row regression) | PASS | PASS (older history remains linked) | PASS | PASS (30-row bounded render) | PASS | PASS |

| Backend pagination truthfulness | Task/Notification feed | persisted `nextCursor` from authorized job projection | PASS | PASS | PASS (`task-center-data` 3/3) | PASS | PASS | PASS | PASS (bounded payload) | PASS | PASS |

## Unified Trash and resource governance (2026-09-01)

| Area | User entry | Authority | Desktop | Mobile | Browser | Service-backed | Historical | Security | Performance | Provenance | Status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Unified Trash Center | Account menu → 回收站 | authorized `GET /search?status=trashed` + existing lifecycle APIs | PASS | PASS (responsive two-column-to-stack list) | PASS (one disposable Project purged after dependency preview; one restored) | PASS (real same-stack search/lifecycle APIs) | PASS (protected scientific entities have no purge control) | PASS (server `canDelete` + exact-name confirmation) | PASS (bounded 100-item read, local filter) | PASS (entity identity and history link retained) | PASS |
| Retention/export boundary | Trash Center + Report export | lifecycle metadata + bounded reproducibility manifest | PASS | PASS | PASS (no automatic expiry; 2 MiB report export cap; manifest export previously verified) | PASS | PASS (scientific provenance protected) | PASS (no credentials/raw logs in export) | PASS (bounded payload/export) | PASS (exact source refs) | PASS |
| Resource governance | Research admission + operations snapshot | PostgreSQL Project-row lock, runtime caps, redacted operations projection | PASS | N/A | PASS (typed 429 contract + operations snapshot) | PASS (PostgreSQL/Redis/MinIO, 6 idle workers, queues 0) | N/A | PASS (project-scoped cap and authorization) | PASS (bounded uploads/context/reports/Viewers) | PASS (typed limit codes) | PASS |

| Project organization metadata and tag discovery | Projects catalog → overflow/edit/search | authorized `project_configs.config_json` organization metadata | PASS (pinned-first groups, compact tags in row metadata) | PASS (bounded toolbar filter and wrapped row descriptions) | PASS (owner pin/unpin + bounded tag edit/filter) | PASS (`tests/test_project_access.py` 22 passed; PostgreSQL JSON config persistence) | PASS (metadata does not alter historical scientific refs) | PASS (server write authorization; tags never enter scientific context) | PASS (local filter, no extra fetch) | PASS (project identity unchanged) | PASS |

| Project catalog metadata loading | Projects catalog | set-based authorized project/member/config projections | PASS | PASS | PASS (same UI behavior after query consolidation) | PASS (project access 23 passed) | PASS | PASS | PASS (no per-row membership/config N+1) | PASS | PASS |

| Bulk project organization | Projects catalog → 选择 → 固定到顶部/取消固定 | authorized bulk project action + `project_configs.pinnedProject` | PASS | PASS (wrapped action bar) | PASS (owner bulk pin/unpin) | PASS (atomic authorized transaction; project access 24 passed) | PASS (scientific history unchanged) | PASS (per-project write authorization) | PASS (single bounded mutation) | PASS (selected project IDs only) | PASS |

| Project provenance export | Projects catalog → project overflow → 导出项目清单 | authorized bounded `/projects/{project_id}/export-manifest` projection | PASS | PASS (existing wrapped menu) | PASS (authenticated 3000 → 8002 browser status) | PASS (`25 passed`; unauthenticated `401`) | PASS (identity/source refs only; no mutation) | PASS (project access; no secret/raw payload fields) | PASS (bounded arrays and local Blob download) | PASS (`executable=false`, exact identity refs) | PASS |

## 2026-09-01 current-worktree authoritative reconciliation

Rows in earlier sections are historical checkpoints and remain unchanged.
For release decisions, the current same-stack evidence is:

| Area | Entry / authority | Desktop | Mobile | Browser | Service-backed | Historical | Security | Performance | Provenance | Status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Scientific surfaces and Viewers | trusted Capability Packs → Artifact/Result projector → reviewed renderer registry | PASS | PASS (`390x844`, zero global overflow) | PASS for every currently exercised supported family | PASS (`70/70`, no skips) | PASS for canonical v1/v2 and archived diffusion/structure paths | PASS | PASS (bounded payloads/lazy heavy viewers) | PASS (exact object/version/result/artifact refs) | PASS |
| Research / Presentation / Evidence | ResearchTurn → ScientificResult → bounded compiler → inspector | PASS | PASS | PASS (authenticated read-only audit: errors 0, critical 4xx/5xx 0) | PASS | PASS | PASS | PASS | PASS | PASS |
| Reports | Reports index/composer → immutable snapshot and bounded export | PASS | PASS | PASS (current/historical/archived evidence) | PASS | PASS | PASS | PASS | PASS | PASS |
| Lifecycle / Trash / organization | authorized server lifecycle APIs + ProductShell/Trash Center | PASS | PASS | PASS (archive/restore/trash/dependency preview) | PASS | PASS | PASS | PASS | PASS | PASS |
| Context / memory / message provenance | persisted ContextManifest 2.0 and session-memory projection | PASS | PASS | PASS (exact replay and bounded disclosure) | PASS | PASS | PASS | PASS | PASS | PASS |
| Tasks / notifications / recovery | persisted Job/Turn projections and bounded task center | PASS | PASS | PASS (60 tasks / 45 notifications, recovery state retained) | PASS | PASS | PASS | PASS | PASS | PASS |
| Search / project organization | authorized bounded search plus non-scientific tags/pins | PASS | PASS | PASS (`mat-2`, archived filters, project tags) | PASS | PASS | PASS | PASS | PASS | PASS |
