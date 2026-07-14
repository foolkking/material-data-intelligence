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
