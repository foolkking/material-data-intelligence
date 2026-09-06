# Phase 5 Runtime Infrastructure Runbook

## 1. Overview

This document covers the minimum operational steps to run the Phase 5 runtime infrastructure: PostgreSQL, Alembic migrations, Redis queue worker, and MinIO object storage.

## 2. Prerequisites

- Docker (or a compatible container runtime) for `postgres`, `redis`, and `minio`.
- Python 3.11+ with `uv` for dependency management.

## 3. Starting Infrastructure Services

### One-click start

```bash
docker compose up -d postgres redis minio
```

Verify all three services are healthy:

```bash
docker compose ps
```

Expected output shows `postgres`, `redis`, and `minio` with status "healthy".

### Stop services

```bash
docker compose down
```

### Reset data volumes

```bash
docker compose down -v
```

## 4. PostgreSQL Setup

### Retained Windows API rotation

When the same-stack API already owns port 8005, do not start another canonical
process or stop Python processes by name. First inspect the repository-scoped
rotation plan:

```powershell
.\scripts\phase14r_rotate_api.ps1
```

The default is dry-run. For a manifest-managed canonical instance, apply the
validated replacement with:

```powershell
.\scripts\phase14r_rotate_api.ps1 -Apply -Confirm:$false
```

The helper starts and validates a shadow on 8006, stops only the exact
revalidated 8005 Uvicorn child and its log runner, starts the new canonical,
validates the 3023 frontend proxy, then stops the shadow. A pre-manifest legacy
instance additionally requires its exact current listener PID through
`-ExpectedCanonicalPid`; never guess it. Success must leave exactly one 8005
listener and no 8006 listener. PostgreSQL, Redis, MinIO, workers and frontend
are intentionally outside the stop authority.

### Default credentials (from `.env` / `.env.example`)

```env
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=mdi
POSTGRES_USER=mdi
POSTGRES_PASSWORD=mdi-local-dev
```

### DATABASE_URL resolution

`ApiSettings.load_settings()` resolves the database URL in this order:

1. `DATABASE_URL` or `MDI_DATABASE_URL` if set explicitly.
2. Auto-built `postgresql+psycopg://` URL if `POSTGRES_HOST` is set.
3. Fallback: `sqlite:///./mdi_phase5.db` for local dev/tests (no Docker required).

### Test connection

```bash
docker compose exec postgres psql -U mdi -d mdi -c "SELECT 1 AS ok"
```

## 5. Alembic Migrations

### Run upgrade (PostgreSQL)

```bash
export DATABASE_URL="postgresql+psycopg://mdi:mdi-local-dev@localhost:5432/mdi"
python -m alembic -c apps/api/alembic.ini upgrade head
```

Expected: migration head `0008_phase_d_r1_namespace` applied.

### Run upgrade (SQLite, no Docker)

```bash
python -m alembic -c apps/api/alembic.ini upgrade head
# Uses the SQLite URL from alembic.ini default
```

### Verify tables (PostgreSQL)

```bash
docker compose exec postgres psql -U mdi -d mdi -c "\dt"
```

Tables expected for the durable Project/Workspace path include `users`,
`organizations`, `projects`, `datasets`, `data_profiles`, `jobs`, `job_events`,
`tool_calls`, `artifacts`, `visualization_recipes`, `reports`,
`scientific_workspaces`, `workspace_panels`, and
`workspace_layout_revisions`.

Creating or rolling back migrations is a maintainer operation and is not part
of the Initial Release reproduction procedure.

## 6. Repository Smoke Tests

### Run all unit tests (no Docker required)

```bash
python -m pytest -q
```

All Phase 2/3/4/5 unit tests pass with SQLite fallback.

### Run integration tests (Docker required)

```bash
docker compose up -d postgres
export MDI_RUN_INTEGRATION=1
export DATABASE_URL="postgresql+psycopg://mdi:mdi-local-dev@localhost:5432/mdi"
python scripts/mandatory_service_qualification.py run --junit integration.junit.xml --log integration.log
python scripts/mandatory_service_qualification.py validate --junit integration.junit.xml
```

If Docker/unavailable, integration tests skip with reason noted.

`config/mandatory-service-qualification.json` owns the mandatory
PostgreSQL/Redis/MinIO test paths, required test identities, minimum pass
count, and zero-skip/failure policy used by both this local command and CI.

## 7. Queue Worker

### Local mode (default, no Redis)

`LocalWorkerRuntime` (from Phase 2/3) executes jobs synchronously in-process. No Redis needed.

### Redis-backed queue mode

Set `MDI_QUEUE_BACKEND=redis`:

```bash
export MDI_QUEUE_BACKEND=redis
export REDIS_URL=redis://localhost:6379/0
```

The `QueueWorkerRuntime` uses RQ to enqueue jobs. Workers load the Job from
PostgreSQL repository, execute ToolCalls through Tool Registry + Adapter, and
write ToolCall/Artifact/JobEvent state back.

Start the canonical worker from the repository environment:

```bash
python -m mdi_workers.worker_entrypoint
```

The entrypoint uses RQ's process-isolated `Worker` on POSIX hosts. On Windows,
where `fork()` and `wait4()` are unavailable, it selects RQ's `SimpleWorker`
so queued jobs execute instead of terminating the worker process. Use one
worker process per queue on Windows because that worker executes jobs in the
worker process.

For persisted planner jobs, the worker must load `job.plan_id`, fetch the
matching `analysis_plans` record, reconstruct the `AnalysisPlan`, and execute
the persisted `steps`. Caller-provided in-memory plans are only a dev/test
fallback when a job has no persisted plan.

## 8. MinIO / S3 Live Client

### Configuration

```env
MINIO_ENDPOINT=http://localhost:9000
MINIO_ACCESS_KEY=mdi-local
MINIO_SECRET_KEY=mdi-local-dev
MINIO_BUCKET=mdi-artifacts
MINIO_SECURE=false
```

### Available operations

- `put_bytes`, `put_text`, `put_json`
- `get_bytes`, `get_text`, `get_json`
- `exists`
- `signed_url` (real presigned URLs via boto3)

Artifact metadata stays in PostgreSQL; binary objects live in MinIO/S3.

### MinIO Console

Open http://localhost:9001 and log in with `mdi-local` / configured secret key.

## 9. Local Fallback Strategy

When infrastructure services are unavailable:

| Service | Fallback |
|---------|----------|
| PostgreSQL | SQLite (`mdi_phase5.db`) |
| Redis | In-process synchronous execution |
| MinIO | `LocalFileArtifactStorage` under `artifacts/` |

This ensures `python -m pytest -q` always works without Docker.

## 10. Quick Reference

| Task | Command |
|------|---------|
| Start infra | `docker compose up -d postgres redis minio` |
| Check infra | `docker compose ps` |
| Alembic upgrade (PG) | `python -m alembic -c apps/api/alembic.ini upgrade head` |
| Start queue worker | `python -m mdi_workers.worker_entrypoint` |
| Run unit tests | `python -m pytest -q` |
| Run integration tests | `MDI_RUN_INTEGRATION=1 python -m pytest -q -m integration` |
| Run Phase 8B persisted-plan integration | `MDI_RUN_INTEGRATION=1 python -m pytest tests/test_phase8b_persisted_plan_queue.py -q -m integration` |
| Downgrade | `python -m alembic -c apps/api/alembic.ini downgrade -1` |
| MinIO console | http://localhost:9001 |
| Safe service stop | `docker compose down` |

Do not remove named volumes or recursively clear buckets when user or
production data may be present. Reproduction uses isolated test identities.

## Operations Alert Response

The platform-admin operations surface and
`scripts/phase14r_operations_snapshot.py` use the same typed alert and
runbook identities. Always collect the read-only snapshot before changing a
worker or queue:

```bash
python scripts/phase14r_operations_snapshot.py \
  --same-stack \
  --fail-on-attention \
  --compact
```

| Runbook ID | Signals | Safe first response |
|---|---|---|
| `OPS-RUNBOOK-QUEUE-BACKLOG` | `OPS_QUEUE_DEPTH_EXCEEDED` | Inspect `queues.items` to identify the accumulating queue and verify that its canonical worker is consuming. Do not clear the queue or retry every Job as a first response. |
| `OPS-RUNBOOK-STALE-JOBS` | `OPS_STALE_JOBS` | Inspect Job age and its owning ResearchTurn. Use the existing bounded recovery command only after confirming the persisted state; never delete the Job, Artifact, or Result rows manually. |
| `OPS-RUNBOOK-WORKER-HEALTH` | `OPS_WORKER_COUNT_BELOW_MINIMUM`, `OPS_WORKER_HEALTH_DEGRADED` | Check canonical queue coverage, RQ state and heartbeat freshness. Start or replace only the missing/degraded role, avoiding duplicate consumers. |

Re-run the snapshot after the bounded response. An alert is closed only when
the authoritative signal returns within its threshold; hiding the alert in
the UI does not change queue, Job, or worker state.

## 11. Phase 6 Integration Tests

### Overview

Phase 6 adds 18 service-backed integration smoke tests that verify PostgreSQL,
Redis, and MinIO live interactions. All integration tests are gated behind
`@pytest.mark.integration` and skip cleanly when services are not available.

### Required environment variables

```env
MDI_RUN_INTEGRATION=1
DATABASE_URL=postgresql+psycopg://mdi:mdi-local-dev@localhost:5432/mdi
REDIS_URL=redis://localhost:6379/0
MINIO_ENDPOINT=http://localhost:9000
MINIO_ACCESS_KEY=mdi-local
MINIO_SECRET_KEY=mdi-local-dev
MINIO_BUCKET=mdi-artifacts
MINIO_SECURE=false
```

### Running integration tests

```bash
# 1. Start services
docker compose up -d postgres redis minio

# 2. Wait for healthy
docker compose ps

# 3. Run Alembic migration (optional — tests create tables via metadata.create_all)
export DATABASE_URL="postgresql+psycopg://mdi:mdi-local-dev@localhost:5432/mdi"
python -m alembic -c apps/api/alembic.ini upgrade head

# 4. Run all integration tests
export MDI_RUN_INTEGRATION=1
python -m pytest -q -m integration

# 5. Run a specific integration file
python -m pytest tests/test_phase6_integration.py -q -m integration
```

### Test categories

| Category | Tests | What it covers |
|----------|-------|----------------|
| Docker compose | 1 | PostgreSQL, Redis, MinIO reachable |
| Alembic live | 1 | Tables created in PostgreSQL |
| Repository live | 6 | Project, Dataset, Job, ToolCall, Artifact, Recipe, Report CRUD + rollback + status transitions |
| JobEvent seq | 3 | Monotonic seq, advisory lock, concurrent seq |
| Redis queue | 2 | Enqueue/dequeue, worker runtime with live PostgreSQL |
| Queue retry idempotency | 2 | Duplicate job, crash+retry |
| MinIO live | 2 | put/get/exists/signed-url, signed URL validation |
| Service-backed loop | 1 | End-to-end: PG repos + queue + storage + adapter |

### Unit tests always work without Docker

```bash
python -m pytest -q                    # 68 passed, 19 skipped
python -m pytest -q -m "not integration"  # Only unit tests
```

## 11A. Phase 8B Persisted Plan Queue Integration

Phase 8B adds one service-backed integration test to the Phase 6 suite. It
requires the same PostgreSQL, Redis, and MinIO environment variables as above.

The acceptance chain is:

```text
validated AnalysisPlan
  -> analysis_plans row with plan_hash
  -> jobs.plan_id
  -> Redis enqueue(job_id)
  -> QueueWorkerRuntime.handle_job(job_id)
  -> load persisted AnalysisPlan
  -> Tool Registry + Adapter
  -> exactly 1 ToolCall
  -> MinIO Artifact + PostgreSQL JobEvent + completed Job
```

Run it directly with:

```bash
MDI_RUN_INTEGRATION=1 python -m pytest tests/test_phase8b_persisted_plan_queue.py -q -m integration
```

CI runs it together with the Phase 6 integration file and fails if any
integration test skips. The expected CI service-backed minimum is now 19
passed tests: 18 Phase 6 tests plus 1 Phase 8B persisted-plan queue test.

## 12. Troubleshooting

### Database connection refused

```bash
# Verify PostgreSQL is running and healthy
docker compose ps postgres
docker compose logs postgres

# Check if DATABASE_URL is correct
docker compose exec postgres psql -U mdi -d mdi -c "SELECT 1 AS ok"
```

### Alembic migration failed

```bash
# Confirm service health, then re-run the idempotent upgrade.
docker compose ps postgres
export DATABASE_URL="postgresql+psycopg://mdi:mdi-local-dev@localhost:5432/mdi"
python -m alembic -c apps/api/alembic.ini upgrade head
```

### Redis connection refused

```bash
docker compose ps redis
docker compose logs redis
docker compose exec redis redis-cli ping
```

### MinIO bucket not found

```bash
# Check MinIO status
docker compose ps minio
docker compose logs minio

# Create bucket via console at http://localhost:9001
# Or via mc client:
docker compose exec minio mc mb local/mdi-artifacts
```

### MinIO capacity scan is incomplete

`OPS_MINIO_USAGE_SCAN_INCOMPLETE` means the read-only diagnostic reached its
bounded object limit or could not continue pagination. Reported bytes and
objects are lower bounds, and utilization is intentionally unknown. Do not
delete scientific Artifacts to clear this warning. Verify storage-side
aggregate metrics or increase only the bounded observation capacity, then run:

```bash
python scripts/phase14r_operations_snapshot.py --same-stack --fail-on-attention --compact
```

### Signed URL invalid

- Ensure `MINIO_ENDPOINT` uses `http://localhost:9000` (not `http://minio:9000`) for local testing.
- Check `MINIO_SECURE=false` when not using TLS.
- Presigned URLs are generated by boto3 and valid for the configured expiration period.
