# Project State

**状态日期：2026-10-12** · **主分支：master**

本文件记录当前产品、架构和运行边界，不记录个人机器路径或历史阶段流水账。

- [CAPABILITIES.md](CAPABILITIES.md)：当前能力、证据与限制。
- [REMAINING_WORK.md](REMAINING_WORK.md)：完整目标的剩余项、完成标准和接手顺序；与能力文档的 1–14 项对应。
- [README.md](README.md)：唯一安装、配置、升级、数据备份和检查入口。
- [AGENTS.md](AGENTS.md)：工程安全、工作区与进程约束。

## 当前产品

MDI 是受控材料科学工作台：用户管理项目和数据，选择精确版本，提交异步 Research，查看保存结果和证据，并生成可复现报告。代表性结构、轨迹、电子、声子、XRD、RDF、体数据、参数化参考及报告流程已经验证；完整目标仍未结束。

当前合同规模：**69 个注册工具、36 个研究能力、38 个 active requirements**。三者属于不同执行层，不等于文件格式覆盖率。AnalysisPlan 0.3 支持精确多数据集来源，0.4 支持无需上传材料的 PROJECT 级能力。迁移链最新为追加式 `0038_user_model_connections`，保留既有个人模型连接。

## 架构与权威数据

Next.js 调用 FastAPI；PostgreSQL 保存身份、项目、科学对象版本、Research Turn、Plan、Job、结果、解释和报告的权威状态；MinIO 保存上传原文件与科学 payload；Redis/RQ 驱动一个物理 Worker 消费六个逻辑队列。

工具调用必须经过 Registry、schema 与受控 adapter。产品模型没有任意 Python、shell、文件或网络执行权。结果投影、事实、解释及报告重新校验保存输入、调用、artifact 和精确来源。UI 可展示结构化过程与证据，不展示隐藏思维链。模型连接密钥在服务端加密，不进入提示词、日志和导出。

## 运行与首次安装

已支持的本地控制器是 Windows PowerShell 7 的 `scripts/dev.ps1`，配置在仓库外 `<checkout-name>.local/local.env`；自定义根使用 `MDI_LOCAL_ROOT`。默认端口为 PostgreSQL 55434、Redis 6380、MinIO 9000/9001、API 8005、Web 3023，实际以外部配置为准。Next.js 输出由 `MDI_NEXT_DIST_DIR` 配置，控制器用项目内相对目录映射到仓库外，避免多个 checkout 共用缓存。

- `init`：从 `.env.example` 在外部根生成 `local.env`，写入随机首次凭据、固定加密密钥和所有本地路径；已有配置保持原样。
- `doctor`：检查配置、依赖、外部目录、端口一致性和运行进程归属。
- `migrate`：启动项目存储，首次初始化集群、数据库、迁移和 bucket；要求项目 API / Worker 停止。
- `start`：验证迁移版本和 bucket，启动 API、Worker 和前端。
- `status|stop|restart`：根据项目状态记录管理服务；应用和前端可单独重启。

首次登录使用外部配置生成的管理员身份；真实模型服务由用户在模型设置中连接，仓库不提供模型密钥。本地控制器只绑定 loopback，不代表生产部署方案。

数据、运行态、日志、缓存、Next.js 输出和临时目录由外部 `local.env` 的 `MDI_DATA_ROOT`、`MDI_RUNTIME_ROOT`、`MDI_LOG_ROOT`、`MDI_CACHE_ROOT`、`MDI_NEXT_DIST_DIR`、`MDI_TEMP_ROOT` 明确配置；`init` 默认把它们放在 `MDI_LOCAL_ROOT` 下，测试使用独立 `pytest` / `pytest-cache` 子目录。变更路径配置不会迁移既有数据。PostgreSQL 与完整 MinIO 数据目录、加密密钥需要一致地备份；Redis 默认不启用 AOF，执行状态以数据库为准。

## 验证范围与当前缺口

源代码及合同由 GitHub CI 验证；具体结果以当前提交的检查为准。代表性真实验收已覆盖多来源/无材料研究、结构与科学结果、报告 ZIP 及 Si CrystalNN 三维局域多面体（原始邻居 → 多面体 → 解释 → 在线报告与 ZIP）。对应功能的 375、770、1280、1920px、键盘/鼠标旋转和选择已有检查，不能据此推导全站已验收。

首次运行已用独立外部目录、独立端口验证空库的完整 38 次迁移、bucket 初始化、六队列 Worker 和首个管理员流程；不修改真实项目数据。单元测试不加载真实 `local.env`。

仍待完成的主要项目：全站 UX/响应式走查、61 份私有样例逐类闭环、各科学数据族图形/选择/损坏状态、浏览器原生 ZIP/PNG 落盘、全消息终态，以及首次浏览器模型密钥提交和管理员发布授权。完整标准见 REMAINING_WORK.md。

前端依赖审计仍有需跨版本处理的风险，已列入 REMAINING_WORK.md 第 1 项。CI 通过表示相应行为检查通过，不代表依赖安全审计清零。

## 文档与依赖治理

Python 依赖由 `pyproject.toml` 和 `uv.lock` 管理，前端使用 npm / `package-lock.json`。CI 不连接真实服务或模型凭据。新的功能同步对应能力和交接条目；只有架构、运行方式或重要产品状态变化才更新本文件。历史留在 Git，不创建平行阶段清单；不修改历史参考 checkout 或用户数据。
