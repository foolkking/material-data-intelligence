# Phase 10F-12 Next Scope

Reviewer should select the next phase. Phase 10F-11 does not make the selection authoritative.

Reasonable options:

1. `Phase 10F-12: Viewer Scene Minimal Adapter Implementation`
   - Implement a small inert JSON adapter producing `viewer_scene.v1`.
   - Do not implement renderer, WebGL, Three.js, or full interactive `structure.viewer_3d`.

2. `Phase 10F-12: Viewer Scene Preview Surface Evidence Hardening`
   - Add more browser coverage or CI integration for the JSON-only preview surface.
   - Do not implement renderer or adapter.

3. `Phase 10F-12: Viewer Scene Runtime Integration Planning`
   - Plan safe runtime integration before adapter execution.
   - Do not change planner routing or Tool Registry behavior.

Always retain these boundaries:
- no direct full `structure.viewer_3d` implementation;
- no WebGL renderer implementation;
- no Three.js integration;
- no phonon implementation;
- no external API or notebook execution.
