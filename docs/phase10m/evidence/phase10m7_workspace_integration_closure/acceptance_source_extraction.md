# Acceptance Source Extraction

Canonical source: `phase10m_acceptance_and_test_plan.md`.

| ID | Exact title | Exact responsibility |
| --- | --- | --- |
| M7-A01 | Service-backed | PostgreSQL + Redis + MinIO full Workspace lifecycle, 0 skipped/failed |
| M7-A02 | Scientific integrity | Adapter -> Runtime -> Artifact -> renderer/evidence authority remains exact |
| M7-A03 | Historical compatibility | 0.1/0.2, modern/legacy/partial/missing-source cases retained |
| M7-A04 | Full tests | Backend/frontend/typecheck/build/lock/migration/closure all pass |
| M7-A05 | Browser | Chromium/Firefox/WebKit/mobile/accessibility/WebGL current evidence passes |
| M7-A06 | Security | All Workspace security markers and secret scan pass |
| M7-A07 | Evidence | Sanitized API/DOM/network/console/screenshots/performance manifest verifies |
| M7-A08 | Lifecycle | Implementation, completion, and verified queue archive exact-SHA CI pass |
