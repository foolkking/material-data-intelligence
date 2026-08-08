# Phase 10N-2 References And Tolerances

Controlled ideal fixtures cover linear, tetrahedral and octahedral references. Distorted,
ambiguous, periodic-image and coplanar/degenerate fixtures test honest component states.
Both CrystalNN- and VoronoiNN-derived N1 payloads are consumed without recomputation.

Exact equality applies to all identities, periodic images, reference IDs/versions and
checksums. Numeric tolerances are: vertex and source-distance `1e-6 angstrom`, pairwise
cosine/geometry score `1e-10`, angles `1e-7 degree`, distortion `1e-10`, volume
`1e-8 angstrom^3`, area `1e-8 angstrom^2`, and classification tie `0.01` by default.
These are contract checks, not a Phase 11 benchmark claim.
