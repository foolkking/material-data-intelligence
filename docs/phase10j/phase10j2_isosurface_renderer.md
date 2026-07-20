# Phase 10J-2 Isosurface Renderer

## Baseline and outcome

Phase 10J-2 builds on Phase 10J-1 commit `b7a14a870123a743602d04dde5d66dbd166fbdcf` and its current-head CI closure. The public tool remains `structure.volumetric_data`; isosurface rendering is an application product capability consuming the tool's validated inert artifacts. No separate scientific calculation tool or artifact-controlled renderer was added.

The supported field gate is exact: `value_kind=real`, `field_rank=scalar`, one stored component, node sampling, finite values, shape axes at least two, and either fully periodic endpoint-excluded or fully non-periodic affine boundaries. Cell-centered, vector, complex, sparse, masked, and mixed-periodicity fields are typed unsupported states.

## Architecture

```text
planner artifact listing
  -> job-scoped bounded artifact content API
  -> strict dataset/manifest validation
  -> field/payload binding and SHA-256 validation
  -> raw/gzip/chunked decode
  -> application-owned module Worker
  -> bounded marching-tetrahedra extraction
  -> immutable transferable mesh buffers
  -> application-owned Three.js scene
  -> JSON/manifest fallback
```

`fflate@0.8.3` is a pinned MIT dependency used only for local deterministic gzip decoding. It has no transitive dependencies, install script, runtime network, binary download, CDN, or remote module requirement. Three.js remains pinned at `0.185.1` and is lazy-loaded with the renderer engine.

## Payload and Worker protocol

The browser only obtains bytes from `/planner/jobs/{job_id}/artifacts/{artifact_id}/content`. The route verifies job ownership, a 64 MiB response cap, stored byte length, SHA-256, and an explicit MIME allowlist. The frontend applies its stricter 16 MiB field budget, validates storage and logical hashes, enforces little-endian float32/float64 and `ijkc_component_fastest`, bounds gzip expansion to 128x, and verifies all decoded values are finite.

Each extraction replaces the prior Worker. The request carries application-owned caps and transfers one field buffer; responses transfer positions, normals, and indices. Revision identity rejects stale responses. Timeout, abort, field switch, artifact switch, tab switch, and unmount terminate the Worker.

## Product behavior

The panel provides Isosurface, Metadata JSON, and Manifest tabs. It supports deterministic initial positive or signed positive/negative layers, manual isovalues, up to four layers, per-layer visibility/removal, opacity, structure/cell/surface toggles, perspective/orthographic cameras, orbit/pan/zoom/reset, bounded clipping, surface and atom picking, local PNG export, status announcements, and mobile controls.

The optional `phase10j2.volumetric_structure_overlay.v1` artifact is independently validated and grid-bound. Periodic sources embed a validated canonical viewer scene; non-periodic CUBE sources carry bounded atomic numbers and Cartesian coordinates. It never carries renderer code, materials, URLs, HTML, shaders, or callbacks.

## Resource and lifecycle policy

Browser caps are 262,144 desktop voxels, 131,072 mobile voxels, four layers, 400,000 vertices and 300,000 triangles per layer, 800,000 vertices and 600,000 triangles total, 48 MiB mesh bytes, 64 MiB estimated GPU bytes, DPR 2, and 16,777,216 PNG pixels. Over-cap inputs are rejected without silent truncation. Rendering is demand-based; there is one canvas, one WebGL context, one active Worker, one shared atom geometry, bounded materials, and explicit disposal of controls, observers, listeners, geometry, materials, renderer, and Worker resources.

Context loss produces a safe typed state while JSON and manifest remain available. Unsupported Worker/WebGL, invalid contracts, failed gzip/hash, empty surfaces, mesh caps, extraction timeout, and lazy chunk failure do not fail the backend job.

## Known limits

Deferred by design: cell-centered isosurfaces, vector/complex derived fields, volume ray casting, 3D textures, slices, transfer functions, planar averages, Bader analysis, potential alignment, vacuum detection, magnetization glyphs, orbital phase, time-dependent volume, mixed-periodicity/slab products, mesh export, field editing, external APIs, notebooks/scripts, artifact code, and remote assets.
