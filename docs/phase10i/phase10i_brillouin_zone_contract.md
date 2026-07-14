# Phase 10I Brillouin Zone Contract

## Scope

Phase 10I defines a closed, versioned, inert contract family for reciprocal
lattices, first Brillouin-zone geometry, high-symmetry paths, and package
manifests. It adds validators, deterministic fixture generation, independent
mathematical references, and a future producer/consumer handoff.

It does not register `structure.brillouin_zone`, add planner routing, execute a
production adapter, or add a renderer. The current generic JSON preview is the
only product surface for these fixtures.

## Baseline

Phase 10I started from clean `master` at
`b0b191cb05f518acfb50924a5021944bfea7c6b4`. Phase 10H-5 implementation
`b67a9e18109f976aeadaf6002eaac6c71297875c` passed CI `29327516331`; its
completion record `1021a2e2cba202ffaec22d4e0d35a4fb345a890c` passed CI
`29327795589`, and the archive baseline passed CI `29327985997`. The H5 local
record was `193` frontend tests and `566 passed, 23 skipped` backend tests;
CI closed unit, frontend, service-backed, and no-skipped jobs.

## Schema Family

| Artifact | Schema | Responsibility |
|---|---|---|
| reciprocal lattice | `phase10i.reciprocal_lattice.v1` | structure/cell binding, standardized primitive basis, transformations, reciprocal matrix |
| first Brillouin zone | `phase10i.brillouin_zone.v1` | closed Wigner-Seitz polyhedron and topology |
| high-symmetry path | `phase10i.kpath.v1` | points, aliases, variants, segments, discontinuities, provider policy |
| package manifest | `phase10i.brillouin_zone_manifest.v1` | hashes, capabilities, JSON-only entry point, inert security state |
| tolerance policy | `phase10i.tolerance_policy.v1` | independent fixed numeric tolerances |

All artifacts use exact field allowlists, canonical JSON, SHA-256 content
identity, hard caps, and application-owned security flags. Geometry and a
high-symmetry path are separate artifacts because the primitive reciprocal
lattice uniquely determines the first BZ, while path choice depends on an
explicit provider convention and time-reversal policy.

## Data Flow

```text
periodic real lattice (rows, angstrom)
  -> validated standardized primitive real lattice
  -> B = 2*pi*A^-T (rows, angstrom^-1)
  -> first reciprocal Wigner-Seitz cell
  -> canonical vertices / edges / oriented faces
  -> optional provider-declared high-symmetry points and paths
  -> inert JSON-only package manifest
```

The contract builder accepts already selected source and primitive cells. Cell
standardization and provider calls are future adapter responsibilities. The
fixture generator uses local pymatgen only to produce bounded face inputs;
NumPy/SciPy independently reconstruct reciprocal matrices, Voronoi topology,
convex hulls, and volumes for evidence.

## Compatibility

The reciprocal convention is identical to Phase 10H: fractional phonon
q-points multiply a physics-`2*pi` reciprocal basis, and a lattice image phase
is `2*pi*q_fractional.image`. Phase 10H spells path distance
`radian_per_angstrom`; Phase 10I spells Cartesian reciprocal length
`angstrom^-1`. Compatibility recognizes this explicit schema-level naming
equivalence only when convention, primitive lattice hash, structure identity,
and selected path endpoints also match.

## Handoff

Phase 10I-1 may add a bounded adapter only after it validates source structure
scope, standardization metadata, provider policy, artifacts, and hashes against
this family. A renderer remains a later Phase 10I-2 concern and must consume
validated artifacts without adding executable content or external resources.

## Known Limits

- Three-dimensional periodic ordered structures are the reference scope.
- Magnetic path conventions, partial-occupancy path semantics, irreducible
  wedges, integration meshes, user paths, electronic calculations, Fermi
  surfaces, 2D/1D BZs, and non-periodic molecules are not implemented.
- Provider-derived path labels are metadata, not geometry authority.
- General transforms are finite decimal matrices with explicit direction and
  tolerance-checked round trips; exact rational encoding remains deferred.
