---TASK---
状态：处理中

# Phase 10L-3: Bounded Multi-Tool Analysis + Typed Artifact Dependency Execution

## Objective

Introduce additive AnalysisPlan 0.2 for at most four already-eligible tools,
using one authoritative typed artifact-binding representation, deterministic
acyclic topology, exact artifact lineage, dependency-aware serial
QueueWorkerRuntime execution, and bounded partial-result semantics.

## Required Delivery

- Preserve AnalysisIntent 1.0, EligibilityResolution 1.0, AnalysisPlan 0.1,
  existing PlanValidator, Registry execution authority, and all L1/L2 gates.
- Audit all available tool outputs and select at least one real registered,
  scientifically valid producer/consumer pair; block rather than fabricate if
  none exists.
- Add strict AnalysisPlan 0.2 Python/JSON/TypeScript contracts, deterministic
  binding/graph/plan hashes, ToolPlannerMetadata artifact ports, compatibility
  matrix, bounded composer, dependency validator, persistence/migration,
  runtime binding resolution, execution records, lineage, API, frontend,
  browser/service-backed evidence, security and performance closure.
- Enforce 4 steps, 6 bindings, depth 4, 3 incoming/outgoing bindings per step,
  one total repair, and 524,288 serialized planning bytes without truncation.
- Only PLAN_READY may create a plan/job or enqueue; invalid dependency plans
  must not downgrade to 0.1 or bypass Registry/Adapter validation.
- Complete implementation exact-SHA CI, permanent result, completion-record
  exact-SHA CI, and verified queue archive before removing this block.

## Frozen Boundaries

No generic workflow engine, order-only edges, parallel scheduler, loops,
conditions, fan-out, runtime replanning/LLM, extra repair/retry, cross-job or
remote artifact inputs, arbitrary code/path/URL authority, plan editor,
interpretation, Workspace, professional science, new LLM SDK, uncontrolled
dependency, enterprise infrastructure, or Phase 10L-4 implementation.

---END---

# REVIEWER GATE AFTER PHASE 10L-3

```text
Phase 10L-3: IN_PROGRESS
Phase 10L-4: REVIEWER_GATE / AWAITING REVIEWER PROMPT
TASK_BLOCK_COUNT: 1
```

Do not create, queue, or execute Phase 10L-4 automatically. Phase 10L-4
requires reviewer approval based on the real Phase 10L-3 implementation,
dependency execution evidence, artifact lineage, failure semantics, CI,
completion record, and verified queue archive.
