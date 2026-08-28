# Phase 14-R Product Reality Audit

Date: 2026-08-28  
Verified base: `e22a732` (Phase 14-R fix-forward worktree; historical Phase 14
seal `d03b0a2e86e50d834a774cf823cfe055c91cf10c` preserved)  
Branch: `master` (`HEAD` is ahead of the historical seal; release CI has not
yet been run for Phase 14-R)  
Runtime: `/health/runtime` verified PostgreSQL + Redis + MinIO + Redis worker +
configured DeepSeek; Phase 15: not created or started.

This is a code-and-runtime grounded baseline. `PARTIAL` and
`NOT_QUALIFIED` are intentional: they mean that a capability exists in code
or was qualified in an earlier phase, but the Phase 14-R product-wide
acceptance evidence is not yet complete.

## Frozen authority map

| Area | Evidence | Status |
| --- | --- | --- |
| Logical scientific identity | `apps/api/mdi_api/db.py`, `agent2_repositories.py` (`scientific_objects`) | PASS |
| Immutable scientific state | `scientific_object_versions` tables and version services | PASS |
| Scientific fact authority | `apps/api/mdi_api/scientific_results/`, result snapshots, Phase 13 evidence | PASS |
| Presentation as derived communication | `apps/api/mdi_api/presentation.py`, `apps/web/app/components/ScientificPresentationBlocks.tsx` | PASS |
| Exact-version Viewer resolution | `apps/api/mdi_api/scientific_viewers/`, workspace source summaries | PASS |
| Trusted Capability Packs | `research_agent/capabilities/{packs,defaults,registry}.py`, Phase 11 tests | PASS |
| Raw Tool exposure | pack/registry validation and Phase 11 regression | PASS |

## Product-surface reality

| Surface | Current evidence | Status |
| --- | --- | --- |
| Authentication and project authorization | shared project authorization dependencies; Phase 14 service/browser evidence | PASS |
| Data ingestion and version lifecycle | Dataset/resource ingestion and `create_version_from_dataset_resource`; Phase 12/14 evidence | PASS |
| Typed Dataset query and sample identity | Dataset routes and Materials Explorer contracts; `sample_id` semantics | PASS |
| Data → Research handoff | Data Platform handoff and exact context selection tests | PASS |
| ResearchTurn → Job → ToolCall → Artifact → Result | `research_agent/service.py`, planner, queue workers, Phase 14 evidence | PASS |
| Grounded interpretation | `apps/api/mdi_api/interpretation/`, strict evidence validator, Dataset projector fix | PASS |
| Scientific Presentation compiler | bounded presentation contracts and deterministic mappings | PASS |
| Structure/Electronic/Dataset user presentation | renderers and routes exist; full current same-stack domain campaign not rerun | PARTIAL |
| Scientific Viewer coverage | registry and many renderer implementations exist; every declared family lacks current live acceptance | PARTIAL |
| Evidence traversal UX | Presentation evidence references now link through the existing secured interpretation-evidence route, retaining Result/interpretation identity; Dataset Agent2 browser proof now shows exact source, Artifact checksum and ToolCall, while every capability-family path remains open | PARTIAL |
| Scientific Report | grounded report composition and immutable snapshots exist; frozen `ReportContextBundle` validates bounded provider input, the report index labels modern recoverable sessions versus compatibility-only history, and the modern Dataset report now traverses its exact Result/interpretation evidence chain in the authenticated browser with zero Job/ToolCall/Artifact/Result delta; multi-family report-quality evaluation remains open | PARTIAL |
| Historical v1/v2 presentation | exact source semantics are sealed in Phase 12/13; Research history links now use persisted `researchTurnId` only, and history explicitly labels modern `RESEARCH_TURN` versus compatibility-only `LEGACY_SESSION_RUN`; modern history now prefers the persisted `user_message_id` with a session-bound safety check; repeated browser campaign is still open | PARTIAL |
| Archived historical presentation | archive API/UI and historical Viewer semantics exist; mature Report/Evidence browser proof not yet run | PARTIAL |
| Viewer no-recompute | read-only architecture and tests exist; current persisted delta campaign across all viewers is not yet rerun | PARTIAL |
| Exact Result reuse | the real PostgreSQL/Redis service campaign passes four continuation/reuse cases and asserts zero aggregate growth for Plan/Job/ToolCall/Artifact/ScientificResult state; browser-level control semantics remain open | PARTIAL |

## Context, memory and message provenance

| Contract | Evidence | Status |
| --- | --- | --- |
| Bounded candidate assembly | `research_agent/context/schemas.py`, `assembler.py` | PASS |
| Deterministic compiler and compaction | `research_agent/context/compiler.py` | PASS |
| Session memory pins/goals/constraints | `research_agent/memory/{schemas,service}.py` and `research_session_*` tables | PASS |
| Exact immutable ContextSnapshot | `research_context_snapshots` table and repository | PASS |
| Explicit ContextManifest 2.0 persisted for resolved research context | `ContextManifest`/`ContextManifestItem` are built from resolved context and persisted in immutable `CONTEXT_RESOLVED` event payloads; authorized `GET /api/research/turns/{turn_id}/context-manifest` exposes the bounded projection | PASS |
| Per-item inclusion/exclusion provenance | manifest items retain authority class, source identity, opaque ref, inclusion reason, selection mode, exact object/version and fingerprints; excluded-item ledger remains bounded | PASS |
| Context budget policy | checked-in `ContextBudgetPolicy 2.0` defines operation-specific effective input budgets with reserved output/repair space; deterministic compiler coverage proves conversation compacts before dropping exact selected scientific identity, while provider/browser-scale benchmark evidence remains open | PARTIAL |
| User-facing Used context disclosure | Research UI fetches the authorized manifest endpoint and renders a bounded “本次研究使用的上下文” disclosure | PASS |
| Historical context replay | immutable `CONTEXT_RESOLVED` event retains manifest fingerprint, policy/budget state and exact refs for a turn; project history now exposes whether a run has an authoritative ResearchTurn or only a legacy session binding; replay UI controls are not part of this contract | PARTIAL |
| Message revisions/branching | completed Result exposes edit-to-new-branch; terminal parent relation, exact source refs and immutable parent are covered by domain/frontend tests; full browser edit submission and branch switcher remain open | PARTIAL |

## Lifecycle and control

| Surface | Current evidence | Status |
| --- | --- | --- |
| Project rename/archive/restore/bulk archive | `routers/projects.py` | PASS |
| Dataset/object metadata update/archive/restore | `routers/datasets.py`, object repositories, Data UI | PASS |
| Dependency impact preview | secured `GET /api/projects/{project_id}/dependency-impact` and `GET /api/datasets/{dataset_id}/dependency-impact` enumerate persisted dependencies server-side; destructive delete remains fail-closed | PASS |
| Trash/restore/purge policy | no complete protected-trash lifecycle found | NOT_QUALIFIED |
| Bulk scientific-object lifecycle | partial Data UI patterns; full authorization/dependency qualification absent | PARTIAL |
| Stop/cancel orchestration and execution | `cancel_turn`, execution supervisor, `/cancel` API | PASS |
| Stop/continue/rerun/re-interpret/retry product controls | cancel path exists; completed Result presentation now exposes explicit continue, deliberate new rerun, and bounded no-recompute re-interpret actions; queued/running recovery and retry browser semantics remain open | PARTIAL |
| Last-message edit and branch history | `编辑问题` routes to an explicit edit composer and creates a child ResearchTurn with `parent_turn_id`; browser submission/branch navigation campaign remains open | PARTIAL |

## Organization, reliability and operations

| Surface | Current evidence | Status |
| --- | --- | --- |
| Global search | `GET /search` (and `/api/search`) provides bounded authorized navigation across projects, datasets, scientific objects, Research sessions, Reports and ScientificResults; ProductShell uses the same endpoint with type labels and direct links | PASS |
| Background task center | `/tasks` aggregates authorized persisted analysis jobs, opens exact Workspace/Research routes, supports explicit reload and cancellation only when a persisted `researchTurnId` is present; retry/notification/network-recovery semantics remain open | PARTIAL |
| Notifications | transient/status projections exist; durable notification center not proven | NOT_QUALIFIED |
| Leave/return/reconnect | persisted Research state and history routes exist; network interruption campaign absent | PARTIAL |
| Export/reproducibility package | Report/Recipe export foundations exist; mature user export manifest not proven | PARTIAL |
| PostgreSQL/Redis/MinIO same-stack runtime | Phase 14 runtime evidence: PostgreSQL, Redis, MinIO, Redis workers | PASS |
| Backup/restore drill | no current Phase 14-R drill evidence | NOT_QUALIFIED |
| Monitoring/resource governance | health/runtime and bounded contracts exist; operational coverage/alerts/quotas absent | PARTIAL |
| Performance baseline/SLOs | no current Phase 14-R measurement artifact | NOT_QUALIFIED |

## Current release conclusion

The Phase 14 architecture is still sealed and there is no evidence requiring
Phase 14 reopening. Phase 14-R is not yet closed. The highest-priority
remaining gaps are full scientific surface acceptance, report-quality/context
contracts, message revision/branching, queued/running recovery and retry,
Trash/retention/export, and current same-stack real-user evidence.

## Current same-stack browser spot check

On 2026-08-28, the authenticated in-app browser loaded
`/projects/project_0002_1a0af866391f412d/research` against the live
PostgreSQL/Redis/MinIO runtime with zero captured console warnings/errors.
The existing legacy Structure run
`job_c4ed9c864f104e5b884c6bae` rendered the bounded `结构组成概览` table and
the deterministic `Scientific Presentation` result入口. Its session route is
explicitly persisted (`research_fbf038934dc84ffeaa5aed9e7c906095`); no Job-name
Turn guessing was observed. A complete current ResearchTurn-linked
interpretation/evidence browser campaign is still open, so this spot check is
not a Phase 14-R closure claim.

The current-worktree PostgreSQL integration smoke
`tests/integration/test_agent2_phase3_service_backed.py` was also executed
with the repository-supported service URLs (PostgreSQL `127.0.0.1:55433`,
Redis DB 13, MinIO `127.0.0.1:9000`) and passed `1/1`; the earlier skip was
only the missing `MDI_TEST_DATABASE_URL` shell alias. This is a focused
service regression, not the complete Phase 14-R campaign.

The current-worktree Phase 12 service campaign
(`tests/integration/test_agent2_phase3_service_backed.py` plus
`tests/integration/test_agent2_phase7_service_backed.py`) was rerun against the
same PostgreSQL/Redis/MinIO stack with the repository's `services/llm` package
on subprocess `PYTHONPATH`: `5 passed`, `0 failed`, `0 errors`, `0 skipped`.
The earlier subprocess error was only a missing `mdi_llm` import path and did
not indicate a service or scientific-result failure.

The authenticated report route for the same legacy run was also opened in the
browser. It rendered the verified 9/9-row `结构组成概览` table, exact dataset
link, methods/limitations sections, and no captured console errors. Because
this legacy run has no modern ResearchTurn-linked interpretation, its report
conclusion remains a generic bounded summary; this is useful read-only
evidence but does not satisfy the full Phase 14-R multi-family report-quality
campaign.

The preserved authenticated historical Research route was refreshed with an
explicit session target and an unnormalized historical run. The route now
loads the persisted conversation and exact Dataset presentation; the previous
false “研究会话不存在或已不可访问” state is absent. The fix is covered by
the `ResearchPages` regression (`35 passed`) and the authoritative session
request returned `200 OK`. This closes that narrow navigation seam, but does
not replace the broader history/resume and mature control campaign.

An authenticated browser request to a different project’s exact modern
ResearchTurn route was denied with the bounded product message
`当前用户无权访问此项目。` and no console warnings/errors. This is a live
cross-project fail-closed check; it does not substitute for the still-open
same-project multi-surface authorization campaign.

The authenticated Data Platform route
`/projects/project_0002_1a0af866391f412d/data` was rechecked in the existing
browser tab. The dataset action menu exposes the existing lifecycle controls
(`归档数据集`, `删除空数据集`) and the bounded dependency preview is wired
before permanent-delete confirmation. The tab remains open and handed back for
continued qualification; no destructive browser action was performed.

An authenticated browser golden path then archived and restored the dedicated
`dataset_0003_1e42d834bfa64961` (`Phase13 Canonical Dataset`) through the normal
menu. While archived it appeared in the `已归档` filter with a `恢复数据集`
action and was absent from the active dataset list; after restore it returned to
the active list and the archived filter reported no archived data. PostgreSQL
afterward showed the dataset `status=profile_ready`, with the project retaining
4 ScientificObjects and 4 ScientificObjectVersions. This proves the reversible
UI state transition but does not close the broader mature Trash/retention gate.

PostgreSQL activity after the service campaign was `active=1`, `idle=5`,
`idle in transaction=0`; no pool timeout or monotonic idle growth was observed
in this check.

The current-worktree full regression was rerun after the Phase 14-R fixes:
frontend `95 files / 606 passed`; backend `1820 passed / 83 skipped`
(the skips remain historical/optional compatibility coverage). This is
regression evidence only; the mature-product P0/P1 browser, report-quality,
trash/retention, recovery and operations gates are still not all qualified.

### Agent-2.0 Phase 14-R evidence traversal projection (2026-08-28)

The secured interpretation-evidence response now keeps the evidence bundle as
the authority for evidence identity while resolving a bounded read-only chain
from the persisted ScientificResult snapshot for the source Job. The response
adds `sourceObjectRefs` (exact object/version pairs) plus bounded Job-scoped
Artifact and ToolCall descriptors. Legacy interpretations without a persisted
Result remain readable with an empty source-ref projection; the secured route
still authorizes through the owning Job before returning the response. The
deterministic persistence test passes (`13 passed` in
`tests/test_phase10l4_api_persistence.py`), targeted frontend Research/
Presentation tests pass (`43 passed`), typecheck and touched Ruff pass. This
closes the missing read-only source-chain projection at the API/UI boundary,
but does not by itself close the broader Phase 14-R cross-project browser and
full scientific-surface campaign.

### Agent-2.0 Phase 14-R history continuity bridge (2026-08-28)

The Research history popover now resolves each session entry through the
server-projected `ProjectHistory.analyses` relation. When a persisted run and
`researchTurnId` exist, the link carries both `run` and exact `turn` query
parameters; sessions without a bound run retain the session-only route. This
removes the prior blank-session risk without deriving identity from Job naming.
The frontend ResearchPages regression suite passes (`34 passed`) and typecheck
remains green. The broader history/resume browser campaign and mature
stop/edit/branch gates remain open.

### Agent-2.0 Phase 14-R evidence inspector (2026-08-28)

Scientific Presentation evidence references now expose a bounded, read-only
“检查证据链” interaction. The browser loads the existing secured
interpretation-evidence projection only when the user asks to inspect a
reference, then displays the exact source object/version, Result evidence
field/value, persisted Artifact identity/checksum, and ToolCall/tool status.
Artifact content remains available through the existing authorized content
route. The UI does not display credentials, queue URLs, filesystem paths, or
raw provider payloads and cannot trigger a Job. The deterministic frontend
regression `ScientificPresentationBlocks.test.tsx` passes; the service-backed
Phase 3/7 campaign also passes `5/5` with no skips under PostgreSQL/Redis/MinIO.
This closes the presentation-layer evidence inspection seam, while the
broader cross-project browser campaign and mature-product release gates remain
open.

### Agent-2.0 Phase 14-R interpretation identity bridge (2026-08-28)

The presentation compiler now accepts the persisted outer
`interpretationId` returned by the authorized Research API. This matters for
legacy and current payloads because the nested grounded interpretation is a
scientific content envelope and is not required to repeat the database
identity. Evidence blocks therefore retain the exact interpretation identity
needed by the secured evidence-chain endpoint. Targeted compiler, presentation,
and Agent2 presentation tests pass (`12 passed`); this is a read-only
provenance fix and does not create or rerun scientific work.
### Agent-2.0 Phase 14-R Agent2 evidence compatibility adapter (2026-08-28)

The secured planner evidence route now recognizes durable Agent2
interpretations in `agent2_scientific_interpretations` and projects their
immutable `ScientificResult` snapshot through the existing read-only evidence
contract. The adapter preserves exact `source_object_refs`, resolves
Job-scoped Artifact and ToolCall descriptors, and accepts both snake_case and
camelCase source bindings used by historical result bundles. No scientific
values are copied into a new authority and no execution path is reachable from
the inspector.

Evidence:

- real same-stack API call for interpretation
  `efccf7a2-6666-429e-be92-20cb2cf659de` returned Result snapshot
  `2809dcd1-243e-4323-8538-0a5fe81780d9`, exact Dataset object
  `8a425466-b697-4c85-9a43-199414a22865`, version
  `be02266a-7d4f-4ebb-9f28-3132855167d0`, Artifact checksum
  `879396a3bc0bfdef2d31387b3eb73df309fa228d95f9cf2fb2c92eca6c119708`,
  and ToolCall `call_job_agent2_8382c443f9ca4c909aa3444fea683807_step_1`
  (`dataset.materials_explorer`, completed).
- authenticated browser tab reloaded against the restarted PostgreSQL /
  Redis / MinIO API and displayed the same source, checksum and ToolCall in
  `证据链 evidence.bf3896f29ae3554e977725d327b4ebba`.
- deterministic persistence suite now passes `14 passed`.

This closes the remaining Agent2-to-planner evidence identity seam. The
broader Phase 14-R mature-product campaign remains PARTIAL: full scientific
surface coverage, lifecycle/trash policy, task recovery, report-quality
evaluation, operations maturity, and exact-SHA release commits are not yet
qualified.

### Agent-2.0 Phase 14-R explicit branch navigation (2026-08-28)

The Research API now returns the persisted `parent_turn_id` and the session
turn list is exposed through an authorized read-only endpoint. The Research
workbench derives sibling branch choices from that relation and renders bounded
links using the exact `researchTurnId`; it no longer relies on Job identifier
formatting. Legacy turns without an explicit relation remain safely
non-branchable. Deterministic coverage includes a three-turn root/sibling
lineage and the API/domain regression suites remain green. Full authenticated
browser submission/edit/branch acceptance is still PARTIAL.
### Agent-2.0 Phase 14-R exact Result reuse service qualification (2026-08-28)

The existing Agent2 continuation/re-interpretation service campaign was rerun
against PostgreSQL and Redis with real worker subprocesses. Four cases passed
(RDF and XRD interpretation reuse plus continuation paths). The campaign
asserted that the follow-up turns completed while aggregate counts for
`analysis_plans`, `jobs`, `tool_calls`, `artifacts`, and
`scientific_result_snapshots` remained unchanged for interpretation-only reuse
cases. This is concrete service-backed zero-delta evidence for the existing
reuse authority; browser-level control coverage remains PARTIAL.
