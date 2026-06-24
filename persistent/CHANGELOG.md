# CHANGELOG

## 2026-06-24

### Added

- 创建 `docs/10_USER_CONFIG_AND_SECURITY.md`。
- 创建 `docs/index.md`。
- 创建 `docs/11_MATERIAL_DOMAIN_EXTENSIONS.md`。
- 创建 `docs/12_MVP_ROADMAP.md`。
- 创建 `README.md`、`AGENTS.md`、`MASTER_PROMPT.md` 作为仓库入口和 Agent 工作规则。
- 创建 `docs/03A_FRONTEND_COMPONENT_SPEC.md`。
- 创建 `docs/03B_FRONTEND_STATE_AND_INTERACTION.md`。
- 创建 `docs/13_SHARED_SCHEMA_SPEC.md`。
- 新增 ADR-041：MVP Worker 沙箱采用 Docker/容器隔离，进程级隔离不足。
- 新增 ADR-042：MVP 支持用户级 BYOK，组织级共享 Key 推迟到 V1。
- 新增 ADR-043：Secret 使用 envelope encryption，明文不进入日志、prompt、Artifact 或导出包。
- 新增 ADR-044：Prompt injection MVP 使用规则检测 + 上下文隔离 + Plan Validator。
- 新增 ADR-045：插件默认无网络、无 Secret、无 shell，必须显式声明能力。
- 新增 ADR-046：MVP 实现顺序按“数据闭环优先于高级功能”。
- 新增 ADR-047：专业材料领域扩展单独成文，但不改变 MVP 实现顺序。
- 新增 ADR-048：`docs/` 和 `persistent/` 必须进入 Git 版本管理。
- 新增 ADR-049：统一 ArtifactType / DisplayTarget / ToolCategory / ToolDomain。
- 新增 ADR-050：ToolInputSchema 使用 inputOptions 表达 OR 输入。
- 新增 ADR-051：MVP table/metrics artifact 是一等产物。
- 新增 ADR-052：plain XYZ 不进入周期性结构工具，除非有 lattice。
- 新增 ADR-053：MVP MatterViz snapshot 可选，viewer.html + metadata.json 为必需。
- 新增 ADR-054：Redis 不作为任务事实源，PostgreSQL 是唯一状态源。
- 新增 ADR-055：用户级 BYOK 按 job runner 解析，不写入 Recipe。
- 新增 ADR-056：V1 phonon 优先支持 phonopy.yaml + band.yaml，DOS 第二批。
- 新增 ADR-057：V1 composition clustering 默认 Magpie + PCA baseline，UMAP 可选。

### Changed

- 将设计进度推进到 Phase 11：MVP Roadmap。
- 将 Phase 10 标记为完成。
- 将 Phase 11 移入任务看板 In Progress。
- 将 Phase 11 标记为完成。
- 将设计阶段标记为完成，下一步进入代码实现准备。
- 根据目标文件清单补齐专业材料领域扩展文件。
- 修正 `docs/06_TOOL_REGISTRY_AND_ADAPTER.md` 中 phonon / trajectory 工具阶段归属，与 ADR 和 Roadmap 保持一致。
- 更新 `docs/12_MVP_ROADMAP.md` 的设计完成标准，纳入 `docs/11_MATERIAL_DOMAIN_EXTENSIONS.md`。
- 完成逐文件审核，修正产品需求和前端设计中的 MVP/V1 工具表述。
- 更新 `persistent/PROJECT_BRIEF.md`、`persistent/DESIGN_PROGRESS.md`、`persistent/TASK_BOARD.md` 和 `persistent/TOOL_REGISTRY_NOTES.md`，记录领域扩展补充文件和逐文件审核结果。
- 修正 `.gitignore`，确保 `docs/` 和 `persistent/` 被 Git 跟踪。
- 统一 MVP/V1 工具范围：MVP 为 10 个核心工具，V1 扩展 parity、uncertainty、error-by-domain、phonon、trajectory、RDF/XRD。
- 将 `ToolInputSchema` 改为 `inputOptions` 多输入方案，并增加 `implementationSource`、`ToolDomain` 和 `periodicity` 约束。
- 将 `metrics_json`、`table_json`、`table_csv`、`quality_issues_json` 纳入 Artifact 类型。
- 修正 JSON limited、ZIP 容器、plain XYZ / EXTXYZ 与周期结构工具边界。
- 调整 MatterViz snapshot、SVG/PDF high-resolution export 的阶段归属。
- 补充 JobEvent 数据库索引、事件保留和日志保留策略。
- 修改 BYOK 规则：用户级 Secret 按 job runner 解析，Recipe 只保存 provider 能力需求。

### Decisions

- 配置优先级为 system defaults < user_config < project_config < recipe/job params。
- MVP 使用 Docker/容器化 Worker 沙箱。
- MVP BYOK 只支持用户级，组织级共享 Key 推迟到 V1。
- 插件默认最小权限，并通过 Tool Registry 和沙箱执行。
- 明确 MVP / V1 / V2 范围、开发里程碑、优先级、风险和验收标准。
- 明确领域扩展阶段：V1 支持 phonon band/DOS 与 trajectory viewer，V2 支持 VASP/LAMMPS、电子结构、生成材料评估和外部生态插件。

## 2026-06-23

### Added

- 创建 `docs/00_PROJECT_GOAL.md`。
- 创建 `docs/01_PRODUCT_REQUIREMENTS.md`。
- 创建 `docs/02_SYSTEM_ARCHITECTURE.md`。
- 创建 `docs/03_FRONTEND_WORKSPACE_DESIGN.md`。
- 创建 `docs/04_BACKEND_SERVICE_DESIGN.md`。
- 创建 `docs/05_AGENT_ORCHESTRATION_DESIGN.md`。
- 创建 `docs/06_TOOL_REGISTRY_AND_ADAPTER.md`。
- 创建 `docs/07_DATA_PIPELINE_DESIGN.md`。
- 创建 `docs/08_JOB_QUEUE_AND_CONCURRENCY.md`。
- 创建 `docs/09_ARTIFACT_AND_RECIPE_SYSTEM.md`。
- 创建 `persistent/PROJECT_BRIEF.md`。
- 创建 `persistent/DESIGN_PROGRESS.md`。
- 创建 `persistent/TASK_BOARD.md`。
- 创建 `persistent/ARCHITECTURE_DECISIONS.md`。
- 创建 `persistent/TOOL_REGISTRY_NOTES.md`。
- 创建 `persistent/OPEN_QUESTIONS.md`。
- 创建 `persistent/CHANGELOG.md`。
- 补充独立系统定位：自然语言输入 + 材料数据文件 -> 交互式图表、3D 结构模型、过程展示和 Artifact。
- 补充 pymatviz / MatterViz / Plotly / pymatgen / ASE / phonopy 的平台内角色。
- 补充数据类型到可视化工具的映射表。
- 补充 MVP Tool Set 和 V1/V2 扩展工具边界。
- 补充 3D 渲染路线：Plotly `structure_3d` 与 MatterViz `StructureWidget` / `TrajectoryWidget`。
- 新增 ADR-003、ADR-004、ADR-005。
- 新增 ADR-006：MVP 默认 Auto 模式，Guided / Expert 推迟到 V1。
- 新增 ADR-007：MVP 只支持登录用户，公开分享推迟到 V1。
- 新增 ADR-008：前端产品形态是材料工作台，不是普通聊天页。
- 新增 ADR-009：MVP API 采用 FastAPI，保留 NestJS / LabPilot BFF 集成边界。
- 新增 ADR-010：MVP 采用模块化单体 + 独立 Celery Worker。
- 新增 ADR-011：MVP 异步任务采用 Celery + Redis，复杂编排后续升级 Temporal。
- 新增 ADR-012：PostgreSQL / S3-MinIO / Redis 三层存储职责。
- 新增 ADR-013：MatterViz 和重型 Plotly HTML 通过 sandboxed artifact iframe 展示。
- 新增 ADR-014：MVP Dashboard 使用固定响应式布局，拖拽布局推迟到 V1。
- 新增 ADR-015：Agent Plan 默认摘要展示，完整 JSON 可展开。
- 新增 ADR-016：Code 面板展示脱敏复现代码和 Recipe。
- 新增 ADR-017：MVP 上传采用对象存储预签名直传，分片/断点续传推迟到 V1。
- 新增 ADR-018：Artifact 和 Recipe 使用不可变记录 + version 字段。
- 新增 ADR-019：权限模型采用组织 + 项目 RBAC。
- 新增 ADR-020：API 错误采用统一 Problem Details 风格。
- 新增 ADR-021：Agent 只能输出 JSON Analysis Plan，不能执行代码。
- 新增 ADR-022：MVP 使用单模型配置，不做自动多模型路由。
- 新增 ADR-023：MVP 不做完整工具文档 RAG，使用版本化 Tool Registry 摘要。
- 新增 ADR-024：Prompt injection 进入 Timeline warning，并阻止高风险计划。
- 新增 ADR-025：MVP 工具参数 Schema 手写维护，V1 再评估半自动生成。
- 新增 ADR-026：Plotly 工具必须输出 `figure.json`。
- 新增 ADR-027：MatterViz 工具输出 `viewer.html` + `metadata.json`，snapshot 可选。
- 新增 ADR-028：Phonon / trajectory 高级工具推迟到 V1。
- 新增 ADR-029：Data Profile 必须由确定性解析管线生成，Agent 不直接猜文件内容。
- 新增 ADR-030：MVP 不执行 phonon 分析，保留识别和 Schema 扩展点。
- 新增 ADR-031：VASP 输出和 LAMMPS dump 推迟到 V2。
- 新增 ADR-032：代表性 3D 结构 MVP 使用规则采样，聚类代表点推迟到 V1。
- 新增 ADR-033：MVP 使用 SSE 推送 JobEvent，WebSocket 推迟到 V1。
- 新增 ADR-034：Worker 按任务类型拆分队列。
- 新增 ADR-035：PostgreSQL 是任务状态事实源，Redis 只做 broker/cache/短期状态。
- 新增 ADR-036：大数据图表和 3D 模型默认启用降采样与 LOD。
- 新增 ADR-037：Artifact、Recipe、Report 默认不可变，重跑生成新版本。
- 新增 ADR-038：Report Markdown 是 canonical，HTML 是派生产物，PDF 推迟到 V1。
- 新增 ADR-039：MVP 不支持公开分享，只支持项目成员访问和授权导出。
- 新增 ADR-040：Job export package 异步生成，且必须脱敏。

### Changed

- 将设计进度推进到 Phase 1：产品需求与用户流程。
- 将 Phase 0 标记为完成。
- 明确不 fork 大改 pymatviz，采用 Adapter + Visualization Service 隔离上游变化。
- 明确前端展示 Agent Timeline，不展示原始隐藏思维链。
- 将设计进度推进到 Phase 2：总体系统架构。
- 将 Phase 1 标记为完成。
- 将 Phase 2 移入任务看板 In Progress。
- 将设计进度推进到 Phase 3：前端工作台设计。
- 将 Phase 2 标记为完成。
- 将 Phase 3 移入任务看板 In Progress。
- 将设计进度推进到 Phase 4：后端服务与数据库设计。
- 将 Phase 3 标记为完成。
- 将 Phase 4 移入任务看板 In Progress。
- 将设计进度推进到 Phase 5：Agent 编排设计。
- 将 Phase 4 标记为完成。
- 将 Phase 5 移入任务看板 In Progress。
- 将设计进度推进到 Phase 6：工具注册表与 Adapter。
- 将 Phase 5 标记为完成。
- 将 Phase 6 移入任务看板 In Progress。
- 将设计进度推进到 Phase 7：数据解析与 Data Profile。
- 将 Phase 6 标记为完成。
- 将 Phase 7 移入任务看板 In Progress。
- 将设计进度推进到 Phase 8：高并发任务系统。
- 将 Phase 7 标记为完成。
- 将 Phase 8 移入任务看板 In Progress。
- 将设计进度推进到 Phase 9：Artifact / Recipe / Report。
- 将 Phase 8 标记为完成。
- 将 Phase 9 移入任务看板 In Progress。
- 将设计进度推进到 Phase 10：用户配置、安全与扩展。
- 将 Phase 9 标记为完成。
- 将 Phase 10 移入任务看板 In Progress。

### Fixed

- 无。

### Decisions

- 系统定位为材料数据智能分析与可视化平台，而不是 pymatviz 套壳。
- LLM 不直接执行任意代码；采用 JSON Plan + Tool Registry + Schema 校验的受控执行模式。
- MVP 优先覆盖文件上传、格式识别、Data Profile、Agent JSON Plan、白名单工具调用、Plotly/MatterViz Artifact、Recipe/Report 基础链路。
- 项目按独立系统设计，同时保留后续作为 LabPilot / ResearchOps 子系统集成的能力。
- MVP 默认 Auto 模式；用户可审查计划摘要，但不直接编辑 JSON Plan。
- MVP 仅支持登录用户和项目成员访问；公开分享推迟到 V1。
- MVP 报告导出支持 Markdown / HTML；PDF 推迟到 V1。
- MVP 架构采用 Next.js 前端 + FastAPI 模块化应用 + Celery/Redis Worker + PostgreSQL + S3/MinIO。
- 所有耗时任务必须异步执行，通过 JobEvent 推送进度。
- Redis 不作为唯一持久化状态源，Job/ToolCall/Artifact 状态必须落 PostgreSQL。
- 前端采用三栏式工作台 + 底部面板。
- MVP 使用固定响应式 Dashboard，不做拖拽自定义布局。
- Code 面板只展示脱敏复现代码和 Recipe，不展示 Worker 内部脚本。
- MVP 上传采用对象存储预签名直传，不做分片/断点续传。
- Artifact、Recipe、Report 采用不可变记录和 version 字段。
- 后端权限以 organization + project RBAC 为基础。
- Agent 只负责计划、解释和报告；执行必须经过 Execution Controller。
- MVP 使用项目默认模型，不做自动多模型路由。
- MVP 不做完整工具文档 RAG，先使用版本化 Tool Registry 摘要。
- Tool Registry 是 Agent 可执行能力的唯一白名单。
- MVP Tool Set 固定为 composition / structure / ml 的核心 8 个工具。
- Adapter 负责输入校验、上游调用、Artifact 输出、错误标准化和缓存。
- Agent 规划必须基于 Data Profile，不能直接猜文件内容。
- MVP 数据解析聚焦结构文件、CSV/JSON 和 ZIP；phonon/trajectory 深度支持后移。
- 代表性 3D 结构 MVP 使用规则采样。
- MVP 使用 SSE 作为任务进度事件流。
- Worker Pool 按 parse/profile/llm/viz/render/export 分队列。
- 大数据图表和 3D 模型默认启用降采样和 LOD。
- Plotly `figure.json`、MatterViz `viewer.html + metadata.json`、Report Markdown、Recipe JSON 是 canonical 产物。
- MVP 不支持公开分享，导出包异步生成且必须脱敏。
- 共享 Schema 是实现阶段的类型基线，未来 `packages/schemas/` 应从该文件拆分 JSON Schema、TypeScript 类型和 Python Pydantic model。
