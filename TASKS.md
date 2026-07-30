---TASK---
状态：处理中

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

---END---

# REVIEWER GATE AFTER PHASE 10L-2

```text
Phase 10L-2: IN_PROGRESS
Phase 10L-3: REVIEWER_GATE / AWAITING REVIEWER PROMPT
```

Do not execute or queue Phase 10L-3 automatically. Phase 10L-3 requires
reviewer approval based on the real Phase 10L-2 implementation, evidence, CI,
and completion result.
