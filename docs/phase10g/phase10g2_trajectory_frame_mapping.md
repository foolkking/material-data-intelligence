# Trajectory Frame Mapping

Cartesian coordinates pass through in angstrom. Fractional coordinates use the current valid row-vector lattice. Fixed trajectories use top-level lattice; variable trajectories use each committed frame lattice. Wrapped, unwrapped, and unknown coordinates are displayed unchanged; unknown emits `TRAJECTORY_VIEWER_WRAPPING_UNKNOWN`.

Frame mapping creates immutable CPU display data. GPU commits update existing instance matrices plus existing cell, boundary, and axes position attributes. Camera state is preserved unless the user invokes Fit current frame. Enabled clipping bounds are recalculated from the newly committed frame without accepting artifact-defined planes.

Picking is disabled while a requested frame is buffering. The inspector reads position, velocity, and force only from the current committed canonical frame and uses application-owned unit labels.
