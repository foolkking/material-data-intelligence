# Lattice Math Policy

Canonical lattice vectors are rows: `cart = f0*a + f1*b + f2*c`. Translation is `xyz + i*a + j*b + k*c`.

All values must be finite. Inversion rejects determinants below `scale^3 * 1e-12` and Frobenius condition bounds above `1e8`. Singular and ill-conditioned lattices fail safely; the UI does not silently fall back to direct distance.
