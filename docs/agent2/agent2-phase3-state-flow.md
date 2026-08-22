# Agent 2.0 Phase 3 State Flow

```text
READY_TO_PLAN
  -> PLANNING
     -> PLAN_READY
     -> UNSUPPORTED
     -> PLAN_REJECTED
     -> FAILED
```

`PLAN_READY` means the validated decision, immutable resolution, immutable
CapabilityPlan and existing validated AnalysisPlan all exist and the Turn has
its `analysis_plan_id`. It is nonterminal and may be canceled. It cannot move
directly to `RUNNING`; Phase 4 must create/attach a Job before `QUEUED`.

The planning RQ wakeup payload contains only `turn_id`. CAS claims make
duplicate delivery a no-op. Optional provider planning happens after the
resolution transaction commits and before a new persistence transaction.
Product SSE exposes only planning, ready, unsupported and failed states.
