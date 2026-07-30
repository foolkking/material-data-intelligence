---TASK---
状态：已完成

# Phase 10L-2: Capability-Aware Planner + Eligibility Resolver

## Objective

Replace non-capability-aware tool choice on the canonical READY AnalysisIntent
path with validated Registry planner metadata, deterministic eligibility,
eligible-only provider projection, capability-aware selection, exact semantic
parameter binding, independent capability-context validation, and at most one
strict LLM repair. Produce unchanged AnalysisPlan 0.1 only for `PLAN_READY`.

## Required Delivery

- Strict planner metadata for every current Planner-visible Registry tool.
- Versioned deterministic resolution and decision contracts with semantic
  hashes, typed rejection diagnostics, caps, and immutable persistence.
- Deterministic Mock selection and strict eligible-only OpenAI-compatible
  selection with one validation-guided repair and no fallback.
- Exact Intent/Profile/Registry binding and parameter provenance; no
  first-column, fuzzy target, display-label, Registry-order, or invented-ID
  selection.
- Additive API and PlannerWorkbench capability surfaces. Non-ready outcomes
  create no plan/job, enqueue nothing, and execute no tool.
- Focused/full/service-backed/browser/performance/security evidence, exact-SHA
  implementation and completion CI, then verified queue archive.

## Frozen Boundaries

Do not change AnalysisPlan 0.1, weaken PlanValidator, change QueueWorkerRuntime
semantics, add dependencies/artifact binding, expand scientific tools, add a
new LLM dependency, arbitrary execution, external scientific APIs, result
interpretation, Workspace behavior, or Phase 10L-3 implementation.

## Completion Gate

This block remains until implementation and completion-record exact-SHA CI are
successful and evidence/results/persistent records agree. Archive only by
deleting this complete block after verification. Do not queue or execute Phase
10L-3.

## Completion Record

- 完成时间：2026-07-30 11:45:38 +08:00
- 修改文件：Registry planner metadata、capability-planning shared schemas、
  Eligibility Resolver/selector/binder/validator、API persistence/migration、
  PlannerWorkbench、focused/service-backed/browser tests、Phase 10L-2 evidence、
  docs、persistent records 和 `results.md`。
- 修改摘要：在 canonical READY AnalysisIntent path 上增加 Registry-derived
  eligibility、eligible-only provider projection、deterministic selection、
  exact binding provenance、one-shot strict LLM repair 和 independent context
  validation；只有 PLAN_READY 进入 unchanged AnalysisPlan 0.1/job/runtime。
- 测试结果：本地 focused 10L-1/10L-2、full backend/frontend、typecheck/build、
  Chromium/Firefox/WebKit/mobile、evidence/security PASS；corrected implementation
  `9786e405f1938b514b95ccbeb1cdb6d4b26dde18` exact-SHA CI run
  `30511654404` PASS，service-backed `27 passed, 0 skipped, 0 failed`。
- 提交/CI：completion-record commit 和其 exact-SHA CI 待本 block 保留状态下
  完成；成功后才允许 verified queue archive。

---END---

# REVIEWER GATE AFTER PHASE 10L-2

```text
Phase 10L-2: COMPLETE / AWAITING_COMPLETION_RECORD_CI
Phase 10L-3: REVIEWER_GATE / AWAITING REVIEWER PROMPT
```

Do not execute or queue Phase 10L-3 automatically. Phase 10L-3 requires
reviewer approval based on the real Phase 10L-2 implementation, evidence, CI,
and completion result.
