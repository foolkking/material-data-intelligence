# Phase 10M-4 Heavy Viewer and WebGL Lifecycle

Status: local browser acceptance passes; exact-SHA CI is pending.

## Ownership

The Workspace heavy-viewer lease is application-owned and enforces:

```text
MAX_ACTIVE_HEAVY_VIEWERS = 1
```

Only the active heavy panel may load its bundle, create a canvas/context,
construct scene resources, register observers/listeners, or start animation.
Acquiring a new lease releases the previous owner. Route and panel unmounts
abort pending requests and release the lease.

The existing specialized components continue to own their scene, camera,
controls, animation loop, ResizeObserver, event listeners, geometry, material,
texture, render target, renderer, and canvas cleanup. Structure and
Brillouin-zone engines explicitly call `forceContextLoss()` before renderer
disposal. Existing trajectory, phonon animation, and volumetric components keep
their reviewed lifecycle paths.

## Context Loss

`webglcontextlost` is handled as a typed viewer state. The Chromium browser
gate dispatches context loss against the real active structure canvas, observes
`context_lost`, retries, and verifies a newly rendered canvas without changing
the scientific payload.

## Local Browser Evidence

The current local browser replay records:

```text
Chromium heavy switches = 50
Firefox heavy switches = 3
WebKit heavy switches = 3
maximum active canvases = 1
remaining canvases after replay = 0
Chromium context-loss recovery = PASS
mobile active canvases = 1
```

Chromium is the full 50-cycle/context-loss lifecycle gate. Firefox and WebKit
provide cross-engine smoke coverage because browser engines retain different
internal context pools. These are development/browser acceptance measurements,
not production capacity claims. Exact-SHA browser CI remains pending.
