# AGENTS.md

当前 active engineering repository：
`E:\1project\mdi-b0-5a1`

`E:\1project\Material Data Intelligence` 仅作为 historical source tree 与
recovery-source 使用，不得继续在那里进行新开发、测试或服务启动。

开始前优先读取 `PROJECT_STATE.md`（存在时仅作为当前快照和导航），再读取
`persistent/PROJECT_BRIEF.md`、`persistent/DESIGN_PROGRESS.md`、
`persistent/TASK_BOARD.md`、`persistent/ARCHITECTURE_DECISIONS.md`、
`docs/index.md`、`docs/ROADMAP.md`、`docs/FUTURE_SCOPE.md`、
`docs/NOT_PLANNED_SCOPE.md` 和 `docs/13_SHARED_SCHEMA_SPEC.md`。

`PROJECT_STATE.md` 不替代任何专门 authority：`TASKS.md` 仍是任务队列，
`results.md` 仍是详细结果账本，ADR、qualification/CI、dynamic/runtime
identity、Tool Registry、roadmap/scope、历史证据和运行时/用户数据仍在各自
领域保持权威。发现 `STATE_STATUS: STALE` 时，先按 source pointers 核对专门
authority，不得静默覆盖或据此删除材料。即使标记为 `CURRENT`，也必须把
Active Work、verification、architecture、runtime identity 和 roadmap/scope
摘要与对应专门 authority 做一次有界核对；若不一致，按 effective stale
处理，先采用专门 authority，再在接受状态后协调 PROJECT_STATE。

## 项目工作规则

1. 不要把本项目变成 pymatviz Web wrapper。
2. 不允许 LLM 直接执行任意 Python、shell、filesystem 或 network 操作。
3. Agent 只能生成结构化 JSON Analysis Plan。
4. 所有可执行 tool call 必须经过 Tool Registry validation。
5. 长时间 parse、planning、visualization、render、export 和 report 必须异步执行。
6. 前端展示 Agent Timeline 和结构化过程记录，不展示隐藏 chain of thought。
7. Artifact、Recipe 和 Report 必须可审计、可复现。
8. User Secret/BYOK 不得进入 prompt、log、Artifact、Recipe、Report 或 export package。
9. 每次有意义的设计或实现变更后更新 persistent 文件。
10. 前端改版不得把执行权移入浏览器；Planner job 仍通过 validated/persisted AnalysisPlan、QueueWorkerRuntime、Tool Registry 和 Adapter。

## 本地服务运行规则

- 除非用户明确要求停止、切换或重启，执行任务期间以及任务结束时都必须保持
  MDI 本地服务运行；不得把“当前任务完成”当作停止服务的理由。
- 优先使用幂等启动器，只补启动缺失进程，不停止或替换健康进程：

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass `
  -File scripts\phase14r_start_stack.ps1 `
  -FrontendPort 3023
```

- 标准本地栈及地址：
  - PostgreSQL：`127.0.0.1:55434`
  - Redis/RQ：`127.0.0.1:6379`
  - MinIO API / Console：`127.0.0.1:9000` / `127.0.0.1:9001`
  - FastAPI：`http://127.0.0.1:8005`
  - Next.js frontend：`http://127.0.0.1:3023`
  - RQ workers：`mdi-agent-turns`、`mdi-agent-plans`、`mdi-jobs`、
    `mdi-agent-results`、`mdi-agent-interpretations`、`mdi-agent-reports`
- `phase14r_start_stack.ps1` 会执行磁盘预检、只启动缺失的 API/frontend/queue
  worker，并验证 PostgreSQL、Redis、MinIO、API、frontend proxy 与全部 queue
  manifest。不要因为端口 `8000` 或 `5432` 未监听就误判服务缺失；当前受控栈
  使用 `8005` 和 `55434`。
- “服务健康”与“历史科学对象的精确源字节仍在当前 MinIO bucket 中”是两件事。
  如果 Data 页面显示“原始来源当前不可访问”，先运行 `-CheckOnly`；若栈健康，
  不要反复重启 MinIO/API，也不得改绑到最新版本。应核对 PostgreSQL 中已记录的
  exact storage key、byte size 和 SHA-256，并仅通过已有的精确恢复工具补回同一
  key：

```powershell
python scripts\restore_exact_minio_references.py `
  --source-endpoint http://127.0.0.1:<RECOVERY_MINIO_PORT> `
  --evidence .runtime_services\managed\recovery\exact-reference-recovery.json
```

  恢复源必须是保留存储的工作副本或受控 recovery endpoint；工具只允许在
  size/SHA-256 完全匹配时写入当前 `mdi-artifacts`，不得修改 PostgreSQL 科学
  authority、静默替换版本或直接改写运行中 MinIO 的磁盘目录。该工具必须同时
  核对并恢复已记录的 ScientificObjectVersion/Artifact 引用，以及 Dataset
  normalized export 的 payload 与 `metadata.json`；只恢复 payload 而遗漏
  metadata 会使 `/datasets/{id}/object-store` 继续返回 `409`。
  recovery endpoint（例如本地 `9010/9011`）不是正常产品依赖；正常 API 始终
  使用 `9000`。不要为了显示历史数据把 API 永久切换到 recovery store。
- 只检查、不补启动时使用：

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass `
  -File scripts\phase14r_start_stack.ps1 `
  -FrontendPort 3023 `
  -CheckOnly
```

- 数据页面无法显示时，先按以下顺序排查，不要先重写前端或猜测存在
  “MIMO”进程：
  1. 运行上面的 `-CheckOnly`，确认 `55434/6379/9000/8005/3023`；
  2. `MinIO` 是对象存储服务，正常进程名为 `minio.exe`，不是 `mimo`；
  3. 端口健康不代表接入了正确的数据目录。登录成功但历史项目/数据集消失时，
     先只读核对 `users.id = user_local`、项目 owner、Dataset/Object 数量和
     `alembic_version`；不得通过新建空项目、改 owner 或直接写数据库掩盖错误
     数据目录。当前包含完整 Phase 13/14R 历史项目的 canonical 恢复副本是：

```text
E:\1project\mdi-b0-5a1\.runtime_services\managed\recovered-phase13-postgres-data-20260913
```

     该目录来自历史仓库
     `E:\1project\Material Data Intelligence\.phase13-postgres-data2` 的逐文件
     工作副本；历史目录只作为 recovery source，不得被 API/worker 直接长期
     使用。旧的
     `.runtime_services\managed\workstream-c\postgres-data` 不包含当前完整
     用户项目，不能再作为 `55434` 的默认数据源。
  4. 如果 PostgreSQL `55434` 被手动关闭，使用上述 canonical 恢复副本启动，
     不要使用 Docker 的 `5432` 数据库或空的 workstream-c 数据目录替代：

```powershell
$repo = "E:\1project\mdi-b0-5a1"
$data = "$repo\.runtime_services\managed\recovered-phase13-postgres-data-20260913"
$log = "$repo\.runtime_services\managed\recovered-phase13-postgres-55434.log"
pg_ctl.exe -D $data -o "-p 55434 -h 127.0.0.1" -l $log -w start
```

  5. 如果 MinIO `9000` 被关闭，使用当前 canonical target store 和标准
     credentials 启动；不要清空 bucket、换 bucket 或切换 recovery store：

```powershell
$repo = "E:\1project\mdi-b0-5a1"
$env:MINIO_ROOT_USER = "mdi-local"
$env:MINIO_ROOT_PASSWORD = "mdi-local-dev"
minio.exe server "$repo\.runtime_services\managed\workstream-c\minio-data" `
  --address "127.0.0.1:9000" --console-address "127.0.0.1:9001"
```

  6. PostgreSQL/MinIO 恢复后，重新运行标准幂等启动器补齐 API、frontend
     和缺失 workers：

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass `
  -File scripts\phase14r_start_stack.ps1 -FrontendPort 3023
```

  7. 如果 API 日志明确报告
     `DATABASE_MIGRATION_HEAD_MISMATCH`，不得关闭 migration-head guard，
     也不得改用 SQLite。先加载 canonical runtime environment，再在同一
     `55434/mdi` 数据库执行受控迁移：

```powershell
$envJson = python scripts\phase14r_runtime_environment.py --compact | ConvertFrom-Json
foreach ($property in $envJson.PSObject.Properties) {
  Set-Item -Path "Env:$($property.Name)" -Value ([string]$property.Value)
}
$env:PYTHONPATH = @(
  "apps/api", "packages/schemas", "packages/tool-registry",
  "packages/adapters", "packages/artifact-core",
  "packages/material-parsers", "services/workers", "services/llm"
) -join [IO.Path]::PathSeparator
python -m alembic -c apps/api/alembic.ini upgrade head
powershell.exe -NoProfile -ExecutionPolicy Bypass `
  -File scripts\phase14r_start_stack.ps1 -FrontendPort 3023
```

  8. 数据库恢复后如果页面仍报告“原始来源当前不可访问”，说明 PostgreSQL
     identity 已恢复但当前 MinIO target 缺少精确 payload。启动 canonical
     recovery copy 的临时 MinIO（例如 `9010`），然后按项目执行 exact-byte
     恢复；恢复工具只在 key、byte size、SHA-256 全部匹配时写入 `9000`：

```powershell
$repo = "E:\1project\mdi-b0-5a1"
$env:MINIO_ROOT_USER = "mdi-local"
$env:MINIO_ROOT_PASSWORD = "mdi-local-dev"
minio.exe server `
  "$repo\.runtime_services\managed\recovery-phase13\minio-data" `
  --address "127.0.0.1:9010" --console-address "127.0.0.1:9011"

python scripts\restore_exact_minio_references.py `
  --db-url "postgresql://mdi@127.0.0.1:55434/mdi" `
  --source-endpoint "http://127.0.0.1:9010" `
  --target-endpoint "http://127.0.0.1:9000" `
  --project-id "project_0002_1a0af866391f412d" `
  --evidence ".runtime_services\managed\recovery-phase13\exact-reference-recovery.json"
```

     不带 `--project-id` 的全账户恢复可能被其他 qualification project 中没有
     对应历史 source 的对象阻断；已知项目恢复应显式限定 project，避免把一个
     无关项目的缺失误判成目标项目恢复失败。
  9. 本地验收登录应保持稳定的数据库身份 `user_local`。调整邮箱/密码时必须
     使用受支持的 `MDI_LOCAL_USER_EMAIL` / `MDI_LOCAL_USER_PASSWORD`
     bootstrap + `/auth/login` 路径，不得直接改 owner、伪造 session 或迁移
     用户数据。邮箱可变，但 `user_local` id 和原项目 ownership 必须保留。
     密码不得写入 `AGENTS.md`、日志或 review bundle。
  10. 恢复完成后必须再次确认：
     `http://127.0.0.1:8005/health/runtime` 和
     `http://127.0.0.1:3023/api/health/runtime` 均报告 PostgreSQL、
     Redis、MinIO、Redis worker backend；还要在真实登录浏览器中打开至少
     一个 Table/Trajectory/Electronic/Phonon 等精确 ObjectVersion，确认没有
     source-unavailable 或 viewer nesting 错误。不要把端口监听误判为数据
     已恢复。
  11. 除非用户明确要求停止、切换或重启，恢复后继续保持整套服务运行。
     任务完成不是停止服务的理由。

- 只有在生产代码变更确实要求重载时，才使用对应的受控 rotate/start 脚本；
  不得停止无关服务、清空共享 Redis、删除 PostgreSQL/MinIO 数据或修改用户凭据。

## 文档规则

- `docs/` 与 `persistent/` 必须纳入 Git。
- 优先更新现有设计文档，不创建重复笔记。
- 新共享 schema 写入 `docs/13_SHARED_SCHEMA_SPEC.md`。
- 保持 MVP/V1/V2 scope 一致。
- 保持 Phase 9C frontend baseline：顶部全局上下文栏、可折叠/缩放左侧数据上下文、单一活动主工作区 tab。
- `docs/ROADMAP.md` 是当前路线唯一权威；历史 phase 文档不得覆盖它。
- 未经 reviewer/user 明确批准，不得把 Future Scope 加入 `TASKS.md`。
- Not Planned 能力不能仅因技术上可实现而重新进入路线。

## 持续任务执行规则

本项目使用 TASKS.md 作为持续任务队列。

每次自动任务运行时，必须执行以下流程：

1. 读取项目根目录中的 TASKS.md。
2. 任务通过以下结构分隔每一个任务：

```text
---TASK---
任务内容
---END---
```

3. 从上到下寻找第一个“状态：待处理”的任务。
4. 一次只执行一个任务。
5. 不执行状态为“处理中”“已完成”或“失败”的任务。
6. 开始执行前，将该任务状态改为“处理中”。
7. 阅读与任务相关的代码、配置和文档。
8. 完整执行任务，不要只输出建议。
9. 尽可能运行测试、构建或检查命令。
10. 成功后，把状态改为“已完成”。
11. 在任务末尾追加：
   - 完成时间
   - 修改文件
   - 修改摘要
   - 测试结果
12. 如果任务无法完成，把状态改为“失败”，并写明原因，你必须尽量把每一个任务都完成，知道尝试了所有方法失败后才改状态，然后退出执行。
13. `TASKS.md` 只保留待处理、处理中、失败或尚未完成归档核验的任务；已完成任务的历史结果由 `results.md` 保存。
14. 不要重复执行已经完成的任务。
15. 不要执行尚未完整写完的任务。
16. 如果不存在待处理任务，则不要修改任何项目文件，只报告“当前没有待处理任务”。
17. 每个任务完成或失败后，将该任务的最终结果追加到项目根目录的 `results.md`；记录任务名称、状态、完成时间、修改摘要、测试结果和提交/CI 状态（如适用），不得覆盖已有任务结果。
18. 删除 `TASKS.md` 中状态为“已完成”的任务前，必须确认任务确实完成：完成记录和 `results.md` 一致、要求的测试/构建已通过、需要 CI 的任务其 current-HEAD CI 已成功；任何一项未闭合都不得删除。
19. 完成上述核验后，删除该任务的完整 `---TASK---` 至 `---END---` block；不得删除失败、处理中或待处理任务，也不得丢失 `results.md` 中的历史结果。
20. 若存在状态为“处理中”的任务，它必须始终位于 `TASKS.md` 的第一个任务位置；开始新任务时先完成必要的队列整理，不得移动或删除用户正在修改的未处理任务内容。

安全要求：

- 不删除用户数据。
- 不覆盖与当前任务无关的未提交修改。
- 未经明确任务要求，不修改数据库生产配置。
- 未经明确任务要求，不执行部署、发布或推送操作。
- 不使用 git reset --hard。
- 不强制覆盖远程分支。
- 进程切换、重启或更换资格环境前，必须先枚举上一轮任务创建的进程树、监听端口和临时资源；不得让旧进程与新进程并存而造成内存或端口资源累积。
- 任何停止、暂停或重启前，必须立即核对 PID、进程启动时间、完整命令行、cwd、PPID、角色以及资格 namespace/端口；PID 单独不能作为所有权证明。
- 只允许停止当前任务明确创建且已验证归属的旧进程及其子进程。共享服务、canonical 服务、未知 PID 和其他任务资源必须排除。
- 终止后必须等待操作系统确认退出，并复核进程树、监听端口和相关资源已释放；未释放时不得启动替代进程。清理前后状态和结果必须记录到对应的 service/process evidence。
- 若身份不匹配、归属不明确或存在共享资源风险，必须中止切换，不得按 PID 猜测、强制 kill 或清空共享队列。
