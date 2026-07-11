# Phase 10F-14 Renderer API Contract

## Input

Only a payload with `kind: viewer_scene`, `version: viewer_scene.v1`, `schema_version: phase10f8.viewer_scene.v1`, valid security flags, finite geometry and Phase 10F caps may map to `ValidatedRenderScene`.

## Internal Model

The model contains renderer-owned `RenderAtom`, `RenderBond`, `RenderLattice` and warnings. Site and bond order are deterministic. Colors are canonical hex or a renderer palette; radii are bounded. Unknown fields are not forwarded.

## Engine API

The surface receives only `resetCamera`, `setCellVisible`, `setBondsVisible`, `render`, `snapshot` and `dispose`. The snapshot exposes object counts, camera, drawing buffer, WebGL generation and Three revision for evidence.
