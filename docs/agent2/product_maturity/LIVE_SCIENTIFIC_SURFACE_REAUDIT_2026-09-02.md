# Live Scientific Surface Re-audit — 2026-09-02

This is a fresh same-stack browser re-audit after the frontend runtime/asset
correction. It supplements the earlier payload-availability evidence and does
not change ScientificObject, ScientificObjectVersion, ScientificResult,
Artifact or Report authority.

## Runtime

```text
frontend primary = http://127.0.0.1:3013
frontend compatibility = http://127.0.0.1:3000 -> 3013
API = http://127.0.0.1:8005
PostgreSQL = 127.0.0.1:55434/mdi
Redis = 127.0.0.1:6379/13
MinIO = 127.0.0.1:9000 / mdi-artifacts
workers = 6 Redis-backed workers
provider = DeepSeek / deepseek-v4-flash
```

`GET /health/runtime` returned `200` with:

```text
database.backend = postgresql
redis.backend = redis
artifactStorage.backend = minio
worker.backend = redis
llmProvider.configured = true
```

The explicit same-stack operations snapshot also returned `status = ok`,
`idleInTransaction = 0`, `pool.checkedOut = 0`, `staleActiveResearchTurns = 0`,
`staleJobs = 0`, `totalQueued = 0`, and six idle workers.

## Browser evidence

All checks used the authenticated acceptance user in the in-app browser. The
existing user tab was claimed and marked for handoff; no service or tab was
closed.

| Surface | Fresh evidence |
| --- | --- |
| Project data landing pages | 16/16 opened without Internal Server Error |
| Exact Dataset/object detail links | 41/41 resolved; no `SOURCE_MISSING`, unavailable-payload message or 5xx |
| Verified scientific reports | 10/10 detail routes rendered |
| Report-referenced exact Viewers | 10/10 rendered; Structure/trajectory routes had a real canvas, table routes had a real table |
| Compatibility entry `:3000` | trajectory Viewer rendered with canvas and no browser errors |
| Legacy `job_*` Report entry | rendered directly through the compatibility reader; no speculative modern-report 404 and no browser error |
| Browser console | no error/warn entries on the sampled routes |
| Page overflow | no global overflow observed on the current tested routes |

Representative exact identities:

```text
Dataset object = 8a425466-b697-4c85-9a43-199414a22865
Dataset version = be02266a-7d4f-4ebb-9f28-3132855167d0
Trajectory object = d325a090-d53f-4980-8a5e-c466bf6470eb
Trajectory version = 052d3a8e-8a35-48ac-9e65-b95a86b42c99
```

The trajectory Viewer displayed three frames, playback controls, atom
selection/measurement controls, bounded supercell controls, source metadata and
a rendered canvas. The Dataset Viewer displayed the three stable rows
`mat-1`, `mat-2`, and `mat-3` with `band_gap` values.

The historical Dataset run
`job_agent2_92fcd73e38034dcfbc7aa63fbcf2a70e` now opens directly into its
read-only legacy report route. Its persisted scientific result eventually
loaded with no Internal Server Error, and the browser captured no error/warn
entries. This verifies the P1 route fix for legacy report references.

The responsive table audit also found and repaired a mobile affordance gap:
scientific tables already had an internal horizontal scroll region, but the
existing `.workspace-table-mobile-hint` was hidden by the mobile stylesheet.
The hint now remains available in the mobile breakpoint, explaining that
complete typed attributes are horizontally scrollable while stable sample
identity and selection controls remain fixed.

## Report and historical routes

All ten verified Report detail pages rendered their title, methods, findings,
limitations, exact source-version metadata and evidence/report controls. The
historical-run routes also rendered their bounded legacy report contract without
an Internal Server Error. A report may intentionally show a scientific surface
as `当前不可用` when that particular run did not persist that optional output;
this is a truthful bounded limitation, not a service outage or replacement
version.

## Classification of the supplied unavailable-payload screenshots

No current acceptance-user route reproduced either screenshot after the exact
current build was started and the `:3000` compatibility alias was repointed.
The earlier failure was stale frontend/runtime/build state and, for some
historical/test records, an absent payload reference. Current acceptance-owned
Dataset and Viewer routes are readable; synthetic service-test placeholder
versions remain intentionally fail-closed and are not fabricated.

```text
CURRENT_SERVICE_OUTAGE = NO
CURRENT_ACCEPTANCE_VISIBLE_ISE = 0
CURRENT_ACCEPTANCE_VISIBLE_SOURCE_MISSING = 0
CURRENT_ACCEPTANCE_ROUTE_ERRORS = 0
MOBILE_TABLE_SCROLL_AFFORDANCE = FIXED
```

## Validation commands

```text
phase14r-runtime-static-assets.mjs = PASS
phase14r_operations_snapshot.py --same-stack --fail-on-attention = PASS
frontend focused UI regression (WorkspaceArtifactGallery +
ScientificWorkspaceShell + ScientificReportRoute) = 53 passed
frontend full regression = 108 files / 789 tests passed
production build = PASS
compileall = PASS
typecheck = PASS
git diff --check = PASS
```

The only implementation changes in this continuation were the bounded legacy
Report route correction and the mobile table scroll affordance. Existing
unrelated worktree modifications and user-owned evidence remain preserved.

The follow-up visual audit found one additional shared styling defect: report
and trash lifecycle filters were inheriting the global primary-button style.
The shared `.product-filter-row` contract now renders only the active filter as
accent-filled while inactive filters use outlined pills; mobile controls retain
44px touch targets. The refreshed Report screenshot confirms the four filters
are visually classified as filters rather than competing primary actions.

The same browser session also exercised a warm in-project transition from
Reports to Data through the shared product navigation. The destination was the
project-scoped Data route with no console errors or authorization failure; no
manual ID construction or hard browser-back dependency was required.

## Report Artifact inline preview

Modern report Figure/Table entries now include an explicit, on-demand
read-only preview backed by the existing persisted Artifact content endpoint.
The preview is bounded (Figure finite-series SVG projection; Table at most 24
rows and 8 columns), keeps the full authoritative Artifact link, and never
creates a Job, ToolCall, Artifact or ScientificResult.

Authenticated same-stack browser verification on
`agent2_report_19a0d0c261c28577101de81532464893` produced:

```text
Figure preview = 2 finite persisted points
Table preview = 1 persisted row / 8 typed columns
browser error/warn logs = []
```

The failed-read branch remains explicit and fail-closed; it does not render a
false-success scientific preview.
## Scientific Viewer unavailable-state recovery

The exact-version Scientific Object Viewer now exposes a bounded retry action
and a project-scoped source/metadata route when the viewer projection fails or
returns `SOURCE_MISSING`. The retry re-reads the existing authoritative
object/version projection only; it never selects a newer version or starts a
scientific Job. Focused browser simulation on the current production build
verified both controls in the 390x844 layout, while the healthy Dataset route
continues to render the exact `mat-1`, `mat-2`, and `mat-3` rows.

## Current authenticated route sweep (2026-09-02)

Using the current production frontend on `127.0.0.1:3017`, the existing
authenticated acceptance cookie, and the user-provided Chromium executable,
the current browser-facing product surface was re-swept:

```text
projects discovered = 16
routes visited = 52
Internal Server Error = 0
Application error = 0
ChunkLoadError = 0
unavailable-payload text = 0
console/page errors = 0
```

The sweep covered the project catalog, task center, notification center,
trash, and each discovered project overview plus its Data, Research, and
Reports routes. This is current-runtime evidence that the supplied error
screenshots are not reproducing on the active same-stack acceptance surface.
Historical records whose original MinIO bytes are genuinely absent remain
typed, fail-closed states and are not counted as recovered scientific payloads.

## Persisted Plotly Figure/Table projection (2026-09-02)

The authenticated Report `agent2_report_e54681009a0e49abe371247d9053ce61`
exposed a real presentation-layer mismatch: persisted Plotly Figures use
`data[]`, while the inline preview only read the internal `series[]` shape;
MSD/diffusion Table Artifacts likewise use typed scientific arrays and nested
fit structures rather than a generic `rows[]` field. The preview now projects
both declared persisted shapes deterministically:

```text
Plotly Figure traces      = 2 SVG previews
MSD/diffusion tables      = 2 typed table previews
empty preview panels      = 0
Internal Server Error      = 0
Artifact read failures    = 0
console/page errors        = 0
```

The projection is read-only and bounded. It preserves the exact Artifact
content and source provenance and does not run a Tool or create scientific
records. Focused component coverage is now `5 passed`.

## Report Figure layout correction (2026-09-02)

The first visual review of the real Plotly preview exposed a CSS grid-placement
defect: the preview component was auto-placed into the narrow figure index
column, so a valid SVG appeared as a thin vertical strip with excessive empty
space. The shared report figure layout now pins the preview to the content
column and preserves bounded width.

Current production-build browser checks:

```text
1280x720: document/body width 1280/1280, SVG 2, tables 2, empty previews 0
390x844:  document/body width 390/390,  SVG 2, tables 2, empty previews 0
console/page errors: 0
```

This is a presentation-only layout repair; Artifact content, exact source
identity and no-recompute behavior are unchanged.
