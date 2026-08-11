---TASK---
 状态：处理中

# Phase 13-1 Release-Critical Product-Entry Fix-Forward

由 Phase 13-2 real-user entry evidence 触发，关闭且只关闭：

```text
P13-RF-001 profile/planner compatibility drift
P13-RF-002 XRD user-input authority conflict
P13-RF-003 phonon/BZ intent coverage gap
P13-RF-004 volumetric canonical prompt mismatch
```

必须建立永久 `CANONICAL_PRODUCT_ENTRY_SLICE_GATE`，要求七个 sealed demo
均通过真实 parser -> DataProfile -> AnalysisIntent -> Eligibility -> Planner ->
PlanValidator，并在 Job 创建前停止。不得新增 science、Tool、Artifact、schema
version、migration、API family、dependency、provider 或 LLM call site；不得执行
Phase 13-2 full E2E。完成后保留历史 Phase 13-2 失败块且不创建 rerun task。

---END---

---TASK---
 状态：失败

# Phase 13-2 Reviewer Prompt

# Seven Canonical Real-User E2E Demonstrations

你现在执行：

# Phase 13-2：Seven Canonical Real-User E2E Demonstrations

中文：

# 七条最终真实用户端到端科学分析演示 + 负向用户场景验证

本阶段属于：

```text
Phase 13:
Final Product Closure
```

当前序列：

```text
13-0
Final Fact Alignment
+ Release Scope Seal
= COMPLETE

13-0 Correction
Clarification Fact Alignment
= COMPLETE

13-1
Release-Critical Integration Gap Closure
/ Zero-Gap Verification Closure
= MUST BE VERIFIED AT ENTRY

13-2
Seven Canonical Real-User E2E Demonstrations
= CURRENT AUTHORIZED PHASE

13-3
Documentation + Reproducibility Package

13-4
Targeted Final Product Polish

13-5
Final Regression + Release Acceptance

13-6
Final Archive + Presentation Package
```

---

# 0. Mission

Phase 13-2 是第一次真正执行：

```text
REAL USER ENTRY
→ REAL PRODUCT PATH
→ REAL SCIENTIFIC RUNTIME
→ REAL PERSISTENCE
→ REAL SCIENTIFIC OUTPUT
→ REAL WORKSPACE
→ REAL INTERPRETATION
→ REAL REPORT / RECIPE
```

它不是：

```text
preflight
fixture inspection
contract inspection
adapter unit testing
Workspace screenshot demo
Artifact injection
handcrafted Plan demonstration
```

本阶段必须证明：

> 一个不知道内部 Tool ID、Artifact ID、Plan schema、Workspace ID 的真实用户，仅通过产品允许的用户界面和自然语言入口，能够完成 Initial Release 所承诺的材料科学分析工作流。

---

# 1. Fundamental Definition

Phase 13-2 中：

```text
E2E
=
actual user-facing entry
+
actual product orchestration
+
actual QueueWorkerRuntime
+
actual registered Adapter
+
actual service-backed persistence
+
actual persisted Artifact
+
actual Workspace
+
actual downstream interpretation/report flow
```

任何缺少其中 required layer 的所谓 E2E：

```text
NOT_ACCEPTABLE_AS_PHASE13_2_PASS
```

---

# 2. Mandatory Phase 13-1 Dependency

执行前必须从真实 Git/repository 验证：

```text
Phase 13-1 =
PASS /
ZERO_GAP_VERIFIED /
RELEASE_CRITICAL_INTEGRATION_SEAMS_CLOSED
```

并确认：

```text
RELEASE_BLOCKERS = 0

RELEASE_CRITICAL_INTEGRATION_GAPS = 0

INTEGRATION_SEAMS_GAP_FOUND = 0

DEMO_PREFLIGHT_COMPLETE = 7/7

DEMO_PREFLIGHT_BLOCKED = 0
```

否则：

```text
PHASE_13_2_ENTRY_GATE = BLOCKED

reason =
PHASE_13_1_NOT_CLOSED
```

立即停止。

---

# 3. Phase 13-1 Lifecycle

必须动态取得：

```text
PHASE13_1_IMPLEMENTATION_SHA

PHASE13_1_EXACT_SHA_CI_RUN

PHASE13_1_EXACT_SHA_CI_RESULT

PHASE13_1_COMPLETION_SHA

PHASE13_1_QUEUE_ARCHIVE_SHA
```

不得根据 Prompt 猜测。

---

# 4. Repository Entry State

必须：

```text
branch = master

HEAD == origin/master

worktree = clean

TASK_BLOCK_COUNT = 0

Phase 13-2 task absent

Phase 13-3 task absent

Phase 14 absent
```

---

# 5. Current Release Authorities

必须重新验证：

```text
INITIAL_RELEASE_FACT_MODEL_HASH =
e0248d502e4a442bb9596a8d2f6fe6d7fdefe61c41121ae08736734ce4004a06
```

以及 corrected current：

```text
INITIAL_RELEASE_SCOPE_BASELINE_HASH =
93dea4a2b0bf31215ab2af1952b16ac47b20b7ed9b111bb2fb60ef70dd431627
```

以及：

```text
PHASE12_PRODUCT_EXPERIENCE_BASELINE_HASH =
29936236efe74a82ad97507385839aa4f5692d26b496292af3172940647973d4
```

如果 current repository authority不同：

使用 actual canonical，并披露原因。

---

# 6. Scientific Baseline

必须保持：

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

# 7. Clarification Authority

必须保持 corrected authority：

```text
MAX_CLARIFICATION_ROUNDS = 1

MAX_CLARIFICATION_QUESTIONS = 3

SECOND_CLARIFICATION_ROUND =
TYPED_FAILURE
```

任何测试、demo 或 user script：

不得期待第二轮 clarification。

---

# 8. Phase 13-2 Handoff

必须读取 canonical：

```text
Phase13_2RealUserE2EEntryHandoff
```

或 repository exact equivalent。

必须包含：

```text
7 demo IDs

fixture records

checksums

canonical prompts

alternate bounded prompts

personas

negative paths

provider modes

no-injection policy

real persistence/runtime policy

required services

expected capability families

expected Artifact families

Workspace expectations

interpretation applicability

Finding/Evidence applicability

Report/Recipe expectations

known limitations

P13X2 acceptance IDs
```

---

# 9. Handoff Missing

若 handoff：

```text
missing
conflicting
stale
does not match corrected Scope Baseline
```

则：

```text
BLOCKED /
PHASE13_2_HANDOFF_INVALID
```

---

# 10. Reviewer Authorization

本 Prompt 授权：

```text
AUTHORIZED_PHASE = Phase 13-2

AUTHORIZED_MODE =
REAL_USER_E2E_EXECUTION

MAX_PHASES_EXECUTED = 1
```

不授权：

```text
Phase 13-3
Phase 13-4
Phase 13-5
Phase 13-6
Phase 14
```

---

# 11. Phase 13-2 Production Change Authority

默认：

```text
PHASE13_2_PRODUCTION_CODE_CHANGE_AUTHORITY = NONE
```

本阶段主要任务是：

```text
EXECUTE
OBSERVE
MEASURE
TRACE
PERSIST
VALIDATE
DOCUMENT
```

不是：

```text
FIX
REDESIGN
EXPAND
```

---

# 12. Discovery Rule

如果真实 E2E 发现产品缺陷：

必须分类：

```text
RELEASE_BLOCKER

RELEASE_CRITICAL_INTEGRATION_DEFECT

TARGETED_POLISH_DEFECT

DOCUMENTATION_DEFECT

NONBLOCKING_LIMITATION

SCIENTIFIC_DEFECT
```

---

# 13. Do Not Silently Fix

本阶段原则：

```text
discover defect
→ preserve evidence
→ classify
→ continue only where safe
→ return reviewer
```

禁止：

```text
discover
→ patch production
→ rerun
→ report only final PASS
```

---

# 14. Exception — Test Harness Defect

允许修：

```text
test-only harness defect

evidence generator defect

browser locator defect

fixture manifest typo
```

前提：

```text
production behavior unchanged
```

并必须披露。

---

# 15. Scientific Defect Rule

如果观察到：

```text
scientific value wrong

scientific method wrong

unit wrong

semantic claim wrong

Artifact scientific payload wrong
```

必须：

```text
BLOCKED /
SCIENTIFIC_RELEASE_DEFECT_REVIEW_REQUIRED
```

不得在 13-2修改算法。

---

# 16. Real-User Rule

normal user path中：

用户/automation不得知道：

```text
Tool ID

Artifact ID

Job ID

Plan ID

Workspace ID

internal Adapter class

database primary key
```

这些仅允许用于：

```text
post-run audit
```

---

# 17. Locator Rule

browser automation主流程优先使用：

```text
accessible role

accessible name

visible label

visible text

user-facing route
```

不得以内部 ID作为用户行为前置条件。

---

# 18. Natural-Language Rule

适用 demo 必须从：

```text
natural-language user prompt
```

进入。

不得：

```text
click internal Tool shortcut
```

绕过 Planner。

---

# 19. No Handcrafted AnalysisPlan

必须：

```text
HANDCRAFTED_ANALYSISPLAN_INJECTION = 0
```

---

# 20. No Handcrafted Job

```text
HANDCRAFTED_JOB_INJECTION = 0
```

---

# 21. No Handcrafted ToolCall

```text
HANDCRAFTED_TOOLCALL_INJECTION = 0
```

---

# 22. No Handcrafted Artifact

```text
HANDCRAFTED_ARTIFACT_INJECTION = 0
```

---

# 23. No Handcrafted Workspace

```text
HANDCRAFTED_WORKSPACE_INJECTION = 0
```

---

# 24. No Handcrafted Interpretation

必须：

```text
HANDCRAFTED_INTERPRETATION_INJECTION = 0
```

---

# 25. No Handcrafted Finding

```text
HANDCRAFTED_FINDING_INJECTION = 0
```

---

# 26. No Handcrafted Evidence

```text
HANDCRAFTED_EVIDENCE_INJECTION = 0
```

---

# 27. No Handcrafted Report

```text
HANDCRAFTED_REPORT_INJECTION = 0
```

---

# 28. No Handcrafted Recipe

```text
HANDCRAFTED_RECIPE_INJECTION = 0
```

---

# 29. No Test-Only Planner Shortcut

禁止：

```text
if phase13_demo:
    return predetermined_plan
```

---

# 30. No Test-Only Eligibility Shortcut

禁止：

```text
if fixture == demo_fixture:
    force_ready
```

---

# 31. Real Persistence

必须：

```text
REAL_PERSISTENCE_USED = YES
```

使用 current required：

```text
PostgreSQL
Redis
MinIO
```

---

# 32. Real Queue

必须：

```text
REAL_QUEUE_USED = YES
```

---

# 33. Real Worker Runtime

必须：

```text
REAL_QUEUE_WORKER_RUNTIME_USED = YES
```

---

# 34. Registered Adapter

每 scientific step：

必须：

```text
registered Tool
→ registered Adapter
```

---

# 35. Direct Adapter Call

作为 product E2E主路径：

```text
DIRECT_ADAPTER_CALL = FORBIDDEN
```

可作为 diagnostic evidence，但：

```text
DIRECT_ADAPTER_PASS
!=
E2E_PASS
```

---

# 36. Persisted Artifact

必须：

```text
ARTIFACT_PERSISTED = YES
```

而不是 browser内临时 object。

---

# 37. Workspace From Real Job

必须：

```text
WORKSPACE_FROM_REAL_JOB = YES
```

---

# 38. One Workspace Per Job

继续：

```text
ONE_WORKSPACE_PER_JOB = YES
```

---

# 39. Report From Persisted Facts

必须：

```text
REPORT_FROM_REAL_PERSISTED_FACTS = YES
```

---

# 40. Recipe Non-Executable

必须：

```text
RECIPE_EXECUTION_AUTHORITY = NONE
```

---

# 41. Seven Demo Families

必须恰好执行七类。

---

# 42. Demo 1

# Dataset Intelligence + Composition Space

必须从真实 data resource入口开始。

至少验证：

```text
resource selection/import

→ DataProfile 2.4

→ user natural-language goal

→ Intent

→ Eligibility

→ Planner

→ Dataset Intelligence / Materials Explorer

→ Composition Space

→ persisted Artifact(s)

→ Workspace

→ linked sample/material inspection

→ exact sample identity

→ Finding/Evidence if applicable

→ Report/Recipe
```

---

# 43. Demo 1 Scientific Boundaries

必须保持：

```text
composition vectors deterministic

PCA bounded/deterministic

KMeans bounded/deterministic

sample identity exact
```

不得前端重新算 PCA/KMeans。

---

# 44. Demo 1 Required Audit

至少验证：

```text
same input resource identity

DataProfile exact version

Plan generated by Planner

Tool IDs only discovered after execution

Artifacts persisted

Workspace panels derive from real Job

sample selection exact

Report source exact
```

---

# 45. Demo 2

# Materials ML

用户从实际 dataset开始。

至少：

```text
resource

→ Profile

→ natural-language ML evaluation request

→ Eligibility

→ Planner

→ AnalysisPlan

→ Runtime

→ registered ML adapter(s)

→ persisted metrics/artifacts

→ Workspace

→ model/evaluation interpretation

→ Finding/Evidence where applicable

→ Report/Recipe
```

---

# 46. Demo 2 Scientific Honesty

不得把：

```text
evaluation result
```

写成：

```text
production predictive guarantee
```

---

# 47. Demo 2 No Frontend ML

必须：

```text
FRONTEND_ML_RECOMPUTATION = 0
```

---

# 48. Demo 3

# Structure + Coordination + Local Environment + Polyhedra + Experimental XRD

这是复杂 multi-capability demo。

必须：

```text
structure resource

→ DataProfile

→ natural-language structural analysis request

→ Intent/Clarification if required

→ Eligibility

→ Planner

→ AnalysisPlan 0.2 where dependencies apply

→ coordination Artifact

→ local-environment / polyhedra consumer

→ experimental XRD comparison

→ persisted Artifacts

→ Workspace

→ structural findings/evidence

→ provenance

→ Report/Recipe
```

---

# 49. Demo 3 Coordination Boundary

必须保持：

```text
algorithm-derived coordination
```

不得：

```text
true chemical bond
```

---

# 50. Demo 3 Local Environment Boundary

必须：

```text
algorithm/geometry-derived
```

不得自动宣称：

```text
definitive oxidation state
definitive bonding
```

---

# 51. Demo 3 N2 Dependency

若 current contract如此：

```text
local environment/polyhedra
consumes exact coordination Artifact
```

不得重新计算 neighbor relation。

---

# 52. Demo 3 XRD Boundary

必须：

```text
peak correspondence under tolerance
```

不得：

```text
phase confirmed
Rietveld refinement
phase fraction
```

---

# 53. Demo 3 Dependency Audit

必须 post-run验证 exact：

```text
producer Artifact

→ consumer binding

→ exact contract

→ exact checksum
```

---

# 54. Demo 4

# Trajectory + RDF + MSD + Diffusion

必须：

```text
trajectory resource

→ Profile

→ user trajectory analysis request

→ Eligibility

→ Planner

→ RDF

→ MSD

→ diffusion

→ persisted Artifacts

→ Workspace

→ Findings/Evidence

→ Report/Recipe
```

---

# 55. Demo 4 Diffusion Boundary

必须：

```text
estimated over selected fit window
```

不得：

```text
true diffusion coefficient
```

无 qualification。

---

# 56. Demo 4 Dependency

如果 diffusion依赖 MSD Artifact：

必须 exact binding。

不得 frontend重新 fit。

---

# 57. Demo 4 Scientific Audit

至少：

```text
trajectory identity

selection identity

fit window identity

unit identity

RDF/MSD/diffusion lineage
```

---

# 58. Demo 5

# Phonon + Brillouin Zone

必须使用 current supported input contract。

至少：

```text
phonon resource

→ Profile

→ natural-language phonon request

→ Eligibility

→ Planner

→ phonon analysis

→ Brillouin Zone presentation

→ persisted Artifact

→ Workspace

→ limitations/provenance

→ Report/Recipe
```

---

# 59. Demo 5 Validation Honesty

如果 current Phase 11 classification仍：

```text
phonon input/coverage has mapping-only aspects
```

必须保留。

不得因为 E2E成功改成：

```text
REFERENCE_VERIFIED
```

---

# 60. Demo 5 BZ Boundary

Brillouin Zone展示：

不得变成新的 scientific authority。

---

# 61. Demo 6

# Volumetric

必须：

```text
volumetric resource

→ Profile

→ natural-language inspection/analysis request

→ Eligibility

→ Planner

→ current registered volumetric path

→ persisted Artifact

→ Workspace viewer

→ metadata/scientific details

→ provenance

→ Report/Recipe
```

---

# 62. Demo 6 Viewer Boundary

viewer只呈现 persisted scientific payload。

不得前端生成新的 scientific field。

---

# 63. Demo 7

# Electronic Band + DOS

必须：

```text
supplied/imported electronic data

→ Profile

→ natural-language electronic analysis request

→ Eligibility

→ Planner

→ Band Structure

→ DOS

→ persisted Artifacts

→ combined Band + DOS presentation

→ Workspace

→ classification/limitations

→ Evidence/Provenance

→ Report/Recipe
```

---

# 64. Demo 7 Scientific Boundary

必须：

```text
derived from supplied electronic data
```

不得暗示：

```text
DFT performed by platform
GW performed by platform
SCF performed by platform
```

---

# 65. Demo 7 Energy Authority

保持：

```text
canonical eV provenance
```

unknown unit：

```text
INELIGIBLE
```

---

# 66. Demo 7 Fermi Boundary

仅当 supplied：

```text
Fermi energy
```

才可使用。

不得自动推断。

---

# 67. Demo 7 Classification

使用 current exact taxonomy：

```text
METAL_LIKE_UNDER_POLICY

NONZERO_GAP_UNDER_POLICY

CLASSIFICATION_UNAVAILABLE
```

actual repository enum wins。

---

# 68. Demo 7 PDOS

若适用：

```text
COMPLETE
PARTIAL
UNKNOWN
```

必须保留真实 completeness。

---

# 69. Combined Band + DOS

必须：

```text
presentation consumer
```

不是新 Tool。

---

# 70. Seven Demo Natural-Language Prompts

必须从 sealed canonical registry读取。

不能现场改写内部含义。

---

# 71. Canonical Prompt Rule

每 demo：

至少执行：

```text
primary canonical prompt
```

---

# 72. Bounded Paraphrase

至少选择部分 demos 执行：

```text
one bounded alternate phrasing
```

用于验证不是字符串 hardcode。

---

# 73. Prompt Must Be User-Like

禁止 prompt包含：

```text
Tool ID

Artifact contract name

AnalysisPlan JSON

internal schema field
```

---

# 74. Planner Result Does Not Need Byte Identity

可以接受：

```text
different human-readable wording
```

只要 semantic plan满足 sealed allowed outcome。

---

# 75. Deterministic E2E Authority

Phase 13-2主 release E2E authority：

必须使用 sealed：

```text
deterministic provider replay
```

或 repository exact deterministic equivalent。

---

# 76. Live DeepSeek Secondary Acceptance

除 deterministic authority外：

执行 bounded live-provider user-facing acceptance。

---

# 77. Live Provider Policy

必须读取 sealed exact：

```text
endpoint
models
call budget
timeout
retry
```

不得现场扩大。

---

# 78. Current Provider Boundary

预计：

```text
DeepSeek only
DEEPSEEK_KEY
```

repository actual为 authority。

---

# 79. Live Provider Must Be Bounded

必须：

```text
max calls = sealed budget

timeouts = sealed

retries = sealed
```

不得：

```text
retry until PASS
```

---

# 80. Live Provider Evidence

记录：

```text
call count

model

latency

outcome class

error category if any
```

不得记录 secret。

---

# 81. Live Provider Does Not Prove Science

必须：

```text
LIVE_PROVIDER_PASS
!=
SCIENTIFIC_VALIDATION_PASS
```

---

# 82. Deterministic Provider Pass Is Primary

若 live DeepSeek因外部网络/provider transient失败：

不得自动让 deterministic scientific runtime结果失效。

必须 classify：

```text
PROVIDER_EXTERNAL_FAILURE
```

并按 sealed release contract决定 blocking性。

---

# 83. Persona A

# Canonical Scientist User

至少用于全部 7 demos。

用户：

```text
knows materials-science goal

does not know internal product IDs

provides supported data

asks reasonable scientific question

expects result + limitations
```

---

# 84. Persona A Completion

用户应能完成：

```text
select data
ask question
resolve clarification if needed
review Plan
start execution
inspect results
inspect trust path
finalize Report
inspect Recipe
```

---

# 85. Persona B

# Imperfect / Exploratory User

必须实际执行 negative-path scenarios。

---

# 86. Negative Scenario 1

# Ambiguous Intent

必须：

```text
user gives ambiguous request

→ one clarification round

→ READY
or
typed non-ready
```

不能第二轮。

---

# 87. Negative Scenario 2

# Second Clarification Would Be Needed

必须：

```text
round 1 insufficient
→ typed failure/non-ready
```

且：

```text
Plan = 0
Job = 0
Queue = 0
ToolCall = 0
Artifact = 0
```

---

# 88. Negative Scenario 3

# Unsupported Capability

用户请求 Future Scope / unsupported capability。

必须：

```text
Eligibility rejects

no Plan execution

no Job enqueue
```

---

# 89. Negative Scenario 4

# Unsupported / Limited Input

必须显示：

```text
typed support state

reason

possible next action
```

不得 fake readiness。

---

# 90. Negative Scenario 5

# Partial Execution

使用 sealed failure simulation/fixture path。

必须真实验证：

```text
successful independent branch preserved

failed branch typed

descendants blocked

Workspace shows usable results

Report includes limitation
```

---

# 91. Negative Scenario 6

# Historical / Stale Recovery

必须验证：

```text
reload / Back / Forward / historical open
```

后：

```text
exact scientific identity preserved
```

不得 latest rebind。

---

# 92. Negative Scenario 7

# Provider Failure

使用 bounded controlled provider failure path。

必须：

```text
typed failure

context preserved

no fake success

no scientific execution if provider decision unavailable
```

按 current contract。

---

# 93. Negative Scenario 8

# Limitation-Bearing Report

必须至少 finalize一次：

```text
Report containing mandatory scientific limitation
```

验证用户不能删掉 mandatory limitation。

---

# 94. Browser Execution

primary full seven-demo E2E：

使用：

```text
Chromium
```

或 current canonical primary browser。

---

# 95. Firefox / WebKit

执行 representative cross-browser release-level flows。

至少覆盖：

```text
one data/planner flow

one scientific Workspace flow

one Report/Recipe flow

one negative path
```

---

# 96. Mobile

390x844不要求七个 science runtime全重复。

但必须用真实完成的 Job/Workspace验证：

```text
mobile Result inspection

Viewer

Finding/Evidence

Inspector

Report

Recipe
```

---

# 97. Mobile Must Use Real Job Data

不得使用 mock Workspace。

---

# 98. Browser Errors

required cases：

```text
PAGE_ERRORS = 0

CONSOLE_ERRORS = 0

UNEXPECTED_FAILED_REQUESTS = 0

UNAPPROVED_EXTERNAL_REQUESTS = 0
```

provider-request exception按 sealed policy。

---

# 99. Real Services

必须运行真实：

```text
PostgreSQL

Redis

MinIO
```

---

# 100. Service Skips

required E2E：

```text
SERVICE_TEST_SKIPS = 0
```

---

# 101. Queue Evidence

每 demo记录：

```text
Job created

queue entry

worker claimed

runtime completed/partial/failed

ToolCalls

Artifacts persisted
```

---

# 102. Job Count Audit

每 canonical demo：

必须明确：

```text
expected jobs
actual jobs
```

防止 duplicate submit。

---

# 103. Double Submit

至少一个 demo测试：

```text
double click / repeated submit
```

按 current idempotency semantics：

不得产生不受控重复 execution。

---

# 104. Artifact Count Audit

每 demo记录：

```text
expected Artifact families

actual Artifact records

exact IDs

versions

checksums
```

---

# 105. Artifact Content Authority

验证 scientific semantic payload来自：

```text
registered Adapter
```

不是 frontend生成。

---

# 106. Workspace Audit

每 demo：

```text
Job
→ Workspace
```

必须 exact且 idempotent。

---

# 107. Workspace Reload

至少部分 demos：

```text
reload
→ same Workspace authority
```

---

# 108. Selection Identity

不得：

```text
latest
nearest
fuzzy
filename
array position
```

rebind scientific selection。

---

# 109. Findings

对于 interpretation-applicable demos：

验证 actual persisted：

```text
ScientificClaim
ScientificEvidenceBundle
GroundedScientificInterpretation
```

---

# 110. No Finding Where Not Applicable

不适用：

```text
Finding = NOT_APPLICABLE
```

不能现场生成 claim只为 demo完整。

---

# 111. Trust Path

至少 selected demos验证：

```text
Finding
→ Evidence
→ Artifact
→ Tool/version
→ input resource
→ provenance
```

---

# 112. Tool Version

必须 exact。

例如 N1/N2/N3/N4/N5 tool IDs：

使用 live Registry exact version。

不得由 Prompt硬编码替代 repository authority。

---

# 113. Report

每 applicable demo：

必须尝试从真实 persisted sources：

```text
compose
preview
finalize
```

---

# 114. Report Mandatory Disclosures

必须保留：

```text
warnings

limitations

failed scope

blocked scope

missing scope
```

按 applicable state。

---

# 115. Report Atomicity

若 current contract是：

```text
Report + paired Recipe atomic
```

必须实际验证。

---

# 116. Recipe

必须检查：

```text
human-readable summary

exact Tool IDs/versions

parameters

Artifact refs

warnings/limitations

semantic hash
```

---

# 117. Recipe Browse

浏览 Recipe：

必须：

```text
new Plan = 0
new Job = 0
new queue = 0
new ToolCall = 0
```

---

# 118. Historical Report

至少一个 demo：

finalize后：

```text
navigate away

reload/open historical Report

verify exact source identity
```

---

# 119. Scientific Validation Comparison

E2E scientific outputs应与 Phase 11 sealed authority做适用的：

```text
identity/invariant/reference comparison
```

---

# 120. Do Not Invent Numeric Golden Values

必须：

```text
NEW_SCIENTIFIC_EXPECTED_VALUES = 0
```

---

# 121. Existing Golden Cases

如果 demo output对应已有 Phase 11 golden：

必须引用 exact existing authority。

---

# 122. Reference-Limited Cases

若对应：

```text
NOT_APPLICABLE
```

仍保持 N/A。

不得因 demo PASS提升。

---

# 123. V4

必须：

```text
V4_BEFORE_13_2 = 0
V4_AFTER_13_2 = 0
```

---

# 124. Scientific Semantic Diff

对适用 outputs：

验证 against sealed/reference baseline。

要求：

```text
UNEXPECTED_SCIENTIFIC_SEMANTIC_DIFF = 0
```

---

# 125. Environment Capture

每 demo记录：

```text
commit SHA

lock identity

Python version

frontend build identity

service versions where material

fixture checksum

provider mode
```

---

# 126. No Arbitrary Environment Mutation

不得：

```text
pip install
npm install
manual dependency change
```

让 demo通过。

---

# 127. Dependency Freeze

必须：

```text
NEW_PYTHON_DEPENDENCIES = 0

NEW_FRONTEND_DEPENDENCIES = 0

LOCKFILE_CHANGES = 0
```

---

# 128. Database Freeze

必须：

```text
NEW_DATABASE_TABLES = 0

NEW_DATABASE_COLUMNS = 0

NEW_DATABASE_MIGRATIONS = 0
```

---

# 129. API Freeze

必须：

```text
NEW_PUBLIC_API_FAMILIES = 0
```

---

# 130. Tool Freeze

必须：

```text
NEW_SCIENTIFIC_TOOLS = 0

NEW_SCIENTIFIC_ALGORITHMS = 0
```

---

# 131. Artifact Family Freeze

```text
NEW_ARTIFACT_FAMILIES = 0
```

---

# 132. DataProfile Freeze

```text
NEW_DATAPROFILE_VERSION = 0
```

---

# 133. AnalysisPlan Freeze

```text
NEW_ANALYSISPLAN_VERSION = 0
```

---

# 134. LLM Call Sites

必须：

```text
NEW_LLM_CALL_SITES = 0
```

---

# 135. Real LLM Calls

允许：

```text
BOUNDED_REAL_LLM_CALLS =
sealed 13-0 policy only
```

必须计数。

---

# 136. Real LLM Evidence Redaction

禁止 evidence包含：

```text
DEEPSEEK_KEY

Authorization header
```

---

# 137. Secret Scan

必须：

```text
NO_SECRET_PATTERN_HITS = PASS
```

---

# 138. Scientific Security

必须继续：

```text
Artifact inert

no arbitrary Python

no shell

no notebook execution

no HTML/JS execution

no iframe

no arbitrary module execution
```

---

# 139. Cross-Project Isolation

至少一个 real service-backed negative case：

```text
Project A
cannot consume Project B Artifact
```

---

# 140. Cross-Workspace Isolation

至少：

```text
Workspace A
cannot fuzzy-select/rebind
Workspace B result
```

---

# 141. Artifact URL Security

不得执行/iframe arbitrary external Artifact URL。

---

# 142. Demo Result Vocabulary

每 demo只能：

```text
PASS

PASS_WITH_EXPLICIT_LIMITATIONS

FAIL_PRODUCT_INTEGRATION

FAIL_SCIENTIFIC

BLOCKED_EXTERNAL_PROVIDER

BLOCKED_ENVIRONMENT
```

---

# 143. Demo PASS

仅当所有 required dimensions通过：

```text
PASS
```

---

# 144. PASS_WITH_EXPLICIT_LIMITATIONS

仅适用于：

```text
already sealed nonblocking limitations
```

不得用它隐藏新 release defect。

---

# 145. Product Integration Failure

例如：

```text
Planner cannot reach Tool

Runtime cannot execute

Workspace cannot show Artifact

Report cannot consume persisted source
```

分类：

```text
FAIL_PRODUCT_INTEGRATION
```

---

# 146. Scientific Failure

如果科学结果不符合 existing authority：

```text
FAIL_SCIENTIFIC
```

立即 reviewer blocker。

---

# 147. External Provider Failure

live DeepSeek次级 case：

可：

```text
BLOCKED_EXTERNAL_PROVIDER
```

但 deterministic authority必须单独给结果。

---

# 148. Environment Failure

仅真实 infra不可用且非产品 defect时使用。

必须证据化。

---

# 149. Seven-Demo Aggregate

最终：

```text
DEMO_1_STATUS
...
DEMO_7_STATUS
```

必须逐个给出。

---

# 150. Ideal Aggregate

成功期望：

```text
7/7
PASS or PASS_WITH_EXPLICIT_LIMITATIONS
```

且：

```text
FAIL_PRODUCT_INTEGRATION = 0

FAIL_SCIENTIFIC = 0
```

---

# 151. P13X2 Acceptance

必须从 sealed registry读取 exact：

```text
P13X2-A01
...
P13X2-A08
```

---

# 152. Acceptance IDs Immutable

必须：

```text
P13X2_EXPECTED = 8

PASS = 8

MISSING = 0

EXTRA = 0

DUPLICATE = 0

CONFLICTING = 0
```

---

# 153. Reviewer Interpretation of P13X2

actual wording优先。

至少 equivalent覆盖：

```text
A.
7 real-user E2E execution

B.
natural-language / Planner path integrity

C.
real queue/runtime/persistence/Adapter execution

D.
Artifact/Workspace/Interpretation/Report lineage

E.
negative/imperfect-user scenarios

F.
deterministic + bounded live provider policy

G.
scientific honesty / security /
identity / regression evidence

H.
lifecycle closure
and 13-3 handoff
```

---

# 154. Evidence Root

建立：

```text
docs/phase13/evidence/
phase13_2_seven_real_user_e2e/
```

---

# 155. Global Evidence Files

至少：

```text
baseline.txt

entry_gate.md

phase13_1_handoff_snapshot.json

fact_model_hash_verification.json

scope_baseline_hash_verification.json

fixture_registry_verification.json

provider_policy.json

service_environment.json

no_injection_audit.json

job_artifact_aggregate.json

workspace_aggregate.json

interpretation_aggregate.json

report_recipe_aggregate.json

negative_path_aggregate.json

browser_matrix.json

mobile_real_job_inspection.json

scientific_authority_nonchange.json

release_scope_nonchange.json

security.md

secret_scan.txt

phase13_3_handoff.json

manifest.json
```

---

# 156. Per-Demo Evidence Directory

每 demo单独：

```text
demo_01_dataset_composition/
demo_02_materials_ml/
demo_03_structure_xrd/
demo_04_trajectory/
demo_05_phonon_bz/
demo_06_volumetric/
demo_07_electronic/
```

---

# 157. Per-Demo Required Evidence

每个至少：

```text
fixture.json

user_prompt.txt

provider_mode.json

browser_steps.json

intent.json

clarification.json

eligibility.json

analysis_plan.json

job.json

tool_calls.json

artifact_manifest.json

workspace.json

selection_identity.json

interpretation.json

finding_evidence.json

provenance.json

report.json

recipe.json

scientific_comparison.json

limitations.json

network_summary.json

console_summary.json

screenshots_manifest.json

demo_result.json
```

不适用项必须：

```text
NOT_APPLICABLE
+
reason
```

不能缺文件不解释。

---

# 158. Screenshots

用于：

```text
presentation evidence
```

不是 scientific numeric authority。

---

# 159. Screenshot Manifest

每 screenshot记录：

```text
demoId

step

route

viewport

source state

purpose
```

---

# 160. No Screenshot Numeric Validation

必须：

```text
SCREENSHOT_NUMERIC_SCIENTIFIC_AUTHORITY = NONE
```

---

# 161. Canonical Docs

至少：

```text
docs/phase13/
phase13_2_seven_real_user_e2e.md

phase13_2_demo_01_dataset_composition.md

phase13_2_demo_02_materials_ml.md

phase13_2_demo_03_structure_xrd.md

phase13_2_demo_04_trajectory.md

phase13_2_demo_05_phonon_bz.md

phase13_2_demo_06_volumetric.md

phase13_2_demo_07_electronic.md

phase13_2_negative_user_scenarios.md

phase13_2_provider_acceptance.md

phase13_2_scientific_authority_reconciliation.md

phase13_2_release_findings.md

phase13_3_documentation_reproducibility_handoff.md

phase13_2_completion.md
```

---

# 162. Human-Equivalent Action Logging

browser evidence应保留：

```text
user-visible actions
```

例如：

```text
clicked Data

selected fixture

typed prompt

answered clarification

reviewed Plan

clicked Run

opened Workspace

selected Result

opened Evidence

finalized Report
```

---

# 163. Avoid Internal Test Narrative

不要把主证据写成：

```text
POST /jobs returned 200
```

而缺少用户路径。

API evidence只是 supporting evidence。

---

# 164. Timing Evidence

可记录：

```text
request duration

job duration

viewer load duration
```

但：

不得据此声称：

```text
human usability speed
```

---

# 165. No Arbitrary Performance Threshold

除非 sealed baseline已有要求。

否则 performance只记录，不新增 release blocker阈值。

---

# 166. User Context Preservation

每 demo验证：

```text
prompt preserved

selected data preserved

analysis context preserved

Workspace transition understandable
```

---

# 167. Error Recovery

negative paths验证：

```text
what happened

why

what user can do

what was preserved
```

---

# 168. Report/Recipe User Experience

至少一个 canonical scientist persona必须：

```text
compose Report

inspect preview

finalize

inspect Recipe

return to Workspace
```

---

# 169. Historical Recovery

至少一个 real demo：

```text
close/reload/reopen
```

再继续 inspection。

---

# 170. Browser Back / Forward

至少一个 real demo：

验证：

```text
Back
Forward
reload
```

不会破坏 exact scientific selection。

---

# 171. Mobile Real Job

至少一个复杂 demo：

完成 desktop/runtime执行后，

用：

```text
390x844
```

真实打开相同 Workspace。

---

# 172. Mobile Authority

必须：

```text
same persisted scientific authority
```

不能生成 mobile-specific scientific summary authority。

---

# 173. Findings Scientific Wording

必须保持：

```text
qualified
bounded
source-grounded
```

---

# 174. Recommendation

如出现 recommendation：

必须：

```text
non-executable
```

---

# 175. Recommendation Click

不得直接：

```text
create Plan
Job
queue
```

---

# 176. Validation Axis Display

至少 selected demo验证 UI没有混淆：

```text
Product Support

Scientific Validation

Cross-Platform Reproducibility

Presentation Validation
```

---

# 177. Scientific Wording Audit — Coordination

```text
algorithm-derived
```

---

# 178. Scientific Wording Audit — XRD

```text
peak correspondence under tolerance
```

---

# 179. Scientific Wording Audit — Diffusion

```text
estimated over selected fit window
```

---

# 180. Scientific Wording Audit — Electronic

```text
supplied/imported electronic data
```

---

# 181. Scientific Wording Audit — ML

不得输出无依据的 generalization guarantee。

---

# 182. Scientific Wording Audit — Phonon

保持 current validation/input limitation措辞。

---

# 183. Regression After E2E

完成 E2E后：

运行完整 regression。

---

# 184. Backend Regression

必须：

```text
uv run python -m pytest -q
```

floor：

```text
>= Phase 13-1 final canonical floor
```

动态读取。

---

# 185. Frontend Regression

```text
npm --prefix apps/web test
```

floor：

```text
>= Phase 13-1 final canonical floor
```

---

# 186. Typecheck

```text
npm --prefix apps/web run typecheck
= PASS
```

---

# 187. Build

```text
npm --prefix apps/web run build
= PASS
```

---

# 188. Lock

```text
uv lock --check
= PASS
```

---

# 189. Diff

```text
git diff --check
= PASS
```

---

# 190. Service Integration

必须：

```text
PostgreSQL PASS
Redis PASS
MinIO PASS
```

---

# 191. Linux / Windows Replay

继续 retained:

```text
Linux invariant replay PASS

Windows invariant replay PASS
```

---

# 192. Semantic Hash

继续：

```text
Linux Scope Baseline hash
==
Windows Scope Baseline hash
==
current corrected hash
```

---

# 193. Browser Matrix

必须：

```text
Chromium full seven-demo primary suite

Firefox representative suite

WebKit representative suite

390x844 real-job inspection
```

---

# 194. npm Audit

若 mirror仍：

```text
NOT_IMPLEMENTED
```

则：

```text
npm audit = UNAVAILABLE
```

不得写 PASS。

---

# 195. Security Regression

必须：

```text
NO_ARBITRARY_CODE_EXECUTION = PASS

NO_ARTIFACT_HTML_EXECUTION = PASS

NO_ARTIFACT_JAVASCRIPT_EXECUTION = PASS

NO_IFRAME_EXECUTION = PASS

NO_RECIPE_EXECUTION = PASS

NO_RECOMMENDATION_EXECUTION = PASS

NO_FRONTEND_SCIENTIFIC_RECOMPUTATION = PASS

NO_CROSS_PROJECT_LEAK = PASS

NO_STALE_IDENTITY_REBINDING = PASS

NO_SECRET_PATTERN_HITS = PASS
```

---

# 196. Phase 13-2 Release Finding Registry

必须建立：

```text
Phase13_2ReleaseFindingRegistry
```

每发现：

```text
findingId

demoId

category

severity

userConsequence

scientificConsequence

releaseConsequence

evidenceRefs

recommendedOwnerPhase
```

---

# 197. Finding Categories

只能：

```text
PASS_OBSERVATION

NONBLOCKING_LIMITATION

DOCUMENTATION_GAP

TARGETED_POLISH_DEFECT

RELEASE_CRITICAL_INTEGRATION_DEFECT

SCIENTIFIC_DEFECT

SECURITY_DEFECT

PROVIDER_EXTERNAL_EVENT
```

---

# 198. 13-3 Handoff

必须生成：

```text
Phase13_3DocumentationReproducibilityHandoff
```

---

# 199. 13-3 Handoff Contents

至少：

```text
7 demo outcomes

exact fixture IDs

canonical prompts

successful user paths

negative-path outcomes

Artifact manifests

Workspace evidence

Findings/Evidence evidence

Report/Recipe examples

scientific limitations

provider-mode results

release findings

documentation gaps

reproduction instructions inputs

baseline hashes

scientific authority refs
```

---

# 200. 13-4 Candidate Findings

如果发现：

```text
TARGETED_POLISH_DEFECT
```

记录给 13-4。

不要在 13-2修。

---

# 201. 13-3 Documentation Gaps

如果发现：

```text
DOCUMENTATION_GAP
```

交给 13-3。

---

# 202. Integration Defects

如果：

```text
RELEASE_CRITICAL_INTEGRATION_DEFECT > 0
```

Phase 13-2不能 PASS。

---

# 203. Scientific Defects

如果：

```text
SCIENTIFIC_DEFECT > 0
```

必须 reviewer BLOCK。

---

# 204. Security Defects

release-impacting：

```text
SECURITY_DEFECT > 0
```

不能 PASS。

---

# 205. Nonblocking Limitations

只允许：

```text
already sealed
or
newly discovered truly nonblocking factual limitation
```

新 limitation必须 reviewer可见。

---

# 206. Production Code Changes

预期：

```text
PHASE13_2_PRODUCTION_CODE_CHANGES = 0
```

---

# 207. If Production Code Was Changed

只能因为：

```text
explicit reviewer-reauthorized correction
```

否则不能 PASS。

---

# 208. Evidence-Only/Test-Only Changes

允许：

```text
E2E tests

browser harness

evidence generator

docs

fixtures manifests

release finding registry

handoff
```

不得改变 runtime semantics。

---

# 209. Queue Admission

Entry Gate PASS后：

只创建：

```text
one Phase 13-2 TASK block
```

---

# 210. Queue State

要求：

```text
TASK_BLOCK_COUNT = 1

ACTIVE_TASK = Phase 13-2

PHASE13_3_EXECUTABLE_TASK_CREATED = NO

PHASE13_4_EXECUTABLE_TASK_CREATED = NO

PHASE14_CREATED = NO
```

---

# 211. First Required Output

执行开始后第一组必须输出：

```text
Phase 13-2 Entry Gate
+ Real-User E2E Contract
+ Seven-Demo Execution Admission
```

至少确认：

1. branch；
2. HEAD；
3. origin/master；
4. worktree clean；
5. TASK_BLOCK_COUNT=0；
6. Phase 13-1 implementation SHA；
7. 13-1 exact-SHA CI；
8. 13-1 completion SHA；
9. 13-1 archive SHA；
10. release blockers=0；
11. integration gaps=0；
12. demo preflight 7/7；
13. Fact Model hash；
14. corrected Scope Baseline hash；
15. Phase 12 baseline hash；
16. Registry=62；
17. DataProfile=2.4；
18. AnalysisIntent=1.0；
19. clarification=1 round / 3 questions / typed failure；
20. EligibilityResolution=1.0；
21. AnalysisPlan=0.1/0.2；
22. migration=0007；
23. Phase 13-2 handoff resolves；
24. exact seven demo IDs；
25. exact fixture count/checksums；
26. exact P13X2-A01..A08；
27. deterministic provider policy；
28. bounded live provider policy；
29. no-injection contract；
30. real persistence/runtime contract；
31. PostgreSQL/Redis/MinIO available；
32. Chromium primary runner available；
33. Phase 13-3 task absent；
34. Phase 14 absent。

成功：

```text
PHASE_13_2_ENTRY_GATE = PASS

PHASE_13_1_DEPENDENCY = VERIFIED

ZERO_GAP_BASELINE = VERIFIED

REAL_USER_E2E_EXECUTION =
AUTHORIZED

SEVEN_DEMO_EXECUTION =
AUTHORIZED

PRODUCTION_CHANGE_AUTHORITY =
NONE

SCIENTIFIC_CHANGE_AUTHORITY =
NONE

PHASE_13_3_EXECUTION_AUTHORITY =
NONE
```

---

# 212. Required Execution Sequence

严格：

```text
verify Phase 13-1 lifecycle

→ verify Fact Model hash

→ verify corrected Scope Baseline hash

→ verify Phase 12 baseline

→ verify Phase 11 authority

→ load exact P13X2 acceptance

→ load seven-demo registry

→ load fixture registry

→ load personas

→ load negative paths

→ load provider policy

→ verify required services

→ admit exactly one 13-2 task

→ execute Demo 1 real-user E2E

→ audit Demo 1 lineage

→ execute Demo 2 real-user E2E

→ audit Demo 2 lineage

→ execute Demo 3 real-user E2E

→ audit dependency bindings

→ execute Demo 4 real-user E2E

→ audit MSD/diffusion lineage

→ execute Demo 5 real-user E2E

→ audit phonon/BZ authority

→ execute Demo 6 real-user E2E

→ audit volumetric authority

→ execute Demo 7 real-user E2E

→ audit Band/DOS lineage

→ run bounded paraphrase cases

→ execute imperfect-user negative scenarios

→ execute second-round clarification failure case

→ execute unsupported capability case

→ execute unsupported/limited input case

→ execute partial execution case

→ execute historical/stale recovery case

→ execute provider failure case

→ execute limitation-bearing Report case

→ run bounded live DeepSeek acceptance

→ run representative Firefox/WebKit flows

→ run 390x844 real-job inspection

→ reconcile seven demo outcomes

→ reconcile release findings

→ run scientific authority comparison

→ run no-injection audit

→ run full backend/frontend regression

→ run service integration

→ run Linux/Windows replay

→ run security/secret scan

→ build evidence manifest

→ generate 13-3 handoff

→ create Phase 13-2 implementation/evidence commit

→ push

→ WAIT FOR IMPLEMENTATION EXACT-SHA CI

→ if PASS:
   append Phase 13-2 completion record

→ completion commit/push directly

→ archive only Phase 13-2 task

→ archive commit/push directly

→ verify queue empty

→ stop
```

---

# 213. User Update Cadence

执行时间可能较长。

执行器必须遵守：

```text
before each major command group:
explain purpose

after each major command group:
summarize result
```

且最多约：

```text
5 tool actions
```

应提供一次状态更新。

---

# 214. No Silent Long Run

每完成 1–2 demo：

必须输出简短状态：

```text
completed demos

current results

issues discovered

whether execution remains inside scope
```

---

# 215. Implementation Commit Allowed

可包含：

```text
E2E/browser tests

evidence harness

demo result manifests

release findings

docs

Phase 13-3 handoff

persistent state

TASK admission
```

---

# 216. Implementation Commit Forbidden

不得包含：

```text
new product capability

scientific algorithm changes

Planner semantic changes

Runtime semantic changes

Adapter semantic changes

Workspace changes

Report/Recipe contract changes

DB migrations

new API family

new dependency

release polish
```

---

# 217. Exact-SHA CI

push后：

必须：

```text
WAIT FOR IMPLEMENTATION EXACT-SHA CI
```

---

# 218. Required CI

至少：

```text
Backend Unit

Frontend Tests

Typecheck

Build

Phase 13-2 focused E2E governance

service-backed integration

Chromium

Firefox

WebKit

390x844

PostgreSQL

Redis

MinIO

Linux invariant replay

Windows invariant replay

Phase 11 integrity

Phase 12 baseline integrity

Phase 13 baseline integrity

security

secret scan
```

---

# 219. Failed Candidate

若 CI失败：

保留：

```text
candidate SHA

CI run

failed jobs

root cause

fix-forward SHA
```

不得 rewrite history。

---

# 220. Test-Harness Fix

如果 failure仅：

```text
locator
evidence hash
line ending
test orchestration
```

可以 fix-forward。

---

# 221. Production Failure

如果 failure揭示 production defect：

不得偷偷 patch。

返回 reviewer。

---

# 222. Completion Record

只有 implementation exact-SHA CI PASS：

才 append：

```text
# Phase 13-2 Seven Canonical Real-User E2E Demonstrations Result
```

---

# 223. Completion Push

直接：

```text
commit
push
```

不等待额外 CI。

---

# 224. Queue Archive

删除：

```text
only Phase 13-2 TASK block
```

---

# 225. Do Not Queue 13-3

必须：

```text
PHASE13_3_EXECUTABLE_TASK_CREATED = NO
```

---

# 226. Archive Push

直接：

```text
commit
push
```

不等待额外 CI。

---

# 227. Lifecycle Terminology

最终：

```text
IMPLEMENTATION_VERIFIED_BY_EXACT_SHA_CI

COMPLETION_RECORDED

QUEUE_ARCHIVED
```

---

# 228. Mandatory Production Markers

必须：

```text
PHASE13_2_PRODUCTION_CODE_CHANGES = 0

PHASE13_2_BACKEND_BEHAVIOR_CHANGES = 0

PHASE13_2_FRONTEND_BEHAVIOR_CHANGES = 0

PHASE13_2_SCIENTIFIC_BEHAVIOR_CHANGES = 0

PHASE13_2_NEW_SCIENTIFIC_TOOLS = 0

PHASE13_2_NEW_SCIENTIFIC_ALGORITHMS = 0

PHASE13_2_NEW_ARTIFACT_FAMILIES = 0

PHASE13_2_NEW_DATAPROFILE_VERSION = 0

PHASE13_2_NEW_ANALYSISPLAN_VERSION = 0

PHASE13_2_NEW_DATABASE_MIGRATIONS = 0

PHASE13_2_NEW_PUBLIC_API_FAMILIES = 0

PHASE13_2_NEW_DEPENDENCIES = 0

PHASE13_2_LOCKFILE_CHANGES = 0

PHASE13_2_NEW_LLM_CALL_SITES = 0

PHASE13_2_FRONTEND_SCIENTIFIC_RECOMPUTATION = 0
```

---

# 229. Real E2E Markers

必须：

```text
REAL_USER_ENTRY_E2E = YES

REAL_PERSISTENCE_USED = YES

REAL_QUEUE_USED = YES

REAL_QUEUE_WORKER_RUNTIME_USED = YES

REGISTERED_ADAPTER_EXECUTION_USED = YES

PERSISTED_ARTIFACT_USED = YES

WORKSPACE_FROM_REAL_JOB = YES

REPORT_FROM_REAL_PERSISTED_FACTS = YES
```

---

# 230. Injection Markers

必须：

```text
HANDCRAFTED_ANALYSISPLAN_INJECTION = 0

HANDCRAFTED_JOB_INJECTION = 0

HANDCRAFTED_TOOLCALL_INJECTION = 0

HANDCRAFTED_ARTIFACT_INJECTION = 0

HANDCRAFTED_WORKSPACE_INJECTION = 0

HANDCRAFTED_INTERPRETATION_INJECTION = 0

HANDCRAFTED_FINDING_INJECTION = 0

HANDCRAFTED_EVIDENCE_INJECTION = 0

HANDCRAFTED_REPORT_INJECTION = 0

HANDCRAFTED_RECIPE_INJECTION = 0
```

---

# 231. Demo Markers

必须：

```text
PHASE13_DEMO_FAMILIES = 7

PHASE13_2_DEMOS_EXECUTED = 7

DEMO_1_STATUS = <actual>
DEMO_2_STATUS = <actual>
DEMO_3_STATUS = <actual>
DEMO_4_STATUS = <actual>
DEMO_5_STATUS = <actual>
DEMO_6_STATUS = <actual>
DEMO_7_STATUS = <actual>
```

---

# 232. Aggregate Success Marker

理想：

```text
DEMO_PASS_OR_EXPLICIT_LIMIT = 7/7

DEMO_FAIL_PRODUCT_INTEGRATION = 0

DEMO_FAIL_SCIENTIFIC = 0
```

---

# 233. Negative Path Markers

必须：

```text
AMBIGUOUS_INTENT_CASE = PASS

ONE_ROUND_CLARIFICATION_CASE = PASS

SECOND_ROUND_TYPED_FAILURE_CASE = PASS

UNSUPPORTED_CAPABILITY_CASE = PASS

UNSUPPORTED_LIMITED_INPUT_CASE = PASS

PARTIAL_EXECUTION_CASE = PASS

HISTORICAL_STALE_RECOVERY_CASE = PASS

PROVIDER_FAILURE_CASE = PASS

LIMITATION_BEARING_REPORT_CASE = PASS
```

---

# 234. Clarification Markers

必须：

```text
PHASE13_CLARIFICATION_MAX_ROUNDS = 1

PHASE13_CLARIFICATION_MAX_QUESTIONS = 3

SECOND_CLARIFICATION_ROUND =
TYPED_FAILURE

CURRENT_CANONICAL_TWO_ROUND_ASSERTIONS = 0
```

---

# 235. Scientific Baseline

必须：

```text
REGISTRY_BEFORE_13_2 = 62
REGISTRY_AFTER_13_2 = 62

DATAPROFILE_BEFORE_13_2 = 2.4
DATAPROFILE_AFTER_13_2 = 2.4

MIGRATION_BEFORE_13_2 =
0007_phase10m1_workspace_domain

MIGRATION_AFTER_13_2 =
0007_phase10m1_workspace_domain

V4_BEFORE_13_2 = 0
V4_AFTER_13_2 = 0
```

---

# 236. Scope Baseline

必须：

```text
INITIAL_RELEASE_FACT_MODEL_HASH =
e0248d502e4a442bb9596a8d2f6fe6d7fdefe61c41121ae08736734ce4004a06

INITIAL_RELEASE_SCOPE_BASELINE_HASH =
93dea4a2b0bf31215ab2af1952b16ac47b20b7ed9b111bb2fb60ef70dd431627
```

除非 reviewer-approved correction发生。

---

# 237. Scientific Honesty

必须：

```text
SUPPORTED_EQUALS_VALIDATED = NO

E2E_PASS_EQUALS_REFERENCE_VALIDATED = NO

REPORT_INCLUDED_EQUALS_VALIDATED = NO

RECIPE_EXISTS_EQUALS_REPRODUCIBILITY_VALIDATED = NO

LIVE_PROVIDER_PASS_EQUALS_SCIENTIFIC_PASS = NO

BROWSER_PASS_EQUALS_SCIENTIFIC_PASS = NO

SERVICE_PASS_EQUALS_SCIENTIFIC_PASS = NO

SCREENSHOT_NUMERIC_SCIENTIFIC_AUTHORITY = NONE

FRONTEND_SCIENTIFIC_AUTHORITY = NONE
```

---

# 238. Provider Markers

必须：

```text
DETERMINISTIC_PROVIDER_E2E =
<actual>

BOUNDED_LIVE_DEEPSEEK_CASES =
<actual>

LIVE_PROVIDER_CALL_COUNT =
<actual within sealed budget>

LIVE_PROVIDER_RETRIES =
<actual within sealed policy>
```

---

# 239. Release Finding Markers

必须：

```text
RELEASE_CRITICAL_INTEGRATION_DEFECTS =
<actual>

SCIENTIFIC_DEFECTS =
<actual>

SECURITY_DEFECTS =
<actual>

TARGETED_POLISH_DEFECTS =
<actual>

DOCUMENTATION_GAPS =
<actual>

NONBLOCKING_LIMITATIONS =
<actual>
```

---

# 240. PASS Gate

Phase 13-2 只有在：

```text
Phase 13-1 PASS

entry clean

current Fact Model verified

corrected Scope Baseline verified

Registry=62

DataProfile=2.4

clarification authority correct

7 demo contracts loaded

all required fixtures valid

real services available


7/7 demos actually executed

all 7 entered from real user-facing path

no handcrafted injection

real Planner used

real Runtime used

real registered Adapters used

real persistence used

real Artifacts persisted

real Workspaces derived from Jobs


all required Report/Recipe paths verified

all required identity lineage verified


negative-path suite PASS

second-round clarification rejection PASS

partial execution PASS

historical recovery PASS

provider failure PASS

mandatory limitation Report PASS


deterministic E2E authority PASS

bounded live provider acceptance completed
according to sealed policy


DEMO_FAIL_PRODUCT_INTEGRATION = 0

DEMO_FAIL_SCIENTIFIC = 0

RELEASE_CRITICAL_INTEGRATION_DEFECTS = 0

SCIENTIFIC_DEFECTS = 0

SECURITY_DEFECTS = 0


scientific authority unchanged

Registry unchanged

DataProfile unchanged

migration unchanged

no new Tool

no new algorithm

no new Artifact family

no new API

no migration

no dependency

no frontend scientific recomputation


backend regression PASS

frontend regression PASS

typecheck PASS

build PASS

lock PASS

diff PASS

PostgreSQL PASS

Redis PASS

MinIO PASS

Linux replay PASS

Windows replay PASS

browser matrix PASS

security PASS

secret scan PASS

evidence manifest PASS


P13X2 = 8/8


implementation exact-SHA CI PASS

completion recorded

queue archived


TASK_BLOCK_COUNT = 0

Phase 13-3 task absent

Phase14 absent

HEAD == origin/master

worktree clean
```

才允许：

```text
PHASE_13_2 = PASS
```

---

# 241. BLOCKED — Any Demo Not Executed

如果：

```text
PHASE13_2_DEMOS_EXECUTED < 7
```

不能 PASS。

---

# 242. BLOCKED — Handcrafted Injection

任一 injection > 0：

不能 PASS。

---

# 243. BLOCKED — Direct Adapter Used As E2E

如果某 demo主路径：

```text
direct Adapter
```

而未经过 product orchestration：

不能 PASS。

---

# 244. BLOCKED — Mock Persistence

如果 required demo使用：

```text
mock DB
fake queue
in-memory Artifact authority
```

不能 PASS。

---

# 245. BLOCKED — Prebuilt Workspace

如果不是 real Job派生：

不能 PASS。

---

# 246. BLOCKED — Planner Bypassed

如果用户 prompt没有真正经过：

```text
Intent
Eligibility
Planner
```

适用路径：

不能 PASS。

---

# 247. BLOCKED — Clarification Drift

如果出现第二轮互动 clarification：

不能 PASS。

---

# 248. BLOCKED — Integration Defect

若：

```text
RELEASE_CRITICAL_INTEGRATION_DEFECTS > 0
```

不能 PASS。

---

# 249. BLOCKED — Scientific Defect

若：

```text
SCIENTIFIC_DEFECTS > 0
```

不能 PASS。

---

# 250. BLOCKED — Security Defect

release-impacting security defect > 0：

不能 PASS。

---

# 251. BLOCKED — Scientific Overclaim

如果成功 demo导致：

```text
MAPPING_ONLY → VALIDATED

N/A → PASS

V4 0 → V4 > 0
```

等未经 scientific authority的 promotion：

不能 PASS。

---

# 252. BLOCKED — Report Loses Limitation

如果 finalized Report漏 mandatory scientific limitation：

不能 PASS。

---

# 253. BLOCKED — Recipe Executes

如果 Recipe浏览/交互会：

```text
create Job
execute Tool
```

不能 PASS。

---

# 254. BLOCKED — Latest Rebinding

如果 historical/reload path使用：

```text
latest
nearest
fuzzy
```

科学绑定：

不能 PASS。

---

# 255. BLOCKED — Scope Baseline Drift

如果当前产品为 demo需要：

扩大 Initial Release scope：

必须：

```text
BLOCKED /
INITIAL_RELEASE_SCOPE_DRIFT
```

---

# 256. BLOCKED — Feature Needed

如果 demo失败原因是：

```text
missing new scientific capability
```

不能在 13-2实现。

返回 reviewer。

---

# 257. Non-Blockers

以下可保持：

```text
V4 = 0

numeric cross-platform reference N/A

formal WCAG certification absent

macOS not current scientific release target

sealed accessibility limitations

sealed unsupported inputs

Future Scope unavailable

bounded external live-provider transient issue
if deterministic authority remains PASS
and sealed policy allows
```

---

# 258. Successful Final State

成功后：

```text
Phase 13-2:
PASS /
SEVEN_CANONICAL_REAL_USER_E2E_DEMONSTRATIONS_COMPLETED /
REAL_PRODUCT_PATHS_VERIFIED /
QUEUE_ARCHIVED

PHASE13_DEMO_FAMILIES = 7

PHASE13_2_DEMOS_EXECUTED = 7

DEMO_PASS_OR_EXPLICIT_LIMIT = 7/7

RELEASE_CRITICAL_INTEGRATION_DEFECTS = 0

SCIENTIFIC_DEFECTS = 0

SECURITY_DEFECTS = 0

Phase 13:
IN_PROGRESS /
REAL_USER_E2E_VALIDATED

Phase 13-3:
REVIEWER_GATE /
AWAITING REVIEWER PROMPT

Initial Release:
NOT_COMPLETE

TASK_BLOCK_COUNT = 0

PHASE13_3_EXECUTABLE_TASK_CREATED = NO

PHASE14_CREATED = NO
```

---

# 259. Meaning of Phase 13-2 Completion

可以说：

```text
All seven canonical Initial Release scientific
demonstrations have been executed through real
user-facing product paths.

The demonstrations traversed the actual Intent,
Eligibility, Planner, Runtime, registered Adapter,
service-backed persistence, Artifact, Workspace and
Report/Recipe authorities without handcrafted Plan,
Job, Artifact or Workspace injection.

The required imperfect-user and negative-path scenarios
were also exercised.
```

---

# 260. What Completion Does NOT Mean

不能说：

```text
Initial Release is complete.

The product is release-ready.

Every scientific result is independently reference validated.

All unsupported inputs are now supported.

All Future Scope is implemented.

Formal accessibility certification is complete.

Phase 13-3 is complete.

Phase 13-5 final acceptance passed.

Phase 14 is authorized.
```

---

# 261. Phase 13-3 Gate

最终：

```text
Phase 13-3:
REVIEWER_GATE /
AWAITING REVIEWER PROMPT

PHASE13_3_EXECUTABLE_TASK_CREATED = NO
```

---

# 262. Stop Rule

完成 Phase 13-2 并归档后立即停止。

不得：

```text
write final release documentation package

perform targeted polish

fix discovered production defects

run final release acceptance

declare Initial Release complete

start Phase 13-3

start Phase 13-4

start Phase 13-5

start Phase 13-6

create Phase 14
```

---

# 263. Final Return to Reviewer

必须返回：

```text
Phase 13-2 conclusion

implementation/evidence SHA

implementation exact-SHA CI

completion SHA

archive SHA

failed candidates

Fact Model hash

corrected Scope Baseline hash

Phase 12 baseline hash

7 demo statuses

7 demo exact fixture IDs

canonical prompt outcomes

paraphrase outcomes

real user-entry proof

Planner proof

Runtime proof

registered Adapter proof

PostgreSQL/Redis/MinIO proof

Artifact manifests

Workspace-from-real-Job proof

Finding/Evidence/Provenance results

Report/Recipe results

negative-path results

clarification boundary result

provider deterministic result

bounded live DeepSeek result

mobile real-Job result

browser results

scientific comparison result

release findings

documentation gaps

targeted polish findings

P13X2 8/8

Phase 13-3 handoff state

TASK_BLOCK_COUNT

HEAD/origin/worktree
```

然后等待 reviewer。

---

# 264. Final Required Status Block

如果成功，结果末尾必须明确输出：

```text
PHASE_13_2 = PASS

PHASE13_DEMO_FAMILIES = 7

PHASE13_2_DEMOS_EXECUTED = 7

DEMO_PASS_OR_EXPLICIT_LIMIT = 7/7

REAL_USER_ENTRY_E2E = YES

REAL_PERSISTENCE_USED = YES

REAL_QUEUE_USED = YES

REAL_QUEUE_WORKER_RUNTIME_USED = YES

REGISTERED_ADAPTER_EXECUTION_USED = YES

PERSISTED_ARTIFACT_USED = YES

WORKSPACE_FROM_REAL_JOB = YES

REPORT_FROM_REAL_PERSISTED_FACTS = YES

HANDCRAFTED_ANALYSISPLAN_INJECTION = 0

HANDCRAFTED_JOB_INJECTION = 0

HANDCRAFTED_TOOLCALL_INJECTION = 0

HANDCRAFTED_ARTIFACT_INJECTION = 0

HANDCRAFTED_WORKSPACE_INJECTION = 0

HANDCRAFTED_INTERPRETATION_INJECTION = 0

HANDCRAFTED_FINDING_INJECTION = 0

HANDCRAFTED_EVIDENCE_INJECTION = 0

HANDCRAFTED_REPORT_INJECTION = 0

HANDCRAFTED_RECIPE_INJECTION = 0

AMBIGUOUS_INTENT_CASE = PASS

ONE_ROUND_CLARIFICATION_CASE = PASS

SECOND_ROUND_TYPED_FAILURE_CASE = PASS

UNSUPPORTED_CAPABILITY_CASE = PASS

UNSUPPORTED_LIMITED_INPUT_CASE = PASS

PARTIAL_EXECUTION_CASE = PASS

HISTORICAL_STALE_RECOVERY_CASE = PASS

PROVIDER_FAILURE_CASE = PASS

LIMITATION_BEARING_REPORT_CASE = PASS

RELEASE_CRITICAL_INTEGRATION_DEFECTS = 0

SCIENTIFIC_DEFECTS = 0

SECURITY_DEFECTS = 0

REGISTRY = 62

DATAPROFILE = 2.4

ANALYSIS_INTENT = 1.0

PHASE13_CLARIFICATION_MAX_ROUNDS = 1

PHASE13_CLARIFICATION_MAX_QUESTIONS = 3

PHASE13_SECOND_CLARIFICATION_ROUND =
TYPED_FAILURE

ELIGIBILITY_RESOLUTION = 1.0

ANALYSIS_PLAN = 0.1 / 0.2

MIGRATION =
0007_phase10m1_workspace_domain

INITIAL_RELEASE_FACT_MODEL_HASH =
e0248d502e4a442bb9596a8d2f6fe6d7fdefe61c41121ae08736734ce4004a06

INITIAL_RELEASE_SCOPE_BASELINE_HASH =
93dea4a2b0bf31215ab2af1952b16ac47b20b7ed9b111bb2fb60ef70dd431627

P13X2_ACCEPTANCE = 8/8

PHASE_13 =
IN_PROGRESS /
REAL_USER_E2E_VALIDATED

PHASE_13_3 =
REVIEWER_GATE /
AWAITING REVIEWER PROMPT

PHASE13_3_EXECUTABLE_TASK_CREATED = NO

INITIAL_RELEASE_COMPLETE = NO

TASK_BLOCK_COUNT = 0

PHASE14_CREATED = NO

HEAD == origin/master

WORKTREE_CLEAN = YES
```




## 执行结果

- 完成时间：2026-08-11 18:17:55 +08:00
- 状态：失败 / `BLOCKED_BY_RELEASE_CRITICAL_INTEGRATION_DEFECTS`
- 修改文件：`.github/workflows/ci.yml`、`scripts/generate_phase13_2_blocker_evidence.py`、`tests/test_phase13_2_blocker_evidence.py`、`docs/phase13/`、`docs/phase13/evidence/phase13_2_seven_real_user_e2e/`、`docs/ROADMAP.md`、`persistent/*.md`、`results.md`、`TASKS.md`
- 修改摘要：完成 Phase 13-2 确定性真实用户入口预检和失败证据封存；未修改生产代码、科学算法、Registry、DataProfile、数据库、API 或依赖。
- 阻断原因：`P13-RF-001`（Planner 拒绝 parser/schema 已产生并支持的 DataProfile 2.3/2.4，阻断 Demo 4/7）、`P13-RF-002`（实验 XRD sealed JSON 无 parser/eligibility 产品入口，阻断 Demo 3）、`P13-RF-003`（phonon/BZ canonical 与 alternate intent 均为 `INTENT_UNSUPPORTED`，阻断 Demo 5）。`P13-RF-004` 为 Demo 6 canonical prompt 与可达 alternate 不一致的 P1 文档契约缺陷。
- 已尝试方法：核验 Phase 13-1 exact-SHA CI 和 handoff；校验 11 个 fixture；通过当前 parser、DataProfile builder、AnalysisIntent、Eligibility、Planner 对七个 canonical/alternate prompt 做确定性入口探测；核验本地 PostgreSQL/Redis/MinIO/Playwright/DeepSeek 环境可用性。阻断发生在真实 Job 创建之前，因此未启动 live provider、真实 queue/runtime 或浏览器演示，也未使用 handcrafted injection 绕过。
- 测试结果：生成器 PASS；Phase 13 聚焦治理测试 `26 passed`；完整后端 `1339 passed, 50 skipped`；前端 `455 passed`；typecheck、production build、lock、diff 均 PASS。Phase 13-2 demos executed = `0/7`，PASS claims = `0`。

---END---
