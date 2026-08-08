# Phase 10N-2 Scope: Local Environment + Coordination Polyhedra

Status: `APPROVED / IN_PROGRESS`.

## Exact Product Identity

N2 adds exactly one Tool, `structure.local_environment_polyhedra@0.1.0`, and one
scientific payload contract, `phase10n2.local_environment_polyhedra.v1`.
Registry count advances from 55 to 56. Environment classification, deterministic polyhedron geometry
and approved distortion metrics are one capability. Comparison is presentation-only.

## Scientific Authority

The Adapter consumes one exact persisted `phase10n1.crystalnn_coordination.v1` or
`phase10n1.voronoinn_coordination.v1` table Artifact plus its exact immutable Structure.
It validates Artifact ID/checksum, producer Tool/version, algorithm/version, parameter
hash, structure hash, site identities and periodic-neighbor identities. It never runs a
neighbor search, CrystalNN, VoronoiNN or ChemEnv coordination discovery and never falls
back to another algorithm.

The geometry method is `mdi.angular_spectrum_reference_match@1.0.0`. It compares sorted
pairwise cosines of normalized exact N1 neighbor vectors to a bounded reference catalog;
there is no permutation search. `scipy.spatial.ConvexHull` from locked SciPy 1.17.1
constructs scientific triangular faces server-side. Faces are unavailable with a typed
reason for fewer than four, coplanar, duplicate or degenerate vertices.

## Reference Catalog 1.0.0

The allowlist is `linear` (CN2), `trigonal_planar` (CN3), `tetrahedral` and
`square_planar` (CN4), `trigonal_bipyramidal` and `square_pyramidal` (CN5),
`octahedral` (CN6), `pentagonal_bipyramidal` (CN7), and `cubic` (CN8). Reference
vertices are fixed unit Cartesian coordinates. Identity is catalog/version plus geometry
ID/version; users cannot supply reference coordinates or executable geometry code.

## Parameters And Metrics

Strict parameters are `site_indices`, `geometry_reference_ids`,
`classification_max_distance`, `classification_tie_tolerance`, `include_faces`,
`max_evaluated_sites`, `max_neighbors_per_site`, `max_geometry_references_per_site`,
`max_polyhedron_vertices`, `max_faces`, and `max_output_bytes`. Unknown and non-finite
values are rejected and resolved defaults are hashed.

Production metrics are `geometryDistanceRms` and `geometryScore` (dimensionless),
`radialDistanceMean` and `radialDistanceSpread` (angstrom),
`bondLengthDistortionIndex` (dimensionless), `angularRmsDeviation` (degree),
`polyhedronVolume` (angstrom^3), and `polyhedronSurfaceArea` (angstrom^2). Geometry
distance is RMS difference between sorted pairwise cosines; score is
`max(0, 1 - geometryDistanceRms / 2)`. Classification is ambiguous when the two best
distances differ by at most the declared tie tolerance and unclassified above the
declared maximum distance.

## Identity, Caps And Integration

Environment identity binds N2 Artifact, exact structure/site, source N1 Artifact and
checksum, source algorithm, reference identity and N2 parameter hash. Polyhedron identity
additionally binds the canonical set of exact N1 neighbor relations and periodic images.
Face identity is the sorted vertex-identity triplet, never rendered vertex order.

Caps are 5,000 evaluated sites, 64 neighbors/vertices per site, 32 reference checks per
site, 128 faces per polyhedron, 16 MiB output and 180 seconds. Workspace surfaces are a
local-environment table, persisted polyhedron overlay, metrics table and Inspector with
table/text fallback. DataProfile remains 2.1. AnalysisPlan 0.2 owns N1 -> N2 binding.

Wording is limited to geometry-derived local environment, source-algorithm-derived
neighbor environment, persisted-neighbor polyhedron and distortion relative to the
stated reference. Definitive bonding, chemistry, hybridization, stability, bond valence
and oxidation-state inference are out of scope. No dependency, API family, table,
column, migration or lockfile change is authorized.
