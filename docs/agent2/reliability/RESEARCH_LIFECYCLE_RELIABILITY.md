# Research Lifecycle Reliability

状态：Workstream A canonical recovery record  
日期：2026-09-10

## Canonical ownership

This record applies to the active repository
`E:\1project\mdi-b0-5a1`. The old tree
`E:\1project\Material Data Intelligence` is historical/recovery source only
and is not an implementation target.

The durable lifecycle authorities remain:

```text
ResearchTurn / ResearchTurnEvent  control flow and transition history
AnalysisPlan / CapabilityPlan     validated execution intent
Job / ToolCall / Artifact          execution authority and outputs
ScientificResult                  immutable normalized result
Interpretation / Report            source-referenced projections
```

## Recovered behavior

The canonical tree now includes a bounded, read-only lifecycle projection in
`mdi_api.research_agent.lifecycle`. The authorized
`/api/research/turns/{turn_id}/correlation` projection exposes:

- conceptual stage and owner;
- stage entry and available latency measurements;
- ContextSnapshot identity and bounded provenance summary;
- decision, resolution, plan, Job, ToolCall, Result, Interpretation and
  Report availability;
- bounded attempt/latest-event data;
- failure category and smallest safe recovery action.

The projection does not create a second state machine or expose provider
payloads, credentials, ToolCall parameters, stack traces, or hidden reasoning.

Failure categories are:

```text
NONE / TERMINAL / RETRYABLE / RECOVERABLE / CANCELLED
```

Recovery continues to use the existing durable identities and boundaries.
Stale active work is classified as recoverable for reconciliation; CAS,
row-lock and existing identity checks remain the protection against an old
worker overwriting newer state.

## Context and memory seams

Workstream B recovery adds provenance metadata to existing context candidates,
operation manifests, ContextSnapshot projections and memory references. The
lifecycle projection can now report candidate/selection counts, source
categories, freshness warnings, budget and degradation state.

## Verification

Canonical focused verification:

```text
83 passed, 15 warnings
compileall PASS
git diff --check PASS
frontend typecheck PASS
Research provenance UI 93 passed
canonical runtime stack PASS
six canonical worker queues discovered
```

The 83-test run covers lifecycle projection, correlation API compatibility,
recovery, context manifests, provenance/memory contracts and existing Agent2
behavior. Canonical service-backed Phase 2/3/4/7 flows passed against the
PostgreSQL, Redis/RQ and MinIO stack started from
`E:\1project\mdi-b0-5a1`, including exact ContextSnapshot persistence,
planning, worker execution, continuation and historical exact-version reuse.

## Known limitations

- There is no durable per-worker lease/heartbeat column. Stale detection is
  an observation policy over persisted timestamps; it is not proof of
  multi-hour lease expiry under load.
- Intrinsically non-resumable scientific processes can recover only from their
  latest durable Job/ToolCall boundary.
- The projection is a read model, not a metrics backend.
