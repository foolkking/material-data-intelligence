# Material Data Intelligence

Material Data Intelligence (MDI) is a controlled materials-science workspace for durable datasets, validated scientific tools, asynchronous Research workflows, grounded interpretations, and reproducible artifacts.

See [`PROJECT_STATE.md`](PROJECT_STATE.md) for current scope and architecture.

## Prerequisites

- Windows PowerShell 7
- Python 3.11+
- Node.js and npm
- PostgreSQL 17 binaries
- Redis or Memurai binaries
- MinIO server binary

The binaries may be installed system-wide. MDI owns its instance configuration and data, not copies of those installations.

## Install

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e ".[test]"
npm --prefix apps/web ci
```

## Environment

Copy `.env.example` to the sibling local runtime `E:\1project\mdi-b0-5a1.local\local.env`. Set `MDI_LOCAL_ROOT` when a different external location is required. Runtime databases, object storage, logs, caches, PIDs, and secrets must remain outside Git.

## Development stack

```powershell
.\scripts\dev.ps1 start
.\scripts\dev.ps1 status
.\scripts\dev.ps1 restart -Scope app
.\scripts\dev.ps1 restart -Scope frontend
.\scripts\dev.ps1 restart
.\scripts\dev.ps1 stop
```

Default topology: PostgreSQL `55434`, Redis `6380`, MinIO `9000/9001`, FastAPI `8005`, Next.js `3023`, and one RQ worker listening to all active logical queues.

Use `restart -Scope app` to load API/Worker changes while retaining the frontend and storage services. It requires a verified idle Worker, requests normal Worker exit, then restarts the application processes and checks queue readiness. If a task begins during draining, the controller withdraws the drain after 30 seconds and leaves that work running. Use `restart -Scope frontend` to reload frontend dependencies without stopping API, Worker or storage. Plain `restart` still restarts the full stack. Worker startup uses a fresh registration name and checks the actual process, host, queue set and live RQ lease; a process that exists without a ready registration is not reported as healthy. Legacy Workers started before local-control support require one verified idle replacement before scoped restart is available.

With PostgreSQL, Redis and Research enabled, the API checks stalled research stages every minute. After the configured recovery window (15 minutes by default, minimum 5), requests that have not created a scientific Job receive a visible preparation timeout. Inactive scientific executions end with an interruption notice only after their database lease has also expired; pending cancellations then finish as canceled. Questions and saved files remain available. Live leases and completed work are preserved, and failed Jobs require an explicit retry before execution can be claimed again. `MDI_AGENT2_STARTUP_RECOVERY_ENABLED` controls both startup recovery and this background check.

## Common checks

```powershell
.\.venv\Scripts\python.exe -m pytest
npm --prefix apps/web test
npm --prefix apps/web run typecheck
npm --prefix apps/web run build
```

Pytest temporary artifacts use `<MDI_LOCAL_ROOT>/tmp/pytest` (default: the sibling `mdi-b0-5a1.local`), with numbered run directories and normal pytest retention. `MDI_PYTEST_CACHE_DIR` or `--basetemp` may name a strict child of that scratch directory; relative values are resolved there. Pytest’s reusable cache defaults to `../mdi-b0-5a1.local/tmp/pytest-cache`; use `-o cache_dir=<external-path>` when a different cache location is needed.


## Repository structure

- `apps/` — FastAPI and Next.js applications
- `packages/` — schemas, adapters, parsers, artifact and Tool Registry code
- `services/` — workers and provider integration
- `tool_registry/` — executable tool manifests
- `tests/` — current behavior and integration tests
- `scripts/dev.ps1` — local project-owned service controller
- `config/` — current runtime/build configuration

Historical phase reports, qualification packages, runtime databases, and service logs are intentionally not part of the active repository.
