# DOS Integration Validation

Integration uses the trapezoidal rule on strictly increasing sample points.
Expected count is exactly `3 * atom_count`; accepted relative tolerance is
application-owned at 0.01. Material mismatch is
`PHONON_DOS_INTEGRAL_MISMATCH` before export.

The imaginary-region integral linearly clips only the crossing interval at
zero. It does not mutate points or make a final stability claim.
