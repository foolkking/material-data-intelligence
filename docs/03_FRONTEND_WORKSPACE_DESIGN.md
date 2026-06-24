# Phase 3：前端工作台设计

## 1. 本阶段目标

定义材料数据智能分析与可视化平台的前端工作台，包括整体页面布局、左侧数据资产区、中央可视化画布、右侧 Agent 面板、底部日志/代码/Artifact/Recipe/Warnings 面板、图表卡片、3D Viewer、任务进度展示和大图表流畅加载策略。

本阶段目标是把 Phase 1 的产品流程和 Phase 2 的系统架构转成可实现的前端信息架构与组件边界。

组件级实现规格见 `docs/03A_FRONTEND_COMPONENT_SPEC.md`，状态与交互状态机见 `docs/03B_FRONTEND_STATE_AND_INTERACTION.md`。

## 2. 本阶段解决的问题

### 前端产品形态

平台前端不是普通聊天框，而是材料数据分析工作台。自然语言输入只是右侧 Agent 面板的一部分，核心界面必须同时承载：

- 数据资产和 Data Profile。
- 字段映射和数据质量警告。
- Plotly 图表与 MatterViz / Plotly 3D 模型。
- Agent Plan、Tool Calls、Timeline、解释和下一步建议。
- 日志、复现代码、Artifact、Recipe 和 Warning。

### Phase 3 前端决策

| 问题 | 决策 |
|---|---|
| MatterViz 如何嵌入 | MVP 优先通过 sandboxed artifact iframe 展示 MatterViz / heavy Plotly HTML；V1 再评估直接 React 集成。 |
| Dashboard 是否拖拽布局 | MVP 使用固定响应式布局；拖拽和自定义布局推迟到 V1。 |
| Agent JSON Plan 如何展示 | 默认显示摘要和风险提示，完整 JSON / ToolCall 细节可展开。 |
| Code 面板显示什么 | 显示脱敏、可复现代码片段和 Recipe，不显示 Worker 内部路径、Secret 或未审查脚本。 |
| 重图如何避免卡页面 | 图表卡片懒加载，重图 iframe 隔离，Artifact URL 拉取大数据。 |

## 3. 设计原则

- 三栏优先：数据、可视化、Agent 并列，减少上下文切换。
- 渐进展示：Data Profile、图表、3D 模型和报告分阶段出现。
- 重组件隔离：大型 Plotly HTML、MatterViz viewer、导出预览优先 iframe sandbox。
- 一图一状态：每个图表卡片有独立 loading/error/warning/artifact 状态。
- 过程可审计：右侧 Timeline 和底部 Logs 同步展示执行过程。
- 可复现优先：每个图表卡片都能看到工具 ID、参数、输入来源和 Recipe 片段。
- 安全显示：前端不展示 Secret、内部临时路径、原始隐藏思维链或未脱敏执行上下文。

## 4. 核心模块

| 模块 | 职责 |
|---|---|
| Workspace Shell | 顶部导航、项目上下文、全局运行状态、布局容器 |
| Data Asset Panel | 文件树、Data Profile、字段映射、异常列表、推荐任务 |
| Visualization Canvas | Dashboard 和多 Tab 图表/3D 模型区域 |
| Chart Card | 单个图表的状态、解释、参数、导出和重跑入口 |
| Structure Viewer | MatterViz / Plotly 3D 结构查看器、代表结构切换 |
| Agent Panel | Chat、Plan、Tool Calls、Explanation、Next Steps |
| Timeline | JobEvent 和 ToolCall 的结构化过程记录 |
| Bottom Panel | Logs、Code、Artifacts、Recipe、Warnings |
| Event Client | SSE/WebSocket 订阅 JobEvent 并更新前端状态 |
| Artifact Loader | 通过 Artifact URL 懒加载 Plotly、MatterViz、metrics、table、quality issues、report |

## 5. 页面布局

### 5.1 Desktop 布局

```text
┌────────────────────────────────────────────────────────────────────────────┐
│ Top Bar: Project / Dataset / LLM Config / Job Status / Export / Settings  │
├───────────────────┬────────────────────────────────────┬──────────────────┤
│ Left Data Panel    │ Center Visualization Canvas         │ Right Agent Panel│
│ 280-360px          │ flexible                           │ 360-440px        │
│                   │                                    │                  │
│ Dataset Tree       │ Tabs: Overview / Composition        │ Chat             │
│ Data Profile       │       Structure / ML / Artifacts    │ Plan Summary     │
│ Field Mapping      │ Dashboard Cards                     │ Tool Calls       │
│ Quality Issues     │ Chart Grid                          │ Timeline         │
│ Recommended Tasks  │ 3D Viewer                           │ Explanation      │
│                   │                                    │ Next Steps       │
├───────────────────┴────────────────────────────────────┴──────────────────┤
│ Bottom Panel: Logs / Code / Artifacts / Recipe / Warnings                 │
│ collapsible, 220-360px                                                     │
└────────────────────────────────────────────────────────────────────────────┘
```

### 5.2 Responsive 行为

| 屏幕 | 行为 |
|---|---|
| >= 1440px | 三栏 + 底部面板完整显示 |
| 1024-1439px | 左侧可折叠，右侧固定，中央优先 |
| 768-1023px | 左/右面板变 Drawer，中央单列 |
| < 768px | MVP 只保证查看结果和日志，不作为主要分析工作流 |

## 6. 左侧：数据资产区

### 信息结构

```text
Data Assets
├── Dataset Summary
├── Files
│   ├── structures.zip
│   ├── predictions.csv
│   └── failed files
├── Data Profile
│   ├── object types
│   ├── elements
│   ├── space groups
│   └── table schema
├── Field Mapping
│   ├── formula
│   ├── target
│   ├── prediction
│   └── uncertainty
├── Quality Issues
└── Recommended Tasks
```

### 组件需求

| 组件 | 行为 |
|---|---|
| FileTree | 显示文件、解析状态、失败原因、格式标签 |
| ProfileSummary | 显示结构数量、元素数、空间群数、表格行数、字段角色 |
| FieldMappingEditor | 用户确认/修正 formula、target、prediction、uncertainty、structure_id |
| QualityIssueList | 按 warning/error 分组，支持点击定位相关文件或结构 |
| RecommendedTaskList | 显示系统可运行分析任务，点击可填入 Agent prompt |

### 状态

- `empty`：提示上传数据。
- `uploading`：显示文件级进度。
- `profiling`：显示 skeleton。
- `ready`：展示 profile 和推荐任务。
- `partial_error`：可继续分析成功解析的数据，但保留失败列表。

## 7. 中央：可视化画布

### Tabs

| Tab | MVP 内容 | V1/V2 扩展 |
|---|---|---|
| Overview | 数据摘要卡、质量卡、推荐分析、关键图表预览 | 可编辑 Dashboard |
| Composition | `ptable_heatmap`、`elements_hist`、`chem_sys_treemap` | composition clustering 2D/3D |
| Structure | 3D Viewer、代表结构列表、coordination histogram | RDF、XRD、spacegroup analysis |
| ML Evaluation | density scatter、error distribution、basic metrics、outlier table | parity plot、uncertainty calibration、error by element/chem system |
| Artifacts | Artifact 列表、预览、下载 | 分享、版本对比 |

### Overview 卡片

| 卡片 | 内容 |
|---|---|
| Dataset Size | 文件数、有效结构数、表格行数 |
| Chemistry | 元素集合、化学体系数量 |
| Structure Quality | 异常短键、解析失败、空间群缺失 |
| ML Metrics | MAE、RMSE、最大误差、缺失列 |
| Job Status | 当前运行任务、队列状态 |

### Chart Card 设计

每个图表卡片包含：

```text
Title
Status Badge
Preview / Interactive Frame
Short Explanation
Data Source
Tool ID
Key Params
Warnings
Actions: Open Detail / Export / Re-run / Save to Report
```

状态机：

```text
planned -> queued -> running -> artifact_ready -> rendered
planned -> queued -> running -> warning -> rendered
planned -> queued -> running -> failed
```

## 8. 右侧：Agent 面板

### 信息架构

```text
Agent Panel
├── Chat Input
├── Plan Summary
├── Tool Calls
├── Timeline
├── Explanation
└── Next Steps
```

### Plan Summary

默认展示：

- 分析目标。
- 将要调用的工具列表。
- 每个工具的目的。
- 预计生成的 Artifact。
- 资源/时间/权限 warning。

完整 JSON Plan 放在“Details”折叠区，不默认展开。

### Tool Calls

每个 ToolCall 显示：

| 字段 | 说明 |
|---|---|
| tool_id | 注册表工具 ID |
| status | queued / running / success / warning / failed |
| input | 输入对象摘要 |
| params | 关键参数 |
| artifact | 输出链接 |
| cache | hit / miss |

### Timeline

Timeline 只展示结构化过程，不展示隐藏思维链：

```text
Data Detection
Data Quality Check
Intent Parsed
Plan Generated
Tool Validated
Tool Running
Artifact Ready
Result Explained
Report Ready
```

## 9. 底部面板

### Tabs

| Tab | 内容 |
|---|---|
| Logs | JobEvent、Worker log 摘要、时间戳 |
| Code | 脱敏复现代码片段、工具调用伪代码、Recipe 片段 |
| Artifacts | Plotly、MatterViz、metrics、table、quality issues、report、recipe 下载 |
| Recipe | 当前分析流程、输入引用、参数、版本 |
| Warnings | 解析失败、数据质量、工具 warning、安全提示 |

### Code 面板原则

展示可复现代码，而不是 Worker 内部脚本：

```python
import pymatviz as pmv

fig = pmv.ptable_heatmap(formulas, log=True)
fig.write_html("ptable_heatmap.html")
```

禁止显示：

- Secret。
- 用户 API Key。
- 内部临时绝对路径。
- 未经过 Tool Registry 的任意代码。

## 10. 3D Viewer 设计

### Viewer 类型

| 类型 | MVP 策略 |
|---|---|
| Plotly `structure_3d` | 图表卡片内可交互展示，支持 HTML/JSON/PNG |
| MatterViz StructureWidget | 通过 sandboxed iframe 加载 viewer artifact |
| TrajectoryWidget | MVP 不提供完整 trajectory 工具；仅当 EXTXYZ/结构集合已解析时，可用结构 viewer 展示首末帧或抽样帧；完整播放器 V1 |

### 控件

- Structure selector。
- Atoms / bonds / cell 开关。
- Label 开关。
- Force / magmom vector 开关。
- Screenshot。
- Reset camera。
- Open full screen。
- Save to report。

### 大结构策略

| 结构规模 | 默认渲染 |
|---|---|
| < 500 atoms | atoms + bonds + cell |
| 500-5000 atoms | atoms + cell，bonds 默认关闭 |
| > 5000 atoms | summary / LOD / sampled view，用户手动展开 |
| trajectory | 默认抽帧，避免一次加载全轨迹 |

## 11. 数据流 / 控制流

### 前端数据流

```text
TanStack Query
  -> projects / datasets / profiles / artifacts metadata

SSE/WebSocket Event Client
  -> job_events
  -> timeline store
  -> chart card state
  -> bottom logs

Artifact Loader
  -> signed artifact URL
  -> iframe / JSON renderer / image preview
```

### 用户控制流

```text
Upload data
  -> Profile ready
  -> User prompt
  -> Plan summary
  -> Run
  -> Timeline updates
  -> Chart cards appear progressively
  -> Report and Recipe ready
```

## 12. API / Schema 草案

正式 API 在 Phase 4 定义。本阶段定义前端需要的视图模型。

```ts
type WorkspaceState = {
  projectId: string;
  activeDatasetId?: string;
  activeJobId?: string;
  activeTab: "overview" | "composition" | "structure" | "ml" | "artifacts";
  panels: {
    leftCollapsed: boolean;
    rightCollapsed: boolean;
    bottomOpen: boolean;
    bottomTab: "logs" | "code" | "artifacts" | "recipe" | "warnings";
  };
};

type ChartCardView = {
  id: string;
  title: string;
  toolId: string;
  status: "planned" | "queued" | "running" | "rendered" | "warning" | "failed";
  artifactId?: string;
  previewUrl?: string;
  explanation?: string;
  dataSourceLabel: string;
  keyParams: Record<string, unknown>;
  warnings: string[];
};

type DataPanelView = {
  datasetId: string;
  files: Array<{ id: string; name: string; status: string; detectedFormat?: string }>;
  profileSummary: Record<string, unknown>;
  fieldMappings: Record<string, string>;
  qualityIssues: Array<{ severity: "info" | "warning" | "error"; message: string; ref?: string }>;
  recommendedTasks: Array<{ id: string; label: string; promptTemplate: string }>;
};
```

## 13. 数据库表草案

本阶段不新增后端表，只明确前端依赖的后端实体：

| 实体 | 前端使用方式 |
|---|---|
| `projects` | 顶部项目上下文 |
| `datasets` | 左侧数据资产根节点 |
| `files` | 文件树和解析状态 |
| `data_profiles` | Profile summary 和推荐任务 |
| `field_mappings` | 字段映射编辑 |
| `jobs` | 当前运行状态 |
| `job_events` | Timeline、logs、progress |
| `tool_calls` | Tool Calls 面板 |
| `artifacts` | 图表卡片和底部 Artifact 面板 |
| `visualization_recipes` | Recipe 面板 |

## 14. 高并发、安全、扩展性考虑

### 流畅展示

- 图表按 Tab 懒加载。
- Chart Card 独立 suspense / error boundary。
- Heavy Plotly HTML 和 MatterViz viewer 用 iframe sandbox 隔离。
- 大数据图表通过 Artifact URL 拉取，不走 SSE。
- 事件流只推状态和小 payload。
- 长列表使用虚拟滚动。

### 安全

- iframe 使用 sandbox，限制脚本能力和跨域访问。
- Artifact URL 必须经过权限校验和短期签名。
- Code 面板只显示脱敏复现代码。
- Timeline 不展示隐藏思维链、Secret 或内部系统提示。
- 上传文件名和用户文本输出必须转义，防止 XSS。

### 扩展性

- V1 支持 Dashboard 拖拽布局。
- V1 支持 Guided / Expert 面板。
- V1 支持 native MatterViz React 集成评估。
- V2 支持协作评论、报告分享、图表版本对比。

## 15. 本阶段产出的目标文件

```text
docs/03_FRONTEND_WORKSPACE_DESIGN.md
persistent/DESIGN_PROGRESS.md
persistent/TASK_BOARD.md
persistent/ARCHITECTURE_DECISIONS.md
persistent/OPEN_QUESTIONS.md
persistent/CHANGELOG.md
```

## 16. 下一阶段任务

Phase 4：后端服务与数据库设计。

需要定义：

- API 设计。
- 数据库实体。
- 项目、数据集、文件、任务、工具调用、Artifact、Recipe、用户配置、Secret、审计日志。
- 数据隔离。
- 权限模型。
