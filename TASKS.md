---TASK---
状态：已完成

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

完成时间：2026-07-29 13:43:46 +08:00

修改文件：`TASKS.md`、`apps/api/`、`apps/web/`、`packages/schemas/`、
`services/llm/`、`tests/`、`.github/workflows/ci.yml`、`docs/phase10l/`、
`docs/13_SHARED_SCHEMA_SPEC.md`、`docs/CAPABILITY_STATUS_MATRIX.md`、
`docs/index.md`、`persistent/` 和 `results.md`。

修改摘要：新增独立 `AnalysisIntent v1` Python/JSON Schema/TypeScript 合同、
确定性 semantic hash/ID、精确 DataProfile 2.0 scope/target/resource 绑定、
READY/NEEDS_CLARIFICATION/UNSUPPORTED 状态、一次最多三问的 immutable 澄清、
deterministic Mock 与 strict-JSON OpenAI-compatible path、独立 Validator、
SQL/in-memory persistence、Alembic migration、typed API、Planner 上游 gate 和
PlannerWorkbench Intent/clarification/unsupported/inert audit surface。未修改
AnalysisPlan 0.1、PlanValidator、Tool Registry 或 QueueWorkerRuntime 语义。

测试结果：focused backend `27 passed`；frontend focused `22 passed`；backend
full `864 passed, 28 skipped`；frontend full `325 passed`；typecheck/build、
lock、Phase 10 closure、三浏览器/mobile、evidence integrity、安全与 network
markers 通过。本机 service-backed 因无 Docker 为 `UNAVAILABLE`；implementation
HEAD `844eb149a4c528d28db9fdf70dddfaf015e91d5a` 的 exact-SHA CI run
`30425804801` 已通过 Unit、Frontend、PostgreSQL/Redis/MinIO service-backed 和
no-skipped。Completion-record CI 与 verified queue archive 尚待闭合。

---END---

# REVIEWER GATE AFTER PHASE 10L-1

```text
Phase 10L-0: ARCHIVED
Phase 10L-1: COMPLETED_AWAITING_COMPLETION_RECORD_CI_AND_ARCHIVE
Phase 10L-2: REVIEWER_GATE / AWAITING REVIEWER PROMPT
```

Do not execute or queue Phase 10L-2 automatically. Phase 10L-2 requires
reviewer approval based on the real Phase 10L-1 implementation, evidence, CI,
and completion result.
