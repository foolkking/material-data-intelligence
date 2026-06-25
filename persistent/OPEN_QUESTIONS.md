# OPEN_QUESTIONS

## 2026-06-25 Phase 1 Acceptance Follow-ups

- Phase 1 now accepts `preview_png` as a required artifact family, but the MVP implementation may use a minimal valid PNG fallback when Kaleido/Chromium is unavailable. V1 still needs a decision on whether render workers must install and manage Kaleido/Chromium for real chart snapshots.
- Phase 1 product-flow acceptance is currently proven by an in-memory deterministic runtime. Next phase must decide the exact repository/API shape for replacing demo project/dataset/job/artifact state.
- The `/jobs/{job_id}/events/stream` route now exposes an SSE-style boundary without `sse-starlette`. Next phase must decide whether to keep plain `StreamingResponse` or introduce a Starlette-compatible SSE dependency.
- Phase 1 engineering reproducibility is now fixed on `uv.lock` for Python and `apps/web/package-lock.json` for frontend npm installs. Future dependency changes should update those lockfiles in the same commit as dependency declarations.

## Product

- 产品正式名称优先采用 Material Insight Studio、MatViz Agent Platform，还是 LabPilot Materials Workspace？
- V1 是否支持公开分享、匿名报告链接和外部协作者查看？
- V1 是否支持 PDF 报告导出？
- Guided / Expert 模式的最小可用范围是什么？

## Architecture

- 何时从 FastAPI 模块化单体拆分为独立 Data / Agent / Visualization 服务？
- LabPilot 集成时采用 NestJS BFF、API Gateway 代理，还是 iframe / embedded workspace？

## Frontend

- V1 是否支持用户自定义 Dashboard 拖拽布局？
- V1 是否评估 native MatterViz React 集成，替代部分 iframe artifact？
- 3D Viewer 的全屏、截图和结构选择器交互细节如何设计？

## Backend

- V1 分片上传和断点续传的最大文件规模目标是多少？
- Artifact / Recipe 何时需要独立 version tree 和 diff 视图？
- Artifact 生命周期和自动清理策略如何定义？

## Agent

- V1 Expert 模式是否允许用户手动编辑 JSON Plan 后再执行？
- V1 多模型路由按哪些任务类型拆分：Planner、Explainer、Report，还是按成本等级？
- V1 工具文档 RAG 使用 pgvector 还是 Qdrant？

## Materials Domain

- V2 VASP 输出优先解析 vasprun.xml、OUTCAR、XDATCAR 还是 DOSCAR？
- V1 代表结构聚类使用 composition embedding 还是 structure fingerprint？
- V1 首批高级工具优先实现 phonon、trajectory、RDF/XRD，还是 ML error-by-domain？
- V1/V2 外部生态集成优先级如何排序：Materials Project、OPTIMADE、AiiDA、atomate2，还是内部数据库 connector？
- 电子结构工具是否进入 V2 核心范围，还是作为专业插件优先接入？

## Security

- V1 组织级 BYOK 的继承、撤销和预算模型如何设计？
- V1 Prompt injection 模型辅助检测使用哪类评估集？
- V2 是否需要 gVisor / Firecracker / Kubernetes Jobs 等更强隔离？

## Implementation

- MVP 是否接受 `preview_png` 继续保持 optional，还是在 render-worker 里显式安装并管理 Kaleido/Chromium？
- ZIP 安全解包的 MVP 限制值如何定：最大文件数、最大展开大小、最大嵌套层级？
- EXTXYZ with lattice：已决定优先通过 ASE 解析后转 pymatgen Structure，不再单独实现轻量 parser。
- V1/V2 manifest 工具在进入可执行阶段前，是否要求先补齐与 MVP 同等级的 `additionalProperties=false` paramsSchema？
- 下一阶段实现 SSE 时需要选择与 `fastapi 0.115.x` / `starlette 0.46.x` 兼容的 SSE 方案；当前全局环境中的 `sse-starlette 3.4.1` 要求 `starlette>=0.49.1`，不能直接作为项目依赖锁定。
