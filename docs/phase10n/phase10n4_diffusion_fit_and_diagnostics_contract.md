# Phase 10N-4 Diffusion Fit and Diagnostics Contract

Tool: `trajectory.diffusion@0.1.0`. Artifact: `phase10n4.trajectory_diffusion.v1`. Input is exactly one persisted `phase10n4.trajectory_msd.v1` Artifact bound by ID, checksum, producer, trajectory hash, and parameter hash. Raw trajectory reads and MSD recomputation are forbidden.

An explicit inclusive `fit_start_time_ps` and `fit_end_time_ps` are mandatory. OLS uses `numpy.linalg.lstsq` under `mdi.explicit_window_ols_einstein@1.0.0`. Total `D=slope/6`; Cartesian directional `D=slope/2`; canonical unit is angstrom squared per picosecond.

Defaults are at least 5 fit points, 1 ps duration, 0.2 minimum origin coverage, 0.9 minimum R-squared, and log-log alpha in `[0.8,1.2]`. Status precedence is insufficient points, duration, coverage, non-positive slope, poor fit, insufficient signal, ballistic-like, non-diffusive, then `DIFFUSIVE_WINDOW_ACCEPTED`. Only the accepted status exposes a qualified estimate. No automatic fit-window optimization, clamping, or long-time bulk claim is permitted.
