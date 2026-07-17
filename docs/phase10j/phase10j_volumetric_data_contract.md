# Phase 10J Volumetric Data Contract

## Scope

Phase 10J defines an inert, deterministic real-space volumetric contract. It
adds no file parser, Tool Registry entry, planner route, runtime adapter,
renderer, isosurface, slicing UI, remote resource, or executable artifact.

The contract family is:

| Layer | Schema |
| --- | --- |
| Grid | `phase10j.volumetric_grid.v1` |
| Payload | `phase10j.volumetric_payload.v1` |
| Field | `phase10j.volumetric_field.v1` |
| Dataset | `phase10j.volumetric_dataset.v1` |
| Manifest | `phase10j.volumetric_manifest.v1` |

## Grid Mathematics

Real-space lattice vectors are rows of `A`, matching the repository structure
contract:

```text
r_cart = r_frac * A
```

Grid samples use three row step vectors:

```text
r(i,j,k) = origin
           + (i + sample_shift) * step[0]
           + (j + sample_shift) * step[1]
           + (k + sample_shift) * step[2]
```

`sample_shift` is `0` for `node` and `0.5` for `cell_center`. In cell-center
mode the origin is the grid-domain corner, not the first sample. A periodic,
structure-bound grid requires all three axes periodic, endpoint `excluded`, a
finite nonsingular row lattice, a structure SHA-256, and an exact lattice
SHA-256. Its step rows multiplied by shape reproduce the bound lattice. A
non-periodic grid is a general nonsingular affine box and may declare endpoint
`included` or `excluded`. Mixed periodicity is deferred and rejected.

The voxel volume is `abs(det(step_matrix))`. Grid inversion is bounded by
finite, determinant, and condition-proxy checks. Fractional wrapping uses the
half-open interval `[0, 1)`.

## Index And Components

Logical indices are `(i, j, k, c)`. The canonical flatten offset is:

```text
offset = (((i * ny) + j) * nz + k) * stored_components + c
```

Component `c` is fastest, then `k`, `j`, and `i`. Shape is always `[nx, ny,
nz]`; components are recorded separately. Supported values are:

| Value kind | Rank | Stored components | Basis/order |
| --- | --- | ---: | --- |
| real | scalar | 1 | scalar |
| real | vector | 3 | Cartesian x, y, z |
| complex | scalar | 2 | interleaved real, imaginary |

Complex vectors, tensors, masks, sparse payloads, and time axes are rejected.

## Payload

Canonical binary dtypes are `float32` and `float64`, always little endian.
Supported encodings are:

* `inline_json` for small finite fixtures;
* `raw_binary`;
* deterministic `gzip_binary` using fixed gzip metadata;
* `chunked_binary`, split only into contiguous whole `i` slabs.

Expected byte length is `nx * ny * nz * stored_components * dtype_bytes` and
is checked before allocation or decode. Every payload carries a logical
SHA-256 over uncompressed canonical bytes and a separate storage SHA-256.
Chunk records carry exact `i` ranges, byte sizes, hashes, and deterministic
order. Gaps, overlap, reordering, trailing bytes, truncation, multi-member gzip,
compression-ratio excess, and hash mismatch are rejected.

## Field Semantics

Quantity and unit are allowlisted and distinct. Electron density, charge
density, spin density, magnetization density, electrostatic potential,
wavefunction, ELF, and generic declared scalar semantics are not aliases.
Canonical/source unit, identity conversion factor, and conversion provenance
are explicit.

Every field declares normalization and integral semantics. Statistics are
computed from finite decoded values with float64 accumulation and include
component min/max, mean, RMS, variance, standard deviation, absolute integral,
and signed integral. Histograms are optional and capped. No silent
renormalization or NaN/Infinity replacement occurs.

Collinear spin records explicit channels and sign convention. Non-collinear
magnetization is a Cartesian three-component vector. Electrostatic potential
records its gauge/reference and any applied shift. Complex scalar data retains
both real and imaginary components; magnitude-derived density would be a
separate future field.

## Dataset And Manifest

A dataset binds one grid, one or more payloads, fields on exactly that grid,
optional validated field relationships, warnings, provenance, caps, and a
content hash. Grid, payload, field, and dataset identities remain separate.
Field relationships such as total equals up plus down are explicit records,
not inferred claims.

The manifest inventories JSON metadata and binary artifacts with media type,
size, SHA-256, schema, and security policy. It states that no renderer,
JavaScript, HTML, CSS, shader, executable, or external URL is included.

## Resource Limits

The v1 hard caps include:

| Resource | Limit |
| --- | ---: |
| dimension per axis | 512 |
| total voxels | 16,777,216 |
| stored values | 50,331,648 |
| fields per dataset | 8 |
| uncompressed bytes per field | 268,435,456 |
| compressed bytes per field | 134,217,728 |
| dataset bytes | 536,870,912 |
| inline values | 262,144 |
| inline JSON bytes | 4,194,304 |
| chunks per field | 256 |
| compression ratio | 128 |
| metadata bytes | 65,536 |

Shape multiplication uses bounded integer checks before buffers are created.
Gzip decode is streaming and bounded by declared output size, ratio, and member
count. Artifact names are local safe names without path traversal. Pickle,
object arrays, nested archives, callbacks, URLs, scripts, shaders, and arbitrary
codecs are not accepted.

## Fixtures And References

Committed fixtures cover a cubic constant scalar, periodic trigonometric
scalar, triclinic periodic grid, non-periodic affine box, synthetic collinear
spin channels, non-collinear magnetization, complex scalar, potential gauge,
chunked payload, and negative cases. Independent standard-library references
verify row-vector coordinates, cell-center offsets, `ijkc` flattening,
little-endian float64 decoding, voxel volume, and the constant-field integral.

All fixtures are deterministic. Gzip bytes use fixed metadata; logical content
identity is independent of raw/gzip/chunk storage; the evidence inventory
records SHA-256 and byte length for every generated file.

## Handoff

The generic JSON preview may display schemas, dimensions, quantities, units,
statistics, encodings, hashes, warnings, and security metadata. It must not
claim rendering or parsing.

`is_isosurface_compatible` is a pure readiness helper for finite real scalar
fields only. It performs no extraction or rendering. Future parser work must
convert source axis, units, endpoints, dtype, and channels into this contract
without mutating its semantics. Future slice, isosurface, trajectory-volume,
and reciprocal-volume capabilities require separately reviewed contracts.
