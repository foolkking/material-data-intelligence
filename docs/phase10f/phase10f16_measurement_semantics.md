# Phase 10F-16 Measurement Semantics

- Distance: Euclidean distance between two displayed Cartesian positions, Å.
- Angle: A-B-C with B as vertex, degrees in `[0, 180]`.
- Dihedral: signed A-B-C-D result in `[-180, 180]` degrees.
- Display precision: three decimal places; calculations retain JavaScript number precision.
- Degenerate zero-length vectors return `DEGENERATE_MEASUREMENT`.
- NaN/Infinity return `INVALID_COORDINATE`.

Measurements use positions represented in the current canonical viewer scene.
Minimum-image periodic correction and periodic image selection are not implemented.
