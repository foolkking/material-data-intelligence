---TASK---
 状态：处理中
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

---TASK---
 状态：待处理

 # Phase 10H：Phonon Contract

进入 Phase 10H：Phonon Contract。

可以默认：

-   Phase 10G：Trajectory Contract 已完成

-   Phase 10G-1：Trajectory Parser / Adapter 已完成

-   Phase 10G-2：Trajectory Viewer 已完成

-   Phase 10G-3：Trajectory Performance / Browser Evidence 已完成并收口

-   `structure.trajectory_viewer` 已正式注册

-   trajectory atom identity、frame identity、fixed/variable lattice、playback、performance tiers、browser matrix和security边界均已稳定

-   Phase 10 Closure Regression Pack保持通过

-   Phase 10F static viewer和Phase 10G trajectory viewer均保持稳定

-   current static scene contract仍为 `phase10f18.viewer_scene.v2`

-   current trajectory contract仍为 `phase10g.trajectory.v1`

-   当前branch、HEAD、working tree和Phase 10G-3 CI可视为正确且clean


本阶段不需要重复Phase 10G-3 baseline检查。

本阶段主要目标：

> 建立统一、严格、可验证、可扩展的phonon数据合同体系，覆盖phonon band、phonon DOS、q-point路径、频率、分支身份、单位、虚频、简并、原子顺序和未来eigenvector扩展边界，为后续Phonon Bands、Phonon DOS、Combined Band + DOS以及Phonon Eigenvector阶段提供稳定基础。

本阶段只完成：

-   phonon domain architecture

-   q-point contract

-   reciprocal-space conventions

-   phonon frequency contract

-   branch identity

-   imaginary frequency policy

-   units and normalization

-   phonon band schema

-   phonon DOS schema

-   combined compatibility contract

-   provenance

-   validation

-   caps

-   fixtures

-   reference tests

-   security

-   readiness documentation


本阶段不实现正式phonon band plot、不实现phonon DOS plot、不实现eigenvector动画。

----------

# 1. 本阶段定位

Phase 10H是phonon科学数据模型基础阶段。

它必须回答：

-   一个phonon band artifact是什么

-   一个q-point如何表示

-   q-point使用什么坐标系

-   reciprocal lattice是否包含`2π`

-   phonon frequency的canonical unit是什么

-   imaginary mode如何表示

-   branch index如何保持稳定

-   degeneracy如何表达

-   high-symmetry labels如何绑定q-point

-   segment boundary如何表达

-   phonon DOS如何归一化

-   projected DOS如何绑定atom/species

-   band和DOS何时可组合

-   eigenvectors将在后续如何关联atom顺序和mode identity

-   invalid或不完整phonon数据如何拒绝


本阶段不是：

-   phonon计算阶段

-   phonopy运行阶段

-   density-functional perturbation theory阶段

-   phonon band renderer阶段

-   phonon DOS renderer阶段

-   phonon animation阶段

-   thermal-property阶段

-   Brillouin zone renderer阶段


----------

# 2. 本阶段目标

必须完成以下十二类工作：

1.  **Existing reciprocal / phonon capability audit**

2.  **Reciprocal-space convention**

3.  **Q-point and path contract**

4.  **Frequency、unit和imaginary-mode policy**

5.  **Branch、mode和degeneracy identity**

6.  **Phonon band schema**

7.  **Phonon DOS schema**

8.  **Band + DOS compatibility contract**

9.  **Validation、caps和typed errors**

10.  **Deterministic serialization、fixtures和reference tests**

11.  **Security and compatibility boundaries**

12.  **Docs、evidence和readiness closure**


本阶段必须产生真实schema、model和validator实现。

如果最终只有规划文档、字段列表或示例JSON，没有可执行validator和tests，本阶段必须判定为FAIL。

----------

# 3. 严格禁止范围

本阶段不得实现：

-   phonon band plotting

-   phonon DOS plotting

-   combined band + DOS UI

-   phonon eigenvector parser

-   phonon animation

-   atomic displacement animation

-   phonopy execution

-   DFPT execution

-   external calculation

-   thermal conductivity

-   free energy

-   entropy

-   heat capacity

-   Grüneisen parameters

-   quasi-harmonic approximation

-   thermal expansion

-   neutron scattering intensity

-   Raman/IR activity

-   Brillouin zone renderer

-   electronic bands

-   electronic DOS

-   trajectory reuse for phonon animation

-   external API

-   notebook execution

-   script execution

-   real LLM

-   formal phonon tool registration


不得：

-   修改trajectory contract

-   修改static viewer scene

-   将phonon mode塞入trajectory contract

-   将phonon frequency与electronic energy混用

-   静默混用THz、cm⁻¹、meV

-   静默改变frequency sign

-   把imaginary frequency绝对值当作positive physical mode

-   使用q-point数组位置作为唯一mode identity而不定义排序

-   静默重新排序branches

-   静默合并degenerate branches

-   静默丢弃negative frequencies

-   静默对DOS重新归一化

-   静默推断high-symmetry labels

-   静默接受不同band和DOS来源进行combined view

-   允许NaN或Infinity

-   允许无限q-points

-   允许无限branches

-   允许无限DOS bins

-   允许任意metadata

-   允许external URL

-   允许artifact JavaScript

-   允许callback

-   允许任意complex payload绕过caps

-   提前标记phonon bands或DOS READY


允许：

-   schema

-   typed models

-   validators

-   canonical serializers

-   unit conversion helpers

-   fixtures

-   reference calculations

-   docs

-   evidence

-   persistent updates


----------

# 4. 必读实现

开始后直接阅读当前真实代码。

## 4.1 Reciprocal-Space and Lattice Code

搜索：

```bash
rg -n "reciprocal|kpoint|qpoint|k-path|brillouin|2\\*pi|2π|lattice inverse|inverse lattice" backend packages apps tests

```

确认：

-   是否已有reciprocal lattice helper

-   是否已有`2π`约定

-   row-vector lattice如何转换到reciprocal lattice

-   是否已有k-point或q-point schema

-   是否已有high-symmetry labels

-   是否有Brillouin规划残留

-   是否存在与本阶段冲突的命名


## 4.2 Existing Plot / Series Contracts

搜索：

```bash
rg -n "band|dos|series|x_axis|y_axis|plot artifact|line plot|density of states" backend packages apps tests

```

确认：

-   通用plot artifact contract

-   series ordering

-   labels

-   units

-   discontinuous segment表示

-   shared axis支持

-   static preview能力


## 4.3 Static Physics Adapters

阅读：

-   `structure.xrd`

-   `structure.rdf`

-   `structure.coordination_hist`


确认：

-   numeric policy

-   units

-   artifact schema

-   provenance

-   candidate expected values

-   official PASS boundaries

-   deterministic ordering


## 4.4 Dependencies

搜索：

```bash
rg -n "phonopy|pymatgen.*phonon|seekpath|spglib|bandstructure|dos" pyproject.toml uv.lock backend packages tests

```

确认：

-   phonopy是否已存在

-   pymatgen phonon对象是否可用

-   seekpath/spglib是否已存在

-   dependency licensing和版本

-   是否已有test-only reference path


----------

# 5. 修改前输出审计

修改任何代码前输出：

# Phase 10H Phonon Contract Pre-Implementation Audit

## 1. Existing Reciprocal-Space Infrastructure

-   lattice convention:

-   reciprocal lattice helper:

-   `2π` convention:

-   q-point model:

-   k-point model:

-   high-symmetry path:

-   reusable validators:

-   current gaps:


## 2. Existing Plot / Artifact Infrastructure

-   line plot contract:

-   DOS-like plot contract:

-   shared axis:

-   discontinuities:

-   series metadata:

-   provenance:

-   deterministic serialization:

-   caps:


## 3. Existing Phonon-Related Code

-   models:

-   adapters:

-   fixtures:

-   docs:

-   dependencies:

-   experimental code:

-   naming conflicts:

-   reusable pieces:


## 4. Scientific Risks

至少列出：

-   reciprocal lattice convention mismatch

-   `2π` ambiguity

-   reciprocal fractional vs Cartesian ambiguity

-   q-point path discontinuity

-   duplicated segment endpoints

-   branch reorder

-   degeneracy ambiguity

-   imaginary frequency sign loss

-   THz/cm⁻¹/meV conversion drift

-   angular frequency vs cyclic frequency confusion

-   DOS normalization ambiguity

-   projected DOS atom-order mismatch

-   atom count mismatch

-   acoustic mode handling

-   Gamma label ambiguity

-   LO-TO metadata ambiguity

-   source library version drift

-   band/DOS source mismatch

-   future eigenvector atom ordering mismatch


## 5. Selected Strategy

说明：

-   reciprocal convention:

-   q-point coordinates:

-   path representation:

-   canonical frequency unit:

-   imaginary mode representation:

-   branch identity:

-   degeneracy:

-   band schema:

-   DOS schema:

-   projected DOS:

-   combined compatibility:

-   caps:

-   determinism:

-   security:


## 6. Planned Files

列出预计新增或修改：

-   phonon models

-   schemas

-   validators

-   unit conversion

-   serializers

-   fixtures

-   backend tests

-   shared/frontend tests，若需要

-   evidence

-   docs

-   persistent


审计后直接继续实现。

----------

# 6. Schema Family

建议建立：

```text
phase10h.phonon_band.v1
phase10h.phonon_dos.v1
phase10h.phonon_summary.v1
phase10h.phonon_manifest.v1

```

建议建立共享子合同：

```text
phase10h.qpoint_path.v1
phase10h.frequency_axis.v1
phase10h.phonon_source.v1

```

可预留但本阶段不完整实现：

```text
phase10h.phonon_mode_ref.v1

```

不得在本阶段建立完整eigenvector payload合同；该内容属于Phase 10H-4。

----------

# 7. Reciprocal Lattice Convention

必须继承项目row-vector lattice约定。

实空间晶格：

```text
A =
[a
 b
 c]

```

其中每一行为一个lattice vector。

必须明确reciprocal lattice定义。

推荐物理学约定：

```text
B = 2π (A⁻¹)ᵀ

```

并满足：

```text
aᵢ · bⱼ = 2π δᵢⱼ

```

如果项目已有不含`2π`的crystallographic reciprocal lattice约定，则必须：

-   选择一个canonical内部约定

-   显式区分

-   提供严格conversion

-   不得混用


建议合同同时记录：

```json
{
  "reciprocal_convention": "physics_2pi",
  "qpoint_coordinate_system": "reciprocal_fractional"
}

```

不得依靠字段名猜测是否含`2π`。

----------

# 8. Q-Point Coordinate Systems

第一版支持：

```text
reciprocal_fractional
reciprocal_cartesian

```

## reciprocal_fractional

q-point：

```text
q = h b1 + k b2 + l b3

```

其中`b1,b2,b3`按合同约定。

推荐canonical representation：

```text
reciprocal_fractional

```

原因：

-   与high-symmetry path兼容

-   与晶格变化解耦

-   更适合序列化


## reciprocal_cartesian

单位必须固定，例如：

```text
radian_per_angstrom

```

或：

```text
inverse_angstrom

```

必须与`2π`约定一致。

不得：

-   每个q-point使用不同坐标系

-   在一个path内混用

-   省略coordinate system


----------

# 9. Q-Point Contract

建议：

```json
{
  "index": 0,
  "coordinates": [0.0, 0.0, 0.0],
  "label": "Γ",
  "segment_index": 0,
  "distance": 0.0
}

```

必须定义：

-   index

-   coordinates

-   optional label

-   segment membership

-   cumulative path distance


要求：

-   coordinates shape = 3

-   finite

-   deterministic

-   index从0开始

-   index连续

-   distance nonnegative

-   segment内distance单调

-   segment boundary策略明确

-   labels bounded

-   label为inert text

-   no HTML

-   no LaTeX execution


----------

# 10. High-Symmetry Label Policy

必须规范化常见标签。

建议canonical：

```text
Γ
X
L
W
K
M
R
A
Z

```

允许来源使用：

```text
GAMMA
Gamma
\\Gamma

```

但normalization必须由后续adapter完成。

本合同必须定义：

-   canonical label representation

-   display label

-   raw source label是否保存

-   label length cap

-   duplicate label policy


建议保存：

```json
{
  "label": "Γ",
  "source_label": "GAMMA"
}

```

不得允许任意HTML或script标签。

----------

# 11. Path Segment Contract

phonon path通常由多个高对称线段组成。

建议：

```json
{
  "segments": [
    {
      "segment_index": 0,
      "start_qpoint_index": 0,
      "end_qpoint_index": 50,
      "start_label": "Γ",
      "end_label": "X"
    }
  ]
}

```

必须固定：

-   segment order

-   endpoint inclusion

-   duplicated endpoints policy

-   discontinuity policy

-   cumulative distance reset或continuous policy


推荐：

-   q-point数组保留source order

-   相邻segments共享端点时，只保存一个q-point或显式保存duplicate marker

-   非连续segment必须标记：


```text
discontinuous = true

```

不得通过distance突变猜测segment discontinuity。

----------

# 12. Path Distance

必须明确distance的数学意义。

推荐：

-   基于reciprocal Cartesian space

-   使用合同固定的reciprocal lattice约定

-   canonical unit：


```text
radian_per_angstrom

```

或项目选定单位。

必须：

-   q-point path distance nondecreasing

-   每segment内部严格或非严格递增

-   duplicated endpoint允许相等distance

-   discontinuous segment可reset或继续累积，但合同必须固定


推荐：

```text
global cumulative distance

```

并为discontinuity提供显式boundary marker。

不得使用q-point数组索引代替科学路径距离。

----------

# 13. Frequency Unit Policy

必须选择canonical frequency unit。

推荐：

```text
terahertz

```

批准输入/转换单位可包括：

```text
terahertz
inverse_centimeter
millielectronvolt

```

必须明确：

-   THz表示cycles per second，不是angular frequency

-   不使用rad/s作为第一版canonical unit

-   cm⁻¹是spectroscopic wavenumber

-   meV是能量等价表示


转换必须使用固定物理常数来源。

不得：

-   将THz与rad·THz混用

-   忽略`2π`

-   使用四舍五入后的常数作为唯一实现

-   静默接受任意unit字符串


----------

# 14. Frequency Representation

每个q-point每个branch一个frequency值。

建议shape：

```text
[qpoint_count, branch_count]

```

或：

```text
branches[branch_index].frequencies[qpoint_index]

```

必须选择并固定。

推荐branch-major：

```json
{
  "branches": [
    {
      "branch_index": 0,
      "frequencies": [0.0, 1.2, 2.1]
    }
  ]
}

```

优势：

-   branch identity更明确

-   plot series自然

-   future eigenvector mode ref更容易绑定


必须：

-   每branch频率长度等于qpoint count

-   branch index连续

-   所有值finite

-   negative值允许

-   no missing values

-   no sparse arrays


----------

# 15. Imaginary Frequency Policy

这是核心科学语义。

推荐canonical规则：

```text
negative real frequency value represents an imaginary phonon mode

```

例如：

```text
-1.5 THz

```

表示：

```text
1.5 i THz

```

必须同时记录合同语义：

```json
{
  "imaginary_frequency_encoding": "negative_real"
}

```

不得：

-   自动取绝对值

-   丢弃negative frequency

-   使用NaN

-   使用字符串`"1.5i"`

-   同一artifact混用negative和explicit imaginary flag


可为每个mode派生：

```text
is_imaginary = frequency < -tolerance

```

但canonical payload不需要重复存储，除非已有schema规范。

----------

# 16. Zero Frequency and Tolerance

必须定义：

```text
frequency_zero_tolerance

```

用途：

-   Gamma acoustic modes

-   small numerical negative values

-   zero classification

-   imaginary classification


必须区分：

-   原始frequency值

-   classification tolerance

-   是否显示为0


不得修改原始值。

建议：

```text
abs(frequency) <= tolerance → near_zero
frequency < -tolerance → imaginary

```

具体tolerance必须通过现有库和fixtures审计确定。

不得凭UI格式化阈值替代科学阈值。

----------

# 17. Acoustic Mode Policy

本阶段不执行acoustic sum rule correction。

必须记录：

-   source是否声明ASR

-   Gamma附近低频模式

-   source-provided corrections

-   warnings


建议metadata：

```json
{
  "acoustic_sum_rule": {
    "applied": false,
    "method": null
  }
}

```

不得：

-   自动把前三个Gamma频率设为0

-   自动排序声学支

-   自动修正imaginary acoustic mode


后续adapter只能根据批准policy处理。

----------

# 18. Branch Identity

第一版必须定义：

```text
branch_index

```

范围：

```text
0 .. branch_count - 1

```

必须明确：

-   branch identity按source order保持

-   不在contract validation阶段按frequency排序

-   不自动跨q-point追踪band connectivity

-   不自动交换crossing branches

-   不因简并重新编号


如果source提供mode eigenvector identity，后续Phase 10H-4可增加更强mode identity。

本阶段：

```text
branch identity = source-stable branch index

```

不得声称branch index一定代表连续物理支，除非source保证。

----------

# 19. Branch Count

对N个原子，通常有：

```text
3N

```

phonon branches。

合同必须检查或警告：

-   `branch_count == 3 * atom_count`


推荐：

-   如果atom count已知且不匹配，默认typed error

-   如果artifact为reduced/filtered dataset，必须显式声明：


```text
branch_scope = subset

```

第一版建议只支持：

```text
branch_scope = full

```

避免歧义。

不得静默接受少量branches并称为完整phonon band。

----------

# 20. Degeneracy Policy

合同必须区分：

-   数值近似简并

-   source-declared degeneracy

-   branch identity


第一版建议：

-   不自动合并branch

-   每branch独立保存

-   可选source metadata记录degeneracy groups

-   validator只检查group indices合法

-   不根据frequency tolerance自动生成权威degeneracy


可选：

```json
{
  "degeneracy_groups": [
    {
      "qpoint_index": 0,
      "branch_indices": [1, 2],
      "source": "producer"
    }
  ]
}

```

不得将近似相等频率自动合并后丢失数据。

----------

# 21. Atom Ordering Contract

即使Phase 10H-4才处理eigenvectors，本阶段必须固定phonon atom ordering基础。

至少记录：

```json
{
  "structure_identity": "...",
  "atom_count": 2,
  "species": ["Si", "Si"],
  "atom_ordering": "canonical_structure_order"
}

```

要求：

-   atom count finite and bounded

-   species order稳定

-   structure identity存在

-   future eigenvectors必须使用同一atom order

-   projected DOS必须绑定同一atom index


不得依赖元素聚合后丢失atom顺序。

----------

# 22. Phonon Band Contract

建议：

```json
{
  "schema_version": "phase10h.phonon_band.v1",
  "structure_identity": "...",
  "atom_count": 2,
  "species": ["Si", "Si"],
  "reciprocal_convention": "physics_2pi",
  "qpoint_coordinate_system": "reciprocal_fractional",
  "frequency_unit": "terahertz",
  "imaginary_frequency_encoding": "negative_real",
  "frequency_zero_tolerance": 1e-6,
  "qpoints": [],
  "segments": [],
  "branches": [],
  "source": {},
  "warnings": [],
  "security": {
    "contains_javascript": false,
    "external_urls": []
  }
}

```

字段名称按项目规范调整。

必须包含：

-   schema version

-   structure identity

-   atom metadata

-   reciprocal convention

-   q-point system

-   frequency unit

-   imaginary encoding

-   tolerance

-   path

-   branches

-   provenance

-   warnings

-   security


----------

# 23. Phonon DOS Contract

建议：

```json
{
  "schema_version": "phase10h.phonon_dos.v1",
  "structure_identity": "...",
  "frequency_unit": "terahertz",
  "density_unit": "states_per_terahertz",
  "normalization": "total_modes",
  "frequencies": [],
  "total_dos": [],
  "projected_dos": [],
  "source": {},
  "warnings": [],
  "security": {
    "contains_javascript": false,
    "external_urls": []
  }
}

```

必须固定：

-   frequency grid

-   density values

-   density unit

-   normalization

-   projected DOS identity

-   negative-frequency region policy

-   integration tolerance

-   smoothing/broadening metadata


----------

# 24. DOS Frequency Grid

要求：

-   one-dimensional

-   finite

-   strictly increasing

-   no duplicates

-   bounded size

-   canonical frequency unit

-   may include negative frequencies

-   no implicit resampling in validator


不得：

-   使用bin edges和bin centers混淆

-   省略grid semantic


必须定义：

```text
frequencies represent sample centers

```

或：

```text
frequencies represent grid points

```

推荐：

```text
sample grid points

```

----------

# 25. DOS Density Unit

推荐：

```text
states_per_terahertz

```

或更科学准确地：

```text
modes_per_terahertz

```

必须区分：

-   total DOS

-   per-atom DOS

-   normalized-to-one DOS

-   mode-count normalized DOS


推荐canonical normalization：

```text
integral(total_dos df) = 3N

```

即：

```text
normalization = total_modes

```

如果输入采用unit-area normalization，后续adapter需转换或明确保存。

不得静默重新归一化。

----------

# 26. DOS Integration Policy

必须固定数值积分方法用于validation/reference。

推荐：

```text
trapezoidal integration

```

验证：

```text
∫ DOS(f) df ≈ 3N

```

使用application-owned tolerance。

必须记录：

-   expected mode count

-   observed integral

-   tolerance

-   normalization status


不得把小网格误差当作严格等式。

----------

# 27. Negative-Frequency DOS

必须允许DOS grid包含negative frequency。

必须明确：

-   negative region表示imaginary modes

-   不自动截断

-   不自动镜像

-   不将其并入positive积分而不说明


可提供：

```text
imaginary_mode_weight

```

作为派生summary，但不修改原始DOS。

----------

# 28. Projected DOS

第一版可支持：

```text
atom_projected
species_projected

```

建议结构：

```json
{
  "projected_dos": [
    {
      "projection_type": "atom",
      "atom_index": 0,
      "species": "Si",
      "values": []
    }
  ]
}

```

或species projection：

```json
{
  "projection_type": "species",
  "species": "Si",
  "values": []
}

```

必须：

-   values长度等于frequency grid

-   atom index合法

-   species与canonical atom order一致

-   projection ordering deterministic

-   no duplicate projection identity

-   units与total DOS一致

-   normalization语义明确


不得：

-   同一字段混合atom和species identity

-   仅靠display label绑定projection

-   将projection总和一定等于total DOS，除非source保证


----------

# 29. DOS Broadening Metadata

本阶段不执行broadening，但合同必须可记录：

```json
{
  "broadening": {
    "method": "gaussian",
    "width": 0.1,
    "unit": "terahertz"
  }
}

```

允许：

-   none

-   gaussian

-   source_defined


不得开放任意函数名。

必须记录：

-   method

-   width

-   unit

-   source


不得声称不同broadening结果可直接比较而无说明。

----------

# 30. Combined Band + DOS Compatibility

Phase 10H-3将实现combined view，本阶段必须定义兼容条件。

两个artifact只有在以下条件满足时才可直接组合：

-   same structure identity

-   same atom count

-   same species ordering

-   same frequency unit或可无损转换

-   same imaginary frequency convention

-   compatible source calculation

-   compatible NAC/LO-TO policy

-   compatible normalization metadata

-   compatible frequency range

-   compatible provenance family


建议validator输出：

```text
compatible
convertible
incompatible

```

不得简单因为两个artifact都有frequency axis就组合。

----------

# 31. Source / Provenance Contract

建议：

```json
{
  "producer": "unknown",
  "producer_version": null,
  "calculation_method": null,
  "force_constants_source": null,
  "supercell_matrix": null,
  "primitive_matrix": null,
  "nac": {
    "enabled": false,
    "direction_policy": null
  },
  "input_sha256": null,
  "adapter_version": null
}

```

字段按真实项目规范调整。

必须记录：

-   source software

-   source version

-   calculation type

-   structure identity

-   primitive/supercell relation，若有

-   NAC status

-   adapter version

-   input hash


不得包含：

-   absolute local path

-   username

-   hostname

-   token

-   environment dump

-   remote URL，除非项目统一provenance允许且安全；本阶段建议禁止


----------

# 32. NAC / LO-TO Metadata

本阶段不计算NAC，但必须记录：

```text
non-analytical correction

```

至少支持：

```json
{
  "nac": {
    "enabled": false,
    "gamma_direction": null
  }
}

```

如果enabled：

-   必须有source metadata

-   Gamma方向策略必须明确

-   不得让validator自行重算

-   combined band/DOS兼容性需考虑


不得省略NAC状态后假设不存在。

----------

# 33. Summary Contract

建议建立：

```text
phase10h.phonon_summary.v1

```

至少包含：

```json
{
  "schema_version": "phase10h.phonon_summary.v1",
  "structure_identity": "...",
  "atom_count": 2,
  "branch_count": 6,
  "qpoint_count": 101,
  "segment_count": 4,
  "frequency_unit": "terahertz",
  "frequency_min": -1.2,
  "frequency_max": 15.4,
  "imaginary_mode_count": 3,
  "near_zero_mode_count": 3,
  "dos_available": true,
  "projected_dos_available": false,
  "nac_enabled": false,
  "warnings": []
}

```

用途：

-   JSON-only preview

-   planner/runtime metadata

-   future frontend summary

-   over-budget fallback


不得复制完整band或DOS arrays。

----------

# 34. Manifest Contract

建议：

```text
phase10h.phonon_manifest.v1

```

允许artifacts：

```text
phonon_band.json
phonon_dos.json
phonon_summary.json
phonon_manifest.json

```

Phase 10H-4后可加入：

```text
phonon_modes.json

```

本阶段不得默认包含eigenvectors。

Manifest必须包含：

-   exact artifact order

-   schema

-   media type

-   size

-   hash

-   structure identity

-   security markers

-   no executable assets

-   no external URLs


----------

# 35. Caps and Budgets

必须定义application-owned caps。

至少包括：

-   max atoms

-   max branches

-   max q-points

-   max path segments

-   max labels

-   max DOS grid points

-   max projected DOS series

-   max total numeric values

-   max metadata bytes

-   max warnings

-   max artifact bytes

-   max degeneracy groups


必须验证：

```text
qpoints × branches

```

以及：

```text
dos_points × projections

```

使用overflow-safe乘法。

必须在大规模allocation前检查。

----------

# 36. Deterministic Ordering

必须固定：

-   q-point order

-   segment order

-   branch order

-   label normalization order

-   projection order

-   warning order

-   manifest artifact order

-   provenance key order

-   degeneracy group order


相同输入必须得到相同canonical JSON hash。

不得在canonical payload中加入：

-   current timestamp

-   random UUID

-   environment path

-   unordered map输出

-   library object repr


结构identity应：

-   content-derived

-   或来自validated canonical structure artifact


----------

# 37. Typed Errors

至少定义：

```text
PHONON_SCHEMA_UNSUPPORTED
PHONON_STRUCTURE_IDENTITY_REQUIRED
PHONON_ATOM_COUNT_INVALID
PHONON_SPECIES_ORDER_INVALID
PHONON_RECIPROCAL_CONVENTION_UNSUPPORTED
PHONON_QPOINT_COORDINATE_SYSTEM_UNSUPPORTED
PHONON_QPOINT_SHAPE_INVALID
PHONON_QPOINT_NONFINITE
PHONON_QPOINT_INDEX_INVALID
PHONON_QPOINT_DISTANCE_NONMONOTONIC
PHONON_PATH_SEGMENT_INVALID
PHONON_PATH_LABEL_INVALID
PHONON_FREQUENCY_UNIT_UNSUPPORTED
PHONON_FREQUENCY_NONFINITE
PHONON_FREQUENCY_SHAPE_INVALID
PHONON_BRANCH_COUNT_MISMATCH
PHONON_BRANCH_INDEX_INVALID
PHONON_IMAGINARY_ENCODING_UNSUPPORTED
PHONON_ZERO_TOLERANCE_INVALID
PHONON_DEGENERACY_GROUP_INVALID
PHONON_DOS_GRID_INVALID
PHONON_DOS_NONFINITE
PHONON_DOS_SHAPE_INVALID
PHONON_DOS_NORMALIZATION_UNSUPPORTED
PHONON_DOS_INTEGRAL_MISMATCH
PHONON_PROJECTED_DOS_IDENTITY_INVALID
PHONON_PROJECTED_DOS_DUPLICATE
PHONON_BAND_DOS_STRUCTURE_MISMATCH
PHONON_BAND_DOS_UNIT_MISMATCH
PHONON_BAND_DOS_SOURCE_INCOMPATIBLE
PHONON_CAP_EXCEEDED
PHONON_METADATA_LIMIT_EXCEEDED
PHONON_EXTERNAL_REFERENCE_FORBIDDEN

```

----------

# 38. Warnings

建议：

```text
PHONON_SMALL_IMAGINARY_FREQUENCY
PHONON_ACOUSTIC_MODES_NOT_CORRECTED
PHONON_SOURCE_SOFTWARE_UNKNOWN
PHONON_NAC_STATUS_UNKNOWN
PHONON_DEGENERACY_SOURCE_UNAVAILABLE
PHONON_DOS_INTEGRAL_APPROXIMATE
PHONON_PROJECTED_DOS_SUM_MISMATCH
PHONON_BAND_CONNECTIVITY_SOURCE_ORDER_ONLY
PHONON_HIGH_SYMMETRY_LABEL_NORMALIZED

```

warning排序必须稳定。

错误和warning不得包含：

-   raw large arrays

-   stack traces

-   local paths

-   secrets

-   library internal repr


----------

# 39. Validation Architecture

建议分层：

## 39.1 Shared Validation

-   schema

-   structure identity

-   atom metadata

-   reciprocal convention

-   units

-   provenance

-   security

-   caps


## 39.2 Band Validation

-   q-points

-   path segments

-   distances

-   branches

-   branch count

-   frequency values

-   imaginary encoding

-   degeneracy


## 39.3 DOS Validation

-   frequency grid

-   total DOS

-   projected DOS

-   normalization

-   integration

-   broadening metadata


## 39.4 Compatibility Validation

-   band + DOS compatibility

-   source consistency

-   unit conversion compatibility

-   structure identity

-   NAC


不得让frontend自行承担scientific validation。

----------

# 40. Independent Reference Tests

必须建立至少两条独立验证路径。

建议：

-   production validator

-   independent Python reference functions

-   TypeScript/shared shape validator，若现有架构需要


至少独立验证：

-   reciprocal lattice convention

-   q-point Cartesian conversion

-   path distance

-   THz ↔ cm⁻¹

-   THz ↔ meV

-   imaginary-mode classification

-   DOS trapezoidal integral

-   branch count = 3N

-   deterministic hash


不得由production helper生成expected再验证同一个helper。

----------

# 41. Reference Physical Constants

必须明确物理常数来源。

至少涉及：

-   Planck constant

-   speed of light

-   electronvolt conversion


应使用：

-   approved library constants

-   或项目固定高精度constants


必须记录：

-   source

-   precision

-   canonical values

-   tests


不得使用散落magic numbers。

----------

# 42. Fixtures

新增small、deterministic fixtures。

至少包括：

## 42.1 Stable Cubic Phonon Band

-   small atom count

-   Γ-X-L path

-   no imaginary modes

-   3N branches


## 42.2 Imaginary Mode Band

-   negative frequency

-   near-zero frequency

-   classification tests


## 42.3 Discontinuous Path

-   multiple segments

-   explicit discontinuity

-   labels


## 42.4 Degenerate Modes

-   source-declared degeneracy group

-   no branch merging


## 42.5 Total DOS

-   known integral≈3N

-   includes positive frequencies


## 42.6 DOS with Imaginary Region

-   negative frequency grid

-   nonzero negative-region weight


## 42.7 Projected DOS

-   atom or species projections

-   deterministic ordering


## 42.8 Band + DOS Compatible Pair

-   same structure/source/unit


## 42.9 Band + DOS Incompatible Pair

-   different structure identity或NAC policy


## 42.10 Invalid Cases

-   branch count mismatch

-   nonmonotonic q-distance

-   invalid q shape

-   nonfinite frequency

-   invalid DOS grid

-   projection length mismatch

-   over-cap synthetic


不得提交大型真实phonon数据。

----------

# 43. Unit Tests

至少覆盖：

## Reciprocal

-   row-vector lattice

-   `2π` convention

-   fractional→Cartesian reciprocal conversion

-   orthogonal

-   triclinic


## Q-Points

-   valid

-   invalid shape

-   nonfinite

-   index ordering

-   label normalization

-   segment references

-   discontinuity

-   distance monotonicity


## Frequencies

-   THz

-   cm⁻¹ conversion

-   meV conversion

-   negative frequency

-   near-zero

-   unsupported unit

-   nonfinite


## Branches

-   correct 3N

-   mismatch

-   duplicate index

-   missing branch

-   unequal lengths

-   source order preserved


## Degeneracy

-   valid group

-   duplicate member

-   invalid branch index

-   same branch in multiple conflicting groups


## DOS

-   valid grid

-   nonmonotonic grid

-   total DOS length

-   projected DOS length

-   normalization

-   trapezoidal integral

-   negative-frequency region


## Compatibility

-   compatible

-   convertible unit

-   structure mismatch

-   atom order mismatch

-   NAC mismatch

-   source mismatch


## Caps

-   q-points

-   branches

-   DOS grid

-   projections

-   numeric total

-   bytes

-   overflow


## Security

-   HTML label

-   script-like metadata

-   external URL

-   callback-like key

-   oversized provenance

-   private path


----------

# 44. Cross-Language Contract Tests

如果phonon artifact未来由backend生成、frontend消费，建议增加：

-   backend canonical fixture validation

-   frontend schema/type guard validation

-   same fixture accept/reject comparison

-   enum parity

-   numeric finite checks

-   warning ordering

-   deterministic serialization comparison


若frontend暂不需要完整validator：

-   至少生成shared types

-   或明确backend为权威validator

-   frontend不得重复定义冲突enum


----------

# 45. Compatibility with Existing Static Structure

Phonon artifacts必须引用已验证的structure identity。

必须明确：

-   phonon structure atom order来自canonical structure

-   primitive cell和supercell关系通过provenance记录

-   phonon band不修改structure artifact

-   phonon DOS不修改structure artifact

-   static viewer不直接消费phonon band

-   future phonon animation必须经过Phase 10H-4 eigenvector contract


不得将phonon q-point身份映射为static periodic site identity。

----------

# 46. Compatibility with Trajectory

本阶段必须明确：

-   phonon mode不是trajectory

-   eigenvector animation未来可派生display frames

-   derived display frames不成为trajectory scientific artifact

-   phonon frequency决定oscillation semantics

-   trajectory playback speed合同不可直接复用为物理phonon时间

-   stable atom order可复用，但artifact类型必须独立


不得将phonon mode序列保存成`phase10g.trajectory.v1`并声称科学等价。

----------

# 47. Security

必须验证：

-   no artifact JavaScript

-   no artifact HTML

-   no callback

-   no shader

-   no module

-   no eval

-   no Function constructor

-   no external URL

-   no remote data

-   no notebook execution

-   no script execution

-   no real LLM

-   no arbitrary formula execution

-   no arbitrary unit expression

-   no arbitrary labels with markup

-   no unbounded arrays

-   no integer overflow

-   no metadata recursion abuse

-   no private paths

-   no secrets

-   no telemetry upload


必须输出：

```text
NO_EXTERNAL_NETWORK_REQUESTS
NO_SECRET_PATTERN_HITS

```

----------

# 48. Evidence

新增：

```text
docs/phase10h/evidence/phase10h_phonon_contract/

```

至少包含：

```text
README.md
phonon_band_schema.json
phonon_dos_schema.json
phonon_summary_schema.json
phonon_manifest_schema.json
qpoint_path_schema.json
reciprocal_convention.json
frequency_unit_policy.json
imaginary_frequency_policy.json
branch_identity_policy.json
degeneracy_policy.json
dos_normalization_policy.json
band_dos_compatibility_policy.json
caps.json
stable_band_fixture_result.json
imaginary_band_fixture_result.json
discontinuous_path_result.json
degenerate_modes_result.json
total_dos_result.json
imaginary_dos_result.json
projected_dos_result.json
compatible_pair_result.json
incompatible_pair_result.json
frontend_backend_validation_comparison.json
deterministic_serialization.json
security_audit.json
network_audit.json
artifact_hashes.json

```

不得保存：

-   大型phonon datasets

-   notebook outputs

-   private paths

-   tokens

-   secrets

-   external URLs

-   raw library object dumps

-   crash dumps


----------

# 49. Documentation

新增或更新：

```text
docs/phase10h/phase10h_phonon_contract.md
docs/phase10h/phase10h_reciprocal_convention.md
docs/phase10h/phase10h_qpoint_path_contract.md
docs/phase10h/phase10h_frequency_units.md
docs/phase10h/phase10h_imaginary_frequency_policy.md
docs/phase10h/phase10h_branch_and_degeneracy.md
docs/phase10h/phase10h_phonon_band_schema.md
docs/phase10h/phase10h_phonon_dos_schema.md
docs/phase10h/phase10h_band_dos_compatibility.md
docs/phase10h/phase10h_caps.md
docs/phase10h/phase10h_security.md
docs/phase10h/phase10h_evidence.md
docs/phase10h/phase10h_readiness_matrix.md

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

-   reciprocal lattice convention

-   `2π` policy

-   q-point coordinate system

-   path segments

-   labels

-   frequency canonical unit

-   unit conversions

-   imaginary encoding

-   zero tolerance

-   branch identity

-   degeneracy

-   DOS normalization

-   projected DOS identity

-   band/DOS compatibility

-   eigenvector deferred

-   renderer deferred

-   formal registration deferred


----------

# 50. Readiness Matrix

最终分别判断：

-   reciprocal convention

-   `2π` policy

-   q-point coordinates

-   q-point path

-   segment discontinuities

-   labels

-   path distance

-   frequency unit

-   THz conversion

-   cm⁻¹ conversion

-   meV conversion

-   imaginary frequency

-   near-zero classification

-   acoustic mode metadata

-   branch identity

-   branch count

-   degeneracy

-   atom ordering

-   phonon band schema

-   phonon DOS schema

-   projected DOS

-   DOS normalization

-   DOS integration

-   negative-frequency DOS

-   broadening metadata

-   band/DOS compatibility

-   source/provenance

-   NAC metadata

-   summary

-   manifest

-   caps

-   deterministic serialization

-   validator

-   fixtures

-   reference comparison

-   security

-   phonon band adapter

-   phonon DOS adapter

-   combined renderer

-   eigenvector contract

-   phonon animation

-   formal registration


推荐期望：

```text
reciprocal convention: READY
q-point contract: READY
path/segment contract: READY
frequency unit policy: READY
imaginary frequency policy: READY
zero tolerance: READY
branch identity: READY
branch count policy: READY
degeneracy policy: READY
atom ordering: READY
phonon band schema: READY
phonon DOS schema: READY
projected DOS contract: READY
DOS normalization: READY
band/DOS compatibility: READY
source/provenance: READY
NAC metadata: READY
summary: READY
manifest: READY
caps: READY
deterministic serialization: READY
validator: READY
fixtures: READY
reference comparison: READY
security: READY

phonon band adapter: NOT_READY
phonon DOS adapter: NOT_READY
combined band + DOS: NOT_READY
phonon eigenvector contract: NOT_READY
phonon animation: NOT_READY
formal phonon product registration: NOT_READY

```

不得因为contract完成就将phonon bands或DOS标记READY。

----------

# 51. Checks

至少运行：

```bash
git diff --check
uv lock --check

uv run python -m pytest -q

npm --prefix apps/web test
npm --prefix apps/web run typecheck
npm --prefix apps/web run build

```

并运行：

-   reciprocal convention tests

-   q-point tests

-   path segment tests

-   frequency conversion tests

-   imaginary-mode tests

-   branch tests

-   degeneracy tests

-   DOS tests

-   normalization/integration tests

-   projected DOS tests

-   band/DOS compatibility tests

-   caps/overflow tests

-   deterministic serialization tests

-   frontend/backend comparison

-   artifact validator tests

-   security scan

-   network audit

-   Phase 10 Closure Regression Pack

-   Phase 10G regression

-   service-backed integration

-   no-skipped assertion


本阶段不要求phonon browser evidence，因为尚未实现renderer。

必须如实记录：

-   passed

-   failed

-   skipped

-   unavailable


不得把skipped写成passed。

----------

# 52. Commit / CI

完成contract、validators、tests、evidence和docs后：

```bash
git status --short
git diff --stat
git add <only Phase 10H related files>
git commit -m "Define phonon data contracts"
git push origin master

```

等待current HEAD CI。

必须确认：

-   backend unit success

-   frontend tests success

-   frontend typecheck success

-   frontend build success

-   phonon contract tests success

-   Phase 10 closure success

-   Phase 10G regression success

-   service-backed integration success

-   no-skipped assertion success

-   origin/master matches HEAD

-   git status clean


不得伪造CI。

----------

# 53. 最终报告格式

完成后输出：

# Phase 10H Phonon Contract Result

## 1. Conclusion

PASS / PARTIAL_PASS / FAIL

## 2. Baseline

-   Phase 10G-3 assumed complete:

-   branch:

-   initial status:

-   final HEAD:

-   final status:


## 3. Schema Family

-   phonon band:

-   phonon DOS:

-   phonon summary:

-   phonon manifest:

-   q-point path:

-   current versions:


## 4. Reciprocal Convention

-   real-space lattice:

-   reciprocal formula:

-   `2π`:

-   reciprocal fractional:

-   reciprocal Cartesian:

-   Cartesian unit:

-   triclinic:


## 5. Q-Point Path

-   q-point shape:

-   index:

-   labels:

-   segments:

-   shared endpoints:

-   discontinuities:

-   path distance:

-   ordering:


## 6. Frequency Policy

-   canonical unit:

-   THz:

-   cm⁻¹:

-   meV:

-   physical constants:

-   angular/cyclic distinction:

-   unsupported units:


## 7. Imaginary / Zero Modes

-   encoding:

-   negative values:

-   zero tolerance:

-   near-zero:

-   acoustic modes:

-   source corrections:

-   warnings:


## 8. Branches / Degeneracy

-   branch identity:

-   source order:

-   branch count:

-   full/subset scope:

-   crossings:

-   degeneracy groups:

-   merging policy:


## 9. Atom Ordering

-   structure identity:

-   atom count:

-   species:

-   canonical order:

-   projected DOS identity:

-   future eigenvectors:


## 10. Phonon Band Contract

-   q-points:

-   segments:

-   branches:

-   frequency shape:

-   provenance:

-   security:

-   caps:


## 11. Phonon DOS Contract

-   frequency grid:

-   total DOS:

-   density unit:

-   normalization:

-   integration:

-   negative region:

-   projected DOS:

-   broadening:


## 12. Band / DOS Compatibility

-   structure:

-   atom order:

-   units:

-   imaginary policy:

-   source:

-   NAC:

-   compatible:

-   convertible:

-   incompatible:


## 13. Provenance / NAC

-   producer:

-   version:

-   method:

-   force constants:

-   primitive/supercell:

-   NAC:

-   input hash:

-   private paths:


## 14. Caps

-   atoms:

-   branches:

-   q-points:

-   segments:

-   DOS grid:

-   projections:

-   numeric values:

-   artifact bytes:

-   overflow:


## 15. Validation

-   shared:

-   band:

-   DOS:

-   compatibility:

-   security:

-   typed errors:

-   warning ordering:


## 16. Determinism

-   q-point order:

-   branch order:

-   segment order:

-   projection order:

-   warning order:

-   manifest order:

-   hashes:

-   structure identity:


## 17. Fixtures

-   stable band:

-   imaginary band:

-   discontinuous path:

-   degenerate modes:

-   total DOS:

-   imaginary DOS:

-   projected DOS:

-   compatible pair:

-   incompatible pair:

-   invalid:

-   over-cap:


## 18. Reference Comparison

-   reciprocal conversion:

-   path distance:

-   THz/cm⁻¹:

-   THz/meV:

-   imaginary classification:

-   DOS integral:

-   backend/frontend:

-   differences:


## 19. Security

-   executable content:

-   labels/markup:

-   external references:

-   unit expressions:

-   metadata abuse:

-   caps:

-   private paths:

-   secrets:

-   network:

-   markers:


## 20. Evidence

-   directory:

-   schemas:

-   reciprocal policy:

-   frequency policy:

-   branch policy:

-   DOS policy:

-   compatibility:

-   fixtures:

-   validation comparison:

-   deterministic serialization:

-   security:

-   hashes:


## 21. Tests

-   reciprocal:

-   q-points:

-   path:

-   frequency:

-   imaginary:

-   branches:

-   degeneracy:

-   DOS:

-   projections:

-   compatibility:

-   caps:

-   security:

-   backend full:

-   frontend full:

-   typecheck:

-   build:

-   Phase 10 closure:

-   Phase 10G:

-   service-backed:

-   no-skipped:

-   lock:

-   diff:


## 22. Files

-   schemas/models:

-   validators:

-   conversions:

-   serializers:

-   fixtures:

-   backend tests:

-   shared/frontend tests:

-   evidence:

-   docs:

-   persistent:

-   dependencies/lockfile:


## 23. Deferred

明确列出：

-   phonopy parser/adapter

-   pymatgen phonon adapter

-   phonon bands plot

-   phonon DOS plot

-   combined band + DOS

-   eigenvector payload

-   eigenvector atom mapping

-   complex phase

-   mode animation

-   LO-TO directional rendering

-   Raman/IR activity

-   thermal properties

-   Grüneisen

-   quasi-harmonic

-   official benchmark validation

-   formal phonon tool registration


## 24. Readiness

-   reciprocal:

-   q-points:

-   frequency:

-   imaginary modes:

-   branches:

-   DOS:

-   compatibility:

-   provenance:

-   caps:

-   validator:

-   fixtures:

-   security:

-   band adapter:

-   DOS adapter:

-   combined:

-   eigenvectors:

-   animation:

-   formal product:


## 25. Commit / CI

-   commit:

-   HEAD:

-   CI run:

-   backend:

-   frontend:

-   typecheck:

-   build:

-   phonon contract:

-   Phase 10 closure:

-   Phase 10G:

-   service-backed:

-   no-skipped:

-   origin:

-   status:


## 26. Whether allowed to enter next phase

允许 / 不允许

下一阶段：

```text
Phase 10H-1：Phonon Bands

```

下一阶段只实现批准来源的phonon band adapter、unit normalization、artifact emission、static plot和API evidence基础，不实现phonon DOS、combined view、eigenvectors或animation。

----------

# 54. PASS 判定

PASS必须满足：

-   有真实phonon band schema

-   有真实phonon DOS schema

-   有summary和manifest schema

-   reciprocal lattice convention明确

-   `2π`语义明确

-   q-point坐标系明确

-   path segments明确

-   discontinuity明确

-   high-symmetry label policy明确

-   path distance数学定义明确

-   canonical frequency unit明确

-   THz/cm⁻¹/meV conversion经过reference测试

-   angular/cyclic frequency不混淆

-   imaginary frequency编码明确

-   zero tolerance明确

-   acoustic modes不被静默修正

-   branch identity明确

-   branch order不被validator重排

-   branch count policy明确

-   degeneracy不被静默合并

-   atom ordering明确

-   DOS grid语义明确

-   DOS normalization明确

-   DOS integration policy明确

-   negative-frequency DOS明确

-   projected DOS identity明确

-   band/DOS compatibility明确

-   provenance和NAC metadata明确

-   caps和overflow protection完成

-   deterministic serialization完成

-   validators完成

-   fixtures和独立reference完成

-   no executable content

-   no external URL

-   no secret hits

-   Phase 10 Closure和Phase 10G不回退

-   tests通过

-   CI通过

-   git clean


PARTIAL_PASS仅允许：

-   projected DOS标记PARTIAL_READY，但total DOS contract完整

-   degeneracy仅支持source-declared groups

-   NAC只记录metadata、不做数值验证

-   frontend完整validator暂未实现，但shared types和backend权威validator完整

-   npm audit因既有registry问题不可用


FAIL包括：

-   只有文档，没有validator

-   reciprocal convention不明确

-   `2π`含义不明确

-   q-point坐标系混用

-   THz和angular frequency混淆

-   negative frequencies被取绝对值

-   branch被按频率静默重排

-   degeneracy被合并导致数据丢失

-   branch count与3N不一致却无说明

-   DOS normalization不明确

-   band和DOS无structure/source检查直接组合

-   projected DOS只靠字符串label绑定

-   无caps

-   允许NaN/Infinity

-   允许external URL

-   提前实现animation导致范围膨胀

-   Phase 10G回退

-   CI失败却声明PASS

---END---

---TASK---
 状态：待处理
 # Phase 10H-1：Phonon Bands

进入 Phase 10H-1：Phonon Bands。

可以默认：

-   Phase 10H：Phonon Contract 已完成并通过

-   `phase10h.phonon_band.v1`

-   `phase10h.phonon_dos.v1`

-   `phase10h.phonon_summary.v1`

-   `phase10h.phonon_manifest.v1`

-   `phase10h.qpoint_path.v1`

-   reciprocal lattice convention、`2π` policy、q-point coordinate system、path segment、frequency unit、imaginary-mode encoding、branch identity、degeneracy、atom ordering、caps和security contract均已固定

-   canonical frequency unit已确定

-   THz、cm⁻¹、meV转换已有reference tests

-   phonon band与DOS compatibility contract已定义

-   Phase 10G trajectory product已正式收口

-   Phase 10 Closure Regression Pack保持通过

-   当前branch、HEAD、working tree和Phase 10H CI可视为正确且clean


本阶段不需要重复Phase 10H baseline检查。

本阶段主要目标：

> 为已批准来源的phonon band数据实现安全、deterministic、可验证的adapter、normalization、artifact emission、静态band plot、表格结果、API路径和最小产品预览，为后续Phonon DOS和Combined Band + DOS提供稳定基础。

本阶段只完成：

-   approved phonon band input scope

-   source adapter

-   q-point/path normalization

-   frequency unit conversion

-   imaginary-mode handling

-   branch preservation

-   high-symmetry label normalization

-   phonon band artifact emission

-   summary and manifest

-   static band plot

-   data table

-   API evidence

-   accessibility

-   browser smoke

-   security

-   docs and readiness


本阶段不实现phonon DOS、不实现combined band + DOS、不实现eigenvector、不实现phonon animation。

----------

# 1. 本阶段定位

Phase 10H-1是phonon band的正式数据生产和静态产品预览阶段。

它必须解决：

-   哪些phonon band来源在第一版受支持

-   来源对象如何映射到`phase10h.phonon_band.v1`

-   reciprocal-space约定如何核对

-   q-point path如何规范化

-   high-symmetry label如何规范化

-   branch顺序如何保留

-   frequency单位如何转换

-   imaginary frequency如何显示

-   discontinuous path如何绘制

-   band artifact如何进入正式runtime

-   static plot和table如何安全呈现

-   malformed或不兼容数据如何拒绝

-   browser/API证据如何形成


本阶段不是：

-   phonon计算执行阶段

-   phonopy命令执行阶段

-   DOS阶段

-   eigenvector阶段

-   animation阶段

-   thermal-property阶段
    -正式完整phonon产品收口阶段


----------

# 2. 本阶段目标

必须完成以下十二类工作：

1.  **Phonon band source and adapter audit**

2.  **Approved input format / object scope**

3.  **Q-point and reciprocal normalization**

4.  **Frequency unit normalization**

5.  **Branch、imaginary-mode和degeneracy preservation**

6.  **Band artifact、summary和manifest emission**

7.  **Static phonon band plot**

8.  **Tabular and JSON preview**

9.  **Runtime、registry和API integration基础**

10.  **Browser smoke and accessibility**

11.  **Security、performance和determinism**

12.  **Docs、evidence和readiness closure**


本阶段必须产生真实adapter和真实plot artifact。

如果最终只有contract mapping文档、mock chart或fixture静态截图，没有真实输入→adapter→artifact→preview路径，本阶段必须判定为FAIL。

----------

# 3. 第一版输入范围

优先支持以下来源之一或多个，必须根据仓库现有依赖审计后决定：

```text
phonopy band.yaml / band structure object
pymatgen phonon band structure object
canonical phase10h.phonon_band.v1 JSON

```

推荐优先级：

1.  canonical JSON

2.  已存在依赖中的pymatgen phonon对象

3.  phonopy静态输出文件

4.  其他格式延后


如果仓库已使用phonopy：

-   可以支持`band.yaml`

-   不得运行phonopy命令

-   只允许静态文件解析


如果仓库已有pymatgen：

-   可以适配其phonon band structure对象或安全序列化结果

-   必须核对其reciprocal convention和branch order


本阶段默认不支持：

-   动态执行phonopy

-   force constants计算

-   vasprun.xml phonon提取

-   OUTCAR解析

-   arbitrary YAML object tags

-   pickle

-   notebook object

-   remote URL

-   compressed archive

-   arbitrary plugin adapter


----------

# 4. 严格禁止范围

本阶段不得实现：

-   phonon DOS

-   combined band + DOS

-   eigenvector payload

-   eigenvector parser

-   phonon animation

-   atomic displacement

-   mode selection animation

-   LO-TO directional renderer

-   thermal properties

-   free energy

-   entropy

-   heat capacity

-   Grüneisen parameters

-   quasi-harmonic approximation

-   phonon calculation execution

-   external solver invocation

-   electronic band structure

-   Brillouin zone renderer

-   external API

-   notebook execution

-   script execution

-   real LLM

-   formal full phonon product registration


不得：

-   修改Phase 10H contract语义

-   修改trajectory contract

-   修改static viewer scene

-   静默改变`2π` convention

-   静默改变q-point coordinate system

-   静默重排branches

-   静默按frequency排序branches

-   静默连接跨越discontinuous segment的线

-   静默丢弃negative frequencies

-   静默将negative frequencies取绝对值

-   静默把near-zero全部设为0

-   静默执行ASR correction

-   静默生成high-symmetry labels

-   静默推断缺失atom order

-   允许任意YAML tag构造对象

-   允许NaN或Infinity

-   允许无限q-points/branches

-   允许外部URL

-   允许artifact JavaScript

-   允许HTML/script label

-   允许用户提供任意plot代码

-   通过前端转换掩盖backend artifact错误

-   将band plot标记为officially validated


允许：

-   safe static parser

-   adapter

-   unit conversion

-   canonicalization

-   plot generation

-   table generation

-   API evidence

-   browser smoke

-   tests

-   docs


----------

# 5. 必读实现

开始后直接阅读当前真实代码。

## 5.1 Phase 10H Contract

阅读：

-   phonon band schema

-   q-point path schema

-   summary schema

-   manifest schema

-   validators

-   frequency conversion helpers

-   reciprocal conversion helpers

-   typed errors

-   caps

-   fixtures

-   deterministic serializer


必须直接复用，不建立第二套phonon band模型。

## 5.2 Existing Adapter Patterns

搜索：

```bash
rg -n "adapter|tool_id|artifact emission|summary artifact|manifest|plot artifact" backend packages tests

```

重点阅读：

-   static physics adapters

-   XRD adapter

-   RDF adapter

-   generic plot adapter

-   service-backed runtime

-   artifact validator

-   Tool Registry

-   planner metadata


## 5.3 Existing Plot Infrastructure

搜索：

```bash
rg -n "line plot|series|x_axis|y_axis|plotly|recharts|canvas|svg|chart" apps/web backend packages tests

```

确认：

-   通用line plot contract

-   series cap

-   discontinuity表达

-   axis labels

-   negative values

-   annotations

-   responsive layout

-   PNG/export能力

-   accessibility


## 5.4 Existing Phonon Dependencies

搜索：

```bash
rg -n "phonopy|pymatgen.*phonon|PhononBand|band.yaml|yaml" pyproject.toml uv.lock backend packages tests

```

确认：

-   dependency是否已存在

-   parser能力

-   YAML安全加载方式

-   library version

-   licensing

-   source object semantics


----------

# 6. 修改前输出审计

修改代码前输出：

# Phase 10H-1 Phonon Bands Pre-Implementation Audit

## 1. Existing Source Support

-   canonical JSON:

-   phonopy:

-   pymatgen:

-   other existing formats:

-   current dependencies:

-   safe parser support:

-   gaps:


## 2. Existing Plot Infrastructure

-   line plot contract:

-   discontinuity support:

-   negative y-values:

-   high-symmetry labels:

-   multiple series:

-   accessibility:

-   export:

-   limits:


## 3. Existing Runtime Path

-   registry:

-   planner:

-   adapter base:

-   runtime:

-   artifact validator:

-   manifest:

-   frontend preview:

-   API:

-   evidence helpers:


## 4. Scientific Risks

至少列出：

-   source reciprocal convention mismatch

-   q-point coordinate mismatch

-   path distance mismatch

-   duplicated segment endpoint handling

-   branch transposition

-   branch reorder

-   negative frequency sign loss

-   frequency unit drift

-   angular/cyclic frequency confusion

-   3N branch mismatch

-   missing atom ordering

-   high-symmetry label corruption

-   source NAC ambiguity

-   source ASR ambiguity

-   YAML unsafe construction

-   large band matrix

-   plot line connection across discontinuity

-   candidate/reference overclaim


## 5. Selected Strategy

说明：

-   supported sources:

-   parser:

-   normalization:

-   reciprocal convention:

-   frequency conversion:

-   branch order:

-   labels:

-   path distance:

-   plot:

-   table:

-   adapter:

-   registry visibility:

-   API:

-   browser:

-   security:


## 6. Planned Files

列出：

-   source parser

-   adapter

-   normalizer

-   plot producer

-   table producer

-   registry metadata

-   API tests

-   frontend preview

-   fixtures

-   browser smoke

-   evidence

-   docs

-   persistent


审计后直接继续实现。

----------

# 7. Tool Boundary

建议内部或受限工具ID：

```text
phonon.bands

```

或符合项目命名规范的：

```text
structure.phonon_bands

```

必须审计现有tool naming后选定唯一ID。

本阶段推荐状态：

```text
registered internally / planner-limited

```

正式完整phonon产品注册可以推迟到：

-   Phase 10H-3 combined view完成

-   或独立phonon band产品证据完整后


如果本阶段已有充分API和browser evidence，也可以将band-only tool正式注册，但必须：

-   capability只声明bands

-   DOS=false

-   eigenvectors=false

-   animation=false


不得将其注册成通用`phonon.viewer`并过度宣称。

----------

# 8. Input Contract

Adapter输入必须是批准来源之一。

建议：

```ts
type PhononBandAdapterInput = {
  sourceArtifactId: string;
  sourceFormat:
    | "phase10h.phonon_band.v1"
    | "phonopy_band_yaml"
    | "pymatgen_phonon_band_json";
  frequencyUnitOverride?: ApprovedFrequencyUnit;
  reciprocalConventionOverride?: ApprovedReciprocalConvention;
};

```

Overrides必须：

-   strict allowlist

-   only when source metadata缺失

-   provenance中记录

-   不允许任意字符串


不得允许：

-   arbitrary parser name

-   arbitrary Python class

-   arbitrary URL

-   arbitrary YAML tag

-   arbitrary unit expression

-   callback

-   plot code


----------

# 9. Canonical JSON Path

如果输入已是：

```text
phase10h.phonon_band.v1

```

则流程：

```text
parse
→ validate
→ canonicalize
→ summary
→ manifest
→ plot/table

```

不得：

-   重新推断q-path

-   重排branches

-   改变unit

-   改变negative frequency

-   改变labels


只允许canonical key ordering和明确格式化。

----------

# 10. Phonopy Band YAML Path

如果实现phonopy支持，必须使用安全静态解析。

## 安全要求

-   使用safe loader

-   禁止自定义tag

-   禁止Python object construction

-   禁止anchors造成过度展开，或设置严格cap

-   输入byte cap

-   nesting depth cap

-   sequence length cap

-   mapping key count cap

-   string length cap


不得使用：

```python
yaml.load(...)

```

搭配不安全loader。

## Mapping

必须审计真实phonopy字段，例如：

-   `nqpoint`

-   `npath`

-   `segment_nqpoint`

-   `reciprocal_lattice`

-   `phonon`

-   `q-position`

-   `distance`

-   `band`

-   `frequency`

-   `label`


不得凭假设实现。

必须核对：

-   reciprocal lattice convention

-   q-position coordinate system

-   frequency unit

-   branch ordering

-   segment boundaries

-   labels

-   NAC metadata

-   group velocity等未知字段处理


未知字段：

-   默认忽略并记录bounded warning

-   不得写入任意metadata


----------

# 11. Pymatgen Source Path

如果支持pymatgen对象或JSON：

必须核对：

-   object serialization shape

-   q-point fractional/cartesian semantics

-   branches shape

-   branch definitions

-   labels dictionary

-   distances

-   reciprocal lattice convention

-   structure linkage

-   NAC metadata

-   frequency unit


不得直接将library object dump写入artifact。

必须映射到纯JSON canonical schema。

如果pymatgen对象只能来自内存：

-   adapter必须使用已批准内部对象

-   不接受pickle上传

-   不接受任意Python module path


----------

# 12. Source Detection

格式检测必须：

-   基于显式source format或artifact media/schema

-   可辅以bounded content sniffing

-   不仅依赖扩展名

-   不尝试所有parser直到一个成功


未知格式返回：

```text
PHONON_BAND_FORMAT_UNSUPPORTED

```

ambiguous格式返回：

```text
PHONON_BAND_FORMAT_AMBIGUOUS

```

----------

# 13. Reciprocal Convention Normalization

所有输出必须符合Phase 10H canonical convention。

如果source使用不同convention：

-   必须显式转换

-   provenance记录source和target convention

-   reference tests覆盖

-   q-point coordinates/path distances同步转换


不得只转换reciprocal lattice而不转换path distance。

建议parse report记录：

```json
{
  "source_reciprocal_convention": "crystallographic_no_2pi",
  "target_reciprocal_convention": "physics_2pi",
  "converted": true
}

```

----------

# 14. Q-Point Coordinate Normalization

Canonical输出建议使用：

```text
reciprocal_fractional

```

如果source为reciprocal Cartesian：

-   使用validated reciprocal lattice转换

-   处理triclinic lattice

-   保留source coordinates可选摘要，不写入主payload除非contract允许


必须验证：

-   shape 3

-   finite

-   count一致

-   index连续

-   no duplicate accidental removal


不得自动折回第一Brillouin zone，除非contract明确；本阶段建议不做。

----------

# 15. Path Distance Normalization

优先策略：

-   如果source distance符合contract，验证后使用

-   如果source缺失或不符合canonical unit，使用q-point和reciprocal lattice重新计算

-   provenance记录是否recomputed


必须：

-   使用reciprocal Cartesian metric

-   处理segment discontinuity

-   deterministic

-   reference-tested


不得：

-   使用q-point index作为distance

-   对discontinuous segments画连接线

-   静默修改source order


----------

# 16. Segment Normalization

必须从source中建立明确segments。

支持：

-   source segment counts

-   source branch definitions

-   explicit start/end indices


必须固定：

-   shared endpoint policy

-   duplicate endpoint policy

-   discontinuity flag

-   label propagation


如果source无法可靠恢复segment：

-   typed failure

-   或生成单segment并发出明确warning，仅在科学上安全时


不得通过labels缺失简单猜测segment。

----------

# 17. High-Symmetry Labels

使用Phase 10H normalization policy。

至少处理：

```text
GAMMA
Gamma
\Gamma
Γ

```

输出canonical：

```text
Γ

```

必须：

-   保留source label，若contract允许

-   sanitize

-   bounded length

-   no markup execution

-   no HTML

-   no script

-   no arbitrary LaTeX rendering


未知安全label可以原样作为inert text保留，但必须符合字符和长度策略。

----------

# 18. Frequency Unit Normalization

输出必须使用canonical frequency unit。

如果canonical为：

```text
terahertz

```

则所有source值转换到THz。

必须支持Phase 10H批准的conversion：

-   THz → THz

-   cm⁻¹ → THz

-   meV → THz


转换必须：

-   使用统一constants helper

-   preserve sign

-   finite

-   deterministic

-   tested


不得：

-   对negative frequency丢失sign

-   把angular frequency当THz

-   仅修改unit label不修改数值


parse report必须记录：

```json
{
  "source_frequency_unit": "inverse_centimeter",
  "target_frequency_unit": "terahertz",
  "conversion_applied": true
}

```

----------

# 19. Imaginary Frequency Handling

Canonical输出继续使用：

```text
negative_real

```

如果source使用：

-   negative frequency

-   imaginary flag + magnitude

-   complex notation


必须安全映射为negative real值。

不得：

-   取绝对值

-   使用字符串`i`

-   丢弃模式

-   将small negative自动改0


分类：

```text
imaginary
near_zero
positive

```

只作为summary/plot派生状态。

原始canonical数值必须保留转换后结果。

----------

# 20. Zero Tolerance and ASR

使用Phase 10H既定tolerance。

Adapter不得：

-   修改原始frequency

-   自动执行acoustic sum rule correction

-   自动把Gamma前三支归零


可以生成warnings：

```text
PHONON_ACOUSTIC_MODES_NOT_CORRECTED
PHONON_SMALL_IMAGINARY_FREQUENCY

```

如果source声明ASR已应用，记录provenance。

----------

# 21. Branch Preservation

输出branch顺序必须按source order保持。

必须检查：

-   branch index连续

-   branch count

-   每branch长度

-   3N policy

-   subset policy


不得：

-   每个q-point独立排序frequency

-   按平均frequency重排

-   自动连接crossing branches

-   自动合并degenerate branches


parse report记录：

```json
{
  "branch_order_policy": "source_preserved",
  "branch_reordered": false
}

```

如果source本身使用q-point-major矩阵，转置时必须有shape tests。

----------

# 22. Degeneracy

本阶段只保留：

-   source-declared degeneracy

-   或不提供


不得自动从frequency tolerance生成权威degeneracy。

如果source没有：

-   summary中标记unknown

-   不影响band plot


plot不得因degeneracy而合并series。

----------

# 23. Atom Ordering and Structure Identity

Adapter必须要求或恢复：

-   canonical structure identity

-   atom count

-   species order


来源可能包括：

-   linked structure artifact

-   source metadata

-   adapter input关联


必须验证：

```text
branch_count == 3 × atom_count

```

除非批准subset scope。

不得：

-   只从branch count反推atom order

-   仅用formula作为identity

-   丢失species ordering


如果无法建立structure identity：

```text
PHONON_STRUCTURE_IDENTITY_REQUIRED

```

----------

# 24. Phonon Band Parse Report

建议新增：

```text
phase10h.phonon_band_parse_report.v1

```

至少包含：

```json
{
  "schema_version": "phase10h.phonon_band_parse_report.v1",
  "detected_format": "phonopy_band_yaml",
  "qpoint_count": 101,
  "segment_count": 4,
  "branch_count": 6,
  "source_frequency_unit": "terahertz",
  "target_frequency_unit": "terahertz",
  "source_reciprocal_convention": "physics_2pi",
  "target_reciprocal_convention": "physics_2pi",
  "path_distance_recomputed": false,
  "labels_normalized": 1,
  "branch_order_policy": "source_preserved",
  "imaginary_mode_count": 2,
  "warnings": [],
  "input_sha256": "...",
  "deterministic": true
}

```

不得包含：

-   raw full source

-   absolute path

-   environment dump

-   stack trace

-   Python repr


----------

# 25. Adapter Output

至少输出：

```text
phonon_band.json
phonon_band_summary.json
phonon_band_parse_report.json
phonon_band_plot.json
phonon_band_table.json
phonon_manifest.json

```

如果项目plot artifact命名已有规范，按现有规范调整。

每个artifact必须：

-   schema明确

-   media type allowlisted

-   size

-   hash

-   provenance

-   security metadata

-   deterministic order


不得输出：

-   renderer bundle

-   HTML

-   JS

-   external assets

-   raw library object

-   source file副本，除非统一artifact policy批准


----------

# 26. Static Plot Contract

优先复用现有line plot contract。

必须支持：

-   x-axis：q-path distance

-   y-axis：frequency

-   multiple branch series

-   negative frequency region

-   zero line

-   segment discontinuities

-   high-symmetry ticks

-   unit label

-   optional imaginary region shading，若现有plot contract安全支持


不得：

-   将discontinuous segment连接

-   将negative频率翻到positive

-   将每branch随机配色作为唯一识别

-   依赖远程字体

-   依赖外部JS


----------

# 27. Plot Series Policy

每个branch为一条series，或使用批准的multi-series表示。

必须：

-   stable branch order

-   stable branch ID

-   no missing q-point

-   discontinuity通过null break、segment series或显式break表达

-   不复制超大数据超过plot cap


如果branch数较多：

-   可使用单一visual style

-   tooltip/legend不需要列出全部branch

-   不得因UI简化丢失scientific data


Legend建议：

```text
Phonon branches

```

而不是列出`Branch 0...Branch 299`。

----------

# 28. Plot Axes

## X Axis

标签建议：

```text
Wave vector path

```

ticks显示：

-   Γ

-   X

-   L

-   等high-symmetry labels


不得将x-axis仅标为`q-point index`，除非fallback明确。

## Y Axis

例如：

```text
Frequency (THz)

```

必须来自canonical unit。

Zero line必须清晰。

Imaginary频率显示在zero以下。

----------

# 29. Discontinuous Segment Rendering

必须显式断线。

可选实现：

-   null separator

-   separate series per segment

-   plot contract segment break


必须验证：

-   Γ-X和L-W等不连续段不被连线

-   shared endpoints不出现错误双线

-   labels/ticks顺序稳定


不得只靠大distance jump让chart library自动判断。

----------

# 30. Imaginary-Mode Plot Policy

Negative frequencies必须正常绘制。

可以：

-   zero以下区域轻量标注

-   显示“Imaginary modes”文字说明


不得：

-   使用红色作为唯一语义

-   自动隐藏

-   镜像为positive

-   标为error而不显示


辅助文本必须说明：

```text
Negative plotted values represent imaginary phonon modes under the contract's negative-real encoding.

```

----------

# 31. Table Artifact

建议提供long-form或branch-oriented table。

例如：

```text
qpoint_index
segment_index
path_distance
q_x
q_y
q_z
label
branch_index
frequency
classification

```

必须：

-   deterministic row order

-   q-point-major或branch-major固定

-   bounded row count

-   no HTML

-   unit metadata

-   imaginary classification派生

-   original values不修改


如果完整table超cap：

-   输出summary table

-   完整band JSON仍保留

-   不允许生成巨大CSV导致内存风险


----------

# 32. Summary

复用`phase10h.phonon_summary.v1`。

至少填充：

-   structure identity

-   atom count

-   branch count

-   q-point count

-   segment count

-   frequency min/max

-   imaginary count

-   near-zero count

-   unit

-   NAC status

-   ASR status

-   source

-   warnings


不得：

-   把small imaginary mode自动视为稳定

-   声称结构稳定/不稳定的最终科学结论

-   把band图当官方benchmark


可显示中性文字：

```text
2 modes fall below the configured imaginary-mode threshold.

```

----------

# 33. Manifest

使用Phase 10H manifest contract。

artifact order固定，例如：

1.  phonon_band.json

2.  phonon_band_summary.json

3.  phonon_band_parse_report.json

4.  phonon_band_plot.json

5.  phonon_band_table.json

6.  phonon_manifest.json


必须包含：

-   schema

-   media type

-   size

-   sha256

-   structure identity

-   source

-   security markers


不得包含：

-   JS

-   HTML

-   external URL

-   eigenvectors

-   DOS


----------

# 34. Adapter Registration

建议tool metadata：

```json
{
  "tool_id": "phonon.bands",
  "category": "phonon",
  "display_name": "Phonon Bands",
  "description": "Normalize and visualize phonon branch frequencies along a validated q-point path.",
  "input_contract": "approved phonon band source",
  "output_contract": "phase10h.phonon_band.v1",
  "execution_mode": "service_backed",
  "deterministic": true,
  "network_access": false
}

```

字段按真实registry调整。

Capabilities：

```text
phonon_bands: true
imaginary_modes: true
high_symmetry_path: true
unit_conversion: true
static_plot: true
table: true
phonon_dos: false
eigenvectors: false
animation: false
thermal_properties: false

```

不得过度宣称。

----------

# 35. Planner Policy

如果planner-visible，正向请求：

```text
Plot the phonon bands for this calculation.
Show imaginary phonon modes along the q-point path.
Visualize the phonon dispersion.

```

应选择phonon band tool。

负向请求：

```text
Show phonon DOS.
Animate this phonon mode.
Calculate thermal conductivity.
Compute phonons from this structure.

```

不得由本tool伪完成。

推荐本阶段：

```text
planner-visible: limited

```

只有当输入artifact已是approved phonon band source时可选择。

不得从普通structure直接承诺计算phonons。

----------

# 36. PlanValidator

必须验证：

-   approved input kind

-   source format

-   structure identity

-   caps

-   unit override allowlist

-   reciprocal override allowlist

-   no DOS request

-   no animation request

-   no computation request

-   no external URL

-   no arbitrary plot code


typed codes建议：

```text
PHONON_BAND_INPUT_REQUIRED
PHONON_BAND_SOURCE_FORMAT_UNSUPPORTED
PHONON_BAND_STRUCTURE_MISMATCH
PHONON_BAND_OPTION_UNSUPPORTED
PHONON_BAND_DOS_UNSUPPORTED
PHONON_BAND_ANIMATION_UNSUPPORTED
PHONON_CALCULATION_UNSUPPORTED

```

不得放宽PlanValidator。

----------

# 37. API Evidence

必须通过正式service-backed路径。

至少覆盖：

## Valid Canonical JSON

```text
approved artifact
→ tool selection/direct tool request
→ PlanValidator
→ runtime
→ adapter
→ band/summary/plot/table/manifest
→ artifact retrieval

```

## Valid External Static Source

如果实现phonopy或pymatgen适配：

-   parse

-   normalize

-   artifact emission

-   stable hash


## Imaginary Modes

-   negative frequencies保留

-   plot在zero以下

-   summary count正确


## Discontinuous Path

-   plot断线

-   labels正确


## Invalid Input

-   typed failure

-   no partial artifacts


## Over-Cap

-   allocation前拒绝

-   no crash

-   no plot build


----------

# 38. Frontend Preview

本阶段需要最小正式产品预览。

至少显示：

-   tool title

-   structure identity摘要

-   atom count

-   branch count

-   q-point count

-   frequency range

-   unit

-   imaginary count

-   plot

-   table/JSON tabs

-   source

-   warnings

-   artifact downloads


不得显示：

-   DOS

-   eigenvector

-   animation controls

-   thermal-property结果

-   stability最终结论


----------

# 39. Accessibility

Plot和预览必须可访问。

要求：

-   plot有标题

-   plot有文本摘要

-   axis含unit

-   high-symmetry path可读

-   negative frequency语义有文本说明

-   table可键盘访问

-   warnings不只靠颜色

-   focus order正确

-   200% zoom可用

-   mobile横向溢出有合理处理


建议文本摘要：

```text
Phonon band structure with 6 branches across 101 q-points. Frequency range: -1.2 to 15.4 THz. Two imaginary modes are present below the configured threshold.

```

不得只提供canvas而无语义fallback。

----------

# 40. Mobile

至少支持：

-   responsive plot

-   horizontal scrolling或压缩策略

-   readable labels

-   summary

-   warnings

-   table fallback

-   artifact download


要求：

-   high-symmetry ticks不全部重叠

-   tooltip不作为唯一数据访问方式

-   no scroll trap

-   touch target合格


本阶段不要求复杂3D或动画。

----------

# 41. Plot Performance

必须设置：

-   max q-points

-   max branches

-   max plotted values

-   max table rows


超过interactive plot cap：

-   artifact仍有效

-   plot进入degraded或summary-only

-   table可分页或只显示sample

-   no browser freeze


超过hard contract cap：

-   adapter拒绝


typed warning：

```text
PHONON_BAND_PLOT_DEGRADED

```

不得：

-   在前端一次生成超大SVG节点

-   为每个point创建DOM element

-   将全部branch放入巨大legend


----------

# 42. Determinism

必须验证：

-   source mapping稳定

-   q-point order稳定

-   segment order稳定

-   branch order稳定

-   label normalization稳定

-   unit conversion稳定

-   warning order稳定

-   table row order稳定

-   manifest order稳定

-   plot series order稳定

-   hashes稳定


PNG截图hash不作为跨浏览器一致性要求。

----------

# 43. Security

必须验证：

-   no unsafe YAML loader

-   no Python object construction

-   no pickle

-   no eval

-   no literal eval

-   no shell

-   no notebook execution

-   no script execution

-   no external URL

-   no remote source

-   no HTML label execution

-   no SVG script

-   no artifact JavaScript

-   no arbitrary plot code

-   no arbitrary unit expression

-   no callback

-   no oversized YAML expansion

-   no metadata recursion abuse

-   no private path

-   no secrets

-   no telemetry upload


必须输出：

```text
NO_EXTERNAL_NETWORK_REQUESTS
NO_SECRET_PATTERN_HITS

```

----------

# 44. Fixtures

新增small、deterministic fixtures。

至少：

## 44.1 Stable Canonical Band

-   2 atoms

-   6 branches

-   Γ-X-L

-   no imaginary modes


## 44.2 Imaginary Band

-   negative frequency

-   near-zero frequency

-   zero line


## 44.3 Discontinuous Path

-   Γ-X | L-W

-   explicit break


## 44.4 Triclinic Reciprocal Case

-   reciprocal conversion

-   path distance


## 44.5 Label Normalization

-   GAMMA / `\Gamma`

-   canonical Γ


## 44.6 Source Unit Conversion

-   cm⁻¹ source

-   meV source


## 44.7 Degeneracy Metadata

-   source-declared group

-   separate branches


## 44.8 Invalid Branch Shape

## 44.9 Branch Count Mismatch

## 44.10 Over-Cap Synthetic

不得提交大型真实dataset。

----------

# 45. Unit Tests

至少覆盖：

## Source Detection

-   canonical JSON

-   phonopy，若支持

-   pymatgen，若支持

-   unsupported

-   ambiguous


## Q-Point Mapping

-   fractional

-   Cartesian

-   reciprocal conversion

-   triclinic

-   distance

-   segment break


## Labels

-   Gamma normalization

-   duplicate labels

-   unsafe markup

-   bounded length


## Frequencies

-   THz

-   cm⁻¹

-   meV

-   negative

-   near-zero

-   nonfinite

-   unsupported unit


## Branches

-   source order

-   q-major transpose

-   correct 3N

-   mismatch

-   unequal length

-   no automatic sorting


## Plot

-   series count

-   discontinuity

-   negative region

-   axis units

-   high-symmetry ticks

-   degraded cap


## Table

-   row order

-   classification

-   labels

-   unit metadata

-   cap


## Artifacts

-   schema

-   summary

-   report

-   manifest

-   hashes

-   order

-   no executable assets


## Security

-   unsafe YAML tags

-   anchors/expansion

-   HTML labels

-   external URL

-   callback-like metadata

-   private path


----------

# 46. API Tests

覆盖：

-   canonical valid

-   supported source valid

-   imaginary modes

-   discontinuous path

-   unit conversion

-   invalid source

-   structure mismatch

-   over-cap

-   deterministic replay

-   artifact retrieval

-   no partial artifacts


----------

# 47. Browser Smoke Evidence

新增：

```text
docs/phase10h/evidence/phase10h1_phonon_bands/

```

## Chromium

覆盖：

-   tool result

-   stable band plot

-   imaginary band

-   discontinuous path

-   table

-   JSON fallback

-   degraded plot

-   invalid state

-   accessibility

-   no external network


## Firefox

smoke：

-   plot

-   labels

-   negative frequencies

-   table fallback

-   console/network


## WebKit

smoke：

-   responsive plot

-   labels

-   table/JSON fallback

-   console/network


## Mobile

smoke：

-   summary

-   responsive plot

-   label handling

-   warning

-   table fallback

-   no scroll trap


----------

# 48. Browser Evidence Assertions

记录：

-   browser version

-   viewport

-   tool ID

-   source format

-   schema

-   atom count

-   branch count

-   q-point count

-   segment count

-   frequency unit

-   min/max

-   imaginary count

-   plot mode

-   series count

-   table rows

-   warnings

-   console errors

-   network requests


必须验证：

-   negative值显示在zero以下

-   discontinuity未连接

-   labels正确

-   unit正确

-   no branch reorder

-   summary一致

-   no external network

-   no artifact JS

-   no capability overclaim


----------

# 49. Evidence Files

至少包含：

```text
README.md
format_scope.json
source_mapping_policy.json
reciprocal_normalization.json
frequency_conversion_results.json
branch_preservation.json
label_normalization.json
path_segment_mapping.json
parse_report_schema.json
stable_band_result.json
imaginary_band_result.json
discontinuous_path_result.json
triclinic_result.json
degeneracy_result.json
plot_contract_result.json
table_contract_result.json
api_valid_canonical.json
api_valid_source.json
api_imaginary.json
api_invalid.json
api_over_cap.json
deterministic_replay.json
browser_chromium.json
browser_firefox.json
browser_webkit.json
browser_mobile.json
accessibility_audit.json
performance_metrics.json
security_audit.json
network_audit.json
artifact_hashes.json

```

截图建议：

```text
01_stable_phonon_bands.png
02_imaginary_modes.png
03_discontinuous_path.png
04_high_symmetry_labels.png
05_phonon_band_table.png
06_degraded_plot.png
07_invalid_input.png
08_mobile_phonon_bands.png

```

不得保存：

-   大型source file

-   unsafe YAML payload

-   private path

-   token

-   secret

-   raw library dump

-   browser cache

-   full traces


----------

# 50. Dependency Policy

优先不新增依赖。

如果已有：

-   PyYAML

-   phonopy

-   pymatgen

-   chart library


则复用。

如果没有phonopy/pymatgen：

-   优先只支持canonical JSON

-   或实现有限safe band.yaml parser

-   不要为了本阶段引入庞大计算依赖


如新增YAML依赖，必须：

-   security audit

-   safe loader

-   lockfile更新

-   license记录


检查：

```bash
uv lock --check
npm --prefix apps/web ls --depth=0
npm --prefix apps/web run build

```

----------

# 51. Documentation

新增或更新：

```text
docs/phase10h/phase10h1_phonon_bands.md
docs/phase10h/phase10h1_phonon_band_source_scope.md
docs/phase10h/phase10h1_phonon_band_mapping.md
docs/phase10h/phase10h1_phonon_band_plot_contract.md
docs/phase10h/phase10h1_phonon_band_table.md
docs/phase10h/phase10h1_phonon_band_api_evidence.md
docs/phase10h/phase10h1_phonon_band_accessibility.md
docs/phase10h/phase10h1_phonon_band_security.md
docs/phase10h/phase10h1_phonon_band_readiness_matrix.md

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

-   supported sources

-   deferred sources

-   reciprocal normalization

-   frequency conversion

-   branch preservation

-   imaginary-mode display

-   path discontinuity

-   labels

-   plot/table contracts

-   planner visibility

-   API path

-   DOS deferred

-   eigenvectors deferred

-   animation deferred


----------

# 52. Readiness Matrix

最终分别判断：

-   source scope

-   canonical JSON adapter

-   phonopy adapter

-   pymatgen adapter

-   safe parsing

-   reciprocal normalization

-   q-point normalization

-   path distance

-   segment discontinuity

-   label normalization

-   frequency conversion

-   imaginary frequency

-   near-zero classification

-   ASR metadata

-   branch preservation

-   branch count

-   degeneracy metadata

-   structure identity

-   phonon band artifact

-   summary

-   parse report

-   manifest

-   static plot

-   table

-   degraded plot

-   API evidence

-   frontend preview

-   accessibility

-   mobile

-   browser smoke

-   security

-   formal band tool registration

-   phonon DOS

-   combined view

-   eigenvectors

-   animation


推荐期望：

```text
source scope: READY
canonical JSON adapter: READY
phonopy adapter: READY or DEFERRED_BY_DESIGN
pymatgen adapter: READY or DEFERRED_BY_DESIGN
safe parsing: READY
reciprocal normalization: READY
q-point/path normalization: READY
segment discontinuity: READY
label normalization: READY
frequency conversion: READY
imaginary frequencies: READY
branch preservation: READY
branch count validation: READY
structure identity: READY
phonon band artifact: READY
summary: READY
parse report: READY
manifest: READY
static plot: READY
table: READY
API evidence: READY
frontend preview: READY
accessibility: READY
mobile: READY
browser smoke: READY
security: READY

formal phonon band tool registration: READY or PARTIAL_READY
phonon DOS: NOT_READY
combined band + DOS: NOT_READY
eigenvector contract: NOT_READY
phonon animation: NOT_READY

```

----------

# 53. Checks

至少运行：

```bash
git diff --check
uv lock --check

uv run python -m pytest -q

npm --prefix apps/web test
npm --prefix apps/web run typecheck
npm --prefix apps/web run build

```

并运行：

-   phonon band source parser tests

-   reciprocal normalization tests

-   q-point/path tests

-   unit conversion tests

-   imaginary-mode tests

-   branch preservation tests

-   label normalization tests

-   plot tests

-   table tests

-   adapter tests

-   API integration

-   frontend preview tests

-   accessibility tests

-   Chromium smoke

-   Firefox smoke

-   WebKit smoke

-   mobile smoke

-   security scan

-   network audit

-   Phase 10 Closure Regression Pack

-   Phase 10G regression

-   Phase 10H contract regression

-   service-backed integration

-   no-skipped assertion


必须如实记录：

-   passed

-   failed

-   skipped

-   unavailable


不得把skipped写成passed。

----------

# 54. Commit / CI

完成adapter、plot、tests、evidence和docs后：

```bash
git status --short
git diff --stat
git add <only Phase 10H-1 related files>
git commit -m "Add phonon band adapter and visualization"
git push origin master

```

等待current HEAD CI。

必须确认：

-   backend unit success

-   frontend tests success

-   frontend typecheck success

-   frontend build success

-   phonon band tests success

-   API integration success

-   browser smoke success

-   Phase 10 Closure success

-   Phase 10G regression success

-   Phase 10H contract success

-   service-backed integration success

-   no-skipped assertion success

-   origin/master matches HEAD

-   git status clean


不得伪造CI。

----------

# 55. 最终报告格式

完成后输出：

# Phase 10H-1 Phonon Bands Result

## 1. Conclusion

PASS / PARTIAL_PASS / FAIL

## 2. Baseline

-   Phase 10H assumed complete:

-   branch:

-   initial status:

-   final HEAD:

-   final status:


## 3. Source Scope

-   canonical JSON:

-   phonopy:

-   pymatgen:

-   deferred:

-   detection:

-   safe parsing:


## 4. Adapter Architecture

-   source parser:

-   normalizer:

-   validator:

-   serializer:

-   summary:

-   parse report:

-   manifest:

-   runtime:


## 5. Reciprocal / Q-Point Mapping

-   source convention:

-   target convention:

-   `2π`:

-   q-point source system:

-   canonical system:

-   path distance:

-   triclinic:

-   conversions:


## 6. Path / Labels

-   segments:

-   shared endpoints:

-   discontinuities:

-   label normalization:

-   Gamma:

-   unsafe labels:

-   ordering:


## 7. Frequency Mapping

-   source units:

-   canonical unit:

-   THz:

-   cm⁻¹:

-   meV:

-   sign:

-   near-zero:

-   ASR:


## 8. Branches / Degeneracy

-   branch order:

-   q-major transpose:

-   branch count:

-   3N:

-   crossings:

-   degeneracy:

-   reordering:


## 9. Structure Identity

-   identity:

-   atom count:

-   species:

-   atom order:

-   mismatch behavior:


## 10. Artifacts

-   phonon band:

-   summary:

-   parse report:

-   plot:

-   table:

-   manifest:

-   hashes:

-   provenance:

-   security:


## 11. Plot

-   series:

-   x-axis:

-   y-axis:

-   units:

-   zero line:

-   imaginary region:

-   discontinuities:

-   labels:

-   degraded mode:


## 12. Table

-   columns:

-   row order:

-   classification:

-   labels:

-   unit metadata:

-   row cap:

-   fallback:


## 13. Tool / Planner

-   tool ID:

-   registry:

-   planner visibility:

-   valid routing:

-   DOS rejection:

-   animation rejection:

-   computation rejection:

-   PlanValidator:


## 14. API Evidence

-   canonical valid:

-   source valid:

-   imaginary:

-   discontinuous:

-   invalid:

-   over-cap:

-   artifact retrieval:

-   runtime path:


## 15. Frontend / Accessibility

-   product preview:

-   summary:

-   plot:

-   table:

-   JSON fallback:

-   keyboard:

-   screen reader text:

-   200% zoom:

-   mobile:


## 16. Browser Smoke

-   Chromium:

-   Firefox:

-   WebKit:

-   mobile:

-   labels:

-   negative values:

-   discontinuities:

-   console:

-   network:


## 17. Performance

-   q-points:

-   branches:

-   plotted values:

-   table rows:

-   degraded threshold:

-   render behavior:

-   memory proxy:


## 18. Determinism

-   q-point order:

-   segment order:

-   branch order:

-   label order:

-   warning order:

-   plot series:

-   table rows:

-   manifest:

-   hashes:


## 19. Security

-   YAML loader:

-   object construction:

-   eval/pickle:

-   external references:

-   labels:

-   plot code:

-   metadata:

-   caps:

-   private paths:

-   secrets:

-   network:

-   markers:


## 20. Evidence

-   directory:

-   source mapping:

-   reciprocal:

-   frequency:

-   branches:

-   plot:

-   table:

-   API:

-   browser:

-   accessibility:

-   security:

-   screenshots:

-   hashes:


## 21. Tests

-   source parser:

-   reciprocal:

-   q-points:

-   path:

-   labels:

-   frequency:

-   imaginary:

-   branches:

-   plot:

-   table:

-   adapter:

-   API:

-   frontend:

-   accessibility:

-   Chromium:

-   Firefox:

-   WebKit:

-   mobile:

-   backend full:

-   frontend full:

-   typecheck:

-   build:

-   Phase 10 closure:

-   Phase 10G:

-   Phase 10H:

-   service-backed:

-   no-skipped:

-   lock:

-   diff:


## 22. Files

-   parser:

-   adapter:

-   normalizer:

-   plot producer:

-   table producer:

-   registry:

-   planner:

-   API:

-   frontend:

-   fixtures:

-   tests:

-   browser runners:

-   evidence:

-   docs:

-   persistent:

-   dependencies/lockfile:


## 23. Deferred

明确列出：

-   unsupported phonon source formats

-   phonon DOS

-   projected phonon DOS rendering

-   combined band + DOS

-   eigenvector payload

-   eigenvector atom mapping

-   complex phase

-   phonon animation

-   LO-TO directional rendering

-   Raman/IR activity

-   thermal properties

-   official benchmark validation

-   full phonon product registration，若未完成


## 24. Readiness

-   source adapter:

-   normalization:

-   artifact:

-   plot:

-   table:

-   API:

-   frontend:

-   browser:

-   accessibility:

-   security:

-   phonon bands:

-   DOS:

-   combined:

-   eigenvectors:

-   animation:

-   formal product:


## 25. Commit / CI

-   commit:

-   HEAD:

-   CI run:

-   backend:

-   frontend:

-   typecheck:

-   build:

-   phonon band:

-   API:

-   browser:

-   Phase 10 closure:

-   Phase 10G:

-   Phase 10H:

-   service-backed:

-   no-skipped:

-   origin:

-   status:


## 26. Whether allowed to enter next phase

允许 / 不允许

下一阶段：

```text
Phase 10H-2：Phonon DOS

```

下一阶段只实现total/projected phonon DOS adapter、normalization、artifact、plot、table和API/browser evidence，不实现combined view、eigenvectors或animation。

----------

# 56. PASS 判定

PASS必须满足：

-   有真实phonon band adapter

-   有至少一种正式支持来源

-   canonical JSON路径完整

-   source parsing安全

-   reciprocal convention转换正确

-   q-point坐标正确

-   path distance正确

-   segment discontinuity正确

-   high-symmetry labels正确

-   canonical frequency单位正确

-   THz/cm⁻¹/meV转换正确

-   negative frequency sign保留

-   near-zero分类不修改原值

-   不自动执行ASR

-   branch order保留

-   不按frequency静默重排

-   branch count验证

-   structure identity和atom order验证

-   band artifact生成

-   summary生成

-   parse report生成

-   manifest生成

-   static plot真实工作

-   imaginary modes在zero以下显示

-   discontinuous path不连线

-   table真实工作

-   plot/table caps生效

-   API正式路径闭合

-   frontend preview真实工作

-   accessibility不回退

-   Chromium真实smoke通过

-   Firefox/WebKit/mobile smoke完成或如实记录

-   deterministic replay稳定

-   no unsafe YAML

-   no artifact JS

-   no external network

-   no secret hits

-   Phase 10 Closure、Phase 10G、Phase 10H contract不回退

-   tests通过

-   CI通过

-   git clean


PARTIAL_PASS仅允许：

-   phonopy或pymatgen其中一个来源明确DEFERRED_BY_DESIGN，但canonical JSON和至少一个正式来源完整

-   formal planner visibility保持limited

-   degeneracy仅保留source metadata

-   browser某非主要环境明确unavailable

-   npm audit因既有registry问题不可用


FAIL包括：

-   只有mock plot

-   adapter绕过Phase 10H validator

-   reciprocal convention错误

-   q-path错误

-   discontinuous segments被连接

-   negative frequency被取绝对值

-   branch被静默重排

-   branch count异常被忽略

-   structure identity缺失

-   unsafe YAML loader

-   前端自行修正错误backend数据

-   无API evidence

-   无browser evidence

-   提前实现DOS/eigenvector/animation导致范围膨胀

-   Phase 10H contract回退

-   CI失败却声明PASS

---END---

---TASK---
 状态：待处理
 # Phase 10H-2：Phonon DOS

进入 Phase 10H-2：Phonon DOS。

可以默认：

* Phase 10H：Phonon Contract 已完成并通过
* Phase 10H-1：Phonon Bands 已完成并通过
* `phase10h.phonon_band.v1`
* `phase10h.phonon_dos.v1`
* `phase10h.phonon_summary.v1`
* `phase10h.phonon_manifest.v1`
* reciprocal-space convention、frequency units、imaginary-mode encoding、atom ordering、DOS normalization、projected DOS identity、caps和security contract均已固定
* phonon band adapter、plot、table、API和browser smoke已完成
* canonical frequency unit已固定
* total DOS normalization目标、negative-frequency DOS语义和trapezoidal integration policy已固定
* Phase 10G trajectory产品保持稳定
* Phase 10 Closure Regression Pack保持通过
* 当前branch、HEAD、working tree和Phase 10H-1 CI可视为正确且clean

本阶段不需要重复Phase 10H-1 baseline检查。

本阶段主要目标：

> 为批准来源的phonon density of states数据实现安全、deterministic、可验证的adapter、frequency-grid normalization、total/projected DOS artifact emission、静态DOS plot、表格结果、API路径和浏览器证据，为下一阶段Combined Phonon Band + DOS提供稳定基础。

本阶段只完成：

* approved phonon DOS input scope
* total DOS adapter
* projected DOS adapter，若来源支持
* frequency unit normalization
* DOS density-unit normalization
* normalization/integration validation
* negative-frequency DOS preservation
* broadening metadata
* atom/species projection identity
* DOS artifact emission
* summary and manifest
* static DOS plot
* data table
* API evidence
* accessibility
* browser smoke
* performance/security closure
* docs and readiness

本阶段不实现combined band + DOS、不实现eigenvectors、不实现phonon animation。

---

# 1. 本阶段定位

Phase 10H-2是phonon DOS正式数据生产和产品预览阶段。

它必须解决：

* 哪些phonon DOS来源在第一版受支持
* 来源对象如何映射到`phase10h.phonon_dos.v1`
* frequency grid如何解释
* frequency单位如何转换
* density单位如何转换
* total DOS采用什么normalization
* DOS积分如何验证
* negative-frequency区域如何保留和显示
* projected DOS如何绑定atom或species
* projected DOS总和与total DOS不一致时如何处理
* broadening信息如何记录
* DOS artifact如何进入runtime、API和frontend
* 大型grid/projection如何degraded或refused
* malformed或科学语义不明的数据如何拒绝

本阶段不是：

* phonon band阶段
* combined band + DOS阶段
* eigenvector阶段
* animation阶段
* phonon thermodynamics阶段
* phonon calculation执行阶段
* neutron/Raman/IR spectrum阶段

---

# 2. 本阶段目标

必须完成以下十二类工作：

1. **Phonon DOS source and adapter audit**
2. **Approved input format / object scope**
3. **Frequency-grid normalization**
4. **Frequency and density-unit normalization**
5. **Total DOS normalization and integration validation**
6. **Projected DOS identity and aggregation**
7. **DOS artifact、summary、parse report和manifest emission**
8. **Static DOS plot and table**
9. **Runtime、registry、planner和API integration基础**
10. **Browser smoke、mobile和accessibility**
11. **Performance、determinism和security**
12. **Docs、evidence和readiness closure**

本阶段必须产生真实adapter和真实DOS plot。

如果最终只有schema映射文档、mock plot或静态fixture截图，没有真实输入→adapter→artifact→preview路径，本阶段必须判定为FAIL。

---

# 3. 第一版输入范围

优先支持以下来源之一或多个，必须根据仓库现有依赖审计后决定：

```text
canonical phase10h.phonon_dos.v1 JSON
phonopy total DOS output
phonopy projected DOS output
pymatgen phonon DOS object or approved JSON
```

推荐优先级：

1. canonical JSON
2. 已存在依赖中的pymatgen phonon DOS对象或安全JSON
3. phonopy静态DOS输出
4. 其他格式延后

如果支持phonopy，候选静态输入可能包括：

```text
total_dos.dat
projected_dos.dat
phonopy.yaml / mesh.yaml metadata
```

但不得凭文件名直接假设字段语义。

如果支持pymatgen：

* 必须审计其frequency grid
* density单位
* normalization
* site/species projection语义
* structure linkage

本阶段默认不支持：

* 动态执行phonopy
* force constants计算
* mesh生成
* arbitrary text columns
* arbitrary CSV schema guessing
* pickle
* notebook object
* remote URL
* compressed archive
* custom Python object upload
* arbitrary plugin adapter

---

# 4. 严格禁止范围

本阶段不得实现：

* combined band + DOS
* phonon eigenvector contract
* eigenvector parser
* phonon animation
* mode displacement
* thermal free energy
* entropy
* heat capacity
* Debye temperature
* thermal conductivity
* Grüneisen parameters
* quasi-harmonic approximation
* Raman activity
* IR activity
* neutron scattering intensity
* phonon calculation execution
* force constants execution
* external solver invocation
* electronic DOS
* electronic bands
* Brillouin renderer
* external API
* notebook execution
* script execution
* real LLM
* full phonon product registration

不得：

* 修改Phase 10H DOS contract语义
* 修改Phase 10H-1 phonon band语义
* 静默重采样frequency grid
* 静默平滑DOS
* 静默应用Gaussian broadening
* 静默裁剪negative-frequency区域
* 静默把negative frequency转换为positive
* 静默归一化到1
* 静默归一化到3N
* 仅修改density unit label不修改数值
* 将states、modes和arbitrary density混为一谈
* 将bin edges当作sample points
* 将projected DOS仅靠display label绑定
* 自动假设projected DOS总和等于total DOS
* 自动修复projection mismatch
* 静默推断atom order
* 静默推断structure identity
* 允许NaN或Infinity
* 允许无限grid points
* 允许无限projections
* 允许任意metadata
* 允许external URL
* 允许artifact JavaScript
* 允许HTML/script label
* 允许任意plot code
* 将DOS结果标记为officially validated

允许：

* safe static parser
* adapter
* unit conversion
* approved normalization conversion
* integration validation
* plot generation
* table generation
* API evidence
* browser smoke
* tests
* docs

---

# 5. 必读实现

开始后直接阅读当前真实代码。

## 5.1 Phase 10H DOS Contract

阅读：

* phonon DOS schema
* summary schema
* manifest schema
* projected DOS contract
* frequency conversion helpers
* DOS normalization policy
* integration helper
* typed errors
* caps
* fixtures
* deterministic serializer
* band/DOS compatibility validator

必须直接复用，不建立第二套DOS模型。

## 5.2 Phase 10H-1 Implementation

阅读：

* phonon band adapter
* source detection
* parser architecture
* parse report
* registry metadata
* PlanValidator
* artifact emission
* plot/table producers
* frontend preview
* browser evidence helpers

优先复用相同模式。

## 5.3 Existing Histogram / Density Plot Infrastructure

搜索：

```bash
rg -n "dos|density|histogram|area plot|line plot|filled area|series|x_axis|y_axis" apps/web backend packages tests
```

确认：

* line/area plot contract
* negative x-axis支持
* multiple projected series
* stacking能力
* normalization metadata
* legend caps
* tooltip/accessibility
* responsive behavior
* export能力

## 5.4 Existing Dependencies

搜索：

```bash
rg -n "phonopy|pymatgen.*dos|PhononDos|CompletePhononDos|total_dos|projected_dos" pyproject.toml uv.lock backend packages tests
```

确认：

* phonopy/pymatgen版本
* static parser能力
* object serialization方式
* site projection API
* species projection API
* licensing
* existing approved use

---

# 6. 修改前输出审计

修改代码前输出：

# Phase 10H-2 Phonon DOS Pre-Implementation Audit

## 1. Existing Source Support

* canonical JSON:
* phonopy total DOS:
* phonopy projected DOS:
* pymatgen DOS:
* other existing sources:
* dependencies:
* safe parser support:
* gaps:

## 2. Existing Plot Infrastructure

* line/area plot:
* negative frequencies:
* multiple projections:
* stacking:
* legend:
* accessibility:
* export:
* performance caps:

## 3. Existing Runtime Path

* registry:
* planner:
* adapter base:
* runtime:
* artifact validator:
* manifest:
* frontend preview:
* API:
* evidence helpers:

## 4. Scientific Risks

至少列出：

* frequency-grid semantic ambiguity
* bin edge vs sample point confusion
* frequency-unit mismatch
* density-unit mismatch
* total-modes vs unit-area normalization
* per-cell vs per-atom DOS ambiguity
* negative-frequency truncation
* imaginary-region weight loss
* broadening metadata loss
* projected DOS atom-order mismatch
* species aggregation ambiguity
* projection duplicate identity
* projected sum mismatch
* source atom count mismatch
* source structure identity mismatch
* nonmonotonic frequency grid
* integration tolerance drift
* unsafe text parsing
* large projection matrix
* candidate/reference overclaim

## 5. Selected Strategy

说明：

* supported sources:
* parser:
* canonical grid:
* frequency unit:
* density unit:
* normalization:
* integration:
* negative region:
* projections:
* broadening:
* plot:
* table:
* adapter:
* planner visibility:
* API:
* browser:
* security:

## 6. Planned Files

列出：

* source parser
* adapter
* normalizer
* integration validator
* projection mapper
* plot producer
* table producer
* registry metadata
* API tests
* frontend preview
* fixtures
* browser smoke
* evidence
* docs
* persistent

审计后直接继续实现。

---

# 7. Tool Boundary

建议工具ID：

```text
phonon.dos
```

或符合项目命名规范的：

```text
structure.phonon_dos
```

必须审计现有tool naming后选定唯一ID。

推荐本阶段状态：

```text
registered internally / planner-limited
```

如果API和browser证据完整，可以正式注册DOS-only tool，但capability必须严格限定。

不得把本工具命名为：

```text
phonon.viewer
```

并宣称bands、eigenvectors或animation已经可用。

---

# 8. Input Contract

建议：

```ts
type PhononDosAdapterInput = {
  sourceArtifactId: string;
  sourceFormat:
    | "phase10h.phonon_dos.v1"
    | "phonopy_total_dos"
    | "phonopy_projected_dos"
    | "pymatgen_phonon_dos_json";
  frequencyUnitOverride?: ApprovedFrequencyUnit;
  densityUnitOverride?: ApprovedPhononDosDensityUnit;
  normalizationOverride?: ApprovedPhononDosNormalization;
};
```

Overrides必须：

* strict allowlist
* 仅在source metadata缺失时使用
* provenance中记录
* validator检查兼容性
* 不允许任意表达式

不得允许：

* arbitrary parser
* arbitrary unit expression
* arbitrary normalization function
* arbitrary source URL
* arbitrary plotting code
* callback
* Python class path

---

# 9. Canonical JSON Path

如果输入已是：

```text
phase10h.phonon_dos.v1
```

流程：

```text
parse
→ validate
→ canonicalize
→ summary
→ parse report
→ plot/table
→ manifest
```

不得：

* 重采样
* 平滑
* broadening
* 裁剪negative frequencies
* 改变normalization
* 聚合projection
* 修改原始DOS值

只有明确请求且contract批准的unit conversion才允许转换。

---

# 10. Phonopy Total DOS Path

如果支持phonopy total DOS静态文件，必须审计真实格式。

通常可能包含：

```text
frequency density
```

但不得凭假设实现。

必须确认：

* 列数量
* header
* frequency unit
* density unit
* normalization
* negative-frequency支持
* broadening来源
* mesh metadata关联
* atom count来源
* structure identity来源

要求：

* UTF-8或ASCII明确
* bounded line reading
* bounded token count
* comment/header allowlist
* no arbitrary expression
* no locale-dependent number parsing
* no partial success

如果source缺少structure identity或atom count：

* 必须通过关联artifact提供
* 否则拒绝

不得仅凭DOS积分反推atom count并作为权威identity。

---

# 11. Phonopy Projected DOS Path

如果支持projected DOS，必须确定列语义。

可能包括：

* frequency
* per-atom projection columns
* per-direction projection columns
* species aggregated columns

第一版建议只批准：

```text
atom-projected scalar DOS
species-projected scalar DOS
```

方向分量：

```text
x / y / z projected DOS
```

建议：

```text
DEFERRED_BY_DESIGN
```

除非Phase 10H contract已明确支持。

必须建立projection column mapping：

```text
source column
→ canonical atom index/species identity
```

不得：

* 仅按列顺序猜atom order而无metadata
* 聚合方向分量而不记录
* 混合atom和species projection
* 允许列数与atom count不一致

---

# 12. Pymatgen DOS Path

如果支持pymatgen对象或JSON，必须审计：

* frequency grid unit
* density values unit
* total DOS normalization
* site projection identity
* species projection aggregation
* structure linkage
* interpolation行为
* smearing/broadening metadata
* imaginary-frequency支持

不得：

* 将library object直接序列化为artifact
* 接受pickle
* 接受任意Python import path
* 依赖object repr

必须转换为纯JSON canonical schema。

---

# 13. Source Detection

格式检测必须：

* 优先使用artifact schema/media metadata
* 或显式source format
* 使用bounded content sniffing
* 不仅依赖扩展名
* 不尝试所有parser直到某个成功

typed errors：

```text
PHONON_DOS_FORMAT_UNSUPPORTED
PHONON_DOS_FORMAT_AMBIGUOUS
```

---

# 14. Frequency Grid Contract

Canonical grid必须：

* 一维数组
* finite
* strictly increasing
* no duplicate points
* length至少2，除非contract另有规定
* bounded
* unit固定
* sample-grid语义明确
* 可包含negative frequencies

不得：

* 自动sort无序grid并掩盖输入问题
* 自动deduplicate
* 自动interpolate
* 自动uniformize
* 将bin edges当作sample centers

如果source明确使用bin centers或edges且与contract不同：

* 必须显式转换
* 或拒绝
* provenance记录

第一版建议只支持：

```text
sample grid points
```

---

# 15. Frequency Unit Normalization

输出必须使用Phase 10H canonical frequency unit。

若canonical为：

```text
terahertz
```

则支持批准转换：

* THz → THz
* cm⁻¹ → THz
* meV → THz

转换frequency grid时必须同步转换density数值。

这是关键：

如果：

```text
x_new = c × x_old
```

则density必须满足积分不变：

```text
D_new(x_new) = D_old(x_old) / c
```

必须验证：

```text
∫ D_old dx_old = ∫ D_new dx_new
```

不得只转换x-axis而不转换density。

Projected DOS也必须同步转换。

---

# 16. Density Unit Contract

Canonical density unit建议：

```text
modes_per_terahertz
```

或Phase 10H已批准的等价枚举。

必须区分：

* modes_per_terahertz
* modes_per_inverse_centimeter
* modes_per_millielectronvolt
* normalized_unit_area
* per_atom
* per_cell

第一版推荐canonical：

```text
modes_per_terahertz
normalization = total_modes
scope = structure_cell
```

不得使用含糊字段：

```text
states
density
```

而不说明单位和scope。

---

# 17. Normalization Policy

必须遵循Phase 10H contract。

推荐目标：

```text
integral(total_dos df) ≈ 3N
```

其中N为canonical atom count。

必须区分：

## total_modes

```text
integral ≈ 3N
```

## unit_area

```text
integral ≈ 1
```

## source_defined

仅在明确metadata下允许，且不能声称与total_modes等价。

本阶段建议canonical输出统一为：

```text
total_modes
```

但只有在source normalization已知且可安全转换时。

如果source normalization未知：

* 不得静默scale
* typed failure或PARTIAL result
* 推荐拒绝正式artifact生成

---

# 18. Normalization Conversion

若source为unit-area normalization且atom count已知，可转换：

```text
D_total_modes = D_unit_area × 3N
```

必须：

* provenance记录
* parse report记录scale factor
* total和projected DOS同步处理
* integration reference test
* deterministic

不得：

* 只scale total DOS不scale projections
* 通过observed integral猜source normalization
* 对unknown normalization做自动判断

---

# 19. Integration Validation

使用Phase 10H固定方法：

```text
trapezoidal integration
```

记录：

* expected integral
* observed integral
* absolute error
* relative error
* tolerance
* status

建议：

```json
{
  "normalization_check": {
    "method": "trapezoidal",
    "expected": 6.0,
    "observed": 5.98,
    "absolute_error": 0.02,
    "relative_error": 0.0033,
    "status": "within_tolerance"
  }
}
```

不得：

* 修改数据以强行通过
* 使用plot采样数据代替artifact原始数据
* 对非均匀grid使用简单矩形积分而无说明

---

# 20. Integration Mismatch Policy

必须区分：

## Small Approximate Mismatch

可输出warning：

```text
PHONON_DOS_INTEGRAL_APPROXIMATE
```

## Material Mismatch

typed failure：

```text
PHONON_DOS_INTEGRAL_MISMATCH
```

阈值必须application-owned并有fixture/reference依据。

不得用UI显示精度决定科学容差。

---

# 21. Negative-Frequency Region

必须完整保留negative-frequency grid和DOS值。

必须：

* plot在x=0左侧显示
* summary记录negative-region weight
* 不裁剪
* 不镜像
* 不取绝对值
* 不自动并入positive side

建议派生：

```text
imaginary_region_integral
```

使用同一积分方法。

可显示：

```text
A nonzero DOS contribution is present below 0 THz.
```

不得直接声称结构不稳定为最终结论。

---

# 22. Near-Zero Policy

DOS grid接近0的点必须按Phase 10H zero tolerance分类。

不得：

* 修改frequency值
* 合并near-zero bins
* 将小negative grid点变成0
* 将near-zero DOS归入positive或negative而不说明

summary可记录：

* grid points below zero threshold
* near-zero region weight

---

# 23. Total DOS Values

要求：

* 长度等于frequency grid
* finite
* nonnegative，允许极小数值容差
* bounded numeric magnitude
* deterministic

对于小负density数值：

* 不能静默abs
* 可按application-owned tolerance判断numerical noise
* 原始值保留或拒绝，必须固定策略

推荐：

```text
density < -tolerance → invalid
-tolerance <= density < 0 → warning, canonicalize only if contract allows
```

更稳妥方案：

* 不修改
* 直接拒绝任何negative density

需根据Phase 10H合同决定。

---

# 24. Projected DOS Identity

Projected DOS必须使用严格身份。

## Atom Projection

至少包含：

```json
{
  "projection_type": "atom",
  "atom_index": 0,
  "species": "Si",
  "values": []
}
```

必须验证：

* atom index合法
* species与canonical structure顺序一致
* values长度一致
* identity唯一
* order按atom index稳定

## Species Projection

至少包含：

```json
{
  "projection_type": "species",
  "species": "Si",
  "values": []
}
```

必须验证：

* species存在于structure
* identity唯一
* order按canonical species policy稳定
* aggregation来源明确

不得使用：

* display label作为唯一identity
* 任意字符串projection ID
* 数组位置隐式绑定

---

# 25. Atom / Species Projection Scope

必须明确DOS projection表示：

* atom total
* species total
* per-atom normalized
* per-species aggregated

建议字段：

```text
projection_scope
```

枚举例如：

```text
atom_total
species_total
```

不得把species total和species per-atom average混为一谈。

如果source提供species average：

* 必须显式标记
* 第一版可选择拒绝

---

# 26. Projected DOS Sum Policy

不得默认要求：

```text
sum(projected_dos) == total_dos
```

除非source contract明确保证complete decomposition。

必须记录：

```text
projection_completeness
```

建议枚举：

```text
complete
partial
unknown
```

## complete

允许验证sum≈total。

## partial

不要求相等，但显示说明。

## unknown

不得做强结论。

对于complete projection：

* 使用application-owned tolerance
* mismatch输出warning或error
* 不自动rescale

---

# 27. Directional Projections

例如：

```text
x
y
z
```

第一版建议：

```text
DEFERRED_BY_DESIGN
```

除非Phase 10H contract已有正式schema。

如果支持：

* 必须明确coordinate basis
* Cartesian axes还是local axes
* sum of components semantics
* atom identity
* units

不得用一个任意label字段塞入方向数据。

---

# 28. Broadening Metadata

本阶段不执行broadening。

只记录source metadata：

```json
{
  "broadening": {
    "method": "gaussian",
    "width": 0.1,
    "unit": "terahertz",
    "source": "producer"
  }
}
```

批准method：

```text
none
gaussian
source_defined
```

不得：

* 应用新的平滑
* 改变width
* 用前端平滑
* 接受任意function string

如果source没有信息：

```text
method = unknown
```

或相应warning，按contract执行。

---

# 29. Mesh Metadata

DOS通常来自q-point mesh。

建议provenance记录：

```json
{
  "mesh": [20, 20, 20],
  "mesh_shift": [0, 0, 0],
  "symmetry_reduction": true
}
```

如果source提供。

必须：

* bounded integers
* nonnegative
* deterministic
* inert

不得从DOS curve反推mesh。

---

# 30. Parse Report

建议新增：

```text
phase10h.phonon_dos_parse_report.v1
```

至少包含：

```json
{
  "schema_version": "phase10h.phonon_dos_parse_report.v1",
  "detected_format": "phonopy_total_dos",
  "grid_point_count": 1001,
  "projection_count": 2,
  "source_frequency_unit": "inverse_centimeter",
  "target_frequency_unit": "terahertz",
  "source_density_unit": "modes_per_inverse_centimeter",
  "target_density_unit": "modes_per_terahertz",
  "source_normalization": "total_modes",
  "target_normalization": "total_modes",
  "frequency_conversion_applied": true,
  "density_jacobian_applied": true,
  "normalization_scale_applied": false,
  "normalization_integral": 5.99,
  "expected_modes": 6,
  "negative_region_integral": 0.04,
  "projection_completeness": "complete",
  "warnings": [],
  "input_sha256": "...",
  "deterministic": true
}
```

不得包含：

* raw完整source
* local path
* environment dump
* stack trace
* library object repr

---

# 31. Adapter Output

至少输出：

```text
phonon_dos.json
phonon_dos_summary.json
phonon_dos_parse_report.json
phonon_dos_plot.json
phonon_dos_table.json
phonon_manifest.json
```

如项目已有统一命名，按真实规范调整。

每个artifact必须：

* schema明确
* media type allowlisted
* deterministic
* hash
* size
* provenance
* security metadata

不得输出：

* phonon bands
* combined plot
* eigenvectors
* renderer bundle
* HTML
* JS
* remote assets
* raw library object

---

# 32. Summary Contract

复用`phase10h.phonon_summary.v1`或建立DOS-specific summary extension。

至少包含：

* structure identity
* atom count
* frequency min/max
* frequency unit
* density unit
* normalization
* expected mode count
* observed integral
* normalization status
* negative-region integral
* total DOS available
* projected DOS available
* projection count
* projection completeness
* broadening
* source
* warnings

不得：

* 声称积分偏差意味着计算错误，除非超出正式阈值
* 声称negative DOS weight等于结构必然不稳定
* 将projected sum mismatch自动解释为错误，除非complete decomposition

---

# 33. Static DOS Plot

优先复用现有line/area plot contract。

必须支持：

* x-axis：Frequency
* y-axis：Phonon DOS
* total DOS
* optional projected DOS
* negative-frequency region
* x=0 reference line
* unit labels
* responsive layout
* degraded mode

推荐：

* total DOS为主线
* projected DOS为可切换系列
* 不默认stack所有projection，除非科学语义明确

不得：

* 裁掉negative x-axis
* 对DOS平滑
* 归一化显示但artifact未归一化
* 让projection颜色成为唯一识别方式
* 为数百projections生成完整legend

---

# 34. Plot Orientation

第一版推荐：

```text
x = frequency
y = DOS
```

因为后续Combined Band + DOS可能需要DOS旋转为：

```text
x = DOS
y = frequency
```

本阶段必须设计plot artifact使未来可转换，但不需要实现combined布局。

不得为combined view提前修改主DOS contract。

---

# 35. Negative Region Plot

必须显示：

* frequency < 0区域
* zero line
* explanatory text

建议：

```text
DOS below 0 THz corresponds to imaginary phonon modes under the contract convention.
```

不得：

* 把negative frequency隐藏
* 将其镜像
* 仅用红色表示
* 标记为parser error

---

# 36. Projection Plot Policy

当projection数量较少：

* 可显示toggle/legend

当projection数量较多：

* 默认只显示total DOS
* 提供projection selector
* species aggregation优先于列出全部atoms
* table/JSON保留全部数据

必须设置：

* max simultaneously rendered projections
* max legend entries
* max plotted numeric values

超过cap：

```text
PHONON_DOS_PLOT_DEGRADED
```

artifact仍有效。

---

# 37. Table Artifact

建议long-form表：

```text
frequency
total_dos
projection_type
projection_identity
projected_dos
classification
```

但完整long-form可能过大。

更推荐：

## Total DOS Table

```text
frequency
total_dos
frequency_classification
```

## Projection Table

```text
frequency
projection_type
atom_index/species
projected_dos
```

必须：

* deterministic row order
* unit metadata
* bounded rows
* no HTML
* no scientific-value mutation
* pagination/sample fallback

如果projection table超cap：

* 总表保留
* projection JSON保留
* UI使用筛选后按projection显示

---

# 38. Tool Metadata

建议：

```json
{
  "tool_id": "phonon.dos",
  "category": "phonon",
  "display_name": "Phonon Density of States",
  "description": "Normalize and visualize total and projected phonon density of states.",
  "input_contract": "approved phonon DOS source",
  "output_contract": "phase10h.phonon_dos.v1",
  "execution_mode": "service_backed",
  "deterministic": true,
  "network_access": false
}
```

Capabilities：

```text
phonon_dos: true
total_dos: true
projected_dos: according to implementation
imaginary_region: true
unit_conversion: true
normalization_validation: true
static_plot: true
table: true
phonon_bands: false
combined_view: false
eigenvectors: false
animation: false
thermal_properties: false
```

不得过度宣称。

---

# 39. Planner Policy

如果planner-visible，正向请求：

```text
Plot the phonon density of states.
Show the total phonon DOS.
Show atom-projected phonon DOS.
Inspect imaginary-frequency DOS weight.
```

应选择DOS tool，但前提是已有approved DOS input。

负向请求：

```text
Plot phonon bands.
Combine phonon bands and DOS.
Animate a phonon mode.
Calculate phonons from this structure.
Compute heat capacity.
```

不得由本tool伪完成。

不得从普通structure artifact直接承诺计算DOS。

推荐：

```text
planner-visible: limited
```

---

# 40. PlanValidator

必须验证：

* approved input kind
* source format
* structure identity
* atom count
* frequency/density units
* normalization
* projection scope
* caps
* no band request
* no combined request
* no animation request
* no thermal-property request
* no external URL
* no arbitrary plot code

typed codes建议：

```text
PHONON_DOS_INPUT_REQUIRED
PHONON_DOS_SOURCE_FORMAT_UNSUPPORTED
PHONON_DOS_STRUCTURE_MISMATCH
PHONON_DOS_UNIT_OVERRIDE_INVALID
PHONON_DOS_NORMALIZATION_OVERRIDE_INVALID
PHONON_DOS_PROJECTION_UNSUPPORTED
PHONON_DOS_BAND_REQUEST_UNSUPPORTED
PHONON_DOS_COMBINED_REQUEST_UNSUPPORTED
PHONON_DOS_ANIMATION_UNSUPPORTED
PHONON_DOS_THERMAL_PROPERTY_UNSUPPORTED
PHONON_CALCULATION_UNSUPPORTED
```

不得放宽PlanValidator。

---

# 41. API Evidence

必须通过正式service-backed路径。

至少覆盖：

## Valid Canonical JSON

```text
approved DOS artifact
→ PlanValidator
→ runtime
→ adapter
→ DOS/summary/report/plot/table/manifest
→ artifact retrieval
```

## Valid Static Source

如果实现phonopy或pymatgen适配：

* parse
* normalize
* unit conversion
* density Jacobian
* stable hash

## Total DOS

* normalization integral正确
* expected mode count正确

## Imaginary Region

* negative frequencies保留
* negative-region integral正确
* plot显示正确

## Projected DOS

* identity正确
* ordering正确
* completeness policy正确

## Invalid Input

* typed failure
* no partial artifacts

## Over-Cap

* allocation前拒绝
* no plot build
* no crash

---

# 42. Frontend Preview

至少显示：

* tool title
* structure identity摘要
* atom count
* frequency range
* frequency unit
* density unit
* normalization
* expected/observed integral
* negative-region weight
* total DOS plot
* projection selector，若支持
* table/JSON tabs
* source
* broadening metadata
* warnings
* artifact downloads

不得显示：

* phonon bands
* combined plot
* eigenvector controls
* animation controls
* thermal properties
* stability最终结论

---

# 43. Accessibility

必须提供：

* plot title
* text summary
* axis units
* normalization说明
* negative-frequency语义说明
* projection selector accessible name
* total/projected series文本标识
* table keyboard navigation
* warnings不只靠颜色
* focus order
* 200% zoom
* mobile可读

建议文本摘要：

```text
Phonon density of states from -1.2 to 15.4 THz. The integrated total DOS is 5.98 modes compared with an expected 6 modes. A small contribution is present below 0 THz.
```

不得只提供canvas而无文本或table fallback。

---

# 44. Mobile

至少支持：

* responsive plot
* total DOS默认显示
* projection selector
* summary
* warning
* table/JSON fallback
* artifact download

要求：

* no scroll trap
* legend不遮挡plot
* projection selector touch target合格
* negative region仍可见
* tooltip不是唯一信息通道

---

# 45. Plot Performance

必须设置：

* max grid points
* max projections
* max simultaneously rendered projections
* max plotted numeric values
* max legend entries
* max table rows

超过interactive cap：

* total DOS仍可显示，若安全
* projections进入selector/degraded
* table分页或sample
* artifact完整保留

超过hard contract cap：

* adapter拒绝

不得：

* 为每个grid point创建DOM节点
* 同时渲染数百projection
* 创建巨大SVG path集合
* 在前端重采样来掩盖性能问题，除非另有明确display-only downsampling contract；本阶段建议不做

---

# 46. Determinism

必须验证：

* source mapping稳定
* frequency grid order稳定
* projection order稳定
* unit conversion稳定
* density Jacobian稳定
* normalization scale稳定
* integration result稳定
* warning order稳定
* plot series order稳定
* table row order稳定
* manifest order稳定
* hashes稳定

跨浏览器PNG hash不要求一致。

---

# 47. Security

必须验证：

* no unsafe YAML/object loader
* no pickle
* no eval
* no literal eval
* no shell
* no notebook execution
* no script execution
* no remote source
* no external URL
* no HTML label execution
* no SVG script
* no artifact JavaScript
* no arbitrary plot code
* no arbitrary unit expression
* no arbitrary normalization expression
* no callback
* no oversized text expansion
* no metadata recursion abuse
* no private path
* no secrets
* no telemetry upload

必须输出：

```text
NO_EXTERNAL_NETWORK_REQUESTS
NO_SECRET_PATTERN_HITS
```

---

# 48. Fixtures

新增small、deterministic fixtures。

至少：

## 48.1 Valid Total DOS

* 2 atoms
* expected integral≈6
* positive frequencies

## 48.2 Imaginary-Region DOS

* negative-frequency grid
* nonzeronegative-region weight

## 48.3 Unit-Area DOS

* source normalization=unit_area
* convert tototal_modes
* validate scale

## 48.4 cm⁻¹ DOS

* frequency and density conversion
* integral invariance

## 48.5 meV DOS

* frequency and density conversion
* integral invariance

## 48.6 Atom-Projected DOS

* canonical atom identity
* complete decomposition

## 48.7 Species-Projected DOS

* species total projections
* deterministic ordering

## 48.8 Partial Projection

* projection completeness=partial
* no forced sum validation

## 48.9 Projection Sum Mismatch

* complete projection
* warning/error policy

## 48.10 Broadening Metadata

* Gaussian width recorded
* no new broadening applied

## 48.11 Invalid Grid

* duplicate/nonmonotonic

## 48.12 Invalid Density

* nonfinite
* negative density beyond tolerance

## 48.13 Over-Cap Synthetic

不得提交大型真实DOS文件。

---

# 49. Unit Tests

至少覆盖：

## Source Detection

* canonical JSON
* phonopy total DOS，若支持
* phonopy projected DOS，若支持
* pymatgen，若支持
* unsupported
* ambiguous

## Grid

* strictly increasing
* duplicate
* nonmonotonic
* negative frequencies
* nonfinite
* too short
* over-cap

## Unit Conversion

* THz
* cm⁻¹
* meV
* density Jacobian
* integral invariance
* unsupported unit

## Normalization

* total_modes
* unit_area conversion
* unknown normalization
* expected 3N
* approximate mismatch
* material mismatch

## Total DOS

* shape
* finite
* negative density policy
* magnitude cap

## Projections

* atom identity
* species identity
* duplicate projection
* invalid atom index
* species mismatch
* complete sum
* partial sum
* deterministic ordering

## Broadening

* none
* Gaussian metadata
* invalid width
* unsupported method
* no transformation

## Plot

* total DOS
* negative region
* zero line
* projections
* selector/degraded
* units
* legend caps

## Table

* row order
* projection filtering
* units
* classification
* row cap

## Artifacts

* schema
* summary
* report
* plot
* table
* manifest
* hashes
* no executable assets

## Security

* unsafe tags
* HTML labels
* external URL
* callback-like metadata
* arbitrary normalization text
* private path

---

# 50. API Tests

覆盖：

* canonical valid
* supported source valid
* total DOS normalization
* imaginary region
* unit conversion
* projected DOS
* projection mismatch
* invalid grid
* structure mismatch
* over-cap
* deterministic replay
* artifact retrieval
* no partial artifacts

---

# 51. Browser Smoke Evidence

新增：

```text
docs/phase10h/evidence/phase10h2_phonon_dos/
```

## Chromium

覆盖：

* total DOS
* imaginary-region DOS
* unit conversion result
* atom projection selector
* species projection
* normalization summary
* table
* JSON fallback
* degraded plot
* invalid state
* accessibility
* no external network

## Firefox

smoke：

* total DOS
* negative frequencies
* projection selector
* table fallback
* console/network

## WebKit

smoke：

* responsive DOS
* projection selection
* warning
* JSON/table fallback
* console/network

## Mobile

smoke：

* total DOS
* summary
* projection selector
* warning
* table fallback
* no scroll trap

---

# 52. Browser Evidence Assertions

记录：

* browser version
* viewport
* tool ID
* source format
* schema
* atom count
* frequency grid size
* projection count
* frequency unit
* density unit
* normalization
* expected integral
* observed integral
* negative-region integral
* projection completeness
* plot mode
* rendered series count
* table rows
* warnings
* console errors
* network requests

必须验证：

* frequency单位正确
* density Jacobian正确反映在artifact结果
* negative频率显示
* normalization摘要正确
* projection identity正确
* no silent resampling
* no external network
* no artifact JS
* no capability overclaim

---

# 53. Evidence Files

至少包含：

```text
README.md
format_scope.json
source_mapping_policy.json
frequency_grid_policy.json
frequency_density_conversion.json
normalization_policy.json
integration_validation.json
negative_frequency_policy.json
projection_identity_policy.json
projection_completeness_policy.json
broadening_policy.json
parse_report_schema.json
total_dos_result.json
imaginary_dos_result.json
unit_area_conversion_result.json
inverse_centimeter_conversion_result.json
mev_conversion_result.json
atom_projected_result.json
species_projected_result.json
partial_projection_result.json
projection_mismatch_result.json
plot_contract_result.json
table_contract_result.json
api_valid_canonical.json
api_valid_source.json
api_imaginary.json
api_projected.json
api_invalid.json
api_over_cap.json
deterministic_replay.json
browser_chromium.json
browser_firefox.json
browser_webkit.json
browser_mobile.json
accessibility_audit.json
performance_metrics.json
security_audit.json
network_audit.json
artifact_hashes.json
```

截图建议：

```text
01_total_phonon_dos.png
02_imaginary_region_dos.png
03_atom_projected_dos.png
04_species_projected_dos.png
05_normalization_summary.png
06_phonon_dos_table.png
07_degraded_dos_plot.png
08_invalid_dos_input.png
09_mobile_phonon_dos.png
```

不得保存：

* 大型source文件
* unsafe payload
* private path
* token
* secret
* raw library dump
* browser cache
* full traces

---

# 54. Dependency Policy

优先不新增依赖。

如果已有：

* phonopy
* pymatgen
* NumPy
* approved chart library

则复用。

如果没有phonopy/pymatgen：

* canonical JSON必须完整
* 可实现有限静态text parser
* 不要引入完整计算栈仅为解析DOS

如新增解析依赖：

* security audit
* safe usage
* lockfile更新
* license记录

检查：

```bash
uv lock --check
npm --prefix apps/web ls --depth=0
npm --prefix apps/web run build
```

记录：

* dependency tree
* lockfile
* frontend bundle
* no unexpected additions

---

# 55. Documentation

新增或更新：

```text
docs/phase10h/phase10h2_phonon_dos.md
docs/phase10h/phase10h2_phonon_dos_source_scope.md
docs/phase10h/phase10h2_frequency_density_conversion.md
docs/phase10h/phase10h2_dos_normalization.md
docs/phase10h/phase10h2_dos_integration_validation.md
docs/phase10h/phase10h2_projected_dos.md
docs/phase10h/phase10h2_phonon_dos_plot_contract.md
docs/phase10h/phase10h2_phonon_dos_table.md
docs/phase10h/phase10h2_phonon_dos_api_evidence.md
docs/phase10h/phase10h2_phonon_dos_accessibility.md
docs/phase10h/phase10h2_phonon_dos_security.md
docs/phase10h/phase10h2_phonon_dos_readiness_matrix.md
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

* supported sources
* deferred sources
* grid semantics
* frequency conversion
* density Jacobian
* normalization
* integration
* negative-frequency region
* projected identity
* projection completeness
* broadening metadata
* plot/table contracts
* planner visibility
* API path
* combined view deferred
* eigenvectors deferred
* animation deferred

---

# 56. Readiness Matrix

最终分别判断：

* source scope
* canonical JSON adapter
* phonopy total DOS adapter
* phonopy projected DOS adapter
* pymatgen adapter
* safe parsing
* frequency grid
* frequency conversion
* density conversion
* Jacobian
* integral invariance
* total-modes normalization
* unit-area conversion
* normalization validation
* negative-frequency DOS
* imaginary-region integral
* total DOS
* atom-projected DOS
* species-projected DOS
* projection completeness
* projection sum validation
* broadening metadata
* structure identity
* DOS artifact
* summary
* parse report
* manifest
* static plot
* table
* degraded plot
* API evidence
* frontend preview
* accessibility
* mobile
* browser smoke
* security
* formal DOS tool registration
* combined view
* eigenvectors
* animation

推荐期望：

```text
source scope: READY
canonical JSON adapter: READY
phonopy total DOS adapter: READY or DEFERRED_BY_DESIGN
phonopy projected DOS adapter: READY or DEFERRED_BY_DESIGN
pymatgen adapter: READY or DEFERRED_BY_DESIGN
safe parsing: READY
frequency grid: READY
frequency conversion: READY
density Jacobian: READY
integral invariance: READY
normalization: READY
integration validation: READY
negative-frequency DOS: READY
total DOS: READY
atom-projected DOS: READY or PARTIAL_READY
species-projected DOS: READY or PARTIAL_READY
projection completeness: READY
broadening metadata: READY
structure identity: READY
DOS artifact: READY
summary: READY
parse report: READY
manifest: READY
static plot: READY
table: READY
API evidence: READY
frontend preview: READY
accessibility: READY
mobile: READY
browser smoke: READY
security: READY

formal phonon DOS tool registration: READY or PARTIAL_READY
combined band + DOS: NOT_READY
phonon eigenvector contract: NOT_READY
phonon animation: NOT_READY
```

---

# 57. Checks

至少运行：

```bash
git diff --check
uv lock --check

uv run python -m pytest -q

npm --prefix apps/web test
npm --prefix apps/web run typecheck
npm --prefix apps/web run build
```

并运行：

* phonon DOS source parser tests
* frequency-grid tests
* frequency/density conversion tests
* Jacobian tests
* normalization tests
* integration tests
* negative-region tests
* total DOS tests
* projected DOS tests
* projection completeness tests
* broadening metadata tests
* plot tests
* table tests
* adapter tests
* API integration
* frontend preview tests
* accessibility tests
* Chromium smoke
* Firefox smoke
* WebKit smoke
* mobile smoke
* security scan
* network audit
* Phase 10 Closure Regression Pack
* Phase 10G regression
* Phase 10H contract regression
* Phase 10H-1 phonon band regression
* service-backed integration
* no-skipped assertion

必须如实记录：

* passed
* failed
* skipped
* unavailable

不得把skipped写成passed。

---

# 58. Commit / CI

完成adapter、plot、tests、evidence和docs后：

```bash
git status --short
git diff --stat
git add <only Phase 10H-2 related files>
git commit -m "Add phonon DOS adapter and visualization"
git push origin master
```

等待current HEAD CI。

必须确认：

* backend unit success
* frontend tests success
* frontend typecheck success
* frontend build success
* phonon DOS tests success
* API integration success
* browser smoke success
* Phase 10 Closure success
* Phase 10G regression success
* Phase 10H contract success
* Phase 10H-1 regression success
* service-backed integration success
* no-skipped assertion success
* origin/master matches HEAD
* git status clean

不得伪造CI。

---

# 59. 最终报告格式

完成后输出：

# Phase 10H-2 Phonon DOS Result

## 1. Conclusion

PASS / PARTIAL_PASS / FAIL

## 2. Baseline

* Phase 10H-1 assumed complete:
* branch:
* initial status:
* final HEAD:
* final status:

## 3. Source Scope

* canonical JSON:
* phonopy total DOS:
* phonopy projected DOS:
* pymatgen:
* deferred:
* detection:
* safe parsing:

## 4. Adapter Architecture

* source parser:
* normalizer:
* unit converter:
* integration validator:
* projection mapper:
* validator:
* serializer:
* summary:
* parse report:
* manifest:
* runtime:

## 5. Frequency Grid

* semantic:
* ordering:
* negative region:
* duplicates:
* nonuniform grid:
* source conversion:
* caps:

## 6. Units and Jacobian

* source frequency unit:
* canonical frequency unit:
* source density unit:
* canonical density unit:
* THz:
* cm⁻¹:
* meV:
* density Jacobian:
* integral invariance:

## 7. Normalization

* source normalization:
* target normalization:
* total modes:
* unit-area conversion:
* scale factor:
* expected integral:
* observed integral:
* tolerance:
* mismatch policy:

## 8. Negative / Near-Zero Region

* negative frequencies:
* imaginary-region integral:
* zero tolerance:
* near-zero:
* clipping:
* display:

## 9. Total DOS

* shape:
* finite:
* nonnegative policy:
* density unit:
* normalization:
* integral:
* source:

## 10. Projected DOS

* atom projections:
* species projections:
* ordering:
* identity:
* scope:
* completeness:
* sum validation:
* mismatch:
* directional projections:

## 11. Broadening / Mesh

* broadening method:
* width:
* unit:
* applied by adapter:
* mesh metadata:
* source:

## 12. Artifacts

* DOS:
* summary:
* parse report:
* plot:
* table:
* manifest:
* hashes:
* provenance:
* security:

## 13. Plot

* x-axis:
* y-axis:
* units:
* zero line:
* negative region:
* total series:
* projected series:
* selector:
* degraded mode:
* legend cap:

## 14. Table

* total table:
* projection table:
* columns:
* row order:
* units:
* classification:
* row cap:
* fallback:

## 15. Tool / Planner

* tool ID:
* registry:
* planner visibility:
* valid routing:
* band rejection:
* combined rejection:
* animation rejection:
* calculation rejection:
* PlanValidator:

## 16. API Evidence

* canonical valid:
* source valid:
* normalization:
* imaginary region:
* projected:
* invalid:
* over-cap:
* artifact retrieval:
* runtime path:

## 17. Frontend / Accessibility

* product preview:
* summary:
* plot:
* projection selector:
* table:
* JSON fallback:
* screen reader summary:
* keyboard:
* 200% zoom:
* mobile:

## 18. Browser Smoke

* Chromium:
* Firefox:
* WebKit:
* mobile:
* negative region:
* projections:
* normalization:
* console:
* network:

## 19. Performance

* grid points:
* projections:
* plotted values:
* simultaneous series:
* table rows:
* degraded threshold:
* memory proxy:
* render behavior:

## 20. Determinism

* frequency order:
* projection order:
* conversion:
* normalization scale:
* integral:
* warning order:
* plot series:
* table rows:
* manifest:
* hashes:

## 21. Security

* parser:
* unsafe object construction:
* eval/pickle:
* external references:
* labels:
* plot code:
* unit/normalization expressions:
* metadata:
* caps:
* private paths:
* secrets:
* network:
* markers:

## 22. Evidence

* directory:
* source mapping:
* grid policy:
* unit conversion:
* Jacobian:
* normalization:
* integration:
* negative region:
* projections:
* plot:
* table:
* API:
* browser:
* accessibility:
* security:
* screenshots:
* hashes:

## 23. Tests

* source parser:
* grid:
* frequency units:
* density units:
* Jacobian:
* normalization:
* integration:
* negative region:
* total DOS:
* projections:
* broadening:
* plot:
* table:
* adapter:
* API:
* frontend:
* accessibility:
* Chromium:
* Firefox:
* WebKit:
* mobile:
* backend full:
* frontend full:
* typecheck:
* build:
* Phase 10 closure:
* Phase 10G:
* Phase 10H:
* Phase 10H-1:
* service-backed:
* no-skipped:
* lock:
* diff:

## 24. Files

* parser:
* adapter:
* normalizer:
* converters:
* integration validator:
* projection mapper:
* plot producer:
* table producer:
* registry:
* planner:
* API:
* frontend:
* fixtures:
* tests:
* browser runners:
* evidence:
* docs:
* persistent:
* dependencies/lockfile:

## 25. Deferred

明确列出：

* unsupported DOS source formats
* directional projected DOS，若未实现
* combined phonon band + DOS
* eigenvector payload
* eigenvector atom mapping
* complex phase
* phonon animation
* LO-TO directional rendering
* Raman/IR activity
* thermodynamic properties
* official benchmark validation
* full phonon product registration，若未完成

## 26. Readiness

* source adapter:
* grid normalization:
* frequency conversion:
* density conversion:
* normalization:
* integration:
* negative region:
* total DOS:
* projected DOS:
* artifact:
* plot:
* table:
* API:
* frontend:
* browser:
* accessibility:
* security:
* phonon DOS:
* bands:
* combined:
* eigenvectors:
* animation:
* formal product:

## 27. Commit / CI

* commit:
* HEAD:
* CI run:
* backend:
* frontend:
* typecheck:
* build:
* phonon DOS:
* API:
* browser:
* Phase 10 closure:
* Phase 10G:
* Phase 10H:
* Phase 10H-1:
* service-backed:
* no-skipped:
* origin:
* status:

## 28. Whether allowed to enter next phase

允许 / 不允许

下一阶段：

```text
Phase 10H-3：Combined Band + DOS
```

下一阶段只实现兼容phonon band和phonon DOS artifact的组合验证、共享frequency axis、联合静态布局、API/frontend/browser evidence，不实现eigenvector或animation。

---

# 60. PASS 判定

PASS必须满足：

* 有真实phonon DOS adapter
* 有至少一种正式支持来源
* canonical JSON路径完整
* source parsing安全
* frequency grid语义明确
* grid严格递增
* frequency单位转换正确
* density Jacobian正确
* 转换前后积分保持
* normalization明确
* total-modes积分检查正确
* unit-area conversion正确
* unknown normalization不被猜测
* negative-frequency区域完整保留
* imaginary-region积分正确
* total DOS artifact生成
* projected DOS identity正确
* atom/species projections不混淆
* projection completeness明确
* complete projection sum验证正确
* mismatch不被静默修复
* broadening只记录、不重新应用
* summary生成
* parse report生成
* manifest生成
* static DOS plot真实工作
* negative region真实显示
* projection selector或degraded策略真实工作
* table真实工作
* plot/table caps生效
* API正式路径闭合
* frontend preview真实工作
* accessibility不回退
* Chromium真实smoke通过
* Firefox/WebKit/mobile smoke完成或如实记录
* deterministic replay稳定
* no unsafe parser
* no artifact JS
* no external network
* no secret hits
* Phase 10 Closure、Phase 10G、Phase 10H和Phase 10H-1不回退
* tests通过
* CI通过
* git clean

PARTIAL_PASS仅允许：

* phonopy或pymatgen某来源明确DEFERRED_BY_DESIGN，但canonical JSON和至少一个正式来源完整
* atom-projected或species-projected其中一类暂未实现，但total DOS完整且另一类projection受控
* formal planner visibility保持limited
* browser某非主要环境明确unavailable
* directional projections明确deferred
* npm audit因既有registry问题不可用

FAIL包括：

* 只有mock DOS plot
* adapter绕过Phase 10H validator
* frequency grid被静默排序或重采样
* frequency转换后density未应用Jacobian
* normalization不明确
* 通过observed积分猜normalization
* negative-frequency区域被裁剪
* projected DOS只靠label绑定
* complete projection mismatch被静默rescale
* broadening被前端自动应用
* structure identity缺失
* 无API evidence
* 无browser evidence
* 提前实现combined/eigenvector/animation导致范围膨胀
* Phase 10H-1回退
* CI失败却声明PASS

---END---

---TASK---
 状态：待处理
 # Phase 10H-3：Combined Band + DOS

进入 Phase 10H-3：Combined Band + DOS。

可以默认：

* Phase 10H：Phonon Contract 已完成并通过
* Phase 10H-1：Phonon Bands 已完成并通过
* Phase 10H-2：Phonon DOS 已完成并通过
* `phase10h.phonon_band.v1` 已稳定
* `phase10h.phonon_dos.v1` 已稳定
* `phase10h.phonon_summary.v1` 已稳定
* `phase10h.phonon_manifest.v1` 已稳定
* `phase10h.qpoint_path.v1` 已稳定
* phonon band adapter、normalizer、plot、table、summary、parse report、manifest、API路径和browser smoke均已完成
* phonon DOS adapter、frequency/density unit conversion、Jacobian、normalization validation、projected DOS、plot、table、summary、parse report、manifest、API路径和browser smoke均已完成
* band / DOS compatibility policy已在Phase 10H contract中定义
* reciprocal lattice convention、`2π` policy、q-point coordinate system、frequency canonical unit、imaginary-frequency encoding、zero tolerance、atom ordering、structure identity、NAC metadata和source lineage policy均已固定
* phonon band standalone view使用：

  * x-axis = q-path distance
  * y-axis = frequency
* phonon DOS standalone view使用：

  * x-axis = frequency
  * y-axis = DOS
* Combined Band + DOS必须改为共享frequency纵轴：

  * band x-axis = q-path distance
  * DOS x-axis = density
  * shared y-axis = frequency
* Phase 10G trajectory产品保持稳定
* Phase 10 Closure Regression Pack保持通过
* static viewer、trajectory viewer、phonon band、phonon DOS不得因本阶段发生回退
* 当前branch、HEAD、working tree和Phase 10H-2 CI可视为正确且clean

本阶段不需要重复Phase 10H-2 baseline检查。

本阶段的主要任务是：

> 建立phonon band与phonon DOS的严格兼容性验证、组合artifact、共享frequency axis和正式联合产品路径，使同一结构、同一原子顺序、兼容计算来源、兼容NAC政策和兼容频率语义的band与DOS能够形成科学上可信、可访问、可导出、可通过API和浏览器验证的Combined Band + DOS视图。

本阶段必须避免将“两个独立图并排显示”误认为完成。

真正的Combined Band + DOS必须具备：

* backend权威compatibility validator
* structure identity验证
* atom ordering验证
* source lineage验证
* force constants / calculation identity验证，若metadata可用
* frequency unit统一
* DOS density Jacobian转换
* normalization有效性验证
* imaginary-mode语义统一
* NAC兼容性验证
* shared frequency domain
* zero line严格对齐
* negative-frequency区域一致
* combined artifact
* compatibility report
* combined summary
* combined plot contract
* registry / planner / validator / runtime / API / frontend完整路径
* browser evidence
* mobile / accessibility
* security和CI收口

本阶段不实现phonon eigenvector，不实现phonon animation，不实现thermal properties。

---

# 1. 本阶段定位

Phase 10H-3是phonon静态频域能力的组合与产品化阶段。

它位于：

```text
Phase 10H      Phonon Contract
Phase 10H-1    Phonon Bands
Phase 10H-2    Phonon DOS
Phase 10H-3    Combined Band + DOS
Phase 10H-4    Phonon Eigenvector Contract
Phase 10H-5    Phonon Animation
```

本阶段负责把两个已经独立稳定的科学产品：

```text
phonon band
phonon DOS
```

通过严格兼容性验证组合为：

```text
phonon combined band + DOS
```

该组合产品必须回答：

* 两个artifact是否来自同一个canonical structure
* atom count是否一致
* species ordering是否逐index一致
* primitive cell / supercell关系是否兼容
* source calculation lineage是否一致
* force constants来源是否一致
* frequency units是否一致或可安全转换
* DOS conversion是否包含正确Jacobian
* imaginary-frequency encoding是否一致
* zero tolerance是否兼容
* NAC设置是否一致
* Gamma方向策略是否兼容
* DOS normalization是否有效
* broadening metadata是否被保留
* 两个frequency ranges如何形成共同显示domain
* band path discontinuity是否保留
* projected DOS如何受控显示
* desktop、mobile和accessibility下如何保持语义正确

本阶段不是：

* 简单CSS并排布局
* 两张PNG拼接
* frontend临时组合
* phonon计算阶段
* eigenvector阶段
* animation阶段
* thermal-property阶段
* Brillouin zone阶段
* electronic band + DOS阶段

---

# 2. 本阶段完成目标

必须完成以下十四类工作：

1. **Band / DOS现状与兼容基础审计**
2. **Combined schema family**
3. **Compatibility validator正式实现**
4. **Structure、atom order和source lineage一致性验证**
5. **Frequency unit和DOS Jacobian转换**
6. **Shared frequency domain与axis contract**
7. **Combined plot producer**
8. **Projected DOS selection policy**
9. **Combined summary、compatibility report、table和manifest**
10. **Tool Registry、Planner、PlanValidator和runtime integration**
11. **正式API和frontend product path**
12. **Accessibility、responsive和mobile**
13. **Performance、determinism和security**
14. **Docs、evidence、commit和CI收口**

本阶段必须产生真实代码，包括：

* schema/model
* validator
* composer
* plot data producer
* frontend combined view
* tests
* browser evidence
* registry / planner wiring
* API evidence

如果最终只有文档、mock、静态截图或两个已有preview的视觉并排，本阶段必须判定为FAIL。

---

# 3. 严格禁止范围

本阶段不得实现：

* phonon eigenvector payload
* eigenvector source parser
* complex eigenvector phase处理
* phonon mode identity正式实现
* phonon animation
* atomic displacement animation
* animation amplitude controls
* phase controls
* LO-TO mode animation
* thermal free energy
* entropy
* heat capacity
* Debye temperature
* thermal conductivity
* Grüneisen parameter
* quasi-harmonic approximation
* Raman activity
* IR activity
* neutron scattering intensity
* phonon计算执行
* force constants计算
* phonopy命令执行
* DFPT执行
* Brillouin zone renderer
* electronic band structure
* electronic DOS
* external solver invocation
* notebook execution
* script execution
* real LLM
* arbitrary plot scripting
* remote artifact loading

不得：

* 修改`phase10h.phonon_band.v1`科学语义
* 修改`phase10h.phonon_dos.v1`科学语义
* 修改Phase 10H-1或10H-2已有artifact内容
* 将不兼容band和DOS机械组合
* 仅按文件名判断来源一致
* 仅按formula判断structure一致
* 仅按atom count判断structure一致
* 仅按species集合判断atom ordering一致
* 静默忽略atom order mismatch
* 静默忽略primitive/supercell mismatch
* 静默忽略force constants mismatch
* 静默忽略NAC mismatch
* 静默忽略Gamma方向差异
* 静默忽略imaginary encoding mismatch
* 静默忽略zero tolerance差异
* 静默重归一化DOS
* 静默重采样DOS
* 静默插值band
* 静默平滑DOS
* 静默裁剪negative-frequency区域
* 静默取negative frequency绝对值
* 静默使用frequency range交集而丢弃数据
* 静默在DOS范围外补零
* 静默连接band discontinuous segments
* 仅修改axis label而不转换数值
* frequency转换后遗漏DOS density Jacobian
* broadening width单位转换遗漏
* frontend独立实现科学兼容判断
* frontend修复backend invalid artifact
* artifact控制layout代码
* artifact控制callback
* artifact控制HTML、SVG script、URL或JS
* artifact控制性能cap
* artifact控制可执行格式化表达式
* 允许无限projected DOS series
* 允许巨大legend
* 允许巨大DOM/SVG节点数量
* 声称eigenvector或animation READY
* 声称combined结果是官方科学验证结果

允许：

* compatibility validator
* approved unit conversion
* density Jacobian
* display-owned derived representation
* shared-axis plot
* combined summary
* projection selector
* responsive layout
* API/browser evidence
* docs和tests

---

# 4. 必读实现

开始后直接阅读当前真实代码。

## 4.1 Phase 10H Contract

必须阅读：

* band schema
* DOS schema
* summary schema
* manifest schema
* structure identity policy
* atom ordering policy
* frequency unit converters
* imaginary encoding policy
* zero tolerance policy
* NAC metadata contract
* source lineage contract
* DOS normalization policy
* band / DOS compatibility contract
* typed errors
* caps
* deterministic serializer

确认：

* compatibility目前是否只是文档
* 是否已有部分validator
* 是否已有`compatible / convertible / incompatible`状态
* 是否已有source calculation identity
* 是否已有force constants identity
* 是否已有primitive / supercell matrices
* 是否已有统一warning ordering

## 4.2 Phase 10H-1 Phonon Bands

阅读：

* tool ID
* adapter
* source parser
* normalizer
* band artifact
* band summary
* parse report
* plot contract
* table
* manifest
* registry metadata
* planner policy
* PlanValidator
* API path
* frontend preview
* browser tests
* accessibility实现

确认：

* band frequency unit
* q-path distance
* branch order
* discontinuity表示
* high-symmetry labels
* negative frequencies
* zero line
* NAC metadata
* source identity
* structure identity

## 4.3 Phase 10H-2 Phonon DOS

阅读：

* tool ID
* adapter
* source parser
* frequency conversion
* density conversion
* Jacobian
* normalization
* projected DOS
* broadening metadata
* DOS artifact
* DOS summary
* parse report
* plot
* table
* manifest
* registry
* planner
* API
* frontend preview
* browser tests

确认：

* standalone DOS orientation
* density unit
* normalization
* expected / observed integral
* negative-region integral
* projection completeness
* atom/species identity
* projection ordering
* broadening width单位

## 4.4 Plot and Layout Infrastructure

搜索：

```bash
rg -n "shared.*axis|linked.*axis|combined.*plot|band.*dos|dos.*band|secondary.*panel|grid.*layout|axis.*domain|responsive.*chart" apps/web backend packages tests
```

确认：

* chart library是否支持共享domain
* 是否支持左右panel
* 是否支持横向DOS
* 是否支持panel-specific x-axis
* 是否支持共同y-axis
* 是否支持null break / segment break
* 是否支持mobile stacked / tabbed
* 是否支持export
* 是否支持accessibility summary
* 是否会为每个point创建DOM node

## 4.5 Registry / Planner / API

搜索：

```bash
rg -n "phonon\\.bands|phonon\\.dos|ToolRegistry|PlanValidator|service_backed|artifact references|planner routing" backend packages apps tests
```

确认：

* band tool和DOS tool的正式状态
* combined tool命名冲突
* multi-input tool如何注册
* PlanValidator如何验证两个artifact
* runtime如何加载多artifact输入
* API如何返回combined artifact引用
* frontend如何进入产品surface

---

# 5. 修改前输出审计

修改任何代码前，必须输出：

# Phase 10H-3 Combined Band + DOS Pre-Implementation Audit

## 1. Baseline Products

### Phonon Band

* tool ID:
* registry status:
* planner visibility:
* artifact schema:
* structure identity:
* atom ordering:
* frequency unit:
* imaginary encoding:
* zero tolerance:
* NAC:
* source lineage:
* path segments:
* plot:
* API:
* browser:

### Phonon DOS

* tool ID:
* registry status:
* planner visibility:
* artifact schema:
* structure identity:
* atom ordering:
* frequency unit:
* density unit:
* normalization:
* zero tolerance:
* NAC:
* source lineage:
* projections:
* broadening:
* plot:
* API:
* browser:

## 2. Existing Compatibility Infrastructure

* schema:
* validator:
* compatibility states:
* structure check:
* atom-order check:
* source-lineage check:
* unit conversion:
* density Jacobian:
* NAC check:
* normalization check:
* warning policy:
* missing pieces:

## 3. Plot Infrastructure

* shared y-axis:
* dual panel:
* band-left / DOS-right:
* horizontal DOS:
* discontinuity:
* zero line:
* negative region:
* responsive:
* mobile:
* accessibility:
* export:
* caps:
* known limitations:

## 4. Runtime / Product Path

* registry:
* planner:
* multi-input validation:
* runtime:
* artifact loader:
* API:
* frontend:
* browser runner:
* CI job:

## 5. Scientific Risks

至少列出：

* same formula but different crystal structure
* same structure but different canonical atom order
* primitive cell vs conventional cell mismatch
* primitive vs supercell mismatch
* different force constants
* different source calculations
* different producer versions
* frequency unit mismatch
* DOS Jacobian omission
* imaginary encoding mismatch
* zero tolerance mismatch
* NAC enabled / disabled mismatch
* Gamma direction mismatch
* DOS normalization invalid
* projection identity mismatch
* incomplete projection misrepresented as complete
* frequency range difference
* negative-frequency truncation
* band discontinuity loss
* shared-axis visual drift
* frontend-only validation
* plot performance blowup
* candidate evidence overclaim

## 6. Selected Strategy

说明：

* combined tool ID:
* combined schema:
* compatibility result states:
* hard incompatibility rules:
* convertible rules:
* warning rules:
* source lineage policy:
* unit conversion:
* density Jacobian:
* shared domain:
* DOS orientation:
* projection selector:
* desktop layout:
* mobile layout:
* API:
* browser:
* registration:
* security:

## 7. Planned Files

必须列出预计新增或修改：

* combined schema/model
* compatibility report schema
* combined summary schema
* combined manifest schema
* compatibility validator
* composer
* unit conversion integration
* plot producer
* table producer
* registry
* planner
* PlanValidator
* runtime/API
* frontend combined view
* fixtures
* unit/integration tests
* browser tests
* accessibility tests
* evidence
* docs
* persistent
* CI

审计后直接继续执行，不等待确认。

---

# 6. Tool ID和产品边界

推荐正式工具ID：

```text
phonon.band_dos
```

如果仓库命名规范要求更完整，也可采用：

```text
phonon.combined_band_dos
```

必须选择唯一一个。

推荐：

```text
phonon.band_dos
```

理由：

* 与`phonon.bands`一致
* 与`phonon.dos`一致
* 名称简洁
* 不过度宣称
* 明确表示静态band + DOS组合

不得使用：

```text
phonon.viewer
phonon.full_analysis
phonon.dynamic
```

因为本阶段不包含：

* eigenvectors
* animation
* thermal properties
* phonon calculation

工具边界必须固定：

```text
phonon.bands
→ band-only

phonon.dos
→ DOS-only

phonon.band_dos
→ compatible band + DOS combined static view
```

---

# 7. Combined Schema Family

建议新增：

```text
phase10h.phonon_band_dos.v1
phase10h.phonon_band_dos_summary.v1
phase10h.phonon_band_dos_compatibility_report.v1
phase10h.phonon_band_dos_plot.v1
phase10h.phonon_band_dos_manifest.v1
```

如项目统一manifest要求继续复用`phase10h.phonon_manifest.v1`，可以扩展允许combined artifact，但必须保持向后兼容并新增严格artifact kind。

不得破坏现有band / DOS manifest。

---

# 8. Combined Top-Level Contract

建议：

```json
{
  "schema_version": "phase10h.phonon_band_dos.v1",
  "structure_identity": "sha256:...",
  "band": {
    "artifact_id": "artifact-band",
    "sha256": "...",
    "schema_version": "phase10h.phonon_band.v1"
  },
  "dos": {
    "artifact_id": "artifact-dos",
    "sha256": "...",
    "schema_version": "phase10h.phonon_dos.v1"
  },
  "compatibility": {
    "status": "compatible",
    "report_artifact_id": "artifact-compatibility",
    "frequency_conversion_applied": false,
    "density_jacobian_applied": false,
    "warnings": []
  },
  "frequency_axis": {
    "unit": "terahertz",
    "minimum": -1.2,
    "maximum": 15.4,
    "domain_policy": "union",
    "zero_tolerance": 0.000001
  },
  "display": {
    "layout": "band_left_dos_right",
    "shared_frequency_axis": true,
    "dos_orientation": "density_x_frequency_y",
    "default_projection_mode": "total_only",
    "selected_projections": []
  },
  "provenance": {},
  "warnings": [],
  "security": {
    "contains_javascript": false,
    "external_urls": []
  }
}
```

要求：

* 不复制完整band数值
* 不复制完整DOS数值
* 引用原始artifact ID和hash
* compatibility report单独保存
* derived display representation受控
* source artifacts保持不可变
* combined artifact必须可deterministic hash

---

# 9. Artifact Reference Validation

每个输入artifact reference必须验证：

* artifact存在
* media type批准
* schema version批准
* sha256匹配
* size在cap内
* security metadata通过
* artifact未被替换
* artifact type正确
* band reference不是DOS
* DOS reference不是band

typed errors建议：

```text
PHONON_BAND_DOS_BAND_ARTIFACT_INVALID
PHONON_BAND_DOS_DOS_ARTIFACT_INVALID
PHONON_BAND_DOS_ARTIFACT_HASH_MISMATCH
PHONON_BAND_DOS_ARTIFACT_SCHEMA_UNSUPPORTED
```

不得仅依赖客户端提交的schema string。

---

# 10. Compatibility状态

必须严格支持：

```text
compatible
convertible
incompatible
```

## 10.1 compatible

表示：

* 无需改变科学数值语义
* units已相同
* structure一致
* atom order一致
* source lineage兼容
* NAC兼容
* normalization有效
* 可直接形成combined view

## 10.2 convertible

只允许严格定义、可验证、不会丢失科学信息的转换，例如：

* THz → canonical THz，无变化
* cm⁻¹ → THz
* meV → THz
* DOS frequency axis转换
* DOS density Jacobian转换
* broadening width单位转换
* zero tolerance单位转换

不得将以下情况标为convertible：

* structure mismatch
* atom order mismatch
* source lineage mismatch
* NAC mismatch
* unknown normalization
* missing structure identity
* partial数据被当完整数据
* frequency range差异需要插值
* projection identity不明确

## 10.3 incompatible

任何hard compatibility check失败时：

* 不生成combined plot
* 不生成combined summary成功artifact
* 不生成partial combined product
* 返回typed failure
* 可以生成安全的validation failure report，按现有artifact policy决定

不得产生“部分看起来可用”的combined UI。

---

# 11. Compatibility检查顺序

必须使用固定顺序，保证deterministic errors。

推荐顺序：

1. input artifact count
2. artifact schema
3. artifact hash
4. structure identity
5. atom count
6. species ordering
7. primitive / supercell lineage
8. calculation / force constants lineage
9. reciprocal convention，若相关
10. frequency unit
11. imaginary encoding
12. zero tolerance
13. NAC
14. DOS normalization
15. projected DOS identity
16. caps
17. frequency domain
18. display options

warning和error顺序必须固定。

---

# 12. Structure Identity Validation

必须满足：

```text
band.structure_identity == dos.structure_identity
```

该identity必须是：

* canonical structure content hash
* 或项目批准的validated structure identity

不得使用以下内容替代：

* formula
* reduced formula
* atom count
* lattice volume
* space group
* composition
* filename

如果structure identity不同：

```text
PHONON_BAND_DOS_STRUCTURE_MISMATCH
```

直接判定incompatible。

必须在error details中提供：

* sanitized band identity
* sanitized DOS identity
* no raw structure
* no local path

---

# 13. Atom Count和Species Ordering

必须检查：

```text
band.atom_count == dos.atom_count
```

以及：

```text
band.species[i] == dos.species[i]
```

对所有`i`成立。

不得仅比较：

```text
sorted(species)
```

不得只比较composition。

失败：

```text
PHONON_BAND_DOS_ATOM_COUNT_MISMATCH
PHONON_BAND_DOS_ATOM_ORDER_MISMATCH
```

即使structure identity相同，也必须执行防御性验证。

---

# 14. Primitive / Supercell Lineage

如果provenance包含：

* primitive matrix
* supercell matrix
* primitive structure identity
* conventional structure identity

必须验证band和DOS的科学cell lineage兼容。

第一版推荐严格规则：

* canonical structure identity相同
* primitive identity相同
* supercell matrix相同或按contract被证明等价
* force constants identity相同

不得：

* 一个来自primitive cell、另一个来自supercell却机械组合
* 仅因formula相同而接受
* 自动转换primitive/supercell phonon modes

typed error：

```text
PHONON_BAND_DOS_CELL_LINEAGE_MISMATCH
```

---

# 15. Source Calculation Lineage

Combined product必须优先验证：

* calculation identity
* force constants hash
* dynamical matrix source
* producer
* producer version
* input structure hash
* adapter version
* source artifact hash

推荐新增或复用：

```text
phonon_calculation_identity
```

理想情况：

```text
band.source.phonon_calculation_identity
==
dos.source.phonon_calculation_identity
```

如果缺失：

## 严格产品模式

推荐：

```text
incompatible
```

因为无法证明来自同一phonon计算。

## 受限兼容模式

仅当项目Phase 10H contract已批准“缺失lineage时warning组合”，才能：

* status = compatible
* warning = `PHONON_BAND_DOS_LINEAGE_INCOMPLETE`

不得由本阶段临时放宽。

typed errors / warnings：

```text
PHONON_BAND_DOS_SOURCE_LINEAGE_MISMATCH
PHONON_BAND_DOS_LINEAGE_INCOMPLETE
PHONON_BAND_DOS_FORCE_CONSTANTS_MISMATCH
```

---

# 16. Frequency Unit Compatibility

Band和DOS必须统一到Phase 10H canonical unit。

假设canonical为：

```text
terahertz
```

允许：

* THz → THz
* cm⁻¹ → THz
* meV → THz

不允许：

* arbitrary unit expression
* rad/s，除非Phase 10H已正式批准
* unknown unit
* unit label mismatch without metadata

转换必须使用Phase 10H统一constants helper。

不得重复定义magic numbers。

---

# 17. DOS Density Jacobian

这是本阶段最重要的数值要求之一。

若DOS frequency发生：

```text
f_new = c × f_old
```

则必须：

```text
D_new(f_new) = D_old(f_old) / c
```

使得：

```text
∫ D_new df_new = ∫ D_old df_old
```

转换必须覆盖：

* total DOS
* atom-projected DOS
* species-projected DOS
* broadening width
* summary integral
* negative-region integral
* display values

必须测试：

* positive conversion factor
* negative frequency sign保留
* nonuniform grid
* total integral invariance
* projected integral invariance
* broadening width conversion

不得：

* 只转换frequency grid
* 忘记projected DOS
* 忘记broadening width
* 修改normalization target

---

# 18. Imaginary Frequency Encoding

必须验证：

```text
band.imaginary_frequency_encoding
==
dos.imaginary_frequency_encoding
```

推荐canonical：

```text
negative_real
```

如果一方为negative real、一方为其他representation：

只有存在Phase 10H批准的严格转换时才可convertible。

否则：

```text
PHONON_BAND_DOS_IMAGINARY_ENCODING_MISMATCH
```

不得：

* 将negative values取绝对值
* 删除negative region
* 把DOS负频区域移动到正频
* 将band imaginary branches隐藏

---

# 19. Zero Tolerance Compatibility

Band和DOS的：

```text
frequency_zero_tolerance
```

必须兼容。

推荐策略：

* 完全一致：compatible
* unit不同但数值转换后相同：convertible
* 不同科学阈值：incompatible或明确approved warning

不得静默选择：

* band tolerance
* DOS tolerance
* 两者最大值
* 两者最小值

除非Phase 10H contract已有固定policy。

建议严格：

```text
converted tolerances must be equal within application-owned numeric tolerance
```

失败：

```text
PHONON_BAND_DOS_ZERO_TOLERANCE_MISMATCH
```

---

# 20. NAC Compatibility

必须验证：

* NAC enabled状态
* NAC来源
* Born charges identity，若记录
* dielectric tensor identity，若记录
* Gamma direction
* direction policy
* LO-TO splitting policy

第一版推荐：

```text
band NAC enabled != DOS NAC enabled
→ incompatible
```

Gamma方向不一致：

```text
→ incompatible
```

typed error：

```text
PHONON_BAND_DOS_NAC_MISMATCH
PHONON_BAND_DOS_NAC_DIRECTION_MISMATCH
```

不得：

* 一方enabled一方disabled仍组合
* 忽略Gamma方向
* 将NAC差异仅作为UI warning

---

# 21. Acoustic Sum Rule Metadata

Band和DOS的ASR metadata必须被读取和显示。

检查：

* applied
* method
* source

第一版可采用：

* 相同：compatible
* 一方unknown：warning或failure，按既定contract
* 明显不同：warning或incompatible

不得执行新的ASR correction。

不得修改原始频率或DOS。

建议warning：

```text
PHONON_BAND_DOS_ASR_POLICY_DIFFERENCE
```

---

# 22. DOS Normalization Validation

DOS必须先通过Phase 10H-2 validator。

Combined composer不得接受：

* normalization unknown
* integral material mismatch
* invalid density unit
* invalid atom count
* invalid expected mode count
* projection identity invalid

推荐要求：

```text
normalization = total_modes
```

或Phase 10H允许的正式normalization。

如果DOS为unit-area且Phase 10H-2已转换为total_modes，则combined只消费转换后的canonical artifact。

不得在combined阶段重新归一化DOS。

---

# 23. Projected DOS Compatibility

如果combined view显示projected DOS：

必须验证：

* projection type
* atom index
* species
* projection scope
* completeness
* values长度
* units
* normalization
* structure identity

Atom projection：

```text
atom_index必须绑定canonical atom order
```

Species projection：

```text
species必须存在于canonical species order
```

不得：

* 仅使用display label
* frontend按名字猜identity
* 将partial projection显示为complete
* 自动聚合atom→species
* 自动重归一化projection

---

# 24. Compatibility Report Schema

建议新增：

```text
phase10h.phonon_band_dos_compatibility_report.v1
```

结构建议：

```json
{
  "schema_version": "phase10h.phonon_band_dos_compatibility_report.v1",
  "status": "compatible",
  "band_artifact": {
    "artifact_id": "...",
    "sha256": "..."
  },
  "dos_artifact": {
    "artifact_id": "...",
    "sha256": "..."
  },
  "checks": [
    {
      "name": "structure_identity",
      "status": "pass",
      "code": null
    },
    {
      "name": "frequency_unit",
      "status": "convertible",
      "code": null
    }
  ],
  "conversion": {
    "frequency_unit_from": "inverse_centimeter",
    "frequency_unit_to": "terahertz",
    "density_jacobian_applied": true,
    "integral_before": 6.0,
    "integral_after": 6.0
  },
  "frequency_domain": {
    "band": [-1.2, 15.0],
    "dos": [-2.0, 16.0],
    "display": [-2.0, 16.0],
    "policy": "union"
  },
  "warnings": [],
  "deterministic": true
}
```

要求：

* check order固定
* values经过sanitize
* 不包含raw arrays
* 不包含stack trace
* 不包含local path
* 不包含library repr
* 不包含secret

---

# 25. Derived Display Representation

Combined phase允许生成display-owned derived representation。

建议：

```text
phase10h.phonon_band_dos_display.v1
```

可包含：

* canonical frequency unit下的band display series
* canonical frequency unit下的DOS display series
* shared y-domain
* zero line
* segment breaks
* selected projections
* labels
* plot caps和mode

但不得：

* 成为新的scientific source of truth
* 修改原始band和DOS artifact
* 丢失source references
* 隐藏conversion history

必须标记：

```text
derived_for_display = true
```

并记录：

* source artifact hashes
* conversion policy
* display options
* derived hash

如果现有plot contract可以直接引用两个artifact并在前端安全映射，则不必重复完整arrays。

---

# 26. Shared Frequency Axis

Combined view必须实现真实shared frequency axis。

桌面布局：

```text
┌─────────────────────────────┬──────────────┐
│                             │              │
│       Phonon Bands          │  Phonon DOS  │
│                             │              │
│  q-path  →                  │  DOS  →      │
│  frequency ↑                │  frequency ↑ │
│                             │              │
└─────────────────────────────┴──────────────┘
```

要求：

* 两panel使用同一个frequency domain对象
* y-scale计算只发生一次或由共享domain驱动
* zero line使用同一coordinate
* negative region使用同一range
* y-axis ticks一致
* resize后仍对齐
* browser缩放后仍对齐
* 200% zoom仍保持语义

不得只靠视觉上相近的两个独立axis。

---

# 27. Frequency Domain Policy

必须定义受控枚举：

```text
union
intersection
band_domain
dos_domain
manual_view
```

推荐默认：

```text
union
```

原因：

* 不丢band数据
* 不丢DOS数据
* negative region完整
* 不隐式裁剪

## union

```text
min = min(band_min, dos_min)
max = max(band_max, dos_max)
```

## intersection

本阶段不建议作为默认。

仅可作为用户显式display override，且必须说明会隐藏范围外数据。

## manual_view

只影响显示，不修改artifact。

必须：

* bounded
* within union domain或明确允许zoom
* no scientific data mutation
* reset可恢复union

不得：

* 在DOS范围外补0
* 在band范围外插值
* 改变summary中的完整range

---

# 28. Frequency Range Difference Policy

范围不同并不自动表示不兼容。

必须区分：

## Normal Difference

例如：

* band：-1到15 THz
* DOS：-2到16 THz

可能由于DOS mesh范围稍宽。

允许combined，使用union，并记录warning或info。

## Suspicious Difference

例如：

* band：0到10 THz
* DOS：-20到80 THz

必须结合source lineage、units和normalization判断。

可以：

* warning
* incompatible

需要application-owned ratio/absolute policy。

typed warning：

```text
PHONON_BAND_DOS_FREQUENCY_RANGE_DIFFERENCE
```

不得仅凭range自动转换或裁剪。

---

# 29. Band Panel要求

Band panel必须复用Phase 10H-1科学结果，不得重新解释。

必须保留：

* q-point order
* segment order
* shared endpoints
* discontinuities
* high-symmetry labels
* branch order
* source-stable branch identity
* negative frequencies
* zero line
* unit metadata

不得：

* 重新计算path
* 按frequency排序branch
* 合并degenerate branches
* 连接discontinuous segments
* 插值缺失点
* 删除imaginary branch

---

# 30. DOS Panel方向

Combined DOS必须使用：

```text
x = DOS density
y = frequency
```

而不是standalone view：

```text
x = frequency
y = DOS
```

要求：

* frequency与band共享y-axis
* density从0向右
* total DOS为主series
* projected DOS为可选series
* density unit明确
* normalization明确
* negative frequency位于zero line下方
* broadening metadata显示
* 不重采样
* 不平滑
* 不stack incomplete projection

---

# 31. Zero Line和Imaginary Region

必须验证视觉和数值对齐。

要求：

* band panel zero line y-coordinate
* DOS panel zero line y-coordinate

二者在允许的pixel tolerance内一致。

必须有自动browser assertion。

Imaginary region：

```text
frequency < -zero_tolerance
```

必须在两panel中一致。

Near-zero region：

```text
abs(frequency) <= zero_tolerance
```

不得修改原始值。

说明文本：

```text
Negative frequency values represent imaginary phonon modes under the shared negative-real encoding.
```

不得只用颜色表达。

---

# 32. Projected DOS默认策略

默认：

```text
total DOS only
```

原因：

* combined view主要强调band与DOS关系
* 防止projection过多造成视觉噪声
* 降低性能成本
* 避免legend爆炸

用户可以选择：

* species projection
* atom projection
* bounded multiple projections

推荐同时可见上限：

```text
desktop: 4
mobile: 2
```

真实值应根据性能审计确定。

不得由artifact指定上限。

---

# 33. Projection Selector

selector必须显示：

* type
* atom index或species
* projection scope
* completeness
* source

示例：

```text
Total DOS
Species: Si
Atom 0: Si
Atom 1: Si
```

如果projection completeness为partial：

必须显示：

```text
Partial projection set
```

不得给用户造成完整分解的误解。

Selector必须：

* keyboard accessible
* mobile touch target合格
* deterministic order
* 无HTML注入
* 不使用tooltip作为唯一信息来源

---

# 34. Projection Aggregation禁止

本阶段默认不得：

* frontend临时聚合atom projections
* frontend求species sum
* frontend计算average
* frontend重归一化
* frontend判断complete decomposition

如果Phase 10H-2已经输出species projection，则可直接选择。

如确需新增aggregation，必须：

* backend生成
* schema明确
* provenance明确
* tests独立
* 不修改原始DOS

本阶段建议不新增aggregation。

---

# 35. Broadening显示

Combined summary和DOS panel必须显示：

* method
* width
* unit
* source

例如：

```text
DOS broadening: Gaussian, 0.10 THz
```

如unknown：

```text
DOS broadening metadata unavailable
```

不得在combined phase重新执行broadening。

不得让band line styling暗示相同broadening。

---

# 36. Combined Summary Contract

建议新增：

```text
phase10h.phonon_band_dos_summary.v1
```

至少包含：

```json
{
  "schema_version": "phase10h.phonon_band_dos_summary.v1",
  "structure_identity": "sha256:...",
  "atom_count": 2,
  "species": ["Si", "Si"],
  "branch_count": 6,
  "qpoint_count": 101,
  "segment_count": 4,
  "dos_grid_point_count": 1001,
  "projection_count": 2,
  "frequency_unit": "terahertz",
  "frequency_min": -2.0,
  "frequency_max": 16.0,
  "band_frequency_min": -1.2,
  "band_frequency_max": 15.4,
  "dos_frequency_min": -2.0,
  "dos_frequency_max": 16.0,
  "imaginary_band_mode_count": 2,
  "imaginary_dos_integral": 0.04,
  "dos_density_unit": "modes_per_terahertz",
  "dos_normalization": "total_modes",
  "dos_integral": 5.98,
  "expected_modes": 6,
  "compatibility_status": "compatible",
  "nac_enabled": false,
  "warnings": []
}
```

不得：

* 给出最终稳定/不稳定结论
* 把imaginary count直接解释成结构必然不稳定
* 隐藏DOS integral偏差
* 隐藏compatibility warnings

---

# 37. Combined Plot Contract

建议新增：

```text
phase10h.phonon_band_dos_plot.v1
```

建议结构：

```json
{
  "schema_version": "phase10h.phonon_band_dos_plot.v1",
  "layout": "band_left_dos_right",
  "shared_frequency_axis": {
    "unit": "terahertz",
    "minimum": -2.0,
    "maximum": 16.0,
    "zero_tolerance": 0.000001,
    "domain_policy": "union"
  },
  "band_panel": {
    "x_axis": "q_path_distance",
    "series_source": "band_artifact",
    "show_zero_line": true,
    "preserve_segment_breaks": true
  },
  "dos_panel": {
    "x_axis": "dos_density",
    "y_axis": "shared_frequency",
    "density_unit": "modes_per_terahertz",
    "show_total_dos": true,
    "selected_projection_ids": []
  },
  "display": {
    "show_imaginary_region": true,
    "show_high_symmetry_labels": true,
    "mode": "interactive"
  }
}
```

不得包含任意render function或callback。

---

# 38. Desktop Layout

推荐比例：

```text
band panel: 75%
DOS panel: 25%
```

允许application-owned范围：

```text
70/30
75/25
80/20
```

必须固定默认值。

要求：

* 共同高度
* y-axis对齐
* band panel显示y-axis labels
* DOS panel可隐藏重复y-axis text，但保留语义
* panel间距不改变shared scale
* high-symmetry labels不与DOS重叠
* resize后重新布局但不重算科学数据

不得让artifact指定任意比例。

---

# 39. Mobile / Narrow Viewport

移动端不应强行压缩side-by-side。

允许两种模式：

## 39.1 Stacked

```text
Band
↓
DOS
```

要求：

* 使用同一frequency domain
* 两panel显示相同min/max
* 文本明确说明共享domain
* zero line语义一致

## 39.2 Tabbed

```text
Bands | DOS | Summary
```

要求：

* tabs ARIA正确
* 切换不丢selection
* domain一致
* no duplicate chart allocation
* no scroll trap

推荐按现有UI能力选择：

```text
desktop: side-by-side
mobile: tabbed or stacked
```

不得在mobile隐藏任一panel。

---

# 40. Combined Table策略

不得生成无意义的巨大笛卡尔积：

```text
qpoints × branches × dos_grid_points
```

建议提供：

## Compatibility Table

列：

* check
* band value
* DOS value
* status
* code

## Combined Summary Table

列：

* structure identity
* atom count
* frequency unit
* range
* NAC
* DOS normalization
* DOS integral
* expected modes
* imaginary metrics

## Linked Tabs

* Band Data
* DOS Data
* Compatibility
* JSON

可以复用Phase 10H-1和10H-2已有table artifacts。

不得复制全部数据形成新巨大table。

---

# 41. Combined Manifest

建议：

```text
phase10h.phonon_band_dos_manifest.v1
```

artifact顺序固定：

1. `phonon_band_dos.json`
2. `phonon_band_dos_summary.json`
3. `phonon_band_dos_compatibility_report.json`
4. `phonon_band_dos_plot.json`
5. `phonon_band_dos_table.json`
6. `phonon_band_dos_manifest.json`

Manifest必须包含：

* schema version
* media type
* byte size
* sha256
* band artifact reference
* DOS artifact reference
* structure identity
* compatibility status
* frequency unit
* security markers
* deterministic artifact order

不得包含：

* JS
* HTML
* eigenvectors
* remote assets
* external URLs
* executable SVG

---

# 42. Export Policy

若现有plot export支持，允许：

* PNG
* safe SVG
* combined JSON
* compatibility report
* manifest

Export必须记录：

* structure identity
* band artifact hash
* DOS artifact hash
* frequency unit
* shared domain
* projection selection
* compatibility status
* tool ID
* schema version

不得：

* 导出可执行HTML
* 嵌入remote font
* 嵌入script
* 嵌入callback
* 依赖CDN
* 将大artifact无界base64嵌入

若SVG安全无法保证：

```text
SVG export: DEFERRED_BY_DESIGN
```

PNG和JSON可以READY。

---

# 43. Tool Metadata

建议：

```json
{
  "tool_id": "phonon.band_dos",
  "category": "phonon",
  "display_name": "Phonon Band and DOS",
  "description": "Validate and display compatible phonon band and density-of-states artifacts on a shared frequency axis.",
  "input_contracts": [
    "phase10h.phonon_band.v1",
    "phase10h.phonon_dos.v1"
  ],
  "output_contract": "phase10h.phonon_band_dos.v1",
  "execution_mode": "service_backed",
  "deterministic": true,
  "network_access": false
}
```

Capabilities必须真实：

```text
phonon_bands: true
phonon_dos: true
combined_view: true
shared_frequency_axis: true
imaginary_modes: true
unit_conversion: true
normalization_validation: true
projected_dos: according to implementation
export: according to implementation

eigenvectors: false
animation: false
thermal_properties: false
phonon_calculation: false
dynamic_3d: false
```

不得用单一boolean掩盖PARTIAL_READY功能。

---

# 44. Planner Routing

正向请求：

```text
Show the phonon bands and DOS together.
```

```text
Create a combined phonon dispersion and density-of-states plot.
```

```text
Compare this phonon band artifact with its phonon DOS.
```

已有兼容输入时，应选择：

```text
phonon.band_dos
```

Band-only请求：

```text
Plot the phonon bands.
```

必须继续选择：

```text
phonon.bands
```

DOS-only请求：

```text
Show the phonon DOS.
```

必须继续选择：

```text
phonon.dos
```

以下请求不得由combined tool完成：

```text
Animate the unstable mode.
Show the eigenvector at Gamma.
Calculate the phonons.
Compute heat capacity.
Compute thermal conductivity.
```

必须返回：

* typed unsupported
* 或等待未来tool

不得从普通structure artifact直接承诺计算phonon band或DOS。

---

# 45. Multi-Input PlanValidator

必须验证：

* exactly one band artifact
* exactly one DOS artifact
* no duplicate input role
* schemas正确
* artifact hashes正确
* artifacts可读取
* compatibility validator通过
* projection options受allowlist约束
* visible projection count受cap约束
* domain override受bounds约束
* layout option受allowlist约束
* no eigenvector request
* no animation request
* no calculation request
* no arbitrary unit expression
* no arbitrary callback
* no external URL

typed codes至少包括：

```text
PHONON_BAND_DOS_BAND_INPUT_REQUIRED
PHONON_BAND_DOS_DOS_INPUT_REQUIRED
PHONON_BAND_DOS_INPUT_COUNT_INVALID
PHONON_BAND_DOS_INPUT_SCHEMA_INVALID
PHONON_BAND_DOS_ARTIFACT_HASH_MISMATCH
PHONON_BAND_DOS_STRUCTURE_MISMATCH
PHONON_BAND_DOS_ATOM_COUNT_MISMATCH
PHONON_BAND_DOS_ATOM_ORDER_MISMATCH
PHONON_BAND_DOS_CELL_LINEAGE_MISMATCH
PHONON_BAND_DOS_SOURCE_LINEAGE_MISMATCH
PHONON_BAND_DOS_FORCE_CONSTANTS_MISMATCH
PHONON_BAND_DOS_FREQUENCY_UNIT_INCOMPATIBLE
PHONON_BAND_DOS_IMAGINARY_ENCODING_MISMATCH
PHONON_BAND_DOS_ZERO_TOLERANCE_MISMATCH
PHONON_BAND_DOS_NAC_MISMATCH
PHONON_BAND_DOS_NAC_DIRECTION_MISMATCH
PHONON_BAND_DOS_NORMALIZATION_INVALID
PHONON_BAND_DOS_PROJECTION_INVALID
PHONON_BAND_DOS_PROJECTION_LIMIT_EXCEEDED
PHONON_BAND_DOS_DOMAIN_INVALID
PHONON_BAND_DOS_LAYOUT_UNSUPPORTED
PHONON_BAND_DOS_EIGENVECTOR_UNSUPPORTED
PHONON_BAND_DOS_ANIMATION_UNSUPPORTED
PHONON_CALCULATION_UNSUPPORTED
```

不得放宽现有band和DOS validator。

---

# 46. Composer Architecture

建议正式流程：

```text
band artifact reference
+
DOS artifact reference
→ resolve artifacts
→ verify hashes
→ validate band independently
→ validate DOS independently
→ run compatibility validator
→ apply approved unit conversion if needed
→ apply DOS density Jacobian
→ verify integral invariance
→ derive shared frequency domain
→ derive projection display set
→ create combined summary
→ create compatibility report
→ create combined plot contract
→ create combined table references
→ create manifest
→ emit artifacts
```

必须保证：

* band validator失败时立即停止
* DOS validator失败时立即停止
* compatibility失败时不生成combined success artifacts
* conversion失败时不生成partial product
* source artifacts不被修改
* no frontend scientific correction

---

# 47. API正式路径

必须证明：

```text
existing band artifact
+
existing DOS artifact
→ planner or direct formal tool request
→ PlanValidator
→ service-backed runtime
→ artifact resolution
→ compatibility validator
→ composer
→ combined artifacts
→ artifact validator
→ frontend product surface
```

不得通过：

* fixture直接注入frontend
* 直接调用plot function
* 跳过registry
* 跳过PlanValidator
* 跳过runtime
* 跳过artifact validation

---

# 48. API Evidence Cases

至少覆盖：

## 48.1 Fully Compatible Pair

* same structure
* same atom order
* same source lineage
* same unit
* same NAC
* valid DOS normalization
* success

## 48.2 Convertible Unit Pair

例如：

* band = THz
* DOS = cm⁻¹

必须证明：

* DOS frequency转换
* density Jacobian
* broadening width转换
* integral before/after一致
* shared axis正确

## 48.3 Imaginary Pair

* band有negative modes
* DOS有negative-frequency weight
* zero line一致
* summary一致

## 48.4 Projected DOS Pair

* selector正确
* identity正确
* visible cap正确
* partial/complete语义正确

## 48.5 Structure Mismatch

* typed failure
* no combined artifacts
* no plot

## 48.6 Atom Ordering Mismatch

* typed failure

## 48.7 Cell Lineage Mismatch

* typed failure

## 48.8 Source / Force Constants Mismatch

* typed failure或按正式contract处理

## 48.9 NAC Mismatch

* typed failure

## 48.10 Invalid Normalization

* typed failure

## 48.11 Over-Cap

* degraded或refused
* no browser freeze
* no partial plot

---

# 49. Frontend产品界面

正式result surface至少显示：

* product title
* tool ID或明确产品名称
* compatibility status
* structure identity摘要
* band artifact reference
* DOS artifact reference
* source lineage摘要
* frequency unit
* shared frequency domain
* atom count
* branch count
* q-point count
* DOS grid count
* imaginary band mode count
* imaginary DOS integral
* DOS normalization
* expected / observed DOS integral
* NAC status
* broadening metadata
* projection selector
* combined plot
* compatibility report
* Band Data tab
* DOS Data tab
* JSON tab
* warnings
* artifact downloads

不得显示：

* eigenvector selector
* animation controls
* thermal properties
* stability最终结论
* phonon calculation按钮，除非平台其他阶段已有正式功能

---

# 50. Accessibility

Combined product必须满足：

## 50.1 Region

名称：

```text
Combined phonon band and density of states
```

## 50.2 Text Summary

建议：

```text
Combined phonon band and density-of-states view for a two-atom structure. Six branches are displayed across 101 q-points. The shared frequency range is -2.0 to 16.0 THz. Two band modes and a DOS weight of 0.04 modes occur below zero frequency.
```

## 50.3 Panel Semantics

Band panel：

```text
Phonon band panel
```

DOS panel：

```text
Phonon density-of-states panel
```

## 50.4 Controls

* projection selector
* view domain reset
* mobile tabs
* table tabs
* downloads

均可键盘访问。

## 50.5 Non-Color Semantics

不得仅靠颜色表达：

* imaginary modes
* total vs projected DOS
* compatibility warning
* selected projection

## 50.6 Zoom

必须验证200% zoom。

## 50.7 Screen Reader

必须能读取：

* shared axis unit
* range
* zero line语义
* compatibility status
* projection identity
* DOS normalization

---

# 51. Mobile要求

至少验证：

* portrait
* landscape
* stacked或tabbed布局
* band labels可读
* DOS selector可用
* summary可读
* warnings可见
* table fallback
* artifact download
* no scroll trap
* no overlapping controls
* no duplicate chart instance
* orientation change稳定

Mobile不得：

* 隐藏band或DOS
* 使用tooltip作为唯一数据入口
* 强制side-by-side导致不可读
* 渲染全部projections

---

# 52. Performance Tiers

建立combined-specific性能策略。

## Interactive

支持：

* full band series
* total DOS
* bounded projections
* full high-symmetry labels
* table tabs
* export

## Degraded

可以：

* total DOS only
* projections默认关闭
* fewer visible labels
* table分页
* disable expensive hover
* preserve完整scientific artifacts

必须显示：

```text
PHONON_BAND_DOS_PLOT_DEGRADED
```

## Refused

超过hard display cap：

* no combined chart
* summary可用
* compatibility report可用
* artifacts可下载
* typed reason
* no huge DOM/SVG allocation

typed error：

```text
PHONON_BAND_DOS_PLOT_BUDGET_EXCEEDED
```

不得通过删branch、删DOS points或重采样来伪造性能。

---

# 53. Combined Caps

至少定义：

* max band branches
* max band q-points
* max band numeric values
* max DOS grid points
* max total projections
* max visible projections
* max combined plotted numeric values
* max labels
* max table rows
* max artifact bytes
* max SVG paths
* max legend entries

必须使用overflow-safe：

```text
qpoints × branches
dos_points × visible_projections
total combined values
```

必须在render allocation前判断。

---

# 54. Determinism

必须固定：

* band input role
* DOS input role
* compatibility check order
* error order
* warning order
* unit conversion
* floating serialization
* frequency domain
* projection order
* default projection selection
* panel order
* manifest order
* table tab order
* artifact order
* hash

相同：

* band hash
* DOS hash
* options

必须得到相同combined artifact hash。

不得加入：

* current timestamp
* random UUID
* environment path
* browser-specific value

---

# 55. Security

必须验证：

* no artifact JavaScript
* no artifact HTML execution
* no SVG script
* no callback
* no arbitrary plot expression
* no arbitrary layout expression
* no arbitrary unit expression
* no external URL
* no remote font
* no CDN
* no iframe
* no eval
* no Function constructor
* no notebook execution
* no script execution
* no real LLM
* no artifact-controlled caps
* no artifact-controlled projection limit
* no artifact-controlled renderer
* no markup labels
* no metadata recursion abuse
* no path leakage
* no secret
* no telemetry upload

必须输出：

```text
NO_EXTERNAL_NETWORK_REQUESTS
NO_SECRET_PATTERN_HITS
```

---

# 56. Fixtures

新增small、deterministic fixtures。

至少：

## 56.1 Fully Compatible Pair

* 2 atoms
* 6 branches
* same source lineage
* same unit
* no NAC
* valid DOS normalization

## 56.2 Convertible Unit Pair

* band THz
* DOS cm⁻¹
* Jacobian required
* integral invariant

## 56.3 meV Conversion Pair

* DOS meV
* canonical THz

## 56.4 Imaginary Pair

* negative band mode
* negative DOS region
* shared zero line

## 56.5 Range Difference Pair

* DOS range wider
* union domain

## 56.6 Species Projected Pair

* species selector

## 56.7 Atom Projected Pair

* atom identity selector

## 56.8 Partial Projection Pair

* partial completeness说明

## 56.9 Structure Mismatch

## 56.10 Atom Order Mismatch

## 56.11 Cell Lineage Mismatch

## 56.12 Force Constants Mismatch

## 56.13 NAC Mismatch

## 56.14 Zero Tolerance Mismatch

## 56.15 Invalid DOS Normalization

## 56.16 Degraded Combined Plot

## 56.17 Over-Cap Synthetic

不得提交大型真实dataset。

---

# 57. Unit Tests

至少覆盖：

## Compatibility

* compatible
* convertible
* incompatible
* deterministic check order
* deterministic error order

## Artifact References

* valid band
* valid DOS
* wrong role
* invalid hash
* unsupported schema
* missing artifact

## Structure

* same identity
* mismatch
* atom count mismatch
* species order mismatch
* same composition different order

## Lineage

* same calculation
* missing calculation ID
* force constants mismatch
* primitive mismatch
* supercell mismatch
* producer version policy

## Units

* same unit
* cm⁻¹ to THz
* meV to THz
* density Jacobian
* projected Jacobian
* broadening width
* integral invariance

## Imaginary / Zero

* same encoding
* mismatch
* same tolerance
* converted tolerance
* mismatch
* negative range

## NAC

* both disabled
* both enabled same direction
* enabled/disabled mismatch
* direction mismatch

## DOS

* valid normalization
* unknown normalization
* integral mismatch
* partial projection
* complete projection
* invalid projection identity

## Frequency Domain

* same
* band wider
* DOS wider
* union
* manual bounded view
* invalid bounds

## Plot

* shared y-domain
* aligned zero line
* band-left
* DOS-right
* horizontal DOS
* discontinuity
* negative region
* total DOS
* selected projection
* degraded
* refused

## Manifest / Summary

* schema
* counts
* ranges
* artifact order
* hashes
* warnings
* source refs

## Security

* HTML label
* callback
* arbitrary layout
* external URL
* oversized projection list
* private path

---

# 58. API Tests

覆盖：

* compatible pair
* convertible pair
* meV pair
* imaginary pair
* projected pair
* partial projection
* structure mismatch
* atom order mismatch
* cell lineage mismatch
* force constants mismatch
* NAC mismatch
* zero tolerance mismatch
* invalid normalization
* over-cap
* deterministic replay
* artifact retrieval
* no partial success artifacts
* frontend launch metadata

---

# 59. Browser Evidence

新增：

```text
docs/phase10h/evidence/phase10h3_combined_band_dos/
```

## Chromium完整矩阵

覆盖：

* tool discovery
* planner routing
* compatible pair
* convertible units
* imaginary region
* zero line alignment
* discontinuous path
* total DOS
* species projection
* atom projection
* compatibility report
* tables
* JSON
* export
* degraded
* refused
* incompatible error
* accessibility
* network/console audit

## Firefox

至少：

* combined layout
* shared domain
* zero alignment
* negative region
* projection selector
* fallback
* console/network

## WebKit

至少：

* combined layout
* resize
* responsive behavior
* projection selector
* table/JSON fallback
* console/network

## Mobile Chromium

至少：

* product entry
* tabbed/stacked layout
* band
* DOS
* selector
* warning
* table
* no scroll trap

## Mobile WebKit

至少：

* responsive mode
* tabs
* projection selection
* summary
* fallback
* canvas/chart count稳定

---

# 60. Browser Assertions

每个case记录：

* browser version
* viewport/device
* tool ID
* band artifact ID/hash
* DOS artifact ID/hash
* structure identity
* compatibility status
* source lineage status
* frequency unit
* shared min/max
* band range
* DOS range
* branch count
* q-point count
* DOS grid count
* projection count
* visible projections
* NAC
* normalization
* observed integral
* expected modes
* imaginary band count
* imaginary DOS integral
* plot tier
* chart count
* console errors
* network requests

必须断言：

* y-domain一致
* zero line对齐
* negative region一致
* discontinuities未连接
* DOS orientation正确
* compatibility report与backend一致
* projection identity正确
* no frontend silent conversion
* no external network
* no artifact JS
* no capability overclaim

---

# 61. Evidence Files

至少包含：

```text
README.md
combined_schema.json
combined_summary_schema.json
combined_plot_schema.json
combined_manifest_schema.json
compatibility_report_schema.json
compatibility_policy.json
compatibility_check_order.json
structure_identity_checks.json
atom_order_checks.json
cell_lineage_checks.json
source_lineage_checks.json
force_constants_checks.json
frequency_conversion.json
density_jacobian.json
integral_invariance.json
imaginary_encoding_policy.json
zero_tolerance_compatibility.json
nac_compatibility.json
frequency_domain_policy.json
projection_display_policy.json
layout_contract.json
performance_caps.json
compatible_pair_result.json
convertible_pair_result.json
mev_pair_result.json
imaginary_pair_result.json
range_difference_result.json
species_projected_result.json
atom_projected_result.json
partial_projection_result.json
structure_mismatch_result.json
atom_order_mismatch_result.json
cell_lineage_mismatch_result.json
force_constants_mismatch_result.json
nac_mismatch_result.json
zero_tolerance_mismatch_result.json
invalid_normalization_result.json
degraded_result.json
over_cap_result.json
api_compatible.json
api_convertible.json
api_incompatible.json
deterministic_replay.json
browser_chromium.json
browser_firefox.json
browser_webkit.json
browser_mobile_chromium.json
browser_mobile_webkit.json
accessibility_audit.json
performance_metrics.json
console_audit.json
network_audit.json
security_audit.json
artifact_hashes.json
```

截图建议：

```text
01_combined_band_dos.png
02_shared_frequency_axis.png
03_zero_line_alignment.png
04_imaginary_band_and_dos.png
05_discontinuous_band_segments.png
06_species_projection.png
07_atom_projection.png
08_compatibility_report.png
09_convertible_unit_pair.png
10_structure_mismatch_error.png
11_degraded_combined_view.png
12_refused_summary_fallback.png
13_mobile_tabbed_view.png
14_accessibility_summary.png
15_exported_combined_plot.png
```

不得保存：

* 大型raw数据
* browser cache
* full trace archive
* local paths
* tokens
* secrets
* remote URLs
* raw Python objects
* crash dumps

---

# 62. Performance Metrics

至少记录：

## Data

* branch count
* q-point count
* band values
* DOS grid points
* projection count
* visible projections
* total plotted values

## Render

* initial render duration
* resize duration
* projection switch duration
* tab switch duration
* export duration
* chart/path count
* DOM/SVG node proxy
* memory proxy

## Modes

* interactive
* degraded
* refused

## Browser

* Chromium
* Firefox
* WebKit
* mobile

不得使用单一严格毫秒值作为唯一PASS标准。

应关注：

* no freeze
* no crash
* bounded nodes
* bounded projection rendering
* deterministic tier
* responsive controls
* no monotonic resource growth

---

# 63. Dependency Policy

默认不新增依赖。

优先复用：

* Phase 10H-1 chart system
* Phase 10H-2 chart system
* existing grid/layout primitives
* existing plot export
* existing Playwright setup
* existing artifact validator
* existing unit conversion helpers

不得为了左右双panel引入第二套大型chart库。

检查：

```bash
uv lock --check
npm --prefix apps/web ls --depth=0
npm --prefix apps/web run build
```

记录：

* backend dependency changes
* frontend dependency changes
* lockfile
* bundle delta
* chart chunk delta
* license impact
* no unexpected additions

---

# 64. Documentation

新增：

```text
docs/phase10h/phase10h3_combined_band_dos.md
docs/phase10h/phase10h3_combined_schema.md
docs/phase10h/phase10h3_band_dos_compatibility.md
docs/phase10h/phase10h3_structure_and_atom_identity.md
docs/phase10h/phase10h3_source_lineage.md
docs/phase10h/phase10h3_frequency_conversion_and_jacobian.md
docs/phase10h/phase10h3_shared_frequency_axis.md
docs/phase10h/phase10h3_frequency_domain_policy.md
docs/phase10h/phase10h3_projection_display_policy.md
docs/phase10h/phase10h3_combined_plot_contract.md
docs/phase10h/phase10h3_combined_api_evidence.md
docs/phase10h/phase10h3_combined_accessibility_mobile.md
docs/phase10h/phase10h3_combined_performance.md
docs/phase10h/phase10h3_combined_security.md
docs/phase10h/phase10h3_combined_evidence.md
docs/phase10h/phase10h3_combined_readiness_matrix.md
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

* tool ID
* schema family
* compatibility states
* check order
* structure identity
* atom ordering
* cell lineage
* source lineage
* force constants identity
* unit conversion
* density Jacobian
* integral invariance
* imaginary encoding
* zero tolerance
* NAC
* DOS normalization
* shared frequency axis
* union domain
* projection policy
* desktop/mobile layout
* export policy
* performance tiers
* eigenvector deferred
* animation deferred

---

# 65. Readiness Matrix

最终必须逐项判断：

* combined top-level schema
* combined summary schema
* compatibility report schema
* plot schema
* manifest schema
* artifact references
* hash validation
* compatibility result states
* check ordering
* structure identity
* atom count
* species ordering
* primitive lineage
* supercell lineage
* calculation identity
* force constants identity
* frequency unit compatibility
* THz conversion
* cm⁻¹ conversion
* meV conversion
* DOS density Jacobian
* broadening width conversion
* integral invariance
* imaginary encoding compatibility
* zero tolerance compatibility
* NAC compatibility
* Gamma direction compatibility
* ASR metadata
* DOS normalization
* projection identity
* projection completeness
* shared frequency axis
* frequency domain policy
* band panel
* DOS panel
* discontinuities
* zero line
* imaginary region
* projected selector
* combined summary
* compatibility table
* manifest
* export
* registry
* planner routing
* PlanValidator
* runtime
* API
* frontend
* accessibility
* mobile
* Chromium
* Firefox
* WebKit
* performance
* determinism
* security
* eigenvector contract
* phonon animation

推荐期望：

```text
combined schema: READY
combined summary: READY
compatibility report: READY
combined plot contract: READY
combined manifest: READY
artifact reference validation: READY
compatibility validator: READY
structure identity: READY
atom count: READY
species ordering: READY
cell lineage: READY
source lineage: READY
force constants identity: READY
frequency conversion: READY
density Jacobian: READY
integral invariance: READY
imaginary encoding compatibility: READY
zero tolerance compatibility: READY
NAC compatibility: READY
DOS normalization validation: READY
projection identity: READY
projection completeness: READY
shared frequency axis: READY
frequency domain policy: READY
band panel: READY
DOS panel: READY
path discontinuities: READY
zero line alignment: READY
imaginary region: READY
projection selector: READY or PARTIAL_READY
combined summary/table: READY
manifest: READY
export: READY or PARTIAL_READY
registry: READY
planner: READY
PlanValidator: READY
runtime/API: READY
frontend: READY
accessibility: READY
mobile: READY
Chromium: READY
Firefox: READY
WebKit: READY
performance: READY
determinism: READY
security: READY

phonon eigenvector contract: NOT_READY
phonon animation: NOT_READY
dynamic phonon product: NOT_READY
```

---

# 66. Checks

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

* combined schema tests
* compatibility report tests
* artifact reference tests
* artifact hash tests
* structure identity tests
* atom count tests
* atom ordering tests
* cell lineage tests
* source lineage tests
* force constants tests
* frequency conversion tests
* DOS Jacobian tests
* integral invariance tests
* imaginary encoding tests
* zero tolerance tests
* NAC tests
* DOS normalization tests
* projection tests
* frequency domain tests
* shared-axis tests
* zero-line alignment tests
* band discontinuity tests
* DOS orientation tests
* combined plot tests
* combined summary tests
* manifest tests
* export tests
* registry tests
* planner tests
* PlanValidator tests
* runtime tests
* API integration
* frontend tests
* accessibility tests
* mobile tests
* Chromium full evidence
* Firefox smoke
* WebKit smoke
* mobile Chromium
* mobile WebKit
* performance tests
* security scan
* network audit
* Phase 10 Closure Regression Pack
* Phase 10G regression
* Phase 10H contract regression
* Phase 10H-1 band regression
* Phase 10H-2 DOS regression
* static viewer regression
* trajectory viewer regression
* service-backed integration
* no-skipped assertion

必须如实记录：

* passed
* failed
* skipped
* unavailable

不得把skipped写成passed。

---

# 67. Commit / CI

完成后：

```bash
git status --short
git diff --stat
git add <only Phase 10H-3 related files>
git commit -m "Add combined phonon band and DOS view"
git push origin master
```

等待current HEAD CI。

必须确认：

* backend unit success
* frontend unit success
* frontend typecheck success
* frontend build success
* combined compatibility tests success
* conversion/Jacobian tests success
* API integration success
* browser evidence success
* accessibility success
* mobile success
* Phase 10 Closure success
* Phase 10G regression success
* Phase 10H contract success
* Phase 10H-1 success
* Phase 10H-2 success
* static viewer regression success
* trajectory viewer regression success
* service-backed integration success
* no-skipped assertion success
* origin/master matches HEAD
* git status clean

不得伪造：

* commit
* CI run
* browser result
* API evidence
* git clean状态

---

# 68. 最终报告格式

完成后必须输出：

# Phase 10H-3 Combined Band + DOS Result

## 1. Conclusion

PASS / PARTIAL_PASS / FAIL

## 2. Baseline

* Phase 10H-2 assumed complete:
* branch:
* initial HEAD:
* initial status:
* final HEAD:
* final status:

## 3. Combined Schema Family

* combined:
* summary:
* compatibility report:
* plot:
* manifest:
* display representation:
* schema versions:

## 4. Tool Boundary

* tool ID:
* display name:
* registry status:
* planner visibility:
* band-only separation:
* DOS-only separation:
* eigenvector status:
* animation status:

## 5. Input Artifacts

* band artifact:
* band schema:
* band hash:
* DOS artifact:
* DOS schema:
* DOS hash:
* reference validation:
* role validation:

## 6. Compatibility States

* compatible:
* convertible:
* incompatible:
* check order:
* warning order:
* hard failure behavior:

## 7. Structure and Atom Identity

* structure identity:
* atom count:
* species ordering:
* primitive lineage:
* supercell lineage:
* mismatch behavior:

## 8. Source Lineage

* calculation identity:
* force constants identity:
* producer:
* producer version:
* adapter versions:
* incomplete lineage policy:
* mismatch behavior:

## 9. Frequency Compatibility

* band source unit:
* DOS source unit:
* canonical unit:
* band conversion:
* DOS grid conversion:
* zero tolerance conversion:
* broadening width conversion:
* unsupported units:

## 10. Density Jacobian

* formula:
* total DOS:
* projected DOS:
* integral before:
* integral after:
* relative error:
* invariance result:

## 11. Imaginary / Zero Policy

* encoding:
* negative values:
* zero tolerance:
* near-zero:
* band imaginary count:
* DOS imaginary integral:
* shared zero line:
* mismatch behavior:

## 12. NAC / ASR

* band NAC:
* DOS NAC:
* Gamma direction:
* compatibility:
* ASR metadata:
* mismatch policy:

## 13. DOS Normalization

* normalization:
* density unit:
* expected modes:
* observed integral:
* tolerance:
* normalization status:
* invalid behavior:

## 14. Shared Frequency Axis

* axis orientation:
* canonical unit:
* band range:
* DOS range:
* display range:
* domain policy:
* manual view:
* zero alignment:
* resize behavior:

## 15. Band Panel

* q-path:
* segments:
* shared endpoints:
* discontinuities:
* labels:
* branch order:
* imaginary branches:
* interpolation:

## 16. DOS Panel

* orientation:
* total DOS:
* projected DOS:
* density unit:
* normalization:
* negative region:
* broadening:
* resampling:
* smoothing:

## 17. Projection Policy

* default:
* atom projections:
* species projections:
* visible cap:
* ordering:
* completeness:
* partial projections:
* aggregation:
* mismatch behavior:

## 18. Layout

* desktop:
* panel ratio:
* shared scale:
* mobile:
* stacked/tabbed:
* orientation changes:
* scroll behavior:
* chart count:

## 19. Combined Artifacts

* combined artifact:
* summary:
* compatibility report:
* plot:
* table:
* manifest:
* source references:
* hashes:
* provenance:
* security:

## 20. Planner / Validator

* discovery:
* combined request routing:
* band-only routing:
* DOS-only routing:
* eigenvector rejection:
* animation rejection:
* calculation rejection:
* artifact validation:
* projection validation:
* domain validation:
* layout validation:

## 21. API Evidence

* compatible pair:
* convertible pair:
* meV pair:
* imaginary pair:
* projected pair:
* structure mismatch:
* atom order mismatch:
* lineage mismatch:
* force constants mismatch:
* NAC mismatch:
* invalid normalization:
* over-cap:
* artifact retrieval:
* partial artifacts:

## 22. Frontend Product

* title:
* compatibility status:
* structure summary:
* source summary:
* combined plot:
* projection selector:
* compatibility report:
* band data:
* DOS data:
* JSON:
* warnings:
* downloads:
* export:

## 23. Accessibility

* region:
* band panel:
* DOS panel:
* shared-axis summary:
* imaginary explanation:
* selector:
* keyboard:
* focus:
* screen reader:
* 200% zoom:
* mobile semantics:

## 24. Browser Evidence

* Chromium:
* Firefox:
* WebKit:
* mobile Chromium:
* mobile WebKit:
* shared axis:
* zero alignment:
* discontinuities:
* negative region:
* projections:
* console:
* network:

## 25. Performance

* band values:
* DOS values:
* projection count:
* visible projections:
* combined plotted values:
* chart/path count:
* interactive:
* degraded:
* refused:
* render trend:
* memory proxy:
* resize:
* selector switching:

## 26. Determinism

* input role order:
* compatibility check order:
* error order:
* warning order:
* unit conversion:
* frequency domain:
* projection order:
* panel order:
* manifest order:
* hashes:

## 27. Security

* artifact JS:
* HTML:
* SVG script:
* callbacks:
* layout expressions:
* unit expressions:
* external assets:
* remote fonts:
* artifact-controlled caps:
* metadata:
* private paths:
* secrets:
* network:
* markers:

## 28. Evidence

* directory:
* schemas:
* compatibility:
* identity:
* lineage:
* conversions:
* Jacobian:
* NAC:
* normalization:
* shared axis:
* projections:
* layout:
* performance:
* API:
* browser:
* accessibility:
* security:
* screenshots:
* hashes:

## 29. Tests

* schemas:
* artifact refs:
* hashes:
* compatibility:
* structure:
* atom ordering:
* cell lineage:
* source lineage:
* force constants:
* units:
* Jacobian:
* integral:
* imaginary:
* zero tolerance:
* NAC:
* normalization:
* projections:
* domain:
* plot:
* summary:
* manifest:
* export:
* registry:
* planner:
* PlanValidator:
* runtime:
* API:
* frontend:
* accessibility:
* mobile:
* Chromium:
* Firefox:
* WebKit:
* performance:
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
* static viewer:
* trajectory viewer:
* service-backed:
* no-skipped:
* lock:
* diff:

## 30. Files

* combined models:
* schemas:
* compatibility validator:
* composer:
* unit conversion integration:
* plot producer:
* summary:
* report:
* manifest:
* registry:
* planner:
* PlanValidator:
* runtime/API:
* frontend:
* fixtures:
* tests:
* browser runners:
* evidence:
* docs:
* persistent:
* CI:
* dependencies/lockfile:

## 31. Deferred

明确列出：

* phonon eigenvector contract
* eigenvector source adapters
* q-point / branch mode binding
* complex eigenvector phase
* mass weighting
* eigenvector normalization
* displacement reconstruction
* phonon animation
* mode amplitude controls
* phase controls
* LO-TO directional animation
* Raman / IR activity
* neutron scattering
* thermal properties
* official benchmark validation
* dynamic phonon product registration

## 32. Readiness

* combined schema:
* compatibility:
* structure identity:
* atom order:
* lineage:
* unit conversion:
* Jacobian:
* imaginary policy:
* NAC:
* normalization:
* shared axis:
* band panel:
* DOS panel:
* projections:
* summary:
* API:
* registry:
* planner:
* frontend:
* browser:
* mobile:
* accessibility:
* performance:
* security:
* Combined Band + DOS:
* eigenvectors:
* animation:

## 33. Commit / CI

* commit:
* HEAD:
* CI run:
* backend:
* frontend:
* typecheck:
* build:
* compatibility:
* conversions:
* API:
* browser:
* accessibility:
* mobile:
* Phase 10 closure:
* Phase 10G:
* Phase 10H:
* Phase 10H-1:
* Phase 10H-2:
* static viewer:
* trajectory viewer:
* service-backed:
* no-skipped:
* origin:
* status:

## 34. Whether allowed to enter next phase

允许 / 不允许

下一阶段：

```text
Phase 10H-4：Phonon Eigenvector Contract
```

下一阶段只定义：

* phonon mode identity
* q-point / branch binding
* atom ordering
* complex eigenvector representation
* real / imaginary components
* normalization
* mass weighting
* phase convention
* degeneracy handling
* displacement reconstruction
* amplitude semantics
* units
* caps
* deterministic serialization
* security

下一阶段不得直接实现phonon animation。

---

# 69. PASS 判定

PASS必须满足：

* 有真实combined schema
* 有真实combined summary schema
* 有真实compatibility report schema
* 有真实combined plot contract
* 有真实manifest
* artifact reference和hash验证完成
* band和DOS分别经过独立validator
* compatibility validator真实执行
* compatibility states明确
* check order稳定
* structure identity严格一致
* atom count严格一致
* species ordering逐index一致
* primitive / supercell lineage有明确policy
* source calculation lineage有明确policy
* force constants mismatch不会被忽略
* frequency units相同或严格可转换
* DOS frequency转换时正确应用density Jacobian
* total和projected DOS全部同步转换
* broadening width同步转换
* conversion前后DOS积分保持
* imaginary encoding一致
* zero tolerance一致
* NAC status一致
* Gamma direction兼容
* DOS normalization有效
* incompatible pair被拒绝
* incompatible时不生成partial combined success artifacts
* compatible pair生成combined artifacts
* shared frequency axis真实工作
* band和DOS使用同一frequency domain
* zero line严格对齐
* negative-frequency区域一致
* band discontinuities未连接
* DOS使用horizontal density / vertical frequency
* projected DOS selector受cap约束
* projection identity严格
* partial projection不会被表示成complete
* combined summary正确
* compatibility report正确
* manifest source refs和hash正确
* registry真实注册
* planner combined routing正确
* band-only routing不回退
* DOS-only routing不回退
* PlanValidator不放宽
* service-backed API路径闭合
* frontend真实combined product可用
* accessibility不回退
* mobile stacked/tabbed可用
* Chromium完整证据通过
* Firefox/WebKit/mobile完成或如实记录
* performance tier工作
* deterministic replay稳定
* no artifact JS
* no HTML/SVG script
* no external network
* no secret hits
* Phase 10 Closure不回退
* Phase 10G不回退
* Phase 10H contract不回退
* Phase 10H-1不回退
* Phase 10H-2不回退
* static viewer不回退
* trajectory viewer不回退
* tests通过
* CI通过
* origin/master等于HEAD
* git status clean

PARTIAL_PASS仅允许：

* projected DOS selector只支持atom或species其中一种，但total DOS combined完整
* source lineage缺失非关键metadata时，按Phase 10H已批准warning policy处理
* SVG export明确DEFERRED_BY_DESIGN，但PNG/JSON和combined product完整
* mobile采用tabs而非side-by-side，但共享domain和语义一致
* 某非主要browser环境明确unavailable，且测试保留、主链路完整
* npm audit因既有registry问题不可用

FAIL包括：

* 只是将两个已有plot视觉并排
* 无combined schema
* 无compatibility validator
* frontend自行判断compatibility
* structure mismatch仍生成combined view
* atom order mismatch仍生成combined view
* cell lineage mismatch被忽略
* force constants mismatch被忽略
* NAC mismatch仍生成combined view
* frequency unit不同只改label
* DOS转换遗漏density Jacobian
* projected DOS转换遗漏Jacobian
* broadening width未转换
* DOS积分不保持
* zero tolerance差异被静默忽略
* band和DOS使用不同frequency domain
* zero line不对齐
* negative region被裁剪
* discontinuous band segments被连接
* DOS仍使用standalone orientation而声称共享axis
* projection无cap
* incomplete projection被当成complete
* incompatible时生成partial artifacts
* 无正式API evidence
* 无browser evidence
* accessibility回退
* 提前实现eigenvector或animation造成范围膨胀
* Phase 10H-2回退
* CI失败却声明PASS

---END---

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
