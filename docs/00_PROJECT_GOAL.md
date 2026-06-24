# Phase 0：项目目标与边界定义

## 1. 本阶段目标

明确“材料数据智能分析与可视化平台”的系统定位、边界、核心用户、核心场景、MVP 范围和长期演进方向，为后续产品需求、系统架构、Agent 编排、工具注册表、数据管线和安全设计提供稳定基线。

## 2. 本阶段解决的问题

### 系统是什么

本系统是一个面向材料科学与材料信息学工作流的智能分析与可视化平台。用户上传 CIF、POSCAR/CONTCAR、XYZ/EXTXYZ、CSV、JSON limited、ZIP 等 MVP 数据，后续扩展到 ASE trajectory、Excel/Parquet、phonopy.yaml、band.yaml、DOS、VASP/LAMMPS 等材料相关文件后，可以用自然语言描述分析目标。系统基于文件解析结果和 Data Profile 生成结构化分析计划，通过受控 Tool Registry 调用 pymatviz、MatterViz、Plotly、pymatgen、ASE、phonopy 等工具，产出可交互图表、3D 材料结构模型、Artifact、Recipe 和报告。

### 系统不是什么

- 不是 pymatviz 的简单 Web 套壳。
- 不是 DFT、MD 或第一性原理计算引擎。
- 不是允许 LLM 任意写代码并直接执行的平台。
- 不是普通聊天机器人；核心界面是材料数据分析工作台。
- 不是只生成静态图的报表工具；必须支持可审计过程、可复现 Recipe 和 Artifact 管理。
- 不展示 LLM 原始隐藏思维链，只展示结构化计划、工具调用、参数、日志、警告和解释。

### 为什么不是简单 pymatviz 套壳

pymatviz 是重要的材料可视化能力来源，但平台的核心价值在于把材料文件解析、对象标准化、Data Profile、自然语言意图理解、分析计划、工具选择、异步任务、Artifact 管理、Recipe 复现、权限安全和高并发展示串成完整工作流。pymatviz / MatterViz / Plotly 是受控工具层的一部分，而不是系统本身。

### 与 pymatviz / MatterViz 的关系

本平台把 pymatviz / MatterViz 作为材料可视化执行层，而不是产品边界本身。

| 能力来源 | 平台内角色 | 典型输出 |
|---|---|---|
| pymatviz | 材料信息学图表和结构可视化函数库 | 周期表图、组成聚类、RDF、XRD、配位、声子、ML 评估图、Plotly 3D |
| MatterViz | 浏览器材料科学交互 UI 与 WebGL 3D Viewer | StructureWidget、TrajectoryWidget、结构/轨迹 HTML、metadata、optional snapshot |
| Plotly | 交互式图表载体与导出格式 | Figure JSON、HTML、PNG；SVG/PDF 进入 V1 |
| pymatgen / ASE / phonopy | 材料对象语义层 | Structure、Composition、Atoms、PhonopyAtoms、phonon band/DOS |
| 平台 Adapter | LLM-friendly 工具封装 | Tool Schema、参数校验、缓存、错误标准化、Artifact 输出 |

数据到图表的基础映射：

| 输入数据 | 标准化对象 | 推荐图表 / 模型 |
|---|---|---|
| 化学式列表、Composition | `pymatgen.Composition[]` | `ptable_heatmap`、`elements_hist`、`chem_sys_treemap` |
| CIF / POSCAR / Structure | `pymatgen.Structure[]` | `structure_3d`、MatterViz StructureWidget、RDF、XRD、coordination histogram、spacegroup distribution |
| XYZ / EXTXYZ / ASE trajectory | `ASE Atoms[]` / trajectory frames | MVP：plain XYZ 作为非周期 Atoms 预览，含 lattice 的 EXTXYZ 可转 Structure；完整 TrajectoryWidget 和曲线进入 V1 |
| phonopy.yaml / band.yaml / DOS | phonopy / pymatgen phonon objects | phonon band、phonon DOS、band + DOS |
| 预测结果表格 | `pandas.DataFrame` | MVP：density scatter、error distribution、basic metrics、outlier table；V1：parity plot、uncertainty calibration、error by element / chemical system |

3D 可视化采用两条路线：

- Plotly 3D：适合快速生成 `structure_3d` 图、论文图、HTML 交互图和图表卡片。
- MatterViz / Widget：适合浏览器端结构查看、轨迹播放、交互检查和专门的材料 Viewer。

### 核心用户

| 用户 | 主要目标 | 典型需求 |
|---|---|---|
| 材料科研人员 | 快速理解结构数据集和计算结果 | CIF 批量统计、空间群分布、元素分布、代表结构查看 |
| 材料机器学习研究者 | 分析模型预测误差与数据偏差 | MVP：band gap 基础误差分布、指标和离群表；V1：按元素/化学体系聚合误差、parity plot |
| 计算材料工程师 | 检查仿真输入输出和结构异常 | POSCAR/CONTCAR 检查、轨迹查看、RDF/XRD/配位分析 |
| 课题组或平台管理员 | 管理项目、权限、配置和可复现记录 | 项目级参数、BYOK、审计日志、Artifact 分享 |
| 高级开发者/领域专家 | 扩展材料分析工具链 | 新工具 Adapter、专业插件、内部工具文档 RAG |

### 核心场景

- 上传一批 CIF 文件，自动识别结构、生成元素分布、化学体系分布、空间群分布、结构异常列表和代表性 3D 模型。
- 上传 band gap 预测 CSV，自动识别真实值/预测值/化学式字段，MVP 生成 density scatter、误差分布、basic metrics 和 outlier table；V1 扩展 parity plot、按元素和化学体系聚合误差。
- 上传 phonopy 输出，生成 phonon band、phonon DOS 和相关 Artifact。
- 上传 trajectory，按帧查看结构演化并生成能量、力或结构变化曲线。
- 保存分析过程为 Recipe，在新数据集上复现同一分析流程。

### MVP 边界

MVP 优先交付一条完整闭环，而不是追求所有材料格式和所有图表类型：

- 文件上传与资产管理：支持单文件与 ZIP 批量上传的设计，MVP 优先实现 CIF、POSCAR/CONTCAR、CSV、ZIP 容器、JSON limited、XYZ/EXTXYZ 基础支持。
- 数据解析与 Data Profile：支持结构类数据和表格类预测结果的基础画像。
- Agent：只输出结构化 JSON Plan，由系统校验后执行。
- Tool Registry：提供 composition、structure、ml 三类核心工具的最小白名单。
- 可视化：生成 Plotly 图表和 MatterViz/pymatviz 3D 结构 Artifact。
- 异步任务：所有耗时解析、分析、图表和报告生成都走 Job Queue。
- Artifact / Recipe / Report：保存关键输出、参数、工具版本和基础 Markdown/HTML 报告。
- 安全：BYOK、Secret 加密、权限、审计、文件解析安全和沙箱执行进入初始设计。

### 长期演进方向

- 扩展到 phonon、DOS、电子结构、LAMMPS dump、VASP 输出、AiiDA/atomate2/OPTIMADE/Materials Project 等生态。
- 提供插件化材料工具注册机制，支持团队内部工具接入。
- 支持更大规模数据集的分布式解析、分层缓存、预计算和近实时交互。
- 支持多租户组织、项目模板、共享空间、报告发布和可复现实验库。
- 构建面向材料数据分析的 Agentic Workflow 平台，而不是单次问答工具。

## 3. 设计原则

- 数据先行：所有分析计划必须基于已解析数据和 Data Profile。
- 受控执行：LLM 只生成 JSON Plan，不直接执行系统命令或任意代码。
- 工具白名单：所有可执行能力必须通过 Tool Registry、Schema 校验、权限检查、资源限制和沙箱。
- 异步优先：文件解析、图表生成、3D 模型、报告和批量任务默认异步执行。
- 渐进展示：前端在文件解析、画像生成、工具执行和 Artifact 生成过程中持续展示阶段性结果。
- 可审计与可复现：保存计划、工具调用、参数、日志、Artifact、Recipe、版本和报告。
- 专业可扩展：从一开始预留材料领域工具、对象类型和插件扩展边界。
- 安全内建：用户、组织、项目、Secret、BYOK、权限、审计和 Prompt injection 防护不是后补功能。

## 4. 核心模块

| 模块 | Phase 0 职责定义 |
|---|---|
| Frontend Workspace | 三栏式材料分析工作台，展示数据资产、图表、3D Viewer、Agent Timeline、日志和 Artifact |
| API Gateway | 统一认证、项目上下文、请求入口、任务提交和事件订阅 |
| Data Service | 文件识别、解析、对象标准化、Data Profile 和数据质量检查 |
| Agent Service | Intent Parser、Data-aware Planner、Tool Selector、Report Writer |
| Execution Controller | 校验 JSON Plan，调度工具调用，不让 LLM 直接执行代码 |
| Visualization Service | 封装 pymatviz、MatterViz、Plotly，生成图表和 3D Artifact |
| Worker Service | 执行耗时任务、并发控制、重试、超时和资源限制 |
| Artifact Service | 管理 Plotly JSON/HTML/图片、MatterViz HTML/metadata/optional snapshot、metrics/table、报告和 Recipe |
| Storage Layer | PostgreSQL 存元数据，S3/MinIO 存文件与 Artifact，Redis 存缓存与队列状态 |
| Security Layer | 用户/组织/项目权限、Secret 加密、沙箱、审计和 Prompt injection 防护 |

## 5. 数据流 / 控制流

### 数据流

```text
用户上传文件
  -> File Asset
  -> 格式识别
  -> 解析为 Structure / Composition / Atoms / DataFrame / Phonon / Trajectory
  -> 标准化材料对象
  -> Data Profile
  -> Agent 读取用户需求 + Data Profile
  -> JSON Analysis Plan
  -> Tool Registry 校验
  -> Worker 执行工具
  -> Artifact / Recipe / Report
  -> 前端渐进展示
```

### 控制流

```text
Frontend
  -> API Gateway 创建 Job
  -> Queue 分发到 Worker
  -> Worker 调用 Data / Agent / Visualization / Artifact 服务
  -> Event Stream 推送 job.started / profile.ready / tool.running / artifact.ready / job.completed
  -> Frontend 更新 Dashboard、Agent Timeline、日志、Artifact 面板
```

## 6. API / Schema 草案

本阶段只定义概念边界，不维护正式 Schema。正式共享 Schema 以 `docs/13_SHARED_SCHEMA_SPEC.md` 为准，包括：

- `DataAsset`
- `NormalizedObject`
- `DataProfile`
- `InputRef`
- `AnalysisPlan`
- `RegisteredTool`
- `ToolCall` / `ToolExecutionRequest` 相关引用结构
- `Artifact`
- `VisualizationRecipe`
- `JobEvent`
- `LlmExecutionProfile`

后续实现不得从 Phase 0 复制旧草案类型；应从 `docs/13_SHARED_SCHEMA_SPEC.md` 派生 JSON Schema、TypeScript 类型和 Python Pydantic model。

## 7. 数据库表草案

Phase 0 只定义实体范围，不锁定字段。Phase 4 将给出正式表结构、索引、多租户隔离和权限模型。

| 实体 | 目的 |
|---|---|
| users | 用户身份 |
| organizations | 组织与租户边界 |
| projects | 项目级数据、配置和权限容器 |
| datasets | 一组材料文件或表格数据的集合 |
| files | 原始上传文件和解析状态 |
| data_profiles | 数据画像、字段映射和质量问题 |
| jobs | 异步任务状态机 |
| tool_calls | 工具调用、参数、状态、日志和错误 |
| artifacts | 图表、3D 模型、报告和导出文件 |
| recipes | 可复现分析流程 |
| user_configs | 用户级默认配置 |
| project_configs | 项目级材料分析参数和图表风格 |
| secrets | BYOK 和外部服务密钥的加密引用 |
| audit_logs | 用户行为、工具执行和权限事件 |

## 8. 前端交互草案

工作台不是普通聊天页，而是四区协同界面：

| 区域 | 内容 |
|---|---|
| 左侧 | 数据资产、文件树、Data Profile、字段映射、异常列表 |
| 中间 | Dashboard、Composition、Structure、Trajectory、Phonon、ML Evaluation 等 Tab |
| 右侧 | Agent 对话、分析计划、工具调用过程、参数解释、下一步建议 |
| 底部 | 日志、代码片段、Artifact、Recipe、Warnings |

MVP 交互闭环：

1. 用户上传文件或压缩包。
2. 系统展示解析进度和 Data Profile。
3. 用户输入自然语言分析目标。
4. Agent 生成可审查 JSON Plan。
5. 系统执行白名单工具并渐进生成 Artifact。
6. 用户查看图表、3D 模型、日志、参数和报告。
7. 用户保存或导出 Recipe / Report。

## 9. 高并发、安全、扩展性考虑

### 高并发

- 所有耗时任务异步执行，API 只负责提交任务和返回 job id。
- 通过 Queue + Worker Pool 分离 API 请求和材料计算任务。
- 使用 WebSocket / SSE 推送事件流，避免前端轮询造成压力。
- 大图表使用降采样、分块加载、懒加载和缓存。
- 3D 模型支持 LOD、结构数量限制、代表样本选择；后台 snapshot 在 MVP 作为可选能力，稳定多角度截图进入 V1。

### 安全

- LLM 不直接执行代码，只输出 JSON Plan。
- Tool Registry 是唯一执行入口。
- 文件解析在隔离环境中执行，限制文件大小、压缩包展开大小、路径穿越和超时。
- 用户 LLM Key 使用 BYOK，Secret 加密保存，不进入日志。
- Agent 输入必须区分用户指令、系统策略、Data Profile 和工具文档，防止 Prompt injection。
- 展示结构化 Agent Timeline，不展示隐藏思维链。
- 所有关键事件写入审计日志。

### 扩展性

- 材料对象标准化层预留 pymatgen.Structure、pymatgen.Composition、ASE Atoms、PhonopyAtoms、pandas.DataFrame、phonon band/DOS、trajectory frames。
- Tool Registry 支持工具分类、Schema、Adapter、成本等级、缓存策略、超时和 Artifact 类型。
- 后续可接入 VASP、LAMMPS、Materials Project、OPTIMADE、AiiDA、atomate2 和内部实验数据库。

## 10. 本阶段产出的目标文件

```text
docs/00_PROJECT_GOAL.md
persistent/PROJECT_BRIEF.md
persistent/DESIGN_PROGRESS.md
persistent/TASK_BOARD.md
persistent/ARCHITECTURE_DECISIONS.md
persistent/TOOL_REGISTRY_NOTES.md
persistent/OPEN_QUESTIONS.md
persistent/CHANGELOG.md
```

## 11. 下一阶段任务

Phase 1：产品需求与用户流程。

需要从用户视角定义：

- 用户角色与权限场景。
- 上传数据流程。
- 自然语言分析流程。
- 图表生成流程。
- 3D 模型查看流程。
- Artifact / Recipe / Report 流程。
- 非功能需求与验收标准。
