# Phase 10F-14 Renderer Implementation

The PlannerWorkbench now offers an experimental renderer only for canonical scene identity. The frontend validator then independently checks required fields, identity, security flags, forbidden content, finite numbers, geometry, caps, nesting, strings and serialized size before mapping.

The product frontend development and production start scripts use port `3050`; API default CORS allows `localhost:3050` and `127.0.0.1:3050`. Isolated browser evidence runners retain dedicated ports so they can replay without colliding with the product server.

Three.js renders shared-geometry atoms, optional bounded bond line segments and the 12 unit-cell edges. A deterministic perspective camera targets the scene bounds center. OrbitControls provides rotate, wheel zoom and pan; reset restores the exact initial camera. Unit-cell and bond toggles change renderer-owned objects only.

Scene JSON and Manifest remain available and are the default preview. Old Phase 10D schema stays JSON-only. No Tool Registry, planner, runtime or artifact contract semantics changed.
