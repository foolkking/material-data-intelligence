# DOS Normalization

The canonical target is `total_modes`, with trapezoidal integral approximately
`3N`. A `total_modes` source is validated but not rescaled. A `unit_area`
source is multiplied by `3N/source_integral`; the identical scale applies to
all projections. Normalization is explicit and never inferred from the curve.
