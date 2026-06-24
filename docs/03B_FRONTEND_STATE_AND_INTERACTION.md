# Phase 3B：前端状态与交互规格

## 1. 本阶段目标

定义前端工作台的状态切片、事件更新规则、Tab/卡片/Artifact 交互状态机和错误恢复策略，确保后续 Next.js + React + TanStack Query + Zustand/Jotai 实现时有稳定边界。

## 2. 本阶段解决的问题

- 明确哪些数据由服务端事实源管理，哪些是前端临时 UI 状态。
- 将 JobEvent 映射到 Timeline、Chart Card、Artifact List 和 Warnings。
- 为 SSE 断线重连、Artifact 懒加载、图表全屏、工具重试预留统一状态。
- 避免前端把 Agent Plan、ToolCall、Artifact 各自维护成互相冲突的状态。

## 3. 设计原则

- 服务端事实源优先：Job、ToolCall、Artifact、Recipe、Profile 以 API/DB 为准。
- 前端 Store 只保存 UI 选择、局部缓存和事件投影。
- JobEvent 是增量 UI 更新的主通道，但完整数据仍通过 Query 重新拉取。
- 所有状态转换可重复应用，支持 SSE 断线后按 cursor 补齐。
- Error 和 Warning 是一等状态，不只写入日志。

## 4. 核心状态类型

```ts
type ChartCardState =
  | "planned"
  | "queued"
  | "running"
  | "artifact_ready"
  | "rendered"
  | "warning"
  | "failed";

type WorkspaceTab =
  | "overview"
  | "composition"
  | "structure"
  | "trajectory"
  | "phonon"
  | "ml"
  | "artifacts"
  | "report";

type WorkspaceStore = {
  activeProjectId: string;
  activeDatasetId?: string;
  activeJobId?: string;
  activeTab: WorkspaceTab;
  selectedArtifactId?: string;
  selectedToolCallId?: string;
  selectedStructureId?: string;
  bottomPanelTab: "logs" | "code" | "artifacts" | "recipe" | "warnings";
  chartCards: Record<string, ChartCardView>;
  timelineEvents: JobEvent[];
  warningIndex: Record<string, WorkspaceWarning>;
  artifactLoadStates: Record<string, ArtifactLoadState>;
  fullscreen:
    | { kind: "chart"; artifactId: string }
    | { kind: "viewer"; artifactId: string }
    | null;
};

type ChartCardView = {
  cardId: string;
  stepId?: string;
  toolCallId?: string;
  toolId?: string;
  title: string;
  displayTarget: WorkspaceTab;
  state: ChartCardState;
  artifactIds: string[];
  warnings: string[];
  errorMessage?: string;
  updatedAt: string;
};

type ArtifactLoadState =
  | { status: "idle" }
  | { status: "loading" }
  | { status: "loaded"; loadedAt: string }
  | { status: "failed"; message: string; retryable: boolean }
  | { status: "expired_url" }
  | { status: "permission_denied" };
```

`DisplayTarget`、`ArtifactType`、`JobEvent` 的实现基线见 `docs/13_SHARED_SCHEMA_SPEC.md`。

## 5. Query 与 Store 边界

| 数据 | 来源 | 前端管理方式 |
|---|---|---|
| project/dataset/profile | REST | TanStack Query |
| files/quality issues | REST | TanStack Query + 左侧筛选 UI |
| analysis plan | REST | TanStack Query，summary 投影到 AgentPanel |
| job_events | SSE + REST cursor | Store append + cursor checkpoint |
| tool_calls | REST | Query invalidation on event |
| artifacts | REST | Query invalidation on `artifact.ready` |
| chart card state | JobEvent 投影 | Zustand/Jotai |
| selected tab/modal/fullscreen | 用户交互 | Zustand/Jotai |

## 6. JobEvent 到 UI 的映射

| Event | Timeline | ChartCard | Artifact/Panel |
|---|---|---|---|
| `job.created` | append | no-op | show task card |
| `plan.generated` | append | create planned cards | show PlanSummary |
| `tool.started` | append | state -> `running` | select toolCall optional |
| `tool.warning` | append warning | state -> `warning` | WarningsTab add item |
| `artifact.ready` | append | add artifactId, state -> `artifact_ready` | invalidate artifacts query |
| `report.ready` | append | no-op | enable Report/Artifacts tab |
| `job.completed` | append | unresolved cards stay rendered/warning | show completed state |
| `job.failed` | append error | affected cards -> `failed` | show retry actions |

事件 payload 不包含大图表数据和 Secret。前端只把 `artifactId`、`toolCallId`、`stepId` 等引用存进 Store。

## 7. 关键交互

### 自然语言分析

```text
ChatInput submit
  -> POST /analysis-requests
  -> activeJobId set
  -> SSE subscribe
  -> PlanSummary appears on plan.generated
  -> user Run / Regenerate / Cancel
```

### 图表详情

```text
ChartCard click
  -> selectedArtifactId set
  -> ArtifactDetailDrawer open
  -> ArtifactLoader fetches signed URL
  -> user can fullscreen / download / inspect params
```

### 3D Viewer 全屏

```text
Structure card fullscreen
  -> fullscreen = { kind: "viewer", artifactId }
  -> ViewerFullscreenModal loads matterviz_html
  -> controls update iframe config through allowed message protocol
```

### 工具重试

```text
RetryToolCallDialog confirm
  -> POST /tool-calls/{tool_call_id}/retry
  -> new toolCallId or retry attempt created
  -> affected ChartCard state -> queued
```

## 8. 空状态、错误态与恢复

```ts
type WorkspaceEmptyState =
  | "no_project"
  | "no_dataset"
  | "no_files"
  | "profile_pending"
  | "profile_failed"
  | "plan_required";

type RetryAction =
  | "retry_upload"
  | "retry_parse"
  | "regenerate_plan"
  | "retry_tool_call"
  | "refresh_artifact_url"
  | "contact_project_owner";
```

UI 必须把错误落在最接近用户操作的位置：

- 上传/解析错误在 Data Asset Panel。
- Plan 错误在 Agent Panel。
- Tool 错误在 Chart Card 和 Timeline。
- Artifact URL/权限错误在 Artifact Loader。
- 系统级错误在 Bottom Logs/Warn 面板。

## 9. Artifact 加载策略

- Tab 首次激活后加载该 Tab 的 Artifact metadata。
- 卡片进入 viewport 后加载 preview。
- 全屏或详情打开后加载完整 Artifact。
- URL 过期时只刷新 URL，不重跑工具。
- 下载操作必须走 `/artifacts/{id}/download-url`，不暴露对象存储 key。

## 10. 性能策略

- Timeline 虚拟列表，默认只渲染最近事件。
- Artifact table preview 使用虚拟滚动和分页。
- Plotly 大图优先使用 `plotly_html` iframe 或后端预聚合 `plotly_json`。
- Store 中不保存大型 Plotly JSON、表格全量数据或结构坐标数组。
- 3D Viewer 通过 LOD metadata 决定默认 controls，不在前端猜测。

## 11. 高并发、安全、扩展性考虑

- SSE 使用 `cursor` 断线重连，重复事件按 `event.id` 去重。
- 前端永不缓存 Secret、临时明文 key、内部绝对路径。
- 多用户协作进入 V1 WebSocket 后，仍以 PostgreSQL JobEvent 为事实源。
- Guided/Expert 模式进入 V1 后可复用 `PlanSummary`、`ToolCallList` 和 `RecipeTab`。

## 12. 本阶段产出的目标文件

```text
docs/03B_FRONTEND_STATE_AND_INTERACTION.md
```

## 13. 下一阶段任务

代码实现阶段应先建立 `WorkspaceStore`、SSE event reducer、Artifact Loader 和 Chart Card 状态机，再扩展各 Tab 的具体可视化组件。
