# Phase 10J-1 Volumetric Parser / Adapter

## Pre-Implementation Audit

- Baseline: `afffec5d83a96e11b07bd755f7d759477b91bfbb` on `master`, matching `origin/master`, clean before the required task transition. Phase 10J implementation was `ee1410572b00ad5844c4ed9b29fd3144644acd41`; archive CI `29599751515` passed.
- Existing contracts: the Phase 10J grid, payload, field, dataset, and manifest builders already fixed row step vectors, endpoint policy, `ijkc_component_fastest`, little-endian float32/float64, deterministic storage, hashes, statistics, security metadata, and caps. No second artifact contract was created.
- Inventory: pymatgen POSCAR/Structure, NumPy, ASE, and gzip were present. There was no bounded VASP/CUBE source parser, `VolumetricData`, public adapter, registry/planner/runtime route, or metadata preview. No tool conflict existed.
- Memory: source bytes, header, line, token, atom, dimension, and voxel counts are checked before large allocation. Production parsing and SHA-256 are streaming. The parser cap is 2,097,152 voxels, below the 16,777,216 canonical contract cap. No temp file or new dependency is used.
- Strategy: an internal bounded parser uses pymatgen only for VASP structure semantics. Third-party parsers are not the safety boundary. The public identity is `structure.volumetric_data` and exactly one normalized source is required.

## Supported Formats and Semantics

| Source | Mapping | Limitation |
| --- | --- | --- |
| CHGCAR / CHG | total density; collinear total + spin difference; non-collinear total + Cartesian magnetization vector | augmentation excluded with warning |
| LOCPOT | local potential in eV, source-defined reference | no alignment or vacuum reference |
| ELFCAR | dimensionless scalar | reported, not clamped |
| PARCHG | source-native orbital density | no projection inference |
| Gaussian CUBE | one real scalar affine grid, Bohr/Angstrom coordinates | negative atom count/multi-orbital rejected |

VASP values are x-fastest and are reordered to canonical i/j/k with k fastest. Density-family raw values are divided by cell volume exactly once. The asymmetric fixture yields `[1,5,3,7,2,6,4,8]` after normalization. Periodic VASP grids use node samples, origin `[0,0,0]`, excluded endpoints, and row steps `lattice[row] / shape[row]`.

CUBE uses i-outer/j-middle/k-fastest values. Positive axis counts mean Bohr and negative counts mean Angstrom; origin, steps, atoms, and allowlisted density units convert explicitly. CUBE is non-periodic and never claims a crystal binding. Its quantity is `generic_scalar` unless an allowlisted hint is supplied.

## Conversion, Artifacts, and Runtime

The pipeline is file precheck, bounded detection, streaming parse, source validation, source-order conversion, endpoint/unit normalization, channel mapping, dtype encoding, statistics from decoded stored bytes, contract validation, hashing, and export. `contract_default` uses deterministic gzip unless the compression ratio exceeds the security cap, in which case it records `VOLUME_COMPRESSION_RATIO_FALLBACK_RAW`; explicit gzip still rejects.

Outputs are grid JSON, payload metadata JSON and field JSON per field, little-endian binary per field, dataset, manifest, summary, and recipe. QueueWorkerRuntime, Tool Registry, PlanValidator, and the normal artifact writer are used without bypass. Positive Mock Planner routes require `VolumetricData` plus parse/normalize intent. Renderer, isosurface, slice, VASP execution, trajectory, phonon, Brillouin-zone, defect, surface, and slab requests remain negative routes.

## Preview and Security

The JSON-only preview shows format, shape, voxel count, origin/sampling/periodicity, field identity, units, components, statistics, payload encoding/bytes, warnings, validation recognition, and renderer absence. It never expands binary values or creates canvas, WebGL, iframe, script, slice, or isosurface content.

The parser accepts no URL, arbitrary path param, parser import, codec, callback, shader, executable field, archive, or source-controlled output name. Comments are not propagated. Errors expose typed codes and safe summaries.

## Evidence and Replay

Evidence contains all supported source families, deterministic replay, a real in-memory planner/job/runtime execution, malformed and over-cap failures, and a temporary `128^3` (2,097,152 voxel) CUBE performance run. A `129^3` header rejects before payload allocation. Timings are observations, not production promises.

```powershell
uv run python -m pytest -q tests/test_phase10j1_volumetric_parser_adapter.py tests/test_phase10j_volumetric_contract.py
uv run python apps/web/test/generate-volumetric-parser-evidence.py
npm --prefix apps/web test -- --run app/components/PlannerWorkbench.test.tsx
```

## Deferred / Handoff

Deferred: multi-orbital CUBE, augmentation reconstruction, partial datasets, HDF5/VTK/OpenVDB/XSF, source compression, remote sources, renderer, slices, isosurfaces, volume analysis, simulation, and production-scale inputs above the parser cap. Phase 10J-2 may consume validated canonical artifacts but must not weaken this parser boundary.
