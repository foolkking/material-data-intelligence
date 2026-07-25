# Phase 10J-5 Scientific Semantics

## ELF Range

ELF is treated as a source-defined dimensionless real scalar normally bounded
by `[0, 1]`. Validation scans decoded source values and uses
`ELF_ORBITAL_DTYPE_SCALE_TOLERANCE_V1`:

```text
float32 tolerance = 64 * 2^-23 * max(1, |minimum|, |maximum|)
float64 tolerance = 256 * epsilon * max(1, |minimum|, |maximum|)
```

The states are `VALID_RANGE`, `NUMERIC_TOLERANCE_WARNING`,
`SOURCE_RANGE_ANOMALY`, and `INVALID_NON_FINITE`. Values are never clamped,
smoothed, denoised, or normalized. An ELF isosurface is a spatial level set;
it is not a basin, attractor, chemical bond, lone pair, shell, or atomic charge
classification.

## Orbital / Partial Density

`orbital_density` must be non-negative within the same dtype-aware tolerance.
The source field is not squared, converted to absolute value, or renormalized.
The full-cell integral is reported with the canonical field's own integral and
normalization semantics. It is not automatically occupancy, probability, or
one electron.

Current PARCHG and CUBE canonical metadata do not provide authoritative
band/k-point/orbital/occupancy/energy identity. The product therefore reports
`UNAVAILABLE` and “Source-defined partial density.” Filenames and display
labels are not scientific identity. Signed real orbital amplitude, complex
wavefunction phase, `|psi|^2` derivation, HOMO/LUMO, orbital character, and
orbital reconstruction are deferred by design.

## Presets and Structure Context

ELF presets are exact `0.50`, `0.70`, `0.80`, and `0.90`. Orbital presets are
application-owned low/medium/high contour heuristics at `0.10`, `0.25`, and
`0.50` of the validated source maximum; each remains an exact displayed source
isovalue and makes no normalization claim. Periodic structure context may be
shown as the source cell or a bounded `2x2x2` renderer-local overlay. It never
replicates or mutates the scalar field artifact.
