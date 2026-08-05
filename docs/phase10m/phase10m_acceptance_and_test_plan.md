# Phase 10M Acceptance and Test Plan

Status: REVIEWER-SEALED RECOMMENDATION

Every acceptance ID belongs to exactly one backlog phase. Every backlog phase names its acceptance range.

| ID | Category | Acceptance |
| --- | --- | --- |
| M1-A01 | Contract | Python/JSON/TypeScript 1.0 parity; unknown fields, versions, hashes, caps, and duplicate keys enforced |
| M1-A02 | Persistence | In-memory and SQLite immutable source refs, idempotent create, optimistic conflict, revisions |
| M1-A03 | Migration | Upgrade/downgrade/re-upgrade of `0007`, current head compatibility |
| M1-A04 | PostgreSQL | Service-backed Workspace/panel/revision round trip, 0 skipped |
| M1-A05 | API | Create/read/update/list and historical Job candidates with ETag/idempotency |
| M1-A06 | Integrity | Foreign project, stale hash, deleted Job, invalid IDs, cap overflow rejected |
| M1-A07 | Legacy | Modern lazy projection and explicit `LEGACY_READ_ONLY` without inferred identity |
| M1-A08 | Security | No payload copy, secret/path, execution authority, or cross-project access |
| M2-A01 | Routing | `/workspaces/{id}` plus `/` compatibility, direct load and 404/source states |
| M2-A02 | IA | Nine groups, one active panel, data rail, overlay inspector shell |
| M2-A03 | Navigation | Back/forward and valid `panel` deep link deterministic |
| M2-A04 | State | Empty/loading/running/partial/failed/stale/legacy typed surfaces |
| M2-A05 | History | Authorized project history opens exact idempotent Workspace |
| M2-A06 | Browser | Chromium, Firefox, WebKit, 390x844 with zero console/external-network failures |
| M2-A07 | Accessibility | Landmarks, headings, keyboard/focus, live status, no horizontal overflow |
| M3-A01 | Selection contract | Every exact kind validates identity, version, scope, and caps |
| M3-A02 | Propagation | Subscribed panels receive only compatible exact refs |
| M3-A03 | Forbidden mapping | Index, row order, display label, fuzzy identity, and unit guessing rejected |
| M3-A04 | URL | Canonical <=2,048-byte token restores and rejects stale/foreign values |
| M3-A05 | Persistence | Explicit pin survives reload with optimistic revision |
| M3-A06 | Inspector | Artifact/sample/site/atom/frame/q-point/branch/field/evidence/claim facts are exact |
| M3-A07 | Browser | Keyboard, mobile bottom sheet, clearing and multi-selection evidence |
| M4-A01 | Registry | Checked-in renderer registry covers every current Planner-visible result contract |
| M4-A02 | Authority | No frontend scientific recomputation; exact artifact contract selects renderer |
| M4-A03 | Fallback | Invalid, unsupported, legacy, missing, and oversized artifacts remain inert and typed |
| M4-A04 | Scientific panels | Dataset/ML/composition/structure/trajectory/phonon/BZ/volumetric current renderers work |
| M4-A05 | Evidence | Artifact lineage and grounded evidence links navigate exact source identities |
| M4-A06 | Loading | Metadata first, active-panel lazy payload, cancellation and request cap |
| M4-A07 | WebGL | Context loss/recovery and unmount dispose canvas resources without growth |
| M4-A08 | Browser/service | Browser matrix/mobile plus MinIO-backed artifact retrieval, 0 skipped |
| M5-A01 | Authority/contracts | `REPORT_RECIPE_AUTHORITY_AND_CONTRACTS`: strict DTOs reuse existing immutable Report/Recipe persistence |
| M5-A02 | Report | `SCIENTIFIC_REPORT_COMPOSITION`: deterministic sections, exact sources, findings, and mandatory disclosures |
| M5-A03 | Recipe | `EXACT_RECIPE_REPLAY_MANIFEST`: exact Plan 0.1/0.2 tools, params, dependencies, bindings, and no-execution flags |
| M5-A04 | Workspace UI | `WORKSPACE_COMPOSITION_UI_AND_HISTORY`: session draft, preview, finalize, immutable history, Recipe detail |
| M5-A05 | Preview/export | `DETERMINISTIC_PREVIEW_AND_SAFE_EXPORT`: zero-write preview plus canonical JSON and inert Markdown |
| M5-A06 | Closure qualities | `PARTIAL_COMPATIBILITY_ACCESSIBILITY_PERFORMANCE_SECURITY`: typed edge states, caps, mobile, a11y, security |
| M5-A07 | Evidence/lifecycle | `END_TO_END_EVIDENCE_AND_VERIFIED_LIFECYCLE`: browser/service evidence and three exact-SHA CI gates |
| M6-A01 | Save/concurrency | `EXPLICIT_WORKSPACE_SAVE_AND_CONCURRENCY`: approved durable fields, no-op suppression, quoted ETag/If-Match, typed conflict and revision-cap UX |
| M6-A02 | Reload/layout | `DETERMINISTIC_RELOAD_AND_LAYOUT_RESTORATION`: server revision, panel order, active-panel fallback, and pinned selection restore without hidden writes |
| M6-A03 | Navigation | `DEEP_LINK_REFRESH_AND_HISTORY_NAVIGATION`: exact panel/selection URL precedence, refresh, Back/Forward, and typed invalid state |
| M6-A04 | Job/source recovery | `JOB_SOURCE_PARTIAL_AND_HISTORICAL_RECOVERY`: persisted Job/ToolCall/Artifact authority, partial/failed/blocked/stale/missing/legacy state, no rerun |
| M6-A05 | Report/Recipe recovery | `REPORT_RECIPE_RECOVERY_AND_DRAFT_HONESTY`: immutable pair reload/export and explicit session-only draft loss boundary |
| M6-A06 | Product states/content | `USER_FACING_STATES_LONG_CONTENT_AND_TERMINOLOGY`: distinct status/error/empty/loading language and bounded long-content presentation |
| M6-A07 | Responsive/accessibility | `RESPONSIVE_MOBILE_AND_ACCESSIBILITY_CLOSURE`: one active mobile panel, drawers/sheets, keyboard/focus/live regions, 44px targets, reflow |
| M6-A08 | Performance/security/lifecycle | `PERFORMANCE_SECURITY_EVIDENCE_AND_VERIFIED_LIFECYCLE`: metadata-first loading, cancellation, WebGL invariants, inert security, service/browser evidence, exact-SHA gates |
| M7-A01 | Service-backed | PostgreSQL + Redis + MinIO full Workspace lifecycle, 0 skipped/failed |
| M7-A02 | Scientific integrity | Adapter -> Runtime -> Artifact -> renderer/evidence authority remains exact |
| M7-A03 | Historical compatibility | 0.1/0.2, modern/legacy/partial/missing-source cases retained |
| M7-A04 | Full tests | Backend/frontend/typecheck/build/lock/migration/closure all pass |
| M7-A05 | Browser | Chromium/Firefox/WebKit/mobile/accessibility/WebGL current evidence passes |
| M7-A06 | Security | All Workspace security markers and secret scan pass |
| M7-A07 | Evidence | Sanitized API/DOM/network/console/screenshots/performance manifest verifies |
| M7-A08 | Lifecycle | Implementation, completion, and verified queue archive exact-SHA CI pass |

No acceptance result from a fixture-only or historical screenshot is labeled as current product proof. Service-backed skips are failures for phases that require service evidence.
