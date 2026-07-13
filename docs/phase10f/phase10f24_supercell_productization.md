# Phase 10F-24 Supercell Productization

The production viewer now exposes bounded renderer-local `[a,b,c]` expansion with draft/apply/reset controls, application-owned presets, preflight estimates, interactive/degraded/refused states, periodic picking and measurement, and inert state download. The canonical structure resource and `phase10f18.viewer_scene.v2` artifact are never modified.

Expansion updates reuse one WebGL renderer and replace bounded GPU buffers. This closes the active-context growth found by the three-browser 20-cycle audit. Formal runtime, Tool Registry, planner, and backend artifact semantics are unchanged.
