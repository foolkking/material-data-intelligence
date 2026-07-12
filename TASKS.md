---TASK---  
状态：已完成

 # Phase 10F-21：Viewer Performance Hardening

进入 Phase 10F-21：Viewer Performance Hardening。

可以默认：

-   Phase 10F-20 已完成
    
-   historical viewer schema compatibility、deprecation 和 renderer gate 已收口
    
-   当前 production viewer scene schema 为 `phase10f18.viewer_scene.v2`
    
-   当前 production manifest 为 Phase 10F-19/10F-20 确认的 v2 manifest
    
-   current adapters 默认生成 v2
    
-   Phase 10D legacy schema 为 read-only / JSON-only compatibility
    
-   canonical v1 仅保留 same-cell compatibility
    
-   v2 是当前 periodic topology renderer contract
    
-   periodic endpoint identity、canonical periodic bonds、neighbor inspector、cross-boundary topology 已稳定
    
-   当前 branch、HEAD、working tree 和 Phase 10F-20 CI 均可视为正确且 clean
    

本阶段不需要重复 baseline 检查。

本阶段的主要任务是：

> 将现有 periodic crystal renderer 从“功能正确、bounded、具备基础证据”提升为“性能行为可量化、资源使用有上限、大型 scene 可降级、生命周期稳定、重复切换不泄漏”的 viewer foundation。

本阶段仍然不是功能扩展阶段。

不要进入 trajectory、phonon、Brillouin zone、volumetric、defects、surfaces、slabs、structure editing 或正式 full product registration。

----------

# 1. 当前已知能力

开始前应完整理解当前已有实现，但不要重新验证 Phase 10F-20 baseline。

当前 viewer 已具备：

-   `viewer_scene.v2`
    
-   periodic site identity
    
-   endpoint image offsets
    
-   canonical periodic bond topology
    
-   same-cell bonds
    
-   cross-boundary bonds
    
-   self-periodic bonds
    
-   triclinic periodic bonds
    
-   periodic neighbor inspector
    
-   real Three.js renderer
    
-   atom rendering
    
-   lattice rendering
    
-   bond rendering
    
-   camera controls
    
-   rotate / zoom / pan / reset
    
-   WebGL fallback
    
-   context-loss handling基础
    
-   JSON-only preview fallback
    
-   renderer lifecycle cleanup基础
    
-   browser evidence
    
-   mobile evidence基础
    
-   bounded scene contracts
    
-   bounded canonical bonds
    
-   compatibility gate
    
-   no artifact JS
    
-   no external resources
    
-   no remote assets
    

当前尚未充分证明：

-   大型 structure 的 CPU/GPU表现
    
-   大型 supercell display 的资源行为
    
-   atom instancing是否已达到稳定可接受状态
    
-   bond batching是否已达到稳定可接受状态
    
-   draw call预算是否明确
    
-   geometry/material是否充分复用
    
-   scene切换是否无泄漏
    
-   mount/unmount重复执行是否稳定
    
-   WebGL context恢复是否可靠
    
-   renderer cancellation是否存在
    
-   stale render是否可能覆盖新scene
    
-   large-scene fallback是否明确
    
-   mobile GPU资源是否有保护
    
-   performance metrics是否可审计
    
-   build bundle是否持续受控
    
-   performance regression是否进入测试
    

----------

# 2. 本阶段目标

必须完成以下六类工作：

1.  **性能架构审计**
    
2.  **render path性能优化**
    
3.  **大型 scene资源限制与降级**
    
4.  **生命周期、取消和资源释放**
    
5.  **性能测试与浏览器证据**
    
6.  **性能 contract、文档和 readiness收口**
    

本阶段必须产生实际实现性代码。

如果最终主要变更只有 docs、readiness matrix 或 benchmark说明，本阶段必须判定为 FAIL。

----------

# 3. 严格禁止范围

本阶段不得实现：

-   trajectory
    
-   trajectory playback
    
-   trajectory frame contract
    
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
    
-   PNG export
    
-   PDF export
    
-   glTF/GLB export
    
-   advanced measurement
    
-   multi-selection
    
-   clipping planes
    
-   production auth
    
-   external API
    
-   notebook execution
    
-   script execution
    
-   real LLM
    

不得：

-   修改 periodic endpoint identity
    
-   修改 canonical periodic bond key
    
-   修改 v2 schema topology semantics
    
-   修改 `1e-5 Å` bond distance tolerance
    
-   放宽 validator caps
    
-   放宽 PlanValidator
    
-   修改 QueueWorkerRuntime 主语义
    
-   修改 AnalysisPlanRepository 主语义
    
-   修改 `/planner/jobs` 主语义
    
-   引入未经批准的新 renderer framework
    
-   替换 Three.js
    
-   引入 Babylon.js
    
-   引入 deck.gl
    
-   引入 WebGPU
    
-   引入 WASM renderer
    
-   引入 remote assets
    
-   引入 CDN
    
-   引入 shader payloads from artifact
    
-   执行 artifact JavaScript
    
-   允许 artifact控制 shader、module、URL或callback
    
-   以删除功能的方式伪造性能通过
    
-   通过关闭 periodic bonds来掩盖性能问题
    
-   通过不渲染大 scene却标记成功来伪造 evidence
    
-   在没有测量的情况下声称性能改善
    
-   把浏览器 crash、context loss 或 timeout视为 PASS
    

允许：

-   refactor renderer internals
    
-   atom instancing优化
    
-   bond batching优化
    
-   geometry/material复用
    
-   render scheduling
    
-   cancellation
    
-   cleanup
    
-   performance metrics
    
-   resource budgets
    
-   safe fallback
    
-   bounded large-scene policy
    
-   test-only benchmark fixtures
    
-   browser evidence
    
-   docs
    
-   persistent updates
    

----------

# 4. 必读实现

开始后直接阅读当前真实代码，不做 baseline检查。

重点定位并阅读：

## 4.1 Renderer

搜索：

```bash
rg -n "Three|WebGLRenderer|InstancedMesh|LineSegments|BufferGeometry|Material|viewer_scene" apps/web

```

重点确认：

-   renderer component
    
-   renderer mapper
    
-   scene construction
    
-   atom mesh construction
    
-   bond geometry construction
    
-   lattice geometry
    
-   camera controls
    
-   resize handling
    
-   requestAnimationFrame使用
    
-   cleanup/dispose逻辑
    
-   context loss handling
    
-   fallback UI
    
-   inspector integration
    

## 4.2 Contract / Validator

阅读：

-   `viewer_scene.v2` validator
    
-   manifest validator
    
-   periodic bond canonicalization
    
-   caps
    
-   scene size restrictions
    
-   atom/bond hard limits
    
-   cell expansion limits
    
-   JSON byte limits
    

## 4.3 Existing tests / evidence

定位：

-   Phase 10F-13 renderer tests
    
-   Phase 10F-17 periodic inspection tests
    
-   Phase 10F-18 periodic bond tests
    
-   Phase 10F-19 integration tests
    
-   Phase 10F-20 compatibility tests
    
-   browser evidence runners
    
-   mobile runner
    
-   performance snapshots
    
-   renderer metrics captures
    

## 4.4 Frontend lifecycle

检查：

-   React mount/unmount
    
-   effect dependencies
    
-   artifact切换
    
-   scene切换
    
-   job切换
    
-   tab切换
    
-   preview/render mode切换
    
-   window resize
    
-   hidden tab
    
-   component disposal
    

----------

# 5. 修改前输出性能审计

修改代码前输出：

# Phase 10F-21 Viewer Performance Pre-Implementation Audit

## 1. Current Renderer Architecture

-   renderer component:
    
-   scene builder:
    
-   atom implementation:
    
-   bond implementation:
    
-   lattice implementation:
    
-   camera controls:
    
-   resize:
    
-   animation loop:
    
-   cleanup:
    
-   context loss:
    
-   fallback:
    

## 2. Current Resource Model

-   atoms:
    
-   bonds:
    
-   geometries:
    
-   materials:
    
-   draw calls:
    
-   WebGL contexts:
    
-   canvases:
    
-   animation frames:
    
-   event listeners:
    
-   observers:
    
-   object disposal:
    

## 3. Current Caps

-   canonical sites:
    
-   displayed atom instances:
    
-   canonical bonds:
    
-   displayed bonds:
    
-   cell expansion:
    
-   JSON bytes:
    
-   viewport limits:
    
-   any missing caps:
    

## 4. Current Performance Risks

至少检查并列出：

-   one mesh per atom risk
    
-   one mesh per bond risk
    
-   geometry duplication
    
-   material duplication
    
-   per-frame allocation
    
-   repeated scene rebuild
    
-   unnecessary animation loop
    
-   duplicate event listeners
    
-   unbounded ResizeObserver
    
-   unbounded raycasting
    
-   stale async render
    
-   context leak
    
-   canvas leak
    
-   GPU resource leak
    
-   mobile memory pressure
    
-   large triclinic supercell
    
-   large bond topology
    
-   inspector coupling
    

## 5. Selected Optimization Strategy

说明：

-   atoms:
    
-   bonds:
    
-   lattice:
    
-   render scheduling:
    
-   cleanup:
    
-   cancellation:
    
-   large-scene degradation:
    
-   metrics:
    

## 6. Planned Files

列出预计修改或新增：

-   renderer
    
-   helpers
    
-   tests
    
-   browser runner
    
-   fixtures
    
-   evidence
    
-   docs
    
-   persistent
    

审计完成后直接继续执行。

----------

# 6. Performance Budgets

本阶段必须建立明确、application-owned的性能预算。

预算必须以真实代码和当前 contract caps为依据，不得凭空选择过大的数字。

至少定义：

## 6.1 Draw Call Budget

按 scene层级定义：

### Small Scene

建议范围：

-   displayed atoms: ≤ 500
    
-   displayed bonds: ≤ 2,048
    

目标：

-   atom draw calls: ≤ 1 per atom style group
    
-   bond draw calls: ≤ 1
    
-   lattice draw calls: ≤ 1
    
-   selection/highlight draw calls: bounded
    
-   total draw calls: 明确上限
    

### Medium Scene

建议范围：

-   displayed atoms: 501–5,000
    
-   displayed bonds: bounded by contract
    

目标：

-   atom draw calls不随原子数线性增长
    
-   bond draw calls不随bond数线性增长
    
-   total draw calls保持固定或按species/style group bounded
    

### Large Scene

当 scene超出交互安全阈值：

-   不允许浏览器卡死
    
-   不允许无限构建
    
-   必须进入 typed degraded mode 或 safe refusal
    
-   必须明确显示原因和建议
    
-   JSON-only preview仍可用
    

## 6.2 Geometry Budget

必须限制：

-   atom base geometries
    
-   bond geometries
    
-   lattice geometries
    
-   highlight geometries
    
-   temporary geometries
    

要求：

-   geometry count与atom count解耦
    
-   geometry count与bond count解耦
    
-   geometry reuse
    
-   disposal可验证
    

## 6.3 Material Budget

必须限制：

-   atom materials
    
-   bond materials
    
-   lattice materials
    
-   highlight materials
    
-   text/label materials
    

要求：

-   material count按species/style group bounded
    
-   不允许每atom一个material
    
-   不允许每bond一个material
    
-   scene dispose后material count回到基准
    

## 6.4 Memory Budget

不要求得到绝对GPU显存精确值，但必须建立可审计 proxy：

-   object count
    
-   geometry count
    
-   material count
    
-   texture count
    
-   buffer attribute count
    
-   renderer.info.memory
    
-   renderer.info.render
    
-   canvas count
    
-   WebGL context count
    

## 6.5 Time Budget

建立合理的测量项：

-   parse-to-map time
    
-   scene build time
    
-   first render time
    
-   scene switch time
    
-   cleanup time
    
-   repeated switch average
    
-   large-scene fallback decision time
    

不得使用依赖机器绝对性能的过窄阈值。

优先采用：

-   bounded upper threshold
    
-   ratio comparison
    
-   no superlinear growth
    
-   no monotonic leak
    
-   fixed draw-call assertions
    

----------

# 7. Atom Rendering Hardening

## 7.1 Instancing

如果当前 atom rendering不是稳定的 `InstancedMesh`，必须完成或强化。

要求：

-   原子不应一atom一Mesh
    
-   按共享geometry + material grouping
    
-   instance matrix deterministic
    
-   instance index映射到 `PeriodicSiteRef`
    
-   picking保持正确
    
-   highlight保持正确
    
-   inspector identity保持正确
    
-   siteIndex/imageOffset不丢失
    

## 7.2 Grouping Policy

按真实style contract选择：

-   species
    
-   radius
    
-   color
    
-   representation
    

不得让任意用户字段创建无限material groups。

必须有最大style group cap。

超出时：

-   fallback到canonical default style
    
-   输出warning
    
-   不允许无限分组
    

## 7.3 Geometry Reuse

要求：

-   sphere geometry共享
    
-   resolution固定并受应用控制
    
-   不允许artifact指定sphere segments
    
-   不允许artifact指定shader
    
-   不允许artifact创建custom geometry
    
-   atom geometry在scene内复用
    
-   scene dispose时正确释放
    

## 7.4 Instance Updates

当前为静态scene，不需要持续每帧更新。

要求：

-   instance matrix只在scene build时写入
    
-   不启用无意义per-frame update
    
-   `instanceMatrix.needsUpdate`只在必要时设置
    
-   color update同理
    
-   camera movement不触发atom data重建
    

----------

# 8. Bond Rendering Hardening

## 8.1 Shared Line Geometry

优先保持或强化当前 bounded shared `LineSegments`。

要求：

-   不允许每bond一个Line对象
    
-   bond positions写入单一或bounded BufferGeometry
    
-   displayed bonds stable sorted
    
-   canonical bond identity映射不丢失
    
-   cross-boundary bonds正确
    
-   self-periodic bonds正确
    
-   triclinic坐标正确
    

## 8.2 Bond Cap

必须在 renderer mapper之前或过程中再次验证：

-   canonical bond cap
    
-   displayed bond cap
    
-   endpoint visibility
    
-   duplicate suppression
    
-   invalid offset rejection
    

不得信任未经validator确认的artifact。

## 8.3 Bond Highlight

高亮不应导致：

-   重建全部bond geometry
    
-   新建无限material
    
-   每次hover创建新geometry
    
-   event listener泄漏
    

推荐：

-   单独bounded highlight geometry
    
-   或使用有限material/state切换
    

必须测量重复highlight后的资源计数。

----------

# 9. Lattice and Auxiliary Geometry

要求：

-   lattice edge geometry共享或单实例
    
-   不随camera movement重建
    
-   axes/helper数量bounded
    
-   hide/show不重复创建未释放对象
    
-   reset不重建整个scene
    
-   resize不重建scene
    
-   inspector open/close不重建scene
    

----------

# 10. Render Scheduling

## 10.1 避免无意义持续动画循环

当前 viewer如果不是动画场景，不应默认永远运行连续 `requestAnimationFrame`。

优先采用：

-   on-demand rendering
    
-   controls change触发render
    
-   resize触发render
    
-   scene change触发render
    
-   highlight变化触发render
    

如果 Three.js controls机制要求短时更新：

-   只在interaction期间运行
    
-   interaction结束后停止
    
-   不保留永远运行loop
    

## 10.2 Animation Frame Lifecycle

必须：

-   保存request ID
    
-   unmount时cancel
    
-   scene切换时cancel stale render
    
-   context lost时停止
    
-   fallback时停止
    
-   component隐藏时避免不必要render
    
-   不允许多个并行loops
    

新增测试验证：

-   mount后最多一个active loop
    
-   scene切换不增加loop数量
    
-   unmount后loop为零
    

----------

# 11. Scene Build Cancellation and Stale Render Protection

这是本阶段必须实现的重要能力。

场景切换可能发生于：

-   用户选择新artifact
    
-   job切换
    
-   tab切换
    
-   JSON preview切换到renderer
    
-   renderer切换到fallback
    
-   大scene validation失败
    

要求：

-   每次scene build拥有generation token或等价机制
    
-   新scene开始后旧scene结果不得提交
    
-   stale scene必须立即dispose
    
-   stale async task不得覆盖新scene
    
-   stale errors不得污染当前scene
    
-   cancellation不泄漏geometry/material/canvas/context
    

即使scene build当前同步，也应建立安全的generation guard，为后续大scene和trajectory做基础。

----------

# 12. Renderer Lifecycle Hardening

## 12.1 Dispose Policy

必须明确并实现：

-   geometry.dispose()
    
-   material.dispose()
    
-   texture.dispose()，如果存在application-owned texture
    
-   renderer.dispose()
    
-   controls.dispose()
    
-   event listener removal
    
-   ResizeObserver disconnect
    
-   mutation/intersection observer cleanup，若存在
    
-   animation frame cancellation
    
-   canvas removal
    
-   scene references clear
    
-   mapper cache clear
    

## 12.2 Repeated Mount / Unmount

必须增加stress test：

-   mount
    
-   render
    
-   unmount
    

重复至少：

-   20次单元/integration级
    
-   10次真实浏览器级，或仓库合理的bounded次数
    

验证：

-   canvas count不增长
    
-   WebGL context count不增长
    
-   listener count不增长
    
-   animation loops不增长
    
-   geometry/material资源不单调增长
    
-   console无context leak warning
    

## 12.3 Artifact Switching

执行序列：

```text
small scene
→ triclinic scene
→ self-periodic scene
→ medium scene
→ invalid scene
→ legacy JSON-only
→ current v2 scene

```

重复多轮。

验证：

-   current scene正确
    
-   previous resources释放
    
-   no duplicate canvas
    
-   no duplicate renderer
    
-   no stale inspector state
    
-   no stale selection
    
-   no stale bond highlight
    

----------

# 13. WebGL Context Loss and Recovery

现有context loss基础必须强化。

要求：

## Context Lost

-   prevent default按当前最佳实践处理
    
-   停止render loop
    
-   停止scene updates
    
-   显示明确fallback
    
-   不重复创建context
    
-   不创建额外canvas
    
-   JSON-only preview仍可访问
    

## Context Restored

只能选择一种明确策略并记录：

1.  rebuild renderer from current validated scene
    
2.  require user-triggered retry
    

不得出现半恢复状态。

必须测试：

-   loss event
    
-   fallback
    
-   retry/rebuild
    
-   scene identity保持
    
-   no duplicate context
    
-   no duplicate canvas
    
-   no leaked old renderer
    

----------

# 14. Large Scene Policy

必须建立三层或类似层级。

## 14.1 Interactive

符合安全阈值：

-   full current renderer
    
-   atoms
    
-   lattice
    
-   bonds
    
-   picking
    
-   inspector
    

## 14.2 Degraded Interactive

超过推荐阈值但仍在hard cap内：

允许的降级必须明确并透明，例如：

-   降低sphere detail
    
-   禁用默认bond显示但允许用户显式开启
    
-   限制highlight
    
-   默认隐藏labels
    
-   减少辅助geometry
    
-   禁用昂贵hover，只保留click
    
-   inspector仍可使用
    

不得静默改变科学数据。

必须显示warning：

```text
VIEWER_PERFORMANCE_DEGRADED_MODE

```

并列出实际降级项。

## 14.3 JSON-Only / Refused Renderer

超过renderer hard cap：

-   renderer不初始化
    
-   no canvas
    
-   no WebGL context
    
-   JSON-only preview
    
-   typed reason
    
-   scene artifact仍可下载
    
-   不将job标记失败，如果artifact本身有效
    
-   UI明确表示“artifact有效，但当前浏览器交互渲染超出安全预算”
    

建议typed code：

```text
VIEWER_SCENE_RENDER_BUDGET_EXCEEDED

```

不得称为contract invalid。

----------

# 15. Scene Complexity Estimator

实现application-owned complexity estimator。

输入至少包括：

-   canonical site count
    
-   displayed atom instance count
    
-   canonical bond count
    
-   displayed bond count
    
-   species/style group count
    
-   lattice count
    
-   cell expansion
    
-   viewport/device hint，若安全且稳定
    
-   mobile/desktop类别，若已有可靠机制
    

输出：

```json
{
  "mode": "interactive",
  "estimated_draw_calls": 0,
  "estimated_geometries": 0,
  "estimated_materials": 0,
  "displayed_atoms": 0,
  "displayed_bonds": 0,
  "warnings": []
}

```

要求：

-   deterministic
    
-   no user-controlled executable input
    
-   no browser fingerprinting
    
-   no remote benchmark
    
-   no network
    
-   no arbitrary device probing
    
-   mode decision可测试
    
-   与真实renderer metrics对照
    

----------

# 16. Renderer Metrics

新增application-owned metrics collector。

至少记录：

## Scene Metrics

-   schema version
    
-   canonical sites
    
-   displayed atom instances
    
-   canonical bonds
    
-   displayed bonds
    
-   cross-boundary bonds
    
-   self-periodic bonds
    
-   species groups
    
-   mode
    

## Render Metrics

-   draw calls
    
-   triangles
    
-   lines
    
-   points
    
-   geometries
    
-   textures
    
-   materials
    
-   canvas count
    
-   WebGL context count
    
-   active animation loops
    

## Timing Metrics

-   map duration
    
-   scene build duration
    
-   first render duration
    
-   disposal duration
    

指标必须：

-   不含绝对私有路径
    
-   不含artifact原始内容
    
-   不含secret
    
-   不含用户可识别信息
    
-   不发送外网
    
-   只用于本地evidence和debug面板
    
-   production UI默认不泄漏内部敏感信息
    

----------

# 17. Performance Fixtures

新增bounded、deterministic performance fixtures。

至少包含：

## 17.1 Tiny

-   2–4 atoms
    
-   1 periodic bond
    
-   用于基准和regression
    

## 17.2 Small

-   50–100 displayed atoms
    
-   bounded bonds
    
-   multiple species
    

## 17.3 Medium

-   500–1,000 displayed atoms
    
-   bounded periodic bonds
    
-   multiple style groups
    
-   triclinic variant
    

## 17.4 Large-but-Allowed

-   接近degraded threshold
    
-   不应导致浏览器卡死
    
-   应进入明确mode
    

## 17.5 Over-Budget

-   超过renderer budget
    
-   artifact contract仍合法，或通过test-only synthetic complexity input
    
-   renderer拒绝初始化
    
-   JSON-only fallback
    

不得将巨大JSON直接提交进仓库。

优先：

-   fixture generator
    
-   compact base structure + deterministic expansion
    
-   test-time generation
    
-   summary/hash evidence
    

fixture generator不得访问外网。

----------

# 18. Performance Tests

## 18.1 Unit Tests

覆盖：

-   complexity estimator
    
-   mode decision
    
-   draw-call estimate
    
-   geometry/material estimate
    
-   threshold boundaries
    
-   warning ordering
    
-   mobile/desktop policy，若存在
    
-   over-budget typed result
    

## 18.2 Renderer Tests

覆盖：

-   atom instancing
    
-   one base geometry per style group或更优
    
-   bounded materials
    
-   shared bond geometry
    
-   lattice not rebuilt on camera movement
    
-   no scene rebuild on inspector toggle
    
-   no scene rebuild on camera reset
    
-   no per-frame allocations，按可测试方式验证
    
-   on-demand rendering
    
-   one animation loop maximum
    

## 18.3 Lifecycle Tests

覆盖：

-   repeated mount/unmount
    
-   repeated artifact switching
    
-   invalid → valid
    
-   v1 → v2
    
-   JSON-only → renderer
    
-   context lost → fallback
    
-   retry/recovery
    
-   selection/highlight cleanup
    
-   observer/listener cleanup
    
-   no duplicate canvas
    
-   no duplicate context
    

## 18.4 Performance Regression Tests

必须断言：

-   draw calls不随atom count线性增长
    
-   geometry count不随atom count线性增长
    
-   material count不随atom count线性增长
    
-   bond object count不随bond count线性增长
    
-   cleanup后资源恢复至基准
    
-   scene switching无单调资源增长
    

不要使用极易受CI波动影响的毫秒级严格断言。

## 18.5 Existing Regression

必须保持：

-   Phase 10F-17 identity
    
-   Phase 10F-18 periodic topology
    
-   Phase 10F-19 integration
    
-   Phase 10F-20 compatibility
    
-   JSON preview
    
-   neighbor inspector
    
-   renderer fallback
    
-   security
    

----------

# 19. Browser Evidence

新增：

```text
docs/phase10f/evidence/phase10f21_viewer_performance_hardening/

```

必须使用真实浏览器。

至少覆盖：

## 19.1 Chromium

-   tiny scene
    
-   small scene
    
-   medium scene
    
-   degraded scene
    
-   over-budget fallback
    
-   repeated scene switching
    
-   context loss/recovery
    

## 19.2 Firefox

至少：

-   small
    
-   medium
    
-   over-budget fallback
    
-   lifecycle
    

## 19.3 WebKit

至少：

-   small
    
-   medium
    
-   over-budget fallback
    
-   lifecycle
    

## 19.4 Mobile

至少：

-   small scene
    
-   degraded threshold case
    
-   over-budget fallback
    
-   touch/viewport基本稳定性
    
-   no duplicate canvas
    
-   no context leak
    

----------

# 20. Browser Evidence Assertions

每个真实浏览器 evidence必须记录：

-   browser version
    
-   viewport
    
-   device class
    
-   schema
    
-   scene complexity
    
-   selected mode
    
-   displayed atoms
    
-   displayed bonds
    
-   draw calls
    
-   geometries
    
-   materials
    
-   first render result
    
-   console errors
    
-   network requests
    
-   canvas count
    
-   context count
    
-   lifecycle result
    

必须验证：

-   no renderer crash
    
-   no page freeze
    
-   no unbounded canvas
    
-   no duplicate WebGL context
    
-   no unhandled promise rejection
    
-   no stale scene
    
-   no external network
    
-   no artifact JS
    
-   over-budget不创建canvas
    
-   over-budget不创建context
    
-   degraded mode显示warning
    
-   current scene identity正确
    

----------

# 21. Evidence Files

建议至少包含：

```text
README.md
performance_budget.json
complexity_thresholds.json
fixture_manifest.json
tiny_scene_metrics.json
small_scene_metrics.json
medium_scene_metrics.json
degraded_scene_metrics.json
over_budget_result.json
draw_call_regression.json
resource_reuse.json
mount_unmount_stress.json
scene_switch_stress.json
context_loss_recovery.json
browser_matrix.json
mobile_metrics.json
console_audit.json
network_audit.json
security_audit.json
artifact_hashes.json

```

screenshots建议：

```text
01_tiny_scene.png
02_small_scene.png
03_medium_scene.png
04_degraded_mode.png
05_over_budget_json_fallback.png
06_context_lost_fallback.png
07_context_recovered.png
08_mobile_small.png
09_mobile_degraded.png

```

不要保存：

-   巨大原始fixture
    
-   browser cache
    
-   GPU dump
    
-   crash dump
    
-   node_modules
    
-   absolute private path
    
-   secret
    
-   token
    
-   real external URL
    

----------

# 22. Performance Acceptance

必须明确区分：

## Functional Correctness

-   atoms correct
    
-   bonds correct
    
-   lattice correct
    
-   periodic identity correct
    
-   inspector correct
    

## Performance Correctness

-   draw calls bounded
    
-   geometries bounded
    
-   materials bounded
    
-   resource cleanup complete
    
-   no duplicate loops
    
-   no context leak
    
-   safe large-scene behavior
    
-   predictable degraded mode
    
-   predictable refusal mode
    

## Scientific Correctness

性能降级不得改变：

-   site identity
    
-   coordinates
    
-   lattice
    
-   canonical bonds
    
-   periodic offsets
    
-   bond distances
    
-   topology authority
    
-   source/provenance
    

可以改变的仅为显示质量或默认显示策略，并必须明确记录。

----------

# 23. Security

必须验证：

-   no artifact JavaScript
    
-   no artifact HTML
    
-   no artifact shader
    
-   no artifact module
    
-   no artifact callback
    
-   no eval
    
-   no Function constructor
    
-   no external URL
    
-   no remote texture
    
-   no CDN
    
-   no iframe
    
-   no arbitrary file access
    
-   no notebook execution
    
-   no script execution
    
-   no real LLM
    
-   no dependency addition
    
-   no browser fingerprinting
    
-   no performance telemetry upload
    
-   no network benchmark
    
-   no GPU information disclosure beyond bounded local metrics
    
-   over-budget artifact cannot force renderer initialization
    
-   artifact cannot override performance thresholds
    
-   artifact cannot request high sphere segments
    
-   artifact cannot request unbounded materials
    
-   artifact cannot disable safety caps
    

必须输出：

```text
NO_EXTERNAL_NETWORK_REQUESTS
NO_SECRET_PATTERN_HITS

```

----------

# 24. Dependency and Bundle Policy

本阶段默认不新增依赖。

必须检查：

```bash
npm --prefix apps/web ls --depth=0
npm --prefix apps/web run build

```

记录：

-   renderer chunk size
    
-   total relevant chunk size
    
-   change from previous baseline
    
-   no unexpected dependency
    
-   no lockfile drift
    

如果 bundle明显增长，必须解释原因。

不得只为了性能测试引入大型benchmark库。

优先使用：

-   browser performance API
    
-   Three.js renderer.info
    
-   existing Playwright/browser tooling
    
-   repository test utilities
    

`npm audit` 如果配置registry仍返回不可用或404：

-   如实记录 unavailable
    
-   不得声称 clean
    
-   不得因此自动判定本阶段失败，除非引入了新依赖
    

----------

# 25. Docs / Persistent

新增或更新：

```text
docs/phase10f/phase10f21_viewer_performance_hardening.md
docs/phase10f/phase10f21_viewer_performance_budget.md
docs/phase10f/phase10f21_viewer_large_scene_policy.md
docs/phase10f/phase10f21_viewer_lifecycle_contract.md
docs/phase10f/phase10f21_viewer_performance_evidence.md
docs/phase10f/phase10f21_viewer_performance_security.md
docs/phase10f/phase10f21_viewer_performance_readiness_matrix.md

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

-   atom instancing策略
    
-   bond batching策略
    
-   draw-call budget
    
-   geometry/material budget
    
-   on-demand render policy
    
-   cancellation
    
-   stale scene protection
    
-   lifecycle disposal
    
-   large-scene mode
    
-   degraded mode
    
-   refusal mode
    
-   current known limits
    
-   remaining accessibility/mobile issues
    
-   remaining full viewer productization work
    

----------

# 26. Readiness Matrix

最终分别判断：

-   atom instancing
    
-   bond batching
    
-   lattice geometry
    
-   geometry reuse
    
-   material reuse
    
-   draw-call budget
    
-   memory proxy metrics
    
-   on-demand rendering
    
-   animation loop lifecycle
    
-   scene cancellation
    
-   stale render prevention
    
-   mount/unmount cleanup
    
-   artifact switching cleanup
    
-   WebGL context loss
    
-   context recovery
    
-   small scene
    
-   medium scene
    
-   degraded scene
    
-   over-budget fallback
    
-   Chromium
    
-   Firefox
    
-   WebKit
    
-   mobile
    
-   security
    
-   full `structure.viewer_3d`
    
-   trajectory
    
-   phonon
    
-   Brillouin zone
    
-   volumetric
    

推荐期望：

```text
atom instancing: READY
bond batching: READY
geometry reuse: READY
material reuse: READY
draw-call budget: READY
on-demand rendering: READY
scene cancellation: READY
lifecycle cleanup: READY
context-loss fallback: READY
small scene: READY
medium scene: READY
degraded scene: READY
over-budget fallback: READY
browser matrix: READY
mobile performance foundation: READY or PARTIAL_READY
full structure.viewer_3d: PARTIAL_READY
trajectory: NOT_READY
phonon: NOT_READY
Brillouin zone: NOT_READY
volumetric: NOT_READY

```

不得因为本阶段性能通过就将 full `structure.viewer_3d` 标记为完全 READY。

后续仍需：

-   accessibility
    
-   mobile interaction
    
-   advanced picking/measurement
    
-   supercell productization
    
-   clipping/camera controls
    
-   export
    
-   formal registration
    

----------

# 27. Checks

至少运行：

```bash
git diff --check
uv lock --check

npm --prefix apps/web test
npm --prefix apps/web run typecheck
npm --prefix apps/web run build

uv run python -m pytest -q

```

并运行：

-   viewer renderer focused tests
    
-   performance tests
    
-   lifecycle stress tests
    
-   compatibility tests
    
-   periodic identity tests
    
-   periodic bond tests
    
-   preview tests
    
-   Chromium browser runner
    
-   Firefox browser runner
    
-   WebKit browser runner
    
-   mobile runner
    
-   service-backed integration
    
-   no-skipped assertion
    
-   secret scan
    
-   network audit
    

必须如实记录：

-   passed
    
-   failed
    
-   skipped
    
-   unavailable
    

不得把 skipped写成passed。

----------

# 28. Commit / CI

完成所有实现、测试、evidence和文档后：

```bash
git status --short
git diff --stat
git add <only Phase 10F-21 related files>
git commit -m "Harden viewer rendering performance"
git push origin master

```

等待 current HEAD CI。

必须确认：

-   unit success
    
-   frontend tests success
    
-   frontend typecheck success
    
-   frontend build success
    
-   service-backed integration success
    
-   no-skipped assertion success
    
-   origin/master matches HEAD
    
-   git status clean
    

不得伪造CI结果。

----------

# 29. 最终报告格式

完成后输出：

# Phase 10F-21 Viewer Performance Hardening Result

## 1. Conclusion

PASS / PARTIAL_PASS / FAIL

## 2. Baseline

-   Phase 10F-20 assumed complete:
    
-   branch:
    
-   initial status:
    
-   final HEAD:
    
-   final status:
    

## 3. Performance Architecture

-   atoms:
    
-   bonds:
    
-   lattice:
    
-   geometries:
    
-   materials:
    
-   render scheduling:
    
-   cancellation:
    
-   lifecycle:
    

## 4. Performance Budgets

-   interactive threshold:
    
-   degraded threshold:
    
-   refusal threshold:
    
-   draw-call budget:
    
-   geometry budget:
    
-   material budget:
    
-   displayed atom cap:
    
-   displayed bond cap:
    

## 5. Atom Rendering

-   instancing:
    
-   grouping:
    
-   geometry reuse:
    
-   material reuse:
    
-   periodic identity:
    
-   picking compatibility:
    

## 6. Bond Rendering

-   shared geometry:
    
-   canonical ordering:
    
-   cross-boundary:
    
-   self-periodic:
    
-   highlight:
    
-   cap enforcement:
    

## 7. Render Scheduling

-   continuous animation loop:
    
-   on-demand rendering:
    
-   active loop cap:
    
-   resize:
    
-   controls:
    
-   hidden/inactive state:
    

## 8. Lifecycle

-   mount/unmount:
    
-   artifact switching:
    
-   observer cleanup:
    
-   event cleanup:
    
-   geometry disposal:
    
-   material disposal:
    
-   renderer disposal:
    
-   canvas/context cleanup:
    
-   stale render prevention:
    

## 9. Large Scene Policy

-   interactive:
    
-   degraded:
    
-   over-budget:
    
-   warnings:
    
-   typed fallback:
    
-   JSON-only behavior:
    

## 10. Context Loss / Recovery

-   context lost:
    
-   fallback:
    
-   recovery strategy:
    
-   duplicate canvas/context:
    
-   state restoration:
    

## 11. Metrics

-   tiny:
    
-   small:
    
-   medium:
    
-   degraded:
    
-   over-budget:
    
-   draw calls:
    
-   geometries:
    
-   materials:
    
-   timings:
    
-   resource trend:
    

## 12. Browser Evidence

-   Chromium:
    
-   Firefox:
    
-   WebKit:
    
-   mobile:
    
-   repeated switching:
    
-   mount/unmount:
    
-   context loss:
    
-   console:
    
-   network:
    

## 13. Performance Regression

-   atom scaling:
    
-   bond scaling:
    
-   draw-call scaling:
    
-   geometry scaling:
    
-   material scaling:
    
-   cleanup:
    
-   bundle size:
    

## 14. Security

-   artifact JS:
    
-   artifact HTML:
    
-   shaders/modules:
    
-   external resources:
    
-   network:
    
-   threshold override:
    
-   dependencies:
    
-   secrets:
    

## 15. Evidence

-   directory:
    
-   budgets:
    
-   metrics:
    
-   stress tests:
    
-   screenshots:
    
-   markers:
    

## 16. Tests

-   focused frontend:
    
-   frontend full:
    
-   backend full:
    
-   typecheck:
    
-   build:
    
-   browser:
    
-   service-backed:
    
-   no-skipped:
    
-   lock:
    
-   diff:
    

## 17. Files

-   renderer:
    
-   helpers:
    
-   tests:
    
-   fixtures:
    
-   browser runner:
    
-   evidence:
    
-   docs:
    
-   persistent:
    
-   dependencies/lockfile:
    

## 18. Deferred

明确列出：

-   accessibility hardening
    
-   mobile interaction hardening
    
-   advanced picking
    
-   measurements
    
-   supercell productization
    
-   clipping
    
-   export
    
-   formal `structure.viewer_3d`
    
-   trajectory
    
-   phonon
    
-   Brillouin zone
    
-   volumetric
    
-   defects
    
-   surfaces
    
-   slabs
    

## 19. Readiness

-   atom instancing:
    
-   bond batching:
    
-   draw-call budget:
    
-   lifecycle:
    
-   large-scene handling:
    
-   browser matrix:
    
-   mobile:
    
-   full `structure.viewer_3d`:
    
-   trajectory:
    
-   phonon:
    
-   Brillouin:
    
-   volumetric:
    

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

```text
Phase 10F-22：Viewer Accessibility, Mobile and Cross-Browser Hardening

```

不要进入 trajectory、phonon、Brillouin zone 或 volumetric。

----------

# 30. PASS 判定

PASS 必须满足：

-   有实际renderer性能实现变更
    
-   atoms使用bounded instancing或等价优化
    
-   bonds使用bounded shared geometry或等价优化
    
-   draw calls受控
    
-   geometries受控
    
-   materials受控
    
-   不存在一atom一mesh的生产路径
    
-   不存在一bond一object的生产路径
    
-   on-demand render或等价bounded scheduling完成
    
-   animation loop不泄漏
    
-   scene切换有stale protection
    
-   mount/unmount资源完整释放
    
-   repeated switching无单调资源增长
    
-   context loss有安全fallback
    
-   context recovery或retry策略明确并验证
    
-   large scene有interactive/degraded/refused策略
    
-   over-budget不创建renderer/canvas/context
    
-   periodic identity不回退
    
-   periodic bond topology不回退
    
-   browser matrix evidence完整
    
-   mobile evidence至少达到基础要求
    
-   no external network
    
-   no secret hits
    
-   无新依赖或依赖变更有明确批准
    
-   tests通过
    
-   CI通过
    
-   git clean
    

PARTIAL_PASS仅允许：

-   某一个非主要浏览器性能指标因明确的browser limitation无法稳定读取
    
-   mobile精确GPU指标不可获得，但行为证据完整
    
-   npm audit因既有registry问题不可用
    
-   某些绝对时间指标因CI机器波动仅做趋势验证
    

FAIL包括：

-   只有文档，没有实现
    
-   通过关闭核心功能掩盖性能
    
-   large scene导致浏览器冻结或crash
    
-   over-budget仍初始化WebGL
    
-   重复mount导致canvas/context增长
    
-   scene切换发生stale覆盖
    
-   periodic identity损坏
    
-   periodic bonds错误
    
-   artifact可绕过性能cap
    
-   artifact可控制shader/material细节造成资源滥用
    
-   引入trajectory/phonon/Brillouin/volumetric
    
-   修改核心runtime语义
    
-   无browser evidence
    
-   无stress test
    
-   CI失败却声明PASS

## 完成记录

- 完成时间：2026-07-13 00:47（Asia/Shanghai）
- 修改文件：renderer surface/engine/types、新增 performance policy 与测试、Phase 10F-21 browser runner、evidence/docs 和 persistent 记录。
- 修改摘要：新增 interactive/degraded/refused 性能预算；保持 atom instancing 与 shared bond geometry；近上限场景降低 DPR/antialias 但不截断数据；超限在 engine factory 前拒绝；增加 generation token stale protection、context-loss retry 和资源 proxy metrics。
- 测试结果：focused frontend 19 passed；frontend full 84 passed；backend full 366 passed, 21 skipped；typecheck/build/uv lock 通过；全部 7 个历史 viewer browser runner 与 Phase 10F-21 browser runner 通过；npm audit 因 registry endpoint `NOT_IMPLEMENTED` unavailable；本地 service-backed 因无 Docker unavailable，待 current-HEAD CI 验证。
- 安全结果：`NO_EXTERNAL_NETWORK_REQUESTS`；`NO_SECRET_PATTERN_HITS`；无依赖、lockfile、canonical schema、PlanValidator、QueueWorkerRuntime 或 AnalysisPlanRepository 语义变更。
---END---

---TASK---  
状态：待处理

 # Phase 10F-22：Viewer Accessibility, Mobile and Cross-Browser Hardening

进入 Phase 10F-22：Viewer Accessibility, Mobile and Cross-Browser Hardening。

可以默认：

-   Phase 10F-21 已完成
    
-   viewer performance budgets 已建立
    
-   atom instancing 已完成或已达到 bounded production path
    
-   bond batching 已完成或已达到 bounded production path
    
-   geometry/material reuse 已收口
    
-   on-demand rendering 已完成
    
-   animation loop lifecycle 已收口
    
-   scene cancellation 和 stale render protection 已完成
    
-   mount/unmount、artifact switching、context-loss fallback 已完成
    
-   large scene 已有 interactive / degraded / over-budget policy
    
-   Chromium、Firefox、WebKit 和 mobile 已有基础 performance evidence
    
-   current production viewer scene schema 仍为 `phase10f18.viewer_scene.v2`
    
-   current production manifest 仍为 Phase 10F-19/10F-20 确认的 v2 manifest
    
-   periodic endpoint identity、canonical periodic bonds、neighbor inspector 和 schema compatibility 均保持稳定
    
-   当前 branch、HEAD、working tree 和 Phase 10F-21 CI 可视为正确且 clean
    

本阶段不需要重复 baseline 检查。

本阶段的主要任务是：

> 将现有 periodic crystal viewer 从“性能稳定、功能可运行”提升为“键盘可用、屏幕阅读器可理解、移动端可操作、跨浏览器行为一致、弱视觉和减少动态用户可安全使用”的 viewer foundation。

本阶段仍然不是高级功能扩展阶段。

不要进入：

-   trajectory
    
-   phonon
    
-   Brillouin zone
    
-   volumetric
    
-   defects
    
-   surfaces
    
-   slabs
    
-   structure editing
    
-   advanced measurement
    
-   export
    
-   formal `structure.viewer_3d` registration
    

----------

# 1. 当前已知能力

当前 viewer 已具备：

-   `viewer_scene.v2`
    
-   periodic atom identity
    
-   canonical periodic bond topology
    
-   same-cell / cross-boundary / self-periodic bonds
    
-   triclinic periodic geometry
    
-   neighbor inspector
    
-   real Three.js renderer
    
-   camera rotate / zoom / pan / reset
    
-   scene fallback
    
-   context-loss handling
    
-   renderer lifecycle cleanup
    
-   performance budgets
    
-   atom instancing
    
-   bond batching
    
-   large-scene degraded mode
    
-   over-budget JSON-only fallback
    
-   browser matrix基础
    
-   mobile performance基础
    
-   no artifact JS
    
-   no external resources
    
-   no remote assets
    

当前尚未充分证明：

-   全功能键盘操作
    
-   focus顺序稳定
    
-   focus不会陷入canvas或消失
    
-   screen reader可以理解当前scene
    
-   screen reader可以理解selected atom/bond
    
-   inspector rows具备完整语义
    
-   mobile touch rotate/zoom/pan稳定
    
-   pointer/touch/mouse事件不会冲突
    
-   Safari/WebKit手势差异已处理
    
-   Firefox controls行为一致
    
-   mobile viewport切换后renderer和inspector稳定
    
-   reduced-motion偏好受到尊重
    
-   high-contrast模式可用
    
-   color-only状态已消除
    
-   error/fallback状态可被辅助技术读取
    
-   context-loss、degraded、over-budget状态有live-region反馈
    
-   tooltip和hover信息可由键盘获得
    
-   text scaling不会破坏布局
    
-   zoom到200%仍可使用
    
-   accessibility regression进入自动测试
    
-   touch target尺寸满足要求
    

----------

# 2. 本阶段目标

必须完成以下七类工作：

1.  **Accessibility architecture audit**
    
2.  **Keyboard and focus interaction**
    
3.  **Screen-reader semantic layer**
    
4.  **Mobile and touch interaction hardening**
    
5.  **High contrast, reduced motion and scalable text**
    
6.  **Cross-browser behavior closure**
    
7.  **Accessibility/browser evidence and readiness closure**
    

本阶段必须产生实际实现性代码。

如果最终主要变更只有 docs、ARIA label、readiness matrix 或截图，而没有真正可用的交互和测试，本阶段必须判定为 FAIL。

----------

# 3. 严格禁止范围

本阶段不得实现：

-   trajectory
    
-   animation playback
    
-   phonon
    
-   phonon mode animation
    
-   Brillouin zone
    
-   volumetric data
    
-   isosurface
    
-   charge density
    
-   spin density
    
-   defects
    
-   surfaces
    
-   slabs
    
-   structure editing
    
-   atom mutation
    
-   bond mutation
    
-   advanced distance measurement
    
-   angle measurement
    
-   dihedral measurement
    
-   multi-selection
    
-   lasso selection
    
-   clipping planes
    
-   PNG/PDF export
    
-   glTF/GLB export
    
-   formal `structure.viewer_3d` product registration
    
-   auth
    
-   external API
    
-   notebook execution
    
-   script execution
    
-   real LLM
    

不得：

-   修改 periodic endpoint identity
    
-   修改 canonical periodic bond key
    
-   修改 v2 topology semantics
    
-   修改 `1e-5 Å` distance tolerance
    
-   放宽 validator caps
    
-   修改 QueueWorkerRuntime 主语义
    
-   修改 AnalysisPlanRepository 主语义
    
-   修改 `/planner/jobs` 主语义
    
-   引入新的 renderer framework
    
-   替换 Three.js
    
-   引入 WebGPU
    
-   引入 accessibility overlay第三方运行时
    
-   引入远程字体、远程图标或CDN
    
-   将artifact内容注入ARIA属性
    
-   将用户任意文本直接作为HTML
    
-   通过禁用核心交互伪造accessibility通过
    
-   通过只支持desktop而忽略mobile
    
-   把某个浏览器不兼容写成PASS
    
-   将hover-only交互保留为唯一入口
    
-   将颜色作为唯一状态表达
    
-   将canvas本身伪装成完整可访问scene
    

允许：

-   renderer interaction refactor
    
-   keyboard controls
    
-   focus management
    
-   semantic inspector
    
-   screen-reader summary
    
-   live regions
    
-   mobile touch controls
    
-   viewport/layout fixes
    
-   reduced motion
    
-   high contrast
    
-   browser-specific safe handling
    
-   test utilities
    
-   browser evidence
    
-   docs
    
-   persistent updates
    

----------

# 4. 必读实现

开始后直接阅读当前真实代码，不做baseline检查。

重点定位：

## 4.1 Viewer and Controls

搜索：

```bash
rg -n "OrbitControls|pointer|touch|wheel|keydown|keyup|tabIndex|aria-|role=|focus|blur|canvas" apps/web

```

重点确认：

-   renderer component
    
-   controls initialization
    
-   canvas attributes
    
-   keyboard handlers
    
-   pointer handlers
    
-   touch handlers
    
-   wheel handling
    
-   reset controls
    
-   inspector controls
    
-   selection/highlight state
    
-   fallback UI
    
-   context loss UI
    
-   degraded mode UI
    
-   over-budget UI
    

## 4.2 Inspector

检查：

-   semantic table
    
-   rows
    
-   atom identity
    
-   bond identity
    
-   selected state
    
-   focus behavior
    
-   keyboard activation
    
-   scrolling
    
-   mobile layout
    

## 4.3 Existing styles

检查：

-   color variables
    
-   focus outlines
    
-   dark/light modes
    
-   high-contrast behavior
    
-   responsive breakpoints
    
-   text sizing
    
-   overflow
    
-   modal/dialog behavior
    
-   tooltips
    

## 4.4 Existing tests and evidence

定位：

-   Phase 10F-17 inspector tests
    
-   Phase 10F-18 periodic topology tests
    
-   Phase 10F-19 preview tests
    
-   Phase 10F-21 performance/browser tests
    
-   current mobile runner
    
-   current WebKit runner
    
-   existing accessibility tests
    
-   existing axe或等价工具，若仓库已有
    

不得为了本阶段引入大型新测试依赖，优先复用现有工具。

----------

# 5. 修改前输出审计

修改代码前输出：

# Phase 10F-22 Viewer Accessibility Pre-Implementation Audit

## 1. Current Keyboard Model

-   canvas focusability:
    
-   toolbar focusability:
    
-   reset control:
    
-   inspector rows:
    
-   selection activation:
    
-   escape behavior:
    
-   focus restoration:
    
-   known gaps:
    

## 2. Current Semantic Model

-   scene summary:
    
-   atom semantics:
    
-   bond semantics:
    
-   selected state:
    
-   topology state:
    
-   fallback state:
    
-   context-loss state:
    
-   degraded mode state:
    
-   live regions:
    
-   known gaps:
    

## 3. Current Mobile Interaction

-   one-finger gesture:
    
-   two-finger gesture:
    
-   pinch:
    
-   pan:
    
-   scroll conflict:
    
-   viewport resize:
    
-   orientation change:
    
-   touch targets:
    
-   inspector mobile layout:
    
-   known gaps:
    

## 4. Current Cross-Browser Risks

-   Chromium:
    
-   Firefox:
    
-   WebKit:
    
-   iOS/Safari:
    
-   mobile Chromium:
    
-   pointer events:
    
-   wheel delta:
    
-   ResizeObserver:
    
-   focus-visible:
    
-   reduced motion:
    
-   high contrast:
    

## 5. Selected Strategy

说明：

-   keyboard:
    
-   focus:
    
-   semantic scene:
    
-   inspector:
    
-   mobile gestures:
    
-   cross-browser handling:
    
-   reduced motion:
    
-   high contrast:
    
-   testing:
    

## 6. Planned Files

列出预计修改或新增：

-   viewer component
    
-   controls
    
-   inspector
    
-   styles
    
-   helpers
    
-   tests
    
-   browser runner
    
-   mobile runner
    
-   evidence
    
-   docs
    
-   persistent
    

审计完成后直接继续执行。

----------

# 6. Accessibility Contract

建立 application-owned accessibility contract。

必须明确：

## 6.1 Renderer Surface

canvas本身不是完整语义载体。

必须提供与scene同步的DOM语义层，至少包含：

-   structure formula
    
-   site count
    
-   species count
    
-   lattice summary
    
-   canonical bond count
    
-   cross-boundary bond count
    
-   self-periodic bond count
    
-   current render mode
    
-   current selected atom/bond
    
-   current warnings
    
-   renderer/fallback state
    

## 6.2 Interaction Equivalence

所有核心交互必须有非pointer替代方式：

-   focus viewer
    
-   rotate or inspect orientation
    
-   zoom
    
-   pan
    
-   reset
    
-   select atom
    
-   select neighbor
    
-   open inspector
    
-   close inspector
    
-   clear selection
    
-   switch between renderer and JSON preview，若UI已有该功能
    
-   retry after recoverable context loss
    

不要求键盘模拟所有自由3D手势，但必须提供功能上等价且可理解的控制。

## 6.3 State Announcements

以下状态变化必须可被辅助技术读取：

-   scene loaded
    
-   scene changed
    
-   selection changed
    
-   atom selected
    
-   neighbor selected
    
-   bond selected，若当前已支持
    
-   selection cleared
    
-   renderer entered degraded mode
    
-   renderer refused due to budget
    
-   context lost
    
-   context restored
    
-   fallback shown
    
-   invalid scene
    
-   legacy schema JSON-only state
    

## 6.4 No Color-Only Communication

以下状态不能只靠颜色：

-   selected atom
    
-   selected neighbor
    
-   warning
    
-   error
    
-   disabled control
    
-   degraded mode
    
-   context loss
    
-   over-budget
    
-   current schema
    
-   current render mode
    

必须同时使用：

-   text
    
-   icon with accessible label
    
-   border/pattern/shape
    
-   semantic attribute
    

----------

# 7. Keyboard Navigation

## 7.1 Tab Order

必须建立稳定tab顺序。

推荐顺序：

1.  viewer region
    
2.  camera/reset controls
    
3.  render mode controls
    
4.  inspector controls
    
5.  atom/neighbor table
    
6.  clear selection
    
7.  fallback/retry controls
    

要求：

-   不出现不可见focus target
    
-   不将大量canvas内部对象逐个加入tab顺序
    
-   不将每个显示atom直接映射为数千个tab item
    
-   大型scene仍保持bounded tab order
    
-   inspector table使用合理的roving tabindex或普通表格焦点策略
    
-   focus顺序不随scene rebuild随机改变
    

## 7.2 Viewer Region

viewer容器必须：

-   可聚焦
    
-   有可理解名称
    
-   有简短说明
    
-   声明当前render mode
    
-   声明可用键盘快捷键
    
-   不使用误导性role
    

可以使用：

```text
role="region"

```

或仓库审计后选择的更合适语义。

不要把canvas标记为：

```text
role="application"

```

除非确有完整的application keyboard model并有充分理由。

## 7.3 Keyboard Camera Controls

提供明确、bounded的键盘控制。

建议：

-   Arrow keys：rotate
    
-   Shift + Arrow：pan
    
-   `+` / `=`：zoom in
    
-   `-`：zoom out
    
-   `0` 或 `r`：reset
    
-   Escape：clear selection / close transient inspector state
    
-   Enter / Space：activate focused control
    

要求：

-   step size application-owned
    
-   key repeat bounded
    
-   不触发页面意外滚动
    
-   仅在viewer聚焦时拦截对应键
    
-   输入框/文本框中不拦截
    
-   reduced-motion模式下降低或取消平滑过渡
    
-   不允许artifact控制快捷键
    

快捷键必须在UI中可发现，不能只存在于文档。

## 7.4 Focus Restoration

以下操作后必须恢复合理focus：

-   scene切换
    
-   inspector关闭
    
-   context-loss fallback
    
-   retry后恢复
    
-   JSON-only fallback
    
-   degraded mode切换
    
-   artifact切换
    
-   invalid scene错误
    

不得让focus丢到`body`或不存在节点。

----------

# 8. Screen Reader Semantic Layer

## 8.1 Scene Summary

新增与当前scene同步的DOM摘要。

至少包含：

```text
Formula
Site count
Species count
Lattice
Canonical bonds
Cross-boundary bonds
Self-periodic bonds
Render mode
Current selection
Warnings

```

要求：

-   不复制巨大scene payload
    
-   不列出全部atom
    
-   不列出全部bond
    
-   内容bounded
    
-   使用真实文本
    
-   不依赖canvas
    
-   与current scene同步
    
-   scene切换后更新
    

## 8.2 Atom Identity

selected atom必须使用统一periodic identity：

```text
site_index@[image_offset]

```

并显示：

-   element/species
    
-   canonical site index
    
-   image offset
    
-   fractional coordinates
    
-   Cartesian coordinates，若当前contract包含
    
-   occupancy，若存在
    
-   selected state
    

不得只说：

```text
Atom 3

```

必须能区分periodic instance。

## 8.3 Bond Identity

若当前UI允许bond或neighbor relationship高亮，语义文本必须包含：

-   source endpoint
    
-   target endpoint
    
-   image offset
    
-   distance
    
-   source
    
-   authoritative
    
-   cross-boundary status
    
-   self-periodic status
    

## 8.4 Live Region

新增bounded live region。

要求：

-   `aria-live`使用合理级别
    
-   普通selection变化使用polite
    
-   error/context-loss可使用assertive，若合适
    
-   不重复播报camera每一步变化
    
-   不在pointer move时连续刷屏
    
-   不播报每一帧
    
-   不播报每个hover atom
    
-   同一消息去重
    
-   scene切换只播报一次
    

----------

# 9. Inspector Accessibility

## 9.1 Semantic Table

Neighbor inspector必须使用真正语义结构：

-   table
    
-   caption
    
-   thead
    
-   tbody
    
-   th
    
-   td
    

若当前交互需要button：

-   row中的可操作元素使用button
    
-   不用div模拟button
    
-   支持Enter和Space
    
-   有focus-visible
    
-   有selected/pressed状态
    

## 9.2 Row Content

每行至少包含：

-   target periodic identity
    
-   element/species
    
-   distance
    
-   image offset
    
-   source
    
-   authoritative state
    
-   cross-boundary状态
    

## 9.3 Selection State

使用：

-   `aria-selected`
    
-   或 `aria-pressed`
    

按实际控件语义选择。

不得滥用两者。

## 9.4 Large Neighbor Lists

必须保持bounded：

-   inspector row cap
    
-   virtualization若已有则复用
    
-   若截断，明确显示count和warning
    
-   不将数千行一次全部加入DOM
    
-   不因accessibility而绕过performance budget
    

----------

# 10. Mobile Touch Interaction

## 10.1 Gesture Contract

必须明确移动端手势：

推荐：

-   单指拖动：rotate
    
-   双指拖动：pan
    
-   pinch：zoom
    
-   tap：select atom
    
-   tap空白：clear selection，若当前交互适合
    
-   double tap：不得默认触发浏览器zoom冲突，除非明确处理
    

要求：

-   页面垂直滚动与viewer手势有明确边界
    
-   viewer不应永久劫持全页scroll
    
-   在viewer外滚动正常
    
-   在viewer内只有有效手势时preventDefault
    
-   touch-action使用明确策略
    
-   不导致iOS橡皮筋滚动异常
    
-   不导致页面卡住
    
-   不产生ghost click
    
-   不触发重复selection
    

## 10.2 Touch Targets

所有触摸控件至少满足合理触摸尺寸。

建议：

```text
minimum 44 × 44 CSS px

```

至少覆盖：

-   reset
    
-   zoom controls
    
-   inspector close
    
-   retry
    
-   render mode switch
    
-   clear selection
    

不得靠极小图标作为唯一点击区域。

## 10.3 Mobile Inspector

要求：

-   不遮挡整个viewer且无法关闭
    
-   可滚动
    
-   header固定或清晰
    
-   close button可见
    
-   focus management正确
    
-   键盘出现时不崩布局
    
-   小屏幕下文本不溢出
    
-   periodic identity可换行
    
-   table可横向滚动或重排
    
-   不依赖hover
    

## 10.4 Orientation Change

必须测试：

-   portrait → landscape
    
-   landscape → portrait
    

验证：

-   renderer resize
    
-   camera不异常
    
-   canvas数量不增加
    
-   controls不重复
    
-   inspector状态合理
    
-   selection不丢失或明确重置
    
-   no stale viewport
    
-   no context leak
    

----------

# 11. Pointer, Mouse and Touch Unification

优先使用Pointer Events，若当前实现已使用。

要求：

-   mouse
    
-   touch
    
-   pen
    

共享统一逻辑。

必须避免：

-   touch和mouse双触发
    
-   pointer capture未释放
    
-   pointercancel未处理
    
-   多指状态残留
    
-   pointerup丢失
    
-   component unmount后仍保留capture
    
-   context loss后手势仍运行
    

新增测试覆盖：

-   pointerdown
    
-   pointermove
    
-   pointerup
    
-   pointercancel
    
-   multi-touch
    
-   interrupted gesture
    
-   unmount during gesture
    

----------

# 12. Reduced Motion

尊重：

```css
@media (prefers-reduced-motion: reduce)

```

要求：

-   camera reset不使用长动画
    
-   selection pulse减弱或取消
    
-   loading animation减弱
    
-   context restore transition减弱
    
-   panel transition减弱
    
-   no infinite decorative animation
    
-   render loop仍按Phase 10F-21 bounded策略
    
-   不能影响科学数据或scene状态
    

若当前没有动画，也必须记录并测试：

-   reduced motion不会触发额外路径
    
-   interaction保持可用
    

----------

# 13. High Contrast and Visual Accessibility

## 13.1 Focus Indicator

所有键盘可操作控件必须有清晰focus-visible。

要求：

-   不只改变轻微颜色
    
-   outline不被overflow裁剪
    
-   dark/light均可见
    
-   high contrast模式可见
    
-   focus indicator不能依赖artifact颜色
    

## 13.2 Selection Highlight

selected atom/bond必须至少有两种视觉变化，例如：

-   outline/ring
    
-   size
    
-   line width
    
-   textual selected state
    

不能只变颜色。

## 13.3 Warning/Error

warning、error、degraded、fallback必须：

-   有文字
    
-   有icon或形状
    
-   有semantic role
    
-   颜色仅作为辅助
    

## 13.4 Contrast

检查：

-   text
    
-   control labels
    
-   muted text
    
-   warnings
    
-   errors
    
-   selected rows
    
-   disabled controls
    
-   inspector table
    
-   overlays
    

目标应符合项目可执行的WCAG AA级对比原则。

不要求对3D atom本身的科学配色做绝对WCAG保证，但必须提供：

-   text legend
    
-   selected outline
    
-   non-color identity
    
-   species text
    

----------

# 14. Text Scaling and Responsive Layout

必须测试：

-   browser zoom 200%
    
-   large text
    
-   narrow mobile viewport
    
-   long formula
    
-   long periodic identity
    
-   long warning text
    
-   multiple warnings
    
-   large inspector table
    

要求：

-   controls不重叠
    
-   文本不截断到无法理解
    
-   横向滚动在必要位置可控
    
-   页面整体不产生不可操作overflow
    
-   viewer仍可访问
    
-   inspector可关闭
    
-   fallback可操作
    
-   no fixed pixel layout breakage
    

----------

# 15. Cross-Browser Hardening

## 15.1 Chromium

验证：

-   keyboard
    
-   focus
    
-   pointer
    
-   touch emulation
    
-   live region
    
-   reduced motion
    
-   high contrast模拟
    
-   200% zoom
    
-   context loss fallback
    

## 15.2 Firefox

重点检查：

-   wheel delta差异
    
-   focus-visible
    
-   keyboard event key values
    
-   pointer capture
    
-   ResizeObserver timing
    
-   screen-reader DOM semantics
    
-   table navigation
    
-   200% zoom
    

## 15.3 WebKit

重点检查：

-   touch-action
    
-   passive event listeners
    
-   pinch/scroll conflict
    
-   focus behavior
    
-   canvas sizing
    
-   viewport resize
    
-   context loss
    
-   orientation change
    
-   button activation
    
-   live region更新
    

## 15.4 Mobile

至少覆盖：

-   mobile Chromium
    
-   WebKit mobile profile
    

验证：

-   portrait
    
-   landscape
    
-   pinch
    
-   pan
    
-   rotate
    
-   tap selection
    
-   inspector
    
-   touch target
    
-   no scroll trap
    
-   no duplicate events
    
-   no duplicate canvas/context
    

----------

# 16. Accessibility Automation

优先复用仓库已有工具。

自动检查至少覆盖：

-   missing accessible names
    
-   invalid ARIA
    
-   duplicate IDs
    
-   focusable hidden elements
    
-   semantic table errors
    
-   button name
    
-   landmark structure
    
-   color-independent state，按可自动验证范围
    
-   keyboard trap
    
-   tab order smoke test
    
-   focus restoration
    
-   live-region update
    
-   reduced-motion class/state
    
-   large text layout smoke test
    

如果仓库已有axe或等价工具：

-   使用现有依赖
    
-   不新增重复工具
    

如果没有：

-   使用Playwright DOM assertions
    
-   不必为了本阶段安装大型依赖
    

不得声称自动工具可以证明全部accessibility。

必须结合：

-   keyboard evidence
    
-   DOM evidence
    
-   screenshots
    
-   browser behavior
    

----------

# 17. Accessibility Fixtures

新增或复用bounded fixtures：

## 17.1 Minimal

-   2–4 atoms
    
-   1 bond
    
-   easy keyboard/selection testing
    

## 17.2 Multi-Species

-   multiple species
    
-   legend/summary testing
    

## 17.3 Periodic Cross-Boundary

-   endpoint offsets
    
-   inspector semantics
    

## 17.4 Self-Periodic

-   self-periodic relationship wording
    

## 17.5 Long Labels

-   long formula
    
-   long warning
    
-   long periodic identity
    

## 17.6 Degraded Mode

-   performance warning
    
-   accessible status
    

## 17.7 Over-Budget

-   JSON-only fallback
    
-   no canvas
    
-   accessible reason
    

不得加入巨大fixture。

----------

# 18. Tests

## 18.1 Keyboard Tests

覆盖：

-   tab into viewer
    
-   arrow rotate
    
-   shift+arrow pan
    
-   plus/minus zoom
    
-   reset shortcut
    
-   Escape clear
    
-   focus not trapped
    
-   focus restoration
    
-   input fields unaffected
    
-   shortcuts discoverable
    
-   disabled controls skipped
    

## 18.2 Semantic Tests

覆盖：

-   viewer region name
    
-   scene summary
    
-   selected atom identity
    
-   periodic offset text
    
-   bond/neighbor text
    
-   warning role
    
-   fallback role
    
-   degraded state
    
-   over-budget state
    
-   context-loss announcement
    

## 18.3 Inspector Tests

覆盖：

-   semantic table
    
-   caption
    
-   headers
    
-   row buttons
    
-   keyboard activation
    
-   selected state
    
-   row cap
    
-   long content
    
-   focus on close/open
    

## 18.4 Mobile Tests

覆盖：

-   pointer/touch events
    
-   pinch zoom
    
-   pan
    
-   rotate
    
-   tap selection
    
-   pointercancel
    
-   orientation change
    
-   no scroll trap
    
-   touch target size
    
-   mobile inspector
    

## 18.5 Reduced Motion Tests

覆盖：

-   media query
    
-   no long reset animation
    
-   no decorative loop
    
-   interaction still works
    

## 18.6 High Contrast / Zoom Tests

覆盖：

-   focus visible
    
-   selected state non-color indicator
    
-   200% zoom
    
-   narrow viewport
    
-   long text
    
-   warning/error visibility
    

## 18.7 Regression Tests

必须保持：

-   performance budgets
    
-   lifecycle cleanup
    
-   periodic identity
    
-   periodic bonds
    
-   schema compatibility
    
-   JSON preview
    
-   context-loss fallback
    
-   no external network
    
-   no artifact JS
    

----------

# 19. Browser Evidence

新增：

```text
docs/phase10f/evidence/phase10f22_viewer_accessibility_mobile_cross_browser/

```

必须使用真实浏览器。

至少覆盖：

## 19.1 Chromium

-   keyboard navigation
    
-   focus order
    
-   selected atom semantics
    
-   inspector keyboard
    
-   reduced motion
    
-   200% zoom
    
-   degraded mode
    
-   over-budget fallback
    

## 19.2 Firefox

-   keyboard navigation
    
-   focus-visible
    
-   wheel/zoom
    
-   inspector semantics
    
-   200% zoom
    
-   over-budget fallback
    

## 19.3 WebKit

-   keyboard
    
-   touch-action
    
-   live region
    
-   inspector
    
-   orientation/viewport behavior
    
-   fallback
    

## 19.4 Mobile

至少：

-   portrait
    
-   landscape
    
-   rotate
    
-   pan
    
-   pinch
    
-   tap selection
    
-   inspector open/close
    
-   over-budget fallback
    
-   no scroll trap
    
-   touch target evidence
    

----------

# 20. Evidence Assertions

每个browser evidence必须记录：

-   browser version
    
-   viewport
    
-   device class
    
-   input mode
    
-   keyboard sequence
    
-   focus sequence
    
-   selected identity
    
-   live-region text
    
-   touch gesture result
    
-   orientation state
    
-   zoom level
    
-   reduced-motion state
    
-   console errors
    
-   network requests
    
-   canvas count
    
-   context count
    

必须验证：

-   keyboard can reach all essential controls
    
-   no keyboard trap
    
-   focus remains visible
    
-   focus restoration works
    
-   screen-reader text is present and correct
    
-   periodic identity is exact
    
-   no hover-only essential information
    
-   mobile gestures work
    
-   page scroll remains possible
    
-   no duplicate pointer/touch event
    
-   orientation change does not duplicate renderer
    
-   200% zoom remains usable
    
-   degraded/over-budget states are announced
    
-   no external network
    
-   no artifact JS
    

----------

# 21. Evidence Files

建议至少包含：

```text
README.md
accessibility_contract.json
keyboard_matrix.json
focus_order.json
semantic_scene_snapshot.json
inspector_semantics.json
live_region_events.json
mobile_gesture_matrix.json
orientation_change.json
touch_target_audit.json
reduced_motion_audit.json
high_contrast_audit.json
zoom_200_percent_audit.json
cross_browser_matrix.json
console_audit.json
network_audit.json
security_audit.json
artifact_hashes.json

```

截图建议：

```text
01_keyboard_focus_viewer.png
02_keyboard_focus_controls.png
03_selected_atom_semantics.png
04_neighbor_inspector_keyboard.png
05_degraded_mode_accessible.png
06_over_budget_accessible_fallback.png
07_firefox_200_percent_zoom.png
08_webkit_focus_state.png
09_mobile_portrait.png
10_mobile_landscape.png
11_mobile_inspector.png
12_reduced_motion_state.png

```

不要保存：

-   OS用户名
    
-   private path
    
-   screen reader用户配置
    
-   browser profile secrets
    
-   tokens
    
-   remote URLs
    
-   large trace dumps
    
-   cache
    
-   crash dumps
    

----------

# 22. Security

必须验证：

-   no artifact JavaScript
    
-   no artifact HTML
    
-   no artifact ARIA injection
    
-   no artifact-controlled role
    
-   no artifact-controlled event handler
    
-   no artifact-controlled keyboard binding
    
-   no artifact-controlled focus target
    
-   no artifact shader
    
-   no artifact module
    
-   no eval
    
-   no Function constructor
    
-   no external URL
    
-   no remote font
    
-   no remote icon
    
-   no CDN
    
-   no iframe
    
-   no arbitrary local file access
    
-   no notebook execution
    
-   no script execution
    
-   no real LLM
    
-   no dependency addition
    
-   no browser fingerprinting
    
-   no accessibility telemetry upload
    
-   no raw scene payload in live region
    
-   no unbounded DOM generation
    
-   no unbounded inspector rows
    
-   no touch gesture bypass of performance caps
    
-   no over-budget renderer initialization
    

必须输出：

```text
NO_EXTERNAL_NETWORK_REQUESTS
NO_SECRET_PATTERN_HITS

```

----------

# 23. Dependency Policy

本阶段默认不新增依赖。

优先使用：

-   React/DOM semantics
    
-   existing Playwright/browser tooling
    
-   existing test utilities
    
-   existing CSS
    
-   existing accessibility tooling，若已有
    

检查：

```bash
npm --prefix apps/web ls --depth=0
npm --prefix apps/web run build

```

记录：

-   dependency tree unchanged
    
-   lockfile unchanged
    
-   bundle size变化
    
-   accessibility代码是否造成异常bundle增长
    

若已有audit registry问题，继续如实记录。

----------

# 24. Docs / Persistent

新增或更新：

```text
docs/phase10f/phase10f22_viewer_accessibility_hardening.md
docs/phase10f/phase10f22_viewer_keyboard_contract.md
docs/phase10f/phase10f22_viewer_semantic_scene_contract.md
docs/phase10f/phase10f22_viewer_mobile_interaction_contract.md
docs/phase10f/phase10f22_viewer_cross_browser_matrix.md
docs/phase10f/phase10f22_viewer_accessibility_security.md
docs/phase10f/phase10f22_viewer_accessibility_evidence.md
docs/phase10f/phase10f22_viewer_accessibility_readiness_matrix.md

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

-   keyboard model
    
-   focus model
    
-   semantic scene model
    
-   live region policy
    
-   inspector accessibility
    
-   mobile gesture contract
    
-   touch target policy
    
-   reduced motion
    
-   high contrast
    
-   cross-browser differences
    
-   current limitations
    
-   remaining advanced picking/measurement work
    
-   remaining supercell productization
    
-   remaining export
    
-   formal viewer registration仍未完成
    

----------

# 25. Readiness Matrix

最终分别判断：

-   viewer region semantics
    
-   keyboard navigation
    
-   camera keyboard controls
    
-   focus order
    
-   focus restoration
    
-   selected atom semantics
    
-   bond/neighbor semantics
    
-   live region
    
-   inspector table
    
-   mobile rotate
    
-   mobile pan
    
-   pinch zoom
    
-   tap selection
    
-   orientation change
    
-   touch target size
    
-   no scroll trap
    
-   reduced motion
    
-   high contrast
    
-   200% zoom
    
-   Chromium
    
-   Firefox
    
-   WebKit
    
-   mobile Chromium
    
-   mobile WebKit
    
-   security
    
-   full `structure.viewer_3d`
    
-   advanced picking
    
-   measurement
    
-   supercell
    
-   export
    
-   trajectory
    
-   phonon
    
-   Brillouin zone
    
-   volumetric
    

推荐期望：

```text
viewer region semantics: READY
keyboard navigation: READY
focus management: READY
scene summary: READY
periodic identity semantics: READY
inspector accessibility: READY
mobile rotate/pan/zoom: READY
orientation handling: READY
touch target policy: READY
reduced motion: READY
high contrast foundation: READY
200% zoom: READY
Chromium: READY
Firefox: READY
WebKit: READY
mobile foundation: READY
full structure.viewer_3d: PARTIAL_READY
advanced picking: NOT_READY
measurement: NOT_READY
supercell productization: NOT_READY
export: NOT_READY
trajectory: NOT_READY
phonon: NOT_READY
Brillouin zone: NOT_READY
volumetric: NOT_READY

```

不得因为本阶段accessibility通过就将full viewer标记完全READY。

----------

# 26. Checks

至少运行：

```bash
git diff --check
uv lock --check

npm --prefix apps/web test
npm --prefix apps/web run typecheck
npm --prefix apps/web run build

uv run python -m pytest -q

```

并运行：

-   accessibility focused tests
    
-   keyboard tests
    
-   focus tests
    
-   inspector tests
    
-   mobile interaction tests
    
-   reduced-motion tests
    
-   200% zoom browser tests
    
-   Chromium runner
    
-   Firefox runner
    
-   WebKit runner
    
-   mobile runner
    
-   performance regression
    
-   lifecycle regression
    
-   periodic identity regression
    
-   periodic bond regression
    
-   schema compatibility regression
    
-   service-backed integration
    
-   no-skipped assertion
    
-   secret scan
    
-   network audit
    

必须如实记录：

-   passed
    
-   failed
    
-   skipped
    
-   unavailable
    

不得把skipped写成passed。

----------

# 27. Commit / CI

完成实现、测试、evidence和文档后：

```bash
git status --short
git diff --stat
git add <only Phase 10F-22 related files>
git commit -m "Harden viewer accessibility and mobile support"
git push origin master

```

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

# 28. 最终报告格式

完成后输出：

# Phase 10F-22 Viewer Accessibility, Mobile and Cross-Browser Hardening Result

## 1. Conclusion

PASS / PARTIAL_PASS / FAIL

## 2. Baseline

-   Phase 10F-21 assumed complete:
    
-   branch:
    
-   initial status:
    
-   final HEAD:
    
-   final status:
    

## 3. Accessibility Architecture

-   viewer region:
    
-   semantic scene layer:
    
-   keyboard model:
    
-   focus model:
    
-   live region:
    
-   inspector:
    
-   mobile model:
    

## 4. Keyboard

-   tab order:
    
-   viewer focus:
    
-   rotate:
    
-   pan:
    
-   zoom:
    
-   reset:
    
-   escape:
    
-   focus restoration:
    
-   shortcuts discoverability:
    

## 5. Semantic Scene

-   formula:
    
-   sites:
    
-   species:
    
-   lattice:
    
-   bonds:
    
-   periodic identity:
    
-   selection:
    
-   warnings:
    
-   render mode:
    

## 6. Inspector

-   semantic table:
    
-   headers:
    
-   rows:
    
-   keyboard activation:
    
-   selected state:
    
-   periodic endpoint text:
    
-   row cap:
    
-   focus behavior:
    

## 7. Mobile Interaction

-   rotate:
    
-   pan:
    
-   pinch zoom:
    
-   tap selection:
    
-   pointer cancellation:
    
-   scroll behavior:
    
-   touch targets:
    
-   mobile inspector:
    
-   orientation change:
    

## 8. Visual Accessibility

-   focus-visible:
    
-   selection indicator:
    
-   warnings/errors:
    
-   high contrast:
    
-   reduced motion:
    
-   200% zoom:
    
-   long text:
    
-   narrow viewport:
    

## 9. Cross-Browser

-   Chromium:
    
-   Firefox:
    
-   WebKit:
    
-   mobile Chromium:
    
-   mobile WebKit:
    
-   browser-specific fixes:
    

## 10. State Announcements

-   scene loaded:
    
-   selection changed:
    
-   degraded mode:
    
-   over-budget:
    
-   context lost:
    
-   context restored:
    
-   invalid scene:
    
-   legacy schema:
    

## 11. Browser Evidence

-   keyboard:
    
-   focus:
    
-   live region:
    
-   inspector:
    
-   mobile gestures:
    
-   orientation:
    
-   zoom:
    
-   console:
    
-   network:
    
-   canvas/context:
    

## 12. Regression

-   performance:
    
-   lifecycle:
    
-   periodic identity:
    
-   periodic bonds:
    
-   schema compatibility:
    
-   fallback:
    
-   no external network:
    

## 13. Security

-   artifact ARIA injection:
    
-   artifact keyboard injection:
    
-   artifact JS/HTML:
    
-   external resources:
    
-   raw payload announcements:
    
-   unbounded DOM:
    
-   dependencies:
    
-   secrets:
    
-   network:
    

## 14. Evidence

-   directory:
    
-   keyboard matrix:
    
-   focus order:
    
-   semantic snapshot:
    
-   mobile matrix:
    
-   cross-browser matrix:
    
-   screenshots:
    
-   markers:
    

## 15. Tests

-   accessibility focused:
    
-   frontend full:
    
-   backend full:
    
-   typecheck:
    
-   build:
    
-   Chromium:
    
-   Firefox:
    
-   WebKit:
    
-   mobile:
    
-   service-backed:
    
-   no-skipped:
    
-   lock:
    
-   diff:
    

## 16. Files

-   viewer:
    
-   controls:
    
-   inspector:
    
-   styles:
    
-   helpers:
    
-   tests:
    
-   browser runners:
    
-   evidence:
    
-   docs:
    
-   persistent:
    
-   dependencies/lockfile:
    

## 17. Deferred

明确列出：

-   advanced picking
    
-   multi-selection
    
-   distance measurement
    
-   angle measurement
    
-   dihedral measurement
    
-   supercell productization
    
-   clipping
    
-   camera preset productization
    
-   export
    
-   formal `structure.viewer_3d`
    
-   trajectory
    
-   phonon
    
-   Brillouin zone
    
-   volumetric
    
-   defects
    
-   surfaces
    
-   slabs
    

## 18. Readiness

-   keyboard:
    
-   focus:
    
-   semantic scene:
    
-   inspector:
    
-   mobile gestures:
    
-   orientation:
    
-   high contrast:
    
-   reduced motion:
    
-   zoom:
    
-   browser matrix:
    
-   full `structure.viewer_3d`:
    
-   advanced picking:
    
-   measurement:
    
-   supercell:
    
-   export:
    
-   trajectory:
    
-   phonon:
    
-   Brillouin:
    
-   volumetric:
    

## 19. Commit / CI

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
    

## 20. Whether allowed to enter next phase

允许 / 不允许

下一阶段建议：

```text
Phase 10F-23：Advanced Picking and Measurement

```

不要进入trajectory、phonon、Brillouin zone或volumetric。

----------

# 29. PASS 判定

PASS 必须满足：

-   有实际accessibility和mobile实现变更
    
-   viewer可由键盘聚焦
    
-   核心camera操作有键盘入口
    
-   focus顺序稳定
    
-   focus restoration完成
    
-   无keyboard trap
    
-   semantic scene summary存在
    
-   selected atom使用完整periodic identity
    
-   neighbor inspector为真实语义table
    
-   essential information不依赖hover
    
-   essential states不只依赖颜色
    
-   live region announcements bounded
    
-   mobile rotate/pan/pinch/tap可用
    
-   页面没有scroll trap
    
-   touch target满足要求
    
-   orientation change稳定
    
-   reduced motion受到尊重
    
-   200% zoom仍可操作
    
-   Chromium/Firefox/WebKit证据完整
    
-   mobile evidence完整
    
-   no duplicate pointer/touch events
    
-   no duplicate canvas/context
    
-   performance regression不回退
    
-   periodic identity不回退
    
-   periodic topology不回退
    
-   no artifact ARIA/keyboard injection
    
-   no external network
    
-   no secret hits
    
-   无新依赖或依赖变更有明确批准
    
-   tests通过
    
-   CI通过
    
-   git clean
    

PARTIAL_PASS仅允许：

-   某个真实screen reader无法在CI自动运行，但DOM语义、键盘、live-region和browser evidence完整
    
-   某个mobile browser无法提供精确自动化gesture数据，但真实行为证据完整
    
-   npm audit因既有registry问题不可用
    
-   某个高对比系统模式无法在CI完全模拟，但CSS和DOM证据完整
    

FAIL包括：

-   只有ARIA label，没有可用键盘交互
    
-   keyboard trap
    
-   focus丢失
    
-   hover-only核心信息
    
-   color-only状态
    
-   mobile scroll被永久劫持
    
-   pinch/rotate造成页面冻结
    
-   orientation change复制canvas/context
    
-   inspector使用div伪造table/button且不可键盘操作
    
-   live region连续播报camera变化
    
-   artifact可注入ARIA、role或快捷键
    
-   200% zoom后不可操作
    
-   某主流浏览器失败却声明PASS
    
-   引入trajectory/phonon/Brillouin/volumetric
    
-   修改核心runtime语义
    
-   无browser evidence
    
-   CI失败却声明PASS
---END---


---TASK---  
状态：待处理

 # Phase 10F-23：Advanced Picking and Measurement

进入 Phase 10F-23：Advanced Picking and Measurement。

可以默认：

-   Phase 10F-22 已完成
    
-   viewer keyboard、focus、screen-reader语义、mobile touch和cross-browser基础已收口
    
-   Phase 10F-21 performance budgets、instancing、bond batching、lifecycle和large-scene policy已完成
    
-   current production scene schema仍为 `phase10f18.viewer_scene.v2`
    
-   current production manifest仍为当前v2 manifest
    
-   periodic endpoint identity、canonical periodic bond topology、neighbor inspector、legacy compatibility和renderer gate均保持稳定
    
-   viewer已经具备单个atom/neighbor基础highlight和inspection能力
    
-   当前branch、HEAD、working tree和Phase 10F-22 CI可视为正确且clean
    

本阶段不需要重复baseline检查。

本阶段的主要任务是：

> 将当前基础inspection能力提升为科学语义完整、周期边界正确、可键盘操作、可导出审计结果的 advanced picking and measurement foundation。

本阶段重点包括：

-   atom picking
    
-   bond picking
    
-   periodic image identity
    
-   single selection
    
-   bounded multi-selection
    
-   distance measurement
    
-   angle measurement
    
-   dihedral measurement
    
-   periodic shortest-image policy
    
-   explicit image-offset measurement
    
-   selection/measurement inspector
    
-   deterministic measurement artifacts
    
-   browser evidence
    

本阶段不是structure editing phase。

不得修改结构、坐标、晶格、bond topology或artifact输入。

----------

# 1. 当前已知能力

当前viewer已具备：

-   periodic atom identity：  
    `site_index@[image_offset]`
    
-   canonical periodic bond topology
    
-   same-cell bonds
    
-   cross-boundary bonds
    
-   self-periodic bonds
    
-   triclinic periodic geometry
    
-   neighbor inspector
    
-   atom instancing
    
-   shared bond geometry
    
-   bounded draw calls
    
-   lifecycle cleanup
    
-   stale scene protection
    
-   context-loss fallback
    
-   keyboard navigation
    
-   focus management
    
-   screen-reader scene summary
    
-   mobile rotate / pan / pinch / tap基础
    
-   semantic inspector table
    
-   degraded mode
    
-   over-budget JSON-only fallback
    
-   browser matrix
    
-   no artifact JS
    
-   no external resources
    

当前尚未充分实现或证明：

-   atom ray picking的完整periodic identity
    
-   bond picking
    
-   selection state model
    
-   multi-selection上限
    
-   selection order
    
-   selection history
    
-   distance measurement
    
-   angle measurement
    
-   dihedral measurement
    
-   periodic displacement policy
    
-   shortest-image与explicit-image区别
    
-   triclinic measurement数学
    
-   self-periodic measurement
    
-   selection在scene切换后清理
    
-   selection在supercell instances之间的身份一致性
    
-   keyboard-only picking替代路径
    
-   mobile picking精度
    
-   measurement accessibility
    
-   measurement persistence/artifact
    
-   measurement security与caps
    
-   browser evidence
    

----------

# 2. 本阶段目标

必须完成以下九类工作：

1.  **Picking architecture audit**
    
2.  **Canonical selection identity**
    
3.  **Atom and bond picking**
    
4.  **Bounded multi-selection**
    
5.  **Distance measurement**
    
6.  **Angle and dihedral measurement**
    
7.  **Periodic geometry policy**
    
8.  **Measurement UI / accessibility / mobile behavior**
    
9.  **Tests、evidence、docs和readiness收口**
    

本阶段必须产生实际实现代码。

如果最终只有docs、测试fixture或静态measurement示例，没有真实viewer interaction path，本阶段必须判定为FAIL。

----------

# 3. 严格禁止范围

本阶段不得实现：

-   structure editing
    
-   add/remove atom
    
-   move atom
    
-   change species
    
-   change occupancy
    
-   lattice editing
    
-   bond editing
    
-   topology editing
    
-   trajectory
    
-   phonon
    
-   Brillouin zone
    
-   volumetric rendering
    
-   charge density
    
-   spin density
    
-   isosurface
    
-   defects
    
-   surfaces
    
-   slabs
    
-   persisted supercell productization
    
-   clipping plane
    
-   PNG/PDF export
    
-   glTF/GLB export
    
-   collaborative annotations
    
-   external API
    
-   notebook execution
    
-   script execution
    
-   real LLM
    
-   formal `structure.viewer_3d` registration
    

不得：

-   修改periodic endpoint identity
    
-   修改canonical periodic bond key
    
-   修改v2 topology semantics
    
-   修改`1e-5 Å` bond distance tolerance
    
-   重新推断canonical bonds
    
-   将measurement结果写回scene topology
    
-   将measurement结果标记为authoritative chemistry
    
-   放宽validator caps
    
-   修改QueueWorkerRuntime主语义
    
-   修改AnalysisPlanRepository主语义
    
-   修改`/planner/jobs`主语义
    
-   引入新的renderer framework
    
-   引入artifact-controlled picking callbacks
    
-   引入artifact-controlled shader
    
-   引入artifact-controlled event handler
    
-   引入remote assets
    
-   允许unbounded selection
    
-   允许unbounded measurement history
    
-   允许hover持续创建measurement对象
    
-   通过只测试same-cell结构伪造periodic measurement完成
    
-   将错误的minimum-image规则用于triclinic晶格
    
-   将screen-space距离当作科学距离
    

允许：

-   raycaster/picking internals重构
    
-   instance-id映射
    
-   bond segment picking
    
-   selection state model
    
-   bounded measurement state
    
-   application-owned math helpers
    
-   measurement artifacts
    
-   inspector扩展
    
-   accessibility和mobile交互
    
-   tests
    
-   browser evidence
    
-   docs
    
-   persistent updates
    

----------

# 4. 必读实现

开始后直接阅读当前真实代码。

## 4.1 Viewer / Picking

搜索：

```bash
rg -n "Raycaster|raycast|instanceId|pointerdown|pointerup|selection|selected|highlight|neighbor|PeriodicSiteRef" apps/web

```

重点确认：

-   atom instanced mesh
    
-   instance ID映射
    
-   periodic site reference
    
-   bond line geometry
    
-   pointer/touch click区分
    
-   camera drag与pick冲突
    
-   highlight geometry
    
-   selected state
    
-   inspector state
    
-   keyboard selection入口
    
-   lifecycle cleanup
    

## 4.2 Periodic Math

定位并阅读：

-   lattice row/column convention
    
-   fractional → Cartesian conversion
    
-   Cartesian → fractional conversion
    
-   lattice inverse
    
-   determinant/condition checks
    
-   periodic offset handling
    
-   triclinic tests
    
-   endpoint distance validation
    
-   self-periodic bond tests
    

## 4.3 Existing Inspector

检查：

-   selected atom panel
    
-   neighbor table
    
-   periodic identity文本
    
-   keyboard activation
    
-   mobile layout
    
-   semantic roles
    
-   focus restoration
    
-   row cap
    

## 4.4 Performance / Accessibility

确认：

-   selection不会触发全scene rebuild
    
-   highlight geometry bounded
    
-   keyboard interaction contract
    
-   mobile pointer/touch contract
    
-   reduced-motion behavior
    
-   cross-browser event model
    

----------

# 5. 修改前输出审计

修改代码前输出：

# Phase 10F-23 Advanced Picking and Measurement Pre-Implementation Audit

## 1. Current Picking Path

-   atom picking:
    
-   bond picking:
    
-   instance mapping:
    
-   pointer/touch handling:
    
-   drag-vs-click detection:
    
-   keyboard alternative:
    
-   highlight:
    
-   cleanup:
    

## 2. Current Selection Model

-   single selection:
    
-   multi-selection:
    
-   selected atom identity:
    
-   selected bond identity:
    
-   selection ordering:
    
-   selection cap:
    
-   scene-switch behavior:
    
-   inspector coupling:
    

## 3. Current Periodic Mathematics

-   lattice convention:
    
-   fractional-to-Cartesian:
    
-   Cartesian-to-fractional:
    
-   offset semantics:
    
-   endpoint distance:
    
-   triclinic handling:
    
-   condition/determinant guard:
    
-   missing helpers:
    

## 4. Measurement Risks

至少列出：

-   wrong periodic image
    
-   wrong shortest image
    
-   triclinic minimum-image error
    
-   ambiguous self-periodic endpoint
    
-   instance ID drift
    
-   stale selection
    
-   scene switching
    
-   duplicate selection
    
-   selection order loss
    
-   unbounded history
    
-   camera drag misclassified as click
    
-   mobile tap ambiguity
    
-   line picking tolerance
    
-   screen-space vs world-space confusion
    
-   nonfinite coordinates
    
-   invalid lattice
    

## 5. Selected Strategy

说明：

-   selection identity:
    
-   atom picking:
    
-   bond picking:
    
-   multi-selection:
    
-   distance:
    
-   angle:
    
-   dihedral:
    
-   periodic policy:
    
-   artifact:
    
-   accessibility:
    
-   mobile:
    
-   caps:
    

## 6. Planned Files

列出预计修改或新增：

-   viewer
    
-   picking helper
    
-   measurement math
    
-   selection state
    
-   inspector
    
-   styles
    
-   tests
    
-   browser runner
    
-   fixtures
    
-   evidence
    
-   docs
    
-   persistent
    

审计后直接继续实现。

----------

# 6. Canonical Selection Identity

建立application-owned selection identity。

至少支持：

## 6.1 Atom Selection

```ts
type AtomSelection = {
  kind: "atom";
  siteIndex: number;
  imageOffset: [number, number, number];
  instanceId: number;
};

```

要求：

-   `siteIndex + imageOffset`是科学身份
    
-   `instanceId`仅是当前render instance索引
    
-   scene rebuild后不得依赖旧instanceId恢复身份
    
-   selection key必须deterministic
    
-   offset必须integer且bounded
    
-   selection必须指向当前scene中的合法displayed instance
    

推荐key：

```text
atom:<siteIndex>@[dx,dy,dz]

```

## 6.2 Bond Selection

```ts
type BondSelection = {
  kind: "bond";
  canonicalKey: string;
  from: PeriodicSiteRef;
  to: PeriodicSiteRef;
};

```

要求：

-   canonical key与Phase 10F-18一致
    
-   reversal不得产生第二身份
    
-   same-cell/cross-boundary/self-periodic均支持
    
-   bond selection不得重新计算topology
    
-   必须来自validated displayed bond mapping
    

## 6.3 Selection Serialization

selection state如需进入measurement artifact，必须使用：

-   canonical site identity
    
-   canonical bond key
    
-   stable order
    
-   no renderer-private object
    
-   no Three.js object reference
    
-   no callback/function
    
-   no raw pointer event
    

----------

# 7. Selection State Model

## 7.1 Modes

至少支持：

```text
inspect
measure_distance
measure_angle
measure_dihedral

```

不建议在本阶段加入自由lasso或box selection。

## 7.2 Selection Caps

必须定义：

-   inspect mode：1个主selection
    
-   distance：2个atom
    
-   angle：3个atom
    
-   dihedral：4个atom
    
-   general bounded selection：不得超过4，除非有明确UI需求
    

不允许无限选择。

## 7.3 Ordering

measurement selection order必须保留：

-   distance：A → B
    
-   angle：A → B → C，B为顶点
    
-   dihedral：A → B → C → D
    

去重规则：

-   同一periodic atom重复点击不得偷偷改变order
    
-   可以切换/取消，但行为必须明确
    
-   same canonical site不同image offset视为不同periodic atom
    
-   same periodic identity重复选择必须按当前mode明确处理
    

## 7.4 Clear / Undo

至少支持：

-   clear all
    
-   remove last selected point
    
-   Escape清除当前measurement draft
    
-   scene切换自动清除
    
-   artifact切换自动清除
    
-   context loss可保留或清除，但必须选择固定策略并记录
    
-   invalid scene/fallback必须清除renderer selection
    

----------

# 8. Atom Picking

## 8.1 Instanced Atom Picking

必须使用：

-   raycaster intersection
    
-   `instanceId`
    
-   immutable `instanceId → PeriodicSiteRef` mapping
    

要求：

-   mapping在scene build后冻结
    
-   scene切换时替换
    
-   stale mapping不得使用
    
-   invalid instanceId拒绝
    
-   hidden atom不可选
    
-   over-budget JSON-only无picking
    
-   degraded mode若禁用hover，click picking仍可按policy工作
    

## 8.2 Click vs Drag

必须区分：

-   camera rotate drag
    
-   camera pan drag
    
-   tap/click selection
    

建议application-owned阈值：

-   pointer displacement
    
-   duration
    
-   pointer count
    

要求：

-   阈值固定且可测试
    
-   不由artifact控制
    
-   mouse/touch/pen一致
    
-   drag结束不得误pick
    
-   pinch结束不得误pick
    
-   pointercancel不得触发pick
    

## 8.3 Hover

hover不是本阶段必需。

若保留hover：

-   不得作为唯一信息入口
    
-   不得写入measurement selection
    
-   不得连续创建geometry/material
    
-   mobile不依赖hover
    
-   reduced-motion下不闪烁
    

----------

# 9. Bond Picking

当前bond通常使用shared `LineSegments`，bond picking需要明确实现。

允许策略：

1.  使用Three.js line raycasting并设置application-owned threshold
    
2.  使用bounded spatial helper
    
3.  使用独立但共享的pick geometry
    

要求：

-   不允许每bond创建独立DOM或Mesh
    
-   raycast result必须映射回displayed bond index
    
-   displayed bond index必须映射到canonical bond key
    
-   threshold application-owned
    
-   threshold不能由artifact控制
    
-   same-cell/cross-boundary/self-periodic均测试
    
-   line交叉时选择结果deterministic，或明确nearest rule
    
-   bond picking不得影响draw-call budget
    
-   bond highlight资源bounded
    

----------

# 10. Measurement Mathematics

所有measurement必须使用世界空间Cartesian坐标。

不得使用：

-   screen-space pixels
    
-   projected NDC distance
    
-   camera-space distance
    
-   rounded preview text反算
    

## 10.1 Atom Position

对每个PeriodicSiteRef：

```text
cartesian =
fractional_site_position
+ image_offset lattice translation

```

使用项目既定row lattice convention。

必须复用现有受测数学helper，避免另写冲突公式。

## 10.2 Distance

定义：

```text
distance(A, B) = ||cart(B) - cart(A)||

```

输出单位：

```text
Å

```

要求：

-   finite
    
-   nonnegative
    
-   deterministic precision
    
-   explicit endpoint identity
    
-   explicit image offsets
    

## 10.3 Angle

对A-B-C，B为顶点：

```text
u = A - B
v = C - B

angle = acos(
  dot(u,v) / (|u||v|)
)

```

输出：

```text
degrees

```

要求：

-   range `[0,180]`
    
-   zero-length vector拒绝
    
-   clamp acos input至`[-1,1]`
    
-   nonfinite拒绝
    
-   exact endpoint order保留
    

## 10.4 Dihedral

对A-B-C-D：

-   plane 1：A-B-C
    
-   plane 2：B-C-D
    
-   使用稳定signed dihedral公式
    
-   输出范围必须固定选择：
    
    -   `[-180,180]`
        
    -   或 `[0,360)`
        

必须在contract中固定一种。

推荐：

```text
[-180, 180] degrees

```

要求：

-   collinear/degenerate拒绝
    
-   zero central bond拒绝
    
-   deterministic sign convention
    
-   tests覆盖正角、负角、180、0附近
    
-   triclinic periodic images覆盖
    

----------

# 11. Periodic Measurement Policy

这是本阶段的核心科学边界。

必须明确区分两类measurement。

## 11.1 Explicit Image Measurement

用户选择的是显示实例：

```text
siteIndex@[imageOffset]

```

measurement默认使用这些明确实例的Cartesian位置。

这意味着：

-   不自动替换成另一周期映像
    
-   结果反映用户实际选中的displayed atoms
    
-   supercell/neighbor image identity保持
    

推荐默认模式：

```text
explicit_displayed_images

```

## 11.2 Shortest-Image Measurement

可以作为可选secondary mode，但必须严格受控。

若实现：

-   只用于两个canonical sites之间的minimum-image distance
    
-   必须对triclinic晶格使用正确数学
    
-   不得简单逐分量round fractional delta后假设总是正确，除非已证明当前晶格范围下正确
    
-   推荐使用bounded lattice image search或现有pymatgen/helper
    
-   search offset必须受cap限制
    
-   返回chosen relative image offset
    
-   明确标记结果为minimum-image
    

如果无法可靠实现triclinic shortest image：

-   本阶段只实现explicit displayed image measurement
    
-   shortest-image标记为deferred
    
-   不得用错误近似伪造完成
    

## 11.3 Self-Periodic Measurement

允许：

```text
same siteIndex
different nonzero imageOffset

```

例如晶格周期长度测量。

必须拒绝：

```text
same siteIndex
same imageOffset

```

用于distance时结果为零且无科学价值，除非UI明确允许显示0；建议typed rejection或warning。

----------

# 12. Numeric Precision and Tolerance

建立measurement numeric policy。

建议：

-   internal calculation：double precision
    
-   artifact values：固定小数位或canonical rounding
    
-   UI display：
    
    -   distance：6 decimal places或项目一致精度
        
    -   angle：6 decimal places
        
    -   dihedral：6 decimal places
        
-   JSON不得包含NaN/Infinity
    
-   negative zero规范化为`0`
    
-   repeated calculation必须稳定
    
-   frontend和backend reference math必须一致
    

measurement不是bond validation，因此不要直接复用`1e-5 Å`作为所有结果显示精度。

但若选中已存在bond：

-   measured distance可与canonical bond distance对照
    
-   差值应在现有bond tolerance内
    
-   mismatch必须显示内部错误，不得静默覆盖
    

----------

# 13. Measurement Result Contract

建立application-owned measurement result。

建议：

```json
{
  "schema_version": "phase10f23.viewer_measurement.v1",
  "scene_schema_version": "phase10f18.viewer_scene.v2",
  "measurement_type": "distance",
  "selection_mode": "explicit_displayed_images",
  "points": [
    {
      "site_index": 0,
      "image_offset": [0, 0, 0]
    },
    {
      "site_index": 1,
      "image_offset": [1, 0, 0]
    }
  ],
  "value": 0.4,
  "unit": "angstrom",
  "warnings": [],
  "security": {
    "contains_javascript": false,
    "external_urls": []
  }
}

```

angle/dihedral使用同一contract变体。

必须包含：

-   schema version
    
-   scene schema version
    
-   scene/artifact identity，按项目安全方式
    
-   measurement type
    
-   selection mode
    
-   ordered points
    
-   value
    
-   unit
    
-   warnings
    
-   deterministic flag
    
-   security metadata
    

不得包含：

-   Three.js object
    
-   camera
    
-   ray
    
-   screen coordinates
    
-   raw pointer event
    
-   callback
    
-   function
    
-   HTML
    
-   URL
    
-   shader
    
-   executable content
    

----------

# 14. Measurement UI

## 14.1 Mode Controls

提供明确控件：

-   Inspect
    
-   Distance
    
-   Angle
    
-   Dihedral
    

要求：

-   keyboard accessible
    
-   touch target满足Phase 10F-22标准
    
-   current mode有text和semantic state
    
-   不只靠颜色
    
-   mode切换时清除不兼容draft
    
-   mode不能由artifact控制
    

## 14.2 Selection Progress

显示：

```text
Distance: select point 1 of 2
Angle: select point 2 of 3
Dihedral: select point 3 of 4

```

必须可被live region适度播报。

不得在pointer move时播报。

## 14.3 Result Panel

显示：

-   measurement type
    
-   ordered endpoint identities
    
-   element/species
    
-   image offsets
    
-   value
    
-   unit
    
-   explicit/shortest-image mode
    
-   warning
    
-   clear
    
-   undo
    
-   save/export result，若本阶段实现measurement artifact download
    

## 14.4 Visual Overlay

允许显示：

-   selected atom markers
    
-   measurement line
    
-   angle arc的简化表示
    
-   dihedral连接线
    
-   labels
    

要求：

-   bounded geometry/material
    
-   application-owned style
    
-   不改变scene topology
    
-   不写回artifact scene
    
-   selection清除时dispose
    
-   scene切换时dispose
    
-   reduced-motion下无动画
    
-   high contrast可见
    
-   不只靠颜色
    

----------

# 15. Multi-Selection

本阶段只实现measurement-driven bounded multi-selection。

不得实现：

-   arbitrary unlimited multi-select
    
-   lasso
    
-   box selection
    
-   select all
    
-   thousands-of-atoms selection
    

要求：

-   cap = 4
    
-   order stable
    
-   duplicates按policy处理
    
-   UI显示序号1–4
    
-   keyboard可移除最后一个
    
-   clear all
    
-   scene切换清理
    
-   selection geometry固定上限
    
-   live region bounded
    

----------

# 16. Keyboard Picking

核心interaction必须有非pointer替代路径。

至少实现一种：

## Strategy A：Inspector-driven Selection

-   通过semantic atom/neighbor list选择
    
-   Enter/Space加入measurement
    
-   selected order显示
    
-   focus保持
    

## Strategy B：Current Atom Navigation

-   在bounded atom list中搜索/选择
    
-   不将所有displayed atoms直接放入tab order
    
-   使用filter或index输入
    

优先复用现有inspector。

必须支持：

-   keyboard选中atom
    
-   keyboard添加neighbor到measurement
    
-   keyboard undo
    
-   keyboard clear
    
-   mode切换
    
-   result读取
    

不要求键盘在3D空间中逐原子移动焦点。

----------

# 17. Mobile Picking

必须测试：

-   tap atom
    
-   tap bond
    
-   tap vs rotate
    
-   tap vs pinch
    
-   double event suppression
    
-   pointercancel
    
-   touch target mode controls
    
-   measurement progress
    
-   result panel
    
-   clear/undo
    
-   orientation change
    

要求：

-   tap精度合理
    
-   picking threshold application-owned
    
-   不因高DPI失效
    
-   不因viewport变化错位
    
-   canvas CSS尺寸与drawing buffer坐标转换正确
    
-   portrait/landscape均可用
    
-   inspector/result panel不遮挡且可关闭
    

----------

# 18. Lifecycle and State Safety

必须处理：

-   scene switch
    
-   artifact switch
    
-   schema switch
    
-   renderer → JSON-only
    
-   context loss
    
-   context restore
    
-   degraded mode
    
-   over-budget fallback
    
-   component unmount
    
-   browser back/forward，若相关
    
-   mobile orientation
    
-   invalid scene
    

要求：

-   stale selection清除
    
-   stale measurement清除
    
-   stale overlay dispose
    
-   no duplicate event listeners
    
-   no duplicate highlight geometry
    
-   no previous scene identity残留
    
-   no measurement跨scene错误复用
    

如果希望保留measurement历史，必须绑定scene artifact hash；否则默认scene切换清空。

本阶段推荐：

```text
scene switch clears active selection and measurement draft

```

----------

# 19. Typed Errors and Warnings

至少覆盖：

```text
VIEWER_PICK_INSTANCE_NOT_FOUND
VIEWER_PICK_BOND_NOT_FOUND
VIEWER_SELECTION_DUPLICATE
VIEWER_SELECTION_LIMIT_REACHED
VIEWER_MEASUREMENT_INCOMPLETE
VIEWER_MEASUREMENT_DEGENERATE
VIEWER_MEASUREMENT_NONFINITE
VIEWER_MEASUREMENT_INVALID_LATTICE
VIEWER_MEASUREMENT_SCENE_CHANGED
VIEWER_MEASUREMENT_UNSUPPORTED_SCHEMA
VIEWER_MEASUREMENT_SHORTEST_IMAGE_NOT_AVAILABLE

```

错误必须：

-   application-owned
    
-   deterministic
    
-   sanitized
    
-   no stack
    
-   no private path
    
-   no raw artifact payload
    
-   no secret
    

warning ordering必须stable。

----------

# 20. Tests

## 20.1 Selection Identity Tests

覆盖：

-   same-cell atom
    
-   cross-boundary atom
    
-   same canonical site不同offset
    
-   self-periodic identity
    
-   invalid instanceId
    
-   stale instanceId
    
-   duplicate selection
    
-   selection order
    
-   cap
    

## 20.2 Atom Picking Tests

覆盖：

-   InstancedMesh hit
    
-   miss
    
-   hidden atom
    
-   click vs drag
    
-   pointercancel
    
-   touch tap
    
-   high-DPI coordinate conversion
    
-   scene switch
    

## 20.3 Bond Picking Tests

覆盖：

-   same-cell bond
    
-   cross-boundary bond
    
-   self-periodic bond
    
-   intersecting lines
    
-   nearest selection rule
    
-   invalid displayed index
    
-   canonical key mapping
    
-   highlight cleanup
    

## 20.4 Distance Tests

覆盖：

-   orthogonal same-cell
    
-   orthogonal cross-boundary
    
-   triclinic
    
-   self-periodic
    
-   same identity
    
-   nonfinite
    
-   invalid lattice
    
-   bond distance comparison
    
-   deterministic precision
    

## 20.5 Angle Tests

覆盖：

-   90°
    
-   60°
    
-   180°
    
-   near-0°
    
-   cross-boundary
    
-   triclinic
    
-   degenerate
    
-   duplicate point
    

## 20.6 Dihedral Tests

覆盖：

-   0°
    
-   positive
    
-   negative
    
-   180°
    
-   triclinic periodic images
    
-   collinear
    
-   zero central bond
    
-   sign convention
    
-   deterministic replay
    

## 20.7 Shortest-Image Tests

仅当实现时：

-   orthogonal
    
-   triclinic
    
-   skewed lattice
    
-   boundary case
    
-   chosen offset
    
-   bounded search
    
-   explicit vs minimum-image difference
    

若不实现，测试：

-   feature unavailable
    
-   typed warning
    
-   no approximate result
    

## 20.8 UI Tests

覆盖：

-   mode controls
    
-   progress
    
-   undo
    
-   clear
    
-   result
    
-   keyboard selection
    
-   live region
    
-   mobile controls
    
-   focus restoration
    
-   result semantics
    

## 20.9 Lifecycle Tests

覆盖：

-   scene switch
    
-   invalid scene
    
-   legacy JSON-only
    
-   context loss
    
-   unmount
    
-   orientation change
    
-   selection overlay disposal
    
-   no resource growth
    

## 20.10 Regression

必须保持：

-   Phase 10F-18 canonical topology
    
-   Phase 10F-19 integration
    
-   Phase 10F-20 compatibility
    
-   Phase 10F-21 performance budgets
    
-   Phase 10F-22 accessibility/mobile
    
-   no external network
    
-   no artifact JS
    

----------

# 21. Reference Mathematics

必须建立独立reference tests。

推荐使用：

-   backend Python reference
    
-   frontend TypeScript implementation
    

对同一fixtures验证：

-   periodic Cartesian positions
    
-   distance
    
-   angle
    
-   dihedral
    
-   selected offsets
    
-   rounding
    

必须记录frontend/backend差值。

不能只用同一实现生成expected再测试自己。

至少包括：

-   orthogonal lattice
    
-   triclinic lattice
    
-   ill-conditioned lattice rejection
    
-   self-periodic vector
    
-   cross-boundary bond
    
-   signed dihedral
    

----------

# 22. Browser Evidence

新增：

```text
docs/phase10f/evidence/phase10f23_advanced_picking_measurement/

```

必须使用真实浏览器。

## 22.1 Chromium

覆盖：

-   atom picking
    
-   bond picking
    
-   distance
    
-   angle
    
-   dihedral
    
-   keyboard-driven measurement
    
-   cross-boundary
    
-   triclinic
    
-   self-periodic
    
-   clear/undo
    
-   scene switch cleanup
    
-   context loss cleanup
    

## 22.2 Firefox

至少覆盖：

-   atom picking
    
-   bond picking
    
-   distance
    
-   angle
    
-   keyboard
    
-   lifecycle
    

## 22.3 WebKit

至少覆盖：

-   atom picking
    
-   touch/pointer behavior
    
-   distance
    
-   inspector
    
-   lifecycle
    

## 22.4 Mobile

至少覆盖：

-   tap atom
    
-   tap bond
    
-   tap vs rotate
    
-   distance measurement
    
-   clear
    
-   undo
    
-   orientation change
    
-   result panel
    
-   no duplicate event
    

----------

# 23. Evidence Assertions

每个browser evidence记录：

-   browser version
    
-   viewport
    
-   device class
    
-   schema version
    
-   scene fixture
    
-   input mode
    
-   selection mode
    
-   ordered selected identities
    
-   measurement value
    
-   unit
    
-   warnings
    
-   canvas count
    
-   context count
    
-   geometry/material counts
    
-   console errors
    
-   network requests
    

必须验证：

-   exact periodic identity
    
-   exact selection order
    
-   correct cross-boundary offset
    
-   correct triclinic value
    
-   bond canonical key
    
-   no drag mis-pick
    
-   no pinch mis-pick
    
-   no duplicate selection event
    
-   no stale scene selection
    
-   no overlay leak
    
-   no external network
    
-   no artifact JS
    

----------

# 24. Evidence Files

建议至少包含：

```text
README.md
selection_contract.json
measurement_contract.json
periodic_measurement_policy.json
atom_picking_results.json
bond_picking_results.json
distance_reference.json
angle_reference.json
dihedral_reference.json
frontend_backend_math_comparison.json
keyboard_measurement.json
mobile_measurement.json
scene_switch_cleanup.json
context_loss_cleanup.json
resource_metrics.json
browser_matrix.json
console_audit.json
network_audit.json
security_audit.json
artifact_hashes.json

```

截图建议：

```text
01_atom_selected.png
02_cross_boundary_atom_identity.png
03_bond_selected.png
04_distance_measurement.png
05_angle_measurement.png
06_dihedral_measurement.png
07_self_periodic_measurement.png
08_keyboard_measurement.png
09_mobile_distance_measurement.png
10_measurement_cleared.png

```

不得保存：

-   raw pointer logs containing excessive device data
    
-   private paths
    
-   browser profile secrets
    
-   large traces
    
-   remote URLs
    
-   cache
    
-   crash dumps
    
-   full scene payload duplicates
    

----------

# 25. Measurement Artifact

本阶段建议生成可下载的纯JSON measurement artifact。

文件名建议：

```text
viewer_measurement.json

```

要求：

-   inert JSON
    
-   no renderer bundle
    
-   no JS
    
-   no external URL
    
-   no HTML
    
-   deterministic serialization
    
-   canonical point ordering
    
-   scene identity/provenance
    
-   calculation policy
    
-   numeric precision
    
-   warnings
    
-   security metadata
    

可选生成：

```text
measurement_summary.md

```

内容：

-   type
    
-   points
    
-   periodic offsets
    
-   value
    
-   unit
    
-   policy
    
-   warnings
    
-   no structure mutation
    
-   no topology mutation
    

不要修改原始viewer scene artifact。

----------

# 26. Security

必须验证：

-   no artifact JavaScript
    
-   no artifact HTML
    
-   no artifact event handler
    
-   no artifact callback
    
-   no artifact shader
    
-   no artifact module
    
-   no eval
    
-   no Function constructor
    
-   no external URL
    
-   no remote texture
    
-   no CDN
    
-   no iframe
    
-   no arbitrary local file access
    
-   no notebook execution
    
-   no script execution
    
-   no real LLM
    
-   no dependency addition
    
-   no unbounded selection
    
-   no unbounded measurement history
    
-   no artifact-controlled picking threshold
    
-   no artifact-controlled keyboard binding
    
-   no artifact-controlled selection cap
    
-   no artifact-controlled overlay geometry
    
-   no measurement result writes to topology
    
-   no screen-space scientific calculation
    
-   no telemetry upload
    
-   no raw pointer-event persistence
    

必须输出：

```text
NO_EXTERNAL_NETWORK_REQUESTS
NO_SECRET_PATTERN_HITS

```

----------

# 27. Performance Requirements

必须保持Phase 10F-21预算。

要求：

-   selection overlay geometry ≤ fixed cap
    
-   measurement points ≤ 4
    
-   measurement lines ≤ fixed cap
    
-   angle/dihedral helper geometry bounded
    
-   no per-frame geometry creation
    
-   no full scene rebuild on selection
    
-   no new atom/bond materials per selection
    
-   highlight materials复用
    
-   picking events on-demand
    
-   no continuous raycasting loop
    
-   no hover raycast on mobile
    
-   scene switch cleanup恢复resource baseline
    
-   draw calls增长固定且明确
    

必须记录：

-   selection前后draw calls
    
-   geometries
    
-   materials
    
-   active loops
    
-   cleanup后恢复
    

----------

# 28. Accessibility Requirements

必须保持Phase 10F-22标准。

要求：

-   mode controls keyboard accessible
    
-   selection progress可读
    
-   exact periodic identities可读
    
-   result可读
    
-   unit可读
    
-   warning可读
    
-   clear/undo键盘可用
    
-   focus-visible
    
-   live region bounded
    
-   no hover-only
    
-   no color-only
    
-   mobile touch targets合格
    
-   200% zoom可用
    
-   result panel可关闭
    
-   scene switch focus恢复
    

----------

# 29. Dependency Policy

默认不新增依赖。

优先使用：

-   Three.js Raycaster
    
-   existing math helpers
    
-   application-owned vector math
    
-   existing Playwright
    
-   existing test utilities
    

检查：

```bash
npm --prefix apps/web ls --depth=0
npm --prefix apps/web run build

```

记录：

-   dependency tree
    
-   lockfile
    
-   bundle size
    
-   renderer chunk变化
    

不得为了简单vector math引入大型数学库。

----------

# 30. Docs / Persistent

新增或更新：

```text
docs/phase10f/phase10f23_advanced_picking_measurement.md
docs/phase10f/phase10f23_selection_identity_contract.md
docs/phase10f/phase10f23_periodic_measurement_contract.md
docs/phase10f/phase10f23_measurement_mathematics.md
docs/phase10f/phase10f23_measurement_security.md
docs/phase10f/phase10f23_measurement_evidence.md
docs/phase10f/phase10f23_measurement_readiness_matrix.md

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

-   selection identity
    
-   atom picking
    
-   bond picking
    
-   selection caps
    
-   explicit-image policy
    
-   shortest-image decision
    
-   distance/angle/dihedral formulas
    
-   precision
    
-   typed errors
    
-   lifecycle
    
-   accessibility
    
-   performance
    
-   remaining supercell work
    
-   remaining clipping/export
    
-   formal viewer registration仍未完成
    

----------

# 31. Readiness Matrix

最终分别判断：

-   atom picking
    
-   bond picking
    
-   instance mapping
    
-   periodic identity
    
-   single selection
    
-   bounded multi-selection
    
-   selection ordering
    
-   distance measurement
    
-   angle measurement
    
-   dihedral measurement
    
-   explicit-image policy
    
-   shortest-image policy
    
-   triclinic math
    
-   self-periodic measurement
    
-   keyboard measurement
    
-   mobile measurement
    
-   measurement artifact
    
-   lifecycle cleanup
    
-   performance
    
-   accessibility
    
-   Chromium
    
-   Firefox
    
-   WebKit
    
-   mobile
    
-   full `structure.viewer_3d`
    
-   supercell productization
    
-   clipping
    
-   export
    
-   trajectory
    
-   phonon
    
-   Brillouin zone
    
-   volumetric
    

推荐期望：

```text
atom picking: READY
bond picking: READY
periodic identity: READY
single selection: READY
bounded multi-selection: READY
distance measurement: READY
angle measurement: READY
dihedral measurement: READY
explicit-image policy: READY
shortest-image policy: READY or DEFERRED_BY_DESIGN
triclinic math: READY
self-periodic measurement: READY
keyboard measurement: READY
mobile measurement: READY
measurement artifact: READY
lifecycle cleanup: READY
performance: READY
accessibility: READY
browser matrix: READY
full structure.viewer_3d: PARTIAL_READY
supercell productization: NOT_READY
clipping: NOT_READY
export: NOT_READY
trajectory: NOT_READY
phonon: NOT_READY
Brillouin zone: NOT_READY
volumetric: NOT_READY

```

若shortest-image未实现但明确拒绝错误近似，本阶段仍可PASS。

----------

# 32. Checks

至少运行：

```bash
git diff --check
uv lock --check

npm --prefix apps/web test
npm --prefix apps/web run typecheck
npm --prefix apps/web run build

uv run python -m pytest -q

```

并运行：

-   selection identity tests
    
-   atom picking tests
    
-   bond picking tests
    
-   distance tests
    
-   angle tests
    
-   dihedral tests
    
-   periodic math reference tests
    
-   frontend/backend comparison
    
-   keyboard tests
    
-   mobile tests
    
-   lifecycle stress
    
-   performance regression
    
-   accessibility regression
    
-   Chromium runner
    
-   Firefox runner
    
-   WebKit runner
    
-   mobile runner
    
-   service-backed integration
    
-   no-skipped assertion
    
-   secret scan
    
-   network audit
    

必须如实记录：

-   passed
    
-   failed
    
-   skipped
    
-   unavailable
    

不得把skipped写成passed。

----------

# 33. Commit / CI

完成实现、测试、evidence和文档后：

```bash
git status --short
git diff --stat
git add <only Phase 10F-23 related files>
git commit -m "Add periodic picking and measurements"
git push origin master

```

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

# 34. 最终报告格式

完成后输出：

# Phase 10F-23 Advanced Picking and Measurement Result

## 1. Conclusion

PASS / PARTIAL_PASS / FAIL

## 2. Baseline

-   Phase 10F-22 assumed complete:
    
-   branch:
    
-   initial status:
    
-   final HEAD:
    
-   final status:
    

## 3. Picking Architecture

-   atom picking:
    
-   bond picking:
    
-   instance mapping:
    
-   click-vs-drag:
    
-   touch handling:
    
-   cleanup:
    

## 4. Selection Identity

-   atom key:
    
-   bond key:
    
-   periodic identity:
    
-   instance identity:
    
-   ordering:
    
-   cap:
    
-   duplicate policy:
    

## 5. Selection Modes

-   inspect:
    
-   distance:
    
-   angle:
    
-   dihedral:
    
-   undo:
    
-   clear:
    
-   scene switch:
    

## 6. Measurement Mathematics

-   lattice convention:
    
-   atom position:
    
-   distance:
    
-   angle:
    
-   dihedral:
    
-   precision:
    
-   degeneracy:
    
-   reference implementation:
    

## 7. Periodic Policy

-   explicit displayed images:
    
-   shortest image:
    
-   cross-boundary:
    
-   self-periodic:
    
-   triclinic:
    
-   warnings:
    

## 8. Atom Picking

-   instanced mesh:
    
-   periodic mapping:
    
-   hidden atoms:
    
-   stale mapping:
    
-   high-DPI:
    
-   mobile:
    

## 9. Bond Picking

-   shared line geometry:
    
-   canonical bond mapping:
    
-   cross-boundary:
    
-   self-periodic:
    
-   threshold:
    
-   highlight:
    

## 10. Measurement UI

-   mode controls:
    
-   progress:
    
-   result:
    
-   point identities:
    
-   undo:
    
-   clear:
    
-   overlay:
    
-   accessibility:
    

## 11. Measurement Artifact

-   schema:
    
-   filename:
    
-   deterministic:
    
-   provenance:
    
-   security:
    
-   structure mutation:
    
-   topology mutation:
    

## 12. Reference Results

-   orthogonal distance:
    
-   cross-boundary distance:
    
-   triclinic distance:
    
-   self-periodic:
    
-   angle:
    
-   dihedral:
    
-   frontend/backend difference:
    

## 13. Lifecycle

-   scene switch:
    
-   artifact switch:
    
-   context loss:
    
-   context restore:
    
-   unmount:
    
-   orientation:
    
-   overlay disposal:
    
-   resource baseline:
    

## 14. Browser Evidence

-   Chromium:
    
-   Firefox:
    
-   WebKit:
    
-   mobile:
    
-   keyboard:
    
-   touch:
    
-   context loss:
    
-   console:
    
-   network:
    

## 15. Performance

-   selection draw calls:
    
-   geometries:
    
-   materials:
    
-   active loops:
    
-   raycasting:
    
-   cleanup:
    
-   budgets:
    

## 16. Accessibility

-   keyboard selection:
    
-   live region:
    
-   exact periodic identity:
    
-   result semantics:
    
-   focus:
    
-   mobile controls:
    
-   zoom/high contrast:
    

## 17. Security

-   artifact callbacks:
    
-   thresholds:
    
-   caps:
    
-   scientific calculation:
    
-   external resources:
    
-   dependencies:
    
-   secrets:
    
-   network:
    

## 18. Evidence

-   directory:
    
-   selection contract:
    
-   measurement contract:
    
-   reference math:
    
-   browser matrix:
    
-   screenshots:
    
-   markers:
    

## 19. Tests

-   picking:
    
-   distance:
    
-   angle:
    
-   dihedral:
    
-   frontend full:
    
-   backend full:
    
-   typecheck:
    
-   build:
    
-   browser:
    
-   mobile:
    
-   service-backed:
    
-   no-skipped:
    
-   lock:
    
-   diff:
    

## 20. Files

-   viewer:
    
-   picking:
    
-   math:
    
-   selection:
    
-   inspector:
    
-   tests:
    
-   browser runners:
    
-   evidence:
    
-   docs:
    
-   persistent:
    
-   dependencies/lockfile:
    

## 21. Deferred

明确列出：

-   unlimited multi-selection
    
-   lasso selection
    
-   box selection
    
-   persisted annotation
    
-   persisted measurement history
    
-   shortest-image mode，若未实现
    
-   supercell productization
    
-   clipping
    
-   camera preset productization
    
-   export
    
-   formal `structure.viewer_3d`
    
-   trajectory
    
-   phonon
    
-   Brillouin zone
    
-   volumetric
    
-   defects
    
-   surfaces
    
-   slabs
    
-   structure editing
    

## 22. Readiness

-   atom picking:
    
-   bond picking:
    
-   periodic identity:
    
-   bounded multi-selection:
    
-   distance:
    
-   angle:
    
-   dihedral:
    
-   shortest image:
    
-   keyboard:
    
-   mobile:
    
-   lifecycle:
    
-   performance:
    
-   accessibility:
    
-   browser matrix:
    
-   full `structure.viewer_3d`:
    
-   supercell:
    
-   clipping:
    
-   export:
    
-   trajectory:
    
-   phonon:
    
-   Brillouin:
    
-   volumetric:
    

## 23. Commit / CI

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
    

## 24. Whether allowed to enter next phase

允许 / 不允许

下一阶段建议：

```text
Phase 10F-24：Supercell Productization

```

不要进入trajectory、phonon、Brillouin zone或volumetric。

----------

# 35. PASS 判定

PASS必须满足：

-   有真实atom picking实现
    
-   有真实bond picking实现
    
-   instanceId正确映射PeriodicSiteRef
    
-   selection identity稳定
    
-   selection cap固定
    
-   measurement order稳定
    
-   distance真实计算
    
-   angle真实计算
    
-   dihedral真实计算
    
-   triclinic结构有reference evidence
    
-   cross-boundary measurement正确
    
-   self-periodic measurement正确
    
-   explicit-image policy明确
    
-   shortest-image若未实现则明确拒绝错误近似
    
-   keyboard可完成measurement
    
-   mobile可完成至少distance measurement
    
-   scene switch清除stale state
    
-   lifecycle无资源泄漏
    
-   measurement不修改scene/topology
    
-   performance budget不回退
    
-   accessibility不回退
    
-   browser matrix完整
    
-   no artifact-controlled callback/threshold/cap
    
-   no screen-space scientific calculation
    
-   no external network
    
-   no secret hits
    
-   无新依赖或依赖变更有明确批准
    
-   tests通过
    
-   CI通过
    
-   git clean
    

PARTIAL_PASS仅允许：

-   shortest-image mode被明确deferred
    
-   某浏览器无法稳定自动化bond hover，但click picking完整
    
-   mobile只验证distance而angle/dihedral通过keyboard和desktop
    
-   npm audit因既有registry问题不可用
    

FAIL包括：

-   picking只返回canonical site index而丢失image offset
    
-   bond picking重新猜测topology
    
-   measurement使用screen-space
    
-   triclinic数学错误
    
-   将同一site不同image误判为同一atom
    
-   unlimited selection
    
-   scene切换保留错误measurement
    
-   drag/pinch误触发pick
    
-   measurement写回scene
    
-   artifact可控制callback或threshold
    
-   只有静态fixture没有真实viewer交互
    
-   引入trajectory/phonon/Brillouin/volumetric
    
-   修改核心runtime语义
    
-   无browser evidence
    
-   CI失败却声明PASS
---END---

---TASK---  
状态：待处理

 # Phase 10F-24：Supercell Productization

进入 Phase 10F-24：Supercell Productization。

可以默认：

-   Phase 10F-23 已完成
    
-   atom picking、bond picking、periodic identity、distance/angle/dihedral measurement 已完成
    
-   explicit displayed image measurement policy 已固定
    
-   shortest-image policy 已完成或明确 deferred by design
    
-   selection、measurement、overlay 和 lifecycle 已收口
    
-   Phase 10F-22 accessibility、mobile、cross-browser 已完成
    
-   Phase 10F-21 performance budgets、instancing、bond batching、large-scene policy 已完成
    
-   current production scene schema 仍为 `phase10f18.viewer_scene.v2`
    
-   current production manifest 仍为当前 v2 manifest
    
-   periodic endpoint identity、canonical periodic bond topology、neighbor inspector、legacy compatibility 和 renderer gate 均保持稳定
    
-   当前 branch、HEAD、working tree 和 Phase 10F-23 CI 可视为正确且 clean
    

本阶段不需要重复 baseline 检查。

本阶段的主要任务是：

> 将当前仅作为内部显示或测试能力存在的周期扩胞逻辑，提升为正式、可配置、可持久化、可回放、受资源预算约束、与 picking/measurement/inspector 一致的 supercell product capability。

本阶段重点包括：

-   supercell params contract
    
-   per-axis expansion
    
-   displayed instance generation
    
-   canonical site vs displayed instance identity
    
-   periodic bond replication
    
-   deduplication
    
-   UI controls
    
-   scene state persistence
    
-   recipe persistence
    
-   safe caps
    
-   large-scene degraded/refusal policy
    
-   measurement/picking consistency
    
-   browser evidence
    

本阶段不是 structure editing phase。

supercell 只影响 viewer display state，不修改原始结构资源，不改变 canonical scene topology，不生成新的化学结构文件，除非本阶段显式生成独立、inert 的 derived supercell display artifact。

----------

# 1. 当前已知能力

当前 viewer 已具备：

-   `viewer_scene.v2`
    
-   canonical lattice
    
-   canonical sites
    
-   periodic atom identity：  
    `site_index@[image_offset]`
    
-   canonical periodic bonds
    
-   same-cell bonds
    
-   cross-boundary bonds
    
-   self-periodic bonds
    
-   triclinic periodic geometry
    
-   immutable instance mapping
    
-   atom instancing
    
-   shared bond geometry
    
-   picking
    
-   measurement
    
-   neighbor inspector
    
-   keyboard accessibility
    
-   mobile interaction
    
-   performance budgets
    
-   degraded mode
    
-   over-budget JSON-only fallback
    
-   lifecycle cleanup
    
-   context-loss fallback
    
-   cross-browser evidence
    

当前尚未正式产品化：

-   user-facing supercell controls
    
-   per-axis expansion state
    
-   persisted supercell configuration
    
-   expansion validation
    
-   expansion cap
    
-   display instance generation contract
    
-   supercell-specific bond replication
    
-   bond deduplication across repeated cells
    
-   boundary clipping policy
    
-   primary-cell vs expanded-cell display modes
    
-   instance count preview
    
-   resource estimate before applying expansion
    
-   supercell recipe
    
-   supercell artifact metadata
    
-   scene reload behavior
    
-   URL/state persistence，若项目已有适合机制
    
-   picking/measurement across expanded images
    
-   accessibility semantics for expansion
    
-   mobile control behavior
    
-   browser evidence
    

----------

# 2. 本阶段目标

必须完成以下九类工作：

1.  **Supercell architecture audit**
    
2.  **Supercell parameter contract**
    
3.  **Deterministic displayed instance generation**
    
4.  **Periodic bond replication and deduplication**
    
5.  **UI controls and preview**
    
6.  **Persistence and reproducibility**
    
7.  **Performance, lifecycle and fallback**
    
8.  **Picking / measurement / accessibility integration**
    
9.  **Tests、evidence、docs和readiness收口**
    

本阶段必须产生实际实现代码。

如果最终只有 docs、static fixtures 或内部 helper，没有真实 viewer 控件和 execution path，本阶段必须判定为 FAIL。

----------

# 3. 严格禁止范围

本阶段不得实现：

-   structure editing
    
-   add/remove atom
    
-   move atom
    
-   change species
    
-   change occupancy
    
-   lattice editing
    
-   canonical topology editing
    
-   bond editing
    
-   trajectory
    
-   phonon
    
-   Brillouin zone
    
-   volumetric rendering
    
-   charge density
    
-   spin density
    
-   isosurface
    
-   defects
    
-   surfaces
    
-   slabs
    
-   clipping plane
    
-   PNG/PDF export
    
-   glTF/GLB export
    
-   persisted arbitrary annotations
    
-   external API
    
-   notebook execution
    
-   script execution
    
-   real LLM
    
-   formal `structure.viewer_3d` registration
    

不得：

-   修改 canonical site index
    
-   修改 original lattice
    
-   修改 canonical periodic bond identity
    
-   修改 `1e-5 Å` bond distance tolerance
    
-   将 supercell display state写回原始结构
    
-   将 display instance当成新的 canonical atom
    
-   将 same canonical site不同 image offset混为同一 displayed instance
    
-   放宽 scene validator caps
    
-   绕过 Phase 10F-21 performance budgets
    
-   允许 unbounded expansion
    
-   允许 artifact 控制任意 expansion
    
-   允许负数、零或 non-integer expansion
    
-   允许 supercell 触发无限 instance/material/geometry 创建
    
-   静默截断而不提示
    
-   通过删除 periodic bonds伪造性能通过
    
-   通过只支持 1×1×1伪造 productization完成
    
-   修改 QueueWorkerRuntime 主语义
    
-   修改 AnalysisPlanRepository 主语义
    
-   修改 `/planner/jobs` 主语义
    
-   引入新的 renderer framework
    
-   引入 remote assets
    
-   执行 artifact JS
    

允许：

-   supercell helper
    
-   display-state contract
    
-   UI controls
    
-   resource estimator
    
-   instance generation
    
-   bond replication
    
-   deduplication
    
-   persistence
    
-   recipe
    
-   derived display artifact
    
-   tests
    
-   browser evidence
    
-   docs
    
-   persistent updates
    

----------

# 4. 必读实现

开始后直接阅读当前真实代码。

## 4.1 Periodic Instance Generation

搜索：

```bash
rg -n "supercell|cellExpansion|imageOffset|PeriodicSiteRef|displayedAtoms|instanceId" apps/web backend packages tests

```

重点确认：

-   当前是否已有 internal expansion helper
    
-   当前 displayed atoms如何生成
    
-   image offset range
    
-   instance ordering
    
-   instanceId映射
    
-   lattice translation
    
-   triclinic支持
    
-   site cap
    
-   display cap
    
-   lifecycle
    

## 4.2 Bond Replication

定位：

-   canonical bond mapper
    
-   displayed bond generation
    
-   endpoint visibility rule
    
-   duplicate suppression
    
-   cross-boundary policy
    
-   self-periodic policy
    
-   bond cap
    
-   line geometry
    

## 4.3 Selection / Measurement

确认：

-   `PeriodicSiteRef`
    
-   atom selection key
    
-   bond selection key
    
-   measurement point identity
    
-   scene switch cleanup
    
-   selection persistence
    
-   overlay behavior
    

## 4.4 Performance

确认：

-   complexity estimator
    
-   interactive/degraded/refused modes
    
-   draw-call budget
    
-   displayed atom cap
    
-   displayed bond cap
    
-   mobile thresholds
    
-   over-budget behavior
    

## 4.5 State / Persistence

检查：

-   current viewer state model
    
-   artifact state
    
-   recipe state
    
-   query params
    
-   local component state
    
-   persisted analysis/job artifacts
    
-   whether viewer display state can be stored safely
    

----------

# 5. 修改前输出审计

修改代码前输出：

# Phase 10F-24 Supercell Productization Pre-Implementation Audit

## 1. Current Supercell Capability

-   current expansion helper:
    
-   current params:
    
-   current default:
    
-   current caps:
    
-   current ordering:
    
-   current bond handling:
    
-   current UI:
    
-   current persistence:
    
-   current evidence:
    

## 2. Identity Model

-   canonical site:
    
-   displayed instance:
    
-   image offset:
    
-   instance ID:
    
-   bond identity:
    
-   measurement identity:
    
-   known risks:
    

## 3. Performance Model

-   current atom cap:
    
-   current bond cap:
    
-   current expansion cap:
    
-   current degraded threshold:
    
-   current refusal threshold:
    
-   mobile threshold:
    
-   missing safeguards:
    

## 4. Persistence Model

-   viewer state:
    
-   recipe:
    
-   artifact metadata:
    
-   reload:
    
-   scene switching:
    
-   URL/state persistence:
    
-   known gaps:
    

## 5. Selected Strategy

说明：

-   expansion params:
    
-   instance generation:
    
-   ordering:
    
-   bond replication:
    
-   deduplication:
    
-   UI:
    
-   persistence:
    
-   fallback:
    
-   lifecycle:
    
-   accessibility:
    

## 6. Planned Files

列出预计修改或新增：

-   renderer
    
-   supercell helper
    
-   state model
    
-   controls
    
-   inspector
    
-   measurement integration
    
-   tests
    
-   browser runner
    
-   fixtures
    
-   evidence
    
-   docs
    
-   persistent
    

审计后直接继续实现。

----------

# 6. Supercell Parameter Contract

建立 application-owned supercell display contract。

推荐：

```ts
type SupercellExpansion = {
  a: number;
  b: number;
  c: number;
};

```

或：

```ts
type SupercellExpansion = [number, number, number];

```

必须选一种 canonical representation。

推荐 JSON：

```json
{
  "schema_version": "phase10f24.supercell_display.v1",
  "expansion": [2, 2, 1],
  "origin_policy": "positive_octant",
  "include_primary_cell": true,
  "display_mode": "expanded_periodic_instances"
}

```

必须固定：

-   axis order：`[a,b,c]`
    
-   integer only
    
-   minimum：1
    
-   maximum per axis
    
-   maximum total cells
    
-   maximum displayed atom instances
    
-   maximum displayed bonds
    
-   origin policy
    
-   instance ordering
    
-   default expansion：`[1,1,1]`
    

不得允许：

-   0
    
-   negative
    
-   float
    
-   NaN
    
-   Infinity
    
-   string coercion
    
-   arbitrary matrix expansion
    
-   artifact callback
    
-   user-defined translation list
    
-   arbitrary offset range
    

----------

# 7. Expansion Origin Policy

必须选择固定、可解释的 policy。

建议优先：

```text
positive_octant

```

即：

```text
offsets:
0 <= i < a
0 <= j < b
0 <= k < c

```

例如 `2×2×1`：

```text
[0,0,0]
[0,1,0]
[1,0,0]
[1,1,0]

```

优点：

-   deterministic
    
-   易持久化
    
-   与传统 supercell 语义一致
    
-   primary cell明确为 `[0,0,0]`
    

也可以选择 centered expansion，但必须解释奇偶数行为。

本阶段只能固定一种 canonical origin policy。

不要允许用户自定义任意 offset范围。

----------

# 8. Deterministic Instance Generation

## 8.1 Ordering

必须固定 instance ordering。

推荐：

```text
for imageOffset in lexicographic order:
    for canonical site in siteIndex order:
        emit PeriodicSiteRef

```

即 key：

```text
(dx,dy,dz,siteIndex)

```

或选择：

```text
(siteIndex,dx,dy,dz)

```

必须只选一种，并在所有组件统一。

要求：

-   same input + same expansion = same ordering
    
-   same ordering用于instanceId mapping
    
-   scene reload稳定
    
-   browser稳定
    
-   no random IDs
    
-   no object iteration order dependency
    

## 8.2 Instance Identity

每个 displayed instance必须为：

```ts
{
  siteIndex: number;
  imageOffset: [number, number, number];
}

```

不得：

-   生成新 canonical site index
    
-   修改原siteIndex
    
-   丢失 imageOffset
    
-   使用显示序号替代科学身份
    

## 8.3 Cartesian Position

必须使用：

```text
cartesian =
canonical fractional coordinates
+ integer image offset
→ lattice transform

```

复用现有 periodic math helper。

必须覆盖：

-   orthogonal
    
-   triclinic
    
-   non-unit lattice
    
-   negative fractional coordinates，若合法
    
-   fractional coordinates >1，若 canonical parser允许
    

----------

# 9. Supercell Size Estimation

应用 expansion 前必须先估算。

至少计算：

```text
total_cells = a * b * c

displayed_atoms =
canonical_sites * total_cells

estimated_displayed_bonds =
based on canonical periodic topology and visibility policy

```

输出：

```json
{
  "expansion": [2,2,2],
  "total_cells": 8,
  "displayed_atoms": 64,
  "estimated_displayed_bonds": 112,
  "mode": "interactive",
  "warnings": []
}

```

要求：

-   deterministic
    
-   bounded arithmetic
    
-   overflow safe
    
-   integer validation
    
-   no browser-dependent hidden behavior
    
-   estimator与real build结果对照
    

如果估算超出hard cap：

-   不生成instances
    
-   不初始化新renderer
    
-   保留当前scene
    
-   显示typed error
    
-   提供较小建议
    
-   不让页面冻结
    

----------

# 10. Supercell Caps

必须建立明确caps。

至少包括：

-   max expansion per axis
    
-   max total cells
    
-   max displayed atoms
    
-   max displayed bonds
    
-   max style groups
    
-   max measurement points保持4
    
-   max inspector rows
    
-   max JSON artifact bytes，若生成derived artifact
    

建议遵循Phase 10F-21模式：

## Interactive

-   small/medium expansion
    
-   full atoms
    
-   full visible bonds
    
-   picking
    
-   inspector
    
-   measurement
    

## Degraded

-   within hard cap
    
-   lower atom sphere detail
    
-   optional bonds default hidden或reduced policy
    
-   hover disabled
    
-   labels disabled
    
-   measurement仍可用
    
-   warning visible
    

## Refused

-   exceeds renderer budget
    
-   expansion not applied
    
-   current scene retained
    
-   no additional canvas/context
    
-   typed error
    
-   JSON/state summary available
    

Typed code建议：

```text
VIEWER_SUPERCELL_BUDGET_EXCEEDED

```

----------

# 11. Bond Replication

这是本阶段核心之一。

## 11.1 Canonical Bond Source

必须继续使用 canonical v2 periodic bonds。

不得：

-   frontend重新猜测neighbor topology
    
-   根据expanded atom距离重新推断bond
    
-   从screen positions生成bond
    
-   忽略canonical offset
    

## 11.2 Replication Rule

对于 canonical bond：

```text
from:
site i @[0,0,0]

to:
site j @[relative offset]

```

对于每个source cell offset `t`：

```text
displayed from:
i @ t

displayed to:
j @ (t + relative offset)

```

仅当两端都落在当前显示offset集合中时绘制。

这应延续Phase 10F-18 boundary policy：

> only draw when both endpoints are displayed; do not draw half-bonds.

## 11.3 Deduplication

必须按 displayed periodic endpoint pair canonicalize。

建议 displayed bond key：

```text
(
  from_site,
  from_dx,
  from_dy,
  from_dz,
  to_site,
  to_dx,
  to_dy,
  to_dz
)

```

并与reversal取lexicographic minimum。

必须防止：

-   canonical reversal duplicate
    
-   replicated duplicate
    
-   self-periodic duplicate
    
-   adjacent cell duplicate
    
-   supercell boundary duplicate
    

## 11.4 Self-Periodic Bonds

对 self-periodic bond：

```text
site i@[t] → site i@[t + delta]

```

两端显示时允许。

零offset self bond继续拒绝。

## 11.5 Bond Cap

replication前估算，生成中再次hard cap。

不得：

-   生成完整列表后再截断造成内存峰值
    
-   非deterministic截断
    
-   silent truncation
    

若允许truncation：

-   stable order
    
-   warning
    
-   summary
    
-   metrics
    

优先使用refusal或degraded策略，不建议无提示截断。

----------

# 12. Supercell Lattice Display

必须区分：

-   canonical unit cell
    
-   displayed supercell boundary
    

## 12.1 Canonical Unit Cell

允许显示原始unit-cell边界。

## 12.2 Supercell Boundary

应支持显示 expanded cell边界。

expanded lattice vectors：

```text
A' = a * A
B' = b * B
C' = c * C

```

要求：

-   仅用于显示
    
-   不修改scene canonical lattice
    
-   inspector明确区分canonical lattice和display lattice
    
-   measurement仍基于instance coordinates
    
-   lattice geometry bounded
    
-   no per-cell lattice box unless explicitly needed
    

不得默认为每个cell画完整box导致大量重复lines。

推荐：

-   primary cell boundary可选
    
-   outer supercell boundary可选
    
-   internal cell grid可选但默认关闭且受cap限制
    

----------

# 13. UI Controls

## 13.1 Controls

至少提供：

-   A axis expansion
    
-   B axis expansion
    
-   C axis expansion
    
-   Apply
    
-   Reset to `1×1×1`
    
-   estimated atom count
    
-   estimated bond count
    
-   expected render mode
    

控件必须：

-   integer input
    
-   min/max
    
-   no silent coercion
    
-   keyboard accessible
    
-   mobile touch target合格
    
-   visible focus
    
-   screen-reader label
    
-   invalid state明确
    
-   current value与applied value区分
    

## 13.2 Apply Model

推荐：

-   inputs可暂存draft
    
-   Apply后才重建display scene
    
-   invalid draft不影响当前scene
    
-   over-budget draft不应用
    
-   reset立即回到`1×1×1`或使用Apply，必须固定一种行为
    

不要每输入一个数字就立即进行大型scene rebuild。

## 13.3 Presets

可选提供bounded presets：

```text
1×1×1
2×1×1
2×2×1
2×2×2
3×3×3

```

但必须经过caps检查。

不得由artifact定义preset。

----------

# 14. State Model

建立清晰状态：

```ts
type SupercellState = {
  draft: [number, number, number];
  applied: [number, number, number];
  mode: "interactive" | "degraded" | "refused";
  estimate: SupercellEstimate;
  warnings: string[];
};

```

要求：

-   draft/applied分离
    
-   scene切换默认策略明确
    
-   artifact切换默认策略明确
    
-   legacy JSON-only不应用supercell
    
-   invalid scene清除或禁用controls
    
-   context loss保留applied state或reset，必须固定策略
    

推荐：

```text
new viewer scene resets expansion to [1,1,1]

```

除非有明确persistence需求。

----------

# 15. Persistence

本阶段必须实现至少一种可审计persistence。

优先顺序：

1.  recipe persistence
    
2.  viewer display-state artifact
    
3.  URL/query state，若项目已有安全机制
    
4.  browser-local state不建议作为唯一证据
    

## 15.1 Recipe

更新或新增viewer recipe字段：

```json
{
  "viewer_state": {
    "supercell_expansion": [2,2,1],
    "origin_policy": "positive_octant",
    "show_primary_cell": true,
    "show_supercell_boundary": true,
    "show_internal_grid": false
  }
}

```

要求：

-   deterministic
    
-   validated
    
-   no executable content
    
-   replayable
    
-   schema versioned
    

## 15.2 Derived Display Artifact

可选生成：

```text
viewer_supercell_state.json

```

建议schema：

```json
{
  "schema_version": "phase10f24.viewer_supercell_state.v1",
  "scene_schema_version": "phase10f18.viewer_scene.v2",
  "expansion": [2,2,1],
  "origin_policy": "positive_octant",
  "total_cells": 4,
  "displayed_atoms": 16,
  "displayed_bonds": 20,
  "mode": "interactive",
  "warnings": [],
  "deterministic": true,
  "security": {
    "contains_javascript": false,
    "external_urls": []
  }
}

```

不得复制完整scene，除非项目artifact规范明确需要。

## 15.3 Replay

必须证明：

-   same scene
    
-   same expansion
    
-   same settings
    

得到：

-   same instance order
    
-   same displayed atom count
    
-   same displayed bond count
    
-   same hashes或等价stable payload
    
-   same metrics
    

----------

# 16. Picking Integration

supercell productization必须保持 picking正确。

要求：

-   atom picking返回expanded periodic identity
    
-   same canonical site不同cell可分别选择
    
-   instanceId映射稳定
    
-   scene rebuild后stale instanceId清理
    
-   1×1×1 → 2×2×2 selection清理或安全重映射
    

推荐：

```text
expansion change clears active selection and measurement draft

```

因为同一display instance集合发生变化。

必须测试：

-   pick primary cell atom
    
-   pick copied cell atom
    
-   same site different offset
    
-   cross-boundary bond
    
-   self-periodic bond
    
-   expanded lattice edge atom
    

----------

# 17. Measurement Integration

必须保证：

-   explicit displayed image measurement继续正确
    
-   selected periodic offsets来自supercell instance
    
-   distance/angle/dihedral基于expanded Cartesian positions
    
-   same canonical site不同cell可测量
    
-   self-periodic距离可测量
    
-   triclinic expansion正确
    
-   expansion change清除measurement draft
    
-   saved measurement包含supercell state或足够provenance
    

measurement artifact建议增加：

```json
{
  "viewer_state": {
    "supercell_expansion": [2,2,1]
  }
}

```

不得：

-   将display expansion误写成canonical scene topology
    
-   将expanded instance当作新site
    
-   自动切换到shortest-image而不说明
    

----------

# 18. Inspector Integration

inspector必须显示：

## Scene

-   canonical site count
    
-   canonical bond count
    

## Display

-   expansion
    
-   total cells
    
-   displayed atom count
    
-   displayed bond count
    
-   render mode
    

## Selected Instance

-   canonical site index
    
-   image offset
    
-   element/species
    
-   fractional coords
    
-   Cartesian coords
    

## Neighbor

-   displayed target identity
    
-   canonical bond key
    
-   displayed bond identity
    
-   cross-boundary state
    
-   source/authoritative
    

必须明确区分：

```text
canonical
displayed

```

避免用户误认为2×2×2生成了8倍新的canonical atoms。

----------

# 19. Accessibility

必须保持Phase 10F-22标准。

要求：

-   expansion controls有label
    
-   axis语义明确
    
-   invalid input可读
    
-   estimate可读
    
-   Apply/Reset可键盘操作
    
-   applied state通过live region播报一次
    
-   degraded/refused状态可读
    
-   display count可读
    
-   no color-only state
    
-   200% zoom可用
    
-   mobile inspector可用
    
-   expansion数值不只以紧凑符号表达
    

建议播报：

```text
Supercell applied: 2 by 2 by 1, 4 cells, 32 displayed atoms.

```

不得播报每个instance。

----------

# 20. Mobile

必须验证：

-   numeric inputs
    
-   preset buttons
    
-   Apply
    
-   Reset
    
-   viewport resize
    
-   portrait/landscape
    
-   expanded scene rotate/pan/zoom
    
-   picking
    
-   measurement
    
-   inspector
    
-   degraded/refused状态
    

要求：

-   controls不遮挡viewer
    
-   面板可折叠
    
-   touch target满足要求
    
-   number input不触发布局崩溃
    
-   orientation change不重复canvas/context
    
-   expansion apply期间不冻结
    

----------

# 21. Lifecycle

必须处理：

-   expansion apply
    
-   expansion reset
    
-   scene switch
    
-   artifact switch
    
-   context loss
    
-   context recovery
    
-   degraded mode
    
-   refused mode
    
-   unmount
    
-   orientation change
    
-   legacy JSON-only
    
-   invalid scene
    

要求：

-   old instance buffers dispose
    
-   old bond buffers dispose
    
-   old lattice geometry dispose
    
-   stale build cancellation
    
-   no duplicate renderer
    
-   no duplicate canvas
    
-   no duplicate context
    
-   no stale inspector state
    
-   no stale selection
    
-   no stale measurement
    
-   no stale estimate
    

必须使用Phase 10F-21 generation token/stale protection或等价机制。

----------

# 22. Performance Requirements

必须保持：

-   atom draw calls bounded
    
-   bond draw calls bounded
    
-   geometry/material bounded
    
-   no one-mesh-per-instance
    
-   no one-object-per-bond
    
-   on-demand render
    
-   no continuous rebuild
    
-   Apply前不build
    
-   estimator先于build
    
-   hard cap先于allocation
    
-   instance buffer一次构建
    
-   bond buffer一次构建
    
-   expansion change才重建
    
-   camera movement不重建
    
-   inspector open/close不重建
    

记录：

-   `1×1×1`
    
-   `2×2×1`
    
-   `2×2×2`
    
-   degraded threshold
    
-   refused threshold
    

的：

-   displayed atoms
    
-   displayed bonds
    
-   draw calls
    
-   geometries
    
-   materials
    
-   build time
    
-   disposal time
    
-   canvas/context
    
-   active loops
    

不得用严格毫秒断言作为唯一PASS依据。

----------

# 23. Typed Errors and Warnings

至少覆盖：

```text
VIEWER_SUPERCELL_INVALID_EXPANSION
VIEWER_SUPERCELL_AXIS_LIMIT_EXCEEDED
VIEWER_SUPERCELL_TOTAL_CELL_LIMIT_EXCEEDED
VIEWER_SUPERCELL_ATOM_BUDGET_EXCEEDED
VIEWER_SUPERCELL_BOND_BUDGET_EXCEEDED
VIEWER_SUPERCELL_RENDER_BUDGET_EXCEEDED
VIEWER_SUPERCELL_SCENE_UNSUPPORTED
VIEWER_SUPERCELL_BUILD_CANCELLED
VIEWER_SUPERCELL_STATE_STALE
VIEWER_SUPERCELL_DEGRADED_MODE

```

要求：

-   deterministic
    
-   sanitized
    
-   no stack
    
-   no local path
    
-   no secret
    
-   stable warning ordering
    
-   no raw artifact payload
    

----------

# 24. Tests

## 24.1 Parameter Tests

覆盖：

-   default `1×1×1`
    
-   valid `2×2×2`
    
-   zero
    
-   negative
    
-   float
    
-   string
    
-   NaN
    
-   Infinity
    
-   axis max
    
-   total cells max
    
-   atom cap
    
-   bond cap
    
-   unknown fields
    

## 24.2 Instance Generation Tests

覆盖：

-   orthogonal `2×1×1`
    
-   orthogonal `2×2×2`
    
-   triclinic
    
-   deterministic ordering
    
-   unique periodic identity
    
-   correct Cartesian positions
    
-   same site multiple offsets
    
-   stable replay
    
-   no duplicate instances
    

## 24.3 Bond Replication Tests

覆盖：

-   same-cell
    
-   cross-boundary
    
-   self-periodic
    
-   triclinic
    
-   endpoint visibility
    
-   no half-bonds
    
-   reversal dedup
    
-   adjacent-cell dedup
    
-   stable ordering
    
-   cap enforcement
    

## 24.4 Lattice Tests

覆盖：

-   canonical cell
    
-   supercell boundary
    
-   internal grid off
    
-   internal grid on with cap
    
-   triclinic outer boundary
    
-   reset
    

## 24.5 UI Tests

覆盖：

-   draft/applied separation
    
-   Apply
    
-   Reset
    
-   invalid input
    
-   estimate
    
-   degraded warning
    
-   refused error
    
-   presets
    
-   keyboard
    
-   live region
    
-   mobile layout
    

## 24.6 Persistence Tests

覆盖：

-   recipe serialization
    
-   replay
    
-   artifact validation
    
-   same hash/equivalent payload
    
-   invalid persisted state
    
-   schema version
    
-   scene mismatch
    

## 24.7 Picking Tests

覆盖：

-   primary cell atom
    
-   copied cell atom
    
-   same site different offset
    
-   expanded bond
    
-   cross-boundary bond
    
-   self-periodic bond
    
-   expansion change cleanup
    

## 24.8 Measurement Tests

覆盖：

-   distance across cells
    
-   angle across cells
    
-   dihedral across cells
    
-   triclinic expansion
    
-   self-periodic distance
    
-   expansion provenance
    
-   reset cleanup
    

## 24.9 Lifecycle Tests

覆盖：

-   repeated expansion apply
    
-   rapid draft changes
    
-   rapid apply switching
    
-   stale build cancellation
    
-   scene switch
    
-   context loss
    
-   unmount
    
-   orientation
    
-   no resource growth
    

## 24.10 Regression

必须保持：

-   Phase 10F-18 periodic topology
    
-   Phase 10F-19 integration
    
-   Phase 10F-20 compatibility
    
-   Phase 10F-21 performance
    
-   Phase 10F-22 accessibility/mobile
    
-   Phase 10F-23 picking/measurement
    
-   no external network
    
-   no artifact JS
    

----------

# 25. Reference Fixtures

至少包含：

## Tiny Orthogonal

-   small atom count
    
-   simple cross-boundary bond
    
-   `2×2×1`
    

## Triclinic

-   non-orthogonal lattice
    
-   cross-boundary topology
    
-   `2×2×2`
    

## Self-Periodic

-   same site nonzero offset
    
-   expansion replication
    

## Multi-Species

-   material grouping
    
-   picking/inspector
    

## Near-Degraded

-   close to performance threshold
    

## Over-Budget

-   estimator rejects before build
    

不得提交巨大expanded JSON。

优先：

-   base scene + expansion params
    
-   deterministic test-time generation
    

----------

# 26. Browser Evidence

新增：

```text
docs/phase10f/evidence/phase10f24_supercell_productization/

```

必须使用真实浏览器。

## 26.1 Chromium

覆盖：

-   `1×1×1`
    
-   `2×1×1`
    
-   `2×2×1`
    
-   `2×2×2`
    
-   triclinic
    
-   self-periodic
    
-   picking copied instance
    
-   measurement across cells
    
-   degraded
    
-   refused
    
-   reset
    
-   persistence/replay
    
-   repeated apply
    
-   scene switch cleanup
    

## 26.2 Firefox

至少覆盖：

-   `2×2×1`
    
-   picking
    
-   measurement
    
-   degraded
    
-   reset
    
-   lifecycle
    

## 26.3 WebKit

至少覆盖：

-   `2×2×1`
    
-   controls
    
-   picking
    
-   reset
    
-   refused fallback
    
-   lifecycle
    

## 26.4 Mobile

至少覆盖：

-   controls
    
-   Apply
    
-   `2×2×1`
    
-   rotate/pan/zoom
    
-   copied atom pick
    
-   distance measurement
    
-   orientation change
    
-   reset
    
-   refused state
    

----------

# 27. Evidence Assertions

每个browser evidence记录：

-   browser version
    
-   viewport
    
-   device class
    
-   base scene
    
-   expansion
    
-   total cells
    
-   canonical sites
    
-   displayed atoms
    
-   canonical bonds
    
-   displayed bonds
    
-   render mode
    
-   draw calls
    
-   geometries
    
-   materials
    
-   build time
    
-   disposal time
    
-   selected identity
    
-   measurement result
    
-   canvas count
    
-   context count
    
-   console errors
    
-   network requests
    

必须验证：

-   exact instance ordering
    
-   exact periodic identity
    
-   correct displayed count
    
-   correct bond replication
    
-   no duplicate bonds
    
-   no half-bonds
    
-   picking copied cell works
    
-   measurement across cells correct
    
-   reset returns to `1×1×1`
    
-   refused mode does not allocate renderer resources
    
-   repeated apply does not leak
    
-   no external network
    
-   no artifact JS
    

----------

# 28. Evidence Files

建议至少包含：

```text
README.md
supercell_contract.json
supercell_caps.json
origin_policy.json
instance_ordering.json
orthogonal_results.json
triclinic_results.json
self_periodic_results.json
bond_replication.json
deduplication_results.json
performance_estimates.json
performance_actuals.json
degraded_mode.json
refused_mode.json
recipe_replay.json
picking_results.json
measurement_results.json
lifecycle_stress.json
browser_matrix.json
mobile_matrix.json
console_audit.json
network_audit.json
security_audit.json
artifact_hashes.json

```

截图建议：

```text
01_default_1x1x1.png
02_supercell_2x1x1.png
03_supercell_2x2x1.png
04_supercell_2x2x2.png
05_triclinic_supercell.png
06_copied_instance_selected.png
07_cross_cell_measurement.png
08_degraded_mode.png
09_refused_mode.png
10_mobile_supercell.png
11_mobile_measurement.png
12_reset_1x1x1.png

```

不得保存：

-   巨大expanded scene payload
    
-   browser cache
    
-   GPU dump
    
-   private path
    
-   secret
    
-   token
    
-   remote URL
    
-   crash dump
    

----------

# 29. Derived Supercell Artifact

建议生成：

```text
viewer_supercell_state.json

```

可选：

```text
supercell_summary.md

```

## viewer_supercell_state.json

必须包含：

-   schema version
    
-   scene schema version
    
-   scene identity/provenance
    
-   expansion
    
-   origin policy
    
-   total cells
    
-   canonical site count
    
-   displayed atom count
    
-   canonical bond count
    
-   displayed bond count
    
-   mode
    
-   caps
    
-   warnings
    
-   deterministic
    
-   security
    

不得包含：

-   renderer objects
    
-   Three.js references
    
-   full duplicated atom coordinates，除非必要
    
-   callback
    
-   HTML
    
-   JS
    
-   URL
    
-   shader
    
-   remote asset
    

## supercell_summary.md

应包含：

-   base structure
    
-   canonical counts
    
-   expansion
    
-   displayed counts
    
-   boundary policy
    
-   bond replication policy
    
-   performance mode
    
-   warnings
    
-   no structure mutation
    
-   no canonical topology mutation
    
-   no artifact JS
    
-   no external resources
    

----------

# 30. Security

必须验证：

-   no artifact JavaScript
    
-   no artifact HTML
    
-   no artifact callback
    
-   no artifact shader
    
-   no artifact module
    
-   no eval
    
-   no Function constructor
    
-   no external URL
    
-   no remote texture
    
-   no CDN
    
-   no iframe
    
-   no arbitrary local file access
    
-   no notebook execution
    
-   no script execution
    
-   no real LLM
    
-   no dependency addition
    
-   no artifact-controlled expansion cap
    
-   no artifact-controlled origin policy
    
-   no artifact-controlled instance ordering
    
-   no artifact-controlled renderer detail
    
-   no unbounded expansion
    
-   no integer overflow
    
-   no memory allocation before cap check
    
-   no topology inference
    
-   no canonical scene mutation
    
-   no telemetry upload
    

必须输出：

```text
NO_EXTERNAL_NETWORK_REQUESTS
NO_SECRET_PATTERN_HITS

```

----------

# 31. Dependency Policy

默认不新增依赖。

优先使用：

-   existing periodic helpers
    
-   existing renderer mapper
    
-   existing complexity estimator
    
-   existing state utilities
    
-   existing Playwright/browser tools
    

检查：

```bash
npm --prefix apps/web ls --depth=0
npm --prefix apps/web run build

```

记录：

-   dependency tree
    
-   lockfile
    
-   bundle size
    
-   renderer chunk变化
    
-   no unexpected dependency
    

不得为了笛卡尔积或数组生成引入新库。

----------

# 32. Docs / Persistent

新增或更新：

```text
docs/phase10f/phase10f24_supercell_productization.md
docs/phase10f/phase10f24_supercell_display_contract.md
docs/phase10f/phase10f24_supercell_identity_and_ordering.md
docs/phase10f/phase10f24_supercell_bond_replication.md
docs/phase10f/phase10f24_supercell_performance_policy.md
docs/phase10f/phase10f24_supercell_persistence.md
docs/phase10f/phase10f24_supercell_security.md
docs/phase10f/phase10f24_supercell_evidence.md
docs/phase10f/phase10f24_supercell_readiness_matrix.md

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

-   params contract
    
-   axis order
    
-   origin policy
    
-   instance ordering
    
-   bond replication
    
-   deduplication
    
-   cap policy
    
-   degraded/refused mode
    
-   persistence
    
-   picking integration
    
-   measurement integration
    
-   accessibility
    
-   mobile
    
-   lifecycle
    
-   current limitations
    
-   remaining clipping/camera/export work
    
-   formal viewer registration仍未完成
    

----------

# 33. Readiness Matrix

最终分别判断：

-   supercell params
    
-   validation
    
-   origin policy
    
-   instance generation
    
-   deterministic ordering
    
-   periodic identity
    
-   Cartesian positions
    
-   bond replication
    
-   bond deduplication
    
-   self-periodic bonds
    
-   triclinic support
    
-   outer boundary
    
-   internal grid
    
-   estimator
    
-   performance caps
    
-   degraded mode
    
-   refused mode
    
-   UI controls
    
-   keyboard
    
-   mobile
    
-   persistence
    
-   recipe replay
    
-   picking
    
-   measurement
    
-   inspector
    
-   lifecycle
    
-   Chromium
    
-   Firefox
    
-   WebKit
    
-   mobile
    
-   full `structure.viewer_3d`
    
-   clipping
    
-   camera presets
    
-   export
    
-   trajectory
    
-   phonon
    
-   Brillouin zone
    
-   volumetric
    

推荐期望：

```text
supercell params: READY
validation: READY
origin policy: READY
instance generation: READY
deterministic ordering: READY
periodic identity: READY
bond replication: READY
bond deduplication: READY
triclinic support: READY
self-periodic support: READY
performance estimator: READY
interactive mode: READY
degraded mode: READY
refused mode: READY
UI controls: READY
persistence: READY
recipe replay: READY
picking integration: READY
measurement integration: READY
accessibility: READY
mobile: READY
browser matrix: READY
full structure.viewer_3d: PARTIAL_READY
clipping: NOT_READY
camera preset productization: NOT_READY
export: NOT_READY
trajectory: NOT_READY
phonon: NOT_READY
Brillouin zone: NOT_READY
volumetric: NOT_READY

```

不得因为supercell完成就将full viewer标记完全READY。

----------

# 34. Checks

至少运行：

```bash
git diff --check
uv lock --check

npm --prefix apps/web test
npm --prefix apps/web run typecheck
npm --prefix apps/web run build

uv run python -m pytest -q

```

并运行：

-   supercell param tests
    
-   instance generation tests
    
-   bond replication tests
    
-   deduplication tests
    
-   triclinic tests
    
-   self-periodic tests
    
-   estimator tests
    
-   UI tests
    
-   persistence tests
    
-   picking regression
    
-   measurement regression
    
-   lifecycle stress
    
-   performance regression
    
-   accessibility regression
    
-   Chromium runner
    
-   Firefox runner
    
-   WebKit runner
    
-   mobile runner
    
-   service-backed integration
    
-   no-skipped assertion
    
-   secret scan
    
-   network audit
    

必须如实记录：

-   passed
    
-   failed
    
-   skipped
    
-   unavailable
    

不得把 skipped 写成 passed。

----------

# 35. Commit / CI

完成实现、测试、evidence和文档后：

```bash
git status --short
git diff --stat
git add <only Phase 10F-24 related files>
git commit -m "Productize periodic supercell display"
git push origin master

```

等待 current HEAD CI。

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

# 36. 最终报告格式

完成后输出：

# Phase 10F-24 Supercell Productization Result

## 1. Conclusion

PASS / PARTIAL_PASS / FAIL

## 2. Baseline

-   Phase 10F-23 assumed complete:
    
-   branch:
    
-   initial status:
    
-   final HEAD:
    
-   final status:
    

## 3. Supercell Contract

-   schema:
    
-   params:
    
-   axis order:
    
-   default:
    
-   origin policy:
    
-   caps:
    
-   validation:
    

## 4. Instance Generation

-   ordering:
    
-   periodic identity:
    
-   instance ID:
    
-   Cartesian positions:
    
-   orthogonal:
    
-   triclinic:
    
-   determinism:
    

## 5. Bond Replication

-   canonical source:
    
-   replication rule:
    
-   endpoint visibility:
    
-   reversal deduplication:
    
-   adjacent-cell deduplication:
    
-   self-periodic:
    
-   bond cap:
    

## 6. Lattice Display

-   canonical cell:
    
-   supercell boundary:
    
-   internal grid:
    
-   triclinic:
    
-   geometry budget:
    

## 7. UI

-   axis controls:
    
-   draft/applied:
    
-   Apply:
    
-   Reset:
    
-   presets:
    
-   estimate:
    
-   degraded warning:
    
-   refused error:
    
-   accessibility:
    
-   mobile:
    

## 8. Performance Policy

-   interactive threshold:
    
-   degraded threshold:
    
-   refusal threshold:
    
-   displayed atom cap:
    
-   displayed bond cap:
    
-   draw calls:
    
-   geometries:
    
-   materials:
    
-   build time:
    
-   disposal time:
    

## 9. Persistence

-   recipe:
    
-   state artifact:
    
-   replay:
    
-   deterministic:
    
-   scene mismatch:
    
-   reload behavior:
    

## 10. Picking Integration

-   primary cell:
    
-   copied cell:
    
-   same site different offset:
    
-   bonds:
    
-   stale selection:
    
-   expansion change:
    

## 11. Measurement Integration

-   distance:
    
-   angle:
    
-   dihedral:
    
-   cross-cell:
    
-   self-periodic:
    
-   triclinic:
    
-   provenance:
    
-   expansion change:
    

## 12. Inspector

-   canonical counts:
    
-   displayed counts:
    
-   expansion:
    
-   selected identity:
    
-   neighbor identity:
    
-   canonical/display distinction:
    

## 13. Lifecycle

-   repeated apply:
    
-   reset:
    
-   scene switch:
    
-   context loss:
    
-   recovery:
    
-   unmount:
    
-   orientation:
    
-   stale build:
    
-   resource cleanup:
    

## 14. Browser Evidence

-   Chromium:
    
-   Firefox:
    
-   WebKit:
    
-   mobile:
    
-   picking:
    
-   measurement:
    
-   degraded:
    
-   refused:
    
-   lifecycle:
    
-   console:
    
-   network:
    

## 15. Security

-   expansion caps:
    
-   allocation-before-validation:
    
-   artifact control:
    
-   topology mutation:
    
-   canonical scene mutation:
    
-   executable content:
    
-   external resources:
    
-   dependencies:
    
-   secrets:
    
-   network:
    

## 16. Evidence

-   directory:
    
-   contract:
    
-   instance ordering:
    
-   bond replication:
    
-   performance:
    
-   persistence:
    
-   browser matrix:
    
-   screenshots:
    
-   markers:
    

## 17. Tests

-   params:
    
-   instances:
    
-   bonds:
    
-   triclinic:
    
-   persistence:
    
-   picking:
    
-   measurement:
    
-   frontend full:
    
-   backend full:
    
-   typecheck:
    
-   build:
    
-   browsers:
    
-   mobile:
    
-   service-backed:
    
-   no-skipped:
    
-   lock:
    
-   diff:
    

## 18. Files

-   renderer:
    
-   supercell helper:
    
-   controls:
    
-   state:
    
-   inspector:
    
-   tests:
    
-   browser runners:
    
-   evidence:
    
-   docs:
    
-   persistent:
    
-   dependencies/lockfile:
    

## 19. Deferred

明确列出：

-   arbitrary offset windows
    
-   centered supercell origin，若未实现
    
-   asymmetric expansion
    
-   persisted structure mutation
    
-   canonical structure export
    
-   clipping planes
    
-   section/slice view
    
-   camera preset productization
    
-   PNG/PDF export
    
-   glTF/GLB export
    
-   formal `structure.viewer_3d`
    
-   trajectory
    
-   phonon
    
-   Brillouin zone
    
-   volumetric
    
-   defects
    
-   surfaces
    
-   slabs
    
-   structure editing
    

## 20. Readiness

-   params:
    
-   instance generation:
    
-   periodic identity:
    
-   bonds:
    
-   triclinic:
    
-   self-periodic:
    
-   performance:
    
-   persistence:
    
-   picking:
    
-   measurement:
    
-   accessibility:
    
-   mobile:
    
-   browser matrix:
    
-   full `structure.viewer_3d`:
    
-   clipping:
    
-   camera presets:
    
-   export:
    
-   trajectory:
    
-   phonon:
    
-   Brillouin:
    
-   volumetric:
    

## 21. Commit / CI

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
    

## 22. Whether allowed to enter next phase

允许 / 不允许

下一阶段建议：

```text
Phase 10F-25：Clipping, Cell and Camera Controls

```

不要进入 trajectory、phonon、Brillouin zone 或 volumetric。

----------

# 37. PASS 判定

PASS必须满足：

-   有真实supercell UI
    
-   支持至少per-axis integer expansion
    
-   不仅支持`1×1×1`
    
-   params有strict validation
    
-   expansion caps明确
    
-   instance generation deterministic
    
-   periodic identity完整
    
-   canonical site index不改变
    
-   imageOffset正确
    
-   triclinic expansion正确
    
-   bond replication来自canonical topology
    
-   no half-bonds
    
-   no duplicate displayed bonds
    
-   self-periodic bond正确
    
-   estimator先于allocation
    
-   over-budget不build
    
-   degraded/refused模式明确
    
-   performance budgets不回退
    
-   recipe或等价persistence完成
    
-   replay稳定
    
-   picking copied instance正确
    
-   measurement across cells正确
    
-   inspector区分canonical/displayed
    
-   expansion change清除stale selection/measurement
    
-   lifecycle无资源泄漏
    
-   accessibility不回退
    
-   mobile可用
    
-   browser matrix完整
    
-   no canonical scene mutation
    
-   no topology inference
    
-   no artifact-controlled caps/order
    
-   no external network
    
-   no secret hits
    
-   无新依赖或依赖变更有明确批准
    
-   tests通过
    
-   CI通过
    
-   git clean
    

PARTIAL_PASS仅允许：

-   centered origin policy明确deferred
    
-   internal cell grid仅实现关闭或有严格cap
    
-   URL persistence未实现，但recipe/state artifact完整
    
-   某mobile浏览器无法提供精确性能计数，但行为证据完整
    
-   npm audit因既有registry问题不可用
    

FAIL包括：

-   通过复制canonical sites生成新siteIndex
    
-   丢失imageOffset
    
-   frontend重新推断bond topology
    
-   重复显示bond
    
-   triclinic位置错误
    
-   unbounded expansion
    
-   先分配后检查cap
    
-   over-budget仍初始化大型buffers
    
-   expansion变化后保留错误selection/measurement
    
-   只有helper没有真实UI
    
-   只有静态fixture没有真实browser interaction
    
-   修改原始结构或canonical scene
    
-   引入trajectory/phonon/Brillouin/volumetric
    
-   修改核心runtime语义
    
-   无browser evidence
    
-   CI失败却声明PASS
---END---
