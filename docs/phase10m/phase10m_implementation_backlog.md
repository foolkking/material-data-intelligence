# Phase 10M Sealed Implementation Backlog

Status: REVIEWER-SEALED RECOMMENDATION
Execution authority: each phase requires a separate reviewer prompt.

## Phase 10M-1: Workspace Domain Contract + Persistence

- **Goal:** implement `ScientificWorkspace 1.0`, `WorkspacePanel 1.0`, and `WorkspaceSelectionContext 1.0` ownership.
- **Production changes:** strict Python/JSON Schema/TypeScript contracts, canonical hashes, repositories, migration `0007_phase10m1_workspace_domain`, Workspace create/read/update/list API, historical Job candidate API.
- **Database:** `scientific_workspaces`, `workspace_panels`, `workspace_layout_revisions`; upgrade/downgrade/re-upgrade; no bulk backfill.
- **Compatibility:** no change to Intent, Plan, Job, Artifact, report, recipe, Runtime, or existing routes.
- **Tests/evidence:** contract parity, caps, in-memory/SQLite/PostgreSQL, idempotency/conflict, auth, stale/deleted/legacy projection, service-backed no-skipped.
- **Entry:** verified 10M-0 reviewer approval.
- **Exit:** exact-SHA implementation/completion/archive CI and Phase 10M-2 reviewer gate.
- **Non-scope:** Workspace UI, renderer integration, report composition.
- **Acceptance IDs:** `M1-A01` through `M1-A08`.

## Phase 10M-2: Unified Workspace Shell

- **Goal:** add `/workspaces/{workspaceId}` and the sealed nine-group information architecture.
- **Production changes:** metadata-first snapshot client, global header, data-context rail reuse, secondary navigation, one active panel, overlay inspector shell, history entry, PlannerWorkbench `Open workspace` command.
- **API:** consume 10M-1 endpoints only; no new scientific endpoint.
- **Compatibility:** `/` remains PlannerWorkbench; historical Job projection is explicit and idempotent.
- **Tests/evidence:** route/back-forward/deep-link, empty/loading/error/partial/legacy shells, Chromium/Firefox/WebKit/mobile, keyboard and screen-reader structure.
- **Entry:** archived 10M-1.
- **Exit:** exact-SHA lifecycle and 10M-3 reviewer gate.
- **Non-scope:** cross-panel selection, full typed scientific renderers, report composition.
- **Acceptance IDs:** `M2-A01` through `M2-A07`.

## Phase 10M-3: Cross-Artifact Navigation + Canonical Selection

- **Goal:** implement exact selection propagation and the contextual inspector.
- **Production changes:** URL codec, server-pinned selection, panel subscriptions, exact compatibility map, stale/unsupported handling.
- **Schemas/API:** unchanged 1.0 contracts; PATCH persists pinned selection with optimistic revision.
- **Compatibility:** legacy artifacts remain whole-artifact selectable; no identity inference.
- **Tests/evidence:** every supported identity, clearing/multi-selection, URL restore, stale/cross-project/incompatible rejection, no index/label/fuzzy mapping, browser keyboard/mobile.
- **Entry:** archived 10M-2.
- **Exit:** exact-SHA lifecycle and 10M-4 reviewer gate.
- **Non-scope:** new scientific computation, arbitrary selection adapters.
- **Acceptance IDs:** `M3-A01` through `M3-A07`.

## Phase 10M-4: Typed Artifact Gallery + Scientific Viewer Integration

- **Goal:** register current product renderers under `WorkspaceRendererRegistry 1.0` and expose typed result panels.
- **Production changes:** artifact-to-renderer map, lazy payload controllers, inert fallbacks, lineage/evidence links, WebGL lifecycle cleanup.
- **Schemas/API:** no Artifact contract change; existing bounded artifact APIs remain authority.
- **Compatibility:** unsupported/legacy contracts use read-only metadata/download or inert fallback.
- **Tests/evidence:** all 38 Planner-visible tool result families, invalid/large artifact behavior, no frontend recompute, WebGL cleanup, Chromium/Firefox/WebKit/mobile, service-backed artifact retrieval.
- **Entry:** archived 10M-3.
- **Exit:** exact-SHA lifecycle and 10M-5 reviewer gate.
- **Non-scope:** new renderer science or professional-science algorithms.
- **Acceptance IDs:** `M4-A01` through `M4-A08`.

## Phase 10M-5: Scientific Report + Recipe Composition

- **Goal:** productize existing Report/Recipe ownership inside Workspace.
- **Production changes:** `ReportCompositionRequest 1.0`, `ReportCompositionSnapshot 1.0`, `RecipeReplayManifest 1.0`, `ReportExportManifest 1.0`, exact source selection UI, deterministic preview/export, and immutable history.
- **Database/API:** reuse existing report/recipe tables and JSON fields; additive composition/read/export endpoints.
- **Compatibility:** old reports/recipes readable; unsupported recipes read-only; Recipe and recommendation remain non-executable.
- **Tests/evidence:** partial/failed disclosure, exact Evidence/lineage, Plan 0.1/0.2 Recipe determinism, zero-write preview, JSON/Markdown export, browser/service-backed.
- **Entry:** archived 10M-4.
- **Exit:** exact-SHA lifecycle and 10M-6 reviewer gate.
- **Non-scope:** document editor, arbitrary template code, PDF/HTML mandatory export, execution, or automatic rerun.
- **Acceptance IDs:** `M5-A01` `REPORT_RECIPE_AUTHORITY_AND_CONTRACTS`; `M5-A02` `SCIENTIFIC_REPORT_COMPOSITION`; `M5-A03` `EXACT_RECIPE_REPLAY_MANIFEST`; `M5-A04` `WORKSPACE_COMPOSITION_UI_AND_HISTORY`; `M5-A05` `DETERMINISTIC_PREVIEW_AND_SAFE_EXPORT`; `M5-A06` `PARTIAL_COMPATIBILITY_ACCESSIBILITY_PERFORMANCE_SECURITY`; `M5-A07` `END_TO_END_EVIDENCE_AND_VERIFIED_LIFECYCLE`.

## Phase 10M-6: Save, Reload, Recovery, and Responsive Closure

- **Goal:** close mutable UI recovery, source tombstones, mobile, accessibility, and performance.
- **Production changes:** optimistic layout save, append-only revisions, restore flow, request cancellation, cache invalidation, typed source loss/staleness UI.
- **API:** existing Workspace PATCH/GET; no new scientific authority.
- **Compatibility:** source hashes preserved; no remap or silent upgrade.
- **Tests/evidence:** repeated reload/recovery/conflict, 32-panel cap, 128 revisions, large payloads, 20-switch resource cleanup, 200% zoom, 390x844, keyboard/screen reader.
- **Entry:** archived 10M-5.
- **Exit:** exact-SHA lifecycle and 10M-7 reviewer gate.
- **Non-scope:** collaboration/tenancy, distributed editing, production-capacity claims.
- **Acceptance IDs:** `M6-A01` through `M6-A08`.

## Phase 10M-7: Workspace Integration + Evidence Closure

- **Goal:** validate the entire Phase 10M product with current scientific families and historical records.
- **Production changes:** integration defects only within sealed contracts; no architecture expansion.
- **Evidence:** PostgreSQL + Redis + MinIO, persisted Workspace/jobs/artifacts/lineage/interpretation/report/recipe, no-skipped CI, current screenshots, API captures, security and manifest.
- **Compatibility:** L1-L5, 0.1/0.2 plans, partial execution, historical jobs, existing root route and clients.
- **Tests:** full backend/frontend/typecheck/build, browser matrix, mobile/accessibility/WebGL, migration replay, evidence/secret/closure checks.
- **Entry:** archived 10M-6.
- **Exit:** implementation/completion/verified archive exact-SHA CI and Phase 10M complete record.
- **Non-scope:** Phase 10N science, Workspace redesign, new LLM or execution authority.
- **Acceptance IDs:** `M7-A01` through `M7-A08`.
