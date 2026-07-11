# Phase 10F-14 Renderer Browser Evidence

Command: `node apps/web/test/viewer-scene-renderer-browser-evidence.mjs`.

Real Chrome `149.0.7827.201`, viewport 1440 x 1200, rendered live adapter Si, NaCl, warning/caps and bonds-disabled artifacts. WebGL 2 used ANGLE SwiftShader with a 1014 x 633 drawing buffer. Three revision is 185.

Evidence verifies rotate, zoom, deterministic reset, bonds toggle, cell toggle, JSON switch, remount, unsupported fallback, invalid gate and context-loss cleanup. Initial and remounted canvas pixel hashes match. Console/page errors are zero after expected browser 404 noise filtering. External requests are zero.

Markers:

- `VIEWER_SCENE_RENDERER_FOUNDATION_BROWSER_EVIDENCE_PASS`
- `NO_RENDERER_EXTERNAL_NETWORK_REQUESTS`
