# Performance / Product Fluency Baseline

Status: `PARTIAL` on 2026-08-28. Warm authenticated navigation was measured
against the live same-stack runtime (API/Redis/MinIO workers unchanged):

| Route | Wall time |
| --- | ---: |
| `/projects/project_0002_1a0af866391f412d/data` | 175 ms |
| `/projects/project_0002_1a0af866391f412d/research` | 215 ms |
| `/projects/project_0002_1a0af866391f412d/reports/agent2_report_819f458171ba2d3219717895bf12eaf9` | 259 ms |
| `/tasks` | 202 ms |
| `/notifications` | 189 ms |

An earlier warm Research navigation reached DOM-ready in `1442 ms` and
exposed the research composer after `1945 ms` including a 500 ms settling
window. These are point measurements, not p95 SLO qualification.

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
