# Phase 10L-1 Planner Compatibility

The production flow is now:

```text
request -> exact Profile 2.0 -> AnalysisIntent v1
        -> READY -> existing Planner -> existing PlanValidator
        -> persisted AnalysisPlan 0.1 -> existing QueueWorkerRuntime
```

`NEEDS_CLARIFICATION` and `UNSUPPORTED` stop before Planner invocation,
AnalysisPlan/job persistence, and enqueue. On READY, the existing provider,
raw goal, tool list, route precedence, generated params, PlanValidator, plan
hash, and Runtime path are preserved.

Phase 10L-1 does not add Registry planner metadata, an eligibility resolver,
capability ranking, multi-tool dependencies, artifact binding, partial success,
repair, interpretation, or workspace behavior. Existing legacy callers may
continue without Intent fields; historical plans/jobs/artifacts remain readable
and historical plan hashes are unchanged.

The deterministic Intent path is an explicit allowlisted classifier over the
raw goal and exact Profile facts. The optional OpenAI-compatible path reuses the
existing bounded provider transport, accepts exactly one strict JSON object,
and has no repair or Mock fallback.
