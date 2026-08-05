# Task Queue

---TASK---
Status: COMPLETE / AWAITING_VERIFIED_QUEUE_ARCHIVE
# Phase 10M-6
Workspace Save / Reload / Recovery / Responsive Closure

Reviewer-authorized executable task based on the verified Phase 10M-5 archive
`56bec17792fff86a99c3d280ab754a69fff6c51b`, CI `30991896855` success.
Corrected implementation `f294fbd305385eb3fd129ab1f815daaca03d15fa`
passed exact-SHA CI `30990265619`; completion record
`aaef8bf254de3569f4411a85138dfb0c8c79497f` passed exact-SHA CI
`30991190818`.

Acceptance IDs:
- M6-A01 EXPLICIT_WORKSPACE_SAVE_AND_CONCURRENCY
- M6-A02 DETERMINISTIC_RELOAD_AND_LAYOUT_RESTORATION
- M6-A03 DEEP_LINK_REFRESH_AND_HISTORY_NAVIGATION
- M6-A04 JOB_SOURCE_PARTIAL_AND_HISTORICAL_RECOVERY
- M6-A05 REPORT_RECIPE_RECOVERY_AND_DRAFT_HONESTY
- M6-A06 USER_FACING_STATES_LONG_CONTENT_AND_TERMINOLOGY
- M6-A07 RESPONSIVE_MOBILE_AND_ACCESSIBILITY_CLOSURE
- M6-A08 PERFORMANCE_SECURITY_EVIDENCE_AND_VERIFIED_LIFECYCLE

Frozen execution boundaries:
- Server owns durable Workspace state, URL owns exact panel/selection, and
  memory owns camera/hover/playback/filters/dialogs/unsaved edits and drafts.
- Implement explicit Save, no-op suppression, ETag conflict and revision-cap
  UX, deterministic reload/layout, deep-link/history recovery, running/partial/
  failed/blocked/stale/missing/historical recovery, finalized Report/Recipe
  recovery, honest session-only drafts, responsive/accessibility closure, and
  bounded cancellation/cache/WebGL lifecycle.
- Reuse existing Workspace/Job/Artifact/Interpretation/Report/Recipe APIs and
  persistence. No new table, column, migration, public endpoint, dependency,
  lockfile, contract version, scientific authority, or local browser authority.
- No Plan, Job, ToolCall, queue, Adapter, rerun, latest-source rebinding,
  Artifact execution, scientific recomputation, or generated scientific claim.
- NEW_LLM_CALL_SITES = 0; REAL_LLM_CALLS = 0; DeepSeek-only policy remains.
- Complete focused/full/browser/service-backed/evidence/security checks and
  implementation, completion-record, and queue-archive exact-SHA CI lifecycle.
- Do not create, queue, or execute Phase 10M-7 automatically.

Completion time: 2026-08-05T23:44:05+08:00

Changed files:
- Workspace shell, Report composer, recovery model, responsive styles, tests,
  browser/service/evidence runners, Phase 10M docs/evidence, CI, and persistent
  project records.

Summary:
- Closed explicit Save, no-op suppression, ETag conflict/revision-cap UX,
  deterministic reload/deep-link recovery, bounded Job/source observation,
  finalized Report/Recipe reload, session-only draft honesty, and responsive
  accessibility behavior without changing sealed contracts or authorities.

Tests:
- Local: frontend 411 passed; backend 1148 passed, 43 skipped; focused backend
  69 passed; evidence 4 passed; typecheck/build and four-browser replay passed.
- Exact-SHA implementation CI: `65e80ba915140e29db08dc053c1d218206daaa03`,
  run `31020968546`, success; service-backed 41 passed, 0 skipped/failed/errors.
- Completion-record and queue-archive exact-SHA CI remain lifecycle gates.
---END---

Phase 10M-7:
REVIEWER_GATE / AWAITING REVIEWER PROMPT
