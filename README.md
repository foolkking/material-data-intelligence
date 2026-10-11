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
- Node.js 22 and npm (the CI baseline)
- PostgreSQL 17 binaries
- Redis or Memurai binaries
- MinIO server binary

The binaries may be installed system-wide. MDI owns its instance configuration and data, not copies of those installations.

## Install

Before project commands on this workstation, set the external scratch root in the current PowerShell process:

    $env:MDI_TEMP_ROOT='C:\Users\86182\Desktop\wkkk'
    $env:TEMP=$env:MDI_TEMP_ROOT
    $env:TMP=$env:MDI_TEMP_ROOT
    $env:TMPDIR=$env:MDI_TEMP_ROOT

Use a dedicated child directory for each task. On other machines choose an existing writable temporary root outside the repository. This setting does not move persistent data.

    python -m venv .venv
    .\.venv\Scripts\python.exe -m pip install -e ".[test]"
    npm --prefix apps/web ci

## Environment and data ownership

Copy .env.example to the sibling project runtime E:\1project\mdi-b0-5a1.local\local.env; keep secrets and service data outside Git. Set MDI_LOCAL_ROOT when using a different external location. The machine-specific temporary root is C:\Users\86182\Desktop\wkkk. See PROJECT_STATE.md for the complete path table and current port override.

Durable model connections require a stable Fernet key in `MDI_PROVIDER_ENCRYPTION_KEY` in the external environment. Preserve this key securely with the database recovery configuration; replacing it prevents existing encrypted connection credentials from being read. API and Worker must use the same key. The local controller loads this environment; code-only tests must not load it.

## Development stack

    .\scripts\dev.ps1 start
    .\scripts\dev.ps1 status
    .\scripts\dev.ps1 restart -Scope app
    .\scripts\dev.ps1 restart -Scope frontend
    .\scripts\dev.ps1 restart
    .\scripts\dev.ps1 stop

restart -Scope app reloads API and Worker while retaining frontend and storage. It requires a verified idle Worker, drains it and checks queue readiness after restart; if work starts during draining, the controller withdraws the drain and leaves that work running. Use the full restart only when the complete stack is intentionally being restarted. Keep the user's browser and project services running after work rounds.

With PostgreSQL, Redis and Research enabled, the API checks stalled stages once per minute. The default recovery window is 15 minutes (minimum 5); execution is only expired after its database lease is also expired. Questions and saved files remain available, and failed Jobs require an explicit retry. MDI_AGENT2_STARTUP_RECOVERY_ENABLED controls startup and periodic recovery.

Default topology is PostgreSQL 55434, Redis 6380, MinIO 9000/9001, FastAPI 8005, Next.js 3023, and one Worker with six logical queues. This host uses PostgreSQL 15434 through its external local.env override.

## Checks

    .\.venv\Scripts\python.exe -m pytest -m "not integration and not live_llm and not llm_integration"
    npm --prefix apps/web test
    npm --prefix apps/web run typecheck

Run `npm --prefix apps/web run build` in an isolated checkout/workspace under the temporary root while the local frontend is running; a production build must not overwrite the live development output. CI uses its own clean checkout. On this 16 GB host, run heavy test/typecheck/build commands serially and set `$env:NODE_OPTIONS='--max-old-space-size=1024'` for them. The dependency authority is npm and `apps/web/package-lock.json`.

Tests do not load the real local.env unless explicitly authorized for an integration/live flow. Pytest scratch is outside the repository at `MDI_TEMP_ROOT\pytest` when configured, otherwise under the sibling local runtime; explicit basetemp values must be strict children of that scratch area.

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
