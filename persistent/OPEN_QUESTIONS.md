# OPEN_QUESTIONS

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
