
---TASK---
 状态：已完成

# Phase 13-0 Reviewer Correction Prompt

# Clarification Round-Limit Fact Alignment Correction

你现在执行一个**严格限定的 Phase 13-0 reviewer correction**：

# Phase 13-0 Fact Alignment Correction

## AnalysisIntent Clarification Round-Limit Alignment

这不是新的 roadmap phase。

不是 Phase 13-1。

不是重新执行 Phase 13-0。

不是生产功能修改。

这是对已经归档的 Phase 13-0 release contract 中一个事实错误进行 **append-only fix-forward correction**。

---

# 0. Correction Mission

当前已确认存在唯一事实冲突：

```text
Production / canonical AnalysisIntent 1.0 authority:

MAX_CLARIFICATION_ROUNDS = 1
MAX_CLARIFICATION_QUESTIONS = 3

second clarification round
= typed failure
```

但 Phase 13-0 sealed E2E contract 当前写成：

```text
clarification bounded to two rounds
```

这是错误的 release-contract projection。

本 correction 的唯一任务：

```text
Phase 13 clarification contract

2 rounds
→
1 round

while preserving:

AnalysisIntent 1.0
maximum questions = 3
second-round typed failure
```

并重新验证：

```text
InitialReleaseFactModel

InitialReleaseScopeBaseline

seven-demo contracts

negative-path registry

acceptance registry

13-1 handoff

13-2 E2E contract
```

是否因此受到 semantic hash 影响。

---

# 1. Correction Classification

必须记录：

```text
CORRECTION_TYPE =
FACT_ALIGNMENT_FIX_FORWARD

PRODUCTION_DEFECT = NO

SCIENTIFIC_DEFECT = NO

RELEASE_CRITICAL_INTEGRATION_GAP = NO

CONTRACT_DOCUMENTATION_DRIFT = YES

ROADMAP_PHASE_CHANGE = NO
```

---

# 2. Reviewer Authorization

本 Prompt 只授权：

```text
PHASE_13_0_FACT_CORRECTION = YES
```

最大允许工作范围：

```text
MAX_CORRECTION_SCOPE = 1
```

不得进入：

```text
Phase 13-1
Phase 13-2
Phase 13-3
Phase 13-4
Phase 13-5
Phase 13-6
Phase 14
```

---

# 3. Mandatory Existing Authority

首先从真实 repository 重新确认：

```text
AnalysisIntent schemaVersion = 1.0
```

并从 production contracts/tests/history，而不是本 Prompt，确定：

```text
MAX_CLARIFICATION_ROUNDS
MAX_CLARIFICATION_QUESTIONS
SECOND_ROUND_BEHAVIOR
```

必须解析为：

```text
MAX_CLARIFICATION_ROUNDS = 1

MAX_CLARIFICATION_QUESTIONS = 3

SECOND_CLARIFICATION_ROUND =
TYPED_FAILURE
```

如果 production authority实际不是这个值：

立即：

```text
BLOCKED /
ANALYSIS_INTENT_AUTHORITY_DIFFERENT_FROM_REVIEWER_EXPECTATION
```

停止。

不得修改 production 来匹配 Prompt。

---

# 4. Current Phase 13-0 Baseline

必须动态确认 Phase 13-0 已完成并归档。

当前 reviewer-known baseline：

```text
Implementation:
6217d042d0190c43144e402e4479aa9810b8e9d0

Implementation exact-SHA CI:
31451202923 PASS

Completion:
0af74ff078e1dab6324852a8329cea42bf092acb

Queue archive:
7a554cd91b0638898bfe097972f29a097540b514
```

Git history为最终 authority。

---

# 5. Existing Hash Baseline

必须确认 correction 前 canonical：

```text
OLD_INITIAL_RELEASE_FACT_MODEL_HASH =
e0248d502e4a442bb9596a8d2f6fe6d7fdefe61c41121ae08736734ce4004a06

OLD_INITIAL_RELEASE_SCOPE_BASELINE_HASH =
8e8b4f659888635192d259eee90f3befdd655cacb292a78c5e13c20a5fdabdde
```

如果 repository current canonical与上述不同：

使用 repository actual，并披露差异。

---

# 6. Existing Phase 13 Facts That Must Remain

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

以及：

```text
RELEASE_BLOCKERS = 0

RELEASE_CRITICAL_INTEGRATION_GAPS = 0

PHASE13_DEMO_FAMILIES = 7

DEMO_CONTRACTS_SEALED = 7

DEMOS_EXECUTED = 0

P13X0_ACCEPTANCE = 8/8
```

除非 correction audit发现这些与 repository authority有独立真实冲突。

不得因为本 correction主动改变。

---

# 7. Repository Entry Gate

开始前必须：

```text
branch = master

HEAD == origin/master

worktree = clean

TASK_BLOCK_COUNT = 0

Phase 13-1 executable task absent

Phase 13-2 executable task absent

Phase 14 absent
```

否则：

```text
BLOCKED /
CORRECTION_ENTRY_REPOSITORY_NOT_CLEAN
```

---

# 8. Do Not Rewrite History

`results.md` 是 append-only。

禁止修改原 Phase 13-0 permanent result中的：

```text
"bounded to two rounds"
```

历史文字。

必须保留原始错误记录作为历史事实。

通过新的：

```text
Phase 13-0 Fact Alignment Correction Addendum
```

进行 superseding correction。

---

# 9. Correction Task Admission

Entry Gate PASS 后，只允许创建：

```text
one temporary correction TASK block
```

建议名称：

```text
Phase 13-0 Reviewer Correction —
Clarification Round-Limit Fact Alignment
```

它不是新的 roadmap phase。

要求：

```text
TASK_BLOCK_COUNT = 1

ACTIVE_TASK =
Phase 13-0 Reviewer Correction
```

同时：

```text
PHASE13_1_EXECUTABLE_TASK_CREATED = NO

PHASE13_2_EXECUTABLE_TASK_CREATED = NO

PHASE14_CREATED = NO
```

---

# 10. Exact Incorrect Statement Discovery

不要只修一个已知文件。

必须搜索整个 repository：

```text
"two rounds"

"2 rounds"

"max clarification rounds"

"clarification rounds"

"bounded clarification"

"second clarification"

"clarification expectation"
```

以及语义等价表述。

---

# 11. Search Scope

至少扫描：

```text
docs/phase13/

docs/phase13/evidence/

persistent/

tests/

scripts/

CI/audit generators

schemas/manifests

results.md
```

但：

```text
results.md historical section
```

只识别，不改写。

---

# 12. Classification of Every Hit

建立：

```text
ClarificationRoundLimitOccurrenceMatrix
```

每个 occurrence：

```text
path

line/field

currentValue

authorityType

historicalOrCurrent

semanticHashInput

requiresCorrection

reason
```

---

# 13. Historical Occurrence Rule

历史 Phase 13-0 result：

```text
historicalOrCurrent = HISTORICAL_APPEND_ONLY
requiresCorrection = NO
```

但必须在 addendum中引用它为：

```text
SUPERSEDED_HISTORICAL_STATEMENT
```

---

# 14. Current Canonical Contract Rule

所有 current canonical Phase 13 contract：

必须：

```text
clarification rounds = 1
```

不得保留：

```text
2
```

---

# 15. Correct Semantic Definition

最终 canonical Phase 13 wording必须等价：

```text
Applicable clarification is user-visible
and bounded to one round.

The round may contain at most three
approved clarification questions.

A request requiring a second clarification
round does not continue interactively;
it follows the existing AnalysisIntent 1.0
typed-failure / unsupported boundary.

Resolved Intent may not be injected to
bypass the clarification path.
```

---

# 16. Do Not Expand Clarification

禁止修改 production：

```text
AnalysisIntent validator

clarification API

frontend clarification behavior

persistence

Intent revision semantics
```

来支持第二轮。

---

# 17. Production Behavior Changes

必须最终：

```text
CORRECTION_PRODUCTION_CODE_CHANGES = 0

CORRECTION_BACKEND_BEHAVIOR_CHANGES = 0

CORRECTION_FRONTEND_BEHAVIOR_CHANGES = 0
```

---

# 18. Scientific Changes

必须：

```text
CORRECTION_SCIENTIFIC_BEHAVIOR_CHANGES = 0

NEW_SCIENTIFIC_TOOLS = 0

NEW_SCIENTIFIC_ALGORITHMS = 0

NEW_ARTIFACT_FAMILIES = 0
```

---

# 19. Contract Versions

不得改变：

```text
AnalysisIntent = 1.0

EligibilityResolution = 1.0

AnalysisPlan = 0.1 / 0.2
```

---

# 20. Clarification Governance Test

必须新增或强化 deterministic governance test：

```text
PHASE13_CLARIFICATION_MAX_ROUNDS
==
ANALYSIS_INTENT_MAX_CLARIFICATION_ROUNDS
==
1
```

---

# 21. Question Count Governance Test

同时：

```text
PHASE13_CLARIFICATION_MAX_QUESTIONS
==
ANALYSIS_INTENT_MAX_CLARIFICATION_QUESTIONS
==
3
```

---

# 22. Second Round Governance Test

必须断言：

```text
PHASE13_SECOND_CLARIFICATION_ROUND_EXPECTATION
==
ANALYSIS_INTENT_SECOND_ROUND_BEHAVIOR
==
TYPED_FAILURE
```

不得：

```text
continue to round 2
```

---

# 23. No Resolved-Intent Injection

继续：

```text
RESOLVED_INTENT_TEST_INJECTION = 0
```

真实用户 E2E仍必须：

```text
user prompt
→ AnalysisIntent
→ clarification if applicable
```

---

# 24. Phase 13 Demo Contract Audit

重新检查全部七个 demo：

```text
Demo 1
Dataset Intelligence + Composition Space

Demo 2
Materials ML

Demo 3
Structure + coordination +
local environment + polyhedra + XRD

Demo 4
Trajectory + RDF + MSD + diffusion

Demo 5
Phonon + Brillouin Zone

Demo 6
Volumetric

Demo 7
Electronic Band + DOS
```

---

# 25. Demo Contract Correction

任何 demo 若：

```text
expects two clarification rounds
```

必须修正。

---

# 26. Canonical Scientist Persona

保持不变。

---

# 27. Imperfect / Exploratory Persona

仍必须覆盖 ambiguity。

但流程必须：

```text
ambiguous user request

→ at most one clarification round

→ READY
or
typed non-ready outcome
```

不得进入第二轮。

---

# 28. Negative Path Registry

必须明确包含：

```text
SECOND_CLARIFICATION_ROUND_REQUIRED
```

作为 negative/boundary case。

预期：

```text
typed failure/non-ready
```

且：

```text
plan creation = 0
job creation = 0
enqueue = 0
ToolCall = 0
Artifact = 0
```

---

# 29. Clarification Success Case

至少保留一个：

```text
ambiguous request
→ one valid clarification round
→ immutable child Intent
→ READY
```

证明 correction没有错误地禁用 clarification。

---

# 30. Clarification Failure Case

至少：

```text
request still ambiguous after one round
```

必须遵循 production typed failure。

不能：

```text
ask second round
```

---

# 31. Acceptance Registry Audit

检查全部 Phase 13 acceptance IDs 中涉及：

```text
clarification

ambiguity

real-user simulation

negative paths
```

的条款。

---

# 32. Acceptance ID Stability

不得：

```text
rename acceptance IDs

delete IDs

lower acceptance requirement

change total count
```

除非 current authority本身错误且 reviewer另行批准。

---

# 33. P13X0

保持：

```text
P13X0-A01..A08 = 8/8
```

但重新验证 contract correction后仍成立。

---

# 34. P13X2 Contract

必须明确：

13-2 real-user E2E：

```text
MAX_CLARIFICATION_ROUNDS = 1
```

---

# 35. P13X5 Contract

最终 release acceptance同样：

```text
MAX_CLARIFICATION_ROUNDS = 1
```

防止 13-5重新漂移。

---

# 36. Semantic Dependency Audit — Critical Gate

必须追踪：

```text
clarification round-limit fact
```

是否进入：

```text
InitialReleaseFactModel

InitialReleaseScopeBaseline
```

的 semantic hash dependency graph。

不得猜测。

---

# 37. Hash Dependency Graph

建立：

```text
ClarificationHashDependencyGraph
```

至少：

```text
clarification contract
→ demo registry?
→ negative path registry?
→ acceptance registry?
→ release claim registry?
→ fact model?
→ scope baseline?
```

每条边：

```text
YES / NO
```

并提供具体字段/manifest evidence。

---

# 38. Fact Model Impact Decision

必须得到二选一：

```text
FACT_MODEL_HASH_IMPACT = YES
```

或：

```text
FACT_MODEL_HASH_IMPACT = NO
```

不能：

```text
UNKNOWN
```

---

# 39. Scope Baseline Impact Decision

同理：

```text
SCOPE_BASELINE_HASH_IMPACT = YES
```

或：

```text
SCOPE_BASELINE_HASH_IMPACT = NO
```

---

# 40. If Fact Model Is Affected

如果：

```text
FACT_MODEL_HASH_IMPACT = YES
```

必须重新生成：

```text
InitialReleaseFactModel
```

并得到：

```text
NEW_INITIAL_RELEASE_FACT_MODEL_HASH =
<new sha256>
```

---

# 41. Fact Model Supersession

记录：

```text
OLD_INITIAL_RELEASE_FACT_MODEL_HASH =
e0248d...

SUPERSEDED_BY =
<new hash>

SUPERSESSION_REASON =
CLARIFICATION_ROUND_LIMIT_FACT_ALIGNMENT
```

不得删除旧 hash历史。

---

# 42. If Fact Model Is Not Affected

必须提供：

```text
FACT_MODEL_HASH_IMPACT = NO

reason =
clarification round-limit is not part of
the Fact Model semantic hash dependency domain
```

并通过自动化 proof验证：

重新生成：

```text
hash == old hash
```

---

# 43. If Scope Baseline Is Affected

如果：

```text
SCOPE_BASELINE_HASH_IMPACT = YES
```

必须重新生成：

```text
InitialReleaseScopeBaseline
```

输出：

```text
NEW_INITIAL_RELEASE_SCOPE_BASELINE_HASH =
<new sha256>
```

---

# 44. Scope Baseline Supersession

记录：

```text
OLD_INITIAL_RELEASE_SCOPE_BASELINE_HASH =
8e8b4f...

SUPERSEDED_BY =
<new hash>

SUPERSESSION_REASON =
CLARIFICATION_ROUND_LIMIT_FACT_ALIGNMENT
```

---

# 45. If Scope Baseline Is Not Affected

必须自动证明：

```text
regenerated hash
==
8e8b4f659888635192d259eee90f3befdd655cacb292a78c5e13c20a5fdabdde
```

并记录：

```text
SCOPE_BASELINE_HASH_IMPACT = NO
```

---

# 46. No Manual Hash Editing

禁止：

```text
editing hash strings by hand
```

所有 hash必须从 canonical generator产生。

---

# 47. Determinism

对所有受影响 baseline：

至少连续重新生成两次。

要求：

```text
RUN_1_HASH == RUN_2_HASH
```

---

# 48. Semantic Hash Inputs

runtime以下内容不得导致 semantic hash改变：

```text
timestamp

absolute path

temporary directory

platform newline

commit runtime metadata
```

---

# 49. CRLF/LF

由于 13-0曾经存在 CRLF/LF hash failure，

本 correction必须继续验证：

```text
CROSS_PLATFORM_TEXT_HASH_NORMALIZATION = PASS
```

---

# 50. Linux / Windows Determinism

若 baseline hash受影响：

implementation exact-SHA CI必须在：

```text
Linux
Windows
```

都验证 identical semantic hash。

---

# 51. Release Scope Drift

修正后必须：

```text
RELEASE_SCOPE_DRIFT =
DOCUMENTATION_FACT_CORRECTION_ONLY
```

不得出现：

```text
CAPABILITY_PROMOTION
VALIDATION_PROMOTION
INPUT_SUPPORT_PROMOTION
SCIENTIFIC_PROMOTION
```

---

# 52. Release Blocker Registry

重新生成/验证：

```text
RELEASE_BLOCKERS = 0

RELEASE_CRITICAL_INTEGRATION_GAPS = 0
```

本 clarification correction本身不得被错误计为 integration gap。

---

# 53. Demo Execution State

必须保持：

```text
PHASE13_2_DEMOS_EXECUTED = 0

PHASE13_2_DEMO_PASS_CLAIMS = 0
```

---

# 54. Phase 13-1 Handoff

继续：

```text
Phase 13-1 =
ZERO_GAP_VERIFICATION_CLOSURE
```

前提 correction PASS。

---

# 55. Do Not Queue Phase 13-1

必须：

```text
PHASE13_1_EXECUTABLE_TASK_CREATED = NO
```

---

# 56. Phase 13-2

必须：

```text
PHASE13_2_CONTRACT_READY = YES
```

如果 correction完成。

但：

```text
PHASE13_2_EXECUTION_READY = NO
```

直到 13-1 reviewer closure。

---

# 57. Phase 13-2 No-Injection Policy

继续保持全部：

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

# 58. Runtime Policies

保持：

```text
REAL_PERSISTENCE_REQUIRED = YES

REAL_RUNTIME_REQUIRED = YES

REGISTERED_ADAPTER_EXECUTION_REQUIRED = YES

WORKSPACE_FROM_REAL_JOB_REQUIRED = YES

REPORT_FROM_REAL_PERSISTED_FACTS_REQUIRED = YES
```

---

# 59. Provider Policy

本 correction不得修改：

```text
deterministic provider replay
= release E2E authority
```

以及 bounded future live-provider policy。

---

# 60. DeepSeek

必须：

```text
CORRECTION_REAL_LLM_CALLS = 0
```

---

# 61. Provider Scope

不得因为 clarification contract修复：

改变：

```text
DeepSeek endpoint

models

DEEPSEEK_KEY policy

provider retry policy
```

---

# 62. Phase 11 Authority

必须：

```text
PHASE11_SCIENTIFIC_AUTHORITY_MUTATION = 0
```

---

# 63. Phase 12 Baseline

必须：

```text
PHASE12_PRODUCT_EXPERIENCE_BASELINE_MUTATION = 0
```

Phase 12 hash保持原 sealed value。

---

# 64. Registry

必须：

```text
REGISTRY_BEFORE = 62
REGISTRY_AFTER = 62
```

---

# 65. DataProfile

必须：

```text
DATAPROFILE_BEFORE = 2.4
DATAPROFILE_AFTER = 2.4
```

---

# 66. Migration

必须：

```text
MIGRATION_BEFORE =
0007_phase10m1_workspace_domain

MIGRATION_AFTER =
0007_phase10m1_workspace_domain
```

---

# 67. API

必须：

```text
NEW_PUBLIC_API_FAMILIES = 0
```

---

# 68. DB

必须：

```text
NEW_DATABASE_TABLES = 0

NEW_DATABASE_COLUMNS = 0

NEW_DATABASE_MIGRATIONS = 0
```

---

# 69. Dependencies

必须：

```text
NEW_PYTHON_DEPENDENCIES = 0

NEW_FRONTEND_DEPENDENCIES = 0

LOCKFILE_CHANGES = 0
```

---

# 70. Production Scientific Recomputation

必须：

```text
FRONTEND_SCIENTIFIC_RECOMPUTATION = 0
```

---

# 71. Release Claims

不得改变任何 public capability claim，

除非它包含错误的 “two-round clarification”表述。

只允许收窄为真实：

```text
bounded one-round clarification
```

---

# 72. No Capability Regression Claim

本修复是 release contract纠正，

不是产品能力 regression。

不要写：

```text
clarification capability reduced
```

因为 production从来没有 two-round authority。

正确表述：

```text
release documentation aligned
to existing production authority
```

---

# 73. Evidence Directory

建议建立：

```text
docs/phase13/evidence/
phase13_0_clarification_fact_correction/
```

---

# 74. Required Evidence

至少：

```text
entry_gate.md

analysis_intent_authority.json

clarification_occurrence_matrix.json

clarification_contract_before_after.json

clarification_governance_test.json

second_round_negative_case.json

one_round_success_case.json

demo_contract_reconciliation.json

acceptance_reconciliation.json

hash_dependency_graph.json

fact_model_hash_impact.json

scope_baseline_hash_impact.json

fact_model_regeneration.json

scope_baseline_regeneration.json

baseline_determinism.json

release_scope_drift.json

release_gap_reconciliation.json

phase13_1_handoff_revalidation.json

phase13_2_contract_revalidation.json

scientific_authority_nonchange.json

phase12_baseline_nonchange.json

security.md

secret_scan.txt

manifest.json
```

---

# 75. Canonical Docs to Inspect / Correct

至少检查：

```text
docs/phase13/
phase13_seven_canonical_e2e_demo_contract.md

phase13_real_user_simulation_contract.md

phase13_acceptance_registry.md

phase13_initial_release_scope.md

phase13_initial_release_fact_model.md

phase13_1_integration_gap_handoff.md
```

以及 actual repository equivalent。

不要假设只有这些文件。

---

# 76. Generated JSON / Manifest Files

如果 canonical generator生成：

```text
seven_demo_registry.json

demo_negative_path_registry.json

initial_release_fact_model.json

initial_release_scope_baseline.json

phase13_acceptance_registry.json
```

必须通过 generator修，

不要手改 generated output而不改 authority source。

---

# 77. Generator Authority

修复顺序应：

```text
canonical source
→ generator
→ generated artifacts
→ semantic hashes
→ evidence manifest
```

不得：

```text
generated JSON manual patch
→ leave generator wrong
```

---

# 78. Historical results.md Addendum

implementation correction exact-SHA CI PASS 后，

append：

```text
# Phase 13-0 Clarification Round-Limit
Fact Alignment Correction Addendum
```

---

# 79. Addendum Must State

至少：

```text
original incorrect release statement

canonical AnalysisIntent authority

corrected statement

production behavior unchanged

scientific behavior unchanged

files corrected

Fact Model hash impact YES/NO

old Fact Model hash

new/current Fact Model hash

Scope Baseline hash impact YES/NO

old Scope Baseline hash

new/current Scope Baseline hash

determinism result

release blockers

release critical gaps

P13X0 status

demo executed count

13-1 gate

13-2 queue state
```

---

# 80. Do Not Rewrite Old Phase 13-0 Conclusion

旧：

```text
PASS / FINAL_FACTS_ALIGNED /
INITIAL_RELEASE_SCOPE_SEALED
```

保留历史原文。

Correction addendum必须声明：

```text
the clarification-round statement
inside the original Phase 13-0 result
is superseded by this addendum
```

---

# 81. Supersession Semantics

如果 hashes改变：

旧 baseline：

```text
HISTORICAL /
SUPERSEDED
```

新 baseline：

```text
CURRENT /
SEALED
```

---

# 82. If Hashes Do Not Change

则：

```text
OLD_HASH == CURRENT_HASH
```

且 correction addendum说明：

```text
clarification expectation was outside
the hashed semantic domain
```

必须有自动化 evidence。

---

# 83. Governance Test Placement

测试必须未来持续运行，

至少在：

```text
Phase 13 governance / release-scope audit
```

中执行。

避免 13-2/13-5再次出现两轮漂移。

---

# 84. Focused Tests

至少：

```text
clarification authority equality

max questions equality

second-round typed failure

one-round valid clarification

no resolved-Intent injection

demo registry consistency

negative-path consistency

acceptance registry consistency

hash dependency consistency

baseline determinism
```

全部 PASS。

---

# 85. Full Backend Regression

运行：

```text
uv run python -m pytest -q
```

要求：

```text
>= Phase 13-0 final backend floor
```

当前 known：

```text
1320 passed
```

actual repository floor优先。

---

# 86. Frontend Regression

运行：

```text
npm --prefix apps/web test
```

要求：

```text
>= Phase 13-0 final frontend floor
```

当前 known：

```text
455 passed
```

---

# 87. Typecheck / Build

必须：

```text
npm --prefix apps/web run typecheck = PASS

npm --prefix apps/web run build = PASS
```

---

# 88. Lock / Diff

必须：

```text
uv lock --check = PASS

git diff --check = PASS

LOCKFILE_CHANGES = 0
```

---

# 89. Browser

本 correction不需要执行七个 E2E demos。

只运行 current required retained browser/governance matrix。

至少：

```text
Chromium PASS

Firefox PASS

WebKit PASS

390x844 PASS
```

如果 exact-SHA CI仍要求。

---

# 90. Service Integration

必须继续：

```text
PostgreSQL

Redis

MinIO
```

required CI PASS。

虽然 production未变，

这是 release baseline regression gate。

---

# 91. Linux / Windows

如果 hash受影响，

必须验证：

```text
LINUX_BASELINE_HASH =
WINDOWS_BASELINE_HASH
```

---

# 92. If Hash Not Affected

仍保留 current sealed Linux/Windows invariant replay。

---

# 93. npm Audit

如果 mirror仍：

```text
NOT_IMPLEMENTED
```

记录：

```text
npm audit = UNAVAILABLE
```

不得写 clean。

---

# 94. Security

必须：

```text
NO_CORRECTION_ARBITRARY_CODE_EXECUTION = PASS

NO_CORRECTION_PRODUCTION_BEHAVIOR_CHANGE = PASS

NO_CORRECTION_REAL_LLM_CALL = PASS

NO_CORRECTION_EXTERNAL_DOWNLOAD = PASS

NO_SECRET_PATTERN_HITS = PASS
```

---

# 95. No External Downloads

必须：

```text
EXTERNAL_DOWNLOADS = 0
```

---

# 96. Implementation Commit Content

允许：

```text
Phase 13 docs correction

Phase 13 generated contract artifacts

release audit generator correction

governance tests

evidence

manifest/hash updates

persistent state

temporary correction TASK block
```

---

# 97. Implementation Commit Forbidden

禁止：

```text
backend production logic

frontend production logic

AnalysisIntent schema change

clarification API change

Planner change

Runtime change

Tool Registry change

scientific Adapter change

database migration

new dependency

13-1 implementation

13-2 execution
```

---

# 98. Correction Lifecycle

严格：

```text
verify clean post-13-0 archive baseline

→ admit one correction task

→ audit production AnalysisIntent authority

→ find all conflicting Phase 13 occurrences

→ correct canonical sources

→ regenerate generated artifacts

→ run hash dependency audit

→ regenerate affected baselines

→ verify deterministic hashes

→ run governance tests

→ run full regressions

→ build correction evidence

→ implementation correction commit

→ push

→ WAIT implementation correction exact-SHA CI
```

---

# 99. After Exact-SHA CI PASS

才允许 append correction completion addendum到：

```text
results.md
```

---

# 100. Correction Completion Commit

然后：

```text
commit
push
```

直接完成。

不等待额外 CI。

---

# 101. Correction Queue Archive

completion push后：

只移除 temporary correction task。

然后：

```text
commit
push
```

不等待额外 CI。

---

# 102. Do Not Touch Phase 13-1 Queue

必须：

```text
PHASE13_1_EXECUTABLE_TASK_CREATED = NO
```

---

# 103. Lifecycle Terminology

最终：

```text
CORRECTION_IMPLEMENTATION_VERIFIED_BY_EXACT_SHA_CI

CORRECTION_COMPLETION_RECORDED

CORRECTION_QUEUE_ARCHIVED
```

---

# 104. Failed Candidate Rule

如果 correction implementation CI失败：

必须保留：

```text
failed SHA

CI run

failure reason

fix-forward SHA
```

不得 rewrite history。

---

# 105. PASS Gate

只有全部成立：

```text
AnalysisIntent 1.0 authority verified

max rounds = 1

max questions = 3

second round = typed failure


all current Phase 13
two-round assertions removed

historical append-only result preserved


Phase13 clarification governance test PASS

one-round success case PASS

second-round rejection case PASS

resolved-Intent bypass = 0


seven demo contracts reconciled

negative paths reconciled

acceptance registry reconciled


Fact Model hash impact resolved YES/NO

Scope Baseline hash impact resolved YES/NO

affected hashes regenerated

unaffected hashes proven stable

baseline determinism PASS


release blockers = 0

release-critical integration gaps = 0

unclassified gaps = 0


Registry = 62

DataProfile = 2.4

AnalysisIntent = 1.0

EligibilityResolution = 1.0

AnalysisPlan = 0.1/0.2

migration = 0007


production code changes = 0

scientific behavior changes = 0

new Tool = 0

new algorithm = 0

new Artifact family = 0

new migration = 0

new API family = 0

new dependency = 0

new LLM call sites = 0

real LLM calls = 0


seven demo contracts = 7

demos executed = 0

P13X0 = 8/8


backend >= dynamic floor

frontend >= dynamic floor

typecheck PASS

build PASS

lock PASS

diff PASS

service integration PASS

required browser regression PASS

Linux/Windows required gates PASS

security PASS

secret scan PASS


correction implementation exact-SHA CI PASS

correction completion recorded

correction task archived


TASK_BLOCK_COUNT = 0

Phase 13-1 task absent

Phase 13-2 task absent

Phase14 absent

HEAD == origin/master

worktree clean
```

才允许：

```text
PHASE_13_0_FACT_CORRECTION = PASS
```

---

# 106. BLOCKED — Production Actually Supports Two Rounds

如果 audit发现 production current authority已经被其他 approved work改成：

```text
MAX_CLARIFICATION_ROUNDS = 2
```

不要把它改回 1。

必须：

```text
BLOCKED /
PRODUCTION_AUTHORITY_REVIEW_REQUIRED
```

返回 reviewer。

---

# 107. BLOCKED — Correction Requires Production Modification

如果无法通过 docs/generated contract correction解决，

而必须修改 production：

```text
BLOCKED /
CORRECTION_EXCEEDS_FACT_ALIGNMENT_SCOPE
```

---

# 108. BLOCKED — Hash Impact Unknown

如果无法证明：

```text
FACT_MODEL_HASH_IMPACT
```

或：

```text
SCOPE_BASELINE_HASH_IMPACT
```

则：

```text
BLOCKED /
SEMANTIC_HASH_DEPENDENCY_UNRESOLVED
```

---

# 109. BLOCKED — Baseline Nondeterminism

如果同一 clean repo：

```text
hash run 1 != hash run 2
```

必须：

```text
BLOCKED /
CORRECTED_BASELINE_NONDETERMINISTIC
```

---

# 110. BLOCKED — Release Blocker Count Changes

如果 correction audit意外发现：

```text
RELEASE_BLOCKERS > 0
```

或：

```text
RELEASE_CRITICAL_INTEGRATION_GAPS > 0
```

不要隐藏。

记录真实 gap并返回 reviewer。

---

# 111. BLOCKED — P13X0 No Longer Passes

如果 correction后：

```text
P13X0 != 8/8
```

不能完成。

---

# 112. Expected Corrected Authority

成功后：

```text
PHASE13_CLARIFICATION_MAX_ROUNDS = 1

PHASE13_CLARIFICATION_MAX_QUESTIONS = 3

PHASE13_SECOND_CLARIFICATION_ROUND =
TYPED_FAILURE

PHASE13_CLARIFICATION_AUTHORITY =
ANALYSIS_INTENT_1_0
```

---

# 113. Expected Release Gap State

仍应：

```text
RELEASE_BLOCKERS = 0

RELEASE_CRITICAL_INTEGRATION_GAPS = 0
```

如果事实支持。

---

# 114. Expected Phase 13-0 State

成功后正式：

```text
Phase 13-0:
PASS /
FINAL_FACTS_ALIGNED /
INITIAL_RELEASE_SCOPE_SEALED /
FACT_ALIGNMENT_CORRECTED /
QUEUE_ARCHIVED
```

---

# 115. Phase 13 State

```text
Phase 13:
IN_PROGRESS /
RELEASE_SCOPE_SEALED
```

---

# 116. Phase 13-1 State

```text
Phase 13-1:
REVIEWER_GATE /
ZERO_GAP_VERIFICATION_CLOSURE /
AWAITING REVIEWER PROMPT
```

---

# 117. Phase 13-2 State

```text
Phase 13-2:
CONTRACT_READY /
NOT_QUEUED /
NOT_EXECUTABLE
```

---

# 118. Initial Release

必须：

```text
INITIAL_RELEASE_COMPLETE = NO
```

---

# 119. Phase 14

必须：

```text
PHASE14_CREATED = NO
```

---

# 120. Final Result Must Report Hashes Explicitly

必须返回：

```text
OLD_FACT_MODEL_HASH =
e0248d502e4a442bb9596a8d2f6fe6d7fdefe61c41121ae08736734ce4004a06

FACT_MODEL_HASH_IMPACT =
YES / NO

CURRENT_FACT_MODEL_HASH =
<exact>


OLD_SCOPE_BASELINE_HASH =
8e8b4f659888635192d259eee90f3befdd655cacb292a78c5e13c20a5fdabdde

SCOPE_BASELINE_HASH_IMPACT =
YES / NO

CURRENT_SCOPE_BASELINE_HASH =
<exact>
```

---

# 121. Final Result Must Report Correction Scope

必须：

```text
CURRENT_CANONICAL_TWO_ROUND_ASSERTIONS = 0

HISTORICAL_TWO_ROUND_ASSERTIONS =
<count retained append-only>

PRODUCTION_FILES_CHANGED = 0

PRODUCTION_BEHAVIOR_CHANGED = 0
```

---

# 122. Final Result Must Report Clarification Tests

必须：

```text
ONE_ROUND_CLARIFICATION_SUCCESS = PASS

SECOND_ROUND_TYPED_FAILURE = PASS

MAX_THREE_QUESTIONS = PASS

RESOLVED_INTENT_BYPASS = 0
```

---

# 123. Final Result Must Report Lifecycle

返回：

```text
Correction implementation SHA

Correction implementation exact-SHA CI

Correction completion SHA

Correction archive SHA

failed correction candidates if any
```

---

# 124. Final Required Status Block

成功结果末尾必须：

```text
PHASE_13_0_FACT_CORRECTION = PASS

CORRECTION_TYPE =
FACT_ALIGNMENT_FIX_FORWARD

PHASE13_CLARIFICATION_MAX_ROUNDS = 1

PHASE13_CLARIFICATION_MAX_QUESTIONS = 3

PHASE13_SECOND_CLARIFICATION_ROUND =
TYPED_FAILURE

CURRENT_CANONICAL_TWO_ROUND_ASSERTIONS = 0

PRODUCTION_CODE_CHANGES = 0

PRODUCTION_BEHAVIOR_CHANGES = 0

SCIENTIFIC_BEHAVIOR_CHANGES = 0

FACT_MODEL_HASH_IMPACT =
<YES_OR_NO>

INITIAL_RELEASE_FACT_MODEL_HASH =
<current exact hash>

SCOPE_BASELINE_HASH_IMPACT =
<YES_OR_NO>

INITIAL_RELEASE_SCOPE_BASELINE_HASH =
<current exact hash>

BASELINE_DETERMINISM = PASS

RELEASE_BLOCKERS = 0

RELEASE_CRITICAL_INTEGRATION_GAPS = 0

P13X0_ACCEPTANCE = 8/8

PHASE13_DEMO_FAMILIES = 7

PHASE13_2_DEMOS_EXECUTED = 0

REGISTRY = 62

DATAPROFILE = 2.4

ANALYSIS_INTENT = 1.0

ELIGIBILITY_RESOLUTION = 1.0

ANALYSIS_PLAN = 0.1 / 0.2

MIGRATION =
0007_phase10m1_workspace_domain

PHASE_13_0 =
PASS /
FINAL_FACTS_ALIGNED /
INITIAL_RELEASE_SCOPE_SEALED /
FACT_ALIGNMENT_CORRECTED

PHASE_13_1 =
REVIEWER_GATE /
ZERO_GAP_VERIFICATION_CLOSURE /
AWAITING REVIEWER PROMPT

PHASE13_1_EXECUTABLE_TASK_CREATED = NO

PHASE13_2_EXECUTABLE_TASK_CREATED = NO

INITIAL_RELEASE_COMPLETE = NO

TASK_BLOCK_COUNT = 0

PHASE14_CREATED = NO

HEAD == origin/master

WORKTREE_CLEAN = YES
```

---

# 125. Stop Rule

完成 correction 并归档后立即停止。

不得：

```text
execute Phase 13-1

create Phase 13-1 task

execute any of seven demos

call real DeepSeek

start Phase 13-2

perform release polish

declare release-ready

declare Initial Release complete

create Phase 14
```

返回 reviewer并等待下一条 prompt。

完成时间：2026-08-11 19:39 +08:00

修改文件：`scripts/generate_phase13_0_release_scope.py`、`scripts/generate_phase13_0_clarification_correction.py`、`scripts/verify_phase13_0_clarification_hash.py`、`.github/workflows/ci.yml`、`tests/test_phase13_0_clarification_correction.py`、Phase 13 docs/evidence、persistent 状态文件、`results.md`、`TASKS.md`。

修改摘要：将 Phase 13 clarification projection 对齐 AnalysisIntent 1.0 的一轮、最多三问及第二轮 typed failure；保留旧历史记录；Fact Model hash 不变，Scope Baseline hash 以生成器确定性更新；未修改生产或科学行为。

测试结果：本地 backend `1327 passed, 50 skipped`；frontend `455 passed`；typecheck/build/uv lock/git diff/docs links/secret scan PASS；implementation `abe4bd68363f9eb9c357a840b17d0f2c216ebfee` exact-SHA CI `31455125693` PASS（含 Linux/Windows hash、service、Chromium/Firefox/WebKit/390x844）。

---END---
