---TASK---
 状态：处理中
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
