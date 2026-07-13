# Phase 10F-25 Clipping Contract

`ViewerClipState` contains an enable flag and exactly three ordered planes:
X, Y, and Z. Each plane contains only an axis enum, a finite Cartesian position
in angstrom, and an enable flag. Positions are bounded by the current displayed
scene. At most three planes are active.

The visible half-space is `coordinate <= position`. Clipping is display-only:
it does not remove atoms or bonds, alter site indices or image offsets, infer
topology, or change measurement coordinates. Arbitrary normals, equations,
callbacks, shaders, artifact-defined limits, and artifact-defined plane lists
are rejected by design.

Three.js local clipping is applied to shared atom, bond, highlight, and
measurement materials. Plane objects are rebuilt only when controls change;
there is no per-frame or per-atom allocation. Ray intersections are filtered
against the same planes before atom or bond selection callbacks run.
