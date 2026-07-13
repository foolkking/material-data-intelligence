# Phase 10H Reciprocal Convention

The real-space lattice is the row-vector matrix `A = [a; b; c]`, in angstrom. The canonical reciprocal lattice is

```text
B = 2*pi*(A^-1)^T
```

so `a_i dot b_j = 2*pi*delta_ij`. A reciprocal-fractional q-point `q = [h,k,l]` maps to Cartesian as `q_cart = q * B`, with unit `radian_per_angstrom`.

The validator rejects non-finite, singular, and excessively ill-conditioned lattices. It never guesses whether a source lattice contains `2*pi`; future adapters must convert explicitly. Tests compare cubic and triclinic results against independent NumPy inversion.
