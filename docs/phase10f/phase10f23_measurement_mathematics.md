# Measurement Mathematics

Scientific values use validated Cartesian positions and row-vector lattice
translations, never screen coordinates. Distance is Euclidean norm; A-B-C uses
clamped dot-product acos; A-B-C-D uses signed atan2 projected around B-C.
Minimum image uses bounded lattice enumeration with deterministic offset ties.

Reference cases cover 4.0 A orthogonal distance, 0.4 A cross-boundary distance,
90 degree angle, 45/-90 signed dihedrals, self-periodic identity, triclinic
minimum-image fixtures, and singular/ill-conditioned rejection. Existing Python
pymatgen reference tests remain independent of frontend implementations.
