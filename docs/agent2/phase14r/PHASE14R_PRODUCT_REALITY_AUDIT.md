# Phase 14-R Product Reality Audit

Date: 2026-08-28  
Verified base: `9684e5a` (Phase 14-R fix-forward worktree; historical Phase 14
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
| Evidence traversal UX | Presentation evidence references now link through the existing secured interpretation-evidence route, retaining Result/interpretation identity; complete browser proof of every Result → ToolCall/Artifact → version path remains open | PARTIAL |
| Scientific Report | grounded report composition and immutable snapshots exist; frozen `ReportContextBundle` now validates the bounded provider input and the quality rubric is checked in; current multi-family browser/service quality campaign remains open | PARTIAL |
| Historical v1/v2 presentation | exact source semantics are sealed in Phase 12/13; Research history links now use persisted `researchTurnId` only, and history explicitly labels modern `RESEARCH_TURN` versus compatibility-only `LEGACY_SESSION_RUN`; modern history now prefers the persisted `user_message_id` with a session-bound safety check; repeated browser campaign is still open | PARTIAL |
| Archived historical presentation | archive API/UI and historical Viewer semantics exist; mature Report/Evidence browser proof not yet run | PARTIAL |
| Viewer no-recompute | read-only architecture and tests exist; current persisted delta campaign across all viewers is not yet rerun | PARTIAL |
| Exact Result reuse | some continuation/reuse infrastructure exists; dedicated zero-delta Phase 14-R acceptance is not yet established | NOT_QUALIFIED |

## Context, memory and message provenance

| Contract | Evidence | Status |
| --- | --- | --- |
| Bounded candidate assembly | `research_agent/context/schemas.py`, `assembler.py` | PASS |
| Deterministic compiler and compaction | `research_agent/context/compiler.py` | PASS |
| Session memory pins/goals/constraints | `research_agent/memory/{schemas,service}.py` and `research_session_*` tables | PASS |
| Exact immutable ContextSnapshot | `research_context_snapshots` table and repository | PASS |
| Explicit ContextManifest 2.0 persisted for resolved research context | `ContextManifest`/`ContextManifestItem` are built from resolved context and persisted in immutable `CONTEXT_RESOLVED` event payloads; authorized `GET /api/research/turns/{turn_id}/context-manifest` exposes the bounded projection | PASS |
| Per-item inclusion/exclusion provenance | manifest items retain authority class, source identity, opaque ref, inclusion reason, selection mode, exact object/version and fingerprints; excluded-item ledger remains bounded | PASS |
| Context budget policy | checked-in `ContextBudgetPolicy 2.0` defines operation-specific 12k/10k/12k/8k effective input budgets with reserved output/repair space; benchmark evidence remains open | PARTIAL |
| User-facing Used context disclosure | Research UI fetches the authorized manifest endpoint and renders a bounded “本次研究使用的上下文” disclosure | PASS |
| Historical context replay | immutable `CONTEXT_RESOLVED` event retains manifest fingerprint, policy/budget state and exact refs for a turn; project history now exposes whether a run has an authoritative ResearchTurn or only a legacy session binding; replay UI controls are not part of this contract | PARTIAL |
| Message revisions/branching | no complete persisted revision/branch product contract found in current Research UI | NOT_QUALIFIED |

## Lifecycle and control

| Surface | Current evidence | Status |
| --- | --- | --- |
| Project rename/archive/restore/bulk archive | `routers/projects.py` | PASS |
| Dataset/object metadata update/archive/restore | `routers/datasets.py`, object repositories, Data UI | PASS |
| Dependency impact preview | no server-derived lifecycle impact endpoint found | NOT_QUALIFIED |
| Trash/restore/purge policy | no complete protected-trash lifecycle found | NOT_QUALIFIED |
| Bulk scientific-object lifecycle | partial Data UI patterns; full authorization/dependency qualification absent | PARTIAL |
| Stop/cancel orchestration and execution | `cancel_turn`, execution supervisor, `/cancel` API | PASS |
| Stop/continue/rerun/re-interpret/retry product controls | cancel path exists and modern Agent2 presentations now expose a bounded no-recompute re-interpret action; full stop/continue/rerun/retry browser semantics remain open | PARTIAL |
| Last-message edit and branch history | no complete immutable message-revision flow found | NOT_QUALIFIED |

## Organization, reliability and operations

| Surface | Current evidence | Status |
| --- | --- | --- |
| Global search | `ProductShell.tsx` searches authorized projects only | PARTIAL |
| Background task center | persisted Job/Report queues exist; unified user task center not proven | PARTIAL |
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
remaining gaps are the durable ContextManifest/message provenance contract,
full scientific surface acceptance, report-quality/context contracts,
explicit research controls, and current same-stack real-user evidence.

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

The current-worktree historical/reuse service suite
`tests/integration/test_agent2_phase7_service_backed.py` was rerun against the
same PostgreSQL/Redis/MinIO stack with the repository's `services/llm` package
on subprocess `PYTHONPATH`: `4 passed`, `0 failed`, `0 errors`, `0 skipped`.
The earlier subprocess error was only a missing `mdi_llm` import path and did
not indicate a service or scientific-result failure.

The authenticated report route for the same legacy run was also opened in the
browser. It rendered the verified 9/9-row `结构组成概览` table, exact dataset
link, methods/limitations sections, and no captured console errors. Because
this legacy run has no modern ResearchTurn-linked interpretation, its report
conclusion remains a generic bounded summary; this is useful read-only
evidence but does not satisfy the full Phase 14-R multi-family report-quality
campaign.
