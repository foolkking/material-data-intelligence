# OPEN_QUESTIONS

## 2026-06-26 Phase 4 Follow-ups

- No P0 blocker is open after the Phase 4 production persistence hardening pass.
- Alembic baseline files and SQLAlchemy metadata now exist, but the runtime still needs a real PostgreSQL database URL, migration execution policy, pool sizing, and deployment runbook.
- Repository transaction boundaries are available through `RepositorySession` / `UnitOfWork`; application services still need to adopt them when the local Phase 2 runtime is replaced by durable workers.
- JobEvent seq allocation is concurrency-tested with repository-level in-process locking. Before multi-process workers, PostgreSQL should use row locking, advisory locking, or a per-job sequence allocation strategy.
- ToolCall and Artifact writes have idempotent repository behavior. A later queue phase still needs explicit worker attempt records, retry policy, crash recovery policy, and dead-letter handling.
- S3/MinIO metadata mapping remains clear, but live presigned URL generation, bucket policy, retention/lifecycle rules, and access-control checks remain future work.

## 2026-06-26 Phase 3 Follow-ups

- No new P0 blocker is open after the Phase 3 persistence foundation pass.
- Repository interfaces and SQLite-testable SQLAlchemy implementations now cover Project, Dataset, DataProfile, Job, JobEvent, ToolCall, Artifact, Recipe, and Report. A later phase still needs production transaction boundaries, Alembic adoption, PostgreSQL connection/session lifecycle, and idempotent worker writes.
- JobEvent seq cursor semantics are implemented for the local runtime and repository layer, including in-process duplicate-seq protection. A later phase still needs database-level multi-process locking strategy, production SSE backpressure, heartbeat, auth checks, and reconnect/load behavior under concurrent workers.
- Artifact storage mapping now covers local files and S3/MinIO-compatible metadata. A later phase still needs a live object-storage client, presigned URL policy, access-control checks, retention/lifecycle policy, and preview generation strategy.
- `reports` now has repository coverage and migration metadata. Report-specific API list/detail routes beyond artifact/report downloads remain future work.
- `S3CompatibleArtifactStorage.signed_url()` intentionally returns a `not_implemented` placeholder until live credentials, bucket policy, and signed URL expiry rules are decided.

## 2026-06-25 Phase 2 Acceptance Audit Follow-ups

- No new P0 blocker is open after the Phase 2 acceptance hardening pass.
- Phase 2 Recipe and AnalysisPlan schema shape is now aligned with the shared schema. Future schema changes should update `docs/13_SHARED_SCHEMA_SPEC.md`, Python schemas, TypeScript schemas, runtime emitters, and tests together.
- Ignored verification outputs (`node_modules`, `.next`, pytest cache/temp directories, Python bytecode, and TypeScript build info) are intentionally not part of Git or archive handoffs and should be cleaned before packaging.

## 2026-06-25 Phase 2 Follow-ups

- Phase 2 now proves the repository/API shape with in-memory state. A later phase still needs to decide the exact PostgreSQL repository interfaces and migration path for projects, datasets, jobs, tool calls, events, artifacts, recipes, and reports.
- Phase 2 artifact lookup reads local files directly. A later phase still needs to map the same API contract to MinIO/S3 signed URLs and access-control checks.
- Phase 2 job creation drains the LocalWorkerRuntime immediately for deterministic acceptance. A later phase still needs durable queue semantics, retry/cancel behavior, and SSE cursor persistence.
- Phase 2 supports local file paths and inline small text uploads for acceptance. Production upload sessions, object-storage direct upload, and file security limits remain future work.

## 2026-06-25 Phase 1 Acceptance Follow-ups

- Phase 1 now accepts `preview_png` as a required artifact family, but the MVP implementation may use a minimal valid PNG fallback when Kaleido/Chromium is unavailable. V1 still needs a decision on whether render workers must install and manage Kaleido/Chromium for real chart snapshots.
- Phase 1 product-flow acceptance is currently proven by an in-memory deterministic runtime. Next phase must decide the exact repository/API shape for replacing demo project/dataset/job/artifact state.
- The `/jobs/{job_id}/events/stream` route now exposes an SSE-style boundary without `sse-starlette`. Next phase must decide whether to keep plain `StreamingResponse` or introduce a Starlette-compatible SSE dependency.
- Phase 1 engineering reproducibility is now fixed on `uv.lock` for Python and `apps/web/package-lock.json` for frontend npm installs. Future dependency changes should update those lockfiles in the same commit as dependency declarations.

## Product

- 产品正式名称优先采用 Material Insight Studio、MatViz Agent Platform，还是 LabPilot Materials Workspace？
- V1 是否支持公开分享、匿名报告链接和外部协作者查看？
- V1 是否支持 PDF 报告导出？
- Guided / Expert 模式的最小可用范围是什么？

## Architecture

- 何时从 FastAPI 模块化单体拆分为独立 Data / Agent / Visualization 服务？
- LabPilot 集成时采用 NestJS BFF、API Gateway 代理，还是 iframe / embedded workspace？

## Frontend

- V1 是否支持用户自定义 Dashboard 拖拽布局？
- V1 是否评估 native MatterViz React 集成，替代部分 iframe artifact？
- 3D Viewer 的全屏、截图和结构选择器交互细节如何设计？

## Backend

- V1 分片上传和断点续传的最大文件规模目标是多少？
- Artifact / Recipe 何时需要独立 version tree 和 diff 视图？
- Artifact 生命周期和自动清理策略如何定义？

## Agent

- V1 Expert 模式是否允许用户手动编辑 JSON Plan 后再执行？
- V1 多模型路由按哪些任务类型拆分：Planner、Explainer、Report，还是按成本等级？
- V1 工具文档 RAG 使用 pgvector 还是 Qdrant？

## Materials Domain

- V2 VASP 输出优先解析 vasprun.xml、OUTCAR、XDATCAR 还是 DOSCAR？
- V1 代表结构聚类使用 composition embedding 还是 structure fingerprint？
- V1 首批高级工具优先实现 phonon、trajectory、RDF/XRD，还是 ML error-by-domain？
- V1/V2 外部生态集成优先级如何排序：Materials Project、OPTIMADE、AiiDA、atomate2，还是内部数据库 connector？
- 电子结构工具是否进入 V2 核心范围，还是作为专业插件优先接入？

## Security

- V1 组织级 BYOK 的继承、撤销和预算模型如何设计？
- V1 Prompt injection 模型辅助检测使用哪类评估集？
- V2 是否需要 gVisor / Firecracker / Kubernetes Jobs 等更强隔离？

## Implementation

- MVP 是否接受 `preview_png` 继续保持 optional，还是在 render-worker 里显式安装并管理 Kaleido/Chromium？
- ZIP 安全解包的 MVP 限制值如何定：最大文件数、最大展开大小、最大嵌套层级？
- EXTXYZ with lattice：已决定优先通过 ASE 解析后转 pymatgen Structure，不再单独实现轻量 parser。
- V1/V2 manifest 工具在进入可执行阶段前，是否要求先补齐与 MVP 同等级的 `additionalProperties=false` paramsSchema？
- 下一阶段实现 SSE 时需要选择与 `fastapi 0.115.x` / `starlette 0.46.x` 兼容的 SSE 方案；当前全局环境中的 `sse-starlette 3.4.1` 要求 `starlette>=0.49.1`，不能直接作为项目依赖锁定。
