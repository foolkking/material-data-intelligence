# MDI V0 — M3 Final Sealed-Evidence Closeout — attempt-05

## Scope

Close only the external-review defects for M3 attempt-04:

1. Preserve accepted M3/F12 evidence; do not rerun F12, M1/M2 faults, or
   scheduler/fairness experiments.
2. Stage a self-consistent final bundle. The semantic checker must load the
   exact paths that are packaged, especially
   `metrics/provider_cross_process_concurrency.json`.
3. Include `browser_state_inventory.json` with durable/runtime pairing for
   queued, running, provider-retrying, preserved-result, and admission
   rejection states.
4. Include the raw capacity-release evidence referenced by
   `capacity_release_results.json`.
5. Execute exactly one targeted real cross-process transient provider retry
   wave through normal worker/service paths. Record first-attempt transient
   failure, Retry-After, bounded jitter/backoff, inflight ceiling, and
   authoritative-effect counts. Do not call direct adapter threads.
6. Add complete production-change provenance for every M3 production file;
   do not alter production behavior unless the retry-wave exposes a defect.
7. Correct contradictory `VERIFIED`/`incomplete` text in `phase_return.json`.
8. Run the semantic checker from the exact staging directory and again after
   extracting the final ZIP. Run official return validation, verify manifest,
   sizes, SHA256 values, and ZIP CRC.

## Safety and stop gate

- Qualification-only resources may be used. Shared PostgreSQL, Redis, MinIO,
  canonical API/frontend, and unknown processes are never fault targets.
- Before any process operation, revalidate PID, start time, command, cwd,
  PPID, role, and qualification namespace; wait for OS-confirmed exit before
  replacement.
- Preserve dirty working-tree changes. Do not reset, clean, commit, push,
  tag, release, or start M4.
- Final status may be `READY_FOR_REVIEW`, `PARTIAL`, or `BLOCKED`, never
  `ACCEPTED`.
