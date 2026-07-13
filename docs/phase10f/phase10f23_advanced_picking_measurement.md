# Phase 10F-23 Advanced Picking and Measurement

The validated Three.js viewer now raycasts both instanced atoms and the bounded
shared bond `LineSegments`. Atom identity remains `siteIndex@[imageOffset]`;
bond identity is the emitted canonical/derived bond id with exact periodic
endpoints. Selection is ordered and capped by mode at one through four points.

`N` selects the next deterministic displayed atom, `B` selects the next emitted
bond, Backspace undoes one point, and Escape clears. Selection creates only
fixed highlight and measurement geometry and never changes scene topology.
