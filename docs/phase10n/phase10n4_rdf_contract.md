# Phase 10N-4 Trajectory RDF Contract

Tool: `trajectory.rdf@0.1.0`. Artifact: `phase10n4.trajectory_rdf.v1`. Algorithm: `mdi.trajectory_rdf_ase_mic_unordered_pair_density@1.0.0`, ASE `3.29.0` `ase.geometry.find_mic` for triclinic/partial-PBC minimum images and NumPy `2.4.6` for bounded histogram normalization.

For each included frame, unordered pairs are accumulated into deterministic linear bins. For shell volume `V_shell = 4*pi/3*(r_outer^3-r_inner^3)`, frame volume `V`, and eligible unordered pair count `N_pairs`, the denominator contribution is `N_pairs*V_shell/V`; `g(r)` is total observed bin count divided by the summed denominator. Same-species self pairs are excluded and counted once. `A-B` and `B-A` share one canonical sorted identity.

The canonical parameterization is `r_min_angstrom`, `r_max_angstrom`, and `bin_count`. Default range is `[0,2] angstrom` with 200 bins. Windows are whole, frame, or physical time; starts are inclusive and ends exclusive. Safe radius is half the minimum periodic interplanar spacing for every included frame. Output `r` is angstrom and `g(r)` is dimensionless. No static `structure.rdf` result is reused or relabeled.
