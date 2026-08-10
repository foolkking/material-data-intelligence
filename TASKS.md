---TASK---
状态：处理中
 状态：待处理

# Phase 12-2 Reviewer Prompt

# Global Navigation + Planner / Agent Experience

你现在执行：

# Phase 12-2：Global Navigation + Planner / Agent Experience

中文：

# 全局导航 + Planner / Agent 核心分析体验重构

本阶段属于：

```text
Phase 12:
Comprehensive UI / UX
Product Experience Redesign
```

Phase 12 顺序：

```text
12-0
Current UX Reality Audit
+ Product Experience Seal
= COMPLETE

12-1
Design System 2.0
+ Visual Language
= COMPLETE

12-2
Global Navigation
+ Planner / Agent Experience
= CURRENT AUTHORIZED PHASE

12-3
Scientific Workspace
+ Scientific Viewer Experience

12-4
Findings / Evidence /
Inspector / Provenance Experience

12-5
Report / Recipe Experience

12-6
Responsive / Mobile /
Accessibility Closure

12-7
Cross-Product UX Validation
+ Design Evidence Closure
```

---

# 0. Mission

Phase 12-2 的目标不是重新设计 Planner 的科学逻辑。

目标是把现有已经成熟的：

```text
DataProfile
→ AnalysisIntent
→ Clarification
→ EligibilityResolution
→ capability-aware Planner
→ AnalysisPlan 0.1 / 0.2
→ PlanValidator
→ QueueWorkerRuntime
→ Artifact
→ Grounded Interpretation
→ ScientificWorkspace
```

转换成一条：

```text
用户可以理解
+
用户知道当前上下文
+
用户知道系统理解了什么
+
用户知道为什么需要澄清
+
用户知道哪些分析可用
+
用户知道准备执行什么
+
用户知道现在进行到哪里
+
用户知道结果在哪里
+
同时仍保留完整开发者审计信息
```

的产品体验。

核心链：

```text
Global Product Navigation

→ Data Context

→ Analysis Composer

→ Intent Understanding

→ Clarification

→ Capability / Eligibility

→ Human-Readable Analysis Plan

→ Explicit Execution State

→ Partial / Error / Unsupported Recovery

→ Result / Workspace Transition

→ Developer Details
```

---

# 1. Fundamental Rule

必须：

```text
UX_REDESIGN
!=
PLANNER_REDESIGN
```

12-2 可以改变：

```text
navigation presentation

information hierarchy

interaction layout

content grouping

labels/copy

progress representation

human-readable summaries

error/recovery presentation

responsive presentation

progressive disclosure
```

不能改变：

```text
scientific eligibility

Tool selection authority

parameter binding authority

Plan semantics

dependency semantics

Runtime execution semantics

Job state

Artifact semantics

interpretation grounding

Workspace scientific authority
```

---

# 2. Reviewer Authorization

正式授权：

```text
AUTHORIZED_PHASE = Phase 12-2

MAX_PHASES_EXECUTED = 1

PHASE_12_2_QUEUE_ADMISSION =
CONDITIONALLY_AUTHORIZED
```

只有 Entry Gate PASS 后才允许创建 Phase 12-2 task。

本 Prompt 不授权：

```text
Phase 12-3
Phase 12-4
Phase 12-5
Phase 12-6
Phase 12-7
Phase 13
```

---

# 3. Mandatory Phase 12-1 Dependency

必须从真实 repository 读取：

```text
results.md

TASKS.md

docs/ROADMAP.md

persistent/

docs/phase12/

docs/phase12/evidence/
```

验证：

```text
PHASE_12_1_IMPLEMENTATION_SHA

PHASE_12_1_IMPLEMENTATION_CI_RUN

PHASE_12_1_IMPLEMENTATION_CI_RESULT

PHASE_12_1_COMPLETION_SHA

PHASE_12_1_QUEUE_ARCHIVE_SHA
```

当前 reviewer 已知：

```text
Implementation:
60269556f70f07014224a801150f214887a56ee5

Implementation CI:
31358512349
success

Completion:
d6279e5f0f9d242d8a98cf5add7baef3749e22f2

Archive:
9cdd7765d3614649b9559d5d826638e5cf1ca87d
```

但必须从 Git history 动态验证。

---

# 4. Entry Repository State

必须：

```text
branch = master

HEAD == origin/master

worktree = clean

TASK_BLOCK_COUNT = 0
```

同时：

```text
PHASE_12_3_EXECUTABLE_TASK_CREATED = NO

PHASE_13_EXECUTABLE_TASK_CREATED = NO
```

否则：

```text
PHASE_12_2_ENTRY_GATE = BLOCKED
```

---

# 5. Current Lifecycle Policy

继续遵循：

```text
Implementation commit
→ push
→ WAIT exact-SHA CI

if PASS:

Completion record
→ commit
→ push directly

Queue archive
→ commit
→ push directly
```

因此最终只能说：

```text
IMPLEMENTATION_VERIFIED_BY_EXACT_SHA_CI

COMPLETION_RECORDED

QUEUE_ARCHIVED
```

如果 completion/archive 没有额外 CI：

禁止：

```text
VERIFIED_COMPLETION

VERIFIED_QUEUE_ARCHIVE
```

---

# 6. Design System 2.0 Authority

必须确认：

```text
DESIGN_SYSTEM_VERSION = 2.0
```

并验证 semantic hash：

```text
2a87269216cddb1193af9a08ae7b136889ba43905532e508042b78369a68714d
```

或者 current repository canonical equivalent。

如果 hash 与当前 sealed Phase 12-1 authority 不一致：

必须先解释变更来源。

未经 reviewer 批准的 DS2 authority drift：

```text
BLOCKED /
DESIGN_SYSTEM_BASELINE_DRIFT
```

---

# 7. Required 12-1 Handoff

必须读取：

```text
Phase12_2NavigationPlannerHandoff
```

或 current canonical equivalent。

至少验证其中：

```text
Design System version

token registry hash

shared component registry

navigation primitives

form primitives

status primitives

responsive primitives

accessibility primitives

remaining Phase 12-2 UX problems

Global IA target

Planner surface inventory

scientific authority constraints

evidence refs
```

不得重新创建平行 handoff authority。

---

# 8. Phase 12-0 Authority

必须继续读取：

```text
phase12_product_experience_principles

phase12_ui_surface_registry

phase12_user_journey_matrix

phase12_ux_problem_matrix

phase12_information_architecture_audit

phase12_planner_agent_ux_audit

phase12_error_state_recovery_matrix

phase12_terminology_i18n_glossary

phase12_experience_decision_registry

phase12_implementation_backlog

phase12_acceptance_and_test_plan

phase12_execution_lock

phase12_execution_manifest
```

repository canonical wording优先于本 Prompt 的概括。

---

# 9. Product Experience Principles Remain Frozen

继续：

```text
Meaning before mechanism

Result before Artifact

Progressive disclosure

Scientific limitations are first-class

One clear primary action per context

State understandable without color

Exact scientific identity remains available

Desktop/mobile share authority

Heavy viewers remain lazy

Errors preserve context

Developer details remain available
but subordinate

No UX convenience creates
scientific authority
```

---

# 10. Global IA Authority

目标 Global IA 已 seal 为：

```text
Home

Data

Analyses

Workspaces

Reports

Settings
```

Phase 12-2 负责将这套 IA 产品化。

不是重新提案。

---

# 11. Route Mapping Must Come From Canonical Handoff

重要：

Global IA 的：

```text
label
destination
route
query/state behavior
back/forward semantics
```

必须读取：

```text
Phase 12-0 / 12-2 canonical handoff
+
current frontend route reality
```

不得 execution agent 自己发明新的 route architecture。

---

# 12. Existing Canonical Routes Must Remain Valid

至少必须保持：

```text
/
```

现有 PlannerWorkbench / analysis-entry compatibility。

以及：

```text
/workspaces/{workspaceId}
```

ScientificWorkspace canonical deep link。

不得破坏历史链接。

---

# 13. Additive Frontend Navigation Routes

只有在 Phase 12 canonical backlog/handoff 已明确授权时：

才允许添加纯 frontend presentation routes。

任何新增 route：

必须：

```text
reuse existing backend authorities

create no new scientific authority

create no new domain entity authority

preserve existing deep links

preserve browser back/forward
```

如果实现 Global IA 需要新的 backend API family：

```text
BLOCKED /
BACKEND_PRODUCT_CAPABILITY_REQUIRED
```

不得偷偷新增。

---

# 14. No Fake Navigation

禁止：

```text
dead nav item

fake placeholder pretending feature exists

empty page labelled supported

navigation entry implying capability
that product does not have
```

任何 destination 必须是：

```text
FUNCTIONAL

or

HONEST_TYPED_UNAVAILABLE
```

但如果 canonical Phase 12-2 acceptance要求它必须 functional：

typed unavailable不能代替完成。

---

# 15. Global Product Shell

必须形成一致：

```text
product identity

primary navigation

current context

primary action

status/notifications if actually available

settings access
```

的 shell。

使用 DS2。

不得重新创建第三套视觉语言。

---

# 16. Navigation Hierarchy

Primary navigation：

```text
Home
Data
Analyses
Workspaces
Reports
Settings
```

应该回答：

```text
Where am I?

What can I do here?

What context am I operating on?

How do I return?
```

---

# 17. Active Navigation State

必须：

```text
textually identifiable

visually distinct

keyboard accessible

not color-only
```

并保持：

```text
URL / product state
```

一致。

---

# 18. Navigation Accessibility

必须：

```text
semantic nav landmark

accessible names

keyboard reachable

visible focus

current-page semantics

mobile equivalent
```

---

# 19. Navigation Must Not Display Invented Counts

例如：

```text
Analyses 12

Reports 7
```

只有 authoritative bounded read path存在时才能显示。

禁止通过 frontend猜测。

---

# 20. Home Experience

Home 的职责是：

```text
orient user

show current/recent relevant context
where existing authority supports it

make Start Analysis obvious

expose data readiness

expose existing Workspace access
```

不是 marketing landing page。

---

# 21. Data Experience Boundary

Data navigation/surface应该让用户理解：

```text
current dataset

version

available resources

Profile readiness

key recognized semantics

limitations
```

但：

```text
DataProfile remains backend authority
```

UI 不 recompute Profile。

---

# 22. Data Context Must Be Visible Before Analysis

Planner primary composer附近应清楚看到：

```text
which dataset

which version

which selected resources

Profile readiness

important availability/limitations
```

而不是用户输入 prompt 后才发现分析对象错误。

---

# 23. No Raw Profile Dump By Default

普通用户默认不应先看到：

```text
profileContractVersion

semanticHash

objectHash

raw schema

raw JSON
```

默认应看到：

```text
Data ready

N samples

available structure/trajectory/etc.

recognized targets/properties

relevant warnings
```

实际内容必须来自 authoritative Profile。

---

# 24. Exact Profile Details Remain Accessible

通过：

```text
Details

Developer Details

Provenance
```

保留：

```text
Profile ID

version

semantic hash

resource IDs
```

等 exact facts。

---

# 25. Analyses Experience

Analyses 应围绕：

```text
analysis intent

status

dataset/context

created time if authoritative

result availability

Workspace availability
```

组织。

不要默认围绕：

```text
ToolCall ID
Plan hash
provider payload
```

组织。

---

# 26. Workspaces Experience

Workspaces navigation必须尊重：

```text
ONE_WORKSPACE_PER_JOB
```

以及现有 project-scoped Workspace APIs。

不能创建第二套 session/workspace entity。

---

# 27. Reports Experience Boundary

Global Reports navigation只能消费现有：

```text
Report
Recipe
Workspace report composition/history
```

authority。

不得生成：

```text
frontend-only report truth
```

---

# 28. Settings Experience

Settings只允许呈现/操作：

```text
current product settings
actually supported by existing authority
```

不得借 UX redesign：

```text
add unsupported provider
add arbitrary API key
add hidden scientific defaults
```

---

# 29. DeepSeek Policy Freeze

Real provider继续：

```text
DeepSeek only
```

固定 endpoint：

```text
https://api.deepseek.com
```

allowlisted models：

```text
deepseek-v4-flash
deepseek-v4-pro
```

key source：

```text
DEEPSEEK_KEY
```

---

# 30. No Frontend API Key Input

必须：

```text
NO_FRONTEND_LLM_KEY_INPUT = PASS
```

Settings 可以展示：

```text
configured / unavailable
provider/model identity
```

但不能暴露 secret。

---

# 31. Planner Primary Experience

Planner 默认界面优先：

```text
Data Context

What do you want to understand?

Suggested analyses if authoritative

Prompt Composer

Current understanding

Clarification if required

Analysis approach

Run / progress

Result / Workspace
```

而不是：

```text
Intent JSON

EligibilityResolution JSON

ToolPlannerMetadata

Plan hash

Tool IDs

bindings

Artifact contracts
```

---

# 32. Meaning Before Mechanism

Planner 默认必须：

```text
HUMAN_MEANING_FIRST = YES
```

Developer detail必须：

```text
AVAILABLE
BUT
SECONDARY
```

---

# 33. Prompt Composer

Prompt Composer应成为 Planner 的明显 primary task surface。

必须审计/改进：

```text
selected data context

input affordance

placeholder

example prompts

submit/run state

disabled reason

loading state

error state

keyboard behavior

mobile input behavior
```

---

# 34. Prompt Examples

如果展示 example prompts：

必须：

```text
bounded

scientifically honest

compatible with current product
```

不得展示 Future Scope prompt作为看似可执行示例。

---

# 35. Suggested Analysis Authority

如果展示：

```text
Suggested analyses
```

建议必须来自：

```text
DataProfile

+
Eligibility / capability facts
```

或 deterministic allowlisted product logic。

不能来自：

```text
random LLM suggestion
```

---

# 36. Suggestion Is Not Execution

永久：

```text
SUGGESTION
!=
EXECUTION
```

用户选择 suggestion最多：

```text
populate intent/prompt
```

仍必须经过：

```text
Intent
Eligibility
Planner
Plan validation
```

---

# 37. AnalysisIntent UX

UI必须以 human-readable 方式展示：

```text
What the system understood
```

例如：

```text
Goal

selected data

target/property

desired result

relevant constraints
```

---

# 38. Intent Authority

不得由 frontend重新解析自然语言得到新的 scientific intent。

UI只能：

```text
render persisted / backend-resolved AnalysisIntent
```

---

# 39. Raw Goal vs Interpretation

如果展示：

```text
Your request
```

和：

```text
Understood as
```

必须明确两者区别。

不能把 normalized intent伪装成用户原话。

---

# 40. Clarification UX

当：

```text
NEEDS_CLARIFICATION
```

必须：

```text
make reason understandable

preserve original request

show valid bounded choices

show current data context

make one required response obvious

preserve keyboard focus

work on mobile
```

---

# 41. Clarification Choice Authority

Choice options只能来自 existing exact：

```text
Profile

resource

target

model

group
```

facts。

UI不得添加推测 option。

---

# 42. Clarification Developer Detail

这些：

```text
question ID

intent hash

Profile hash

option identity
```

可在 developer details中显示。

默认用户层只显示：

```text
what needs clarification
+
why
+
valid choices
```

---

# 43. One-Round Clarification Boundary

当前 contract：

```text
MAX_CLARIFICATION_ROUNDS = 1
```

Phase 12-2 不得通过 UI 制造：

```text
multi-turn autonomous clarification
```

---

# 44. Unsupported Intent UX

`UNSUPPORTED` 必须回答：

```text
What is unsupported?

Why?

Is it the data,
capability,
input,
or future scope?

What can the user do next?
```

---

# 45. Future Scope UX

Future Scope不能显示成：

```text
disabled button without explanation
```

必须明确：

```text
Not available in Initial Release
```

或 canonical wording。

---

# 46. Eligibility UX

Eligibility默认展示：

```text
Available analysis capabilities

Unavailable relevant capabilities

why unavailable
```

而不是优先：

```text
eligibleToolIds[]
rejectedToolIds[]
```

---

# 47. Tool Identity Remains Accessible

advanced detail中仍允许：

```text
Tool ID

Tool version

binding source

eligibility diagnostic
```

确保 auditability。

---

# 48. Eligibility Cannot Be Recomputed Frontend

必须：

```text
FRONTEND_ELIGIBILITY_RECOMPUTATION = 0
```

UI 不得根据 button state / string keyword自己判断 capability。

---

# 49. Capability Mismatch UX

`CAPABILITY_MISMATCH` 必须：

```text
distinct from generic failure
```

因为这不是：

```text
server crashed
```

而是：

```text
current data/request
does not match executable capability
```

---

# 50. Planner Outcome Vocabulary

必须消费 existing authoritative outcomes，例如：

```text
READY

NEEDS_CLARIFICATION

UNSUPPORTED

PLAN_READY

CAPABILITY_MISMATCH

VALIDATION_FAILED
```

实际 current contracts为 authority。

不要创建 backend-like fake states。

---

# 51. Human-Readable Plan

AnalysisPlan UI默认必须先回答：

```text
What will be done?

In what order?

What will be produced?

What depends on what?

What is limited?
```

---

# 52. Human Plan Before Tool Plan

硬规则：

```text
HUMAN_PLAN_FIRST = YES
```

默认类似：

```text
1. Analyze the supplied trajectory
2. Compute mean-squared displacement
3. Estimate diffusion over the selected fit window
```

而不是首先：

```text
step_001
trajectory.msd@0.1.0
dependencyBinding xyz
```

---

# 53. No Scientific Rewording Beyond Authority

Human plan可以改变表达方式。

不能：

```text
turn algorithm-derived result
into definitive scientific claim
```

例如：

```text
Estimate diffusion
```

不能写成：

```text
Determine the true diffusion coefficient
```

---

# 54. Plan 0.1 Support

AnalysisPlan 0.1：

必须继续显示为：

```text
ordered independent/sequential analysis steps
```

不得 UI invent dependency graph。

---

# 55. Plan 0.2 Support

AnalysisPlan 0.2：

允许 human-readable dependency explanation。

例如：

```text
Band and DOS results
are combined after both are available
```

开发者层再显示 exact：

```text
step IDs

ports

bindings

graph hash
```

---

# 56. Dependency Visualization Boundary

如果使用视觉 dependency representation：

它必须来自 exact persisted:

```text
dependencyBindings
```

不能根据 list order推断。

---

# 57. No Plan Editor

Phase 12-2 不增加：

```text
arbitrary Plan editing

step reordering

Tool substitution

parameter mutation

dependency editing
```

除非当前 canonical backend已经支持并由 12-0明确授权。

默认：

```text
PLAN_EDITOR = NOT_AUTHORIZED
```

---

# 58. No Fake Approval Contract

如果 backend lifecycle当前并不存在：

```text
approve plan before job creation
```

UI 不得创造一个假审批按钮。

可以改善：

```text
plan visibility
```

不能改变 backend transaction semantics。

---

# 59. Run Authority

Run / Execute action必须严格对应 current API/lifecycle。

只有 authoritative ready state才能允许。

必须：

```text
NON_READY_RUN_DISABLED = YES
```

---

# 60. Disabled Run Must Explain Why

禁止：

```text
disabled button with no explanation
```

至少指出：

```text
clarification required

unsupported capability

invalid plan

missing data

provider unavailable
```

中的真实原因。

---

# 61. Execution Experience

必须把现有 runtime状态映射成可理解阶段。

12-0 audit target包括：

```text
Preparing

Planning

Validating

Queued

Running

Producing results

Interpreting

Building Workspace

Complete

Partial

Failed
```

实际映射必须来自 current event/state authority。

---

# 62. Presentation Phase Mapping

允许建立：

```text
PlannerExecutionPresentationState
```

但它必须是：

```text
many-to-one presentation projection
```

不是新 backend state machine。

---

# 63. State Mapping Registry

必须记录：

```text
sourceState

sourceAuthority

presentationLabel

presentationStage

userDescription

terminal?

partial?

error?

scientificAuthorityChanged = false
```

---

# 64. No Fake Progress Percentage

如果 backend没有真实百分比：

禁止：

```text
42%
78%
```

fake progress。

可使用：

```text
stage progress
indeterminate progress
completed steps / total steps
```

前提 authoritative。

---

# 65. ToolCall Detail

默认 execution UI：

优先显示：

```text
analysis step name

current state

duration if authoritative

output availability
```

ToolCall IDs 进入 developer detail。

---

# 66. Partial Execution

当存在：

```text
PARTIAL_RESULTS
```

必须同时表达：

```text
what succeeded

what failed

what was blocked

what remains available
```

不能只显示：

```text
Completed
```

---

# 67. Dependency Failure UX

`BLOCKED_DEPENDENCY`：

必须区别：

```text
step failed
```

和：

```text
step was never run
because dependency failed
```

---

# 68. Existing Successful Results Stay Visible

partial/failure时：

不得因一个 sibling failure：

```text
hide all successful results
```

---

# 69. Interpretation UX Boundary

Phase 12-2 可以在 Planner completion区展示：

```text
summary
finding count
warnings
limitations
```

但 Findings/Evidence 深层 UX 属于：

```text
Phase 12-4
```

---

# 70. No New Interpretation

12-2 不修改：

```text
ScientificEvidenceBundle

ScientificClaim

GroundedScientificInterpretation

projectors

grounding validator
```

---

# 71. Recommendations Boundary

Recommendation：

必须：

```text
executionAuthorized = false
```

不得显示成：

```text
Run recommendation
```

直接执行。

---

# 72. Planner → Workspace Transition

成功持久化分析后：

用户必须清楚知道：

```text
analysis exists

results are available

Workspace is the durable scientific result environment
```

---

# 73. Workspace Cardinality

继续：

```text
ONE_WORKSPACE_PER_JOB = YES
```

---

# 74. Workspace Opening

必须使用 current idempotent projection/open semantics。

禁止：

```text
frontend-generated Workspace identity

duplicate Workspace creation

latest Workspace guess
```

---

# 75. Explicit Workspace Transition

如果现有 lifecycle要求 explicit projection：

保留：

```text
explicit user-authorized Open Workspace
```

不得为了 UX convenience：

偷偷 create Workspace on unrelated GET。

---

# 76. Auto Navigation Boundary

如果 canonical handoff允许 completed Job 自动导航：

必须确保：

```text
Workspace identity already authoritative
```

否则不得自动生成 authority。

以 repository 12-2 handoff为准。

---

# 77. Workspace Deep Link

必须继续使用：

```text
/workspaces/{workspaceId}
```

且只使用 exact ID。

---

# 78. Analysis History

若 Analyses surface展示历史：

只能来自 existing authoritative read API。

至少显示：

```text
goal/intention

dataset/context

status

time if persisted

Workspace availability
```

---

# 79. Analysis History Does Not Reconstruct Science

列表 UI不得从：

```text
Artifact filenames
labels
latest record
```

重新推断 analysis type。

---

# 80. Error UX

Phase 12-2 至少覆盖 Planner-owned：

```text
validation error

clarification required

unsupported input/capability

provider unavailable/failure

plan validation failure

capability mismatch

queue/runtime failure

partial execution

blocked dependency

Workspace transition failure
```

---

# 81. Error Message Structure

默认：

```text
What happened?

Why?

What can I do?

What was preserved?
```

---

# 82. Technical Error Details

保留：

```text
error code

diagnostics

request/plan IDs

provider state

stack-safe audit detail
```

在 developer detail。

不得向普通用户直接暴露 stack/path。

---

# 83. Recovery

每个 recoverable Planner error必须有：

```text
clear next action
```

例如：

```text
Change selection

Answer clarification

Edit request

Retry eligible network/provider operation

Open existing results

Return to data
```

实际 action必须对应真实 authority。

---

# 84. No Unsafe Retry

不得添加：

```text
Retry
```

如果 retry可能：

```text
duplicate Job
duplicate ToolCall
duplicate execution
```

而 backend没有 idempotency contract。

---

# 85. Provider Failure

Provider failure不能重命名成：

```text
analysis unavailable
```

而掩盖 provider layer。

同时不能泄漏：

```text
secret
raw authorization
internal URL/path
```

---

# 86. Loading States

至少区分：

```text
loading data context

resolving intent

waiting clarification submission

resolving eligibility

planning

submitting/running

loading result summary

opening Workspace
```

---

# 87. Loading Must Preserve Context

加载时不应：

```text
blank entire Planner
```

导致用户忘记：

```text
dataset
prompt
current stage
```

---

# 88. Empty States

至少：

```text
no data selected

no analyses

no Workspace yet

no supported capability

no prior reports
```

需要：

```text
explanation
+
action
```

---

# 89. Planner Internal-Identifier Audit

必须测量：

```text
visible internal identifiers
```

12-0 baseline之后：

普通用户默认层应显著减少：

```text
Tool IDs
Artifact IDs
hashes
contract versions
step IDs
binding IDs
```

---

# 90. Exact IDs Cannot Disappear Entirely

developer/audit层必须仍然能够获取这些 exact IDs。

目标：

```text
SUBORDINATE
```

不是：

```text
DELETE
```

---

# 91. Progressive Disclosure Layers

Planner建议统一为：

```text
Layer 1:
User Meaning

Layer 2:
Analysis Details

Layer 3:
Developer / Provenance Details
```

实际 component naming可以依 DS2/current architecture调整。

---

# 92. Layer 1

默认显示：

```text
data context

request

understanding

clarification

availability

analysis approach

progress

result
```

---

# 93. Layer 2

可显示：

```text
selected capability

parameters in human language

dependency description

warnings

output types

limitations
```

---

# 94. Layer 3

可显示：

```text
Intent ID/hash

Eligibility ID/hash

Tool IDs/versions

Plan schema/hash

step IDs

bindings

ToolCall IDs

Artifact IDs/checksums

provider audit
```

---

# 95. Developer Detail Must Stay Inert

JSON / audit detail：

必须：

```text
text-only / inert
```

禁止执行：

```text
HTML
JavaScript
iframe
module
URL
```

---

# 96. Terminology

12-0 glossary是 authority。

优先产品词：

```text
Data

Analysis

Result

Finding

Evidence

Workspace

Report
```

内部词：

```text
Artifact

ToolCall

binding

contract
```

默认 subordinate。

---

# 97. Agent Terminology

不要把系统包装成：

```text
autonomous scientific agent
```

如果它实际上是：

```text
bounded intent
+
planner
+
validated runtime
+
grounded interpretation
```

---

# 98. “AI” Labeling

如果 UI 使用 AI/Agent wording：

必须不暗示：

```text
unbounded autonomy

scientific authority

automatic research
```

---

# 99. Provider vs Planner

UI必须区分：

```text
LLM/provider helps interpret/select
within bounded contract
```

与：

```text
system scientific execution
```

真正 science由 adapters/runtime执行。

---

# 100. Scientific Execution Authority

必须在 architecture/evidence中继续：

```text
LLM = Planner / Router / Explainer

LLM != Scientific Executor
```

---

# 101. Global Navigation on Workspace Route

进入：

```text
/workspaces/{workspaceId}
```

时 global shell应保持 product-level orientation。

但：

Workspace internal IA 的大规模 restructure 属于 12-3。

---

# 102. Workspace Internal Navigation Boundary

12-2 不能实施完整：

```text
Overview
Data
Analysis
Results
Findings
Evidence
Report
Provenance
Developer Details
```

Workspace reorganization。

12-3拥有该 scope。

---

# 103. Allowed Workspace Touches in 12-2

仅允许为：

```text
global shell integration

global navigation consistency

Planner→Workspace transition

breadcrumb/product orientation
```

做必要改动。

---

# 104. Viewer Boundary

禁止 12-2 重构：

```text
chart controls

3D controls

viewer chrome

Gallery behavior

scientific selection interactions
```

这些属于 12-3。

---

# 105. Findings/Evidence Boundary

禁止 12-2 完成：

```text
three-layer Inspector

evidence drilldown redesign

claim hierarchy redesign
```

这些属于 12-4。

---

# 106. Report/Recipe Boundary

禁止 12-2 完成：

```text
Report Builder UX

Recipe human-readable full redesign
```

属于 12-5。

---

# 107. Accessibility Boundary

12-2 必须保证所有自己改动的：

```text
navigation

Planner

clarification

plan

progress

errors
```

可访问。

但：

```text
FULL_PRODUCT_ACCESSIBILITY_COMPLETE = NO
```

直到 12-6/12-7。

---

# 108. Mobile Boundary

12-2 必须让：

```text
global nav
Planner composer
clarification
plan
progress
```

在 390x844 可用。

全产品 mobile closure属于 12-6。

---

# 109. Global Mobile Navigation

必须使用：

```text
bounded drawer/menu/presentation
```

不能让六项主导航产生横向 overflow。

---

# 110. Mobile Prompt Composer

必须：

```text
primary composer remains reachable

keyboard does not permanently obscure action

context remains understandable

submit action remains reachable

error/clarification remains visible
```

---

# 111. Touch Targets

所有 12-2 新/reworked touch controls：

```text
>= 44x44 CSS px
```

---

# 112. Focus

必须覆盖：

```text
nav opening/closing

prompt submit

clarification

plan details

error action

Workspace transition
```

focus order和 restoration。

---

# 113. Status Non-Color

所有：

```text
ready

clarification

unsupported

running

partial

failed

complete
```

状态：

不得仅靠颜色。

---

# 114. Screen Reader Status

重要 async state change：

应使用 appropriate live semantics。

不要把所有 DOM 变化都设为 aggressive live region。

---

# 115. 200% Zoom Foundation

至少测试：

```text
Global navigation

Planner

Clarification

Plan

Execution status
```

200% zoom 下：

```text
no essential control loss
```

---

# 116. Reduced Motion

使用 DS2 motion primitives。

必须尊重：

```text
prefers-reduced-motion
```

---

# 117. i18n

如果 current product支持：

```text
zh-CN
English
```

12-2 改过的所有 user-facing strings：

必须进入现有 i18n机制。

---

# 118. No New i18n Framework

必须：

```text
NEW_I18N_DEPENDENCIES = 0
```

---

# 119. Scientific Terms

特别审查：

```text
coordination

local environment

XRD comparison

diffusion estimate

Band Structure

DOS
```

不得因 UX copy简化而越过 Phase 11 claim boundaries。

---

# 120. Support / Validation Presentation

如果 Planner显示 capability status：

必须继续区分：

```text
available to run

scientifically validated

cross-platform replay

presentation verified
```

不能统一成：

```text
Verified
```

---

# 121. Phase 11 Scientific Authority Freeze

必须继续：

```text
Registry = 62

DataProfile = 2.4

AnalysisIntent = 1.0

EligibilityResolution = 1.0

AnalysisPlan = 0.1 / 0.2

migration =
0007_phase10m1_workspace_domain
```

---

# 122. Golden Evidence Honesty

继续：

```text
12 golden records

8 PASS_INVARIANT

4 NOT_APPLICABLE

numeric cross-platform =
NOT_APPLICABLE

V4 = 0
```

按 repository actual final authority动态检查。

---

# 123. No UI Scientific Promotion

必须：

```text
MAPPING_ONLY_VISUAL_UPGRADE = 0

NOT_APPLICABLE_VISUAL_UPGRADE = 0

V4_VISUAL_FABRICATION = 0
```

---

# 124. Frontend Scientific Computation

必须：

```text
PHASE12_2_FRONTEND_SCIENTIFIC_RECOMPUTATION = 0
```

---

# 125. Planner Scientific Contracts Freeze

不得修改：

```text
AnalysisIntent contract

EligibilityResolution contract

ToolPlannerMetadata contract

AnalysisPlan contract

dependency contract

ScientificEvidenceBundle

ScientificClaim
```

---

# 126. Planner Backend Freeze

默认：

```text
PLANNER_BACKEND_BEHAVIOR_CHANGES = 0
```

Phase 12-2 是 UX phase。

---

# 127. API Freeze

默认：

```text
NEW_PUBLIC_API_FAMILIES = 0
```

允许消费现有 APIs。

如果 UX 需要新的 business capability API：

停止并 reviewer。

---

# 128. Database Freeze

必须：

```text
NEW_DATABASE_TABLES = 0

NEW_DATABASE_COLUMNS = 0

NEW_DATABASE_MIGRATIONS = 0
```

migration保持：

```text
0007_phase10m1_workspace_domain
```

---

# 129. Dependency Freeze

必须：

```text
NEW_PYTHON_DEPENDENCIES = 0

NEW_FRONTEND_DEPENDENCIES = 0

LOCKFILE_CHANGES = 0
```

---

# 130. Design System Freeze

12-2 必须消费：

```text
DS2
```

不得开始：

```text
DS 2.1
```

除非是修正 12-2发现的明确 DS2 bug。

任何 token semantic change：

必须记录 reason。

---

# 131. DS2 Bug Fix Rule

允许：

```text
component bug fix

focus bug

responsive primitive defect

semantic token typo
```

如果确实阻塞 12-2。

不得借机重新设计整个 Design System。

---

# 132. LLM Calls

必须：

```text
PHASE12_2_NEW_LLM_CALL_SITES = 0
```

以及默认：

```text
PHASE12_2_REAL_LLM_CALLS = 0
```

UX browser evidence使用 persisted/fake/sanitized fixtures。

---

# 133. No Browser → DeepSeek Direct Calls

必须：

```text
NO_BROWSER_TO_DEEPSEEK_DIRECT_CALL = PASS
```

---

# 134. No External UX Assets

不得：

```text
download icons

download fonts

download illustrations

external CSS

external design system
```

---

# 135. Security

必须保持：

```text
NO_PHASE12_2_ARBITRARY_CODE_EXECUTION = PASS

NO_PHASE12_2_ARTIFACT_JAVASCRIPT = PASS

NO_PHASE12_2_ARTIFACT_HTML_EXECUTION = PASS

NO_PHASE12_2_IFRAME_EXECUTION = PASS

NO_PHASE12_2_EXTERNAL_ARTIFACT_URL_EXECUTION = PASS

NO_PHASE12_2_FRONTEND_LLM_SECRET_INPUT = PASS

NO_PHASE12_2_FRONTEND_SCIENTIFIC_RECOMPUTATION = PASS

NO_PHASE12_2_RECOMMENDATION_AUTO_EXECUTION = PASS

NO_SECRET_PATTERN_HITS = PASS
```

---

# 136. Exact 12-2 UX Problems

必须从：

```text
phase12_ux_problem_matrix
```

读取：

```text
owner = 12-2
```

所有 exact problem IDs。

Phase 12-1 completion显示：

```text
12-2 owned count = 2
```

因此预期：

```text
PHASE12_2_OWNED_PROBLEM_COUNT = 2
```

但必须动态验证。

---

# 137. Do Not Guess IDs

本 Prompt 不替 repository 编造：

```text
UX-XXX
```

execution agent必须输出 exact canonical IDs。

如果 count不是 2：

解释 repository-authorized变化来源。

---

# 138. Owned Problems Closure

全部：

```text
owner = 12-2
```

必须：

```text
FIXED_WITH_EVIDENCE
```

才能 PASS。

禁止：

```text
change owner

lower severity

delete row
```

逃避。

---

# 139. Future Owner Problems

其余：

```text
12-3 = 2
12-4 = 1
12-5 = 1
12-6 = 2
12-7 = 1
```

当前 known distribution。

必须动态读取 actual。

它们继续：

```text
OPEN / OWNED
```

---

# 140. Foundation Improvement

若 12-2 顺便改善 future problem：

记录：

```text
FOUNDATION_IMPROVED
```

但 owner 不改变，除非 exact acceptance已完整达到。

---

# 141. New UX Regression Rule

必须：

```text
NEW_P0_INTRODUCED_BY_12_2 = 0

NEW_P1_INTRODUCED_BY_12_2 = 0
```

---

# 142. Canonical Acceptance IDs

Phase 12-0已封板：

```text
P12X2-A01
...
P12X2-A08
```

必须从：

```text
phase12_acceptance_and_test_plan.md
```

读取 exact descriptions。

---

# 143. Do Not Rename Acceptance IDs

禁止：

```text
rename

delete

add

shorten

replace

merge
```

canonical P12X2 IDs。

要求：

```text
EXPECTED = 8
IMPLEMENTED = 8
MISSING = 0
EXTRA = 0
DUPLICATE = 0
CONFLICTING = 0
SHORTHAND = 0
```

---

# 144. Reviewer Interpretation of Acceptance Areas

repository exact wording优先。

但至少必须覆盖 equivalent scope：

```text
A.
Global product navigation
and IA implementation

B.
Data context
and analysis-entry experience

C.
Prompt composer
and Intent understanding

D.
Clarification
and Eligibility experience

E.
Human-readable Plan
with developer progressive disclosure

F.
Execution / partial / error /
recovery experience

G.
Planner → Workspace transition,
responsive and accessibility

H.
Cross-browser, regression,
scientific-authority, evidence
and lifecycle closure
```

---

# 145. Canonical Journey Coverage

至少重新验证与 12-2相关：

```text
New data
→ analysis

Natural-language analysis

Unsupported analysis

Clarification

Partial execution

Provider unavailable

Analysis completion
→ Workspace

Mobile analysis
```

---

# 146. Do Not Claim Human Usability Study

Automation click counts、elapsed time：

只能：

```text
interaction proxy
```

不得说：

```text
human usability validated
```

---

# 147. Interaction Baseline Comparison

对 12-0 baseline至少比较：

```text
steps to start analysis

visible internal identifiers

clarification steps

plan information layers

Workspace opening path

primary action ambiguity
```

---

# 148. No Artificial Improvement Target

不要求：

```text
50% fewer clicks
```

除非 canonical acceptance有数值。

目标：

```text
remove avoidable friction
```

---

# 149. Evidence Directory

建立：

```text
docs/phase12/evidence/
phase12_2_global_navigation_planner/
```

至少：

```text
baseline.txt

entry_gate.md

phase12_1_handoff_snapshot.json

global_navigation_map.json

route_navigation_mapping.json

global_shell_matrix.json

planner_surface_matrix.json

data_context_matrix.json

prompt_composer_matrix.json

intent_presentation_matrix.json

clarification_matrix.json

eligibility_presentation_matrix.json

human_plan_matrix.json

developer_disclosure_matrix.json

execution_state_mapping.json

partial_failure_matrix.json

error_recovery_matrix.json

planner_workspace_transition.json

provider_settings_matrix.json

status_terminology_matrix.json

mobile_navigation_matrix.json

mobile_planner_matrix.json

accessibility_matrix.json

interaction_baseline_comparison.json

internal_identifier_visibility_audit.json

phase12_2_problem_closure.json

deferred_problem_matrix.json

phase12_3_handoff.json

before_after_surface_matrix.json

browser_matrix.json

network_audit.json

no_scientific_change_audit.md

no_planner_contract_change_audit.md

no_backend_change_audit.md

security.md

secret_scan.txt

manifest.json
```

---

# 150. Before / After Evidence

12-0/12-1 retained evidence是 BEFORE foundation。

12-2保存 AFTER。

至少：

```text
Home/global shell

Data context

Planner empty

Planner ready

Clarification

Unsupported

Eligibility

Human Plan

Running

Partial

Failed

Complete

Workspace transition

mobile nav

mobile Planner
```

---

# 151. Desktop Viewports

至少：

```text
1440x900

1280x720
```

---

# 152. Mobile

必须：

```text
390x844
```

---

# 153. Browser Matrix

必须：

```text
Chromium

Firefox

WebKit

Chromium 390x844
```

---

# 154. Browser Requirements

必须：

```text
console errors = 0

page errors = 0

unapproved external requests = 0

unexpected horizontal overflow = 0

scientific payload mutation = 0
```

---

# 155. Browser Scientific Authority

继续：

```text
BROWSER_PASS
!=
SCIENTIFIC_PASS
```

---

# 156. Screenshot Authority

继续：

```text
SCREENSHOT_NUMERIC_SCIENTIFIC_AUTHORITY = NONE
```

---

# 157. Network Audit

browser evidence必须明确记录：

```text
allowed application API requests

no external design assets

no browser-to-DeepSeek call

no external artifact execution
```

---

# 158. Frontend Testing

必须扩充 tests覆盖：

```text
global navigation

active state

keyboard navigation

prompt composer

clarification

eligibility

human plan

developer detail

execution

partial

errors

Workspace transition

mobile
```

---

# 159. Backend Regression

即使 backend不应改变：

运行：

```text
uv run python -m pytest -q
```

dynamic floor：

```text
>= Phase 12-1 final canonical floor
```

当前 known：

```text
1293 passed
```

但必须动态读取。

---

# 160. Frontend Regression

当前 Phase 12-1 known：

```text
450 passed
```

12-2 final不得低于 dynamic floor。

---

# 161. Typecheck

必须：

```text
PASS
```

---

# 162. Build

必须：

```text
PASS
```

---

# 163. Lock

必须：

```text
uv lock --check = PASS

lockfile changes = 0
```

---

# 164. Diff

必须：

```text
git diff --check = PASS
```

---

# 165. Service-Backed Regression

Implementation exact-SHA CI必须继续：

```text
PostgreSQL

Redis

MinIO
```

required suite PASS。

---

# 166. Linux / Windows Replay

当前 CI已有 Linux/Windows scientific replay。

必须继续保持：

```text
PASS
```

因为 UX phase不能破坏 scientific reproducibility infrastructure。

---

# 167. npm Audit

如果 configured mirror仍：

```text
404_NOT_IMPLEMENTED
```

必须：

```text
npm audit = UNAVAILABLE
```

不得：

```text
PASS
clean
```

---

# 168. Production Behavior Diff Audit

必须证明：

```text
same Intent semantics

same Eligibility semantics

same selected Tool IDs for same fixture

same bound parameters

same AnalysisPlan semantic hash
where presentation-only path should preserve it

same Job/Runtime behavior

same Artifact scientific values

same interpretation claims/evidence

same Workspace identity
```

---

# 169. Semantic Comparison

对 canonical fixture：

比较 before/after：

```text
Intent semantic identity

Eligibility semantic identity

Plan semantic identity

Artifact semantic payload

Workspace source identity
```

UI DOM可以变化。

科学/执行 semantic authority不能变化。

---

# 170. Allowed Planner API Request Differences

由于 UI重组：

可能出现：

```text
different timing
different metadata read ordering
```

但不得：

```text
duplicate create
duplicate enqueue
duplicate ToolCall
extra provider execution
```

---

# 171. No Hidden Writes

导航/浏览历史：

不得触发：

```text
Job creation

Plan creation

Workspace mutation

Report finalize

Recipe creation
```

除非对应明确 user action。

---

# 172. Global Navigation History

Back/Forward必须：

```text
restore correct product destination

not execute analysis

not create Workspace

not mutate Planner scientific state
```

---

# 173. Planner Draft State

如果 current product已有 prompt draft state：

可保留 current authority。

不得擅自新增：

```text
localStorage canonical Planner state
```

---

# 174. localStorage Authority

继续：

```text
LOCAL_STORAGE_SCIENTIFIC_AUTHORITY = NONE
```

---

# 175. Workspace localStorage

继续：

```text
LOCAL_STORAGE_CANONICAL_WORKSPACE_AUTHORITY = NONE
```

---

# 176. Security of User Prompt

Prompt显示/历史：

必须：

```text
React/plain text

no HTML execution
```

---

# 177. Prompt Injection

自然语言 prompt即使包含：

```text
<script>
javascript:
ignore previous instructions
```

UI层必须保持 inert。

---

# 178. Provider Audit Detail

如果显示 provider metadata：

不得显示：

```text
raw Authorization

secret

private path

full environment data
```

---

# 179. Global Nav and Project Scope

如果 product有 Project context：

Global nav必须保留 project scope。

不得从一个 project 导航后：

读取另一个 project的数据。

---

# 180. Cross-Project Isolation

必须回归：

```text
NO_CROSS_PROJECT_NAVIGATION_DATA_LEAK = PASS
```

---

# 181. Cross-Workspace Isolation

必须：

```text
NO_CROSS_WORKSPACE_RESULT_LEAK = PASS
```

---

# 182. Phase 12-3 Handoff

必须生成：

```text
Phase12_3WorkspaceViewerUXHandoff
```

至少：

```text
DS2 version/hash

global shell state

global IA implementation

Planner→Workspace transition

Workspace entry behavior

remaining 12-3 UX problem IDs

Workspace IA target

viewer surface inventory

current result-first constraints

selection authority

mobile Workspace constraints

accessibility constraints

Phase 11 scientific authority refs

browser evidence refs
```

---

# 183. Do Not Implement 12-3

handoff完成后：

禁止开始：

```text
Workspace IA restructure

Gallery redesign

viewer chrome redesign

chart toolbar redesign

3D viewer redesign
```

---

# 184. Canonical Documentation

至少更新/新增：

```text
docs/phase12/
phase12_2_global_navigation_planner_agent_experience.md

phase12_2_global_navigation_map.md

phase12_2_planner_information_hierarchy.md

phase12_2_data_context_and_prompt_composer.md

phase12_2_intent_clarification_eligibility_ux.md

phase12_2_human_readable_plan.md

phase12_2_execution_progress_and_recovery.md

phase12_2_planner_workspace_transition.md

phase12_2_accessibility_responsive.md

phase12_2_problem_closure.md

phase12_3_workspace_viewer_handoff.md

phase12_2_completion.md
```

使用 existing naming convention优先。

不要创建 duplicate authority。

---

# 185. Persistent State

同步：

```text
persistent/PROJECT_BRIEF.md

persistent/DESIGN_PROGRESS.md

persistent/TASK_BOARD.md

persistent/CHANGELOG.md

persistent/OPEN_QUESTIONS.md

persistent/ARCHITECTURE_DECISIONS.md

persistent/TOOL_REGISTRY_NOTES.md
```

不得修改 Tool science facts。

---

# 186. ROADMAP

成功后：

```text
Phase 11:
COMPLETE /
REFERENCE_VALIDATED_WITH_EXPLICIT_LIMITS

Phase 12-0:
COMPLETE

Phase 12-1:
COMPLETE /
DESIGN_SYSTEM_2_0_IMPLEMENTED

Phase 12-2:
COMPLETE /
GLOBAL_NAVIGATION_AND_PLANNER_EXPERIENCE_IMPLEMENTED

Phase 12-3:
REVIEWER_GATE /
AWAITING REVIEWER PROMPT

Phase 13:
ROADMAP_APPROVED /
NOT_QUEUED
```

---

# 187. Queue Admission

Entry PASS 后：

只创建：

```text
one Phase 12-2 TASK block
```

必须：

```text
TASK_BLOCK_COUNT = 1

ACTIVE_TASK = Phase 12-2

PHASE_12_3_EXECUTABLE_TASK_CREATED = NO

PHASE_13_EXECUTABLE_TASK_CREATED = NO
```

---

# 188. First Required Output

开始执行后第一组必须输出：

```text
Phase 12-2 Entry Gate
+ Phase 12-1 Design-System Handoff
+ Global Navigation / Planner UX Admission
```

至少确认：

1. current HEAD；
2. origin/master；
3. branch；
4. worktree clean；
5. Phase 12-1 implementation SHA；
6. Phase 12-1 CI；
7. completion SHA；
8. archive SHA；
9. TASK_BLOCK_COUNT=0；
10. Phase 12-3 task absent；
11. Phase 13 task absent；
12. DS2 version；
13. DS2 semantic hash；
14. DS2 token registry resolves；
15. shared component registry resolves；
16. 12-2 navigation/planner handoff resolves；
17. Global IA target resolves；
18. current route mapping；
19. current Planner surfaces；
20. Data/Profile authority；
21. Intent contract/version；
22. Clarification contract；
23. Eligibility contract/version；
24. AnalysisPlan 0.1/0.2；
25. execution status authority；
26. partial/dependency semantics；
27. Workspace projection/open behavior；
28. exact 12-2 owned UX problem IDs；
29. owned count；
30. exact P12X2-A01..A08 descriptions；
31. current provider policy；
32. no new backend API required；
33. no migration required；
34. no dependency required；
35. no scientific change required。

成功才输出：

```text
PHASE_12_2_ENTRY_GATE = PASS

PHASE_12_1_DEPENDENCY = VERIFIED

DESIGN_SYSTEM_2_0 =
VERIFIED_FOUNDATION

PHASE_11_SCIENTIFIC_AUTHORITY =
VERIFIED_READ_ONLY

PHASE_12_2_QUEUE_ADMISSION =
AUTHORIZED

PHASE_12_2_GLOBAL_NAVIGATION_AUTHORITY =
AUTHORIZED_WITHIN_SEALED_IA

PHASE_12_2_PLANNER_PRESENTATION_AUTHORITY =
AUTHORIZED

PHASE_12_2_PLANNER_SEMANTIC_CHANGE_AUTHORITY =
NONE

PHASE_12_2_SCIENTIFIC_CHANGE_AUTHORITY =
NONE

PHASE_12_2_BACKEND_BEHAVIOR_CHANGE_AUTHORITY =
NONE

PHASE_12_2_READINESS =
READY_FOR_GLOBAL_NAVIGATION_AND_PLANNER_UX_IMPLEMENTATION
```

---

# 189. Required Execution Sequence

严格：

```text
verify Phase 12-1 lifecycle

→ verify DS2 semantic baseline

→ verify Phase 11 scientific authority

→ load 12-0 UX decisions

→ load 12-2 handoff

→ load exact 12-2 owned problems

→ load exact P12X2 acceptance IDs

→ verify current routes/API/frontend authority

→ admit exactly one 12-2 task

→ snapshot current global navigation

→ snapshot current Planner workflow

→ snapshot canonical before evidence

→ implement sealed global navigation IA

→ implement product shell integration

→ improve Data context

→ improve Prompt Composer

→ implement human-readable Intent presentation

→ improve bounded Clarification UX

→ improve Eligibility/capability UX

→ implement human-readable Plan presentation

→ subordinate developer Plan details

→ implement execution-stage presentation mapping

→ improve partial/failure/dependency disclosure

→ improve Planner error/recovery states

→ improve provider/settings discoverability
without changing provider policy

→ implement explicit Planner→Workspace transition UX

→ implement 12-2 mobile navigation/Planner behavior

→ validate accessibility

→ close exact 12-2-owned UX problems

→ keep future-phase problems typed/open

→ generate 12-3 handoff

→ capture after evidence

→ compare interaction baseline

→ run no-scientific-change audit

→ run no-planner-semantic-change audit

→ run no-backend-change audit

→ run frontend/full backend regression

→ run browser matrix

→ run service-backed regression

→ run Linux/Windows retained replay

→ run evidence/security/secret checks

→ create implementation commit

→ push

→ WAIT FOR IMPLEMENTATION EXACT-SHA CI

→ if PASS:
   append Phase 12-2 completion result

→ commit/push completion record directly

→ remove only Phase 12-2 TASK block

→ commit/push queue archive directly

→ verify queue empty

→ stop
```

---

# 190. Implementation Commit Contents

允许：

```text
frontend global navigation

product shell

Planner UX components

Planner styles using DS2

human-readable projection helpers

presentation-only state mapping

frontend tests

browser/evidence runner

documentation

persistent state

TASKS admission
```

---

# 191. Implementation Commit Must Not Include

禁止：

```text
new scientific Tool

scientific algorithm

new Planner semantic contract

new eligibility rule

new parameter binding

new dependency rule

new Runtime state

database migration

new public backend API family

new LLM provider

Phase 12-3 implementation

Phase 12-2 completion result
```

---

# 192. Implementation Exact-SHA CI

push后必须等待：

```text
IMPLEMENTATION EXACT-SHA CI
```

所有 required jobs必须：

```text
success
```

---

# 193. Minimum CI Gates

至少：

```text
Backend Unit

Frontend Tests

Typecheck

Build

Phase 12-2 browser evidence

Chromium

Firefox

WebKit

390x844

PostgreSQL/Redis/MinIO

Linux scientific replay

Windows scientific replay

Phase 11 authority integrity

Phase 12 evidence integrity

security / secret
```

---

# 194. Failed Candidate Policy

如果失败：

必须保存：

```text
failed SHA

CI run

failed job

root cause
```

然后：

```text
fix-forward
```

禁止：

```text
force push

history rewrite

test deletion

acceptance weakening

browser removal

mobile removal

problem owner reassignment

scientific contract change
```

---

# 195. Completion Record

只有 implementation exact-SHA CI PASS 后：

向：

```text
results.md
```

append：

```text
Phase 12-2 Global Navigation
+ Planner / Agent Experience Result
```

然后：

```text
commit
push
```

不主动等待 completion CI。

---

# 196. Queue Archive

completion push 后：

删除且只删除：

```text
Phase 12-2 TASK block
```

不得创建：

```text
Phase 12-3 executable task
```

然后：

```text
commit
push
```

不主动等待 archive CI。

---

# 197. Mandatory Result Markers

必须：

```text
PHASE12_2_PRODUCTION_UI_CHANGES =
YES_UX_PRESENTATION_AND_NAVIGATION

PHASE12_2_PLANNER_BACKEND_BEHAVIOR_CHANGES = 0

PHASE12_2_SCIENTIFIC_BEHAVIOR_CHANGES = 0

PHASE12_2_ANALYSIS_INTENT_CONTRACT_CHANGES = 0

PHASE12_2_ELIGIBILITY_CONTRACT_CHANGES = 0

PHASE12_2_ANALYSISPLAN_CONTRACT_CHANGES = 0

PHASE12_2_RUNTIME_SEMANTIC_CHANGES = 0

PHASE12_2_ARTIFACT_SEMANTIC_CHANGES = 0

PHASE12_2_WORKSPACE_AUTHORITY_CHANGES = 0

PHASE12_2_NEW_SCIENTIFIC_TOOLS = 0

PHASE12_2_NEW_SCIENTIFIC_ALGORITHMS = 0

PHASE12_2_NEW_ARTIFACT_FAMILIES = 0

PHASE12_2_NEW_DATAPROFILE_VERSION = 0

PHASE12_2_NEW_DATABASE_MIGRATIONS = 0

PHASE12_2_NEW_PUBLIC_API_FAMILIES = 0

PHASE12_2_NEW_DEPENDENCIES = 0

PHASE12_2_LOCKFILE_CHANGES = 0

PHASE12_2_NEW_LLM_CALL_SITES = 0

PHASE12_2_REAL_LLM_CALLS = 0

PHASE12_2_FRONTEND_SCIENTIFIC_RECOMPUTATION = 0
```

---

# 198. Planner Honesty Markers

必须：

```text
HUMAN_PLAN_FIRST = YES

DEVELOPER_DETAILS_AVAILABLE = YES

TOOL_ID_DEFAULT_PRIMARY_UI = NO

ARTIFACT_ID_DEFAULT_PRIMARY_UI = NO

FRONTEND_INTENT_RECOMPUTATION = 0

FRONTEND_ELIGIBILITY_RECOMPUTATION = 0

FRONTEND_PLAN_RECOMPUTATION = 0

FAKE_PROGRESS_PERCENTAGES = 0

NON_READY_EXECUTION_ENABLED = 0

RECOMMENDATION_AUTO_EXECUTION = 0

PLANNER_AUTO_TOOL_SUBSTITUTION = 0
```

---

# 199. Navigation Markers

必须：

```text
GLOBAL_IA =
Home|Data|Analyses|Workspaces|Reports|Settings

GLOBAL_NAVIGATION_CURRENT_STATE_ACCESSIBLE = PASS

GLOBAL_NAVIGATION_KEYBOARD = PASS

GLOBAL_NAVIGATION_MOBILE = PASS

GLOBAL_NAVIGATION_COLOR_ONLY_CURRENT_STATE = 0

BROKEN_NAVIGATION_DESTINATIONS = 0
```

exact route mapping另行报告。

---

# 200. Scientific Honesty Markers

必须：

```text
SUPPORTED_EQUALS_VALIDATED = NO

MAPPING_ONLY_VISUAL_UPGRADE = 0

NOT_APPLICABLE_VISUAL_UPGRADE = 0

V4_VISUAL_FABRICATION = 0

BROWSER_PASS_EQUALS_SCIENTIFIC_PASS = NO

SERVICE_PASS_EQUALS_SCIENTIFIC_PASS = NO

SCREENSHOT_NUMERIC_SCIENTIFIC_AUTHORITY = NONE

FRONTEND_SCIENTIFIC_AUTHORITY = NONE
```

---

# 201. Baseline Markers

必须：

```text
REGISTRY_BEFORE_12_2 = 62
REGISTRY_AFTER_12_2 = 62

DATAPROFILE_BEFORE_12_2 = 2.4
DATAPROFILE_AFTER_12_2 = 2.4

MIGRATION_BEFORE_12_2 =
0007_phase10m1_workspace_domain

MIGRATION_AFTER_12_2 =
0007_phase10m1_workspace_domain
```

---

# 202. Design System Markers

必须：

```text
DESIGN_SYSTEM_VERSION_BEFORE_12_2 = 2.0

DESIGN_SYSTEM_VERSION_AFTER_12_2 = 2.0

DESIGN_SYSTEM_SEMANTIC_HASH_ENTRY =
<actual>

UNAPPROVED_PARALLEL_DESIGN_SYSTEM = 0
```

如果有允许的 DS2 bug fix：

报告 new hash + exact reason。

---

# 203. UX Problem Markers

必须：

```text
PHASE12_2_OWNED_PROBLEMS =
<exact IDs>

PHASE12_2_OWNED_PROBLEM_COUNT =
<actual>

PHASE12_2_OWNED_PROBLEMS_CLOSED =
<same count>

PHASE12_2_OWNED_PROBLEMS_OPEN = 0

NEW_P0_INTRODUCED_BY_12_2 = 0

NEW_P1_INTRODUCED_BY_12_2 = 0
```

---

# 204. Acceptance Marker

必须：

```text
P12X2_ACCEPTANCE = 8/8
```

使用 repository exact descriptions。

---

# 205. Accessibility Markers

至少：

```text
GLOBAL_NAV_KEYBOARD = PASS

GLOBAL_NAV_FOCUS_VISIBLE = PASS

PLANNER_KEYBOARD_FLOW = PASS

CLARIFICATION_KEYBOARD_FLOW = PASS

PLAN_DISCLOSURE_KEYBOARD = PASS

ASYNC_STATUS_NON_COLOR = PASS

MOBILE_TOUCH_TARGETS = PASS

REDUCED_MOTION = PASS
```

以及：

```text
FULL_PRODUCT_ACCESSIBILITY_COMPLETE = NO
```

---

# 206. Required results.md Structure

至少：

# Phase 12-2 Global Navigation + Planner / Agent Experience Result

1. Conclusion
2. Phase 12-1 Baseline
3. Entry Gate
4. Repository State
5. DS2 Handoff Integrity
6. Phase 11 Scientific Authority
7. Phase 12-0 Experience Decisions
8. Phase 12-2 UX Problem Ownership
9. Production Behavior Changes
10. Global IA Implementation
11. Route / Navigation Mapping
12. Product Shell
13. Home Experience
14. Data Navigation / Context
15. Analyses Navigation
16. Workspaces Navigation
17. Reports Navigation
18. Settings Navigation
19. Navigation Accessibility
20. Mobile Navigation
21. Planner Information Hierarchy
22. Data Context
23. Profile Readiness Presentation
24. Prompt Composer
25. Suggested Analysis Authority
26. AnalysisIntent Presentation
27. Clarification
28. Unsupported Intent
29. Eligibility
30. Capability Mismatch
31. Human-Readable Plan
32. AnalysisPlan 0.1 Presentation
33. AnalysisPlan 0.2 Dependencies
34. Developer Plan Details
35. Run Authority
36. Execution State Mapping
37. Planning/Validation Progress
38. Runtime Progress
39. Partial Execution
40. Failed/Blocked Dependencies
41. Error / Recovery
42. Loading / Empty States
43. Provider / Settings
44. DeepSeek Policy
45. Recommendation Boundary
46. Planner → Workspace Transition
47. Workspace Identity / Deep Link
48. Internal-Identifier Visibility
49. Terminology / i18n
50. Desktop 1440x900
51. Desktop 1280x720
52. Mobile 390x844
53. 200% Zoom
54. Reduced Motion
55. Accessibility
56. Browser Matrix
57. Interaction Baseline Comparison
58. Scientific Payload Non-Change
59. Planner Contract Non-Change
60. Backend/API/DB Freeze
61. Registry/DataProfile Freeze
62. Security
63. LLM / Provider
64. Phase 12-2 Problem Closure
65. Deferred UX Problems
66. Phase 12-3 Handoff
67. Evidence Inventory
68. Evidence Manifest
69. Backend Regression
70. Frontend Regression
71. Typecheck
72. Build
73. Service Regression
74. Linux/Windows Replay
75. npm Audit
76. Files Changed
77. Acceptance Registry
78. Implementation Commit
79. Implementation CI
80. Failed Candidates
81. Completion Record
82. Queue Archive
83. Queue State
84. Phase 12-3 Reviewer Gate
85. Final Repository State

---

# 207. PASS Gate

只有全部满足：

```text
Phase 12-1 PASS

Phase 12-1 queue archived

Phase 12-1 implementation exact-SHA CI PASS

HEAD == origin/master at entry

worktree clean

TASK_BLOCK_COUNT = 0


DS2 2.0 authority resolves

DS2 semantic hash resolves

Phase 12-2 handoff resolves


Phase 11 scientific authority resolves

Registry = 62

DataProfile = 2.4

migration = 0007


Global IA implemented

all six navigation destinations mapped

broken navigation destination = 0

existing canonical deep links preserved


Data context improved

Prompt Composer improved

Intent presentation human-readable

Clarification human-readable

Eligibility human-readable

Human Plan first

Developer Plan details retained

Execution state presentation complete

Partial/failure distinction complete

error/recovery complete

Planner→Workspace transition complete


no Planner semantic change

no eligibility semantic change

no Plan semantic change

no Runtime semantic change

no scientific value change

no Workspace authority change


12-2 owned UX problems closed

new P0 = 0

new P1 introduced = 0


future-phase problems remain correctly owned


no scientific Tool

no scientific algorithm

no Artifact family

no DataProfile version

no AnalysisPlan version

no database migration

no new public backend API family

no dependency

no lock change

no new LLM call site

real LLM calls = 0

frontend scientific recomputation = 0


global nav keyboard PASS

Planner keyboard PASS

clarification keyboard PASS

non-color state PASS

touch target PASS

reduced motion PASS


Chromium PASS

Firefox PASS

WebKit PASS

390x844 PASS


backend >= dynamic Phase 12-1 floor

frontend >= dynamic Phase 12-1 floor

typecheck PASS

build PASS

lock PASS

diff PASS

PostgreSQL/Redis/MinIO PASS

Linux replay PASS

Windows replay PASS

evidence integrity PASS

security PASS

secret scan PASS


P12X2 = 8/8


implementation exact-SHA CI PASS

completion record committed/pushed

queue archive committed/pushed


TASK_BLOCK_COUNT = 0

Phase 12-3 task absent

Phase 13 task absent

HEAD == origin/master

worktree clean
```

才允许：

```text
Phase 12-2 = PASS
```

---

# 208. BLOCKED — Planner Semantics Changed

如果 UX implementation需要：

```text
change intent contract

change eligibility

change Tool ranking

change binding

change AnalysisPlan semantics

change dependency graph

change Runtime
```

必须：

```text
BLOCKED /
PLANNER_SEMANTIC_CHANGE_REVIEW_REQUIRED
```

---

# 209. BLOCKED — New Backend Capability Needed

如果 Global IA / Planner target需要：

```text
new backend domain

new persistence

new public API family
```

必须：

```text
BLOCKED /
PRODUCT_CAPABILITY_REVIEW_REQUIRED
```

不能自己扩 scope。

---

# 210. BLOCKED — Fake Feature Navigation

如果：

```text
navigation item implies a working capability
```

但当前产品没有 authoritative path：

必须修复或 BLOCKED。

---

# 211. BLOCKED — Scientific Overclaim

如果 UX copy：

```text
upgrades unsupported
or
reference-limited science
```

必须：

```text
BLOCKED /
SCIENTIFIC_UX_MISREPRESENTATION
```

---

# 212. BLOCKED — Internal Concepts Still Dominate

如果 final default Planner仍然要求用户首先理解：

```text
Tool ID

Artifact ID

Plan hash

binding

contract
```

才能完成基本分析：

12-2 的核心目标没有完成。

不能 PASS。

---

# 213. BLOCKED — Clarification Is Raw Schema

如果 clarification默认显示：

```text
raw JSON
raw schema
internal IDs
```

作为主要选择体验：

不能 PASS。

---

# 214. BLOCKED — Human Plan Missing

如果 AnalysisPlan仍然只能通过：

```text
ToolCall-oriented technical UI
```

理解：

不能 PASS。

---

# 215. BLOCKED — Execution State Fabrication

如果新增：

```text
fake progress percent

fake backend status

fake completed state
```

不能 PASS。

---

# 216. BLOCKED — Workspace Authority Leak

如果 Planner→Workspace UX：

```text
creates duplicate Workspace

uses latest Workspace

uses display label

creates frontend-only Workspace identity
```

不能 PASS。

---

# 217. BLOCKED — Owned Problems Remain

如果：

```text
PHASE12_2_OWNED_PROBLEMS_OPEN > 0
```

不能 PASS。

---

# 218. Non-Blockers

以下可继续存在：

```text
12-3 Workspace/viewer UX debt

12-4 Evidence/Inspector UX debt

12-5 Report/Recipe UX debt

12-6 full mobile/accessibility debt

12-7 final consistency debt

V4=0

reference-limited science

unsupported formats

Future Scope
```

只要没有被 UI 隐藏或误称已解决。

---

# 219. Final Successful State

成功：

```text
Phase 12-2:
PASS /
GLOBAL_NAVIGATION_IMPLEMENTED /
PLANNER_AGENT_EXPERIENCE_REDESIGNED /
QUEUE_ARCHIVED

Phase 12:
IN_PROGRESS /
GLOBAL_NAVIGATION_AND_ANALYSIS_ENTRY_COMPLETE

Phase 12-3:
REVIEWER_GATE /
AWAITING REVIEWER PROMPT

Phase 13:
ROADMAP_APPROVED /
NOT_QUEUED /
NOT_EXECUTABLE

TASK_BLOCK_COUNT = 0

PHASE_12_3_EXECUTABLE_TASK_CREATED = NO

PHASE_13_EXECUTABLE_TASK_CREATED = NO
```

---

# 220. What Phase 12-2 Completion Means

可以说：

```text
The product now exposes the sealed global information
architecture and a redesigned analysis-entry experience
that presents data context, intent, clarification,
capability eligibility, analysis plans, execution state
and Workspace transition in user-oriented language while
preserving the existing Planner, Runtime and scientific
authority contracts.
```

---

# 221. What Phase 12-2 Does NOT Mean

不能说：

```text
Workspace redesign is complete.

Scientific viewers are redesigned.

Evidence/Inspector redesign is complete.

Report/Recipe redesign is complete.

Mobile/accessibility is complete.

Phase 12 is complete.

The product is release-ready.
```

---

# 222. Phase 12-3 State

最终必须：

```text
Phase 12-3:
REVIEWER_GATE /
AWAITING REVIEWER PROMPT

PHASE_12_3_EXECUTABLE_TASK_CREATED = NO
```

---

# 223. Stop Rule

完成后立即停止。

不得：

```text
implement Workspace target IA

redesign Gallery

redesign scientific viewers

redesign Inspector

redesign Report Builder

perform Phase 12-6 closure

start Phase 12-7

start Phase 13
```

返回 reviewer：

```text
Phase 12-2 final result

implementation SHA

implementation CI

completion SHA

archive SHA

Global IA route mapping

exact 12-2-owned UX problem closure

exact P12X2 8/8 result

before/after interaction evidence

Planner semantic non-change proof

scientific authority non-change proof

browser/mobile/accessibility evidence

remaining UX problem ownership

Phase 12-3 handoff state
```

然后等待 reviewer。

---END---
---TASK---
 状态：待处理

# Phase 12-3 Reviewer Prompt

# Scientific Workspace + Scientific Viewer Experience

你现在执行：

# Phase 12-3：Scientific Workspace + Scientific Viewer Experience

中文：

# 科学工作区 + 科学可视化 Viewer 核心体验重构

本阶段属于：

```text
Phase 12:
Comprehensive UI / UX
Product Experience Redesign
```

Phase 12 序列：

```text
12-0
Current UX Reality Audit
+ Product Experience Seal
= COMPLETE

12-1
Design System 2.0
+ Visual Language
= COMPLETE

12-2
Global Navigation
+ Planner / Agent Experience
= MUST BE VERIFIED AT ENTRY

12-3
Scientific Workspace
+ Scientific Viewer Experience
= CURRENT AUTHORIZED PHASE

12-4
Findings / Evidence /
Inspector / Provenance Experience

12-5
Report / Recipe Experience

12-6
Responsive / Mobile /
Accessibility Closure

12-7
Cross-Product UX Validation
+ Design Evidence Closure
```

---

# 0. Mission

Phase 12-3 的目标：

```text
已有 ScientificWorkspace authority

+
已有 Artifact / Selection / Result contracts

+
已有 Design System 2.0

+
Phase 12-2 global shell / Planner transition

→

统一的 Scientific Workspace 信息架构

→

Result-first scientific experience

→

统一 scientific viewer chrome

→

更清晰的 selection / source / warning / limitation

→

专业 chart / 3D / table viewing experience

→

metadata-first + lazy heavy viewer behavior

→

desktop/mobile scientific exploration foundation

→

preserve exact scientific identity

→

preserve Artifact provenance authority

→

preserve zero frontend scientific recomputation

→

Phase 12-4 reviewer handoff
```

本阶段不是：

```text
new scientific calculation

new Tool

new Artifact family

new Workspace authority

new evidence science

new report semantics

new mobile architecture

new accessibility closure

new backend product capability
```

---

# 1. Fundamental Rule

必须：

```text
WORKSPACE_UX_REDESIGN
!=
WORKSPACE_AUTHORITY_REDESIGN
```

以及：

```text
VIEWER_UX_REDESIGN
!=
SCIENTIFIC_RECOMPUTATION
```

Phase 12-3 可以改变：

```text
Workspace information hierarchy

navigation presentation

result presentation

Artifact Gallery relationship

viewer layout

viewer chrome

toolbars

control placement

legend presentation

selection affordances

loading/error presentation

table alternatives

fullscreen presentation

responsive scientific-viewer presentation

copy / terminology

progressive disclosure
```

不能改变：

```text
scientific algorithms

scientific values

units

Tool identity

Artifact identity

Artifact contract

Artifact lineage

selection scientific identity

Workspace identity

Workspace persistence authority

URL authority

Report authority

Recipe authority

Phase 11 scientific claims
```

---

# 2. Reviewer Authorization

正式条件预授权：

```text
PHASE_12_3_PROMPT_PREAUTHORIZED = YES

AUTHORIZED_PHASE = Phase 12-3

MAX_PHASES_EXECUTED = 1
```

只有 Entry Gate PASS 后才能创建 Phase 12-3 task。

不得创建或执行：

```text
Phase 12-4

Phase 12-5

Phase 12-6

Phase 12-7

Phase 13
```

---

# 3. Mandatory Phase 12-2 Dependency

执行器必须从真实 repository 读取：

```text
results.md

TASKS.md

docs/ROADMAP.md

persistent/

docs/phase12/

docs/phase12/evidence/

git history
```

动态取得：

```text
PHASE_12_2_IMPLEMENTATION_SHA

PHASE_12_2_IMPLEMENTATION_CI_RUN

PHASE_12_2_IMPLEMENTATION_CI_RESULT

PHASE_12_2_COMPLETION_SHA

PHASE_12_2_QUEUE_ARCHIVE_SHA
```

必须满足：

```text
Phase 12-2 = PASS

implementation exact-SHA CI = PASS

completion recorded

queue archived
```

否则：

```text
PHASE_12_3_ENTRY_GATE = BLOCKED

reason =
PHASE_12_2_NOT_COMPLETED_OR_NOT_ARCHIVED
```

立即停止。

---

# 4. Repository Entry State

必须：

```text
branch = master

HEAD == origin/master

worktree = clean

TASK_BLOCK_COUNT = 0

Phase 12-3 task absent

Phase 12-4 task absent

Phase 13 task absent
```

---

# 5. Phase 12-2 Handoff Authority

必须找到唯一 canonical：

```text
Phase12_3WorkspaceViewerUXHandoff
```

或 repository current equivalent。

至少验证：

```text
Design System version/hash

Global shell state

Global IA implementation

Planner → Workspace transition

Workspace entry behavior

remaining Phase 12-3 UX problem IDs

Workspace target IA

Workspace surface inventory

scientific viewer inventory

result-first constraints

Artifact authority constraints

selection authority

mobile Workspace constraints

accessibility constraints

Phase 11 scientific authority refs

browser evidence refs
```

不得重新创造平行 handoff。

---

# 6. Phase 12-0 / 12-1 Authorities

必须继续读取：

```text
Phase 12 Product Experience Principles

Experience Decision Registry

UI Surface Registry

UX Problem Matrix

Scientific Workspace / Viewer UX Audit

Component Coverage Matrix

Phase 12 Implementation Backlog

Acceptance Plan

Execution Lock

Design System 2.0
```

repository canonical wording优先。

---

# 7. Design System Authority

必须确认：

```text
DESIGN_SYSTEM_VERSION = 2.0
```

并读取 current sealed semantic hash。

Phase 12-3 必须消费 DS2。

不得创建：

```text
parallel viewer design system

ViewerDesignSystem2

special workspace token authority
```

---

# 8. Phase 11 Remains Read-Only

必须继续：

```text
PHASE_11_SCIENTIFIC_AUTHORITY =
READ_ONLY
```

至少：

```text
Registry = 62

DataProfile = 2.4

AnalysisIntent = 1.0

EligibilityResolution = 1.0

AnalysisPlan = 0.1 / 0.2

migration =
0007_phase10m1_workspace_domain
```

---

# 9. Scientific Evidence Honesty

必须保持 actual final Phase 11 facts。

当前 expected baseline仍包括：

```text
12 golden benchmark records

8 PASS_INVARIANT

4 NOT_APPLICABLE

scientific failure = 0

Linux invariant replay = PASS

Windows invariant replay = PASS

numeric cross-platform validation =
NOT_APPLICABLE

V4 = 0
```

必须从 repository验证。

---

# 10. Viewer Cannot Upgrade Science

禁止：

```text
pretty chart
→ validated science

successful render
→ reference verification

browser replay
→ scientific verification

3D visualization
→ geometry truth beyond Artifact

MAPPING_ONLY
→ VERIFIED

N/A
→ PASS
```

---

# 11. Workspace Architecture Freeze

继续：

```text
ONE_WORKSPACE_PER_JOB = YES
```

DB authority继续：

```text
scientific_workspaces

workspace_panels

workspace_layout_revisions
```

migration继续：

```text
0007_phase10m1_workspace_domain
```

不得修改。

---

# 12. Workspace Authority Distribution

必须保持：

## Server authority

```text
Workspace identity

title

panel membership

layout revisions

durable state
```

## URL authority

```text
active panel

exact versioned selection
```

## memory authority

```text
transient viewer UI state
```

---

# 13. No localStorage Canonical Authority

必须：

```text
LOCAL_STORAGE_CANONICAL_WORKSPACE_AUTHORITY = NONE

SESSION_STORAGE_CANONICAL_WORKSPACE_AUTHORITY = NONE
```

Phase 12-3不得为了 UX persistence：

偷偷把：

```text
active scientific selection
Workspace layout
Artifact source
```

迁入 localStorage authority。

---

# 14. Canonical Workspace Route

必须保持：

```text
/workspaces/{workspaceId}
```

作为 exact Workspace deep link。

不得创建：

```text
/workspace/latest

/workspace/current
```

之类 fuzzy authority。

---

# 15. Workspace Target IA

Phase 12-0 已 seal target：

```text
Overview

Data

Analysis

Results

Findings

Evidence

Report
```

Advanced：

```text
Provenance

Developer Details
```

Phase 12-3 负责实现 Workspace 级 IA foundation。

---

# 16. Boundary With Phase 12-4

重要：

12-3 可以实施：

```text
Findings
Evidence
Provenance
Developer Details
```

作为 Workspace navigation destinations / structural containers。

但不能完成：

```text
Finding hierarchy redesign

Evidence trust path redesign

Inspector three-layer redesign

Provenance drilldown redesign
```

这些属于：

```text
Phase 12-4
```

---

# 17. Boundary With Phase 12-5

12-3 可以：

```text
place Report destination
integrate Workspace navigation
```

但不能完成：

```text
Report Builder redesign

Recipe redesign

Report source composition UX
```

这些属于 12-5。

---

# 18. Workspace Overview

Overview 默认应回答：

```text
What analysis is this?

What data does it use?

What results exist?

What succeeded / failed?

What should I look at first?

What important warnings/limitations exist?
```

不要默认展示：

```text
Workspace UUID

Artifact checksums

raw plan

ToolCall IDs
```

---

# 19. Result Before Artifact

硬规则：

```text
RESULT_FIRST_UI = YES
```

普通用户应看到：

```text
Structure

Coordination

Experimental XRD

RDF

MSD

Diffusion

Phonon

Brillouin Zone

Volumetric

Band Structure

DOS

ML Evaluation

Composition Space
```

等 scientific result categories。

---

# 20. Artifact Remains Scientific Provenance Authority

Result-first 不意味着：

```text
Artifact disappears
```

必须：

```text
Artifact remains exact persisted authority
```

但默认层级可以把：

```text
Artifact ID
checksum
contract version
```

下沉到：

```text
Scientific Details

Provenance

Developer Details
```

---

# 21. Artifact Gallery Role

审计并重构 current Artifact Gallery：

目标：

```text
Artifact Gallery
→ result/resource discovery surface
```

而不是：

```text
raw Artifact object browser
```

---

# 22. Artifact Gallery Must Retain Exactness

每个 result仍必须可追踪：

```text
Artifact kind

Artifact version

Tool ID/version

source inputs

parameters

units

warnings

lineage

checksum
```

---

# 23. No Frontend Result Reconstruction

禁止：

```text
filename
MIME
latest Artifact
array position
display title
```

成为 scientific result identity。

---

# 24. Exact Version Selection

所有 viewer navigation必须绑定：

```text
exact Artifact version
```

禁止：

```text
latest

nearest

fallback version

best match
```

---

# 25. Selection Authority

必须保持 canonical：

```text
objectId:sampleRef
```

以及其它现有 exact：

```text
site

atom

frame

q-point

band

spin

peak

resource
```

identities。

---

# 26. No Selection By Display Label

禁止：

```text
Material 1
Atom A
Peak 2
Band 5
```

仅靠 display label成为 canonical identity。

---

# 27. Selection Context

Workspace 应让用户清楚：

```text
what is selected

where selection came from

which result/viewers share that selection
```

但 exact binding authority仍来自 canonical selection context。

---

# 28. URL Selection Authority

如果 current contract规定：

```text
URL owns exact versioned selection
```

Phase 12-3 必须保留。

Back/Forward应恢复 exact context。

---

# 29. Back / Forward

必须验证：

```text
active panel restored

exact selection restored

no scientific recomputation

no Workspace duplication
```

---

# 30. Result Surface Pattern

建议统一：

```text
Result header

Scientific summary

Primary viewer

Warnings / limitations

Viewer controls

Selection/context

Table/text alternative

Scientific details

Provenance link
```

具体结构可依 viewer 类型调整。

---

# 31. Unified Scientific Viewer Chrome

Phase 12-3 必须建立：

```text
UNIFIED_SCIENTIFIC_VIEWER_CHROME
```

至少包含可适用的：

```text
title

result type

source/status

warning/limitation indicator

toolbar

selection context

legend

table/data alternative

reset

fullscreen

export where already allowed

details/provenance access
```

---

# 32. Unified Chrome != Identical Controls

不同 scientific viewer 可以有不同专业 controls。

统一的是：

```text
placement
hierarchy
interaction conventions
terminology
accessibility
```

不是强行所有 viewer 有相同按钮。

---

# 33. Viewer Inventory

必须覆盖真实 current specialized viewer inventory。

至少：

```text
Dataset Explorer

Materials ML

Composition Space

Structure 3D

Coordination

Local Environment / Polyhedra

Experimental XRD

Trajectory

RDF

MSD

Diffusion

Phonon Band

Phonon DOS

Brillouin Zone

Volumetric

Electronic Band Structure

Electronic DOS

Combined Band + DOS presentation
```

如果 repository 有更多 current viewers：

全部纳入。

---

# 34. Viewer Matrix

每个 viewer至少记录：

```text
viewerId

resultType

Artifact authority

scientific authority

selection identity

controls

toolbar

legend

warnings

limitations

table alternative

fullscreen

export

loading behavior

error behavior

mobile behavior

keyboard behavior

screen-reader alternative

WebGL/Plotly resource behavior

Phase12_3 status

evidence refs
```

---

# 35. Viewer Completeness

最终：

```text
CURRENT_SCIENTIFIC_VIEWER_UNCLASSIFIED = 0
```

---

# 36. Viewer Toolbar

统一 toolbar hierarchy：

优先：

```text
scientific exploration controls
```

次级：

```text
view controls
```

advanced：

```text
developer/provenance controls
```

---

# 37. Reset Behavior

Viewer reset必须定义清楚：

```text
reset view
```

不能等同：

```text
reset scientific selection
```

除非 current contract明确。

---

# 38. Fullscreen

Fullscreen：

只改变 presentation。

不得：

```text
create new viewer calculation

change selection identity

change Artifact source
```

---

# 39. Export Boundary

如果 viewer当前允许 export：

保留 existing safe export authority。

不得新增：

```text
arbitrary HTML export

executable notebook

script export
```

---

# 40. Screenshot Export

如果已有 screenshot：

可以保留 presentation export。

必须明确：

```text
SCREENSHOT_NUMERIC_SCIENTIFIC_AUTHORITY = NONE
```

---

# 41. Table Alternative

所有适合 numeric/tabular scientific content 的 viewer：

应提供或保留：

```text
accessible table/data representation
```

具体是否适用必须按 viewer contract判定。

---

# 42. Table Does Not Recompute

Table值必须来自：

```text
same persisted scientific payload
```

不得：

```text
derive a second numeric result
```

---

# 43. Plotly Boundary

Plotly负责：

```text
presentation
interaction
```

不能成为：

```text
scientific executor
```

---

# 44. Plotly Viewer Controls

按适用性统一：

```text
zoom

pan

reset

legend

series visibility

tooltip

selection

table view

fullscreen

export
```

---

# 45. Plotly Scientific Data Freeze

禁止 viewer层：

```text
calculate band gap

calculate peak

calculate RDF

fit diffusion

calculate statistics
```

---

# 46. Plotly Series Identity

必须绑定 exact series/channel identities。

例如：

```text
spin

DOS projection

band

species

trajectory component
```

不得仅按 display order。

---

# 47. Scientific Color Identity

如果颜色有 scientific meaning：

必须保留 mapping。

DS2 status colors不得覆盖 scientific series colors。

---

# 48. WebGL / Three.js Boundary

WebGL只能：

```text
render
select
navigate
```

不能计算新的 science。

---

# 49. Structure 3D

至少审计/重构：

```text
camera controls

reset

projection

cell

axes

labels

selection

fullscreen

loading

warning

mobile
```

不得改变：

```text
atom positions

periodic identity

structure geometry
```

---

# 50. Coordination Viewer

必须明确：

```text
algorithm-derived coordination
```

不能视觉/文案暗示：

```text
true bond network
```

---

# 51. CrystalNN / VoronoiNN

如果同 surface展示：

必须明确算法 identity。

不得：

```text
merge results as one truth
```

---

# 52. Local Environment / Polyhedra

Viewer应清楚：

```text
source coordination artifact

selected site

geometry-derived polyhedron

distortion/geometry metrics
```

不得重新计算 N1 neighbor graph。

---

# 53. Experimental XRD

Viewer至少：

```text
theoretical pattern

experimental pattern

matched peaks

unmatched peaks

configured tolerance context

warning/limitation
```

不得写：

```text
phase confirmed
```

---

# 54. XRD Selection

peak selection必须使用 exact peak identity。

不得依赖：

```text
second rendered marker
```

之类 DOM order。

---

# 55. Trajectory

Viewer至少：

```text
frame identity

time/frame context

play/pause where current capability allows

selection

PBC/context warning
```

不得在 browser重新 unwrap。

---

# 56. RDF

必须明确：

```text
pair/species

r units

g(r)

source Artifact
```

不得通过 visual peak暗示 bond truth。

---

# 57. MSD

必须明确：

```text
lag/time

MSD unit

directional/total semantics

selected group
```

不在 frontend unwrap。

---

# 58. Diffusion

必须显示：

```text
estimated over selected fit window
```

如果 scientific artifact包含：

```text
fit diagnostics
fit range
```

可显示。

不得 browser refit。

---

# 59. Phonon

必须清楚：

```text
q-point/path

frequency units

imaginary-frequency semantics

source/imported nature
```

不得自动显示：

```text
stable
```

除非 exact backend claim允许。

---

# 60. Brillouin Zone

Viewer必须使用 persisted reciprocal/path data。

不允许 browser成为 BZ numeric authority。

---

# 61. Volumetric

至少：

```text
field identity

grid/cell context

slice

isosurface

level

units if available
```

控件改变 presentation level/view。

若 level本身是 user-visible visualization parameter：

必须与 scientific interpretation区别。

---

# 62. Band Structure

必须：

```text
energy reference

Fermi context if supplied

spin/channel

k-path identity

band selection

warnings
```

frontend不得重新算 gap。

---

# 63. DOS

必须：

```text
energy grid

spin

total/projected identity

completeness status
```

不得：

```text
rank partial PDOS as definitive dominance
```

若 completeness != COMPLETE。

---

# 64. Combined Band + DOS

必须继续：

```text
presentation/consumer
```

不是第三 scientific Tool。

UI必须保留：

```text
exact compatible source Artifacts
```

---

# 65. Dataset Explorer

重构重点：

```text
summary hierarchy

table density

filters if existing

selection

missingness/duplicates visibility

linked context
```

不得在 frontend重新计算 scientific summaries。

---

# 66. Materials ML

必须明确区分：

```text
regression
classification
uncertainty
```

及 current metric availability。

不存在的 metric不能 UI推算。

---

# 67. Composition Space

必须清楚：

```text
PCA axes

cluster identity

selected sample

linked material context
```

不得 browser重新 PCA/KMeans。

---

# 68. Heavy Viewer Policy

继续冻结：

```text
METADATA_FIRST = YES

HEAVY_VIEWER_LAZY = YES
```

只有 active/needed viewer才加载 heavy payload。

---

# 69. Hidden Heavy Viewers

禁止：

```text
mount all heavy WebGL/Plotly viewers
and hide with CSS
```

---

# 70. Lazy Load

必须：

```text
activate on demand
```

并保留：

```text
loading
cancellation
cleanup
```

---

# 71. Cancellation

切换：

```text
panel

Artifact

selection

Workspace
```

时：

过期的 heavy request必须：

```text
cancel
or
ignore safely by exact request identity
```

---

# 72. Exact Cache Identity

如果有 client cache：

必须使用 exact：

```text
Workspace

Artifact ID/version

viewer/data contract

selection
```

相关 identity。

禁止：

```text
latest

title

filename

MIME
```

作为 cache authority。

---

# 73. Cache Is Not Scientific Authority

cache只能：

```text
accelerate presentation
```

不能改变：

```text
scientific source identity
```

---

# 74. WebGL Cleanup

切换/卸载 viewer时：

必须验证：

```text
animation loop stopped

event listeners removed

WebGL resources disposed

observer cleaned

fetch aborted/ignored

no hidden canvas leak
```

---

# 75. Viewer Resource Evidence

至少记录：

```text
mounted heavy viewer count

canvas count

active request count

cleanup after switch

cleanup after Workspace leave
```

---

# 76. Viewer Loading UX

必须区分：

```text
metadata available

heavy payload loading

viewer initializing

viewer unavailable

viewer failed
```

不要 blank panel。

---

# 77. Viewer Error UX

至少回答：

```text
What could not be displayed?

Is the scientific result still persisted?

Can I view table/details?

Can I retry presentation safely?
```

---

# 78. Viewer Failure != Science Failure

如果 Artifact science有效但 renderer失败：

必须呈现：

```text
PRESENTATION_FAILURE
```

不能显示：

```text
analysis failed
```

---

# 79. Unsupported Renderer

若 Artifact没有 viewer：

必须：

```text
show typed unsupported presentation state

retain metadata/provenance access
```

不能隐藏 Artifact。

---

# 80. Stale State

如果 Workspace panel引用 stale/missing exact version：

必须：

```text
show explicit stale state
```

禁止静默 rebind到 latest。

---

# 81. Missing Artifact

必须：

```text
MISSING
```

而不是：

```text
find nearest result
```

---

# 82. Result Warning Placement

scientific warning/limitation必须靠近：

```text
result/viewer
```

不能只藏在：

```text
Developer Details
```

---

# 83. Limitation Persistence

mandatory scientific limitations：

不得：

```text
dismiss permanently
```

成为不存在。

可以：

```text
collapse
```

但必须有持续 indicator。

---

# 84. Status vs Limitation

必须视觉区分：

```text
Result status

Scientific limitation

Presentation warning

Runtime failure
```

---

# 85. Scientific Result Summary

Result header可以显示：

```text
human-readable summary

scientific status

source

units

warning/limitation
```

必须来自 persisted authority。

---

# 86. No LLM-Generated Viewer Facts

12-3：

```text
NEW_LLM_CALL_SITES = 0

REAL_LLM_CALLS = 0
```

不能调用 LLM 来生成：

```text
viewer title

scientific summary

warning

classification
```

除非它是已有 persisted grounded interpretation。

---

# 87. Inspector Boundary

12-3只负责：

```text
Inspector placement/integration affordance
```

不能完成：

```text
Summary / Scientific Details / Provenance
```

三层 Inspector redesign。

那属于：

```text
Phase 12-4
```

---

# 88. Findings Boundary

Findings可以作为：

```text
Workspace destination
```

存在。

但：

```text
finding hierarchy
claim cards
evidence paths
```

由 12-4负责。

---

# 89. Evidence Boundary

Evidence destination可以结构化嵌入 Workspace。

但 12-3不能重新定义：

```text
ScientificEvidenceBundle

ScientificClaim
```

或 trust path。

---

# 90. Report Boundary

Report destination保持。

12-3不重新设计：

```text
source discovery

builder

outline

finalize

Recipe
```

---

# 91. Workspace Mobile Authority

继续：

```text
one active panel

context/navigation drawer

panel switcher

Inspector bottom sheet
```

---

# 92. No Mobile Desktop Compression

禁止：

```text
desktop multi-column Workspace
scaled down to 390px
```

---

# 93. Phase 12-3 Mobile Scope

本阶段必须使：

```text
Workspace navigation

result selection

scientific viewer

viewer controls

panel switching

basic Inspector access
```

在 390x844 可用。

---

# 94. Full Mobile Closure Still Phase 12-6

必须：

```text
FULL_PRODUCT_MOBILE_CLOSURE = NO
```

12-6仍负责全产品 closure。

---

# 95. Mobile Viewer Toolbar

必须：

```text
avoid horizontal control overflow
```

允许：

```text
overflow menu

bottom toolbar

grouped controls
```

前提不隐藏核心 scientific context。

---

# 96. Touch Targets

所有 12-3 新/reworked touch controls：

```text
>= 44x44 CSS px
```

---

# 97. Mobile Legends

不得让长 legend：

```text
cover entire scientific result
```

必须有 bounded presentation。

---

# 98. Mobile Tables

允许：

```text
horizontal scroll
summary mode
column prioritization
```

但不能：

```text
drop scientific fields silently
```

---

# 99. 200% Zoom

至少验证：

```text
Workspace navigation

Result header

chart viewer

3D viewer

viewer toolbar

warning/limitation
```

essential actions不能丢失。

---

# 100. Keyboard

至少：

```text
Workspace navigation

panel switcher

viewer toolbar

table alternative

selection affordance where appropriate

fullscreen exit

warning disclosure
```

必须 keyboard accessible。

---

# 101. Focus Restoration

切换：

```text
panel

fullscreen

drawer

bottom sheet
```

必须合理恢复 focus。

---

# 102. Screen Reader Alternatives

对于纯视觉内容：

必须有合理：

```text
title

summary

status

warning

tabular/text alternative
```

本阶段建立 viewer-level foundation。

全产品 closure仍是 12-6。

---

# 103. Reduced Motion

3D/chart UI animation：

必须尊重：

```text
prefers-reduced-motion
```

但不要修改 scientific trajectory/time semantics。

---

# 104. Responsive Breakpoints

消费 DS2 canonical breakpoints。

不得创建：

```text
viewer-specific random breakpoint system
```

除非 specialized viewer有明确 documented exception。

---

# 105. DS2 Scientific Viewer Tokens

可以增加必要：

```text
viewer surface semantic tokens

toolbar tokens

selection tokens

legend tokens
```

如果 12-1 handoff已经预留/授权。

---

# 106. DS2 Version Rule

如果仅新增 DS2 2.0 extension token：

依 current DS governance记录 semantic hash变化。

不得擅自：

```text
DESIGN_SYSTEM_VERSION = 2.1
```

---

# 107. No New Frontend Dependency

必须：

```text
NEW_FRONTEND_DEPENDENCIES = 0
```

不得为了 Viewer redesign安装新的：

```text
chart library

3D library

table library

UI framework
```

---

# 108. Existing Renderer Stack

必须复用 current：

```text
Plotly

MatterViz / existing WebGL/3D layer

current component stack
```

实际 repository为准。

---

# 109. No Backend Changes

默认：

```text
PHASE12_3_BACKEND_BEHAVIOR_CHANGES = 0
```

如果 Workspace/viewer UX需要新的 backend capability：

```text
BLOCKED /
BACKEND_CAPABILITY_REVIEW_REQUIRED
```

---

# 110. API Freeze

必须：

```text
NEW_PUBLIC_API_FAMILIES = 0
```

允许消费现有 Workspace/Artifact APIs。

---

# 111. Database Freeze

必须：

```text
NEW_DATABASE_TABLES = 0

NEW_DATABASE_COLUMNS = 0

NEW_DATABASE_MIGRATIONS = 0
```

---

# 112. Workspace Contract Freeze

必须：

```text
ScientificWorkspace contract changes = 0

WorkspacePanel contract changes = 0

WorkspaceSelectionContext contract changes = 0
```

---

# 113. Artifact Contract Freeze

必须：

```text
NEW_ARTIFACT_FAMILIES = 0

SCIENTIFIC_ARTIFACT_CONTRACT_CHANGES = 0
```

---

# 114. Registry Freeze

必须：

```text
REGISTRY_BEFORE_12_3 = 62

REGISTRY_AFTER_12_3 = 62
```

---

# 115. DataProfile Freeze

必须：

```text
DATAPROFILE_BEFORE_12_3 = 2.4

DATAPROFILE_AFTER_12_3 = 2.4
```

---

# 116. AnalysisPlan Freeze

必须：

```text
AnalysisPlan 0.1 / 0.2 unchanged
```

---

# 117. Planner Boundary

12-2 已负责 Planner。

12-3不得回头大改：

```text
Prompt Composer

Intent

Clarification

Eligibility

Human Plan

Execution UX
```

只允许修复：

```text
Planner → Workspace transition integration bug
```

---

# 118. Global Navigation Boundary

12-2 已实现 Global IA。

12-3不得重新设计：

```text
Home

Data

Analyses

Workspaces

Reports

Settings
```

---

# 119. Phase 12-3-Owned UX Problems

必须从 canonical：

```text
phase12_ux_problem_matrix
```

读取：

```text
owner = 12-3
```

的 exact IDs。

Phase 12-1 baseline曾记录 expected count：

```text
2
```

但必须动态读取 Phase 12-2 final actual。

---

# 120. Do Not Guess Problem IDs

不得由 Prompt/agent编造：

```text
UX-XXX
```

必须使用 repository exact IDs。

---

# 121. Owned Problem Closure

所有：

```text
owner = 12-3
```

最终必须：

```text
FIXED_WITH_EVIDENCE
```

禁止：

```text
reassign owner
lower severity
delete row
```

逃避。

---

# 122. Future Problems Remain

属于：

```text
12-4
12-5
12-6
12-7
```

的 problems继续 typed/open。

可以：

```text
FOUNDATION_IMPROVED
```

但 final closure仍由 owner负责。

---

# 123. New Regression Rule

必须：

```text
NEW_P0_INTRODUCED_BY_12_3 = 0

NEW_P1_INTRODUCED_BY_12_3 = 0
```

---

# 124. Acceptance IDs

Phase 12-0已 seal：

```text
P12X3-A01
...
P12X3-A08
```

exact descriptions必须从：

```text
phase12_acceptance_and_test_plan.md
```

读取。

---

# 125. Acceptance IDs Immutable

要求：

```text
EXPECTED = 8

IMPLEMENTED = 8

MISSING = 0

EXTRA = 0

DUPLICATE = 0

CONFLICTING = 0

SHORTHAND = 0
```

---

# 126. Reviewer Interpretation of P12X3 Scope

repository exact wording wins。

至少 equivalent 覆盖：

```text
A.
Workspace IA / result-first structure

B.
Artifact Gallery / result discovery

C.
Canonical selection / exact source identity

D.
Unified chart viewer experience

E.
Unified 3D / scientific viewer experience

F.
Metadata-first lazy loading /
cache / cleanup / presentation failure

G.
Responsive / keyboard /
accessibility viewer foundation

H.
scientific non-recomputation /
browser / regression / evidence /
lifecycle closure
```

---

# 127. Canonical Viewer Cases

至少验证：

```text
Dataset Explorer

Materials ML

Composition Space

Structure

Coordination / Polyhedra

Experimental XRD

Trajectory

RDF

MSD

Diffusion

Phonon / BZ

Volumetric

Band Structure

DOS

Combined Band + DOS
```

---

# 128. Representative Deep Cases

至少选择：

```text
one dense table/result

one Plotly line/curve viewer

one linked-selection viewer

one WebGL/3D viewer

one trajectory viewer

one electronic viewer

one error/stale viewer

one partial-result Workspace
```

进行 detailed evidence。

---

# 129. Evidence Directory

建立：

```text
docs/phase12/evidence/
phase12_3_scientific_workspace_viewers/
```

至少：

```text
baseline.txt

entry_gate.md

phase12_2_handoff_snapshot.json

workspace_information_architecture.json

workspace_navigation_matrix.json

workspace_overview_matrix.json

result_first_matrix.json

artifact_gallery_matrix.json

viewer_inventory.json

viewer_chrome_matrix.json

viewer_control_matrix.json

selection_identity_matrix.json

selection_url_matrix.json

scientific_warning_matrix.json

table_alternative_matrix.json

plotly_viewer_matrix.json

webgl_viewer_matrix.json

structure_viewer.json

coordination_polyhedra_viewer.json

xrd_viewer.json

trajectory_viewer.json

rdf_msd_diffusion_viewers.json

phonon_bz_viewers.json

volumetric_viewer.json

electronic_band_dos_viewers.json

heavy_viewer_lifecycle.json

lazy_loading_matrix.json

cache_identity_matrix.json

cleanup_matrix.json

presentation_failure_matrix.json

stale_missing_matrix.json

mobile_workspace_matrix.json

mobile_viewer_matrix.json

accessibility_matrix.json

zoom_200_matrix.json

browser_matrix.json

before_after_surface_matrix.json

scientific_payload_nonchange.json

workspace_authority_nonchange.json

phase12_3_problem_closure.json

deferred_problem_matrix.json

phase12_4_handoff.json

no_frontend_recomputation_audit.md

no_workspace_authority_change_audit.md

no_artifact_contract_change_audit.md

security.md

secret_scan.txt

manifest.json
```

---

# 130. Canonical Docs

至少新增/更新：

```text
docs/phase12/
phase12_3_scientific_workspace_viewer_experience.md

phase12_3_workspace_information_architecture.md

phase12_3_result_first_experience.md

phase12_3_artifact_gallery_result_discovery.md

phase12_3_scientific_viewer_chrome.md

phase12_3_selection_and_source_identity.md

phase12_3_chart_viewer_experience.md

phase12_3_3d_viewer_experience.md

phase12_3_heavy_viewer_lifecycle.md

phase12_3_responsive_accessibility_foundation.md

phase12_3_problem_closure.md

phase12_4_findings_evidence_inspector_handoff.md

phase12_3_completion.md
```

使用 repository naming convention优先。

---

# 131. Before / After Evidence

必须利用 12-0 current baseline。

至少：

```text
Workspace overview

Workspace navigation

Result list/Gallery

chart result

3D result

viewer warning

viewer loading

viewer error

stale/missing

partial Workspace

mobile Workspace

mobile chart

mobile 3D
```

---

# 132. Viewports

至少：

```text
1440x900

1280x720

390x844
```

---

# 133. Browser Matrix

必须：

```text
Chromium

Firefox

WebKit

Chromium 390x844
```

---

# 134. Browser Requirements

至少：

```text
page errors = 0

console errors = 0

unapproved external requests = 0

unexpected horizontal overflow = 0

selection identity regression = 0

scientific payload mutation = 0

hidden heavy viewer leak = 0
```

---

# 135. Screenshot Authority

继续：

```text
SCREENSHOT_NUMERIC_SCIENTIFIC_AUTHORITY = NONE
```

---

# 136. Browser Scientific Authority

继续：

```text
BROWSER_PASS
!=
SCIENTIFIC_REFERENCE_PASS
```

---

# 137. Network

禁止 viewer：

```text
load external scientific data

load arbitrary Artifact URL

call external rendering API

call DeepSeek
```

---

# 138. Artifact Safety

继续：

```text
Artifact content is inert
```

禁止：

```text
HTML execution

JavaScript execution

iframe

module import

filesystem execution

network execution
```

---

# 139. User-Provided Labels

必须 React/plain text escape。

Material/sample/title中：

```text
<script>
```

不能执行。

---

# 140. Long Labels

必须验证：

```text
long material names

long Artifact IDs

long Tool IDs

long warning text

long unit labels
```

不会破坏 Workspace。

---

# 141. Viewer Performance Boundary

可以记录：

```text
loading duration

interaction responsiveness

canvas count

request count
```

作为 UX diagnostics。

不得声明：

```text
scientific performance benchmark
```

---

# 142. Heavy Viewer Caps

如果 current Workspace已有 caps：

```text
32 panels

128 revisions
```

继续保留。

不得因 UX重构提高 caps。

---

# 143. Panel Limit UX

如果达到 panel cap：

必须：

```text
typed understandable state
```

不能：

```text
silently drop panel
```

---

# 144. Revision Cap UX

同理：

```text
revision cap
```

必须有 typed recovery。

不修改 backend cap。

---

# 145. Historical Workspace

必须继续支持：

```text
lazy idempotent projection
```

旧 Job打开 Workspace：

不应产生 duplicate Workspace。

---

# 146. Reload / Recovery

必须验证：

```text
reload same Workspace

restore active panel

restore exact selection where URL-authoritative

recover persisted layout/state

do not restore transient stale viewer state incorrectly
```

---

# 147. Workspace Switch

若从一个 Workspace到另一个：

必须：

```text
clear transient viewer state

cancel stale requests

dispose heavy resources

load exact new source
```

---

# 148. Cross-Workspace Isolation

必须：

```text
NO_CROSS_WORKSPACE_SELECTION_LEAK = PASS

NO_CROSS_WORKSPACE_ARTIFACT_LEAK = PASS
```

---

# 149. Cross-Project Isolation

必须：

```text
NO_CROSS_PROJECT_WORKSPACE_LEAK = PASS
```

---

# 150. Viewer Selection Linking

如果两个 viewers支持 linked selection：

必须来自：

```text
canonical selection context
```

禁止 frontend fuzzy link。

---

# 151. Unsupported Linked Selection

如果 viewer不支持当前 selection type：

必须：

```text
typed no-linked-selection
```

不能绑定 nearest item。

---

# 152. Selection Clear

需要区分：

```text
clear transient viewer highlight
```

与：

```text
clear canonical scientific selection
```

不要混淆。

---

# 153. Inspector Integration

Phase 12-3 允许保证：

```text
selected result/selection can open Inspector
```

但 Inspector内部内容 hierarchy留给 12-4。

---

# 154. Phase 12-4 Handoff

必须生成：

```text
Phase12_4FindingsEvidenceInspectorHandoff
```

至少：

```text
DS2 version/hash

global shell state

Workspace IA implementation

result-first structure

scientific viewer chrome

selection model presentation

warning/limitation placement

Inspector entry points

Findings destination

Evidence destination

Provenance destination

Developer Details destination

remaining Phase 12-4 UX problems

Phase 11 claim/evidence authority

mobile Inspector constraints

accessibility constraints

browser evidence refs
```

---

# 155. Do Not Implement Phase 12-4

禁止开始：

```text
Finding cards redesign

Evidence drilldown redesign

Inspector 3-layer redesign

Provenance browser redesign
```

---

# 156. Persistent State

更新：

```text
persistent/PROJECT_BRIEF.md

persistent/DESIGN_PROGRESS.md

persistent/TASK_BOARD.md

persistent/CHANGELOG.md

persistent/OPEN_QUESTIONS.md

persistent/ARCHITECTURE_DECISIONS.md

persistent/TOOL_REGISTRY_NOTES.md
```

不能改变 scientific Tool facts。

---

# 157. ROADMAP

成功后：

```text
Phase 11:
COMPLETE /
REFERENCE_VALIDATED_WITH_EXPLICIT_LIMITS

Phase 12-0:
COMPLETE

Phase 12-1:
COMPLETE

Phase 12-2:
COMPLETE

Phase 12-3:
COMPLETE /
SCIENTIFIC_WORKSPACE_AND_VIEWER_EXPERIENCE_IMPLEMENTED

Phase 12-4:
REVIEWER_GATE /
AWAITING REVIEWER PROMPT

Phase 13:
ROADMAP_APPROVED /
NOT_QUEUED
```

---

# 158. Queue Admission

Entry Gate PASS 后：

只创建：

```text
one Phase 12-3 TASK block
```

要求：

```text
TASK_BLOCK_COUNT = 1

ACTIVE_TASK = Phase 12-3

PHASE_12_4_EXECUTABLE_TASK_CREATED = NO

PHASE_13_EXECUTABLE_TASK_CREATED = NO
```

---

# 159. First Required Output

执行开始后第一组必须输出：

```text
Phase 12-3 Entry Gate
+ Phase 12-2 Workspace/Viewer Handoff
+ Scientific Workspace UX Admission
```

至少确认：

1. current HEAD；
2. origin/master；
3. branch；
4. clean worktree；
5. Phase 12-2 implementation SHA；
6. Phase 12-2 implementation CI；
7. completion SHA；
8. archive SHA；
9. TASK_BLOCK_COUNT=0；
10. Phase 12-4 task absent；
11. Phase 13 task absent；
12. DS2 version/hash；
13. Phase 12-3 handoff resolves；
14. Global IA implementation resolves；
15. Planner→Workspace transition resolves；
16. Workspace route `/workspaces/{workspaceId}`；
17. ONE_WORKSPACE_PER_JOB；
18. DB authority；
19. URL authority；
20. memory authority；
21. localStorage authority none；
22. Workspace caps；
23. Workspace target IA；
24. Artifact authority；
25. viewer inventory；
26. selection model；
27. exact 12-3-owned UX problem IDs；
28. exact owned count；
29. P12X3-A01..A08 exact definitions；
30. backend APIs required by current Workspace；
31. no new backend capability required；
32. no migration required；
33. no dependency required；
34. no scientific change required；
35. no LLM required。

成功才：

```text
PHASE_12_3_ENTRY_GATE = PASS

PHASE_12_2_DEPENDENCY = VERIFIED

DESIGN_SYSTEM_2_0 =
VERIFIED_FOUNDATION

PHASE_11_SCIENTIFIC_AUTHORITY =
VERIFIED_READ_ONLY

PHASE_12_3_QUEUE_ADMISSION =
AUTHORIZED

PHASE_12_3_WORKSPACE_INFORMATION_ARCHITECTURE_AUTHORITY =
AUTHORIZED_WITHIN_SEALED_TARGET

PHASE_12_3_VIEWER_PRESENTATION_AUTHORITY =
AUTHORIZED

PHASE_12_3_WORKSPACE_AUTHORITY_CHANGE =
NONE

PHASE_12_3_SCIENTIFIC_CHANGE_AUTHORITY =
NONE

PHASE_12_3_BACKEND_CHANGE_AUTHORITY =
NONE

PHASE_12_3_READINESS =
READY_FOR_SCIENTIFIC_WORKSPACE_AND_VIEWER_UX_IMPLEMENTATION
```

---

# 160. Required Execution Sequence

严格：

```text
verify Phase 12-2 lifecycle

→ verify 12-3 handoff

→ verify DS2 baseline

→ verify Phase 11 read-only authority

→ load exact 12-3 problems

→ load exact P12X3 acceptance IDs

→ verify Workspace/Artifact/selection contracts

→ admit exactly one 12-3 task

→ snapshot current Workspace

→ snapshot current viewer inventory

→ snapshot before browser evidence

→ implement sealed Workspace IA

→ implement Overview

→ implement result-first Results experience

→ restructure Artifact Gallery relationship

→ preserve exact Artifact provenance

→ implement unified viewer chrome

→ standardize chart viewer UX

→ standardize 3D viewer UX

→ standardize selection presentation

→ standardize source/unit/warning presentation

→ implement table/text alternatives where applicable

→ implement presentation failure states

→ implement stale/missing states

→ implement metadata-first loading

→ implement lazy heavy viewer behavior

→ verify exact cache identity

→ verify cancellation

→ verify WebGL/observer/listener cleanup

→ implement mobile Workspace/viewer foundation

→ verify keyboard/focus/zoom/touch/reduced motion

→ close exact 12-3-owned problems

→ leave 12-4/12-5/12-6/12-7 problems typed/open

→ generate 12-4 handoff

→ capture after evidence

→ run scientific payload non-change audit

→ run selection identity audit

→ run Workspace authority non-change audit

→ run Artifact contract non-change audit

→ run frontend scientific recomputation audit

→ run full frontend/backend regression

→ run browser matrix

→ run service-backed regression

→ run retained Linux/Windows replay

→ run evidence/security/secret checks

→ create implementation commit

→ push

→ WAIT FOR IMPLEMENTATION EXACT-SHA CI

→ if PASS:
   append Phase 12-3 completion result

→ commit/push completion directly

→ archive only Phase 12-3 task

→ commit/push archive directly

→ verify final queue empty

→ stop
```

---

# 161. Implementation Commit May Include

```text
Workspace frontend components

Workspace navigation presentation

Results/Gallery frontend

viewer shell/chrome

viewer controls

responsive viewer frontend

lazy/cancellation/cleanup frontend logic

presentation-only selection components

tests

browser evidence tooling

docs

persistent state

TASK admission
```

---

# 162. Implementation Commit Must Not Include

```text
scientific algorithm

new Tool

new Artifact contract

new Artifact family

Workspace domain contract changes

database migration

new backend public API family

selection semantic changes

Plan changes

Report semantics

Recipe semantics

Phase 12-4 implementation

completion record
```

---

# 163. Production Behavior Diff Audit

必须证明：

```text
same Workspace ID

same Job → Workspace cardinality

same Artifact IDs/versions

same selection identities

same scientific values

same units

same warnings

same limitations

same lineage

same source bindings

same Report/Recipe authority

same backend calls for equivalent actions
except harmless presentation-read ordering
```

---

# 164. Scientific Payload Comparison

对代表性 viewers：

比较 before/after：

```text
scientific payload semantic hash

Artifact identity

unit identity

selection identity
```

必须：

```text
SEMANTIC_DIFF = 0
```

---

# 165. Frontend Scientific Recomputation Audit

至少扫描：

```text
band gap

RDF

MSD

diffusion fit

XRD peak detection

coordination

PCA

KMeans

DOS derivation

phonon classification
```

确保：

```text
FRONTEND_SCIENTIFIC_RECOMPUTATION = 0
```

---

# 166. Backend Regression

运行：

```text
uv run python -m pytest -q
```

最终：

```text
>= Phase 12-2 final canonical backend floor
```

必须动态读取。

---

# 167. Frontend Regression

运行：

```text
npm --prefix apps/web test
```

最终：

```text
>= Phase 12-2 final canonical frontend floor
```

---

# 168. Typecheck

必须：

```text
npm --prefix apps/web run typecheck
= PASS
```

---

# 169. Build

必须：

```text
npm --prefix apps/web run build
= PASS
```

---

# 170. Lock

必须：

```text
uv lock --check = PASS

LOCKFILE_CHANGES = 0
```

---

# 171. Diff

必须：

```text
git diff --check = PASS
```

---

# 172. Service Regression

Implementation exact-SHA CI继续要求：

```text
PostgreSQL

Redis

MinIO
```

current required integration：

```text
PASS
```

---

# 173. Linux / Windows Scientific Replay

继续：

```text
Linux replay = PASS

Windows replay = PASS
```

这些不是 12-3新 science。

只是防止 UX改动破坏 retained infrastructure。

---

# 174. Browser CI

必须：

```text
Chromium PASS

Firefox PASS

WebKit PASS

390x844 PASS
```

至少覆盖：

```text
Workspace shell

result-first flow

chart viewer

3D viewer

selection

heavy viewer lifecycle

partial/error/stale

mobile
```

---

# 175. npm Audit

如果 configured mirror仍：

```text
404_NOT_IMPLEMENTED
```

必须：

```text
npm audit = UNAVAILABLE
```

不得写：

```text
PASS
```

---

# 176. Security

必须：

```text
NO_PHASE12_3_ARBITRARY_CODE_EXECUTION = PASS

NO_PHASE12_3_ARTIFACT_HTML_EXECUTION = PASS

NO_PHASE12_3_ARTIFACT_JAVASCRIPT_EXECUTION = PASS

NO_PHASE12_3_IFRAME_EXECUTION = PASS

NO_PHASE12_3_EXTERNAL_ARTIFACT_URL_EXECUTION = PASS

NO_PHASE12_3_FRONTEND_SCIENTIFIC_RECOMPUTATION = PASS

NO_PHASE12_3_LLM_SCIENTIFIC_AUTHORITY = PASS

NO_PHASE12_3_EXTERNAL_SCIENTIFIC_API = PASS

NO_SECRET_PATTERN_HITS = PASS
```

---

# 177. No LLM

必须：

```text
PHASE12_3_NEW_LLM_CALL_SITES = 0

PHASE12_3_REAL_LLM_CALLS = 0
```

---

# 178. Mandatory Result Markers

必须：

```text
PHASE12_3_PRODUCTION_UI_CHANGES =
YES_WORKSPACE_AND_VIEWER_PRESENTATION

PHASE12_3_BACKEND_BEHAVIOR_CHANGES = 0

PHASE12_3_SCIENTIFIC_BEHAVIOR_CHANGES = 0

PHASE12_3_WORKSPACE_DOMAIN_CONTRACT_CHANGES = 0

PHASE12_3_SELECTION_SEMANTIC_CHANGES = 0

PHASE12_3_ARTIFACT_CONTRACT_CHANGES = 0

PHASE12_3_REPORT_AUTHORITY_CHANGES = 0

PHASE12_3_RECIPE_AUTHORITY_CHANGES = 0

PHASE12_3_NEW_SCIENTIFIC_TOOLS = 0

PHASE12_3_NEW_SCIENTIFIC_ALGORITHMS = 0

PHASE12_3_NEW_ARTIFACT_FAMILIES = 0

PHASE12_3_NEW_DATAPROFILE_VERSION = 0

PHASE12_3_NEW_ANALYSISPLAN_VERSION = 0

PHASE12_3_NEW_DATABASE_MIGRATIONS = 0

PHASE12_3_NEW_PUBLIC_API_FAMILIES = 0

PHASE12_3_NEW_DEPENDENCIES = 0

PHASE12_3_LOCKFILE_CHANGES = 0

PHASE12_3_NEW_LLM_CALL_SITES = 0

PHASE12_3_REAL_LLM_CALLS = 0

PHASE12_3_FRONTEND_SCIENTIFIC_RECOMPUTATION = 0
```

---

# 179. Workspace Authority Markers

必须：

```text
ONE_WORKSPACE_PER_JOB = YES

SERVER_WORKSPACE_AUTHORITY = UNCHANGED

URL_ACTIVE_PANEL_AUTHORITY = UNCHANGED

URL_EXACT_SELECTION_AUTHORITY = UNCHANGED

TRANSIENT_MEMORY_AUTHORITY = UNCHANGED

LOCAL_STORAGE_CANONICAL_AUTHORITY = NONE

SESSION_STORAGE_CANONICAL_AUTHORITY = NONE

LATEST_WORKSPACE_BINDING = 0

LATEST_ARTIFACT_BINDING = 0

FUZZY_SELECTION_REBINDING = 0
```

---

# 180. Viewer Markers

必须：

```text
RESULT_FIRST_UI = YES

UNIFIED_SCIENTIFIC_VIEWER_CHROME = YES

CURRENT_SCIENTIFIC_VIEWER_UNCLASSIFIED = 0

HEAVY_VIEWER_LAZY = YES

METADATA_FIRST = YES

HIDDEN_HEAVY_VIEWER_MOUNTS = 0

STALE_REQUEST_RESULT_BINDINGS = 0

WEBGL_RESOURCE_LEAKS_IN_REQUIRED_CASES = 0

SCIENTIFIC_SERIES_COLOR_SEMANTIC_CHANGES = 0
```

---

# 181. Scientific Honesty Markers

必须：

```text
SUPPORTED_EQUALS_VALIDATED = NO

MAPPING_ONLY_VISUAL_UPGRADE = 0

NOT_APPLICABLE_VISUAL_UPGRADE = 0

V4_VISUAL_FABRICATION = 0

BROWSER_PASS_EQUALS_SCIENTIFIC_PASS = NO

SERVICE_PASS_EQUALS_SCIENTIFIC_PASS = NO

SCREENSHOT_NUMERIC_SCIENTIFIC_AUTHORITY = NONE

WEBGL_NUMERIC_SCIENTIFIC_AUTHORITY = NONE

PLOTLY_NUMERIC_SCIENTIFIC_AUTHORITY = NONE

FRONTEND_SCIENTIFIC_AUTHORITY = NONE
```

---

# 182. Baseline Markers

必须：

```text
REGISTRY_BEFORE_12_3 = 62
REGISTRY_AFTER_12_3 = 62

DATAPROFILE_BEFORE_12_3 = 2.4
DATAPROFILE_AFTER_12_3 = 2.4

MIGRATION_BEFORE_12_3 =
0007_phase10m1_workspace_domain

MIGRATION_AFTER_12_3 =
0007_phase10m1_workspace_domain
```

---

# 183. UX Problem Markers

必须：

```text
PHASE12_3_OWNED_PROBLEMS =
<exact IDs>

PHASE12_3_OWNED_PROBLEM_COUNT =
<actual>

PHASE12_3_OWNED_PROBLEMS_CLOSED =
<same actual>

PHASE12_3_OWNED_PROBLEMS_OPEN = 0

NEW_P0_INTRODUCED_BY_12_3 = 0

NEW_P1_INTRODUCED_BY_12_3 = 0
```

---

# 184. Acceptance Marker

必须：

```text
P12X3_ACCEPTANCE = 8/8
```

exact IDs/descriptions来自 canonical acceptance plan。

---

# 185. Accessibility Markers

至少：

```text
WORKSPACE_KEYBOARD_NAVIGATION = PASS

VIEWER_TOOLBAR_KEYBOARD = PASS

FOCUS_RESTORATION_REQUIRED_CASES = PASS

VIEWER_STATUS_NON_COLOR = PASS

MOBILE_TOUCH_TARGETS = PASS

REDUCED_MOTION = PASS

TABLE_TEXT_ALTERNATIVES_REQUIRED_CASES = PASS
```

但：

```text
FULL_PRODUCT_ACCESSIBILITY_COMPLETE = NO
```

---

# 186. Required results.md Structure

至少：

# Phase 12-3 Scientific Workspace + Scientific Viewer Experience Result

1. Conclusion
2. Phase 12-2 Baseline
3. Entry Gate
4. Repository State
5. DS2 Authority
6. Phase 11 Scientific Authority
7. Phase 12-3 Handoff Integrity
8. UX Problem Ownership
9. Production Behavior Changes
10. Workspace Domain Authority
11. Workspace Information Architecture
12. Workspace Overview
13. Data Destination
14. Analysis Destination
15. Results Destination
16. Findings/Evidence/Report Structural Destinations
17. Advanced / Provenance / Developer Detail Structure
18. Result-First Experience
19. Artifact Gallery Relationship
20. Artifact Provenance Preservation
21. Selection Identity
22. Selection URL Authority
23. Back/Forward Selection Restoration
24. Result Header Pattern
25. Unified Scientific Viewer Chrome
26. Viewer Inventory
27. Viewer Toolbar
28. Selection Affordances
29. Warning/Limitation Presentation
30. Loading / Presentation Failure
31. Stale / Missing Result
32. Table/Text Alternatives
33. Plotly Viewer Foundation
34. WebGL/3D Viewer Foundation
35. Dataset Explorer
36. Materials ML
37. Composition Space
38. Structure
39. Coordination
40. Local Environment / Polyhedra
41. Experimental XRD
42. Trajectory
43. RDF
44. MSD
45. Diffusion
46. Phonon
47. Brillouin Zone
48. Volumetric
49. Band Structure
50. DOS
51. Combined Band + DOS
52. Scientific Color Mapping
53. Metadata-First Loading
54. Heavy Viewer Lazy Loading
55. Cancellation
56. Cache Identity
57. WebGL Cleanup
58. Workspace Reload/Recovery
59. Workspace Switch Cleanup
60. Cross-Workspace Isolation
61. Cross-Project Isolation
62. Desktop 1440x900
63. Desktop 1280x720
64. Mobile 390x844
65. 200% Zoom
66. Keyboard / Focus
67. Reduced Motion
68. Accessibility Foundation
69. Browser Matrix
70. Scientific Payload Non-Change
71. Workspace Authority Non-Change
72. Artifact Contract Non-Change
73. Frontend No-Recomputation
74. Phase 12-3 Problem Closure
75. Deferred Problems
76. Phase 12-4 Handoff
77. Security
78. LLM / DeepSeek
79. Database/API/Dependency Freeze
80. Registry/DataProfile Freeze
81. Backend Regression
82. Frontend Regression
83. Typecheck
84. Build
85. Service Regression
86. Linux/Windows Replay
87. npm Audit
88. Evidence Inventory
89. Evidence Manifest
90. Files Changed
91. Acceptance Registry
92. Implementation Commit
93. Implementation CI
94. Failed Candidates
95. Completion Record
96. Queue Archive
97. Queue State
98. Phase 12-4 Reviewer Gate
99. Final Repository State

---

# 187. PASS Gate

只有全部满足：

```text
Phase 12-2 PASS

Phase 12-2 queue archived

Phase 12-2 implementation exact-SHA CI PASS


HEAD == origin/master at entry

worktree clean

TASK_BLOCK_COUNT = 0


DS2 authority resolves

Phase 12-3 handoff resolves

Phase 11 authority resolves


Registry = 62

DataProfile = 2.4

migration = 0007


Workspace target IA implemented

canonical Workspace route preserved

ONE_WORKSPACE_PER_JOB preserved

server / URL / memory authority preserved

localStorage authority = none


Result-first UI implemented

Artifact provenance preserved

Artifact exact version preserved

latest/fuzzy rebinding = 0


all current scientific viewers classified

unified viewer chrome implemented

chart viewer foundation implemented

3D viewer foundation implemented

warnings/limitations visible

presentation failure typed

stale/missing typed


selection exactness preserved

URL selection authority preserved

no display-label scientific identity

no array-position authority


metadata-first PASS

heavy-viewer lazy PASS

cancellation PASS

exact cache identity PASS

cleanup PASS

hidden heavy-viewer mount = 0


scientific payload diff = 0

frontend scientific recomputation = 0

Artifact contract changes = 0

Workspace authority changes = 0

selection semantic changes = 0


12-3-owned UX problems closed

new P0 = 0

new P1 = 0


future-phase problems remain typed/open

12-4 handoff complete


keyboard PASS

focus PASS

non-color status PASS

touch targets PASS

reduced motion PASS

required table/text alternative PASS


Chromium PASS

Firefox PASS

WebKit PASS

390x844 PASS


backend >= dynamic 12-2 floor

frontend >= dynamic 12-2 floor

typecheck PASS

build PASS

lock PASS

diff PASS

PostgreSQL/Redis/MinIO PASS

Linux replay PASS

Windows replay PASS

evidence integrity PASS

security PASS

secret scan PASS


P12X3 acceptance = 8/8


implementation exact-SHA CI PASS

completion record committed/pushed

queue archive committed/pushed


TASK_BLOCK_COUNT = 0

Phase 12-4 task absent

Phase 13 task absent

HEAD == origin/master

worktree clean
```

才能：

```text
Phase 12-3 = PASS
```

---

# 188. BLOCKED — Phase 12-2 Not Closed

如果 12-2：

```text
not PASS
or
queue not archived
or
implementation CI not PASS
```

必须：

```text
BLOCKED /
PHASE_12_2_DEPENDENCY_NOT_CLOSED
```

不得执行。

---

# 189. BLOCKED — Workspace Authority Changed

如果 implementation需要：

```text
change one-Workspace-per-Job

change Workspace identity

change durable state authority

change URL exact selection authority

introduce localStorage authority
```

必须：

```text
BLOCKED /
WORKSPACE_AUTHORITY_REDESIGN_REQUIRED
```

---

# 190. BLOCKED — Scientific Recomputation

如果 viewer需要 frontend：

```text
compute

fit

classify

derive
```

scientific result才能完成设计：

必须：

```text
BLOCKED /
SCIENTIFIC_AUTHORITY_VIOLATION
```

---

# 191. BLOCKED — New Backend Capability

如果 viewer UX目标必须新增：

```text
backend API family

DB column/table

Artifact family

scientific endpoint
```

必须：

```text
BLOCKED /
BACKEND_CAPABILITY_REVIEW_REQUIRED
```

---

# 192. BLOCKED — Artifact Fuzzy Binding

如果 Gallery/Viewer为了便利：

```text
choose latest

nearest version

matching filename

same title
```

必须 BLOCKED。

---

# 193. BLOCKED — Selection Fuzzy Binding

如果 selection：

```text
falls back by label

array index

nearest coordinate
```

不能 PASS。

---

# 194. BLOCKED — Hidden Limitation

如果 scientific warning/limitation在新 Viewer UX中：

```text
disappears

only exists in hidden raw JSON

is replaced by generic success
```

必须：

```text
BLOCKED /
SCIENTIFIC_UX_MISREPRESENTATION
```

---

# 195. BLOCKED — Viewer Resource Leak

如果 required heavy viewer case：

```text
continues animation

keeps canvas

keeps request

keeps event listener
```

在切换后：

不能 PASS。

---

# 196. BLOCKED — Owned Problems Remain

如果：

```text
PHASE12_3_OWNED_PROBLEMS_OPEN > 0
```

不能 PASS。

---

# 197. BLOCKED — Scope Leakage

如果 12-3提前完成：

```text
Findings/Evidence full redesign

Inspector three-layer redesign

Report/Recipe redesign

full accessibility closure
```

必须 revert scope或 BLOCKED。

---

# 198. Non-Blockers

以下允许继续：

```text
Phase 12-4 Findings/Evidence UX debt

Phase 12-5 Report/Recipe UX debt

Phase 12-6 full mobile/accessibility debt

Phase 12-7 final consistency debt

V4 = 0

reference-limited science

unsupported file formats

Future Scope
```

---

# 199. Implementation Lifecycle

严格：

```text
admit Phase 12-3

→ implement

→ evidence

→ regressions

→ implementation commit

→ push

→ WAIT exact-SHA CI

→ if PASS:

append results.md completion

→ completion commit/push

→ no wait

archive only Phase 12-3 task

→ archive commit/push

→ no wait

→ stop
```

---

# 200. Failed Candidate

CI失败：

必须保留：

```text
SHA

CI run

failed job

failure reason
```

然后：

```text
fix-forward
```

禁止：

```text
force push

rewrite history

delete browser coverage

disable scientific replay

remove heavy-viewer lifecycle test

change Artifact identity

change selection authority

move UX problem ownership
```

---

# 201. Completion Terminology

最终使用：

```text
IMPLEMENTATION_VERIFIED_BY_EXACT_SHA_CI

COMPLETION_RECORDED

QUEUE_ARCHIVED
```

除非 completion/archive真的额外等待 CI。

---

# 202. Final Successful State

成功后：

```text
Phase 12-3:
PASS /
SCIENTIFIC_WORKSPACE_REDESIGNED /
SCIENTIFIC_VIEWER_EXPERIENCE_UNIFIED /
QUEUE_ARCHIVED

Phase 12:
IN_PROGRESS /
WORKSPACE_AND_SCIENTIFIC_VIEWER_EXPERIENCE_COMPLETE

Phase 12-4:
REVIEWER_GATE /
AWAITING REVIEWER PROMPT

Phase 13:
ROADMAP_APPROVED /
NOT_QUEUED /
NOT_EXECUTABLE

TASK_BLOCK_COUNT = 0

PHASE_12_4_EXECUTABLE_TASK_CREATED = NO

PHASE_13_EXECUTABLE_TASK_CREATED = NO
```

---

# 203. What Completion Means

可以说：

```text
The Scientific Workspace now exposes the sealed
Workspace information architecture and a result-first
scientific exploration experience with unified chart
and 3D viewer conventions, exact versioned source and
selection identity, explicit scientific limitations,
metadata-first lazy loading, and bounded responsive
presentation while retaining the original Workspace,
Artifact and scientific authority contracts.
```

---

# 204. What Completion Does NOT Mean

不能说：

```text
Findings/Evidence redesign is complete.

Inspector/Provenance redesign is complete.

Report/Recipe redesign is complete.

Full mobile/accessibility closure is complete.

Phase 12 is complete.

The product is release-ready.
```

---

# 205. Phase 12-4 Gate

最终必须：

```text
Phase 12-4:
REVIEWER_GATE /
AWAITING REVIEWER PROMPT

PHASE_12_4_EXECUTABLE_TASK_CREATED = NO
```

---

# 206. Stop Rule

完成后立即停止。

不得：

```text
start Findings redesign

start Evidence drilldown redesign

start Inspector redesign

start Provenance redesign

start Report redesign

start Recipe redesign

perform Phase 12-6 closure

perform Phase 12-7 closure

start Phase 13
```

返回 reviewer：

```text
Phase 12-3 final result

implementation SHA

implementation exact-SHA CI

completion SHA

archive SHA

exact 12-3-owned UX problem IDs/status

P12X3 8/8 result

Workspace IA implementation summary

viewer inventory

selection authority proof

Artifact authority proof

scientific payload non-change proof

heavy viewer lazy/cancel/cleanup evidence

browser/mobile/accessibility evidence

remaining problem ownership

Phase 12-4 handoff state
```

然后等待 reviewer。



---END---
