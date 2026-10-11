# Material Data Intelligence

Material Data Intelligence (MDI) is a controlled materials-science workspace for durable datasets, validated scientific tools, asynchronous Research workflows, grounded interpretations, and reproducible reports.

## Project documents

- [PROJECT_STATE.md](PROJECT_STATE.md): current architecture, runtime and data ownership.
- [CAPABILITIES.md](CAPABILITIES.md): current capabilities and evidence.
- [REMAINING_WORK.md](REMAINING_WORK.md): numbered handoff and unfinished goal.
- [AGENTS.md](AGENTS.md): engineering and data-safety rules.

## Prerequisites

- Windows PowerShell 7
- Python 3.11+
- Node.js and npm
- PostgreSQL 17 binaries
- Redis or Memurai binaries
- MinIO server binary

The binaries may be installed system-wide. MDI owns its instance configuration and data, not copies of those installations.

## Install

    python -m venv .venv
    .\.venv\Scripts\python.exe -m pip install -e ".[test]"
    npm --prefix apps/web ci

## Environment and data ownership

Copy .env.example to the sibling project runtime E:\1project\mdi-b0-5a1.local\local.env; keep secrets and service data outside Git. Set MDI_LOCAL_ROOT when using a different external location. The machine-specific temporary root is C:\Users\86182\Desktop\wkkk. See PROJECT_STATE.md for the complete path table and current port override.

## Development stack

    .\scripts\dev.ps1 start
    .\scripts\dev.ps1 status
    .\scripts\dev.ps1 restart -Scope app
    .\scripts\dev.ps1 restart -Scope frontend
    .\scripts\dev.ps1 restart
    .\scripts\dev.ps1 stop

restart -Scope app reloads API and Worker while retaining frontend and storage. Use the full restart only when the complete stack is intentionally being restarted. Keep the user's browser and project services running after work rounds.

With PostgreSQL, Redis and Research enabled, the API checks stalled stages once per minute. The default recovery window is 15 minutes (minimum 5); execution is only expired after its database lease is also expired. Questions and saved files remain available, and failed Jobs require an explicit retry. MDI_AGENT2_STARTUP_RECOVERY_ENABLED controls startup and periodic recovery.

Default topology is PostgreSQL 55434, Redis 6380, MinIO 9000/9001, FastAPI 8005, Next.js 3023, and one Worker with six logical queues. This host uses PostgreSQL 15434 through its external local.env override.

## Checks

    .\.venv\Scripts\python.exe -m pytest -m "not integration and not live_llm and not llm_integration"
    npm --prefix apps/web test
    npm --prefix apps/web run typecheck
    npm --prefix apps/web run build

Tests do not load the real local.env unless explicitly marked for an integration/live flow. Pytest scratch is outside the repository under the configured temporary root or sibling local runtime; explicit basetemp values must be strict children of that scratch area.

## Repository layout

- apps/api — FastAPI application and Research orchestration
- apps/web — Next.js product shell and scientific viewers
- packages — schemas, registries, adapters, parsers and artifacts
- services/workers — RQ execution, projection, interpretation and report workers
- services/llm — bounded provider integration
- tool_registry — executable tool manifests
- tests — behavior and integration contracts
- scripts/dev.ps1 — project-owned local service controller

Runtime databases, object storage, logs, caches, PIDs, screenshots and temporary exports are intentionally outside this repository.
