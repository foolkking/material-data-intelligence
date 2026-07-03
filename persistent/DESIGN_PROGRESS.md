# DESIGN_PROGRESS

## 2026-07-03 Phase 8B Persisted Plans + Queue Worker Update

- Added PostgreSQL-backed `analysis_plans` persistence and `jobs.plan_id` linkage through Alembic revision `0002_phase8b_persisted_analysis_plans`.
- Added `AnalysisPlanRepository` to both in-memory and SQLAlchemy repository bundles, including `save_plan`, `get_plan`, `get_plan_for_job`, `attach_plan_to_job`, AnalysisPlan JSON round-trip, canonical SHA-256 `plan_hash`, and credential-key rejection before persistence.
- Upgraded `POST /planner/jobs` to validate first, persist the exact validated `AnalysisPlan`, create a Job linked by `plan_id`, and optionally enqueue only `job_id`; it no longer synchronously executes in the planner route.
- Upgraded `QueueWorkerRuntime.handle_job(job_id)` so the main path loads `job.plan_id`, reconstructs the persisted `AnalysisPlan`, executes exactly `plan.steps`, and writes ToolCall, JobEvent, Artifact, and completed Job status with `planId`/`planHash` provenance.
- Preserved explicit fallback only for dev/test jobs without a persisted plan. When `plan_id` exists, persisted plan loading wins and `build_phase2_plan` is not used.
- Core local evidence: `tests/test_phase8b_persisted_plan_queue.py` proves persisted 1-step plan -> exactly 1 ToolCall, `toolId=ml.basic_metrics`, `stepId=llm_step_1`, Artifact generated, `plan.loaded` JobEvent includes `planId`/`planHash`, and Job reaches `completed`.
- Verification so far: `uv lock --check` passed; Phase 8B targeted 8 passed / 1 skipped; Phase 8A 11 passed; Phase 7 22 passed; backend full 109 passed / 20 skipped; frontend `npm ci`, `npm run typecheck`, and `npm run build` passed.
- Local machine has no Docker CLI, so service-backed Phase 8B integration could not be run locally. CI is configured to run Phase 6 + Phase 8B integration against PostgreSQL + Redis + MinIO with zero skipped tests and at least 19 passes before Phase 8B can be considered frozen.
- Remaining boundaries after Phase 8B: true LLM integration, frontend Planner UX (Phase 8C), multi-step DAG/data-dependency execution, production secret encryption, worker process supervision/dead-letter policy.

## 2026-06-27 Phase 8A LLM Plan Execution Bridge Update

- Closed the largest Phase 7 boundary: validated LLM AnalysisPlans now actually execute, instead of being discarded in favor of the deterministic plan.
- `Phase2ProductRuntime.create_job` gained two parameters: `analysis_plan` (use this EXACT validated plan instead of `build_phase2_plan`) and `execute` (False = planned-only, no ToolCalls run).
- `POST /planner/jobs` now: generates plan → validates → on success creates a job that executes the EXACT validated LLM plan; added an `execute` flag (default False = planned, True = run). Response includes `plan_source` and `executed`.
- The runtime execution loop was unchanged — it already iterated `plan.steps` through Tool Registry + Adapter (`run_tool_call_job`). Only the plan *source* changed.
- MockLLMProvider's plan now references the conventional `ml_table` normalized object so the validated plan is executable end-to-end (no plan mutation/auto-repair by the bridge).
- Deterministic `build_phase2_plan` preserved as fallback: when no `analysis_plan` is provided, create_job uses it (Phase 2/3 product loop unchanged).
- **Key acceptance evidence**: `test_runtime_executes_exact_provided_plan_one_tool_call` proves a 1-step LLM plan produces EXACTLY 1 ToolCall (`ml.basic_metrics`, stepId `llm_step_1`), NOT the deterministic 5 ToolCalls. `test_runtime_deterministic_fallback_when_no_plan` proves fallback still works.
- Added `tests/test_phase8a_plan_execution.py` (11 tests). All execution still goes through Tool Registry + Adapter; unknown/V1/V2/invalid plans still rejected before job creation (Phase 7 validator unchanged).
- Baseline-freeze hardening added 4 tests covering exact-plan execution side effects: produces a `metrics_json` artifact, emits `tool.started`/`tool.completed`/`artifact.ready`/`plan.generated` events, job status reaches `completed`, and `execute=False` yields zero ToolCalls + no tool artifact + no tool events.
- Verification: backend 101 passed, 19 skipped, 0 failed; Phase 7 targeted 22 passed; frontend typecheck+build passed; uv lock + git diff clean.
- **Remaining boundary**: execution uses the in-memory `Phase2ProductRuntime` (synchronous local loop). Wiring the validated plan into the Redis `QueueWorkerRuntime` + PostgreSQL plan persistence is still future work (recorded in OPEN_QUESTIONS).

## 当前阶段

Phase 8A: LLM Plan Execution Bridge — **通过 (PASS) / baseline frozen**。validated LLM plan 现在真正执行（1-step → 恰好 1 ToolCall，非 deterministic 5），并验证了 Artifact/JobEvent/completed status 副作用 + execute=False 零 ToolCall。deterministic fallback 保留。backend 101 passed / 19 skipped / 0 failed。剩余边界：QueueWorkerRuntime + PostgreSQL plan persistence 待后续。

## 2026-06-27 Phase 7 LLM JSON Planner + BYOK Secret Management Update

- Implemented LLMPlannerProvider abstraction with 3 implementations:
  - MockLLMProvider: deterministic, no API key, returns valid AnalysisPlan for testing
  - OpenAICompatibleProvider: OpenAI/DeepSeek compatible with fake-transport support for testing
  - DeterministicPlannerAdapter: wraps existing build_phase2_plan() as fallback
- Added PlanValidator (strict mode, no auto-repair) in `packages/tool-registry/mdi_tool_registry/plan_validator.py`
  - Validates: JSON schema, step_id uniqueness, tool_id in ToolRegistry, MVP-only stage, no credentials in params, known artifact types, empty steps rejection, V1/V2 tool rejection
- Added planner prompt template in `services/llm/mdi_llm/planner_prompt.py` (JSON-only output, tool-aware system prompt)
- Added Planner API routes: POST /planner/preview, /planner/validate, /planner/jobs
  - /planner/preview: generates plan without creating job
  - /planner/validate: validates existing plan without creating job
  - /planner/jobs: plan → validate → create job (rejects invalid plans before job creation)
- Added SecretStore abstraction + InMemorySecretStore + EncryptedSecretStore placeholder
  - Secret list API never returns plaintext values
  - SecretStore creates/gets/deletes secrets internally
- Added secrets API routes: POST/GET/DELETE /me/secrets
- Added redaction helpers: credential key detection, secret value replacement in logs/params
- Added 19 Phase 7 tests: mock provider, schema validation, unknown tool rejection, V1/V2 rejection, duplicate step_id, empty steps, credential param rejection, preview no job, validate no job, plan→job flow, secret list no plaintext, secret CRUD, redaction, deterministic planner regression, OpenAI fake transport
- Security boundaries enforced:
  - LLM cannot execute Python/Shell, cannot bypass Tool Registry, cannot access secrets
  - Secret values never enter prompts, logs, JobEvents, Artifacts, Recipe, or Reports
  - params containing api_key/token/password are rejected at PlanValidator level
  - Preview and validate endpoints do not create jobs or enqueue work
- Verification: 87 passed, 19 skipped; frontend typecheck+build passed; git clean pending commit
- No real LLM key required for default pytest; MockLLMProvider + fake transport cover all test paths

## 2026-06-27 Phase 6B Live Integration Closeout Update

- GitHub Actions CI run [#28286885004](https://github.com/foolkking/material-data-intelligence/actions/runs/28286885004) completed with **full success**:
  - Unit Tests (Python 3.11): passed
  - Frontend Typecheck & Build: passed
  - Service-backed Integration (PostgreSQL + Redis + MinIO): **18 passed, 0 skipped, 0 failed**
- Alembic upgrade head ran against live PostgreSQL (CI service container) — 9 tables + 6 indexes verified
- MinIO bucket `mdi-artifacts` created and live-tested with put/get/exists/signed-url
- Redis queue live enqueue/handle tested against real Redis service container
- PostgreSQL repository live CRUD tested for all 9 entity types
- JobEvent seq monotonic/concurrent correctness verified on PostgreSQL with advisory lock strategy
- Service-backed product loop tested with real Tool Registry + BasicMetricsAdapter through execute_tool_request()
- CI workflow includes zero-skip enforcement: if any integration test skips, the job fails
- Added `httpx` to pyproject.toml dependencies (required by starlette.testclient)
- Fixed multiple P0 integration bugs: FK violations from shared project IDs, invalid job state transitions, ToolRegistry constructor mismatch
- **Final acceptance: PASS.** All 18 integration tests ran and passed on live Docker-backed PostgreSQL/Redis/MinIO via GitHub Actions. Phase 6 is live-verified.
- **Phase 6B closeout complete. Phase 7 may proceed.**

## 2026-06-26 Phase 6 Service-backed Runtime Smoke & Integration Hardening Update

- Re-read the required Phase 6 docs, Alembic baseline, persistent state, and docker-compose config before changes.
- Verified the Phase 5 baseline: clean Git status, `uv lock --check`, `python -m pytest -q`, `npm ci`, `npm run typecheck`, and `npm run build` all passed.
- Added 18 service-backed integration smoke tests in `tests/test_phase6_integration.py` covering:
  - Docker compose services reachability (PostgreSQL, Redis, MinIO).
  - Alembic live migration: real `alembic.command.upgrade(alembic_cfg, "head")` against PostgreSQL, plus downgrade+reupgrade cycle and index existence checks.
  - PostgreSQL repository live CRUD: Project, Dataset, Job, ToolCall, Artifact, Recipe, Report.
  - Transaction rollback and status transition rejection at repository boundary.
  - PostgreSQL JobEvent seq live: monotonic seq, advisory lock strategy, 30-event concurrent append correctness.
  - Redis queue live: enqueue/dequeue, QueueWorkerRuntime with PG repos + Redis backend.
  - Queue retry idempotency: duplicate job handle, crash+retry persistence.
  - MinIO live: put/get/exists/signed-url for json/text/bytes, signed URL structure validation.
  - Service-backed product-loop smoke: PG repos + Redis queue + MinIO storage + real Tool Registry + BasicMetricsAdapter (not fake executor).
- All 18 integration tests are gated with `@pytest.mark.integration` and skip cleanly when `MDI_RUN_INTEGRATION != 1` or Docker services are unreachable.
- Fixed `docker-compose.yml` MinIO healthcheck to use `mc ready local` for reliability.
- Updated `docs/16_RUNTIME_INFRASTRUCTURE_RUNBOOK.md` with integration test guide (sections 11-12), environment variables, category table, and troubleshooting for connection refused, migration failed, bucket not found, and signed URL invalid.
- Updated `.env.example` with `MDI_RUN_INTEGRATION` and `MDI_TEST_DATABASE_URL`.
- Verification:
  - `python -m pytest -q`: 68 passed, 19 skipped.
  - `python -m pytest tests/test_phase6_integration.py -q`: 18 skipped (Docker not available on this machine).
  - `python -m pytest -q -m integration`: all skipped (no Docker).
  - `uv lock --check`: passed.
  - `npm ci`: passed.
  - `npm run typecheck`: passed.
  - `npm run build`: passed.
- **Final acceptance**: CONDITIONAL PASS. Docker is not available on this machine; all 18 integration tests skip cleanly. Alembic test calls real `alembic.command.upgrade()`, service-backed loop test uses real Tool Registry + BasicMetricsAdapter, and git is clean at commit `e3c7a73`. Cannot enter Phase 7 until live Docker-backed integration is verified.

## 2026-06-26 Phase 5 PostgreSQL Runtime + Queue Worker + MinIO Integration Update

- Re-read the required Phase 5 project docs, Alembic baseline, and persistent state, then verified the Phase 4 baseline before changes: clean Git status, `uv lock --check`, `python -m pytest -q`, `npm ci`, `npm run typecheck`, and `npm run build` all passed.
- Added Phase 5 runtime configuration support for standard `DATABASE_URL`, `POSTGRES_*`, `REDIS_URL`, and `MINIO_*` variables while keeping existing `MDI_*` aliases.
- Added `mdi_api.database` engine/repository-factory helpers and made Alembic honor configured runtime database URLs while preserving the local SQLite fallback when no runtime DB env is set.
- Added `docs/16_RUNTIME_INFRASTRUCTURE_RUNBOOK.md` with Docker, Alembic, repository smoke, queue, MinIO, and integration-test operating notes.
- Extended `docker-compose.yml` and `.env.example` for one-command local infrastructure: PostgreSQL, Redis, and MinIO.
- Added live-capable `S3CompatibleArtifactStorage` behavior with optional boto3-compatible client support for `put_*`, `get_*`, `exists`, and real presigned URL generation; mapping/placeholder behavior remains unchanged when no client is configured.
- Added `QueueWorkerRuntime`, `InMemoryQueueBackend`, and `RedisRQQueueBackend`. The queue handler receives `job_id`, loads repository state, writes ToolCall status, JobEvents, Artifact metadata, and preserves idempotent retry behavior.
- Hardened SQLAlchemy JobEvent seq allocation for PostgreSQL with a transaction-scoped advisory lock keyed by `job_id`; SQLite/local tests continue to use the existing in-process lock.
- Verification:
  - `python -m pytest tests/test_phase5_runtime_infrastructure.py -q`: 7 passed, 1 skipped.
  - `python -m pytest -q`: 68 passed, 1 skipped, 50 third-party warnings.
  - `python -m pytest -q -m integration`: 1 skipped because external services were not enabled.
  - `uv lock --check`: passed.
  - `npm ci`: passed.
  - `npm run typecheck`: passed.
  - `npm run build`: passed.
  - `git diff --check`: passed with Windows line-ending notices only.

## 2026-06-26 Phase 4 Production Persistence Hardening Update

- Re-read the required project docs and persistent state, then verified the Phase 3 baseline before changes: clean Git status, `uv lock --check`, `python -m pytest -q`, `npm ci`, `npm run typecheck`, and `npm run build` all passed.
- Added an Alembic migration entrypoint and Phase 4 baseline revision for the PostgreSQL-oriented persistence schema while keeping SQLite-compatible SQLAlchemy metadata for tests.
- Hardened SQLAlchemy metadata for `jobs`, `tool_calls`, and `artifacts` with status checks, ToolCall idempotency fields, `(job_id, step_id)` uniqueness, artifact duplicate metadata detection, and storage-provider constraints.
- Added centralized `RepositorySession`, `UnitOfWork`, and `RepositoryFactory` transaction boundaries with rollback coverage.
- Added centralized Job/ToolCall status transition validation. The local synchronous worker keeps `created -> running` compatibility, while queued production flow can use `created -> queued -> running`.
- Added idempotent ToolCall and Artifact repository writes so repeated worker attempts reuse stable records instead of generating uncontrolled duplicates.
- Kept the Phase 2/3 product loop unchanged in scope: no real LLM, no V1/V2 tools, no Celery/Ray/Kubernetes, no production PostgreSQL runtime, no live MinIO/S3 client, and no frontend redesign.
- Verification after fixes:
  - `python -m pytest tests/test_phase4_persistence_hardening.py -q`: 8 passed.
  - `uv lock --check`: passed.
  - `python -m pytest -q`: 61 passed, 50 third-party warnings.
  - `npm ci`: passed.
  - `npm run typecheck`: passed.
  - `npm run build`: passed.
  - `git diff --check`: passed with Windows line-ending notices only.

## 2026-06-26 Phase 3 Acceptance Hardening Update

- Re-ran Phase 3 acceptance against the stricter handoff checklist: Phase 2 regression, repository coverage, database schema/indexes, JobEvent cursor semantics, SSE stream, ArtifactStorage mapping, API event/artifact routes, and reproducible frontend checks.
- Found and fixed P1 repository coverage gaps by adding `DataProfileRepository` and `ReportRepository` to both InMemory and SQLAlchemy repository bundles.
- Found and fixed a JobEvent cursor hardening gap by adding in-process append locks to the repository layer and `InMemoryJobStore`; tests now cover concurrent appends without duplicate seq values.
- Found and fixed P1 storage schema gaps by adding `storage_provider`, `bucket`, `content_type`, `sha256`, `size_bytes`, `preview_key`, and `created_at` metadata coverage across storage mapping, SQL metadata, migration draft, shared schemas, and artifact API summaries.
- Found and fixed a frontend P0 reproducibility issue where `npm run typecheck` depended on existing `.next/types`; added `apps/web/tsconfig.typecheck.json` so typecheck passes from a clean `.next` state.
- Kept scope unchanged: no real LLM, no V1/V2 tools, no Celery/Ray/Kubernetes, no production PostgreSQL/MinIO wiring, and no frontend feature expansion.
- Verification after fixes:
  - `npm ci`: passed.
  - `uv lock --check`: passed.
  - `python -m pytest -q`: 53 passed, 50 third-party deprecation warnings.
  - `npm run typecheck`: passed from a clean `.next` state.
  - `npm run build`: passed.

## 2026-06-26 Phase 3 Persistence Foundation Update

- Added Phase 3 persistence foundation without adding real LLM execution, V1/V2 tools, Celery/Ray/Kubernetes, full auth, or frontend expansion.
- Added repository abstraction for `ProjectRepository`, `DatasetRepository`, `JobRepository`, `JobEventRepository`, `ToolCallRepository`, `ArtifactRepository`, and `RecipeRepository`.
- Kept the Phase 2 local product loop on its InMemory path, while adding SQLAlchemy Core repositories that are SQLite-testable and PostgreSQL-oriented.
- Extended SQLAlchemy metadata and migration draft coverage for `projects`, `datasets`, `data_profiles`, `jobs`, `job_events`, `tool_calls`, `artifacts`, `visualization_recipes`, and `reports`.
- Added durable cursor semantics to job events: seq remains monotonic per job, `list_events_after_seq(job_id, after_seq)` exists, and `GET /jobs/{job_id}/events?after_seq=N` filters by cursor.
- Added `GET /jobs/{job_id}/stream` as an SSE smoke endpoint using the existing local runtime event stream.
- Added `ArtifactStorage` abstraction with local filesystem storage and an S3/MinIO-compatible mapping interface, including `storage_key`, `content_type`, `sha256`, `size_bytes`, and `preview_key` metadata.
- Added `GET /artifacts/{artifact_id}/download` as a local signed-url/download placeholder while preserving `GET /artifacts/{artifact_id}` for artifact detail.
- Added Phase 3 tests for repository interfaces, SQLAlchemy schema/cursor behavior, SSE smoke streaming, artifact storage mapping, and Phase 2 loop regression.
- Hardened frontend typecheck reproducibility by disabling stale incremental `tsconfig.tsbuildinfo` reuse in `npm run typecheck`.
- Verification:
  - `uv lock --check`: passed.
  - `python -m pytest -q`: 52 passed, 50 third-party deprecation warnings.
  - `npm run typecheck`: passed.
  - `npm run build`: passed.

## 2026-06-25 Phase 2 Acceptance Hardening Update

- Re-ran the Phase 2 acceptance audit against the current worktree after the local product loop implementation.
- Fixed a shared-schema alignment issue in generated `AnalysisPlan.expectedArtifacts`: Phase 1 and Phase 2 planners now emit `{name, type, fromStepId}` entries instead of step-level grouped artifact summaries.
- Fixed Phase 2 job-level Recipe generation to include per-step `toolVersion` and `inputBindings` as `Record<string, string>`, matching `docs/13_SHARED_SCHEMA_SPEC.md` and `packages/schemas/src/index.ts`.
- Added shared Python/TypeScript schema types for `ExpectedArtifact` and `VisualizationRecipeStep`, and validated Phase 2 Recipe JSON with the Pydantic `VisualizationRecipe` model before export.
- Changed Phase 2 local-path uploads to parse the copied raw file under the runtime artifact root, keeping the accepted dataset path independent from the caller's original local path.
- Updated `docs/01_PRODUCT_REQUIREMENTS.md` and `README.md` to remove stale schema/status wording.
- Verification:
  - `python -m pytest -q`: 48 passed, 45 third-party deprecation warnings.
  - `npm ci`: passed from `apps/web/package-lock.json`.
  - `npm run typecheck`: passed.
  - `npm run build`: passed.
  - Manifest audit: 3 manifests load, registry version `0.1.0`, 10 MVP tools.
  - Phase 2 loop audit: project -> dataset upload -> profile -> plan -> job -> 5 tool calls -> 25 artifacts completed.
- Scope guard remains unchanged: no real LLM execution, no V1/V2 tool execution, no Celery/PostgreSQL/MinIO runtime persistence, and no frontend expansion this round.

## 2026-06-25 Phase 2 Local Product Loop Update

- Added `apps/api/mdi_api/phase2_runtime.py` as the Phase 2 in-memory product loop.
- The runtime now covers project creation, dataset upload from local paths or inline small files, deterministic parsing, `DataProfile` generation, deterministic `AnalysisPlan` generation, local Worker execution, Adapter invocation, Artifact export, JobEvent recording, job-level Recipe generation, Markdown/HTML report generation, and API result queries.
- Added Phase 2 API routes:
  - `POST /projects`
  - `POST /datasets/upload`
  - `GET /datasets/{dataset_id}/profile`
  - `POST /jobs`
  - `GET /jobs/{job_id}`
  - `GET /jobs/{job_id}/events`
  - `GET /jobs/{job_id}/tool-calls`
  - `GET /jobs/{job_id}/artifacts`
  - `GET /artifacts/{artifact_id}`
- The deterministic Phase 2 planner selects 3-5 MVP tools and currently chooses this five-tool mixed-dataset path when structures and an ML table are present:
  `composition.ptable_heatmap`, `composition.chem_sys_treemap`, `structure.viewer_3d`, `ml.basic_metrics`, and `ml.outlier_table`.
- Added `LocalFileArtifactStore` over `LocalArtifactExporter` output so API routes can return artifact metadata and text/JSON content without introducing MinIO.
- Kept execution inside the existing validated boundary:
  `AnalysisPlan` -> `ToolExecutionRequest` -> Tool Registry lookup -> paramsSchema validation -> Adapter -> Artifact.
- Explicitly did not add real LLM API calls, full auth, V1/V2 tools, Celery, PostgreSQL, MinIO, or frontend feature expansion.
- Added `tests/test_phase2_product_loop.py` with coverage for data pipeline upload/profile, deterministic planner, local worker runtime, artifact store, API routes, and end-to-end product flow.
- Verification:
  - `python -m pytest -q`: 48 passed, 45 third-party deprecation warnings.
  - Frontend typecheck/build were not rerun because no frontend files changed in this Phase 2 implementation.
- `.gitignore` now ignores `material-data-intelligence-*.zip`, so the Phase 1 handoff archive can stay in the workspace without entering commits.

## 2026-06-25 Phase 1 Engineering Hardening Update

- Froze Python dependencies with `uv.lock`.
- Verified the Python test suite from an isolated uv-managed `.venv` using:
  `python -m pytest -q` -> 42 passed.
- Froze frontend dependencies with `apps/web/package-lock.json` because `pnpm` is not installed in the current environment.
- Verified frontend reproducibility from the lockfile with:
  - `npm ci`
  - `npm run typecheck`: passed
  - `npm run build`: passed
- Confirmed `.gitignore` covers generated dependency/build/cache outputs:
  `.venv/`, `*.egg-info/`, `node_modules/`, `.next/`, `.pytest_cache/`, `.pytest_tmp/`,
  `__pycache__/`, `*.pyc`, and `*.tsbuildinfo`.
- Phase 1 is now ready for a Git baseline commit and `git archive` handoff package after final cleanup.

## 2026-06-25 Phase 1 Product Acceptance Update

- Completed a docs/01 Phase 1 MVP acceptance pass against the current implementation.
- Added a deterministic Phase 1 product-flow runtime in `apps/api/mdi_api/phase1_demo.py`.
- The runtime covers: create project, parse upload set, Data Profile, natural-language request boundary, structured `AnalysisPlan`, registry-approved Worker execution, Artifact/Recipe generation, Markdown/HTML report, and JobEvent timeline.
- The demo flow validates all 10 MVP tools through Tool Registry + Adapter:
  `composition.ptable_heatmap`, `composition.elements_hist`, `composition.chem_sys_treemap`,
  `structure.structure_3d`, `structure.viewer_3d`, `structure.coordination_hist`,
  `ml.density_scatter`, `ml.error_distribution`, `ml.basic_metrics`, `ml.outlier_table`.
- Added API boundary routes for project creation, upload sessions, analysis requests, job events, event streaming, and artifact summaries.
- Expanded Phase 1 SQLAlchemy metadata to include the product-flow entities listed in docs/01: data profiles, field mappings, sessions/messages, jobs/events/tool calls/artifacts, recipes, configs, secrets, and audit logs.
- Updated the frontend shell so Agent Timeline, chart cards, 3D Viewer, Logs, Artifacts, Recipe, and Report surfaces are visible in the Phase 1 workspace.
- Verification passed:
  - `python -m pytest -q`: 42 passed, 25 third-party deprecation warnings.
  - `npm run typecheck`: passed.
  - `npm run build`: passed.
- Current Phase 1 caveats:
  - The product-flow runtime is deterministic/in-memory and intended for acceptance/demo, not a production repository or Celery deployment.
  - `preview_png` now has a minimal PNG fallback when Kaleido/Chromium is unavailable.
  - `structure.viewer_3d` may still emit a MatterViz-safe fallback HTML if widget rendering is unavailable.
  - Real object storage upload sessions, PostgreSQL repositories, Celery workers, and durable SSE cursors remain next-phase implementation work.

## 当前阶段

Phase 7: LLM JSON Planner + BYOK Secret Management — **通过 (PASS)**。90 passed, 19 skipped, 0 failed（22 个 Phase 7 tests + 68 个现有 tests）。MockLLMProvider + PlanValidator（严格，10 规则）+ SecretStore + Planner API 全部可测。**边界说明**：`/planner/jobs` 在 validate 成功后创建 job，但当前 job 实际运行的是 deterministic plan（`build_phase2_plan`），验证过的 LLM plan 尚未接入真实执行——「LLM→执行」闭环未打通，属已记录的后续工作（见 OPEN_QUESTIONS / ADR-075）。Secret 仅 InMemoryStore，生产 envelope encryption 未实现。

## 已完成阶段

- [x] Phase 0：项目目标与边界定义
- [x] Phase 1：产品需求与用户流程
- [x] Phase 2：总体系统架构
- [x] Phase 3：前端工作台设计
- [x] Phase 4：后端服务与数据库设计
- [x] Phase 5：Agent 编排设计
- [x] Phase 6：工具注册表与 Adapter
- [x] Phase 7：数据解析与 Data Profile
- [x] Phase 8：高并发任务系统
- [x] Phase 9：Artifact / Recipe / Report
- [x] Phase 10：用户配置、安全与扩展
- [x] Phase 11：MVP Roadmap

补充文件：

- [x] `docs/11_MATERIAL_DOMAIN_EXTENSIONS.md`：专业材料领域扩展设计
- [x] `docs/index.md`：文档索引
- [x] `docs/03A_FRONTEND_COMPONENT_SPEC.md`：前端组件规格
- [x] `docs/03B_FRONTEND_STATE_AND_INTERACTION.md`：前端状态与交互规格
- [x] `docs/13_SHARED_SCHEMA_SPEC.md`：共享 Schema 基线
- [x] `docs/14_PYMATVIZ_CAPABILITY_INVENTORY.md`：pymatviz 能力清单与平台 Tool ID 映射
- [x] `docs/15_ADAPTER_IMPLEMENTATION_PLAN.md`：Adapter 实现计划
- [x] `tool_registry/pymatviz_manifest.yaml`：pymatviz 原生能力 manifest
- [x] `tool_registry/matterviz_manifest.yaml`：MatterViz / widget 能力 manifest
- [x] `tool_registry/platform_builtin_manifest.yaml`：平台内置与自定义 Plotly 能力 manifest

当前新增设计重点：

本项目进一步明确为“以 pymatviz 为 primary visualization kernel 的材料数据智能分析与可视化平台”。当前补充了 pymatviz capability inventory、manifest-based tool registry 和 adapter implementation plan。

## 本轮完成

- 建立代码工程骨架：`apps/web`、`apps/api`、`services/workers`、`packages/schemas`、`packages/tool-registry`、`packages/adapters`、`packages/material-parsers`、`packages/artifact-core`、`tests/fixtures`。
- 新增根级 `pyproject.toml`，配置 Python 包发现、pytest 路径和核心材料依赖声明。
- 在 `packages/schemas` 中实现共享类型基线：
  - Python/Pydantic：`mdi_schemas.models`
  - JSON Schema：`packages/schemas/json/registered-tool.schema.json`
  - TypeScript 类型：`packages/schemas/src/index.ts`
- 在 `packages/tool-registry` 中实现 manifest loader：
  - `loadManifests()` / `load_manifests()`
  - `validateManifest()` / `validate_manifest()`
  - `getToolById()`、`listTools()`、`listToolsByStage()`、`listToolsByDomain()`、`listMvpTools()`
  - 校验 `tool_id` 唯一、`stage`、`implementation_source`、`display_target`、`artifact_types` 和 adapter class name。
- 在 `packages/artifact-core` 中实现本地文件系统 `LocalArtifactExporter`，输出稳定 storage key、content hash、Artifact metadata 和 provenance。
- 在 `packages/adapters` 中实现：
  - `BaseToolAdapter`
  - `ToolExecutionContext`
  - `ToolExecutionError` / error normalizer
  - Adapter class registry
  - Plotly export helper
- 实现 MVP 前 3 个 Adapter：
  - `composition.ptable_heatmap` -> `PTableHeatmapAdapter`
  - `structure.structure_3d` -> `Structure3DAdapter`
  - `structure.viewer_3d` -> `StructureViewer3DAdapter`
- 为 fixture 和测试补齐：
  - `tests/fixtures/structures/si.cif`
  - `tests/fixtures/tables/formulas.csv`
  - manifest loader、BaseToolAdapter、三个 Adapter、Artifact metadata/recipe 的最小测试。
- 真实环境核对并安装/升级运行依赖：`pymatviz 0.18.0`、`pymatgen 2026.5.4`、`ase 3.29.0`、`plotly 6.8.0`；为兼容 NumPy 2.x 同步升级 `xarray`、`pyarrow`、`numexpr`、`bottleneck`、`shapely`、`scikit-image`。
- 测试结果：`python -m pytest`，11 passed。
- 继续实现 Data Pipeline 最小库层：
  - 新增 `packages/material-parsers/mdi_material_parsers/detector.py`，支持 CIF、POSCAR/CONTCAR、CSV、JSON limited、ZIP、XYZ/EXTXYZ 的格式识别。
  - 新增 `packages/material-parsers/mdi_material_parsers/parsers.py`，支持 CIF/POSCAR -> `Structure`、CSV -> `DataFrame`、JSON limited -> `Structure` 或 simple table。
  - 新增 `packages/material-parsers/mdi_material_parsers/profile.py`，从 parse results 构建轻量 `DataProfile`、`structureSummary`、`tableSummary`、quality issues 和 recommended tasks。
  - 新增 normalized object draft 数据模型，记录 object id、object type、source file ids、storage key、metadata、hash 和 payload。
  - 补充 `tests/test_data_pipeline.py` 与 fixtures：`POSCAR`、`plain.xyz`、`ml_results.csv`。
  - 更新共享 `DataProfile` Pydantic model，补齐 `structureSummary`、`tableSummary`、`phononSummary`、`trajectorySummary` 可选字段。
  - 更新 `pyproject.toml`，显式加入 `pandas>=2.2`。
- 最新测试结果：`python -m pytest`，17 passed。
- 继续补齐剩余 7 个 MVP Adapter，并将 10 个 MVP 工具全部接入 adapter class registry：
  - `composition.elements_hist` -> `ElementsHistAdapter`
  - `composition.chem_sys_treemap` -> `ChemSysTreemapAdapter`
  - `structure.coordination_hist` -> `CoordinationHistAdapter`
  - `ml.density_scatter` -> `DensityScatterAdapter`
  - `ml.error_distribution` -> `ErrorDistributionAdapter`
  - `ml.basic_metrics` -> `BasicMetricsAdapter`
  - `ml.outlier_table` -> `OutlierTableAdapter`
- 新增 ML adapter 共用校验层，支持 DataFrame / records 输入、target/prediction 字段推断、数值列校验、metrics 和 outlier 计算。
- 新增测试覆盖全部 10 个 MVP Adapter，新增 manifest MVP adapter class registry 校验。
- 最新测试结果：`python -m pytest`，25 passed。
- 继续核验 Milestone 0/1 + 已实现库层闭环：
  - 将 pytest 临时目录固定到仓库内 `.pytest_tmp`，避免受限 sandbox 访问系统临时目录失败。
  - 将 plain XYZ Data Pipeline 语义对齐设计：解析为非周期 `Atoms` normalized object，并在 `DataProfile.qualityIssues` 中记录 `NON_PERIODIC_ATOMS` warning；它仍不会进入 `periodic_required` 的结构工具。
  - 新增 `.extxyz` 检测与 ASE->pymatgen 周期结构转换测试。
  - 新增 ZIP 安全解包回归测试，验证路径穿越 member 会被拒绝，保留 safe member 解析为 partial。
  - 新增 normalized object 稳定落盘 helper 测试，路径固定为 `projects/{project}/datasets/{dataset}/normalized/...`。
  - 最新测试结果：`python -m pytest`，25 passed。
- 继续核验共享 Schema 覆盖面：
  - 补齐 `packages/schemas/src/index.ts` 中的 TypeScript 核心类型导出：`JobStatus`、`JobEventStatus`、`ToolExecutionRequest`、`ToolCall`、`Artifact`、`AnalysisPlan`、`AnalysisStep`、`DataProfile`、`VisualizationRecipe` 等。
  - 在 Python/Pydantic schema 中新增 `JobEvent`，为后续 SSE / Agent Timeline 事件流复用同一共享类型。
  - 新增 `tests/test_shared_schemas.py`，校验 Python 和 TypeScript schema 入口暴露用户要求的核心类型。
  - 最新测试结果：`python -m pytest -q`，30 passed，20 warnings；warnings 来自当前 Anaconda 环境中的 matplotlib/Jupyter/ipywidgets 依赖弃用提示，不影响本阶段功能。
- 继续补齐受控执行库层入口：
  - 新增 `packages/adapters/mdi_adapters/executor.py`，提供 `execute_tool_request()`，执行顺序为 Tool Registry lookup -> input resolution / cache key -> paramsSchema validation -> optional in-memory cache lookup -> adapter instantiation -> adapter execution。
  - 新增 `ToolExecutionResult`，记录 `tool`、`artifacts`、`cache_key`、`cache_hit`，为后续 ToolCall 状态表和 JobEvent 持久化留出结构化结果。
  - 新增 `tests/test_tool_executor.py`，覆盖 registry 路由、非法参数拒绝、未注册 tool 拒绝和 cache hit。
  - 最新测试结果：`python -m pytest -q`，34 passed，20 warnings；warnings 仍为当前 Anaconda 第三方依赖弃用提示。
- 继续补齐 Worker 语义基线：
  - 新增 `services/workers/mdi_workers/runtime.py`，提供 `run_tool_call_job()` 和开发用 `InMemoryJobStore`。
  - `run_tool_call_job()` 会记录 Job status、ToolCall status、`tool.started`、`artifact.ready`、`tool.completed` / `tool.failed` JobEvent，并保留事件 `seq` 单调递增语义。
  - ToolCall 记录会对 secret-like params 做脱敏，失败路径不会保存明文 API key / BYOK。
  - 新增 `tests/test_worker_runtime.py`，覆盖成功事件流和失败脱敏路径。
  - 最新测试结果：`python -m pytest -q`，36 passed，20 warnings；warnings 仍为当前 Anaconda 第三方依赖弃用提示。
- 本轮恢复核验：
  - 已按新会话要求重新读取 `README.md`、`AGENTS.md`、`MASTER_PROMPT.md`、核心 `docs/`、3 个 manifest 和 `persistent/` 状态文件。
  - 已检查 `git status --short`，确认上一轮代码与文档仍处于未提交工作区中；本轮继续在该状态上增量推进，未回退既有变更。
  - 已检查配置，当前仅存在 Python `pyproject.toml` 测试配置，未发现前端 `package.json` / `pnpm-workspace.yaml`。
  - 已运行基线测试：`python -m pytest -q`，36 passed，20 warnings。
- 本轮补强 Tool Registry paramsSchema：
  - 将剩余 MVP 工具的 `paramsSchema` 从宽松 `additionalProperties: true` 收紧为平台批准参数白名单：
    `composition.elements_hist`、`composition.chem_sys_treemap`、`structure.coordination_hist`、`ml.density_scatter`、`ml.error_distribution`、`ml.basic_metrics`、`ml.outlier_table`。
  - 新增 `tests/test_manifest_loader.py::test_mvp_tools_reject_unregistered_params`，确保 10 个 MVP 工具均拒绝未注册参数。
  - 最新测试结果：`python -m pytest -q`，37 passed，20 warnings；warnings 仍为当前 Anaconda 第三方依赖弃用提示。
- 本轮完成 Milestone 1 scaffold：
  - 新增 `docker-compose.yml`，配置本地 PostgreSQL、Redis、MinIO 服务；新增 `.env.example` 并只保留占位符，不写入真实 Secret。
  - 新增 `apps/api/mdi_api` FastAPI app factory、配置加载、模块路由边界和 SQLAlchemy Core metadata。
  - 建立基础 Auth / Project / Dataset 表元数据：`users`、`organizations`、`projects`、`project_members`、`datasets`、`files`。
  - 新增 `/health`、`/auth/me`、`/projects`、`/datasets`、`/tools`、`/tools/mvp` API 边界，其中工具路由读取 Tool Registry。
  - 新增 `apps/web` Next.js App Router shell、三栏式工作台页面、底部面板、`package.json`、`tsconfig.json`、`next.config.mjs` 和 `pnpm-workspace.yaml`。
  - 更新 `pyproject.toml`，纳入 `apps/api` 包发现和 `fastapi`、`sqlalchemy`、`uvicorn`、`starlette>=0.40,<0.47` 依赖边界。
  - 修正当前 Anaconda 环境中 `starlette 1.0.0` 与 `fastapi 0.115.12` 不兼容的问题，将 Starlette 降级到 `0.46.2`。
  - 新增 `tests/test_phase1_scaffold.py`，验证 API route 边界、数据库表元数据、compose 服务和前端 shell 文件。
  - 最新测试结果：`python -m pytest -q`，41 passed，20 warnings；`npm run typecheck` passed；`npm run build` passed。

- 创建 `docs/00_PROJECT_GOAL.md`。
- 创建 `persistent/PROJECT_BRIEF.md`。
- 初始化持久化跟踪文件。
- 明确系统是材料数据智能分析与可视化平台，而不是 pymatviz 套壳。
- 明确 LLM 采用 JSON Plan + Tool Registry 的受控执行模式。
- 明确 MVP 优先覆盖文件上传、格式识别、Data Profile、Agent Plan、白名单工具调用、Artifact、Recipe 和报告基础链路。
- 补充独立系统定位：自然语言 + 材料数据文件 -> Plotly / MatterViz 图表、3D 模型、过程展示和可复现 Artifact。
- 补充 pymatviz / MatterViz 数据输入、可视化能力、3D 渲染路线和 MVP 工具集。
- 补充 Adapter 层决策：不 fork 大改 pymatviz，通过 Tool Registry 和 Visualization Service 隔离上游变化。
- 创建 `docs/01_PRODUCT_REQUIREMENTS.md`。
- 完成用户角色、用户故事、上传流程、Data Profile 流程、自然语言分析流程、图表生成流程、3D 模型查看流程、Agent Timeline、Artifact / Recipe / Report 流程定义。
- 明确 Phase 1 产品决策：MVP 仅登录用户、默认 Auto 模式、用户审查计划摘要但不编辑 JSON Plan、报告导出支持 Markdown/HTML。
- 创建 `docs/02_SYSTEM_ARCHITECTURE.md`。
- 明确 MVP 架构：Next.js 前端 + FastAPI 模块化应用 + Celery/Redis Worker + PostgreSQL + S3/MinIO。
- 明确逻辑服务边界：API Gateway、Data Service、Agent Service、Visualization Service、Worker Service、Artifact Service、Storage Layer、Queue Layer、Security Layer。
- 明确所有耗时任务必须通过 Job Queue 异步执行，前端通过 SSE/WebSocket 渐进展示 JobEvent。
- 创建 `docs/03_FRONTEND_WORKSPACE_DESIGN.md`。
- 明确前端采用三栏式工作台 + 底部面板：左侧数据资产、中央可视化画布、右侧 Agent 面板、底部 Logs/Code/Artifacts/Recipe/Warnings。
- 明确 MVP 使用固定响应式 Dashboard，MatterViz / heavy Plotly 优先通过 sandboxed artifact iframe 展示。
- 明确 Agent Plan 默认展示摘要，完整 JSON 和 ToolCall 细节可展开。
- 创建 `docs/04_BACKEND_SERVICE_DESIGN.md`。
- 明确后端模块边界：Auth、Project、Dataset、Profile、Jobs、Agent、Tools、Artifacts、Config、Secrets、Audit、Workers。
- 明确 MVP 上传采用对象存储预签名直传，不做分片/断点续传。
- 明确核心数据库实体、项目级 RBAC、数据隔离、统一错误模型和审计日志边界。
- 创建 `docs/05_AGENT_ORCHESTRATION_DESIGN.md`。
- 明确 Agent 职责：Intent Parser、Data-aware Planner、Tool Selector、Parameter Generator、Result Explainer、Report Writer。
- 明确 Agent 只能输出 JSON Analysis Plan，Execution Controller 校验后创建 ToolCall。
- 明确 MVP 不做自动多模型路由和完整工具文档 RAG；使用项目默认模型和静态 Tool Registry 摘要。
- 明确 Prompt injection 进入 Agent Timeline warning，并可阻止高风险计划执行。
- 创建 `docs/06_TOOL_REGISTRY_AND_ADAPTER.md`。
- 明确 Tool Registry 是唯一执行白名单，Adapter 隔离 pymatviz / MatterViz / Plotly 上游变化。
- 明确 MVP Tool Set、Tool Schema、Artifact 标准、ToolError、缓存 key 和插件扩展机制。
- 明确 MVP Phonon 工具推迟到 V1，当前只保留 Schema 和扩展点。
- 创建 `docs/07_DATA_PIPELINE_DESIGN.md`。
- 明确数据管线流程：格式识别、安全解析、标准化对象、Data Profile、质量检查、推荐任务。
- 明确 MVP 支持 CIF、POSCAR/CONTCAR、XYZ/EXTXYZ 基础解析、CSV、JSON、ZIP；phonon/trajectory 深度支持推迟到 V1，VASP/LAMMPS 推迟到 V2。
- 明确代表 3D 结构 MVP 采用规则采样，composition clustering 推迟到 V1。
- 创建 `docs/08_JOB_QUEUE_AND_CONCURRENCY.md`。
- 明确 MVP 使用 SSE 推送 JobEvent，WebSocket 协作能力推迟到 V1。
- 明确 Worker 按 parse/profile/llm/viz/render/export 队列拆分。
- 明确 PostgreSQL 是 Job/ToolCall/Artifact 状态事实源，Redis 只做 broker/cache/短期状态。
- 明确大数据降采样、3D LOD、资源限制、多用户并发和可观测性策略。
- 创建 `docs/09_ARTIFACT_AND_RECIPE_SYSTEM.md`。
- 明确 Plotly `figure.json`、MatterViz `viewer.html + metadata.json`、Report Markdown、Recipe JSON 的 canonical 地位。
- 明确 Artifact / Recipe / Report 默认不可变，重跑或编辑生成新 version。
- 明确 MVP 不支持公开分享，只支持项目成员访问和授权导出包。
- 创建 `docs/10_USER_CONFIG_AND_SECURITY.md`。
- 明确配置优先级：system defaults < user_config < project_config < recipe/job params。
- 明确 MVP 使用 Docker/容器化 Worker 沙箱，用户级 BYOK，组织级共享 Key 推迟到 V1。
- 明确 Secret envelope encryption、文件安全、Prompt injection MVP 防护、审计日志和插件默认最小权限。
- 创建 `docs/12_MVP_ROADMAP.md`。
- 明确 MVP / V1 / V2 范围、技术栈、开发里程碑、优先级、风险清单、验收标准和进入代码实现顺序。
- Phase 0-11 设计文档全部完成。
- 复核用户给定目标文件清单，补充创建 `docs/11_MATERIAL_DOMAIN_EXTENSIONS.md`。
- 修正 `docs/06_TOOL_REGISTRY_AND_ADAPTER.md` 中 phonon / trajectory 工具阶段归属，使其与 ADR 和 Roadmap 一致：V1 支持 phonon band/DOS 与 trajectory viewer，V2 支持 VASP/LAMMPS、电子结构、生成材料评估和外部生态插件。
- 更新 `docs/12_MVP_ROADMAP.md` 的设计完成标准，纳入 `docs/11_MATERIAL_DOMAIN_EXTENSIONS.md`。
- 完成逐文件审核，创建 `docs/index.md` 作为文档入口。
- 修正 `docs/01_PRODUCT_REQUIREMENTS.md` 中 MVP 示例混入 V1 `structure.spacegroup_bar` 的表述。
- 修正 `docs/03_FRONTEND_WORKSPACE_DESIGN.md` 中 TrajectoryWidget MVP 表述，明确 MVP 仅基于已解析结构集合展示首末帧/抽样帧，不提供完整 trajectory 工具。
- 更新 `persistent/TOOL_REGISTRY_NOTES.md`，补齐 `ml.parity_plot` 的 V1 归属，并区分 V1 phonon/trajectory 与 V2 VASP/LAMMPS。
- 完成 Design Review Fixes：修正 `.gitignore`，确保 `docs/` 和 `persistent/` 进入 Git 版本管理。
- 新增根目录 `README.md`、`AGENTS.md`、`MASTER_PROMPT.md`，作为新会话和 Coding Agent 入口。
- 新增 `docs/13_SHARED_SCHEMA_SPEC.md`，统一 `ArtifactType`、`DisplayTarget`、`ToolCategory`、`ToolDomain`、`ToolInputSchema`、`AnalysisPlan`、`JobEvent`、`Recipe`、`Config` 等跨模块 Schema。
- 新增 `docs/03A_FRONTEND_COMPONENT_SPEC.md` 和 `docs/03B_FRONTEND_STATE_AND_INTERACTION.md`，补齐前端组件树、状态切片、Artifact Loader、全屏/重试/错误态和 SSE 事件投影。
- 统一 MVP/V1 工具范围：MVP 为 composition/structure/ml 的 10 个核心工具；V1 扩展 parity、uncertainty、error-by-domain、phonon、trajectory、RDF/XRD、composition clustering。
- 修正 Tool Registry：`ToolInputSchema` 改为 `inputOptions` 多输入方案，增加 `implementationSource`、`ToolDomain` 和周期性结构约束。
- 增加 `metrics_json`、`table_json`、`table_csv`、`quality_issues_json`，将指标和表格结果作为一等 Artifact。
- 修正 JSON limited、ZIP 容器、plain XYZ / EXTXYZ 与周期结构工具的边界。
- 调整 MatterViz snapshot、SVG/PDF high-resolution export 的阶段归属，MVP 不把这些作为阻塞项。
- 明确 BYOK 多人项目规则：用户级 Secret 按 job runner 解析，Recipe 不保存具体 SecretRef。
- 补充 JobEvent 关键数据库索引和事件/日志保留策略。
- 更新 ADR-027、ADR-042，并新增 ADR-048 至 ADR-057。
- 完成第二轮实现前一致性修正：补全 `docs/13_SHARED_SCHEMA_SPEC.md` 中 `FileProfile`、`ObjectProfile`、`QualityIssue`、`RecommendedTask`、`InputRef`、`ToolExecutionRequest` 和 `Molecule`。
- 统一 `artifactTypes` 命名，移除旧的 format 语义残留。
- 删除 Phase 0 旧 Schema 草案，改为引用 `docs/13_SHARED_SCHEMA_SPEC.md`。
- 修正 Phase 3 `activeTab` 为 `DisplayTarget`，修正 Phase 4 `job_events.seq`，修正 Phase 12 10 个 MVP 工具与 Milestone 3 的冲突。
- 将推荐任务增加 `stage`、`availableNow`、`requiredTools` 和 `reason` 语义，避免 MVP Planner 自动选择 V1 工具。
- 统一 Redis 只作为 broker/cache/transient state 的表述；Celery result backend 若启用也不作为业务事实源。
- 在 `README.md` 增加对外分享压缩包排除 `.git/` 的建议。
- 完成第三轮一致性修正：统一 JobEvent status 为 `info/running/success/warning/error`，移除 retry 专用 JobStatus，修正用户配置导出格式为 download format，确认 Phase 0 只引用共享 Schema，确认 Tool Registry 执行流和 Markdown 代码块无重复/破损。
- 完成第四轮实现前一致性修正：拆分 MVP 10 个工具实现标准与 6 个工具端到端演示标准；统一 Plotly MVP 交互展示产物口径；Phase 2 `JobEvent` 补齐 `seq/progress` 并让 `ArtifactRecord` 引用共享 `Artifact`；Phase 4 表字段补齐索引依赖的时间字段；MVP Secret API 改为用户级 `/me/secrets`，项目级共享 Secret 推迟到 V1；Agent Timeline 状态与共享 `JobEvent.status` 对齐。
- 完成第五轮实现前小修：Phase 1 MVP 验收标准与 Phase 12 完全对齐；Phase 1 上传范围补齐 POSCAR/CONTCAR、JSON limited、XYZ/EXTXYZ 基础解析；Phase 6 / Phase 9 Artifact 元数据改为引用 `docs/13_SHARED_SCHEMA_SPEC.md` 的正式 `Artifact` / `ArtifactMetadata`；复核 Phase 6 缓存策略中 `refresh` 条目无重复。
- 完成 pymatviz 能力抽象基线补充：新增 `docs/14_PYMATVIZ_CAPABILITY_INVENTORY.md`，明确 Level 0-5 能力分层、9 类 pymatviz/MatterViz/Plotly 能力、原始函数到平台 Tool ID 的映射表，以及 3 个 MVP capability 完整示例。
- 新增 `tool_registry/pymatviz_manifest.yaml`、`tool_registry/matterviz_manifest.yaml`、`tool_registry/platform_builtin_manifest.yaml`，将 10 个 MVP 工具来源拆分为 pymatviz、MatterViz、plotly_custom 和 platform_builtin。
- 新增 `docs/15_ADAPTER_IMPLEMENTATION_PLAN.md`，明确 BaseToolAdapter 接口、执行流程、MVP Adapter 实现顺序和测试要求。
- 更新 `docs/06_TOOL_REGISTRY_AND_ADAPTER.md` 与 `docs/12_MVP_ROADMAP.md`，把 manifest-based Tool Registry 和 Milestone 0 纳入正式实现顺序。

## 当前阻塞

无架构方向阻塞。Milestone 1 scaffold 已完成：本地 infra 配置、FastAPI API 边界、基础 Auth/Project/Dataset 表元数据和 Next.js 工作台 shell 均已有测试或构建证据。当前仍有工程化后续项：建议建立隔离虚拟环境/锁文件，避免继续修改全局 Anaconda 环境；`preview_png` 因 Kaleido/Chromium 依赖仍按 MVP optional 处理；ZIP 解包已具备最小安全解析但仍需补更多安全测试；EXTXYZ with lattice 需要继续验证；当前 Worker runtime 仍是内存语义基线，尚未接入 Celery / PostgreSQL / SSE。

## 下一步

下一步按 Roadmap 继续进入 Milestone 2 / Milestone 4 的交界：建立隔离依赖/锁文件，补齐 parser artifact storage、上传/对象存储边界、更多 ZIP / EXTXYZ 回归测试；随后接 Celery Job Queue、PostgreSQL ToolCall/Artifact 状态持久化和 SSE 事件流。
