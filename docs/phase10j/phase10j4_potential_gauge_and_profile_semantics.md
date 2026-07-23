# Phase 10J-4 Gauge and Profile Semantics

## Gauge

The allowlisted formulas are:

```text
POTENTIAL_SOURCE_NATIVE_V1: V_display = V_source
POTENTIAL_CELL_AVERAGE_ZERO_V1: V_display = V_source - mean(V_source)
POTENTIAL_SELECTED_POINT_ZERO_V1: V_display = V_source - V_source(r_ref)
```

All are display gauges. A constant shift preserves point differences,
gradients, standard deviation, and source-contour identity, while changing
displayed absolute values, RMS, and numeric isovalues. Each layer stores a
source isovalue and derives `displayed_isovalue = source_isovalue + shift`.
It is not a vacuum or Fermi reference. Source payload bytes are never rewritten.

## Sampling

Cartesian points are transformed into canonical grid-index coordinates using
the inverse row-step matrix. Periodic node grids wrap each neighboring index;
non-periodic affine grids clamp at the validated domain boundary. Eight finite
node samples are combined by trilinear interpolation. Point differences are
`V(B)-V(A)` and must be identical before and after a constant shift.

## Planar profiles

For each `lattice_axis_0/1/2`, the product computes the arithmetic mean over
the other two uniform grid indices. Positions are `index/n_axis` and path
length is that fraction times the corresponding lattice-vector length. In a
triclinic cell this is a lattice-axis path, not necessarily a Cartesian normal.
No smoothing, spline, convolution, macroscopic averaging, or vacuum-region
detection is applied. One application-owned Worker pass accumulates all three
raw profiles; the main thread applies only the constant display shift. Profiles
carry deterministic hashes. The chart, accessible table, and bounded 3D plane
overlay use the same profile index.
