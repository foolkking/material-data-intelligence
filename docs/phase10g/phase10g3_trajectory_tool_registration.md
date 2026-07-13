# Phase 10G-3 Formal Trajectory Tool Registration

`structure.trajectory_viewer` is registered exactly once in `platform_builtin_manifest.yaml` using `TrajectoryViewerAdapter`. It accepts exactly one normalized `Trajectory` and emits the existing four inert contracts:

- `trajectory.json`
- `trajectory_summary.json`
- `trajectory_parse_report.json`
- `trajectory_manifest.json`

Strict params allow only playback speed, loop, 1-3 axis supercell, cell visibility, clipping, `performanceMode=auto`, and `bondMode=none`. Tool metadata truthfully declares stable fixed atom/species identity, fixed/variable lattice, wrapped/unwrapped display, playback, picking, current-frame measurement, bounded supercell, clipping, and camera controls.

Static-reference bonds remain `partial_ready`. Dynamic bonds, variable atom count, reactive trajectories, ensemble RDF, MSD, diffusion, editing, and video export are false. Artifacts contain no renderer, JavaScript, HTML, remote frames, or external assets.

`structure.trajectory_import` remains the planner-hidden normalization path. `structure.viewer_3d` remains the static structure viewer and is not an alias.
