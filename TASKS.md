---TASK---
 状态：已完成

# Phase 12-4 Reviewer Prompt

# Findings + Evidence + Inspector + Provenance Experience

你现在执行：

# Phase 12-4：Findings / Evidence / Inspector / Provenance Experience

中文：

# 科学发现 + 证据 + 检查器 + 来源追溯核心体验重构

本阶段属于：

```text
Phase 12:
Comprehensive UI / UX
Product Experience Redesign
```

当前序列：

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
= COMPLETE

12-3
Scientific Workspace
+ Scientific Viewer Experience
= COMPLETE

12-4
Findings / Evidence /
Inspector / Provenance Experience
= CURRENT AUTHORIZED PHASE

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

Phase 12-4 的核心任务不是再改 Workspace 或 scientific Viewer。

它要解决的是：

> 用户看到一个科学结论之后，如何快速理解它是什么、可信度如何、基于哪些证据、有哪些限制，以及如何沿着 exact provenance 一直追溯到真正的 persisted scientific authority。

目标链：

```text
Scientific Result

→ Finding

→ Claim meaning

→ Qualification / limitation

→ Supporting Evidence

→ Exact scientific fact

→ Artifact

→ Tool + version

→ parameters

→ source data identity

→ lineage

→ provenance
```

用户应该能够回答：

```text
What is the finding?

What exactly supports it?

What limits it?

Which result produced it?

Which Artifact contains the source facts?

Which Tool/version produced that Artifact?

Which exact inputs and parameters were used?

Is this direct fact, qualified interpretation,
limitation, warning, or recommendation?

Can I inspect the complete provenance
without being forced to understand raw JSON?
```

核心产品目标：

```text
TRUST_PATH_FIRST = YES

SCIENTIFIC_AUDITABILITY_RETAINED = YES
```

---

# 1. Fundamental Boundary

必须：

```text
FINDINGS_UX_REDESIGN
!=
SCIENTIFIC_INTERPRETATION_REDESIGN
```

以及：

```text
EVIDENCE_UX_REDESIGN
!=
EVIDENCE_AUTHORITY_REDESIGN
```

以及：

```text
PROVENANCE_UX_REDESIGN
!=
SCIENTIFIC_LINEAGE_REDESIGN
```

Phase 12-4 允许改变：

```text
finding information hierarchy

finding cards / lists

claim presentation

confidence / qualification presentation

warning / limitation placement

evidence navigation

evidence detail presentation

Inspector information architecture

Inspector progressive disclosure

Provenance presentation

lineage presentation

developer detail hierarchy

selection / navigation presentation

copy / terminology

responsive presentation

accessibility behavior
```

禁止改变：

```text
ScientificEvidenceBundle semantics

ScientificEvidenceItem semantics

ScientificClaim semantics

GroundedScientificInterpretation semantics

grounding validation

claim predicates

claim confidence authority

claim supportingEvidence IDs

claim limitingEvidence IDs

Artifact values

Artifact lineage

Tool identity/version

input identity

units

parameters

scientific algorithms

scientific validation level
```

---

# 2. Reviewer Authorization

正式授权：

```text
AUTHORIZED_PHASE = Phase 12-4

MAX_PHASES_EXECUTED = 1

PHASE_12_4_QUEUE_ADMISSION =
CONDITIONALLY_AUTHORIZED
```

只有 Entry Gate PASS 后：

才允许创建：

```text
one Phase 12-4 task
```

不得执行：

```text
Phase 12-5

Phase 12-6

Phase 12-7

Phase 13
```

---

# 3. Mandatory Phase 12-3 Dependency

必须从真实 repository 动态验证：

```text
results.md

TASKS.md

docs/ROADMAP.md

persistent/

docs/phase12/

docs/phase12/evidence/

git history
```

取得：

```text
PHASE_12_3_IMPLEMENTATION_SHA

PHASE_12_3_IMPLEMENTATION_CI_RUN

PHASE_12_3_IMPLEMENTATION_CI_RESULT

PHASE_12_3_COMPLETION_SHA

PHASE_12_3_QUEUE_ARCHIVE_SHA
```

当前 reviewer/user 已知：

```text
Implementation:
9b38a753bda134e9c27425e1193d2980a0790731

Implementation CI:
31370240101
PASS

Completion:
2abbcf20ff283931536c6643a3ce96347fd24556

Queue archive:
f6a39ca4d6afc560662d98c6f882ecc10a0e3d71
```

但 execution agent：

不得仅依赖 Prompt。

必须通过 Git/repository 验证。

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
Phase 12-4 executable task = absent

Phase 12-5 executable task = absent

Phase 13 executable task = absent
```

否则：

```text
PHASE_12_4_ENTRY_GATE = BLOCKED
```

---

# 5. Phase 12-3 Required Result

必须确认：

```text
Phase 12-3 =
PASS
```

以及至少：

```text
RESULT_FIRST_UI = YES

UX-002 = CLOSED

UX-003 = CLOSED

UX-004 = OPEN / OWNER 12-4

frontend scientific recomputation = 0

Workspace authority unchanged

Artifact authority unchanged

Selection authority unchanged
```

---

# 6. 12-4 Handoff

必须读取唯一 canonical：

```text
Phase12_4FindingsEvidenceInspectorHandoff
```

或 repository current canonical equivalent。

必须验证至少包含：

```text
Design System version/hash

Global shell state

Workspace IA implementation

Result-first structure

Scientific viewer chrome

Selection presentation

warning / limitation placement

Inspector entry points

Findings destination

Evidence destination

Provenance destination

Developer Details destination

remaining Phase 12-4 UX problem IDs

Phase 11 claim/evidence authority refs

mobile Inspector constraints

accessibility constraints

browser evidence refs
```

如果 handoff 不存在或不完整：

```text
BLOCKED /
PHASE_12_4_HANDOFF_INVALID
```

---

# 7. Canonical UX Problem

必须从：

```text
phase12_ux_problem_matrix
```

动态读取：

```text
owner = 12-4
```

当前 expected canonical problem：

```text
UX-004
```

但：

必须读取 repository 中：

```text
exact severity

exact currentBehavior

exact consequence

exact targetOutcome

exact acceptanceMethod
```

不得由 Prompt 猜测或重写 UX-004 定义。

---

# 8. UX Problem Closure Rule

Phase 12-4 PASS 前：

```text
PHASE12_4_OWNED_PROBLEMS_OPEN = 0
```

禁止：

```text
change owner

lower severity

delete problem

rename problem
```

逃避 closure。

如果 current repository 中 owner count != expected：

报告实际 authority。

---

# 9. Future UX Problems

必须动态读取并保持：

```text
Phase 12-5 owned problems

Phase 12-6 owned problems

Phase 12-7 owned problems
```

不得提前把它们全部写成：

```text
FIXED
```

若 foundation 改善：

记录：

```text
FOUNDATION_IMPROVED
/
FINAL_CLOSURE_REMAINS_WITH_OWNER
```

---

# 10. Phase 12-0 Experience Authority

继续消费 sealed：

```text
Meaning before mechanism

Result before Artifact

Progressive disclosure

Scientific limitations are first-class

Exact scientific identity remains available

Developer details remain accessible
but subordinate

No UX convenience creates scientific authority
```

---

# 11. Core Trust Path

正式目标：

```text
Finding
→ Evidence
→ Artifact
→ Tool/version
→ Input identity
→ Provenance
```

Phase 12-4 必须让这个 trust path：

```text
discoverable

human-readable

exact

bounded

keyboard-accessible

mobile-usable

scientifically honest
```

---

# 12. Trust Path Must Be Bidirectional Where Authority Exists

允许用户从：

```text
Finding
→ Evidence
→ Artifact
→ Provenance
```

向下追。

如果 existing exact mappings允许：

也应支持：

```text
Artifact
→ Evidence
→ Findings
```

或：

```text
selected Evidence
→ related Finding
```

但不得使用：

```text
fuzzy title matching
```

实现关联。

---

# 13. Existing Scientific Interpretation Authority

必须动态读取 current contracts。

当前 architecture至少包括：

```text
ScientificEvidenceBundle 1.0

ScientificEvidenceItem 1.0

ScientificEvidenceRef 1.0

ScientificClaim 1.0

GroundedScientificInterpretation 1.0
```

repository current contracts为 authority。

---

# 14. Interpretation Is Read-Only in 12-4

必须：

```text
INTERPRETATION_RECOMPUTATION = 0

INTERPRETATION_REGENERATION = 0

CLAIM_GENERATION = 0

EVIDENCE_PROJECTION_RECOMPUTATION = 0
```

Phase 12-4：

只改善如何呈现已有 persisted interpretation。

---

# 15. No New LLM Interpretation

必须：

```text
PHASE12_4_NEW_LLM_CALL_SITES = 0

PHASE12_4_REAL_LLM_CALLS = 0
```

不能为了更漂亮的 Finding 文案：

重新调用 DeepSeek。

---

# 16. Persisted Interpretation Only

UI 展示 Finding 的 authority：

必须来自：

```text
persisted
GroundedScientificInterpretation
```

及其 persisted claims/evidence membership。

不得用 frontend：

```text
summarize raw Artifact

infer finding from chart

infer finding from table

generate conclusion from warning
```

---

# 17. Finding Taxonomy

必须从 current ScientificClaim contract读取 exact enums。

当前 architecture可能包括：

```text
OBSERVATION

COMPARISON

ANOMALY

WARNING

LIMITATION

RECOMMENDATION

NO_SUPPORTED_CONCLUSION
```

实际 repository contract优先。

UI 不得创建新的 claim scientific category。

---

# 18. Finding Type Presentation

不同 Claim 类型需要可辨识：

```text
Finding / Observation

Comparison

Warning

Limitation

Recommendation

No supported conclusion
```

但：

```text
visual category
!=
new scientific semantics
```

---

# 19. Observation vs Interpretation

Finding UI 应帮助用户区分：

```text
directly supported fact
```

与：

```text
qualified interpretation
```

不得让所有 claims 看起来都是：

```text
scientific fact
```

---

# 20. Confidence / Qualification

必须从 current claim contract读取 exact confidence vocabulary。

当前 architecture至少存在：

```text
DIRECT

QUALIFIED

LIMITED
```

如果 repository actual不同：

使用 actual。

---

# 21. No Probability Fabrication

禁止把：

```text
DIRECT
QUALIFIED
LIMITED
```

转成：

```text
95% confidence
72% confidence
```

除非 persisted contract真的包含这个数。

---

# 22. Finding Card Structure

默认 Finding card 建议按：

```text
Claim statement

Claim type

Qualification / confidence

Important warning / limitation

Primary supporting evidence summary

Evidence count

Inspect evidence

Inspect provenance
```

组织。

不要先显示：

```text
claimId
bundleId
Artifact checksum
locator
```

---

# 23. Exact IDs Still Available

必须通过：

```text
Scientific Details

Provenance

Developer Details
```

访问：

```text
claimId

interpretationId

bundleId

evidence IDs

Artifact IDs

checksums

Tool IDs

versions
```

---

# 24. Finding Hierarchy

当 findings较多时：

必须建立稳定 hierarchy。

可以按 authoritative metadata：

```text
claim type

importance if persisted

result grouping

source result
```

组织。

禁止 frontend根据：

```text
wording sentiment

color

text length

LLM ranking
```

决定 scientific importance。

---

# 25. No Arbitrary Finding Ranking

如果 backend没有 ranking authority：

UI不得显示：

```text
Most important finding
Top finding
```

作为 scientific authority。

可以使用：

```text
Key findings
```

仅当 canonical deterministic product rule已定义。

否则使用中性：

```text
Findings
```

---

# 26. Recommendations

Recommendation 必须明显：

```text
non-executable
```

保留：

```text
recommendation != executable plan
```

禁止：

```text
Run recommendation
Execute this
Apply
```

直接触发 Plan/Job。

---

# 27. Recommendation CTA

如果需要下一步 action：

最多允许：

```text
Use as new analysis request
```

等进入正式：

```text
Intent
→ Eligibility
→ Planner
```

路径。

前提 current architecture已有安全 route。

不得自动执行。

---

# 28. NO_SUPPORTED_CONCLUSION

必须作为正式、可理解的结果。

不能：

```text
hide empty Finding panel
```

让用户误以为系统失败。

应该解释：

```text
No supported scientific conclusion
was generated from the available evidence.
```

具体 wording使用 project i18n。

---

# 29. Partial Interpretation

当：

```text
INTERPRETATION_READY_WITH_LIMITS
```

必须明显展示：

```text
successful evidence scope

failed / blocked scope

missing desired outputs

limitations applying to claims
```

---

# 30. Partial Is Not Success Green

不能让：

```text
READY_WITH_LIMITS
```

视觉等价：

```text
fully complete success
```

---

# 31. All-Failed / No Evidence

对于：

```text
NO_SUPPORTED_EVIDENCE

SOURCE_INTEGRITY_FAILED

VALIDATION_FAILED

PROVIDER_FAILED
```

必须分别保留 typed meaning。

不要全部叫：

```text
No findings
```

---

# 32. Finding Warning Placement

如果 Claim自身受限制：

warning/limitation必须：

```text
near the Claim
```

而不是只存在于：

```text
Evidence tab
Developer JSON
```

---

# 33. Limitation Is First-Class

必须：

```text
SCIENTIFIC_LIMITATION_FIRST_CLASS = YES
```

不能用：

```text
small gray footnote
```

隐藏重要 limitation。

---

# 34. Limitation Persistence

mandatory limitation：

不得永久 dismiss。

可以：

```text
collapse
```

但必须保留 persistent indicator。

---

# 35. Warning vs Limitation

必须清楚区分：

```text
runtime warning

scientific limitation

validation limitation

presentation warning
```

不得全部使用同一个：

```text
Warning
```

badge。

---

# 36. Evidence Experience Mission

Evidence UI 应回答：

```text
What exact fact supports this claim?

Where did that fact come from?

What value/unit/entity is involved?

Which Artifact stores it?

Which Tool produced that Artifact?

Is this supporting, limiting or contradicting evidence?
```

---

# 37. Evidence Membership Authority

Evidence→Claim关联必须严格来自：

```text
supporting evidence IDs

limiting evidence IDs

contradicting evidence IDs
```

或 current exact contract。

不得根据文本相似度关联。

---

# 38. Evidence Role

必须视觉区分：

```text
SUPPORTING

LIMITING

CONTRADICTING
```

如果 current contract有相应角色。

没有 persisted role：

不得自行推断。

---

# 39. Evidence Item Structure

每个 evidence item 默认优先：

```text
human-readable fact

value

unit

subject/entity

source result

role in claim
```

然后再：

```text
Artifact

Tool/version

locator

checksum

lineage
```

---

# 40. Evidence Numeric Authority

所有数值：

必须来自 exact evidence item / Artifact authority。

禁止：

```text
round and then use rounded value as canonical

calculate delta

calculate percentage

convert unit

calculate significance
```

除非 persisted evidence已经提供。

---

# 41. Display Formatting

允许：

```text
bounded display formatting

approved rounding for display
```

但：

exact value必须能够通过 detail访问。

---

# 42. Units

单位：

必须显示 persisted unit。

禁止：

```text
frontend unit guessing

frontend automatic unit conversion
```

除非现有 validated presentation contract已经授权。

---

# 43. Entity Identity

Evidence subject可显示人类友好标签。

但 canonical identity必须保持 exact。

禁止：

```text
display label = scientific identity
```

---

# 44. Evidence Locator

projector-owned semantic locator：

可在 Scientific Details / Provenance 中展示。

不得把：

```text
array index

raw JSON pointer

filesystem path
```

变成用户科学 authority。

---

# 45. Evidence Source Artifact

每项 Evidence必须能够追到：

```text
exact Artifact ID

Artifact version/contract

checksum

source ToolCall/step
```

如果 current Evidence contract支持。

---

# 46. Artifact Payload Boundary

Evidence UI不需要加载完整 heavy Artifact payload才能显示 trust path。

优先：

```text
metadata
+
projected evidence fact
```

---

# 47. Metadata First

继续：

```text
METADATA_FIRST = YES
```

不要因为 Evidence drilldown：

自动打开 heavy WebGL Viewer。

---

# 48. Open Source Result

可提供：

```text
Open source result
```

并导航到 exact Result/Artifact。

必须：

```text
exact version
```

禁止 latest。

---

# 49. Selection Integration

如果 Finding/Evidence进入 WorkspaceSelectionContext：

必须使用 current canonical exact identity。

不得建立第二套 selection system。

---

# 50. Evidence Selection

当前 architecture已经支持 evidence item / claim identity contract。

Phase 12-4应：

在 formal support存在时激活这些 exact selections。

如果 mapper不支持：

使用：

```text
NOT_APPLICABLE
or
UNSUPPORTED_WITH_TYPED_REASON
```

不得 fuzzy bridge。

---

# 51. Finding Selection

同理：

Finding / Claim selection必须：

```text
exact Claim identity
```

不能通过 card position。

---

# 52. Cross-Panel Linking

允许：

```text
Finding
→ Evidence panel

Evidence
→ Results

Evidence
→ Provenance

Result
→ related Findings
```

前提每个 link都有 exact authoritative identity。

---

# 53. No Text-Matching Navigation

禁止：

```text
find Artifact whose title resembles claim
```

禁止：

```text
find Tool by displayed result label
```

---

# 54. Inspector Mission

Phase 12-4 正式实现 sealed：

```text
Summary

Scientific Details

Provenance
```

三层 Inspector model。

---

# 55. Inspector Is One System

禁止继续存在：

```text
Artifact Inspector

Finding Inspector

Evidence Inspector

Viewer Inspector

Developer Inspector
```

五套无关的 detail hierarchy。

可以有不同 content adapter。

但 shared conceptual model：

```text
Summary
→ Scientific Details
→ Provenance
```

---

# 56. Inspector Summary

Summary回答：

```text
What is selected?

What does it mean?

What is its current status?

What result/claim/evidence is this?

What important warning/limitation applies?
```

避免：

```text
raw IDs first
```

---

# 57. Inspector Scientific Details

Scientific Details回答：

```text
What exact scientific facts are available?

What values and units?

Which method/Tool was used?

What parameter facts matter?

What qualification/coverage applies?
```

---

# 58. Inspector Provenance

Provenance回答：

```text
Where did this come from?

Which Project/Dataset/version?

Which Profile?

Which Intent/Eligibility/Plan?

Which Tool/step/ToolCall?

Which Artifact/version/checksum?

Which lineage?

Which evidence bundle/claim?
```

只显示实际 applicable facts。

---

# 59. Developer Details

Developer Details可以进一步展示：

```text
raw canonical IDs

semantic hashes

contract versions

audit JSON

provider/repair metadata
```

但应该 subordinate。

可以位于：

```text
Provenance
→ Developer Details
```

或现有 Advanced destination。

---

# 60. No Raw JSON First

普通 Inspector默认不得：

```text
raw JSON
```

作为第一屏。

---

# 61. Raw JSON Remains Available

但不得删除现有 auditability。

要求：

```text
RAW_AUDIT_DETAILS_ACCESSIBLE = YES
```

---

# 62. Inspector Adapters

每种 selected kind可以有 typed adapter：

```text
Result

Artifact

Finding/Claim

Evidence Item

Dataset Sample

Structure Site

Trajectory Frame

Phonon Q-point

Volumetric Field
```

实际 current selection kinds为 authority。

---

# 63. Inspector Must Not Derive Science

每个 adapter只：

```text
project/present persisted fields
```

不得：

```text
calculate
fit
classify
infer
```

---

# 64. Provenance Mission

Provenance UI不是“显示很多 ID”。

目标是：

```text
make lineage understandable
without losing exact identity
```

---

# 65. Provenance Hierarchy

建议 hierarchy：

```text
Source data

→ Analysis context

→ Method / Tool

→ Execution

→ Artifact

→ Evidence

→ Claim
```

实际 applicable层级按 current persisted chain。

---

# 66. Provenance Graph Boundary

如果做 provenance graph：

只能使用：

```text
persisted lineage edges
```

不得：

```text
infer edge by timing

infer edge by same name

infer edge by adjacency
```

---

# 67. AnalysisPlan 0.1

对于 legacy Plan 0.1：

不得 UI invent dependency graph。

显示：

```text
ordered plan
```

并明确：

```text
no explicit dependency graph
```

---

# 68. AnalysisPlan 0.2

对于 Plan 0.2：

可以呈现 exact：

```text
producer

consumer

binding

ports

Artifact lineage
```

但仍使用 human-readable layer优先。

---

# 69. Tool Provenance

显示：

```text
Tool human name
```

同时允许访问：

```text
Tool ID
version
```

不能只显示 Tool ID。

---

# 70. Parameter Provenance

parameters：

可按：

```text
scientifically relevant

advanced

developer
```

分层。

但：

不得隐藏会改变解释的重要 parameter。

---

# 71. Input Provenance

必须在适用时显示：

```text
Dataset/version

resource identity

object/sample identity

target/model/group

structure/site

trajectory/frame

Artifact dependency
```

---

# 72. Checksums

checksum不是普通用户第一层信息。

应该：

```text
available in Provenance/Developer
```

---

# 73. Validation / Coverage Provenance

如果显示：

```text
scientific validation

support status

cross-platform status
```

必须继续四轴分离。

---

# 74. Phase 11 Four-Axis Separation

必须：

```text
Product Support
!=
Scientific Validation
!=
Cross-Platform Reproducibility
!=
Presentation Validation
```

---

# 75. Phase 11 Honesty

必须保留：

```text
12 golden records

8 PASS_INVARIANT

4 NOT_APPLICABLE

numeric cross-platform =
NOT_APPLICABLE

V4 = 0
```

按 current final authority验证。

---

# 76. No Provenance Badge Overclaim

禁止：

```text
Provenance complete
→ Scientifically validated
```

---

# 77. Browser Evidence Boundary

继续：

```text
BROWSER_PASS
!=
SCIENTIFIC_VALIDATION
```

---

# 78. Service Evidence Boundary

继续：

```text
SERVICE_PASS
!=
SCIENTIFIC_VALIDATION
```

---

# 79. Screenshot Boundary

继续：

```text
SCREENSHOT_NUMERIC_SCIENTIFIC_AUTHORITY = NONE
```

---

# 80. Finding Source Status

Finding UI应该能够反映：

```text
direct evidence

qualified evidence

partial evidence

limited evidence

no supported evidence
```

实际 exact states从 interpretation contract读取。

---

# 81. Partial Execution Disclosure

对于 partial Job：

Finding页面必须显示：

```text
successful scope

failed scope

blocked scope

missing outputs
```

不能让 claim看起来覆盖整个 original Plan。

---

# 82. Claim Scope

每个 Claim必须展示其真正：

```text
subject / scope
```

不得扩展到：

```text
entire dataset
entire model
entire material system
```

除非 persisted Claim就是该 scope。

---

# 83. Scientific Wording Freeze

必须保持 professional-science boundaries。

例如：

```text
algorithm-derived coordination
```

不能改：

```text
true bonds
```

---

# 84. XRD Wording

Peak matching：

不得变成：

```text
phase confirmation
```

---

# 85. Diffusion Wording

必须：

```text
estimated over selected fit window
```

不能变：

```text
true diffusion coefficient
```

---

# 86. Electronic Wording

必须维持：

```text
supplied-data-derived
```

不得暗示系统完成 DFT/GW。

---

# 87. Phonon Wording

不得无依据：

```text
stable
```

---

# 88. ML Wording

classification / regression findings：

不能暗示：

```text
generalization beyond supplied evaluation data
```

除非 persisted evidence明确支持。

---

# 89. Recommendation Wording

不能：

```text
You should definitely...
```

将 limited recommendation写成 definitive scientific instruction。

---

# 90. No Claim Editing

Phase 12-4 不增加：

```text
edit claim

rewrite finding

approve claim

manually change confidence

manually remove limitation
```

---

# 91. No Evidence Editing

不得：

```text
attach arbitrary evidence

remove mandatory supporting evidence

change locator

change source Artifact
```

---

# 92. No Provenance Editing

Provenance完全：

```text
read-only
```

---

# 93. Report Boundary

12-4可以让 Findings/Evidence：

有清楚的：

```text
Report source eligibility indication
```

如果 current Report authority已有。

但不能开始重构：

```text
Report Builder
```

这属于 12-5。

---

# 94. Add to Report Boundary

若 current product已有 exact source-add interaction：

可以保持。

不得在 12-4 新定义：

```text
Report composition semantics
```

---

# 95. Recipe Boundary

12-4不修改 Recipe。

继续：

```text
RECIPE_EXECUTION_AUTHORITY = NONE
```

---

# 96. Workspace Boundary

12-3已经完成 Workspace IA。

12-4不得重新组织：

```text
Overview
Data
Analysis
Results
Findings
Evidence
Report
Advanced
```

只实现：

```text
Findings/Evidence/Inspector/Provenance
```

内部体验。

---

# 97. Viewer Boundary

12-3已经完成 Viewer chrome。

12-4不得重新设计：

```text
chart controls

3D controls

toolbar

legend system
```

只允许增加必要：

```text
Inspect evidence

Open provenance
```

入口。

---

# 98. Planner Boundary

不得回改 12-2：

```text
Prompt
Intent
Clarification
Eligibility
Human Plan
Execution
```

---

# 99. Design System

必须继续消费：

```text
Design System 2.0
```

不得创建 parallel design system。

---

# 100. Information Density

Findings/Evidence页面应：

```text
dense enough for professional review

but progressive
```

避免：

```text
one giant card per evidence item
```

造成无意义纵向滚动。

---

# 101. Finding List Density

建议支持：

```text
compact summary rows/cards

expand selected Finding
```

具体 architecture按 existing frontend。

---

# 102. Evidence List Density

应允许快速比较：

```text
role

subject

value/unit

source

limitation
```

不应每项默认展开所有 provenance。

---

# 103. Evidence Count

Evidence count只能来自 persisted membership。

不能从 DOM计算作为 authority。

---

# 104. Contradicting Evidence

如果 current contract存在 contradiction：

必须显眼。

不能把 supporting evidence放前面、contradicting evidence藏到底部。

---

# 105. Missing Evidence

如果 Claim引用的 evidence无法解析：

必须：

```text
SOURCE_INTEGRITY_FAILED
or typed equivalent
```

不得隐藏 broken reference。

---

# 106. Cross-Scope Evidence

cross-job/cross-project evidence：

必须继续拒绝。

---

# 107. Exact Scope

必须保持：

```text
project

dataset/version

Job

Plan

Artifact

interpretation
```

scope一致。

---

# 108. Historical Compatibility

必须支持：

```text
jobs without interpretation

legacy interpretation records

Plan 0.1

Plan 0.2

partial execution

missing Artifact

stale source

no supported evidence
```

以 typed状态呈现。

---

# 109. No Fake Findings for Historical Jobs

如果 old Job没有 interpretation：

显示：

```text
Findings unavailable
```

不能 browser从 Artifact summary生成新 Finding。

---

# 110. Provenance for Legacy Data

legacy facts只显示真实 available chain。

缺失层：

```text
Unavailable
```

不得 invent。

---

# 111. Loading UX

区分：

```text
Findings loading

Evidence loading

Inspector detail loading

Provenance loading
```

避免 blank Workspace。

---

# 112. Loading Context Preservation

加载 Evidence时：

Finding本身必须继续可见。

---

# 113. Error UX

至少覆盖：

```text
interpretation missing

evidence missing

source integrity failure

Artifact unavailable

cross-scope denial

stale source

provenance incomplete

provider-failed interpretation

validation-failed interpretation
```

---

# 114. Error Structure

继续：

```text
What happened?

Why?

What can I still inspect?

What was preserved?
```

---

# 115. Renderer Failure Independence

Viewer presentation failure：

不应导致 Evidence页面消失。

Evidence基于 persisted facts。

---

# 116. Evidence Does Not Depend on Screenshot

如果 chart无法render：

Evidence numeric/table fact仍应可访问。

---

# 117. Accessibility

所有 12-4 new/reworked UI：

必须：

```text
semantic headings

keyboard navigation

visible focus

accessible names

non-color claim status

non-color evidence roles

focus restoration

screen-reader-readable warnings

touch targets >= 44x44
```

---

# 118. Inspector Keyboard

必须能够：

```text
open

switch Summary/Scientific Details/Provenance

close

return focus to origin
```

---

# 119. Evidence Keyboard

必须能够：

```text
select Finding

open evidence

navigate evidence items

open source result

open Inspector

return
```

---

# 120. Mobile Authority

继续：

```text
one active panel

context/navigation drawer

panel switcher

Inspector bottom sheet
```

---

# 121. Mobile Inspector

在：

```text
390x844
```

必须使用 bounded bottom-sheet behavior。

不能：

```text
desktop side inspector compressed to 390px
```

---

# 122. Mobile Evidence

Evidence list：

不得水平溢出。

长 IDs/units：

必须：

```text
wrap / truncate-with-access
```

---

# 123. Mobile Trust Path

用户必须能在 mobile完成：

```text
Finding
→ Evidence
→ Provenance
→ back
```

而不丢 context。

---

# 124. Full Mobile Closure Boundary

仍然：

```text
FULL_PRODUCT_MOBILE_CLOSURE = NO
```

最终 closure属于 12-6。

---

# 125. Full Accessibility Boundary

仍然：

```text
FULL_PRODUCT_ACCESSIBILITY_COMPLETE = NO
```

最终 closure属于 12-6 / 12-7。

---

# 126. 200% Zoom

至少测试：

```text
Findings list

expanded Finding

Evidence detail

Inspector

Provenance
```

essential info不能隐藏。

---

# 127. Reduced Motion

drawer/sheet/Inspector transitions：

使用 DS2 reduced-motion policy。

---

# 128. i18n

如果 current app支持：

```text
zh-CN
English
```

所有新增 user-facing strings：

必须进入现有机制。

---

# 129. Scientific Terminology Consistency

至少审查：

```text
Finding

Evidence

Scientific Details

Provenance

Limitation

Warning

Qualified

Direct

Recommendation

Unsupported

Unavailable
```

---

# 130. Do Not Translate IDs

Tool IDs、contract versions、hashes：

保持 exact。

---

# 131. No New Backend Capability

默认：

```text
PHASE12_4_BACKEND_BEHAVIOR_CHANGES = 0
```

应复用 existing:

```text
interpretation APIs

evidence APIs

Artifact metadata/content APIs

Workspace metadata APIs

lineage/provenance data
```

---

# 132. New API Requirement

如果 UX目标需要新 public API family：

```text
BLOCKED /
BACKEND_CAPABILITY_REVIEW_REQUIRED
```

不得偷偷新增。

允许：

对 existing endpoint做 bug fix：

只有确实是 frontend无法消费既有 authority的 defect。

必须 reviewer-style记录。

---

# 133. Database Freeze

必须：

```text
NEW_DATABASE_TABLES = 0

NEW_DATABASE_COLUMNS = 0

NEW_DATABASE_MIGRATIONS = 0
```

---

# 134. Migration Freeze

继续：

```text
0007_phase10m1_workspace_domain
```

---

# 135. Registry Freeze

必须：

```text
REGISTRY_BEFORE_12_4 = 62

REGISTRY_AFTER_12_4 = 62
```

---

# 136. DataProfile Freeze

必须：

```text
DATAPROFILE_BEFORE_12_4 = 2.4

DATAPROFILE_AFTER_12_4 = 2.4
```

---

# 137. Analysis Contracts Freeze

必须：

```text
AnalysisIntent = unchanged

EligibilityResolution = unchanged

AnalysisPlan 0.1 / 0.2 = unchanged
```

---

# 138. Scientific Evidence Contract Freeze

必须：

```text
SCIENTIFIC_EVIDENCE_BUNDLE_CONTRACT_CHANGES = 0

SCIENTIFIC_CLAIM_CONTRACT_CHANGES = 0

INTERPRETATION_CONTRACT_CHANGES = 0
```

---

# 139. Artifact Freeze

必须：

```text
NEW_ARTIFACT_FAMILIES = 0

SCIENTIFIC_ARTIFACT_CONTRACT_CHANGES = 0
```

---

# 140. Workspace Freeze

必须：

```text
WORKSPACE_DOMAIN_CONTRACT_CHANGES = 0

WORKSPACE_SELECTION_CONTRACT_CHANGES = 0
```

---

# 141. Report / Recipe Freeze

必须：

```text
REPORT_AUTHORITY_CHANGES = 0

RECIPE_AUTHORITY_CHANGES = 0
```

---

# 142. Dependency Freeze

必须：

```text
NEW_PYTHON_DEPENDENCIES = 0

NEW_FRONTEND_DEPENDENCIES = 0

LOCKFILE_CHANGES = 0
```

---

# 143. DeepSeek Policy

保持：

```text
REAL_LLM_PROVIDER = DEEPSEEK_ONLY
```

12-4：

```text
REAL_LLM_CALLS = 0
```

---

# 144. No External Scientific API

必须：

```text
EXTERNAL_SCIENTIFIC_API_CALLS = 0
```

---

# 145. Security

必须：

```text
NO_PHASE12_4_ARBITRARY_CODE_EXECUTION = PASS

NO_PHASE12_4_ARTIFACT_JAVASCRIPT = PASS

NO_PHASE12_4_ARTIFACT_HTML_EXECUTION = PASS

NO_PHASE12_4_IFRAME_EXECUTION = PASS

NO_PHASE12_4_DYNAMIC_MODULE_EXECUTION = PASS

NO_PHASE12_4_EXTERNAL_ARTIFACT_URL_EXECUTION = PASS

NO_PHASE12_4_RAW_ARTIFACT_TO_LLM = PASS

NO_PHASE12_4_RECOMMENDATION_AUTO_EXECUTION = PASS

NO_PHASE12_4_CROSS_JOB_EVIDENCE = PASS

NO_PHASE12_4_CROSS_PROJECT_EVIDENCE = PASS

NO_PHASE12_4_STALE_IDENTITY_REBINDING = PASS

NO_SECRET_PATTERN_HITS = PASS
```

---

# 146. Inert Audit Content

raw JSON、Artifact strings、provider text：

必须：

```text
text-only
```

不得 render为 active HTML。

---

# 147. Injection Cases

必须测试：

```text
<script>

<img onerror>

javascript:

iframe

Markdown HTML

path strings

URL strings

prompt injection content
```

在 Finding/Evidence/Provenance中均 inert。

---

# 148. Acceptance IDs

Phase 12-0 已封板：

```text
P12X4-A01
...
P12X4-A08
```

必须从 canonical：

```text
docs/phase12/phase12_acceptance_and_test_plan.md
```

读取 exact descriptions。

---

# 149. Acceptance IDs Immutable

要求：

```text
P12X4_EXPECTED = 8

IMPLEMENTED = 8

MISSING = 0

EXTRA = 0

DUPLICATE = 0

CONFLICTING = 0

SHORTHAND = 0
```

禁止 execution agent：

```text
rename

merge

delete

invent
```

acceptance IDs。

---

# 150. Reviewer Interpretation of P12X4 Scope

repository exact wording为 authority。

但至少应 equivalent覆盖：

```text
A.
Finding hierarchy and scientific claim
presentation

B.
Finding → Evidence exact trust path

C.
Evidence detail and source-result navigation

D.
Three-layer Inspector:
Summary / Scientific Details / Provenance

E.
Exact provenance and lineage presentation

F.
Warnings / limitations / partial /
no-supported-evidence honesty

G.
responsive / keyboard / accessibility /
security trust-path behavior

H.
scientific-authority non-change,
browser / regression / evidence /
lifecycle closure
```

---

# 151. Evidence Directory

建立：

```text
docs/phase12/evidence/
phase12_4_findings_evidence_inspector_provenance/
```

至少：

```text
baseline.txt

entry_gate.md

phase12_3_handoff_snapshot.json

finding_inventory.json

claim_type_matrix.json

finding_hierarchy_matrix.json

finding_qualification_matrix.json

limitation_warning_matrix.json

finding_evidence_membership.json

evidence_inventory.json

evidence_role_matrix.json

evidence_source_matrix.json

evidence_artifact_trace_matrix.json

trust_path_matrix.json

inspector_adapter_matrix.json

inspector_summary_matrix.json

inspector_scientific_details_matrix.json

inspector_provenance_matrix.json

developer_detail_matrix.json

provenance_chain_matrix.json

lineage_matrix.json

plan01_provenance_matrix.json

plan02_provenance_matrix.json

selection_integration_matrix.json

partial_interpretation_matrix.json

no_supported_evidence_matrix.json

integrity_failure_matrix.json

stale_missing_matrix.json

recommendation_boundary.json

scientific_wording_audit.json

phase11_validation_presentation_audit.json

mobile_findings_matrix.json

mobile_inspector_matrix.json

accessibility_matrix.json

zoom_200_matrix.json

browser_matrix.json

before_after_surface_matrix.json

interaction_baseline_comparison.json

scientific_payload_nonchange.json

interpretation_contract_nonchange.json

phase12_4_problem_closure.json

deferred_problem_matrix.json

phase12_5_handoff.json

security.md

secret_scan.txt

manifest.json
```

---

# 152. Canonical Docs

至少：

```text
docs/phase12/
phase12_4_findings_evidence_inspector_provenance.md

phase12_4_finding_information_hierarchy.md

phase12_4_scientific_trust_path.md

phase12_4_evidence_experience.md

phase12_4_inspector_three_layer_model.md

phase12_4_provenance_lineage_experience.md

phase12_4_warning_limitation_qualification.md

phase12_4_responsive_accessibility.md

phase12_4_problem_closure.md

phase12_5_report_recipe_handoff.md

phase12_4_completion.md
```

如现有 canonical naming不同：

复用现有。

不要创建重复 authority。

---

# 153. Canonical Evidence Cases

至少：

```text
Case A
direct observation
with supporting evidence

Case B
qualified comparison

Case C
claim with limitation

Case D
warning

Case E
recommendation
non-executable

Case F
NO_SUPPORTED_CONCLUSION

Case G
partial execution
READY_WITH_LIMITS

Case H
no supported evidence

Case I
source integrity failure

Case J
Plan 0.1 legacy provenance

Case K
Plan 0.2 dependency provenance

Case L
stale/missing Artifact

Case M
mobile Finding→Evidence→Provenance

Case N
injection/inert content
```

---

# 154. Professional Science Cases

至少覆盖有 representative findings/evidence 的：

```text
Dataset / property

Materials ML

Structure

Phonon

Volumetric
```

如果 current professional N1-N5 interpretation数据已存在：

可增加：

```text
coordination

XRD

trajectory/diffusion

electronic
```

但不能制造新 interpretation fixture facts。

---

# 155. Before / After

12-0/12-3 evidence作为 BEFORE。

12-4保存 AFTER。

至少：

```text
Findings list

Finding selected

Evidence drilldown

Evidence source

Inspector Summary

Inspector Scientific Details

Inspector Provenance

partial interpretation

no evidence

integrity failure

mobile Inspector
```

---

# 156. Browser Matrix

必须：

```text
Chromium

Firefox

WebKit

Chromium 390x844
```

---

# 157. Browser Requirements

必须：

```text
console errors = 0

page errors = 0

unexpected failed requests = 0

unapproved external requests = 0

horizontal overflow = 0

claim/evidence identity mismatch = 0

scientific payload mutation = 0
```

---

# 158. Browser Trust-Path Test

至少自动执行：

```text
select Finding

→ inspect evidence

→ inspect source Artifact

→ inspect provenance

→ return to Finding
```

并验证 context retained。

---

# 159. Exact Identity Test

必须验证：

```text
Finding claimId exact

Evidence evidenceId exact

Artifact exact version/checksum

Tool exact ID/version

source identity exact
```

---

# 160. No Fuzzy Link Test

必须 adversarial验证：

```text
same display title

duplicate human labels

different Artifact versions

same Tool name different version

same numeric value from different source
```

不会错误绑定。

---

# 161. Scientific Payload Non-Change

before/after比较：

```text
ScientificEvidenceBundle semantic identity

ScientificClaim semantic identity

interpretation semantic identity

evidence membership

Artifact identity

Artifact scientific values
```

要求：

```text
SEMANTIC_DIFF = 0
```

---

# 162. No Reinterpretation Test

浏览：

```text
Finding
Evidence
Inspector
Provenance
```

必须：

```text
new interpretation rows = 0

new claims = 0

new evidence bundles = 0

new provider calls = 0
```

---

# 163. No Execution Growth

浏览 trust path：

必须：

```text
new Plan = 0

new Job = 0

new ToolCall = 0

new Artifact = 0

new queue message = 0
```

---

# 164. Interaction Baseline

与 12-0 baseline比较：

```text
steps Finding→Evidence

steps Finding→Provenance

number of exposed raw IDs
on default Finding surface

number of layers to exact developer detail

mobile trust-path steps
```

不得声称 human time-on-task。

---

# 165. Backend Regression

运行：

```text
uv run python -m pytest -q
```

要求：

```text
>= Phase 12-3 final canonical backend floor
```

当前已知：

```text
1298 passed
```

但必须动态读取最新 canonical floor。

---

# 166. Frontend Regression

运行：

```text
npm --prefix apps/web test
```

要求：

```text
>= Phase 12-3 final canonical frontend floor
```

当前已知：

```text
451 passed
```

新增 focused tests通常应增加 count。

---

# 167. Typecheck

必须：

```text
npm --prefix apps/web run typecheck
= PASS
```

---

# 168. Build

必须：

```text
npm --prefix apps/web run build
= PASS
```

---

# 169. Lock

必须：

```text
uv lock --check = PASS

LOCKFILE_CHANGES = 0
```

---

# 170. Diff

必须：

```text
git diff --check = PASS
```

---

# 171. Service-Backed Regression

Implementation exact-SHA CI必须继续：

```text
PostgreSQL

Redis

MinIO
```

PASS。

---

# 172. Service Evidence Purpose

这些只验证：

```text
persistence

identity

scope

retrieval

lineage
```

不等于：

```text
scientific validation
```

---

# 173. Linux / Windows Replay

必须继续 retained：

```text
Linux PASS

Windows PASS
```

如果 current CI matrix仍要求。

---

# 174. Phase 11 Integrity Gate

必须确认：

```text
Registry = 62

DataProfile = 2.4

golden benchmark identity unchanged

validation levels unchanged

references unchanged

tolerances unchanged

V4 = 0
```

---

# 175. npm Audit

如果 mirror仍：

```text
404_NOT_IMPLEMENTED
```

必须：

```text
npm audit = UNAVAILABLE
```

不能写：

```text
clean
```

---

# 176. Phase 12-5 Handoff

必须生成：

```text
Phase12_5ReportRecipeUXHandoff
```

至少包含：

```text
DS2 version/hash

Global shell state

Workspace IA state

Findings hierarchy

Evidence trust path

Inspector architecture

Provenance architecture

Report source entry points

existing Report authority

existing Recipe authority

mandatory limitations behavior

remaining 12-5 UX problem IDs

mobile constraints

accessibility constraints

Phase 11 scientific authority refs

browser evidence refs
```

---

# 177. Do Not Implement 12-5

禁止开始：

```text
Report Builder redesign

Report source workflow redesign

Recipe human-readable redesign

Report history redesign

export workflow redesign
```

---

# 178. Queue Admission

Entry PASS 后：

只创建：

```text
Phase 12-4
```

一个 task block。

要求：

```text
TASK_BLOCK_COUNT = 1

ACTIVE_TASK = Phase 12-4

PHASE_12_5_EXECUTABLE_TASK_CREATED = NO

PHASE_13_EXECUTABLE_TASK_CREATED = NO
```

---

# 179. Persistent State

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

不能改 scientific facts。

---

# 180. ROADMAP

Phase 12-4 success：

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
COMPLETE

Phase 12-4:
COMPLETE /
FINDINGS_EVIDENCE_INSPECTOR_PROVENANCE_EXPERIENCE_IMPLEMENTED

Phase 12-5:
REVIEWER_GATE /
AWAITING REVIEWER PROMPT

Phase 13:
ROADMAP_APPROVED /
NOT_QUEUED
```

---

# 181. First Required Output

执行器开始后第一组必须输出：

```text
Phase 12-4 Entry Gate
+ Phase 12-3 Findings/Evidence Handoff
+ Trust-Path UX Admission
```

至少确认：

1. current HEAD；
2. origin/master；
3. branch；
4. worktree clean；
5. Phase 12-3 implementation SHA；
6. implementation CI；
7. completion SHA；
8. archive SHA；
9. TASK_BLOCK_COUNT=0；
10. Phase 12-5 task absent；
11. Phase 13 task absent；
12. DS2 version/hash；
13. Phase 12-4 handoff resolves；
14. Workspace IA resolves；
15. Findings destination resolves；
16. Evidence destination resolves；
17. Inspector entry point resolves；
18. Provenance destination resolves；
19. ScientificEvidenceBundle contract/version；
20. ScientificClaim contract/version；
21. interpretation contract/version；
22. claim types；
23. confidence/qualification vocabulary；
24. evidence membership semantics；
25. recommendation non-execution boundary；
26. exact 12-4 UX problem IDs；
27. exact problem count；
28. exact P12X4-A01..A08 descriptions；
29. current interpretation APIs；
30. current evidence APIs；
31. Artifact/lineage retrieval authority；
32. no new backend capability required；
33. no migration required；
34. no dependency required；
35. no scientific/interpretation change required；
36. no LLM required。

成功：

```text
PHASE_12_4_ENTRY_GATE = PASS

PHASE_12_3_DEPENDENCY = VERIFIED

PHASE_11_SCIENTIFIC_AUTHORITY =
VERIFIED_READ_ONLY

PHASE_12_4_QUEUE_ADMISSION =
AUTHORIZED

PHASE_12_4_FINDINGS_PRESENTATION_AUTHORITY =
AUTHORIZED

PHASE_12_4_EVIDENCE_PRESENTATION_AUTHORITY =
AUTHORIZED

PHASE_12_4_INSPECTOR_PRESENTATION_AUTHORITY =
AUTHORIZED

PHASE_12_4_PROVENANCE_PRESENTATION_AUTHORITY =
AUTHORIZED

PHASE_12_4_INTERPRETATION_SEMANTIC_CHANGE_AUTHORITY =
NONE

PHASE_12_4_EVIDENCE_SEMANTIC_CHANGE_AUTHORITY =
NONE

PHASE_12_4_SCIENTIFIC_CHANGE_AUTHORITY =
NONE

PHASE_12_4_BACKEND_CHANGE_AUTHORITY =
NONE

PHASE_12_4_READINESS =
READY_FOR_FINDINGS_EVIDENCE_INSPECTOR_PROVENANCE_UX
```

---

# 182. Required Execution Sequence

严格：

```text
verify Phase 12-3 lifecycle

→ verify DS2

→ verify Phase 11 authority

→ load Phase 12-4 handoff

→ load exact UX-004/current owned problem set

→ load exact P12X4 acceptance IDs

→ audit live interpretation/evidence APIs/contracts

→ admit exactly one 12-4 task

→ snapshot current Findings UX

→ snapshot current Evidence UX

→ snapshot current Inspector UX

→ snapshot current Provenance UX

→ capture before evidence

→ implement Finding hierarchy

→ implement claim type / qualification presentation

→ implement limitation/warning prominence

→ implement Finding → Evidence exact trust path

→ implement Evidence detail hierarchy

→ implement supporting/limiting/contradicting role presentation

→ implement Evidence → Artifact exact source navigation

→ implement three-layer Inspector

→ implement Summary layer

→ implement Scientific Details layer

→ implement Provenance layer

→ subordinate Developer Details

→ implement exact provenance chain presentation

→ implement Plan 0.1 legacy provenance

→ implement Plan 0.2 dependency provenance

→ integrate canonical Claim/Evidence selection where formally supported

→ implement partial/no-evidence/integrity/stale states

→ preserve recommendation non-execution

→ preserve Report/Recipe boundary

→ implement mobile Findings/Evidence/Inspector

→ validate keyboard/focus/zoom/touch/reduced motion

→ close exact 12-4-owned UX problems

→ keep 12-5/6/7 problems typed/open

→ generate Phase 12-5 handoff

→ capture after evidence

→ run Finding/Evidence exact-identity tests

→ run scientific wording audit

→ run no-reinterpretation audit

→ run no-scientific-change audit

→ run interpretation-contract non-change audit

→ run frontend/backend regression

→ run browser matrix

→ run service-backed regression

→ run Linux/Windows retained replay

→ run Phase 11 integrity

→ run security/secret/evidence manifest checks

→ create implementation commit

→ push

→ WAIT FOR IMPLEMENTATION EXACT-SHA CI

→ if PASS:
   append Phase 12-4 completion record

→ commit/push completion directly

→ remove only Phase 12-4 task

→ commit/push archive directly

→ verify queue empty

→ stop
```

---

# 183. Implementation Commit Allowed

可包含：

```text
Findings frontend

Evidence frontend

Inspector frontend

Provenance frontend

presentation adapters

selection integration

DS2 styling

accessibility changes

frontend tests

browser evidence tooling

documentation

persistent state

TASKS admission
```

---

# 184. Implementation Commit Forbidden

不得包含：

```text
new scientific Tool

new scientific algorithm

new claim contract

new Evidence contract

new interpretation contract

grounding validator changes

new Artifact family

Workspace authority change

Selection contract change

new DB migration

new public backend capability family

new LLM provider/call site

Report/Recipe redesign

Phase 12-5 implementation

completion result
```

---

# 185. Interpretation Bug Rule

如果发现 current interpretation contract/grounding本身存在 scientific defect：

不要在 12-4“顺便修”。

必须：

```text
BLOCKED /
SCIENTIFIC_INTERPRETATION_DEFECT_REVIEW_REQUIRED
```

这是 UX phase，不是 science correction phase。

---

# 186. Implementation Exact-SHA CI

push implementation 后：

必须：

```text
WAIT FOR IMPLEMENTATION EXACT-SHA CI
```

required jobs全部：

```text
success
```

---

# 187. Minimum Implementation CI

至少：

```text
Backend Unit

Frontend Tests

Typecheck

Build

Phase 12-4 focused evidence

Chromium

Firefox

WebKit

390x844

PostgreSQL/Redis/MinIO

Linux scientific replay

Windows scientific replay

Phase 11 authority integrity

Phase 12 evidence integrity

security / secret scan
```

---

# 188. Failed Candidate

任何 CI failure：

保存：

```text
failed SHA

CI run

failed job

root cause
```

然后 fix-forward。

禁止：

```text
force push

rewrite history

delete test

reduce evidence cases

disable browser

disable mobile

remove exact identity checks

weaken scientific wording

change claim/evidence contract

move UX problem ownership
```

---

# 189. Completion Record

只有 implementation exact-SHA CI PASS：

才向：

```text
results.md
```

append：

```text
Phase 12-4 Findings / Evidence /
Inspector / Provenance Experience Result
```

然后：

```text
commit
push
```

按当前 lifecycle：

```text
DO NOT WAIT
for completion-record CI
```

---

# 190. Queue Archive

completion push 后：

删除且只删除：

```text
Phase 12-4 TASK block
```

不得创建：

```text
Phase 12-5 executable task
```

然后：

```text
commit
push
```

不等待 archive CI。

---

# 191. Lifecycle Terminology

最终只能：

```text
IMPLEMENTATION_VERIFIED_BY_EXACT_SHA_CI

COMPLETION_RECORDED

QUEUE_ARCHIVED
```

除非 completion/archive真的另有 exact-SHA CI。

---

# 192. Mandatory Result Markers

必须：

```text
PHASE12_4_PRODUCTION_UI_CHANGES =
YES_FINDINGS_EVIDENCE_INSPECTOR_PROVENANCE_PRESENTATION

PHASE12_4_BACKEND_BEHAVIOR_CHANGES = 0

PHASE12_4_SCIENTIFIC_BEHAVIOR_CHANGES = 0

PHASE12_4_INTERPRETATION_SEMANTIC_CHANGES = 0

PHASE12_4_SCIENTIFIC_CLAIM_CONTRACT_CHANGES = 0

PHASE12_4_EVIDENCE_CONTRACT_CHANGES = 0

PHASE12_4_GROUNDING_VALIDATOR_CHANGES = 0

PHASE12_4_ARTIFACT_CONTRACT_CHANGES = 0

PHASE12_4_WORKSPACE_AUTHORITY_CHANGES = 0

PHASE12_4_SELECTION_CONTRACT_CHANGES = 0

PHASE12_4_REPORT_AUTHORITY_CHANGES = 0

PHASE12_4_RECIPE_AUTHORITY_CHANGES = 0

PHASE12_4_NEW_SCIENTIFIC_TOOLS = 0

PHASE12_4_NEW_SCIENTIFIC_ALGORITHMS = 0

PHASE12_4_NEW_ARTIFACT_FAMILIES = 0

PHASE12_4_NEW_DATAPROFILE_VERSION = 0

PHASE12_4_NEW_ANALYSISPLAN_VERSION = 0

PHASE12_4_NEW_DATABASE_MIGRATIONS = 0

PHASE12_4_NEW_PUBLIC_API_FAMILIES = 0

PHASE12_4_NEW_DEPENDENCIES = 0

PHASE12_4_LOCKFILE_CHANGES = 0

PHASE12_4_NEW_LLM_CALL_SITES = 0

PHASE12_4_REAL_LLM_CALLS = 0

PHASE12_4_FRONTEND_SCIENTIFIC_RECOMPUTATION = 0
```

---

# 193. Trust-Path Markers

必须：

```text
FINDING_TO_EVIDENCE_EXACT_LINKING = PASS

EVIDENCE_TO_ARTIFACT_EXACT_LINKING = PASS

ARTIFACT_TO_TOOL_VERSION_TRACEABILITY = PASS

INPUT_IDENTITY_TRACEABILITY = PASS

PROVENANCE_TRACEABILITY = PASS

FUZZY_FINDING_EVIDENCE_LINKING = 0

DISPLAY_LABEL_PROVENANCE_AUTHORITY = 0

ARRAY_POSITION_PROVENANCE_AUTHORITY = 0
```

---

# 194. Inspector Markers

必须：

```text
INSPECTOR_SUMMARY_LAYER = PASS

INSPECTOR_SCIENTIFIC_DETAILS_LAYER = PASS

INSPECTOR_PROVENANCE_LAYER = PASS

DEVELOPER_DETAILS_AVAILABLE = YES

RAW_JSON_DEFAULT_PRIMARY_LAYER = NO

INSPECTOR_SCIENTIFIC_RECOMPUTATION = 0
```

---

# 195. Scientific Honesty Markers

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

# 196. Recommendation Markers

必须：

```text
RECOMMENDATION_EXECUTION_AUTHORITY = NONE

RECOMMENDATION_AUTO_PLAN = 0

RECOMMENDATION_AUTO_JOB = 0

RECOMMENDATION_AUTO_QUEUE = 0
```

---

# 197. Baseline Markers

必须：

```text
REGISTRY_BEFORE_12_4 = 62
REGISTRY_AFTER_12_4 = 62

DATAPROFILE_BEFORE_12_4 = 2.4
DATAPROFILE_AFTER_12_4 = 2.4

MIGRATION_BEFORE_12_4 =
0007_phase10m1_workspace_domain

MIGRATION_AFTER_12_4 =
0007_phase10m1_workspace_domain
```

---

# 198. UX Problem Markers

必须：

```text
PHASE12_4_OWNED_PROBLEMS =
<exact repository IDs>

PHASE12_4_OWNED_PROBLEM_COUNT =
<actual>

PHASE12_4_OWNED_PROBLEMS_CLOSED =
<same>

PHASE12_4_OWNED_PROBLEMS_OPEN = 0

NEW_P0_INTRODUCED_BY_12_4 = 0

NEW_P1_INTRODUCED_BY_12_4 = 0
```

---

# 199. Acceptance Marker

必须：

```text
P12X4_ACCEPTANCE = 8/8
```

exact descriptions来自 canonical acceptance plan。

---

# 200. Accessibility Markers

必须：

```text
FINDINGS_KEYBOARD = PASS

EVIDENCE_KEYBOARD = PASS

INSPECTOR_KEYBOARD = PASS

INSPECTOR_FOCUS_RESTORE = PASS

FINDING_STATUS_NON_COLOR = PASS

EVIDENCE_ROLE_NON_COLOR = PASS

MOBILE_TOUCH_TARGETS = PASS

REDUCED_MOTION = PASS
```

但：

```text
FULL_PRODUCT_ACCESSIBILITY_COMPLETE = NO
```

---

# 201. Required results.md Structure

至少：

# Phase 12-4 Findings / Evidence / Inspector / Provenance Experience Result

1. Conclusion
2. Phase 12-3 Baseline
3. Entry Gate
4. Repository State
5. Design System Authority
6. Phase 11 Scientific Authority
7. Phase 12-4 Handoff Integrity
8. UX Problem Ownership
9. Production Behavior Changes
10. Scientific Interpretation Authority
11. Scientific Claim Contract
12. Evidence Bundle Contract
13. Finding Information Hierarchy
14. Claim Type Presentation
15. Qualification / Confidence Presentation
16. Observation / Comparison Presentation
17. Warning Presentation
18. Limitation Presentation
19. Recommendation Presentation
20. No Supported Conclusion
21. Partial Interpretation
22. No Supported Evidence
23. Source Integrity Failure
24. Finding → Evidence Trust Path
25. Evidence Membership
26. Supporting Evidence
27. Limiting Evidence
28. Contradicting Evidence
29. Evidence Fact Presentation
30. Numeric / Unit Presentation
31. Evidence Source Artifact
32. Source Result Navigation
33. Selection Integration
34. Finding Selection Identity
35. Evidence Selection Identity
36. Cross-Panel Navigation
37. Inspector Architecture
38. Inspector Summary
39. Inspector Scientific Details
40. Inspector Provenance
41. Developer Details
42. Provenance Information Architecture
43. Data Source Provenance
44. Analysis Context Provenance
45. Tool / Version Provenance
46. Parameter Provenance
47. Execution Provenance
48. Artifact Provenance
49. Evidence / Claim Provenance
50. Lineage
51. AnalysisPlan 0.1 Legacy Provenance
52. AnalysisPlan 0.2 Dependency Provenance
53. Historical Compatibility
54. Stale / Missing Source
55. Cross-Scope Rejection
56. Scientific Wording Audit
57. Phase 11 Validation/Coverage Presentation
58. Report Boundary
59. Recipe Boundary
60. Workspace Boundary
61. Viewer Boundary
62. Loading UX
63. Error / Recovery UX
64. Desktop 1440x900
65. Desktop 1280x720
66. Mobile 390x844
67. 200% Zoom
68. Keyboard / Focus
69. Reduced Motion
70. Accessibility Foundation
71. Browser Matrix
72. Trust-Path Browser Replay
73. Interaction Baseline Comparison
74. Scientific Payload Non-Change
75. Interpretation Contract Non-Change
76. No-Reinterpretation Audit
77. No-Execution-Growth Audit
78. Security
79. LLM / DeepSeek
80. Database/API/Dependency Freeze
81. Registry/DataProfile Freeze
82. Phase 12-4 Problem Closure
83. Deferred UX Problems
84. Phase 12-5 Handoff
85. Backend Regression
86. Frontend Regression
87. Typecheck
88. Build
89. Service Regression
90. Linux/Windows Replay
91. npm Audit
92. Evidence Inventory
93. Evidence Manifest
94. Files Changed
95. Acceptance Registry
96. Implementation Commit
97. Implementation CI
98. Failed Candidates
99. Completion Record
100. Queue Archive
101. Queue State
102. Phase 12-5 Reviewer Gate
103. Final Repository State

---

# 202. PASS Gate

只有全部满足：

```text
Phase 12-3 PASS

Phase 12-3 implementation exact-SHA CI PASS

Phase 12-3 queue archived


HEAD == origin/master at entry

worktree clean

TASK_BLOCK_COUNT = 0


Phase 12-4 handoff resolves

exact owner problem set resolves

exact P12X4 acceptance set resolves


DS2 authority resolves

Phase 11 scientific authority resolves

Registry = 62

DataProfile = 2.4

migration = 0007


ScientificEvidenceBundle unchanged

ScientificClaim unchanged

GroundedInterpretation unchanged

grounding semantics unchanged


Finding hierarchy implemented

claim types clear

qualification clear

limitations first-class

recommendations non-executable

NO_SUPPORTED_CONCLUSION handled

partial interpretation handled

no-supported-evidence handled


Finding → Evidence exact

Evidence → Artifact exact

Artifact → Tool/version exact

input identity traceable

provenance traceable

fuzzy linking = 0


Inspector Summary implemented

Scientific Details implemented

Provenance implemented

Developer Details retained

raw JSON not primary


legacy Plan 0.1 provenance honest

Plan 0.2 lineage exact

no invented dependency


no scientific recomputation

no reinterpretation

no new claims

no new evidence

no provider call

no Plan/Job/ToolCall/Artifact growth
from trust-path browsing


12-4-owned UX problems closed

new P0 = 0

new P1 = 0


12-5/12-6/12-7 problems remain owned


no Tool

no algorithm

no Artifact family

no DataProfile version

no AnalysisPlan version

no migration

no new public API family

no dependency

no lock change

no new LLM call site

real LLM calls = 0


keyboard PASS

focus PASS

non-color state PASS

touch target PASS

reduced motion PASS


Chromium PASS

Firefox PASS

WebKit PASS

390x844 PASS


backend >= dynamic 12-3 floor

frontend >= dynamic 12-3 floor

typecheck PASS

build PASS

lock PASS

diff PASS

PostgreSQL/Redis/MinIO PASS

retained Linux replay PASS

retained Windows replay PASS

Phase 11 integrity PASS

evidence integrity PASS

security PASS

secret scan PASS


P12X4 = 8/8


implementation exact-SHA CI PASS

completion record committed/pushed

queue archive committed/pushed


TASK_BLOCK_COUNT = 0

Phase 12-5 task absent

Phase 13 task absent

HEAD == origin/master

worktree clean
```

才允许：

```text
Phase 12-4 = PASS
```

---

# 203. BLOCKED — Scientific Interpretation Changed

如果 UX implementation需要修改：

```text
claim predicate

claim confidence

evidence membership

numeric grounding

unit grounding

entity grounding

grounding validator
```

必须：

```text
BLOCKED /
SCIENTIFIC_INTERPRETATION_AUTHORITY_CHANGE_REQUIRED
```

---

# 204. BLOCKED — Finding Generated Frontend

如果 frontend：

```text
reads Artifact
→ generates new Finding
```

必须 BLOCKED。

---

# 205. BLOCKED — Evidence Generated Frontend

如果 frontend：

```text
derives new numeric Evidence
```

必须 BLOCKED。

---

# 206. BLOCKED — Fuzzy Trust Path

如果 Finding→Evidence或Evidence→Artifact使用：

```text
title matching

nearest match

latest

array position

same displayed value
```

不能 PASS。

---

# 207. BLOCKED — Limitation Hidden

如果 redesign：

让 scientific limitation：

```text
disappear
```

或只存在：

```text
raw developer JSON
```

必须：

```text
BLOCKED /
SCIENTIFIC_UX_MISREPRESENTATION
```

---

# 208. BLOCKED — Recommendation Executes

如果 Recommendation：

能够绕开 Planner直接：

```text
create Plan
create Job
enqueue
execute Tool
```

必须 BLOCKED。

---

# 209. BLOCKED — Raw JSON Still Primary

如果最终用户必须先阅读 raw JSON：

才能理解 Finding / Evidence / Provenance：

12-4核心目标没有完成。

不能 PASS。

---

# 210. BLOCKED — Provenance Loses Exact Identity

如果 human-readable redesign导致：

```text
Tool version hidden entirely

Artifact exact version unavailable

checksum unavailable

source identity unavailable
```

不能 PASS。

---

# 211. BLOCKED — Owned UX Problem Remains

如果：

```text
PHASE12_4_OWNED_PROBLEMS_OPEN > 0
```

不能 PASS。

---

# 212. Non-Blockers

以下允许继续：

```text
Phase 12-5 Report/Recipe UX debt

Phase 12-6 full responsive/mobile/accessibility debt

Phase 12-7 final consistency debt

V4 = 0

reference-limited scientific validation

unsupported file formats

unsupported interpretation contracts

historical jobs with no interpretation

Future Scope
```

只要诚实呈现。

---

# 213. Final Successful State

成功后：

```text
Phase 12-4:
PASS /
FINDINGS_EVIDENCE_TRUST_PATH_IMPLEMENTED /
INSPECTOR_PROVENANCE_EXPERIENCE_UNIFIED /
QUEUE_ARCHIVED

Phase 12:
IN_PROGRESS /
SCIENTIFIC_TRUST_AND_EXPLAINABILITY_EXPERIENCE_COMPLETE

Phase 12-5:
REVIEWER_GATE /
AWAITING REVIEWER PROMPT

Phase 13:
ROADMAP_APPROVED /
NOT_QUEUED /
NOT_EXECUTABLE

TASK_BLOCK_COUNT = 0

PHASE_12_5_EXECUTABLE_TASK_CREATED = NO

PHASE_13_EXECUTABLE_TASK_CREATED = NO
```

---

# 214. What Completion Means

可以说：

```text
The product now exposes a coherent scientific trust path
from human-readable findings through exact supporting,
limiting and contradicting evidence to persisted Artifact,
Tool/version, input identity and lineage provenance.

The Inspector now provides progressive Summary,
Scientific Details and Provenance layers while retaining
exact developer/audit information without creating new
scientific authority.
```

---

# 215. What Completion Does NOT Mean

不能说：

```text
Scientific interpretation was upgraded.

Every claim is reference validated.

Evidence proves scientific truth.

Report/Recipe redesign is complete.

Full accessibility is complete.

Phase 12 is complete.

The product is release-ready.
```

---

# 216. Phase 12-5 Gate

最终必须：

```text
Phase 12-5:
REVIEWER_GATE /
AWAITING REVIEWER PROMPT

PHASE_12_5_EXECUTABLE_TASK_CREATED = NO
```

---

# 217. Stop Rule

完成后立即停止。

不得：

```text
redesign Report Builder

redesign Recipe

perform full mobile/accessibility closure

perform Phase 12-7 final UX closure

start Phase 13
```

返回 reviewer：

```text
Phase 12-4 result

implementation SHA

implementation exact-SHA CI

completion SHA

archive SHA

exact 12-4 UX problem closure

P12X4 8/8

Finding hierarchy summary

Finding→Evidence→Artifact→Tool/input
trust-path proof

Inspector 3-layer implementation

provenance / lineage proof

scientific interpretation non-change proof

no-reinterpretation proof

recommendation non-execution proof

browser/mobile/accessibility evidence

remaining UX problem ownership

Phase 12-5 handoff state
```

然后等待 reviewer。


完成时间：2026-08-10 18:48:27 +08:00

修改文件：`apps/web/app/components/workspace/ScientificWorkspaceShell.tsx`、`workspace-selection-runtime.ts`、相关测试与浏览器证据脚本、`docs/phase12/`、`persistent/`、阶段治理测试和 `results.md`。

修改摘要：完成 persisted Finding 到 exact Evidence、source Artifact、Tool/version、Plan/Job 和输入 identity 的可信路径；实现 Summary / Scientific details / Provenance 三层 Inspector；保持推荐不可执行、科学 authority 和 contracts 不变；关闭 `UX-004`，验收 `P12X4-A01` 至 `P12X4-A08`。

测试结果：后端 `1301 passed`；前端 `453 passed`；typecheck、production build、`uv lock --check`、`git diff --check`、62 项阶段治理/证据测试、Chromium/Firefox/WebKit/390x844、48 项 PostgreSQL/Redis/MinIO（0 skipped/failed/errors）均通过。Implementation `9fac62bbb2cc9069da62370ee9d02cf3150e987a` 经 exact-SHA CI `31379672528` 验证成功。


---END---


---TASK---
 状态：待处理

# Phase 12-5 Reviewer Prompt

# Report + Recipe Experience

你现在执行：

# Phase 12-5：Report / Recipe Experience

中文：

# 科学报告 + 可复现 Recipe 核心体验重构

本阶段属于：

```text
Phase 12:
Comprehensive UI / UX
Product Experience Redesign
```

当前序列：

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
= COMPLETE

12-3
Scientific Workspace
+ Scientific Viewer Experience
= COMPLETE

12-4
Findings / Evidence /
Inspector / Provenance Experience
= MUST BE VERIFIED AT ENTRY

12-5
Report / Recipe Experience
= CURRENT AUTHORIZED PHASE

12-6
Responsive / Mobile /
Accessibility Closure

12-7
Cross-Product UX Validation
+ Design Evidence Closure
```

---

# 0. Mission

Phase 12-5 的任务不是创建新的 Report science。

不是重新设计 Report/Recipe 数据合同。

不是让 Recipe 变成 workflow engine。

本阶段目标是把已经存在的：

```text
Workspace
Results
Findings
Evidence
Provenance
Report composition authority
Recipe replay authority
Report history
Export authority
```

组织为一条清楚、专业、可审计的产品体验：

```text
Discover trustworthy sources

→ understand what can enter the Report

→ select exact sources

→ compose and order sections

→ preserve scientific warnings / limitations

→ preview the deterministic Report

→ finalize an immutable Report + paired Recipe

→ inspect exact reproducibility information

→ reopen historical Reports

→ export through existing safe formats
```

核心：

```text
REPORT_IS_COMPOSITION_OF_PERSISTED_FACTS = YES

RECIPE_IS_DECLARATIVE_REPRODUCIBILITY_RECORD = YES

RECIPE_EXECUTION_AUTHORITY = NONE
```

---

# 1. Fundamental Boundary

必须：

```text
REPORT_UX_REDESIGN
!=
REPORT_AUTHORITY_REDESIGN
```

以及：

```text
RECIPE_UX_REDESIGN
!=
RECIPE_EXECUTION
```

12-5 可以改变：

```text
Report information hierarchy

source discovery

source selection UX

composition layout

ordering UX

caption/disclosure presentation

preview presentation

finalization UX

history UX

export UX

Recipe human-readable presentation

Recipe raw-detail hierarchy

error / empty / loading states

responsive behavior

accessibility behavior
```

不能改变：

```text
ReportCompositionRequest semantics

ReportCompositionSnapshot semantics

RecipeReplayManifest semantics

ReportExportManifest semantics

Report persistence authority

Recipe persistence authority

source eligibility semantics

scientific values

Artifact identity

Finding/Evidence identity

Workspace identity

scientific warnings

scientific limitations

Plan/Tool/Artifact lineage

Recipe execution authority
```

---

# 2. Reviewer Authorization

正式条件预授权：

```text
PHASE_12_5_PROMPT_PREAUTHORIZED = YES

AUTHORIZED_PHASE = Phase 12-5

MAX_PHASES_EXECUTED = 1
```

只有 Entry Gate PASS 后：

才允许创建：

```text
one Phase 12-5 TASK block
```

禁止创建/执行：

```text
Phase 12-6
Phase 12-7
Phase 13
```

---

# 3. Mandatory Phase 12-4 Dependency

必须从真实 repository 动态读取：

```text
git history

results.md

TASKS.md

docs/ROADMAP.md

persistent/

docs/phase12/

docs/phase12/evidence/
```

取得：

```text
PHASE_12_4_IMPLEMENTATION_SHA

PHASE_12_4_IMPLEMENTATION_CI_RUN

PHASE_12_4_IMPLEMENTATION_CI_RESULT

PHASE_12_4_COMPLETION_SHA

PHASE_12_4_QUEUE_ARCHIVE_SHA
```

必须确认：

```text
Phase 12-4 = PASS

implementation exact-SHA CI = PASS

completion recorded

queue archived
```

否则：

```text
PHASE_12_5_ENTRY_GATE = BLOCKED

reason =
PHASE_12_4_NOT_COMPLETED_OR_NOT_ARCHIVED
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

Phase 12-5 task absent

Phase 12-6 task absent

Phase 13 task absent
```

---

# 5. Phase 12-5 Handoff

必须找到唯一 canonical：

```text
Phase12_5ReportRecipeUXHandoff
```

或 repository current equivalent。

至少读取：

```text
Design System version/hash

Global shell state

Workspace IA state

Findings hierarchy

Evidence trust path

Inspector architecture

Provenance architecture

Report source entry points

existing Report authority

existing Recipe authority

mandatory limitation behavior

remaining Phase 12-5 UX problem IDs

mobile constraints

accessibility constraints

Phase 11 scientific authority refs

browser evidence refs
```

handoff 缺失或不完整：

```text
BLOCKED /
PHASE_12_5_HANDOFF_INVALID
```

---

# 6. Canonical UX Problem

必须从：

```text
phase12_ux_problem_matrix
```

读取：

```text
owner = 12-5
```

的 exact IDs。

当前历史 baseline 预期包含：

```text
UX-005
```

但 repository current authority 优先。

必须读取该 row 的：

```text
severity

currentBehavior

userConsequence

scientificConsequence

targetOutcome

acceptanceMethod
```

不得根据 Prompt 重写定义。

---

# 7. Owned Problem Closure

最终：

```text
PHASE12_5_OWNED_PROBLEMS_OPEN = 0
```

禁止：

```text
reassign owner

lower severity

delete problem

rename canonical problem
```

逃避 closure。

---

# 8. Future Problems

12-6 / 12-7 owned UX problems：

继续：

```text
OPEN / OWNED
```

若 12-5 对其有基础改善：

记录：

```text
FOUNDATION_IMPROVED /
FINAL_CLOSURE_REMAINS_WITH_OWNER
```

---

# 9. Existing Report Authority

必须动态验证 current contract。

当前 sealed architecture至少：

```text
reports.report_json
=
Report persistence authority

visualization_recipes.recipe_json
=
Recipe persistence authority
```

不得创建第二套：

```text
frontendReport

localReport

temporaryCanonicalReport

latestRecipe
```

authority。

---

# 10. Existing Composition Contracts

必须读取 current exact versions。

当前 known authority：

```text
ReportCompositionRequest 1.0

ReportCompositionSnapshot 1.0

RecipeReplayManifest 1.0

ReportExportManifest 1.0
```

如果 repository current version不同：

使用 actual。

12-5 不修改 contract。

---

# 11. Report Definition

Report 必须继续被理解为：

```text
selected delivery snapshot
of persisted scientific facts
```

不是：

```text
new scientific analysis

new interpretation engine

LLM-generated paper

mutable notebook
```

---

# 12. Recipe Definition

Recipe 必须继续：

```text
exact
declarative
non-executable
reproducibility manifest
```

它记录：

```text
Project

Dataset/version

Profile

Intent

Eligibility

Decision

Plan

Tool IDs/versions

parameters

bindings

expected outputs

Artifact IDs/checksums

outcome

provenance

warnings/limitations

semantic hash
```

以 actual contract为准。

---

# 13. Recipe Permanent Boundary

必须：

```text
RECIPE_EXECUTION_AUTHORITY = NONE
```

禁止增加：

```text
Run Recipe

Replay Recipe

Execute

Rerun workflow

Create Job from Recipe automatically
```

---

# 14. Reproducibility Explanation

Recipe default UI 应首先回答：

```text
What analysis was performed?

On which exact data?

With which methods/tools?

With which important parameters?

What dependencies existed?

Which outputs were produced?

What warnings/limitations applied?

Which exact Artifact results correspond?
```

而不是默认 raw JSON。

---

# 15. Exact Declaration Remains Available

必须：

```text
RECIPE_RAW_DECLARATION_ACCESSIBLE = YES
```

通过：

```text
Scientific Details
Provenance
Developer Details
Exact Recipe
```

等 current hierarchy。

---

# 16. Recipe Human-Readable Layer Is Projection Only

human-readable Recipe：

只能 deterministic presentation 已持久化 fields。

禁止：

```text
LLM summarize Recipe

infer missing method

infer parameter

infer dependency

invent rationale
```

---

# 17. AnalysisPlan 0.1 Recipe

对于：

```text
planSchemaVersion = 0.1
```

必须保持：

```text
ordered independent/sequential steps
```

禁止 UI invent：

```text
dependency graph

Artifact binding
```

---

# 18. AnalysisPlan 0.2 Recipe

对于 Plan 0.2：

可 human-readable 呈现 exact：

```text
dependency edges

producer / consumer

ports

bindings

Artifact contract/version/checksum
```

但不能重新推断 dependency。

---

# 19. Report Mandatory Scientific Scope

必须读取 current Report contract。

当前 existing Report composition拥有固定 mandatory scientific sections。

至少 current authority包含 equivalent：

```text
Title

Goal

Scope

Methods / Plan

Execution

Results

Findings

Warnings / Limitations

Failed / Blocked / Missing scope

Evidence / Provenance

Environment / References

Exact Recipe reference
```

不要为了更简洁的 UX 删除 mandatory scientific sections。

---

# 20. Empty Mandatory Section

如果某 mandatory section 没有可用内容：

必须：

```text
typed unavailable / not applicable state
```

不得：

```text
silently omit
```

导致 Report 看起来比实际更完整。

---

# 21. Report Information Hierarchy

默认优先：

```text
Title

Goal

Scope

Key Results

Findings

Warnings / Limitations

Evidence / Provenance

Methods / Execution

Reproducibility
```

实际 ordering 需服从 current contract允许的 composition semantics。

若 contract固定 12-section order：

UI不得破坏 semantic order。

---

# 22. Report Source Discovery Mission

用户必须能回答：

```text
What can I add?

Why is it eligible?

What will it contribute?

Which exact persisted source will be used?

What important limitation will travel with it?
```

---

# 23. Existing Source Eligibility Authority

必须复用 current deterministic source eligibility projector。

当前 known classes：

```text
REPORT_FIGURE_SOURCE

REPORT_TABLE_SOURCE

REPORT_FINDING_SOURCE

REPORT_EVIDENCE_SOURCE

REPORT_PROVENANCE_SOURCE

REPORT_DISCLOSURE_ONLY

REPORT_METADATA_ONLY

REPORT_UNSUPPORTED
```

实际 repository enums优先。

---

# 24. No Frontend Eligibility Inference

必须：

```text
FRONTEND_REPORT_SOURCE_ELIGIBILITY_RECOMPUTATION = 0
```

UI 只呈现 authoritative eligibility。

---

# 25. Forbidden Source Inference

严格禁止使用：

```text
filename

title

MIME only

array position

latest version

nearest version

fuzzy text match
```

判断 Report source。

---

# 26. Exact Report Sources

Report source必须绑定：

```text
exact Workspace revision

exact Panel

exact Artifact ID/version/checksum

exact Claim ID

exact Evidence ID

exact Provenance ref
```

按 source kind实际 contract。

---

# 27. Source Discovery UI

推荐按人类概念组织：

```text
Results

Findings

Evidence

Figures

Tables

Provenance

Disclosures
```

而不是：

```text
Artifact JSON objects
```

---

# 28. Source Eligibility Explanation

若 source不能加入：

不能只 disabled。

必须显示 typed reason，例如：

```text
unsupported source type

wrong scope

stale source

missing payload

ineligible interpretation

presentation-only source

metadata-only

disclosure-only
```

实际 reason来自 authority。

---

# 29. Whole Artifact Fallback

如果 viewer sub-selection 没有正式 Report authority：

可以按 current approved fallback使用：

```text
whole Artifact

Panel

metadata

approved numeric/text representation
```

不得 frontend创建新的 sub-selection authority。

---

# 30. WebGL Boundary

必须：

```text
WEBGL_CANVAS_REPORT_AUTHORITY = NONE
```

WebGL screenshot不能成为 scientific Report source authority。

---

# 31. Browser Screenshot Boundary

必须：

```text
BROWSER_SCREENSHOT_SCIENTIFIC_AUTHORITY = NONE
```

如果 current safe presentation export允许图片：

必须明确它是 presentation。

---

# 32. Static Figure Authority

若 backend/current Report contracts有正式：

```text
static figure projection
```

可以使用。

必须绑定 exact scientific source。

---

# 33. Table Authority

Report table必须来自：

```text
approved persisted numeric/table projection
```

不得 browser重新计算 summary。

---

# 34. Finding Source

Finding加入 Report：

必须保留：

```text
Claim type

qualification

warnings

limitations

supporting Evidence membership
```

不得只复制一句漂亮的 claim text。

---

# 35. Evidence Source

Evidence加入 Report：

必须保留 exact：

```text
subject

value

unit

source Artifact

role

provenance
```

按 current persisted contract。

---

# 36. Provenance Source

Provenance section：

必须来自 persisted lineage。

不能 UI重建一个推测 provenance chain。

---

# 37. Warnings / Limitations Are Mandatory

核心：

```text
REPORT_LIMITATION_PROPAGATION = REQUIRED
```

如果 selected source带：

```text
warning

scientific limitation

partial status

failed scope

blocked scope
```

Report不得通过 composition隐藏。

---

# 38. User Cannot Delete Mandatory Limitation

可以：

```text
move

collapse in UI

format
```

若 contract允许。

不能：

```text
remove

rewrite as success

omit from finalized Report
```

mandatory disclosure。

---

# 39. Partial Job Report

Report必须保留：

```text
successful outputs

failed steps

blocked dependencies

missing outputs

affected findings

limitations
```

不得形成：

```text
all analysis completed successfully
```

假象。

---

# 40. Report Composition Draft

现有 draft authority必须动态验证。

当前 known：

```text
REPORT_DRAFT_PERSISTENCE = SESSION_ONLY

REPORT_DRAFT_SERVER_WRITES = 0

REPORT_DRAFT_LOCALSTORAGE_WRITES = 0

REPORT_DRAFT_AUTOMATIC_FINALIZE = 0
```

12-5 必须保持，除非 repository已有 reviewer-approved change。

---

# 41. Draft Is Not Durable Authority

必须清楚告诉用户：

```text
unfinalized draft is session-only
```

如果 refresh/close 会丢失：

必须有明确 disclosure。

---

# 42. No Silent Draft Persistence

禁止：

```text
localStorage report draft

server autosave

hidden finalize

background report creation
```

若 current contracts没有这种 authority。

---

# 43. Navigation Protection

如果 session draft有未提交 changes：

允许使用现有安全：

```text
navigation/unload warning
```

不得自动 finalize来避免丢失。

---

# 44. Report Builder Mission

Report Builder 应回答：

```text
What is included?

What order will it appear in?

What is missing?

What warnings are mandatory?

What will be finalized?

Which Recipe will be paired?
```

---

# 45. Report Builder Is Not WYSIWYG

本阶段禁止扩成：

```text
rich-text editor

arbitrary HTML editor

word processor

notebook

freeform document editor
```

---

# 46. No Arbitrary Report Science Text

用户可编辑字段必须严格来自 current contract，例如：

```text
title

allowed captions

allowed bounded presentation fields
```

具体 actual contract优先。

不得增加：

```text
arbitrary scientific conclusion body
```

使未grounded文本看起来等同于 scientific finding。

---

# 47. Captions

若 current contract允许 caption：

caption必须：

```text
bounded

inert

non-executable
```

并明确：

```text
caption != scientific authority
```

---

# 48. User Caption Must Not Override Warning

caption不能覆盖、删除或 contradict mandatory limitation。

---

# 49. Ordering

如果 Report contract允许 source ordering：

UI提供明确 drag/reorder 或 accessible equivalent。

必须绑定 exact source IDs。

---

# 50. Ordering Does Not Change Provenance

改变 source presentation order：

不得改变：

```text
Artifact lineage

Claim evidence membership

Plan dependency
```

---

# 51. Accessible Reordering

若实现 drag：

必须同时提供：

```text
keyboard accessible reorder
```

或等价明确 controls。

---

# 52. Preview

Preview必须：

```text
deterministic
```

来自当前 session composition request / projection。

不能：

```text
LLM-generated preview

new science

browser-only unsupported projection
```

---

# 53. Preview ≠ Finalized Report

必须视觉区分：

```text
DRAFT PREVIEW
```

与：

```text
FINALIZED REPORT
```

---

# 54. Preview Must Show Mandatory Disclosures

不能等 finalize 后才突然出现 warnings/limitations。

preview就必须显示。

---

# 55. Preview Failure

如果某 source无法 preview：

必须 typed：

```text
presentation unavailable

source stale

source unsupported

source missing
```

但不要把整个 Report错误说成 scientific failure。

---

# 56. Finalization

Finalize必须是：

```text
explicit user action
```

不得自动触发。

---

# 57. Finalization Semantics

必须复用 current atomic authority。

当前 architecture：

```text
Report + exact paired Recipe
created atomically
```

实际 transaction semantics以 repository为准。

---

# 58. No Partial Finalization

如果 atomic creation失败：

不得出现：

```text
Report persisted
Recipe missing
```

或相反。

---

# 59. Finalize Confirmation

在 finalize 前：

应清楚展示：

```text
selected sources

mandatory disclosures

Report title/scope

Recipe pairing

immutability consequences
```

---

# 60. Immutable Finalized Report

finalized Report：

必须保持 current immutable/history semantics。

禁止直接：

```text
edit finalized Report in place
```

---

# 61. Create New Version Boundary

如果 current product支持新 Report creation：

通过正式 new composition。

不要修改历史 Report authority。

---

# 62. Historical Report

历史 Report必须：

```text
exact immutable snapshot
```

打开时不得：

```text
bind to latest Artifact

latest Finding

latest Recipe
```

---

# 63. Historical Recipe

paired Recipe：

必须打开 exact historical Recipe。

---

# 64. Semantic Hash

必须显示/可访问 current：

```text
Report semantic hash

Recipe semantic hash
```

在 provenance/developer detail。

默认不需要抢占主 UI。

---

# 65. History UX

Report history应该优先显示：

```text
title

scope

finalized status

created time if authoritative

source summary

warnings/limitations indicator

paired Recipe availability
```

developer detail再显示 hashes/IDs。

---

# 66. No “Latest” Scientific Rebinding

“Latest Report”仅可以是 navigation/list sorting concept。

不能让其内部 source重新绑定 latest science。

---

# 67. Export

必须读取 existing exact export authority。

当前 known：

```text
JSON

Markdown
```

以及 current `ReportExportManifest`。

实际 formats由 repository authority决定。

---

# 68. No New Mandatory Export Format

12-5 不增加：

```text
PDF

DOCX

LaTeX

PPTX
```

作为 required product capability。

如果 repository已经支持更多：

可以改善 existing UX。

---

# 69. Export Is Representation

Export：

不能重新计算 science。

必须：

```text
REPORT_EXPORT_SCIENTIFIC_RECOMPUTATION = 0
```

---

# 70. Export Manifest

必须能追踪：

```text
Report

Recipe

format

semantic identity

source identity
```

按 current contract。

---

# 71. Export Safety

禁止：

```text
executable HTML

JavaScript

notebook

shell

Python

macro-enabled document
```

---

# 72. Recipe UX Structure

默认 Recipe 建议三层：

```text
Reproducibility Summary

Exact Analysis Details

Raw Recipe / Developer Details
```

名称可根据 DS2/12-4 Inspector vocabulary协调。

---

# 73. Reproducibility Summary

优先显示：

```text
Data

Goal

Method

Key parameters

Execution structure

Outputs

Warnings / limitations
```

---

# 74. Exact Analysis Details

显示：

```text
Profile

Intent

Eligibility

Plan version

Tool IDs/versions

parameters

dependencies

Artifact bindings

checksums

environment/references
```

仅 actual applicable fields。

---

# 75. Raw Recipe

raw JSON必须：

```text
inert

copyable

bounded

accessible
```

但：

```text
RAW_RECIPE_DEFAULT_PRIMARY_UI = NO
```

---

# 76. Recipe Never Becomes “Run Again”

严格：

```text
RECIPE_RERUN_BUTTON = 0
```

除非未来 reviewer明确引入新的 Planner-mediated rerun product。

本阶段没有授权。

---

# 77. Recommendation Boundary

Report中出现 Recommendation：

必须继续：

```text
non-executable
```

不得：

```text
Run recommendation
```

直接产生 Job。

---

# 78. Findings / Evidence Boundary

12-4 已负责 trust path。

12-5只消费：

```text
Finding

Evidence

Provenance
```

作为 Report source。

不得重新设计 12-4 trust architecture。

---

# 79. Inspector Boundary

可以从 Report/Recipe打开：

```text
Inspector / Provenance
```

不得再重构 Inspector architecture。

---

# 80. Workspace Boundary

12-3已完成 Workspace IA。

12-5仅改：

```text
Report destination
```

及必要 source-entry affordances。

不得重构：

```text
Workspace navigation

Results

Viewer chrome
```

---

# 81. Planner Boundary

不得改：

```text
Intent

Clarification

Eligibility

Human Plan

Execution
```

---

# 82. Scientific Authority Freeze

继续：

```text
Registry = 62

DataProfile = 2.4

AnalysisIntent = 1.0

EligibilityResolution = 1.0

AnalysisPlan = 0.1 / 0.2

migration =
0007_phase10m1_workspace_domain
```

actual repository为准。

---

# 83. Phase 11 Honesty

继续保留 current final：

```text
12 golden records

8 PASS_INVARIANT

4 NOT_APPLICABLE

numeric cross-platform =
NOT_APPLICABLE

V4 = 0
```

---

# 84. Report Cannot Upgrade Science

禁止：

```text
selected for Report
→ scientifically validated
```

禁止：

```text
exported
→ verified
```

禁止：

```text
Recipe exists
→ reproducibility scientifically proven
```

---

# 85. Four Validation Axes

继续：

```text
Product Support
!=
Scientific Validation
!=
Cross-Platform Reproducibility
!=
Presentation Validation
```

---

# 86. Scientific Wording

Report不得通过 polished formatting升级 wording。

例如：

```text
estimated diffusion
```

不能变成：

```text
true diffusion coefficient
```

---

# 87. XRD

保持：

```text
peak correspondence under tolerance
```

不得：

```text
phase confirmed
```

---

# 88. Coordination

保持：

```text
algorithm-derived coordination
```

不得：

```text
true chemical bonds
```

---

# 89. Electronic

保持：

```text
analysis of supplied/imported electronic data
```

不得暗示：

```text
platform DFT/GW calculation
```

---

# 90. Report Does Not Call LLM

必须：

```text
PHASE12_5_NEW_LLM_CALL_SITES = 0

PHASE12_5_REAL_LLM_CALLS = 0

REPORT_LLM_WRITING_CALLS = 0
```

---

# 91. No Auto Captions From LLM

禁止调用 DeepSeek产生：

```text
caption

summary

abstract

conclusion

citation
```

---

# 92. Existing Persisted Grounded Interpretation

Report可以组成已有：

```text
persisted GroundedScientificInterpretation
```

不能重新生成它。

---

# 93. Frontend Scientific Recomputation

必须：

```text
PHASE12_5_FRONTEND_SCIENTIFIC_RECOMPUTATION = 0
```

包括：

```text
no new statistics

no chart-derived values

no unit conversion

no fit

no ranking
```

---

# 94. Database Freeze

必须：

```text
NEW_DATABASE_TABLES = 0

NEW_DATABASE_COLUMNS = 0

NEW_DATABASE_MIGRATIONS = 0
```

---

# 95. Existing Persistence Reuse

必须继续复用 existing Report/Recipe persistence。

如果 12-5目标需要新 table：

```text
BLOCKED /
PERSISTENCE_REDESIGN_REQUIRED
```

---

# 96. API Freeze

必须：

```text
NEW_PUBLIC_API_FAMILIES = 0
```

应复用 existing Report composition/read/history/export APIs。

---

# 97. Backend Behavior

默认：

```text
PHASE12_5_BACKEND_BEHAVIOR_CHANGES = 0
```

如果已有 API有真正 blocking bug：

可 fix-forward bug，

但不得改变 Report/Recipe authority semantics。

必须在结果中单独披露。

---

# 98. Dependency Freeze

必须：

```text
NEW_PYTHON_DEPENDENCIES = 0

NEW_FRONTEND_DEPENDENCIES = 0

LOCKFILE_CHANGES = 0
```

---

# 99. No Rich Text Dependency

禁止为了 Report Builder安装：

```text
TipTap

ProseMirror

Slate

Quill

Markdown editor framework
```

除非已是 repository dependency且 current contract需要。

---

# 100. No External Publishing

禁止：

```text
remote publishing service

Google Docs export

Notion export

external document API
```

---

# 101. Draft Security

caption/title/user text：

必须：

```text
inert
```

不得执行：

```text
HTML

JavaScript

iframe

module

Markdown HTML
```

---

# 102. Recipe Security

Raw Recipe content：

不得被当作：

```text
script

config-to-execute

URL-to-fetch
```

---

# 103. Artifact Safety

继续：

```text
Artifact = inert data
```

Report preview不能执行 Artifact内 HTML/JS。

---

# 104. Cross-Scope Safety

Report source必须属于 exact allowed scope。

必须：

```text
NO_CROSS_PROJECT_REPORT_SOURCE = PASS

NO_CROSS_JOB_REPORT_SOURCE = PASS
```

按 existing contract。

---

# 105. Stale Source

stale exact source：

必须 typed：

```text
STALE
```

不能自动绑定 latest。

---

# 106. Missing Source

missing Artifact/Finding/Evidence：

finalization必须依据 existing contract：

```text
reject
or
typed disclosure
```

不得 silent substitution。

---

# 107. Source Integrity Failure

checksum/lineage mismatch：

必须：

```text
SOURCE_INTEGRITY_FAILED
```

或 current typed equivalent。

不能 finalize看似正常的 scientific Report。

---

# 108. Historical Compatibility

必须覆盖：

```text
AnalysisPlan 0.1

AnalysisPlan 0.2

legacy Artifacts

legacy Reports

legacy Recipes

jobs without interpretation

partial jobs

stale dataset versions

missing Profile fields
```

只显示真实可用 information。

---

# 109. Mobile Scope

Phase 12-5必须使核心：

```text
source selection

ordering

preview

finalization

Report detail

Recipe detail
```

在：

```text
390x844
```

可用。

---

# 110. Mobile Report Pattern

继续 current sealed：

```text
single-surface Report workflow
```

不能把 desktop multi-column builder压缩到 mobile。

---

# 111. Full Mobile Closure

仍然：

```text
FULL_PRODUCT_MOBILE_CLOSURE = NO
```

12-6负责最终 closure。

---

# 112. Accessibility

12-5 new/reworked UI必须：

```text
semantic headings

keyboard source selection

keyboard reorder

visible focus

non-color state

dialog focus containment

status announcements

touch targets >= 44x44

200% zoom support

reduced motion
```

---

# 113. Full Accessibility Boundary

仍：

```text
FULL_PRODUCT_ACCESSIBILITY_COMPLETE = NO
```

---

# 114. Report Ordering Keyboard

若存在 reorder：

必须支持：

```text
Move up
Move down
```

或 equivalent accessible action。

不能只 drag-and-drop。

---

# 115. Finalize Focus

Finalize dialog关闭后：

focus必须合理返回。

---

# 116. Error UX

至少覆盖：

```text
no eligible sources

stale source

missing source

source integrity failure

invalid composition

mandatory disclosure failure

finalization failure

paired Recipe failure

export failure

historical Report unavailable
```

---

# 117. Error Structure

继续：

```text
What happened?

Why?

What can I do?

What draft/context was preserved?
```

---

# 118. Empty States

至少：

```text
no Report yet

empty session draft

no eligible sources

no historical Reports

Recipe unavailable for legacy record
```

---

# 119. Loading

区分：

```text
source catalog loading

preview loading

finalization

history loading

Report detail loading

Recipe detail loading

export generation
```

---

# 120. No Fake Finalization Progress

如果没有 authoritative percent：

使用 stage/indeterminate。

禁止：

```text
63% finalizing
```

凭空生成。

---

# 121. UX Problem Closure

必须关闭所有：

```text
owner = 12-5
```

的 exact UX problems。

当前 expected：

```text
UX-005
```

实际 repository优先。

---

# 122. New Regression Rule

必须：

```text
NEW_P0_INTRODUCED_BY_12_5 = 0

NEW_P1_INTRODUCED_BY_12_5 = 0
```

---

# 123. Acceptance IDs

必须从：

```text
docs/phase12/phase12_acceptance_and_test_plan.md
```

读取 exact：

```text
P12X5-A01
...
P12X5-A08
```

及 exact descriptions。

---

# 124. Acceptance IDs Immutable

必须：

```text
P12X5_EXPECTED = 8

IMPLEMENTED = 8

MISSING = 0

EXTRA = 0

DUPLICATE = 0

CONFLICTING = 0

SHORTHAND = 0
```

不得重写 canonical IDs。

---

# 125. Reviewer Interpretation of P12X5 Scope

repository exact wording优先。

至少 equivalent覆盖：

```text
A.
Report source discovery
and deterministic eligibility

B.
Exact source selection,
ordering and mandatory disclosures

C.
Report composition / draft /
preview experience

D.
Explicit atomic finalization
and immutable history

E.
Human-readable Recipe
plus exact raw manifest

F.
Export and historical recovery UX

G.
mobile / keyboard /
accessibility / security

H.
authority non-change /
browser / regression /
evidence / lifecycle closure
```

---

# 126. Evidence Directory

建立：

```text
docs/phase12/evidence/
phase12_5_report_recipe_experience/
```

至少：

```text
baseline.txt

entry_gate.md

phase12_4_handoff_snapshot.json

report_authority_matrix.json

recipe_authority_matrix.json

report_source_inventory.json

report_source_eligibility_matrix.json

source_identity_matrix.json

source_disclosure_matrix.json

draft_state_matrix.json

report_builder_matrix.json

report_ordering_matrix.json

caption_boundary_matrix.json

preview_matrix.json

finalization_matrix.json

atomic_report_recipe_matrix.json

report_history_matrix.json

recipe_human_readable_matrix.json

recipe_exact_manifest_matrix.json

plan01_recipe_matrix.json

plan02_recipe_matrix.json

warning_limitation_propagation.json

partial_failed_scope_matrix.json

export_matrix.json

historical_compatibility_matrix.json

stale_missing_source_matrix.json

mobile_report_matrix.json

mobile_recipe_matrix.json

accessibility_matrix.json

zoom_200_matrix.json

browser_matrix.json

before_after_surface_matrix.json

interaction_baseline_comparison.json

scientific_payload_nonchange.json

report_contract_nonchange.json

recipe_contract_nonchange.json

no_recipe_execution_audit.json

no_llm_report_writing_audit.json

phase12_5_problem_closure.json

deferred_problem_matrix.json

phase12_6_handoff.json

security.md

secret_scan.txt

manifest.json
```

---

# 127. Canonical Docs

至少新增/更新：

```text
docs/phase12/
phase12_5_report_recipe_experience.md

phase12_5_report_source_discovery.md

phase12_5_report_composition_and_preview.md

phase12_5_finalization_and_history.md

phase12_5_recipe_reproducibility_experience.md

phase12_5_export_and_recovery.md

phase12_5_responsive_accessibility.md

phase12_5_problem_closure.md

phase12_6_responsive_mobile_accessibility_handoff.md

phase12_5_completion.md
```

若现有 naming convention不同：

复用 canonical。

---

# 128. Canonical Cases

至少覆盖：

```text
Case A
new Report
with eligible result + finding + evidence

Case B
figure + table Report

Case C
Report with mandatory scientific limitation

Case D
partial Job Report

Case E
blocked / missing scope disclosure

Case F
unsupported Report source

Case G
stale source

Case H
preview then finalize

Case I
atomic Report + Recipe creation

Case J
historical finalized Report reopen

Case K
Plan 0.1 Recipe

Case L
Plan 0.2 Recipe with dependencies

Case M
JSON/Markdown export
or current actual formats

Case N
mobile Report workflow

Case O
injection / inert caption / raw Recipe
```

---

# 129. Before / After Evidence

至少：

```text
Report empty state

source discovery

source selected

ordering

mandatory warning

preview

finalize confirmation

finalized Report

history

Recipe summary

Recipe exact details

export

mobile source selection

mobile finalized Report
```

---

# 130. Viewports

至少：

```text
1440x900

1280x720

390x844
```

---

# 131. Browser Matrix

必须：

```text
Chromium

Firefox

WebKit

Chromium 390x844
```

---

# 132. Browser Requirements

必须：

```text
console errors = 0

page errors = 0

unapproved external requests = 0

unexpected horizontal overflow = 0

source identity mismatch = 0

mandatory disclosure loss = 0

scientific payload mutation = 0
```

---

# 133. Finalization Browser Replay

至少自动：

```text
open Workspace

→ Report

→ discover eligible source

→ add source

→ reorder if permitted

→ inspect warning/limitation

→ preview

→ finalize explicitly

→ verify Report

→ verify paired Recipe

→ reopen historical Report
```

---

# 134. No Hidden Writes Before Finalize

浏览/preview阶段：

必须：

```text
new finalized Report = 0

new Recipe = 0

new Plan = 0

new Job = 0

new ToolCall = 0

queue growth = 0
```

---

# 135. Finalize Growth

一次 successful explicit finalize：

必须产生 exact expected persistence growth。

不能 duplicate。

---

# 136. Idempotency / Double Click

必须测试：

```text
double click

repeated submit

slow response
```

不会创建 duplicate finalized pair，按 current API semantics。

---

# 137. Draft Persistence Test

验证：

```text
REPORT_DRAFT_SERVER_WRITES = 0

REPORT_DRAFT_LOCALSTORAGE_WRITES = 0
```

如果 current authority仍如此。

---

# 138. Recipe Non-Execution Test

浏览 Recipe：

必须：

```text
Plan growth = 0

Job growth = 0

ToolCall growth = 0

queue growth = 0

Adapter execution = 0
```

---

# 139. Scientific Payload Non-Change

before/after比较：

```text
selected Artifact IDs

Finding IDs

Evidence IDs

values

units

warnings

limitations

lineage

Report/Recipe source identities
```

要求：

```text
SCIENTIFIC_SEMANTIC_DIFF = 0
```

---

# 140. Report Semantic Hash Stability

对同一 exact composition：

若 contract要求 deterministic：

重复 projection/finalization test必须验证 semantic hash规则。

Runtime timestamp等 non-semantic fields不得影响 semantic identity。

---

# 141. Recipe Semantic Hash Stability

同理：

exact same replay manifest semantic facts：

semantic hash必须 deterministic。

---

# 142. Backend Regression

必须：

```text
uv run python -m pytest -q
```

floor：

```text
>= Phase 12-4 final canonical backend floor
```

必须动态读取。

---

# 143. Frontend Regression

必须：

```text
npm --prefix apps/web test
```

floor：

```text
>= Phase 12-4 final canonical frontend floor
```

---

# 144. Typecheck / Build / Lock / Diff

必须：

```text
npm --prefix apps/web run typecheck
= PASS

npm --prefix apps/web run build
= PASS

uv lock --check
= PASS

git diff --check
= PASS
```

---

# 145. Service Regression

Implementation exact-SHA CI继续要求：

```text
PostgreSQL

Redis

MinIO
```

required integration PASS。

Report/Recipe persistence尤其必须覆盖 service-backed path。

---

# 146. Linux / Windows Replay

若 current required CI仍包含：

```text
Linux scientific replay

Windows scientific replay
```

必须继续 PASS。

---

# 147. npm Audit

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
PASS / clean
```

---

# 148. Security

必须：

```text
NO_PHASE12_5_ARBITRARY_CODE_EXECUTION = PASS

NO_PHASE12_5_ARTIFACT_HTML_EXECUTION = PASS

NO_PHASE12_5_ARTIFACT_JAVASCRIPT_EXECUTION = PASS

NO_PHASE12_5_IFRAME_EXECUTION = PASS

NO_PHASE12_5_RECIPE_EXECUTION = PASS

NO_PHASE12_5_NOTEBOOK_EXPORT = PASS

NO_PHASE12_5_SCRIPT_EXPORT = PASS

NO_PHASE12_5_EXTERNAL_PUBLISHING = PASS

NO_PHASE12_5_RAW_ARTIFACT_TO_LLM = PASS

NO_PHASE12_5_REPORT_LLM_WRITING = PASS

NO_PHASE12_5_CROSS_PROJECT_SOURCE = PASS

NO_PHASE12_5_STALE_SOURCE_REBINDING = PASS

NO_SECRET_PATTERN_HITS = PASS
```

---

# 149. Injection Cases

至少：

```text
<script>

<img onerror>

javascript:

iframe

Markdown HTML

long caption

URL-looking string

prompt-injection text
```

在：

```text
Report title

caption

Finding text

Evidence text

Recipe raw display
```

中均 inert。

---

# 150. Phase 12-6 Handoff

必须生成：

```text
Phase12_6ResponsiveMobileAccessibilityHandoff
```

至少：

```text
DS2 version/hash

Global shell state

Planner state

Workspace state

viewer state

Findings/Evidence/Inspector state

Report/Recipe state

remaining 12-6 UX problem IDs

mobile Report constraints

mobile Workspace constraints

keyboard gaps

screen-reader gaps

zoom/reflow gaps

contrast gaps

touch gaps

reduced-motion gaps

browser evidence refs

Phase 11 authority refs
```

---

# 151. Do Not Implement 12-6

禁止把本阶段扩成：

```text
full cross-product responsive closure

full accessibility closure

all-screen mobile redesign
```

只保证 12-5 自己改动的 Report/Recipe surfaces达到 required baseline。

---

# 152. Queue Admission

Entry Gate PASS 后：

只 admit：

```text
Phase 12-5
```

要求：

```text
TASK_BLOCK_COUNT = 1

ACTIVE_TASK = Phase 12-5

PHASE_12_6_EXECUTABLE_TASK_CREATED = NO

PHASE_13_EXECUTABLE_TASK_CREATED = NO
```

---

# 153. Persistent State

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

不能改变 scientific facts。

---

# 154. ROADMAP

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
COMPLETE

Phase 12-4:
COMPLETE

Phase 12-5:
COMPLETE /
REPORT_RECIPE_EXPERIENCE_IMPLEMENTED

Phase 12-6:
REVIEWER_GATE /
AWAITING REVIEWER PROMPT

Phase 13:
ROADMAP_APPROVED /
NOT_QUEUED
```

---

# 155. First Required Output

开始后第一组输出必须：

```text
Phase 12-5 Entry Gate
+ Phase 12-4 Report/Recipe Handoff
+ Report/Recipe UX Admission
```

至少确认：

1. current HEAD；
2. origin/master；
3. branch；
4. clean worktree；
5. Phase 12-4 implementation SHA；
6. Phase 12-4 exact-SHA CI；
7. completion SHA；
8. archive SHA；
9. TASK_BLOCK_COUNT=0；
10. Phase 12-6 task absent；
11. Phase 13 task absent；
12. DS2 version/hash；
13. Phase 12-5 handoff resolves；
14. UX-005/current exact owner problems；
15. exact P12X5-A01..A08；
16. Report persistence authority；
17. Recipe persistence authority；
18. ReportCompositionRequest version；
19. ReportCompositionSnapshot version；
20. RecipeReplayManifest version；
21. ReportExportManifest version；
22. source eligibility enums；
23. mandatory Report sections；
24. draft persistence semantics；
25. finalization transaction semantics；
26. history semantics；
27. actual export formats；
28. Recipe non-execution authority；
29. Plan 0.1 behavior；
30. Plan 0.2 dependency behavior；
31. no new persistence required；
32. no new API family required；
33. no dependency required；
34. no science change required；
35. no LLM required。

成功：

```text
PHASE_12_5_ENTRY_GATE = PASS

PHASE_12_4_DEPENDENCY = VERIFIED

PHASE_11_SCIENTIFIC_AUTHORITY =
VERIFIED_READ_ONLY

PHASE_12_5_QUEUE_ADMISSION =
AUTHORIZED

PHASE_12_5_REPORT_PRESENTATION_AUTHORITY =
AUTHORIZED

PHASE_12_5_RECIPE_PRESENTATION_AUTHORITY =
AUTHORIZED

PHASE_12_5_REPORT_CONTRACT_CHANGE_AUTHORITY =
NONE

PHASE_12_5_RECIPE_CONTRACT_CHANGE_AUTHORITY =
NONE

PHASE_12_5_RECIPE_EXECUTION_AUTHORITY =
NONE

PHASE_12_5_SCIENTIFIC_CHANGE_AUTHORITY =
NONE

PHASE_12_5_READINESS =
READY_FOR_REPORT_RECIPE_UX_IMPLEMENTATION
```

---

# 156. Required Execution Sequence

严格：

```text
verify Phase 12-4 lifecycle

→ verify Phase 12-5 handoff

→ verify DS2 / Phase 11 authority

→ load exact 12-5 UX problems

→ load exact P12X5 acceptance IDs

→ audit live Report/Recipe contracts/APIs

→ admit exactly one 12-5 task

→ snapshot current Report UX

→ snapshot current Recipe UX

→ capture BEFORE evidence

→ implement Report source discovery

→ implement eligibility explanations

→ implement exact source selection

→ implement ordering

→ implement mandatory disclosure presentation

→ implement bounded caption/title UX

→ implement session-draft honesty

→ implement preview

→ implement explicit finalization UX

→ preserve atomic Report + Recipe semantics

→ implement finalized Report detail

→ implement history/recovery UX

→ implement Recipe human-readable summary

→ implement exact Recipe details

→ retain raw Recipe

→ implement export UX for existing formats

→ implement partial/stale/missing/error states

→ implement mobile Report/Recipe surfaces

→ validate keyboard/focus/zoom/touch/reduced-motion

→ close exact 12-5-owned UX problems

→ leave 12-6/12-7 problems typed/open

→ generate 12-6 handoff

→ capture AFTER evidence

→ run source identity tests

→ run mandatory disclosure propagation audit

→ run Recipe non-execution audit

→ run no-LLM-writing audit

→ run scientific payload non-change audit

→ run Report/Recipe contract non-change audit

→ run frontend/backend regressions

→ run browser matrix

→ run service-backed regression

→ run retained platform replay

→ run security/evidence/secret checks

→ create implementation commit

→ push

→ WAIT FOR IMPLEMENTATION EXACT-SHA CI

→ if PASS:
   append completion record

→ completion commit/push directly

→ archive only Phase 12-5 task

→ archive commit/push directly

→ verify queue empty

→ stop
```

---

# 157. Implementation Commit Allowed

可以包含：

```text
Report frontend

Recipe frontend

source selection UI

composition UI

preview UI

history UI

export UI

presentation-only deterministic projection helpers

DS2 styling

accessibility changes

frontend tests

browser evidence tooling

docs

persistent state

TASK admission
```

---

# 158. Implementation Commit Forbidden

不得包含：

```text
new scientific Tool

new algorithm

new Artifact family

new Report contract

new Recipe contract

Recipe execution

new Report persistence model

database migration

new public API family

new LLM writing

new external publishing integration

Report-generated science

Phase 12-6 implementation

completion result
```

---

# 159. Blocking Scientific Defect

如果发现 current Report authority：

```text
loses mandatory scientific warning

incorrectly binds source

mutates scientific value

misrepresents provenance
```

且修复需要 scientific/domain contract redesign：

必须：

```text
BLOCKED /
REPORT_SCIENTIFIC_AUTHORITY_DEFECT_REVIEW_REQUIRED
```

不得把它伪装成 UX fix。

---

# 160. Blocking Recipe Defect

如果 exact Recipe本身：

```text
loses Tool version

loses parameter

invents dependency

binds latest Artifact

can execute
```

必须：

```text
BLOCKED /
RECIPE_AUTHORITY_DEFECT_REVIEW_REQUIRED
```

---

# 161. Implementation Exact-SHA CI

push 后：

必须：

```text
WAIT FOR IMPLEMENTATION EXACT-SHA CI
```

required jobs全部 PASS。

---

# 162. Minimum CI

至少：

```text
Backend Unit

Frontend Tests

Typecheck

Build

Phase 12-5 focused evidence

Chromium

Firefox

WebKit

390x844

PostgreSQL/Redis/MinIO

Report/Recipe service-backed cases

retained Linux replay

retained Windows replay

Phase 11 authority integrity

evidence integrity

security / secret scan
```

---

# 163. Failed Candidate

CI failure：

记录：

```text
failed SHA

CI run

failed job

root cause
```

然后 fix-forward。

禁止：

```text
force push

rewrite history

delete tests

weaken source identity

remove mandatory disclosure

enable latest rebinding

enable Recipe execution

change acceptance IDs

move UX problem ownership
```

---

# 164. Completion Record

只有 implementation exact-SHA CI PASS：

才 append：

```text
Phase 12-5 Report / Recipe Experience Result
```

到：

```text
results.md
```

然后：

```text
commit
push
```

不等待 completion CI。

---

# 165. Queue Archive

completion push 后：

只删除：

```text
Phase 12-5 TASK block
```

不得创建：

```text
Phase 12-6 executable task
```

然后：

```text
commit
push
```

不等待 archive CI。

---

# 166. Lifecycle Terminology

最终：

```text
IMPLEMENTATION_VERIFIED_BY_EXACT_SHA_CI

COMPLETION_RECORDED

QUEUE_ARCHIVED
```

不能虚构 completion/archive exact-SHA verification。

---

# 167. Mandatory Result Markers

必须：

```text
PHASE12_5_PRODUCTION_UI_CHANGES =
YES_REPORT_RECIPE_PRESENTATION

PHASE12_5_BACKEND_BEHAVIOR_CHANGES = 0

PHASE12_5_SCIENTIFIC_BEHAVIOR_CHANGES = 0

PHASE12_5_REPORT_CONTRACT_CHANGES = 0

PHASE12_5_RECIPE_CONTRACT_CHANGES = 0

PHASE12_5_REPORT_PERSISTENCE_AUTHORITY_CHANGES = 0

PHASE12_5_RECIPE_PERSISTENCE_AUTHORITY_CHANGES = 0

PHASE12_5_SOURCE_ELIGIBILITY_SEMANTIC_CHANGES = 0

PHASE12_5_WORKSPACE_AUTHORITY_CHANGES = 0

PHASE12_5_ARTIFACT_CONTRACT_CHANGES = 0

PHASE12_5_NEW_SCIENTIFIC_TOOLS = 0

PHASE12_5_NEW_SCIENTIFIC_ALGORITHMS = 0

PHASE12_5_NEW_ARTIFACT_FAMILIES = 0

PHASE12_5_NEW_DATAPROFILE_VERSION = 0

PHASE12_5_NEW_ANALYSISPLAN_VERSION = 0

PHASE12_5_NEW_DATABASE_MIGRATIONS = 0

PHASE12_5_NEW_PUBLIC_API_FAMILIES = 0

PHASE12_5_NEW_DEPENDENCIES = 0

PHASE12_5_LOCKFILE_CHANGES = 0

PHASE12_5_NEW_LLM_CALL_SITES = 0

PHASE12_5_REAL_LLM_CALLS = 0

PHASE12_5_REPORT_LLM_WRITING_CALLS = 0

PHASE12_5_FRONTEND_SCIENTIFIC_RECOMPUTATION = 0
```

---

# 168. Report Authority Markers

必须：

```text
REPORT_SOURCE_EXACT_IDENTITY = PASS

REPORT_SOURCE_LATEST_REBINDING = 0

REPORT_SOURCE_FUZZY_BINDING = 0

REPORT_SOURCE_FILENAME_AUTHORITY = 0

REPORT_SOURCE_MIME_ONLY_AUTHORITY = 0

REPORT_MANDATORY_DISCLOSURE_LOSS = 0

REPORT_DRAFT_AUTOMATIC_FINALIZE = 0

REPORT_PREVIEW_EQUALS_FINALIZED = NO

FINALIZED_REPORT_IMMUTABILITY = PASS
```

---

# 169. Recipe Markers

必须：

```text
RECIPE_EXECUTION_AUTHORITY = NONE

RECIPE_AUTO_PLAN_CREATION = 0

RECIPE_AUTO_JOB_CREATION = 0

RECIPE_AUTO_QUEUE = 0

RECIPE_AUTO_TOOL_EXECUTION = 0

RECIPE_EXACT_TOOL_VERSION_TRACEABILITY = PASS

RECIPE_EXACT_PARAMETER_TRACEABILITY = PASS

RECIPE_EXACT_ARTIFACT_TRACEABILITY = PASS

RECIPE_RAW_DECLARATION_ACCESSIBLE = YES

RAW_RECIPE_DEFAULT_PRIMARY_UI = NO
```

---

# 170. Draft Markers

按 actual authority：

```text
REPORT_DRAFT_PERSISTENCE =
SESSION_ONLY

REPORT_DRAFT_SERVER_WRITES = 0

REPORT_DRAFT_LOCALSTORAGE_WRITES = 0

REPORT_DRAFT_AUTOMATIC_FINALIZE = 0
```

如果 current repository已有 reviewer-approved不同值：

使用 actual并解释 authority。

---

# 171. Scientific Honesty Markers

必须：

```text
SUPPORTED_EQUALS_VALIDATED = NO

REPORT_INCLUDED_EQUALS_VALIDATED = NO

RECIPE_EXISTS_EQUALS_REPRODUCIBILITY_VALIDATED = NO

MAPPING_ONLY_VISUAL_UPGRADE = 0

NOT_APPLICABLE_VISUAL_UPGRADE = 0

V4_VISUAL_FABRICATION = 0

BROWSER_PASS_EQUALS_SCIENTIFIC_PASS = NO

SCREENSHOT_NUMERIC_SCIENTIFIC_AUTHORITY = NONE

FRONTEND_SCIENTIFIC_AUTHORITY = NONE
```

---

# 172. Baseline Markers

必须：

```text
REGISTRY_BEFORE_12_5 = 62
REGISTRY_AFTER_12_5 = 62

DATAPROFILE_BEFORE_12_5 = 2.4
DATAPROFILE_AFTER_12_5 = 2.4

MIGRATION_BEFORE_12_5 =
0007_phase10m1_workspace_domain

MIGRATION_AFTER_12_5 =
0007_phase10m1_workspace_domain
```

---

# 173. UX Problem Markers

必须：

```text
PHASE12_5_OWNED_PROBLEMS =
<exact repository IDs>

PHASE12_5_OWNED_PROBLEM_COUNT =
<actual>

PHASE12_5_OWNED_PROBLEMS_CLOSED =
<same>

PHASE12_5_OWNED_PROBLEMS_OPEN = 0

NEW_P0_INTRODUCED_BY_12_5 = 0

NEW_P1_INTRODUCED_BY_12_5 = 0
```

---

# 174. Acceptance Marker

必须：

```text
P12X5_ACCEPTANCE = 8/8
```

使用 canonical exact descriptions。

---

# 175. Accessibility Markers

至少：

```text
REPORT_SOURCE_SELECTION_KEYBOARD = PASS

REPORT_ORDERING_KEYBOARD = PASS

REPORT_FINALIZE_KEYBOARD = PASS

REPORT_DIALOG_FOCUS = PASS

RECIPE_KEYBOARD = PASS

MANDATORY_DISCLOSURE_NON_COLOR = PASS

MOBILE_TOUCH_TARGETS = PASS

REDUCED_MOTION = PASS
```

但：

```text
FULL_PRODUCT_ACCESSIBILITY_COMPLETE = NO
```

---

# 176. Required results.md Structure

至少：

# Phase 12-5 Report / Recipe Experience Result

1. Conclusion
2. Phase 12-4 Baseline
3. Entry Gate
4. Repository State
5. DS2 Authority
6. Phase 11 Scientific Authority
7. Phase 12-5 Handoff Integrity
8. UX Problem Ownership
9. Production Behavior Changes
10. Report Persistence Authority
11. Recipe Persistence Authority
12. Report Composition Contracts
13. Recipe Contract
14. Source Eligibility Authority
15. Report Source Discovery
16. Exact Source Identity
17. Figure Sources
18. Table Sources
19. Finding Sources
20. Evidence Sources
21. Provenance Sources
22. Disclosure-Only / Metadata Sources
23. Unsupported Sources
24. Source Eligibility Explanations
25. Report Draft Authority
26. Draft Session Honesty
27. Report Builder
28. Source Selection
29. Ordering
30. Caption Boundary
31. Mandatory Warnings / Limitations
32. Partial / Failed / Blocked Scope
33. Preview
34. Preview vs Finalized State
35. Finalization
36. Atomic Report + Recipe
37. Finalized Immutability
38. Report Detail
39. Report History
40. Historical Recovery
41. Recipe Reproducibility Summary
42. Recipe Exact Analysis Details
43. Recipe Raw Manifest
44. AnalysisPlan 0.1 Recipe
45. AnalysisPlan 0.2 Recipe
46. Recipe Non-Execution
47. Export
48. Export Safety
49. Stale / Missing Sources
50. Source Integrity Failure
51. Report Scientific Wording
52. Findings/Evidence Integration
53. Provenance Integration
54. Workspace Boundary
55. Inspector Boundary
56. Mobile 390x844
57. Desktop 1440x900
58. Desktop 1280x720
59. 200% Zoom
60. Keyboard / Focus
61. Reduced Motion
62. Accessibility Foundation
63. Browser Matrix
64. Report Finalization Replay
65. Interaction Baseline Comparison
66. Scientific Payload Non-Change
67. Report Contract Non-Change
68. Recipe Contract Non-Change
69. Recipe Non-Execution Audit
70. No-LLM-Writing Audit
71. Security
72. Database/API/Dependency Freeze
73. Registry/DataProfile Freeze
74. Phase 12-5 Problem Closure
75. Deferred UX Problems
76. Phase 12-6 Handoff
77. Backend Regression
78. Frontend Regression
79. Typecheck
80. Build
81. Service Regression
82. Linux/Windows Replay
83. npm Audit
84. Evidence Inventory
85. Evidence Manifest
86. Files Changed
87. Acceptance Registry
88. Implementation Commit
89. Implementation CI
90. Failed Candidates
91. Completion Record
92. Queue Archive
93. Queue State
94. Phase 12-6 Reviewer Gate
95. Final Repository State

---

# 177. PASS Gate

只有全部满足：

```text
Phase 12-4 PASS

Phase 12-4 implementation exact-SHA CI PASS

Phase 12-4 queue archived


HEAD == origin/master at entry

worktree clean

TASK_BLOCK_COUNT = 0


Phase 12-5 handoff resolves

exact owned UX problems resolve

exact P12X5 acceptance IDs resolve


Report persistence authority unchanged

Recipe persistence authority unchanged

Report contracts unchanged

Recipe contract unchanged

source eligibility semantics unchanged


Report source discovery implemented

source eligibility explained

exact source identity preserved

fuzzy/latest binding = 0


Report Builder implemented

ordering implemented where authorized

mandatory warnings/limitations preserved

partial/failed scope preserved

draft honesty preserved

preview distinct from finalized


explicit finalize implemented

atomic Report + Recipe preserved

finalized Report immutable

history/recovery implemented


Recipe human-readable UX implemented

exact Recipe details retained

raw Recipe retained

Recipe execution authority = NONE


existing export UX implemented

no executable export

historical exact identity preserved


12-5-owned UX problems closed

new P0 = 0

new P1 = 0


12-6/12-7 problems remain typed/open


scientific behavior changes = 0

frontend scientific recomputation = 0

Report-generated science = 0

LLM Report writing = 0

new Tool = 0

new algorithm = 0

new Artifact family = 0

DataProfile unchanged

AnalysisPlan unchanged

migration unchanged

new public API family = 0

new dependency = 0

lock change = 0


keyboard PASS

focus PASS

non-color disclosures PASS

touch target PASS

reduced motion PASS


Chromium PASS

Firefox PASS

WebKit PASS

390x844 PASS


backend >= dynamic 12-4 floor

frontend >= dynamic 12-4 floor

typecheck PASS

build PASS

lock PASS

diff PASS

PostgreSQL/Redis/MinIO PASS

required retained platform replay PASS

evidence integrity PASS

security PASS

secret scan PASS


P12X5 = 8/8


implementation exact-SHA CI PASS

completion record committed/pushed

queue archive committed/pushed


TASK_BLOCK_COUNT = 0

Phase 12-6 task absent

Phase 13 task absent

HEAD == origin/master

worktree clean
```

才能：

```text
Phase 12-5 = PASS
```

---

# 178. BLOCKED — Phase 12-4 Incomplete

若：

```text
Phase 12-4 not PASS

implementation CI not PASS

queue not archived
```

必须：

```text
BLOCKED /
PHASE_12_4_DEPENDENCY_NOT_CLOSED
```

---

# 179. BLOCKED — Report Contract Redesign Required

如果 UX目标需要：

```text
new Report contract

new composition authority

new mandatory scientific section semantics

new persistent draft model
```

必须：

```text
BLOCKED /
REPORT_DOMAIN_REDESIGN_REQUIRED
```

---

# 180. BLOCKED — Recipe Execution Required

如果执行器认为“Recipe UX完整”必须：

```text
run Recipe
```

则：

```text
BLOCKED /
RECIPE_EXECUTION_OUT_OF_SCOPE
```

---

# 181. BLOCKED — Scientific Source Recomputed

若 browser为了 Report生成：

```text
new metric

new table science

new figure science

unit conversion

fit

summary statistic
```

必须 BLOCKED。

---

# 182. BLOCKED — Latest/Fuzzy Source

任何：

```text
latest Artifact

nearest Artifact

same title

same filename

same numeric value

array position
```

绑定 Report source：

不能 PASS。

---

# 183. BLOCKED — Mandatory Limitation Lost

如果：

```text
scientific limitation

warning

failed scope

blocked scope
```

从 finalized Report消失：

必须：

```text
BLOCKED /
SCIENTIFIC_REPORT_MISREPRESENTATION
```

---

# 184. BLOCKED — Draft Becomes Hidden Authority

如果 frontend把 session draft：

自动保存为：

```text
localStorage canonical

server canonical

finalized canonical
```

而 current contract未授权：

不能 PASS。

---

# 185. BLOCKED — LLM Report Writing

若新增：

```text
DeepSeek summary

LLM caption

LLM conclusion

LLM citation
```

不能 PASS。

---

# 186. BLOCKED — Owned UX Problems Remain

如果：

```text
PHASE12_5_OWNED_PROBLEMS_OPEN > 0
```

不能 PASS。

---

# 187. Non-Blockers

允许继续：

```text
Phase 12-6 remaining mobile/accessibility debt

Phase 12-7 final consistency debt

session-only unfinalized drafts

JSON/Markdown-only export
if that is current authority

legacy Reports with unavailable fields

Plan 0.1 without dependency graph

V4 = 0

reference-limited science

unsupported formats

Future Scope
```

只要诚实呈现。

---

# 188. Final Successful State

成功：

```text
Phase 12-5:
PASS /
REPORT_RECIPE_EXPERIENCE_REDESIGNED /
REPRODUCIBILITY_PRESENTATION_UNIFIED /
QUEUE_ARCHIVED

Phase 12:
IN_PROGRESS /
CORE_DESKTOP_PRODUCT_EXPERIENCE_COMPLETE

Phase 12-6:
REVIEWER_GATE /
AWAITING REVIEWER PROMPT

Phase 13:
ROADMAP_APPROVED /
NOT_QUEUED /
NOT_EXECUTABLE

TASK_BLOCK_COUNT = 0

PHASE_12_6_EXECUTABLE_TASK_CREATED = NO

PHASE_13_EXECUTABLE_TASK_CREATED = NO
```

---

# 189. What Phase 12-5 Completion Means

可以说：

```text
The product now provides a coherent Report experience
for discovering, selecting, ordering, previewing and
finalizing exact persisted scientific sources while
preserving mandatory warnings, limitations, failed scope,
evidence and provenance.

The paired Recipe is presented as a human-readable
reproducibility record with exact Tool, parameter,
dependency and Artifact identities available for audit,
while remaining declarative and non-executable.
```

---

# 190. What Completion Does NOT Mean

不能说：

```text
Reports generate new scientific conclusions.

Recipe can reproduce by executing itself.

Every Report is scientifically validated.

PDF/DOCX publishing is complete.

Full mobile/accessibility closure is complete.

Phase 12 is complete.

The product is release-ready.
```

---

# 191. Phase 12-6 Gate

最终：

```text
Phase 12-6:
REVIEWER_GATE /
AWAITING REVIEWER PROMPT

PHASE_12_6_EXECUTABLE_TASK_CREATED = NO
```

---

# 192. Stop Rule

完成后立即停止。

不得：

```text
perform full responsive/mobile closure

perform full accessibility closure

start Phase 12-7

start Phase 13

add new export product families

add Recipe execution
```

返回 reviewer：

```text
Phase 12-5 final result

implementation SHA

implementation exact-SHA CI

completion SHA

archive SHA

exact 12-5-owned UX problem closure

P12X5 8/8

Report source eligibility proof

mandatory disclosure propagation proof

draft/finalization authority proof

atomic Report + Recipe proof

Recipe non-execution proof

historical exact-identity proof

export boundary

scientific payload non-change proof

browser/mobile/accessibility evidence

remaining UX problem ownership

Phase 12-6 handoff state
```

然后等待 reviewer。




---END---



---TASK---
 状态：待处理

# Phase 12-6 Reviewer Prompt

# Responsive + Mobile + Accessibility Closure

你现在执行：

# Phase 12-6：Responsive / Mobile / Accessibility Closure

中文：

# 全产品响应式 + 移动端 + 无障碍体验封板

本阶段属于：

```text
Phase 12:
Comprehensive UI / UX
Product Experience Redesign
```

当前 Phase 12 序列：

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
= COMPLETE

12-3
Scientific Workspace
+ Scientific Viewer Experience
= COMPLETE

12-4
Findings / Evidence /
Inspector / Provenance Experience
= MUST ALREADY BE COMPLETE

12-5
Report / Recipe Experience
= MUST BE VERIFIED AT ENTRY

12-6
Responsive / Mobile /
Accessibility Closure
= CURRENT AUTHORIZED PHASE

12-7
Cross-Product UX Validation
+ Design Evidence Closure
```

---

# 0. Mission

Phase 12-6 的职责不是再设计一轮产品。

它的职责是：

```text
consume completed 12-1 ~ 12-5 product experience

→ audit every current product surface

→ close responsive layout gaps

→ close canonical mobile workflow gaps

→ close keyboard navigation gaps

→ close focus-management gaps

→ close screen-reader semantics gaps

→ close touch-target gaps

→ close zoom/reflow gaps

→ close contrast/non-color-state gaps

→ close reduced-motion gaps

→ close chart/3D accessibility alternatives

→ verify cross-product consistency

→ prove no scientific authority changed

→ produce Phase 12-7 UX validation handoff

→ exact-SHA CI

→ completion

→ queue archive

→ stop
```

核心目标：

```text
RESPONSIVE_CLOSURE = YES

MOBILE_CLOSURE = YES

ACCESSIBILITY_ENGINEERING_CLOSURE = YES

SCIENTIFIC_AUTHORITY_CHANGE = NO
```

---

# 1. Fundamental Boundary

必须：

```text
ACCESSIBILITY_CLOSURE
!=
PRODUCT_REARCHITECTURE
```

以及：

```text
MOBILE_CLOSURE
!=
COMPRESSED_DESKTOP
```

以及：

```text
RESPONSIVE_REDESIGN
!=
SCIENTIFIC_SEMANTIC_CHANGE
```

12-6 可以改变：

```text
responsive layout

breakpoint behavior

mobile presentation

drawer/sheet behavior

control placement at responsive widths

focus management

keyboard interaction

ARIA/semantic markup

accessible naming

status announcements

touch-target sizing

contrast

non-color presentation

zoom/reflow behavior

reduced motion

table responsive presentation

chart accessibility presentation

3D accessibility presentation

screen-reader alternatives

mobile Report/Recipe presentation

mobile Findings/Evidence presentation
```

不能改变：

```text
Global IA

Planner semantics

Workspace IA

Workspace authority

scientific viewer computation

Artifact contracts

selection semantics

Finding/Evidence semantics

Inspector conceptual architecture

Report contracts

Recipe contracts

scientific algorithms

scientific values

scientific claims

database/API/domain authority
```

---

# 2. Reviewer Authorization

正式条件预授权：

```text
PHASE_12_6_PROMPT_PREAUTHORIZED = YES

AUTHORIZED_PHASE = Phase 12-6

MAX_PHASES_EXECUTED = 1
```

只有 Entry Gate PASS 后：

才能创建：

```text
one Phase 12-6 TASK block
```

本 Prompt 不授权：

```text
Phase 12-7 implementation

Phase 13 implementation
```

---

# 3. Mandatory Phase 12-5 Dependency

必须从真实 repository 读取：

```text
git history

results.md

TASKS.md

docs/ROADMAP.md

persistent/

docs/phase12/

docs/phase12/evidence/
```

动态取得：

```text
PHASE_12_5_IMPLEMENTATION_SHA

PHASE_12_5_IMPLEMENTATION_CI_RUN

PHASE_12_5_IMPLEMENTATION_CI_RESULT

PHASE_12_5_COMPLETION_SHA

PHASE_12_5_QUEUE_ARCHIVE_SHA
```

必须确认：

```text
Phase 12-5 = PASS

implementation exact-SHA CI = PASS

completion recorded

queue archived
```

否则：

```text
PHASE_12_6_ENTRY_GATE = BLOCKED

reason =
PHASE_12_5_NOT_COMPLETED_OR_NOT_ARCHIVED
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

Phase 12-6 task absent

Phase 12-7 task absent

Phase 13 task absent
```

---

# 5. Mandatory Phase 12-6 Handoff

必须找到唯一 canonical：

```text
Phase12_6ResponsiveMobileAccessibilityHandoff
```

或 repository current equivalent。

至少读取：

```text
Design System version/hash

Global shell state

Planner state

Workspace state

scientific viewer state

Findings/Evidence/Inspector state

Report/Recipe state

remaining Phase 12-6 UX problem IDs

desktop/mobile surface inventory

mobile constraints

keyboard gaps

focus gaps

screen-reader gaps

zoom/reflow gaps

contrast gaps

touch-target gaps

reduced-motion gaps

browser evidence refs

Phase 11 scientific authority refs
```

缺失：

```text
BLOCKED /
PHASE_12_6_HANDOFF_INVALID
```

---

# 6. Prior Phase Authority

必须确认：

```text
Phase 12-1
Design System 2.0
= authoritative presentation foundation

Phase 12-2
Global Navigation + Planner
= architecture frozen

Phase 12-3
Workspace + Viewer
= architecture frozen

Phase 12-4
Findings/Evidence/Inspector/Provenance
= architecture frozen

Phase 12-5
Report/Recipe
= architecture frozen
```

12-6 不重新打开这些架构决策。

---

# 7. Design System

继续消费：

```text
DESIGN_SYSTEM_VERSION = 2.0
```

及 current canonical semantic hash。

允许修复：

```text
responsive token defect

contrast token defect

focus token defect

touch primitive defect

reduced-motion defect
```

但不得：

```text
create DS 2.1

create parallel mobile design system
```

---

# 8. Phase 11 Scientific Authority

继续：

```text
READ_ONLY
```

必须动态验证：

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

# 9. Scientific Validation Honesty

继续保留 final actual facts。

当前 expected baseline包括：

```text
golden benchmark records = 12

PASS_INVARIANT = 8

NOT_APPLICABLE = 4

numeric cross-platform validation =
NOT_APPLICABLE

V4 = 0
```

UI不得通过 accessibility/mobile wording升级这些事实。

---

# 10. Accessibility Target

Phase 12 engineering target：

```text
WCAG-LIKE AA
```

含义：

```text
engineering acceptance target
```

不表示：

```text
formal WCAG certification

legal compliance certification

third-party accessibility certification
```

最终必须诚实写：

```text
ACCESSIBILITY_ENGINEERING_TARGET_MET = YES/NO
```

而不是：

```text
WCAG_CERTIFIED = YES
```

---

# 11. Canonical Accessibility Dimensions

至少完整覆盖：

```text
Keyboard

Focus

Screen Reader Semantics

Accessible Names

Heading Structure

Landmarks

Dialogs / Drawers / Bottom Sheets

Async Status Announcements

Forms

Tables

Charts

3D / WebGL

Touch Targets

Contrast

Non-Color Meaning

200% Zoom

Reflow

Reduced Motion

Text Expansion

Mobile Navigation

Mobile Scientific Workflows

Error / Loading / Empty states
```

---

# 12. Canonical Responsive Surface Inventory

必须重新读取 current user-visible surface registry。

至少覆盖：

```text
Global Shell

Home

Data

Analyses

Workspaces

Reports

Settings

Planner

Data Context

Prompt Composer

Clarification

Eligibility

Human Plan

Execution / Progress

Error / Recovery

Scientific Workspace

Workspace Overview

Data

Analysis

Results

Artifact Gallery

Scientific viewers

Findings

Evidence

Inspector

Provenance

Report

Recipe

History

Settings

Dialogs

Drawers

Bottom Sheets

Loading

Empty

Error

Unsupported

Stale

Partial
```

---

# 13. Surface Completeness

最终：

```text
RESPONSIVE_SURFACE_UNCLASSIFIED = 0

ACCESSIBILITY_SURFACE_UNCLASSIFIED = 0
```

---

# 14. Phase 12-6 UX Problems

必须从：

```text
phase12_ux_problem_matrix
```

读取：

```text
owner = 12-6
```

的 exact IDs。

历史 expected baseline：

```text
UX-006

UX-009
```

但 actual repository authority优先。

不得根据 Prompt 直接假定 ID。

---

# 15. UX Problem Closure

全部 owner=12-6：

必须：

```text
FIXED_WITH_EVIDENCE
```

最终：

```text
PHASE12_6_OWNED_PROBLEMS_OPEN = 0
```

禁止：

```text
change owner

lower severity

delete row

rename canonical problem
```

---

# 16. Phase 12-7 Problems

12-7 owned problems继续：

```text
OPEN / OWNED
```

若 12-6改善：

```text
FOUNDATION_IMPROVED /
FINAL_CLOSURE_REMAINS_WITH_12_7
```

---

# 17. New UX Regression Rule

必须：

```text
NEW_P0_INTRODUCED_BY_12_6 = 0

NEW_P1_INTRODUCED_BY_12_6 = 0
```

---

# 18. Mobile Authority

Workspace mobile architecture继续冻结：

```text
ONE_ACTIVE_PANEL = YES

CONTEXT_NAVIGATION_DRAWER = YES

PANEL_SWITCHER = YES

INSPECTOR_BOTTOM_SHEET = YES
```

不得改成：

```text
desktop 3-column Workspace
scaled down to phone
```

---

# 19. Global Mobile Navigation

必须覆盖六项 Global IA：

```text
Home

Data

Analyses

Workspaces

Reports

Settings
```

在移动端：

```text
discoverable

keyboard accessible

screen-reader understandable

touch usable

current state explicit

no horizontal nav overflow
```

---

# 20. Mobile Navigation State

current destination：

必须：

```text
textually identifiable

aria-current or semantic equivalent

not color-only
```

---

# 21. Mobile Planner

必须覆盖：

```text
data context

prompt composer

suggestions if applicable

intent

clarification

eligibility

human plan

execution

partial/error

Workspace transition
```

390x844下可完整完成主流程。

---

# 22. Mobile Keyboard Interaction

软件键盘打开时：

必须验证：

```text
prompt remains visible enough

submit remains reachable

error remains reachable

clarification options remain reachable

page can recover after keyboard closes
```

---

# 23. Mobile Clarification

Clarification：

不能因移动端：

```text
bury valid choices

hide question reason

require horizontal scrolling
```

---

# 24. Mobile Human Plan

必须：

```text
readable

not raw Tool IDs first

dependencies understandable

developer detail optional
```

---

# 25. Mobile Execution

必须：

```text
show stage

show partial state

show errors

show preserved results

show Workspace transition
```

不得 blank screen只剩 spinner。

---

# 26. Mobile Workspace

必须完整支持：

```text
navigation

active result

panel switch

result selection

viewer

warning/limitation

Inspector entry

Findings

Evidence

Report
```

---

# 27. Mobile Workspace Does Not Mount Everything

继续：

```text
HEAVY_VIEWER_LAZY = YES
```

不得因 mobile layout：

mount hidden sibling viewers。

---

# 28. Mobile Scientific Viewer

至少验证：

```text
toolbar

legend

selection

table alternative

fullscreen

warning

loading

error

touch interaction
```

---

# 29. Mobile Chart

必须防止：

```text
legend covering chart

toolbar offscreen

axis label clipping

tooltip permanently blocking data

horizontal page overflow
```

---

# 30. Mobile 3D

必须：

```text
viewer receives bounded area

toolbar reachable

camera reset reachable

selection reachable

fullscreen exit reachable
```

不得改变 scientific scene。

---

# 31. Mobile Tables

必须：

```text
preserve scientific data
```

允许：

```text
horizontal table scrolling

column prioritization

responsive summaries
```

但禁止：

```text
silently drop scientific columns
```

---

# 32. Mobile Findings

必须：

```text
read claim

see qualification

see limitation

open evidence
```

不要求阅读 desktop-width cards。

---

# 33. Mobile Evidence

必须支持：

```text
Finding
→ Evidence
→ Artifact/Result
→ Provenance
→ Back
```

不丢 exact context。

---

# 34. Mobile Inspector

继续：

```text
Inspector = bottom sheet
```

至少：

```text
Summary

Scientific Details

Provenance
```

可完整访问。

---

# 35. Mobile Report

必须能：

```text
discover source

select source

inspect mandatory disclosure

order source

preview

finalize

open historical Report

open Recipe
```

---

# 36. Mobile Recipe

human-readable Recipe必须先于 raw manifest。

Raw manifest：

仍可访问。

---

# 37. Touch Target Requirement

所有主要 interactive touch controls：

```text
>= 44x44 CSS px
```

至少覆盖：

```text
nav

buttons

icon buttons

tabs

panel switcher

viewer toolbar

dialog controls

bottom sheet controls

Report source controls

Inspector controls
```

---

# 38. Touch Target Exceptions

如果 inline control物理视觉尺寸较小：

可通过：

```text
larger hit area
```

满足。

但必须 evidence验证 actual interactive target。

---

# 39. Touch Target Audit

建立：

```text
TouchTargetMatrix
```

每 row：

```text
surface

control

viewport

width

height

pass

exceptionReason

evidence
```

最终：

```text
REQUIRED_TOUCH_TARGET_FAILURES = 0
```

---

# 40. Keyboard Mission

目标：

> 不使用鼠标，也能完成所有核心产品工作流。

至少：

```text
navigate product

select data context

submit analysis

answer clarification

inspect Plan

follow execution

open Workspace

switch result

use basic viewer controls

open Findings

inspect Evidence

use Inspector

build/finalize Report

open Recipe
```

---

# 41. Native Semantics First

优先：

```text
button

a

input

select

textarea

table

dialog semantics
```

禁止：

```text
div onClick
```

作为可交互 control而无完整 keyboard semantics。

---

# 42. Keyboard Activation

buttons/controls：

必须支持 appropriate：

```text
Enter

Space
```

native behavior。

---

# 43. Tab Order

必须：

```text
logical

predictable

matches visual reading order
```

不得通过大量 positive tabindex重排。

---

# 44. Positive Tabindex

目标：

```text
POSITIVE_TABINDEX_COUNT = 0
```

除非 repository有明确 documented exception。

---

# 45. Keyboard Traps

必须：

```text
UNINTENTIONAL_KEYBOARD_TRAPS = 0
```

dialogs/modals除外：

仅允许 intentional focus containment。

---

# 46. Focus Visible

所有 keyboard-focusable controls：

必须：

```text
focus-visible
```

明显可辨。

---

# 47. Focus Color Only

focus不能仅靠极轻微颜色变化。

应有：

```text
outline/ring/shape
```

等明确 visual indicator。

---

# 48. Focus Restoration

必须覆盖：

```text
dialog close

drawer close

bottom sheet close

fullscreen exit

Inspector close

Report finalization dialog close

navigation menu close
```

focus回到合理 origin。

---

# 49. Route Navigation Focus

route change后：

必须避免：

```text
focus stays on removed DOM node
```

应进入：

```text
new page main heading/content
```

或 equivalent accessible pattern。

---

# 50. Dialog Focus

必须：

```text
initial focus reasonable

tab contained

escape behavior if allowed

close accessible

focus restored
```

---

# 51. Drawer Focus

Global nav drawer / Workspace drawer：

同样。

---

# 52. Bottom Sheet Focus

Inspector mobile bottom sheet：

同样必须处理：

```text
open

focus

navigate

close

restore
```

---

# 53. Screen Reader Landmarks

至少：

```text
header/banner

navigation

main

complementary where appropriate

contentinfo if present
```

不能滥用 landmark。

---

# 54. Heading Hierarchy

每 canonical surface：

必须：

```text
one clear page/main heading

logical nested section headings
```

避免：

```text
h1 → h4
```

无语义理由的跳级。

---

# 55. Accessible Names

所有：

```text
icon buttons

menus

inputs

comboboxes

dialogs

viewer controls

report controls

copy buttons
```

必须有 accessible name。

---

# 56. Placeholder Is Not Label

表单不得仅靠 placeholder。

必须有：

```text
visible label
or
programmatic persistent label
```

---

# 57. Form Error Association

错误必须与对应 input：

```text
programmatically associated
```

并可被 screen reader发现。

---

# 58. Required / Optional

必须清晰。

不能仅：

```text
red asterisk
```

表达 required。

---

# 59. Async Status Announcements

至少审计：

```text
Planning

Clarification ready

Execution started

Execution partial

Execution failed

Workspace ready

Report finalized

Export ready
```

使用适当 live semantics。

---

# 60. No Live Region Spam

禁止：

```text
every progress tick
every viewer hover
every chart redraw
```

都进入 live region。

---

# 61. Error Announcements

blocking error：

必须被 screen reader及时发现。

---

# 62. Non-Color Meaning

必须验证：

```text
ready

running

success

partial

warning

limitation

error

unsupported

stale

read-only

support

validation

reproducibility
```

均不依赖颜色单独表达。

---

# 63. Scientific Series Colors

科学 series颜色保持 existing scientific mapping。

Accessibility不得通过：

```text
replace every scientific series with semantic status colors
```

破坏 identity。

---

# 64. Scientific Chart Accessibility

每 applicable chart至少应提供：

```text
title

scientific summary

axis labels

units

legend labels

status/warnings

table/data alternative
```

---

# 65. Chart Table Alternative

表格必须来自：

```text
same persisted scientific payload
```

不得重新计算。

---

# 66. Chart Keyboard

必须审计当前 chart library可实现范围。

至少 page-level/chart controls：

```text
keyboard accessible
```

若 plot internals无法完整 screen-reader探索：

必须通过：

```text
table/text alternative
```

提供 equivalent scientific data access。

---

# 67. Chart Accessibility Honesty

不能声称：

```text
interactive chart fully screen-reader accessible
```

如果实际只是有替代表格。

应准确记录：

```text
VISUAL_CHART_INTERACTION_ACCESSIBILITY =
LIMITED_WITH_EQUIVALENT_DATA_ALTERNATIVE
```

若实际如此。

---

# 68. 3D Accessibility

3D scene本身不能保证 screen-reader spatial equivalence。

必须提供：

```text
structure summary

selection summary

scientific metadata

tabular/text representation where available

warnings

camera/view controls accessible
```

---

# 69. 3D Accessibility Honesty

不得声称：

```text
3D scientific geometry fully screen-reader equivalent
```

除非有真实证据。

可记录：

```text
3D_VISUAL_ACCESS =
VISUAL_WITH_STRUCTURED_TEXT_ALTERNATIVE
```

---

# 70. 3D Scientific Authority

继续：

```text
WEBGL_NUMERIC_SCIENTIFIC_AUTHORITY = NONE
```

---

# 71. Motion

必须扫描：

```text
CSS transitions

animations

drawers

sheets

toasts

skeleton shimmer

chart animations

viewer transitions

loading animations
```

---

# 72. Reduced Motion

在：

```text
prefers-reduced-motion: reduce
```

下：

必须：

```text
disable/simplify non-essential animation
```

不得改变：

```text
scientific trajectory semantics
```

如果 trajectory播放是用户显式启动：

可以运行。

但 UI decorative animation应简化。

---

# 73. Skeleton Motion

reduced motion时：

shimmer必须关闭/简化。

---

# 74. 200% Zoom

必须在 browser实际测试：

```text
200% zoom
```

至少：

```text
Global shell

Planner

Clarification

Plan

Execution

Workspace

Results

Scientific viewer

Findings

Evidence

Inspector

Report

Recipe

Settings
```

---

# 75. 200% Zoom PASS

不能：

```text
essential action clipped

dialog close unreachable

warning hidden

text overlapping

fixed-height content lost
```

---

# 76. Reflow

至少在：

```text
~320 CSS px effective width
```

或 equivalent 200% zoom / responsive condition下：

核心流程仍可操作。

---

# 77. Horizontal Overflow

允许：

```text
scientific table container horizontal scroll

specialized data canvas
```

不允许：

```text
whole page accidental horizontal scroll
```

---

# 78. Overflow Matrix

必须区分：

```text
INTENTIONAL_COMPONENT_SCROLL

UNEXPECTED_PAGE_OVERFLOW
```

最终：

```text
UNEXPECTED_PAGE_OVERFLOW_REQUIRED_CASES = 0
```

---

# 79. Contrast

必须 automated + representative visual audit。

覆盖：

```text
body text

secondary text

disabled text where meaningful

links

buttons

inputs

focus

statuses

warnings

limitations

table grid/header

tooltip

dialog

mobile nav

viewer chrome
```

---

# 80. Contrast Target

使用：

```text
WCAG-like AA engineering thresholds
```

适用字体大小按 current design system计算。

---

# 81. Disabled Contrast

disabled controls可适用不同要求。

但：

```text
scientific unavailable explanation
```

不能因 disabled styling不可读。

---

# 82. Focus Contrast

focus indicator必须足够可辨。

---

# 83. High Contrast / Forced Colors

如果 browser/platform支持：

至少进行 representative：

```text
forced-colors / high-contrast
```

engineering smoke test。

不要声称全面 Windows High Contrast certification。

---

# 84. Text Expansion

必须验证：

```text
English

zh-CN

long material names

long warnings

long status

long Tool names

long Artifact IDs
```

不会破坏关键 layout。

---

# 85. Fixed Height Audit

禁止关键文本容器使用固定高度导致：

```text
text clipping
```

尤其：

```text
warnings

limitations

errors

Findings

Report disclosures
```

---

# 86. Truncation

允许视觉 truncate：

前提：

```text
full content accessible
```

例如：

```text
tooltip

expand

details

accessible label
```

---

# 87. Accessible Tables

所有 HTML tables：

必须：

```text
header semantics

scope/association

caption/accessible name

selected state semantics where applicable
```

---

# 88. Data Grid Boundary

若自定义 virtual grid：

必须验证：

```text
keyboard

row/column semantics

focus

selection
```

若无法完整符合：

需提供 equivalent accessible fallback。

---

# 89. Mobile Data Tables

不能 silent-hide important scientific columns。

若 prioritized view：

必须可访问 full data。

---

# 90. Global Navigation Mobile

至少测试：

```text
open drawer

navigate all destinations

current state

close drawer

focus restore

back/forward
```

---

# 91. Workspace Mobile Navigation

测试：

```text
open context drawer

switch panel

open result

open Inspector

close Inspector

return to result
```

---

# 92. Fullscreen Viewer

必须：

```text
keyboard enter

keyboard exit

Escape if expected

focus restore

screen reader label
```

---

# 93. Viewer Toolbar Overflow

在：

```text
390x844

200% zoom
```

必须 bounded。

可使用：

```text
overflow menu
```

但不得隐藏 core status/warnings。

---

# 94. Error States

所有 error：

必须：

```text
understandable

actionable

keyboard accessible

screen-reader discoverable

context-preserving
```

---

# 95. Empty States

所有 empty state：

必须：

```text
meaningful

not decorative-only

have next action if applicable
```

---

# 96. Loading States

loading必须：

```text
identify what is loading

preserve context

not trap keyboard

announce important completion
```

---

# 97. Unsupported States

必须解释：

```text
what is unsupported

why

what remains possible
```

不能只灰掉。

---

# 98. Stale States

必须：

```text
typed

understandable

no latest rebinding
```

---

# 99. Partial States

必须明确：

```text
what succeeded

what failed

what remains usable
```

---

# 100. Accessibility of Scientific Limitations

科学 limitation：

必须：

```text
screen-reader readable

keyboard reachable

non-color

not hidden by tooltip-only
```

---

# 101. Accessibility of Validation Labels

support/validation/reproducibility badges：

必须有完整 text。

不得只：

```text
icons

abbreviations without accessible expansion
```

---

# 102. Tooltip Boundary

tooltip不能是访问必要科学信息的唯一方式。

---

# 103. Hover Boundary

任何 hover-only interaction：

必须有：

```text
keyboard/touch equivalent
```

---

# 104. Context Menu

若有右键 interaction：

必须有 standard UI equivalent。

---

# 105. Drag-and-Drop

若：

```text
Report ordering

panel ordering
```

依赖 drag：

必须有 keyboard alternative。

---

# 106. Pointer Gestures

复杂 multi-pointer gestures不得成为唯一操作方式。

---

# 107. 3D Pinch/Rotate

mobile 3D可支持 gestures。

但至少：

```text
reset

basic view

selection

fullscreen
```

有明确 controls。

---

# 108. Accessible Authentication/Secrets Boundary

当前没有 frontend DeepSeek key input。

必须继续：

```text
NO_FRONTEND_LLM_SECRET_INPUT = PASS
```

---

# 109. Security and Accessibility

无障碍修复不得：

```text
inject raw HTML

use dangerous innerHTML

expose secrets in aria-label

expose full sensitive payload to accessibility tree
```

---

# 110. Accessibility Tree Data Hygiene

Developer Details中的大型 raw JSON：

如果 collapsed：

不得无必要把全部数十 KB 放入 accessibility tree。

应按合理 disclosure模式。

---

# 111. Virtualization

如果 large list/table virtualized：

必须：

```text
not lose semantic access
```

若 current implementation已有：

验证即可。

不得为 accessibility安装新 dependency。

---

# 112. No New Accessibility Framework

必须：

```text
NEW_ACCESSIBILITY_DEPENDENCIES = 0
```

复用 current React/browser/test stack。

---

# 113. No New UI Framework

继续：

```text
NEW_UI_FRAMEWORKS = 0
```

---

# 114. No New Responsive Framework

不要安装：

```text
new CSS framework

mobile component library
```

---

# 115. Backend Freeze

必须：

```text
PHASE12_6_BACKEND_BEHAVIOR_CHANGES = 0
```

如果 accessibility目标需要 new backend domain capability：

```text
BLOCKED /
BACKEND_CAPABILITY_REVIEW_REQUIRED
```

---

# 116. API Freeze

必须：

```text
NEW_PUBLIC_API_FAMILIES = 0
```

---

# 117. Database Freeze

必须：

```text
NEW_DATABASE_TABLES = 0

NEW_DATABASE_COLUMNS = 0

NEW_DATABASE_MIGRATIONS = 0
```

---

# 118. Dependency Freeze

必须：

```text
NEW_PYTHON_DEPENDENCIES = 0

NEW_FRONTEND_DEPENDENCIES = 0

LOCKFILE_CHANGES = 0
```

---

# 119. Scientific Tool Freeze

必须：

```text
NEW_SCIENTIFIC_TOOLS = 0

NEW_SCIENTIFIC_ALGORITHMS = 0
```

---

# 120. Artifact Freeze

必须：

```text
NEW_ARTIFACT_FAMILIES = 0

ARTIFACT_CONTRACT_CHANGES = 0
```

---

# 121. Workspace Freeze

必须：

```text
WORKSPACE_DOMAIN_CONTRACT_CHANGES = 0

WORKSPACE_SELECTION_CONTRACT_CHANGES = 0
```

---

# 122. Interpretation Freeze

必须：

```text
SCIENTIFIC_CLAIM_CONTRACT_CHANGES = 0

SCIENTIFIC_EVIDENCE_CONTRACT_CHANGES = 0

INTERPRETATION_CONTRACT_CHANGES = 0
```

---

# 123. Report / Recipe Freeze

必须：

```text
REPORT_CONTRACT_CHANGES = 0

RECIPE_CONTRACT_CHANGES = 0

RECIPE_EXECUTION_AUTHORITY = NONE
```

---

# 124. Frontend Scientific Recomputation

必须：

```text
PHASE12_6_FRONTEND_SCIENTIFIC_RECOMPUTATION = 0
```

Accessibility alternatives：

必须来自相同 persisted payload。

---

# 125. No Alternate Science For Accessibility

禁止为了 accessible text：

frontend自行：

```text
calculate summary

calculate statistics

calculate extrema

calculate peaks

fit trend

infer interpretation
```

---

# 126. LLM Freeze

必须：

```text
PHASE12_6_NEW_LLM_CALL_SITES = 0

PHASE12_6_REAL_LLM_CALLS = 0
```

---

# 127. No AI Accessibility Description

不得调用 LLM：

```text
describe chart

describe structure

summarize scientific finding
```

作为 accessible alternative。

只用 deterministic persisted facts。

---

# 128. Scientific Color Mapping

必须：

```text
SCIENTIFIC_SERIES_COLOR_SEMANTIC_CHANGES = 0
```

Accessibility可以添加：

```text
patterns

labels

markers

table alternatives
```

若 current renderer支持且不改变 scientific identity。

---

# 129. Color Blindness

对于 categories/series：

至少保证：

```text
not color-only
```

可通过：

```text
legend labels

markers

line styles

selection text
```

等补充。

不得重新定义 scientific channel。

---

# 130. Phase 12-6 Acceptance IDs

必须从 canonical：

```text
docs/phase12/phase12_acceptance_and_test_plan.md
```

读取 exact：

```text
P12X6-A01
...
P12X6-A08
```

及 exact descriptions。

---

# 131. Acceptance IDs Immutable

必须：

```text
P12X6_EXPECTED = 8

IMPLEMENTED = 8

MISSING = 0

EXTRA = 0

DUPLICATE = 0

CONFLICTING = 0

SHORTHAND = 0
```

---

# 132. Reviewer Interpretation of P12X6 Scope

repository exact wording优先。

至少 equivalent覆盖：

```text
A.
Cross-product responsive closure

B.
Canonical mobile workflow closure

C.
Keyboard navigation
and focus-management closure

D.
Screen-reader semantics
and accessible-name closure

E.
Contrast / non-color /
touch-target closure

F.
200% zoom / reflow /
text-expansion / reduced-motion closure

G.
Scientific chart / 3D /
table accessibility alternatives

H.
cross-browser / scientific-authority /
regression / evidence /
lifecycle closure
```

---

# 133. Evidence Directory

建立：

```text
docs/phase12/evidence/
phase12_6_responsive_mobile_accessibility/
```

至少：

```text
baseline.txt

entry_gate.md

phase12_5_handoff_snapshot.json

surface_accessibility_inventory.json

responsive_surface_matrix.json

mobile_workflow_matrix.json

mobile_global_navigation.json

mobile_planner.json

mobile_workspace.json

mobile_viewer.json

mobile_findings_evidence.json

mobile_inspector.json

mobile_report_recipe.json

keyboard_navigation_matrix.json

tab_order_matrix.json

focus_visible_matrix.json

focus_restoration_matrix.json

dialog_focus_matrix.json

drawer_focus_matrix.json

bottom_sheet_focus_matrix.json

landmark_matrix.json

heading_matrix.json

accessible_name_matrix.json

form_label_matrix.json

async_status_matrix.json

screen_reader_matrix.json

touch_target_matrix.json

contrast_matrix.json

non_color_state_matrix.json

zoom_200_matrix.json

reflow_matrix.json

overflow_matrix.json

text_expansion_matrix.json

reduced_motion_matrix.json

chart_accessibility_matrix.json

table_alternative_matrix.json

three_d_accessibility_matrix.json

tooltip_hover_equivalence.json

drag_keyboard_equivalence.json

high_contrast_smoke.json

browser_matrix.json

before_after_surface_matrix.json

phase12_6_problem_closure.json

deferred_phase12_7_matrix.json

scientific_payload_nonchange.json

contract_nonchange.json

phase12_7_handoff.json

security.md

secret_scan.txt

manifest.json
```

---

# 134. Canonical Docs

至少新增/更新：

```text
docs/phase12/
phase12_6_responsive_mobile_accessibility.md

phase12_6_mobile_product_experience.md

phase12_6_keyboard_focus_accessibility.md

phase12_6_screen_reader_semantics.md

phase12_6_zoom_reflow_contrast_motion.md

phase12_6_scientific_visualization_accessibility.md

phase12_6_problem_closure.md

phase12_7_cross_product_validation_handoff.md

phase12_6_completion.md
```

复用 repository canonical naming优先。

---

# 135. Canonical Mobile Journeys

至少：

```text
M1
Open mobile product
→ navigate globally

M2
Data
→ start analysis

M3
Clarification
→ answer
→ Plan

M4
Run analysis
→ progress
→ result

M5
Open Workspace

M6
Switch Workspace panel

M7
Open chart result

M8
Open 3D result

M9
Finding
→ Evidence
→ Provenance

M10
Open Inspector bottom sheet

M11
Build Report

M12
Preview/finalize Report

M13
Open Recipe

M14
Handle unsupported/error/partial state
```

---

# 136. Canonical Keyboard Journeys

至少：

```text
K1
Global nav without mouse

K2
Prompt submit without mouse

K3
Clarification without mouse

K4
Plan disclosure without mouse

K5
Workspace navigation without mouse

K6
Viewer toolbar without mouse

K7
Finding→Evidence→Inspector without mouse

K8
Report source selection and ordering

K9
Finalize Report

K10
Dialog/Drawer/Bottom Sheet open-close-focus restore
```

---

# 137. Canonical Screen Reader Cases

至少 representative：

```text
Global navigation

Planner

Clarification

Execution status

Workspace Result

scientific warning/limitation

Finding

Evidence

Inspector

Report

Recipe
```

---

# 138. Canonical Zoom Cases

至少：

```text
1440x900 @ 200%

1280x720 @ 200%

390x844 normal
```

如果 browser automation无法真实 browser zoom：

使用 equivalent CSS-pixel viewport/reflow method，

并明确证据方法。

不得虚构 browser zoom。

---

# 139. Browser Matrix

必须：

```text
Chromium

Firefox

WebKit

Chromium 390x844
```

---

# 140. Browser Accessibility Checks

必须在可行范围自动检查：

```text
accessible names

focus visibility

keyboard path

ARIA relationships

unexpected overflow

touch targets

contrast

reduced motion

page errors

console errors
```

---

# 141. Automated Accessibility Tool Boundary

如果 repository已有 axe 或 equivalent：

可以复用。

如果没有：

不得新增 dependency。

使用：

```text
DOM assertions
browser tests
deterministic contrast tooling
manual evidence from existing harness
```

---

# 142. No “Zero Violations = Certified”

即使 automated scan：

```text
0 violations
```

也不能声称完整 accessibility certification。

---

# 143. Screen Reader Tooling Honesty

如果没有真正 NVDA/VoiceOver/JAWS automation：

不能写：

```text
NVDA PASS
```

只能写：

```text
SCREEN_READER_SEMANTIC_CONTRACT =
PASS_BY_DOM/ARIA_EVIDENCE
```

或 accurate equivalent。

---

# 144. Browser Accessibility Evidence Is Presentation Evidence

继续：

```text
BROWSER_ACCESSIBILITY_PASS
!=
SCIENTIFIC_VALIDATION
```

---

# 145. Scientific Payload Non-Change

before/after至少比较：

```text
Artifact IDs

Artifact versions

scientific values

units

selection identities

claims

evidence membership

warnings

limitations

Report source identity

Recipe identity
```

要求：

```text
SCIENTIFIC_SEMANTIC_DIFF = 0
```

---

# 146. Contract Non-Change

必须验证：

```text
AnalysisIntent unchanged

EligibilityResolution unchanged

AnalysisPlan unchanged

Workspace unchanged

Artifact unchanged

Claim/Evidence unchanged

Report unchanged

Recipe unchanged
```

---

# 147. Navigation Non-Change

Global IA保持：

```text
Home

Data

Analyses

Workspaces

Reports

Settings
```

12-6不重新设计 IA。

---

# 148. Workspace IA Non-Change

保持：

```text
Overview

Data

Analysis

Results

Findings

Evidence

Report

Advanced:
Provenance
Developer Details
```

或 current exact implemented authority。

---

# 149. Inspector Non-Change

保持：

```text
Summary

Scientific Details

Provenance
```

三层 architecture。

12-6只修 accessibility/mobile presentation。

---

# 150. Report Non-Change

保持：

```text
source authority

composition authority

mandatory disclosures

finalization

Recipe non-execution
```

---

# 151. Error Recovery Context

responsive/accessibility改动不得导致：

```text
error action hidden

context reset

source lost

prompt lost
```

---

# 152. Route Back/Forward

必须继续验证：

```text
active global destination

Workspace active panel

exact selection
```

不被 responsive nav破坏。

---

# 153. localStorage Authority

继续：

```text
LOCAL_STORAGE_SCIENTIFIC_AUTHORITY = NONE

LOCAL_STORAGE_CANONICAL_WORKSPACE_AUTHORITY = NONE
```

---

# 154. Security

必须：

```text
NO_PHASE12_6_ARBITRARY_CODE_EXECUTION = PASS

NO_PHASE12_6_ARTIFACT_HTML_EXECUTION = PASS

NO_PHASE12_6_ARTIFACT_JAVASCRIPT_EXECUTION = PASS

NO_PHASE12_6_IFRAME_EXECUTION = PASS

NO_PHASE12_6_EXTERNAL_ARTIFACT_URL_EXECUTION = PASS

NO_PHASE12_6_LLM_SCIENTIFIC_AUTHORITY = PASS

NO_PHASE12_6_RECIPE_EXECUTION = PASS

NO_PHASE12_6_FRONTEND_SCIENTIFIC_RECOMPUTATION = PASS

NO_PHASE12_6_SECRET_DISCLOSURE = PASS

NO_SECRET_PATTERN_HITS = PASS
```

---

# 155. Accessibility Labels Must Not Leak Secrets

aria-label / visually-hidden text：

不得包含：

```text
DEEPSEEK_KEY

authorization tokens

private paths

raw secret-bearing payload
```

---

# 156. Injection Safety

必须测试长/恶意：

```text
material title

prompt

Finding

Evidence

Report caption

Recipe field
```

在 screen-reader/hidden text path中仍然 inert。

---

# 157. Phase 12-7 Handoff

必须生成：

```text
Phase12_7CrossProductUXValidationHandoff
```

至少：

```text
Design System version/hash

Global IA state

Planner state

Workspace state

viewer state

Findings/Evidence/Inspector state

Report/Recipe state

responsive closure status

mobile closure status

keyboard closure status

screen-reader semantic status

touch-target status

contrast status

200% zoom/reflow status

reduced-motion status

chart/3D alternative status

remaining Phase 12-7 UX problem IDs

remaining P0/P1/P2/P3

canonical journey evidence

browser evidence

scientific-authority refs

known accepted accessibility limitations
```

---

# 158. Known Accessibility Limitation Registry

如果某 advanced scientific visualization：

无法做到完全 equivalent interaction，

必须建立：

```text
AcceptedAccessibilityLimitation
```

仅当：

```text
core scientific information remains accessible
through exact alternative
```

并记录：

```text
limitationId

surface

what is not accessible

accessible alternative

scientific consequence

user consequence

releaseBlocking

Phase12_7 verification requirement
```

---

# 159. Accessibility Limitation Cannot Hide Blocker

例如：

```text
keyboard cannot finalize Report
```

不能降级为 accepted limitation。

它是 release blocker。

---

# 160. Core Accessibility Blockers

以下默认必须 BLOCK：

```text
core workflow keyboard inaccessible

essential action unreachable on mobile

screen-reader cannot identify primary form controls

mandatory scientific warning inaccessible

Report finalize inaccessible

Inspector inaccessible

global nav inaccessible

focus trap

critical contrast failure

critical 200% zoom content loss
```

---

# 161. Non-Blocking Advanced Limitations

可能允许：

```text
some 3D spatial exploration
not fully screen-reader equivalent
```

前提：

```text
structured scientific summary
+
exact data alternative
+
selection details
```

可访问。

必须诚实披露。

---

# 162. Phase 12-6 Queue Admission

Entry PASS 后：

只创建：

```text
Phase 12-6
```

一个 task。

要求：

```text
TASK_BLOCK_COUNT = 1

ACTIVE_TASK = Phase 12-6

PHASE_12_7_EXECUTABLE_TASK_CREATED = NO

PHASE_13_EXECUTABLE_TASK_CREATED = NO
```

---

# 163. Persistent State

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

不得改 scientific facts。

---

# 164. ROADMAP

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
COMPLETE

Phase 12-4:
COMPLETE

Phase 12-5:
COMPLETE

Phase 12-6:
COMPLETE /
RESPONSIVE_MOBILE_ACCESSIBILITY_CLOSED

Phase 12-7:
REVIEWER_GATE /
AWAITING REVIEWER PROMPT

Phase 13:
ROADMAP_APPROVED /
NOT_QUEUED
```

---

# 165. First Required Output

执行开始后第一组必须输出：

```text
Phase 12-6 Entry Gate
+ Phase 12-5 Responsive/Accessibility Handoff
+ Cross-Product Accessibility Closure Admission
```

至少确认：

1. current HEAD；
2. origin/master；
3. branch；
4. worktree clean；
5. Phase 12-5 implementation SHA；
6. Phase 12-5 exact-SHA CI；
7. completion SHA；
8. archive SHA；
9. TASK_BLOCK_COUNT=0；
10. Phase 12-7 task absent；
11. Phase 13 task absent；
12. DS2 version/hash；
13. Phase 12-6 handoff resolves；
14. Global IA state；
15. Planner state；
16. Workspace state；
17. Viewer state；
18. Findings/Evidence/Inspector state；
19. Report/Recipe state；
20. exact Phase 12-6 UX problem IDs；
21. exact owned count；
22. exact P12X6-A01..A08；
23. mobile canonical viewport；
24. current browser matrix；
25. current accessibility tooling；
26. current touch target primitives；
27. current reduced-motion primitives；
28. current contrast tokens；
29. current responsive breakpoints；
30. current screen-reader semantics；
31. no new backend capability required；
32. no new API required；
33. no migration required；
34. no dependency required；
35. no scientific change required；
36. no LLM required。

成功：

```text
PHASE_12_6_ENTRY_GATE = PASS

PHASE_12_5_DEPENDENCY = VERIFIED

DESIGN_SYSTEM_2_0 =
VERIFIED_FOUNDATION

PHASE_11_SCIENTIFIC_AUTHORITY =
VERIFIED_READ_ONLY

PHASE_12_6_QUEUE_ADMISSION =
AUTHORIZED

PHASE_12_6_RESPONSIVE_CHANGE_AUTHORITY =
AUTHORIZED

PHASE_12_6_ACCESSIBILITY_CHANGE_AUTHORITY =
AUTHORIZED

PHASE_12_6_PRODUCT_INFORMATION_ARCHITECTURE_CHANGE_AUTHORITY =
NONE

PHASE_12_6_SCIENTIFIC_CHANGE_AUTHORITY =
NONE

PHASE_12_6_BACKEND_CHANGE_AUTHORITY =
NONE

PHASE_12_6_READINESS =
READY_FOR_RESPONSIVE_MOBILE_ACCESSIBILITY_CLOSURE
```

---

# 166. Required Execution Sequence

严格：

```text
verify Phase 12-5 lifecycle

→ verify 12-6 handoff

→ verify DS2

→ verify Phase 11 authority

→ load exact 12-6 UX problems

→ load exact P12X6 acceptance IDs

→ inventory every current responsive/accessibility surface

→ admit exactly one 12-6 task

→ snapshot current desktop/mobile state

→ snapshot keyboard/focus baseline

→ snapshot contrast/touch/zoom baseline

→ fix Global shell responsive/mobile gaps

→ fix Planner responsive/mobile gaps

→ fix Workspace responsive/mobile gaps

→ fix scientific viewer responsive gaps

→ fix Findings/Evidence mobile gaps

→ fix Inspector bottom-sheet gaps

→ fix Report/Recipe mobile gaps

→ close keyboard gaps

→ close tab-order gaps

→ close focus-visible gaps

→ close focus-restoration gaps

→ close semantic landmark/heading gaps

→ close accessible-name/form-label gaps

→ close async status announcement gaps

→ close non-color state gaps

→ close touch-target gaps

→ close contrast gaps

→ close 200% zoom/reflow gaps

→ close text expansion gaps

→ close reduced-motion gaps

→ provide chart/table alternatives

→ provide 3D structured alternatives

→ validate high-contrast representative cases

→ validate no scientific payload change

→ close exact 12-6-owned UX problems

→ classify any accepted non-blocking advanced limitations

→ keep 12-7 problem(s) owned/open

→ generate Phase 12-7 handoff

→ capture AFTER evidence

→ run browser matrix

→ run accessibility focused tests

→ run full frontend/backend regression

→ run service-backed integration

→ run retained Linux/Windows scientific replay

→ run Phase 11 integrity

→ run security/evidence/secret checks

→ create implementation commit

→ push

→ WAIT FOR IMPLEMENTATION EXACT-SHA CI

→ if PASS:
   append completion record

→ completion commit/push directly

→ remove only Phase 12-6 task

→ archive commit/push directly

→ verify queue empty

→ stop
```

---

# 167. Implementation Commit Allowed

可以包含：

```text
responsive frontend CSS/components

mobile presentation changes

ARIA/semantic improvements

focus-management changes

keyboard interaction fixes

responsive navigation behavior

responsive Workspace/viewer behavior

accessible table/text alternatives

screen-reader presentation adapters

contrast fixes

touch-target fixes

reduced-motion fixes

frontend tests

browser evidence tooling

accessibility evidence tooling

docs

persistent state

TASK admission
```

---

# 168. Implementation Commit Forbidden

禁止：

```text
new scientific Tool

new algorithm

new Artifact family

new scientific computation

new Planner semantics

new Workspace authority

new selection semantics

new Finding/Evidence contract

new Report contract

new Recipe contract

new API family

new DB migration

new accessibility framework dependency

new UI framework

LLM accessibility generation

Phase 12-7 implementation

completion result
```

---

# 169. Accessibility Bug vs Domain Bug

如果发现某 accessibility问题：

只能通过修改 scientific/domain contract才能解决：

必须：

```text
BLOCKED /
DOMAIN_AUTHORITY_REDESIGN_REQUIRED
```

不要在 UX phase偷偷改 contract。

---

# 170. Backend Regression

必须：

```text
uv run python -m pytest -q
```

要求：

```text
>= Phase 12-5 final canonical backend floor
```

从 repository动态读取。

---

# 171. Frontend Regression

必须：

```text
npm --prefix apps/web test
```

要求：

```text
>= Phase 12-5 final canonical frontend floor
```

---

# 172. Focused Accessibility Tests

应新增/运行至少覆盖：

```text
global navigation

Planner

clarification

Workspace

viewer toolbar

Finding/Evidence

Inspector

Report

Recipe

mobile

focus restoration

touch target

non-color state

reduced motion
```

---

# 173. Typecheck

必须：

```text
npm --prefix apps/web run typecheck
= PASS
```

---

# 174. Build

必须：

```text
npm --prefix apps/web run build
= PASS
```

---

# 175. Lock

必须：

```text
uv lock --check = PASS

LOCKFILE_CHANGES = 0
```

---

# 176. Diff

必须：

```text
git diff --check = PASS
```

---

# 177. Service-Backed Regression

Implementation exact-SHA CI继续要求：

```text
PostgreSQL

Redis

MinIO
```

PASS。

---

# 178. Linux / Windows Replay

若 current required matrix仍包含：

```text
Linux scientific replay

Windows scientific replay
```

必须 PASS。

---

# 179. Browser CI

必须：

```text
Chromium PASS

Firefox PASS

WebKit PASS

390x844 PASS
```

---

# 180. Browser Accessibility Evidence

至少：

```text
keyboard journey PASS

focus PASS

touch PASS

reflow PASS

contrast PASS

reduced motion PASS

accessible-name PASS

unexpected overflow = 0
```

在 required canonical cases。

---

# 181. npm Audit

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
PASS / clean
```

---

# 182. Exact-SHA CI

implementation push 后：

必须：

```text
WAIT FOR IMPLEMENTATION EXACT-SHA CI
```

required jobs全部：

```text
success
```

---

# 183. Minimum Exact-SHA CI

至少：

```text
Backend Unit

Frontend Tests

Typecheck

Build

Phase 12-6 accessibility evidence

Chromium

Firefox

WebKit

390x844

PostgreSQL/Redis/MinIO

retained Linux replay

retained Windows replay

Phase 11 authority integrity

Phase 12 contract integrity

security / secret scan
```

---

# 184. Failed Candidate

若失败：

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

rewrite history

delete accessibility test

remove mobile coverage

lower touch target threshold

hide contrast failure

remove keyboard requirement

change UX problem ownership

change scientific contract
```

---

# 185. Completion Record

只有 implementation exact-SHA CI PASS：

向：

```text
results.md
```

append：

```text
Phase 12-6 Responsive / Mobile /
Accessibility Closure Result
```

然后：

```text
commit
push
```

不等待 completion CI。

---

# 186. Queue Archive

completion push后：

只删除：

```text
Phase 12-6 TASK block
```

不得创建：

```text
Phase 12-7 executable task
```

然后：

```text
commit
push
```

不等待 archive CI。

---

# 187. Lifecycle Terminology

最终只能：

```text
IMPLEMENTATION_VERIFIED_BY_EXACT_SHA_CI

COMPLETION_RECORDED

QUEUE_ARCHIVED
```

除非 completion/archive另有独立 exact-SHA CI。

---

# 188. Mandatory Result Markers

必须：

```text
PHASE12_6_PRODUCTION_UI_CHANGES =
YES_RESPONSIVE_MOBILE_ACCESSIBILITY

PHASE12_6_BACKEND_BEHAVIOR_CHANGES = 0

PHASE12_6_SCIENTIFIC_BEHAVIOR_CHANGES = 0

PHASE12_6_GLOBAL_IA_CHANGES = 0

PHASE12_6_PLANNER_SEMANTIC_CHANGES = 0

PHASE12_6_WORKSPACE_AUTHORITY_CHANGES = 0

PHASE12_6_SELECTION_SEMANTIC_CHANGES = 0

PHASE12_6_ARTIFACT_CONTRACT_CHANGES = 0

PHASE12_6_INTERPRETATION_CONTRACT_CHANGES = 0

PHASE12_6_REPORT_CONTRACT_CHANGES = 0

PHASE12_6_RECIPE_CONTRACT_CHANGES = 0

PHASE12_6_NEW_SCIENTIFIC_TOOLS = 0

PHASE12_6_NEW_SCIENTIFIC_ALGORITHMS = 0

PHASE12_6_NEW_ARTIFACT_FAMILIES = 0

PHASE12_6_NEW_DATAPROFILE_VERSION = 0

PHASE12_6_NEW_ANALYSISPLAN_VERSION = 0

PHASE12_6_NEW_DATABASE_MIGRATIONS = 0

PHASE12_6_NEW_PUBLIC_API_FAMILIES = 0

PHASE12_6_NEW_DEPENDENCIES = 0

PHASE12_6_LOCKFILE_CHANGES = 0

PHASE12_6_NEW_LLM_CALL_SITES = 0

PHASE12_6_REAL_LLM_CALLS = 0

PHASE12_6_FRONTEND_SCIENTIFIC_RECOMPUTATION = 0
```

---

# 189. Responsive Markers

必须：

```text
RESPONSIVE_SURFACE_UNCLASSIFIED = 0

MOBILE_CORE_WORKFLOWS_COMPLETE = YES

UNEXPECTED_PAGE_HORIZONTAL_OVERFLOW = 0

MOBILE_GLOBAL_NAVIGATION = PASS

MOBILE_PLANNER = PASS

MOBILE_WORKSPACE = PASS

MOBILE_SCIENTIFIC_VIEWERS = PASS

MOBILE_FINDINGS_EVIDENCE = PASS

MOBILE_INSPECTOR = PASS

MOBILE_REPORT_RECIPE = PASS
```

---

# 190. Accessibility Markers

必须：

```text
CORE_KEYBOARD_WORKFLOWS = PASS

VISIBLE_FOCUS_REQUIRED_CASES = PASS

FOCUS_RESTORATION_REQUIRED_CASES = PASS

ACCESSIBLE_NAME_REQUIRED_CASES = PASS

FORM_LABEL_REQUIRED_CASES = PASS

HEADING_LANDMARK_REQUIRED_CASES = PASS

ASYNC_STATUS_ANNOUNCEMENTS = PASS

STATUS_COLOR_ONLY_MEANING = 0

REQUIRED_TOUCH_TARGET_FAILURES = 0

CONTRAST_REQUIRED_FAILURES = 0

ZOOM_200_REQUIRED_FAILURES = 0

REFLOW_REQUIRED_FAILURES = 0

REDUCED_MOTION_REQUIRED_CASES = PASS

FULL_PRODUCT_ACCESSIBILITY_ENGINEERING_CLOSURE = YES
```

注意：

```text
FORMAL_ACCESSIBILITY_CERTIFICATION = NO
```

---

# 191. Scientific Visualization Accessibility Markers

必须：

```text
CHART_ACCESSIBLE_DATA_ALTERNATIVE_REQUIRED_CASES = PASS

THREE_D_STRUCTURED_ALTERNATIVE_REQUIRED_CASES = PASS

PLOTLY_NUMERIC_SCIENTIFIC_AUTHORITY = NONE

WEBGL_NUMERIC_SCIENTIFIC_AUTHORITY = NONE

ACCESSIBLE_ALTERNATIVE_SCIENTIFIC_RECOMPUTATION = 0

SCIENTIFIC_SERIES_COLOR_SEMANTIC_CHANGES = 0
```

---

# 192. Scientific Honesty Markers

必须：

```text
SUPPORTED_EQUALS_VALIDATED = NO

MAPPING_ONLY_VISUAL_UPGRADE = 0

NOT_APPLICABLE_VISUAL_UPGRADE = 0

V4_VISUAL_FABRICATION = 0

BROWSER_PASS_EQUALS_SCIENTIFIC_PASS = NO

SERVICE_PASS_EQUALS_SCIENTIFIC_PASS = NO

ACCESSIBILITY_PASS_EQUALS_SCIENTIFIC_PASS = NO

SCREENSHOT_NUMERIC_SCIENTIFIC_AUTHORITY = NONE

FRONTEND_SCIENTIFIC_AUTHORITY = NONE
```

---

# 193. Baseline Markers

必须：

```text
REGISTRY_BEFORE_12_6 = 62
REGISTRY_AFTER_12_6 = 62

DATAPROFILE_BEFORE_12_6 = 2.4
DATAPROFILE_AFTER_12_6 = 2.4

MIGRATION_BEFORE_12_6 =
0007_phase10m1_workspace_domain

MIGRATION_AFTER_12_6 =
0007_phase10m1_workspace_domain
```

---

# 194. UX Problem Markers

必须：

```text
PHASE12_6_OWNED_PROBLEMS =
<exact repository IDs>

PHASE12_6_OWNED_PROBLEM_COUNT =
<actual>

PHASE12_6_OWNED_PROBLEMS_CLOSED =
<same>

PHASE12_6_OWNED_PROBLEMS_OPEN = 0

NEW_P0_INTRODUCED_BY_12_6 = 0

NEW_P1_INTRODUCED_BY_12_6 = 0
```

---

# 195. Acceptance Marker

必须：

```text
P12X6_ACCEPTANCE = 8/8
```

exact IDs/descriptions来自 canonical plan。

---

# 196. Required results.md Structure

至少：

# Phase 12-6 Responsive / Mobile / Accessibility Closure Result

1. Conclusion
2. Phase 12-5 Baseline
3. Entry Gate
4. Repository State
5. DS2 Authority
6. Phase 11 Scientific Authority
7. Phase 12-6 Handoff Integrity
8. UX Problem Ownership
9. Production Behavior Changes
10. Responsive Surface Inventory
11. Global Shell Responsive Closure
12. Global Mobile Navigation
13. Data Mobile Experience
14. Planner Mobile Experience
15. Clarification Mobile Experience
16. Plan Mobile Experience
17. Execution Mobile Experience
18. Workspace Mobile Experience
19. Result Mobile Experience
20. Scientific Viewer Mobile Experience
21. Findings Mobile Experience
22. Evidence Mobile Experience
23. Inspector Bottom Sheet
24. Provenance Mobile Experience
25. Report Mobile Experience
26. Recipe Mobile Experience
27. Keyboard Navigation
28. Tab Order
29. Focus Visible
30. Focus Restoration
31. Dialog Focus
32. Drawer Focus
33. Bottom Sheet Focus
34. Landmarks
35. Heading Structure
36. Accessible Names
37. Forms / Labels / Errors
38. Async Status Announcements
39. Screen Reader Semantic Contract
40. Non-Color State
41. Touch Targets
42. Contrast
43. High Contrast / Forced Colors Smoke
44. 200% Zoom
45. Reflow
46. Horizontal Overflow
47. Text Expansion
48. Reduced Motion
49. Tables
50. Chart Accessibility
51. Chart Data Alternatives
52. 3D Accessibility
53. 3D Structured Alternatives
54. Tooltips / Hover Equivalence
55. Drag / Keyboard Equivalence
56. Pointer Gesture Alternatives
57. Error / Empty / Loading States
58. Unsupported / Stale / Partial States
59. Scientific Warning Accessibility
60. Validation/Support Label Accessibility
61. Security / Accessibility Tree Hygiene
62. Scientific Payload Non-Change
63. Contract Non-Change
64. Global IA Non-Change
65. Workspace IA Non-Change
66. Inspector Architecture Non-Change
67. Report/Recipe Authority Non-Change
68. Phase 12-6 Problem Closure
69. Accepted Accessibility Limitations
70. Remaining Phase 12-7 UX Problems
71. Phase 12-7 Handoff
72. Browser Matrix
73. Accessibility Focused Tests
74. Backend Regression
75. Frontend Regression
76. Typecheck
77. Build
78. Lock
79. Service Regression
80. Linux/Windows Replay
81. npm Audit
82. Evidence Inventory
83. Evidence Manifest
84. Security
85. Secret Scan
86. Files Changed
87. Acceptance Registry
88. Implementation Commit
89. Implementation CI
90. Failed Candidates
91. Completion Record
92. Queue Archive
93. Queue State
94. Phase 12-7 Reviewer Gate
95. Final Repository State

---

# 197. PASS Gate

只有全部满足：

```text
Phase 12-5 PASS

Phase 12-5 implementation exact-SHA CI PASS

Phase 12-5 queue archived


HEAD == origin/master at entry

worktree clean

TASK_BLOCK_COUNT = 0


Phase 12-6 handoff resolves

exact 12-6 UX problems resolve

exact P12X6 acceptance IDs resolve


DS2 authority resolves

Phase 11 authority resolves

Registry = 62

DataProfile = 2.4

migration = 0007


all current surfaces responsive-classified

responsive unclassified = 0

accessibility unclassified = 0


mobile Global nav PASS

mobile Planner PASS

mobile Workspace PASS

mobile Viewer PASS

mobile Findings/Evidence PASS

mobile Inspector PASS

mobile Report/Recipe PASS


core keyboard workflows PASS

focus visible PASS

focus restoration PASS

unintentional keyboard trap = 0

accessible name required cases PASS

form labels PASS

heading/landmark semantics PASS

async status PASS


non-color state PASS

touch target failures = 0

contrast required failures = 0

200% zoom required failures = 0

reflow required failures = 0

unexpected page overflow = 0

reduced motion PASS


chart accessible alternatives PASS

3D structured alternatives PASS

accessibility alternative scientific recomputation = 0


all 12-6-owned UX problems closed

new P0 = 0

new P1 = 0


accepted accessibility limitations
are explicit and non-release-blocking

Phase 12-7 remaining problem set preserved


Global IA unchanged

Planner semantics unchanged

Workspace authority unchanged

selection semantics unchanged

Artifact contracts unchanged

Claim/Evidence contracts unchanged

Report/Recipe contracts unchanged

scientific behavior unchanged


new scientific Tool = 0

new scientific algorithm = 0

new Artifact family = 0

DataProfile version unchanged

AnalysisPlan unchanged

migration unchanged

new API family = 0

new dependency = 0

lockfile change = 0

new LLM call site = 0

real LLM calls = 0

frontend scientific recomputation = 0


Chromium PASS

Firefox PASS

WebKit PASS

390x844 PASS


backend >= dynamic Phase 12-5 floor

frontend >= dynamic Phase 12-5 floor

typecheck PASS

build PASS

lock PASS

diff PASS

PostgreSQL/Redis/MinIO PASS

retained Linux replay PASS

retained Windows replay PASS

Phase 11 integrity PASS

evidence integrity PASS

security PASS

secret scan PASS


P12X6 = 8/8


implementation exact-SHA CI PASS

completion record committed/pushed

queue archive committed/pushed


TASK_BLOCK_COUNT = 0

Phase 12-7 task absent

Phase 13 task absent

HEAD == origin/master

worktree clean
```

才允许：

```text
Phase 12-6 = PASS
```

---

# 198. BLOCKED — Phase 12-5 Incomplete

如果：

```text
Phase 12-5 not PASS

implementation CI not PASS

queue not archived
```

必须：

```text
BLOCKED /
PHASE_12_5_DEPENDENCY_NOT_CLOSED
```

---

# 199. BLOCKED — Core Mobile Workflow Failure

如果以下任意 core path：

```text
analysis creation

Workspace exploration

Finding→Evidence

Report finalization
```

在 390x844 无法完成：

不能 PASS。

---

# 200. BLOCKED — Core Keyboard Failure

如果用户不用鼠标无法完成：

```text
analysis

Workspace navigation

Report finalization
```

不能 PASS。

---

# 201. BLOCKED — Mandatory Warning Inaccessible

如果 scientific warning / limitation：

```text
not screen-reader accessible

not keyboard reachable

color-only

tooltip-only
```

不能 PASS。

---

# 202. BLOCKED — Focus Trap

存在 unintentional keyboard trap：

不能 PASS。

---

# 203. BLOCKED — Critical Contrast

如果 primary content/action存在 unresolved critical contrast failure：

不能 PASS。

---

# 204. BLOCKED — 200% Zoom Loses Essential Content

若：

```text
primary action

warning

navigation

Report finalize

Inspector content
```

在 required zoom/reflow case消失：

不能 PASS。

---

# 205. BLOCKED — Scientific Accessibility Recompute

如果为了 accessible alternative：

frontend重新计算 science：

必须：

```text
BLOCKED /
SCIENTIFIC_AUTHORITY_VIOLATION
```

---

# 206. BLOCKED — Mobile Authority Changed

如果为 mobile UX：

引入：

```text
localStorage scientific authority

new Workspace identity

latest Artifact binding

fuzzy selection
```

不能 PASS。

---

# 207. BLOCKED — Accessibility Requires Domain Redesign

如果必须修改：

```text
Artifact contract

Claim contract

Workspace contract

Report contract

scientific algorithm
```

才能完成：

必须：

```text
BLOCKED /
DOMAIN_REVIEW_REQUIRED
```

---

# 208. BLOCKED — Owned Problems Remain

如果：

```text
PHASE12_6_OWNED_PROBLEMS_OPEN > 0
```

不能 PASS。

---

# 209. Non-Blockers

以下可接受：

```text
some advanced 3D interaction
not screen-reader spatially equivalent

some chart direct manipulation
not fully screen-reader navigable
```

前提：

```text
same scientific information
is available via structured accessible alternative
```

并且 limitation：

```text
explicit

non-release-blocking

handed to 12-7
```

---

# 210. Final Successful State

成功后：

```text
Phase 12-6:
PASS /
RESPONSIVE_MOBILE_ACCESSIBILITY_CLOSED /
QUEUE_ARCHIVED

Phase 12:
IN_PROGRESS /
PRODUCT_EXPERIENCE_IMPLEMENTATION_COMPLETE /
AWAITING_FINAL_UX_VALIDATION

Phase 12-7:
REVIEWER_GATE /
AWAITING REVIEWER PROMPT

Phase 13:
ROADMAP_APPROVED /
NOT_QUEUED /
NOT_EXECUTABLE

TASK_BLOCK_COUNT = 0

PHASE_12_7_EXECUTABLE_TASK_CREATED = NO

PHASE_13_EXECUTABLE_TASK_CREATED = NO
```

---

# 211. Meaning of Phase 12-6 Completion

可以说：

```text
The implemented Phase 12 product experience has been
closed across responsive layouts, the canonical mobile
workflows, keyboard interaction, focus management,
screen-reader semantics, non-color state communication,
touch targets, contrast, zoom/reflow and reduced-motion
requirements.

Scientific charts and 3D surfaces expose structured
accessible alternatives where direct visual interaction
cannot be made semantically equivalent, without creating
new frontend scientific authority.
```

---

# 212. What Completion Does NOT Mean

不能说：

```text
Formal WCAG certification is complete.

All 3D spatial interaction is screen-reader equivalent.

All scientific visualization interactions are fully
accessible in identical form.

Phase 12 is complete.

The product is release-ready.

Initial Release is complete.
```

---

# 213. Phase 12-7 State

最终：

```text
Phase 12-7:
REVIEWER_GATE /
AWAITING REVIEWER PROMPT

PHASE_12_7_EXECUTABLE_TASK_CREATED = NO
```

---

# 214. Stop Rule

完成后立即停止。

不得：

```text
perform final Phase 12 closure

change remaining UX problem ownership

start Phase 13

run canonical Phase 13 demonstrations

perform release acceptance
```

返回 reviewer：

```text
Phase 12-6 final result

implementation SHA

implementation exact-SHA CI

completion SHA

archive SHA

exact 12-6 UX problem closure

P12X6 8/8

responsive surface coverage

canonical mobile journey results

keyboard journey results

focus/focus-restoration results

screen-reader semantic evidence

touch-target results

contrast results

200% zoom/reflow results

reduced-motion results

chart accessibility alternatives

3D accessibility alternatives

accepted accessibility limitations

scientific payload non-change proof

contract non-change proof

browser evidence

remaining Phase 12-7 problem ownership

Phase 12-7 handoff state
```

然后等待 reviewer。


---END---
