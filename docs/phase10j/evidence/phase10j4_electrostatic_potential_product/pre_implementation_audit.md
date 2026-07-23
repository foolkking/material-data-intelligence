# Phase 10J-4 Pre-Implementation Audit

## Baseline

- Phase 10J-3 implementation: `d4de1a342d767fcfe21302b7465ae047fdf620f9`
- Phase 10J-3 implementation CI: run `29757885564`, success
- Phase 10J-3 completion record: `694c79eae7f65b1513fc010281972211642b22d6`
- Phase 10J-3 completion CI: run `29895985539`, success
- Phase 10J-3 archive/current starting HEAD: `39dcd1b1f795af0b213123b5d6d71947f43d8492`
- Branch and remote: `master`, equal to `origin/master`
- Starting worktree: clean before the task was marked `处理中`
- Phase 10J-3 checks: frontend `246 passed`; backend `719 passed, 24 skipped`; Chromium, Firefox, WebKit, mobile, build, service-backed, and no-skipped gates passed

## Available Potential Fields

- Canonical schemas remain `phase10j.volumetric_grid.v1`, `phase10j.volumetric_payload.v1`, `phase10j.volumetric_field.v1`, `phase10j.volumetric_dataset.v1`, and `phase10j.volumetric_manifest.v1`.
- Quantity enums include `local_potential` and `electrostatic_potential`.
- VASP LOCPOT parsing is implemented and intentionally emits source-defined `local_potential` in `electronvolt`.
- Explicit CUBE quantity hints may emit `electrostatic_potential` in `hartree`; generic scalar fields do not enter this product.
- Potential reference kinds are strict canonical metadata. No reference is inferred from statistics.

## Existing Product Infrastructure

- The Phase 10J-2 application-owned Worker, Three.js 0.185.1 renderer, periodic extraction, structure overlay, clipping, picking, camera controls, local PNG export, context handling, and lifecycle cleanup are reused.
- Browser caps remain 16 MiB payload, 262144 desktop voxels, 131072 mobile voxels, four layers, 600000 total triangles, 64 MiB estimated GPU bytes, and 16777216 export pixels.
- Phase 10J-3 product selection and signed density behavior remain independent.

## Selected Strategy

- Preserve source bytes and source isovalues.
- Represent source-native, cell-average-zero, and selected-point-zero as allowlisted display gauges.
- Preserve source contour identity across gauge changes.
- Compute all three raw lattice-axis profiles in one existing Worker pass and bind deterministic profile models to the source field hash.
- Perform bounded trilinear point sampling and point differences locally from the validated source field.
- Add one bounded renderer-local profile plane; do not add a tool, dependency, parser, or artifact execution surface.

## Excluded Claims

Vacuum detection, work function, Fermi alignment, cross-calculation alignment, macroscopic averaging, electric-field calculation, component decomposition, arbitrary paths/slices, direct volume rendering, DFT execution, external APIs, and artifact code remain excluded.
