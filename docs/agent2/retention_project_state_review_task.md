# Materials Intelligence Platform — Retention and PROJECT_STATE Transition Review

## Execution mode
READ_ONLY_REPOSITORY_REVIEW_AND_TRANSITION_DESIGN

## Scope
Independently classify repository, runtime, evidence, ledger, and state surfaces;
build the reader/writer/reference dependency map; define future deletion gates;
and design a bounded additive PROJECT_STATE.md transition. This task must not
execute cleanup or state migration.

## Prohibited actions
Do not delete, move, rename, archive, purge, or rewrite runtime databases,
Redis, MinIO/object-store data, uploads, cookies, logs, screenshots, phase
evidence, qualification evidence, or historical records. Do not create
PROJECT_STATE.md, remove TASKS.md/results.md, migrate readers, modify source
architecture/facades, create branches/worktrees, or push.

## Required checks
Verify accepted HEAD `f3c6fa055d447ec6e25cabc7e9825ebbb769bba8`, clean starting
state, and current state authorities. Inspect source, scripts, CI, tests,
PowerShell, docs, AGENTS workflow, dynamic references, ignore rules, and
runtime-adjacent paths. Classify each relevant surface as runtime-protected,
user-owned/unknown, historical-immutable, qualification-authority,
current-operational-ledger, redundant-evidence-candidate, or
disposable-generated-candidate. Unknown ownership remains protected.

Build a bounded reader/writer graph for TASKS.md, results.md, persistent/*,
roadmap/scope docs, frozen architecture/manifests, qualification/evidence,
runtime manifests, caches/logs, databases, uploads, sessions, and object
stores. Distinguish automated and human readers/writers and identify deletion
blockers.

Design PROJECT_STATE.md as a compact human-readable current snapshot only.
It must not replace task queue semantics, detailed results, ADRs, CI or
qualification manifests, dynamic/runtime identity contracts, Tool Registry,
historical evidence, roadmap/scope authority, or domain-specific authority.
Define schema, conflict winners, freshness/staleness behavior, source pointers,
and additive dual-read/dual-write phases. Do not implement the transition.

Required final decisions:
RETENTION_AND_PROJECT_STATE_TRANSITION_REVIEW = PASS / PARTIAL_ADDITIONAL_CLASSIFICATION_REQUIRED / BLOCKED_REAL_DECISION_REQUIRED
RETENTION_CLEANUP_EXECUTION_READY = YES / PARTIAL / NO
PROJECT_STATE_TRANSITION_EXECUTION_READY = YES / PARTIAL / NO

Record safety facts: no files deleted/archived, no PROJECT_STATE created, no
readers migrated, no runtime state changed, no evidence rewritten, no source
architecture changed, no push. Update TASKS/results and persistent progress/
decision/board records only as required by AGENTS.md after the review; those
records are task bookkeeping, not PROJECT_STATE migration.
