# PROJECT_BRIEF

## 2026-08-01 Phase 10M-1 Complete, Awaiting Verified Archive

The reviewer-approved Phase 10M-1 task is the sole active implementation.
ScientificWorkspace 1.0, WorkspacePanel 1.0, WorkspaceSelectionContext 1.0,
Alembic 0007, repositories, explicit historical Job projection, and additive
metadata APIs are implemented. Workspace stores source
references and durable presentation state only; it has no scientific,
execution, provider, or artifact-payload authority. Corrected implementation
`27c5aa9` passed exact-SHA CI `30705503707`, including service-backed `37
passed, 0 skipped, 0 failed, 0 errors`. Completion-record and queue-archive CI
remain. The Workspace page and Phase 10M-2 remain reviewer-gated.

## 2026-08-01 Current Phase Status

Phase 10L is `COMPLETE / READY_WITH_EXPLICIT_LIMITS`. L5 implementation
`bfc43bd39d7cc2fa319b9e88f9a4d37eec57ee37` and completion record
`e4b0a8f5619cbb1001ef64809db6400729a99d8d` passed exact-SHA CI runs
`30693848581` and `30694747664`. The Agent chain is verified across five
current real-DeepSeek product cases and 40 useful historical Mock/Fake LLM
semantic replays. Queue archive `8f304fa` passed exact-SHA CI run
`30695065220`. Phase 10M-0 is a directly authorized documentation-only audit.
Its sealed proposal and retained evidence are complete at audit/planning commit
`4c5d25e` with exact-SHA CI `30698489359` success; the completion-record CI is
the final audit gate. Phase 10M-1 is not active and remains reviewer-gated.

## 2026-07-27 Canonical Product Brief

### Identity

**Material Data Intelligence & Visualization Platform / 材料数据智能分析与可视化平台**

The platform helps users understand supported material data, discover valid
analyses, express goals in natural language, execute bounded scientific tools,
inspect professional visual results, receive limitation-aware interpretation,
and preserve reproducible Reports and Recipes. It is not a library wrapper,
generic BI/viewer, DFT workflow manager, arbitrary-code Agent, enterprise SaaS
program, deployment product, or plugin marketplace.

### Core Stack

* pymatgen for materials semantics and reviewed scientific transformations.
* ASE for Atoms and trajectory interoperability.
* phonopy for phonon semantics and source conventions.
* pymatviz and Plotly for materials/scientific visualization.
* MatterViz as a selective browser capability source.
* Existing application-owned Three.js/WebGL renderers for structure,
  trajectory, phonon, BZ, and volumetric products.
* LLM Agent for intent, planning, bounded interpretation, and recommendations.
* Tool Registry and Adapters as the strict executable boundary.
* Artifact, Recipe, and Report for provenance, audit, export, and replay.

### Core User Journey

```text
Data -> Profile -> Natural Language -> AnalysisIntent v1
     -> bounded clarification -> Registry/Profile eligibility
     -> capability-aware selection + exact binding
     -> AnalysisPlan 0.1 or bounded dependency-aware AnalysisPlan 0.2
     -> Execute
     -> Visualize -> Interpret -> Report / Recipe
```

### Current Focus and Initial Release Route

Phase 10J-6 is archived and Phase 10K Material Intelligence is complete with
explicit limits. Phase 10L-0 and Phase 10L-1 are archived. Phase 10L-2 has
implemented strict Registry planner metadata, deterministic Profile/Intent
eligibility, eligible-only capability selection, exact parameter provenance,
and an independent validation gate. Phase 10L-3 is archived with additive
AnalysisPlan 0.2, typed Artifact ports, deterministic serial dependency
execution, partial-result records, and Artifact lineage while preserving all
0.1 behavior. Phase 10L-4 implementation is complete at corrected commit
`02a9e33b93f96aa99413dc49ca2dabca652679c9`; exact-SHA CI run `30606774006`
passed Unit, Frontend/browser/build, PostgreSQL/Redis/MinIO, and the zero-skip
service gate. It adds post-execution ScientificEvidenceBundle 1.0 projection,
deterministic and strict-provider interpretation, grounded claims, immutable
persistence, and an additive findings/evidence UI without changing Plan,
Runtime, Registry, Job, or Artifact execution authority. Completion record
`45af09e` passed exact-SHA CI run `30607509775`; verified queue archive
`58ee943` passed exact-SHA CI run `30608078520`. Phase 10L-5 subsequently
closed the five natural-language evidence cases, froze new real LLM calls to
DeepSeek with `DEEPSEEK_KEY` as the only key source, and was archived at
`8f304fa`. The remaining initial-release route is:

```text
10K Material Intelligence
 -> 10L Intelligent Analysis Agent
 -> 10M Unified Scientific Workspace
 -> 10N Professional Scientific Completion
 -> 11 Scientific Validation
 -> 12 Final Product Closure
```

Professional completion includes CrystalNN/VoronoiNN, local environments and
polyhedra, experimental XRD comparison, basic trajectory analytics, and
Electronic Band/DOS. Fermi Surface is Future Scope, not an initial blocker.

### Phase 10L-5 Live Closure State

The five frozen natural-language cases have been replayed through the real
DeepSeek provider using `DEEPSEEK_KEY` only. Dataset, structure, ML, phonon
dependency, and volumetric cases all reached persisted Plan/Job, Runtime
artifacts, grounded interpretation, and PASS. The suite used 16 real calls in
total, with an independent maximum of 12 per case and no other real provider.
The repository-wide historical audit additionally replayed 40 useful
browser/Mock-LLM semantic cases through the current canonical path: 45/45
passed with 92 supplemental real DeepSeek calls. Pure browser-only checks,
deterministic negative/security fixtures, infrastructure-only phases, and
superseded tools remain explicitly excluded rather than misreported as live
LLM coverage; see the historical replay matrix.
Default CI remains real-call-free. The L5 lifecycle is closed. Phase 10M-0 now
seals a one-Workspace-per-Job proposal; Phase 10M implementation remains
reviewer-gated.

Canonical authority:

* `docs/ROADMAP.md`
* `docs/01_PRODUCT_REQUIREMENTS.md`
* `docs/CAPABILITY_STATUS_MATRIX.md`
* `docs/FUTURE_SCOPE.md`
* `docs/NOT_PLANNED_SCOPE.md`

The historical detail below is retained for implementation context. Where it
conflicts with the canonical documents above, the canonical documents govern.

## 2026-07-05 Current UI Baseline

Phase 9C updates the frontend product direction to an AI analysis assistant
workspace:

```text
Top global context bar
  -> current dataset, profile status, model/provider status, job status,
     dataset/model configuration dialogs, and system settings

Left data-context viewer
  -> resizable/collapsible dataset/profile viewer adapted to table,
     structure, composition, archive, and unsupported/partial inputs

Main workspace
  -> exactly one active tab among Agent 过程, 对话与 Plan, 结果与导出
```

There is no independent right-side Result Inspector in the current design
baseline. Reports, 3D material views, metrics, table summaries, Artifact
Gallery, Recipe/provenance, export, and downloads belong to the main
`结果与导出` tab.

This UI direction does not change the platform execution boundary: LLMs still
produce JSON AnalysisPlans only, valid plans still pass PlanValidator and
persistence, and executable work still goes through QueueWorkerRuntime, Tool
Registry, and Adapter execution.

## 项目名称

材料数据智能分析与可视化平台

## 一句话目标

通过自然语言输入和材料数据文件上传，自动完成材料数据解析、智能分析规划、交互式 Plotly 图表和 MatterViz / pymatviz 3D 材料模型生成，并展示可审计执行过程、工具调用、参数、代码、日志、Artifact 和报告。

## 核心定位

本系统不是 pymatviz 的简单套壳，而是面向材料科学、材料机器学习、晶体结构分析、科研复现和数据集探索的智能分析与可视化平台。

## 独立系统定义

本项目应作为一个可独立运行的系统建设，也可以后续作为 LabPilot / ResearchOps 平台中的材料数据子系统集成。系统主流程是：

```text
自然语言分析需求 + 材料数据文件
  -> 数据解析与材料对象标准化
  -> Data Profile
  -> Agent 生成可校验分析计划
  -> Tool Registry 调用 pymatviz / MatterViz / Plotly 等白名单工具
  -> 交互式图表、3D 结构模型、Artifact、Recipe、报告和执行过程展示
```

核心产品不是“LLM 写 Python 调 pymatviz”，而是一个受控、可审计、可复现的材料数据分析工作台。

## 核心能力

- 多格式材料数据上传与解析。
- 材料对象标准化。
- Data Profile 自动生成。
- LLM Agent 分析计划。
- Tool Registry + JSON Plan 安全工具调用。
- pymatviz / MatterViz / Plotly 图表和 3D 模型生成。
- 异步任务和高并发 Worker。
- Artifact / Recipe / Report 管理。
- 用户配置、LLM Key、权限和安全。
- 专业材料领域插件化扩展。
- 共享 Schema 基线，统一前端、后端、Worker、Agent 与 Tool Registry 的核心类型。

## MVP 边界快照

- 数据输入：CIF、POSCAR/CONTCAR、CSV、ZIP 容器、JSON limited、XYZ/EXTXYZ 基础支持。
- JSON limited：pymatgen Structure JSON、Materials Project-like structure dict、simple table JSON。
- plain XYZ：作为非周期 `Atoms` / molecule-like 对象；只有带 lattice 的 EXTXYZ 才可进入周期结构工具。
- MVP 工具：composition/structure/ml 的 10 个核心工具，包含 density scatter、error distribution、basic metrics 和 outlier table。
- V1 扩展：parity plot、uncertainty calibration、error by element/chemical system、phonon、trajectory、RDF/XRD、composition clustering。
- MatterViz：MVP 必需 `viewer.html` + `metadata.json` + `recipe.json`，snapshot 为可选。

## pymatviz / MatterViz 的角色

- 本项目是一个以 `janosh/pymatviz` 为 primary visualization kernel，以 MatterViz 为 3D / widget 展示内核，以 pymatgen / ASE / phonopy 为材料对象解析内核，以 Tool Registry + Adapter 为 LLM-friendly 能力抽象层，以 Agent JSON Plan 为自然语言规划层，以 Artifact / Recipe / Report 为可复现分析资产层，以 Phase 9C AI 分析助手工作台为用户交互层的材料数据智能分析与可视化平台。
- pymatviz：材料信息学可视化工具层，负责周期表图、组成聚类、结构 2D/3D、RDF、XRD、配位、声子、机器学习评估图等。
- MatterViz：浏览器端材料科学交互 UI 和 3D / trajectory viewer 能力来源。
- Plotly：交互式图表、HTML、JSON 和图片导出的主要图表载体。
- pymatgen / ASE / phonopy / pandas：材料对象、结构对象、轨迹、声子和表格数据的语义基础。
- 平台自身：负责上传、解析、Profile、Agent Plan、工具校验、任务队列、Artifact、Recipe、权限、安全和前端工作台。

## 不做什么

- 不做 DFT / MD 计算引擎。
- 不做无限制任意代码执行平台。
- 不让 LLM 绕过 Tool Registry 直接运行系统命令。
- 不展示模型原始隐藏思维链。
- 不把平台降级为单一可视化库的 Web UI。

## 默认技术栈

| 层 | 默认选择 |
|---|---|
| 前端 | Next.js、React、TypeScript、Tailwind CSS、shadcn/ui、Plotly.js、MatterViz、TanStack Query、Zustand/Jotai、WebSocket/SSE |
| 后端 | FastAPI 或 NestJS、PostgreSQL、Redis、S3/MinIO、Celery/Dramatiq/Temporal |
| Python 材料服务 | pymatviz、pymatgen、ASE、phonopy、matminer、pandas、numpy、scikit-learn、plotly |
| Agent / LLM | OpenAI-compatible API、BYOK、Tool Calling、JSON Schema Validation、内部工具文档 RAG |

## 长期约束

- Agent 只生成结构化 JSON Plan，系统校验后执行。
- 所有工具调用必须经过 Tool Registry 和 Schema 校验。
- 所有耗时任务必须异步执行。
- Artifact、Recipe、日志、参数和报告必须可追踪、可审计、可复现。
- 用户配置、Secret、权限和审计从平台第一版设计开始纳入。
- 材料领域扩展必须通过稳定工具接口和 Adapter 接入。
- 不 fork 大改 pymatviz；优先通过 `pymatviz-agent-adapter` 和 Visualization Service 隔离上游变化。
- 实现阶段以 `docs/13_SHARED_SCHEMA_SPEC.md` 作为类型基线，未来 `packages/schemas/` 从该文件拆分 JSON Schema、TypeScript 类型和 Python Pydantic model。
- 新会话应优先阅读 `README.md`、`AGENTS.md`、`MASTER_PROMPT.md`、`docs/index.md` 和 `persistent/` 文件。

## 当前阶段

Phase 0-11 核心设计阶段已完成，`docs/11_MATERIAL_DOMAIN_EXTENSIONS.md` 作为专业材料领域扩展补充文件已补齐；Design Review Fixes 已补充共享 Schema、前端组件/状态规格和实现前一致性修正。

下一阶段：按 `docs/12_MVP_ROADMAP.md` 进入代码实现准备。
