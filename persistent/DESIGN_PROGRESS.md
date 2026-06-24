# DESIGN_PROGRESS

## 当前阶段

Design Review Fixes 完成；新增 pymatviz Capability Inventory & Adapter Baseline，进入代码实现准备前的工具能力基线锁定

## 已完成阶段

- [x] Phase 0：项目目标与边界定义
- [x] Phase 1：产品需求与用户流程
- [x] Phase 2：总体系统架构
- [x] Phase 3：前端工作台设计
- [x] Phase 4：后端服务与数据库设计
- [x] Phase 5：Agent 编排设计
- [x] Phase 6：工具注册表与 Adapter
- [x] Phase 7：数据解析与 Data Profile
- [x] Phase 8：高并发任务系统
- [x] Phase 9：Artifact / Recipe / Report
- [x] Phase 10：用户配置、安全与扩展
- [x] Phase 11：MVP Roadmap

补充文件：

- [x] `docs/11_MATERIAL_DOMAIN_EXTENSIONS.md`：专业材料领域扩展设计
- [x] `docs/index.md`：文档索引
- [x] `docs/03A_FRONTEND_COMPONENT_SPEC.md`：前端组件规格
- [x] `docs/03B_FRONTEND_STATE_AND_INTERACTION.md`：前端状态与交互规格
- [x] `docs/13_SHARED_SCHEMA_SPEC.md`：共享 Schema 基线
- [x] `docs/14_PYMATVIZ_CAPABILITY_INVENTORY.md`：pymatviz 能力清单与平台 Tool ID 映射
- [x] `docs/15_ADAPTER_IMPLEMENTATION_PLAN.md`：Adapter 实现计划
- [x] `tool_registry/pymatviz_manifest.yaml`：pymatviz 原生能力 manifest
- [x] `tool_registry/matterviz_manifest.yaml`：MatterViz / widget 能力 manifest
- [x] `tool_registry/platform_builtin_manifest.yaml`：平台内置与自定义 Plotly 能力 manifest

当前新增设计重点：

本项目进一步明确为“以 pymatviz 为 primary visualization kernel 的材料数据智能分析与可视化平台”。当前补充了 pymatviz capability inventory、manifest-based tool registry 和 adapter implementation plan。

## 本轮完成

- 创建 `docs/00_PROJECT_GOAL.md`。
- 创建 `persistent/PROJECT_BRIEF.md`。
- 初始化持久化跟踪文件。
- 明确系统是材料数据智能分析与可视化平台，而不是 pymatviz 套壳。
- 明确 LLM 采用 JSON Plan + Tool Registry 的受控执行模式。
- 明确 MVP 优先覆盖文件上传、格式识别、Data Profile、Agent Plan、白名单工具调用、Artifact、Recipe 和报告基础链路。
- 补充独立系统定位：自然语言 + 材料数据文件 -> Plotly / MatterViz 图表、3D 模型、过程展示和可复现 Artifact。
- 补充 pymatviz / MatterViz 数据输入、可视化能力、3D 渲染路线和 MVP 工具集。
- 补充 Adapter 层决策：不 fork 大改 pymatviz，通过 Tool Registry 和 Visualization Service 隔离上游变化。
- 创建 `docs/01_PRODUCT_REQUIREMENTS.md`。
- 完成用户角色、用户故事、上传流程、Data Profile 流程、自然语言分析流程、图表生成流程、3D 模型查看流程、Agent Timeline、Artifact / Recipe / Report 流程定义。
- 明确 Phase 1 产品决策：MVP 仅登录用户、默认 Auto 模式、用户审查计划摘要但不编辑 JSON Plan、报告导出支持 Markdown/HTML。
- 创建 `docs/02_SYSTEM_ARCHITECTURE.md`。
- 明确 MVP 架构：Next.js 前端 + FastAPI 模块化应用 + Celery/Redis Worker + PostgreSQL + S3/MinIO。
- 明确逻辑服务边界：API Gateway、Data Service、Agent Service、Visualization Service、Worker Service、Artifact Service、Storage Layer、Queue Layer、Security Layer。
- 明确所有耗时任务必须通过 Job Queue 异步执行，前端通过 SSE/WebSocket 渐进展示 JobEvent。
- 创建 `docs/03_FRONTEND_WORKSPACE_DESIGN.md`。
- 明确前端采用三栏式工作台 + 底部面板：左侧数据资产、中央可视化画布、右侧 Agent 面板、底部 Logs/Code/Artifacts/Recipe/Warnings。
- 明确 MVP 使用固定响应式 Dashboard，MatterViz / heavy Plotly 优先通过 sandboxed artifact iframe 展示。
- 明确 Agent Plan 默认展示摘要，完整 JSON 和 ToolCall 细节可展开。
- 创建 `docs/04_BACKEND_SERVICE_DESIGN.md`。
- 明确后端模块边界：Auth、Project、Dataset、Profile、Jobs、Agent、Tools、Artifacts、Config、Secrets、Audit、Workers。
- 明确 MVP 上传采用对象存储预签名直传，不做分片/断点续传。
- 明确核心数据库实体、项目级 RBAC、数据隔离、统一错误模型和审计日志边界。
- 创建 `docs/05_AGENT_ORCHESTRATION_DESIGN.md`。
- 明确 Agent 职责：Intent Parser、Data-aware Planner、Tool Selector、Parameter Generator、Result Explainer、Report Writer。
- 明确 Agent 只能输出 JSON Analysis Plan，Execution Controller 校验后创建 ToolCall。
- 明确 MVP 不做自动多模型路由和完整工具文档 RAG；使用项目默认模型和静态 Tool Registry 摘要。
- 明确 Prompt injection 进入 Agent Timeline warning，并可阻止高风险计划执行。
- 创建 `docs/06_TOOL_REGISTRY_AND_ADAPTER.md`。
- 明确 Tool Registry 是唯一执行白名单，Adapter 隔离 pymatviz / MatterViz / Plotly 上游变化。
- 明确 MVP Tool Set、Tool Schema、Artifact 标准、ToolError、缓存 key 和插件扩展机制。
- 明确 MVP Phonon 工具推迟到 V1，当前只保留 Schema 和扩展点。
- 创建 `docs/07_DATA_PIPELINE_DESIGN.md`。
- 明确数据管线流程：格式识别、安全解析、标准化对象、Data Profile、质量检查、推荐任务。
- 明确 MVP 支持 CIF、POSCAR/CONTCAR、XYZ/EXTXYZ 基础解析、CSV、JSON、ZIP；phonon/trajectory 深度支持推迟到 V1，VASP/LAMMPS 推迟到 V2。
- 明确代表 3D 结构 MVP 采用规则采样，composition clustering 推迟到 V1。
- 创建 `docs/08_JOB_QUEUE_AND_CONCURRENCY.md`。
- 明确 MVP 使用 SSE 推送 JobEvent，WebSocket 协作能力推迟到 V1。
- 明确 Worker 按 parse/profile/llm/viz/render/export 队列拆分。
- 明确 PostgreSQL 是 Job/ToolCall/Artifact 状态事实源，Redis 只做 broker/cache/短期状态。
- 明确大数据降采样、3D LOD、资源限制、多用户并发和可观测性策略。
- 创建 `docs/09_ARTIFACT_AND_RECIPE_SYSTEM.md`。
- 明确 Plotly `figure.json`、MatterViz `viewer.html + metadata.json`、Report Markdown、Recipe JSON 的 canonical 地位。
- 明确 Artifact / Recipe / Report 默认不可变，重跑或编辑生成新 version。
- 明确 MVP 不支持公开分享，只支持项目成员访问和授权导出包。
- 创建 `docs/10_USER_CONFIG_AND_SECURITY.md`。
- 明确配置优先级：system defaults < user_config < project_config < recipe/job params。
- 明确 MVP 使用 Docker/容器化 Worker 沙箱，用户级 BYOK，组织级共享 Key 推迟到 V1。
- 明确 Secret envelope encryption、文件安全、Prompt injection MVP 防护、审计日志和插件默认最小权限。
- 创建 `docs/12_MVP_ROADMAP.md`。
- 明确 MVP / V1 / V2 范围、技术栈、开发里程碑、优先级、风险清单、验收标准和进入代码实现顺序。
- Phase 0-11 设计文档全部完成。
- 复核用户给定目标文件清单，补充创建 `docs/11_MATERIAL_DOMAIN_EXTENSIONS.md`。
- 修正 `docs/06_TOOL_REGISTRY_AND_ADAPTER.md` 中 phonon / trajectory 工具阶段归属，使其与 ADR 和 Roadmap 一致：V1 支持 phonon band/DOS 与 trajectory viewer，V2 支持 VASP/LAMMPS、电子结构、生成材料评估和外部生态插件。
- 更新 `docs/12_MVP_ROADMAP.md` 的设计完成标准，纳入 `docs/11_MATERIAL_DOMAIN_EXTENSIONS.md`。
- 完成逐文件审核，创建 `docs/index.md` 作为文档入口。
- 修正 `docs/01_PRODUCT_REQUIREMENTS.md` 中 MVP 示例混入 V1 `structure.spacegroup_bar` 的表述。
- 修正 `docs/03_FRONTEND_WORKSPACE_DESIGN.md` 中 TrajectoryWidget MVP 表述，明确 MVP 仅基于已解析结构集合展示首末帧/抽样帧，不提供完整 trajectory 工具。
- 更新 `persistent/TOOL_REGISTRY_NOTES.md`，补齐 `ml.parity_plot` 的 V1 归属，并区分 V1 phonon/trajectory 与 V2 VASP/LAMMPS。
- 完成 Design Review Fixes：修正 `.gitignore`，确保 `docs/` 和 `persistent/` 进入 Git 版本管理。
- 新增根目录 `README.md`、`AGENTS.md`、`MASTER_PROMPT.md`，作为新会话和 Coding Agent 入口。
- 新增 `docs/13_SHARED_SCHEMA_SPEC.md`，统一 `ArtifactType`、`DisplayTarget`、`ToolCategory`、`ToolDomain`、`ToolInputSchema`、`AnalysisPlan`、`JobEvent`、`Recipe`、`Config` 等跨模块 Schema。
- 新增 `docs/03A_FRONTEND_COMPONENT_SPEC.md` 和 `docs/03B_FRONTEND_STATE_AND_INTERACTION.md`，补齐前端组件树、状态切片、Artifact Loader、全屏/重试/错误态和 SSE 事件投影。
- 统一 MVP/V1 工具范围：MVP 为 composition/structure/ml 的 10 个核心工具；V1 扩展 parity、uncertainty、error-by-domain、phonon、trajectory、RDF/XRD、composition clustering。
- 修正 Tool Registry：`ToolInputSchema` 改为 `inputOptions` 多输入方案，增加 `implementationSource`、`ToolDomain` 和周期性结构约束。
- 增加 `metrics_json`、`table_json`、`table_csv`、`quality_issues_json`，将指标和表格结果作为一等 Artifact。
- 修正 JSON limited、ZIP 容器、plain XYZ / EXTXYZ 与周期结构工具的边界。
- 调整 MatterViz snapshot、SVG/PDF high-resolution export 的阶段归属，MVP 不把这些作为阻塞项。
- 明确 BYOK 多人项目规则：用户级 Secret 按 job runner 解析，Recipe 不保存具体 SecretRef。
- 补充 JobEvent 关键数据库索引和事件/日志保留策略。
- 更新 ADR-027、ADR-042，并新增 ADR-048 至 ADR-057。
- 完成第二轮实现前一致性修正：补全 `docs/13_SHARED_SCHEMA_SPEC.md` 中 `FileProfile`、`ObjectProfile`、`QualityIssue`、`RecommendedTask`、`InputRef`、`ToolExecutionRequest` 和 `Molecule`。
- 统一 `artifactTypes` 命名，移除旧的 format 语义残留。
- 删除 Phase 0 旧 Schema 草案，改为引用 `docs/13_SHARED_SCHEMA_SPEC.md`。
- 修正 Phase 3 `activeTab` 为 `DisplayTarget`，修正 Phase 4 `job_events.seq`，修正 Phase 12 10 个 MVP 工具与 Milestone 3 的冲突。
- 将推荐任务增加 `stage`、`availableNow`、`requiredTools` 和 `reason` 语义，避免 MVP Planner 自动选择 V1 工具。
- 统一 Redis 只作为 broker/cache/transient state 的表述；Celery result backend 若启用也不作为业务事实源。
- 在 `README.md` 增加对外分享压缩包排除 `.git/` 的建议。
- 完成第三轮一致性修正：统一 JobEvent status 为 `info/running/success/warning/error`，移除 retry 专用 JobStatus，修正用户配置导出格式为 download format，确认 Phase 0 只引用共享 Schema，确认 Tool Registry 执行流和 Markdown 代码块无重复/破损。
- 完成第四轮实现前一致性修正：拆分 MVP 10 个工具实现标准与 6 个工具端到端演示标准；统一 Plotly MVP 交互展示产物口径；Phase 2 `JobEvent` 补齐 `seq/progress` 并让 `ArtifactRecord` 引用共享 `Artifact`；Phase 4 表字段补齐索引依赖的时间字段；MVP Secret API 改为用户级 `/me/secrets`，项目级共享 Secret 推迟到 V1；Agent Timeline 状态与共享 `JobEvent.status` 对齐。
- 完成第五轮实现前小修：Phase 1 MVP 验收标准与 Phase 12 完全对齐；Phase 1 上传范围补齐 POSCAR/CONTCAR、JSON limited、XYZ/EXTXYZ 基础解析；Phase 6 / Phase 9 Artifact 元数据改为引用 `docs/13_SHARED_SCHEMA_SPEC.md` 的正式 `Artifact` / `ArtifactMetadata`；复核 Phase 6 缓存策略中 `refresh` 条目无重复。
- 完成 pymatviz 能力抽象基线补充：新增 `docs/14_PYMATVIZ_CAPABILITY_INVENTORY.md`，明确 Level 0-5 能力分层、9 类 pymatviz/MatterViz/Plotly 能力、原始函数到平台 Tool ID 的映射表，以及 3 个 MVP capability 完整示例。
- 新增 `tool_registry/pymatviz_manifest.yaml`、`tool_registry/matterviz_manifest.yaml`、`tool_registry/platform_builtin_manifest.yaml`，将 10 个 MVP 工具来源拆分为 pymatviz、MatterViz、plotly_custom 和 platform_builtin。
- 新增 `docs/15_ADAPTER_IMPLEMENTATION_PLAN.md`，明确 BaseToolAdapter 接口、执行流程、MVP Adapter 实现顺序和测试要求。
- 更新 `docs/06_TOOL_REGISTRY_AND_ADAPTER.md` 与 `docs/12_MVP_ROADMAP.md`，把 manifest-based Tool Registry 和 Milestone 0 纳入正式实现顺序。

## 当前阻塞

无架构方向阻塞。当前设计基线已完成一致性修正，并补齐 pymatviz capability inventory 与 manifest-based Tool Registry 基线；本轮已清理本地快捷方式、统一 `structure.chem_env_sunburst` 为 V2、同步 ADR-046 实现顺序。进入代码实现前仍建议人工确认 `TASK_BOARD.md` 的 Review Needed 清单。

## 下一步

完成人工确认后进入代码实现准备。

下一步可按 `docs/12_MVP_ROADMAP.md` 的更新后实现顺序，先实现 manifest loader、BaseToolAdapter 和前 3 个 MVP Adapter，再建立数据管线、Job Queue、Artifact Service、前端工作台和 Agent Plan 流程。
