# Phase 5：Agent 编排设计

## 1. 本阶段目标

定义平台中 LLM Agent 的职责边界、编排流程、JSON Plan Schema、Tool Calling 约束、可审计过程展示和报告生成方式。Agent 负责理解用户意图、结合 Data Profile 生成分析计划、选择工具、生成解释和报告；Agent 不直接执行任意代码，不绕过 Tool Registry，不展示原始隐藏思维链。

## 2. 本阶段解决的问题

### Agent 定位

Agent 是：

- Intent Parser。
- Data-aware Planner。
- Tool Selector。
- Parameter Generator。
- Result Explainer。
- Report Writer。

Agent 不是：

- 任意 Python 执行器。
- Shell 执行器。
- 数据库直接操作者。
- 文件系统任意读写者。
- Tool Registry 之外的工具调用者。

### Phase 5 决策

| 问题 | 决策 |
|---|---|
| MVP 是否多模型路由 | 不做自动多模型路由；支持用户/项目选择一个默认 OpenAI-compatible provider/model。 |
| MVP 是否需要工具文档 RAG | 不做完整 RAG；使用版本化 Tool Registry 摘要和静态工具说明注入上下文。 |
| Prompt injection 告警如何展示 | 检测到可疑输入时写入 Agent Timeline warning，并阻止或降级相关步骤。 |
| Agent 是否可执行代码 | 不可执行；只能输出 JSON Analysis Plan，由 Execution Controller 校验后调度。 |
| 是否展示隐藏思维链 | 不展示；展示结构化 Timeline、选择理由、工具参数、日志和结果解释。 |

## 3. 设计原则

- 数据先于计划：Agent 必须读取 Data Profile 和字段映射，不能猜文件内容。
- JSON-only 执行边界：可执行计划必须是结构化 JSON，不接受自然语言直接执行。
- 先校验再执行：tool_id、输入引用、参数、权限、预算、资源限制全部校验。
- 最小上下文：LLM prompt 只包含必要 profile、工具摘要和用户需求，不包含 Secret。
- 可审计不暴露 CoT：展示结构化过程，不展示模型隐藏推理。
- 失败可恢复：计划失败、工具失败、报告失败都要产生可重试事件。
- 版本可追踪：计划记录模型、prompt template、tool registry version 和 schema version。

## 4. 核心模块

| 模块 | 职责 |
|---|---|
| Intent Agent | 从用户自然语言提取分析目标、数据对象、期望输出、约束 |
| Data Agent | 读取 Data Profile、字段映射、质量问题，判断哪些任务可行 |
| Visualization Planner | 选择工具、排序步骤、生成参数、声明预期 Artifact |
| Execution Controller | 校验 JSON Plan，创建 ToolCall，不让 LLM 直接执行 |
| Result Explainer | 基于 Artifact metadata、metrics、warnings 生成图表解释 |
| Report Agent | 生成 Markdown/HTML 报告草案 |
| Prompt Guard | 检测 prompt injection、越权请求、Secret 请求和危险指令 |
| Plan Validator | JSON Schema、Tool Registry、权限、预算、输入可用性校验 |

## 5. Agent 编排流程

```text
User Prompt
  -> Prompt Guard
  -> Intent Agent
  -> Data Agent
  -> Visualization Planner
  -> Plan Validator
  -> Plan Summary shown to user
  -> User clicks Run
  -> Execution Controller creates ToolCalls
  -> Workers execute tools
  -> Result Explainer
  -> Report Agent
  -> Recipe + Report saved
```

### 状态机

```text
drafting
  -> plan_generated
  -> validation_failed

plan_generated
  -> user_cancelled
  -> execution_queued
  -> execution_running
  -> completed

execution_running
  -> partial_success
  -> failed
```

## 6. JSON Plan Schema 草案

正式 Schema 在 Phase 6 与 Tool Registry 一起固化。本阶段定义最小执行边界。
`ArtifactType` 和 `DisplayTarget` 使用 `docs/13_SHARED_SCHEMA_SPEC.md` 的统一定义，避免 Agent、Tool Registry、Artifact Service 和前端各自维护不同枚举。

```ts
type AnalysisPlan = {
  schemaVersion: "0.1";
  goal: string;
  datasetId: string;
  profileId: string;
  toolRegistryVersion: string;
  assumptions: string[];
  warnings: string[];
  steps: AnalysisStep[];
  expectedArtifacts: ExpectedArtifact[];
};

type AnalysisStep = {
  stepId: string;
  toolId: string;
  purpose: string;
  reason: string;
  inputRefs: InputRef[];
  params: Record<string, unknown>;
  output: {
    artifactTypes: ArtifactType[];
    displayTarget: DisplayTarget;
  };
  constraints?: {
    timeoutSec?: number;
    maxRows?: number;
    maxStructures?: number;
    requiresConfirmation?: boolean;
  };
};

type ExpectedArtifact = {
  name: string;
  type: ArtifactType;
  fromStepId?: string;
};
```

禁止字段：

- shell command。
- arbitrary python code。
- raw secret。
- absolute local path。
- external URL fetch without approved connector。

## 7. Tool Calling 约束

Execution Controller 必须执行以下校验：

| 校验 | 说明 |
|---|---|
| Tool existence | `toolId` 必须存在于当前 Tool Registry |
| Input availability | `inputRefs` 必须可被当前 dataset/profile/artifact 解析 |
| Schema validation | `params` 必须符合工具 JSON Schema |
| Permission check | 用户必须有 project/job/tool/artifact 权限 |
| Budget check | LLM 成本、Worker 成本、预计运行时不超过配置 |
| Resource limit | 结构数、行数、原子数、轨迹帧数不超过阈值 |
| Safety check | 不允许任意代码、shell、未授权网络访问 |
| Cache check | 根据 data hash + tool id + params + version 判断是否复用 |

校验失败必须生成：

- `plan.validation_failed` JobEvent。
- 用户可读错误。
- 可修复建议。
- 不创建 ToolCall。

## 8. 可审计过程展示

前端展示 Agent Timeline，而不是隐藏思维链：

```text
1. Prompt Received
2. Prompt Guard Checked
3. Intent Parsed
4. Data Profile Read
5. Plan Generated
6. Plan Validated
7. ToolCall Created
8. Tool Started
9. Artifact Ready
10. Result Explained
11. Report Ready
```

每个事件包含：

```ts
type AgentTimelineEvent = {
  id: string;
  jobId: string;
  seq?: number;
  eventType: string;
  title: string;
  message: string;
  status: "info" | "running" | "success" | "warning" | "error";
  visibleReason?: string;
  toolId?: string;
  artifactId?: string;
  payload?: Record<string, unknown>;
  createdAt: string;
};
```

`AgentTimelineEvent` 是 `JobEvent` 的前端投影视图，`status` 继承 `docs/13_SHARED_SCHEMA_SPEC.md` 的 `JobEvent.status`。`visibleReason` 是产品化解释，例如“数据包含 formula 列，因此选择周期表热力图”，不是模型原始推理。

## 9. Prompt injection 防护

### 风险来源

- 用户 prompt 要求绕过工具注册表。
- 上传文件内容包含“忽略系统指令”等文本。
- CSV 列名或元数据伪装成指令。
- Artifact / report 旧内容被重新注入 Agent。

### 防护策略

- Data Profile 和文件内容作为 data，不作为 instruction。
- Tool Registry 和系统策略优先级高于用户 prompt。
- Prompt Guard 检测危险模式：索要 Secret、要求执行 shell、要求读取任意路径、要求忽略规则。
- 可疑内容写入 Timeline warning。
- 高风险计划直接 validation failed。

## 10. 报告生成

Report Agent 输入：

- 用户目标。
- Data Profile 摘要。
- Analysis Plan。
- ToolCall 状态。
- Artifact metadata。
- 指标和 warning。

Report Agent 输出：

- Dataset overview。
- Generated visualizations。
- Key findings。
- Warnings and limitations。
- Recommended next steps。
- Reproducibility section with Recipe link。

报告不得包含：

- 隐藏思维链。
- Secret。
- 未授权原始文件内容。
- 未校验的外部事实。

## 11. 数据流 / 控制流

```text
analysis_requests
  -> analysis_plans
  -> jobs
  -> job_events
  -> tool_calls
  -> artifacts
  -> reports
  -> visualization_recipes
```

Agent Service 只写计划和解释，不直接写 Artifact 文件；Artifact 由 Worker / Artifact Service 写入。

## 12. API / Schema 草案

```http
POST /analysis-requests
GET /analysis-requests/{id}/plan
POST /analysis-requests/{id}/regenerate
POST /analysis-requests/{id}/run
GET /analysis-requests/{id}/timeline
POST /jobs/{job_id}/report
```

```ts
type AnalysisRequestCreate = {
  projectId: string;
  datasetId: string;
  sessionId?: string;
  prompt: string;
  mode: "auto";
};

type PlanValidationResult = {
  valid: boolean;
  errors: Array<{ code: string; message: string; stepId?: string }>;
  warnings: Array<{ code: string; message: string; stepId?: string }>;
};
```

## 13. 数据库表草案

| 表 | 关键用途 |
|---|---|
| `analysis_requests` | 用户 prompt、dataset、status、mode |
| `analysis_plans` | JSON Plan、schema version、tool registry version、model metadata |
| `tool_calls` | 经过校验后的工具调用 |
| `job_events` | Agent Timeline 和工具过程 |
| `messages` | Chat 记录和系统摘要 |
| `reports` | Report Agent 生成的报告 metadata |
| `visualization_recipes` | 可复现计划 |

新增字段建议：

- `analysis_plans.model_provider`
- `analysis_plans.model_name`
- `analysis_plans.prompt_template_version`
- `analysis_plans.validation_status`
- `analysis_plans.validation_errors_json`

## 14. 前端交互草案

- 用户输入 prompt 后，右侧 Agent 面板显示 “Planning...”。
- 计划生成后默认展示 Plan Summary。
- 如果有 validation warning，Run 按钮旁展示 warning。
- 用户可 Run、Regenerate、Cancel。
- 执行后 Timeline 实时更新。
- 结果解释显示在图表卡片和 Agent Explanation 中。
- 报告生成后进入底部 Artifacts / Report 面板。

## 15. 高并发、安全、扩展性考虑

### 高并发

- LLM 调用进入 `llm` queue，不阻塞 API。
- Plan 生成、Report 生成和 Tool Execution 是不同 job step。
- LLM 超时和失败可重试，但不重复创建 ToolCall。
- 相同 dataset/profile/prompt 可缓存 plan draft，但执行仍需重新校验。

### 安全

- LLM prompt 不包含 Secret。
- Tool docs 和 Data Profile 分隔注入。
- 所有 LLM 输出必须 JSON parse + schema validate。
- 不允许 LLM 返回代码作为执行依据。
- Prompt injection 事件进入 audit log 和 Timeline。

### 扩展性

- V1 支持 Guided / Expert 模式。
- V1 支持工具文档 RAG。
- V1 支持多模型路由。
- V2 支持 Agent 评估集、计划质量评分和组织级 prompt templates。

## 16. 本阶段产出的目标文件

```text
docs/05_AGENT_ORCHESTRATION_DESIGN.md
persistent/DESIGN_PROGRESS.md
persistent/TASK_BOARD.md
persistent/ARCHITECTURE_DECISIONS.md
persistent/OPEN_QUESTIONS.md
persistent/CHANGELOG.md
```

## 17. 下一阶段任务

Phase 6：pymatviz 工具注册表与 Adapter 设计。

需要定义：

- Tool Registry。
- Tool Schema。
- 输入校验。
- 输出 Artifact。
- 错误标准化。
- 缓存策略。
- pymatviz 函数封装。
- MatterViz 3D Viewer 封装。
- 专业材料工具扩展机制。
