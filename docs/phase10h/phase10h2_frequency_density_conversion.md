# Frequency and Density Conversion

Canonical frequency is cyclic THz. Approved source units are THz, inverse cm,
and meV using exact SI constants already owned by Phase 10H.

For `f_target = c * f_source`, `D_target = D_source / c`. The same Jacobian is
applied to total and projected series, preserving `integral D(f) df`. The
adapter never sorts, deduplicates, resamples, smooths, clips, mirrors, or takes
absolute frequency values.
