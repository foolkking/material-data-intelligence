# MDI V0 — M1 attempt-01

## Durable ownership, leases, fencing and truthful recovery

Authoritative program state supplied by the user on 2026-09-14:

- R0, Pre-M0...Pre-M6 and M0 are externally accepted.
- Accepted M0 baseline: `E:\mdi-v0-review\M0_attempt-02.zip`,
  SHA256 `3979c42b3c70c09e8ef5a7de4019892a931286d43cd4a843e75c4822d88d330d`;
  phase-return SHA256
  `66203564d376792ff44f4664045de51a9e554756d02ccb52ded3309beaf55db6`.
- Execute `M1 attempt-01`, produce
  `E:\mdi-v0-review\M1_attempt-01.zip`, and stop before M2.

This file is the repository-owned execution specification for the full M1
prompt authorized in the current task. It preserves the complete operative
requirements below; M0 and all accepted Pre-M/J evidence are immutable inputs.

## Scope and ownership

M1 owns exactly `M1-001`...`M1-008`:

1. Identify and extend the existing single durable owner/attempt/state
   authority with claim, renewal, expiry and reclaim using transactional
   row-lock/CAS and an attempt/fencing identity.
2. Fence stale/lost attempts from authoritative terminal state, Result,
   verified/promoted Artifact, dependent child scheduling, Interpretation and
   Report scheduling. Heartbeat is liveness only.
3. Use bounded server-controlled lease time; handle skew, delay, renewal loss,
   late renewal/completion and cancellation/terminal precedence. Derive policy
   from M0 measurements and product timeouts, not arbitrary `updated_at` age.
4. Classify every registered Tool exactly once as
   `RESUMABLE_CHECKPOINT`, `RESTARTABLE_IDEMPOTENT_ATTEMPT`, or
   `NONRESUMABLE_BOUNDED_RETRY_OR_USER_ACTION`.
5. Permit checkpoints only for Tools with a stable scientific continuation
   contract binding source versions, parameters, method/implementation,
   attempt/fence and integrity. Partial state is not completed science.
6. Cancellation stops new autonomous cycles, requests supported cancellation,
   preserves completed science, and separately tracks request,
   acknowledgement, child termination request/actual termination and durable
   terminal state.
7. Preserve all six queue identities/handlers and add only a narrow read-only,
   durable-source-backed lifecycle projection.
8. Migrate only if durable correctness requires it; test isolated upgrade,
   historical reads and rollback/restore. A clean Git tree is not required.

M1 does not own generic retry/durable-boundary/artifact/provider redesign,
queue replacement, M2-M5, new science or a new Agent framework. There must be
one durable authority, not a Redis/UI/worker-local parallel state machine.

## Required reading and frozen inputs

Read current governance, conflicts/audit, return protocol, `phases/M1.md`,
`cases/fault_matrix.json`, current Job/Turn/ToolCall/Result/Artifact/Research/
worker/queue/cancellation/recovery code, and accepted M0 artifacts:
environment, ownership, fault plan, workload matrix, baseline measurements,
success criteria and tiers. Locate Completion Pack files by repository/source
authority when their paths are outside the application root.

Do not modify M0 attempts. Old PIDs are not current ownership proof.

## M1 isolated qualification environment

Create a new M1-owned Project/data boundary and isolated PostgreSQL DB/schema,
Redis DB/namespace, MinIO bucket/prefix, API and workers using free actual
ports/DB numbers. Shared services are excluded. Before any process action
revalidate PID, start time, command, cwd, PPID and qualification namespace;
abort on mismatch.

## Required pre-change analysis

Before implementation create:

- `ownership_authority_map.json` for Research Turn, Job, ToolCall/attempt,
  Result publication, Artifact promotion, Interpretation and Report scheduling,
  including durable model/table, state/owner/attempt/CAS fields, owners,
  transaction/lock behavior, worker-local state, Redis role and DB role.
- `M1_gap_analysis.md`, classifying claim, renewal, expiry, reclaim, fencing,
  completion/publication/scheduling, cancellation, checkpoint and projection
  as `ALREADY_CORRECT`, `MISSING`, `INCORRECT` or `NOT_APPLICABLE`.
- `ownership_state_machine.md` with legal transitions, predicates, transaction
  owner, attempt/fence checks and terminal-state precedence.
- `lease_policy.json` with DB/server time authority, default and qualification
  timing, cadence/deadline/expiry/grace/reclaim rules and M0-derived rationale.
- `heartbeat_semantics.md`.

Do not implement from documentation gaps alone.

## Durable ownership and fencing invariants

- Reclaim must create a distinct durable attempt/fence.
- Worker-local wall clock is never authoritative.
- Ambiguous renewal beyond the allowed boundary means ownership is lost for
  final publication, even if local computation finishes.
- Correct-owner renewal may continue; stale/late renewal must fail and cannot
  alter the new owner.
- All authoritative write boundaries must enforce current attempt ownership:
  terminal Job/ToolCall transition, Result publication, Artifact verification/
  promotion, Interpretation/Report and next autonomous child scheduling.
- Temporary/staged bytes are not a ScientificResult or verified Artifact.
- Terminal states cannot be renewed, reclaimed or resurrected.
- N local attempts may run, but at most one current authoritative completion,
  Result, verified Artifact and dependent scheduling effect may exist.
- Content-hash equality is not permission to publish duplicate Results.
- Authorization and exact source/ObjectVersion scope remain enforced.

## Required real acceptance executions

### Two-worker claim race

Two actual M1-owned workers concurrently claim the same supported eligible Job,
using a synchronization barrier if needed. Capture worker identity and
DB/server timing. Require two attempts, exactly one authoritative owner/fence
and no duplicate authoritative scientific effect. Produce
`lease_claim_race.json`.

### F03 — old worker late result after reclaim

Run the actual qualification-owned sequence: worker A claims and begins a real
deterministic Tool; renewal is deliberately prevented or the owned worker is
safely paused; lease expires; worker B reclaims with a new attempt/fence and
completes authoritatively; A resumes and attempts late completion/publication.
Require rejection of A's stale terminal write, Result, verified Artifact and
dependent scheduling, with exactly one authoritative Result. Revalidate process
ownership immediately before pause/resume/termination. Define expected effect
counts before execution and compare actual. Produce
`F03_old_worker_late_result.json`, `lease_expiry_reclaim_trace.json`,
`stale_completion_fencing.json`, `f03_effect_counts.json` or consolidated
`scientific_effect_counts.json`. F03 cannot pass from unit tests alone.

Test late renewal after B's reclaim; it must be rejected without changing B.

### Terminal/cancellation races and F10

Test completion-before-cancel, cancel-before-completion, cancel-vs-renewal,
cancel-vs-expiry/reclaim and stale completion after cancel according to current
contract. Execute real F10 through the cancellation API against M1-owned active
heavy work. Track request/persisted/worker-observed timestamps and child
cancellation/termination separately. Preserve completed science, stop new
autonomous cycles, prevent stale resurrection, enumerate post-test processes
and require no unintended owned child orphan. If no child exists use
`NOT_APPLICABLE`; never claim unsupported termination. Produce
`F10_user_cancellation.json` and `cancellation_race_results.json`. API execution
is required; unit-only evidence is insufficient.

### Tool recovery inventory and F16

Enumerate every current Tool with implementation version, scientific/execution
boundary, child/provider behavior, one recovery class, reason, durable boundary,
checkpoint support, retry/side-effect safety and source/parameter binding.
Never call restart “resume”.

If a real checkpointable Tool exists, execute F16 at a declared stable
checkpoint and reject source, parameter, method and integrity mutations. If
none exists, record `F16 = NOT_APPLICABLE_WITH_CURRENT_TOOLSET` and execute one
real restartable indivisible Tool recovery from the beginning with exactly one
final authoritative Result. Partial/checkpoint/staged output cannot become
science. Produce `F16_checkpoint_or_restart.json`,
`tool_recovery_capabilities.json` and `checkpoint_validation_results.json`.

### Queue and lifecycle projection

Snapshot before/after six queues and handler/subscription mappings; require no
rename, merge or redirection. Add/test the smallest read-only durable lifecycle
projection necessary to report factual execution state, display-safe attempt,
lease status/expiry, recovery/retry, cancellation and stale rejection while
not exposing secrets or allowing writes. Verify projection during F03/F10 with
API/read-model evidence; browser evidence is optional. Produce
`queue_identity_preservation.json` and `lifecycle_projection_results.json`.

### Migration decision

Produce `migration_decision.md`: `NO_MIGRATION_REQUIRED` or
`MIGRATION_REQUIRED`. If required, first test upgrade on isolated M1 DB,
historical Job/Turn/Result reads, new ownership writes and rollback/restore,
then apply only if correctness requires it. Historical rows remain readable
with truthful legacy/null semantics; do not fabricate old leases/owners.
Produce `migration_test_results.json` only if required.

## Testing requirements

Use real PostgreSQL concurrency for ownership tests where applicable. Cover:
concurrent claims; correct/stale renew; late renew after reclaim; correct/stale
completion; stale Result publication; cancel-before/after completion;
cancel-vs-reclaim; terminal state cannot renew/reclaim; authorization/project
isolation. Use deterministic Tool paths and an independent scientific oracle.
Do not use unnecessary provider calls, unbounded retry, arbitrary sleeps to
hide races, or M5 soak/capacity claims.

Qualification lease overrides may be short only if explicitly recorded and
exercise the same code path; do not change public/default policy silently.

## Required artifacts

Create a fresh M1 attempt directory containing at minimum:

`phase_return.json`, `change_summary.md`, `M1_gap_analysis.md`,
`ownership_authority_map.json`, `ownership_state_machine.md`,
`lease_policy.json`, `heartbeat_semantics.md`, `lease_claim_race.json`,
`lease_expiry_reclaim_trace.json`, `stale_completion_fencing.json`,
`cancellation_race_results.json`, `tool_recovery_capabilities.json`,
`checkpoint_validation_results.json`, `queue_identity_preservation.json`,
`lifecycle_projection_results.json`, `migration_decision.md`,
`migration_test_results.json` only if needed,
`F03_old_worker_late_result.json`, `F10_user_cancellation.json`,
`F16_checkpoint_or_restart.json`, `scientific_effect_counts.json`,
`qualification_environment.json`, `owned_resource_manifest.json`,
`qualification_process_registry.json`, `test_logs/`, `fault_logs/`,
`service_state.txt`, and, if code changes, `changes.patch` plus focused logs.

## Final acceptance gate

Before `READY_FOR_REVIEW`, close M1-001...M1-008 and mechanically prove:

- two-worker race has exactly one owner/fence;
- expiry/reclaim creates a new fence;
- late completion/publication/dependent scheduling and late renewal reject;
- duplicate authoritative Results = 0;
- cancellation precedence is coherent and post-cancel orphan children = 0;
- every current Tool is classified; fake partial resume = 0;
- all six queues are preserved;
- lifecycle projection is read-only and durable-source-backed;
- migration decision is truthful and tested if used;
- shared resource damage = 0.

Generate the phase template with `tools/phase_brief.py M1`, validate/seal with
`tools/validate_return.py`, build
`E:\mdi-v0-review\M1_attempt-01.zip`, verify ZIP CRC and compute ZIP and
phase-return SHA256. The agent may return READY_FOR_REVIEW, PARTIAL or BLOCKED,
never ACCEPTED.

## Protected state and stop gate

Preserve accepted Pre-M/M0 and frozen J evidence, all uncommitted work and
shared/user resources. No reset, clean, destructive checkout, commit, push,
tag, release, remote CI, shared Redis flush, shared DB destruction, existing
user-data fault injection, unknown PID signal, fake checkpoint/resume,
heartbeat-as-progress, UI ownership, arbitrary infrastructure migration or
public limit uplift. Keep existing services healthy.

Do not start M2/M3/M4/M5/M6/FINAL0. Stop after producing M1 attempt-01 for
external review.
