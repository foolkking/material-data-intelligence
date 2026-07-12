# Periodic Bond Schema Decision

Decision: introduce `viewer_scene.v2` / `phase10f18.viewer_scene.v2` and retain v1 unchanged.

Each v2 bond has strict `id`, nested `from` and `to` endpoints, `displacement_cartesian`, `distance_angstrom`, allowlisted `source`, and `authoritative`. The source endpoint is normalized to image `[0,0,0]`; the target image is relative. A v1 optional extension was rejected because an old consumer could ignore offsets and draw a scientifically wrong edge.

v1 remains valid and is mapped as `legacy_same_cell`; it never acquires inferred periodic topology.
