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
| Run integration tests | `python -m pytest -q -m integration` |
| Downgrade | `python -m alembic -c apps/api/alembic.ini downgrade -1` |
| MinIO console | http://localhost:9001 |
