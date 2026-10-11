# Project State

**状态日期：2026-10-12**
**仓库：** E:\1project\mdi-b0-5a1
**当前分支：** codex/scientific-workspace-20261012

本文件只记录当前产品、架构、运行边界和经过核对的状态。两份按序号对应的交接文档负责产品能力与剩余目标：

- [CAPABILITIES.md](CAPABILITIES.md)：当前已有能力、证据和边界。
- [REMAINING_WORK.md](REMAINING_WORK.md)：完整目标中仍待完成的项目、完成标准和接手顺序。
- [README.md](README.md)：安装、启动、测试和仓库入口。
- [AGENTS.md](AGENTS.md)：开发、安全、数据保护和运行规则。

## 当前结论

MDI 是一个受控的材料科学工作台：用户管理项目和数据，选择精确版本，提交异步 Research，查看保存的科学结果和证据，并生成可复现报告。当前已完成一批跨结构、轨迹、电子、声子、XRD、RDF、体数据、参数化参考和报告导出的实现与代表性验收；完整产品目标仍未结束，主要剩余工作是全站 UX/响应式收口、61 份真实样例的格式到报告闭环，以及浏览器实际文件落盘验收。详见 REMAINING_WORK.md，不要从旧历史段落推导状态。

## 架构和数据流

Next.js 前端调用 FastAPI。FastAPI 将身份、项目、数据集、对象版本、Research Turn、Analysis Plan、Job、Result、Interpretation 和 Report 的权威状态写入 PostgreSQL；科学原件和结果 payload 由 MinIO 保存；Redis/RQ 驱动异步队列；一个物理 Worker 消费六个逻辑队列。工具必须先通过 Tool Registry、schema 和受控 adapter，产品 LLM 不获得任意 Python、shell、文件或网络执行权。

AnalysisPlan 0.3 支持精确多数据集来源；AnalysisPlan 0.4 支持不预先上传材料的 PROJECT 级能力。结果投影、事实、解释和报告都重新校验保存的输入、工具调用、artifact 和来源版本。

当前合同规模是 69 个注册工具、38 个 active research requirements。迁移链当前包含追加式 0038_user_model_connections；它保留历史 personal 连接并支持独立的多连接身份。

## 当前运行拓扑

本机项目服务由 scripts\dev.ps1 管理，保持运行：

| 服务 | 当前端口/状态 |
|---|---|
| PostgreSQL | 127.0.0.1:15434，项目显式端口覆盖 |
| Redis | 127.0.0.1:6380 |
| MinIO API/Console | 127.0.0.1:9000/9001 |
| FastAPI | 127.0.0.1:8005 |
| Next.js | 127.0.0.1:3023 |
| RQ Worker | 1 个物理进程，6 个逻辑队列 |

55434 是跨机器默认值；此主机使用 15434。不要把系统 PostgreSQL 5432 或 Redis 6379 当作 MDI 依赖。项目浏览器页和 65103 报告预览也应跨工作轮次保留。

## 数据、运行态与临时目录

当前配置文件在仓库外的 E:\1project\mdi-b0-5a1.local\local.env，不进入 Git：

| 内容 | 实际位置 |
|---|---|
| PostgreSQL 数据目录 | E:\1project\mdi-b0-5a1.local\data\postgres |
| MinIO 数据目录及 bucket | E:\1project\mdi-b0-5a1.local\data\minio\mdi-artifacts |
| 受控 artifact 工作目录 | E:\1project\mdi-b0-5a1.local\data\artifacts |
| Redis 运行数据目录 | E:\1project\mdi-b0-5a1.local\data\redis |
| PID、服务状态、Redis 配置 | E:\1project\mdi-b0-5a1.local\run |
| API/Worker/存储/前端日志 | E:\1project\mdi-b0-5a1.local\logs |
| 用户指定临时根 | C:\Users\86182\Desktop\wkkk |
| 61 份真实样例 | C:\Users\86182\Desktop\材料智能体平台_完整61测试数据 |

MDI_TEMP_ROOT、TEMP、TMP、TMPDIR 指向 wkkk；测试 scratch 使用其 pytest 子目录并保持编号隔离。临时根不是权威数据库，也没有把现有服务数据迁移到那里。用户输入、模型连接密钥和运行凭据只从外部 local.env/服务存储读取，不写入文档、prompt、artifact 或报告。

## 已验证的当前基线

以下是本次文档整理前最新源代码检查记录，文档改动本身不改变产品运行逻辑：

- 后端相关回归：320 passed, 1 skipped；更广相关后端组也已通过。
- 前端相关回归：500 项检查通过。
- 前端 typecheck 通过，隔离 production build 通过。
- 真实 Si CrystalNN 局域多面体：两次受控工具调用、位点 0 的四近邻和四面体；在线报告及 ZIP 的原件、校验和、相对链接通过。
- 真实无材料、跨数据集、结构/轨迹/电子/声子/XRD/体数据和多类报告流程已有代表性验收。

这些数字不是全项目永远不变的计数；提交后以 CI 结果和当前命令重新核对。

## 保留的已知未完成项

1. 全站 Projects、Data、Research、Reports、Tasks、Account、模型设置和 Admin 的最终 UX/响应式/键盘走查。
2. 61 份样例的格式、解析、查看器、Research、回答、报告和导出矩阵。
3. 各真实科学数据族的完整图形、大尺寸、选择、刷新和损坏状态回归。
4. 内置浏览器原生 ZIP/PNG 文件落盘事件的可检查证据；服务器 HTTP 下载成功不等于该项完成。
5. 所有被接受 Research 消息的统一端到端终态回归。

不要重新执行已经取代的 M6、运行时迁移、前端源码架构迁移或仓库治理基线。不要删除真实数据、外部运行目录、用户浏览器页或临时根中的其他任务目录。

## 文档治理

历史阶段流水账不再作为当前事实源。新的功能应更新代码、测试和对应的能力或交接条目；只有架构、运行方式、重要产品状态变化时才更新本文件或 README。GitHub CI 的 workflow 在 .github/workflows/ci.yml，只运行不依赖真实服务和凭据的后端、前端检查。
