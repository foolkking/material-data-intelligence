# Symbol Ownership Manifest

**Status:** `FROZEN_BASELINE_V2`
**Observed baseline:** `268106e7634472cc8a815e27a8bf3d3eda16be1d`
**Purpose:** freeze canonical symbol ownership before Batch 0 or physical relocation.
**Physical moves authorized:** `NO`

`PUBLIC_EXPORT_SET` means top-level public definitions/constants plus names externally imported, dynamically resolved, used as FastAPI dependencies, or targeted by tests/monkeypatching. Absence of `__all__` does not make a symbol private.

## Backend Mixed Modules

| CURRENT_FILE | SYMBOL / SYMBOL_GROUP | SYMBOL_TYPE | PUBLIC_OR_INTERNAL | CURRENT_RESPONSIBILITY | DOMAIN_OWNER | TARGET_LAYER / TARGET_MODULE | STATIC_IMPORTERS / CALLERS | CALLEES | DYNAMIC / STRING / TEST REFERENCES | PERSISTED_IDENTITY / ENTRYPOINT | COMPATIBILITY | EXTRACTION_REQUIRED | WHOLE_FILE_ALLOWED | RISK / NOTES |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `phase2_runtime.py` | `CreateProjectRequest`, `InlineUploadFile`, `DatasetUploadRequest`, `CreateJobRequest` | DTOs | public | legacy HTTP/use-case inputs | projects/data/jobs | transport-neutral application command DTOs, then transport adapters | access + dataset/planner/history/research/secured routers + tests | schemas/models | broad static imports/tests | request shape | old module re-export | YES | NO | BLOCKER; do not move entire implementation into compatibility |
| same | `ProjectRecord`, `DatasetRecord`, `MaterializedUpload`, `UploadSession*`, `JobRunRecord` | records | public | legacy runtime records | projects/data/jobs | domain/application records by domain | same legacy callers | schemas/artifacts | tests import selected records | IDs/status semantics | re-export | YES | NO | HIGH |
| same | `LocalFileArtifactStore` | class | public | filesystem artifact adapter | artifacts | `infrastructure/storage/local_artifact_store.py` | runtime/tests | filesystem/artifact models | artifact root paths | artifact authority | shim if imported | YES | NO | HIGH |
| same | `Phase2ProductRuntime`, `_PHASE2_RUNTIME`, `get/reset_phase2_runtime` | class/global/functions | public + internal | in-memory compatibility composition/runtime | cross-domain legacy | split application use cases and bootstrap-owned legacy runtime provider | many routers/tests | repositories, tools, artifact store | monkeypatch/reset tests | runtime singleton semantics | old facade required | YES | NO | BLOCKER |
| same | `build_phase2_plan`, `summarize_plan`, `_phase2_step`, recipe/default helpers | functions | public + internal | deterministic legacy planning | planning | application/research planning compatibility service | planner/tests | schemas/tool order | static/test references | plan/tool semantics | facade | YES | NO | HIGH |
| same | `build_object_store`, dataset/object-store helpers | functions | public + internal | dataset projection/materialization | data | application/data + infrastructure storage | routers/tests | DB/runtime/object schemas | static/test references | object/version authority | facade | YES | NO | BLOCKER |
| same | `list/create/upload/get/...phase2_*` API functions | functions | public | compatibility use-case facade | projects/data/jobs/artifacts | application services by domain | routers and tests | singleton runtime/durable repositories | numerous local imports | URL/job/artifact behavior | KEEP old exported functions | YES | NO | BLOCKER |
| `repositories.py` | repository protocols (`ProjectRepository` … `WorkspaceRepository`) | protocols/classes | public | persistence ports | cross-domain | domain/application `ports/*.py` by owner | UoW/services/workers/tests | schemas | extensive imports | repository contract | old exports | YES | NO | BLOCKER |
| same | `InMemory*Repository`, `InMemoryRepositoryBundle` | implementations | public | in-memory persistence/testing runtime | cross-domain | `infrastructure/persistence/memory/*` | tests, routers, workers, generators | ports/schemas | many tests | behavior/test fixtures | shim | YES | NO | BLOCKER |
| same | `SqlAlchemy*Repository`, `SqlAlchemyRepositoryBundle` | implementations | public | SQL persistence | cross-domain | `infrastructure/persistence/sqlalchemy/*` | database factory, tests | `db.py`, SQLAlchemy | many tests | schema/transaction semantics | shim | YES | NO | BLOCKER |
| same | workspace errors and workspace parse/validation helpers | classes/functions | mixed | workspace policy plus persistence mapping | workspaces | errors/pure policy to domain; mapping to infrastructure | workspace services/tests | workspace schemas | static tests | workspace identity | shim selected public errors | YES | NO | HIGH |
| same | `canonical_analysis_plan_json`, `compute_plan_hash` | functions | public | canonical plan hashing | planning | domain/shared plan integrity module | planning/tests/workers | JSON/hash | externally imported | persisted plan hash | old re-export | YES | NO | BLOCKER |
| same | remaining `_...values/from_row/normalize` helpers | functions | internal | SQL mapping/validation | owning domains | infrastructure persistence modules | repository implementations | db/schemas | patch targets must be checked per batch | row/schema semantics | no external removal assumed | YES | NO | HIGH |
| `agent2_repositories.py` | `ScientificObjectRepository` | class | public | object persistence implementation/port blend | scientific objects | split port and infrastructure implementation | UoW/services/tests | db/schemas | static tests | object/version IDs | old export | YES | NO | BLOCKER |
| same | `ResearchTurn*`, memory/event/decision/capability/execution repositories | classes | public | research persistence | research | split domain ports and SQL infrastructure | UoW/research services/tests | db/schemas | static tests | turn/session state | old exports | YES | NO | BLOCKER |
| same | result/interpretation/report repositories and `Agent2RepositoryBundle` | classes | public | scientific product persistence | results/reports | per-domain ports + infrastructure bundle | UoW/workers/tests | db/schemas | static tests | snapshot/report identity | old exports | YES | NO | BLOCKER |
| `database.py` | `create_engine_from_settings`, engine cache/disposal | functions/globals | public + internal | engine lifecycle | platform persistence | `infrastructure/persistence/engine.py` | routers, workers, operations, providers, tests | settings/SQLAlchemy | broad imports | connection behavior | old exports | YES | NO | BLOCKER |
| same | `create_repository_factory` | function | public | concrete composition factory | platform persistence | bootstrap/composition factory returning application ports | broad runtime/tests | UoW/repository bundles | broad test patch/import | transaction semantics | old export | YES | NO | BLOCKER |
| `db.py` | table objects, `metadata`, `PHASE1_TABLES`, `PHASE3_TABLES`, `PHASE4_TABLES` | schema/constants | public | canonical SQL schema metadata | database | KEEP current canonical infrastructure schema path initially | migrations/repositories/routers/tests | SQLAlchemy | extensive imports and migration/tests | schema identity | path retained | NO initially | NO | BLOCKER; V1 incorrectly treated it as compatibility |
| `workspaces.py` | `WorkspaceDomainError`, selection constants | error/constants | public + internal | workspace validation vocabulary | workspaces | domain workspace policy/errors | routers/repositories/service | schemas | tests | selection semantics | old export | YES | NO | HIGH |
| same | `WorkspaceSnapshot`, `_SourceProjection` | records | public + internal | projection state | workspaces | application/workspaces/models | projection service | schemas | tests | workspace IDs | public snapshot re-export | YES | NO | HIGH |
| same | `WorkspaceProjectionService` and helpers | service/functions | public + internal | workspace query/projection orchestration | workspaces | application/workspaces/projection.py | routers/report composition/tests | repositories/UoW | broad static tests | workspace semantics | old export | YES | NO | BLOCKER |
| `report_composition.py` | `_provider_report_projection` | function | internal but patched/called | provider selection projection | reports/providers | application provider-selection boundary | composition service | **private router helper** | test patch targets | provider behavior | preserve patch surface if used | YES | NO | BLOCKER reverse-layer edge, B0-1 |
| same | `ReportCompositionDomainError`, eligibility constants/helpers | error/policy | public + internal | report eligibility/security policy | reports | domain/reports/composition_policy | router/service | schemas | tests | report authority/fail-closed | old error export | YES | NO | HIGH |
| same | `CompositionPreview`, `_CompositionContext`, `ReportSourceEligibilityProjector` | models/service | public + internal | source eligibility projection | reports | application/reports/eligibility.py | composition service/tests | workspace/results/artifacts | tests | source identities | old exports where public | YES | NO | HIGH |
| same | `ReportCompositionService`, export helpers, `REPORT_EXPORT_MAX_BYTES` | service/functions/constants | public | report composition/finalize/export | reports | application/reports/composition.py + export policy | router/operations/tests | UoW/workspaces/providers | tests/route | report/artifact/recipe identity | old export facade | YES | NO | BLOCKER |
| `project_history.py` | `PROJECT_HISTORY_SCHEMA_VERSION`, `ProjectHistoryService`, projection helpers | constant/service/functions | public + internal | project history query/projection | projects | application/projects/history.py | router/tests | repositories/runtime records | static/test refs | schema version/run IDs | old exports | YES | NO | HIGH; not core domain |
| `research_agent/service.py` | `ResearchTurnService`, lock/status helpers | service/functions | public + internal | research turn orchestration/state transitions | research | application/research/turn_service.py; actor port separated | processor/router/tests | repositories, **routers.auth.CurrentUser** | extensive tests | session/turn state | old export | YES | NO | BLOCKER reverse-layer auth type |
| `research_agent/planning/*` | binder/deterministic/planner/validator/processor | classes/functions | public | capability planning | research/planning | application/research/planning; pure validators/policy may be domain | router/worker/tests | Tool Registry, LLM, repositories | prompt relative path/tests | prompt/plan contract | package facades | REVIEW per module | NO as directory | BLOCKER; prompt path preserved/updated atomically |
| same | queue classes and `run_queued_planning` | queue/handler | public/dynamic | async submission and handler | research/planning | application queue port + infrastructure RQ + old handler shim | worker manifest/runtime | Redis/RQ/service | dotted handler | queue identity | required shim | YES | NO | BLOCKER |
| `scientific_objects/*` | schemas and registry symbols | enums/models/registry | public | object/version contract and type registry | scientific objects | domain/scientific_objects | service/router/tests | schemas/adapters | broad tests | immutable object/version identity | package exports retained | per module | REVIEW | BLOCKER identity authority |
| same | `ScientificObjectService` | service | public | lifecycle/admission/version orchestration | scientific objects | application/scientific_objects/service.py | router/tests | repositories/registry | tests | lifecycle/version | old export | YES | NO | BLOCKER |
| `scientific_results/*` | schemas/fingerprint/projector contracts/relevance | models/policy | public | canonical result contracts/projection rules | scientific results | domain/scientific_results | services/workers/tests | artifact schemas | dynamic projector registry/tests | result/fingerprint identity | package exports retained | REVIEW | NO as directory | BLOCKER |
| same | queue/worker/service/reconciler/artifact loader | services/adapters | public/dynamic | result projection runtime | scientific results | application + infrastructure + queue shim | workers/tests | DB/artifacts/RQ | dotted result worker | result authority/handler | required old handler path | YES | NO | BLOCKER |
| `scientific_reports/*` | schemas/grounding contracts | models/policy | public | report contract/grounding | scientific reports | domain/scientific_reports | services/workers/tests | result schemas | prompts/tests | report identity/version | package exports retained | REVIEW | NO as directory | BLOCKER |
| same | assembler/client/composer/request/service/queue | services/adapters | public | report generation orchestration/provider/RQ | scientific reports | application + infrastructure/provider + queue adapter | router/workers/tests | LLM/UoW/RQ | prompt path/worker handler | report authority | old imports retained | YES | NO | BLOCKER |
| `routers/*.py` | request models, FastAPI dependencies, route functions | models/functions | public/patchable | HTTP transport plus current construction/helpers | respective domains | `transport/http/*`; extract nontransport symbols first | `main.py`, tests, internal reverse callers | application + current DB internals | route decorators/test patch strings | URLs/dependency identity | module shims only if imported | YES for mixed routers | NO as directory | BLOCKER; preserve every route/method/dependency/error |

## Frontend Ownership

| CURRENT_FILE | SYMBOL_GROUP | PUBLIC_OR_INTERNAL | CURRENT_RESPONSIBILITY | DOMAIN_OWNER | TARGET_MODULE | IMPORTERS / REFERENCES | DYNAMIC / ROUTE / CSS COUPLING | COMPATIBILITY | EXTRACTION_REQUIRED | WHOLE_FILE_ALLOWED | RISK |
|---|---|---|---|---|---|---|---|---|---|---|---|
| `ProductPages.tsx` | `ConsolePage`, project hooks/dialogs/pages | public + internal | console/projects CRUD and overview | projects | `features/projects/*` | route files/tests/components | route/query + global CSS | old re-export barrel | YES | NO | BLOCKER |
| same | `ProjectDataPage`, `DatasetUploadPage`, data selection/view helpers | public + internal | Data workbench/upload | data | `features/data/*` | data routes/tests | selection query, viewers, CSS | old re-export | YES | NO | BLOCKER |
| same | `ScientificDataView`, `TableScientificView` and source helpers | internal | scientific source/table presentation | data/viewing | data feature plus viewer public boundary | project data page/tests | viewer APIs/CSS | no forced shared extraction | YES | NO | HIGH |
| `ResearchPages.tsx` | research types/windowing/state helpers + `ResearchPage` | public + internal | Research route/state/timeline/workbench composition | research | `features/research/*` | research routes/tests | session/turn/result query, CSS | old re-export | YES | NO | BLOCKER |
| same | `ReportsPage`, `ReportReaderPage`, report figure helpers | public + internal | legacy reports surfaces | reports | `features/reports/*` | report routes/tests, dynamic legacy import | dynamic `./ResearchPages`, report IDs | old re-export | YES | NO | BLOCKER |
| `PlannerWorkbench.tsx` | `PlannerWorkbench`, context/nav/workbench panels | public + internal | legacy planner/research workspace | research/planning | `features/research/planner/*` | route/tests/docs | API/query/global CSS | old entry re-export | YES | NO | BLOCKER |
| same | viewer preview/render helpers | internal | scientific preview composition | scientific viewers | viewer adapters or research-owned composition | workbench/tests | viewer schemas/dynamic engines | retain feature ownership unless reusable | YES | NO | HIGH |
| `ProductShell.tsx` | `ProductShell`, `ProductShellFrame`, auth frames/prefetch helpers | public + internal | global shell/auth frame | shared layout | `shared/layout/ProductShell.tsx` | all product routes/tests | global CSS, auth/route behavior | old re-export | NO after B0 | YES as cohesive module | BLOCKER |
| `ProductRouteFrame.tsx` | route detection/reset + `ProductRouteFrame` | public + internal | product route frame/document-scroll policy | shared layout | `shared/layout/ProductRouteFrame.tsx` | root layout/tests | URL patterns/scroll CSS | old re-export | NO | YES | HIGH |
| `ProductNavigation.tsx` | provider/hooks/link/navigation helpers | public + internal | client navigation/context | shared layout | `shared/layout/ProductNavigation.tsx` | shell/routes/tests | route/query | old re-export | NO | YES | HIGH |
| `LazyScientificViewers.tsx` | three lazy viewer loaders | public | dynamic viewer boundary | scientific viewers | `scientific-viewers/LazyScientificViewers.tsx` | data/research pages/tests | `next/dynamic` relative imports | old re-export | NO; move cohesive deps | YES only with refs | BLOCKER |
| `ScientificReportRoute.tsx` | report route/document/normalizers | public + internal | canonical report presentation | reports | `features/reports/ScientificReportRoute.tsx` | report routes/tests | report query + dynamic legacy reader import + CSS | old re-export | YES to remove legacy coupling | NO initially | HIGH |
| `ScientificReportsIndexPage.tsx` | index page/pagination | public + internal | report directory | reports | `features/reports/ScientificReportsIndexPage.tsx` | report route/tests | report APIs/CSS | old re-export | NO | YES | MEDIUM |

## Public Export Freeze

Before each Batch 0 or move PR, generate and store a machine-readable pre/post surface for the affected modules. Required comparison scope:

- all symbols explicitly listed above;
- all public top-level definitions/constants in affected Python modules;
- every route/dependency and queue handler;
- TypeScript named/default exports and test-imported helpers;
- test monkeypatch strings and module attributes;
- package `__init__` exports and `__getattr__` behavior.

`MOVE_WHOLE_FILE_ALLOWED=YES` never overrides a dynamic-contract or test-path gate.

## Static PUBLIC_EXPORT_SET Appendix

The following is the exact top-level definition/constant surface extracted from the listed Python modules without importing the application. Imported names, test patch targets and dynamic names are additionally governed by the contract scan and must be compared in each migration batch.

```text
apps/api/mdi_api/phase2_runtime.py:
PHASE2_TOOL_ORDER, DEFAULT_ARTIFACT_ROOT, CreateProjectRequest, InlineUploadFile, DatasetUploadRequest, CreateJobRequest, ProjectRecord, DatasetRecord, MaterializedUpload, UploadSessionFileRecord, UploadSessionRecord, JobRunRecord, LocalFileArtifactStore, Phase2ProductRuntime, build_phase2_plan, summarize_plan, build_object_store, list_phase2_projects, create_phase2_project, list_phase2_datasets, get_phase2_dataset, create_phase2_demo_dataset, upload_phase2_dataset, create_phase2_upload_session, put_phase2_upload_session_file, complete_phase2_upload_session, cancel_phase2_upload_session, get_phase2_dataset_profile, get_phase2_dataset_object_store, get_phase2_dataset_profile_model, create_phase2_dataset_profile, create_phase2_job, get_phase2_job, get_phase2_job_events, stream_phase2_job_events, get_phase2_job_tool_calls, get_phase2_job_artifacts, get_phase2_artifact, get_phase2_artifact_download, reset_phase2_runtime, get_phase2_runtime

apps/api/mdi_api/repositories.py:
ProjectRepository, DatasetRepository, DataProfileRepository, AnalysisPlanRepository, AnalysisIntentRepository, CapabilityPlanningRepository, DependencyExecutionRepository, JobRepository, JobEventRepository, ToolCallRepository, ArtifactRepository, RecipeRepository, ReportRepository, ScientificInterpretationRepository, WorkspaceRepository, InMemoryRepositoryBundle, InMemoryProjectRepository, InMemoryDatasetRepository, InMemoryDataProfileRepository, InMemoryAnalysisIntentRepository, InMemoryCapabilityPlanningRepository, InMemoryDependencyExecutionRepository, InMemoryAnalysisPlanRepository, InMemoryJobRepository, InMemoryJobEventRepository, InMemoryToolCallRepository, InMemoryArtifactRepository, InMemoryRecipeRepository, InMemoryReportRepository, InMemoryScientificInterpretationRepository, WorkspaceRepositoryError, WorkspaceConflictError, WorkspaceScopeError, WorkspaceCapacityError, WorkspaceNotFoundError, InMemoryWorkspaceRepository, SqlAlchemyRepositoryBundle, SqlAlchemyProjectRepository, SqlAlchemyDatasetRepository, SqlAlchemyDataProfileRepository, SqlAlchemyAnalysisIntentRepository, SqlAlchemyCapabilityPlanningRepository, SqlAlchemyDependencyExecutionRepository, SqlAlchemyAnalysisPlanRepository, SqlAlchemyJobRepository, SqlAlchemyJobEventRepository, SqlAlchemyToolCallRepository, SqlAlchemyArtifactRepository, SqlAlchemyRecipeRepository, SqlAlchemyReportRepository, SqlAlchemyScientificInterpretationRepository, SqlAlchemyWorkspaceRepository, canonical_analysis_plan_json, compute_plan_hash

apps/api/mdi_api/agent2_repositories.py:
ScientificObjectRepository, ResearchTurnRepository, ResearchContextSnapshotRepository, ResearchSessionMemoryRepository, ResearchTurnEventRepository, ScientificResultSnapshotRepository, ResearchTurnDecisionRepository, ResearchCapabilityResolutionRepository, ResearchCapabilityPlanRepository, ResearchExecutionSummaryRepository, Agent2ScientificInterpretationRepository, Agent2ScientificReportGenerationRepository, Agent2ScientificReportRepository, Agent2RepositoryBundle

apps/api/mdi_api/database.py:
create_engine_from_settings, dispose_cached_engines, create_repository_factory

apps/api/mdi_api/db.py:
PHASE1_TABLES, PHASE3_TABLES, PHASE4_TABLES, plus the module's table/metadata names consumed by migrations/repositories/tests; retain the complete module surface at the old path initially.

apps/api/mdi_api/workspaces.py:
WorkspaceDomainError, WorkspaceSnapshot, WorkspaceProjectionService

apps/api/mdi_api/report_composition.py:
REPORT_EXPORT_MAX_BYTES, ReportCompositionDomainError, CompositionPreview, ReportSourceEligibilityProjector, ReportCompositionService

apps/api/mdi_api/project_history.py:
PROJECT_HISTORY_SCHEMA_VERSION, ProjectHistoryService

apps/api/mdi_api/research_agent/service.py:
ResearchTurnService

apps/api/mdi_api/research_agent/planning/*.py:
CapabilityBinder, build_deterministic_capability_plan, PROMPT_VERSION, load_capability_planner_prompt, requires_llm_planning, ScientificCapabilityPlanner, CapabilityPlanningProcessor, PlanningQueueSubmitResult, DisabledCapabilityPlanningQueue, InMemoryCapabilityPlanningQueue, RedisRQCapabilityPlanningQueue, CapabilityPlanValidator, run_queued_planning

apps/api/mdi_api/scientific_objects/*.py:
ObjectTypeRegistry, InMemoryObjectTypeRegistry, build_default_object_type_registry, ScientificObjectKind, ScientificObjectAvailability, ScientificObjectLifecycle, ScientificObjectRef, ScientificObjectVersionRef, StorageRef, ScientificDatasetFilter, ScientificDatasetQueryRequest, ScientificObjectAdmissionRequest, ScientificObjectVersionCreateRequest, ObjectTypeManifest, ScientificObjectVersionContract, CANONICAL_RELATIONS, ScientificObjectService

apps/api/mdi_api/scientific_results/*.py:
ScientificResultSnapshotService, ScientificResultProjectionService, run_queued_result_projection, and the public schema/projector/queue/registry symbols listed by the package modules; preserve the complete package export surface and handler identity.

apps/api/mdi_api/scientific_reports/*.py:
ScientificReportError, ScientificReportService, ReportQueueSubmitResult, DisabledReportQueue, InMemoryReportQueue, RedisRQReportQueue, and the public schema/assembler/client/grounding symbols listed by the package modules; preserve the complete package export surface and handler identity.
```

Frontend named exports/route entrypoints frozen by static census:

```text
ProductPages.tsx: ConsolePage, ProjectsPage, ProjectOverviewPage, ProjectDataPage, DatasetUploadPage, ScientificDataView, TableScientificView
ResearchPages.tsx: ResearchPage, ResearchStarter, ResearchWorkbenchContent, ReportsPage, ReportReaderPage, ResearchTechnicalSummary, ViewerResearchContext, researchMessageWindow, agent2ContextManifestRenderItems, and all test-imported timeline/state helpers
PlannerWorkbench.tsx: PlannerWorkbench, GlobalContextBar, GlobalPrimaryNavigation, DataContextShell, MainWorkspaceTabs, AgentProcessTab, ConversationPlanTab, PlannerStageRail, AnalysisIntentPanel, CapabilityPlanningPanel, ResultsExportTab, GroundedInterpretationPanel, PlanPreviewPanel, DependencyExecutionPanel, ValidationResultPanel, MaterialResultRenderer, ArtifactGallery, ReportRecipeSummaryPanel, ToolCallList, ExportControls, and viewer preview helpers
ProductShell.tsx: ProductShell, ProductShellFrame, RequireProductAuth, ProductAuthFrame
ProductRouteFrame.tsx: ProductRouteFrame
ProductNavigation.tsx: ProductNavigationProvider, useProductNavigation, useProductRouter, ProductLink
LazyScientificViewers.tsx: LazyScientificResultViewer, LazyScientificSourceViewer, LazyScientificObjectViewer
ScientificReportRoute.tsx: ScientificReportRoute, ScientificReportDocument, LegacyReportReaderPage
ScientificReportsIndexPage.tsx: ScientificReportsIndexPage
```

This appendix is a static surface baseline, not proof that dynamic runtime registration or every historical monkeypatch has been executed. Such verification remains a required future batch gate.
