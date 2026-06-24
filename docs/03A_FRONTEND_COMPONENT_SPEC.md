# Phase 3A：前端组件规格

## 1. 本阶段目标

把 Phase 3 的工作台布局进一步拆成可实现的 React 组件树、组件职责、输入输出和关键交互。本文面向后续 `apps/web` 实现，和 `docs/03_FRONTEND_WORKSPACE_DESIGN.md`、`docs/03B_FRONTEND_STATE_AND_INTERACTION.md` 配套使用。

## 2. 本阶段解决的问题

- 避免前端只停留在三栏布局说明，缺少组件边界。
- 明确 Data Asset、Visualization、Agent、Bottom Panel 四个区域之间的数据流。
- 明确图表、3D Viewer、Artifact、日志和 Recipe 的加载入口。
- 为大图表懒加载、错误重试、全屏查看和 Artifact 下载预留组件位置。

## 3. 设计原则

- 工作台组件优先承载任务状态，不把自然语言聊天作为唯一主界面。
- 卡片只用于单个图表、Artifact、质量问题、工具调用等重复实体。
- 大图、3D Viewer、报告、Recipe 通过 Artifact Loader 懒加载。
- 所有危险或失败状态必须有明确可见位置：Timeline、Warnings、Chart Card、Bottom Panel。
- 组件不直接拼接对象存储路径，只使用 API 返回的 Artifact URL 或签名 URL。

## 4. 核心组件树

```text
WorkspacePage
├── TopBar
│   ├── ProjectSwitcher
│   ├── DatasetSelector
│   ├── RunStatusBadge
│   ├── BudgetMeter
│   └── ExportMenu
├── WorkspaceLayout
│   ├── DataAssetPanel
│   │   ├── FileTree
│   │   ├── UploadDropzone
│   │   ├── ProfileSummary
│   │   ├── FieldMappingEditor
│   │   ├── QualityIssueList
│   │   └── RecommendedTaskList
│   ├── VisualizationCanvas
│   │   ├── WorkspaceTabs
│   │   ├── OverviewDashboard
│   │   ├── CompositionTab
│   │   ├── StructureTab
│   │   ├── MLEvaluationTab
│   │   ├── TrajectoryTabPlaceholder
│   │   ├── PhononTabPlaceholder
│   │   └── ArtifactDetailDrawer
│   ├── AgentPanel
│   │   ├── ChatInput
│   │   ├── PlanSummary
│   │   ├── ToolCallList
│   │   ├── Timeline
│   │   ├── ExplanationPanel
│   │   └── NextStepSuggestions
│   └── BottomPanel
│       ├── LogsTab
│       ├── CodeTab
│       ├── ArtifactsTab
│       ├── RecipeTab
│       └── WarningsTab
└── GlobalOverlays
    ├── ChartFullscreenModal
    ├── ViewerFullscreenModal
    ├── ArtifactPreviewModal
    └── RetryToolCallDialog
```

## 5. 主要组件职责

| 组件 | 职责 | 主要数据 |
|---|---|---|
| `WorkspacePage` | 读取 route params，装配 workspace providers | projectId、datasetId |
| `TopBar` | 项目/数据集切换、运行状态、预算、导出入口 | project、dataset、activeJob |
| `DataAssetPanel` | 数据文件、Data Profile、字段映射和质量问题 | files、profile、fieldMappings |
| `VisualizationCanvas` | Tab 化图表与 3D Viewer 展示 | chartCards、artifacts、activeTab |
| `AgentPanel` | 自然语言输入、计划摘要、工具调用、Timeline | messages、analysisPlan、jobEvents |
| `BottomPanel` | 日志、代码、Artifact、Recipe、Warnings | logs、codeSnippets、artifacts、recipe |

## 6. 图表卡片规格

```ts
type ChartCardProps = {
  cardId: string;
  title: string;
  displayTarget: DisplayTarget;
  state: ChartCardState;
  toolId?: string;
  artifactIds: string[];
  warningCount: number;
  errorMessage?: string;
  onOpenDetail: (artifactId: string) => void;
  onFullscreen: (artifactId: string) => void;
  onRetry?: (toolCallId: string) => void;
};
```

卡片区域：

- Header：标题、工具 ID、状态图标、更多菜单。
- Body：skeleton、Plotly renderer、iframe、image preview 或 table preview。
- Footer：输入摘要、关键参数、导出按钮、重试按钮。
- Warning Strip：展示降采样、LOD、解析失败、字段缺失等提示。

## 7. Artifact Loader

`ArtifactLoader` 根据 `ArtifactType` 选择加载策略：

| ArtifactType | Loader |
|---|---|
| `plotly_json` | React Plotly renderer，必要时 Web Worker 预处理 |
| `plotly_html` | sandboxed iframe |
| `preview_png` | image preview |
| `matterviz_html` | sandboxed iframe |
| `metrics_json` | MetricsGrid |
| `table_json` | VirtualizedTable preview |
| `table_csv` | 下载入口 + 预览摘要 |
| `quality_issues_json` | QualityIssueList |
| `report_html` | sandboxed report viewer |
| `recipe_json` | RecipeViewer |

Artifact Loader 必须处理：

- `loading`
- `loaded`
- `failed`
- `expired_url`
- `permission_denied`
- `too_large_preview`

## 8. 3D Viewer 组件

```text
StructureTab
├── RepresentativeStructureList
├── StructureViewerPanel
│   ├── MatterVizIframeViewer
│   ├── Structure3DPlotlyFallback
│   └── ViewerLoadingOverlay
├── StructureMetadataPanel
└── ViewerControls
    ├── BondsToggle
    ├── CellToggle
    ├── SiteLabelToggle
    ├── LODBadge
    └── FullscreenButton
```

MVP 中 `MatterVizIframeViewer` 以 `viewer.html` 为 canonical。`snapshot.png` 只作为可选预览，不作为首版必需依赖。

## 9. 空状态、错误态与重试态

| 场景 | 组件行为 |
|---|---|
| 无数据 | 中央显示上传入口，右侧 Agent 输入禁用 |
| 正在解析 | 左侧和中央显示 skeleton，Timeline 显示解析事件 |
| 部分解析失败 | 左侧 QualityIssueList 可定位失败文件，成功对象仍可分析 |
| 计划校验失败 | AgentPanel 显示失败步骤、原因和修复建议 |
| 单个工具失败 | 对应 ChartCard 显示 retry，不影响其他 Artifact |
| Artifact URL 过期 | ArtifactLoader 重新请求签名 URL |
| 权限不足 | 显示项目权限错误，不暴露存储路径 |

## 10. 数据流 / 控制流

```text
Route projectId/datasetId
  -> TanStack Query loads workspace metadata
  -> SSE subscribes active job events
  -> WorkspaceStore updates timeline and card states
  -> Artifact events invalidate artifact queries
  -> ArtifactLoader fetches signed preview/download URL
```

## 11. 高并发、安全、扩展性考虑

- 图表和 3D Viewer 进入视口或 Tab 激活后再加载。
- `table_json` 只加载 preview window，大表走分页或虚拟列表。
- HTML Artifact 一律 sandboxed iframe + CSP，不允许访问父窗口。
- Plotly 大图优先加载后端预聚合 Artifact，不在前端直接渲染百万点。
- `TrajectoryTab` 和 `PhononTab` 在 MVP 可显示能力占位和已识别数据摘要，完整执行工具进入 V1。

## 12. 本阶段产出的目标文件

```text
docs/03A_FRONTEND_COMPONENT_SPEC.md
```

## 13. 下一阶段任务

结合 `docs/03B_FRONTEND_STATE_AND_INTERACTION.md` 实现前端状态切片、事件流 reducer、Artifact Loader 和 Chart Card 状态机。
