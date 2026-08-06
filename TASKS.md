# Task Queue

---TASK---
Status: IN_PROGRESS
# Phase 10M-7
Workspace Integration + Browser/API/Service Evidence Closure

Reviewer-authorized executable task based on the verified Phase 10M-6
lifecycle:
- implementation `65e80ba915140e29db08dc053c1d218206daaa03`, CI `31020968546` success;
- completion `aec09cebb33ae9673063a22f8fc772737c9a47b4`, CI `31022245082` success;
- archive `200212b164041e38626d6b948c7fe64c772ca6ce`, CI `31060008583` success.

Canonical acceptance source:
`docs/phase10m/phase10m_acceptance_and_test_plan.md`

Acceptance registry:
- M7-A01 `Service-backed`: PostgreSQL + Redis + MinIO full Workspace lifecycle, 0 skipped/failed.
- M7-A02 `Scientific integrity`: Adapter -> Runtime -> Artifact -> renderer/evidence authority remains exact.
- M7-A03 `Historical compatibility`: 0.1/0.2, modern/legacy/partial/missing-source cases retained.
- M7-A04 `Full tests`: Backend/frontend/typecheck/build/lock/migration/closure all pass.
- M7-A05 `Browser`: Chromium/Firefox/WebKit/mobile/accessibility/WebGL current evidence passes.
- M7-A06 `Security`: All Workspace security markers and secret scan pass.
- M7-A07 `Evidence`: Sanitized API/DOM/network/console/screenshots/performance manifest verifies.
- M7-A08 `Lifecycle`: Implementation, completion, and verified queue archive exact-SHA CI pass.

Execution boundaries:
- Reconcile this exact registry into the backlog, execution lock, and execution
  manifest as authorized M7 Stage R0 work.
- Close the existing source/Profile/Intent/Eligibility/Plan/Runtime/Artifact/
  interpretation/Workspace/Viewer/selection/Report/Recipe/Save/reopen chain
  through integration, browser, API, service, security, and evidence tests.
- Targeted implementation bug fixes are allowed only within sealed contracts.
- No database or migration change, public API expansion, contract redesign,
  dependency or lockfile change, new science, new tool/Adapter, new LLM call
  site, provider fallback, execution authority, or stale identity rebinding.
- Reuse verified DeepSeek evidence where identity continuity is sufficient;
  any new real call remains DeepSeek-only via `DEEPSEEK_KEY` with no fallback.
- Complete implementation, completion-record, and queue-archive exact-SHA CI.
- Do not create, queue, or execute Phase 10N-0 automatically.
---END---

Phase 10N-0:
REVIEWER_GATE / AWAITING REVIEWER PROMPT
