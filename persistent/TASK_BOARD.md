# TASK_BOARD

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

- 为当前 Python 依赖建立隔离虚拟环境或锁文件，避免依赖全局 Anaconda 状态。
- 为 V1/V2 工具补完整 paramsSchema，或在未启用阶段保持 register-only 并显式标记不可执行。
- 补齐 parser artifact storage、上传服务边界和对象存储 presigned URL 设计/实现。
- 将当前 `InMemoryJobStore` 迁移到 PostgreSQL repository，并实现 ToolCall / Artifact 状态持久化。
- 实现 Celery Queue Router、parse/profile/viz/render/export 队列入口和 Redis broker 配置。
- 实现 SSE `/jobs/{job_id}/events` cursor 查询和前端 Agent Timeline 数据接入。
- 将 FastAPI stub route 接入真实项目/数据集 repository。

## Deferred

无。
