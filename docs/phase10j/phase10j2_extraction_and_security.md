# Phase 10J-2 Extraction, Scientific Mapping, and Security

## Extraction policy

Canonical values use `index=((i*ny)+j)*nz+k`; `k` is fastest. Every logical cube is split into the same six tetrahedra, avoiding the unresolved 256-case marching-cubes face ambiguity. Edge vertices use deterministic endpoint keys, linear field interpolation, stable ordering, and welding. Repeated-index and near-zero-area triangles are rejected before transfer.

For periodic endpoint-excluded grids, extraction creates a logical halo through wrapped sample addressing. It emits `nx*ny*nz` logical cubes without allocating or mutating a halo artifact. Non-periodic grids emit `(nx-1)*(ny-1)*(nz-1)` cubes. Coordinates always use full row-vector affine mapping:

```text
r = origin + i*step_0 + j*step_1 + k*step_2
```

This applies unchanged to shifted, orthogonal, and triclinic grids. Normals derive from central periodic or one-sided non-periodic field differences and transform through the inverse affine step basis into Cartesian space. Zero or non-finite gradients receive a deterministic geometric fallback; source values are never smoothed or resampled.

## Display semantics

The default isovalue is a display heuristic, not scientific analysis. One-signed fields begin one quarter through the finite range; signed fields use simultaneous `+/- 0.25*max(abs(min),abs(max))`. Exact active values, sign, unit, field identity, mesh hash, vertex count, and triangle count are visible. Picking reports the selected triangle and its Cartesian intersection; the interpolated value is the active layer isovalue.

## Threat boundary

Untrusted inputs include all artifact JSON, payload bytes, source names, field labels, warnings, dimensions, values, and hashes. Trusted inputs are application code, pinned packages, canonical validators, fixed tetrahedralization, fixed shaders/materials, and fixed caps.

Controls prevent JavaScript/HTML/CSS/shader/module/callback/URL interpretation, prototype keys, arbitrary codecs, gzip bombs, oversized allocations, non-finite values, stale Worker results, duplicate contexts, listener leaks, and filename injection. Artifact values never select imports, Worker URLs, materials, shader source, DOM ids, selectors, callbacks, textures, or external services. Errors expose bounded codes/summaries rather than payloads, stacks, storage paths, environment values, or secrets.

The renderer performs no fetch/XHR/WebSocket/image/texture/module request. Only local frontend chunks and local planner artifact routes are permitted. Browser evidence records `NO_VOLUMETRIC_ISOSURFACE_EXTERNAL_NETWORK_REQUESTS` and `NO_SECRET_PATTERN_HITS`.
