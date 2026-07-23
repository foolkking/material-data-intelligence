# Phase 10J-4 Electrostatic Potential Product Evidence

This evidence consumes a real LOCPOT artifact produced through Mock Planner, QueueWorkerRuntime, the canonical adapter, and job-scoped content routes. The product preserves source-defined local-potential semantics and computes only application-owned constant gauge views, trilinear point samples, point differences, and three raw lattice-axis planar averages.

## Replay

```powershell
uv run python apps/web/test/generate-electrostatic-potential-evidence.py
npm --prefix apps/web run build
node apps/web/test/electrostatic-potential-browser-evidence.mjs
```

## Verified Browser Matrix

The current `browser/matrix.json` records Chromium, Firefox, and WebKit as
available WebGL2 implementations. Each rendered one canvas with 64 triangles,
50 vertices, five draw calls, four geometries, and four materials, with zero
console/page errors and zero external requests. The Chromium interaction pack
also records source/cell-average/selected-point gauges, source contour identity,
three axis profiles, a linked 3D profile plane, surface picking, point
sampling/difference, structure and clipping controls, accessibility, PNG
signature, and the invalid/reference fallback cases. The mobile captures use a
390x844 touch viewport with no horizontal page overflow.
