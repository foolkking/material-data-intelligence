# Phase 10N-4 Scope: Trajectory RDF / MSD / Diffusion

Status: `REVIEWER_GATE / NOT QUEUED / NOT EXECUTABLE`.

N4 consumes the exact `phase10g.trajectory.v1` resource. Proposed tools are
`trajectory.rdf`, `trajectory.msd` and `trajectory.diffusion_fit`. Static
`structure.rdf` remains a foundation and is not relabeled whole-trajectory RDF.

Eligibility requires constant atom count, stable atomRef/order and species identity,
ordered frames, explicit periodic cell and explicit time/unit for MSD/diffusion.
Variable species and reactive trajectories are unsupported. Variable-cell trajectories
are accepted only for RDF display under a declared per-frame-cell policy and are rejected
for MSD/diffusion until separately validated. Missing time may support frame-only Viewer
display but not diffusion. Irregular time is allowed with exact time-aware regression.

MSD uses server-side periodic unwrapping before displacement. Wrapped coordinates are
never fitted directly. Drift/center-of-mass correction and dimensionality are explicit
parameters. Directional MSD records the chosen lattice/Cartesian basis. Diffusion emits
estimate, angstrom^2/picosecond, fit window, slope/intercept, R2, sample count, coverage
and warnings; insufficient span/frames or diagnostics yields no estimate.

Artifacts include whole/time-window/species-pair RDF, MSD series, directional MSD and
fit diagnostics with exact atom/frame/time identities. Workspace plots link exact
trajectory/atom/frame selection and provide tables. Interpretation uses "estimated
diffusion coefficient over the selected fit window" and cannot confirm a diffusive regime
without sealed diagnostics.

Caps: 20,000 frames, 20,000 atoms/frame, 64 species pairs, 32 windows, 8,192 bins and 64
fit candidates. NumPy/SciPy suffice; no new dependency, API, table or migration is
proposed.
