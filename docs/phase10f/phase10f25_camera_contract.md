# Phase 10F-25 Camera Contract

The perspective camera supports five application-owned presets: `default`,
`top`, `front`, `side`, and `isometric`. Every preset derives its target and
distance from the deterministic current-scene camera frame. `top` uses a Y-up
vector; other presets use Z-up. Transitions are immediate, which satisfies
reduced-motion policy without an animation loop.

`phase10f25.viewer_view_state.v1` stores finite position, target, up vector,
zoom, preset, clipping state, cell visibility, and source scene identity. It is
inert local JSON. Coordinates are bounded to magnitude 1,000,000 and zoom to
the finite interval `(0, 100]`. Replay rejects scene identity mismatches and
does not deserialize Three.js objects, matrices, functions, or callbacks.
