# OPEN_QUESTIONS

## 2026-07-03 Phase 8B Follow-ups (Persisted Plans + Queue Runtime)

- **Closed/frozen: QueueWorkerRuntime + persisted AnalysisPlan execution.** The main worker path now loads `job.plan_id`, fetches the persisted `AnalysisPlan`, reconstructs it, and executes exact `steps`; tests prove a persisted 1-step plan creates exactly 1 ToolCall, not the deterministic 5-tool fallback.
- **Closed/frozen: PostgreSQL persisted plan schema.** Alembic revision `0002_phase8b_plans` adds `analysis_plans`, `jobs.plan_id`, and required indexes. CI verifies these through Alembic upgrade head against PostgreSQL.
- **Closed/frozen: service-backed Phase 8B gate.** This local machine has no Docker CLI, so the PostgreSQL + Redis + MinIO Phase 8B integration test could not be run locally. GitHub Actions run `28631817086` on Phase 8B code acceptance commit `962c429` ran Phase 6 + Phase 8B integration with 19 passed, 0 skipped, 0 failed.
- **Frontend Planner UX remains deferred to Phase 8C.** Do not start Phase 8C until Phase 8B is frozen by CI-backed service integration.
- **Multi-step dependency graph remains deferred.** Phase 8B executes persisted steps in order and preserves the existing `inputRefs`/`object_store` mechanism; it does not add DAG scheduling or inter-step artifact binding.
- **True LLM integration remains deferred.** Default tests continue to use MockLLMProvider/fake transport; real OpenAI/DeepSeek service tests need a separate opt-in gate and redaction policy.
- **Production secret encryption remains deferred.** Plan persistence rejects credential-like params, but the production `EncryptedSecretStore`/KMS path is still not implemented.

## 2026-06-27 Phase 8A Follow-ups (Plan Execution Bridge)

- **LLM→execution closed loop is now CLOSED at the local-runtime level.** `/planner/jobs` (execute=True) runs the EXACT validated LLM plan through `Phase2ProductRuntime` → Tool Registry → Adapter, proven by `test_runtime_executes_exact_provided_plan_one_tool_call` (1 step → 1 ToolCall, not deterministic 5).
- **Remaining: QueueWorkerRuntime + PostgreSQL plan persistence.** Execution currently uses the in-memory synchronous `Phase2ProductRuntime`. The validated plan is NOT yet persisted to PostgreSQL nor enqueued onto the Redis `QueueWorkerRuntime`. Wiring `analysis_plan` into the queue worker + a `persisted_plans` table (Alembic migration) is the next integration step.
- **Multi-step dependency graph deferred.** The bridge executes steps in plan order; there is no inter-step data-dependency resolution beyond the existing inputRefs/object_store mechanism. A real DAG executor is future work.
- **Plan input binding is still conventional.** The LLM plan must reference the conventional `ml_table` (or `formulas`/`structures`) normalized object refs. A general field-mapping/resolution layer between LLM logical refs and dataset objects is future work.
- Real LLM integration, production envelope encryption, frontend Planner UX, and plan auto-repair remain deferred (unchanged from Phase 7 records).

## 2026-06-27 Phase 7 Follow-ups (LLM Planner + BYOK)

- **Production envelope encryption is NOT implemented.** `EncryptedSecretStore` is a placeholder that raises `NotImplementedError`. Only `InMemorySecretStore` works, and it is for dev/test ONLY — it holds plaintext values in memory and must never be used in production. A real backend (KMS, Fernet, or HashiCorp Vault) is required before any production BYOK use.
- **LLM → execution closed loop is NOT complete.** `POST /planner/jobs` generates an LLM plan, validates it, and then creates a job via `Phase2ProductRuntime.create_job()`. However, that runtime internally regenerates its own **deterministic** plan (`build_phase2_plan`) — the validated LLM plan is currently NOT the plan that executes. The job status returned is "created" (in-memory Phase 2 path), not a real enqueue onto Redis/PostgreSQL. Wiring the validated LLM plan into the real QueueWorkerRuntime + Tool Registry + Adapter execution path is deferred to a later phase.
- **Real OpenAI/DeepSeek integration tests are optional and not in the default suite.** All Phase 7 tests use `MockLLMProvider` or a fake transport. A real LLM integration test (gated behind an env var like `MDI_RUN_LLM_INTEGRATION=1` + `OPENAI_API_KEY`) is future work; it must never run in the default `pytest -q`.
- **Prompt / completion logging policy is undecided.** Currently no prompt or completion is logged. If debug logging is added later, it MUST pass through `redact_credential_values()` and default to off. A formal policy (what to log, retention, redaction guarantees) is open.
- **Runtime full-chain secret-leak audit is not yet done.** Phase 7 has unit-level redaction tests and a secret-list-no-plaintext test, but no end-to-end audit proving secrets never reach JobEvent / Artifact metadata / Recipe / Report in the live runtime. The current code has no path that writes secrets to those sinks, but an explicit audit test is future work.
- **Plan auto-repair is intentionally not implemented.** PlanValidator is strict — invalid plans are rejected, not repaired. Auto-repair (ask the LLM to fix its own invalid plan) is deferred to avoid silently executing mutated plans.

## 2026-06-26 Phase 6 Follow-ups

- **Acceptance: CONDITIONAL PASS.** No P0 blocker in the code or test design. All 18 integration tests skip cleanly because Docker is not available on this machine. Git is clean at commit `e3c7a73`.
- P0-2 (integration tests all skipped) is unresolved at the infrastructure level: Docker must be installed and services started before live tests can run. This is by design — tests skip rather than fail on missing infrastructure.
- P0-3 (Alembic test) is resolved: the committed test calls real `alembic.command.upgrade(alembic_cfg, "head")` with downgrade+reupgrade cycle and index existence verification.
- P0-4 (service-backed loop) is resolved: the committed test uses real Tool Registry + BasicMetricsAdapter through `execute_tool_request()`, not a fake executor.
- **Cannot enter Phase 7** until: (1) Docker is installed, (2) `docker compose up -d postgres redis minio` succeeds with all services healthy, (3) `MDI_RUN_INTEGRATION=1 python -m pytest -q -m integration` passes with zero skipped tests.
- Concurrent JobEvent seq test uses `ThreadPoolExecutor(max_workers=6)` with 30 concurrent appends — unit-level concurrency smoke; true multi-process/container stress testing remains a production-readiness task.
- Queue integration tests use synchronous `handle_job()` after enqueue (simulating worker process fetch). Real RQ multi-worker deployment remains later work.
- MinIO presigned URL HTTP GET verification requires the caller on the Docker network or localhost. The API-level test (URL contains bucket/key, expires, content_type) is in place.
- CI pipeline needs a service-backed job: `docker compose up -d postgres redis minio` → wait healthy → `MDI_RUN_INTEGRATION=1 python -m pytest -q -m integration`.

## 2026-06-26 Phase 5 Follow-ups

- No P0 blocker is open after the Phase 5 PostgreSQL runtime, queue worker, and MinIO integration pass.
- PostgreSQL runtime configuration, Alembic env override, Docker Compose infrastructure, and runbook now exist. A later deployment pass still needs pool sizing, migration rollback policy, backup/restore policy, and production secret injection.
- QueueWorkerRuntime now supports repository-backed job handling, duplicate enqueue stability, and retry idempotency tests. Later work still needs worker process supervision, dead-letter queues, exponential backoff policy, visibility timeout policy, and operational metrics.
- PostgreSQL JobEvent seq allocation now uses a transaction-scoped advisory lock keyed by `job_id`. Multi-process/container stress testing remains a production-readiness task beyond the default unit suite.
- S3/MinIO storage now supports live put/get/exists/presigned-url behavior when a boto3-compatible client or credentials are configured. Bucket creation policy, bucket lifecycle rules, object retention, access-control checks, and preview object policy remain open.
- Integration tests are intentionally opt-in with `MDI_RUN_INTEGRATION=1`; CI still needs a service-backed job that starts PostgreSQL, Redis, and MinIO and runs the integration marker.

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
