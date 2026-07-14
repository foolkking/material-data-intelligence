# Phase 10H-3 Frequency Conversion and DOS Jacobian

Canonical display frequency is THz. For `f_target = c * f_source`, density is
`D_target = D_source / c`; broadening width is multiplied by `c`.

Conversion validates finite ordered arrays, non-negative densities, shape
identity, positive factors, and trapezoidal integral invariance. It never sorts,
resamples, smooths, clips, or renormalizes a valid DOS. The report records the
factor, Jacobian, and integral before and after conversion.
