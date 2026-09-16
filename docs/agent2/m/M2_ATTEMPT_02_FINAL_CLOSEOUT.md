# MDI V0 — M2 final closeout — attempt-02

## Authority and immutable baseline
- External review: M2 attempt-01 = NEEDS_FIX.
- Sealed immutable bundle: `E:\mdi-v0-review\M2_attempt-01.zip`.
- ZIP SHA256: `f476da7fd9e18c42934ceeeba5530557888589600531dc0f897f40da22ae123b`.
- phase_return SHA256: `a5dc5f15c85b595a7615c40bb2ac11f75cc62a24d91d1c0aa8d3f818c464c603`.
- Create only `M2 attempt-02`; expected ZIP `E:\mdi-v0-review\M2_attempt-02.zip`.
- Stop before M3.

## Scope
Do not repeat valid M2 evidence. Reuse by exact attempt/path/SHA256: M2-001 durable boundary matrix; M2-004 authoritative-effect identity and duplicate publication protection; M2-008 recovery scan/lifecycle projection; F05, F07, F08; duplicate delivery; Interpretation-only Result preservation; API restart; 62-tool recovery inventory; F16 N/A; six queue identities; no migration.

Close only the externally identified gaps for M2-002/003/005/006/007:
1. F01 causal worker death.
2. F02 causal mid-Tool worker death.
3. F04 causal crash after verified Artifact and before Result.
4. Result committed / before next-stage enqueue crash.
5. Real upload-success / DB-failure reconciliation.
6. Real Redis-unavailable operation.
7. Real client disconnect.
8. Browser reconnect and exact persisted reopen.
9. Report/Context/source identity preservation on reopen.
10. Exact elapsed-recovery timelines.
11. Explicit delayed duplicate delivery.

## F01 causal sequence
- Persist Job; A claims; A reaches PRE-TOOL barrier.
- Immediately revalidate PID, PPID, start time, exact command, cwd, role and M2 namespace.
- Terminate A, record termination request and OS exit code, and wait until OS confirms A no longer exists.
- Only after `exit_confirmed_at`, permit expiry/recovery and start B.
- B must claim the same Job and publish one Result.
- Hard order: `worker_A_exit_confirmed_at < worker_B_claimed_at`, preferably before B process start.

## F02 causal sequence and accounting
- Use current restartable `structure.coordination_hist` unless a more truthful current Tool is needed.
- A claims attempt 1 and reaches an actual registered Tool-active marker.
- Revalidate, terminate A while Tool is active, and confirm exit.
- Only after exit/expiry, start fresh B; B starts from the durable Job boundary.
- Hard order: Tool active < terminate request <= exit confirmed < B authoritative execution.
- Record separately: physical executions A=1, B=1; A authoritative completed ToolCall=0; B=1; authoritative Results=1.
- Recovery mode exactly `RESTART_FROM_DURABLE_JOB_BOUNDARY`; never claim resume/checkpoint.

## F04 causal process crash
- Tool and verified Artifact(s) already durable; Result count 0.
- Result projector A loads and verifies exact Artifact(s), reaches AFTER_ARTIFACT_VERIFICATION / BEFORE_RESULT_COMMIT.
- Revalidate and terminate A; confirm exit before starting B.
- Fresh B publishes one Result from existing Artifact(s).
- Hard order: artifact verified < A exit confirmed < B start < Result commit.
- Tool/scientific execution counter remains 1; Artifact hashes unchanged; algorithm rerun after Artifact = 0.

## Result-before-next-stage crash
- Commit CURRENT ScientificResult with exact source ObjectVersions and ToolCall count.
- Determine the current next-stage durable Interpretation/child identity.
- Crash owned scheduler/process before next-stage enqueue/ack completes.
- Fresh reconciliation must reuse the same Result and same deterministic next-stage identity; replacement child count 0; ToolCall count unchanged; Result ID unchanged; downstream stage continues.

## Upload-success / DB-failure seam
- Under an exact M2-owned object prefix, write bytes and verify key/size/SHA256.
- Inject a controlled DB failure before authoritative Artifact metadata commit.
- Prove Artifact authoritative row count 0 and ScientificResult count 0.
- Run real orphan/recovery scan. Either safely promote exact staged bytes through the supported contract, or retain/classify/clean only the exact M2 staging object as non-authoritative.
- Never infer completed Artifact merely from bytes.

## F06 real Redis outage
- Persist a Job/child identity that genuinely requires enqueue and ensure it is not already queued.
- Cut only the M2 Redis proxy and invoke the actual enqueue path.
- Require an actual connection failure/typed queue publication failure, not an `already queued/completed` short circuit.
- While cut, durable PostgreSQL identity remains and no replacement entity is created.
- Restore endpoint, reconcile same identity, run fresh worker, and publish one authoritative downstream effect. Shared Redis untouched.

## Real client disconnect
Use a genuine incomplete request: Content-Length exceeds sent bytes and the socket closes before request-body completion, with no completed response. Verify no Dataset/ObjectVersion/science from partial request, then retry with a fresh upload/session and succeed; or durably admit a Turn, disconnect before observing completion, and reconnect with an independent client to the same Turn/Job/Result. A complete HTTP 200 request is not evidence.

## Browser reconnect and exact reopen
Use the current normal product UI, not a new recovery page. Capture real browser evidence before and after closing/disconnecting the browser session and after selected recovery/API restart. Reopen the exact project/research/result route. Prove same project, source/version, turn, Result, Context, Interpretation and Report where applicable, with ToolCall and Result counts unchanged. Pair screenshots with API/DB identifiers.

## Reopen identity completion
Preserve attempt-01 core Interpretation retry evidence. Add before/after: project, exact source ObjectVersion IDs, Context snapshot, Result, Interpretation, Report, turn/session. If the selected workflow lacks a Report, use the current supported Report path once and then reopen it; do not fabricate one. Reopen must not create ToolCall/Result.

## Delayed duplicate delivery
After the first delivery completes authoritatively, deliver the same transport identity later. The handler may run but new Tool execution, authoritative Result and child work must each be zero.

## M1 accepted race provenance
Reuse accepted M1 F03/F10 with exact bundle/path/hash/key IDs unless current M2 code touches fencing/cancellation. Explain why the narrow Interpretation change does not invalidate them.

## Recovery timing
For each executed case record fault requested, fault observed, exit confirmed when relevant, recovery trigger, fresh process start, durable completion, and exact elapsed failure-to-recovery seconds. For proxies record cut enabled, first dependency failure, cut restored, completion.

## Semantic checker
Reject READY unless all causal ordering rules above hold. Also reject missing Result-before-next-stage case; upload DB-failure without real bytes/write receipt; F06 without real Redis dependency attempt; full-body/HTTP-200 client “disconnect”; missing browser reconnect; reopen identity changes; delayed duplicate creates science; F04 algorithm rerun; unresolved M2 orphan; duplicate Result; shared-resource damage.

## Required current artifacts
`phase_return.json`, `change_summary.md`, corrected F01/F02/F04, `result_before_next_stage_crash.json`, `upload_success_db_failure.json`, `artifact_publication_reconciliation.json`, corrected F06, corrected client disconnect, `browser_reconnect_recovery.json`, browser before/after/recovery screenshots, `result_interpretation_recovery.json`, `reopen_identity_preservation.json`, `delayed_delivery_results.json`, `recovery_timeline_summary.json`, `before_after_effect_counts.json`, `M1_accepted_race_provenance.json`, semantic checker and `service_state.txt`. Reused attempt-01 evidence must include exact provenance/hash.

## Safety and implementation discipline
Expected work is qualification harness/timing/evidence. Change production only if a correctly executed missing case exposes a real owner-layer defect, then reproduce, minimally fix, test and rerun. Use only qualification-owned endpoints/proxies/data/processes. Never stop shared PostgreSQL/Redis/MinIO, FLUSHALL/FLUSHDB, kill unknown PID, delete user science, reset/clean/checkout/commit/push/tag/release/remote CI, modify accepted evidence, or start M3. No migration/public-limit uplift unless explicitly and truthfully required.

## Closure and sealing
All M2-001..008 must be closed. Require F01/F02/F04/result-before-next-stage/upload-DB-failure/F05/F06/F07/F08/client disconnect/browser reconnect/reopen identity/duplicate/delayed delivery PASS; duplicate Results=0; read recomputation=0; unresolved owned RUNNING=0; shared damage=0.
Run attempt-02 semantic checker, official `validate_return.py --seal`, build `E:\mdi-v0-review\M2_attempt-02.zip`, verify CRC/manifest and compute ZIP/phase hashes. Return READY/PARTIAL/BLOCKED and stop before M3.
