# Phase 10N-4 MSD Contract

Tool: `trajectory.msd@0.1.0`. Artifact: `phase10n4.trajectory_msd.v1`. Estimator: `mdi.multiple_time_origin_msd@1.0.0`, NumPy `2.4.6`.

For lag `k`, selected origins are `0, origin_stride, ...` up to `max_origins_per_lag`. Cartesian displacement is calculated from the validated unwrapped trajectory. Directional MSD is the mean of squared x, y, or z displacement across selected atoms and origins; total MSD is their sum. Output contains exact lag time in ps, total and Cartesian directional MSD in angstrom squared, atom identity set, and origin count per lag.

Species selection uses formal trajectory species identity. Drift correction is frozen to `none`; no mass or isotope inference occurs. Variable-cell trajectories, missing time, identity/species changes, ambiguous wrapping, and fewer than three timed frames are typed ineligible. x/y/z are Cartesian axes, not crystallographic a/b/c.
