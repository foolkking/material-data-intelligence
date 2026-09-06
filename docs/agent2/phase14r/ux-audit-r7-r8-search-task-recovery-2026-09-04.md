# UX audit — Phase 14-R R7/R8 search, task and recovery

## 1. Scope & evidence base

This scoped audit covers the authenticated web application's Global Search,
Task Center and Notification Center. The audience is a mixed group of
materials-science researchers and platform operators; scientific work is
high-stakes because selecting the wrong historical run or retrying the wrong
execution can invalidate provenance. Evidence is current repository source,
focused tests and the checked-in same-stack browser evidence. No new live
browser campaign was run for this pre-change audit, so visual consequences are
inferred where they were not already recorded.

**Seen:** bounded authorized global search, saved-search lifecycle, Task Center
and Notification Center loading/error/refresh/filter/search/reconnect states,
the authoritative Job → ResearchTurn relation, and current Phase 14-R evidence.

**Not seen:** multi-user analytics, production-scale notification volume, push
delivery outside the product, and screen-reader output for these routes.

## 2. Executive summary

The product already has the correct bounded architecture: Global Search is an
authorized navigation read model, saved searches store filters rather than
results, and task/notification state is rebuilt from persisted Jobs. Recovery
also has explicit refresh, visibility and online resynchronization. The
remaining product-quality defect is identity: a current ResearchTurn-backed
task is presented as the generic title “可恢复研究” or “研究会话更新”, while
the local search index contains only project name, Job ID, status and workspace
projection status. A researcher therefore cannot locate a task by the question
they remember asking, even though the exact user message is already linked by
the persisted ResearchTurn. Rows are sorted by update time but do not expose
that time, so users cannot independently verify recency. The smallest correct
repair is a bounded task-feed projection of the exact user-message summary,
used only for display/search, plus a semantic `<time>` element.

## 3. Quick wins

1. Project the exact ResearchTurn user-message summary in the existing task feed.
2. Use that summary as the task/notification title and searchable text.
3. Display the persisted update/create timestamp in each row.

## 4. Findings

### 4.1 Search and organization

#### SEARCH-01 · Tasks cannot be found by their remembered research question

| | |
|---|---|
| **Dimension** | Navigation and information architecture; data display |
| **Severity** | High |
| **Confidence** | Observed (source); rendered impact inferred |
| **Effort** | M |
| **Location** | `apps/web/app/lib/task-center-data.ts`; `TaskCenterPage.tsx`; `NotificationCenterPage.tsx` |

**Evidence.** `productTaskSearchText()` indexes only `projectName`, `jobId`,
`jobStatus` and `workspaceProjectionStatus`. Current ResearchTurn-backed rows
render the generic titles “可恢复研究” and “研究会话更新”. The backend already
joins each Job to `research_turns`, whose `user_message_id` is an exact foreign
key to the persisted user message.

**Why it matters.** Researchers remember “compare CrystalNN and VoronoiNN” or
“analyse the selected mat-2 row”, not a 32-character Job identifier. With many
runs in one project, the current list makes distinct work look identical and
pushes users toward opening several runs to find the right one.

**Recommendation.** Extend the existing metadata-only task feed with one
bounded `researchQuestion` field from the exact ResearchTurn user message.
Render it as the row title and include it in local task/notification search.
Keep Job and Turn identities unchanged and available under technical details.

### 4.2 System status and recovery

#### STATE-01 · Time-sorted rows do not disclose their persisted update time

| | |
|---|---|
| **Dimension** | System status and feedback; data display |
| **Severity** | Medium |
| **Confidence** | Observed (source); rendered impact inferred |
| **Effort** | S |
| **Location** | Task Center and Notification Center row renderers |

**Evidence.** Both centers sort on `updatedAt || createdAt`, but rows display
only Artifact and interpretation counts. The page-level “最近同步” timestamp
describes feed refresh time, not the age of an individual scientific run.

**Why it matters.** A researcher cannot distinguish a run updated a minute ago
from an otherwise identical historical row, or confirm that a recovered task
is the one that just changed.

**Recommendation.** Show the authoritative row timestamp with a semantic
`<time dateTime>` value and concise localized copy. Do not synthesize relative
time on an uncontrolled timer.

## 5. Prioritized backlog

| # | ID | What to do | Severity | Effort | Why it's here |
|---|---|---|---|---|---|
| 1 | SEARCH-01 | Add bounded exact research-question projection and use it for titles/search | High | M | Restores human findability without a new search authority |
| 2 | STATE-01 | Display persisted row update time | Medium | S | Makes recency and recovery state independently inspectable |

## 6. What's working, and what I left alone

**What's working.** Global Search already rejects blank unbounded retrieval,
supports type/project/lifecycle filters, stores only saved filter definitions,
and rechecks authorization when executed. Task/Notification surfaces preserve
last-known data during refresh failure, refresh on visibility/online events,
and keep legacy records read-only.

**What I left alone, and why.** I did not introduce push notifications, a
second task database, or a new global-search index. Those would duplicate
existing persisted Job/Search authority and are not required to close the
observed user path.

## 7. Open questions

- Production-scale pagination beyond the current bounded feed still requires a
  separate real-volume campaign; this repair does not claim that qualification.
- Push/browser notifications remain outside this scoped product-path audit.
