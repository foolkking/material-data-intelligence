# Phase 3 / Phase 9C：前端 AI 分析助手工作台设计

## 1. 当前 Canonical Baseline

Phase 9C 将前端工作台的推荐实现基线更新为 **顶部全局栏 + 左侧数据上下文 + 主体三视图**。旧的“三栏工作台 + 独立右侧 Agent 面板 + 底部结果面板”仅作为历史基线保留，不再作为新的 UI/UX 实现方向。

本轮是文档基线调整，不改变后端 API、AnalysisPlan、QueueWorkerRuntime、Tool Registry 或 Adapter 执行语义。

```text
┌──────────────────────────────────────────────────────────────┐
│ 顶部：当前数据集 + 模型状态 + 数据集/模型配置弹窗 + 系统设置入口 │
├───────────────┬──────────────────────────────────────────────┤
│ 左侧数据上下文 │ 主体工作区                                      │
│ 可拉伸/可收起  │ Tabs: Agent过程 / 对话与Plan / 结果与导出          │
│ 适配多数据格式 │ 同一时刻只显示一个 Tab                            │
└───────────────┴──────────────────────────────────────────────┘
```

## 2. 设计目标

- 把 Planner 页面从工程调试面板升级为 AI 分析助手式材料工作台。
- 保留工作台的信息密度，但取消独立右侧栏和底部结果区，减少用户视线分裂。
- 让用户先选数据集和模型，再在主体中完成“提问、看计划、看执行、看结果”的闭环。
- 让普通用户默认看到任务、数据、计划和结果；让开发者模式再展示 raw JSON、ID、hash 和 API payload。
- 继续展示 Agent Timeline 和结构化执行过程，不展示隐藏思维链。
- 继续保证 LLM 只能输出 JSON AnalysisPlan，执行必须经过 PlanValidator、persisted AnalysisPlan、QueueWorkerRuntime、Tool Registry 和 Adapter。

## 3. 顶部：Global Context Bar

顶部只承载全局上下文和系统入口，不放具体分析结果。

| 区域 | 内容 | 交互 |
|---|---|---|
| 当前数据集 | dataset name、profile status、row/structure/formula 摘要 | 点击打开 DatasetCommandDialog |
| 模型状态 | Mock Planner / OpenAI-compatible、model、provider status | 点击打开 ModelProviderDialog |
| 当前任务 | job status、最近一次运行结果、队列状态 | 点击可定位到主体的 Agent 过程 Tab |
| 顶部右侧设置 | 语言、主题、用户设置、帮助、开发者模式 | 这些入口与当前材料分析主题解耦 |

### DatasetCommandDialog

- 列出已上传数据集。
- 支持选择数据集、上传数据、加载 demo 数据。
- 展示 dataset detail、profile summary、parse status。
- 不伪造 dataset/profile 成功状态；后端不可用时显示明确错误和建议。

### ModelProviderDialog

- 支持 Mock Planner、本地安全模式、OpenAI-compatible provider。
- 支持 OpenAI、DeepSeek、自定义 baseUrl/model。
- 支持 temperature、maxTokens、timeoutSeconds。
- 只能选择已保存 Secret 或通过 Secret UX 新增；前端不把 API key 写入 localStorage/sessionStorage。
- Provider test 必须走后端安全测试接口，不返回 API key、Authorization header、raw prompt 或 raw completion。

## 4. 左侧：Data Context Viewer

左侧是数据集查看器，不是主要控制面板。它提供数据上下文，帮助用户理解当前数据能做什么分析。

### 布局规则

- 左侧宽度可拖拽调整，推荐默认 280-360px。
- 左侧可收起；收起后主体工作区自动扩展。
- 左中边界必须有明确 resize handle。
- 小屏幕下左侧进入 Drawer，但主体三视图规则不变。

### 按格式适配

| 数据类型 | 左侧展示 |
|---|---|
| CSV / table | 字段、行数、数值列、类别列、字段角色、缺失率、表格预览 |
| CIF / POSCAR / Structure JSON | 结构数、formula、元素、原子数、代表结构摘要、解析 warning |
| composition / formula | 组成字段、元素分布、化学体系、可用 composition 工具提示 |
| ZIP / archive | 文件树、解析成功/失败、normalized objects、失败原因 |
| unsupported / partial | 显示不可支持原因、已解析对象、推荐下一步；不得伪装为完整支持 |

### 左侧状态

| 状态 | 文案/行为 |
|---|---|
| empty | 请选择数据集，或在顶部加载/上传数据 |
| loading | 正在读取数据上下文 |
| profiling | 正在生成 Profile |
| ready | 展示 Profile 和可用分析入口 |
| partial_error | 显示可分析对象，同时列出失败文件和风险 |
| unsupported | 说明当前格式尚不支持，并给出后续能力建议 |

## 5. 主体：Main Workspace

主体是唯一承载 Agent 过程、对话/计划和结果展示的区域。**没有独立右侧 Result Inspector，也没有独立底部结果面板。**

主体内只有三个 Tab，同一时刻只显示其中一个：

1. `Agent 过程`
2. `对话与 Plan`
3. `结果与导出`

Tab 切换不能导致数据丢失；只改变当前主视图。后台 SSE / polling 可继续更新状态，但 UI 只渲染当前 active tab。

## 6. 主体 Tab 1：Agent 过程

该 Tab 展示结构化执行过程，不展示隐藏思维链。

### 事件类型

| Event | 中文标题 | 说明 |
|---|---|---|
| `plan.generated` | 分析计划已生成 | Provider 生成了候选 AnalysisPlan |
| `plan.persisted` | 分析计划已保存 | validated AnalysisPlan 已持久化 |
| `job.queued` | 任务已入队 | job_id 已进入队列或本地 demo worker path |
| `plan.loaded` | Worker 已加载分析计划 | QueueWorkerRuntime 根据 `job.plan_id` 加载 persisted plan |
| `data.loaded` | 数据对象已加载 | worker 已绑定 normalized dataset object |
| `tool.started` | 工具开始执行 | Tool Registry + Adapter 路径开始 |
| `artifact.ready` | 结果产物已生成 | artifact metadata 已写入 |
| `tool.completed` | 工具执行完成 | ToolCall completed |
| `job.completed` | 任务完成 | Job completed |
| `job.failed` | 任务失败 | 显示安全错误和建议 |

### 展示规则

- 每个事件显示时间、中文标题、简短说明、状态图标。
- 每个事件可展开安全 payload。
- 默认突出 persisted AnalysisPlan、Tool Registry + Adapter、无 deterministic fallback。
- 不显示 prompt/completion raw text、API key、Secret、内部临时路径或隐藏思维链。

## 7. 主体 Tab 2：对话与 Plan

该 Tab 是用户提出自然语言需求、查看系统响应和审查 Plan Preview 的地方。

### Chunk 模型

对话与计划采用统一 chunk 视觉：

| Chunk | 内容 |
|---|---|
| UserRequestChunk | 用户自然语言分析需求 |
| SystemResponseChunk | 系统对数据上下文、模型状态或错误的解释 |
| PlanPreviewChunk | validated AnalysisPlan 的自然语言步骤摘要 |
| ValidationChunk | 校验结果、风险、拒绝原因 |
| RunChunk | 创建/运行 job 的状态和入口 |

每个 chunk 可被选中。选中状态用于 `结果与导出` Tab 的上下文定位，例如选中某个 Plan step 后，结果 Tab 优先展示该 step 的 ToolCall、Artifact、Report/Recipe 片段。

### Plan Preview

普通用户默认看到：

```text
步骤 1：计算基础误差指标
工具：基础指标计算
输入：当前数据表
输出：metrics_json
预计产物：误差指标摘要
```

开发者模式才展示：

- stepId
- toolId
- inputRefs
- params
- expectedArtifacts
- planId
- planHash
- raw AnalysisPlan JSON

## 8. 主体 Tab 3：结果与导出

该 Tab 根据当前选中的 chunk / job / artifact 展示结果。所有结果相关内容都在这里，不放独立右侧栏。

### 支持结果类型

| 类型 | Renderer |
|---|---|
| 报告摘要 | ReportRecipeRenderer |
| 3D 材料图 | MaterialResultRenderer / sandboxed artifact iframe |
| metrics | MetricsResultRenderer |
| table / numeric summary | TableSummaryRenderer |
| artifact gallery | ArtifactGallery |
| recipe / provenance | ReportRecipeRenderer / ProvenanceBlock |
| report export | ExportControls |
| artifact download | ArtifactDownloadList |

### 空状态

| 场景 | 文案 |
|---|---|
| 未选择 chunk | 请选择一个分析步骤或结果 chunk |
| job 未创建 | 任务运行后将在这里显示结果 |
| artifact 未生成 | 当前步骤尚未生成结果产物 |
| report 未生成 | 任务完成后将在这里生成系统摘要 |
| unsupported artifact | 当前结果类型暂不支持预览，可下载原始 Artifact |

不得在主界面默认渲染大面积 `Not available yet`。

## 9. 响应式规则

| 屏幕 | 行为 |
|---|---|
| >= 1440px | 顶部 + 左侧可调宽 + 主体三 Tab 完整展示 |
| 1024-1439px | 左侧可收起；主体 Tab 仍保持单视图 |
| 768-1023px | 左侧进入 Drawer；顶部保留数据集/模型状态；主体单列 |
| < 768px | 优先保证对话、Plan Preview、结果查看；复杂数据查看进入 Drawer |

## 10. 数据流 / 控制流

```text
Top dataset/model selection
  -> DataContextViewer loads dataset/profile
  -> ConversationPlanTab submits natural-language request
  -> provider returns JSON AnalysisPlan
  -> PlanValidator validates
  -> /planner/jobs persists exact plan and creates job
  -> QueueWorkerRuntime loads job.plan_id
  -> Tool Registry + Adapter executes tool calls
  -> JobEvents update AgentProcessTab
  -> Artifacts/Results update ResultsExportTab
```

前端不得：

- 直接写 `analysis_plans`。
- 直接 enqueue queue message。
- 直接执行 adapter。
- 自行计算 authoritative plan hash。
- 在 validation failure 后伪造 jobId/planId。

## 11. 安全与审计

- LLM 只输出 JSON AnalysisPlan，不直接执行 Python、Shell、文件系统或网络动作。
- AnalysisPlan 必须通过 PlanValidator 后才能持久化。
- ToolCall 必须走 Tool Registry + Adapter。
- API key / Secret 不进入 prompt、JobEvent、Artifact、Report、Recipe、export package、localStorage 或 sessionStorage。
- Agent 过程展示结构化 JobEvent，不展示隐藏思维链。
- Developer Audit 只能在开发者模式下打开，且仍必须使用脱敏 payload。

## 12. Legacy Layout 处理

旧文档中的以下结构为历史实现背景：

- 独立右侧 Agent Panel。
- 独立底部 Logs / Code / Artifacts / Recipe / Warnings 面板。
- 中央 Visualization Canvas 与右侧 Chat 并列。

后续实现不得继续把“结果查看”设计成独立右侧栏，也不得把 Agent 过程、对话和结果固定为页面三列。它们必须作为主体工作区的三个 Tab。

## 13. 关联文档

- 组件规格：`docs/03A_FRONTEND_COMPONENT_SPEC.md`
- 状态与交互：`docs/03B_FRONTEND_STATE_AND_INTERACTION.md`
- 产品流程：`docs/01_PRODUCT_REQUIREMENTS.md`
- UI-only view model：`docs/13_SHARED_SCHEMA_SPEC.md`
