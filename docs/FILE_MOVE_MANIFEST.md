# File Move Manifest

**Previous freeze:** `FROZEN_BASELINE_V1`
**Current:** `FROZEN_BASELINE_V2`
**Amendment date:** 2026-09-06
**Physical file moves authorized:** `NO`

V2 replaces the V1 file-only model with symbol groups, facades and cohesive frontend move units. Every `READY_TO_MOVE` is `NO`. `READY_FOR_BATCH0` means only that a dependency-normalization task may be proposed after an approved exact-SHA baseline.

| MOVE_ID | MOVE_UNIT | CURRENT_PATH | OWNED_SYMBOLS | MIXED_LAYER | SPLIT_REQUIRED | PROPOSED_CANONICAL_PATH | OLD_PATH_DISPOSITION | PUBLIC_EXPORT_SET | DYNAMIC_CONTRACT_IDS | DEPENDENCY_PREREQUISITES | BATCH0_PREREQUISITE | SHIM_REQUIRED | RISK | READY_FOR_BATCH0 | READY_TO_MOVE |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `M-API-001` | `FACADE_ONLY` | `mdi_api.main` | `app` and startup composition | YES | YES | `mdi_api/bootstrap/app.py` | `COMPATIBILITY_SHIM` | `app` | `DC-API-01,DC-PS-01,DC-CI-01` | thin routers/application factories | B0 import/composition normalization | YES | BLOCKER | NO | NO |
| `M-API-002` | `SYMBOL_GROUP` | `phase2_runtime.py` | DTOs/records by domain | YES | YES | `application/{projects,data,jobs}/models.py` | `COMPATIBILITY_SHIM` | listed in Symbol Manifest | `DC-TEST-01,DC-ROUTE-01` | identify all external imports | `B0-5` | YES | BLOCKER | YES | NO |
| `M-API-003` | `SYMBOL_GROUP` | `phase2_runtime.py` | legacy runtime/use-case functions | YES | YES | `application/{projects,data,jobs,artifacts}/*` | `COMPATIBILITY_SHIM` | all public `*phase2*`, plan/store/runtime functions | `DC-TEST-01,DC-RUNTIME-01` | ports and composition root | `B0-4,B0-5` | YES | BLOCKER | YES | NO |
| `M-API-004` | `SYMBOL_GROUP` | `repositories.py` | repository protocols | YES | YES | `domain/*/ports.py` or `application/*/ports.py` | `COMPATIBILITY_SHIM` | all public repository protocols | `DC-TEST-01,DC-DB-01` | consumers depend on ports | `B0-4,B0-5` | YES | BLOCKER | YES | NO |
| `M-API-005` | `SYMBOL_GROUP` | `repositories.py` | in-memory implementations/bundle | YES | YES | `infrastructure/persistence/memory/*` | `COMPATIBILITY_SHIM` | `InMemory*` | `DC-TEST-01` | port split | `B0-5` | YES | BLOCKER | YES | NO |
| `M-API-006` | `SYMBOL_GROUP` | `repositories.py` | SQLAlchemy implementations/mappers | YES | YES | `infrastructure/persistence/sqlalchemy/*` | `COMPATIBILITY_SHIM` | `SqlAlchemy*`, selected hash functions | `DC-TEST-01,DC-DB-01` | port split and schema path retained | `B0-4,B0-5` | YES | BLOCKER | YES | NO |
| `M-API-007` | `SYMBOL_GROUP` | `agent2_repositories.py` | object/research/result/report repositories | YES | YES | domain ports + `infrastructure/persistence/sqlalchemy/*` | `COMPATIBILITY_SHIM` | all public classes | `DC-TEST-01,DC-DB-01` | UoW decomposition | `B0-4,B0-5` | YES | BLOCKER | YES | NO |
| `M-API-008` | `SYMBOL_GROUP` | `database.py` | engine lifecycle | YES | YES | `infrastructure/persistence/engine.py` | `COMPATIBILITY_SHIM` | `create_engine_from_settings`, `dispose_cached_engines` | `DC-TEST-01,DC-DB-01` | bootstrap must select engine | `B0-4` | YES | BLOCKER | YES | NO |
| `M-API-009` | `SYMBOL_GROUP` | `database.py` | `create_repository_factory` | YES | YES | `bootstrap/repository_factory.py` | `COMPATIBILITY_SHIM` | factory symbol | `DC-TEST-01,DC-DB-01` | application ports stable | `B0-4` | YES | BLOCKER | YES | NO |
| `M-API-010` | `WHOLE_FILE` | `db.py` | SQLAlchemy tables/metadata/constants | NO | NO | KEEP current path initially | `KEEP` | all table symbols/metadata/constants | `DC-DB-01` | none; schema identity immutable | none | NO | BLOCKER | NO | NO |
| `M-API-011` | `SYMBOL_GROUP` | `workspaces.py` | domain error/policy/models | YES | YES | `domain/workspaces/*` | `COMPATIBILITY_SHIM` | `WorkspaceDomainError`, `WorkspaceSnapshot` | `DC-TEST-01` | separate projection service | `B0-5` | YES | HIGH | YES | NO |
| `M-API-012` | `SYMBOL_GROUP` | `workspaces.py` | `WorkspaceProjectionService` and projection helpers | YES | YES | `application/workspaces/projection.py` | `COMPATIBILITY_SHIM` | service | `DC-TEST-01` | repository ports | `B0-4,B0-5` | YES | BLOCKER | YES | NO |
| `M-API-013` | `SYMBOL_GROUP` | `report_composition.py` | provider-selection projection | YES | YES | `application/providers/selection.py` | `COMPATIBILITY_SHIM` | patch/import surface frozen | `DC-TEST-01` | remove router private import | `B0-1` | YES | BLOCKER | YES | NO |
| `M-API-014` | `SYMBOL_GROUP` | `report_composition.py` | eligibility policy/projector | YES | YES | `domain/reports/policy.py` + `application/reports/eligibility.py` | `COMPATIBILITY_SHIM` | error, preview, projector | `DC-TEST-01` | provider boundary | `B0-1,B0-5` | YES | HIGH | YES | NO |
| `M-API-015` | `SYMBOL_GROUP` | `report_composition.py` | composition/export service | YES | YES | `application/reports/composition.py` | `COMPATIBILITY_SHIM` | service/max-bytes | `DC-TEST-01,DC-PROMPT-02` | UoW/workspace ports | `B0-1,B0-4,B0-5` | YES | BLOCKER | YES | NO |
| `M-API-016` | `SYMBOL_GROUP` | `project_history.py` | history query service/projections | YES | YES | `application/projects/history.py` | `COMPATIBILITY_SHIM` | schema version/service | `DC-TEST-01` | runtime fallback isolated | `B0-5` | YES | HIGH | YES | NO |
| `M-API-017` | `SYMBOL_GROUP` | `research_agent/service.py` | `ResearchTurnService` | YES | YES | `application/research/turn_service.py` | `COMPATIBILITY_SHIM` | service | `DC-TEST-01,DC-RQ-01` | transport-neutral actor context | `B0-4,B0-5` | YES | BLOCKER | YES | NO |
| `M-API-018` | `SYMBOL_GROUP` | `research_agent/planning/*` | planning/binding/validation/processor | YES | REVIEW | `application/research/planning/*` and pure domain policy | `COMPATIBILITY_SHIM` | public symbols in Symbol Manifest | `DC-PROMPT-01,DC-RQ-02,DC-TEST-01` | Tool/Adapter composition normalized | `B0-2,B0-4,B0-5` | YES | BLOCKER | YES | NO |
| `M-API-019` | `SHIM_ONLY` | `research_agent_worker.py` | `run_queued_turn` | NO | NO | canonical application handler behind current module | `IMMUTABLE` | handler | `DC-RQ-01` | stable application entrypoint | `B0-3` | existing shim | BLOCKER | YES | NO |
| `M-API-020` | `SHIM_ONLY` | `research_agent_planning_worker.py` | `run_queued_planning` | NO | NO | canonical planning handler behind current module | `IMMUTABLE` | handler | `DC-RQ-02` | stable application entrypoint | `B0-3` | existing shim | BLOCKER | YES | NO |
| `M-API-021` | `SYMBOL_GROUP` | `scientific_objects/*` | schemas/registry/policy/service | YES | YES | `domain/scientific_objects/*` + `application/scientific_objects/*` | `COMPATIBILITY_SHIM` | package public set | `DC-TEST-01,DC-DB-01` | ports separated | `B0-4,B0-5` | YES | BLOCKER | YES | NO |
| `M-API-022` | `SYMBOL_GROUP` | `scientific_results/*` | schemas/projectors/services/queue/worker | YES | YES | domain + application + infrastructure by symbol | `COMPATIBILITY_SHIM` | package public set/handler | `DC-RQ-04,DC-TEST-01` | stable application handler | `B0-3,B0-4,B0-5` | YES | BLOCKER | YES | NO |
| `M-API-023` | `SYMBOL_GROUP` | `scientific_reports/*` | schemas/grounding/composition/client/queue/service | YES | YES | domain + application + infrastructure by symbol | `COMPATIBILITY_SHIM` | package public set | `DC-RQ-06,DC-PROMPT-02,DC-TEST-01` | stable provider and application boundaries | `B0-1,B0-3,B0-4,B0-5` | YES | BLOCKER | YES | NO |
| `M-API-024` | `SYMBOL_GROUP` | `routers/*` | route/dependency symbols | YES | YES | `transport/http/*` | `COMPATIBILITY_SHIM` where imported | every route/dependency/request model | `DC-ROUTE-01,DC-TEST-01,DC-API-01` | extract DB/private business helpers | `B0-1,B0-4,B0-5` | YES | BLOCKER | YES | NO |
| `M-WEB-001` | `SYMBOL_GROUP` | `app/components/ProductPages.tsx` | projects/console group | YES | YES | `features/projects/*` | `COMPATIBILITY_SHIM` | named route page exports | `DC-TEST-02,DC-ROUTE-01` | split data group | `B0-5` | YES | BLOCKER | YES | NO |
| `M-WEB-002` | `SYMBOL_GROUP` | same | data/upload/viewer composition group | YES | YES | `features/data/*` | `COMPATIBILITY_SHIM` | data route exports | `DC-NEXT-01,DC-TEST-02,DC-ROUTE-01` | viewer public boundary | `B0-5` | YES | BLOCKER | YES | NO |
| `M-WEB-003` | `SYMBOL_GROUP` | `app/components/ResearchPages.tsx` | Research page/state/history group | YES | YES | `features/research/*` | `COMPATIBILITY_SHIM` | `ResearchPage` + tested helpers | `DC-TEST-02,DC-ROUTE-01` | separate report group | `B0-5` | YES | BLOCKER | YES | NO |
| `M-WEB-004` | `SYMBOL_GROUP` | same | legacy Reports/Reader group | YES | YES | `features/reports/legacy/*` | `COMPATIBILITY_SHIM` | `ReportsPage`, `ReportReaderPage` | `DC-NEXT-01,DC-TEST-02,DC-ROUTE-01` | remove cross-feature dynamic import | `B0-5` | YES | BLOCKER | YES | NO |
| `M-WEB-005` | `SYMBOL_GROUP` | `PlannerWorkbench.tsx` | planning workspace/panels | YES | YES | `features/research/planner/*` | `COMPATIBILITY_SHIM` | `PlannerWorkbench` and tested helpers | `DC-NEXT-01,DC-TEST-02,DC-ROUTE-01` | viewer composition boundary | `B0-5` | YES | BLOCKER | YES | NO |
| `M-WEB-006` | `WHOLE_FILE` | `ProductShell.tsx` | shell/auth frames | NO | NO | `shared/layout/ProductShell.tsx` | `COMPATIBILITY_SHIM` | named exports | `DC-TEST-02,DC-ROUTE-01` | feature imports must be absent | `B0-5` | YES | BLOCKER | YES | NO |
| `M-WEB-007` | `WHOLE_FILE` | `ProductRouteFrame.tsx` | route frame | NO | NO | `shared/layout/ProductRouteFrame.tsx` | `COMPATIBILITY_SHIM` | named exports | `DC-TEST-02,DC-ROUTE-01` | none beyond route inventory | `B0-5` | YES | HIGH | YES | NO |
| `M-WEB-008` | `WHOLE_FILE` | `ProductNavigation.tsx` | navigation provider/link/hooks | NO | NO | `shared/layout/ProductNavigation.tsx` | `COMPATIBILITY_SHIM` | named exports | `DC-TEST-02,DC-ROUTE-01` | preserve client boundary | `B0-5` | YES | HIGH | YES | NO |
| `M-WEB-009` | `WHOLE_FILE` | `LazyScientificViewers.tsx` + referenced viewer entrypoints | lazy viewer boundary | NO | NO | `scientific-viewers/LazyScientificViewers.tsx` | `COMPATIBILITY_SHIM` | three lazy loaders | `DC-NEXT-01,DC-NEXT-02,DC-TEST-02` | cohesive viewer/worker move | `B0-5` | YES | BLOCKER | YES | NO |
| `M-WEB-010` | `SYMBOL_GROUP` | `ScientificReportRoute.tsx` | canonical report route/document | YES | YES | `features/reports/*` | `COMPATIBILITY_SHIM` | `ScientificReportRoute` | `DC-NEXT-01,DC-ROUTE-01,DC-TEST-02` | isolate legacy reader | `B0-5` | YES | HIGH | YES | NO |
| `M-WEB-011` | `WHOLE_FILE` | `ScientificReportsIndexPage.tsx` | report directory | NO | NO | `features/reports/ScientificReportsIndexPage.tsx` | `COMPATIBILITY_SHIM` | page export | `DC-ROUTE-01,DC-TEST-02` | none | `B0-5` | YES | MEDIUM | YES | NO |

## Do Not Move

- `mdi_api.db` and Alembic history during initial migration batches.
- queue names/handler identities, Tool/Adapter manifests and identities.
- `packages/*` and `services/*` paths; only internal dependency normalization is proposed.
- launcher, CI, qualification, retention, runtime-manifest or evidence-authority paths without a separate approved manifest change.
- runtime, database, object-store, cache, log, screenshot or evidence data.

## Gate

`READY_FOR_BATCH0=YES` does not authorize implementation under this documentation task. Physical movement requires completed Batch 0 prerequisites, an approved clean exact-SHA worktree, public-surface comparison, dynamic-contract acceptance, and separate human approval.
