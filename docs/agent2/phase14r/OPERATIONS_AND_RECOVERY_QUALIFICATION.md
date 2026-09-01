# Operations and Recovery Qualification

## 2026-08-30 local same-stack process recovery

After the qualification processes exited, the current PostgreSQL data
directory, MinIO object directory and Redis database were retained. The stack
was restored without recreating scientific records:

```text
PostgreSQL 127.0.0.1:55434 = accepting connections
Redis 127.0.0.1:6379/13 = retained and reachable
MinIO 127.0.0.1:9000 / mdi-artifacts = reachable
API 127.0.0.1:8000 = running
frontend 127.0.0.1:3000 = running
canonical Redis workers = running
```

`/health/runtime` then reported PostgreSQL, Redis, MinIO, Redis worker and the
configured DeepSeek provider as `ok`. Task/Notification browser state rebuilt
from persisted backend state (17 tasks / 7 terminal notifications), and the
offline/reconnect banner accurately stated that server work may continue.
This is process-recovery evidence, not a substitute for the broader alerting,
quota and long-duration soak gates.

Phase 14-R must qualify the existing service topology rather than introduce a
new deployment platform:

```text
PostgreSQL = scientific identity/state/provenance authority
Redis = queue/cache/transient state
MinIO = source and Artifact bytes
API + real workers + configured provider
```

Required drills:

* PostgreSQL backup/restore followed by scientific identity and provenance
  integrity checks.
* MinIO source/Artifact backup, checksum validation, restore and bounded
  missing-object behavior.
* Redis restart/loss with PostgreSQL/MinIO retained; queued work must recover
  or surface a truthful failure without changing scientific authority.
* Health/queue/worker/pool monitoring, stuck-job visibility and bounded
  upload/Dataset/Artifact/concurrency/provider resource limits.

## 2026-08-29 same-stack recovery drill

The current PostgreSQL/Redis/MinIO/API/worker/frontend stack remained online
throughout the qualification. The browser-facing runtime continued to report
PostgreSQL, Redis, MinIO, Redis-backed workers and the configured DeepSeek
provider as healthy.

### PostgreSQL

`pg_dump` created a custom-format backup of `mdi`; `pg_restore` loaded it into
the isolated audit database `mdi_phase14r_restore_20260829_01`. The restored
database is intentionally retained as bounded recovery evidence. The dump is
1,359,213 bytes with SHA-256:

```text
1f6cef65bf04798a1ff83bae6623148091c5baf7f478bf06f3ba8e70b3878f6f
```

Source and restored counts matched for all checked authority tables:

```text
scientific_objects                         134
scientific_object_versions                 162
scientific_object_relationships              0
research_turns                             257
jobs                                       164
tool_calls                                 206
artifacts                                  811
scientific_result_snapshots                112
agent2_scientific_interpretations          115
reports                                     18
agent2_scientific_report_snapshots          17
```

Both databases report Alembic
`0025_agent2_scientific_selection`. The restored database contains zero
orphan `ScientificObjectVersion` rows and zero invalid current-version
pointers.

### MinIO

A bounded existing object from `mdi-artifacts` was copied into the isolated
bucket `mdi-phase14r-recovery-20260829-01`, read back as a backup, restored to
a second key and read again. Source, backup, restored and post-drill source
SHA-256 values all matched:

```text
4e34572e413c39ed6ac67003bcc6b3c0c101547f755d480f198483337a710b47
```

The original object remained unchanged. A deliberately absent object failed
closed with HTTP 404. The first probe also found local environment-file
credential drift relative to the running launcher; it failed before listing
or mutating buckets. The successful drill used the credentials of the actual
running MinIO process without exposing them in evidence.

### Redis

The production-style Redis on `6379/13` and all five application workers were
left running. A separate no-persistence Memurai instance on port `6380` was
used to prove transient-loss semantics: a qualification key existed before
forced process loss and was absent after restart. PostgreSQL scientific
authority counts remained `164 jobs / 206 ToolCalls / 811 Artifacts /
112 Result snapshots`, and the primary Redis remained `PONG`. The isolated
instance was then stopped.

The deterministic queue recovery regression proves that a publication
failure reconciles and republishes the same persisted Job identity:

```text
test_queue_publish_failure_reconciles_the_same_job_identity = PASS
test_dispatch_is_idempotent_and_uses_identity_only_queue_payload = PASS
```

### Runtime health

```text
PostgreSQL connections: active 1, idle 10
idle-in-transaction: 0
canonical workers: 5, all idle
canonical queues: no queued/executing work
health/runtime: PostgreSQL + Redis + MinIO + Redis worker + DeepSeek = OK
```

RQ inspection initially showed 208 historical `mdi-agent2-phase2..8-*` test
queue registrations. The service fixtures deleted their RQ Jobs but not the
queue registrations. Successful cleanup was added to the Phase 2–8
service-backed harness, including fixture `finally` paths. A fresh campaign
passed:

```text
Phase 2–5 = 5 passed
Phase 6–8 = 10 passed
test queue registrations before/after = 208 / 208
touched Ruff = PASS
```

One old test queue still contained a Redis wakeup while its authoritative
PostgreSQL Job and Turn were already `FAILED`; no test queue had started,
scheduled or deferred work. All 208 strict test registrations and that
orphan wakeup were removed. PostgreSQL failure evidence was retained.
Canonical queues and MinIO data were not changed.

Two canonical workers had also exited because their historical launcher used
the bounded two-hour idle timeout. A no-secret recovery launcher restored
planning and execution workers without restarting the three surviving
workers. Final state:

```text
canonical queues = 5, all depth 0
canonical workers = 5, all idle
test queue registrations = 0
```

Alert thresholds, resource/quota enforcement and a repeatable production
runbook remain open.

Recovery drill status: `PASS`.

Overall R11 operations maturity status: `PARTIAL`.

## Repeatable redacted operations snapshot

The repository now includes:

```text
apps/api/mdi_api/operations.py
scripts/phase14r_operations_snapshot.py
```

The script reads the normal runtime configuration, but its output contains no
database URL, Redis URL, MinIO credentials, provider key, or filesystem path.
It reports:

```text
PostgreSQL connection states and pool counters
idle-in-transaction
stale active vs waiting ResearchTurn states
stale queued/running/cancel-requested Jobs
canonical RQ queue depth/started/failed/recent-failed counts
worker count/state
MinIO bucket reachability
```

Example qualification invocation:

```text
uv run python scripts/phase14r_operations_snapshot.py \
  --stale-minutes 15 --queue-depth 100 --minimum-workers 5
```

The first current-stack snapshot correctly returned `attention`, not a false
green:

```text
PostgreSQL: active 1 / idle 8 / idle-in-transaction 0
pool: size 5 / checked-out 0 / overflow -4
canonical workers: 5 idle
canonical queue depth: 0
recent RQ failures (15-minute window): 0
retained historical failed-registry records: 15
MinIO: OK
stale non-terminal ResearchTurns: 141
stale active automatic-stage ResearchTurns: 9
stale queued/running Jobs: 1
```

Inspection showed that the nine active-stage Turns belong to historical
Agent2 service qualification Projects and the stale Job is
`job_p6_1` (`created_by=test_user`, Project `Phase 6 #1`). Other old
`RECEIVED`, `PLAN_READY`, `RESULT_PENDING`, and `RESULT_READY` rows are
reported as waiting boundaries rather than automatically classified as stuck.
The 15 RQ failures are retained historical diagnostics and none occurred in
the current 15-minute alert window.

This closes the missing repeatable snapshot and recent-vs-retained failure
classification. It deliberately does not delete or mutate persisted
qualification evidence. A production data-hygiene/reconciliation policy,
alert delivery, concurrency/provider quotas, and deployment runbook remain
open, so R11 remains `PARTIAL`.
# Direct diagnostic invocation (2026-08-29)

The operations snapshot script self-bootstraps `apps/api` from the repository
root, so the documented diagnostic command no longer requires a shell-level
`PYTHONPATH` alias. Runtime configuration remains supplied by the caller and
the output remains redacted.

## 2026-08-30 API and scientific communication worker restart

The current-worktree API, Interpretation worker and Report worker were rolled
while PostgreSQL, Redis, MinIO, frontend and the remaining Plan/Job/Result/Turn
workers stayed available. Worker launcher scripts now allocate unique
timestamp/process-qualified RQ worker names, avoiding the stale-name collision
that previously prevented a stopped local worker from restarting.

Verified current identities:

```text
API listener = 127.0.0.1:8000
Interpretation worker =
  phase14r-current-interpretations-20260831-035900-16760
Report worker =
  phase14r-reports-durable-55434-20260831-035900-15584
```

After restart `/health/runtime` reported:

```text
database = postgresql / ok
redis = redis / ok
artifactStorage = minio / ok
worker = redis / ok
llmProvider = deepseek-v4-flash / configured
```

The preserved authenticated browser then reopened the exact Research and
Report routes successfully. This is a bounded local recovery proof; full
provider outage, queued/running cancellation, Redis-loss and repeated
resource-leak campaigns remain open.

## 2026-08-31 — product stale-work recovery and restart proof

The recovery service now classifies product work separately from explicit
qualification namespaces and reconciles only durable states for which the
next queue transition is deterministic. A bounded one-shot script and the API
startup hook use the same classifier and queue authorities.

The live campaign reduced product stale ResearchTurns from nine to zero:

* three legacy `QUERY_DATA` turns terminalized as `ANSWERED` without Jobs;
* three reinterpretation turns completed;
* one Dataset pending-result turn preserved valid partial output;
* one Dataset plan-ready turn completed through the real workers;
* one old Structure turn executed and failed closed because its exact
  ScientificObjectVersion payload was unavailable.

The failed Structure Turn remained auditable as
`ec298988-0b32-4e5e-a3c0-8bbb22725818` /
`job_agent2_ec2989880b324e5ea3c08bbb22725818`, with zero ToolCalls and the
explicit error `Exact ScientificObjectVersion payload is unavailable.` No
scientific success was fabricated.

After an API-only restart, the current startup log recorded:

```text
research_startup_recovery product_candidates=0 qualification_retained=159 accepted=0 attention=0
```

PostgreSQL, Redis, MinIO, frontend and all six workers remained running.
The final live snapshot reported `active=1`, `idle=10`,
`idle-in-transaction=0`, empty queues, six idle workers, no recent queue
failures and zero remaining product stale turns/jobs.

## 2026-09-01 resource governance and retention qualification

The same-stack operations snapshot now exposes one redacted,
machine-readable `resourceGovernance` projection. It is derived from the
loaded runtime settings and trusted viewer/context contracts:

```text
uploads: 64 MiB per file / 128 MiB per request
reports: 512 KiB request / 2 MiB export
research: 4 active ResearchTurns per Project
queue attention depth: 100
context input budgets: DATA 8k, INTERPRETER 12k, ORCHESTRATOR 12k,
                       PLANNER 10k, REPORT 10k
typed limit errors: PROJECT_ACTIVE_RESEARCH_LIMIT,
                    TOOL_RESOURCE_LIMIT,
                    WORKSPACE_PAYLOAD_CAP_EXCEEDED,
                    REPORT_CAP_EXCEEDED,
                    EXPORT_SIZE_EXCEEDED
```

Research admission locks the authoritative Project row and counts
non-terminal ResearchTurns in the same transaction. When the cap is reached,
the API returns HTTP `429` with the typed
`PROJECT_ACTIVE_RESEARCH_LIMIT` code before persisting a new Message or Turn;
the frontend renders the bounded summary rather than an object-shaped error.
No process-local semaphore was introduced.

The command
`uv run python scripts/phase14r_operations_snapshot.py --same-stack`
returned `status=ok` on 2026-09-01 with PostgreSQL/Redis/MinIO healthy, six
idle workers, zero queued work, `idle-in-transaction=0` and pool
`checkedOut=0`. The snapshot is suitable for local alert polling; external
paging delivery and historical qualification-record reconciliation remain
operational follow-up work, not hidden product success criteria.

## 2026-09-01 deterministic operations alert gate

The redacted snapshot now includes a bounded typed-alert contract:

```text
alertsSchemaVersion = phase14r-operations-alerts/1.0

alerts[]:
  code
  severity = WARNING | CRITICAL
  component
  observed
  threshold
  message

alertSummary:
  total
  critical
  warning
```

Alerts are derived deterministically from the existing PostgreSQL, Redis/RQ,
MinIO and resource-governance projections. Stable codes cover:

```text
PostgreSQL backend/reachability
idle-in-transaction
stale active ResearchTurns
stale queued/running Jobs

Redis backend/reachability
queue-depth threshold
minimum worker count
recent queue failures

MinIO backend/reachability

invalid upload/report/context/Viewer limits
missing typed resource-limit contracts
```

Retained historical qualification failures and explicit waiting boundaries do
not become alerts merely because they exist. Alert observations are bounded
counts, backend classes or redacted exception class names. Database/Redis
URLs, MinIO credentials, Provider secrets and filesystem paths are never
projected.

`resourceGovernance` now participates in the overall snapshot status instead
of being an informational block that was always marked healthy. The validator
checks:

```text
positive upload limits and total-request >= per-file
positive per-Project Research concurrency
non-negative queue threshold
positive Report request/export limits and export >= request
complete positive operation-specific Context budgets
non-empty positive Viewer payload limits
the complete typed limit-error contract
```

The CLI always emits one machine-readable JSON document. Pretty JSON remains
the default; `--compact` emits the same contract on one line.

Diagnostic inspection does not fail the shell merely because attention is
present:

```text
uv run python scripts/phase14r_operations_snapshot.py --same-stack
# exit 0 after emitting status=ok or status=attention
```

Release/monitoring gates opt into deterministic failure:

```text
uv run python scripts/phase14r_operations_snapshot.py \
  --same-stack \
  --fail-on-attention \
  --compact

status=ok        → exit 0
status=attention → exit 2
```

This provides a repository-owned alert gate suitable for CI, scheduled
polling or an external paging adapter without introducing a new monitoring
authority. External notification delivery remains deployment integration
work; it is no longer required to reinterpret free-form snapshot text.

## 2026-09-01 foundation migration and marker reconciliation

The final operations audit found a migration provenance marker drift rather
than scientific schema or data corruption:

```text
repository head = 0028_foundation_schema_reconciliation
live marker before reconciliation = 0006_phase10l4_interpretation
live migration-managed schema before reconciliation = equivalent to 0027
scientific-data corruption = NO
```

The same audit identified a separate fresh-install gap: six foundation tables
declared by the application metadata were absent from the historical Alembic
chain. Migration `0028_foundation_schema_reconciliation` now validates or
creates `project_members`, `files`, `field_mappings`, `user_configs`,
`secrets`, and `audit_logs`, plus three required lookup indexes. Compatible
historical tables are preserved; incompatible shapes fail closed.

Qualification followed a recoverable sequence:

```text
1. fresh PostgreSQL database upgrade to head
   foundation tables = 6/6
   required indexes = 3/3
   marker = 0028

2. full live-database clone rehearsal
   clone marker 0006 → controlled stamp 0027 → upgrade 0028
   table set unchanged = YES
   every table row count unchanged = YES

3. live pre-change pg_dump
   bytes = 2,541,674
   SHA-256 =
     0639772C91A3EC7F7D730F6416B45983B24386275B77EB6DBA5F3B3ECCDFD651

4. live controlled reconciliation
   stamp 0027 → upgrade 0028 = PASS
   marker column = VARCHAR(64)
   marker = 0028_foundation_schema_reconciliation
```

Post-reconciliation authority counts remained:

```text
tables = 57
Projects = 179
Research Sessions = 164
Jobs = 301
Artifacts = 1565
ScientificObjects = 213
ScientificObjectVersions = 249
ResearchTurns = 426
ScientificResults = 203
Scientific Reports = 45
invalid current-version pointers = 0
Results missing ResearchTurn = 0
```

The same-stack API remained online with PostgreSQL, Redis, MinIO, Redis
workers and DeepSeek configured. The release alert gate then returned:

```text
status = ok
alerts = 0
DB active / idle / idle-in-transaction = 1 / 5 / 0
workers = 6 idle
queued = 0
recent queue failures = 0
MinIO = ok
```

No service or authenticated browser session was stopped during the controlled
marker reconciliation.

## 2026-09-01 current release-candidate operations snapshot

The current worktree snapshot is the release-candidate operational baseline:

```text
status = ok
alerts = 0
PostgreSQL active / idle / idle-in-transaction = 1 / 5 / 0
SQLAlchemy pool checkedOut = 0
stale jobs = 0
stale research turns = 0
Redis workers = 6 idle
canonical queue depth = 0
MinIO = ok (bucket mdi-artifacts)
```

An isolated same-stack service campaign selected `70` mandatory tests and
passed all `70`; failed, error and skipped counts were all `0`. The campaign
used PostgreSQL database `mdi_phase14r_sb_20260901_2010`, Redis DB `14`, and
MinIO bucket `mdi-phase14r-sb-20260901-2010`. Historical optional tests were
deselected by marker rather than converted to skips. This is the current
operations evidence; older partial checkpoint wording above is retained as
history.
