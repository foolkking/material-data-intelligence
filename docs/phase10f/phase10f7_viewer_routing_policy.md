# Phase 10F-7 Viewer Routing Policy

## 1. Scope

This document plans future deterministic routing boundaries for advanced structure viewer work. Phase 10F-7 does not implement routing.

## 2. Prompts That May Route to Future `structure.viewer_3d`

- 显示 3D 晶体结构
- 打开结构 viewer
- 生成结构 3D 视图
- Create a 3D structure viewer
- Show the crystal structure in 3D
- Create a static structure scene

## 3. Prompts That Must Not Route to `structure.viewer_3d`

- 生成 XRD 图谱
- 计算 RDF
- 生成 coordination histogram
- 画 phonon bands
- 画 phonon DOS
- 生成 Brillouin zone
- 做 Rietveld refinement
- 做 experimental fitting
- 做 CrystalNN local environment

## 4. Boundary Rules

- XRD prompts stay with `structure.xrd`.
- RDF prompts stay with `structure.rdf`.
- Coordination histogram prompts stay with `structure.coordination_hist`.
- Brillouin-zone prompts remain future scope unless a separate planning phase approves them.
- Phonon prompts remain deferred and must not route to viewer.
- Local environment classification prompts remain deferred and must not route to viewer.
- Fitting/refinement prompts remain unsupported for the viewer scope.

## 5. Implementation Rule

Routing implementation is deferred. Any future change must add positive and negative routing tests without modifying `/planner/jobs` main semantics or weakening PlanValidator boundaries.
