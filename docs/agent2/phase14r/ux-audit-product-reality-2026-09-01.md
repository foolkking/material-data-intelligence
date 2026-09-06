# UX audit — Material Data Intelligence product reality

## 1. Scope and evidence base

This is a whole-product audit of the current local production frontend at
`http://127.0.0.1:3013`, for an expert/mixed materials-research audience in a
high-trust scientific context. It is an audit only: no product implementation,
data mutation, service shutdown, or browser-tab closure was performed.

Observed live on September 1, 2026:

- unauthenticated landing and protected-route login handoff;
- authenticated Projects, Project Overview, Data, Dataset detail, Table Viewer,
  Structure Viewer, Research index/completed/missing-payload states, Reports,
  current Report, legacy run Report, Tasks, Notifications, Trash, model
  settings, Console, legacy Analysis route, and Global Search;
- desktop `1280×720` and mobile `390×844`;
- 42 full-page screenshots;
- route metrics for global overflow, internal horizontal scrolling, duplicate
  IDs, broken ARIA references, and browser/network errors;
- App Router continuity across Project → Data → Research → Reports → Tasks →
  Notifications: shell marker preserved and document requests stayed at `0`.

Primary machine evidence:

- `docs/agent2/phase14r/evidence/product_reality_browser_audit_2026-09-01.json`
- `docs/agent2/phase14r/evidence/product_reality_before_2026-09-01/`

Limitations:

- one acceptance researcher and one populated project were sampled;
- no destructive lifecycle action was executed;
- screen-reader speech output, 200% zoom, forced colors, and real slow-network
  throttling were not included in this pass;
- timing figures below are local same-machine observations, not production p95.

## 2. Executive summary

The current product is substantially more coherent than its historical pages:
the shared shell survives route transitions, the Data and Viewer mobile
transformations avoid global overflow, current Reports preserve exact
provenance, and the scientific surfaces inspected did render real content.
The largest maturity problem is now information volume and state quality, not
missing architecture. Project, Report, Search, Task, Notification, and Research
surfaces expose too much ungrouped test/history material and too many technical
identities at once. Two state defects remain especially trust-sensitive:
Research can briefly say that no result is available before the real result
arrives, and the legacy Report route issues a malformed double-`/api` request.
Task and Notification centers take roughly six seconds to replace generic
loading copy with useful content. Mobile preserves functionality but removes
project identity from the global header and relies heavily on long internal
scroll areas. No global horizontal overflow, duplicate DOM IDs, broken ARIA
references, or current 500/Internal Server Error responses were observed in the
42-screen campaign.

## 3. Quick wins

1. Fix the legacy Report request from `/api/api/scientific-reports/...` to the
   single proxy prefix.
2. Replace the transient “当前没有可展示的结果” with a neutral
   “正在解析已持久化结果” state until resolution is terminal.
3. Add a visible Project identifier/name to the mobile shell.
4. Hide “技术身份” and raw UUIDs behind technical-detail disclosures.
5. Make Trash reachable from a visible lifecycle-management destination, not
   only the account menu.
6. Disable “保存当前搜索” until a query or non-default filter exists.
7. Add a visible horizontal-scroll affordance and sticky identity column to
   mobile scientific tables.
8. Collapse or paginate historical Reports and repetitive Research messages.

## 4. Route-by-route product reality

| Surface | Desktop evidence | Mobile evidence | Observed product issue |
|---|---|---|---|
| Landing / login | `1280x720_unauth_landing.png` | `390x844_unauth_landing.png` | Clear product explanation and return-to login; mobile page is 3,228 px tall before the final CTA. |
| Projects | `1280x720_projects.png` | `390x844_projects.png` | 16 projects include acceptance and technical fixture names in the default active list; repeated subtitles provide little differentiation. |
| Project overview | `1280x720_project.png` | `390x844_project.png` | Recent research is visible, but mixed completed/failed records are undifferentiated beyond status text and repeat similar titles. |
| Data | `1280x720_data.png` | `390x844_data.png` | Desktop has a narrow dense source rail; the same scientific identity is represented in separate Dataset and Scientific Object lists without explaining the relationship. |
| Dataset detail | `1280x720_dataset_detail.png` | `390x844_dataset_detail.png` | Separate legacy-style “数据工作台” exposes Provider/Profile/Plan terminology and duplicates the modern Data → Research path. |
| Table Viewer | `1280x720_viewer_table.png` | `390x844_viewer_table.png` | Real table content loads by ~1.5 s and preserves sample identity; mobile needs an explicit overflow cue when larger schemas exceed the viewport. |
| Structure Viewer | `1280x720_viewer_structure.png` | `390x844_viewer_structure.png` | Real 3D content loads by ~1.5 s; raw lattice precision and many controls compete with the scientific summary. |
| Research | `1280x720_research_index.png` | `390x844_research_index.png` | Repeated re-interpretation messages dominate the timeline; mobile composer and internal timeline split leave little simultaneous reading space. |
| Missing-payload Research | `1280x720_research_payload_missing.png` | `390x844_research_payload_missing.png` | At 3 s mobile briefly states no result is displayable; by 6 s the authoritative diffusion result is present. |
| Reports index | `1280x720_reports.png` | `390x844_reports.png` | 11 current Reports plus 33 historical runs render as one 5,513/7,558 px list with no search, pagination, or collapsed history. |
| Current Report | `1280x720_report_good.png` | `390x844_report_good.png` | Strong scientific structure, but exact UUIDs dominate primary prose and the mobile chapter strip truncates without an overflow cue. |
| Legacy run Report | `1280x720_report_payload_missing.png` | `390x844_report_payload_missing.png` | Content eventually renders, but duplicate headings and a wide MSD table reduce scanability; one malformed Report API request returns 404. |
| Tasks | `1280x720_tasks.png` | `390x844_tasks.png` | Useful persisted state appears around 6 s; before that two generic loading labels occupy the page. |
| Notifications | `1280x720_notifications.png` | `390x844_notifications.png` | Same ~6 s generic loading; no page-level `h1` was found in the rendered DOM. |
| Trash | `1280x720_trash.png` | `390x844_trash.png` | Good retention explanation and empty state, but no visible top-level route from Notifications/Tasks; route is account-menu dependent. |
| Model settings | `1280x720_settings_models.png` | `390x844_settings_models.png` | Direct route opens a modal over Console, so the URL identifies settings while the background document still reads as Console. |
| Console | `1280x720_console.png` | `390x844_console.png` | Useful return point, but no page-level `h1` was found in the sampled rendered DOM. |
| Legacy Analysis | `1280x720_analysis_legacy.png` | `390x844_analysis_legacy.png` | Honest “历史链接暂时无法解析” state, but only “查看项目” is offered; no contextual recovery to likely Project/Research. |
| Global Search | `1280x720_global_search_overlay.png` | `390x844_global_search_overlay.png` | Blank query returns “至少 140 项” and 40 rows, many titled only `ScientificResult <id>`; save action remains available for the default query. |

## 5. Findings

### Feedback, status, and recovery

#### STATE-01 · Research publishes a false empty-result state during resolution

| | |
|---|---|
| **Severity** | **High** |
| **Confidence** | Observed (live browser + timed samples) |
| **Location** | missing-payload Research route, mobile `390×844` |
| **Effort** | S |

At 3 seconds the Workbench rendered “当前没有可展示的结果” and a generic
fallback finding. At 6 seconds the same route rendered the persisted diffusion
result with four scientific outputs, R², α, and the bounded diffusion
coefficient. A researcher can interpret the first statement as scientific data
loss. Keep the state neutral until resolution is terminal; reserve “no result”
for an authoritative empty response.

#### STATE-02 · Task and Notification centers withhold useful state for ~6 seconds

| | |
|---|---|
| **Severity** | **High** |
| **Confidence** | Observed (live browser + timed samples) |
| **Location** | `/tasks`, `/notifications`, both viewports |
| **Effort** | M |

At 0.5, 1.5, and 3 seconds both pages still showed paired generic loading
messages. Persisted counts and rows appeared around 6 seconds. These are the
surfaces users visit to regain control of long-running work, so a blank wait
undermines the recovery promise. Render cached summary counts or skeleton rows
immediately, then reconcile with current state.

#### STATE-03 · Legacy Report emits a malformed API request

| | |
|---|---|
| **Severity** | **Medium** |
| **Confidence** | Observed (network) |
| **Location** | `/projects/project_0002_1a0af866391f412d/reports/job_dc63f3f5d57742009c6be09e` |
| **Effort** | S |

Both desktop and mobile issued `GET
/api/api/scientific-reports/job_dc63f3f5d57742009c6be09e` and received 404.
The fallback run projection eventually rendered, but the route creates a
console error and leaves its durable Report relationship unresolved. Normalize
the client path so the shared `/api` base is applied once.

### Navigation and information architecture

#### NAV-01 · Mobile shell removes the current Project identity

| | |
|---|---|
| **Severity** | **High** |
| **Confidence** | Observed (rendered) |
| **Location** | all authenticated mobile project routes |
| **Effort** | M |

The desktop shell shows “项目 · Phase 13 Structure Browser Qualification”; the
mobile shell shows only `M`, Tasks, Notifications, Search, and the account
avatar. A researcher moving among Data, Research, and Reports cannot confirm
which Project owns the evidence without reading page content. Preserve a
compact, truncatable Project label or a project switcher in the mobile shell.

#### NAV-02 · Trash is product-critical but account-menu dependent

| | |
|---|---|
| **Severity** | **High** |
| **Confidence** | Observed (navigation campaign) |
| **Location** | global shell; transition from `/notifications` |
| **Effort** | S |

Direct `/trash` works and explains retention well, but no visible Trash link was
available in the shell/navigation sequence from Notifications; it is hidden in
the account menu. Lifecycle recovery is not an account setting. Add a visible
Content/Trash entry near Projects or expose it consistently from lifecycle
filters.

#### NAV-03 · Two Data mental models are presented without explaining their relation

| | |
|---|---|
| **Severity** | **High** |
| **Confidence** | Observed (rendered) |
| **Location** | Project Data page |
| **Effort** | M |

The page lists upload-oriented Datasets and then a separate “科研对象” list,
often with the same name. Nothing in the primary UI explains whether these are
duplicates, versions, derived objects, or alternate entry points. Add explicit
labels such as “Sources” and “Scientific objects derived from sources,” and
surface the relationship on selection.

#### NAV-04 · Dataset detail is a legacy parallel research surface

| | |
|---|---|
| **Severity** | **High** |
| **Confidence** | Observed (rendered) |
| **Location** | `/projects/.../datasets/dataset_0001_441637edf69740aa` |
| **Effort** | L |

The page exposes “DeepSeek / deepseek-v4-flash,” “Profile ID,” Plan chunks,
queue audit, and its own “创建并运行” flow, while the current product direction
uses Data → Research Timeline/Workbench. This teaches two competing execution
models. Keep dataset diagnostics, but route new scientific requests into the
authoritative Research surface.

#### NAV-05 · Legacy Analysis recovery is too generic

| | |
|---|---|
| **Severity** | **Medium** |
| **Confidence** | Observed (rendered) |
| **Location** | `/analysis` |
| **Effort** | S |

“历史链接暂时无法解析” is honest, but “查看项目” discards all known context.
Offer the nearest recoverable Project/History destination when identifiers can
be resolved, and expose a search action when they cannot.

### Search and organization

#### SEARCH-01 · Blank global search starts with 140+ undifferentiated results

| | |
|---|---|
| **Severity** | **High** |
| **Confidence** | Observed (rendered) |
| **Location** | Global Search overlay |
| **Effort** | M |

Opening search with no query immediately reports “至少找到 140 项，显示前 40
项.” Many rows are raw `ScientificResult <short-id>` records. The first
interaction is therefore inventory scanning rather than finding. Default to
recent/pinned work or require a query; provide Project scope and human-readable
Result titles/snippets.

#### SEARCH-02 · The default empty search can be saved

| | |
|---|---|
| **Severity** | **Medium** |
| **Confidence** | Observed (rendered) |
| **Location** | Global Search overlay |
| **Effort** | S |

“保存当前搜索” is enabled while the query is empty and all filters are default.
This can create meaningless saved searches and later noise. Disable it until a
query or non-default filter exists, and preview the saved criteria.

#### ORG-01 · Acceptance fixtures occupy the normal Project workspace

| | |
|---|---|
| **Severity** | **High** |
| **Confidence** | Observed (rendered) |
| **Location** | `/projects` |
| **Effort** | M |

The 16-item current Project list includes `project_capability_*`,
`project_intent_*`, `Input transport regression`, and phase qualification
projects beside user-named work. The product looks like an internal test
console and makes real projects harder to find. Segregate qualification data
into a non-user workspace or provide a default collection that excludes it.

### Density, hierarchy, and scientific data display

#### LAYOUT-01 · Reports index renders 44 records as one uninterrupted page

| | |
|---|---|
| **Severity** | **High** |
| **Confidence** | Observed (measured + rendered) |
| **Location** | Project Reports |
| **Effort** | M |

Eleven verified Reports and 33 historical runs produce a 5,513 px desktop page
and a 7,558 px mobile page. Current Reports and recoverable runs are visually
similar, so the user must scroll through an audit ledger to find communication
artifacts. Collapse history by default and add search/filter/pagination.

#### LAYOUT-02 · Repeated reinterpretations dominate the Research Timeline

| | |
|---|---|
| **Severity** | **Medium** |
| **Confidence** | Observed (rendered) |
| **Location** | Research index |
| **Effort** | M |

The visible recent conversation contains several near-identical
“请重新解释这份科学结果…” turns and answers with the same diffusion numbers.
Group reinterpretations under the reused Result or show a branch/revision
summary so new work remains scannable.

#### DATA-01 · Mobile legacy scientific table hides columns without a cue

| | |
|---|---|
| **Severity** | **High** |
| **Confidence** | Observed (rendered + measured internal scroller) |
| **Location** | legacy MSD Report, mobile |
| **Effort** | M |

The wide MSD table is bounded, but x/y/z and time-origin columns extend beyond
the viewport and there is no visible “swipe for more columns” cue or sticky row
identity. A researcher can read the visible total MSD as the complete table.
Add an overflow affordance, sticky lag-time/selection column, and a compact
column chooser.

#### DATA-02 · Exact UUIDs overpower the current Report narrative

| | |
|---|---|
| **Severity** | **Medium** |
| **Confidence** | Observed (rendered) |
| **Location** | current `mat-2 band_gap` Report |
| **Effort** | S |

The exact Dataset version UUID is repeated in the question, narrative, source
card, finding, and conclusion. Exact provenance must remain available, but
repetition interrupts scientific reading. Use “版本 1” or a short checksum in
primary prose and keep the full UUID in the evidence/provenance disclosure.

#### DATA-03 · Legacy Report duplicates primary headings

| | |
|---|---|
| **Severity** | **Medium** |
| **Confidence** | Observed (rendered) |
| **Location** | legacy MSD Report |
| **Effort** | S |

“主要结果” and “均方位移（MSD）” each appear twice before the data. This makes
the hierarchy look like a projection bug and weakens heading navigation.
Deduplicate the wrapper and Result renderer headings.

#### DATA-04 · Mobile Report chapter navigation truncates silently

| | |
|---|---|
| **Severity** | **Medium** |
| **Confidence** | Observed (rendered + measured internal scroller) |
| **Location** | current Report, mobile |
| **Effort** | S |

The chapter row is horizontally scrollable and cuts off later chapter labels
without a fade, chevron, or active-position cue. Add deliberate overflow
signaling or use a compact section dropdown on narrow screens.

### Content and terminology

#### CONTENT-01 · “技术身份” is normal-user primary content

| | |
|---|---|
| **Severity** | **Medium** |
| **Confidence** | Observed (rendered) |
| **Location** | Tasks and Notifications |
| **Effort** | S |

Task and notification rows repeatedly expose “技术身份” beside status and
actions. It does not help a researcher decide what happened or what to do.
Move IDs and correlation metadata into a technical-details disclosure.

#### CONTENT-02 · Project rows do not help distinguish projects

| | |
|---|---|
| **Severity** | **Medium** |
| **Confidence** | Observed (rendered) |
| **Location** | `/projects` |
| **Effort** | S |

Most rows repeat “查看数据、研究过程与分析报告,” regardless of contents. Replace
that generic subtitle with the most useful differentiators: last activity,
object types/count, owner/role, and active research status.

### Accessibility

#### A11Y-01 · Notifications and Console lack a page-level heading

| | |
|---|---|
| **Severity** | **Medium** |
| **Confidence** | Observed (rendered DOM) |
| **Location** | `/notifications`, `/console` |
| **Effort** | S |

The sampled DOM contained no `h1` on either route, although visible page titles
exist. Heading navigation therefore cannot reliably announce the page boundary.
Promote the visible primary title to one unique `h1`.

## 6. Prioritized backlog

| # | ID | Action | Severity | Effort |
|---|---|---|---|---|
| 1 | STATE-01 | Make Result resolution monotonic; never publish a false empty state | High | S |
| 2 | STATE-02 | Show cached/skeleton Task and Notification state before the ~6 s refresh | High | M |
| 3 | NAV-04 | Retire the parallel Dataset execution UI in favor of Data → Research | High | L |
| 4 | NAV-01 | Preserve current Project identity in the mobile shell | High | M |
| 5 | LAYOUT-01 | Collapse/search/page verified Reports and historical runs | High | M |
| 6 | SEARCH-01 | Replace blank-query 140-item dump with recent/pinned or query-first results | High | M |
| 7 | ORG-01 | Remove qualification fixtures from the normal user workspace | High | M |
| 8 | NAV-03 | Explain Dataset → Scientific Object relationships | High | M |
| 9 | DATA-01 | Add mobile scientific-table overflow affordance and sticky identity | High | M |
| 10 | NAV-02 | Make lifecycle/Trash recovery visibly discoverable | High | S |
| 11 | STATE-03 | Remove the duplicate `/api` prefix on legacy Report lookup | Medium | S |
| 12 | LAYOUT-02 | Group repetitive reinterpretations by reused Result | Medium | M |
| 13 | DATA-02 | Move full UUIDs into provenance disclosures | Medium | S |
| 14 | DATA-03 | Deduplicate legacy Report headings | Medium | S |
| 15 | DATA-04 | Make mobile Report chapter overflow explicit | Medium | S |

## 7. What is working, and what was left alone

**Working well.**

- App Router transitions preserved the shell and produced zero document reloads
  on both target viewports.
- No sampled route had global horizontal overflow.
- No duplicate IDs or broken `aria-controls`/`aria-labelledby`/
  `aria-describedby` references were found.
- Table and Structure Viewers rendered real scientific content by roughly
  1.5 seconds in targeted follow-up checks.
- Current Reports preserve source versions, limitations, evidence, and
  no-recompute language in a coherent scientific hierarchy.
- The mobile Data layout deliberately hides the source rail and keeps the
  selected scientific surface primary.
- Trash explains protected provenance and retention honestly.

**Left alone.** The dense expert-oriented presentation, technical scientific
terms such as R²/MSD, and exact provenance itself were not treated as defects.
The problem is where operational identifiers displace the scientific narrative,
not that expert detail exists.

## 8. Open questions

- Does usage telemetry show that users search by Result ID, or are the raw
  `ScientificResult <id>` titles strictly an internal fallback?
- Are qualification projects expected in a production user workspace, or is
  this acceptance account intentionally shared with test automation?
- Can Task/Notification summaries be safely cached per user to eliminate the
  six-second empty wait?
- Should Dataset detail remain a supported execution surface, or is it a legacy
  compatibility route that should become read-only?
- Screen-reader, 200% zoom, forced-colors, and interrupted-network recovery
  remain to be sampled before making a WCAG conformance claim.

## Appendix — evidence log

### Seen

- 21 desktop screenshots at `1280×720`;
- 21 mobile screenshots at `390×844`;
- login handoff preserved `returnTo=/projects`;
- populated Project
  `project_0002_1a0af866391f412d`;
- exact Table object/version
  `8a425466-b697-4c85-9a43-199414a22865` /
  `be02266a-7d4f-4ebb-9f28-3132855167d0`;
- exact Structure object/version
  `dc3c3eee-f254-4edf-a0fa-c955402b3069` /
  `8859cb49-0766-48cd-8a56-e44f5332e0c5`;
- legacy run `job_dc63f3f5d57742009c6be09e`;
- zero sampled 500/Internal Server Error responses;
- one reproducible 404:
  `/api/api/scientific-reports/job_dc63f3f5d57742009c6be09e`.

### Not seen

- destructive archive/trash/purge confirmations;
- cross-user role differences;
- true offline recovery;
- screen-reader speech output;
- slow external-network p95;
- browser zoom/reflow beyond the two fixed viewports.
