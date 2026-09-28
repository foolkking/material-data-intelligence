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
.\scripts\dev.ps1 restart
.\scripts\dev.ps1 stop
```

Default topology: PostgreSQL `55434`, Redis `6380`, MinIO `9000/9001`, FastAPI `8005`, Next.js `3023`, and one RQ worker listening to all active logical queues.

## Common checks

```powershell
.\.venv\Scripts\python.exe -m pytest
npm --prefix apps/web test
npm --prefix apps/web run typecheck
npm --prefix apps/web run build
```

## Repository structure

- `apps/` — FastAPI and Next.js applications
- `packages/` — schemas, adapters, parsers, artifact and Tool Registry code
- `services/` — workers and provider integration
- `tool_registry/` — executable tool manifests
- `tests/` — current behavior and integration tests
- `scripts/dev.ps1` — local project-owned service controller
- `config/` — current runtime/build configuration

Historical phase reports, qualification packages, runtime databases, and service logs are intentionally not part of the active repository.
