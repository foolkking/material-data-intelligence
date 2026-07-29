---TASK---
状态：处理中

# Phase 10L-1: Analysis Intent Contract + Bounded Clarification

## Objective

Implement an independent, versioned, persisted, validated and auditable
`AnalysisIntent v1` between the natural-language request and the existing
Planner. Preserve the raw goal, bind exact DataProfile 2.0 identities, expose
`READY`, `NEEDS_CLARIFICATION` and `UNSUPPORTED`, and support at most one
clarification round with at most three typed questions.

## Required Delivery

- Python, JSON Schema and TypeScript contract parity with deterministic
  canonical serialization and semantic hashing.
- Independent deterministic and strict-JSON LLM Intent paths with no silent
  repair or provider fallback.
- Independent validator, bounded caps, Future/Not Planned and execution-boundary
  rejection, exact semantic/resource binding, and immutable clarification
  revisions.
- SQLAlchemy/in-memory repositories, Alembic migration, PostgreSQL-compatible
  persistence, and intent-to-plan/job association outside AnalysisPlan 0.1.
- Typed create/get/clarify API and an upstream `/planner/jobs` gate. Non-READY
  states must not create a plan/job or enqueue work; READY must preserve the
  current provider, routing, PlanValidator and QueueWorkerRuntime behavior.
- Minimal PlannerWorkbench Intent, clarification, unsupported and inert audit
  surfaces with accessibility/mobile coverage.
- Focused/full tests, service-backed/browser/API/performance/security evidence,
  documentation and persistent project records.
- Implementation exact-SHA CI, completion record exact-SHA CI, then verified
  queue archive.

## Frozen Boundaries

Do not change AnalysisPlan 0.1, PlanValidator, Tool Registry planner metadata,
QueueWorkerRuntime semantics, tool ranking, dependencies, artifact binding,
plan repair, result interpretation, Workspace, professional science, Registry
tools, scientific renderers or dependencies. Default CI must make zero real LLM
calls and no external network requests.

## Completion Gate

The task remains in this queue until implementation and completion-record
exact-SHA CI are successful and evidence/results/persistent records agree.
Archive only by deleting this entire block after verification. Do not queue or
execute Phase 10L-2.

---END---

# REVIEWER GATE AFTER PHASE 10L-1

```text
Phase 10L-0: ARCHIVED
Phase 10L-1: IN_PROGRESS
Phase 10L-2: REVIEWER_GATE / AWAITING REVIEWER PROMPT
```

Do not execute or queue Phase 10L-2 automatically. Phase 10L-2 requires
reviewer approval based on the real Phase 10L-1 implementation, evidence, CI,
and completion result.
