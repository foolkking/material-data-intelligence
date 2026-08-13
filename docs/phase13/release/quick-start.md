# Installation and Quick Start

## Requirements

- Python 3.11 or newer and `uv`.
- Node.js 20 was verified for this package; `apps/web/package.json` does not declare a stricter `engines` constraint. npm uses the checked-in package lock.
- Docker Compose for PostgreSQL 16, Redis 7, and MinIO.

## Fresh checkout

```powershell
uv sync --frozen --extra test
npm --prefix apps/web ci
Copy-Item .env.example .env
docker compose up -d postgres redis minio
docker compose ps
$env:DATABASE_URL = "postgresql+psycopg://mdi:<LOCAL_POSTGRES_PASSWORD>@localhost:5432/mdi"
uv run python -m alembic -c apps/api/alembic.ini upgrade head
uv run uvicorn mdi_api.main:app --app-dir apps/api --host 127.0.0.1 --port 8000
```

In another PowerShell:

```powershell
npm --prefix apps/web run dev
```

Open `http://localhost:3000`. API health is `http://localhost:8000/health`.

Linux uses the same commands except `cp .env.example .env` and `export DATABASE_URL=...`.

## Verify

```powershell
uv run python -m pytest -q -m "not integration"
npm --prefix apps/web test
npm --prefix apps/web run typecheck
npm --prefix apps/web run build
uv lock --check
```

Migration head must be `0007_phase10m1_workspace_domain`.

## Safe shutdown

`docker compose down` stops services without deleting named volumes. Do not use `down -v` against user or production data. Phase 13 reproducibility uses isolated test identities and requires no preexisting PostgreSQL rows, MinIO objects, or Redis messages.
