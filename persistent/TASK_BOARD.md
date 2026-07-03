# TASK_BOARD

## 2026-07-03 Phase 8B Persisted Plans + Redis QueueWorkerRuntime Status

### Done This Round

- [x] Added Alembic migration `0002_phase8b_plans` for `analysis_plans` and nullable `jobs.plan_id`.
- [x] Added indexes: `idx_analysis_plans_project_created`, `idx_analysis_plans_job`, `idx_analysis_plans_plan_hash`, and `idx_jobs_plan_id`.
- [x] Added `AnalysisPlanRepository` to in-memory and SQLAlchemy repository bundles.
- [x] Added stable canonical SHA-256 `plan_hash` and AnalysisPlan JSON round-trip tests.
- [x] Upgraded `/planner/jobs`: invalid plans persist nothing; valid plans persist exact validated JSON, create Job with `plan_id`, return `plan_id`/`plan_hash`, and optionally enqueue only `job_id`.
- [x] Upgraded `QueueWorkerRuntime.handle_job(job_id)` to load `job.plan_id` and execute exact persisted `AnalysisPlan.steps`.
- [x] Added plan provenance to worker events/artifact metadata/result (`planId`, `planHash`, `planSource`).
- [x] Proved persisted 1-step plan -> exactly 1 ToolCall with `toolId`/`stepId` from the persisted plan, Artifact generated, and Job completed.
- [x] Preserved explicit fallback only when a job has no persisted plan.
- [x] Updated CI integration job to include Phase 8B service-backed test and enforce zero skips / at least 19 integration passes.

### Verification

- [x] `uv lock --check`
- [x] `python -m pytest tests/test_phase8b_persisted_plan_queue.py -q` -> 8 passed, 1 skipped locally (integration gated)
- [x] `python -m pytest tests/test_phase8a_plan_execution.py -q` -> 11 passed
- [x] `python -m pytest tests/test_phase7_llm_planner.py -q` -> 22 passed
- [x] `python -m pytest -q` -> 109 passed, 20 skipped
- [x] `npm ci`, `npm run typecheck`, `npm run build` in `apps/web`
- [ ] `MDI_RUN_INTEGRATION=1 python -m pytest -q -m integration` on this machine (blocked: Docker CLI unavailable)
- [ ] GitHub Actions current HEAD service-backed integration success (required before Phase 8B freeze)

### Handoff Notes

- Phase 8B is locally complete but not frozen until CI proves PostgreSQL + Redis + MinIO service-backed integration with zero skipped tests.
- Phase 8C frontend Planner UX must not start before the CI-backed Phase 8B freeze.
- Remaining boundaries: true LLM integration, frontend Planner UX, multi-step DAG/data binding, production secret encryption, worker process supervision/dead-letter queue.

## 2026-06-27 Phase 8A LLM Plan Execution Bridge Status

### Done This Round

- [x] `Phase2ProductRuntime.create_job` accepts `analysis_plan` + `execute` params
- [x] `/planner/jobs` executes the EXACT validated LLM plan (not deterministic) when execute=True
- [x] `/planner/jobs` execute=False = planned-only (job + persisted plan, no ToolCalls)
- [x] Response includes plan_source + executed flags
- [x] MockLLMProvider plan references ml_table so it executes end-to-end
- [x] Deterministic build_phase2_plan preserved as fallback (no analysis_plan → deterministic)
- [x] 11 Phase 8A tests; core proves 1-step LLM plan → exactly 1 ToolCall (not 5); freeze added artifact/event/status/execute=False coverage
- [x] backend 101 passed / 19 skipped / 0 failed; Phase 7 22 passed; frontend ✓; CI HEAD success — baseline frozen
- [x] All execution still through Tool Registry + Adapter; invalid/unknown/V1-V2 rejected before job

### Handoff Notes

- **Acceptance: PASS.** Validated LLM plan now executes; deterministic fallback intact.
- Remaining boundary: Redis QueueWorkerRuntime + PostgreSQL plan persistence integration is future work (execution currently in-memory Phase2ProductRuntime).
- No real LLM, no frontend, no Secret encryption, no V1/V2 tools added this round.

## 2026-06-27 Phase 7 LLM JSON Planner + BYOK Secret Management Status

### Done This Round

- [x] LLMPlannerProvider abstraction + MockLLMProvider + OpenAICompatibleProvider + DeterministicPlannerAdapter
- [x] Planner prompt template (JSON-only, tool-aware, no markdown)
- [x] PlanValidator (strict mode, 10 validation rules, no auto-repair)
- [x] Planner API: POST /planner/preview, /planner/validate, /planner/jobs
- [x] SecretStore abstraction + InMemorySecretStore + EncryptedSecretStore placeholder
- [x] Secrets API: POST/GET/DELETE /me/secrets
- [x] Secret redaction helpers (credential key detection, value scrub)
- [x] 19 Phase 7 tests covering all validation rules + safety guards + API behavior
- [x] Existing Phase 1-6 tests all pass (87 passed, 19 skipped)
- [x] Security enforced: no LLM code execution, no Tool Registry bypass, secrets never in plaintext
- [x] Default pytest does NOT require a real LLM key

### Handoff Notes

- Real OpenAI/DeepSeek calls are optional; fake transport + MockLLMProvider cover all tests
- EncryptedSecretStore is a placeholder; production envelope encryption needs KMS/key-management infra
- Planner API currently uses Phase2ProductRuntime (in-memory) for job creation; production should use PostgreSQL repo + Redis queue
- CI workflow unchanged — Phase 6 service-backed integration still runs on push

## 2026-06-27 Phase 6B Live Integration Closeout Update

### Done This Round

- [x] GitHub Actions CI workflow created with 3 jobs: unit, frontend, service-backed integration
- [x] Integration job validated via live Docker-backed services: PostgreSQL, Redis, MinIO
- [x] **18 integration tests passed, 0 skipped, 0 failed** (CI run `28286885004`)
- [x] Alembic upgrade head ran on live PostgreSQL — 9 tables + 6 indexes verified
- [x] MinIO bucket created and live-tested (put/get/exists/signed-url)
- [x] Redis queue enqueue/handle tested against real Redis
- [x] Service-backed product loop ran with real Tool Registry + BasicMetricsAdapter
- [x] CI zero-skip enforcement in place (skipped > 0 → exit 1)
- [x] Added httpx to pyproject.toml (starlette.testclient dependency)
- [x] Fixed P0 bugs: FK violations (unique project IDs), invalid job state transitions, ToolRegistry constructor
- [x] Unit tests: 68 passed, 19 skipped (local); Frontend: typecheck + build passed

### Handoff Notes

- **Acceptance: PASS.** Phase 6 is live-verified through GitHub Actions.
- CI run: https://github.com/foolkking/material-data-intelligence/actions/runs/28286885004
- **Phase 7 may proceed.**
- Every future push to master/main will re-run the full suite, guarding against regression.

## 2026-06-26 Phase 6 Service-backed Runtime Smoke & Integration Hardening Status

### Done This Round

- [x] Re-read required Phase 6 docs, Alembic baseline, persistent files, and docker-compose config.
- [x] Verified Phase 5 baseline: `git status --short`, `uv lock --check`, `python -m pytest -q`, `npm ci`, `npm run typecheck`, and `npm run build` passed.
- [x] Fixed `docker-compose.yml` MinIO healthcheck: `mc ready local` instead of `curl`.
- [x] Added 18 service-backed integration smoke tests in `tests/test_phase6_integration.py`:
  - Docker compose services reachability.
  - Alembic live migration: real `alembic.command.upgrade(alembic_cfg, "head")` with downgrade+reupgrade cycle + index checks.
  - PostgreSQL repository live CRUD for Project, Dataset, Job/ToolCall/Artifact, Recipe/Report.
  - Transaction rollback and status transition rejection.
  - PostgreSQL JobEvent seq live: monotonic, advisory lock, 30-event concurrent correctness.
  - Redis queue live: enqueue/dequeue, QueueWorkerRuntime with live repos.
  - Queue retry idempotency: duplicate job, crash+retry with live repos.
  - MinIO live: put/get/exists/signed-url, signed URL validation.
  - Service-backed product-loop smoke: PG repos + Redis queue + MinIO storage + real Tool Registry + BasicMetricsAdapter.
- [x] Updated `docs/16_RUNTIME_INFRASTRUCTURE_RUNBOOK.md` with integration test guide, category table, MinIO bucket commands, and troubleshooting (sections 11-12).
- [x] Updated `.env.example` with `MDI_RUN_INTEGRATION` and `MDI_TEST_DATABASE_URL`.
- [x] Re-ran verification: `uv lock --check`, `python -m pytest -q`, `python -m pytest -q -m integration`, `npm ci`, `npm run typecheck`, and `npm run build` passed or skipped as expected.

### Handoff Notes

- **Acceptance: CONDITIONAL PASS.** Docker is not available on this machine; all 18 integration tests skip cleanly by design.
- All P0 issues fixed: Alembic test uses real `alembic.command.upgrade()`, service-backed loop uses real Tool Registry + BasicMetricsAdapter, git status is clean at commit `e3c7a73`.
- **Cannot enter Phase 7** until live Docker-backed integration tests are run and passed on a Docker-capable machine.
- Default unit tests remain Docker-free: `python -m pytest -q` passes 68 tests with 19 skipped.
- Integration tests are opt-in with: `MDI_RUN_INTEGRATION=1 DATABASE_URL=... REDIS_URL=... python -m pytest -q -m integration`.
- Queue execution still has no real LLM and no V1/V2 tool expansion.
- To verify live: `docker compose up -d postgres redis minio` then `MDI_RUN_INTEGRATION=1 python -m pytest -q -m integration`.

## 2026-06-26 Phase 5 PostgreSQL Runtime + Queue Worker + MinIO Status

### Done This Round

- [x] Re-read the required Phase 5 docs, Alembic files, and persistent files before implementation.
- [x] Rechecked the Phase 4 baseline: `git status --short`, `uv lock --check`, `python -m pytest -q`, `npm ci`, `npm run typecheck`, and `npm run build` passed before Phase 5 edits.
- [x] Added standard PostgreSQL/Redis/MinIO runtime environment support while keeping existing `MDI_*` aliases.
- [x] Added SQLAlchemy engine and repository-factory helpers for runtime database wiring.
- [x] Updated Alembic env handling so `DATABASE_URL` / configured PostgreSQL env can drive `alembic upgrade head`.
- [x] Added `docs/16_RUNTIME_INFRASTRUCTURE_RUNBOOK.md` and linked it from `docs/index.md`.
- [x] Updated `.env.example` and `docker-compose.yml` for `postgres`, `redis`, and `minio` infrastructure.
- [x] Added live-capable S3/MinIO object storage behavior with optional boto3-compatible client support and real presigned URL generation.
- [x] Added `QueueWorkerRuntime`, `InMemoryQueueBackend`, and `RedisRQQueueBackend`.
- [x] Added queue retry/idempotency coverage for duplicate enqueue, repeated handler invocation, failed worker retry, artifact metadata stability, and one ToolCall per job step.
- [x] Added PostgreSQL JobEvent advisory-lock strategy and tests for strategy exposure plus SQLite `after_seq` regression.
- [x] Added integration marker coverage that skips cleanly when external PostgreSQL/MinIO services are not explicitly enabled.
- [x] Re-ran verification: `uv lock --check`, `python -m pytest -q`, `python -m pytest -q -m integration`, `npm ci`, `npm run typecheck`, and `npm run build` passed or skipped as expected.

### Handoff Notes

- Live PostgreSQL/Redis/MinIO integration tests are opt-in with `MDI_RUN_INTEGRATION=1`; default unit tests remain Docker-free.
- Queue execution still has no real LLM and no V1/V2 tool expansion. The default queue worker execution path calls Tool Registry + Adapter.
- Multi-process PostgreSQL JobEvent seq stress testing, queue dead-letter policy, worker supervision, and bucket lifecycle/access policy remain later production-deployment work.

## 2026-06-26 Phase 4 Production Persistence Hardening Status

### Done This Round

- [x] Re-read the required Phase 4 docs and persistent files before implementation.
- [x] Rechecked the Phase 3 baseline: `git status --short`, `uv lock --check`, `python -m pytest -q`, `npm ci`, `npm run typecheck`, and `npm run build` passed before Phase 4 edits.
- [x] Added Alembic baseline files under `apps/api/alembic` plus a Phase 4 PostgreSQL-oriented baseline SQL string.
- [x] Added `alembic` to Python dependencies and refreshed `uv.lock`.
- [x] Added repository transaction boundaries through `RepositorySession`, `UnitOfWork`, and `RepositoryFactory`.
- [x] Added centralized Job and ToolCall status transition validation.
- [x] Added ToolCall idempotency fields and repository behavior for stable `(job_id, step_id)` retries.
- [x] Added Artifact metadata consistency validation and idempotent `(job_id, storage_key, sha256)` handling.
- [x] Added Phase 4 tests for migration coverage, SQLAlchemy CRUD, rollback, status transitions, idempotent writes, concurrent JobEvent seq allocation, and `after_seq` ordering.
- [x] Re-ran final verification: `uv lock --check`, `python -m pytest -q`, `npm ci`, `npm run typecheck`, `npm run build`, and `git diff --check` passed.

### Handoff Notes

- PostgreSQL runtime connection settings, pool sizing, and multi-process seq allocation are still future deployment work.
- S3/MinIO signed URLs remain placeholder behavior; live object-storage clients and access-control checks are later work.
- No new Tool Registry manifests, adapters, V1/V2 tools, real LLM calls, or frontend features were added.

## 2026-06-26 Phase 3 Acceptance Hardening Status

### Done This Round

- [x] Re-read the required project docs and persistent files before validation.
- [x] Rechecked Git status and baseline commands before hardening.
- [x] Confirmed Phase 2 product loop did not regress.
- [x] Added missing `DataProfileRepository` and `ReportRepository` abstractions and InMemory/SQLAlchemy implementations.
- [x] Added repository aliases required by the handoff checklist: `create`, `get_by_id`, `list_by_project`, `update_status`, and `list_artifacts_by_job` where applicable.
- [x] Hardened `JobEventRepository.append_event` and worker `InMemoryJobStore.append_event` with in-process seq locks.
- [x] Expanded database metadata and migration draft with artifact `storage_provider` and `bucket`, while preserving required Job/Event/ToolCall/Artifact indexes.
- [x] Expanded `ArtifactStorage` with `put_text`, `put_json`, `get_text`, `get_json`, `exists`, and explicit signed-url placeholder behavior.
- [x] Added storage mapping fields to shared Artifact schemas and Phase 2 artifact API summaries.
- [x] Fixed frontend typecheck reproducibility by moving source-only checking to `tsconfig.typecheck.json`.
- [x] Added Phase 3 tests for DataProfile/Report repositories, concurrent JobEvent seq cursor, storage local/json helpers, S3/MinIO mapping metadata, SSE payload shape, and API/artifact regression.
- [x] Ran final verification: `npm ci`, `uv lock --check`, `python -m pytest -q`, `npm run typecheck`, and `npm run build` passed.

### Handoff Notes

- The S3/MinIO class remains a mapping interface; live client writes, reads, and presigned URLs are later work.
- SQLAlchemy repositories are SQLite-tested and PostgreSQL-oriented; production transaction/session lifecycle and Alembic migrations remain later work.
- Phase 3 is ready for Git baseline after final generated-output cleanup.

## 2026-06-26 Phase 3 Persistence Foundation Status

### Done This Round

- [x] Re-read the Phase 3 entry docs and persistent project state before implementation.
- [x] Rechecked the Phase 2 baseline: clean Git status, `uv lock --check`, `python -m pytest -q`, `npm run typecheck`, and `npm run build` all passed before Phase 3 edits.
- [x] Added repository interfaces for Project, Dataset, Job, JobEvent, ToolCall, Artifact, and Recipe records.
- [x] Added InMemory repository implementations and SQLAlchemy Core implementations for the Phase 3 persistence boundary.
- [x] Added a Phase 3 migration draft covering projects, datasets, data_profiles, jobs, job_events, tool_calls, artifacts, visualization_recipes, and reports.
- [x] Added `job_events.progress`, artifact storage mapping fields, and `reports` metadata to SQLAlchemy table metadata.
- [x] Added per-job seq cursor support through `list_events_after_seq(job_id, after_seq)` and `GET /jobs/{job_id}/events?after_seq=N`.
- [x] Added `GET /jobs/{job_id}/stream` SSE smoke endpoint for local-runtime event replay.
- [x] Added `ArtifactStorage`, `LocalFileArtifactStorage`, and S3/MinIO-compatible storage mapping interface.
- [x] Added `GET /artifacts/{artifact_id}/download` signed-url/download placeholder metadata.
- [x] Added tests for repository behavior, seq cursor, SSE stream, artifact storage mapping, and Phase 2 product-loop regression.
- [x] Ran targeted Phase 3 verification: `python -m pytest tests/test_phase3_persistence.py -q` passed.
- [x] Hardened `npm run typecheck` against stale `tsconfig.tsbuildinfo` cache by disabling incremental reuse.
- [x] Ran final verification: `uv lock --check`, `python -m pytest -q`, `npm run typecheck`, and `npm run build` all passed.

### Handoff Notes

- Phase 3 still does not run Celery, PostgreSQL, MinIO, a real LLM provider, or V1/V2 tools.
- The SQLAlchemy repositories are a migration-ready boundary; the Phase 2 runtime remains local/in-memory until a later queue/persistence phase wires production transactions.
- The S3/MinIO implementation is a mapping interface and signed-url placeholder, not a live object-storage client.
- Git baseline commit remains the final step for this round.

## 2026-06-25 Phase 2 Acceptance Hardening Status

### Done This Round

- [x] Re-ran Phase 2 acceptance after the in-memory/local-file product loop implementation.
- [x] Fixed `AnalysisPlan.expectedArtifacts` output shape to match the shared schema.
- [x] Fixed Phase 2 Recipe steps to include `toolVersion` and schema-compatible `inputBindings`.
- [x] Added `ExpectedArtifact` and `VisualizationRecipeStep` to shared Python/TypeScript schemas.
- [x] Parsed local-path uploads from the copied raw artifact-store file instead of the original caller path.
- [x] Added regression assertions for Phase 2 planner and Recipe schema shape.
- [x] Updated stale product/schema documentation in `README.md` and `docs/01_PRODUCT_REQUIREMENTS.md`.
- [x] Ran `python -m pytest -q`: 48 passed.
- [x] Ran `npm ci`, `npm run typecheck`, and `npm run build`: all passed.
- [x] Verified manifest loading: 3 manifests, registry version `0.1.0`, 10 MVP tools.
- [x] Verified Phase 2 product loop: 5 tool calls and 25 artifacts for the mixed CIF/POSCAR/CSV path.

### Handoff Notes

- Ignored cache/build/dependency outputs are regenerated by pytest/npm verification and must remain excluded from Git and archives.
- Phase 2 remains intentionally local/in-memory. Durable PostgreSQL repositories, Celery queues, MinIO/S3 storage, real LLM execution, V1/V2 tools, and frontend expansion remain out of this round.

## 2026-06-25 Phase 2 Local Product Loop Status

### Done This Round

- [x] Added Phase 2 `InMemoryJobStore`-backed product runtime for project -> dataset upload -> parse -> profile -> plan -> job -> tool calls -> artifacts -> report.
- [x] Added `/datasets/upload`, `/datasets/{dataset_id}/profile`, `/jobs`, `/jobs/{job_id}`, `/jobs/{job_id}/tool-calls`, and `/artifacts/{artifact_id}` API boundaries.
- [x] Added local artifact lookup through `LocalFileArtifactStore`, including report/recipe/plan content queries.
- [x] Added deterministic planner coverage for the five-tool MVP mixed-dataset path.
- [x] Added tests for data pipeline, planner, job runtime, artifact store, API routes, and end-to-end product flow.
- [x] Ran `python -m pytest -q`: 48 passed.
- [x] Kept Phase 2 scoped away from real LLM API, full auth, V1/V2 tools, Celery, PostgreSQL, MinIO, and frontend expansion.

### Handoff Notes

- The Phase 2 loop is intentionally in-memory and local-file-backed. It proves API/state semantics before durable repositories and distributed workers are introduced.
- Frontend checks were not rerun this round because no frontend files changed and `apps/web/node_modules` is not present.
- The Phase 1 handoff archive is ignored via `material-data-intelligence-*.zip` and should not be committed.

## 2026-06-25 Phase 1 Engineering Hardening Status

### Done This Round

- [x] Generated `uv.lock` for Python dependency reproducibility.
- [x] Verified `uv lock --check` and `uv sync --extra test --frozen`.
- [x] Ran `python -m pytest -q` from the uv-managed `.venv`: 42 passed.
- [x] Generated `apps/web/package-lock.json` using npm because `pnpm` is unavailable in the current environment.
- [x] Verified frontend dependencies with `npm ci`.
- [x] Re-ran frontend checks: `npm run typecheck` passed and `npm run build` passed.
- [x] Confirmed `.gitignore` covers dependency directories, build outputs, pytest caches, Python bytecode, TypeScript build info, and setuptools egg-info.

### Handoff Notes

- [x] Final cleanup of regenerated `node_modules`, `.next`, `.pytest_cache`, `.pytest_tmp`, `__pycache__`, `*.pyc`, `*.tsbuildinfo`, and `*.egg-info`.
- The Phase 1 baseline should be committed after this documentation update.
- The handoff zip should be created from Git with `git archive --format=zip HEAD -o material-data-intelligence-phase1.zip`.

## 2026-06-25 Phase 1 Acceptance Status

### Done This Round

- [x] Re-accepted Phase 1/MVP against `docs/01_PRODUCT_REQUIREMENTS.md`.
- [x] Added deterministic Phase 1 demo runtime for project -> upload parse -> Data Profile -> AnalysisPlan -> Worker -> Artifact/Recipe/Report -> JobEvents.
- [x] Covered CIF, POSCAR, CSV, ZIP, JSON limited, XYZ, and EXTXYZ in an end-to-end acceptance test.
- [x] Executed all 10 MVP tools through Tool Registry + Adapter in the Phase 1 product-flow test.
- [x] Verified required Phase 1 artifact families: Plotly JSON/HTML, PNG preview, MatterViz HTML, metrics/table JSON, table CSV, recipe JSON, Markdown report, HTML report.
- [x] Added API boundary routes for create project, upload session, analysis request, job events, event stream, and artifact summaries.
- [x] Expanded Phase 1 table metadata for profile/session/job/event/tool/artifact/recipe/config/secret/audit entities.
- [x] Updated frontend workspace shell acceptance markers.
- [x] Ran verification: `python -m pytest -q`, `npm run typecheck`, and `npm run build`.

### Next Implementation Backlog

- Replace Phase 1 demo runtime state with real repositories for projects, datasets, files, jobs, tool calls, artifacts, and reports.
- Implement real upload object-storage boundary instead of fixture/demo file paths.
- Move in-memory Worker semantics to Celery + PostgreSQL-backed status/event writes.
- Implement durable SSE cursor semantics for `/jobs/{job_id}/events`.
- Wire the frontend shell to live API data instead of static acceptance/demo state.

## Backlog

## In Progress

无。

## Review Needed

- 人工确认 `.gitignore` 已允许 `docs/` 和 `persistent/` 进入 Git，并在本轮提交中包含这些核心设计文件。
- 人工确认 `docs/13_SHARED_SCHEMA_SPEC.md` 作为实现阶段类型基线，后续 `packages/schemas/` 从该文件派生。
- 人工确认 MVP / V1 工具范围：MVP 为 10 个核心工具，10 个均需注册、校验并可由 Worker 执行；端到端 Demo 至少覆盖 6 个并包含 composition、structure、ml。
- 人工确认 MatterViz snapshot、SVG/PDF high-resolution export 不作为 MVP 阻塞项。
- 人工确认 BYOK 多人项目规则：用户级 Secret 按 job runner 解析，Recipe 不保存具体 SecretRef。
- 人工确认 MVP Secret API 使用 `/me/secrets`，项目级共享 Secret API 推迟到 V1。
- 人工确认 `tool_registry/*.yaml` 作为首批 Tool Registry manifest 来源，并在代码实现阶段优先实现 manifest loader。

## Done

- Phase 0：项目目标与边界定义
- Phase 0 补充：独立系统定位与 pymatviz / MatterViz 能力基线
- Phase 1：产品需求与用户流程
- Phase 2：总体系统架构
- Phase 3：前端工作台设计
- Phase 4：后端服务与数据库设计
- Phase 5：Agent 编排设计
- Phase 6：工具注册表与 Adapter
- Phase 7：数据解析与 Data Profile
- Phase 8：高并发任务系统
- Phase 9：Artifact / Recipe / Report
- Phase 10：用户配置、安全与扩展
- 补充设计文件：专业材料领域扩展
- 复核修正：phonon / trajectory 工具阶段归属
- 逐文件审核：修正 MVP/V1 工具表述并新增文档索引
- Phase 11：MVP Roadmap
- Design Review Fixes：修正 `.gitignore`、新增入口文件、统一共享 Schema、修正 MVP/V1 范围、补充前端组件/状态规格、更新 ADR。
- Implementation Readiness Fixes 2：补全共享 Schema 缺失类型、统一 `artifactTypes`、修正 10 个 MVP 工具冲突、删除 Phase 0 旧 Schema、补充 `job_events.seq`、修正推荐任务阶段标记和 Redis 事实源表述。
- Implementation Readiness Fixes 3：统一 JobEvent status、移除 retry 专用 JobStatus、修正下载格式命名、更新 RecommendedTask 字段、明确 Plotly MVP 推荐输出，并复核 Tool Registry 执行流/Markdown 代码块。
- Implementation Readiness Fixes 4：拆分 MVP 工具实现标准与演示标准、统一 Plotly 交互展示产物口径、对齐 Phase 2 JobEvent/ArtifactRecord、补齐 Phase 4 时间字段和 BYOK API、修正 AgentTimelineEvent status。
- Implementation Readiness Fixes 5：对齐 Phase 1 与 Phase 12 的 MVP 验收和上传格式范围，移除 Phase 6 / Phase 9 Artifact Schema 重复定义，复核 Phase 6 缓存 refresh 条目无重复。
- [x] 新增 pymatviz capability inventory。
- [x] 新增 pymatviz / matterviz / platform builtin manifest。
- [x] 新增 Adapter implementation plan。
- [x] 更新 MVP roadmap，加入 Milestone 0。
- [x] 清理 `tool_registry/1project.lnk` 并忽略 Windows 快捷方式/系统缩略图文件。
- [x] 将 `structure.chem_env_sunburst` 的 manifest 阶段统一为 `v2`，late V1 仅保留为探索备注。
- [x] 更新 ADR-046，使实现顺序与 Milestone 0 一致。
- [x] 建立 repo scaffold：`apps/web`、`apps/api`、`services/workers`、`packages/*` 和 `tests/fixtures`。
- [x] 从 `docs/13_SHARED_SCHEMA_SPEC.md` 建立 `packages/schemas` 的 Python/Pydantic、JSON Schema 和 TypeScript 类型基线。
- [x] 实现 Tool Registry manifest loader，加载并校验 3 个 manifest。
- [x] 实现 `BaseToolAdapter`、本地 Input Resolver、参数 Secret 拦截、Artifact Exporter 和 Error Normalizer。
- [x] 实现 MVP 前 3 个 Adapter：`composition.ptable_heatmap`、`structure.structure_3d`、`structure.viewer_3d`。
- [x] 建立最小测试：manifest loader、BaseToolAdapter、前三个 Adapter、Artifact metadata/recipe。
- [x] 运行 `python -m pytest`，11 passed。
- [x] 实现 Data Pipeline 最小库层：格式检测、CIF/POSCAR/CSV/JSON limited 解析、normalized object draft、DataProfile builder。
- [x] 补充 Data Pipeline fixtures 和测试：CIF、POSCAR、CSV、JSON limited、plain XYZ detection。
- [x] 运行 `python -m pytest`，17 passed。
- [x] 补齐剩余 7 个 MVP Adapter：`composition.elements_hist`、`composition.chem_sys_treemap`、`structure.coordination_hist`、`ml.density_scatter`、`ml.error_distribution`、`ml.basic_metrics`、`ml.outlier_table`。
- [x] 将 10 个 MVP adapter class 全部注册到 `ADAPTER_CLASSES`，并新增 manifest -> adapter class registry 测试。
- [x] 运行 `python -m pytest`，25 passed。
- [x] 将 pytest 临时目录固定在仓库内 `.pytest_tmp`，适配受限 sandbox。
- [x] 对齐 plain XYZ 语义：解析为非周期 `Atoms`，生成 `NON_PERIODIC_ATOMS` quality warning，不进入周期结构工具。
- [x] 增加 `.extxyz` 检测与周期结构转换测试，确认 ASE->pymatgen 路径可用。
- [x] 增加 ZIP 安全解包回归测试，确认路径穿越 member 被拒绝。
- [x] 增加 normalized object 稳定落盘 helper 测试。
- [x] 再次运行 `python -m pytest`，25 passed。
- [x] 补齐共享 Schema TypeScript 核心类型导出，并新增 Python `JobEvent` 模型。
- [x] 新增共享 Schema 导出覆盖测试。
- [x] 运行 `python -m pytest -q`，30 passed。
- [x] 新增受控 ToolExecutionRequest 执行入口 `execute_tool_request()`，通过 Tool Registry lookup 和 paramsSchema 校验后才实例化 Adapter。
- [x] 新增 Tool Executor 测试，覆盖未注册工具、非法参数和内存 cache hit。
- [x] 运行 `python -m pytest -q`，34 passed。
- [x] 新增最小 Worker runtime：`run_tool_call_job()`、`InMemoryJobStore`、ToolCall 状态和 JobEvent 事件序列。
- [x] 新增 Worker runtime 测试，覆盖 artifact.ready 事件和失败路径 Secret 脱敏。
- [x] 运行 `python -m pytest -q`，36 passed。
- [x] 新会话恢复核验：重读项目入口、核心 docs、manifest 和 persistent 文件，检查 `git status --short` 与仓库文件清单。
- [x] 运行恢复基线测试：`python -m pytest -q`，36 passed。
- [x] 收紧剩余 7 个 MVP 工具的 `paramsSchema`，确保所有 10 个 MVP 工具拒绝未注册参数。
- [x] 新增 manifest loader 测试，校验 MVP 工具 `additionalProperties=false` 且未知参数会被 JSON Schema 拒绝。
- [x] 运行 `python -m pytest -q`，37 passed。
- [x] 完成 Milestone 1 scaffold：`docker-compose.yml` 配置 PostgreSQL / Redis / MinIO，本地 `.env.example` 只保存占位符。
- [x] 建立 FastAPI API 边界：`mdi_api.main:create_app()`、health/auth/project/dataset/tools 路由和 Tool Registry 读取入口。
- [x] 建立基础 Auth / Project / Dataset 表元数据：`users`、`organizations`、`projects`、`project_members`、`datasets`、`files`。
- [x] 建立 Next.js workspace shell：App Router、三栏式材料工作台、Agent Timeline 和底部面板。
- [x] 新增 Phase 1 scaffold 测试：API route、SQLAlchemy metadata、compose 服务、web shell 文件。
- [x] 修正当前环境 FastAPI/Starlette 版本不兼容：`starlette` 固定为 `>=0.40,<0.47`，当前运行版本为 `0.46.2`。
- [x] 运行 `python -m pytest -q`，41 passed。
- [x] 运行 `npm run typecheck`，passed。
- [x] 运行 `npm run build`，passed。

## Next Implementation Backlog

- Phase 6 integration tests need Docker-backed PostgreSQL/Redis/MinIO on the test machine. CI pipeline should include a service-backed job that starts services and runs `MDI_RUN_INTEGRATION=1 python -m pytest -q -m integration`.
- Multi-process PostgreSQL JobEvent seq stress testing, worker process supervision, dead-letter policy, and bucket lifecycle/access policy remain later production-deployment work.
- Live Celery/RQ worker process orchestration and SSE cursor production backpressure remain later work.
- Real LLM JSON Planner, BYOK Secret management API, frontend API integration, and V1/V2 tool implementation remain future phases.

## Deferred

无。
