# Phase 10F-10 Viewer Scene Readiness Matrix

| Area | Status | Evidence | Decision |
|---|---|---|---|
| JSON-only preview surface | READY | `ViewerScenePreview` recognizes `viewer_scene.v1` and renders summary/validation fields | Can be used for inert preview evidence |
| Fixture-backed preview samples | READY | Frontend tests cover valid, warning/caps, and invalid fixture content | Can support follow-up evidence |
| Manifest preview | READY | `ViewerManifestPreview` recognizes `phase10f9.viewer_scene_manifest.v1` | JSON-only manifest preview is supported |
| Validation state display | READY | stable selectors for state, errors, warnings | Evidence selectors available |
| Warnings/caps display | READY | warning fixture test covers `VIEWER_SCENE_CAP_NEAR_LIMIT` and cap values | Evidence selectors available |
| Scene summary display | READY | kind, version, schema, site/bond/species counts, coordinate basis, lattice presence | Evidence selectors available |
| Frontend/API evidence | READY | fixture-backed workbench tests replay mock job artifacts | No production route added |
| Browser screenshot evidence | PARTIAL_READY | frontend/jsdom evidence exists; real screenshot not captured | Optional future hardening |
| Security evidence | READY | tests assert no canvas/script/iframe and no external URL/script/WebGL/Three.js markers | Renderer-free boundary preserved |
| Renderer evidence | DEFERRED | no renderer exists | Requires explicit future approval |
| Renderer implementation | NOT_READY | WebGL/Three.js/dependency review remains deferred | Do not implement directly |
| Full `structure.viewer_3d` implementation | NOT_READY | no adapter, no routing, no producer contract integrated | Do not implement directly |

## Conclusion

The JSON-only preview surface is ready. Renderer evidence, renderer implementation, and full `structure.viewer_3d` implementation are not ready.
