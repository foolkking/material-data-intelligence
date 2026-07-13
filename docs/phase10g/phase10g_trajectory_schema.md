# Trajectory Schema

The top-level contract is closed: unknown fields are invalid. Required sections describe schema/content identity, kind, coordinate/wrapping/lattice modes, PBC, canonical units, time, immutable atom records, frames, property availability, bounded metadata/provenance/warnings, and inert security flags.

Kinds are `molecular_dynamics`, `geometry_optimization`, `structure_sequence`, and `unknown_static_sequence`. MD requires at least two frames and physical time. A structure sequence may contain one frame. Partial periodicity and partial occupancy are deferred.

`trajectory_id` is `sha256:<digest>` of compact, sorted-key, ASCII JSON for the payload excluding `trajectory_id`. NaN/Infinity are forbidden. Summary contains counts/ranges only. Manifest lists trajectory then summary JSON with local byte sizes and SHA-256; executable and remote assets are forbidden.
