# Local Test Command Summary

All commands ran with real-provider environment variables empty.

| Gate | Result |
| --- | --- |
| `uv lock --check` | PASS; 108 packages resolved, lock unchanged |
| Focused backend L1-L5/persistence/read/API/artifact | 292 passed |
| Full backend | 1078 passed, 38 skipped, 63 warnings |
| Focused frontend product/PlannerWorkbench | 15 files, 129 tests passed |
| Full frontend | 52 files, 333 tests passed |
| Frontend typecheck | PASS |
| Frontend production build | PASS; `/` 144 kB, first-load JS 247 kB |
| Dependency tree | PASS; no dependency or lock change |
| Phase 10 closure pack | 2 passed |
| Phase 10 closure evidence | PASS |
| Phase 10L-5 evidence check | PASS; 166 entries, 40 historical cases, 16 retained live calls in historical evidence |
| L5 current browser replay | PASS; three desktop browsers + Chromium 390x844 |
| L4 current browser replay | PASS; three desktop browsers + Chromium 390x844 |
| Local service-backed | UNAVAILABLE; `docker` command absent |
| npm audit | UNAVAILABLE; configured mirror returned `404 NOT_IMPLEMENTED` |

The 38 full-backend skips are reported as skips and are not service-backed
success. Exact-SHA CI must prove PostgreSQL + Redis + MinIO and its no-skipped
gate before Phase 10M-0 completion.

Existing pymatgen CIF warnings and spglib deprecation warnings account for the
63 warnings; no warning was suppressed or relabeled.
