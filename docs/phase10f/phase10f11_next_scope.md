# Phase 10F-11 Next Scope Options

Phase 10F-10 implements JSON-only preview evidence for `viewer_scene.v1`. The next scope should be selected by reviewer decision, not by automatic progression into a renderer.

## Option A: Viewer Scene Minimal Adapter Implementation

Scope:

- implement a small inert `viewer_scene.v1` artifact producer;
- produce JSON-only artifacts only;
- do not implement WebGL, Three.js, renderer bundle, or full interactive viewer;
- keep planner routing and Tool Registry changes scoped and reviewed.

## Option B: Viewer Scene Preview Surface Evidence Hardening

Scope:

- add real browser screenshot evidence for existing JSON-only preview surface;
- capture console/network audit;
- prove no external resource request and no artifact JS execution;
- do not add a renderer.

## Option C: Viewer Scene Runtime Integration Planning

Scope:

- plan how a future `structure.viewer_3d` adapter would register and route;
- define resource caps, typed errors, warnings, and artifact filenames;
- do not implement runtime integration yet.

## Explicit Non-Scope

- Do not directly enter full `structure.viewer_3d` implementation.
- Do not implement WebGL.
- Do not integrate Three.js.
- Do not add a renderer bundle.
- Do not implement phonon or Brillouin-zone 3D.
