# Performance / Product Fluency Baseline

Status: `NOT_QUALIFIED` on 2026-08-28. This artifact defines the measurement
plan and records no invented timing numbers.

Measure cold and warm runs for:

```text
page navigation, project/data lists, typed Dataset query, Research submit
acknowledgement, first truthful progress, planning, queue wait, Viewer
metadata, Viewer usable state, Report open, History resume, search typing,
cancel acknowledgement, mobile interaction
```

Record p50/p95 wall time, request count, payload size, render count, and
resource usage. Separate scientific computation duration from interaction
latency. Initial product goals are immediate visual feedback, sub-second
normal navigation, first truthful progress near one second when services are
healthy, Viewer usability within roughly two seconds for bounded data, and
cancel acknowledgement within roughly one second. These are goals, not
current PASS evidence; measured deviations must be documented.

No fake progress is permitted. UI state must derive from persisted
ResearchTurn/Plan/Job/ToolCall/Artifact/Result/Interpretation state.

