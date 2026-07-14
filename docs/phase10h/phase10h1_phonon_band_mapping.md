# Phase 10H-1 Phonon Band Mapping

Phonopy lattice rows map to canonical real-space lattice rows. Reciprocal
fractional q-points retain source order; path distances are recomputed with the
Phase 10H physics `2*pi` helper in radian/angstrom. `segment_nqpoint` defines
contiguous canonical segments and a coordinate change between segment endpoints
sets `discontinuous_from_previous`.

Phonopy q-point-major frequencies are transposed once into branch-major arrays
without sorting. Version 1 requires exactly `3N` source-ordered branches.
Approved cm^-1 and meV source values use exact Phase 10H SI conversions to THz.
Negative signs are preserved. Labels are normalized only by the canonical
high-symmetry helper; missing labels are never invented. ASR, NAC, and
degeneracy uncertainty remain explicit warnings rather than corrections.
