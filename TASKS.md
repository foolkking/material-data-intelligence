---TASK---
状态：已完成

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
## 完成记录

* 完成时间：2026-07-13 11:25 +08:00
* 修改文件：supercell validation/estimator/state、controls、renderer engine/surface/types、measurement provenance、tests、browser runners、Phase 10F-24 evidence/docs和persistent记录。
* 修改摘要：实现strict [a,b,c] draft/apply/reset/presets、positive-octant deterministic instances、canonical periodic bond replication、独立unit-cell/outer-boundary、interactive/degraded/refused preflight、inert phase10f24.viewer_supercell_state.v1 replay，以及single-context GPU buffer replacement；未修改canonical scene、backend runtime或Tool Registry。
* 测试结果：frontend 94 passed；backend 366 passed, 21 skipped, 11 warnings（首次并行运行因残留SQLite测试临时文件锁失败，清理workspace内.pytest_tmp后独立重跑通过）；typecheck/build/uv lock/git diff通过；全部10个viewer browser runners通过；Chromium 150、Firefox 128、WebKit 18及mobile通过；60次总supercell lifecycle cycles无context leak；NO_EXTERNAL_NETWORK_REQUESTS；NO_SECRET_PATTERN_HITS；npm audit因npmmirror endpoint NOT_IMPLEMENTED不可用；GitHub Actions run 29221567076（SHA 61978b1210b27d5ec03368aeac274c73dd50aadd）的unit、frontend typecheck/build、service-backed integration和no-skipped assertion全部成功。
---END---

---TASK---
状态：待处理
 # Phase 10F-25：Clipping, Cell and Camera Controls

进入 Phase 10F-25：Clipping, Cell and Camera Controls。

可以默认：

* Phase 10F-24 已完成
* supercell productization 已完成
* supercell expansion、instance generation、bond replication、deduplication、persistence、picking、measurement 已完成
* Phase 10F-23 advanced picking and measurement 已完成
* Phase 10F-22 accessibility、mobile、cross-browser 已完成
* Phase 10F-21 performance budgets、instancing、bond batching、lifecycle 已完成
* current production scene schema 仍为 `phase10f18.viewer_scene.v2`
* current manifest仍为当前 v2 manifest
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
* measurement
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
* camera preset
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
* export
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
```

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
```

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
```

确认：

* 是否已有Three.js clipping能力
* material共享策略
* shader修改风险
* GPU lifecycle

---

# 5. 修改前审计输出

输出：

# Phase 10F-25 Pre-Implementation Audit

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

* clipping cost
* extra draw calls
* extra geometry
* camera animation cost
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

# 6. Clipping Contract

建立：

```ts
type ViewerClipState = {
  enabled: boolean;
  planes: ClipPlane[];
};
```

推荐：

```ts
type ClipPlane = {
  axis: "x" | "y" | "z";
  position: number;
  enabled: boolean;
};
```

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
* boolean geometry cut
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
* position slider/input
* reset

要求：

* keyboard accessible
* mobile usable
* numeric input验证
* slider bounded
* live region提示一次

显示：

例如：

```text
Clipping X enabled at 4.2 Å
```

---

# 10. Clipping Caps

必须限制：

* maximum active planes

推荐：

```text
max active clipping planes = 3
```

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

```text
A' = aA
B' = bB
C' = cC
```

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
* disabled by default

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

```
a vector length: 5.43 Å
b vector length: 5.43 Å
c vector length: 5.43 Å
```

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
```

要求：

* deterministic
* bounded
* keyboard accessible
* mobile accessible

每个preset定义：

* position
* target
* up vector

不得：

* 自动随机旋转
* 无限动画

---

# 14. Camera State Contract

可选保存：

```json
{
 "schema_version":"phase10f25.camera_state.v1",
 "preset":"isometric",
 "position":[1,2,3],
 "target":[0,0,0],
 "zoom":1
}
```

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

```
siteIndex@[imageOffset]
```

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
* camera preset

例如：

```
Clipping enabled. X plane at 3.5 angstrom.
Camera preset: top.
```

不得：

* 只靠视觉

---

# 20. Mobile

测试：

* slider
* numeric input
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
* canvas count

---

# 22. Tests

必须覆盖：

## Clipping

* enable
* disable
* x/y/z
* multiple planes
* reset
* invalid values

## Cell

* unit cell
* supercell
* triclinic
* hide/show

## Camera

* presets
* reset
* serialization
* invalid state

## Integration

* clipping + picking
* clipping + measurement
* clipping + supercell
* mobile
* lifecycle

---

# 23. Evidence

新增：

```
docs/phase10f/evidence/phase10f25_clipping_cell_camera/
```

包含：

```
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
```

截图：

```
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
```

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
* no secret

输出：

```
NO_EXTERNAL_NETWORK_REQUESTS
NO_SECRET_PATTERN_HITS
```

---

# 25. Docs

新增：

```
docs/phase10f/phase10f25_clipping_cell_camera.md
docs/phase10f/phase10f25_clipping_contract.md
docs/phase10f/phase10f25_camera_contract.md
docs/phase10f/phase10f25_cell_display_contract.md
docs/phase10f/phase10f25_security.md
docs/phase10f/phase10f25_evidence.md
```

更新：

```
persistent/DESIGN_PROGRESS.md
persistent/TASK_BOARD.md
persistent/CHANGELOG.md
persistent/ARCHITECTURE_DECISIONS.md
```

---

# 26. Readiness Matrix

最终输出：

```
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
```

---

# 27. Checks

运行：

```bash
git diff --check
uv lock --check

npm --prefix apps/web test
npm --prefix apps/web run typecheck
npm --prefix apps/web run build

uv run python -m pytest -q
```

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

# 28. Commit

完成：

```bash
git status --short
git add <Phase 10F-25 files>
git commit -m "Add viewer clipping cell and camera controls"
git push origin master
```

确认：

* CI success
* origin/master matches
* clean tree

---

# 29. 最终报告

输出：

# Phase 10F-25 Clipping, Cell and Camera Controls Result

包括：

1. Conclusion
2. Baseline
3. Clipping contract
4. Cell display
5. Supercell integration
6. Camera presets
7. Persistence
8. Picking
9. Measurement
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

```
Phase 10F-26：Scientific Export and Reporting Foundation
```

不要进入trajectory、phonon、Brillouin zone或volumetric。

---END---


---TASK---
 状态：待处理
 # Phase 10F-26：Scientific Export and Reporting Foundation

进入 Phase 10F-26：Scientific Export and Reporting Foundation。

可以默认：

* Phase 10F-25 已完成
* clipping、cell display、supercell boundary、camera presets 和 camera state 已完成
* Phase 10F-24 supercell productization 已完成
* Phase 10F-23 picking and measurement 已完成
* Phase 10F-22 accessibility、mobile、cross-browser 已完成
* Phase 10F-21 performance hardening 已完成
* current production scene schema 仍为 `phase10f18.viewer_scene.v2`
* current manifest仍为当前 v2 manifest
* periodic identity、canonical bonds、measurement、supercell、clipping 和 camera controls均保持稳定
* 当前 branch、HEAD、working tree 和 Phase 10F-25 CI 可视为正确且 clean

本阶段不需要重复 baseline 检查。

本阶段主要目标：

> 为当前 periodic crystal viewer 建立安全、确定性、可复现的科学导出和报告基础，使用户可以导出视图、状态、测量结果和结构化报告，同时不允许 artifact 执行代码或加载外部资源。

本阶段重点包括：

* deterministic PNG export
* high-DPI screenshot
* transparent/solid background
* camera-consistent export
* clipping/supercell state capture
* measurement overlay capture
* JSON state export
* manifest export
* Markdown scientific summary
* PDF readiness assessment
* export artifact contracts
* export accessibility
* browser evidence
* security closure

本阶段仍不是 trajectory、phonon、Brillouin zone 或 volumetric phase。

---

# 1. 当前已知能力

当前 viewer 已具备：

* validated `viewer_scene.v2`
* periodic site identity
* canonical bonds
* cross-boundary and self-periodic topology
* picking
* distance / angle / dihedral measurement
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

* PNG export
* high-resolution export
* deterministic export dimensions
* transparent background export
* export with/without overlays
* export with current camera
* export with saved camera preset
* export with clipping/supercell state
* measurement result packaging
* scientific summary artifact
* export manifest
* export recipe
* PDF export readiness
* browser export evidence
* export security audit

---

# 2. 本阶段目标

必须完成以下八类工作：

1. Export architecture audit
2. Deterministic render capture
3. PNG and image export
4. JSON state and measurement export
5. Scientific summary/report artifact
6. Export provenance and manifest
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
* canonical structure export，除非已有安全、明确contract
* glTF/GLB export
* arbitrary 3D format export
* video export
* animation export
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
* manifest
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
```

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
```

确认：

* current artifact download helpers
* filename sanitization
* MIME policy
* object URL cleanup
* existing JSON/Markdown artifact patterns
* security metadata conventions

## 4.3 Measurement and Viewer State

确认：

* measurement artifact
* supercell state artifact
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

# Phase 10F-26 Scientific Export Pre-Implementation Audit

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
* stale scene export
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
* persistent

审计后直接继续实现。

---

# 6. Export Contract

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
```

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
```

---

# 7. Export Size and Resource Caps

必须定义：

* minimum width
* maximum width
* minimum height
* maximum height
* max total pixels
* max pixel ratio
* max estimated memory
* max concurrent export jobs

建议：

```text
min width/height: 256
max width/height: 4096
max total pixels: 16,777,216
max pixel ratio: 2
max concurrent export: 1
```

具体数值应结合真实代码和浏览器测试调整。

必须在 allocation 前检查。

Typed errors：

```text
VIEWER_EXPORT_INVALID_SIZE
VIEWER_EXPORT_PIXEL_BUDGET_EXCEEDED
VIEWER_EXPORT_BUSY
VIEWER_EXPORT_SCENE_UNAVAILABLE
VIEWER_EXPORT_CONTEXT_LOST
VIEWER_EXPORT_FAILED
```

---

# 8. PNG Export

## 8.1 Deterministic Capture

导出必须使用当前 validated scene 和 applied viewer state。

必须捕获：

* camera
* target
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

```text
preserveDrawingBuffer: true
```

如果必须使用，需证明性能影响可接受。

## 8.3 Deterministic Camera

导出使用：

* current camera state
* 或 selected camera preset

必须明确。

导出前不自动改变用户camera。

## 8.4 Background

支持：

* transparent
* light
* dark

background由应用定义。

不得由artifact提供任意CSS或shader。

## 8.5 High-DPI

支持 bounded high-DPI。

必须：

* 先检查pixel budget
* 不使用设备真实DPR作为无上限输入
* mobile默认更保守
* 导出后恢复renderer state

---

# 9. Overlay Export

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
* 让export改变measurement
* 让export改变scene

---

# 10. JSON Export

至少生成：

```text
viewer_export_state.json
```

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
```

要求：

* deterministic key ordering
* no NaN/Infinity
* no renderer objects
* no raw Three.js matrix unless normalized
* no local path
* no URL
* no callback
* no HTML
* no executable content

---

# 11. Scientific Markdown Summary

生成：

```text
viewer_export_summary.md
```

至少包含：

* formula
* scene schema
* lattice summary
* canonical site count
* canonical bond count
* cross-boundary bond count
* self-periodic bond count
* supercell expansion
* displayed atom count
* displayed bond count
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

# 12. Export Manifest

新增：

```text
viewer_export_manifest.json
```

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
```

要求：

* exact allowlist
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

```text
viewer.png
viewer_export_state.json
viewer_export_summary.md
viewer_export_manifest.json
```

可允许安全前缀：

```text
<sanitized_formula>_viewer.png
```

必须：

* strip path separators
* strip control chars
* bound length
* normalized Unicode
* fallback name
* no user-provided extension

不得允许：

```text
../../secret
C:\...
file://
http://
```

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
* focus management
* live-region announcements
* no color-only status
* export during busy state disabled
* invalid size blocked before allocation

建议预设：

```text
Web 1200×900
Presentation 1600×900
Square 1600×1600
Publication 2400×1800
```

所有preset必须经过caps。

---

# 15. Accessibility

必须保持Phase 10F-22标准。

必须可读：

* selected format
* dimensions
* estimated pixels
* background
* included overlays
* progress
* success
* failure
* downloaded filename

Live region：

```text
Export started.
Export completed: viewer.png.
Export failed: image size exceeds safe limit.
```

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
* download result
* orientation change
* repeated export
* over-budget rejection

要求：

* mobile使用更保守默认尺寸
* 导出期间不冻结UI
* 不创建重复canvas/context
* export完成后资源释放
* download失败时提供明确fallback

---

# 17. Lifecycle

必须处理：

* export start
* export cancel
* scene switch
* artifact switch
* camera change
* clipping change
* supercell change
* context loss
* component unmount
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

```text
PDF export: DEFERRED_BY_DESIGN
```

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
* deterministic layout
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
* canvas count
* context count
* memory proxy before/after

必须验证：

* repeated export no monotonic growth
* 10次bounded repeated export
* over-budget rejected before allocation
* export不改变interactive renderer性能
* no continuous loop

不得用严格毫秒值作为唯一PASS依据。

---

# 20. Security

必须验证：

* no artifact JS
* no HTML execution
* no SVG script
* no remote image
* no remote font
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

```text
NO_EXTERNAL_NETWORK_REQUESTS
NO_SECRET_PATTERN_HITS
```

---

# 21. Tests

## 21.1 Export Contract Tests

覆盖：

* valid PNG
* valid JSON
* valid Markdown
* invalid format
* invalid dimensions
* pixel budget
* pixel ratio
* background
* unknown fields

## 21.2 PNG Tests

覆盖：

* default
* transparent
* dark
* high-DPI
* camera preset
* clipping
* supercell
* measurement overlay
* no inspector UI
* deterministic dimensions
* repeated export

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
* no HTML/script

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

* scene switch during export
* context loss
* unmount
* repeated export
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
* measurement
* supercell
* clipping
* camera
* compatibility
* no external network
* no artifact JS

---

# 22. Browser Evidence

新增：

```text
docs/phase10f/evidence/phase10f26_scientific_export/
```

必须使用真实浏览器。

## Chromium

覆盖：

* PNG default
* transparent PNG
* high-DPI
* supercell
* clipping
* measurement overlays
* JSON
* Markdown
* manifest
* repeated export
* stale export cancellation

## Firefox

至少覆盖：

* PNG
* JSON
* clipping
* repeated export
* download handling

## WebKit

至少覆盖：

* PNG
* transparent background
* measurement overlay
* JSON
* lifecycle

## Mobile

至少覆盖：

* export panel
* preset
* PNG
* JSON
* over-budget rejection
* repeated export
* orientation change

---

# 23. Evidence Assertions

每个browser evidence记录：

* browser version
* viewport
* scene
* viewer state
* format
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

* image dimensions exact
* camera state exact
* clipping state exact
* supercell state exact
* measurement values exact
* manifest hashes exact
* no external network
* no executable assets
* repeated export no leak
* stale export rejected

---

# 24. Evidence Files

至少包含：

```text
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
```

截图或导出样例：

```text
01_default_viewer.png
02_transparent_background.png
03_dark_background.png
04_supercell_export.png
05_clipping_export.png
06_measurement_export.png
07_mobile_export_panel.png
08_export_success.png
```

不要保存：

* browser cache
* private paths
* token
* debug dump
* remote asset
* giant images beyond caps
* object URLs
* crash dumps

---

# 25. Docs / Persistent

新增或更新：

```text
docs/phase10f/phase10f26_scientific_export.md
docs/phase10f/phase10f26_export_contract.md
docs/phase10f/phase10f26_png_export.md
docs/phase10f/phase10f26_export_manifest.md
docs/phase10f/phase10f26_export_security.md
docs/phase10f/phase10f26_pdf_readiness.md
docs/phase10f/phase10f26_export_evidence.md
docs/phase10f/phase10f26_export_readiness_matrix.md
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

* export contract
* size caps
* PNG strategy
* high-DPI policy
* background policy
* camera consistency
* clipping/supercell consistency
* measurement overlay policy
* JSON schema
* Markdown summary
* manifest
* security
* PDF deferred/ready decision
* remaining formal viewer registration work

---

# 26. Readiness Matrix

最终分别判断：

* export request contract
* filename policy
* PNG export
* transparent background
* dark/light background
* high-DPI
* current camera capture
* camera preset capture
* clipping capture
* supercell capture
* measurement overlay
* JSON state export
* Markdown summary
* manifest
* deterministic hashes
* lifecycle
* repeated export
* accessibility
* mobile
* Chromium
* Firefox
* WebKit
* security
* PDF export
* full `structure.viewer_3d`
* trajectory
* phonon
* Brillouin zone
* volumetric

推荐期望：

```text
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
```

---

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
* network audit

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
git status --short
git diff --stat
git add <only Phase 10F-26 related files>
git commit -m "Add scientific viewer export foundation"
git push origin master
```

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

# Phase 10F-26 Scientific Export and Reporting Foundation Result

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

## 4. Export Contract

* schema:
* formats:
* dimensions:
* pixel ratio:
* backgrounds:
* overlays:
* caps:

## 5. PNG Export

* default:
* transparent:
* dark/light:
* high-DPI:
* dimensions:
* camera:
* clipping:
* supercell:
* measurements:

## 6. JSON Export

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

## 8. Manifest

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

* true vector SVG export
* PDF export，若未实现
* glTF/GLB
* video/animation export
* structure file export
* collaboration/share links
* formal `structure.viewer_3d`
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

```text
Phase 10F-27：Formal structure.viewer_3d Registration and Product Evidence
```

不要进入 trajectory、phonon、Brillouin zone 或 volumetric。

---

# 30. PASS 判定

PASS必须满足：

* 有真实PNG export
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
* MIME allowlist
* no path traversal
* no executable asset
* no external asset
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

---END---

---TASK---
 状态：待处理
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

-   current production scene schema 仍为 `phase10f18.viewer_scene.v2`

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

-   `viewer_scene.v2`

-   canonical lattice

-   canonical sites

-   periodic image identity

-   canonical periodic bonds

-   same-cell bonds

-   cross-boundary bonds

-   self-periodic bonds

-   triclinic support

-   neighbor inspector

-   performance budgets

-   large-scene degraded/refused policy

-   accessibility

-   mobile

-   atom/bond picking

-   distance/angle/dihedral measurement

-   supercell

-   clipping

-   cell controls

-   camera presets

-   scientific export

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

-   将legacy Phase 10D schema标记成current

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

-   frontend entry point

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

```

确认：

-   registry schema

-   tool metadata

-   input contract

-   output contract

-   capability metadata

-   registration mechanism

-   discovery endpoint

-   planner integration

-   validation


## 4.2 Planner

搜索：

```bash
rg -n "planner|available tools|tool selection|tool routing|PlanValidator|AnalysisPlan" backend apps tests

```

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

-   mobile layout

-   legacy compatibility handling


## 4.5 Existing Viewer Tools

搜索所有：

```text
structure.viewer_scene_metadata
structure.viewer_export_package
phase10d viewer tools
phase10f viewer adapters

```

必须审计是否存在：

-   duplicate tools

-   overlapping tools

-   deprecated tools

-   hidden aliases

-   conflicting output schemas


----------

# 5. 修改前输出审计

修改代码前输出：

# Phase 10F-27 Formal Viewer Registration Pre-Implementation Audit

## 1. Current Viewer Tool Inventory

对每个viewer-related tool列出：

-   tool ID

-   registry status

-   producer

-   input

-   output

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

-   capability drift

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

-   input contract

-   output contract

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

-   persistent


审计完成后直接继续实现。

----------

# 6. Formal Tool ID

正式注册：

```text
structure.viewer_3d

```

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

```

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

# 8. Input Contract

必须明确正式input。

至少支持：

-   valid periodic crystal structure

-   lattice

-   fractional coordinates

-   species

-   optional canonical bond source，若adapter contract允许

-   deterministic viewer options，若正式支持


必须拒绝或typed fallback：

-   molecule without lattice，除非已有独立nonperiodic contract

-   trajectory

-   phonon data

-   volumetric grid

-   malformed lattice

-   nonfinite coordinates

-   over-cap site count

-   arbitrary renderer config

-   executable payload

-   external URLs


typed codes建议：

```text
STRUCTURE_VIEWER_3D_INPUT_INVALID
STRUCTURE_VIEWER_3D_LATTICE_REQUIRED
STRUCTURE_VIEWER_3D_SITE_LIMIT_EXCEEDED
STRUCTURE_VIEWER_3D_UNSUPPORTED_DATA_KIND
STRUCTURE_VIEWER_3D_RENDER_BUDGET_EXCEEDED

```

----------

# 9. Output Contract

正式输出必须以：

```text
phase10f18.viewer_scene.v2

```

为current scene contract。

同时输出current manifest。

至少包含：

-   scene

-   manifest

-   recipe

-   validation output

-   optional export artifacts

-   summary


不得默认生成：

-   Phase 10D legacy schema

-   canonical v1

-   renderer bundle

-   JavaScript

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

-   validated input

-   validated output

-   no network

-   no external resources

-   no artifact JS

-   no hidden renderer bundle

-   current v2 output

-   exact capabilities

-   stable warnings

-   sanitized errors


必须证明：

```text
input
→ adapter
→ viewer_scene.v2
→ manifest
→ validator
→ artifact store
→ frontend renderer

```

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

-   internal implementation backing `structure.viewer_3d`

-   hidden fromplanner catalog

-   not separately user-facing

-   no duplicate formal registration


必须避免：

-   planner看到多个近似viewer tools

-   用户不知道该选哪个

-   一个输出v1、一个输出v2

-   capability冲突


最终只应有一个正式用户可发现ID：

```text
structure.viewer_3d

```

----------

# 12. Planner Registration

必须将 `structure.viewer_3d` 加入 planner tool catalog。

Planner描述必须准确：

适合：

-   periodic crystal visualization

-   bond topology inspection

-   supercell display

-   measurement

-   static viewer export


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

-   no executable artifact request

-   no external resource request

-   no over-cap options

-   no arbitrary renderer config


不得放宽PlanValidator。

如果planner请求：

```text
trajectory=true

```

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

-   validation result

-   failure result


复用现有API，不建议新增重复route。

API evidence必须通过正式路径：

```text
POST planner/job or equivalent
→ registered tool
→ service-backed execution
→ artifacts

```

不得：

-   直接调用adapter函数伪造API evidence

-   仅测试fixture endpoint

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


## Over-Budget

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

-   显示 `3D Structure Viewer`

-   显示tool ID或合理用户名称

-   支持planner result打开

-   支持renderer

-   支持JSON-only fallback

-   支持inspector

-   支持measurement

-   支持supercell

-   支持clipping/camera

-   支持export

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

-   site count

-   lattice

-   canonical bond count

-   cross-boundary bond count

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

-   over-budget

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

# 19. Formal Capability Contract

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

```

必须与真实implementation一致。

若Phase 10F-26某项是PARTIAL_READY或DEFERRED：

-   这里不得写true

-   或使用更准确状态模型


禁止简单boolean过度宣称。

----------

# 20. Evidence Package

新增：

```text
docs/phase10f/evidence/phase10f27_structure_viewer_3d_product/

```

至少包含：

```text
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

```

截图建议：

```text
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

```

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

-   measurement

-   supercell

-   clipping

-   export

-   degraded mode

-   over-budget fallback

-   context loss

-   reload/reopen artifact


## Firefox

至少覆盖：

-   planner→job→result

-   periodic render

-   measurement

-   export

-   fallback


## WebKit

至少覆盖：

-   planner→job→result

-   render

-   mobile-like interaction

-   export

-   fallback


## Mobile

至少覆盖：

-   tool discovery或result entry

-   renderer

-   controls

-   measurement

-   supercell

-   export

-   degraded/refused state


----------

# 22. Browser Evidence Assertions

每个case记录：

-   browser version

-   viewport

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

-   canvas count

-   context count


必须验证：

-   formal tool ID shown

-   planner selects correct tool

-   job executes registered adapter

-   output is v2

-   no legacy default output

-   renderer loads

-   fallback works

-   no external network

-   no artifact JS

-   no duplicate canvas/context

-   no capability overclaim


----------

# 23. API Evidence Assertions

必须记录：

-   request

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

-   frontend使用真实artifact


----------

# 24. Tests

## 24.1 Registry Tests

覆盖：

-   `structure.viewer_3d` registered

-   exactly once

-   metadata exact

-   current schema exact

-   capabilities exact

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

-   over-budget

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

-   over-budget

-   invalid

-   export

-   accessibility

-   mobile


## 24.7 Regression

必须保持：

-   Phase 10F-18 periodic topology

-   Phase 10F-19 integration

-   Phase 10F-20 compatibility

-   Phase 10F-21 performance

-   Phase 10F-22 accessibility

-   Phase 10F-23 picking/measurement

-   Phase 10F-24 supercell

-   Phase 10F-25 clipping/camera

-   Phase 10F-26 export

-   no external network

-   no artifact JS


----------

# 25. Security

必须验证：

-   no artifact JavaScript

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

-   no legacy schema masquerading as current

-   no private path

-   no token

-   no secret

-   no telemetry upload


必须输出：

```text
NO_EXTERNAL_NETWORK_REQUESTS
NO_SECRET_PATTERN_HITS

```

----------

# 26. Documentation

新增或更新：

```text
docs/phase10f/phase10f27_structure_viewer_3d_registration.md
docs/phase10f/phase10f27_structure_viewer_3d_tool_contract.md
docs/phase10f/phase10f27_structure_viewer_3d_capabilities.md
docs/phase10f/phase10f27_structure_viewer_3d_planner_routing.md
docs/phase10f/phase10f27_structure_viewer_3d_api_evidence.md
docs/phase10f/phase10f27_structure_viewer_3d_browser_evidence.md
docs/phase10f/phase10f27_structure_viewer_3d_security.md
docs/phase10f/phase10f27_structure_viewer_3d_readiness_matrix.md

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

-   manifest

-   frontend product entry

-   renderer

-   JSON fallback

-   picking

-   measurement

-   supercell

-   clipping

-   camera

-   export

-   accessibility

-   mobile

-   performance

-   Chromium

-   Firefox

-   WebKit

-   security

-   legacy deprecation

-   full `structure.viewer_3d`

-   trajectory

-   phonon

-   Brillouin zone

-   volumetric

-   editing


推荐期望：

```text
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

```

只有本阶段全部闭环后，才允许首次将：

```text
full structure.viewer_3d: READY

```

----------

# 28. Checks

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

-   network audit


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
git status --short
git diff --stat
git add <only Phase 10F-27 related files>
git commit -m "Register structure viewer 3D product"
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

# 30. 最终报告格式

输出：

# Phase 10F-27 Formal `structure.viewer_3d` Registration and Product Evidence Result

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


## 4. Capability Contract

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

```text
Phase 10G：Brillouin Zone Planning and Contract

```

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

-   legacy不再作为正式production default

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

-   `full structure.viewer_3d: READY`


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
---END---

---TASK---
 状态：待处理
 # Phase 10 Closure Regression Pack

进入 Phase 10 Closure Regression Pack。

可以默认：

-   Phase 10A 至 Phase 10F-27 已按各阶段结论完成

-   `structure.viewer_3d` 已正式注册

-   Phase 10F 系列已完成产品化收口

-   current production viewer scene schema 为 `phase10f18.viewer_scene.v2`

-   current production manifest 为正式 v2 manifest

-   legacy Phase 10D viewer schema仅保留read-only / JSON-only compatibility

-   canonical v1仅保留same-cell legacy compatibility

-   v2为current periodic topology renderer contract

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

-   新export format

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

-   将legacy schema升级成current

-   复制数千行已有测试

-   把已有单元测试简单重命名为closure test

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
find tests -maxdepth 4 -type f | sort
rg -n "phase10|viewer_3d|viewer_scene|ToolRegistry|PlanValidator|planner|artifact|manifest" tests backend packages

```

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
find apps/web -type f \( -name "*.test.ts" -o -name "*.test.tsx" -o -name "*.spec.ts" \) | sort
rg -n "viewer_3d|viewer_scene|measurement|supercell|clipping|export|accessibility|fallback" apps/web

```

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
find . -type f \( -iname "*playwright*" -o -iname "*browser*" -o -iname "*e2e*" \) | sort

```

确认：

-   Chromium runner

-   Firefox runner

-   WebKit runner

-   mobile runner

-   formal product-path evidence runner

-   download handling

-   network audit

-   console audit


## 4.4 CI

搜索：

```bash
find .github -type f -maxdepth 4 -print
rg -n "pytest|npm test|typecheck|build|playwright|integration|no.*skipped" .github scripts pyproject.toml package.json apps/web/package.json

```

确认：

-   当前CI入口

-   哪些测试已经自动运行

-   哪些测试只在本地运行

-   哪些browser tests有独立job

-   closure pack最合适的接入方式


----------

# 5. 修改前输出审计

修改任何文件前输出：

# Phase 10 Closure Regression Pack Pre-Implementation Audit

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

-   legacy不成为default

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

-   可复用的API client


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

-   persistent


审计后直接继续执行。

----------

# 6. Closure Test Architecture

建议建立三层closure pack。

## 6.1 Backend/Product Integration

建议路径：

```text
tests/integration/test_phase10_product_closure.py
tests/integration/test_phase10_registry_planner_runtime.py
tests/integration/test_phase10_artifact_contracts.py

```

如果仓库已有更合适目录，遵循现有结构。

## 6.2 Frontend Product Composition

建议路径：

```text
apps/web/src/__tests__/phase10ProductClosure.test.tsx

```

或现有测试目录的等价位置。

## 6.3 Browser Product Smoke

建议路径：

```text
apps/web/e2e/phase10-product-closure.spec.ts

```

或当前Playwright目录的等价位置。

不得为了满足文件数量机械创建三个文件。

如果现有架构更适合集中为一个backend文件和一个browser文件，可以调整，但必须覆盖三层语义。

----------

# 7. Cross-Phase Invariant Matrix

新增机器可读或文档化matrix。

至少覆盖：

Invariant

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

Artifact

Inspector

Picking

Canonical bonds稳定

Adapter

Bond validator

Artifact

Renderer

Measurement

Security inert

Producer

Manifest validator

Runtime

Preview

Network audit

Caps生效

Validator

PlanValidator

Runtime

Fallback

Over-budget

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

```text
Tool Registry
→ planner tool catalog
→ PlanValidator
→ service-backed execution runtime
→ adapter
→ scene/manifest generation
→ artifact validation
→ artifact persistence/retrieval

```

至少覆盖一个正式viewer请求：

```text
Show this periodic crystal in 3D and allow bond inspection.

```

不得直接调用adapter函数作为唯一证据。

必须断言：

-   selected tool为`structure.viewer_3d`

-   tool只注册一次

-   plan validation通过

-   runtime调用正式adapter

-   scene schema为v2

-   manifest schema为current v2

-   artifacts inert

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

-   `table.distribution_summary`

-   `viz.scatter`或`viz.histogram`


## Composition

至少一个composition adapter：

-   `composition.summary`

-   或当前正式注册的等价tool


## Lightweight Structure

至少一个：

-   `structure.summary`

-   `structure.lattice_summary`

-   `structure.spacegroup_summary`


## Static Physics

至少一个或两个：

-   `structure.coordination_hist`

-   `structure.xrd`

-   `structure.rdf`


## Viewer

-   `structure.viewer_3d`


要求：

-   不需要重测全部算法细节

-   只验证registry、routing、runtime、artifact、preview基本闭环

-   static physics继续遵守candidate/official PASS语义

-   不得把candidate expected values写成官方认证结果


----------

# 10. Artifact Contract Closure

必须验证Phase 10主要artifact类型。

至少包括：

-   table summary artifact

-   visualization artifact

-   composition artifact

-   structure summary artifact

-   static physics artifact

-   viewer scene v2

-   viewer manifest v2

-   measurement artifact

-   supercell state artifact

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

# 11. Viewer Product Composition Test

必须加入一个高价值组合测试，至少执行：

```text
valid triclinic periodic scene
→ render
→ inspect periodic atom
→ select cross-boundary bond
→ measure distance
→ apply bounded supercell
→ select copied instance
→ apply clipping
→ switch camera preset
→ export viewer state/PNG package

```

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

-   no duplicate canvas/context

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

-   not planner default

-   not current schema


## Canonical v1

断言：

-   supported legacy same-cell only

-   no periodic topology claim

-   no fake image offsets

-   not default producer output


## Current v2

断言：

-   planner/runtime default

-   periodic topology enabled

-   renderer eligible

-   product UI current


必须防止未来代码将legacy重新提升为默认。

----------

# 13. Capability Truth Closure

必须断言正式capability与真实实现一致。

至少检查：

```text
periodic_structure: true
periodic_bonds: true
cross_boundary_bonds: true
picking: true
measurement: true
supercell: true
clipping: true
camera_presets: true

```

export按Phase 10F-26真实结论。

以下必须为false或NOT_READY：

```text
trajectory
phonon
Brillouin zone
volumetric
editing

```

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

## Invalid Input

-   malformed lattice

-   nonfinite coordinates

-   typed sanitized failure

-   no renderer initialization


## Degraded

-   valid artifact

-   degraded warning

-   renderer仍可用

-   scientific data不变


## Over-Budget

-   valid artifact或test-owned synthetic complexity

-   no renderer/canvas/context allocation

-   JSON-only fallback

-   job不被误标为scientific failure


## Context Loss

-   fallback可访问

-   retry/rebuild按现有policy

-   no duplicate canvas/context


## Unsupported Capability

-   typed rejection

-   no silent ignore


----------

# 16. Security Closure

必须加入跨阶段security regression。

断言：

-   no artifact JavaScript

-   no artifact HTML execution

-   no shader payload

-   no module payload

-   no callback payload

-   no external URL

-   no remote texture

-   no remote font

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

```text
NO_EXTERNAL_NETWORK_REQUESTS
NO_SECRET_PATTERN_HITS

```

----------

# 17. Lifecycle Closure

必须运行一个bounded lifecycle组合。

推荐序列：

```text
structure summary
→ static physics artifact
→ viewer v2
→ supercell apply
→ measurement
→ clipping
→ export
→ invalid scene
→ legacy JSON-only
→ viewer v2

```

重复合理次数。

断言：

-   no stale artifact

-   no stale selection

-   no stale measurement

-   no duplicate canvas

-   no duplicate context

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

-   measurement

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

-   planner request

-   job execution

-   artifact result

-   renderer

-   inspector

-   measurement

-   supercell

-   clipping

-   camera preset

-   export

-   degraded/refused

-   legacy fallback

-   lifecycle switch

-   console/network audit


## Firefox Smoke

覆盖：

-   product entry

-   v2 renderer

-   measurement

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

-   one distance measurement

-   fallback

-   no scroll trap

-   no duplicate canvas/context


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

-   measurement

-   clipping

-   export


## Fixture C：Self-Periodic

用于：

-   self-periodic topology

-   inspector


## Fixture D：Degraded

使用compact generator或complexity input。

## Fixture E：Over-Budget

必须在allocation前拒绝。

不得：

-   提交巨大scene

-   复制历史fixture内容

-   通过随机生成导致不稳定

-   访问外网


----------

# 21. Closure Evidence

新增：

```text
docs/phase10/evidence/phase10_closure_regression_pack/

```

如果项目使用其他Phase 10目录约定，遵循现有结构。

至少包含：

```text
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

```

截图建议：

```text
01_phase10_tool_discovery.png
02_viewer_product_result.png
03_triclinic_periodic_inspection.png
04_measurement_supercell_clipping.png
05_export_result.png
06_degraded_mode.png
07_over_budget_fallback.png
08_legacy_json_only.png
09_mobile_smoke.png

```

不得保存：

-   巨大原始artifacts

-   browser cache

-   trace dump

-   private path

-   token

-   secret

-   remote URL

-   crash dump


----------

# 22. CI Entry

Closure pack必须有明确、稳定的执行入口。

推荐新增脚本或命令：

```bash
uv run python -m pytest -q tests/integration/test_phase10_product_closure.py

```

以及：

```bash
npm --prefix apps/web test -- phase10ProductClosure

```

browser：

```bash
npm --prefix apps/web run test:e2e -- phase10-product-closure

```

具体命令按真实package scripts调整。

建议增加统一入口：

```text
phase10-closure

```

例如：

```bash
scripts/test_phase10_closure.sh

```

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

-   network audit


----------

# 24. Test Runtime Budget

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

```text
docs/phase10/phase10_closure_regression_pack.md
docs/phase10/phase10_cross_phase_invariants.md
docs/phase10/phase10_closure_test_inventory.md
docs/phase10/phase10_closure_ci_contract.md
docs/phase10/phase10_closure_security.md
docs/phase10/phase10_final_readiness_matrix.md

```

按项目现有目录调整。

更新：

```text
docs/index.md
persistent/DESIGN_PROGRESS.md
persistent/TASK_BOARD.md
persistent/CHANGELOG.md
persistent/OPEN_QUESTIONS.md
persistent/ARCHITECTURE_DECISIONS.md

```

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

-   viewer scene contract

-   periodic topology


## Viewer Product

-   formal tool registration

-   renderer

-   inspector

-   picking

-   measurement

-   supercell

-   clipping

-   camera

-   export

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

```text
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

```

----------

# 27. Checks

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

-   network audit


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
git status --short
git diff --stat
git add <only Phase 10 Closure Regression Pack related files>
git commit -m "Add Phase 10 closure regression pack"
git push origin master

```

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

# Phase 10 Closure Regression Pack Result

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


## 17. Runtime Budget

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

-   any unavailable browser environment


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

```text
Phase 10G：Brillouin Zone Planning and Contract

```

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
---END---
