---TASK---
状态：已完成
 # Phase 10F-25：Clipping, Cell and Camera Controls

进入 Phase 10F-25：Clipping, Cell and Camera Controls。

可以默认：

* Phase 10F-24 已完成
* supercell productization 已完成
* supercell expansion、instance generation、bond replication、deduplication、persistence、picking、measurement 已完成
* Phase 10F-23 advanced picking and measurement 已完成
* Phase 10F-22 accessibility、mobile、cross-browser 已完成
* Phase 10F-21 performance budgets、instancing、bond batching、lifecycle 已完成
* current production scene schema 仍为 `phase10f18.viewer_scene.v2
* current manifest仍为当前 v2 manifes
* canonical periodic topology、PeriodicSiteRef、measurement identity、supercell display state保持稳定
* 当前 branch、HEAD、working tree 和 Phase 10F-24 CI 可视为正确且 clean

本阶段不需要重复 baseline 检查。

---

# 1. 本阶段目标

本阶段目标：

> 为周期晶体 viewer 增加科学可解释的空间控制能力，包括 clipping、unit cell/supercell boundary display、camera presets 和视角控制，同时保持周期拓扑、measurement、picking、performance、安全边界不变。

本阶段重点：

* clipping plane foundation
* bounded section inspection
* unit cell display
* supercell boundary display
* lattice axes display
* camera presets
* deterministic camera state
* view state persistence
* accessibility
* mobile interaction
* browser evidence

---

# 2. 当前能力基础

当前 viewer 已具备：

* unit cell结构
* supercell display
* periodic instances
* canonical bonds
* picking
* measuremen
* inspector
* keyboard controls
* mobile gestures
* camera rotate / pan / zoom
* performance budgets
* degraded/refused mode
* lifecycle cleanup
* JSON-only fallback

当前缺少：

* clipping plane
* section view
* scientific slice inspection
* cell boundary toggle
* axis display
* camera prese
* camera state serialization
* view reproducibility
* clipping accessibility
* clipping mobile behavior

---

# 3. 严格禁止范围

本阶段不得实现：

* structure editing
* atom mutation
* bond mutation
* lattice editing
* trajectory
* phonon
* Brillouin zone
* volumetric rendering
* charge density
* spin density
* isosurface
* defects
* surfaces
* slabs
* arbitrary mesh editing
* CAD-like modeling
* expor
* glTF/GLB
* PNG/PDF
* formal structure.viewer_3d registration
* external APIs
* notebook execution
* script execution
* real LLM

不得：

* 修改 canonical lattice
* 修改 fractional coordinates
* 修改 canonical topology
* 修改 periodic identity
* 使用 clipping 修改实际结构数据
* 将camera state当作scientific data
* 将clip后的显示结果写回scene
* 允许artifact控制camera代码
* 允许artifact控制clip shader
* 引入远程shader
* 引入外部viewer runtime
* 放宽performance caps

允许：

* renderer state
* camera state
* clipping state
* display-only derived state
* tests
* evidence
* docs

---

# 4. 必读代码

开始前阅读：

## 4.1 Camera

搜索：

```bash
rg -n "Camera|OrbitControls|PerspectiveCamera|OrthographicCamera|controls|zoom|rotate|pan" apps/web


确认：

* camera初始化
* controls
* reset逻辑
* lifecycle
* resize
* mobile handling
* keyboard camera controls
* persistence

---

## 4.2 Cell Display

搜索：

```bash
rg -n "lattice|cell|boundary|axis|supercell|grid" apps/web


确认：

* 当前unit cell
* supercell boundary
* line geometry
* visibility
* styling
* disposal

---

## 4.3 Rendering Pipeline

搜索：

```bash
rg -n "ShaderMaterial|clippingPlanes|renderer.localClippingEnabled|material" apps/web


确认：

* 是否已有Three.js clipping能力
* material共享策略
* shader修改风险
* GPU lifecycle

---

# 5. 修改前审计输出

输出：

# Phase 10F-25 Pre-Implementation Audi

## 1. Current Camera

* camera type:
* controls:
* reset:
* keyboard:
* mobile:
* persistence:

## 2. Current Cell Display

* unit cell:
* supercell:
* axes:
* lattice vectors:
* geometry count:

## 3. Current Rendering

* material strategy:
* shader:
* clipping support:
* renderer capabilities:

## 4. Performance Risks

列出：

* clipping cos
* extra draw calls
* extra geometry
* camera animation cos
* mobile GPU risk

## 5. Selected Strategy

说明：

* clipping implementation
* cell display
* camera presets
* persistence
* caps
* fallback

---

# 6. Clipping Contrac

建立：

```ts
type ViewerClipState = {
  enabled: boolean;
  planes: ClipPlane[];
};


推荐：

```ts
type ClipPlane = {
  axis: "x" | "y" | "z";
  position: number;
  enabled: boolean;
};


要求：

* application-owned
* bounded
* deterministic
* no arbitrary plane equation输入
* no shader injection
* no artifact callback

---

# 7. Clipping Policy

第一阶段只支持：

* axis aligned clipping

支持：

* X
* Y
* Z

不支持：

* arbitrary normal vector
* user drawn plane
* boolean geometry cu
* mesh modification

原因：

* 更容易保持科学解释
* 更容易保证性能
* 更容易跨浏览器

---

# 8. Clip Semantics

必须明确：

clip只影响：

* renderer visibility

不影响：

* scene JSON
* topology
* picking identity
* measurement coordinates

例如：

atom被clip隐藏：

* 仍存在于scene
* 不改变siteIndex
* 不改变bond

---

# 9. Clipping UI

提供：

* enable/disable
* X/Y/Z选择
* position slider/inpu
* rese

要求：

* keyboard accessible
* mobile usable
* numeric input验证
* slider bounded
* live region提示一次

显示：

例如：

```tex
Clipping X enabled at 4.2 Å


---

# 10. Clipping Caps

必须限制：

* maximum active planes

推荐：

```tex
max active clipping planes = 3


不得：

* 创建无限plane
* 每atom创建clip对象

---

# 11. Cell Display

实现：

## Unit Cell

支持：

* show/hide

显示：

* lattice edges
* origin
* vectors

---

## Supercell Boundary

支持：

* show/hide

根据Phase 10F-24：

```tex
A' = aA
B' = bB
C' = cC


显示：

* outer boundary

默认：

* 不显示内部所有cell grid

原因：

避免大量line geometry。

---

## Internal Grid

可选。

必须：

* bounded
* disabled by defaul

限制：

* 最大cell数量
* 最大line数量

---

# 12. Axis Display

提供：

* a vector
* b vector
* c vector

要求：

* text label
* color不是唯一标识
* accessibility文本说明

例如：


a vector length: 5.43 Å
b vector length: 5.43 Å
c vector length: 5.43 Å


---

# 13. Camera Presets

建立：

```ts
type CameraPreset =
 | "default"
 | "top"
 | "front"
 | "side"
 | "isometric";


要求：

* deterministic
* bounded
* keyboard accessible
* mobile accessible

每个preset定义：

* position
* targe
* up vector

不得：

* 自动随机旋转
* 无限动画

---

# 14. Camera State Contrac

可选保存：

```json
{
 "schema_version":"phase10f25.camera_state.v1",
 "preset":"isometric",
 "position":[1,2,3],
 "target":[0,0,0],
 "zoom":1
}


要求：

* finite
* bounded
* validated

不得保存：

* Three.js对象
* matrix对象
  -函数
* callback

---

# 15. Camera Animation

如果已有：

必须支持：

* reduced motion

要求：

prefers-reduced-motion:

* instant transition

否则：

* bounded short transition

禁止：

* 无限旋转
* idle animation

---

# 16. Picking Integration

必须验证：

clip开启时：

* visible atom可pick
* hidden atom不可pick

但是：

measurement/picking identity保持：


siteIndex@[imageOffset]


不得：

* clip重新生成scene
* 修改instance mapping

---

# 17. Measurement Integration

必须验证：

clip不会影响：

* distance
* angle
* dihedral

因为：

measurement来自world coordinates。

---

# 18. Supercell Integration

测试：

* clip + supercell
* cell boundary + supercell
* camera preset + supercell
* picking copied instance

---

# 19. Accessibility

必须保持Phase 10F-22。

新增：

必须可读：

* clipping enabled
* active plane
* plane position
* visible cell mode
* camera prese

例如：


Clipping enabled. X plane at 3.5 angstrom.
Camera preset: top.


不得：

* 只靠视觉

---

# 20. Mobile

测试：

* slider
* numeric inpu
* presets
* orientation change
* clipping
* camera controls
* inspector

要求：

* 不阻塞viewer
* 不破坏gesture
* 不增加scroll trap

---

# 21. Performance

必须保持：

* no per-frame clipping allocation
* no geometry rebuild on camera move
* no material explosion
* no duplicate renderer

记录：

before/after：

* draw calls
* geometries
* materials
* GPU resources
* canvas coun

---

# 22. Tests

必须覆盖：

## Clipping

* enable
* disable
* x/y/z
* multiple planes
* rese
* invalid values

## Cell

* unit cell
* supercell
* triclinic
* hide/show

## Camera

* presets
* rese
* serialization
* invalid state

## Integration

* clipping + picking
* clipping + measuremen
* clipping + supercell
* mobile
* lifecycle

---

# 23. Evidence

新增：


docs/phase10f/evidence/phase10f25_clipping_cell_camera/


包含：


README.md
clipping_contract.json
camera_contract.json
cell_display.json
camera_presets.json
performance_metrics.json
browser_matrix.json
mobile_matrix.json
security_audit.json
network_audit.json
artifact_hashes.json


截图：


01_unit_cell.png
02_supercell_boundary.png
03_clipping_x.png
04_clipping_xyz.png
05_camera_top.png
06_camera_isometric.png
07_mobile_controls.png
08_picking_after_clip.png
09_measurement_after_clip.png
10_reset_view.png


---

# 24. Security

必须确认：

* no shader injection
* no artifact clipping plane
* no artifact camera callback
* no external assets
* no remote shader
* no eval
* no Function
* no iframe
* no network
* no secre

输出：


NO_EXTERNAL_NETWORK_REQUESTS
NO_SECRET_PATTERN_HITS


---

# 25. Docs

新增：


docs/phase10f/phase10f25_clipping_cell_camera.md
docs/phase10f/phase10f25_clipping_contract.md
docs/phase10f/phase10f25_camera_contract.md
docs/phase10f/phase10f25_cell_display_contract.md
docs/phase10f/phase10f25_security.md
docs/phase10f/phase10f25_evidence.md


更新：


persistent/DESIGN_PROGRESS.md
persistent/TASK_BOARD.md
persistent/CHANGELOG.md
persistent/ARCHITECTURE_DECISIONS.md


---

# 26. Readiness Matrix

最终输出：


clipping foundation: READY
axis clipping: READY
cell display: READY
supercell boundary: READY
camera presets: READY
camera persistence: READY
picking integration: READY
measurement integration: READY
accessibility: READY
mobile: READY
performance: READY
security: READY

full structure.viewer_3d: PARTIAL_READY

export: NOT_READY
trajectory: NOT_READY
phonon: NOT_READY
Brillouin zone: NOT_READY
volumetric: NOT_READY


---

# 27. Checks

运行：

```bash
git diff --check
uv lock --check

npm --prefix apps/web tes
npm --prefix apps/web run typecheck
npm --prefix apps/web run build

uv run python -m pytest -q


额外：

* clipping tests
* camera tests
* lifecycle tests
* browser tests
* mobile tests
* performance regression
* accessibility regression
* security scan

---

# 28. Commi

完成：

```bash
git status --shor
git add <Phase 10F-25 files>
git commit -m "Add viewer clipping cell and camera controls"
git push origin master


确认：

* CI success
* origin/master matches
* clean tree

---

# 29. 最终报告

输出：

# Phase 10F-25 Clipping, Cell and Camera Controls Resul

包括：

1. Conclusion
2. Baseline
3. Clipping contrac
4. Cell display
5. Supercell integration
6. Camera presets
7. Persistence
8. Picking
9. Measuremen
10. Accessibility
11. Mobile
12. Performance
13. Security
14. Evidence
15. Tests
16. Files
17. Deferred
18. Readiness
19. Commit / CI
20. Whether allowed to enter next phase

PASS条件：

* clipping真实工作
* cell显示真实工作
* camera presets真实工作
* 不修改结构
* 不修改topology
* picking/measurement保持正确
* performance不回退
* accessibility不回退
* browser evidence完整
* security闭合
* CI通过
* git clean

下一阶段建议：


Phase 10F-26：Scientific Export and Reporting Foundation


不要进入trajectory、phonon、Brillouin zone或volumetric。
## 完成记录

* 完成时间：2026-07-13 14:05 +08:00
* 修改文件：viewer view-state contract、controls、renderer engine/types/surface、CSS、component/contract tests、browser runners、Phase 10F-25 evidence/docs 和 persistent 记录。
* 修改摘要：实现最多 3 个 application-owned X/Y/Z clipping planes、共享材质 WebGL clipping 与同语义 raycast gate；独立 unit-cell/supercell-boundary/lattice-axes display；deterministic default/top/front/side/isometric camera presets；inert phase10f25.viewer_view_state.v1 validation/download/replay；未修改 canonical scene、periodic topology、measurement、backend runtime 或依赖。
* 测试结果：frontend 98 passed；backend 366 passed, 21 skipped, 11 warnings；typecheck/build/uv lock 通过；全部历史 viewer runners 与新增 Chromium 150、Firefox 128、WebKit 18/mobile runner 通过；hidden clipped atom pick rejected；console/page errors 0；NO_EXTERNAL_NETWORK_REQUESTS；NO_SECRET_PATTERN_HITS；npm audit 因 npmmirror NOT_IMPLEMENTED 不可用；本地 service-backed 因无 Docker 命令不可用；GitHub Actions run 29227580893（SHA 460867536564b1846fefaea138625ef6878bddcb）的 unit、frontend npm ci/typecheck/build、PostgreSQL+Redis+MinIO service-backed integration 和 no-skipped assertion 全部成功。
---END---


---TASK---
 状态：已完成
 # Phase 10F-26：Scientific Export and Reporting Foundation

进入 Phase 10F-26：Scientific Export and Reporting Foundation。

可以默认：

* Phase 10F-25 已完成
* clipping、cell display、supercell boundary、camera presets 和 camera state 已完成
* Phase 10F-24 supercell productization 已完成
* Phase 10F-23 picking and measurement 已完成
* Phase 10F-22 accessibility、mobile、cross-browser 已完成
* Phase 10F-21 performance hardening 已完成
* current production scene schema 仍为 `phase10f18.viewer_scene.v2
* current manifest仍为当前 v2 manifes
* periodic identity、canonical bonds、measurement、supercell、clipping 和 camera controls均保持稳定
* 当前 branch、HEAD、working tree 和 Phase 10F-25 CI 可视为正确且 clean

本阶段不需要重复 baseline 检查。

本阶段主要目标：

> 为当前 periodic crystal viewer 建立安全、确定性、可复现的科学导出和报告基础，使用户可以导出视图、状态、测量结果和结构化报告，同时不允许 artifact 执行代码或加载外部资源。

本阶段重点包括：

* deterministic PNG expor
* high-DPI screensho
* transparent/solid background
* camera-consistent expor
* clipping/supercell state capture
* measurement overlay capture
* JSON state expor
* manifest expor
* Markdown scientific summary
* PDF readiness assessmen
* export artifact contracts
* export accessibility
* browser evidence
* security closure

本阶段仍不是 trajectory、phonon、Brillouin zone 或 volumetric phase。

---

# 1. 当前已知能力

当前 viewer 已具备：

* validated `viewer_scene.v2
* periodic site identity
* canonical bonds
* cross-boundary and self-periodic topology
* picking
* distance / angle / dihedral measuremen
* supercell display
* clipping
* cell boundaries
* camera presets
* deterministic camera state
* accessibility
* mobile interaction
* performance budgets
* browser matrix
* lifecycle cleanup
* no artifact JS
* no external assets

当前尚未正式实现：

* PNG expor
* high-resolution expor
* deterministic export dimensions
* transparent background expor
* export with/without overlays
* export with current camera
* export with saved camera prese
* export with clipping/supercell state
* measurement result packaging
* scientific summary artifac
* export manifes
* export recipe
* PDF export readiness
* browser export evidence
* export security audi

---

# 2. 本阶段目标

必须完成以下八类工作：

1. Export architecture audi
2. Deterministic render capture
3. PNG and image expor
4. JSON state and measurement expor
5. Scientific summary/report artifac
6. Export provenance and manifes
7. Browser/mobile evidence
8. Security、tests、docs和readiness收口

本阶段必须产生真实可下载的 export artifacts。

如果最终只有文档、按钮占位或静态fixture，没有真实浏览器导出路径，本阶段必须判定为 FAIL。

---

# 3. 严格禁止范围

本阶段不得实现：

* trajectory
* phonon
* Brillouin zone
* volumetric rendering
* charge density
* spin density
* isosurface
* defects
* surfaces
* slabs
* structure editing
* atom mutation
* bond mutation
* canonical structure export，除非已有安全、明确contrac
* glTF/GLB expor
* arbitrary 3D format expor
* video expor
* animation expor
* notebook execution
* script execution
* external API
* cloud upload
* remote storage
* email/share service
* real LLM
* formal `structure.viewer_3d` registration

不得：

* 修改 canonical scene
* 修改 topology
* 修改 measurement values
* 重新计算 bonds
* 将截图结果作为科学数据源
* 将 export 过程依赖外部 CDN
* 允许 artifact 控制文件名路径
* 允许 path traversal
* 允许任意 MIME type
* 允许任意 HTML
* 执行 artifact JS
* 允许 external URL
* 允许 remote fonts/textures
* 导出用户未明确请求的私有信息
* 在图片中泄漏本地路径、token或调试数据
* 通过浏览器打印对话框伪装成PDF export完成
* 将未实现的PDF标记为READY

允许：

* canvas capture
* application-owned export rendering
* deterministic offscreen render
* PNG generation
* JSON generation
* Markdown generation
* safe download
* manifes
* recipe
* tests
* evidence
* docs
* persistent updates

---

# 4. 必读代码

开始后直接阅读当前真实实现。

## 4.1 Renderer Capture

搜索：

```bash
rg -n "toDataURL|toBlob|canvas|preserveDrawingBuffer|WebGLRenderer|renderTarget|screenshot|export" apps/web


确认：

* current renderer lifecycle
* canvas ownership
* preserveDrawingBuffer setting
* render scheduling
* camera state
* clipping state
* supercell state
* measurement overlay
* background handling

## 4.2 Artifact and Download

搜索：

```bash
rg -n "download|Blob|URL.createObjectURL|artifact|manifest|recipe|summary.md" apps/web backend packages


确认：

* current artifact download helpers
* filename sanitization
* MIME policy
* object URL cleanup
* existing JSON/Markdown artifact patterns
* security metadata conventions

## 4.3 Measurement and Viewer State

确认：

* measurement artifac
* supercell state artifac
* camera state
* clipping state
* scene identity
* provenance
* deterministic serialization

## 4.4 Existing Browser Evidence

定位：

* screenshot helpers
* browser runners
* Playwright download handling
* mobile runner
* cross-browser runner

---

# 5. 修改前输出审计

修改前输出：

# Phase 10F-26 Scientific Export Pre-Implementation Audi

## 1. Current Export Capability

* image export:
* JSON export:
* Markdown export:
* download helper:
* filename handling:
* MIME handling:
* provenance:
* manifest:
* current gaps:

## 2. Renderer Capture Risks

* preserveDrawingBuffer:
* canvas reuse:
* offscreen rendering:
* background:
* clipping:
* overlays:
* devicePixelRatio:
* browser differences:
* memory:
* context loss:

## 3. Artifact Risks

至少检查：

* path traversal
* object URL leak
* stale scene expor
* wrong camera state
* wrong clipping state
* missing periodic identity
* inconsistent measurement values
* external resources
* hidden debug data
* non-deterministic timestamps
* browser-specific PNG differences
* large image memory
* mobile download behavior

## 4. Selected Strategy

说明：

* PNG capture:
* export dimensions:
* high-DPI:
* background:
* overlays:
* JSON:
* Markdown:
* manifest:
* filename:
* security:
* fallback:

## 5. Planned Files

列出：

* renderer/export helper
* UI
* artifact serializer
* tests
* browser runner
* evidence
* docs
* persisten

审计后直接继续实现。

---

# 6. Export Contrac

建立 application-owned export request contract。

推荐：

```ts
type ViewerExportRequest = {
  format: "png" | "json" | "markdown";
  width?: number;
  height?: number;
  pixelRatio?: number;
  background: "transparent" | "light" | "dark";
  includeCell: boolean;
  includeAxes: boolean;
  includeBonds: boolean;
  includeMeasurements: boolean;
  includeInspectorSummary: boolean;
};


必须：

* strict validation
* bounded values
* deterministic defaults
* no arbitrary MIME
* no arbitrary extension
* no arbitrary path
* no executable fields
* no callback
* no URL

推荐默认：

```json
{
  "format": "png",
  "width": 1600,
  "height": 1200,
  "pixel_ratio": 1,
  "background": "light",
  "include_cell": true,
  "include_axes": true,
  "include_bonds": true,
  "include_measurements": true,
  "include_inspector_summary": false
}


---

# 7. Export Size and Resource Caps

必须定义：

* minimum width
* maximum width
* minimum heigh
* maximum heigh
* max total pixels
* max pixel ratio
* max estimated memory
* max concurrent export jobs

建议：

```tex
min width/height: 256
max width/height: 4096
max total pixels: 16,777,216
max pixel ratio: 2
max concurrent export: 1


具体数值应结合真实代码和浏览器测试调整。

必须在 allocation 前检查。

Typed errors：

```tex
VIEWER_EXPORT_INVALID_SIZE
VIEWER_EXPORT_PIXEL_BUDGET_EXCEEDED
VIEWER_EXPORT_BUSY
VIEWER_EXPORT_SCENE_UNAVAILABLE
VIEWER_EXPORT_CONTEXT_LOST
VIEWER_EXPORT_FAILED


---

# 8. PNG Expor

## 8.1 Deterministic Capture

导出必须使用当前 validated scene 和 applied viewer state。

必须捕获：

* camera
* targe
* zoom
* projection
* supercell expansion
* clipping state
* cell visibility
* axes visibility
* bond visibility
* measurement overlays
* background

不得捕获：

* hover tooltip
* transient focus ring，除非明确选择
* browser chrome
* unrelated UI
* private debug panels
* console
* local file path

## 8.2 Capture Strategy

优先：

* application-owned export render pass
* fixed output dimensions
* temporary render target或bounded offscreen renderer
* capture完成后dispose

不建议永久启用：

```tex
preserveDrawingBuffer: true


如果必须使用，需证明性能影响可接受。

## 8.3 Deterministic Camera

导出使用：

* current camera state
* 或 selected camera prese

必须明确。

导出前不自动改变用户camera。

## 8.4 Background

支持：

* transparen
* ligh
* dark

background由应用定义。

不得由artifact提供任意CSS或shader。

## 8.5 High-DPI

支持 bounded high-DPI。

必须：

* 先检查pixel budge
* 不使用设备真实DPR作为无上限输入
* mobile默认更保守
* 导出后恢复renderer state

---

# 9. Overlay Expor

必须明确可选包含：

* cell boundary
* supercell boundary
* axes
* bonds
* selected atoms
* measurement lines
* angle/dihedral overlays

默认不包含：

* hover state
* inspector panel
* controls
* warnings overlay

可选生成单独的文本summary，而不是把大量UI画进PNG。

不得：

* 让export改变selection
* 让export改变measuremen
* 让export改变scene

---

# 10. JSON Expor

至少生成：

```tex
viewer_export_state.json


建议schema：

```json
{
  "schema_version": "phase10f26.viewer_export_state.v1",
  "scene_schema_version": "phase10f18.viewer_scene.v2",
  "scene_identity": "...",
  "viewer_state": {
    "supercell_expansion": [2,2,1],
    "camera_preset": "isometric",
    "camera_position": [1,2,3],
    "camera_target": [0,0,0],
    "clipping": [],
    "show_unit_cell": true,
    "show_supercell_boundary": true,
    "show_axes": true,
    "show_bonds": true
  },
  "measurements": [],
  "export_request": {
    "format": "png",
    "width": 1600,
    "height": 1200,
    "background": "light"
  },
  "deterministic": true,
  "security": {
    "contains_javascript": false,
    "external_urls": []
  }
}


要求：

* deterministic key ordering
* no NaN/Infinity
* no renderer objects
* no raw Three.js matrix unless normalized
* no local path
* no URL
* no callback
* no HTML
* no executable conten

---

# 11. Scientific Markdown Summary

生成：

```tex
viewer_export_summary.md


至少包含：

* formula
* scene schema
* lattice summary
* canonical site coun
* canonical bond coun
* cross-boundary bond coun
* self-periodic bond coun
* supercell expansion
* displayed atom coun
* displayed bond coun
* camera preset/state summary
* clipping summary
* measurements
* export dimensions
* background
* provenance
* security declaration
* known limitations

不得：

* 声称 authoritative chemistry
* 声称截图本身是结构数据
* 省略periodic identity
* 使用远程图片
* 嵌入HTML或脚本

---

# 12. Export Manifes

新增：

```tex
viewer_export_manifest.json


建议schema：

```json
{
  "schema_version": "phase10f26.viewer_export_manifest.v1",
  "artifacts": [
    {
      "name": "viewer.png",
      "media_type": "image/png",
      "sha256": "..."
    },
    {
      "name": "viewer_export_state.json",
      "media_type": "application/json",
      "sha256": "..."
    },
    {
      "name": "viewer_export_summary.md",
      "media_type": "text/markdown",
      "sha256": "..."
    }
  ],
  "renderer_included": false,
  "javascript_included": false,
  "external_assets": []
}


要求：

* exact allowlis
* deterministic artifact order
* hashes
* sizes
* media types
* no executable assets
* no external URLs
* no renderer bundle

---

# 13. Filename Policy

必须 application-owned。

推荐：

```tex
viewer.png
viewer_export_state.json
viewer_export_summary.md
viewer_export_manifest.json


可允许安全前缀：

```tex
<sanitized_formula>_viewer.png


必须：

* strip path separators
* strip control chars
* bound length
* normalized Unicode
* fallback name
* no user-provided extension

不得允许：

```tex
../../secre
C:\...
file://
http://


---

# 14. UI

提供：

* Export button
* format selector
* dimensions
* background
* include overlays
* export preview summary
* progress
* success
* failure

要求：

* keyboard accessible
* mobile usable
* touch targets合格
* focus managemen
* live-region announcements
* no color-only status
* export during busy state disabled
* invalid size blocked before allocation

建议预设：

```tex
Web 1200×900
Presentation 1600×900
Square 1600×1600
Publication 2400×1800


所有preset必须经过caps。

---

# 15. Accessibility

必须保持Phase 10F-22标准。

必须可读：

* selected forma
* dimensions
* estimated pixels
* background
* included overlays
* progress
* success
* failure
* downloaded filename

Live region：

```tex
Export started.
Export completed: viewer.png.
Export failed: image size exceeds safe limit.


不得播报：

* binary data
* object URL
* hashes全文
* internal stack

---

# 16. Mobile

必须测试：

* export panel
* preset selection
* dimensions
* export PNG
* export JSON
* download resul
* orientation change
* repeated expor
* over-budget rejection

要求：

* mobile使用更保守默认尺寸
* 导出期间不冻结UI
* 不创建重复canvas/contex
* export完成后资源释放
* download失败时提供明确fallback

---

# 17. Lifecycle

必须处理：

* export star
* export cancel
* scene switch
* artifact switch
* camera change
* clipping change
* supercell change
* context loss
* component unmoun
* browser tab hidden
* mobile orientation

要求：

* export绑定scene generation
* scene变化后stale export不得完成为当前scene
* stale export结果必须丢弃
* temporary renderer/target dispose
* object URL revoke
* no canvas leak
* no context leak
* no stale success message
* no duplicate downloads

---

# 18. PDF Readiness

本阶段必须做正式评估，但不要求强制实现PDF。

允许结果：

```tex
PDF export: DEFERRED_BY_DESIGN


原因可包括：

* browser print nondeterministic
* vector fidelity未定义
* font embedding未定义
* pagination contract未定义
* no approved PDF dependency

不得用浏览器 `window.print()` 直接标记 PDF READY。

必须记录后续PDF所需：

* page size
* image embedding
* metadata
* fonts
* vector/raster policy
* accessibility
* deterministic layou
* dependency/security review

---

# 19. Performance

必须保持Phase 10F-21预算。

记录：

* capture duration
* encode duration
* total duration
* temporary geometries
* temporary materials
* temporary textures/render targets
* canvas coun
* context coun
* memory proxy before/after

必须验证：

* repeated export no monotonic growth
* 10次bounded repeated expor
* over-budget rejected before allocation
* export不改变interactive renderer性能
* no continuous loop

不得用严格毫秒值作为唯一PASS依据。

---

# 20. Security

必须验证：

* no artifact JS
* no HTML execution
* no SVG scrip
* no remote image
* no remote fon
* no CDN
* no external URL
* no iframe
* no eval
* no Function constructor
* no path traversal
* no arbitrary MIME
* no arbitrary extension
* no raw local path
* no token
* no private debug data
* no browser fingerprinting
* no cloud upload
* no telemetry upload
* no object URL leak
* no export of hidden unrelated UI
* no artifact-controlled filename path
* no artifact-controlled shader
* no artifact-controlled camera callback

必须输出：

```tex
NO_EXTERNAL_NETWORK_REQUESTS
NO_SECRET_PATTERN_HITS


---

# 21. Tests

## 21.1 Export Contract Tests

覆盖：

* valid PNG
* valid JSON
* valid Markdown
* invalid forma
* invalid dimensions
* pixel budge
* pixel ratio
* background
* unknown fields

## 21.2 PNG Tests

覆盖：

* defaul
* transparen
* dark
* high-DPI
* camera prese
* clipping
* supercell
* measurement overlay
* no inspector UI
* deterministic dimensions
* repeated expor

## 21.3 JSON Tests

覆盖：

* schema
* scene identity
* camera
* clipping
* supercell
* measurements
* deterministic ordering
* nonfinite rejection
* no executable fields

## 21.4 Markdown Tests

覆盖：

* formula
* counts
* periodic identity
* measurement formatting
* clipping
* camera
* limitations
* no HTML/scrip

## 21.5 Manifest Tests

覆盖：

* exact files
* hashes
* sizes
* media types
* stable order
* no JS
* no external assets

## 21.6 Lifecycle Tests

覆盖：

* scene switch during expor
* context loss
* unmoun
* repeated expor
* object URL cleanup
* temporary renderer cleanup
* no duplicate download

## 21.7 Regression

必须保持：

* periodic identity
* topology
* performance
* accessibility
* picking
* measuremen
* supercell
* clipping
* camera
* compatibility
* no external network
* no artifact JS

---

# 22. Browser Evidence

新增：

```tex
docs/phase10f/evidence/phase10f26_scientific_export/


必须使用真实浏览器。

## Chromium

覆盖：

* PNG defaul
* transparent PNG
* high-DPI
* supercell
* clipping
* measurement overlays
* JSON
* Markdown
* manifes
* repeated expor
* stale export cancellation

## Firefox

至少覆盖：

* PNG
* JSON
* clipping
* repeated expor
* download handling

## WebKi

至少覆盖：

* PNG
* transparent background
* measurement overlay
* JSON
* lifecycle

## Mobile

至少覆盖：

* export panel
* prese
* PNG
* JSON
* over-budget rejection
* repeated expor
* orientation change

---

# 23. Evidence Assertions

每个browser evidence记录：

* browser version
* viewpor
* scene
* viewer state
* forma
* dimensions
* pixel ratio
* background
* included overlays
* filename
* media type
* size
* hash
* duration
* canvas/context counts
* console errors
* network requests

必须验证：

* image dimensions exac
* camera state exac
* clipping state exac
* supercell state exac
* measurement values exac
* manifest hashes exac
* no external network
* no executable assets
* repeated export no leak
* stale export rejected

---

# 24. Evidence Files

至少包含：

```tex
README.md
export_contract.json
export_caps.json
png_export_results.json
transparent_export_results.json
high_dpi_results.json
camera_consistency.json
clipping_consistency.json
supercell_consistency.json
measurement_overlay_results.json
json_export_results.json
markdown_export_results.json
manifest_validation.json
repeated_export_stress.json
stale_export_cancellation.json
browser_matrix.json
mobile_matrix.json
console_audit.json
network_audit.json
security_audit.json
artifact_hashes.json


截图或导出样例：

```tex
01_default_viewer.png
02_transparent_background.png
03_dark_background.png
04_supercell_export.png
05_clipping_export.png
06_measurement_export.png
07_mobile_export_panel.png
08_export_success.png


不要保存：

* browser cache
* private paths
* token
* debug dump
* remote asse
* giant images beyond caps
* object URLs
* crash dumps

---

# 25. Docs / Persisten

新增或更新：

```tex
docs/phase10f/phase10f26_scientific_export.md
docs/phase10f/phase10f26_export_contract.md
docs/phase10f/phase10f26_png_export.md
docs/phase10f/phase10f26_export_manifest.md
docs/phase10f/phase10f26_export_security.md
docs/phase10f/phase10f26_pdf_readiness.md
docs/phase10f/phase10f26_export_evidence.md
docs/phase10f/phase10f26_export_readiness_matrix.md


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

* export contrac
* size caps
* PNG strategy
* high-DPI policy
* background policy
* camera consistency
* clipping/supercell consistency
* measurement overlay policy
* JSON schema
* Markdown summary
* manifes
* security
* PDF deferred/ready decision
* remaining formal viewer registration work

---

# 26. Readiness Matrix

最终分别判断：

* export request contrac
* filename policy
* PNG expor
* transparent background
* dark/light background
* high-DPI
* current camera capture
* camera preset capture
* clipping capture
* supercell capture
* measurement overlay
* JSON state expor
* Markdown summary
* manifes
* deterministic hashes
* lifecycle
* repeated expor
* accessibility
* mobile
* Chromium
* Firefox
* WebKi
* security
* PDF expor
* full `structure.viewer_3d
* trajectory
* phonon
* Brillouin zone
* volumetric

推荐期望：

```tex
export request contract: READY
PNG export: READY
transparent background: READY
high-DPI export: READY
camera consistency: READY
clipping consistency: READY
supercell consistency: READY
measurement overlay: READY
JSON export: READY
Markdown summary: READY
manifest: READY
deterministic serialization: READY
lifecycle: READY
accessibility: READY
mobile: READY
browser matrix: READY
security: READY
PDF export: DEFERRED_BY_DESIGN or PARTIAL_READY
full structure.viewer_3d: PARTIAL_READY
trajectory: NOT_READY
phonon: NOT_READY
Brillouin zone: NOT_READY
volumetric: NOT_READY


---

# 27. Checks

至少运行：

```bash
git diff --check
uv lock --check

npm --prefix apps/web tes
npm --prefix apps/web run typecheck
npm --prefix apps/web run build

uv run python -m pytest -q


并运行：

* export focused tests
* PNG tests
* JSON tests
* Markdown tests
* manifest tests
* filename security tests
* repeated export stress
* lifecycle tests
* performance regression
* accessibility regression
* Chromium runner
* Firefox runner
* WebKit runner
* mobile runner
* service-backed integration
* no-skipped assertion
* secret scan
* network audi

必须如实记录：

* passed
* failed
* skipped
* unavailable

不得把 skipped 写成 passed。

---

# 28. Commit / CI

完成实现、tests、evidence和docs后：

```bash
git status --shor
git diff --sta
git add <only Phase 10F-26 related files>
git commit -m "Add scientific viewer export foundation"
git push origin master


等待current HEAD CI。

必须确认：

* unit success
* frontend tests success
* frontend typecheck success
* frontend build success
* service-backed integration success
* no-skipped assertion success
* origin/master matches HEAD
* git status clean

不得伪造CI。

---

# 29. 最终报告格式

输出：

# Phase 10F-26 Scientific Export and Reporting Foundation Resul

## 1. Conclusion

PASS / PARTIAL_PASS / FAIL

## 2. Baseline

* Phase 10F-25 assumed complete:
* branch:
* initial status:
* final HEAD:
* final status:

## 3. Export Architecture

* capture strategy:
* renderer reuse:
* temporary resources:
* deterministic state:
* cancellation:
* cleanup:

## 4. Export Contrac

* schema:
* formats:
* dimensions:
* pixel ratio:
* backgrounds:
* overlays:
* caps:

## 5. PNG Expor

* default:
* transparent:
* dark/light:
* high-DPI:
* dimensions:
* camera:
* clipping:
* supercell:
* measurements:

## 6. JSON Expor

* schema:
* viewer state:
* measurements:
* provenance:
* determinism:
* security:

## 7. Markdown Summary

* structure:
* topology:
* supercell:
* clipping:
* camera:
* measurements:
* limitations:

## 8. Manifes

* schema:
* files:
* hashes:
* media types:
* executable assets:
* external assets:

## 9. Filename and Download

* sanitization:
* extensions:
* MIME allowlist:
* object URL cleanup:
* mobile download:

## 10. Lifecycle

* repeated export:
* scene switch:
* context loss:
* unmount:
* stale export:
* temporary resource cleanup:

## 11. Performance

* capture duration:
* encoding:
* memory proxy:
* repeated trend:
* over-budget:
* interactive renderer impact:

## 12. Accessibility

* controls:
* live region:
* progress:
* error:
* mobile:
* focus:

## 13. Browser Evidence

* Chromium:
* Firefox:
* WebKit:
* mobile:
* downloads:
* console:
* network:

## 14. PDF Readiness

* decision:
* implemented:
* deferred:
* remaining requirements:

## 15. Security

* filenames:
* MIME:
* executable content:
* external resources:
* hidden UI:
* secrets:
* network:
* dependencies:

## 16. Evidence

* directory:
* contracts:
* PNG:
* JSON:
* Markdown:
* manifest:
* stress:
* screenshots:
* markers:

## 17. Tests

* export:
* PNG:
* JSON:
* Markdown:
* manifest:
* security:
* frontend full:
* backend full:
* typecheck:
* build:
* browsers:
* mobile:
* service-backed:
* no-skipped:
* lock:
* diff:

## 18. Files

* renderer/export:
* UI:
* serializers:
* tests:
* browser runners:
* evidence:
* docs:
* persistent:
* dependencies/lockfile:

## 19. Deferred

明确列出：

* true vector SVG expor
* PDF export，若未实现
* glTF/GLB
* video/animation expor
* structure file expor
* collaboration/share links
* formal `structure.viewer_3d
* trajectory
* phonon
* Brillouin zone
* volumetric
* defects
* surfaces
* slabs
* structure editing

## 20. Readiness

* PNG:
* high-DPI:
* transparent:
* JSON:
* Markdown:
* manifest:
* lifecycle:
* accessibility:
* mobile:
* browser matrix:
* PDF:
* full `structure.viewer_3d`:
* trajectory:
* phonon:
* Brillouin:
* volumetric:

## 21. Commit / CI

* commit:
* HEAD:
* CI run:
* unit:
* frontend:
* build:
* service-backed:
* no-skipped:
* origin:
* status:

## 22. Whether allowed to enter next phase

允许 / 不允许

下一阶段建议：

```tex
Phase 10F-27：Formal structure.viewer_3d Registration and Product Evidence


不要进入 trajectory、phonon、Brillouin zone 或 volumetric。

---

# 30. PASS 判定

PASS必须满足：

* 有真实PNG expor
* PNG尺寸确定
* background可选
* high-DPI受cap约束
* camera state一致
* clipping一致
* supercell一致
* measurement overlay一致
* JSON state export完成
* Markdown summary完成
* manifest完成
* filename安全
* MIME allowlis
* no path traversal
* no executable asse
* no external asse
* repeated export无泄漏
* stale export保护完成
* mobile可导出
* Chromium/Firefox/WebKit证据完整
* performance不回退
* accessibility不回退
* no external network
* no secret hits
* tests通过
* CI通过
* git clean

PARTIAL_PASS仅允许：

* PDF明确deferred
* 某浏览器PNG编码二进制hash不同，但视觉和尺寸等语义证据一致
* mobile下载API有平台限制，但生成和fallback完整
* npm audit因既有registry问题不可用

FAIL包括：

* 只有截图按钮占位
* 依赖浏览器页面截图而非viewer capture
* 导出包含无关UI或私有路径
* export修改scene/camera
* over-budget先分配后拒绝
* object URL泄漏
* stale scene导出成功
* artifact可控制路径/MIME
* 引入远程资源
* 用window.print伪造PDF READY
* 无browser evidence
* CI失败却声明PASS

完成时间：2026-07-13 16:14:28 +08:00

修改文件：
- `apps/web/app/components/viewer-scene/ViewerExportPanel.tsx`
- `apps/web/app/components/viewer-scene/ViewerSceneRendererSurface.tsx`
- `apps/web/app/components/viewer-scene/viewerSceneExport.ts`
- `apps/web/app/components/viewer-scene/viewerSceneRendererEngine.ts`
- `apps/web/app/components/viewer-scene/viewerSceneRendererTypes.ts`
- `apps/web/app/globals.css`
- export/component tests and browser evidence runners
- `docs/phase10f/phase10f26_*` and `docs/phase10f/evidence/phase10f26_scientific_export/`
- shared schema, docs index, and persistent project records

修改摘要：
- Added strict bounded PNG/JSON/Markdown scientific export requests and responsive controls.
- Reused one validated Three.js renderer with temporary size, DPR, background, and overlay state plus complete restoration.
- Added transparent/light/dark and high-DPI PNG, deterministic inert view-state JSON, scientific Markdown, and ordered SHA-256 manifest.
- Added stale-scene/camera cancellation, one-export concurrency, safe filenames/errors, Blob URL cleanup, and PDF deferred-by-design closure.
- Added live Chromium/Firefox/WebKit/mobile evidence and updated the historical production accessibility assertion to use semantic controls.

测试结果：
- export/renderer focused: `29 passed`
- frontend full: `104 passed`
- frontend typecheck/build: passed
- backend full: `366 passed, 21 skipped, 11 warnings`
- all historical viewer browser runners: passed
- Phase 10F-26 browser markers: passed; external requests `0`; console/page errors `0`
- `uv lock --check` and `git diff --check`: passed
- npm audit: unavailable (`npmmirror` audit endpoint `NOT_IMPLEMENTED`); no dependency or lockfile changes
- local service-backed: unavailable because Docker CLI is not installed
- CI run `29234514215` for `fd9212ae5e659643c9204e402c1fd59e785763b8`: unit, frontend install/typecheck/build, service-backed integration, and no-skipped assertion all succeeded
- security: `NO_SECRET_PATTERN_HITS`, `NO_EXTERNAL_NETWORK_REQUESTS`

---END---

---TASK---
 状态：已完成
 # Phase 10F-27：Formal `structure.viewer_3d` Registration and Product Evidence

进入 Phase 10F-27：Formal `structure.viewer_3d` Registration and Product Evidence。

可以默认：

-   Phase 10F-26 已完成

-   scientific export and reporting foundation 已完成

-   PNG、JSON、Markdown、manifest export 已完成或按Phase 10F-26结论收口

-   Phase 10F-25 clipping、cell、camera controls 已完成

-   Phase 10F-24 supercell productization 已完成

-   Phase 10F-23 advanced picking and measurement 已完成

-   Phase 10F-22 accessibility、mobile、cross-browser 已完成

-   Phase 10F-21 performance hardening 已完成

-   current production scene schema 仍为 `phase10f18.viewer_scene.v2

-   current manifest、measurement、supercell、camera、clipping、export contracts均已稳定

-   periodic identity、canonical periodic topology、performance、安全边界均保持稳定

-   当前 branch、HEAD、working tree 和 Phase 10F-26 CI 可视为正确且 clean


本阶段不需要重复 baseline 检查。

本阶段主要目标：

> 将现有已经完成技术闭环的 periodic crystal viewer，正式注册为生产可发现、可规划、可执行、可审计的 `structure.viewer_3d` 工具，并完成 Browser/API/Product Evidence。

本阶段不是新的科学功能扩展阶段。

不得借正式注册之名继续加入trajectory、phonon、Brillouin zone、volumetric、defects、surfaces、slabs或structure editing。

----------

# 1. 本阶段目标

必须完成以下九类工作：

1.  **Formal tool contract**

2.  **Tool Registry registration**

3.  **Planner discovery and routing**

4.  **Execution adapter and artifact closure**

5.  **Product UI integration**

6.  **API evidence**

7.  **Browser evidence**

8.  **Security and readiness closure**

9.  **Formal product acceptance**


本阶段必须形成真实的production execution path。

如果最终只有registry metadata、docs或静态fixture，没有planner/API/browser真实调用，本阶段必须判定为FAIL。

----------

# 2. 当前能力基础

当前viewer已经具备：

-   `viewer_scene.v2

-   canonical lattice

-   canonical sites

-   periodic image identity

-   canonical periodic bonds

-   same-cell bonds

-   cross-boundary bonds

-   self-periodic bonds

-   triclinic suppor

-   neighbor inspector

-   performance budgets

-   large-scene degraded/refused policy

-   accessibility

-   mobile

-   atom/bond picking

-   distance/angle/dihedral measuremen

-   supercell

-   clipping

-   cell controls

-   camera presets

-   scientific expor

-   deterministic artifacts

-   browser matrix

-   no artifact JS

-   no external assets

-   no remote renderer assets


当前尚未正式完成：

-   `structure.viewer_3d`正式tool ID

-   Tool Registry registration

-   planner discoverability

-   planner routing

-   API invocation

-   job execution

-   artifact manifest declaration

-   frontend product entry

-   formal product evidence

-   final readiness decision

-   legacy viewer tool consolidation

-   capability truthfulness

-   production user-facing documentation


----------

# 3. 严格禁止范围

本阶段不得实现：

-   trajectory

-   trajectory playback

-   phonon

-   phonon animation

-   Brillouin zone

-   volumetric rendering

-   charge density

-   spin density

-   isosurface

-   defects

-   surfaces

-   slabs

-   structure editing

-   atom mutation

-   bond mutation

-   lattice editing

-   arbitrary annotations

-   arbitrary scene scripting

-   remote assets

-   external renderer

-   notebook execution

-   script execution

-   real LLM

-   new plugin framework

-   new auth model

-   multi-tenant changes


不得：

-   修改 `viewer_scene.v2` periodic topology semantics

-   修改 canonical bond identity

-   修改 `1e-5 Å` bond tolerance

-   放宽 PlanValidator

-   绕过 Tool Registry

-   绕过 execution runtime

-   使用隐藏未注册路径

-   将preview-only路径伪装成正式tool execution

-   将legacy Phase 10D schema标记成curren

-   将canonical v1标记成periodic

-   让artifact执行JS

-   加载remote texture、font、shader、module

-   让artifact控制camera callback、shader、URL或event handler

-   在capability中宣称trajectory/phonon/volumetric为true

-   将PARTIAL_READY项写成READY

-   伪造browser/API evidence

-   伪造CI

-   通过直接调用前端内部fixture绕过正式API


允许：

-   registry changes

-   planner metadata

-   adapter wiring

-   artifact contract wiring

-   frontend entry poin

-   API route exposure

-   tests

-   evidence

-   docs

-   persistent updates


----------

# 4. 必读实现

开始后直接阅读当前真实代码。

## 4.1 Tool Registry

搜索：

```bash
rg -n "ToolRegistry|tool_id|structure.viewer|viewer_3d|registered_tools|tool catalog" backend packages apps tests



确认：

-   registry schema

-   tool metadata

-   input contrac

-   output contrac

-   capability metadata

-   registration mechanism

-   discovery endpoin

-   planner integration

-   validation


## 4.2 Planner

搜索：

```bash
rg -n "planner|available tools|tool selection|tool routing|PlanValidator|AnalysisPlan" backend apps tests



确认：

-   planner tool catalog

-   tool capability descriptions

-   input matching

-   unsupported input behavior

-   deterministic test planner

-   no-real-LLM path

-   service-backed integration


## 4.3 Execution

检查：

-   adapter registration

-   job runtime

-   artifact emission

-   manifest emission

-   validation

-   provenance

-   result preview

-   retry behavior

-   failure behavior


## 4.4 Frontend Product Entry

检查：

-   tool selection UI

-   planner workbench

-   results page

-   viewer preview

-   JSON fallback

-   export controls

-   accessibility

-   mobile layou

-   legacy compatibility handling


## 4.5 Existing Viewer Tools

搜索所有：

```tex
structure.viewer_scene_metadata
structure.viewer_export_package
phase10d viewer tools
phase10f viewer adapters



必须审计是否存在：

-   duplicate tools

-   overlapping tools

-   deprecated tools

-   hidden aliases

-   conflicting output schemas


----------

# 5. 修改前输出审计

修改代码前输出：

# Phase 10F-27 Formal Viewer Registration Pre-Implementation Audi

## 1. Current Viewer Tool Inventory

对每个viewer-related tool列出：

-   tool ID

-   registry status

-   producer

-   inpu

-   outpu

-   schema

-   planner visibility

-   API visibility

-   browser visibility

-   deprecation status


## 2. Current Production Path

-   planner:

-   registry:

-   execution:

-   artifact:

-   manifest:

-   preview:

-   renderer:

-   export:

-   browser:

-   API:


## 3. Registration Gaps

至少列出：

-   missing formal ID

-   duplicate legacy path

-   output schema ambiguity

-   capability drif

-   planner nondiscovery

-   missing API evidence

-   missing browser evidence

-   missing result metadata

-   unsupported input ambiguity

-   fallback ambiguity


## 4. Selected Strategy

说明：

-   formal tool ID

-   legacy tool policy

-   input contrac

-   output contrac

-   planner registration

-   execution routing

-   product UI

-   evidence

-   deprecation


## 5. Planned Files

列出预计修改或新增：

-   registry

-   adapter

-   planner

-   validator

-   API

-   frontend

-   tests

-   evidence

-   docs

-   persisten


审计完成后直接继续实现。

----------

# 6. Formal Tool ID

正式注册：

```tex
structure.viewer_3d



必须保证：

-   唯一

-   稳定

-   无alias冲突

-   不与legacy tool重名

-   不在不同registry重复定义

-   不通过magic string散落定义


推荐application-owned constant。

----------

# 7. Tool Metadata

正式metadata至少包含：

```json
{
  "tool_id": "structure.viewer_3d",
  "category": "structure",
  "display_name": "3D Structure Viewer",
  "description": "Render and inspect periodic crystal structures with canonical periodic topology.",
  "input_contract": "structure_input.v1",
  "output_contract": "phase10f18.viewer_scene.v2",
  "manifest_contract": "phase10f19.viewer_assets_manifest.v2",
  "execution_mode": "service_backed",
  "deterministic": true,
  "network_access": false
}



字段名按真实registry规范调整。

必须明确：

-   periodic structure：true

-   periodic bonds：true

-   cross-boundary bonds：true

-   neighbor graph：true

-   picking：true

-   measurement：true

-   supercell：true

-   clipping：true

-   export：按Phase 10F-26真实结论

-   trajectory：false

-   phonon：false

-   Brillouin zone：false

-   volumetric：false

-   editing：false


capability不得过度宣称。

----------

# 8. Input Contrac

必须明确正式input。

至少支持：

-   valid periodic crystal structure

-   lattice

-   fractional coordinates

-   species

-   optional canonical bond source，若adapter contract允许

-   deterministic viewer options，若正式支持


必须拒绝或typed fallback：

-   molecule without lattice，除非已有独立nonperiodic contrac

-   trajectory

-   phonon data

-   volumetric grid

-   malformed lattice

-   nonfinite coordinates

-   over-cap site coun

-   arbitrary renderer config

-   executable payload

-   external URLs


typed codes建议：

```tex
STRUCTURE_VIEWER_3D_INPUT_INVALID
STRUCTURE_VIEWER_3D_LATTICE_REQUIRED
STRUCTURE_VIEWER_3D_SITE_LIMIT_EXCEEDED
STRUCTURE_VIEWER_3D_UNSUPPORTED_DATA_KIND
STRUCTURE_VIEWER_3D_RENDER_BUDGET_EXCEEDED



----------

# 9. Output Contrac

正式输出必须以：

```tex
phase10f18.viewer_scene.v2



为current scene contract。

同时输出current manifest。

至少包含：

-   scene

-   manifes

-   recipe

-   validation outpu

-   optional export artifacts

-   summary


不得默认生成：

-   Phase 10D legacy schema

-   canonical v1

-   renderer bundle

-   JavaScrip

-   HTML

-   remote assets


如果需要compatibility artifact：

-   必须显式

-   仅test/legacy mode

-   不进入default production path


----------

# 10. Adapter Registration

正式adapter必须：

-   register once

-   deterministic

-   validated inpu

-   validated outpu

-   no network

-   no external resources

-   no artifact JS

-   no hidden renderer bundle

-   current v2 outpu

-   exact capabilities

-   stable warnings

-   sanitized errors


必须证明：

```tex
inpu
→ adapter
→ viewer_scene.v2
→ manifes
→ validator
→ artifact store
→ frontend renderer



完整闭环。

----------

# 11. Legacy Tool Policy

必须审计并处理旧viewer-related tools。

建议策略：

## Phase 10D tools

-   deprecated

-   not planner-visible

-   not recommended

-   read-only artifact compatibility

-   no new production generation


## Phase 10F pre-formal adapters

允许：

-   internal implementation backing `structure.viewer_3d

-   hidden fromplanner catalog

-   not separately user-facing

-   no duplicate formal registration


必须避免：

-   planner看到多个近似viewer tools

-   用户不知道该选哪个

-   一个输出v1、一个输出v2

-   capability冲突


最终只应有一个正式用户可发现ID：

```tex
structure.viewer_3d



----------

# 12. Planner Registration

必须将 `structure.viewer_3d` 加入 planner tool catalog。

Planner描述必须准确：

适合：

-   periodic crystal visualization

-   bond topology inspection

-   supercell display

-   measuremen

-   static viewer expor


不适合：

-   trajectory

-   phonon

-   volumetric

-   editing

-   Brillouin zone


必须有tests验证：

-   “show this crystal in 3D”选择viewer

-   “inspect periodic bonds”选择viewer

-   “measure distance in structure”选择viewer或viewer-compatible path

-   “play trajectory”不得选择viewer完成trajectory

-   “plot phonon bands”不得选择viewer

-   “render charge density”不得选择viewer


----------

# 13. PlanValidator

必须确保：

-   tool ID known

-   input artifact kind compatible

-   output schema known

-   unsupported capability rejected

-   no executable artifact reques

-   no external resource reques

-   no over-cap options

-   no arbitrary renderer config


不得放宽PlanValidator。

如果planner请求：

```tex
trajectory=true



必须拒绝或route到未来tool，不得让viewer静默忽略。

----------

# 14. API Registration

正式API路径必须真实可调用。

至少证明：

-   tool discovery

-   job creation

-   execution

-   status polling

-   artifact retrieval

-   validation resul

-   failure resul


复用现有API，不建议新增重复route。

API evidence必须通过正式路径：

```tex
POST planner/job or equivalen
→ registered tool
→ service-backed execution
→ artifacts



不得：

-   直接调用adapter函数伪造API evidence

-   仅测试fixture endpoin

-   绕过job runtime


----------

# 15. API Evidence Cases

至少覆盖：

## Valid Orthogonal

-   scene PASS

-   manifest PASS

-   renderer-compatible


## Valid Triclinic

-   periodic offsets

-   cross-boundary bonds

-   renderer-compatible


## Self-Periodic

-   nonzero self-periodic bond

-   inspector-compatible


## Large but Allowed

-   degraded mode

-   artifact valid


## Over-Budge

-   artifact or input valid

-   renderer fallback typed

-   no crash


## Invalid

-   invalid lattice

-   nonfinite coordinates

-   typed failure

-   sanitized error


----------

# 16. Product UI Registration

正式frontend entry必须：

-   显示 `3D Structure Viewer

-   显示tool ID或合理用户名称

-   支持planner result打开

-   支持renderer

-   支持JSON-only fallback

-   支持inspector

-   支持measuremen

-   支持supercell

-   支持clipping/camera

-   支持expor

-   支持accessibility

-   支持mobile


必须显示真实capability summary。

不得显示：

-   trajectory ready

-   phonon ready

-   volumetric ready

-   editing ready


----------

# 17. Result Surface

正式result surface至少显示：

-   formula

-   site coun

-   lattice

-   canonical bond coun

-   cross-boundary bond coun

-   render mode

-   schema version

-   tool ID

-   capabilities

-   warnings

-   security state

-   artifact downloads


必须区分：

-   artifact valid

-   renderer degraded

-   renderer refused

-   tool execution failed


不得将renderer budget exceeded写成analysis job failure。

----------

# 18. Product UX

正式产品路径必须具备：

-   loading

-   success

-   warning

-   degraded

-   over-budge

-   invalid

-   retry

-   JSON fallback

-   artifact download

-   no blank screen

-   no silent failure


必须保持：

-   keyboard

-   focus

-   mobile

-   browser matrix

-   context loss fallback

-   lifecycle cleanup


----------

# 19. Formal Capability Contrac

建立可机器验证的正式capability。

建议：

```json
{
  "periodic_structure": true,
  "periodic_bonds": true,
  "cross_boundary_bonds": true,
  "neighbor_graph": true,
  "picking": true,
  "measurement": true,
  "supercell": true,
  "clipping": true,
  "camera_presets": true,
  "png_export": true,
  "json_export": true,
  "markdown_export": true,
  "trajectory": false,
  "phonon": false,
  "brillouin_zone": false,
  "volumetric": false,
  "editing": false
}



必须与真实implementation一致。

若Phase 10F-26某项是PARTIAL_READY或DEFERRED：

-   这里不得写true

-   或使用更准确状态模型


禁止简单boolean过度宣称。

----------

# 20. Evidence Package

新增：

```tex
docs/phase10f/evidence/phase10f27_structure_viewer_3d_product/



至少包含：

```tex
README.md
tool_registration.json
tool_registry_snapshot.json
planner_catalog_snapshot.json
capability_contract.json
input_contract.json
output_contract.json
manifest_validation.json
api_valid_orthogonal.json
api_valid_triclinic.json
api_self_periodic.json
api_large_degraded.json
api_over_budget.json
api_invalid_input.json
browser_product_matrix.json
mobile_product_matrix.json
legacy_tool_policy.json
security_audit.json
network_audit.json
artifact_hashes.json



截图建议：

```tex
01_tool_discovery.png
02_planner_selected_viewer.png
03_job_running.png
04_viewer_success.png
05_triclinic_periodic.png
06_self_periodic.png
07_measurement.png
08_supercell.png
09_clipping_camera.png
10_export.png
11_degraded_mode.png
12_over_budget_fallback.png
13_mobile_viewer.png
14_json_fallback.png



----------

# 21. Browser Evidence

必须通过真实产品路径。

## Chromium

覆盖：

-   tool discovery

-   planner selection

-   job execution

-   result render

-   picking

-   measuremen

-   supercell

-   clipping

-   expor

-   degraded mode

-   over-budget fallback

-   context loss

-   reload/reopen artifac


## Firefox

至少覆盖：

-   planner→job→resul

-   periodic render

-   measuremen

-   expor

-   fallback


## WebKi

至少覆盖：

-   planner→job→resul

-   render

-   mobile-like interaction

-   expor

-   fallback


## Mobile

至少覆盖：

-   tool discovery或result entry

-   renderer

-   controls

-   measuremen

-   supercell

-   expor

-   degraded/refused state


----------

# 22. Browser Evidence Assertions

每个case记录：

-   browser version

-   viewpor

-   tool ID

-   planner choice

-   job ID或sanitized identity

-   execution status

-   scene schema

-   manifest schema

-   capabilities

-   render mode

-   artifact names

-   console errors

-   network requests

-   canvas coun

-   context coun


必须验证：

-   formal tool ID shown

-   planner selects correct tool

-   job executes registered adapter

-   output is v2

-   no legacy default outpu

-   renderer loads

-   fallback works

-   no external network

-   no artifact JS

-   no duplicate canvas/contex

-   no capability overclaim


----------

# 23. API Evidence Assertions

必须记录：

-   reques

-   selected tool

-   validated plan

-   job status

-   adapter execution

-   output schemas

-   artifact names

-   warnings

-   typed errors

-   security metadata

-   hashes


必须证明：

-   Tool Registry真实参与

-   PlanValidator真实参与

-   runtime真实参与

-   artifact validator真实参与

-   frontend使用真实artifac


----------

# 24. Tests

## 24.1 Registry Tests

覆盖：

-   `structure.viewer_3d` registered

-   exactly once

-   metadata exac

-   current schema exac

-   capabilities exac

-   deprecated tools hidden

-   no alias collision


## 24.2 Planner Tests

覆盖：

-   visualization request selects viewer

-   bond inspection selects viewer

-   measurement request selects viewer-compatible route

-   trajectory request rejected/not routed

-   phonon request rejected/not routed

-   volumetric request rejected/not routed

-   editing request rejected/not routed


## 24.3 Validator Tests

覆盖：

-   valid structure

-   invalid lattice

-   nonfinite coordinates

-   unsupported data kind

-   over-cap sites

-   executable options

-   external URL

-   unsupported capability


## 24.4 Execution Tests

覆盖：

-   orthogonal

-   triclinic

-   self-periodic

-   degraded

-   over-budge

-   invalid

-   deterministic replay

-   artifact hashes


## 24.5 API Tests

覆盖：

-   discovery

-   job create

-   job status

-   artifact retrieve

-   validation

-   failure

-   retry，若现有runtime支持


## 24.6 Frontend Tests

覆盖：

-   product title

-   tool metadata

-   result render

-   JSON fallback

-   capability display

-   warnings

-   degraded

-   over-budge

-   invalid

-   expor

-   accessibility

-   mobile


## 24.7 Regression

必须保持：

-   Phase 10F-18 periodic topology

-   Phase 10F-19 integration

-   Phase 10F-20 compatibility

-   Phase 10F-21 performance

-   Phase 10F-22 accessibility

-   Phase 10F-23 picking/measuremen

-   Phase 10F-24 supercell

-   Phase 10F-25 clipping/camera

-   Phase 10F-26 expor

-   no external network

-   no artifact JS


----------

# 25. Security

必须验证：

-   no artifact JavaScrip

-   no artifact HTML execution

-   no remote assets

-   no external URL

-   no shader injection

-   no callback injection

-   no arbitrary renderer config

-   no arbitrary file access

-   no notebook execution

-   no script execution

-   no real LLM

-   no registry bypass

-   no planner bypass

-   no validator bypass

-   no hidden alias execution

-   no capability overclaim

-   no legacy schema masquerading as curren

-   no private path

-   no token

-   no secre

-   no telemetry upload


必须输出：

```tex
NO_EXTERNAL_NETWORK_REQUESTS
NO_SECRET_PATTERN_HITS



----------

# 26. Documentation

新增或更新：

```tex
docs/phase10f/phase10f27_structure_viewer_3d_registration.md
docs/phase10f/phase10f27_structure_viewer_3d_tool_contract.md
docs/phase10f/phase10f27_structure_viewer_3d_capabilities.md
docs/phase10f/phase10f27_structure_viewer_3d_planner_routing.md
docs/phase10f/phase10f27_structure_viewer_3d_api_evidence.md
docs/phase10f/phase10f27_structure_viewer_3d_browser_evidence.md
docs/phase10f/phase10f27_structure_viewer_3d_security.md
docs/phase10f/phase10f27_structure_viewer_3d_readiness_matrix.md



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

-   formal tool ID

-   input/output contracts

-   planner behavior

-   API behavior

-   artifact behavior

-   capability truth

-   legacy policy

-   product UX

-   security

-   remaining unsupported scopes


----------

# 27. Readiness Matrix

最终分别判断：

-   formal tool ID

-   registry

-   planner discovery

-   planner routing

-   PlanValidator

-   adapter

-   execution runtime

-   API

-   artifact emission

-   manifes

-   frontend product entry

-   renderer

-   JSON fallback

-   picking

-   measuremen

-   supercell

-   clipping

-   camera

-   expor

-   accessibility

-   mobile

-   performance

-   Chromium

-   Firefox

-   WebKi

-   security

-   legacy deprecation

-   full `structure.viewer_3d

-   trajectory

-   phonon

-   Brillouin zone

-   volumetric

-   editing


推荐期望：

```tex
formal tool ID: READY
registry: READY
planner discovery: READY
planner routing: READY
PlanValidator: READY
adapter: READY
execution runtime: READY
API: READY
artifact emission: READY
manifest: READY
frontend product entry: READY
renderer: READY
JSON fallback: READY
picking: READY
measurement: READY
supercell: READY
clipping: READY
camera: READY
export: READY or PARTIAL_READY according to Phase 10F-26
accessibility: READY
mobile: READY
performance: READY
browser matrix: READY
security: READY
legacy deprecation: READY
full structure.viewer_3d: READY
trajectory: NOT_READY
phonon: NOT_READY
Brillouin zone: NOT_READY
volumetric: NOT_READY
editing: NOT_READY



只有本阶段全部闭环后，才允许首次将：

```tex
full structure.viewer_3d: READY



----------

# 28. Checks

至少运行：

```bash
git diff --check
uv lock --check

npm --prefix apps/web tes
npm --prefix apps/web run typecheck
npm --prefix apps/web run build

uv run python -m pytest -q



并运行：

-   registry tests

-   planner tests

-   PlanValidator tests

-   adapter tests

-   execution tests

-   API tests

-   frontend product tests

-   browser tests

-   mobile tests

-   performance regression

-   accessibility regression

-   export regression

-   service-backed integration

-   no-skipped assertion

-   secret scan

-   network audi


必须如实记录：

-   passed

-   failed

-   skipped

-   unavailable


不得把skipped写成passed。

----------

# 29. Commit / CI

完成实现、tests、evidence和docs后：

```bash
git status --shor
git diff --sta
git add <only Phase 10F-27 related files>
git commit -m "Register structure viewer 3D product"
git push origin master



等待current HEAD CI。

必须确认：

-   unit success

-   frontend tests success

-   frontend typecheck success

-   frontend build success

-   service-backed integration success

-   no-skipped assertion success

-   origin/master matches HEAD

-   git status clean


不得伪造CI。

----------

# 30. 最终报告格式

输出：

# Phase 10F-27 Formal `structure.viewer_3d` Registration and Product Evidence Resul

## 1. Conclusion

PASS / PARTIAL_PASS / FAIL

## 2. Baseline

-   Phase 10F-26 assumed complete:

-   branch:

-   initial status:

-   final HEAD:

-   final status:


## 3. Formal Tool Registration

-   tool ID:

-   registry:

-   display name:

-   category:

-   deterministic:

-   network:

-   current schema:

-   manifest:


## 4. Capability Contrac

-   periodic structure:

-   periodic bonds:

-   cross-boundary:

-   neighbor graph:

-   picking:

-   measurement:

-   supercell:

-   clipping:

-   camera:

-   export:

-   trajectory:

-   phonon:

-   Brillouin:

-   volumetric:

-   editing:


## 5. Legacy Tool Policy

-   Phase 10D:

-   canonical v1:

-   internal adapters:

-   planner visibility:

-   user-facing IDs:

-   deprecation:


## 6. Planner

-   discovery:

-   routing:

-   valid visualization:

-   measurement:

-   trajectory rejection:

-   phonon rejection:

-   volumetric rejection:

-   editing rejection:


## 7. PlanValidator

-   known tool:

-   input validation:

-   output validation:

-   unsupported capability:

-   executable options:

-   external URLs:

-   caps:


## 8. Execution

-   adapter:

-   runtime:

-   scene:

-   manifest:

-   recipe:

-   validation:

-   deterministic replay:

-   warnings:

-   failure behavior:


## 9. API Evidence

-   discovery:

-   orthogonal:

-   triclinic:

-   self-periodic:

-   degraded:

-   over-budget:

-   invalid:

-   artifact retrieval:

-   typed errors:


## 10. Product UI

-   tool entry:

-   result surface:

-   renderer:

-   JSON fallback:

-   inspector:

-   measurement:

-   supercell:

-   clipping:

-   camera:

-   export:

-   warnings:

-   invalid state:


## 11. Browser Evidence

-   Chromium:

-   Firefox:

-   WebKit:

-   mobile:

-   planner:

-   execution:

-   renderer:

-   fallback:

-   export:

-   console:

-   network:


## 12. Performance

-   interactive:

-   degraded:

-   refused:

-   lifecycle:

-   canvas/context:

-   draw calls:

-   memory proxy:


## 13. Accessibility

-   keyboard:

-   focus:

-   semantic scene:

-   inspector:

-   measurement:

-   mobile:

-   fallback:

-   live regions:


## 14. Security

-   registry bypass:

-   planner bypass:

-   validator bypass:

-   artifact JS:

-   external assets:

-   capability overclaim:

-   legacy masquerading:

-   dependencies:

-   secrets:

-   network:


## 15. Evidence

-   directory:

-   registration:

-   registry snapshot:

-   planner snapshot:

-   capability contract:

-   API:

-   browser:

-   mobile:

-   security:

-   markers:


## 16. Tests

-   registry:

-   planner:

-   validator:

-   execution:

-   API:

-   frontend:

-   backend:

-   typecheck:

-   build:

-   browsers:

-   mobile:

-   service-backed:

-   no-skipped:

-   lock:

-   diff:


## 17. Files

-   registry:

-   planner:

-   adapter:

-   validator:

-   API:

-   frontend:

-   tests:

-   browser runners:

-   evidence:

-   docs:

-   persistent:

-   dependencies/lockfile:


## 18. Deferred

明确列出：

-   trajectory

-   trajectory playback

-   phonon

-   phonon animation

-   Brillouin zone

-   volumetric

-   charge density

-   spin density

-   isosurface

-   defects

-   surfaces

-   slabs

-   structure editing

-   atom mutation

-   bond mutation

-   lattice editing

-   collaboration

-   remote assets

-   external plugins


## 19. Readiness

-   formal tool:

-   registry:

-   planner:

-   validator:

-   execution:

-   API:

-   product UI:

-   renderer:

-   picking:

-   measurement:

-   supercell:

-   clipping:

-   camera:

-   export:

-   accessibility:

-   mobile:

-   performance:

-   security:

-   full `structure.viewer_3d`:

-   trajectory:

-   phonon:

-   Brillouin:

-   volumetric:

-   editing:


## 20. Commit / CI

-   commit:

-   HEAD:

-   CI run:

-   unit:

-   frontend:

-   build:

-   service-backed:

-   no-skipped:

-   origin:

-   status:


## 21. Whether allowed to enter next phase

允许 / 不允许

下一阶段建议：

```tex
Phase 10G：Brillouin Zone Planning and Contrac



下一阶段只做planning和contract，不直接实现Brillouin zone renderer。

----------

# 31. PASS 判定

PASS必须满足：

-   `structure.viewer_3d`正式注册

-   registry中唯一

-   planner可发现

-   planner可正确选择

-   unsupported scopes不误选

-   PlanValidator不放宽

-   service-backed execution真实闭环

-   API evidence真实闭环

-   browser evidence真实闭环

-   output默认v2

-   manifest正确

-   legacy不再作为正式production defaul

-   product UI真实可用

-   renderer真实可用

-   JSON fallback真实可用

-   picking/measurement/supercell/clipping/camera/export不回退

-   performance不回退

-   accessibility不回退

-   mobile不回退

-   capability metadata真实

-   trajectory/phonon/Brillouin/volumetric/editing全部false

-   no registry/planner/validator bypass

-   no artifact JS

-   no external network

-   no secret hits

-   tests通过

-   CI通过

-   git clean

-   `full structure.viewer_3d: READY


PARTIAL_PASS仅允许：

-   Phase 10F-26某个export子项本来就是PARTIAL_READY，且这里准确继承

-   某个mobile平台下载行为有既有限制，但viewer product路径完整

-   npm audit因既有registry问题不可用


FAIL包括：

-   只有registry metadata，没有真实执行

-   planner看不到tool

-   planner错误选择viewer处理trajectory/phonon/volumetric

-   API绕过runtime

-   browser使用fixture绕过product path

-   output仍默认legacy schema

-   capability过度宣称

-   formal tool与legacy tool冲突

-   PlanValidator被放宽

-   artifact执行JS或加载remote assets

-   无API evidence

-   无browser evidence

-   CI失败却声明PASS

-   full viewer未闭环却标记READY

完成时间：2026-07-13 17:57:29 +08:00

修改文件：

- `tool_registry/platform_builtin_manifest.yaml`、`tool_registry/matterviz_manifest.yaml`
- `tests/test_manifest_loader.py`、`tests/test_phase10f15_production_viewer.py`、`tests/test_phase10f27_formal_viewer_product.py`
- `apps/web/test/generate-viewer-scene-live-adapter-evidence.py`、`apps/web/test/generate-viewer-3d-product-evidence.py`
- `apps/web/test/viewer-scene-production-browser-evidence.mjs`、`apps/web/test/viewer-scene-formal-product-browser-evidence.mjs`
- `docs/phase10f/phase10f27_structure_viewer_3d_*.md`、`docs/phase10f/evidence/phase10f27_structure_viewer_3d_product/`
- `docs/index.md`、`docs/13_SHARED_SCHEMA_SPEC.md`、相关 `persistent/*.md`

修改摘要：

- 将唯一 `structure.viewer_3d` 条目迁移到 platform built-in manifest，保持 adapter、strict params、artifact 和 runtime 语义不变。
- 冻结正式 viewer 产品能力与负能力边界，保留显式 JSON route 和 legacy compatibility。
- 增加 registry/catalog/routing/PlanValidator/adapter tests，以及真实 planner job、periodic topology、三浏览器、移动、性能、accessibility、network 和 security evidence。
- 主提交：`187722a0b994971dabcf55882d0b169e3cbcd147 Register structure viewer 3D product`。

测试结果：

- 精确后端组：`27 passed`。
- frontend：`104 passed`；typecheck 和 Next.js production build 通过。
- backend full：`370 passed, 21 skipped, 11 warnings`。
- 13 个历史 viewer browser runners 与 Phase 10F-27 formal product runner 全部通过。
- Chromium 150、Firefox 128、WebKit 18 均 rendered；console errors `0`；external requests `0`。
- `uv lock --check`、`git diff --check`、`NO_EXTERNAL_NETWORK_REQUESTS`、`NO_SECRET_PATTERN_HITS` 通过。
- `npm audit` 因配置 registry 不实现 audit endpoint 而 unavailable；本阶段无 dependency/lockfile 变更。
- 本地 Docker CLI 不可用；current-HEAD CI run `29240890361` 的 unit、frontend npm ci/typecheck/build、PostgreSQL+Redis+MinIO service-backed integration 和 no-skipped assertion 全部 success。
---END---

---TASK---
 状态：已完成
 # Phase 10 Closure Regression Pack

进入 Phase 10 Closure Regression Pack。

可以默认：

-   Phase 10A 至 Phase 10F-27 已按各阶段结论完成

-   `structure.viewer_3d` 已正式注册

-   Phase 10F 系列已完成产品化收口

-   current production viewer scene schema 为 `phase10f18.viewer_scene.v2

-   current production manifest 为正式 v2 manifes

-   legacy Phase 10D viewer schema仅保留read-only / JSON-only compatibility

-   canonical v1仅保留same-cell legacy compatibility

-   v2为current periodic topology renderer contrac

-   Tool Registry、Planner、PlanValidator、service-backed runtime、artifact store、frontend result surface已形成正式路径

-   当前branch、HEAD、working tree和Phase 10F-27 CI可视为正确且clean


本阶段不需要重复Phase 10F-27 baseline检查。

本阶段不是新功能阶段。

本阶段主要目标：

> 建立一套精简、稳定、高价值的 Phase 10 总体回归测试包，证明 Phase 10 的数据适配、结构分析、可视化、viewer产品路径、artifact contracts、安全边界和跨模块组合在正式收口后仍然完整成立。

本阶段不得复制每个历史Phase的全部单元测试。

本阶段必须关注：

-   跨模块不变量

-   正式产品链路

-   关键能力组合

-   compatibility边界

-   deterministic replay

-   security closure

-   CI长期回归价值


----------

# 1. Closure Pack定位

Phase 10 Closure Regression Pack是：

-   Phase 10A–10F局部测试的补充

-   正式产品路径的端到端证明

-   后续Phase 10G及之后阶段的回归防线

-   CI中的长期稳定测试集合


它不是：

-   对所有历史单元测试的复制

-   新功能开发

-   大规模性能benchmark

-   全浏览器测试的重复实现

-   文档整理阶段

-   Phase 11 benchmark closure

-   Phase 10G功能实现


----------

# 2. 本阶段目标

必须完成以下八类工作：

1.  **Phase 10 test inventory audit**

2.  **Cross-phase invariant matrix**

3.  **Registry → Planner → Runtime → Artifact closure tests**

4.  **Viewer product composition tests**

5.  **Legacy and compatibility regression tests**

6.  **Determinism、security和lifecycle closure**

7.  **CI test entry and evidence**

8.  **Phase 10 final closure report**


本阶段必须新增真实测试代码。

如果最终只有测试计划、matrix、文档或已有测试列表，没有新增可执行closure tests，本阶段必须判定为FAIL。

----------

# 3. 严格禁止范围

本阶段不得实现：

-   新adapter

-   新tool

-   新viewer feature

-   trajectory

-   phonon

-   Brillouin zone

-   volumetric

-   defects

-   surfaces

-   slabs

-   structure editing

-   新export forma

-   新schema version

-   新manifest version

-   新planner behavior

-   新runtime机制

-   新认证

-   新外部API

-   notebook execution

-   script execution

-   real LLM


不得：

-   修改Phase 10既有科学语义以让测试通过

-   放宽validator

-   放宽PlanValidator

-   放宽performance caps

-   改写canonical periodic identity

-   改写canonical bond key

-   修改`1e-5 Å` bond tolerance

-   将legacy schema升级成curren

-   复制数千行已有测试

-   把已有单元测试简单重命名为closure tes

-   使用fixture-only路径代替正式产品路径

-   绕过Tool Registry

-   绕过Planner

-   绕过runtime

-   绕过artifact validator

-   绕过frontend product surface

-   将skipped测试写成passed

-   通过只跑Chromium声称完整cross-browser closure

-   将不稳定绝对时间阈值加入CI

-   引入大型新测试依赖


允许：

-   新增integration tests

-   新增closure fixtures

-   新增test helpers

-   新增Playwright product-path smoke tests

-   新增CI command或job step

-   新增evidence

-   新增docs

-   更新persistent记录


----------

# 4. 必读测试资产

开始后直接审计当前仓库。

## 4.1 Backend Tests

搜索：

```bash
find tests -maxdepth 4 -type f | sor
rg -n "phase10|viewer_3d|viewer_scene|ToolRegistry|PlanValidator|planner|artifact|manifest" tests backend packages



重点识别：

-   Phase 10A adapter tests

-   Phase 10B composition tests

-   Phase 10C structure adapter tests

-   Phase 10D viewer compatibility tests

-   Phase 10E static physics tests

-   Phase 10F viewer tests

-   registry tests

-   planner tests

-   service-backed integration tests

-   no-skipped assertion

-   artifact validation tests

-   security tests


## 4.2 Frontend Tests

搜索：

```bash
find apps/web -type f \( -name "*.test.ts" -o -name "*.test.tsx" -o -name "*.spec.ts" \) | sor
rg -n "viewer_3d|viewer_scene|measurement|supercell|clipping|export|accessibility|fallback" apps/web



识别：

-   preview tests

-   renderer tests

-   accessibility tests

-   picking tests

-   measurement tests

-   supercell tests

-   clipping/camera tests

-   export tests

-   product registration tests


## 4.3 Browser Tests

搜索：

```bash
find . -type f \( -iname "*playwright*" -o -iname "*browser*" -o -iname "*e2e*" \) | sor



确认：

-   Chromium runner

-   Firefox runner

-   WebKit runner

-   mobile runner

-   formal product-path evidence runner

-   download handling

-   network audi

-   console audi


## 4.4 CI

搜索：

```bash
find .github -type f -maxdepth 4 -prin
rg -n "pytest|npm test|typecheck|build|playwright|integration|no.*skipped" .github scripts pyproject.toml package.json apps/web/package.json



确认：

-   当前CI入口

-   哪些测试已经自动运行

-   哪些测试只在本地运行

-   哪些browser tests有独立job

-   closure pack最合适的接入方式


----------

# 5. 修改前输出审计

修改任何文件前输出：

# Phase 10 Closure Regression Pack Pre-Implementation Audi

## 1. Existing Test Inventory

按阶段列出：

-   Phase 10A:

-   Phase 10B:

-   Phase 10C:

-   Phase 10D:

-   Phase 10E:

-   Phase 10F:

-   registry/planner:

-   service-backed:

-   browser:

-   security:

-   CI:


每项说明：

-   test files

-   coverage

-   execution command

-   current gaps

-   whether suitable for reuse


## 2. Existing Product Path Coverage

-   tool discovery:

-   planner selection:

-   plan validation:

-   service-backed execution:

-   artifact validation:

-   artifact persistence:

-   frontend result:

-   renderer:

-   fallback:

-   export:

-   browser:

-   mobile:


## 3. Cross-Phase Gaps

至少检查：

-   adapter output进入正式runtime

-   static physics artifacts与preview兼容

-   viewer scene v2正式输出

-   legacy不成为defaul

-   periodic identity跨renderer/inspector/measurement一致

-   supercell与measurement组合

-   clipping与picking组合

-   export与viewer state一致

-   degraded/refused路径

-   deterministic replay

-   security markers

-   no external network

-   capability truth

-   lifecycle cleanup


## 4. Duplication Risks

列出：

-   不应复制的已有数学单测

-   不应复制的schema单测

-   不应复制的browser矩阵

-   可复用的fixtures

-   可复用的helpers

-   可复用的API clien


## 5. Selected Closure Strategy

说明：

-   backend closure tests:

-   frontend closure tests:

-   browser closure tests:

-   fixtures:

-   CI entry:

-   evidence:

-   runtime target:


## 6. Planned Files

列出预计新增或修改：

-   backend tests

-   frontend tests

-   e2e tests

-   fixtures

-   scripts

-   CI

-   evidence

-   docs

-   persisten


审计后直接继续执行。

----------

# 6. Closure Test Architecture

建议建立三层closure pack。

## 6.1 Backend/Product Integration

建议路径：

```tex
tests/integration/test_phase10_product_closure.py
tests/integration/test_phase10_registry_planner_runtime.py
tests/integration/test_phase10_artifact_contracts.py



如果仓库已有更合适目录，遵循现有结构。

## 6.2 Frontend Product Composition

建议路径：

```tex
apps/web/src/__tests__/phase10ProductClosure.test.tsx



或现有测试目录的等价位置。

## 6.3 Browser Product Smoke

建议路径：

```tex
apps/web/e2e/phase10-product-closure.spec.ts



或当前Playwright目录的等价位置。

不得为了满足文件数量机械创建三个文件。

如果现有架构更适合集中为一个backend文件和一个browser文件，可以调整，但必须覆盖三层语义。

----------

# 7. Cross-Phase Invariant Matrix

新增机器可读或文档化matrix。

至少覆盖：

Invarian

Producer

Validator

Runtime

Frontend

Browser

Tool ID唯一

Registry

Registry tests

Planner

Tool entry

Discovery

Default scene为v2

Adapter

Scene validator

Artifact store

Renderer

Product path

Legacy非默认

Compatibility layer

Schema gate

Runtime

JSON-only

Legacy case

Periodic identity稳定

Scene mapper

Validator

Artifac

Inspector

Picking

Canonical bonds稳定

Adapter

Bond validator

Artifac

Renderer

Measuremen

Security iner

Producer

Manifest validator

Runtime

Preview

Network audi

Caps生效

Validator

PlanValidator

Runtime

Fallback

Over-budge

Deterministic replay

Adapter

Hash validation

Runtime

State replay

Reopen

Capability真实

Registry

Planner tests

Runtime

Product UI

Product evidence

matrix不得仅作为文档存在；关键项必须由closure tests真实断言。

----------

# 8. Registry → Planner → Runtime → Artifact闭环

必须增加正式闭环测试。

测试路径必须真实经过：

```tex
Tool Registry
→ planner tool catalog
→ PlanValidator
→ service-backed execution runtime
→ adapter
→ scene/manifest generation
→ artifact validation
→ artifact persistence/retrieval



至少覆盖一个正式viewer请求：

```tex
Show this periodic crystal in 3D and allow bond inspection.



不得直接调用adapter函数作为唯一证据。

必须断言：

-   selected tool为`structure.viewer_3d

-   tool只注册一次

-   plan validation通过

-   runtime调用正式adapter

-   scene schema为v2

-   manifest schema为current v2

-   artifacts iner

-   no external URL

-   no executable assets

-   result status正确

-   artifact retrieval成功


----------

# 9. Phase 10 Adapter Portfolio Closure

Phase 10不仅包含viewer。

必须挑选少量代表性adapter验证正式执行路径。

至少覆盖：

## Table / Visualization

从已正式完成的能力中选取代表：

-   `table.distribution_summary

-   `viz.scatter`或`viz.histogram


## Composition

至少一个composition adapter：

-   `composition.summary

-   或当前正式注册的等价tool


## Lightweight Structure

至少一个：

-   `structure.summary

-   `structure.lattice_summary

-   `structure.spacegroup_summary


## Static Physics

至少一个或两个：

-   `structure.coordination_his

-   `structure.xrd

-   `structure.rdf


## Viewer

-   `structure.viewer_3d


要求：

-   不需要重测全部算法细节

-   只验证registry、routing、runtime、artifact、preview基本闭环

-   static physics继续遵守candidate/official PASS语义

-   不得把candidate expected values写成官方认证结果


----------

# 10. Artifact Contract Closure

必须验证Phase 10主要artifact类型。

至少包括：

-   table summary artifac

-   visualization artifac

-   composition artifac

-   structure summary artifac

-   static physics artifac

-   viewer scene v2

-   viewer manifest v2

-   measurement artifac

-   supercell state artifac

-   export manifest，若Phase 10F-26已READY


每类至少断言：

-   schema version

-   media type

-   deterministic serialization

-   provenance

-   warning ordering

-   security metadata

-   no JS

-   no external URL

-   size/cap policy

-   preview compatibility


不需要复制每个schema validator的全部边界测试。

----------

# 11. Viewer Product Composition Tes

必须加入一个高价值组合测试，至少执行：

```tex
valid triclinic periodic scene
→ render
→ inspect periodic atom
→ select cross-boundary bond
→ measure distance
→ apply bounded supercell
→ select copied instance
→ apply clipping
→ switch camera prese
→ export viewer state/PNG package



测试必须断言：

-   periodic identity未丢失

-   canonical siteIndex未改变

-   imageOffset正确

-   bond canonical key稳定

-   measurement值稳定

-   supercell仅改变display state

-   clipping不改变topology

-   camera不改变scientific data

-   export state与applied viewer state一致

-   no duplicate canvas/contex

-   no resource leak

-   no external network


不要求每个browser都执行完整长链路。

完整链路可在Chromium执行，Firefox/WebKit运行精简smoke。

----------

# 12. Legacy and Compatibility Closure

必须覆盖：

## Phase 10D Legacy

断言：

-   accepted only throughlegacy compatibility path

-   read-only

-   JSON-only

-   no production renderer

-   no new generation

-   not planner defaul

-   not current schema


## Canonical v1

断言：

-   supported legacy same-cell only

-   no periodic topology claim

-   no fake image offsets

-   not default producer outpu


## Current v2

断言：

-   planner/runtime defaul

-   periodic topology enabled

-   renderer eligible

-   product UI curren


必须防止未来代码将legacy重新提升为默认。

----------

# 13. Capability Truth Closure

必须断言正式capability与真实实现一致。

至少检查：

```tex
periodic_structure: true
periodic_bonds: true
cross_boundary_bonds: true
picking: true
measurement: true
supercell: true
clipping: true
camera_presets: true



export按Phase 10F-26真实结论。

以下必须为false或NOT_READY：

```tex
trajectory
phonon
Brillouin zone
volumetric
editing



必须加入negative planner tests：

-   trajectory request不由viewer伪完成

-   phonon request不由viewer伪完成

-   volumetric request不由viewer伪完成

-   editing request不由viewer伪完成


----------

# 14. Deterministic Replay Closure

选择少量稳定fixtures进行两次或多次重放。

必须验证：

-   selected tool相同

-   plan结构相同或语义等价

-   artifact schema相同

-   scene ordering相同

-   periodic identity ordering相同

-   bond ordering相同

-   warning ordering相同

-   manifest artifact order相同

-   stable JSON hash相同


PNG二进制hash可能受browser实现影响。

如果PNG hash不稳定：

-   验证dimensions

-   viewer state

-   camera

-   scene identity

-   semantic image evidence

-   不将跨浏览器PNG hash一致作为PASS要求


----------

# 15. Failure and Fallback Closure

至少覆盖：

## Invalid Inpu

-   malformed lattice

-   nonfinite coordinates

-   typed sanitized failure

-   no renderer initialization


## Degraded

-   valid artifac

-   degraded warning

-   renderer仍可用

-   scientific data不变


## Over-Budge

-   valid artifact或test-owned synthetic complexity

-   no renderer/canvas/context allocation

-   JSON-only fallback

-   job不被误标为scientific failure


## Context Loss

-   fallback可访问

-   retry/rebuild按现有policy

-   no duplicate canvas/contex


## Unsupported Capability

-   typed rejection

-   no silent ignore


----------

# 16. Security Closure

必须加入跨阶段security regression。

断言：

-   no artifact JavaScrip

-   no artifact HTML execution

-   no shader payload

-   no module payload

-   no callback payload

-   no external URL

-   no remote texture

-   no remote fon

-   no CDN

-   no iframe

-   no eval

-   no Function constructor

-   no notebook execution

-   no script execution

-   no registry bypass

-   no planner bypass

-   no validator bypass

-   no artifact-controlled caps

-   no capability overclaim

-   no telemetry upload

-   no secrets

-   no private paths


必须保留或生成：

```tex
NO_EXTERNAL_NETWORK_REQUESTS
NO_SECRET_PATTERN_HITS



----------

# 17. Lifecycle Closure

必须运行一个bounded lifecycle组合。

推荐序列：

```tex
structure summary
→ static physics artifac
→ viewer v2
→ supercell apply
→ measuremen
→ clipping
→ expor
→ invalid scene
→ legacy JSON-only
→ viewer v2



重复合理次数。

断言：

-   no stale artifac

-   no stale selection

-   no stale measuremen

-   no duplicate canvas

-   no duplicate contex

-   no monotonic geometry/material growth

-   active loops归零

-   listeners/observers清理

-   object URLs释放


不得使用过长stress导致CI不稳定。

----------

# 18. Frontend Closure Tests

至少覆盖：

-   formal tool title

-   tool ID/capabilities

-   loading/success/warning/error

-   v2 renderer

-   JSON fallback

-   legacy banner

-   degraded warning

-   over-budget message

-   inspector

-   measuremen

-   supercell

-   clipping/camera

-   export controls

-   accessibility semantics

-   no capability overclaim


重点测试跨组件组合，不重复全部细节单测。

----------

# 19. Browser Closure Tests

## Chromium Full Closure

至少覆盖：

-   tool discovery

-   planner reques

-   job execution

-   artifact resul

-   renderer

-   inspector

-   measuremen

-   supercell

-   clipping

-   camera prese

-   expor

-   degraded/refused

-   legacy fallback

-   lifecycle switch

-   console/network audi


## Firefox Smoke

覆盖：

-   product entry

-   v2 renderer

-   measuremen

-   fallback

-   no console/network error


## WebKit Smoke

覆盖：

-   product entry

-   renderer

-   mobile-compatible controls

-   export或fallback

-   no console/network error


## Mobile Smoke

覆盖：

-   viewer entry

-   touch controls

-   inspector

-   bounded supercell

-   one distance measuremen

-   fallback

-   no scroll trap

-   no duplicate canvas/contex


closure pack不需要重新运行每个Phase的全部browser case。

----------

# 20. Test Fixture Policy

使用少量、deterministic、bounded fixtures。

推荐：

## Fixture A：Minimal Orthogonal

用于：

-   registry/runtime smoke

-   preview

-   legacy/current comparison


## Fixture B：Triclinic Cross-Boundary

用于：

-   periodic identity

-   bonds

-   measuremen

-   clipping

-   expor


## Fixture C：Self-Periodic

用于：

-   self-periodic topology

-   inspector


## Fixture D：Degraded

使用compact generator或complexity input。

## Fixture E：Over-Budge

必须在allocation前拒绝。

不得：

-   提交巨大scene

-   复制历史fixture内容

-   通过随机生成导致不稳定

-   访问外网


----------

# 21. Closure Evidence

新增：

```tex
docs/phase10/evidence/phase10_closure_regression_pack/



如果项目使用其他Phase 10目录约定，遵循现有结构。

至少包含：

```tex
README.md
test_inventory.json
cross_phase_invariant_matrix.json
tool_portfolio_results.json
registry_planner_runtime_closure.json
artifact_contract_closure.json
viewer_product_composition.json
legacy_compatibility_closure.json
capability_truth.json
deterministic_replay.json
failure_fallback_matrix.json
lifecycle_closure.json
browser_matrix.json
mobile_smoke.json
security_audit.json
network_audit.json
artifact_hashes.json



截图建议：

```tex
01_phase10_tool_discovery.png
02_viewer_product_result.png
03_triclinic_periodic_inspection.png
04_measurement_supercell_clipping.png
05_export_result.png
06_degraded_mode.png
07_over_budget_fallback.png
08_legacy_json_only.png
09_mobile_smoke.png



不得保存：

-   巨大原始artifacts

-   browser cache

-   trace dump

-   private path

-   token

-   secre

-   remote URL

-   crash dump


----------

# 22. CI Entry

Closure pack必须有明确、稳定的执行入口。

推荐新增脚本或命令：

```bash
uv run python -m pytest -q tests/integration/test_phase10_product_closure.py



以及：

```bash
npm --prefix apps/web test -- phase10ProductClosure



browser：

```bash
npm --prefix apps/web run test:e2e -- phase10-product-closure



具体命令按真实package scripts调整。

建议增加统一入口：

```tex
phase10-closure



例如：

```bash
scripts/test_phase10_closure.sh



或package/task runner中的等价命令。

要求：

-   本地可运行

-   CI可运行

-   失败返回非零

-   不吞掉skips

-   不依赖外网

-   不依赖手工环境

-   不执行部署

-   不执行push


----------

# 23. CI策略

优先将closure pack接入现有required CI，而不是新增大量独立job。

建议：

## Unit/Integration Job

运行：

-   backend closure

-   frontend closure


## Browser Job

运行：

-   Chromium full closure

-   Firefox/WebKit smoke，按当前CI矩阵

-   mobile smoke


如果browser矩阵已存在：

-   将closure spec加入现有runner

-   不重复安装浏览器

-   不复制CI workflow


必须保持：

-   service-backed integration

-   no-skipped assertion

-   secret scan

-   network audi


----------

# 24. Test Runtime Budge

Closure pack应精简。

目标不是绝对毫秒限制，而是：

-   backend closure case数量有限

-   frontend组合测试有限

-   Chromium一个完整长链路

-   Firefox/WebKit精简smoke

-   fixtures小

-   不重复历史数学边界测试

-   不重复完整browser evidence pack


必须记录：

-   backend closure duration

-   frontend closure duration

-   browser closure duration

-   total incremental CI duration


如果增量明显过大，必须优化重复setup。

----------

# 25. Documentation

新增：

```tex
docs/phase10/phase10_closure_regression_pack.md
docs/phase10/phase10_cross_phase_invariants.md
docs/phase10/phase10_closure_test_inventory.md
docs/phase10/phase10_closure_ci_contract.md
docs/phase10/phase10_closure_security.md
docs/phase10/phase10_final_readiness_matrix.md



按项目现有目录调整。

更新：

```tex
docs/index.md
persistent/DESIGN_PROGRESS.md
persistent/TASK_BOARD.md
persistent/CHANGELOG.md
persistent/OPEN_QUESTIONS.md
persistent/ARCHITECTURE_DECISIONS.md



必须记录：

-   closure pack定位

-   与历史测试的关系

-   复用策略

-   跨阶段不变量

-   CI入口

-   runtime预算

-   known limitations

-   Phase 10最终ready范围

-   Phase 10G尚未开始实现


----------

# 26. Phase 10 Final Readiness Matrix

必须对Phase 10整体能力进行最终判断。

至少包括：

## Data / Table

-   table adapters

-   visualization adapters

-   composition adapters


## Structure

-   lightweight structure adapters

-   static physics adapters

-   viewer scene contrac

-   periodic topology


## Viewer Produc

-   formal tool registration

-   renderer

-   inspector

-   picking

-   measuremen

-   supercell

-   clipping

-   camera

-   expor

-   accessibility

-   mobile

-   performance

-   browser matrix


## Platform

-   registry

-   planner

-   PlanValidator

-   runtime

-   artifact validation

-   service-backed integration

-   deterministic replay

-   security

-   CI


## Deferred

-   Brillouin zone

-   phonon

-   trajectory

-   volumetric

-   defects

-   surfaces

-   slabs

-   structure editing

-   Phase 11 official benchmark closure


推荐最终状态：

```tex
Phase 10 adapter portfolio: READY
Phase 10 structure analysis: READY
Phase 10 static physics foundation: READY
Phase 10 viewer scene v2: READY
structure.viewer_3d product: READY
Phase 10 product path: READY
Phase 10 closure regression pack: READY
Phase 10 security closure: READY
Phase 10 CI regression protection: READY

Brillouin zone: NOT_READY
phonon: NOT_READY
trajectory: NOT_READY
volumetric: NOT_READY
defects/surfaces/slabs: NOT_READY
structure editing: NOT_READY
Phase 11 official benchmark closure: NOT_READY



----------

# 27. Checks

至少运行：

```bash
git diff --check
uv lock --check

uv run python -m pytest -q

npm --prefix apps/web tes
npm --prefix apps/web run typecheck
npm --prefix apps/web run build



并运行：

-   Phase 10 backend closure entry

-   Phase 10 frontend closure entry

-   Phase 10 browser closure entry

-   Chromium full closure

-   Firefox smoke

-   WebKit smoke

-   mobile smoke

-   registry tests

-   planner tests

-   PlanValidator tests

-   artifact contract tests

-   service-backed integration

-   no-skipped assertion

-   secret scan

-   network audi


必须如实记录：

-   passed

-   failed

-   skipped

-   unavailable


不得把skipped写成passed。

----------

# 28. Commit / CI

完成实现、tests、evidence和docs后：

```bash
git status --shor
git diff --sta
git add <only Phase 10 Closure Regression Pack related files>
git commit -m "Add Phase 10 closure regression pack"
git push origin master



等待current HEAD CI。

必须确认：

-   backend unit success

-   frontend tests success

-   frontend typecheck success

-   frontend build success

-   closure tests success

-   browser closure success

-   service-backed integration success

-   no-skipped assertion success

-   origin/master matches HEAD

-   git status clean


不得伪造CI结果。

----------

# 29. 最终报告格式

完成后输出：

# Phase 10 Closure Regression Pack Resul

## 1. Conclusion

PASS / PARTIAL_PASS / FAIL

## 2. Baseline

-   Phase 10F-27 assumed complete:

-   branch:

-   initial status:

-   final HEAD:

-   final status:


## 3. Existing Test Inventory

-   Phase 10A:

-   Phase 10B:

-   Phase 10C:

-   Phase 10D:

-   Phase 10E:

-   Phase 10F:

-   registry/planner:

-   service-backed:

-   browser:

-   reused assets:


## 4. Closure Architecture

-   backend:

-   frontend:

-   browser:

-   fixtures:

-   unified entry:

-   CI integration:


## 5. Cross-Phase Invariants

-   formal tool ID:

-   default v2:

-   legacy non-default:

-   periodic identity:

-   canonical bonds:

-   artifact security:

-   caps:

-   deterministic replay:

-   capability truth:


## 6. Adapter Portfolio Closure

-   table:

-   visualization:

-   composition:

-   lightweight structure:

-   static physics:

-   viewer:

-   runtime paths:


## 7. Registry / Planner / Runtime

-   registry:

-   planner discovery:

-   planner routing:

-   PlanValidator:

-   service-backed runtime:

-   adapter:

-   artifact store:

-   retrieval:


## 8. Artifact Contract Closure

-   table artifacts:

-   visualization artifacts:

-   composition artifacts:

-   structure artifacts:

-   static physics artifacts:

-   viewer scene:

-   manifest:

-   measurement:

-   supercell:

-   export:

-   security:


## 9. Viewer Product Composition

-   renderer:

-   periodic inspection:

-   bond selection:

-   measurement:

-   supercell:

-   clipping:

-   camera:

-   export:

-   identity preservation:

-   topology preservation:


## 10. Compatibility

-   Phase 10D legacy:

-   canonical v1:

-   current v2:

-   planner default:

-   renderer eligibility:

-   fake topology prevention:


## 11. Capability Truth

-   periodic:

-   picking:

-   measurement:

-   supercell:

-   clipping:

-   export:

-   trajectory:

-   phonon:

-   Brillouin:

-   volumetric:

-   editing:


## 12. Determinism

-   planner:

-   scene:

-   bond ordering:

-   warning ordering:

-   manifest ordering:

-   JSON hashes:

-   PNG policy:


## 13. Failure / Fallback

-   invalid input:

-   degraded:

-   over-budget:

-   context loss:

-   unsupported capability:

-   JSON fallback:


## 14. Lifecycle

-   sequence:

-   repetitions:

-   stale state:

-   canvas:

-   context:

-   geometries:

-   materials:

-   loops:

-   object URLs:


## 15. Browser Closure

-   Chromium:

-   Firefox:

-   WebKit:

-   mobile:

-   console:

-   network:


## 16. Security

-   registry bypass:

-   planner bypass:

-   validator bypass:

-   artifact JS:

-   external assets:

-   executable content:

-   capability overclaim:

-   secrets:

-   network:

-   markers:


## 17. Runtime Budge

-   backend closure:

-   frontend closure:

-   browser closure:

-   incremental CI:

-   duplication avoided:


## 18. Evidence

-   directory:

-   inventory:

-   invariant matrix:

-   product closure:

-   compatibility:

-   determinism:

-   lifecycle:

-   browser:

-   security:

-   screenshots:


## 19. Tests

-   backend closure:

-   frontend closure:

-   Chromium:

-   Firefox:

-   WebKit:

-   mobile:

-   backend full:

-   frontend full:

-   typecheck:

-   build:

-   service-backed:

-   no-skipped:

-   lock:

-   diff:


## 20. Files

-   backend tests:

-   frontend tests:

-   browser tests:

-   fixtures:

-   scripts:

-   CI:

-   evidence:

-   docs:

-   persistent:

-   dependencies/lockfile:


## 21. Deferred

明确列出：

-   Brillouin zone

-   phonon

-   trajectory

-   volumetric

-   defects

-   surfaces

-   slabs

-   structure editing

-   Phase 11 official benchmarks

-   production scale/load testing，若尚未完成

-   any unavailable browser environmen


## 22. Final Phase 10 Readiness

-   adapter portfolio:

-   structure analysis:

-   static physics:

-   viewer scene:

-   `structure.viewer_3d`:

-   registry/planner/runtime:

-   artifact contracts:

-   browser product path:

-   security:

-   closure regression pack:

-   Phase 10 overall:


## 23. Commit / CI

-   commit:

-   HEAD:

-   CI run:

-   unit:

-   frontend:

-   closure:

-   browser:

-   service-backed:

-   no-skipped:

-   origin:

-   status:


## 24. Whether Phase 10 is formally closed

YES / NO

## 25. Whether allowed to enter next phase

允许 / 不允许

下一阶段：

```tex
Phase 10G：Brillouin Zone Planning and Contrac



下一阶段只做planning、contract、numeric policy、fixture/evidence strategy和security边界，不直接实现Brillouin zone renderer。

----------

# 30. PASS 判定

PASS必须满足：

-   新增真实可执行closure tests

-   没有复制全部历史单测

-   有清晰的cross-phase invariant matrix

-   Registry → Planner → Validator → Runtime → Artifact正式闭环被测试

-   至少覆盖代表性table/composition/structure/static physics/viewer tools

-   viewer组合链路真实执行

-   default output为v2

-   legacy不成为默认

-   periodic identity不丢失

-   canonical topology不改变

-   measurement/supercell/clipping/export组合正确

-   capability metadata真实

-   deterministic replay闭合

-   invalid/degraded/over-budget/fallback闭合

-   lifecycle无单调资源增长

-   Chromium完整closure通过

-   Firefox/WebKit/mobile smoke通过或按既有CI真实记录

-   no external network

-   no artifact JS

-   no secret hits

-   closure pack有独立执行入口

-   closure pack接入CI

-   service-backed integration通过

-   no-skipped assertion通过

-   full test suite不回退

-   CI通过

-   git clean

-   Phase 10 overall标记READY


PARTIAL_PASS仅允许：

-   某非主要browser环境在当前CI不可用，但其测试保留且标记unavailable

-   PNG跨browser二进制hash不一致，但语义一致

-   npm audit因既有registry问题不可用

-   某个非核心closure case因明确环境限制无法自动执行，但正式产品主链路完整


FAIL包括：

-   只有docs，没有新增测试

-   只是把已有测试聚合运行，没有新增跨阶段断言

-   closure tests直接调用adapter绕过正式runtime

-   browser tests使用fixture绕过正式产品路径

-   legacy重新成为默认

-   v2 periodic identity回退

-   capability过度宣称

-   over-budget仍初始化renderer

-   skipped被写成passed

-   closure pack未接入CI

-   引入新功能导致范围膨胀

-   无security closure

-   无browser closure

-   CI失败却声明PASS

完成时间：2026-07-13 18:38:54 +08:00

修改文件：

- `tests/integration/test_phase10_product_closure.py`、`tests/test_phase10f27_formal_viewer_product.py`
- `apps/web/app/components/viewer-scene/phase10ProductClosure.test.ts`
- `apps/web/test/phase10-product-closure-browser-evidence.mjs`、`phase10-closure-evidence-check.mjs`、`generate-phase10-closure-evidence.py`
- `scripts/test_phase10_closure.ps1`、`apps/web/package.json`、`.github/workflows/ci.yml`
- `docs/phase10/*.md`、`docs/phase10/evidence/phase10_closure_regression_pack/`、`docs/index.md`
- `services/llm/mdi_llm/providers.py`、相关 `persistent/*.md`

修改摘要：

- 新增 6-tool registry→planner→PlanValidator→runtime→artifact closure，并加入 PostgreSQL/Redis/MinIO service-backed formal viewer case。
- 新增 frontend v2/periodic/supercell/measurement/clipping/export/legacy/refused composition closure。
- 新增 Chromium full、Firefox/WebKit/mobile smoke、console/network/lifecycle/fallback/security evidence 和跨平台 SHA-256 integrity gate。
- 修复任务指定 `Show this periodic crystal in 3D and allow bond inspection` 被 preview metadata 抢占的 route precedence。
- 将 backend/frontend/evidence integrity 和 service-backed 20-pass/0-skip gate 接入 required CI；无 dependency、schema、adapter、runtime 或 renderer feature 变更。

测试结果：

- backend closure：`2 passed, 1 deselected`；精确 registry/planner/PlanValidator/artifact/compatibility 组：`72 passed, 1 deselected`。
- frontend closure：`2 passed`；frontend full：`106 passed`；typecheck/build 通过。
- backend full：`372 passed, 22 skipped, 11 warnings`；本地额外 skip 为 Docker 不可用的 service-backed closure。
- browser closure entry：Chromium 150、Firefox 128、WebKit 18 和 mobile PASS；console/page errors `0`；external requests `0`。
- `PHASE10_CLOSURE_EVIDENCE_PASS`、`PHASE10_PRODUCT_CLOSURE_BROWSER_PASS`、`PHASE10_CLOSURE_EVIDENCE_INTEGRITY_PASS`、`NO_EXTERNAL_NETWORK_REQUESTS`、`NO_SECRET_PATTERN_HITS`。
- `npm audit` 因配置 registry 不实现 audit endpoint而 unavailable；dependency/lockfile unchanged。
- 主提交：`589ddca02ac039b2de6456b5c7ca49d92e026f2c Add Phase 10 closure regression pack`。
- CI `29243052704` 因 Windows CRLF hash 与 Linux LF 不一致失败；`69b93a7` 改为 canonical LF text hashing。
- CI `29243222153` 因 hash inventory 包含被 gitignore 排除的重复 artifact copies 失败；`5230105` 删除重复 raw copies。
- 最终 current-HEAD CI `29243395743`：unit、Phase 10 backend/frontend closure、evidence integrity、typecheck/build、service-backed integration、20-pass/0-skip 全部 success。
---END---

---TASK---
 状态：待处理
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
