# Phase 10L-2 Persistence, API, and Compatibility

## Persistence

Alembic revision `0004_phase10l2_capability_planning` adds immutable tables for
eligibility resolutions, capability decisions, and successful execution
associations. Resolution and decision records preserve deterministic semantic
IDs/hashes, exact Intent/Profile/Registry identities, provider and repair
provenance, and the bounded contract JSON. Execution association links a
`PLAN_READY` decision to the unchanged plan and job outside AnalysisPlan 0.1.

Repository saves are idempotent for identical content and reject a different
semantic record under the same identity. The migration upgrades from 0003 and
defines downgrade removal in reverse dependency order. SQLite repository and
migration behavior are covered locally; PostgreSQL behavior is a required
exact-SHA service-backed CI gate.

## Canonical API Flow

The canonical Intent path now loads the persisted READY Intent and exact
Profile, constructs and validates the current Registry snapshot, resolves
eligibility, selects and binds capabilities, validates capability context,
and only then emits AnalysisPlan 0.1 through the existing PlanValidator and
job/enqueue path.

Additive response fields expose bounded resolution and decision summaries.
Only `PLAN_READY` creates a plan, job, or queue message. Clarification,
unsupported, mismatch, and validation failure return typed responses before
those side effects. The optional single LLM repair is recorded in decision
provenance.

## Compatibility

- `AnalysisIntent` remains schema `1.0`.
- `AnalysisPlan` remains schema `0.1`; historical hashes are unchanged.
- PlanValidator and QueueWorkerRuntime semantics are unchanged.
- Tool input/output execution contracts are unchanged.
- Historical jobs and artifacts remain readable.
- Legacy requests without Intent retain their documented route and are marked
  by legacy provenance; canonical failures never downgrade to that route.
- READY Intent requests preserve existing execution after the new selection
  and validation gate.
- Phase 10K Profile and product semantics remain the source facts rather than
  being re-inferred by the Planner.
