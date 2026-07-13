# Phase 10H Phonon DOS Schema

`phase10h.phonon_dos.v1` uses a strictly increasing one-dimensional THz sample-point grid. Negative grid values are allowed and retain imaginary-region weight. `total_dos` is nonnegative `modes_per_terahertz` and must integrate approximately to `3N` by the trapezoidal rule within the declared bounded tolerance.

Projected series are deterministically indexed and use either exact atom identity (`atom_index` plus matching species) or exact species identity. Display labels never define identity. A source may declare that projections sum to total DOS; mismatches then produce a warning without rewriting data.

Broadening metadata is closed to `none`, `gaussian`, or `source_defined`. The validator records but never performs smoothing, broadening, resampling, mirroring, clipping, or normalization.
