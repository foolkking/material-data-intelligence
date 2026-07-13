---TASK---
 状态：处理中
 # Phase 10G：Trajectory Contrac

进入 Phase 10G：Trajectory Contract。

可以默认：

* Phase 10 Closure Regression Pack 已完成并通过
* Phase 10 overall 已正式标记为 READY
* `structure.viewer_3d` 已正式注册并完成产品闭环
* static periodic viewer、picking、measurement、supercell、clipping、camera、export均已稳定
* viewer performance budgets、lifecycle、context-loss、accessibility、mobile和cross-browser基础均已完成
* current static production scene schema仍为 `phase10f18.viewer_scene.v2
* current static viewer manifest仍为正式v2 manifes
* periodic identity、canonical topology、artifact security和runtime正式路径保持稳定
* 当前branch、HEAD、working tree和Phase 10 Closure CI可视为正确且clean

本阶段不需要重复Phase 10 Closure baseline检查。

本阶段的主要任务是：

> 建立可用于分子动力学轨迹、结构弛豫轨迹和一般结构演化序列的统一、严格、可扩展、受资源预算约束的trajectory数据contract，为后续Trajectory Parser / Adapter和Trajectory Viewer提供稳定基础。

本阶段只完成：

* trajectory数据模型
* frame identity
* atom identity
* coordinate/lattice conventions
* time and unit policy
* optional properties contrac
* parser boundary
* caps
* validation
* fixtures
* reference tests
* security
* readiness documentation

本阶段不实现正式trajectory parser，不实现viewer playback，不实现动画。

---

# 1. 本阶段定位

Phase 10G是动态结构能力的基础contract阶段。

它必须解决：

* 一个trajectory是什么
* 一个frame是什么
* 原子如何跨frame保持身份
* 晶格如何随frame变化
* 坐标如何解释
* 周期边界如何表示
* 时间如何表示
* velocities、forces、energy、temperature等可选数据如何表示
* 大型轨迹如何受cap约束
* parser和viewer未来如何安全消费该contrac
* malformed、incomplete、inconsistent trajectory如何拒绝

本阶段不是：

* trajectory parser phase
* viewer playback phase
* MD simulation phase
* trajectory analysis phase
* RDF ensemble phase
* trajectory editing phase
* production registration phase

---

# 2. 本阶段目标

必须完成以下十类工作：

1. **Trajectory architecture audit**
2. **Canonical trajectory schema**
3. **Frame and atom identity contract**
4. **Coordinate、lattice和periodic boundary policy**
5. **Time、units和optional properties policy**
6. **Validation、caps和typed errors**
7. **Deterministic serialization and hashing**
8. **Fixtures and independent reference tests**
9. **Security and compatibility boundaries**
10. **Docs、evidence和readiness closure**

本阶段必须产生实际contract实现代码和validator代码。

如果最终只有规划文档、schema草图或readiness matrix，没有可执行validator和tests，本阶段必须判定为FAIL。

---

# 3. 严格禁止范围

本阶段不得实现：

* trajectory file parser
* XYZ parser
* extended XYZ parser
* ASE trajectory parser
* LAMMPS dump parser
* trajectory playback
* animation loop
* frame slider
* play/pause
* atom interpolation
* dynamic bonds
* trajectory viewer registration
* trajectory expor
* trajectory editing
* frame mutation
* velocity editing
* force editing
* MD simulation
* relaxation execution
* phonon animation
* ensemble RDF
* mean-square displacemen
* diffusion coefficien
* VACF
* trajectory clustering
* external API
* notebook execution
* script execution
* real LLM

不得：

* 修改static `viewer_scene.v2
* 将trajectory fields直接塞入static viewer scene contrac
* 将trajectory注册成`structure.viewer_3d`的隐式模式
* 使用数组位置作为唯一跨frame atom identity而不定义前提
* 静默接受frame间atom count变化
* 静默接受species ordering变化
* 静默混用Cartesian和fractional coordinates
* 静默混用wrapped和unwrapped positions
* 静默混用时间单位
* 允许NaN或Infinity
* 允许无限frames
* 允许无限atoms
* 允许无限metadata
* 允许外部URL引用frame数据
* 允许artifact JavaScrip
* 允许artifact callback
* 允许任意二进制payload嵌入JSON
* 以压缩字符串绕过byte caps
* 在没有contract的情况下预先决定viewer实现细节
* 将trajectory contract标记为正式产品READY

允许：

* schema
* validator
* typed models
* deterministic serializers
* test fixtures
* reference utilities
* docs
* evidence
* persistent updates

---

# 4. 必读实现

开始后直接阅读当前真实代码，不做baseline检查。

## 4.1 Existing Structure Contracts

搜索：

```bash
rg -n "viewer_scene|structure_input|lattice|fractional|cartesian|siteIndex|PeriodicSiteRef|schema_version" backend packages apps tests


确认：

* static structure input contrac
* lattice convention
* fractional/Cartesian conversion
* site ordering
* species model
* occupancy model
* metadata model
* existing numeric guard
* current schema validation framework

## 4.2 Artifact and Manifest Contracts

搜索：

```bash
rg -n "manifest|artifact validator|schema validator|deterministic|sha256|provenance|security" backend packages tests


确认：

* artifact schema pattern
* manifest pattern
* security metadata pattern
* canonical JSON serialization
* hash generation
* warning ordering
* typed error conventions

## 4.3 Runtime Caps

搜索：

```bash
rg -n "MAX_.*SITE|MAX_.*BYTE|MAX_.*FRAME|budget|cap|limit" backend packages apps tests


确认：

* structure site caps
* artifact byte caps
* frontend preview caps
* runtime memory policies
* integer overflow guards
* JSON size validation

## 4.4 Existing Trajectory References

搜索：

```bash
rg -n "trajectory|frame_index|timestep|velocity|force|temperature|molecular dynamics|relaxation" .


必须识别：

* 是否已有未注册trajectory模型
* 是否有fixture
* 是否有dependency对象
* 是否有旧实验代码
* 是否有future notes
* 是否有命名冲突

---

# 5. 修改前输出审计

修改任何代码前输出：

# Phase 10G Trajectory Contract Pre-Implementation Audi

## 1. Existing Structure Model

* static structure schema:
* lattice convention:
* coordinate convention:
* species representation:
* occupancy:
* site ordering:
* numeric guards:
* caps:
* reusable components:

## 2. Existing Artifact Model

* schema framework:
* validator framework:
* manifest:
* provenance:
* security metadata:
* deterministic serialization:
* hashing:
* warning ordering:

## 3. Existing Trajectory-Related Code

* models:
* fixtures:
* parser code:
* viewer code:
* experimental code:
* docs:
* conflicts:
* reusable pieces:

## 4. Contract Risks

至少列出：

* atom identity drif
* atom count mismatch
* species ordering mismatch
* coordinate mode mismatch
* wrapped/unwrapped ambiguity
* fixed/variable lattice ambiguity
* timestamp ambiguity
* unit ambiguity
* missing frames
* duplicate frame index
* nonmonotonic time
* nonfinite values
* integer overflow
* artifact size blowup
* metadata abuse
* future parser incompatibility
* static viewer schema contamination

## 5. Selected Strategy

说明：

* trajectory schema:
* frame schema:
* atom identity:
* lattice policy:
* coordinate policy:
* periodic boundary policy:
* time policy:
* optional properties:
* caps:
* determinism:
* compatibility:
* security:

## 6. Planned Files

列出预计修改或新增：

* schema/model
* validator
* serializer
* caps
* fixtures
* backend tests
* frontend/shared contract tests，若需要
* evidence
* docs
* persisten

审计后直接继续执行。

---

# 6. Canonical Schema Family

本阶段建议建立三个核心schema：

```tex
phase10g.trajectory.v1
phase10g.trajectory_frame.v1
phase10g.trajectory_manifest.v1


可选建立：

```tex
phase10g.trajectory_summary.v1


不得复用static viewer scene schema作为trajectory容器。

---

# 7. Trajectory Top-Level Contrac

建议结构：

```json
{
  "schema_version": "phase10g.trajectory.v1",
  "trajectory_id": "stable-id",
  "kind": "molecular_dynamics",
  "coordinate_mode": "fractional",
  "position_wrapping": "wrapped",
  "lattice_mode": "fixed",
  "atom_identity_mode": "stable_index",
  "time": {
    "unit": "femtosecond",
    "origin": 0.0
  },
  "atoms": {
    "count": 2,
    "species": ["Si", "Si"],
    "labels": ["Si1", "Si2"]
  },
  "fixed_lattice": [
    [5.43, 0.0, 0.0],
    [0.0, 5.43, 0.0],
    [0.0, 0.0, 5.43]
  ],
  "frames": [],
  "properties": {
    "positions": true,
    "velocities": false,
    "forces": false,
    "energy": false,
    "temperature": false,
    "stress": false
  },
  "provenance": {},
  "warnings": [],
  "security": {
    "contains_javascript": false,
    "external_urls": []
  }
}


字段名可以按项目现有风格调整，但语义必须完整。

---

# 8. Trajectory Kind

必须定义受控枚举。

建议第一版支持：

```tex
molecular_dynamics
geometry_optimization
structure_sequence
unknown_static_sequence


语义：

## molecular_dynamics

* 有物理时间或step
* atom identity稳定
* 通常atom count固定

## geometry_optimization

* frame表示优化步骤
* time可能不存在
* 需要step index
* energy/force可能存在

## structure_sequence

* 一般有序结构序列
* 不声称MD时间语义

## unknown_static_sequence

* 仅表示有序frame集合
* 不允许推断动力学结论

不得允许artifact定义任意kind字符串。

---

# 9. Frame Contrac

建议：

```json
{
  "schema_version": "phase10g.trajectory_frame.v1",
  "frame_index": 0,
  "step": 0,
  "time": 0.0,
  "lattice": null,
  "positions": [
    [0.0, 0.0, 0.0],
    [0.25, 0.25, 0.25]
  ],
  "velocities": null,
  "forces": null,
  "energy": null,
  "temperature": null,
  "stress": null,
  "metadata": {}
}


必须固定：

* frame_index从0开始
* frame_index连续
* frame顺序由数组顺序和frame_index共同验证
* positions是必需字段
* lattice是否出现由lattice_mode决定
* optional arrays长度必须等于atom coun
* metadata受键数量和byte caps限制

---

# 10. Atom Identity Contrac

这是本阶段最关键部分之一。

第一版推荐：

```tex
atom_identity_mode = stable_index


定义：

* top-level `atoms.species[i]
* top-level atom index `i
* 在所有frame中指向同一逻辑原子
* frame positions数组索引必须与top-level atom index一致
* frame间不允许reorder
* 不允许atom count变化
* 不允许species在frame中变化

可选支持stable label：

```json
{
  "atom_id": 0,
  "label": "Si1",
  "species": "Si"
}


但科学身份仍由stable integer index主导。

不得：

* 仅依赖元素符号
* 仅依赖坐标近邻匹配
* 每frame重新排序
* 自动猜测atom correspondence
* 允许一帧中删除/新增atom

动态反应、variable atom count trajectory延后到未来schema。

---

# 11. Species and Occupancy

第一版trajectory建议仅支持：

* ordered species
* occupancy = 1

如需兼容static structure的partial occupancy，必须明确：

* occupancy是否top-level固定
* frame间不得变化
* viewer是否支持

推荐第一版：

```tex
partial occupancy: unsupported


并给出typed error。

原因：

* 动态trajectory中的partial occupancy科学语义不清晰
* 容易和ensemble/disorder混淆

typed code建议：

```tex
TRAJECTORY_PARTIAL_OCCUPANCY_UNSUPPORTED


---

# 12. Coordinate Mode

必须在top-level固定一种：

```tex
fractional
cartesian


所有frame必须一致。

不得每frame混用。

## fractional

positions表示相对于该frame lattice的fractional coordinates。

要求：

* lattice必须可用
* fixed lattice使用top-level lattice
* variable lattice使用frame lattice

## cartesian

positions单位必须明确。

建议内部统一为：

```tex
angstrom


不得在frame级改变单位。

---

# 13. Position Wrapping Policy

必须定义：

```tex
wrapped
unwrapped
unknown


## wrapped

fractional coordinates通常在canonical interval内，但允许数值容差。

推荐canonical interval：

```tex
[0,1)


必须定义边界容差。

## unwrapped

允许fractional coordinates超出cell范围，用于扩散和连续轨迹。

## unknown

不得用于需要连续位移的分析。

第一版contract必须保存原始wrapping语义，不自动wrap或unwrap。

禁止validator静默改变positions。

---

# 14. Lattice Mode

必须支持：

```tex
fixed
variable


## fixed

* top-level必须包含`fixed_lattice
* frame不得重复提供不同lattice
* frame lattice应为null或省略
* 所有positions使用同一lattice

## variable

* 每个frame必须包含lattice
* top-level不得把单一fixed lattice当作权威
* 支持NPT、cell relaxation等情况

不支持：

* 部分frame缺lattice
* 隐式沿用上一frame
* frame混用fixed/variable语义

---

# 15. Lattice Mathematics

必须继承Phase 10既定约定：

```tex
row lattice vectors


即：

```tex
cartesian =
fractional[0] * a
+ fractional[1] * b
+ fractional[2] * c


每个lattice必须：

* 3×3
* finite
* determinant nonzero
* condition number在既定安全范围
* 单位angstrom
* deterministic validation

优先复用Phase 10F已有inverse、determinant和condition guard。

不得建立第二套冲突阈值。

如果Phase 10F当前标准是：

```tex
relative determinant threshold = 1e-12
maximum condition number = 1e8


应继续复用，除非审计发现更正式的统一常量。

---

# 16. Periodic Boundary Contrac

必须定义：

```json
{
  "periodic_boundary": [true, true, true]
}


允许未来支持：

* 3D periodic
* slab-like partial periodicity
* nonperiodic sequence

但第一版是否支持partial periodicity必须明确。

推荐第一版：

* `[true,true,true]
* `[false,false,false]

partial periodicity：

```tex
DEFERRED_BY_DESIGN


如果已有结构contract支持partial PBC，可以复用，但必须有tests。

不得通过lattice是否存在来猜PBC。

---

# 17. Time Contrac

时间必须区分：

* frame index
* simulation step
* physical time

## frame_index

必需、连续、从0开始。

## step

可选整数。

要求：

* nonnegative
* monotonic nondecreasing
* 不要求连续

## time

对MD trajectory可选或必需，必须根据kind定义。

推荐：

### molecular_dynamics

* time必需
* monotonic nondecreasing
* unit必需

### geometry_optimization

* time可省略
* step建议必需

### structure_sequence

* time可省略

支持单位建议第一版：

```tex
femtosecond
picosecond


内部canonical unit建议：

```tex
femtosecond


不得接受任意时间unit字符串。

---

# 18. Positions Contrac

每frame的positions必须：

* shape = `[atom_count, 3]
* finite
* numeric
* deterministic order
* no missing atom
* no extra atom
* no sparse representation
* no arbitrary typed binary blob in v1 JSON contrac

必须限制：

* coordinate magnitude
* total numeric values
* frame bytes

对于unwrapped轨迹，不能使用过窄coordinate bound，但必须防止非合理极值和overflow。

建议建立application-owned absolute guard，并记录理由。

---

# 19. Velocities Contrac

velocities为可选。

必须固定：

* shape = `[atom_count,3]
* Cartesian vectors
* canonical uni

推荐canonical unit：

```tex
angstrom_per_femtosecond


不得允许：

* fractional velocity而不标记
* frame间单位变化
* 与positions坐标模式混淆

如果输入来源是不同单位，后续parser负责转换，contract只保存canonical unit。

---

# 20. Forces Contrac

forces为可选。

必须固定：

* shape = `[atom_count,3]
* Cartesian vectors
* canonical uni

推荐：

```tex
electronvolt_per_angstrom


必须明确：

* force不是displacemen
* force不会由viewer直接应用为位置变化
* 不允许NaN/Infinity

---

# 21. Energy Contrac

需要区分：

* potential energy
* kinetic energy
* total energy
* free energy

不应只使用含糊的`energy`字段。

建议：

```json
{
  "energy": {
    "potential": -10.0,
    "kinetic": 1.5,
    "total": -8.5,
    "free": null,
    "unit": "electronvolt"
  }
}


也可以只支持第一版有限字段，但必须明确。

不得自动假设per-atom或total。

必须定义：

```tex
scope = total_system


未来per-atom energy另设字段。

---

# 22. Temperature Contrac

temperature为可选。

必须固定：

* unit = kelvin
* finite
* nonnegative，允许小容差
* 不允许viewer从velocities自行推断
* provenance必须说明来源

不得把单帧temperature视为必然严格热力学温度。

---

# 23. Stress Contrac

如第一版支持stress，必须固定：

* tensor shape
* component ordering
* sign convention
* uni

建议第一版可选择：

```tex
stress: DEFERRED_BY_DESIGN


因为不同软件：

* Voigt ordering不同
* 压力符号不同
* 单位不同

如实现，必须明确：

```tex
3×3 Cartesian symmetric tensor
unit = gigapascal
sign convention = tensile positive or compressive positive


不得使用未说明的6-vector。

---

# 24. Optional Per-Atom Properties

第一版只建议批准：

* velocities
* forces

不建议开放任意：

```tex
properties: Record<string, any>


如果必须支持扩展，使用严格extension命名空间：

```json
{
  "extensions": {
    "approved.namespace": {}
  }
}


并设：

* approved key lis
* key count cap
* value type cap
* byte cap

不得允许任意嵌套对象绕过contract。

---

# 25. Top-Level Metadata

允许有限metadata：

* title
* description
* source forma
* source software
* source version
* calculation type
* ensemble
* integrator
* timestep
* user-provided tags，若项目允许

必须：

* sanitized
* bounded
* iner
* no HTML
* no URL，除非项目provenance允许受控URL；本阶段建议禁止
* no executable conten
* no private path
* no secre

---

# 26. Provenance Contrac

至少包含：

```json
{
  "source_format": "extxyz",
  "source_software": "unknown",
  "source_version": null,
  "parser_version": null,
  "input_sha256": "...",
  "created_by_tool": null
}


本阶段尚未实现parser，因此：

* parser_version可为空
* source_format可来自fixture
* provenance schema必须先固定

不得包含：

* absolute local path
* token
* environment dump
* hostname
* username

---

# 27. Trajectory Summary Contrac

建议新增：

```tex
phase10g.trajectory_summary.v1


包含：

```json
{
  "schema_version": "phase10g.trajectory_summary.v1",
  "kind": "molecular_dynamics",
  "frames": 100,
  "atoms": 64,
  "coordinate_mode": "fractional",
  "position_wrapping": "wrapped",
  "lattice_mode": "fixed",
  "periodic_boundary": [true,true,true],
  "time_start": 0.0,
  "time_end": 99.0,
  "time_unit": "femtosecond",
  "available_properties": [
    "positions",
    "velocities",
    "temperature"
  ],
  "warnings": []
}


用途：

* JSON-only preview
* parser summary
* future planner/runtime
* over-budget fallback

不得复制完整frame数据。

---

# 28. Manifest Contrac

建议：

```tex
phase10g.trajectory_manifest.v1


至少包含：

* trajectory artifac
* summary artifac
* optional index artifac
* schema versions
* media types
* sizes
* hashes
* frame coun
* atom coun
* security markers

禁止包含：

* JS bundle
* remote frames
* external URL
* arbitrary media type
* executable assets

---

# 29. Caps and Budgets

必须以真实平台限制为依据建立application-owned caps。

至少定义：

* max atom coun
* max frame coun
* max total coordinate values
* max JSON bytes
* max metadata bytes
* max optional property arrays
* max property key coun
* max label length
* max warning coun
* max provenance fields
* max numeric magnitude

建议建立分层：

## Contract Hard Cap

超过直接invalid。

## Future Interactive Cap

用于Trajectory Viewer，但本阶段只定义建议值。

## Future Degraded Cap

用于后续viewer fallback。

不得在本阶段声称viewer performance READY。

必须使用overflow-safe乘法：

```tex
frames × atoms × components


在任何大规模allocation前检查。

---

# 30. Storage Strategy Decision

本阶段必须明确v1采用何种存储。

推荐：

## Contract Representation

```tex
JSON


用于：

* small/medium fixture
* validation
* evidence
* interoperability

但必须记录：

* 大型trajectory不适合完整JSON驻留
* Phase 10G-1 parser可能需要indexed/chunked artifac
* v1 JSON contract不代表未来viewer必须一次加载全部frame

建议为后续预留：

```tex
trajectory index artifac
frame chunk artifacts


但本阶段不得实现chunk runtime。

---

# 31. Deterministic Ordering

必须固定：

* top-level key serialization
* atom order
* frame order
* optional property order
* warning order
* manifest artifact order
* provenance key order
* enum representation

相同输入contract必须得到相同canonical JSON hash。

不得将：

* current time
* random UUID
* unordered map iteration
* environment-specific path

放入canonical payload。

如果需要trajectory_id，必须说明：

* content-derived
* caller-provided validated ID
* 或排除在deterministic hash之外

推荐使用content-derived identity。

---

# 32. Typed Errors and Warnings

至少定义：

```tex
TRAJECTORY_SCHEMA_UNSUPPORTED
TRAJECTORY_KIND_UNSUPPORTED
TRAJECTORY_EMPTY
TRAJECTORY_FRAME_LIMIT_EXCEEDED
TRAJECTORY_ATOM_LIMIT_EXCEEDED
TRAJECTORY_BYTE_LIMIT_EXCEEDED
TRAJECTORY_FRAME_INDEX_INVALID
TRAJECTORY_FRAME_INDEX_DUPLICATE
TRAJECTORY_FRAME_COUNT_MISMATCH
TRAJECTORY_ATOM_COUNT_MISMATCH
TRAJECTORY_SPECIES_MISMATCH
TRAJECTORY_COORDINATE_MODE_INVALID
TRAJECTORY_POSITION_WRAPPING_INVALID
TRAJECTORY_LATTICE_MODE_INVALID
TRAJECTORY_LATTICE_REQUIRED
TRAJECTORY_LATTICE_UNEXPECTED
TRAJECTORY_LATTICE_SINGULAR
TRAJECTORY_LATTICE_ILL_CONDITIONED
TRAJECTORY_TIME_UNIT_UNSUPPORTED
TRAJECTORY_TIME_NONMONOTONIC
TRAJECTORY_STEP_NONMONOTONIC
TRAJECTORY_POSITION_NONFINITE
TRAJECTORY_VELOCITY_NONFINITE
TRAJECTORY_FORCE_NONFINITE
TRAJECTORY_PROPERTY_SHAPE_INVALID
TRAJECTORY_PARTIAL_OCCUPANCY_UNSUPPORTED
TRAJECTORY_METADATA_LIMIT_EXCEEDED
TRAJECTORY_EXTERNAL_REFERENCE_FORBIDDEN


warnings建议：

```tex
TRAJECTORY_TIME_MISSING
TRAJECTORY_STEP_MISSING
TRAJECTORY_WRAPPING_UNKNOWN
TRAJECTORY_SOURCE_SOFTWARE_UNKNOWN
TRAJECTORY_OPTIONAL_PROPERTY_PARTIAL


必须固定warning排序。

错误必须：

* sanitized
* deterministic
* no stack
* no private path
* no raw frame dump
* no secre

---

# 33. Validation Rules

validator至少分为：

## Top-Level Validation

* schema
* kind
* coordinate mode
* wrapping
* lattice mode
* atom metadata
* time metadata
* properties
* provenance
* security

## Frame Validation

* frame index
* step/time
* lattice
* positions
* optional arrays
* scalar properties
* metadata

## Cross-Frame Validation

* atom count constan
* species constan
* frame index continuous
* step monotonic
* time monotonic
* lattice mode consisten
* coordinate mode consisten
* optional property consistency policy
* total caps

## Security Validation

* no executable fields
* no URLs
* no binary payloads
* no oversized strings
* no unbounded nested objects

---

# 34. Optional Property Consistency Policy

必须选择：

## Strict Consistency

如果top-level声明：

```tex
velocities = true


则每个frame必须都有velocities。

推荐第一版采用此策略。

不建议：

* 某些frame有、某些frame没有

除非显式：

```tex
availability = partial


但会增加viewer复杂度。

第一版建议：

* properties声明与所有frame严格一致
* 不允许partial arrays
* scalar properties可按明确policy允许partial，但优先保持stric

---

# 35. Reference Fixtures

新增small、deterministic fixtures。

至少包含：

## 35.1 Fixed-Lattice MD

* 2–4 atoms
* 3–5 frames
* fractional wrapped
* timestamps
* velocities

## 35.2 Variable-Lattice Relaxation

* Cartesian或fractional
* 3–5 frames
* per-frame lattice
* energy
* forces

## 35.3 Unwrapped Diffusion-Like Sequence

* fractional coordinates跨越cell
* wrapping = unwrapped
* stable atom identity

## 35.4 Nonperiodic Structure Sequence

仅当第一版支持nonperiodic。

## 35.5 Invalid Atom Coun

某frame少一个atom。

## 35.6 Invalid Species Reorder

atom count相同但species mapping变化。

## 35.7 Invalid Lattice

singular或ill-conditioned。

## 35.8 Invalid Time

nonmonotonic time。

## 35.9 Over-Cap Synthetic

使用test generator，不提交巨大JSON。

不得提交大型真实MD轨迹。

---

# 36. Independent Reference Tests

必须建立独立参考。

至少验证：

* fractional→Cartesian
* variable lattice conversion
* wrapped coordinate interpretation
* unwrapped coordinate preservation
* frame time monotonicity
* atom identity stability
* canonical serialization hash

优先：

* frontend/shared TypeScript validator
* backend Python reference validator

同一fixtures双实现对照。

不得用同一实现生成expected再验证自己。

---

# 37. Unit Tests

至少覆盖：

## Schema

* valid minimal
* valid full
* unknown field
* unsupported schema
* unsupported enum

## Atom Identity

* stable order
* count mismatch
* species mismatch
* reorder
* duplicate labels
* invalid atom ID

## Frames

* frame index continuous
* duplicate index
* missing index
* invalid shape
* empty trajectory

## Coordinates

* fractional
* Cartesian
* wrapped
* unwrapped
* nonfinite
* excessive magnitude

## Lattice

* fixed
* variable
* missing
* unexpected
* singular
* ill-conditioned
* triclinic

## Time

* MD valid time
* missing MD time
* optimization without time
* nonmonotonic
* unsupported uni
* step monotonicity

## Properties

* velocities
* forces
* energy
* temperature
* invalid shape
* inconsistent availability

## Caps

* frames
* atoms
* bytes
* metadata
* warning coun
* overflow multiplication

## Security

* JS-like field
* URL
* HTML
* callback-like field
* oversized nested metadata
* private path

---

# 38. Compatibility Policy

必须明确：

## Static Viewer Scene

* 不包含trajectory
* 不改变schema
* 可由未来Trajectory Viewer按frame派生静态display scene
* derived static scene不得反向成为trajectory权威

## Static Structure Inpu

* 可作为single-frame trajectory来源
* 但本阶段不自动转换
* single-frame trajectory是否允许必须固定

推荐：

```tex
minimum frame count = 1


但：

* kind为structure_sequence时允许1
* molecular_dynamics建议至少2

## Future Parser

Phase 10G-1必须输出本contract。

## Future Viewer

Phase 10G-2只消费validated trajectory contract或其chunked等价形式。

---

# 39. Security

必须验证：

* no artifact JavaScrip
* no artifact HTML
* no callback
* no shader
* no module
* no eval
* no Function constructor
* no external URL
* no remote frame reference
* no remote texture
* no CDN
* no iframe
* no arbitrary file access
* no notebook execution
* no script execution
* no real LLM
* no unbounded frames
* no unbounded atoms
* no integer overflow
* no compressed payload bypass
* no metadata recursion abuse
* no parser execution
* no private path
* no secre
* no telemetry upload

必须输出：

```tex
NO_EXTERNAL_NETWORK_REQUESTS
NO_SECRET_PATTERN_HITS


---

# 40. Evidence

新增：

```tex
docs/phase10g/evidence/phase10g_trajectory_contract/


至少包含：

```tex
README.md
trajectory_schema.json
trajectory_frame_schema.json
trajectory_manifest_schema.json
trajectory_summary_schema.json
enum_policy.json
atom_identity_policy.json
coordinate_policy.json
lattice_policy.json
time_unit_policy.json
optional_property_policy.json
caps.json
fixed_lattice_fixture_result.json
variable_lattice_fixture_result.json
unwrapped_fixture_result.json
invalid_cases.json
frontend_backend_validation_comparison.json
deterministic_serialization.json
security_audit.json
network_audit.json
artifact_hashes.json


不得保存：

* 大型trajectory
* cache
* private path
* token
* secre
* remote URL
* notebook outpu
* parser traces
* crash dump

---

# 41. Documentation

新增或更新：

```tex
docs/phase10g/phase10g_trajectory_contract.md
docs/phase10g/phase10g_trajectory_schema.md
docs/phase10g/phase10g_trajectory_frame_identity.md
docs/phase10g/phase10g_trajectory_coordinate_and_lattice_policy.md
docs/phase10g/phase10g_trajectory_units.md
docs/phase10g/phase10g_trajectory_caps.md
docs/phase10g/phase10g_trajectory_security.md
docs/phase10g/phase10g_trajectory_evidence.md
docs/phase10g/phase10g_trajectory_readiness_matrix.md


更新：

```tex
docs/index.md
docs/13_SHARED_SCHEMA_SPEC.md
persistent/DESIGN_PROGRESS.md
persistent/TASK_BOARD.md
persistent/CHANGELOG.md
persistent/OPEN_QUESTIONS.md
persistent/TOOL_REGISTRY_NOTES.md
persistent/ARCHITECTURE_DECISIONS.md


必须记录：

* schema family
* atom identity
* frame identity
* lattice convention
* coordinate modes
* wrapping policy
* time policy
* units
* optional properties
* caps
* storage decision
* chunking deferred
* parser deferred
* viewer deferred
* registration deferred

---

# 42. Readiness Matrix

最终分别判断：

* trajectory top-level schema
* frame schema
* manifest schema
* summary schema
* atom identity
* frame identity
* species stability
* coordinate mode
* wrapping policy
* fixed lattice
* variable lattice
* periodic boundary
* time units
* step policy
* positions
* velocities
* forces
* energy
* temperature
* stress
* optional properties
* metadata
* provenance
* caps
* deterministic serialization
* validator
* fixtures
* reference comparison
* security
* parser
* adapter
* viewer
* performance/browser evidence
* formal tool registration

推荐期望：

```tex
trajectory schema: READY
frame schema: READY
manifest schema: READY
summary schema: READY
atom identity: READY
frame identity: READY
coordinate policy: READY
wrapping policy: READY
fixed lattice: READY
variable lattice: READY
time/unit policy: READY
positions: READY
velocities: READY
forces: READY
energy: READY
temperature: READY
stress: READY or DEFERRED_BY_DESIGN
caps: READY
deterministic serialization: READY
validator: READY
fixtures: READY
reference comparison: READY
security: READY

trajectory parser: NOT_READY
trajectory adapter: NOT_READY
trajectory viewer: NOT_READY
trajectory performance evidence: NOT_READY
formal trajectory tool registration: NOT_READY


不得因为contract完成就将trajectory product标记READY。

---

# 43. Checks

至少运行：

```bash
git diff --check
uv lock --check

uv run python -m pytest -q

npm --prefix apps/web tes
npm --prefix apps/web run typecheck
npm --prefix apps/web run build


并运行：

* trajectory schema tests
* trajectory frame tests
* atom identity tests
* coordinate/lattice tests
* time/unit tests
* property tests
* cap/overflow tests
* deterministic serialization tests
* frontend/backend comparison
* artifact validator tests
* security scan
* network audi
* Phase 10 closure regression pack
* service-backed integration
* no-skipped assertion

本阶段不要求trajectory browser evidence，因为尚未实现viewer。

必须如实记录：

* passed
* failed
* skipped
* unavailable

不得把skipped写成passed。

---

# 44. Commit / CI

完成contract、validator、tests、evidence和docs后：

```bash
git status --shor
git diff --sta
git add <only Phase 10G related files>
git commit -m "Define trajectory data contract"
git push origin master


等待current HEAD CI。

必须确认：

* backend unit success
* frontend tests success
* frontend typecheck success
* frontend build success
* Phase 10 closure regression success
* service-backed integration success
* no-skipped assertion success
* origin/master matches HEAD
* git status clean

不得伪造CI结果。

---

# 45. 最终报告格式

完成后输出：

# Phase 10G Trajectory Contract Resul

## 1. Conclusion

PASS / PARTIAL_PASS / FAIL

## 2. Baseline

* Phase 10 Closure assumed complete:
* branch:
* initial status:
* final HEAD:
* final status:

## 3. Schema Family

* trajectory:
* frame:
* summary:
* manifest:
* current versions:

## 4. Trajectory Semantics

* supported kinds:
* minimum frames:
* atom count policy:
* species policy:
* atom identity:
* frame identity:
* ordering:

## 5. Coordinate Policy

* coordinate modes:
* canonical Cartesian unit:
* wrapped:
* unwrapped:
* unknown wrapping:
* conversion convention:

## 6. Lattice Policy

* lattice convention:
* fixed lattice:
* variable lattice:
* determinant threshold:
* condition threshold:
* triclinic:
* periodic boundary:

## 7. Time and Step

* frame index:
* simulation step:
* physical time:
* supported units:
* canonical unit:
* monotonicity:

## 8. Properties

* positions:
* velocities:
* forces:
* energy:
* temperature:
* stress:
* partial availability:
* extension policy:

## 9. Caps

* max atoms:
* max frames:
* max numeric values:
* max bytes:
* metadata:
* warning count:
* overflow protection:

## 10. Validation

* top-level:
* frame:
* cross-frame:
* atom identity:
* lattice:
* time:
* optional properties:
* security:

## 11. Determinism

* atom order:
* frame order:
* property order:
* warning order:
* manifest order:
* canonical hash:
* trajectory identity:

## 12. Fixtures

* fixed lattice:
* variable lattice:
* unwrapped:
* invalid atom count:
* species reorder:
* invalid lattice:
* invalid time:
* over-cap:

## 13. Reference Comparison

* frontend:
* backend:
* coordinate conversion:
* variable lattice:
* identity:
* hashes:
* differences:

## 14. Security

* executable content:
* external references:
* metadata abuse:
* overflow:
* caps:
* private paths:
* secrets:
* network:
* markers:

## 15. Evidence

* directory:
* schemas:
* policies:
* fixtures:
* validation comparison:
* deterministic serialization:
* security:
* hashes:

## 16. Tests

* schemas:
* frames:
* identity:
* coordinates:
* lattice:
* time:
* properties:
* caps:
* security:
* backend full:
* frontend full:
* typecheck:
* build:
* Phase 10 closure:
* service-backed:
* no-skipped:
* lock:
* diff:

## 17. Files

* schemas/models:
* validators:
* serializers:
* fixtures:
* backend tests:
* frontend/shared tests:
* evidence:
* docs:
* persistent:
* dependencies/lockfile:

## 18. Deferred

明确列出：

* XYZ/extxyz parser
* ASE trajectory parser
* LAMMPS parser
* chunked storage
* frame index artifac
* trajectory adapter
* trajectory viewer
* playback
* interpolation
* dynamic bonds
* trajectory expor
* ensemble RDF
* MSD
* diffusion
* VACF
* trajectory editing
* variable atom coun
* reactive trajectories
* partial occupancy
* stress，若未实现
* formal trajectory tool registration

## 19. Readiness

* contract:
* validator:
* identity:
* coordinates:
* lattice:
* time:
* properties:
* caps:
* determinism:
* fixtures:
* security:
* parser:
* adapter:
* viewer:
* browser:
* formal product:

## 20. Commit / CI

* commit:
* HEAD:
* CI run:
* backend:
* frontend:
* typecheck:
* build:
* Phase 10 closure:
* service-backed:
* no-skipped:
* origin:
* status:

## 21. Whether allowed to enter next phase

允许 / 不允许

下一阶段：

```tex
Phase 10G-1：Trajectory Parser / Adapter


下一阶段只实现批准的trajectory输入parser、normalization、adapter、artifact emission和API evidence基础，不直接实现trajectory playback viewer。

---

# 46. PASS 判定

PASS必须满足：

* 有真实trajectory schema实现
* 有真实frame schema实现
* 有validator实现
* atom identity明确
* frame identity明确
* frame间atom count固定
* frame间species稳定
* coordinate mode固定
* wrapped/unwrapped语义固定
* fixed/variable lattice语义固定
* lattice convention复用Phase 10标准
* time/step语义固定
* units固定
* positions shape验证
* velocities/forces policy明确
* energy scope明确
* optional property一致性明确
* caps明确
* overflow protection完成
* deterministic serialization完成
* manifest和summary contract完成
* fixtures完整
* frontend/backend reference comparison完成
* no external references
* no executable conten
* no secret hits
* Phase 10 closure regression不回退
* tests通过
* CI通过
* git clean

PARTIAL_PASS仅允许：

* stress明确DEFERRED_BY_DESIGN
* partial periodicity明确deferred
* nonperiodic trajectory明确deferred
* frontend validator暂不实现，但backend contract和独立reference完整
* npm audit因既有registry问题不可用

FAIL包括：

* 只有docs，没有validator
* trajectory直接复用static viewer scene作为容器
* atom identity依赖模糊坐标匹配
* frame间atom count变化被静默接受
* frame间species reorder被静默接受
* 坐标模式混用
* lattice语义不明确
* wrapped/unwrapped不明确
* units不明确
* 无caps
* 先分配后检查cap
* 允许NaN/Infinity
* 允许外部frame URL
* 允许任意metadata绕过限制
* 提前实现viewer/playback导致范围膨胀
* Phase 10 closure tests回退
* CI失败却声明PASS

---END---

---TASK---
 状态：待处理
 # Phase 10G-1：Trajectory Parser / Adapter

进入 Phase 10G-1：Trajectory Parser / Adapter。

可以默认：

-   Phase 10G：Trajectory Contract 已完成并通过

-   `phase10g.trajectory.v1

-   `phase10g.trajectory_frame.v1

-   `phase10g.trajectory_summary.v1

-   `phase10g.trajectory_manifest.v1

-   atom identity、frame identity、coordinate mode、wrapping、lattice mode、time/unit policy、caps、deterministic serialization和security contract均已固定

-   Phase 10 Closure Regression Pack保持通过

-   static viewer、`structure.viewer_3d`和Phase 10F产品路径保持稳定

-   当前branch、HEAD、working tree和Phase 10G CI可视为正确且clean


本阶段不需要重复Phase 10G baseline检查。

本阶段的主要任务是：

> 为已批准的trajectory contract实现安全、bounded、deterministic的输入解析和正式adapter路径，将受支持的trajectory文件或结构序列规范化为`phase10g.trajectory.v1`、summary和manifest artifacts，并完成API evidence基础。

本阶段只完成：

-   parser architecture

-   approved format parsing

-   normalization

-   units conversion

-   atom/frame identity validation

-   bounded ingestion

-   trajectory adapter

-   artifact emission

-   registry/planner内部准备或受限注册

-   API evidence

-   parser security

-   tests和docs


本阶段不实现trajectory viewer、不实现播放动画、不实现dynamic bonds。

----------

# 1. 本阶段定位

Phase 10G-1是trajectory ingestion和normalization阶段。

它必须解决：

-   哪些文件格式在第一版正式支持

-   parser如何识别输入

-   parser如何防止大型文件和恶意输入

-   不同来源如何映射到统一trajectory contrac

-   单位如何转换

-   lattice、PBC、positions、velocities、forces如何提取

-   atom identity如何保持

-   malformed trajectory如何拒绝

-   parser结果如何进入runtime和artifact体系

-   summary/manifest如何生成

-   API如何返回typed resul


本阶段不是：

-   trajectory viewer

-   trajectory playback

-   trajectory analysis

-   MD simulation

-   trajectory editing

-   dynamic bond inference

-   trajectory product registration最终阶段


----------

# 2. 本阶段目标

必须完成以下十类工作：

1.  **Parser architecture audit**

2.  **Approved input format scope**

3.  **Safe streaming/bounded parsing**

4.  **Normalization into trajectory contract**

5.  **Unit、lattice、PBC和identity mapping**

6.  **Trajectory adapter and artifact emission**

7.  **Registry / Planner / API integration基础**

8.  **Fixtures、tests和reference comparison**

9.  **Security and resource closure**

10.  **Docs、evidence和readiness closure**


本阶段必须产生真实parser和adapter实现。

如果最终只有parser计划、fixture、schema mapping文档或adapter stub，没有真实输入→artifact路径，本阶段必须判定为FAIL。

----------

# 3. 第一版支持格式

第一版建议正式支持：

```tex
Extended XYZ / extxyz
Native trajectory JSON



可选支持：

```tex
plain XYZ



但必须明确其能力受限。

本阶段默认不支持：

-   ASE `.traj

-   LAMMPS dump

-   XTC

-   TRR

-   DCD

-   NetCDF

-   HDF5

-   XDATCAR

-   vasprun.xml

-   PDB trajectory

-   remote URL

-   compressed archive

-   notebook objec

-   pickled Python objec


这些格式必须留到后续独立parser phase或明确扩展。

----------

# 4. 严格禁止范围

本阶段不得实现：

-   trajectory viewer

-   playback

-   frame slider

-   animation loop

-   atom interpolation

-   dynamic bond inference

-   per-frame neighbor guessing

-   trajectory editing

-   structure mutation

-   frame mutation

-   trajectory expor

-   chunked viewer runtime

-   ensemble RDF

-   MSD

-   diffusion

-   VACF

-   phonon animation

-   external API

-   notebook execution

-   script execution

-   real LLM

-   arbitrary plugin parser

-   arbitrary Python impor

-   pickle/deserialization


不得：

-   修改Phase 10G contract语义

-   修改static `viewer_scene.v2

-   将trajectory塞入`structure.viewer_3d

-   静默重新排序atoms

-   静默匹配species

-   静默补frame

-   静默丢frame

-   静默wrap或unwrap

-   静默改变lattice

-   静默推断缺失time为真实物理时间

-   静默转换未知单位

-   允许remote reference

-   允许archive bomb

-   允许压缩payload绕过caps

-   允许parser执行输入代码

-   允许无限metadata

-   允许超大文件先读入内存再拒绝

-   允许格式探测读取整个文件

-   允许artifact JavaScrip

-   允许外部URL

-   允许任意MIME

-   允许任意扩展名决定parser而不做内容验证


允许：

-   bounded parser

-   streaming line reader

-   safe format detection

-   unit normalization

-   schema validation

-   adapter

-   manifes

-   summary

-   tests

-   API evidence

-   docs


----------

# 5. 必读实现

开始后直接阅读当前真实代码。

## 5.1 Trajectory Contrac

阅读Phase 10G新增：

-   trajectory schema

-   frame schema

-   summary schema

-   manifest schema

-   validator

-   canonical serializer

-   caps

-   typed errors

-   fixtures

-   reference tests


必须直接复用，不建立第二套trajectory模型。

## 5.2 Existing Parser Patterns

搜索：

```bash
rg -n "parse.*file|upload|multipart|mime|extension|stream|readline|artifact input|parser" backend packages tests



确认：

-   current upload handling

-   file byte caps

-   MIME detection

-   extension allowlis

-   streaming helpers

-   temporary file policy

-   parser error model

-   artifact storage

-   input hash

-   cleanup


## 5.3 Existing Structure Parsers

搜索：

```bash
rg -n "CIF|POSCAR|XYZ|extxyz|structure parser|pymatgen|ase" backend packages tests



确认：

-   当前是否已有structure parser

-   pymatgen或ASE是否已经是依赖

-   是否已有extxyz支持

-   是否已有safe parser wrapper

-   dependency policy


## 5.4 Tool / Adapter Patterns

检查：

-   adapter base class

-   registry registration

-   input artifact selection

-   output artifacts

-   manifest generation

-   summary generation

-   provenance

-   API evidence

-   service-backed runtime


----------

# 6. 修改前输出审计

修改代码前输出：

# Phase 10G-1 Trajectory Parser / Adapter Pre-Implementation Audi

## 1. Current Parser Infrastructure

-   upload path:

-   byte caps:

-   MIME handling:

-   extension handling:

-   streaming:

-   temp files:

-   cleanup:

-   hash:

-   parser errors:

-   reusable helpers:


## 2. Existing Dependencies

-   pymatgen:

-   ASE:

-   extxyz support:

-   structure parser:

-   lockfile impact:

-   licensing:

-   existing approved use:


## 3. Format Scope

对每个候选格式说明：

-   extxyz:

-   native JSON:

-   plain XYZ:

-   ASE trajectory:

-   LAMMPS dump:

-   XDATCAR:


每项列出：

-   support decision

-   reason

-   metadata quality

-   lattice suppor

-   PBC suppor

-   velocities/forces suppor

-   unit ambiguity

-   security risk


## 4. Mapping Risks

至少列出：

-   species reorder

-   atom count drif

-   lattice omission

-   extxyz property descriptor mismatch

-   unknown units

-   wrapped/unwrapped ambiguity

-   time extraction ambiguity

-   malformed frame boundary

-   truncated file

-   enormous comment line

-   metadata recursion

-   invalid UTF-8

-   duplicate property names

-   unsupported property types

-   plain XYZ missing lattice

-   parser dependency behavior

-   whole-file memory use


## 5. Selected Strategy

说明：

-   format detection:

-   extxyz parser:

-   native JSON parser:

-   plain XYZ policy:

-   unit conversion:

-   identity:

-   bounded reading:

-   error handling:

-   adapter:

-   artifacts:

-   API:


## 6. Planned Files

列出：

-   parser module

-   format detector

-   normalizer

-   adapter

-   registry metadata

-   tests

-   fixtures

-   API tests

-   evidence

-   docs

-   persisten


审计后直接继续实现。

----------

# 7. Parser Architecture

建议建立：

```tex
input bytes/file
→ safe format detector
→ format-specific parser
→ raw parsed frames
→ normalization
→ trajectory validator
→ canonical serializer
→ summary
→ manifes
→ artifact emission



必须严格分层。

不得：

-   parser直接生成前端viewer对象

-   parser绕过trajectory validator

-   parser直接写artifact store而不经过adapter

-   parser把library对象泄漏进artifac

-   parser结果携带callback或自定义class


----------

# 8. Safe Format Detection

格式检测必须综合：

-   allowlisted extension

-   allowlisted MIME，若可靠

-   bounded content sniffing

-   schema marker


推荐规则：

## Native JSON

-   `.json

-   top-level `schema_version

-   必须为批准的trajectory schema或批准的raw import schema


## Extended XYZ

-   `.xyz`或`.extxyz

-   第一行可解析为nonnegative atom coun

-   第二行包含可识别extxyz metadata或允许plain XYZ fallback


不得：

-   只看扩展名

-   读整个文件做检测

-   执行magic内容

-   fallback到任意parser


未知格式返回：

```tex
TRAJECTORY_FORMAT_UNSUPPORTED



----------

# 9. Extended XYZ Parser

## 9.1 第一行

必须解析：

```tex
atom_coun



要求：

-   integer

-   positive

-   不超过contract cap

-   每frame一致

-   no trailing executable syntax


## 9.2 第二行 Metadata

extxyz通常包含：

-   `Lattice

-   `Properties

-   `pbc

-   `Time

-   `energy

-   其他key/value


必须实现受控parser。

不得：

-   使用`eval

-   使用shell-like parser执行命令

-   使用Python literal eval

-   允许无限key

-   允许无限value长度

-   允许嵌套对象


必须限制：

-   metadata key coun

-   key length

-   value length

-   comment line bytes


## 9.3 Properties Descriptor

必须解析类似：

```tex
Properties=species:S:1:pos:R:3



批准字段建议：

-   species

-   pos

-   positions

-   vel

-   velocity

-   velocities

-   force

-   forces

-   id

-   atom_id


必须映射为canonical字段。

未知字段：

-   默认忽略并记录bounded warning

-   或进入approved extension namespace

-   不得任意写入frame metadata


descriptor必须验证：

-   name

-   type

-   component coun

-   duplicate names

-   required species/position fields

-   row token coun


## 9.4 Lattice

从`Lattice`读取9个finite numeric values。

必须：

-   按项目row-vector convention映射

-   unit默认angstrom仅在extxyz约定明确且项目批准时使用

-   validator再次检查determinant/condition


缺失lattice：

-   对periodic trajectory拒绝

-   对nonperiodic plain sequence可按policy允许


## 9.5 PBC

解析：

```tex
pbc="T T T"



或批准的等价形式。

必须映射到：

```json
[true,true,true]



不得从lattice存在自动猜测PBC。

## 9.6 Atom Rows

每行必须：

-   token数量匹配descriptor

-   species合法

-   positions finite

-   optional vectors shape正确

-   no extra unbounded columns

-   no row-level metadata injection


## 9.7 Frame Boundary

每frame必须完整。

遇到：

-   premature EOF

-   missing atom row

-   extra row

-   next frame malformed


必须typed failure，不得返回partial success，除非项目明确支持partial import；本阶段建议不支持。

----------

# 10. Plain XYZ Policy

plain XYZ通常只有：

-   atom coun

-   commen

-   species + Cartesian coordinates


因此第一版只能映射为：

```tex
kind = structure_sequence
coordinate_mode = cartesian
lattice_mode = absent/nonperiodic
periodic_boundary = [false,false,false]
position_wrapping = unknown



只有当Phase 10G contract明确支持nonperiodic trajectory时才允许。

如果Phase 10G第一版只支持有lattice轨迹：

```tex
plain XYZ: DEFERRED_BY_DESIGN



不得伪造lattice。

不得根据bounding box自动构造cell。

----------

# 11. Native JSON Parser

Native JSON必须分为两类：

## 11.1 Canonical Trajectory JSON

如果输入已经是：

```tex
phase10g.trajectory.v1



则：

-   parse

-   validate

-   canonicalize

-   hash

-   emi


不得重新解释或改变语义。

## 11.2 Approved Raw Import JSON

如果需要支持简化raw JSON，必须定义独立schema，例如：

```tex
phase10g.trajectory_import.v1



不得接受任意JSON结构后“尽力猜测”。

推荐第一版仅支持canonical JSON，减少歧义。

----------

# 12. Atom Identity Mapping

## 12.1 extxyz有ID字段

如果descriptor包含：

```tex
id:I:1



必须：

-   validate integer ID

-   frame内唯一

-   frame间集合一致

-   映射到stable atom order


但不能静默重排后掩盖输入变化。

必须选择明确策略：

### Strategy A

首帧ID顺序成为canonical order，后续按ID重排。

允许条件：

-   ID完整

-   ID唯一

-   species与ID稳定

-   必须记录`source_atom_ids


### Strategy B

要求每frame原始顺序一致，不重排。

推荐更稳妥的第一版：

```tex
有stable ID时允许按首帧ID建立canonical order，但必须显式记录reordering和source IDs。



没有ID时：

-   只能依赖row order

-   row order变化不可检测

-   必须记录identity confidence/policy


## 12.2 Species Stability

对每个canonical atom：

-   species必须跨frame一致

-   不允许mutation

-   不允许reorder导致species错配


失败：

```tex
TRAJECTORY_SPECIES_MISMATCH



----------

# 13. Coordinate Normalization

所有parser输出必须符合Phase 10G contract。

## extxyz positions

通常为Cartesian。

规范化为：

```tex
coordinate_mode = cartesian
unit = angstrom



除非文件明确、批准地声明fractional。

第一版不建议支持extxyz fractional position别名，除非已有可靠约定。

## Native JSON

保持contract指定mode。

不得：

-   因viewer偏好转换为fractional

-   因lattice存在自动转换

-   在parser阶段wrap positions


如果确需canonical内部mode，必须严格按Phase 10G contract执行并保留source metadata。

----------

# 14. Wrapping Policy Mapping

extxyz通常不可靠声明wrapped/unwrapped。

必须：

-   若approved metadata明确提供，则解析

-   否则：


```tex
position_wrapping = unknown



不得通过坐标是否超出cell猜测unwrapped。

后续viewer可以显示，但连续位移分析不得在unknown状态下执行。

----------

# 15. Time Mapping

支持来源字段建议：

-   `Time

-   `time

-

-   `step

-   `Step


但必须有allowlist和优先级。

必须明确：

-   time和step不混淆

-   time单位必须来自批准metadata或adapter option

-   缺失单位时不得假设fs，除非格式规范或用户显式参数批准

-   geometry optimization允许无physical time


如果用户通过adapter options指定unit：

-   必须strict enum

-   artifact记录该override

-   不允许任意unit string


----------

# 16. Unit Conversion

必须建立approved unit conversion表。

至少可能包括：

## Position

-   angstrom

-   nanometer，若批准

-   bohr，若批准


canonical：

```tex
angstrom



## Time

-   femtosecond

-   picosecond


canonical：

```tex
femtosecond



## Velocity

-   angstrom/fs

-   angstrom/ps

-   nm/ps，若批准


canonical：

```tex
angstrom_per_femtosecond



## Force

-   eV/angstrom

-   hartree/bohr，若批准


canonical：

```tex
electronvolt_per_angstrom



## Energy

-   eV

-   hartree，若批准


canonical：

```tex
electronvol



不得：

-   接受模糊缩写而无测试

-   自动猜测

-   使用locale number parsing

-   产生NaN/Infinity


所有conversion必须有reference tests。

----------

# 17. Lattice Mapping

## extxyz

`Lattice`必须按9值映射。

必须核对extxyz convention与项目row-vector convention。

如果来源是column-major或格式说明不同，必须显式转换。

不得凭记忆实现。

必须建立fixture：

-   orthogonal

-   triclinic

-   variable cell


验证：

-   fractional/cartesian conversion reference

-   determinan

-   condition


## variable lattice

每frame有不同Lattice时：

```tex
lattice_mode = variable



如果所有frame完全相同：

可选择：

-   normalize为fixed

-   或保留variable


必须固定策略。

推荐：

```tex
如果所有frame lattice在严格canonical tolerance内相同，normalize为fixed。



但必须：

-   deterministic

-   tolerance application-owned

-   evidence记录


如果不想引入歧义，保留source mode也可以，但必须固定。

----------

# 18. Optional Properties Mapping

第一版支持：

-   velocities

-   forces

-   energy

-   temperature


## Per-Atom

-   velocities

-   forces


必须所有frame一致存在。

## Per-Frame

-   energy

-   temperature

-   step

-   time


必须按contract consistency policy处理。

如果某些frame缺失：

推荐第一版：

-   整个property标记不可用

-   或拒绝输入


为了contract严格，优先：

```tex
declared property must exist in every frame



不得生成partial arrays。

----------

# 19. Energy Mapping

必须区分：

-   total energy

-   potential energy

-   kinetic energy

-   free energy


approved metadata aliases必须有限。

例如：

```tex
energy → potential or total



不能模糊映射。

如果格式只写`energy`且语义不明确：

-   保存为approved generic source field不进入canonical energy

-   或要求adapter option指定scope

-   推荐typed warning而非擅自归类


----------

# 20. Parser Caps

必须在读取过程中执行，而不是结束后。

至少限制：

-   input bytes

-   line bytes

-   comment bytes

-   atom coun

-   frame coun

-   tokens per atom row

-   metadata keys

-   metadata value bytes

-   numeric values

-   total parsed coordinate values

-   warning coun

-   output JSON bytes


必须实现overflow-safe：

```tex
frame_count × atom_count × fields



达到hard cap时立即停止解析并失败。

不得：

-   先读取整个文件

-   先split整个文件

-   先构建全部Python对象后检查

-   将超限内容写入错误消息


----------

# 21. Streaming Strategy

extxyz优先使用：

-   file-like iterator

-   buffered line reading

-   bounded line length

-   incremental frame parse


Native canonical JSON如果继续使用标准JSON parser，必须：

-   输入byte cap先检查

-   不接受超大JSON

-   不接受深度过高

-   不接受重复危险key，若框架可控制


本阶段不要求真正chunked artifact输出，但parser内部不得无界。

----------

# 22. Invalid UTF-8 and Encoding

第一版建议：

```tex
UTF-8 only



遇到invalid UTF-8：

```tex
TRAJECTORY_TEXT_ENCODING_INVALID



不得：

-   自动使用系统编码

-   locale-dependent fallback

-   忽略错误字节

-   将二进制误解析为文本


BOM处理策略必须固定。

----------

# 23. Adapter Contrac

建议正式或内部工具ID：

```tex
structure.trajectory_impor



或符合项目命名规范的等价ID。

本阶段必须审计是否应正式user-facing注册。

推荐状态：

```tex
registered internally / planner-hidden



直到Phase 10G-2 Viewer完成后再正式产品化。

Adapter输入：

-   uploaded trajectory artifac

-   format hint，可选且受allowlis

-   unit overrides，可选且受allowlis

-   trajectory kind，可选且受allowlis


Adapter输出：

-   canonical trajectory JSON

-   summary JSON

-   manifest JSON

-   parser report JSON

-   warnings


不得输出：

-   viewer scene

-   renderer bundle

-   HTML

-   JS

-   remote assets


----------

# 24. Parser Report Artifac

建议新增：

```tex
phase10g.trajectory_parse_report.v1



包含：

```json
{
  "schema_version": "phase10g.trajectory_parse_report.v1",
  "detected_format": "extxyz",
  "frames_read": 10,
  "atoms_per_frame": 64,
  "lattice_mode": "fixed",
  "coordinate_mode": "cartesian",
  "properties_detected": ["positions", "velocities"],
  "unit_conversions": [],
  "reordered_by_atom_id": false,
  "warnings": [],
  "input_sha256": "...",
  "deterministic": true
}



不得包含：

-   raw file conten

-   absolute path

-   full metadata dump

-   private environmen

-   stack trace


----------

# 25. Manifes

使用Phase 10G manifest contract。

至少列出：

```tex
trajectory.json
trajectory_summary.json
trajectory_parse_report.json
trajectory_manifest.json



每项包含：

-   media type

-   schema version

-   byte size

-   sha256

-   security marker


artifact order固定。

不得包含：

-   source file副本，除非现有artifact policy明确批准

-   executable file

-   external URL


----------

# 26. Provenance

必须记录：

-   source forma

-   parser name

-   parser version

-   adapter version

-   input hash

-   unit overrides

-   atom-ID reorder policy

-   normalization decisions

-   warnings


不得记录：

-   absolute source path

-   username

-   hostname

-   token

-   temporary directory


----------

# 27. Typed Errors and Warnings

除Phase 10G contract errors外，新增parser errors：

```tex
TRAJECTORY_FORMAT_UNSUPPORTED
TRAJECTORY_FORMAT_DETECTION_AMBIGUOUS
TRAJECTORY_INPUT_TOO_LARGE
TRAJECTORY_TEXT_ENCODING_INVALID
TRAJECTORY_LINE_TOO_LONG
TRAJECTORY_FRAME_TRUNCATED
TRAJECTORY_FRAME_HEADER_INVALID
TRAJECTORY_COMMENT_METADATA_INVALID
TRAJECTORY_PROPERTIES_DESCRIPTOR_INVALID
TRAJECTORY_PROPERTY_DUPLICATE
TRAJECTORY_ATOM_ROW_INVALID
TRAJECTORY_ATOM_ID_INVALID
TRAJECTORY_ATOM_ID_DUPLICATE
TRAJECTORY_ATOM_ID_SET_MISMATCH
TRAJECTORY_UNIT_UNKNOWN
TRAJECTORY_UNIT_OVERRIDE_INVALID
TRAJECTORY_PBC_INVALID
TRAJECTORY_LATTICE_METADATA_INVALID
TRAJECTORY_TIME_METADATA_INVALID
TRAJECTORY_ENERGY_SCOPE_AMBIGUOUS
TRAJECTORY_PARSE_CANCELLED



warnings：

```tex
TRAJECTORY_PLAIN_XYZ_NONPERIODIC
TRAJECTORY_WRAPPING_UNKNOWN
TRAJECTORY_TIME_UNIT_ASSUMED
TRAJECTORY_UNKNOWN_PROPERTY_IGNORED
TRAJECTORY_ATOMS_REORDERED_BY_ID
TRAJECTORY_IDENTICAL_VARIABLE_LATTICE_NORMALIZED
TRAJECTORY_ENERGY_FIELD_IGNORED_AMBIGUOUS



`TIME_UNIT_ASSUMED`仅在项目明确批准默认值时允许；否则应失败或缺失。

----------

# 28. Cancellation and Runtime Safety

parser必须支持：

-   request cancellation

-   job cancellation

-   timeou

-   temp resource cleanup

-   stale result rejection


如果runtime已有generation/cancellation token，必须复用。

取消后：

-   不写partial artifacts

-   不保留temp file

-   不返回success

-   不泄漏file handle


----------

# 29. Fixtures

新增small、deterministic parser fixtures。

至少包括：

## Valid extxyz

-   fixed lattice

-   variable lattice

-   triclinic

-   velocities

-   forces

-   stable atom IDs

-   reordered rows with IDs

-   geometry optimization metadata


## Valid Native JSON

-   canonical trajectory

-   minimal

-   full optional properties


## Invalid

-   truncated frame

-   wrong atom coun

-   duplicate atom ID

-   ID set mismatch

-   species mismatch

-   invalid lattice

-   invalid Properties descriptor

-   line too long

-   unknown uni

-   nonmonotonic time

-   invalid UTF-8

-   over-cap generated inpu


不得提交大型trajectory。

----------

# 30. Reference Comparison

必须建立独立reference。

至少对同一extxyz fixture比较：

-   parser output atom coun

-   frame coun

-   species

-   lattice

-   positions

-   velocities

-   forces

-   time

-   units

-   atom reorder mapping


如果仓库已有ASE且已批准，可使用ASE作为test-only参考，但不得让同一library同时作为唯一生产parser和唯一expected来源。

更稳妥：

-   production parser

-   independent fixture expectation或第二解析路径

-   Python/TypeScript normalization comparison


----------

# 31. Unit Tests

至少覆盖：

## Detection

-   extxyz

-   canonical JSON

-   unsupported

-   ambiguous

-   misleading extension


## extxyz Header

-   valid atom coun

-   zero

-   negative

-   floa

-   over-cap


## Metadata

-   valid Lattice

-   valid Properties

-   valid PBC

-   malformed quoting

-   duplicate keys

-   oversized commen


## Atom Rows

-   valid

-   missing token

-   extra token

-   invalid species

-   nonfinite numeric

-   invalid ID


## Identity

-   row order stable

-   ID reorder

-   duplicate ID

-   missing ID

-   species mismatch

-   ID set mismatch


## Units

-   position

-   velocity

-   force

-   energy

-   time

-   unsupported


## Lattice

-   fixed

-   variable

-   triclinic

-   singular

-   ill-conditioned

-   missing periodic lattice


## Consistency

-   frame coun

-   atom coun

-   property consistency

-   time monotonic

-   step monotonic


## Caps

-   bytes

-   lines

-   frames

-   atoms

-   metadata

-   numeric coun

-   output bytes

-   overflow


## Security

-   code-like metadata

-   URL

-   HTML

-   callback-looking keys

-   private path

-   invalid encoding


----------

# 32. Adapter Tests

覆盖：

-   input artifact accepted

-   parser selected

-   normalized trajectory emitted

-   summary emitted

-   report emitted

-   manifest emitted

-   schemas validated

-   hashes stable

-   warnings stable

-   invalid input typed failure

-   cancellation

-   no partial artifacts

-   deterministic replay


----------

# 33. API Evidence基础

本阶段必须有API evidence，但不要求viewer browser evidence。

至少通过正式service-backed路径覆盖：

## Valid extxyz

```tex
upload/impor
→ plan or direct approved tool reques
→ runtime
→ parser adapter
→ artifacts



## Valid Native JSON

-   canonical pass-through

-   canonicalization

-   stable hash


## Invalid Inpu

-   typed failure

-   sanitized error

-   no partial artifac


## Over-Cap

-   rejected before full allocation

-   no artifac

-   no crash


必须证明：

-   registry参与，若tool已注册

-   PlanValidator参与，若走planner

-   runtime参与

-   artifact validator参与

-   artifact retrieval成功


----------

# 34. Planner Policy

如果本阶段tool planner-visible，必须验证：

适合：

-   import this molecular dynamics trajectory

-   parse this extxyz trajectory

-   normalize this trajectory file


不适合：

-   play trajectory

-   animate trajectory

-   calculate RDF

-   simulate MD

-   edit trajectory


推荐本阶段：

```tex
planner-visible: false or limited



直到Trajectory Viewer完成。

必须记录决定。

----------

# 35. Frontend范围

本阶段不实现viewer。

允许实现最小JSON-only result surface：

-   parse status

-   forma

-   frames

-   atoms

-   properties

-   lattice mode

-   warnings

-   artifact downloads


不得实现：

-   play

-   pause

-   slider

-   3D animation

-   per-frame rendering


如果已有generic artifact preview，可复用。

----------

# 36. Performance

记录：

-   input bytes

-   parse duration

-   normalization duration

-   serialization duration

-   peak memory proxy

-   frames/s处理趋势

-   artifact sizes


测试应采用：

-   bounded thresholds

-   ratio/trend

-   no superlinear obvious growth

-   no monotonic resource leak


不得使用过窄毫秒断言。

必须验证：

-   parser不一次性split大extxyz

-   cap在读取中生效

-   repeated parse无file handle/temp leak

-   cancellation及时


----------

# 37. Security

必须验证：

-   no code execution

-   no eval

-   no literal eval

-   no pickle

-   no arbitrary impor

-   no notebook execution

-   no script execution

-   no shell

-   no external URL

-   no remote file

-   no archive extraction

-   no symlink traversal

-   no path traversal

-   no arbitrary MIME

-   no arbitrary parser plugin

-   no metadata HTML execution

-   no JS

-   no callback

-   no oversized line bypass

-   no compressed payload bypass

-   no temp file leak

-   no private path

-   no secrets

-   no telemetry upload


必须输出：

```tex
NO_EXTERNAL_NETWORK_REQUESTS
NO_SECRET_PATTERN_HITS



----------

# 38. Dependency Policy

优先不新增依赖。

如果已有ASE或pymatgen：

-   可以复用

-   但必须审计其parser行为

-   必须包裹caps和security

-   不得直接暴露library exceptions

-   不得绕过canonical validator


如果没有：

-   优先实现有限extxyz parser

-   不要为了两种格式引入大型依赖


必须检查：

```bash
uv lock --check
npm --prefix apps/web ls --depth=0
npm --prefix apps/web run build



记录：

-   dependency tree

-   lockfile

-   bundle

-   parser dependency

-   licenses

-   no unexpected additions


----------

# 39. Evidence

新增：

```tex
docs/phase10g/evidence/phase10g1_trajectory_parser_adapter/



至少包含：

```tex
README.md
format_scope.json
format_detection.json
extxyz_mapping.json
native_json_mapping.json
unit_conversion_policy.json
identity_mapping.json
parser_caps.json
valid_fixed_lattice_result.json
valid_variable_lattice_result.json
valid_triclinic_result.json
atom_id_reorder_result.json
invalid_case_matrix.json
over_cap_result.json
deterministic_replay.json
api_valid_extxyz.json
api_valid_json.json
api_invalid.json
api_over_cap.json
performance_metrics.json
security_audit.json
network_audit.json
artifact_hashes.json



截图如有最小result surface，可包含：

```tex
01_trajectory_import_success.png
02_trajectory_summary.png
03_invalid_trajectory_error.png
04_over_cap_rejection.png



不得保存：

-   大型source trajectory

-   temp files

-   cache

-   private paths

-   token

-   secre

-   remote URL

-   crash dump

-   raw malformed payload全文


----------

# 40. Documentation

新增或更新：

```tex
docs/phase10g/phase10g1_trajectory_parser_adapter.md
docs/phase10g/phase10g1_trajectory_format_scope.md
docs/phase10g/phase10g1_extxyz_mapping.md
docs/phase10g/phase10g1_trajectory_normalization.md
docs/phase10g/phase10g1_trajectory_unit_conversion.md
docs/phase10g/phase10g1_trajectory_parser_security.md
docs/phase10g/phase10g1_trajectory_api_evidence.md
docs/phase10g/phase10g1_trajectory_readiness_matrix.md



更新：

```tex
docs/index.md
docs/13_SHARED_SCHEMA_SPEC.md
persistent/DESIGN_PROGRESS.md
persistent/TASK_BOARD.md
persistent/CHANGELOG.md
persistent/OPEN_QUESTIONS.md
persistent/TOOL_REGISTRY_NOTES.md
persistent/ARCHITECTURE_DECISIONS.md



必须记录：

-   supported formats

-   deferred formats

-   format detection

-   identity mapping

-   extxyz metadata

-   units

-   lattice/PBC

-   wrapping

-   caps

-   parser repor

-   adapter

-   planner visibility

-   API path

-   viewer deferred


----------

# 41. Readiness Matrix

最终分别判断：

-   format detection

-   extxyz parser

-   plain XYZ

-   native JSON parser

-   atom identity

-   atom-ID reorder

-   species stability

-   lattice

-   PBC

-   coordinates

-   wrapping

-   time

-   velocities

-   forces

-   energy

-   temperature

-   units

-   normalization

-   parser caps

-   cancellation

-   deterministic serialization

-   trajectory adapter

-   summary artifac

-   parser repor

-   manifes

-   API evidence

-   JSON result preview

-   security

-   trajectory viewer

-   playback

-   browser performance evidence

-   formal trajectory product registration


推荐期望：

```tex
format detection: READY
extxyz parser: READY
native JSON parser: READY
plain XYZ: READY or DEFERRED_BY_DESIGN
atom identity: READY
atom-ID reorder: READY
species stability: READY
lattice/PBC: READY
coordinate normalization: READY
wrapping policy: READY
time/unit mapping: READY
velocities: READY
forces: READY
energy: READY or PARTIAL_READY
temperature: READY
parser caps: READY
cancellation: READY
determinism: READY
trajectory adapter: READY
summary artifact: READY
parse report: READY
manifest: READY
API evidence: READY
security: READY

trajectory viewer: NOT_READY
playback: NOT_READY
browser performance evidence: NOT_READY
formal trajectory product registration: NOT_READY



----------

# 42. Checks

至少运行：

```bash
git diff --check
uv lock --check

uv run python -m pytest -q

npm --prefix apps/web tes
npm --prefix apps/web run typecheck
npm --prefix apps/web run build



并运行：

-   format detection tests

-   extxyz parser tests

-   native JSON parser tests

-   unit conversion tests

-   atom identity tests

-   lattice/PBC tests

-   parser cap tests

-   cancellation tests

-   deterministic replay

-   adapter tests

-   API integration

-   artifact validation

-   security scan

-   network audi

-   Phase 10 Closure Regression Pack

-   Phase 10G contract regression

-   service-backed integration

-   no-skipped assertion


本阶段不要求Trajectory Viewer browser matrix。

必须如实记录：

-   passed

-   failed

-   skipped

-   unavailable


不得把skipped写成passed。

----------

# 43. Commit / CI

完成parser、adapter、tests、evidence和docs后：

```bash
git status --shor
git diff --sta
git add <only Phase 10G-1 related files>
git commit -m "Add trajectory parser and adapter"
git push origin master



等待current HEAD CI。

必须确认：

-   backend unit success

-   frontend tests success

-   frontend typecheck success

-   frontend build success

-   parser tests success

-   API integration success

-   Phase 10 closure success

-   service-backed integration success

-   no-skipped assertion success

-   origin/master matches HEAD

-   git status clean


不得伪造CI。

----------

# 44. 最终报告格式

完成后输出：

# Phase 10G-1 Trajectory Parser / Adapter Resul

## 1. Conclusion

PASS / PARTIAL_PASS / FAIL

## 2. Baseline

-   Phase 10G assumed complete:

-   branch:

-   initial status:

-   final HEAD:

-   final status:


## 3. Format Scope

-   extxyz:

-   native JSON:

-   plain XYZ:

-   deferred formats:

-   detection:


## 4. Parser Architecture

-   detector:

-   streaming:

-   extxyz parser:

-   JSON parser:

-   normalizer:

-   validator:

-   cancellation:

-   cleanup:


## 5. Identity

-   source atom IDs:

-   canonical atom order:

-   row-order fallback:

-   reorder policy:

-   species stability:

-   mismatch handling:


## 6. Coordinates / Lattice / PBC

-   source coordinate mode:

-   canonical mode:

-   lattice mapping:

-   fixed/variable:

-   triclinic:

-   PBC:

-   wrapping:

-   missing lattice:


## 7. Units

-   positions:

-   time:

-   velocities:

-   forces:

-   energy:

-   temperature:

-   unknown units:

-   overrides:


## 8. Optional Properties

-   velocities:

-   forces:

-   energy:

-   temperature:

-   partial availability:

-   unknown properties:


## 9. Caps

-   input bytes:

-   line bytes:

-   atoms:

-   frames:

-   numeric values:

-   metadata:

-   output bytes:

-   overflow:

-   allocation timing:


## 10. Adapter

-   tool ID:

-   registry status:

-   planner visibility:

-   input:

-   output:

-   runtime:

-   validator:

-   artifacts:


## 11. Artifacts

-   trajectory:

-   summary:

-   parse report:

-   manifest:

-   hashes:

-   provenance:

-   security:


## 12. API Evidence

-   valid extxyz:

-   valid JSON:

-   invalid:

-   over-cap:

-   artifact retrieval:

-   typed errors:

-   runtime path:


## 13. Determinism

-   frame order:

-   atom order:

-   warning order:

-   manifest order:

-   hashes:

-   replay:


## 14. Performance

-   fixed fixture:

-   variable fixture:

-   over-cap:

-   repeated parse:

-   cancellation:

-   memory proxy:

-   temp/file handles:


## 15. Security

-   eval/literal eval:

-   pickle:

-   code execution:

-   external references:

-   path traversal:

-   archive handling:

-   metadata:

-   caps:

-   private paths:

-   secrets:

-   network:

-   markers:


## 16. Evidence

-   directory:

-   format scope:

-   mappings:

-   fixtures:

-   invalid matrix:

-   API:

-   performance:

-   security:

-   hashes:


## 17. Tests

-   detection:

-   extxyz:

-   JSON:

-   identity:

-   units:

-   lattice/PBC:

-   caps:

-   cancellation:

-   adapter:

-   API:

-   backend full:

-   frontend full:

-   typecheck:

-   build:

-   Phase 10 closure:

-   Phase 10G contract:

-   service-backed:

-   no-skipped:

-   lock:

-   diff:


## 18. Files

-   detector:

-   parser:

-   normalizer:

-   adapter:

-   schemas reused:

-   fixtures:

-   tests:

-   API tests:

-   evidence:

-   docs:

-   persistent:

-   dependencies/lockfile:


## 19. Deferred

明确列出：

-   ASE `.traj

-   LAMMPS dump

-   XDATCAR

-   XTC/TRR/DCD

-   chunked storage

-   frame index artifac

-   plain XYZ，若未实现

-   ambiguous energy mapping

-   partial property availability

-   trajectory viewer

-   playback

-   interpolation

-   dynamic bonds

-   trajectory expor

-   ensemble analysis

-   formal trajectory product registration


## 20. Readiness

-   parser:

-   extxyz:

-   JSON:

-   identity:

-   normalization:

-   units:

-   caps:

-   adapter:

-   artifacts:

-   API:

-   security:

-   viewer:

-   browser performance:

-   formal product:


## 21. Commit / CI

-   commit:

-   HEAD:

-   CI run:

-   backend:

-   frontend:

-   typecheck:

-   build:

-   parser:

-   API:

-   Phase 10 closure:

-   service-backed:

-   no-skipped:

-   origin:

-   status:


## 22. Whether allowed to enter next phase

允许 / 不允许

下一阶段：

```tex
Phase 10G-2：Trajectory Viewer



下一阶段只实现validated trajectory contract的静态/动态3D消费、frame controls、playback、selection identity和bounded rendering，不实现ensemble RDF、dynamic bond inference或trajectory editing。

----------

# 45. PASS 判定

PASS必须满足：

-   有真实format detector

-   有真实extxyz parser

-   有真实canonical JSON parser

-   parser bounded/streaming

-   input caps在读取过程中生效

-   atom identity稳定

-   ID reorder policy明确

-   species mismatch拒绝

-   frame count/atom count一致

-   lattice/PBC正确

-   triclinic正确

-   coordinate normalization正确

-   wrapping不被猜测

-   units严格转换

-   unknown units不被静默接受

-   optional properties按contract一致

-   parser cancellation完成

-   no partial artifacts

-   adapter真实进入runtime

-   canonical trajectory artifact生成

-   summary/report/manifest生成

-   deterministic replay完成

-   API evidence完成

-   no code execution

-   no external URL

-   no path traversal

-   no archive bomb路径

-   no secret hits

-   Phase 10G contract regression不回退

-   Phase 10 closure不回退

-   tests通过

-   CI通过

-   git clean


PARTIAL_PASS仅允许：

-   plain XYZ明确DEFERRED_BY_DESIGN

-   ambiguous generic energy字段明确不映射

-   某个非核心unit转换明确deferred

-   parser依赖audit因既有registry问题不可用

-   npm audit因既有registry问题不可用


FAIL包括：

-   只有parser stub

-   parser读取完整文件后才检查cap

-   仅按扩展名选择parser

-   使用eval/literal eval/pickle

-   静默重排atoms且不记录

-   species变化被接受

-   缺失lattice时伪造cell

-   wrapping被猜测

-   unknown units被默认转换

-   truncated frame返回partial success

-   invalid输入产生partial artifacts

-   adapter绕过validator

-   API evidence直接调用parser函数

-   提前实现viewer导致范围膨胀

-   Phase 10 closure回退

-   CI失败却声明PASS
---END---

---TASK---
 状态：待处理
 # Phase 10G-2：Trajectory Viewer

进入 Phase 10G-2：Trajectory Viewer。

可以默认：

-   Phase 10G：Trajectory Contract 已完成并通过

-   Phase 10G-1：Trajectory Parser / Adapter 已完成并通过

-   `phase10g.trajectory.v1

-   `phase10g.trajectory_frame.v1

-   `phase10g.trajectory_summary.v1

-   `phase10g.trajectory_manifest.v1

-   `phase10g.trajectory_parse_report.v1

-   extxyz和canonical trajectory JSON已能通过正式parser / adapter路径生成validated trajectory artifacts

-   atom identity、frame identity、coordinate mode、wrapping、lattice mode、time/unit policy、caps和security contract均已固定

-   Phase 10F static viewer、picking、measurement、supercell、clipping、camera、export、accessibility和performance基础保持稳定

-   `structure.viewer_3d`仍是静态结构viewer，不承担trajectory正式产品语义

-   Phase 10 Closure Regression Pack保持通过

-   当前branch、HEAD、working tree和Phase 10G-1 CI可视为正确且clean


本阶段不需要重复Phase 10G-1 baseline检查。

本阶段的主要任务是：

> 在现有static periodic crystal viewer基础上，实现validated trajectory artifact的bounded 3D消费、frame navigation、playback、stable atom identity、variable lattice支持、动态buffer更新、生命周期和accessibility闭环，为后续Phase 10G-3性能与浏览器证据提供真实产品基础。

本阶段重点包括：

-   trajectory viewer state

-   frame loading

-   play / pause

-   previous / nex

-   frame slider

-   playback speed

-   loop

-   timestamp / step display

-   stable atom identity across frames

-   fixed / variable lattice

-   wrapped / unwrapped display policy

-   current-frame picking

-   current-frame measuremen

-   current-frame inspector

-   bounded frame cache

-   dynamic GPU buffer updates

-   lifecycle and cancellation

-   accessibility

-   mobile controls

-   JSON fallback

-   initial browser smoke evidence


本阶段不实现ensemble analysis、dynamic bond inference、trajectory editing或正式trajectory product registration。

----------

# 1. 本阶段定位

Phase 10G-2是trajectory动态可视化实现阶段。

它必须解决：

-   trajectory artifact如何进入viewer

-   frame数据如何映射到GPU

-   frame切换如何避免完整renderer重建

-   atom identity如何跨frame稳定

-   fixed lattice和variable lattice如何显示

-   wrapped和unwrapped positions如何解释

-   playback如何受帧率和资源预算约束

-   picking和measurement如何绑定current frame

-   supercell、clipping和camera如何与trajectory组合

-   context loss、scene切换、快速拖动slider时如何取消stale frame

-   mobile和keyboard如何操作

-   over-budget trajectory如何安全fallback


本阶段不是：

-   trajectory parser phase

-   trajectory performance最终验收

-   ensemble RDF phase

-   MSD/diffusion phase

-   dynamic bond chemistry phase

-   trajectory editing phase

-   formal product registration phase


----------

# 2. 本阶段目标

必须完成以下十二类工作：

1.  **Trajectory viewer architecture audit**

2.  **Trajectory viewer state contract**

3.  **Frame navigation and playback**

4.  **Dynamic atom and lattice rendering**

5.  **Stable identity、picking和measurement**

6.  **Bond display policy**

7.  **Frame cache、cancellation和lifecycle**

8.  **Performance budgets and degraded/refused modes**

9.  **Accessibility and mobile controls**

10.  **Fallback、error和context-loss handling**

11.  **Tests、fixtures和initial browser smoke**

12.  **Docs、evidence和readiness closure**


本阶段必须产生真实trajectory viewer实现。

如果最终只有UI controls、mock animation、static frame preview或fixture demo，没有validated trajectory artifact驱动的真实动态3D路径，本阶段必须判定为FAIL。

----------

# 3. 严格禁止范围

本阶段不得实现：

-   dynamic bond inference

-   per-frame chemical bond guessing

-   reactive trajectory topology

-   variable atom count trajectory

-   atom insertion/deletion

-   species mutation

-   trajectory editing

-   frame editing

-   coordinate editing

-   lattice editing

-   trajectory trimming

-   trajectory merging

-   interpolation-based scientific frame creation

-   ensemble RDF

-   MSD

-   diffusion coefficien

-   VACF

-   velocity distribution

-   energy analysis

-   trajectory clustering

-   phonon animation

-   Brillouin zone

-   volumetric

-   trajectory export video

-   GIF/MP4

-   cloud streaming

-   remote frame loading

-   external API

-   notebook execution

-   script execution

-   real LLM

-   formal `structure.trajectory_viewer` registration


不得：

-   修改Phase 10G trajectory contract语义

-   修改static `viewer_scene.v2

-   将trajectory数据塞入`structure.viewer_3d` schema

-   将static viewer tool ID扩展为隐式trajectory tool

-   依赖array position之外的未经验证猜测恢复atom identity

-   对wrapped trajectory自动unwrap

-   对unknown wrapping做连续位移推断

-   对variable lattice静默使用首帧lattice

-   每帧重新创建所有Mesh、Material或Renderer

-   每帧重建整个React组件树

-   每帧重新推断bonds

-   每帧创建新event listener

-   每帧创建新geometry

-   无限缓存frames

-   无限预加载trajectory

-   在hidden tab继续高速播放

-   在context lost后继续更新GPU

-   将interpolation结果当作真实frame

-   允许artifact控制播放脚本、shader、callback或URL

-   允许external frame reference

-   允许trajectory绕过Phase 10G caps

-   先分配大型frame buffers再判断budge


允许：

-   bounded frame cache

-   dynamic instanced matrix update

-   dynamic buffer attribute update

-   frame navigation

-   on-demand rendering

-   bounded playback loop

-   current-frame measuremen

-   static bond policy

-   no-bond policy

-   tests

-   browser smoke

-   docs


----------

# 4. 必读实现

开始后直接阅读当前真实代码。

## 4.1 Static Viewer Architecture

搜索：

```bash
rg -n "WebGLRenderer|InstancedMesh|BufferGeometry|OrbitControls|viewer_scene|instanceId|PeriodicSiteRef|measurement|supercell|clipping|camera" apps/web



重点确认：

-   renderer ownership

-   scene build path

-   atom instancing

-   bond geometry

-   lattice geometry

-   instance mapping

-   picking

-   measurement overlays

-   supercell display state

-   clipping

-   camera state

-   on-demand render

-   animation frame lifecycle

-   cleanup

-   context loss

-   degraded/refused policy


## 4.2 Trajectory Contracts and Parser Outpu

阅读：

-   trajectory schema

-   frame schema

-   summary

-   manifes

-   parse repor

-   validator

-   parser

-   adapter

-   fixtures

-   API artifacts


确认：

-   artifact shape

-   atom ordering

-   frame ordering

-   coordinate mode

-   lattice mode

-   wrapping policy

-   optional properties

-   caps

-   canonical units


## 4.3 Existing Dynamic or Animation Code

搜索：

```bash
rg -n "playback|play|pause|frameIndex|requestAnimationFrame|timeline|slider|speed|loop|animation" apps/web backend packages tests



识别：

-   existing animation utilities

-   reusable controls

-   stale animation risks

-   hidden-tab handling

-   reduced-motion behavior

-   mobile slider patterns


## 4.4 Artifact Preview Integration

确认：

-   generic artifact result surface

-   manifest preview

-   artifact switching

-   JSON fallback

-   download links

-   tool metadata display

-   legacy/current schema gates


----------

# 5. 修改前输出审计

修改代码前输出：

# Phase 10G-2 Trajectory Viewer Pre-Implementation Audi

## 1. Current Static Renderer

-   renderer component:

-   atom rendering:

-   bond rendering:

-   lattice rendering:

-   picking:

-   measurement:

-   supercell:

-   clipping:

-   camera:

-   render scheduling:

-   cleanup:

-   context loss:


## 2. Current Trajectory Artifact Shape

-   trajectory schema:

-   frame schema:

-   frame count:

-   atom identity:

-   coordinate mode:

-   lattice mode:

-   wrapping:

-   time:

-   optional properties:

-   caps:


## 3. Existing Animation Infrastructure

-   requestAnimationFrame:

-   timers:

-   visibility handling:

-   reduced motion:

-   slider:

-   keyboard:

-   mobile:

-   cancellation:

-   known gaps:


## 4. Main Risks

至少列出：

-   full scene rebuild per frame

-   stale frame commi

-   frame slider race

-   playback loop duplication

-   atom identity drif

-   variable lattice stale geometry

-   wrapped/unwrapped confusion

-   measurement stale across frame

-   dynamic bond misuse

-   frame cache growth

-   hidden tab playback

-   context-loss updates

-   mobile memory pressure

-   long trajectory preload

-   supercell multiplication

-   clipping/picking mismatch

-   current-frame export ambiguity


## 5. Selected Strategy

说明：

-   trajectory state:

-   frame loading:

-   atom updates:

-   lattice updates:

-   bond policy:

-   picking:

-   measurement:

-   playback:

-   cache:

-   lifecycle:

-   accessibility:

-   mobile:

-   fallback:


## 6. Planned Files

列出预计修改或新增：

-   trajectory viewer componen

-   trajectory state

-   frame mapper

-   playback controller

-   frame cache

-   static viewer integration

-   controls

-   inspector

-   tests

-   fixtures

-   browser smoke runner

-   evidence

-   docs

-   persisten


审计后直接继续实现。

----------

# 6. Viewer Tool Boundary

本阶段不得修改：

```tex
structure.viewer_3d



的静态产品语义。

trajectory viewer应采用内部或预注册工具边界，例如：

```tex
structure.trajectory_viewer



但本阶段推荐：

```tex
registered internally / planner-hidden



正式用户可发现注册推迟到Phase 10G-3完成后。

必须明确：

-   static viewer消费`viewer_scene.v2

-   trajectory viewer消费`phase10g.trajectory.v1

-   trajectory viewer可以复用renderer internals

-   不复用静态scene schema作为trajectory数据容器

-   单frame显示可派生内部display state，但不生成新的权威trajectory artifac


----------

# 7. Trajectory Viewer State Contrac

建立application-owned viewer state。

建议：

```ts
type TrajectoryViewerState = {
  status:
    | "idle"
    | "loading"
    | "ready"
    | "playing"
    | "paused"
    | "degraded"
    | "refused"
    | "error";
  currentFrameIndex: number;
  requestedFrameIndex: number;
  frameCount: number;
  playbackSpeed: number;
  loop: boolean;
  direction: 1;
  isBuffering: boolean;
  activeGeneration: number;
};



可扩展：

```ts
type TrajectoryDisplayState = {
  showAtoms: boolean;
  showBonds: boolean;
  showCell: boolean;
  showAxes: boolean;
  supercellExpansion: [number, number, number];
  clippingState: ViewerClipState;
  cameraState: ViewerCameraState;
};



要求：

-   deterministic defaults

-   bounded values

-   no artifact callback

-   no executable fields

-   scene/trajectory切换时reset policy明确

-   frame index永远在合法范围内

-   requested/current分离，避免stale commi


----------

# 8. Initial Load Policy

trajectory artifact打开时：

必须先：

1.  validate trajectory summary/manifes

2.  validate viewer budge

3.  select initial frame

4.  build renderer

5.  expose controls


推荐initial frame：

```tex
frame 0



不得：

-   自动播放

-   自动加载全部frames

-   自动生成bonds

-   自动启用supercell

-   自动开启高成本overlays


初始状态推荐：

```tex
paused at frame 0



----------

# 9. Frame Navigation

必须支持：

-   previous frame

-   next frame

-   direct frame slider

-   frame number input，若UI合适

-   jump to firs

-   jump to last，可选


要求：

-   frame index bounded

-   slider change和frame commit分离

-   快速拖动时旧请求可取消

-   不提交stale frame

-   frame change触发on-demand render

-   不重建renderer

-   不重建camera

-   不重置user camera

-   不重复创建controls

-   frame change后UI、inspector和live region同步


键盘建议：

```tex
Left / Right: previous / next frame
Home: first frame
End: last frame
Space: play / pause



仅在trajectory viewer region聚焦时拦截。

不得影响输入框编辑。

----------

# 10. Playback Contrac

必须支持：

-   play

-   pause

-   playback speed

-   loop on/off


第一版只支持forward playback。

不实现reverse playback。

## Playback Speeds

使用application-owned allowlist。

建议：

```tex
0.25x
0.5x
1x
2x
4x



不得允许任意超高速度。

## End Behavior

必须固定：

### loop=false

到最后一帧：

-   pause

-   保持最后一帧


### loop=true

到最后一帧：

-   跳转frame 0

-   继续播放


## Frame Timing

第一版可以使用display playback interval，不必严格按physical time播放。

但必须区分：

```tex
display playback speed



与：

```tex
physical trajectory time



不得声称1x等于真实时间比例，除非contract明确实现。

UI应说明：

```tex
Playback speed controls display rate, not physical-time scale.



----------

# 11. Playback Scheduling

不得默认使用永久连续动画loop。

推荐策略：

-   仅playing状态启动调度

-   pause立即停止

-   hidden tab暂停或显著降频

-   unmount取消

-   scene switch取消

-   context lost取消

-   error/refused取消


可使用：

-   `requestAnimationFrame

-   或bounded timer + on-demand render


必须保证：

-   同一viewer最多一个playback loop

-   frame commit不会生成第二loop

-   repeated play/pause不增加loop

-   active loop metric可测

-   pause后loop为0


不得将OrbitControls render loop和playback loop重复叠加为多个持续loop。

----------

# 12. Reduced Motion

尊重：

```css
prefers-reduced-motion: reduce



要求：

-   不自动播放

-   手动play仍可用

-   默认playback speed可降低

-   frame transition不插值

-   no decorative motion

-   controls清晰说明


不得因为reduced motion完全禁用trajectory访问。

----------

# 13. Frame Data Mapping

必须建立：

```tex
validated trajectory frame
→ current frame display data
→ GPU updates



映射必须使用Phase 10G既定coordinate/lattice policy。

## Fractional Positions

使用当前frame有效lattice：

```tex
cartesian =
fractional[0] * a
+ fractional[1] * b
+ fractional[2] * c



## Cartesian Positions

直接使用canonical angstrom单位。

## Fixed Lattice

使用top-level fixed lattice。

## Variable Lattice

使用current frame lattice。

不得：

-   使用前一帧lattice

-   忘记更新cell boundary

-   混用Cartesian和fractional

-   对unknown wrapping自动转换


----------

# 14. Dynamic Atom Rendering

必须复用Phase 10F atom instancing基础。

要求：

-   atom count固定

-   species grouping固定

-   geometry/material复用

-   instanceId稳定

-   每帧只更新instance transforms或position buffers

-   不每帧新建InstancedMesh

-   不每帧新建geometry

-   不每帧新建material

-   不每帧重建scene graph

-   update后仅设置必要`needsUpdate

-   camera movement不触发frame remap


如果species固定，style groups应在initial build后保持稳定。

----------

# 15. Atom Identity Across Frames

Trajectory atom scientific identity：

```tex
atomIndex



或Phase 10G固定的stable atom ID。

显示身份建议：

```tex
atom:<atomIndex>



如果trajectory有source atom IDs，可同时显示：

-   canonical atom index

-   source atom ID

-   species

-   current frame


不得继续使用static periodic site identity：

```tex
siteIndex@[imageOffset]



作为trajectory顶层身份，除非viewer显示supercell periodic instance。

trajectory periodic display instance可表示为：

```ts
type TrajectoryPeriodicAtomRef = {
  atomIndex: number;
  imageOffset: [number, number, number];
};



key建议：

```tex
atom:<atomIndex>@[dx,dy,dz]



必须区分：

-   canonical trajectory atom

-   displayed periodic instance

-   current frame


frame index不是atom身份的一部分，但selection/result必须记录measurement发生在哪个frame。

----------

# 16. Supercell Integration

trajectory viewer可以复用Phase 10F-24 supercell display能力。

默认：

```tex
1×1×1



要求：

-   supercell只影响display

-   atomIndex不改变

-   imageOffset正确

-   frame切换只更新expanded instance positions

-   expansion cap继续生效

-   estimator考虑：

    -   atom coun

    -   frame coun

    -   current cache

    -   displayed instances

-   expansion change清除current selection和measurement draf

-   expansion change不修改trajectory artifac

-   variable lattice下supercell boundary随frame更新


不得：

-   为每frame预生成全部supercell instances

-   修改canonical trajectory atoms

-   将expanded instance写回trajectory


----------

# 17. Wrapped / Unwrapped Display Policy

## wrapped

按artifact positions原样显示。

不得额外wrap，除非parser已canonical化且contract明确。

## unwrapped

允许atoms移出primary cell。

cell仍显示current lattice。

UI必须明确：

```tex
Unwrapped trajectory positions may lie outside the displayed unit cell.



## unknown

按原始positions显示。

必须显示warning：

```tex
Trajectory wrapping state is unknown.



不得：

-   自动纠正

-   自动追踪跨边界连续性

-   自动做minimum-image动画


----------

# 18. Variable Lattice Rendering

variable lattice trajectory必须支持：

-   current frame cell update

-   axes update

-   supercell boundary update

-   fractional coordinate conversion

-   camera preservation

-   fit-current-frame操作


不得默认每frame自动camera fit，因为会导致跳动。

推荐camera策略：

```tex
preserve user camera across frames



提供可选：

```tex
Fit current frame



不自动执行。

如果lattice变化导致scene超出视野，UI可提示，但不强制改变camera。

----------

# 19. Bond Display Policy

本阶段必须固定明确策略。

推荐支持两种：

```tex
none
static_reference



## none

-   不显示bonds

-   默认安全模式


## static_reference

仅当trajectory artifact或关联artifact提供经过验证的canonical static bond topology时允许。

要求：

-   bond endpoints按stable atom index

-   topology在所有frame保持不变

-   bond positions随frame更新

-   不重新推断

-   不新增/删除bond

-   cross-boundary offset语义必须明确

-   variable lattice正确


不得实现：

```tex
dynamic_inferred



本阶段禁止逐帧距离猜bond。

默认建议：

```tex
bond mode = none



如果有关联静态结构和权威topology，可让用户显式开启static_reference。

----------

# 20. Static Reference Bond Contrac

如果实现static reference bonds，必须定义内部validated contract。

至少包含：

```ts
type TrajectoryStaticBond = {
  fromAtomIndex: number;
  toAtomIndex: number;
  relativeImageOffset: [number, number, number];
  source: string;
  authoritative: boolean;
};



要求：

-   stable order

-   no reversal duplicates

-   no zero-offset self bond

-   endpoint index合法

-   cap生效

-   bond identity跨frame稳定

-   bond length随frame变化，但topology不变


不得将变化bond length误报为topology变化。

----------

# 21. Picking

picking只针对current committed frame。

要求：

-   atom pick返回：

    -   atom index

    -   image offse

    -   current frame index

    -   current position

-   static bond pick返回：

    -   canonical bond identity

    -   current frame geometry

-   stale frame pick结果拒绝

-   requested frame未commit时不使用旧mapping产生新selection

-   frame切换后selection policy固定


推荐：

```tex
frame change clears hover but preserves selected atom identity



因为atom identity稳定。

对于selected periodic instance：

-   如果同一imageOffset仍显示，可保留

-   如果supercell变化导致实例不存在，清除


必须测试快速播放中的pick行为。

建议播放时：

-   禁用hover

-   click可自动pause后select，或直接禁止


必须选择固定策略。

推荐：

```tex
click selection pauses playback, then selects current frame.



----------

# 22. Measuremen

measurement只针对current committed frame。

必须支持：

-   distance

-   angle

-   dihedral


使用current frame Cartesian positions。

measurement result必须记录：

-   frame index

-   step，若存在

-   time，若存在

-   ordered atom identities

-   image offsets

-   value

-   uni

-   lattice identity/current frame

-   wrapping state

-   trajectory identity


推荐：

```tex
frame change clears active measurement draf



已完成measurement result可保留为历史项吗？

本阶段建议：

```tex
不保留跨frame measurement history



只保留current frame result。

原因：

-   避免状态复杂

-   ensemble measurement后续单独规划


播放开始时：

-   清除measurement draf

-   可保留current completed result但标记旧frame，或直接清除


推荐：

```tex
playback start clears active measurement and completed current-frame resul



确保不会把旧数值误认为当前frame。

----------

# 23. Inspector

Trajectory inspector必须显示：

## Trajectory Summary

-   kind

-   frame coun

-   atom coun

-   coordinate mode

-   wrapping

-   lattice mode

-   available properties


## Current Frame

-   frame index

-   step

-   time

-   lattice

-   energy

-   temperature

-   current status


## Selected Atom

-   atom index

-   source atom ID，若存在

-   species

-   image offse

-   Cartesian position

-   fractional position，若lattice可用

-   velocity，若存在

-   force，若存在


## Bond

仅static reference模式：

-   endpoints

-   relative image offse

-   current distance

-   source

-   authoritative


不得：

-   显示未提供的temperature/energy

-   从velocity推算temperature

-   将current distance称为canonical bond length

-   把unknown wrapping描述成wrapped


----------

# 24. Frame Cache

必须实现bounded frame cache。

推荐策略：

```tex
current frame
+ small look-behind
+ small look-ahead



例如：

```tex
2 previous + current + 4 nex



具体数值根据真实caps调整。

要求：

-   fixed maximum frame coun

-   fixed maximum bytes

-   LRU或deterministic eviction

-   no unbounded prefetch

-   scene switch清空

-   unmount清空

-   cache不含GPU renderer objects

-   stale loaded frame不可commi

-   cache metrics可审计


如果trajectory artifact当前完整驻留JSON：

-   cache仍应作为mapped display data cache

-   不复制全部frame多份


----------

# 25. Frame Prefetch

允许bounded prefetch。

播放时：

-   优先prefetch下一帧

-   loop时可prefetchframe 0

-   slider快速跳转时取消旧prefetch


不得：

-   预加载全部trajectory

-   并行无限frame decode

-   让prefetch阻塞current frame

-   在hidden tab继续大量prefetch


prefetch失败：

-   pause playback

-   显示typed warning/error

-   不提交错误frame


----------

# 26. Frame Generation and Stale Protection

每次frame request必须有generation token或等价机制。

必须防止：

```tex
request frame 10
request frame 20
frame 10 finishes later
frame 10 overwrites frame 20



要求：

-   current request generation

-   stale frame result discarded

-   stale mapped buffers released

-   stale error不覆盖current state

-   slider、playback、scene switch共用同一guard

-   unmount后不commi


typed code：

```tex
TRAJECTORY_FRAME_REQUEST_STALE



通常作为内部结果，不必向用户显示。

----------

# 27. Playback Buffering

如果下一帧未准备好：

必须选择固定策略。

推荐：

```tex
pause advancement, show buffering, resume when ready



不得：

-   跳过未知frame而不提示

-   显示旧frame但增加frame counter

-   让UI frame index领先于GPU frame

-   声称播放成功


必须区分：

-   requested frame

-   displayed frame


----------

# 28. Performance Modes

必须继承Phase 10F性能策略并加入trajectory维度。

## Interactive

-   atom/frame数在安全范围

-   full playback

-   picking

-   measuremen

-   bounded supercell

-   optional static bonds


## Degraded

可能降级：

-   lower sphere detail

-   bonds default off

-   hover disabled

-   lower maximum playback fps

-   smaller prefetch cache

-   labels off

-   measurement仍可手动使用


必须显示：

```tex
TRAJECTORY_VIEWER_DEGRADED_MODE



并列出降级项。

## Refused

超过trajectory viewer hard cap：

-   不初始化WebGL

-   no canvas

-   no contex

-   JSON summary可用

-   artifacts可下载

-   typed reason

-   parser/import job不应误标scientific failure


typed code：

```tex
TRAJECTORY_VIEWER_BUDGET_EXCEEDED



----------

# 29. Trajectory Complexity Estimator

扩展或新建application-owned estimator。

输入至少：

-   frame coun

-   atom coun

-   displayed instances

-   static bond coun

-   lattice mode

-   available vector properties

-   planned cache frames

-   mobile/desktop class

-   supercell expansion


输出建议：

```json
{
  "mode": "interactive",
  "frames": 100,
  "atoms": 64,
  "displayed_instances": 64,
  "cache_frames": 7,
  "estimated_position_values": 1344,
  "estimated_gpu_buffers": 4,
  "max_playback_fps": 30,
  "warnings": []
}



要求：

-   deterministic

-   no fingerprinting

-   no remote benchmark

-   no artifact override

-   before renderer allocation


----------

# 30. Playback FPS Policy

必须设置应用层上限。

建议：

```tex
interactive desktop max: 30 fps
degraded desktop max: 15 fps
mobile max: 15 fps
reduced motion default: paused



真实值需根据架构审计调整。

不得：

-   以monitor refresh rate无上限运行

-   artifact指定fps

-   允许1000fps

-   使用physical timestep直接造成高频循环


可以通过跳过display intervals降低播放速率，但不得跳过scientific frame而不说明。

推荐：

-   每次显示相邻真实frame

-   调整帧间时间控制display speed


----------

# 31. Hidden Tab and Visibility

监听document visibility。

当tab hidden：

-   pause playback

-   停止prefetch或降至0

-   停止render loop

-   保持current frame state


返回visible：

-   保持paused

-   不自动恢复播放，或恢复前状态


必须选择固定策略。

推荐：

```tex
hidden tab pauses; returning remains paused.



避免意外资源消耗。

----------

# 32. Context Loss and Recovery

## Context Los

-   stop playback

-   stop frame commits

-   cancel prefetch

-   show accessible fallback

-   preserve trajectory/current frame state in application memory

-   no duplicate contex

-   JSON summary仍可用


## Recovery

选择固定策略：

```tex
user-triggered retry



或：

```tex
automatic rebuild from current committed frame



推荐复用static viewer现有策略。

恢复后：

-   rebuild renderer

-   restore current frame

-   restore camera

-   restore supercell/clipping

-   remain paused

-   no duplicate canvas/contex


----------

# 33. Scene / Artifact Switching

切换trajectory时必须：

-   pause playback

-   cancel current frame reques

-   clear cache

-   clear selection

-   clear measuremen

-   dispose dynamic buffers

-   reset frame index

-   validate new artifac

-   preserve or resetcamera，必须固定策略


推荐：

```tex
new trajectory resets camera to fit frame 0



因为不同trajectory bounds可能差异巨大。

从trajectory切到static viewer：

-   trajectory loop归零

-   cache清空

-   no stale frame commi

-   no trajectory inspector残留


----------

# 34. Camera Integration

必须复用Phase 10F camera controls。

要求：

-   camera不随每帧自动rese

-   orbit/pan/zoom继续工作

-   camera preset可用

-   fit current frame可用

-   variable lattice不自动改变camera

-   camera state与trajectory frame解耦

-   playback期间camera操作可用或明确禁用


推荐：

```tex
camera controls remain usable during playback



但必须保证：

-   不触发scene rebuild

-   不改变frame timing语义

-   不重复render loop


----------

# 35. Clipping Integration

clipping作用于current frame display。

要求：

-   frame变化后clipping state保持

-   clipping不改变trajectory data

-   hidden atom不可pick

-   measurement只对visible selected atom进行新选择

-   existing selection若被clip隐藏，按static viewer既定policy处理

-   variable lattice下clip coordinate system语义固定


如果Phase 10F clipping使用display-cell fractional space：

-   variable lattice只改变world plane映射

-   semantic clip position保持


必须有tests。

----------

# 36. Accessibility

必须保持Phase 10F accessibility标准。

## Viewer Region

名称建议：

```tex
Trajectory viewer



必须说明：

-   current frame

-   total frames

-   playing/paused

-   speed

-   loop

-   wrapping mode

-   lattice mode


## Controls

必须可键盘操作：

-   play/pause

-   previous/nex

-   slider

-   speed

-   loop

-   first/las

-   fit current frame

-   clear selection


## Live Region

播报：

-   trajectory loaded

-   playback started

-   playback paused

-   frame changed，需节流

-   end reached

-   buffering

-   degraded mode

-   context los

-   error


不得：

-   每个高频frame都连续播报

-   播报每个atom位置

-   播报每一帧camera变化


推荐：

-   手动frame change播报

-   自动播放时只更新静态status文本，不逐帧live announce

-   pause时播报当前frame


----------

# 37. Mobile

必须支持：

-   play/pause大按钮

-   previous/nex

-   slider

-   speed selector

-   loop

-   frame summary

-   rotate/pan/zoom

-   tap selection

-   current-frame distance measuremen


要求：

-   touch target至少符合Phase 10F标准

-   slider不与viewer drag冲突

-   controls不遮挡全部viewer

-   portrait/landscape稳定

-   orientation change不复制canvas/contex

-   playback期间orientation change安全pause

-   mobile默认更低fps

-   mobile cache更小

-   no scroll trap


----------

# 38. Current-Frame Properties UI

如果frame包含：

-   time

-   step

-   energy

-   temperature


显示：

```tex
Frame 12 of 100
Step 1200
Time 1.2 ps
Potential energy -35.2 eV
Temperature 300 K



要求：

-   单位来自contrac

-   unavailable字段不显示

-   不显示`null

-   不推断

-   长数值格式稳定

-   scientific notation policy固定


----------

# 39. JSON-Only Fallback

以下情况必须有JSON-only summary：

-   over-budge

-   WebGL unavailable

-   context loss

-   unsupported renderer capability

-   trajectory valid but viewer refused

-   mobile resource refusal


显示：

-   trajectory summary

-   current capabilities

-   refusal reason

-   frame/atom counts

-   artifact downloads

-   no canvas

-   no contex


不得将有效trajectory标记为invalid。

----------

# 40. Typed Errors and Warnings

至少覆盖：

```tex
TRAJECTORY_VIEWER_SCHEMA_UNSUPPORTED
TRAJECTORY_VIEWER_ARTIFACT_INVALID
TRAJECTORY_VIEWER_BUDGET_EXCEEDED
TRAJECTORY_VIEWER_FRAME_INDEX_INVALID
TRAJECTORY_VIEWER_FRAME_LOAD_FAILED
TRAJECTORY_VIEWER_FRAME_REQUEST_STALE
TRAJECTORY_VIEWER_FRAME_DATA_NONFINITE
TRAJECTORY_VIEWER_LATTICE_MISSING
TRAJECTORY_VIEWER_LATTICE_INVALID
TRAJECTORY_VIEWER_ATOM_IDENTITY_MISMATCH
TRAJECTORY_VIEWER_STATIC_BOND_INVALID
TRAJECTORY_VIEWER_STATIC_BOND_LIMIT_EXCEEDED
TRAJECTORY_VIEWER_CACHE_LIMIT_EXCEEDED
TRAJECTORY_VIEWER_CONTEXT_LOST
TRAJECTORY_VIEWER_PLAYBACK_UNAVAILABLE
TRAJECTORY_VIEWER_DEGRADED_MODE
TRAJECTORY_VIEWER_WRAPPING_UNKNOWN



错误必须：

-   deterministic

-   sanitized

-   no stack

-   no raw frame payload

-   no private path

-   no secre


warning排序必须stable。

----------

# 41. Viewer Metrics

新增application-owned metrics。

至少记录：

## Trajectory

-   schema

-   kind

-   frame coun

-   atom coun

-   coordinate mode

-   wrapping

-   lattice mode

-   properties


## Viewer

-   current frame

-   requested frame

-   mode

-   playback state

-   speed

-   loop

-   cache size

-   cache bytes

-   displayed instances

-   static bonds

-   draw calls

-   geometries

-   materials

-   active loops

-   canvas coun

-   context coun


## Timing

-   initial load

-   frame map

-   GPU update

-   render

-   cache hit/miss

-   seek latency

-   disposal


不得上传metrics。

----------

# 42. Fixtures

新增bounded viewer fixtures。

至少：

## 42.1 Fixed Lattice MD

-   4 atoms

-   10–20 frames

-   fractional wrapped

-   time

-   velocities


## 42.2 Variable Lattice Relaxation

-   4 atoms

-   5–10 frames

-   per-frame triclinic lattice

-   forces

-   energy


## 42.3 Unwrapped Diffusion-Like

-   positions跨cell

-   wrapping=unwrapped

-   no auto-wrap


## 42.4 Unknown Wrapping

-   warning path


## 42.5 Static Reference Bonds

-   fixed topology

-   current-frame bond length变化


## 42.6 Near-Degraded

-   compact generator

-   enters degraded mode


## 42.7 Over-Budge

-   estimator refuses before renderer allocation


不得提交大型trajectory。

----------

# 43. Unit Tests

## Viewer State

-   initial paused

-   frame 0

-   frame bounds

-   play/pause

-   loop

-   speed allowlis

-   end behavior


## Frame Mapping

-   fractional fixed lattice

-   Cartesian fixed lattice

-   variable lattice

-   triclinic

-   wrapped

-   unwrapped

-   unknown wrapping


## Atom Updates

-   instance count stable

-   instance mapping stable

-   transforms update

-   no geometry recreation

-   no material recreation


## Playback

-   one loop maximum

-   pause stops loop

-   repeated play/pause

-   hidden tab

-   reduced motion

-   end without loop

-   end with loop


## Cache

-   hi

-   miss

-   eviction

-   byte cap

-   scene switch clear

-   unmount clear


## Stale Protection

-   rapid slider

-   playback plus slider

-   scene switch

-   stale frame resul

-   stale error


## Variable Lattice

-   cell update

-   axes update

-   supercell update

-   camera preserved

-   no automatic fi


## Bonds

-   none

-   static reference

-   invalid endpoin

-   cap

-   no inference


----------

# 44. Picking and Measurement Tests

## Picking

-   current frame atom

-   copied supercell atom

-   frame switch identity

-   stale mapping

-   hidden clipped atom

-   playback click pauses

-   mobile tap


## Measuremen

-   distance current frame

-   angle current frame

-   dihedral current frame

-   variable lattice

-   cross-cell measuremen

-   frame provenance

-   frame change clears draf

-   playback start clears resul

-   no cross-frame stale value


----------

# 45. Accessibility Tests

覆盖：

-   viewer region name

-   play/pause names

-   slider accessible value

-   current frame tex

-   speed selector

-   loop state

-   keyboard shortcuts

-   no keyboard trap

-   focus restoration

-   live region bounded

-   auto playback不逐帧刷屏

-   degraded/refused state

-   reduced motion

-   200% zoom

-   mobile touch targets


----------

# 46. Lifecycle Tests

至少覆盖：

-   repeated mount/unmoun

-   repeated artifact switch

-   play→switch

-   rapid slider→switch

-   context loss during playback

-   retry

-   hidden tab

-   unmount during frame load

-   orientation change

-   cache cleanup

-   active loop zero

-   canvas/context stable

-   geometry/material stable

-   no stale inspector

-   no stale selection

-   no stale measuremen


----------

# 47. Initial Browser Smoke Evidence

本阶段需要真实browser smoke，但最终性能矩阵推迟到Phase 10G-3。

新增：

```tex
docs/phase10g/evidence/phase10g2_trajectory_viewer/



## Chromium

至少覆盖：

-   trajectory load

-   frame slider

-   play/pause

-   next/previous

-   loop

-   fixed lattice

-   variable lattice

-   atom picking

-   distance measuremen

-   supercell

-   clipping

-   context loss

-   over-budget fallback


## Firefox

smoke：

-   load

-   play/pause

-   slider

-   fallback


## WebKi

smoke：

-   load

-   slider

-   mobile-like controls

-   fallback


## Mobile

smoke：

-   play/pause

-   slider

-   rotate

-   tap selection

-   distance

-   orientation

-   refused fallback


----------

# 48. Browser Evidence Assertions

记录：

-   browser version

-   viewpor

-   trajectory fixture

-   frame coun

-   atom coun

-   current frame

-   requested frame

-   playback state

-   speed

-   loop

-   wrapping

-   lattice mode

-   cache size

-   draw calls

-   geometries

-   materials

-   active loops

-   canvas coun

-   context coun

-   console errors

-   network requests


必须验证：

-   frame order正确

-   displayed frame与UI一致

-   no stale frame

-   play/pause正确

-   no duplicate loop

-   atom identity稳定

-   variable lattice正确

-   measurement绑定current frame

-   hidden/over-budget无renderer分配

-   no external network

-   no artifact JS


----------

# 49. Evidence Files

至少包含：

```tex
README.md
trajectory_viewer_state_contract.json
playback_policy.json
frame_mapping_policy.json
identity_policy.json
bond_policy.json
cache_policy.json
performance_modes.json
fixed_lattice_results.json
variable_lattice_results.json
unwrapped_results.json
unknown_wrapping_results.json
picking_results.json
measurement_results.json
supercell_results.json
clipping_results.json
lifecycle_results.json
context_loss_results.json
over_budget_result.json
browser_smoke_matrix.json
mobile_smoke.json
console_audit.json
network_audit.json
security_audit.json
artifact_hashes.json



截图建议：

```tex
01_trajectory_frame_0.png
02_trajectory_playing.png
03_frame_slider.png
04_variable_lattice.png
05_atom_selected.png
06_distance_measurement.png
07_supercell_trajectory.png
08_unknown_wrapping_warning.png
09_over_budget_fallback.png
10_mobile_trajectory.png



不得保存：

-   巨大trajectory

-   full browser traces

-   cache dump

-   GPU dump

-   private path

-   token

-   secre

-   remote URL

-   crash dump


----------

# 50. Security

必须验证：

-   no artifact JavaScrip

-   no artifact HTML

-   no artifact callback

-   no artifact shader

-   no artifact module

-   no eval

-   no Function constructor

-   no remote frame

-   no external URL

-   no CDN

-   no remote texture

-   no iframe

-   no arbitrary file access

-   no notebook execution

-   no script execution

-   no real LLM

-   no artifact-controlled fps

-   no artifact-controlled cache size

-   no artifact-controlled loop callback

-   no artifact-controlled bond inference

-   no unbounded frame cache

-   no integer overflow

-   no telemetry upload

-   no private paths

-   no secrets


必须输出：

```tex
NO_EXTERNAL_NETWORK_REQUESTS
NO_SECRET_PATTERN_HITS



----------

# 51. Performance Requirements

本阶段必须达到基础性能正确性，但最终正式性能验收在Phase 10G-3。

必须证明：

-   renderer只初始化一次

-   frame change不重建renderer

-   atom geometry/material复用

-   current frame update bounded

-   one playback loop maximum

-   cache bounded

-   no preload all frames

-   over-budget before allocation

-   pause/hidden/unmount loop为0

-   repeated playback无资源单调增长

-   variable lattice更新不创建无限geometry

-   picking不持续raycas

-   measurement overlay bounded

-   supercell cap继续生效


不得使用过窄毫秒阈值。

----------

# 52. Dependency Policy

默认不新增依赖。

优先使用：

-   existing Three.js

-   existing static viewer internals

-   existing React state

-   existing Playwrigh

-   existing accessibility utilities

-   existing trajectory contracts


不得为了slider、cache或playback引入大型依赖。

检查：

```bash
uv lock --check
npm --prefix apps/web ls --depth=0
npm --prefix apps/web run build



记录：

-   dependency tree

-   lockfile

-   bundle size

-   renderer chunk change

-   no unexpected dependency


----------

# 53. Documentation

新增或更新：

```tex
docs/phase10g/phase10g2_trajectory_viewer.md
docs/phase10g/phase10g2_trajectory_viewer_state.md
docs/phase10g/phase10g2_trajectory_playback_contract.md
docs/phase10g/phase10g2_trajectory_frame_mapping.md
docs/phase10g/phase10g2_trajectory_identity.md
docs/phase10g/phase10g2_trajectory_bond_policy.md
docs/phase10g/phase10g2_trajectory_cache_and_lifecycle.md
docs/phase10g/phase10g2_trajectory_accessibility_mobile.md
docs/phase10g/phase10g2_trajectory_security.md
docs/phase10g/phase10g2_trajectory_evidence.md
docs/phase10g/phase10g2_trajectory_readiness_matrix.md



更新：

```tex
docs/index.md
docs/13_SHARED_SCHEMA_SPEC.md
persistent/DESIGN_PROGRESS.md
persistent/TASK_BOARD.md
persistent/CHANGELOG.md
persistent/OPEN_QUESTIONS.md
persistent/TOOL_REGISTRY_NOTES.md
persistent/ARCHITECTURE_DECISIONS.md



必须记录：

-   viewer/tool boundary

-   trajectory viewer state

-   frame mapping

-   playback semantics

-   display speed vs physical time

-   atom identity

-   periodic instance identity

-   wrapped/unwrapped behavior

-   fixed/variable lattice

-   bond policy

-   cache

-   stale protection

-   accessibility

-   mobile

-   performance limitations

-   formal registration deferred


----------

# 54. Readiness Matrix

最终分别判断：

-   trajectory artifact loading

-   frame validation

-   initial frame

-   previous/nex

-   frame slider

-   play

-   pause

-   playback speed

-   loop

-   end behavior

-   hidden tab handling

-   reduced motion

-   atom buffer updates

-   fixed lattice

-   variable lattice

-   triclinic

-   wrapped

-   unwrapped

-   unknown wrapping warning

-   atom identity

-   periodic instance identity

-   static reference bonds

-   bond inference

-   picking

-   measuremen

-   supercell

-   clipping

-   camera

-   cache

-   prefetch

-   stale protection

-   context loss

-   JSON fallback

-   accessibility

-   mobile

-   initial browser smoke

-   final performance evidence

-   formal tool registration


推荐期望：

```tex
trajectory artifact loading: READY
frame navigation: READY
playback: READY
speed/loop: READY
frame mapping: READY
fixed lattice: READY
variable lattice: READY
triclinic: READY
wrapped display: READY
unwrapped display: READY
unknown wrapping warning: READY
atom identity: READY
periodic instance identity: READY
static reference bonds: READY or PARTIAL_READY
dynamic bond inference: NOT_READY
picking: READY
measurement: READY
supercell: READY
clipping: READY
camera: READY
bounded cache: READY
stale protection: READY
context-loss fallback: READY
JSON fallback: READY
accessibility: READY
mobile foundation: READY
initial browser smoke: READY

final trajectory performance evidence: NOT_READY
formal structure.trajectory_viewer registration: NOT_READY
ensemble RDF: NOT_READY
trajectory analysis: NOT_READY
trajectory editing: NOT_READY



----------

# 55. Checks

至少运行：

```bash
git diff --check
uv lock --check

uv run python -m pytest -q

npm --prefix apps/web tes
npm --prefix apps/web run typecheck
npm --prefix apps/web run build



并运行：

-   trajectory viewer state tests

-   frame mapping tests

-   fixed lattice tests

-   variable lattice tests

-   playback tests

-   cache tests

-   stale frame tests

-   atom identity tests

-   picking tests

-   measurement tests

-   supercell/clipping regression

-   accessibility tests

-   mobile tests

-   lifecycle stress

-   context loss tests

-   Chromium smoke

-   Firefox smoke

-   WebKit smoke

-   mobile smoke

-   security scan

-   network audi

-   Phase 10 Closure Regression Pack

-   Phase 10G contract regression

-   Phase 10G-1 parser regression

-   service-backed integration

-   no-skipped assertion


必须如实记录：

-   passed

-   failed

-   skipped

-   unavailable


不得把skipped写成passed。

----------

# 56. Commit / CI

完成viewer、tests、evidence和docs后：

```bash
git status --shor
git diff --sta
git add <only Phase 10G-2 related files>
git commit -m "Add trajectory viewer playback"
git push origin master



等待current HEAD CI。

必须确认：

-   backend unit success

-   frontend tests success

-   frontend typecheck success

-   frontend build success

-   trajectory viewer tests success

-   browser smoke success

-   Phase 10 closure success

-   Phase 10G contract success

-   Phase 10G-1 parser success

-   service-backed integration success

-   no-skipped assertion success

-   origin/master matches HEAD

-   git status clean


不得伪造CI结果。

----------

# 57. 最终报告格式

完成后输出：

# Phase 10G-2 Trajectory Viewer Resul

## 1. Conclusion

PASS / PARTIAL_PASS / FAIL

## 2. Baseline

-   Phase 10G-1 assumed complete:

-   branch:

-   initial status:

-   final HEAD:

-   final status:


## 3. Viewer Architecture

-   trajectory component:

-   static renderer reuse:

-   frame mapper:

-   playback controller:

-   cache:

-   stale protection:

-   lifecycle:


## 4. Tool Boundary

-   internal tool ID:

-   registry status:

-   planner visibility:

-   static viewer impact:

-   formal registration:


## 5. Viewer State

-   initial state:

-   current/requested frame:

-   playing/paused:

-   speed:

-   loop:

-   buffering:

-   degraded/refused:


## 6. Frame Navigation

-   previous:

-   next:

-   slider:

-   first/last:

-   keyboard:

-   rapid seeking:

-   stale frame handling:


## 7. Playback

-   scheduler:

-   one-loop cap:

-   display speed:

-   physical time distinction:

-   end behavior:

-   loop behavior:

-   hidden tab:

-   reduced motion:


## 8. Frame Mapping

-   fractional:

-   Cartesian:

-   fixed lattice:

-   variable lattice:

-   triclinic:

-   wrapped:

-   unwrapped:

-   unknown wrapping:


## 9. Dynamic Rendering

-   atom instancing:

-   instance transforms:

-   geometry reuse:

-   material reuse:

-   lattice updates:

-   scene rebuild:

-   render scheduling:


## 10. Identity

-   canonical atom identity:

-   source atom IDs:

-   periodic display instance:

-   frame provenance:

-   instance mapping:

-   frame switch behavior:


## 11. Bonds

-   default mode:

-   static reference:

-   bond identity:

-   frame geometry:

-   dynamic inference:

-   caps:


## 12. Picking

-   current frame:

-   playback behavior:

-   periodic instance:

-   stale mapping:

-   clipped atoms:

-   mobile:


## 13. Measuremen

-   distance:

-   angle:

-   dihedral:

-   frame identity:

-   time/step provenance:

-   frame switch:

-   playback start:

-   variable lattice:


## 14. Supercell / Clipping / Camera

-   supercell:

-   variable lattice supercell:

-   clipping:

-   camera preservation:

-   fit current frame:

-   expansion change:


## 15. Cache / Prefetch

-   cache frames:

-   cache bytes:

-   eviction:

-   prefetch:

-   cancellation:

-   scene switch:

-   unmount:


## 16. Performance Modes

-   interactive:

-   degraded:

-   refused:

-   estimator:

-   fps caps:

-   mobile policy:

-   over-budget allocation:


## 17. Context Loss / Fallback

-   context lost:

-   playback stop:

-   recovery:

-   current frame restore:

-   duplicate canvas/context:

-   JSON fallback:


## 18. Accessibility

-   viewer region:

-   controls:

-   keyboard:

-   slider semantics:

-   live region:

-   reduced motion:

-   200% zoom:

-   focus:


## 19. Mobile

-   play/pause:

-   slider:

-   speed:

-   rotate/pan/zoom:

-   selection:

-   measurement:

-   orientation:

-   scroll behavior:

-   resource policy:


## 20. Metrics

-   initial load:

-   frame map:

-   GPU update:

-   render:

-   seek:

-   cache:

-   loops:

-   draw calls:

-   geometries:

-   materials:

-   canvas/context:


## 21. Browser Smoke

-   Chromium:

-   Firefox:

-   WebKit:

-   mobile:

-   fixed lattice:

-   variable lattice:

-   playback:

-   picking:

-   measurement:

-   fallback:

-   console:

-   network:


## 22. Security

-   artifact JS:

-   callbacks:

-   fps control:

-   cache control:

-   bond inference:

-   external frames:

-   dependencies:

-   private paths:

-   secrets:

-   network:

-   markers:


## 23. Evidence

-   directory:

-   state contract:

-   playback policy:

-   frame mapping:

-   identity:

-   bond policy:

-   cache:

-   lifecycle:

-   browser smoke:

-   screenshots:

-   hashes:


## 24. Tests

-   viewer state:

-   navigation:

-   playback:

-   frame mapping:

-   identity:

-   cache:

-   stale protection:

-   bonds:

-   picking:

-   measurement:

-   accessibility:

-   mobile:

-   lifecycle:

-   browsers:

-   backend full:

-   frontend full:

-   typecheck:

-   build:

-   Phase 10 closure:

-   Phase 10G:

-   Phase 10G-1:

-   service-backed:

-   no-skipped:

-   lock:

-   diff:


## 25. Files

-   trajectory viewer:

-   frame mapper:

-   playback:

-   cache:

-   renderer integration:

-   controls:

-   inspector:

-   tests:

-   fixtures:

-   browser runners:

-   evidence:

-   docs:

-   persistent:

-   dependencies/lockfile:


## 26. Deferred

明确列出：

-   final performance/browser acceptance

-   formal `structure.trajectory_viewer` registration

-   dynamic bond inference

-   reactive trajectories

-   variable atom coun

-   interpolation

-   frame blending

-   video/GIF expor

-   trajectory trimming

-   trajectory editing

-   ensemble RDF

-   MSD

-   diffusion

-   VACF

-   trajectory clustering

-   phonon animation


## 27. Readiness

-   artifact loading:

-   frame navigation:

-   playback:

-   identity:

-   fixed lattice:

-   variable lattice:

-   wrapped/unwrapped:

-   bonds:

-   picking:

-   measurement:

-   cache:

-   lifecycle:

-   accessibility:

-   mobile:

-   browser smoke:

-   final performance:

-   formal product:


## 28. Commit / CI

-   commit:

-   HEAD:

-   CI run:

-   backend:

-   frontend:

-   typecheck:

-   build:

-   viewer tests:

-   browser smoke:

-   Phase 10 closure:

-   Phase 10G:

-   Phase 10G-1:

-   service-backed:

-   no-skipped:

-   origin:

-   status:


## 29. Whether allowed to enter next phase

允许 / 不允许

下一阶段：

```tex
Phase 10G-3：Trajectory Performance / Browser Evidence



下一阶段只做trajectory viewer性能强化、长轨迹资源策略、完整浏览器矩阵、mobile evidence、formal tool registration和产品收口，不实现ensemble RDF、dynamic bond inference、trajectory editing或新的trajectory file formats。

----------

# 58. PASS 判定

PASS必须满足：

-   有真实validated trajectory artifact驱动的3D viewer

-   initial frame正确

-   previous/next正确

-   slider正确

-   play/pause正确

-   speed/loop正确

-   one playback loop maximum

-   pause/unmount/hidden tab loop归零

-   frame change不重建renderer

-   atom geometry/material复用

-   atom identity跨frame稳定

-   current/requested frame不混淆

-   stale frame不能覆盖新frame

-   fixed lattice正确

-   variable lattice正确

-   triclinic正确

-   wrapped/unwrapped不被错误转换

-   unknown wrapping显示warning

-   supercell仅影响display

-   clipping保持一致

-   camera不随每帧重置

-   picking绑定current frame

-   measurement绑定current frame并记录frame provenance

-   playback开始和frame切换不会保留错误measuremen

-   bond policy明确

-   不进行dynamic bond inference

-   cache bounded

-   no preload all frames

-   over-budget在renderer allocation前拒绝

-   context loss安全停止playback

-   JSON fallback可用

-   accessibility不回退

-   mobile基本可用

-   Chromium真实smoke完整

-   Firefox/WebKit/mobile smoke完成或如实记录

-   no artifact JS

-   no external frame/network

-   no secret hits

-   Phase 10 Closure、Phase 10G、Phase 10G-1不回退

-   tests通过

-   CI通过

-   git clean


PARTIAL_PASS仅允许：

-   static reference bonds明确PARTIAL_READY，但默认no-bond路径完整

-   某非主要浏览器自动播放计时存在已记录差异，但手动navigation和fallback完整

-   mobile只验证distance measurement，不验证angle/dihedral

-   精确性能指标留待Phase 10G-3

-   npm audit因既有registry问题不可用


FAIL包括：

-   只有静态frame preview

-   playback只是CSS或mock动画

-   每帧重建renderer

-   每帧创建geometry/material

-   多个并行playback loops

-   frame slider发生stale覆盖

-   variable lattice使用错误cell

-   atom identity跨frame漂移

-   wrapped/unwrapped被静默改变

-   measurement值来自旧frame

-   播放期间旧selection被错误解释

-   逐帧重新猜bond

-   缓存无上限

-   hidden tab继续高速播放

-   over-budget仍初始化WebGL

-   context loss后继续更新

-   提前正式注册trajectory产品但browser/performance未闭合

-   无真实browser smoke

-   Phase 10 closure回退

-   CI失败却声明PASS
---END---

---TASK---
 状态：待处理
 # Phase 10G-3：Trajectory Performance / Browser Evidence

进入 Phase 10G-3：Trajectory Performance / Browser Evidence。

可以默认：

* Phase 10G：Trajectory Contract 已完成并通过
* Phase 10G-1：Trajectory Parser / Adapter 已完成并通过
* Phase 10G-2：Trajectory Viewer 已完成并通过
* validated trajectory artifacts 已能通过正式parser / adapter路径生成
* trajectory viewer 已具备：

  * frame navigation
  * play / pause
  * playback speed
  * loop
  * fixed / variable lattice
  * wrapped / unwrapped / unknown wrapping显示策略
  * stable atom identity
  * picking
  * current-frame measuremen
  * bounded supercell
  * clipping
  * camera controls
  * bounded frame cache
  * stale frame protection
  * context-loss fallback
  * accessibility
  * mobile foundation
  * initial browser smoke
* `structure.viewer_3d`仍保持静态viewer语义
* trajectory viewer当前仍为内部或planner-hidden状态
* dynamic bond inference、ensemble analysis和trajectory editing仍未实现
* Phase 10 Closure Regression Pack保持通过
* 当前branch、HEAD、working tree和Phase 10G-2 CI可视为正确且clean

本阶段不需要重复Phase 10G-2 baseline检查。

本阶段主要目标：

> 对trajectory viewer进行正式性能强化、长轨迹资源策略闭合、完整跨浏览器和移动端证据验证，并在所有产品、安全、性能和API链路完成后正式注册`structure.trajectory_viewer`。

本阶段重点包括：

* performance budgets
* long trajectory strategy
* frame cache hardening
* GPU / CPU lifecycle
* memory growth detection
* rapid seeking stress
* playback stability
* variable lattice stress
* supercell trajectory stress
* context loss recovery
* browser matrix
* mobile evidence
* accessibility regression
* API / product-path evidence
* formal tool registration
* planner routing
* capability truth
* security closure
* CI closure

本阶段不实现新的科学分析功能。

---

# 1. 本阶段定位

Phase 10G-3是trajectory产品化收口阶段。

它必须解决：

* trajectory viewer在真实浏览器中是否长期稳定
* playback、seek、cache和GPU资源是否bounded
* 中长轨迹是否有明确interactive / degraded / refused策略
* Chromium、Firefox、WebKit是否行为一致
* mobile是否具备可接受的资源策略
* context loss和artifact switching是否无泄漏
  -正式API和产品路径是否真实闭环
* planner是否会正确选择trajectory viewer
* unsupported trajectory分析请求是否不会被误路由
* capability metadata是否准确
* formal tool registration是否安全

本阶段不是：

* trajectory parser扩展
* 新文件格式支持
* trajectory analytics
* trajectory editing
* dynamic bonds
* reactive MD
* distributed trajectory streaming
* cloud trajectory service

---

# 2. 本阶段目标

必须完成以下十二类工作：

1. **Performance architecture audit**
2. **Trajectory-specific performance budgets**
3. **Long trajectory and cache policy hardening**
4. **GPU / CPU / lifecycle stress validation**
5. **Complete browser and mobile evidence**
6. **Accessibility and reduced-motion regression**
7. **Formal API and product-path evidence**
8. **Formal `structure.trajectory_viewer` registration**
9. **Planner / PlanValidator routing**
10. **Capability and security closure**
11. **CI integration and stable regression entry**
12. **Phase 10G final readiness closure**

本阶段必须产生真实性能测试、browser evidence、API evidence和formal registration。

如果最终只有性能文档、手工截图或registry metadata，没有真实产品链路和自动化证据，本阶段必须判定为FAIL。

---

# 3. 严格禁止范围

本阶段不得实现：

* 新trajectory格式
* ASE `.traj
* LAMMPS dump
* XDATCAR
* XTC
* TRR
* DCD
* chunked remote streaming
* dynamic bond inference
* reactive trajectories
* variable atom coun
* atom insertion/deletion
* species mutation
* ensemble RDF
* MSD
* diffusion
* VACF
* velocity distribution
* trajectory clustering
* trajectory comparison
* trajectory trimming
* trajectory merging
* trajectory editing
* video expor
* GIF expor
* MP4 expor
* phonon animation
* volumetric rendering
* real MD simulation
* external API
* notebook execution
* script execution
* real LLM

不得：

* 修改Phase 10G contract语义
* 修改Phase 10G-1 parser语义
* 修改static `viewer_scene.v2
* 将trajectory嵌入`structure.viewer_3d
* 通过降低测试覆盖来改善性能
* 通过关闭validation改善性能
* 通过跳帧而不提示来伪造流畅
* 通过移除picking/measurement来达到性能指标
* 允许cache无上限
* 允许mobile预加载全部frames
* 允许artifact指定fps/cache/budge
* 在over-budget后初始化WebGL
* 使用不稳定绝对毫秒阈值作为唯一PASS标准
* 用开发机结果替代browser evidence
* 只跑Chromium就声称cross-browser READY
* 把skipped写成passed
* 提前声明dynamic bonds或ensemble analysis READY
* 伪造API、browser、CI结果

允许：

* performance hardening
* estimator改进
* cache tuning
* buffer reuse
* browser tests
* mobile tests
* registry/planner changes
* formal API wiring
* product UI integration
* docs
* evidence
* CI changes

---

# 4. 必读实现

开始后直接阅读当前真实代码。

## 4.1 Trajectory Viewer

搜索：

```bash
rg -n "TrajectoryViewer|frameIndex|playback|frame cache|prefetch|requestAnimationFrame|trajectory" apps/web


确认：

* viewer componen
* playback scheduler
* frame mapper
* atom buffer update
* variable lattice update
* cache
* prefetch
* stale generation guard
* picking
* measuremen
* supercell
* clipping
* camera
* fallback
* accessibility
* mobile layou

## 4.2 Metrics / Performance Infrastructure

搜索：

```bash
rg -n "performance|metrics|draw calls|memory|geometries|materials|canvas|context|FPS|frame duration" apps/web tests scripts


确认：

* existing Phase 10F metrics
* Three.js renderer.info usage
* lifecycle counters
* browser measurement helpers
* performance evidence forma
* thresholds and budget policy

## 4.3 Tool Registry / Planner / Runtime

搜索：

```bash
rg -n "structure.trajectory_viewer|ToolRegistry|PlanValidator|planner|tool catalog|service-backed" backend packages apps tests


确认：

* current internal tool registration
* planner visibility
* runtime adapter
* artifact inputs
* product result surface
* static viewer boundary
* API execution path

## 4.4 Browser Infrastructure

搜索：

```bash
find . -type f \( -iname "*playwright*" -o -iname "*browser*" -o -iname "*e2e*" \) | sor
rg -n "chromium|firefox|webkit|mobile|context loss|network audit|console audit" .


确认：

* browser matrix
* mobile devices
* test server
* service-backed setup
* download handling
* screenshot and metrics helpers
* CI environmen

---

# 5. 修改前输出审计

修改任何代码前输出：

# Phase 10G-3 Trajectory Performance / Browser Evidence Pre-Implementation Audi

## 1. Current Performance Architecture

* renderer count:
* canvas count:
* context count:
* geometry reuse:
* material reuse:
* atom buffer updates:
* lattice updates:
* playback loop:
* cache:
* prefetch:
* disposal:
* metrics:

## 2. Current Browser Coverage

* Chromium:
* Firefox:
* WebKit:
* mobile:
* context loss:
* variable lattice:
* long trajectory:
* rapid seek:
* supercell:
* accessibility:
* current gaps:

## 3. Current Product Path

* tool ID:
* registry status:
* planner visibility:
* PlanValidator:
* API:
* runtime:
* artifacts:
* result surface:
* browser entry:
* fallback:

## 4. Performance Risks

至少列出：

* repeated buffer allocation
* stale GPU updates
* cache byte growth
* prefetch overrun
* seek race
* playback loop duplication
* hidden tab work
* variable lattice geometry churn
* supercell multiplication
* measurement overlay churn
* context loss resource duplication
* mobile thermal/memory pressure
* browser timer throttling
* large artifact JSON parse cos
* renderer refusal timing
* test flakiness

## 5. Selected Strategy

说明：

* performance budgets:
* frame tiers:
* cache tiers:
* GPU reuse:
* long trajectory:
* browser matrix:
* mobile:
* formal registration:
* planner routing:
* API evidence:
* CI:

## 6. Planned Files

列出预计修改或新增：

* estimator/budgets
* trajectory viewer optimization
* metrics
* registry
* planner
* validator
* API tests
* frontend product UI
* browser specs
* performance runners
* evidence
* docs
* CI
* persisten

审计后直接继续执行。

---

# 6. Formal Tool ID

正式注册：

```tex
structure.trajectory_viewer


必须保证：

* 唯一
* 稳定
* registry中只出现一次
* 不与`structure.viewer_3d`重叠
* 不作为静态viewer alias
* 不通过magic string散落定义

推荐使用application-owned constant。

---

# 7. Formal Tool Metadata

建议metadata：

```json
{
  "tool_id": "structure.trajectory_viewer",
  "category": "structure",
  "display_name": "Trajectory Viewer",
  "description": "Inspect and play validated atomic structure trajectories with stable atom identity and bounded rendering.",
  "input_contract": "phase10g.trajectory.v1",
  "summary_contract": "phase10g.trajectory_summary.v1",
  "manifest_contract": "phase10g.trajectory_manifest.v1",
  "execution_mode": "service_backed",
  "deterministic": true,
  "network_access": false
}


字段按真实registry规范调整。

必须准确声明：

* fixed atom count：true
* stable species ordering：true
* fixed lattice：true
* variable lattice：true
* wrapped positions：true
* unwrapped positions：true
* playback：true
* picking：true
* current-frame measurement：true
* bounded supercell：true
* clipping：true
* camera controls：true
* static reference bonds：按真实结论
* dynamic bonds：false
* variable atom count：false
* editing：false
* ensemble analysis：false
* video export：false

---

# 8. Planner Routing

Planner必须正确选择trajectory viewer。

正向请求：

```tex
Play this molecular dynamics trajectory.


```tex
Inspect this relaxation trajectory frame by frame.


```tex
Show the atomic motion in this extxyz trajectory.


应选择：

```tex
structure.trajectory_viewer


负向请求：

```tex
Calculate ensemble RDF.


```tex
Compute diffusion coefficient.


```tex
Infer changing chemical bonds.


```tex
Edit frame 20.


不得由trajectory viewer伪完成。

必须验证：

* parser/import tool与viewer tool边界清晰
* static structure请求仍选择`structure.viewer_3d
* trajectory请求不选择static viewer
* unsupported analytics typed rejection或等待未来tool

---

# 9. PlanValidator

必须验证：

* tool ID已注册
* input artifact schema正确
* manifest正确
* frame/atom caps正确
* viewer options受allowlist约束
* playback speed受allowlist约束
* supercell受cap约束
* no dynamic bond reques
* no editing reques
* no external URL
* no arbitrary callback
* no arbitrary renderer config
* no remote frame source

typed codes建议：

```tex
TRAJECTORY_VIEWER_INPUT_REQUIRED
TRAJECTORY_VIEWER_INPUT_SCHEMA_INVALID
TRAJECTORY_VIEWER_OPTION_UNSUPPORTED
TRAJECTORY_VIEWER_DYNAMIC_BONDS_UNSUPPORTED
TRAJECTORY_VIEWER_ANALYSIS_UNSUPPORTED
TRAJECTORY_VIEWER_EDITING_UNSUPPORTED


不得放宽PlanValidator。

---

# 10. Performance Tier Model

必须建立正式性能tier。

建议至少三层：

## Tier A：Interactive

特征：

* 小到中型trajectory
* full navigation
* playback
* picking
* measuremen
* bounded supercell
* static reference bonds可用
* normal cache
* desktop最大30fps
* mobile最大15fps

## Tier B：Degraded

特征：

* 较大atom count或frame coun
* lower atom detail
* bonds默认off
* hover disabled
* lower fps
* smaller cache
* labels off
* supercell更严格
* measurement保留
* manual seek保留

## Tier C：Refused

特征：

* 超过hard cap
* no WebGL initialization
* no canvas/contex
* JSON summary
* artifact downloads
* typed reason
* parser/import job仍可成功

必须机器可验证。

---

# 11. Performance Budget Contrac

建立application-owned预算。

至少包含：

* max interactive atom coun
* max degraded atom coun
* max displayed instances
* max static bond coun
* max cache frames
* max cache bytes
* max mapped position values
* max playback fps
* max pending frame requests
* max prefetch requests
* max measurement overlays
* max active animation loops
* max canvas/context coun

建议区分：

```tex
desktop interactive
desktop degraded
mobile interactive
mobile degraded
hard refusal


具体值必须通过真实测试决定。

不得使用artifact提供的预算。

---

# 12. Long Trajectory Strategy

必须明确长轨迹处理。

至少分类：

## Many Frames / Few Atoms

主要风险：

* JSON parse
* cache
* seek
* playback scheduling

## Few Frames / Many Atoms

主要风险：

* GPU buffers
* draw calls
* supercell
* picking

## Many Frames / Many Atoms

通常进入：

* degraded
* refused
* future chunked storage

必须记录：

```tex
chunked/indexed storage: DEFERRED_BY_DESIGN


本阶段不得实现remote chunk streaming。

如果artifact已完整驻留JSON，必须避免：

* 映射全部frame为重复typed arrays
* 复制全部frame
* 预构建全部supercell数据

---

# 13. Frame Cache Hardening

必须验证并可能优化：

* deterministic LRU或固定window
* current frame永不被过早evic
* byte cap
* frame cap
* prefetch cap
* cache key包含trajectory identity
* trajectory switch清空
* schema switch清空
* no GPU object in cache
* no duplicate mapped frame copies
* stale frame不进入cache或可安全复用
* metrics可见

必须记录：

* cache hit ratio
* cache miss
* eviction
* bytes
* frame coun
* peak

---

# 14. Pending Request Cap

必须限制：

```tex
max pending frame decode/map requests


建议：

* current request：1
* prefetch：少量
* 快速seek取消旧请求
* 不排队数百frame

要求：

* rapid slider不会创建无限promise/task
* stale result被丢弃
* cancelled task释放临时buffer
* request queue metrics可测

---

# 15. GPU Resource Policy

必须证明：

* single WebGLRenderer per active viewer
* single canvas
* single contex
* atom geometries稳定
* atom materials稳定
* static bond geometries/materials稳定或bounded
* variable lattice不会每frame泄漏line geometry
* measurement overlay数量bounded
* clipping plane对象不每frame创建
* camera/controls不重建
* render targets无泄漏
* context recovery不复制renderer

记录：

* `renderer.info.memory.geometries
* `renderer.info.memory.textures
* draw calls
* programs，若可用
* canvas coun
* context coun

不得依赖私有browser internals作为唯一证据。

---

# 16. CPU and Main-Thread Policy

必须测量或记录：

* frame mapping duration
* GPU update duration
* render duration
* seek latency
* playback scheduling delay
* cache mapping cos
* variable lattice update cos
* supercell update cos

要求：

* no obvious O(frames × atoms) work per frame
* current frame更新应主要与displayed atoms/bonds相关
* camera move不重新map frame
* hidden tab工作归零
* pause后调度归零

不要求严格硬实时。

---

# 17. Playback Stability

必须进行bounded playback stress。

至少：

* 连续播放多个loop
* repeated play/pause
* speed切换
* loop切换
* slider介入播放
* next/previous介入播放
* browser tab隐藏
* artifact切换
* context loss
* mobile orientation change

断言：

* active loop最多1
* displayed frame不重复错乱
* current/requested frame一致
* no skipped frame，除非明确buffering
* end behavior正确
* loop behavior正确
* pause立即生效
* no monotonic memory growth

---

# 18. Rapid Seek Stress

测试：

```tex
0 → 20 → 3 → 50 → 7 → last → 1


或按fixture大小等价序列。

必须验证：

* 最终显示最后请求frame
* stale frame不能覆盖
* stale error不能覆盖
* cache仍bounded
* pending requests归零
* selection/measurement状态正确
* no duplicate render loop
* no console error

---

# 19. Variable Lattice Stress

至少覆盖：

* orthogonal → distorted
* triclinic变化
* cell volume变化
* lattice axis变化
* supercell boundary变化
* fractional positions映射
* camera保持
* fit current frame
* clipping保持
* measurement正确

必须证明：

* old lattice geometry被更新或dispose
* geometry count不单调增长
* no camera reset per frame
* no stale lattice/frame mismatch

---

# 20. Supercell Stress

至少测试：

* `1×1×1
* bounded `2×2×2
* max allowed expansion
* expansion during pause
* expansion during playback
* expansion then rapid seek
* variable lattice + supercell
* over-cap expansion拒绝

要求：

* displayed instance count准确
* atom identity稳定
* imageOffset稳定
* frame cache不复制supercell
* no geometry/material explosion
* over-cap before allocation

推荐：

* playback中改变supercell时自动pause
* 完成重建后保持paused

必须固定策略。

---

# 21. Picking / Measurement Performance

必须验证：

* hover按Phase 10F policy节流
* degraded模式hover可关闭
* playback中hover不持续高频raycas
* click selection按既定策略pause
* measurement overlay bounded
* measurement计算只使用current frame
* frame change清除stale resul
* no measurement history无界增长

记录：

* raycast calls，若可测
* overlay coun
* selection state
* measurement state

---

# 22. Context Loss Stress

必须真实或test-controlled触发context loss。

流程：

1. load trajectory
2. seek
3. play
4. trigger context loss
5. verify playback stops
6. verify fallback
7. retry/recover
8. restore current frame
9. remain paused
10. verify single canvas/contex

必须断言：

* no stale GPU update after loss
* cache/application state安全
* no duplicate renderer
* no duplicate controls
* no duplicate event listeners
* no extra playback loop

---

# 23. Artifact Switching Stress

序列建议：

```tex
small fixed trajectory
→ variable lattice trajectory
→ over-budget trajectory
→ invalid trajectory
→ static viewer
→ trajectory again


重复有限次数。

断言：

* old loop stopped
* old frame requests cancelled
* cache cleared
* selection cleared
* measurement cleared
* renderer disposed/reused按policy
* canvas/context stable
* fallback state不污染新trajectory
* no stale inspector

---

# 24. Mobile Performance Policy

mobile必须有独立预算。

至少考虑：

* lower max fps
* smaller cache
* stricter displayed instance cap
* bonds default off
* labels off
* hover unavailable
* touch selection
* reduced prefetch
* orientation pause
* background pause

必须测试：

* portrai
* landscape
* orientation change
* play/pause
* rapid slider
* supercell
* distance measuremen
* context loss/fallback
* over-budget refusal

不得把desktop预算直接应用到mobile。

---

# 25. Browser Matrix

必须完成完整矩阵。

## Chromium

完整覆盖：

* formal tool discovery
* planner selection
* API execution
* trajectory load
* fixed lattice
* variable lattice
* playback
* speed
* loop
* rapid seek
* picking
* measuremen
* supercell
* clipping
* camera
* degraded
* refused
* context loss
* artifact switching
* accessibility
* network/console audi

## Firefox

至少覆盖：

* tool/product path
* load
* fixed lattice
* variable lattice
* play/pause
* slider
* loop
* picking
* distance
* degraded/refused
* context fallback
* network/console audi

## WebKi

至少覆盖：

* tool/product path
* load
* play/pause
* slider
* mobile-like controls
* variable lattice
* measuremen
* fallback
* network/console audi

## Mobile Chromium / WebKi

至少覆盖：

* product entry
* play/pause
* slider
* speed
* loop
* touch selection
* distance
* supercell
* orientation
* over-budget fallback
* no scroll trap
* no duplicate canvas/contex

---

# 26. Browser Timing Policy

不得要求不同浏览器绝对时间相同。

应验证：

* frame ordering
* end behavior
* loop behavior
* bounded seek latency
* no long-task explosion
* no monotonic degradation
* no freeze/crash
* playback remains responsive

允许浏览器timer节流差异。

必须记录：

* browser version
* test environmen
* observed timer behavior
* semantic PASS依据

---

# 27. Accessibility Regression

必须完整回归：

* viewer region name
* formal product title
* play/pause accessible name
* current frame
* total frames
* slider value tex
* speed selector
* loop state
* keyboard shortcuts
* focus order
* no keyboard trap
* no focus loss after play/pause
* degraded/refused announcements
* buffering announcemen
* context loss announcemen
* reduced motion
* 200% zoom
* mobile touch targets
* autoplay禁止

自动播放时不得逐帧live announce。

---

# 28. Formal API Path

必须通过正式路径证明：

```tex
trajectory impor
→ validated trajectory artifac
→ planner selects structure.trajectory_viewer
→ PlanValidator
→ service-backed runtime
→ viewer result artifacts/state
→ frontend product surface


如果viewer本身是前端消费工具，API必须至少返回：

* formal tool resul
* trajectory artifact references
* summary
* manifes
* capability metadata
* viewer launch metadata
* warnings
* performance mode

不得直接调用前端fixture伪造API evidence。

---

# 29. API Evidence Cases

至少覆盖：

## Valid Fixed Lattice

* planner selects viewer
* runtime success
* product result ready

## Valid Variable Lattice

* schema valid
* viewer eligible
* variable lattice capability true

## Degraded

* runtime success
* viewer degraded
* artifact仍有效

## Refused

* runtime success或viewer-specific refused status
* no WebGL allocation
* JSON fallback

## Invalid Trajectory

* typed failure
* no viewer initialization
* sanitized error

## Unsupported Analytics Reques

* no false routing
* typed unsupported resul

---

# 30. Product UI

正式产品入口必须显示：

* Trajectory Viewer
* tool ID或合理产品名称
* trajectory kind
* frame coun
* atom coun
* lattice mode
* wrapping
* available properties
* performance mode
* warnings
* controls
* JSON fallback
* artifacts

不得显示：

* dynamic bonds READY
* ensemble RDF READY
* diffusion READY
* editing READY
* video export READY

---

# 31. Capability Contrac

建议：

```json
{
  "fixed_atom_count": true,
  "stable_species_order": true,
  "fixed_lattice": true,
  "variable_lattice": true,
  "wrapped_positions": true,
  "unwrapped_positions": true,
  "playback": true,
  "frame_navigation": true,
  "picking": true,
  "current_frame_measurement": true,
  "bounded_supercell": true,
  "clipping": true,
  "camera_controls": true,
  "static_reference_bonds": true,
  "dynamic_bonds": false,
  "variable_atom_count": false,
  "reactive_trajectory": false,
  "ensemble_rdf": false,
  "msd": false,
  "diffusion": false,
  "editing": false,
  "video_export": false
}


按真实实现调整。

若static reference bonds仍PARTIAL_READY：

* 不得简单写true
* 使用status模型或false

---

# 32. Deterministic Product State

必须验证：

* same trajectory → same initial frame
* same tool options → same viewer defaults
* same performance estimator resul
* same warnings
* same capability metadata
* same manifest order
* same product state serialization

不要求播放期间wall-clock timing一致。

不得将current timestamp加入canonical state。

---

# 33. Performance Test Fixtures

使用小型generator生成不同tier。

至少：

## A. Small Interactive

* 少量atoms
* 中等frames
* full capabilities

## B. Many Frames

* 少atoms
* 高frame coun
* cache/seek stress

## C. Many Atoms

* 少frames
* GPU/display stress

## D. Variable Lattice

* triclinic变化

## E. Supercell Stress

* moderate atoms
* bounded expansion

## F. Degraded

* estimator进入degraded

## G. Refused

* estimator拒绝
* 不创建巨大实际数组

不得提交大型binary fixture。

---

# 34. Repeated Playback Stress

必须进行有限重复。

建议：

* 10次play/pause
* 3个完整短loop
* 多次speed切换
* 多次seek

断言：

* memory proxy无单调增长
* geometries/materials稳定
* active loops回零
* pending requests回零
* cache回到bounded范围
* no console error

不得使用过长stress拖慢CI。

---

# 35. Long Session Stress

建议模拟：

```tex
load
→ seek
→ play
→ pause
→ measure
→ supercell
→ play
→ variable lattice
→ context loss
→ recover
→ switch artifac


重复有限次数。

目标：

* 组合生命周期
* 非纯fps benchmark

---

# 36. Metrics Evidence

必须记录：

## Scene / Renderer

* draw calls
* triangles/points/lines，若可用
* geometries
* textures
* programs
* canvas
* contex

## Trajectory

* frames
* atoms
* displayed instances
* static bonds
* lattice mode
* cache frames
* cache bytes
* pending requests

## Playback

* configured fps cap
* observed frame progression
* seek latency distribution或summary
* frame map duration
* GPU update duration
* render duration
* dropped/buffered events
* loop coun

## Lifecycle

* active loops
* listeners/observers，若可测
* object URLs
* cache after disposal
* renderer after disposal

不得上传metrics。

---

# 37. PASS Performance原则

不以单一毫秒阈值判断。

应综合：

* no leak
* no unbounded growth
* no freeze
* no stale commi
* bounded cache
* bounded pending requests
* stable resource counts
* correct tier selection
* responsive controls
* semantic browser consistency

对于时间指标：

* 使用宽松上限
* 使用趋势
* 使用相对比较
* 记录环境

---

# 38. Security

必须验证：

* no artifact JS
* no artifact HTML execution
* no callback
* no shader
* no module
* no eval
* no Function constructor
* no remote frame
* no external URL
* no CDN
* no remote texture/fon
* no iframe
* no notebook execution
* no script execution
* no real LLM
* no artifact-controlled fps
* no artifact-controlled cache
* no artifact-controlled browser tier
* no artifact-controlled renderer option
* no dynamic bond request execution
* no analytics overclaim
* no unbounded requests
* no telemetry upload
* no private path
* no secrets

必须输出：

```tex
NO_EXTERNAL_NETWORK_REQUESTS
NO_SECRET_PATTERN_HITS


---

# 39. Evidence Directory

新增：

```tex
docs/phase10g/evidence/phase10g3_trajectory_performance_browser/


至少包含：

```tex
README.md
formal_tool_registration.json
capability_contract.json
performance_budget_contract.json
performance_tier_matrix.json
cache_metrics.json
pending_request_metrics.json
gpu_resource_metrics.json
playback_stress.json
rapid_seek_stress.json
variable_lattice_stress.json
supercell_stress.json
context_loss_stress.json
artifact_switching_stress.json
desktop_performance_matrix.json
mobile_performance_matrix.json
api_valid_fixed.json
api_valid_variable.json
api_degraded.json
api_refused.json
api_invalid.json
planner_routing.json
plan_validator_results.json
browser_chromium.json
browser_firefox.json
browser_webkit.json
browser_mobile.json
accessibility_audit.json
console_audit.json
network_audit.json
security_audit.json
artifact_hashes.json


截图建议：

```tex
01_trajectory_tool_discovery.png
02_planner_selected_trajectory.png
03_fixed_lattice_playback.png
04_variable_lattice_playback.png
05_rapid_seek_final_frame.png
06_measurement_current_frame.png
07_supercell_trajectory.png
08_degraded_mode.png
09_refused_json_fallback.png
10_context_loss_recovery.png
11_mobile_playback.png
12_accessibility_controls.png


不得保存：

* 巨大trajectory
* browser cache
* full trace archive
* GPU dump
* private paths
* tokens
* secrets
* crash dumps
* remote URLs

---

# 40. Browser Evidence Assertions

每个case记录：

* browser version
* viewport/device
* tool ID
* trajectory schema
* trajectory identity
* frame coun
* atom coun
* current frame
* requested frame
* lattice mode
* wrapping
* performance tier
* fps cap
* cache frames/bytes
* pending requests
* displayed instances
* static bonds
* draw calls
* geometries
* materials
* active loops
* canvas/contex
* console errors
* network requests

必须验证：

* formal tool ID显示
* planner选择正确
* API/runtime真实路径
* displayed frame与UI一致
* no stale frame
* no duplicate loop
* no resource growth
* degraded/refused正确
* no external network
* no artifact JS
* no capability overclaim

---

# 41. CI Integration

必须建立稳定入口。

建议：

```bash
uv run python -m pytest -q tests/integration/test_phase10g3_trajectory_product.py


```bash
npm --prefix apps/web test -- trajectoryPerformance


```bash
npm --prefix apps/web run test:e2e -- trajectory-performance


具体按仓库现状调整。

优先加入现有：

* service-backed integration job
* frontend job
* browser matrix job

不建议复制完整workflow。

必须保证：

* failures返回非零
* core tests不可skip
* browser unavailable如实记录
* no deploymen
* no push in test scripts
* no external network dependency

---

# 42. Regression Scope

必须保持：

* Phase 10 Closure Regression Pack
* Phase 10G contrac
* Phase 10G-1 parser
* Phase 10G-2 viewer
* static `structure.viewer_3d
* periodic identity
* measuremen
* supercell
* clipping
* camera
* accessibility
* mobile
* expor
* security

必须特别验证：

* trajectory正式注册后不会改变static planner routing
* static结构不被误送trajectory viewer
* trajectory不被static viewer误处理

---

# 43. Documentation

新增或更新：

```tex
docs/phase10g/phase10g3_trajectory_performance.md
docs/phase10g/phase10g3_trajectory_browser_matrix.md
docs/phase10g/phase10g3_trajectory_mobile_policy.md
docs/phase10g/phase10g3_trajectory_tool_registration.md
docs/phase10g/phase10g3_trajectory_planner_routing.md
docs/phase10g/phase10g3_trajectory_security.md
docs/phase10g/phase10g3_trajectory_evidence.md
docs/phase10g/phase10g3_trajectory_readiness_matrix.md


更新：

```tex
docs/index.md
docs/13_SHARED_SCHEMA_SPEC.md
persistent/DESIGN_PROGRESS.md
persistent/TASK_BOARD.md
persistent/CHANGELOG.md
persistent/OPEN_QUESTIONS.md
persistent/TOOL_REGISTRY_NOTES.md
persistent/ARCHITECTURE_DECISIONS.md


必须记录：

* formal tool ID
* tool boundary
* planner routing
* performance tiers
* desktop/mobile budgets
* cache policy
* pending request policy
* browser differences
* context-loss policy
* capability truth
* unsupported analytics
* future chunked storage
* Phase 10G final readiness

---

# 44. Readiness Matrix

最终分别判断：

* formal tool ID
* registry
* planner discovery
* planner routing
* PlanValidator
* service-backed runtime
* API
* product UI
* trajectory artifact loading
* playback
* rapid seek
* cache
* pending request cap
* fixed lattice
* variable lattice
* wrapped/unwrapped
* picking
* measuremen
* supercell
* clipping
* camera
* degraded mode
* refused mode
* context loss
* artifact switching
* accessibility
* reduced motion
* mobile
* Chromium
* Firefox
* WebKi
* security
* CI regression
* full trajectory viewer produc
* dynamic bonds
* ensemble analysis
* editing

推荐期望：

```tex
formal tool ID: READY
registry: READY
planner discovery: READY
planner routing: READY
PlanValidator: READY
service-backed runtime: READY
API: READY
product UI: READY
trajectory playback: READY
rapid seek: READY
bounded cache: READY
pending request cap: READY
fixed lattice: READY
variable lattice: READY
wrapped/unwrapped: READY
picking: READY
current-frame measurement: READY
supercell: READY
clipping: READY
camera: READY
degraded mode: READY
refused mode: READY
context loss: READY
artifact switching: READY
accessibility: READY
mobile: READY
Chromium: READY
Firefox: READY
WebKit: READY
security: READY
CI regression: READY

full structure.trajectory_viewer: READY

dynamic bonds: NOT_READY
variable atom count: NOT_READY
reactive trajectories: NOT_READY
ensemble RDF: NOT_READY
MSD: NOT_READY
diffusion: NOT_READY
trajectory editing: NOT_READY
video export: NOT_READY


---

# 45. Checks

至少运行：

```bash
git diff --check
uv lock --check

uv run python -m pytest -q

npm --prefix apps/web tes
npm --prefix apps/web run typecheck
npm --prefix apps/web run build


并运行：

* trajectory performance tests
* cache tests
* pending request tests
* playback stress
* rapid seek stress
* variable lattice stress
* supercell stress
* context loss stress
* artifact switching stress
* registry tests
* planner tests
* PlanValidator tests
* API integration
* product UI tests
* accessibility regression
* mobile regression
* Chromium full matrix
* Firefox matrix
* WebKit matrix
* mobile matrix
* security scan
* network audi
* Phase 10 Closure Regression Pack
* Phase 10G contract regression
* Phase 10G-1 parser regression
* Phase 10G-2 viewer regression
* service-backed integration
* no-skipped assertion

必须如实记录：

* passed
* failed
* skipped
* unavailable

不得把skipped写成passed。

---

# 46. Commit / CI

完成性能强化、正式注册、tests、evidence和docs后：

```bash
git status --shor
git diff --sta
git add <only Phase 10G-3 related files>
git commit -m "Complete trajectory viewer performance and product evidence"
git push origin master


等待current HEAD CI。

必须确认：

* backend unit success
* frontend tests success
* frontend typecheck success
* frontend build success
* trajectory performance tests success
* browser matrix success
* API integration success
* registry/planner tests success
* Phase 10 Closure success
* Phase 10G success
* Phase 10G-1 success
* Phase 10G-2 success
* service-backed integration success
* no-skipped assertion success
* origin/master matches HEAD
* git status clean

不得伪造CI。

---

# 47. 最终报告格式

完成后输出：

# Phase 10G-3 Trajectory Performance / Browser Evidence Resul

## 1. Conclusion

PASS / PARTIAL_PASS / FAIL

## 2. Baseline

* Phase 10G-2 assumed complete:
* branch:
* initial status:
* final HEAD:
* final status:

## 3. Formal Tool Registration

* tool ID:
* registry:
* display name:
* input contract:
* summary contract:
* manifest:
* deterministic:
* network:
* planner visibility:

## 4. Capability Contrac

* fixed atom count:
* variable lattice:
* wrapped/unwrapped:
* playback:
* picking:
* measurement:
* supercell:
* clipping:
* static reference bonds:
* dynamic bonds:
* ensemble analysis:
* editing:

## 5. Planner / Validator

* discovery:
* trajectory routing:
* static viewer separation:
* unsupported analytics:
* dynamic bond rejection:
* editing rejection:
* option validation:
* caps:

## 6. Performance Budgets

* desktop interactive:
* desktop degraded:
* mobile interactive:
* mobile degraded:
* refusal:
* fps:
* cache:
* pending requests:
* displayed instances:
* static bonds:

## 7. Long Trajectory Strategy

* many frames:
* many atoms:
* many frames + many atoms:
* JSON limits:
* chunked storage:
* refusal policy:

## 8. Cache / Prefetch

* cache algorithm:
* frame cap:
* byte cap:
* prefetch:
* eviction:
* hit/miss:
* pending requests:
* rapid seek:
* cleanup:

## 9. GPU / CPU Resources

* renderer:
* canvas:
* context:
* geometries:
* materials:
* textures:
* draw calls:
* programs:
* frame mapping:
* GPU update:
* render:
* growth trend:

## 10. Playback Stress

* loops:
* repeated play/pause:
* speed switching:
* loop switching:
* end behavior:
* hidden tab:
* stale frame:
* buffering:
* active loop cap:

## 11. Variable Lattice / Supercell

* lattice updates:
* triclinic:
* camera:
* clipping:
* measurement:
* supercell:
* geometry growth:
* over-cap:

## 12. Lifecycle

* artifact switching:
* invalid trajectory:
* refused trajectory:
* static viewer switch:
* context loss:
* recovery:
* cache cleanup:
* pending request cleanup:
* loop cleanup:
* canvas/context stability:

## 13. API Evidence

* valid fixed:
* valid variable:
* degraded:
* refused:
* invalid:
* unsupported analytics:
* runtime:
* artifact retrieval:
* product state:

## 14. Product UI

* tool entry:
* trajectory summary:
* controls:
* performance mode:
* warnings:
* fallback:
* capability display:
* unsupported features:

## 15. Browser Evidence

* Chromium:
* Firefox:
* WebKit:
* mobile Chromium:
* mobile WebKit:
* semantic consistency:
* timer differences:
* console:
* network:

## 16. Accessibility

* region:
* controls:
* slider:
* keyboard:
* focus:
* live region:
* reduced motion:
* 200% zoom:
* touch targets:
* autoplay:

## 17. Security

* artifact JS:
* callbacks:
* external frames:
* fps/cache control:
* renderer options:
* dynamic bonds:
* analytics overclaim:
* dependencies:
* private paths:
* secrets:
* network:
* markers:

## 18. Evidence

* directory:
* registration:
* capabilities:
* budgets:
* stress:
* browser:
* mobile:
* API:
* accessibility:
* security:
* screenshots:
* hashes:

## 19. Tests

* performance:
* cache:
* pending requests:
* playback:
* rapid seek:
* variable lattice:
* supercell:
* context loss:
* lifecycle:
* registry:
* planner:
* validator:
* API:
* frontend:
* accessibility:
* mobile:
* Chromium:
* Firefox:
* WebKit:
* backend full:
* frontend full:
* typecheck:
* build:
* Phase 10 closure:
* Phase 10G:
* Phase 10G-1:
* Phase 10G-2:
* service-backed:
* no-skipped:
* lock:
* diff:

## 20. Files

* performance budgets:
* estimator:
* cache:
* viewer optimizations:
* registry:
* planner:
* validator:
* API:
* product UI:
* tests:
* browser runners:
* evidence:
* docs:
* persistent:
* CI:
* dependencies/lockfile:

## 21. Deferred

明确列出：

* new parser formats
* chunked/indexed trajectory storage
* remote streaming
* dynamic bond inference
* reactive trajectories
* variable atom coun
* ensemble RDF
* MSD
* diffusion
* VACF
* velocity analysis
* trajectory comparison
* trajectory editing
* interpolation
* video/GIF/MP4 expor
* phonon animation

## 22. Final Readiness

* parser/adapter:
* viewer:
* performance:
* browser:
* mobile:
* API:
* registry:
* planner:
* security:
* `structure.trajectory_viewer`:
* Phase 10G overall:

## 23. Commit / CI

* commit:
* HEAD:
* CI run:
* backend:
* frontend:
* typecheck:
* build:
* performance:
* browser:
* API:
* registry/planner:
* Phase 10 closure:
* Phase 10G:
* Phase 10G-1:
* Phase 10G-2:
* service-backed:
* no-skipped:
* origin:
* status:

## 24. Whether Phase 10G is formally closed

YES / NO

## 25. Whether allowed to enter next phase

允许 / 不允许

下一阶段：

```tex
Phase 10H：Phonon Contrac


下一阶段只定义phonon band、DOS、q-point、frequency、units、branch、eigenvector和mode contracts，不直接实现phonon animation。

---

# 48. PASS 判定

PASS必须满足：

* `structure.trajectory_viewer`正式注册
* registry中唯一
* planner可正确选择
* static viewer边界不回退
* unsupported analytics不误路由
* PlanValidator不放宽
  -正式API/runtime路径闭合
* performance tier明确
* desktop/mobile预算明确
* cache bounded
* pending requests bounded
* rapid seek无stale覆盖
* playback最多一个loop
* hidden/pause/unmount后loop归零
* frame mapping和GPU update无明显无界增长
* variable lattice无geometry泄漏
* supercell无资源爆炸
* degraded/refused模式真实工作
* over-budget前不初始化WebGL
* context loss恢复无重复canvas/contex
* artifact switching无stale状态
* Chromium完整矩阵通过
* Firefox矩阵通过
* WebKit矩阵通过
* mobile evidence通过
* accessibility不回退
* reduced motion正确
* capability metadata真实
* dynamic bonds/ensemble/editing全部false
* no artifact JS
* no external network
* no secret hits
* Phase 10 Closure、Phase 10G、Phase 10G-1、Phase 10G-2不回退
* tests通过
* CI通过
* git clean
* `full structure.trajectory_viewer: READY
* `Phase 10G overall: READY

PARTIAL_PASS仅允许：

* 某非核心browser环境在CI中明确unavailable，但测试保留且Chromium主链路完整
* 精确timer行为存在browser差异，但语义一致
* static reference bonds保持PARTIAL_READY且默认no-bond路径完整
* mobile在更严格预算下进入degraded，但功能和fallback正确
* npm audit因既有registry问题不可用

FAIL包括：

* 只有手工性能报告
* formal tool只注册metadata，没有真实产品路径
* planner仍选择static viewer处理trajectory
* cache/pending requests无上限
* rapid seek发生stale覆盖
* 多个playback loop
* memory/geometry/material单调增长
* over-budget仍初始化WebGL
* variable lattice泄漏geometry
* context loss后重复renderer
* Firefox/WebKit完全未验证却声明READY
* capability过度宣称
* unsupported analytics被trajectory viewer静默接受
  -无API evidence
* 无browser evidence
* Phase 10 closure回退
* CI失败却声明PASS


---END---
