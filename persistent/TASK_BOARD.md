# TASK_BOARD

## Backlog

## In Progress

无。

## Review Needed

- 人工确认 `.gitignore` 已允许 `docs/` 和 `persistent/` 进入 Git，并在本轮提交中包含这些核心设计文件。
- 人工确认 `docs/13_SHARED_SCHEMA_SPEC.md` 作为实现阶段类型基线，后续 `packages/schemas/` 从该文件派生。
- 人工确认 MVP / V1 工具范围：MVP 为 10 个核心工具，V1 才加入 parity、uncertainty、error-by-domain、phonon、trajectory、RDF/XRD。
- 人工确认 MatterViz snapshot、SVG/PDF high-resolution export 不作为 MVP 阻塞项。
- 人工确认 BYOK 多人项目规则：用户级 Secret 按 job runner 解析，Recipe 不保存具体 SecretRef。

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

## Next Implementation Backlog

- 建立 repo scaffold：`apps/web`、`apps/api`、`workers`、`packages/schemas`。
- 建立 PostgreSQL / Redis / MinIO 本地开发环境。
- 实现 Auth / Project / Dataset 基础 schema。
- 实现上传、解析和 Data Profile MVP。
- 实现 Tool Registry 与首批 Adapter。
- 实现 Job Queue、SSE 和 Artifact Service。
- 实现三栏式前端工作台基础布局。

## Deferred

无。
