# Project State Transition Plan

**Status:** `TRANSITION_PHASE_A_ADDITIVE_SNAPSHOT`
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

## Phased Strategy

1. Freeze this schema and reader map; do not create `PROJECT_STATE.md` yet.
2. Add a bounded transition writer/reader only in a separately approved documentation/task change; dual-write current state while all old ledgers remain.
3. Compare normalized state against TASKS/results/board/design progress at each task closeout.
4. Migrate readers one family at a time, retaining compatibility adapters and old files.
5. After a clean exact-SHA reader scan and reviewer approval, designate `PROJECT_STATE.md` canonical for current state.
6. Keep ADR, schema, CI/qualification, evidence, runtime and specialized contract documents independent.

## Anti-Bloat Gate

A proposed entry is rejected from `PROJECT_STATE.md` if it is raw evidence, a full command transcript, a large payload, a duplicate stable contract, or a historical detail that has no current decision/status impact. Each entry must link to a bounded source artifact instead.

No current ledger may be deleted under this amendment.
