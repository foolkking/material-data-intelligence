# Materials Intelligence Platform — Phased PROJECT_STATE and Retention Execution

## Execution mode
PHASED_ADDITIVE_STATE_TRANSITION_WITH_BOUNDED_SAFE_CLEANUP

## Scope
Create `PROJECT_STATE.md` as a compact human-readable current snapshot;
preserve all specialized authorities; enable only approved high-level
dual-read guidance; define controlled snapshot write/freshness semantics;
record reverse references; and run the existing bounded safe-cleanup dry-run.

## Prohibited actions
Do not create branches/worktrees or push. Do not move source architecture,
change application behavior, remove compatibility facades, alter API/auth/
schema/Alembic/transactions/persisted identities/worker or queue identities,
change Tool/Adapter or scientific semantics, redesign UI, retire TASKS/results,
delete/archive runtime, user-owned, historical, qualification, release, or
unknown material, or migrate specialized readers.

## Required phases
1. Add `PROJECT_STATE.md` from authoritative current evidence only.
2. Enable high-level human/Agent orientation while preserving TASKS/results and
   all specialized readers as authorities.
3. Define procedural snapshot update triggers and visible `CURRENT`/`STALE`
   freshness semantics without self-referential commit hashes.
4. Audit reverse references for PROJECT_STATE, TASKS, results, persistent state,
   roadmap/scope, qualification, dynamic contracts, and Tool Registry.
5. Run `python scripts/repo_safe_cleanup.py --dry-run --older-than-days 30`;
   apply only if a candidate passes every existing safety gate. Zero candidates
   is a successful no-op.

## Authority rules
`PROJECT_STATE.md` is an orientation snapshot only. TASKS, results, ADRs,
qualification/CI, dynamic/runtime identity manifests, Tool Registry,
roadmap/scope, historical evidence, and runtime/user-owned state remain
authoritative in their domains. Specialized authority wins conflicts.

## Required invariants
No runtime/source-architecture/evidence changes; no historical or qualification
retirement; no reader redirection for specialized authorities; no
self-referential commit loop; TASKS/results authority preserved; no push.

## Required validation and records
Verify source pointers, focused state/task/result contract checks, reverse
references, `git diff --check`, and the safe-cleanup dry-run. Update existing
project records and `results.md` only as required by `AGENTS.md`. Finish with a
clean worktree and a bounded report of readiness, unknowns, and next gates.
