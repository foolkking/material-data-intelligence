---TASK---
 状态：待处理


# Phase 11-5 Reviewer Prompt

# Scientific Validation Closure + Release Candidate Gate

你现在执行：

# Phase 11-5：Scientific Validation Closure + Release Candidate Gate

中文：

# 科学验证最终封板 + 科学发布候选门禁

本阶段属于：

```text id="m8xx11"
Phase 11:
Scientific Validation,
Reference Provenance,
Reproducibility
& Honest Coverage
```

这是整个 Phase 11 的最终阶段。

本阶段的职责不是继续验证更多科学。

本阶段的职责是：

```text id="o3b2wp"
verify Phase 11-0 governance

+
verify Phase 11-1 reference / fixture provenance closure

+
verify Phase 11-2 golden benchmark closure

+
verify Phase 11-3 cross-platform reproducibility closure

+
verify Phase 11-4 honest Tool / Input / Example coverage closure

+
reconcile all hashes / manifests / gaps / limitations

+
prove no release-blocking scientific validation gap remains

+
freeze final scientific-validation release baseline

+
publish final reproducibility and limitation package

+
seal Phase 11

+
open Phase 12 only as REVIEWER_GATE

+
stop
```

---

# 0. Fundamental Phase Rule

Phase 11-5 是：

```text id="uijcec"
CLOSURE
```

不是：

```text id="l2q1y6"
NEW VALIDATION
NEW SCIENCE
NEW REFERENCE
NEW BENCHMARK
NEW COVERAGE RECLASSIFICATION
NEW PLATFORM SUPPORT
NEW INPUT SUPPORT
NEW UI/UX
```

因此：

```text id="4a8it0"
PHASE11_5_NEW_SCIENTIFIC_VALIDATION = 0

PHASE11_5_NEW_REFERENCE_ACQUISITION = 0

PHASE11_5_NEW_GOLDEN_BENCHMARKS = 0

PHASE11_5_NEW_CROSS_PLATFORM_CASES = 0

PHASE11_5_NEW_COVERAGE_VERDICTS = 0
```

11-5 只能：

```text id="613rlo"
VERIFY
RECONCILE
HASH
SUMMARIZE
SEAL
ARCHIVE
```

---

# 1. Reviewer Authorization

正式条件预授权：

```text id="4whxf1"
PHASE_11_5_PROMPT_PREAUTHORIZED = YES

AUTHORIZED_PHASE = Phase 11-5

MAX_PHASES_EXECUTED = 1
```

只有 Entry Gate PASS 后才能 admission。

本 Prompt 不授权：

```text id="68lpbv"
Phase 12 implementation

Phase 13 implementation

Future Scope implementation
```

---

# 2. Mandatory Phase 11-4 Dependency

执行器必须从真实 repository 读取：

```text id="t3jm4m"
git history

results.md

TASKS.md

persistent/

docs/phase11/

docs/phase11/evidence/
```

动态取得：

```text id="pfs22g"
PHASE_11_4_IMPLEMENTATION_SHA

PHASE_11_4_IMPLEMENTATION_CI_RUN

PHASE_11_4_IMPLEMENTATION_CI_RESULT

PHASE_11_4_COMPLETION_SHA

PHASE_11_4_QUEUE_ARCHIVE_SHA
```

并确认：

```text id="e2lm5p"
Phase 11-4 =
PASS / HONEST_COVERAGE_SEALED

queue =
ARCHIVED

implementation exact-SHA CI =
PASS
```

如果不存在：

```text id="vxg0ao"
PHASE_11_5_ENTRY_GATE = BLOCKED

reason =
PHASE_11_4_NOT_COMPLETED_OR_NOT_ARCHIVED
```

立即停止。

---

# 3. Mandatory Phase 11-4 Handoff

必须找到唯一 canonical：

```text id="3smum0"
Phase11_5ClosureInputManifest
```

或 repository current equivalent。

不得根据本 Prompt 重建一份平行 authority。

必须读取其真实：

```text id="6on4u0"
Registry count

DataProfile version

migration head

validation-level distribution

Tool Coverage Matrix hash

Input Support Matrix hash

Official Example Coverage Matrix hash

Reference Registry hash

Fixture Registry hash

Golden Benchmark Suite hash

Phase 11-2 result summary

Phase 11-3 reproducibility summary

Tolerance Registry hash

Known Scientific Limitations hash

Remaining Gap Matrix hash

Revalidation Trigger Policy hash

roadmap state

release-blocking gap count

accepted limitation count

evidence refs
```

---

# 4. Closure Input Is Immutable

11-5 不得：

```text id="0kcgvi"
change 11-4 matrix

change coverage verdict

change Tool validation level

change input support verdict

change example verdict

change known limitation

change remaining gap priority
```

如果 closure handoff 与 source matrices不一致：

```text id="6dxv4i"
BLOCKED /
CLOSURE_HANDOFF_INTEGRITY_FAILURE
```

而不是修 handoff 让它通过。

---

# 5. Dynamic Entry Authority

Phase 11-5 entry authority：

```text id="pg5nw4"
PHASE_11_4_QUEUE_ARCHIVE_SHA
```

必须验证：

```text id="yn32h9"
branch = master

HEAD == origin/master

worktree = clean

11-4 implementation is ancestor of HEAD

11-4 completion is ancestor of HEAD

11-4 queue archive is ancestor of HEAD
```

如果存在 archive 后 commits：

必须证明：

```text id="s8pbhh"
NO_UNREVIEWED_PRODUCTION_CHANGES_AFTER_11_4
```

否则 BLOCKED。

---

# 6. Current Scientific Platform Floor

必须保持：

```text id="e0fj1b"
Registry = 62

DataProfile = 2.4

migration head =
0007_phase10m1_workspace_domain
```

并验证：

```text id="rzcsqm"
Registry count unchanged through Phase 11

DataProfile unchanged through Phase 11

migration unchanged through Phase 11
```

---

# 7. Phase 11 Authority Chain

必须验证完整：

```text id="a67gr4"
Phase 11-0
Validation Governance

↓

Phase 11-1
Reference Provenance / Fixtures

↓

Phase 11-2
Golden Scientific Benchmark

↓

Phase 11-3
Cross-Platform Reproducibility

↓

Phase 11-4
Honest Coverage

↓

Phase 11-5
Closure
```

任何缺失一环：

Phase 11 不得 COMPLETE。

---

# 8. Phase 11-0 Closure Verification

必须读取并 hash/reconcile：

```text id="izba4o"
validation governance

Tool validation matrix baseline

input-support governance

reference provenance policy

validation-level policy

tolerance registry

variance policy

revalidation trigger policy

gap taxonomy

execution lock

acceptance registry
```

11-5 不得重新定义这些政策。

---

# 9. Phase 11-1 Closure Verification

必须验证：

```text id="esnwbn"
reference registry

fixture registry

source checksum registry

license dispositions

raw-retention dispositions

transformation registry

reference independence matrix

official/example extraction status

11-2 benchmark handoff
```

至少确保：

```text id="o6p1ko"
reference identity resolves

fixture identity resolves

checksums resolve

provenance chain resolves

transformation chain resolves

no in-place fixture mutation occurred
```

---

# 10. Phase 11-2 Closure Verification

必须读取真实 final：

```text id="4vra6c"
Golden Scientific Benchmark Suite

benchmark result matrix

validation levels before

validation levels after

scientific discrepancy matrix

11-3 reproducibility handoff
```

并验证 suite semantic hash。

---

# 11. Current Known 11-2 Facts

当前 retained evidence 已知：

```text id="jjpq9q"
benchmark records = 12

PASS_INVARIANT = 8

NOT_APPLICABLE = 4

scientific failures = 0

blocked = 0
```

11-5 必须从 current repository重新读取 actual。

不得只因为 Prompt 有这些数字就跳过检查。

---

# 12. Four Reference-Limited Cases

如果 final 11-2 事实仍然是：

```text id="em7mlq"
NOT_APPLICABLE = 4
```

11-5 必须确保这四项：

```text id="xfma6x"
remain visible

remain typed

remain linked to affected capability

remain linked to coverage consequence

remain linked to limitation statement
```

不能在最终 Phase 11 summary消失。

---

# 13. Numeric Validation Honesty

如果这四项缺少：

```text id="bb84xo"
bounded expected numeric truth
```

最终必须保持：

```text id="tn1yr4"
NUMERIC_REFERENCE_VALIDATION_NOT_ESTABLISHED
```

不能：

```text id="6d1hd7"
derive PASS from invariant replay
```

---

# 14. Phase 11-3 Closure Verification

必须读取：

```text id="xk6pvc"
Linux environment identity

Windows environment identity

lock parity

reference replay matrix

variance matrix

browser presentation matrix

V4 transition matrix

11-4 honest coverage handoff
```

---

# 15. Current Known 11-3 Facts

当前 retained evidence 已知：

```text id="qjkpip"
reproducibility cases = 8

Linux sealed invariant reference PASS = 8/8

Windows sealed invariant reference PASS = 8/8

numeric cross-platform comparison =
NOT_APPLICABLE

V4 promotions = 0
```

11-5 必须从 repository验证实际 final facts。

---

# 16. Cross-Platform Honesty

最终 Reproducibility Report 可以写：

```text id="lrttzz"
Linux and Windows reproduced the admitted
sealed invariant/reference cases
under the locked environment.
```

如果事实如此。

不能写：

```text id="7zn58s"
all numeric scientific results
are cross-platform validated
```

---

# 17. V4 Honesty

如果 final matrix：

```text id="wwl3gk"
V4 = 0
```

必须显式报告。

禁止隐藏：

```text id="1jr1px"
V4 count
```

也禁止把：

```text id="d5mz7b"
cross-platform invariant replay
```

重新命名为 V4。

---

# 18. Phase 11-4 Closure Verification

必须读取 final：

```text id="jlcj9j"
Tool Coverage Matrix

Input Support Matrix

Official / Candidate Example Coverage Matrix

Support × Validation Matrix

Public Scientific Claim Matrix

Known Scientific Limitations

Remaining Gap Matrix

coverage transition audit

coverage distributions

Phase11_5ClosureInputManifest
```

---

# 19. Tool Coverage Matrix Exactness

必须：

```text id="0w8ka6"
Registry = 62

Tool coverage rows = 62

missing = 0

extra = 0

duplicate = 0

unclassified = 0
```

任何不等：

BLOCKED。

---

# 20. Tool-Version Identity

每个 Tool coverage row：

必须：

```text id="o25pb5"
Tool ID + Tool version
```

为 exact identity。

不得按 domain summary替代。

---

# 21. Coverage Taxonomy Freeze

必须保持唯一：

```text id="0n77kq"
DIRECT_VERIFIED

OFFICIAL_DERIVED_VERIFIED

REFERENCE_VERIFIED

MAPPING_ONLY

EXTRACTION_REQUIRED

FUTURE_SCOPE

UNSUPPORTED
```

11-5不得改变任何 row。

---

# 22. Input Support Taxonomy Freeze

必须保持：

```text id="a27etp"
DIRECT_SUPPORTED

SUPPORTED_WITH_LIMITS

MAPPING_ONLY

PARSE_ONLY

UNSUPPORTED

FUTURE_SCOPE
```

---

# 23. Current Input Baseline

如果 11-4 final无 reviewer-approved change：

应继续是：

```text id="yu1p6d"
DIRECT_SUPPORTED:

CSV
CIF
POSCAR
```

```text id="f5bxl2"
SUPPORTED_WITH_LIMITS:

canonical JSON
XYZ / EXTXYZ
volumetric
ZIP
supplied electronic JSON
```

```text id="xowvuv"
MAPPING_ONLY:

phonon direct upload
```

```text id="xxodg8"
UNSUPPORTED:

XLSX
Parquet
LAMMPS trajectory
```

必须动态从 final matrix验证。

不得重新推断。

---

# 24. Official / Candidate Example Matrix

必须验证：

```text id="vsni9n"
all final retained example rows classified

unclassified = 0

duplicates = 0

all source identities resolve

all verdicts allowed
```

11-5 不得执行 example。

---

# 25. Public Scientific Claim Matrix

必须验证每个 release claim：

具有：

```text id="fu188v"
approvedClaim

requiredQualifier

prohibitedClaim

evidenceRefs
```

不得发布没有 evidenceRefs 的 scientific claim。

---

# 26. Scientific Claim Boundary — Coordination

必须保持：

```text id="hnc2jn"
algorithm-derived local coordination
```

禁止：

```text id="7zdi74"
true chemical bond
```

---

# 27. Scientific Claim Boundary — Local Environment

必须保持：

```text id="4qemry"
algorithm/geometry-derived local environment
```

不能扩大：

```text id="eg1qfa"
definitive oxidation
definitive bonding
```

---

# 28. Scientific Claim Boundary — XRD

必须保持：

```text id="e36l66"
peak correspondence under tolerance
```

不能：

```text id="v995b5"
phase confirmation

phase identification

Rietveld refinement
```

---

# 29. Scientific Claim Boundary — Diffusion

必须保持：

```text id="0x79jk"
estimated diffusion
over selected fit window
```

不能：

```text id="opwdc4"
unconditional bulk diffusivity
```

---

# 30. Scientific Claim Boundary — Electronic

必须保持：

```text id="ezho5z"
analysis of supplied/imported
Band Structure / DOS data
```

不能：

```text id="6si7eq"
platform DFT

platform GW

electronic ground-state calculation
```

---

# 31. Phonon Boundary

必须避免暗示：

```text id="xl303c"
platform first-principles phonon calculation
```

如果当前只分析 imported/supplied phonon data。

---

# 32. Volumetric Boundary

必须继续排除：

```text id="hty3mx"
Bader

charge topology

advanced ELF topology
```

---

# 33. Future Scope Guard

必须最终冻结 Future Scope：

至少继续包括：

```text id="8bh1xj"
Fermi surface

projected bands / fatbands

full Rietveld refinement

phase fractions

automatic phase identification

advanced diffraction

Bader / charge topology

defects

surfaces / slabs

advanced transport

effective mass

advanced trajectory:
VACF
Green-Kubo
Arrhenius
hop detection
van Hove
```

只作为：

```text id="kybkuc"
DOCUMENTED / UNQUEUED
```

---

# 34. Not Planned Guard

继续保持：

```text id="nsdpcj"
generic workflow platform

arbitrary DAG engine

arbitrary Python/Shell

notebook execution platform

runtime autonomous replanning

RAG/vector DB

plugin marketplace

multi-tenant SaaS

billing

enterprise RBAC

Kubernetes productization

distributed scheduler

KMS/HSM productization

unrestricted multi-provider LLM
```

---

# 35. Remaining Gap Matrix

11-5 必须读取 final：

```text id="t9dg2s"
Phase11RemainingGapMatrix
```

并重新统计：

```text id="pyxom8"
P0

P1

P2
```

---

# 36. Release-Blocking Gap Definition

11-5 最关键 gate：

```text id="99pvhc"
RELEASE_BLOCKING_GAP_COUNT
```

必须来自 11-4 final handoff。

不是 execution agent自己决定。

---

# 37. Release-Blocking Gap Gate

要求：

```text id="slbr6e"
RELEASE_BLOCKING_GAP_COUNT = 0
```

才允许 Phase 11 COMPLETE。

如果：

```text id="2fyzvk"
> 0
```

必须：

```text id="rtnvhm"
Phase 11-5:
BLOCKED /
SCIENTIFIC_VALIDATION_RELEASE_BLOCKERS_REMAIN
```

停止。

不得：

```text id="g7uft9"
downgrade blocker

convert to limitation

hide from summary
```

---

# 38. P0 Gate

必须：

```text id="t235hp"
P0 = 0
```

任何 P0：

Phase 11不得 close。

---

# 39. P1/P2 May Remain Only If Accepted

P1/P2 可以继续存在：

仅当 Phase 11-4 已明确：

```text id="i9l4lg"
ACCEPTED_EXPLICIT_LIMITATION
```

并且：

```text id="w65hp3"
releaseBlocking = false
```

11-5 不拥有把 gap变 accepted limitation 的权限。

---

# 40. Accepted Limitation Must Be Traceable

每个 accepted limitation必须：

```text id="5zk35w"
limitationId

affected Tool/input/example

scientific consequence

user-facing consequence

what remains supported

what is not claimed

evidence

Phase 11 governance disposition

revalidation trigger
```

---

# 41. No New Limitation During Closure

禁止：

```text id="bxuydd"
new failure discovered
→ call it known limitation
```

新发现事实必须：

```text id="rocd2z"
BLOCKED / REVIEWER_REQUIRED
```

除非它纯粹是 already-existing limitation missing from one summary file，且 source authority明确。

---

# 42. Final Reference Registry

必须产出一个 Phase 11 final reference index：

不是复制 reference bytes。

至少：

```text id="mlwqj4"
referenceId

referenceVersion

referenceType

source identity

source version

checksum

license disposition

independence

fixture links

Tool/version links

benchmark links

coverage links

status
```

---

# 43. Final Fixture Registry

必须产出：

```text id="n1ephx"
fixtureId

fixtureVersion

normalized checksum

source checksum

referenceId

transformationId

Tool/version applicability

benchmark IDs

immutability status
```

---

# 44. Final Golden Benchmark Registry

必须索引：

```text id="n0gbwm"
suite ID/version

all benchmark IDs

Tool/version

fixture/reference

expected truth type

units

tolerance IDs

final verdict

limitations
```

11-5 不执行 benchmark。

---

# 45. Final Tolerance Registry

必须冻结当前：

```text id="60ed1k"
Phase11ToleranceRegistry
```

并生成 final semantic hash。

必须验证：

```text id="bd1gqw"
all benchmark tolerance IDs resolve

no orphan required tolerance

no pass-driven modification
```

---

# 46. Final Variance Matrix

必须冻结：

```text id="ko3z2j"
EXACT

TOLERANCE_BOUNDED

DISPLAY_ONLY_VARIANCE

UNSUPPORTED_PLATFORM

KNOWN_LIMITATION
```

实际 11-3结果。

不得新增数据。

---

# 47. Final Validation-Level Distribution

必须读取最终 Tool Validation Matrix：

报告：

```text id="c9ok0g"
V0_COUNT

V1_COUNT

V2_COUNT

V3_COUNT

V4_COUNT
```

不能使用 11-0 baseline作为 final。

---

# 48. Validation-Level Honesty

如果：

```text id="m93uj0"
V4_COUNT = 0
```

必须明确。

不能说：

```text id="5uvg3v"
cross-platform scientifically verified
```

而省略其 invariant-only限制。

---

# 49. Final Coverage Distribution

Tool Coverage：

必须统计：

```text id="l9gxch"
DIRECT_VERIFIED_COUNT

OFFICIAL_DERIVED_VERIFIED_COUNT

REFERENCE_VERIFIED_COUNT

MAPPING_ONLY_COUNT

EXTRACTION_REQUIRED_COUNT

FUTURE_SCOPE_COUNT

UNSUPPORTED_COUNT
```

要求：

```text id="s8tjfs"
sum = 62
```

---

# 50. Final Input Coverage Distribution

统计：

```text id="b29502"
DIRECT_SUPPORTED

SUPPORTED_WITH_LIMITS

MAPPING_ONLY

PARSE_ONLY

UNSUPPORTED

FUTURE_SCOPE
```

并确保：

```text id="qf8xxe"
sum = all current input rows
```

---

# 51. Final Example Distribution

统计七种 coverage verdict。

要求：

```text id="l1ao5n"
sum =
current canonical official/example inventory count
```

---

# 52. Final Scientific Reproducibility Report

必须新增：

# Phase 11 Scientific Reproducibility Report

至少包含：

```text id="r1o7k8"
validated environment

locked dependency policy

reference authority

fixture authority

golden benchmark summary

Linux status

Windows status

browser scope

service scope

determinism

identity

unit handling

tolerance model

variance results

numeric limitations

platform limitations

revalidation triggers
```

---

# 53. Reproducibility Report Must Distinguish Axes

至少明确：

```text id="3zyhwz"
Scientific reference validation

Software regression

Cross-platform invariant reproducibility

Numeric cross-platform reproducibility

Browser presentation

Service-backed persistence
```

不能揉成：

```text id="ovq3xf"
reproducible = PASS
```

---

# 54. Final Known Scientific Limitations

必须形成正式：

# Known Scientific Limitations

至少覆盖：

```text id="qqrc5b"
reference limitations

numeric-reference limitations

validation-level limitations

algorithm semantics

input-support limitations

platform limitations

browser limitations

service authority boundary

scientific claim boundaries

Future Scope
```

---

# 55. Four N/A Cases Must Be Explicit

如果 final仍为四项：

必须建立：

```text id="tke5np"
REFERENCE_LIMITED_CASE_COUNT = 4
```

并逐项列：

```text id="5ri2xo"
benchmarkId

Tool/version

scientific family

available evidence

missing evidence

why N/A

effect on validation level

effect on public claim

effect on release
```

---

# 56. No “Scientifically Correct” Blanket Claim

最终禁止：

```text id="jgsm4c"
scientifically correct

fully scientifically validated

all algorithms validated

all outputs independently verified

numerically identical across platforms
```

除非精确限定到具体 evidence。

---

# 57. Preferred Phase 11 Completion Wording

如果 PASS：

推荐最终状态：

```text id="fl962o"
Phase 11:
COMPLETE /
REFERENCE_VALIDATED_WITH_EXPLICIT_LIMITS
```

或者 repository 已封板 equivalent。

不得：

```text id="044796"
ALL_SCIENCE_CORRECT
```

---

# 58. Meaning of Phase 11 COMPLETE

必须定义：

```text id="1zhpo5"
Phase 11 COMPLETE
```

仅表示：

```text id="nijncp"
Initial Release scientific capabilities
have been audited, provenance-indexed,
benchmarked to the extent supported by sealed references,
reproducibility-characterized,
honestly classified,
and closed with explicit limitations.
```

不表示：

```text id="riwzpi"
every possible scientific quantity
has independent numeric ground truth
```

---

# 59. Scientific Release Candidate Meaning

`Release Candidate Gate` 在这里仅表示：

```text id="6mslgq"
SCIENTIFIC_VALIDATION_BASELINE_READY
FOR DOWNSTREAM PRODUCT EXPERIENCE / RELEASE WORK
```

不是：

```text id="kesrfl"
FINAL PRODUCT RELEASE READY
```

因为 Phase 12 和 Phase 13 尚未完成。

---

# 60. Phase 12 Transition

Phase 11-5 PASS 后：

应变为：

```text id="v5dmcx"
Phase 12:
REVIEWER_GATE /
AWAITING REVIEWER PROMPT
```

不得：

```text id="i4s9an"
auto-create Phase 12 task
```

---

# 61. Phase 12 Scope Reminder

Phase 12 已批准：

```text id="th969e"
Comprehensive UI / UX
Product Experience Redesign
```

包括：

```text id="wjh9mx"
12-0
UX Reality Audit

12-1
Design System 2.0

12-2
Navigation + Planner/Agent UX

12-3
Workspace + Viewer UX

12-4
Findings/Evidence/Inspector UX

12-5
Report/Recipe UX

12-6
Responsive/Mobile/Accessibility

12-7
UX Validation
```

11-5 不执行任何一项。

---

# 62. Phase 12 Scientific Authority Contract

11-5 必须生成一份供 Phase 12 使用的：

# UI/UX Scientific Authority Handoff

至少包括：

```text id="vdhlb9"
approved public claims

required qualifiers

prohibited claims

Tool availability

input support

validation levels

coverage verdicts

known limitations

warning language requirements

evidence/provenance visibility requirements

unsupported/future-scope distinctions
```

---

# 63. UI/UX Handoff Is Read-Only Science

Phase 12 可以：

```text id="o7i1x5"
change how facts are displayed
```

不能：

```text id="t5d4zn"
change scientific facts
```

11-5 必须明确：

```text id="wz7f1k"
PHASE12_SCIENTIFIC_AUTHORITY =
READ_ONLY_FROM_PHASE11_FINAL_BASELINE
```

除非未来有 reviewer-approved science correction。

---

# 64. Phase 13 Transition

Phase 13继续：

```text id="x4aaax"
ROADMAP_APPROVED /
NOT_QUEUED /
NOT_EXECUTABLE
```

直到 Phase 12 closure 后 reviewer批准。

---

# 65. Final Phase 11 Version Matrix

必须建立：

# Scientific Validation Version Matrix

至少：

```text id="vkpo9r"
Registry count

DataProfile

AnalysisIntent

EligibilityResolution

AnalysisPlan

migration head

Tool IDs/versions

scientific authority dependency versions

reference registry version/hash

fixture registry version/hash

golden benchmark suite version/hash

tolerance registry version/hash

coverage matrix versions/hashes

validation baseline version/hash
```

---

# 66. Dependency Version Matrix

必须记录当前 scientific-authority dependencies：

例如实际 repository：

```text id="h1kjfk"
Python

NumPy

SciPy

pandas

pymatgen

spglib

Plotly
```

以及其它真正参与科学 authority 的 lock versions。

不得从模型记忆猜版本。

必须读取 current environment/lock evidence。

---

# 67. Browser Version Boundary

浏览器 CI 可以记录 runner/browser identity。

但 browser版本：

不是 scientific reference authority。

---

# 68. Final Evidence Manifest

必须建立 Phase 11 umbrella：

```text id="vejmwx"
docs/phase11/evidence/
phase11_5_scientific_validation_closure/
```

以及一个：

```text id="upbon8"
Phase11FinalEvidenceManifest
```

---

# 69. Umbrella Evidence Must Reference, Not Duplicate

Phase 11-5 不应复制所有 11-0～11-4 evidence。

应：

```text id="ew4iyc"
reference exact relative path
+
semantic hash
+
file checksum
```

形成 umbrella manifest。

---

# 70. Evidence Roots

至少索引：

```text id="lmw2nu"
phase11_0_validation_baseline_reconciliation

phase11_1_reference_provenance_safe_fixture

phase11_2_golden_scientific_benchmark

phase11_3_cross_platform_reproducibility

phase11_4_honest_coverage
```

以及当前 exact canonical paths。

---

# 71. Evidence Integrity

必须：

```text id="yrqrhj"
missing referenced file = 0

checksum mismatch = 0

semantic-hash mismatch = 0

duplicate authority ID = 0

broken relative path = 0

orphan release-critical gap = 0

unresolved Tool coverage row = 0

unresolved input row = 0

unresolved example row = 0
```

---

# 72. Manifest Hash

最终：

```text id="9d4b0y"
PHASE11_FINAL_EVIDENCE_MANIFEST_SHA256
```

必须 deterministic。

---

# 73. Scientific Baseline ID

建议/要求建立：

```text id="d1ha9a"
PHASE11_SCIENTIFIC_VALIDATION_BASELINE_ID
```

例如 repository canonical naming：

```text id="w6x4on"
phase11-initial-release-scientific-validation-v1
```

实际命名必须遵从 current docs convention。

该 ID 只是 documentation/evidence identity。

不是 runtime contract。

---

# 74. Baseline Semantic Hash

建立：

```text id="68vnth"
scientificValidationBaselineHash
```

至少覆盖：

```text id="0wty5w"
Tool/version matrix hash

input support matrix hash

reference registry hash

fixture registry hash

benchmark suite hash

tolerance registry hash

variance matrix hash

known limitation hash

public claim matrix hash

revalidation policy hash
```

---

# 75. Revalidation Trigger Closure

必须确认最终 triggers继续包括：

```text id="al4h7t"
Tool scientific version change

algorithm change

algorithm default semantic change

Artifact scientific contract change

unit/reference semantic change

scientific parser semantic change

scientific authority dependency change

fixture expected truth change

tolerance change

identity model change
```

---

# 76. Phase 12 Changes Do Not Automatically Invalidate Science

必须明确：

```text id="7bkz73"
CSS

layout

typography

visual hierarchy

non-scientific wording

presentation order
```

通常：

```text id="ni3zu8"
DO_NOT_INVALIDATE_SCIENTIFIC_NUMERIC_VALIDATION
```

但仍要求：

```text id="83u2kb"
browser/accessibility/product regression
```

---

# 77. Phase 12 Must Revalidate If It Crosses Authority Boundary

如果 Phase 12意外修改：

```text id="1htn0a"
scientific computation

Tool semantics

units

identity

Artifact scientific interpretation

frontend scientific recomputation
```

则必须触发：

```text id="zo1071"
SCIENTIFIC_REVALIDATION_REQUIRED
```

不能因为它名义上是 UI phase 而跳过。

---

# 78. Final Support × Validation Contract

11-5 必须冻结：

```text id="vlc57y"
Product Support
!=
Scientific Validation
!=
Cross-Platform Reproducibility
!=
Presentation Validation
```

四轴不能合并成一个 badge。

---

# 79. Input Support ≠ Scientific Truth

再次冻结：

```text id="ax3zbb"
can parse
!=
scientifically validated
```

---

# 80. Cross-Platform Agreement ≠ Independent Truth

冻结：

```text id="lh8mw0"
Linux == Windows
!=
independent numeric validation
```

---

# 81. Browser PASS ≠ Science PASS

冻结：

```text id="r2k4mv"
Browser PASS
!=
scientific reference PASS
```

---

# 82. Service PASS ≠ Science PASS

冻结：

```text id="g4btvy"
Service PASS
!=
scientific reference PASS
```

---

# 83. Screenshot Authority

必须：

```text id="5upyyh"
SCREENSHOT_NUMERIC_SCIENTIFIC_AUTHORITY = NONE
```

---

# 84. LLM Authority

必须：

```text id="366c2e"
LLM_SCIENTIFIC_NUMERIC_AUTHORITY = NONE
```

---

# 85. DeepSeek Policy

Phase 11-5：

```text id="64tyhl"
NEW_LLM_CALL_SITES = 0

REAL_LLM_CALLS = 0
```

现有 DeepSeek-only policy不变。

---

# 86. No External Network

必须：

```text id="pxe03u"
EXTERNAL_REFERENCE_DOWNLOADS = 0

EXTERNAL_SCIENTIFIC_API_CALLS = 0

EXTERNAL_VALIDATION_RESEARCH = 0
```

---

# 87. Production Behavior Freeze

必须：

```text id="3328n9"
PRODUCTION_BEHAVIOR_CHANGES = NONE
```

---

# 88. Production Source Boundary

默认：

```text id="a6my8w"
PRODUCTION_SOURCE_CHANGES = 0
```

允许：

```text id="jlq7i5"
closure validators

evidence manifest generators

docs

persistent state

TASKS

results
```

---

# 89. No Scientific Fixes

如果 closure发现：

```text id="psw0ew"
scientific mismatch

missing required benchmark

wrong coverage

wrong unit

wrong reference
```

不得：

```text id="ab0dje"
fix production
or
invent evidence
```

必须 BLOCKED。

---

# 90. No Coverage Fixes

如果发现 11-4 verdict错误：

不得 11-5静默改 matrix。

必须：

```text id="0gcigi"
COVERAGE_CLOSURE_INCONSISTENCY
```

BLOCKED。

---

# 91. Database Freeze

必须：

```text id="rurr64"
NEW_DATABASE_TABLES = 0

NEW_DATABASE_COLUMNS = 0

NEW_MIGRATIONS = 0

migration =
0007_phase10m1_workspace_domain
```

---

# 92. API Freeze

必须：

```text id="y6ss9w"
NEW_PUBLIC_API_FAMILIES = 0
```

---

# 93. Dependency Freeze

必须：

```text id="uj678i"
NEW_PYTHON_DEPENDENCIES = 0

NEW_FRONTEND_DEPENDENCIES = 0

LOCKFILE_CHANGES = 0
```

---

# 94. Registry Freeze

必须：

```text id="zpsgs0"
REGISTRY_BEFORE_11_5 = 62

REGISTRY_AFTER_11_5 = 62
```

---

# 95. DataProfile Freeze

必须：

```text id="tlpb7a"
DATAPROFILE_BEFORE_11_5 = 2.4

DATAPROFILE_AFTER_11_5 = 2.4
```

---

# 96. AnalysisPlan Freeze

必须：

```text id="cal34f"
AnalysisPlan 0.1 / 0.2 unchanged
```

---

# 97. Artifact Freeze

必须：

```text id="6btzu2"
NEW_PRODUCTION_ARTIFACT_FAMILIES = 0
```

---

# 98. Validation Level Freeze

必须：

```text id="0x5ypl"
PHASE11_5_VALIDATION_LEVEL_PROMOTIONS = 0

PHASE11_5_VALIDATION_LEVEL_DEMOTIONS = 0
```

11-5只冻结 11-4输入。

---

# 99. Coverage Freeze

必须：

```text id="io0i8y"
PHASE11_5_TOOL_COVERAGE_CHANGES = 0

PHASE11_5_INPUT_SUPPORT_CHANGES = 0

PHASE11_5_EXAMPLE_COVERAGE_CHANGES = 0
```

---

# 100. Reference Freeze

必须：

```text id="rjpdi4"
PHASE11_5_REFERENCE_MUTATIONS = 0

PHASE11_5_FIXTURE_MUTATIONS = 0

PHASE11_5_EXPECTED_VALUE_MUTATIONS = 0
```

---

# 101. Tolerance Freeze

必须：

```text id="caf335"
PHASE11_5_TOLERANCE_CHANGES = 0
```

---

# 102. Benchmark Freeze

必须：

```text id="ow1s3m"
PHASE11_5_NEW_BENCHMARKS = 0

PHASE11_5_BENCHMARK_REEXECUTIONS_FOR_NEW_AUTHORITY = 0
```

普通 regression可以跑。

但不能生成新 validation status。

---

# 103. Cross-Platform Freeze

必须：

```text id="i4jyim"
PHASE11_5_NEW_CROSS_PLATFORM_CASES = 0
```

---

# 104. Security

必须：

```text id="8f8wr7"
NO_PHASE11_5_ARBITRARY_CODE_EXECUTION = PASS

NO_PHASE11_5_NOTEBOOK_EXECUTION = PASS

NO_PHASE11_5_DOWNLOADED_SCRIPT_EXECUTION = PASS

NO_PHASE11_5_EXTERNAL_SCIENTIFIC_API = PASS

NO_PHASE11_5_REFERENCE_DOWNLOAD = PASS

NO_PHASE11_5_FRONTEND_SCIENTIFIC_RECOMPUTATION = PASS

NO_PHASE11_5_LLM_SCIENTIFIC_AUTHORITY = PASS

NO_SECRET_PATTERN_HITS = PASS
```

---

# 105. Final Documentation Deliverables

至少新增：

```text id="lil56d"
docs/phase11/
phase11_5_scientific_validation_closure.md

docs/phase11/
phase11_final_scientific_validation_baseline.md

docs/phase11/
phase11_final_reference_registry.md

docs/phase11/
phase11_final_fixture_registry.md

docs/phase11/
phase11_final_golden_benchmark_registry.md

docs/phase11/
phase11_final_tolerance_registry.md

docs/phase11/
phase11_final_variance_matrix.md

docs/phase11/
phase11_final_reproducibility_report.md

docs/phase11/
phase11_final_known_scientific_limitations.md

docs/phase11/
phase11_final_validation_version_matrix.md

docs/phase11/
phase11_final_evidence_index.md

docs/phase11/
phase11_phase12_scientific_authority_handoff.md

docs/phase11/
phase11_5_completion.md
```

如果 existing naming convention已有 canonical equivalents：

使用 current names。

不得创建重复 authority。

---

# 106. Existing Final Matrices Remain Authorities

Phase 11-4 已生成的：

```text id="sszbvu"
final Tool Coverage Matrix

final Input Support Matrix

final Official Example Coverage Matrix

Support × Validation Matrix

Public Scientific Claim Matrix
```

不要在 11-5复制出：

```text id="vwk49x"
final_final_*.md
```

11-5应引用/hash并索引。

---

# 107. Final Evidence Directory

建立：

```text id="gn06px"
docs/phase11/evidence/
phase11_5_scientific_validation_closure/
```

至少：

```text id="rx0vso"
baseline.txt

entry_gate.md

phase11_4_handoff_snapshot.json

phase11_authority_chain.json

phase11_version_matrix.json

phase11_validation_level_distribution.json

phase11_tool_coverage_distribution.json

phase11_input_support_distribution.json

phase11_example_coverage_distribution.json

phase11_reference_registry_index.json

phase11_fixture_registry_index.json

phase11_golden_suite_index.json

phase11_tolerance_registry_index.json

phase11_variance_index.json

phase11_reproducibility_summary.json

phase11_reference_limited_cases.json

phase11_known_limitations.json

phase11_remaining_gaps.json

phase11_release_blocker_audit.json

phase11_accepted_limitation_audit.json

phase11_public_claim_audit.json

phase11_revalidation_trigger_audit.json

phase12_scientific_authority_handoff.json

phase11_final_evidence_manifest.json

phase11_final_baseline.json

no_new_science_audit.md

no_mutation_audit.md

no_overclaim_audit.md

no_production_change_audit.md

security.md

docs_link_check.txt

secret_scan.txt

manifest.json
```

---

# 108. Final Acceptance Registry

建立 exact 12 项：

```text id="2a3tav"
P11V5-A01
PHASE11_4_HONEST_COVERAGE_HANDOFF_ENTRY_AND_CLOSURE_AUTHORITY

P11V5-A02
PHASE11_0_VALIDATION_GOVERNANCE_AND_POLICY_INTEGRITY

P11V5-A03
PHASE11_1_REFERENCE_FIXTURE_PROVENANCE_AND_IMMUTABILITY_INTEGRITY

P11V5-A04
PHASE11_2_GOLDEN_BENCHMARK_RESULT_AND_REFERENCE_LIMITATION_INTEGRITY

P11V5-A05
PHASE11_3_LINUX_WINDOWS_REPRODUCIBILITY_VARIANCE_AND_V4_INTEGRITY

P11V5-A06
PHASE11_4_TOOL_INPUT_EXAMPLE_COVERAGE_AND_PUBLIC_CLAIM_INTEGRITY

P11V5-A07
FINAL_REFERENCE_FIXTURE_BENCHMARK_TOLERANCE_AND_VARIANCE_REGISTRY_SEAL

P11V5-A08
FINAL_REPRODUCIBILITY_KNOWN_LIMITATION_VERSION_AND_REVALIDATION_PACKAGE

P11V5-A09
ZERO_RELEASE_BLOCKING_SCIENTIFIC_VALIDATION_GAPS_AND_EXPLICIT_LIMITATION_CLOSURE

P11V5-A10
PHASE12_READ_ONLY_SCIENTIFIC_AUTHORITY_HANDOFF_AND_ROADMAP_GATE

P11V5-A11
NO_NEW_SCIENCE_NO_PRODUCTION_CHANGE_SECURITY_REGRESSION_AND_EVIDENCE_INTEGRITY

P11V5-A12
IMPLEMENTATION_EXACT_SHA_CI_PHASE11_COMPLETION_QUEUE_ARCHIVE_AND_PHASE12_REVIEWER_GATE
```

要求：

```text id="xnw71y"
expected = 12

implemented = 12

missing = 0

extra = 0

duplicate = 0

conflicting = 0

shorthand = 0
```

---

# 109. Queue Admission

Entry Gate PASS 后：

只创建：

```text id="2p1xwh"
one Phase 11-5 task
```

要求：

```text id="qtzb74"
TASK_BLOCK_COUNT = 1

ACTIVE_TASK = Phase 11-5

PHASE_12_EXECUTABLE_TASK_CREATED = NO

PHASE_13_EXECUTABLE_TASK_CREATED = NO
```

---

# 110. Persistent State Updates

完成后必须同步：

```text id="xfnjv4"
persistent/PROJECT_BRIEF.md

persistent/DESIGN_PROGRESS.md

persistent/TASK_BOARD.md

persistent/CHANGELOG.md

persistent/OPEN_QUESTIONS.md

persistent/ARCHITECTURE_DECISIONS.md

persistent/TOOL_REGISTRY_NOTES.md
```

---

# 111. Roadmap Update

Phase 11-5 PASS 后：

`docs/ROADMAP.md` 必须表达：

```text id="3h9o4m"
Phase 11:
COMPLETE /
REFERENCE_VALIDATED_WITH_EXPLICIT_LIMITS

Phase 12:
REVIEWER_GATE /
AWAITING REVIEWER PROMPT

Phase 13:
ROADMAP_APPROVED /
NOT_QUEUED

Future Scope:
DOCUMENTED /
NOT_QUEUED
```

---

# 112. Do Not Mark Initial Release Complete

必须：

```text id="qleuno"
INITIAL_RELEASE_COMPLETE = NO
```

因为仍然需要：

```text id="k72v14"
Phase 12 UI/UX redesign

Phase 13 Final Product Closure
```

---

# 113. Do Not Mark Product Release Candidate

Phase 11 的：

```text id="odl9z2"
Release Candidate Gate
```

是：

```text id="hfwcj9"
SCIENTIFIC_VALIDATION_RELEASE_CANDIDATE
```

不是：

```text id="ptel7j"
FINAL_PRODUCT_RELEASE_CANDIDATE
```

---

# 114. Final Phase 11 Status

PASS 后必须使用：

```text id="ucqnpi"
Phase 11:
COMPLETE /
REFERENCE_VALIDATED_WITH_EXPLICIT_LIMITS
```

建议同时：

```text id="idxbub"
SCIENTIFIC_VALIDATION_BASELINE = SEALED
```

---

# 115. Phase 12 State

最终：

```text id="3vuz42"
Phase 12:
REVIEWER_GATE /
AWAITING REVIEWER PROMPT

PHASE_12_EXECUTABLE_TASK_CREATED = NO
```

---

# 116. Phase 13 State

最终：

```text id="btdg7p"
Phase 13:
ROADMAP_APPROVED /
NOT_QUEUED /
NOT_EXECUTABLE
```

---

# 117. Future Scope State

最终：

```text id="z3rjt2"
FUTURE_SCOPE =
DOCUMENTED /
UNQUEUED
```

---

# 118. No Phase 14

必须：

```text id="qp7wlh"
PHASE14_CREATED = NO
```

---

# 119. Regression Floors

动态从 Phase 11-4 final读取：

```text id="8xub4j"
backend floor

frontend floor

service-backed floor
```

不得使用更低历史 count。

至少：

```text id="6h7pwf"
backend >= Phase 11-4 final

frontend >= Phase 11-4 final

service-backed >= Phase 11-4 final
```

---

# 120. Full Backend Regression

必须运行：

```powershell id="s1dfpe"
uv run python -m pytest -q
```

如果 repository full suite有：

```text id="yn1ua7"
known non-required skip
```

必须如实报告。

不得：

```text id="p3apne"
hide skip
```

---

# 121. Focused Phase 11 Closure Tests

必须运行：

```text id="v37dt0"
Phase 11-0 governance integrity

Phase 11-1 provenance integrity

Phase 11-2 golden benchmark integrity

Phase 11-3 reproducibility integrity

Phase 11-4 coverage integrity

Phase 11-5 closure integrity
```

---

# 122. No New Scientific Benchmark Run

Focused integrity tests可以验证：

```text id="c0omj1"
stored benchmark manifests
```

不得运行新的科学 case形成新的 authority。

---

# 123. Frontend Regression

必须：

```text id="3s7j9z"
npm --prefix apps/web test

npm --prefix apps/web run typecheck

npm --prefix apps/web run build
```

---

# 124. Browser Regression

保持：

```text id="cc4hpb"
Chromium = PASS

Firefox = PASS

WebKit = PASS

390x844 = PASS
```

这些只证明 no-regression/presentation。

---

# 125. Service-Backed Regression

必须：

```text id="12fiq0"
PostgreSQL = PASS

Redis = PASS

MinIO = PASS
```

以及 current canonical selected integration suite：

```text id="946qzh"
skipped = 0

failed = 0

errors = 0
```

---

# 126. Lock Verification

必须：

```powershell id="cmfp3r"
uv lock --check
```

并验证：

```text id="yrv8v1"
lockfile unchanged
```

---

# 127. Git Integrity

必须：

```powershell id="ybgobj"
git diff --check
```

---

# 128. Documentation Link Integrity

必须：

```text id="hf2vzw"
all Phase 11 final docs resolve

all evidence paths resolve

all hashes resolve

all cross references resolve
```

---

# 129. Secret Scan

必须：

```text id="o6bwat"
NO_SECRET_PATTERN_HITS = PASS
```

---

# 130. npm Audit

如果 configured mirror仍：

```text id="au30dj"
404_NOT_IMPLEMENTED
```

必须：

```text id="o232x4"
npm audit = UNAVAILABLE
```

不得写：

```text id="0gd1st"
PASS
clean
```

---

# 131. Overclaim Audit

必须扫描 final：

```text id="86ovxj"
README

ROADMAP

Phase 11 final docs

public claim matrix

known limitations

persistent project state
```

确保没有未经 evidence支持的：

```text id="wmq3ct"
all science validated

all formats supported

all platforms validated

numeric cross-platform verified

true bonding

phase confirmed

platform DFT

full phonon calculation

automatic phase identification
```

---

# 132. Historical Results Must Not Be Rewritten

`results.md`：

```text id="dvjgwl"
append-only
```

不得修改历史 Phase 11-0～11-4结果。

---

# 133. Implementation Commit Content

Implementation commit包含：

```text id="f7wk8t"
Phase 11-5 task admission

closure validators

final baseline package

final reference index

final fixture index

final benchmark index

final tolerance index

final variance index

reproducibility report

known limitation package

version matrix

revalidation audit

Phase 12 scientific-authority handoff

final evidence manifest

docs

persistent state
```

不得提前写：

```text id="i5pnyl"
results.md Phase 11-5 final completion
```

---

# 134. Implementation Exact-SHA CI

Implementation push 后：

必须等待：

```text id="daqkzy"
IMPLEMENTATION EXACT-SHA CI
```

这是当前 lifecycle唯一必须等待的 CI gate。

至少必须：

```text id="e53xzq"
Unit = PASS

Phase 11 closure integrity = PASS

Frontend/browser/typecheck/build = PASS

PostgreSQL/Redis/MinIO = PASS

evidence manifest = PASS

overclaim audit = PASS

security = PASS
```

---

# 135. Failed Implementation Candidate

如果 CI失败：

保留：

```text id="n53ih0"
failed SHA

failed CI run

failure reason
```

然后 fix-forward。

禁止：

```text id="zxhc2q"
force push

rewrite history

remove limitation

change coverage

change reference

change fixture

change expected value

change tolerance

change validation level

lower test floor
```

---

# 136. Closure Failure Caused by Docs/Harness

如果只是：

```text id="wz8phf"
broken docs link

incorrect hash serializer

manifest path error

coverage index typo

Windows path string in evidence tooling

closure validator bug
```

且 upstream scientific facts不变：

可以 fix-forward。

---

# 137. Closure Failure Caused by Scientific Fact

如果发现：

```text id="vvvmyr"
missing required validation

wrong scientific coverage

scientific discrepancy

reference integrity failure

release blocker
```

不得 fix in 11-5。

必须：

```text id="05kpt8"
BLOCKED / REVIEWER_REQUIRED
```

---

# 138. Completion Record

只有 implementation exact-SHA CI PASS 后：

向：

```text id="b342sa"
results.md
```

追加：

```text id="sdjqzt"
Phase 11-5 Scientific Validation Closure
+ Release Candidate Gate Result
```

并同时记录：

```text id="663fv5"
Phase 11 final closure summary
```

然后：

```text id="9a6eb9"
commit
push
```

按照当前 lifecycle：

```text id="yi01bc"
DO NOT WAIT
for completion-record CI
```

如果该 CI 自然返回明确失败：

不得故意忽略。

---

# 139. Queue Archive

Completion record push 后：

删除且只删除：

```text id="mlk29m"
Phase 11-5 TASK block
```

不得创建：

```text id="i0q9gp"
Phase 12 task
```

然后：

```text id="wfhned"
commit
push
```

不主动等待 archive CI。

---

# 140. Archive Terminology

如果 archive commit本身未等待 exact-SHA CI：

最终只能：

```text id="gz86vm"
QUEUE_ARCHIVED
```

不得：

```text id="rldcjj"
ARCHIVED_BY_VERIFIED_QUEUE_COMMIT
```

---

# 141. Final Queue State

必须：

```text id="58mfrd"
TASK_BLOCK_COUNT = 0

Phase 11-5 task absent

Phase 12 task absent

Phase 13 task absent
```

---

# 142. Final Repository State

必须：

```text id="6kjvky"
branch = master

HEAD == origin/master

worktree = clean
```

---

# 143. Required Result Markers

必须：

```text id="wwv4rw"
PHASE11_5_NEW_SCIENTIFIC_TOOLS = 0

PHASE11_5_NEW_SCIENTIFIC_ALGORITHMS = 0

PHASE11_5_NEW_SCIENTIFIC_BENCHMARKS = 0

PHASE11_5_NEW_REFERENCE_SOURCES = 0

PHASE11_5_NEW_CROSS_PLATFORM_CASES = 0

PHASE11_5_NEW_ARTIFACT_FAMILIES = 0

PHASE11_5_NEW_DATAPROFILE_VERSION = 0

PHASE11_5_NEW_ANALYSISPLAN_VERSION = 0

PHASE11_5_NEW_DATABASE_MIGRATIONS = 0

PHASE11_5_NEW_PUBLIC_API_FAMILIES = 0

PHASE11_5_NEW_DEPENDENCIES = 0

PHASE11_5_NEW_LLM_CALL_SITES = 0

PHASE11_5_REAL_LLM_CALLS = 0

PHASE11_5_EXTERNAL_REFERENCE_DOWNLOADS = 0

PHASE11_5_EXTERNAL_SCIENTIFIC_API_CALLS = 0

PHASE11_5_VALIDATION_LEVEL_CHANGES = 0

PHASE11_5_TOOL_COVERAGE_CHANGES = 0

PHASE11_5_INPUT_SUPPORT_CHANGES = 0

PHASE11_5_EXAMPLE_COVERAGE_CHANGES = 0

PHASE11_5_REFERENCE_MUTATIONS = 0

PHASE11_5_FIXTURE_MUTATIONS = 0

PHASE11_5_EXPECTED_VALUE_MUTATIONS = 0

PHASE11_5_TOLERANCE_CHANGES = 0
```

---

# 144. Baseline Markers

必须：

```text id="fg5408"
REGISTRY_BEFORE_11_5 = 62
REGISTRY_AFTER_11_5 = 62

DATAPROFILE_BEFORE_11_5 = 2.4
DATAPROFILE_AFTER_11_5 = 2.4

MIGRATION_BEFORE_11_5 =
0007_phase10m1_workspace_domain

MIGRATION_AFTER_11_5 =
0007_phase10m1_workspace_domain
```

---

# 145. Scientific Honesty Markers

必须：

```text id="jgsi3k"
SUPPORTED_EQUALS_VALIDATED = NO

PASS_INVARIANT_EQUALS_BOUNDED_NUMERIC_VALIDATION = NO

LINUX_WINDOWS_AGREEMENT_EQUALS_NUMERIC_TRUTH = NO

V4_INFERRED_FROM_PLATFORM_PASS = NO

OFFICIAL_EXAMPLE_EQUALS_VERIFIED = NO

MAPPING_EQUALS_VERIFIED = NO

FIXTURE_EXISTS_EQUALS_REFERENCE_VERIFIED = NO

SELF_REFERENCE_EQUALS_INDEPENDENT_REFERENCE = NO

BROWSER_PASS_EQUALS_SCIENTIFIC_PASS = NO

SERVICE_PASS_EQUALS_SCIENTIFIC_PASS = NO

SCREENSHOT_NUMERIC_SCIENTIFIC_AUTHORITY = NONE

LLM_NUMERIC_SCIENTIFIC_AUTHORITY = NONE

PASS_DRIVEN_TOLERANCE_CHANGE = PROHIBITED
```

---

# 146. Phase Completion Markers

成功必须：

```text id="5a6frl"
PHASE_11 =
COMPLETE /
REFERENCE_VALIDATED_WITH_EXPLICIT_LIMITS

SCIENTIFIC_VALIDATION_BASELINE =
SEALED

SCIENTIFIC_RELEASE_CANDIDATE_GATE =
PASS

FINAL_PRODUCT_RELEASE_READY =
NO

INITIAL_RELEASE_COMPLETE =
NO
```

---

# 147. Phase 12 Markers

必须：

```text id="j6cva8"
PHASE_12 =
REVIEWER_GATE /
AWAITING REVIEWER PROMPT

PHASE_12_EXECUTABLE_TASK_CREATED = NO
```

---

# 148. Phase 13 Markers

必须：

```text id="49w2qw"
PHASE_13 =
ROADMAP_APPROVED /
NOT_QUEUED /
NOT_EXECUTABLE

PHASE_13_EXECUTABLE_TASK_CREATED = NO
```

---

# 149. Future Markers

必须：

```text id="twaqax"
FUTURE_SCOPE =
DOCUMENTED /
NOT_QUEUED

PHASE14_CREATED = NO
```

---

# 150. Required results.md Structure

至少：

# Phase 11-5 Scientific Validation Closure + Release Candidate Gate Result

1. Conclusion
2. Phase 11-4 Baseline
3. Entry Gate
4. Phase 11-4 Lifecycle Verification
5. Phase 11-5 Closure Handoff Integrity
6. Production Behavior Changes
7. Phase 11 Authority Chain
8. Phase 11-0 Governance Closure
9. Phase 11-1 Reference/Fixture Closure
10. Phase 11-2 Golden Benchmark Closure
11. Phase 11-3 Reproducibility Closure
12. Phase 11-4 Honest Coverage Closure
13. Registry / DataProfile / Migration Baseline
14. Final Tool Validation-Level Distribution
15. Final Tool Coverage Distribution
16. Final Input Support Distribution
17. Final Official/Example Coverage Distribution
18. Final Reference Registry
19. Final Fixture Registry
20. Final Golden Benchmark Registry
21. Final Tolerance Registry
22. Final Variance Matrix
23. Final Scientific Validation Version Matrix
24. Phase 11-2 Benchmark Summary
25. PASS_INVARIANT Summary
26. Reference-Limited N/A Summary
27. Scientific Failure Summary
28. Phase 11-3 Linux Summary
29. Phase 11-3 Windows Summary
30. Numeric Cross-Platform Limitation
31. V4 Status
32. Browser Validation Boundary
33. Service Validation Boundary
34. Screenshot Authority Boundary
35. Scientific Reproducibility Report
36. Determinism
37. Identity Validation
38. Unit Validation
39. Locked Environment
40. Known Scientific Limitations
41. Reference Limitations
42. Input Limitations
43. Platform Limitations
44. Algorithm-Semantic Limitations
45. Public Scientific Claims
46. Required Qualifiers
47. Prohibited Claims
48. Remaining Gap Matrix
49. P0/P1/P2 Counts
50. Release-Blocking Gap Count
51. Accepted Explicit Limitations
52. Revalidation Triggers
53. Scientific Baseline ID
54. Scientific Baseline Hash
55. Final Evidence Manifest
56. Evidence Integrity
57. Phase 12 Scientific Authority Handoff
58. Phase 12 Reviewer Gate
59. Phase 13 State
60. Future Scope State
61. Not Planned State
62. Initial Release State
63. Security
64. LLM / DeepSeek
65. Database / API / Dependency Freeze
66. Registry / DataProfile Freeze
67. Tests
68. Focused Phase 11 Closure Tests
69. Browser Regression
70. Service-Backed Regression
71. npm Audit
72. Documentation Link Integrity
73. Overclaim Audit
74. Secret Scan
75. Files Changed
76. Acceptance Registry
77. Implementation Commit
78. Implementation CI
79. Failed Implementation Candidates
80. Completion Record
81. Queue Archive
82. Queue State
83. Final Repository State
84. Phase 11 Final Decision
85. Phase 12 Next Gate

---

# 151. Entry Gate Commands

进入 repository：

```powershell id="q9w5q8"
cd "E:\1project\Material Data Intelligence"
```

运行：

```powershell id="iz0km3"
pwd

git remote -v

git branch --show-current

git status --short

git rev-parse HEAD

git rev-parse origin/master

git log --oneline --decorate -200

git diff --stat

git diff --check
```

---

# 152. Phase 11 Ancestry Audit

动态取得各 Phase authoritative SHAs 后：

必须验证：

```text id="16klkc"
11-0 implementation/archive ancestry

11-1 implementation/archive ancestry

11-2 implementation/archive ancestry

11-3 implementation/archive ancestry

11-4 implementation/archive ancestry
```

不得只看最新 commit message。

---

# 153. First Required Output

执行开始后首先输出：

```text id="tg0jsm"
Phase 11-5 Entry Gate
+ Phase 11-4 Honest Coverage Closure Handoff
+ Phase 11 Scientific Validation Final Closure Audit
```

至少确认：

1. Phase 11-4 implementation SHA；
2. Phase 11-4 implementation CI；
3. Phase 11-4 completion SHA；
4. Phase 11-4 queue archive SHA；
5. HEAD / origin / branch / worktree；
6. Registry=62；
7. DataProfile=2.4；
8. migration=0007；
9. TASK_BLOCK_COUNT=0；
10. Phase 12 task absent；
11. Phase 13 task absent；
12. Phase11_5ClosureInputManifest exists；
13. Tool Coverage Matrix hash resolves；
14. Tool rows=62；
15. Input Matrix hash resolves；
16. Example Matrix hash resolves；
17. Reference Registry hash resolves；
18. Fixture Registry hash resolves；
19. Golden Benchmark Suite hash resolves；
20. Tolerance Registry hash resolves；
21. Variance Matrix resolves；
22. Known Limitations hash resolves；
23. Remaining Gap Matrix hash resolves；
24. validation-level distribution resolves；
25. Phase 11-2 final benchmark summary；
26. Phase 11-3 final reproducibility summary；
27. V4 actual count；
28. P0 count；
29. release-blocking gap count；
30. accepted limitation count；
31. revalidation trigger policy；
32. public claim matrix；
33. Future Scope guard；
34. Not Planned guard；
35. no production scientific change required；
36. no new reference/benchmark required。

只有全部满足才输出：

```text id="sdxxgz"
PHASE_11_5_ENTRY_GATE = PASS

PHASE_11_4_REVIEWER_DEPENDENCY = VERIFIED

PHASE_11_5_QUEUE_ADMISSION = AUTHORIZED

PHASE_11_5_NEW_SCIENTIFIC_VALIDATION_AUTHORITY = NONE

PHASE_11_5_CLOSURE_AUTHORITY = AUTHORIZED

PHASE_11_5_RELEASE_BLOCKER_AUDIT = AUTHORIZED

PHASE_11_5_PHASE12_HANDOFF = AUTHORIZED

PHASE_11_5_READINESS =
READY_FOR_SCIENTIFIC_VALIDATION_CLOSURE
```

---

# 154. Entry BLOCKED — Release Blockers

如果：

```text id="nme5mp"
RELEASE_BLOCKING_GAP_COUNT > 0
```

必须立即：

```text id="ca5mae"
PHASE_11_5_ENTRY_GATE = BLOCKED

Phase 11 =
IN_PROGRESS /
RELEASE_BLOCKERS_REMAIN
```

不得 admit 11-5 closure task。

---

# 155. Entry BLOCKED — Phase 11-4 Incomplete

如果 coverage：

```text id="k0av3j"
Tool unclassified > 0

Input unclassified > 0

Example unclassified > 0
```

不能进入 11-5。

---

# 156. Entry BLOCKED — Scientific Evidence Inconsistency

如果：

```text id="4r0fku"
golden suite hash mismatch

reference hash mismatch

fixture hash mismatch

tolerance hash mismatch

variance hash mismatch
```

必须 BLOCKED。

---

# 157. Entry BLOCKED — Hidden N/A

如果 11-2 final存在 reference-limited N/A：

但 11-4 known limitations未体现：

必须 BLOCKED。

---

# 158. Entry BLOCKED — V4 Fabrication

如果 11-3：

```text id="9z0ago"
V4 promotions = 0
```

但 11-4 final：

```text id="yz3tnk"
V4 > 0
```

必须：

```text id="3vjp8k"
BLOCKED /
VALIDATION_LEVEL_GOVERNANCE_VIOLATION
```

---

# 159. Entry BLOCKED — Numeric Overclaim

如果 final coverage或public claims声称：

```text id="up34r9"
bounded numeric reference validation
```

而只有 invariant evidence：

必须 BLOCKED。

---

# 160. Entry BLOCKED — Input Overclaim

如果 unsupported/mapping-only input被 final claims写为：

```text id="6t5kwb"
direct supported
```

必须 BLOCKED。

---

# 161. Entry BLOCKED — Future Scope Leakage

如果 Future Scope science进入 Initial Release claim：

必须 BLOCKED。

---

# 162. Closure Execution Sequence

严格执行：

```text id="t5hn52"
verify Phase 11-4 lifecycle

→ verify 11-5 handoff hashes

→ verify release blocker count = 0

→ admit exactly one Phase 11-5 task

→ snapshot all Phase 11 final authorities

→ reconcile Phase 11-0 governance

→ reconcile Phase 11-1 provenance

→ reconcile Phase 11-2 golden suite

→ reconcile Phase 11-3 reproducibility

→ reconcile Phase 11-4 honest coverage

→ verify all accepted limitations

→ verify all public claims

→ verify all revalidation triggers

→ generate final reference index

→ generate final fixture index

→ generate final benchmark index

→ generate final tolerance index

→ generate final variance index

→ generate final version matrix

→ generate final reproducibility report

→ generate final known scientific limitations

→ generate Phase 12 scientific authority handoff

→ generate final evidence manifest

→ generate scientific validation baseline ID/hash

→ run closure consistency validators

→ run overclaim audit

→ run no-mutation audit

→ run full regression

→ run browser regression

→ run service-backed regression

→ run security/secret/docs checks

→ create implementation commit

→ push

→ wait for implementation exact-SHA CI

→ if PASS:
   append Phase 11-5 + Phase 11 closure result

→ commit/push completion record directly

→ remove only Phase 11-5 task

→ commit/push queue archive directly

→ verify final repository state

→ stop
```

---

# 163. PASS Gate

只有全部满足：

```text id="7a8iq0"
Phase 11-4 PASS

Phase 11-4 queue archived

Phase 11-4 implementation CI PASS


HEAD == origin/master at entry

worktree clean


Registry = 62

DataProfile = 2.4

migration = 0007


Phase 11-0 governance intact

Phase 11-1 provenance intact

Phase 11-2 benchmark evidence intact

Phase 11-3 reproducibility evidence intact

Phase 11-4 coverage evidence intact


Tool coverage rows = 62

Tool unclassified = 0

Input unclassified = 0

Example unclassified = 0


all final hashes resolve

all final evidence refs resolve

all release-critical identity refs resolve


P0 = 0

release-blocking gaps = 0


all remaining gaps are
accepted explicit limitations
or non-release future/non-scope items


reference-limited benchmark cases
remain visible and honest


no numeric reference overclaim

no cross-platform numeric overclaim

no V4 fabrication

no input-support overclaim

no Future Scope leakage


final reference registry sealed

final fixture registry sealed

final benchmark registry sealed

final tolerance registry sealed

final variance matrix sealed

final version matrix sealed

final reproducibility report complete

final known limitation package complete

final public claim package complete

final revalidation trigger package complete

Phase 12 authority handoff complete


new science = 0

new benchmark = 0

new reference = 0

new Tool = 0

new algorithm = 0

new Artifact family = 0

validation-level changes = 0

coverage changes = 0

input-support changes = 0

reference mutation = 0

fixture mutation = 0

expected-value mutation = 0

tolerance changes = 0

Registry changes = 0

DataProfile changes = 0

migration changes = 0

public API changes = 0

dependency changes = 0

lockfile changes = 0

real LLM calls = 0


backend >= Phase 11-4 final floor

frontend >= Phase 11-4 final floor

service-backed >= Phase 11-4 final floor

required service skipped = 0

required service failed = 0

required service errors = 0

Chromium PASS

Firefox PASS

WebKit PASS

390x844 PASS

typecheck PASS

build PASS

lock PASS

docs links PASS

overclaim audit PASS

no-mutation audit PASS

evidence integrity PASS

security PASS

secret scan PASS


P11V5 acceptance = 12/12


implementation exact-SHA CI PASS

completion record committed/pushed

queue archive committed/pushed


final TASK_BLOCK_COUNT = 0

Phase 12 task absent

Phase 13 task absent

HEAD == origin/master

worktree clean
```

才允许：

```text id="3o4d5z"
Phase 11-5 = PASS

Phase 11 =
COMPLETE /
REFERENCE_VALIDATED_WITH_EXPLICIT_LIMITS
```

---

# 164. BLOCKED — Release-Blocking Gap

如果：

```text id="8ynjjq"
releaseBlockingGapCount > 0
```

必须：

```text id="7ivhip"
Phase 11-5 =
BLOCKED /
SCIENTIFIC_VALIDATION_RELEASE_BLOCKERS_REMAIN
```

不能进入 Phase 12。

---

# 165. BLOCKED — New Scientific Validation Required

如果 closure发现要满足现有 Initial Release claim必须：

```text id="3q9d0g"
obtain new reference

create new fixture

run new benchmark

add numeric truth

change tolerance
```

必须：

```text id="r7ao9a"
BLOCKED /
ADDITIONAL_SCIENTIFIC_VALIDATION_REVIEW_REQUIRED
```

不得让 11-5补做。

---

# 166. BLOCKED — Scientific Defect

如果发现：

```text id="1mf92f"
current production science contradicts
sealed valid reference
```

必须 BLOCKED。

11-5无修复权限。

---

# 167. BLOCKED — Coverage Integrity

如果：

```text id="5bt2fc"
Tool coverage

Input support

Official/example coverage
```

任一 final matrix无法由 evidence deterministic重建：

必须 BLOCKED。

---

# 168. BLOCKED — Baseline Hash Instability

同一个 clean repository：

连续两次生成：

```text id="stebp4"
scientificValidationBaselineHash
```

不同：

必须：

```text id="mmgpor"
FAIL_DETERMINISM
```

不得封板。

---

# 169. Non-Blockers

以下可以存在：

```text id="w9tw6q"
V4 = 0

reference-limited numeric cases remain

some Tools remain V1/V2

some examples remain MAPPING_ONLY

some examples remain EXTRACTION_REQUIRED

phonon direct upload remains MAPPING_ONLY

XLSX remains unsupported

Parquet remains unsupported

LAMMPS trajectory remains unsupported

macOS remains not current release target

Future Scope remains unimplemented
```

只要：

```text id="n0qvnj"
honestly disclosed

non-release-blocking

consistent with Phase 11 governance
```

---

# 170. Required Final Scientific Statement

Phase 11 PASS 后，推荐正式措辞：

```text id="e7adv6"
The Initial Release scientific capability set has been
validation-governed, provenance-indexed, benchmarked
against the sealed available references, replayed across
the approved locked Linux/Windows environments where
admitted, and honestly classified with explicit scientific,
input, reference, and platform limitations.
```

---

# 171. Prohibited Final Statement

不得写：

```text id="hckp0c"
All scientific capabilities are independently numerically verified.

All Tools are V4.

All platforms produce identical science.

Every supported material format is scientifically validated.

The product is ready for final release.

Initial Release is complete.
```

---

# 172. Final Phase 11 State

最终只能：

```text id="f4chvp"
Phase 11:
COMPLETE /
REFERENCE_VALIDATED_WITH_EXPLICIT_LIMITS

SCIENTIFIC_VALIDATION_BASELINE:
SEALED

SCIENTIFIC_VALIDATION_RELEASE_CANDIDATE:
PASS
```

---

# 173. Final Product State

仍然：

```text id="p2qxdi"
FINAL_PRODUCT_RELEASE_READY = NO

INITIAL_RELEASE_COMPLETE = NO
```

---

# 174. Next Phase State

最终：

```text id="pqa5mq"
Phase 12:
REVIEWER_GATE /
AWAITING REVIEWER PROMPT

TASK_BLOCK_COUNT = 0

PHASE_12_EXECUTABLE_TASK_CREATED = NO
```

---

# 175. Stop Rule

完成后立即停止。

不得：

```text id="y43isy"
create Phase 12 task

execute Phase 12-0

redesign UI

change Design System

modify Planner UX

modify Workspace UX

modify Viewer UX

start Phase 13

perform final release
```

返回：

```text id="k7ri4e"
complete Phase 11-5 result

+
complete Phase 11 final closure result

+
final baseline hash

+
final limitation summary

+
Phase 12 reviewer-gate status
```

然后等待 reviewer。




---END---
