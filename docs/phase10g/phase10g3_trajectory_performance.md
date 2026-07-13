# Phase 10G-3 Trajectory Performance Hardening

## Architecture

The formal viewer consumes a validated `phase10g.trajectory.v1` artifact and maps only the committed frame. One Three.js renderer, canvas, context, control set, atom instance buffer, and lattice/bond buffer set remain active. Frame changes update existing GPU data. The CPU cache stores mapped scenes only and is keyed by canonical trajectory identity plus frame index.

Rapid seeks use one application-owned pending slot. A new request replaces the pending index before its microtask runs; generation tokens reject stale work. Playback uses one bounded timeout, pauses when hidden or context-lost, and never uses artifact-provided fps/cache/tier values.

## Budgets

| Device/tier | Displayed instances | Coordinate values | FPS | Cache |
| --- | ---: | ---: | ---: | ---: |
| Desktop interactive | <= 384 | <= 300,000 | 30 | 7 frames / 16 MiB |
| Desktop degraded | <= 768 | <= 2,000,000 | 15 | 4 frames / 8 MiB |
| Mobile interactive | <= 192 | <= 150,000 | 15 | 3 frames / 4 MiB |
| Mobile degraded | <= 384 | <= 1,000,000 | 15 | 2 frames / 2 MiB |

Over either degraded bound is refused before WebGL initialization. Pending requests are capped at one, prefetch at zero, and active playback loops/canvases/contexts/measurement overlays at one.

## Hardening Result

- LRU eviction occurs before insertion, so observed frame/byte peaks cannot exceed configured caps.
- The currently committed frame is protected until a replacement frame commits.
- Cache identity rejects frames from another trajectory.
- Formal launch defaults are validated backend params and frontend-whitelisted values.
- Supercell instance multiplication participates in launch-tier preflight.
- Context retry restores one paused renderer; a prior retry-host bug is covered by tests.
- Mobile identity remains active in landscape and uses a standard device-width viewport.
- Large fallback DOM contains a bounded JSON summary; the complete artifact remains in the JSON tab.

## Acceptance

The 64-frame browser case converged to frame 63 with peak pending requests 1 and zero pending work. Ten play/pause cycles ended with zero active loops and stable geometry/material counts. Chromium 150, Firefox 128, and WebKit 18 each retained one canvas/context with no console, page, or external-network error. These are bounded environment observations, not universal FPS or hardware-memory claims.

Local indexed/chunked storage is `DEFERRED_BY_DESIGN`. Remote chunk streaming is not permitted.
