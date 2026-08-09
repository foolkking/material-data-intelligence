---TASK---
 状态：处理中
# Phase 11-1 Reviewer Prompt

# Reference Provenance + Safe Fixture Consolidation

你现在执行：

# Phase 11-1：Reference Provenance + Safe Fixture Consolidation

中文：

# 参考来源溯源 + 安全验证基准固化

本阶段属于：

```text
Phase 11:
Scientific Validation,
Reference Provenance,
Reproducibility
& Honest Coverage
```

Phase 11-1 是 Phase 11-0 已封板 Validation Governance 的第一项执行阶段。

本阶段不是：

```text
numeric benchmark phase
scientific algorithm implementation phase
cross-platform variance phase
honest coverage finalization phase
UI/UX phase
release phase
```

本阶段唯一核心职责：

```text
Phase 11-0 exact validation gaps/backlog

→ resolve approved official/static reference provenance

→ resolve source identity/version

→ resolve license/redistribution disposition

→ acquire only reviewer-approved static sources where authorized

→ compute source checksum

→ retain source only when allowed

→ deterministically extract/normalize bounded fixture material

→ record complete transformation provenance

→ assign immutable fixture identity/version/hash

→ classify reference independence

→ prepare exact Phase 11-2 benchmark inputs

→ DO NOT declare numeric scientific PASS
```

---

# 0. Reviewer Authorization

正式批准：

```text
PHASE_11_0_RESULT = APPROVED

PHASE_11_1_QUEUE_ADMISSION = AUTHORIZED

AUTHORIZED_PHASE = Phase 11-1

MAX_PHASES_EXECUTED = 1
```

本 Prompt 只授权 Phase 11-1。

不得创建、排队或执行：

```text
Phase 11-2
Phase 11-3
Phase 11-4
Phase 11-5
Phase 12
Phase 13
```

---

# 1. Phase 11-0 Authoritative Baseline

Phase 11-0 implementation：

```text
312fd4445d404f0f89c061fbdc055789912dc552
```

唯一 blocking implementation CI：

```text
31324356338
PASS
```

Phase 11-0 completion record：

```text
dee197d39e194277351a34fcd063b3de97729534
```

Phase 11-0 queue archive：

```text
ef40ade537820e88bbe2d259a9b4ccb9cd04ac1c
```

当前 lifecycle policy：

```text
Implementation exact-SHA CI
= BLOCKING CI GATE

Completion-record commit
= direct push after implementation CI PASS

Queue-archive commit
= direct push after completion record

NO ADDITIONAL WAIT REQUIRED
for completion/archive CI
```

不得把 completion/archive 两个 commit 描述成：

```text
VERIFIED_BY_EXACT_SHA_CI
```

除非 repository 中确实存在相应成功 CI 事实。

---

# 2. Required Entry Baseline

Phase 11-1 开始前必须验证：

```text
branch = master

HEAD =
ef40ade537820e88bbe2d259a9b4ccb9cd04ac1c

origin/master =
ef40ade537820e88bbe2d259a9b4ccb9cd04ac1c

worktree = clean
```

并验证：

```text
Registry count = 62

DataProfile = 2.4

migration head =
0007_phase10m1_workspace_domain

TASK_BLOCK_COUNT = 0

PHASE_11_2_EXECUTABLE_TASK_CREATED = NO

PHASE_12_EXECUTABLE_TASK_CREATED = NO

PHASE_13_EXECUTABLE_TASK_CREATED = NO
```

如果 actual immutable Git 与 Prompt 中的 archive SHA 不一致：

必须先确认：

```text
whether the difference is only
post-archive documentation history
```

如果 current HEAD 包含未审核 production changes：

```text
BLOCKED / REVIEWER_REQUIRED
```

不得静默继续。

---

# 3. Phase 11-0 Validation Reality

11-0 已经冻结：

```text
Registry Tools = 62

V2 CONTROLLED_REFERENCE_VERIFIED-ish baseline rows = 28
V1 RUNTIME_AND_ARTIFACT_VERIFIED rows = 34

V3 promotions by 11-0 = 0
V4 promotions by 11-0 = 0
```

注意：

上述 `V2` 必须使用 repository 中 Phase 11-0 对 Level V2 的 exact 定义。

不得自行提升或重命名。

当前 retained inventories：

```text
reference-like records = 43

fixture records = 169

official/example records = 54

validation gaps = 12

P0 gaps = 0
```

不得为了让 11-1 “显得完成更多”：

```text
increase validation level
decrease gap severity
declare new DIRECT_VERIFIED
declare new numeric scientific PASS
```

---

# 4. Phase 11-0 Input Reality Must Remain Frozen

当前已审计：

```text
DIRECT_SUPPORTED:
CSV
CIF
POSCAR

SUPPORTED_WITH_LIMITS:
canonical JSON
XYZ / EXTXYZ
volumetric
ZIP
supplied electronic JSON

MAPPING_ONLY:
phonon direct upload

UNSUPPORTED:
XLSX
Parquet
LAMMPS trajectory
```

Phase 11-1 不负责增加格式支持。

因此：

```text
INPUT_SUPPORT_CHANGES = 0
```

不得因为找到一个 official example：

```text
MAPPING_ONLY → DIRECT_SUPPORTED
```

也不得：

```text
UNSUPPORTED → SUPPORTED
```

这类变化不是 reference-provenance 权限。

---

# 5. Phase 11-1 Core Source of Truth

开始执行前必须读取 current repository 中：

```text
docs/phase11/phase11_0_validation_baseline_reconciliation.md

docs/phase11/phase11_validation_governance.md

docs/phase11/phase11_tool_validation_matrix.md

docs/phase11/phase11_input_support_matrix.md

docs/phase11/phase11_reference_evidence_inventory.md

docs/phase11/phase11_reference_provenance_policy.md

docs/phase11/phase11_validation_level_policy.md

docs/phase11/phase11_tolerance_registry.md

docs/phase11/phase11_variance_and_reproducibility_policy.md

docs/phase11/phase11_revalidation_trigger_policy.md

docs/phase11/phase11_gap_matrix.md

docs/phase11/phase11_implementation_backlog.md

docs/phase11/phase11_acceptance_and_test_plan.md

docs/phase11/phase11_execution_lock.md

docs/phase11/phase11_execution_manifest.md

docs/phase11/phase11_1_next_scope.md
```

以及：

```text
docs/phase11/evidence/
phase11_0_validation_baseline_reconciliation/
```

中的 structured inventories。

Phase 11-1 backlog 只能来自这些 current canonical records。

---

# 6. No Reviewer Guessing

禁止执行 Agent：

```text
invent new 11-1 reference targets

pick famous datasets because they look useful

download additional papers/examples opportunistically

expand from one official example to an entire repository

replace a sealed source with another source because it looks better
```

原则：

```text
11-0 BACKLOG
IS THE ADMISSION LIST
```

如果发现新的潜在 reference：

只能：

```text
record as CANDIDATE_FOR_REVIEW
```

不能加入本阶段 authoritative fixture closure。

---

# 7. Phase 11-1 Exact Mission

对 11-0 标记为需要 11-1 的每一个 gap/backlog item：

必须完成：

```text
source identity

source type

publisher/project/library

exact version/release

exact source location

retrieval disposition

license disposition

redistribution disposition

original checksum

source-byte retention decision

normalization requirement

transformation procedure

transformation version

normalized checksum

fixture identity

fixture version

expected reference content provenance

reference independence classification

11-2 benchmark linkage

evidence manifest membership
```

不得只写：

```text
downloaded
```

或：

```text
reference found
```

---

# 8. Approved Reference Taxonomy

严格使用 Phase 11-0 已封板 taxonomy：

```text
ANALYTIC_REFERENCE

OFFICIAL_LIBRARY_REFERENCE

OFFICIAL_PROJECT_EXAMPLE

INDEPENDENT_CROSS_LIBRARY_REFERENCE

CONTROLLED_SYNTHETIC_REFERENCE

REPOSITORY_INTERNAL_EXPECTED_VALUE

MAPPING_ONLY

NO_REFERENCE
```

不得临时添加：

```text
TRUSTED_REFERENCE
GOOD_REFERENCE
MANUAL_REFERENCE
WEB_REFERENCE
```

这种模糊类别。

如确有 contract requirement：

先更新 Phase 11 governance，并必须证明与已有 taxonomy 完全兼容。

---

# 9. Reference Strength Ordering

继续执行：

```text
1. ANALYTIC / MATHEMATICAL TRUTH

2. OFFICIAL LIBRARY / SPECIFICATION REFERENCE

3. INDEPENDENT CROSS-LIBRARY REFERENCE

4. OFFICIAL-DERIVED REVIEWED FIXTURE

5. CONTROLLED SYNTHETIC FIXTURE

6. INTERNAL REGRESSION EXPECTATION

7. MAPPING-ONLY EVIDENCE
```

这只是：

```text
validation-strength ordering
```

不是：

```text
automatic PASS ordering
```

11-1 只准备 reference authority。

---

# 10. Static External Acquisition Authorization

Phase 11-1 与 11-0 不同。

本阶段允许：

```text
STATIC_EXTERNAL_REFERENCE_ACQUISITION = YES
```

但只允许：

```text
exact official/static sources
already sealed in Phase 11-0 backlog
```

允许来源：

```text
official project documentation

official project repository static file

official release asset

official library documentation

official specification

reviewer-sealed independent reference source
```

---

# 11. External Acquisition Is NOT Open Research

禁止：

```text
general web research to find alternatives

search engine result used as authority

random GitHub repository substitution

blog post as scientific authority

forum answer as scientific authority

Stack Overflow as numeric reference

Reddit as numeric reference

LLM-generated expected values

AI search summary as source

package README snippet from an unpinned branch
```

如果 sealed source失效：

```text
SOURCE_UNAVAILABLE
```

不要擅自寻找替代 source。

---

# 12. Redirect Policy

如果 official URL发生 redirect：

仅当满足：

```text
same official publisher/project

same source identity

same pinned release/version

same content semantics
```

可以跟随。

必须记录：

```text
requested URL

resolved URL

redirect chain

retrieval timestamp

content checksum
```

如果 redirect 指向：

```text
latest
main
master
nightly
```

且无法证明与 sealed version一致：

```text
SOURCE_VERSION_UNRESOLVED
```

不得继续形成 authoritative fixture。

---

# 13. Version Pinning

禁止使用浮动 reference：

```text
latest docs
main branch
master branch
current example
latest release
```

除非：

```text
the source itself is version-independent specification
```

并在 provenance 中明确解释。

普通 library/project reference 必须 pin：

```text
release
tag
commit
documentation version
dataset version
or immutable published identifier
```

---

# 14. Original Source Checksum

每个 acquired source必须至少：

```text
SHA-256
```

记录：

```text
sourceChecksumAlgorithm = SHA-256
sourceChecksum
sourceByteLength
```

如果 official publisher提供自己的 checksum：

必须同时记录：

```text
publisherChecksum
publisherChecksumAlgorithm
```

并检查。

不得用：

```text
filename
URL
ETag alone
Last-Modified alone
```

作为内容 identity。

---

# 15. Source Retention Policy

下载到本地：

不等于：

```text
can commit to repository
```

每个 source必须分类：

```text
VENDOR_ALLOWED

DERIVED_ONLY_ALLOWED

REFERENCE_ONLY

LICENSE_REVIEW_REQUIRED

REDISTRIBUTION_PROHIBITED_OR_UNCLEAR
```

名字可使用 Phase 11-0 当前 exact canonical equivalent。

---

# 16. Unknown License Rule

如果 license 未知或不清楚：

禁止：

```text
commit raw source bytes
```

允许保留：

```text
source metadata

official URL

version

published checksum

retrieval checksum if legitimately obtained

transformation intent

license status
```

并标记：

```text
LICENSE_REVIEW_REQUIRED
```

不得：

```text
assume GitHub public == redistributable

assume documentation visible == fixture vendoring permitted
```

---

# 17. License Is Not Scientific Authority

必须保持：

```text
LICENSE_STATUS
```

与：

```text
SCIENTIFIC_REFERENCE_STATUS
```

分离。

一个 scientifically authoritative source：

可能：

```text
REFERENCE_ONLY
```

一个 permissively licensed fixture：

也不自动变：

```text
INDEPENDENT_REFERENCE
```

---

# 18. Raw Source Retention

如果 license允许：

建议保存 immutable original：

```text
original/
```

但具体路径必须服从 repository current fixture/evidence convention。

不得为了 Phase 11-1 建立第二套平行 fixture authority。

原则：

```text
REUSE_CANONICAL_FIXTURE_ROOT
```

---

# 19. Do Not Duplicate Existing Raw Sources

如果同 exact checksum 的 source 已存在：

```text
DO_NOT_COPY_AGAIN
```

而应：

```text
reference existing immutable source
```

并建立：

```text
reuse relationship
```

不得把：

```text
same source duplicated 3 times
```

当作三个 reference。

---

# 20. Safe Fixture Transformation

允许 transformation 仅限：

```text
bounded deterministic extraction

line-ending normalization

encoding normalization

stable JSON serialization

stable CSV extraction

stable table subset extraction

metadata removal when irrelevant

ordering normalization where scientifically irrelevant
and contractually approved

unit canonicalization
ONLY when formally specified and logged
```

---

# 21. Forbidden Fixture Transformation

绝对禁止：

```text
change numbers until test passes

remove mismatching rows

drop outliers because platform disagrees

round values to hide error

change units without explicit conversion provenance

rescale curves to resemble current platform output

relabel peaks manually to make matching easier

rewrite band gap

rewrite coordination values

change diffusion window

alter geometry

change source spin/channel semantics
```

---

# 22. Transformation Must Be Reproducible

每一个 normalized fixture必须能回答：

```text
Which exact source bytes produced it?

Which exact transformation produced it?

Which tool/script version performed transformation?

What fields were removed?

What fields were retained?

Were any numbers changed?

Were units changed?

Why?

What is the normalized checksum?
```

---

# 23. Transformation Tooling Boundary

允许新增：

```text
deterministic fixture extraction tooling

fixture manifest validators

checksum validators

provenance validators
```

但必须：

```text
NO_SCIENTIFIC_COMPUTATION_AUTHORITY
```

不得：

```text
implement CrystalNN

compute XRD

compute MSD

compute diffusion

compute band gaps

compute DOS

compute phonon physics

compute new scientific expected result
```

Phase 11-1 工具只能整理 source/reference。

---

# 24. Downloaded Code Execution

必须：

```text
DOWNLOADED_SCRIPT_EXECUTION = 0

DOWNLOADED_NOTEBOOK_EXECUTION = 0

DOWNLOADED_BINARY_EXECUTION = 0

EXTERNAL_BUILD_SYSTEM_EXECUTION = 0
```

即使 official repository 自带：

```text
example.py
notebook.ipynb
build.sh
```

也不能执行。

可以读取其静态数据/文档：

前提是它已在 11-0 backlog 中获批。

---

# 25. External Scientific API

必须：

```text
EXTERNAL_SCIENTIFIC_API_CALLS = 0
```

不能：

```text
query Materials Project API

query external DFT service

query remote XRD calculator

query remote structure analysis service
```

来生成 expected values。

---

# 26. LLM Boundary

必须：

```text
NEW_LLM_CALL_SITES = 0

PHASE11_1_REQUIRES_LLM = NO

REAL_LLM_CALLS = 0
```

禁止使用 LLM：

```text
extract numeric truth

infer missing units

reconstruct reference data

guess license

guess source version

fill missing expected values
```

---

# 27. Self-Reference Audit

如果：

```text
platform Tool
uses library X
```

而 expected fixture：

```text
was also generated directly by library X
```

必须标记：

```text
SELF_REFERENCE
```

它可以用于：

```text
regression

serialization

integration

determinism
```

但不能升级成：

```text
INDEPENDENT_CROSS_LIBRARY_REFERENCE
```

---

# 28. Independent Reference Audit

若 sealed backlog 声明：

```text
INDEPENDENT_CROSS_LIBRARY_REFERENCE
```

必须证明：

```text
independent implementation

independent scientific path

semantic comparability

same units or explicit conversion

same quantity definition

same boundary conditions
```

不能因为：

```text
two packages expose similarly named functions
```

就称 independent validation。

---

# 29. Different Algorithms Must Stay Different

特别禁止：

```text
CrystalNN == VoronoiNN
```

作为 validation reference。

二者是不同 algorithmic authorities。

11-1 可准备各自 source/reference。

不得：

```text
choose one as truth for the other
```

---

# 30. Scientific Scope Families

必须依据 11-0 exact backlog处理 reference gaps，可能涉及：

```text
Material Intelligence

Materials ML

Composition Space

Structure

CrystalNN

VoronoiNN

Local Environment / Polyhedra

Experimental XRD

Trajectory RDF

Trajectory MSD

Trajectory Diffusion

Phonon

Brillouin Zone

Volumetric

Electronic Band Structure

Electronic DOS
```

但：

```text
not every family necessarily requires new 11-1 acquisition
```

只处理 backlog 中明确列出的条目。

---

# 31. N1 Reference Preparation

若 11-0 backlog包含 N1 reference gaps：

必须分别处理：

```text
CrystalNN

VoronoiNN
```

至少记录：

```text
algorithm/version source

reference structure identity

site identity

neighbor semantics

weight semantics

coordination semantics

distance semantics

parameter semantics
```

不得做 N1 numeric PASS。

---

# 32. N2 Reference Preparation

若 backlog要求：

必须准备：

```text
local-environment classification source

polyhedron geometry source

ConvexHull/reference geometry source

periodic identity fixture

distortion reference
```

但：

```text
N2 may not independently regenerate N1 neighbors
```

11-1 fixture 必须保留 N1 dependency provenance。

---

# 33. N3 Reference Preparation

若 backlog要求：

准备：

```text
experimental pattern source

peak source

theoretical-pattern source identity

wavelength

2theta units

matching reference cases

zero-match source

tie/competing case
```

不得：

```text
declare phase identified

perform Rietveld

perform refinement
```

11-1 只是 reference packaging。

---

# 34. N4 Reference Preparation

若 backlog要求：

准备：

```text
boundary-crossing trajectory

random-walk reference

ballistic reference

known-time trajectory

RDF analytic/control reference

MSD analytic/control reference

diffusion expected-source reference
```

如果 expected diffusion value来自 analytic construction：

必须清楚记录：

```text
ANALYTIC_REFERENCE
```

但平台计算与 expected 的 comparison PASS：

留给 11-2。

---

# 35. N5 Reference Preparation

若 backlog要求：

准备：

```text
supplied band fixture

direct-gap fixture

indirect-gap fixture

metal-like threshold control

spin-resolved fixture

DOS fixture

partial/complete PDOS fixture

Band+DOS compatibility fixture
```

必须明确：

```text
REFERENCE VALIDATES SUPPLIED ELECTRONIC DATA HANDLING

NOT PLATFORM DFT
```

不得通过 11-1引入：

```text
DFT calculation
GW
Fermi surface
projected bands
```

---

# 36. Earlier Initial-Release Science

11-1 不得只关注 N1-N5。

必须按 11-0 exact gaps检查：

```text
dataset statistics

Materials ML metrics

PCA

KMeans

static RDF

theoretical XRD

phonon

Brillouin zone

volumetric
```

是否存在 reference/provenance backlog。

仅处理被列入 11-1 的条目。

---

# 37. Official Examples

11-0 已索引 54 个 official/example records。

11-1 不得：

```text
process all 54 by default
```

只处理：

```text
11-0 current status
=
EXTRACTION_REQUIRED
or exact 11-1 backlog dependency
```

其它：

```text
MAPPING_ONLY
CURRENTLY_RELEVANT
SUPERSEDED
RETAINED_HISTORICAL
```

保持原状态，除非 sealed backlog明确要求。

---

# 38. Official Example Does Not Mean Verified

必须继续：

```text
OFFICIAL_EXAMPLE_EXISTS
!=
REFERENCE_VERIFIED
```

即使 official example 成功转成 fixture：

本阶段也只能得到类似：

```text
REFERENCE_SOURCE_READY
FIXTURE_READY_FOR_BENCHMARK
```

不能得到：

```text
TOOL_VALIDATED
```

---

# 39. Numeric Scientific PASS Is Prohibited

这是 Phase 11-1 最大边界。

必须：

```text
PHASE11_1_NUMERIC_SCIENTIFIC_PASS_DECLARATIONS = 0
```

禁止：

```text
expected = 1.23
platform = 1.23
therefore PASS
```

即使顺手能比较：

也不能把它作为 Phase 11-1 acceptance authority。

比较属于：

```text
Phase 11-2
```

---

# 40. No Validation-Level Promotion

必须：

```text
PHASE11_1_TOOL_VALIDATION_LEVEL_PROMOTIONS = 0
```

因此：

```text
V1 rows remain V1

V2 rows remain V2

V3 count does not increase because of 11-1 alone

V4 count does not increase
```

11-1 可以增加：

```text
REFERENCE_READY
```

状态，但不能直接改变 final validation level。

---

# 41. No Honest Coverage Promotion

Phase 11-4 才发布 final honest coverage。

因此 11-1 禁止：

```text
MAPPING_ONLY → DIRECT_VERIFIED

EXTRACTION_REQUIRED → DIRECT_VERIFIED

OFFICIAL example → OFFICIAL_DERIVED_VERIFIED
```

仅因 fixture 已准备好。

允许：

```text
EXTRACTION_REQUIRED
→ REFERENCE_PREPARED_FOR_11_2
```

或 repository sealed equivalent。

---

# 42. Canonical Reference Record

每个 reference record 至少：

```text
referenceId

referenceVersion

referenceType

scientificCapability

toolIds

toolVersions

sourcePublisher

sourceProject

sourceVersion

sourceLocation

sourceImmutableIdentity

retrievedAt

sourceChecksumAlgorithm

sourceChecksum

sourceBytes

publisherChecksum

licenseIdentifier

licenseEvidence

redistributionDisposition

rawRetentionDisposition

referenceIndependence

selfReference

expectedContentDescription

unitSemantics

transformationIds

fixtureIds

phase11GapIds

phase11_2BenchmarkIds

reviewStatus
```

不得包含：

```text
numeric PASS result
```

---

# 43. Canonical Fixture Record

每个 fixture 至少：

```text
fixtureId

fixtureVersion

scientificCapability

referenceId

sourceChecksum

normalizedChecksum

filePath

mediaType

encoding

byteSize

schema/format

units

expectedContentOrigin

transformationId

immutable

redistributionDisposition

tool/version applicability

11-2 benchmark target

reviewStatus
```

---

# 44. Fixture Identity

Fixture identity不得只使用：

```text
filename
```

必须结合：

```text
fixtureId
fixtureVersion
normalizedChecksum
```

如果 fixture 内容变：

必须：

```text
new version
```

不得覆盖原 fixture。

---

# 45. Immutable Fixture Policy

继续冻结：

```text
AUTHORITATIVE_FIXTURE_IN_PLACE_OVERWRITE = PROHIBITED
```

以下变化要求新版本：

```text
source changed

transformation changed

scientific values changed

unit semantics changed

schema changed

ordering meaning changed

expected content changed
```

---

# 46. Existing 169 Fixtures Must Not Be Rewritten

默认：

```text
EXISTING_FIXTURE_REWRITE_COUNT = 0
```

若一个现有 fixture 被发现 provenance 不完整：

优先：

```text
add provenance sidecar
```

而不是重写 fixture bytes。

只有 unavoidable normalization correction 且 governance允许时：

```text
new fixture version
```

---

# 47. Transformation Registry

建立 canonical：

```text
Phase11TransformationRegistry
```

至少：

```text
transformationId

transformationVersion

inputReferenceId

inputChecksum

operationClass

operations

numericMutation

unitMutation

orderingMutation

removedFields

retainedFields

tool/script identity

scriptChecksum

outputFixtureId

outputChecksum

deterministicReplayStatus
```

必须：

```text
numericMutation = false
```

除非 unit canonicalization 已在 11-0 exact policy中明确允许。

---

# 48. Unit Conversion Rule

如果 transformation涉及单位：

必须有：

```text
source unit

target unit

formal conversion equation

conversion authority

conversion version

conversion exactness/tolerance

original values retained or recoverable
```

如果 source unit不明确：

```text
UNIT_SEMANTICS_UNRESOLVED
```

不得猜。

---

# 49. Unit Unknown Means No Fixture Authority

禁止：

```text
looks like eV
looks like angstrom
probably ps
```

未知 unit：

```text
BLOCK_REFERENCE_FOR_NUMERIC_USE
```

可保留 source metadata。

但不能进入 11-2 numeric benchmark ready set。

---

# 50. Missing Source Version

如果 source存在但 version无法确认：

标记：

```text
SOURCE_VERSION_UNRESOLVED
```

如果该 item：

```text
BLOCKING_11_2 = YES
```

则 Phase 11-1 不能 PASS。

---

# 51. Source Unavailable

如果 exact source无法获取：

必须保留：

```text
source identity

attempted official location

failure mode

date

whether historical checksum exists

whether alternative retained repository fixture exists
```

不得自行使用替代 source。

结果：

```text
SOURCE_UNAVAILABLE
```

---

# 52. Source Changed Upstream

如果同 official URL：

当前内容 hash 与 retained/history 不同：

必须：

```text
DO_NOT_REPLACE_EXISTING_AUTHORITY
```

记录：

```text
UPSTREAM_CONTENT_CHANGED
```

并尝试通过：

```text
exact tagged/released immutable source
```

解决。

如果不能：

```text
REVIEWER_REQUIRED
```

针对 blocking reference。

---

# 53. Reference Independence Matrix

建立：

```text
ReferenceIndependenceMatrix
```

每项至少：

```text
referenceId

platform computation authority

reference computation authority

same implementation?

same library?

same algorithm?

shared dependency?

analytic truth?

independence verdict

limitations
```

允许 verdict：

```text
INDEPENDENT

PARTIALLY_INDEPENDENT

SELF_REFERENCE

ANALYTIC

NOT_APPLICABLE

UNRESOLVED
```

或 11-0 existing canonical equivalents。

---

# 54. Duplicate Reference Detection

必须按：

```text
content checksum
+
source identity
+
version
```

检测：

```text
duplicate reference
```

不得按 filename判断。

输出：

```text
DUPLICATED_REFERENCE_BYTES

SAME_REFERENCE_REUSED

DISTINCT_REFERENCE
```

---

# 55. 11-2 Handoff Contract

11-1 最关键交付是：

```text
Phase11_2BenchmarkInputManifest
```

它不是 production contract。

是 evidence/planning artifact。

每条 benchmark dependency必须包含：

```text
benchmarkId

gapId

toolId

toolVersion

referenceId

fixtureId

fixtureVersion

fixtureChecksum

expected content source

units

toleranceId

positive/negative case role

reference strength

independence

11-2 readiness

blocking reason
```

---

# 56. 11-2 Readiness States

必须严格：

```text
READY_FOR_11_2

READY_WITH_REFERENCE_LIMITATION

BLOCKED_SOURCE_UNAVAILABLE

BLOCKED_LICENSE

BLOCKED_VERSION

BLOCKED_UNIT_SEMANTICS

BLOCKED_PROVENANCE

NOT_REQUIRED_FOR_11_2
```

名称可遵从已封板 canonical equivalents。

不得只写：

```text
TODO
```

---

# 57. No TBD Handoff

要求：

```text
IMPLEMENTATION_CRITICAL_TBD = 0
```

对于每个 11-2 benchmark：

要么：

```text
READY
```

要么：

```text
typed BLOCKED reason
```

不得把：

```text
find reference later
```

交给 11-2 execution agent。

---

# 58. Blocking Rule

如果 11-0 backlog 标记：

```text
BLOCKING_11_2 = YES
```

的 reference无法完成：

Phase 11-1：

```text
BLOCKED / REVIEWER_REQUIRED
```

不得 PASS 后把问题推给 11-2。

对于：

```text
non-release-critical
supporting P2
```

如果 11-0 governance允许 deferred：

可保留 typed unresolved。

但必须证明：

```text
does not block sealed 11-2 benchmark acceptance
```

---

# 59. P0/P1/P2 Integrity

11-0：

```text
P0 = 0
```

11-1 不得为了方便：

```text
downgrade P1 → P2
```

也不得：

```text
upgrade P2 → P0
```

除非发现新事实。

如果出现真正 release-critical source/provenance contradiction：

允许新增：

```text
P0
```

但必须：

```text
BLOCKED / REVIEWER_REQUIRED
```

并记录证据。

---

# 60. Reference Preparation ≠ Scientific Correction

如果 reference source 与当前 platform scientific result明显矛盾：

11-1 不能：

```text
change platform

change expected result

change tolerance
```

必须记录：

```text
POTENTIAL_SCIENTIFIC_DISCREPANCY
```

并：

```text
BLOCKED / REVIEWER_REQUIRED
```

如果只是还没有正式比较：

留给 11-2。

---

# 61. Tolerance Freeze

11-1 不重新设计 tolerances。

继续使用 11-0：

```text
Phase11ToleranceRegistry
```

必须：

```text
TOLERANCE_CHANGES = 0
```

除非只是补：

```text
source provenance metadata
```

且不改变 numeric acceptance。

---

# 62. Pass-Driven Tolerance Still Forbidden

继续：

```text
PASS_DRIVEN_TOLERANCE_CHANGE = PROHIBITED
```

尤其禁止：

```text
reference seems stricter
→ widen tolerance

reference source differs
→ broaden threshold

fixture noisy
→ remove comparison
```

---

# 63. Exact Identity Remains Exact

以下不能经过 fixture normalization弱化：

```text
Tool ID/version

Artifact contract/version

source checksum

fixture checksum

site identity

atom identity

frame identity

q-point identity

band identity

evidence identity
```

不得变成：

```text
closest
similar
display-equivalent
```

---

# 64. Production Scientific Authority

Phase 11-1：

```text
PRODUCTION_SCIENTIFIC_AUTHORITY_CHANGES = 0
```

不能改变：

```text
Adapter

Tool Registry scientific metadata

DataProfile science

Planner semantics

Eligibility

AnalysisPlan

Runtime

Artifact scientific schema

Workspace science

interpretation science

Report science
```

---

# 65. Production Source Boundary

默认：

```text
PRODUCTION_SOURCE_CHANGES = 0
```

允许改：

```text
fixtures

tests

validation scripts

evidence tools

docs

persistent project state

TASKS.md

results.md
```

如果发现必须改 production science：

```text
STOP
BLOCKED / REVIEWER_REQUIRED
```

---

# 66. Database Freeze

必须：

```text
new database table = 0

new database column = 0

new migration = 0

migration head =
0007_phase10m1_workspace_domain
```

---

# 67. API Freeze

必须：

```text
NEW_PUBLIC_API_FAMILIES = 0
```

Phase 11-1 不需要 runtime API。

---

# 68. Dependency Freeze

必须：

```text
new Python dependency = 0

new frontend dependency = 0

lockfile change = 0
```

Reference extraction 必须使用：

```text
standard library
or
already locked dependency
```

不得为了读一个 source：

```text
pip install new parser
```

---

# 69. Registry Freeze

必须：

```text
REGISTRY_BEFORE_11_1 = 62

REGISTRY_AFTER_11_1 = 62

NEW_SCIENTIFIC_TOOL = 0
```

---

# 70. DataProfile Freeze

必须：

```text
DATAPROFILE_BEFORE_11_1 = 2.4

DATAPROFILE_AFTER_11_1 = 2.4
```

Reference metadata 不进入 DataProfile。

---

# 71. Artifact Freeze

必须：

```text
NEW_PRODUCTION_ARTIFACT_FAMILY = 0
```

Fixture/reference records：

```text
are evidence artifacts
```

不是 production scientific Artifact contract。

---

# 72. Phase 12/13 Freeze

Phase 11-1 不得提前做：

```text
Design System 2.0

navigation redesign

Planner redesign

Workspace redesign

viewer redesign

Report UX redesign

mobile redesign
```

Phase 12 仍：

```text
ROADMAP_APPROVED
NOT_QUEUED
NOT_EXECUTABLE
```

Phase 13 同样。

---

# 73. Future Scope Guard

不得通过 reference work实现：

```text
Fermi surface

projected bands

Rietveld

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

van Hove

hop detection
```

看到这些官方例子：

只保留：

```text
FUTURE_SCOPE
```

---

# 74. Not Planned Guard

仍禁止：

```text
generic workflow engine

arbitrary notebook execution

RAG/vector DB

plugin marketplace

enterprise SaaS

distributed scheduler

autonomous agent

arbitrary Python
```

---

# 75. Evidence Directory

建立：

```text
docs/phase11/evidence/
phase11_1_reference_provenance_safe_fixture/
```

至少包含：

```text
baseline.txt

entry_gate.md

phase11_0_backlog_reconciliation.json

reference_acquisition_manifest.json

reference_provenance_registry.json

source_checksum_registry.json

license_disposition_matrix.json

raw_retention_matrix.json

fixture_registry.json

fixture_checksum_registry.json

transformation_registry.json

reference_independence_matrix.json

duplicate_reference_audit.json

official_example_extraction_status.json

phase11_2_benchmark_input_manifest.json

unresolved_reference_matrix.json

network_acquisition_audit.json

security.md

no_numeric_validation_audit.md

no_production_change_audit.md

docs_link_check.txt

secret_scan.txt

manifest.json
```

---

# 76. Canonical Source Bytes

如果 raw source可合法保留：

必须纳入：

```text
manifest.json
```

并有 checksum。

如果不可保留：

manifest记录 metadata/provenance sidecar。

不得假装：

```text
raw source retained
```

---

# 77. Evidence Manifest

必须：

```text
entries > 0

missing required entries = 0

hash mismatch = 0

duplicate logical fixture identity = 0

secret-bearing evidence = 0

untracked authoritative fixture = 0
```

---

# 78. Network Acquisition Audit

因为 11-1 首次允许 bounded static reference retrieval：

必须记录每一次：

```text
timestamp

requested source

resolved source

official domain/project

HTTP result if applicable

content type

bytes

checksum

retained?

reason
```

最终：

```text
UNAPPROVED_EXTERNAL_REQUESTS = 0
```

---

# 79. Secret Safety

严禁将：

```text
cookies

auth headers

tokens

session IDs

signed URLs

local private paths
```

保存到 evidence。

必须：

```text
NO_SECRET_PATTERN_HITS = PASS
```

---

# 80. Reference Source Security

任何 downloaded source：

只能：

```text
read as inert bytes/data
```

不得：

```text
execute
import as Python module
source shell script
open macro-enabled office automation
execute notebook
run bundled binary
render arbitrary HTML/JS
```

---

# 81. Archive Safety

如果 source是：

```text
ZIP
tar
other container
```

仅允许 bounded extraction。

必须防止：

```text
path traversal

absolute path

symlink escape

decompression bomb

nested archive explosion

oversized files
```

使用 repository 已有安全 extraction policy。

不得增加新 execution authority。

---

# 82. Malicious Fixture Content

Fixture可能包含：

```text
HTML
script text
prompt injection
formula strings
paths
URLs
```

这些必须：

```text
INERT_DATA
```

不能执行。

---

# 83. Acceptance Registry

Phase 11-1 建立 exact 10 项：

```text
P11V1-A01
PHASE11_0_BASELINE_BACKLOG_AND_ENTRY_AUTHORITY_CLOSURE

P11V1-A02
APPROVED_STATIC_REFERENCE_SOURCE_VERSION_AND_CHECKSUM_PROVENANCE

P11V1-A03
LICENSE_REDISTRIBUTION_AND_RAW_RETENTION_DISPOSITION_CLOSURE

P11V1-A04
IMMUTABLE_FIXTURE_IDENTITY_VERSION_AND_CHECKSUM_CONSOLIDATION

P11V1-A05
DETERMINISTIC_TRANSFORMATION_AND_REPLAY_PROVENANCE_CLOSURE

P11V1-A06
REFERENCE_INDEPENDENCE_SELF_REFERENCE_AND_DUPLICATION_CLASSIFICATION

P11V1-A07
OFFICIAL_EXAMPLE_EXTRACTION_WITHOUT_NUMERIC_VALIDATION_OVERCLAIM

P11V1-A08
PHASE11_2_EXACT_BENCHMARK_INPUT_HANDOFF_AND_ZERO_CRITICAL_TBD

P11V1-A09
SECURITY_NETWORK_NO_PRODUCTION_CHANGE_REGRESSION_AND_EVIDENCE_INTEGRITY

P11V1-A10
IMPLEMENTATION_EXACT_SHA_CI_COMPLETION_ARCHIVE_AND_11_2_REVIEWER_GATE
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

# 84. Queue Admission

Entry Gate PASS 后：

创建且只创建：

```text
one Phase 11-1 task
```

要求：

```text
TASK_BLOCK_COUNT = 1

ACTIVE_TASK = Phase 11-1

PHASE_11_2_EXECUTABLE_TASK_CREATED = NO

PHASE_12_EXECUTABLE_TASK_CREATED = NO

PHASE_13_EXECUTABLE_TASK_CREATED = NO
```

---

# 85. Required Documentation

至少新增/更新：

```text
docs/phase11/
phase11_1_reference_provenance_and_safe_fixture_consolidation.md

docs/phase11/
phase11_reference_registry.md

docs/phase11/
phase11_fixture_registry.md

docs/phase11/
phase11_source_license_matrix.md

docs/phase11/
phase11_transformation_registry.md

docs/phase11/
phase11_reference_independence_matrix.md

docs/phase11/
phase11_2_benchmark_input_handoff.md

docs/phase11/
phase11_1_completion.md
```

同步更新：

```text
phase11_reference_evidence_inventory.md

phase11_gap_matrix.md

phase11_implementation_backlog.md

phase11_acceptance_and_test_plan.md

phase11_execution_lock.md

phase11_execution_manifest.md
```

注意：

只能更新：

```text
11-1 completion facts
+
11-2 prepared inputs
```

不得重写已封板 governance。

---

# 86. Persistent State

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

只记录实际事实。

不得把：

```text
11-2
```

标记为 executable。

---

# 87. Gap Matrix Update Rules

每个 11-1 gap从：

```text
REFERENCE_MISSING
REFERENCE_PROVENANCE_INCOMPLETE
FIXTURE_LICENSE_UNKNOWN
EXTRACTION_REQUIRED
...
```

转到具体状态。

但：

```text
scientific validation gap
```

不能因为 reference准备好自动关闭。

例如：

```text
REFERENCE_MISSING
→ REFERENCE_READY_FOR_BENCHMARK
```

后续 11-2才能：

```text
benchmark validation gap
→ validated / failed
```

---

# 88. Official Example Status Update

允许：

```text
EXTRACTION_REQUIRED
→ REFERENCE_PREPARED_FOR_11_2
```

不允许：

```text
EXTRACTION_REQUIRED
→ DIRECT_VERIFIED
```

除非它原本只缺静态 provenance 而不涉及 scientific validation，并且 11-0 coverage policy明确允许。

默认：

```text
NO COVERAGE PROMOTION
```

---

# 89. Reference Status Update

允许：

```text
NO_REFERENCE
→ OFFICIAL_REFERENCE_AVAILABLE

PROVENANCE_INCOMPLETE
→ PROVENANCE_COMPLETE

LICENSE_UNKNOWN
→ LICENSE_DISPOSITION_RECORDED

FIXTURE_MISSING
→ FIXTURE_READY
```

不允许：

```text
REFERENCE_READY
→ NUMERICALLY_VALIDATED
```

---

# 90. Verification Commands

至少执行：

```powershell
git diff --check

uv lock --check

uv run python -m pytest -q

npm --prefix apps/web test

npm --prefix apps/web run typecheck

npm --prefix apps/web run build
```

以及 repository current canonical：

```text
Phase 10 closure validators

Phase 10K evidence integrity

Phase 10L evidence integrity

Phase 10M evidence integrity

Phase 10N evidence integrity

Phase 11-0 evidence integrity

Phase 11-1 provenance validator

fixture manifest validator

source checksum validator

transformation replay validator

license-disposition completeness validator

reference independence validator

11-2 handoff validator

TASKS lifecycle checker

docs link checker

secret scanner
```

---

# 91. Regression Floor

至少保持：

```text
Backend >= 1263 passed

Frontend >= 449 passed

Registry = 62

DataProfile = 2.4
```

service-backed：

必须保持 current canonical CI：

```text
PostgreSQL / Redis / MinIO = PASS

skipped = 0
failed = 0
errors = 0
```

不得为了 fixture changes删除测试。

---

# 92. Browser Regression

11-1 不增加 UI。

因此不需要新建专门 scientific browser product。

但 existing CI/browser regression必须保持：

```text
Chromium PASS

Firefox PASS

WebKit PASS

390x844 PASS
```

注意：

browser PASS 不算 reference scientific PASS。

---

# 93. npm Audit

如果 configured mirror 仍返回：

```text
404_NOT_IMPLEMENTED
```

必须：

```text
npm audit = UNAVAILABLE
```

不得：

```text
npm audit = PASS
npm audit = clean
```

---

# 94. Phase 11-1 Required Markers

必须：

```text
PHASE11_1_NEW_SCIENTIFIC_TOOLS = 0

PHASE11_1_NEW_SCIENTIFIC_ALGORITHMS = 0

PHASE11_1_NEW_ARTIFACT_FAMILIES = 0

PHASE11_1_NEW_DATAPROFILE_VERSION = 0

PHASE11_1_NEW_ANALYSISPLAN_VERSION = 0

PHASE11_1_NEW_DATABASE_MIGRATIONS = 0

PHASE11_1_NEW_PUBLIC_API_FAMILIES = 0

PHASE11_1_NEW_DEPENDENCIES = 0

PHASE11_1_NEW_LLM_CALL_SITES = 0

PHASE11_1_REAL_LLM_CALLS = 0

PHASE11_1_NUMERIC_SCIENTIFIC_PASS_DECLARATIONS = 0

PHASE11_1_TOOL_VALIDATION_LEVEL_PROMOTIONS = 0

PHASE11_1_DOWNLOADED_SCRIPT_EXECUTIONS = 0

PHASE11_1_NOTEBOOK_EXECUTIONS = 0

PHASE11_1_EXTERNAL_SCIENTIFIC_API_CALLS = 0
```

---

# 95. Reference Honesty Markers

必须：

```text
SELF_REFERENCE_EQUALS_INDEPENDENT_REFERENCE = NO

OFFICIAL_EXAMPLE_EQUALS_VERIFIED = NO

FIXTURE_READY_EQUALS_NUMERIC_PASS = NO

REFERENCE_READY_EQUALS_TOOL_VALIDATED = NO

SCREENSHOT_NUMERIC_AUTHORITY = NONE

BROWSER_NUMERIC_AUTHORITY = NONE

SERVICE_NUMERIC_AUTHORITY = NONE

LATEST_SOURCE_AUTHORITY = NONE

PASS_DRIVEN_TOLERANCE_CHANGE = PROHIBITED
```

---

# 96. Entry Gate Commands

进入：

```powershell
cd "E:\1project\Material Data Intelligence"
```

运行：

```powershell
pwd

git remote -v

git branch --show-current

git status --short

git rev-parse HEAD

git rev-parse origin/master

git log --oneline --decorate -160

git diff --stat

git diff --check
```

Ancestry 至少：

```powershell
git merge-base --is-ancestor 312fd4445d404f0f89c061fbdc055789912dc552 HEAD

git merge-base --is-ancestor dee197d39e194277351a34fcd063b3de97729534 HEAD

git merge-base --is-ancestor ef40ade537820e88bbe2d259a9b4ccb9cd04ac1c HEAD
```

---

# 97. Entry Gate Audit

在 admission 之前必须确认：

```text
11-0 implementation CI PASS

11-0 completion present

11-0 queue archive present

HEAD == origin/master

worktree clean

Registry = 62

DataProfile = 2.4

migration = 0007

TASK_BLOCK_COUNT = 0

11-2 task absent

Phase 12 task absent

Phase 13 task absent

11-0 12-gap matrix readable

11-1 exact backlog readable

reference inventory readable

fixture inventory readable

official-example inventory readable

tolerance registry readable

license disposition rules readable

reference provenance rules readable

11-2 benchmark dependency map readable
```

---

# 98. Entry Gate Output

成功：

```text
PHASE_11_1_ENTRY_GATE = PASS

PHASE_11_0_REVIEWER_APPROVAL = VERIFIED

PHASE_11_1_QUEUE_ADMISSION = AUTHORIZED

PHASE_11_1_REFERENCE_PROVENANCE_SCOPE = SEALED

PHASE_11_1_SAFE_FIXTURE_SCOPE = SEALED

PHASE_11_1_NUMERIC_VALIDATION_AUTHORITY = NONE

PHASE_11_1_READINESS =
READY_FOR_REFERENCE_AND_FIXTURE_CONSOLIDATION
```

---

# 99. Phase 11-1 Execution Order

严格按：

```text
admit exactly one Phase 11-1 task

→ reconcile 11-0 exact 11-1 backlog

→ resolve exact source/version identities

→ retrieve only reviewer-approved static sources

→ checksum source bytes

→ resolve license/redistribution status

→ determine raw-retention disposition

→ deduplicate retained sources

→ perform bounded deterministic extraction

→ create immutable normalized fixtures

→ checksum normalized fixtures

→ create transformation records

→ classify self-reference / independence

→ reconcile official-example statuses

→ prepare exact 11-2 benchmark input manifest

→ validate no numeric PASS was declared

→ run regression/evidence/security checks

→ create implementation commit

→ push

→ wait for implementation exact-SHA CI

→ if PASS:
   create completion-record commit and push directly

→ create queue-archive commit and push directly

→ stop

→ return complete Phase 11-1 result
```

---

# 100. Implementation Exact-SHA CI Gate

这是当前 lifecycle 唯一必须等待的 CI gate。

Implementation commit必须包含：

```text
Phase 11-1 task admission

reference acquisitions

fixtures

provenance

license matrix

transformation registry

independence matrix

11-2 handoff

tests

evidence

docs

persistent state
```

push 后：

```text
WAIT FOR IMPLEMENTATION EXACT-SHA CI
```

只有成功：

```text
IMPLEMENTATION_EXACT_SHA_CI = PASS
```

才能写 completion record。

---

# 101. Failed Implementation CI

如果失败：

必须：

```text
retain failed SHA

retain failed CI run

record cause

fix forward

push corrected implementation

wait for corrected exact-SHA CI
```

不得：

```text
force push

rewrite history

delete failed candidate

silently replace fixture

weaken source requirements

weaken checksum requirements

weaken tests

widen scientific tolerance
```

---

# 102. Completion Record Lifecycle

Implementation exact-SHA CI PASS 后：

向：

```text
results.md
```

追加完整：

```text
Phase 11-1 Reference Provenance
+ Safe Fixture Consolidation Result
```

然后：

```text
commit
push
```

按当前用户 lifecycle direction：

```text
DO NOT WAIT
for additional completion-record CI
```

如果在继续之前 CI 已经自然返回明确 failure：

不能故意忽略。

必须 fix-forward。

但不要求主动等待。

---

# 103. Queue Archive Lifecycle

Completion record push 后：

删除且只删除：

```text
Phase 11-1 TASK block
```

不得创建：

```text
Phase 11-2 task
```

然后：

```text
commit
push
```

同样：

```text
DO NOT WAIT
for archive CI
```

最终使用：

```text
QUEUE_ARCHIVED
```

而不是在没有 exact-SHA CI事实时声称：

```text
ARCHIVED_BY_VERIFIED_QUEUE_COMMIT
```

---

# 104. Final Phase State

最终：

```text
Phase 11-1:
PASS / REFERENCE_PROVENANCE_AND_FIXTURES_SEALED / QUEUE_ARCHIVED

Phase 11:
IN_PROGRESS / REFERENCE_BASELINE_PREPARED

Phase 11-2:
REVIEWER_GATE / AWAITING REVIEWER PROMPT

Phase 12:
ROADMAP_APPROVED / NOT_QUEUED / NOT_EXECUTABLE

Phase 13:
ROADMAP_APPROVED / NOT_QUEUED / NOT_EXECUTABLE

TASK_BLOCK_COUNT = 0

PHASE_11_2_EXECUTABLE_TASK_CREATED = NO
```

---

# 105. Required Results.md Format

至少：

# Phase 11-1 Reference Provenance + Safe Fixture Consolidation Result

1. Conclusion
2. Phase 11-0 Baseline
3. Entry Gate
4. Phase 11-0 Backlog Reconciliation
5. Production Behavior Changes
6. Reference Acquisition Scope
7. Reference Sources Requested
8. Reference Sources Resolved
9. Source Version Pinning
10. Source Redirects
11. Source Checksums
12. Publisher Checksums
13. Source Retention Decisions
14. License Inventory
15. Redistribution Dispositions
16. License Review Required Items
17. Existing Reference Reuse
18. Duplicate Reference Detection
19. Reference Independence Audit
20. Self-Reference Audit
21. Existing Fixture Reuse
22. New Fixture Inventory
23. Fixture Identity / Versioning
24. Original Source Retention
25. Normalized Fixture Inventory
26. Fixture Checksums
27. Transformation Registry
28. Transformation Replay
29. Numeric Mutation Audit
30. Unit Transformation Audit
31. N1 Reference Preparation
32. N2 Reference Preparation
33. N3 Reference Preparation
34. N4 Reference Preparation
35. N5 Reference Preparation
36. Earlier Initial-Release Reference Preparation
37. Official Example Reconciliation
38. Input Support Non-Change Verification
39. Numeric Validation Non-Scope
40. Validation-Level Non-Promotion
41. Coverage Non-Promotion
42. Tolerance Non-Change
43. Gap Matrix Update
44. P0/P1/P2 Status
45. Unresolved Sources
46. Unresolved Licensing
47. Potential Scientific Discrepancies
48. Phase 11-2 Benchmark Input Manifest
49. Phase 11-2 Blocking Readiness
50. Zero Critical TBD Verification
51. Reference Provenance Registry
52. Fixture Registry
53. License Matrix
54. Independence Matrix
55. Evidence Inventory
56. Evidence Manifest
57. Network Acquisition Audit
58. Security
59. LLM / DeepSeek
60. Database / API / Dependency Freeze
61. Registry / DataProfile Freeze
62. Tests
63. Browser Regression
64. Service-Backed Regression
65. npm Audit
66. Files Changed
67. Acceptance Registry
68. Implementation Commit / CI
69. Failed Implementation Candidates
70. Completion Record
71. Queue Archive
72. Queue State
73. Phase 11-2 Gate
74. Final Repository State

---

# 106. PASS Conditions

只有满足全部：

```text
11-0 baseline ancestry verified

HEAD == origin/master at entry

worktree clean

Registry = 62

DataProfile = 2.4

migration = 0007

TASK_BLOCK_COUNT = 0 at entry


all 11-1 backlog entries reconciled

all blocking reference sources resolved

all blocking source versions pinned

all blocking checksums recorded

all blocking unit semantics resolved

all blocking license dispositions resolved enough for allowed use

all retained raw files have explicit redistribution disposition

all normalized fixtures have immutable identity/version/checksum

all transformations reproducible

all transformations recorded

all duplicate references classified

all self-references classified

all independent references justified


11-2 benchmark input manifest complete

11-2 blocking entries READY

implementation-critical TBD = 0


numeric scientific PASS declarations = 0

Tool validation-level promotions = 0

honest coverage promotions = 0

scientific tolerance changes = 0

production science changes = 0


new Tool = 0

Registry final = 62

DataProfile final = 2.4

new Artifact family = 0

database schema unchanged

migration unchanged

public API unchanged

dependencies unchanged

lockfile unchanged


downloaded script executions = 0

notebook executions = 0

external scientific API calls = 0

real LLM calls = 0

unapproved external requests = 0


Backend >= 1263 passed

Frontend >= 449 passed

PostgreSQL / Redis / MinIO PASS

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

evidence PASS

docs links PASS

secret scan PASS


P11V1 acceptance = 10/10


implementation exact-SHA CI PASS

completion record committed/pushed

queue archive committed/pushed


final TASK_BLOCK_COUNT = 0

Phase 11-2 task absent

Phase 12 task absent

Phase 13 task absent
```

才允许：

```text
Phase 11-1:
PASS
```

---

# 107. BLOCKED Conditions

必须 BLOCKED / REVIEWER_REQUIRED：

```text
a blocking 11-0 source cannot be identified

a blocking source cannot be pinned to an immutable version

a blocking source is unavailable

a blocking source has unresolved unit semantics

a blocking source license prevents required fixture use
and no sealed alternative exists

source checksum contradicts retained authoritative checksum

official source changed without immutable historical version

fixture transformation would require changing scientific values

fixture requires arbitrary code/notebook execution

reference requires an external scientific API

reference independence claim cannot be established

reference reveals probable current scientific contract error

11-2 blocking benchmark cannot receive an exact fixture

a required expected-value source remains unknown

production scientific code must change

new dependency is required

new scientific algorithm is required

tolerance must change to fit reference
```

不得自行解决这些 reviewer-level问题。

---

# 108. Non-Blocking Conditions

通常不阻塞 11-1：

```text
supporting P2 source remains reference-only

raw bytes cannot be vendored
but official source/version/checksum/provenance
and legally permissible benchmark input are sufficient

non-blocking historical official example remains mapping-only

superseded example remains historical

browser screenshot unavailable

presentation-only Tool has no numeric reference
where numeric reference is not applicable
```

必须明确记录原因。

---

# 109. Critical Scientific Honesty Rule

Phase 11-1 完成后，你只能说：

```text
“The reference and fixture inputs required
for the approved Phase 11-2 benchmark scope
have been provenance-sealed and safely prepared.”
```

不能说：

```text
“The scientific Tools are now validated.”
```

也不能说：

```text
“All reference tests pass.”
```

因为真正的：

```text
platform output
vs
reference expected value/invariant
```

属于 Phase 11-2。

---

# 110. First Required Output

开始后首先输出：

```text
Phase 11-1 Entry Gate
+ 11-0 Backlog Reconciliation
+ Reference Acquisition / Fixture Consolidation Readiness
```

至少确认：

1. Phase 11-0 implementation SHA；
2. Phase 11-0 implementation exact-SHA CI；
3. Phase 11-0 completion SHA；
4. Phase 11-0 queue archive SHA；
5. branch / HEAD / origin / worktree；
6. Registry 62；
7. DataProfile 2.4；
8. migration 0007；
9. TASK_BLOCK_COUNT=0；
10. 11-2 task absent；
11. 12-gap matrix；
12. P0=0 baseline；
13. exact 11-1 backlog；
14. 43-reference inventory；
15. 169-fixture inventory；
16. 54-official/example inventory；
17. license statuses；
18. transformation policy；
19. tolerance registry；
20. 11-2 benchmark dependencies；
21. no production code change required；
22. all external retrieval targets are already reviewer-approved/static。

成功后输出：

```text
PHASE_11_1_ENTRY_GATE = PASS

PHASE_11_0_REVIEWER_APPROVAL = VERIFIED

PHASE_11_1_QUEUE_ADMISSION = AUTHORIZED

PHASE_11_1_REFERENCE_ACQUISITION = AUTHORIZED_WITH_SEALED_SOURCE_LIST

PHASE_11_1_SAFE_FIXTURE_CONSOLIDATION = AUTHORIZED

PHASE_11_1_NUMERIC_VALIDATION = NOT_AUTHORIZED

PHASE_11_1_READINESS =
READY_FOR_REFERENCE_PROVENANCE_AND_FIXTURE_CLOSURE
```

然后执行 Phase 11-1。

---

# 111. Stop Rule

完成：

```text
reference provenance

fixture consolidation

11-2 handoff

implementation CI

completion record

queue archive
```

后立即停止。

最终不得：

```text
run Phase 11-2 numeric benchmarks

compare platform outputs against golden expected values
as authoritative PASS/FAIL

run Phase 11-3 platform variance

publish Phase 11-4 honest coverage

close Phase 11

begin Phase 12 UI/UX redesign
```

返回完整 Phase 11-1 result，等待 reviewer 下一步指令。


---END---

---TASK---
 状态：待处理

# Phase 11-2 Reviewer Prompt

# Cross-Capability Golden Scientific Benchmark Suite

你现在执行：

# Phase 11-2：Cross-Capability Golden Scientific Benchmark Suite

中文：

# 跨能力 Golden Scientific Benchmark 科学基准验证

本阶段属于：

```text
Phase 11:
Scientific Validation,
Reference Provenance,
Reproducibility
& Honest Coverage
```

Phase 11-2 是 Phase 11 中第一次正式允许：

```text
production scientific output
vs
sealed expected scientific value / invariant
```

进行权威 PASS / FAIL 比较的阶段。

---

# 0. Fundamental Phase Boundary

Phase 11-0 已完成：

```text
validation governance
validation-level model
Tool validation inventory
tolerance ownership
gap matrix
benchmark backlog
```

Phase 11-1 应完成：

```text
reference provenance
source/version/checksum
license disposition
immutable fixtures
transformation provenance
reference independence
Phase11_2BenchmarkInputManifest
```

Phase 11-2 才负责：

```text
execute exact approved benchmark cases

→ run the actual production scientific authority

→ produce actual scientific output

→ compare against sealed expected values/invariants

→ apply sealed quantity-specific tolerances

→ validate units

→ validate exact identities

→ validate positive cases

→ validate negative cases

→ validate deterministic replay

→ validate Artifact scientific contracts

→ classify benchmark PASS / FAIL

→ update evidence-derived validation levels

→ prepare Phase 11-3 reproducibility input

→ stop
```

---

# 1. Reviewer Authorization

正式条件授权：

```text
PHASE_11_2_PROMPT_PREAUTHORIZED = YES
```

但是 Phase 11-2 只有满足本 Prompt 的 Entry Gate 才能真正 admission。

正式授权：

```text
AUTHORIZED_PHASE = Phase 11-2
MAX_PHASES_EXECUTED = 1
```

不得创建、排队或执行：

```text
Phase 11-3
Phase 11-4
Phase 11-5
Phase 12
Phase 13
```

---

# 2. Mandatory Phase 11-1 Dependency

本 Prompt 不允许凭当前文字假设 Phase 11-1 已经完成。

执行器必须从：

```text
Git history
results.md
TASKS.md
persistent state
docs/phase11/
docs/phase11/evidence/
```

读取真实 Phase 11-1 lifecycle。

必须解析：

```text
PHASE_11_1_IMPLEMENTATION_SHA

PHASE_11_1_IMPLEMENTATION_CI_RUN

PHASE_11_1_IMPLEMENTATION_CI_RESULT

PHASE_11_1_COMPLETION_SHA

PHASE_11_1_QUEUE_ARCHIVE_SHA
```

并确认：

```text
Phase 11-1:
PASS

reference provenance = SEALED

fixtures = SEALED

queue = ARCHIVED
```

如果 repository 中没有这些事实：

```text
PHASE_11_2_ENTRY_GATE = BLOCKED

reason =
PHASE_11_1_NOT_COMPLETED
```

立即停止。

---

# 3. Phase 11-1 Implementation CI Gate

至少要求：

```text
PHASE_11_1_IMPLEMENTATION_CI_RESULT = PASS
```

Phase 11-1 completion/archive 按当前 project lifecycle 可以是：

```text
direct committed / pushed
```

不要求执行器虚构：

```text
completion/archive exact-SHA CI PASS
```

如果它们事实上有 CI：

如实记录。

如果没有：

不得写成 VERIFIED。

---

# 4. Phase 11-2 Dynamic Baseline

Phase 11-2 不应把 Phase 11-0 archive SHA 写死成当前 HEAD。

Entry baseline 应动态取：

```text
PHASE_11_1_QUEUE_ARCHIVE_SHA
```

然后验证：

```text
branch = master

HEAD == origin/master

HEAD contains Phase 11-1 implementation

HEAD contains Phase 11-1 completion

HEAD contains Phase 11-1 queue archive

worktree = clean
```

如果：

```text
HEAD != origin/master
```

或：

```text
worktree != clean
```

则：

```text
BLOCKED / REVIEWER_REQUIRED
```

---

# 5. Current Platform Floor

必须保持：

```text
Registry count = 62

DataProfile = 2.4

migration head =
0007_phase10m1_workspace_domain
```

不得变化：

```text
Registry scientific surface

DataProfile contract

AnalysisIntent

EligibilityResolution

AnalysisPlan 0.1 / 0.2

QueueWorkerRuntime scientific authority

Artifact scientific authority

Workspace scientific authority
```

---

# 6. Dynamic Regression Floors

Phase 11-0 已有基础 floor：

```text
Backend >= 1263

Frontend >= 449
```

但 11-1 可能新增验证测试。

因此 Phase 11-2 Entry Gate 必须从 11-1 final result 读取：

```text
PHASE_11_1_BACKEND_PASS_COUNT

PHASE_11_1_FRONTEND_PASS_COUNT

PHASE_11_1_SERVICE_PASS_COUNT
```

Phase 11-2 floor：

```text
BACKEND_FLOOR =
max(1263, Phase 11-1 final backend pass count)

FRONTEND_FLOOR =
max(449, Phase 11-1 final frontend pass count)

SERVICE_FLOOR =
Phase 11-1 current verified service-backed floor
```

不得因为 Phase 11-2：

```text
delete tests
lower pass floor
disable difficult benchmarks
```

---

# 7. Mandatory 11-1 Handoff

必须找到 Phase 11-1 canonical equivalent：

```text
Phase11_2BenchmarkInputManifest
```

例如 repository naming 可以是：

```text
phase11_2_benchmark_input_manifest.json

phase11_2_benchmark_input_handoff.md
```

但必须存在一个唯一 canonical authority。

不得创建第二份相互竞争的 benchmark scope。

---

# 8. Benchmark Manifest Required Fields

每个 benchmark entry 必须至少有：

```text
benchmarkId

gapId

toolId

toolVersion

scientificCapability

referenceId

referenceType

referenceVersion

fixtureId

fixtureVersion

fixtureChecksum

expectedValue
or
expectedInvariant

expectedUnits

toleranceId

positiveOrNegativeCase

referenceStrength

referenceIndependence

executionPath

artifactContract

11_2Readiness
```

如果 current sealed manifest 使用 equivalent field names：

保持原名称。

不得重新设计 semantic contract。

---

# 9. Every Benchmark Must Be Ready

允许：

```text
READY_FOR_11_2

READY_WITH_REFERENCE_LIMITATION

NOT_REQUIRED_FOR_11_2
```

不得执行：

```text
BLOCKED_SOURCE_UNAVAILABLE

BLOCKED_LICENSE

BLOCKED_VERSION

BLOCKED_UNIT_SEMANTICS

BLOCKED_PROVENANCE
```

如果一个：

```text
BLOCKING_11_2 = YES
```

的 benchmark 不 READY：

```text
PHASE_11_2_ENTRY_GATE = BLOCKED
```

不得：

```text
skip it
replace it
invent another fixture
```

---

# 10. Zero Critical TBD Gate

必须：

```text
IMPLEMENTATION_CRITICAL_TBD = 0
```

不得存在：

```text
expected value TBD

unit TBD

tolerance TBD

fixture TBD

reference TBD

Tool version TBD

negative expected outcome TBD
```

这类内容必须回 Phase 11-1/reviewer。

---

# 11. Benchmark Scope Authority

执行范围必须来自：

```text
Phase 11-0 benchmark backlog
+
Phase 11-1 exact handoff
```

禁止：

```text
benchmark every Tool just because Registry has 62

invent additional benchmarks

choose easier fixtures

drop hard fixtures

replace official reference with synthetic reference

change benchmark family coverage
```

---

# 12. Cross-Capability Means Initial Release Science

必须检查 handoff 是否已经 disposition 以下 Initial Release 科学家族：

```text
Dataset / Material Intelligence

Materials ML

Composition Space

Structure

Coordination

Local Environment / Polyhedra

Experimental XRD

Trajectory RDF

Trajectory MSD

Trajectory Diffusion

Phonon

Brillouin Zone

Volumetric

Electronic Band Structure

Electronic DOS
```

每个 family 必须：

```text
has benchmark IDs

or

NOT_REQUIRED_FOR_11_2
with exact governance reason
```

不能：

```text
silently disappear
```

---

# 13. Not All 62 Tools Need Numeric Benchmarks

继续遵守 11-0 role classification。

对于：

```text
PRESENTATION_ONLY

PRODUCT_COMPOSITION

METADATA_OR_UTILITY
```

不得人为制造：

```text
fake numeric scientific truth
```

这些 Tool 可以由：

```text
contract
identity
no-recomputation
runtime
Artifact
browser
security
```

验证。

Phase 11-2 的 Golden Scientific Benchmark 重点是：

```text
SCIENTIFIC_NUMERIC

SCIENTIFIC_GEOMETRY

SCIENTIFIC_CLASSIFICATION

SCIENTIFIC_TRANSFORMATION

DATA_INTELLIGENCE

MATERIALS_ML

COMPOSITION_ANALYSIS
```

等有科学/数学 truth 的能力。

---

# 14. Scientific Authority Under Test

正式 benchmark 必须测试：

```text
the actual registered production scientific authority
```

即：

```text
registered Tool
→ registered Adapter
→ production computation path
→ output scientific contract
```

不能只测试：

```text
a copied test implementation

a benchmark-only reimplementation

a Python formula written solely in tests
```

---

# 15. Production Runtime Evidence

对于 Registry Tool benchmark：

至少必须验证：

```text
Tool ID/version exact

Adapter registration exact

parameter binding exact

input identity exact

scientific output exact contract

Artifact persistence where applicable
```

对于适合 persisted execution 的 family：

至少一个 representative benchmark 必须经过：

```text
real QueueWorkerRuntime
→ persisted Artifact
```

以证明：

```text
production execution path
```

和：

```text
scientific kernel
```

没有分叉。

---

# 16. Direct Adapter Benchmark

允许直接调用 registered Adapter：

用于：

```text
high-density scientific numeric benchmark

isolated deterministic scientific comparison
```

但它不能成为唯一证据，如果该 capability 正常生产路径通过：

```text
QueueWorkerRuntime
```

执行。

原则：

```text
Adapter-level benchmark
+
representative persisted Runtime benchmark
```

共同组成 production scientific validation。

---

# 17. Benchmark-Only Scientific Reimplementation Is Forbidden

禁止：

```text
reimplement RDF formula in benchmark code
and compare production RDF against it
if this new implementation has no sealed analytic authority

reimplement CrystalNN

reimplement VoronoiNN

reimplement XRD

reimplement band gap calculation

reimplement diffusion
```

Expected truth 必须来自：

```text
sealed reference / analytic construction
```

不是 Phase 11-2 新写一套“参考算法”。

---

# 18. Analytic Reference Cases

如果 11-1 handoff 为：

```text
ANALYTIC_REFERENCE
```

允许 benchmark harness 对 sealed analytic formula 做：

```text
deterministic expected-value evaluation
```

前提：

```text
formula already sealed

parameters already sealed

units already sealed

no new scientific decision
```

不得 Phase 11-2 临时发明 analytic reference。

---

# 19. Reference Value Is Immutable

禁止：

```text
modify expected value after observing platform output
```

必须：

```text
EXPECTED_VALUE_FREEZE_BEFORE_PLATFORM_COMPARISON = YES
```

Benchmark evidence 必须能证明：

```text
fixture checksum

expected reference checksum/value

tolerance ID
```

在 comparison 前已存在。

---

# 20. Tolerance Authority

必须严格使用：

```text
Phase11ToleranceRegistry
```

禁止：

```text
new tolerance
temporary tolerance
pytest approx default
ad hoc decimal places
visual similarity tolerance
```

如果 benchmark entry找不到 exact：

```text
toleranceId
```

则：

```text
BLOCKED
```

---

# 21. Pass-Driven Tolerance Remains Forbidden

必须：

```text
PASS_DRIVEN_TOLERANCE_CHANGE = PROHIBITED
```

如果结果：

```text
expected = X
actual = Y
```

超出 sealed tolerance：

必须：

```text
FAIL
```

不能：

```text
widen tolerance
```

---

# 22. Exact Comparison Class

对于 exact quantity/identity：

必须：

```text
comparisonMode = EXACT
```

例如：

```text
Tool ID/version

Artifact contract/version

source hash

fixture hash

site/atom/frame identity

k-point identity

band identity

spin channel identity

categorical outcome
```

不得使用 floating tolerance 代替 identity。

---

# 23. Numeric Comparison Class

允许 only sealed：

```text
ABSOLUTE_TOLERANCE

RELATIVE_TOLERANCE

ABSOLUTE_AND_RELATIVE

POSITIONAL_TOLERANCE

ANGULAR_TOLERANCE

ENERGY_TOLERANCE

PEAK_TOLERANCE

FIT_TOLERANCE
```

或 Phase 11-0 exact equivalents。

每个必须有：

```text
unit
scientific justification
tolerance owner
```

---

# 24. NaN / Inf Policy

Benchmark 必须明确验证：

```text
finite scientific outputs
```

除非 scientific contract 对某字段明确允许：

```text
null
undefined
```

不能：

```text
NaN == NaN
```

当作科学 PASS。

非有限值必须依 contract：

```text
reject
or
typed unavailable
```

---

# 25. Signed Zero

必须统一处理：

```text
-0.0
+0.0
```

依 sealed serialization/numeric policy。

不得因为 display format制造 false failure。

但：

```text
semantic hash
```

必须遵守 repository canonical representation。

---

# 26. Unit Validation

每个 numeric benchmark 必须先验证：

```text
actual unit
expected unit
```

再比较数值。

禁止：

```text
same number
different unit
→ PASS
```

---

# 27. Unit Conversion

如果 production contract canonicalizes：

```text
source unit → canonical unit
```

benchmark 必须验证：

```text
conversion provenance

source unit

canonical unit

conversion rule
```

但不得：

```text
benchmark harness silently fix a wrong platform unit
```

---

# 28. Identity Before Value

必须执行：

```text
identity validation
→ unit validation
→ numeric/invariant comparison
```

如果 identity错误：

即使数值相同：

```text
FAIL_IDENTITY
```

不能 PASS。

---

# 29. Benchmark Verdict Taxonomy

建议/要求使用 sealed equivalent：

```text
PASS_EXACT

PASS_TOLERANCE_BOUNDED

PASS_INVARIANT

PASS_EXPECTED_TYPED_REJECTION

FAIL_IDENTITY

FAIL_UNIT

FAIL_NUMERIC

FAIL_INVARIANT

FAIL_CONTRACT

FAIL_DETERMINISM

FAIL_UNEXPECTED_SUCCESS

BLOCKED_REFERENCE

NOT_APPLICABLE
```

不得只：

```text
PASS
FAIL
```

而隐藏失败类型。

---

# 30. Positive Cases

每个 sealed positive benchmark 必须验证：

```text
valid input

expected Tool applicability

expected output contract

expected identity

expected unit

expected numeric/invariant result

expected warnings/qualification
where sealed
```

---

# 31. Negative Cases

Phase 11-0 已要求：

```text
positive
+
negative
```

case。

负例不是：

```text
test throws somehow
```

而必须验证 exact typed semantics。

例如：

```text
invalid unit
→ typed rejection

missing time
→ ineligible/typed unavailable

ballistic diffusion case
→ rejected/qualified under sealed policy

wavelength mismatch
→ typed mismatch

partial PDOS
→ no full dominance claim

stale identity
→ exact rejection
```

实际 case 以 11-1 handoff 为准。

---

# 32. Unexpected Success Is a Failure

如果 negative fixture本应：

```text
REJECT
UNAVAILABLE
QUALIFIED
```

production 却：

```text
returns normal scientific result
```

必须：

```text
FAIL_UNEXPECTED_SUCCESS
```

不能因为程序没有 crash 就 PASS。

---

# 33. Determinism

对于 sealed deterministic capabilities：

每个 benchmark至少执行：

```text
first run
+
replay run
```

要求 scientific semantic output：

```text
same identities

same units

same values within exact deterministic contract

same canonical ordering

same semantic checksum/hash where applicable
```

运行时 ID / timestamp 可依 contract 排除。

---

# 34. Randomized Scientific Methods

如果已有 approved method 存在随机性：

必须使用：

```text
sealed seed
```

并验证：

```text
seed provenance
```

例如 existing KMeans/PCA policies只能按现有 contract。

不得：

```text
rerun until good result
```

---

# 35. Dataset / Material Intelligence Benchmarks

如果 handoff 包含：

必须验证相应 sealed truth，例如：

```text
row/sample counts

element counts

chemical systems

duplicate classes

finite property distributions

missingness

dataset comparison

stable sample identity
```

禁止：

```text
infer anomaly truth
infer chemical validity
```

除非 contract already owns it。

---

# 36. Materials ML Benchmarks

如果 handoff 包含：

至少按 sealed references验证：

```text
MAE

RMSE

R2 defined-or-null semantics

signed bias / residual convention

classification confusion counts

accuracy

precision/recall/F1

undefined metric null policy

uncertainty bins

sample identity

model/target identity
```

不得增加：

```text
training

AutoML

SHAP

new ML science
```

---

# 37. PCA / Composition Space Benchmarks

如果 handoff 包含：

验证：

```text
normalized atomic-fraction vectors

centering

PCA coordinates/reference invariants

sign convention

explained behavior if contract emits it

KMeans seeded determinism

sample identity

cluster label semantics
```

注意：

```text
cluster label number
```

若 contract只具有 permutation-equivalent semantics：

必须依 sealed policy比较。

不得自己决定。

---

# 38. Structure Benchmarks

如果 handoff包含：

验证：

```text
lattice

species

sites

distances

angles

structure identities

periodic images
```

不得验证不存在的：

```text
true bond
stability
oxidation state
```

---

# 39. CrystalNN Benchmark Rules

如果 handoff包含：

验证：

```text
exact pymatgen-bound algorithm/version

reference structure/site

neighbor identities

periodic images

weights

coordination

parameters

warnings
```

科学措辞：

```text
algorithm-derived local coordination
```

不得：

```text
true bond coordination
```

---

# 40. VoronoiNN Benchmark Rules

同样验证其自身 official/reference behavior。

禁止：

```text
VoronoiNN output must equal CrystalNN
```

算法之间：

```text
DISAGREEMENT != FAILURE
```

只要各自符合自己的 reference。

---

# 41. N2 Local Environment Benchmarks

如果 handoff包含：

必须验证：

```text
exact persisted N1 dependency identity

environment classification

reference scores

polyhedron vertices

faces

distortion

periodic identity
```

同时必须证明：

```text
N2_RECOMPUTED_N1_NEIGHBORS = 0

N2_INDEPENDENT_NEIGHBOR_SEARCH = 0
```

---

# 42. Experimental XRD Benchmarks

如果 handoff包含：

验证：

```text
peak detection

normalization

one-to-one matching

2θ units

Δ2θ

tolerance

matched

unmatched experimental

unmatched theoretical

zero-match

wavelength mismatch

tie handling
```

禁止：

```text
Rietveld

phase confirmation

phase fraction

automatic phase identification
```

---

# 43. XRD Zero Match

必须允许：

```text
valid benchmark result
with zero matched peaks
```

如果 contract如此定义。

不得：

```text
zero match → exception
```

来逃避科学结果。

---

# 44. Trajectory RDF Benchmarks

如果 handoff包含：

验证：

```text
species selection

pair identity

r bins

normalization

window

PBC semantics

units

expected analytic/control behavior
```

不得：

```text
RDF peak → chemical bond claim
```

---

# 45. Trajectory MSD Benchmarks

如果 handoff包含：

验证：

```text
atom identity

frame/time identity

PBC unwrapping

boundary crossing

origin semantics

lag time

MSD

directional MSD
```

尤其：

```text
server-side unwrapping
```

必须与 sealed control/reference一致。

---

# 46. Diffusion Benchmarks

如果 handoff包含：

验证：

```text
exact persisted MSD dependency

fit-window identity

slope

dimensional factor

D

fit diagnostics

ballistic rejection

random-walk reference
```

必须证明：

```text
DIFFUSION_MSD_RECOMPUTATION = 0

DIFFUSION_RAW_TRAJECTORY_READS = 0
```

如果 existing contract如此封板。

---

# 47. Diffusion Wording Boundary

PASS 只能证明：

```text
estimated diffusion
under selected fit window / policy
```

不能升级为：

```text
true bulk diffusion coefficient
```

---

# 48. Phonon Benchmarks

如果 handoff包含：

验证：

```text
q-point identity

frequency

unit

band path

branch identity

DOS

combined Band+DOS compatibility

imaginary-frequency semantics
```

不得：

```text
unqualified thermodynamic stability claim
```

---

# 49. Brillouin Zone Benchmarks

如果 handoff包含：

验证：

```text
reciprocal lattice

BZ vertices/faces

persisted labels

path identity

coordinate/reference semantics
```

不得：

```text
frontend regenerate BZ and use it as reference
```

---

# 50. Volumetric Benchmarks

如果 handoff包含：

验证：

```text
grid shape

cell mapping

field identity

scalar values/range

slice coordinates

isosurface value semantics

volume mapping
```

不得：

```text
Bader

charge topology

ELF topology
```

---

# 51. Band Structure Benchmarks

如果 handoff包含：

验证：

```text
source identity

energy unit

energy reference

Fermi

spin

k-points

path breaks

band identities

VBM

CBM

gap

direct/indirect classification

bounded metal-like policy
```

不得：

```text
frontend recompute band gap
```

生产科学 authority 仍在 server/Adapter。

---

# 52. DOS Benchmarks

如果 handoff包含：

验证：

```text
energy grid

DOS units

spin channels

total DOS

element projection

orbital projection

projection completeness

partial/unknown semantics
```

禁止：

```text
sum incomplete PDOS
→ claim total dominance
```

---

# 53. Band + DOS Combined

combined view不是第三 Tool。

Benchmark只能验证：

```text
exact compatible persisted Band + DOS
```

包括：

```text
source

calculation identity

structure identity

energy reference

Fermi

spin
```

不兼容时：

```text
typed no-combine
```

---

# 54. No DFT Claim

所有 N5 benchmark必须明确：

```text
N5_PLATFORM_DFT_EXECUTION = 0

N5_PLATFORM_GW_EXECUTION = 0
```

Golden fixtures 验证：

```text
supplied/imported electronic data handling
```

不是平台电子结构计算。

---

# 55. Artifact Contract Validation

每个 benchmark必须验证 exact：

```text
artifact kind

artifact contract/version

media type

tool/version

source identity

parameter provenance

units

scientific fields

checksum

warnings

lineage where applicable
```

如果 numeric value正确但 Artifact contract错：

```text
FAIL_CONTRACT
```

---

# 56. Artifact Integrity

必须有 negative evidence：

```text
tampered checksum

wrong contract

wrong source identity

stale fixture/resource

wrong Tool version
```

这些不得进入 scientific PASS path。

---

# 57. Runtime Dependency Benchmarks

对于 0.2 dependent science：

至少重点验证：

```text
N1 → N2

MSD → Diffusion
```

以及 repository 已批准的 dependent families。

必须证明 consumer：

```text
consumes persisted exact producer Artifact
```

不是重新计算 producer science。

---

# 58. Partial Execution

如果 benchmark涉及 dependent plan failure：

必须验证：

```text
producer failure
→ descendant BLOCKED_DEPENDENCY

independent branch
→ may continue
```

不得：

```text
failed dependency silently replaced by raw source
```

---

# 59. Frontend Scientific Authority

Phase 11-2 benchmark不得把：

```text
frontend chart output
```

当 expected scientific truth。

必须保持：

```text
FRONTEND_SCIENTIFIC_RECOMPUTATION = 0
```

---

# 60. Screenshot Authority

继续：

```text
SCREENSHOT_NUMERIC_SCIENTIFIC_AUTHORITY = NONE
```

截图只能支持：

```text
presentation regression
```

不能通过：

```text
looks the same
```

证明 scientific benchmark。

---

# 61. Browser Authority

Browser regression：

```text
does not promote scientific validation level
```

Phase 11-2 不负责 cross-browser numeric variance characterization。

那属于：

```text
Phase 11-3
```

---

# 62. Service Authority

Service-backed PASS用于：

```text
production persistence/runtime/storage integrity
```

不能单独证明：

```text
scientific numeric truth
```

Golden benchmark本身必须拥有 reference comparison evidence。

---

# 63. No External Reference Retrieval

Phase 11-2：

```text
EXTERNAL_REFERENCE_DOWNLOADS = 0
```

所有 scientific references必须来自：

```text
11-1 sealed local/metadata fixtures
```

如果发现 missing reference：

回：

```text
BLOCKED_REFERENCE
```

不得上网补。

---

# 64. No External Scientific API

必须：

```text
EXTERNAL_SCIENTIFIC_API_CALLS = 0
```

---

# 65. No Downloaded Code Execution

必须：

```text
DOWNLOADED_SCRIPT_EXECUTIONS = 0

NOTEBOOK_EXECUTIONS = 0

DOWNLOADED_BINARY_EXECUTIONS = 0
```

---

# 66. LLM Boundary

必须：

```text
NEW_LLM_CALL_SITES = 0

PHASE11_2_REQUIRES_LLM = NO

REAL_LLM_CALLS = 0
```

LLM 不能：

```text
judge scientific correctness

select tolerance

explain failed numeric mismatch as PASS

repair benchmark output
```

---

# 67. Benchmark Harness Is Deterministic

允许新增：

```text
benchmark runners

comparison utilities

evidence serializers

manifest validators

reference loaders
```

但：

```text
BENCHMARK_HARNESS_SCIENTIFIC_AUTHORITY = NONE
```

它只：

```text
loads sealed expected truth
runs production authority
compares
records
```

---

# 68. Benchmark Harness Security

禁止 benchmark fixture触发：

```text
Python eval

shell

filesystem escape

network

HTML

JS

iframe

module

external URL

macro execution
```

Fixture始终：

```text
INERT_DATA
```

---

# 69. Production Change Boundary

Phase 11-2 默认：

```text
PRODUCTION_SOURCE_CHANGES = 0
```

允许：

```text
tests

benchmark tooling

evidence

fixtures metadata

docs

persistent state

TASKS

results
```

---

# 70. Benchmark Failure Does Not Authorize a Fix

如果 benchmark发现 production scientific result错误：

禁止：

```text
fix production algorithm
and rerun until green
```

必须：

```text
record exact failure

freeze actual output

freeze expected output

freeze tolerance

identify affected Tool/version

identify affected Artifact contract

identify affected claims

classify severity

BLOCKED / REVIEWER_REQUIRED
```

---

# 71. Harness Defects Can Be Fixed

如果 failure被证明只是：

```text
benchmark loader bug

wrong fixture path

checksum reader bug

evidence serialization bug

test harness platform bug
```

且：

```text
sealed expected scientific truth unchanged

production scientific output unchanged

tolerance unchanged
```

可以 fix-forward harness。

必须保留 failed SHA/CI history。

---

# 72. Reference Defect

如果发现：

```text
sealed fixture is corrupted

11-1 transformation was wrong

expected value provenance incorrect
```

不能 Phase 11-2自行改。

必须：

```text
REFERENCE_DEFECT

BLOCKED / REVIEWER_REQUIRED
```

回到 reference governance。

---

# 73. Scientific Contract Defect

如果发现：

```text
current contract scientifically inconsistent
```

必须：

```text
SCIENTIFIC_CONTRACT_DEFECT
```

不能用 benchmark phase 改 science。

---

# 74. Validation-Level Update

11-2 第一次允许：

```text
evidence-derived validation-level promotion
```

但必须严格遵守 Phase 11-0 policy。

---

# 75. V1 → V2

只有 Tool已经满足所有 V1要求，并通过：

```text
CONTROLLED_REFERENCE
```

或 sealed equivalent benchmark：

才可：

```text
V1 → V2
```

---

# 76. V2 → V3

只有 Tool满足 lower-level要求，并且通过：

```text
OFFICIAL_REFERENCE
or
INDEPENDENT_REFERENCE
```

且 reference independence/provenance 已封板：

才可：

```text
V2 → V3
```

---

# 77. No V4 in Phase 11-2

必须：

```text
PHASE11_2_V4_PROMOTIONS = 0
```

因为 V4：

```text
CROSS_PLATFORM_REPRODUCIBILITY_VERIFIED
```

属于：

```text
Phase 11-3
```

---

# 78. No Level Promotion By Association

禁止：

```text
one CrystalNN benchmark passes
→ all structure Tools V3

one ML metric passes
→ all ML Tools V3

one N5 fixture passes
→ Band and DOS both promoted automatically
```

每个 Tool/version：

必须具有自己的 required benchmark evidence。

---

# 79. Multiple Benchmarks Per Tool

如果 Tool required set中：

```text
n benchmark cases
```

必须全部 required cases达到：

```text
PASS*
```

才能 promotion。

一个 positive PASS不能覆盖 negative FAIL。

---

# 80. Provisional Coverage Only

Phase 11-2 可以更新：

```text
validation level
benchmark result
```

但不得发布最终：

```text
DIRECT_VERIFIED
OFFICIAL_DERIVED_VERIFIED
REFERENCE_VERIFIED
```

产品 coverage verdict。

最终 coverage 属于：

```text
Phase 11-4
```

---

# 81. Benchmark Result Record

每个 benchmark至少保存：

```text
benchmarkId

toolId

toolVersion

executionMode

fixtureId

fixtureVersion

fixtureChecksum

referenceId

referenceVersion

referenceChecksum

expectedValues/invariants

actualValues/invariants

expectedUnits

actualUnits

toleranceId

comparisonMode

absoluteError

relativeError
where meaningful

identityStatus

contractStatus

determinismStatus

negativeCaseStatus

verdict

diagnostics

artifactRefs

evidenceRefs

runtime environment

timestamp excluded from semantic identity
```

---

# 82. Benchmark Semantic Hash

每个 result必须有：

```text
benchmarkResultHash
```

semantic identity至少包含：

```text
benchmark ID

Tool/version

fixture checksum

reference identity

expected truth

tolerance ID

actual scientific output

comparison verdict
```

不得只 hash：

```text
timestamp
filename
```

---

# 83. Golden Suite Manifest

建立：

```text
Phase11GoldenScientificBenchmarkSuite
```

至少：

```text
suiteId

suiteVersion

benchmarkManifestHash

environmentIdentity

toolCount

benchmarkCount

passCount

failCount

blockedCount

notApplicableCount

validationLevelBefore

validationLevelAfter

scientificFailureSummary

manifestHash
```

---

# 84. Evidence Directory

建立：

```text
docs/phase11/evidence/
phase11_2_golden_scientific_benchmark/
```

至少包含：

```text
baseline.txt

entry_gate.md

phase11_1_handoff_snapshot.json

benchmark_input_manifest.json

benchmark_execution_manifest.json

golden_suite_summary.json

benchmark_results.json

benchmark_result_hashes.json

tool_validation_levels_before.json

tool_validation_levels_after.json

validation_level_changes.json

positive_case_matrix.json

negative_case_matrix.json

identity_validation_matrix.json

unit_validation_matrix.json

tolerance_application_matrix.json

determinism_matrix.json

artifact_contract_matrix.json

runtime_artifact_matrix.json

dependency_benchmark_matrix.json

scientific_failures.json

blocked_benchmarks.json

no_tolerance_change_audit.md

no_reference_mutation_audit.md

no_production_change_audit.md

security.md

service_backed.md

browser_regression.md

secret_scan.txt

manifest.json
```

---

# 85. Evidence Per Benchmark

建议：

```text
benchmarks/{benchmarkId}/
```

包含：

```text
input_manifest.json

expected.json

actual.json

comparison.json

runtime.json

artifact_manifest.json

replay.json

diagnostics.txt
```

但必须遵守 repository existing convention。

不得建立第二套 conflicting evidence authority。

---

# 86. Expected vs Actual Must Be Separate

必须保存：

```text
expected
```

与：

```text
actual
```

为独立 records。

禁止 evidence只保存：

```text
difference = 0
```

而看不到 reference truth。

---

# 87. Numeric Precision in Evidence

Evidence必须保存：

```text
full comparison precision
```

不能只保存 UI rounded values。

展示可以 round。

comparison必须使用 sealed numeric precision。

---

# 88. Benchmark Ordering

Suite执行顺序必须确定性。

例如：

```text
benchmarkId lexical order
```

或 manifest sealed order。

不得根据：

```text
Registry iteration
filesystem order
test discovery accident
```

改变 authority。

---

# 89. Fail-Fast vs Continue

科学 benchmark suite不得第一个 FAIL 就停止全套。

应：

```text
continue independent benchmark cases
```

以得到完整 discrepancy matrix。

但是：

如果发现：

```text
reference corruption
fixture integrity failure
environment integrity failure
```

可能影响整个 family/suite：

必须停止 affected domain。

不能继续生成误导 evidence。

---

# 90. Aggregate Status

允许：

```text
ALL_PASS

PASS_WITH_NONBLOCKING_LIMITATIONS

SCIENTIFIC_FAILURES_PRESENT

REFERENCE_BLOCKED

ENVIRONMENT_INVALID
```

不得：

```text
mostly pass
good enough
```

---

# 91. Phase 11-2 PASS Meaning

Phase 11-2 PASS 只能表示：

```text
All reviewer-required golden scientific benchmarks
that are in the sealed Phase 11-2 scope
pass their exact identity, unit, contract,
reference and tolerance requirements,
with explicit limitations retained.
```

不能表示：

```text
all materials science is correct
```

---

# 92. Cross-Platform Is Not Yet Closed

即使 Linux CI benchmark全部 PASS：

仍不能：

```text
V4
cross-platform verified
```

Phase 11-3 才负责：

```text
Linux / Windows
variance characterization
```

---

# 93. Phase 11-3 Handoff

11-2 必须生成：

```text
Phase11_3ReproducibilityInputManifest
```

其中只包含：

```text
reference-validated benchmark cases
```

每条至少：

```text
benchmarkId

toolId/version

fixture ID/checksum

reference ID

expected truth

sealed tolerance

11-2 verdict

current validation level

target variance class

Linux baseline scientific output hash/value

required Windows comparison

presentation-only browser requirement
```

---

# 94. Failed Benchmarks Must Not Enter 11-3

如果：

```text
11-2 verdict = FAIL*
```

则不得：

```text
send to Phase 11-3 as validated baseline
```

只能：

```text
blocked pending reviewer
```

---

# 95. Acceptance Registry

建立 exact 10 项：

```text
P11V2-A01
PHASE11_1_REFERENCE_FIXTURE_HANDOFF_AND_ENTRY_AUTHORITY_CLOSURE

P11V2-A02
GOLDEN_BENCHMARK_INPUT_IDENTITY_UNIT_REFERENCE_AND_TOLERANCE_INTEGRITY

P11V2-A03
DATA_INTELLIGENCE_ML_COMPOSITION_GOLDEN_SCIENTIFIC_VALIDATION

P11V2-A04
STRUCTURE_COORDINATION_LOCAL_ENVIRONMENT_AND_XRD_GOLDEN_VALIDATION

P11V2-A05
TRAJECTORY_RDF_MSD_DIFFUSION_GOLDEN_SCIENTIFIC_VALIDATION

P11V2-A06
PHONON_BRILLOUIN_ZONE_VOLUMETRIC_GOLDEN_SCIENTIFIC_VALIDATION

P11V2-A07
ELECTRONIC_BAND_DOS_AND_COMBINED_PRESENTATION_SOURCE_VALIDATION

P11V2-A08
NEGATIVE_DETERMINISM_ARTIFACT_LINEAGE_AND_VALIDATION_LEVEL_CLOSURE

P11V2-A09
NO_PRODUCTION_CHANGE_SECURITY_SERVICE_BROWSER_REGRESSION_AND_EVIDENCE_INTEGRITY

P11V2-A10
IMPLEMENTATION_EXACT_SHA_CI_COMPLETION_ARCHIVE_AND_11_3_REVIEWER_GATE
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

如果某 family 在 sealed manifest明确：

```text
NOT_REQUIRED_FOR_11_2
```

其 acceptance必须通过：

```text
documented N/A disposition
```

而不是虚构 benchmark。

---

# 96. Queue Admission

Entry Gate PASS 后：

```text
admit exactly one Phase 11-2 task
```

要求：

```text
TASK_BLOCK_COUNT = 1

ACTIVE_TASK = Phase 11-2

PHASE_11_3_EXECUTABLE_TASK_CREATED = NO

PHASE_12_EXECUTABLE_TASK_CREATED = NO

PHASE_13_EXECUTABLE_TASK_CREATED = NO
```

---

# 97. Database Freeze

必须：

```text
new database table = 0

new database column = 0

new migration = 0

migration head =
0007_phase10m1_workspace_domain
```

Benchmark results进入：

```text
docs/evidence/test outputs
```

不是 production database。

---

# 98. API Freeze

必须：

```text
NEW_PUBLIC_API_FAMILIES = 0
```

如果 production runtime route已有：

可以用。

不得为 benchmark新增 public API。

---

# 99. Dependency Freeze

必须：

```text
new Python dependency = 0

new frontend dependency = 0

lockfile change = 0
```

Golden comparison使用：

```text
existing locked environment
```

---

# 100. Registry Freeze

必须：

```text
REGISTRY_BEFORE_11_2 = 62

REGISTRY_AFTER_11_2 = 62
```

不得：

```text
create benchmark-only Tool
```

---

# 101. DataProfile Freeze

必须：

```text
DATAPROFILE_BEFORE_11_2 = 2.4

DATAPROFILE_AFTER_11_2 = 2.4
```

---

# 102. AnalysisPlan Freeze

必须：

```text
AnalysisPlan versions =
0.1 / 0.2 unchanged
```

不得为 benchmark增加：

```text
0.3
```

---

# 103. Artifact Contract Freeze

默认：

```text
NEW_PRODUCTION_ARTIFACT_FAMILIES = 0
```

如果 benchmark证明 existing contract有 scientific defect：

BLOCKED。

不得在 11-2升级。

---

# 104. Scientific Algorithm Freeze

必须：

```text
NEW_SCIENTIFIC_ALGORITHMS = 0
```

---

# 105. UI/UX Freeze

不得做 Phase 12 工作：

```text
design system

navigation redesign

Workspace redesign

viewer redesign

Report UX redesign
```

Phase 11-2只允许必要的：

```text
test/evidence harness
```

---

# 106. Security Markers

必须：

```text
NO_PHASE11_2_ARBITRARY_CODE_EXECUTION = PASS

NO_PHASE11_2_DOWNLOADED_SCRIPT_EXECUTION = PASS

NO_PHASE11_2_NOTEBOOK_EXECUTION = PASS

NO_PHASE11_2_EXTERNAL_SCIENTIFIC_API = PASS

NO_PHASE11_2_REFERENCE_DOWNLOAD = PASS

NO_PHASE11_2_FRONTEND_SCIENTIFIC_RECOMPUTATION = PASS

NO_PHASE11_2_LLM_SCIENTIFIC_AUTHORITY = PASS

NO_BENCHMARK_FIXTURE_EXECUTION_AUTHORITY = PASS

NO_SECRET_PATTERN_HITS = PASS
```

---

# 107. Mandatory Scientific Integrity Markers

必须：

```text
PASS_DRIVEN_TOLERANCE_CHANGE = PROHIBITED

EXPECTED_VALUE_MUTATION_AFTER_COMPARISON = 0

REFERENCE_FIXTURE_MUTATIONS = 0

SCIENTIFIC_REFERENCE_SUBSTITUTIONS = 0

SCREENSHOT_NUMERIC_SCIENTIFIC_AUTHORITY = NONE

BROWSER_NUMERIC_SCIENTIFIC_AUTHORITY = NONE

SERVICE_NUMERIC_SCIENTIFIC_AUTHORITY = NONE

BENCHMARK_HARNESS_SCIENTIFIC_AUTHORITY = NONE

SELF_REFERENCE_EQUALS_INDEPENDENT_REFERENCE = NO

V4_PROMOTIONS = 0
```

---

# 108. Tool Validation Level Result

必须输出：

```text
Validation levels before 11-2

Validation levels after 11-2
```

至少：

```text
V0 count
V1 count
V2 count
V3 count
V4 count
```

11-0 baseline曾记录：

```text
V1 = 34
V2 = 28
V3/V4 promotion by 11-0 = 0
```

但 Phase 11-2 必须以 11-1 current matrix为 entry authority。

11-1不得因 reference preparation自行 promotion。

若 repository显示它错误 promotion：

```text
BLOCKED / GOVERNANCE_VIOLATION
```

---

# 109. Validation Level Change Record

每个 promotion：

```text
toolId
toolVersion

beforeLevel
afterLevel

benchmarkIds

referenceIds

referenceStrength

required criteria

evidence paths
```

不得：

```text
bulk promote domain
```

---

# 110. No Demotion Hiding

如果现有 V2 Tool benchmark FAIL：

不能：

```text
quietly demote to V1
and still Phase PASS
```

必须记录：

```text
VALIDATION_REGRESSION
```

并 BLOCK Phase 11-2 closure。

---

# 111. Benchmark Failure Severity

科学 failure至少：

```text
P0
P1
P2
```

沿用 Phase 11 governance。

典型：

```text
wrong numeric science in release-critical Tool
→ P0/P1 according sealed policy

minor non-authoritative presentation mismatch
→ not scientific benchmark failure
```

不要擅自 redefine severity。

---

# 112. Existing Scientific Wording

Benchmark PASS不得扩大 claims。

继续：

```text
coordination
= algorithm-derived

local environment
= algorithm/geometry classified

XRD
= peak correspondence

diffusion
= estimated over selected fit window

electronic
= derived from supplied/imported data
```

---

# 113. References and Citations

11-2 evidence引用：

```text
11-1 sealed referenceId
```

不要：

```text
add new web citation as substitute scientific authority
```

---

# 114. Documentation Deliverables

至少新增：

```text
docs/phase11/
phase11_2_cross_capability_golden_scientific_benchmark.md

docs/phase11/
phase11_golden_benchmark_registry.md

docs/phase11/
phase11_benchmark_result_matrix.md

docs/phase11/
phase11_validation_level_update.md

docs/phase11/
phase11_scientific_discrepancy_matrix.md

docs/phase11/
phase11_3_reproducibility_input_handoff.md

docs/phase11/
phase11_2_completion.md
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

不得改 Phase 11 governance semantic rules。

---

# 115. Persistent State

更新：

```text
PROJECT_BRIEF

DESIGN_PROGRESS

TASK_BOARD

CHANGELOG

OPEN_QUESTIONS

ARCHITECTURE_DECISIONS

TOOL_REGISTRY_NOTES
```

只记录 benchmark事实。

不得创建 11-3 executable task。

---

# 116. Test Strategy

至少四层：

```text
Layer 1:
fixture/reference integrity

Layer 2:
direct registered Adapter scientific benchmark

Layer 3:
representative QueueWorkerRuntime
+ persisted Artifact validation

Layer 4:
full regression / service/browser/security
```

---

# 117. Focused Benchmark Test Suite

建议 canonical：

```text
phase11 golden benchmark focused suite
```

必须覆盖所有：

```text
required benchmark IDs
```

不得：

```text
pytest marks skip
```

release-critical scientific benchmarks。

---

# 118. Skips

对于 Phase 11-2 required benchmark：

```text
SKIPPED = FAIL
```

除非 benchmark manifest明确：

```text
NOT_APPLICABLE
```

不得：

```text
environment skip
```

然后算 PASS。

---

# 119. Service-Backed

至少保持：

```text
PostgreSQL
Redis
MinIO
```

current CI no-skipped regression。

对于 production Runtime benchmark representative path：

必须使用：

```text
persisted plan/job/toolcall/artifact
```

验证。

Service-backed count不得低于 dynamic floor。

---

# 120. Browser Regression

必须保持：

```text
Chromium PASS

Firefox PASS

WebKit PASS

390x844 PASS
```

但：

```text
no new scientific validation level
from browser alone
```

---

# 121. Phase 11-3 Platform Work Is Deferred

Phase 11-2不要求：

```text
Windows scientific benchmark equality
```

除非 existing CI本身跑 Windows。

正式：

```text
Linux/Windows variance closure
```

留给 11-3。

---

# 122. npm Audit

如果 configured mirror：

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
PASS
```

---

# 123. Verification Commands

至少：

```powershell
git diff --check

uv lock --check

uv run python -m pytest -q

npm --prefix apps/web test

npm --prefix apps/web run typecheck

npm --prefix apps/web run build
```

以及：

```text
Phase 10 retained evidence validators

Phase 11-0 evidence integrity

Phase 11-1 evidence integrity

Phase 11-2 benchmark manifest validator

fixture checksum validator

reference checksum validator

expected-value freeze validator

tolerance registry validator

golden benchmark result validator

validation-level transition validator

determinism validator

Artifact contract validator

dependency benchmark validator

11-3 handoff validator

docs link checker

TASKS lifecycle checker

secret scan
```

---

# 124. Implementation Commit

Implementation commit包括：

```text
Phase 11-2 task admission

benchmark harness

scientific benchmark tests

benchmark results/evidence

validation-level updates

11-3 handoff

docs

persistent state

CI/evidence validators
```

不得包含：

```text
results.md final completion record
```

直到 implementation CI PASS。

---

# 125. Implementation Exact-SHA CI

push implementation。

然后：

```text
WAIT FOR IMPLEMENTATION EXACT-SHA CI
```

必须 PASS：

```text
Unit

Frontend / browser / build

PostgreSQL / Redis / MinIO

no-skipped service gate

benchmark integrity

evidence integrity
```

这是 lifecycle 中必须等待的 CI。

---

# 126. Failed Implementation Candidate

如果 CI失败：

保留：

```text
failed SHA

failed CI run

failure reason
```

然后：

```text
fix forward
```

不得：

```text
force push

rewrite history

delete failed candidate

mutate reference

mutate expected value

widen tolerance

remove failed benchmark
```

---

# 127. Completion Record

只有 implementation exact-SHA CI PASS 后：

向：

```text
results.md
```

追加完整 Phase 11-2 result。

然后：

```text
commit
push
```

按当前 lifecycle：

```text
NO ADDITIONAL WAIT REQUIRED
for completion-record CI
```

如果 CI 已自然明确失败：

不能故意忽略。

---

# 128. Queue Archive

Completion record push 后：

删除且只删除：

```text
Phase 11-2 TASK block
```

不得创建：

```text
Phase 11-3 task
```

然后：

```text
commit
push
```

不主动等待 archive CI。

没有 exact-SHA CI事实时：

最终术语使用：

```text
QUEUE_ARCHIVED
```

不要错误声称：

```text
ARCHIVED_BY_VERIFIED_QUEUE_COMMIT
```

---

# 129. Final State

成功后：

```text
Phase 11-2:
PASS /
GOLDEN_SCIENTIFIC_BENCHMARK_COMPLETE /
QUEUE_ARCHIVED

Phase 11:
IN_PROGRESS /
REFERENCE_VALIDATION_COMPLETE_FOR_SEALED_11_2_SCOPE

Phase 11-3:
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

PHASE_11_3_EXECUTABLE_TASK_CREATED = NO
```

---

# 130. Mandatory Result Markers

必须：

```text
PHASE11_2_NEW_SCIENTIFIC_TOOLS = 0

PHASE11_2_NEW_SCIENTIFIC_ALGORITHMS = 0

PHASE11_2_NEW_ARTIFACT_FAMILIES = 0

PHASE11_2_NEW_DATAPROFILE_VERSION = 0

PHASE11_2_NEW_ANALYSISPLAN_VERSION = 0

PHASE11_2_NEW_DATABASE_MIGRATIONS = 0

PHASE11_2_NEW_PUBLIC_API_FAMILIES = 0

PHASE11_2_NEW_DEPENDENCIES = 0

PHASE11_2_NEW_LLM_CALL_SITES = 0

PHASE11_2_REAL_LLM_CALLS = 0

PHASE11_2_EXTERNAL_REFERENCE_DOWNLOADS = 0

PHASE11_2_EXTERNAL_SCIENTIFIC_API_CALLS = 0

PHASE11_2_NOTEBOOK_EXECUTIONS = 0

PHASE11_2_DOWNLOADED_SCRIPT_EXECUTIONS = 0

PHASE11_2_V4_PROMOTIONS = 0
```

---

# 131. Baseline Markers

必须：

```text
REGISTRY_BEFORE_11_2 = 62
REGISTRY_AFTER_11_2 = 62

DATAPROFILE_BEFORE_11_2 = 2.4
DATAPROFILE_AFTER_11_2 = 2.4

MIGRATION_BEFORE_11_2 =
0007_phase10m1_workspace_domain

MIGRATION_AFTER_11_2 =
0007_phase10m1_workspace_domain
```

---

# 132. Benchmark Honesty Markers

必须：

```text
EXPECTED_VALUES_MUTATED_AFTER_COMPARISON = 0

REFERENCE_FIXTURES_MUTATED = 0

SCIENTIFIC_TOLERANCES_CHANGED = 0

FAILED_BENCHMARKS_REMOVED = 0

FAILED_BENCHMARKS_SKIPPED = 0

SCREENSHOT_NUMERIC_SCIENTIFIC_AUTHORITY = NONE

BROWSER_NUMERIC_SCIENTIFIC_AUTHORITY = NONE

SERVICE_NUMERIC_SCIENTIFIC_AUTHORITY = NONE

SELF_REFERENCE_EQUALS_INDEPENDENT_REFERENCE = NO

PASS_DRIVEN_TOLERANCE_CHANGE = PROHIBITED
```

---

# 133. Required results.md Structure

至少：

# Phase 11-2 Cross-Capability Golden Scientific Benchmark Suite Result

1. Conclusion
2. Phase 11-1 Baseline
3. Entry Gate
4. Phase 11-1 Lifecycle Verification
5. Benchmark Handoff Integrity
6. Benchmark Scope
7. Production Behavior Changes
8. Registry / DataProfile / Migration Baseline
9. Validation Levels Before
10. Benchmark Execution Architecture
11. Reference Integrity
12. Fixture Integrity
13. Expected-Value Freeze
14. Tolerance Integrity
15. Identity Validation
16. Unit Validation
17. Dataset Intelligence Benchmarks
18. Materials ML Benchmarks
19. Composition Space Benchmarks
20. Structure Benchmarks
21. CrystalNN Benchmarks
22. VoronoiNN Benchmarks
23. Local Environment / Polyhedra Benchmarks
24. Experimental XRD Benchmarks
25. RDF Benchmarks
26. MSD Benchmarks
27. Diffusion Benchmarks
28. Phonon Benchmarks
29. Brillouin Zone Benchmarks
30. Volumetric Benchmarks
31. Band Structure Benchmarks
32. DOS Benchmarks
33. Combined Band + DOS Benchmarks
34. Positive Case Matrix
35. Negative Case Matrix
36. Determinism Matrix
37. Runtime / Persisted Artifact Matrix
38. Dependency Validation
39. Artifact Contract Validation
40. Scientific Wording Boundaries
41. Benchmark Results
42. Exact Passes
43. Tolerance-Bounded Passes
44. Invariant Passes
45. Expected Rejections
46. Scientific Failures
47. Reference-Blocked Cases
48. Validation Levels After
49. Validation-Level Promotions
50. V4 Non-Promotion Confirmation
51. Remaining Validation Gaps
52. Phase 11-3 Handoff
53. Cross-Platform Deferred Scope
54. Evidence Inventory
55. Evidence Manifest
56. Security
57. LLM / DeepSeek
58. Database / API / Dependency Freeze
59. Tests
60. Browser Regression
61. Service-Backed Regression
62. npm Audit
63. Files Changed
64. Acceptance Registry
65. Implementation Commit
66. Implementation CI
67. Failed Candidates
68. Completion Record
69. Queue Archive
70. Queue State
71. Phase 11-3 Gate
72. Final Repository State

---

# 134. PASS Gate

只有全部满足：

```text
Phase 11-1 PASS

Phase 11-1 queue archived

Phase 11-1 implementation CI PASS

HEAD == origin/master at entry

worktree clean


Registry = 62

DataProfile = 2.4

migration = 0007


all blocking 11-2 benchmark inputs READY

critical TBD = 0

fixture checksums PASS

reference checksums PASS

expected truth frozen

units resolved

tolerances resolved


all required positive benchmarks executed

all required negative benchmarks executed

required benchmark skips = 0


identity validation PASS

unit validation PASS

Artifact contract validation PASS

determinism PASS


required numeric/invariant benchmarks PASS

required negative typed outcomes PASS


no production scientific change

no algorithm change

no Tool change

no Registry change

no DataProfile change

no migration

no API family

no dependency

no lockfile change


reference fixture mutation = 0

expected value mutation = 0

tolerance change = 0

failed benchmark removal = 0


V4 promotions = 0


Phase 11-3 reproducibility handoff complete

critical 11-3 TBD = 0


backend >= dynamic 11-1 floor

frontend >= dynamic 11-1 floor

service >= dynamic 11-1 floor

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

evidence PASS

docs links PASS

security PASS

secret scan PASS


P11V2 acceptance = 10/10


implementation exact-SHA CI PASS

completion record committed/pushed

queue archive committed/pushed


TASK_BLOCK_COUNT = 0

Phase 11-3 task absent

Phase 12 task absent

Phase 13 task absent
```

才能：

```text
Phase 11-2 = PASS
```

---

# 135. Scientific Failure Gate

如果任何 required benchmark：

```text
FAIL_IDENTITY

FAIL_UNIT

FAIL_NUMERIC

FAIL_INVARIANT

FAIL_CONTRACT

FAIL_DETERMINISM

FAIL_UNEXPECTED_SUCCESS
```

则 Phase 11-2不能宣告 PASS。

必须：

```text
Phase 11-2:
BLOCKED / SCIENTIFIC_DISCREPANCY_REVIEW_REQUIRED
```

---

# 136. Reference Failure Gate

如果发现：

```text
wrong expected truth

corrupted fixture

wrong source/version

wrong unit

wrong reference transformation
```

必须：

```text
BLOCKED / REFERENCE_GOVERNANCE_REVIEW_REQUIRED
```

不得在 11-2 修 reference。

---

# 137. Production Scientific Defect Gate

如果 reference可靠而 production science错误：

必须保留：

```text
actual
expected
delta
tolerance
Tool/version
Artifact contract
fixture/reference IDs
```

然后停止。

不得：

```text
patch algorithm
```

直到 reviewer另开 correction phase。

---

# 138. Non-Blockers

通常不阻塞：

```text
presentation-only Tool has no numeric benchmark

Phase 11-3 Windows variance not yet executed

browser pixel differences

official historical example remains mapping-only
when not required by 11-2

non-release P2 reference remains limited
when explicitly allowed by sealed benchmark scope
```

必须记录。

---

# 139. First Required Output

执行开始后第一步必须输出：

```text
Phase 11-2 Entry Gate
+ Phase 11-1 Reference / Fixture Handoff Verification
+ Golden Benchmark Admission Matrix
```

至少确认：

1. Phase 11-1 implementation SHA；
2. Phase 11-1 implementation CI；
3. Phase 11-1 completion SHA；
4. Phase 11-1 queue archive SHA；
5. HEAD/origin/master/worktree；
6. Registry 62；
7. DataProfile 2.4；
8. migration 0007；
9. TASK_BLOCK_COUNT=0；
10. Phase 11-3 task absent；
11. Phase 11-1 reference registry；
12. Phase 11-1 fixture registry；
13. source checksums；
14. fixture checksums；
15. reference independence matrix；
16. tolerance registry；
17. exact benchmark input manifest；
18. required benchmark count；
19. blocked benchmark count；
20. critical TBD count；
21. validation levels before；
22. no production scientific change is required to execute benchmark；
23. no external reference/network work remains；
24. no new dependency required。

只有全部满足才输出：

```text
PHASE_11_2_ENTRY_GATE = PASS

PHASE_11_1_REVIEWER_DEPENDENCY = VERIFIED

PHASE_11_2_QUEUE_ADMISSION = AUTHORIZED

PHASE_11_2_REFERENCE_INPUTS = SEALED

PHASE_11_2_EXPECTED_VALUES = SEALED

PHASE_11_2_TOLERANCES = SEALED

PHASE_11_2_NUMERIC_VALIDATION_AUTHORITY = AUTHORIZED

PHASE_11_2_PRODUCTION_SCIENCE_CHANGE_AUTHORITY = NONE

PHASE_11_2_READINESS =
READY_FOR_GOLDEN_SCIENTIFIC_BENCHMARK_EXECUTION
```

---

# 140. Required Execution Sequence

严格：

```text
verify 11-1 lifecycle

→ verify benchmark handoff

→ admit exactly one 11-2 task

→ snapshot validation levels before

→ validate reference checksums

→ validate fixture checksums

→ validate expected values/invariants

→ validate tolerance IDs

→ run scientific positive benchmarks

→ run scientific negative benchmarks

→ run deterministic replay

→ run Artifact contract validation

→ run representative persisted Runtime validation

→ run dependency scientific validation

→ calculate evidence-derived validation-level transitions

→ produce complete golden benchmark result matrix

→ produce 11-3 reproducibility handoff

→ run full regression

→ run service-backed regression

→ run browser regression

→ run security/evidence validators

→ create implementation commit

→ push

→ wait for implementation exact-SHA CI

→ if implementation CI PASS:
   append completion result

→ commit/push completion record

→ archive only Phase 11-2 task

→ commit/push queue archive

→ return complete result

→ stop
```

---

# 141. Stop Rule

完成 Phase 11-2 后：

不得：

```text
execute Windows cross-platform scientific comparison

run Phase 11-3 variance closure

publish final Honest Coverage

execute Phase 11-4

close Phase 11

execute Phase 11-5

start Phase 12 UI/UX
```

最终停在：

```text
Phase 11-3:
REVIEWER_GATE / AWAITING REVIEWER PROMPT
```

等待 reviewer。



---END---

---TASK---
 状态：待处理

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
