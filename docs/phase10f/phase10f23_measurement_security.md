# Measurement Security

Raycast threshold `0.12`, movement threshold `5px`, selection cap `4`, and
history cap `20` are application-owned. Picking occurs only on pointer release;
there is no hover or continuous raycast loop. Highlight/measurement geometries
and materials are fixed, reused, and disposed.

`phase10f23.viewer_measurement.v1` is inert local JSON with no JavaScript, HTML,
URL, callback, shader, module, telemetry, structure mutation, or topology
mutation. Artifact content cannot configure callbacks, thresholds, shortcuts,
caps, overlays, or scientific formulas.
