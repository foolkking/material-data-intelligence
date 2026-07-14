# Phase 10I Reciprocal Lattice Convention

## Canonical Mathematics

Real-space lattice vectors are rows of `A`, real fractional coordinates are row
vectors, and `r_cart = r_frac*A`. The only canonical reciprocal basis is:

```text
B = 2*pi*(A^-1)^T
A*B^T = 2*pi*I
k_cart = k_frac*B
```

`A` is measured in angstrom, `B` and `k_cart` in `angstrom^-1`, and `k_frac`
is dimensionless. The crystallographic no-`2*pi` convention is not accepted in
canonical matrices.

## Cell Identity and Transforms

The reciprocal artifact binds source, standardized primitive, and optional
conventional real lattices by value and SHA-256. Every basis transform records
old/new roles and the fixed direction:

```text
A_new = M*A_old
r_new = r_old*M^-1
B_new = M^-T*B_old
k_new = k_old*M^T
```

The conventional-BCC fixture verifies all four identities and Cartesian
round trips. The BZ is always constructed from the standardized primitive
reciprocal basis, never directly from a larger conventional cell.

## Validation

Validation checks exact shape, finite bounded values, determinant relative to
lattice scale, condition number, reciprocal duality, reciprocal/real volume,
transform direction and round trip, source hashes, provider metadata,
versioned tolerances, canonical content hash, and inert security fields.

The determinant relative threshold is `1e-12`; the condition-number proxy limit
is `1e8`. Reciprocal duality and transform tolerances are independent. Singular
and ill-conditioned inputs fail with typed errors and never proceed to geometry.

## Phonon Phase Compatibility

For `R_cart=n*A` and `q_cart=q_frac*B`:

```text
q_cart.R_cart = 2*pi*(q_frac.n)
```

This is the exact Phase 10H-4/H-5 non-Gamma image phase. Neither contract adds
nor removes another `2*pi` factor.
