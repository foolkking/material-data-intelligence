# MDI V0 — M4-02 Service-edge Interruption Resilience

## Authority and execution mode

- Committed base: `c4e74f922947be96833d0e276ad20f23241d6707`.
- M4-01 F11 Active API Restart Resilience is accepted but intentionally remains
  uncommitted in the current worktree.
- Preserve every M4-01 production/test change. Do not reset, restore, clean,
  stash, revert, commit, push, tag, release, run Phase D, or run Phase E.
- This is normal mainline M4 development, not qualification.

## Objective

Recover the exact historical F13 and F14 definitions from accepted repository
and program evidence, select the earliest coherent unresolved M4 fault boundary,
and execute that slice through current-behavior audit, deterministic
reproduction, minimal generic repair, focused tests, live fault execution,
browser/runtime evidence, durable identity/effect audit, affected regressions,
and a complete M4-02 evidence package.

Do not stop after authority recovery or planning.

## Entry requirements

Before changes:

1. Record `git rev-parse HEAD`, `git status --porcelain=v1`,
   `git diff --name-status`, and `git diff --cached --name-status`.
2. Require HEAD
   `c4e74f922947be96833d0e276ad20f23241d6707`.
3. Classify existing M4-01 changed paths as
   `PRE_EXISTING_ACCEPTED_M4_01`.
4. Create `M4_02_ENTRY_WORKTREE_BASELINE.json`.

## Historical fault authority

Search accepted current and historical program sources for `F13`, `F14`,
fault matrices/plans, service-edge recovery, long-running history, scale, and
M4. Create `M4_REMAINING_FAULT_AUTHORITY.json` with each fault's exact name,
description, trigger/boundary, expected invariant, owner, dependencies,
implementation state, and evidence source. Record and resolve source conflicts
using accepted/current program authority without rewriting history.

Create `M4_02_SCOPE_DECISION.json`, selecting the earliest unresolved coherent
M4 fault according to actual authority and dependency order.

## Required behavior

For the selected fault:

1. Reconstruct the normal workflow, fault trigger, durable and ephemeral
   pre-fault state, browser/API/worker/provider/scientific state, and expected
   recovery mechanism in `M4_02_FAULT_BOUNDARY_MAP.json`.
2. Prove the normal no-fault path first.
3. Reproduce the fault against the current M4-01 worktree using task-owned
   resources, preserving raw workflow IDs, service state, fault timestamps,
   durable state, queue state, browser state, and terminal outcome.
4. Identify the earliest failing invariant and classify the root cause as one
   of:
   `TRANSPORT_RECOVERY_DEFECT`, `CLIENT_RECONCILIATION_DEFECT`,
   `SERVICE_RECONNECTION_DEFECT`, `DURABLE_CORRELATION_DEFECT`,
   `IDEMPOTENCY_DEFECT`, `QUEUE_RECOVERY_DEFECT`,
   `READ_MODEL_RECOVERY_DEFECT`, `PROVIDER_EDGE_RECOVERY_DEFECT`,
   `OBJECT_STORE_EDGE_RECOVERY_DEFECT`, or `OTHER:<exact>`.
5. Implement only the smallest generic, bounded, idempotent,
   restart/recovery-safe fix. Do not add case-specific branches, latest-object
   or latest-job fallbacks, question-text correlation, or retry-until-green.
6. Do not redesign the six worker queues, leases, ownership, fencing, or retry
   architecture.
7. Prefer no migration. If the invariant cannot be represented by current
   durable models, stop with `M4_ARCHITECTURAL_BLOCKER` before adding one.

## Preserved invariants

- Durable Research Turn, Plan, and Job identity.
- Existing ownership, lease, and fencing rules.
- One completed authoritative scientific execution produces one authoritative
  `ScientificResult`.
- Deterministic Scientific Adapters.
- Interpretation remains a grounded projection; `ScientificResult` remains
  fact authority.
- Result-preserving interpretation retry.
- Display LOD is not computation input.
- No second Agent, critic, judge, or expert.
- If a `ScientificResult` already exists, edge recovery must not recompute
  Tools merely to reconstruct UI or Interpretation state.

Hard audit gates:

- duplicate admissions = 0
- duplicate Jobs = 0
- duplicate authoritative Results = 0
- unexpected duplicate Tool effects = 0
- orphan scientific entities = 0
- cross-workflow contamination = 0
- Tool recomputations caused only by M4-02 recovery = 0, unless the original
  Tool never completed.

## Browser/runtime behavior

Where user-visible, recovery must truthfully distinguish temporarily
unavailable, reconnecting, recovered, running, completed, failed, and
needs-attention using existing terminology. Do not hide a real failure or make
browser memory authoritative. Verify full reload and a new session/context when
relevant.

At least one live scenario must use real API, workers, PostgreSQL, Redis, MinIO
where relevant, and real frontend/browser when user-visible. Use a real provider
only if the selected edge requires it.

## Testing and regression

- Add focused unit tests only for new M4-02 behavior.
- Add at least one deterministic integration-level fault test that does not
  mock away the exercised service boundary.
- Run affected M4-01 regression, selecting the full-stack F11-B path if
  frontend polling/reconciliation ownership is touched.
- Run only affected M1 ownership/fencing, M2 durable recovery, and M3
  Result-preserving interpretation regressions.
- Do not run Phase D, Phase E, a candidate freeze, or a 16-case campaign.

## Evidence and classification

Use:

`_qualification/evidence/mainline_m4/m4_02_<fault-name>_20260920/`

and classify it as `MAINLINE_MILESTONE_EVIDENCE`.

Produce:

- `M4_REMAINING_FAULT_AUTHORITY.json`
- `M4_02_SCOPE_DECISION.json`
- `M4_02_ENTRY_WORKTREE_BASELINE.json`
- `M4_02_FAULT_BOUNDARY_MAP.json`
- `M4_02_ROOT_CAUSE.json`
- `M4_02_IMPLEMENTATION_SUMMARY.md`
- `M4_02_FAULT_MATRIX.json`
- `M4_02_EFFECT_AUDIT.json`
- `M4_02_IDENTITY_AUDIT.json`
- `M4_02_REGRESSION_RESULT.json`
- `M4_02_WORKTREE_CLASSIFICATION.json`
- `M4_02_FINAL_RESULT.json`

Track deltas relative to both the committed base and the M4-02 entry worktree.
Classify every changed/untracked path as:

- `M4_01_ACCEPTED_EXISTING`
- `M4_02_PRODUCTION`
- `M4_02_TEST`
- `M4_MAINLINE_EVIDENCE`
- `PRE_EXISTING_EXCLUDED`
- `GENERATED_LOCAL`
- `UNKNOWN`

Require `UNKNOWN = 0`.

## Completion gate

`READY_FOR_EXTERNAL_M4_02_REVIEW` requires exact historical F13/F14 recovery,
a justified next-fault selection, normal workflow PASS, controlled live
reproduction, proven root cause, minimal fix, selected recovery PASS, durable
identity and scientific authority PASS, all duplicate/orphan/contamination
counters zero, applicable browser/service reconciliation PASS, affected M4-01
and M1-M3 regressions PASS, and no shared-resource damage.

Do not commit and do not start M4-03.
