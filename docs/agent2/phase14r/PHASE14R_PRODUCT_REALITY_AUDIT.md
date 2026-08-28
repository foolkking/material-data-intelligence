# Phase 14-R Product Reality Audit

Date: 2026-08-28  
Verified base: `d03b0a2e86e50d834a774cf823cfe055c91cf10c`  
Branch: `master` (`HEAD == origin/master`)  
Phase 14 historical seal: preserved; Phase 15: not created or started.

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
| Evidence traversal UX | labels and provenance summaries exist; complete user-navigable Result → ToolCall/Artifact → version path not proven for every surface | PARTIAL |
| Scientific Report | grounded report composition and immutable snapshots exist; formal `ReportContextBundle` and quality rubric are not yet a checked-in contract | PARTIAL |
| Historical v1/v2 presentation | exact source semantics are sealed in Phase 12/13; Phase 14-R repeated browser campaign not yet run | PARTIAL |
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
| Context budget policy | compiler has a bounded default budget; operation-specific checked-in policy and benchmark evidence absent | PARTIAL |
| User-facing Used context disclosure | Research UI fetches the authorized manifest endpoint and renders a bounded “本次研究使用的上下文” disclosure | PASS |
| Historical context replay | immutable `CONTEXT_RESOLVED` event retains manifest fingerprint, policy/budget state and exact refs for a turn; replay UI controls are not part of this contract | PARTIAL |
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
| Stop/continue/rerun/re-interpret/retry product controls | cancel path exists; full distinct UX semantics not proven | PARTIAL |
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
