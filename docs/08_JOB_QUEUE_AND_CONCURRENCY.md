# Phase 8：高并发任务系统与流畅展示设计

## 1. 本阶段目标

定义平台从 MVP 起支撑多用户、长任务、渐进展示和资源控制的任务系统，包括 Job Queue、Worker Pool、SSE/WebSocket 事件流、任务状态机、缓存、大数据降采样、3D LOD、资源限制、多用户并发和可观测性。

## 2. 本阶段解决的问题

### 为什么必须异步

MVP 以下操作不能同步阻塞 API 请求：

- ZIP 解压和批量文件识别。
- CIF / POSCAR / CSV / JSON limited / XYZ/EXTXYZ 基础解析。
- Data Profile 构建和结构异常检查。
- LLM 计划和报告生成。
- MVP Tool Set 图表、指标和表格结果生成。
- MatterViz / Plotly 3D 渲染。
- PNG 导出；SVG/PDF 进入 V1 论文图导出链路。

V1 以下操作也必须异步：

- phonopy / trajectory 深度解析。
- RDF、XRD、composition embedding、UMAP/t-SNE。
- stable MatterViz snapshot。
- SVG/PDF high-resolution export。

### Phase 8 决策

| 问题 | 决策 |
|---|---|
| MVP 事件流 | 使用 SSE 推送 JobEvent；WebSocket 推迟到 V1 用于协作和双向控制。 |
| Worker 分层 | 按 `parse`、`profile`、`llm`、`viz`、`render`、`export` 队列拆分。 |
| 状态事实来源 | PostgreSQL `jobs/job_events/tool_calls/artifacts` 是事实来源；Redis 只做 broker/cache/短期状态。 |
| 大图流畅展示 | 小数据直接 Plotly，中数据 density/hexbin，大数据后端预聚合或采样。 |
| 3D LOD | 按 atom count / frame count 自动降级，默认关闭大结构 bonds 和 trajectory 全帧加载。 |
| 资源控制 | 按 user/project/org 做并发、预算、内存、CPU、超时和 Artifact 大小限制。 |

## 3. 设计原则

- API 快速返回：创建 Job 后立即返回 `job_id`。
- 事件驱动 UI：前端主要依赖 JobEvent 更新进度。
- Artifact 分阶段可见：每个图表完成即展示，不等待全任务完成。
- 资源先校验再执行：预计超限的任务不进入 Worker。
- Worker 可水平扩展：不同队列可独立扩容。
- 状态可恢复：Worker 崩溃后可从 PostgreSQL 状态恢复。
- 缓存优先：相同输入、工具、参数和版本不重复计算。

## 4. 核心模块

| 模块 | 职责 |
|---|---|
| Job Manager | 创建 Job、状态机、取消、重试、优先级 |
| Queue Router | 根据任务类型路由到 Celery queue |
| Worker Pool | 执行 parse/profile/llm/viz/render/export |
| Event Publisher | 写 `job_events` 并推送 SSE |
| Cache Manager | 计算 cache key、命中 Artifact、失效策略 |
| Resource Guard | 并发、预算、CPU、内存、超时、大小限制 |
| Sampling Service | 大表格降采样、density/hexbin、预聚合 |
| LOD Service | 3D 结构和 trajectory 分级加载策略 |
| Observability | metrics、logs、traces、worker health |

## 5. Job Queue 设计

### 队列

| Queue | 任务 | 特点 |
|---|---|---|
| `parse` | 文件识别、解压、解析 | I/O + CPU 混合 |
| `profile` | Data Profile、质量检查 | CPU 中等 |
| `llm` | Plan、解释、报告 | 外部 API、预算敏感 |
| `viz` | pymatviz / Plotly 计算 | CPU 中高 |
| `render` | MVP：Plotly HTML、Plotly PNG preview、MatterViz viewer HTML、optional snapshot；V1：SVG/PDF/high-resolution export | CPU/内存/浏览器资源 |
| `export` | report/export package | I/O 密集 |

### Job 状态机

```text
created -> queued -> running -> partial_success -> completed
created -> queued -> running -> failed
running -> cancel_requested -> cancelled
failed -> queued -> running
```

`partial_success` 用于批量任务：部分文件或工具失败，但已有 Artifact 可用。Retry 不新增专门的 JobStatus；ToolCall retry 创建新的 attempt record，Job 状态回到 `queued` / `running`。

## 6. Worker Pool

### Worker 类型

| Worker | 默认任务 | 资源策略 |
|---|---|---|
| parse-worker | archive、CIF/POSCAR/CSV/JSON parse | 中等 CPU，严格文件安全 |
| profile-worker | profile、quality、recommendations | CPU 中等，可并行 |
| llm-worker | planner、explainer、report | rate limit + budget |
| viz-worker | pymatviz tools | CPU 中高，按 costLevel 限流 |
| render-worker | MVP：Plotly HTML/PNG preview、MatterViz viewer HTML、optional snapshot；V1：SVG/PDF/high-resolution export | 高内存，低并发 |
| export-worker | report package、zip export | I/O 中等 |

### 任务幂等

每个 Worker 任务必须可重试：

- 输入引用不可变。
- 输出 Artifact 用 deterministic key 或 version。
- ToolCall 状态更新使用 compare-and-set。
- 重试不能重复扣预算或重复生成冲突 Artifact。

## 7. SSE / WebSocket 进度推送

### MVP：SSE

MVP 使用 SSE：

```http
GET /jobs/{job_id}/events?cursor=evt_xxx
```

原因：

- 单向进度流足够。
- 易于实现断线重连。
- 与 JobEvent 表天然匹配。
- 比 WebSocket 运维更简单。

### V1：WebSocket

WebSocket 用于：

- 多用户协作。
- 任务交互控制。
- 实时评论。
- 复杂 workspace presence。

### JobEvent

```ts
type JobEvent = {
  id: string;
  jobId: string;
  seq: number;
  eventType:
    | "job.created"
    | "job.queued"
    | "job.running"
    | "file.parsed"
    | "profile.ready"
    | "plan.generated"
    | "tool.started"
    | "artifact.ready"
    | "tool.warning"
    | "report.ready"
    | "job.completed"
    | "job.failed";
  status: "info" | "running" | "success" | "warning" | "error";
  message: string;
  progress?: number;
  payload?: Record<string, unknown>;
  createdAt: string;
};
```

事件流只推小 payload；大图表数据只通过 Artifact URL 拉取。

## 8. 缓存策略

### Cache key

```text
cache:{kind}:{input_hash}:{tool_id}:{tool_version}:{adapter_version}:{params_hash}:{style_hash}
```

### 缓存对象

| 对象 | 存储 |
|---|---|
| normalized object | S3/MinIO + metadata |
| Data Profile | PostgreSQL + Redis hot cache |
| Tool result | Artifact metadata + object storage |
| Plotly JSON / HTML | object storage |
| preview image | object storage |
| LLM plan draft | PostgreSQL，短 TTL 可选 |

### 失效条件

- 原始文件 hash 变化。
- parser / adapter / tool version 变化。
- params 或 style config 变化。
- 用户选择 refresh。
- 安全策略或权限变化影响访问。

## 9. 大数据降采样

### 表格可视化阈值

| 数据量 | 策略 |
|---|---|
| `< 10k` points | 直接 Plotly scatter |
| `10k - 500k` points | density scatter / hexbin / server-side sampling |
| `> 500k` points | 后端预聚合、分桶、tile 或只输出 summary + sampled preview |

### 降采样原则

- 保留 outliers。
- 保留类别分布。
- 对用户说明采样策略。
- Artifact metadata 记录 sample method 和 sample size。

## 10. 3D LOD

| 规模 | 策略 |
|---|---|
| `< 500 atoms` | atoms + bonds + cell |
| `500-5000 atoms` | atoms + cell，bonds 默认关闭 |
| `> 5000 atoms` | LOD/sampled structure，用户手动加载完整 |
| trajectory `< 200 frames` | 可抽帧预览 |
| trajectory `>= 200 frames` | 默认抽帧 + frame window |

LOD metadata：

```json
{
  "lod": "sampled",
  "original_atoms": 12480,
  "rendered_atoms": 1200,
  "bonds_enabled": false,
  "sampling_method": "spatial_grid"
}
```

## 11. 资源限制

### 维度

| 限制 | 作用 |
|---|---|
| max concurrent jobs per user | 防止单用户占满队列 |
| max concurrent jobs per project | 保护项目预算 |
| max rows / structures / atoms / frames | 防止超大任务 |
| timeout per tool | 防止 Worker 卡死 |
| max artifact size | 防止对象存储膨胀 |
| max LLM cost per job | 控制 BYOK/系统 Key 成本 |

### 默认策略

- low-cost 工具可并发较高。
- high-cost 工具排队并限流。
- render-worker 默认低并发。
- LLM worker 按 provider / key 限速。

## 12. 多用户并发

### Fair scheduling

队列调度考虑：

- org plan。
- project priority。
- user concurrency。
- job costLevel。
- submitted time。

MVP 可先实现简单优先级 + per-user/project concurrency；V1 再做更细公平调度。

### Budget

预算来源：

- user config。
- project config。
- organization quota。
- BYOK provider limits。

超预算时：

- Plan 生成 warning。
- Run 阶段阻止 high-cost task。
- 提示用户调整配置或减少输入规模。

## 13. 可观测性

### Metrics

- job count by status。
- queue length by queue。
- worker runtime by task type。
- tool success/failure rate。
- artifact size。
- cache hit rate。
- LLM cost and latency。
- SSE connection count。

### Logs

- request_id。
- job_id。
- tool_call_id。
- project_id。
- worker_id。
- error_code。

### Tracing

推荐链路：

```text
API request -> job created -> worker task -> tool adapter -> artifact export -> event published
```

## 14. 数据流 / 控制流

```text
POST /analysis-requests/{id}/run
  -> Job Manager
  -> Resource Guard
  -> Queue Router
  -> Worker
  -> Artifact Service
  -> Event Publisher
  -> SSE client
  -> Frontend chart card update
```

## 15. API / Schema 草案

```http
GET /jobs/{job_id}
GET /jobs/{job_id}/events
POST /jobs/{job_id}/cancel
POST /jobs/{job_id}/retry
GET /projects/{project_id}/queue-status
GET /projects/{project_id}/usage
```

```ts
type QueueStatus = {
  queues: Array<{
    name: "parse" | "profile" | "llm" | "viz" | "render" | "export";
    queued: number;
    running: number;
    avgWaitSec: number;
  }>;
};

type ResourceEstimate = {
  costLevel: "low" | "medium" | "high";
  estimatedRuntimeSec?: number;
  estimatedMemoryMb?: number;
  estimatedArtifactMb?: number;
  warnings: string[];
};
```

## 16. 数据库表草案

| 表 | 关键字段 |
|---|---|
| `jobs` | `status`、`priority`、`cost_level`、`progress`、`resource_usage_json` |
| `job_events` | `seq`、`event_type`、`payload_json`、`progress` |
| `worker_runs` | `worker_id`、`queue`、`started_at`、`finished_at`、`heartbeat_at` |
| `tool_calls` | `timeout_sec`、`cache_key`、`cache_hit`、`resource_usage_json` |
| `artifacts` | `size_bytes`、`metadata_json` |
| `rate_limit_events` | `scope_type`、`scope_id`、`limit_type`、`created_at` |

### 关键索引

```sql
-- job events cursor query
CREATE INDEX idx_job_events_job_seq ON job_events(job_id, seq);

-- project job list
CREATE INDEX idx_jobs_project_created ON jobs(project_id, created_at DESC);

-- artifact list
CREATE INDEX idx_artifacts_job ON artifacts(job_id);
CREATE INDEX idx_artifacts_project_created ON artifacts(project_id, created_at DESC);

-- tool call list
CREATE INDEX idx_tool_calls_job ON tool_calls(job_id);

-- audit
CREATE INDEX idx_audit_project_created ON audit_logs(project_id, created_at DESC);
```

### 事件与日志保留

MVP：

- `job_events` 永久保存小型 metadata，但限制 `payload_json` 大小。
- Worker debug logs 设置保留期，不把完整大日志写入 PostgreSQL 大字段。
- 大型日志、渲染诊断和失败文件摘要进入对象存储或日志系统，只在 DB 保存引用。

V1：

- `job_events` 支持按组织策略归档。
- `audit_logs` 支持组织级保留期、导出和合规检索。

## 17. 前端交互草案

- Job 创建后立即显示任务卡片。
- SSE 断线自动重连，并用 cursor 补齐事件。
- 图表卡片按 `artifact.ready` 单独渲染。
- Queue status 显示“排队中/运行中/预计等待”。
- 超限任务显示可操作建议：减少数据、关闭高成本工具、使用采样。
- Cache hit 在 ToolCall 详情显示。

## 18. 高并发、安全、扩展性考虑

### 高并发

- Worker 按队列水平扩容。
- render-worker 单独限流。
- LLM worker 按 provider/key 限速。
- Artifact 大文件不经过 API 转发。

### 安全

- Worker 临时目录隔离。
- 任务执行超时强制终止。
- Artifact HTML 仍通过 sandboxed iframe 展示。
- JobEvent payload 不包含 Secret 或大数据。

### 扩展性

- V1 引入 WebSocket 协作。
- V1/V2 可迁移 Temporal。
- V2 支持 Kubernetes Jobs / Ray / GPU worker。
- V2 支持组织级队列配额和计费。

## 19. 本阶段产出的目标文件

```text
docs/08_JOB_QUEUE_AND_CONCURRENCY.md
persistent/DESIGN_PROGRESS.md
persistent/TASK_BOARD.md
persistent/ARCHITECTURE_DECISIONS.md
persistent/OPEN_QUESTIONS.md
persistent/CHANGELOG.md
```

## 20. 下一阶段任务

Phase 9：Artifact、Recipe 与报告系统。

需要定义：

MVP：

- Plotly JSON / HTML / PNG preview。
- MatterViz HTML / metadata。
- Metrics JSON、table JSON/CSV、quality issues JSON。
- Report Markdown / HTML。
- Recipe JSON。

V1：

- SVG / PDF high-resolution export。
- stable MatterViz snapshot。
- 分享、版本对比和高级导出。
## Phase 4 Addendum: production persistence hardening

- Phase 4 keeps the Phase 2/3 local worker path, but adds a production-oriented
  persistence baseline: Alembic entrypoint, SQLAlchemy metadata constraints,
  repository transaction boundaries, and idempotent write semantics.
- Repository session management is centralized through `RepositorySession`,
  `UnitOfWork`, and `RepositoryFactory`. Business code should use these
  transaction boundaries instead of creating ad hoc sessions.
- Job status validation is centralized. The local synchronous worker may move
  `created -> running`; queued production workers should prefer
  `created -> queued -> running`.
- ToolCall status validation is centralized with
  `planned -> running -> completed/failed/skipped`. Retry can reuse a stable
  `(job_id, step_id)` or `(job_id, idempotency_key)` record without generating
  unbounded duplicate rows.
- `job_events.seq` is the SSE resume cursor. SQLite tests guard allocation with
  an in-process lock; PostgreSQL runtime should use transactional locking or an
  equivalent allocation strategy before multi-worker deployment.
