# Phase 11：MVP Roadmap 与开发计划

> Status: HISTORICAL / SUPERSEDED BY POST-J6 PRODUCT ROADMAP
> Current authority: [ROADMAP.md](ROADMAP.md). Historical milestones below are
> retained as design history and do not authorize future work.

## 1. 本阶段目标

将 Phase 0-10 的核心设计和领域扩展补充设计收敛为可执行开发路线，明确 MVP、V1、V2 范围，给出任务拆解、技术栈选择、优先级、风险清单、验收标准和进入代码实现的顺序。

## 2. 本阶段解决的问题

### 产品阶段定义

| 阶段 | 目标 |
|---|---|
| MVP | 打通结构数据 + 预测结果 CSV 的自然语言分析、图表/3D、Artifact、Recipe、Report 闭环 |
| V1 | 系统化工作台：更完整工具、Trajectory/Phonon、分享、PDF、Guided/Expert、RAG |
| V2 | 专业平台版：VASP/LAMMPS、插件市场、团队协作、私有化/K8s、组织级治理 |

### MVP 成功标准

用户能上传 CIF/POSCAR/CSV/ZIP 和 limited JSON，用自然语言提出分析需求，系统生成 Data Profile 和 JSON Plan，执行白名单工具，展示 Plotly / MatterViz 图表、指标表格与 Agent Timeline，并保存 Artifact、Recipe 和 Markdown/HTML Report。

## 3. MVP 范围

### 必须做

| 模块 | MVP 范围 |
|---|---|
| Frontend | 三栏式工作台 + 底部面板 |
| Auth/Project | 登录用户、项目、项目成员 RBAC 基础 |
| Upload/Data | CIF、POSCAR/CONTCAR、CSV、ZIP 容器、JSON limited、XYZ/EXTXYZ 基础 |
| Data Profile | 结构/组成/表格摘要、字段映射、质量问题、推荐任务 |
| Agent | Auto 模式、JSON Plan、Plan Summary、Timeline、Report |
| Tools | 10 个 MVP 工具：ptable_heatmap、elements_hist、chem_sys_treemap、structure_3d、viewer_3d、coordination_hist、density_scatter、error_distribution、basic_metrics、outlier_table |
| Queue | FastAPI + Celery + Redis + SSE JobEvent |
| Storage | PostgreSQL + S3/MinIO + Redis |
| Artifact | Plotly JSON、交互展示产物、PNG preview、MatterViz HTML/metadata、metrics JSON、table JSON/CSV、quality issues JSON、Recipe JSON、Report MD/HTML；MatterViz snapshot 可选 |
| Security | Docker Worker sandbox、用户级 BYOK、Secret 加密、审计、Prompt Guard |

### 明确不做

- 公开分享链接。
- PDF 导出。
- SVG/PDF high-resolution paper export。
- WebSocket 协作。
- Expert JSON Plan 编辑。
- 完整工具文档 RAG。
- phonon / trajectory 完整执行工具。
- VASP / LAMMPS 解析。
- 插件市场。
- Kubernetes / Ray / Temporal 生产级编排。

## 4. V1 范围

- Guided / Expert 模式。
- Tool docs RAG。
- 多模型路由。
- PDF 导出。
- 公开分享和匿名报告链接。
- Dashboard 拖拽布局。
- native MatterViz React 集成评估。
- RDF / XRD / spacegroup / composition clustering。
- phonon band / DOS。
- trajectory viewer。
- 组织级 BYOK。
- Artifact / Recipe diff 和版本树。

## 5. V2 范围

- VASP 输出解析：vasprun.xml、OUTCAR、XDATCAR、DOSCAR。
- LAMMPS dump。
- Materials Project / OPTIMADE / AiiDA / atomate2 集成。
- 插件市场和组织级插件白名单。
- Kubernetes Jobs / Ray / GPU worker。
- 私有化部署和多租户企业治理。
- 团队协作、评论、报告发布。
- 高级材料异常检测：氧化态、电荷平衡、局部环境、结构去重。

## 6. 推荐技术栈

| 层 | MVP 技术 |
|---|---|
| Web | Next.js、React、TypeScript、Tailwind CSS、shadcn/ui |
| Data fetching | TanStack Query、SSE client、Zustand/Jotai |
| Charts | Plotly.js、sandboxed iframe artifact |
| 3D | MatterViz artifact iframe、Plotly structure_3d |
| API | FastAPI modular app |
| Workers | Celery + Redis |
| DB | PostgreSQL |
| Object storage | MinIO / S3-compatible |
| Python materials | pymatviz、pymatgen、ASE、pandas、numpy、plotly |
| LLM | OpenAI-compatible API、BYOK |
| Security | Docker sandbox、envelope encryption |

## 7. 开发任务拆解

### Milestone 0：pymatviz Capability Inventory & Adapter Baseline

目标：在正式实现 API、前端和 Agent 之前，先锁定 pymatviz 能力抽象边界。

任务：

- 新增 `docs/14_PYMATVIZ_CAPABILITY_INVENTORY.md`。
- 新增 `docs/15_ADAPTER_IMPLEMENTATION_PLAN.md`。
- 新增 `tool_registry/pymatviz_manifest.yaml`。
- 新增 `tool_registry/matterviz_manifest.yaml`。
- 新增 `tool_registry/platform_builtin_manifest.yaml`。
- 明确 10 个 MVP 工具分别来自 pymatviz / MatterViz / Plotly custom / platform builtin。
- 明确每个工具的 source function、adapter、artifactTypes、displayTarget、stage。

### Milestone 1：项目骨架与基础设施

- 建立 monorepo 或双仓结构：`apps/web`、`apps/api`、`workers`、`packages/schemas`。
- 配置 PostgreSQL、Redis、MinIO。
- 建立 FastAPI 模块边界。
- 建立 Next.js 工作台 shell。
- 建立基础 Auth / Project / Dataset 表。

### Milestone 2：上传、解析和 Data Profile

- 实现对象存储预签名直传。
- 实现 CIF / POSCAR / CSV / JSON limited / ZIP 容器解析。
- 实现 XYZ/EXTXYZ 基础解析边界：plain XYZ 作为非周期 `Atoms`，含 lattice 的 EXTXYZ 才进入周期结构工具。
- 实现 normalized object 存储。
- 实现 Data Profile 和质量问题。
- 前端左侧 Data Asset Panel 联调。

### Milestone 3：Tool Registry 和 MVP Adapters

- 实现 Tool Registry。
- 实现 Tool Schema 校验。
- 实现 10 个 MVP Tool Executor / Adapter：`ptable_heatmap`、`elements_hist`、`chem_sys_treemap`、`structure_3d`、`viewer_3d`、`coordination_hist`、`density_scatter`、`error_distribution`、`basic_metrics`、`outlier_table`。
- 实现 Artifact Exporter。
- 实现 ToolError 标准化和缓存 key。

### Milestone 4：Job Queue 和事件流

- 实现 jobs、job_events、tool_calls、artifacts。
- 实现 Celery queues：parse/profile/llm/viz/render/export。
- 实现 SSE `/jobs/{id}/events`。
- 前端 Agent Timeline 和 Chart Card 渐进展示。

### Milestone 5：Agent Auto 模式

- 实现 AnalysisRequest。
- 实现 JSON Plan generation。
- 实现 Plan Validator。
- 实现 Execution Controller。
- 实现 Result Explainer 和 Markdown/HTML Report。

### Milestone 6：Artifact / Recipe / Security

- 实现 Artifact 列表、下载 URL、预览。
- 实现 Recipe JSON 保存和重跑。
- 实现用户级 BYOK 和 Secret 加密引用。
- 实现 Docker Worker sandbox。
- 实现 audit logs 和 Prompt Guard。

## 8. 优先级

| Priority | 任务 |
|---|---|
| P0 | 数据上传、解析、Data Profile、Job Queue、Tool Registry、MVP 工具、Artifact |
| P0 | Agent JSON Plan + Plan Validator + Execution Controller |
| P0 | 三栏工作台、SSE Timeline、图表卡片、3D Viewer |
| P1 | Recipe、Report、BYOK、审计、沙箱 |
| P1 | 导出包、缓存、资源限制、错误恢复 |
| P2 | PDF、公开分享、Guided/Expert、RAG、更多材料工具 |

## 9. 风险清单

| 风险 | 影响 | 缓解 |
|---|---|---|
| pymatviz/MatterViz 上游 API 变化 | Adapter 失效 | Adapter 隔离 + 版本锁定 + smoke tests |
| 大文件解析慢 | 用户等待长 | Celery + SSE + 分阶段 profile |
| Plotly 大图卡顿 | 前端体验差 | density/hexbin/预聚合/iframe |
| 3D 大结构卡顿 | 页面冻结 | LOD + bonds 默认关闭 + viewer HTML，snapshot 作为可选预览 |
| LLM 计划错误 | 工具失败 | JSON Schema + Tool Registry + Plan Validator |
| Secret 泄漏 | 高安全风险 | envelope encryption + never log + audit |
| Worker 崩溃 | 任务失败 | PostgreSQL 状态源 + retry + idempotency |
| 范围膨胀 | MVP 延期 | 严格推迟 phonon/trajectory/VASP/LAMMPS 到 V1/V2 |

## 10. MVP 验收标准

- 用户可以创建项目并上传 CIF/POSCAR/CSV/ZIP，且 JSON limited 和 XYZ/EXTXYZ 基础解析有明确边界。
- 系统可以生成 Data Profile，显示结构数量、元素、化学体系、字段映射和质量问题。
- 用户可以输入自然语言分析需求。
- Agent 生成 JSON Plan，并展示 Plan Summary。
- Plan Validator 阻止非法工具、非法参数和无效输入。
- 10 个 MVP 工具均已注册、可通过 Tool Registry 校验并可被 Worker 执行。
- 端到端演示至少覆盖 6 个核心工具，并包含 composition、structure、ml 三类能力。
- metrics/table 类 Artifact 必须在端到端演示中出现。
- 前端通过 SSE 展示 JobEvent 和 Agent Timeline。
- 图表卡片能展示 Plotly Artifact。
- Structure Tab 能展示 3D Viewer Artifact。
- 系统保存 Recipe JSON 和 Report MD/HTML。
- Artifact 下载经过项目权限校验。
- BYOK 不进入日志、prompt、Artifact 或导出包。

## 11. 后续进入代码实现顺序

建议顺序：

0. pymatviz Capability Inventory & Adapter Baseline。
1. repo scaffold。
2. packages/schemas。
3. Tool Registry manifest loader。
4. BaseToolAdapter。
5. MVP 前 3 个 Adapter。
6. Data Pipeline。
7. Job Queue + SSE。
8. Artifact Service。
9. Agent JSON Plan + Validator。
10. 前端三栏工作台。
11. 补齐 10 个 MVP 工具。

## 12. 本阶段产出的目标文件

```text
docs/12_MVP_ROADMAP.md
docs/14_PYMATVIZ_CAPABILITY_INVENTORY.md
docs/15_ADAPTER_IMPLEMENTATION_PLAN.md
tool_registry/pymatviz_manifest.yaml
tool_registry/matterviz_manifest.yaml
tool_registry/platform_builtin_manifest.yaml
persistent/DESIGN_PROGRESS.md
persistent/TASK_BOARD.md
persistent/ARCHITECTURE_DECISIONS.md
persistent/OPEN_QUESTIONS.md
persistent/CHANGELOG.md
```

## 13. 设计阶段完成标准

完成 Phase 11 后，Phase 0-11 的设计文档应全部存在，补充领域扩展文件 `docs/11_MATERIAL_DOMAIN_EXTENSIONS.md` 应覆盖材料专业扩展方向，`persistent/DESIGN_PROGRESS.md` 应标记所有阶段完成，`persistent/TASK_BOARD.md` 应无 In Progress 阶段。后续工作可进入代码实现。
