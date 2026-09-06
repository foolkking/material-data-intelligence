# Product Maturity Batch — Runtime Compatibility and Project Governance

Date: 2026-09-01
Status: completed batch; umbrella Product Maturity Closure remains in progress.

## Runtime and visibility diagnosis

The reported unavailable/`Internal Server Error` pages were not caused by
stopped PostgreSQL, Redis, MinIO, API, worker, or frontend services. The
current same-stack runtime remains:

```text
API            = http://127.0.0.1:8005
frontend       = http://127.0.0.1:3013
PostgreSQL     = 127.0.0.1:55434/mdi
Redis          = 127.0.0.1:6379/13
MinIO          = 127.0.0.1:9000/mdi-artifacts
workers        = six Redis-backed workers
```

`GET /health/runtime` returned `200` with PostgreSQL, Redis, MinIO, Redis
workers and the configured provider all `ok`. The acceptance-visible
scientific inventory currently resolves all 13 ScientificObject Viewer
projections as `READY`, with no visible `SOURCE_MISSING`, and the canonical
Dataset/report routes return `200`.

The user-facing `127.0.0.1:3000` entry had no listener while the current
production frontend was intentionally isolated on `3013`. A small, inert
HTTP compatibility alias was added and started as a separate hidden process:

```text
3000 → 3013
```

It does not own application state, does not alter API routing, and leaves the
primary frontend and all scientific services running. Root, Dataset and
canonical Report requests through the alias returned `200`.

The two historical synthetic Artifact references documented in the payload
availability ledger remain intentionally fail-closed; they are not visible
acceptance-user scientific data and were not fabricated.

## Project governance batch

Platform-admin project governance now exposes the existing durable
`project_members` authority without adding a second permission model:

```text
GET    /api/admin/projects
GET    /api/admin/projects/{project_id}/members
PUT    /api/admin/projects/{project_id}/members/{user_id}
DELETE /api/admin/projects/{project_id}/members/{user_id}
```

The bounded Admin Center now includes a project/member section using the
existing scientific workbench tokens and responsive table/list patterns.
Project owners are protected from role demotion/removal. Every membership
mutation is server-authorized and emits a sanitized platform audit event.
ScientificObject, ScientificObjectVersion, Result, Artifact and Report
authority remain unchanged.

## Verification

```text
backend account/admin focused = 7 passed
frontend Admin/Trash/ProductShell focused = 24 passed
frontend typecheck             = PASS
frontend production build      = PASS
touched Ruff                   = PASS
compileall                     = PASS
git diff --check               = PASS
```

No service or existing browser tab was closed. No commit, push or CI run was
performed in this local fix-forward batch.

## Remaining maturity status

The umbrella Product Maturity Closure task remains `处理中`. The current
remaining work is broader lifecycle/retention/export, full real-user
qualification and release evidence; this batch specifically closes the
runtime-entry compatibility and platform-admin project-governance seam.
