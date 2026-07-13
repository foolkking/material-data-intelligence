# Coordinate and Lattice Policy

Coordinate mode is fixed for the complete trajectory: fractional or Cartesian. Cartesian positions are angstrom. Fractional positions use row lattice vectors:

`cartesian = f0*a + f1*b + f2*c`.

Wrapped fractional positions use `[0,1)` with `1e-9` validation tolerance. Unwrapped values are preserved exactly; the validator never wraps or unwraps. `unknown` cannot support continuity claims.

Fixed mode requires one top-level lattice and null frame lattices. Variable mode requires every frame lattice and forbids implicit carry-forward. Lattices are finite 3x3 row vectors in angstrom, with relative determinant threshold `1e-12` and maximum condition number `1e8`. PBC is explicitly all-periodic or all-nonperiodic; partial PBC is deferred.
