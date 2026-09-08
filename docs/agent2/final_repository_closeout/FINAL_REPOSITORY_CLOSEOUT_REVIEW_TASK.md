# Materials Intelligence Platform

# FINAL REPOSITORY CLOSEOUT REVIEW

## Post-Physical-Migration Acceptance, Compatibility Review, Retention Readiness, and Project-State Transition Readiness

This task begins after `AUTONOMOUS_PHYSICAL_MIGRATION_COMPLETE`.

Approved review baseline:

```text
MIGRATION_START_COMMIT = db75aa57136e4512b11b6fe69bb54840ad970323
REPORTED_MIGRATION_FINAL_COMMIT = 19799f89017390e67eafbe2c448e05cd55e77302
REPORTED_COMMITS_CREATED = 28
ACTIVE_WORKTREE = E:/1project/mdi-b0-5a1
REPORTED_WORKTREE_STATUS = CLEAN
PUSHED = NO
NEW_WORKTREES_CREATED = 0
NEW_BRANCHES_CREATED = 0
```

Reported result:

```text
SOURCE_ARCHITECTURE_MIGRATION_COMPLETE = YES
BACKEND_PHYSICAL_RELOCATION_COMPLETE = YES
FRONTEND_PHYSICAL_RELOCATION_COMPLETE = YES
COMPATIBILITY_REDUCTION_COMPLETE_TO_SAFE_LIMIT = YES
ARCHITECTURE_GUARD_PASS = YES
ARCHITECTURE_CHECKER_PASS = YES
NEW_BACKEND_REGRESSIONS = 0
NEW_FRONTEND_REGRESSIONS = 0
```

## 0. Execution mode

```text
MODE = FINAL_CLOSEOUT_REVIEW_WITH_AUTONOMOUS_NARROW_REPAIR
```

Use the existing active worktree. Do not create another worktree or branch,
push, or use file-content/evidence hashes as review gates. Do not begin
forensic/root cleanup, evidence or screenshot deletion, runtime-data deletion,
PROJECT_STATE migration, UI redesign, feature development, schema/Alembic
changes, or provider changes. This task closes source architecture only.

## 1. Purpose

Independently verify the repository rather than repeating the migration report:

1. Review all migration commits for relocation/compatibility scope.
2. Verify canonical implementation ownership.
3. Verify remaining legacy paths are facades rather than duplicate authorities.
4. Reject canonical-to-compatibility dependencies.
5. Verify public, dynamic, worker, queue, Tool, Adapter, launcher, prompt, and
   frontend dynamic identities.
6. Confirm behavior/schema/identity invariants.
7. Classify remaining compatibility surfaces.
8. Determine readiness for a separate retention/cleanup review.
9. Determine readiness for a separate PROJECT_STATE transition review.

## 2. Review authority

Read current frozen architecture and migration records, including:

```text
docs/TARGET_REPOSITORY_ARCHITECTURE.md
docs/FILE_MOVE_MANIFEST.md
docs/IMPORT_BOUNDARY_RULES.md
docs/BEHAVIOR_INVARIANTS.md
docs/SYMBOL_OWNERSHIP_MANIFEST.md
docs/DYNAMIC_CONTRACT_MANIFEST.md
docs/BATCH0_DEPENDENCY_NORMALIZATION_PLAN.md
docs/PROJECT_STATE_TRANSITION_PLAN.md
TASKS.md
results.md
persistent architecture/state records
```

Historical documents remain historical and must not be rewritten.

## 3. Git/worktree gate

Verify the active worktree, current HEAD, clean/detached state, no push, and
review the full range
`db75aa57136e4512b11b6fe69bb54840ad970323..CURRENT_HEAD`.
If a legitimate post-report local correction exists, inspect it rather than
resetting. Final PASS requires a clean worktree.

## 4. Commit scope review

Classify every commit as one of:

```text
PHYSICAL_RELOCATION
SYMBOL_GROUP_EXTRACTION
COMPATIBILITY_ADAPTATION
IMPORT_PATH_MIGRATION
ARCHITECTURE_GUARD_OR_CHECKER
REQUIRED_TEST_ADAPTATION
STATE/CLOSEOUT_RECORD
```

Flag feature work, UI redesign, schema/auth/scientific semantic changes,
unrelated cleanup, evidence rewrites, or runtime-data changes.

Required: `UNRELATED_MIGRATION_COMMITS = 0`.

## 5. Backend ownership review

Verify physical ownership under bootstrap, transport, application, domain, and
infrastructure for database/repository composition, Workspace, Project History,
Scientific Object, Scientific Result, Scientific Report, Interpretation,
Agent2 persistence, Report composition, Phase2 runtime, and FastAPI routers.

For each legacy module record its canonical owner, why it remains, whether it
is an implementation or facade, public/dynamic dependencies, and whether it is
safe to remove now. Required: `DUPLICATE_AUTHORITIES = 0`.

## 6. Frontend ownership review

Verify thin routes under `apps/web/app`, product ownership under
`apps/web/features`, scientific implementation under
`apps/web/scientific-viewers`, and shared layout/UI/workspace/observability
under `apps/web/shared`. Inspect `apps/web/app/components` compatibility paths.
Canonical feature/viewer/shared modules must not import those facades.

## 7. Architecture direction

Run the existing B0-6 guard and B0-7 checker without weakening the allowlist.
Require:

```text
CYCLES = 0
FORBIDDEN_EDGES = 0
DYNAMIC_CONTRACT_ERRORS = 0
PUBLIC_SURFACE_ERRORS = 0
CANONICAL_TO_COMPATIBILITY_EDGES = 0
ALLOWLIST_START = 5
ALLOWLIST_CURRENT = 4
```

Record every remaining bounded edge exactly.

## 8. Dynamic contracts

Verify all six frozen handlers:

```text
mdi_api.research_agent_worker.run_queued_turn
mdi_api.research_agent_planning_worker.run_queued_planning
mdi_workers.queue_runtime.run_queued_job
mdi_api.scientific_results.worker.run_queued_result_projection
mdi_workers.interpretation_worker.run_queued_interpretation
mdi_workers.report_worker.run_queued_report_generation
```

Require handler resolution 6/6, unchanged six queue names, 62 Tool IDs and 50
Adapter IDs. Inspect importlib/`__import__`, dotted strings, `python -m`, uvicorn
strings, subprocess paths, Next dynamic imports, React lazy imports, Web Worker
URLs, manifest/prompt paths, launchers, and CI/qualification references.

## 9. Hard invariants

All must remain NO:

```text
API_CONTRACT_CHANGED
AUTHORIZATION_CHANGED
DATABASE_SCHEMA_CHANGED
ALEMBIC_CHANGED
TRANSACTION_SEMANTICS_CHANGED
PERSISTED_IDENTITY_CHANGED
QUEUE_IDENTITY_CHANGED
HANDLER_IDENTITY_CHANGED
TOOL_IDENTITY_CHANGED
ADAPTER_IDENTITY_CHANGED
SCIENTIFIC_IDENTITY_CHANGED
UI_BEHAVIOR_CHANGED
```

## 10. Test policy

Do not blindly rerun expensive historical qualification. First verify that the
reported tests correspond to final source state, no source change followed the
qualification, the worktree is clean, and guard/checker results reproduce.
At minimum run guard, checker, required compile/static checks, and
`git diff --check`. Run focused tests only for credible risks. Rerun broad
suites only if evidence is missing/stale, source is changed, or a credible new
regression appears.

## 11. Backend reconciliation

Review recorded evidence:

```text
PRE_MOVE = 2185 passed, 76 failed, 75 skipped
FINAL = 2211 passed, 76 failed, 75 skipped
NEW_BACKEND_REGRESSIONS = 0
```

Confirm the 76 failures remain baseline-only historical/environmental failures.
Do not repair them in this task.

## 12. Frontend reconciliation

Review recorded evidence:

```text
PRE_MOVE = 117 files / 950 tests PASS; typecheck PASS; build PASS
FINAL = 117 files / 950 tests PASS; typecheck PASS; build PASS
NEW_FRONTEND_REGRESSIONS = 0
```

Confirm no later source change invalidates it. No browser redesign campaign.

## 13. Compatibility closeout

Classify major compatibility surfaces as permanent frozen, temporary public,
temporary test/monkeypatch, removable after reverse-reference zero, or
unexpected duplicate authority. Include `mdi_api.repositories`,
`mdi_api.database`, `mdi_api.phase2_runtime`, `mdi_api.workspaces`,
`mdi_api.project_history`, `mdi_api.report_composition`,
`mdi_api.agent2_repositories`, `mdi_api.routers.*`, scientific legacy packages,
six worker modules, and `apps/web/app/components/*`.

Do not remove them unless correcting an actual migration defect.

## 14. Generated/runtime/forensic safety

Review Git paths and ownership and confirm no intentional changes to runtime
databases, object-store data, Redis/queue state, active logs, cookies,
screenshots, qualification evidence, historical forensic data, or cleanup
archives. Require evidence, screenshots, runtime data, and forensic tree all
unchanged.

## 15. Narrow repair policy

Autonomously repair only migration-scope defects that preserve behavior, API,
auth, schema/Alembic, transactions, persisted identities, scientific meaning,
and UI. Acceptable examples are missing re-exports, stale canonical imports,
checker-path errors, canonical-to-compatibility imports, missed dynamic paths,
or source-inspection tests aimed at old implementation authority. Run focused
qualification and create a cohesive local commit. Stop only for a real
semantic/identity/product decision.

## 16. No cleanup

Do not delete `.phase*`, runtime files, logs, temporary/cache files,
screenshots, evidence, qualification data, object-store data, database files,
or historical records. Only prepare bounded classification input.

## 17. No PROJECT_STATE transition

Do not create or replace project-state authority. Identify current state files,
readers, compatibility dependencies, blockers, and safe consolidation
candidates. `PROJECT_STATE.md` must not silently replace CI evidence,
qualification manifests, architecture decisions, historical evidence, runtime
identity manifests, or dynamic compatibility readers.

## 18. Remote status

Report `PUSHED = NO` and `REMOTE_CI_RUN = NO`. Determine whether remote CI is
required before a future remote/release operation, but do not push.

## 19. Decision

Return exactly one:

```text
FINAL_REPOSITORY_CLOSEOUT_REVIEW = PASS
FINAL_REPOSITORY_CLOSEOUT_REVIEW = REPAIRED_AND_PASS
FINAL_REPOSITORY_CLOSEOUT_REVIEW = BLOCKED_REAL_DECISION_REQUIRED
```

PASS requires clean worktree, no unrelated commits, no duplicate authorities,
zero forbidden/cycle/canonical-to-compatibility/dynamic/public errors, handler
6/6, unchanged queue/Tool/Adapter identities, zero new backend/frontend
regressions, all hard invariants preserved, and no evidence/runtime/forensic
changes.

## 20. Required report

Return the requested eighteen-section `Final Repository Closeout Review`,
including Git, commit-scope review, backend/frontend ownership, architecture and
dynamic contracts, hard invariants, regression reconciliation, compatibility
inventory, allowlist, safety, technical debt, retention readiness,
PROJECT_STATE readiness, remote status, final repository state, and:

```text
NEXT = RETENTION_AND_PROJECT_STATE_TRANSITION_REVIEW
```

Do not begin deletion, cleanup, PROJECT_STATE replacement, or push.
