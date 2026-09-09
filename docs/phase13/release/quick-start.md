# Installation and Quick Start

## Requirements

- Python 3.11 or newer and `uv`.
- Node.js 20 and npm using the checked-in `apps/web/package-lock.json`.
- The checked-in `uv.lock`.
- PostgreSQL, Redis, and MinIO. The retained Windows qualification topology is
  distinct from the default-port Docker Compose topology.

## Retained Windows same-stack start

The canonical retained stack uses:

- PostgreSQL `127.0.0.1:55434/mdi`;
- Redis `127.0.0.1:6379/13`;
- MinIO `http://127.0.0.1:9000`;
- API `http://127.0.0.1:8005`;
- production frontend `http://127.0.0.1:3023`.

Prepare a fresh checkout with the locked dependencies and production frontend
artifact:

```powershell
uv sync --frozen --extra test
npm --prefix apps/web ci
$env:MDI_NEXT_DIST_DIR = ".cache/next-production"
npm --prefix apps/web run build
uv run python -m alembic -c apps/api/alembic.ini upgrade head
powershell.exe -NoProfile -ExecutionPolicy Bypass -File scripts/phase14r_start_stack.ps1 -FrontendPort 3023
```

The launcher performs a disk preflight, starts only missing processes, and
never replaces an existing listener. It preserves the retained service data
and checks that API, worker, and artifact backends are PostgreSQL, Redis, and
MinIO rather than local substitutes.

Verify readiness and the dynamic migration head:

```powershell
uv run python -m alembic -c apps/api/alembic.ini current
uv run python -m alembic -c apps/api/alembic.ini heads
powershell.exe -NoProfile -ExecutionPolicy Bypass -File scripts/phase14r_start_stack.ps1 -FrontendPort 3023 -CheckOnly
```

The API runtime check is `http://127.0.0.1:8005/health/runtime`.

The deterministic/replay workflow does not require a live model. Optional
provider credentials must be supplied only to the server-side managed process
environment. Never put a real key in Git, frontend environment variables,
request JSON, browser storage, logs, or qualification evidence.

## Default-port Docker Compose topology

Docker Compose remains a separate, isolated reproduction option on its
declared default ports. Do not mix its database, Redis namespace, or MinIO
bucket with the retained Windows topology. Use qualification-owned identities
and follow `docs/16_RUNTIME_INFRASTRUCTURE_RUNBOOK.md`.

## Verify

```powershell
uv run python -m pytest -q -m "not integration"
npm --prefix apps/web test
npm --prefix apps/web run typecheck
npm --prefix apps/web run build
uv lock --check
```

The release migration check compares `alembic.ini current` with
`alembic.ini heads`; the repository must have one head and the live database
must be at that head. Do not pin a historical revision in the quick start.

## Safe process and service handling

The start command is idempotent and intentionally does not stop retained
services. If an obsolete repository-owned frontend listener must be reviewed,
first run the scoped dry-run:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File scripts/phase14r_rotate_frontend.ps1 -CurrentPort 3023
```

Only after inspecting that output may an operator use the separately
authorized apply form:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File scripts/phase14r_rotate_frontend.ps1 -CurrentPort 3023 -Apply -Confirm
```

That operation must leave PostgreSQL, Redis, MinIO, API, workers, and all
runtime/user data intact. Never use `docker compose down -v` against retained,
user-owned, or production-like service data.
