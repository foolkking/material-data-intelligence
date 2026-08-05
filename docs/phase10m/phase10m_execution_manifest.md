# Phase 10M Execution Manifest

Status: REVIEWER-SEALED RECOMMENDATION
Purpose: sole high-level repository entry for future Phase 10M implementation agents.

## Baseline and canonical documents

Begin from the verified Phase 10M-0 completion SHA named in `results.md`. Read `AGENTS.md`, `docs/ROADMAP.md`, `docs/13_SHARED_SCHEMA_SPEC.md`, this manifest, `phase10m_execution_lock.md`, `phase10m_implementation_backlog.md`, and `phase10m_acceptance_and_test_plan.md`. Decision IDs M-D001 through M-D025 are mandatory.

## Contracts and persistence

- `ScientificWorkspace 1.0`
- `WorkspacePanel 1.0`
- `WorkspaceSelectionContext 1.0`
- `WorkspaceRendererRegistry 1.0`
- `WorkspaceReportComposition 1.0`
- `WorkspaceRecipe 1.0`
- migration `0007_phase10m1_workspace_domain`
- tables `scientific_workspaces`, `workspace_panels`, `workspace_layout_revisions`

The Workspace stores references and mutable presentation state, never scientific payloads.

## APIs and routes

Implement the exact Workspace endpoints in `phase10m0_workspace_persistence_api_migration_decision.md`. Frontend route is `/workspaces/{workspaceId}`. Root `/` remains PlannerWorkbench. Report/recipe composition endpoints are owned by Phase 10M-5.

## Module map

Backend work follows current contract/repository/service/API conventions under `apps/api/mdi_api`. Shared JSON schemas remain checked in under current schema ownership. Frontend contracts and clients follow `apps/web/lib`; route and Workspace components live under `apps/web/app/workspaces/[workspaceId]` and `apps/web/components/workspace`. Existing scientific components are reused through the presentation-only renderer registry.

## Phase order

Execute M1 domain/persistence, M2 shell, M3 selection, M4 typed renderers, M5 report/recipe, M6 recovery/responsive closure, and M7 integration closure. Each phase requires its own reviewer prompt and verified implementation/completion/archive lifecycle.

M5 owns exactly `M5-A01`, `M5-A02`, `M5-A03`, `M5-A04`, `M5-A05`, `M5-A06`,
and `M5-A07`: authority/contracts, scientific Report composition, exact Recipe
replay manifest, Workspace composition UI and history, deterministic preview/
safe export, partial/compatibility/accessibility/performance/security, and
end-to-end verified lifecycle. The exact names and set are mirrored in the
acceptance plan, backlog, and M5 evidence map.

M6 owns exactly `M6-A01`, `M6-A02`, `M6-A03`, `M6-A04`, `M6-A05`, `M6-A06`,
`M6-A07`, and `M6-A08`: explicit Save/concurrency, deterministic reload/layout,
deep-link/history navigation, Job/source/partial/historical recovery,
Report/Recipe recovery with session-draft honesty, user-facing state and long
content closure, responsive/accessibility closure, and performance/security/
verified lifecycle. The exact names and set are mirrored in the acceptance
plan, backlog, TASKS block, and M6 evidence map.

The exact M6 requirement names are `EXPLICIT_WORKSPACE_SAVE_AND_CONCURRENCY`,
`DETERMINISTIC_RELOAD_AND_LAYOUT_RESTORATION`,
`DEEP_LINK_REFRESH_AND_HISTORY_NAVIGATION`,
`JOB_SOURCE_PARTIAL_AND_HISTORICAL_RECOVERY`,
`REPORT_RECIPE_RECOVERY_AND_DRAFT_HONESTY`,
`USER_FACING_STATES_LONG_CONTENT_AND_TERMINOLOGY`,
`RESPONSIVE_MOBILE_AND_ACCESSIBILITY_CLOSURE`, and
`PERFORMANCE_SECURITY_EVIDENCE_AND_VERIFIED_LIFECYCLE` in ID order.

## Required commands

Use repository-current equivalents of:

```powershell
git diff --check
uv lock --check
uv run python -m pytest -q
npm --prefix apps/web test
npm --prefix apps/web run typecheck
npm --prefix apps/web run build
npm --prefix apps/web ls --depth=0
```

Run focused contract/repository/API/frontend tests, Alembic upgrade/downgrade/re-upgrade, PostgreSQL + Redis + MinIO no-skipped tests, Chromium/Firefox/WebKit/390x844, accessibility, WebGL lifecycle, evidence manifest, secret scan, TASKS parser, and closure checker required by each phase.

## Evidence

Use `docs/phase10m/evidence/phase10m{n}_*/`. Record exact API captures, DOM/network/console summaries, current screenshots, migration/service facts, caps/performance, security markers, hashes, and exact-SHA CI. Normalize text to LF for SHA-256 and hash PNG bytes raw.

## Security markers

At minimum retain every marker in `phase10m0_responsive_accessibility_performance_security.md`, L1-L5 candidate/provider/execution security regressions, `REAL_LLM_CALLS` disclosure, no external science network, no secret hits, and no recommendation execution.

## Completion format

Every implementation phase records baseline, production behavior, contracts, persistence/API/UI, compatibility, tests and exact counts, browser/service evidence, security, evidence manifest, files, SHAs/CI, non-scope, queue state, reviewer gate, and final clean `HEAD == origin/master`.

## Stop conditions

Stop before source changes when the entry baseline, task state, worktree, prior archive, or reviewer authorization is inconsistent. Stop during implementation on any conflict listed in `phase10m_execution_lock.md`. Never repair unrelated history, weaken tests, infer historical identity, add execution authority, or enter the next phase automatically.
