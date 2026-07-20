# Phase 10J-3 Charge / Spin Density Product

## Scope and boundary

Phase 10J-3 adds a product interpretation layer over the existing
`structure.volumetric_data` artifacts. It does not add a second parser or
scientific calculation tool. The backend emits inert, validated fields; the
existing Phase 10J-2 Worker and Three.js consumer renders them locally.

The supported products are electron density, explicitly signed charge
density, and collinear spin density. Non-collinear vector magnetization is
identified and remains deferred. Bader charge, atomic partitioning,
charge-density differences, electrostatic potential, slices, and volume
ray-casting are not inferred from these fields.

## Quantity and sign semantics

`electron_density` is positive electron number density in
`electron/angstrom^3`; it is not an electric charge density. A signed
`charge_density` is accepted only when the source explicitly declares its
signed charge semantics and uses `elementary_charge/angstrom^3`.

For VASP collinear data, the source-native total field is electron density
and the source-native magnetization field is the signed difference
`rho_spin = rho_up - rho_down` in `bohr_magneton/angstrom^3`. The adapter
derives only the allowlisted fields:

```text
rho_up   = (rho_total + rho_spin) / 2
rho_down = (rho_total - rho_spin) / 2
```

The fields retain source hash, producer version, transformation detail,
formula ID, and exact field relationships. No clipping or renormalization is
performed. Full-cell integrals are reported using the declared integral
semantics and are never described as atomic charges or enclosed-isosurface
electron counts.

## Product UI and evidence

The product selects the collinear spin difference by default, offers total,
spin-up, and spin-down modes, and uses paired positive/negative isosurfaces
with a symmetric absolute threshold by default. The threshold lock is a
visual policy only and does not alter the canonical field. The UI displays
integrals, formula IDs, augmentation warnings, unavailable authoritative
references, and a non-authoritative scientific limitation notice.

The live evidence in
`docs/phase10j/evidence/phase10j3_charge_spin_density_product/` was generated
through Mock Planner, `QueueWorkerRuntime`, the real volumetric adapter, and
job-scoped artifact content routes. Chromium, Firefox, WebKit, and a mobile
viewport render one WebGL2 canvas with two default spin layers, four integral
rows, no console errors, and zero external requests.

## Security and lifecycle

Only validated scalar field data reaches the application Worker and renderer.
Artifact fields cannot select code, shader, URL, module, callback, HTML, or
external assets. Existing payload hash, byte, decompression, voxel, mesh,
Worker, WebGL, and PNG caps remain active. Field changes, artifact changes,
Worker replacement, renderer replacement, context loss, and unmount retain
the Phase 10J-2 disposal behavior.

## Deferred scope

Bader analysis, atomic charges, charge partitioning, density differences,
isolated-atom references, bond critical points, Laplacians, gradients,
non-collinear glyphs, spin texture, orbital phase, wavefunction density,
volume ray casting, slices, planar averages, potential alignment,
vacuum-level detection, electrostatic potential, time-dependent density,
mixed-periodicity/slab products, mesh export, external APIs, notebooks,
scripts, artifact code, and remote assets remain deferred.
