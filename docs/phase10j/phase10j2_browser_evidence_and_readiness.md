# Phase 10J-2 Browser Evidence and Readiness

Evidence is stored in [`evidence/phase10j2_isosurface_renderer/`](evidence/phase10j2_isosurface_renderer/). The runner consumes the real Phase 10J-1 `chgcar_augmentation` runtime artifact package, including its gzip binary payload, through a local job-scoped artifact content endpoint. Chromium, Firefox, and WebKit execute validation, gzip decode, the module Worker, mesh extraction, and the Three.js renderer. Chromium also records 390x844 touch/mobile output.

Observed Chromium reference case: WebGL2, one canvas/context, 50 welded vertices, 48 triangles, no external request, no console/page error, and a nonblank screenshot. Exact timings remain environment-specific and are evidence, not production guarantees.

## Readiness

| Capability | Decision |
| --- | --- |
| canonical volumetric contracts | READY |
| VASP/CUBE parser and adapter | READY |
| bounded raw/gzip/chunked loader | READY |
| Worker extraction/cancellation | READY |
| periodic logical halo/seam | READY |
| non-periodic affine/triclinic mapping | READY |
| gradient normals and mesh welding | READY |
| signed/multi-layer isosurfaces | READY |
| Three.js renderer and structure overlay | READY |
| picking, clipping, camera, PNG | READY |
| JSON/manifest/error fallback | READY |
| Chromium/Firefox/WebKit/mobile baseline | READY |
| lifecycle, network, and security | READY |
| cell-centered/vector/complex fields | NOT_IMPLEMENTED |
| slice/direct volume/Bader analysis | NOT_IMPLEMENTED |

Phase 10J-3 may consume this generic renderer only after current-head CI closure. It must add product-specific charge/spin semantics without changing this extraction boundary or inventing derived scientific fields in the renderer.
