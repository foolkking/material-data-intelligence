# Continuous Optimization Log

Authoritative loop log for
`CONTINUOUS_SYSTEM_OPTIMIZATION_GOAL.md`.

Status after the initial cross-system audit:

```text
DISCOVERED = 156
COMPLETED = 155
BLOCKED = 0
REMAINING = 1
CURRENT = NONE
```

Only independently implemented and verified improvements increment
`COMPLETED`. Audits and candidate discovery do not.

## Improvement #156 — CO-156 (2026-09-06)

- 状态：已完成并验证；持续优化队列已清空。
- 问题：独立 operations CLI 每次运行于新进程，无法共享 API 进程内的
  MinIO last-known observation。
- 修改：增加受保护 runtime observation file。文件名只含
  `sha256(endpoint|bucket)`；内容仅含 schema、fingerprint、capturedAt、
  storageBytes、objectCount。写入使用临时文件、`fsync` 和原子替换；TTL
  为 300 秒；未来时间戳（超过 60 秒）拒绝；过期内存/文件观察清理。
  当前扫描超时时仍返回 `usageScanComplete=false`、当前 bytes/count 为
  `null`，旧值仅作为 `authoritative=false` 的诊断上下文。
- 修改文件：`apps/api/mdi_api/operations.py`、
  `tests/test_phase14r_operations.py`、`persistent/ARCHITECTURE_DECISIONS.md`、
  `persistent/DESIGN_PROGRESS.md`、`persistent/TASK_BOARD.md`、
  `docs/agent2/continuous_optimization/OPTIMIZATION_BACKLOG.md`、
  `docs/agent2/continuous_optimization/evidence/co-156-minio-observation-cache-2026-09-06.json`、
  `results.md`。
- 验证：operations/storage/service-failure `33 passed, 1 skipped`；Ruff、
  compileall、git diff --check 通过；同栈 CLI 显示 PostgreSQL/Redis/MinIO、
  6 workers，真实完整扫描 `8739` objects / `139815841` bytes；超时仍为
  current unknown。

## Improvement #145 — CO-146 (2026-09-06)

Problem:

Managed API identity manifests were stored beneath the general `.cache` tree,
which made their protection depend on unrelated cache-cleanup allowlists.

Change:

- Added `scripts/phase14r_runtime_paths.ps1` as the shared repository-scoped
  runtime path authority.
- API start/rotation now use `.runtime_services/managed/api`; rotation
  compat-reads the legacy `.cache/runtime` manifest and removes it only after
  the exact old process pair is stopped.
- `repo_safe_cleanup.py` explicitly classifies `.runtime_services` as protected
  active service data.

Verification:

- Focused rotation/cleanup/build-cache/log tests: `21 passed`.
- PowerShell AST, Ruff and diff checks: PASS.
- Live same-stack rotation replaced API `25704/5060` with `12044/19996`;
  8005 has one listener, 8006 is closed, the legacy manifest is absent and the
  protected manifest is present.
- Runtime health remains PostgreSQL/Redis/MinIO with six worker queues.
- Cleanup dry-runs selected no active runtime manifest and changed no service
  data.

Result:

Runtime identity is now explicit and durable across cache maintenance, while
old API processes are still reclaimed only through exact ownership checks.

New finding:

- CO-147: worker launchers need repository-scoped process identity and safe
  rotation evidence comparable to the API path.

## Improvement #146 — CO-147 (2026-09-06)

Problem:

`phase14r_start_stack.ps1` considered any `mdi_workers.worker_entrypoint`
process sufficient, so a partial six-queue topology could be mistaken for a
healthy stack. The first implementation also failed to read the manifest from
a plain shell without `PYTHONPATH`.

Change:

- Read the checked-in queue manifest with a scoped `packages/schemas` path and
  restore the caller's environment afterward.
- Compare every expected queue with live worker command lines.
- Start `phase14r_start_workers.ps1 -OnlyQueue` only for missing manifest
  queues; reject requested names outside the manifest.

Verification:

- Focused worker/stack/log regression: `17 passed`.
- PowerShell AST, Ruff, compileall and diff checks: PASS.
- Real `phase14r_start_stack.ps1 -FrontendPort 3023` returned success with all
  six queues present; worker process count remained 12 and all 12 PIDs were
  unchanged, proving no duplicate launch or service interruption.
- Runtime remained PostgreSQL/Redis/MinIO-backed; frontend, workers and
  infrastructure were not stopped.

Result:

Stack startup now repairs only missing queue workers and cannot silently treat
one surviving worker as a complete topology.

New finding:

- CO-148: per-queue worker identity manifests are still needed for exact future
  replacement and memory-safe cleanup.

## Improvement #147 — CO-148 (2026-09-06)

Problem:

Worker runner/child ownership was only visible through transient process
inspection, so exact future replacement and memory-safe cleanup had no durable
per-queue identity authority.

Change:

- Added `Get-MdiWorkerRuntimeDirectory` under the protected
  `.runtime_services/managed` root.
- Added `phase14r_discover_workers.ps1`, which reads the checked-in queue
  manifest, pairs each `worker_entrypoint` child with its exact log-runner
  parent, and atomically writes one `phase14r-worker-instance/1.0` record per
  queue.
- Wired discovery after worker launch so future starts refresh identities.

Verification:

- Focused worker/API rotation/log regression: `19 passed`.
- PowerShell AST, Ruff, compileall and diff checks: PASS.
- Live discovery found all six expected queues and wrote six manifests,
  recording runner/child PIDs, creation FILETIMEs, executable paths, command
  digests, Redis URL and release SHA.
- Existing 12 worker processes remained alive and no service was stopped.
- A first operations scan transiently timed out in MinIO; an immediate retry
  completed with 0 alerts and 8,739/10,000 objects. This is recorded as the
  next reliability finding, CO-149, not hidden as a worker regression.

Result:

Worker process ownership is now durable and bounded, enabling a future exact
stop/rotation helper without guessing from names or stopping healthy workers.

New finding:

- CO-149: classify and safely retry transient MinIO bounded-scan timeouts.

## Improvement #148 — CO-149 (2026-09-06)

Problem:

A transient MinIO bounded-list timeout could temporarily turn a healthy bucket
into an unknown-capacity warning.

Change:

- `_minio_snapshot` now retries the bounded usage scan once only when the
  shared service-failure classifier marks the error retryable.
- The retry uses a bounded 50 ms delay and records `usageRetryCount` when used.
- Authentication, not-found and other non-retryable failures remain typed
  fail-closed with no fabricated counts or utilization.

Verification:

- Operations/storage/service-failure regression: `29 passed, 1 skipped`.
- Timeout-then-success fake client performs exactly two list calls and returns
  complete usage; authentication failure performs one call and remains rejected.
- Live same-stack snapshot is `ok` with zero alerts, MinIO `8739/10000`
  complete, PostgreSQL/Redis healthy, six workers idle, and no pool timeout.
- Ruff, compileall and diff checks pass.

Result:

Transient storage latency no longer causes avoidable operator noise, while
persistent or unauthorized storage failures remain visible and fail closed.

New finding:

- CO-150: redact credential-bearing Redis URLs before worker manifests are
  persisted.

## Improvement #149 — CO-150 (2026-09-06)

Problem:

Per-queue worker manifests previously persisted the complete `redisUrl`, which
could put Redis credentials into repository runtime data.

Change:

- Replaced the persisted field with bounded `redisIdentity`.
- The projection keeps only scheme, host, optional port and a numeric database
  path; userinfo, password, query strings and the raw URL are never written.
- Re-discovered all currently running workers so existing manifests are
  migrated in place through atomic replacement.

Verification:

- Focused identity/queue regression: `14 passed`.
- PowerShell AST, Ruff, compileall and diff checks: PASS.
- Six live manifests contain no `redisUrl`, credential-bearing URL or secret
  sentinel; all identities are `redis://127.0.0.1:6379/13`.
- Twelve existing worker processes remained alive and no service was stopped.

Result:

Runtime evidence no longer persists credential-bearing Redis connection data.

New finding:

- CO-151: mark stale worker manifests explicitly without treating transient
  worker loss as permission to delete identity evidence.

## Improvement #150 — CO-151 (2026-09-06)

Problem:

Worker discovery could leave an old `worker-*.json` after a queue process
disappeared, allowing stale identity to look active during later cleanup or
rotation.

Change:

- Found queues are written with `status=RUNNING`, a fresh `lastSeenAt`, and
  `staleSince=null`.
- Existing records for missing queues are atomically rewritten with
  `status=MISSING`, preserved `lastSeenAt`, and a bounded `staleSince`.
- Missing records are never deleted; old Redis URL fields are removed during
  this migration path.

Verification:

- Focused identity/queue regression: `14 passed`.
- PowerShell AST, Ruff, compileall and diff checks: PASS.
- Live discovery found all six queues and six manifests; each is `RUNNING`
  with `lastSeenAt` and no stale state. Twelve workers remained alive and no
  service was stopped.
- A destructive stale simulation was intentionally not run because it would
  require stopping a healthy worker; the code path is covered by static
  assertions and the live active-state proof.

Result:

Stale identity is explicit and recoverable rather than silently authoritative.

New finding:

- CO-152: consume worker manifests through a dry-run, health-gated exact
  rotation helper.

## Improvement #151 — CO-152 (2026-09-06)

Problem:

Worker identity manifests existed but no bounded helper consumed them for
exact ownership validation and safe replacement planning.

Change:

- Added `phase14r_rotate_workers.ps1`, dry-run by default.
- It validates repository token, release SHA, runner/child existence and
  parentage, creation FILETIMEs, executable command digests, queue command and
  redacted Redis identity before producing a plan.
- Apply is constrained to one queue and an explicit `ShouldProcess` decision;
  successful replacement is followed by bounded rediscovery.

Verification:

- Focused worker rotation/identity regression: `16 passed`.
- PowerShell AST, Ruff, compileall and diff checks: PASS.
- Live dry-run validated all six queue manifests and preserved the complete
  12-process worker PID set; no service was stopped.

Result:

Future worker replacement now has a repository-authorized, fail-closed dry-run
plan instead of manual PID handling.

New finding:

- CO-153: require real replacement identity/health validation before stopping
  the old worker pair in the Apply path.

## Improvement #152 — CO-153 (2026-09-06)

Problem:

The worker Apply path started a replacement, waited two fixed seconds and then
stopped the old pair without proving replacement identity and liveness.

Change:

- Added bounded replacement discovery keyed by exact queue and generated
  worker name.
- Before old stop, validate replacement child/runner parentage, exact queue
  command, redacted Redis identity, and both live PIDs.
- If admission fails, the old pair remains untouched; if a replacement was
  discovered before a later failure, it is revalidated by command digest and
  stopped as a rollback target.

Verification:

- Focused worker rotation/identity regression: `16 passed`.
- PowerShell AST, Ruff, compileall and diff checks: PASS.
- Live dry-run validated all six current manifests and kept the complete
  12-process worker PID set unchanged; no service was stopped.

Result:

An unproven replacement can no longer authorize old-worker shutdown.

New finding:

- CO-154: require Redis/RQ worker registration and expected queue state before
  admitting a replacement.

## Improvement #153 — CO-154 (2026-09-06)

Problem:

Worker replacement admission checked OS process identity but not Redis/RQ
registration. Forced process termination also left stale registrations, which
made operations report duplicate workers.

Change:

- Added `phase14r_worker_registration.py` with redacted exact-name,
  exact-single-queue, healthy-state and heartbeat-age checks.
- Rotation now requires that probe before old stop and calls exact
  `register_death()` cleanup for the verified old registration; rollback
  unregisters a discovered replacement only while the old pair is still active.
- Fixed replacement discovery to exclude `phase14r_log_runner.py` from child
  matching.

Verification:

- Registration/rotation focused regression: `7 + 16 passed`.
- PowerShell AST, Ruff, compileall and diff checks: PASS.
- First Apply attempt failed closed before old stop; after the matcher fix a
  real single-queue replacement succeeded:
  `mdi-jobs 18684/26300 → 29512/2972`.
- Redis/RQ returned to exactly 6 workers, each on one expected queue; queue
  depth is 0 and old/failed replacement pairs are absent.
- PostgreSQL/Redis/MinIO/API/frontend remained available; no service data was
  changed.

Result:

An OS-live but unregistered replacement cannot authorize old-worker shutdown,
and forced-stop stale RQ registrations are cleaned through the exact queue
identity.

New finding:

- CO-155: preserve bounded last-known-complete MinIO observation metadata across
  transient timeouts without presenting it as current capacity.

## Improvement #154 — CO-155 (2026-09-06)

Problem:

Transient MinIO bounded-list timeouts left a healthy API process with no
continuity metadata, even though the previous complete scan was still useful
as operator context.

Change:

- Added a thread-safe endpoint+bucket keyed in-process cache of the most recent
  complete aggregate measurement.
- The cache is valid for five minutes only as a non-authoritative diagnostic
  reference. A timed-out current scan keeps `storageBytes`/`objectCount` null,
  `usageScanComplete=false`, and includes bounded age/value context.
- Expired entries produce `lastKnownCompleteExpired=true` without exposing
  stale values; storage budget remains unknown.
- Operations alert projection includes last-known age only when present.

Verification:

- Operations/storage/service-failure regression: `31 passed, 1 skipped`.
- Ruff, compileall and diff checks: PASS.
- API rotation loaded the change (`12044/19996 → 26224/21772`), frontend proxy
  remained valid, runtime stayed PostgreSQL/Redis/MinIO with six idle workers.
- Direct deterministic tests prove complete→timeout and expired-cache behavior.
- Standalone CLI snapshots intentionally run in separate processes and do not
  share the in-process cache; this boundary is recorded rather than hidden.

Result:

Operators receive useful bounded continuity without any stale capacity being
promoted to current truth.

New finding:

- CO-156: decide whether a protected TTL-bound CLI observation cache is worth
  adding, or document the process boundary and classify consistently.

## Improvement #144 — CO-145 (2026-09-05)

Problem:

The bounded MinIO capacity scan was approaching its 10,000-object limit. The
probe marked a truncated scan incomplete, but the downstream budget projection
still displayed a precise utilization percentage and operations emitted no
typed warning, which could make an observed lower bound look complete.

Change:

- Added explicit bounded reasons for scan-limit and missing-continuation
  termination without projecting bucket keys.
- Preserved observed bytes/count as lower bounds while setting incomplete
  utilization to `null` and budget state to `unknown`.
- Added `OPS_MINIO_USAGE_SCAN_INCOMPLETE` with a bounded warning and runbook
  action that explicitly forbids deleting scientific Artifacts as a response.
- Preserved complete-scan behavior unchanged.

Files:

- `apps/api/mdi_api/operations.py`
- `apps/api/mdi_api/storage_budget.py`
- `tests/test_phase14r_operations.py`
- `tests/test_phase14r_storage_budget.py`
- `docs/agent2/continuous_optimization/evidence/co-145-minio-scan-completeness-2026-09-05.json`

Verification:

- Focused operations/storage/admin regression: `29 passed`, one existing
  opt-in integration skip.
- Ruff, compileall and diff check passed.
- A pure bounded simulation stopped at 3 objects, reported
  `MINIO_USAGE_SCAN_LIMIT_REACHED`, retained 6 observed bytes and projected no
  object key.
- Live same-stack scan remains complete at 8,739/10,000 objects with zero
  alerts, so normal operation did not regress.
- Managed API rotation loaded the code into canonical child `25704` / runner
  `5060`; old `18468/19620` exited and port 8006 is closed.

Result:

Operators can distinguish complete capacity facts from lower-bound estimates;
the diagnostic remains read-only and cannot suggest or perform provenance-
breaking Artifact deletion.

New findings:

- CO-146 tracks explicit protection of live API instance manifests from
  general cache-maintenance scope.

## Improvement #143 — CO-144 (2026-09-05)

Problem:

API code updates depended on manual child/runner PID choreography. An
interrupted shadow/canonical replacement could leave an obsolete Uvicorn or
log-runner pair resident even when the canonical port looked healthy.

Change:

- Made the API starter health-gated and gave every new instance an atomic,
  repository-tokened manifest containing exact child/runner PID, creation
  time, executable, command digest, release SHA and runtime fingerprint.
- Added a dry-run-by-default rotation state machine. It validates a same-stack
  shadow before touching canonical, revalidates process identity immediately
  before stopping, stops child before runner, validates the frontend proxy,
  and removes the shadow after cutover.
- Required explicit PID adoption for the one legacy canonical instance that
  predated manifests; unknown listeners always fail closed.
- Fixed an initial real-shadow self-check defect caused by ambiguous
  PowerShell comma/equality parsing. All eleven checks are now named and fully
  parenthesized, and failures report only bounded field names.
- Remove an instance manifest only after its exact PID and creation identity
  have been revalidated and stopped.

Files:

- `scripts/phase14r_start_api.ps1`
- `scripts/phase14r_rotate_api.ps1`
- `tests/test_phase14r_api_rotation.py`
- `tests/test_phase14r_log_rotation.py`
- `docs/16_RUNTIME_INFRASTRUCTURE_RUNBOOK.md`
- `docs/agent2/continuous_optimization/evidence/co-144-api-rotation-process-ownership-2026-09-05.json`

Verification:

- Focused startup/rotation/log/runtime regression: `20 passed`.
- Both PowerShell scripts parse successfully; diff check passed.
- Dry-run identified only legacy child `20748` / runner `16260`.
- Live rotation replaced them with child `18468` / runner `19620`.
- Old PIDs are absent, port 8005 has exactly one listener, port 8006 has none,
  and no shadow manifest remains.
- Frontend PID `29664`, six worker pairs, PostgreSQL PID `11720`, Redis PID
  `7284` and MinIO PID `12552` remained unchanged.
- Direct/proxy runtime fingerprint is
  `ee8baa498d3aef0aacbdbbafeb37453fde9c3c430469500009b0a42906e4a619`.
- Operations snapshot: zero alerts, six healthy idle workers, queue depth 0,
  DB idle-in-transaction 0 and pool checked-out 0.

Result:

New API code can be admitted before the replaced instance is reclaimed, and
successful rotation deterministically leaves one canonical API rather than
old/shadow processes continuing to consume memory.

New findings:

- CO-145 tracks the MinIO object scan approaching its 10,000-object bound and
  the need to expose an incomplete scan without false precision.

## Improvement #142 — CO-143 (2026-09-05)

Problem:

`tests/test_phase14r_recovery.py` annotated its fake recovery queue with
`UUID` but imported only `uuid4`. Postponed annotations let pytest pass, while
Ruff correctly rejected the recovery regression file with two F821 errors.

Change:

- Imported `UUID` from the existing standard-library `uuid` import.
- Made no runtime or recovery behavior changes.

Files:

- `tests/test_phase14r_recovery.py`
- `docs/agent2/continuous_optimization/evidence/co-143-recovery-test-uuid-import-2026-09-05.json`

Verification:

- Complete Phase 14-R recovery regression: `6 passed`.
- Ruff, compileall and diff check: passed.
- Live frontend/API/PostgreSQL/Redis/MinIO/worker topology remained healthy;
  API PID `20748`, frontend PID `29664`, and port 8006 remained closed.

Result:

The recovery regression is now statically valid as well as executable, so
touched-code lint can protect future queue-recovery changes.

New findings:

- CO-144 tracks the manual API blue-green process choreography used by
  CO-141/CO-142 and the risk of leaving obsolete API process pairs resident.

## Improvement #141 — CO-142 (2026-09-05)

Problem:

The API app factory still registered two deprecated FastAPI
`@app.on_event("startup")` handlers. One guarded the database migration head
and one recovered interrupted Research work, so a future FastAPI/Starlette
upgrade could remove startup behavior or change its ordering.

Change:

- Replaced both handlers with one app-factory-scoped async lifespan contract.
- Preserved the admission order: migration-head validation runs first and
  remains fail-fast.
- Preserved recovery as operational best effort: a recovery exception is
  logged and does not falsely block API admission.
- Captured each `create_app()` settings snapshot inside its own lifespan so
  multiple test/app instances cannot share mutable startup state.
- Added deterministic tests for ordering, recovery failure and factory
  isolation.
- Validated on shadow API 8006, then replaced the canonical 8005 API and
  stopped both old and shadow process pairs.

Files:

- `apps/api/mdi_api/main.py`
- `tests/test_api_lifespan.py`
- `docs/agent2/continuous_optimization/evidence/co-142-fastapi-lifespan-2026-09-05.json`

Verification:

- Lifespan/migration/recovery/API factory regression: `49 passed`.
- Strict `DeprecationWarning` gate: `7 passed`.
- Touched Ruff, compileall and diff check: passed.
- Runtime introspection: `startup_handlers=0`, `shutdown_handlers=0`, lifespan
  context installed.
- Shadow 8006 reported PostgreSQL/Redis/MinIO/Redis-worker topology and did
  not emit the deprecated startup warning.
- Final canonical API PID `20748` on 8005; old PIDs `29280/27464` and shadow
  PIDs `19060/21200` stopped; no 8006 listener; frontend PID `29664`
  remained uninterrupted and its API proxy still reports PostgreSQL.

Result:

API admission and recovery now use the framework-supported lifecycle contract
without weakening migration safety or durable-work recovery. The service
rotation again leaves exactly one API instance, avoiding duplicate memory
usage.

New findings:

- CO-143 tracks the missing `UUID` import found when Ruff covered the complete
  recovery regression file.

## Improvement #140 — CO-141 (2026-09-05)

Problem:

Platform Provider credentials were held in a process-local dictionary, so API
restarts or multiple API processes could lose or disagree on the configured
credential. The legacy `/me/secrets` route also exposed a process-local store
in same-stack runtime while frontend types and copy implied durable storage.

Change:

- Added migration `0032_provider_connections` and a shared PostgreSQL
  repository for encrypted Provider connection metadata and ciphertext.
- Required a stable `MDI_PROVIDER_ENCRYPTION_KEY` for durable writes and
  returned typed fail-closed configuration errors when it is missing/invalid.
- Preserved a process-local adapter only for explicit local/test runtimes.
- Restricted Provider mutations to platform administrators while retaining
  authorized read/test/resolve behavior.
- Made legacy `/me/secrets` unavailable in same-stack/production-like runtime
  with typed HTTP 503 and required exact user scope for every local lookup,
  usage mark and delete.
- Removed unused browser secret clients, `secretId` request fields and stale
  persistence copy.
- Backed up the live PostgreSQL database, migrated `0031` to the single
  `0032` head, validated a shadow API, then replaced the canonical API and
  stopped both the old and shadow process pairs.

Files:

- `apps/api/alembic/versions/0032_provider_connections.py`
- `apps/api/mdi_api/db.py`
- `apps/api/mdi_api/provider_connections.py`
- `apps/api/mdi_api/routers/planner.py`
- `apps/api/mdi_api/routers/planner_providers.py`
- `apps/api/mdi_api/routers/secrets.py`
- `apps/api/mdi_api/secrets/store.py`
- `apps/web/app/lib/planner-api.ts`
- `apps/web/app/lib/messages/en-US.ts`
- `apps/web/app/lib/messages/zh-CN.ts`
- `apps/web/app/components/ModelSettingsPage.tsx`
- `apps/web/app/components/ModelSettingsPage.test.tsx`
- focused Provider, legacy-secret and migration tests
- `docs/agent2/continuous_optimization/evidence/co-141-provider-credential-authority-2026-09-05.json`

Verification:

- Backend Provider/legacy-secret/Planner/migration matrix: `84 passed`.
- Frontend Model Settings/Planner Workbench: `40 passed`.
- Frontend typecheck, touched Ruff, compileall and diff check: passed.
- Real PostgreSQL backup:
  `.qualification_runs/qual-20260905T121646Z-2405f691/postgresql/mdi-pre-0032-provider-connections.dump`,
  SHA-256 `7AC281AC9E49D08B3121EAA94CDCDE98685370905EEFBE3F5FD7D0A707F91DC1`.
- Two independent Python processes wrote/read/decrypted one temporary Provider
  record through PostgreSQL; the record was deleted afterward and the key was
  never returned to the browser or logs.
- Authenticated shadow API returned
  `503 / LEGACY_USER_SECRET_API_UNAVAILABLE` for `/me/secrets`.
- Final runtime has frontend PID `29664`, canonical API PID `29280`, one
  listener on 8005, no listener on 8006, and healthy PostgreSQL/Redis/MinIO/
  Redis-worker topology. Old API PIDs `29356/22124` are stopped.

Result:

Provider credentials now have one encrypted shared runtime authority instead
of divergent process memory. Legacy UI/API semantics no longer promise
durability that the product cannot provide, and the controlled service
rotation left no duplicate API consuming memory.

New findings:

- CO-142 tracks the two deprecated FastAPI startup handlers observed in the
  final regression.

## Improvement #139 — CO-140 (2026-09-05)

Problem:

Repository-local build/test caches consumed 40,349,635,642 bytes across 113
Next build directories, exceeding the 25 GiB budget. Historical build names
were mixed with the active 3023 build, so an unscoped recursive cleanup could
have broken the running frontend.

Change:

- Added a dry-run-first cleanup authority restricted to direct
  `apps/web/.next*` directories.
- Permanently excluded `apps/web/.cache`, source, dependencies, service data,
  browser profiles, logs and release/qualification evidence.
- Required complete Git tracking inspection and resolution of every active
  frontend BUILD_ID over localhost.
- Required an exact candidate fingerprint and a fresh re-scan before apply.
- Applied the verified plan to 105 untracked builds older than 24 hours.

Verification:

- Cleanup/safe-cleanup/retention tests: `14 passed`.
- Dry-run: 113 directories, 105 candidates, zero tracked/symlink/out-of-scope
  candidates; active BUILD_ID `8sfvpRz5rhQnpDvDpnPdW` resolved to
  `apps/web/.cache/next-live-20260905`.
- Apply fingerprint:
  `a461a0a39483c4b5717d242a5bc979bbd183c017ea6e84370b451a655326e10b`.
- Removed 105 generated directories / 38,056,000,111 bytes.
- Post-run: 8 retained directories / 2,293,972,298 bytes; no remaining
  candidate; storage budget 8.55% and `within`.
- Frontend remained HTTP 200 on unchanged PID 29664; API/PostgreSQL/Redis/
  MinIO/workers remained healthy.
- Ruff, compileall and diff check: PASS.

Result:

35.44 GiB of obsolete generated cache was reclaimed without restarting the
product or touching scientific/service authority. The removed caches are not
recoverable in place but are reproducible build output.

Evidence:

- `evidence/co-140-safe-build-cache-cleanup-2026-09-05.json`

## Improvement #138 — CO-120 (2026-09-05)

Problem:

The release quickstart mixed historical/default-port launch paths with the
retained Windows same-stack profile. A fresh checkout also omitted the
production frontend build required by the launcher, documented the wrong
health endpoint and could imply `docker compose down` was safe for retained
services.

Change:

- Declared one canonical Windows retained same-stack application start path.
- Required lockfile installs and a matching `.cache/next-production` build.
- Added read-only PostgreSQL/Redis/MinIO endpoint preflight.
- Kept Alembic at the repository's dynamic single head rather than a stale
  hard-coded revision.
- Documented `/health/runtime`, canonical ports and `-CheckOnly`.
- Made service retention the default and documented only the existing
  repository-scoped frontend rotation dry-run/apply flow for obsolete
  processes.
- Explicitly separated the default-port Compose topology from the retained
  qualification topology.

Verification:

- Quickstart contract tests: `5 passed`.
- Alembic: single head `0031_product_search_keyset`.
- Live `-CheckOnly`: PostgreSQL 55434, Redis 6379/13, MinIO 9000, API 8005,
  frontend 3023, Redis workers and configured DeepSeek all healthy.
- Ruff and diff check: PASS.

Result:

A developer has one reproducible current-stack path that neither duplicates
application services nor accidentally shuts down retained service data.

Evidence:

- `evidence/co-120-canonical-same-stack-quickstart-2026-09-05.json`

## Improvement #137 — CO-068 (2026-09-05)

Problem:

The existing disk preflight reported only volume free space. Operators could
not attribute usage to repository source, PostgreSQL, MinIO, runtime logs,
qualification browser profiles or build/test caches without exposing paths or
object identities.

Change:

- Added a read-only `phase14r-storage-budget/1.0` projection for six bounded
  storage categories.
- Added PostgreSQL `pg_database_size(current_database())` and a 10,000-object
  bounded MinIO usage scan.
- Added a 100,000-entry, no-symlink filesystem scan with a 30-second cache.
- Returned only aggregate bytes/counts, budget, utilization, completeness and
  state; absolute paths, file names, object keys, bucket/database names and
  credentials are excluded.
- Added typed, configurable budgets with fail-closed parsing and a second
  platform-admin allowlist.

Verification:

- Storage budget, operations and platform-admin focused matrix:
  `20 passed, 1 existing integration skip`.
- Dedicated storage budget tests: `6 passed`.
- Ruff and diff check: PASS.
- Real same-stack snapshot: PostgreSQL 46,659,251 B, MinIO 139,815,841 B /
  8,739 objects, logs 871,980 B, profiles 23,911,527 B; all complete and
  within budget.
- Build/test caches measured 40,349,971,256 B / 36,279 entries, complete,
  `exceeded` at 150.32% of the 25 GiB budget.

Result:

Operators now have a redacted capacity authority that distinguishes service
health from storage attention. The discovered build-cache excess is tracked
separately as CO-140; this read-only improvement deleted nothing.

Evidence:

- `evidence/co-068-storage-budget-reporting-2026-09-05.json`

## Improvement #136 — CO-067 (2026-09-05)

Problem:

Qualification PostgreSQL and MinIO directories had no bounded run identity,
terminal status or retention authority. A cleanup based only on directory age
could not distinguish active services, release evidence and disposable
qualification state safely.

Change:

- Added an isolated `.qualification_runs/<run-id>/{postgresql,minio}` contract
  with a versioned manifest, active marker and strict run ID.
- Added ACTIVE, COMPLETED and FAILED states plus indefinite protection for
  release evidence.
- Added a checked-in 14-day TTL policy.
- Made the default operation a read-only plan; explicit apply moves eligible
  terminal runs into a recoverable archive rather than deleting them.
- Excluded symlinks, malformed manifests, active runs, release evidence and
  every legacy `.phase13-*`/`.phase14r-*` service directory.

Verification:

- Retention contract tests: `7 passed`.
- Current-repository dry-run: `candidateCount=0`,
  `legacyDirectoriesManaged=false`, no move performed.
- Ruff, compileall and diff check: PASS.
- Live `/health/runtime`: PostgreSQL, Redis, MinIO and Redis-backed worker
  topology all `status=ok`.

Result:

Future isolated qualification state can expire predictably without risking
the running same-stack services or historical release evidence. Existing
legacy service directories remain deliberately unmanaged.

Evidence:

- `evidence/co-067-qualification-run-retention-2026-09-05.json`

## Improvement #135 — CO-139 (2026-09-05)

Problem:

The Phase 5 Alembic regression required the literal token `DATABASE_URL` in
`alembic/env.py`. Runtime database authority now intentionally comes from the
shared typed settings loader, so the implementation-detail assertion failed
while the migration environment remained correctly configured.

Change:

- Asserted the `load_settings` and `database_configuration_declared` imports.
- Asserted `load_settings().database_url` is the runtime URL authority.
- Asserted environment override detection and safe Alembic URL injection,
  including percent escaping.

Verification:

- Complete Phase 5 runtime infrastructure file: `9 passed, 1 skipped`.
- Ruff and diff check: PASS.

Result:

The regression now protects the actual typed database-authority contract
instead of an obsolete source-text spelling.

Evidence:

- `evidence/co-139-alembic-settings-contract-2026-09-05.json`

## Improvement #134 — CO-138 (2026-09-05)

Problem:

The Task Center and Notification Center shared-feed regression asserted that a
project label must render exactly twice. The current valid UI renders the two
surface headings but de-duplicates the repeated project label, so the brittle
text-node count failed even though one shared request and refresh transition
remained active.

Change:

- Replaced the duplicate-label count with semantic assertions for the
  `全部任务` and `最近通知` surfaces.
- Retained an assertion that the shared project content is visible.
- Kept the single shared request and refresh-transition assertions unchanged.

Verification:

- Task Center, Notification Center and shared task-feed tests: `27 passed`
  across 3 files.
- `git diff --check`: PASS.

Result:

The regression now protects the actual shared-feed contract and both product
surfaces without coupling correctness to duplicated presentation text.

Evidence:

- `evidence/co-138-shared-feed-test-reliability-2026-09-05.json`

## Improvement #133 — CO-118 (2026-09-05)

Problem:

CI and local PostgreSQL/Redis/MinIO qualification duplicated test paths,
required identities and terminal-text assertions.

Change:

- Added one versioned mandatory-service manifest.
- Declared 29 test paths, 34 required test identities, minimum 50 passed and
  zero skip/failure policy.
- Added one runner/validator used by CI and local runbooks.
- Replaced terminal grep with structured JUnit identity and count validation.

Verification:

- Manifest/runner/JUnit focused tests: `6 passed`.
- Manifest load, missing-required-test rejection and skip rejection: PASS.
- CI and both runbooks reference the same runner.
- Ruff, compileall, JSON/YAML parse and diff check: PASS.

Result:

A service-backed test can no longer be added to one shell list while silently
remaining absent from another qualification path.

Evidence:

- `evidence/co-118-mandatory-service-manifest-2026-09-05.json`

## Improvement #132 — CO-116 (2026-09-05)

Problem:

CI referenced third-party GitHub Actions and PostgreSQL, Redis and MinIO
service images by mutable tags.

Change:

- Replaced every third-party Action tag with a full commit SHA.
- Bound each service image to an immutable multi-platform manifest digest.
- Added a checked-in provenance lock containing the reviewed tags and resolved
  immutable identities.
- Added a guard that rejects floating Action and service image references.

Verification:

- Supply-chain focused tests: `3 passed`.
- Five official repository tags resolved to the five recorded Action SHAs.
- Workflow YAML and provenance JSON parse: PASS.
- Floating Action references 0; floating service image references 0.
- Ruff and diff check: PASS.

Result:

CI dependencies can no longer drift merely because a third-party tag is
retargeted, and the reviewed provenance remains inspectable in the repository.

Evidence:

- `evidence/co-116-ci-supply-chain-pins-2026-09-05.json`

## Improvement #131 — CO-065 (2026-09-05)

Problem:

Research submit relied on React disabled state and global search suppressed late
responses without canceling obsolete network work.

Change:

- Added a synchronous same-tick single-flight guard before Research durable
  admission.
- Preserved PostgreSQL active-Turn limits as the server authority and added a
  typed five-second `Retry-After` hint to 429 responses.
- Propagated `AbortSignal` through global search and canceled obsolete requests
  on query, filter, close and unmount transitions.
- Retained the existing shared hidden/offline-aware Task/Notification polling
  transport instead of adding another limiter.

Verification:

- Backend focused: `13 passed`.
- 24 concurrent admissions: 3 accepted, 21 limited, 3 persisted Turns.
- Search/API + ProductShell: `29 passed`.
- Complete Research Pages: `93 passed`.
- Typecheck, Ruff and diff check: PASS.

Result:

Rapid user input no longer creates duplicate scientific admission or wastes
search capacity, while durable server state remains the final backpressure
authority.

Evidence:

- `evidence/co-065-request-backpressure-2026-09-05.json`

## Improvement #130 — CO-066 (2026-09-05)

Problem:

Artifact storage had no backend-wide write ceiling, and a local write failure
could leave partially written content at the final path.

Change:

- Added a 256 MiB storage write ceiling for Local and S3/MinIO backends.
- Rejected oversized content before creating a local file or calling
  `put_object`.
- Changed local writes to a same-directory `.part` file followed by atomic
  replacement.
- Removed temporary content on every failure path.

Verification:

- Artifact storage focused: `4 passed`.
- Product upload/input transport regression: `18 passed`.
- Oversize target creation 0, S3 client calls 0, interrupted `.part` residue 0.
- Ruff, compileall and diff check: PASS.

Result:

Scientific source and Artifact persistence now has a bounded final admission
point, and an interrupted local write cannot publish or leave a partial
scientific payload.

Evidence:

- `evidence/co-066-artifact-size-and-partial-cleanup-2026-09-05.json`

## Improvement #129 — CO-064 (2026-09-05)

Problem:

PostgreSQL, Redis and MinIO failures surfaced inconsistent exception-class
labels across runtime health and operations diagnostics, and raw exception
messages could contain endpoints, buckets or credentials.

Change:

- Added the shared `ServiceFailure/1.0` contract.
- Classified authentication, configuration, missing resource, timeout,
  unavailable and unknown failures from bounded exception metadata.
- Made health and operations return the same typed code and retryability.
- Excluded raw exception messages from the projection.

Verification:

- Failure-classification tests: `6 passed`.
- Broader health/operations run passed 39 tests before one unrelated stale
  Phase 5 source-text assertion; that finding is tracked as CO-139.
- Live same-stack database, Redis, MinIO and worker health: ok.
- Ruff, compileall and diff check: PASS.

Result:

Operators and product health surfaces can now identify the failed dependency
and retry class consistently without leaking infrastructure details.

Evidence:

- `evidence/co-064-typed-service-failures-2026-09-05.json`

## Improvement #128 — CO-062 (2026-09-05)

Problem:

API, worker and operations launch paths duplicated the same PostgreSQL, Redis
and MinIO qualification settings, so one topology change could move only one
process role.

Change:

- Added one typed `SameStackRuntimeTopology` builder.
- API and worker PowerShell launchers consume the builder's complete alias set.
- The standalone operations snapshot applies the same builder instead of its
  own hard-coded topology.
- Dedicated bounded override inputs move a service without inheriting stale
  generic aliases.

Verification:

- Runtime/config/worker/operations focused suite: `38 passed, 1 existing live
  integration skipped`.
- One Redis override reached API settings, worker resolution, health probing
  and operations configuration identically.
- Live same-stack snapshot: PostgreSQL ok, Redis ok, MinIO ok, 6 healthy
  workers, queued 0, idle-in-transaction 0.
- PowerShell parse, Ruff, compileall and diff check: PASS.

Result:

Qualification topology now has one construction authority across process roles;
launching or diagnosing the system cannot silently select a different
PostgreSQL, Redis namespace or MinIO endpoint.

Evidence:

- `evidence/co-062-shared-runtime-environment-2026-09-05.json`

## Improvement #127 — CO-101 (2026-09-05)

Problem:

Task Center inferred cancellation availability independently from Research,
which could expose Agent2 mutation controls for legacy Jobs or tasks without an
authoritative ResearchTurn.

Change:

- Added one shared cancellation contract with `MODERN_TURN`,
  `LEGACY_READ_ONLY` and `NO_TURN_UNAVAILABLE` states.
- Limited Stop to persisted modern ResearchTurns.
- Kept legacy and unresolved tasks read-only instead of deriving mutation
  authority from a Job naming convention.

Verification:

- Shared cancellation contract: `3 passed`.
- Complete Task Center/status run: `14 passed`; one unrelated shared-feed
  assertion failed and is tracked separately as CO-138.
- Frontend typecheck and diff check: PASS.

Result:

Research and Task Center now use the same fail-closed UI contract while the
server remains authoritative for cancellation. No legacy mutation or Job-name
identity inference was introduced.

Evidence:

- `evidence/co-101-research-cancellation-contract-2026-09-05.json`

## Improvement #126 — CO-059 (2026-09-05)

Problem:

Unhandled API, worker and browser failures lacked one release-bound,
request-correlated and secret-safe event contract.

Change:

- Added `OperationalExceptionEvent/1.0` for API, worker and frontend failures.
- Bound events to release SHA plus bounded request/scientific correlation
  identities.
- Added an authenticated frontend capture endpoint and RQ exception hook while
  preserving the default worker failure path.
- Excluded exception text, stack traces, prompts, credentials, service URLs and
  filesystem paths from the event schema.

Verification:

- Backend focused: `16 passed`.
- Frontend focused: `2 passed`.
- Live authenticated capture through frontend 3023/API 8005 returned `202`,
  request ID `b7f5745f2d854e4d9907e891555cf959`.
- Typecheck, Ruff and diff check: PASS.

Result:

Operational failures can now be correlated to an exact release and bounded
product identities without turning exception payloads into a secret or
scientific-data leak.

Evidence:

- `evidence/co-059-unified-exception-correlation-2026-09-05.json`

## Improvement #125 — CO-057 (2026-09-05)

Problem:

Queue depth, stale Jobs and worker registration were visible as separate
numbers, but operators and the administration UI had no shared explanation of
worker health or bounded recovery procedure.

Change:

- Added typed worker health with healthy/non-serving/stale-heartbeat counts.
- Mapped backlog, stale Job and worker health alerts to three repository
  runbook identities with bounded operator action and read-only recheck command.
- Exposed sanitized alerts through platform administration and added one
  focused queue/Job/worker operations panel.

Verification:

- Backend focused: `21 passed, 1 integration skipped`.
- Real same-stack integration: `1 passed, 0 skipped`.
- Frontend focused: `8 passed`.
- Live snapshot: status ok, alerts 0, depth 0, workers 6/6 healthy, stale
  heartbeat 0, recent failures 0, authority consistency issues 0.
- Ruff and diff check: PASS.

Result:

One server-derived, read-only contract now connects operational symptoms to a
safe response without allowing the UI to clear queues or mutate scientific
records.

Evidence:

- `evidence/co-057-operations-runbook-alerts-2026-09-05.json`

## Improvement #124 — CO-061 (2026-09-05)

Problem:

The live same-stack PostgreSQL database was still at
`0030_account_invitations` while repository code required
`0031_product_search_keyset`. API and worker processes had no admission guard,
and Alembic ignored the launcher's `MDI_POSTGRES_HOST` alias.

Change:

- Added one repository-head/database-head validator for same-stack API and
  worker startup.
- Made stale, unversioned and multi-head databases fail before traffic or
  queue consumption with `DATABASE_MIGRATION_HEAD_MISMATCH`.
- Unified Alembic and API detection of explicit database authority, including
  `MDI_POSTGRES_HOST`.
- Kept migration execution explicit; startup checks never mutate schema.

Verification:

- Focused migration/runtime tests: `24 passed`.
- A shadow API on 8006 refused the real stale `0030` database.
- A 2,679,964-byte PostgreSQL backup was captured before the normal Alembic
  upgrade.
- After upgrade, Alembic alias resolution and API startup both verified
  `0031_product_search_keyset`.
- Final runtime: frontend 3024 HTTP 200, API 8005 PID `23948`, six idle
  `migration3` workers, six empty queues, and no obsolete project process.
- PostgreSQL connections: active 1, idle 7, idle-in-transaction 0.
- Ruff, compileall and diff check: PASS.

Result:

Qualification can no longer silently run newer code against an older database
schema. The migration remains an explicit operator action, and a bounded
rolling replacement removed every old/failed API and worker generation after
the current generation was healthy.

Evidence:

- `evidence/co-061-migration-head-startup-guard-2026-09-05.json`

## Improvement #123 — CO-106 (2026-09-05)

Problem:

Expanding a long Research conversation rendered every historical message. A
1,000-message session therefore created an unbounded DOM and made the supposed
full-history control progressively less usable.

Change:

- Kept the normal recent view at 10 messages.
- Replaced unbounded expansion with a 100-message navigable window.
- Added explicit older/newer controls and truthful range/total status.
- Preserved persisted message IDs and reset window position when the exact
  Session or ResearchTurn changes.

Verification:

- Real 1,001-message `ResearchPage` renders exactly 100 message nodes.
- Older/newer navigation preserves exact content identity and trigger focus.
- Twenty window projections stay below the recorded 100 ms test budget.
- Full Research component suite: `92 passed`.
- Frontend typecheck and diff check: PASS.

Result:

Long sessions remain inspectable without making DOM and memory grow linearly
with the full transcript; scientific message and Turn authority is unchanged.

Evidence:

- `evidence/co-106-conversation-windowing-2026-09-05.json`

## Improvement #122 — CO-063 (2026-09-05)

Problem:

The six production worker queues were repeated across launchers, settings,
producers, recovery, operations and health. Environment overrides could make
API and worker processes use different queue topology.

Change:

- Added one checked-in six-role queue manifest with default name, environment
  variable, settings attribute and trusted handler per role.
- Routed all current producers, recovery, operations, runtime health and worker
  startup through that authority.
- Added same-stack validation for empty, duplicate, unknown and wrong-Redis
  worker topology.
- Added bounded API port and worker generation parameters so new processes can
  be health-checked before old processes are retired.

Verification:

- Focused runtime/manifest/health tests: `40 passed`.
- Manifest CLI, Ruff, compileall, PowerShell parse and diff check: PASS.
- Shadow API 8006 reported PostgreSQL/Redis/MinIO and the complete manifest.
- New six-worker generation registered idle on Redis DB13 before the old six
  workers were shut down.
- Final API PID `25628` on 8005 reports manifest version 1.0 and runtime
  fingerprint `ee8baa…a619`; shadow 8006 and all old worker PIDs are stopped.
- Frontend 3024 remained HTTP 200.

Result:

API, launchers and workers now share one queue topology and can be rotated
without keeping obsolete project processes resident.

Evidence:

- `evidence/co-063-worker-queue-manifest-2026-09-05.json`

## Improvement #121 — CO-044 (2026-09-05)

Problem:

Frontend and test tools could write large caches to the Windows user profile or
to inconsistent transient directories. That consumed constrained system-disk
space and made reproducibility and safe cleanup harder.

Change:

- Added one bounded workspace-cache runner for Next, Vitest, TypeScript,
  Playwright and repository Node scripts.
- Routed npm, Playwright, tool temporary files, pytest and Next build output to
  configurable repository-local cache roots.
- Rejected every override outside the repository; Next output is additionally
  constrained to `apps/web`.
- Declared both platform path forms for generated Next types so Windows and
  Linux builds do not rewrite `tsconfig.json`.

Verification:

- Focused routing tests: `3 passed`.
- Outside-workspace probe: exit `64`,
  `MDI_WORKSPACE_CACHE_OUTSIDE_REPOSITORY`.
- npm cache resolves to `.cache/tooling/npm`.
- Typecheck and two production builds: PASS.
- Node syntax, Ruff and diff check: PASS.
- Existing frontend remained HTTP 200; no service was stopped or restarted.

Result:

Large tool caches are now contained inside the repository's ignored cache
boundary, while unsafe external paths fail before tools start writing.

Evidence:

- `evidence/co-044-workspace-cache-routing-2026-09-05.json`

## Improvement #120 — CO-137 (2026-09-05)

Problem:

The dynamic optimization backlog contained five IDs twice, once as OPEN and
once as COMPLETED. Its declared counters therefore disagreed with the unique
task set, and two completed improvements were absent from the append-only
result archive. A resumed agent could select work that had already passed.

Change:

- Removed only the five stale duplicate OPEN rows, preserving their completed
  rows and evidence.
- Reconciled the declared counters from unique task identities.
- Added the missing CO-027 and CO-028 result archive records.
- Added a deterministic validator for unique/contiguous IDs, exact counters,
  valid CURRENT state and completed-result archival.

Files:

- `scripts/validate_optimization_ledger.py`
- `tests/test_optimization_ledger.py`
- `docs/agent2/continuous_optimization/OPTIMIZATION_BACKLOG.md`
- `results.md`
- `docs/agent2/continuous_optimization/evidence/co-137-ledger-integrity-2026-09-05.json`

Verification:

- Live ledger validation: `137 discovered`, `121 completed`, `0 blocked`,
  `16 remaining`, `CURRENT=CO-063`.
- Focused pytest: `5 passed`.
- Ruff, compileall and `git diff --check`: PASS.

Result:

The continuous task queue now has one authoritative row per improvement and a
machine-checked recovery point. Completed work cannot silently re-enter the
queue through a stale duplicate row.

## Improvement #119 — CO-060 (2026-09-05)

Problem:

Fresh and legacy upgrade tests checked the final schema but did not prevent a
future multiple-head graph or unreviewed destructive operation, and 0031 had
no data-bearing downgrade/re-upgrade proof for core scientific identities.

Change:

- Locked Alembic to one unique, linear, fully reachable head:
  `0031_product_search_keyset`.
- Required every revision to define both upgrade and downgrade functions.
- Added an AST guard against unreviewed `drop_table`, `drop_column`,
  `DROP TABLE`, `DROP COLUMN`, `TRUNCATE` and `DELETE FROM` in upgrades.
- Added negative self-tests proving dangerous samples are detected.
- Added a 0030→0031→0030→0031 round trip carrying a real Project,
  ScientificObject, exact ScientificObjectVersion, ResearchTurn and
  ScientificResult.

Verification:

- Migration guard plus fresh/legacy suites: `7 passed`.
- Exact head: `0031_product_search_keyset (head)`.
- Project, object, version and Result identities remained readable after both
  downgrade and re-upgrade.
- Ruff, compileall and diff check: passed.

Result:

Migration drift now fails in deterministic tests before it can silently fork
the revision graph or destroy scientific identity data.

Evidence:

- `evidence/co-060-migration-safety-guard-2026-09-05.json`

## Improvement #118 — CO-042 (2026-09-05)

Problem:

Workspace residue had no dry-run-first classifier that could distinguish safe
repository-owned temporary files from release evidence, active service data,
runtime logs and recoverable cleanup archives.

Change:

- Added a default and explicit `--dry-run` inventory.
- Restricted candidates to reviewed regular files under root `.tmp-*`,
  `.pytest_tmp` and direct `.managed_logs` allowlists.
- Rejected symlinks and every resolved source/destination outside the repository
  and recovery-archive boundaries.
- Kept apply recoverable: files move into `.cleanup_archive`; the tool performs
  no permanent deletion.
- Added bounded classifications for retained temporary files, release evidence,
  service data, runtime logs and existing recovery archives.

Verification:

- Focused safety regression: `4 passed`.
- Ruff, compileall and diff check: passed.
- Live dry-run: 0 candidates, 1 retained temporary file, 17 release-evidence
  roots, 16 service-data roots, 45 protected runtime logs and 1 recovery item.

Result:

Cleanup is now reviewable and fail-closed. Active data and evidence are
explicitly visible as protected instead of being silently omitted from a
candidate list.

Neat-freak disposition:

The isolated 285 MB CO-043 build remains recoverable under
`.cleanup_archive/co043-next-build-20260905`. Permanent clearing is deferred
until the required post-report explicit confirmation.

Evidence:

- `evidence/co-042-safe-workspace-cleanup-2026-09-05.json`

## Improvement #117 — CO-043 (2026-09-05)

Problem:

Service, pytest, npm/build and browser-evidence entry points could allocate
processes and write caches before checking whether the relevant volume had
safe capacity.

Change:

- Added one cross-platform read-only capacity gate with 5 GiB critical and
  10 GiB warning defaults.
- Gated pytest session startup, frontend tests/typecheck/build, packaged browser
  evidence, CI unit/frontend jobs and API/worker/frontend service launch.
- Checked repository plus configured PostgreSQL, MinIO and Artifact locations.
- Added typed capacity/path/configuration outcomes and a validated
  `MDI_DISK_FALLBACK_PATH` disclosure for low-space recovery.
- Kept the PowerShell service entry point as a thin wrapper over the same
  Python policy to prevent policy drift.

Verification:

- Disk-preflight plus log-retention regression: `11 passed`.
- Frontend command reached its preflight and focused test: `5 passed`.
- Typecheck passed through the preflight.
- Production build passed through the preflight using an isolated distDir;
  the running frontend remained HTTP 200.
- Ruff, compileall, four PowerShell parser checks and diff check: passed.
- Live E: free space: `47,090,618,368` bytes, state `ok`.

Result:

Large test, build, browser and service operations now fail before partial
writes on critically low space and show the configured recovery volume.

Evidence:

- `evidence/co-043-disk-space-preflight-2026-09-05.json`

## Improvement #116 — CO-040 (2026-09-05)

Problem:

`/health/runtime` performed real SQL, Redis and MinIO probes but did not expose
a comparable, redacted identity proving which declared topology and successful
connections produced the response.

Change:

- Added `RuntimeConfigurationFingerprint/1.0` over the declared backend
  topology and the successful connection proofs.
- Added separate SHA-256 connection fingerprints for PostgreSQL, Redis and
  MinIO without returning endpoints, usernames, passwords or access keys.
- Excluded credential values from the hash input, so secret rotation does not
  create a credential-comparison oracle.
- Kept backend/target identity in the hash input so an actual topology change
  produces a different fingerprint.
- Rolled only the API from PID `27560` to PID `26356`; PostgreSQL, Redis,
  MinIO, workers, frontend and browser tabs stayed running.

Verification:

- Focused runtime-health regression: `3 passed`.
- Ruff, compileall and diff check: passed.
- Live `/health/runtime`: PostgreSQL, Redis and MinIO all `ok`; all three
  `connectionBound` values are `true`.
- Live configuration fingerprint:
  `7e630226572f98d3fcaff65d81a214f3895ae8d206aba778383bfdf562137ad4`.

Result:

Operators can now compare runtime topology identities and detect accidental
backend drift without exposing configuration secrets or spoofing health output.

Evidence:

- `evidence/co-040-runtime-configuration-fingerprint-2026-09-05.json`

## Improvement #115 — CO-047 (2026-09-05)

Problem:

Product search used an offset-only continuation cursor. Inserts ahead of an
active page could shift the continuation window, causing duplicates or missed
authorized records, while the production tables lacked the complete composite
indexes needed by their authorization filters and stable sort.

Change:

- Replaced offset continuation with an opaque keyset v2 cursor over exact
  `updatedAt`, `kind` and `id` ordering.
- Bound the cursor fingerprint to the authenticated user and every query,
  Project, entity type, lifecycle and date filter.
- Continued each entity query below the previous global sort key in SQL while
  retaining the 100-item page cap and bounded candidate windows.
- Added idempotent Alembic-managed composite search indexes for Project,
  membership, Dataset, Research Session, Report, ScientificObject and
  ScientificResult.

Verification:

- Backend search/authorization regression: `27 passed`.
- Fresh and legacy migration regression: `4 passed`.
- Frontend continuation/API regression: `32 passed`.
- Qualified corpus: 1,250 records, 1,000 authorized, 250 private.
- 30 samples: p50 `14.33 ms`, p95 `15.33 ms`, max `17.25 ms`.
- Payload remained below 64 KiB and cross-Project leakage was zero.
- Ruff and diff check: passed.

Result:

Long-running product searches now retain a stable authorized continuation
despite concurrent inserts, without loading an unbounded result set into the
browser.

Evidence:

- `evidence/co-047-search-keyset-qualification-2026-09-05.json`

## Improvement #114 — CO-074 (2026-09-05)

Problem:

Volumetric validation required identical boundary conditions on all three axes,
so a scientifically valid mixed periodic/non-periodic grid was reported as
malformed instead of as unsupported by the current renderer.

Change:

- Accepted valid per-axis periodic/non-periodic boundary declarations.
- Marked mixed boundaries as valid data with a bounded
  `mixed_boundary_conditions_unsupported` renderer reason.
- Added distinct payload/grid mismatch validation.
- Rejected inline values outside the authoritative field range with a typed
  data-invalid error.
- Kept malformed boundary tokens as schema-invalid.

Verification:

- Volumetric validation focused tests: `7 passed`.
- TypeScript typecheck and diff check: passed.

Result:

The product now distinguishes valid-but-not-renderable science from corrupted
or internally inconsistent volumetric data.

Evidence:

- `evidence/co-074-volumetric-boundary-validation-2026-09-05.json`

## Improvement #113 — CO-041 (2026-09-05)

Problem:

API, worker and frontend output was redirected to fixed log files with no size
rotation, time rotation or retention cap, so repeated acceptance runs could
grow workspace logs indefinitely.

Change:

- Added one shared stdout/stderr runner with 25 MiB and UTC-day rotation.
- Kept at most eight managed archives and fourteen days per stream.
- Allowed bounded environment overrides for the three policy values.
- Protected the active log and every file outside the runner's exact timestamp
  archive pattern.
- Added maintenance-only dry-run planning.
- Integrated API, all six Redis workers and frontend launchers.

Verification:

- Rotation/retention focused tests: `5 passed`.
- Ruff and diff check: passed.
- API, worker and stack PowerShell parser checks: passed.
- Current 3024/8005/PostgreSQL/Redis/MinIO/worker stack stayed healthy and was
  not restarted.

Result:

Future service sessions have bounded logs without deleting active output,
manual evidence or unrelated files.

Evidence:

- `evidence/co-041-log-rotation-retention-2026-09-05.json`

## Improvement #112 — CO-031 (2026-09-05)

Problem:

Project action visibility was based on duplicated frontend write checks, while
the platform member editor allowed a collaborator to be assigned `owner`.
Actual owner-only purge authority still came from `projects.created_by`, so the
product could advertise an operation the server correctly rejected.

Change:

- Added one typed frontend Project capability matrix for read, export, write,
  archive, research and purge.
- Bound Project and Research surfaces to that shared contract.
- Preserved `projects.created_by` as the only owner identity.
- Rejected attempts to promote a non-creator collaborator to owner.
- Projected legacy duplicate-owner memberships as admin: write remains allowed,
  but owner-only purge authority is not invented.
- Removed owner from editable collaborator role choices.
- Kept platform-admin authority separate from Project membership.

Verification:

- Backend role/lifecycle matrix: `5 passed`.
- Frontend permission/Admin Center matrix: `12 passed`.
- Project action surfaces: `6 passed`.
- Research read-only surfaces: `3 passed`.
- TypeScript typecheck, Ruff, compileall and diff check: passed.

Result:

Owner, admin, researcher and viewer controls now agree with server enforcement;
neither a role label nor platform administration can create scientific Project
authority.

Evidence:

- `evidence/co-031-project-role-action-matrix-2026-09-05.json`

## Improvement #111 — CO-107 (2026-09-05)

Problem:

Expanded ContextManifest disclosure rendered every included item at once, so a
large manifest could create an unbounded DOM even though normal scientific
provenance only needs a bounded inspection window.

Change:

- Kept the default disclosure at eight priority-ordered items.
- Added a 32-item expanded window with previous/next navigation.
- Preserved authoritative order, exact source identities, Result references and
  scientific provenance across windows.
- Left the existing backend 128-item manifest contract unchanged.
- Added a deterministic 10,000-item stress regression.

Verification:

- ContextManifest focused frontend tests: `3 passed`.
- Existing provenance UI regression: passed.
- Backend ContextManifest tests: `13 passed`.
- TypeScript typecheck and diff check: passed.

Result:

Context inspection stays responsive and bounded without hiding or rewriting
scientific authority; researchers can traverse all server-provided items in
stable windows.

Evidence:

- `evidence/co-107-context-manifest-windowing-2026-09-05.json`

## Improvement #110 — CO-029 (2026-09-05)

Problem:

Cross-project exact-route regressions were distributed across domain tests, so
new Result, Report, History or Evidence routes could miss the invariant that
authorization must precede projection, mutation or storage access.

Change:

- Expanded one real HTTP matrix to 24 exact Turn, Context, Correlation,
  Result, Report, History, Object, Version, Query, Viewer and relationship
  routes.
- Added exact Report read/mutation/revision/compare denial before downstream
  service methods.
- Added exact Dataset payload and Artifact browse/download denial before
  projection or storage.
- Retained the mismatch-as-404 Evidence oracle protection.
- Fixed the Project History pytest compatibility branch so it can never
  swallow a real 403; only a genuinely absent synthetic Project may fall back.

Verification:

- 24-route HTTP matrix: `1 passed`.
- Exact Report/Evidence authorization: `3 passed`.
- Exact Dataset/Artifact pre-storage guards: `2 passed`.
- Ruff, compileall and diff check: passed.

Result:

Data, Turn, Result, Artifact, Version, Evidence, Report and History exact
boundaries now share an executable cross-project contract with no target ID or
private title leakage.

## Improvement #109 — CO-046 (2026-09-05)

Problem:

Global Search lacked date filters, Result destinations did not consistently
follow the authoritative ResearchTurn→ResearchSession relationship, and
Result lifecycle filtering did not inherit archived/trashed session state.

Change:

- Added UTC-normalized inclusive `date_from`/`date_to` filters with invalid
  ranges rejected and all filters bound into the continuation cursor.
- Result destinations now prefer exact Project/Session/Turn SPA routes, then
  exact Turn or Job fallbacks, and finally the safe Research index.
- Result joins validate Project identity before exposing Session/Turn context.
- Result/Finding search continues to use ScientificResult and grounded
  Interpretation authority.
- Added active/archived/trashed coverage across Project, Dataset, Scientific
  Object, Research Session, Report and Result.

Verification:

- Backend search/pagination/authorization focused: `27 passed`.
- Frontend search focused: `28 passed`.
- TypeScript typecheck, Ruff, route registration and diff check: passed.

Result:

Authorized users can discover all supported work with exact SPA navigation and
date/status/type/project filters, without leaking malformed cross-project
lineage or promoting search results to scientific facts.

## Improvement #108 — CO-039 (2026-09-05)

Problem:

Runtime configuration accepted unknown backend values and inconsistent
PostgreSQL/Redis/MinIO aliases; API and worker processes could start with
different Redis namespaces or a misleading partial same-stack topology.

Change:

- Added typed `local | same-stack` runtime profiles and bounded backend values.
- `load_settings()` now fails before serving on missing, conflicting or
  scheme-incompatible PostgreSQL, Redis, MinIO and orchestration settings.
- Worker startup validates the same profile and exact Redis URL/DB namespace
  before connecting or consuming queues.
- Canonical API/worker launchers explicitly select the same-stack profile.
- Failures expose typed error codes without credentials.

Verification:

- Runtime, worker and health focused regression: `35 passed`.
- Ruff and diff check: passed.

Result:

Qualification cannot silently serve SQLite/local infrastructure or split API
and worker namespaces while health appears acceptable.

## Improvement #107 — CO-105 (2026-09-05)

Problem:

Project Home requested the full project history and only then sliced each
section in the browser, making navigation payload and render work grow with
the entire project.

Change:

- Added bounded, stable server pagination for datasets, analyses and activity
  while preserving the legacy unpaginated history contract for other callers.
- Project Home requests eight items per section and appends exact server
  continuation pages independently.
- Continuation requests bypass the first-page cache and preserve exact
  identity, ordering and SPA destinations.

Verification:

- 1000-item deterministic history pagination regression.
- Backend Project History focused: `5 passed`.
- Frontend Project Home focused: `5 passed`.
- Frontend typecheck and diff check: passed.

Result:

Large projects now reach useful Home content with a bounded first payload and
can continue each section without a document reload or client-side full-history
cost.

## Improvement #106 — CO-086 (2026-09-05)

Problem:

Direct Artifact content reads used one generic bounded-validation outcome for
oversized transfers and had no explicit distinction between a temporarily
missing object-store payload and retained Artifact metadata with no payload
location. Viewer and Report surfaces could not explain those states precisely.

Change:

- Browse and download continue through the same exact Job/project
  authorization boundary before storage is touched.
- A temporary object-store miss remains typed `404
  ARTIFACT_CONTENT_NOT_FOUND`.
- Retained Artifact metadata without a storage key is now typed `410
  ARTIFACT_CONTENT_GONE`.
- Payloads above the 64 MiB browser transfer cap fail before storage as `413
  ARTIFACT_CONTENT_TOO_LARGE`; size/hash integrity failures remain `422`.
- Viewer and Report previews show distinct bounded, non-fabricating states;
  GONE and TOO_LARGE do not offer misleading retry loops.

Verification:

- Planner content and authorization focused backend regression: `11 passed`.
- Viewer/Report status regression: `28 passed`.
- Open/download/Presentation link regression: `12 passed`.
- TypeScript typecheck, Ruff, Python compileall and diff check: passed.

Result:

Users get accurate recovery guidance without leaking storage detail, forcing a
download, selecting another version or creating new scientific computation.

## Improvement #105 — CO-033 (2026-09-05)

Problem:

Known Presentation block types could carry undeclared runtime fields, Viewer
selection accepted fuzzy attacker-controlled tokens, and Capability Pack
viewer bindings lacked an explicit boundary against components, module paths
and remote URLs.

Change:

- Added exact per-block Presentation field allowlists and strict nested source,
  reference, confidence and evidence validation.
- Restricted Viewer resolution inputs to bounded declarative tokens; malicious
  or remote descriptors resolve only to the generic safe fallback.
- Capability Pack registration atomically rejects executable/dynamic/remote
  viewer bindings.
- Backend Viewer descriptor identifiers now use bounded declarative schemas.

Verification:

- Backend Pack/Viewer security regression: `44 passed`.
- Frontend Presentation/Viewer security regression: `29 passed`.
- Frontend typecheck, Ruff and diff check: passed.

Result:

Scientific presentation remains repository-reviewed, declarative rendering;
server strings and Packs cannot select arbitrary frontend code or smuggle
HTML/script/remote module payloads.

## Improvement #104 — CO-052 (2026-09-05)

Problem:

Notification Center derived “needs attention” from transient Job status and
had no durable user-specific read/unread model, so refresh, re-entry and
multiple page instances could not preserve what the user had reviewed.

Change:

- Reused `user_configs` for non-scientific, user-private read markers bound to
  user, project, Job and the exact Job update revision.
- A later Job revision automatically invalidates the old marker and becomes
  unread again.
- Read-state writes revalidate project access and the exact Job/project
  relation; revoked projects no longer disclose markers.
- Added bounded read-state GET/PATCH APIs and Notification Center unread
  count/filter/toggle/open-as-read behavior with honest synchronization errors.

Verification:

- Backend persistence, user isolation, revision invalidation and authorization:
  `2 passed`.
- Notification Center and API focused regression: `14 passed`.
- TypeScript typecheck, Ruff, Python compile/import, route registration and
  diff check: passed.

Result:

Notification state now survives navigation and login cycles without becoming
scientific authority, while updated Jobs correctly demand attention again.

## Improvement #103 — CO-030 (2026-09-05)

Problem:

The shared session-expired event correctly represented HTTP 401, but the
re-authentication handoff lost the URL hash and the login page did not explain
that the user's local Research draft and exact return location were preserved.

Change:

- Session-expiry redirects now retain `pathname + search + hash` and carry the
  bounded reason `session-expired`.
- The login surface distinguishes re-authentication from an ordinary login,
  explains draft preservation, and returns to the exact local URL after
  success.
- External and ambiguous return URLs continue to fail closed.
- Authentication remains Cookie/session based; no browser token store or
  scientific failure state was introduced.

Verification:

- Focused ProductShell/LandingPage regression: `27 passed`.
- Frontend typecheck and diff check: passed.
- Successful, failed and unsafe-return re-authentication paths are covered.

Result:

An expired browser session is now a recoverable authentication interruption,
not a lost Research draft or a misleading scientific execution failure.

## Improvement #102 — CO-071 (2026-09-05)

Problem:

The generic Plot renderer used only a broad point count. Heatmaps lacked a
dedicated cell limit, while `mesh3d` counted vertices but not triangle indices,
so an otherwise small vertex set could still create an excessive GPU payload.

Change:

- Added a 100,000-cell heatmap cap.
- Added independent 100,000 vertex and 100,000 triangle mesh caps.
- Over-cap payloads show a type-specific refused state rather than silently
  truncating or freezing the tab.
- The complete persisted Artifact remains available through its authorized
  open/download path.

Verification:

- Focused generic plot regression: `13 passed`.
- Oversized heatmap and 100,001-triangle mesh cases are covered.
- TypeScript typecheck and diff check: passed.

Result:

Heavy heatmap and mesh payloads now fail predictably before reaching Plotly,
without changing scientific values, units, source identity or Artifact
authority.

## Improvement #101 — CO-136 (2026-09-05)

Problem:

Repeated acceptance runs had left eleven obsolete repository-owned Next
frontends plus wrapper processes listening between ports 3000 and 3023,
wasting memory and making browser evidence easy to collect from stale builds.

Change:

- Added a health-gated frontend rotation script with dry-run as the default.
- It excludes the current port and only admits a `node.exe` listener whose
  command line points to this repository's exact Next binary, `next start` and
  the candidate port.
- `-Apply` uses PowerShell confirmation semantics and stops only eligible
  listener PIDs.
- Output is bounded JSON and does not expose command lines or repository paths.

Verification:

- Focused deterministic tests: `2 passed`.
- Live temporary frontend on port 3025:
  dry-run identified only PID `26440`; apply stopped exactly PID `26440`.
- Port 3025 closed; current 3024, API 8005, PostgreSQL 55434, Redis 6379 and
  MinIO 9000 remained healthy.
- Ports 3000–3025 now contain only the current frontend on 3024.
- Diff check: passed.

Result:

Acceptance can rotate to a current immutable frontend without retaining stale
Next servers or risking backend, worker, database, queue or object-storage
processes.

## Improvement #100 — CO-035 (2026-09-05)

Problem:

Research acknowledgement and first truthful progress had only isolated manual
wall-clock samples. A local timer would be lost when the App Router moved from
the Research index to an exact Turn route, and automation `click()` duration
incorrectly included handler/navigation work.

Change:

- Added a current-tab, bounded 50-sample Research performance ledger containing
  only opaque attempt/Turn identity, status and timing.
- Measured visible acknowledgement after two animation frames.
- Bound the attempt to the exact created ResearchTurn and recorded only its
  first persisted progress status.
- Added deterministic p50/p95 reporting and a hidden, content-free diagnostic
  output for browser acceptance.
- Defined non-blocking budgets of 500 ms acknowledgement and 1500 ms first
  truthful progress; diagnostics never block Research.

Verification:

- Helper tests: `5 passed`; focused Research regression: `1 passed`.
- Same-stack runtime: PostgreSQL, Redis, MinIO, Redis workers and configured
  DeepSeek all healthy.
- Five exact Turns:
  `44a0fef8-fe87-4265-8de7-c4403cfd8760`,
  `857a7e5e-d634-4c91-bad5-d01f1f7fd6ab`,
  `84eeb963-7d56-4422-aec4-7698d58cdff5`,
  `1d5a494a-9dc2-45c1-9168-055baaf663c2`,
  `fac4a3e5-e04c-4973-a69f-6aefa2065a52`.
- Acknowledgement p50/p95: `26/29 ms`.
- First persisted `RECEIVED` p50/p95: `262/293 ms`.
- Browser warnings/errors: `0`; typecheck and production build: passed.

Result:

Research responsiveness is now measured at the correct product boundary across
route transitions, without fabricated progress, prompt content, credentials or
scientific recomputation.

## Improvement #99 — CO-045 (2026-09-05)

Problem:

Global search stopped at a fixed aggregate window and exposed only a terminal
`truncated` warning, so users could not traverse a long authorized result set.

Change:

- Added a bounded continuation cursor bound to user, query, project, type and
  lifecycle filters.
- Re-applied project authorization on every page, used stable time/entity
  ordering and deduplicated by authorized entity identity.
- Added frontend Load more/retry behavior that keeps already loaded results
  and explicitly discloses the server scan bound.

Verification:

- Backend pagination/authorization regression: `9 passed`.
- Frontend ProductShell regression: `22 passed`.
- 125 authorized results traversed as `23,23,23,23,23,10`, with `125` unique
  identities and `0` private-project leaks.
- Cross-user or changed-filter cursor reuse: `422` fail closed.
- Typecheck, Ruff and diff check: passed.

Result:

Long search results are navigable without a document reload, silent omission,
duplicate entities or cross-project metadata disclosure.

## Improvement #98 — CO-058 (2026-09-05)

Problem:

ResearchTurn, Job, ToolCall, Result and Report already had authoritative
persisted relations, but operators had to query several repositories and risk
exposing raw parameters or storage/provider details to trace one request.

Change:

- Added an authorized read-only correlation endpoint for one exact
  ResearchTurn.
- Projected Project/Session/Turn, Job, bounded ToolCall, Result and Report
  identities plus typed integrity warnings.
- Limited ToolCalls to 64 with an explicit truncation flag.
- Excluded Tool parameters, error payloads, paths, storage keys, provider
  requests, queue internals and credentials.

Verification:

- Focused correlation API regression: `2 passed`.
- Cross-project access, empty lineage, full lineage and 65th-call truncation
  covered.
- Ruff, compileall and scoped diff check: passed.

Result:

One scientific request is diagnosable across the durable lineage through a
bounded, authorized projection without creating scientific authority or
leaking operational secrets.

## Improvement #97 — CO-069 (2026-09-05)

Problem:

An async Plotly `newPlot` that completed after unmount could call `purge`
again after normal cleanup, creating a duplicate-release race.

Change:

- Made the generic Plotly surface purge path idempotent.
- Preserved ResizeObserver, window-listener and unmount cleanup.
- Audited existing scene, trajectory, phonon and volumetric viewer disposal
  paths for engine/worker/request/listener cleanup.

Verification:

- Focused renderer cleanup regression: `60 passed`.
- TypeScript typecheck and diff check: passed.
- No cleanup path creates a Job, ToolCall or ScientificResult.

Result:

Rapid Artifact switching or unmount during async plot creation releases the
surface exactly once and does not introduce read-only scientific recomputation.

## Improvement #96 — CO-032 (2026-09-05)

Problem:

Provider payloads and durable Job/Tool/Report failure summaries did not share a
recursive sentinel scan, leaving a risk that credentials, service endpoints or
absolute paths could escape through nested error structures.

Change:

- Added recursive payload and text redaction plus a deterministic sensitive
  sentinel scanner.
- Covered credential fields and values, Bearer/API tokens, Redis/MinIO/S3
  endpoints and absolute paths.
- Applied the shared redactor to Provider requests/errors, queue Job/Tool/
  dependency failure events and Report failure summaries.
- Preserved scientific numeric values, units, sample/version identities and
  evidence references.

Verification:

- Focused secret-safety campaign: `37 passed`.
- Sensitive scanner and Provider subset: `11 passed`.
- Report/export/project-authorization regressions: passed.
- Web typecheck, touched Python compileall, touched Ruff and diff check: passed.

Result:

Nested operational failures now fail closed against credential, endpoint and
filesystem leakage without erasing authoritative scientific content.

## Improvement #95 — CO-135 (2026-09-05)

Problem:

Artifact open and download actions used the same response semantics, so the
browser could not reliably distinguish inline scientific inspection from an
explicit native download.

Change:

- Added an optional authorized `download=true` query to the existing Artifact
  content route.
- Kept normal open behavior inline.
- Added a sanitized attachment `Content-Disposition` only for explicit
  downloads.
- Reused the same project authorization and exact Artifact content authority.

Verification:

- Backend Artifact content regression: `7 passed`.
- Frontend Artifact/presentation/report regression: `35 passed`.
- TypeScript typecheck: passed.

Result:

Scientific inspection remains inline while explicit downloads use a bounded,
safe native filename without adding a second Artifact route or authority.

## Improvement #86 — CO-048 (2026-09-05)

Problem:

Saved-search mutations could leave another open shell or browser tab with a
stale list, while two transport mechanisms could deliver duplicate refreshes.

Change:

- Added a bounded saved-search invalidation channel using same-document events,
  `storage`, and `BroadcastChannel`.
- Broadcast only a random revision marker, never saved-search content.
- Deduplicated revisions and ignored malformed markers.
- ProductShell refreshes its authorized list after successful mutations.

Verification:

- `saved-search-sync.test.ts`: `5 passed`.
- `ProductShell.test.tsx`: `21 passed`.
- TypeScript typecheck: passed; diff check passed with known CRLF warnings.

Result:

Saved-search state converges across open/close and multi-tab use without
hard reloads or cross-tab content leakage.

## Improvement #87 — CO-109 (2026-09-05)

Problem:

Scientific Artifact rendering repeatedly scanned the Artifact bundle to resolve
the active renderer, adding avoidable O(n) work during gallery updates.

Change:

- Added deterministic identity indexing in the renderer registry.
- Memoized the index at the Artifact Gallery boundary so repeated renders use
  O(1) identity lookup.

Verification:

- Workspace renderer regression: `11 passed` (including a 500-artifact index case).
- TypeScript typecheck: passed.
- Diff check: passed with known CRLF warnings.

Result:

Large Artifact galleries no longer repeat linear matching for every render while
preserving exact Artifact identity and renderer selection.

## Improvement #88 — CO-055 (2026-09-05)

Problem:

Research and Task Center represented the same cancellation transition with
different labels (`CANCELING` vs `cancel_requested`) and refresh cadences,
making a slow server-side cancellation look stale or ambiguous.

Change:

- Added a shared cancellation status/label contract and 1.8-second polling
  interval while cancellation is pending.
- Task Center now refreshes until the persisted task reaches a terminal state.
- Both surfaces disable duplicate stop actions and clearly say that server
  confirmation is pending.

Verification:

- Cancellation-focused regression: `25 passed`.
- TypeScript typecheck: passed.
- Diff check: passed with known CRLF warnings only.

Result:

Cancellation now has one truthful lifecycle across Research and Task Center;
pending work is never presented as completed and repeated stop requests are
prevented.

## Improvement #89 — CO-134 (2026-09-05)

Problem:

Artifact download names were passed directly into the browser `download`
attribute. Although content retrieval is authorized server-side, path
separators and control characters are unnecessary and unsafe metadata.

Change:

- Added bounded filename sanitization before rendering the download link.
- Removes control characters and path separators, strips leading dot traversal,
  caps names at 120 characters, and rejects empty/dot-only names.
- Kept the existing trusted Artifact route allow-list and server authorization.

Verification:

- Artifact download focused regression: `3 passed`.
- TypeScript typecheck: passed.
- Diff check: passed.

Result:

Artifact downloads retain useful names without allowing caller-controlled path
or control metadata to reach the browser surface.

## Improvement #90 — CO-051 (2026-09-05)

Problem:

Task Center only exposed a client-side slice of the task feed, making older
jobs inaccessible and encouraging large unbounded first-page payloads.

Change:

- Reused the authorized server cursor feed and retained `nextCursor`.
- Added a bounded “读取更早任务” path that loads one page at a time.
- Merged pages by stable `projectId:jobId` identity while preserving exact
  ResearchTurn links, filters and sorting.
- Added explicit retry state for later-page failures.

Verification:

- Task feed and Task Center regression: `21 passed`.
- TypeScript typecheck: passed.
- Diff check: passed.

Result:

Researchers can navigate long task histories without a large initial payload or
loss of exact Research links, and pagination remains read-only.

## Improvement #91 — CO-110 (2026-09-05)

Problem:

Scientific Viewer loading used one generic spinner even after Artifact metadata
was available, hiding identity, provenance and recovery actions during slow
payload transfers.

Change:

- Split metadata-ready from heavy-payload-ready presentation states.
- During delayed loading, expose Artifact identity/type/name, ToolCall and
  checksum provenance plus the existing source/retry entry.
- Reuse the same metadata block for missing and failed payload states.

Verification:

- Scientific Viewer effect regression: `8 passed`.
- TypeScript typecheck: passed.
- Diff check: passed with known CRLF warnings only.

Result:

Researchers retain scientific identity and a truthful recovery path while large
Viewer payloads load, without triggering recomputation or changing authority.

## Improvement #92 — CO-054 (2026-09-05)

Problem:

Task Center “Open” and “Open and retry” previously resolved to the same route
and could not communicate whether a new scientific lineage would be created.

Change:

- Open continues to restore the existing exact ResearchTurn without a retry flag.
- Retry uses explicit `retry=1`, checks the persisted failure/cancel state and
  session write authority, then creates one child Turn with `parent_turn_id`.
- The original failed Turn and its evidence remain addressable.

Verification:

- Research and Task Center combined regression: `99 passed`.
- TypeScript typecheck: passed.
- Diff check: passed with known CRLF warnings only.

Result:

Users can distinguish resuming history from deliberately creating a new
execution lineage, and retry cannot overwrite the original evidence.

## Improvement #93 — CO-037 (2026-09-05)

Problem:

Narrow/mobile report and presentation grids could retain intrinsic minimum
content widths, causing global horizontal clipping even when a wide table had a
local scroll container.

Change:

- Added `min-width: 0` and `max-width: 100%` to report/presentation grid items.
- Allowed mobile action controls to wrap while retaining reachable control height.
- Made wide table regions independently focusable and scrollable, keeping global
  overflow bounded.

Verification:

- Workspace Artifact Gallery responsive regression: `7 passed`.
- TypeScript typecheck: passed.
- Diff check: passed with known CRLF warnings only.

Result:

390x844 and high-zoom users can reach table controls and sample selection
without the whole page being clipped by wide scientific content.

## Improvement #94 — CO-056 (2026-09-05)

Problem:

Research remount/reconnect recovered progress and Result fragments but did not
explicitly validate `Project + Session + Turn` scope or rebuild a missing user
message from the persisted ResearchTurn.

Change:

- Resolve recovery only from the authorized session-scoped Turn inventory.
- Fail closed when project, session or Turn identity does not match.
- Rebuild a missing user question from the persisted Turn.
- Refresh Project History, Session and Turn data on mount, visibility and
  network recovery while existing APIs restore progress and Result.

Verification:

- Exact recovery/reconnect focused tests: passed.
- Full Research suite: `88 passed, 1 known order-sensitive context retry
  failure`; that case passes alone.
- TypeScript typecheck: passed.

Result:

Leaving, refreshing or reconnecting restores exact durable Research state
without Job-name guessing or reliance on frontend memory.

## Improvement #95 — CO-135 (2026-09-05)

Problem:

Artifact “open” and “download” links used the same response semantics. Browser
behavior depended only on the client attribute and did not give the authorized
server route an explicit disposition intent.

Change:

- Download links add the bounded `download=true` query flag.
- The existing job-scoped authorized route returns `Content-Disposition:
  attachment` only for that flag, using a sanitized bounded Artifact name.
- Open links remain inline; both modes retain the same hash/size/media-type
  validation, no-store policy and project authorization.

Verification:

- Backend Artifact content regression: `7 passed`.
- Frontend presentation/report/download regression: `35 passed`.
- TypeScript typecheck: passed.

Result:

Opening and downloading persisted Artifact content now have predictable,
separate product semantics without duplicating content or authorization.

## Improvement #85 — CO-103 (2026-09-05)

Problem:

ProductShell fallback prewarming issued several speculative route requests in
one burst shortly after mount, competing with the primary surface on cold
startup.

Change:

- Added a bounded, cancelable prefetch queue that schedules one route per idle
  callback (or a 50 ms timer fallback).
- Applied it to projectless and isolated project-shell fallback prewarming.
- Cleanup cancels pending idle/timer work on route changes and unmount.

Verification:

- Dedicated scheduler regression: `1 passed`.
- TypeScript typecheck: passed.
- Diff check: passed with known CRLF warnings only.

Result:

Speculative navigation remains available without a cold-login request burst,
and abandoned routes no longer continue prefetching after the shell changes.

## Improvement #84 — CO-049 (2026-09-05)

Problem:

Task Center and Notification Center used the same feed but maintained separate
subscriptions, lifecycle listeners and polling state, duplicating network work
and allowing their synchronization states to drift.

Change:

- Added one bounded shared feed subscription with an immutable snapshot.
- The first consumer owns one request, interval and online/visibility listener
  set; the last unsubscribe aborts and releases them.
- Manual refresh and post-cancel refresh use the same shared authority.
- Preserved CO-050 hidden/offline pause and multi-consumer cancellation rules.

Verification:

- Task/Notification/cache focused regression: `22 passed`.
- Merged TypeScript typecheck: passed.
- Diff check: passed with known CRLF warnings only.

Result:

Opening both product centers now produces one initial request and one recovery
refresh, while each surface retains independent filtering and presentation.

## Improvement #83 — CO-097 (2026-09-05)

Problem:

The Research branch switcher exposed arrow counters but not enough persisted
source context to distinguish similar branches.

Change:

- Derived labels only from server-returned Turn, parent Turn, message revision
  and user question fields.
- Added target-aware previous/next labels plus a bounded all-branches
  disclosure.
- Displayed source question, exact ResearchTurn and message-revision identity,
  with `aria-current` on the active branch.
- Kept Result restoration behind the existing exact Turn route.

Verification:

- Full Research regression: `86 passed`.
- Merged TypeScript typecheck: passed.
- Diff check: passed with known CRLF warnings only.

Result:

Researchers can identify and navigate branches without guessing from counters
or losing immutable lineage.

## Improvement #82 — CO-088 (2026-09-05)

Problem:

Bounded Figure previews could fill their point budget from the beginning of a
series and miss scientifically important extrema later in the source.

Change:

- Workspace Plot and Report SVG sampling now preserve endpoints and global
  minimum/maximum values before using the remaining budget for bucket-local
  extrema.
- Both surfaces disclose displayed/total point counts and the deterministic
  sampling strategy.

Verification:

- Workspace Plot and Report preview focused regression: `24 passed`.
- Merged TypeScript typecheck: passed.
- Diff check: passed with known CRLF warnings only.

Result:

Large Figure previews remain bounded without hiding later critical peaks or
presenting a sampled trace as complete authority.

## Improvement #81 — CO-083 (2026-09-05)

Problem:

Data table query, sort, selected row and exact sample selection lived only in
component state. Reloading or sharing the Data page lost the user's view even
though Dataset/Object/Version route authority was already present.

Change:

- Added bounded `tableQuery`, `tableSort`, `tableRow` and canonical `selection`
  route state.
- Query changes replace the current entry; sort and row/selection changes add
  navigable history entries.
- Reused the existing canonical selection token and rejects malformed,
  cross-project or cross-Dataset state.
- Preserved existing Dataset/Object/Version parameters and added a visible
  shareability note.

Verification:

- Product/Data regression: `48 passed`.
- Merged TypeScript typecheck: passed.
- Diff check: passed with known CRLF warnings only.

Result:

Refresh, copied URLs and browser history can restore the same bounded Data view
without inventing a new scientific identity or silently changing versions.

## Improvement #80 — CO-050 (2026-09-05)

Problem:

Task Center and Notification Center continued fixed-interval polling while the
tab was hidden or the browser was offline. In-flight responses could complete
after state changed, and either consumer could not cancel safely without
risking the shared request used by the other surface.

Change:

- Added caller-aware `AbortSignal` support to the shared task-feed cache.
- The shared transport now aborts only when every cancelable consumer has
  released it.
- Hidden-tab and offline transitions cancel in-flight refreshes and suppress
  the 30-second polling loop.
- Visibility and online recovery trigger a fresh authorized read.
- Expected aborts do not surface as synchronization failures or overwrite
  newer state.

Files:

- `apps/web/app/lib/task-center-data.ts`
- `apps/web/app/lib/task-center-data.test.ts`
- `apps/web/app/components/TaskCenterPage.tsx`
- `apps/web/app/components/TaskCenterPage.test.tsx`
- `apps/web/app/components/NotificationCenterPage.tsx`
- `apps/web/app/components/NotificationCenterPage.test.tsx`
- `docs/agent2/continuous_optimization/evidence/co-050-task-polling-lifecycle-2026-09-05.json`

Verification:

- Focused cache/Task/Notification regression: `21 passed`.
- TypeScript typecheck: passed in the merged worktree.
- `git diff --check`: passed; only known CRLF conversion warnings.

Result:

Background product surfaces stop consuming network and rendering stale
responses when they cannot be observed or reached, then recover from persisted
authority without a hard page reload.

New findings:

- CO-049 remains open for further shared subscription/cache consolidation.

## Improvement #79 — CO-115 (2026-09-05)

Problem:

Project, Research-session and Report organization used generic “固定” wording
alongside scientific Result/source context pinning. Users could reasonably
misread a list-sorting action as changing what the Agent knows.

Change:

- Standardized non-scientific organization actions and status labels to
  `列表置顶` / `取消列表置顶`.
- Renamed Result and exact-source actions to explicit
  `加入本会话上下文` / `从本会话上下文移除`.
- Renamed session-memory chips to `上下文对象` and `上下文结果`.
- Added a visible explanation that session context can affect later research,
  while list pinning only changes ordering.
- Kept all existing authorization, persistence and scientific authority
  contracts unchanged.

Files:

- `apps/web/app/components/Agent2ScientificPresentation.tsx`
- `apps/web/app/components/ResearchPages.tsx`
- `apps/web/app/components/ProductPages.tsx`
- `apps/web/app/components/ScientificReportsIndexPage.tsx`
- the four corresponding focused test files
- `docs/agent2/continuous_optimization/evidence/co-115-pin-context-semantics-2026-09-05.json`

Verification:

- Focused frontend regression: `151 passed`.
- TypeScript typecheck: passed.
- `git diff --check`: passed; only the repository's existing CRLF conversion
  warnings were emitted.

Result:

Users can now distinguish organization metadata from scientific working
context before taking either action. No Result, object version or execution
authority changed.

New findings:

- CO-029 remains open for the broad cross-project route campaign.

The initial pool was derived from independent repository audits covering
scientific presentation, Research/context, lifecycle, search/tasks,
authorization, service recovery, CI/build, storage and developer experience.
Each item is independently actionable and includes repository evidence plus a
verification method in `OPTIMIZATION_BACKLOG.md`.

## Improvement #56 — CO-098 (2026-09-05)

- 状态：已完成并验证；持续优化总任务继续处理中。
- Research 生命周期菜单在 archive/restore 后恢复来源焦点；当行因筛选
  消失时回退到当前状态筛选按钮，并通过 `aria-live="polite"` 播报成功状态。
- 修改文件：`apps/web/app/components/ResearchPages.tsx`、
  `apps/web/app/components/ResearchPages.test.tsx`及 CO-098 evidence。
- 验证：生命周期 focused test `1 passed, 74 skipped`；`npm run typecheck`
  通过。
- 收益：键盘用户在可逆生命周期操作后不会丢失工作位置，且状态变化可被
  屏幕阅读器获知；未改变科学身份或历史记录。

## Improvement #57 — CO-132 (2026-09-05)

- 状态：已完成并验证；持续优化总任务继续处理中。
- 修复 Scientific Table 中共享同一 `objectId` 的样本行 React key 冲突；
  现在优先使用带对象作用域的 `sampleKey`/`sample_id`/`sampleRef`/`id`，
  无稳定身份时使用确定性的行回退键。
- 修改文件：`apps/web/app/components/workspace/WorkspaceArtifactGallery.tsx`、
  `apps/web/app/components/workspace/WorkspaceArtifactGallery.test.tsx`及
  CO-132 evidence。
- 验证：gallery focused tests `5 passed`且无 duplicate-key warning；
  `npm run typecheck` 通过。
- 收益：205 行同对象数据在分页、筛选与重排时保持稳定 React 身份，
  消除控制台噪声和潜在 DOM 状态漂移；未改变科学事实权威。

## Improvement #58 — CO-081 (2026-09-05)

- Dataset inspector 以 `objectId:sampleRef` 和样本引用为主要身份；源行号
  降为“辅助定位”，并在表头、提示和可访问名称中明确不是持久身份。
- 修改文件：DatasetMaterialsExplorerPanel 及对应 focused test/evidence。
- 验证：focused tests `12 passed`；typecheck 与 diff check PASS。
- 收益：排序、过滤和重新投影不会诱导用户用视觉行号引用科学样本。

## Improvement #59 — CO-099 (2026-09-05)

- `CANCELED` 后只由 Research execution card 呈现终态，不再同时显示重复
  cancel notice；停止请求已记录和竞态完成提示仍保留。
- 修改文件：ResearchPages 及对应 focused test/evidence。
- 验证：ResearchPages cancel cases `3 passed`；ResearchExecutionActivity
  `11 passed`；typecheck PASS。
- 收益：快速停止、409 竞态与持久化取消终态不会向用户播报冲突状态。

## Improvement #60 — CO-090 (2026-09-05)

- 重复 Scientific Presentation 的 Evidence item、inspector 与 Finding anchor
  全部加入实例作用域；Viewer 已有实例级 ID，Report 单文档路由不扩大修改。
- 修改文件：ScientificPresentationBlocks 及对应 focused test/evidence。
- 验证：Presentation/Viewer/Report `35 passed`；typecheck 与 diff check PASS。
- 收益：同页多个科学呈现的 `href`、`aria-controls` 与标题关系不会串到其他实例。

## Improvement #61 — CO-133 (2026-09-05)

- Workspace Artifact Gallery 的主标题、分组标题和活动 Viewer 标题 ID 使用
  `useId` 实例作用域，替代静态全局 ID。
- 修改文件：WorkspaceArtifactGallery 及对应 focused test/evidence。
- 验证：gallery `6 passed`；typecheck PASS。
- 收益：分栏或重复 Workspace 场景下，ARIA 标题关系仍解析到本实例。

## Improvement #62 — CO-108 (2026-09-05)

- Generic JSON Artifact 预览改为有界结构投影，限制节点、层级、数组项、
  对象字段和长文本字符，再序列化投影结果；不再先序列化完整大 payload。
- 预览明确显示精确省略数量/预算原因，并声明完整内容仍保留在 Artifact。
- 修改文件：WorkspaceArtifactGallery、ScientificWorkspaceShell focused test
  及 CO-108 evidence。
- 验证：10 万项数组只读取前 128 项，尾部 getter 未触发；focused test
  `1 passed`，typecheck PASS。
- 收益：大 JSON 查看不再因完整同步序列化阻塞主线程，同时不改变或伪装
  科学权威内容。

## Improvement #63 — CO-075 (2026-09-05)

- Source-missing/metadata-only/invalidated Viewer 保留精确版本、内容指纹、来源
  数量和来源入口；增加只包含有界元数据的安全导出，不含科学 payload。
- 验证：ScientificObjectViewer + ScientificViewerShell `6 passed`；
  typecheck PASS。
- 收益：历史 payload 缺失时仍可审计身份和来源，且不会静默替代或重算。

## Improvement #64 — CO-093 (2026-09-05)

- Research 状态筛选保留命名组，并增加 Arrow/Home/End 键盘导航；移动焦点
  同步更新筛选、`aria-pressed` 与批量选择状态。
- 验证：ResearchPages 合并回归 `77 passed`；typecheck PASS。
- 收益：状态分段控件可被键盘和读屏稳定理解与操作。

## Improvement #65 — CO-102 (2026-09-05)

- 空 Research 项目将主要入口指向 Data Platform；read-only 用户可查看数据，
  archived/trashed 项目不再因 owner 角色误获研究写权限，并保留历史说明。
- 验证：ResearchPages 合并回归 `77 passed`；typecheck PASS。
- 收益：用户不再困在无数据空状态，且入口遵循真实项目生命周期与授权。

## Improvement #66 — CO-117 (2026-09-05)

- service-backed CI 改用 pytest 原生 JUnit XML；仓库解析器聚合多个 suite 的
  selected/passed/skipped/failed/errors，并执行 zero-skip/最小通过数门禁。
- 验证：解析器 `2 passed`，真实 pytest JUnit smoke 为 selected=2、
  passed=2、skipped/failed/errors=0；touched Ruff 与 diff check PASS。
- 收益：CI 不再因终端颜色、summary 顺序或多段输出而误判集成资格。

## Improvement #67 — CO-111 (2026-09-05)

- ScientificObject Viewer 重试保留 AbortController，增加进行中去重、最大
  1 秒有界指数退避与卸载清理；退避/请求期间按钮禁用并呈现真实状态。
- 验证：ScientificObjectViewer `4 passed`；typecheck/diff check PASS。
- 收益：快速重复点击不会产生并发 payload 请求或旧响应覆盖。

## Improvement #68 — CO-113 (2026-09-05)

- Trash Center 增加逐项/全选和“恢复所选”；按实体/项目复用服务端原子批量
  API，只有完整成功批次从列表移除，失败组保留选中并显示 typed partial result。
- 验证：Trash Center `8 passed`；typecheck/diff check PASS。
- 收益：混合授权批量恢复既不会丢失失败项，也不会把部分成功伪装为全成功。

## Improvement #69 — CO-119 (2026-09-05)

- service-backed CI 使用 `always()` 生成脱敏 operations snapshot，并上传
  integration log、exit、JUnit XML 和 runtime JSON，失败路径同样保留诊断。
- 验证：workflow YAML parse PASS；operations tests `11 passed, 1 historical
  skip`；本机同栈 snapshot status=ok，PostgreSQL/Redis/MinIO 与 6 workers 正常。
- 收益：集成失败不再只留下终端片段，可追溯 exact test report 与服务健康。

## Improvement #70 — CO-104 (2026-09-05)

- 为 30 秒 Research session 预热缓存补充 lifecycle mutation 回归：重复读取
  继续合并为一个请求，archive/restore/rename mutation 后下一次读取必须
  重新访问授权 API。
- 修改文件：`apps/web/app/lib/product-api.test.ts`及 CO-104 evidence。
- 验证：product-api `7 passed`；typecheck/diff check PASS。
- 收益：跨 Data/Viewer/History/Research 预热不会在生命周期操作后展示旧列表。

## Improvement #1 — CO-001

Problem:

The persisted Report figure preview retained authoritative `x` values in its
payload but positioned points by array index. Non-uniform scientific sampling
such as `0, 0.1, 10` therefore appeared evenly spaced and could mislead a
researcher about the geometry of an XRD, trajectory or electronic curve.

Why now:

This was a high-impact, high-confidence scientific-communication correctness
defect with a small bounded fix. It affected presentation only and did not
require changing Artifact or ScientificResult authority.

Root cause:

`FigurePreview` used `left + index * step` for every circle/polyline point.
The persisted numeric `x` array was used only in the React key.

Change:

- Parse finite persisted numeric `x` coordinates.
- Apply one shared numeric x-domain across the bounded displayed traces.
- Preserve index spacing only as a safe fallback for categorical/missing x.
- Center a constant numeric domain instead of inventing a range.
- Keep the existing 96-point display budget and read-only behavior.

Files:

- `apps/web/app/components/ScientificReportArtifactPreview.tsx`
- `apps/web/app/components/ScientificReportArtifactPreview.test.tsx`

Verification:

- Focused Vitest: `7 passed`.
- Added non-uniform-x regression proving the second point is positioned at
  one percent of the total x span rather than halfway across the chart.
- Frontend TypeScript typecheck: PASS.
- `git diff --check` for the touched scope: PASS (only the existing TASKS.md
  line-ending warning).
- Same-stack authenticated browser:
  `agent2_report_e54681009a0e49abe371247d9053ce61` opened at port `3023`;
  the persisted MSD preview rendered `92` points and browser error log was
  empty.

Result:

Report previews now communicate authoritative numeric x spacing without
recomputing or changing scientific data.

New findings:

- CO-087: previews still need explicit authoritative ticks/ranges/units.
- CO-088: bounded point sampling needs a disclosed extrema-preserving policy.

## Improvement #2 — CO-002

Problem:

The Report table preview used the visual array index as its React identity when
a row lacked `id`, `sample_id` or `site_index`. Sorting, refreshed projections
or column-order changes could therefore make React reuse one scientific row's
DOM as another row.

Root cause:

The `<tr>` key was
`row.id ?? row.sample_id ?? row.site_index ?? index`; there was no
deterministic fallback derived from the persisted row.

Change:

- Prefer a unique bounded semantic identifier from the persisted row.
- Fall back to a canonical, property-order-independent row representation.
- Disambiguate only completely identical duplicate rows with an occurrence
  suffix; visual position is no longer the default identity.

Files:

- `apps/web/app/components/ScientificReportArtifactPreview.tsx`
- `apps/web/app/components/ScientificReportArtifactPreview.test.tsx`

Verification:

- Focused Vitest: `9 passed`.
- Reorder regression proves rows without explicit IDs retain their identities.
- Semantic `sample_id` regression and duplicate-row uniqueness both pass.
- Frontend TypeScript typecheck: PASS.
- Touched-scope `git diff --check`: PASS.

Result:

Report table previews now preserve deterministic scientific row identity across
display reordering without creating a new data authority.

New findings:

- No new candidate was required; CO-003 tracks the independently implemented
  Materials Explorer table equivalent.

## Improvement #3 — CO-003

Problem:

The reusable Materials Explorer `DataTable` used the visual array index as the
React key for composition, structure, quality and comparison rows. A display
reorder or refreshed projection could reuse the wrong row DOM.

Root cause:

The helper accepted only `string[][]`, so the authoritative upstream semantic
identity had already been discarded before rendering.

Change:

- Replace positional rows with bounded `{ key, cells }` rows.
- Bind chemical system, structure object, quality column/value and comparison
  property identities at their authoritative call sites.
- Preserve stable keys across reordering and deterministically disambiguate
  duplicated upstream identities.

Files:

- `apps/web/app/components/dataset-explorer/DatasetMaterialsExplorerPanel.tsx`
- `apps/web/app/components/dataset-explorer/DatasetMaterialsExplorerPanel.test.tsx`

Verification:

- Focused Vitest: `11 passed`.
- Reordering and duplicated-upstream-identity regressions: PASS.
- Frontend TypeScript typecheck: PASS.
- Touched diff check: PASS with only existing line-ending notices.

Result:

Materials Explorer summary tables no longer promote visual position to
scientific row identity.

New findings:

- No additional candidate; CO-081 separately covers the user-facing row-number
  wording in the sample inspector.

## Improvement #4 — CO-005

Problem:

Both modern ResearchTurn and legacy Job polling relied mainly on an `active`
boolean. Leaving a Turn stopped state writes but did not cancel network work,
clear every retry timer or prevent an online event from starting overlapping
polls. Legacy terminal Interpretation callbacks could also finish after the
user switched research.

Root cause:

The polling API helpers did not accept an `AbortSignal`; the effects had no
single in-flight guard, and the legacy Job timer was not retained for cleanup.

Change:

- Add optional request signals to ResearchTurn progress, Planner Job, event and
  Artifact reads.
- Abort in-flight polling on Turn/Job change or unmount.
- Allow only one progress request per polling effect at a time.
- Clear scheduled retries on cleanup.
- Guard legacy Interpretation/Evidence callbacks with the exact active lineage.
- Ignore only typed `AbortError`; real network failures retain existing error
  behavior.

Files:

- `apps/web/app/lib/agent2-execution-api.ts`
- `apps/web/app/lib/planner-api.ts`
- `apps/web/app/components/ResearchPages.tsx`
- `apps/web/app/components/ResearchPages.test.tsx`

Verification:

- ResearchPages focused regression: `73 passed`.
- New test proves an in-flight ResearchTurn request is aborted on unmount and
  online events cannot create an overlapping or post-unmount poll.
- Typed AbortError classification regression: PASS.
- Frontend TypeScript typecheck: PASS.
- Touched diff check: PASS with only existing line-ending notices.

Result:

Long-running Research navigation releases obsolete requests and cannot apply
late polling/interpretation state to a different Turn.

New findings:

- CO-004 remains a separate authority issue: when both a legacy run ID and an
  explicit ResearchTurn ID are present, only the Turn should drive execution
  state.

## Improvement #5 — CO-004

Problem:

Project History intentionally retains both a related Job ID and an explicit
ResearchTurn ID. The Research route previously hydrated the legacy Job and
could start its poller while the authoritative ResearchTurn progress effect was
also active.

Root cause:

`runId` unconditionally initialized legacy loading and historical Job
hydration. The legacy polling effect did not yield authority when
`agent2TurnId` was present.

Change:

- Treat an explicit ResearchTurn as the execution-state authority.
- Keep related `runId` only for persisted history/session provenance.
- Skip legacy Job detail/events/artifacts/interpretation hydration and polling
  when the route has an authoritative Turn.
- Preserve legacy run-only behavior.

Files:

- `apps/web/app/components/ResearchPages.tsx`
- `apps/web/app/components/ResearchPages.test.tsx`

Verification:

- ResearchPages focused regression: `74 passed`.
- New run+turn test verifies Turn progress renders while Planner Job, event and
  Artifact readers are never called.
- Frontend TypeScript typecheck: PASS.
- Touched diff check: PASS with only existing line-ending notices.

Result:

One route can no longer have two execution-state authorities or mix a legacy
Job workbench with current ResearchTurn progress.

New findings:

- CO-036 is now selected to close the user-visible SPA navigation/reload gap.

## Improvement #6 — CO-036

Problem:

The product had shared Next.js navigation primitives, but no repeatable browser
qualification proving that the user-facing Data → Research → Viewer → Report →
History path remained a single-page application. Without this guard, a later
link or layout change could silently reintroduce document reloads and make
scientific navigation feel slow or lose runtime state.

Investigation:

- The authenticated same-stack browser served the current frontend at
  `http://127.0.0.1:3023`.
- A standalone Chrome probe confirmed the existing implementation already uses
  client routing: the three primary transitions produced zero document
  requests, preserved `performance.timeOrigin`, and preserved a page-runtime
  marker.
- Warm transition timings were 63 ms (reports → data), 76 ms (data →
  research), 139 ms (research → reports), 37 ms (reports → report detail),
  84 ms (report → source research/history), and 52 ms (research → viewer).

Change:

- Added a reusable authenticated browser acceptance script that fails on any
  document request, changed document identity, lost runtime marker, console
  error, or server 5xx while traversing the product navigation path.
- Added an npm entry point for the acceptance script.
- The expected unauthenticated bootstrap 401 is cleared at the authenticated
  boundary; post-login failures remain strict.

Files:

- `apps/web/test/product-navigation-spa-acceptance.mjs`
- `apps/web/package.json`
- `docs/agent2/continuous_optimization/evidence/co-036-navigation-spa-2026-09-05.json`

Verification:

- `npm run test:product-navigation-spa`: PASS,
  `PRODUCT_NAVIGATION_SPA_ACCEPTANCE_PASS`.
- Six authenticated transitions: document requests `0` for every transition;
  `timeOriginPreserved=true`, `runtimeStatePreserved=true` for every transition.
- Browser console errors `0`; server 5xx responses `0`.
- Frontend typecheck: PASS.
- Touched diff check: PASS (existing line-ending notice only).

Result:

The current navigation architecture is now protected by a real browser
regression instead of relying on visual perception. Internal navigation is
demonstrably SPA-preserving and remains fast in the warmed same-stack runtime.

New findings:

- CO-006 is next: replace historical Job-name parsing with an explicit,
  server-authoritative ResearchTurn resolver.

## Improvement #7 — CO-006

Problem:

Project History already carried explicit `researchTurnId` relations, but the
legacy compatibility projection joined a historical Job to `research_turns`
using only `job_id`. A malformed cross-project relation could therefore expose
another project's ResearchTurn identity in an authorized project's history.

Change:

- Constrained the legacy `research_session_runs` → `research_turns` join by
  both Job ID and the requested project ID.
- Preserved the legacy run-only fallback when no same-project Turn relation
  exists; no frontend Job-name parsing or new identity model was introduced.
- Added a regression with a non-standard Job ID whose Turn belongs to another
  project; the result is now a safe `LEGACY_SESSION_RUN` projection with no
  leaked `researchTurnId`.

Files:

- `apps/api/mdi_api/routers/project_history.py`
- `tests/test_project_history_research_context.py`
- `docs/agent2/continuous_optimization/evidence/co-006-history-turn-scope-2026-09-05.json`

Verification:

- `pytest tests/test_project_history_research_context.py -q`: `5 passed`.
- `pytest tests/test_project_access.py -q`: `32 passed`.
- Touched Ruff: PASS.
- Touched diff check: PASS (existing line-ending notices only).

Result:

History resolution is explicitly relational, supports non-standard Job IDs,
and fails closed against cross-project Turn disclosure.

New findings:

- CO-007 is next: stress ContextManifest budgets and deterministic overflow.

## Improvement #8 — CO-007 (2026-09-05)

Problem:

The legacy `ContextSnapshot` compatibility projection in
`routers/agent2.py` emitted every item without applying the checked-in
operation budget. Historical replay could therefore exceed `input_budget`,
overflow the bounded item contract, and incorrectly report `compaction_state =
NONE`.

Change:

- Applied deterministic scientific-first priority ordering to compatibility
  items.
- Compacted non-critical overflow and recorded excluded item IDs.
- Preserved exact scientific object/version and Result items; critical
  scientific overflow now fails closed.
- Enforced the bounded `included_items` contract.

Files:

- `apps/api/mdi_api/routers/agent2.py`
- `tests/test_phase14r_context_manifest.py`
- `docs/agent2/continuous_optimization/evidence/co-007-context-manifest-compat-2026-09-05.json`

Verification:

- `pytest tests/test_phase14r_context_manifest.py -q`: `13 passed`.
- Touched Ruff: PASS.
- Touched diff check: PASS.

Result:

Legacy ContextManifest replay now obeys the same bounded, fail-closed budget
contract as fresh manifests without changing scientific authority or provider
identity semantics.

New findings:

- CO-008 is next: persist and verify context pin/unpin/use/compare controls
  across reload and re-login.

## Improvement #9 — CO-008 (2026-09-05)

Problem:

Session context pin/unpin behavior was implemented, but there was no regression
proving that a pinned scientific Result survives a repository reload (the
equivalent of browser refresh or re-login) and that unpinning is durable.

Change:

- Added a repository-lifecycle regression with a real persisted
  `ScientificResultSnapshot`.
- Pins the exact Result, closes the unit of work, reloads through a fresh
  repository session, unpins, and verifies the empty state through another
  fresh read.

Files:

- `tests/test_agent2_phase7_memory.py`
- `docs/agent2/continuous_optimization/evidence/co-008-context-pin-reload-2026-09-05.json`

Verification:

- `pytest tests/test_agent2_phase7_memory.py -q`: `10 passed`.
- Touched Ruff: PASS.
- Touched diff check: PASS.

Result:

Context controls now have a durable regression for cross-refresh persistence
without mutating scientific Result authority.

New findings:

- CO-009 is next: qualify recovery across network interruption, API restart and
  worker restart.

## Improvement #35 — CO-125 (2026-09-05)

Problem:

The secured Planner interpretation-evidence route authorized the source Job's
Project, but the persisted Agent2 interpretation/snapshot Project relation was
not carried into the response or compared with that Job. A tampered relation
could therefore expose a foreign evidence bundle through a guessed
interpretation identifier.

Change:

- Added bounded `projectId` provenance to Agent2 and legacy Planner evidence
  projections.
- The secured evidence route now compares evidence Project and Job Project and
  returns the same typed `404` for a mismatch.
- Added matching-project and cross-project deterministic regressions.

Files:

- `apps/api/mdi_api/routers/planner.py`
- `apps/api/mdi_api/routers/secured_planner.py`
- `tests/test_phase14r_authorization.py`
- `docs/agent2/continuous_optimization/evidence/co-125-planner-evidence-scope-2026-09-05.json`

Verification:

- `pytest -q tests/test_phase14r_authorization.py tests/test_phase8c_planner_read_api.py tests/test_phase10l4_api_persistence.py`: `26 passed`.
- `python -m compileall` on touched Python files: PASS.
- `git diff --check` on touched files: PASS.

Result:

Planner evidence now inherits both the authorized Job boundary and the
persisted interpretation Project relation. Cross-project relation mismatches
fail closed without becoming an identifier oracle, while valid same-project
evidence remains unchanged.

New findings:

- CO-029 remains OPEN for the remaining exact-route cross-project fuzzing
  campaign.
- CO-030 is next: browser session-expiry and re-auth recovery.

## Improvement #36 — CO-126 (2026-09-05)

Problem:

Agent2 Research's direct fetch helpers (`read`, `create`, and `dispatch`)
treated HTTP 401 as an ordinary request error. ProductShell's existing
session-expiry recovery therefore did not run for the primary Research
surface, making an expired session look like a scientific failure.

Change:

- Added one shared `notifySessionExpired` boundary to the Agent2 Research API
  transport.
- Applied it to read, create-turn, and dispatch requests.
- Preserved the original typed request rejection after the event.
- Added a parameterized regression covering all three paths.

Files:

- `apps/web/app/lib/agent2-research-api.ts`
- `apps/web/app/lib/agent2-research-api.test.ts`
- `docs/agent2/continuous_optimization/evidence/co-126-agent2-session-expiry-2026-09-05.json`

Verification:

- `npm run test -- --run app/lib/agent2-research-api.test.ts`: `7 passed`.
- `npm run typecheck`: PASS.
- `git diff --check` on touched files: PASS.

Result:

An expired Agent2 session now reaches the existing ProductShell login
recovery path consistently for reads, new Research submissions, and dispatch,
without changing scientific state or hiding the original request error.

New findings:

- CO-030 remains OPEN for browser-level expiry, draft preservation and
  re-auth recovery.
- CO-031 is next: role-matrix qualification for lifecycle/export/research
  controls.

## Improvement #32 — CO-026 (2026-09-05)

Problem:

When Redis/RQ was unavailable during stale Research recovery, the first queue
exception escaped `reconcile_turn` and could abort the recovery scan. Durable
PostgreSQL Turn/Job state remained recoverable, but the product had no typed,
retryable outcome.

Change:

- Added injectable queue adapters to `StaleResearchRecoveryService` for
  deterministic outage qualification while preserving settings-backed
  production queues.
- Wrapped orchestration, planning, execution, Result projection and
  interpretation republish boundaries.
- Queue failures now return `QUEUE_UNAVAILABLE` with a bounded retry message,
  preserve exact durable identities/statuses, and log only the error type.
- ScientificInterpretationReconciler now accepts an injected queue so recovery
  tests can simulate outage/reconnect without mutating shared Redis.

Files:

- `apps/api/mdi_api/research_agent/recovery.py`
- `apps/api/mdi_api/interpretation/reconciler.py`
- `tests/test_phase14r_recovery.py`
- `docs/agent2/continuous_optimization/evidence/co-026-queue-recovery-2026-09-05.json`

Verification:

- `pytest -q tests/test_phase14r_recovery.py tests/test_agent2_phase4_execution.py`:
  `15 passed`.
- `pytest -q tests/test_phase14r_operations.py tests/test_phase14r_retention_policy.py`:
  `14 passed, 1 skipped`.
- `compileall`: PASS.
- Touched diff check: PASS.

Result:

Redis loss/restart is now fail-closed at the recovery boundary: the system
does not fabricate completion, mutate durable scientific state, or abandon
other recovery candidates. Once the queue is available again, the same Turn
identity can be republished; existing ToolCall/Artifact/Result idempotency
guards prevent duplicate scientific outputs.

New findings:

- CO-027 is next: qualify provider 429/5xx/timeout behavior with typed retry and
  bounded user-visible recovery semantics.

## Improvement #33 — CO-027 (2026-09-05)

Problem:

DeepSeek 429, provider 5xx/network and timeout failures were classified into
safe typed errors, but the first transient response always terminated the
operation. A short provider-side disturbance therefore surfaced as a failed
Research/Report action even when an immediate retry would succeed.

Change:

- Added one bounded transient retry with a deterministic 250 ms backoff.
- Retry is restricted to `DEEPSEEK_RATE_LIMITED`,
  `DEEPSEEK_PROVIDER_FAILED` and `DEEPSEEK_TIMEOUT`.
- Authentication, configuration, model, purpose and invalid-response errors
  remain fail-fast and are never retried.
- Provider call audit records each attempt without prompt or credential
  content.

Files:

- `services/llm/mdi_llm/providers.py`
- `tests/test_phase10l5_deepseek_provider.py`
- `docs/agent2/continuous_optimization/evidence/co-027-provider-retry-2026-09-05.json`

Verification:

- Full DeepSeek provider regression: `67 passed`.
- Agent2 provider/timeout/failure regression: `4 passed, 41 deselected`.
- `compileall`: PASS.
- Touched diff check: PASS.

Result:

One transient Provider disturbance is absorbed without changing scientific
authority or creating a Result. Persistent transient failures still return
the existing typed error after the bounded retry, while non-retryable failures
remain immediate.

New findings:

- CO-028 is next: audit resource and concurrency limit enforcement plus typed
  product error semantics.

## Improvement #34 — CO-028 (2026-09-05)

Problem:

The legacy/direct `DatasetUploadRequest` path accepted an unbounded number of
files and inline content, while the newer upload-session contract enforced
`MAX_FILES_PER_UPLOAD`, `MAX_FILE_BYTES` and `MAX_TOTAL_UPLOAD_BYTES`. Filesystem
imports were copied before their size was checked, risking partial raw data.

Change:

- Reused the existing shared upload caps for direct inline requests.
- Added a preflight over filesystem paths and inline UTF-8 byte sizes before
  creating the dataset raw directory.
- Preserved the existing atomic publication and typed error codes:
  `UPLOAD_FILE_COUNT_CAP_EXCEEDED`, `UPLOAD_PER_FILE_BYTE_CAP_EXCEEDED` and
  `UPLOAD_TOTAL_BYTE_CAP_EXCEEDED`.

Files:

- `apps/api/mdi_api/phase2_runtime.py`
- `tests/test_phase2_product_loop.py`
- `docs/agent2/continuous_optimization/evidence/co-028-direct-upload-quota-2026-09-05.json`

Verification:

- Direct upload cap/preflight tests: `2 passed`.
- Full Phase 2 product loop: `9 passed`.
- Typed phonon and durable upload regressions: `15 passed`.
- `compileall`: PASS.
- Touched diff check: PASS.

Result:

All supported upload entry points now share the same bounded resource policy.
Oversized direct imports fail before raw bytes are published, reducing resource
exhaustion and partial-upload cleanup risk without changing scientific authority.

New findings:

- CO-029 is next: fuzz cross-project/cross-user authorization over exact Data,
  Turn, Result, Artifact, Version, Evidence, Report and History routes.

## Improvement #25 — CO-021 (2026-09-05)

Problem:

The Job-event sequence regression only covered one repository instance. A live
campaign also exposed that the shared fixture reused deterministic IDs across
processes, so a prior Job row could make Dataset cleanup fail with a foreign
key violation before the concurrency behavior was exercised.

Change:

- Added a PostgreSQL integration test with four independent
  `SqlAlchemyRepositoryBundle` instances and twelve concurrent writers.
- Made the integration seed project/dataset/job IDs unique per invocation,
  preventing cross-run fixture collisions without changing production locking.

Files:

- `tests/test_phase6_integration.py`
- `docs/agent2/continuous_optimization/evidence/co-021-job-event-concurrency-2026-09-05.json`

Verification:

- `pytest -q tests/test_phase6_integration.py -k "concurrent_seq"` with
  `postgresql+psycopg` and `MDI_RUN_INTEGRATION=1`: `2 passed, 17 deselected`.
- Both same-repository and cross-repository concurrency checks assert complete
  monotonic sequences with no gaps.

Result:

The advisory-lock path now has a real multi-bundle PostgreSQL regression, and
the test harness no longer fails before reaching the behavior under test.

New findings:

- CO-022 is next: queue idempotency, duplicate consumption, dead-letter and
  orphan Artifact/Result recovery tests.

## Improvement #26 — CO-022 (2026-09-05)

Problem:

Independent worker deliveries could race between the ToolCall idempotency
lookup and INSERT. The unique database constraint protected storage but the
losing worker surfaced an exception instead of converging on the committed
ToolCall.

Change:

- `SqlAlchemyToolCallRepository.save` now recovers a losing uniqueness
  `IntegrityError` by loading the committed matching ToolCall.
- Conflicting tool-step bindings and unrelated integrity failures remain
  fail-closed.

Files:

- `apps/api/mdi_api/repositories.py`
- `tests/test_phase6_integration.py`
- `docs/agent2/continuous_optimization/evidence/co-022-tool-call-idempotency-2026-09-05.json`

Verification:

- Real PostgreSQL with `postgresql+psycopg` and `MDI_RUN_INTEGRATION=1`:
  `tests/test_phase6_integration.py -k "concurrent_seq or duplicate_delivery"`
  → `3 passed, 17 deselected`.
- Twelve workers issued 48 duplicate saves through four independent repository
  bundles and produced one ToolCall row.

Result:

Duplicate queue delivery now converges at the ToolCall persistence boundary
without duplicating scientific execution authority.

New findings:

- CO-123 isolates the remaining Artifact select-then-insert race and bounded
  dead-letter/orphan recovery behavior.

## Improvement #27 — CO-123 (2026-09-05)

Problem:

Artifact persistence had the same cross-worker select-then-insert race as
ToolCall persistence. A duplicate delivery could surface a uniqueness error
even though the exact bytes were already committed.

Change:

- `SqlAlchemyArtifactRepository.save` now reloads the committed row after a
  losing uniqueness `IntegrityError`.
- Conflicting project/job/storage/checksum bindings and unrelated integrity
  failures remain fail-closed.
- Added a live four-bundle, 48-delivery PostgreSQL regression.

Files:

- `apps/api/mdi_api/repositories.py`
- `tests/test_phase6_integration.py`
- `docs/agent2/continuous_optimization/evidence/co-123-artifact-idempotency-2026-09-05.json`

Verification:

- `pytest -q tests/test_phase6_integration.py -k "concurrent_seq or duplicate_delivery"`
  with `postgresql+psycopg` and `MDI_RUN_INTEGRATION=1`: `4 passed, 17 deselected`.
- All duplicate saves return one exact Artifact identity and checksum.

Result:

Concurrent Artifact persistence now converges without duplicating scientific
provenance rows.

New findings:

- CO-124 isolates the remaining read-only dead-letter/orphan consistency
  scanner and fail-closed recovery qualification.

## Improvement #28 — CO-124 (2026-09-05)

Problem:

Operations diagnostics did not expose whether persisted ToolCall, Artifact,
ScientificResult, Report and ScientificObject lineage references were broken.
Dead-letter/orphan recovery could therefore lack a precise, non-mutating signal.

Change:

- Added a bounded `authorityConsistency` projection to the PostgreSQL
  operations snapshot.
- It checks ToolCall→Job, Artifact→Job/ToolCall, Result→Turn/Job,
  Report→Job/Result and current-version→ScientificObjectVersion references.
- The projection reports typed issue codes and at most 20 sample IDs per class,
  explicitly marks `readOnly=true`, and never repairs data.
- Added a same-stack integration regression.

Files:

- `apps/api/mdi_api/operations.py`
- `tests/test_phase14r_operations.py`
- `docs/agent2/continuous_optimization/evidence/co-124-authority-consistency-2026-09-05.json`

Verification:

- `MDI_RUN_INTEGRATION=1 pytest -q tests/test_phase14r_operations.py -k authority_consistency`
  → `2 passed, 9 deselected`.
- Same-stack snapshot reports PostgreSQL, Redis and MinIO healthy with
  `authorityConsistency.status=ok`, `issueCount=0`, `readOnly=true`.

Result:

Broken lineage is now observable through a fail-closed, read-only diagnostic
without changing scientific records.

New findings:

- CO-023 is next: repeated PostgreSQL connection-pool pressure qualification.

## Improvement #29 — CO-023 (2026-09-05)

Problem:

The pool lifecycle regression covered repeated SQLite engine creation but did
not qualify the real PostgreSQL pool under concurrent repeated transactions.

Change:

- Added an integration campaign with eight concurrent workers and 40
  repository transactions per worker.
- The test uses the configured `postgresql+psycopg` stack, checks process-scoped
  engine reuse, and queries `pg_stat_activity` for idle-in-transaction leaks.
- No pool limits or production connection architecture were changed.

Files:

- `tests/test_database_pool_lifecycle.py`
- `docs/agent2/continuous_optimization/evidence/co-023-postgres-pool-pressure-2026-09-05.json`

Verification:

- `MDI_RUN_INTEGRATION=1 pytest -q tests/test_database_pool_lifecycle.py`
  with PostgreSQL: `2 passed`.
- Engine identity is reused, checked-out connections return to zero, and
  idle-in-transaction is zero after the campaign.

Result:

The real PostgreSQL pool has a repeatable concurrent pressure guard against
connection leaks without changing runtime tuning.

New findings:

- CO-024 is next: read-only consistency scanner coverage for seeded broken
  relations and proof that it never mutates data.

## Improvement #30 — CO-024 (2026-09-05)

Problem:

The authority consistency projection had same-stack zero-issue evidence but no
deterministic regression proving exact orphan classification and non-mutation.

Change:

- Added an isolated database fixture containing one ToolCall with a missing
  Job reference.
- Asserted the scanner emits only `ORPHAN_TOOL_CALL_JOB`, includes the exact
  sample identity, and leaves all rows unchanged.

Files:

- `tests/test_phase14r_operations.py`
- `docs/agent2/continuous_optimization/evidence/co-024-consistency-nonmutation-2026-09-05.json`

Verification:

- `MDI_RUN_INTEGRATION=1 pytest -q tests/test_phase14r_operations.py -k authority_consistency`
  → `2 passed, 10 deselected`.
- Seeded row count is one before and after the scan.

Result:

The scanner is now protected as a precise read-only diagnostic rather than an
implicit repair path.

New findings:

- CO-025 is next: MinIO backup/restore/checksum and missing-object behavior.

## Improvement #31 — CO-025 (2026-09-05)

Problem:

MinIO integration covered basic put/get and signed URLs but did not prove
backup-copy integrity or behavior when the original object is missing.

Change:

- Added a live test using a unique temporary prefix.
- Writes a binary object, performs a server-side MinIO copy, verifies size and
  SHA-256, deletes the source, confirms typed absence, reads the backup, and
  cleans up both test keys.

Files:

- `tests/test_phase6_integration.py`
- `docs/agent2/continuous_optimization/evidence/co-025-minio-backup-restore-2026-09-05.json`

Verification:

- `MDI_RUN_INTEGRATION=1 pytest -q tests/test_phase6_integration.py -k "minio_backup_restore_checksum or minio_put_get_exists"`
  → `2 passed, 20 deselected`.
- Backup content and checksum remain exact after source deletion.

Result:

The real object-storage path now has evidence for backup/restore integrity and
safe missing-source handling without touching user data.

New findings:

- CO-026 is next: Redis loss/recovery semantics with PostgreSQL/MinIO as
  canonical authority.

## Improvement #24 — CO-020 (2026-09-05)

Problem:

Project deletion and account deactivation preserved scientific records in
practice, but the distinction between user workspace access and protected
scientific provenance was not returned as a structured account contract.

Change:

- Account deactivation now returns `provenanceRetained: true` and the shared
  protected retention policy.
- Project physical deletion remains server-gated to empty, zero-dependency
  projects.
- Logout keeps its minimal `{ok: true}` contract; deactivation alone carries
  retention semantics.
- Existing session revocation and `account.deactivated` audit behavior remain
  unchanged.

Verification:

- Account management regression: `8 passed`.
- Deactivation/logout subset: `2 passed`.
- Frontend typecheck, API compileall and touched diff check: PASS.

Result:

Workspace lifecycle and scientific provenance retention are now explicitly
separated in the account API without deleting scientific results, versions or
audit records.

New findings:

- CO-021 is next: stress concurrent Job event sequencing and locking for queue
  integrity.

## Improvement #23 — CO-019 (2026-09-05)

Problem:

Project/Dataset had dependency previews, and Object/Report had service-level
impact methods, but Research Session lacked an authorized database-derived
dependency endpoint. Lifecycle clients could not inspect the session's
messages, Turns, context snapshots and historical result/report bindings using
one authoritative contract.

Change:

- Added `GET /research-sessions/{session_id}/dependency-impact`.
- The endpoint scans real `session_id`/`research_session_id` columns, bounds the
  response to 64 dependency kinds, and enforces project authorization.
- Research Sessions are explicitly non-purgeable and return the shared
  `NOT_SUPPORTED_FOR_ENTITY` retention policy.
- Added frontend contract and project-scoped regression coverage.

Verification:

- Research Session lifecycle: `1 passed, 31 deselected`.
- Report lifecycle: `1 passed, 38 deselected`.
- Viewer/Object lifecycle: `28 passed`.
- Frontend typecheck: PASS.
- API compileall and touched diff check: PASS.
- Stranger access: HTTP `403`.

Result:

All major lifecycle entities now have a server-derived dependency boundary;
Research history cannot be treated as a deletable UI-only record.

New findings:

- CO-020 is next: verify project/account deletion semantics preserve protected
  scientific provenance and cannot orphan exact source references.

## Improvement #21 — CO-017 (2026-09-05)

Problem:

Trash retention behavior was described in the frontend but did not have one
reusable server-side policy contract shared by dependency previews and purge
enforcement. This left future expiry work at risk of drifting from scientific
provenance protection.

Change:

- Added `mdi_api.lifecycle_policy` with a versioned immutable retention policy.
- Automatic purge is explicitly disabled because no expiry worker is
  authorized in the current product.
- Manual purge is allowed only after server-derived dependency count is zero.
- Project/Dataset dependency previews and physical-delete paths now share the
  same decision function and expose the policy for auditability.
- Trash Center shows the server-derived policy during purge inspection.

Files:

- `apps/api/mdi_api/lifecycle_policy.py`
- `apps/api/mdi_api/routers/secured_runtime.py`
- `apps/web/app/lib/planner-api.ts`
- `apps/web/app/components/TrashCenterPage.tsx`
- `apps/web/app/components/TrashCenterPage.test.tsx`
- `tests/test_phase14r_retention_policy.py`
- `tests/test_project_access.py`
- `docs/agent2/continuous_optimization/evidence/co-017-retention-policy-2026-09-05.json`

Verification:

- Retention policy tests: `3 passed`.
- Lifecycle/dependency tests: `6 passed, 29 deselected`.
- Trash Center tests: `5 passed`.
- API module compileall: PASS.
- Frontend typecheck: PASS.
- Touched diff check: PASS.

Result:

Retention is now fail-closed and auditable: referenced scientific
provenance remains protected, automatic expiry cannot silently remove it, and
manual deletion uses one server-side rule.

New findings:

- CO-018 is next: complete cross-entity Trash/Purge policy coverage without
  changing scientific authority.

## Improvement #22 — CO-018 (2026-09-05)

Problem:

Project and Dataset containers supported dependency-checked permanent deletion,
while Research Session, ScientificObject and Scientific Report were protected
in practice but did not expose the same machine-readable lifecycle policy.
Clients could not reliably distinguish “zero dependencies required” from
“purge is not supported for this entity.”

Change:

- Extended the shared retention contract with explicit `manualPurge`.
- Project/Dataset return `SERVER_ZERO_DEPENDENCY_ONLY`.
- Research Session, ScientificObject and Scientific Report return
  `NOT_SUPPORTED_FOR_ENTITY`.
- Added the protected policy to Research Session read models and object/report
  dependency previews.
- Updated frontend contracts without adding a delete route or mutating
  scientific authorities.

Verification:

- Retention policy: `3 passed`.
- Research/dependency lifecycle: `2 passed, 33 deselected`.
- Report lifecycle: `1 passed, 38 deselected`.
- Viewer/object lifecycle: `28 passed`.
- Trash Center: `5 passed`.
- Frontend typecheck and touched diff check: PASS.

Result:

Every managed entity now advertises an explicit, fail-closed purge policy.
Workspace containers may be purged only after a zero-dependency server scan;
scientific and historical authorities remain non-purgeable.

New findings:

- CO-019 is next: compare dependency previews with authoritative database
  relations for every managed entity.

### 2026-09-05 Continuous optimization — trusted Artifact download bridge (CO-015)

- Research 与 Report 的 Figure/Table 入口原先只能打开受信 Artifact，缺少与
  Workbench 一致的下载动作；后端已有项目授权、大小与 SHA-256 校验，因此
  未新增 API 或科学执行路径。
- 新增 `ArtifactDownloadLink`，只接受同源
  `/api/planner/jobs/{job}/artifacts/{artifact}/content`，并在
  `ScientificPresentationBlocks`、`ScientificReportRoute` 的 Figure/Table
  与证据 Artifact 入口提供原生下载。
- 下载是只读原生 anchor 行为，Job/ToolCall/Artifact/ScientificResult 增量
  为 `0`；恶意或外部 URL fail-closed。
- `ArtifactDownloadLink`、ScientificPresentationBlocks、
  ScientificReportRoute focused 共 `32 passed`；typecheck 与 diff check
  通过。下一项为 CO-016：全 Viewer 家族持久化零重算回归。

### 2026-09-05 Continuous optimization — all registered Viewer zero-recompute guard (CO-016)

- 原有授权 Viewer API 的持久化只读计数断言只覆盖 Structure，其他已注册
  ScientificObject-backed family 缺少同等级保护。
- 将同一授权 API 回归参数化到 `11` 个当前注册类型：Dataset、Table、
  Structure、Trajectory、XRD experimental/theoretical、Electronic
  Band/DOS、Phonon Band/DOS、Volumetric。
- 每个类型都验证返回 renderer identity、`analysis_plans/jobs/tool_calls/
  artifacts/scientific_result_snapshots` 计数不变，并验证陌生项目仍 `403`
  且不泄露来源元数据。
- `pytest tests/test_agent2_phase9_viewers.py -q`: `28 passed`；Ruff 与
  diff check 通过。下一项为 CO-017：Retention/expiry 对受保护科学 provenance
  的审计策略。

### 2026-09-05 Continuous optimization — explicit Result-only Viewer contracts (CO-122)

- 审计确认 `analysis.rdf` 与 `reciprocal.brillouin_zone` 是 Result/Artifact
  renderer 合同，而不是当前 `ScientificObject` authority 注册的对象类型；
  混入对象级 Viewer registry 会制造错误的版本/归档预期。
- 从对象级 registry 移除两个 descriptor，新增只读
  `RESULT_ONLY_VIEWER_TYPES` 明确分类；不创建第二种科学身份，也不影响
  现有 RDF/BZ Artifact renderer。
- Registry/viewer focused `38 passed`；Ruff 与 diff check 通过。下一项仍为
  CO-017：Retention/expiry 对受保护 scientific provenance 的审计策略。

### 2026-09-05 Continuous optimization — presentation block fail-closed boundary (CO-034)

- 运行时未知 Presentation block 之前可能通过文本检查，被后续分组逻辑
  静默丢弃；这会掩盖不受支持内容，也无法证明没有执行未知组件。
- `isSafePresentationBlock` 现在先验证有界语义类型 allowlist，再检查危险
  HTML/script/URL 文本；`ScientificPresentationBlocks` 对被拒绝的 block
  显示有界状态，不暴露原始 payload。
- `scientific-presentation` 与 `ScientificPresentationBlocks` focused 共
  `23 passed`；typecheck 与 diff check 通过。下一项为 CO-017：
  Retention/expiry 对受保护 scientific provenance 的审计策略。

### 2026-09-05 Continuous optimization — canonical same-stack startup/readiness (CO-038)

- API、workers、frontend 原先需要分别启动，缺少统一且幂等的就绪门禁；这
  容易在服务重启后出现端口可用但运行时仍是错误 backend 的假健康。
- 新增 `scripts/phase14r_start_stack.ps1`：只启动缺失进程，不停止现有
  服务；等待 PostgreSQL/Redis/MinIO/API/frontend 端口，并直接探测
  `/health/runtime`，拒绝 SQLite、local artifact/cache 或 local worker。
- 当前 `-CheckOnly -FrontendPort 3023` 实测 PostgreSQL、Redis、MinIO、
  Redis worker 与 DeepSeek provider 全部 `ok/configured`。下一项仍为
  CO-017：Retention/expiry 对受保护 scientific provenance 的审计策略。

## Improvement #14 — CO-012 (2026-09-05)

Problem:

The Phase 14-R scientific surface matrix was manually maintained without a
regression against the live capability registry and trusted Capability Packs.
The initial audit found a real drift: `ml.regression_evaluation` was documented
under `core.data`, while the live pack builder places the `ml` domain in
`core.other`.

Change:

- Added `tests/test_phase14r_surface_coverage.py`.
- The regression derives active capability IDs, trusted-pack membership,
  ToolBinding IDs and Result projector IDs from the current registries.
- It requires exact matrix row parity, non-empty coverage cells, allowed
  statuses and registered Result projectors.
- Corrected the matrix pack cell for `ml.regression_evaluation` to
  `core.other`.

Files:

- `tests/test_phase14r_surface_coverage.py`
- `docs/agent2/phase14r/SCIENTIFIC_SURFACE_COVERAGE_MATRIX.md`
- `docs/agent2/continuous_optimization/evidence/co-012-surface-registry-drift-2026-09-05.json`

Verification:

- `pytest tests/test_phase14r_surface_coverage.py -q`: `1 passed`.
- Touched Ruff: PASS.
- Touched diff check: PASS.

Result:

Registry/Pack/documentation drift now fails fast, keeping the scientific
coverage matrix truthful without introducing a second capability authority.

New findings:

- CO-013 is next: expand exact historical/archived presentation evidence
  beyond the currently exercised capability families.

## Improvement #15 — CO-013 (2026-09-05)

Problem:

Historical exact-version Viewer qualification was concentrated in Dataset and
Structure examples. Other currently registered ScientificObject-backed Viewer
families did not have a deterministic regression proving that an old version
remains readable after a newer version becomes current and the object is
archived/restored.

Change:

- Added a parametrized regression for ten registered object-backed Viewer
  types, covering Dataset/Table, Structure, Trajectory, XRD, Electronic,
  Phonon and Volumetric families.
- Each case creates immutable v1/v2 state, makes v2 current, archives the
  object, projects exact v1, then restores and checks version/current identity.
- Descriptor-only `analysis.rdf` and `reciprocal.brillouin_zone` entries were
  explicitly excluded because they are not currently registered ScientificObject
  types; this surfaced new candidate CO-122 rather than silently treating them
  as object authority.

Files:

- `tests/test_agent2_phase9_viewers.py`
- `docs/agent2/continuous_optimization/evidence/co-013-historical-viewer-families-2026-09-05.json`

Verification:

- `pytest tests/test_agent2_phase9_viewers.py -q`: `18 passed`.
- Touched Ruff: PASS.
- Touched diff check: PASS.

Result:

All currently registered ScientificObject-backed Viewer families now have a
repeatable historical/archived exact-version guard; no Viewer navigation or
archive transition creates a replacement version.

New findings:

- CO-122: Viewer registry contains descriptor-only object types not present in
  the ScientificObject registry and needs an explicit bounded classification.
- CO-014 is next: typed temporary/permanent payload recovery UX.

## Improvement #16 — CO-014 (2026-09-05)

Problem:

The scientific Viewer used one unavailable-payload fallback for
`SOURCE_MISSING`, `METADATA_ONLY` and `INVALIDATED`. Permanent or policy-driven
states therefore displayed a misleading retry control.

Change:

- Added the bounded `viewerPayloadRecovery` state mapping.
- `SOURCE_MISSING` keeps retry plus exact source navigation.
- `METADATA_ONLY` explains the interactive preview limit and removes retry.
- `INVALIDATED` explains historical invalidation and removes retry.
- Added UI regressions for both non-retryable states.

Files:

- `apps/web/app/components/scientific-viewer/ScientificObjectViewer.tsx`
- `apps/web/app/components/scientific-viewer/ScientificObjectViewer.test.tsx`
- `docs/agent2/continuous_optimization/evidence/co-014-payload-recovery-states-2026-09-05.json`

Verification:

- `npm run test -- --run app/components/scientific-viewer/ScientificObjectViewer.test.tsx`: `3 passed`.
- `npm run typecheck`: PASS.
- Touched diff check: PASS.

Result:

Payload recovery controls now match the persisted scientific state; users are
not encouraged to retry an oversized or invalidated source, and exact-source
navigation remains available.

New findings:

- CO-015 is next: complete trusted Figure Artifact open/download integration.

## Improvement #12 — CO-009 (2026-09-05)

Problem:

Recovery already had same-stack operational evidence, but no focused database
regression protected the distinction between real product stale work and
retained qualification work.

Change:

- Added one stale product turn and one bounded qualification turn.
- Verified `list_stale` exposes the product candidate while retaining the
  qualification candidate separately, avoiding accidental republish.

Files:

- `tests/test_phase14r_recovery.py`
- `docs/agent2/continuous_optimization/evidence/co-009-recovery-partition-2026-09-05.json`

Verification:

- `pytest tests/test_phase14r_recovery.py -q`: `5 passed`.
- Touched Ruff: PASS.
- Touched diff check: PASS.

Result:

Stale recovery classification is now protected against cross-category
execution and duplicate qualification work.

New findings:

- CO-011 is next: evaluate grounded scientific discussion quality in XRD
  reports.

## Improvement #13 — CO-011 (2026-09-05)

Problem:

The report composer had grounded discussion/conclusion fallbacks, but XRD
communication quality was not protected by a focused regression.

Change:

- Added an XRD report case asserting discussion and conclusion preserve the
  authoritative matched-peak fact.
- Asserted limitations remain present and `ReportGroundingValidator` accepts
  the resulting report.

Files:

- `tests/test_agent2_phase8_reports.py`
- `docs/agent2/continuous_optimization/evidence/co-011-xrd-report-quality-2026-09-05.json`

Verification:

- `pytest tests/test_agent2_phase8_reports.py -q`: `35 passed, 4 skipped`.
- Touched Ruff: PASS.
- Touched diff check: PASS.

Result:

XRD reports now have a deterministic quality guard for useful scientific
discussion without rerunning or changing scientific computation.

New findings:

- CO-012 is next: derive a truthful supported-capability coverage matrix from
  the current Registry, Packs, Artifact contracts and Viewer registry.

## Improvement #11 — CO-010 (2026-09-05)

Problem:

Research evidence disclosures showed only a generic source label and value.
Users could not quickly inspect the persisted field, Artifact, ToolCall and
checksum chain behind a claim.

Change:

- Added a bounded `evidenceProvenanceSummary` helper.
- Research evidence rows now disclose field locator, Artifact ID, ToolCall ID
  and SHA-256 when available while preserving existing result navigation.
- Added a deterministic UI helper regression.

Files:

- `apps/web/app/components/ResearchPages.tsx`
- `apps/web/app/components/ResearchPages.test.tsx`
- `docs/agent2/continuous_optimization/evidence/co-010-evidence-provenance-ui-2026-09-05.json`

Verification:

- `npm run test -- --run app/components/ResearchPages.test.tsx`: `75 passed`.
- Frontend typecheck: PASS.
- Touched diff check: PASS.

Result:

Evidence is now more useful to researchers without becoming a second
provenance authority or exposing operational secrets.

New findings:

- CO-009 remains the next priority: recovery qualification across network,
  API and worker interruption.

## Improvement #10 — CO-121 (2026-09-05)

Problem:

`ScientificResultSnapshotNotFound` was not included in Agent2's typed HTTP
error mapping. A context-memory pin action referencing a missing Result could
therefore surface a generic 500 instead of a recoverable 404.

Change:

- Added the existing `ScientificResultSnapshotNotFound` domain error to the
  stable Agent2 resource-not-found mapping.
- Added an API regression asserting status `404` and the existing safe detail.

Files:

- `apps/api/mdi_api/routers/agent2.py`
- `tests/test_agent2_api.py`
- `docs/agent2/continuous_optimization/evidence/co-121-memory-reference-404-2026-09-05.json`

Verification:

- `pytest tests/test_agent2_api.py -q`: `27 passed`.
- Touched Ruff: PASS.
- Touched diff check: PASS.

Result:

Missing context-memory Result references now fail predictably without leaking
internal errors or changing scientific/session authorities.

New findings:

- CO-009 is next: qualify recovery across network interruption, API restart and
  worker restart.
## Improvement #37 — CO-127 (2026-09-05)

Problem:

The project export manifest is a read-only, project-authorized operation on
the server, but the Projects actions menu exposed it only to write-capable
roles. Shared viewer members therefore could not discover a safe provenance
export even though the API allowed it.

Change:

- Moved the export action into the read-access action set.
- Kept archive, trash, pin and metadata mutation actions write-gated.
- Added a viewer-role regression proving the authorized export path and the
  existing owner path.

Files:

- `apps/web/app/components/ProductPages.tsx`
- `apps/web/app/components/ProductPages.test.tsx`
- `docs/agent2/continuous_optimization/evidence/co-127-project-export-viewer-2026-09-05.json`

Verification:

- `npm run test -- --run app/components/ProductPages.test.tsx`: `46 passed`.
- Viewer export invokes `getProjectExportManifest` and starts a download.
- Viewer mutation affordances remain absent.

Result:

Read-only project members can now export the bounded provenance manifest
without gaining any lifecycle or metadata mutation authority.

New findings:

- CO-029 remains the next P0 authorization candidate: cross-project/cross-user
  fuzzing across exact Data/Turn/Result/Artifact/Version/Evidence/Report/History
  routes.
## Improvement #38 — CO-128 (2026-09-05)

Problem:

The retired `/analysis-requests` compatibility endpoint required an
authenticated caller but ignored a supplied `projectId`/`project_id`. A
cross-project caller could therefore receive an unconditional accepted
response, even though no scientific execution was started.

Change:

- Apply the existing `require_project_access(..., write=False)` boundary when
  a Project scope is present.
- Preserve the legacy unscoped, non-executing compatibility response.
- Add owner, viewer, stranger and unscoped regression coverage.

Files:

- `apps/api/mdi_api/routers/secured_runtime.py`
- `tests/test_project_access.py`
- `docs/agent2/continuous_optimization/evidence/co-128-legacy-analysis-scope-2026-09-05.json`

Verification:

- `pytest -q tests/test_project_access.py -k 'legacy_analysis_request_scope or project_export_manifest'`: `2 passed`.
- Owner and viewer scoped requests remain accepted.
- Stranger scoped request returns `403`.
- No Job/ToolCall/Artifact/ScientificResult is created by the compatibility
  stub.

Result:

The compatibility boundary now respects project isolation without breaking
older callers that never supplied a project scope.

New findings:

- CO-029 remains open for broader exact-route cross-project/cross-user fuzzing.
## Improvement #39 — CO-129 (2026-09-05)

Problem:

Missing direct-upload files raised an HTTP 400 whose detail contained the
absolute local path. That could expose the current user name, workspace layout,
or a sensitive filename.

Change:

- Added a dedicated `FileNotFoundError` branch in `_api_call`.
- Return stable `UPLOAD_SOURCE_NOT_FOUND` code and bounded message.
- Preserve the existing `ValueError` quota and validation responses.

Files:

- `apps/api/mdi_api/phase2_runtime.py`
- `tests/test_phase2_product_loop.py`
- `docs/agent2/continuous_optimization/evidence/co-129-upload-path-redaction-2026-09-05.json`

Verification:

- `pytest -q tests/test_phase2_product_loop.py -k 'api_call_redacts_missing_upload_paths or direct_upload_path_preflights'`: `2 passed`.
- Absolute path is absent from the HTTP detail.
- Existing upload size preflight remains green.

Result:

Upload source failures are now useful and retryable without leaking local
filesystem details.

New findings:

- CO-032 remains open for broader secret/path redaction scanning across logs,
  evidence and exports.

## Improvement #40 — CO-091 (2026-09-05)

Problem:

The scientific Viewer shell rendered an `article` without an accessible name
relationship. Screen readers could encounter the scientific region without a
reliable heading association.

Change:

- Generate a unique per-instance `scientific-viewer-title-*` id.
- Assign it to the Viewer `h2`.
- Bind the outer `article` with `aria-labelledby`.
- Add a regression assertion that the relationship points at the rendered
  heading and remains unique across repeated Viewer instances.

Files:

- `apps/web/app/components/scientific-viewer/ScientificViewerShell.tsx`
- `apps/web/app/components/scientific-viewer/ScientificViewerShell.test.tsx`
- `docs/agent2/continuous_optimization/evidence/co-091-viewer-accessible-name-2026-09-05.json`

Verification:

- `npm run test -- --run app/components/scientific-viewer/ScientificViewerShell.test.tsx`: `2 passed`.
- `npm run typecheck`: passed.
- `git diff --check` for touched files: passed; only normal CRLF conversion warnings.

Result:

Every Viewer region now has a deterministic accessible name tied to its
visible scientific title without changing scientific data, rendering authority
or navigation behavior.

New findings:

- CO-029 remains the highest-priority open authorization campaign.

## Improvement #44 — CO-092 (2026-09-05)

Problem:

Opening the Evidence inspector revealed new provenance content without moving
keyboard focus, and the trigger did not identify the controlled region.

Change:

- Add `aria-controls` from each evidence trigger to a stable inspector id.
- Make the inspector programmatically focusable.
- Move focus into the inspector after opening, including Finding direct-open
  actions.
- Restore focus to the original trigger after closing.

Files:

- `apps/web/app/components/ScientificPresentationBlocks.tsx`
- `apps/web/app/components/ScientificPresentationBlocks.test.tsx`
- `docs/agent2/continuous_optimization/evidence/co-092-evidence-focus-2026-09-05.json`

Verification:

- `npm run test -- --run app/components/ScientificPresentationBlocks.test.tsx`: `7 passed`.
- `npm run typecheck`: passed.
- `git diff --check` for touched files: passed; only normal CRLF conversion warnings.

Result:

Evidence inspection now has a predictable keyboard lifecycle and an explicit
ARIA relationship while continuing to use the existing bounded provenance
authority.

New findings:

- CO-029 remains the highest-priority open authorization campaign.

## Improvement #43 — CO-084 (2026-09-05)

Problem:

Finding cards displayed only an evidence count. A researcher had to scroll to
the page-wide evidence section and manually identify the matching evidence
entry before inspecting provenance.

Change:

- Match each finding to its existing `evidence_reference` block by stable
  evidence identity.
- Add a compact, keyboard-accessible `查看证据链` anchor with `aria-controls`.
- Open the existing evidence disclosure and bounded inspector for the exact
  interpretation/evidence identity; no new Result or execution path is added.

Files:

- `apps/web/app/components/ScientificPresentationBlocks.tsx`
- `apps/web/app/components/ScientificPresentationBlocks.test.tsx`
- `docs/agent2/continuous_optimization/evidence/co-084-finding-evidence-entry-2026-09-05.json`

Verification:

- `npm run test -- --run app/components/ScientificPresentationBlocks.test.tsx`: `7 passed`.
- `npm run typecheck`: passed.
- `git diff --check` for touched files: passed; only normal CRLF conversion warnings.
- `npm run lint -- --file ...` was attempted; the repository has no ESLint
  configuration and Next opened its interactive setup prompt, so no lint
  result was claimed.

Result:

Researchers can jump from a finding directly to its exact evidence chain while
the existing bounded provenance UI remains the single source of inspection.

New findings:

- CO-029 remains the highest-priority open authorization campaign.

## Improvement #42 — CO-076 (2026-09-05)

Problem:

Scientific Viewer metadata was silently capped at 16 fields. Researchers could
not tell whether omitted fields were unavailable or merely outside the compact
summary.

Change:

- Keep the first 16 fields as the bounded summary for dense workbench layouts.
- Add a native nested disclosure with the exact remaining field count.
- Render every additional loaded field inside that disclosure, preserving
  keyboard accessibility and avoiding a new component framework.
- Add an 18-field regression proving the disclosure opens and exposes the
  final fields.

Files:

- `apps/web/app/components/scientific-viewer/ScientificViewerShell.tsx`
- `apps/web/app/components/scientific-viewer/ScientificViewerShell.test.tsx`
- `docs/agent2/continuous_optimization/evidence/co-076-viewer-metadata-disclosure-2026-09-05.json`

Verification:

- `npm run test -- --run app/components/scientific-viewer/ScientificViewerShell.test.tsx`: `3 passed`.
- `npm run typecheck`: passed.
- `git diff --check` for touched files: passed; only normal CRLF conversion warnings.

Result:

Viewer metadata is now honest about truncation, compact by default, and fully
inspectable without changing scientific authority or loading unbounded data.

New findings:

- CO-029 remains the highest-priority open authorization campaign.

## Improvement #41 — CO-130 (2026-09-05)

Problem:

The direct Artifact download route had authorization code, but no focused
regression proved that a foreign-project request is rejected before the
storage/download operation runs.

Change:

- Added an owner/stranger secured-route test around
  `get_phase2_artifact_download_secured`.
- The test observes the downstream download function and requires zero calls
  for the denied request.
- The same test preserves the authorized owner's successful download path.

Files:

- `tests/test_project_access.py`
- `docs/agent2/continuous_optimization/evidence/co-130-artifact-download-cross-project-2026-09-05.json`

Verification:

- `pytest -q tests/test_project_access.py -k 'artifact_download_denies_foreign_project'`: `1 passed, 33 deselected`.

Result:

Direct Artifact downloads now have an explicit regression protecting the
cross-project fail-closed boundary and the authorized owner path.

New findings:

- CO-029 remains open for broader exact-route cross-project/cross-user
  fuzzing.

## Improvement #45 — CO-072 (2026-09-05)

Problem:

The generic Plotly viewer only listened to `window.resize`, so plots could
remain incorrectly sized after split-pane, tab, or responsive container
transitions that do not resize the browser window.

Change:

- Added a bounded `ResizeObserver` on the Plotly host element.
- Preserved the existing `window.resize` fallback.
- Disconnects the observer on unmount alongside Plotly cleanup.

Files:

- `apps/web/app/components/workspace/WorkspaceGenericPlot.tsx`
- `apps/web/app/components/workspace/WorkspaceGenericPlot.test.tsx`
- `docs/agent2/continuous_optimization/evidence/co-072-generic-plot-resize-observer-2026-09-05.json`

Verification:

- `npm test -- --run app/components/workspace/WorkspaceGenericPlot.test.tsx`:
  `9 passed`.
- `npm run typecheck`: passed.

Result:

Scientific plots now follow their real workspace/container geometry without
changing scientific data or initiating computation.

New findings:

- CO-029 remains the highest-priority open authorization campaign.

## Improvement #46 — CO-112 (2026-09-05)

Problem:

Permanent deletion confirmation used editable titles. Duplicate names made the
destructive action ambiguous even though the server-side entity identity was
distinct.

Change:

- Require the stable confirmation token `{kind}:{id}`.
- Explain retention and dependency protection in the confirmation dialog.
- Add a duplicate-title regression proving the wrong token cannot delete the
  selected entity.
- Preserve the existing server dependency-impact and authorization checks.

Files:

- `apps/web/app/components/TrashCenterPage.tsx`
- `apps/web/app/components/TrashCenterPage.test.tsx`
- `docs/agent2/continuous_optimization/evidence/co-112-trash-stable-confirmation-2026-09-05.json`

Verification:

- `npm test -- --run app/components/TrashCenterPage.test.tsx`: `6 passed`.
- `npm run typecheck`: passed.

Result:

Destructive confirmation is unambiguous for duplicate names while retaining
server-side provenance protection.

New findings:

- CO-029 remains the highest-priority open authorization campaign.

## Improvement #47 — CO-131 (2026-09-05)

Problem:

Authorization coverage for exact-id ResearchTurn and ScientificObject routes
was fragmented across individual tests, leaving no consolidated regression for
the read, mutate, query, viewer, and event boundaries.

Change:

- Added a TestClient matrix backed by persisted project-owned Turn/Object
  identities.
- Exercised turn detail, context, cancel, dispatch, progress, result,
  projection, interpretation, and events routes.
- Exercised object metadata, dependency impact, version listing/creation,
  exact-version read, Dataset query, Viewer, and relationship routes.
- Asserted every foreign-user request returns 403 without leaking object,
  version, or sentinel metadata.

Files:

- `tests/test_agent2_api.py`
- `docs/agent2/continuous_optimization/evidence/co-131-exact-route-auth-matrix-2026-09-05.json`

Verification:

- `pytest -q tests/test_agent2_api.py -k 'exact_turn_and_object_routes_fail_closed_for_foreign_user'`:
  `1 passed, 27 deselected`.

Result:

The covered exact-id Research and ScientificObject API surface now has a
single fail-closed regression before downstream work or metadata disclosure.

New findings:

- CO-029 remains open for the remaining Report/Artifact/Evidence/History
  route matrix.

## Improvement #71 — CO-114 (2026-09-05)

- 状态：已完成并验证；持续优化总任务继续处理中。
- 服务端依赖影响投影增加授权范围内的可选产品 `href`，覆盖 exact Data、
  Research Turn 和 Report；前端只渲染服务端显式目标，内部依赖保持纯文本。
- 修改文件：ScientificObject/Report/runtime service、对应 API 类型、
  Product/Report/Trash 页面及 6 组 focused tests。
- 验证：backend `37 passed, 4 historical skips`；frontend `66 passed`；
  typecheck 与 diff check PASS。
- 收益：用户可从破坏性操作预览直接核验引用来源，无需复制隐藏 ID，
  且不引入前端身份猜测或越权导航。

## Improvement #72 — CO-073 (2026-09-05)

- 状态：已完成并验证；持续优化总任务继续处理中。
- Viewer 场景 fallback 区分科学数据校验、WebGL 环境、动态 chunk 加载和
  renderer 初始化失败；初始化失败提供有界重试并保留源摘要/下载路径。
- 修改文件：`ViewerSceneRendererSurface.tsx`及 focused test。
- 验证：focused tests `25 passed`；typecheck PASS。
- 收益：不同根因不再被压成一个“Viewer 不可用”，恢复动作与科研含义一致。

## Improvement #73 — CO-053 (2026-09-05)

- 状态：已完成并验证；持续优化总任务继续处理中。
- 超过既有 15 分钟阈值且未更新的持久化 RUNNING 任务进入“需要关注”，
  显示真实运行状态和“打开并检查”，不伪装失败、不提供虚假重试。
- 修改文件：`TaskCenterPage.tsx`及 focused test。
- 验证：focused tests `7 passed`；typecheck 与 diff check PASS。
- 收益：停滞工作可被发现，同时不会篡改后端任务状态或错误创建新 lineage。

## Improvement #74 — CO-096 (2026-09-05)

- 状态：已完成并验证；持续优化总任务继续处理中。
- 编辑最后一条消息时立即清除旧 Turn/Result/问题缓存；权威原问题读取失败
  会禁用编辑和提交，并由提交前合同再次 fail closed。
- 修改文件：`ResearchPages.tsx`、`ResearchPages.test.tsx`。
- 验证：精确 focused `2 passed`；合并 Research/API 回归 `89 passed`；
  typecheck 与 diff check PASS。
- 收益：历史消息无法因加载失败被静默替换为普通新研究，旧 lineage 保持不变。

## Improvement #75 — CO-095 (2026-09-05)

- 状态：已完成并验证；持续优化总任务继续处理中。
- Continue 只把 Result 端点明确 404 解释为“无可复用结果”；503、权限或
  网络失败中止提交且不创建 Turn/伪失败消息。精确 snapshot 则作为显式
  reuse candidate 传递，并向用户区分复用候选与新科学执行。
- 修改文件：`agent2-research-api.ts`、`ResearchPages.tsx`及对应 tests。
- 验证：Research/API `89 passed`；typecheck 与 diff check PASS。
- 收益：继续研究不再把基础设施故障伪装成重新计算，科学复用语义可见且可审计。

## Improvement #76 — CO-077 (2026-09-05)

- 状态：已完成并验证；持续优化总任务继续处理中。
- Viewer 生命周期操作按权限、读取中、服务失败、归档、回收站和失效状态
  提供可访问禁用原因；PATCH 失败不再隐藏完整只读 Viewer。
- 修改文件：ScientificViewerShell/ObjectViewer 及 focused tests。
- 验证：focused tests `8 passed`；typecheck 与 diff check PASS。
- 收益：用户能理解管理动作不可用的准确原因，同时服务端权限和科学只读权威不变。

## Improvement #77 — CO-094 (2026-09-05)

- 状态：已完成并验证；持续优化总任务继续处理中。
- Retry 明确创建新 ResearchTurn，并用持久化 parent relation 验证来源 lineage；
  页面同时显示新/旧 Turn 身份并提供返回原失败运行的链接。
- 修改文件：ResearchPages、两个 Research route 及 focused tests。
- 验证：focused `3 passed`；完整 Research tests `85 passed`；typecheck/diff PASS。
- 收益：重试不会被误解为覆盖旧科学证据，失败与新运行均可追溯。

## Improvement #78 — CO-100 (2026-09-05)

- 状态：已完成并验证；持续优化总任务继续处理中。
- 运行中输入的下一条问题按 Project/Session/Turn 隔离到当前标签页
  sessionStorage；刷新恢复，并清楚说明草稿不会修改或重新提交当前科学任务。
- 修改文件：`ResearchPages.tsx`、其测试与 `globals.css`。
- 验证：完整 Research tests `85 passed`；typecheck 与 diff check PASS。
- 收益：长任务期间可安全预写后续问题，刷新不丢失且不会造成隐藏重算。

## Improvement #52 — CO-079 (2026-09-05)

- 状态：已完成并验证；持续优化总任务继续处理中。
- 结构 Viewer 现在保留并显示受信任的截断警告消息，在站点超过 256
  时明确呈现“当前显示前 256 / 总站点数”，并说明完整结构仍保留在源数据中。
- 修改文件：`viewerSceneRendererMapper.ts`、`ViewerSceneRendererSurface.tsx`、
  `ViewerSceneRendererSurface.test.tsx`及 CO-079 evidence。
- 验证：Viewer mapper 与 surface focused tests `43 passed`，typecheck 通过。
- 收益：有界三维预览不会被误解为完整结构，用户能直接核对当前显示范围
  与权威源数据的关系；未改变渲染上限或科学事实。
- 提交/CI：未提交、未推送；持续优化任务保持处理中。

## Improvement #53 — CO-082 (2026-09-05)

- 状态：已完成并验证；持续优化总任务继续处理中。
- 配位数直方图增加了与图形绑定的屏幕阅读器摘要，逐 bin 暴露配位数、
  位点数和占比；原有数值表继续作为可键盘访问的完整替代路径。
- 修改文件：`CoordinationHistogramPanel.tsx`、`CoordinationHistogramPanel.test.tsx`
  及 CO-082 evidence。
- 验证：focused tests `2 passed`，typecheck 通过。
- 收益：图表不再依赖 hover、颜色或视觉柱高来传达科学数值，移动和辅助技术
  用户可以读取同一权威 Artifact 数据；未引入新的科学计算。
- 提交/CI：未提交、未推送；持续优化任务保持处理中。

## Improvement #54 — CO-080 (2026-09-05)

- 状态：已完成并验证；持续优化总任务继续处理中。
- Dataset Explorer 增加每页 50 条的有界分页，显示当前范围、已投影索引
  总数与权威总样本数；通用 Scientific Table 同步显示当前页范围和总行数，
  首尾分页边界正确禁用，sample_id/sampleRef 身份保持稳定。
- 修改文件：`DatasetMaterialsExplorerPanel.tsx`、`WorkspaceArtifactGallery.tsx`
  及对应 focused tests/evidence。
- 验证：focused tests `17 passed`，typecheck 与 diff check 通过。
- 收益：大数据集不会把有界 payload 误显示成完整数据，同时用户可预测地
  浏览和定位行。
- 提交/CI：未提交、未推送；持续优化任务保持处理中。

## Improvement #55 — CO-085 (2026-09-05)

- 状态：已完成并验证；持续优化总任务继续处理中。
- Figure/Table Artifact 预览按 401/403/404/410、无效 JSON 和大小边界提供
  稳定且不泄露基础设施细节的状态；安全域错误码继续保留，不改变完整
  Artifact 入口或科学重算语义。
- 修改文件：`ScientificReportArtifactPreview.tsx`、对应测试及 CO-085 evidence。
- 验证：focused tests `12 passed`，typecheck 通过。
- 收益：报告用户能区分权限、缺失、过期、内容损坏和大小限制，不会把原始
  堆栈误认为科学结果失败。
- 提交/CI：未提交、未推送；持续优化任务保持处理中。

## Improvement #51 — CO-070 (2026-09-05)

Problem:

The bounded Plotly renderer sampled large traces, but its status only reported
the number of displayed points. Users could mistake the preview for complete
source data.

Change:

- Added `totalPointCount` to the validated plot projection.
- Status now reports displayed/original counts for sampled plots.
- Discloses the deterministic “保留端点与极值” sampling rule.

Files:

- `apps/web/app/components/workspace/WorkspaceGenericPlot.tsx`
- `apps/web/app/components/workspace/WorkspaceGenericPlot.test.tsx`
- `docs/agent2/continuous_optimization/evidence/co-070-plot-sampling-disclosure-2026-09-05.json`

Verification:

- `npm test -- --run app/components/workspace/WorkspaceGenericPlot.test.tsx`:
  `10 passed`.
- `npm run typecheck`: passed.

Result:

Scientific previews remain bounded while transparently distinguishing sampled
display data from the complete persisted series.

New findings:

- CO-029 remains open for the remaining Report/Artifact/Evidence/History
  route matrix.

## Improvement #50 — CO-078 (2026-09-05)

Problem:

The Viewer loaded companion Artifacts with `Promise.allSettled` but silently
discarded rejected items. A result with one readable Artifact and one missing,
unauthorized, or corrupt companion could look complete.

Change:

- Track rejected companion loads and expose a bounded partial-availability
  status while keeping the selected Artifact readable.
- Normalize invalid JSON/parser failures to `ARTIFACT_CONTENT_INVALID`.
- Show each failed Artifact label and code with an in-place retry action.
- Keep all existing read-only and no-recompute behavior intact.

Files:

- `apps/web/app/components/ScientificViewerAdapter.tsx`
- `apps/web/app/components/ScientificViewerAdapter.effect.test.tsx`
- `apps/web/app/globals.css`
- `docs/agent2/continuous_optimization/evidence/co-078-viewer-partial-artifact-state-2026-09-05.json`

Verification:

- `npm test -- --run app/components/ScientificViewerAdapter.effect.test.tsx`:
  `8 passed`.
- `npm run typecheck`: passed.

Result:

Partial Viewer availability is explicit, actionable, and scientifically honest
without hiding a usable primary result or exposing unstable parser details.

New findings:

- CO-029 remains open for the remaining Report/Artifact/Evidence/History
  route matrix.

## Improvement #49 — CO-089 (2026-09-05)

Problem:

Report table previews intentionally cap display at 24 rows and 8 columns, but
the old note did not say how much data was hidden.

Change:

- Added exact omitted row and column counts.
- Added an accessible native disclosure listing hidden column labels.
- Kept the existing authorized “open full Artifact” action as the complete
  data path; no duplicate table authority was introduced.

Files:

- `apps/web/app/components/ScientificReportArtifactPreview.tsx`
- `apps/web/app/components/ScientificReportArtifactPreview.test.tsx`
- `apps/web/app/globals.css`
- `docs/agent2/continuous_optimization/evidence/co-089-table-omission-disclosure-2026-09-05.json`

Verification:

- `npm test -- --run app/components/ScientificReportArtifactPreview.test.tsx`:
  `11 passed`.
- `npm run typecheck`: passed.

Result:

Bounded report tables now clearly distinguish hidden data from missing data and
retain a direct authorized path to the complete Artifact.

New findings:

- CO-029 remains open for the remaining Report/Artifact/Evidence/History
  route matrix.

## Improvement #48 — CO-087 (2026-09-05)

Problem:

Inline scientific Figure previews showed axis titles only. Researchers could
not tell the authoritative plotted range, tick labels, or units from the
compact report preview.

Change:

- Project bounded Plotly axis `range`, `tickvals`, `ticktext`, and `title`
  metadata from persisted Artifact payloads.
- Render an accessible visible axis summary and an SVG `<desc>`.
- Display `Artifact 未提供` when the source does not supply metadata instead
  of inferring units or ranges.
- Add responsive two-column axis metadata styling using existing product
  tokens.

Files:

- `apps/web/app/components/ScientificReportArtifactPreview.tsx`
- `apps/web/app/components/ScientificReportArtifactPreview.test.tsx`
- `apps/web/app/globals.css`
- `docs/agent2/continuous_optimization/evidence/co-087-figure-axis-fidelity-2026-09-05.json`

Verification:

- `npm test -- --run app/components/ScientificReportArtifactPreview.test.tsx`:
  `10 passed`.
- `npm run typecheck`: passed.

Result:

Report previews now expose authoritative scientific axis fidelity without
creating a second data source or triggering recomputation.

New findings:

- CO-029 remains open for the remaining Report/Artifact/Evidence/History
  route matrix.
