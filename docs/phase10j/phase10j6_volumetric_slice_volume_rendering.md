# Phase 10J-6 Volumetric Slice / Volume Rendering

## Result scope

Phase 10J-6 adds two application-owned consumers over unchanged canonical
Phase 10J artifacts:

```text
structure.volumetric_data
  -> validated dataset/grid/field/payload/manifest
  -> bounded browser payload loader
  -> Slice Worker or WebGL2 Direct Volume Renderer
```

No public tool, dependency, canonical scientific field, persisted resampling
artifact, executable artifact, or remote resource is added. The typed
`phase10j6.volumetric_slice.v1` object is ephemeral display state with a
deterministic SHA-256 and source hashes.

## Pre-implementation audit

The Phase 10J-5 baseline is commit `a5ba567` with completion commit `75b2d74`
and verified archive HEAD `f8cbdda`. Existing canonical artifacts use
`phase10j.volumetric_*.v1`, little-endian float32/float64 payloads, raw,
deterministic gzip, chunked, or bounded inline encodings. Three.js remains the
single direct dependency at `0.185.1`.

The existing payload loader, artifact authorization, SHA-256 validation,
Worker bundling, structure overlay mapper, OrbitControls, PNG path, context
loss handling, mobile layout, and one-canvas lifecycle are reused. Supported
input is exactly finite, real, scalar, one-component, node-sampled data on a
fully periodic endpoint-excluded or fully non-periodic affine 3D grid.
Vector, complex, cell-centered, sparse, masked, mixed-periodic, arbitrary
expression, and artifact-controlled rendering inputs are rejected before
sampling or GPU allocation.

## Slice scientific model

Slices are restricted to canonical lattice axes 0, 1, and 2. Their coordinate
is a fractional position in the affine grid domain. Periodic coordinates wrap;
non-periodic coordinates are bounded and never extrapolated.

An aligned plane is `exact_grid_plane`. Other positions use only one-dimensional
linear interpolation between adjacent axis planes. The source payload is never
clamped, smoothed, normalized, or mutated. Axis orientation is fixed:

| Fixed axis | Horizontal parameter | Vertical parameter |
|---|---|---|
| 0 | axis 2 | axis 1 |
| 1 | axis 2 | axis 0 |
| 2 | axis 1 | axis 0 |

The 2D view is a parameter-space heatmap. The 3D plane uses the true affine
parallelogram, including triclinic cells and shifted origins. Point probing
maps continuous slice coordinates back to fractional and Cartesian positions
and reports the exact sampled/interpolated source value and unit. Palette,
window, pinned point, and zoom are display state only. The accessible table is
bounded and remains available when WebGL is unavailable.

Sampling runs in an application-owned module Worker. One Worker is retained
while axis/position changes occur; revision IDs reject stale results, transfer
buffers avoid duplicate ownership, and mode/artifact/unmount transitions
cancel or terminate work. Superseding an in-flight request terminates the old
Worker before a replacement is created, so stale synchronous sampling does not
continue consuming CPU. Slice hashes use the application-owned synchronous
SHA-256 implementation and bind source dataset/field hashes, plane definition,
sampling metadata, values, units, and provenance.

Slice payloads remain source-native float32 or float64 data. The float64 to
float32 conversion and GPU byte preflight apply only to Direct Volume. The 2D
surface exposes exact source/display ranges, a numeric legend, a paginated
value table, keyboard and pointer probes, and bounded zoom/pan. Its optional 3D
plane is lazy-loaded, provides perspective and orthographic projection, shows
the unit cell and selected-point marker, and shares the synchronized probe.

## Direct volume architecture

Direct Volume requires WebGL2, at least two fragment texture units,
`MAX_3D_TEXTURE_SIZE` compatibility, `OES_texture_float_linear`, bounded
allocation, and successful local shader execution. Before Three.js allocation,
a transient WebGL2 context compiles and links the exact static vertex/fragment
program; failure releases that context and enters the typed fallback. It uploads one R32F-equivalent
Three.js `Data3DTexture`. Canonical `k`-fastest storage is not transposed:

```text
texture width  = nz
texture height = ny
texture depth  = nx
texture xyz    = canonical q2, q1, q0
```

Float64 source payloads are copied to a float32 display buffer only after the
browser byte cap is checked. Maximum absolute, relative, RMS conversion errors
and a conversion SHA-256 are exposed; the source buffer remains immutable.

The static application-owned GLSL3 shader performs affine world-to-unit ray
mapping, unit-cube intersection, bounded trilinear 3D texture sampling,
front-to-back compositing, step-length opacity correction, and early
termination at alpha `0.985`. The compile-time loop cap is 768 and quality
presets can only lower the runtime step count, samples per voxel, and DPR.
Transfer functions and palettes are closed application enums; they are display
state, not scientific transforms.

## Structure depth and clipping

Volume, atoms, bonds, unit cell, camera, and controls use one Three.js scene,
canvas, and WebGL2 context. Rendering uses a bounded structure depth prepass:

1. Opaque structure depth is written to one local `DepthTexture`.
2. Structure color and depth are rendered to the default framebuffer.
3. The volume shader reconstructs structure position from depth and terminates
   its ray at an internal or rear opaque surface.
4. Normal source-over blending preserves volume attenuation in front of the
   structure; front geometry is retained by the default depth test.

This is not a render-order-only policy. The depth target tracks DPR/resize,
counts toward estimated GPU memory, and is disposed with the renderer.

Clipping is shared. The volume shader uses canonical unit coordinate
`q_axis <= offset`; atoms, bonds, and cell use the corresponding world-space
plane derived from the full affine basis. Orthogonal and triclinic plane math
is unit tested. Direct Volume remains source-cell only; supercell volume is
deferred.

## Resource policy

| Resource | Desktop cap | Mobile cap / behavior |
|---|---:|---:|
| Volume voxels | 2,097,152 | 524,288 |
| Volume texture bytes | 16,777,216 | same byte ceiling plus lower voxel cap |
| Float64 conversion input | 16,777,216 bytes | same |
| Slice values | 262,144 | same |
| Slice cache | 2 entries | 2 entries |
| Ray steps | 768 | 384 |
| Samples per voxel | 2 | 2 |
| Render pixels | 2,097,152 | same; DPR is reduced first |
| Export pixels | 16,777,216 | same |

GPU estimate includes the float texture, upload/display copy allowance, and
RGBA plus depth render target. Any dimension, voxel, byte, GPU estimate,
texture-unit, filtering, shader, or context failure refuses Direct Volume
before unbounded allocation. Slice and Isosurface remain explicit fallbacks.
There is no silent downsampling.

## Product integration

`VolumetricPreviewPanel` retains Metadata, Isosurface, existing Charge/Spin,
Potential, and ELF/Orbital product surfaces and adds Slice and Volume tabs for
compatible fields. Planner routing keeps `structure.volumetric_data` as the
only public identity and recognizes explicit slice/direct-volume intent while
retaining negative routing for Bader, segmentation, arbitrary filters,
arbitrary planes, calculations, remote rendering, vector/complex fields, and
unsupported scientific inference.

## Evidence and audit

Evidence is under
`docs/phase10j/evidence/phase10j6_volumetric_slice_volume_rendering/`.
Real Mock Planner -> `/planner/jobs` -> QueueWorkerRuntime artifacts cover
CHGCAR charge, signed collinear spin difference, LOCPOT, ELFCAR, PARCHG, and a
triclinic non-periodic CUBE. Browser evidence covers Chromium, Firefox,
WebKit, mobile Slice, all three axes, exact/interpolated planes, probing, 3D
plane, perspective/orthographic projection, Direct Volume shader linking,
annotated Slice/Volume PNGs, clipping, context loss, and repeated mode switching.

The near-cap runner creates a deterministic valid `128^3` float32 field in
memory, validates and hashes it through the normal frontend path, uploads the
8,388,608-byte texture, and records a 33,556,480-byte conservative GPU estimate.
The large payload is not committed. This environment reached ready in
2960.709 ms under Chromium ANGLE SwiftShader; this is an environment-specific
measurement, not a universal FPS or hardware claim.

Security review confirms no artifact JavaScript, shader, Worker/WASM, HTML,
CSS, URL, module, callback, transfer code, plane expression, remote texture,
CDN, iframe, fetch added by the renderer, or source mutation. Static scan,
browser request interception, console/page-error capture, payload hashes,
allocation caps, Worker revisions, lifecycle disposal, and safe PNG dimensions
are independently evidenced.

Local closure passed 294 frontend tests, 760 backend tests with 24 intentional
service-gated skips, all 98 Phase 10J tests, typecheck, production build, the
Phase 10J/10I/10H/10G/formal structure/Phase 10 browser runners, and the final
three-browser Slice/Volume replay. The home route first-load JS is 228 kB after
lazy-loading both Three.js engines. Docker is unavailable locally, so the
PostgreSQL/Redis/MinIO service-backed and zero-skip gates remain mandatory in
current-HEAD CI. The configured npm mirror does not implement the audit endpoint
and returned HTTP 404; no dependency or lockfile changed.

Required markers are:

```text
VOLUMETRIC_SLICE_VOLUME_RUNTIME_EVIDENCE_PASS
VOLUMETRIC_SLICE_BROWSER_EVIDENCE_PASS
VOLUMETRIC_DIRECT_VOLUME_BROWSER_EVIDENCE_PASS
VOLUMETRIC_TEXTURE_MAPPING_EVIDENCE_PASS
VOLUMETRIC_SLICE_VOLUME_PERFORMANCE_EVIDENCE_PASS
NO_VOLUMETRIC_SLICE_VOLUME_EXTERNAL_NETWORK_REQUESTS
NO_SECRET_PATTERN_HITS
```

## Readiness

The canonical contracts, parsers, prior isosurface/products, lattice-axis
Slice Product, exact/interpolated planes, quantitative heatmap, affine 3D
plane, point probing, WebGL2 Direct Volume, canonical texture mapping,
triclinic rendering, transfer functions, structure depth, shared clipping,
PNG, three-browser support, mobile fallback, accessibility, caps, lifecycle,
network isolation, and security are READY. Implementation CI `30197771307`
passed unit, frontend build, service-backed integration, and no-skipped gates;
the queue completion-record CI/archive step remains administrative closure.

Explicitly deferred are cell-centered rendering, arbitrary oblique or curved
scientific slices, vector/complex volume, scientific resampling, display
downsampling, empty-space octrees, segmentation, basin/topology/Bader analysis,
scientific volume ray picking, 4D volume, mixed-periodicity products, direct
volume supercells, remote GPU rendering, video, external APIs, notebooks,
scripts, artifact code, and remote assets.
