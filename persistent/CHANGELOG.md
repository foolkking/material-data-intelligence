# CHANGELOG

## 2026-07-03

### Phase 8C Frontend Planner UX

#### Added

- Added a `PlannerWorkbench` frontend page as the user-facing Planner Job creation entry point.
- Added typed frontend planner API helpers for `createPlannerJob`, planner job detail, persisted AnalysisPlan detail, JobEvents, ToolCalls, Artifacts, and Result summary.
- Added read-only backend planner endpoints under `/planner/...` so the frontend can display persisted `planId`/`planHash` provenance without mutating state or triggering execution.
- Added Vitest + React Testing Library setup for the frontend and tests covering success, persisted provenance, `plan.loaded`, validation failure, loading, and API error states.
- Added `tests/test_phase8c_planner_read_api.py` for read-only planner API provenance behavior.

#### Changed

- Replaced the static frontend shell with a functional analysis planner workbench.
- `POST /planner/jobs` is now exposed through a FastAPI wrapper that preserves the existing injectable implementation while accepting the expected JSON HTTP body.
- Local non-PostgreSQL planner routes now share a module-level in-memory repository bundle so a created planner job can be read back by subsequent read-only planner API calls during local/dev frontend use.
- Updated the scaffold test to assert the Phase 8C Planner workbench content instead of the old static shell.

#### Preserved

- Frontend job creation still goes only through `/planner/jobs`.
- The frontend does not directly write `analysis_plans`, directly create jobs, directly enqueue work, compute authoritative plan hashes, or treat deterministic fallback as the production path.
- Read-only planner endpoints do not enqueue, execute, mutate plans/jobs, or call `build_phase2_plan`.
- QueueWorkerRuntime, AnalysisPlanRepository, Tool Registry, and adapter execution semantics remain the Phase 8B baseline.

#### Verification

- `uv lock --check`: passed.
- Phase 8C backend targeted: 2 passed.
- Phase 8C + Phase 8B targeted: 11 passed, 1 skipped locally.
- Backend full: 112 passed, 20 skipped.
- Frontend: `npm ci`, `npm test` (4 passed), `npm run typecheck`, and `npm run build` passed in `apps/web`.
- Current HEAD CI verification remains pending until this Phase 8C commit is pushed.

### Phase 8B Persisted Plans + Queue Worker Runtime

#### Added

- Added Alembic revision `0002_phase8b_plans` for `analysis_plans` and nullable `jobs.plan_id`.
- Added `AnalysisPlanRepository` implementations for in-memory tests and SQLAlchemy/PostgreSQL runtime.
- Added stable canonical SHA-256 `plan_hash` for validated `AnalysisPlan` JSON.
- Added `tests/test_phase8b_persisted_plan_queue.py` covering repository round-trip/hash, planner persistence/enqueue behavior, validation-failure no-op, worker persisted-plan loading, exact 1-step execution, fallback behavior, and service-backed PostgreSQL + Redis + MinIO integration.

#### Changed

- `POST /planner/jobs` now validates first; invalid plans save no plan, create no job, and enqueue nothing.
- Valid `/planner/jobs` requests now persist the exact validated plan, create a Job linked by `plan_id`, return `plan_id`/`plan_hash`, and enqueue only `job_id` when requested.
- `QueueWorkerRuntime.handle_job(job_id)` now loads `job.plan_id` / `analysis_plans[plan_id]`, reconstructs `AnalysisPlan`, and executes exact persisted `steps`.
- Worker JobEvents, Artifact metadata, and `QueueWorkerResult` now include persisted plan provenance where available.
- QueueWorkerRuntime now initializes real adapter execution context from Tool Registry metadata for persisted-plan jobs, so the service-backed path can execute `ml.basic_metrics` without a fake executor.
- CI service-backed integration now runs Phase 6 plus Phase 8B integration and requires at least 19 passes with 0 skips.

#### Preserved

- LLM provider still only emits JSON plans and never executes code.
- PlanValidator remains the safety gate for unknown tools, non-MVP/V1/V2 tools, duplicate steps, empty steps, and credential-like params before persistence.
- Tool execution still goes through Tool Registry + Adapter; the deterministic fallback remains available only when no persisted plan is attached.

#### Verification

- `uv lock --check`: passed.
- Phase 8B targeted: 9 passed, 1 skipped locally (integration gated).
- Phase 8A targeted: 11 passed.
- Phase 7 targeted: 22 passed.
- Backend full: 110 passed, 20 skipped.
- Frontend: `npm ci`, `npm run typecheck`, `npm run build` passed in `apps/web`.
- Local service-backed integration: not run because Docker CLI is unavailable on this machine.
- CI run `28631817086` on Phase 8B code acceptance commit `962c429`: Unit Tests, Frontend Typecheck & Build, and Service-backed Integration all passed. Integration summary: 19 passed, 0 skipped, 0 failed.

## 2026-06-27

### Phase 8A LLM Plan Execution Bridge

#### Added

- `tests/test_phase8a_plan_execution.py` (7 tests) — core proof: 1-step LLM plan → exactly 1 ToolCall (not deterministic 5).

#### Changed

- `Phase2ProductRuntime.create_job` accepts `analysis_plan` (execute this exact validated plan) and `execute` (False = planned-only) parameters.
- `POST /planner/jobs` executes the EXACT validated LLM plan when execute=True; planned-only when execute=False. Response now includes plan_source + executed.
- `MockLLMProvider` plan references the `ml_table` normalized object so the validated plan is executable end-to-end.

#### Preserved

- Deterministic `build_phase2_plan` remains the fallback when no analysis_plan is provided (Phase 2/3 loop unchanged).
- All execution still flows through Tool Registry + Adapter; PlanValidator unchanged (invalid/unknown/V1-V2 rejected before job).

#### Verification

- backend: 97 passed, 19 skipped, 0 failed
- Phase 7 targeted: 22 passed
- frontend typecheck/build: passed
- uv lock + git diff --check: clean

## 2026-06-27

### Phase 7 LLM JSON Planner + BYOK Secret Management

#### Added

- LLMPlannerProvider abstraction + MockLLMProvider + OpenAICompatibleProvider + DeterministicPlannerAdapter
- Planner prompt template (JSON-only, tool-aware, DataProfile context)
- PlanValidator (strict mode, 10 rules, structured errors)
- Planner API: POST /planner/preview, /planner/validate, /planner/jobs
- SecretStore abstraction + InMemorySecretStore + EncryptedSecretStore placeholder
- Secrets API: POST/GET/DELETE /me/secrets
- Secret redaction helpers (credential detection, value scrubbing)
- 19 Phase 7 tests (no real LLM key required)

#### Verification

- `python -m pytest -q`: 87 passed, 19 skipped
- Frontend typecheck/build: passed
- `uv lock --check`: passed

## 2026-06-26

### Phase 6: Service-backed Runtime Smoke & Integration Hardening

#### Added

- Added 18 service-backed integration smoke tests under `tests/test_phase6_integration.py`:
  - Docker compose services reachability (PostgreSQL, Redis, MinIO).
  - Alembic live migration: real `alembic.command.upgrade(alembic_cfg, "head")` with downgrade+reupgrade cycle + index checks (not metadata.create_all).
  - PostgreSQL repository live integration: Project, Dataset, Job/ToolCall/Artifact, Recipe/Report, transaction rollback, status transition rejection.
  - PostgreSQL JobEvent seq live: monotonic seq, advisory lock strategy, 30-event concurrent correctness.
  - Redis queue live: enqueue/dequeue, QueueWorkerRuntime with live PG repos.
  - Queue retry idempotency: duplicate job handle, crash+retry with live repos.
  - MinIO live: put/get/exists/signed-url for json/text/bytes, signed URL structure validation.
  - Service-backed product-loop smoke: PG repos + Redis queue + MinIO storage + real Tool Registry + BasicMetricsAdapter (not fake executor).
  - Alembic `metadata.create_all` live table creation verification against PostgreSQL.
  - PostgreSQL repository live integration: Project, Dataset, Job/ToolCall/Artifact, Recipe/Report, transaction rollback, and status transition rejection.
  - PostgreSQL JobEvent seq live integration: monotonic seq, advisory lock strategy, concurrent append seq correctness.
  - Redis queue live integration: enqueue/dequeue, QueueWorkerRuntime with live PG repos + Redis queue backend.
  - Queue retry idempotency live smoke: duplicate job handle, crash+retry with live repositories.
  - MinIO live integration: put/get/exists/signed-url for json/text/bytes, signed URL structure validation.
  - Service-backed product-loop smoke: PG repos + Redis queue + MinIO storage + MVP Adapter end-to-end.
- Updated `docs/16_RUNTIME_INFRASTRUCTURE_RUNBOOK.md` with Phase 6 sections: integration test environment variables, per-category test descriptions, MinIO bucket cleanup, troubleshooting for common errors (connection refused, migration failed, bucket not found, signed URL invalid).
- Updated `.env.example` with `MDI_RUN_INTEGRATION` and `MDI_TEST_DATABASE_URL` opt-in variables.

#### Changed

- Fixed `docker-compose.yml` MinIO healthcheck to use `mc ready local` instead of `curl` for reliability.
- Fixed `tests/test_phase6_integration.py` Docker compose reachable test to use proper `SELECT 1` query and MinIO put+exists verification.
- Fixed `tests/test_phase6_integration.py` Alembic table test to remove broken dialect statement compilation.
- Added Phase 6 runbook sections 11-12: integration test guide and troubleshooting.

#### Scope Guard

- Did not add real LLM API calls, V1/V2 tool execution, BYOK UI, full auth, Kubernetes/Ray/autoscaling, plugin market work, or frontend redesign.
- All 18 integration tests skip cleanly when Docker services are not available or `MDI_RUN_INTEGRATION` is not set to `1`.
- Queue worker default execution still goes through `ToolExecutionRequest` -> Tool Registry validation -> Adapter execution.

#### Verification

- `python -m pytest -q`: 68 passed, 19 skipped, 50 third-party warnings.
- `python -m pytest tests/test_phase6_integration.py -q`: 18 skipped (Docker not available).
- `uv lock --check`: passed.
- `npm ci`: passed.
- `npm run typecheck`: passed.
- `npm run build`: passed.
- `git diff --check`: passed with Windows line-ending notices only.

### Phase 5 PostgreSQL Runtime + Queue Worker + MinIO Integration Update

#### Added

- Added runtime config support for `DATABASE_URL`, `POSTGRES_*`, `REDIS_URL`, and `MINIO_*` variables while preserving existing `MDI_*` aliases.
- Added `apps/api/mdi_api/database.py` with SQLAlchemy engine and repository-factory helpers.
- Added `docs/16_RUNTIME_INFRASTRUCTURE_RUNBOOK.md` for PostgreSQL, Redis/RQ, MinIO, Alembic, and integration-test operations.
- Added `QueueWorkerRuntime`, `InMemoryQueueBackend`, and `RedisRQQueueBackend` under `services/workers/mdi_workers`.
- Added Phase 5 tests for config parsing, Alembic/runbook presence, PostgreSQL JobEvent advisory-lock strategy, queue retry idempotency, S3/MinIO live-client behavior, signed URLs, and `after_seq` regression.

#### Changed

- Updated `.env.example` and `docker-compose.yml` for local PostgreSQL, Redis, and MinIO runtime services.
- Updated Alembic env handling so configured runtime database URLs can drive `alembic upgrade head`.
- Extended `S3CompatibleArtifactStorage` from metadata mapping only to optional live boto3-compatible object operations and presigned URL generation.
- Hardened SQLAlchemy JobEvent seq allocation with a PostgreSQL transaction-scoped advisory lock while keeping SQLite tests on the existing local lock path.
- Refreshed `uv.lock` after adding Phase 5 runtime dependencies: boto3, psycopg, redis, and rq.

#### Scope Guard

- Did not add real LLM API calls, V1/V2 tool execution, BYOK UI, full auth, Kubernetes/Ray/autoscaling, plugin market work, or frontend redesign.
- Queue worker default execution still goes through `ToolExecutionRequest` -> Tool Registry validation -> Adapter execution.

#### Verification

- `python -m pytest tests/test_phase5_runtime_infrastructure.py -q`: 7 passed, 1 skipped.
- `python -m pytest -q`: 68 passed, 1 skipped, 50 third-party warnings.
- `python -m pytest -q -m integration`: 1 skipped because Docker-backed services were not enabled.
- `uv lock --check`: passed.
- `npm ci`: passed.
- `npm run typecheck`: passed.
- `npm run build`: passed.
- `git diff --check`: passed with Windows line-ending notices only.

### Phase 4 Production Persistence Hardening Update

#### Added

- Added Alembic baseline files under `apps/api/alembic` and a Phase 4 migration baseline SQL string.
- Added `RepositorySession`, `UnitOfWork`, and `RepositoryFactory` for explicit transaction boundaries.
- Added centralized Job and ToolCall status transition validation.
- Added Phase 4 persistence tests for migration smoke coverage, SQLAlchemy CRUD, rollback, status transitions, idempotent writes, concurrent JobEvent seq allocation, and stable `after_seq` ordering.

#### Changed

- Added `alembic` to Python dependencies and refreshed `uv.lock`.
- Hardened SQLAlchemy metadata with Job/ToolCall status constraints, ToolCall `idempotency_key` and `attempt`, `uq_tool_calls_job_step`, `uq_tool_calls_job_idempotency_key`, artifact storage-provider checks, and `uq_artifacts_job_storage_sha`.
- Made SQLAlchemy and InMemory ToolCall writes idempotent by stable job step/idempotency key.
- Made SQLAlchemy and InMemory Artifact metadata writes idempotent by stable job/storage/sha identity.
- Updated Python and TypeScript shared schemas with `ToolCallStatus`, `idempotencyKey`, and `attempt`.
- Updated worker runtime ToolCall status writes to use the shared enum.

#### Scope Guard

- Did not add real LLM API calls, V1/V2 tool execution, Celery/Ray/Kubernetes, full auth, live PostgreSQL runtime wiring, live S3/MinIO clients, or frontend rewrites.

#### Verification

- `python -m pytest tests/test_phase4_persistence_hardening.py -q`: 8 passed.
- `uv lock --check`: passed.
- `python -m pytest -q`: 61 passed, 50 third-party warnings.
- `npm ci`: passed.
- `npm run typecheck`: passed.
- `npm run build`: passed.
- `git diff --check`: passed with Windows line-ending notices only.

### Phase 3 Acceptance Hardening Update

#### Added

- Added `DataProfileRepository` and `ReportRepository` to InMemory and SQLAlchemy repository bundles.
- Added repository acceptance coverage for DataProfile, Report, concurrent JobEvent seq appends, ArtifactStorage helpers, S3/MinIO mapping metadata, SSE payload aliases, and API artifact routes.
- Added `apps/web/tsconfig.typecheck.json` so frontend typecheck no longer depends on `.next/types` being present.

#### Changed

- Hardened JobEvent seq allocation with in-process locks for repository and local worker append paths.
- Expanded artifact storage metadata with `storage_provider`, `bucket`, `content_type`, `sha256`, `size_bytes`, `preview_key`, and `created_at` coverage.
- Updated SQLAlchemy metadata, migration draft, Python/TypeScript schemas, and `docs/13_SHARED_SCHEMA_SPEC.md` for storage mapping fields.
- Phase 2 artifact summaries/details now expose local storage provider, content type, sha256, and created time metadata.

#### Fixed

- Fixed a frontend P0 where `npm run typecheck` failed in clean environments without pre-existing `.next/types`.
- Fixed an InMemory DataProfile project-listing gap when datasets were stored with `id` but no `datasetId` alias.

#### Verification

- `npm ci`: passed.
- `uv lock --check`: passed.
- `python -m pytest -q`: 53 passed, 50 third-party deprecation warnings.
- `npm run typecheck`: passed from clean `.next` state.
- `npm run build`: passed.

### Phase 3 Persistence Foundation Update

#### Added

- Added `apps/api/mdi_api/repositories.py` with Project, Dataset, Job, JobEvent, ToolCall, Artifact, and Recipe repository interfaces.
- Added InMemory repository implementations and SQLAlchemy Core repository implementations for SQLite-compatible tests and PostgreSQL-oriented persistence.
- Added `apps/api/mdi_api/artifact_storage.py` with local filesystem storage and S3/MinIO-compatible mapping interface.
- Added `apps/api/mdi_api/migrations.py` with Phase 3 SQL migration draft for projects, datasets, data_profiles, jobs, job_events, tool_calls, artifacts, visualization_recipes, and reports.
- Added `GET /jobs/{job_id}/stream` SSE smoke endpoint.
- Added `GET /artifacts/{artifact_id}/download` local signed-url/download placeholder.
- Added `tests/test_phase3_persistence.py` for repository, cursor, SSE, storage mapping, and Phase 2 regression coverage.

#### Changed

- Extended `job_events` metadata with `progress` and preserved unique `(job_id, seq)` cursor semantics.
- Extended `artifacts` metadata with storage mapping fields: `version`, `preview_key`, `size_bytes`, `content_type`, and `sha256`.
- Added `reports` metadata table and Phase 3 table list coverage.
- `GET /jobs/{job_id}/events` now supports `after_seq=N`.
- Phase 2 artifact summaries now point download links to `/artifacts/{artifact_id}/download`.
- `InMemoryJobStore` now supports `list_events_after_seq(job_id, after_seq)`.
- `npm run typecheck` now disables incremental cache reuse to avoid stale `.next/types` references from prior builds.

#### Scope Guard

- Did not add real LLM API calls, V1/V2 tools, Celery/Ray/Kubernetes, full auth, production PostgreSQL wiring, live S3/MinIO clients, or frontend rewrites.

#### Verification

- `uv lock --check`: passed.
- `python -m pytest -q`: 52 passed, 50 third-party deprecation warnings.
- `npm run typecheck`: passed.
- `npm run build`: passed.

## 2026-06-25

### Phase 2 Acceptance Hardening Update

#### Changed

- Aligned generated `AnalysisPlan.expectedArtifacts` with the shared schema shape `{name, type, fromStepId}`.
- Aligned Phase 2 job-level Recipe JSON with `VisualizationRecipe.steps`: each step now includes `toolVersion` and `inputBindings` as a string-to-string map.
- Added named shared schema types for `ExpectedArtifact` and `VisualizationRecipeStep` in Python and TypeScript.
- Local-path dataset uploads now parse the copied raw file under the Phase 2 artifact root instead of the caller's original path.
- Updated stale schema/status documentation in `docs/01_PRODUCT_REQUIREMENTS.md` and `README.md`.

#### Added

- Added Phase 2 regression assertions for planner expected artifacts and Recipe step shape.

#### Verification

- `python -m pytest -q`: 48 passed, 45 third-party deprecation warnings.
- `npm ci`: passed.
- `npm run typecheck`: passed.
- `npm run build`: passed.
- Manifest audit: registry version `0.1.0`, 10 MVP tools.
- Phase 2 loop audit: completed with 5 tool calls and 25 artifacts.

### Phase 2 Local Product Loop Update

#### Added

- Added `apps/api/mdi_api/phase2_runtime.py`, a deterministic in-memory product runtime for Phase 2.
- Added local runtime support for:
  - project creation
  - dataset upload from local paths or inline small text files
  - parser/profile execution
  - deterministic AnalysisPlan generation
  - LocalWorkerRuntime ToolCall execution
  - Artifact export and lookup
  - JobEvent recording
  - job-level Recipe JSON generation
  - Markdown/HTML report generation
- Added Phase 2 API routes for dataset upload/profile, job create/query, job events, tool calls, job artifacts, and artifact detail lookup.
- Added `LocalFileArtifactStore` for local-file-backed artifact metadata/content retrieval.
- Added `tests/test_phase2_product_loop.py`, covering data pipeline, deterministic planner, job runtime, artifact store, API routes, and end-to-end product flow.

#### Changed

- `POST /projects`, `GET /projects`, and `GET /datasets` now read from the Phase 2 in-memory runtime instead of static stubs.
- `.gitignore` now ignores `material-data-intelligence-*.zip` handoff archives.

#### Scope Guard

- Did not add real LLM API calls, full auth, V1/V2 tools, Celery, PostgreSQL, MinIO, or frontend feature expansion.

#### Verification

- `python -m pytest -q`: 48 passed, 45 third-party deprecation warnings.
- Frontend typecheck/build were not rerun because no frontend files changed in this Phase 2 round.

### Phase 1 Engineering Hardening Update

#### Added

- Added `uv.lock` for Python dependency locking.
- Added `apps/web/package-lock.json` for frontend dependency locking with npm.
- Added `.gitignore` coverage for `*.egg-info/`.

#### Changed

- Phase 1 verification now runs against an isolated uv-managed `.venv` instead of relying on the shared Anaconda environment.
- Frontend verification now uses lockfile-based install semantics via `npm ci`.

#### Verification

- `uv lock --check`: passed.
- `uv sync --extra test --frozen`: passed.
- `python -m pytest -q`: 42 passed from the uv-managed `.venv`.
- `npm ci`: passed.
- `npm run typecheck`: passed.
- `npm run build`: passed.

### Phase 1 Product Acceptance Update

#### Added

- Added `apps/api/mdi_api/phase1_demo.py`, a deterministic Phase 1 product-flow runtime.
- Added Phase 1 API boundaries for:
  - `POST /projects`
  - `POST /projects/{project_id}/upload-sessions`
  - `POST /analysis-requests`
  - `GET /jobs/{job_id}/events`
  - `GET /jobs/{job_id}/events/stream`
  - `GET /jobs/{job_id}/artifacts`
- Added product-flow table metadata for data profiles, field mappings, sessions, messages, jobs, job events, tool calls, artifacts, visualization recipes, configs, secrets, and audit logs.
- Added `tests/test_phase1_product_acceptance.py`, covering CIF, POSCAR, CSV, ZIP, JSON limited, XYZ, EXTXYZ, Data Profile, AnalysisPlan, 10 MVP tools, artifacts, report, and JobEvents.

#### Changed

- Plotly preview export now writes a minimal valid PNG fallback when image export is unavailable, so Phase 1 preview artifacts are stable in environments without Kaleido/Chromium.
- Frontend workspace shell now includes visible Phase 1 surfaces for Agent Timeline, composition charts, 3D Viewer, ML Evaluation, Logs, Artifacts, Recipe, and Report.
- `mdi_schemas.__init__` now exports `InputRef` for shared-schema consumers.

#### Verification

- `python -m pytest -q`: 42 passed, 25 warnings from third-party deprecations.
- `npm run typecheck`: passed.
- `npm run build`: passed.

### Added

- 新增 Phase 1 API scaffold：`apps/api/mdi_api`，包含 FastAPI app factory、配置加载、health/auth/project/dataset/tools 路由边界。
- 新增基础 SQLAlchemy Core 表元数据：`users`、`organizations`、`projects`、`project_members`、`datasets`、`files`。
- 新增本地基础设施配置：`docker-compose.yml` 覆盖 PostgreSQL、Redis、MinIO；`.env.example` 只保留占位符。
- 新增 Next.js workspace shell：`apps/web/package.json`、`next.config.mjs`、`tsconfig.json`、App Router 页面和三栏工作台样式。
- 新增 `pnpm-workspace.yaml`，将 `apps/web` 纳入前端 workspace。
- 新增 `tests/test_phase1_scaffold.py`，覆盖 API route、基础表 metadata、compose 服务和前端 shell 文件。
- 新增 `tests/test_manifest_loader.py::test_mvp_tools_reject_unregistered_params`，校验 10 个 MVP 工具的 `paramsSchema` 均拒绝未注册参数。
- 新增 Python/Pydantic `JobEvent` 共享模型，并从 `mdi_schemas` 包入口导出。
- 新增 TypeScript 共享核心类型：`JobStatus`、`JobEventStatus`、`JobEvent`、`InputRef`、`ToolExecutionRequest`、`ToolCall`、`ArtifactMetadata`、`Artifact`、`AnalysisStep`、`AnalysisPlan`、`DataProfile`、`VisualizationRecipe`。
- 新增 `tests/test_shared_schemas.py`，校验 Python 与 TypeScript schema 入口暴露本阶段要求的核心类型。
- 新增库层受控执行入口 `packages/adapters/mdi_adapters/executor.py`，提供 `execute_tool_request()` 和 `ToolExecutionResult`。
- 新增 `tests/test_tool_executor.py`，覆盖 Registry 路由、paramsSchema 拒绝、未注册工具拒绝和 in-memory cache hit。
- 新增最小 Worker runtime：`services/workers/mdi_workers/runtime.py`，提供 `run_tool_call_job()`、`InMemoryJobStore`、`WorkerRunResult` 和 `WorkerToolExecutionError`。
- 新增 `tests/test_worker_runtime.py`，覆盖 ToolCall 状态、JobEvent 序列、`artifact.ready` 事件和失败路径 Secret 脱敏。
- 新增 pytest workspace-local basetemp 配置：`--basetemp=.pytest_tmp`，避免受限运行环境访问系统临时目录失败。
- 新增 plain XYZ 非周期对象质量提示：`NON_PERIODIC_ATOMS`。
- 新增 `.extxyz` 检测与 ASE->Structure 周期转换支持测试。
- 新增 ZIP 安全解包回归测试。
- 新增 normalized object 稳定落盘 helper：`LocalArtifactExporter.export_normalized_object()`。
- 新增根级 `pyproject.toml`，配置 Python 包发现、pytest 路径和核心依赖。
- 新增工程骨架：`apps/web`、`apps/api`、`services/workers`、`packages/schemas`、`packages/tool-registry`、`packages/adapters`、`packages/material-parsers`、`packages/artifact-core`、`tests/fixtures`。
- 新增共享 Schema 实现：
  - `packages/schemas/mdi_schemas/models.py`
  - `packages/schemas/json/registered-tool.schema.json`
  - `packages/schemas/src/index.ts`
- 新增 Tool Registry manifest loader：`packages/tool-registry/mdi_tool_registry/loader.py`。
- 新增本地 Artifact exporter：`packages/artifact-core/mdi_artifact_core/exporter.py`。
- 新增 Adapter runtime：`BaseToolAdapter`、`ToolExecutionContext`、`ToolExecutionError`、adapter class registry 和 Plotly exporter。
- 新增前三个 MVP Adapter：
  - `PTableHeatmapAdapter`
  - `Structure3DAdapter`
  - `StructureViewer3DAdapter`
- 新增测试：
  - manifest loader 校验和计数测试。
  - BaseToolAdapter 生命周期、错误标准化和 Secret 参数拦截测试。
  - 三个 Adapter smoke tests。
  - Artifact storage key、metadata 和 recipe 测试。
- 新增 Data Pipeline 最小库层：
  - `detect_format()` 支持 CIF、POSCAR/CONTCAR、CSV、JSON limited、ZIP、XYZ/EXTXYZ 识别。
  - `parse_file()` / `parse_dataset()` 支持 CIF/POSCAR、CSV、JSON limited 解析。
  - `build_data_profile()` 生成 structure/table summary、quality issues 和 recommended tasks。
  - normalized object draft 记录 object type、metadata、hash、storage key 和 payload。
- 新增 Data Pipeline fixtures 和测试：`POSCAR`、`plain.xyz`、`ml_results.csv`、`tests/test_data_pipeline.py`。
- 新增剩余 7 个 MVP Adapter：
  - `ElementsHistAdapter`
  - `ChemSysTreemapAdapter`
  - `CoordinationHistAdapter`
  - `DensityScatterAdapter`
  - `ErrorDistributionAdapter`
  - `BasicMetricsAdapter`
  - `OutlierTableAdapter`
- 新增 ML adapter 公共校验与计算 helper：DataFrame / records 输入、target/prediction 字段推断、数值列校验、回归指标和 outlier 排序。
- 新增 10 个 MVP adapter class registry 覆盖测试和 7 个新增 Adapter smoke tests。

### Changed

- 将 Milestone 1 从 placeholder/scaffold 第一段推进为可验证 scaffold 完成：API、infra、Auth/Project/Dataset 表 metadata、Next.js shell 均有测试或构建证据。
- 更新 `pyproject.toml`，加入 `apps/api` package discovery / pytest path，并声明 `fastapi`、`sqlalchemy`、`uvicorn` 和 `starlette>=0.40,<0.47`。
- 更新 `README.md`、`apps/api/README.md`、`apps/web/README.md` 和 persistent 状态，记录 Phase 1 当前边界与验证结果。
- 收紧剩余 7 个 MVP 工具的 `paramsSchema`，从宽松 `additionalProperties: true` 改为平台批准参数白名单：
  `composition.elements_hist`、`composition.chem_sys_treemap`、`structure.coordination_hist`、`ml.density_scatter`、`ml.error_distribution`、`ml.basic_metrics`、`ml.outlier_table`。
- 更新 persistent 状态，记录新会话恢复核验、Git 工作区状态、测试命令和 Tool Registry 参数白名单补强。
- 将共享 Schema 实现从 Python 优先补齐为 Python + TypeScript 双入口覆盖；JSON Schema 当前仍以 `registered-tool.schema.json` 作为 manifest loader 校验基线。
- Adapter 执行路径从“测试直接实例化 Adapter”补强为可通过 `execute_tool_request()` 统一完成 Registry lookup、输入解析、参数校验、cache key 计算和 Adapter 路由。
- Worker 服务从 placeholder 推进为最小库层语义基线，可记录 Job / ToolCall / JobEvent，但仍不声明 Celery、PostgreSQL 或 SSE 已完成。
- plain XYZ Data Pipeline 语义从“unsupported”对齐为“解析成功的非周期 `Atoms`”，但仍不允许进入 `periodic_required` 的结构工具。
- `.extxyz` 现在按扩展名优先识别，避免落入 unknown。
- 将 Milestone 0 / Milestone 1 第一段从设计基线推进到可运行代码闭环。
- 采用 packages-first 实现结构：API、Web、Worker 先保留运行入口壳，可复用逻辑进入 `packages/`。
- 将 `composition.ptable_heatmap` 的平台参数先通过 adapter 聚合为 element value map，再调用真实 `pymatviz.ptable_heatmap(values)`。
- 将 `structure.viewer_3d` 的 snapshot 保持 optional，MVP 输出 `viewer.html` / `structure.json` / `summary.md` / `recipe.json`。
- 将 `DataProfile` Pydantic model 补齐 `structureSummary`、`tableSummary`、`phononSummary`、`trajectorySummary` 可选字段。
- `pyproject.toml` 显式加入 `pandas>=2.2`。
- 将所有 10 个 MVP manifest adapter 注册到 `ADAPTER_CLASSES`，让 Registry 中的 MVP 工具都能实例化执行库层 smoke path。
- `composition.elements_hist` 的标题设置改为 `fig.update_layout(title_text=...)`，避免将无效 `title` 传给 Plotly `go.Figure(**fig_kwargs)`。

### Fixed

- 修复当前运行环境中 `fastapi 0.115.12` 与 `starlette 1.0.0` 不兼容导致 API app 无法创建的问题；当前 Starlette 运行版本为 `0.46.2`。
- 修复 MVP 工具中 7 个 Adapter 仍允许任意未知参数通过 Tool Registry `paramsSchema` 的缺口。
- 修复受限 sandbox 下 `pytest tmp_path` 访问系统临时目录导致的测试失败。
- 修复 Data Pipeline 测试与设计语义不一致的问题：plain XYZ 不再被期待为 parser failure，而是作为非周期 Atoms 边界处理。
- 修复 `.extxyz` 无法被识别的问题。
- 修正 JSON Schema 中 `ToolInputSchema.periodicity`，允许可选字段导出为 `null`。
- 解决当前运行环境中 `pymatviz` 与 NumPy 2.x 相关二进制依赖导入问题：升级 `xarray`、`pyarrow`、`numexpr`、`bottleneck`、`shapely`、`scikit-image`。
- 修正 pandas dtype 检测，避免使用即将移除的 `is_categorical_dtype`。

### Verification

- `python -m pytest -q`：41 passed，20 warnings；新增 Phase 1 scaffold 后通过。
- `npm run typecheck`：passed。
- `npm run build`：passed；Next.js 15.5.19 production build succeeded。
- `python -m pytest -q`：36 passed，20 warnings；恢复核验基线。
- `python -m pytest -q`：37 passed，20 warnings；新增 MVP paramsSchema 白名单测试后通过。
- `python -m pytest`：17 passed。
- `python -m pytest`：25 passed。
- `python -m pytest`：25 passed。
- `python -m pytest -q`：30 passed，20 warnings；warnings 为 matplotlib/Jupyter/ipywidgets 依赖弃用提示。
- `python -m pytest -q`：34 passed，20 warnings；warnings 为 matplotlib/Jupyter/ipywidgets 依赖弃用提示。
- `python -m pytest -q`：36 passed，20 warnings；warnings 为 matplotlib/Jupyter/ipywidgets 依赖弃用提示。

## 2026-06-24

### Added

- 创建 `docs/10_USER_CONFIG_AND_SECURITY.md`。
- 创建 `docs/index.md`。
- 创建 `docs/11_MATERIAL_DOMAIN_EXTENSIONS.md`。
- 创建 `docs/12_MVP_ROADMAP.md`。
- 创建 `README.md`、`AGENTS.md`、`MASTER_PROMPT.md` 作为仓库入口和 Agent 工作规则。
- 创建 `docs/03A_FRONTEND_COMPONENT_SPEC.md`。
- 创建 `docs/03B_FRONTEND_STATE_AND_INTERACTION.md`。
- 创建 `docs/13_SHARED_SCHEMA_SPEC.md`。
- 创建 `docs/14_PYMATVIZ_CAPABILITY_INVENTORY.md`。
- 创建 `docs/15_ADAPTER_IMPLEMENTATION_PLAN.md`。
- 创建 `tool_registry/pymatviz_manifest.yaml`、`tool_registry/matterviz_manifest.yaml`、`tool_registry/platform_builtin_manifest.yaml`。
- 在共享 Schema 中补充 `FileProfile`、`ObjectProfile`、`QualityIssue`、`RecommendedTask`、`InputRef`、`ToolExecutionRequest` 和 `Molecule`。
- 新增 ADR-041：MVP Worker 沙箱采用 Docker/容器隔离，进程级隔离不足。
- 新增 ADR-042：MVP 支持用户级 BYOK，组织级共享 Key 推迟到 V1。
- 新增 ADR-043：Secret 使用 envelope encryption，明文不进入日志、prompt、Artifact 或导出包。
- 新增 ADR-044：Prompt injection MVP 使用规则检测 + 上下文隔离 + Plan Validator。
- 新增 ADR-045：插件默认无网络、无 Secret、无 shell，必须显式声明能力。
- 新增 ADR-046：MVP 实现顺序按“数据闭环优先于高级功能”。
- 新增 ADR-047：专业材料领域扩展单独成文，但不改变 MVP 实现顺序。
- 新增 ADR-048：`docs/` 和 `persistent/` 必须进入 Git 版本管理。
- 新增 ADR-049：统一 ArtifactType / DisplayTarget / ToolCategory / ToolDomain。
- 新增 ADR-050：ToolInputSchema 使用 inputOptions 表达 OR 输入。
- 新增 ADR-051：MVP table/metrics artifact 是一等产物。
- 新增 ADR-052：plain XYZ 不进入周期性结构工具，除非有 lattice。
- 新增 ADR-053：MVP MatterViz snapshot 可选，viewer.html + metadata.json 为必需。
- 新增 ADR-054：Redis 不作为任务事实源，PostgreSQL 是唯一状态源。
- 新增 ADR-055：用户级 BYOK 按 job runner 解析，不写入 Recipe。
- 新增 ADR-056：V1 phonon 优先支持 phonopy.yaml + band.yaml，DOS 第二批。
- 新增 ADR-057：V1 composition clustering 默认 Magpie + PCA baseline，UMAP 可选。
- 新增 ADR-058：pymatviz 作为 primary visualization kernel。

### Changed

- 将设计进度推进到 Phase 11：MVP Roadmap。
- 将 Phase 10 标记为完成。
- 将 Phase 11 移入任务看板 In Progress。
- 将 Phase 11 标记为完成。
- 将设计阶段标记为完成，下一步进入代码实现准备。
- 根据目标文件清单补齐专业材料领域扩展文件。
- 修正 `docs/06_TOOL_REGISTRY_AND_ADAPTER.md` 中 phonon / trajectory 工具阶段归属，与 ADR 和 Roadmap 保持一致。
- 更新 `docs/12_MVP_ROADMAP.md` 的设计完成标准，纳入 `docs/11_MATERIAL_DOMAIN_EXTENSIONS.md`。
- 完成逐文件审核，修正产品需求和前端设计中的 MVP/V1 工具表述。
- 更新 `persistent/PROJECT_BRIEF.md`、`persistent/DESIGN_PROGRESS.md`、`persistent/TASK_BOARD.md` 和 `persistent/TOOL_REGISTRY_NOTES.md`，记录领域扩展补充文件和逐文件审核结果。
- 修正 `.gitignore`，确保 `docs/` 和 `persistent/` 被 Git 跟踪。
- 统一 MVP/V1 工具范围：MVP 为 10 个核心工具，V1 扩展 parity、uncertainty、error-by-domain、phonon、trajectory、RDF/XRD。
- 将 `ToolInputSchema` 改为 `inputOptions` 多输入方案，并增加 `implementationSource`、`ToolDomain` 和 `periodicity` 约束。
- 将 `metrics_json`、`table_json`、`table_csv`、`quality_issues_json` 纳入 Artifact 类型。
- 修正 JSON limited、ZIP 容器、plain XYZ / EXTXYZ 与周期结构工具边界。
- 调整 MatterViz snapshot、SVG/PDF high-resolution export 的阶段归属。
- 补充 JobEvent 数据库索引、事件保留和日志保留策略。
- 修改 BYOK 规则：用户级 Secret 按 job runner 解析，Recipe 只保存 provider 能力需求。
- 统一 `artifactTypes` 命名，移除旧的 format 语义残留。
- 将 Phase 0 旧 Schema 草案替换为共享 Schema 引用。
- 修正 Phase 3 `activeTab` 为 `DisplayTarget`。
- 修正 Phase 4 `job_events` 表字段，增加 `seq`、`progress`、`created_at`，并说明同一 job 内 seq 单调递增。
- 修正 Phase 12 Milestone 3 的工具数量冲突，统一为 10 个 MVP Tool Executor / Adapter。
- 将 Phase 7 推荐任务补充 `stage`、`availableNow`、`requiredTools` 和 `reason` 语义。
- 将 Phase 2 / Phase 8 的异步任务列表拆分为 MVP 与 V1。
- 统一 Redis 表述为 broker/cache/transient state；Celery result backend 不作为业务事实源。
- 在 `README.md` 增加对外交付压缩包排除 `.git/` 的说明。
- 统一 JobEvent status 为 `info/running/success/warning/error`，移除产品/架构草案中的 `pending`。
- 移除 retry 专用 JobStatus，改为 ToolCall retry 创建新的 attempt record。
- 将用户配置中的导出偏好改为 `defaultDownloadFormats` / `default_download_formats`，避免和内部 `ArtifactType` 混淆。
- 明确 Plotly Adapter MVP 推荐输出 `figure.html` 与 `preview.png`，SVG/PDF 进入 V1。
- 拆分 MVP 工具实现标准与端到端演示标准：10 个 MVP 工具均需注册、校验并可执行，Demo 至少覆盖 6 个核心工具且包含 composition、structure、ml。
- 统一 Plotly MVP 输出口径：`figure.json` 为必需；需要前端交互展示的 Adapter 必须提供 `figure.html` 或可直接渲染的 `plotly_json`，`preview.png` 为 MVP 推荐输出。
- 修正 Phase 2 `JobEvent`，补齐 `seq` 和 `progress`；`ArtifactRecord` 改为引用共享 `Artifact`。
- 补齐 Phase 4 数据库表字段：`jobs`、`tool_calls`、`artifacts`、`audit_logs` 等加入索引依赖的时间字段。
- 修正 MVP Secret API：使用 `/me/secrets` 管理用户级 BYOK，项目级共享 Secret API 推迟到 V1；项目只配置 LLM provider policy。
- 修正 Agent Timeline 事件结构，加入 `info` status、`id`、`jobId`、`seq` 和 `createdAt`，并声明其为 `JobEvent` 前端投影视图。
- 修正 Phase 1 MVP 验收标准，使其与 Phase 12 一致：10 个 MVP 工具均需注册、校验并可执行，端到端演示至少覆盖 6 个并包含 composition、structure、ml，且必须出现 metrics/table Artifact。
- 修正 Phase 1 上传格式验收范围，补齐 POSCAR/CONTCAR、ZIP 容器、JSON limited 与 XYZ/EXTXYZ 基础解析边界。
- 将 Phase 6 / Phase 9 Artifact 元数据从重复 Schema 定义改为引用 `docs/13_SHARED_SCHEMA_SPEC.md` 的正式 `Artifact` / `ArtifactMetadata`。
- 复核 Phase 6 缓存策略，确认 `用户要求 refresh 的工具` 条目无重复。
- 补充 pymatviz capability inventory，明确 Level 0-5 能力分层、9 类能力分类、原始 pymatviz 函数/类到平台 Tool ID 的映射表，以及 `composition.ptable_heatmap`、`structure.structure_3d`、`structure.viewer_3d` 的完整 capability 示例。
- 补充 manifest-based Tool Registry 基线，将首批工具来源拆分为 pymatviz、MatterViz/widget、platform_builtin 和 plotly_custom。
- 新增 Adapter implementation plan，明确 BaseToolAdapter 接口、Adapter 执行流程、MVP Adapter 实现顺序和测试要求。
- 更新 Phase 6 Tool Registry 文档，声明初始工具来源于 `tool_registry/*.yaml`，并要求每个工具可追溯 source package / source function / implementationSource。
- 更新 Phase 11 Roadmap，加入 Milestone 0：pymatviz Capability Inventory & Adapter Baseline，并调整代码实现顺序为 manifest loader -> BaseToolAdapter -> MVP 前 3 个 Adapter -> Data Pipeline。
- 清理 `tool_registry/1project.lnk` 本地快捷方式，并在 `.gitignore` 增加 `*.lnk`、`desktop.ini`、`Thumbs.db`。
- 修正 `structure.chem_env_sunburst` 阶段标记：manifest 与 capability inventory 统一为 `v2`，late V1 仅作为 exploratory 备注。
- 更新 ADR-046，使 MVP 实现顺序与 `docs/12_MVP_ROADMAP.md` 的 Milestone 0 和新版实现路线一致。

### Decisions

- 配置优先级为 system defaults < user_config < project_config < recipe/job params。
- MVP 使用 Docker/容器化 Worker 沙箱。
- MVP BYOK 只支持用户级，组织级共享 Key 推迟到 V1。
- 插件默认最小权限，并通过 Tool Registry 和沙箱执行。
- 明确 MVP / V1 / V2 范围、开发里程碑、优先级、风险和验收标准。
- 明确领域扩展阶段：V1 支持 phonon band/DOS 与 trajectory viewer，V2 支持 VASP/LAMMPS、电子结构、生成材料评估和外部生态插件。
- 明确 pymatviz 是 primary visualization kernel，MatterViz 是 3D/widget 展示内核，Tool Registry + Adapter 是 LLM-friendly 能力抽象层。

## 2026-06-23

### Added

- 创建 `docs/00_PROJECT_GOAL.md`。
- 创建 `docs/01_PRODUCT_REQUIREMENTS.md`。
- 创建 `docs/02_SYSTEM_ARCHITECTURE.md`。
- 创建 `docs/03_FRONTEND_WORKSPACE_DESIGN.md`。
- 创建 `docs/04_BACKEND_SERVICE_DESIGN.md`。
- 创建 `docs/05_AGENT_ORCHESTRATION_DESIGN.md`。
- 创建 `docs/06_TOOL_REGISTRY_AND_ADAPTER.md`。
- 创建 `docs/07_DATA_PIPELINE_DESIGN.md`。
- 创建 `docs/08_JOB_QUEUE_AND_CONCURRENCY.md`。
- 创建 `docs/09_ARTIFACT_AND_RECIPE_SYSTEM.md`。
- 创建 `persistent/PROJECT_BRIEF.md`。
- 创建 `persistent/DESIGN_PROGRESS.md`。
- 创建 `persistent/TASK_BOARD.md`。
- 创建 `persistent/ARCHITECTURE_DECISIONS.md`。
- 创建 `persistent/TOOL_REGISTRY_NOTES.md`。
- 创建 `persistent/OPEN_QUESTIONS.md`。
- 创建 `persistent/CHANGELOG.md`。
- 补充独立系统定位：自然语言输入 + 材料数据文件 -> 交互式图表、3D 结构模型、过程展示和 Artifact。
- 补充 pymatviz / MatterViz / Plotly / pymatgen / ASE / phonopy 的平台内角色。
- 补充数据类型到可视化工具的映射表。
- 补充 MVP Tool Set 和 V1/V2 扩展工具边界。
- 补充 3D 渲染路线：Plotly `structure_3d` 与 MatterViz `StructureWidget` / `TrajectoryWidget`。
- 新增 ADR-003、ADR-004、ADR-005。
- 新增 ADR-006：MVP 默认 Auto 模式，Guided / Expert 推迟到 V1。
- 新增 ADR-007：MVP 只支持登录用户，公开分享推迟到 V1。
- 新增 ADR-008：前端产品形态是材料工作台，不是普通聊天页。
- 新增 ADR-009：MVP API 采用 FastAPI，保留 NestJS / LabPilot BFF 集成边界。
- 新增 ADR-010：MVP 采用模块化单体 + 独立 Celery Worker。
- 新增 ADR-011：MVP 异步任务采用 Celery + Redis，复杂编排后续升级 Temporal。
- 新增 ADR-012：PostgreSQL / S3-MinIO / Redis 三层存储职责。
- 新增 ADR-013：MatterViz 和重型 Plotly HTML 通过 sandboxed artifact iframe 展示。
- 新增 ADR-014：MVP Dashboard 使用固定响应式布局，拖拽布局推迟到 V1。
- 新增 ADR-015：Agent Plan 默认摘要展示，完整 JSON 可展开。
- 新增 ADR-016：Code 面板展示脱敏复现代码和 Recipe。
- 新增 ADR-017：MVP 上传采用对象存储预签名直传，分片/断点续传推迟到 V1。
- 新增 ADR-018：Artifact 和 Recipe 使用不可变记录 + version 字段。
- 新增 ADR-019：权限模型采用组织 + 项目 RBAC。
- 新增 ADR-020：API 错误采用统一 Problem Details 风格。
- 新增 ADR-021：Agent 只能输出 JSON Analysis Plan，不能执行代码。
- 新增 ADR-022：MVP 使用单模型配置，不做自动多模型路由。
- 新增 ADR-023：MVP 不做完整工具文档 RAG，使用版本化 Tool Registry 摘要。
- 新增 ADR-024：Prompt injection 进入 Timeline warning，并阻止高风险计划。
- 新增 ADR-025：MVP 工具参数 Schema 手写维护，V1 再评估半自动生成。
- 新增 ADR-026：Plotly 工具必须输出 `figure.json`。
- 新增 ADR-027：MatterViz 工具输出 `viewer.html` + `metadata.json`，snapshot 可选。
- 新增 ADR-028：Phonon / trajectory 高级工具推迟到 V1。
- 新增 ADR-029：Data Profile 必须由确定性解析管线生成，Agent 不直接猜文件内容。
- 新增 ADR-030：MVP 不执行 phonon 分析，保留识别和 Schema 扩展点。
- 新增 ADR-031：VASP 输出和 LAMMPS dump 推迟到 V2。
- 新增 ADR-032：代表性 3D 结构 MVP 使用规则采样，聚类代表点推迟到 V1。
- 新增 ADR-033：MVP 使用 SSE 推送 JobEvent，WebSocket 推迟到 V1。
- 新增 ADR-034：Worker 按任务类型拆分队列。
- 新增 ADR-035：PostgreSQL 是任务状态事实源，Redis 只做 broker/cache/短期状态。
- 新增 ADR-036：大数据图表和 3D 模型默认启用降采样与 LOD。
- 新增 ADR-037：Artifact、Recipe、Report 默认不可变，重跑生成新版本。
- 新增 ADR-038：Report Markdown 是 canonical，HTML 是派生产物，PDF 推迟到 V1。
- 新增 ADR-039：MVP 不支持公开分享，只支持项目成员访问和授权导出。
- 新增 ADR-040：Job export package 异步生成，且必须脱敏。

### Changed

- 将设计进度推进到 Phase 1：产品需求与用户流程。
- 将 Phase 0 标记为完成。
- 明确不 fork 大改 pymatviz，采用 Adapter + Visualization Service 隔离上游变化。
- 明确前端展示 Agent Timeline，不展示原始隐藏思维链。
- 将设计进度推进到 Phase 2：总体系统架构。
- 将 Phase 1 标记为完成。
- 将 Phase 2 移入任务看板 In Progress。
- 将设计进度推进到 Phase 3：前端工作台设计。
- 将 Phase 2 标记为完成。
- 将 Phase 3 移入任务看板 In Progress。
- 将设计进度推进到 Phase 4：后端服务与数据库设计。
- 将 Phase 3 标记为完成。
- 将 Phase 4 移入任务看板 In Progress。
- 将设计进度推进到 Phase 5：Agent 编排设计。
- 将 Phase 4 标记为完成。
- 将 Phase 5 移入任务看板 In Progress。
- 将设计进度推进到 Phase 6：工具注册表与 Adapter。
- 将 Phase 5 标记为完成。
- 将 Phase 6 移入任务看板 In Progress。
- 将设计进度推进到 Phase 7：数据解析与 Data Profile。
- 将 Phase 6 标记为完成。
- 将 Phase 7 移入任务看板 In Progress。
- 将设计进度推进到 Phase 8：高并发任务系统。
- 将 Phase 7 标记为完成。
- 将 Phase 8 移入任务看板 In Progress。
- 将设计进度推进到 Phase 9：Artifact / Recipe / Report。
- 将 Phase 8 标记为完成。
- 将 Phase 9 移入任务看板 In Progress。
- 将设计进度推进到 Phase 10：用户配置、安全与扩展。
- 将 Phase 9 标记为完成。
- 将 Phase 10 移入任务看板 In Progress。

### Fixed

- 无。

### Decisions

- 系统定位为材料数据智能分析与可视化平台，而不是 pymatviz 套壳。
- LLM 不直接执行任意代码；采用 JSON Plan + Tool Registry + Schema 校验的受控执行模式。
- MVP 优先覆盖文件上传、格式识别、Data Profile、Agent JSON Plan、白名单工具调用、Plotly/MatterViz Artifact、Recipe/Report 基础链路。
- 项目按独立系统设计，同时保留后续作为 LabPilot / ResearchOps 子系统集成的能力。
- MVP 默认 Auto 模式；用户可审查计划摘要，但不直接编辑 JSON Plan。
- MVP 仅支持登录用户和项目成员访问；公开分享推迟到 V1。
- MVP 报告导出支持 Markdown / HTML；PDF 推迟到 V1。
- MVP 架构采用 Next.js 前端 + FastAPI 模块化应用 + Celery/Redis Worker + PostgreSQL + S3/MinIO。
- 所有耗时任务必须异步执行，通过 JobEvent 推送进度。
- Redis 不作为唯一持久化状态源，Job/ToolCall/Artifact 状态必须落 PostgreSQL。
- 前端采用三栏式工作台 + 底部面板。
- MVP 使用固定响应式 Dashboard，不做拖拽自定义布局。
- Code 面板只展示脱敏复现代码和 Recipe，不展示 Worker 内部脚本。
- MVP 上传采用对象存储预签名直传，不做分片/断点续传。
- Artifact、Recipe、Report 采用不可变记录和 version 字段。
- 后端权限以 organization + project RBAC 为基础。
- Agent 只负责计划、解释和报告；执行必须经过 Execution Controller。
- MVP 使用项目默认模型，不做自动多模型路由。
- MVP 不做完整工具文档 RAG，先使用版本化 Tool Registry 摘要。
- Tool Registry 是 Agent 可执行能力的唯一白名单。
- MVP Tool Set 固定为 composition / structure / ml 的核心 10 个工具。
- Adapter 负责输入校验、上游调用、Artifact 输出、错误标准化和缓存。
- Agent 规划必须基于 Data Profile，不能直接猜文件内容。
- MVP 数据解析聚焦结构文件、CSV/JSON 和 ZIP；phonon/trajectory 深度支持后移。
- 代表性 3D 结构 MVP 使用规则采样。
- MVP 使用 SSE 作为任务进度事件流。
- Worker Pool 按 parse/profile/llm/viz/render/export 分队列。
- 大数据图表和 3D 模型默认启用降采样和 LOD。
- Plotly `figure.json`、MatterViz `viewer.html + metadata.json`、Report Markdown、Recipe JSON 是 canonical 产物。
- MVP 不支持公开分享，导出包异步生成且必须脱敏。
- 共享 Schema 是实现阶段的类型基线，未来 `packages/schemas/` 应从该文件拆分 JSON Schema、TypeScript 类型和 Python Pydantic model。
- `artifactTypes` 是统一产物类型字段名；不再使用 format 语义表达业务产物。
