---TASK---
 状态：已完成

# Phase 13-1 Reviewer Prompt

# Release-Critical Integration Gap Closure

# Zero-Gap Verification Closure

你现在执行：

# Phase 13-1：Release-Critical Integration Gap Closure

当前 13-0 authority 已给出：

```text
RELEASE_BLOCKERS = 0

RELEASE_CRITICAL_INTEGRATION_GAPS = 0
```

因此本次 Phase 13-1 的执行模式固定为：

# ZERO-GAP VERIFICATION CLOSURE

中文：

# 发布关键集成零缺口独立验证封板

本阶段不是常规 implementation phase。

---

# 0. Phase 13 Sequence

当前 roadmap：

```text
Phase 12
COMPLETE /
PRODUCT_EXPERIENCE_REDESIGN_VALIDATED_AND_SEALED

Phase 13-0
COMPLETE /
FINAL_FACTS_ALIGNED /
INITIAL_RELEASE_SCOPE_SEALED /
FACT_ALIGNMENT_CORRECTED

Phase 13-1
CURRENT /
ZERO-GAP VERIFICATION CLOSURE

Phase 13-2
Seven Canonical Real-User E2E Demonstrations

Phase 13-3
Documentation + Reproducibility Package

Phase 13-4
Targeted Final Product Polish

Phase 13-5
Final Regression + Release Acceptance

Phase 13-6
Final Archive + Presentation Package
```

---

# 1. Mission

Phase 13-1 的唯一核心任务：

```text
independently verify

that the release-critical integration gap count
really is zero
```

需要证明：

```text
real user entry exists

→ exact data/profile path exists

→ Intent/Clarification authority resolves

→ Eligibility resolves

→ Planner contract can reach intended capability

→ PlanValidator accepts approved semantics

→ QueueWorkerRuntime is wired

→ Registry entry resolves

→ registered Adapter exists

→ service-backed persistence is wired

→ persisted Artifact authority exists

→ Workspace projection exists

→ interpretation/trust path exists where applicable

→ Report/Recipe source path exists where applicable
```

而不是：

```text
actually execute all seven complete user demos
```

七个完整 real-user E2E 属于：

```text
Phase 13-2
```

---

# 2. Fundamental Boundary

必须：

```text
ZERO_GAP_VERIFICATION
!=
SEVEN_DEMO_EXECUTION
```

以及：

```text
INTEGRATION_PREFLIGHT
!=
USER_E2E_PASS
```

以及：

```text
EXISTING_SERVICE_INTEGRATION_PASS
!=
FINAL_PRODUCT_DEMO_PASS
```

---

# 3. Default Change Authority

本阶段默认：

```text
PHASE13_1_PRODUCTION_CODE_CHANGE_AUTHORITY = NONE

PHASE13_1_SCIENTIFIC_CHANGE_AUTHORITY = NONE

PHASE13_1_PRODUCT_ARCHITECTURE_CHANGE_AUTHORITY = NONE
```

13-0 已报告 0 gap。

因此执行器不能为了“完成 13-1”主动寻找代码改动。

---

# 4. Critical Discovery Rule

如果 13-1 独立验证发现真实：

```text
RELEASE_BLOCKER > 0

or

RELEASE_CRITICAL_INTEGRATION_GAP > 0
```

必须：

```text
BLOCKED /
ZERO_GAP_ASSUMPTION_INVALIDATED
```

然后返回 reviewer。

不得在本 Prompt 下直接修。

原因：

```text
13-0 sealed zero gaps

→ 13-1 independently disproves it

→ reviewer must reassess
```

不能：

```text
discover gap
→ silently fix
→ report zero gap
```

---

# 5. Reviewer Authorization

本 Prompt 正式授权：

```text
AUTHORIZED_PHASE = Phase 13-1

AUTHORIZED_MODE =
ZERO_GAP_VERIFICATION_CLOSURE

MAX_PHASES_EXECUTED = 1
```

不授权：

```text
Phase 13-2
Phase 13-3
Phase 13-4
Phase 13-5
Phase 13-6
Phase 14
```

---

# 6. Mandatory Phase 13-0 Dependency

必须从真实 Git/repository 验证：

```text
Phase 13-0 = PASS

original implementation complete

clarification correction complete

both queues archived
```

---

# 7. Original 13-0 Lifecycle

当前 reviewer-known：

```text
Implementation:
6217d042d0190c43144e402e4479aa9810b8e9d0

Exact-SHA CI:
31451202923
PASS

Completion:
0af74ff078e1dab6324852a8329cea42bf092acb

Archive:
7a554cd91b0638898bfe097972f29a097540b514
```

但必须通过 Git动态验证。

---

# 8. Clarification Correction Lifecycle

当前 reviewer-known：

```text
Correction implementation:
abe4bd68363f9eb9c357a840b17d0f2c216ebfee

Correction exact-SHA CI:
31455125693
PASS

Correction completion:
d488c53...

Correction archive:
7bf991c6524db0544f8e97024b6a5d30868ebaf5
```

必须从 Git验证 exact values。

---

# 9. Corrected Release Authorities

必须验证 current canonical：

```text
INITIAL_RELEASE_FACT_MODEL_HASH =
e0248d502e4a442bb9596a8d2f6fe6d7fdefe61c41121ae08736734ce4004a06
```

以及 corrected：

```text
INITIAL_RELEASE_SCOPE_BASELINE_HASH =
93dea4a2b0bf31215ab2af1952b16ac47b20b7ed9b111bb2fb60ef70dd431627
```

旧 Scope Baseline：

```text
8e8b4f659888635192d259eee90f3befdd655cacb292a78c5e13c20a5fdabdde
```

必须仅作为：

```text
HISTORICAL /
SUPERSEDED
```

不得重新成为 current authority。

---

# 10. Clarification Authority

必须验证：

```text
AnalysisIntent = 1.0

PHASE13_CLARIFICATION_MAX_ROUNDS = 1

PHASE13_CLARIFICATION_MAX_QUESTIONS = 3

PHASE13_SECOND_CLARIFICATION_ROUND =
TYPED_FAILURE
```

要求：

```text
CURRENT_CANONICAL_TWO_ROUND_ASSERTIONS = 0
```

---

# 11. Repository Entry Gate

必须：

```text
branch = master

HEAD == origin/master

worktree = clean

TASK_BLOCK_COUNT = 0
```

并且：

```text
Phase 13-1 task absent

Phase 13-2 task absent

Phase 14 absent
```

否则：

```text
PHASE_13_1_ENTRY_GATE = BLOCKED
```

---

# 12. Entry Hash Verification

必须重新生成/验证：

```text
InitialReleaseFactModel
```

要求：

```text
hash =
e0248d502e4a442bb9596a8d2f6fe6d7fdefe61c41121ae08736734ce4004a06
```

---

# 13. Corrected Scope Baseline Verification

必须重新生成：

```text
InitialReleaseScopeBaseline
```

要求：

```text
hash =
93dea4a2b0bf31215ab2af1952b16ac47b20b7ed9b111bb2fb60ef70dd431627
```

---

# 14. Baseline Determinism

至少连续生成两次：

```text
RUN_1 == RUN_2
```

要求：

```text
INITIAL_RELEASE_SCOPE_BASELINE_DETERMINISM = PASS
```

---

# 15. Phase 12 Baseline

必须继续验证：

```text
PHASE12_PRODUCT_EXPERIENCE_BASELINE_HASH =
29936236efe74a82ad97507385839aa4f5692d26b496292af3172940647973d4
```

要求：

```text
PHASE12_BASELINE_MUTATION_BY_13_1 = 0
```

---

# 16. Phase 11 Scientific Authority

必须保持：

```text
Phase 11 =
COMPLETE /
REFERENCE_VALIDATED_WITH_EXPLICIT_LIMITS
```

---

# 17. Frozen Scientific Baseline

必须：

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

# 18. Validation Facts

继续：

```text
golden records = 12

PASS_INVARIANT = 8

NOT_APPLICABLE = 4

failures = 0

V4 = 0
```

---

# 19. Scientific Honesty

必须：

```text
SUPPORTED_EQUALS_VALIDATED = NO

E2E_PASS_EQUALS_REFERENCE_VALIDATED = NO

BROWSER_PASS_EQUALS_SCIENTIFIC_PASS = NO

SERVICE_PASS_EQUALS_SCIENTIFIC_PASS = NO

SCREENSHOT_NUMERIC_SCIENTIFIC_AUTHORITY = NONE

FRONTEND_SCIENTIFIC_AUTHORITY = NONE
```

---

# 20. Phase 13-0 Gap Authority

必须读取 current：

```text
Phase13ReleaseCriticalGapRegistry
```

要求当前：

```text
RELEASE_BLOCKERS = 0

RELEASE_CRITICAL_INTEGRATION_GAPS = 0

UNCLASSIFIED_RELEASE_GAPS = 0
```

---

# 21. Existing Nonblocking Records

必须保留 current：

```text
NONBLOCKING_LIMITATIONS
```

以及：

```text
Phase 13-2 seven-demo execution evidence gap
```

不得因为尚未执行七 demo就错误升级为：

```text
RELEASE_CRITICAL_INTEGRATION_GAP
```

13-2 evidence 尚缺属于计划中的验证工作，

不是已知产品 broken integration。

---

# 22. 13-1 Handoff

必须读取唯一 canonical：

```text
Phase13_1ReleaseCriticalIntegrationGapHandoff
```

或 current repository equivalent。

---

# 23. Required Handoff Contents

至少确认：

```text
Initial Release Fact Model hash

corrected Scope Baseline hash

gap registry

zero-gap conclusion

seven demo registry

fixture registry

no-injection policy

real persistence/runtime policy

provider policy

Phase 11 authority

Phase 12 baseline

P13X1 acceptance IDs

13-2 entry criteria
```

---

# 24. Missing Handoff

如果 handoff无法解析：

```text
BLOCKED /
PHASE13_1_HANDOFF_INVALID
```

---

# 25. Phase 13 Acceptance Registry

必须读取 sealed：

```text
Phase13AcceptanceRegistry
```

current expected total：

```text
56
```

如果 repository actual不同：

使用 actual authority。

---

# 26. P13X1 Acceptance IDs

必须读取 exact：

```text
P13X1-A01
...
P13X1-A08
```

的 canonical wording。

不得由 Prompt改写。

---

# 27. P13X1 Immutable

要求：

```text
P13X1_EXPECTED = 8

MISSING = 0

EXTRA = 0

DUPLICATE = 0

CONFLICTING = 0

SHORTHAND = 0
```

---

# 28. Reviewer Interpretation of P13X1

repository exact wording为 authority。

但实际 verification 至少应 equivalent覆盖：

```text
A.
corrected Phase 13-0 authority
and baseline integrity

B.
complete release-critical integration
seam inventory

C.
seven-demo entry-path
preflight readiness

D.
Registry / Adapter / Runtime /
persistence / Workspace integration

E.
negative-path /
no-injection /
provider-boundary verification

F.
independent zero-gap conclusion

G.
regression / browser /
service / science / security gates

H.
lifecycle closure
and Phase 13-2 handoff
```

---

# 29. 13-1 Is Independent Verification

不能简单：

```text
read RELEASE_BLOCKERS = 0
→ PASS
```

必须重新验证 supporting evidence。

---

# 30. Integration Seam Registry

必须建立：

```text
Phase13IntegrationSeamVerificationMatrix
```

---

# 31. Seam Categories

至少：

```text
Resource ingestion

Dataset/version resolution

DataProfile

AnalysisIntent

Clarification

EligibilityResolution

Planner

AnalysisPlan

PlanValidator

Queue submission

Redis queue

QueueWorkerRuntime

Tool Registry

Adapter resolution

Adapter execution boundary

PostgreSQL persistence

MinIO Artifact persistence

Artifact retrieval

Workspace projection

Workspace selection

Interpretation

Finding/Evidence

Provenance

Report source eligibility

Report finalization

Recipe generation

Historical recovery

Cross-project isolation

Stale identity behavior

Security boundary
```

---

# 32. Seam Matrix Fields

每 row：

```text
seamId

producer

consumer

contract

exact identity

current implementation path

test/evidence

sevenDemoDependencies

negativePathDependencies

status

gapIfFailed
```

---

# 33. Seam Status Vocabulary

只能：

```text
VERIFIED

VERIFIED_WITH_EXPLICIT_LIMIT

NOT_APPLICABLE

GAP_FOUND
```

不得：

```text
probably works
```

---

# 34. Zero-Gap Condition

最终：

```text
GAP_FOUND_COUNT = 0
```

否则不能 Phase 13-1 PASS。

---

# 35. Seven Demo Registry

必须重新确认恰好：

```text
7
```

families。

---

# 36. Demo 1

```text
Dataset Intelligence
+ Composition Space
```

---

# 37. Demo 2

```text
Materials ML
```

---

# 38. Demo 3

```text
Structure
+ coordination
+ local environment
+ polyhedra
+ experimental XRD
```

---

# 39. Demo 4

```text
Trajectory
+ RDF
+ MSD
+ diffusion
```

---

# 40. Demo 5

```text
Phonon
+ Brillouin Zone
```

---

# 41. Demo 6

```text
Volumetric
```

---

# 42. Demo 7

```text
Electronic Band
+ DOS
```

---

# 43. Phase 13-1 Demo Rule

对七个 demo：

只做：

```text
PRE-FLIGHT /
INTEGRATION READINESS
```

不能：

```text
DEMO_PASS
```

---

# 44. Demo Execution Counts

必须始终：

```text
PHASE13_2_DEMOS_EXECUTED = 0

PHASE13_2_DEMO_PASS_CLAIMS = 0
```

直到 13-2。

---

# 45. Demo Preflight Matrix

每 demo建立：

```text
DemoIntegrationReadinessRecord
```

至少：

```text
demoId

fixtureIds

input format

Profile expectations

required capability families

eligible Tool set

Planner reachability

required plan semantics

Runtime compatibility

registered Adapter availability

Artifact contracts

Workspace mapping

interpretation applicability

Finding/Evidence applicability

Report eligibility

Recipe eligibility

negative cases

readiness

blocking reason
```

---

# 46. Demo Readiness Vocabulary

只允许：

```text
READY_FOR_REAL_USER_E2E

READY_WITH_EXPLICIT_NONBLOCKING_LIMIT

BLOCKED
```

---

# 47. Zero-Gap Expected Demo State

为了 13-1 PASS：

七个必须全部：

```text
READY_FOR_REAL_USER_E2E
```

或：

```text
READY_WITH_EXPLICIT_NONBLOCKING_LIMIT
```

其中 limit必须已经在 sealed Initial Release limitation registry。

---

# 48. New Demo Blocker

任一 demo：

```text
BLOCKED
```

即：

```text
ZERO_GAP_ASSUMPTION_INVALIDATED
```

不能继续 PASS。

---

# 49. Fixture Registry

必须验证 retained：

```text
fixture records = 11
```

如果 current canonical仍是 11。

---

# 50. Fixture Integrity

要求：

```text
MISSING_FIXTURES = 0

CHECKSUM_MISMATCH = 0

UNLICENSED_REQUIRED_FIXTURES = 0

EXTERNAL_DOWNLOADS_REQUIRED = 0
```

---

# 51. No External Download

13-1：

```text
EXTERNAL_DOWNLOADS = 0
```

---

# 52. Fixture-to-Demo Coverage

必须：

```text
ALL_7_DEMOS_HAVE_EXACT_FIXTURE_COVERAGE = YES
```

---

# 53. Resource Identity

fixture必须具有 exact：

```text
fixtureId

checksum

resource kind

expected data/profile semantics
```

---

# 54. No Filename Authority

必须：

```text
FILENAME_SCIENTIFIC_AUTHORITY = 0
```

---

# 55. Profile Preflight

对所有 seven demo fixtures：

静态/contract verification必须证明：

```text
DataProfile 2.4
can represent required prerequisites
```

这不是执行 demo。

---

# 56. Profile Preflight Does Not Promote Support

若 Profile can parse/describe：

不代表：

```text
scientific tool validated
```

继续保持轴分离。

---

# 57. Intent Preflight

确认 canonical natural-language prompts：

可以进入现有：

```text
AnalysisIntent 1.0
```

contract。

不得直接创建 resolved Intent。

---

# 58. Clarification Preflight

必须确认：

```text
MAX_ROUNDS = 1
MAX_QUESTIONS = 3
SECOND_ROUND = TYPED_FAILURE
```

---

# 59. Clarification Negative Preflight

negative registry中的：

```text
request requiring second clarification round
```

必须预期：

```text
typed non-ready/failure
```

并：

```text
Plan = 0
Job = 0
Queue = 0
```

---

# 60. Eligibility Preflight

必须证明 intended seven-demo capability families：

存在 current deterministic：

```text
EligibilityResolver
```

路径。

---

# 61. Eligibility Does Not Execute

13-1不要通过创建 real user demo Job来证明。

使用：

```text
existing contract tests
service integration probes
static Registry/Profile compatibility checks
```

---

# 62. Planner Preflight

必须确认：

```text
capability-aware Planner
```

拥有到七个 demo families 的 current route/metadata。

---

# 63. No Tool-ID User Requirement

任何 demo若需要用户知道：

```text
internal Tool ID
```

才能达到 capability：

```text
GAP_FOUND
```

---

# 64. Plan Contract Preflight

确认七 demo可能产生的计划：

符合：

```text
AnalysisPlan 0.1
or
AnalysisPlan 0.2
```

current contract。

---

# 65. Plan 0.1

不得 invent dependencies。

---

# 66. Plan 0.2

必须使用 exact:

```text
producer
consumer
binding
ports
Artifact contract
```

---

# 67. PlanValidator Seam

确认 expected demo plan semantics：

有对应 current PlanValidator support。

---

# 68. Runtime Seam

确认：

```text
QueueWorkerRuntime
```

支持七 demo所需：

```text
independent steps

0.2 dependency execution

partial branch semantics
```

按实际 demo requirement。

---

# 69. No Runtime Execution Yet

这里验证 wiring/contract/tests。

不执行七个完整 user demo。

---

# 70. Registry Seam

必须：

```text
LIVE_REGISTRY_COUNT = 62
```

且所有 seven-demo所需 exact Tool/version：

```text
present

registered

adapter-backed

current
```

---

# 71. Manifest-Only Tool Rejection

任何只有：

```text
manifest
```

却没有 real Adapter 的能力：

不能算 ready。

---

# 72. Adapter Resolution Matrix

对七 demo所需 tools：

建立：

```text
Tool ID
→ version
→ Adapter
→ input contract
→ output contract
```

要求：

```text
UNRESOLVED_REQUIRED_ADAPTERS = 0
```

---

# 73. Adapter Does Not Mean E2E PASS

仍然：

```text
ADAPTER_EXISTS
!=
DEMO_PASS
```

---

# 74. Queue Seam

确认 real production path：

```text
Job
→ queue
→ worker
```

存在。

---

# 75. Redis Seam

service-backed verification：

```text
Redis required queue path = PASS
```

---

# 76. PostgreSQL Seam

必须验证 release relevant persistence：

```text
Dataset/Profile references

Intent

Plan

Job

ToolCall

Artifact metadata

Workspace

Report

Recipe
```

按 current actual schema。

---

# 77. MinIO Seam

必须确认 persisted Artifact object path：

```text
write

retrieve

checksum/integrity
```

现有 service-backed tests PASS。

---

# 78. No Mock Persistence Authority

必须：

```text
MOCK_PERSISTENCE_AS_RELEASE_AUTHORITY = NO
```

---

# 79. Artifact Seam

七 demo的 required output families：

必须存在 formal persisted Artifact contract。

---

# 80. Artifact Identity

必须：

```text
exact

versioned

checksum-bound
```

---

# 81. No Latest Binding

必须：

```text
LATEST_SCIENTIFIC_BINDING = 0
```

---

# 82. No Nearest Binding

```text
NEAREST_SCIENTIFIC_BINDING = 0
```

---

# 83. No Fuzzy Binding

```text
FUZZY_SCIENTIFIC_BINDING = 0
```

---

# 84. Workspace Seam

必须证明：

```text
real completed Job
→ idempotent Workspace projection
```

current path存在。

---

# 85. Workspace Identity

继续：

```text
ONE_WORKSPACE_PER_JOB = YES
```

---

# 86. Workspace Authority

必须：

```text
server authority retained

URL exact selection retained

localStorage canonical authority = NONE

sessionStorage canonical authority = NONE
```

---

# 87. Viewer Mapping Seam

每 required seven-demo Artifact family：

必须有 current product presentation mapping。

如果 presentation formally unsupported：

必须为：

```text
explicit sealed limitation
```

否则 gap。

---

# 88. Heavy Viewer Lifecycle

仅做 retained smoke：

```text
metadata first

lazy active viewer

request cancellation

cleanup
```

不执行 full seven-demo browser flows。

---

# 89. Interpretation Seam

对于 current interpretation-supported outputs：

确认：

```text
persisted Artifact
→ ScientificEvidenceBundle
→ ScientificClaim
→ GroundedScientificInterpretation
```

authority wiring存在。

---

# 90. No Interpretation Fabrication

对于不适用的 capability：

必须：

```text
NOT_APPLICABLE
```

不能为了 demo统一而制造 Finding。

---

# 91. Evidence Seam

必须确保 exact：

```text
Finding
→ Evidence
→ Artifact
→ Tool/version
→ input
```

authority仍 intact。

---

# 92. Provenance Seam

七 demo最终 required provenance：

必须能由 existing persisted lineage提供。

---

# 93. Report Source Seam

对每 demo：

确认 intended persisted outputs存在 current：

```text
Report source eligibility
```

路径。

---

# 94. Report Source Does Not Require New Authority

若某 viewer sub-selection不能直接进入 Report：

existing whole-Artifact/panel fallback若已批准：

可视为 ready。

不能在 13-1创造新 Report source semantics。

---

# 95. Report Finalization Seam

必须验证 existing：

```text
explicit finalize

immutable Report

paired Recipe
```

service/integration wiring intact。

---

# 96. Recipe Seam

保持：

```text
RECIPE_EXECUTION_AUTHORITY = NONE
```

---

# 97. Historical Recovery Seam

至少验证：

```text
historical Job

→ exact Workspace

→ exact Artifact

→ exact Report/Recipe
```

current tests/contracts存在。

---

# 98. Stale Identity Seam

验证：

```text
stale source
→ typed stale
```

而不是：

```text
latest rebind
```

---

# 99. Partial Execution Seam

确认 current Runtime：

```text
failed branch

→ blocks descendants

→ preserves independent success
```

并可在 Workspace/Report中准确呈现。

---

# 100. Unsupported Input Seam

确认：

```text
unsupported input
→ typed unsupported
→ no execution
```

---

# 101. Unsupported Capability Seam

确认：

```text
ineligible capability
→ Eligibility rejection
→ no Plan/Job enqueue
```

---

# 102. Provider Failure Seam

13-1必须验证 current provider failure path是：

```text
typed
non-executing
context-preserving
```

---

# 103. Real LLM Calls

13-1：

```text
REAL_LLM_CALLS = 0
```

---

# 104. Provider Test Mode

可以使用：

```text
deterministic/fake provider contract tests
```

验证 wiring。

不得用真实 DeepSeek作为 13-1 zero-gap authority。

---

# 105. Bounded Live DeepSeek Policy

只验证 policy本身仍 sealed。

不要执行。

---

# 106. Provider Policy

继续：

```text
REAL_PROVIDER = DEEPSEEK_ONLY

endpoint =
https://api.deepseek.com

models =
deepseek-v4-flash
deepseek-v4-pro

key =
DEEPSEEK_KEY
```

actual repository authority优先。

---

# 107. No Provider Expansion

必须：

```text
NEW_PROVIDER = 0
```

---

# 108. User Simulation Contract

重新核验：

```text
Canonical Scientist Persona = SEALED

Imperfect / Exploratory Persona = SEALED
```

---

# 109. No-Injection Policy

必须继续：

```text
HANDCRAFTED_PLAN_INJECTION = 0

HANDCRAFTED_JOB_INJECTION = 0

HANDCRAFTED_TOOLCALL_INJECTION = 0

HANDCRAFTED_ARTIFACT_INJECTION = 0

HANDCRAFTED_WORKSPACE_INJECTION = 0

HANDCRAFTED_FINDING_INJECTION = 0

HANDCRAFTED_EVIDENCE_INJECTION = 0

HANDCRAFTED_REPORT_INJECTION = 0

HANDCRAFTED_RECIPE_INJECTION = 0
```

---

# 110. 13-1 Must Not Weaken No-Injection

禁止为了让 13-2 easier：

引入：

```text
test-only plan shortcut

test-only artifact preload

test-only Workspace injection
```

---

# 111. Real Persistence Contract

必须保持：

```text
REAL_PERSISTENCE_REQUIRED = YES
```

---

# 112. Real Runtime Contract

```text
REAL_RUNTIME_REQUIRED = YES
```

---

# 113. Registered Adapter Contract

```text
REGISTERED_ADAPTER_EXECUTION_REQUIRED = YES
```

---

# 114. Real Job Workspace Contract

```text
WORKSPACE_FROM_REAL_JOB_REQUIRED = YES
```

---

# 115. Report Contract

```text
REPORT_FROM_REAL_PERSISTED_FACTS_REQUIRED = YES
```

---

# 116. Negative-Path Registry

必须重新核验至少：

```text
ambiguous Intent

second-round clarification boundary

unsupported capability

limited/unsupported input

partial execution

stale recovery

provider failure

limitation-bearing Report
```

---

# 117. Negative Path Readiness

13-1只验证：

```text
typed path exists
+
test/evidence exists
```

不执行完整 13-2 user scenarios。

---

# 118. Cross-Project Isolation Seam

必须 service-backed验证 current enforcement：

```text
Project A
cannot consume Project B authority
```

---

# 119. Cross-Workspace Isolation

必须：

```text
Workspace A
cannot silently select/rebind Workspace B Artifact
```

---

# 120. Security Integration Seams

至少：

```text
Artifact inert

no arbitrary Python

no shell

no notebook

no HTML/JS execution

no iframe

no arbitrary filesystem access

no arbitrary network execution

Recipe non-executable

Recommendation non-executable
```

---

# 121. Secret Boundary

必须：

```text
NO_FRONTEND_LLM_SECRET_INPUT = PASS

NO_SECRET_PATTERN_HITS = PASS
```

---

# 122. Accessibility/Browser Boundary

13-1只需确认 Phase 12 sealed presentation foundation未漂移。

不是重新执行 Phase 12。

---

# 123. Phase 12 UX Baseline Drift

必须：

```text
PHASE12_PRODUCT_EXPERIENCE_BASELINE_DRIFT = 0
```

---

# 124. Release Claim Drift

必须检查：

```text
InitialReleaseClaimRegistry
```

未因 13-1发生：

```text
capability promotion

validation promotion

input-support promotion

browser/platform overclaim
```

---

# 125. Forbidden Claims

必须继续：

```text
all tools independently validated = forbidden

all numeric outputs cross-platform validated = forbidden

formal WCAG certified = forbidden

autonomous researcher = forbidden

arbitrary workflow engine = forbidden

DFT/GW execution platform = forbidden

Rietveld refinement = forbidden

executable Recipe = forbidden
```

---

# 126. Future Scope

必须保持 unqueued。

---

# 127. Not Planned

必须保持 unqueued。

---

# 128. Zero-Gap Evidence Must Be Positive

不能只证明：

```text
no issue found
```

要为关键 seams提供：

```text
positive contract/test/service evidence
```

---

# 129. No Seven-Demo Screenshots Required

13-1不能假装 13-2已经发生。

不得生成：

```text
seven demo PASS screenshots
```

---

# 130. Allowed Existing Evidence Reuse

可以引用：

```text
Phase 10
Phase 11
Phase 12
Phase 13-0
```

retained evidence。

但必须核验：

```text
still maps to current HEAD/contracts
```

---

# 131. Stale Evidence Rule

如果旧证据不再与 current authority/hash对应：

不能用于 zero-gap proof。

---

# 132. Evidence Freshness

13-1至少需要 fresh：

```text
repository audit

Registry/Adapter resolution

fixture checksums

baseline hashes

service-backed integration

contract integrity

gap reconciliation
```

---

# 133. Evidence Directory

建立：

```text
docs/phase13/evidence/
phase13_1_zero_gap_verification_closure/
```

---

# 134. Mandatory Evidence Files

至少：

```text
baseline.txt

entry_gate.md

phase13_0_authority_snapshot.json

clarification_correction_snapshot.json

fact_model_hash_verification.json

scope_baseline_hash_verification.json

phase12_baseline_verification.json

phase11_authority_verification.json

release_gap_registry_before.json

integration_seam_matrix.json

integration_seam_summary.json

seven_demo_preflight_matrix.json

demo1_preflight.json

demo2_preflight.json

demo3_preflight.json

demo4_preflight.json

demo5_preflight.json

demo6_preflight.json

demo7_preflight.json

fixture_integrity.json

fixture_demo_coverage.json

profile_prerequisite_matrix.json

intent_clarification_preflight.json

eligibility_preflight.json

planner_reachability_matrix.json

plan_validator_matrix.json

registry_adapter_matrix.json

runtime_capability_matrix.json

queue_service_matrix.json

persistence_matrix.json

artifact_contract_matrix.json

workspace_projection_matrix.json

interpretation_applicability_matrix.json

finding_evidence_provenance_matrix.json

report_recipe_integration_matrix.json

historical_recovery_matrix.json

partial_execution_matrix.json

unsupported_path_matrix.json

provider_failure_matrix.json

cross_project_isolation.json

stale_identity_matrix.json

no_injection_revalidation.json

security.md

scientific_authority_nonchange.json

release_claim_nonchange.json

release_gap_registry_after.json

phase13_2_entry_handoff.json

manifest.json

secret_scan.txt
```

---

# 135. Canonical Docs

至少：

```text
docs/phase13/
phase13_1_zero_gap_verification_closure.md

phase13_1_integration_seam_verification.md

phase13_1_seven_demo_preflight.md

phase13_1_release_gap_reconciliation.md

phase13_2_real_user_e2e_entry_handoff.md

phase13_1_completion.md
```

复用 repository canonical naming优先。

---

# 136. 13-2 Entry Handoff

成功后必须生成：

```text
Phase13_2RealUserE2EEntryHandoff
```

或 current canonical equivalent。

---

# 137. Handoff Must Include

至少：

```text
Fact Model hash

corrected Scope Baseline hash

Phase 12 baseline hash

Registry/DataProfile/migration

Clarification contract

7 demo IDs

11 fixture records

fixture checksums

canonical prompts

personas

negative paths

provider modes

no-injection policy

persistence/runtime policy

required service environment

expected Artifact families

Workspace expectations

Report/Recipe expectations

known limitations

zero-gap seam evidence

P13X2 acceptance IDs

13-2 execution prohibitions
```

---

# 138. Handoff Does Not Queue 13-2

必须：

```text
PHASE13_2_EXECUTABLE_TASK_CREATED = NO
```

---

# 139. Handoff State

成功可写：

```text
PHASE13_2_ENTRY_HANDOFF =
READY_FOR_REVIEWER
```

不能：

```text
PHASE13_2_EXECUTION_AUTHORIZED = YES
```

---

# 140. Production Code Freeze

必须：

```text
PHASE13_1_PRODUCTION_CODE_CHANGES = 0
```

---

# 141. Backend Behavior Freeze

```text
PHASE13_1_BACKEND_BEHAVIOR_CHANGES = 0
```

---

# 142. Frontend Behavior Freeze

```text
PHASE13_1_FRONTEND_BEHAVIOR_CHANGES = 0
```

---

# 143. Scientific Freeze

```text
PHASE13_1_SCIENTIFIC_BEHAVIOR_CHANGES = 0

PHASE13_1_NEW_SCIENTIFIC_TOOLS = 0

PHASE13_1_NEW_SCIENTIFIC_ALGORITHMS = 0

PHASE13_1_NEW_ARTIFACT_FAMILIES = 0
```

---

# 144. Contract Freeze

必须：

```text
NEW_DATAPROFILE_VERSION = 0

NEW_ANALYSISINTENT_VERSION = 0

NEW_ELIGIBILITY_VERSION = 0

NEW_ANALYSISPLAN_VERSION = 0
```

---

# 145. Database Freeze

```text
NEW_DATABASE_TABLES = 0

NEW_DATABASE_COLUMNS = 0

NEW_DATABASE_MIGRATIONS = 0
```

---

# 146. API Freeze

```text
NEW_PUBLIC_API_FAMILIES = 0
```

---

# 147. Dependency Freeze

```text
NEW_PYTHON_DEPENDENCIES = 0

NEW_FRONTEND_DEPENDENCIES = 0

LOCKFILE_CHANGES = 0
```

---

# 148. LLM Freeze

```text
NEW_LLM_CALL_SITES = 0

REAL_LLM_CALLS = 0
```

---

# 149. Frontend Science Freeze

```text
FRONTEND_SCIENTIFIC_RECOMPUTATION = 0
```

---

# 150. Queue Admission

Entry Gate PASS 后：

只创建：

```text
one Phase 13-1 zero-gap verification TASK block
```

要求：

```text
TASK_BLOCK_COUNT = 1

ACTIVE_TASK =
Phase 13-1 Zero-Gap Verification Closure

PHASE13_2_EXECUTABLE_TASK_CREATED = NO

PHASE14_CREATED = NO
```

---

# 151. Persistent State

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

仅记录 verification state。

不得改变 scientific facts。

---

# 152. ROADMAP Success State

成功后：

```text
Phase 12:
COMPLETE /
PRODUCT_EXPERIENCE_REDESIGN_VALIDATED_AND_SEALED

Phase 13-0:
COMPLETE /
FINAL_FACTS_ALIGNED /
INITIAL_RELEASE_SCOPE_SEALED /
FACT_ALIGNMENT_CORRECTED

Phase 13-1:
COMPLETE /
ZERO_GAP_VERIFIED /
RELEASE_CRITICAL_INTEGRATION_SEAMS_CLOSED

Phase 13:
IN_PROGRESS /
READY_FOR_REAL_USER_E2E_DEMONSTRATIONS

Phase 13-2:
REVIEWER_GATE /
AWAITING REVIEWER PROMPT

Initial Release:
NOT_COMPLETE

Phase 14:
NOT_CREATED
```

---

# 153. First Required Output

开始执行后的第一组必须输出：

```text
Phase 13-1 Entry Gate
+ Corrected Release Authority
+ Zero-Gap Verification Admission
```

至少确认：

1. branch；
2. HEAD；
3. origin/master；
4. clean worktree；
5. TASK_BLOCK_COUNT=0；
6. original 13-0 implementation SHA；
7. original exact-SHA CI；
8. original completion SHA；
9. original archive SHA；
10. clarification correction SHA；
11. correction exact-SHA CI；
12. correction completion SHA；
13. correction archive SHA；
14. Fact Model hash；
15. corrected Scope Baseline hash；
16. Phase 12 baseline hash；
17. Registry=62；
18. DataProfile=2.4；
19. AnalysisIntent=1.0；
20. clarification rounds=1；
21. max questions=3；
22. second round typed failure；
23. EligibilityResolution=1.0；
24. AnalysisPlan=0.1/0.2；
25. migration=0007；
26. release blockers=0；
27. release critical integration gaps=0；
28. seven demo contracts=7；
29. demos executed=0；
30. fixture records=11；
31. P13X1 exact IDs resolve；
32. 13-1 handoff resolves；
33. Phase 13-2 task absent；
34. Phase14 absent；
35. no production change required；
36. no scientific change required。

成功：

```text
PHASE_13_1_ENTRY_GATE = PASS

PHASE_13_0_DEPENDENCY = VERIFIED

PHASE_13_0_CORRECTION = VERIFIED

PHASE_13_1_MODE =
ZERO_GAP_VERIFICATION_CLOSURE

PHASE_13_1_QUEUE_ADMISSION =
AUTHORIZED

PHASE_13_1_PRODUCTION_CHANGE_AUTHORITY =
NONE

PHASE_13_1_SCIENTIFIC_CHANGE_AUTHORITY =
NONE

PHASE_13_2_EXECUTION_AUTHORITY =
NONE

PHASE_13_1_READINESS =
READY_FOR_INDEPENDENT_ZERO_GAP_VERIFICATION
```

---

# 154. Required Execution Sequence

严格：

```text
verify original 13-0 lifecycle

→ verify correction lifecycle

→ verify Fact Model hash

→ verify corrected Scope Baseline hash

→ verify Phase 12 baseline

→ verify Phase 11 authority

→ load release gap registry

→ load Phase 13-1 handoff

→ load exact P13X1-A01..A08

→ load seven-demo registry

→ load fixture registry

→ admit exactly one 13-1 task

→ build complete integration seam registry

→ verify resource/profile seams

→ verify Intent/Clarification seams

→ verify Eligibility seams

→ verify Planner reachability

→ verify PlanValidator support

→ verify Registry/Adapter resolution

→ verify queue/runtime seams

→ verify PostgreSQL persistence

→ verify Redis queue path

→ verify MinIO Artifact persistence

→ verify Artifact contracts

→ verify Workspace projection

→ verify interpretation applicability

→ verify Finding/Evidence/Provenance seams

→ verify Report/Recipe integration

→ verify historical recovery

→ verify stale identity behavior

→ verify partial execution

→ verify unsupported paths

→ verify provider failure path

→ verify cross-project isolation

→ verify security boundary

→ run seven-demo PRE-FLIGHT only

→ classify each demo readiness

→ verify 11 retained fixtures

→ verify no-injection policy

→ re-run release-gap classification

→ confirm gap count remains zero

→ build 13-2 entry handoff

→ run focused governance tests

→ run full regression

→ run service-backed integration

→ run browser smoke

→ run Linux/Windows retained integrity

→ run Phase 11 integrity

→ run Phase 12 baseline integrity

→ run security/secret/evidence checks

→ create audit/verification implementation commit

→ push

→ WAIT FOR IMPLEMENTATION EXACT-SHA CI

→ if PASS:
   append Phase 13-1 completion record

→ completion commit/push directly

→ archive only Phase 13-1 task

→ archive commit/push directly

→ verify queue empty

→ stop
```

---

# 155. If Any Gap Is Found

立即停止 normal PASS sequence。

必须输出：

```text
PHASE_13_1 =
BLOCKED /
ZERO_GAP_ASSUMPTION_INVALIDATED
```

并：

```text
RELEASE_BLOCKERS =
<actual>

RELEASE_CRITICAL_INTEGRATION_GAPS =
<actual>
```

---

# 156. Gap Discovery Record

每个新 gap必须：

```text
gapId

seam

affectedDemo

severity

repositoryEvidence

productConsequence

scientificConsequence

securityConsequence

minimalFixBoundary

why13_0MissedIt

recommendedReviewerAction
```

---

# 157. Do Not Fix Discovered Gap

禁止：

```text
discover
→ patch
→ erase evidence
→ continue zero-gap PASS
```

---

# 158. Gap Reviewer Return

发现 gap后：

不得 completion/archive为 PASS。

返回 reviewer请求：

```text
revised Phase 13-1 integration-fix prompt
```

---

# 159. Focused Governance Tests

至少：

```text
corrected release hash authority

clarification 1/3/typed-failure

Registry=62

required adapters resolve

all seven demo preflights classified

11 fixture integrity

no injection

zero release blockers

zero critical integration gaps

no demo execution

Phase 13 acceptance integrity
```

---

# 160. Backend Regression

运行：

```text
uv run python -m pytest -q
```

要求：

```text
>= corrected Phase 13-0 final floor
```

当前 reviewer-known：

```text
1327 passed
```

actual repository floor优先。

---

# 161. Frontend Regression

运行：

```text
npm --prefix apps/web test
```

要求：

```text
>= corrected Phase 13-0 final floor
```

当前 known：

```text
455 passed
```

---

# 162. Typecheck

```text
npm --prefix apps/web run typecheck
= PASS
```

---

# 163. Build

```text
npm --prefix apps/web run build
= PASS
```

---

# 164. Lock

```text
uv lock --check
= PASS
```

---

# 165. Diff

```text
git diff --check
= PASS
```

---

# 166. Service-Backed Integration

Exact-SHA CI必须继续真实使用：

```text
PostgreSQL

Redis

MinIO
```

---

# 167. Service Expectations

至少验证：

```text
required service tests skipped = 0

failed = 0
```

---

# 168. Browser Matrix

13-1不跑完整七 demo。

但 retained product/browser smoke必须：

```text
Chromium PASS

Firefox PASS

WebKit PASS

390x844 PASS
```

如果 current CI contract如此。

---

# 169. Linux / Windows

必须继续验证：

```text
scientific sealed invariant replay

release semantic hash normalization
```

按 current CI。

---

# 170. Scope Baseline Cross-Platform Hash

必须：

```text
LINUX_SCOPE_BASELINE_HASH
==
WINDOWS_SCOPE_BASELINE_HASH
==
93dea4a2b0bf31215ab2af1952b16ac47b20b7ed9b111bb2fb60ef70dd431627
```

---

# 171. npm Audit

若 configured mirror仍：

```text
NOT_IMPLEMENTED
```

记录：

```text
npm audit = UNAVAILABLE
```

不得写：

```text
clean
```

---

# 172. Evidence Manifest

13-1 evidence manifest必须：

```text
missing = 0

hash mismatch = 0

unclassified = 0
```

---

# 173. Security

必须：

```text
NO_PHASE13_1_ARBITRARY_CODE_EXECUTION = PASS

NO_PHASE13_1_ARTIFACT_EXECUTION = PASS

NO_PHASE13_1_RECIPE_EXECUTION = PASS

NO_PHASE13_1_RECOMMENDATION_EXECUTION = PASS

NO_PHASE13_1_FRONTEND_SCIENTIFIC_RECOMPUTATION = PASS

NO_PHASE13_1_REAL_LLM_CALL = PASS

NO_PHASE13_1_EXTERNAL_DOWNLOAD = PASS

NO_SECRET_PATTERN_HITS = PASS
```

---

# 174. Implementation/Audit Commit Allowed

可包含：

```text
Phase 13-1 docs

evidence

audit scripts

governance tests

integration seam matrices

demo preflight manifests

13-2 handoff

persistent state

ROADMAP

TASKS admission
```

---

# 175. Forbidden Commit Content

不得包含：

```text
production backend logic

production frontend behavior

Planner behavior

Runtime behavior

Adapter behavior

Registry capability changes

scientific code

Artifact schema

Workspace schema

Report/Recipe schema

database migration

new dependency

real demo outputs

Phase 13-2 user E2E result
```

---

# 176. Implementation Exact-SHA CI

audit/verification commit push后：

必须：

```text
WAIT FOR IMPLEMENTATION EXACT-SHA CI
```

---

# 177. CI Must Pass

required jobs：

```text
success
```

否则 fix-forward audit/evidence/test defect。

---

# 178. Failed Candidate Rule

若 CI失败：

保留：

```text
candidate SHA

CI run

failed job

root cause

fix-forward SHA
```

禁止 rewrite history。

---

# 179. Completion Record

只有 exact-SHA CI PASS：

才 append：

```text
# Phase 13-1 Zero-Gap Verification Closure Result
```

到：

```text
results.md
```

---

# 180. Completion Push

然后：

```text
commit
push
```

直接完成。

不等待 completion CI。

---

# 181. Queue Archive

completion push后：

删除且只删除：

```text
Phase 13-1 TASK block
```

---

# 182. Do Not Create Phase 13-2 Task

必须：

```text
PHASE13_2_EXECUTABLE_TASK_CREATED = NO
```

---

# 183. Archive Push

```text
commit
push
```

不等待 archive CI。

---

# 184. Lifecycle Terminology

最终：

```text
IMPLEMENTATION_VERIFIED_BY_EXACT_SHA_CI

COMPLETION_RECORDED

QUEUE_ARCHIVED
```

---

# 185. Mandatory Result Markers

必须：

```text
PHASE13_1_MODE =
ZERO_GAP_VERIFICATION_CLOSURE

PHASE13_1_PRODUCTION_CODE_CHANGES = 0

PHASE13_1_BACKEND_BEHAVIOR_CHANGES = 0

PHASE13_1_FRONTEND_BEHAVIOR_CHANGES = 0

PHASE13_1_SCIENTIFIC_BEHAVIOR_CHANGES = 0

PHASE13_1_NEW_SCIENTIFIC_TOOLS = 0

PHASE13_1_NEW_SCIENTIFIC_ALGORITHMS = 0

PHASE13_1_NEW_ARTIFACT_FAMILIES = 0

PHASE13_1_NEW_DATABASE_MIGRATIONS = 0

PHASE13_1_NEW_PUBLIC_API_FAMILIES = 0

PHASE13_1_NEW_DEPENDENCIES = 0

PHASE13_1_LOCKFILE_CHANGES = 0

PHASE13_1_NEW_LLM_CALL_SITES = 0

PHASE13_1_REAL_LLM_CALLS = 0

PHASE13_1_FRONTEND_SCIENTIFIC_RECOMPUTATION = 0
```

---

# 186. Authority Markers

必须：

```text
INITIAL_RELEASE_FACT_MODEL_HASH =
e0248d502e4a442bb9596a8d2f6fe6d7fdefe61c41121ae08736734ce4004a06

INITIAL_RELEASE_SCOPE_BASELINE_HASH =
93dea4a2b0bf31215ab2af1952b16ac47b20b7ed9b111bb2fb60ef70dd431627

PHASE12_PRODUCT_EXPERIENCE_BASELINE_HASH =
29936236efe74a82ad97507385839aa4f5692d26b496292af3172940647973d4
```

---

# 187. Clarification Markers

必须：

```text
PHASE13_CLARIFICATION_MAX_ROUNDS = 1

PHASE13_CLARIFICATION_MAX_QUESTIONS = 3

PHASE13_SECOND_CLARIFICATION_ROUND =
TYPED_FAILURE

CURRENT_CANONICAL_TWO_ROUND_ASSERTIONS = 0
```

---

# 188. Gap Markers

必须：

```text
RELEASE_BLOCKERS = 0

RELEASE_CRITICAL_INTEGRATION_GAPS = 0

UNCLASSIFIED_RELEASE_GAPS = 0

INTEGRATION_SEAMS_GAP_FOUND = 0
```

---

# 189. Demo Markers

必须：

```text
PHASE13_DEMO_FAMILIES = 7

DEMO_PREFLIGHT_COMPLETE = 7/7

DEMO_PREFLIGHT_BLOCKED = 0

PHASE13_2_DEMOS_EXECUTED = 0

PHASE13_2_DEMO_PASS_CLAIMS = 0
```

---

# 190. Fixture Markers

必须：

```text
RETAINED_FIXTURE_RECORDS =
<actual current, expected 11>

MISSING_FIXTURES = 0

CHECKSUM_MISMATCH = 0

EXTERNAL_DOWNLOADS = 0
```

---

# 191. No-Injection Markers

必须：

```text
HANDCRAFTED_PLAN_INJECTION = 0

HANDCRAFTED_JOB_INJECTION = 0

HANDCRAFTED_TOOLCALL_INJECTION = 0

HANDCRAFTED_ARTIFACT_INJECTION = 0

HANDCRAFTED_WORKSPACE_INJECTION = 0

HANDCRAFTED_FINDING_INJECTION = 0

HANDCRAFTED_EVIDENCE_INJECTION = 0

HANDCRAFTED_REPORT_INJECTION = 0

HANDCRAFTED_RECIPE_INJECTION = 0
```

---

# 192. Runtime Markers

必须：

```text
REAL_PERSISTENCE_REQUIRED = YES

REAL_RUNTIME_REQUIRED = YES

REGISTERED_ADAPTER_EXECUTION_REQUIRED = YES

WORKSPACE_FROM_REAL_JOB_REQUIRED = YES

REPORT_FROM_REAL_PERSISTED_FACTS_REQUIRED = YES
```

这些是 13-2 contract，

13-1只验证 contract/wiring准备度。

---

# 193. Scientific Baseline

必须：

```text
REGISTRY_BEFORE_13_1 = 62
REGISTRY_AFTER_13_1 = 62

DATAPROFILE_BEFORE_13_1 = 2.4
DATAPROFILE_AFTER_13_1 = 2.4

MIGRATION_BEFORE_13_1 =
0007_phase10m1_workspace_domain

MIGRATION_AFTER_13_1 =
0007_phase10m1_workspace_domain

V4 = 0
```

---

# 194. Scientific Honesty Markers

必须：

```text
SUPPORTED_EQUALS_VALIDATED = NO

E2E_PASS_EQUALS_REFERENCE_VALIDATED = NO

REPORT_INCLUDED_EQUALS_VALIDATED = NO

RECIPE_EXISTS_EQUALS_REPRODUCIBILITY_VALIDATED = NO

BROWSER_PASS_EQUALS_SCIENTIFIC_PASS = NO

SERVICE_PASS_EQUALS_SCIENTIFIC_PASS = NO

FRONTEND_SCIENTIFIC_AUTHORITY = NONE

SCREENSHOT_NUMERIC_SCIENTIFIC_AUTHORITY = NONE
```

---

# 195. Acceptance Marker

必须：

```text
P13X1_ACCEPTANCE = 8/8
```

使用 sealed canonical exact descriptions。

---

# 196. Required results.md Structure

至少：

# Phase 13-1 Zero-Gap Verification Closure Result

1. Conclusion
2. Phase 13-0 Baseline
3. Clarification Correction Baseline
4. Entry Gate
5. Repository State
6. Fact Model Hash Verification
7. Corrected Scope Baseline Verification
8. Phase 12 Baseline Verification
9. Phase 11 Scientific Authority
10. Phase 13-1 Handoff Integrity
11. P13X1 Acceptance Authority
12. Release Gap Registry — Before
13. Integration Seam Inventory
14. Resource / Dataset Seam
15. DataProfile Seam
16. AnalysisIntent Seam
17. Clarification Seam
18. Eligibility Seam
19. Planner Reachability
20. AnalysisPlan Seam
21. PlanValidator Seam
22. Registry Seam
23. Adapter Resolution
24. Queue Seam
25. Runtime Seam
26. PostgreSQL Persistence
27. Redis Queue
28. MinIO Artifact Storage
29. Artifact Contract Integrity
30. Workspace Projection
31. Workspace Identity
32. Viewer Mapping
33. Interpretation Applicability
34. Finding / Evidence
35. Provenance
36. Report Source Eligibility
37. Report Finalization
38. Recipe
39. Historical Recovery
40. Stale Identity
41. Partial Execution
42. Unsupported Input
43. Unsupported Capability
44. Provider Failure
45. Cross-Project Isolation
46. Security Integration
47. Demo Registry
48. Demo 1 Preflight
49. Demo 2 Preflight
50. Demo 3 Preflight
51. Demo 4 Preflight
52. Demo 5 Preflight
53. Demo 6 Preflight
54. Demo 7 Preflight
55. Demo Preflight Aggregate
56. Fixture Integrity
57. Fixture-to-Demo Coverage
58. User Persona Contract
59. Negative Path Contract
60. No-Injection Contract
61. Persistence / Runtime Contract
62. Provider Contract
63. Release Claim Non-Change
64. Release Gap Registry — After
65. Zero-Gap Independent Conclusion
66. Phase 13-2 Entry Handoff
67. Backend Regression
68. Frontend Regression
69. Typecheck
70. Build
71. Lock / Diff
72. Service-Backed Integration
73. Browser Smoke
74. Linux / Windows Integrity
75. Phase 11 Integrity
76. Phase 12 Integrity
77. Evidence Manifest
78. Security / Secret Scan
79. Files Changed
80. Implementation/Audit Commit
81. Exact-SHA CI
82. Failed Candidates
83. Completion Record
84. Queue Archive
85. Queue State
86. Phase 13-2 Reviewer Gate
87. Final Repository State

---

# 197. PASS Gate

只有全部满足：

```text
Phase 13-0 PASS

clarification correction PASS

both 13-0 queues archived


HEAD == origin/master at entry

worktree clean

TASK_BLOCK_COUNT = 0


Fact Model hash verified

corrected Scope Baseline hash verified

baseline determinism PASS

Phase 12 baseline verified

Phase 11 authority verified


clarification rounds = 1

questions = 3

second round = typed failure

two-round current assertions = 0


release blockers before = 0

critical integration gaps before = 0


all required integration seams verified

GAP_FOUND_COUNT = 0


Registry = 62

all required seven-demo Tools
resolve to real registered Adapters


real queue/runtime wiring verified

PostgreSQL wiring verified

Redis wiring verified

MinIO wiring verified


Artifact contracts ready

Workspace projection ready

interpretation path ready where applicable

Report/Recipe integration ready


7 demo contracts present

7/7 demo preflight complete

0 demo preflight blocked

all exact fixtures present

checksum mismatches = 0

external downloads = 0


no-injection policy intact

negative-path contract intact

real persistence/runtime contract intact


release blockers after = 0

release-critical integration gaps after = 0

unclassified gaps = 0


P13X1 = 8/8


production code changes = 0

scientific behavior changes = 0

new Tool = 0

new algorithm = 0

new Artifact family = 0

new migration = 0

new API family = 0

new dependency = 0

new LLM call site = 0

real LLM calls = 0

frontend scientific recomputation = 0


backend >= corrected 13-0 floor

frontend >= corrected 13-0 floor

typecheck PASS

build PASS

lock PASS

diff PASS

PostgreSQL/Redis/MinIO PASS

browser smoke PASS

required Linux/Windows integrity PASS

Phase 11 integrity PASS

Phase 12 baseline integrity PASS

security PASS

secret scan PASS

evidence manifest PASS


PHASE13_2_DEMOS_EXECUTED = 0

PHASE13_2_DEMO_PASS_CLAIMS = 0


implementation exact-SHA CI PASS

completion record committed/pushed

queue archive committed/pushed


TASK_BLOCK_COUNT = 0

Phase 13-2 executable task absent

Phase14 absent

HEAD == origin/master

worktree clean
```

才能：

```text
Phase 13-1 = PASS
```

---

# 198. BLOCKED — Gap Found

任意：

```text
GAP_FOUND_COUNT > 0
```

必须：

```text
BLOCKED /
ZERO_GAP_ASSUMPTION_INVALIDATED
```

---

# 199. BLOCKED — Demo Preflight Blocked

任一：

```text
DEMO_PREFLIGHT = BLOCKED
```

不能 PASS。

---

# 200. BLOCKED — Required Adapter Missing

若：

```text
Registry Tool exists
but Adapter missing
```

这是 release integration gap。

---

# 201. BLOCKED — User Entry Missing

若 capability只能通过：

```text
internal API
Tool ID
direct Adapter
handcrafted Plan
```

达到：

这是 release integration gap。

---

# 202. BLOCKED — Persistence Mock Only

若 release path只能在：

```text
mock DB
in-memory queue
fake Artifact storage
```

完成：

不能 PASS。

---

# 203. BLOCKED — Workspace Not From Job

若 required demo只能靠：

```text
prebuilt Workspace
```

展示：

不能 PASS。

---

# 204. BLOCKED — Report Source Gap

若 real persisted output没有合法：

```text
Report source path
```

而 demo contract要求 Report：

不能 PASS。

---

# 205. BLOCKED — Hash Drift

若：

```text
Fact Model hash
or
Scope Baseline hash
```

与 sealed current authority不一致：

不能 PASS。

---

# 206. BLOCKED — Clarification Drift

如果：

```text
MAX_ROUNDS != 1
```

不能 PASS。

---

# 207. BLOCKED — Scientific Authority Drift

若：

```text
Registry != 62

DataProfile != 2.4

migration != 0007
```

无 approved revision：

不能 PASS。

---

# 208. BLOCKED — New Science Required

如果 13-2 readiness需要新增：

```text
Tool
algorithm
Artifact family
scientific semantics
```

则不是 integration gap closure可以解决。

必须返回 reviewer。

---

# 209. Non-Blockers

继续允许：

```text
V4 = 0

numeric cross-platform reference N/A

macOS not current scientific target

formal WCAG certification absent

bounded 3D accessibility limitation

mapping-only/input limitations

planned Phase 13-2 execution evidence absent
```

只要 already disclosed。

---

# 210. Successful Final State

成功后：

```text
Phase 13-1:
PASS /
ZERO_GAP_VERIFIED /
RELEASE_CRITICAL_INTEGRATION_SEAMS_CLOSED /
QUEUE_ARCHIVED

Phase 13:
IN_PROGRESS /
READY_FOR_REAL_USER_E2E_DEMONSTRATIONS

RELEASE_BLOCKERS = 0

RELEASE_CRITICAL_INTEGRATION_GAPS = 0

INTEGRATION_SEAMS_GAP_FOUND = 0

DEMO_PREFLIGHT_COMPLETE = 7/7

DEMO_PREFLIGHT_BLOCKED = 0

Phase 13-2:
REVIEWER_GATE /
AWAITING REVIEWER PROMPT

PHASE13_2_EXECUTABLE_TASK_CREATED = NO

Initial Release:
NOT_COMPLETE

TASK_BLOCK_COUNT = 0

PHASE14_CREATED = NO
```

---

# 211. Meaning of Phase 13-1 Completion

可以说：

```text
The Phase 13-0 zero-gap conclusion has been
independently verified across the release-critical
integration seams required by all seven canonical
real-user demonstrations.

All seven demo contracts have passed preflight
readiness checks against the current Registry,
Adapters, Runtime, persistence, Workspace and
Report/Recipe authorities.

The seven real-user demonstrations themselves
have not yet been executed.
```

---

# 212. What Completion Does NOT Mean

不能说：

```text
Seven demos passed.

Real users completed the product flows.

The product is release-ready.

Initial Release is complete.

Live DeepSeek acceptance passed.

Every scientific output is reference validated.

Phase 13-2 is complete.

Phase 14 is authorized.
```

---

# 213. Phase 13-2 Gate

最终：

```text
Phase 13-2:
REVIEWER_GATE /
AWAITING REVIEWER PROMPT

PHASE13_2_ENTRY_HANDOFF =
READY_FOR_REVIEWER

PHASE13_2_EXECUTABLE_TASK_CREATED = NO
```

---

# 214. Stop Rule

13-1 completion并归档后立即停止。

严禁：

```text
execute Demo 1

execute Demo 2

execute Demo 3

execute Demo 4

execute Demo 5

execute Demo 6

execute Demo 7

run bounded live DeepSeek acceptance

create Phase 13-2 task

start Phase 13-3

declare release-ready

declare Initial Release complete

create Phase 14
```

---

# 215. Final Return to Reviewer

必须返回：

```text
Phase 13-1 conclusion

implementation/audit SHA

implementation exact-SHA CI

completion SHA

archive SHA

failed candidates if any

Fact Model hash

corrected Scope Baseline hash

Phase 12 baseline hash

clarification authority

integration seam count

verified seam count

gap-found count

release blockers

release-critical integration gaps

7 demo preflight results

fixture integrity

Registry/Adapter resolution result

queue/runtime result

PostgreSQL/Redis/MinIO result

Artifact/Workspace readiness

interpretation/trust-path readiness

Report/Recipe readiness

negative-path readiness

no-injection status

P13X1 8/8

backend/frontend regression

browser/service/platform results

Phase 13-2 handoff status

TASK_BLOCK_COUNT

HEAD/origin/worktree
```

然后等待 reviewer。

---

# 216. Final Required Status Block

成功结果末尾必须：

```text
PHASE_13_1 = PASS

PHASE_13_1_MODE =
ZERO_GAP_VERIFICATION_CLOSURE

ZERO_GAP_INDEPENDENTLY_VERIFIED = YES

RELEASE_BLOCKERS = 0

RELEASE_CRITICAL_INTEGRATION_GAPS = 0

UNCLASSIFIED_RELEASE_GAPS = 0

INTEGRATION_SEAMS_GAP_FOUND = 0

PHASE13_DEMO_FAMILIES = 7

DEMO_PREFLIGHT_COMPLETE = 7/7

DEMO_PREFLIGHT_BLOCKED = 0

PHASE13_2_DEMOS_EXECUTED = 0

PHASE13_2_DEMO_PASS_CLAIMS = 0

INITIAL_RELEASE_FACT_MODEL_HASH =
e0248d502e4a442bb9596a8d2f6fe6d7fdefe61c41121ae08736734ce4004a06

INITIAL_RELEASE_SCOPE_BASELINE_HASH =
93dea4a2b0bf31215ab2af1952b16ac47b20b7ed9b111bb2fb60ef70dd431627

PHASE12_PRODUCT_EXPERIENCE_BASELINE_HASH =
29936236efe74a82ad97507385839aa4f5692d26b496292af3172940647973d4

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

P13X1_ACCEPTANCE = 8/8

PRODUCTION_CODE_CHANGES = 0

SCIENTIFIC_BEHAVIOR_CHANGES = 0

REAL_LLM_CALLS = 0

FRONTEND_SCIENTIFIC_RECOMPUTATION = 0

PHASE_13 =
IN_PROGRESS /
READY_FOR_REAL_USER_E2E_DEMONSTRATIONS

PHASE_13_2 =
REVIEWER_GATE /
AWAITING REVIEWER PROMPT

PHASE13_2_EXECUTABLE_TASK_CREATED = NO

INITIAL_RELEASE_COMPLETE = NO

TASK_BLOCK_COUNT = 0

PHASE14_CREATED = NO

HEAD == origin/master

WORKTREE_CLEAN = YES
```

完成时间：2026-08-11 13:18:00 +08:00

修改文件：`.github/workflows/ci.yml`、`scripts/generate_phase13_1_zero_gap.py`、`tests/test_phase13_1_zero_gap_verification.py`、历史队列治理测试、`docs/phase13/`、`docs/ROADMAP.md`、`persistent/`、`TASKS.md`、`results.md`。

修改摘要：完成 Phase 13-1 zero-gap verification closure；独立核对 30 个 integration seams、七个 canonical demo preflight、11 个 retained fixtures、62 个 Registry Tool（51 runtime Adapter + 11 mapping-only/unavailable），保持 release blockers、release-critical integration gaps 和 unclassified gaps 均为 0。未修改 production/science，未执行 Phase 13-2 demo。

测试结果：本地 backend `1335 passed, 50 skipped`；frontend `455 passed`；typecheck/build/`uv lock --check`/`git diff --check` PASS；focused governance `69 passed` 与 Phase 13-1 `14 passed`；implementation exact-SHA `d1a60955a77aec000f1e6fd630f0770db545421d` CI `31460352586` PASS。失败候选 `800d15c0401a30507fe679dfa6dba3d539e39559` / CI `31459364889` 已保留，根因为 CRLF/LF manifest byte-size drift，已 fix-forward。


---END---


---TASK---
 状态：待处理

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




---END---
