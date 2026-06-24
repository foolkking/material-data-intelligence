# Phase 2：总体系统架构

## 1. 本阶段目标

定义材料数据智能分析与可视化平台的总体系统架构，包括前端、API Gateway、Agent Service、Data Service、Visualization Service、Worker Service、Artifact Service、Storage Layer、Queue Layer 和 Security Boundary 的职责边界。

本阶段给出逻辑服务拆分和 MVP 部署形态，为 Phase 3 前端工作台、Phase 4 后端与数据库、Phase 5 Agent 编排、Phase 6 Tool Registry 和 Phase 8 高并发任务系统提供架构基线。

## 2. 本阶段解决的问题

### 关键架构决策

| 问题 | Phase 2 决策 |
|---|---|
| MVP API 主服务用 NestJS 还是 FastAPI | MVP 采用 FastAPI，减少 Python 材料生态集成成本；保留未来 NestJS BFF / LabPilot 集成边界。 |
| Python 材料服务与主 API 是否拆开 | MVP 采用逻辑服务拆分、部署上模块化单体 + 独立 Worker；V1 按负载拆成独立服务。 |
| 异步编排用什么 | MVP 使用 Celery + Redis；复杂工作流和企业部署可升级 Temporal。 |
| 是否所有耗时任务异步 | 是。上传解析、Data Profile、Agent Plan、工具执行、3D 渲染、报告生成全部走 Job。 |
| 数据存哪里 | PostgreSQL 存元数据，S3/MinIO 存原始文件和 Artifact，Redis 存队列、缓存和短期状态。 |
| 安全边界在哪里 | API 鉴权、项目权限、Tool Registry 校验、Worker 沙箱、Secret 管理、Artifact 访问控制共同构成边界。 |

### 架构目标

- 前端不卡顿：所有长任务通过 Job 事件流渐进展示。
- Agent 不越权：只能生成 JSON Plan，执行必须经过 Tool Registry。
- 材料工具隔离：pymatviz / MatterViz / pymatgen / ASE / phonopy 只在受控 Worker 中执行。
- Artifact 可复现：每次工具调用保存输入引用、参数、版本、输出和日志。
- MVP 简洁可做：先用 FastAPI 模块化单体和 Celery Worker，避免过早微服务化。
- 后续可扩展：逻辑边界清晰，能逐步拆分服务和扩展 Worker Pool。

## 3. 设计原则

- 逻辑服务清晰，物理部署渐进：MVP 不强制微服务，但代码边界按服务划分。
- API 同步轻量，计算异步执行：API 不直接跑解析、绘图、LLM 报告等重任务。
- 数据与 Artifact 分层：数据库只存元数据和索引，大文件和图表产物进入对象存储。
- Event-first UI：前端主要订阅 JobEvent 并按 Artifact URL 拉取结果。
- Tool Registry 是执行边界：任何图表、3D、分析工具都不能绕过注册表。
- Worker 最小权限：Worker 只拿到任务所需数据和临时 Secret，不持久化明文密钥。
- 可观测性内建：Job、ToolCall、Worker、Artifact、LLM 调用都产生结构化日志和指标。

## 4. 总体架构

### 4.1 逻辑架构图

```text
┌────────────────────────────────────────────────────────────┐
│ Frontend Workspace                                         │
│ Next.js / React / TypeScript / Plotly.js / MatterViz        │
│ Data Panel | Visualization Canvas | Agent Panel | Logs      │
└──────────────────────────────┬─────────────────────────────┘
                               │ REST / SSE / WebSocket
┌──────────────────────────────▼─────────────────────────────┐
│ API Gateway / Application Service                           │
│ Auth | Project | Dataset | Upload | Job | Artifact | Config │
│ MVP: FastAPI modular app                                    │
└───────────────┬───────────────────────┬────────────────────┘
                │                       │
                │                       │
┌───────────────▼──────────────┐  ┌─────▼────────────────────┐
│ Domain Services               │  │ Queue Layer              │
│ Data | Agent | Visualization  │  │ Redis broker/cache/transient │
│ Artifact | Security | Config  │  │ Celery task routing      │
└───────────────┬──────────────┘  └─────┬────────────────────┘
                │                       │
                │                       │
┌───────────────▼───────────────────────▼────────────────────┐
│ Worker Pool                                                 │
│ parse-worker | viz-worker | render-worker | llm-worker      │
│ pymatviz / MatterViz / pymatgen / ASE / phonopy / Plotly    │
└───────────────┬───────────────────────┬────────────────────┘
                │                       │
┌───────────────▼──────────────┐  ┌─────▼────────────────────┐
│ PostgreSQL                    │  │ Object Storage           │
│ users/projects/jobs/toolcalls │  │ S3/MinIO raw files       │
│ profiles/artifacts/recipes    │  │ Plotly/MatterViz/report  │
└──────────────────────────────┘  └──────────────────────────┘
```

### 4.2 MVP 部署拓扑

```text
web
  Next.js frontend

api
  FastAPI application
  logical modules: auth/project/data/agent/jobs/artifacts/config

worker
  Celery workers
  queues: parse, viz, render, llm, export

postgres
  metadata and audit

redis
  broker, cache, rate limit state, transient worker state

minio
  raw files and artifacts
```

MVP 不是无边界单体。代码结构应按逻辑服务组织，后续可拆：

```text
api_gateway
domain/data_service
domain/agent_service
domain/visualization_service
domain/artifact_service
domain/security
workers/parse_worker
workers/viz_worker
workers/render_worker
workers/llm_worker
```

## 5. 核心模块与职责

| 模块 | 职责 | MVP 部署 |
|---|---|---|
| Frontend Workspace | 工作台 UI、上传、Data Profile、图表、3D、Agent Timeline、Artifact 面板 | Next.js |
| API Gateway | Auth、权限、项目、数据集、上传、Job、Artifact、配置 API | FastAPI |
| Data Service | 文件识别、解析调度、Data Profile、字段映射、质量检查 | FastAPI module + parse worker |
| Agent Service | Intent、Plan、Report、LLM Provider、Prompt Guard | FastAPI module + llm worker |
| Visualization Service | Tool Registry、Adapter、参数校验、工具调度 | FastAPI module + viz worker |
| Worker Service | 执行 parse/viz/render/export/llm 任务、重试、超时 | Celery workers |
| Artifact Service | Artifact 元数据、对象存储路径、预览、导出、Recipe | FastAPI module + object storage |
| Storage Layer | PostgreSQL、Redis、S3/MinIO | managed services / containers |
| Queue Layer | Job routing、event emission、worker dispatch | Celery + Redis |
| Security Layer | AuthN/AuthZ、Secret、sandbox、audit、rate limit、prompt injection guard | cross-cutting |

## 6. 同步 / 异步边界

### 同步 API

同步接口只做轻量操作：

- 用户登录和会话校验。
- 创建项目、读取项目配置。
- 创建上传会话。
- 完成文件上传后的任务登记。
- 查询 Data Profile、Job、Artifact、Recipe 元数据。
- 获取签名下载/预览 URL。
- 订阅 SSE/WebSocket 事件入口。

### 异步任务

MVP 必须异步执行：

- ZIP 解压和批量文件识别。
- CIF / POSCAR / CSV / JSON limited / XYZ/EXTXYZ 基础解析。
- Data Profile 和数据质量检查。
- LLM Analysis Plan 生成。
- MVP Tool Set 图表、指标和表格结果生成。
- 3D Viewer HTML / optional snapshot / PNG preview。
- Report 和 Recipe 生成。

V1 必须异步执行：

- phonopy / trajectory 深度解析。
- RDF、XRD、composition embedding、UMAP/t-SNE。
- SVG/PDF high-resolution export。

### 任务状态机

```text
created
  -> queued
  -> running
  -> partial_success
  -> completed

created
  -> queued
  -> running
  -> failed

running
  -> cancel_requested
  -> cancelled
```

## 7. 数据流 / 控制流

### 7.1 上传与 Data Profile 数据流

```text
Frontend
  -> POST /upload-sessions
  -> PUT object upload URL
  -> POST /datasets/{id}/parse-jobs
  -> Celery parse-worker
  -> raw file from MinIO
  -> parsed objects / normalized metadata
  -> PostgreSQL data_profiles
  -> object storage normalized payloads
  -> job_events: profile.ready
  -> Frontend refreshes data panel
```

### 7.2 自然语言分析控制流

```text
Frontend prompt
  -> POST /analysis-requests
  -> API loads Data Profile + Tool Registry + Project Config
  -> llm-worker generates JSON Analysis Plan
  -> Execution Controller validates plan
  -> job_events: plan.generated
  -> user clicks Run
  -> ToolCall jobs enqueued
  -> viz/render workers execute
  -> artifacts saved
  -> report generated
```

### 7.3 Artifact 展示流

```text
Worker writes artifact to MinIO
  -> Artifact Service records metadata in PostgreSQL
  -> job_events: artifact.ready
  -> Frontend receives event
  -> GET /artifacts/{id}
  -> render chart card / viewer / report panel
```

## 8. API / Schema 草案

正式 API 在 Phase 4 定义。本阶段固定服务边界级接口。

### Project / Dataset

```http
POST /projects
GET /projects/{project_id}
GET /projects/{project_id}/datasets
POST /projects/{project_id}/datasets
```

### Upload / Parse

```http
POST /datasets/{dataset_id}/upload-sessions
POST /upload-sessions/{session_id}/complete
POST /datasets/{dataset_id}/parse-jobs
GET /datasets/{dataset_id}/profile
PATCH /datasets/{dataset_id}/field-mappings
```

### Analysis / Jobs

```http
POST /analysis-requests
GET /analysis-requests/{request_id}/plan
POST /analysis-requests/{request_id}/run
GET /jobs/{job_id}
GET /jobs/{job_id}/events
POST /jobs/{job_id}/cancel
```

### Artifact / Recipe

```http
GET /jobs/{job_id}/artifacts
GET /artifacts/{artifact_id}
GET /artifacts/{artifact_id}/download-url
POST /recipes
POST /recipes/{recipe_id}/run
```

### Core Architecture Types

```ts
type JobEvent = {
  id: string;
  jobId: string;
  seq: number;
  eventType: string;
  status: "info" | "running" | "success" | "warning" | "error";
  message: string;
  progress?: number;
  payload?: Record<string, unknown>;
  createdAt: string;
};

type ToolExecutionRequest = {
  jobId: string;
  toolCallId: string;
  toolId: string;
  inputRefs: InputRef[];
  params: Record<string, unknown>;
  projectConfigRef: string;
  artifactTypes: ArtifactType[];
};

// ArtifactRecord 不在 Phase 2 单独维护正式结构。
// 正式字段以 docs/13_SHARED_SCHEMA_SPEC.md 的 Artifact 为准。
type ArtifactRecord = Artifact;
```

## 9. 数据库表草案

Phase 4 会细化字段、索引、约束和迁移。本阶段按架构层分组。

| 分组 | 表 |
|---|---|
| Identity | `users`、`organizations`、`organization_members`、`project_members` |
| Project | `projects`、`project_configs`、`user_configs` |
| Data | `datasets`、`files`、`data_profiles`、`field_mappings`、`normalized_objects` |
| Agent | `sessions`、`messages`、`analysis_requests`、`analysis_plans` |
| Jobs | MVP: `jobs`、`job_events`; V1: `worker_runs` |
| Tools | `tool_calls`、`tool_registry_versions` |
| Artifacts | MVP: `artifacts`、`visualization_recipes`、`reports`; V1: `artifact_versions` |
| Security | MVP: `secrets`、`audit_logs`; V1: `rate_limit_events` |
| Plugins | V2: `plugins`、`plugin_tools`、`plugin_versions` |

### 数据库存储原则

- PostgreSQL 存可查询元数据、状态、权限、索引和审计。
- 对象存储存 raw files、normalized payloads、Plotly JSON、HTML、PNG preview、MatterViz HTML、metrics/table、report files；SVG/PDF high-resolution export 进入 V1。
- Redis 存短期状态、队列、缓存、rate limit counters，不作为唯一持久化来源。
- Celery result backend 不作为任务事实源；Worker 完成状态必须写入 PostgreSQL `jobs`、`tool_calls`、`job_events` 和 `artifacts`。

## 10. 前端交互草案

### 前端架构

```text
Next.js app
  app/(workspace)/projects/[id]
  components/data-panel
  components/visualization-canvas
  components/agent-panel
  components/bottom-panel
  lib/api-client
  lib/event-client
  stores/workspace-store
```

### 数据获取策略

| 数据 | 获取方式 |
|---|---|
| 项目和配置 | REST + TanStack Query |
| 文件上传 | signed URL / chunk upload later |
| Job 进度 | SSE MVP；WebSocket 可选 |
| 图表数据 | Artifact URL 拉取 |
| 3D Viewer | viewer artifact HTML 或结构 JSON |
| UI 临时状态 | Zustand / Jotai |

### 前端事件处理

```text
job_events stream
  -> update Agent Timeline
  -> update chart card state
  -> update artifact list
  -> update warnings
  -> trigger TanStack Query invalidation for affected resources
```

## 11. 高并发、安全、扩展性考虑

### 高并发

- API 只提交任务，不执行 CPU 密集任务。
- Celery queue 按任务类型分队列：`parse`、`viz`、`render`、`llm`、`export`。
- Worker 设置并发、内存、超时、重试和最大 Artifact 大小。
- Artifact 分阶段生成，前端按事件渐进展示。
- 缓存 key 包含 raw file hash、normalized data hash、tool id、params hash、tool version、style config hash。

### 安全边界

| 边界 | 机制 |
|---|---|
| API 边界 | AuthN、AuthZ、rate limit、request validation |
| Project 边界 | project membership、role-based permissions |
| Tool 边界 | Tool Registry、JSON Schema、input availability check |
| Worker 边界 | sandbox、resource limit、no arbitrary shell、temporary workspace |
| File 边界 | file type whitelist、zip bomb guard、path traversal guard、parse timeout |
| Secret 边界 | encrypted storage、temporary injection、never logged |
| Prompt 边界 | system policy、profile/tool docs separation、prompt injection checks |
| Artifact 边界 | signed URL、project permission check、no public sharing in MVP |

### 扩展性

- V1 可把 Agent Service、Data Service、Visualization Service 拆成独立 FastAPI services。
- V1/V2 可将 Celery 升级为 Temporal，用于长工作流、补偿和可恢复执行。
- 若接入 LabPilot，可增加 NestJS BFF 或通过现有 LabPilot API Gateway 代理。
- Worker Pool 可按任务类型水平扩容，render/export worker 可单独扩容。
- 工具扩展通过 Tool Registry 和 plugin_tools 注册，不修改 Agent 核心。

## 12. 本阶段产出的目标文件

```text
docs/02_SYSTEM_ARCHITECTURE.md
persistent/DESIGN_PROGRESS.md
persistent/TASK_BOARD.md
persistent/ARCHITECTURE_DECISIONS.md
persistent/OPEN_QUESTIONS.md
persistent/CHANGELOG.md
```

## 13. 下一阶段任务

Phase 3：前端工作台设计。

需要定义：

- 页面布局。
- 左侧数据资产区。
- 中央可视化画布。
- 右侧 Agent 面板。
- 底部日志 / 代码 / Artifact / Recipe 面板。
- 图表卡片设计。
- 3D Viewer 设计。
- 任务进度展示。
- 大图表流畅加载策略。
