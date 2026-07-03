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

Expected: migration `0001_phase4_persistence_baseline` applied; all Phase 4 tables created.

### Run upgrade (SQLite, no Docker)

```bash
python -m alembic -c apps/api/alembic.ini upgrade head
# Uses the SQLite URL from alembic.ini default
```

### Verify tables (PostgreSQL)

```bash
docker compose exec postgres psql -U mdi -d mdi -c "\dt"
```

Tables expected: `projects`, `datasets`, `data_profiles`, `jobs`, `job_events`, `tool_calls`, `artifacts`, `visualization_recipes`, `reports`.

### Create a new migration

```bash
python -m alembic -c apps/api/alembic.ini revision --autogenerate -m "description"
```

### Rollback

```bash
python -m alembic -c apps/api/alembic.ini downgrade -1
```

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
python -m pytest -q -m integration
```

If Docker/unavailable, integration tests skip with reason noted.

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
| Run unit tests | `python -m pytest -q` |
| Run integration tests | `MDI_RUN_INTEGRATION=1 python -m pytest -q -m integration` |
| Run Phase 8B persisted-plan integration | `MDI_RUN_INTEGRATION=1 python -m pytest tests/test_phase8b_persisted_plan_queue.py -q -m integration` |
| Downgrade | `python -m alembic -c apps/api/alembic.ini downgrade -1` |
| MinIO console | http://localhost:9001 |
| Reset PostgreSQL | `docker compose down -v postgres && docker compose up -d postgres` |
| Clean MinIO bucket | `docker compose exec minio mc rm --recursive local/mdi-artifacts/` |

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
# Reset and re-migrate
docker compose down -v postgres
docker compose up -d postgres
# Wait for healthy
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

### Signed URL invalid

- Ensure `MINIO_ENDPOINT` uses `http://localhost:9000` (not `http://minio:9000`) for local testing.
- Check `MINIO_SECURE=false` when not using TLS.
- Presigned URLs are generated by boto3 and valid for the configured expiration period.
