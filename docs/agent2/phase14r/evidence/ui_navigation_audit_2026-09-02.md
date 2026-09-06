# UI Navigation Audit — 2026-09-02

## Scope and evidence

This audit covers the shared product navigation used by Projects, Project Home,
Data, Research, Reports, Tasks, Notifications, History, Viewer and mobile
layouts. Evidence is based on the current frontend source plus persisted
browser/performance captures from the same-stack qualification campaign.
The in-app browser connector was unavailable in this child task, so no new
live-browser PASS is claimed here.

## Findings

### Navigation — no current full-document reload found

`ProductNavigationProvider` uses Next App Router `router.push`/`router.replace`
and `ProductLink` uses `Link` for internal routes. `ProductRouteFrame` keeps the
shared product shell mounted across route changes. Persisted navigation captures
recorded `documentRequests=0` and preserved the shell marker for Projects,
Project Home, Data, Research and Reports on desktop and mobile.

### Performance — production route transitions are within the current baseline

The production captures show no document requests and the following URL/usable
latencies (milliseconds):

| Capture | Route | Cold | Warm |
| --- | --- | ---: | ---: |
| Desktop 1280x720 | Data | 85 | 49 |
| Desktop 1280x720 | Research | 118 | 49 |
| Desktop 1280x720 | Reports | 61 | 29 |
| Mobile 390x844 | Data | 68 | 45 |
| Mobile 390x844 | Research | 102 | 45 |
| Mobile 390x844 | Reports | 66 | 35 |

The older local-runtime captures had Data/Research cold timings around
1.4–3.5 seconds, but this is not reproduced by the dedicated production
captures and is therefore classified as runtime warm-up noise, not a confirmed
shared navigation defect.

### Shared loading feedback is present

`RouteTransitionProgress` delays its indicator by 120 ms to avoid flicker,
clears it on route commit, and has a bounded timeout. `RouteLoading` preserves
the Research workbench shape during loading instead of replacing it with a
blank page.

### Existing fixes verified in source/tests

* The legacy report route avoids a predictable modern report probe for
  `job_*`/`run_*` identifiers; its focused test covers the read-only legacy
  path.
* Mobile scientific tables expose a deliberate horizontal-scroll affordance
  through `.workspace-table-mobile-hint`; the related gallery/workspace tests
  pass.
* Task-center requests use shared TTL and in-flight deduplication.

## Severity outcome

No new P0/P1 navigation defect is supported by the available evidence. No code
change is required in this audit batch.

## Remaining verification

Fresh interactive browser control should be repeated when the browser connector
is available, especially to confirm the current rebuilt runtime includes the
legacy-report and mobile-table fixes. This is a verification debt, not evidence
of a product failure.
