# AGENTS.md

## Active repository

This checkout is the active engineering repository. Historical sibling checkouts
are reference material, not source or runtime authorities for this checkout.

## Read first

Read `PROJECT_STATE.md`, then inspect only the code and tests relevant to the
current task. For product capability or goal handoff work, also consult
`CAPABILITIES.md` and `REMAINING_WORK.md`; their numbered sections correspond.
Use `README.md` for installation and operation.

## Product safety invariants

- Product LLMs may not execute arbitrary Python, shell, filesystem, or network operations.
- Executable analysis calls must be structured, validated by the current Tool Registry, and executed by controlled adapters.
- Long parsing, planning, scientific execution, rendering, export, and report work remains asynchronous.
- The UI may show structured status and provenance, but never hidden chain-of-thought.
- Secrets and BYOK values must not enter prompts, logs, artifacts, reports, recipes, or exports.
- Preserve real user data and the Alembic migration chain.
- Do not overwrite unrelated uncommitted work, use `git reset --hard`, force push, deploy, publish, tag, or release without explicit authorization.

## Repository hygiene

- Git contains source, executable contracts, tests, and concise current documentation; Git history contains project history.
- Do not create phase, qualification, attempt, closure, evidence-bundle, or result-ledger files for normal development.
- Do not place PostgreSQL, Redis, MinIO, SQLite runtime state, logs, caches, PID files, temporary screenshots, or temporary exports in the repository.
- Local persistent data belongs under `MDI_LOCAL_ROOT` (normally the sibling `<checkout-name>.local` directory).
- Resolve the temporary root from the current user instruction or external `local.env` (`MDI_TEMP_ROOT`), otherwise use `<local-root>/tmp`. Keep it outside the repository. Put each task/run in its own child directory; never recursively clear the temporary root itself.
- Set `MDI_TEMP_ROOT`, `TEMP`, `TMP` and `TMPDIR` to the task temporary path before project commands. `scripts\dev.ps1` loads the configured path from the external `local.env`; commands that bypass it must set these process variables explicitly. Pytest uses dedicated `MDI_TEMP_ROOT/pytest` and `pytest-cache` children and keeps numbered-run isolation. Unit tests never load real service credentials.
- This temporary-path setting does not relocate persistent data, logs, service state or existing files. Keep project services and the user's browser running across work rounds.
- Do not create a new top-level directory unless current product source or an executable contract genuinely requires it. Explicitly approved public documentation images may live with the web assets; temporary evidence stays outside Git.
- Update `PROJECT_STATE.md` only when current product state, architecture, scope, or operating instructions materially change.

## Change workflow

Work on `master` in this repository. The user requests a single main branch;
create another branch only when explicitly requested.

1. Read `PROJECT_STATE.md`.
2. Inspect the relevant implementation and existing behavior tests.
3. Make the smallest coherent change.
4. Run focused tests.
5. Run broader regression only when subsystem boundaries are touched.
6. Update `PROJECT_STATE.md` only for a material current-state change.
7. Commit only when the task explicitly requires it.

## Runtime and processes

- Unit/code-only work does not require the full stack.
- Frontend-only and backend-only work should start only their required dependencies.
- Start the full stack for real end-to-end Research or data flows.
- Use `scripts\dev.ps1 init|doctor|migrate|start|status|stop|restart` for the project-owned local stack.
- Stop only processes whose ownership is verified by the project runtime state, command line, port, and local data root. Never stop unknown or shared services merely because a PID or conventional port matches.
- Clean up task-created temporary processes when they are no longer needed.

## Current authority

- `PROJECT_STATE.md`: current product and architecture state.
- `README.md`: installation and operation.
- Code, schemas, migrations, Tool Registry manifests, and tests: executable contracts.
