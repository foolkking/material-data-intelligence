---TASK---
 状态：待处理

 # Phase 10H-4：Phonon Eigenvector Contract

进入 Phase 10H-4：Phonon Eigenvector Contract。

可以默认：

* Phase 10H：Phonon Contract 已完成并通过
* Phase 10H-1：Phonon Bands 已完成并通过
* Phase 10H-2：Phonon DOS 已完成并通过
* Phase 10H-3：Combined Band + DOS 已完成并通过
* `phase10h.phonon_band.v1` 已稳定
* `phase10h.phonon_dos.v1` 已稳定
* `phase10h.phonon_band_dos.v1` 已稳定
* `phase10h.phonon_summary.v1` 已稳定
* `phase10h.phonon_manifest.v1` 已稳定
* reciprocal lattice convention已固定
* `2π` policy已固定
* q-point coordinate system已固定
* q-point path、segment和branch identity已固定
* canonical frequency unit已固定
* imaginary-frequency encoding已固定
* zero tolerance已固定
* structure identity已固定
* canonical atom ordering已固定
* source calculation lineage已固定
* NAC metadata policy已固定
* band / DOS compatibility validator已稳定
* Combined Band + DOS产品已具备正式Registry、Planner、PlanValidator、Runtime、API、Frontend和Browser证据
* Phase 10G trajectory viewer保持稳定
* static viewer和trajectory viewer的周期身份、measurement、supercell、camera、clipping、performance和security均保持稳定
* Phase 10 Closure Regression Pack保持通过
* 当前branch、HEAD、working tree和Phase 10H-3 CI可视为正确且clean

本阶段不需要重复Phase 10H-3 baseline检查。

本阶段主要目标：

> 建立统一、严格、可验证、可扩展且可安全消费的phonon eigenvector contract，明确一个phonon mode如何通过q-point、branch、structure identity和atom ordering进行唯一绑定，并固定complex eigenvector表示、normalization、mass weighting、phase convention、units、degeneracy、NAC方向、displacement reconstruction、caps、determinism和security，为下一阶段Phonon Animation提供稳定科学基础。

本阶段只完成：

* phonon mode identity
* eigenvector schema
* q-point / branch binding
* atom ordering
* complex number representation
* per-atom displacement vectors
* normalization policy
* mass-weighting policy
* phase convention
* gauge / global phase invariance policy
* degeneracy policy
* NAC direction binding
* displacement reconstruction contract
* amplitude semantics
* unit policy
* validation
* caps
* deterministic serialization
* fixtures
* reference tests
* security
* docs
* evidence
* readiness closure

本阶段不实现phonon animation，不实现3D displacement renderer，不实现mode playback。

---

# 1. 本阶段定位

Phase 10H-4是phonon动态3D能力的科学合同阶段。

它位于：

```text
Phase 10H      Phonon Contract
Phase 10H-1    Phonon Bands
Phase 10H-2    Phonon DOS
Phase 10H-3    Combined Band + DOS
Phase 10H-4    Phonon Eigenvector Contract
Phase 10H-5    Phonon Animation
```

本阶段必须回答：

* 一个phonon mode如何唯一标识
* mode如何绑定具体q-point
* mode如何绑定具体branch
* q-point与branch index是否足以唯一定位mode
* mode是否必须绑定structure identity
* eigenvector的atom顺序如何定义
* eigenvector是否是complex vector
* complex值如何序列化
* real / imaginary components如何排列
* 每个atom有几个分量
* eigenvector是否mass weighted
* eigenvector normalization如何定义
* global complex phase如何处理
* 同一mode不同phase表示是否视为等价
* degenerate modes如何保持独立身份
* NAC和Gamma方向如何绑定mode
* imaginary-frequency mode如何表示
* 如何从eigenvector重构用于显示的real-space displacement
* animation amplitude是否具有物理长度单位
* display displacement是否是科学原始量还是derived representation
* large eigenvector payload如何受cap限制
* malformed、ambiguous或incompatible eigenvector如何拒绝

本阶段不是：

* phonon eigenvector来源adapter阶段
* phonopy parser阶段
* pymatgen eigenvector adapter阶段
* phonon animation阶段
* renderer阶段
* GPU阶段
* trajectory阶段
* thermal-property阶段
* vibrational intensity阶段
* Raman / IR阶段
* neutron scattering阶段

---

# 2. 本阶段完成目标

必须完成以下十五类工作：

1. **Existing mode/eigenvector infrastructure audit**
2. **Phonon mode identity contract**
3. **Q-point and branch binding**
4. **Structure and atom-order binding**
5. **Complex eigenvector representation**
6. **Normalization policy**
7. **Mass-weighting policy**
8. **Phase and gauge policy**
9. **Degeneracy and branch-subspace policy**
10. **Imaginary-mode and NAC binding**
11. **Displacement reconstruction contract**
12. **Caps、validation和typed errors**
13. **Deterministic serialization and reference tests**
14. **Security and compatibility boundaries**
15. **Docs、evidence和readiness closure**

本阶段必须产生真实schema、typed model、validator、canonical serializer和reference tests。

如果最终只有文档、公式草图或示例JSON，没有可执行validator和tests，本阶段必须判定为FAIL。

---

# 3. 严格禁止范围

本阶段不得实现：

* phonon animation
* 3D displacement renderer
* mode playback
* play / pause
* phase slider
* amplitude slider
* arrow renderer
* atom motion renderer
* trajectory conversion
* GIF/MP4 export
* video export
* eigenvector file parser
* phonopy eigenvector adapter
* pymatgen eigenvector adapter
* vasprun.xml eigenvector parser
* arbitrary library object ingestion
* Brillouin renderer
* phonon mode browser UI
* Raman intensity
* IR intensity
* neutron scattering intensity
* thermal conductivity
* free energy
* entropy
* heat capacity
* Grüneisen parameters
* quasi-harmonic approximation
* force constants calculation
* dynamical matrix calculation
* external solver invocation
* notebook execution
* script execution
* real LLM
* remote artifact loading
* arbitrary plugin parser

不得：

* 修改Phase 10H band contract语义
* 修改Phase 10H DOS contract语义
* 修改Combined Band + DOS contract语义
* 将eigenvector塞入trajectory contract
* 将phonon mode伪装成trajectory frame
* 使用q-point index和branch index但不绑定artifact identity
* 仅使用frequency值作为mode identity
* 仅使用high-symmetry label作为q-point identity
* 仅使用species ordering代替atom ordering
* 静默重排atoms
* 静默重排branches
* 静默合并degenerate modes
* 静默移除complex phase
* 静默取eigenvector实部
* 静默丢弃imaginary component
* 静默归一化而不记录
* 静默mass-unweight
* 静默mass-weight
* 静默选择phase
* 静默将imaginary mode转成positive mode
* 静默改变eigenvector handedness
* 静默接受不同structure identity
* 静默接受不同source calculation lineage
* 静默接受不同NAC方向
* 允许NaN或Infinity
* 允许无限modes
* 允许无限atoms
* 允许任意complex nesting
* 允许外部URL
* 允许artifact JavaScript
* 允许callback
* 允许任意公式执行
* 允许任意unit expression
* 允许任意matrix expression
* 允许私有路径
* 允许secret
* 将eigenvector contract完成标记为animation READY

允许：

* schema
* model
* validator
* canonical serializer
* complex-number helper
* normalization helper
* reconstruction reference helper
* fixtures
* tests
* docs
* evidence

---

# 4. 必读实现

开始后直接阅读当前真实代码。

## 4.1 Phase 10H Contracts

必须阅读：

* phonon band schema
* q-point schema
* branch identity
* source lineage
* structure identity
* atom ordering
* frequency unit
* imaginary encoding
* zero tolerance
* NAC metadata
* summary
* manifest
* deterministic serializer
* typed error framework
* caps

必须确认：

* mode是否已有预留字段
* band branches中是否已有mode references
* q-point是否已有stable identity
* source artifacts是否有content hash
* branch index是否稳定
* atom order是否来自canonical structure

## 4.2 Phase 10H-1 Band Implementation

阅读：

* band adapter
* branch preservation
* q-point ordering
* source-stable branch index
* segment handling
* labels
* NAC metadata
* source calculation identity
* summary
* artifact hashes

确认：

* q-point identity能否稳定引用
* branch index是否在所有source中一致
* crossing和degeneracy如何记录
* band artifact是否可被mode contract引用

## 4.3 Existing Complex Number Models

搜索：

```bash
rg -n "complex|real.*imag|imaginary|Complex|phase|eigenvector|eigenmode|normalization|mass weighted|mass_weighted" backend packages apps tests
```

确认：

* 是否已有complex schema
* 是否已有real/imag pair
* 是否已有NumPy complex serialization
* 是否已有matrix/vector numeric caps
* 是否已有canonical floating serialization
* 是否已有complex tolerance helper

## 4.4 Existing Structure Identity

搜索：

```bash
rg -n "structure_identity|atom_order|canonical atom|species order|siteIndex|atomIndex" backend packages apps tests
```

确认：

* canonical atom index定义
* species顺序
* atomic mass来源
* isotope支持
* occupancy限制
* partial occupancy policy
* structure hash

## 4.5 Existing Physics Dependencies

搜索：

```bash
rg -n "phonopy|pymatgen.*phonon|eigenvector|dynamical matrix|mass weighting|atomic mass" pyproject.toml uv.lock backend packages tests
```

确认：

* phonopy对象如何表示eigenvectors
* pymatgen对象如何表示eigendisplacements
* eigenvector array shape
* mass-weighted语义
* normalization语义
* complex dtype
* dependency版本
* test-only reference可能性

---

# 5. 修改前输出审计

修改代码前必须输出：

# Phase 10H-4 Phonon Eigenvector Contract Pre-Implementation Audit

## 1. Existing Mode Identity Infrastructure

* band artifact identity:
* q-point identity:
* branch identity:
* source calculation identity:
* structure identity:
* atom ordering:
* NAC metadata:
* current gaps:

## 2. Existing Complex Data Infrastructure

* complex number schema:
* real/imag representation:
* canonical serialization:
* numeric validation:
* finite checks:
* tolerance helpers:
* reusable pieces:

## 3. Existing Eigenvector-Related Code

* models:
* parsers:
* adapters:
* fixtures:
* docs:
* library objects:
* experimental code:
* naming conflicts:
* reusable pieces:

## 4. Scientific Risks

至少列出：

* q-point identity ambiguity
* branch crossing ambiguity
* degenerate subspace ambiguity
* source branch reorder
* atom-order mismatch
* mass-weighting ambiguity
* normalization ambiguity
* global complex phase ambiguity
* phase gauge drift
* real-part-only data loss
* imaginary component loss
* source convention mismatch
* Cartesian basis mismatch
* NAC direction mismatch
* Gamma mode ambiguity
* imaginary-frequency mode handling
* atomic mass source mismatch
* isotope ambiguity
* displacement unit ambiguity
* arbitrary animation amplitude overclaim
* complex payload size blowup
* deterministic hash instability

## 5. Selected Strategy

说明：

* mode identity:
* q-point binding:
* branch binding:
* artifact binding:
* atom ordering:
* complex representation:
* normalization:
* mass weighting:
* phase convention:
* gauge equivalence:
* degeneracy:
* NAC:
* displacement reconstruction:
* amplitude:
* units:
* caps:
* determinism:
* security:

## 6. Planned Files

列出：

* eigenvector schema/model
* mode reference schema
* complex number schema
* validator
* serializer
* normalization helper
* phase canonicalization helper，若批准
* reconstruction helper
* fixtures
* backend tests
* shared/frontend types，若需要
* evidence
* docs
* persistent

审计后直接继续执行，不等待确认。

---

# 6. Schema Family

建议新增：

```text
phase10h.phonon_mode_ref.v1
phase10h.phonon_eigenvector.v1
phase10h.phonon_eigenvector_set.v1
phase10h.phonon_eigenvector_summary.v1
phase10h.phonon_eigenvector_manifest.v1
```

建议复用或新增共享complex schema：

```text
phase10h.complex_scalar.v1
phase10h.complex_vector3.v1
```

如已有全局shared complex schema，必须复用，不得建立冲突类型。

---

# 7. Mode Identity

一个phonon mode不得仅用：

```text
qpoint_index + branch_index
```

作为全局唯一身份。

必须至少绑定：

```text
band artifact identity
+
q-point identity
+
branch identity
+
structure identity
+
source calculation identity
```

建议：

```json
{
  "schema_version": "phase10h.phonon_mode_ref.v1",
  "mode_id": "content-derived-id",
  "band_artifact": {
    "artifact_id": "...",
    "sha256": "..."
  },
  "structure_identity": "sha256:...",
  "phonon_calculation_identity": "sha256:...",
  "qpoint_index": 0,
  "qpoint_coordinates": [0.0, 0.0, 0.0],
  "branch_index": 0,
  "frequency": -1.2,
  "frequency_unit": "terahertz",
  "nac_direction": null
}
```

要求：

* mode ID content-derived
* q-point index合法
* coordinates与band artifact对应
* branch index合法
* frequency与band artifact对应
* frequency tolerance固定
* artifact hash验证
* no random UUID
* no timestamp

---

# 8. Mode ID生成

推荐：

```text
mode_id =
hash(
  band_artifact_sha256
  + qpoint_index
  + branch_index
  + nac_direction
)
```

具体canonicalization必须固定。

不得将以下内容作为唯一mode identity：

* frequency
* label
* q-point label
* branch display name
* source filename
* array position
* UI selection index

Mode ID必须在同一artifact内稳定。

如果band artifact内容变化：

* mode ID必须变化
* stale mode reference必须拒绝

typed error：

```text
PHONON_MODE_REFERENCE_STALE
```

---

# 9. Q-Point Binding

Mode reference必须绑定：

* q-point index
* q-point coordinates
* coordinate system
* reciprocal convention
* optional label
* segment identity，若path mode
* NAC direction，若Gamma方向相关

不得只绑定：

```text
Γ
```

因为：

* 多个segment可能重复Γ
* NAC方向可能不同
* 同一坐标可能在不同path context出现

validator必须检查：

```text
mode_ref.qpoint_index
```

与band artifact中的q-point完全一致或在固定tolerance内一致。

---

# 10. Branch Binding

Mode reference必须绑定：

* branch index
* source branch identity，若有
* frequency
* branch scope
* degeneracy group，若有

Branch identity原则继续沿用Phase 10H：

```text
source-stable branch index
```

不得：

* 按frequency重新排序
* 按eigenvector相似度重新编号
* 按degeneracy合并
* 在validator阶段追踪crossing

如果source branch identity缺失：

* 使用canonical branch index
* 明确记录source-order-only

---

# 11. Frequency Binding

Mode reference中的frequency必须与band artifact匹配。

验证：

```text
abs(mode.frequency - band.frequency[q,b]) <= tolerance
```

tolerance必须：

* application-owned
* 单位转换后比较
* 与frequency zero tolerance不同
* 记录在policy中

不得用UI显示精度作为tolerance。

失败：

```text
PHONON_MODE_FREQUENCY_MISMATCH
```

---

# 12. Structure Binding

Eigenvector必须绑定：

* structure identity
* atom count
* species ordering
* atom ordering policy
* optional atomic masses
* isotope metadata，若支持

要求：

```text
eigenvector.structure_identity
==
band.structure_identity
```

以及：

```text
eigenvector.atom_count
==
band.atom_count
```

species逐index一致。

不得只比较composition。

---

# 13. Atom Ordering

建议：

```text
atom_ordering = canonical_structure_order
```

每个atom index：

```text
0 .. N-1
```

必须与canonical structure artifact一致。

Eigenvector payload中的第`i`个atom displacement必须绑定：

```text
canonical atom index i
```

不得：

* 根据species分组重排
* 根据坐标排序
* 根据atomic mass排序
* 根据source library输出重新排列而不记录

如果source顺序不同，后续adapter必须显式映射并记录。

本阶段只定义合同。

---

# 14. Atomic Mass Policy

Mass weighting依赖atomic masses。

必须明确mass来源。

建议：

```text
atomic_mass_source
```

枚举：

```text
standard_atomic_weight
isotope_specific
source_provided
```

第一版推荐：

```text
source_provided or canonical structure mass metadata
```

如structure没有mass：

* 可以使用批准的periodic table reference
* 必须记录source和版本
* 不得隐藏

必须明确单位：

```text
atomic_mass_unit = unified_atomic_mass_unit
```

不得：

* 使用atomic number代替mass
* 忽略isotope信息
* 混用kg和amu而不转换

---

# 15. Partial Occupancy Policy

第一版建议：

```text
partial occupancy eigenvectors: unsupported
```

原因：

* atom identity不稳定
* mass weighting不明确
* disorder语义复杂

typed error：

```text
PHONON_EIGENVECTOR_PARTIAL_OCCUPANCY_UNSUPPORTED
```

不得自动使用平均质量而无合同。

---

# 16. Complex Number Representation

推荐使用显式real / imaginary components。

Complex scalar：

```json
{
  "real": 0.123,
  "imag": -0.456
}
```

Complex vector3：

```json
{
  "real": [0.1, 0.2, 0.3],
  "imag": [0.0, -0.1, 0.2]
}
```

或per-component：

```json
[
  {"real": 0.1, "imag": 0.0},
  {"real": 0.2, "imag": -0.1},
  {"real": 0.3, "imag": 0.2}
]
```

必须选择一个并固定。

推荐：

```text
real[3] + imag[3]
```

优势：

* shape清晰
* 易于验证
* 更紧凑
* 前后端一致

不得使用：

* `"0.1+0.2i"`字符串
* Python complex repr
* `[real, imag]`但无schema说明
* arbitrary nested arrays
* NaN/Infinity

---

# 17. Eigenvector Payload Shape

单个mode建议：

```text
[atom_count, 3 complex components]
```

Schema示例：

```json
{
  "schema_version": "phase10h.phonon_eigenvector.v1",
  "mode": {},
  "structure_identity": "...",
  "atom_count": 2,
  "species": ["Si", "Si"],
  "coordinate_basis": "cartesian",
  "normalization": {
    "type": "unit_norm",
    "mass_weighted": true
  },
  "eigenvectors": [
    {
      "atom_index": 0,
      "real": [0.1, 0.0, 0.0],
      "imag": [0.0, 0.1, 0.0]
    },
    {
      "atom_index": 1,
      "real": [-0.1, 0.0, 0.0],
      "imag": [0.0, -0.1, 0.0]
    }
  ],
  "phase": {},
  "provenance": {},
  "warnings": [],
  "security": {}
}
```

要求：

* 每atom恰好一项
* atom index连续
* no duplicates
* real shape 3
* imag shape 3
* finite
* deterministic order

---

# 18. Coordinate Basis

第一版推荐只支持：

```text
cartesian
```

即eigenvector components在real-space Cartesian basis中表达。

必须固定：

* x/y/z为global Cartesian axes
* 与real-space lattice坐标系一致
* 不使用fractional displacement
* 不使用local atomic frame
* 不使用reciprocal basis

如source为fractional components，后续adapter必须显式转换。

不得：

* 每个atom使用不同basis
* 省略basis
* 将q-point reciprocal coordinates与eigenvector components混淆

---

# 19. Eigenvector Unit

Eigenvector通常是无量纲normal mode vector，但不同库语义不同。

必须明确合同。

建议：

```text
eigenvector_component_unit = dimensionless
```

而用于显示的real-space displacement通过：

```text
display_amplitude × normalized_eigenvector
```

得到angstrom位移。

必须区分：

* raw eigenvector
* physical normal coordinate
* display displacement
* animation amplitude

不得声称raw eigenvector本身单位是angstrom，除非source明确且contract支持。

---

# 20. Normalization Policy

必须定义受控枚举。

建议支持：

```text
unit_norm
mass_weighted_unit_norm
source_normalized
```

但canonical内部最好只保留一种。

推荐canonical：

```text
mass_weighted_unit_norm
```

或：

```text
unit_norm_unweighted
```

必须根据现有库审计决定。

关键是明确：

## Unweighted Unit Norm

```text
Σ_i |e_i|² = 1
```

## Mass-Weighted Unit Norm

可能表示：

```text
Σ_i m_i |u_i|² = 1
```

或：

```text
Σ_i |e_i|² = 1
```

但`e_i = sqrt(m_i) u_i`

必须严格写清。

不得仅用：

```text
normalized = true
```

这种含糊字段。

---

# 21. 推荐Canonical Normalization

推荐合同明确区分：

```text
stored_vector_representation
```

枚举：

```text
mass_weighted_eigenvector
cartesian_displacement_eigenvector
```

以及：

```text
normalization_type
```

例如：

```json
{
  "stored_vector_representation": "mass_weighted_eigenvector",
  "normalization_type": "euclidean_unit_norm"
}
```

定义：

```text
Σ_i |e_i|² = 1
```

real-space displacement方向：

```text
u_i = e_i / sqrt(m_i)
```

然后可再整体normalize或乘display amplitude。

该策略常见且适合明确重构。

但必须根据现有依赖真实语义审计，不得凭假设选择。

---

# 22. Mass Weighting Policy

必须显式记录：

```text
mass_weighted = true / false
```

如果true，必须定义：

* mass unit
* source
* reconstruction公式
* zero/invalid mass行为

建议：

```text
u_i = e_i / sqrt(m_i)
```

其中：

* `e_i`为stored mass-weighted eigenvector
* `u_i`为unweighted displacement direction

不得：

* 重复除以sqrt(m)
* 忘记除以sqrt(m)
* 使用atomic number
* 使用species平均mass而忽略isotope

必须有reference fixtures验证轻/重原子差异。

---

# 23. Global Phase / Gauge Ambiguity

Complex eigenvector存在global phase自由度：

```text
e_i → e_i exp(iφ)
```

物理mode不变。

合同必须明确：

* raw source phase可保留
* mode identity不得依赖global phase
* equivalence validator必须允许global phase等价
* deterministic hash是否对phase敏感必须固定

推荐：

## Raw Artifact

保留source phase。

## Scientific Equivalence

允许全局phase等价。

## Canonical Serialization

可选择phase canonicalization，或明确hash对source phase敏感。

更推荐：

```text
canonicalize global phase for deterministic scientific representation
```

但实现必须谨慎。

---

# 24. Phase Canonicalization

如果实现canonical phase，建议规则：

1. 找到第一个幅值大于phase tolerance的complex component
2. 旋转全体eigenvector，使该component成为非负实数
3. 若该component实部接近0，使用固定tie-break
4. 所有components应用相同phase rotation
5. 记录canonicalization applied

必须：

* tolerance固定
* traversal order固定
* atom-major、x/y/z顺序固定
* 对近零vector拒绝
* reference-tested

不得：

* 每atom单独phase canonicalize
* 每component独立取绝对值
* 破坏相对phase

如果本阶段不实现phase canonicalization，也必须明确：

```text
source phase preserved
scientific equivalence ignores global phase
canonical hash remains phase-sensitive
```

但这会影响determinism和cross-source equivalence，需要记录。

---

# 25. Recommended Phase Policy

建议本阶段采用：

```text
source_phase_preserved = true
canonical_global_phase = true
```

即：

* provenance可记录source phase
* canonical payload使用统一global phase
* 原始source数据不作为scientific artifact重复保存，除非policy批准

或采用：

```text
source_phase_preserved = true
canonical_global_phase = false
```

但必须证明deterministic replay在同一source下稳定。

最终选择必须在审计后固定。

---

# 26. Phase Convention Metadata

建议：

```json
{
  "phase_convention": {
    "global_phase_policy": "first_nonzero_component_real_positive",
    "component_order": "atom_major_xyz",
    "tolerance": 1e-12,
    "canonicalized": true
  }
}
```

不得开放任意phase function。

---

# 27. Degenerate Modes

Degenerate modes存在basis rotation自由度。

即使frequency相同，individual eigenvectors可能因source不同而旋转。

合同必须明确：

* 每个source-declared branch仍保持独立mode
* 不自动合并degenerate modes
* 不声称跨source individual eigenvector一一相等
* degenerate subspace可作为group记录
* scientific equivalence可比较subspace，但本阶段不必完整实现

建议：

```json
{
  "degeneracy": {
    "group_id": "q0-group1",
    "branch_indices": [1, 2],
    "source_declared": true,
    "basis_arbitrary_within_subspace": true
  }
}
```

不得：

* 根据频率相等自动生成权威group
* 对degenerate modes排序并声称物理唯一
* 合并后丢失vectors

---

# 28. Degenerate Subspace Equivalence

本阶段可以只定义policy，不必实现完整线性代数比较。

建议：

```text
individual mode equivalence:
  valid for nondegenerate modes after global phase alignment

degenerate mode equivalence:
  defined at subspace level, not individual vector level
```

Future adapter/benchmark可以使用：

* overlap matrix
* principal angles
* projector comparison

但本阶段不实现官方benchmark。

必须标记：

```text
degenerate_cross_source_mode_matching: DEFERRED_BY_DESIGN
```

---

# 29. Imaginary-Frequency Modes

Imaginary mode仍有eigenvector。

必须：

* frequency保持negative-real encoding
* eigenvector照常complex表示
* 不取frequency绝对值
* 不修改mode identity
* displacement reconstruction不声称真实周期振动

对imaginary mode，未来animation只能是：

```text
illustrative displacement along unstable mode direction
```

而不是：

```text
physical harmonic oscillation
```

本阶段必须提前固定语义。

建议metadata：

```json
{
  "mode_character": "imaginary",
  "animation_semantics": "unstable_mode_displacement_preview"
}
```

但animation字段可推迟到Phase 10H-5。

---

# 30. Gamma and NAC Direction

Gamma点可能因NAC方向不同产生不同eigenvectors。

Mode identity必须包含：

* NAC enabled
* Gamma direction
* direction coordinate system
* direction normalization

建议：

```json
{
  "nac": {
    "enabled": true,
    "direction": [1.0, 0.0, 0.0],
    "direction_coordinate_system": "reciprocal_cartesian"
  }
}
```

不得：

* 用同一mode ID表示不同Gamma方向
* 省略方向
* 自动normalize后不记录
* 混用fractional/cartesian方向

---

# 31. Direction Vector Policy

如果NAC direction存在：

* shape 3
* finite
* nonzero
* canonical normalization
* coordinate system明确

建议canonical：

```text
unit reciprocal Cartesian direction
```

即只保留方向，不保留大小。

必须记录source direction。

typed errors：

```text
PHONON_EIGENVECTOR_NAC_DIRECTION_INVALID
PHONON_EIGENVECTOR_NAC_DIRECTION_MISMATCH
```

---

# 32. Displacement Reconstruction

本阶段必须定义从stored eigenvector到display displacement的公式。

对于complex eigenvector：

```text
e_i = a_i + i b_i
```

在q-point `q`、atom equilibrium position `r_i`、cell translation `R_l`下，real displacement可写为：

```text
u_{l,i}(t)
=
A Re[
  v_i
  exp(i(q·R_l - ωt + φ))
]
```

但第一版animation可能只显示单cell mode。

合同必须区分：

* Gamma-point single-cell preview
* non-Gamma supercell wave preview
* static phase snapshot
* time-dependent animation

本阶段只定义，不实现。

---

# 33. Phase 10H-5 Reconstruction Readiness

必须为下一阶段提供明确字段：

* q-point vector
* eigenvector
* frequency
* mode phase
* atom equilibrium positions
* lattice
* mass weighting
* normalization
* display amplitude
* cell image offset
* NAC direction
* imaginary mode semantics

不得让Phase 10H-5猜测这些语义。

---

# 34. Display Displacement Contract

建议新增derived helper contract：

```text
phase10h.phonon_displacement_frame.v1
```

但本阶段只可定义最小schema，不实现viewer。

示例：

```json
{
  "schema_version": "phase10h.phonon_displacement_frame.v1",
  "mode_id": "...",
  "phase_radians": 0.0,
  "display_amplitude_angstrom": 0.1,
  "cell_images": [[0, 0, 0]],
  "positions": [],
  "displacements": []
}
```

注意：

* 这是derived display artifact
* 不是trajectory
* 不是scientific source of truth
* 不得写入`phase10g.trajectory.v1`

是否现在正式建立该schema，应根据Phase 10H-5设计需要决定。

---

# 35. Display Amplitude Semantics

必须区分：

## Eigenvector Norm

无量纲科学表示。

## Normal Coordinate Amplitude

可能具有质量和能量相关物理语义，本阶段不实现。

## Display Amplitude

用户界面中用于可视化的最大位移标度。

推荐单位：

```text
angstrom
```

必须标记：

```text
display_only = true
```

不得声称：

* 对应真实热振幅
* 对应零点振幅
* 对应温度下平均振幅
* 对应真实MD位移

除非未来另有严格计算。

---

# 36. Amplitude Reference Policy

未来animation需要明确display amplitude如何作用。

推荐：

```text
max_atom_displacement
```

即canonicalized unweighted displacement方向先normalize，使：

```text
max_i ||u_i|| = 1
```

然后：

```text
display displacement = amplitude_angstrom × u_i
```

优势：

* UI可预测
* 不依赖atom count
* 不让轻原子位移无限放大

但这与scientific eigenvector normalization不同，必须标记为display-derived。

也可使用RMS amplitude，但必须固定。

本阶段必须选定或明确留给10H-5。

推荐现在固定：

```text
display amplitude reference = max_cartesian_displacement
```

---

# 37. Real-Space Phase Snapshot

对于complex eigenvector，给定phase `φ`：

```text
d_i(φ) = Re[u_i exp(iφ)]
```

必须：

* `φ`单位radian
* bounded/canonical
* periodic modulo `2π`
* no arbitrary expression

建议phase canonical range：

```text
[0, 2π)
```

未来animation可以随时间更新φ。

本阶段只定义helper/reference tests。

---

# 38. Non-Gamma q-Point Policy

非Gamma mode在单primitive cell中无法完整表达空间相位。

必须明确：

```text
non-Gamma mode visualization requires cell translations or a commensurate supercell
```

本阶段必须定义：

* q·R phase factor
* cell image offsets
* reciprocal convention
* whether q uses fractional reciprocal coordinates
* commensurability policy

不得让Phase 10H-5只移动primitive cell原子并声称完整模式。

---

# 39. Cell Translation Phase

若q-point为reciprocal fractional：

```text
q = (h,k,l)
```

cell image：

```text
R = n1 a + n2 b + n3 c
```

在crystallographic fractional convention下phase可能：

```text
2π(hn1 + kn2 + ln3)
```

具体必须与Phase 10H reciprocal convention一致。

必须写出精确公式并reference test。

不得混淆：

* physics reciprocal basis含2π
* fractional reciprocal coordinates
* Cartesian q-vector

---

# 40. Commensurate Supercell Policy

Phase 10H-5可能需要构造与q-point相容的supercell。

本阶段只定义合同边界。

建议：

```text
commensurate_supercell: DEFERRED_TO_PHASE_10H_5
```

但必须记录：

* arbitrary q-point不保证有限小supercell
* display cell count必须受cap限制
* 不得自动无限扩展
* 不能将非commensurate preview声称为exact periodic mode

---

# 41. Eigenvector Set Contract

除了单mode，建议支持一组modes。

```json
{
  "schema_version": "phase10h.phonon_eigenvector_set.v1",
  "band_artifact": {},
  "structure_identity": "...",
  "atom_count": 2,
  "mode_count": 6,
  "modes": [],
  "provenance": {},
  "warnings": [],
  "security": {}
}
```

必须限制：

* mode count
* total complex values
* artifact bytes
* no duplicate mode ID
* deterministic mode order

推荐order：

```text
qpoint_index ascending
then branch_index ascending
then NAC direction canonical order
```

---

# 42. Sparse vs Full Mode Sets

第一版允许：

```text
subset
full
```

建议字段：

```text
mode_scope
```

## subset

只包含部分q-points/branches。

## full

覆盖artifact声明的全部modes。

不得让subset被误报为full。

Summary必须显示：

* included mode count
* expected mode count
* coverage

---

# 43. Eigenvector Summary

建议新增：

```text
phase10h.phonon_eigenvector_summary.v1
```

至少包含：

```json
{
  "schema_version": "phase10h.phonon_eigenvector_summary.v1",
  "structure_identity": "...",
  "band_artifact_sha256": "...",
  "atom_count": 2,
  "mode_count": 6,
  "mode_scope": "subset",
  "qpoint_count": 1,
  "frequency_unit": "terahertz",
  "complex_representation": "real_imag_vectors",
  "coordinate_basis": "cartesian",
  "stored_vector_representation": "mass_weighted_eigenvector",
  "normalization_type": "euclidean_unit_norm",
  "global_phase_policy": "first_nonzero_component_real_positive",
  "imaginary_mode_count": 1,
  "degenerate_group_count": 1,
  "warnings": []
}
```

不得复制完整vectors。

---

# 44. Eigenvector Manifest

建议：

```text
phase10h.phonon_eigenvector_manifest.v1
```

artifact顺序建议：

1. `phonon_eigenvectors.json`
2. `phonon_eigenvector_summary.json`
3. `phonon_eigenvector_validation_report.json`
4. `phonon_eigenvector_manifest.json`

本阶段不输出：

* animation
* renderer
* JS
* HTML
* trajectory
* video

Manifest必须包含：

* schema
* media type
* size
* sha256
* band artifact reference
* structure identity
* source calculation identity
* mode count
* security markers

---

# 45. Validation Report

建议新增：

```text
phase10h.phonon_eigenvector_validation_report.v1
```

至少记录：

* artifact reference check
* structure identity
* atom ordering
* mode reference
* q-point binding
* branch binding
* frequency binding
* complex shape
* normalization
* mass weighting
* phase canonicalization
* degeneracy
* NAC direction
* caps
* deterministic status

不得包含完整vectors。

---

# 46. Normalization Validation

必须根据declared representation检查。

## Euclidean Unit Norm

```text
Σ_i (|x_i|² + |y_i|² + |z_i|²) ≈ 1
```

## Mass-Weighted Displacement Norm

根据合同公式检查。

必须：

* nonzero vector
* finite norm
* tolerance固定
* no automatic rescale unless explicitly approved

推荐：

```text
invalid normalization → typed failure
```

或允许：

```text
source normalized + canonical conversion
```

但必须记录scale factor。

不得静默归一化。

---

# 47. Canonical Normalization Conversion

如果source normalization不同但可安全转换：

允许：

```text
source vector
→ compute norm
→ divide by norm
→ canonical vector
```

必须记录：

* source normalization
* target normalization
* scale factor
* pre-norm
* post-norm
* tolerance

但如果mass-weighting语义未知：

* 不得转换
* typed failure

---

# 48. Complex Equivalence Reference

必须实现独立reference helper，至少验证：

* identical vectors
* global phase-equivalent vectors
* negative sign equivalent，等价于phase π
* non-equivalent vectors
* near-zero components
* degenerate group不按individual mode判等

推荐overlap：

```text
overlap = |<u|v>|
```

对于normalized nondegenerate modes：

```text
overlap ≈ 1
```

表示global phase等价。

不得使用逐component直接相等作为唯一科学等价。

---

# 49. Typed Errors

至少定义：

```text
PHONON_EIGENVECTOR_SCHEMA_UNSUPPORTED
PHONON_EIGENVECTOR_BAND_REFERENCE_REQUIRED
PHONON_EIGENVECTOR_BAND_HASH_MISMATCH
PHONON_EIGENVECTOR_MODE_REFERENCE_INVALID
PHONON_EIGENVECTOR_MODE_REFERENCE_STALE
PHONON_EIGENVECTOR_QPOINT_MISMATCH
PHONON_EIGENVECTOR_BRANCH_MISMATCH
PHONON_EIGENVECTOR_FREQUENCY_MISMATCH
PHONON_EIGENVECTOR_STRUCTURE_MISMATCH
PHONON_EIGENVECTOR_ATOM_COUNT_MISMATCH
PHONON_EIGENVECTOR_ATOM_ORDER_MISMATCH
PHONON_EIGENVECTOR_PARTIAL_OCCUPANCY_UNSUPPORTED
PHONON_EIGENVECTOR_COMPLEX_SHAPE_INVALID
PHONON_EIGENVECTOR_NONFINITE
PHONON_EIGENVECTOR_ZERO_NORM
PHONON_EIGENVECTOR_NORMALIZATION_UNSUPPORTED
PHONON_EIGENVECTOR_NORMALIZATION_INVALID
PHONON_EIGENVECTOR_MASS_WEIGHTING_UNSUPPORTED
PHONON_EIGENVECTOR_ATOMIC_MASS_INVALID
PHONON_EIGENVECTOR_PHASE_POLICY_UNSUPPORTED
PHONON_EIGENVECTOR_PHASE_CANONICALIZATION_FAILED
PHONON_EIGENVECTOR_DEGENERACY_INVALID
PHONON_EIGENVECTOR_NAC_DIRECTION_INVALID
PHONON_EIGENVECTOR_NAC_DIRECTION_MISMATCH
PHONON_EIGENVECTOR_MODE_DUPLICATE
PHONON_EIGENVECTOR_MODE_LIMIT_EXCEEDED
PHONON_EIGENVECTOR_NUMERIC_LIMIT_EXCEEDED
PHONON_EIGENVECTOR_ARTIFACT_LIMIT_EXCEEDED
PHONON_EIGENVECTOR_EXTERNAL_REFERENCE_FORBIDDEN
```

---

# 50. Warnings

建议：

```text
PHONON_EIGENVECTOR_SOURCE_PHASE_CANONICALIZED
PHONON_EIGENVECTOR_SOURCE_NORMALIZATION_CONVERTED
PHONON_EIGENVECTOR_ATOMIC_MASS_SOURCE_DEFAULTED
PHONON_EIGENVECTOR_DEGENERATE_BASIS_ARBITRARY
PHONON_EIGENVECTOR_MODE_SCOPE_PARTIAL
PHONON_EIGENVECTOR_IMAGINARY_MODE
PHONON_EIGENVECTOR_NAC_DIRECTION_REQUIRED_FOR_GAMMA
PHONON_EIGENVECTOR_CROSS_SOURCE_EQUIVALENCE_LIMITED
PHONON_EIGENVECTOR_NON_GAMMA_SUPERCELL_REQUIRED
```

warning排序必须稳定。

---

# 51. Caps

必须定义application-owned caps。

至少：

* max atoms
* max modes
* max q-points represented
* max complex components
* max total numeric values
* max degeneracy groups
* max members per degeneracy group
* max provenance bytes
* max warnings
* max artifact bytes
* max source labels
* max NAC directions

计算：

```text
modes × atoms × 3 × 2
```

即real/imag numeric count。

必须overflow-safe。

必须在allocation前检查。

---

# 52. Deterministic Ordering

必须固定：

* mode order
* atom order
* component order
* real/imag order
* degeneracy group order
* NAC direction order
* warning order
* manifest order
* provenance order

Component order：

```text
atom-major
x
y
z
```

Global phase canonicalization遍历顺序必须与此一致。

不得依赖：

* dictionary iteration
* NumPy memory layout
* source library object order，除非已canonicalize
* current timestamp
* random UUID

---

# 53. Floating Serialization

必须复用项目canonical float policy。

要求：

* no NaN
* no Infinity
* stable decimal representation
* negative zero policy固定
* tolerance不进入serialization变化
* complex components稳定

必须明确：

```text
-0.0
```

是否canonicalize为：

```text
0.0
```

推荐统一为`0.0`，但需与现有serializer一致。

---

# 54. Independent Reference Tests

必须建立独立reference路径。

至少验证：

* complex norm
* mass unweighting
* global phase rotation
* phase canonicalization
* overlap equivalence
* displacement snapshot
* q·R phase
* Gamma mode
* non-Gamma mode
* negative frequency mode metadata
* deterministic hash

不得使用production helper生成expected再验证自己。

---

# 55. Reference Fixtures

新增small、deterministic fixtures。

至少：

## 55.1 Gamma Real Mode

* 2 atoms
* purely real
* no NAC
* unit norm

## 55.2 Gamma Complex Mode

* nonzero real/imag
* phase canonicalization

## 55.3 Global Phase Equivalent Pair

* vectors differ by`exp(iφ)`
* equivalence true

## 55.4 Negative Sign Pair

* vectors differ by-1
* equivalence true

## 55.5 Non-Equivalent Pair

* overlap below threshold

## 55.6 Mass-Weighted Binary Structure

* light and heavy atom
* unweighting reference

## 55.7 Imaginary Mode

* negative frequency
* valid eigenvector
* unstable-mode semantics

## 55.8 Degenerate Pair

* same frequency
* source-declared group
* arbitrary basis warning

## 55.9 NAC Gamma Direction Modes

* same q-point
* different directions
* distinct mode IDs

## 55.10 Non-Gamma Mode

* q-point fractional
* cell phase reference

## 55.11 Atom Order Mismatch

## 55.12 Frequency Mismatch

## 55.13 Zero-Norm Vector

## 55.14 Invalid Shape

## 55.15 Nonfinite Complex Component

## 55.16 Over-Cap Synthetic

不得提交大型真实eigenvector datasets。

---

# 56. Unit Tests

至少覆盖：

## Mode Reference

* valid
* stale band hash
* invalid q-point
* invalid branch
* frequency mismatch
* duplicate mode ID
* NAC direction difference

## Structure

* identity match
* mismatch
* atom count mismatch
* species ordering mismatch
* partial occupancy rejection
* isotope metadata

## Complex Shape

* valid real/imag arrays
* wrong length
* missing component
* nonfinite
* negative zero
* deterministic serialization

## Normalization

* valid unit norm
* invalid norm
* zero norm
* canonical conversion
* scale factor
* tolerance

## Mass Weighting

* weighted
* unweighted
* invalid mass
* light/heavy atom
* isotope-specific mass

## Phase

* source preserved
* canonicalized
* first nonzero component
* tie-break
* global phase equivalent
* negative sign equivalent
* per-atom phase corruption rejection

## Degeneracy

* valid group
* invalid branch member
* duplicate membership
* source-declared
* arbitrary basis warning

## NAC

* disabled
* enabled valid direction
* zero direction
* mismatched direction
* canonical normalization

## Reconstruction

* Gamma snapshot
* complex phase
* non-Gamma cell phase
* amplitude scaling
* max-displacement normalization
* imaginary-mode semantics

## Caps

* atoms
* modes
* complex values
* degeneracy groups
* bytes
* overflow

## Security

* external URL
* callback-like metadata
* formula string
* HTML label
* private path
* oversized metadata

---

# 57. Cross-Language Contract Tests

如果future frontend或renderer会消费eigenvectors，必须至少完成：

* backend canonical fixture validation
* generated shared types或frontend type guard
* enum parity
* shape parity
* finite checks
* mode identity parity
* warning order parity
* deterministic serialization parity，若架构支持

Frontend不得重新定义：

* normalization enum
* mass-weighting enum
* phase policy enum
* coordinate basis enum
* NAC direction semantics

Backend必须是科学validator权威。

---

# 58. Compatibility with Phonon Band

必须验证：

* band artifact hash
* structure identity
* q-point index
* q-point coordinates
* branch index
* frequency
* unit
* imaginary encoding
* zero tolerance
* NAC
* source lineage

不得允许eigenvector脱离band artifact存在为正式mode。

可以支持standalone eigenvector only if contract明确，但本阶段推荐不支持。

---

# 59. Compatibility with Combined Band + DOS

Combined product可以未来提供mode selection入口，但本阶段只定义：

* selected mode reference
* band artifact binding
* combined artifact reference可选

不得将DOS projection绑定为eigenvector identity。

不得因DOS存在而改变eigenvector。

---

# 60. Compatibility with Trajectory

必须明确：

* phonon eigenvector不是trajectory
* displacement snapshots不是trajectory scientific artifact
* animation frame是derived display state
* trajectory interpolation和phonon phase evolution语义不同
* trajectory playback speed不能直接定义phonon physical time
* phonon mode频率与display phase关系需由10H-5定义

不得写入：

```text
phase10g.trajectory.v1
```

并声称科学等价。

---

# 61. Security

必须验证：

* no artifact JavaScript
* no artifact HTML
* no callbacks
* no shader
* no module
* no eval
* no Function constructor
* no arbitrary formula execution
* no arbitrary matrix expression
* no arbitrary unit expression
* no external URL
* no remote eigenvector
* no notebook execution
* no script execution
* no real LLM
* no pickle
* no arbitrary Python object
* no unbounded nested arrays
* no metadata recursion abuse
* no private paths
* no secrets
* no telemetry upload

必须输出：

```text
NO_EXTERNAL_NETWORK_REQUESTS
NO_SECRET_PATTERN_HITS
```

---

# 62. Evidence目录

新增：

```text
docs/phase10h/evidence/phase10h4_phonon_eigenvector_contract/
```

至少包含：

```text
README.md
phonon_mode_ref_schema.json
phonon_eigenvector_schema.json
phonon_eigenvector_set_schema.json
phonon_eigenvector_summary_schema.json
phonon_eigenvector_manifest_schema.json
complex_scalar_schema.json
complex_vector3_schema.json
mode_identity_policy.json
qpoint_branch_binding_policy.json
atom_ordering_policy.json
complex_representation_policy.json
normalization_policy.json
mass_weighting_policy.json
atomic_mass_policy.json
global_phase_policy.json
phase_canonicalization_policy.json
degeneracy_policy.json
nac_direction_policy.json
imaginary_mode_policy.json
displacement_reconstruction_policy.json
display_amplitude_policy.json
non_gamma_mode_policy.json
caps.json
gamma_real_mode_result.json
gamma_complex_mode_result.json
global_phase_equivalent_result.json
negative_sign_equivalent_result.json
non_equivalent_result.json
mass_weighted_result.json
imaginary_mode_result.json
degenerate_pair_result.json
nac_direction_result.json
non_gamma_phase_result.json
atom_order_mismatch_result.json
frequency_mismatch_result.json
zero_norm_result.json
invalid_shape_result.json
over_cap_result.json
frontend_backend_validation_comparison.json
deterministic_serialization.json
security_audit.json
network_audit.json
artifact_hashes.json
```

不得保存：

* 大型eigenvector datasets
* raw binary arrays
* library object dumps
* local paths
* tokens
* secrets
* remote URLs
* notebook outputs
* crash dumps

---

# 63. Documentation

新增：

```text
docs/phase10h/phase10h4_phonon_eigenvector_contract.md
docs/phase10h/phase10h4_phonon_mode_identity.md
docs/phase10h/phase10h4_qpoint_branch_binding.md
docs/phase10h/phase10h4_atom_ordering.md
docs/phase10h/phase10h4_complex_representation.md
docs/phase10h/phase10h4_normalization.md
docs/phase10h/phase10h4_mass_weighting.md
docs/phase10h/phase10h4_global_phase_and_gauge.md
docs/phase10h/phase10h4_degenerate_modes.md
docs/phase10h/phase10h4_nac_direction.md
docs/phase10h/phase10h4_imaginary_modes.md
docs/phase10h/phase10h4_displacement_reconstruction.md
docs/phase10h/phase10h4_display_amplitude.md
docs/phase10h/phase10h4_non_gamma_modes.md
docs/phase10h/phase10h4_caps.md
docs/phase10h/phase10h4_security.md
docs/phase10h/phase10h4_evidence.md
docs/phase10h/phase10h4_readiness_matrix.md
```

更新：

```text
docs/index.md
docs/13_SHARED_SCHEMA_SPEC.md
persistent/DESIGN_PROGRESS.md
persistent/TASK_BOARD.md
persistent/CHANGELOG.md
persistent/OPEN_QUESTIONS.md
persistent/TOOL_REGISTRY_NOTES.md
persistent/ARCHITECTURE_DECISIONS.md
```

必须记录：

* schema family
* mode identity
* band artifact binding
* q-point binding
* branch binding
* frequency binding
* atom ordering
* complex representation
* coordinate basis
* normalization
* mass weighting
* atomic mass source
* phase canonicalization
* global phase equivalence
* degeneracy limits
* NAC direction
* imaginary-mode semantics
* displacement reconstruction
* display amplitude
* non-Gamma supercell requirement
* caps
* animation deferred
* parser/adapter deferred
* formal dynamic product deferred

---

# 64. Readiness Matrix

最终必须逐项判断：

* mode reference schema
* eigenvector schema
* eigenvector set schema
* summary schema
* manifest schema
* complex scalar
* complex vector3
* mode ID
* band artifact binding
* q-point binding
* branch binding
* frequency binding
* structure identity
* atom count
* species ordering
* atom ordering
* partial occupancy policy
* atomic mass source
* isotope metadata
* coordinate basis
* complex representation
* normalization
* canonical normalization conversion
* mass weighting
* mass unweighting
* global phase policy
* phase canonicalization
* scientific phase equivalence
* degeneracy metadata
* degenerate subspace policy
* NAC direction
* imaginary mode semantics
* displacement reconstruction
* display amplitude
* non-Gamma phase
* commensurate supercell policy
* caps
* deterministic serialization
* validator
* fixtures
* reference comparison
* security
* eigenvector parser
* eigenvector adapter
* mode selection UI
* animation renderer
* phonon animation
* formal dynamic product registration

推荐期望：

```text
mode reference schema: READY
eigenvector schema: READY
eigenvector set schema: READY
summary schema: READY
manifest schema: READY
complex representation: READY
mode identity: READY
band binding: READY
q-point binding: READY
branch binding: READY
frequency binding: READY
structure identity: READY
atom ordering: READY
atomic mass policy: READY
coordinate basis: READY
normalization policy: READY
mass weighting policy: READY
global phase policy: READY
phase canonicalization: READY or PARTIAL_READY
scientific phase equivalence: READY
degeneracy policy: READY
NAC direction policy: READY
imaginary mode semantics: READY
displacement reconstruction: READY
display amplitude policy: READY
non-Gamma mode policy: READY
caps: READY
deterministic serialization: READY
validator: READY
fixtures: READY
reference comparison: READY
security: READY

eigenvector parser: NOT_READY
eigenvector adapter: NOT_READY
mode selection UI: NOT_READY
animation renderer: NOT_READY
phonon animation: NOT_READY
formal dynamic phonon product: NOT_READY
```

---

# 65. Checks

至少运行：

```bash
git diff --check
uv lock --check

uv run python -m pytest -q

npm --prefix apps/web test
npm --prefix apps/web run typecheck
npm --prefix apps/web run build
```

并单独运行：

* mode reference schema tests
* eigenvector schema tests
* complex representation tests
* band binding tests
* q-point binding tests
* branch binding tests
* frequency binding tests
* structure identity tests
* atom ordering tests
* atomic mass tests
* normalization tests
* mass weighting tests
* phase canonicalization tests
* global phase equivalence tests
* degeneracy tests
* NAC direction tests
* imaginary mode tests
* displacement reconstruction tests
* non-Gamma phase tests
* display amplitude tests
* caps/overflow tests
* deterministic serialization tests
* frontend/backend contract comparison
* artifact validator tests
* security scan
* network audit
* Phase 10 Closure Regression Pack
* Phase 10G regression
* Phase 10H contract regression
* Phase 10H-1 band regression
* Phase 10H-2 DOS regression
* Phase 10H-3 combined regression
* static viewer regression
* trajectory viewer regression
* service-backed integration
* no-skipped assertion

本阶段不要求phonon animation browser evidence，因为尚未实现animation。

必须如实记录：

* passed
* failed
* skipped
* unavailable

不得把skipped写成passed。

---

# 66. Commit / CI

完成contract、validator、tests、evidence和docs后：

```bash
git status --short
git diff --stat
git add <only Phase 10H-4 related files>
git commit -m "Define phonon eigenvector contracts"
git push origin master
```

等待current HEAD CI。

必须确认：

* backend unit success
* frontend tests success
* frontend typecheck success
* frontend build success
* eigenvector contract tests success
* phase/mass-weighting reference tests success
* Phase 10 Closure success
* Phase 10G regression success
* Phase 10H contract success
* Phase 10H-1 success
* Phase 10H-2 success
* Phase 10H-3 success
* static viewer regression success
* trajectory viewer regression success
* service-backed integration success
* no-skipped assertion success
* origin/master matches HEAD
* git status clean

不得伪造：

* commit
* CI run
* tests
* evidence
* git clean状态

---

# 67. 最终报告格式

完成后必须输出：

# Phase 10H-4 Phonon Eigenvector Contract Result

## 1. Conclusion

PASS / PARTIAL_PASS / FAIL

## 2. Baseline

* Phase 10H-3 assumed complete:
* branch:
* initial HEAD:
* initial status:
* final HEAD:
* final status:

## 3. Schema Family

* mode reference:
* eigenvector:
* eigenvector set:
* summary:
* manifest:
* complex scalar:
* complex vector:
* current versions:

## 4. Mode Identity

* mode ID:
* band artifact binding:
* artifact hash:
* q-point index:
* q-point coordinates:
* branch index:
* frequency:
* NAC direction:
* content-derived identity:
* stale reference policy:

## 5. Structure / Atom Ordering

* structure identity:
* atom count:
* species ordering:
* canonical atom order:
* partial occupancy:
* isotope metadata:
* mismatch behavior:

## 6. Complex Representation

* representation:
* real shape:
* imaginary shape:
* component order:
* coordinate basis:
* finite validation:
* negative zero:
* serialization:

## 7. Normalization

* stored representation:
* normalization type:
* norm formula:
* tolerance:
* source conversion:
* scale factor:
* zero norm:
* invalid behavior:

## 8. Mass Weighting

* mass weighted:
* mass source:
* mass unit:
* isotope handling:
* reconstruction formula:
* light/heavy atom reference:
* invalid mass behavior:

## 9. Global Phase / Gauge

* source phase:
* canonical phase:
* canonicalization rule:
* component traversal order:
* tolerance:
* global phase equivalence:
* negative sign equivalence:
* hash sensitivity:

## 10. Degeneracy

* source-declared groups:
* branch identities:
* basis arbitrariness:
* individual matching:
* subspace matching:
* cross-source limitation:

## 11. Frequency / Imaginary Modes

* frequency binding:
* unit:
* match tolerance:
* imaginary encoding:
* imaginary-mode semantics:
* near-zero:
* acoustic modes:

## 12. NAC Direction

* enabled:
* direction:
* coordinate system:
* normalization:
* mode identity impact:
* mismatch behavior:

## 13. Displacement Reconstruction

* raw eigenvector:
* unweighted direction:
* phase snapshot:
* q-point phase:
* cell translation:
* Gamma:
* non-Gamma:
* imaginary mode:
* derived display state:

## 14. Display Amplitude

* unit:
* display-only:
* normalization reference:
* maximum displacement:
* physical amplitude claim:
* bounds:
* future animation:

## 15. Mode Set

* scope:
* mode count:
* ordering:
* duplicate prevention:
* coverage:
* full/subset:
* caps:

## 16. Caps

* atoms:
* modes:
* q-points:
* complex values:
* degeneracy groups:
* artifact bytes:
* provenance:
* warnings:
* overflow:

## 17. Validation

* schema:
* mode ref:
* artifact binding:
* structure:
* atoms:
* complex shape:
* normalization:
* mass weighting:
* phase:
* degeneracy:
* NAC:
* reconstruction:
* caps:
* security:

## 18. Determinism

* mode order:
* atom order:
* component order:
* phase canonicalization:
* warning order:
* manifest order:
* float serialization:
* hashes:

## 19. Fixtures

* Gamma real:
* Gamma complex:
* phase-equivalent:
* negative-sign equivalent:
* non-equivalent:
* mass weighted:
* imaginary:
* degenerate:
* NAC direction:
* non-Gamma:
* atom-order mismatch:
* frequency mismatch:
* zero norm:
* invalid shape:
* over-cap:

## 20. Reference Comparison

* complex norm:
* mass unweighting:
* phase rotation:
* overlap:
* phase canonicalization:
* displacement snapshot:
* q·R phase:
* deterministic hash:
* backend/frontend:
* differences:

## 21. Security

* artifact JS:
* HTML:
* callbacks:
* formulas:
* matrix expressions:
* external references:
* object construction:
* metadata:
* caps:
* private paths:
* secrets:
* network:
* markers:

## 22. Evidence

* directory:
* schemas:
* identity:
* atom ordering:
* complex representation:
* normalization:
* mass weighting:
* phase:
* degeneracy:
* NAC:
* reconstruction:
* fixtures:
* reference comparison:
* determinism:
* security:
* hashes:

## 23. Tests

* schemas:
* mode identity:
* band binding:
* q-point:
* branch:
* frequency:
* structure:
* atom order:
* masses:
* complex:
* normalization:
* mass weighting:
* phase:
* equivalence:
* degeneracy:
* NAC:
* imaginary:
* reconstruction:
* non-Gamma:
* amplitude:
* caps:
* security:
* backend full:
* frontend full:
* typecheck:
* build:
* Phase 10 closure:
* Phase 10G:
* Phase 10H:
* Phase 10H-1:
* Phase 10H-2:
* Phase 10H-3:
* static viewer:
* trajectory viewer:
* service-backed:
* no-skipped:
* lock:
* diff:

## 24. Files

* schemas/models:
* complex helpers:
* validators:
* serializers:
* normalization helpers:
* mass-weighting helpers:
* phase helpers:
* reconstruction helpers:
* fixtures:
* backend tests:
* shared/frontend tests:
* evidence:
* docs:
* persistent:
* dependencies/lockfile:

## 25. Deferred

明确列出：

* phonopy eigenvector parser
* pymatgen eigenvector adapter
* vasprun.xml eigenvector adapter
* source atom-order remapping
* full degenerate-subspace matching
* commensurate supercell construction
* non-Gamma exact supercell renderer
* mode selection UI
* arrow renderer
* displacement renderer
* animation phase controls
* animation amplitude controls
* playback
* GIF/MP4 export
* LO-TO directional animation
* Raman / IR activity
* neutron scattering
* thermal properties
* official benchmark validation
* formal dynamic phonon product registration

## 26. Readiness

* mode identity:
* band binding:
* q-point/branch:
* structure:
* atom order:
* complex representation:
* normalization:
* mass weighting:
* global phase:
* degeneracy:
* NAC:
* imaginary modes:
* reconstruction:
* amplitude:
* caps:
* validator:
* fixtures:
* security:
* parser:
* adapter:
* mode UI:
* animation renderer:
* phonon animation:
* formal dynamic product:

## 27. Commit / CI

* commit:
* HEAD:
* CI run:
* backend:
* frontend:
* typecheck:
* build:
* eigenvector contract:
* reference tests:
* Phase 10 closure:
* Phase 10G:
* Phase 10H:
* Phase 10H-1:
* Phase 10H-2:
* Phase 10H-3:
* static viewer:
* trajectory viewer:
* service-backed:
* no-skipped:
* origin:
* status:

## 28. Whether allowed to enter next phase

允许 / 不允许

下一阶段：

```text
Phase 10H-5：Phonon Animation
```

下一阶段只实现：

* approved eigenvector source adapter
* mode selection
* q-point / branch binding
* displacement reconstruction
* Gamma and non-Gamma display policy
* animation phase
* display amplitude
* atom motion
* optional displacement arrows
* bounded supercell
* lifecycle
* performance
* browser evidence
* accessibility
* formal dynamic phonon product registration

下一阶段不得实现：

* thermal properties
* Raman / IR
* neutron scattering
* force constants calculation
* phonon calculation execution
* arbitrary trajectory conversion

---

# 68. PASS 判定

PASS必须满足：

* 有真实mode reference schema
* 有真实eigenvector schema
* 有真实eigenvector set schema
* 有summary和manifest schema
* mode identity绑定band artifact hash
* q-point binding明确
* branch binding明确
* frequency binding明确
* stale reference可拒绝
* structure identity严格
* atom count严格
* species ordering严格
* canonical atom order明确
* partial occupancy policy明确
* complex representation明确
* real/imag shape明确
* coordinate basis明确
* normalization公式明确
* mass weighting语义明确
* atomic mass source明确
* global phase policy明确
* phase canonicalization完成或明确PARTIAL_READY
* scientific equivalence支持global phase
* degenerate mode policy明确
* individual mode与subspace等价边界明确
* NAC direction进入mode identity
* imaginary mode语义明确
* displacement reconstruction公式明确
* non-Gamma q·R phase明确
* display amplitude语义明确
* display displacement不被误称为physical amplitude
* caps明确
* overflow protection完成
* deterministic serialization完成
* validators完成
* fixtures完整
* independent reference完成
* no artifact JS
* no external URL
* no arbitrary formula execution
* no secret hits
* Phase 10 Closure不回退
* Phase 10G不回退
* Phase 10H contract不回退
* Phase 10H-1不回退
* Phase 10H-2不回退
* Phase 10H-3不回退
* static viewer不回退
* trajectory viewer不回退
* tests通过
* CI通过
* origin/master等于HEAD
* git status clean

PARTIAL_PASS仅允许：

* global phase canonicalization标记PARTIAL_READY，但source phase、equivalence和deterministic replay完整
* isotope-specific mass明确DEFERRED_BY_DESIGN，但standard/source-provided mass完整
* full degenerate subspace matching明确deferred
* non-Gamma commensurate supercell构造明确deferred
* frontend完整validator未实现，但shared types和backend权威validator完整
* npm audit因既有registry问题不可用

FAIL包括：

* 只有文档，没有validator
* mode identity不绑定band artifact
* q-point/branch binding含糊
* 只用frequency作为mode identity
* atom order不明确
* complex imaginary部分被丢弃
* 只保存real part
* normalization不明确
* mass weighting不明确
* 静默mass-unweight
* 静默归一化
* global phase被错误视为不同物理mode
* 每atom独立phase canonicalize
* degenerate modes被静默合并
* NAC方向被忽略
* imaginary mode被转成positive mode
* non-Gamma mode没有空间phase语义
* display amplitude被声称为真实物理振幅
* eigenvector写入trajectory contract
* 无caps
* 允许NaN/Infinity
* 允许external URL
* 提前实现animation导致范围膨胀
* Phase 10H-3回退
* CI失败却声明PASS


---END---

---TASK---
 状态：待处理
# Phase 10H-5：Phonon Animation

进入 Phase 10H-5：Phonon Animation。

可以默认以下阶段均已严肃执行、完成、验收并通过 current-HEAD CI：

* Phase 10F：Production Structure Viewer
* Phase 10F-17：Periodic Crystal Inspection
* Phase 10F-18：Canonical Periodic Bond Topology
* Phase 10F-19：Periodic Scene Integration
* Phase 10G：Trajectory Contract
* Phase 10G-1：Trajectory Parser / Adapter
* Phase 10G-2：Trajectory Viewer
* Phase 10G-3：Trajectory Performance / Browser Evidence
* Phase 10H：Phonon Contract
* Phase 10H-1：Phonon Bands
* Phase 10H-2：Phonon DOS
* Phase 10H-3：Combined Band + DOS
* Phase 10H-4：Phonon Eigenvector Contract

可以默认当前仓库、branch、HEAD、working tree、origin/master 和 Phase 10H-4 CI 均正确且 clean，但仍必须记录实际基线，不得编造 commit、HEAD、测试数或 CI run。

本阶段必须产生真实实现，不是 planning、readiness、contract-only 或 evidence-only 阶段。

---

## 1. 本阶段总目标

实现正式、科学语义明确、资源受限、可验证、可访问、可通过真实浏览器使用的 Phonon Animation 产品能力。

必须完成从已有 phonon artifacts 到动画 viewer 的完整链路：

```text
phonon band artifact
        +
phonon eigenvector artifact
        +
canonical structure identity
        ↓
mode compatibility validation
        ↓
phonon animation package
        ↓
persisted AnalysisPlan / QueueWorkerRuntime
        ↓
formal Tool Registry adapter
        ↓
frontend phonon animation viewer
        ↓
mode selection / phase animation / supercell
        ↓
browser, API, performance and security evidence
```

本阶段的核心不是“让原子随便移动”，而是保证动画中的每一个原子位移都严格来源于 Phase 10H-4 已固定的：

* mode identity
* band artifact binding
* q-point identity
* branch identity
* structure identity
* canonical atom ordering
* complex eigenvector
* normalization
* mass-weighting semantics
* global phase convention
* NAC direction
* imaginary-mode semantics
* non-Gamma spatial phase
* display-amplitude semantics
* displacement reconstruction formula

前端不得自行猜测或重新定义这些科学语义。

---

## 2. 本阶段必须实现

必须实现或正式接入：

* `phonon.animation`
* animation package schema
* animation package validator
* mode/eigenvector/structure compatibility validator
* bounded supercell resolution
* complex displacement reconstruction consumption
* Gamma mode animation
* bounded non-Gamma commensurate mode animation
* stable real-frequency mode playback
* imaginary-mode visualization policy
* mode selector
* q-point selector
* branch selector
* phase slider
* amplitude/display-scale slider
* play / pause
* speed control
* loop
* supercell display
* vector overlay
* optional bounded displacement trail
* atom inspector integration
* periodic identity integration
* band-to-animation handoff
* WebGL lifecycle cleanup
* reduced-motion behavior
* deterministic fixed-phase screenshot
* Tool Registry
* Planner routing
* PlanValidator
* QueueWorkerRuntime
* API execution
* frontend product integration
* browser evidence
* performance evidence
* security evidence
* docs and persistent updates
* current-HEAD CI closure

---

## 3. 本阶段禁止范围

不得实现或宣称：

* phonon calculation
* force-constant calculation
* dynamical-matrix calculation
* DFPT
* finite-displacement calculation
* phonopy workflow execution
* VASP / Quantum ESPRESSO execution
* arbitrary Python execution
* notebook execution
* uploaded script execution
* remote phonon service
* external API fetching
* artifact JavaScript
* artifact-provided shader
* artifact-provided GLSL
* artifact-provided HTML
* artifact-provided CSS
* artifact-provided module
* artifact-provided callback
* arbitrary mathematical expression evaluation
* `eval`
* `new Function`
* remote texture
* CDN asset
* external URL
* dynamic bond inference per animation frame
* reactive trajectory
* variable atom count
* structure editing
* phonon eigenvector editing
* mode mixing editor
* degenerate-subspace rotation editor
* physical temperature sampling
* quantum nuclear amplitude
* zero-point amplitude calculation，除非仓库已有经过验证的独立合同；默认禁止
* finite-temperature Bose–Einstein amplitude
* anharmonic phonon
* phonon lifetime
* thermal conductivity
* electron–phonon coupling
* Brillouin zone viewer
* volumetric rendering
* charge/spin density
* isosurface
* Fermi surface
* production video encoding
* MP4/WebM export
* GIF export
* persisted structure mutation
* unrestricted supercell generation
* general integer-supercell search without caps
* silent approximation of incompatible q-points
* silent dropping of imaginary components
* silent mass unweighting
* silent renormalization
* treating imaginary modes as stable physical oscillations
* treating display amplitude as experimentally meaningful displacement
* treating playback speed as physical time unless explicitly and correctly derived

不得修改 Phase 10H-4 eigenvector contract 的既有科学语义来迁就前端。

---

## 4. 开始前读取真实项目状态

首先记录：

```bash
cd "E:\1project\Material Data Intelligence"

git status --short
git branch --show-current
git rev-parse HEAD
git log --oneline -25
git remote -v
git rev-parse origin/master
```

确认：

* repository 正确
* branch 为 `master`
* working tree clean
* HEAD 包含 Phase 10H-4
* origin/master 与预期一致
* Phase 10H-4 implementation、tests、docs、evidence 存在

如果 working tree 不干净，停止并报告，不得覆盖未知修改。

不要求 HEAD 等于 prompt 中预写的某个 hash；以真实 Phase 10H-4 Result 为准。

---

## 5. 必读实现

开始实现前必须完整阅读真实代码，不得只读 docs。

### 5.1 Phase 10H-4 Eigenvector Contract

必须定位并阅读：

* mode reference schema
* eigenvector schema
* eigenvector-set schema
* complex scalar/vector models
* structure binding
* band artifact binding
* artifact content hash
* q-point identity
* branch identity
* frequency binding
* NAC direction binding
* atom ordering
* atomic masses
* normalization metadata
* mass-weighting metadata
* phase/gauge metadata
* degeneracy metadata
* displacement reconstruction helper
* display-amplitude metadata
* caps
* validators
* canonical serializer
* fixtures
* independent reference tests

必须确认当前正式 schema version，不能根据 prompt 猜文件名或版本。

### 5.2 Phase 10H-1 / 10H-3

阅读：

* phonon band adapter
* band artifact validator
* q-point and segment identity
* combined band + DOS frontend
* plot point identity
* compatibility validator
* artifact handoff mechanism
* browser evidence runner

确认 band plot 中每个可选择点是否已经能稳定映射到：

```text
band artifact hash
q-point index
branch index
mode ID
frequency
NAC direction
```

### 5.3 Static / Trajectory Viewer

阅读现有：

* Three.js renderer
* scene mapper
* instanced atom renderer
* periodic bond renderer
* periodic site identity
* supercell mapper
* camera
* clipping
* picking
* inspector
* measurement
* lifecycle
* WebGL fallback
* context-loss handling
* PNG export
* mobile controls
* accessibility
* reduced-motion support
* browser runners

必须尽量复用稳定 viewer infrastructure，不得建立第二套互不兼容的 Three.js 生命周期。

### 5.4 Runtime / Registry / Planner

阅读：

* Tool Registry
* params schema conventions
* PlanValidator
* persisted AnalysisPlan
* QueueWorkerRuntime
* artifact writer
* API job flow
* frontend artifact detection
* deterministic/mock planner routing
* service-backed integration
* no-skipped assertion

---

## 6. 修改前必须输出审计

修改代码前输出：

# Phase 10H-5 Phonon Animation Pre-Implementation Audit

## 1. Baseline

* branch
* HEAD
* origin/master
* git status
* Phase 10H-4 commit
* Phase 10H-4 CI
* current schema versions

## 2. Existing Contracts

* band contract
* eigenvector contract
* mode reference
* structure identity
* atom ordering
* complex representation
* normalization
* mass weighting
* phase convention
* NAC policy
* imaginary-mode policy
* displacement helper
* caps

## 3. Existing Viewer Infrastructure

* renderer
* instancing
* periodic identity
* supercell
* bonds
* picking
* inspector
* camera
* clipping
* lifecycle
* context loss
* mobile/accessibility
* export

## 4. Compatibility Path

说明：

```text
band artifact
eigenvector artifact
structure resource
mode ID
```

如何组成可动画的兼容输入。

## 5. Selected Implementation Strategy

明确：

* 是否新增 `phonon.animation`
* 是否新增 animation package schema
* 是否复用 viewer renderer
* 如何处理 supercell
* 如何处理 non-Gamma
* 如何处理 imaginary mode
* 如何处理 vectors/trails
* 如何连接 band plot

## 6. Planned Files

列出预计修改或新增的实现、测试、runner、evidence、docs 和 persistent 文件。

审计完成后直接继续实现，不等待人工确认。

---

## 7. 正式 Tool Identity

优先正式注册：

```text
tool_id: phonon.animation
domain: phonon
```

语义：

> 根据已验证的 phonon band、eigenvector 和 canonical structure artifacts，生成一个受限、声明式的 phonon mode animation package，并由应用内置 Three.js renderer 进行交互式显示。

描述必须明确：

* 使用已有 eigenvector 数据
* 不计算 phonon
* 不计算 force constants
* 动画是 mode visualization
* display amplitude 是可视化尺度
* imaginary mode 不代表稳定时间振荡
* renderer 由应用提供
* artifact 不包含 JavaScript
* artifact 不包含 remote assets

禁止注册多个重叠工具，例如同时新增：

* `phonon.mode_animation`
* `phonon.animate`
* `phonon.viewer`
* `phonon.eigenvector_viewer`

除非仓库已有正式命名要求。最终只能保留一个 canonical tool identity。

---

## 8. 输入合同

`phonon.animation` 必须接收明确且可验证的资源绑定。

至少包含：

* canonical structure resource 或其不可变 identity
* phonon band artifact reference
* phonon eigenvector-set artifact reference
* selected mode reference

Selected mode 必须通过以下之一表达：

```text
canonical mode_id
```

或完整复合引用：

```text
band_artifact_hash
q_point_index
branch_index
NAC_direction_if_required
```

不得只使用 frequency 作为 mode identity。

### 8.1 Compatibility Validation

执行前必须验证：

* band artifact hash 与 mode reference 一致
* eigenvector artifact 引用同一 band calculation
* structure identity 一致
* structure content hash 一致
* atom count 一致
* atom ordering一致
* species ordering一致
* lattice lineage一致
* q-point identity一致
* branch identity一致
* frequency在合同容差内一致
* NAC direction一致
* normalization metadata存在
* mass-weighting metadata存在
* complex vector shape正确
* eigenvector atom dimension正确
* 所有数值 finite
* caps 未超限

任何不兼容必须 typed failure，不得生成部分动画或静默 fallback。

---

## 9. Params Schema

使用 strict whitelist。

建议参数语义如下，但字段名和最终范围必须服从现有项目规范：

```json
{
  "mode_id": "canonical-mode-id",
  "display_scale": 1.0,
  "initial_phase_radians": 0.0,
  "playback_cycles_per_second": 0.5,
  "autoplay": false,
  "loop": true,
  "supercell_mode": "auto",
  "supercell": [1, 1, 1],
  "show_vectors": true,
  "show_trails": false,
  "show_bonds": true,
  "show_unit_cell": true,
  "show_axes": true,
  "representation": "ball_and_stick"
}
```

必须拒绝 unknown params。

必须校验：

* strings 为固定枚举
* booleans 为严格 boolean
* numbers finite
* no NaN
* no Infinity
* phase 有明确归一化策略
* display scale 有最小/最大值
* playback speed 有最小/最大值
* supercell 为 bounded integer tuple 或合同允许的 matrix
* trail length bounded
* no callback
* no URL
* no shader
* no HTML
* no arbitrary formula
* no source code

### 9.1 Autoplay

默认：

```text
autoplay = false
```

如果浏览器启用 `prefers-reduced-motion`：

* 必须保持 paused
* 不得自动播放
* 必须提供静态 phase preview
* 用户仍可显式启动，除非项目 accessibility policy 要求进一步确认

---

## 10. Animation Package Contract

新增独立、版本化、声明式合同，例如：

```text
phase10h5.phonon_animation.v1
```

实际版本命名应遵循仓库现有 conventions。

不得把动画数据塞进 trajectory contract，也不得修改 trajectory semantics。

Animation package 至少应包含：

```json
{
  "schema_version": "...",
  "tool_id": "phonon.animation",
  "source": {},
  "structure_binding": {},
  "band_binding": {},
  "eigenvector_binding": {},
  "mode": {},
  "q_point": {},
  "frequency": {},
  "eigenvector": {},
  "supercell": {},
  "display": {},
  "playback": {},
  "limits": {},
  "warnings": [],
  "security": {},
  "provenance": {}
}
```

### 10.1 不存储完整动画帧

不得为一个 mode 预生成并持久化数百个重复 structure frames。

正确策略：

* 保存 canonical structure
* 保存 selected complex eigenvector reference或受限内联数据
* 保存 q-point
* 保存 reconstruction metadata
* 保存 display parameters
* 由应用内置 renderer 按 phase 程序化重建当前位移

这样避免把 phonon mode 错误建模为 trajectory，并降低 artifact size。

---

## 11. 位移重建必须服从 Phase 10H-4

动画不得自行重新定义公式。

必须复用 Phase 10H-4 的权威 reconstruction helper 或共享数学模块。

概念上必须保持：

```text
u(l, kappa, phase)
=
display_scale
× Re[
  e(kappa, mode)
  × exp(i(q · R_l + phase))
]
```

但具体：

* eigenvector是否已mass-unweighted
* normalization factor
* displacement unit
* phase sign
* q·R单位
* 2π是否包含
* global phase canonicalization

必须完全按 Phase 10H-4 contract 执行。

不得在 frontend 和 backend 各写一套不一致公式。

### 11.1 Shared Reference

优先建立或复用共享的纯函数定义，并确保：

```text
backend reference displacement
=
frontend reconstructed displacement
```

在容差内逐原子一致。

至少验证 phase：

* 0
* π/2
* π
* 3π/2
* 2π

并验证：

```text
u(phase + 2π) == u(phase)
```

---

## 12. Global Phase 与 Gauge

必须保持：

* 全局复相位不改变 mode 的物理等价性
* artifact canonical phase 不因 UI 操作被修改
* phase slider 只是 viewer state
* 不对每个 atom 独立 canonicalize phase
* 不把 global-phase-equivalent vectors识别为不同 mode

测试必须覆盖：

```text
e
```

与：

```text
e × exp(iφ0)
```

在相应 phase shift 后产生相同动画。

---

## 13. Gamma Mode

对于 Γ 点：

```text
q = [0, 0, 0]
```

必须保证：

* 所有 unit-cell replicas 使用相同空间 phase
* displacement仅随动画 phase 变化
* supercell复制不引入伪相位
* acoustic near-zero mode保留频率/容差标签
* 不因频率接近0而除零或产生无限周期

零频或近零频模式仍可作为 phase morph 可视化，但不得声称具有可靠物理振荡周期。

---

## 14. Non-Gamma Mode

Non-Gamma 模式必须实现真实空间 phase：

```text
q · R_l
```

不得让所有 supercell replicas 同相移动。

### 14.1 Commensurate Supercell Policy

必须采用以下优先顺序：

1. 使用 Phase 10H-4 或 source artifact 中经过验证的 commensurate supercell matrix。
2. 如果合同允许推导，使用 bounded deterministic solver。
3. 如果在现有 hard caps 内无法得到 commensurate supercell，则 typed refusal。
4. 不得静默把 non-Gamma mode 降级成 Γ mode。
5. 不得用近似 q 代替原 q 而不明确记录。

必须验证条件，概念上满足：

```text
S^T q = integer vector
```

容差必须来自合同，不得前端自定。

### 14.2 Bounded Solver

若实现推导：

* 搜索范围固定
* determinant cap固定
* matrix component cap固定
* candidate count固定
* deterministic ordering
* deterministic tie-break
* overflow protection
* singular matrix拒绝
* displayed atom cap检查
* displayed bond cap检查
* vector/trail cap检查

若第一阶段只支持 diagonal supercell，必须明确记录并拒绝需要一般整数矩阵的 q-point，不得伪造支持。

---

## 15. Supercell 与周期身份

必须复用：

```text
PeriodicSiteRef {
  siteIndex,
  imageOffset
}
```

或项目当前 canonical periodic identity。

每个 displayed atom 必须可映射到：

* canonical atom index
* image offset
* displayed instance ID
* reference position
* current displacement
* current displayed position

必须保证：

* picking identity稳定
* inspector identity稳定
* phase变化不改变instance identity
* supercell变化会清理 stale selection
* mode切换会清理或重新校验 selection
* artifact切换会清理所有旧 mapping
* 不产生重复 instance ID

---

## 16. Display Amplitude

UI 必须使用：

```text
Display scale
```

或中文：

```text
显示位移比例
```

不得默认标记为：

```text
Physical amplitude
真实振幅
热振幅
零点振幅
```

除非 source contract 确实提供可验证物理振幅。

必须显示：

* 当前 display scale
* 当前最大显示位移
* 位移长度单位
* 是否仅为visualization scale

必须设置安全上限，避免：

* 原子移出合理范围
* geometry爆炸
* clipping失控
* bond line无限拉长
* GPU precision问题

可根据 lattice、nearest valid distance 或合同固定尺度计算显示上限，但算法必须：

* deterministic
* bounded
* documented
* tested

---

## 17. Playback 语义

内部动画状态优先使用：

```text
phase ∈ [0, 2π)
```

UI playback speed优先表示：

```text
visual cycles per second
```

不得把用户选择的视觉播放速度伪装成真实声子时间。

对于 stable real-frequency mode，可以显示 source frequency，例如 THz，但必须区分：

* source phonon frequency
* visual playback speed

### 17.1 Controls

必须提供：

* play
* pause
* phase slider
* speed control
* loop toggle
* reset phase
* reset animation
* step backward
* step forward，若项目交互风格适合

Pause 后 phase 必须稳定，不得继续后台漂移。

浏览器 tab hidden 时：

* 暂停或停止 requestAnimationFrame 更新
* 恢复后不得产生巨大 phase jump
* 不得创建重复 animation loop

---

## 18. Imaginary Mode Policy

Imaginary mode不得作为稳定简谐时间振荡来描述。

必须：

* 显示明显 `Imaginary / unstable mode` badge
* 显示 signed/imaginary frequency encoding
* 显示科学警告
* 默认 paused
* 允许用户通过 phase slider查看双向位移形态
* 可以提供visual morph播放，但必须明确“非真实稳定时间演化”
* 不得将 imaginary frequency 取绝对值后当作普通 stable frequency
* 不得隐藏负频/虚频
* 不得在 summary 中写“stable oscillation”

Browser evidence必须覆盖一个 imaginary mode。

---

## 19. Degenerate Modes

必须保留 selected mode 的 branch/mode identity。

不得：

* 自动平均degenerate modes
* 自动求和
* 自动旋转degenerate subspace
* 根据数值噪声重排mode
* 把相同frequency的mode视为同一个mode

如果 source basis在degenerate subspace内不唯一：

* 显示warning
* 动画所展示的是source-provided basis vector
* 不宣称这是唯一物理方向

---

## 20. NAC Direction

对于需要NAC方向区分的 Γ 附近模式：

* NAC direction必须进入兼容检查
* mode selector必须显示或可检查NAC direction
* 不同NAC方向不得错误复用同一mode
* missing direction必须 typed error或明确 unsupported
* 不得静默选择默认方向

至少增加一个NAC fixture；如现有正式 fixture没有，则测试 synthetic bounded contract fixture，但不得声称来自真实计算。

---

## 21. Atom Rendering

必须复用已有 production structure viewer 的：

* species-based instancing
* element color/radius policy
* unit-cell rendering
* axes
* clipping
* camera
* reset
* fallback
* cleanup

每帧优先只更新实例矩阵或position buffer。

不得每帧：

* 重建全部Three.js scene
* 创建新geometry
* 创建新material
* 创建新canvas
* 创建新WebGL context
* 重新解析artifact
* 重新执行bond inference
* 重新生成React component tree中的大型对象

---

## 22. Bonds

Phonon animation中的 bond topology必须是reference topology。

允许：

* 使用已有 canonical periodic bonds
* endpoints随原子当前位置移动
* show/hide bonds
* cross-boundary bond
* supercell bond replication
* selected atom/neighbor highlight

禁止：

* 每phase重新推断bond
* 根据瞬时距离创建/删除bond
* 将distance-cutoff topology说成authoritative chemical bonds
* 在动画过程中改变canonical topology

如果结构没有有效bond topology：

* 允许atoms-only animation
* 显示warning
* 不得阻止phonon animation本身

---

## 23. Vector Overlay

必须提供可选 displacement vector overlay。

每个vector：

* anchor为reference或current position，策略必须固定
* direction来自当前phase displacement
* magnitude与display displacement一致
* zero-length vector不生成geometry
* vector count受displayed atom cap约束
* arrow size bounded
* no NaN/Infinity

必须提供：

* show/hide vectors
* vector scale说明
* textual fallback

不得把complex eigenvector的real part固定画成vector而忽略当前phase。

---

## 24. Displacement Trails

Trail为可选能力。

如果实现：

* 默认关闭
* 固定最大trail samples
* 固定最大total vertices
* mode切换时清理
* supercell切换时清理
* amplitude切换时重建或清理
* artifact切换时清理
* context loss时清理
* reduced motion时默认关闭
* 不持久化完整动画轨迹

如果trail会扩大本阶段风险，可以实现最小bounded版本，但不能用静态占位按钮声称READY。

---

## 25. Mode Selector

必须提供可检索、可访问的mode selector。

每项至少显示：

* q-point label或index
* q-point fractional coordinates
* segment/point identity
* branch index
* mode ID
* frequency
* unit
* imaginary badge
* NAC direction，若存在
* degeneracy warning，若存在
* eigenvector availability

不得仅显示“Mode 1、Mode 2”而隐藏科学身份。

---

## 26. Band → Animation 联动

Phase 10H-3 Combined Band + DOS 产品必须能够安全进入动画。

推荐交互：

1. 用户点击 band point。
2. 前端读取 stable mode reference。
3. 检查 eigenvector artifact availability。
4. 检查 compatibility。
5. 显示 `Open mode animation`。
6. 打开时选中同一 q-point / branch / mode。
7. 不重新根据frequency搜索mode。

如果该band point没有eigenvector：

* 按钮disabled或显示typed unavailable状态
* 不选择最近frequency
* 不伪造动画

必须新增联动测试。

---

## 27. Inspector

复用现有structure inspector，并增加 phonon 字段：

* canonical atom index
* species
* periodic image offset
* reference fractional position
* reference Cartesian position
* current displacement vector
* current displacement magnitude
* current displayed position
* selected mode ID
* q-point
* branch
* phase
* display scale
* normalization
* mass-weighting status

不得显示用户不可理解的原始complex数组作为唯一界面；可以在developer/details区域展示real/imag components。

---

## 28. Measurement

现有distance/angle/dihedral measurement在动画中必须有明确策略。

推荐：

* measurement基于当前 displayed positions
* UI明确显示 `current animated geometry`
* phase变化时measurement实时更新或明确冻结
* minimum-image语义继续沿用现有实现
* selection identity不随phase变化
* degenerate geometry安全失败

不得把动画瞬时measurement误写为equilibrium structure measurement。

如果实时更新性能风险过高，可在paused状态允许measurement，并在playback时冻结或禁用，但必须明确UI和tests。

---

## 29. Frontend状态模型

动画viewer状态至少包括：

* selected mode
* phase
* playing
* speed
* loop
* display scale
* supercell
* vectors enabled
* trails enabled
* bonds enabled
* selected atom
* camera
* clipping
* context state
* validation state

必须区分：

```text
artifact canonical data
```

与：

```text
ephemeral viewer state
```

不得把phase、camera或playback进度写回canonical eigenvector artifact。

---

## 30. Lifecycle

必须保证：

* 一个viewer实例最多一个active canvas
* 一个viewer实例最多一个active WebGL context
* 一个active animation loop
* component unmount取消requestAnimationFrame
* mode switch不产生第二个loop
* artifact switch清理旧resources
* route change清理
* context loss停止animation
* context restore安全重建
* Blob URL全部revoke
* event listener全部remove
* ResizeObserver全部disconnect
* controls dispose
* geometries dispose
* materials dispose
* trail buffers dispose
* vector buffers dispose
* instance buffers dispose

必须增加重复切换stress test。

---

## 31. Performance Caps

必须复用或收紧现有viewer和Phase 10H-4 caps。

至少限制：

* canonical atoms
* eigenvector atom count
* supercell determinant
* per-axis repeat
* displayed atoms
* displayed bonds
* displayed vectors
* trail samples
* total trail vertices
* animation package bytes
* JSON bytes
* mode count
* q-point count
* branch count
* labels
* warnings
* frame update work
* WebGL draw calls
* geometries
* materials

现有viewer已验证的硬上限不得被无证据放宽。

若扩展supercell cap：

* 必须有专门near-cap browser evidence
* 必须有memory/draw-call metrics
* 必须有mobile拒绝或降级策略
* 必须更新security/resource policy

Over-cap必须：

* explicit refusal，或
* 合同已定义的安全降级

不得静默truncate atoms/eigenvectors，因为会破坏mode物理身份。

---

## 32. Animation Performance

必须测量：

* average frame time
* p95 frame time
* dropped frames或等价指标
* draw calls
* geometry count
* material count
* displayed atoms
* displayed bonds
* displayed vectors
* trail vertices
* memory trend，若工具可用
* animation loops
* canvas count
* context count
* mode-switch latency
* supercell-switch latency
* pause/resume behavior

至少覆盖：

1. small Γ stable mode
2. non-Gamma commensurate mode
3. imaginary mode
4. multi-species structure
5. periodic bond structure
6. near-cap displayed atom case
7. rapid mode switching
8. repeated play/pause
9. repeated mount/unmount
10. context loss/restore

Acceptance threshold应基于现有viewer budget，不得随意放宽。

---

## 33. Fallback

必须有以下fallback：

### 33.1 WebGL不可用

显示：

* phonon mode summary
* q-point
* branch
* frequency
* imaginary status
* eigenvector availability
* supercell
* textual displacement summary
* JSON artifact preview

不得显示空白区域。

### 33.2 Invalid Artifact

显示typed validation error，不初始化renderer。

### 33.3 Incompatible Inputs

显示compatibility failure，不生成animation package。

### 33.4 Over-Cap

显示明确resource-limit错误，不冻结浏览器。

### 33.5 Context Loss

暂停animation，显示恢复状态，恢复后不得重复canvas/context。

---

## 34. Artifact Contract

本阶段至少生成：

### 34.1 `phonon_animation.json`

* canonical animation package
* application/json
* validator PASS
* no executable content
* no external URLs
* content hashes
* deterministic serialization

### 34.2 Animation Manifest

建议：

```text
phonon_animation_manifest.json
```

或项目现有canonical名称。

至少声明：

* entry artifact
* schema version
* band reference
* eigenvector reference
* structure reference
* renderer provided by application
* renderer bundle not embedded
* external resources none
* executable assets none
* WebGL capability由应用提供
* fallback available
* security flags

### 34.3 `summary.md`

必须包含：

* source structure
* source phonon calculation
* band artifact
* eigenvector artifact
* selected mode
* q-point
* branch
* frequency
* imaginary status
* NAC direction
* normalization
* mass weighting
* supercell
* display scale semantics
* animation controls
* caps
* warnings
* security
* deferred scientific scope

### 34.4 `recipe.json`

记录：

* tool ID
* input references
* input hashes
* mode ID
* normalized params
* compatibility checks
* reconstruction contract version
* supercell resolution
* display settings
* deterministic package generation
* dependencies
* renderer included in artifact: false
* external assets: none

不得包含可执行代码。

---

## 35. Determinism

相同输入和相同参数必须生成等价：

* animation package
* manifest
* summary
* recipe
* warning order
* mode identity
* supercell matrix
* displayed instance order
* artifact hashes，除基础设施生成的外部ID外

Fixed-phase screenshot必须使用固定：

* mode
* q-point
* branch
* phase
* display scale
* supercell
* camera
* viewport
* device scale factor
* renderer settings

动画运行中的任意实时帧截图不能作为唯一deterministic evidence。

---

## 36. Typed Errors

至少覆盖：

* input missing
* band artifact missing
* eigenvector artifact missing
* structure missing
* invalid mode reference
* stale band hash
* stale eigenvector hash
* structure identity mismatch
* atom count mismatch
* atom ordering mismatch
* species mismatch
* q-point mismatch
* branch mismatch
* frequency mismatch
* NAC direction mismatch
* eigenvector unavailable
* invalid complex value
* non-finite value
* normalization missing
* mass-weighting missing
* reconstruction unsupported
* non-commensurate q-point
* supercell exceeds cap
* displayed atom cap exceeded
* displayed bond cap exceeded
* vector cap exceeded
* trail cap exceeded
* payload byte cap exceeded
* contract validation failed
* manifest validation failed
* artifact write failed
* renderer unavailable
* WebGL context lost

错误不得泄漏：

* private path
* stack trace
* token
* API key
* secret
* internal URL

---

## 37. Tool Registry

Registry entry必须包含：

* `phonon.animation`
* domain
* precise description
* required resource kinds
* strict params schema
* compatibility requirements
* output artifact declarations
* deterministic package flag
* renderer capability
* security characteristics
* caps
* typed errors
* no external network
* no executable artifact

Registry tests必须确认：

* tool存在
* tool ID唯一
* output contract正确
* params严格
* caps存在
* no artifact JS
* no external URL capability
* 不与trajectory viewer混淆
* 不与static structure viewer混淆
* 不与phonon bands/DOS混淆

---

## 38. Planner Routing

必须增加明确正向路由。

正向示例：

* 播放这个声子模式
* 显示这个q点的原子振动
* 为选中的phonon branch创建动画
* 动画展示这个虚频模式
* Visualize this phonon eigenmode
* Animate the selected phonon mode
* Show atomic displacements for this q-point and branch
* Open a phonon mode animation

应路由到：

```text
phonon.animation
```

前提是上下文中存在兼容eigenvector artifact。

### 38.1 Negative Routing

不得误路由：

* 计算声子谱
* 从结构计算force constants
* 运行phonopy
* 计算热导率
* 显示MD trajectory
* 打开普通structure viewer
* 生成Brillouin zone
* 绘制charge density
* 生成XRD
* 做CrystalNN
* 编辑结构
* 导出MP4

如果缺少eigenvector：

* planner必须说明缺少必要输入
* 不得生成假的动画计划
* 不得退化成trajectory viewer

---

## 39. Runtime Integration

必须证明：

* Planner生成合法plan
* PlanValidator接受合法params
* persisted AnalysisPlan保存
* QueueWorkerRuntime执行
* Registry解析`phonon.animation`
* compatibility validator运行
* adapter生成animation artifacts
* artifacts保存
* artifact listing返回
* frontend识别animation package
* renderer消费artifact
* job completed
* events/tool calls完整
* report/recipe可查看

不得只通过直接调用函数证明功能。

---

## 40. API Evidence

至少提供：

* sanitized request
* planner response
* validated plan
* persisted plan ID/hash
* job ID
* selected tool
* tool-call state
* artifact list
* artifact metadata
* contract validation result
* compatibility result
* content hashes
* job events
* final result

至少覆盖：

1. stable Γ mode
2. non-Gamma commensurate mode
3. imaginary mode

所有capture必须redacted。

---

## 41. Browser UI

Phonon Animation应进入现有结果/科学可视化工作台，不得建立孤立调试页作为唯一产品证据。

UI至少包含：

### Header / Mode Summary

* mode label
* q-point
* branch
* frequency
* imaginary badge
* NAC direction
* source calculation
* validation state

### Viewer

* atoms
* cell
* optional bonds
* optional vectors
* optional trails
* periodic supercell
* camera interaction
* clipping

### Controls

* mode selector
* play/pause
* phase slider
* speed
* display scale
* loop
* supercell
* vectors toggle
* trails toggle
* bonds toggle
* reset phase
* reset camera

### Inspector

* periodic atom identity
* reference/current positions
* displacement
* magnitude
* phase
* mode identity

### Warnings

* imaginary mode
* visual scale
* degenerate basis
* non-authoritative bonds
* cap/fallback state

---

## 42. Accessibility

必须覆盖：

* keyboard-operable controls
* labelled play/pause
* labelled sliders
* visible focus
* semantic buttons
* slider value text
* mode identity text
* frequency text
* imaginary status text
* screen-reader summary
* no color-only status
* reduced motion
* paused default
* touch target size
* mobile layout
* textual displacement fallback
* WebGL fallback readable

快捷键如实现，必须不抢占浏览器基础快捷键，并有说明。

---

## 43. Mobile

必须验证：

* small viewport
* portrait
* landscape
* touch rotate
* pinch zoom
* mode selection
* phase slider
* play/pause
* amplitude slider
* inspector
* warning display
* no horizontal page overflow
* no control overlap
* context lifecycle

Near-cap supercell可在mobile上明确拒绝或降低允许上限，但策略必须可预测并记录。

---

## 44. Browser Evidence Matrix

必须在真实浏览器验证：

* Chromium
* Firefox
* WebKit
* mobile viewport

至少保存以下类型截图：

1. stable Γ mode paused at phase 0
2. stable Γ mode at phase π/2
3. non-Gamma supercell phase pattern
4. imaginary mode warning
5. mode selector
6. vector overlay
7. periodic atom inspector
8. mobile controls
9. WebGL fallback或context-loss state
10. combined band → animation handoff
11. reduced-motion state
12. fixed-phase PNG export，若复用现有export

必须记录：

* browser/version
* viewport
* device scale factor
* selected mode
* phase
* display scale
* supercell
* console
* network
* metrics
* screenshot hash

---

## 45. Network 与安全审计

必须证明：

```text
NO_PHONON_ANIMATION_EXTERNAL_NETWORK_REQUESTS
```

并检查：

* no artifact JavaScript
* no artifact HTML
* no artifact CSS
* no artifact shader
* no external URL
* no remote texture
* no CDN
* no iframe
* no eval
* no Function constructor
* no dynamic import from artifact
* no arbitrary formula execution
* no local path traversal
* no secret
* no token
* no stack/path disclosure
* labels rendered as plain text
* filenames sanitized
* JSON payload inert
* renderer is application-owned

必须输出：

```text
NO_SECRET_PATTERN_HITS
```

npm audit若因既有registry不可用：

* 记录unavailable
* 不得写PASS或clean
* 必须重新检查 dependency/lockfile是否变化
* 新增dependency必须有明确必要性和reachability分析

优先不新增依赖。

---

## 46. Unit / Reference Tests

必须增加独立科学参考测试。

### 46.1 Displacement

覆盖：

* Γ real eigenvector
* Γ complex eigenvector
* non-Gamma complex phase
* replica phase difference
* phase periodicity
* phase sign convention
* global phase equivalence
* mass-weighted source
* non-mass-weighted source
* normalized vector
* display scaling
* zero vector
* imaginary mode
* NAC mode

### 46.2 Supercell

覆盖：

* valid diagonal commensurate
* valid general matrix，若支持
* non-commensurate
* tolerance boundary
* deterministic selection
* determinant cap
* displayed atom cap
* singular matrix
* invalid integer matrix
* q-point near rational boundary

### 46.3 Identity

覆盖：

* canonical atom index
* replica offset
* mode switch
* supercell switch
* artifact switch
* selection cleanup
* band point handoff

参考实现不得复制生产实现的同一代码路径作为“独立验证”。

可使用小型手算fixture验证预期位移。

---

## 47. Frontend Tests

至少覆盖：

* artifact mapper
* compatibility failure
* initial paused state
* play
* pause
* phase slider
* speed
* loop
* display scale
* mode selection
* q-point/branch identity
* imaginary warning
* vector toggle
* trail toggle
* bonds toggle
* supercell
* inspector
* reduced motion
* keyboard
* mobile layout
* context loss
* lifecycle cleanup
* no duplicate loop
* no duplicate canvas
* no duplicate context
* fixed-phase render state
* band-to-animation handoff
* fallback

不得仅测试按钮存在；必须验证状态和数学输出。

---

## 48. Regression Tests

必须运行并保持：

* Phase 10 Closure Regression Pack
* Phase 10F static viewer regression
* periodic identity regression
* periodic bond regression
* picking/measurement regression
* supercell regression
* camera/clipping/export regression
* Phase 10G trajectory contract
* trajectory adapter
* trajectory viewer
* trajectory performance/browser regression
* Phase 10H phonon contract
* Phase 10H-1 bands
* Phase 10H-2 DOS
* Phase 10H-3 combined
* Phase 10H-4 eigenvector contract
* service-backed integration
* no-skipped assertion

Phonon animation不得导致trajectory viewer把animation package识别为trajectory。

---

## 49. Evidence Directory

建议新增：

```text
docs/phase10h/evidence/phase10h5_phonon_animation/
```

至少包含：

* README
* implementation audit
* sanitized API captures
* selected plans
* compatibility results
* animation package samples
* manifest samples
* validator results
* deterministic replay
* scientific reference calculations
* browser matrix
* screenshots
* performance metrics
* lifecycle metrics
* context-loss evidence
* accessibility audit
* mobile audit
* console audit
* network audit
* security audit
* artifact hashes
* CI record

不得提交：

* secrets
* private paths
* large raw phonon datasets
* node_modules
* browser cache
* videos
* unrestricted binary dumps
* external URLs
* generated renderer bundles作为artifact

---

## 50. Required Fixtures

至少准备或复用以下bounded fixtures：

### Fixture A：Stable Γ Mode

* small crystal
* multiple atoms
* real or simple complex eigenvector
* known displacement
* stable positive frequency

### Fixture B：Non-Gamma Commensurate Mode

* q-point非零
* bounded supercell
* replica phase差异可手算
* complex eigenvector
* deterministic expected positions

### Fixture C：Imaginary Mode

* negative/imaginary encoding
* warning expected
* no stable-oscillation claim
* phase morph可验证

### Fixture D：Multi-Species Mode

* species颜色和质量语义
* atom ordering验证

### Fixture E：NAC Direction

* Γ directional identity
* direction mismatch negative case

### Fixture F：Over-Cap

* supercell或displayed atoms超限
* explicit refusal

Fixtures必须小、稳定、可提交、无外部依赖。

---

## 51. Documentation

新增或更新Phase 10H-5文档，至少说明：

* architecture
* tool contract
* animation package
* mode binding
* displacement mathematics
* global phase
* Gamma modes
* non-Gamma modes
* commensurate supercells
* imaginary modes
* degenerate modes
* NAC
* display amplitude
* playback semantics
* renderer integration
* periodic identity
* bonds
* vectors
* trails
* performance caps
* accessibility
* browser evidence
* security
* known limitations
* replay instructions

更新：

* `docs/index.md`
* `persistent/DESIGN_PROGRESS.md`
* `persistent/TASK_BOARD.md`
* `persistent/CHANGELOG.md`
* `persistent/OPEN_QUESTIONS.md`
* `persistent/TOOL_REGISTRY_NOTES.md`
* `persistent/ARCHITECTURE_DECISIONS.md`

Persistent必须如实记录READY和DEFERRED。

---

## 52. 明确 Deferred

Phase 10H-5完成后仍然明确deferred：

* phonon calculation
* force constants
* dynamical matrices
* mode editing
* degenerate-subspace rotation
* anharmonicity
* phonon lifetime
* thermal conductivity
* physical temperature amplitudes
* quantum zero-point amplitudes
* unrestricted/general large supercells
* incommensurate modulation
* production video export
* Brillouin zone 3D
* electronic bands
* volumetric data
* charge/spin density
* isosurfaces
* Fermi surfaces
* external APIs
* notebooks/scripts
* artifact JS
* remote assets

不要将“animation READY”写成“complete phonon simulation platform”。

---

## 53. Required Checks

至少运行：

```bash
git diff --check
uv lock --check
npm --prefix apps/web ls
npm --prefix apps/web test
npm --prefix apps/web run typecheck
npm --prefix apps/web run build
uv run python -m pytest -q
```

并单独运行：

* phonon animation schema tests
* package validator tests
* compatibility validator tests
* displacement reference tests
* global phase tests
* Gamma tests
* non-Gamma tests
* supercell tests
* imaginary mode tests
* NAC tests
* atom identity tests
* vector tests
* trail tests
* lifecycle tests
* context-loss tests
* accessibility tests
* mobile tests
* registry tests
* planner positive tests
* planner negative tests
* PlanValidator tests
* runtime integration
* API evidence
* browser evidence
* performance evidence
* network audit
* secret scan
* Phase 10 Closure Regression Pack
* Phase 10G regression
* Phase 10H through 10H-4 regression
* service-backed integration
* no-skipped assertion

必须如实记录：

* passed
* failed
* skipped
* unavailable

不得将skipped写成passed。

---

## 54. Commit / Push / CI

所有实现、tests、evidence、docs和persistent完成后：

```bash
git status --short
git diff --stat
git add <only Phase 10H-5 related files>
git commit -m "Implement phonon mode animation"
git push origin master
```

等待current-HEAD CI。

必须确认：

* backend unit success
* frontend tests success
* frontend typecheck success
* frontend build success
* phonon animation tests success
* scientific reference tests success
* browser evidence success
* performance evidence success
* Phase 10 Closure success
* Phase 10G regression success
* Phase 10H contract success
* Phase 10H-1 success
* Phase 10H-2 success
* Phase 10H-3 success
* Phase 10H-4 success
* static viewer regression success
* trajectory viewer regression success
* service-backed integration success
* no-skipped assertion success
* origin/master equals HEAD
* git status clean

不得伪造commit、CI run、test counts、browser evidence或git状态。

---

## 55. PASS 判定

PASS必须全部满足：

* 真实实现，不是docs-only
* `phonon.animation`正式注册
* animation package合同完成
* validator完成
* compatibility validator完成
* band/eigenvector/structure绑定严格
* mode identity不只依赖frequency
* complex eigenvector完整保留
* atom ordering严格
* normalization严格
* mass weighting严格
* global phase语义正确
* Gamma animation正确
* non-Gamma空间phase正确
* bounded commensurate supercell完成
* imaginary mode语义正确
* NAC方向正确
* display amplitude不被误称为physical amplitude
* playback speed不被误称为physical time
* periodic identity完整
* vector overlay正确
* trail如实现则bounded
* bond topology不动态推断
* lifecycle完整
* no duplicate canvas/context/loop
* caps完整
* API execution完成
* Browser UI完成
* Chromium/Firefox/WebKit/mobile evidence完成
* accessibility完成
* performance evidence完成
* no artifact JS
* no external URLs
* no arbitrary formula execution
* no secret hits
* Phase 10F不回退
* Phase 10G不回退
* Phase 10H至10H-4不回退
* tests通过
* CI通过
* origin/master等于HEAD
* git status clean

---

## 56. PARTIAL_PASS 仅允许

仅允许以下有限情况：

* 一般整数supercell matrix尚未实现，但bounded diagonal commensurate supercell完整、科学边界明确，其他q-point显式拒绝
* displacement trail明确标记PARTIAL_READY，但核心animation、vectors和lifecycle完整
* isotope-specific mass继续DEFERRED_BY_DESIGN
* degenerate-subspace basis rotation继续deferred
* npm audit因既有registry问题unavailable，但依赖未变化且reachability复核完成
* broad physical GPU lab不可用，但Chromium/Firefox/WebKit/mobile软件矩阵完整
* MP4/GIF视频导出明确deferred

不得因为缺少：

* real animation
* non-Gamma phase
* compatibility validator
* browser evidence
* formal tool registration
* runtime integration
* scientific reference tests
* lifecycle cleanup

而判定PARTIAL_PASS；这些缺失必须FAIL。

---

## 57. FAIL 条件

以下任一情况必须FAIL：

* 只有planning/docs
* 只有静态位移截图，没有animation
* 只有前端mock，没有真实artifact
* 未正式注册tool
* 未进入QueueWorkerRuntime
* mode只按frequency查找
* 忽略band/eigenvector hash
* structure identity不验证
* atom ordering不验证
* 丢弃complex imaginary components
* 只动画real part
* frontend自行猜mass weighting
* frontend自行归一化
* Gamma和non-Gamma使用同一空间phase
* non-Gamma被当Γ mode
* 静默近似q-point
* imaginary mode被当稳定振荡
* display scale被声称为physical amplitude
* visual playback speed被声称为physical time
* 每帧重建整个scene造成明显泄漏
* 重复canvas/context/animation loop
* 无caps
* over-cap仍渲染
* atom/eigenvector被静默截断
* 动态推断bond
* artifact包含JS/HTML/shader/URL
* 允许任意表达式
* browser evidence伪造
* skipped写成passed
* Phase 10G或Phase 10H回退
* CI失败却声明PASS
* git不clean却声明完成

---

## 58. 最终报告格式

完成后必须输出：

# Phase 10H-5 Phonon Animation Result

## 1. Conclusion

PASS / PARTIAL_PASS / FAIL

## 2. Baseline

* Phase 10H-4 commit
* initial HEAD
* branch
* initial status
* origin/master
* final HEAD
* final status

## 3. Implementation Summary

* tool
* adapter
* animation package
* validator
* compatibility validator
* frontend viewer
* runtime integration
* band handoff

## 4. Schema Family

* animation package
* manifest
* mode reference
* eigenvector reference
* structure binding
* versions

## 5. Scientific Semantics

* displacement formula
* complex representation
* normalization
* mass weighting
* global phase
* Gamma
* non-Gamma
* imaginary modes
* degeneracy
* NAC
* display amplitude
* playback semantics

## 6. Supercell

* strategy
* matrix support
* commensurability
* caps
* refusal policy
* identity mapping

## 7. Renderer

* atoms
* bonds
* vectors
* trails
* camera
* clipping
* picking
* inspector
* measurements
* lifecycle
* context loss
* fallback

## 8. Product UI

* mode selection
* q-point/branch selection
* phase
* play/pause
* speed
* amplitude
* supercell
* warnings
* accessibility
* mobile

## 9. Runtime / API

* registry
* planner
* PlanValidator
* persisted plan
* QueueWorkerRuntime
* jobs
* artifacts
* evidence cases

## 10. Browser Evidence

* Chromium
* Firefox
* WebKit
* mobile
* stable Γ
* non-Gamma
* imaginary
* NAC
* reduced motion
* context loss
* screenshots
* console
* network

## 11. Performance

* displayed atoms
* displayed bonds
* vectors
* trails
* frame metrics
* draw calls
* geometries/materials
* mode-switch latency
* lifecycle metrics
* near-cap result

## 12. Security

* artifact JS
* HTML/CSS/shader
* external URLs
* network
* formula execution
* error disclosure
* secrets
* dependency audit

## 13. Tests

* backend
* frontend
* scientific reference
* browser
* Phase 10 Closure
* Phase 10G
* Phase 10H through 10H-4
* service-backed
* no-skipped

## 14. Evidence

* directory
* API captures
* artifacts
* screenshots
* metrics
* hashes
* replay commands

## 15. Files

列出主要implementation、tests、evidence、docs和persistent文件。

## 16. Explicitly Deferred

列出本阶段仍未实现的功能。

## 17. Checks

* diff
* lock
* npm tree
* frontend tests
* typecheck
* build
* backend tests
* browser runners
* network
* secrets

## 18. Commit / CI

* commit
* HEAD
* CI run
* unit
* frontend
* build
* browser
* service-backed
* no-skipped
* origin
* git status

## 19. Readiness

* stable Γ animation
* non-Gamma animation
* imaginary visualization
* phonon animation product
* performance
* security
* full phonon visualization stack
* Brillouin zone readiness

## 20. Whether Allowed to Enter Next Phase

可以 / 不可以

只有 Phase 10H-5 完成、current-HEAD CI通过、browser/performance/security evidence闭合且git clean后，才允许进入：

```text
Phase 10I：Brillouin Zone Contract
```

现在开始执行。先读取 Phase 10H-4 的真实result、schema、validator、fixtures和current viewer实现，输出 Pre-Implementation Audit，然后直接完成 `phonon.animation`、动画package、supercell和科学位移重建、正式runtime/API/frontend/browser/performance/security闭环。不得停留在planning或静态preview。

---END---

---TASK---
 状态：待处理

# Phase 10I：Brillouin Zone Contract

进入 Phase 10I：Brillouin Zone Contract。

可以默认以下阶段均已严肃执行、完整验收并通过 current-HEAD CI：

* Phase 10F：Production Structure Viewer
* Phase 10F-17：Periodic Crystal Inspection
* Phase 10F-18：Canonical Periodic Bond Topology
* Phase 10F-19：Periodic Scene Integration
* Phase 10G：Trajectory Contract
* Phase 10G-1：Trajectory Parser / Adapter
* Phase 10G-2：Trajectory Viewer
* Phase 10G-3：Trajectory Performance / Browser Evidence
* Phase 10H：Phonon Contract
* Phase 10H-1：Phonon Bands
* Phase 10H-2：Phonon DOS
* Phase 10H-3：Combined Band + DOS
* Phase 10H-4：Phonon Eigenvector Contract
* Phase 10H-5：Phonon Animation

必须记录实际 Phase 10H-5 commit、HEAD、CI run、测试数量与工作区状态，不得根据本 prompt 编造这些信息。

本阶段是**真实 Contract Implementation 阶段**，不是只写规划文档；但本阶段仍然不是 Brillouin Zone Adapter 或 3D Renderer 阶段。

---

## 1. 本阶段总目标

建立正式、版本化、数学定义完整、确定性、可验证、安全、与现有结构和声子合同兼容的 Brillouin Zone Schema Family。

必须固定：

```text
real-space lattice
        ↓
canonical reciprocal lattice
        ↓
primitive reciprocal basis
        ↓
first Brillouin zone polyhedron
        ↓
vertices / edges / faces
        ↓
high-symmetry points
        ↓
high-symmetry path
        ↓
future adapter / renderer handoff
```

本阶段必须完成：

* reciprocal lattice convention
* `2π` convention
* reciprocal units
* row-lattice matrix mathematics
* source / primitive / conventional cell identity
* basis transformation direction
* primitive reciprocal basis
* first Brillouin zone definition
* convex polyhedron schema
* vertex identity
* edge identity
* face identity
* face orientation
* face-generating reciprocal vector
* high-symmetry point schema
* point labels and aliases
* high-symmetry path schema
* path segment identity
* discontinuity policy
* time-reversal policy
* symmetry-provider metadata
* tolerance policy
* canonical ordering
* deterministic serialization
* content hashes
* validators
* independent mathematical references
* bounded fixtures
* artifact security contract
* future Adapter handoff
* future Renderer handoff
* documentation and persistent updates
* current-HEAD CI closure

---

## 2. 本阶段明确不实现

不得实现或注册：

* `structure.brillouin_zone`
* `structure.brillouin_zone_3d`
* `structure.kpath`
* Brillouin Zone production Adapter
* Tool Registry entry
* Planner routing
* QueueWorkerRuntime execution
* API production job
* Three.js BZ renderer
* WebGL BZ component
* translucent polyhedron faces
* reciprocal-space picking
* k-point inspector UI
* BZ camera presets
* BZ screenshot product evidence
* band/BZ linked product view
* phonon/BZ linked product view
* user-defined k-path editor
* electronic band calculation
* phonon calculation
* reciprocal-space volumetric rendering
* Fermi surface
* isoenergy surface
* arbitrary mesh import
* remote structure lookup
* external API
* notebook execution
* script execution
* arbitrary Python
* arbitrary shell
* artifact JavaScript
* artifact HTML
* artifact CSS
* artifact shader
* artifact GLSL
* external URL
* CDN
* remote texture
* remote module
* renderer bundle inside artifact
* magnetic Brillouin zone，除非仓库已有独立、验证完整的磁空间群合同；默认 deferred
* irreducible Brillouin zone integration mesh
* Monkhorst–Pack mesh generation
* tetrahedron integration
* Wannier interpolation
* band unfolding
* surface Brillouin zone
* 2D slab BZ
* 1D chain BZ
* non-periodic molecule support

本阶段不能因为合同已经完成就声称 Brillouin Zone Viewer 已经可用。

---

## 3. 开始前确认真实基线

首先执行：

```bash
cd "E:\1project\Material Data Intelligence"

git status --short
git branch --show-current
git rev-parse HEAD
git log --oneline -30
git remote -v
git rev-parse origin/master
```

确认：

* repository 为 Material Data Intelligence
* branch 为 `master`
* working tree clean
* HEAD 包含 Phase 10H-5
* origin/master 状态正确
* Phase 10H-5 implementation、tests、evidence、docs 存在
* current-HEAD CI 已成功

如果 working tree 不干净，停止并报告，不得覆盖未知修改。

不要求 HEAD 等于 prompt 内预写 hash；必须以真实 Phase 10H-5 Result 为准。

---

## 4. 必读项目实现

实现前必须阅读真实代码和合同，不得只阅读阶段摘要。

### 4.1 Real-Space Structure Mathematics

重点阅读：

* canonical structure schema
* lattice representation
* row-vector convention
* fractional-to-Cartesian conversion
* Cartesian-to-fractional conversion
* determinant checks
* condition-number checks
* periodic identity
* lattice content hash
* primitive/conventional metadata，若已有
* symmetry summary Adapter
* space-group summary
* structure parser
* triclinic fixtures
* minimum-image mathematics

必须确认项目现有约定是否仍为：

```text
cartesian = fractional[0] * a
          + fractional[1] * b
          + fractional[2] * c
```

即 lattice matrix 以行表示 `a、b、c`。

不得为 reciprocal-space 单独引入相反的列向量习惯。

### 4.2 Phonon Contracts

阅读：

* phonon band schema
* q-point representation
* q-point fractional coordinates
* q-point Cartesian coordinates
* q-path segment identity
* high-symmetry labels
* frequency units
* phonon eigenvector schema
* non-Gamma `q·R` phase convention
* `2π` handling
* NAC direction
* band content hashes
* mode identity
* phonon animation reconstruction

必须保证 Phase 10I 的 reciprocal convention 与 Phase 10H 的 q-point 和空间相位完全一致。

不得建立第二套不兼容的 q-point convention。

### 4.3 Existing Dependencies

审计：

* pymatgen
* spglib
* seekpath
* numpy
* scipy
* phonopy
* pymatviz

确认：

* 当前哪些依赖已存在
* 哪些依赖是直接依赖
* 哪些只是传递依赖
* 当前版本
* 是否已有高对称路径或 BZ 几何 helper
* 是否已有 license/dependency 记录
* 是否需要新增依赖

本阶段优先不新增依赖。

Contract、validator 和 reference fixtures 不得依赖外网。

### 4.4 Artifact Infrastructure

阅读：

* canonical serializer
* hash policy
* JSON finite-number policy
* typed errors
* artifact security metadata
* fixture replay
* contract validation conventions
* docs/evidence conventions
* persistent files

---

## 5. 修改前必须输出审计

修改任何代码前，输出：

# Phase 10I Brillouin Zone Contract Pre-Implementation Audit

## 1. Baseline

* Phase 10H-5 commit
* current HEAD
* branch
* origin/master
* git status
* current CI
* dependency state

## 2. Existing Real-Space Convention

* lattice storage
* vector orientation
* Cartesian formula
* inverse formula
* units
* determinant tolerance
* condition tolerance
* canonical precision

## 3. Existing Reciprocal / Q-Point Semantics

* phonon q-point basis
* fractional convention
* Cartesian convention
* `2π` policy
* q-path labels
* NAC direction
* existing transforms

## 4. Existing Symmetry Support

* space-group parser
* primitive structure support
* conventional structure support
* spglib
* seekpath
* pymatgen high-symmetry helpers
* current dependency versions

## 5. Selected Schema Family

列出计划实现的：

* reciprocal lattice schema
* Brillouin zone polyhedron schema
* high-symmetry path schema
* manifest schema
* validators
* fixtures
* reference tests

## 6. Scientific Scope

明确：

* canonical BZ 由哪一个 cell 构造
* source/primitive/conventional 关系
* high-symmetry path convention
* time-reversal policy
* magnetic structures策略
* partial occupancy策略
* dimensionality策略

## 7. Planned Files

列出预计修改或新增的实现、测试、fixture、evidence、docs 和 persistent 文件。

审计完成后直接继续，不等待人工确认。

---

## 6. Schema Family

本阶段优先建立四个独立但可组合的合同：

```text
reciprocal_lattice.v1
brillouin_zone.v1
kpath.v1
brillouin_zone_manifest.v1
```

实际完整 schema version 名称必须服从项目现有命名规则，例如：

```text
phase10i.reciprocal_lattice.v1
phase10i.brillouin_zone.v1
phase10i.kpath.v1
phase10i.brillouin_zone_manifest.v1
```

不得把所有内容塞入一个无法独立校验的大型 JSON。

### 6.1 Schema Responsibilities

`reciprocal_lattice.v1`：

* real-space lattice binding
* reciprocal matrix
* duality convention
* units
* determinant/volume
* basis role
* transformations

`brillouin_zone.v1`：

* first BZ polyhedron
* vertices
* edges
* faces
* planes
* topology
* geometric invariants

`kpath.v1`：

* high-symmetry points
* labels
* aliases
* path variants
* segments
* discontinuities
* provider metadata
* time-reversal assumptions

`brillouin_zone_manifest.v1`：

* schema references
* structure identity
* entry artifacts
* renderer not included
* executable content absent
* external resources absent
* provenance
* hashes

---

## 7. Canonical Reciprocal Lattice Convention

必须固定唯一 canonical internal convention。

项目使用 row lattice：

```text
A =
[a_x a_y a_z
 b_x b_y b_z
 c_x c_y c_z]
```

分数坐标为 row vector：

```text
r_cart = r_frac · A
```

Canonical physics reciprocal lattice必须定义为：

```text
B = 2π · A^(-T)
```

并满足：

```text
A · B^T = 2π I
```

Reciprocal Cartesian vector：

```text
k_cart = k_frac · B
```

其中：

* `A` 单位：Å
* `B` 单位：Å⁻¹
* `k_frac`：dimensionless reciprocal fractional coordinates
* `k_cart`：Å⁻¹

不得使用模糊的“reciprocal units”。

### 7.1 `2π` Policy

合同必须明确：

```text
canonical_reciprocal_convention = physics_2pi
```

即 canonical Cartesian reciprocal basis包含 `2π`。

如果需要保存 crystallographic convention：

```text
B_crystallographic = A^(-T)
```

只能作为明确标记的 derived representation，不能与 canonical matrix 混用。

必须保存枚举字段，例如：

```text
reciprocal_convention:
  physics_2pi
```

不得允许自由字符串。

### 7.2 Phonon Compatibility

必须证明：

当 lattice translation 为：

```text
R_cart = n · A
```

q-point 为：

```text
q_cart = q_frac · B
```

则：

```text
q_cart · R_cart = 2π (q_frac · n)
```

Phase 10H-4/10H-5 的 non-Gamma displacement phase必须与此一致。

增加交叉合同测试，防止 Phase 10H 和 Phase 10I 对 `2π` 重复计算或漏算。

---

## 8. Reciprocal Lattice Schema

至少包含：

```json
{
  "schema_version": "...",
  "convention": "physics_2pi",
  "units": "angstrom^-1",
  "real_lattice_binding": {},
  "basis_role": "primitive",
  "matrix": [[0,0,0],[0,0,0],[0,0,0]],
  "dual_product": [[0,0,0],[0,0,0],[0,0,0]],
  "determinant": 0,
  "cell_volume": 0,
  "real_cell_volume": 0,
  "transformations": {},
  "tolerances": {},
  "provenance": {},
  "security": {}
}
```

实际字段应使用仓库风格，但必须覆盖这些语义。

### 8.1 Validation

必须验证：

* matrix 为 3×3
* 所有数值 finite
* determinant finite
* determinant non-zero
* basis orientation明确
* duality满足 `A·Bᵀ = 2πI`
* volume满足：

```text
V_BZ = |det(B)| = (2π)^3 / |det(A)|
```

这里 `|det(B)|` 是 reciprocal primitive-cell volume，同时也是第一 BZ 体积。

* units正确
* convention枚举正确
* content hash正确
* transformation可逆
* no NaN
* no Infinity
* no overflow

优先复用 Phase 10F 的 lattice determinant 与 condition-number安全策略。

---

## 9. Source、Primitive 与 Conventional Cell

第一 BZ 必须基于**primitive reciprocal lattice**。

不得默认使用任意 source conventional cell 直接构造第一 BZ。

合同必须区分：

```text
source_cell
primitive_cell
conventional_cell
standardized_primitive_cell
```

实际支持哪些角色由仓库能力决定，但不能混为一谈。

### 9.1 Binding

至少保存：

* source structure ID
* source structure content hash
* source lattice hash
* primitive lattice hash
* conventional lattice hash，若存在
* standardization provider
* provider version
* symmetry tolerance
* space-group number/symbol，若可用
* transformation matrices
* origin shift，若存在
* Cartesian rotation，若存在

### 9.2 Transformation Direction

每个 transformation 必须明确方向和公式。

对于 row lattice，若：

```text
A_new = M · A_old
```

必须记录：

* `M`
* `old_basis`
* `new_basis`
* coordinate transform

对应分数实空间坐标：

```text
r_new = r_old · M^(-1)
```

对应 reciprocal basis：

```text
B_new = M^(-T) · B_old
```

对应 reciprocal fractional coordinates：

```text
k_new = k_old · M^T
```

实际实现必须通过 reference tests验证。

不得只保存一个名为 `transformation_matrix` 但方向不明的矩阵。

### 9.3 Rational Matrices

primitive/conventional 转换可能包含 rational entries。

合同必须规定：

* 是否允许 rational matrix
* JSON 中使用 finite decimal还是 numerator/denominator
* tolerance
* determinant relation
* round-trip validation

不得假设所有 transformation 都是整数 unimodular matrix。

---

## 10. First Brillouin Zone Definition

合同必须固定：

> First Brillouin Zone 是 primitive reciprocal lattice 中，以 Γ 为中心的 Wigner–Seitz cell。

不得将：

* primitive reciprocal parallelepiped
* conventional reciprocal cell
* arbitrary reciprocal bounding box
* irreducible wedge

误称为第一 Brillouin区。

### 10.1 Half-Space Definition

对于非零 reciprocal lattice vector `G`，对应 bisector plane：

```text
x · G <= |G|² / 2
```

第一 BZ 为所有相关 half-space 的交集。

合同应允许每个 face记录生成该 face 的 reciprocal lattice vector：

```text
generator_hkl
generator_cartesian
plane_normal
plane_offset
```

其中 canonical plane可写为：

```text
n_hat · x <= d
```

且：

```text
n_hat = G / |G|
d = |G| / 2
```

### 10.2 Origin

必须验证：

* Γ / origin位于 BZ 内部
* origin距离每个face非负
* polyhedron围绕origin
* 不接受整体平移后的polyhedron

---

## 11. Brillouin Zone Polyhedron Schema

至少包含：

```json
{
  "schema_version": "...",
  "reciprocal_lattice_binding": {},
  "definition": "wigner_seitz",
  "center": [0,0,0],
  "vertices": [],
  "edges": [],
  "faces": [],
  "volume": 0,
  "surface_area": 0,
  "topology": {},
  "tolerances": {},
  "warnings": [],
  "provenance": {},
  "security": {}
}
```

### 11.1 Vertex

每个 vertex至少包含：

* stable vertex ID
* Cartesian coordinates
* primitive reciprocal fractional coordinates
* optional exact/symbolic coordinates，若fixture支持
* plane/face incidence
* canonical order index

不得只保存 renderer buffer offset。

### 11.2 Edge

每个 edge至少包含：

* stable edge ID
* endpoint vertex IDs
* canonical endpoint order
* incident face IDs
* length
* deterministic order

边 key必须 canonical：

```text
(min(vertex_a, vertex_b), max(vertex_a, vertex_b))
```

不得有：

* self edge
* duplicate edge
* zero-length edge

### 11.3 Face

每个 face至少包含：

* stable face ID
* ordered vertex loop
* ordered edge loop或可推导关系
* outward normal
* plane offset
* generator reciprocal vector
* area
* centroid
* canonical order
* polygon winding

Face vertices必须：

* 共面
* 无重复
* 至少3个
* 按从外部观察的 CCW 顺序
* normal朝外

不得保存无方向的无序vertex set作为正式face合同。

---

## 12. Polyhedron Topology Validation

必须验证：

* convex
* closed
* manifold
* connected
* no duplicate vertices
* no duplicate edges
* no duplicate faces
* no dangling edges
* 每条edge恰好属于两个faces
* 每个face至少三个vertices
* face loop闭合
* face area非零
* edge length非零
* vertex incidence一致
* face normal outward
* 所有vertices满足所有half-space
* origin在所有half-space内部
* volume为正
* volume与reciprocal primitive-cell volume一致
* Euler characteristic：

```text
V - E + F = 2
```

适用于本阶段支持的闭合凸三维BZ。

### 12.1 Central Symmetry

第一 BZ 必须具有中心对称性。

在容差内：

* 每个 vertex `v` 存在 `-v`
* 每个face存在相反normal/offset partner
* 每个edge存在中心反演partner

必须增加验证，但实现需使用scale-aware tolerance，避免浮点噪声导致误判。

---

## 13. Canonicalization

同一几何结果无论底层算法返回顺序如何，必须得到等价 canonical serialization。

### 13.1 Numeric Canonicalization

定义：

* canonical decimal precision
* negative zero normalization
* finite-number enforcement
* scale-aware merge tolerance
* no NaN
* no Infinity

所有 `-0.0` 必须标准化为 `0.0`。

### 13.2 Vertex Ordering

建议策略：

1. 以scale-aware tolerance合并重复vertices。
2. 生成canonical quantized key。
3. 按 Cartesian `x、y、z` 字典序排序。
4. 分配stable IDs。

具体策略可调整，但必须 deterministic且有reference tests。

### 13.3 Face Ordering

建议：

1. normal canonicalization
2. plane offset
3. generator integer vector
4. ordered vertex-loop key

Face loop本身应：

* 固定outward normal
* 旋转到最小vertex ID开头
* 不允许反向等价产生不同序列

### 13.4 Edge Ordering

按canonical endpoint tuple排序。

### 13.5 Content Hash

Hash必须基于：

* canonical structure binding
* reciprocal convention
* primitive lattice
* canonical geometry
* tolerance policy
* provider metadata
* schema version

不得包含：

* runtime random ID
* filesystem path
* creation timestamp，除非不进入content hash
* browser state
* future camera state

---

## 14. High-Symmetry Point Schema

每个点必须至少包含：

```json
{
  "point_id": "canonical-id",
  "label_key": "GAMMA",
  "display_label": "Γ",
  "aliases": [],
  "fractional_coordinates": [0,0,0],
  "cartesian_coordinates": [0,0,0],
  "basis": "standardized_primitive_reciprocal",
  "provider_identity": {},
  "metadata": {}
}
```

### 14.1 Identity

Point identity不得只依赖display label。

Stable identity必须绑定：

* kpath convention/provider
* standardized primitive lattice hash
* fractional coordinate
* canonical label key
* path variant或point namespace

### 14.2 Labels

必须采用安全、明确的label策略：

* stable ASCII key，例如 `GAMMA`
* display label，例如 `Γ`
* aliases，例如 `G`
* plain text only
* no HTML
* no Markdown execution
* no arbitrary LaTeX
* no script
* max label length
* allowlisted characters或安全Unicode normalization

如果需要下标，例如 `K_1`：

* 使用结构化字段或plain text
* 不接受任意HTML/MathJax payload

### 14.3 Duplicate Coordinates

多个label指向同一坐标时必须定义：

* canonical point是否合并
* aliases如何保存
* path语义是否保留原label
* renderer未来如何显示

不得因为坐标相同就丢失source path语义，也不得产生两个几何完全重复但identity无法解释的点。

---

## 15. High-Symmetry Path Schema

K-path合同至少包含：

```json
{
  "schema_version": "...",
  "reciprocal_lattice_binding": {},
  "provider": {},
  "path_convention": "...",
  "time_reversal_used": true,
  "points": [],
  "path_variants": [],
  "segments": [],
  "discontinuities": [],
  "tolerances": {},
  "warnings": [],
  "provenance": {},
  "security": {}
}
```

### 15.1 Segment

每个segment至少包含：

* segment ID
* variant ID
* order index
* start point ID
* end point ID
* start label
* end label
* Euclidean length in Å⁻¹
* discontinuity before/after
* optional source branch identity

不得只保存：

```text
["Γ", "X"]
```

而不绑定实际坐标和basis。

### 15.2 Path Discontinuity

必须明确表示：

```text
X | K
```

一类非连续路径。

不得通过重复点、空label或隐式数组分组让consumer猜测。

### 15.3 Multiple Path Variants

不同规范或provider可能提供不同合法path。

合同必须允许：

* 一个canonical selected variant
* optional alternative variants
* provider identity
* convention identity
* deterministic selected-variant policy

不得宣称高对称路径在所有文献中唯一。

### 15.4 Path Distance

若保存累计path distance：

* 单位必须为 Å⁻¹
* 距离从每个连续path branch重新累计还是全局累计必须明确
* discontinuity处不得计算虚假跨段距离
* 与Phase 10H phonon band path distance语义一致

---

## 16. Symmetry Provider Policy

本阶段必须固定 provider metadata合同，但不一定在生产Adapter中执行provider。

可能provider包括：

* Seek-path / HPKOT
* pymatgen HighSymmKpath
* spglib-based standardization
* explicit validated input
* internal fixture reference

必须记录：

* provider name
* provider version
* convention
* input structure hash
* symmetry tolerance
* angle tolerance
* time-reversal setting
* standardization result
* warnings

不得把不同provider输出混合后称为同一canonical source。

### 16.1 Preferred Future Adapter Policy

Phase 10I-1的默认provider应在本阶段做出明确建议。

优先选择：

* 科学定义明确
* 可记录版本
* 支持primitive standardization
* 支持高对称path
* deterministic
* 无外网
* 依赖可审计

但本阶段不得提前实现正式Adapter。

---

## 17. Time-Reversal Policy

K-path合同必须明确：

```text
time_reversal_used: true | false
```

若 provider 使用 time-reversal reduction：

* 必须记录
* 不得默认为所有结构成立
* 磁性或破坏time-reversal的结构必须显式处理

本阶段建议支持：

* non-magnetic crystallographic structures
* time reversal explicitly declared

以下默认deferred或unsupported：

* magnetic space groups
* non-collinear magnetism
* spin texture
* external magnetic field
* time-reversal-broken k-path
* magnetic BZ

不得将普通空间群路径自动应用于上述情况并声称科学正确。

---

## 18. Structure Scope

本阶段合同默认支持：

* three-dimensional periodic crystal
* finite 3×3 lattice
* valid primitive cell
* ordered or provider-supported structure
* canonical structure identity

必须明确拒绝或defer：

* molecule
* 0D non-periodic
* 1D periodic
* 2D slab/surface BZ
* singular lattice
* nearly singular lattice beyond condition cap
* invalid species
* unresolved disorder
* unsupported partial occupancy
* magnetic symmetry requiring separate policy

如果现有parser支持partial occupancy，合同必须说明：

* lattice geometry仍可定义
* 但高对称path provider是否接受
* 不能静默近似成ordered structure

---

## 19. Tolerance Policy

必须建立独立、版本化的 Brillouin Zone tolerance policy。

至少包括：

* real lattice determinant tolerance
* real lattice condition limit
* reciprocal duality tolerance
* transformation round-trip tolerance
* symmetry `symprec`，单位 Å
* angle tolerance，单位 degree或provider default
* vertex merge tolerance，单位 Å⁻¹
* plane tolerance
* coplanarity tolerance
* edge-length tolerance
* volume relative tolerance
* central-symmetry tolerance
* label coordinate tolerance
* path endpoint tolerance
* rationalization tolerance

不得只使用一个全局 `1e-5` 解决所有问题。

Tolerance必须：

* finite
* positive
* bounded
* versioned
* recorded in artifact
* deterministic
* scale-aware where required

不得根据运行结果动态放宽到“直到测试通过”。

---

## 20. Caps

必须固定 hard caps，至少包括：

* max vertices
* max edges
* max faces
* max vertices per face
* max high-symmetry points
* max aliases per point
* max path variants
* max path segments
* max discontinuities
* max label length
* max warnings
* max provider metadata bytes
* max JSON bytes
* max transformation count
* max reciprocal generator search radius，供未来Adapter参考
* max candidate planes，供未来Adapter参考

建议初始上限保持保守，例如：

* vertices ≤ 256
* edges ≤ 512
* faces ≤ 256
* vertices per face ≤ 64
* high-symmetry points ≤ 128
* path segments ≤ 256

但最终值必须结合仓库现有资源策略确定并记录，不得无理由放大。

Over-cap必须：

* validator拒绝
* typed error
* 不静默truncate geometry
* 不静默丢face或point

截断BZ会破坏拓扑，因此默认禁止truncation。

---

## 21. Security Contract

所有合同必须是 inert JSON。

必须声明并验证：

* contains_javascript = false
* external_urls = []
* external_urls_allowed = false
* renderer_included = false
* executable_assets = []
* remote_assets = []
* shader_sources = []
* HTML absent
* CSS absent
* callback absent
* arbitrary expression absent
* arbitrary file path absent

Label、provider name、structure name全部按plain text处理。

不得允许artifact控制：

* Three.js module
* shader
* material class
* texture URL
* camera script
* event handler
* import URL
* worker URL
* iframe
* HTML tooltip

---

## 22. Typed Errors

至少定义或复用以下typed error：

* structure missing
* structure non-periodic
* unsupported dimensionality
* invalid lattice shape
* non-finite lattice
* singular lattice
* ill-conditioned lattice
* primitive cell unavailable
* standardization failed
* transformation invalid
* reciprocal duality failed
* reciprocal convention mismatch
* volume invariant failed
* invalid polyhedron
* non-convex polyhedron
* open polyhedron
* non-manifold polyhedron
* duplicate vertex
* duplicate edge
* duplicate face
* invalid face winding
* inward face normal
* origin outside BZ
* central symmetry failed
* BZ volume mismatch
* high-symmetry point invalid
* duplicate point identity
* invalid label
* invalid path segment
* missing path endpoint
* invalid discontinuity
* provider metadata invalid
* time-reversal policy unsupported
* magnetic structure unsupported
* cap exceeded
* payload too large
* content hash mismatch
* schema validation failed
* fixture validation failed

错误不得泄漏：

* local path
* private URL
* stack trace
* token
* secret
* environment credential

---

## 23. Independent Mathematical Reference

不得仅用production helper验证production helper。

必须建立独立reference calculations。

至少验证：

### 23.1 Reciprocal Duality

对多个lattice手算或使用独立小型公式验证：

```text
A · Bᵀ = 2πI
```

### 23.2 Volume

验证：

```text
V_BZ = (2π)^3 / V_real
```

### 23.3 Basis Transform

验证：

```text
A_new = M A_old
B_new = M^(-T) B_old
```

以及 reciprocal coordinate round-trip。

### 23.4 Plane

对face generator `G`验证：

```text
x · G = |G|² / 2
```

适用于face vertices。

### 23.5 Convexity

验证所有vertices满足全部face half-space。

### 23.6 Topology

验证：

```text
V - E + F = 2
```

### 23.7 Central Symmetry

验证 `v ↔ -v`。

Reference实现不能直接调用production canonicalization或geometry validator完成相同判断。

---

## 24. Required Fixtures

至少新增以下bounded fixtures。

### Fixture A：Simple Cubic

设：

```text
A = a I
```

预期：

* reciprocal lattice为 `(2π/a)I`
* first BZ为cube
* 8 vertices
* 12 edges
* 6 faces
* boundaries为 `±π/a`
* volume为 `(2π/a)^3`
* Γ point
* basic high-symmetry path fixture

这是最重要的解析reference。

### Fixture B：Body-Centered Cubic

验证：

* reciprocal lattice type
* BZ topology
* expected face/edge/vertex counts
* volume
* high-symmetry labels/path provider metadata

不能只验证snapshot文本。

### Fixture C：Face-Centered Cubic

验证：

* reciprocal lattice type
* BZ topology
* expected face/edge/vertex counts
* volume
* Γ、X、L、W、K 等point identity，具体以选定provider为准

不得混淆 BCC 与 FCC 的 reciprocal relationship。

### Fixture D：Hexagonal

验证：

* non-orthogonal lattice
* hexagonal-prism BZ topology
* basal and axial faces
* Γ、M、K、A、L、H 等label，具体以provider为准
* `c/a`变化不破坏identity策略

### Fixture E：Triclinic

验证：

* general lattice
* reciprocal duality
* convex closed polyhedron
* volume
* central symmetry
* deterministic serialization
* no hardcoded high-symmetry assumptions

### Fixture F：Primitive / Conventional Pair

同一晶体使用：

* conventional source cell
* primitive source cell

验证最终 standardized primitive reciprocal lattice和BZ等价，且transformation metadata正确。

### Fixture G：Negative / Invalid Cases

至少包括：

* singular lattice
* ill-conditioned lattice
* non-finite lattice
* malformed transformation
* duplicate vertex
* open face topology
* inward face
* invalid path endpoint
* label injection
* cap exceeded
* convention mismatch
* volume mismatch

Fixtures必须：

* 小型
* 无外部网络
* 可提交
* deterministic
* 无secret
* 无大型二进制

---

## 25. BCC / FCC Reference 审计要求

BCC与FCC极易被错误互换。

必须在docs和tests中明确：

* FCC real lattice的reciprocal lattice为BCC
* BCC real lattice的reciprocal lattice为FCC
* First BZ是reciprocal lattice的Wigner–Seitz cell
* 不能根据real-space cell外观直接猜BZ polyhedron

Reference topology counts必须经过独立来源或解析几何验证后写入fixture。

不得凭记忆写错误 expected values。

---

## 26. High-Symmetry Path 不是几何本身

必须严格区分：

```text
Brillouin Zone geometry
```

与：

```text
recommended high-symmetry path
```

BZ geometry由reciprocal lattice唯一确定。

High-symmetry path依赖：

* standardization
* symmetry convention
* provider
* time-reversal assumption
* path convention

合同必须允许：

* 有BZ但没有k-path
* 有validated explicit k-path
* provider生成k-path
* k-path unavailable warning

不得因path provider失败而伪造BZ失败；也不得因BZ存在而声称k-path必然唯一。

---

## 27. Compatibility with Existing Phonon Bands

必须增加compatibility contract，验证未来 phonon band artifact与Phase 10I kpath：

* structure hash一致
* primitive lattice hash一致
* reciprocal convention一致
* q-point basis一致
* q-point coordinates一致
* path provider/convention一致或明确不同
* segment identity一致
* label aliases可解析
* units一致
* `2π` policy一致
* time-reversal policy兼容

不得用frequency或display label推断q-point对应关系。

Phase 10I只实现compatibility helper/validator，不实现联动UI。

---

## 28. Future Electronic Band Compatibility

合同必须为未来 electronic band预留通用性：

* 使用 `k-point` / `reciprocal_point` 中性基础语义
* phonon可将其解释为q-point
* electronic band可解释为k-point
* 不把BZ合同硬编码成phonon-only

但不得在本阶段实现 electronic band Adapter。

---

## 29. Manifest Contract

`brillouin_zone_manifest.v1` 至少声明：

* package identity
* structure binding
* reciprocal lattice artifact
* BZ artifact
* kpath artifact，optional
* schema versions
* entry artifact
* content hashes
* provider
* convention
* units
* renderer included: false
* WebGL artifact included: false
* executable assets: none
* external resources: none
* preview mode: JSON-only
* security flags
* provenance

Manifest只能引用package内逻辑artifact名称或正式artifact ID。

不得包含：

* local absolute path
* URL
* CDN
* script
* shader
* wasm
* HTML
* renderer bundle

---

## 30. Contract Fixtures 与 Replay

必须提供 deterministic replay command。

Replay至少执行：

1. load fixture
2. validate structure/lattice binding
3. validate reciprocal lattice
4. validate BZ geometry
5. validate topology
6. validate high-symmetry points/path
7. verify hashes
8. reserialize
9. compare canonical output
10. run independent invariants

两次replay必须生成等价内容。

不得依赖：

* current time
* random seed
* filesystem-specific absolute path
* dictionary insertion accident
* provider network
* browser
* GPU

---

## 31. JSON-Only Preview Readiness

本阶段不得实现3D BZ renderer，但合同fixture应能被现有安全JSON preview查看。

如需最小additive preview support，只允许显示：

* schema version
* reciprocal convention
* reciprocal units
* primitive lattice matrix
* vertex/edge/face counts
* BZ volume
* high-symmetry point count
* path segment count
* provider
* validation state
* security state
* renderer not included

不得：

* 初始化Three.js
* 创建WebGL canvas
* 添加BZ renderer component
* 声称“3D Brillouin Zone available”

如果现有通用JSON preview已足够，则不要修改frontend。

---

## 32. 本阶段不注册 Tool

Phase 10I是Contract阶段。

不得在Tool Registry正式注册：

```text
structure.brillouin_zone
```

不得添加Planner正向路由。

可以在Tool Registry notes中规划 Phase 10I-1 candidate：

```text
tool_id: structure.brillouin_zone
```

但状态必须是：

```text
PLANNED / NOT_REGISTERED / NOT_EXECUTABLE
```

不能显示READY。

---

## 33. Evidence

建议新增：

```text
docs/phase10i/evidence/phase10i_brillouin_zone_contract/
```

至少包含：

* README
* pre-implementation audit
* schema snapshots
* reciprocal lattice fixtures
* BZ fixtures
* kpath fixtures
* manifest fixtures
* validation outputs
* independent reference outputs
* canonical replay outputs
* hash records
* negative-case outputs
* dependency audit
* security audit
* secret scan
* current-HEAD CI record

本阶段不要求：

* 3D screenshots
* browser renderer evidence
* GPU metrics
* API job captures
* production Planner evidence

不得伪造这些证据。

---

## 34. Documentation

至少新增或更新：

* Phase 10I overview
* reciprocal lattice convention
* `2π` decision
* row-vector mathematics
* primitive/conventional transformation
* first BZ definition
* polyhedron topology contract
* canonicalization
* high-symmetry point contract
* k-path contract
* provider policy
* time-reversal policy
* tolerance policy
* caps
* security
* compatibility with phonon
* fixture/reference strategy
* known limitations
* Phase 10I-1 handoff

更新：

* `docs/index.md`
* `persistent/DESIGN_PROGRESS.md`
* `persistent/TASK_BOARD.md`
* `persistent/CHANGELOG.md`
* `persistent/OPEN_QUESTIONS.md`
* `persistent/TOOL_REGISTRY_NOTES.md`
* `persistent/ARCHITECTURE_DECISIONS.md`

ADR必须记录：

1. canonical reciprocal lattice使用 `2π A⁻ᵀ`
2. BZ基于standardized primitive reciprocal lattice
3. geometry与high-symmetry path分离
4. path provider与time-reversal显式记录
5. artifacts为inert JSON
6. renderer留给Phase 10I-2

---

## 35. 明确 Deferred

Phase 10I完成后仍然deferred：

* production BZ Adapter
* Tool Registry registration
* Planner routing
* API job execution
* Three.js BZ renderer
* reciprocal-space picking
* high-symmetry point inspector
* band/BZ linked view
* phonon/BZ linked view
* custom path editor
* magnetic BZ
* surface BZ
* 2D/1D periodic BZ
* irreducible BZ wedge
* k-point meshes
* tetrahedron integration
* electronic bands
* Fermi surfaces
* volumetric reciprocal data
* band unfolding
* external API
* notebooks/scripts
* artifact JS
* remote assets

---

## 36. Required Tests

必须增加：

### 36.1 Reciprocal Mathematics

* cubic
* orthorhombic
* monoclinic
* triclinic
* determinant
* condition number
* duality
* volume
* `2π`
* coordinate conversion
* transformation round-trip

### 36.2 Polyhedron

* vertices
* edges
* faces
* winding
* normals
* planes
* convexity
* manifold
* Euler characteristic
* volume
* central symmetry
* canonical ordering

### 36.3 K-Path

* point identity
* labels
* aliases
* duplicate coordinates
* segments
* discontinuities
* multiple variants
* time reversal
* provider metadata
* path distance

### 36.4 Security

* HTML label
* script label
* URL label
* oversized label
* arbitrary metadata
* non-finite number
* oversized payload
* executable field rejection

### 36.5 Cross-Phase

* Phase 10H q-point compatibility
* non-Gamma phase `2π` consistency
* primitive lattice hash compatibility
* structure hash mismatch
* convention mismatch
* path mismatch

### 36.6 Regression

* structure viewer
* periodic lattice math
* trajectory
* phonon bands
* phonon eigenvectors
* phonon animation
* static structure analysis
* service-backed integration
* no-skipped assertion

---

## 37. Required Checks

至少运行：

```bash
git diff --check
uv lock --check
npm --prefix apps/web ls
npm --prefix apps/web test
npm --prefix apps/web run typecheck
npm --prefix apps/web run build
uv run python -m pytest -q
```

并单独运行：

* reciprocal lattice contract tests
* BZ geometry contract tests
* topology tests
* canonicalization tests
* transformation tests
* kpath tests
* compatibility tests
* independent reference tests
* fixture replay
* negative fixtures
* security tests
* Phase 10 closure regression
* Phase 10G regression
* Phase 10H through 10H-5 regression
* service-backed integration
* no-skipped assertion
* secret scan

必须如实记录：

* passed
* failed
* skipped
* unavailable

不得把 skipped 写成 passed。

---

## 38. Dependency Audit

如果没有新增依赖：

* 明确记录dependency/lockfile unchanged
* 检查现有spglib/seekpath/pymatgen能力

如果必须新增依赖：

* 说明为什么合同无法在现有依赖下完成
* 固定版本策略
* license
* transitive dependency
* package size
* security findings
* CI compatibility
* Windows/Linux compatibility
* deterministic behavior
* offline behavior

未经必要性证明不得新增。

npm audit或Python audit若因registry不可用：

* 记录unavailable
* 不得写clean
* 不得写PASS
* 继续做dependency reachability和lockfile diff审计

---

## 39. Commit / Push / CI

全部完成后：

```bash
git status --short
git diff --stat
git add <only Phase 10I related files>
git commit -m "Define Brillouin zone contracts"
git push origin master
```

等待current-HEAD CI。

必须确认：

* unit success
* frontend tests success
* typecheck success
* build success
* reciprocal contract tests success
* BZ topology tests success
* kpath tests success
* independent references success
* Phase 10 closure success
* Phase 10G success
* Phase 10H through 10H-5 success
* service-backed integration success
* no-skipped assertion success
* origin/master equals HEAD
* git status clean

不得编造commit、CI run或测试数量。

---

## 40. PASS 判定

PASS必须满足：

* 真实schema和validator实现，不是docs-only
* reciprocal convention固定
* `2π` convention固定
* row-lattice数学明确
* units明确
* reciprocal duality验证
* volume invariant验证
* primitive/conventional关系明确
* transformation方向明确
* BZ定义为primitive reciprocal Wigner–Seitz cell
* vertex/edge/face schema完整
* face winding和outward normal明确
* convex/closed/manifold验证
* Euler characteristic验证
* central symmetry验证
* high-symmetry point identity完整
* label安全
* kpath segment完整
* discontinuity明确
* provider metadata明确
* time-reversal policy明确
* tolerance policy版本化
* caps完整
* canonical ordering稳定
* deterministic serialization完成
* independent references完成
* cubic/BCC/FCC/hexagonal/triclinic fixtures完成
* primitive/conventional equivalence fixture完成
* Phase 10H q-point兼容验证完成
* no artifact JS
* no external URL
* no renderer
* no Tool Registry registration
* no Planner route
* Phase 10H-5不回退
* tests通过
* CI通过
* origin/master等于HEAD
* git status clean

---

## 41. PARTIAL_PASS 仅允许

仅允许以下有限情况：

* high-symmetry path provider尚未确定为唯一默认，但schema、provider metadata和至少一个validated fixture provider完整
* magnetic/time-reversal-broken结构明确DEFERRED_BY_DESIGN
* 2D/1D BZ明确DEFERRED_BY_DESIGN
* symbolic exact coordinates未实现，但finite canonical numeric coordinates和independent validation完整
* general rational transformation使用finite decimal而非exact rational，但round-trip和容差完整
* JSON-only preview未增加专用UI，因为现有通用preview足够
* npm/package audit因既有registry问题unavailable，但依赖未变化且审计完整

以下缺失不得判定PARTIAL_PASS：

* `2π` convention
* primitive basis policy
* reciprocal duality
* BZ volume invariant
* polyhedron topology
* canonicalization
* kpath identity
* independent fixtures
* validators
* Phase 10H compatibility

这些缺失必须FAIL。

---

## 42. FAIL 条件

以下任一情况必须FAIL：

* 只有规划文档
* 没有正式schema
* 没有validator
* reciprocal convention含糊
* `2π`未固定
* 与Phase 10H q-point convention冲突
* row/column convention混用
* source conventional cell被直接当primitive BZ
* transformation方向不明确
* BZ实际是parallelepiped却声称Wigner–Seitz
* polyhedron不闭合
* face winding不明确
* inward normal未检测
* volume不验证
* origin不验证
* duplicate geometry未检测
* high-symmetry点只靠label识别
* path discontinuity隐式
* provider未记录
* time-reversal被无条件假定
* BCC/FCC reference混淆
* NaN/Infinity被接受
* geometry被静默truncate
* artifact包含JS/HTML/URL/shader
* 提前实现renderer导致范围膨胀
* 提前注册production tool
* 伪造browser/API evidence
* skipped写成passed
* Phase 10H-5回退
* CI失败却声明PASS
* git不clean却声明完成

---

## 43. 最终报告格式

完成后必须输出：

# Phase 10I Brillouin Zone Contract Result

## 1. Conclusion

PASS / PARTIAL_PASS / FAIL

## 2. Baseline

* Phase 10H-5 commit
* initial HEAD
* branch
* origin/master
* initial status
* final HEAD
* final status

## 3. Existing Convention Audit

* real lattice
* row/column convention
* Cartesian formula
* determinant policy
* condition policy
* phonon q-point convention
* existing symmetry dependencies

## 4. Schema Family

* reciprocal lattice schema
* BZ schema
* kpath schema
* manifest schema
* versions

## 5. Reciprocal Mathematics

* canonical convention
* `2π`
* units
* duality
* volume
* coordinate conversion
* numeric precision

## 6. Cell Standardization

* source cell
* primitive cell
* conventional cell
* provider
* transforms
* origin shift
* rotation
* hashes

## 7. Brillouin Zone Geometry

* definition
* vertices
* edges
* faces
* plane generators
* winding
* normals
* convexity
* manifold
* Euler characteristic
* central symmetry
* volume

## 8. High-Symmetry Points

* point identity
* labels
* aliases
* coordinates
* basis
* duplicates
* provider

## 9. K-Path

* variants
* segments
* discontinuities
* path distance
* convention
* time reversal
* limitations

## 10. Compatibility

* structure binding
* phonon band compatibility
* q-point compatibility
* `2π` compatibility
* future electronic band readiness

## 11. Tolerances / Caps

* tolerance policy
* geometry caps
* path caps
* payload cap
* refusal policy

## 12. Fixtures / References

* simple cubic
* BCC
* FCC
* hexagonal
* triclinic
* primitive/conventional
* negative fixtures
* independent calculations

## 13. Security

* artifact JS
* HTML/CSS/shader
* external URLs
* executable fields
* label safety
* errors
* secrets
* dependency audit

## 14. Tests

* reciprocal math
* transformations
* topology
* canonicalization
* kpath
* compatibility
* fixtures
* regression
* service-backed
* no-skipped

## 15. Evidence

* directory
* schema snapshots
* validation outputs
* reference outputs
* replay
* hashes
* audit records

## 16. Files

列出主要implementation、tests、fixtures、evidence、docs和persistent文件。

## 17. Explicitly Not Implemented

* production Adapter
* Tool Registry
* Planner
* API job
* Three.js renderer
* browser GPU evidence
* linked band/BZ UI
* magnetic/surface BZ
* meshes and electronic features

## 18. Checks

* diff
* lock
* dependency tree
* frontend tests
* typecheck
* build
* backend tests
* fixture replay
* secrets

## 19. Commit / CI

* commit
* HEAD
* CI run
* unit
* frontend
* build
* contract tests
* service-backed
* no-skipped
* origin
* git status

## 20. Readiness

* reciprocal lattice contract
* primitive-cell binding
* first BZ geometry contract
* high-symmetry point contract
* kpath contract
* phonon compatibility
* security
* Adapter readiness
* Renderer readiness

预期：

```text
reciprocal lattice contract: READY
first BZ geometry contract: READY
high-symmetry point contract: READY
kpath contract: READY
phonon compatibility: READY
production Adapter: NOT_IMPLEMENTED
3D Renderer: NOT_IMPLEMENTED
full Brillouin Zone product: NOT_READY
```

## 21. Whether Allowed to Enter Next Phase

可以 / 不可以

只有 Phase 10I Contract 完成、current-HEAD CI通过、数学reference和fixtures闭合且git clean后，才允许进入：

```text
Phase 10I-1：Brillouin Zone Adapter
```

现在开始执行。

先读取 Phase 10H-5 的真实结果、Phase 10H q-point合同、Phase 10F lattice数学以及当前 symmetry dependencies，输出 Pre-Implementation Audit；然后实现 reciprocal lattice、first BZ、high-symmetry point、kpath和manifest合同及validator、fixtures、independent references、security和CI闭环。

本阶段不得进入 production Adapter 或 3D Brillouin Zone Renderer。


---END---


---TASK---
 状态：待处理
# Phase 10I-1：Brillouin Zone Adapter

进入 Phase 10I-1：Brillouin Zone Adapter。

可以默认 Phase 10I：Brillouin Zone Contract 已严肃执行、完整验收并通过 current-HEAD CI。

必须以真实 Phase 10I Result 为基线，记录实际：

* Phase 10I commit
* Phase 10I HEAD
* schema versions
* tolerance-policy version
* dependency decision
* CI run
* test counts
* origin/master
* working-tree status

不得根据本 prompt 编造这些内容。

本阶段必须产生真实 Adapter、Registry、Planner、Runtime 和 Artifact 实现，不是 planning、contract-only、fixture-only 或 evidence-only 阶段。

本阶段仍然**不实现三维 Brillouin Zone Renderer**。Renderer、GPU/browser matrix、reciprocal-space picking 与正式产品证据留给 Phase 10I-2。

---

## 1. 本阶段总目标

实现一个正式、确定性、资源受限、科学语义严格、可通过现有执行链运行的 Brillouin Zone Adapter：

```text
canonical periodic structure
        ↓
structure / lattice validation
        ↓
primitive-cell standardization
        ↓
canonical reciprocal lattice
        ↓
first Brillouin zone geometry
        ↓
high-symmetry points / k-path
        ↓
Phase 10I validators
        ↓
inert JSON artifacts
        ↓
Tool Registry
        ↓
Planner / AnalysisPlan
        ↓
QueueWorkerRuntime
        ↓
Artifact / Summary / Recipe
        ↓
existing JSON-only preview
```

优先正式注册一个 canonical tool：

```text
tool_id: structure.brillouin_zone
domain: structure
```

该工具必须生成：

* reciprocal lattice artifact
* first Brillouin zone artifact
* high-symmetry path artifact
* manifest
* summary
* recipe

必须支持至少：

* cubic
* tetragonal
* orthorhombic
* hexagonal
* monoclinic
* triclinic

必须包含经过独立验证的：

* simple cubic
* BCC
* FCC
* hexagonal
* triclinic
* primitive/conventional equivalent pair

---

## 2. 本阶段必须实现

必须完成：

* `structure.brillouin_zone` Adapter
* strict params schema
* canonical structure input binding
* three-dimensional periodicity validation
* source-cell identity
* primitive-cell standardization
* primitive/conventional transformation metadata
* canonical reciprocal lattice calculation
* `2π` convention enforcement
* first BZ geometry generation
* vertex normalization
* edge reconstruction
* face normalization
* outward face winding
* generator-plane binding
* high-symmetry point generation
* high-symmetry path generation
* provider/version metadata
* time-reversal metadata
* deterministic canonicalization
* content hashing
* Phase 10I schema validation
* topology validation
* independent invariant checks
* artifact generation
* manifest generation
* summary
* recipe
* typed errors
* resource caps
* Tool Registry registration
* Planner data-generation routing
* PlanValidator integration
* QueueWorkerRuntime integration
* direct execution tests
* service-backed execution smoke
* JSON-only preview compatibility
* deterministic replay
* security checks
* docs and persistent updates
* current-HEAD CI closure

---

## 3. 本阶段明确禁止

不得实现或宣称：

* Three.js BZ Renderer
* WebGL BZ Renderer
* canvas reciprocal-space viewer
* `structure.brillouin_zone_3d` 交互产品
* translucent faces UI
* reciprocal-space picking
* high-symmetry point inspector UI
* BZ camera controls
* k-path clicking
* band/BZ linked UI
* phonon/BZ linked UI
* BZ PNG product export
* browser GPU performance evidence
* Chromium/Firefox/WebKit完整Renderer matrix
* mobile BZ renderer
* surface Brillouin zone
* slab/2D BZ
* 1D BZ
* magnetic Brillouin zone
* irreducible BZ wedge
* Monkhorst–Pack mesh
* integration weights
* tetrahedron method
* Fermi surface
* electronic band calculation
* phonon calculation
* custom k-path editor
* arbitrary reciprocal mesh
* external API
* remote structure lookup
* notebook execution
* uploaded script execution
* arbitrary Python
* arbitrary shell
* artifact JavaScript
* artifact HTML
* artifact CSS
* artifact shader
* artifact GLSL
* remote texture
* CDN
* external URL
* renderer bundle inside artifact
* unsupported官方示例PASS声明

如果最终主要变更只是文档、fixture 或 readiness matrix，本阶段必须判定 FAIL。

---

## 4. Baseline Verification

开始前执行：

```bash
cd "E:\1project\Material Data Intelligence"

git status --short
git branch --show-current
git rev-parse HEAD
git log --oneline -30
git remote -v
git rev-parse origin/master
```

必须确认：

* repository正确
* branch为`master`
* working tree clean
* HEAD包含Phase 10I
* origin/master符合预期
* Phase 10I schema、validator、fixtures和docs存在
* Phase 10I current-HEAD CI成功

如果working tree不干净，停止并报告，不得覆盖未知变更。

---

## 5. 必读实现

不得只阅读Phase结果摘要。

### 5.1 Phase 10I Contract

必须定位并阅读实际存在的：

* reciprocal lattice schema
* Brillouin zone schema
* k-path schema
* manifest schema
* canonical serializer
* tolerance policy
* caps
* typed errors
* reciprocal validators
* topology validators
* k-path validators
* compatibility validators
* fixture replay
* independent references
* ADRs

必须使用仓库实际schema version，不得重新创建语义重叠的另一套合同。

### 5.2 Existing Structure Pipeline

阅读：

* structure resource model
* CIF/POSCAR parser
* normalized structure JSON
* lightweight structure Adapters
* lattice validation
* row-lattice mathematics
* periodic identity
* structure content hash
* space-group summary
* partial-occupancy policy
* disorder policy
* typed parser errors

### 5.3 Existing Runtime

阅读：

* Adapter protocol/base class
* Tool Registry
* params schema
* PlanValidator
* Mock/Deterministic Planner
* persisted AnalysisPlan
* QueueWorkerRuntime
* artifact writer
* summary/recipe conventions
* API job routes
* service-backed integration
* artifact listing/download
* frontend JSON preview detection

### 5.4 Candidate Providers

审计当前真实依赖和版本：

* seekpath
* spglib
* pymatgen
* scipy
* numpy
* pymatviz

确认 Phase 10I 已批准的默认：

* primitive standardization provider
* high-symmetry path provider
* BZ geometry provider
* fallback policy
* dependency boundary

不得自行推翻Phase 10I的provider decision。

---

## 6. 修改前输出审计

修改代码前输出：

# Phase 10I-1 Brillouin Zone Adapter Pre-Implementation Audit

## 1. Baseline

* Phase 10I commit
* current HEAD
* branch
* origin/master
* git status
* current CI
* schema versions

## 2. Contract Inventory

* reciprocal lattice contract
* BZ contract
* k-path contract
* manifest contract
* tolerance policy
* caps
* validators
* fixtures

## 3. Input Pipeline

* supported resource kinds
* structure parser
* normalized model
* lattice convention
* structure identity
* partial occupancy
* magnetic metadata
* unsupported inputs

## 4. Provider Audit

* standardization provider
* BZ geometry provider
* k-path provider
* versions
* dependency status
* provider output conventions
* conversion required
* risks

## 5. Existing Tool Overlap

搜索并列出：

* reciprocal-related tools
* kpath-related tools
* historical prototypes
* pymatviz mapping
* registry conflicts
* artifact-schema conflicts

## 6. Selected Implementation Strategy

只能明确选择一种主策略，例如：

* one combined canonical Adapter
* internal helpers + one public Adapter
* reuse historical unregistered prototype
* upgrade an existing experimental Adapter

## 7. Planned Files

列出实现、测试、fixtures、evidence、docs、persistent预计变更。

审计完成后直接实施，不等待人工确认。

---

## 7. Public Tool Identity

优先正式注册：

```text
structure.brillouin_zone
```

工具语义：

> 根据一个经过验证的三维周期晶体结构，计算并导出标准化primitive reciprocal lattice、第一Brillouin zone多面体以及可选高对称k-path的声明式JSON数据。

Tool description必须明确：

* output is reciprocal-space data
* uses Phase 10I canonical `2π` convention
* first BZ is the primitive reciprocal Wigner–Seitz cell
* high-symmetry path depends on recorded provider/convention
* renderer is not included
* output is not an interactive 3D viewer
* no band energies
* no phonon calculation
* no external resources
* no artifact JavaScript

不得注册三个公开重叠工具：

```text
structure.reciprocal_lattice_summary
structure.brillouin_zone
structure.kpath
```

推荐：

* 一个公开工具：`structure.brillouin_zone`
* 多个内部纯函数/helper
* 多个独立artifact

只有在真实Registry架构强烈要求拆分时，才允许新增额外公开工具；必须在审计中解释，避免用户发现多个含义重叠的入口。

---

## 8. Readiness Metadata

虽然本阶段注册可执行工具，但产品状态必须区分：

```text
adapter: IMPLEMENTED
runtime: IMPLEMENTED
numeric fixtures: VERIFIED
JSON preview: READY
3D renderer: NOT_IMPLEMENTED
browser renderer evidence: PENDING_PHASE_10I_2
full product readiness: EVIDENCE_PENDING
```

不得在Phase 10I-1把完整Brillouin Zone产品标记为READY。

---

## 9. Input Scope

本阶段只接受单个、三维、周期性结构资源。

支持范围以现有结构pipeline为准，至少覆盖：

* CIF-derived normalized structure
* POSCAR-derived normalized structure
* canonical structure JSON
* existing in-memory normalized `pymatgen.Structure`

不得新增另一套结构parser。

### 9.1 Multiple Structures

若输入包含多个结构：

* 必须typed rejection，或
* 必须由上层resource selection明确指定单一结构

不得静默选择第一个结构。

### 9.2 Unsupported Inputs

明确拒绝：

* molecule
* non-periodic structure
* trajectory
* multiple frames
* slab/2D structure
* singular lattice
* ill-conditioned lattice
* unresolved invalid species
* unsupported magnetic-symmetry request
* arbitrary local file path
* remote URL

### 9.3 Partial Occupancy / Disorder

必须服从Phase 10I contract。

若provider不支持：

* 返回typed error，或
* 仅输出reciprocal lattice与BZ geometry，并明确`kpath unavailable`

不得静默将partial occupancy改成fully ordered structure。

---

## 10. Params Schema

使用strict whitelist。

建议参数语义：

```json
{
  "include_reciprocal_lattice": true,
  "include_brillouin_zone": true,
  "include_kpath": true,
  "standardization": "contract_default",
  "kpath_provider": "contract_default",
  "time_reversal": true,
  "symmetry_tolerance_angstrom": null,
  "angle_tolerance_degrees": null,
  "include_alternative_path_variants": false
}
```

实际字段、默认值和枚举必须服从Phase 10I contract。

### 10.1 Validation

必须：

* reject unknown params
* strict booleans
* finite numeric values
* no NaN
* no Infinity
* tolerances在contract bounds内
* provider为allowlist枚举
* standardization为allowlist枚举
* time reversal显式
* alternative variants bounded

禁止参数：

* callback
* Python code
* shell command
* arbitrary expression
* URL
* shader
* HTML
* renderer config
* camera
* texture
* arbitrary provider import path
* unrestricted search radius

### 10.2 Contract Defaults

默认tolerance必须来自versioned Phase 10I policy。

不得在Adapter中另设一组未记录的magic numbers。

---

## 11. Adapter Execution Pipeline

实现流程必须明确：

```text
1. resolve one structure resource
2. parse/reuse normalized structure
3. validate 3D periodic lattice
4. compute source structure hash
5. run approved primitive standardization
6. record transformations/provider/version
7. calculate canonical reciprocal lattice
8. verify A · B^T = 2πI
9. obtain/generate first-BZ geometry
10. normalize vertices/faces
11. reconstruct canonical edges
12. bind face generator planes
13. canonicalize topology
14. validate convexity/manifold/volume/symmetry
15. generate high-symmetry points/path
16. convert all coordinates into canonical bases
17. validate k-path
18. build artifacts
19. validate artifacts
20. canonical serialize and hash
21. write summary/recipe/manifest
```

任何核心validation失败时，不得写出标记成功的BZ artifact。

---

## 12. Primitive Standardization

必须使用Phase 10I选定provider。

记录：

* provider name
* provider version
* symprec
* angle tolerance
* source cell role
* standardized primitive lattice
* conventional lattice，若返回
* transformation direction
* transformation matrices
* origin shift
* rotation
* source/primitive hashes
* space-group number/symbol
* warnings

### 12.1 Provider Output Normalization

不得直接把provider raw output当canonical artifact。

必须转换为Phase 10I合同定义的：

* row lattice
* physics `2π` reciprocal basis
* canonical units
* transformation direction
* coordinate basis
* deterministic precision
* stable IDs

### 12.2 Equivalent Inputs

同一晶体分别由primitive和conventional input进入时，应生成等价的：

* standardized primitive reciprocal lattice
* first BZ geometry
* high-symmetry path
* content-level scientific identity

source binding和provenance可以不同。

---

## 13. Reciprocal Lattice Calculation

Canonical calculation必须使用：

```text
B = 2π · A^(-T)
```

其中`A`是标准化primitive real-space row lattice。

必须验证：

```text
A · B^T = 2πI
```

并记录：

* matrix
* convention
* units
* determinant
* reciprocal volume
* real-cell volume
* duality residual
* tolerance policy
* basis role

不得直接信任provider的reciprocal matrix而不做转换和复核。

---

## 14. Brillouin Zone Geometry Provider

优先使用Phase 10I已批准的现有helper。

不论来源是：

* pymatgen
* scipy Voronoi
* internal half-space algorithm
* validated provider

都必须转换为canonical contract。

不得：

* 假设provider返回face顺序稳定
* 假设normal朝外
* 假设vertex无重复
* 假设edge列表存在
* 假设单位包含`2π`
* 假设基于primitive cell
* 假设low-symmetry输出总是合法

---

## 15. Geometry Normalization

### 15.1 Vertices

必须：

* finite
* merge within contract tolerance
* normalize negative zero
* compute reciprocal fractional coordinates
* deterministic lexical/quantized ordering
* stable IDs
* no duplicates

### 15.2 Faces

必须：

* remove duplicate loop endpoints
* reject fewer than 3 unique vertices
* enforce coplanarity
* calculate normal
* orient normal outward from Γ
* canonicalize CCW winding
* rotate loop to canonical start vertex
* calculate area and centroid
* bind generating reciprocal vector/plane
* deterministic ordering

### 15.3 Edges

优先从canonical face loops重建。

必须：

* canonical endpoint tuple
* deduplicate
* reject self edge
* reject zero length
* bind exactly two incident faces
* deterministic ordering

不得仅依赖provider不稳定的edge顺序。

---

## 16. Generator Plane Binding

每个face必须绑定对应reciprocal generator：

```text
G = h*b1 + k*b2 + l*b3
```

并验证face vertices满足：

```text
x · G = |G|² / 2
```

在合同容差内。

必须记录：

* integer reciprocal generator
* Cartesian generator
* unit normal
* plane offset
* residual

如果多个等价generator候选：

* 使用deterministic canonical tie-break
* 记录ambiguity warning，若合同要求
* 不得随机选择

如果无法可靠绑定generator，不得静默省略关键字段并声称完整PASS。

---

## 17. Topology Validation

正式Adapter输出前必须通过Phase 10I validator：

* convex
* closed
* connected
* manifold
* no duplicate vertices
* no duplicate edges
* no duplicate faces
* no dangling edges
* each edge belongs to exactly two faces
* face loops close
* outward normals
* origin inside
* all vertices satisfy all half-spaces
* volume positive
* volume matches reciprocal primitive volume
* Euler characteristic `V-E+F=2`
* central symmetry
* content hash valid
* caps respected

不得为了通过测试放宽validator。

---

## 18. High-Symmetry Points

必须由Phase 10I批准provider生成，或读取经过验证的explicit input。

每个点必须输出：

* stable point ID
* canonical label key
* display label
* aliases
* reciprocal fractional coordinates
* reciprocal Cartesian coordinates
* standardized primitive basis identity
* provider identity
* source mapping
* optional equivalence metadata

不得只保存label到坐标的无序dict。

### 18.1 Label Normalization

必须：

* plain text
* safe Unicode normalization
* stable ASCII key
* bounded length
* no HTML
* no script
* no arbitrary LaTeX
* deterministic alias ordering

Gamma必须使用stable key，例如：

```text
GAMMA
```

display可以是：

```text
Γ
```

---

## 19. K-Path Generation

必须输出：

* selected path variant
* provider/convention
* time-reversal setting
* points
* ordered segments
* discontinuities
* Cartesian segment length
* cumulative branch distance，若contract包含
* warnings
* hashes

### 19.1 Discontinuity

必须显式表达：

```text
X | K
```

不得通过重复点或空label让consumer猜测。

### 19.2 Multiple Variants

默认只输出一个canonical selected variant。

若参数允许alternative variants：

* 必须bounded
* deterministic ordering
* separate variant IDs
* separate segment IDs
* no ambiguous merging

### 19.3 Path Unavailable

BZ geometry和k-path必须解耦。

如果：

* reciprocal lattice有效
* BZ geometry有效
* 但provider无法产生可信k-path

则根据Phase 10I contract选择：

* typed partial artifact policy，或
* tool failure

如果合同允许partial：

* `kpath.json`必须明确`unavailable`
* summary必须说明
* 不得伪造高对称路径
* job结果和readiness不得声称kpath READY

---

## 20. Time-Reversal Policy

必须保存实际：

```text
time_reversal_used: true | false
```

若输入含磁性或time-reversal可能破缺的metadata：

* 必须执行合同策略
* 不得默认普通non-magnetic k-path
* 可typed reject
* 可禁用kpath仅输出BZ，前提是合同允许

不得忽略该风险。

---

## 21. Artifact Contract

至少生成以下六个artifact。

### 21.1 `reciprocal_lattice.json`

必须符合Phase 10I正式reciprocal lattice schema。

包含：

* source/primitive binding
* canonical matrix
* convention
* units
* volume
* duality residual
* transformations
* provider
* tolerances
* security
* hash

### 21.2 `brillouin_zone.json`

必须符合正式BZ schema。

包含：

* reciprocal binding
* center
* vertices
* edges
* faces
* generator planes
* volume
* surface area
* topology summary
* validation
* tolerances
* warnings
* security
* provenance
* hash

### 21.3 `kpath.json`

必须符合正式k-path schema。

包含：

* reciprocal binding
* provider
* convention
* points
* labels
* aliases
* variants
* segments
* discontinuities
* time reversal
* validation
* warnings
* security
* hash

### 21.4 `brillouin_zone_manifest.json`

包含：

* schema versions
* logical artifact references
* source structure
* content hashes
* entry artifact
* renderer included: false
* WebGL artifact included: false
* executable assets: none
* external resources: none
* preview: JSON-only
* security
* provenance

### 21.5 `summary.md`

必须包括：

#### Input

* structure resource
* filename/resource identity
* parser
* formula
* site count
* source lattice
* source cell role

#### Standardization

* provider
* version
* symmetry tolerance
* source → primitive transform
* space group
* warnings

#### Reciprocal Lattice

* convention
* units
* matrix
* volume
* duality validation

#### First Brillouin Zone

* vertices
* edges
* faces
* volume
* topology validation
* central symmetry
* generator-plane validation

#### K-Path

* provider/convention
* high-symmetry points
* segments
* discontinuities
* time reversal
* alternatives

#### Limits / Warnings

* caps
* applied tolerance policy
* partial support
* unsupported magnetic/dimensional cases

#### Preview

* JSON-only
* renderer not included
* interactive 3D deferred to Phase 10I-2

#### Security

* no artifact JavaScript
* no external URLs
* no renderer bundle
* no remote assets

### 21.6 `recipe.json`

记录：

* tool ID
* input resource ID/hash
* normalized params
* parser
* standardization provider/version
* tolerance policy
* reciprocal formula
* BZ provider
* normalization steps
* kpath provider
* canonicalization
* validation steps
* output schema versions
* deterministic: true
* dependency versions
* renderer included: false
* external resources: none

不得包含可执行代码。

---

## 22. Determinism

同一输入和同一参数必须生成等价：

* primitive lattice
* reciprocal matrix
* vertex order
* vertex IDs
* face loops
* face IDs
* edge order
* generator-plane identity
* point IDs
* labels
* path variants
* segment IDs
* warning order
* JSON serialization
* content hashes

不得把以下内容纳入科学content hash：

* random job ID
* runtime timestamp
* absolute filesystem path
* browser state
* future camera state

必须提供至少两次replay并比较hash。

---

## 23. Caps

必须执行Phase 10I hard caps。

至少包括：

* max vertices
* max edges
* max faces
* max vertices per face
* max high-symmetry points
* max aliases
* max path variants
* max segments
* max discontinuities
* max label length
* max warnings
* max JSON bytes
* max provider metadata bytes
* max candidate geometry work，若合同已有

Over-cap必须typed failure。

不得truncate：

* vertices
* faces
* edges
* path endpoints

截断会破坏科学拓扑。

---

## 24. Typed Errors

至少覆盖：

* resource missing
* multiple structures unsupported
* unsupported resource kind
* structure parse failed
* non-periodic structure
* unsupported dimensionality
* invalid lattice
* singular lattice
* ill-conditioned lattice
* primitive standardization failed
* provider unavailable
* provider convention mismatch
* invalid transformation
* reciprocal duality failed
* BZ geometry generation failed
* duplicate vertex
* invalid face
* open polyhedron
* non-manifold topology
* inward normal
* generator-plane binding failed
* origin outside BZ
* volume mismatch
* central-symmetry failure
* kpath generation failed
* invalid high-symmetry label
* invalid segment
* unsupported time-reversal policy
* magnetic structure unsupported
* cap exceeded
* payload too large
* schema validation failed
* manifest validation failed
* hash mismatch
* artifact write failed

错误不得泄漏：

* absolute path
* private URL
* token
* API key
* stack trace
* environment variable

---

## 25. Tool Registry

Registry entry必须包含：

* tool ID
* domain
* precise description
* required resource kinds
* strict params schema
* output artifacts
* schema versions
* deterministic flag
* resource caps
* typed errors
* security properties
* renderer not included
* external network false
* executable artifact false
* readiness/evidence-pending metadata，若Registry支持

Registry tests必须确认：

* tool存在
* ID唯一
* params严格
* expected artifacts完整
* no WebGL capability
* no interactive-viewer claim
* no external resource capability
* no executable artifact capability
* existing tools unchanged
* no overlapping public tool

---

## 26. Planner Routing

允许增加明确的**数据生成**路由。

正向示例：

* 计算这个晶体的第一布里渊区
* 生成倒易晶格和高对称路径
* 导出这个结构的Brillouin zone数据
* 计算这个晶体的k路径
* Generate first Brillouin zone data
* Export the reciprocal lattice and high-symmetry path
* Build a Brillouin zone JSON artifact
* Compute the standardized k-path for this crystal

必须路由到：

```text
structure.brillouin_zone
```

### 26.1 3D Requests

以下请求不得声称已经有3D Renderer：

* 打开交互式布里渊区3D viewer
* 用Three.js显示BZ
* 显示可旋转倒空间多面体
* Render the Brillouin zone interactively

处理方式：

* 明确返回当前只能生成BZ JSON数据，Renderer将在Phase 10I-2提供；或
* 保持renderer-specific request为deferred/unsupported

不得显示“interactive 3D available”。

### 26.2 Negative Routing

不得误路由：

* 计算电子能带
* 计算声子
* 播放声子模式
* 显示MD trajectory
* 生成Fermi surface
* 计算Monkhorst-Pack mesh
* 显示charge density
* 生成XRD
* 做CrystalNN
* 编辑结构
* 运行DFT

必须增加positive和negative tests。

---

## 27. PlanValidator / Runtime

必须证明合法AnalysisPlan可以引用：

```text
structure.brillouin_zone
```

必须覆盖：

* valid params accepted
* unknown params rejected
* invalid tolerance rejected
* invalid provider rejected
* invalid resource rejected
* tool resolved from Registry
* Adapter invoked by QueueWorkerRuntime
* artifacts persisted
* events recorded
* tool-call state completed/failed
* typed failure propagated
* no core runtime semantic changes

不得只直接调用Adapter函数。

---

## 28. API / Service-Backed Smoke

本阶段不是完整Browser/API evidence阶段，但必须有真实execution smoke。

至少覆盖：

1. simple cubic
2. hexagonal
3. triclinic
4. conventional/primitive equivalent pair
5. invalid singular lattice
6. unsupported non-periodic input

记录sanitized：

* request
* selected tool
* plan
* job
* tool call
* artifacts
* schema versions
* validation state
* hashes
* failure state

完整跨浏览器、Renderer和accessibility evidence留给Phase 10I-2。

---

## 29. JSON-Only Preview

生成的artifacts必须可进入现有安全JSON preview。

允许最小additive支持显示：

* schema version
* reciprocal convention
* units
* primitive lattice
* vertex count
* edge count
* face count
* BZ volume
* point count
* segment count
* provider
* validation
* warnings
* renderer not included

不得：

* 添加Three.js
* 创建canvas
* 创建WebGL context
* 实现BZ surface
* 实现camera
* 实现label overlay
* 实现reciprocal picking

如果通用JSON preview已经足够，不要修改frontend。

---

## 30. Scientific Reference Tests

不得只用provider输出验证provider输出。

### 30.1 Simple Cubic

验证：

* `B=(2π/a)I`
* 8 vertices
* 12 edges
* 6 faces
* boundaries `±π/a`
* volume `(2π/a)^3`
* outward normals
* generator planes
* Euler characteristic
* central symmetry

### 30.2 BCC / FCC

验证：

* reciprocal-lattice relationship
* expected topology
* volume invariant
* no BCC/FCC swap
* provider labels
* path convention

Expected topology必须来源于已审核reference，而不是凭记忆填写。

### 30.3 Hexagonal

验证：

* reciprocal duality
* non-orthogonal geometry
* axial/basal faces
* Γ、M、K、A、L、H provider identities
* deterministic path

### 30.4 Triclinic

验证：

* no symmetry hardcoding
* closed convex polyhedron
* correct volume
* canonical replay
* stable hashes

### 30.5 Primitive / Conventional

验证：

* equivalent standardized primitive lattice
* equivalent BZ geometry
* equivalent k-path
* transformation metadata
* distinct source provenance

---

## 31. Provider Cross-Checks

如果使用seekpath生成k-path：

* 将output转换为canonical row/`2π` convention
* 验证point coordinates
* 验证primitive lattice
* 验证transformation metadata
* 记录version

如果使用pymatgen生成BZ：

* 不信任原face顺序
* 不信任normal方向
* 不信任unit convention
* 完整canonicalization

如果两个provider都可用，可在tests中做有限交叉检查，但不得把两者结果混合为一个未注明来源的artifact。

---

## 32. Security

必须自动验证：

* no artifact JavaScript
* no HTML
* no CSS
* no shader
* no external URL
* no remote texture
* no CDN
* no iframe
* no eval
* no Function constructor
* no callback
* no arbitrary expression
* no arbitrary local file path
* no notebook execution
* no script execution
* no real LLM requirement
* no external network
* plain-text labels
* bounded metadata
* safe filenames
* typed/redacted errors

必须输出：

```text
NO_SECRET_PATTERN_HITS
```

并记录：

```text
NO_BRILLOUIN_ZONE_EXTERNAL_NETWORK_REQUESTS
```

若本阶段无Browser网络runner，可通过代码、artifact和service-backed network audit证明，不得伪造浏览器network evidence。

---

## 33. Dependency Policy

优先不新增依赖。

如果Phase 10I已经批准并引入provider依赖：

* 复用该依赖
* 不重复引入另一套功能重叠依赖
* 固定version/provenance

如果Adapter实际需要新增依赖：

* 必须先证明现有依赖不能满足合同
* 记录license
* version
* transitive dependencies
* wheel/platform availability
* CI impact
* package size
* deterministic/offline behavior
* security findings
* lockfile变化

未经充分理由不得同时新增seekpath和另一个重型对称性依赖。

npm/Python audit若registry不可用：

* 记录unavailable
* 不得写clean
* 检查lockfile diff和依赖reachability

---

## 34. Evidence Directory

建议新增：

```text
docs/phase10i/evidence/phase10i1_brillouin_zone_adapter/
```

至少包含：

* README
* pre-implementation audit
* sanitized execution captures
* selected plans
* adapter outputs
* reciprocal lattice artifacts
* BZ artifacts
* kpath artifacts
* manifests
* validation outputs
* reference calculations
* deterministic replay
* hash comparison
* negative cases
* registry evidence
* routing evidence
* service-backed smoke
* JSON preview compatibility
* security audit
* dependency audit
* secret scan
* CI record

不得提交：

* secrets
* private paths
* external URLs
* browser cache
* node_modules
* large raw datasets
* renderer bundles
* generated videos
* arbitrary provider dumps

---

## 35. Tests

必须增加：

### Adapter

* valid cubic
* tetragonal
* orthorhombic
* hexagonal
* monoclinic
* triclinic
* BCC
* FCC
* primitive/conventional
* invalid structure
* singular lattice
* ill-conditioned lattice
* over-cap

### Artifacts

* reciprocal schema
* BZ schema
* kpath schema
* manifest schema
* summary
* recipe
* media types
* hashes
* security flags

### Canonicalization

* shuffled provider vertices
* reversed face loops
* shuffled faces
* duplicate vertex within tolerance
* negative zero
* provider nondeterministic order
* repeated replay

### Topology

* convexity
* closedness
* manifold
* incidence
* outward normals
* generator planes
* Euler characteristic
* volume
* central symmetry

### K-Path

* labels
* aliases
* duplicate coordinates
* discontinuities
* variants
* path lengths
* time reversal
* provider metadata

### Registry / Planner

* registry entry
* uniqueness
* params
* positive routing
* negative routing
* 3D-renderer request boundary

### Runtime

* AnalysisPlan
* PlanValidator
* QueueWorkerRuntime
* artifacts
* typed failures
* service-backed smoke

### Regression

* Phase 10I contract
* Phase 10H phonon/q-point compatibility
* Phase 10H-5 animation
* Phase 10G trajectory
* Phase 10F viewer
* structure parsers
* static structure adapters
* service-backed integration
* no-skipped assertion

---

## 36. Documentation

新增或更新：

* Phase 10I-1 implementation overview
* Adapter contract mapping
* provider strategy
* input support
* params
* primitive standardization
* reciprocal computation
* BZ normalization
* generator-plane mapping
* k-path generation
* deterministic canonicalization
* artifacts
* errors
* caps
* security
* replay
* known limitations
* Phase 10I-2 handoff

更新：

* `docs/index.md`
* `persistent/DESIGN_PROGRESS.md`
* `persistent/TASK_BOARD.md`
* `persistent/CHANGELOG.md`
* `persistent/OPEN_QUESTIONS.md`
* `persistent/TOOL_REGISTRY_NOTES.md`
* `persistent/ARCHITECTURE_DECISIONS.md`

Persistent必须记录：

```text
structure.brillouin_zone:
  adapter: implemented
  runtime: implemented
  artifacts: implemented
  numeric fixtures: verified
  JSON preview: ready
  3D renderer: not implemented
  browser renderer evidence: pending
  full product readiness: pending Phase 10I-2
```

---

## 37. 明确 Deferred

Phase 10I-1完成后仍然deferred：

* Three.js BZ Renderer
* 3D face/edge rendering
* labels in 3D
* reciprocal axes UI
* point picking
* segment highlighting
* camera presets
* BZ inspector
* band/BZ linkage
* phonon/BZ linkage
* Chromium/Firefox/WebKit renderer matrix
* mobile renderer
* accessibility renderer audit
* GPU performance evidence
* deterministic renderer screenshots
* PNG reciprocal export
* custom k-path editing
* magnetic BZ
* surface BZ
* irreducible wedge
* k-point meshes
* Fermi surfaces
* electronic band calculation

不得把这些写成READY。

---

## 38. Required Checks

至少运行：

```bash
git diff --check
uv lock --check
npm --prefix apps/web ls
npm --prefix apps/web test
npm --prefix apps/web run typecheck
npm --prefix apps/web run build
uv run python -m pytest -q
```

并单独运行：

* reciprocal contract tests
* BZ contract tests
* kpath contract tests
* Adapter tests
* provider normalization tests
* topology tests
* generator-plane tests
* canonicalization tests
* scientific reference tests
* fixture replay
* registry tests
* Planner positive/negative tests
* PlanValidator tests
* runtime integration
* service-backed smoke
* JSON preview regression
* security tests
* Phase 10 Closure Regression Pack
* Phase 10G regression
* Phase 10H through 10H-5 regression
* Phase 10I regression
* no-skipped assertion
* secret scan

必须如实记录：

* passed
* failed
* skipped
* unavailable

不得将skipped写成passed。

---

## 39. Commit / Push / CI

所有实现、测试、evidence、docs和persistent完成后：

```bash
git status --short
git diff --stat
git add <only Phase 10I-1 related files>
git commit -m "Implement Brillouin zone adapter"
git push origin master
```

等待current-HEAD CI。

必须确认：

* backend unit success
* frontend tests success
* typecheck success
* build success
* BZ Adapter tests success
* scientific reference tests success
* registry/Planner tests success
* Phase 10 Closure success
* Phase 10G success
* Phase 10H through 10H-5 success
* Phase 10I contract success
* service-backed integration success
* no-skipped assertion success
* origin/master equals HEAD
* git status clean

不得伪造commit、CI run、test counts或git状态。

---

## 40. PASS 判定

PASS必须全部满足：

* 真实Adapter实现
* `structure.brillouin_zone`注册
* strict params完成
* single-structure input完成
* primitive standardization完成
* provider/version记录
* canonical `2π` reciprocal lattice完成
* duality验证完成
* first BZ geometry完成
* vertices/edges/faces完整
* outward winding完成
* generator-plane binding完成
* convex/closed/manifold验证完成
* volume invariant完成
* Euler characteristic完成
* central symmetry完成
* high-symmetry points完成
* k-path完成
* labels/aliases安全
* discontinuities明确
* time-reversal metadata完成
* deterministic canonicalization完成
* content hashes稳定
* artifacts完整
* manifest完整
* summary/recipe完整
* caps完整
* typed errors完整
* Planner data-routing完成
* interactive 3D请求不误导
* QueueWorkerRuntime执行完成
* service-backed smoke完成
* JSON-only preview兼容
* cubic/BCC/FCC/hexagonal/triclinic fixtures通过
* primitive/conventional等价验证通过
* no artifact JS
* no external URL
* no renderer实现
* Phase 10I contract不回退
* Phase 10H q-point语义不回退
* tests通过
* CI通过
* origin/master等于HEAD
* git status clean

---

## 41. PARTIAL_PASS 仅允许

仅允许：

* 磁性/time-reversal-broken结构明确DEFERRED_BY_DESIGN
* partial occupancy只能输出BZ但不能输出k-path，且合同明确允许partial artifact
* alternative path variants未实现，但canonical path完整
* 2D/1D BZ明确deferred
* 一个低对称fixture的provider label存在已记录差异，但geometry和合同验证完整
* 通用JSON preview已足够，因此没有新增专用frontend
* npm/Python audit因既有registry不可用，但依赖和lockfile审计完整

以下缺失不得PARTIAL_PASS：

* Adapter
* Registry
* Runtime execution
* reciprocal lattice
* BZ geometry
* topology validation
* canonicalization
* cubic/hexagonal/triclinic fixtures
* deterministic replay
* artifact validation

这些缺失必须FAIL。

---

## 42. FAIL 条件

以下任一情况必须FAIL：

* 只有docs或fixtures
* 没有真实Adapter
* 只直接调用函数，未进入Runtime
* 没有Tool Registry
* 没有strict params
* 使用source conventional cell直接构造错误BZ
* reciprocal convention不一致
* 丢失`2π`
* row/column混用
* provider raw output未经canonicalization
* face normals方向不验证
* topology不验证
* volume不验证
* BCC/FCC混淆
* k-path只按label识别
* path discontinuity隐式
* time reversal未记录
* geometry被静默truncate
* provider failure后伪造path
* output schema与Phase 10I冲突
* artifact包含JS/HTML/URL/shader
* 提前实现不受控Renderer
* Planner声称已有交互式3D
* unsupported官方case被标记PASS
* browser evidence伪造
* skipped写成passed
* Phase 10H或10I回退
* CI失败却声明PASS
* git不clean却声明完成

---

## 43. 最终报告格式

完成后必须输出：

# Phase 10I-1 Brillouin Zone Adapter Result

## 1. Conclusion

PASS / PARTIAL_PASS / FAIL

## 2. Baseline

* Phase 10I commit
* initial HEAD
* branch
* origin/master
* initial status
* final HEAD
* final status

## 3. Pre-Implementation Audit

* contracts
* dependencies
* provider selection
* existing overlap
* selected strategy

## 4. Tool / Registry

* tool ID
* domain
* description
* params
* inputs
* outputs
* caps
* readiness metadata

## 5. Structure Standardization

* parser
* source cell
* primitive cell
* conventional cell
* provider
* transformations
* hashes
* partial occupancy
* magnetic/time-reversal policy

## 6. Reciprocal Lattice

* formula
* convention
* units
* matrix
* duality
* volume
* validation

## 7. Brillouin Zone Geometry

* provider
* vertices
* edges
* faces
* generator planes
* canonicalization
* winding
* convexity
* manifold
* Euler characteristic
* central symmetry
* volume

## 8. High-Symmetry Path

* provider
* points
* labels
* aliases
* variants
* segments
* discontinuities
* time reversal
* limitations

## 9. Artifacts

* reciprocal lattice
* BZ
* kpath
* manifest
* summary
* recipe
* schema versions
* hashes

## 10. Runtime / API

* Planner
* PlanValidator
* persisted plan
* QueueWorkerRuntime
* service-backed smoke
* successful cases
* negative cases

## 11. Determinism

* canonical order
* replay
* hash stability
* primitive/conventional equivalence

## 12. Fixtures / References

* simple cubic
* BCC
* FCC
* tetragonal
* orthorhombic
* hexagonal
* monoclinic
* triclinic
* invalid cases

## 13. JSON Preview

* artifact detection
* displayed metadata
* renderer status
* fallback behavior

## 14. Security

* artifact JS
* HTML/CSS/shader
* external URLs
* network
* labels
* errors
* secrets
* dependencies

## 15. Tests

* backend
* frontend
* Adapter
* contracts
* topology
* reference
* registry
* Planner
* runtime
* regression
* service-backed
* no-skipped

## 16. Evidence

* directory
* API captures
* artifact samples
* validation
* replay
* hashes
* audit records

## 17. Files

列出主要implementation、tests、fixtures、evidence、docs和persistent文件。

## 18. Explicitly Not Implemented

* Three.js Renderer
* 3D product UI
* reciprocal picking
* linked band/BZ view
* renderer browser matrix
* magnetic/surface BZ
* electronic/Fermi features

## 19. Checks

* diff
* lock
* dependency tree
* frontend tests
* typecheck
* build
* backend tests
* fixture replay
* network
* secrets

## 20. Commit / CI

* commit
* HEAD
* CI run
* unit
* frontend
* build
* Adapter tests
* contract tests
* service-backed
* no-skipped
* origin
* git status

## 21. Readiness

预期：

```text
reciprocal lattice Adapter: READY
first BZ geometry Adapter: READY
high-symmetry path Adapter: READY
Tool Registry: READY
runtime execution: READY
JSON-only preview: READY
numeric fixture validation: READY
3D Brillouin Renderer: NOT_IMPLEMENTED
browser/GPU evidence: PENDING
full Brillouin Zone product: PARTIAL_READY
```

## 22. Whether Allowed to Enter Next Phase

可以 / 不可以

只有 Phase 10I-1 完成、current-HEAD CI通过、科学fixtures、Runtime、Artifacts与安全边界闭合且git clean后，才允许进入：

```text
Phase 10I-2：Brillouin Renderer / Evidence
```

现在开始执行。

首先读取真实Phase 10I Result、schema、validator、provider decision和现有structure/runtime代码，输出Pre-Implementation Audit；然后直接完成`structure.brillouin_zone` Adapter、primitive standardization、reciprocal lattice、first-BZ geometry、high-symmetry path、Artifacts、Registry、Planner、Runtime、service-backed smoke、tests、security、commit和CI闭环。

本阶段不得进入Three.js Brillouin Zone Renderer。


---END---
