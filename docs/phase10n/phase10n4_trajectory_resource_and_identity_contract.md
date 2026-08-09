# Phase 10N-4 Trajectory Resource and Identity Contract

Status: `SEALED_FOR_N4_IMPLEMENTATION`.

The input authority is `phase10g.trajectory.v1`. An immutable `trajectory_id` is the canonical content identity. A frame is identified by `trajectory_id + frame_index`; an atom is identified by `trajectory_id + stable atom_id`. Atom ordering and species must remain invariant across all analyzed frames. Filename, MIME, viewer index, display label, nearest-coordinate tracking, and latest-resource lookup have no authority.

Coordinates use the explicit trajectory `coordinate_mode`, `position_unit`, and `position_wrapping`. Cell identity comes from `fixed_lattice` or the exact per-frame lattice. `periodic_boundary` is an exact three-boolean vector and may contain partial PBC. Physical time comes only from explicit frame times and the declared time unit.

Caps are 200 frames, 5,000 atoms, 2,000,000 RDF pair evaluations, 2,048 RDF bins, 2,048 MSD lags, 4,096 origins per lag, 10,000 diffusion fit points, 32 MiB per scientific Artifact, and the Registry timeout. No bulk backfill or read-time analysis is permitted.
