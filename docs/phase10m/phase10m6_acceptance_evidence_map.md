# Phase 10M-6 Acceptance Evidence Map

| ID | Requirement | Implementation | Tests/evidence |
| --- | --- | --- | --- |
| M6-A01 | `EXPLICIT_WORKSPACE_SAVE_AND_CONCURRENCY` | canonical durable draft, no-op suppression, If-Match, conflict/cap UX | shell/model tests; save/conflict/cap captures |
| M6-A02 | `DETERMINISTIC_RELOAD_AND_LAYOUT_RESTORATION` | exact GET snapshot and URL/fallback precedence | shell tests; reload/state ownership evidence |
| M6-A03 | `DEEP_LINK_REFRESH_AND_HISTORY_NAVIGATION` | canonical panel/selection route and stale-response rejection | M3/M6 tests; deep-link/Back/Forward/browser evidence |
| M6-A04 | `JOB_SOURCE_PARTIAL_AND_HISTORICAL_RECOVERY` | persisted projection observation and typed source loss | integration test; running/partial/stale/missing/history captures |
| M6-A05 | `REPORT_RECIPE_RECOVERY_AND_DRAFT_HONESTY` | exact immutable history/reload/export; memory-only draft warning | composer/shell tests; browser and draft evidence |
| M6-A06 | `USER_FACING_STATES_LONG_CONTENT_AND_TERMINOLOGY` | distinct Save/conflict/cap/source/draft states and bounded details | component/browser/accessibility evidence |
| M6-A07 | `RESPONSIVE_MOBILE_AND_ACCESSIBILITY_CLOSURE` | one active mobile surface, focus trap/return, live status, 44px controls | 390x844 browser capture and mobile metrics |
| M6-A08 | `PERFORMANCE_SECURITY_EVIDENCE_AND_VERIFIED_LIFECYCLE` | metadata-first loading, abort/invalidation, retained WebGL/security boundaries | lifecycle/security/evidence tests; CI service gate |

```text
expected = 8
implemented = 8
missing = 0
extra = 0
duplicate = 0
```
