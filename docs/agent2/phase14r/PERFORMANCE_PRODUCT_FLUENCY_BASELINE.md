# Performance / Product Fluency Baseline

Status: `PARTIAL` on 2026-08-28. A warm authenticated Research navigation
against the same-stack runtime reached DOM-ready in `1442 ms` and exposed the
research composer after `1945 ms` (including a 500 ms settling window). This
is an initial point measurement, not a p95 SLO qualification.

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

The remaining cold/warm matrix, p50/p95 campaign, payload/render/resource
measurements and mobile interaction timings remain open; no release PASS is
claimed from this single sample.
