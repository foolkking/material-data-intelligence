# Phase 1：产品需求与用户流程

## 1. 本阶段目标

从用户视角定义“材料数据智能分析与可视化平台”的产品需求和核心使用流程，明确用户如何创建项目、上传材料数据、用自然语言提出分析需求、审查 Agent 计划、生成 Plotly / MatterViz 图表和 3D 模型、查看执行过程、保存 Artifact / Recipe / Report。

本阶段不细化服务拆分、数据库索引、Tool Registry 参数 Schema 或 Worker 实现，这些在 Phase 2 之后展开。

## 2. 本阶段解决的问题

### 产品要解决的核心问题

用户通常不是单纯想调用某个 pymatviz 函数，而是面对一批材料数据时不知道：

- 文件里到底有什么材料对象。
- 数据质量是否可靠。
- 应该画哪些图。
- 哪些结构、元素、化学体系或预测结果值得关注。
- 如何复现这次分析。
- 如何把过程、图表和结论整理成报告。

平台要把这些问题转成一条可操作流程：

```text
创建项目
  -> 上传数据
  -> 系统生成 Data Profile
  -> 用户自然语言提出目标
  -> Agent 生成结构化 Analysis Plan
  -> 用户查看计划摘要
  -> 系统异步执行工具
  -> 前端渐进展示图表、3D 模型、日志和 Artifact
  -> 系统生成 Recipe 和 Report
```

### Phase 1 明确的产品决策

| 决策 | 结论 |
|---|---|
| MVP 用户范围 | 默认只支持登录用户；公开分享和游客访问推迟到 V1。 |
| MVP 交互模式 | 默认 Auto 模式：系统自动生成计划并展示可审查摘要；Guided / Expert 模式推迟到 V1。 |
| MVP 计划编辑 | 用户可以取消、重新生成或选择推荐任务；不直接编辑 JSON Plan。 |
| MVP 报告导出 | 支持 Markdown / HTML；PDF 推迟到 V1。 |
| MVP 数据路径 | 同时覆盖结构数据和预测结果 CSV 的核心闭环。 |
| Agent 过程展示 | 展示 Agent Timeline、工具调用、参数、日志和 Artifact；不展示原始隐藏思维链。 |

## 3. 设计原则

- 工作台优先：产品不是聊天框，而是材料数据分析工作台。
- 数据画像先于 Agent：自然语言分析必须基于 Data Profile。
- 默认自动，但过程可见：MVP 让系统自动规划，用户能看到计划摘要、工具调用和参数。
- 所有耗时操作异步：上传解析、图表生成、3D 渲染、报告生成都通过 Job 执行。
- Artifact 优先：每个图表和模型都必须有可保存、可预览、可导出、可复现的产物。
- Recipe 即流程资产：一次分析流程应能保存并应用到新数据集。
- 安全默认开启：文件安全、权限、Secret、Prompt injection 防护和审计进入产品流程。
- 渐进式展示：用户不等待全量任务完成；Data Profile、图表卡片、3D 模型和报告分阶段出现。

## 4. 核心用户、角色与用户故事

### 用户角色

| 角色 | 权限范围 | 典型目标 |
|---|---|---|
| Project Owner | 管理项目、成员、配置、Secret、Recipe 和 Artifact | 建立课题组数据分析空间 |
| Researcher | 上传数据、运行分析、保存报告和 Recipe | 分析结构数据集、检查异常、导出图表 |
| ML Researcher | 上传预测结果、分析误差和不确定性 | 找出模型误差来源和 OOD 样本 |
| Viewer | 查看已生成 Dashboard、Artifact 和报告 | 阅读结果，不运行高成本任务 |
| Org Admin | 管理组织、额度、审计和安全策略 | 控制 BYOK、预算、权限和数据边界 |
| Plugin Developer | 添加工具 Adapter 和材料领域扩展 | 扩展新的分析能力 |

### 用户故事

| 用户故事 | 验收标准 |
|---|---|
| 作为 Researcher，我上传一批 CIF，系统自动告诉我有效结构数量、元素集合、空间群和异常结构。 | 上传后生成 Data Profile，显示成功/失败文件、元素、结构统计和质量警告。 |
| 作为 Researcher，我输入“分析元素分布和结构异常”，系统自动生成图表计划。 | Agent 返回结构化计划，MVP 包含 ptable、chem_sys、3D、coordination 等工具；spacegroup 先从 Data Profile 展示，V1 工具化为 `structure.spacegroup_bar`。 |
| 作为 ML Researcher，我上传 `formula,y_true,y_pred,y_std` 表格，系统分析误差来源。 | MVP：系统识别回归任务，生成 density scatter、error distribution、basic metrics 和 outlier table；V1 扩展 parity plot、uncertainty calibration、error by element、error by chemical system。 |
| 作为用户，我想知道系统为什么画这些图。 | Agent Timeline 展示数据识别、计划生成、工具选择理由、参数和 Artifact。 |
| 作为用户，我想查看 3D 结构和代表样本。 | Structure Tab 展示 MatterViz / Plotly 3D Viewer，并能切换代表结构。 |
| 作为用户，我想复现这次分析。 | 系统保存 Recipe JSON，包含输入引用、工具 ID、参数、版本和输出格式。 |
| 作为 Owner，我想限制项目预算和 LLM Key。 | 项目配置支持预算、BYOK 引用、默认模型和导出格式；Key 不出现在日志或前端。 |

## 5. 核心模块

| 模块 | 产品职责 |
|---|---|
| Project Workspace | 项目入口，承载数据集、会话、Job、Artifact、Recipe 和报告 |
| Data Asset Panel | 文件树、解析状态、Data Profile、字段映射、异常列表和推荐任务 |
| Visualization Canvas | 多 Tab 图表和 3D 模型展示区 |
| Agent Panel | 自然语言输入、计划摘要、工具调用 Timeline、解释和下一步建议 |
| Bottom Panel | Logs、Code、Artifacts、Recipe、Warnings |
| Upload Flow | 文件/压缩包上传、类型识别、解析进度和失败反馈 |
| Data Profile Flow | 结构、组成、表格、声子、轨迹的摘要和质量检查 |
| Analysis Plan Flow | 用户需求 + Data Profile + Tool Registry -> JSON Plan |
| Artifact / Recipe Flow | 结果保存、预览、导出、复现和应用到新数据集 |

## 6. 用户流程

### 6.1 创建项目流程

```text
用户进入首页
  -> 创建 Project
  -> 选择项目类型：结构数据 / ML 预测结果 / 混合材料数据 / 声子 / 轨迹
  -> 设置默认单位、图表主题、LLM 配置引用
  -> 进入工作台
```

MVP 项目创建字段：

| 字段 | 说明 |
|---|---|
| project_name | 项目名称 |
| project_type | `structure_dataset` / `ml_results` / `mixed_material_dataset` |
| default_units | energy、length、pressure 等默认单位 |
| default_download_formats | HTML、JSON、PNG、Markdown |
| llm_config_ref | 用户或项目级 LLM 配置引用 |

### 6.2 上传数据流程

```text
用户拖拽或选择文件
  -> 前端创建 Upload Session
  -> API 保存 raw file
  -> 创建 parse job
  -> SSE/WebSocket 推送 file.detected / file.parsed / file.failed
  -> Data Service 生成 Data Profile
  -> 左侧数据区刷新数据资产树和字段映射
```

MVP 支持：

- CIF
- POSCAR / CONTCAR
- XYZ / EXTXYZ 基础支持：plain XYZ 解析为 `Atoms` / molecule-like 对象；只有包含 lattice 的 EXTXYZ 才可进入周期结构工具
- CSV
- JSON limited：仅支持 pymatgen Structure JSON、Materials Project-like structure dict、simple table JSON
- ZIP 作为容器格式，内部只处理 MVP 支持的文件

V1/V2 扩展：

- Excel / Parquet
- ASE trajectory
- phonopy.yaml / band.yaml / DOS
- VASP 输出
- LAMMPS dump
- tar.gz

上传反馈必须包含：

| 信息 | 示例 |
|---|---|
| 文件数量 | 128 files |
| 成功解析 | 126 valid structures |
| 失败解析 | 2 failed files |
| 检测对象 | `pymatgen.Structure[]`、`pandas.DataFrame` |
| 推荐任务 | composition overview、structure quality、ml evaluation |
| Warning | short bonds、missing columns、unknown format |

### 6.3 Data Profile 与字段映射流程

结构数据 Profile：

| 字段 | 示例 |
|---|---|
| n_structures | 126 |
| elements | Li, Fe, P, O |
| formula_stats | unique count、top formulas、完整列表 object ref |
| spacegroups | number / symbol distribution |
| atom_count_stats | min / median / max |
| lattice_stats | a/b/c/alpha/beta/gamma summary |
| has_forces | true / false |
| has_magmoms | true / false |
| quality_issues | parse failure、short bond、unusual volume |

表格数据 Profile：

| 字段 | 示例 |
|---|---|
| columns | formula, y_true, y_pred, y_std |
| inferred_task | regression / classification / unknown |
| inferred_roles | formula、target、prediction、uncertainty |
| missing_values | by column |
| numeric_stats | min / mean / max |
| recommended_tasks | MVP: ml evaluation；V1: error by element / chemical system |

字段映射交互：

- 系统自动推断 `formula`、`target`、`prediction`、`uncertainty`、`structure_id`。
- 用户可在左侧面板修正字段映射。
- Agent 只能基于确认后的字段映射生成计划。

### 6.4 自然语言分析流程

```text
用户输入需求
  -> Intent Agent 提取目标
  -> Data Agent 检查 Data Profile 可用性
  -> Planner 选择工具
  -> 系统生成 Analysis Plan 摘要
  -> 用户点击 Run / Regenerate / Cancel
  -> Execution Controller 校验并提交 Job
```

示例输入：

```text
帮我分析这批 CIF 结构的元素分布、空间群分布、结构异常，并生成几个代表性 3D 模型。
```

计划摘要示例：

| Step | Tool | 目的 |
|---|---|---|
| 1 | `composition.ptable_heatmap` | 查看元素覆盖和频率 |
| 2 | `composition.chem_sys_treemap` | 查看化学体系分布 |
| 3 | Data Profile `spacegroupDistribution` | 查看空间群分布；V1 可升级为 `structure.spacegroup_bar` |
| 4 | `structure.coordination_hist` | 检查局部环境异常 |
| 5 | `structure.viewer_3d` | 展示代表性 3D 结构 |

### 6.5 图表生成流程

```text
Analysis Plan
  -> Tool Registry 校验工具存在性
  -> 输入引用校验
  -> 参数 Schema 校验
  -> 缓存检查
  -> Worker 执行工具
  -> Artifact Service 保存结果
  -> 前端图表卡片渐进显示
```

图表卡片必须显示：

- 标题。
- 图表预览或 skeleton。
- 数据来源。
- 工具 ID。
- 关键参数。
- 图表解释。
- 导出按钮：HTML / JSON / PNG，V1 增加 SVG / PDF。
- 重新运行入口。
- Warning / Error 状态。

### 6.6 3D 模型查看流程

```text
结构数据 Profile ready
  -> 系统选择代表结构
  -> 生成低成本 preview
  -> 用户进入 Structure Tab
  -> 加载 MatterViz / Plotly 3D Viewer
  -> 用户切换结构、查看晶胞、bonds、site labels、force/magmom vectors
```

3D Viewer MVP 行为：

| 场景 | 默认行为 |
|---|---|
| 小结构 | 显示 atoms + bonds + cell |
| 中结构 | 显示 atoms + cell，bonds 可开关 |
| 大结构 | 默认 summary / LOD，用户手动展开 |
| 多结构 | 系统选代表结构，用户可从列表切换 |
| trajectory | MVP 可展示静态首末帧；完整播放器推迟到 V1 |

### 6.7 Agent Timeline 流程

前端展示结构化过程：

```text
1. Data Detection
2. Data Quality Check
3. Intent Parsed
4. Plan Generated
5. Tool Validated
6. Tool Running
7. Artifact Ready
8. Result Explained
9. Report Ready
```

每个 Timeline item 至少包含：

| 字段 | 说明 |
|---|---|
| event_type | `data_detected` / `plan_generated` / `tool_started` 等 |
| title | 用户可读标题 |
| message | 简短解释 |
| payload | 结构化数据，不含 Secret |
| timestamp | 事件时间 |
| status | info / running / success / warning / error |

### 6.8 Artifact / Recipe / Report 流程

每次分析生成：

| 产物 | MVP 格式 |
|---|---|
| Plotly 图 | JSON、HTML、PNG preview |
| MatterViz / 3D | viewer HTML、metadata；snapshot 为 MVP 可选预览 |
| Metrics | metrics JSON |
| Tables | table JSON / table CSV |
| Quality Issues | quality issues JSON |
| Execution Plan | JSON |
| Tool Calls | JSON + Timeline events |
| Recipe | recipe JSON |
| Report | Markdown、HTML |

Recipe 复现流程：

```text
用户选择 Recipe
  -> 选择同项目或新项目 Dataset
  -> 系统检查输入对象和字段映射是否满足
  -> 生成可运行计划
  -> 提交 Job
  -> 生成新 Artifact 和 Report
```

## 7. 数据流 / 控制流

### 数据流

```text
Raw Files
  -> Parsed Objects
  -> Data Profile
  -> Field Mapping
  -> Analysis Plan
  -> Tool Calls
  -> Artifacts
  -> Recipe
  -> Report
```

### 控制流

```text
Frontend Action
  -> API request
  -> Job created
  -> Worker execution
  -> Job events
  -> Artifact ready
  -> Frontend incremental update
```

关键事件类型：

```text
upload.started
file.detected
file.parsed
profile.ready
analysis.requested
plan.generated
tool.started
tool.warning
artifact.ready
report.ready
job.completed
job.failed
```

## 8. API / Schema 草案

正式 API 在 Phase 4 定义。本阶段固定产品级请求/响应边界。

```ts
type CreateProjectRequest = {
  name: string;
  projectType: "structure_dataset" | "ml_results" | "mixed_material_dataset" | "phonon" | "trajectory";
  defaultUnits?: Record<string, string>;
  defaultDownloadFormats?: Array<"html" | "json" | "png" | "markdown">;
};

type UploadSession = {
  id: string;
  projectId: string;
  status: "created" | "uploading" | "uploaded" | "parsing" | "profile_ready" | "failed";
  files: Array<{ fileId: string; name: string; detectedFormat?: string; status: string }>;
};

type AnalysisRequest = {
  projectId: string;
  datasetId: string;
  userPrompt: string;
  mode: "auto";
  confirmedFieldMappings?: Record<string, string>;
};

type AnalysisPlanSummary = {
  goal: string;
  steps: Array<{
    toolId: string;
    purpose: string;
    inputSummary: string;
    keyParams: Record<string, unknown>;
    expectedArtifacts: Array<{ name: string; type: ArtifactType; fromStepId?: string }>;
  }>;
  warnings: string[];
};

type AgentTimelineEvent = {
  id: string;
  jobId: string;
  seq?: number;
  eventType: string;
  title: string;
  message: string;
  status: "info" | "running" | "success" | "warning" | "error";
  payload?: Record<string, unknown>;
  createdAt: string;
};

type ArtifactSummary = {
  id: string;
  type:
    | "plotly_json"
    | "plotly_html"
    | "preview_png"
    | "matterviz_html"
    | "metrics_json"
    | "table_json"
    | "table_csv"
    | "quality_issues_json"
    | "report_md"
    | "report_html"
    | "recipe_json";
  name: string;
  previewUrl?: string;
  downloadUrl: string;
  toolCallId?: string;
};
```

## 9. 数据库表草案

Phase 4 会细化字段、索引和权限。本阶段增加产品流程所需实体。

| 表 | Phase 1 用途 |
|---|---|
| users | 登录用户和偏好 |
| organizations | 组织租户 |
| projects | 项目工作台容器 |
| project_members | 项目成员和角色 |
| datasets | 数据集集合 |
| files | 上传文件、解析状态和存储引用 |
| data_profiles | 数据画像和质量检查 |
| field_mappings | 表格列和材料字段映射 |
| sessions | Agent 对话会话 |
| messages | 用户输入、系统摘要和 Agent 输出 |
| jobs | 异步任务状态 |
| job_events | Agent Timeline 和进度事件 |
| tool_calls | 工具调用、参数、状态和错误 |
| artifacts | 图表、3D 模型、报告和导出文件 |
| visualization_recipes | 可复现分析流程 |
| user_configs | 用户偏好和模型配置引用 |
| project_configs | 项目默认单位、字段、图表风格和预算 |
| secrets | BYOK 和外部服务密钥加密引用 |
| audit_logs | 上传、运行、导出、权限和 Secret 使用记录 |

## 10. 前端交互草案

### 页面布局

```text
┌────────────────────────────────────────────────────────────┐
│ 顶部：项目 / 数据集 / 模型配置 / 运行状态 / 导出 / 分享     │
├───────────────┬───────────────────────────┬────────────────┤
│ 左侧数据区     │ 中央可视化画布              │ 右侧 Agent 区   │
│ 文件树         │ Overview Dashboard         │ Chat            │
│ Data Profile   │ Composition Tab            │ Plan            │
│ 字段映射       │ Structure Tab              │ Tool Calls      │
│ 异常列表       │ ML Evaluation Tab          │ Explanation     │
│ 推荐任务       │ Artifact Detail            │ Next Steps      │
├───────────────┴───────────────────────────┴────────────────┤
│ 底部：Logs / Code / Artifacts / Recipe / Warnings           │
└────────────────────────────────────────────────────────────┘
```

### Tab 需求

| Tab | MVP 内容 |
|---|---|
| Overview | 数据集摘要、质量卡片、推荐任务、关键 warning |
| Composition | 周期表热力图、元素直方图、化学体系 treemap |
| Structure | 3D Viewer、配位数分布、代表结构列表 |
| ML Evaluation | density scatter、误差分布、basic metrics、outlier table；parity 和 error-by-domain 进入 V1 |
| Artifacts | 全部生成产物、下载、预览、Recipe 链接 |

V1/V2 增加：

- Trajectory Tab。
- Phonon Tab。
- RDF / XRD 专区。
- 可拖拽 Dashboard。
- Expert Recipe editor。

### 交互状态

| 状态 | 前端行为 |
|---|---|
| No data | 显示上传引导和支持格式 |
| Uploading | 显示文件级进度 |
| Profiling | 左侧显示 skeleton，右侧禁用 Run |
| Profile ready | 显示推荐任务和自然语言输入 |
| Plan generated | 显示计划摘要和 Run / Regenerate / Cancel |
| Running | 图表卡片 skeleton，Timeline 实时更新 |
| Partial artifacts ready | 单个图表完成即展示 |
| Completed | 展示报告、Recipe、导出入口 |
| Failed | 展示错误、可重试步骤和日志 |

## 11. 高并发、安全、扩展性考虑

### 高并发与流畅展示

- 上传、解析、Agent 规划、工具执行、3D 渲染、报告生成全部异步。
- 前端通过 SSE/WebSocket 接收 JobEvent，只通过 Artifact URL 拉取大图表数据。
- 图表卡片按 Tab 懒加载，避免一个重图阻塞全页面。
- 大表格默认 density/hexbin/后端预聚合，不直接渲染百万点散点。
- 3D Viewer 按结构大小启用 LOD、隐藏 bonds、抽帧或代表结构选择。

### 安全

- MVP 默认登录用户访问；公开分享推迟到 V1。
- BYOK 只保存加密引用，不进入 prompt、日志、Timeline 或前端响应。
- Agent 输入区分用户 prompt、Data Profile、Tool Registry、系统策略。
- 用户上传文件需要大小限制、类型白名单、压缩包安全检查、路径穿越防护和解析超时。
- Code 面板展示可复现代码片段或安全执行摘要，不展示包含 Secret 或内部路径的代码。
- 所有 Run、Export、Secret 使用和权限变更进入 audit log。

### 扩展性

- 后续支持 Guided / Expert 模式。
- 后续支持 public share、PDF export、SVG/PDF 论文图导出。
- 后续支持 trajectory、phonon、RDF/XRD、Materials Project / OPTIMADE、AiiDA / atomate2。
- 后续支持插件工具、团队 Recipe 库和组织级默认配置。

## 12. 非功能需求与验收标准

### 非功能需求

| 类别 | 要求 |
|---|---|
| 可用性 | 用户无需知道 pymatviz 函数名也能完成分析 |
| 可解释性 | 每个图表显示选择理由、输入、参数和解释 |
| 可审计性 | 每个 Job 有 Timeline、ToolCall、Artifact 和日志 |
| 可复现性 | 每次分析保存 Recipe 和工具版本 |
| 性能 | 页面渐进展示，不等待全部图表完成 |
| 安全 | 无任意代码执行、无 Secret 泄漏、文件解析隔离 |

### MVP 验收标准

- 用户能创建项目并上传 CIF、POSCAR/CONTCAR、CSV、ZIP 容器，并支持 JSON limited 与 XYZ/EXTXYZ 基础解析边界。
- 系统能生成结构数据和预测结果表格的 Data Profile。
- 用户能输入自然语言并得到 Analysis Plan 摘要。
- 10 个 MVP 工具均已注册、可通过 Tool Registry 校验，并可由 Worker 执行。
- 端到端演示至少覆盖 6 个核心工具，并包含 composition、structure、ml 三类能力。
- 端到端演示中必须出现 metrics/table 类 Artifact。
- 前端能展示 Agent Timeline、图表卡片、3D Viewer、日志、Artifact 和 Recipe。
- 生成的 Artifact 至少包含 Plotly JSON、交互展示产物、PNG preview、metrics/table JSON、Markdown/HTML report。
- 所有耗时任务通过 Job 事件流展示进度。

## 13. 本阶段产出的目标文件

```text
docs/01_PRODUCT_REQUIREMENTS.md
persistent/DESIGN_PROGRESS.md
persistent/TASK_BOARD.md
persistent/ARCHITECTURE_DECISIONS.md
persistent/OPEN_QUESTIONS.md
persistent/CHANGELOG.md
```

## 14. 下一阶段任务

Phase 2：总体系统架构。

需要定义：

- 前端、API Gateway、Agent Service、Data Service、Visualization Service、Worker Service、Artifact Service 的边界。
- 同步 / 异步边界。
- 数据流和控制流。
- PostgreSQL / Redis / S3-MinIO / Queue 的职责。
- 安全边界和部署拓扑。
