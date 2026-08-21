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

The default deterministic/replay workflow does not need a live model. To
enable the optional server-side DeepSeek Planner and strict Interpretation
path, set the variables in the API process environment before starting
Uvicorn; do not put a real key in Git, frontend env, request JSON, or browser
storage:

```powershell
$env:DEEPSEEK_KEY = "<DEEPSEEK_KEY>"
$env:MDI_LLM_PROVIDER = "deepseek"
$env:DEEPSEEK_MODEL = "deepseek-v4-flash"
uv run uvicorn mdi_api.main:app --app-dir apps/api --host 127.0.0.1 --port 8000
```

The API reports only redacted readiness through `/planner/providers/status`.
The browser-facing model settings page can run a bounded connection test, but
never accepts or stores the key. The allowlisted model names are owned by
`services/llm/mdi_llm/providers.py`.

In another PowerShell:

```powershell
npm --prefix apps/web run dev
```

Open `http://localhost:3000`. API health is `http://localhost:8000/health`.

Linux uses the same commands except `cp .env.example .env`, `export DATABASE_URL=...`,
and, for the optional live provider, `export MDI_LLM_PROVIDER=deepseek`,
`export DEEPSEEK_KEY=...` and
`export DEEPSEEK_MODEL=deepseek-v4-flash` before launching Uvicorn.

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
