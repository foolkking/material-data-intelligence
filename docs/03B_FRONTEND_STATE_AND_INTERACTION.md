# Phase 3B / Phase 9C：前端状态与交互规格

## 1. 目标

本文定义 Phase 9C AI 分析助手工作台的前端状态边界。新的状态模型服务于：

- 顶部全局数据集/模型/任务状态。
- 左侧可拉伸、可收起的数据上下文查看器。
- 主体三个互斥 Tab：`Agent 过程`、`对话与 Plan`、`结果与导出`。
- chunk selection 驱动结果展示。
- SSE JobEvent 驱动 Agent 过程和 Plan/Result 状态。

## 2. 状态原则

- 服务端事实源优先：Dataset、Profile、AnalysisPlan、Job、ToolCall、Artifact、Result、Recipe 以 API/DB 为准。
- 前端 store 只保存 UI 选择、展开状态、布局状态和事件投影。
- 主体同一时刻只渲染一个 Tab；切换 Tab 不会停止 SSE 或丢失状态。
- Chunk 是对话、计划、校验、运行和结果的统一 UI 投影，不是后端执行事实源。
- Secret/API key 不进入 UI store、localStorage、sessionStorage、JobEvent、Artifact、Report 或 Recipe。

## 3. 核心 UI 状态类型

```ts
type MainWorkspaceTab =
  | "agent_process"
  | "conversation_plan"
  | "results_export";

type WorkspaceUiState = {
  activeProjectId: string;
  activeDatasetId?: string;
  activeProfileId?: string;
  activeJobId?: string;
  activePlanId?: string;
  activeMainTab: MainWorkspaceTab;
  leftPanelWidth: number;
  leftPanelCollapsed: boolean;
  selectedChunkId?: string;
  selectedResultArtifactId?: string;
  selectedToolCallId?: string;
  datasetDialogOpen: boolean;
  modelDialogOpen: boolean;
  developerMode: boolean;
  fullscreen:
    | { kind: "artifact"; artifactId: string }
    | { kind: "material_viewer"; artifactId: string }
    | null;
};
```

`activeMainTab` 是主体渲染开关。它只能是三个值之一；不得出现独立 right panel tab 或 bottom panel tab 作为主布局状态。

## 4. Conversation Chunk View

```ts
type ConversationChunkKind =
  | "user_request"
  | "system_response"
  | "plan_preview"
  | "validation_result"
  | "run_status"
  | "result_reference";

type ConversationChunkView = {
  id: string;
  kind: ConversationChunkKind;
  title: string;
  summary: string;
  createdAt: string;
  status: "idle" | "running" | "success" | "warning" | "error";
  relatedJobId?: string;
  relatedPlanId?: string;
  relatedStepId?: string;
  relatedToolCallId?: string;
  relatedArtifactIds: string[];
  userVisiblePayload: Record<string, unknown>;
  developerPayload?: Record<string, unknown>;
};
```

用户点击 chunk 后：

```text
selectedChunkId = chunk.id
if chunk.relatedArtifactIds has item:
  selectedResultArtifactId = first related artifact
```

如果用户切换到 `results_export`，结果 Tab 按 `selectedChunkId` / `selectedResultArtifactId` 决定展示内容。

## 5. Data Context Viewer State

```ts
type DataContextViewerState = {
  datasetId?: string;
  profileId?: string;
  status: "empty" | "loading" | "profiling" | "ready" | "partial_error" | "unsupported";
  detectedKind?: "table" | "structure" | "composition" | "archive" | "mixed" | "unsupported";
  summary: {
    rowCount?: number;
    columnCount?: number;
    numericColumns?: string[];
    categoricalColumns?: string[];
    formulaColumns?: string[];
    structureCount?: number;
    formulaCount?: number;
    elementCount?: number;
    archiveFileCount?: number;
  };
  qualityIssues: Array<{
    severity: "info" | "warning" | "error";
    message: string;
    ref?: string;
  }>;
};
```

左侧 resize/collapse 只影响布局，不影响 dataset/profile 事实源。

## 6. Selected Result Context

```ts
type SelectedResultContext = {
  chunkId?: string;
  jobId?: string;
  planId?: string;
  planHash?: string;
  stepId?: string;
  toolCallId?: string;
  artifactId?: string;
  resultKind?:
    | "report"
    | "material_3d"
    | "metrics"
    | "table_summary"
    | "artifact_gallery"
    | "recipe"
    | "export";
};
```

`ResultsExportTab` 的空状态必须基于该上下文判断：

- 无 chunk：请选择一个分析步骤或结果 chunk。
- 有 chunk 但无 artifact：当前步骤尚未生成结果产物。
- 有 artifact 但无法预览：当前结果类型暂不支持预览，可下载原始 Artifact。

## 7. Query 与 Store 边界

| 数据 | 来源 | 前端管理方式 |
|---|---|---|
| datasets/profile | REST | TanStack Query |
| provider catalog/status | REST | TanStack Query |
| secrets metadata | REST | TanStack Query，不缓存 plaintext |
| planner preview/jobs | REST | Mutation + Query invalidation |
| job_events | SSE + REST fallback | Store append + cursor checkpoint |
| tool_calls | REST | Query invalidation on `tool.completed` |
| artifacts/results | REST | Query invalidation on `artifact.ready` / `job.completed` |
| active tab/chunk/layout | UI | Zustand/Jotai 或 React state |

## 8. JobEvent 到 UI 的映射

| Event | AgentProcessTab | ConversationPlanTab | ResultsExportTab |
|---|---|---|---|
| `plan.generated` | append event | add/update PlanPreviewChunk | no-op |
| `plan.persisted` | append event | attach planId/planHash | provenance available |
| `job.queued` | append event | add RunStatusChunk | no-op |
| `plan.loaded` | highlight persisted plan load | mark run chunk running | provenance available |
| `data.loaded` | append event | dataset-bound status | no-op |
| `tool.started` | append event | mark related chunk running | selected result loading |
| `artifact.ready` | append event | attach artifact to chunk | invalidate artifacts |
| `tool.completed` | append event | mark related chunk success | enable result render |
| `job.completed` | append event | mark run chunk success | show summary/export |
| `job.failed` | append error | add ErrorExplainer chunk | show safe failure state |

事件 payload 不包含大图表数据、Secret、API key、raw prompt 或 raw completion。前端只保存 ID 引用和安全摘要。

## 9. 主体 Tab 切换规则

```text
User clicks Agent 过程
  -> activeMainTab = "agent_process"
  -> render AgentProcessTab only

User clicks 对话与 Plan
  -> activeMainTab = "conversation_plan"
  -> render ConversationPlanTab only

User clicks 结果与导出
  -> activeMainTab = "results_export"
  -> render ResultsExportTab only
  -> derive SelectedResultContext from selectedChunkId / selectedResultArtifactId
```

不得在主体旁边同时固定显示结果 Inspector。结果只能通过 `results_export` Tab 或 fullscreen modal 查看。

## 10. 关键交互

### 数据集选择

```text
Top dataset button
  -> datasetDialogOpen = true
  -> user selects/uploads/demo dataset
  -> activeDatasetId set
  -> DataContextViewer loads profile
```

### 模型配置

```text
Top model button
  -> modelDialogOpen = true
  -> user selects Mock Planner or OpenAI-compatible
  -> optional secret save/test via backend
  -> model status updates
```

明文 API key 只能停留在受控输入框中；保存/测试后清空，不进 store persistence。

### 自然语言分析

```text
Prompt submit
  -> add UserRequestChunk
  -> POST planner preview/validate/jobs
  -> add PlanPreviewChunk / ValidationChunk / RunChunk
  -> activeJobId set on success
  -> SSE subscribe to job events
```

### 结果查看

```text
User selects chunk
  -> selectedChunkId set
  -> optional selectedResultArtifactId set
  -> user switches to ResultsExportTab
  -> ResultsExportTab renders selected context
```

## 11. 错误态与恢复

```ts
type WorkspaceErrorType =
  | "network_error"
  | "api_unavailable"
  | "dataset_not_found"
  | "profile_not_found"
  | "provider_not_configured"
  | "provider_auth_failed"
  | "provider_timeout"
  | "plan_validation_failed"
  | "queue_enqueue_failed"
  | "worker_failed"
  | "artifact_unavailable"
  | "unknown_error";
```

| 错误位置 | UI 落点 |
|---|---|
| dataset/profile | 顶部数据集弹窗 + 左侧 DataContextViewer |
| provider/secret | 顶部模型弹窗 |
| plan validation | ConversationPlanTab 的 ValidationChunk / ErrorExplainer |
| worker/tool | AgentProcessTab + ResultsExportTab |
| artifact preview/download | ResultsExportTab |

Validation failure 必须明确显示：

- No AnalysisPlan was saved.
- No Job was created.
- Nothing was enqueued.

## 12. 性能与安全

- 左侧表格预览分页/虚拟滚动。
- 结果 Artifact 懒加载，避免把大型 Plotly JSON 或结构坐标放入全局 store。
- SSE 使用 cursor/seq 去重和补拉。
- HTML Artifact 使用 sandboxed iframe。
- Developer payload 默认不渲染。
- 前端不缓存 Secret、临时明文 key、内部绝对路径。

## 13. Legacy 状态字段

以下字段来自旧三栏/底部面板设计，后续不应作为 Phase 9C 主布局状态继续扩展：

- `rightCollapsed`
- `bottomOpen`
- `bottomPanelTab`
- `activeTab: WorkspaceTab` 用于 overview/composition/structure/ml/artifacts/report 的全局画布 Tab

如代码中仍有这些字段，应在实现阶段迁移到 `activeMainTab`、`selectedChunkId` 和 `ResultsExportTab` 内部局部状态。
