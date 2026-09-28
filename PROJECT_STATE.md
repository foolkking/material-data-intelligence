# Project State

## 1. Product Purpose

MDI provides a durable materials-science workspace in which users manage source data, request validated analyses, inspect authoritative scientific results, and receive grounded interpretations and reports.

## 2. Current V0 Scope

Authenticated projects and datasets; immutable scientific object versions and provenance; validated Analysis Plans and Tool Registry execution; asynchronous Research Turn, Plan, Job, Result, Interpretation, and Report workflows; deterministic scientific adapters; PostgreSQL durability, Redis/RQ execution, MinIO object storage, and browser recovery from durable state.

## 3. Explicit Non-goals

Arbitrary LLM execution, hidden chain-of-thought display, browser-owned scientific authority, development mocks replacing core stores, M6/F15 execution under the superseded roadmap, and UI redesign during this consolidation.

## 4. Current Architecture

Next.js talks to FastAPI. FastAPI persists identity and workflow state in PostgreSQL, stores payloads/artifacts in MinIO, and enqueues asynchronous work through Redis/RQ. One local multi-queue worker consumes the active logical queues; ownership, leases, fencing, and idempotent publication remain database-authoritative.

## 5. Core Modules

`apps/api` owns API/application/persistence/Research orchestration; `apps/web` owns the UI; `packages` owns schemas, registries, adapters, parsers, and artifacts; `services/workers` owns RQ execution; `services/llm` owns bounded provider integration.

## 6. Runtime Topology

Default local services are PostgreSQL `55434`, Redis `6380`, MinIO `9000/9001`, FastAPI `8005`, Next.js `3023`, and one multi-queue RQ worker. Logical queues remain distinct for routing and observability.

## 7. Persistent Data Ownership

Git stores source and executable contracts. `MDI_DATA_ROOT` stores PostgreSQL and MinIO authoritative local data. `MDI_RUNTIME_ROOT` stores Redis runtime, PID/state files, logs, cache, and temp. The normal local root is the sibling `mdi-b0-5a1.local`; secrets live in its untracked `local.env`.

## 8. Current Product State

V0 through M5 is complete. Service-edge recovery and the 120-minute mixed-work endurance qualification were accepted. Historical qualification data is not current product authority.

## 9. Completed Major Milestones

Pre-M and M0–M3 established the product, scientific authority, durable recovery, and bounded provider/resource behavior. M4 closed F11, F13, and F14. M5 passed sustained mixed-real-work endurance and included the runtime memory-release repair. M6 is **superseded / not executed by current product decision**.

## 10. Current Verification

Current verification covers migration head, authentication, preserved project records, MinIO access, API/frontend health, multi-queue execution, focused backend regression, frontend tests/typecheck/build, and stop/restart of the project-owned stack.

## 11. Known Product Debt

UI framework consistency, redundant Data/Research navigation, and remaining early Agent2/phase-oriented internal test names need later product-level consolidation.

## 12. Current UI Direction

The next phase should unify the application frame and clarify Data, Research, provenance, execution, and recovery state without changing scientific authority or moving execution into the browser.

## 13. Next Work

Begin UI/Product Framework consolidation from this baseline. Do not resume M6.

## 14. Current Accepted Commit

The accepted pre-consolidation baseline is
`a57c0b583e27cd686e547ebb03bfed5d3e59cfe4`. This consolidation is the current
governance change; Git `HEAD` is the final authority after the single
consolidation commit.
