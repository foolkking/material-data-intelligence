# Phase 10F-15 Integrated Plan

## Outcome

Promote the validated Phase 10F renderer into a production-minimal capability without changing `viewer_scene.v1` or moving execution authority into the browser.

## Frozen Decisions

- Formal product identity: `structure.viewer_3d`.
- Explicit data-export identity: `structure.viewer_scene`.
- Legacy identities: `structure.viewer_scene_metadata` and `structure.viewer_export_package` remain direct-purpose compatibility tools.
- `structure.structure_3d` remains a separate static Plotly tool.
- Backend jobs generate inert canonical artifacts; frontend rendering is an independent capability.
- Renderer hard cap equals the canonical contract cap, so there is no renderer-side truncation.
- Three.js remains lazy and local; no artifact controls modules, shaders, textures, URLs, HTML, or callbacks.

## Acceptance

Registry, planner, PlanValidator, QueueWorkerRuntime, canonical validation, instanced rendering, desktop/mobile interaction, Chromium/Firefox/WebKit evidence, security scans, build, full tests, and current-HEAD CI must pass.
