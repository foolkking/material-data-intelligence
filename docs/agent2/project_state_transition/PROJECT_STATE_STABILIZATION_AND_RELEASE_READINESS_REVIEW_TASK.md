# Materials Intelligence Platform — PROJECT_STATE Stabilization and Release Readiness Review

## Mode
READ_ONLY_STATE_STABILIZATION_AND_RELEASE_READINESS_REVIEW

## Purpose
Validate the additive `PROJECT_STATE.md` system after repository evolution:
role and pointer correctness, freshness/staleness behavior, dual-read authority
ownership, bounded runtime unknowns, retention safety, and future remote
CI/release prerequisites.

## Scope and constraints
- Use the existing worktree at accepted HEAD
  `20b508bb7b714f27e63973b9ae6e8ea8fb0e5b57`.
- Do not reopen source architecture, remove compatibility, clean or retire
  historical/qualification material, mutate runtime/user data, create a branch
  or worktree, push, or run a remote release.
- Prefer static/non-destructive simulations of freshness cases. Do not create
  artificial authority changes.
- Specialized authorities remain primary: TASKS, results, ADRs,
  qualification/CI, dynamic/runtime identities, Tool Registry, roadmap/scope,
  historical evidence, and runtime/user-owned state.

## Required checks
1. Verify PROJECT_STATE role, accepted-base semantics, current represented
   facts, and all source pointers.
2. Validate static outcomes for snapshot-only, TASKS, qualification, and
   architecture-authority changes.
3. Confirm high-level readers use PROJECT_STATE only for orientation while
   specialized readers retain their authority paths.
4. Classify live RQ registration, live database migration head, and
   runtime/user-owned data ownership as resolved, protected unknown, or
   externally blocked without invasive probing.
5. Determine current-HEAD remote CI and runtime qualification requirements and
   whether release readiness is conditional.
6. Confirm zero deletion, retirement, runtime mutation, push, and source
   architecture change.

## Validation
Run focused state/task/result/reference checks and `git diff --check`. Broad
backend/frontend suites are not required because no source/runtime behavior is
authorized to change.
