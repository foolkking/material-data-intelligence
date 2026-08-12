# Phase 13-2 Attempt 4 Failure

Attempt 4 is `FAILED / REVIEWER_ACTION_REQUIRED`. Attempts 1-3 remain
historical failures and Fix-Forwards 1-3 remain PASS. Entry authority, Level C
7/7, Level C2 7/7 and the real PostgreSQL/Redis/MinIO D0 gate passed before the
first fresh full demonstration.

Fresh Demo 1 used `tests/fixtures/tables/formulas.csv`, the current canonical
natural-language prompt, durable PostgreSQL/MinIO source persistence, Redis,
and a fresh QueueWorkerRuntime. The real Plan and ToolCall contained only
`dataset.materials_explorer`; no `dataset.composition_space` ToolCall or
`plotly_json` Artifact was produced. This conflicts with the sealed Demo 1
capability family and is `P13-R4-001`.

The resulting AnalysisPlan 0.1 Workspace was projected as
`LEGACY_READ_ONLY`. The real Workspace Report UI disables Finalize for a
read-only Workspace, so the sealed real-user Report/Recipe path cannot be
completed. A diagnostic direct API finalize was deliberately excluded from
PASS authority. This is `P13-R4-002`.

The stop rule prevented Demo 2-7, negative scenarios, browsers and live
DeepSeek from running. No production, Planner, Runtime, Adapter, scientific,
schema, dependency or scope change was made.

Post-stop regression passed backend `1391 passed, 52 skipped`, frontend
`456 passed`, Phase 13 focused/governance `46 passed`, typecheck, production
build, lock, diff, current Fact/Scope hash verification, and secret/security
scans. The real PostgreSQL/Redis/MinIO D0 rerun passed `1 passed, 0 skipped`.
An initial local backend candidate reported `1390 passed, 1 failed` because the
new TASK block used an English status label; the evidence/queue-only correction
closed that governance failure. Browser and Linux/Windows replay remain
`NOT_EXECUTED_AFTER_P0_STOP`, consistent with the release-critical stop rule.

```text
PHASE_13_2_ATTEMPT_4 = FAILED / REVIEWER_ACTION_REQUIRED
DEMO_1_STATUS = FAIL_PRODUCT_INTEGRATION
DEMO_2_STATUS = NOT_EXECUTED_AFTER_P0_STOP
DEMO_3_STATUS = NOT_EXECUTED_AFTER_P0_STOP
DEMO_4_STATUS = NOT_EXECUTED_AFTER_P0_STOP
DEMO_5_STATUS = NOT_EXECUTED_AFTER_P0_STOP
DEMO_6_STATUS = NOT_EXECUTED_AFTER_P0_STOP
DEMO_7_STATUS = NOT_EXECUTED_AFTER_P0_STOP
P13X2_ACCEPTANCE = 0/8
RELEASE_CRITICAL_INTEGRATION_DEFECTS = 2
SCIENTIFIC_DEFECTS = 0
SECURITY_DEFECTS = 0
PRODUCTION_CODE_CHANGES = 0
```
