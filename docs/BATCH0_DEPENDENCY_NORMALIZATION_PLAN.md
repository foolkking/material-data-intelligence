# Batch 0 Dependency Normalization Plan

**Status:** `FROZEN_BASELINE_V2`
**Execution:** plan only; not executed.
**Prerequisite:** approved exact-SHA clean worktree.
**Physical file move authorized:** `NO`

Batch 0 changes dependencies in place or behind minimal compatibility boundaries. It is not a directory cleanup or physical relocation batch. Each task must be independently commit-able, verifiable and revertible.

| TASK_ID | PROBLEM / CURRENT_DEPENDENCY | TARGET_DEPENDENCY | FILES / SYMBOLS | BEHAVIOR_INVARIANTS | DYNAMIC_CONTRACT_IMPACT | TESTS_REQUIRED | RUNTIME_VERIFICATION_REQUIRED | ROLLBACK | PREREQUISITES | RISK | ORDER |
|---|---|---|---|---|---|---|---|---|---|---|---|
| `B0-1` | `report_composition._provider_report_projection` imports private `routers.planner._select_planner_provider` | stable application/provider-selection boundary called by router and report composition | `report_composition.py`, `routers/planner.py`, provider symbols | same provider eligibility, fallback, auth/secrets and report output | `DC-TEST-01`; no URL/queue change | provider unit tests; report/planner regressions; import graph gate | report preview/finalize read-only smoke; no runtime mutation in freeze | restore private import and prior helper call | identify all callers/patch targets | BLOCKER reverse-layer edge | 1 |
| `B0-2` | Tool Registry metadata lazily imports Adapter Registry while adapter executor imports Tool Registry | bootstrap/composition supplies registry/metadata dependency; one directional contract | `planner_metadata.py`, adapters registry/executor, composition wiring | tool/adapter identity and scientific semantics unchanged | `DC-TOOL-01`, `DC-ADAPTER-01` | registry identity, manifest validation, adapter/executor tests | controlled worker/planner smoke after code change | restore old lazy edge | define injection contract; preserve manifests | BLOCKER cycle/implementation leak | 2 |
| `B0-3` | worker modules import arbitrary `mdi_api` internals | old handler identity -> stable application entrypoint -> domain/application operation | six worker roles, queue shims, application entrypoints | queue names, handler semantics, async behavior, persisted IDs unchanged | `DC-RQ-01..06`, `DC-PYM-01` | handler resolution, queue manifest byte comparison, worker unit tests | fresh controlled worker registration/heartbeat and one safe read-only job path | restore handler-to-old-internal call | B0-4 entrypoint contracts; clean runtime gate | BLOCKER runtime boundary | 4 |
| `B0-4` | research/application paths use concrete config/database globals | application/domain ports selected by bootstrap; infra implements ports | research service/planning, database factory, UoW, config access | auth, transactions, state/identity, fail-closed semantics unchanged | `DC-DB-01`, `DC-TEST-01` | unit/integration import graph and persistence tests | API/worker controlled smoke with exact SHA; DB read-only checks | restore concrete provider wiring | define ports; no schema change | HIGH | 3 |
| `B0-5` | mixed modules obscure ownership and make whole-file moves unsafe | symbol groups have canonical owners; old module re-exports remain | phase2_runtime, repositories, agent2_repositories, workspaces, report_composition, project_history, scientific families, frontend aggregators | all public symbols, routes, viewer semantics and identities unchanged | all associated `DC-*`; public export comparison mandatory | pre/post export sets, test patch scan, focused tests | only after each cohesive code slice; no service topology change | restore old module implementation/re-exports | B0-1..4 as applicable; symbol manifest | BLOCKER surface drift | 5 |
| `B0-6` | no static guard prevents canonical code importing compatibility | architecture check rejects canonical -> compatibility edge | future lint/check target; no current CI change here | compatibility remains facade-only | `DC-PY-INIT-01` and all shim IDs | positive/negative import graph fixtures | not required for docs-only; later CI gate | remove guard only if false-positive documented | canonical/shim map complete | HIGH | 6 |
| `B0-7` | import graph/path contract verification is manual and fragmented | deterministic report of layer edges, exports, dynamic strings and route/worker identities | scripts/check design only; no implementation in this task | verification itself cannot mutate runtime or data | all manifests | architecture fixture strategy, no test/CI modification now | later read-only and controlled runtime modes | revert checker only | approved output schema and false-positive policy | MEDIUM | 7 |

## Batch Rules

- Execution order is `B0-1` -> `B0-2` -> `B0-4` -> `B0-3` -> `B0-5` -> `B0-6` -> `B0-7`. `B0-4` precedes `B0-3` because `B0-3` consumes the stable application-facing entrypoint contracts produced by `B0-4`.
- One task per commit; no opportunistic file move.
- Preserve old public/dynamic paths until verification proves no remaining reader and a separate deprecation approval exists.
- Do not alter API/schema/migration/queue/tool/adapter/scientific identities.
- Any failed verification stops that task and uses its rollback concept; it does not trigger cleanup.
- `READY_FOR_BATCH0` in the file manifest is proposal readiness only. `READY_TO_MOVE` stays `NO` for all rows.
