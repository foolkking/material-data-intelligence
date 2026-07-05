# Phase 3A / Phase 9C：前端组件规格

## 1. 目标

本文定义 Phase 9C 之后的前端组件基线。组件树必须匹配新的 AI 分析助手式工作台：

```text
顶部 Global Context Bar
左侧 Data Context Viewer
主体 Main Workspace Tabs
  - Agent 过程
  - 对话与 Plan
  - 结果与导出
```

旧 `AgentPanel`、`VisualizationCanvas`、`BottomPanel` 作为历史概念保留，不再是新实现的顶层布局边界。

## 2. 组件原则

- 顶部只放全局上下文、数据集/模型配置入口和系统设置入口。
- 左侧只做数据上下文查看，不承载结果查看和 Agent 执行过程。
- 主体内同一时刻只渲染一个 Tab。
- 结果、报告、3D 材料图、metrics、Artifact、Recipe、导出都归入 `ResultsExportTab`。
- Developer 信息默认隐藏，放入 `DeveloperAuditDrawer` 或开发者模式折叠区。
- 组件不得创建绕过 `/planner/jobs`、PlanValidator、QueueWorkerRuntime 或 Tool Registry 的执行入口。

## 3. 核心组件树

```text
AIPlannerWorkspace
├── GlobalContextBar
│   ├── CurrentDatasetButton
│   ├── ModelStatusButton
│   ├── JobStatusBadge
│   └── GlobalSettingsMenu
│       ├── LanguageToggle
│       ├── ThemeToggle
│       ├── UserSettingsEntry
│       ├── HelpEntry
│       └── DeveloperModeToggle
├── DatasetCommandDialog
│   ├── DatasetList
│   ├── UploadDatasetAction
│   ├── DemoDatasetAction
│   ├── DatasetDetailSummary
│   └── ProfilePreview
├── ModelProviderDialog
│   ├── ProviderModeSelector
│   ├── ProviderPresetSelector
│   ├── ProviderConfigForm
│   ├── SecretSelector
│   ├── SecretCreateForm
│   └── ProviderTestResult
├── WorkspaceBody
│   ├── ResizableDataContextShell
│   │   ├── DataContextCollapseButton
│   │   ├── DataContextResizeHandle
│   │   └── DataContextViewer
│   │       ├── TableDatasetViewer
│   │       ├── StructureDatasetViewer
│   │       ├── CompositionDatasetViewer
│   │       ├── ArchiveDatasetViewer
│   │       └── UnsupportedDatasetNotice
│   └── MainWorkspaceTabs
│       ├── AgentProcessTab
│       │   ├── AgentEventTimeline
│       │   ├── EventPayloadDisclosure
│       │   └── ProvenanceStatusStrip
│       ├── ConversationPlanTab
│       │   ├── PromptComposer
│       │   ├── ConversationChunkList
│       │   │   ├── UserRequestChunk
│       │   │   ├── SystemResponseChunk
│       │   │   ├── PlanPreviewChunk
│       │   │   ├── ValidationResultChunk
│       │   │   └── RunStatusChunk
│       │   └── PlanPreviewPanel
│       └── ResultsExportTab
│           ├── SelectedResultContextHeader
│           ├── MaterialResultRenderer
│           ├── MetricsResultRenderer
│           ├── TableSummaryRenderer
│           ├── ArtifactGallery
│           ├── ReportRecipeRenderer
│           ├── ExportControls
│           └── EmptyResultState
├── DeveloperAuditDrawer
│   ├── RawAnalysisPlanView
│   ├── RawJobEventsView
│   ├── RawToolCallsView
│   ├── RawArtifactsView
│   └── ApiResponseView
└── SharedOverlays
    ├── ErrorExplainer
    ├── ArtifactPreviewModal
    └── FullscreenResultModal
```

## 4. 顶部组件职责

| 组件 | 职责 | 主要数据 |
|---|---|---|
| `GlobalContextBar` | 显示当前数据集、模型状态、任务状态和系统设置入口 | dataset, profile, provider, job |
| `CurrentDatasetButton` | 打开数据集弹窗，展示当前 dataset 简要状态 | datasetId, profileStatus |
| `ModelStatusButton` | 打开模型配置弹窗，展示 Mock/real provider 状态 | providerMode, model, status |
| `GlobalSettingsMenu` | 语言、主题、用户、帮助、开发者模式 | ui preferences |
| `DatasetCommandDialog` | 数据集选择、上传、demo 数据、profile 摘要 | datasets, profiles |
| `ModelProviderDialog` | provider 选择、Secret 选择/保存、连接测试 | providers, secrets |

## 5. 左侧组件职责

`DataContextViewer` 是 format-adaptive viewer。

| 子组件 | 数据类型 | 展示内容 |
|---|---|---|
| `TableDatasetViewer` | CSV/table | 行数、字段数、数值列、类别列、字段角色、表格预览 |
| `StructureDatasetViewer` | CIF/POSCAR/Structure JSON | formula、元素、原子数、结构摘要、解析 warning |
| `CompositionDatasetViewer` | composition/formula | 组成字段、元素分布、化学体系 |
| `ArchiveDatasetViewer` | ZIP/archive | 文件树、解析状态、normalized objects |
| `UnsupportedDatasetNotice` | unsupported/partial | 原因、可用对象、推荐下一步 |

左侧 shell 必须提供：

- `leftPanelWidth`
- `leftPanelCollapsed`
- drag resize
- collapse/expand
- responsive drawer fallback

## 6. 主体组件职责

### AgentProcessTab

展示 JobEvent 和执行 provenance。

| 子组件 | 职责 |
|---|---|
| `AgentEventTimeline` | 渲染 `plan.generated`、`plan.persisted`、`plan.loaded`、`data.loaded`、`tool.completed` 等事件 |
| `EventPayloadDisclosure` | 展开安全 payload，不展示 Secret 或 raw prompt/completion |
| `ProvenanceStatusStrip` | 显示 persisted plan、Tool Registry + Adapter、no fallback 等状态 |

### ConversationPlanTab

承载自然语言对话和 Plan Preview。

| 子组件 | 职责 |
|---|---|
| `PromptComposer` | 用户输入中文/英文分析需求，展示当前 dataset/provider 状态 |
| `ConversationChunkList` | 统一渲染 user/system/plan/validation/run chunks |
| `PlanPreviewPanel` | 普通用户看自然语言步骤；开发者模式看 stepId/toolId/raw JSON |

Chunk 必须可选中，选中后更新结果上下文。

### ResultsExportTab

根据 `selectedChunkId`、`selectedResultArtifactId`、active job 和 artifacts 展示结果。

| 子组件 | 职责 |
|---|---|
| `SelectedResultContextHeader` | 显示当前结果来源 chunk/job/tool/artifact |
| `MaterialResultRenderer` | 展示 3D 材料图或 sandboxed structure viewer |
| `MetricsResultRenderer` | 展示 metrics_json |
| `TableSummaryRenderer` | 展示 table_json / numeric_summary_json |
| `ArtifactGallery` | 按类型分组展示 Artifact |
| `ReportRecipeRenderer` | 展示系统摘要、Recipe、provenance |
| `ExportControls` | 报告导出、artifact 下载 |

## 7. ErrorExplainer

`ErrorExplainer` 可被三个主体 Tab 和两个顶部 Dialog 复用。

```ts
type ErrorExplainerProps = {
  title: string;
  message: string;
  errorType?: string;
  safeDetails?: string;
  suggestions: string[];
  redacted: boolean;
};
```

错误文案必须描述用户下一步，例如重新选择数据集、生成 Profile、检查模型配置、重试任务。不得把 provider raw error、API key、Authorization header 或内部绝对路径显示给普通用户。

## 8. Artifact 渲染策略

| ArtifactType | Component |
|---|---|
| `plotly_json` / `plotly_html` | `ArtifactGallery` + `FullscreenResultModal` |
| `matterviz_html` | `MaterialResultRenderer` sandboxed iframe |
| `metrics_json` | `MetricsResultRenderer` |
| `table_json` / `table_csv` | `TableSummaryRenderer` |
| `quality_issues_json` | `DataContextViewer` 或 `ResultsExportTab` |
| `report_markdown` / `report_html` | `ReportRecipeRenderer` |
| `recipe_json` | `ReportRecipeRenderer` |

大对象不进入前端全局 store，只通过 Artifact URL/API 懒加载。

## 9. 安全边界

- `ModelProviderDialog` 不能把明文 key 写入 localStorage/sessionStorage。
- Secret 保存后必须清空输入框。
- Secret list 只能展示 alias/provider/status/masked preview。
- Provider test 只显示 redacted 结果。
- `DeveloperAuditDrawer` 不展示 Secret、raw completion、内部临时路径。
- 所有执行仍由后端 `/planner/jobs` 创建 persisted AnalysisPlan 和 job；前端组件不能绕过。

## 10. Legacy 组件映射

| Legacy | Phase 9C 替代 |
|---|---|
| `TopBar` | `GlobalContextBar` |
| `DataAssetPanel` | `DataContextViewer` |
| `VisualizationCanvas` | `MainWorkspaceTabs` |
| `AgentPanel` | `ConversationPlanTab` + `AgentProcessTab` |
| `BottomPanel` | `ResultsExportTab` + `DeveloperAuditDrawer` |
| `ArtifactDetailDrawer` | `ResultsExportTab` / `ArtifactPreviewModal` |

后续实现不得重新引入独立右侧 Result Inspector 作为主布局。
