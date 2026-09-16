# MDI V0 — M3 FINAL TARGETED CLOSEOUT

## attempt-03

Authoritative external decision: M3 attempt-02 is `NEEDS_FIX / PARTIAL`.
M4 is not authorized. Attempts 01 and 02 are immutable. Create
`E:\mdi-v0-review\M3\attempt-03` and the final review bundle
`E:\mdi-v0-review\M3_attempt-03.zip`. Stop before M4.

## Accepted evidence to preserve by exact source/hash

- M3-004 resource/admission evidence: 64 MiB current upload limit, typed 422
  for a 300 MiB declaration, zero false Result and zero orphan science.
- Accepted qualification-safe 4096-atom import.
- Six queue identities preserved.
- Attempt-01 4096-atom RDF failure is
  `INVALID_F12_WORKLOAD_SELECTION`; it is not a supported heavy F12 case.
- Current per-project active Research limit is four.
- Existing project protection remains sufficient unless this attempt proves
  cross-project monopolization.
- Public limits unchanged; shared-resource damage remains zero.

Do not repeat accepted upload-over-limit work unless a change invalidates it.

## Final F12 contract

F12 is measured at the real Job/Tool/ScientificResult boundary, independently
of downstream Interpretation:

- Heavy workload: accepted 4096-atom NaCl fixture with registered
  `structure.coordination_hist`.
- Small workload: accepted small NaCl structure with registered
  `structure.rdf`.
- Both travel through real product admission, Plan, durable Job, `mdi-jobs`,
  worker, ToolCall and Result publication. No direct Tool invocation or fake
  rows.
- Heavy solo control must establish exact Project, Turn, Plan, Job, ToolCall,
  source object/version and Result IDs plus enqueued/start/result timestamps.
- Frozen queued RDF qualification bound is `34.9059s`
  (`3 * 11.6353s`); it is not a public SLA.
- The `0.25s` local bound applies only to a comparable local/no-provider
  operation.
- Derive queue wait from authoritative enqueued and execution-start
  timestamps, and running time from execution start to Tool/Result completion.
  Resource wait is `NOT_APPLICABLE` only when there is no separate gate.
- Normal+heavy: start the heavy Tool, then enqueue small RDF on the same
  `mdi-jobs` resource. Both Results and scientific oracles must pass; small
  queue wait must be within 34.9059s; no starvation, authorization bypass,
  dependency reorder or duplicate Result.
- Heavy+heavy: two actual 4096-atom coordination Jobs in separate projects.
  Current one-worker serialization is acceptable if A runs, B queues, then B
  runs; both Results must pass.
- Do not add a scheduler if current behavior passes.

## Resource-bound contract

Regenerate `resource_budget_matrix.json` for interactive, normal scientific,
heavy CPU/memory, provider/model, large transfer/parser/archive and
artifact/object-store classes. Record admission owner, execution owner,
actual/configured worker count, exact current concurrency bound and scope,
waiting representation, release owner, over-limit behavior and evidence.
Current worker topology is a valid bounded classification only when verified
from code and runtime. No applicable final row may remain partially bounded,
unbounded or unknown.

## Provider caller topology and jitter

Create `provider_caller_topology.json` and enumerate every current model caller,
including interpretation, reports, turn/planning workers, API and any other
path. Record role/queue, worker count, purpose and possible concurrency.

Attempt-02 established fixed 0.25s backoff and zero jitter. This is a genuine
M3-003 production gap. Implement the narrowest bounded retry-delay correction:

- base delay honors the current backoff and valid provider `Retry-After`;
- add real bounded production jitter;
- cap total delay;
- keep bounded attempts;
- qualification may inject a deterministic RNG seed, but production jitter
  must not be zero.

Only add a shared provider gate if complete topology plus cross-process
measurement proves the current finite worker ceiling is insufficient. Any
gate is coordination only, with finite capacity, bounded acquisition,
owner/expiry and exactly-once release; it is not scientific authority.

## Integrated F09 contract

Final F09 must begin from real completed ScientificResults and run real durable
Interpretation work through `mdi-agent-interpretations`, the actual worker,
production adapter and a qualification-only loopback provider fault proxy.
Direct provider calls are focused regression only and cannot close F09.

Run:

1. HTTP 429 + valid `Retry-After`, then success.
2. Controlled provider timeout, then success.
3. Transient failures through configured attempt exhaustion, leaving the
   Result preserved and Interpretation truthfully retryable/bounded-failed.
4. Actual current provider-worker topology concurrency and retry-wave test.

Record Result/Turn/Interpretation Job/ID, logical request, physical attempts,
per-attempt timestamps, HTTP/error, Retry-After, base delay, jitter, actual
delay, inflight concurrency, declared ceiling and final state. Require bounded
attempts, measured jitter/desynchronization, no retry storm, no Tool
recomputation, no Result loss/duplication, one authoritative Interpretation
where successful, and no runaway child Jobs.

Enumerate the scholarly path. If it shares the controller, prove reuse; if it
has a separate current adapter, run bounded smoke; if absent from current V0
runtime, record `NOT_APPLICABLE_TO_CURRENT_M3_RUNTIME` with code/config proof.

## Capacity-release contract

Attempt-02 early cancellation cycles are not sufficient. Execute:

- Project limit: create four genuinely active turns, observe typed fifth
  rejection, durably cancel one, and prove a replacement is admitted without
  active count exceeding four.
- Queued cancellation: heavy A running, B queued, cancel B through supported
  API before it executes; B must produce no Tool/Result, A remains correct,
  and C subsequently runs.
- Running cancellation: confirm supported Job is RUNNING, issue user/API
  cancellation, preserve M1 fencing/no stale publication, then prove capacity
  reuse.
- Timeout/provider release: after F09 timeout/exhaustion, inflight provider
  capacity returns to baseline and a subsequent request succeeds.
- At least five bounded cycles. Measure actual applicable counters before and
  after: active Research, queued/running Jobs, provider inflight/gate permits,
  DB pool or temporary/staged resources where exposed. Do not fabricate
  counters.
- Execute cancel-vs-completion or cancel-vs-timeout and prove exactly one
  release, no negative/above-max counter and no duplicate science.

## Timing, health and user states

Build a read-only operational projection from current durable Job/M1/RQ/provider
facts. Distinguish queued, running, retrying, inherited recovering/expired and
waiting-for-resource only if a real gate exists. Include queue age/wait,
running duration and provider backoff. Add safe aggregate visibility:
queued/running/retrying counts, oldest queue wait and starved-candidate count
derived from the frozen bound. A waiting task is not scientific failure.
Prefer no migration.

Primary user states must remain simple: Queued, Running, Waiting for resources
only when factual, Retrying, Result completed while Interpretation is
temporarily unavailable/retrying, and Failed/retry later. Do not expose Redis
keys, PIDs, fencing tokens, credentials or provider coordination keys.

Use the established real production frontend build plus a qualification-only
loopback reverse proxy to the M3 isolated API. Do not substitute canonical API
data. Capture truthful applicable browser evidence for queued/waiting, running,
provider retrying, preserved Result during provider failure and typed admission
rejection. Do not fabricate states.

## Change/test discipline

Expected legitimate production change: bounded provider jitter. Other changes
require measured gaps. Do not change science algorithms, science families,
Result authority, M1 fencing, M2 publication, public limits or six queues.
Prefer `NO_NEW_MIGRATION`.

Run focused tests for retry-delay calculation, Retry-After, jitter,
exhaustion, actual concurrency ceiling, gate release if added, task timing and
state projection, preserved Result and cancel/timeout release. Re-run relevant
M1/M2 regressions if their owner layer changes.

## Required evidence

At minimum:

- `phase_return.json`, `change_summary.md`, `M3_gap_analysis.md`
- `resource_budget_matrix.json`
- `provider_caller_topology.json`, `provider_control_matrix.json`,
  `provider_retry_measurements.json`
- `fairness_policy.json`, `queue_fairness_results.json`,
  `task_timing_breakdown.json`
- `capacity_release_results.json`, `task_health_projection.json`
- accepted admission/transfer/effect/queue evidence by exact provenance
- `qualification_environment.json`, `owned_resource_manifest.json`,
  `qualification_process_registry.json`
- `validate_m3_semantic_coherence.py`
- truthful browser images, logs, metrics and `service_state.txt`
- `changes.patch` and `focused_regression.log` if code changes.

The semantic checker must reject READY for any unbounded class, import-only
F12, Interpretation-dependent F12 verdict, missing numeric queue wait, direct
adapter-only F09, missing integrated IDs/jitter/concurrency, retry overflow,
Result/Tool violations, incomplete release coverage/baseline, missing
blocked/starved health or browser evidence, changed queues or shared damage.

## Final gate and packaging

`READY_FOR_REVIEW` requires M3-001 through M3-007 implemented and verified,
M3-008 implemented or satisfied by existing evidence, F09/F12 and all detailed
subcases passing, all classes bounded, measured jitter/concurrency, capacity
returned to baseline with zero double release, useful browser/health evidence,
six queues preserved and zero shared damage.

If any gate remains open, return `PARTIAL` or `BLOCKED`,
`NEXT_PHASE_PROPOSED=NONE`, and do not start M4.

Run:

```powershell
python <attempt-03>\validate_m3_semantic_coherence.py
python tools\validate_return.py <attempt-03>\phase_return.json --seal
python tools\build_review_bundle.py <attempt-03>\phase_return.json `
  --output E:\mdi-v0-review\M3_attempt-03.zip
```

Verify semantic coherence, official format/evidence integrity, ZIP CRC and
manifest, and compute ZIP/phase-return SHA256. Preserve all accepted evidence,
dirty worktree and shared services. No reset, clean, commit, push, tag,
release, remote CI, shared-service stop/flush, unknown PID kill or user-data
test. Before stopping/restarting any qualification process, revalidate PID,
start time, command, cwd, PPID, role and namespace; wait for OS-confirmed exit
and verify ports/resources released.

