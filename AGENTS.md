# AGENTS.md

开始前读取 `persistent/PROJECT_BRIEF.md`、`persistent/DESIGN_PROGRESS.md`、
`persistent/TASK_BOARD.md`、`persistent/ARCHITECTURE_DECISIONS.md`、
`docs/index.md` 和 `docs/13_SHARED_SCHEMA_SPEC.md`。

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

## 文档规则

- `docs/` 与 `persistent/` 必须纳入 Git。
- 优先更新现有设计文档，不创建重复笔记。
- 新共享 schema 写入 `docs/13_SHARED_SCHEMA_SPEC.md`。
- 保持 MVP/V1/V2 scope 一致。
- 保持 Phase 9C frontend baseline：顶部全局上下文栏、可折叠/缩放左侧数据上下文、单一活动主工作区 tab。

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
13. 不要删除 TASKS.md 中的历史任务。
14. 不要重复执行已经完成的任务。
15. 不要执行尚未完整写完的任务。
16. 如果不存在待处理任务，则不要修改任何项目文件，只报告“当前没有待处理任务”。

安全要求：

- 不删除用户数据。
- 不覆盖与当前任务无关的未提交修改。
- 未经明确任务要求，不修改数据库生产配置。
- 未经明确任务要求，不执行部署、发布或推送操作。
- 不使用 git reset --hard。
- 不强制覆盖远程分支。
