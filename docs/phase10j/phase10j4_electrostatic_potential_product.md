# Phase 10J-4 Electrostatic Potential Product

Phase 10J-4 is an application-owned consumer of the existing
`structure.volumetric_data` artifacts. The real VASP LOCPOT boundary remains
`local_potential` in `electronvolt`, with `source_defined` reference metadata.
It is not renamed to pure electrostatic potential, and no ionic, Hartree,
exchange-correlation, vacuum, Fermi, or work-function component is inferred.

The product reuses the Phase 10J-2 Worker and Three.js renderer for bounded
equipotential surfaces, structure overlay, clipping, picking, camera controls,
profile-plane linking, and PNG export. The Worker computes all three raw
profiles in one pass while it owns the transferred field buffer. Source payload
bytes, hashes, field ID, statistics, and reference metadata remain immutable.

Supported renderer-local views are source-native, discrete cell-average-zero,
and selected-point-zero. Each is one bounded constant shift. The UI discloses
the shift, exact unit, source reference, full-cell statistics, limitations,
trilinear point samples, gauge-invariant point differences, and three raw
lattice-axis planar profiles. Surface layers retain source-native isovalues;
changing gauge shifts only their displayed values and preserves the same
source contour and mesh.

Vacuum detection, work function, Fermi alignment, cross-calculation alignment,
macroscopic averaging, arbitrary paths/slices, electric field, potential
component decomposition, direct volume rendering, and DFT execution remain
deferred.

## Verified Closure

- Runtime evidence was generated from a real QueueWorkerRuntime LOCPOT artifact
  and its job-scoped artifact content, not from a browser-only synthetic field.
- Chromium, Firefox, and WebKit each produced one WebGL2 canvas with 64
  triangles, 50 vertices, five draw calls, four geometries, and four materials;
  all had zero console/page errors and zero external requests. Chromium also
  completed surface picking, point sampling, three profiles, linked plane,
  gauge changes, structure toggles, clipping, accessibility, and local PNG
  export. Mobile evidence recorded one nonblank canvas and no page overflow.
- The bounded near-cap frontend test exercised a `128^3` float64 field
  (2,097,152 voxels / 16 MiB) and reduced it to 384 stored profile values.
- Local checks passed: 258 frontend tests, 722 backend tests, 24 intentional
  backend skips, typecheck, production build, Ruff with repository compact-test
  style exclusions, historical volumetric/charge-spin/Phase 10 browser replay,
  `uv lock --check`, and `git diff --check`.
- Docker is not installed locally, so PostgreSQL/Redis/MinIO service-backed
  and zero-skip integration remain current-HEAD CI gates. The configured npm
  audit mirror returned `404 NOT_IMPLEMENTED`; no dependency changed.
