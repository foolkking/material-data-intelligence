# Phase 10J Post-J6 Roadmap Reconciliation

> Status: HISTORICAL / SUPERSEDED BY GATE J6-R
> Current authority: [../ROADMAP.md](../ROADMAP.md). The J-7 through J-12
> electronic/Fermi sequence below was superseded by the product-centered
> roadmap and must not be used as an executable queue.

## Status

This was the reviewer-approved roadmap at that point after Phase 10J-6. It is a
planning freeze only. It adds no scientific schema, parser, adapter, public
tool, planner route, runtime behavior, renderer, dependency, or execution
authority.

## 1. Why Reconciliation Was Required

The historical plan assigned Electronic Band / DOS to J-5 and Fermi Surface
to J-6. Actual delivery used those identifiers for:

```text
Phase 10J-5  ELF / Orbital Volumetric Product
Phase 10J-6  Volumetric Slice / Volume Rendering
```

Those completed historical names remain unchanged. Reusing their numbers did
not implement Electronic Band / DOS or Fermi Surface. Repository audit found
no electronic-band schema, electronic-DOS schema, Fermi-surface schema,
parser, adapter, public tool, product surface, or renderer. Existing band/DOS
contracts and products are phonon-specific; the Phase 10I reciprocal-space
consumer explicitly reserves no electronic semantics.

## 2. Reviewer Decision

The canonical continuation is frozen as:

```text
Phase 10J-7   Electronic Band / DOS Contract
Phase 10J-8   Electronic Band / DOS Parser & Adapter
Phase 10J-9   Electronic Band + DOS Product / Brillouin Zone Link
Phase 10J-10  Fermi Surface Contract
Phase 10J-11  Fermi Surface Extraction / Renderer
Phase 10J-12  Electronic / Fermi Evidence Closure
```

This is roadmap reconciliation, not retroactive renaming. J-5 and J-6 retain
their actual completed meanings.

## 3. Existing Completed J-Line

```text
10J     Volumetric Contract
10J-1   Volumetric Parser / Adapter
10J-2   Isosurface Renderer
10J-3   Charge / Spin Density
10J-4   Electrostatic Potential
10J-5   ELF / Orbital Volumetric Product
10J-6   Volumetric Slice / Volume Rendering
```

Phase 10J-6 is `READY_WITH_EXPLICIT_LIMITS`. Its result, evidence, completion
record, exact-SHA CI, and queue archive are retained. Deferred volumetric work
includes cell-centered, arbitrary oblique/curved, vector/complex/4D, sparse or
octree, resampling, segmentation/topology/Bader, remote GPU, and video scope.

## 4. Frozen J-7 Through J-12 Scope

### Phase 10J-7: Electronic Band / DOS Contract

Contract work must define, validate, cap, and secure electronic band identity,
calculation and structure lineage, reciprocal lattice and k-point identity,
Phase 10I BZ/k-path binding, reciprocal units and `2*pi` convention, energy
unit/reference, Fermi energy, band/spin/occupation semantics, metallicity,
direct/indirect gap semantics, degeneracy/crossings, discontinuities,
high-symmetry labels, and provenance.

DOS work must define energy grid/reference, Fermi reference, total and spin
DOS, projected element/site/orbital DOS, density units and normalization,
integrated-state validation, smearing metadata, projection completeness,
caps, validation, provenance, and security. J-7 adds no parser, adapter, tool,
plot, renderer, or calculation.

### Phase 10J-8: Electronic Band / DOS Parser & Adapter

After J-7 freezes the contracts, J-8 may audit and select a bounded first
source-format set, then add format detection, parsers, canonical conversion,
strict public tool identities and parameters, Registry/PlanValidator/Planner/
QueueWorkerRuntime integration, inert artifacts, parse reports, manifests,
summaries, recipes, and real API evidence. No format is promised before audit.

### Phase 10J-9: Electronic Band + DOS Product / BZ Link

J-9 may add application-owned band, DOS, projected DOS, spin, Fermi-line,
shared-energy-axis, gap/metal behavior, table, JSON, PNG, mobile,
accessibility, and browser products. Bidirectional linking must reuse Phase
10I canonical reciprocal-space and k-path identities; it must not invent a
second BZ convention.

### Phase 10J-10: Fermi Surface Contract

The contract must require a validated regular three-dimensional k mesh and
define reciprocal coordinates, periodicity, first-BZ mapping, band/spin
identity, energy reference and Fermi energy, iso-energy, interpolation,
degeneracy, multiple sheets, mesh completeness, topology identity, caps,
validation, and provenance. A one-dimensional high-symmetry band path is
insufficient and must be rejected with a typed result.

### Phase 10J-11: Fermi Surface Extraction / Renderer

Only after J-10 may the product select band/spin, derive bounded
`E(k)-E_F`, extract deterministic periodic surfaces, clip to the first BZ,
represent multiple sheets, reuse BZ overlays and reciprocal axes, and add
bounded opacity, picking, inspection, camera, clipping, PNG, JSON fallback,
Three.js reuse, lifecycle, GPU caps, and browser evidence.

### Phase 10J-12: Electronic / Fermi Evidence Closure

This phase is limited to scientific reference validation and product closure:
semiconductor, metal, spin-polarized and multiple-sheet cases; degeneracy,
insufficient-mesh rejection, BZ clipping, periodic seams, deterministic
extraction, API/browser/mobile/accessibility/performance/GPU/context-loss,
network/secrets, service-backed/no-skipped, and current-HEAD CI evidence.

## 5. Scientific Boundaries

J-7 through J-12 consume existing electronic-structure results. They do not
run VASP, Quantum ESPRESSO, ABINIT, DFT, HPC jobs, notebooks, scripts, or
external material-data requests. Fermi surfaces require genuine 3D reciprocal
sampling. Fermi energy is not vacuum alignment, work function,
cross-calculation alignment, band-edge alignment, core-level alignment, or an
absolute electrostatic zero. Projected `s/p/d/f` DOS identity is not complex
wavefunction phase, orbital reconstruction, HOMO/LUMO inference, or orbital
linear combination.

## 6. Historical Next-Domain Proposal

```text
Phase 10K   Advanced Structure Science
Phase 10L   Experimental XRD
Phase 10M   Trajectory Advanced Analytics
Phase 10N   Scientific Workspace Integration
Phase 10 Expansion Closure
Phase 11    Official Scientific Validation
Phase 12    Production Platform Hardening
Phase 13    Advanced / Research Extensions
```

This sequence was the proposed next route at the time. It is not current. Gate
J6-R replaces it with Phase 10K Material Intelligence through Phase 12 Final
Product Closure; see `docs/ROADMAP.md`.
