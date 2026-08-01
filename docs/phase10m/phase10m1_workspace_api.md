# Phase 10M-1 Workspace API

Status: additive API implementation and local regression are verified.
Service-backed and exact-SHA verification remain pending; no archive claim is
made.

## Implemented routes

The current route registration is in `apps/api/mdi_api/main.py` and the
handlers are in `apps/api/mdi_api/routers/workspaces.py`.

| Method | Route | Current purpose |
| --- | --- | --- |
| POST | `/workspaces` | Explicit create/project by source Job |
| GET | `/workspaces/{workspaceId}` | Metadata-first Workspace snapshot |
| PATCH | `/workspaces/{workspaceId}` | Mutable title/layout/selection state with `If-Match` |
| GET | `/projects/{projectId}/workspaces` | Bounded project Workspace list |
| GET | `/projects/{projectId}/analysis-jobs` | Historical Job candidates and projection state |
| GET | `/workspaces/{workspaceId}/panels` | Ordered panel descriptors |
| GET | `/workspaces/{workspaceId}/panels/{panelId}` | One panel descriptor |
| GET | `/workspaces/{workspaceId}/layout-revisions` | Bounded immutable revision history |
| GET | `/workspaces/{workspaceId}/layout-revisions/{revision}` | Exact layout revision |

`/workspaces/{workspaceId}` is an additive API identity. The Workspace page
and route UI remain deferred to Phase 10M-2.

## Write and read semantics

Create requires `Idempotency-Key`, validates Project/Job scope, creates the
initial panel projection and layout revision, and returns a snapshot with an
ETag. A semantic retry returns the existing Workspace rather than creating a
second row. PATCH requires a quoted `If-Match` ETag and only accepts the
bounded mutable request fields. A stale ETag is rejected with a typed
revision-conflict response.

GET responses are metadata-first and do not load or return complete Artifact
payloads. `If-None-Match` can return `304`. Ordinary Job listing and Workspace
GET do not create a hidden Workspace projection.

Request parsing uses strict JSON duplicate-key detection, unknown-field
rejection, byte caps, UTF-8 validation, and Pydantic contract validation.
Errors use bounded `{code, message, retryable}` details and do not expose
stack traces, SQL, paths, storage keys, credentials, or provider payloads.

## TypeScript client

`apps/web/app/lib/workspace-api.ts` contains typed client contracts and
functions for create, get, patch, project listing, Job candidates, panels, and
layout revisions. The client does not add a Workspace page, renderer, or
selection store.

## Current verification state

API-focused tests in `tests/test_phase10m1_workspace_projection_api.py`, full
backend regression, frontend regression, and existing browser replay pass.
PostgreSQL/Redis/MinIO and exact-SHA CI are **PENDING**. Workspace UI is
intentionally not implemented in M1.

`REAL_LLM_CALLS = 0`; no API route in this scope invokes an LLM, ToolCall,
Job enqueue, or scientific adapter.
