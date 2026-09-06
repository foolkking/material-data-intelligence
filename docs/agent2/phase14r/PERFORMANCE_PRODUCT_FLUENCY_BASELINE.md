# Performance / Product Fluency Baseline

## 2026-09-05 Research submit and first-truthful-progress baseline

The current worktree was built into the isolated `.next-contopt-0905`
production directory and served on `127.0.0.1:3024` without stopping the
existing `3023` frontend. Both frontends use API `8005`; `/health/runtime`
reported PostgreSQL, Redis, MinIO, Redis workers and configured DeepSeek
healthy.

Research now records a bounded current-tab diagnostic across the App Router
handoff:

```text
submit
→ second animation frame visible acknowledgement
→ exact ResearchTurn binding
→ first persisted progress status
```

It stores no prompt, Result data, credentials or infrastructure secrets and
retains at most 50 samples. Five authenticated non-computing Research requests
produced:

| Metric | p50 | p95 | Budget |
| --- | ---: | ---: | ---: |
| double-paint acknowledgement | 26 ms | 29 ms | 500 ms |
| first exact persisted `RECEIVED` | 262 ms | 293 ms | 1500 ms |

Exact Turn IDs:

```text
44a0fef8-fe87-4265-8de7-c4403cfd8760
857a7e5e-d634-4c91-bad5-d01f1f7fd6ab
84eeb963-7d56-4422-aec4-7698d58cdff5
1d5a494a-9dc2-45c1-9168-055baaf663c2
fac4a3e5-e04c-4973-a69f-6aefa2065a52
```

Browser warnings/errors were zero. Focused helper/Research tests, typecheck and
the isolated production build passed. The first progress state is durable
server state; no synthetic “thinking” phase was introduced.

## 2026-09-01 immutable production navigation seal

The latest current-worktree frontend was built into the immutable
`.next-prod-phase14r-navseal2` directory and served on `127.0.0.1:3008`
against API `8002`, PostgreSQL, Redis and MinIO. This avoided the diagnosed
local acceptance hazard where a running Next process retained an older
HTML/manifest while its build directory was overwritten with newer hashed
chunks. The product code was not blamed for that mismatched-runtime failure.

The navigation provider now coalesces repeated pointer/focus prefetch intent
for 1.5 seconds. Route completion is driven by the App Router's committed
pathname/search state through `RouteTransitionProgress`; the redundant 50 ms
`window.location` polling loop was removed.

| Viewport | Cold usable range | Warm usable range | Document requests | ProductShell |
| --- | --- | --- | --- | --- |
| `1280x720` | `61–118 ms` | `33–70 ms` | `0` for all eight transitions | exact marker/node preserved |
| `390x844` | `66–102 ms` | `41–68 ms` | `0` for all eight transitions | exact marker/node preserved |

Every transition also made zero post-login `/auth/me` requests. The production
route was independently opened and authenticated in the Codex in-app browser;
the Research workbench rendered with no captured console warning/error. The
completed Dataset result remained bounded at `390/390` with its conversation/
workbench switch, scientific presentation and contextual research actions
reachable.

Focused navigation, persistent-frame, ProductShell and Research regression:
`85 passed`; TypeScript typecheck and production build: `PASS`.

## 2026-08-31 isolated production navigation baseline

To distinguish product architecture from active-development HMR, the current
worktree was built into the isolated `.next-prod-phase14r-batch1` output and
served on `127.0.0.1:3002` without stopping the existing development or
production services. The production frontend used current API `8002`, real
PostgreSQL, Redis and MinIO.

Two authenticated navigation cycles clicked the normal project navigation:

| Route | Cold URL / usable | Warm URL / usable | Document requests | Shell identity |
| --- | --- | --- | --- | --- |
| Data | `103 / 112 ms` | `93 / 97 ms` | `0` | preserved |
| Research | `49 / 1889 ms` | `33 / 866 ms` | `0` | preserved |
| Reports | `53 / 58 ms` | `53 / 59 ms` | `0` | preserved |
| Overview | `241 / 1076 ms` | `46 / 872 ms` | `0` | preserved |

The global ProductShell count remained exactly one and both the window marker
and DOM-node marker survived all eight transitions. Data, Research and Reports
were already prefetched on several transitions and therefore required zero
new RSC requests; this is cache reuse, not a document reload.

The authenticated trajectory-diffusion page at `390x844` measured
`documentElement/body = 390/390`, rendered the complete fit/evidence path and
reported zero post-auth console errors, page errors, critical responses or
failed API requests. Login bootstrap `401` and canceled unused RSC prefetches
were separately observed before the valid-path sample and are not product
runtime failures.

The active Next development server still incurs multi-second compilation and
Fast Refresh full reloads while files are edited. Those development-only
events explain the user's earlier perception and must not be used as
production navigation evidence. Broader p95, heavy Viewer, provider submit and
cancel SLO campaigns remain open.

## 2026-08-30 route-continuity and layout defect follow-up

An additional authenticated live-browser audit distinguished framework
navigation from development compilation cost:

```text
Research → Data warm server route: 89 ms
document/icon reload request:       0
window marker retained:             YES
browser errors/warnings:            0
```

The first Data and Research visits compiled their route chunks in `1779 ms`
and `1178 ms` respectively on the Next development server. This cost explains
the slow first transition but is not a browser document reload. Remaining
same-origin Planner/Workspace paths were converted from
`window.location.assign` or plain anchors to Next `router.push`/`Link`.

Responsive measurements after the same batch:

```text
mobile effective layout viewport: 375 px
document/body/header scroll width: 375/375/375 px
desktop Data Navigator:            248/248 px
desktop control row:               208/208 px
desktop managed rows:              224/224 px
```

The mobile product header retains the accessible product mark and its four
primary global actions while hiding only the redundant long brand wordmark.
The Data Navigator keeps lifecycle actions at a consistent `44 px` column.
These close the measured overflow defects; provider-scale submit/cancel
latency, heavy Viewer p95 and repeated-flow resource measurements remain open.

The Research timeline was also found to render every long branch message in a
single DOM even when the user opened one historical Turn. The authenticated
acceptance session contained `50` messages. The route now renders a
five-message window around the exact selected Turn by default, with an explicit
full-history control:

```text
bounded articles: 5
hidden unrelated history: 45
expanded articles: 50
collapsed articles: 5
selected Turn message retained: YES
mobile document width: 390/390
```

This is presentation-only progressive disclosure. It does not delete,
summarize or mutate message authority. Active progress has its own live region,
so historical expansion is not announced as a stream of fifty new messages.

## 2026-08-30 — Client navigation and transition evidence

The current same-stack Chromium navigation campaign clicked the existing
project navigation (`数据 → 研究 → 报告 → 概览`) rather than using direct URL
loads. Every transition had `documentRequests = 0`, retained a window marker
across routes and used a single Next RSC request (Report cold path used two
while its route chunk settled). The browser therefore remains on the App
Router client-navigation path; the prior “full reload” perception came from
route data latency and an empty transition state.

After adding a module-level authenticated-user request cache, navigation
reported zero additional `/auth/me` requests on all measured transitions.
Warm usable times were:

```text
Data     131 ms
Research 967 ms
Reports  95 ms
Overview 922 ms
```

Cold usable times were `Data 481 ms`, `Research 991 ms`, `Reports 1659 ms`
and `Overview 952 ms` on the current dev runtime. Project navigation now
prefetches sibling routes on pointer/focus intent. Segment-level Next
`loading.tsx` boundaries show the same product shell hierarchy and preserve a
truthful “正在保留当前研究上下文…” transition state instead of a blank
document.

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

## 2026-08-29 authenticated API campaign and Dataset-list repair

A 25-sample authenticated same-stack campaign against the live API measured
bounded read paths separately from scientific execution:

| API projection | Samples | p50 | p95 | Max | Mean payload |
| --- | ---: | ---: | ---: | ---: | ---: |
| Projects | 25 | 28.5 ms | 48.0 ms | 238.2 ms | 3,253 B |
| Datasets (pre-repair live process) | 25 | 908.4 ms | 936.9 ms | 1,038.0 ms | 5,258 B |
| Global search | 25 | 20.3 ms | 45.3 ms | 73.5 ms | 40 B |
| Scientific Objects | 25 | 14.9 ms | 17.5 ms | 18.7 ms | 1,588 B |
| Project History | 25 | 155.1 ms | 175.3 ms | 308.1 ms | 13,649 B |
| Scientific Reports | 25 | 20.6 ms | 31.2 ms | 41.2 ms | 836 B |

The Dataset projection was the only clear outlier. Query instrumentation
proved that the durable listing performed one Dataset query per Project and
one Profile query per Dataset. For the current 129 Dataset records this
produced 265 SQL statements per request.

The read path now batch-loads Projects, Datasets, and Profiles in three
deterministic queries, retaining the same Dataset count and selecting the same
latest Profile by `(createdAt, profileId)`. Direct current-worktree measurement
against the same PostgreSQL authority reports:

```text
old: 129 rows, SQL 265, p50 312.0 ms, p95 324.6 ms
new: 129 rows, SQL   3, p50  19.7 ms, p95  20.5 ms
```

Focused deterministic coverage verifies that no per-Project Dataset or
per-Dataset Profile lookup is used and that hidden-project rows remain
excluded. The existing browser-facing API was intentionally not restarted
during this measurement, so its 25-sample Dataset row remains the honest
pre-reload baseline.

This closes the demonstrated Dataset-list N+1 defect. Browser cold/warm
navigation, first-progress/cancel, Viewer usable time, mobile, render counts,
request duplication, and p95 user-interaction qualification remain open;
overall R6 therefore remains `PARTIAL`.

## 2026-08-30 current-worktree browser matrix

The existing Chromium performance harness was rerun against the live
PostgreSQL/Redis/MinIO/worker stack using the repository-provided Chromium
binary. The harness now waits one 250 ms render-settle window after each
route's primary ready marker before measuring usable time; this prevents an
asynchronous long evidence identifier from being recorded as final layout
overflow.

Current warm p50/p95 usable times (milliseconds) and maximum overflow:

| Route | Desktop p50/p95 | Mobile p50/p95 | max overflow |
| --- | ---: | ---: | ---: |
| Data | 1,144 / 1,253 | 1,077 / 1,141 | 0 px |
| Research | 1,275 / 1,438 | 1,224 / 1,272 | 0 px |
| Viewer | 1,197 / 1,251 | N/A | 0 px |
| Report | 969 / 1,173 | 867 / 887 | 0 px |
| Tasks | 1,144 / 1,939 | N/A | 0 px |
| Notifications | 1,079 / 1,249 | N/A | 0 px |

The largest bounded payload was approximately 2.57 MB (Viewer); the Research
route made at most 28 requests in a warm sample and all measured routes had
zero page errors and zero critical 5xx responses. The previous mobile Report
30 px transient overflow is closed by making Evidence grid items shrinkable
and long identifiers breakable. This is current evidence for the R6 layout/
fluency slice; p95 research-submit acknowledgement, cancellation timing and
provider-scale context campaigns remain open.

## 2026-08-30 App Router transition feedback

The persistent root-layout transition indicator was observed on every route
change in a controlled 600 ms RSC-delay diagnostic. It appears immediately
while the client navigation is pending and disappears when the new pathname is
committed, so slower route data no longer presents as an unexplained blank
reload.

The project route group now owns a persistent `ProductRouteFrame`; page-level
ProductShell/RequireProductAuth wrappers detect that frame and render content
only. This preserves one global shell DOM node across project navigation while
leaving standalone `/tasks` and `/notifications` routes unchanged. Next
production build passed after wrapping query-aware transition state in
Suspense; all 17 application routes generated successfully.

## 2026-08-30 — Production navigation closure and cache coherence

The final diagnosis separates framework navigation, development compilation
and authoritative data loading. The browser runtime now uses the same-origin
`/api` rewrite instead of sending client requests directly to port `8000`.
Project-navigation intent prewarms bounded Project History and Research
session reads. Both are three-second promise caches that coalesce concurrent
requests and invalidate after related Project, Dataset, ScientificObject,
upload, promotion, run-archive or session mutations; they are not durable
application state.

The route progress affordance waits `180 ms` before appearing. Fast
transitions therefore do not flash a loading banner or displace content;
genuinely slower transitions retain an accessible live status and a
three-pixel mineral-green line.

Authenticated Chromium production evidence used the optimized Next build on
port `3001` while the development service on `3000` remained available:

| Route | Cold usable | Warm usable | document requests | shell preserved |
| --- | ---: | ---: | ---: | --- |
| Data | 59 ms | 34 ms | 0 | YES |
| Research | 372 ms | 43 ms | 0 | YES |
| Reports | 356 ms | 32 ms | 0 | YES |
| Overview | 43 ms | 32 ms | 0 | YES |

Every transition also had zero post-login `/auth/me` requests. Development
post-repair warm times were `113–158 ms`; cold times were `102–945 ms`,
matching first compilation/data hydration rather than a document reload.

Real in-app-browser review at `390x844` verified Data, Research and Reports:

```text
global horizontal overflow = 0
duplicate DOM IDs on Reports = 0
project navigation retained = YES
scientific table reachable = YES
Research timeline reachable = YES
Report filters and rows reachable = YES
```

The scoped senior-design checklist passed the applicable typography,
hierarchy, single-accent, grid, responsive, state, motion, reduced-motion,
anti-gradient, anti-card-wall and product-specific-copy checks. Onboarding and
SwiftUI-only checks were not applicable. The interface remains the frozen dense
scientific workbench rather than a generic dashboard.
## 2026-08-30 persistent product-shell navigation batch

The project-scoped product routes now share a root `ProductRouteFrame`, so
Project, Task Center and Notification Center transitions retain the same
global context bar instead of rebuilding the entire page shell. The landing
login return path uses `router.replace`; internal navigation remains inside
the Next App Router authority.

Task Center and Notification Center now consume one bounded shared task feed
with a 15-second TTL and in-flight request coalescing. ProductShell prefetches
both destination routes and that feed; each destination still invalidates or
refetches through the shared authority after an explicit refresh rather than
hand-mutating multiple caches.

Authenticated browser measurements:

```text
Project → Tasks = 504 ms
document requests = 0
RSC requests = 1
ProductShell DOM identity preserved = YES

Tasks → Notifications, cold development compile = 2550 ms
document requests = 0
RSC requests = 1
duplicate project/job-list API requests = 0

Notifications → Tasks, browser history = 54 ms
Tasks → Project, browser history = 26 ms
document requests = 0
```

The `2550 ms` transition is a cold Next development compilation cost, not a
document reload. Warm history transitions are interaction-class. The final
focused frontend rerun is `7 files / 52 tests passed`; typecheck and
diff-check pass. A production-build route timing and final desktop/mobile
visual campaign remain open, so the broad product-fluency verdict remains
`PARTIAL`.

## 2026-08-31 — current-worktree navigation and responsive requalification

The authenticated navigation probe was rerun after the current Project History
status repair. Across Overview, Data, Research and Reports, every transition
used one RSC request and zero document requests. The global product shell DOM,
its qualification marker and the authenticated session remained mounted.

| Surface | cold URL / usable | warm URL / usable |
| --- | ---: | ---: |
| Data | 166 / 513 ms | 95 / 108 ms |
| Research | 181 / 1,043 ms | 115 / 946 ms |
| Reports | 139 / 446 ms | 110 / 121 ms |
| Overview | 104 / 1,449 ms | 108 / 929 ms |

The slower observations made while source files were being edited were traced
to Next development Fast Refresh rebuilding or performing its documented
development-only reload. They were not product navigation document requests.

The complete independent page-load matrix then sampled each route once cold
and five times warm:

| Route | Desktop warm p50/p95 | Mobile warm p50/p95 | max overflow |
| --- | ---: | ---: | ---: |
| Data | 899 / 958 ms | 873 / 948 ms | 0 px |
| Research | 1,849 / 2,276 ms | 1,741 / 2,178 ms | 0 px |
| Viewer | 1,623 / 1,672 ms | N/A | 0 px |
| Report | 869 / 901 ms | 854 / 903 ms | 0 px |
| Tasks | 1,382 / 1,880 ms | N/A | 0 px |
| Notifications | 1,114 / 1,173 ms | N/A | 0 px |

All samples recorded zero browser errors and zero critical 5xx responses. The
Research route remains the largest interaction target because it restores the
timeline, exact Result/Presentation and workbench state; it is bounded but
remains the primary further performance-optimization candidate.

## 2026-08-31 — post-table-repair same-stack baseline

The current worktree was measured again with authenticated Chromium against the
live PostgreSQL/Redis/MinIO stack. App Router transitions retained the shell and
recorded `documentRequests=0` throughout; warm route usability was Data
`192 ms`, Research `254 ms`, Reports `139 ms`, and Overview `188 ms`.
Independent page-load sampling remained bounded with zero overflow:

| Route | Desktop warm p50/p95 | Mobile warm p50/p95 |
| --- | ---: | ---: |
| Data | 2,139 / 5,184 ms | 1,462 / 1,490 ms |
| Research | 1,866 / 1,931 ms | 1,874 / 1,901 ms |
| Viewer | 1,499 / 1,541 ms | N/A |
| Report | 850 / 1,403 ms | 844 / 856 ms |
| Tasks | 1,124 / 1,323 ms | N/A |
| Notifications | 1,193 / 1,445 ms | N/A |

The isolated reports run also observed no critical responses or page errors.
The only browser console message was the expected bootstrap `401` from the
isolated authentication probe. The Data table's `400px` internal content width
is intentionally bounded by its `390px` scroll region and does not contribute
to page-level overflow.

## 2026-09-01 — immutable production navigation and destination continuity

The current immutable production build on port `3008` supersedes the earlier
development/HMR navigation timings. Across two complete
Overview/Data/Research/Reports cycles:

| Viewport | cold usable | warm usable | document reloads |
| --- | ---: | ---: | ---: |
| `1280x720` | `61–118 ms` | `33–70 ms` | `0` |
| `390x844` | `66–102 ms` | `41–68 ms` | `0` |

Every transition preserved the exact ProductShell DOM node and authenticated
session. The shared navigation provider now owns App Router prefetch, while
ProductShell only warms bounded domain reads; this removes the duplicate eager
route-prefetch campaign without changing data freshness.

Route continuity now also resets document scroll only when the pathname
changes. Query-only ResearchTurn navigation retains its workbench scroll
owner, while navigation from a deeply scrolled Reports list opens the report
at `scrollY=0` beneath the global/project context bars. The authenticated
report check had one main landmark, one labelled report-reader region, no
duplicate IDs and no global overflow.

## 2026-09-01 — final current-code production navigation batch

The current worktree was rebuilt into the isolated production directory
`.next-prod-phase14r-release` and served on `3013`, proxied to the same-stack
API on `8005`. PostgreSQL, Redis, MinIO, six Redis workers and the configured
DeepSeek provider remained active throughout the measurement. This avoids
classifying Next development compilation or Fast Refresh latency as product
navigation latency.

Two complete authenticated Overview/Data/Research/Reports cycles produced:

| Viewport | cold usable range | warm usable range | document requests |
| --- | ---: | ---: | ---: |
| `1280x720` | `79–135 ms` | `47–62 ms` | `0` |
| `390x844` | `60–152 ms` | `46–67 ms` | `0` |

Every transition preserved:

```text
ProductShell DOM marker = YES
single ProductShell instance = YES
authenticated session = YES
full-document reload = NO
duplicate /auth/me request = NO
```

The small number of RSC requests occurred only where the destination required
server data; they did not replace the document. The production build itself
passed with a shared first-load bundle of `104 kB`; Project/Data/Report shell
routes remained `132–148 kB`, while the deliberately heavier Research
workbench was `181 kB`.

This current-code production batch closes the previously open navigation and
mobile transition evidence. Long scientific computation remains governed by
truthful persisted progress and is intentionally evaluated separately from
page transition latency.

### Independent production route readiness

The same immutable production build was then measured in fresh browser
contexts with one cold and five warm samples per route:

| Surface | desktop warm p50 / p95 | mobile warm p50 / p95 | max overflow |
| --- | ---: | ---: | ---: |
| Data | `1,123 / 1,248 ms` | `1,041 / 1,085 ms` | `0 px` |
| Research | `1,210 / 1,304 ms` | `1,306 / 1,382 ms` | `0 px` |
| Structure Viewer | `1,082 / 1,183 ms` | qualified through the bounded mobile handoff campaign | `0 px` |
| Scientific Report | `401 / 448 ms` | `385 / 658 ms` | `0 px` |
| Task Center | `1,335 / 2,586 ms` | bounded responsive surface verified separately | `0 px` |
| Notification Center | `1,326 / 1,486 ms` | bounded responsive surface verified separately | `0 px` |

All samples recorded:

```text
browser/page errors = 0
critical HTTP 5xx = 0
global horizontal overflow = 0
```

The Task Center p95 remains the slowest independent cold-context read because
it reconstructs the authorized persisted task window. Normal in-product
navigation does not pay that cost: the shared ProductShell feed and App Router
transition remain in the `47–67 ms` warm range. The retained bounded
30-record window, request coalescing and explicit refresh preserve truthful
state without an unbounded preload.

## 2026-09-04 current-worktree production build and feed projection

The current worktree was rebuilt into isolated production directories without
overwriting the still-running validation instances. The latest build
`.next-phase14r-0904e` is served on `127.0.0.1:3023` and proxies the same-stack
API on `127.0.0.1:8005`.

```text
shared first-load JS = 104 kB
Data / Project shell = 151 kB
Research workbench = 183 kB
Report reader = 148 kB
Task Center = 130 kB
Notification Center = 128 kB
production build = PASS
```

The task/notification feed now uses one bounded cross-project API projection
instead of issuing one client request per project. Backend regression confirms
that both one-Job and five-Job samples use two SQL statements. The feed
projects the persisted Research question and update time, so researchers can
recognize and search their work without opening technical IDs.

This closes the demonstrated N+1 and generic-title fluency seams. Provider-scale
submit/cancel p95 and long-duration recovery campaigns remain separate open
Phase 14-R acceptance work.
