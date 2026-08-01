# Phase 10M-1 Evidence

Status: sanitized local evidence and manifest are implemented and verified.
Corrected implementation exact-SHA CI `30705503707` is successful, including
PostgreSQL/Redis/MinIO `37 passed, 0 skipped, 0 failed, 0 errors`.

## Evidence directory

```text
docs/phase10m/evidence/phase10m1_workspace_domain_persistence/
```

The directory contains baseline/entry records, M0 decision verification,
contract/schema parity, migration upgrade/downgrade/re-upgrade, in-memory and
SQLite repository cases, PostgreSQL service-backed cases, idempotency and
optimistic concurrency, panel/revision caps, historical projections, API
responses, security cases, performance measurements, compatibility, browser
regression, console/network summaries, secret scan, test summary, and a
deterministic file manifest. `scripts/finalize_phase10m1_evidence.py` writes
and verifies LF-normalized text and raw-binary SHA-256 membership.

## Current source evidence

The current implementation and focused tests are the source of truth for this
sidecar:

- `packages/schemas/mdi_schemas/workspace.py`
- `packages/schemas/json/workspace-v1.schema.json`
- `packages/schemas/src/index.ts`
- `apps/api/alembic/versions/0007_phase10m1_workspace_domain.py`
- `apps/api/mdi_api/repositories.py`
- `apps/api/mdi_api/workspaces.py`
- `apps/api/mdi_api/routers/workspaces.py`
- `tests/test_phase10m1_workspace_contracts.py`
- `tests/test_phase10m1_workspace_migration.py`
- `tests/test_phase10m1_workspace_persistence.py`
- `tests/test_phase10m1_workspace_projection_api.py`

## Verification status

Focused M1 tests pass (`26 passed`). Full backend passes with `1103 passed,
39 skipped, 63 warnings`; skips are local service/integration gates and are
not counted as service PASS. Frontend passes `333` tests, typecheck, and build.
Phase 10 closure plus L4/L5 Chromium/Firefox/WebKit/mobile replay pass with no
unapproved network, console, HTML/JS, overflow, or secret findings.

SQLite verifies focused `0006 -> 0007 -> 0006 -> 0007` and fresh
`0001 -> 0007`. PostgreSQL full-chain upgrade/downgrade/re-upgrade,
repository/API service evidence, and the zero-skip assertion passed corrected
exact-SHA CI. Local Docker/services remain unavailable and are not reported as
a local PASS.

Evidence must remain LF-normalized for text, hash raw binary files, and omit
secrets, private paths, credentials, provider payloads, Artifact bodies, and
storage keys.
