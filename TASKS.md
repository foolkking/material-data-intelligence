---TASK---
 状态：已完成

# Phase 11-4 Reviewer Prompt

# Honest Tool / Input / Official-Example Coverage Matrix

你现在执行：

# Phase 11-4：Honest Tool / Input / Official-Example Coverage Matrix

中文：

# 工具 / 输入格式 / 官方示例诚实覆盖矩阵封板

本阶段属于：

```text
Phase 11:
Scientific Validation,
Reference Provenance,
Reproducibility
& Honest Coverage
```

Phase 11-4 的任务不是继续增加科学验证。

本阶段的唯一核心任务是：

```text
读取 Phase 11-0 ～ 11-3 已经形成的全部事实

→ 不再生成新的 scientific truth

→ 不再扩展 reference

→ 不再追加 golden benchmark scope

→ 不再改变 validation level

→ 不再改变 input support

→ 不再改变 platform support

→ 把现有证据转换成一套
   deterministic / auditable / conservative
   Honest Coverage

→ 分别形成：
   Tool Coverage Matrix
   Input Support Matrix
   Official / Candidate Example Coverage Matrix

→ 明确每项“真正证明了什么”
   和“没有证明什么”

→ 明确每项限制

→ 明确 Initial Release 可以公开声称的范围

→ 生成 Phase 11-5 closure handoff

→ stop
```

---

# 0. Fundamental Rule

Phase 11-4 必须遵守：

```text
COVERAGE_IS_A_CLASSIFICATION_OF_EXISTING_EVIDENCE
```

而不是：

```text
COVERAGE_IS_NEW_SCIENTIFIC_EVIDENCE
```

因此：

```text
PHASE11_4_NEW_SCIENTIFIC_VALIDATION = 0

PHASE11_4_NEW_REFERENCE_VALIDATION = 0

PHASE11_4_NEW_NUMERIC_BENCHMARKS = 0

PHASE11_4_NEW_CROSS_PLATFORM_BENCHMARKS = 0
```

本阶段只允许：

```text
READ
RECONCILE
CLASSIFY
DISCLOSE
DOCUMENT
VALIDATE CONSISTENCY
```

---

# 1. Reviewer Authorization

正式条件授权：

```text
PHASE_11_4_PROMPT_PREAUTHORIZED = YES

AUTHORIZED_PHASE = Phase 11-4

MAX_PHASES_EXECUTED = 1
```

只有 Entry Gate PASS 后才能 admission。

不得创建、排队或执行：

```text
Phase 11-5

Phase 12

Phase 13
```

---

# 2. Mandatory Phase 11-3 Dependency

执行器不能仅根据本 Prompt 假设 11-3 已完成。

必须从真实 repository 读取：

```text
git history

results.md

TASKS.md

persistent/

docs/phase11/

docs/phase11/evidence/
```

并动态确认：

```text
PHASE_11_3_IMPLEMENTATION_SHA

PHASE_11_3_IMPLEMENTATION_CI_RUN

PHASE_11_3_IMPLEMENTATION_CI_RESULT

PHASE_11_3_COMPLETION_SHA

PHASE_11_3_QUEUE_ARCHIVE_SHA
```

必须满足：

```text
Phase 11-3 = PASS

Phase 11-3 queue = ARCHIVED

implementation exact-SHA CI = PASS
```

如果不存在：

```text
PHASE_11_4_ENTRY_GATE = BLOCKED

reason =
PHASE_11_3_NOT_COMPLETED_OR_NOT_ARCHIVED
```

然后停止。

---

# 3. Current Lifecycle Policy

继续使用当前项目生命周期：

```text
Implementation commit
→ push
→ WAIT FOR implementation exact-SHA CI

if PASS:

Completion record
→ commit
→ push directly

Queue archive
→ commit
→ push directly
```

不要求主动等待：

```text
completion-record CI
queue-archive CI
```

因此若没有 exact-SHA CI 事实：

最终术语只能使用：

```text
COMPLETION_RECORDED
QUEUE_ARCHIVED
```

不得虚构：

```text
VERIFIED_COMPLETION
VERIFIED_QUEUE_ARCHIVE
ARCHIVED_BY_VERIFIED_QUEUE_COMMIT
```

---

# 4. Dynamic Entry Baseline

Phase 11-4 entry authority：

```text
PHASE_11_3_QUEUE_ARCHIVE_SHA
```

必须验证：

```text
branch = master

HEAD == origin/master

worktree = clean

11-3 archive is ancestor of HEAD
```

如果 current HEAD 包含之后的 documentation-only commits：

可以继续，但必须证明：

```text
NO_UNREVIEWED_PRODUCTION_CHANGE_AFTER_11_3
```

否则：

```text
BLOCKED / REVIEWER_REQUIRED
```

---

# 5. Platform Baseline Must Remain

必须：

```text
Registry = 62

DataProfile = 2.4

migration head =
0007_phase10m1_workspace_domain
```

并保持：

```text
AnalysisIntent = 1.0

EligibilityResolution = 1.0

AnalysisPlan = 0.1 / 0.2

ToolPlannerMetadata = existing versions unchanged

ScientificWorkspace = existing contract unchanged
```

---

# 6. Phase 11-0 Governance Is Authority

Phase 11-4 不允许重新定义 coverage taxonomy。

必须读取 current canonical：

```text
docs/phase11/phase11_validation_governance.md

docs/phase11/phase11_validation_level_policy.md

docs/phase11/phase11_tool_validation_matrix.md

docs/phase11/phase11_input_support_matrix.md

docs/phase11/phase11_reference_provenance_policy.md

docs/phase11/phase11_reference_evidence_inventory.md

docs/phase11/phase11_gap_matrix.md

docs/phase11/phase11_tolerance_registry.md

docs/phase11/phase11_variance_and_reproducibility_policy.md

docs/phase11/phase11_execution_lock.md

docs/phase11/phase11_execution_manifest.md
```

特别：

```text
Phase 11-0 exact coverage criteria
```

拥有 authority。

如果本 Prompt 的概括与 repository 中 exact criterion 有差异：

```text
PHASE_11_0_CANONICAL_CRITERION_WINS
```

不得修改 criterion 来获得更好的 coverage。

---

# 7. Frozen Coverage Verdicts

唯一允许的 final coverage verdict：

```text
DIRECT_VERIFIED

OFFICIAL_DERIVED_VERIFIED

REFERENCE_VERIFIED

MAPPING_ONLY

EXTRACTION_REQUIRED

FUTURE_SCOPE

UNSUPPORTED
```

不得新增：

```text
MOSTLY_VERIFIED
SEMI_VERIFIED
PROBABLY_SUPPORTED
STRONGLY_SUPPORTED
PARTIAL_PASS
GOOD_ENOUGH
BETA_VERIFIED
LIKELY_CORRECT
```

---

# 8. Coverage Verdict Is Not Validation Level

必须保持两个轴独立：

```text
Validation Level:
V0 / V1 / V2 / V3 / V4
```

和：

```text
Coverage Verdict:
DIRECT_VERIFIED
OFFICIAL_DERIVED_VERIFIED
REFERENCE_VERIFIED
...
```

禁止：

```text
V2 automatically means DIRECT_VERIFIED

V3 automatically means REFERENCE_VERIFIED

V4 automatically means DIRECT_VERIFIED
```

Coverage verdict必须逐项按照：

```text
Phase 11-0 exact evidence criteria
```

判定。

---

# 9. Coverage Verdict Is Not Support Verdict

Input support：

```text
DIRECT_SUPPORTED

SUPPORTED_WITH_LIMITS

MAPPING_ONLY

PARSE_ONLY

UNSUPPORTED

FUTURE_SCOPE
```

与 scientific coverage：

```text
DIRECT_VERIFIED
...
```

是不同轴。

禁止：

```text
DIRECT_SUPPORTED
→ DIRECT_VERIFIED
```

因为：

```text
can parse/run
!=
scientifically independently validated
```

---

# 10. Phase 11-2 Frozen Scientific Facts

必须读取并继承真实 11-2 result。

当前已知事实必须保持：

```text
Golden benchmark records = 12

PASS_INVARIANT = 8

NOT_APPLICABLE = 4

scientific failures = 0

blocked = 0

aggregate =
PASS_WITH_NONBLOCKING_LIMITATIONS
```

四个：

```text
NOT_APPLICABLE
```

的核心限制：

```text
retained reference does not contain
bounded expected numeric value
```

因此：

```text
NUMERIC_REFERENCE_VALIDATION
=
NOT_ESTABLISHED
```

不得在 11-4重解释。

---

# 11. Eight PASS_INVARIANT Cases

8 条 `PASS_INVARIANT` 只能证明：

```text
sealed identity
+
unit
+
invariant
+
registered-contract replay
```

实际证明的内容以 11-2 benchmark result为准。

禁止自动升级为：

```text
independent bounded numeric validation
```

除非对应 row 已经具有 Phase 11-0 criterion要求的 exact reference evidence。

---

# 12. Four NOT_APPLICABLE Cases

这 4 条必须保留：

```text
reference-limited
```

事实。

禁止：

```text
NOT_APPLICABLE
→ PASS

NOT_APPLICABLE
→ DIRECT_VERIFIED

NOT_APPLICABLE
→ OFFICIAL_DERIVED_VERIFIED

NOT_APPLICABLE
→ REFERENCE_VERIFIED
```

除非 exact Phase 11-0 coverage criterion 本来就不要求此 numeric dimension，并且其他 required evidence 全部成立。

这种情况必须逐 row 说明：

```text
why numeric N/A does not block that exact verdict
```

不能 bulk promote。

---

# 13. Phase 11-3 Frozen Facts

必须保持：

```text
11-3 scientific cases = 8

Linux = 8/8 sealed invariant reference PASS

Windows = 8/8 sealed invariant reference PASS
```

以及：

```text
numeric cross-platform comparison =
NOT_APPLICABLE
```

因为 input handoff：

```text
contained no sealed numeric expected values
```

---

# 14. V4 Freeze

必须保持：

```text
PHASE11_3_V4_PROMOTIONS = 0
```

所以 11-4：

```text
PHASE11_4_V4_PROMOTIONS = 0
```

不得因为：

```text
Linux PASS
+
Windows PASS
```

重新解释成 V4。

---

# 15. Cross-Platform Coverage Honesty

可以说：

```text
cross-platform invariant reproducibility
verified for the eight admitted sealed cases
```

不能说：

```text
cross-platform numeric reproducibility verified
```

不能说：

```text
all 62 Tools cross-platform verified
```

不能说：

```text
Windows parity proven for all science
```

---

# 16. Browser Honesty

继续：

```text
Chromium
Firefox
WebKit
390x844
```

只证明：

```text
presentation

interaction

state

accessibility where tested

no frontend recomputation
```

不能证明：

```text
numeric scientific correctness
```

---

# 17. Service Honesty

PostgreSQL / Redis / MinIO只证明：

```text
persistence

queue/runtime integration

Artifact storage

identity

lineage

scope

checksum
```

不得：

```text
SERVICE_PASS
→ REFERENCE_VERIFIED
```

---

# 18. Screenshot Honesty

必须：

```text
SCREENSHOT_NUMERIC_SCIENTIFIC_AUTHORITY = NONE
```

不能因为 scientific plot：

```text
looks right
```

就提升 coverage。

---

# 19. Self-Reference Honesty

继续：

```text
SELF_REFERENCE
!=
INDEPENDENT_REFERENCE
```

Same-library output可作为：

```text
regression
serialization
determinism
```

但不能因为重复执行而变 independent。

---

# 20. Fixture Honesty

继续：

```text
FIXTURE_EXISTS
!=
REFERENCE_VERIFIED
```

Fixture：

```text
has provenance
has hash
has version
```

也不意味着：

```text
Tool output agrees with independent truth
```

---

# 21. Official Example Honesty

必须：

```text
OFFICIAL_EXAMPLE_EXISTS
!=
REFERENCE_VERIFIED
```

以及：

```text
OFFICIAL_EXAMPLE_MAPPING
!=
PLATFORM_EXECUTION
```

---

# 22. Primary Deliverable A

必须建立最终：

# Tool Coverage Matrix

exact rows：

```text
62
```

来源：

```text
live Registry source of truth
```

不得使用 stale documentation list。

---

# 23. Tool Matrix Row Identity

每 row 至少：

```text
toolId

toolVersion

domain

roleClass

availability

scientificAuthority

inputContracts

outputArtifacts

validationLevel

referenceTypes

referenceIndependence

11_2BenchmarkIds

11_2BenchmarkVerdicts

11_3ReproducibilityCaseIds

11_3VarianceVerdicts

browserEvidence

serviceEvidence

knownLimitations

coverageVerdict

coverageReason

whatIsVerified

whatIsNotVerified

inputSupportDependencies

officialExampleDependencies

evidenceRefs

revalidationTriggers
```

---

# 24. Tool Matrix Completeness

要求：

```text
TOOL_MATRIX_EXPECTED = 62

TOOL_MATRIX_ROWS = 62

TOOL_MATRIX_MISSING = 0

TOOL_MATRIX_EXTRA = 0

TOOL_MATRIX_DUPLICATE = 0

TOOL_MATRIX_UNCLASSIFIED = 0
```

---

# 25. Tool Coverage Must Be Tool-Version Specific

禁止：

```text
tool family verified
```

而不带 version。

必须：

```text
toolId@version
```

为 coverage identity。

如果未来 Tool version变化：

旧 verdict不自动继承。

---

# 26. Product / Presentation Tools

对于：

```text
PRESENTATION_ONLY

PRODUCT_COMPOSITION

METADATA_OR_UTILITY
```

不能因为没有 numeric reference就判：

```text
UNSUPPORTED
```

它们必须使用 Phase 11-0 对该 role 的 exact validation requirement：

通常可能包括：

```text
contract

source identity

no recomputation

runtime/persistence

deterministic projection

browser

accessibility

security
```

具体仍以 canonical policy 为 authority。

---

# 27. Scientific Numeric Tools

对于有 numeric scientific authority 的 Tool：

coverage reason 必须明确：

```text
reference strength

numeric/invariant validation type

unit validation

tolerance availability

cross-platform status

limitations
```

不得写：

```text
tested
```

这种无信息描述。

---

# 28. Scientific Geometry Tools

必须区分：

```text
geometry invariant/reference

numeric geometry values

identity

periodicity

algorithm-specific semantics
```

特别：

```text
CrystalNN
!=
VoronoiNN
```

二者 mutual disagreement 不等 failure。

---

# 29. Scientific Classification Tools

必须明确 classification 是否验证：

```text
exact categorical semantics

threshold semantics

negative/boundary cases
```

以及是否有：

```text
bounded numeric reference
```

不能把 classification PASS 扩大成整个 numeric family PASS。

---

# 30. Dataset / ML Coverage

必须保持历史科学边界：

```text
descriptive statistics
!=
scientific causal inference

ML evaluation
!=
model training validity

PCA/KMeans
!=
material family discovery truth

outlier candidate
!=
invalid material
```

---

# 31. Coordination Coverage

所有 coverage文案必须继续：

```text
algorithm-derived local coordination
```

禁止：

```text
true bonding coordination
```

---

# 32. Local Environment Coverage

必须：

```text
algorithm/geometry-derived
```

禁止自动扩展：

```text
oxidation state

true bonding

chemical environment certainty
```

---

# 33. XRD Coverage

必须：

```text
peak correspondence under configured tolerance
```

禁止：

```text
phase confirmation

Rietveld refinement

phase identification

phase fraction
```

---

# 34. RDF / MSD / Diffusion Coverage

必须分别描述。

尤其：

```text
RDF peak
!=
bond proof
```

```text
MSD
!=
diffusion by itself
```

```text
diffusion =
estimated over selected fit window
```

禁止 unconditional bulk diffusivity claim。

---

# 35. Electronic Coverage

必须明确：

```text
supplied/imported electronic outputs
```

不是：

```text
platform DFT

platform GW

ground-state calculation
```

Band/DOS coverage 不得扩大到：

```text
Fermi surface

fatbands

projected bands
```

---

# 36. Phonon Coverage

必须保留：

```text
supplied/imported phonon information
```

与：

```text
platform phonon calculation
```

之间边界。

不能通过 viewer/runtime coverage宣传 phonon first-principles computation。

---

# 37. Volumetric Coverage

不得扩展到：

```text
Bader

charge topology

advanced ELF topology
```

如果现有 Tool只负责：

```text
field/slice/isosurface/volume
```

coverage必须按真实 surface 写。

---

# 38. Primary Deliverable B

建立最终：

# Input Support Matrix

必须从现有 11-0/11-1 matrix继承。

不得重新推测 library theoretical capability。

---

# 39. Current Frozen Input Baseline

除非 repository在 11-2/11-3 中有明确 reviewer-approved support change——原则上不应有——必须保持：

```text
DIRECT_SUPPORTED:

CSV
CIF
POSCAR
```

```text
SUPPORTED_WITH_LIMITS:

canonical JSON
XYZ / EXTXYZ
volumetric
ZIP
supplied electronic JSON
```

```text
MAPPING_ONLY:

phonon direct upload
```

```text
UNSUPPORTED:

XLSX
Parquet
LAMMPS trajectory
```

如果 current exact matrix有 additional rows：

全部保留。

---

# 40. Input Matrix Row Fields

至少：

```text
inputFamily

extensions

MIME/sniffing

parser

parser authority/version

resourceContract

DataProfile support

identity semantics

unit semantics

Planner/Eligibility support

eligible Tools

runtime support

Workspace support

renderer support

limits/caps

negative cases

supportVerdict

scientificCoverageRelation

knownLimitations

evidenceRefs
```

---

# 41. Parser ≠ Support

禁止：

```text
parser exists
→ DIRECT_SUPPORTED
```

必须具有真实：

```text
upload/sniffing
→ parser
→ Resource
→ Profile
→ Eligibility
→ Runtime
```

platform path。

---

# 42. Library Capability ≠ Product Capability

例如：

```text
pymatgen theoretically can read format X
```

不能证明：

```text
platform supports format X
```

这是硬规则。

---

# 43. Renderer ≠ Input Support

存在 renderer：

```text
does not prove direct upload
```

例如某 phonon viewer可能消费：

```text
prepared Resource / Artifact
```

但 direct phonon upload仍可能是：

```text
MAPPING_ONLY
```

---

# 44. ZIP Coverage

ZIP必须保留：

```text
SUPPORTED_WITH_LIMITS
```

并明确：

```text
container semantics

safe extraction

recognized inner content

aggregate support restrictions
```

不得描述成：

```text
arbitrary archive supported
```

---

# 45. Canonical JSON Coverage

必须写：

```text
canonical / recognized schema JSON
```

不能写：

```text
any JSON
```

---

# 46. XYZ / EXTXYZ

必须明确：

```text
supported within current parser/resource semantics
```

而非所有 dialect/features。

---

# 47. Supplied Electronic JSON

必须写：

```text
supplied electronic JSON
```

不能简化成：

```text
electronic structure file support
```

以免暗示所有 DFT output格式都支持。

---

# 48. Unsupported Formats

对：

```text
XLSX
Parquet
LAMMPS trajectory
```

不得因为：

```text
Python/pandas/pymatgen could theoretically parse
```

升级。

如果以后支持：

属于新的 implementation/reviewer scope。

---

# 49. Primary Deliverable C

建立最终：

# Official / Candidate Example Coverage Matrix

必须基于现有 retained official/example inventory。

当前 11-1实际 retained example inventory：

```text
55 records
```

执行前动态读取 exact count。

如果 repository current count不是 55：

使用真实 current canonical count，并说明变化来源。

---

# 50. Example Matrix Row Fields

至少：

```text
exampleId

sourceProject

sourceVersion

sourceIdentity

sourceStatus

licenseDisposition

scientificFamily

mappedPlatformToolIds

mappedInputFamily

platformExecutablePath

fixtureId

referenceId

referenceType

referenceIndependence

11_2BenchmarkId

11_2Verdict

11_3ReproducibilityStatus

coverageVerdict

coverageReason

currentRelevance

supersededBy

whatIsVerified

whatIsNotVerified

evidenceRefs
```

---

# 51. Historical Examples Remain Historical

如果 example：

```text
SUPERSEDED
```

不能因为历史上成功：

```text
become current product coverage
```

必须保留历史事实。

---

# 52. MAPPING_ONLY

`MAPPING_ONLY` 必须严格表示：

```text
conceptual/static mapping exists
```

但未满足 exact Phase 11-0 direct/reference verification criterion。

禁止把：

```text
official example looks similar
```

当 verification。

---

# 53. EXTRACTION_REQUIRED

只有 current canonical criterion认为：

```text
scientifically relevant source exists
but required bounded/reference fixture
has not been safely extracted/prepared
```

才可使用。

如果 11-1已经完成 exact extraction：

必须根据真实 evidence重新分类。

但不能直接跳到 verified，除非 11-2所需 criterion也通过。

---

# 54. FUTURE_SCOPE

Future example/capability：

必须：

```text
FUTURE_SCOPE
```

不得因为 official project展示该能力而：

```text
pretend platform supports it
```

---

# 55. UNSUPPORTED

只有当前 platform path明确不支持：

使用：

```text
UNSUPPORTED
```

不要把：

```text
not independently reference-validated
```

误标成 unsupported。

---

# 56. Coverage Promotion Must Be Evidence-Derived

允许 verdict变化：

仅当：

```text
11-1 provenance
+
11-2 benchmark
+
11-3 reproducibility
```

实际新增的证据满足 11-0已封板 criterion。

每个改变必须保存：

```text
previousVerdict

newVerdict

evidenceThatChangedVerdict

criterionSatisfied
```

---

# 57. No Coverage Promotion By Association

禁止：

```text
one structure Tool verified
→ all structure Tools verified

one electronic fixture verified
→ all N5 Tools verified

one official example
→ entire input family verified

one cross-platform case
→ entire domain cross-platform verified
```

---

# 58. No Coverage Promotion From Invariant Alone

特别：

```text
PASS_INVARIANT
```

不能自动意味着：

```text
REFERENCE_VERIFIED
```

必须根据 Phase 11-0 exact criterion判断。

---

# 59. No Coverage Promotion From Cross-Platform Agreement

特别：

```text
Linux == Windows
```

不能自动意味着：

```text
DIRECT_VERIFIED
REFERENCE_VERIFIED
V4
```

---

# 60. Evidence Strength Must Be Visible

每个 Tool/exemplar最好至少展示：

```text
referenceType

independence

validationLevel

benchmarkVerdict

crossPlatformStatus
```

这样 coverage不会成为一个不透明 badge。

---

# 61. Coverage Explanation Required

每个 row必须有：

```text
whatIsVerified
```

和：

```text
whatIsNotVerified
```

不能为空。

这是 Phase 11-4 的关键设计。

---

# 62. No Marketing Language

禁止：

```text
fully scientifically validated

industry-grade accuracy

universally reproducible

production-grade science

research-grade correctness

complete materials analysis
```

除非 exact evidence支持，当前默认不支持这些泛化。

---

# 63. Known Limits Are First-Class

必须建立：

# Scientific Known Limitations Matrix

至少涵盖：

```text
reference limitations

numeric-reference limitations

algorithm-specific semantics

input-format limitations

cross-platform limitations

browser/presentation limits

historical/example limits

scientific claim boundaries

future scope
```

---

# 64. Four N/A Golden Cases Must Appear

11-4 Known Limitations中必须显式保留：

```text
4 Phase 11-2 reference-limited benchmark records
```

不得从最终文档中消失。

至少记录：

```text
benchmarkId

Tool/family

why N/A

missing bounded numeric reference

effect on coverage verdict

effect on validation level

what remains verified
```

---

# 65. V4=0 Must Appear

最终 coverage summary必须明确：

```text
V4_COUNT = 0
```

如果实际 11-2/11-3 final matrix仍然如此。

不得隐藏 V4 absence。

---

# 66. Validation-Level Distribution

必须从 current post-11-3 matrix自动读取并输出：

```text
V0 count

V1 count

V2 count

V3 count

V4 count
```

不要使用 11-0：

```text
V1=34
V2=28
```

作为最终假设。

11-4必须读取真实 current matrix。

---

# 67. Validation Level ≠ Public Support

即使 Tool只有 V1/V2：

也可能是 production supported with explicit limits。

反之：

高 validation level也不能突破 input/Planner capability限制。

所以最终必须同时保留：

```text
availability

validationLevel

coverageVerdict

inputSupport
```

---

# 68. Coverage Summary by Domain

生成 deterministic summary：

```text
Data / Table

Material Intelligence

Materials ML

Composition Space

Structure

Coordination

Local Environment

XRD

Trajectory

Phonon

Brillouin Zone

Volumetric

Electronic

Presentation / Utility
```

每个 domain至少：

```text
tool count

coverage verdict distribution

validation-level distribution

supported input dependencies

known limitations
```

---

# 69. No Domain Aggregate Without Rule

如果需要 domain aggregate：

必须使用显式 conservative aggregation。

不得：

```text
majority verified
→ domain verified
```

建议/要求：

```text
domain aggregate
=
summary only
```

不作为 individual Tool authority。

---

# 70. Professional N1–N5 Surface Summary

必须单独输出 Initial Release professional coverage：

```text
CrystalNN

VoronoiNN

Local Environment / Polyhedra

Experimental XRD Comparison

Trajectory RDF

Trajectory MSD

Trajectory Diffusion

Electronic Band Structure

Electronic DOS
```

共 9 个 Phase 10N professional Tools。

每个必须带：

```text
exact Tool/version

current validation level

coverage verdict

reference class

11-2 status

11-3 status

known limitation
```

---

# 71. Earlier Initial-Release Science Summary

还必须覆盖：

```text
dataset/composition

statistics

Dataset Explorer

Materials ML

PCA/KMeans

structure summaries

static RDF/XRD

trajectory presentation

phonon

Brillouin zone

volumetric
```

不能只报告最新 N1–N5。

---

# 72. Support + Validation Cross Matrix

建议/要求生成：

# Support × Validation Matrix

例如每项区分：

```text
Product Support

Scientific Validation

Cross-Platform Reproducibility

Presentation Validation
```

目的是防止：

```text
supported
```

与：

```text
reference validated
```

混淆。

---

# 73. Public Claim Matrix

建立：

# Initial Release Public Scientific Claim Matrix

每个 capability至少：

```text
approvedClaim

requiredQualifier

prohibitedClaim

evidenceRefs
```

例如必须保持：

```text
algorithm-derived coordination
```

而不是：

```text
true bonds
```

---

# 74. Input Public Claim Matrix

例如：

允许：

```text
CSV input supported
```

但必须根据 actual matrix限定。

对于：

```text
ZIP
```

应写：

```text
supported with bounded container/content limitations
```

而不是：

```text
all archive formats supported
```

---

# 75. Electronic Public Claim

允许类似：

```text
visualize and analyze supplied/imported
band-structure and DOS data
within supported schemas
```

禁止：

```text
perform DFT electronic-structure calculations
```

---

# 76. Trajectory Public Claim

允许：

```text
RDF / MSD / selected-window diffusion analysis
for supported trajectory resources
```

禁止扩大：

```text
full molecular-dynamics analysis platform
```

---

# 77. XRD Public Claim

允许：

```text
compare experimental peaks against
theoretical peak positions under configured tolerances
```

禁止：

```text
identify phases automatically
```

---

# 78. Coverage UI Is NOT Phase 11-4 Scope

本阶段只生成：

```text
docs
structured evidence
matrices
```

不得开始：

```text
product UI badges
coverage dashboard
design system
new settings page
```

这些属于 Phase 12 UI/UX。

---

# 79. No New Runtime Coverage API

不得创建：

```text
GET /coverage
GET /validation
```

等 public API。

Coverage是当前：

```text
release documentation/evidence authority
```

不是 runtime product feature。

---

# 80. Phase 11-4 Production Boundary

必须：

```text
PRODUCTION_BEHAVIOR_CHANGES = NONE
```

默认：

```text
production source changes = 0
```

允许：

```text
docs

evidence

deterministic coverage generator

coverage consistency tests

persistent state

TASKS

results
```

---

# 81. Deterministic Coverage Generator

允许新增：

```text
coverage matrix generator
```

但只能消费：

```text
Registry

Phase 11 matrices

evidence manifests

input matrix

official-example inventory
```

不能：

```text
execute science

call Adapters for new validation

download references

call external API

call LLM
```

---

# 82. Generator Must Not Infer Missing Facts

如果 evidence缺字段：

输出：

```text
UNRESOLVED
or canonical typed equivalent
```

并由 criterion决定是否 blocker。

不能：

```text
guess reference independence

guess validation level

guess input support

guess license

guess coverage
```

---

# 83. Deterministic Ordering

Tool Matrix：

```text
toolId + version
```

稳定排序。

Input Matrix：

```text
inputFamily canonical key
```

稳定排序。

Example Matrix：

```text
exampleId
```

稳定排序。

不能依赖：

```text
filesystem iteration
Registry insertion order
JSON dict accident
```

---

# 84. Machine-Readable Evidence

建立：

```text
docs/phase11/evidence/
phase11_4_honest_coverage/
```

至少包含：

```text
baseline.txt

entry_gate.md

phase11_3_handoff_snapshot.json

tool_coverage_matrix.json

tool_coverage_summary.json

input_support_matrix.json

input_coverage_summary.json

official_example_coverage_matrix.json

official_example_coverage_summary.json

validation_level_distribution.json

coverage_verdict_distribution.json

support_validation_cross_matrix.json

professional_science_coverage.json

initial_release_science_coverage.json

public_claim_matrix.json

known_scientific_limitations.json

reference_limited_cases.json

cross_platform_limitations.json

coverage_transition_audit.json

coverage_consistency_audit.json

phase11_5_closure_input_manifest.json

no_new_science_audit.md

no_overclaim_audit.md

no_production_change_audit.md

security.md

secret_scan.txt

manifest.json
```

---

# 85. Tool Coverage Distribution

最终必须统计：

```text
DIRECT_VERIFIED_COUNT

OFFICIAL_DERIVED_VERIFIED_COUNT

REFERENCE_VERIFIED_COUNT

MAPPING_ONLY_COUNT

EXTRACTION_REQUIRED_COUNT

FUTURE_SCOPE_COUNT

UNSUPPORTED_COUNT

UNCLASSIFIED_COUNT
```

要求：

```text
sum = 62
UNCLASSIFIED_COUNT = 0
```

---

# 86. Input Distribution

必须统计：

```text
DIRECT_SUPPORTED_COUNT

SUPPORTED_WITH_LIMITS_COUNT

MAPPING_ONLY_COUNT

PARSE_ONLY_COUNT

UNSUPPORTED_COUNT

FUTURE_SCOPE_COUNT

UNCLASSIFIED_COUNT
```

最后：

```text
UNCLASSIFIED_COUNT = 0
```

---

# 87. Example Distribution

必须统计七类 coverage verdict实际数量。

不能提前写死。

最终：

```text
sum =
official/example inventory row count
```

---

# 88. Coverage Transition Audit

每一个相较 11-0发生变化的 row：

必须记录：

```text
rowId

before

after

triggeringPhase

triggeringEvidence

criterion

reason
```

如果：

```text
no evidence change
```

不得改变 verdict。

---

# 89. No Downplaying Gaps

如果某项仍是：

```text
EXTRACTION_REQUIRED
```

或：

```text
MAPPING_ONLY
```

必须保留。

Phase 11-4 不是要求全部变绿。

---

# 90. No Artificial Balance

不要为了让报告好看：

```text
try to maximize verified count
```

目标是：

```text
maximize truthfulness
```

---

# 91. Gap Closure Rules

11-4 可以关闭的 gap只有：

```text
HONEST_COVERAGE_CLASSIFICATION gaps
```

即此前只是：

```text
coverage verdict not yet finalized
```

的 gap。

不能因为 classification完成就关闭：

```text
missing numeric reference

missing independent reference

scientific contract defect
```

---

# 92. Remaining Gaps

最终必须形成：

```text
Phase11RemainingGapMatrix
```

每条：

```text
gapId

category

capability/input/example

current status

release blocking?

why remaining

Phase 11-5 disposition

Future Scope?
```

---

# 93. 11-5 Is Closure, Not New Validation

Phase 11-4 handoff必须确保：

Phase 11-5只负责：

```text
integrity reconciliation

final evidence manifest

final limitation reconciliation

final reproducibility report

final acceptance

Phase 11 seal
```

不是再补 science。

因此：

如果 11-4发现必须新增 benchmark/reference才能让 Phase 11达到 release criteria：

不能：

```text
push it silently to 11-5
```

必须：

```text
BLOCKED / REVIEWER_REQUIRED
```

或者明确：

```text
ACCEPTED_EXPLICIT_LIMITATION
```

前提是 Phase 11 governance允许。

---

# 94. Phase 11-5 Handoff Manifest

建立：

```text
Phase11_5ClosureInputManifest
```

至少包含：

```text
Registry count

DataProfile version

migration head

validation-level distribution

Tool coverage matrix hash

Input support matrix hash

Official-example matrix hash

Reference registry hash

Fixture registry hash

Golden benchmark suite hash

11-2 result summary

11-3 reproducibility summary

Tolerance registry hash

Known limitations hash

Remaining gap matrix hash

revalidation trigger policy hash

roadmap state

release-blocking gap count

accepted limitation count

evidence manifest refs
```

---

# 95. Release-Blocking Gap Rule

11-4 必须明确：

```text
RELEASE_BLOCKING_GAPS
```

如果 >0：

11-4 可以完成 classification工作，

但 Phase状态应：

```text
BLOCKED / REVIEWER_REQUIRED
```

不得假装 Phase 11-5可以纯 closure。

---

# 96. Explicit-Limitation Rule

如果剩余 gap：

```text
scientifically honest

non-release-critical

already bounded

does not falsely advertise support
```

可标：

```text
ACCEPTED_EXPLICIT_LIMITATION
```

但必须引用：

```text
Phase 11 governance authority
```

不得临时创造。

---

# 97. P0/P1/P2

必须读取 current gap matrix。

不能假定：

```text
P0 still 0
```

虽然 11-0/11-1 时是 0。

11-4必须重新统计：

```text
P0 count
P1 count
P2 count
```

如果出现 P0：

默认：

```text
BLOCKED / REVIEWER_REQUIRED
```

---

# 98. No Hidden Scientific Discrepancy

如果 11-2/11-3实际没有 scientific failure：

写：

```text
SCIENTIFIC_BENCHMARK_FAILURES = 0
```

但仍必须保留：

```text
REFERENCE_LIMITATIONS = 4
```

不能把二者混成：

```text
everything validated
```

---

# 99. Validation Level Summary

必须至少输出：

```text
V0
V1
V2
V3
V4
```

并解释：

```text
V4 = 0
```

如果仍为 0。

禁止将：

```text
cross-platform invariant replay
```

重新命名成 V4。

---

# 100. Revalidation Trigger Matrix

每个 final coverage row必须能够映射到既有：

```text
revalidation triggers
```

至少包括：

```text
Tool scientific version changes

algorithm changes

parameter-default semantic changes

Artifact scientific contract changes

unit/reference changes

parser semantic changes

scientific authority dependency changes

fixture expected truth changes

tolerance changes

identity model changes
```

---

# 101. Phase 12 Boundary

必须继续：

```text
Phase 12 =
Comprehensive UI / UX
Product Experience Redesign
```

Phase 11-4 不得做 UI implementation。

但是 11-4 的 coverage/public-claim matrix 将成为 Phase 12：

```text
status language
warning language
availability language
```

的重要输入。

---

# 102. Phase 13 Boundary

继续：

```text
Phase 13 =
Final Product Closure
```

11-4 不执行：

```text
seven final E2E demos
final release packaging
```

---

# 103. Future Scope Guard

必须继续标记 Future Scope，例如：

```text
Fermi surface

projected bands / fatbands

Rietveld refinement

phase fraction

automatic phase identification

DFT

GW

Bader

charge topology

defects

surfaces

advanced transport

effective mass

VACF

Green-Kubo

Arrhenius

hop detection

van Hove
```

不得因 official/example mapping而升级。

---

# 104. Not Planned Guard

继续排除：

```text
generic workflow platform

arbitrary DAG engine

arbitrary notebook execution

runtime autonomous replanning

RAG/vector DB

plugin marketplace

multi-tenant SaaS

billing

enterprise RBAC

distributed scheduler

arbitrary Python
```

---

# 105. LLM Boundary

必须：

```text
NEW_LLM_CALL_SITES = 0

PHASE11_4_REQUIRES_LLM = NO

REAL_LLM_CALLS = 0
```

禁止让 LLM决定：

```text
coverage verdict

support verdict

reference strength

scientific limitation severity
```

Coverage必须是 deterministic evidence classification。

---

# 106. No External Network

Phase 11-4：

```text
EXTERNAL_REFERENCE_DOWNLOADS = 0

EXTERNAL_SCIENTIFIC_API_CALLS = 0

EXTERNAL_COVERAGE_RESEARCH = 0
```

所有事实来自 repository retained evidence。

---

# 107. Security

必须：

```text
NO_PHASE11_4_ARBITRARY_CODE_EXECUTION = PASS

NO_PHASE11_4_NOTEBOOK_EXECUTION = PASS

NO_PHASE11_4_DOWNLOADED_SCRIPT_EXECUTION = PASS

NO_PHASE11_4_EXTERNAL_SCIENTIFIC_API = PASS

NO_PHASE11_4_REFERENCE_DOWNLOAD = PASS

NO_PHASE11_4_FRONTEND_SCIENTIFIC_RECOMPUTATION = PASS

NO_PHASE11_4_LLM_SCIENTIFIC_AUTHORITY = PASS

NO_SECRET_PATTERN_HITS = PASS
```

---

# 108. Database Freeze

必须：

```text
new table = 0

new column = 0

new migration = 0

migration head =
0007_phase10m1_workspace_domain
```

---

# 109. API Freeze

必须：

```text
NEW_PUBLIC_API_FAMILIES = 0
```

---

# 110. Dependency Freeze

必须：

```text
NEW_PYTHON_DEPENDENCIES = 0

NEW_FRONTEND_DEPENDENCIES = 0

LOCKFILE_CHANGES = 0
```

---

# 111. Registry Freeze

必须：

```text
REGISTRY_BEFORE_11_4 = 62

REGISTRY_AFTER_11_4 = 62
```

---

# 112. DataProfile Freeze

必须：

```text
DATAPROFILE_BEFORE_11_4 = 2.4

DATAPROFILE_AFTER_11_4 = 2.4
```

---

# 113. Validation-Level Freeze

必须：

```text
PHASE11_4_VALIDATION_LEVEL_PROMOTIONS = 0

PHASE11_4_VALIDATION_LEVEL_DEMOTIONS = 0
```

11-4只读取 11-3 final levels。

如果发现 level 与 evidence不一致：

```text
GOVERNANCE_INCONSISTENCY
```

而不是自行修改。

---

# 114. Tolerance Freeze

必须：

```text
PHASE11_4_TOLERANCE_CHANGES = 0
```

---

# 115. Reference Freeze

必须：

```text
PHASE11_4_REFERENCE_MUTATIONS = 0

PHASE11_4_FIXTURE_MUTATIONS = 0

PHASE11_4_EXPECTED_VALUE_MUTATIONS = 0
```

---

# 116. Scientific Runtime

Phase 11-4 不应运行新的 targeted scientific benchmark。

允许：

```text
existing regression tests
```

因为它们是 no-regression gate。

但不得将本阶段跑出的普通 regression结果：

```text
promote to new scientific reference evidence
```

---

# 117. Regression Floors

动态读取 Phase 11-3 final：

```text
backend floor

frontend floor

service-backed floor
```

不得低于。

当前 known 11-3 local：

```text
backend = 1278 passed
frontend = 449 passed
```

但必须以 repository final lifecycle中的 canonical count为准。

---

# 118. Browser Regression

必须保持：

```text
Chromium PASS

Firefox PASS

WebKit PASS

390x844 PASS
```

仍然：

```text
presentation-only authority
```

---

# 119. Service Regression

必须保持：

```text
PostgreSQL / Redis / MinIO = PASS

skipped = 0
failed = 0
errors = 0
```

以 current canonical CI threshold为准。

---

# 120. npm Audit

如果 configured mirror仍返回：

```text
404_NOT_IMPLEMENTED
```

必须：

```text
npm audit = UNAVAILABLE
```

不能写：

```text
PASS
clean
```

---

# 121. Acceptance Registry

建立 exact 10 项：

```text
P11V4-A01
PHASE11_3_REPRODUCIBILITY_HANDOFF_ENTRY_AND_COVERAGE_GOVERNANCE_CLOSURE

P11V4-A02
ALL_62_TOOL_VERSIONED_HONEST_COVERAGE_CLASSIFICATION

P11V4-A03
INPUT_PARSER_RESOURCE_PROFILE_PLANNER_RUNTIME_SUPPORT_COVERAGE_CLOSURE

P11V4-A04
OFFICIAL_AND_CANDIDATE_EXAMPLE_HONEST_COVERAGE_RECONCILIATION

P11V4-A05
VALIDATION_LEVEL_REFERENCE_STRENGTH_AND_COVERAGE_AXIS_SEPARATION

P11V4-A06
REFERENCE_LIMITED_NUMERIC_NA_AND_CROSS_PLATFORM_LIMITATION_DISCLOSURE

P11V4-A07
PUBLIC_SCIENTIFIC_CLAIM_LIMITATION_AND_FUTURE_SCOPE_CLOSURE

P11V4-A08
PHASE11_5_FINAL_CLOSURE_HANDOFF_AND_ZERO_CRITICAL_TBD

P11V4-A09
NO_NEW_SCIENCE_NO_PRODUCTION_CHANGE_SECURITY_REGRESSION_AND_EVIDENCE_INTEGRITY

P11V4-A10
IMPLEMENTATION_EXACT_SHA_CI_COMPLETION_ARCHIVE_AND_11_5_REVIEWER_GATE
```

要求：

```text
expected = 10
implemented = 10
missing = 0
extra = 0
duplicate = 0
conflicting = 0
shorthand = 0
```

---

# 122. Queue Admission

Entry Gate PASS 后：

只创建：

```text
one Phase 11-4 task
```

要求：

```text
TASK_BLOCK_COUNT = 1

ACTIVE_TASK = Phase 11-4

PHASE_11_5_EXECUTABLE_TASK_CREATED = NO

PHASE_12_EXECUTABLE_TASK_CREATED = NO

PHASE_13_EXECUTABLE_TASK_CREATED = NO
```

---

# 123. Required Documentation

至少新增：

```text
docs/phase11/
phase11_4_honest_tool_input_example_coverage.md

docs/phase11/
phase11_final_tool_coverage_matrix.md

docs/phase11/
phase11_final_input_support_matrix.md

docs/phase11/
phase11_final_official_example_coverage_matrix.md

docs/phase11/
phase11_support_validation_cross_matrix.md

docs/phase11/
phase11_public_scientific_claim_matrix.md

docs/phase11/
phase11_known_scientific_limitations.md

docs/phase11/
phase11_remaining_gap_matrix.md

docs/phase11/
phase11_5_closure_input_handoff.md

docs/phase11/
phase11_4_completion.md
```

并根据 existing authority更新：

```text
phase11_tool_validation_matrix.md

phase11_input_support_matrix.md

phase11_gap_matrix.md

phase11_implementation_backlog.md

phase11_acceptance_and_test_plan.md

phase11_execution_lock.md

phase11_execution_manifest.md
```

不得重写治理规则。

---

# 124. Persistent State

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

记录：

```text
Phase 11-4 coverage facts only
```

不得：

```text
mark Phase 11 complete
```

Phase 11-5 才有最终 closure authority。

---

# 125. Coverage Consistency Validator

必须至少验证：

```text
all 62 Registry Tools exist exactly once

all Tool versions exact

all validation-level refs resolve

all reference IDs resolve

all benchmark IDs resolve

all 11-3 case IDs resolve

all input families resolve

all official/example IDs resolve

all evidence refs resolve

all coverage verdicts allowlisted

all support verdicts allowlisted

all limitations present where required

all transition reasons present

no impossible promotion

no V4 rows unless source matrix actually has V4

no DIRECT_VERIFIED due browser-only evidence

no REFERENCE_VERIFIED due self-reference only

no official-example verification via mapping-only

no unsupported input marked supported
```

---

# 126. Overclaim Validator

必须 deterministic 检查 prohibited phrases/semantic claims。

至少扫描：

```text
all science validated

fully validated

DFT calculation supported

automatic phase identification

Rietveld

true bonds

confirmed phase

unconditional diffusion

all file formats supported

all platforms verified

numeric reproducibility verified
```

除非上下文明确是在：

```text
prohibitedClaim
```

字段。

---

# 127. Coverage Matrix Hashes

三个 final matrices必须有 deterministic semantic hash：

```text
toolCoverageMatrixHash

inputCoverageMatrixHash

officialExampleCoverageMatrixHash
```

Phase 11-5 使用这些 exact hashes。

---

# 128. Evidence Manifest

必须：

```text
missing required evidence = 0

hash mismatches = 0

duplicate logical IDs = 0

unclassified Tool = 0

unclassified Input = 0

unclassified Example = 0

secret-bearing evidence = 0
```

---

# 129. Implementation Commit

Implementation commit包含：

```text
Phase 11-4 task admission

coverage generator

Tool matrix

Input matrix

Official/example matrix

claim matrix

limitations matrix

remaining gaps

11-5 handoff

validators

tests

evidence

docs

persistent state
```

不得提前：

```text
append final Phase 11-4 completion result
```

---

# 130. Implementation Exact-SHA CI

push implementation后：

必须等待：

```text
IMPLEMENTATION EXACT-SHA CI
```

至少要求：

```text
Unit = PASS

Frontend/typecheck/build/browser = PASS

PostgreSQL/Redis/MinIO = PASS

coverage consistency = PASS

evidence integrity = PASS

no overclaim = PASS
```

---

# 131. Failed Implementation Candidate

如果 CI失败：

必须保留：

```text
SHA
CI run
failure reason
```

然后 fix-forward。

禁止：

```text
force push

rewrite history

delete failed candidate

downgrade coverage requirement

promote weaker evidence

remove inconvenient limitation

change previous scientific evidence
```

---

# 132. Completion Record

Implementation exact-SHA CI PASS 后：

向：

```text
results.md
```

追加：

```text
Phase 11-4 Honest Tool / Input /
Official-Example Coverage Matrix Result
```

然后：

```text
commit
push
```

不主动等待 completion-record CI。

---

# 133. Queue Archive

Completion record push 后：

删除且只删除：

```text
Phase 11-4 TASK block
```

不得创建：

```text
Phase 11-5 task
```

然后：

```text
commit
push
```

不主动等待 archive CI。

---

# 134. Final Successful State

成功：

```text
Phase 11-4:
PASS /
HONEST_COVERAGE_SEALED /
QUEUE_ARCHIVED

Phase 11:
IN_PROGRESS /
SCIENTIFIC_VALIDATION_AND_COVERAGE_COMPLETE
AWAITING_FINAL_CLOSURE

Phase 11-5:
REVIEWER_GATE /
AWAITING REVIEWER PROMPT

Phase 12:
ROADMAP_APPROVED /
NOT_QUEUED /
NOT_EXECUTABLE

Phase 13:
ROADMAP_APPROVED /
NOT_QUEUED /
NOT_EXECUTABLE

TASK_BLOCK_COUNT = 0

PHASE_11_5_EXECUTABLE_TASK_CREATED = NO
```

---

# 135. Mandatory Result Markers

必须：

```text
PHASE11_4_NEW_SCIENTIFIC_TOOLS = 0

PHASE11_4_NEW_SCIENTIFIC_ALGORITHMS = 0

PHASE11_4_NEW_ARTIFACT_FAMILIES = 0

PHASE11_4_NEW_DATAPROFILE_VERSION = 0

PHASE11_4_NEW_ANALYSISPLAN_VERSION = 0

PHASE11_4_NEW_DATABASE_MIGRATIONS = 0

PHASE11_4_NEW_PUBLIC_API_FAMILIES = 0

PHASE11_4_NEW_DEPENDENCIES = 0

PHASE11_4_NEW_LLM_CALL_SITES = 0

PHASE11_4_REAL_LLM_CALLS = 0

PHASE11_4_EXTERNAL_REFERENCE_DOWNLOADS = 0

PHASE11_4_EXTERNAL_SCIENTIFIC_API_CALLS = 0

PHASE11_4_NEW_SCIENTIFIC_BENCHMARKS = 0

PHASE11_4_VALIDATION_LEVEL_PROMOTIONS = 0

PHASE11_4_VALIDATION_LEVEL_DEMOTIONS = 0

PHASE11_4_REFERENCE_MUTATIONS = 0

PHASE11_4_FIXTURE_MUTATIONS = 0

PHASE11_4_EXPECTED_VALUE_MUTATIONS = 0

PHASE11_4_TOLERANCE_CHANGES = 0
```

---

# 136. Coverage Honesty Markers

必须：

```text
SUPPORTED_EQUALS_VALIDATED = NO

DIRECT_SUPPORTED_EQUALS_DIRECT_VERIFIED = NO

PASS_INVARIANT_EQUALS_NUMERIC_REFERENCE_PASS = NO

LINUX_WINDOWS_AGREEMENT_EQUALS_NUMERIC_VALIDATION = NO

OFFICIAL_EXAMPLE_EQUALS_REFERENCE_VERIFIED = NO

MAPPING_EQUALS_VERIFIED = NO

FIXTURE_EXISTS_EQUALS_VERIFIED = NO

SELF_REFERENCE_EQUALS_INDEPENDENT_REFERENCE = NO

BROWSER_PASS_EQUALS_SCIENTIFIC_REFERENCE_PASS = NO

SERVICE_PASS_EQUALS_SCIENTIFIC_REFERENCE_PASS = NO

SCREENSHOT_NUMERIC_SCIENTIFIC_AUTHORITY = NONE

LATEST_EVIDENCE_WINS_AUTHORITY = NO

PASS_DRIVEN_TOLERANCE_CHANGE = PROHIBITED
```

---

# 137. Frozen Scientific Result Markers

必须如实报告：

```text
PHASE11_2_BENCHMARK_RECORDS = <actual>

PHASE11_2_PASS_INVARIANT = <actual>

PHASE11_2_NOT_APPLICABLE = <actual>

PHASE11_2_FAILURES = <actual>

PHASE11_3_REPRODUCIBILITY_CASES = <actual>

PHASE11_3_LINUX_REFERENCE_PASS = <actual>

PHASE11_3_WINDOWS_REFERENCE_PASS = <actual>

PHASE11_3_NUMERIC_CROSS_PLATFORM_COMPARISON =
<actual>

V4_COUNT =
<actual>
```

按照当前 retained事实预期：

```text
12
8
4
0
8
8
8
NOT_APPLICABLE
0
```

但必须从 repository重新读取，不得硬编码后跳过检查。

---

# 138. Baseline Markers

必须：

```text
REGISTRY_BEFORE_11_4 = 62
REGISTRY_AFTER_11_4 = 62

DATAPROFILE_BEFORE_11_4 = 2.4
DATAPROFILE_AFTER_11_4 = 2.4

MIGRATION_BEFORE_11_4 =
0007_phase10m1_workspace_domain

MIGRATION_AFTER_11_4 =
0007_phase10m1_workspace_domain
```

---

# 139. Required results.md Structure

至少：

# Phase 11-4 Honest Tool / Input / Official-Example Coverage Matrix Result

1. Conclusion
2. Phase 11-3 Baseline
3. Entry Gate
4. Phase 11-3 Lifecycle Verification
5. Production Behavior Changes
6. Coverage Governance Authority
7. Coverage Taxonomy
8. Validation-Level vs Coverage Separation
9. Support vs Validation Separation
10. Phase 11-2 Golden Benchmark Reconciliation
11. Eight PASS_INVARIANT Reconciliation
12. Four NOT_APPLICABLE Reference-Limited Cases
13. Phase 11-3 Linux/Windows Reconciliation
14. Numeric Cross-Platform N/A Disclosure
15. V4 Non-Promotion
16. Registry Inventory
17. 62-Tool Matrix Completeness
18. Tool Coverage Matrix
19. Tool Coverage Distribution
20. Validation-Level Distribution
21. Reference Strength Distribution
22. Data/Table Coverage
23. Material Intelligence Coverage
24. Materials ML Coverage
25. Composition Space Coverage
26. Structure Coverage
27. CrystalNN Coverage
28. VoronoiNN Coverage
29. Local Environment/Polyhedra Coverage
30. Experimental XRD Coverage
31. RDF Coverage
32. MSD Coverage
33. Diffusion Coverage
34. Phonon Coverage
35. Brillouin Zone Coverage
36. Volumetric Coverage
37. Band Structure Coverage
38. DOS Coverage
39. Product/Presentation Tool Coverage
40. Nine Professional Tool Summary
41. Earlier Initial-Release Science Summary
42. Input Support Governance
43. Input Support Matrix
44. Direct Supported Inputs
45. Supported-With-Limits Inputs
46. Mapping-Only Inputs
47. Parse-Only Inputs
48. Unsupported Inputs
49. Future Inputs
50. Input Support Limitations
51. Official/Example Inventory
52. Official Example Coverage Matrix
53. Current Examples
54. Historical Examples
55. Mapping-Only Examples
56. Extraction-Required Examples
57. Future-Scope Examples
58. Unsupported Examples
59. Coverage Transition Audit
60. Support × Validation Matrix
61. Public Scientific Claim Matrix
62. Approved Claims
63. Required Qualifiers
64. Prohibited Claims
65. Scientific Known Limitations
66. Four Reference-Limited Benchmark Disclosures
67. Cross-Platform Limitations
68. Browser Authority Boundary
69. Service Authority Boundary
70. Screenshot Authority Boundary
71. Remaining Gaps
72. P0/P1/P2 Distribution
73. Release-Blocking Gaps
74. Accepted Explicit Limitations
75. Revalidation Triggers
76. Phase 11-5 Closure Input Manifest
77. Phase 12 Boundary
78. Phase 13 Boundary
79. Future Scope Guard
80. Not Planned Guard
81. Evidence Inventory
82. Evidence Manifest
83. Security
84. LLM / DeepSeek
85. Database / API / Dependency Freeze
86. Tests
87. Browser Regression
88. Service Regression
89. npm Audit
90. Files Changed
91. Acceptance Registry
92. Implementation Commit
93. Implementation CI
94. Failed Candidates
95. Completion Record
96. Queue Archive
97. Queue State
98. Phase 11-5 Gate
99. Final Repository State

---

# 140. PASS Gate

只有全部满足：

```text
Phase 11-3 PASS

Phase 11-3 queue archived

Phase 11-3 implementation exact-SHA CI PASS

HEAD == origin/master at entry

worktree clean


Registry = 62

DataProfile = 2.4

migration = 0007


all 62 Tools classified exactly once

Tool unclassified = 0

Tool duplicate = 0


all current input families classified

Input unclassified = 0


all official/example records classified

Example unclassified = 0


Phase 11-2:
12 benchmark records reconciled
8 invariant PASS retained
4 N/A retained
0 scientific failure retained

Phase 11-3:
8 admitted cases reconciled
Linux reference replay PASS
Windows reference replay PASS
numeric cross-platform status retained as N/A
V4 promotion remains 0


coverage verdict follows
Phase 11-0 exact criteria

no support→validation shortcut

no invariant→numeric shortcut

no mapping→verified shortcut

no browser→scientific shortcut

no service→scientific shortcut

no screenshot→scientific shortcut

no self-reference→independent shortcut


four reference-limited cases visible

known scientific limitations complete

public claim matrix complete

prohibited claims complete


remaining gaps typed

release-blocking gaps explicitly counted

11-5 handoff complete

critical TBD = 0


new science = 0

new benchmark = 0

new Tool = 0

new algorithm = 0

new reference = 0

reference mutation = 0

fixture mutation = 0

expected-value mutation = 0

tolerance changes = 0

validation-level changes = 0

Registry changes = 0

DataProfile changes = 0

migration changes = 0

public API changes = 0

dependency changes = 0

lockfile changes = 0

real LLM calls = 0


backend >= Phase 11-3 final floor

frontend >= Phase 11-3 final floor

service-backed >= Phase 11-3 final floor

service skipped = 0

service failed = 0

service errors = 0

Chromium PASS

Firefox PASS

WebKit PASS

390x844 PASS

typecheck PASS

build PASS

lock PASS

docs links PASS

coverage consistency PASS

overclaim audit PASS

evidence integrity PASS

security PASS

secret scan PASS


P11V4 acceptance = 10/10


implementation exact-SHA CI PASS

completion record committed/pushed

queue archive committed/pushed


TASK_BLOCK_COUNT = 0

Phase 11-5 task absent

Phase 12 task absent

Phase 13 task absent
```

才允许：

```text
Phase 11-4 = PASS
```

---

# 141. BLOCKED — Evidence Cannot Support Verdict

如果某 row：

```text
does not satisfy exact Phase 11-0 criterion
```

不得选更高 verdict。

如果无法确定：

```text
BLOCKED /
COVERAGE_GOVERNANCE_INCONSISTENCY
```

而不是猜。

---

# 142. BLOCKED — 62 Tool Matrix Incomplete

如果：

```text
Registry = 62
```

但 coverage matrix：

```text
<62
>62
duplicate
unclassified
```

必须 BLOCKED。

---

# 143. BLOCKED — Overclaim

如果生成材料声称：

```text
numeric reference validation
```

而依据只有：

```text
PASS_INVARIANT
```

必须 BLOCKED。

同理：

```text
cross-platform numeric verified
```

而 11-3 numeric status为 N/A：

必须 BLOCKED。

---

# 144. BLOCKED — Hidden N/A

如果四个 11-2 N/A cases：

```text
missing from limitation matrix
```

必须 BLOCKED。

---

# 145. BLOCKED — V4 Fabrication

如果：

```text
V4 > 0
```

但 Phase 11-3 final matrix：

```text
V4 promotion = 0
```

必须：

```text
BLOCKED / VALIDATION_LEVEL_GOVERNANCE_VIOLATION
```

---

# 146. BLOCKED — Input Overstatement

例如发现：

```text
XLSX marked supported
```

但 parser/resource/platform path仍不存在：

必须 BLOCKED。

---

# 147. BLOCKED — Future Scope Leakage

如果 final matrix将：

```text
DFT
GW
Rietveld
Fermi surface
Bader
defects
surfaces
```

等写为 Initial Release supported/verified：

必须 BLOCKED。

---

# 148. BLOCKED — New Science Needed

如果 final release criterion要求补充：

```text
new numeric benchmark
new official reference
new scientific comparison
```

才能成立：

11-4不能自己完成。

必须：

```text
BLOCKED / REVIEWER_REQUIRED
```

由 reviewer决定：

```text
accepted explicit limitation
```

还是：

```text
new corrective validation phase
```

不得推给 11-5偷偷做。

---

# 149. Non-Blockers

通常不阻塞：

```text
some Tools remain V1/V2

V4 count remains 0

four cases remain numeric-reference N/A

some examples remain MAPPING_ONLY

some examples remain EXTRACTION_REQUIRED

phonon direct upload remains MAPPING_ONLY

XLSX remains UNSUPPORTED

Parquet remains UNSUPPORTED

LAMMPS trajectory remains UNSUPPORTED

macOS remains NOT_CURRENT_RELEASE_TARGET
```

只要这些都：

```text
honestly documented
and consistent with Initial Release policy
```

---

# 150. First Required Output

执行开始后首先输出：

```text
Phase 11-4 Entry Gate
+ Phase 11-3 Reproducibility Handoff
+ Honest Coverage Admission Audit
```

至少确认：

1. 11-3 implementation SHA；
2. 11-3 implementation CI；
3. 11-3 completion SHA；
4. 11-3 queue archive SHA；
5. HEAD / origin / branch / worktree；
6. Registry 62；
7. DataProfile 2.4；
8. migration 0007；
9. TASK_BLOCK_COUNT=0；
10. 11-5 task absent；
11. Phase 11-0 exact coverage criteria；
12. Tool Validation Matrix；
13. current validation-level distribution；
14. Phase 11-1 reference registry；
15. Phase 11-1 fixture registry；
16. official/example inventory；
17. Input Support Matrix；
18. 11-2 12-case suite；
19. 8 PASS_INVARIANT；
20. 4 NOT_APPLICABLE；
21. 11-3 8-case handoff；
22. Linux 8/8；
23. Windows 8/8；
24. numeric cross-platform N/A；
25. V4=0；
26. current remaining gap matrix；
27. Future Scope guard；
28. no new scientific work required for classification；
29. no external reference work required；
30. no production change required。

成功才输出：

```text
PHASE_11_4_ENTRY_GATE = PASS

PHASE_11_3_REVIEWER_DEPENDENCY = VERIFIED

PHASE_11_4_QUEUE_ADMISSION = AUTHORIZED

PHASE_11_4_TOOL_COVERAGE_CLASSIFICATION = AUTHORIZED

PHASE_11_4_INPUT_SUPPORT_CLASSIFICATION = AUTHORIZED

PHASE_11_4_OFFICIAL_EXAMPLE_CLASSIFICATION = AUTHORIZED

PHASE_11_4_NEW_SCIENTIFIC_VALIDATION_AUTHORITY = NONE

PHASE_11_4_VALIDATION_LEVEL_CHANGE_AUTHORITY = NONE

PHASE_11_4_PRODUCTION_CHANGE_AUTHORITY = NONE

PHASE_11_4_READINESS =
READY_FOR_HONEST_COVERAGE_CLOSURE
```

---

# 151. Required Execution Sequence

严格：

```text
verify Phase 11-3 lifecycle

→ load Phase 11-0 exact coverage criteria

→ load Phase 11-1 reference/fixture/example/input inventories

→ load Phase 11-2 benchmark matrix

→ load Phase 11-3 reproducibility matrix

→ admit exactly one Phase 11-4 task

→ snapshot current validation levels

→ reconcile all 62 Tool rows

→ assign conservative Tool coverage verdicts

→ generate whatIsVerified / whatIsNotVerified

→ reconcile complete input support matrix

→ reconcile official/example inventory

→ generate Support × Validation matrix

→ generate professional nine-Tool summary

→ generate earlier Initial Release science summary

→ generate public scientific claim matrix

→ generate known limitation matrix

→ preserve four numeric-reference N/A cases

→ preserve V4=0

→ reconcile remaining gaps

→ determine release-blocking gap count

→ generate Phase 11-5 closure handoff

→ run coverage consistency validator

→ run overclaim validator

→ run full no-regression/evidence/security checks

→ create implementation commit

→ push

→ wait for implementation exact-SHA CI

→ if PASS:
   append Phase 11-4 completion result

→ commit/push completion record directly

→ archive only Phase 11-4 task

→ commit/push queue archive directly

→ stop

→ return complete Phase 11-4 result
```

---

# 152. Stop Rule

完成后不得：

```text
execute Phase 11-5

declare Phase 11 COMPLETE

alter scientific validation

add references

run new golden science

change input support

start Phase 12 UI/UX

start Phase 13 release closure
```

必须停在：

```text
Phase 11-5:
REVIEWER_GATE / AWAITING REVIEWER PROMPT
```

等待 reviewer。

---

# 153. Final Scientific Honesty Statement

Phase 11-4 完成后可以说：

```text
“The Initial Release Tool, input, and official-example
coverage has been deterministically classified against
the existing Phase 11 evidence with explicit limitations.”
```

不能说：

```text
“All Tools are independently scientifically validated.”
```

不能说：

```text
“All scientific outputs are numerically cross-platform verified.”
```

不能说：

```text
“All advertised file types are directly supported.”
```

不能说：

```text
“Phase 11 is complete.”
```

Phase 11 的最终封板权仍属于：

```text
Phase 11-5
Scientific Validation Closure
+ Release Candidate Gate
```

完成时间：2026-08-10
修改文件：docs/phase11/phase11_4_*.md，docs/phase11/evidence/phase11_4_honest_tool_input_example_coverage/*，scripts/generate_phase11_4_coverage.py，tests/test_phase11_4_coverage.py及队列兼容测试，persistent/*，results.md
修改摘要：完成62 Tool、14输入家族、55官方/候选示例的诚实覆盖分类；保持Registry、DataProfile、科学算法、验证等级、支持判定、依赖和生产行为不变；保留Phase 11-5 reviewer gate。
测试结果：后端1282 passed，50 skipped；前端449 passed；typecheck、build、uv lock check、Phase 11-4定向测试和CI 31348272583全部通过。
提交/CI状态：失败候选0d57a99及CI 31347561130保留为历史；修正提交09250b1及implementation CI 31348272583成功。

---END---



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
