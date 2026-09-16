# MDI V0 — M0 attempt-01

Status: AUTHORIZED / IN_PROGRESS  
Date: 2026-09-14  
Canonical repository: `E:\1project\mdi-b0-5a1`  
Review output: `E:\mdi-v0-review\M0\attempt-01`  
Expected ZIP: `E:\mdi-v0-review\M0_attempt-01.zip`

## Accepted baseline and stop boundary

- R0 and Pre-M0 through Pre-M6 are externally accepted.
- Accepted sources are immutable, including Pre-M5 attempt-11 and Pre-M6
  attempt-03.
- M0 may return `READY_FOR_REVIEW`, `PARTIAL`, or `BLOCKED`; it may not
  self-assign `ACCEPTED`.
- Stop before M1. Do not start M1-M6 or FINAL0.
- Preserve the genuine browser 125/150/200 zoom limitation as
  `NONBLOCKING_WITH_LIMIT`; do not simulate it.

## M0-owned requirements

M0 owns exactly `M0-001` through `M0-008`.

1. Build workload classes from accepted real traces: short interactive,
   ordinary analysis, CPU/memory-heavy, long ToolCall, provider task, large
   Artifact, and long history.
2. Record the exact qualification hardware, OS, browser, runtimes,
   dependencies, storage placement, queue and worker configuration. Separate
   contract limits, Pre-M tested limits, M0 single-workload observations, and
   M0 concurrent observations.
3. Create qualification-owned Project/data and the narrow supported
   PostgreSQL, Redis, MinIO, queue/worker namespace boundaries. Shared parent
   services must be explicitly excluded from destructive actions.
4. Register every future fault target by PID, start time, command, cwd,
   parent, role, namespace, and ownership proof. Revalidate the full identity
   immediately before injection and abort on any mismatch.
5. Prove a small isolated backup → restore → reopen → export round trip that
   preserves source, ObjectVersion, Result, Report, scientific metadata and
   coherent references. Restore must not overwrite the source environment.
   Create a migration recovery plan before future necessary migrations.
6. Freeze measured duration/concurrency/workload tiers while retaining all
   current autonomy, Tool, provider and Context bounds. Freeze an M5
   continuous mixed-real-work target of at least 120 minutes; M0 does not run
   the soak.
7. Define baseline-relative latency, timeout, memory, queue, effect-count,
   fault, recovery, integrity and permission criteria before later campaigns.
8. Define Stage A baseline, Stage B near-normal, Stage C mixed heavy plus
   interactive, Stage D later-phase recovery/fault, and Stage E M5 soak.
   Public limit uplift requires a current user need, measured bottleneck,
   narrow owner and renewed scientific/resource validation.

## Required inputs

Read and apply:

- Completion Pack governance execution/clarification and return protocol.
- `phases/M0.md`.
- S04, S10 and S15.
- `cases/fault_matrix.json` and `cases/scientific_journeys.json`.
- Accepted Pre-M6 attempt-03 handoff, envelope and integrated journeys.
- Final accepted Pre-M5 workload/accounting/resource evidence.

## Accepted pointer errata

Create `pre_m6_pointer_errata.json` without editing accepted bundles:

- verify the exact accepted Research failure/recovery artifact for turn
  `46095d1c-1f97-412f-9f79-58001793e264`;
- verify the exact accepted `/tasks` screenshot path/hash from Pre-M3;
- record old pointer, corrected pointer/hash, source attempt and reason;
- classify as evidence hygiene only, with accepted decisions, science and
  runtime behavior unchanged.

## Measurement and effect baseline

Run a small qualification-owned M0 baseline campaign, not the M5 soak. Cover
interactive latency, ordinary analysis, heavy-resource evidence, provider,
artifact and history/context paths with the smallest non-wasteful set.

Before each selected execution define expected Job, Tool execution, Result,
Artifact, Report and provider-call counts/ranges; compare actual effects.
Capture timestamps, duration, queue wait/execution where exposed, API/worker
RSS, queue depth before/during/after, safe DB observations, object bytes,
scientific/user completion and independent invariants. Use `NOT_EXPOSED` with
reason rather than guessed values.

## Isolation and safety

- Use only qualification-owned data and processes.
- Never flush shared Redis, stop the original PostgreSQL, alter credentials,
  delete existing user objects, kill unknown PIDs, or wildcard-delete MinIO.
- If a component has no independently isolated supported mode, document the
  exact narrower supported isolation; do not fake isolation.
- Perform cleanup and fault ownership as dry runs only in M0.
- One harmless fault-ownership dry run must capture and re-resolve the full
  identity of a qualification-owned process without killing it.

## Required acceptance executions

1. Qualification ownership and cleanup dry-run excludes all shared/user
   resources.
2. One real qualification-owned upload/request persists, the request-process
   state is no longer relied on, and a fresh qualification-owned worker
   consumes the actual queue path and persists a valid Result.
3. One small isolated backup/restore/export round trip preserves lineage,
   scientific metadata, permissions and usable export.
4. Workload cases, baseline measurements, expected effect counts,
   duration/concurrency tiers, M5 target, success criteria and fault/recovery
   deadlines are frozen before later phases.

## Required artifacts

Create at least:

- `phase_return.json`, `change_summary.md`
- `pre_m6_pointer_errata.json`, `M0_input_provenance.json`
- `M_workload_matrix.json`, `M_workload_tiers.json`
- `qualification_environment.json`, `dependency_versions.txt`
- `queue_worker_inventory.json`, `owned_resource_manifest.json`
- `operating_envelope_baseline.json`, `baseline_measurements.json`,
  `effect_count_baseline.json`
- `FAULT_INJECTION_PLAN.md`, `fault_target_registry.json`,
  `fault_ownership_dry_run.json`, `cleanup_dry_run.json`
- `test_data_recovery_record.json`, `migration_recovery_plan.md`
- `M5_campaign_target.json`, `M_success_criteria.json`,
  `M_STAGED_QUALIFICATION_PLAN.md`, `START_STOP_RUNBOOK.md`
- `service_state.txt` and `logs/`, `metrics/`, `backup_restore/`, `exports/`

Production changes are not expected. Qualification helpers/runbooks are
allowed. No speculative infrastructure migration or public-limit uplift.

## Validation and packaging

Generate the M0 template with Completion Pack `phase_brief.py`, populate real
evidence, then seal with `validate_return.py` and build
`E:\mdi-v0-review\M0_attempt-01.zip`. Require format/evidence integrity and ZIP
CRC validity; compute ZIP and phase-return SHA-256.

Keep services healthy and running after completion.
