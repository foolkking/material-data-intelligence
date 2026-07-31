# Phase 10L-4 Local Test Summary

Date: 2026-07-30 (Asia/Shanghai)

| Check | Result |
| --- | --- |
| L4 contract/API/persistence/provider focused backend | 74 passed |
| L4 evidence integrity | 4 passed |
| L4 local service-backed selection | 3 skipped; services unavailable, not PASS |
| PlannerWorkbench focused | 30 passed |
| L1-L4 focused regression | included in full backend and frontend runs |
| Full backend initial run | 952 passed, 33 skipped, 63 warnings; 2 L4 browser-evidence order failures |
| Full backend corrected run | 954 passed, 33 skipped, 63 warnings |
| Full frontend | 52 files, 333 passed |
| Frontend typecheck | PASS |
| Production frontend build | PASS after replacing two CSS end-alignment compatibility warnings with flex-end |
| Phase 10 closure regression pack | PASS: backend 3 passed/6 deselected, frontend 2 passed, Chromium/Firefox/WebKit browser evidence |
| `uv lock --check` | PASS |
| `npm ls --depth=0` | PASS |
| Browser matrix | Chromium, Firefox, WebKit, and Chromium 390x844 PASS |
| Local PostgreSQL/Redis/MinIO | UNAVAILABLE: Docker CLI is not installed |
| `npm audit` | UNAVAILABLE: configured npmmirror endpoint returns `404 NOT_IMPLEMENTED` |

The default full suite skips service-backed tests when services are absent.
Those skips are not counted as service-backed PASS. The implementation exact-
SHA CI must run the selected PostgreSQL/Redis/MinIO suite with zero skips.
