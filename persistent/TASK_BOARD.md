# TASK_BOARD

## Backlog

## In Progress

无。

## Review Needed

- 人工确认 `.gitignore` 已允许 `docs/` 和 `persistent/` 进入 Git，并在本轮提交中包含这些核心设计文件。
- 人工确认 `docs/13_SHARED_SCHEMA_SPEC.md` 作为实现阶段类型基线，后续 `packages/schemas/` 从该文件派生。
- 人工确认 MVP / V1 工具范围：MVP 为 10 个核心工具，10 个均需注册、校验并可由 Worker 执行；端到端 Demo 至少覆盖 6 个并包含 composition、structure、ml。
- 人工确认 MatterViz snapshot、SVG/PDF high-resolution export 不作为 MVP 阻塞项。
- 人工确认 BYOK 多人项目规则：用户级 Secret 按 job runner 解析，Recipe 不保存具体 SecretRef。
- 人工确认 MVP Secret API 使用 `/me/secrets`，项目级共享 Secret API 推迟到 V1。
- 人工确认 `tool_registry/*.yaml` 作为首批 Tool Registry manifest 来源，并在代码实现阶段优先实现 manifest loader。

## Done

- Phase 0：项目目标与边界定义
- Phase 0 补充：独立系统定位与 pymatviz / MatterViz 能力基线
- Phase 1：产品需求与用户流程
- Phase 2：总体系统架构
- Phase 3：前端工作台设计
- Phase 4：后端服务与数据库设计
- Phase 5：Agent 编排设计
- Phase 6：工具注册表与 Adapter
- Phase 7：数据解析与 Data Profile
- Phase 8：高并发任务系统
- Phase 9：Artifact / Recipe / Report
- Phase 10：用户配置、安全与扩展
- 补充设计文件：专业材料领域扩展
- 复核修正：phonon / trajectory 工具阶段归属
- 逐文件审核：修正 MVP/V1 工具表述并新增文档索引
- Phase 11：MVP Roadmap
- Design Review Fixes：修正 `.gitignore`、新增入口文件、统一共享 Schema、修正 MVP/V1 范围、补充前端组件/状态规格、更新 ADR。
- Implementation Readiness Fixes 2：补全共享 Schema 缺失类型、统一 `artifactTypes`、修正 10 个 MVP 工具冲突、删除 Phase 0 旧 Schema、补充 `job_events.seq`、修正推荐任务阶段标记和 Redis 事实源表述。
- Implementation Readiness Fixes 3：统一 JobEvent status、移除 retry 专用 JobStatus、修正下载格式命名、更新 RecommendedTask 字段、明确 Plotly MVP 推荐输出，并复核 Tool Registry 执行流/Markdown 代码块。
- Implementation Readiness Fixes 4：拆分 MVP 工具实现标准与演示标准、统一 Plotly 交互展示产物口径、对齐 Phase 2 JobEvent/ArtifactRecord、补齐 Phase 4 时间字段和 BYOK API、修正 AgentTimelineEvent status。
- Implementation Readiness Fixes 5：对齐 Phase 1 与 Phase 12 的 MVP 验收和上传格式范围，移除 Phase 6 / Phase 9 Artifact Schema 重复定义，复核 Phase 6 缓存 refresh 条目无重复。
- [x] 新增 pymatviz capability inventory。
- [x] 新增 pymatviz / matterviz / platform builtin manifest。
- [x] 新增 Adapter implementation plan。
- [x] 更新 MVP roadmap，加入 Milestone 0。
- [x] 清理 `tool_registry/1project.lnk` 并忽略 Windows 快捷方式/系统缩略图文件。
- [x] 将 `structure.chem_env_sunburst` 的 manifest 阶段统一为 `v2`，late V1 仅保留为探索备注。
- [x] 更新 ADR-046，使实现顺序与 Milestone 0 一致。

## Next Implementation Backlog

- 建立 repo scaffold：`apps/web`、`apps/api`、`workers`、`packages/schemas`。
- 从 `docs/13_SHARED_SCHEMA_SPEC.md` 建立 `packages/schemas`。
- 实现 Tool Registry manifest loader，加载 `tool_registry/pymatviz_manifest.yaml`、`tool_registry/matterviz_manifest.yaml`、`tool_registry/platform_builtin_manifest.yaml`。
- 实现 `BaseToolAdapter`、Input Resolver、Param Validator、Artifact Exporter 和 Error Normalizer。
- 实现 MVP 前 3 个 Adapter：`composition.ptable_heatmap`、`structure.structure_3d`、`structure.viewer_3d`。
- 建立 PostgreSQL / Redis / MinIO 本地开发环境。
- 实现 Auth / Project / Dataset 基础 schema。
- 实现上传、解析和 Data Profile MVP。
- 实现 Job Queue、SSE 和 Artifact Service。
- 实现三栏式前端工作台基础布局。

## Deferred

无。
