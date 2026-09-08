# Project State Transition Plan

**Status:** `TRANSITION_PHASE_A_TO_E_COMPLETE_NO_RETIREMENT`
**Canonical file created:** `YES` (additive snapshot only; specialized authorities remain separate)
**Purpose:** transition from duplicated ledgers to a bounded `PROJECT_STATE.md` without breaking readers.

## Future Authority

`PROJECT_STATE.md` should become the **CURRENT HUMAN-READABLE STATE AUTHORITY**. It must not replace Alembic, CI, qualification manifests, evidence manifests, ADRs, raw evidence, databases, runtime manifests, or Tool Registry contracts.

## Required Schema

```yaml
schema_version: <integer>
updated_at: <ISO-8601>
baseline_sha: <exact committed SHA>
state_status: <bounded status>
```

```text
# Project Snapshot
# Architecture Snapshot
# Runtime Snapshot
# Active Work
# Current Decisions
# Current Risks / Debt
# Verification State
# Compact Work Log
# Cleanup Ledger
# Historical Milestones
```

Each compact work-log entry contains: date/time, task ID, purpose, files/areas, intentionally changed behavior, explicitly unchanged behavior, validation, verification level, result, runtime state, commit/CI identity when applicable, and rollback note.

## Non-Goals / Boundedness

`PROJECT_STATE.md` stores normalized current truth, identity, hashes, decisions and traceable references. It does not store raw logs, JSON dumps, screenshots, test stdout, DB dumps, LLM prompts, secrets, credentials, scientific payloads, or absolute sensitive paths. Work-log entries are bounded; Git history carries full history; milestones are compact summaries only.

## Reader Inventory and Transition

| CURRENT_READER | CURRENT_FORMAT_ASSUMPTION | TARGET_SOURCE | DUAL_READ_REQUIRED | MIGRATION_RISK | DEPRECATION_CONDITION |
|---|---|---|---|---|---|
| `AGENTS.md` agent workflow | reads `TASKS.md`, persistent docs and results workflow | `PROJECT_STATE.md` for snapshot, `TASKS.md` for queue | yes | agents may select wrong task/status | only after explicit rule update |
| `TASKS.md` and task-queue process | `---TASK---` blocks and `状态` fields | `PROJECT_STATE.md` Active Work + keep TASKS queue | yes | queue automation breakage | all queue readers migrated and verified |
| `results.md` task/result validators and phase tests | append-only task result prose/markers | Verification State + compact Work Log, while results remains historical | yes | phase tests expect old markers | current-HEAD reader scan is empty or migrated |
| `persistent/TASK_BOARD.md` | task board/current work tables | Active Work | yes | human workflow drift | board consumers migrated and history retained |
| `persistent/DESIGN_PROGRESS.md` | design progress/status narrative | Architecture Snapshot + Work Log | yes | design milestones lost | all readers migrated; preserve milestones |
| `persistent/CHANGELOG.md` | historical change ledger | Historical Milestones, with changelog retained as history | yes | audit chronology loss | no direct reader and explicit archival decision |
| `persistent/OPEN_QUESTIONS.md` | unresolved questions | Current Risks/Debt and Decisions | yes | open questions disappear | all open items linked/closed |
| `persistent/PROJECT_BRIEF.md` | project identity/scope | Project Snapshot; retain as stable brief | yes | scope and identity duplication | separate scope document approved |
| `persistent/ARCHITECTURE_DECISIONS.md` | ADR identity and rationale | Current Decisions links/IDs only; ADR remains independent | yes | decision rationale lost | never fully replaced by state ledger |
| `persistent/TOOL_REGISTRY_NOTES.md` | stable tool/adapter contract notes | link from Architecture Snapshot; retain specialized contract | yes | tool identity ambiguity | never replaced for registry authority |
| phase scripts/tests/docs reading historical ledgers | exact paths/markers/content assumptions | explicit adapter/read model, then PROJECT_STATE | yes | hidden reader missed | exhaustive static path scan + current-HEAD verification |

## Phased Strategy / Execution Status

1. **Phase A complete:** `PROJECT_STATE.md` was added additively from current
   authoritative evidence.
2. **Phase B complete:** `AGENTS.md` reads PROJECT_STATE for high-level
   orientation; task, result, qualification, runtime, and specialized readers
   were not redirected.
3. **Phase C complete:** procedural update triggers and visible stale semantics
   were defined without an automated dual writer or self-referential commit
   loop.
4. **Phase D complete:** reverse references were audited; TASKS/results and
   specialized authorities remain required.
5. **Phase E complete:** the existing safe-cleanup dry-run returned zero
   candidates; no cleanup was applied.
6. Historical, qualification, runtime, user-owned, and unknown material remains
   retained pending separate explicit review.

## Anti-Bloat Gate

A proposed entry is rejected from `PROJECT_STATE.md` if it is raw evidence, a full command transcript, a large payload, a duplicate stable contract, or a historical detail that has no current decision/status impact. Each entry must link to a bounded source artifact instead.

No current ledger may be deleted under this amendment.

## Stabilization Validation (2026-09-08)

| CASE | SPECIALIZED CHANGE | EXPECTED SNAPSHOT BEHAVIOR | VALIDATION |
|---|---|---|---|
| A | PROJECT_STATE-only synchronization | remain `CURRENT` | PASS |
| B | active `TASKS.md` work changes | TASKS wins; reconcile Active Work | PASS; bounded prior-task drift detected and reconciled |
| C | qualification result changes | qualification evidence wins; mirror accepted summary only | PASS |
| D | architecture acceptance changes | architecture authority wins; effective stale until reconciliation | PASS |

Stored `CURRENT` is not trusted blindly. High-level readers compare represented
fields against the linked specialized authority; a mismatch is treated as
effective stale. This remains a procedural synchronization rule and does not
redirect specialized readers or introduce an automated dual writer.

Remote CI is technically available through the checked-in GitHub workflow and
authenticated CLI, but no push or workflow run occurred in stabilization.
Future release readiness is conditional on separately authorized current-HEAD
remote CI and the mandatory PostgreSQL/Redis/MinIO qualification gate.
