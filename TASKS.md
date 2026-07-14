---TASK---
 状态：已完成

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

完成时间：2026-07-14 22:08:32 +08:00

修改文件：`packages/artifact-core/mdi_artifact_core/brillouin_zone_contract.py`、`packages/artifact-core/mdi_artifact_core/__init__.py`、`tests/test_phase10i_brillouin_zone_contract.py`、`scripts/generate_phase10i_brillouin_zone_evidence.py`、`docs/phase10i/`、`docs/13_SHARED_SCHEMA_SPEC.md`、`docs/index.md`、`persistent/*.md`。

修改摘要：实现五个 versioned inert Brillouin Zone schema contracts、row-vector physics-`2*pi` reciprocal math、source/primitive/conventional transforms、first-BZ canonical polyhedron topology、high-symmetry point/path/provider/time-reversal policy、manifest、hard caps、typed validators、deterministic hashes/replay、六套 bounded fixtures、11 类 negative evidence 和 independent NumPy/SciPy references。保持 `structure.brillouin_zone` NOT_REGISTERED/NOT_EXECUTABLE；未新增 adapter、planner/runtime、frontend renderer、依赖、网络或 real LLM 能力。

测试结果：Phase 10I `39 passed`；focused cross-phase `157 passed`；frontend `193 passed`；backend full `605 passed, 23 skipped, 11 warnings`；typecheck/build、`uv lock --check`、`git diff --check`、Phase 10 closure/browser regression均成功；evidence markers、无外部网络/API/path和 Phase 10I secret scan通过。`npm audit` 因 configured npmmirror endpoint 404 `NOT_IMPLEMENTED` 为 unavailable，未声称 clean；无 dependency/lockfile 变更。本机 Docker/service env 不可用，GitHub CI service-backed 与 no-skipped assertion成功。

提交 / CI：implementation commit `653ea133d5791db3f6879b05dc66a2e397d0d646`；CI run `29339358234` success（unit、frontend typecheck/build、service-backed integration、no-skipped assertion）。完成记录提交需再次通过 current-HEAD CI 后才允许删除本 block。

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



---TASK---
 状态：待处理
# Phase 10I-2：Brillouin Renderer / Evidence

进入 Phase 10I-2：Brillouin Renderer / Evidence。

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
* Phase 10H-5：Phonon Animation
* Phase 10I：Brillouin Zone Contract
* Phase 10I-1：Brillouin Zone Adapter

必须以真实 Phase 10I-1 Result 为基线，记录实际：

* Phase 10I-1 commit
* Phase 10I-1 HEAD
* Tool Registry 状态
* schema versions
* provider versions
* CI run
* backend/frontend test counts
* origin/master
* working-tree status

不得根据本 prompt 编造 commit、HEAD、CI、浏览器版本、测试数或性能指标。

本阶段必须产生真实 Three.js Renderer、正式前端产品集成和真实 Browser/API/Performance/Security Evidence，不是 planning、readiness、contract-only、fixture-only 或静态 JSON preview 阶段。

---

## 1. 本阶段总目标

将 Phase 10I-1 生成的声明式 artifacts：

```text
reciprocal_lattice.json
brillouin_zone.json
kpath.json
brillouin_zone_manifest.json
```

接入应用内置、受控、资源受限的 Three.js reciprocal-space renderer：

```text
structure.brillouin_zone
        ↓
persisted artifacts
        ↓
artifact contract validation
        ↓
Brillouin Zone scene mapper
        ↓
Three.js renderer
        ↓
faces / edges / vertices
        ↓
reciprocal axes
        ↓
high-symmetry points
        ↓
high-symmetry paths
        ↓
picking / inspector
        ↓
camera / clipping / export / fallback
        ↓
Chromium / Firefox / WebKit / mobile evidence
```

本阶段必须实现：

* 正式 BZ artifact consumer
* Brillouin Zone scene mapper
* Three.js BZ renderer
* translucent faces
* bounded face triangulation
* canonical edges
* canonical vertices
* reciprocal axes
* high-symmetry points
* high-symmetry labels
* high-symmetry path segments
* discontinuity-aware path rendering
* point picking
* face picking，若满足性能与可访问性要求
* edge/path picking，若能可靠实现
* reciprocal-space inspector
* camera rotate / zoom / pan / reset
* camera presets
* perspective / orthographic projection
* show/hide faces
* show/hide edges
* show/hide vertices
* show/hide reciprocal axes
* show/hide high-symmetry points
* show/hide labels
* show/hide k-path
* opacity control
* clipping或section controls，若能复用现有稳定实现
* deterministic fixed-camera screenshot
* PNG export
* WebGL fallback
* context-loss handling
* lifecycle cleanup
* keyboard accessibility
* reduced-motion behavior
* mobile touch controls
* Browser/API evidence
* performance evidence
* security evidence
* docs/persistent
* current-HEAD CI closure

---

## 2. 本阶段明确不实现

不得实现或宣称：

* electronic band calculation
* phonon calculation
* force constants
* DFT
* DFPT
* arbitrary Python
* notebook execution
* uploaded script execution
* remote reciprocal-space service
* external API
* custom arbitrary k-path editor
* user-authored reciprocal mesh
* Monkhorst–Pack generation
* integration weights
* irreducible Brillouin zone wedge
* magnetic Brillouin zone
* surface Brillouin zone
* slab/2D BZ
* 1D BZ
* Fermi surface
* isoenergy surface
* Wannier interpolation
* band unfolding
* volumetric reciprocal data
* reciprocal charge density
* electron–phonon coupling
* full Band–BZ linked product
* full Phonon–BZ linked product
* bidirectional synchronized selection
* custom path persistence
* BZ geometry editing
* vertex/face editing
* artifact-provided JavaScript
* artifact-provided HTML
* artifact-provided CSS
* artifact-provided shader
* artifact-provided GLSL
* artifact-provided material class
* artifact-provided texture
* external URL
* CDN
* iframe
* remote module
* remote worker
* arbitrary renderer config
* renderer bundle embedded in artifact
* production MP4/WebM/GIF export

完整 Band–BZ 联动必须留给：

```text
Phase 10I-3：Band–BZ Linked View
```

本阶段只允许提供未来联动所需的稳定 point/segment identity和有限的“打开相关 artifact”入口，不得提前实现完整双向同步产品。

---

## 3. Public Tool 与产品身份

Phase 10I-1 已正式注册：

```text
structure.brillouin_zone
```

本阶段优先继续使用该 canonical tool，不新增语义重叠的：

```text
structure.brillouin_zone_3d
structure.bz_viewer
structure.reciprocal_viewer
```

正确架构：

```text
structure.brillouin_zone
        ↓
生成 canonical artifacts
        ↓
前端应用内置 renderer 自动识别并渲染
```

只有仓库现有 Tool Registry 架构明确要求数据生成和交互产品分离时，才允许注册额外 tool；必须在 Pre-Implementation Audit 中说明理由、避免重叠路由，并确保只有一个用户推荐入口。

Phase 10I-2 完成后，Registry/产品 metadata 可以更新为：

```text
adapter: READY
runtime: READY
JSON artifacts: READY
3D renderer: READY
browser evidence: READY
mobile: READY
accessibility: READY
performance: READY
security: READY
full standalone BZ product: READY
Band–BZ linkage: NOT_IMPLEMENTED
```

---

## 4. Baseline Verification

开始前执行：

```bash
cd "E:\1project\Material Data Intelligence"

git status --short
git branch --show-current
git rev-parse HEAD
git log --oneline -35
git remote -v
git rev-parse origin/master
```

必须确认：

* repository 为 Material Data Intelligence
* branch 为 `master`
* working tree clean
* HEAD 包含 Phase 10I-1
* origin/master 状态正确
* `structure.brillouin_zone` 已注册
* Runtime execution 已完成
* reciprocal/BZ/kpath artifacts 存在
* contract validators 存在
* Phase 10I-1 current-HEAD CI 成功

如果 working tree 不干净，停止并报告，不得覆盖未知变更。

---

## 5. 必读实现

开始实现前必须完整阅读真实代码。

### 5.1 Phase 10I / 10I-1

必须定位并阅读：

* reciprocal lattice schema
* BZ schema
* k-path schema
* manifest schema
* schema versions
* canonical IDs
* vertex ordering
* edge ordering
* face loops
* face normals
* generator planes
* high-symmetry point IDs
* segment IDs
* discontinuity model
* path variants
* units
* `2π` convention
* tolerance policy
* caps
* content hashes
* security flags
* Adapter
* Tool Registry
* Planner routing
* runtime integration
* service-backed smoke
* fixtures
* independent reference tests

Renderer 不得重新解释或重算这些科学语义。

### 5.2 Existing Structure / Trajectory / Phonon Renderers

必须阅读并优先复用：

* Three.js dependency gate
* lazy loading
* canvas lifecycle
* WebGL context lifecycle
* renderer creation/disposal
* camera controls
* perspective/orthographic switching
* clipping planes
* resize handling
* devicePixelRatio caps
* screenshot/PNG export
* WebGL fallback
* context loss/restore
* geometry/material disposal
* event-listener cleanup
* ResizeObserver cleanup
* requestAnimationFrame cleanup
* picking
* raycasting
* inspector
* keyboard controls
* touch controls
* reduced motion
* mobile layout
* accessibility summaries
* browser evidence runners
* performance metrics collectors

不得建立第二套互不兼容的 Three.js framework。

### 5.3 Frontend Artifact Integration

阅读：

* Results view
* Artifact Gallery
* preview dispatch
* viewer tabs
* loading/error states
* manifest detection
* validation-state display
* summary/recipe views
* developer mode
* screenshot evidence selectors

---

## 6. 修改前必须输出审计

修改代码前输出：

# Phase 10I-2 Brillouin Renderer Pre-Implementation Audit

## 1. Baseline

* Phase 10I-1 commit
* current HEAD
* branch
* origin/master
* git status
* current CI
* schema versions
* dependency state

## 2. Artifact Contract

* reciprocal lattice artifact
* BZ artifact
* kpath artifact
* manifest
* coordinate convention
* units
* canonical IDs
* caps
* security

## 3. Existing Renderer Infrastructure

* Three.js version
* scene lifecycle
* camera
* controls
* picking
* clipping
* export
* mobile
* accessibility
* fallback
* performance instrumentation

## 4. Geometry Mapping Plan

说明：

* vertices 如何映射
* faces 如何 triangulate
* edges 如何绘制
* point markers 如何绘制
* labels 如何绘制
* k-path 如何绘制
* discontinuities 如何处理
* axes 如何绘制
* selection 如何映射 canonical IDs

## 5. Product Integration

* artifact detection
* viewer entry point
* route/component
* controls
* inspector
* fallback
* PNG export

## 6. Scope Boundary

明确：

* 本阶段实现 standalone BZ product
* 不实现完整 Band–BZ linked view
* 不实现电子结构计算
* 不实现 magnetic/surface BZ

## 7. Planned Files

列出预计修改/新增的实现、测试、runner、evidence、docs 和 persistent 文件。

审计完成后直接继续，不等待人工确认。

---

## 7. Renderer Input Validation

Renderer 只能消费已经通过 Phase 10I validator 的 artifacts。

在初始化 WebGL 前必须验证：

* manifest schema
* reciprocal lattice schema
* BZ schema
* kpath schema，若存在
* artifact hashes
* structure binding
* reciprocal convention
* units
* primitive lattice hash
* BZ geometry hash
* kpath reciprocal binding
* vertices/edges/faces caps
* point/segment caps
* all numbers finite
* no executable fields
* no external URLs
* no unexpected artifact references

验证失败时：

* 不创建 canvas
* 不创建 WebGL context
* 显示 typed error
* 保留 JSON preview
* 不尝试“修复”无效 artifact

前端不得因为绘制方便而放宽后端合同。

---

## 8. Coordinate Mapping

Canonical reciprocal Cartesian coordinates单位为：

```text
Å⁻¹
```

并使用：

```text
physics_2pi
```

Renderer必须直接使用 canonical Cartesian坐标。

不得：

* 再次乘 `2π`
* 再次除 `2π`
* 根据bbox猜单位
* 使用source conventional reciprocal coordinates代替primitive canonical coordinates
* 将fractional coordinates直接当Cartesian

### 8.1 Scene Scaling

Three.js scene可以应用统一视觉缩放：

```text
scene_position = reciprocal_cartesian_position × visual_scale
```

但必须：

* 仅使用一个uniform scalar
* 保持角度、形状、拓扑
* 在inspector中显示原始 Å⁻¹ 坐标
* visual scale不进入artifact
* visual scale不改变科学identity
* screenshot metadata记录scale策略

不得进行各轴独立归一化，否则会扭曲BZ几何。

---

## 9. Face Triangulation

Artifacts中的face是ordered planar polygon loops。

Renderer必须安全triangulate。

允许：

* 使用 Three.js `ShapeUtils.triangulateShape`
* 使用经过验证的平面投影 + ear clipping
* 复用项目已有bounded polygon triangulation helper

不得：

* 信任任意artifact triangles
* 使用artifact-provided shader
* 将3D polygon直接错误投影到XY平面
* 对非共面polygon继续渲染
* 无限递归triangulation
* 无上限分配

### 9.1 Projection

对每个face：

1. 使用canonical outward normal。
2. 选择稳定局部正交basis。
3. 将face vertices投影到2D。
4. 根据合同winding验证方向。
5. triangulate。
6. 将triangle indices映射回3D。
7. 验证triangle area finite/non-zero。
8. 验证triangles总面积与face area在容差内一致。

如果triangulation失败：

* typed renderer mapping error
* 不渲染错误face
* 默认整个BZ进入fallback或明确partial refusal
* 不得静默显示破洞多面体并声称成功

---

## 10. Face Rendering

必须实现半透明face rendering。

要求：

* application-owned material
* no artifact material class
* bounded opacity
* depth behavior明确
* double-sided仅在必要时使用
* outward normals保留
* selected face highlight
* hover/focus state
* high-contrast模式可识别
* no per-face unbounded material creation

推荐：

* 一个或少量共享materials
* indexed BufferGeometry
* face ID到triangle range映射
* selection通过共享highlight material或attribute实现

### 10.1 Transparency

必须明确处理透明排序限制。

至少验证：

* 不同camera angles
* face overlap
* inside/outside viewing
* orthographic/perspective
* mobile GPU

不得通过关闭所有depth test造成错误前后关系。

可采用：

* transparent faces + opaque edges
* conservative opacity range
* depthWrite策略
* renderOrder
* backface/frontface policy

必须在docs中说明浏览器透明渲染限制。

---

## 11. Edge Rendering

必须使用canonical edges。

要求：

* 不从triangles推断重复internal diagonals
* 不显示triangulation内部边
* canonical endpoint order
* one line segment per scientific edge
* shared LineSegments geometry
* bounded line width策略
* selected edge/path区分
* finite coordinates

不得为每条edge创建独立Three.js object。

---

## 12. Vertex Rendering

BZ polyhedron vertices可以使用：

* instanced spheres
* Points
* shared geometry markers

要求：

* stable vertex ID
* picking mapping
* show/hide
* size bounded
* no one-material-per-vertex
* no label injection
* no duplicate marker

Vertex默认可关闭，以避免视觉拥挤，但必须可以开启用于inspection/evidence。

---

## 13. Reciprocal Axes

必须显示canonical primitive reciprocal basis：

```text
b1
b2
b3
```

要求：

* origin为Γ
* direction来自 reciprocal lattice artifact
* length策略明确
* visual scaling uniform
* labels使用plain text
* units显示 Å⁻¹
* show/hide
* selected axis inspection可选
* no arbitrary artifact label HTML

不得用real-space `a、b、c` 向量代替。

可同时显示：

* `b₁`
* `b₂`
* `b₃`

但必须保留安全 ASCII identity：

```text
b1
b2
b3
```

---

## 14. High-Symmetry Points

必须渲染 kpath artifact中的canonical points。

每个point映射：

* point ID
* label key
* display label
* aliases
* fractional reciprocal coordinates
* Cartesian reciprocal coordinates
* provider/convention
* incident path segments

要求：

* point marker共享geometry/material
* stable picking identity
* show/hide
* selected/highlight state
* labels可独立show/hide
* no duplicate point marker for aliases
* duplicate-coordinate labels按合同策略合并或偏移显示
* all labels plain text

不得根据display label重新匹配坐标。

---

## 15. High-Symmetry Labels

标签优先使用受控HTML DOM overlay或安全Canvas text，由应用生成。

不得：

* 执行artifact HTML
* 使用dangerouslySetInnerHTML
* 注入MathJax payload
* 加载外部字体
* 使用remote sprite
* 允许任意CSS

标签系统必须：

* textContent rendering
* bounded label count
* bounded string length
* safe Unicode normalization
* viewport clipping
* overlap strategy
* hide labels控制
* mobile降级
* selected point优先
* screen-reader textual list

### 15.1 Label Overlap

必须有确定性策略，例如：

* selected/hovered labels优先
* 其余按screen-space距离过滤
* 固定最大可见标签数
* deterministic tie-break by point ID
* camera变化时bounded update

不得每帧进行无界O(N²)布局。

---

## 16. K-Path Rendering

必须使用canonical segments。

要求：

* start/end point IDs
* segment ID
* variant ID
* deterministic order
* line geometry共享
* selected/highlight state
* show/hide
* distinct from ordinary BZ edges
* path color/style由应用固定
* no artifact-defined shader/style code

### 16.1 Discontinuities

对于：

```text
X | K
```

一类discontinuity：

* 不绘制X到K的连接线
* UI/inspector显示path break
* path order保留
* 不通过空间接近度猜连接
* 不把branch gap画成scientific segment

### 16.2 Alternative Variants

如果artifact含multiple variants：

* 提供variant selector，或
* 只显示canonical selected variant

不得把所有variants叠加而不说明。

如果实现selector：

* bounded options
* stable variant IDs
* switching清理selection
* no duplicate geometries
* accessibility labels

---

## 17. Picking

必须支持至少：

* high-symmetry point picking

建议支持：

* face picking
* vertex picking
* k-path segment picking

Edge picking若line raycasting不稳定，可以defer，但必须如实记录。

### 17.1 Identity

Picking结果必须映射到canonical IDs：

```text
BZPointRef {
  pointId
}

BZVertexRef {
  vertexId
}

BZFaceRef {
  faceId
}

BZSegmentRef {
  variantId,
  segmentId
}
```

不得使用临时triangle index作为用户可见identity。

### 17.2 Selection State

必须保证：

* camera变化不改变selection
* opacity变化不改变selection
* show/hide对应项时清理无效selection
* artifact切换清理selection
* variant切换重新校验segment selection
* context restore后selection可恢复或明确清理
* stale IDs不得指向新artifact对象

---

## 18. Reciprocal-Space Inspector

Inspector至少支持以下内容。

### 18.1 Point Inspector

* point ID
* display label
* aliases
* fractional reciprocal coordinates
* Cartesian reciprocal coordinates
* units
* provider
* convention
* incident segments
* path position
* time-reversal metadata

### 18.2 Face Inspector

* face ID
* vertex IDs
* edge IDs
* area
* centroid
* outward normal
* generator integer vector
* generator Cartesian vector
* plane offset
* incident topology
* validation residual

### 18.3 Vertex Inspector

* vertex ID
* Cartesian coordinates
* reciprocal fractional coordinates
* incident faces
* incident edges

### 18.4 Segment Inspector

* segment ID
* variant
* start/end point
* labels
* length
* order
* discontinuity context
* provider/convention

Inspector不得只显示raw JSON。

Developer details区域可以展示完整contract字段，但主界面必须是可读的科学语义。

---

## 19. Camera

必须复用现有viewer controls。

至少提供：

* rotate
* zoom
* pan
* reset
* fit to BZ
* fit to selected point/face，若实现
* perspective projection
* orthographic projection

### 19.1 Camera Presets

必须提供确定性 presets：

* isometric
* +b1
* +b2
* +b3
* opposite views，若UI不拥挤
* fit-all

Preset必须基于reciprocal basis，不得假定world X/Y/Z就是科学b1/b2/b3。

### 19.2 Deterministic Screenshot Camera

Evidence screenshot必须固定：

* projection
* camera position
* target
* up vector
* zoom
* viewport
* devicePixelRatio
* face opacity
* visible layers
* selected path variant

---

## 20. Clipping

优先复用现有structure viewer clipping infrastructure。

如果实现：

* one or bounded clipping planes
* application-owned controls
* reset
* finite plane parameters
* show/hide
* no artifact-supplied plane equation
* no unbounded clipping count

Clipping只影响显示，不改变scientific BZ geometry或artifact。

如果clipping无法安全复用，本阶段可明确defer，不得放一个无功能按钮。

---

## 21. Controls

UI至少提供：

* Faces toggle
* Edges toggle
* Vertices toggle
* Reciprocal axes toggle
* High-symmetry points toggle
* Labels toggle
* K-path toggle
* Face opacity slider
* Path variant selector，若存在
* Perspective/orthographic selector
* Camera preset
* Reset camera
* Export PNG
* Open JSON data
* Open summary
* Open recipe

所有controls必须：

* keyboard operable
* semantic labels
* visible focus
* bounded values
* stable state
* mobile可用
* no hidden hover-only operation

---

## 22. Product Integration

Renderer必须进入现有材料科学结果工作台。

推荐识别逻辑：

```text
manifest + validated brillouin_zone artifact
        ↓
Brillouin Zone tab / preview
```

不得只做独立测试页作为唯一实现。

至少提供：

* loading state
* validation state
* renderer-ready state
* fallback state
* context-lost state
* over-cap state
* invalid-artifact state
* no-kpath state
* full viewer state

### 22.1 No K-Path

BZ geometry有效但kpath unavailable时：

* 仍显示BZ polyhedron
* 隐藏/禁用path controls
* 显示明确warning
* 不伪造point/path

---

## 23. Planner Routing 更新

Phase 10I-1 中，3D请求可能被标记deferred或降级为JSON数据。

Phase 10I-2完成后，允许将明确的交互查看请求路由到：

```text
structure.brillouin_zone
```

正向示例：

* 打开这个晶体的三维布里渊区
* 显示可旋转的第一布里渊区
* 可视化这个结构的高对称点和k路径
* 用3D查看倒易晶格
* Open an interactive Brillouin zone viewer
* Show the first Brillouin zone in 3D
* Visualize reciprocal axes and the high-symmetry path

Planner/Tool description必须说明：

* Adapter生成声明式数据
* Renderer由应用提供
* 不计算电子能带
* 不计算声子
* 不使用外部资源

### 23.1 Negative Routing

不得误路由：

* 计算电子能带
* 运行DFT
* 计算声子
* 生成Fermi surface
* 生成Monkhorst-Pack网格
* 编辑k路径
* 显示surface BZ
* 显示magnetic BZ
* 播放phonon mode
* 打开MD trajectory

必须更新positive/negative routing tests。

---

## 24. Limited Handoff Readiness

本阶段必须为Phase 10I-3保留稳定接口，但不实现完整linked view。

允许：

* Inspector显示point/segment IDs
* 提供“相关phonon band artifact可用”状态
* 提供只读compatibility result
* 提供“Open related band artifact”普通导航
* 保留selection callback interface但不启用双向同步

禁止：

* 点击BZ path立即同步band chart cursor
* 点击band point立即在BZ中高亮
* shared cross-panel selection state
* custom path editing
* band path重算
* frequency/energy-linked rendering

---

## 25. PNG Export

必须复用已有安全export机制。

要求：

* fixed camera export
* current visibility settings
* current opacity
* current selected variant
* optional transparent background
* optional publication background，若已有
* bounded resolution
* bounded devicePixelRatio
* no external assets
* deterministic metadata
* Blob URL revoke
* no artifact JS

Export artifact metadata至少记录：

* source BZ artifact hash
* schema version
* camera
* projection
* viewport
* visibility
* opacity
* selected variant
* timestamp，若项目export metadata要求
* renderer version

PNG本身不是scientific data contract的替代品。

---

## 26. WebGL Fallback

必须有明确fallback。

当：

* WebGL不可用
* WebGL context创建失败
* context lost
* renderer dependency加载失败
* geometry mapping失败
* device资源不足

必须显示：

* formula/structure identity
* reciprocal convention
* reciprocal matrix
* BZ vertex/edge/face counts
* BZ volume
* high-symmetry points
* path segments
* provider
* warnings
* JSON preview入口
* summary/recipe入口
* typed status

不得显示空白黑框。

---

## 27. Context Loss / Restore

必须测试：

* `webglcontextlost`
* preventDefault
* stop animation/render loop
* display context-lost state
* cleanup stale GPU resources
* restore/reinitialize
* no duplicate canvas
* no duplicate context
* no duplicate controls
* no duplicate listeners
* selection恢复或明确清理
* camera恢复或明确reset

Context restore后不得重复创建整个React subtree或保留旧renderer引用。

---

## 28. Lifecycle

必须保证：

* 一个viewer实例最多一个canvas
* 一个viewer实例最多一个WebGL context
* 一个render loop
* controls只创建一次
* ResizeObserver只创建一次
* artifact切换清理旧scene
* route切换dispose
* unmount dispose
* screenshot Blob URL revoke
* geometries dispose
* materials dispose
* textures为0或正确dispose
* raycaster references清理
* DOM labels清理
* event listeners清理
* clipping resources清理
* context restore不泄漏

必须增加：

* repeated mount/unmount stress
* repeated artifact switch
* repeated variant switch
* repeated projection switch
* repeated label toggle
* repeated PNG export
* context loss/restore cycles

---

## 29. Performance Caps

必须复用Phase 10I caps，并增加renderer caps。

至少限制：

* max vertices
* max edges
* max faces
* max triangles
* max points
* max path segments
* max labels
* max visible labels
* max materials
* max geometries
* max draw calls
* max pixel ratio
* max export dimensions
* max inspector rows
* max DOM overlay updates
* max triangulation work
* max raycast targets

不得在frontend接受超过contract hard caps的geometry。

### 29.1 Triangles

必须计算：

```text
triangle_count = Σ(face_vertex_count - 2)
```

或实际triangulation结果。

设置hard cap。

Over-cap时：

* 不初始化renderer
* 显示typed resource-limit错误
* 保留JSON preview
* 不静默减少faces

---

## 30. Performance Strategy

优先采用：

* one indexed face geometry或少量batched geometries
* one LineSegments geometry for BZ edges
* one LineSegments geometry for k-path
* instanced/Points markers
* shared materials
* bounded DOM labels
* render-on-demand when static
* controls change触发render
* no continuous animation loop，除非交互需要
* tab hidden停止render
* no per-frame geometry rebuild
* no repeated triangulation

BZ是静态场景，不应在idle状态持续占用requestAnimationFrame。

如现有controls依赖animation loop，应改为：

* interaction期间render
* control change render
* resize render
* selection render
* idle停止

---

## 31. Required Performance Metrics

必须记录：

* artifact bytes
* vertex count
* edge count
* face count
* triangle count
* point count
* path segment count
* visible label count
* draw calls
* geometries
* materials
* textures
* canvas count
* context count
* initial mapping time
* renderer initialization time
* first meaningful render time
* camera interaction responsiveness
* picking latency
* label update cost
* PNG export time
* artifact-switch cleanup
* memory trend，若测试工具可用

至少覆盖：

1. simple cubic
2. BCC
3. FCC
4. hexagonal
5. triclinic
6. near-cap synthetic valid BZ
7. kpath unavailable
8. many-label bounded case
9. repeated artifact switching
10. context loss/restore

Acceptance thresholds必须基于现有viewer预算和真实测试结果，不得为通过而任意放宽。

---

## 32. Accessibility

必须完成：

* semantic controls
* keyboard operation
* visible focus
* screen-reader BZ summary
* selected object textual description
* no color-only status
* high-contrast distinguishable edges/path/selection
* labels可以隐藏
* reduced-motion support
* touch target size
* projection/control labels
* opacity slider value text
* fallback可读
* error可读
* keyboard reset camera
* keyboard toggle layers
* point list/table alternative

### 32.1 Textual Alternative

必须提供至少一个可访问文本视图：

* high-symmetry point table
* path segment table
* selected face/point inspector
* geometry summary

用户不使用3D canvas也能获得核心科学信息。

### 32.2 Reduced Motion

BZ本身静态，但camera transition/preset若含动画：

* reduced motion下立即切换
* 不做长动画
* 不自动旋转
* 默认不启用auto-rotate

本阶段建议完全不实现auto-rotate。

---

## 33. Mobile

必须验证：

* portrait
* landscape
* touch rotate
* pinch zoom
* pan
* reset
* toggles
* opacity slider
* point picking
* inspector drawer/panel
* label visibility
* projection switch
* PNG export，若移动端允许
* no horizontal page overflow
* no control overlap
* fallback
* context lifecycle

移动端允许：

* 默认隐藏部分非关键labels
* 降低pixel ratio
* 禁用near-cap scene
* 限制export resolution

但必须是明确、可预测的策略。

---

## 34. Browser Evidence Matrix

必须使用真实浏览器：

* Chromium
* Firefox
* WebKit
* mobile viewport

每个desktop浏览器至少验证：

* scene loads
* faces
* edges
* axes
* points
* labels
* k-path
* camera rotate/zoom/pan
* reset
* projection switch
* toggles
* opacity
* picking
* inspector
* PNG export
* console
* network
* lifecycle
* no duplicate canvas/context

Mobile至少验证：

* rendering
* touch controls
* point selection
* inspector
* controls
* no overflow
* fallback

---

## 35. Required Screenshots

至少保存以下类型截图，实际命名服从仓库规范：

1. simple cubic isometric
2. BCC fixed camera
3. FCC fixed camera
4. hexagonal with labels/path
5. triclinic fixed camera
6. reciprocal axes
7. selected high-symmetry point
8. selected face inspector
9. orthographic projection
10. faces hidden / edge-only
11. kpath unavailable fallback
12. invalid artifact fallback
13. WebGL unavailable/context-lost state
14. mobile portrait
15. mobile landscape
16. accessibility text/table view
17. PNG export result
18. near-cap scene

每张capture必须记录：

* browser/version
* viewport
* deviceScaleFactor
* artifact hash
* camera
* projection
* opacity
* visible layers
* selected point/face
* path variant
* screenshot hash

不得把单浏览器截图复制后声称多浏览器证据。

---

## 36. Browser Console / Network

所有正式evidence cases必须记录：

* console errors
* console warnings
* page errors
* failed requests
* external requests
* resource types
* WebGL warnings
* context messages

必须证明：

```text
NO_BRILLOUIN_RENDERER_EXTERNAL_NETWORK_REQUESTS
```

允许的网络仅限项目本地/测试服务。

不得加载：

* CDN
* external fonts
* textures
* shaders
* modules
* analytics
* remote maps
* remote structure data

---

## 37. Security

必须自动审计：

* no artifact JavaScript
* no artifact HTML
* no artifact CSS
* no artifact shader
* no remote texture
* no external URL
* no iframe
* no eval
* no Function constructor
* no dynamic import from artifact
* no arbitrary expression
* no arbitrary renderer settings
* no path traversal
* no local file read
* no secret
* no token
* no private URL
* no stack/path disclosure
* labels rendered via textContent
* provider metadata plain text
* bounded arrays
* finite numbers
* safe export filename
* renderer application-owned

必须输出：

```text
NO_SECRET_PATTERN_HITS
```

### 37.1 Shader Boundary

Three.js内部或应用源码中的固定shader是依赖实现的一部分。

必须明确：

* artifact不能携带shader源码
* artifact不能指定shader URL
* artifact不能选择任意material class
* artifact只能提供科学数据和有限非权威display hints
* renderer忽略未知display fields

---

## 38. Dependency Audit

优先复用现有Three.js依赖。

不得为BZ单独引入第二个大型3D framework。

如果新增triangulation/label依赖：

* 必须证明现有能力不足
* 记录版本
* license
* size
* transitive dependencies
* security findings
* tree-shaking/lazy-loading
* browser support
* offline behavior
* lockfile changes

优先使用：

* Three.js已有helper
* 小型内部bounded pure function

npm audit若既有registry不可用：

* 记录unavailable
* 不得写clean
* 不得写PASS
* 检查lockfile变化和dependency reachability

---

## 39. API Evidence

Phase 10I-1已有service-backed smoke；本阶段必须补正式端到端evidence。

至少覆盖：

* simple cubic
* BCC或FCC
* hexagonal
* triclinic
* kpath unavailable case
* invalid artifact/negative case

记录sanitized：

* request
* selected tool
* AnalysisPlan
* plan ID/hash
* job ID
* tool call
* artifacts
* schema versions
* validation state
* artifact hashes
* final status
* browser entry artifact

必须证明真实job生成的artifacts被renderer消费，不得只用手写fixture完成全部browser evidence。

Fixture可以用于negative/cap测试，但正式主证据必须包含QueueWorkerRuntime产物。

---

## 40. Formal Product Routing

完成Browser/Performance/Security evidence后，才允许将产品说明更新为：

> 可在平台中生成并交互查看第一 Brillouin Zone、高对称点和高对称路径。

仍必须注明：

* 不包含电子能带计算
* 不包含声子计算
* high-symmetry path取决于已记录provider/convention
* magnetic/surface BZ尚未支持

不得写：

* complete reciprocal-space simulation
* full electronic structure platform
* arbitrary k-space editor

---

## 41. Unit Tests

必须增加：

### 41.1 Mapper

* valid cubic
* valid BCC
* valid FCC
* valid hexagonal
* valid triclinic
* invalid hash
* convention mismatch
* units mismatch
* missing vertex
* invalid face loop
* non-finite coordinate
* over-cap
* no kpath
* multiple variants

### 41.2 Triangulation

* triangle
* square
* pentagon
* non-axis-aligned polygon
* reversed winding
* duplicate endpoint
* collinear point
* near-degenerate polygon
* non-coplanar rejection
* area consistency
* triangle count cap

### 41.3 Rendering State

* layer toggles
* opacity
* projection
* camera presets
* reset
* variant selection
* selection
* inspector
* labels
* PNG metadata
* fallback
* context loss
* lifecycle

### 41.4 Identity

* point IDs
* face IDs
* vertex IDs
* segment IDs
* artifact switching
* variant switching
* stale selection cleanup

---

## 42. Frontend Tests

至少覆盖：

* artifact detection
* loading state
* validation error
* renderer initialization
* face geometry
* edge geometry
* point markers
* axes
* labels
* kpath
* discontinuity
* point picking
* face picking，若实现
* inspector
* camera controls
* orthographic/perspective
* opacity
* toggles
* path variant
* no-kpath state
* PNG export
* WebGL fallback
* context loss
* reduced motion
* keyboard
* mobile
* no duplicate canvas
* no duplicate context
* no duplicate controls
* cleanup

不得仅测试DOM按钮存在；必须验证mapper state和scientific IDs。

---

## 43. Regression Tests

必须保持：

* Phase 10I reciprocal contract
* Phase 10I topology
* Phase 10I kpath
* Phase 10I-1 Adapter
* Tool Registry
* Planner routing
* QueueWorkerRuntime
* static structure viewer
* periodic identity
* periodic bonds
* measurement
* supercell
* clipping/camera/export
* trajectory viewer
* phonon bands
* phonon DOS
* combined band+DOS
* phonon eigenvectors
* phonon animation
* service-backed integration
* no-skipped assertion
* Phase 10 Closure Regression Pack

BZ renderer不得破坏structure viewer的Three.js lifecycle或bundle loading。

---

## 44. Bundle / Loading

Renderer必须lazy-load。

要求：

* 不访问BZ页面时，不加载BZ专用renderer代码
* 不重复打包Three.js
* 不引入第二份Three.js版本
* chunk size记录
* build输出审计
* dynamic import为应用静态代码路径
* dynamic import目标不能来自artifact
* loading fallback明确

必须检查：

```bash
npm --prefix apps/web ls three
```

确保dependency tree没有重复冲突版本。

---

## 45. Evidence Directory

建议新增：

```text
docs/phase10i/evidence/phase10i2_brillouin_renderer/
```

至少包含：

* README
* pre-implementation audit
* sanitized API captures
* plans/jobs/tool calls
* actual runtime artifacts
* fixture artifacts
* mapper validation
* triangulation validation
* browser matrix
* screenshots
* console logs
* network logs
* performance metrics
* lifecycle metrics
* context-loss evidence
* mobile audit
* accessibility audit
* PNG export samples
* artifact/screenshot hashes
* dependency audit
* security audit
* secret scan
* CI record
* replay commands

不得提交：

* secrets
* private paths
* browser profiles
* caches
* node_modules
* videos
* oversized raw structures
* external assets
* shader dumps
* renderer bundles作为artifact

---

## 46. Documentation

新增或更新：

* Phase 10I-2 implementation overview
* scene mapper
* coordinate mapping
* visual scale
* face triangulation
* transparency policy
* edge/vertex rendering
* reciprocal axes
* high-symmetry points/labels
* kpath/discontinuities
* picking identity
* inspector
* camera
* projection
* controls
* PNG export
* lifecycle
* context loss
* fallback
* accessibility
* mobile
* performance caps
* browser evidence
* security
* known limitations
* Phase 10I-3 handoff

更新：

* `docs/index.md`
* `persistent/DESIGN_PROGRESS.md`
* `persistent/TASK_BOARD.md`
* `persistent/CHANGELOG.md`
* `persistent/OPEN_QUESTIONS.md`
* `persistent/TOOL_REGISTRY_NOTES.md`
* `persistent/ARCHITECTURE_DECISIONS.md`

ADR至少记录：

1. Renderer只消费validated canonical artifacts。
2. Renderer使用reciprocal Cartesian Å⁻¹，禁止重复应用`2π`。
3. Scene只能uniform scale，禁止anisotropic normalization。
4. Artifact不控制shader/material/module。
5. K-path discontinuity不绘制跨段连接。
6. Full Band–BZ linkage留给Phase 10I-3。

---

## 47. 明确 Deferred

Phase 10I-2完成后仍然deferred：

* Band–BZ bidirectional linked view
* phonon band/BZ linked view
* electronic band Adapter
* custom k-path editor
* magnetic BZ
* surface/slab BZ
* irreducible wedge
* k-point meshes
* integration weights
* Fermi surfaces
* reciprocal volumetric data
* band unfolding
* BZ editing
* production video export
* external APIs
* notebooks/scripts
* artifact JS
* remote assets

不得将Standalone BZ Viewer READY写成完整倒空间电子结构平台READY。

---

## 48. Required Checks

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

* BZ mapper tests
* triangulation tests
* renderer state tests
* point/face picking tests
* inspector tests
* camera tests
* projection tests
* export tests
* lifecycle tests
* context-loss tests
* accessibility tests
* mobile tests
* browser evidence runners
* performance runners
* console/network audit
* API evidence
* registry/planner regression
* Phase 10I contract
* Phase 10I-1 Adapter
* Phase 10H regression
* Phase 10G regression
* structure viewer regression
* Phase 10 Closure Regression Pack
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

## 49. Commit / Push / CI

所有实现、tests、evidence、docs和persistent完成后：

```bash
git status --short
git diff --stat
git add <only Phase 10I-2 related files>
git commit -m "Add Brillouin zone renderer"
git push origin master
```

等待current-HEAD CI。

必须确认：

* backend unit success
* frontend tests success
* typecheck success
* build success
* BZ renderer tests success
* browser evidence success
* performance evidence success
* accessibility tests success
* Phase 10I contract success
* Phase 10I-1 Adapter success
* Phase 10H regression success
* Phase 10G regression success
* structure viewer regression success
* service-backed integration success
* no-skipped assertion success
* origin/master equals HEAD
* git status clean

不得伪造commit、CI run、browser version、metrics、test counts或git状态。

---

## 50. PASS 判定

PASS必须全部满足：

* 真实Three.js Renderer实现
* 使用Phase 10I validated artifacts
* 不重新计算scientific BZ geometry
* reciprocal Cartesian Å⁻¹语义正确
* `2π`不重复、不遗漏
* uniform visual scaling
* faces正确triangulate
* face面积reference通过
* translucent faces完成
* canonical edges完成
* vertices完成
* reciprocal axes完成
* high-symmetry points完成
* labels安全
* kpath完成
* discontinuities正确
* point picking完成
* inspector完成
* camera controls完成
* projection切换完成
* layer controls完成
* opacity完成
* PNG export完成
* fallback完成
* context loss完成
* lifecycle无泄漏
* no duplicate canvas/context
* performance caps完整
* Chromium通过
* Firefox通过
* WebKit通过
* mobile通过
* accessibility通过
* real runtime artifacts用于browser evidence
* console无feature错误
* no external network
* no artifact JS
* no artifact HTML/CSS/shader
* Planner可处理interactive BZ请求
* 不误导为电子能带/声子计算
* Phase 10I/10I-1不回退
* structure/trajectory/phonon viewers不回退
* tests通过
* CI通过
* origin/master等于HEAD
* git status clean

---

## 51. PARTIAL_PASS 仅允许

仅允许以下有限情况：

* face picking未正式支持，但point picking、path picking和text inspector完整
* edge picking明确deferred，因为浏览器线宽/raycast差异，但不影响科学显示
* clipping未实现，但没有无功能UI，其他renderer能力完整
* alternative path variant selector未实现，只显示canonical variant
* mobile PNG export明确禁用，但desktop export完整
* WebKit透明排序存在记录完整的非阻断视觉差异，拓扑和坐标准确
* npm audit因既有registry问题unavailable，但依赖审计完整
* magnetic/surface BZ继续DEFERRED_BY_DESIGN

以下缺失不得判定PARTIAL_PASS：

* real renderer
* face geometry
* edge geometry
* high-symmetry points/path
* point picking
* fallback
* lifecycle cleanup
* browser matrix
* performance evidence
* actual runtime artifact consumption

这些缺失必须FAIL。

---

## 52. FAIL 条件

以下任一情况必须FAIL：

* 只有docs/screenshots
* 仍然只有JSON preview
* 只有静态mock cube
* renderer不消费真实artifacts
* frontend重新计算BZ科学几何
* 重复乘或除`2π`
* anisotropic缩放扭曲BZ
* face triangulation错误
* 显示internal triangle diagonals为BZ edges
* discontinuity被画成连续path
* label通过HTML注入
* artifact控制shader/material/module
* 未实现point picking
* 无inspector
* 无WebGL fallback
* context loss后重复canvas
* artifact切换泄漏context
* idle持续无必要render loop
* 无caps
* over-cap仍初始化GPU
* 浏览器证据只来自一个browser
* fixture截图冒充runtime artifact证据
* 伪造console/network/metrics
* Planner仍声称interactive BZ不可用
* 提前声称Band–BZ联动完成
* skipped写成passed
* Phase 10I或现有viewers回退
* CI失败却声明PASS
* git不clean却声明完成

---

## 53. 最终报告格式

完成后必须输出：

# Phase 10I-2 Brillouin Renderer / Evidence Result

## 1. Conclusion

PASS / PARTIAL_PASS / FAIL

## 2. Baseline

* Phase 10I-1 commit
* initial HEAD
* branch
* origin/master
* initial status
* final HEAD
* final status

## 3. Pre-Implementation Audit

* artifact contracts
* existing renderer infrastructure
* selected mapper strategy
* dependency decision
* planned scope

## 4. Product Integration

* tool identity
* Planner routing
* artifact detection
* workbench integration
* loading/error/fallback states
* readiness metadata

## 5. Coordinate Mapping

* reciprocal convention
* units
* visual scale
* `2π`
* primitive basis
* validation

## 6. Geometry

* vertices
* edges
* faces
* triangulation
* normals
* transparency
* triangle count
* generator planes

## 7. Reciprocal-Space Features

* reciprocal axes
* high-symmetry points
* labels
* k-path
* discontinuities
* path variants

## 8. Interaction

* picking
* point inspector
* face inspector
* vertex inspector
* segment inspector
* selection identity

## 9. Camera / Controls

* rotate
* zoom
* pan
* reset
* fit
* presets
* perspective/orthographic
* toggles
* opacity
* clipping
* keyboard
* touch

## 10. Export / Fallback

* PNG export
* deterministic camera
* WebGL unavailable
* invalid artifact
* over-cap
* context loss/restore
* JSON fallback

## 11. Lifecycle

* canvas count
* context count
* render loops
* cleanup
* artifact switching
* mount/unmount
* context restore
* Blob URL cleanup

## 12. Browser Evidence

* Chromium
* Firefox
* WebKit
* mobile
* screenshots
* console
* network
* runtime artifact cases
* fallback cases

## 13. Accessibility

* keyboard
* focus
* semantic controls
* screen-reader summary
* textual tables
* reduced motion
* high contrast
* mobile

## 14. Performance

* vertices
* edges
* faces
* triangles
* points
* segments
* labels
* draw calls
* geometries
* materials
* initialization
* first render
* picking
* export
* lifecycle
* near-cap case

## 15. Security

* artifact JS
* HTML/CSS/shader
* external URLs
* network
* labels
* dynamic imports
* error disclosure
* secrets
* dependency audit

## 16. Tests

* mapper
* triangulation
* frontend
* picking
* inspector
* lifecycle
* accessibility
* browser
* performance
* Phase 10I
* Phase 10I-1
* Phase 10H
* Phase 10G
* structure viewer
* service-backed
* no-skipped

## 17. Evidence

* directory
* API captures
* runtime artifacts
* screenshots
* metrics
* logs
* hashes
* replay commands

## 18. Files

列出主要 implementation、tests、runner、evidence、docs 和 persistent 文件。

## 19. Explicitly Deferred

* Band–BZ linked view
* phonon/BZ linked view
* custom path editing
* electronic bands
* magnetic/surface BZ
* irreducible wedge
* meshes
* Fermi surfaces
* reciprocal volumetric data

## 20. Checks

* diff
* lock
* dependency tree
* frontend tests
* typecheck
* build
* backend tests
* browser runners
* performance runners
* network
* secrets

## 21. Commit / CI

* commit
* HEAD
* CI run
* unit
* frontend
* build
* browser
* performance
* accessibility
* service-backed
* no-skipped
* origin
* git status

## 22. Readiness

预期：

```text
reciprocal lattice Adapter: READY
first BZ Adapter: READY
k-path Adapter: READY
Three.js BZ Renderer: READY
point picking: READY
inspector: READY
camera and controls: READY
PNG export: READY
fallback: READY
Chromium: READY
Firefox: READY
WebKit: READY
mobile: READY
accessibility: READY
performance: READY
security: READY
standalone Brillouin Zone product: READY
Band–BZ linked view: NOT_IMPLEMENTED
full reciprocal-space electronic product: PARTIAL_READY
```

## 23. Whether Allowed to Enter Next Phase

可以 / 不可以

只有 Phase 10I-2 完成、current-HEAD CI通过、真实 Browser/API/Performance/Security Evidence 闭合且git clean后，才允许进入：

```text
Phase 10I-3：Band–BZ Linked View
```

现在开始执行。

先读取真实 Phase 10I-1 Result、canonical artifacts、现有 Three.js viewer infrastructure和Browser evidence runners，输出 Pre-Implementation Audit；然后完成正式 Brillouin Zone scene mapper、Three.js renderer、faces/edges/axes/points/path、picking/inspector、camera、controls、PNG export、fallback、lifecycle、移动端、可访问性、浏览器矩阵、性能、安全、commit和CI闭环。

不得提前进入完整 Band–BZ Linked View。

---END---


---TASK---
 状态：待处理
 # Phase 10I-3：Band–BZ Linked View

进入 Phase 10I-3：Band–BZ Linked View。

可以默认以下阶段均已严肃执行、完整验收并通过 current-HEAD CI：

* Phase 10F：Production Structure Viewer
* Phase 10G：Trajectory Contract / Adapter / Viewer / Evidence
* Phase 10H：Phonon Contract
* Phase 10H-1：Phonon Bands
* Phase 10H-2：Phonon DOS
* Phase 10H-3：Combined Band + DOS
* Phase 10H-4：Phonon Eigenvector Contract
* Phase 10H-5：Phonon Animation
* Phase 10I：Brillouin Zone Contract
* Phase 10I-1：Brillouin Zone Adapter
* Phase 10I-2：Brillouin Renderer / Evidence

必须以真实 Phase 10I-2 Result 为基线，记录实际：

* Phase 10I-2 commit
* current HEAD
* branch
* origin/master
* working-tree status
* schema versions
* browser matrix
* CI run
* backend/frontend test counts
* renderer dependency state

不得根据本 prompt 编造 commit、HEAD、测试数量、浏览器版本、性能指标或 CI 结果。

本阶段必须产生真实双向联动产品，不是 planning、contract-only、静态 handoff、单向导航或按钮占位阶段。

---

## 1. 本阶段总目标

实现正式的 Band–BZ Linked View，使同一材料计算中的 band path 与 Brillouin Zone path 共享稳定科学身份和交互状态：

```text
phonon band artifact
        +
Brillouin Zone artifact
        +
k-path artifact
        ↓
cross-artifact compatibility validation
        ↓
canonical reciprocal-path link model
        ↓
shared selection state
        ↓
band chart ↔ BZ renderer
        ↓
q-point / segment / branch inspection
        ↓
optional phonon animation handoff
```

本阶段首先完整支持：

```text
phonon band ↔ Brillouin Zone
```

必须为未来：

```text
electronic band ↔ Brillouin Zone
```

保留中性、可复用的 reciprocal-band linking interface，但不得实现或伪造电子能带数据。

---

## 2. 本阶段必须实现

必须完成：

* reciprocal band-link contract
* cross-artifact compatibility validator
* band artifact binding
* BZ artifact binding
* k-path binding
* structure identity validation
* primitive reciprocal lattice identity validation
* reciprocal convention validation
* `2π` policy validation
* provider/convention compatibility
* time-reversal compatibility
* path-variant compatibility
* point identity mapping
* segment identity mapping
* sampled q-point mapping
* discontinuity handling
* shared selection state
* band → BZ selection
* BZ → band selection
* hover preview
* pinned selection
* keyboard selection
* synchronized inspector
* chart viewport and BZ selection behavior
* mode/branch identity preservation
* phonon animation handoff
* URL/session-safe ephemeral state，若现有架构允许
* stale-selection cleanup
* artifact-switch cleanup
* mismatch/fallback UI
* accessible linked tables
* mobile linked layout
* real API/browser evidence
* Chromium / Firefox / WebKit / mobile evidence
* performance evidence
* security evidence
* docs and persistent updates
* current-HEAD CI closure

---

## 3. 本阶段明确不实现

不得实现或宣称：

* electronic band calculation
* electronic band Adapter
* electronic DOS
* projected electronic bands
* Fermi energy calculation
* band gap calculation，除非已有正式独立 artifact；默认禁止
* Fermi surface
* isoenergy surface
* Wannier interpolation
* band unfolding
* DFT
* DFPT
* phonon calculation
* force-constant calculation
* custom arbitrary k-path editor
* k-path mutation
* BZ geometry mutation
* user-authored reciprocal coordinates without validation
* Monkhorst–Pack grid
* irreducible BZ wedge
* magnetic BZ
* surface/slab BZ
* 2D/1D BZ
* arbitrary Python
* notebook execution
* script execution
* external API
* remote structure lookup
* artifact JavaScript
* artifact HTML
* artifact CSS
* artifact shader
* artifact-controlled callback
* arbitrary expression evaluation
* external URL
* CDN
* remote texture/module/worker
* renderer bundle inside artifact
* automatic nearest-frequency mode matching
* automatic nearest-coordinate linking outside contract tolerance
* silent provider-convention conversion
* silent path reordering
* silent path-segment merging
* silent interpolation across path discontinuities
* production collaborative multi-user shared cursor
* persistent scientific mutation of band/BZ artifacts

本阶段不得把“未来 electronic band interface 可兼容”写成“电子能带产品已完成”。

---

## 4. Public Tool 与产品身份

优先不新增新的公开 Tool。

继续使用已有：

```text
phonon.bands
phonon.band_dos
structure.brillouin_zone
phonon.animation
```

Linked View 应作为兼容 artifacts 的前端产品组合层，而不是创建语义模糊的新计算工具。

如现有架构确实要求显式生成链接包，可以新增内部或正式派生工具：

```text
reciprocal.band_bz_link
```

但只有满足以下条件才允许：

* 它不重新计算 band 或 BZ。
* 它只验证兼容性并生成 inert link artifact。
* 它不与 `structure.brillouin_zone` 或 `phonon.bands` 重叠。
* 它有严格资源输入。
* 它进入 Registry、PlanValidator、Runtime 和 evidence。
* Pre-Implementation Audit 明确说明必要性。

推荐策略：

```text
现有 band / BZ artifacts
        ↓
应用内置 compatibility/link builder
        ↓
linked product
```

避免为了 UI 联动增加用户可见的多余 Tool。

---

## 5. Baseline Verification

开始前执行：

```bash
cd "E:\1project\Material Data Intelligence"

git status --short
git branch --show-current
git rev-parse HEAD
git log --oneline -40
git remote -v
git rev-parse origin/master
```

必须确认：

* repository 正确
* branch 为 `master`
* working tree clean
* HEAD 包含 Phase 10I-2
* origin/master 正确
* Phonon Bands 已实现
* Combined Band + DOS 已实现
* Phonon Animation 已实现
* Brillouin Zone Adapter 已实现
* Brillouin Zone Renderer 已实现
* 相关 artifacts、validators、browser evidence 存在
* current-HEAD CI 成功

如果 working tree 不干净，停止并报告，不得覆盖未知变更。

---

## 6. 必读实现

### 6.1 Phonon Band

必须阅读：

* phonon band schema
* q-point identity
* q-point index
* branch index
* mode ID
* segment ID
* path variant ID
* path distance
* high-symmetry labels
* discontinuity representation
* frequency units
* band artifact hash
* primitive reciprocal lattice binding
* structure binding
* time-reversal metadata
* NAC direction
* point hover/click implementation
* chart zoom/pan implementation
* combined band+DOS shared axes

### 6.2 Brillouin Zone

必须阅读：

* reciprocal lattice schema
* BZ schema
* k-path schema
* point IDs
* segment IDs
* path variants
* discontinuities
* primitive lattice hash
* structure hash
* reciprocal convention
* provider metadata
* time-reversal metadata
* point/segment picking
* BZ inspector
* scene mapper
* renderer lifecycle
* browser evidence

### 6.3 Phonon Animation

必须阅读：

* canonical mode ID
* band artifact binding
* q-point binding
* branch binding
* eigenvector availability
* animation handoff
* mode selector
* current animation route/state

### 6.4 Existing Cross-Artifact Infrastructure

检查是否已有：

* artifact compatibility validators
* shared selection stores
* URL state
* panel composition
* event bus
* typed refs
* stale artifact cleanup
* cross-panel focus management

不得引入第二套全局状态系统，除非现有架构无法满足并有充分理由。

---

## 7. 修改前必须输出审计

修改代码前输出：

# Phase 10I-3 Band–BZ Linked View Pre-Implementation Audit

## 1. Baseline

* Phase 10I-2 commit
* HEAD
* branch
* origin/master
* git status
* CI
* schema versions

## 2. Band Identity

* artifact hash
* structure binding
* primitive reciprocal binding
* path variant
* segment identity
* q-point identity
* branch/mode identity
* discontinuities
* NAC semantics

## 3. BZ Identity

* BZ artifact hash
* k-path artifact hash
* primitive lattice hash
* point IDs
* segment IDs
* path variants
* provider/convention
* time reversal

## 4. Existing Compatibility Support

* current validators
* current handoff buttons
* current shared state
* missing mappings
* stale-state risks

## 5. Selected Linking Strategy

明确：

* 是否新增 link contract
* 是否新增 link artifact
* shared state位置
* point映射方法
* sampled q-point映射方法
* segment映射方法
* discontinuity处理
* hover和pinned selection区别
* animation handoff

## 6. Product Layout

* band panel
* BZ panel
* shared inspector
* mobile layout
* accessibility alternative

## 7. Planned Files

列出预计修改或新增的实现、测试、runner、evidence、docs 和 persistent 文件。

审计完成后直接实施，不等待人工确认。

---

## 8. Reciprocal Band Link Contract

必须建立正式、版本化的链接合同或等价 typed model，例如：

```text
phase10i3.reciprocal_band_bz_link.v1
```

该合同不存储新的科学 band 或 BZ 数据，只保存已验证的绑定与映射。

至少包含：

```json
{
  "schema_version": "...",
  "band_binding": {},
  "brillouin_zone_binding": {},
  "kpath_binding": {},
  "structure_binding": {},
  "reciprocal_lattice_binding": {},
  "path_variant_binding": {},
  "point_mappings": [],
  "segment_mappings": [],
  "sample_mappings": [],
  "compatibility": {},
  "warnings": [],
  "limits": {},
  "security": {},
  "provenance": {}
}
```

若不生成持久化 artifact，也必须实现同等严格的 typed internal model、validator 和测试。

---

## 9. Compatibility Validation

Linked View 初始化前必须验证：

### 9.1 Structure

* structure ID一致
* structure content hash一致
* standardized primitive structure identity一致
* source structure不同但primitive等价时，必须依赖合同允许的等价关系
* atom ordering不是band/BZ联动核心，但structure lineage必须一致

### 9.2 Reciprocal Lattice

* primitive reciprocal lattice hash一致
* matrix在合同容差内一致
* basis role一致
* units一致
* convention一致
* `physics_2pi`一致
* no hidden transpose
* no source conventional basis substitution

### 9.3 Provider / Path Convention

* k-path provider一致，或
* 明确存在经过验证的跨provider equivalence map

不得因为 labels相同就假定provider兼容。

必须验证：

* convention ID
* provider version
* standardized cell identity
* path variant ID
* time-reversal setting
* label namespace
* coordinate basis

### 9.4 Path

* point coordinates一致
* segment endpoints一致
* segment order一致
* discontinuities一致
* path direction一致或有明确反向映射
* cumulative distance语义一致
* path branch boundaries一致

### 9.5 Band-Specific

* band artifact完整
* q-point count合法
* q-point coordinates finite
* each sampled q-point belongs to declared segment
* branch count合法
* mode identity合法
* frequency values finite
* NAC direction兼容

任何核心不兼容必须阻止linked mode，不得只显示warning后继续错误联动。

---

## 10. 不得按 Label 直接链接

以下方法禁止作为canonical mapping：

```text
band label == BZ display label
```

因为：

* aliases可能不同
* provider可能不同
* duplicate coordinates可能有多个label
* display label可能为Unicode
* discontinuity两端可能共享坐标
* path variant可能不同

Canonical mapping必须使用：

```text
primitive reciprocal lattice hash
+
path convention/provider
+
path variant ID
+
point/segment ID
+
fractional reciprocal coordinate
```

Label只能用于展示和辅助诊断。

---

## 11. Point Mapping

对于band artifact中的高对称端点，必须映射到BZ k-path point。

每个mapping至少保存：

* band point reference
* BZ point ID
* k-path point ID
* reciprocal fractional coordinate
* reciprocal Cartesian coordinate
* tolerance residual
* label aliases
* path occurrence context
* mapping status

### 11.1 同一坐标多次出现

同一高对称点可能在path不同位置重复出现。

必须区分：

```text
geometric point identity
```

与：

```text
path occurrence identity
```

例如 Γ 可能在多个segment中重复出现。

Band chart选择一个具体path occurrence时：

* BZ高亮同一几何点
* shared inspector显示当前path occurrence
* chart cursor保持具体x位置
* 不将所有Γ occurrence全部视为同一个band index

---

## 12. Segment Mapping

每个band path segment必须映射到BZ k-path segment。

Mapping至少包含：

* band segment ID
* BZ segment ID
* variant ID
* start point occurrence
* end point occurrence
* direction
* Cartesian length
* band distance range
* continuity state
* residuals

如果segment方向相反：

* 必须有明确reverse flag
* normalized parameter需转换为 `1-t`
* 不得静默当同向

---

## 13. Sampled Q-Point Mapping

Band chart通常包含segment内部采样点，不仅是高对称端点。

每个sample必须能映射为：

```text
segment ID + normalized segment parameter t
```

其中：

```text
t ∈ [0,1]
```

并验证：

```text
q_sample ≈ (1-t) q_start + t q_end
```

在合同容差内。

必须保存或计算：

* band q-point index
* segment ID
* `t`
* reciprocal fractional coordinate
* reciprocal Cartesian coordinate
* band path distance
* BZ world position
* mapping residual

不得用chart x-axis全局比例直接猜BZ位置。

### 13.1 Nonlinear Band Distance

如果band distance由Cartesian reciprocal distance累计：

* `t`应根据segment内物理距离计算
* 对直线segment与坐标插值一致

若未来支持曲线路径，本合同必须显式标记；本阶段只支持合同中定义的直线高对称segment。

---

## 14. Discontinuity

对于：

```text
X | K
```

类型断点：

* band chart可以相邻绘制两个branch区域
* BZ中不得绘制X到K连接
* hover跨过断点时不得进行插值
* keyboard next-point必须跳到下一个branch起点，并显示path break
* shared inspector显示discontinuity
* chart crosshair不得显示不存在的BZ线段

不得用全局x连续性推断 reciprocal-space 连续性。

---

## 15. Shared Selection State

必须实现正式 typed selection model。

至少支持：

```text
none
high_symmetry_point
sampled_reciprocal_point
path_segment
phonon_mode
```

建议结构：

```text
ReciprocalSelection {
  sourcePanel,
  selectionKind,
  bandArtifactHash,
  bzArtifactHash,
  pathVariantId,
  segmentId,
  pointId?,
  qPointIndex?,
  branchIndex?,
  modeId?,
  t?,
  reciprocalFractional,
  reciprocalCartesian,
  pinned
}
```

### 15.1 Hover 与 Pinned

必须区分：

* transient hover
* pinned click/keyboard selection

规则：

* hover离开后恢复pinned selection
* click固定selection
* Escape清除pinned selection
* artifact切换清除
* path variant切换清除或重新映射
* incompatibility出现时清除
* panel unmount不保留stale object reference

---

## 16. Band → BZ 联动

用户在band chart中：

* hover sample
* click sample
* keyboard focus sample
* click high-symmetry tick
* select branch/mode

BZ必须：

* 高亮对应point或segment内位置
* 显示reciprocal marker
* 可选显示垂直/辅助marker，但不得扭曲科学几何
* 更新shared inspector
* 保持camera不强制跳动
* 提供可选“focus selection”
* 保持当前face/edge visibility设置

不得每次hover都重建Three.js geometry。

优先：

* 更新一个共享selection marker
* 更新现有segment highlight attribute/material
* render-on-demand

---

## 17. BZ → Band 联动

用户在BZ中：

* hover/click high-symmetry point
* click k-path segment
* click segment内部位置，若支持line picking
* keyboard选择point/segment

Band chart必须：

* 高亮对应高对称tick
* 高亮对应segment范围
* 显示sample nearest/exact mapping状态
* 更新crosshair或selection marker
* 保持当前zoom，除非用户显式选择fit
* 不自动选择某一branch/frequency，除非用户点击的是具体mode selection

### 17.1 Segment Interior Picking

如果line raycast返回segment内参数：

* 转换为canonical `t`
* 映射到band path distance
* 选择最近band sample必须显示“nearest sampled q-point”
* 不得声称raycast位置就是实际计算sample
* 误差/距离必须可检查

如跨浏览器line picking不稳定，可仅支持point和whole-segment selection，但必须明确状态，不得伪造连续picking。

---

## 18. Branch / Mode Identity

一个q-point通常有多个phonon branches。

选择band sample时必须保留：

* q-point index
* branch index
* mode ID
* frequency
* NAC direction
* eigenvector availability

BZ空间位置只能表达q-point，不能单独表达branch。

因此：

* BZ marker高亮q-point
* band panel高亮具体branch/mode
* shared inspector同时显示空间identity和mode identity
* BZ直接点选q-point时，不自动猜branch
* 用户必须在band panel或mode list中选择branch

不得根据：

* 最低频率
* 最高频率
* 当前颜色
* 最近hover branch

自动推断用户想要的mode。

---

## 19. Phonon Animation Handoff

当selection包含完整：

* band artifact hash
* q-point index
* branch index
* mode ID
* eigenvector availability

且通过Phase 10H-4/10H-5兼容验证后，显示：

```text
Open phonon animation
```

Handoff必须：

* 使用canonical mode ID
* 使用band/eigenvector/structure hashes
* 保留NAC direction
* 不按frequency重新搜索
* 不重新猜q-point
* 打开正确mode
* 返回Linked View时可恢复或明确清除selection

如果eigenvector不可用：

* 按钮disabled
* 显示原因
* 不选择最近mode
* 不生成mock animation

---

## 20. Product Layout

Desktop推荐：

```text
┌──────────────────────────────────────────────┐
│ Shared calculation / compatibility header   │
├──────────────────────┬───────────────────────┤
│ Band / Band+DOS      │ Brillouin Zone 3D     │
│ chart                │ renderer              │
├──────────────────────┴───────────────────────┤
│ Shared reciprocal selection inspector       │
└──────────────────────────────────────────────┘
```

必须允许：

* 调整左右panel宽度，若现有layout支持
* 单panel最大化
* 回到linked layout
* shared selection保持
* JSON/summary/recipe访问

### 20.1 Mobile

移动端推荐：

* tab或stacked layout
* Band
* BZ
* Inspector

要求：

* 切换tab后selection保留
* 不同时维持不必要的GPU render
* 隐藏panel时暂停BZ rendering
* 回到BZ时恢复selection marker
* no horizontal overflow
* controls不重叠

---

## 21. Compatibility Header

Linked View顶部必须显示：

* compatible / incompatible / partial
* structure identity
* primitive reciprocal lattice identity
* reciprocal convention
* path provider
* path variant
* time reversal
* band type：phonon
* selected q-point
* selected branch/mode
* warnings

不得只显示一个绿色图标而没有文字。

不兼容时必须显示具体原因，例如：

* structure hash mismatch
* primitive lattice mismatch
* provider mismatch
* path variant mismatch
* `2π` convention mismatch
* time-reversal mismatch
* point mapping incomplete

---

## 22. Partial Compatibility

必须定义严格的partial状态。

允许的partial示例：

* BZ geometry兼容，但band path provider不同，无法linked selection。
* point endpoints可映射，但sampled points无法完整映射。
* kpath artifact缺失，BZ只能standalone。
* eigenvectors缺失，因此不能打开animation。

Partial状态不得启用错误联动。

每个feature独立标记：

```text
BZ rendering: available
Band rendering: available
Point linking: unavailable
Segment linking: unavailable
Animation handoff: unavailable
```

---

## 23. Chart Interaction

必须复用现有band chart，不得为Linked View建立第二套band renderer。

至少支持：

* hover point
* click point
* keyboard focus
* selected point marker
* selected segment background/highlight
* high-symmetry tick selection
* mode/branch identity
* zoom/pan保持
* reset chart view
* reduced-motion

Chart selection不得修改canonical artifact。

---

## 24. BZ Interaction

必须复用Phase 10I-2 renderer。

增加：

* shared selection marker
* selected k-path segment highlight
* selected point highlight
* hover marker
* optional focus-to-selection
* linked status indicator

不得：

* 重建BZ mesh
* 重算kpath
* 修改artifact IDs
* 创建第二canvas
* 创建第二WebGL context

---

## 25. Shared Inspector

至少显示：

### Reciprocal Position

* point/occurrence ID
* q-point index
* fractional reciprocal coordinates
* Cartesian reciprocal coordinates
* units
* path segment
* normalized `t`
* band path distance

### Band / Mode

* band type
* branch index
* mode ID
* frequency
* unit
* imaginary status
* NAC direction
* eigenvector availability

### BZ

* BZ artifact
* path variant
* provider
* time reversal
* corresponding BZ point/segment
* mapping residual

### Compatibility

* structure hash
* primitive reciprocal hash
* convention
* mapping status
* warnings

主界面不得只展示raw JSON。

---

## 26. URL / Session State

如现有项目支持安全URL state，可持久化非敏感ephemeral selection：

* artifact IDs
* path variant
* q-point index
* branch index
* selected panel
* camera preset，若现有策略允许

不得在URL写入：

* full artifact payload
* local path
* token
* private signed URL
* raw eigenvector
* secret

URL恢复时必须重新执行兼容验证，不能盲目信任参数。

如果现有项目没有URL state，不要为本阶段引入大型新框架。

---

## 27. Lifecycle

必须保证：

* 一个BZ canvas
* 一个WebGL context
* band chart不重复mount
* shared store单实例
* hover listeners正确清理
* artifact切换清理selection
* route切换清理
* mobile tab隐藏BZ时停止无效render
* context loss清理linked marker
* context restore重新绑定selection
* no duplicate event bus listeners
* no stale closure
* no selection dispatch loop

### 27.1 防止循环同步

必须避免：

```text
Band selection
→ update BZ
→ BZ emits selection
→ update Band
→ Band emits selection
→ infinite loop
```

使用：

* source panel
* transaction ID
* revision number
* idempotent reducer

之一实现明确防环策略。

必须有测试证明无递归selection storm。

---

## 28. Performance Caps

必须限制：

* point mappings
* segment mappings
* sample mappings
* selectable band points
* linked branches
* hover events per frame
* label updates
* shared inspector rows
* selection history
* URL state length
* mapping-build time
* compatibility-validation time

不得为所有band samples创建独立Three.js sphere。

推荐：

* 一个shared selection marker
* 一个hover marker
* selected segment复用已有geometry/material
* band chart复用已有trace
* mapping使用typed arrays或bounded maps
* compatibility结果memoized by artifact hashes

---

## 29. Performance Evidence

至少测量：

* compatibility validation time
* mapping construction time
* first linked render
* band hover → BZ update latency
* BZ point click → band update latency
* segment selection latency
* branch selection latency
* animation handoff latency
* artifact switch cleanup
* mobile tab switch
* memory trend，若工具可用
* canvas count
* context count
* event listener count
* render-loop count

至少覆盖：

1. small cubic phonon band
2. hexagonal multi-segment path
3. triclinic path
4. discontinuous path
5. repeated Γ occurrences
6. multiple phonon branches
7. imaginary mode
8. NAC mode
9. near-cap q-point/branch case
10. repeated artifact switching
11. repeated linked selections
12. mobile panel switching

---

## 30. Determinism

相同 artifacts 和相同 pinned selection必须得到等价：

* compatibility result
* point mappings
* segment mappings
* sample `t`
* mapping residuals
* selected IDs
* inspector content
* fixed-camera BZ screenshot
* fixed-chart selection screenshot

Hover不是deterministic evidence的唯一来源。

正式截图应使用pinned selection。

---

## 31. Accessibility

必须支持：

* keyboard在band samples/high-symmetry ticks间导航
* keyboard在BZ points/path segments间导航
* Enter/Space pin selection
* Escape clear selection
* visible focus
* screen-reader announcement
* compatibility status文本
* selected reciprocal coordinate文本
* selected branch/mode文本
* no color-only linked state
* accessible point table
* accessible segment table
* reduced-motion
* mobile touch targets

### 31.1 Text Table Linking

必须提供不依赖canvas的可访问替代：

* high-symmetry point table
* path segment table
* selected band sample row
* branch/mode list

点击/键盘选择表格项必须同步band与BZ。

---

## 32. Browser Evidence Matrix

必须在真实：

* Chromium
* Firefox
* WebKit
* mobile viewport

验证：

* linked layout loads
* compatibility status
* band → BZ hover
* band → BZ pinned selection
* BZ point → band selection
* segment selection
* repeated high-symmetry point occurrences
* discontinuity
* branch/mode identity
* imaginary mode
* animation handoff
* standalone fallback
* mismatch fallback
* keyboard
* mobile tabs
* no duplicate canvas/context
* console
* network
* lifecycle

---

## 33. Required Screenshots

至少保存：

1. compatible linked view
2. band-selected Γ mapped to BZ
3. interior q-point mapped to BZ segment
4. BZ point mapped back to band tick
5. selected segment highlighted in both panels
6. repeated Γ occurrence inspector
7. discontinuous path state
8. imaginary mode selected
9. animation handoff available
10. eigenvector unavailable state
11. incompatible provider/path state
12. primitive lattice mismatch state
13. accessibility point table
14. keyboard selection
15. mobile band tab
16. mobile BZ tab
17. mobile inspector
18. near-cap linked case

每张截图记录：

* browser/version
* viewport
* deviceScaleFactor
* band artifact hash
* BZ artifact hash
* kpath artifact hash
* selected path variant
* selected q-point
* selected branch/mode
* selected segment/point
* screenshot hash

---

## 34. API / Runtime Evidence

必须使用真实 Runtime artifacts。

至少覆盖：

### Case A：Compatible Cubic

* structure
* phonon band
* BZ
* kpath
* link success

### Case B：Hexagonal Multi-Segment

* multiple high-symmetry points
* multiple segments
* discontinuity
* link success

### Case C：Imaginary Mode

* link success
* animation handoff

### Case D：NAC Mode

* directional mode identity
* correct handoff

### Case E：Incompatible Primitive Lattice

* typed incompatibility
* no linked interaction

### Case F：Provider/Variant Mismatch

* explicit mismatch
* no label-based fallback

记录sanitized：

* plan
* job IDs
* tool calls
* artifact IDs/hashes
* compatibility result
* link mapping summary
* browser entry state

---

## 35. Security

必须验证：

* no artifact JavaScript
* no artifact HTML
* no artifact CSS
* no artifact shader
* no external URLs
* no remote assets
* no iframe
* no eval
* no Function constructor
* no arbitrary expression
* no dynamic import from artifact
* labels使用textContent
* URL state严格白名单
* artifact IDs验证
* no local path
* no token
* no private URL
* no stack/path disclosure
* bounded mappings
* finite coordinates
* safe error messages

必须输出：

```text
NO_BAND_BZ_LINK_EXTERNAL_NETWORK_REQUESTS
```

以及：

```text
NO_SECRET_PATTERN_HITS
```

---

## 36. Planner / Product Routing

本阶段通常不需要新增计算 Tool，但Planner和UI必须能组合已有能力。

正向请求：

* 同时显示声子能带和布里渊区
* 把声子q路径映射到三维BZ
* 联动查看phonon bands与高对称路径
* Show the phonon band path in the Brillouin zone
* Link the phonon band chart to the 3D BZ
* Highlight selected q-points in reciprocal space

Planner应生成或复用：

```text
phonon.bands
structure.brillouin_zone
```

并在结果层进入Linked View。

如果已有兼容artifacts，不应重复执行计算。

### 36.1 Negative Routing

不得将以下请求误路由成Linked View已完成能力：

* 计算电子能带
* 生成电子DOS
* 计算Fermi surface
* 编辑k路径
* 运行DFT
* 运行phonopy
* 生成magnetic BZ
* 生成surface BZ

必须明确unsupported/deferred。

---

## 37. Tests

### 37.1 Compatibility Validator

* exact match
* structure mismatch
* primitive lattice mismatch
* convention mismatch
* units mismatch
* provider mismatch
* variant mismatch
* time-reversal mismatch
* discontinuity mismatch
* missing artifacts
* invalid hashes

### 37.2 Mapping

* endpoint point
* repeated point occurrence
* segment mapping
* reversed segment
* interior `t`
* near-endpoint sample
* path break
* duplicate labels
* alias labels
* triclinic coordinates
* residual over tolerance

### 37.3 Shared State

* hover
* pin
* clear
* source panel
* no feedback loop
* artifact switch
* variant switch
* mobile tab switch
* context loss/restore
* stale selection

### 37.4 Band → BZ

* sample hover
* sample click
* high-symmetry tick
* branch selection
* imaginary mode
* NAC mode

### 37.5 BZ → Band

* point pick
* segment pick
* interior nearest sample
* discontinuity
* no branch auto-guess

### 37.6 Animation Handoff

* valid mode
* missing eigenvector
* stale eigenvector hash
* wrong NAC direction
* exact mode identity

---

## 38. Regression Tests

必须保持：

* phonon bands
* phonon DOS
* combined band+DOS
* eigenvector contract
* phonon animation
* BZ contract
* BZ Adapter
* BZ Renderer
* structure viewer
* trajectory viewer
* Tool Registry
* Planner
* PlanValidator
* QueueWorkerRuntime
* service-backed integration
* Phase 10 Closure Regression Pack
* no-skipped assertion

不得为Linked View修改现有band或BZ scientific contracts的核心语义。

---

## 39. Evidence Directory

建议新增：

```text
docs/phase10i/evidence/phase10i3_band_bz_linked_view/
```

至少包含：

* README
* pre-implementation audit
* compatibility fixtures
* mapping fixtures
* actual Runtime artifacts
* sanitized API captures
* compatibility outputs
* link mapping outputs
* browser matrix
* screenshots
* console logs
* network logs
* performance metrics
* lifecycle metrics
* accessibility audit
* mobile audit
* animation handoff evidence
* negative mismatch evidence
* artifact/screenshot hashes
* security audit
* secret scan
* CI record
* replay commands

不得提交：

* secrets
* private paths
* browser profiles
* caches
* videos
* external assets
* raw large eigenvectors
* node_modules

---

## 40. Documentation

新增或更新：

* Phase 10I-3 implementation overview
* link contract/model
* compatibility policy
* point identity
* path occurrence identity
* segment mapping
* sampled q-point mapping
* discontinuity
* shared selection
* band → BZ
* BZ → band
* branch/mode semantics
* animation handoff
* layout
* mobile
* accessibility
* performance
* security
* known limitations
* future electronic-band readiness

更新：

* `docs/index.md`
* `persistent/DESIGN_PROGRESS.md`
* `persistent/TASK_BOARD.md`
* `persistent/CHANGELOG.md`
* `persistent/OPEN_QUESTIONS.md`
* `persistent/TOOL_REGISTRY_NOTES.md`
* `persistent/ARCHITECTURE_DECISIONS.md`

ADR至少记录：

1. Linking依赖stable scientific IDs，不依赖display labels。
2. BZ selection表达q-point，不自动表达phonon branch。
3. Discontinuity禁止空间插值。
4. Artifact compatibility必须在Linked View前通过。
5. 当前正式支持phonon band，电子band仅保留接口。
6. Linked selection是ephemeral viewer state，不修改canonical artifacts。

---

## 41. 明确 Deferred

Phase 10I-3完成后仍然deferred：

* electronic band Adapter
* electronic DOS
* projected electronic bands
* spin-polarized electronic bands
* orbital projections
* Fermi level
* band gap product
* Fermi surfaces
* custom k-path editor
* magnetic BZ
* surface BZ
* irreducible wedge
* k-point meshes
* band unfolding
* Wannier interpolation
* collaborative linked cursors
* scientific artifact mutation
* external APIs
* notebooks/scripts
* artifact JS
* remote assets

---

## 42. Required Checks

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

* compatibility validator tests
* point mapping tests
* segment mapping tests
* sample interpolation tests
* discontinuity tests
* shared-state tests
* feedback-loop tests
* band → BZ tests
* BZ → band tests
* animation handoff tests
* accessibility tests
* mobile tests
* lifecycle tests
* browser evidence runners
* performance runners
* console/network audit
* Planner composition tests
* Phase 10H regressions
* Phase 10I regressions
* Phase 10 Closure Regression Pack
* service-backed integration
* no-skipped assertion
* secret scan

必须如实记录：

* passed
* failed
* skipped
* unavailable

不得将skipped写成passed。

---

## 43. Commit / Push / CI

全部完成后：

```bash
git status --short
git diff --stat
git add <only Phase 10I-3 related files>
git commit -m "Link phonon bands with Brillouin zone"
git push origin master
```

等待current-HEAD CI。

必须确认：

* backend unit success
* frontend tests success
* typecheck success
* build success
* link compatibility tests success
* browser evidence success
* performance evidence success
* accessibility success
* Phase 10H regression success
* Phase 10I regression success
* service-backed integration success
* no-skipped assertion success
* origin/master equals HEAD
* git status clean

不得伪造commit、CI run、浏览器版本、metrics、test counts或git状态。

---

## 44. PASS 判定

PASS必须全部满足：

* 真实Linked View产品实现
* 使用真实phonon band与BZ Runtime artifacts
* compatibility validator完成
* structure binding严格
* primitive reciprocal lattice binding严格
* provider/convention严格
* `2π` convention严格
* path variant严格
* point mapping完成
* point occurrence identity完成
* segment mapping完成
* sampled q-point `t`映射完成
* discontinuity正确
* band → BZ完成
* BZ → band完成
* hover与pinned selection区分
* 无selection feedback loop
* q-point与branch/mode语义分离
* 不自动猜branch
* animation handoff使用canonical mode ID
* mismatch fallback完成
* mobile layout完成
* accessibility完成
* performance caps完成
* Chromium通过
* Firefox通过
* WebKit通过
* mobile通过
* no external network
* no artifact JS
* no label-based scientific mapping
* Phase 10H不回退
* Phase 10I不回退
* tests通过
* CI通过
* origin/master等于HEAD
* git status clean

---

## 45. PARTIAL_PASS 仅允许

仅允许：

* BZ segment interior连续raycast未实现，但point和whole-segment双向selection完整
* URL state未实现，但session内linked state完整
* alternative path variant linking只支持canonical variant
* electronic-band generic interface只有typed protocol，没有真实electronic artifacts
* mobile使用tab而非同时双panel
* npm audit因既有registry不可用，但依赖未变化且审计完整

以下缺失不得PARTIAL_PASS：

* compatibility validation
* point/segment identity
* bidirectional selection
* real Runtime artifacts
* discontinuity handling
* branch/mode identity
* browser matrix
* lifecycle
* accessibility基本替代视图

这些缺失必须FAIL。

---

## 46. FAIL 条件

以下任一情况必须FAIL：

* 只有“Open BZ”单向按钮
* 只有两个独立panel，没有shared selection
* 仅按label链接
* 仅按frequency链接
* 仅按chart x比例猜BZ位置
* provider mismatch仍继续联动
* primitive lattice mismatch仍继续联动
* 重复Γ occurrence处理错误
* discontinuity被插值
* BZ点选后自动猜phonon branch
* animation handoff按frequency搜索
* selection触发无限循环
* artifact切换保留stale selection
* 重新计算BZ或band科学数据
* 只有fixture，没有Runtime artifact
* 只有Chromium证据
* browser evidence伪造
* artifact包含JS/HTML/URL
* skipped写成passed
* Phase 10H或10I回退
* CI失败却声明PASS
* git不clean却声明完成

---

## 47. 最终报告格式

完成后必须输出：

# Phase 10I-3 Band–BZ Linked View Result

## 1. Conclusion

PASS / PARTIAL_PASS / FAIL

## 2. Baseline

* Phase 10I-2 commit
* initial HEAD
* branch
* origin/master
* initial status
* final HEAD
* final status

## 3. Pre-Implementation Audit

* band identity
* BZ identity
* existing compatibility
* selected linking strategy
* state architecture

## 4. Link Contract / Model

* schema/type
* band binding
* BZ binding
* kpath binding
* structure binding
* reciprocal binding
* versions

## 5. Compatibility

* structure
* primitive lattice
* convention
* units
* provider
* path variant
* time reversal
* discontinuities
* validation states

## 6. Point / Segment Mapping

* high-symmetry points
* path occurrences
* segments
* reversed segments
* sampled q-points
* normalized `t`
* residuals
* limits

## 7. Shared Selection

* hover
* pinned
* source panel
* feedback-loop prevention
* stale cleanup
* URL/session behavior

## 8. Band → BZ

* point selection
* interior sample
* segment highlight
* branch/mode identity
* chart behavior
* BZ marker

## 9. BZ → Band

* point picking
* segment picking
* nearest sampled q-point
* high-symmetry tick
* branch handling
* chart viewport

## 10. Phonon Animation Handoff

* mode ID
* eigenvector compatibility
* NAC
* imaginary mode
* unavailable state

## 11. Product UI

* linked layout
* compatibility header
* shared inspector
* desktop
* mobile
* fallback
* partial states

## 12. Accessibility

* keyboard
* focus
* screen-reader announcements
* point table
* segment table
* reduced motion
* mobile

## 13. Browser Evidence

* Chromium
* Firefox
* WebKit
* mobile
* screenshots
* console
* network
* compatible cases
* mismatch cases

## 14. Performance

* compatibility time
* mapping time
* update latency
* interaction latency
* artifact switching
* memory/lifecycle
* canvas/context/listeners
* near-cap result

## 15. Security

* artifact JS
* HTML/CSS/shader
* external URLs
* URL state
* labels
* errors
* secrets
* network

## 16. Tests

* compatibility
* mapping
* state
* bidirectional linking
* animation handoff
* accessibility
* browser
* performance
* Phase 10H
* Phase 10I
* service-backed
* no-skipped

## 17. Evidence

* directory
* Runtime artifacts
* API captures
* mappings
* screenshots
* logs
* metrics
* hashes
* replay commands

## 18. Files

列出主要 implementation、tests、runner、evidence、docs 和 persistent 文件。

## 19. Explicitly Deferred

* electronic bands
* electronic DOS
* projected bands
* Fermi surfaces
* custom path editor
* magnetic/surface BZ
* reciprocal meshes
* band unfolding

## 20. Checks

* diff
* lock
* dependency tree
* frontend tests
* typecheck
* build
* backend tests
* browser runners
* performance runners
* network
* secrets

## 21. Commit / CI

* commit
* HEAD
* CI run
* unit
* frontend
* build
* browser
* performance
* accessibility
* service-backed
* no-skipped
* origin
* git status

## 22. Readiness

预期：

```text
phonon band product: READY
Brillouin Zone product: READY
cross-artifact compatibility: READY
band → BZ selection: READY
BZ → band selection: READY
shared reciprocal inspector: READY
phonon animation handoff: READY
Chromium: READY
Firefox: READY
WebKit: READY
mobile: READY
accessibility: READY
performance: READY
security: READY
phonon reciprocal-space workflow: READY
electronic band product: NOT_IMPLEMENTED
full electronic reciprocal-space platform: NOT_READY
```

## 23. Whether Allowed to Enter Next Phase

可以 / 不可以

只有 Phase 10I-3 完成、current-HEAD CI通过、双向联动、真实Browser/API/Performance/Security Evidence闭合且git clean后，才允许进入：

```text
Phase 10J：Volumetric Data Contract
```

现在开始执行。

先读取真实 Phase 10I-2 Result、phonon band/combined/animation artifacts、BZ/kpath artifacts和当前前端状态架构，输出 Pre-Implementation Audit；然后完成兼容性验证、point/segment/sample mapping、双向selection、shared inspector、animation handoff、移动端、可访问性、浏览器矩阵、性能、安全、commit和CI闭环。

不得把本阶段扩展为电子能带实现。


---END---


---TASK---
 状态：待处理
 # Phase 10J：Volumetric Data Contract

进入 Phase 10J：Volumetric Data Contract。

可以默认以下阶段均已严肃执行、完整验收并通过 current-HEAD CI：

* Phase 10F：Production Structure Viewer
* Phase 10G：Trajectory Contract / Adapter / Viewer / Evidence
* Phase 10H：Phonon Contract / Bands / DOS / Animation
* Phase 10I：Brillouin Zone Contract
* Phase 10I-1：Brillouin Zone Adapter
* Phase 10I-2：Brillouin Renderer / Evidence
* Phase 10I-3：Band–BZ Linked View

必须以真实 Phase 10I-3 Result 为基线，记录实际：

* Phase 10I-3 commit
* current HEAD
* branch
* origin/master
* working-tree status
* CI run
* backend/frontend test counts
* current artifact schema conventions
* current binary artifact/storage capabilities

不得根据本 prompt 编造 commit、HEAD、测试数、CI run 或仓库状态。

本阶段是正式 **Contract Implementation** 阶段，不是只写 planning 文档；但本阶段仍然不是文件 Parser、Tool Adapter、等值面 Renderer 或电荷密度产品阶段。

---

## 1. 本阶段总目标

建立一个正式、版本化、数学定义完整、可确定性序列化、支持大规模数组、资源受限且安全的三维体数据 Schema Family：

```text
periodic structure / affine spatial domain
        ↓
canonical volumetric grid
        ↓
field components and quantity semantics
        ↓
bounded array payload
        ↓
statistics / integral / provenance
        ↓
dataset and manifest
        ↓
validator / canonical serializer
        ↓
future parser / adapter / isosurface renderer
```

本阶段必须固定：

* 三维网格坐标约定
* row-lattice 兼容性
* real-space 单位
* periodic / non-periodic domain
* grid origin
* grid basis和step vectors
* grid shape
* sample location
* endpoint policy
* canonical index order
* canonical flattened order
* component order
* real / complex representation
* scalar / vector field语义
* dtype
* endianness
* binary payload contract
* compression contract
* chunk contract
* payload byte-length计算
* content hashing
* field quantity identity
* physical units
* normalization/integral semantics
* spin-channel semantics
* electrostatic-potential reference语义
* statistics contract
* structure binding
* lattice/grid compatibility
* periodic translation语义
* caps
* typed errors
* security policy
* deterministic fixtures
* independent mathematical references
* future Parser handoff
* future Isosurface handoff
* documentation和persistent更新
* current-HEAD CI闭环

---

## 2. 本阶段明确不实现

不得实现或注册：

* `volumetric.parse`
* `structure.volumetric`
* `structure.charge_density`
* `structure.spin_density`
* `structure.electrostatic_potential`
* `structure.isosurface`
* CHGCAR production parser
* LOCPOT production parser
* ELFCAR production parser
* PARCHG production parser
* Gaussian CUBE production parser
* XSF production parser
* OpenDX production parser
* VTK production parser
* HDF5 production parser
* arbitrary binary file parser
* Tool Registry entry
* Planner routing
* QueueWorkerRuntime execution
* API production job
* frontend isosurface
* Three.js volume renderer
* marching cubes product
* volume ray casting
* slicing UI
* clipping-volume UI
* colormap product
* opacity transfer function
* isovalue controls
* charge-density product
* spin-density product
* electrostatic-potential product
* ELF product
* orbital/wavefunction product
* Bader analysis
* charge partitioning
* electron-count correction
* potential alignment
* vacuum-level detection
* Fermi surface
* reciprocal-space volumetric data
* electronic band calculation
* DFT
* arbitrary Python
* notebook execution
* uploaded script execution
* external API
* remote asset
* artifact JavaScript
* artifact HTML
* artifact CSS
* artifact shader
* artifact-provided GLSL
* external URL
* CDN
* iframe
* remote module
* arbitrary expression evaluation

本阶段不得因为合同支持某个 quantity enum，就声称相应科学产品已经完成。

---

## 3. Contract Scope

本阶段正式支持的合同范围：

```text
three-dimensional affine real-space volumetric data
```

包括：

* 3D periodic crystal cell中的体数据
* 3D non-periodic affine box中的体数据
* real scalar field
* real vector field
* complex scalar field
* bounded multi-channel dataset
* contiguous或bounded chunked array payload
* inline small fixture payload
* binary artifact payload

本阶段默认不支持：

* 0D/1D/2D grid
* adaptive mesh
* octree
* unstructured mesh
* tetrahedral mesh
* curvilinear grid
* cylindrical/spherical grid
* sparse voxel list
* masked/missing-value grid
* AMR
* reciprocal-space grid
* arbitrary tensor rank
* time-dependent 4D volume
* variable-grid trajectory
* distributed external storage references
* remote byte ranges
* user-defined executable decompressor

未来轨迹体数据必须另建 time-series contract，不得在本阶段把时间轴偷偷加入shape。

---

## 4. Baseline Verification

开始前执行：

```bash
cd "E:\1project\Material Data Intelligence"

git status --short
git branch --show-current
git rev-parse HEAD
git log --oneline -40
git remote -v
git rev-parse origin/master
```

必须确认：

* repository正确
* branch为`master`
* working tree clean
* HEAD包含Phase 10I-3
* origin/master正确
* current-HEAD CI成功
* artifact writer存在
* binary artifact storage能力已审计
* canonical JSON serializer存在
* content hash策略存在
* structure/lattice contract存在
* row-lattice数学存在
* caps/security conventions存在

如果working tree不干净，停止并报告，不得覆盖未知变更。

---

## 5. 必读现有实现

### 5.1 Structure / Lattice

必须阅读：

* canonical structure schema
* lattice row-vector convention
* fractional → Cartesian公式
* Cartesian → fractional公式
* determinant检查
* condition-number检查
* structure identity
* structure content hash
* periodicity metadata
* lattice units
* primitive/conventional bindings
* supercell identity
* coordinate wrapping helper

必须确认项目当前仍使用：

```text
r_cart = r_frac · A
```

其中：

```text
A =
[a
 b
 c]
```

为row lattice。

Volumetric合同不得建立相反的列向量约定。

### 5.2 Artifact Infrastructure

阅读：

* JSON artifact model
* binary artifact model，若存在
* MIME type conventions
* artifact logical names
* manifest conventions
* hash calculation
* byte caps
* upload/download behavior
* object-storage integration
* MinIO/storage abstraction
* summary/recipe conventions
* JSON-only preview
* secret scan
* error redaction

### 5.3 Existing Scientific Contracts

阅读并复用风格：

* trajectory contract
* phonon eigenvector array representation
* Brillouin Zone geometry arrays
* complex scalar/vector encoding
* normalization metadata
* tolerance-policy versioning
* manifest security metadata
* deterministic fixture replay

不得创建与现有complex-number或binary-array合同语义冲突的表示。

### 5.4 Current Dependencies

审计：

* numpy
* scipy
* pymatgen
* pymatviz
* zlib/gzip
* zstandard，若已有
* h5py，若已有
* pyarrow，若已有
* frontend TypedArray support

本阶段优先不新增依赖。

---

## 6. 修改前必须输出审计

修改代码前输出：

# Phase 10J Volumetric Data Contract Pre-Implementation Audit

## 1. Baseline

* Phase 10I-3 commit
* current HEAD
* branch
* origin/master
* git status
* current CI
* artifact schema conventions
* dependency state

## 2. Existing Spatial Convention

* row/column convention
* lattice formula
* coordinate units
* determinant policy
* condition policy
* periodic wrapping
* structure hashes

## 3. Existing Array / Binary Support

* JSON arrays
* binary artifact support
* MIME types
* hashing
* compression
* chunking
* object-storage behavior
* browser TypedArray behavior

## 4. Existing Complex / Component Models

* real/imag representation
* vector component order
* dtype handling
* finite-number policy
* canonical serializer

## 5. Selected Schema Family

列出计划实现的：

* grid schema
* field schema
* payload schema
* dataset schema
* manifest schema
* tolerance/caps schema
* validators
* fixtures
* replay

## 6. Scientific Scope

明确：

* periodic和non-periodic支持范围
* scalar/vector/complex支持范围
* endpoint policy
* grid sampling policy
* unit策略
* spin策略
* potential-reference策略
* integration策略
* unsupported范围

## 7. Planned Files

列出实现、测试、fixtures、evidence、docs和persistent文件。

审计完成后直接实施，不等待人工确认。

---

## 7. Schema Family

优先建立以下合同：

```text
volumetric_grid.v1
volumetric_payload.v1
volumetric_field.v1
volumetric_dataset.v1
volumetric_manifest.v1
```

实际完整版本名称服从项目约定，例如：

```text
phase10j.volumetric_grid.v1
phase10j.volumetric_payload.v1
phase10j.volumetric_field.v1
phase10j.volumetric_dataset.v1
phase10j.volumetric_manifest.v1
```

### 7.1 Responsibilities

`volumetric_grid.v1`：

* 空间domain
* origin
* grid basis
* shape
* sample location
* boundary/periodicity
* endpoint policy
* structure/lattice binding
* coordinate conversions
* voxel volume

`volumetric_payload.v1`：

* dtype
* endianness
* component storage
* flatten order
* encoding
* compression
* chunks
* byte counts
* content hashes

`volumetric_field.v1`：

* field identity
* quantity
* units
* scalar/vector/complex semantics
* component labels
* normalization
* payload binding
* statistics

`volumetric_dataset.v1`：

* one grid
* one or more compatible fields
* channel relationships
* source/provenance
* dataset-level validation

`volumetric_manifest.v1`：

* package artifacts
* schema versions
* logical references
* renderer absent
* executable content absent
* external resources absent
* security/provenance

不得把所有大型数组直接塞进一个JSON schema。

---

## 8. Canonical Coordinate Convention

所有空间坐标使用：

```text
length unit: angstrom
```

Canonical point公式：

```text
r(i, j, k) =
origin_cartesian
+ i * step_0
+ j * step_1
+ k * step_2
```

其中：

```text
0 <= i < nx
0 <= j < ny
0 <= k < nz
```

`step_0、step_1、step_2`以row vectors保存。

Grid step matrix：

```text
S =
[step_0
 step_1
 step_2]
```

不得把step vectors解释为columns。

### 8.1 Periodic Structure-Bound Grid

对于覆盖一个完整periodic cell且endpoint excluded的grid：

```text
nx * step_0 ≈ a
ny * step_1 ≈ b
nz * step_2 ≈ c
```

等价矩阵形式：

```text
diag(nx, ny, nz) · S ≈ A
```

其中`A`为绑定结构的row lattice。

允许fractional origin shift：

```text
origin_cartesian = origin_fractional · A
```

并要求：

```text
origin_fractional ∈ [0,1)
```

按合同容差canonical wrap。

### 8.2 Non-Periodic Affine Grid

non-periodic grid可以使用任意finite、非奇异的`S`。

必须记录：

* origin
* shape
* step vectors
* boundary conditions
* domain extent
* sample location
* endpoint policy

不得把non-periodic grid错误绑定为periodic structure field。

---

## 9. Sample Location

必须使用枚举：

```text
node
cell_center
```

### 9.1 Node Sample

```text
r(i,j,k) = origin + i*step_0 + j*step_1 + k*step_2
```

### 9.2 Cell-Center Sample

```text
r(i,j,k) =
origin
+ (i + 0.5)*step_0
+ (j + 0.5)*step_1
+ (k + 0.5)*step_2
```

合同必须明确`origin`在cell-center模式下表示grid-domain corner，而不是第一个sample本身。

不得让consumer猜测origin语义。

---

## 10. Endpoint Policy

必须使用明确枚举：

```text
excluded
included
not_applicable
```

### 10.1 Periodic Canonical Policy

Phase 10J的canonical periodic grid必须使用：

```text
endpoint_policy = excluded
```

即：

* `(0,0,0)`存在
* `(1,0,0)`的周期等价endpoint不重复存储
* 每个方向恰有`n`个独立samples

未来Parser若遇到重复endpoint：

* 必须检测
* 必须验证重复面
* 必须移除重复endpoint
* 必须记录source transform

但本阶段不得实现这些文件Parser。

### 10.2 Non-Periodic

non-periodic grid可声明`included`或`excluded`，但必须结合：

* sample location
* shape
* step vectors
* domain extent

完整定义。

---

## 11. Boundary Conditions

每个axis必须明确：

```text
periodic
non_periodic
```

本阶段只允许：

* 三轴全部periodic
* 三轴全部non-periodic

默认拒绝混合周期：

```text
periodic, periodic, non_periodic
```

因为它会涉及surface/slab volumetric产品、vacuum方向和2D边界语义，留给后续独立扩展。

不得将slab grid伪装成普通3D periodic volume。

---

## 12. Grid Identity

Grid identity必须绑定：

* schema version
* coordinate space
* units
* shape
* origin
* step matrix
* sample location
* boundary conditions
* endpoint policy
* structure hash，若绑定
* lattice hash，若绑定
* tolerance-policy version

不得包含：

* payload values
* runtime job ID
* filename
* local path
* timestamp
* camera/renderer state

Grid hash与Field hash必须分离。

同一grid可承载多个fields。

---

## 13. Canonical Index Order

逻辑索引固定为：

```text
(i, j, k, component)
```

其中：

* `i`沿`step_0`
* `j`沿`step_1`
* `k`沿`step_2`
* `component`为field component

Canonical flattened order固定为：

```text
component-fastest
k-fastest
j-middle
i-slowest
```

公式：

```text
offset(i,j,k,c)
=
((((i * ny) + j) * nz + k) * component_count) + c
```

必须在schema中明确记录：

```text
flatten_order = ijkc_component_fastest
```

不得依赖：

* NumPy默认order
* Fortran order
* source file order
* language内存布局
* consumer猜测

### 13.1 Shape

Payload logical shape：

```text
[nx, ny, nz, component_count]
```

但field metadata中必须分别存：

* grid shape
* component count

防止将component误认为第四空间轴。

---

## 14. Field Rank 与 Components

本阶段合同支持：

### 14.1 Real Scalar

```text
value_kind = real
field_rank = scalar
component_count = 1
```

### 14.2 Real Vector

```text
value_kind = real
field_rank = vector
component_count = 3
```

Canonical component labels：

```text
x
y
z
```

向量分量默认是Cartesian components。

必须明确：

```text
component_basis = cartesian
```

未来若支持fractional/lattice-basis vector，必须作为单独枚举。

### 14.3 Complex Scalar

```text
value_kind = complex
field_rank = scalar
logical_component_count = 1
stored_component_count = 2
```

Canonical stored component order：

```text
real
imag
```

不得使用Python complex字符串或不透明对象。

### 14.4 Deferred

本阶段不支持：

* complex vector
* tensor
* matrix
* quaternion
* arbitrary component count
* spherical harmonics payload

Schema必须拒绝，而不是接受任意`component_count`。

---

## 15. Quantity Identity

必须使用结构化quantity identity，不得只用自由字符串。

建议枚举至少包括：

```text
generic_scalar
charge_density
electron_density
spin_density
magnetization_density
electrostatic_potential
local_potential
electron_localization_function
orbital_density
wavefunction
custom_declared
```

但readiness必须区分：

* 合同能够表达
* 生产Parser是否实现
* 科学产品是否实现

本阶段所有quantity均仅为：

```text
CONTRACT_DEFINED
PARSER_NOT_IMPLEMENTED
RENDERER_NOT_IMPLEMENTED
```

### 15.1 Custom Declared

如允许`custom_declared`，必须要求：

* bounded ASCII identity
* display name
* exact unit
* value semantics
* source provenance
* no HTML
* no arbitrary expression

不得允许quantity name控制renderer行为。

---

## 16. Units

使用严格枚举或验证后的结构化单位。

至少预定义：

```text
dimensionless
electron / angstrom^3
elementary_charge / angstrom^3
electron / bohr^3
volt
electronvolt
hartree
hartree / elementary_charge
angstrom^-3
custom_declared
```

Canonical contract不应无条件把所有source values转换为一个单位，除非转换精确且记录完整。

必须保存：

* source unit
* canonical unit
* conversion factor
* conversion provenance
* conversion applied: true/false

### 16.1 Density Distinction

必须区分：

```text
electron_density
```

与：

```text
charge_density
```

符号语义可能不同。

不得默认：

```text
charge_density = -electron_density
```

除非source contract明确说明并记录转换。

### 16.2 Unknown Unit

不得把unknown unit写成dimensionless。

必须：

* typed reject，或
* 使用明确`unknown`状态且限制scientific claims

优先reject正式scientific quantities中的unknown unit。

---

## 17. Normalization 与 Integral Semantics

每个field必须声明：

```text
normalization_semantics
integral_semantics
```

可能值包括：

```text
source_native
normalized_to_unit_integral
normalized_to_electron_count
normalized_to_charge
not_normalized
unknown
```

Integral semantics包括：

```text
electron_count
elementary_charge
magnetic_moment
cell_average
zero_by_definition
not_physically_interpreted
unknown
```

不得根据quantity name自动猜normalization。

### 17.1 Voxel Volume

Periodic full-cell grid：

```text
voxel_volume =
|det(A)| / (nx * ny * nz)
```

Affine grid：

```text
voxel_volume = |det(S)|
```

对于cell-center或node/excluded policy，上述每sample积分权重相同。

### 17.2 Discrete Integral

Real scalar field：

```text
integral = Σ values[i,j,k] * voxel_volume
```

Complex scalar field不得直接使用complex sum作为物理integral。

可记录：

* real integral
* imaginary integral
* norm integral

但必须明确语义。

### 17.3 No Silent Renormalization

Validator不得为了匹配预期电子数而修改field values。

不匹配时：

* warning
* typed validation failure，取决于quantity policy
* 记录residual

不得静默缩放。

---

## 18. Spin Semantics

必须为未来自旋密度固定结构化语义。

允许channel identity：

```text
total
spin_up
spin_down
magnetization_x
magnetization_y
magnetization_z
magnetization_vector
spin_difference
```

必须记录：

* collinear / non_collinear
* component basis
* sign convention
* source convention
* unit
* relationships between channels

### 18.1 Collinear

常见表示可能是：

```text
rho_total
rho_spin = rho_up - rho_down
```

或：

```text
rho_up
rho_down
```

合同必须明确实际表示，不得自动等价。

### 18.2 Non-Collinear

可由real vector field表示magnetization density：

```text
Mx, My, Mz
```

但本阶段只固定合同，不实现解析或渲染。

### 18.3 Forbidden Assumptions

不得默认：

* spin density单位与electron density完全相同
* spin channel顺序固定来自source
* `up/down`适用于non-collinear
* magnetization vector等于三个独立电荷密度

---

## 19. Electrostatic Potential Reference

Potential field必须声明reference/gauge：

```text
absolute_declared
cell_average_zero
vacuum_reference
fermi_reference
source_defined
unknown
```

并可记录：

* reference value
* reference unit
* source metadata
* shift applied
* shift amount

不得将任意potential field自动设为：

```text
vacuum_zero
```

不得根据grid平均值为零就推断source使用了cell-average-zero。

本阶段不执行potential alignment。

---

## 20. Complex Field Semantics

Complex scalar field必须声明：

* real/imag representation
* phase/gauge semantics
* normalization
* quantity
* source convention

可能用途：

* wavefunction
* complex orbital
* complex response field

不得默认：

* global phase具有物理可观测意义
* `real part`等于完整field
* `|ψ|²`已经包含在payload
* wavefunction归一化为1

若consumer未来生成density：

```text
|ψ|²
```

必须作为独立derived field artifact，不能修改原complex field。

---

## 21. Payload Dtype

允许的初始dtype：

```text
float32
float64
```

本阶段默认拒绝：

* float16
* bfloat16
* int
* uint
* decimal string
* arbitrary precision
* native-endian
* platform-dependent long double

Canonical binary endianness：

```text
little
```

如果source是big-endian，未来Parser必须转换或明确生成big-endian artifact；推荐统一转换为little-endian并记录。

### 21.1 Precision

Field必须记录：

* source dtype
* stored dtype
* conversion applied
* maximum conversion error estimate，若转换
* lossless/lossy

不得将float64静默降为float32。

---

## 22. Payload Encodings

允许：

### 22.1 Inline JSON

仅用于小型fixtures：

```text
encoding = inline_json
```

必须有严格value-count和byte caps。

### 22.2 Raw Binary

```text
encoding = raw_binary
```

要求：

* logical artifact reference
* MIME type
* byte length
* dtype
* endianness
* shape
* flatten order
* SHA-256或项目canonical hash
* no local path
* no URL

### 22.3 Compressed Binary

允许：

```text
encoding = gzip_binary
```

前提：

* decompressed byte length明确
* compressed byte length明确
* compressed hash
* decompressed hash
* deterministic gzip metadata
* decompression cap
* compression-ratio cap
* stream validation
* no nested archive
* no filename inside archive
* no multi-member ambiguity，除非明确禁止/验证

如仓库已有稳定zstd依赖，可增加：

```text
zstd_binary
```

否则不得为了合同新增依赖。

### 22.4 Forbidden Encodings

禁止：

* pickle
* npy object arrays
* npz with arbitrary filenames
* HDF5作为canonical payload
* Java serialization
* Python marshal
* MessagePack extension objects
* base64 for large production payload
* ZIP archive with paths
* TAR
* arbitrary codec name
* executable decompressor

Source formats可以未来解析，但canonical artifact不得直接继承不安全容器。

---

## 23. Payload Byte-Length Validation

必须精确计算：

```text
expected_value_count =
nx * ny * nz * stored_component_count
```

```text
expected_byte_length =
expected_value_count * bytes_per_value
```

必须检查：

* integer overflow
* multiplication overflow
* zero dimensions
* negative dimensions
* payload length mismatch
* decompressed length mismatch
* extra trailing bytes
* truncated bytes

不得容忍“接近正确”的payload长度。

---

## 24. Chunking

为支持大grid，合同可支持bounded chunking。

每个chunk至少包含：

* chunk ID
* logical start index
* logical shape
* byte offset或独立artifact reference
* compressed length
* decompressed length
* hash
* encoding
* dtype
* endianness

### 24.1 Canonical Chunk Policy

优先沿`i`轴切分完整`j×k×components` slabs。

每个chunk必须覆盖连续范围：

```text
i_start <= i < i_end
```

要求：

* 无重叠
* 无空洞
* 完整覆盖
* 顺序确定
* chunk count bounded
* chunk shape与grid一致
* 单chunk和总bytes受限

不得支持任意三维碎片化直到有真实需求。

### 24.2 Hashing

Dataset/field content hash必须与chunk边界无关，或明确区分：

* logical field content hash
* storage-layout hash

相同values仅因chunk大小不同，不应被误认为科学内容不同。

---

## 25. Statistics Contract

每个real field可保存derived statistics：

* count
* minimum
* maximum
* mean
* variance
* standard deviation
* RMS
* integral
* absolute integral
* finite count
* optional bounded histogram

Complex field可保存：

* real min/max
* imag min/max
* magnitude min/max
* norm integral
* real/imag means

### 25.1 Authority

Statistics必须标记：

```text
computed_from_payload
source_reported
unverified
```

正式Adapter生成时应由payload重新计算。

### 25.2 Numeric Algorithm

必须固定：

* streaming algorithm
* accumulation precision
* overflow handling
* deterministic reduction order，或容差策略
* NaN/Infinity拒绝
* negative zero normalization

### 25.3 Histogram

如果合同包含histogram：

* bounded bin count
* deterministic bin edges
* min/max policy
* no auto-unbounded bins
* no scientific identity dependence

Histogram是derived preview metadata，不是原field替代品。

---

## 26. Finite Values 与 Missing Data

本阶段canonical payload要求：

```text
all values finite
```

禁止：

* NaN
* +Infinity
* -Infinity
* null
* missing voxel
* sparse holes
* implicit fill values

如果未来需要masked data，必须建立独立mask contract。

不得把NaN当透明区域交给renderer。

---

## 27. Grid / Structure Compatibility

Periodic structure-bound grid必须验证：

* structure hash存在
* lattice hash存在
* lattice units为Å
* grid三轴均periodic
* endpoint excluded
* grid step vectors span one lattice cell
* determinant finite
* grid/lattice orientation一致
* origin fractional有限
* origin wrapping正确
* voxel volume一致
* no hidden transpose
* no `2π`
* no reciprocal-space coordinates

### 27.1 Origin Shift

Periodic field允许非零fractional origin。

Structure atom positions不需要与grid node重合。

不得强制：

```text
origin_fractional = [0,0,0]
```

但必须记录并正确转换。

### 27.2 Supercell

若field覆盖supercell：

* 必须绑定该supercell的canonical structure/lattice
* 不得只用primitive structure hash加隐式repeat
* 不得让consumer猜supercell矩阵

---

## 28. Periodic Coordinate Wrapping

对于periodic grid，fractional position映射到grid coordinate：

```text
u = wrap(frac - origin_fractional)
```

Sample index的连续坐标：

```text
g = [u_x * nx, u_y * ny, u_z * nz]
```

具体插值策略留给未来Renderer/analysis阶段。

本阶段必须固定：

* wrap区间
* endpoint tolerance
* `-0.0`处理
* `1.0`映射回`0.0`
* triclinic lattice不影响fractional wrapping

不得在Cartesian坐标中按axis-aligned bounding box做periodic wrap。

---

## 29. Dataset Contract

一个dataset必须包含：

* dataset ID
* one canonical grid
* one or more fields
* source identity
* structure binding，optional
* field relationships
* provenance
* caps
* security
* hashes

所有fields必须：

* 使用同一grid，或
* 明确引用其他grid

本阶段建议一个dataset只允许一个grid，以降低复杂度。

不同grid必须生成不同dataset。

### 29.1 Field Relationships

可结构化记录：

* total = up + down
* spin_difference = up - down
* derived magnitude from vector
* derived density from complex wavefunction

但必须标记：

```text
declared
validated
unverified
```

Validator不得盲目信任source relationship。

---

## 30. Provenance

必须记录：

* source kind
* source format identity，若已知
* source file hash，fixture可用
* parser identity，未来
* parser version，未来
* conversion steps
* unit conversion
* dtype conversion
* endpoint removal
* axis permutation
* origin transformation
* structure binding
* generated timestamp，若项目需要，但不得进入科学content hash
* software versions

本阶段fixtures可使用：

```text
source_kind = synthetic_fixture
```

不得伪装成VASP或Gaussian真实输出。

---

## 31. Canonicalization

必须固定：

* field ID排序
* component label排序
* channel排序
* chunk排序
* statistics字段顺序
* warning顺序
* numeric canonicalization
* negative zero normalization
* metadata key ordering
* Unicode normalization
* hash inputs

Payload数值顺序由canonical flatten order固定。

### 31.1 Content Hash Layers

建议区分：

```text
grid_content_hash
payload_content_hash
field_content_hash
dataset_content_hash
manifest_content_hash
```

`field_content_hash`应绑定：

* grid hash
* quantity semantics
* units
* components
* payload logical hash
* normalization
* source transformations

不得只hash binary bytes而忽略单位和grid。

---

## 32. Manifest Contract

`volumetric_manifest.v1`至少包含：

* schema versions
* dataset artifact
* grid artifact
* field artifacts
* payload artifacts
* logical references
* content hashes
* media types
* byte lengths
* compression
* renderer included: false
* executable assets: none
* external resources: none
* remote URLs: none
* preview mode: metadata/JSON only
* provenance
* security
* caps

Manifest不得包含：

* local absolute path
* signed URL
* external URL
* script
* shader
* HTML
* renderer bundle
* arbitrary codec module

---

## 33. Security Contract

所有metadata均为inert JSON，payload仅为numeric bytes。

必须声明并验证：

```text
contains_javascript = false
contains_html = false
contains_css = false
contains_shader = false
contains_executable = false
external_urls_allowed = false
renderer_included = false
```

必须防止：

* decompression bomb
* integer overflow
* oversized allocation
* path traversal
* archive filename injection
* nested archive
* arbitrary MIME type
* arbitrary codec
* executable payload
* object deserialization
* symlink reference
* remote reference
* hash bypass
* chunk overlap
* chunk gap
* metadata explosion
* label injection
* stack/path disclosure

---

## 34. Caps

必须定义versioned hard caps，至少包括：

* max grid dimension per axis
* max total voxels
* max stored values
* max component count
* max fields per dataset
* max chunks per field
* max uncompressed bytes per field
* max compressed bytes per field
* max dataset bytes
* max compression ratio
* max inline JSON values
* max inline JSON bytes
* max metadata bytes
* max field-name length
* max unit-string length
* max warnings
* max histogram bins
* max provenance entries

初始值必须结合现有storage、CI和未来浏览器能力保守制定。

不得仅使用Python整数无限计算后再分配内存。

### 34.1 Allocation Safety

Validator必须在：

* 读取payload
* 解压
* 分配NumPy array
* 计算statistics

之前完成shape和byte cap检查。

---

## 35. Typed Errors

至少定义或复用：

* unsupported dimensionality
* unsupported mixed periodicity
* invalid grid shape
* zero grid dimension
* grid dimension cap exceeded
* voxel cap exceeded
* invalid origin
* invalid step matrix
* singular grid basis
* ill-conditioned grid basis
* structure binding missing
* structure hash mismatch
* lattice hash mismatch
* grid/lattice mismatch
* endpoint policy invalid
* sample-location invalid
* flatten-order invalid
* unsupported field rank
* unsupported value kind
* invalid component count
* invalid component labels
* unsupported dtype
* unsupported endianness
* unsupported encoding
* payload missing
* payload byte mismatch
* payload truncated
* payload has trailing bytes
* payload hash mismatch
* decompression failed
* decompression cap exceeded
* compression ratio exceeded
* chunk overlap
* chunk gap
* chunk order invalid
* non-finite field value
* invalid unit
* quantity/unit mismatch
* normalization missing
* integral semantics missing
* statistics mismatch
* potential reference missing
* spin semantics invalid
* complex representation invalid
* metadata cap exceeded
* manifest validation failed
* content hash mismatch
* fixture replay failed

错误不得泄漏：

* local path
* private URL
* token
* secret
* stack trace
* environment variable
* object-storage credentials

---

## 36. Independent Mathematical References

不得仅用production validator验证production serializer。

必须建立独立reference calculations。

### 36.1 Coordinate Mapping

验证：

```text
r(i,j,k) = origin + i*s0 + j*s1 + k*s2
```

包括：

* orthogonal
* triclinic
* shifted origin
* cell-center

### 36.2 Periodic Lattice Match

验证：

```text
diag(nx,ny,nz) · S = A
```

在合同容差内。

### 36.3 Flatten Order

用小型：

```text
shape = [2,3,4]
```

和已知pattern验证每个offset。

不得使用NumPy reshape默认行为作为唯一reference。

### 36.4 Voxel Volume

验证：

```text
voxel_volume = |det(S)|
```

和periodic：

```text
|det(A)| / (nx*ny*nz)
```

一致。

### 36.5 Integral

对constant field：

```text
f = c
```

验证：

```text
integral = c * domain_volume
```

### 36.6 Complex Encoding

验证real/imag interleaving和magnitude/norm。

### 36.7 Binary Bytes

用`struct`或独立小型decoder验证：

* little-endian float32
* little-endian float64
* exact byte length
* flatten order

Reference测试不得调用production payload decoder完成相同验证。

---

## 37. Required Fixtures

### Fixture A：Cubic Constant Scalar

* periodic cubic cell
* grid `4×4×4`
* node/excluded
* constant value
* knownvoxel volume
* known min/max/mean/integral
* inline JSON和raw binary两个等价版本

### Fixture B：Periodic Trigonometric Scalar

例如：

```text
f(x,y,z) =
cos(2πx) + 0.5 sin(2πy) - 0.25 cos(4πz)
```

其中`x,y,z`为fractional coordinates。

验证：

* periodicity
* flatten order
* statistics
* approximate zero cell integral
* shifted-origin behavior

### Fixture C：Triclinic Periodic Grid

* general row lattice
* non-orthogonal step vectors
* shifted fractional origin
* known coordinate samples
* knownvoxel volume
* structure binding

### Fixture D：Non-Periodic Affine Box

* all axes non-periodic
* cell-center sampling
* nonzero origin
* anisotropic step lengths
* knowndomain volume
* no structure binding

### Fixture E：Collinear Spin Dataset

包含：

* total field
* spin-difference field
* declared relationship
* units
* channel semantics
* validation residual

必须明确这是synthetic fixture，不是生产CHGCAR解析结果。

### Fixture F：Non-Collinear Magnetization

* real vector field
* Cartesian components
* `Mx、My、Mz`
* knownmagnitude statistics
* no renderer claim

### Fixture G：Complex Scalar

* real/imag interleaved
* knownphase pattern
* knownnorm integral
* explicit normalization semantics

### Fixture H：Potential Gauge

* real scalar potential
* source-defined或cell-average-zero reference
* knownmean
* no automatic vacuum alignment

### Fixture I：Chunked Payload

* multipleordered i-slabs
* completecoverage
* chunk hashes
* logical content hash等于unchunked版本

### Fixture J：Negative Cases

至少包括：

* zero dimension
* dimension over cap
* integer overflow
* singular step matrix
* endpoint included onperiodic canonical grid
* lattice mismatch
* wrong flatten order
* wrong byte length
* trailing bytes
* truncated bytes
* hash mismatch
* NaN
* Infinity
* invalid unit
* invalid spin channels
* missing potential reference
* chunk overlap
* chunk gap
* gzip bomb ratio
* archive filename/path
* executable MIME type
* metadata over cap

---

## 38. Deterministic Compression

如果实现gzip fixture：

* 使用固定compression level
* `mtime=0`
* 不包含source filename
* deterministic header
* deterministic bytes
* compressed hash固定
* decompressed hash固定

相同logical payload必须得到相同canonical gzip bytes。

如果当前语言/runtime无法保证完全稳定，content identity必须以decompressed logical bytes为主，storage hash单独记录。

---

## 39. Statistics Validation

Validator应支持streaming读取，避免对最大payload复制多份内存。

必须验证：

* count
* min/max
* mean
* RMS
* integral
* finite values

对于float32输入，accumulation优先使用float64。

统计容差必须基于：

* dtype
* value magnitude
* count
* deterministic policy

不得使用一个固定绝对`1e-6`覆盖所有cases。

---

## 40. Quantity / Unit Validation Matrix

必须建立明确matrix，例如：

| Quantity                | Allowed field      | Expected units                 |
| ----------------------- | ------------------ | ------------------------------ |
| electron_density        | real scalar        | electron/Å³等明确单位               |
| charge_density          | real scalar        | e/Å³等明确单位                      |
| spin_density            | real scalar        | 声明的spin-density单位              |
| magnetization_density   | real scalar/vector | 明确磁矩/体积单位                      |
| electrostatic_potential | real scalar        | eV、V、Ha/e等                     |
| ELF                     | real scalar        | dimensionless                  |
| wavefunction            | complex scalar     | source-defined、明确normalization |

实际文档可使用表格，但schema必须用allowlist实现，不得只靠文档。

不兼容quantity/unit必须typed error或明确custom quantity。

---

## 41. Future Isosurface Handoff

本阶段必须为Phase 10J-2预留稳定接口。

Isosurface-compatible field至少要求：

* real scalar
* finite
* validated grid
* validated payload
* min/max
* value unit
* structure binding，若周期
* no missing values
* size within renderer cap

必须提供pure helper：

```text
is_isosurface_compatible(field)
```

或等价validator。

不得实现：

* marching cubes
* triangle mesh
* normals
* WebGL
* isovalue UI

### 41.1 Periodic Seam Handoff

未来等值面需要处理跨cell边界。

合同必须明确：

* endpoint excluded
* periodic axes
* grid origin
* wrap semantics
* consumer可按周期halo处理

不得提前持久化重复halo planes作为canonical data。

---

## 42. Future Slice Handoff

为未来切片产品记录：

* Cartesian ↔ grid coordinate conversion
* fractional ↔ grid coordinate conversion
* boundary/wrap semantics
* interpolation-readiness metadata

但本阶段不实现：

* interpolation
* slicing
* plane sampling
* texture generation

---

## 43. Parser Handoff

Phase 10J-1未来Parser必须完成：

```text
source format
→ parse
→ identify axes/order
→ identify units
→ identify endpoint policy
→ identify quantity semantics
→ convert into canonical grid/payload
→ validate
→ write artifacts
```

本阶段必须提供清晰的Source Transformation记录字段：

* axis permutation
* axis reversal
* origin shift
* endpoint removal
* unit conversion
* dtype conversion
* endian conversion
* component remapping
* source flatten order
* source shape
* canonical shape

不得在Phase 10J直接实现这些生产Parser。

---

## 44. JSON-Only Preview

本阶段可以为合同fixtures增加安全metadata preview。

允许显示：

* schema version
* grid shape
* total voxels
* origin
* step vectors
* boundary conditions
* sample location
* endpoint policy
* quantity
* units
* components
* dtype
* encoding
* compressed/uncompressed bytes
* min/max/mean/integral
* structure binding
* validation state
* renderer not included

不得：

* 加载完整大型payload到DOM
* 显示数百万values
* 初始化Three.js
* 生成isosurface
* 生成slice
* 创建WebGL context
* 声称volume viewer ready

如果现有通用JSON preview已足够，不要修改frontend。

---

## 45. 本阶段不注册 Tool

Phase 10J是Contract阶段。

不得注册：

```text
structure.volumetric
structure.charge_density
structure.isosurface
```

可以在Tool Registry notes规划Phase 10J-1 candidate，例如：

```text
tool_id: structure.volumetric_data
status: PLANNED
```

但必须是：

```text
NOT_REGISTERED
NOT_EXECUTABLE
PARSER_NOT_IMPLEMENTED
```

不得显示READY。

---

## 46. Evidence Directory

建议新增：

```text
docs/phase10j/evidence/phase10j_volumetric_data_contract/
```

至少包含：

* README
* pre-implementation audit
* schema snapshots
* grid fixtures
* field fixtures
* payload fixtures
* dataset fixtures
* manifest fixtures
* raw binary samples
* deterministic gzip sample，若支持
* validation outputs
* independent reference outputs
* flatten-order evidence
* coordinate evidence
* integral evidence
* chunk replay
* hash records
* negative cases
* cap tests
* decompression-security tests
* dependency audit
* secret scan
* CI record
* replay commands

不得提交：

* secrets
* private paths
* large production CHGCAR
* large CUBE files
* browser cache
* node_modules
* arbitrary archives
* executable payload
* external URLs

---

## 47. Documentation

至少新增或更新：

* Phase 10J overview
* schema family
* coordinate convention
* row-vector mathematics
* periodic grid semantics
* origin
* sample location
* endpoint policy
* boundary conditions
* index/flatten order
* scalar/vector/complex field
* quantity identity
* units
* normalization
* integral
* spin semantics
* potential reference
* dtype/endianness
* payload encodings
* compression
* chunking
* statistics
* structure binding
* caps
* security
* fixtures
* replay
* future Parser handoff
* future Isosurface handoff
* known limitations

更新：

* `docs/index.md`
* `persistent/DESIGN_PROGRESS.md`
* `persistent/TASK_BOARD.md`
* `persistent/CHANGELOG.md`
* `persistent/OPEN_QUESTIONS.md`
* `persistent/TOOL_REGISTRY_NOTES.md`
* `persistent/ARCHITECTURE_DECISIONS.md`

ADR至少记录：

1. Volumetric grid使用row step vectors。
2. Canonical periodic grid排除重复endpoint。
3. Canonical flatten order固定为`ijkc`且component fastest。
4. Canonical binary使用little-endian float32/float64。
5. Grid、payload、field和dataset hash分层。
6. Quantity、unit和normalization必须显式。
7. Canonical artifact禁止pickle、object arrays和可执行容器。
8. Parser留给Phase 10J-1。
9. Isosurface Renderer留给后续阶段。

---

## 48. 明确 Deferred

Phase 10J完成后仍然deferred：

* CHGCAR/LOCPOT/ELFCAR/PARCHG Parser
* CUBE Parser
* XSF Parser
* HDF5/VTK Parser
* production Tool Registry
* Planner
* Runtime execution
* Three.js volume renderer
* marching cubes
* isosurface
* slices
* transfer functions
* charge-density product
* spin-density product
* electrostatic-potential product
* ELF product
* orbital product
* wavefunction product
* Bader analysis
* potential alignment
* vacuum detection
* 2D/slab mixed periodicity
* reciprocal-space volume
* time-dependent volume
* adaptive/unstructured meshes
* external APIs
* notebooks/scripts
* artifact JS
* remote assets

---

## 49. Tests

### 49.1 Grid

* periodic cubic
* periodic triclinic
* shifted origin
* non-periodic affine
* node sampling
* cell-center sampling
* endpoint policy
* mixed-periodicity rejection
* singular step matrix
* grid/lattice mismatch
* coordinate round-trip

### 49.2 Flattening

* known `2×3×4`
* scalar
* vector
* complex scalar
* offset boundaries
* first/last element
* wrong order rejection

### 49.3 Payload

* inline JSON
* raw float32
* raw float64
* little endian
* wrong endian metadata
* gzip，若支持
* byte mismatch
* hash mismatch
* truncated
* trailing bytes
* decompression cap
* compression ratio
* chunks
* chunk gaps/overlaps

### 49.4 Field

* scalar
* vector
* complex
* quantity/unit matrix
* normalization
* integral semantics
* spin
* potential reference
* statistics
* non-finite rejection

### 49.5 Dataset / Manifest

* one grid/multiple fields
* incompatiblefield grid
* field ordering
* logical references
* hashes
* media types
* security flags
* no external URLs
* no executable assets

### 49.6 Scientific References

* voxel volume
* constant integral
* periodic trigonometric field
* triclinic coordinates
* complex norm
* spin relationship
* potential mean/reference

### 49.7 Security

* path traversal
* archive filename
* nested archive
* executable MIME
* object payload
* metadata overflow
* integer overflow
* allocation cap
* label injection
* secret/path redaction

### 49.8 Regression

* structure/lattice contracts
* trajectory arrays
* phonon complex vectors
* Brillouin Zone contracts
* artifact storage
* manifest validation
* JSON preview
* Phase 10 Closure Regression Pack
* service-backed integration
* no-skipped assertion

---

## 50. Required Checks

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

* volumetric grid schema tests
* payload schema tests
* field schema tests
* dataset schema tests
* manifest schema tests
* coordinate tests
* flatten-order tests
* binary decoder reference tests
* compression tests
* chunk tests
* quantity/unit tests
* normalization/integral tests
* spin tests
* potential-reference tests
* complex-field tests
* fixture replay
* deterministic serialization
* content-hash tests
* cap tests
* decompression-security tests
* Phase 10 regressions
* service-backed integration
* no-skipped assertion
* secret scan

必须如实记录：

* passed
* failed
* skipped
* unavailable

不得将skipped写成passed。

---

## 51. Dependency Audit

如果没有新增依赖：

* 明确记录lockfile unchanged
* 记录使用标准库gzip或现有codec

如果必须新增依赖：

* 说明合同为何无法使用现有依赖完成
* version
* license
* transitive dependencies
* package size
* Windows/Linux support
* offline behavior
* deterministic behavior
* security findings
* decompression safety
* lockfile变化

不得为了读取尚未支持的HDF5或VTK格式提前加入重型依赖。

---

## 52. Commit / Push / CI

全部完成后：

```bash
git status --short
git diff --stat
git add <only Phase 10J related files>
git commit -m "Define volumetric data contracts"
git push origin master
```

等待current-HEAD CI。

必须确认：

* backend unit success
* frontend tests success
* frontend typecheck success
* frontend build success
* volumetric contract tests success
* scientific reference tests success
* payload security tests success
* Phase 10 Closure success
* Phase 10G regression success
* Phase 10H regression success
* Phase 10I regression success
* service-backed integration success
* no-skipped assertion success
* origin/master equals HEAD
* git status clean

不得伪造commit、CI run、测试数量或git状态。

---

## 53. PASS 判定

PASS必须全部满足：

* 真实schema和validator实现，不是docs-only
* grid schema完成
* payload schema完成
* field schema完成
* dataset schema完成
* manifest schema完成
* row step-vector约定明确
* periodic/non-periodic语义明确
* origin语义明确
* sample location明确
* endpoint policy明确
* periodic canonical endpoint excluded
* flatten order固定
* scalar/vector/complex语义明确
* dtype/endianness明确
* binary payload完成
* byte-length验证完成
* compression安全策略完成
* chunk完整性完成
* quantity identity完成
* units完成
* normalization/integral完成
* spin语义完成
* potential reference完成
* statistics完成
* structure/lattice兼容验证完成
* grid/payload/field/dataset hash分层完成
* deterministic fixtures完成
* independent references完成
* cap/overflow检查完成
* decompression bomb防护完成
* no pickle/object deserialization
* no artifact JS
* no external URL
* no Renderer
* no Tool registration
* Phase 10I-3不回退
* tests通过
* CI通过
* origin/master等于HEAD
* git status clean

---

## 54. PARTIAL_PASS 仅允许

仅允许：

* canonical compression暂时只支持`none`和`gzip`
* chunking只支持沿`i`轴完整slab
* complex vector明确DEFERRED_BY_DESIGN
* mixed-periodicity明确DEFERRED_BY_DESIGN
* masked/sparse data明确DEFERRED_BY_DESIGN
* exact unit转换只覆盖合同已定义单位
* JSON-only preview没有新增专用frontend，因为通用preview足够
* npm/Python audit因既有registry不可用，但依赖未变化且审计完整

以下缺失不得PARTIAL_PASS：

* coordinate convention
* flatten order
* byte-length validation
* payload hashing
* units
* endpoint policy
* caps
* validators
* fixtures
* independent references
* decompression safety

这些缺失必须FAIL。

---

## 55. FAIL 条件

以下任一情况必须FAIL：

* 只有规划文档
* 没有正式schema
* 没有validator
* 网格坐标方向含糊
* row/column约定混用
* endpoint policy未固定
* periodic grid保存重复endpoint却未声明
* flatten order依赖NumPy默认
* component顺序含糊
* dtype/endianness含糊
* payload长度不验证
* 接受NaN/Infinity
* 接受pickle/object array
* 解压前不检查caps
* 允许nested archive
* chunk有gap/overlap仍通过
* quantity和unit不匹配仍通过
* electron density和charge density混同
* spin channel语义含糊
* potential reference未记录
* complex field只保留real part
* grid与structure lattice不验证
* 使用axis-aligned box代替triclinic grid
* 只有source filename，没有content hash
* artifact包含JS/HTML/URL/shader
* 提前注册生产Tool
* 提前实现不受控Renderer
* 伪造Parser或browser evidence
* skipped写成passed
* Phase 10I回退
* CI失败却声明PASS
* git不clean却声明完成

---

## 56. 最终报告格式

完成后必须输出：

# Phase 10J Volumetric Data Contract Result

## 1. Conclusion

PASS / PARTIAL_PASS / FAIL

## 2. Baseline

* Phase 10I-3 commit
* initial HEAD
* branch
* origin/master
* initial status
* final HEAD
* final status

## 3. Pre-Implementation Audit

* spatial convention
* artifact/storage support
* array support
* dependency state
* selected schema strategy

## 4. Schema Family

* grid
* payload
* field
* dataset
* manifest
* versions

## 5. Grid Mathematics

* row vectors
* origin
* step matrix
* periodicity
* sample location
* endpoint policy
* coordinate conversion
* voxel volume

## 6. Index / Storage Order

* logical indices
* flatten order
* component order
* shape
* offsets
* reference validation

## 7. Field Semantics

* scalar
* vector
* complex
* quantities
* units
* components
* normalization
* integral semantics

## 8. Scientific Specializations

* electron/charge density
* spin channels
* magnetization
* electrostatic potential reference
* complex wavefunction semantics
* explicit readiness boundaries

## 9. Payload

* dtype
* endianness
* encodings
* raw bytes
* compression
* chunks
* byte validation
* hashes

## 10. Statistics

* min/max
* mean/RMS
* integral
* accumulation
* histogram
* validation

## 11. Structure Compatibility

* structure hash
* lattice hash
* periodic grid
* origin shift
* triclinic support
* supercell policy

## 12. Caps / Security

* dimensions
* voxels
* bytes
* compression ratio
* chunks
* metadata
* allocation
* decompression
* executable-content policy

## 13. Fixtures / References

* cubic constant
* periodic trigonometric
* triclinic
* non-periodic affine
* collinear spin
* non-collinear magnetization
* complex scalar
* potential gauge
* chunked
* negative cases

## 14. Determinism

* canonical order
* compression
* content hashes
* chunk-independent identity
* replay

## 15. Preview / Handoff

* JSON metadata preview
* Parser readiness
* Isosurface readiness
* slice readiness
* renderer status

## 16. Tests

* grid
* payload
* fields
* dataset
* manifest
* references
* security
* regression
* service-backed
* no-skipped

## 17. Evidence

* directory
* schema snapshots
* binary fixtures
* validation outputs
* reference outputs
* replay
* hashes
* audits

## 18. Files

列出主要implementation、tests、fixtures、evidence、docs和persistent文件。

## 19. Explicitly Not Implemented

* production file parsers
* Tool Registry
* Planner
* Runtime execution
* isosurface
* volume renderer
* charge/spin-density product
* electrostatic-potential product
* Bader analysis
* reciprocal/time-dependent volume

## 20. Checks

* diff
* lock
* dependency tree
* frontend tests
* typecheck
* build
* backend tests
* fixture replay
* compression security
* secrets

## 21. Commit / CI

* commit
* HEAD
* CI run
* unit
* frontend
* build
* contract tests
* scientific references
* service-backed
* no-skipped
* origin
* git status

## 22. Readiness

预期：

```text
volumetric grid contract: READY
payload contract: READY
field contract: READY
dataset contract: READY
manifest contract: READY
periodic real-space grid: READY
non-periodic affine grid: READY
real scalar field: READY
real vector field: CONTRACT_READY
complex scalar field: CONTRACT_READY
binary payload: READY
bounded compression: READY
chunked payload: READY
scientific quantity semantics: READY
security: READY
production file parsers: NOT_IMPLEMENTED
Tool Registry: NOT_REGISTERED
isosurface renderer: NOT_IMPLEMENTED
charge-density product: NOT_IMPLEMENTED
full volumetric product: NOT_READY
```

## 23. Whether Allowed to Enter Next Phase

可以 / 不可以

只有 Phase 10J Contract 完成、current-HEAD CI通过、数学reference、binary fixtures、caps和安全验证闭合且git clean后，才允许进入：

```text
Phase 10J-1：Volumetric Parser / Adapter
```

现在开始执行。

先读取真实Phase 10I-3 Result、structure/lattice contracts、现有artifact storage和complex-array模型，输出Pre-Implementation Audit；然后实现volumetric grid、payload、field、dataset和manifest schemas、validators、fixtures、independent references、deterministic replay、安全审计、docs、commit和CI闭环。

本阶段不得进入生产Parser、Tool Registry、等值面或Three.js volume renderer。


---END---
