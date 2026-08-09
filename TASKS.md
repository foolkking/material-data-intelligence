
---TASK---
 状态：处理中

# Phase 11-3 Reviewer Prompt

# Cross-Platform Reproducibility + Variance Characterization

你现在执行：

# Phase 11-3：Cross-Platform Reproducibility + Variance Characterization

中文：

# 跨平台科学可复现性 + 数值/展示差异表征

本阶段属于：

```text
Phase 11:
Scientific Validation,
Reference Provenance,
Reproducibility
& Honest Coverage
```

Phase 11-3 的核心问题是：

> 已经在 Phase 11-2 通过 reference/golden scientific validation 的结果，
> 在当前正式锁定环境下跨 Linux 与 Windows 是否保持科学可复现？

以及：

> 浏览器之间是否只存在允许的展示差异，
> 而不存在前端科学重计算或语义漂移？

````

本阶段不是：

```text
new scientific validation scope

new reference acquisition

new fixture creation

new scientific algorithm

dependency compatibility sweep

performance benchmarking project

UI redesign

release closure
````

---

# 0. Fundamental Scientific Rule

Phase 11-3 绝不能把：

```text
Linux result
```

直接定义为：

```text
scientific truth
```

科学 truth 仍然来自：

```text
Phase 11-1 sealed reference
+
Phase 11-2 golden benchmark
```

因此每个跨平台 scientific case 必须同时满足：

```text
Linux output
→ passes sealed reference

Windows output
→ passes same sealed reference

then:

Linux
vs
Windows
→ variance classification
```

不能只做：

```text
Windows ≈ Linux
→ PASS
```

因为：

```text
two platforms can agree
and both still be scientifically wrong
```

---

# 1. Reviewer Authorization

正式条件预授权：

```text
PHASE_11_3_PROMPT_PREAUTHORIZED = YES

AUTHORIZED_PHASE = Phase 11-3

MAX_PHASES_EXECUTED = 1
```

本 Prompt 不自动证明 11-2 已完成。

Phase 11-3 只有 Entry Gate PASS 后才能 admission。

不得创建、排队或执行：

```text
Phase 11-4

Phase 11-5

Phase 12

Phase 13
```

---

# 2. Mandatory Phase 11-2 Dependency

执行器必须读取真实 repository：

```text
results.md

TASKS.md

git history

persistent/

docs/phase11/

docs/phase11/evidence/
```

动态取得：

```text
PHASE_11_2_IMPLEMENTATION_SHA

PHASE_11_2_IMPLEMENTATION_CI_RUN

PHASE_11_2_IMPLEMENTATION_CI_RESULT

PHASE_11_2_COMPLETION_SHA

PHASE_11_2_QUEUE_ARCHIVE_SHA
```

以及：

```text
Phase 11-2 final status

Golden benchmark suite ID/hash

Benchmark result manifest

Validation levels after 11-2

Scientific discrepancy matrix

Phase11_3ReproducibilityInputManifest
```

如果不存在：

```text
Phase 11-2 = PASS
```

或者：

```text
Phase 11-2 queue archive
```

不存在：

立即：

```text
PHASE_11_3_ENTRY_GATE = BLOCKED

reason =
PHASE_11_2_NOT_COMPLETED_OR_NOT_ARCHIVED
```

然后停止。

---

# 3. 11-2 Scientific Failure Guard

如果 Phase 11-2 最终包含任何未解决：

```text
FAIL_IDENTITY

FAIL_UNIT

FAIL_NUMERIC

FAIL_INVARIANT

FAIL_CONTRACT

FAIL_DETERMINISM

FAIL_UNEXPECTED_SUCCESS

SCIENTIFIC_CONTRACT_DEFECT

REFERENCE_DEFECT
```

且被标记为 blocking：

Phase 11-3 不得执行。

返回：

```text
BLOCKED /
PHASE_11_2_SCIENTIFIC_VALIDATION_NOT_CLOSED
```

不得利用跨平台比较绕过 golden failure。

---

# 4. Dynamic Entry Baseline

Entry authority：

```text
PHASE_11_2_QUEUE_ARCHIVE_SHA
```

必须确认：

```text
branch = master

HEAD == origin/master

HEAD contains 11-2 implementation

HEAD contains 11-2 completion

HEAD contains 11-2 queue archive

worktree = clean
```

不得写死旧的 11-0 / 11-1 SHA 为 current HEAD。

---

# 5. Current Platform Contract Freeze

必须保持：

```text
Registry count = 62

DataProfile = 2.4

migration head =
0007_phase10m1_workspace_domain
```

同时：

```text
AnalysisIntent = unchanged

EligibilityResolution = unchanged

AnalysisPlan 0.1 / 0.2 = unchanged

ToolPlannerMetadata = unchanged

QueueWorkerRuntime = unchanged

Artifact scientific contracts = unchanged

Workspace scientific authority = unchanged

Report/Recipe authority = unchanged
```

---

# 6. Primary Scientific Environment

继续遵守 Phase 11-0：

```text
PRIMARY_SCIENTIFIC_ENVIRONMENT =
CURRENT_LOCKED_REPOSITORY_ENVIRONMENT
```

Phase 11-3 不是：

```text
dependency compatibility project
```

因此禁止测试：

```text
many Python versions

many NumPy versions

many SciPy versions

many pymatgen versions

latest dependencies

nightly dependencies
```

除非 current repository 本身正式声明多个 runtime environments。

---

# 7. Scientific OS Matrix

当前 sealed scientific target：

```text
Linux
+
Windows
```

具体：

```text
Linux =
current canonical CI Linux environment

Windows =
current approved Windows x64 environment
```

如 repository 已存在正式 Windows runner：

复用。

如果不存在：

允许为 Phase 11-3 新增：

```text
validation-only Windows CI job
```

但不得修改 production scientific semantics。

---

# 8. macOS Policy

默认：

```text
MACOS_RELEASE_TARGET = NO
```

因此：

```text
macOS scientific validation
= NOT_REQUIRED
```

除非真实 repository 在 Entry Gate 证明：

```text
macOS is already an explicit current release target
```

不得为了 coverage 临时扩充 macOS。

---

# 9. Architecture Target

默认 scientific platform architecture：

```text
x86_64 / AMD64
```

以 current Linux CI 和 Windows runner 实际事实为准。

不得临时增加：

```text
ARM64
```

作为 release requirement。

如 CI 实际使用其它 architecture：

必须如实记录。

---

# 10. Phase 11-3 Reproducibility Input Authority

必须读取 Phase 11-2 生成的 canonical：

```text
Phase11_3ReproducibilityInputManifest
```

不得重新选择 benchmark cases。

每条至少应具有：

```text
benchmarkId

toolId

toolVersion

scientificCapability

fixtureId

fixtureVersion

fixtureChecksum

referenceId

referenceVersion

expectedTruth

expectedUnits

toleranceId

11_2Verdict

11_2ValidationLevel

Linux baseline output/value/hash

target variance class

Windows requirement

browser requirement if applicable
```

字段名以 repository canonical schema 为准。

---

# 11. Only 11-2 Validated Cases Enter

允许：

```text
11_2 verdict =
PASS_EXACT

PASS_TOLERANCE_BOUNDED

PASS_INVARIANT

PASS_EXPECTED_TYPED_REJECTION
```

进入 11-3。

不得把：

```text
FAIL*

BLOCKED_REFERENCE

NOT_VALIDATED
```

作为 cross-platform baseline。

---

# 12. Reproducibility Scope Cannot Expand

禁止：

```text
add extra scientific benchmark

add extra material dataset

add easier reference

replace fixture

change expected values

change tolerances

change Tool version

change scientific params
```

11-3 必须使用：

```text
same benchmark identity

same Tool/version

same fixture checksum

same reference

same parameter semantics

same tolerance authority
```

---

# 13. Variance Taxonomy

只能使用 Phase 11-0 frozen taxonomy：

```text
EXACT

TOLERANCE_BOUNDED

DISPLAY_ONLY_VARIANCE

UNSUPPORTED_PLATFORM

KNOWN_LIMITATION
```

不得新增：

```text
CLOSE_ENOUGH

MOSTLY_EQUAL

ACCEPTABLE

NEAR_MATCH

PASSISH
```

---

# 14. EXACT Definition

`EXACT` 仅当适用 contract要求 exact semantics。

包括但不限于：

```text
Tool identity

Tool version

fixture checksum

reference identity

Artifact contract/version

categorical scientific result

integer counts

sample/site/atom/frame identities

spin identity

k-point identity

band identity

semantic hashes where platform-independent by contract
```

Numeric floating values：

只有 contract明确要求 exact 时才使用 `EXACT`。

---

# 15. TOLERANCE_BOUNDED Definition

只有满足：

```text
Linux independently passes reference

Windows independently passes reference

cross-platform difference
fits the sealed variance-relevant tolerance policy
```

才允许：

```text
TOLERANCE_BOUNDED
```

不能因为：

```text
Linux ≈ Windows
```

就跳过 reference comparison。

---

# 16. No New Cross-Platform Epsilon

禁止：

```text
CROSS_PLATFORM_EPSILON = newly invented number
```

必须使用：

```text
Phase11ToleranceRegistry
```

中已经具有：

```text
variance relevance
```

的 tolerance。

如果某 quantity：

没有跨平台 variance policy：

```text
VARIANCE_TOLERANCE_UNRESOLVED
```

必须按 governance 处理。

不得临场造 tolerance。

---

# 17. DISPLAY_ONLY_VARIANCE

仅适用于：

```text
pixel placement

font rasterization

canvas antialiasing

subpixel layout

browser tooltip position

non-semantic SVG path rendering

WebGL presentation differences
```

前提：

```text
underlying backend scientific data
is identical / scientifically validated
```

不得将：

```text
numeric scientific discrepancy
```

归类成：

```text
DISPLAY_ONLY_VARIANCE
```

---

# 18. UNSUPPORTED_PLATFORM

只有真实 platform capability 不支持时使用。

必须记录：

```text
why unsupported

whether Windows is current release target

affected Tool/family

dependency/runtime reason

whether limitation existed before 11-3
```

如果一个 Initial Release core scientific capability：

在 Windows current release target 无法运行：

不能简单：

```text
UNSUPPORTED_PLATFORM
→ Phase PASS
```

必须按 release severity 判断。

通常：

```text
REVIEWER_REQUIRED
```

---

# 19. KNOWN_LIMITATION

只能用于已经明确：

```text
documented
bounded
scientifically honest
non-silent
```

的 limitation。

不得：

```text
new mismatch
→ KNOWN_LIMITATION
```

来绕过失败。

新发现 limitation 必须先：

```text
classify severity
```

release-critical 时：

```text
BLOCKED / REVIEWER_REQUIRED
```

---

# 20. Environment Identity Manifest

Linux 与 Windows 都必须记录：

```text
OS

OS version

architecture

Python implementation

Python version

repository commit

lockfile checksum

dependency lock identity

NumPy version

SciPy version

pandas version

pymatgen version

Plotly version if relevant

spglib version if relevant

other scientific authority dependency versions

locale

timezone

float information

BLAS/LAPACK implementation where discoverable

CPU architecture information

CI runner identity class
```

不得记录：

```text
private user path

secret environment variables

tokens

machine credentials
```

---

# 21. Same Lock Requirement

必须：

```text
LINUX_LOCKFILE_SHA256
==
WINDOWS_LOCKFILE_SHA256
```

即：

```text
same repository lock authority
```

平台 marker 导致不同 platform-specific wheels：

允许。

但是：

```text
dependency version semantics
```

必须符合 lock。

---

# 22. No Lock Mutation

如果 Windows 无法安装 current lock：

禁止：

```text
update lock

downgrade library

upgrade library

add dependency

remove dependency
```

来使测试通过。

必须：

```text
WINDOWS_LOCKED_ENVIRONMENT_UNAVAILABLE
```

并 reviewer review。

---

# 23. Dependency Tree Recording

Linux/Windows 都应保存：

```text
resolved package versions
```

重点科学 authority dependencies。

但不得把：

```text
different wheel filename
```

自动当 scientific variance。

---

# 24. Cross-Platform Scientific Procedure

对每一个 scientific reproducibility entry：

执行：

```text
A. verify fixture checksum

B. verify reference identity

C. verify Tool/version

D. verify locked environment

E. run production scientific authority

F. verify exact output contract

G. compare output vs sealed reference

H. classify reference verdict

I. compare Linux vs Windows

J. classify variance

K. deterministic replay

L. record evidence
```

顺序不得反过来。

---

# 25. Linux Revalidation

Linux 不是自动 trusted baseline。

11-3 必须重新执行 selected manifest cases。

要求：

```text
11-3 Linux result
vs
11-2 Linux golden result
```

符合 deterministic/reproducibility semantics。

如果 11-3 Linux 自己已经漂移：

必须：

```text
LINUX_BASELINE_DRIFT
```

不能继续称 Windows variance。

---

# 26. Windows Independent Reference Validation

Windows 必须独立：

```text
Windows output
vs
same sealed reference
```

PASS。

不能只做：

```text
Windows output
vs
Linux output
```

---

# 27. Three-Way Evidence

核心 scientific record：

```text
Reference
↕
Linux
↔
Windows
↕
Reference
```

必须能够回答：

```text
Does Linux pass reference?

Does Windows pass reference?

How much do Linux and Windows differ?
```

---

# 28. Numeric Variance Record

对 numeric field至少记录：

```text
expected

Linux actual

Windows actual

Linux-reference delta

Windows-reference delta

Linux-Windows delta

absolute difference

relative difference
where meaningful

unit

scientific tolerance

variance tolerance policy

classification
```

---

# 29. Identity Variance Record

对 exact identity：

```text
Linux
==
Windows
==
sealed expected identity
```

否则：

```text
FAIL_IDENTITY
```

不能 numeric tolerance 修复 identity mismatch。

---

# 30. Unit Reproducibility

要求：

```text
Linux unit semantics
==
Windows unit semantics
==
sealed expected unit semantics
```

如 numeric values转换后一样但 production unit不同：

不能静默转换后 PASS。

必须按 contract判断。

---

# 31. Canonical Ordering

特别审计：

```text
neighbor ordering

peak ordering

sample ordering

q-point/path ordering

band ordering

DOS channel ordering

polyhedron face ordering

JSON serialization ordering
```

如果 ordering本身不是 scientific identity：

可以 canonicalize：

仅当现有 contract已经规定。

不得 Phase 11-3 新发明排序规则。

---

# 32. Floating-Point Variance Audit

必须显式审计：

```text
floating-point roundoff

negative zero

summation order

BLAS differences

linear algebra differences

regression fitting

ConvexHull ordering

assignment tie behavior
```

但必须区分：

```text
scientific value variance
```

与：

```text
serialization/display variance
```

---

# 33. Negative Zero

`-0.0` 与 `+0.0`：

按照 current canonical serialization/scientific policy。

如果仅 display不同：

```text
DISPLAY_ONLY_VARIANCE
```

如果 semantic hash按 contract要求统一：

必须 canonicalize exactly as existing contract defines。

不得临时决定。

---

# 34. NaN / Inf

任何平台不得因为数值库差异产生未经 contract允许：

```text
NaN
Inf
-Inf
```

若一端出现：

```text
SCIENTIFIC_VARIANCE_FAILURE
```

除非 sealed expected outcome本就是：

```text
typed unavailable/null
```

---

# 35. Locale Audit

验证 Windows/Linux 不因为：

```text
decimal comma

locale-specific parsing

thousands separator

sorting collation
```

改变 scientific semantics。

Scientific serialization必须 locale-independent。

---

# 36. Timezone Audit

Scientific result不得因为：

```text
timezone
```

变化。

Runtime timestamp可不同。

但是 timestamp：

不能参与 scientific semantic hash，除非 contract已有其它规定。

---

# 37. NumPy / Linear Algebra Audit

对于涉及：

```text
PCA

regression

matrix operations

least squares
```

的 benchmark：

记录平台 numerical backend。

只按 sealed scientific tolerance比较。

禁止要求：

```text
bitwise equality
```

除非 contract要求。

---

# 38. PCA Specific Variance

必须保持 existing：

```text
stable sign convention
```

如果 contract已经封板。

禁止：

```text
Windows eigenvector sign opposite
→ just visually flip after result
```

如果 production canonicalization应该消除它：

必须原 production output已经满足。

---

# 39. KMeans Variance

必须使用：

```text
same sealed seed

same feature input

same parameter identity
```

cluster-label semantics依 existing contract。

如 contract允许 permutation equivalence：

使用已封板 equivalence。

不得临时新增。

---

# 40. SciPy Tie Behavior

重点检查可能影响：

```text
XRD matching

assignment

peak operations

ConvexHull
```

的 ties。

如果不同平台对真正等价 tie产生不同合法 ordering：

只能在：

```text
existing contract permits equivalent canonical outcome
```

时接受。

否则是：

```text
DETERMINISM_FAILURE
```

---

# 41. pymatgen Neighbor Ordering

CrystalNN/VoronoiNN：

科学比较应围绕：

```text
stable site/neighbor identity

periodic images

weights

coordination semantics
```

不能仅按 returned array order比较。

但：

不得忽略 identity差异。

---

# 42. CrystalNN / VoronoiNN Independence

继续：

```text
CrystalNN != VoronoiNN
```

Phase 11-3 分别检查：

```text
CrystalNN Linux ↔ Windows

VoronoiNN Linux ↔ Windows
```

不做：

```text
CrystalNN ↔ VoronoiNN equality
```

---

# 43. N2 Geometry Variance

Local Environment / Polyhedra：

重点：

```text
N1 exact dependency identity

classification

vertices

faces

distortion

ConvexHull-related ordering
```

若 face ordering非 semantic：

按 existing canonical policy。

几何值必须在 sealed tolerance内。

---

# 44. XRD Variance

检查：

```text
peak positions

intensity normalized semantics

detected peak identities

one-to-one matching

Δ2θ

matched/unmatched sets

tie cases

zero-match behavior
```

Windows/Linux不得改变：

```text
scientific match conclusion
```

除非 sealed tie policy允许 equivalent result。

---

# 45. RDF Variance

检查：

```text
bin edges

pair identities

counts

normalization

g(r)

window semantics
```

不得因为 floating bin boundary：

产生未解释的不同 particle assignment。

---

# 46. MSD Variance

检查：

```text
PBC unwrap

lag identity

MSD

directional MSD

origin coverage
```

特别是 boundary-crossing fixtures。

---

# 47. Diffusion Variance

检查：

```text
persisted MSD dependency

fit-window identity

fit coefficients

D

diagnostics
```

要求：

```text
classification/diagnostic outcome
```

跨平台保持 contract-compatible。

---

# 48. Phonon Variance

检查：

```text
q-point identity

branch identity

frequency

DOS

imaginary-frequency semantics

combined compatibility
```

不允许因浮点符号附近误差：

静默把：

```text
imaginary
↔
non-imaginary
```

互换。

如果 threshold存在：

使用 sealed threshold。

---

# 49. Brillouin Zone Variance

检查：

```text
reciprocal lattice

vertices

faces

labels

path identities
```

几何 ordering与 scientific identity必须区分。

---

# 50. Volumetric Variance

检查：

```text
grid dimensions

cell identity

field identity

scalar range

slice coordinates

isosurface level semantics
```

浏览器 WebGL mesh像素差：

不等于 backend volumetric science差。

---

# 51. Band Structure Variance

检查：

```text
energy reference

Fermi

spin

k-point identities

bands

VBM

CBM

gap

direct/indirect

bounded classification
```

特别：

```text
threshold-boundary fixture
```

不能跨平台发生无说明分类翻转。

---

# 52. DOS Variance

检查：

```text
energy grid

DOS values

spin channels

projection identities

completeness state
```

不得改变：

```text
COMPLETE / PARTIAL / UNKNOWN
```

semantics。

---

# 53. Materials ML Variance

检查：

```text
MAE

RMSE

R2/null

bias

classification metrics

confusion counts

uncertainty summaries

sample identity
```

categorical/count fields优先 exact。

float metrics按 sealed tolerance。

---

# 54. Dataset Intelligence Variance

应主要：

```text
EXACT
```

针对：

```text
counts

identities

duplicate classes

element/system membership

coverage

missingness
```

如果同 source 在不同 OS 得不同 dataset identity/count：

通常是 blocker。

---

# 55. Browser Matrix

保持：

```text
Chromium

Firefox

WebKit

Chromium 390x844
```

这是：

```text
PRESENTATION REPRODUCIBILITY MATRIX
```

不是 numeric scientific matrix。

---

# 56. Do Not Multiply OS × Browser Without Need

11-3 默认不要求：

```text
Linux × Chromium/Firefox/WebKit
+
Windows × Chromium/Firefox/WebKit
```

完整笛卡尔积。

除非 Phase 11-0/11-2 handoff明确要求。

科学 OS matrix：

```text
Linux + Windows
```

Browser presentation matrix：

```text
existing canonical browser environment
```

两者分开。

---

# 57. Browser Scientific Payload Rule

所有 browser viewer：

必须消费：

```text
same backend/persisted scientific data
```

不得：

```text
recalculate scientific values
per browser
```

必须保持：

```text
FRONTEND_SCIENTIFIC_RECOMPUTATION = 0
```

---

# 58. Browser Presentation Invariants

至少验证：

```text
same scientific labels

same scientific values after approved display formatting

same units

same warnings

same limitations

same selection identity

same source identity

same Artifact provenance

same typed states

same report/recipe scientific content
```

---

# 59. Display Rounding

浏览器显示可以按 existing formatting：

```text
round
format
wrap
```

但 raw scientific authority：

不在浏览器。

如果不同 browser格式化数值不同：

必须判断：

```text
DISPLAY_ONLY_VARIANCE
```

还是：

```text
semantic presentation defect
```

不能藏起来。

---

# 60. WebGL Variance

允许：

```text
antialiasing

shader rasterization

pixel-level appearance

minor camera raster differences
```

成为：

```text
DISPLAY_ONLY_VARIANCE
```

但：

```text
selected scientific object identity

structure data

trajectory frame

volumetric field

BZ identity
```

必须保持 exact。

---

# 61. Screenshot Authority

继续：

```text
SCREENSHOT_NUMERIC_SCIENTIFIC_AUTHORITY = NONE
```

截图只能支持：

```text
presentation evidence
```

不能用于 Linux/Windows scientific numeric comparison。

---

# 62. Browser Pixel Perfect Equality

禁止：

```text
PIXEL_PERFECT_EQUALITY_REQUIRED = YES
```

除非 current existing test明确有此要求。

重点是：

```text
semantic presentation invariants
```

---

# 63. Accessibility Reproducibility

browser matrix继续验证：

```text
semantic headings

labels

status

numeric/table alternatives

keyboard access

focus

non-color states

mobile no-overflow
```

但 Phase 12 才负责全面 UX redesign。

11-3 不进行 UI重构。

---

# 64. Service-Backed Boundary

PostgreSQL / Redis / MinIO继续作为 regression。

它们验证：

```text
persistence

runtime

Artifact storage

lineage

scope

checksum
```

不属于：

```text
cross-platform numeric truth
```

---

# 65. Windows Service Requirement

默认不要求：

```text
Windows service-backed PostgreSQL/Redis/MinIO stack
```

除非 existing release architecture明确要求。

Windows scientific reproducibility可以使用：

```text
direct registered production Adapter/kernel paths
+
sealed benchmark harness
```

Linux existing service-backed path继续证明 production integration。

---

# 66. Production Runtime Cross-Check

若某 cross-platform case 可以无 service执行 registered scientific authority：

允许。

但不得换成：

```text
test-only reimplementation
```

必须仍使用：

```text
production module / registered Adapter implementation
```

---

# 67. No Scientific Reference Downloads

Phase 11-3：

```text
EXTERNAL_REFERENCE_DOWNLOADS = 0
```

所有 reference/fixture来自：

```text
Phase 11-1 sealed local reference authority
```

---

# 68. No Scientific External APIs

必须：

```text
EXTERNAL_SCIENTIFIC_API_CALLS = 0
```

---

# 69. Normal CI Dependency Acquisition

正常：

```text
uv sync/install from existing lock
npm install from existing lock
```

依 current CI policy执行。

这不算：

```text
scientific external reference acquisition
```

但不得：

```text
pip install arbitrary new package
```

---

# 70. No LLM

必须：

```text
NEW_LLM_CALL_SITES = 0

PHASE11_3_REQUIRES_LLM = NO

REAL_LLM_CALLS = 0
```

LLM不能：

```text
judge numeric variance

classify scientific mismatch

invent known limitation

repair platform result
```

---

# 71. No Scientific Algorithm Change

必须：

```text
PHASE11_3_NEW_SCIENTIFIC_ALGORITHMS = 0
```

---

# 72. Production Change Boundary

默认：

```text
PRODUCTION_SCIENTIFIC_SOURCE_CHANGES = 0
```

允许修改：

```text
validation harness

cross-platform CI

test utilities

evidence serializers

docs

persistent state

TASKS

results
```

---

# 73. Harness / CI Fixes

如果 failure来自：

```text
Windows path separator in test harness

shell quoting

newline handling

CI command syntax

evidence path normalization

platform temp directory handling
```

且：

```text
production scientific output unchanged
```

可 fix-forward。

---

# 74. Scientific Production Divergence

如果 Windows/Linux scientific production logic实际产生超 tolerance差异：

不得：

```text
add if sys.platform == "win32"
to force matching
```

也不得：

```text
round harder
sort away mismatch
change algorithm
```

必须冻结 discrepancy 并 reviewer review。

---

# 75. Reference Revalidation Per Platform

每个 scientific platform run必须再次确认：

```text
fixture checksum unchanged

reference checksum unchanged

expected truth unchanged

tolerance unchanged
```

不得 Phase 11-3改变任何一个。

---

# 76. Reference Mutation Marker

必须：

```text
PHASE11_3_REFERENCE_FIXTURE_MUTATIONS = 0

PHASE11_3_EXPECTED_VALUE_MUTATIONS = 0

PHASE11_3_TOLERANCE_CHANGES = 0
```

---

# 77. 11-2 Evidence Immutability

不得 rewrite：

```text
Phase 11-2 benchmark results

Phase 11-2 golden suite

Phase 11-2 validation-level-before

Phase 11-2 validation-level-after
```

11-3产生自己的新 evidence。

---

# 78. Validation Levels

Phase 11-3 是第一次允许：

```text
V3 → V4
```

但必须严格依 Phase 11 validation policy。

---

# 79. V4 Meaning

V4：

```text
CROSS_PLATFORM_REPRODUCIBILITY_VERIFIED
```

只有 Tool/version 已经满足 required V3 scientific-reference criteria，并通过 required Linux/Windows reproducibility matrix：

才可：

```text
V3 → V4
```

---

# 80. No V2 → V4 Shortcut

禁止：

```text
V2 → V4
```

即使 Windows/Linux结果一致。

没有 V3 reference authority：

跨平台一致也不能证明 reference validity。

---

# 81. No Domain Bulk V4

禁止：

```text
one N4 Tool V4
→ all trajectory V4
```

每个：

```text
Tool ID/version
```

必须自己的 required cross-platform evidence完整。

---

# 82. Presentation-Only Tool Levels

presentation-only / metadata tools：

按照 Phase 11-0 validation-level policy。

不得因为：

```text
three browsers PASS
```

强行称 scientific V4。

---

# 83. V4 Promotion Record

每个 promotion至少：

```text
toolId

toolVersion

beforeLevel

afterLevel

11_2 benchmark IDs

Linux result IDs

Windows result IDs

variance classifications

reference IDs

tolerance IDs

evidence paths

limitations
```

---

# 84. Reproducibility Result Record

每个 case至少：

```text
reproducibilityCaseId

benchmarkId

Tool/version

fixture/reference identity

Linux environment ID

Windows environment ID

Linux actual

Windows actual

expected truth

units

reference tolerance

cross-platform delta

variance verdict

Linux reference verdict

Windows reference verdict

determinism verdict

known limitation

evidence refs
```

---

# 85. Environment Semantic Hash

建立：

```text
environmentSemanticHash
```

至少覆盖：

```text
OS family

architecture

Python exact version

lockfile hash

scientific dependency versions

relevant numerical backend identities
```

不应包含：

```text
runner hostname

username

private path

timestamp
```

---

# 86. Cross-Platform Matrix

建立：

```text
Phase11CrossPlatformReproducibilityMatrix
```

每个 row：

```text
Tool/version

benchmark ID

scientific family

Linux reference status

Windows reference status

Linux-Windows variance

variance taxonomy

current validation level

V4 eligibility

known limitation

blocking?
```

---

# 87. Variance Summary

最终必须统计：

```text
EXACT count

TOLERANCE_BOUNDED count

DISPLAY_ONLY_VARIANCE count

UNSUPPORTED_PLATFORM count

KNOWN_LIMITATION count
```

还必须：

```text
UNCLASSIFIED = 0
```

---

# 88. Scientific Variance Cannot Be DISPLAY_ONLY

硬规则：

```text
scientific field changed
→ DISPLAY_ONLY_VARIANCE prohibited
```

---

# 89. Variance Failure Taxonomy

如果需要 failure detail：

至少：

```text
FAIL_REFERENCE_LINUX

FAIL_REFERENCE_WINDOWS

FAIL_CROSS_PLATFORM_TOLERANCE

FAIL_IDENTITY

FAIL_UNIT

FAIL_CONTRACT

FAIL_DETERMINISM

FAIL_ENVIRONMENT

FAIL_UNEXPECTED_PLATFORM_UNSUPPORTED
```

---

# 90. Both Platforms Pass Reference But Differ

如果：

```text
Linux passes reference

Windows passes reference

Linux != Windows
```

但差异仍在 sealed cross-platform tolerance：

```text
TOLERANCE_BOUNDED
```

这是合法结果。

不需要追求 byte-for-byte float equality。

---

# 91. One Platform Fails Reference

如果：

```text
Linux PASS

Windows FAIL
```

或者反之：

不能：

```text
TOLERANCE_BOUNDED
```

必须：

```text
SCIENTIFIC_REPRODUCIBILITY_FAILURE
```

---

# 92. Both Platforms Fail the Same Way

如果：

```text
Linux fails reference

Windows fails reference

Linux == Windows
```

仍然：

```text
FAIL
```

不能用一致性掩盖科学错误。

---

# 93. Known Limitation Cannot Mask Reference Failure

即使已有：

```text
KNOWN_LIMITATION
```

也不能自动允许：

```text
reference benchmark failure
```

除非 Phase 11 governance明确规定该 limitation使 case：

```text
not a supported scientific claim
```

并已经在 11-2 disposition。

---

# 94. Performance Measurements

允许记录：

```text
elapsed time

memory
```

作为 diagnostics。

但 Phase 11-3不应建立：

```text
Linux must be same speed as Windows
```

的要求。

不得做生产 capacity claim。

---

# 95. Browser Performance

同样只作为 diagnostics。

不影响 scientific variance verdict。

---

# 96. Windows CI Job

如果 current repo没有：

允许新增类似：

```text
Phase 11 Cross-Platform Scientific Reproducibility - Windows
```

validation job。

该 job必须：

```text
checkout exact SHA

use locked dependencies

run exact sealed 11-3 scientific subset

generate deterministic evidence

perform zero external science calls

perform zero real LLM calls
```

---

# 97. Linux CI Job

应在同一 implementation exact-SHA CI中运行：

```text
Linux scientific reproducibility baseline
```

不能只用历史 11-2结果而不重跑。

---

# 98. Implementation CI Required Jobs

11-3 implementation exact-SHA CI必须至少覆盖：

```text
Linux Unit / scientific reproducibility

Windows scientific reproducibility

Frontend/typecheck/build

canonical browser matrix

PostgreSQL/Redis/MinIO service-backed regression

evidence integrity

no-skipped required scientific matrix
```

---

# 99. Required Scientific Skip Policy

对于 11-3 required scientific cases：

```text
SKIP = FAILURE
```

除非 manifest已明确：

```text
NOT_REQUIRED
```

或：

```text
UNSUPPORTED_PLATFORM
```

且该 unsupported status本身已被 governance允许。

---

# 100. Windows Core Capability Unsupported

如果 required release capability：

```text
Windows = UNSUPPORTED_PLATFORM
```

必须判断：

```text
Is Windows an explicit release target?
YES
```

则通常：

```text
BLOCKED / REVIEWER_REQUIRED
```

不得自动 PASS Phase 11-3。

---

# 101. Browser Skip Policy

Chromium / Firefox / WebKit / mobile required matrix：

不得因为 runner困难静默 skip。

如果当前 browser matrix是 release requirement：

skip：

```text
FAIL
```

---

# 102. Evidence Directory

建立：

```text
docs/phase11/evidence/
phase11_3_cross_platform_reproducibility/
```

至少：

```text
baseline.txt

entry_gate.md

phase11_2_handoff_snapshot.json

environment_matrix.json

linux_environment.json

windows_environment.json

lock_identity.json

scientific_reproducibility_manifest.json

linux_results.json

windows_results.json

reference_revalidation_matrix.json

cross_platform_numeric_variance.json

cross_platform_identity_variance.json

unit_variance_matrix.json

determinism_matrix.json

variance_classification_matrix.json

known_limitations.json

unsupported_platform_matrix.json

validation_levels_before.json

validation_levels_after.json

v4_promotions.json

browser_presentation_invariants.json

browser_variance_matrix.json

service_backed.md

no_reference_mutation_audit.md

no_tolerance_change_audit.md

no_production_science_change_audit.md

security.md

phase11_4_handoff.json

secret_scan.txt

manifest.json
```

---

# 103. Per-Case Evidence

建议：

```text
cases/{reproducibilityCaseId}/
```

保存：

```text
input.json

reference.json

linux_actual.json

windows_actual.json

linux_reference_comparison.json

windows_reference_comparison.json

cross_platform_comparison.json

environment.json

classification.json
```

遵从 repository existing convention。

---

# 104. Browser Evidence Separation

browser evidence目录必须与：

```text
scientific numeric variance
```

明确分开。

不能同一 screenshot文件同时作为 numeric authority。

---

# 105. Phase 11-4 Handoff

11-3 必须生成：

```text
Phase11_4HonestCoverageInputManifest
```

至少包含：

```text
toolId/version

roleClass

validationLevel after 11-3

reference provenance status

11-2 benchmark verdict

11-3 variance verdict

V4 status

browser status

service status

input-support relationship

official-example relationship

known limitations

remaining gaps

evidence refs

coverage eligibility facts
```

---

# 106. No Final Coverage Verdict Yet

11-3 不能直接发布：

```text
DIRECT_VERIFIED

OFFICIAL_DERIVED_VERIFIED

REFERENCE_VERIFIED
```

作为最终 product coverage。

这些属于：

```text
Phase 11-4
```

11-3只能提供：

```text
coverage inputs
```

---

# 107. Acceptance Registry

建立 exact 10 项：

```text
P11V3-A01
PHASE11_2_GOLDEN_BASELINE_REPRODUCIBILITY_HANDOFF_AND_ENTRY_CLOSURE

P11V3-A02
LOCKED_LINUX_WINDOWS_ENVIRONMENT_IDENTITY_AND_LOCK_PARITY_CLOSURE

P11V3-A03
LINUX_GOLDEN_REFERENCE_REPLAY_AND_BASELINE_STABILITY

P11V3-A04
WINDOWS_INDEPENDENT_GOLDEN_REFERENCE_REPRODUCIBILITY

P11V3-A05
CROSS_PLATFORM_EXACT_TOLERANCE_VARIANCE_AND_LIMITATION_CLASSIFICATION

P11V3-A06
SCIENTIFIC_IDENTITY_UNIT_DETERMINISM_AND_DOMAIN_VARIANCE_CLOSURE

P11V3-A07
CHROMIUM_FIREFOX_WEBKIT_MOBILE_PRESENTATION_INVARIANT_CLOSURE

P11V3-A08
V4_VALIDATION_LEVEL_PROMOTION_REVALIDATION_AND_HONEST_LIMITATION_CLOSURE

P11V3-A09
NO_PRODUCTION_SCIENCE_CHANGE_SECURITY_SERVICE_REGRESSION_AND_EVIDENCE_INTEGRITY

P11V3-A10
IMPLEMENTATION_EXACT_SHA_CI_COMPLETION_ARCHIVE_AND_11_4_REVIEWER_GATE
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

# 108. Queue Admission

Entry Gate PASS 后：

只创建：

```text
one Phase 11-3 task
```

要求：

```text
TASK_BLOCK_COUNT = 1

ACTIVE_TASK = Phase 11-3

PHASE_11_4_EXECUTABLE_TASK_CREATED = NO

PHASE_12_EXECUTABLE_TASK_CREATED = NO

PHASE_13_EXECUTABLE_TASK_CREATED = NO
```

---

# 109. Required Documentation

至少新增：

```text
docs/phase11/
phase11_3_cross_platform_reproducibility_and_variance.md

docs/phase11/
phase11_cross_platform_environment_matrix.md

docs/phase11/
phase11_cross_platform_reproducibility_matrix.md

docs/phase11/
phase11_variance_result_matrix.md

docs/phase11/
phase11_v4_validation_level_update.md

docs/phase11/
phase11_browser_presentation_invariant_matrix.md

docs/phase11/
phase11_known_platform_limitations.md

docs/phase11/
phase11_4_honest_coverage_input_handoff.md

docs/phase11/
phase11_3_completion.md
```

并更新：

```text
phase11_tool_validation_matrix.md

phase11_gap_matrix.md

phase11_implementation_backlog.md

phase11_acceptance_and_test_plan.md

phase11_execution_lock.md

phase11_execution_manifest.md
```

不得修改已封板 scientific meaning。

---

# 110. Persistent State

同步：

```text
PROJECT_BRIEF

DESIGN_PROGRESS

TASK_BOARD

CHANGELOG

OPEN_QUESTIONS

ARCHITECTURE_DECISIONS

TOOL_REGISTRY_NOTES
```

不得创建 11-4 executable task。

---

# 111. Database Freeze

必须：

```text
new database tables = 0

new database columns = 0

new migrations = 0

migration head =
0007_phase10m1_workspace_domain
```

---

# 112. API Freeze

必须：

```text
NEW_PUBLIC_API_FAMILIES = 0
```

---

# 113. Dependency Freeze

必须：

```text
NEW_PYTHON_DEPENDENCIES = 0

NEW_FRONTEND_DEPENDENCIES = 0

LOCKFILE_CHANGES = 0
```

---

# 114. Registry Freeze

必须：

```text
REGISTRY_BEFORE_11_3 = 62

REGISTRY_AFTER_11_3 = 62
```

---

# 115. DataProfile Freeze

必须：

```text
DATAPROFILE_BEFORE_11_3 = 2.4

DATAPROFILE_AFTER_11_3 = 2.4
```

---

# 116. AnalysisPlan Freeze

必须：

```text
ANALYSISPLAN_VERSIONS =
0.1 / 0.2 unchanged
```

---

# 117. Artifact Freeze

必须：

```text
NEW_PRODUCTION_ARTIFACT_FAMILIES = 0
```

---

# 118. UI/UX Freeze

不得开始 Phase 12。

尤其：

```text
Design System 2.0 = NOT_STARTED

Navigation redesign = NOT_STARTED

Planner UX redesign = NOT_STARTED

Workspace redesign = NOT_STARTED
```

browser修复只允许：

```text
test harness / regression infrastructure
```

或非常明确的非科学 blocker，且不能演变成 UX redesign。

---

# 119. Future Scope Guard

继续排除：

```text
Fermi surface

projected bands

Rietveld

phase fraction

automatic phase ID

DFT/GW

Bader

defects/surfaces

advanced transport

advanced trajectory science
```

---

# 120. Not Planned Guard

继续排除：

```text
generic workflow

arbitrary DAG

notebook execution

RAG/vector DB

plugin marketplace

multi-tenant SaaS

distributed scheduler

arbitrary Python

autonomous replanning
```

---

# 121. Security

必须：

```text
NO_PHASE11_3_ARBITRARY_CODE_EXECUTION = PASS

NO_PHASE11_3_NOTEBOOK_EXECUTION = PASS

NO_PHASE11_3_DOWNLOADED_SCRIPT_EXECUTION = PASS

NO_PHASE11_3_EXTERNAL_SCIENTIFIC_API = PASS

NO_PHASE11_3_REFERENCE_DOWNLOAD = PASS

NO_PHASE11_3_FRONTEND_SCIENTIFIC_RECOMPUTATION = PASS

NO_PHASE11_3_LLM_SCIENTIFIC_AUTHORITY = PASS

NO_SECRET_PATTERN_HITS = PASS
```

---

# 122. Scientific Honesty Markers

必须：

```text
LINUX_EQUALS_SCIENTIFIC_TRUTH = NO

WINDOWS_EQUALS_SCIENTIFIC_TRUTH = NO

CROSS_PLATFORM_AGREEMENT_EQUALS_REFERENCE_PASS = NO

SCREENSHOT_NUMERIC_SCIENTIFIC_AUTHORITY = NONE

BROWSER_NUMERIC_SCIENTIFIC_AUTHORITY = NONE

SERVICE_NUMERIC_SCIENTIFIC_AUTHORITY = NONE

DISPLAY_ONLY_VARIANCE_CAN_MASK_NUMERIC_DIFFERENCE = NO

PASS_DRIVEN_TOLERANCE_CHANGE = PROHIBITED

REFERENCE_FIXTURE_MUTATIONS = 0

EXPECTED_VALUE_MUTATIONS = 0

SCIENTIFIC_TOLERANCE_CHANGES = 0
```

---

# 123. Validation-Level Markers

必须：

```text
V2_TO_V4_SHORTCUT = PROHIBITED

V3_TO_V4_REQUIRES_REQUIRED_PLATFORM_EVIDENCE = YES

DOMAIN_BULK_V4_PROMOTION = PROHIBITED

BROWSER_PASS_EQUALS_V4 = NO
```

---

# 124. Dynamic Regression Floors

必须读取 Phase 11-2 final：

```text
BACKEND_PASS_COUNT

FRONTEND_PASS_COUNT

SERVICE_PASS_COUNT
```

Phase 11-3 final不得低于：

```text
backend floor =
max(1263, Phase 11-2 final backend)

frontend floor =
max(449, Phase 11-2 final frontend)

service floor =
Phase 11-2 final required service-backed count
```

---

# 125. Browser Regression Floor

保持：

```text
Chromium = PASS

Firefox = PASS

WebKit = PASS

390x844 = PASS
```

---

# 126. Service Regression

必须：

```text
PostgreSQL / Redis / MinIO = PASS

skipped = 0

failed = 0

errors = 0
```

依据 dynamic service floor。

---

# 127. npm Audit

如果 configured mirror仍：

```text
404_NOT_IMPLEMENTED
```

必须：

```text
npm audit = UNAVAILABLE
```

不能：

```text
PASS
clean
```

---

# 128. Verification Commands

至少：

```powershell
git diff --check

uv lock --check

uv run python -m pytest -q

npm --prefix apps/web test

npm --prefix apps/web run typecheck

npm --prefix apps/web run build
```

另运行：

```text
Phase 10 retained evidence integrity

Phase 11-0 evidence integrity

Phase 11-1 evidence integrity

Phase 11-2 golden benchmark integrity

Phase 11-3 environment validator

lock parity validator

Linux reproducibility runner

Windows reproducibility runner

reference revalidation validator

variance classification validator

V4 transition validator

browser presentation invariant runner

Phase 11-4 handoff validator

docs links

TASKS lifecycle

secret scan
```

---

# 129. Windows Commands / Shell Independence

不要假设 Windows：

```text
bash
```

可用。

validation tooling应尽量：

```text
Python-based
cross-platform
```

或者使用：

```text
PowerShell
```

不得因为测试工具依赖 Unix-only shell：

错误标记 scientific capability：

```text
UNSUPPORTED_PLATFORM
```

---

# 130. Path Independence

科学 fixture/resource identity不得依赖：

```text
/

vs

\
```

也不得依赖 absolute path。

Windows/Linux source path差异不能进入 scientific semantic hash。

---

# 131. Line Ending Independence

必须处理：

```text
LF

CRLF
```

只在：

```text
non-scientific text/evidence representation
```

层 canonicalize。

不得改变 binary/scientific source bytes 的 checksum authority。

---

# 132. Case Sensitivity

必须审计：

```text
case-sensitive filesystem
vs
case-insensitive filesystem
```

不能导致：

```text
fixture collision

wrong resource load

Tool identity collision
```

---

# 133. Unicode Paths

如现有 fixtures/tests涵盖：

可以验证。

但不能新增不必要 platform expansion。

Scientific identity不得依赖 local filesystem display path。

---

# 134. Implementation Commit

Implementation commit应包含：

```text
Phase 11-3 task admission

cross-platform validation harness

Linux scientific replay

Windows scientific reproducibility CI

variance classifiers

environment manifests

browser presentation invariant evidence

V4 level updates

Phase 11-4 handoff

tests

docs

persistent state
```

不得提前：

```text
append final results.md completion
```

---

# 135. Implementation Exact-SHA CI

push implementation。

然后必须等待：

```text
IMPLEMENTATION EXACT-SHA CI
```

这里比普通 Phase 更关键，因为必须确认：

```text
Linux required job PASS

Windows required job PASS

Frontend/browser/build PASS

service-backed PASS

evidence integrity PASS
```

如果 Windows job没有实际运行：

不能声称 Phase 11-3 PASS。

---

# 136. Failed Implementation Candidate

任何 failed implementation：

必须保留：

```text
SHA

CI run

failed job

failure reason
```

然后：

```text
fix forward
```

禁止：

```text
force push

rewrite history

remove Windows job

skip failing scientific case

change reference

change tolerance

change expected value

weaken validation
```

---

# 137. Completion Record

只有 implementation exact-SHA CI PASS 后：

向：

```text
results.md
```

追加完整 Phase 11-3 result。

然后：

```text
commit
push
```

按当前 user lifecycle：

```text
DO NOT WAIT
for additional completion-record CI
```

如果自然返回明确 failure：

不得故意忽略。

---

# 138. Queue Archive

Completion record push 后：

删除且只删除：

```text
Phase 11-3 TASK block
```

不得创建：

```text
Phase 11-4 task
```

然后：

```text
commit
push
```

不主动等待 archive CI。

若 archive 未经 exact-SHA CI等待验证：

术语：

```text
QUEUE_ARCHIVED
```

不得虚构：

```text
ARCHIVED_BY_VERIFIED_QUEUE_COMMIT
```

---

# 139. Final State

成功后：

```text
Phase 11-3:
PASS /
CROSS_PLATFORM_REPRODUCIBILITY_CHARACTERIZED /
QUEUE_ARCHIVED

Phase 11:
IN_PROGRESS /
REFERENCE_AND_REPRODUCIBILITY_VALIDATION_COMPLETE
FOR_SEALED_SCOPE

Phase 11-4:
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

PHASE_11_4_EXECUTABLE_TASK_CREATED = NO
```

---

# 140. Required results.md Structure

至少：

# Phase 11-3 Cross-Platform Reproducibility + Variance Characterization Result

1. Conclusion
2. Phase 11-2 Baseline
3. Entry Gate
4. Phase 11-2 Lifecycle Verification
5. Reproducibility Handoff Integrity
6. Scientific Scope
7. Production Behavior Changes
8. Linux Environment Identity
9. Windows Environment Identity
10. Lockfile Parity
11. Scientific Dependency Version Parity
12. Numerical Backend Inventory
13. Locale / Timezone / Float Environment
14. Validation Levels Before
15. Linux Golden Replay
16. Linux Baseline Drift Audit
17. Windows Reference Validation
18. Cross-Platform Scientific Comparison
19. Exact Variance Matrix
20. Tolerance-Bounded Variance Matrix
21. Display-Only Variance Matrix
22. Unsupported Platform Matrix
23. Known Limitation Matrix
24. Identity Reproducibility
25. Unit Reproducibility
26. Determinism
27. Dataset Intelligence Variance
28. Materials ML Variance
29. Composition Space Variance
30. Structure Variance
31. CrystalNN Variance
32. VoronoiNN Variance
33. Local Environment / Polyhedra Variance
34. Experimental XRD Variance
35. RDF Variance
36. MSD Variance
37. Diffusion Variance
38. Phonon Variance
39. Brillouin Zone Variance
40. Volumetric Variance
41. Band Structure Variance
42. DOS Variance
43. Combined Band + DOS Variance
44. Floating-Point Variance
45. Ordering / Tie Variance
46. NaN / Inf / Signed-Zero Audit
47. Locale / Timezone Audit
48. Browser Presentation Matrix
49. Chromium
50. Firefox
51. WebKit
52. 390x844
53. WebGL Presentation Variance
54. Accessibility Presentation Invariants
55. Frontend No-Recomputation
56. Service-Backed Regression
57. Validation Levels After
58. V4 Promotions
59. Tools Not Eligible for V4
60. Scientific Reproducibility Failures
61. Platform Limitations
62. Phase 11-4 Honest Coverage Handoff
63. Evidence Inventory
64. Evidence Manifest
65. Security
66. LLM / DeepSeek
67. Database / API / Dependency Freeze
68. Tests
69. Linux CI
70. Windows CI
71. Browser CI
72. npm Audit
73. Files Changed
74. Acceptance Registry
75. Implementation Commit
76. Implementation CI
77. Failed Candidates
78. Completion Record
79. Queue Archive
80. Queue State
81. Phase 11-4 Gate
82. Final Repository State

---

# 141. Mandatory Result Markers

必须：

```text
PHASE11_3_NEW_SCIENTIFIC_TOOLS = 0

PHASE11_3_NEW_SCIENTIFIC_ALGORITHMS = 0

PHASE11_3_NEW_ARTIFACT_FAMILIES = 0

PHASE11_3_NEW_DATAPROFILE_VERSION = 0

PHASE11_3_NEW_ANALYSISPLAN_VERSION = 0

PHASE11_3_NEW_DATABASE_MIGRATIONS = 0

PHASE11_3_NEW_PUBLIC_API_FAMILIES = 0

PHASE11_3_NEW_DEPENDENCIES = 0

PHASE11_3_NEW_LLM_CALL_SITES = 0

PHASE11_3_REAL_LLM_CALLS = 0

PHASE11_3_EXTERNAL_REFERENCE_DOWNLOADS = 0

PHASE11_3_EXTERNAL_SCIENTIFIC_API_CALLS = 0

PHASE11_3_REFERENCE_FIXTURE_MUTATIONS = 0

PHASE11_3_EXPECTED_VALUE_MUTATIONS = 0

PHASE11_3_SCIENTIFIC_TOLERANCE_CHANGES = 0
```

---

# 142. Platform Markers

必须：

```text
SCIENTIFIC_PLATFORM_LINUX = VERIFIED

SCIENTIFIC_PLATFORM_WINDOWS = VERIFIED
```

仅在真实执行成功时才能写。

macOS：

```text
SCIENTIFIC_PLATFORM_MACOS =
NOT_CURRENT_RELEASE_TARGET
```

除非 Entry Gate真实证明其它 policy。

---

# 143. Variance Markers

必须报告：

```text
EXACT_COUNT = <actual>

TOLERANCE_BOUNDED_COUNT = <actual>

DISPLAY_ONLY_VARIANCE_COUNT = <actual>

UNSUPPORTED_PLATFORM_COUNT = <actual>

KNOWN_LIMITATION_COUNT = <actual>

UNCLASSIFIED_VARIANCE_COUNT = 0
```

不能提前填数字。

---

# 144. Baseline Markers

必须：

```text
REGISTRY_BEFORE_11_3 = 62
REGISTRY_AFTER_11_3 = 62

DATAPROFILE_BEFORE_11_3 = 2.4
DATAPROFILE_AFTER_11_3 = 2.4

MIGRATION_BEFORE_11_3 =
0007_phase10m1_workspace_domain

MIGRATION_AFTER_11_3 =
0007_phase10m1_workspace_domain
```

---

# 145. PASS Gate

只有全部满足：

```text
Phase 11-2 PASS

Phase 11-2 queue archived

Phase 11-2 implementation CI PASS

golden reproducibility handoff valid


HEAD == origin/master at entry

worktree clean


Registry = 62

DataProfile = 2.4

migration = 0007


same locked repository authority
on Linux and Windows


all required Linux cases executed

all required Windows cases executed

required scientific skips = 0


Linux independently passes sealed reference

Windows independently passes sealed reference


all cross-platform differences classified

unclassified variance = 0


all exact identity requirements PASS

all unit requirements PASS

all deterministic requirements PASS


no required scientific result exceeds
sealed variance/reference tolerance


no new unexplained platform classification divergence


browser:
Chromium PASS
Firefox PASS
WebKit PASS
390x844 PASS


frontend scientific recomputation = 0

screenshot numeric authority = none


V4 promotions only from eligible V3 Tools

V2→V4 shortcut = 0

bulk domain V4 promotions = 0


Phase 11-4 handoff complete

critical TBD = 0


production scientific changes = 0

scientific algorithm changes = 0

reference mutations = 0

expected-value mutations = 0

tolerance changes = 0

Registry changes = 0

DataProfile changes = 0

migration changes = 0

dependency changes = 0

lockfile changes = 0

real LLM calls = 0


backend >= dynamic Phase 11-2 floor

frontend >= dynamic Phase 11-2 floor

service >= dynamic Phase 11-2 floor

service skipped = 0

service failed = 0

service errors = 0


typecheck PASS

build PASS

lock PASS

evidence PASS

docs links PASS

security PASS

secret scan PASS


P11V3 acceptance = 10/10


implementation exact-SHA CI PASS
including required Linux and Windows jobs

completion record committed/pushed

queue archive committed/pushed


TASK_BLOCK_COUNT = 0

Phase 11-4 task absent

Phase 12 task absent

Phase 13 task absent
```

才能：

```text
Phase 11-3 = PASS
```

---

# 146. BLOCKED — Cross-Platform Scientific Failure

如果：

```text
Linux passes reference
Windows fails reference
```

或相反：

必须：

```text
Phase 11-3:
BLOCKED /
CROSS_PLATFORM_SCIENTIFIC_REPRODUCIBILITY_FAILURE
```

不得继续到 Phase 11-4。

---

# 147. BLOCKED — Linux Baseline Drift

如果同：

```text
Tool/version
fixture
reference
lock
```

下：

11-3 Linux不能重现 11-2 science：

必须：

```text
BLOCKED /
LINUX_BASELINE_DRIFT
```

先查：

```text
environment
determinism
evidence integrity
```

不得以 Windows 为由掩盖。

---

# 148. BLOCKED — Windows Locked Environment

如果 Windows无法建立 current locked environment：

必须：

```text
BLOCKED /
WINDOWS_LOCKED_ENVIRONMENT_UNAVAILABLE
```

若仅 CI harness问题：

允许 fix-forward。

若依赖本身不支持 current release target：

reviewer decision。

---

# 149. BLOCKED — Scientific Variance

如果 Linux/Windows都 pass reference，但：

```text
cross-platform delta
>
sealed variance tolerance
```

必须：

```text
BLOCKED /
CROSS_PLATFORM_VARIANCE_EXCEEDS_POLICY
```

除非已有 exact governance允许 KNOWN_LIMITATION。

不得新建 limitation逃避。

---

# 150. BLOCKED — Scientific Classification Flip

如果：

```text
direct ↔ indirect

metal-like ↔ nonzero-gap

ballistic reject ↔ accepted diffusion

matched ↔ unmatched XRD

complete ↔ partial projection
```

等 scientific classification 跨平台翻转：

默认：

```text
BLOCKED
```

除非 sealed tolerance/threshold contract明确允许。

---

# 151. BLOCKED — Identity Difference

如果同 benchmark：

```text
site

atom

frame

q-point

band

spin

Artifact source
```

identity跨平台不同：

不能标：

```text
TOLERANCE_BOUNDED
```

必须：

```text
FAIL_IDENTITY
```

---

# 152. BLOCKED — Hidden Production Fix Required

如果要 PASS 必须：

```text
change scientific formula

change algorithm

change default

change threshold

change unit semantics

change scientific sorting authority

change Adapter science
```

必须停止。

11-3 不拥有 scientific correction authority。

---

# 153. Non-Blockers

通常不阻塞：

```text
browser antialiasing difference

font rasterization difference

WebGL pixel difference

non-semantic timing difference

different temp path

different runner hostname

different package wheel filename
with same locked semantic version

different runtime timestamps

known approved display-only variance
```

必须明确分类。

---

# 154. First Required Output

开始执行后第一步输出：

```text
Phase 11-3 Entry Gate
+ Phase 11-2 Golden Benchmark Handoff
+ Linux / Windows Reproducibility Admission Matrix
```

至少确认：

1. 11-2 implementation SHA；
2. 11-2 implementation CI；
3. 11-2 completion SHA；
4. 11-2 queue archive SHA；
5. 11-2 final PASS；
6. HEAD / origin / branch / worktree；
7. Registry 62；
8. DataProfile 2.4；
9. migration 0007；
10. TASK_BLOCK_COUNT=0；
11. 11-4 task absent；
12. Golden suite ID/hash；
13. Validation levels after 11-2；
14. Phase11_3ReproducibilityInputManifest；
15. required cross-platform case count；
16. blocked case count；
17. Linux CI target；
18. Windows target；
19. lock hash；
20. Python version policy；
21. scientific dependency identities；
22. tolerance variance relevance；
23. browser matrix；
24. macOS not-current-target status；
25. no new dependency required；
26. no production scientific change required。

成功才输出：

```text
PHASE_11_3_ENTRY_GATE = PASS

PHASE_11_2_REVIEWER_DEPENDENCY = VERIFIED

PHASE_11_3_QUEUE_ADMISSION = AUTHORIZED

PHASE_11_3_LINUX_SCIENTIFIC_REPLAY = AUTHORIZED

PHASE_11_3_WINDOWS_SCIENTIFIC_REPRODUCIBILITY = AUTHORIZED

PHASE_11_3_VARIANCE_CHARACTERIZATION = AUTHORIZED

PHASE_11_3_V4_PROMOTION_AUTHORITY =
BOUNDED_BY_EXISTING_VALIDATION_POLICY

PHASE_11_3_PRODUCTION_SCIENCE_CHANGE_AUTHORITY = NONE

PHASE_11_3_READINESS =
READY_FOR_CROSS_PLATFORM_REPRODUCIBILITY
```

---

# 155. Required Execution Sequence

严格：

```text
verify Phase 11-2 lifecycle

→ verify 11-3 handoff

→ verify Linux/Windows target environment

→ verify same lock authority

→ admit exactly one Phase 11-3 task

→ snapshot validation levels before

→ snapshot environment identities

→ rerun sealed scientific cases on Linux

→ compare Linux against reference

→ compare Linux against 11-2 baseline

→ run same sealed scientific cases on Windows

→ compare Windows against same reference

→ compare Linux vs Windows

→ classify every variance

→ run deterministic replay

→ audit identity/unit/order/tie/NaN/locale/timezone variance

→ run browser presentation invariants

→ run service-backed regression

→ calculate permitted V3→V4 transitions

→ generate Phase 11-4 honest-coverage input handoff

→ run complete regression/security/evidence validation

→ create implementation commit

→ push

→ wait for implementation exact-SHA CI
   including required Linux + Windows jobs

→ if PASS:
   append Phase 11-3 completion result

→ commit/push completion record

→ archive only Phase 11-3 task

→ commit/push queue archive

→ stop

→ return complete Phase 11-3 result
```

---

# 156. Stop Rule

完成 11-3 后不得：

```text
publish final honest capability coverage

change input support verdicts

execute Phase 11-4

close Phase 11

execute Phase 11-5

start Phase 12 UI/UX redesign
```

必须停在：

```text
Phase 11-4:
REVIEWER_GATE / AWAITING REVIEWER PROMPT
```

等待 reviewer。


---END---
