# Phase 10N-1 Scope: CrystalNN / VoronoiNN Coordination

Status: `REVIEWER_GATE / NOT QUEUED / NOT EXECUTABLE`.

## Proposed product

N1 adds server-side registered tools `structure.coordination_crystalnn`,
`structure.coordination_voronoinn` and a bounded comparison product. Algorithms are the
exact `pymatgen 2026.5.4` / `pymatgen-core 2026.5.18` `CrystalNN` and `VoronoiNN`
implementations. Final parameter defaults must be extracted from that locked source and
stored explicitly; library defaults may not remain implicit.

Input is an exact periodic structure resource with immutable structure/site identity,
lattice, fractional coordinates, species and occupancy. Disordered/partial sites are
either supported according to explicit algorithm policy or reported per site as
unsupported. No silent occupancy coercion is allowed.

## Artifact proposal

`phase10n1.coordination.v1` contains source/structure/site IDs and hashes, algorithm ID
and locked library version, parameter hash, center/neighbor site refs, periodic image
vector, distance in angstrom, weight, coordination number, coverage, diagnostics,
warnings, deterministic ordering, and inert security markers. A comparison Artifact
links two exact algorithm Artifacts rather than recomputing in the Viewer.

Static table/plot and Structure Viewer overlay consume this Artifact. Selection is exact
site/neighbor identity. Interpretation may say "algorithm-derived local coordination"
and may not say true chemical bond or absolute coordination truth.

## Existing foundation disposition

`structure.coordination_hist` remains a valid distance-cutoff product. It coexists and
may consume or compare against N1 outputs only through a future explicit contract; it is
not replaced, relabeled, or used as CrystalNN/VoronoiNN authority.

## Caps, errors and validation

Use N0 caps: 32 structures, 5,000 sites/structure, 1,000 neighbor candidates/site, two
algorithms and 50,000 retained rows. Typed errors include nonperiodic input, missing
lattice/site identity, unsupported disorder, algorithm failure, nonfinite result,
resource cap and timeout. Fixtures cover ordered crystals, periodic images, partial
occupancy, pathological Voronoi cells and deterministic ties.

No new dependency, public API, table or migration is proposed. Additive Profile 2.1 and
new Artifact/Registry contracts require reviewer approval in N1.
