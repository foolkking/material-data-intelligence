# Phase 10N-3 References and Tolerances

Reference authority is the checked `structure.xrd` contract, locked SciPy 1.17.1 API and controlled synthetic peak series. Fixtures cover perfect/shifted/missing/extra/competing/zero-match patterns, wavelength mismatch, unit ambiguity, threshold bounds and near-cap behavior.

Identity/checksum equality is exact. Wavelength compatibility tolerance is `1e-6 angstrom`; default matching tolerance is `0.15 degree 2theta`, bounded to `[0.001,2.0]`. Residual and normalization regressions use `1e-12` absolute/relative floating tolerance. These are quantity-specific test tolerances, not refinement uncertainty claims.
