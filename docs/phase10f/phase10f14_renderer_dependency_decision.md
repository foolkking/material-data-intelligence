# Phase 10F-14 Renderer Dependency Decision

## Selected

- runtime package: `three@0.185.1`
- type package: `@types/three@0.185.1`
- license: MIT
- runtime transitive dependencies: zero
- install scripts: none for the installed runtime package
- runtime network requirement: none
- controls: locally bundled `three/addons/controls/OrbitControls.js`

## Rejected or Deferred

- React Three Fiber `9.6.1`: compatible with React 19 but adds reconciler and multiple runtime dependencies.
- MatterViz `0.4.2`: MIT, but its Svelte/Threlte/WASM dependency tree is not a minimal fit for the React PlannerWorkbench.
- custom WebGL: no dependency, but unreasonable shader/control/lifecycle ownership for this slice.

The package and lockfile changes are limited to Three.js and its development-only type graph. No post-install binary download, CDN, remote texture or runtime module import is required.
