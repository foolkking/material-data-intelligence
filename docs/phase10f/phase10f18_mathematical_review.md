# Periodic Bond Mathematical Review

Lattice vectors are row vectors and translated coordinates are `xyz + i*a + j*b + k*c`. Stored displacement is `to_xyz + lattice(to_image) - from_xyz`; stored distance must agree within `1e-5` angstrom.

Orthogonal boundary evidence gives `0@[0,0,0] -> 1@[1,0,0]`, distance `0.4`. The triclinic reference gives target image `[1,-1,1]`, distance `1.264391`. pymatgen supplies neighbor images; contract and frontend independently recompute geometry. Stable reverse canonicalization and self-periodic cases are unit tested.
