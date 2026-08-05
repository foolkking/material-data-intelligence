# Task Queue

---TASK---
Status: IN_PROGRESS
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
---END---

Phase 10M-7:
REVIEWER_GATE / AWAITING REVIEWER PROMPT
