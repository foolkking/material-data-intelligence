---TASK---
 状态：已完成
你现在执行：

# Phase 10L-0：Agent / Planner Capability Audit

本阶段是 Phase 10L Intelligent Analysis Agent 的入口审计阶段。

这是一个：

**ARCHITECTURE AUDIT / CAPABILITY INVENTORY / GAP ANALYSIS GATE**

不是 Planner 实现阶段。

本阶段结束后必须：

**REVIEWER_GATE**

不得自动进入 Phase 10L-1。

---

# 0. 本阶段最高目标

本阶段必须基于真实 repository 回答：

> 当前项目中的 Agent / Planner 到底已经做到什么程度？

重点不是根据旧文档猜。

重点是审计真实：

* Mock Planner
* deterministic routing
* real LLM Planner
* DataProfile 2.0
* AnalysisPlan
* ToolCall
* Tool Registry
* Tool capability metadata
* PlanValidator
* QueueWorkerRuntime
* resource/artifact binding
* current multi-tool support
* frontend planner flow
* result interpretation
* error/repair behavior

最终需要判断：

当前 Planner 到底属于：

```text
KEYWORD_ROUTER

MOSTLY_PROMPT_ROUTED

PROFILE_AWARE_SINGLE_TOOL_PLANNER

CAPABILITY_AWARE_SINGLE_TOOL_PLANNER

PARTIAL_MULTI_TOOL_PLANNER

CAPABILITY_AWARE_MULTI_TOOL_PLANNER
```

只能根据真实实现选。

---

# 1. Hard Entry Gate

首先验证：

```text
Phase 10J-6 = ARCHIVED
Gate J6-R = PASS

Phase 10K-0 = ARCHIVED
Phase 10K-1 = ARCHIVED
Phase 10K-2 = ARCHIVED
Phase 10K-3 = ARCHIVED
Phase 10K-4 = ARCHIVED
Phase 10K-5 = ARCHIVED

Phase 10K = COMPLETE

Phase 10L-0 = NEXT
```

必须读取真实：

* Phase 10K-5 result
* Phase 10K completion summary
* current roadmap
* TASKS
* persistent state
* Tool Registry notes
* architecture decisions

如果 Phase 10K 尚未完整关闭：

输出：

`BLOCKED_BY_PHASE_10K`

并停止。

不得继续 Planner audit。

---

# 2. Reviewer Gate Rule

这是本阶段的硬规则。

Phase 10L-0 完成后：

```text
Phase 10L-0:
ARCHIVED

Phase 10L-1:
REVIEWER_GATE / NOT_QUEUED
```

或者符合当前 repository queue terminology 的等价状态。

不得：

* 自动创建 Phase 10L-1 executable task
* 自动进入 Analysis Intent implementation
* 自动修改 Planner contracts
* 自动开始 multi-tool planning
* 自动实现 result interpretation

最终必须停下来等待 reviewer 根据本阶段结果设计 10L-1。

---

# 3. Canonical Product Context

项目最终目标：

# Material Data Intelligence & Visualization Platform

核心流程：

```text
Materials Data
      ↓
Material Data Profile
      ↓
Natural Language Goal
      ↓
Analysis Intent
      ↓
Capability-Aware Planner
      ↓
Validated AnalysisPlan
      ↓
Tool Registry / Adapter
      ↓
Scientific Execution
      ↓
Artifacts
      ↓
Interpretation
      ↓
Report / Recipe
```

Phase 10K 已经负责：

* Material Data Profile 2.0
* Dataset Materials Explorer
* Materials ML
* Composition Space

Phase 10L 开始负责：

**如何让 Agent 正确理解目标并选择/组合这些能力。**

---

# 4. Phase 10L Current High-Level Direction

当前 roadmap 只冻结大方向：

```text
Phase 10L-0
Agent / Planner Capability Audit

Phase 10L-1
Analysis Intent Contract

Phase 10L-2
Capability-Aware Planner

Phase 10L-3
Bounded Multi-Tool Analysis

Phase 10L-4
Scientific Result Interpretation

Phase 10L-5
Natural-Language Analysis Evidence
```

但：

**10L-1～10L-5 的具体 contract 尚未冻结。**

本阶段必须通过真实代码判断：

这些子阶段是否需要：

* 合并
* 缩小
* 调整边界

不得自行改 ROADMAP。

只提出 reviewer recommendation。

---

# 5. Explicit Non-Scope

本阶段禁止修改：

* AnalysisPlan schema
* ToolCall schema
* DataProfile schema
* Tool Registry public contract
* PlanValidator behavior
* QueueWorkerRuntime behavior
* Mock Planner routing
* LLM Planner prompt
* LLM provider configuration
* frontend planning behavior
* artifact dependency semantics
* result interpretation
* report generation
* retry/repair behavior

禁止新增：

* Agent framework
* workflow engine
* DAG
* memory system
* RAG
* multi-agent architecture
* prompt chaining
* tool calling framework
* new LLM dependency

本阶段允许的代码变更原则上只有：

* audit-only helper/test if absolutely required
* documentation
* persistent records
* result/evidence
* queue state

如果审计需要修改 production Planner 才能“确认能力”：

说明审计设计有问题。

不得修改。

---

# 6. Baseline Verification

进入：

```text
E:\1project\Material Data Intelligence
```

运行：

```bash
git status --short
git branch --show-current
git rev-parse HEAD
git rev-parse origin/master
git log --oneline -40
git diff --stat
git diff --check
```

记录：

* repository
* branch
* HEAD
* origin/master
* status
* Phase 10K-5 implementation commit
* Phase 10K-5 completion-record commit
* Phase 10K archive state
* exact-head CI

工作区必须明确。

如果存在 unrelated source changes：

停止并报告。

---

# 7. Queue Transition

只有 Entry Gate PASS 后：

将：

`Phase 10L-0：Agent / Planner Capability Audit`

设为唯一 active task。

不得把：

`10L-1`

加入 active queue。

TASKS 中必须加入 reviewer barrier，例如：

```text
REVIEWER GATE AFTER PHASE 10L-0

Do not execute Phase 10L-1 automatically.
Phase 10L-1 requires reviewer approval based on the real
Phase 10L-0 Agent / Planner Capability Audit result.
```

实际格式遵循当前 repository。

---

# 8. 必读 Canonical Documentation

完整阅读：

```text
README.md
AGENTS.md
MASTER_PROMPT.md

docs/ROADMAP.md
docs/00_PROJECT_GOAL.md
docs/01_PRODUCT_REQUIREMENTS.md
```

或实际 canonical equivalents。

同时：

```text
persistent/PROJECT_BRIEF.md
persistent/DESIGN_PROGRESS.md
persistent/TASK_BOARD.md
persistent/CHANGELOG.md
persistent/OPEN_QUESTIONS.md
persistent/TOOL_REGISTRY_NOTES.md
persistent/ARCHITECTURE_DECISIONS.md
```

以及 Phase 10K completion summary。

---

# 9. 必读历史 Planner 设计

必须定位并阅读所有与 Planner 有关的历史 docs。

搜索：

```bash
rg -n "Planner|AnalysisPlan|PlanValidator|Mock Planner|LLM Planner|tool routing|Tool Registry|intent|planning|repair|retry|tool selection" docs persistent README.md MASTER_PROMPT.md
```

重点阅读：

* Phase 1–9 Planner implementation/history
* real LLM phase
* PlanValidator
* Tool Registry
* QueueWorkerRuntime
* Phase 10 planner-routing changes
* Phase 10K DataProfile integration notes

历史文档：

只用于理解。

当前代码才是 implementation truth。

---

# 10. Planner Code Discovery

搜索真实代码：

```bash
rg -n "class .*Planner|def .*plan|MockPlanner|LLMPlanner|AnalysisPlan|PlanValidator|ToolCall|tool_registry|planner" .
```

排除：

* generated
* node_modules
* build artifacts
* evidence binary

建立：

# Planner Architecture File Map

至少列：

| Component          | File | Responsibility |
| ------------------ | ---- | -------------- |
| Planner API        |      |                |
| Mock Planner       |      |                |
| LLM Planner        |      |                |
| Prompt Builder     |      |                |
| AnalysisPlan Model |      |                |
| ToolCall Model     |      |                |
| PlanValidator      |      |                |
| Tool Registry      |      |                |
| Queue Runtime      |      |                |
| Planner UI         |      |                |

---

# 11. Audit A — AnalysisPlan Contract

完整审计当前 AnalysisPlan。

必须回答：

* schema name/version
* plan ID
* user goal storage
* dataset/resource binding
* ToolCall count
* ordering
* dependencies
* artifact input references
* output expectations
* validation state
* planner metadata
* model/provider metadata
* warnings
* provenance
* persistence

建立：

# Current AnalysisPlan Contract Matrix

---

# 12. Single Tool vs Multiple Tools

这是最关键问题之一。

必须通过代码和测试确认：

当前 `AnalysisPlan` 是否允许：

```text
ToolCall[]
```

如果允许多个：

进一步确认：

* 是独立顺序 list？
* 是否真正执行多个？
* 是否 validator 支持？
* runtime 是否支持？
* artifacts 是否各自持久化？
* 是否有 dependencies？

不要因为 schema 是 array 就写：

MULTI_TOOL_READY。

---

# 13. Multi-Tool Execution Reality

必须找到真实测试或运行代码证明：

### Case

一个 AnalysisPlan：

```text
Tool A
Tool B
```

是否真正执行。

分别审计：

* persistence
* validation
* queue execution
* failure handling
* artifact persistence
* frontend timeline

分类：

```text
NOT_SUPPORTED

SCHEMA_ONLY

SEQUENTIAL_INDEPENDENT

ORDERED_MULTI_TOOL

DEPENDENCY_AWARE
```

---

# 14. Dependency Representation

检查 AnalysisPlan 是否存在：

* `depends_on`
* artifact binding
* input from previous ToolCall
* dependency IDs
* step IDs
* resource outputs

如果不存在：

明确。

不得把 list order 称：

DAG。

---

# 15. Artifact Input Binding

非常重要。

检查一个 ToolCall 的 input 是否只能来自：

* dataset/resource

还是可以来自：

* previous artifact

例如：

```text
Tool A produces artifact X
Tool B consumes artifact X
```

当前支持程度必须明确。

---

# 16. Failure Semantics

如果 AnalysisPlan 有多个 ToolCall：

检查：

Tool A FAIL 时：

* Tool B 是否继续？
* 整个 job FAIL？
* partial artifacts保留？
* retry？
* error propagation？

这会直接决定 10L-3 scope。

---

# 17. Cancellation

审计 Planner-generated multi-tool job 的 cancellation semantics。

只记录现状。

不要修改。

---

# 18. Audit B — Mock / Deterministic Planner

找到 Mock Planner 全部 routing logic。

检查：

* keyword matching
* regex
* tool ID lookup
* resource type
* DataProfile
* column semantics
* Tool Registry metadata
* params generation
* fallback
* ambiguity

建立：

# Mock Planner Decision Inputs

| Signal             | Used? | How |
| ------------------ | ----: | --- |
| raw prompt         |       |     |
| keywords           |       |     |
| resource kind      |       |     |
| DataProfile        |       |     |
| semantic roles     |       |     |
| readiness          |       |     |
| Tool Registry      |       |     |
| explicit tool IDs  |       |     |
| previous artifacts |       |     |

---

# 19. Keyword Router Audit

必须真实统计：

当前 Mock Planner 中有多少 routing rule 属于类似：

```text
if "rdf" in prompt
if "xrd" in prompt
if "histogram" in prompt
```

不要只给 impression。

可以分类：

* exact command mapping
* keyword
* structured detection
* profile-aware
* registry-aware

不需要精确到无意义行数，但必须有实质证据。

---

# 20. Resource Awareness

例如用户说：

> analyze this dataset

Mock Planner 是否知道：

这是：

* table
* structure
* trajectory
* phonon
* volumetric

还是完全只看 prompt？

必须测试/代码证明。

---

# 21. DataProfile 2.0 Use

这是 Phase 10K → 10L 最重要衔接。

必须追踪：

DataProfile 2.0 是否进入 Planner。

包括：

* object passed?
* serialized context?
* only resource kind?
* readiness?
* semantic groups?
* ML task identities?
* properties?
* composition?

建立：

# Planner DataProfile Consumption Matrix

| Profile Information | Mock Planner | LLM Planner | Validator |
| ------------------- | -----------: | ----------: | --------: |
| resource kind       |              |             |           |
| formula             |              |             |           |
| material properties |              |             |           |
| structure presence  |              |             |           |
| trajectory          |              |             |           |
| phonon              |              |             |           |
| volumetric          |              |             |           |
| regression task     |              |             |           |
| uncertainty         |              |             |           |
| classification      |              |             |           |
| readiness           |              |             |           |

---

# 22. Planner Classification

Mock Planner 最终必须归类为：

```text
KEYWORD_ROUTED
MOSTLY_KEYWORD_ROUTED
PARTIAL_PROFILE_AWARE
PROFILE_AWARE
CAPABILITY_AWARE
```

并说明证据。

---

# 23. Audit C — Real LLM Planner

找到真实 LLM provider path。

必须确认：

* provider interface
* prompt template
* system prompt
* Tool Registry serialization
* DataProfile serialization
* model config
* JSON mode/schema
* timeout
* retry
* parse failure
* validation loop
* fallback
* mock isolation

不得调用真实 LLM。

本阶段只读代码/tests。

---

# 24. LLM Planner Prompt Inputs

明确 LLM 实际收到什么。

建立：

# LLM Planner Context Matrix

包括：

* user prompt
* dataset/resource metadata
* DataProfile
* Tool descriptions
* params schemas
* capability requirements
* artifact types
* safety instructions
* max tools
* previous errors
* previous plan
* conversation history

---

# 25. Tool Registry Exposure to LLM

检查是：

### A

只提供：

```text
tool ID + description
```

还是：

### B

提供：

```text
tool ID
description
params schema
resource compatibility
outputs
```

还是更完整 capability metadata。

必须真实记录。

---

# 26. Tool Capability Metadata Audit

当前 Tool Registry 每个 Tool 是否有：

* tool ID
* description
* domain
* input resource kind
* params schema
* output artifacts
* cost/resource cap
* scientific requirements
* semantic role requirements
* user-facing description
* planner hints

建立：

# Tool Capability Metadata Matrix

---

# 27. Planner-Friendly Registry

最终判断 Registry 当前更像：

```text
EXECUTION_REGISTRY
```

还是：

```text
PLANNER_CAPABILITY_REGISTRY
```

可能是：

`PARTIAL_PLANNER_CAPABILITY_REGISTRY`

说明缺口。

---

# 28. Analysis Eligibility

例如：

`ml.regression_evaluation`

是否在 Registry 中正式声明：

需要 regression semantic group？

还是只有 adapter 自己执行时才检查？

这个差异非常重要。

---

# 29. Audit D — PlanValidator

完整审计 PlanValidator。

检查：

* allowed Tool IDs
* params schema
* strict additionalProperties
* resource existence
* resource kind
* DataProfile
* semantic readiness
* artifact input
* caps
* tool count
* dependencies
* duplicate calls
* unsafe params

---

# 30. Validator Classification

PlanValidator 当前是：

```text
SCHEMA_VALIDATOR

SCHEMA_AND_REGISTRY_VALIDATOR

RESOURCE_AWARE_VALIDATOR

SEMANTIC_CAPABILITY_VALIDATOR

DEPENDENCY_AWARE_VALIDATOR
```

根据真实实现分类。

---

# 31. DataProfile Readiness in Validator

检查：

DataProfile 2.0 readiness 是否用于：

拒绝：

```text
regression tool on dataset without predictions
```

或者：

这种错误直到 Adapter runtime 才发现。

必须明确。

---

# 32. Params Generation

Planner 当前如何决定：

* x/y columns
* selected ML task
* property
* model
* structure resource
* volumetric field
* trajectory params

是：

* prompt extraction
* default
* DataProfile
* hardcoded
* adapter default
* LLM guessed

必须分类。

---

# 33. Ambiguous Semantics

DataProfile 可能返回：

`AMBIGUOUS`

当前 Planner 遇到时：

* reject?
* choose first?
* ask user?
* ignore?
* LLM decides?

必须查真实行为。

---

# 34. Clarification Support

检查现有 Planner/UI 是否存在：

* needs clarification state
* follow-up question
* unresolved field
* plan draft requiring user selection

如果不存在：

明确：

`NOT_IMPLEMENTED`

不要设计实现。

---

# 35. Audit E — Tool Selection

建立正式：

# Tool Selection Mechanism Inventory

对于至少以下 domain：

* general table
* composition
* structure
* trajectory
* phonon
* BZ
* volumetric
* dataset intelligence
* materials ML
* composition space

检查：

Planner 是如何选择 tool 的。

---

# 36. Capability Collision

检查是否存在多个 tool 都可以处理相似问题。

例如：

```text
viz.histogram
table.distribution_summary
dataset.materials_summary
```

Planner 当前如何区分？

如果只是 keyword：

记录 risk。

---

# 37. Tool Granularity Effect on Planner

Phase 10K 已刻意采用 product-level tools。

审计：

这是否使 Planner capability surface 更清晰。

记录：

* product-level tools
* low-level tools
* overlap

这会影响 10L-2。

---

# 38. Audit F — Planner Output Quality

使用现有 deterministic tests/fixtures，审计典型自然语言。

禁止调用真实 LLM。

可以使用：

* Mock Planner
* fixture-based LLM responses
* existing tests

测试以下代表性 prompt。

---

# 39. Case 1 — Composition

```text
分析这批材料主要有哪些元素和化学体系。
```

当前 Planner：

选择什么？

是否数据感知？

---

# 40. Case 2 — Structure

```text
看看这个晶体结构是否合理。
```

当前 Planner 能否：

理解这是 broad scientific intent？

还是只找到：

structure summary

或根本不匹配？

这里只记录。

---

# 41. Case 3 — ML

```text
分析这个模型在哪些材料上预测得不好。
```

当前 Planner 是否选择：

Materials ML Evaluation？

是否知道 chemistry-conditioned error？

还是只匹配 scatter？

---

# 42. Case 4 — Uncertainty

```text
这些不确定度可信吗？
```

当前 Planner 是否知道：

uncertainty readiness？

---

# 43. Case 5 — Phonon

```text
检查这个声子计算有没有明显问题。
```

当前 Planner 输出什么？

---

# 44. Case 6 — Volumetric

```text
看看这个电荷密度里主要有什么特征。
```

当前 Planner 输出什么？

---

# 45. Case 7 — Broad Dataset Intent

```text
帮我全面分析一下这批材料。
```

这是关键。

当前 Planner：

* 一个 tool？
* arbitrary first match？
* fails？
* multi-tool？
* LLM only？

记录。

不要修。

---

# 46. Case 8 — Explicit Tool-Like Intent

```text
画 formation_energy 的分布。
```

这种应该是现有 Planner 相对擅长的 case。

作为 baseline。

---

# 47. Planner Evaluation Matrix

建立：

| Prompt | Expected Capability Category | Current Mock Result | Current LLM Design Capability | Gap |
| ------ | ---------------------------- | ------------------- | ----------------------------- | --- |

注意：

这里的 “Expected” 是产品意图，不是官方 validation。

---

# 48. Audit G — Analysis Intent

检查 repository 是否已经存在类似：

* Intent
* UserIntent
* AnalysisIntent
* Goal
* AnalysisRequest
* PlannerRequest
* objective

如果已有：

必须审计。

不要因为 roadmap 叫：

`Analysis Intent Contract`

就新建重复对象。

---

# 49. Current Intent Representation

如果目前只有：

```text
prompt: string
```

明确。

如果已经有：

```text
goal
targets
constraints
output preferences
```

则记录。

这直接决定 10L-1 是否需要新 contract。

---

# 50. Intent vs Plan

必须检查当前 architecture 是否混合：

用户需求

和：

执行计划。

例如：

AnalysisPlan 是否直接保存 raw prompt，但没有独立 intent。

记录优缺点。

不要修改。

---

# 51. Audit H — Multi-Turn / Conversation

检查当前 Planner 是否接收：

* conversation history
* previous plan
* previous user correction
* selected resource context

如果没有：

明确。

但 Phase 10L Initial Release 不一定需要 full conversational memory。

不要自动把 multi-turn 变成 blocker。

---

# 52. Audit I — Plan Repair

检查现有：

* invalid JSON repair
* schema re-prompt
* validation-error repair
* fallback
* retry

区分：

## Transport / Parse Repair

例如 invalid JSON。

## Scientific Plan Repair

例如：

tool requires regression data but dataset lacks it。

后者可能尚未实现。

---

# 53. Plan Repair Authority

检查是否存在风险：

LLM 在 validation fail 后无限改计划。

当前 caps：

* retry count
* timeout
* provider limits

记录。

---

# 54. Audit J — Runtime / Planner Boundary

确认：

LLM 是否任何时候能够：

* execute Python
* shell
* arbitrary code
* direct filesystem
* direct scientific library calls

预期必须是：

NO。

如果不是：

高优先级风险。

---

# 55. Tool Execution Authority

正式应该是：

```text
Planner
↓
Validated AnalysisPlan
↓
QueueWorkerRuntime
↓
Registered Adapter
```

本阶段必须验证真实 architecture 仍然满足这一点。

---

# 56. Audit K — Frontend Planner UX

审计 PlannerWorkbench/current frontend。

检查用户目前能看到：

* natural-language prompt
* selected dataset/resource
* generated plan
* tool calls
* params
* validation
* execution timeline
* artifacts
* errors
* retry
* edit plan
* plan approval

建立：

# Planner UX Inventory

---

# 57. User Control

检查当前是否支持：

* inspect plan before execution
* edit params
* remove tool
* rerun
* cancel
* retry

只记录。

不要认为所有都必须进入 Phase 10L。

---

# 58. Broad Intent UX

如果 Planner 无法处理 broad intent：

当前 UI 是否引导用户：

* choose tool
* refine prompt
* select resource

记录。

---

# 59. Audit L — Result Interpretation

检查是否已经存在：

* LLM summary
* deterministic summary
* findings
* warnings
* next-step recommendations
* artifact explanation

Phase 10L-4 可能不是从零开始。

必须真实盘点。

---

# 60. Scientific Interpretation Authority

如果已有 LLM result summary：

检查它收到：

* raw artifact?
* structured summary?
* entire dataset?
* tool metadata?
* warnings?

以及是否存在：

“不要编造未计算结论”

的 contract。

---

# 61. Audit M — Planner Security

检查：

* prompt injection handling
* tool description exposure
* untrusted dataset names
* artifact contents
* provider prompt boundaries
* arbitrary tool ID
* arbitrary params
* unknown tool rejection
* output schema enforcement

只审计。

不要展开企业 security phase。

---

# 62. Tool Injection

检查用户 prompt 能否让 Planner输出：

不存在 tool

或：

危险 params。

PlanValidator 是否阻止？

必须有实际 test/code evidence。

---

# 63. Artifact Prompt Injection

如果未来/当前 LLM 会读取 artifact summary：

是否有 untrusted content boundary？

如果当前还没 result interpretation：

记录 future risk 给 10L-4。

---

# 64. Audit N — Caps / Resource Limits

Planner 层当前是否限制：

* max ToolCalls
* max prompt size
* max registry tools serialized
* max output size
* provider timeout
* retry count
* max plan complexity

这会影响 10L-3。

---

# 65. Max Tool Count

如果当前没有 multi-tool：

也检查 AnalysisPlan validator 是否已有：

max tool count。

记录。

---

# 66. Audit O — Current Tests

完整定位：

* Planner unit tests
* PlanValidator tests
* Mock Planner tests
* LLM fixture tests
* provider tests
* service-backed planning tests
* browser planner tests

建立：

# Planner Test Coverage Matrix

---

# 67. Do Not Mistake Fixture LLM for Real Provider Evidence

必须区分：

* Mock Planner
* fake LLM response
* recorded fixture
* gated real provider

不要写：

“LLM Planner scientifically validated”

仅因为 fixture PASS。

---

# 68. Real LLM Test Boundary

本阶段禁止调用真实 LLM。

只审计：

当前 gated real-provider integration 是否存在和如何工作。

不消耗用户 API key。

---

# 69. Audit P — Tool Registry Scale

统计当前正式 Tool Registry：

* total tools
* domains
* 10K additions
* overlapping low-level tools
* product-level tools

目的是判断：

LLM prompt 是否还能直接 serialise entire registry。

不要为此做 optimization。

---

# 70. Tool Description Quality

抽样审计至少：

* generic visualization
* structure
* trajectory
* phonon
* volumetric
* dataset
* ML
* composition space

检查 description 是否足以让 Planner区分。

---

# 71. Capability Requirements

特别检查 Tool Registry 是否能够表达：

```text
requires:
regression_task
```

或：

```text
resource_kind:
trajectory
```

如果没有：

这是 10L-2 可能要解决的重要 gap。

---

# 72. Audit Q — Plan / Recipe Relationship

检查：

AnalysisPlan

和：

Recipe

是否不同对象。

Recipe 是否可以：

* replay
* hold tool params
* reference resources

Planner 是否可以直接生成 Recipe？

当前如何？

这关系 10L architecture，但本阶段只记录。

---

# 73. Audit R — Planner Persistence

检查 Plan 是否：

* persisted before execution
* immutable
* editable
* versioned
* linked job
* linked user prompt
* linked planner/provider

记录。

---

# 74. Audit S — Planner Reproducibility

Mock Planner：

相同 prompt/data 是否 deterministic？

LLM Planner：

是否记录：

* provider
* model
* temperature
* prompt/schema version
* generated plan

确保以后可以审计。

---

# 75. Temperature / Randomness

如果 LLM provider config 有 temperature：

记录 current policy。

不要修改。

---

# 76. Audit T — Agent Terminology

检查 repository 中：

* Agent
* Planner
* Assistant
* Analysis Agent

是否混用。

本阶段建议文档统一概念，但不要大规模 rename source code。

最终至少冻结：

```text
Agent = user-facing intelligent orchestration concept
Planner = component that generates AnalysisPlan
Runtime = deterministic execution
```

如果 current architecture已有更准确定义：

遵循真实设计。

---

# 77. Current-State Architecture Diagram

本阶段必须形成基于真实代码的 diagram。

例如：

```text
User Prompt
   ↓
Planner Request
   ↓
Mock / LLM Planner
   ↓
AnalysisPlan
   ↓
PlanValidator
   ↓
Persisted Job
   ↓
QueueWorkerRuntime
   ↓
Tool Registry
   ↓
Adapters
   ↓
Artifacts
```

然后标注：

DataProfile 当前在哪里进入。

必须与真实代码一致。

---

# 78. Gap Analysis Categories

所有发现统一分类：

## READY

真实可用。

## REUSABLE_FOUNDATION

已有基础，但不满足 Agent product goal。

## PARTIAL

有部分行为。

## MISSING_10L

Phase 10L Initial Release 必须解决。

## DEFER_10M

属于 Workspace。

## DEFER_10N

属于 scientific tool coverage。

## FUTURE

非初版。

## NOT_NEEDED

不需要。

---

# 79. 必须形成 Agent / Planner Gap Matrix

新增：

```text
docs/phase10l/phase10l0_agent_planner_gap_matrix.md
```

或等价文件。

至少包含：

| Capability | Current Implementation | Evidence | Status | Target Phase |
| ---------- | ---------------------- | -------- | ------ | ------------ |

覆盖：

* user intent
* DataProfile awareness
* tool capability metadata
* tool selection
* params selection
* single-tool plan
* multi-tool plan
* dependencies
* artifact binding
* PlanValidator
* ambiguity
* clarification
* plan repair
* result interpretation
* user plan inspection
* execution safety

---

# 80. 必须形成 Planner Maturity Assessment

输出一个明确 maturity level。

建议：

## Level 0

Manual tool execution

## Level 1

Keyword routing

## Level 2

Structured single-tool planning

## Level 3

Data/profile-aware tool selection

## Level 4

Capability-aware multi-tool planning

## Level 5

Bounded interpretation/repair

选择当前真实 level。

也可以用 repository 更适合的等级，但必须定义。

---

# 81. 10L-1 Scope Recommendation

本阶段最终必须向 reviewer 推荐：

**Analysis Intent Contract 到底需不需要独立存在。**

可能结果：

### A — REQUIRED

当前只有 raw prompt。

需要明确 intent contract。

### B — LIGHTWEIGHT_EXTENSION

当前已有足够 PlannerRequest，只需增加少量结构化 fields。

### C — ALREADY_EXISTS

已有 equivalent。

则 10L-1 应调整为 hardening，而不是重复造 contract。

必须选一个。

---

# 82. 10L-2 Scope Recommendation

回答：

Capability-Aware Planner 真正缺什么？

候选：

* profile context
* structured capability metadata
* eligibility resolver
* tool ranking
* params binding
* ambiguity handling

只建议。

不实现。

---

# 83. 10L-3 Scope Recommendation

根据真实 multi-tool能力判断：

### Case A

已有 multi-tool execution：

只补 dependency/selection。

### Case B

schema 支持多 tool，但 runtime不完整：

需要 execution hardening。

### Case C

完全 single-tool：

可能需要 contract evolution。

必须明确。

---

# 84. 10L-4 Scope Recommendation

根据现有 summary/report能力判断：

* 从零实现？
* 扩展 existing LLM summary？
* 只需要 structured result context + guardrails？

必须给 recommendation。

---

# 85. 10L-5 Scope Recommendation

规划最终 natural-language evidence cases。

至少建议：

* dataset analysis
* structure analysis
* model evaluation
* phonon
* volumetric

但不要写 implementation prompt。

---

# 86. Critical Reviewer Decisions

最终列出：

# Reviewer Decisions Required Before Phase 10L-1

只列真正需要人工决定的架构点。

例如：

1. 是否需要独立 AnalysisIntent schema？
2. 是否允许 AnalysisPlan schema evolution？
3. multi-tool 采用 ordered sequence 还是 dependency graph？
4. artifact binding最小模型是什么？
5. clarification 是否进入 Initial Release？
6. plan repair 是否进入 Initial Release？
7. capability metadata 放 Tool Registry 还是独立 resolver？

不要自己决定这些高影响问题，除非 current architecture 已经事实上确定。

---

# 87. Architecture Constraints Already Frozen

以下不需要 reviewer重新决定：

## LLM Does Not Execute Code

继续成立。

## Tool Registry Is Execution Boundary

继续成立。

## PlanValidator Before Runtime

继续成立。

## DataProfile Is Deterministic Data Truth

继续成立。

## Scientific Calculations Are Deterministic Backend

继续成立。

## LLM Can Plan / Explain

但不能虚构未计算结果。

---

# 88. Documentation

建议新增：

```text
docs/phase10l/
  phase10l0_agent_planner_capability_audit.md
  phase10l0_agent_planner_gap_matrix.md
  phase10l0_current_planner_architecture.md
  phase10l0_phase10l_scope_recommendation.md
  phase10l0_reviewer_decisions.md
```

允许合并重复文档。

不要生成 10L-1 implementation prompt。

这是 reviewer gate。

---

# 89. Canonical Roadmap

不要修改：

Phase 10L high-level roadmap。

可以在 Phase 10L docs 中提出：

`RECOMMENDED INTERNAL SCOPE ADJUSTMENT`

但：

不得自行改变：

* Phase number
* future sequence
* current roadmap authority

---

# 90. Persistent Updates

更新：

```text
persistent/DESIGN_PROGRESS.md
persistent/TASK_BOARD.md
persistent/CHANGELOG.md
persistent/OPEN_QUESTIONS.md
persistent/TOOL_REGISTRY_NOTES.md
persistent/ARCHITECTURE_DECISIONS.md
```

但 ARCHITECTURE_DECISIONS：

只记录审计确认的现状或既有事实。

不要提前冻结 reviewer 尚未批准的新 architecture。

---

# 91. DESIGN_PROGRESS

记录：

* Phase 10K complete
* Phase 10L-0 audit
* current Planner maturity
* critical gaps
* reviewer gate

---

# 92. TASK_BOARD

执行中：

```text
10L-0 = IN_PROGRESS
```

完成后：

```text
10L-0 = COMPLETE / ARCHIVED

10L-1 = REVIEWER_GATE
```

不得：

```text
10L-1 = NEXT_AUTOMATIC
```

---

# 93. OPEN_QUESTIONS

将真正需要 reviewer 决定的 Agent architecture问题列为 ACTIVE。

已经由代码事实回答的问题关闭。

---

# 94. TOOL_REGISTRY_NOTES

记录：

当前 Registry 对 Planner 的可用 metadata。

重点：

* resource requirements
* semantic requirements
* outputs
* descriptions
* caps

并指出 missing planner-facing metadata。

不修改 Tool definitions。

---

# 95. Architecture Decision Records

如果发现 repository 已经通过代码事实确立：

例如：

> AnalysisPlan supports ordered multiple ToolCalls

可以在 ADR/persistent 中记录现状。

但不要把：

“我们建议 future 使用 DAG”

写成已决定 ADR。

---

# 96. Audit Tests

本阶段不新增 production feature。

但可以运行现有 Planner tests。

至少：

```bash
uv run python -m pytest -q
npm --prefix apps/web test
npm --prefix apps/web run typecheck
npm --prefix apps/web run build
```

以及：

* Planner-specific unit tests
* PlanValidator tests
* service-backed integration
* no-skipped assertion
* docs consistency
* TASKS/result consistency
* security scan

---

# 97. Optional Read-Only Probe Tests

如果需要确认 planner behavior：

允许使用：

* existing test client
* Mock Planner
* fixed fixtures
* local deterministic service stack

禁止：

* real LLM
* external network
* production provider

---

# 98. No Real LLM

本阶段必须明确：

```text
REAL_LLM_CALLS = 0
```

如果已有 test gate会自动 skip real provider：

如实报告。

不得用用户 API key。

---

# 99. External Network

必须：

```text
NO_PHASE10L0_EXTERNAL_NETWORK_REQUESTS
```

或 repository等价 marker。

---

# 100. Secret Scan

必须：

```text
NO_SECRET_PATTERN_HITS
```

---

# 101. No Source Implementation Changes

理想状态：

本阶段 source implementation changes：

`NONE`

如果为了 audit 增加非常小的 test helper：

必须解释。

不得修改 Planner行为。

最终 report 必须单独列：

`Production Planner Behavior Changes: NONE`

---

# 102. Commit

完成 audit/docs/persistent 后：

```bash
git status --short
git diff --stat
git diff --check
```

只 stage Phase 10L-0相关文件。

禁止：

```bash
git add .
```

建议 commit：

```text
Audit agent planner capabilities
```

遵循 repository style。

push：

`origin master`

---

# 103. Current-HEAD CI

必须验证 exact audit commit SHA：

* Unit Tests
* Frontend Typecheck & Build
* Service-backed Integration
* no-skipped assertion

全部 success。

---

# 104. Completion Record

CI success 后：

写 Phase 10L-0 completion record。

记录：

* current Planner architecture
* maturity
* DataProfile use
* registry use
* AnalysisPlan capabilities
* multi-tool reality
* validator
* result interpretation
* gaps
* recommended 10L scope
* reviewer decisions

然后 commit。

---

# 105. Completion-Record CI

验证 completion-record exact SHA。

成功后 archive 10L-0。

---

# 106. Queue Barrier

最终必须保证：

```text
Phase 10L-0:
ARCHIVED

Phase 10L-1:
REVIEWER_GATE / AWAITING REVIEWER PROMPT
```

TASKS 不得含可自动执行的 10L-1 implementation block。

---

# 107. Final Report Format

最终严格输出：

# Phase 10L-0 Agent / Planner Capability Audit Result

## 1. Conclusion

PASS / PARTIAL_PASS / FAIL

## 2. Baseline

* Phase 10K completion:
* 10K-5 archive:
* branch:
* initial HEAD:
* origin/master:
* git status:

## 3. Current Planner Architecture

列出真实 flow：

```text
...
```

包括：

* API
* Mock Planner
* LLM Planner
* AnalysisPlan
* PlanValidator
* Runtime
* Tool Registry
* Artifact

## 4. Current AnalysisPlan

* schema/version:
* ToolCall count:
* ordering:
* dependencies:
* artifact binding:
* persistence:
* versioning:
* failure semantics:

## 5. Multi-Tool Reality

明确选择：

* NOT_SUPPORTED
* SCHEMA_ONLY
* SEQUENTIAL_INDEPENDENT
* ORDERED_MULTI_TOOL
* DEPENDENCY_AWARE

并给证据。

## 6. Mock Planner

* routing style:
* keyword dependence:
* resource awareness:
* DataProfile awareness:
* Registry awareness:
* ambiguity:
* params generation:

最终 classification。

## 7. LLM Planner

* provider architecture:
* prompt inputs:
* DataProfile context:
* Tool Registry context:
* JSON/schema enforcement:
* validation:
* retry:
* repair:
* fallback:

本阶段：

`REAL_LLM_CALLS = 0`

## 8. DataProfile → Planner Integration

逐项：

* resource kind:
* composition:
* properties:
* structure:
* trajectory:
* phonon:
* volumetric:
* regression:
* uncertainty:
* classification:
* readiness:

分别：

Mock / LLM / Validator。

## 9. Tool Registry Planner Readiness

* total tools:
* domains:
* descriptions:
* params schemas:
* resource requirements:
* semantic requirements:
* output metadata:
* caps:
* planner hints:

最终：

EXECUTION_REGISTRY / PARTIAL_PLANNER_REGISTRY / PLANNER_CAPABILITY_REGISTRY

## 10. PlanValidator

* tool allowlist:
* params:
* resource:
* profile:
* semantics:
* caps:
* multi-tool:
* dependency:
* artifact binding:

最终 maturity classification。

## 11. Tool Selection

按 domain：

* table:
* composition:
* structure:
* trajectory:
* phonon:
* BZ:
* volumetric:
* dataset:
* ML:
* composition space:

说明 current mechanism。

## 12. Representative Prompt Audit

逐 case：

### Composition

prompt:
current result:
gap:

### Structure

...

### ML

...

### Uncertainty

...

### Phonon

...

### Volumetric

...

### Broad Dataset Intent

...

### Explicit Single Tool

...

## 13. Analysis Intent

* existing object:
* raw prompt only:
* structured goal:
* targets:
* constraints:
* desired outputs:

结论：

* REQUIRED
* LIGHTWEIGHT_EXTENSION
* ALREADY_EXISTS

## 14. Ambiguity / Clarification

* semantic ambiguity:
* clarification state:
* user follow-up:
* current behavior:

## 15. Plan Repair

* JSON repair:
* schema repair:
* validation repair:
* scientific capability repair:
* retry limits:

## 16. Result Interpretation

* existing deterministic summaries:
* LLM summaries:
* structured context:
* hallucination guardrails:
* next-step recommendations:

## 17. Frontend Planner UX

* prompt:
* resource selection:
* plan inspection:
* validation:
* execution:
* timeline:
* edit:
* retry:
* cancel:
* artifacts:

## 18. Security Boundary

* arbitrary Python:
* shell:
* direct library execution:
* unknown tools:
* invalid params:
* prompt injection:
* artifact content:
* external network:

## 19. Planner Test Coverage

* Mock:
* LLM fixture:
* PlanValidator:
* runtime:
* service-backed:
* browser:
* real-provider gated tests:

## 20. Planner Maturity

使用正式定义：

Level 0–5

或 audit文档中定义的等价体系。

给出：

`CURRENT_LEVEL = ...`

和证据。

## 21. Gap Matrix

按：

* READY
* REUSABLE_FOUNDATION
* PARTIAL
* MISSING_10L
* DEFER_10M
* DEFER_10N
* FUTURE
* NOT_NEEDED

总结。

## 22. Recommended Phase 10L Scope

### 10L-1

* recommendation:
* contract need:
* exact problem:

### 10L-2

* planner gap:
* capability metadata:
* profile context:
* selection:

### 10L-3

* current multi-tool baseline:
* required evolution:
* dependency/artifact binding:

### 10L-4

* current interpretation baseline:
* required work:

### 10L-5

* natural-language evidence recommendation:

## 23. Reviewer Decisions Required

列真正需要 reviewer 决策的问题。

不要自行决定。

## 24. Production Behavior Changes

必须输出：

```text
Production Planner Behavior Changes:
NONE
```

如果不是 NONE：

说明为什么，并且本阶段原则上不得 PASS。

## 25. Files Changed

只能主要是：

* docs
* persistent
* TASKS
* result/evidence
* tests if audit-only

## 26. Checks

* git diff --check:
* uv lock:
* backend:
* frontend:
* typecheck:
* build:
* Planner tests:
* PlanValidator:
* service-backed:
* no-skipped:
* docs:
* TASKS:
* security:

## 27. Security

必须：

```text
REAL_LLM_CALLS = 0
NO_PHASE10L0_EXTERNAL_NETWORK_REQUESTS
NO_SECRET_PATTERN_HITS
```

或 repository真实等价 marker。

## 28. Commit / CI

### Audit Commit

* commit:
* exact SHA:
* CI:

### Completion Record

* commit:
* exact SHA:
* CI:

## 29. Queue State

必须：

```text
Phase 10L-0:
ARCHIVED

Phase 10L-1:
REVIEWER_GATE / AWAITING REVIEWER PROMPT
```

## 30. Whether Allowed to Enter Phase 10L-1 Automatically

必须写：

```text
NO
```

理由：

Phase 10L-1 requires reviewer review of the real Phase 10L-0 architecture audit.

## 31. Next Action

必须写：

> Return Phase 10K-5 and Phase 10L-0 results to the reviewer for Phase 10L architecture decision and Phase 10L-1 execution prompt.

不得开始实现。

---

# 108. PASS 标准

Phase 10L-0 只有全部满足才能 PASS：

1. Phase 10K 完整 CLOSED。
2. 真实审计 repository，不只读 docs。
3. AnalysisPlan contract审计完成。
4. multi-tool真实能力审计完成。
5. dependency representation审计完成。
6. artifact binding审计完成。
7. Mock Planner routing审计完成。
8. keyword dependency明确。
9. DataProfile use明确。
10. LLM Planner context明确。
11. Tool Registry planner metadata明确。
12. PlanValidator maturity明确。
13. params selection机制明确。
14. ambiguity behavior明确。
15. clarification能力明确。
16. plan repair能力明确。
17. runtime boundary明确。
18. Planner无法任意执行代码得到确认。
19. frontend Planner UX审计完成。
20. result interpretation baseline明确。
21. security boundary审计完成。
22. caps审计完成。
23. tests/evidence coverage审计完成。
24. representative prompts完成。
25. Planner maturity level明确。
26. Agent/Planner Gap Matrix完成。
27. 10L-1 scope recommendation完成。
28. 10L-2 scope recommendation完成。
29. 10L-3 scope recommendation完成。
30. 10L-4 scope recommendation完成。
31. 10L-5 evidence recommendation完成。
32. reviewer decision list完成。
33. 无 production Planner behavior change。
34. 无 AnalysisPlan schema change。
35. 无 Tool Registry contract change。
36. 无 PlanValidator behavior change。
37. 无 Runtime behavior change。
38. 无新 dependency。
39. 无真实 LLM call。
40. 无 external network。
41. secret scan PASS。
42. regression checks PASS。
43. audit exact-SHA CI success。
44. completion-record exact-SHA CI success。
45. 10L-0 archived。
46. 10L-1 NOT automatically queued。
47. reviewer gate明确。
48. origin/master == HEAD。
49. git clean。

---

现在开始。

第一步：

**不要修改 Planner implementation。**

先输出：

# Phase 10L-0 Entry / Current Planner Architecture Audit

必须基于真实代码回答：

1. Phase 10K 是否正式 COMPLETE？
2. 当前 Planner 入口在哪里？
3. Mock Planner 如何选择 tool？
4. LLM Planner 实际收到什么 context？
5. DataProfile 2.0 是否真的进入 Mock Planner？
6. DataProfile 2.0 是否真的进入 LLM Planner？
7. Tool Registry 向 Planner 暴露哪些 metadata？
8. AnalysisPlan 是 single-tool 还是 multi-tool？
9. 如果是 multi-tool，runtime 是否真的支持？
10. 是否存在 dependencies？
11. 是否支持 previous-artifact binding？
12. PlanValidator 到底验证到哪一层？
13. semantic readiness 在 Planner/Validator/Adapter 哪一层检查？
14. ambiguous semantics 当前如何处理？
15. 是否已有 structured intent object？
16. 是否已有 plan repair？
17. 是否已有 scientific result interpretation？
18. frontend 能否 inspect/edit plan？
19. 当前 Planner 最准确的 maturity classification 是什么？
20. Phase 10L-1～10L-5 各自真正需要解决什么？

Audit 完成后继续完成：

* Gap Matrix
* architecture docs
* persistent updates
* tests
* commit
* CI
* completion record
* archive

然后强制停止。

最终状态必须是：

**Phase 10L-1 = REVIEWER_GATE / AWAITING REVIEWER PROMPT**

完成时间：2026-07-29 09:32:06 +08:00

修改文件：`TASKS.md`、`results.md`、`docs/index.md`、
`docs/phase10l/`、`persistent/PROJECT_BRIEF.md`、
`persistent/DESIGN_PROGRESS.md`、`persistent/TASK_BOARD.md`、
`persistent/CHANGELOG.md`、`persistent/OPEN_QUESTIONS.md`、
`persistent/TOOL_REGISTRY_NOTES.md`、
`persistent/ARCHITECTURE_DECISIONS.md`。

修改摘要：完成 Mock/LLM Planner、DataProfile 2.0、AnalysisPlan、Tool
Registry、PlanValidator、QueueWorkerRuntime、持久化、前端 Planner UX、代表性
prompt、安全和 caps 的实现级审计；当前成熟度判定为 Level 3
`PROFILE_AWARE_SINGLE_TOOL_PLANNER`，仅存在一个窄范围的 sequential-independent
两工具组合。生产 Planner 行为、schema、Registry、Validator 与 Runtime 均未修改。

测试结果：Planner focused `92 passed, 1 skipped`；backend full `837 passed,
27 skipped`；frontend full `323 passed`；typecheck/build、Phase 10 closure、
evidence/TASKS/docs、`uv lock --check`、`git diff --check` 和安全 marker 通过。
本机 service-backed 因无 Docker 为 `UNAVAILABLE`（`25 skipped`）；audit commit
`a7f8b143129d4cf3ced95373d8d81199b06f7ca6` 的 exact-SHA CI run
`30414233888` 已通过 Unit、Frontend、service-backed 和 no-skipped。
Completion-record CI 与队列归档待后续 gate 完成。

---END---
