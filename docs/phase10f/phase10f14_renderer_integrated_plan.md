# Phase 10F-14 Renderer Integrated Plan

## Outcome

Implement a minimal interactive renderer for canonical `viewer_scene.v1` artifacts while retaining the existing JSON and manifest preview. The renderer is a frontend display capability, not a new executable tool and not `structure.viewer_3d`.

## Candidate Review

| Candidate | Decision | Reason |
|---|---|---|
| direct Three.js | SELECTED | Smallest controllable API surface, local bundle, MIT, deterministic camera, OrbitControls, explicit disposal |
| React Three Fiber | REJECTED | Adds reconciler and React renderer abstractions beyond the minimal requirement |
| MatterViz | DEFERRED | Current package brings Svelte/Threlte, WASM and materials-widget coupling |
| custom Canvas/WebGL | REJECTED | Shader, controls, camera and compatibility maintenance would become project-owned |

## Frozen Flow

`Artifact API response -> JSON parser -> frontend canonical validator -> whitelist mapper -> immutable RenderScene -> Three engine -> Canvas/WebGL`.

## Layers

1. Artifact contract: unchanged inert `viewer_scene.v1`.
2. Validation and mapper: identity, security, finite numbers, caps, byte size, safe colors/radii and internal IDs.
3. Engine: atoms, bonds, lattice, deterministic camera, OrbitControls, resize, demand rendering and disposal.
4. React surface: tabs, states, controls, accessibility and JSON fallback.

## UI and Scope

The preview modes are `3D Renderer`, `Scene JSON`, and `Manifest`. The default remains Scene JSON so earlier browser evidence stays stable. Renderer controls are reset camera, unit-cell visibility and bond visibility. Trajectory, mutation, picking, measurements, phonon, Brillouin zone and formal `structure.viewer_3d` registration remain outside this phase.
