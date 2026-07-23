---TASK---
 状态：处理中

# Phase 10J-4：Electrostatic Potential Product

进入 Phase 10J-4：Electrostatic Potential Product。

可以默认以下阶段均已严肃执行、完整验收并通过 current-HEAD CI：

* Phase 10F：Production Structure Viewer
* Phase 10G：Trajectory Contract / Adapter / Viewer / Evidence
* Phase 10H：Phonon Contract / Bands / DOS / Animation
* Phase 10I：Brillouin Zone Contract / Adapter / Renderer / Linked View
* Phase 10J：Volumetric Data Contract
* Phase 10J-1：Volumetric Parser / Adapter
* Phase 10J-2：Isosurface Renderer
* Phase 10J-3：Charge / Spin Density Product

必须以真实 Phase 10J-3 Result 为基线，记录实际：

* Phase 10J-3 commit
* current HEAD
* branch
* origin/master
* working-tree status
* volumetric schema versions
* potential quantity enums
* LOCPOT parser状态
* isosurface renderer版本
* browser caps
* CI run
* backend/frontend test counts

不得根据本 prompt 编造 commit、HEAD、测试数量、电势数值、浏览器版本、性能指标或 CI run。

本阶段必须产生真实 Electrostatic Potential 产品、科学语义验证、产品级 UI、Runtime artifact 消费和 Browser/API/Performance/Security Evidence，不是给通用等值面改标题或增加一个 LOCPOT 预设。

---

## 1. 本阶段总目标

在 Phase 10J-1 的 LOCPOT/volumetric artifacts 和 Phase 10J-2 的通用等值面 Renderer 上，实现正式电势工作流：

```text
LOCPOT / compatible potential source
        ↓
canonical real scalar potential field
        ↓
quantity / unit / gauge validation
        ↓
reference-state disclosure
        ↓
full-cell statistics
        ↓
3D equipotential surfaces
        ↓
point sampling / inspector
        ↓
axis-resolved planar averages
        ↓
bounded one-dimensional potential profiles
        ↓
structure overlay
        ↓
browser / performance / accessibility / security evidence
```

本阶段至少必须正式支持：

* `local_potential`
* `electrostatic_potential`，仅当来源明确
* source-defined potential gauge
* cell-average-zero gauge，若来源或显式派生明确
* constant-shift derived view
* 3D equipotential surfaces
* exact potential units
* Cartesian/fractional point sampling
* axis-aligned planar averages along lattice axes
* deterministic one-dimensional potential profiles
* source/reference disclosure
* potential difference between explicitly selected points
* real Runtime LOCPOT evidence
* Chromium / Firefox / WebKit / mobile evidence

---

## 2. Scientific Boundary

电势具有加常数的规范自由度。

对于：

```text
V'(r) = V(r) + C
```

局部电场梯度和点间电势差不变，但绝对零点发生变化。

本阶段必须始终区分：

* raw/source-native potential
* displayed shifted potential
* source-declared reference
* user-selected display reference
* derived cell-average-zero view
* physically authoritative reference
* unknown reference

不得把任意数值零点称为：

* absolute vacuum zero
* absolute electrostatic zero
* Fermi level
* vacuum level
* work-function reference

---

## 3. Minimum PASS Scope

PASS 至少要求：

### 3.1 LOCPOT Product

* Phase 10J-1 真实 LOCPOT Runtime artifact
* validated real scalar field
* explicit source quantity
* explicit unit
* explicit potential reference状态
* source-native values preserved
* 3D equipotential surfaces
* structure overlay
* potential inspector
* cell statistics
* planar average along three lattice directions
* point-to-point potential difference
* PNG export
* browser matrix
* performance/security evidence

### 3.2 Gauge Handling

至少支持：

* source-native
* cell-average-zero derived display
* user-selected point-zero display reference

所有shift必须：

* 只改变derived/display field
* 不修改source field
* 有明确shift amount
* 有单位
* 有provenance
* 可reset
* 不被称为物理真空对齐

### 3.3 Product Evidence

正式证据必须消费：

* Phase 10J-1 Runtime LOCPOT artifacts
* Phase 10J-2 Worker extraction
* 真实结构绑定
* 真实binary payload
* 真实field statistics

不得只使用synthetic plane或mock gradient完成产品证据。

---

## 4. 本阶段明确禁止

不得实现或宣称：

* automatic vacuum-level detection
* automatic work-function calculation
* work-function product
* Fermi-level extraction
* band-edge alignment
* core-level alignment
* absolute electrostatic potential
* cross-calculation potential alignment
* arbitrary two-LOCPOT subtraction
* defect correction
* charged-cell correction
* Makov–Payne correction
* Freysoldt correction
* dipole correction inference
* electric-field calculation product
* force calculation
* Poisson equation solution
* charge-density reconstruction
* Hartree potential reconstruction
* ionic potential separation
* exchange-correlation potential separation
* arbitrary potential component decomposition
* electrostatic energy calculation
* Bader analysis
* planar charge integration
* macroscopic dielectric analysis
* arbitrary smoothing
* unbounded convolution
* automatic vacuum-region recognition
* automatic slab-normal inference
* mixed-periodicity scientific claims
* surface dipole calculation
* interface lineup
* band offset
* direct volume ray casting
* general slice renderer
* arbitrary user-defined slicing planes
* arbitrary line paths
* arbitrary expression evaluation
* arbitrary Python
* notebook execution
* uploaded script execution
* external API
* artifact JavaScript
* artifact Worker code
* artifact WASM
* artifact shader
* artifact HTML/CSS
* external URL
* CDN
* remote assets
* artifact-defined colormap code

只有在未来存在独立、验证完整的 Fermi-level 和 vacuum-reference artifacts 时，才能计算 work function。

---

## 5. Public Tool 与产品身份

继续使用：

```text
structure.volumetric_data
```

优先不新增计算Tool。

正确架构：

```text
structure.volumetric_data
        ↓
validated potential field artifacts
        ↓
application-owned Electrostatic Potential Product
```

不得注册语义重叠的：

```text
structure.locpot
structure.electrostatic_potential
structure.potential_viewer
structure.work_function
```

如果现有架构必须为derived profiles生成正式artifact，可新增内部派生步骤或受控工具：

```text
structure.potential_profile
```

但必须满足：

* 只消费validated potential artifact
* 不重新解析source
* 不执行DFT
* 不自动确定vacuum level
* 不自动计算work function
* strict params
* 只允许三个canonical lattice-axis profiles
* 正式进入Registry、PlanValidator、Runtime和evidence
* Pre-Implementation Audit说明必要性

推荐将profile生成作为受控derived artifact步骤，而不是新的用户主入口。

---

## 6. Baseline Verification

首先执行：

```bash
cd "E:\1project\Material Data Intelligence"

git status --short
git branch --show-current
git rev-parse HEAD
git log --oneline -45
git remote -v
git rev-parse origin/master
```

必须确认：

* repository正确
* branch为`master`
* working tree clean
* HEAD包含Phase 10J-3
* origin/master正确
* LOCPOT Parser已实现
* canonical potential field已实现
* generic Isosurface Renderer已实现
* Charge/Spin产品未修改source field语义
* current-HEAD CI成功

如果working tree不干净，停止并报告，不得覆盖未知修改。

---

## 7. 必读实现

### 7.1 Phase 10J Contracts

必须阅读：

* `local_potential`
* `electrostatic_potential`
* potential units
* potential reference enums
* shift metadata
* grid coordinates
* row-step vectors
* flatten order
* statistics
* payload hashes
* structure binding
* derived-field provenance
* caps
* security

### 7.2 Phase 10J-1 LOCPOT Parser

必须阅读：

* LOCPOT source mapping
* source unit
* value conversion
* source order
* normalization
* source reference语义
* parser/provider version
* structure/grid binding
* spin/layout handling，若存在
* source metadata
* potential field ID

必须确认当前LOCPOT解析的是：

* local potential
* electrostatic potential
* total local potential
* 或其他正式定义

不得根据文件名将其重新命名为更强的科学语义。

### 7.3 Phase 10J-2 Renderer

必须复用：

* payload loader
* Worker protocol
* isosurface extraction
* periodic halo
* triclinic mapping
* clipping
* structure overlay
* picking
* inspector
* PNG export
* context loss
* browser evidence
* lifecycle

不得建立第二套Three.js Renderer或marching-cubes实现。

### 7.4 Phase 10J-3 Product Infrastructure

必须阅读并复用：

* product compatibility validators
* field/product manifest
* source/derived field区别
* scientific warnings
* exact unit显示
* statistics panel
* artifact reuse/cache
* mobile/accessibility产品布局

---

## 8. 修改前必须输出审计

修改代码前输出：

# Phase 10J-4 Electrostatic Potential Product Pre-Implementation Audit

## 1. Baseline

* Phase 10J-3 commit
* HEAD
* branch
* origin/master
* git status
* CI
* schema versions
* renderer version

## 2. Available Potential Fields

列出真实可用：

* local potential
* electrostatic potential
* source field IDs
* units
* gauge/reference
* grid
* normalization
* source format
* parser semantics

## 3. LOCPOT Scientific Semantics

明确：

* source value代表什么
* source unit
* zero/reference状态
* 是否含ionic/Hartree/XC components
* parser是否做过shift
* spin channels，若存在
* source metadata能够支持哪些结论

## 4. Existing Renderer/Product Support

* generic isosurfaces
* signed layers
* point sampling
* structure overlay
* inspector
* clipping
* export
* statistics
* missing potential-specific能力

## 5. Profile Strategy

明确：

* 平面平均方向
* node-grid weighting
* triclinic坐标
* position轴定义
* periodic endpoint
* profile artifacts
* smoothing政策
* caps
* independent references

## 6. Gauge Strategy

明确：

* source-native
* cell-average-zero
* selected-point-zero
* shift storage
* reset
* authoritative/non-authoritative labels

## 7. Scope Boundary

明确不实现：

* vacuum detection
* work function
* Fermi alignment
* cross-dataset alignment
* arbitrary slicing
* arbitrary line profile

## 8. Planned Files

列出implementation、tests、fixtures、runner、evidence、docs和persistent预计变更。

审计完成后直接实施，不等待人工确认。

---

## 9. Product Compatibility Validator

产品初始化前必须验证：

* dataset schema
* grid schema
* field schema
* payload schema
* structure binding
* lattice binding
* grid hash
* field hash
* payload hash
* quantity
* unit
* reference/gauge
* field rank
* value kind
* component count
* sample location
* endpoint policy
* boundary conditions
* finite values
* browser caps

正式支持：

```text
value_kind = real
field_rank = scalar
component_count = 1
quantity ∈ {
  local_potential,
  electrostatic_potential
}
```

Unknown或generic scalar不能自动进入Potential Product。

可以继续使用generic isosurface viewer，但不得提供电势科学声明。

---

## 10. Potential Quantity Semantics

### 10.1 Local Potential

```text
quantity = local_potential
```

必须显示：

* exact source label
* source format
* parser mapping
* unit
* reference state
* component decomposition unavailable，除非source明确提供

不得自动重命名为：

```text
electrostatic potential
```

### 10.2 Electrostatic Potential

只有source artifact明确声明：

```text
quantity = electrostatic_potential
```

才能使用该名称。

必须记录：

* physical definition
* sign convention
* unit
* reference
* source/provider
* included/excluded terms

### 10.3 Potential Energy vs Electric Potential

必须区分：

* electric potential，单位例如V
* electron potential energy，单位例如eV
* atomic-unit potential，单位例如Hartree/e

不得仅因为数值单位为eV就称为electric potential。

UI必须使用合同中的正式quantity和unit名称。

---

## 11. Potential Reference / Gauge

每个field必须有明确状态：

```text
absolute_declared
cell_average_zero
vacuum_reference
fermi_reference
source_defined
unknown
```

本阶段正式接受：

* source_defined
* cell_average_zero
* absolute_declared，仅有权威来源时
* vacuum_reference，仅由source artifact明确声明时
* fermi_reference，仅由独立兼容artifact明确绑定时
* unknown，可显示generic potential但限制科学操作

不得根据field mean、min、max自动推断reference。

---

## 12. Source-Native Field Preservation

原始field必须不可修改。

禁止：

* 直接覆盖source payload
* 将shift后的values写回source field ID
* 自动减去mean
* 自动将minimum设为0
* 自动将selected point设为0
* 自动归一化范围
* 自动clamp

所有变化必须生成：

* derived display state，或
* 正式derived shifted field artifact

并保存：

* source field hash
* shift type
* shift value
* shift unit
* formula/version
* provenance
* derived hash

---

## 13. Allowed Gauge Shifts

只允许allowlisted shifts：

```text
POTENTIAL_SOURCE_NATIVE_V1
POTENTIAL_CELL_AVERAGE_ZERO_V1
POTENTIAL_SELECTED_POINT_ZERO_V1
POTENTIAL_EXPLICIT_CONSTANT_SHIFT_V1
```

不得执行任意表达式。

### 13.1 Cell-Average-Zero

```text
V_shifted(r) = V_source(r) - <V_source>
```

其中：

```text
<V> = (1 / N) Σ V_i
```

对uniform full-cell grid，sample mean等于离散体积平均。

必须记录：

* source mean
* shift amount
* shifted mean residual
* unit
* formula ID

必须明确：

> Cell-average-zero 是显示/比较规范，不是真空参考。

### 13.2 Selected-Point-Zero

用户选择一个validated spatial point：

```text
V_shifted(r) = V_source(r) - V(r_ref)
```

必须记录：

* reference point Cartesian
* fractional coordinate，若periodic
* periodic image
* interpolation method
* sampled reference value
* source field hash

不得将该点称为物理零点。

### 13.3 Explicit Constant Shift

如允许用户输入shift：

* finite numeric only
* unit固定为field unit
* bounded magnitude
* no expression
* clearly marked user display shift
* not persisted as source scientific fact

---

## 14. Constant-Shift Invariants

必须验证：

* field range整体平移
* standard deviation不变
* RMS根据shift变化
* point differences不变
* gradients不变
* isosurface at shifted value对应source isosurface at原值
* structure/grid/hash不变
* source payload不变

必须增加reference tests防止shift被错误应用两次。

---

## 15. Full-Cell Statistics

必须显示：

* minimum
* maximum
* mean
* median或bounded quantile，若已有
* standard deviation
* RMS
* integral
* cell average
* value range
* reference/gauge
* shift amount
* source-native/derived状态

### 15.1 Potential Integral

必须谨慎命名：

```text
volume integral of potential
```

不得给出默认物理能量解释。

对于：

```text
∫ V(r) dV
```

必须显示单位，例如：

```text
eV·Å³
```

不得称为：

* total electrostatic energy
* potential energy
* field energy

### 15.2 Cell Average

```text
<V> = (1 / Ω) ∫ V(r)dV
```

对uniform grid使用sample mean。

必须有triclinic和shifted-origin reference tests。

---

## 16. Equipotential Surfaces

必须复用Phase 10J-2 Renderer。

支持：

* one isovalue
* multiple bounded isovalues
* positive/negative values
* source-native或shifted display field
* exact units
* structure overlay
* clipping
* picking
* PNG export

### 16.1 Default Isovalues

默认值是display heuristic，不是科学阈值。

建议提供：

* Low
* Mid
* High
* Around mean
* Around zero，只有当前gauge有明确零点时

每个preset必须显示实际数值与单位。

不得默认生成对称正负层，除非range和用户选择适合。

### 16.2 Gauge-Aware Isovalues

切换gauge时：

* surface的物理空间集合应保持或明确变化。
* 若保持相同source contour，应同步平移display isovalue。
* 若保持相同numeric display value，应明确surface将变化。

必须选择一种确定性产品策略并记录。

推荐：

```text
preserve source contour identity
```

即切换constant shift时，同一layer保存source-native isovalue，并显示转换后的当前gauge值。

这样避免仅因改变零点就意外改变表面。

---

## 17. Layer Identity

每个potential surface layer至少绑定：

* layer ID
* source field hash
* current gauge ID
* source-native isovalue
* displayed isovalue
* unit
* mesh hash
* visibility
* opacity
* product preset
* structure binding

不得只绑定一个会随gauge变化而失去语义的numeric isovalue。

---

## 18. Point Sampling

必须支持选中空间位置并显示：

* source-native potential
* current-gauge potential
* shift amount
* Cartesian coordinate
* fractional coordinate，若periodic
* periodic image offset
* interpolation method
* source field unit
* structure binding

必须使用经过验证的trilinear interpolation：

* canonical `ijk`
* periodic wrap
* shifted origin
* triclinic Cartesian→grid transform
* node samples
* finite results

不得将nearest voxel冒充精确采样。

---

## 19. Point-to-Point Potential Difference

用户可以选择两个点：

```text
A
B
```

计算：

```text
ΔV = V(B) - V(A)
```

必须显示：

* A/B coordinates
* A/B source-native values
* A/B displayed values
* ΔV
* unit
* interpolation method
* field hash
* gauge-invariant状态

必须验证：

* constant shift前后ΔV一致
* 两点来自同一field/grid
* periodic image identity明确
* selection stale时清理

不得将：

```text
q ΔV
```

自动称为能量，除非未来有显式charge输入和独立功能。

---

## 20. Planar Average

本阶段必须实现沿三个canonical lattice directions的平面平均。

对于grid shape：

```text
[nx, ny, nz]
```

定义：

```text
V̄_i(i) = average over j,k
V̄_j(j) = average over i,k
V̄_k(k) = average over i,j
```

其中每个profile position对应：

```text
u_axis = index / n_axis
```

并映射到沿对应lattice vector的物理长度：

```text
s_axis = u_axis * |a_axis|
```

但必须明确：

* profile plane由另外两个lattice vectors张成。
* triclinic情况下该profile方向与Cartesian法向不一定相同。
* `s_axis`是沿lattice vector的路径长度，不是平面法向距离。

不得将其模糊称为Cartesian x/y/z average。

---

## 21. Planar-Average Weighting

对uniform affine grid，每个voxel具有相同体积权重，因此固定index plane可使用算术平均。

必须验证：

* scalar field
* canonical flatten order
* periodic endpoint excluded
* shifted origin
* triclinic lattice
* dtype
* finite values

不得对不同grid或非uniform grid使用该公式。

Phase 10J当前只支持uniform affine grid，因此可以正式支持。

---

## 22. Profile Coordinate Identity

每个profile point至少包含：

* profile ID
* field hash
* gauge ID
* axis identity：`a1/a2/a3`
* index
* fractional coordinate
* path length in Å
* source-native value
* displayed value
* unit
* plane sample count

Axis identity必须使用结构化枚举：

```text
lattice_axis_0
lattice_axis_1
lattice_axis_2
```

UI可显示：

```text
a
b
c
```

但不得假定它们对应Cartesian x/y/z。

---

## 23. Profile Artifact / Model

建议新增正式derived artifact：

```text
potential_profile.v1
```

至少包含：

* source dataset/field binding
* structure/lattice binding
* gauge
* axis
* coordinates
* source values
* displayed values
* units
* statistics
* hash
* provenance
* security

如果profiles仅在前端Worker计算，也必须：

* typed model
* deterministic hash
* source field binding
* formula version
* tests
* evidence

优先生成可复现的derived profile artifacts。

---

## 24. Profile Caps

必须限制：

* max profile count
* max profile points
* max simultaneously visible profiles
* max cached profile artifacts
* max profile metadata bytes
* max profile export rows

默认仅允许三个canonical axis profiles。

不得允许任意高分辨率用户路径采样。

---

## 25. No Automatic Smoothing

本阶段不得默认执行：

* Gaussian smoothing
* moving average
* Savitzky–Golay
* FFT filtering
* macroscopic averaging
* convolution window
* spline interpolation

UI默认显示raw planar average。

如果为了显示可选连接线，只是绘图插值，不得生成新的科学values。

未来macroscopic average必须有独立窗口定义和合同。

---

## 26. Profile Chart

必须复用现有安全chart infrastructure。

支持：

* axis selector
* source-native / current-gauge display
* hover
* point selection
* zoom/pan
* reset
* exact coordinate/value
* structure-axis label
* unit
* mean reference line
* zero line，若当前gauge有明确零点
* selected spatial point handoff

不得：

* 使用任意HTML tooltip
* 允许artifact控制formatter代码
* 通过图形暗示vacuum plateau已识别
* 自动标注vacuum region
* 自动标注work function

---

## 27. Profile ↔ 3D Linked Selection

必须实现有限联动：

### Chart → 3D

选择profile index时：

* 在3D中显示对应lattice-coordinate plane
* plane仅为显示辅助
* 显示axis/index/fraction
* 不生成科学slice artifact
* 不改变field

### 3D → Chart

选择surface或空间点时：

* 计算该点在三个lattice axes的fractional coordinate
* 在当前profile中标记最近plane index或interpolated profile position
* 明确nearest/interpolated状态

不得将plane indicator称为field slice。

---

## 28. Plane Display

可在3D中显示当前profile plane。

要求：

* application-owned translucent plane
* bounded opacity
* correct triclinic geometry
* plane由对应两个lattice vectors张成
* periodic image明确
* no artifact shader
* no arbitrary plane equation
* no field texture

Plane只表示平均位置，不显示二维field。

---

## 29. Structure Overlay

必须验证：

* structure hash
* lattice hash
* grid hash
* coordinate frame
* source cell
* atom positions
* supercell identity

支持：

* atoms
* bonds
* unit cell
* lattice axes
* bounded supercell

不得将potential extrema自动归属给最近原子。

Inspector可显示：

```text
nearest atom distance
```

但必须明确这不是原子电势或原子电荷。

---

## 30. Potential Inspector

### 30.1 Field

必须显示：

* quantity
* source format
* parser/version
* source field ID
* source-native unit
* reference/gauge
* source shift
* current display shift
* grid
* min/max/mean/std
* volume integral
* cell average
* payload hash

### 30.2 Point

必须显示：

* Cartesian coordinate
* fractional coordinate
* image offset
* source-native value
* displayed value
* unit
* interpolation
* current gauge
* nearest atom distance，可选
* no atomic attribution

### 30.3 Surface

必须显示：

* source-native isovalue
* displayed isovalue
* gauge
* unit
* mesh hash
* selected coordinate
* sampled residual
* structure binding

### 30.4 Profile

必须显示：

* axis
* index
* fractional coordinate
* path length
* raw planar average
* displayed value
* plane sample count
* source field hash

---

## 31. Product Header / Scientific Warnings

Header必须显示：

* Local Potential / Electrostatic Potential
* source format
* structure/formula
* unit
* reference/gauge
* source-native/shifted状态
* grid shape
* validation state
* scientific limitations

至少显示以下适用警告：

* Potential zero is source-defined.
* Absolute potential is not available.
* Cell-average-zero is a display gauge.
* Vacuum level has not been detected.
* Work function has not been calculated.
* Cross-calculation comparison requires explicit alignment.
* LOCPOT component semantics depend on source/parser definition.

不得把这些信息隐藏在developer mode。

---

## 32. Product UI

建议布局：

```text
┌──────────────────────────────────────────────┐
│ Potential Header / Gauge / Scientific Status │
├───────────────────────┬──────────────────────┤
│ Controls / Profiles   │ 3D Equipotential     │
│                       │ + Structure           │
├───────────────────────┴──────────────────────┤
│ Point / Surface / Profile Inspector          │
└──────────────────────────────────────────────┘
```

必须包含：

### Controls

* field selector
* gauge selector
* shift value，若允许
* reset gauge
* isovalue layers
* exact source/display values
* opacity
* structure/bonds/cell
* clipping
* profile axis
* profile visibility
* camera/projection
* PNG export

### Status

* source quantity
* unit
* reference
* current shift
* profile formula
* unsupported scientific claims

---

## 33. Product Manifest

建议新增：

```text
electrostatic_potential_product.v1
```

至少包含：

* dataset binding
* source potential field
* derived shifted field/view
* gauge
* shift
* profile artifacts
* profile formulas
* surface layers
* source/display isovalues
* structure binding
* validation
* limitations
* security
* provenance

不得包含：

* JavaScript
* arbitrary formula
* callback
* shader
* URL
* camera script
* external assets

---

## 34. Planner Routing

完成后，以下请求应路由到：

```text
structure.volumetric_data
+
Electrostatic Potential Product
```

正向示例：

* 显示这个LOCPOT的局域势
* 查看这个电势场的等势面
* 沿晶格c方向画平面平均势
* 检查两个空间点之间的电势差
* 把这个LOCPOT设为胞平均零点显示
* Visualize the local potential from this LOCPOT
* Show equipotential surfaces
* Plot the planar-averaged potential along the third lattice axis
* Compare the potential at two selected points

### 34.1 Ambiguous Requests

例如：

* 显示静电势
* 画电势

如果source field只有`local_potential`：

* 使用其正式名称。
* 不升级为electrostatic potential。
* 显示source semantics。

### 34.2 Negative Routing

不得声称支持：

* 计算功函数
* 自动找真空能级
* 对齐两个LOCPOT
* 计算band offset
* 做缺陷电荷修正
* 计算电场
* 计算势能
* 运行VASP
* 计算LOCPOT
* 做宏观平均
* 生成任意切片
* 任意Python分析

必须返回明确unsupported/deferred。

---

## 35. Artifact Reuse

如果LOCPOT已被Phase 10J-1解析：

* 必须复用现有dataset。
* 不重复解析。
* 不复制source payload。
* profiles按field hash缓存。
* gauge shifts按source hash + shift formula identity缓存。
* isosurface mesh复用Phase 10J-2 cache。
* source artifact保持immutable。

不得为每次打开产品重新运行Parser。

---

## 36. API / Runtime Evidence

至少覆盖：

### Case A：Source-Defined LOCPOT

* real Runtime artifact
* local-potential semantics
* source-defined gauge
* equipotential surface
* structure overlay

### Case B：Cell-Average-Zero

* deterministic shift
* mean residual
* source field unchanged
* gauge warning

### Case C：Selected-Point-Zero

* picked reference point
* interpolated source value
* derived shift
* reset

### Case D：Point Difference

* points A/B
* source/display values
* gauge-invariant ΔV

### Case E：Planar Profiles

* lattice axis 0
* lattice axis 1
* lattice axis 2
* triclinic structure
* exact reference values

### Case F：Unknown Reference

* product remains viewable
* absolute-reference operations disabled
* warnings displayed

### Case G：Invalid Quantity

* generic scalar viewer remains available
* Potential Product refused

记录sanitized：

* plan
* job
* artifacts
* source field hash
* derived profile hashes
* gauge
* shift
* statistics
* selected points
* ΔV
* profile axes
* surface mesh hashes
* final states

---

## 37. Independent Scientific References

不得只用production product验证自己。

### 37.1 Constant Field

对于：

```text
V(r) = C
```

验证：

* min=max=mean=C
* cell-average-zero全为0
* point difference为0
* planar profiles恒定
* 非平凡等势面为空或全域退化，必须安全处理

### 37.2 Linear Affine Field

对于non-periodic affine grid：

```text
V(q0,q1,q2) = αq0 + βq1 + γq2 + C
```

验证：

* trilinear point sampling
* point differences
* planar averages
* gauge shift
* triclinic Cartesian mapping

### 37.3 Periodic Trigonometric Field

例如：

```text
V = A cos(2πu0) + B sin(2πu1) + C cos(4πu2) + D
```

验证：

* periodic wrap
* cell average
* three planar profiles
* source/display shifts
* isosurface contour identity

### 37.4 Gauge Invariance

验证：

* `ΔV`不变
* gradient不变，若内部测试计算
* profile differences不变
* source-contour identity不变
* source payload hash不变

---

## 38. Planar Profile Tests

必须覆盖：

* cubic grid
* orthorhombic grid
* triclinic grid
* shifted origin
* constant field
* axis-only varying field
* multi-axis varying field
* periodic endpoint excluded
* first/last plane
* source/display gauge
* float32/float64
* deterministic profile hash
* over-cap profile
* stale profile cancellation

Reference实现不得直接调用production profile reducer。

---

## 39. Potential-Profile Performance

必须避免：

* 三个profiles各自重复加载完整field。
* profile切换重新解析payload。
* gauge shift复制完整field。
* 每次hover重新计算plane average。
* 主线程对near-cap field同步求和。

优先：

* Worker一次计算三个raw profiles。
* source-native profile缓存。
* gauge shift对profile values应用常数。
* float64 streaming accumulation。
* transfer compact profile arrays。
* hash-keyed cache。
* artifact switch清理。

---

## 40. Performance Metrics

至少记录：

* payload bytes
* voxel count
* field load time
* gauge shift setup time
* profile calculation time
* profile bytes
* point-sampling latency
* point-difference latency
* field/gauge switching latency
* isosurface extraction time
* profile ↔ 3D selection latency
* mesh vertices/triangles
* browser memory estimate
* Worker count
* canvas/context count
* cache entries
* PNG export time
* artifact-switch cleanup

---

## 41. Required Performance Cases

至少覆盖：

1. small LOCPOT
2. triclinic LOCPOT
3. source-native gauge
4. cell-average-zero
5. repeated selected-point-zero changes
6. three planar profiles
7. rapid axis switching
8. repeated point sampling
9. repeated isovalue/gauge switching
10. moderate multi-million-voxel potential
11. near-browser-cap potential
12. repeated artifact switching
13. mobile profile/3D tab switching

---

## 42. Browser Evidence Matrix

必须在真实：

* Chromium
* Firefox
* WebKit
* mobile viewport

验证：

* product detection
* exact quantity/unit
* source-defined gauge
* cell-average-zero
* selected-point-zero
* reset
* equipotential surfaces
* source/display isovalues
* point sampling
* point-to-point difference
* three lattice-axis profiles
* triclinic profile plane
* profile ↔ 3D linked selection
* structure overlay
* picking
* inspector
* clipping
* PNG export
* scientific warnings
* invalid quantity fallback
* lifecycle
* console
* network

---

## 43. Required Screenshots

至少保存：

1. Potential Product header
2. source-native LOCPOT surface
3. quantity/unit/reference disclosure
4. cell-average-zero gauge
5. selected-point-zero gauge
6. source/display isovalue disclosure
7. selected surface inspector
8. selected point potential
9. point A/B potential difference
10. lattice-axis-0 planar profile
11. lattice-axis-1 planar profile
12. lattice-axis-2 planar profile
13. triclinic profile plane in 3D
14. source/profile linked selection
15. structure overlay
16. clipping state
17. unknown-reference warning
18. invalid-quantity fallback
19. accessibility profile table
20. mobile profile tab
21. mobile 3D tab
22. PNG export

每张截图记录：

* browser/version
* viewport
* deviceScaleFactor
* dataset hash
* field hash
* quantity
* unit
* source reference
* gauge
* shift
* source/display isovalues
* selected points
* ΔV
* profile axis
* profile hash
* mesh hash
* screenshot hash

---

## 44. Accessibility

必须支持：

* semantic gauge selector
* exact shift amount
* semantic field selector
* exact isovalues
* source/display value distinction
* keyboard point selection
* keyboard A/B point workflow
* point-difference announcement
* profile axis selector
* profile table
* profile chart keyboard focus
* linked plane selection
* visible focus
* quantity/unit/reference announcement
* scientific warnings可读
* no color-only status
* reduced motion
* mobile touch targets

Canvas外必须提供：

* source field summary
* gauge summary
* shift
* statistics
* selected points
* point difference
* profile values
* active layers
* limitations

---

## 45. Mobile

必须验证：

* product header
* gauge selector
* source/display values
* isovalue controls
* point sampling
* A/B selection
* ΔV panel
* profile axis
* profile chart/table
* 3D/profile tab switching
* structure controls
* clipping
* inspector drawer
* warnings
* no horizontal overflow
* Worker cancellation
* context lifecycle

移动端允许：

* 更低voxel/triangle cap
* 一次只显示一个profile
* 更低profile chart点数显示，但原始profile数据不得截断
* 禁用大supercell
* 降低pixel ratio
* 限制PNG分辨率

不得隐藏reference/gauge和scientific limitations。

---

## 46. Security

必须验证：

* no artifact JavaScript
* no artifact Worker/WASM
* no artifact shader
* no artifact HTML/CSS
* no external URLs
* no remote assets
* no iframe
* no eval
* no Function constructor
* no arbitrary gauge formula
* no arbitrary profile expression
* no arbitrary path sampling
* allowlisted shift formulas only
* finite shift values
* bounded profile arrays
* overflow-safe counts
* stale-worker protection
* source field immutable
* no local path
* no signed URL disclosure
* no token
* no secret
* redacted errors
* safe export filename

必须输出：

```text
NO_ELECTROSTATIC_POTENTIAL_PRODUCT_EXTERNAL_NETWORK_REQUESTS
```

以及：

```text
NO_SECRET_PATTERN_HITS
```

---

## 47. Dependency Policy

优先不新增依赖。

复用：

* Phase 10J statistics
* Phase 10J-2 Worker
* existing chart infrastructure
* existing Three.js
* existing payload loader
* existing interpolation helpers

不得为planar average引入重型信号处理库。

如果新增依赖：

* 说明必要性
* version
* license
* browser/Worker compatibility
* bundle size
* transitive dependencies
* security findings
* deterministic behavior
* lockfile变化

---

## 48. Frontend Tests

至少覆盖：

* product detection
* quantity validation
* unit/reference显示
* source-native gauge
* cell-average-zero
* selected-point-zero
* explicit shift
* reset
* source field immutability
* constant-shift invariants
* source/display isovalue mapping
* equipotential layers
* point sampling
* A/B point selection
* ΔV
* planar profile axes
* profile table/chart
* profile ↔ 3D linking
* triclinic plane
* structure overlay
* picking
* inspector
* clipping
* PNG export
* warnings
* invalid quantity fallback
* keyboard
* mobile
* lifecycle
* no duplicate canvas/context/Worker
* no stale profile/mesh

不得只测试控件存在。

---

## 49. Regression Tests

必须保持：

* Phase 10J contracts
* LOCPOT Parser
* source units/reference
* payload hashes
* generic Isosurface Renderer
* periodic halo/seam
* Charge/Spin Product
* structure viewer
* trajectory viewer
* phonon viewer
* BZ viewer
* Band–BZ linked view
* Tool Registry
* Planner
* PlanValidator
* QueueWorkerRuntime
* service-backed integration
* Phase 10 Closure Regression Pack
* no-skipped assertion

不得为电势产品修改LOCPOT source-native语义。

---

## 50. Evidence Directory

建议新增：

```text
docs/phase10j/evidence/phase10j4_electrostatic_potential_product/
```

至少包含：

* README
* pre-implementation audit
* real Runtime LOCPOT datasets
* source potential artifacts
* derived gauge/profile artifacts
* compatibility outputs
* statistics
* gauge-invariance references
* point-sampling references
* point-difference references
* planar-profile references
* product manifests
* browser matrix
* screenshots
* console logs
* network logs
* performance metrics
* memory estimates
* lifecycle metrics
* accessibility audit
* mobile audit
* PNG exports
* negative/fallback cases
* security audit
* dependency audit
* secret scan
* CI record
* replay commands

不得提交：

* secrets
* private paths
* proprietary productionLOCPOT
* browser profiles
* caches
* node_modules
* videos
* external assets
* oversized source files

---

## 51. Documentation

新增或更新：

* Phase 10J-4 overview
* local vs electrostatic potential
* potential energy vs electric potential
* units
* gauge/reference freedom
* source-native field
* constant-shift derived views
* cell-average-zero
* selected-point-zero
* gauge invariants
* source/display isovalues
* point sampling
* point differences
* planar-average definition
* lattice-axis profile semantics
* triclinic considerations
* profile ↔ 3D linking
* structure overlay
* inspector
* scientific warnings
* accessibility
* mobile
* performance
* security
* known limitations
* next-phase handoff

更新：

* `docs/index.md`
* `persistent/DESIGN_PROGRESS.md`
* `persistent/TASK_BOARD.md`
* `persistent/CHANGELOG.md`
* `persistent/OPEN_QUESTIONS.md`
* `persistent/TOOL_REGISTRY_NOTES.md`
* `persistent/ARCHITECTURE_DECISIONS.md`

ADR至少记录：

1. LOCPOT source quantity不得升级为更强语义。
2. Potential reference/gauge必须显式。
3. Source potential field不可修改。
4. Cell-average-zero只是规范选择，不是真空参考。
5. Point-to-point potential difference对constant shift不变。
6. Planar profiles沿lattice axes定义，不称为Cartesian x/y/z profile。
7. 本阶段不自动检测vacuum level。
8. 本阶段不计算work function。
9. Cross-calculation potential alignment留给独立后续阶段。

---

## 52. 明确 Deferred

Phase 10J-4完成后仍然deferred：

* automatic vacuum-level detection
* work-function calculation
* Fermi-level binding
* band alignment
* interface lineup
* defect-potential correction
* charged-cell correction
* arbitrary cross-dataset potential differences
* macroscopic averaging
* smoothing/filtering
* arbitrary slicing planes
* arbitrary line profiles
* electric-field product
* potential-gradient product
* potential component decomposition
* volume ray casting
* mixed-periodicity scientific product
* Bader/atomic charge analysis
* orbital/wavefunction products
* external APIs
* notebooks/scripts
* artifact code
* remote assets

---

## 53. Required Checks

至少运行：

```bash
git diff --check
uv lock --check
npm --prefix apps/web ls
npm --prefix apps/web ls three
npm --prefix apps/web test
npm --prefix apps/web run typecheck
npm --prefix apps/web run build
uv run python -m pytest -q
```

并单独运行：

* potential quantity tests
* unit/reference tests
* gauge-shift tests
* source-field immutability tests
* gauge-invariance tests
* source/display isovalue tests
* point-sampling tests
* point-difference tests
* planar-average tests
* triclinic-profile tests
* profile-artifact tests
* product-manifest tests
* profile ↔ 3D linking tests
* inspector tests
* clipping tests
* PNG export tests
* accessibility tests
* mobile tests
* lifecycle tests
* browser evidence runners
* performance/memory runners
* network audit
* security tests
* Phase 10J regressions
* Phase 10I regressions
* Phase 10H regressions
* Phase 10G regressions
* structure-viewer regressions
* service-backed integration
* no-skipped assertion
* secret scan

必须如实记录：

* passed
* failed
* skipped
* unavailable

不得把skipped写成passed。

---

## 54. Commit / Push / CI

全部完成后：

```bash
git status --short
git diff --stat
git add <only Phase 10J-4 related files>
git commit -m "Add electrostatic potential product"
git push origin master
```

等待current-HEAD CI。

必须确认：

* backend unit success
* frontend tests success
* typecheck success
* build success
* potential semantics tests success
* gauge/reference tests success
* profile tests success
* browser evidence success
* performance evidence success
* accessibility success
* Phase 10J contract success
* Phase 10J-1 parser success
* Phase 10J-2 renderer success
* Phase 10J-3 product success
* Phase 10I regression success
* Phase 10H regression success
* Phase 10G regression success
* structure-viewer regression success
* service-backed integration success
* no-skipped assertion success
* origin/master equals HEAD
* git status clean

不得伪造commit、CI run、电势值、profile值、浏览器版本、测试数量或性能指标。

---

## 55. PASS 判定

PASS必须全部满足：

* 真实Electrostatic Potential Product实现
* 使用真实Phase 10J-1 Runtime LOCPOT artifacts
* 使用Phase 10J-2 Renderer
* quantity语义严格
* unit严格
* potential energy/electric potential不混同
* source reference/gauge完整显示
* source field不可修改
* source-native mode完成
* cell-average-zero完成
* selected-point-zero完成
* constant shift provenance完成
* gauge-invariance tests完成
* source/display isovalue identity完成
* equipotential surfaces完成
* point sampling完成
* point-to-point ΔV完成
* ΔV gauge invariance完成
* 三个lattice-axis planar profiles完成
* triclinic profile语义正确
* profile artifacts/model完成
* profile ↔ 3D linked selection完成
* structure overlay完成
* inspector完成
* clipping完成
* PNG export完成
* scientific warnings完整
* 不声称vacuum level
* 不声称work function
* accessibility完成
* mobile完成
* performance/memory caps完成
* Chromium通过
* Firefox通过
* WebKit通过
* mobile通过
* no external network
* no artifact code
* Phase 10J/10J-1/10J-2/10J-3不回退
* 其他viewers不回退
* tests通过
* CI通过
* origin/master等于HEAD
* git status clean

---

## 56. PARTIAL_PASS 仅允许

仅允许：

* potential field仅正式支持`local_potential`，没有来源明确的`electrostatic_potential`
* profiles作为前端Worker typed model而非持久化artifact，但hash/provenance/reference完整
* explicit constant user shift未实现，但source-native、cell-average-zero和selected-point-zero完整
* profile ↔ 3D只支持nearest plane而非continuous marker
* non-periodic CUBE potential只支持点采样和表面，不支持periodic profile假设
* mobile一次只显示一个profile
* WebKit透明排序存在非阻断差异
* npm/Python audit因既有registry问题unavailable，但依赖未变化且审计完整

以下缺失不得PARTIAL_PASS：

* reference/gauge disclosure
* source field immutability
* cell-average-zero
* point sampling
* point difference
* planar profiles
* real LOCPOT Runtime evidence
* browser matrix
* accessibility
* lifecycle

这些缺失必须FAIL。

---

## 57. FAIL 条件

以下任一情况必须FAIL：

* 只是给通用isosurface换标题
* 只增加LOCPOT颜色预设
* 将local potential自动称为electrostatic potential
* 将eV自动称为volt
* reference/gauge未显示
* 自动把minimum或mean设为物理零点
* cell-average-zero被称为vacuum reference
* 自动检测vacuum plateau但无正式合同
* 计算work function但无Fermi/reference artifacts
* 修改source payload
* shift被重复应用
* 切换gauge导致source contour identity无说明地变化
* point sampling使用nearest voxel却称为精确值
* ΔV在constant shift后发生变化
* planar average按错误axis/order计算
* triclinic profile被称为Cartesian z profile
* arbitrary smoothing默认开启
* arbitrary line path可执行
* unknown generic field自动进入Potential Product
* 只有synthetic fixtures，没有Runtime LOCPOT
* artifact控制公式/Worker/shader
* 只有Chromium证据
* browser/API/performance evidence伪造
* skipped写成passed
* Phase 10J-3或其他viewers回退
* CI失败却声明PASS
* git不clean却声明完成

---

## 58. 最终报告格式

完成后必须输出：

# Phase 10J-4 Electrostatic Potential Product Result

## 1. Conclusion

PASS / PARTIAL_PASS / FAIL

## 2. Baseline

* Phase 10J-3 commit
* initial HEAD
* branch
* origin/master
* initial status
* final HEAD
* final status

## 3. Pre-Implementation Audit

* available fields
* LOCPOT semantics
* units
* references
* renderer support
* profile strategy
* selected scope

## 4. Product Model

* schema/type
* dataset binding
* source field
* derived gauges
* profiles
* surface layers
* versions

## 5. Potential Semantics

* local potential
* electrostatic potential
* electric potential vs potential energy
* source definition
* units
* limitations

## 6. Gauge / Reference

* source-native
* source reference
* cell-average-zero
* selected-point-zero
* explicit shift
* provenance
* invariants

## 7. Statistics

* min/max
* mean
* standard deviation
* RMS
* volume integral
* cell average
* units

## 8. Equipotential Surfaces

* source/display isovalues
* presets
* layers
* structure overlay
* mesh hashes
* gauge switching
* clipping

## 9. Point Sampling / Difference

* interpolation
* Cartesian/fractional coordinates
* point A/B
* ΔV
* gauge invariance
* periodic identity

## 10. Planar Profiles

* axis 0
* axis 1
* axis 2
* coordinate semantics
* triclinic behavior
* profile artifacts
* hashes
* linked selection

## 11. Product UI

* header
* gauge controls
* isovalue controls
* profile chart/table
* warnings
* inspector
* desktop
* mobile

## 12. Runtime / API

* Planner
* artifact reuse
* source artifacts
* derived artifacts
* successful cases
* negative cases

## 13. Browser Evidence

* Chromium
* Firefox
* WebKit
* mobile
* screenshots
* console
* network
* product cases
* fallback cases

## 14. Accessibility

* keyboard
* focus
* gauge/reference text
* point difference
* profile table
* linked plane
* screen-reader summary
* reduced motion
* mobile

## 15. Performance / Memory

* payload
* profile calculation
* gauge switching
* point sampling
* isosurface extraction
* mesh/GPU
* cache
* memory
* profile switching
* lifecycle

## 16. Security

* artifact JS
* Worker/WASM
* arbitrary formulas
* external URLs
* shift validation
* profile bounds
* race handling
* errors
* secrets
* dependencies

## 17. Tests

* quantity/unit
* gauge
* invariants
* point sampling
* point difference
* profiles
* linked selection
* UI
* renderer
* accessibility
* browser
* performance
* regressions
* service-backed
* no-skipped

## 18. Evidence

* directory
* Runtime LOCPOT datasets
* source/derived artifacts
* gauge references
* profile references
* screenshots
* logs
* metrics
* hashes
* replay commands

## 19. Files

列出主要implementation、tests、fixtures、runner、evidence、docs和persistent文件。

## 20. Explicitly Deferred

* vacuum-level detection
* work function
* Fermi alignment
* cross-calculation alignment
* defect correction
* macroscopic averaging
* arbitrary slicing/profiles
* electric-field product
* potential decomposition
* volume ray casting
* orbital/wavefunction products

## 21. Checks

* diff
* lock
* dependency tree
* Three.js tree
* frontend tests
* typecheck
* build
* backend tests
* browser runners
* performance runners
* network
* secrets

## 22. Commit / CI

* commit
* HEAD
* CI run
* unit
* frontend
* build
* potential tests
* gauge/profile tests
* browser
* performance
* accessibility
* service-backed
* no-skipped
* origin
* git status

## 23. Readiness

预期：

```text
volumetric contracts: READY
LOCPOT parser: READY
generic isosurface renderer: READY
Charge / Spin Density Product: READY
Local Potential Product: READY
explicit Electrostatic Potential Product: READY when source semantics permit
source/reference disclosure: READY
source-native gauge: READY
cell-average-zero gauge: READY
selected-point-zero gauge: READY
equipotential surfaces: READY
point sampling: READY
point-to-point potential difference: READY
lattice-axis planar profiles: READY
profile ↔ 3D linking: READY
structure overlay: READY
Chromium: READY
Firefox: READY
WebKit: READY
mobile: READY
accessibility: READY
performance: READY
security: READY
automatic vacuum-level detection: NOT_IMPLEMENTED
work-function calculation: NOT_IMPLEMENTED
cross-calculation potential alignment: NOT_IMPLEMENTED
full volumetric analysis platform: PARTIAL_READY
```

## 24. Whether Allowed to Enter Next Phase

可以 / 不可以

只有 Phase 10J-4 完成、current-HEAD CI通过、真实LOCPOT Runtime artifacts、gauge/reference、point difference、planar profiles和 Browser/API/Performance/Security Evidence闭合且git clean后，才允许进入：

```text
Phase 10J-5：ELF / Orbital Volumetric Product
```

现在开始执行。

先读取真实 Phase 10J-3 Result、Phase 10J potential quantity/reference contracts、Phase 10J-1 LOCPOT解析语义、Phase 10J-2 Renderer和当前产品基础设施，输出 Pre-Implementation Audit；然后完成Potential compatibility、source/gauge管理、equipotential surfaces、point sampling、point-to-point difference、三个lattice-axis planar profiles、profile与3D联动、科学警告、真实Browser/API/Performance/Security Evidence、docs、commit和CI闭环。

不得把本阶段扩展为vacuum-level detection、work-function calculation、cross-calculation alignment、defect correction、arbitrary slicing或electric-field product。


---END---

---TASK---
 状态：待处理
 # Phase 10J-5：ELF / Orbital Volumetric Product

进入 Phase 10J-5：ELF / Orbital Volumetric Product。

可以默认以下阶段均已严肃执行、完整验收并通过 current-HEAD CI：

* Phase 10F：Production Structure Viewer
* Phase 10G：Trajectory Contract / Adapter / Viewer / Evidence
* Phase 10H：Phonon Contract / Bands / DOS / Animation
* Phase 10I：Brillouin Zone Contract / Adapter / Renderer / Linked View
* Phase 10J：Volumetric Data Contract
* Phase 10J-1：Volumetric Parser / Adapter
* Phase 10J-2：Isosurface Renderer
* Phase 10J-3：Charge / Spin Density Product
* Phase 10J-4：Electrostatic Potential Product

必须以真实 Phase 10J-4 Result 为基线，记录实际：

* Phase 10J-4 commit
* current HEAD
* branch
* origin/master
* working-tree status
* volumetric schema versions
* ELFCAR parser状态
* PARCHG parser状态
* CUBE quantity-hint状态
* isosurface renderer版本
* browser caps
* CI run
* backend/frontend test counts

不得根据本 prompt 编造 commit、HEAD、轨道身份、积分结果、浏览器版本、测试数量、性能指标或 CI run。

本阶段必须产生真实 ELF / Orbital Volumetric Product、科学语义验证、产品级 UI、Runtime artifact 消费和 Browser/API/Performance/Security Evidence，不是给通用等值面增加两个颜色预设。

---

## 1. 本阶段总目标

实现两个边界清晰、科学语义独立的产品：

```text
ELF Product
+
Orbital / Partial Density Product
```

整体流水线：

```text
ELFCAR / PARCHG / compatible CUBE
        ↓
Phase 10J-1 canonical volumetric fields
        ↓
quantity / unit / source-semantics validation
        ↓
ELF or Orbital Product compatibility
        ↓
field statistics / integral / range validation
        ↓
Phase 10J-2 isosurface extraction
        ↓
structure overlay / surface picking
        ↓
product-specific inspector and warnings
        ↓
browser / performance / accessibility / security evidence
```

本阶段至少必须正式支持：

* ELFCAR-derived ELF field
* explicit `electron_localization_function`
* explicit `orbital_density`
* PARCHG-derived partial/orbital density
* CUBE orbital-density field，只有quantity和source语义明确时
* ELF value-range validation
* orbital-density non-negativity validation
* full-cell field integral
* source normalization disclosure
* orbital/selection identity disclosure
* structure overlay
* exact isovalue/unit display
* isosurface picking
* product-specific inspector
* PNG export
* real Runtime artifact evidence
* Chromium / Firefox / WebKit / mobile evidence

---

## 2. Minimum PASS Scope

PASS至少要求以下能力完整。

### 2.1 ELF Product

* 使用真实 Phase 10J-1 ELFCAR Runtime artifact。
* `quantity = electron_localization_function`。
* `unit = dimensionless`。
* source-native field不可修改。
* range validation完成。
* exact ELF isovalue显示。
* ELF等值面和结构叠加完成。
* full-cell statistics完成。
* product warnings完整。
* 不自动作成键、孤对电子或原子壳层分类。

### 2.2 Orbital / Partial Density Product

* 使用真实 Phase 10J-1 PARCHG或来源明确的CUBE Runtime artifact。
* field quantity明确。
* field unit明确。
* normalization/integral semantics明确。
* source selection metadata尽可能保留。
* 正值等值面完成。
* field integral完成。
* 不自动称为单电子概率密度。
* 不自动称为某个具体轨道，除非有权威轨道身份。

### 2.3 Evidence

正式主证据必须包含：

* real Runtime artifacts
* real binary payloads
* real Phase 10J-2 mesh extraction
* real structure/atom context
* browser matrix
* performance and lifecycle evidence

不得只使用synthetic sphere、Gaussian blob或手写mesh宣称产品完成。

---

## 3. Scientific Product Separation

必须严格区分以下概念。

### 3.1 Electron Localization Function

```text
quantity = electron_localization_function
```

ELF是无量纲标量场。

通常取值接近：

```text
0 <= ELF <= 1
```

但合同和UI必须允许dtype/算法产生的微小数值越界，并使用scale-aware tolerance。

不得仅凭高ELF值自动宣称：

* 存在共价键
* 存在孤对电子
* 存在电子对
* 存在核心电子壳层
* 存在某类化学键
* 存在吸引子或盆地

这些结论需要独立拓扑分析和化学解释。

### 3.2 Orbital Density

```text
quantity = orbital_density
```

表示来源明确的非负标量密度。

不得默认等同于：

```text
|ψ|²
```

除非source contract明确如此声明。

不得默认其full-cell integral为：

```text
1
```

或：

```text
orbital occupancy
```

必须以source normalization和authoritative metadata为准。

### 3.3 Partial Charge Density

PARCHG可能表示：

* 单个band/k-point选择
* 多band组合
* 多k-point组合
* 某个能量窗口
* 某种投影选择
* source-defined partial density

不得仅凭文件名将其称为：

```text
orbital n
```

如果合同没有独立`partial_charge_density` quantity，可：

* 保持正式`orbital_density`或source-native quantity；
* 保存`source_selection_kind`；
* 显示“source-defined partial density”；
* 避免更强的轨道身份声明。

### 3.4 Signed Orbital Amplitude

带正负号的实轨道振幅与轨道密度不是同一quantity。

除非已有正式合同和source明确声明：

```text
quantity = real_orbital_amplitude
```

否则本阶段不得将signed scalar CUBE自动解释为轨道振幅。

---

## 4. Complex Wavefunction Boundary

本阶段不得从complex scalar field自动生成：

```text
real(ψ)
imag(ψ)
|ψ|
|ψ|²
phase(ψ)
```

也不得把complex field的real part交给通用isosurface而称为轨道。

以下保持deferred：

* complex wavefunction product
* wavefunction phase
* phase-colored isosurfaces
* nodal-phase product
* gauge/phase alignment
* Bloch phase
* k-point wavefunction reconstruction
* real-space orbital reconstruction
* linear combinations of orbitals
* Wannier functions

未来如需支持，必须建立正式derived-field合同和phase/gauge语义。

---

## 5. Signed Real Orbital Field Optional Scope

如果仓库真实合同已经正式支持来源明确的实值signed orbital amplitude，本阶段可以增加：

* positive amplitude surface
* negative amplitude surface
* symmetric threshold lock
* sign legend
* nodal surface提示
* exact source normalization
* source phase/sign convention

但必须明确：

* 正负号是振幅符号，不是正负电荷。
* 全局符号翻转不改变密度。
* 不得根据颜色称为电子/空穴。
* 不得将振幅积分解释为电子数。
* 不得将正负lobes自动命名为成键/反键。

如果合同和真实source不支持，则：

```text
SIGNED_ORBITAL_AMPLITUDE = DEFERRED_BY_DESIGN
```

不影响ELF和orbital-density产品PASS。

---

## 6. 本阶段明确禁止

不得实现或宣称：

* ELF basin analysis
* ELF attractor detection
* bond basin classification
* lone-pair basin classification
* core basin classification
* localization topology
* critical-point analysis
* gradient vector field
* Hessian field
* Laplacian field
* Bader analysis
* atomic charge
* charge partitioning
* orbital reconstruction
* wavefunction reconstruction
* complex phase rendering
* Bloch phase
* arbitrary orbital linear combinations
* HOMO/LUMO identification without authoritative electronic artifact
* molecular-orbital energy calculation
* band calculation
* orbital energy calculation
* occupancy inference
* k-point inference
* spin inference from filename
* automatic orbital naming
* automatic `s/p/d/f` character assignment
* automatic bonding/antibonding classification
* automatic lone-pair identification
* automatic nodal-plane classification
* arbitrary field subtraction
* arbitrary field addition
* arbitrary field multiplication
* arbitrary normalization
* smoothing
* denoising
* resampling
* volume ray casting
* arbitrary slices
* arbitrary line profiles
* external DFT
* VASP execution
* Gaussian execution
* arbitrary Python
* notebook execution
* uploaded script execution
* artifact JavaScript
* artifact Worker code
* artifact WASM
* artifact shader
* artifact HTML/CSS
* arbitrary expression
* external URL
* CDN
* remote assets
* production mesh export

---

## 7. Public Tool 与产品身份

继续使用：

```text
structure.volumetric_data
```

优先不新增公开计算Tool。

正确架构：

```text
structure.volumetric_data
        ↓
validated ELFCAR / PARCHG / CUBE artifacts
        ↓
application-owned ELF / Orbital Product
```

不得注册语义重叠的：

```text
structure.elf
structure.parchg
structure.orbital_density
structure.orbital_viewer
```

如果必须生成正式product manifest或derived product artifact，可新增内部派生步骤，但不得成为新的主要用户入口。

如确实需要公开Tool，建议唯一候选：

```text
structure.elf_orbital_product
```

但必须满足：

* 只消费validated volumetric artifacts。
* 不重新解析source。
* 不执行DFT。
* 不重构轨道。
* 不计算复波函数。
* strict params。
* 只生成inert product metadata。
* 进入Registry、PlanValidator、Runtime和evidence。
* Pre-Implementation Audit说明必要性。

推荐不新增公开Tool。

---

## 8. Baseline Verification

首先执行：

```bash
cd "E:\1project\Material Data Intelligence"

git status --short
git branch --show-current
git rev-parse HEAD
git log --oneline -45
git remote -v
git rev-parse origin/master
```

必须确认：

* repository正确
* branch为`master`
* working tree clean
* HEAD包含Phase 10J-4
* origin/master正确
* ELFCAR Parser已实现
* PARCHG Parser已实现
* CUBE Parser已实现
* canonical volumetric fields存在
* generic Isosurface Renderer已实现
* Charge/Spin和Potential产品未修改source字段语义
* current-HEAD CI成功

如果working tree不干净，停止并报告，不得覆盖未知修改。

---

## 9. 必读实现

### 9.1 Phase 10J Contracts

必须阅读：

* quantity enums
* `electron_localization_function`
* `orbital_density`
* `wavefunction`
* field rank/value kind
* units
* normalization
* integral semantics
* source relationships
* derived-field provenance
* structure binding
* payload hashes
* caps
* security

### 9.2 Phase 10J-1 ELFCAR / PARCHG / CUBE Parser

必须阅读：

* ELFCAR field mapping
* ELFCAR source units
* ELFCAR channel behavior
* PARCHG quantity mapping
* PARCHG source normalization
* PARCHG selection metadata
* source filename处理
* CUBE quantity-hint policy
* CUBE orbital/multi-dataset support
* source-order conversion
* parser/provider versions
* augmentation/extra-section policy

### 9.3 Phase 10J-2 Renderer

必须复用：

* compatibility validator
* payload loader
* Worker extraction
* periodic halo
* triclinic coordinates
* positive/negative layers
* structure overlay
* picking
* inspector
* clipping
* PNG export
* lifecycle
* browser caps

不得创建第二套marching-cubes或Three.js renderer。

### 9.4 Existing Product Infrastructure

必须阅读并复用：

* Charge/Spin Product manifest
* Potential Product manifest
* source/derived field distinction
* product routing
* product warnings
* exact units/isovalues
* artifact cache
* accessibility tables
* mobile layout
* browser evidence runners

---

## 10. 修改前必须输出审计

修改代码前输出：

# Phase 10J-5 ELF / Orbital Product Pre-Implementation Audit

## 1. Baseline

* Phase 10J-4 commit
* HEAD
* branch
* origin/master
* git status
* CI
* schema versions
* renderer version

## 2. Available Fields

列出真实可用：

* ELFCAR fields
* PARCHG fields
* CUBE orbital fields
* quantities
* units
* normalization
* integral semantics
* source identities
* spin/channel metadata
* multi-dataset状态

## 3. ELF Semantics

明确：

* source field定义
* value range
* unit
* channels
* parser是否转换
* source/provider
* 可以和不可以作出的科学结论

## 4. Orbital / PARCHG Semantics

明确：

* field究竟表示什么
* source selection metadata
* band/k-point/spin identity是否存在
* occupancy是否存在
* integral如何解释
* 是否为source-defined partial density
* 是否可称为single orbital

## 5. CUBE Semantics

明确：

* quantity hint来源
* multi-orbital支持
* orbital IDs
* units
* normalization
* signed/unsigned field区别
* atom context

## 6. Existing Renderer Support

* positive surfaces
* signed paired surfaces
* structure overlay
* picking
* inspector
* export
* missing product能力

## 7. Selected Product Strategy

明确：

* ELF产品模型
* orbital产品模型
* identity metadata
* range/non-negativity validation
* integral policy
* presets
* signed amplitude是否支持
* product manifest策略

## 8. Scope Boundary

明确不实现：

* complex phase
* orbital reconstruction
* ELF topology
* HOMO/LUMO推断
* arbitrary field arithmetic
* quantum calculation

## 9. Planned Files

列出implementation、tests、fixtures、runner、evidence、docs和persistent预计变更。

审计完成后直接实施，不等待人工确认。

---

## 11. Product Compatibility Validator

产品初始化前必须验证：

* dataset schema
* grid schema
* field schema
* payload schema
* manifest
* field/grid/payload hashes
* structure binding
* lattice binding
* quantity
* unit
* normalization
* integral semantics
* source selection metadata
* field rank
* value kind
* component count
* sample location
* endpoint policy
* finite values
* browser caps
* security flags

ELF Product正式接受：

```text
quantity = electron_localization_function
value_kind = real
field_rank = scalar
component_count = 1
unit = dimensionless
```

Orbital Density Product正式接受：

```text
quantity = orbital_density
value_kind = real
field_rank = scalar
component_count = 1
```

Generic scalar不得自动进入这些产品。

---

## 12. ELF Range Validation

必须计算：

* minimum
* maximum
* below-zero count
* above-one count
* maximum lower violation
* maximum upper violation
* dtype
* scale-aware tolerance

建议状态：

```text
VALID_RANGE
NUMERIC_TOLERANCE_WARNING
SOURCE_RANGE_ANOMALY
INVALID_NON_FINITE
```

### 12.1 Tolerance

不得使用一个未版本化的固定magic number。

Tolerance应考虑：

* stored dtype
* field range
* parser conversion
* contract tolerance policy

### 12.2 No Clamping

禁止：

```text
ELF = clamp(ELF, 0, 1)
```

不得为了显示修正source values。

轻微越界：

* 保留source value
* 显示warning
* slider可按主要有效range限制，但exact input仍显示异常值状态

显著越界：

* 产品进入scientific anomaly状态
* 可保留generic isosurface
* 不得声称ELF validation PASS

---

## 13. ELF Interpretation Boundary

产品必须显示：

> ELF等值面仅表示选定ELF数值的空间集合，不自动构成化学键、孤对电子、电子盆地或原子壳层判定。

不得自动输出：

* “此处为共价键”
* “发现孤对电子”
* “该原子具有多少孤对电子”
* “该键为离子键/金属键”
* “ELF盆地电子数”
* “ELF临界点”
* “键级”

允许显示：

* selected ELF value
* position
* nearest atoms/distances
* structure context
* source field statistics

Nearest-atom信息不得升级为拓扑归属。

---

## 14. ELF Visualization Presets

必须提供确定性、明确数值的显示预设。

可以使用：

```text
0.50
0.70
0.80
0.90
```

或由真实Phase审计决定的受控集合。

每个preset必须显示：

* exact value
* dimensionless unit
* preset ID
* preset version
* no automatic chemical interpretation

不得只显示：

```text
bonding
lone pair
core
```

作为科学预设名称。

允许中性名称：

* Low ELF
* Medium ELF
* High ELF
* Very High ELF

但UI必须显示exact numeric value。

---

## 15. ELF Layers

默认只显示一个ELF等值面。

允许bounded多层：

* max layers服从Phase 10J-2 cap
* each layer exact value
* deterministic visual distinction
* bounded opacity
* structure overlay
* selected layer identity

不得默认叠加大量层造成误导和性能问题。

ELF为非负field，不应默认生成负等值面。

---

## 16. Orbital / Partial Density Quantity

产品必须显示正式来源名称。

允许状态：

```text
orbital_density
source_defined_partial_density
orbital_density_with_explicit_identity
```

实际enum必须服从真实合同。

### 16.1 Identity Levels

必须定义结构化identity completeness：

```text
FULL
PARTIAL
UNAVAILABLE
```

可能metadata包括：

* source field ID
* source file hash
* source format
* orbital ID
* dataset/orbital index
* band index
* k-point index
* k-point coordinate
* spin channel
* occupancy
* energy
* projection selection
* energy window
* band range
* k-point range
* source comment
* parser/provider version

### 16.2 Authority

只有以下可作为正式identity：

* source file正式metadata
* parser明确解析的orbital IDs
* upstream electronic artifact binding
* explicit resource metadata with validated provenance
* synthetic fixture identity

不得使用：

* filename字符串
* 用户随意文件名
* LLM猜测
* 文件顺序推断
* 颜色
* isosurface形状
* 原子种类
* visual orbital形状

---

## 17. Orbital Naming

如果完整identity不可用，UI必须使用：

```text
Source-defined partial density
```

或：

```text
Orbital-density field <stable-id>
```

不得显示：

```text
HOMO
LUMO
d_z2
p_x
bonding orbital
antibonding orbital
```

除非权威metadata明确提供。

如果source提供band/k-point，只显示：

```text
band 12, k-point 3, spin up
```

不得自动映射为HOMO/LUMO。

---

## 18. Orbital Density Non-Negativity

对于明确`orbital_density`：

* 计算minimum。
* 使用dtype/scale-aware tolerance。
* 微小负值显示numeric warning。
* 显著负值显示scientific anomaly。
* 不自动clamp。
* 不自动取absolute value。
* 不自动square。

对于source-defined signed orbital amplitude：

* 不执行non-negative validation。
* 必须进入不同产品mode。
* 正负号语义必须明确。

---

## 19. Orbital Integral

必须计算：

```text
I = Σ rho_orbital(i,j,k) * voxel_volume
```

并显示：

* value
* unit
* normalization semantics
* source reference，若存在
* residual
* authority state

不得默认将其解释为：

* occupancy
* electron count
* probability 1
* number of electrons in an orbital

只有source artifact明确声明：

```text
integral_semantics = electron_count
```

或：

```text
normalized_to_unit_integral
```

时，才能作对应解释。

---

## 20. Orbital Occupancy

如果source metadata包含occupancy：

* 显示source occupancy
* 显示field integral
* 显示两者是否可比较
* 保存单位和normalization
* 计算residual only if semantics compatible

不得在以下情况下比较：

* density未归一化
* k-point weight未知
* 多band组合
* 多k-point组合
* source selection不明
* spin degeneracy不明
* augmentation或projection贡献不明

不得为匹配occupancy而renormalize field。

---

## 21. PARCHG Source Selection

必须保存Phase 10J-1能够解析或绑定的选择信息：

* band selection
* k-point selection
* spin channel
* atom/projection selection，若存在
* energy window，若存在
* source-native comments
* selection completeness

如果PARCHG自身不包含足够身份：

* 明确`identity unavailable`
* 不使用filename补全
* 不阻止generic orbital-density可视化
* 阻止HOMO/LUMO/band-specific claims

---

## 22. CUBE Orbital Product

CUBE只有在以下条件之一满足时进入Orbital Product：

* source正式multi-orbital IDs被解析；
* quantity hint由受信任Plan/resource metadata明确给出；
* upstream artifact明确绑定；
* synthetic fixture明确声明。

不得仅根据`.cube`扩展名进入Orbital Product。

### 22.1 Multi-Orbital CUBE

如果Phase 10J-1已正式支持：

* bounded orbital list
* stable orbital IDs
* shared grid
* one field per orbital
* deterministic order
* field selector
* no simultaneous unlimited loading

如果Phase 10J-1 typed拒绝multi-orbital CUBE，则本阶段继续：

```text
MULTI_ORBITAL_CUBE = DEFERRED_BY_DESIGN
```

不得静默只显示第一轨道。

---

## 23. Source-Native Field Preservation

ELF和orbital source fields必须immutable。

不得：

* clamp
* normalize
* smooth
* rescale
* take square root
* square
* take absolute value
* subtract mean
* change units without记录
* overwrite source field ID

任何显示派生必须：

* 使用allowlisted derived operation；
* 有source hash；
* 有formula/version；
* 有derived identity；
* 不修改source artifact。

本阶段默认不需要生成新的科学derived field。

---

## 24. Product Manifest

建议新增：

```text
elf_orbital_product.v1
```

也可以拆分为：

```text
elf_product.v1
orbital_volumetric_product.v1
```

优先根据现有产品manifest模式选择，避免重复。

至少包含：

* product kind
* dataset binding
* source field binding
* quantity
* units
* normalization
* integral semantics
* source identity
* orbital-selection identity
* identity completeness
* range validation
* source/reference integrals
* active isosurface layers
* exact isovalues
* structure binding
* renderer capabilities
* scientific limitations
* security
* provenance

不得包含：

* JavaScript
* arbitrary formulas
* shader
* callback
* external URL
* camera script
* arbitrary HTML

---

## 25. Product UI

建议布局：

```text
┌─────────────────────────────────────────────┐
│ ELF / Orbital Header and Scientific Status  │
├──────────────────────┬──────────────────────┤
│ Field / Identity     │ 3D Isosurface        │
│ Isovalue Controls   │ + Structure           │
├──────────────────────┴──────────────────────┤
│ Statistics / Inspector / Warnings           │
└─────────────────────────────────────────────┘
```

### 25.1 ELF Header

显示：

* Electron Localization Function
* source format
* field ID
* structure/formula
* dimensionless
* value range
* validation state
* parser/provider
* no-topology-analysis warning

### 25.2 Orbital Header

显示：

* Orbital Density或Source-Defined Partial Density
* source format
* field ID
* identity completeness
* orbital/band/k-point/spin metadata，若存在
* units
* normalization
* integral semantics
* no-HOMO/LUMO-inference warning

---

## 26. Field / Dataset Selector

如果dataset包含多个compatible fields：

* stable field IDs
* bounded options
* exactquantity
* source identity
* spin/channel labels
* lazy payload loading
* field switch cancellation
* stale mesh cleanup
* current selection reset

不得同时加载所有大payload。

对于CUBE multi-orbital：

* selector显示orbital ID
* 不按文件位置生成不稳定名称
* 不使用display label作为scientific identity

---

## 27. Isovalue Controls

ELF：

* exact numeric input
* bounded slider
* dimensionless
* presets
* reset
* layer visibility
* opacity

Orbital density：

* exact numeric input
* field unit
* low/medium/high display heuristics
* reset
* layer visibility
* opacity

Signed orbital amplitude，若支持：

* symmetric positive/negative lock
* exact sign
* no density claim
* no charge-sign claim

所有controls必须拒绝：

* NaN
* Infinity
* arbitrary expression
* code
* unitless interpretation when unit exists

---

## 28. Default Isovalue Strategy

### 28.1 ELF

默认可以使用固定、显式的中性值，例如：

```text
0.70
```

但必须：

* versioned preset
* exact value显示
* no automatic bonding claim
* 若field range不覆盖则选择安全可见值并显示原因

### 28.2 Orbital Density

使用deterministic display heuristic：

* bounded quantile，或
* `min + fraction * (max-min)`

必须显示：

* exact value
* unit
* heuristic ID/version
* no normalization claim

不得自动选择使表面“看起来像轨道”的阈值。

---

## 29. Structure Overlay

必须验证：

* structure hash
* lattice hash
* grid hash
* coordinate frame
* origin
* periodicity
* source cell
* atom positions

支持：

* atoms
* bonds
* unit cell
* axes
* bounded supercell

### 29.1 ELF

nearest atoms可以作为空间上下文显示，但不得将surface分配给某个原子或化学键。

### 29.2 Orbital Density

surface形状不得自动归属为：

* 原子轨道
* 分子轨道
* 键轨道
* 某元素的d轨道

除非source identity正式提供。

---

## 30. Surface Picking

Surface pick至少包含：

```text
ElfOrbitalSurfacePick {
  productKind,
  fieldId,
  sourceIdentity,
  layerId,
  isovalue,
  unit,
  cartesianPosition,
  fractionalPosition?,
  periodicImageOffset?,
  interpolatedFieldValue,
  meshHash
}
```

必须使用validated trilinear interpolation。

不得用nearest voxel并称为精确值。

---

## 31. ELF Inspector

必须显示：

* field ID
* source format
* parser/version
* dimensionless
* selected ELF isovalue
* interpolated ELF value
* Cartesian coordinate
* fractional coordinate
* periodic image
* field min/max/mean
* range validation
* nearest atoms/distances，可选
* explicit interpretation warning

不得显示：

* bond type
* lone-pair count
* basin population
* atomic assignment

---

## 32. Orbital Inspector

必须显示：

* field ID
* product quantity
* source format
* source/partial-density identity
* identity completeness
* band index，若权威
* k-point index/coordinate，若权威
* spin channel，若权威
* orbital/dataset ID，若权威
* occupancy，若权威
* energy，若权威
* projection selection，若权威
* selected isovalue
* unit
* interpolated value
* full-cell integral
* normalization
* structure binding
* mesh hash

不得根据surface附近原子自动显示轨道字符。

---

## 33. Integral / Statistics Panel

### 33.1 ELF

显示：

* min
* max
* mean
* standard deviation
* RMS
* below-zero count
* above-one count
* range residuals
* volume integral

ELF volume integral不得自动解释为：

* 电子数
* 键电子数
* basin population

### 33.2 Orbital Density

显示：

* min
* max
* mean
* RMS
* integral
* source reference
* residual
* normalization semantics
* negative-value count
* identity completeness

### 33.3 Signed Amplitude Optional

显示：

* min/max
* positive/negative range
* mean
* norm-related data only if source contract supports
* 不显示电子数积分

---

## 34. No Enclosed-Volume Interpretation

等值面所包围区域不得自动产生：

* enclosed electron count
* enclosed probability
* orbital occupancy
* ELF basin population
* atomic contribution

本阶段不实现surface-interior体积分。

UI必须避免：

```text
electrons inside surface
```

之类措辞。

---

## 35. Product Presets

ELF presets必须中性，例如：

```text
ELF 0.50
ELF 0.70
ELF 0.80
ELF 0.90
```

Orbital-density presets可命名：

* Low contour
* Medium contour
* High contour

每个preset必须包含：

* exact isovalue
* unit
* source field hash
* heuristic/preset version
* no scientific classification

不得命名：

* bonding
* antibonding
* lone pair
* core
* valence orbital
* HOMO
* LUMO

除非来源身份正式明确且名称仅反映source metadata。

---

## 36. Product Routing

完成后，以下请求应路由到：

```text
structure.volumetric_data
+
ELF / Orbital Volumetric Product
```

正向ELF示例：

* 显示这个ELFCAR的ELF等值面
* 查看电子局域函数
* 用0.8的ELF等值面显示结构
* Visualize the ELF from this ELFCAR
* Show an ELF isosurface at 0.7

正向Orbital示例：

* 显示这个PARCHG的部分电荷密度
* 可视化这个轨道密度CUBE
* 查看这个源定义的部分密度
* Show the orbital-density isosurface
* Visualize the partial charge density from this PARCHG

### 36.1 Ambiguous Requests

例如：

* 显示轨道
* 查看HOMO
* 显示LUMO

如果没有权威电子结构identity：

* 不得选择某个field猜测。
* 返回identity不足。
* 可以展示可用field列表。
* 不得将任意PARCHG称为HOMO/LUMO。

### 36.2 Negative Routing

不得声称支持：

* 判断成键类型
* 找孤对电子
* 计算ELF盆地
* 计算轨道
* 运行DFT
* 生成HOMO/LUMO
* 重构波函数
* 显示复相位
* 组合两个轨道
* 对轨道做线性组合
* 做Bader分析
* 计算轨道占据数
* 任意Python处理

---

## 37. Artifact Reuse

如果ELFCAR/PARCHG/CUBE已解析：

* 必须复用validated dataset。
* 不重复解析。
* 不复制source payload。
* mesh按field hash + isovalue缓存。
* field selector按需加载。
* source artifact保持immutable。
* 切换产品不得重新执行source Tool。

不得为打开ELF产品重新运行ELFCAR parser。

---

## 38. API / Runtime Evidence

至少覆盖：

### Case A：Valid ELFCAR

* real Runtime artifact
* dimensionless
* range validation
* ELF surface
* structure overlay

### Case B：ELF Minor Numeric Excursion

* slight below-zero或above-one
* warning
* no clamping
* exact source value preserved

### Case C：ELF Major Anomaly

* product scientific warning/failure
* generic viewer fallback，若允许
* no false PASS

### Case D：PARCHG Partial Density

* source-defined identity
* unit/normalization
* integral
* positive surface
* no single-orbital claim

### Case E：PARCHG with Explicit Selection Metadata

* band/k-point/spin metadata
* identity completeness
* field selector/inspector

### Case F：CUBE Orbital Density

* explicit trusted quantity
* atom context
* non-periodic grid
* orbital identity or explicit unavailable state

### Case G：Ambiguous Generic CUBE

* generic isosurface remains available
* Orbital Product refused
* typed reason

### Case H：Signed Real Field

* optional supported mode，或
* explicit typed unsupported
* no silent squaring/absolute value

记录sanitized：

* plan
* job
* tool call
* dataset
* field hashes
* source identity
* quantity
* units
* normalization
* integrals
* range validation
* mesh hashes
* product state

---

## 39. Real Evidence Requirement

正式主证据必须包含：

* 真实Phase 10J-1 ELFCAR Runtime artifact
* 真实Phase 10J-1 PARCHG或source-defined orbital-density Runtime artifact
* 真实Phase 10J-2 Worker mesh
* 真实structure overlay
* source/parser provenance
* scientific warnings

Synthetic fixtures只允许用于：

* exact ELF range cases
* integral references
* identity completeness
* signed-amplitude optional tests
* caps/security
* malformed metadata

---

## 40. Performance Strategy

必须避免：

* 同时加载所有orbital fields。
* 每次field切换重新解析source。
* 每次isovalue变化重新加载payload。
* 同时缓存无限多个轨道mesh。
* 将所有multi-orbital CUBE数据常驻主线程。
* idle持续render。

优先：

* lazy field loading
* bounded field-buffer cache
* bounded mesh cache
* hash-keyed identity
* Worker持有current field
* field switch cancellation
* stale mesh rejection
* one canvas/context
* render-on-demand

---

## 41. Product Caps

除Phase 10J-2 caps外，必须增加：

* max ELF fields per dataset
* max orbital fields per dataset
* max identity metadata entries
* max simultaneously loaded orbital payloads
* max cached orbital payloads
* max cached meshes
* max active surfaces
* max source comment bytes
* max selection metadata bytes
* max orbital label length
* max field-selector options rendered
* max product manifest bytes

Multi-orbital dataset超过UI cap时必须提供bounded paging/virtualization或typed refusal。

不得一次创建数千个DOM option和payload fetch。

---

## 42. Performance Metrics

至少记录：

* source format
* field count
* payload bytes
* active payload buffers
* field load time
* field-switch latency
* range validation time
* integral time
* isosurface extraction time
* mesh vertices/triangles
* mesh/GPU bytes
* selector render cost
* picking latency
* PNG export time
* cache entries
* cache eviction
* browser memory estimate
* canvas/context/Worker count
* artifact-switch cleanup

---

## 43. Required Performance Cases

至少覆盖：

1. small ELFCAR
2. moderate ELFCAR
3. ELF multi-isovalue switching
4. PARCHG single field
5. PARCHG with explicit identity metadata
6. multi-field orbital dataset，若支持
7. rapid field switching
8. rapid isovalue changes
9. triclinic periodic field
10. non-periodic CUBE field
11. near-browser-cap field
12. repeated artifact switching
13. mobile field switching
14. context loss/restore

---

## 44. Browser Evidence Matrix

必须在真实：

* Chromium
* Firefox
* WebKit
* mobile viewport

验证：

* ELF Product detection
* exact dimensionless unit
* ELF range validation
* ELF presets
* exact isovalue
* PARCHG Product detection
* orbital/partial-density identity
* identity unavailable state
* field selector
* unit/normalization
* integral
* structure overlay
* surface picking
* inspector
* supercell
* clipping
* PNG export
* ambiguous quantity fallback
* signed field boundary
* lifecycle
* console
* network

---

## 45. Required Screenshots

至少保存：

1. ELF Product header
2. ELF 0.70 surface
3. ELF exact range/statistics
4. ELF minor range warning
5. ELF interpretation warning
6. ELFCAR structure overlay
7. PARCHG Product header
8. source-defined partial density surface
9. orbital identity completeness
10. band/k-point/spin metadata，若存在
11. identity unavailable state
12. orbital-density integral panel
13. selected ELF surface inspector
14. selected orbital surface inspector
15. field selector
16. non-periodic CUBE orbital density
17. ambiguous CUBE fallback
18. signed-amplitude optional state或deferred状态
19. clipping
20. accessibility field/statistics table
21. mobile portrait
22. mobile landscape
23. PNG export

每张截图记录：

* browser/version
* viewport
* deviceScaleFactor
* dataset hash
* field hash
* product kind
* quantity
* unit
* source identity
* identity completeness
* isovalue
* range/integral status
* mesh hash
* camera
* screenshot hash

---

## 46. Accessibility

必须支持：

* semantic product selector
* semantic field selector
* exact isovalue
* exact unit
* ELF range status
* source identity completeness
* normalization/integral text
* keyboard layer controls
* surface selection
* visible focus
* screen-reader field summary
* accessible field list
* accessible statistics table
* scientific warnings
* no color-only state
* reduced motion
* mobile touch targets

Canvas外必须提供：

* field identity
* quantity
* unit
* source selection metadata
* range validation
* statistics
* integral
* active surfaces
* selected spatial value
* interpretation limitations

---

## 47. Mobile

必须验证：

* product header
* ELF/orbital mode
* field selector
* exact isovalue
* preset selector
* range/integral panel
* structure toggle
* clipping
* surface picking
* inspector drawer
* identity metadata
* warnings
* no horizontal overflow
* Worker cancellation
* context lifecycle

移动端允许：

* 一次只加载一个field
* 更低voxel/triangle cap
* 更少active layers
* 更低pixel ratio
* 禁用大supercell
* 降低PNG分辨率
* field selector虚拟化

不得隐藏quantity、normalization、identity completeness或科学警告。

---

## 48. Security

必须验证：

* no artifact JavaScript
* no artifact Worker/WASM
* no artifact shader
* no artifact HTML/CSS
* no external URLs
* no remote assets
* no iframe
* no eval
* no Function constructor
* no arbitrary field expression
* no arbitrary orbital combination
* no arbitrary normalization
* no arbitrary quantity override
* no filename-derived authority
* bounded identity metadata
* bounded field list
* finite values
* overflow-safe counts
* stale-worker result protection
* source field immutable
* no local path
* no signed URL disclosure
* no token
* no secret
* redacted errors
* safe export filename

必须输出：

```text
NO_ELF_ORBITAL_PRODUCT_EXTERNAL_NETWORK_REQUESTS
```

以及：

```text
NO_SECRET_PATTERN_HITS
```

---

## 49. Dependency Policy

优先不新增依赖。

复用：

* Phase 10J validators
* Phase 10J-2 Worker
* existing Three.js
* existing payload loader
* existing statistics
* existing product UI
* existing artifact cache

不得为轨道识别引入量子化学计算库。

如果新增依赖：

* 说明必要性
* version
* license
* browser/Worker compatibility
* bundle size
* transitive dependencies
* security findings
* deterministic behavior
* lockfile变化

不得提前引入波函数、Wannier或量子化学重型依赖。

---

## 50. Independent Scientific Reference Tests

### 50.1 ELF

覆盖：

* all-zero
* all-one
* constant 0.5
* valid varying field
* slight negative noise
* slight above-one noise
* significant negative
* significant above-one
* NaN/Infinity rejection
* triclinic grid
* shifted origin

### 50.2 Orbital Density

覆盖：

* normalized constant field
* non-normalized field
* knownintegral
* small negative numerical noise
* significant negative anomaly
* source reference absent
* source occupancy compatible
* source occupancy incompatible
* multi-field identity

### 50.3 Identity

覆盖：

* full metadata
* partial metadata
* no metadata
* conflicting metadata
* filename-only metadata rejected
* duplicate orbital IDs
* invalid k-point index
* invalid spin label
* oversized source comments

### 50.4 Signed Amplitude Optional

如支持：

* positive/negative lobes
* global sign inversion
* symmetric threshold
* zero nodal plane
* no density/electron integral claim

---

## 51. Product / Manifest Tests

必须覆盖：

* ELF product manifest
* orbital product manifest
* dataset binding
* field hash
* source identity
* identity completeness
* quantity/unit
* normalization
* integral semantics
* range validation
* exact isovalues
* structure binding
* security
* deterministic replay
* manifest hash
* source immutability

---

## 52. Frontend Tests

至少覆盖：

* product detection
* ELF compatibility
* orbital compatibility
* generic-field rejection
* ELF range status
* ELF presets
* exact isovalue
* orbital identity
* identity unavailable
* multi-field selector
* normalization/integral
* structure overlay
* picking
* inspector
* clipping
* supercell
* PNG export
* ambiguous CUBE fallback
* signed amplitude optional/deferred
* keyboard
* accessibility
* mobile
* lifecycle
* no duplicate canvas/context/Worker
* no stale field/mesh

不得只测试控件存在。

---

## 53. Regression Tests

必须保持：

* Phase 10J contracts
* Phase 10J-1 ELFCAR Parser
* Phase 10J-1 PARCHG Parser
* Phase 10J-1 CUBE Parser
* payload hashes
* Phase 10J-2 Isosurface Renderer
* Phase 10J-3 Charge/Spin Product
* Phase 10J-4 Potential Product
* structure viewer
* trajectory viewer
* phonon viewer
* BZ viewer
* Band–BZ linked view
* Tool Registry
* Planner
* PlanValidator
* QueueWorkerRuntime
* service-backed integration
* Phase 10 Closure Regression Pack
* no-skipped assertion

不得为产品方便修改ELFCAR/PARCHG source-native语义。

---

## 54. Evidence Directory

建议新增：

```text
docs/phase10j/evidence/phase10j5_elf_orbital_product/
```

至少包含：

* README
* pre-implementation audit
* real Runtime ELFCAR dataset
* real Runtime PARCHG/orbital dataset
* source field artifacts
* product manifests
* compatibility outputs
* ELF range validation
* orbital integral references
* source identity records
* identity completeness evidence
* browser matrix
* screenshots
* console logs
* network logs
* performance metrics
* memory estimates
* lifecycle metrics
* accessibility audit
* mobile audit
* PNG exports
* ambiguous/fallback cases
* security audit
* dependency audit
* secret scan
* CI record
* replay commands

不得提交：

* secrets
* private paths
* proprietary productionELFCAR/PARCHG
* browser profiles
* caches
* node_modules
* videos
* external assets
* oversized source files

---

## 55. Documentation

新增或更新：

* Phase 10J-5 overview
* ELF scientific semantics
* ELF range
* ELF visualization limits
* no-topology-analysis boundary
* orbital density vs partial density
* orbital density vs signed amplitude
* source orbital identity
* identity completeness
* PARCHG semantics
* CUBE orbital semantics
* normalization/integral
* occupancy comparison policy
* visualization presets
* structure overlay
* picking/inspector
* accessibility
* mobile
* performance
* security
* known limitations
* next-phase handoff

更新：

* `docs/index.md`
* `persistent/DESIGN_PROGRESS.md`
* `persistent/TASK_BOARD.md`
* `persistent/CHANGELOG.md`
* `persistent/OPEN_QUESTIONS.md`
* `persistent/TOOL_REGISTRY_NOTES.md`
* `persistent/ARCHITECTURE_DECISIONS.md`

ADR至少记录：

1. ELF等值面不等于ELF拓扑分析。
2. ELF值不得静默clamp到`[0,1]`。
3. PARCHG不得仅凭文件名获得轨道身份。
4. Orbital density不得默认归一化为1或occupancy。
5. Partial density不得自动称为single orbital。
6. Signed orbital amplitude与orbital density严格分离。
7. 本阶段不从complex wavefunction派生`|ψ|²`。
8. 本阶段不自动识别HOMO/LUMO或轨道字符。
9. Source field不可修改。
10. Wavefunction phase留给独立后续阶段。

---

## 56. 明确 Deferred

Phase 10J-5完成后仍然deferred：

* ELF basin topology
* ELF attractors
* basin populations
* automatic bond/lone-pair classification
* complex wavefunction
* wavefunction phase
* phase-colored surfaces
* Bloch phase
* orbital reconstruction
* orbital linear combinations
* HOMO/LUMO inference
* orbital character analysis
* projected orbital composition
* electronic band Adapter
* occupancy calculation
* density-matrix analysis
* Bader/atomic charges
* orbital difference fields
* volume ray casting
* arbitrary slices/profiles
* time-dependent orbitals
* external quantum calculations
* external APIs
* notebooks/scripts
* artifact code
* remote assets

---

## 57. Required Checks

至少运行：

```bash
git diff --check
uv lock --check
npm --prefix apps/web ls
npm --prefix apps/web ls three
npm --prefix apps/web test
npm --prefix apps/web run typecheck
npm --prefix apps/web run build
uv run python -m pytest -q
```

并单独运行：

* ELF compatibility tests
* ELF range tests
* ELF preset tests
* orbital compatibility tests
* orbital non-negativity tests
* orbital integral tests
* normalization tests
* occupancy/reference tests
* source identity tests
* identity completeness tests
* PARCHG product tests
* CUBE orbital tests
* product-manifest tests
* field-selector tests
* picking/inspector tests
* clipping/supercell tests
* PNG export tests
* accessibility tests
* mobile tests
* lifecycle tests
* browser evidence runners
* performance/memory runners
* network audit
* security tests
* Phase 10J regressions
* Phase 10I regressions
* Phase 10H regressions
* Phase 10G regressions
* structure-viewer regressions
* service-backed integration
* no-skipped assertion
* secret scan

必须如实记录：

* passed
* failed
* skipped
* unavailable

不得把skipped写成passed。

---

## 58. Commit / Push / CI

全部完成后：

```bash
git status --short
git diff --stat
git add <only Phase 10J-5 related files>
git commit -m "Add ELF and orbital volumetric products"
git push origin master
```

等待current-HEAD CI。

必须确认：

* backend unit success
* frontend tests success
* typecheck success
* build success
* ELF semantics tests success
* orbital semantics tests success
* identity/integral tests success
* browser evidence success
* performance evidence success
* accessibility success
* Phase 10J contract success
* Phase 10J-1 parser success
* Phase 10J-2 renderer success
* Phase 10J-3 product success
* Phase 10J-4 product success
* Phase 10I regression success
* Phase 10H regression success
* Phase 10G regression success
* structure-viewer regression success
* service-backed integration success
* no-skipped assertion success
* origin/master equals HEAD
* git status clean

不得伪造commit、CI run、ELF范围、轨道身份、积分、浏览器版本、测试数量或性能指标。

---

## 59. PASS 判定

PASS必须全部满足：

* 真实ELF Product实现
* 真实Orbital/Partial Density Product实现
* 使用真实Phase 10J-1 Runtime artifacts
* 使用Phase 10J-2 Renderer
* ELF quantity/unit严格
* ELF range validation完成
* ELF不静默clamp
* ELF科学解释边界完整
* 不声称bond/lone-pair/basin分析
* orbital quantity严格
* partial density身份严格
* source identity completeness完成
* filename不作为权威identity
* orbital-density non-negativity验证完成
* orbital integral完成
* normalization/integral语义完整
* occupancy只在兼容时比较
* 不静默renormalize
* 不自动识别HOMO/LUMO
* 不自动识别轨道字符
* source fields immutable
* exact isovalues完成
* structure overlay完成
* picking/inspector完成
* clipping/supercell完成
* PNG export完成
* product warnings完成
* accessibility完成
* mobile完成
* performance/memory caps完成
* Chromium通过
* Firefox通过
* WebKit通过
* mobile通过
* no external network
* no artifact code
* no arbitrary field arithmetic
* Phase 10J/10J-1/10J-2/10J-3/10J-4不回退
* 其他viewers不回退
* tests通过
* CI通过
* origin/master等于HEAD
* git status clean

---

## 60. PARTIAL_PASS 仅允许

仅允许：

* signed real orbital amplitude继续DEFERRED_BY_DESIGN
* complex wavefunction继续DEFERRED_BY_DESIGN
* CUBE multi-orbital继续typed unsupported
* PARCHG缺少完整轨道identity，但正确显示source-defined partial density
* occupancy无法比较，因为normalization或k-point weights未知
* ELFCAR存在轻微范围越界并明确标记numeric warning
* mobile一次只允许一个active layer和一个loaded field
* WebKit透明排序存在记录完整的非阻断差异
* npm/Python audit因既有registry问题unavailable，但依赖未变化且审计完整

以下缺失不得PARTIAL_PASS：

* real ELFCAR Runtime evidence
* real PARCHG/orbital-density Runtime evidence
* ELF range validation
* orbital quantity/normalization
* source identity disclosure
* exact isovalue/unit
* structure overlay
* picking/inspector
* browser matrix
* accessibility
* lifecycle

这些缺失必须FAIL。

---

## 61. FAIL 条件

以下任一情况必须FAIL：

* 只是给generic isosurface换标题
* 只增加ELF颜色预设
* ELF越界被clamp
* 高ELF被自动标记为共价键或孤对电子
* 声称完成ELF basin分析但没有拓扑合同
* PARCHG仅根据文件名识别band/orbital
* 任意PARCHG被称为HOMO/LUMO
* orbital density被默认归一化为1
* integral被自动称为occupancy
* source field被renormalize
* significant negative orbital density被取absolute value
* signed amplitude被自动square成density
* complex wavefunction只取real part
* CUBE generic scalar自动进入Orbital Product
* multi-orbital CUBE静默只取第一field
* surface形状被自动识别为s/p/d轨道
* surface附近原子被称为轨道归属
* 只有synthetic fixture，没有Runtime artifacts
* 同时无界加载所有orbital payloads
* artifact控制公式/Worker/shader
* 只有Chromium证据
* browser/API/performance evidence伪造
* skipped写成passed
* Phase 10J-4或其他viewers回退
* CI失败却声明PASS
* git不clean却声明完成

---

## 62. 最终报告格式

完成后必须输出：

# Phase 10J-5 ELF / Orbital Volumetric Product Result

## 1. Conclusion

PASS / PARTIAL_PASS / FAIL

## 2. Baseline

* Phase 10J-4 commit
* initial HEAD
* branch
* origin/master
* initial status
* final HEAD
* final status

## 3. Pre-Implementation Audit

* available fields
* ELFCAR semantics
* PARCHG semantics
* CUBE semantics
* identity metadata
* renderer support
* selected scope

## 4. Product Model

* product schema/type
* dataset binding
* fields
* quantities
* identities
* normalization
* integral semantics
* versions

## 5. ELF Product

* quantity
* unit
* range
* tolerance
* presets
* exact isovalues
* statistics
* warnings
* interpretation boundary

## 6. Orbital / Partial Density Product

* quantity
* source identity
* identity completeness
* band/k-point/spin metadata
* normalization
* integral
* occupancy comparison
* warnings

## 7. Signed / Complex Boundary

* signed amplitude support
* positive/negative surfaces
* complex wavefunction status
* phase status
* deferred capabilities

## 8. Product UI

* headers
* field selector
* presets
* exact thresholds
* statistics
* identity panel
* scientific warnings
* desktop
* mobile

## 9. Renderer / Interaction

* isosurfaces
* structure overlay
* supercell
* picking
* inspector
* clipping
* camera
* PNG export

## 10. Runtime / API

* Planner
* artifact reuse
* ELFCAR artifacts
* PARCHG/orbital artifacts
* successful cases
* negative/fallback cases

## 11. Browser Evidence

* Chromium
* Firefox
* WebKit
* mobile
* screenshots
* console
* network
* ELF cases
* orbital cases
* fallback cases

## 12. Accessibility

* keyboard
* focus
* exact units/isovalues
* identity text
* range/integral tables
* warnings
* screen-reader summary
* reduced motion
* mobile

## 13. Performance / Memory

* field counts
* payloads
* field switching
* extraction
* meshes
* cache
* memory
* GPU
* selector cost
* lifecycle
* near-cap behavior

## 14. Security

* artifact JS
* Worker/WASM
* arbitrary formulas
* external URLs
* identity metadata
* payload safety
* race handling
* errors
* secrets
* dependencies

## 15. Tests

* ELF semantics
* ELF range
* orbital semantics
* identity
* normalization
* integral
* product manifests
* UI
* renderer
* accessibility
* browser
* performance
* regressions
* service-backed
* no-skipped

## 16. Evidence

* directory
* Runtime datasets
* field artifacts
* product manifests
* identity records
* range/integral references
* screenshots
* logs
* metrics
* hashes
* replay commands

## 17. Files

列出主要implementation、tests、fixtures、runner、evidence、docs和persistent文件。

## 18. Explicitly Deferred

* ELF topology/basins
* automatic bond/lone-pair interpretation
* complex wavefunction
* wavefunction phase
* orbital reconstruction
* HOMO/LUMO inference
* orbital-character analysis
* orbital combinations
* density-matrix analysis
* Bader/atomic charges
* volume ray casting
* arbitrary slices/profiles

## 19. Checks

* diff
* lock
* dependency tree
* Three.js tree
* frontend tests
* typecheck
* build
* backend tests
* browser runners
* performance runners
* network
* secrets

## 20. Commit / CI

* commit
* HEAD
* CI run
* unit
* frontend
* build
* ELF tests
* orbital tests
* identity/integral tests
* browser
* performance
* accessibility
* service-backed
* no-skipped
* origin
* git status

## 21. Readiness

预期：

```text
volumetric contracts: READY
ELFCAR parser: READY
PARCHG parser: READY
CUBE scalar parser: READY
generic isosurface renderer: READY
Charge / Spin Density Product: READY
Electrostatic Potential Product: READY
ELF Product: READY
ELF range validation: READY
ELF structure overlay: READY
Orbital / Partial Density Product: READY
source identity disclosure: READY
orbital integral reporting: READY
normalization disclosure: READY
surface picking / inspector: READY
Chromium: READY
Firefox: READY
WebKit: READY
mobile: READY
accessibility: READY
performance: READY
security: READY
ELF topology / basin analysis: NOT_IMPLEMENTED
complex wavefunction phase: NOT_IMPLEMENTED
orbital reconstruction: NOT_IMPLEMENTED
automatic HOMO/LUMO identification: NOT_IMPLEMENTED
full volumetric analysis platform: PARTIAL_READY
```

## 22. Whether Allowed to Enter Next Phase

可以 / 不可以

只有 Phase 10J-5 完成、current-HEAD CI通过、真实ELFCAR与PARCHG/orbital Runtime artifacts、科学语义、Browser/API/Performance/Security Evidence闭合且git clean后，才允许进入仓库路线图中的下一阶段。

如果当前正式路线图将下一阶段定义为：

```text
Phase 10J-6：Volumetric Slice / Volume Rendering
```

则只有在上述条件全部满足后才允许进入；如果真实路线图名称不同，必须使用仓库中的正式下一阶段名称，不得由执行Agent自行改写路线图。

现在开始执行。

先读取真实 Phase 10J-4 Result、Phase 10J ELF/orbital quantity contracts、Phase 10J-1 ELFCAR/PARCHG/CUBE解析语义、Phase 10J-2 Renderer和现有产品基础设施，输出 Pre-Implementation Audit；然后完成ELF和Orbital compatibility、range/non-negativity验证、source identity、normalization/integral、产品UI、真实Browser/API/Performance/Security Evidence、docs、commit和CI闭环。

不得把本阶段扩展为ELF basin分析、复波函数相位、轨道重构、HOMO/LUMO推断、轨道线性组合或外部量子计算。


---END---

---TASK---
 状态：待处理
 # Phase 10J-6：Volumetric Slice / Volume Rendering

进入 Phase 10J-6：Volumetric Slice / Volume Rendering。

可以默认以下阶段均已严肃执行、完整验收并通过 current-HEAD CI：

* Phase 10F：Production Structure Viewer
* Phase 10G：Trajectory Contract / Adapter / Viewer / Evidence
* Phase 10H：Phonon Contract / Bands / DOS / Animation
* Phase 10I：Brillouin Zone Contract / Adapter / Renderer / Linked View
* Phase 10J：Volumetric Data Contract
* Phase 10J-1：Volumetric Parser / Adapter
* Phase 10J-2：Isosurface Renderer
* Phase 10J-3：Charge / Spin Density Product
* Phase 10J-4：Electrostatic Potential Product
* Phase 10J-5：ELF / Orbital Volumetric Product

必须以真实 Phase 10J-5 Result 为基线，记录实际：

* Phase 10J-5 commit
* current HEAD
* branch
* origin/master
* working-tree status
* volumetric schema versions
* payload encodings
* browser volumetric caps
* Three.js version
* WebGL2 support策略
* Worker版本
* CI run
* backend/frontend test counts

不得根据本 prompt 编造 commit、HEAD、浏览器能力、GPU限制、测试数量、渲染帧率、内存、截图或 CI run。

本阶段必须产生真实 Slice Product、真实 WebGL2 Direct Volume Renderer、正式产品集成以及 Browser/API/Performance/Security Evidence，不是静态热图、预渲染视频、伪3D半透明切片堆叠或仅设计文档阶段。

---

## 1. 本阶段总目标

将 Phase 10J-1 的 canonical volumetric artifacts 接入两条正式产品流水线：

```text
validated volumetric field
        ├── Slice Pipeline
        │     ↓
        │   bounded Worker sampling
        │     ↓
        │   lattice-axis 2D slice
        │     ↓
        │   quantitative heatmap / 3D plane
        │     ↓
        │   exact point probing
        │
        └── Direct Volume Pipeline
              ↓
            bounded payload loading
              ↓
            WebGL2 3D texture
              ↓
            application-owned ray marcher
              ↓
            transfer function / compositing
              ↓
            structure overlay / clipping
              ↓
            browser and GPU evidence
```

本阶段必须实现：

### Slice

* slice compatibility validator
* canonical lattice-axis slices
* continuous fractional slice position
* exact grid-plane mode
* interpolated plane mode
* periodic wrap
* non-periodic bounds
* triclinic plane geometry
* Worker-based sampling
* 2D quantitative slice view
* 3D slice-plane display
* synchronized 2D ↔ 3D selection
* exact value probe
* palette/window controls
* numeric legend
* PNG export
* accessible tabular fallback

### Direct Volume Rendering

* volume-render compatibility validator
* WebGL2 capability gate
* 3D texture upload
* canonical texture-axis mapping
* float32 GPU display buffer
* float64 → float32 display conversion audit
* application-owned ray-marching shader
* affine/triclinic unit-box mapping
* transfer function
* display window
* front-to-back compositing
* opacity step correction
* early ray termination
* bounded sample count
* clipping
* structure overlay
* camera controls
* perspective/orthographic behavior
* deterministic screenshot mode
* WebGL/texture fallback
* context-loss handling
* GPU/resource disposal

### Evidence

* real Runtime artifacts
* Chromium
* Firefox
* WebKit
* mobile
* WebGL2 fallback
* performance
* memory
* security
* accessibility
* current-HEAD CI closure

---

## 2. Minimum PASS Scope

PASS 至少要求正式支持：

### 2.1 Field Scope

```text
value_kind = real
field_rank = scalar
component_count = 1
sample_location = node
all values finite
```

### 2.2 Grid Scope

* 3D periodic endpoint-excluded affine grid
* 3D non-periodic affine grid
* orthogonal grid
* triclinic grid
* shifted origin
* float32 payload
* float64 payload

### 2.3 Slice Scope

* lattice axis 0 slice
* lattice axis 1 slice
* lattice axis 2 slice
* exact node plane
* continuous interpolated position
* 2D heatmap
* 3D plane
* point probing
* periodic wrap
* non-periodic clamp/reject

### 2.4 Volume Scope

* WebGL2 3D texture
* one active scalar field
* one active volume-render layer
* source-native values preserved
* bounded transfer function
* structure overlay
* clipping
* PNG screenshot
* GPU cap enforcement

### 2.5 Real Product Cases

正式证据至少覆盖：

* CHGCAR electron density
* signed spin density
* LOCPOT
* ELFCAR
* PARCHG或orbital density
* non-periodic Gaussian CUBE
* triclinic periodic field

---

## 3. 本阶段明确禁止

不得实现或宣称：

* scientific resampling artifact
* field smoothing
* denoising
* Gaussian filtering
* FFT filtering
* macroscopic averaging
* adaptive mesh
* octree volume
* sparse volume
* unstructured grid
* cell-centered volume rendering，除非本阶段完整实现并验证
* arbitrary tensor/vector volume rendering
* complex wavefunction volume rendering
* automatic `|ψ|²`
* wavefunction phase
* volume segmentation
* connected-component analysis
* basin analysis
* Bader analysis
* automatic feature detection
* automatic vacuum detection
* automatic bond/lone-pair classification
* scientific classification from transfer-function colors
* arbitrary oblique scientific slice artifact
* arbitrary curved slice
* arbitrary user expression
* arbitrary shader
* artifact shader
* artifact Worker/WASM
* artifact transfer-function code
* arbitrary remote colormap
* remote texture
* CDN
* external URL
* arbitrary Python
* notebook execution
* uploaded script execution
* DFT
* remote rendering service
* server-side GPU rendering
* production video export
* DICOM/medical-volume claims
* mesh extraction replacement
* hidden source-data mutation

本阶段的任意window、palette、opacity或transfer function均为显示状态，不得修改canonical field。

---

## 4. Public Tool 与产品身份

继续使用：

```text
structure.volumetric_data
```

优先不新增公开计算Tool。

正确架构：

```text
structure.volumetric_data
        ↓
canonical artifacts
        ↓
application-owned Slice / Volume Renderer
```

不得注册语义重叠的：

```text
structure.volume_render
structure.slice
structure.ray_cast
structure.volumetric_viewer
```

如果仓库现有架构要求持久化slice数据，可新增受控派生步骤：

```text
structure.volumetric_slice
```

但必须：

* 只消费validated volumetric artifacts
* 只允许canonical lattice-axis slice
* strict params
* 不接受任意公式
* 不接受任意plane shader
* 输出inert numeric slice artifact
* 正式进入Registry、PlanValidator、Runtime和evidence
* Pre-Implementation Audit说明必要性

推荐主产品仍作为结果层能力。

---

## 5. Baseline Verification

首先执行：

```bash
cd "E:\1project\Material Data Intelligence"

git status --short
git branch --show-current
git rev-parse HEAD
git log --oneline -50
git remote -v
git rev-parse origin/master
```

必须确认：

* repository正确
* branch为`master`
* working tree clean
* HEAD包含Phase 10J-5
* origin/master正确
* volumetric Parser已完成
* generic Isosurface Renderer已完成
* Charge/Spin、Potential、ELF/Orbital产品已完成
* payload loader、Worker和Three.js基础设施存在
* current-HEAD CI成功

如果working tree不干净，停止并报告，不得覆盖未知变更。

---

## 6. 必读实现

### 6.1 Volumetric Contracts

必须阅读：

* grid schema
* origin
* row step vectors
* shape
* sample location
* boundary conditions
* endpoint policy
* canonical `ijkc` flatten order
* dtype
* endianness
* payload hashes
* quantity
* units
* statistics
* caps
* security

### 6.2 Parser / Payload

必须阅读：

* raw payload loader
* gzip loader
* chunk状态
* artifact authorization
* float32/float64 decoding
* payload hash validation
* browser payload caps
* cache
* cancellation
* source-field immutability

### 6.3 Isosurface Renderer

必须复用：

* Three.js lifecycle
* camera
* structure overlay
* clipping
* atom picking
* inspector
* PNG export
* WebGL fallback
* context loss
* render-on-demand
* mobile/accessibility
* browser evidence runners

### 6.4 Product Infrastructure

必须复用：

* product detection
* field selector
* quantity/unit labels
* scientific warnings
* transfer/palette conventions，若已有
* artifact reuse
* mobile layout
* accessible tables
* screenshot metadata

### 6.5 WebGL Capabilities

必须审计：

* WebGL2
* `TEXTURE_3D`
* `MAX_3D_TEXTURE_SIZE`
* `MAX_TEXTURE_SIZE`
* `MAX_TEXTURE_IMAGE_UNITS`
* `R32F`
* float texture upload
* float texture filtering
* `OES_texture_float_linear`
* framebuffer formats
* depth texture
* timer query availability
* WebKit behavior
* mobile GPU behavior

不得假定所有WebGL2设备具有相同能力。

---

## 7. 修改前必须输出审计

修改代码前输出：

# Phase 10J-6 Volumetric Slice / Volume Rendering Pre-Implementation Audit

## 1. Baseline

* Phase 10J-5 commit
* HEAD
* branch
* origin/master
* git status
* CI
* schema versions
* Three.js version

## 2. Field / Grid Support

* quantities
* dtypes
* encodings
* node/cell-center
* periodic/non-periodic
* triclinic
* payload caps
* browser caps

## 3. Existing Rendering Infrastructure

* canvas/context lifecycle
* Worker
* payload loading
* camera
* clipping
* structure overlay
* export
* fallback
* accessibility
* evidence runners

## 4. Slice Strategy

明确：

* supported planes
* slice coordinates
* interpolation
* periodic wrapping
* 2D heatmap
* 3D plane
* point probing
* palette/window
* artifact/model策略

## 5. Volume Strategy

明确：

* WebGL2 gate
* texture dimensions
* canonical axis mapping
* GPU dtype
* float filtering strategy
* ray-box intersection
* ray step policy
* transfer function
* opacity compositing
* structure depth policy
* caps
* fallback

## 6. Precision / Memory

* float64 conversion
* conversion error
* texture bytes
* Worker bytes
* GPU bytes
* peak memory
* texture-size limits
* over-cap strategy

## 7. Scope Boundary

明确：

* lattice-axis slices
* direct volume rendering
* no scientific smoothing
* no arbitrary oblique slice artifact
* no vector/complex rendering
* no source mutation

## 8. Planned Files

列出implementation、shader、Worker、tests、fixtures、runner、evidence、docs和persistent文件。

审计完成后直接实施，不等待人工确认。

---

## 8. Compatibility Validation

在启动slice Worker或创建3D texture前必须验证：

* manifest schema
* dataset schema
* grid schema
* field schema
* payload schema
* hashes
* byte length
* dtype
* endianness
* flatten order
* field rank
* value kind
* component count
* sample location
* boundary conditions
* endpoint policy
* finite statistics
* browser caps
* security flags

不兼容时：

* 不启动采样Worker
* 不加载完整field，若metadata已足够判断
* 不创建3D texture
* 不创建WebGL context
* 显示typed状态
* 保留metadata、isosurface和已有产品入口

---

## 9. Supported Field Types

正式支持：

```text
real scalar node-sampled field
```

明确拒绝：

* real vector
* complex scalar
* complex vector
* arbitrary multi-component field
* masked field
* sparse field
* missing-value field
* cell-centered field，除非本阶段完整实现

不得自动执行：

* magnitude
* real part
* imaginary part
* absolute value
* square
* normalization

这些必须由正式derived-field artifact提供。

---

## 10. Canonical Texture Mapping

Phase 10J canonical offset：

```text
offset(i,j,k)
=
((i * ny) + j) * nz + k
```

其中`k`最快。

为避免全场transpose，WebGL 3D texture必须优先映射为：

```text
texture width  = nz
texture height = ny
texture depth  = nx
```

对应：

```text
texture coordinate x = q2
texture coordinate y = q1
texture coordinate z = q0
```

其中：

* `q0`沿`step_0`
* `q1`沿`step_1`
* `q2`沿`step_2`

必须有独立非对称pattern fixture验证：

* i/j/k没有交换
* 纹理x/y/z与科学axis没有混淆
* first/interior/last voxel正确
* triclinic映射正确

不得为了符合“texture x = lattice x”的直觉而无证据重排数据。

---

## 11. Domain Geometry

必须使用正式grid-domain helper。

对于periodic node/excluded grid：

```text
domain_basis_0 = nx * step_0
domain_basis_1 = ny * step_1
domain_basis_2 = nz * step_2
```

对于non-periodic node grid，domain extent必须根据Phase 10J endpoint policy确定，通常为：

```text
(n_axis - 1) * step_axis
```

但必须使用合同定义，不能硬编码猜测。

World position：

```text
r =
origin
+ u0 * domain_basis_0
+ u1 * domain_basis_1
+ u2 * domain_basis_2
```

其中：

```text
u ∈ [0,1]^3
```

必须支持：

* orthogonal
* monoclinic
* triclinic
* shifted origin
* non-periodic affine box

不得使用axis-aligned bounding box代替affine parallelepiped。

---

# Part A：Volumetric Slice

## 12. Slice Scope

正式支持三类canonical slice：

```text
lattice_axis_0
lattice_axis_1
lattice_axis_2
```

每个slice由：

* source field hash
* axis identity
* fractional position
* exact/interpolated mode
* output shape
* units
* window/palette display state

定义。

本阶段默认不支持正式科学意义上的：

* arbitrary oblique plane
* camera-facing slice
* curved slice
* arbitrary Cartesian equation
* arbitrary user-defined normal

可以将camera clipping plane作为显示辅助，但不得称为scientific slice。

---

## 13. Slice Coordinate

Slice位置使用：

```text
fractional_position ∈ [0,1)
```

对于periodic axis：

* `1.0`canonical wrap为`0.0`
* negative values按合同wrap或typed reject
* UI slider显示fraction和physical position

对于non-periodic axis：

* 必须限制在domain范围
* 不wrap
* 越界typed reject

必须显示：

* axis
* fractional position
* physical path length
* exact plane index或interpolation indices
* source field unit

---

## 14. Exact Plane Mode

当slice位置与grid node对齐时：

```text
q_axis * n_axis = integer
```

或按non-periodic endpoint合同对应index时，允许：

```text
sampling_mode = exact_grid_plane
```

必须记录：

* plane index
* no interpolation
* source values exact
* output shape
* orientation

不得对齐后仍执行不必要插值并称为exact。

---

## 15. Interpolated Slice Mode

连续位置位于两个plane之间时：

```text
sampling_mode = linear_axis_interpolation
```

对于轴0示例：

```text
V_slice(j,k)
=
(1-t) V(i0,j,k)
+ t V(i1,j,k)
```

Periodic grid：

* `i1`可以wrap到0
* boundary interpolation必须连续

Non-periodic grid：

* 不得越界外推
* endpoint使用合同规则

必须保存：

* lower index
* upper index
* `t`
* interpolation formula version
* periodic-wrap状态

不得在slice平面内执行额外平滑。

---

## 16. Slice Orientation

二维slice必须有明确坐标轴。

例如axis 0 slice：

* 2D horizontal coordinate沿`domain_basis_2`或合同固定顺序
* 2D vertical coordinate沿`domain_basis_1`

实际顺序必须统一、文档化、确定性。

每个slice必须记录：

* plane origin
* in-plane basis U
* in-plane basis V
* normal
* source lattice axes
* pixel/index mapping

不得将triclinic slice显示为科学意义上正交矩形而不披露几何映射。

### 16.1 2D Display Geometry

允许将slice values显示为矩形heatmap纹理，但必须：

* 显示其参数坐标含义
* 3D plane使用真实parallelogram
* 不把矩形UI距离当真实Cartesian距离
* inspector提供真实Cartesian坐标

---

## 17. Slice Worker

Slice采样必须在application-owned Worker中执行。

Worker请求至少包含：

```text
SliceRequest {
  requestId,
  fieldHash,
  grid,
  axis,
  fractionalPosition,
  samplingMode,
  fieldBuffer,
  dtype,
  outputCaps
}
```

响应至少包含：

```text
SliceResult {
  requestId,
  values,
  shape,
  planeDefinition,
  statistics,
  samplingMetadata,
  hash
}
```

必须支持：

* cancellation
* stale-result rejection
* field switch
* rapid slider changes
* route unmount cleanup
* transferable buffers

不得让artifact提供Worker代码。

---

## 18. Slice Data Model

建议建立：

```text
volumetric_slice.v1
```

或等价typed model。

至少包含：

* schema/type version
* source dataset hash
* source field hash
* axis
* fractional position
* physical position
* exact/interpolated mode
* indices
* interpolation factor
* plane origin
* in-plane basis
* output shape
* values dtype
* units
* statistics
* content hash
* provenance
* security

如果不持久化artifact，也必须有同等严格的ephemeral model和deterministic hash。

---

## 19. Slice 2D View

必须提供定量二维slice view。

至少支持：

* heatmap
* exact legend
* min/max
* display window
* palette
* hover
* click/pin point
* zoom/pan
* reset
* pixel/index
* fractional coordinate
* Cartesian coordinate
* source value
* displayed normalized value
* unit

不得用静态PNG作为唯一slice实现。

### 19.1 Value Authority

Inspector必须显示source/interpolated scientific value。

Palette归一化值只能作为display metadata，不能替代field value。

---

## 20. Slice 3D Plane

必须在现有Three.js scene中显示对应平面：

* real affine geometry
* correct triclinic shape
* application-owned texture/material
* bounded opacity
* structure overlay
* unit cell
* clipping compatibility
* no second canvas/context

纹理只来自validated slice values。

不得：

* 使用artifact shader
* 使用外部texture
* 将平面显示称为体等值面
* 将2D display normalization写回field

---

## 21. Slice Point Probe

点击2D或3D slice必须返回：

```text
SlicePointRef {
  fieldId,
  sliceId,
  axis,
  fractionalSlicePosition,
  sliceCoordinates,
  fractionalPosition,
  cartesianPosition,
  sourceValue,
  displayedNormalizedValue,
  unit,
  interpolationMetadata
}
```

必须验证：

* 2D → 3D mapping
* 3D → 2D mapping
* periodic identity
* triclinic coordinates
* shifted origin
* exact/interpolated plane

不得使用nearest voxel冒充continuous interpolated value。

---

## 22. Slice ↔ Structure Linking

选择slice point时：

* 3D中显示marker
* structure保持当前camera
* inspector显示nearest atom distance，可选
* 不将value归属给最近原子
* 不声称atomic charge/orbital contribution

选择3D atom时可显示：

* atom fractional coordinate
* 对应三个canonical slice positions
* “move slice to atom coordinate”显示操作

移动slice只改变显示位置，不修改field。

---

## 23. Slice Display Window

Slice必须支持：

* source min/max
* slice min/max
* manual low/high
* symmetric window around zero
* reset
* quantity-specific presets

Window只控制：

```text
source value → display normalized value
```

不得：

* clamp source payload
* 修改slice scientific values
* 生成新field
* 隐藏exact numeric unit

必须显示：

* window low/high
* unit
* source range
* slice range
* out-of-window policy

---

## 24. Slice Palette

只允许application-owned allowlisted palettes。

至少区分：

* sequential
* diverging
* cyclic仅在有正式周期量时；本阶段默认不使用

Quantity presets：

* density / ELF / orbital：sequential
* signed spin：diverging with explicit zero
* potential：sequential或diverging，依gauge/window明确

不得：

* artifact提供palette code
* artifact提供CSS gradient
* palette名称暗示未验证的科学分类
* 用颜色替代单位和符号文本

---

# Part B：Direct Volume Rendering

## 25. WebGL2 Gate

Direct Volume Renderer必须要求WebGL2。

初始化前检测：

* WebGL2 context
* `MAX_3D_TEXTURE_SIZE`
* float texture support
* texture allocation可行性
* shader compile/link
* required texture units
* GPU memory estimate
* browser product cap

不满足时：

* 不尝试无限降级循环
* 显示typed fallback
* 保留Slice和Isosurface产品
* 保留metadata/JSON

不得在WebGL1上伪实现完整3D texture ray marching并声称同等支持。

---

## 26. GPU Texture Dtype

Canonical source允许float32/float64。

GPU正式显示texture优先：

```text
R32F
```

### 26.1 Float32 Source

可直接上传或经过必要字节布局验证后上传。

### 26.2 Float64 Source

WebGL2没有通用float64 3D texture路径。

必须生成display-only float32 buffer，并记录：

* source dtype
* GPU dtype
* conversion applied
* max absolute error
* max relative error
* RMS conversion error
* finite count
* conversion hash
* source field unchanged

不得静默降精度。

如果误差超过quantity-specific display tolerance：

* 禁止volume mode
* Slice/Isosurface可继续使用source CPU values
* 显示typed precision failure

---

## 27. GPU Texture Size / Bytes

必须同时验证：

* `nx、ny、nz`与`MAX_3D_TEXTURE_SIZE`
* mapped texture width/height/depth
* total texels
* bytes per texel
* estimated GPU allocation
* product GPU cap
* mobile GPU cap

不得仅检查单轴dimension。

估算至少包含：

```text
volume texture
transfer-function texture
depth texture
render targets
structure depth resources
temporary upload buffer
```

超过cap：

* 不分配texture
* 不依赖GPU allocation failure作为正常控制流
* 显示resource-limit状态
* 提供Slice/Isosurface fallback

---

## 28. No Silent Display Downsampling

默认禁止自动对volume source做不可见降采样。

如果原field超过GPU texture cap：

```text
Direct Volume Rendering unavailable at source resolution
```

允许用户继续：

* slices
* isosurfaces
* metadata
* source artifact download

### 28.1 Optional Display-Only Downsampling

只有实现以下全部条件时，才允许可选display-only downsampling：

* 用户明确启用
* 显示原始shape
* 显示display shape
* 显示algorithm
* 显示error estimates
* source field immutable
* point inspector仍从source field取值
* derived display buffer有hash/provenance
* 不作为scientific artifact
* 不用于积分、statistics或exported field
* positive/negative extrema preservation策略明确

若未满足，保持DEFERRED_BY_DESIGN。

---

## 29. Ray / Affine Box Intersection

Volume必须在normalized grid unit cube中进行ray-box intersection：

```text
u ∈ [0,1]^3
```

流程：

1. camera ray位于world Cartesian。
2. 使用domain affine transform逆矩阵转换到grid unit coordinates。
3. 与unit cube求entry/exit。
4. 沿grid ray采样3D texture。
5. 将clipping和non-periodic边界应用于采样区间。

必须支持triclinic domain。

不得用world axis-aligned box进行科学采样。

---

## 30. Ray Step Policy

Ray step必须基于grid resolution和ray在voxel coordinates中的长度。

建议：

```text
ray_voxel_delta =
ray_unit_delta * [nx, ny, nz]
```

```text
sample_count =
ceil(length(ray_voxel_delta) * samples_per_voxel)
```

必须：

* bounded minimum
* bounded maximum
* product/browser cap
* mobile cap
* exact strategy version
* no infinite loop
* no camera-dependent严重欠采样

不得只用固定world step而忽略anisotropic/triclinic voxel geometry。

---

## 31. Texture Sampling

必须支持可靠的trilinear sampling。

优先：

* hardware linear float filtering，能力验证通过时

否则：

* application-owned manual trilinear sampling

Manual trilinear必须：

* 使用mapped texture axis
* 8个bounded samples
* periodic wrap
* non-periodic clamp/outside handling
* correct half-texel convention
* exact tests

不得在不支持linear float filtering时静默退化为nearest并声称同等质量。

如果仅能nearest：

* volume mode typed degraded或unavailable
* slices仍可正常工作

---

## 32. Periodic Sampling

Periodic grid：

* texture source仍为endpoint-excluded
* normalized coordinate wrap到`[0,1)`
* sampling跨边界连续
* 不创建持久化重复halo texture
* triclinic world mapping正确

Non-periodic grid：

* 不wrap
* outside domain透明
* 边界采样服从endpoint contract

必须有三轴boundary reference tests。

---

## 33. Transfer Function

Transfer function必须由应用定义为受限、声明式数据。

建议model：

```text
TransferFunction {
  version,
  windowLow,
  windowHigh,
  controlPoints[],
  interpolation,
  opacityScale,
  zeroPolicy,
  paletteId
}
```

限制：

* max control points
* finite values
* sorted positions
* bounded opacity `[0,1]`
* allowlisted interpolation
* allowlisted palette
* no code
* no arbitrary GLSL
* no external texture

Transfer function是显示状态，不进入source field scientific hash。

---

## 34. Transfer Function Presets

必须提供中性、quantity-aware presets：

### Non-Negative Fields

* Low intensity
* Medium intensity
* High intensity

### Signed Fields

* Symmetric signed
* Positive only
* Negative only

### Potential

* Source-range
* Around current zero
* Narrow window
* Wide window

### ELF

* Low-to-high localization display

每个preset必须显示：

* exact window
* exact opacity controls
* unit
* preset ID/version
* no scientific classification claim

不得命名为：

* bonding
* lone pair
* atomic charge
* vacuum
* HOMO
* magnetic domain

除非存在正式独立分析结果。

---

## 35. Window / Normalization

Shader sampling必须保留：

```text
sourceValue
```

再进行display mapping：

```text
x =
(sourceValue - windowLow)
/
(windowHigh - windowLow)
```

Window无效时：

* `low >= high`
* NaN/Infinity
* 超出允许范围

必须typed reject。

不得修改source buffer。

### 35.1 Signed Zero

Signed field必须明确：

* zero location
* positive/negative mapping
* symmetric lock状态
* window unit

不得因window变化丢失符号。

---

## 36. Front-to-Back Compositing

必须使用确定、文档化的front-to-back alpha compositing：

```text
C_acc =
C_acc + (1 - A_acc) * α * C
```

```text
A_acc =
A_acc + (1 - A_acc) * α
```

必须：

* bounded steps
* early termination
* stable precision
* deterministic fixed-camera evidence
* no premultiplied-alpha混淆

不得使用未说明的浏览器blend state替代ray内部积分。

---

## 37. Opacity Step Correction

为避免改变sample count导致整体不透明度严重变化，必须采用step-aware opacity correction。

例如：

```text
alpha_step =
1 - (1 - alpha_reference)^(step_length / reference_step)
```

实际公式可以不同，但必须：

* versioned
* documented
* independently tested
* camera/sample-count变化下视觉结果稳定
* no NaN
* bounded `[0,1]`

不得直接把transfer-function alpha在每个step重复累积而不考虑step length。

---

## 38. Early Ray Termination

允许：

```text
A_acc >= threshold
```

时提前终止。

要求：

* threshold固定/版本化
* bounded
* screenshot metadata记录
* 不改变source data
* performance evidence包含开启状态

可以使用例如0.98或0.995，但必须以真实实现和测试为准，不得由prompt编造最终值。

---

## 39. Empty-Space Skipping

本阶段可选。

若实现：

* 只能使用validated min/max brick metadata
* brick size bounded
* metadata deterministic
* 不得漏掉transfer-function非透明区
* 有CPU reference tests
* 有browser一致性证据

若未实现：

```text
EMPTY_SPACE_SKIPPING = DEFERRED_BY_DESIGN
```

不影响PASS。

不得使用不安全的动态octree或artifact code。

---

## 40. Volume Shader Ownership

所有shader必须：

* 位于application source
* static bundled
* reviewed
* versioned
* covered by tests
* no artifact source
* no remote import
* no dynamic string concatenation fromartifact
* no eval

Artifact只提供：

* numeric field
* units
* quantity
* limited display hints

Artifact不得控制：

* shader source
* loop count
* sampler count
* ray algorithm
* material class
* GLSL defines
* extensions

---

## 41. Structure Overlay

Volume mode必须复用现有单一Three.js scene：

* one canvas
* one context
* one camera
* structure atoms
* bonds
* unit cell
* volume box

不得为volume和structure创建两个重叠canvas。

### 41.1 Depth / Occlusion Policy

必须定义结构与volume的深度合成策略。

优先：

* structure depth prepass
* ray marching在opaque geometry depth处终止
* 后续绘制structure highlight/labels

或其他经过验证的单场景策略。

必须验证：

* atoms位于volume前方
* atoms位于volume内部
* atoms位于volume后方
* transparent volume不错误覆盖所有geometry
* clipping一致

不得仅依赖render order造成明显错误空间关系。

---

## 42. Supercell Scope

Direct Volume Rendering默认正式支持：

```text
source cell only
```

结构overlay必须与source cell一致。

如果实现periodic supercell：

* 不复制完整3D texture
* 复用同一texture
* ray domain/image mapping bounded
* total cell cap
* camera/picking identity明确
* performance证据完整

否则：

```text
DIRECT_VOLUME_SUPERCELL = DEFERRED_BY_DESIGN
```

用户仍可在Isosurface模式使用既有bounded supercell。

不得只复制结构而不复制volume却让用户误以为空间一致。

---

## 43. Clipping

Volume mode必须复用现有clipping controls。

至少支持：

* enable/disable
* bounded plane count
* offset
* orientation
* reset
* keyboard/mobile

Clipping在grid/world变换后正确应用。

不得：

* 生成scientific slice artifact
* 修改source field
* 把clipped face称为定量slice

可提供：

```text
Open current clipping position as canonical lattice slice
```

但只有plane与canonical lattice axis一致时才能直接转换。

---

## 44. Volume Interaction

由于体绘制没有唯一表面，点击volume不得自动声称获得“选中体素深度”。

正式支持：

* transfer-function inspector
* current ray/sample settings
* field metadata
* explicit slice probe
* explicit crosshair point probe

可选支持：

```text
first-opacity-threshold hit
```

但必须标记为：

```text
display-derived volume hit
```

并记录：

* opacity threshold
* transfer function
* ray
* source value
* not a scientific surface

如果无法可靠实现，保持deferred。

---

## 45. Mode Composition

产品至少提供：

```text
Isosurface
Slice
Volume
```

三个模式。

要求：

* field selection共享
* source artifact共享
* quantity/unit共享
* source field不重复解析
* mode switch取消stale work
* camera可保留或明确reset
* product warnings共享
* no duplicate canvas/context

不得把三个模式分别实现为互不兼容的页面和资源栈。

---

## 46. Volume Product UI

至少包含：

### Field

* field selector
* quantity
* unit
* source format
* validation

### Rendering Mode

* Isosurface
* Slice
* Volume

### Volume Controls

* display window
* transfer-function preset
* control points，若提供高级模式
* opacity scale
* sample quality
* clipping
* structure visibility
* unit cell
* reset

### Status

* source shape
* texture shape
* source dtype
* GPU dtype
* conversion error
* texture bytes
* ray-step policy
* current caps
* WebGL2 state

不得隐藏float64 → float32转换信息。

---

## 47. Quality Presets

允许：

```text
Low
Balanced
High
```

但每个preset必须绑定实际：

* samples per voxel
* max ray steps
* opacity correction policy
* pixel ratio cap
* mobile availability

UI必须显示具体参数或可展开查看。

不得让“High”突破GPU安全cap。

---

## 48. Render-on-Demand

Volume renderer可以在camera交互时连续render，但必须：

* interaction开始启动
* interaction结束停止
* controls change触发
* transfer-function change触发
* resize触发
* idle停止
* hidden tab停止
* reduced-motion遵守

不得在静止页面持续永久60 FPS。

---

## 49. Determinism

相同：

* field hash
* texture conversion
* camera
* transfer function
* window
* sample quality
* viewport
* devicePixelRatio
* structure visibility
* clipping

必须产生容差内确定的：

* slice values
* slice hash
* volume screenshot
* shader state metadata
* texture conversion hash
* render metrics

GPU rasterization允许轻微浏览器差异，但必须使用合理像素容差，不得要求跨GPU逐字节相同。

---

## 50. PNG Export

必须支持：

### Slice

* 2D slice PNG
* legend
* exact unit
* axis/position
* field hash
* window/palette metadata

### Volume

* current 3D volume screenshot
* transfer function
* window
* quality preset
* camera
* clipping
* structure state
* texture conversion metadata

要求：

* bounded resolution
* safe filename
* no external assets
* Blob URL revoke
* stale render禁止export
* fixed-camera evidence mode

PNG不替代source field或slice numeric artifact。

---

## 51. Optional Slice Numeric Export

如现有安全表格导出基础设施成熟，可支持bounded：

```text
CSV
```

必须包含：

* source field hash
* axis
* fractional position
* sampling mode
* row/column indices
* coordinates
* values
* unit

禁止：

* over-cap导出
* spreadsheet公式注入
* arbitrary filename
* external link

该能力可defer，不影响PASS。

---

## 52. WebGL / Renderer Fallback

### 52.1 No WebGL2

显示：

* Slice available
* Isosurface available，若WebGL1/现有实现支持
* Direct Volume unavailable
* capability reason
* field metadata

### 52.2 Texture Too Large

显示：

* source shape
* detected max texture size
* browser cap
* no allocation attempted
* Slice/Isosurface fallback

### 52.3 Float Texture Failure

显示：

* source dtype
* attempted GPU format
* capability failure
* Slice fallback

### 52.4 Shader Failure

* typed shader initialization error
* redacted details
* no raw driver dump in user UI
* fallback available

### 52.5 Context Loss

* stop render
* dispose/rebuild texture
* no duplicate canvas/context
* restore source state或明确reload
* no stale Worker
* selection恢复或清理

---

## 53. Lifecycle

必须保证：

* one canvas
* one WebGL context
* one volume material
* bounded render targets
* one active volume texture
* one active field buffer
* bounded slice buffers
* one Worker或受控Worker pool
* one controls instance
* one ResizeObserver
* mode switch cleanup
* field switch cleanup
* route unmount cleanup
* texture dispose
* render target dispose
* material dispose
* geometry dispose
* Worker cancellation
* fetch abort
* Blob URL revoke
* no stale texture upload
* no stale slice result
* no render-loop leak

---

## 54. Browser / GPU Caps

除Phase 10J-2 caps外，必须定义：

* max 3D texture dimension
* max texture voxels
* max texture bytes
* max source payload bytes
* max float64 conversion bytes
* max transfer-function points
* max ray steps
* max samples per voxel
* max render pixel count
* max pixel ratio
* max slice output values
* max slice texture size
* max active volume fields
* max GPU render targets
* max cached volume textures
* max cached slices
* max frame-time budget
* mobile-specific caps

Browser cap可以低于Parser cap。

必须明确：

```text
parseable
≠ sliceable in browser
≠ direct-volume-renderable
```

---

## 55. Performance Metrics

### Payload

* source bytes
* dtype
* shape
* voxel count
* decode time
* hash time
* conversion time
* conversion error

### Slice

* Worker startup
* exact-plane time
* interpolated-plane time
* slice bytes
* texture upload
* point-probe latency
* 2D render time
* 3D plane update time

### Volume

* GPU capability query
* texture allocation
* texture upload
* shader compile/link
* first meaningful render
* frame time during interaction
* frame time idle
* ray-step count
* early termination rate，若可测
* transfer-function update latency
* clipping latency
* camera latency
* PNG export

### Resources

* CPU field bytes
* GPU texture bytes
* render-target bytes
* slice cache bytes
* texture cache entries
* Worker count
* canvas count
* context count
* listeners
* cleanup time

---

## 56. Required Performance Cases

至少覆盖：

1. small CHGCAR
2. signed spin field
3. LOCPOT
4. ELFCAR
5. PARCHG/orbital field
6. non-periodic CUBE
7. triclinic periodic field
8. float32 source
9. float64 source conversion
10. three axis slices
11. rapid slice movement
12. rapid transfer-function changes
13. rapid mode switching
14. moderate multi-million-voxel field
15. near-texture-cap field
16. texture-over-cap refusal
17. repeated artifact switching
18. repeated mount/unmount
19. context loss/restore
20. mobile volume rendering或明确mobile fallback

---

## 57. Scientific Reference Tests：Slice

必须建立独立reference。

### 57.1 Constant Field

* all slices constant
* exact/interpolated一致
* point probe exact
* window不改变source value

### 57.2 Axis Pattern

例如：

```text
f(i,j,k) = 100i + 10j + k
```

验证：

* axis order
* 2D orientation
* exact plane
* interpolation
* texture mapping

### 57.3 Linear Field

```text
f(q0,q1,q2) = A q0 + B q1 + C q2 + D
```

验证任意continuous slice和probe。

### 57.4 Periodic Field

验证：

* wrap
* position接近1与接近0连续
* shifted origin
* triclinic coordinates

Reference不得调用production slice Worker。

---

## 58. Scientific Reference Tests：Volume

### 58.1 Constant Transparent / Opaque

* transfer function全透明
* constant opacity
* deterministic compositing
* early termination

### 58.2 Linear Ramp

验证：

* texture orientation
* window mapping
* ray direction
* front/back顺序

### 58.3 Layered Slabs

构造已知前后层，验证front-to-back compositing。

### 58.4 Triclinic Domain

验证：

* world ray → unit cube
* structure alignment
* clipping
* domain bounds

### 58.5 Periodic Pattern

验证边界采样连续。

### 58.6 CPU Reference Ray Marcher

为极小fixture建立独立CPU reference：

* same transfer-function semantics
* same step correction
* same compositing
* pixel comparison tolerance

不得直接复用shader逻辑生成expected结果。

---

## 59. Shader Tests

至少覆盖：

* compile/link Chromium
* compile/link Firefox
* compile/link WebKit
* mapped texture axes
* float filtering path
* manual trilinear path
* window
* transfer function
* signed zero
* ray-box intersection
* clipping
* opacity correction
* early termination
* max-step safety
* NaN protection
* context restore

必须对shader源码执行静态安全审计。

---

## 60. Structure Depth Tests

必须验证：

* atom在volume前
* atom在volume内
* atom在volume后
* bond crossing volume
* unit-cell lines
* clipping plane
* transparent/opaque transfer functions
* orthographic/perspective
* mobile

不得出现所有atoms永远在volume前或永远被错误遮挡的情况。

---

## 61. Accessibility

必须支持：

### Slice

* semantic axis selector
* position input
* exact/interpolated状态
* field unit
* window values
* palette名称
* keyboard point navigation
* accessible value table
* selected coordinate/value announcement

### Volume

* semantic mode selector
* transfer-function preset
* window
* opacity
* quality preset
* WebGL capability status
* source/GPU dtype
* textual field summary
* no color-only sign distinction
* reduced motion
* keyboard controls
* fallback可读

Canvas外必须提供：

* field metadata
* source range
* display window
* transfer function
* current slice
* selected point
* texture shape
* rendering limitations
* scientific warnings

---

## 62. Mobile

必须验证：

### Slice

* axis selector
* position slider
* 2D heatmap
* pinch/zoom
* point probe
* 3D plane
* inspector

### Volume

* capability gate
* lower pixel ratio
* lower ray steps
* transfer-function controls
* camera touch
* clipping
* structure overlay
* context lifecycle

移动端允许：

* Direct Volume unavailable onlow-cap devices
* 只提供Slice和Isosurface fallback
* 更低texture cap
* 更低ray steps
* 一次只缓存一个slice
* 禁用高分辨率PNG

但必须显示明确原因，不得空白失败。

---

## 63. Browser Evidence Matrix

必须在真实：

* Chromium
* Firefox
* WebKit
* mobile viewport

验证：

### Slice

* three axes
* continuous position
* exact/interpolated mode
* periodic boundary
* triclinic geometry
* 2D heatmap
* 3D plane
* point probe
* palette/window
* PNG

### Volume

* WebGL2 detection
* texture mapping
* float32
* float64 conversion
* transfer function
* signed field
* structure overlay
* clipping
* camera
* context loss
* texture-over-cap fallback
* no-WebGL2 fallback
* lifecycle
* console
* network

---

## 64. Required Screenshots

至少保存：

1. Slice Product header
2. axis-0 exact slice
3. axis-1 interpolated slice
4. axis-2 slice
5. triclinic 3D slice plane
6. selected slice point inspector
7. periodic boundary slice
8. signed spin diverging slice
9. LOCPOT slice
10. ELF slice
11. Volume Product header
12. CHGCAR direct volume
13. signed spin direct volume
14. LOCPOT direct volume
15. ELF direct volume
16. orbital-density direct volume
17. non-periodic CUBE volume
18. triclinic volume + structure
19. transfer-function controls
20. structure-depth evidence
21. clipping
22. float64 conversion disclosure
23. texture-over-cap fallback
24. no-WebGL2 fallback
25. context-lost state
26. accessibility value table
27. mobile slice
28. mobile volume或mobile fallback
29. PNG export

每张截图记录：

* browser/version
* viewport
* deviceScaleFactor
* dataset hash
* field hash
* quantity
* unit
* source dtype
* GPU dtype
* source/texture shape
* slice axis/position，若适用
* window
* transfer-function ID
* quality preset
* camera
* clipping
* texture bytes
* screenshot hash

---

## 65. API / Runtime Evidence

正式主证据必须使用 Phase 10J-1 QueueWorkerRuntime artifacts。

至少覆盖：

### Case A：Electron Density

* canonical payload
* axis slices
* direct volume
* structure overlay

### Case B：Signed Spin Density

* diverging slice
* signed transfer function
* zero preservation

### Case C：Potential

* gauge-aware values
* slice
* volume
* no vacuum/work-function claim

### Case D：ELF

* dimensionless
* bounded display
* no topology claim

### Case E：Orbital Density

* source identity
* non-negative display
* no HOMO/LUMO inference

### Case F：Non-Periodic CUBE

* affine domain
* atom context
* no periodic wrap

### Case G：Over-Cap

* metadata available
* direct volume refused
* slice或isosurface fallback
* no excessive allocation

记录sanitized：

* plan
* job
* tool call
* artifacts
* schema versions
* field hash
* payload hash
* slice hashes
* texture conversion hash
* compatibility
* GPU caps
* render state
* final status

---

## 66. Planner Routing Update

完成后，以下请求可以进入对应产品模式：

### Slice

* 显示这个CHGCAR在晶格c方向的切片
* 查看这个体数据在fractional 0.5位置的截面
* 显示LOCPOT的二维晶格切片
* Show a slice through this volumetric field
* Display the plane at fractional coordinate 0.5

### Direct Volume

* 直接体绘制这个电荷密度
* 用volume rendering显示这个CUBE
* 显示ELF的体绘制
* Render this volumetric field directly
* Open the 3D volume view

Planner必须：

* 复用已有parsed artifacts
* 验证field compatibility
* 不自动派生vector magnitude
* 不自动降采样
* 不把display window称为scientific threshold
* 不声称执行计算

### 66.1 Negative Routing

不得声称支持：

* 任意曲面切片
* 自动找缺陷区域
* 自动分割电子云
* 做Bader分析
* 计算真空能级
* 重构波函数
* 显示复相位
* 任意Python volume filter
* 运行VASP
* 远程GPU渲染

---

## 67. Security

必须验证：

* no artifact JavaScript
* no artifact shader
* no artifact Worker/WASM
* no artifact HTML/CSS
* no external URL
* no remote texture
* no CDN
* no iframe
* no eval
* no Function constructor
* no dynamic shader from metadata
* no arbitrary transfer-function code
* no arbitrary plane expression
* no arbitrary codec
* no unbounded texture allocation
* no shader infinite loop
* max ray steps compile/runtime bounded
* no stale texture race
* source field immutable
* no local path
* no signed URL disclosure
* no token
* no secret
* redacted shader/driver errors
* safe export filename

必须输出：

```text
NO_VOLUMETRIC_SLICE_VOLUME_EXTERNAL_NETWORK_REQUESTS
```

以及：

```text
NO_SECRET_PATTERN_HITS
```

---

## 68. Dependency Policy

优先不新增依赖。

复用：

* existing Three.js
* existing Worker bundling
* existing payload loader
* existing chart/heatmap infrastructure
* existing math helpers
* existing product UI

不得引入：

* second Three.js
* second 3D framework
* remote shader library
* medical volume framework
* heavy image-processing library

如新增小型transfer-function或heatmap依赖，必须记录：

* version
* license
* bundle size
* browser support
* transitive dependencies
* security findings
* deterministic behavior
* lockfile变化

必须运行：

```bash
npm --prefix apps/web ls three
```

确认Three.js版本唯一且符合现有基线。

---

## 69. Frontend Tests

至少覆盖：

### Compatibility

* scalar real
* vector rejection
* complex rejection
* cell-center rejection
* over-cap
* missing WebGL2

### Slice

* axis selector
* exact plane
* interpolated plane
* periodic wrap
* non-periodic bounds
* triclinic plane
* 2D orientation
* point probe
* window/palette
* 3D linking
* cancellation
* stale result

### Volume

* WebGL2 gate
* texture axis mapping
* R32F upload
* float64 conversion
* conversion error
* ray-box intersection
* transfer function
* opacity correction
* clipping
* structure overlay
* quality preset
* context loss
* texture-over-cap
* shader failure
* PNG

### Lifecycle

* field switch
* mode switch
* mount/unmount
* no duplicate canvas
* no duplicate context
* no duplicate Worker
* no stale texture
* no render-loop leak

不得只测试控件存在。

---

## 70. Regression Tests

必须保持：

* Phase 10J contracts
* Phase 10J-1 Parsers
* Phase 10J-2 Isosurface Renderer
* Phase 10J-3 Charge/Spin Product
* Phase 10J-4 Potential Product
* Phase 10J-5 ELF/Orbital Product
* structure viewer
* trajectory viewer
* phonon viewer
* Brillouin Zone viewer
* Band–BZ linked view
* Tool Registry
* Planner
* PlanValidator
* QueueWorkerRuntime
* service-backed integration
* Phase 10 Closure Regression Pack
* no-skipped assertion

不得因volume shader或scene lifecycle修改破坏现有viewer。

---

## 71. Evidence Directory

建议新增：

```text
docs/phase10j/evidence/phase10j6_volumetric_slice_volume_rendering/
```

至少包含：

* README
* pre-implementation audit
* real Runtime datasets
* compatibility outputs
* slice models/artifacts
* slice hashes
* independent slice references
* texture mapping references
* GPU capability captures
* float64 conversion evidence
* shader version/hash
* CPU ray-march references
* browser matrix
* screenshots
* console logs
* network logs
* performance metrics
* GPU/memory estimates
* lifecycle metrics
* context-loss evidence
* accessibility audit
* mobile audit
* PNG exports
* fallback cases
* cap/over-cap cases
* security audit
* dependency audit
* secret scan
* CI record
* replay commands

不得提交：

* secrets
* private paths
* proprietary production volumes
* browser profiles
* caches
* node_modules
* external assets
* compiled shader dumps with private environment details
* videos
* oversized source payloads

---

## 72. Documentation

新增或更新：

* Phase 10J-6 overview
* slice scientific model
* slice axes
* exact/interpolated planes
* periodic wrapping
* triclinic slice geometry
* 2D heatmap semantics
* point probing
* display windows
* palettes
* WebGL2 volume architecture
* canonical texture mapping
* float64 → float32 display conversion
* ray-box intersection
* ray-step policy
* texture sampling
* transfer functions
* opacity correction
* compositing
* structure depth integration
* clipping
* GPU caps
* fallbacks
* context loss
* lifecycle
* performance
* accessibility
* mobile
* security
* known limitations
* roadmap handoff

更新：

* `docs/index.md`
* `persistent/DESIGN_PROGRESS.md`
* `persistent/TASK_BOARD.md`
* `persistent/CHANGELOG.md`
* `persistent/OPEN_QUESTIONS.md`
* `persistent/TOOL_REGISTRY_NOTES.md`
* `persistent/ARCHITECTURE_DECISIONS.md`

ADR至少记录：

1. Canonical texture映射使用`width=nz、height=ny、depth=nx`。
2. Slice正式范围为三个canonical lattice-axis planes。
3. Slice interpolation不修改source field。
4. Direct Volume Rendering要求WebGL2。
5. float64 GPU显示需显式转换和误差披露。
6. Transfer function是显示状态，不是科学数据变换。
7. Volume shader必须由应用静态拥有。
8. Triclinic volume使用完整affine transform。
9. 超GPU cap时默认拒绝，不自动静默降采样。
10. Slice/Isosurface是Direct Volume不可用时的正式fallback。
11. 本阶段不支持vector/complex volume。
12. 本阶段不实现scientific segmentation或feature detection。

---

## 73. 明确 Deferred

Phase 10J-6完成后仍然deferred：

* cell-centered slice/volume
* arbitrary oblique scientific slices
* curved slices
* vector-field volume rendering
* complex wavefunction rendering
* phase-colored volume
* adaptive/sparse volume
* empty-space octree，若未实现
* display downsampling，若未严格实现
* volume segmentation
* basin/topology analysis
* volume ray picking作为科学点选择
* arbitrary field filters
* scientific resampling artifacts
* time-dependent 4D volume
* mixed-periodicity/slab scientific product
* remote GPU rendering
* production video export
* external APIs
* notebooks/scripts
* artifact code
* remote assets

---

## 74. Required Checks

至少运行：

```bash
git diff --check
uv lock --check
npm --prefix apps/web ls
npm --prefix apps/web ls three
npm --prefix apps/web test
npm --prefix apps/web run typecheck
npm --prefix apps/web run build
uv run python -m pytest -q
```

并单独运行：

* slice compatibility tests
* exact-plane tests
* interpolated-slice tests
* periodic-wrap tests
* triclinic-plane tests
* slice Worker tests
* slice cancellation tests
* point-probe tests
* texture-axis mapping tests
* WebGL2 capability tests
* float texture tests
* float64 conversion tests
* shader compile/link tests
* ray-box tests
* texture sampling tests
* transfer-function tests
* opacity-correction tests
* CPU ray-march reference tests
* structure-depth tests
* clipping tests
* PNG export tests
* context-loss tests
* lifecycle tests
* accessibility tests
* mobile tests
* browser evidence runners
* performance/GPU/memory runners
* network audit
* security tests
* Phase 10J regressions
* Phase 10I regressions
* Phase 10H regressions
* Phase 10G regressions
* structure-viewer regressions
* service-backed integration
* no-skipped assertion
* secret scan

必须如实记录：

* passed
* failed
* skipped
* unavailable

不得把skipped写成passed。

---

## 75. Commit / Push / CI

全部完成后：

```bash
git status --short
git diff --stat
git add <only Phase 10J-6 related files>
git commit -m "Add volumetric slice and volume rendering"
git push origin master
```

等待current-HEAD CI。

必须确认：

* backend unit success
* frontend tests success
* typecheck success
* build success
* slice tests success
* volume shader tests success
* texture mapping tests success
* browser evidence success
* performance/GPU evidence success
* accessibility success
* Phase 10J contract success
* Phase 10J-1 parser success
* Phase 10J-2 renderer success
* Phase 10J-3 product success
* Phase 10J-4 product success
* Phase 10J-5 product success
* Phase 10I regression success
* Phase 10H regression success
* Phase 10G regression success
* structure-viewer regression success
* service-backed integration success
* no-skipped assertion success
* origin/master equals HEAD
* git status clean

不得伪造commit、CI run、GPU caps、frame time、texture size、测试数量或浏览器证据。

---

## 76. PASS 判定

PASS必须全部满足：

* 真实Slice Product实现
* 真实Direct Volume Renderer实现
* 使用真实Phase 10J-1 Runtime artifacts
* canonical texture axis正确
* 三个lattice-axis slices完成
* exact plane完成
* interpolated plane完成
* periodic wrap完成
* triclinic plane完成
* 2D heatmap完成
* 3D plane完成
* exact point probe完成
* window/palette语义完整
* WebGL2 gate完成
* R32F或正式等价GPU path完成
* float64转换误差披露完成
* 3D texture caps完成
* ray-box affine transform正确
* triclinic volume正确
* texture sampling正确
* transfer function完成
* opacity step correction完成
* front-to-back compositing完成
* bounded ray steps完成
* structure overlay/depth完成
* clipping完成
* PNG export完成
* WebGL2/texture fallback完成
* context loss完成
* lifecycle无泄漏
* no duplicate canvas/context/Worker
* no source field mutation
* no silent downsampling
* no artifact shader/Worker/WASM
* Chromium通过
* Firefox通过
* WebKit通过
* mobile通过或在低cap设备明确fallback
* accessibility完成
* performance/GPU/memory evidence完成
* Phase 10J-1至10J-5不回退
* 其他viewers不回退
* tests通过
* CI通过
* origin/master等于HEAD
* git status clean

---

## 77. PARTIAL_PASS 仅允许

仅允许：

* cell-centered fields继续DEFERRED_BY_DESIGN
* arbitrary oblique slice继续DEFERRED_BY_DESIGN
* direct-volume supercell继续DEFERRED_BY_DESIGN
* display-only downsampling继续DEFERRED_BY_DESIGN
* empty-space skipping未实现
* manual trilinear仅在缺少float-linear支持的浏览器启用
* mobile低cap设备只提供Slice/Isosurface fallback
* Slice model为ephemeral typed model而非持久化artifact，但hash/provenance完整
* optional numeric CSV export未实现
* WebKit存在记录完整的轻微像素差异
* npm/Python audit因既有registry问题unavailable，但依赖未变化且审计完整

以下缺失不得PARTIAL_PASS：

* 三轴slice
* interpolated slice
* point probe
* WebGL2 direct volume
* canonical texture mapping
* transfer function
* affine/triclinic ray mapping
* GPU caps
* browser matrix
* fallback
* lifecycle
* real Runtime artifact evidence

这些缺失必须FAIL。

---

## 78. FAIL 条件

以下任一情况必须FAIL：

* Slice只是预生成PNG
* Volume只是多张透明切片堆叠并声称ray marching
* 只有mock sphere或synthetic noise
* 不消费真实canonical payload
* texture axes错误
* row/column convention混用
* triclinic volume按axis-aligned box绘制
* float64静默降为float32
* source field被display window修改
* transfer function通过artifact代码控制
* shader来自artifact或CDN
* ray loop无hard cap
* texture超cap后仍尝试分配
* 自动静默降采样
* periodic边界采样不连续
* slice使用nearest plane却称为continuous interpolation
* point probe使用nearest voxel却称为精确值
* structure与volume空间错位
* volume永远遮挡所有atoms
* idle持续无意义render loop
* mode switch泄漏texture/context
* context loss后重复canvas
* 只有Chromium证据
* fixture截图冒充Runtime证据
* browser/GPU/performance evidence伪造
* skipped写成passed
* Phase 10J-5或其他viewers回退
* CI失败却声明PASS
* git不clean却声明完成

---

## 79. 最终报告格式

完成后必须输出：

# Phase 10J-6 Volumetric Slice / Volume Rendering Result

## 1. Conclusion

PASS / PARTIAL_PASS / FAIL

## 2. Baseline

* Phase 10J-5 commit
* initial HEAD
* branch
* origin/master
* initial status
* final HEAD
* final status

## 3. Pre-Implementation Audit

* field/grid support
* payload support
* WebGL capabilities
* slice strategy
* volume strategy
* precision/memory strategy
* dependency decision

## 4. Product Integration

* tool identity
* artifact detection
* mode composition
* field selection
* Planner routing
* readiness metadata

## 5. Slice Model

* axes
* fractional position
* exact/interpolated
* plane geometry
* orientation
* hashes
* provenance

## 6. Slice Sampling

* canonical indexing
* periodic wrap
* non-periodic boundaries
* interpolation
* Worker
* cancellation
* deterministic references

## 7. Slice UI

* 2D heatmap
* 3D plane
* window
* palette
* legend
* point probe
* structure linking
* PNG export

## 8. WebGL2 / GPU Gate

* WebGL2
* max texture size
* float texture support
* texture dimensions
* texture bytes
* mobile caps
* fallbacks

## 9. Texture Pipeline

* source dtype
* GPU dtype
* float64 conversion
* conversion error
* texture-axis mapping
* upload
* cache
* hashes

## 10. Volume Ray Marcher

* affine ray-box
* triclinic mapping
* sample count
* texture sampling
* periodicity
* transfer function
* opacity correction
* compositing
* early termination

## 11. Structure / Scene Integration

* one canvas/context
* structure overlay
* depth policy
* unit cell
* clipping
* camera
* projection
* supercell status

## 12. Interaction / Inspector

* slice probe
* 2D ↔ 3D selection
* volume display status
* field metadata
* transfer-function metadata
* selected coordinates/values

## 13. Export / Fallback

* Slice PNG
* Volume PNG
* no-WebGL2
* texture over cap
* float texture unavailable
* shader failure
* context loss

## 14. Browser Evidence

* Chromium
* Firefox
* WebKit
* mobile
* screenshots
* console
* network
* Runtime artifact cases
* fallback cases

## 15. Accessibility

* keyboard
* focus
* slice table
* point values
* transfer-function text
* capability status
* reduced motion
* mobile

## 16. Performance / GPU / Memory

* payload
* slicing
* conversion
* texture upload
* shader initialization
* frame time
* ray steps
* GPU bytes
* caches
* cleanup
* near-cap behavior

## 17. Security

* artifact JS
* shader
* Worker/WASM
* external URLs
* transfer functions
* allocation caps
* shader loop caps
* races
* errors
* secrets
* dependencies

## 18. Scientific References

* slice patterns
* interpolation
* periodic wrap
* texture mapping
* CPU ray marcher
* opacity correction
* triclinic domain
* pixel tolerances

## 19. Tests

* compatibility
* slice
* point probe
* texture
* shader
* volume
* structure depth
* lifecycle
* accessibility
* browser
* performance
* regressions
* service-backed
* no-skipped

## 20. Evidence

* directory
* Runtime artifacts
* slice hashes
* GPU captures
* shader hashes
* screenshots
* logs
* metrics
* audits
* replay commands

## 21. Files

列出主要implementation、shader、Worker、tests、fixtures、runner、evidence、docs和persistent文件。

## 22. Explicitly Deferred

* cell-centered fields
* arbitrary oblique slices
* vector/complex volume
* scientific resampling
* display downsampling，若未实现
* empty-space skipping，若未实现
* volume segmentation
* time-dependent 4D volume
* remote GPU rendering
* scientific feature detection

## 23. Checks

* diff
* lock
* dependency tree
* Three.js tree
* frontend tests
* typecheck
* build
* backend tests
* browser runners
* GPU/performance runners
* network
* secrets

## 24. Commit / CI

* commit
* HEAD
* CI run
* unit
* frontend
* build
* slice tests
* shader/volume tests
* browser
* performance
* accessibility
* service-backed
* no-skipped
* origin
* git status

## 25. Readiness

预期：

```text
volumetric contracts: READY
VASP/CUBE parsers: READY
generic isosurface renderer: READY
Charge / Spin Density Product: READY
Electrostatic Potential Product: READY
ELF / Orbital Product: READY
lattice-axis Slice Product: READY
exact slice planes: READY
interpolated slice planes: READY
2D quantitative heatmap: READY
3D slice plane: READY
slice point probing: READY
WebGL2 Direct Volume Renderer: READY
canonical 3D texture mapping: READY
triclinic volume rendering: READY
transfer functions: READY
structure overlay: READY
clipping: READY
PNG export: READY
Chromium: READY
Firefox: READY
WebKit: READY
mobile: READY or CAPABILITY_FALLBACK
accessibility: READY
performance / GPU caps: READY
security: READY
cell-centered volume: NOT_IMPLEMENTED
vector / complex volume: NOT_IMPLEMENTED
arbitrary scientific slicing: NOT_IMPLEMENTED
volume segmentation: NOT_IMPLEMENTED
full volumetric platform: READY_WITH_EXPLICIT_LIMITS
```

## 26. Whether Allowed to Enter Next Phase

可以 / 不可以

只有 Phase 10J-6 完成、current-HEAD CI通过、真实Runtime artifacts、Slice科学reference、WebGL2 Direct Volume Renderer、GPU/Memory/Browser/Security Evidence闭合且git clean后，才允许进入仓库正式路线图中的下一阶段。

必须读取真实路线图确定下一阶段名称，不得由执行Agent自行创造Phase编号或名称。

现在开始执行。

先读取真实 Phase 10J-5 Result、Phase 10J grid/payload contracts、Phase 10J-2 Three.js/Worker基础设施、Phase 10J-3至10J-5产品实现及当前Browser evidence runners，输出 Pre-Implementation Audit；然后完成三轴slice、continuous interpolation、2D/3D slice、point probe、WebGL2 3D texture、float precision audit、affine ray marcher、transfer function、structure depth integration、fallback、browser matrix、GPU/performance/security、docs、commit和CI闭环。

不得把本阶段扩展为scientific resampling、arbitrary oblique slicing、vector/complex volume、segmentation、Bader analysis或外部GPU服务。


---END---
