# Phase 10H-5 Renderer, Lifecycle, and Performance

The existing direct `three@0.185.1` engine owns the WebGL renderer, camera, OrbitControls, instanced atoms, cell, bonds, picking, context loss, resize, and disposal. H5 adds bounded application-owned `LineSegments` for displacement vectors and trails. No material is created per atom, vector, or trail.

One `requestAnimationFrame` loop exists only while playing. It is cancelled on pause, hidden tab, reduced-motion activation, context loss, artifact change, and unmount. Dynamic phases call `updateDynamicScene`; they do not recreate canvas, WebGL context, camera, controls, atom geometry, or React surface. Selection preserves `PeriodicSiteRef`; artifact/mode initialization clears stale state.

Evidence records one canvas/context, nonzero draw calls and nonblank composited pixels in Chromium, Firefox, and WebKit. Mobile uses the same bounded package and responsive controls. Displayed atom/vector/trail caps are checked before allocation. Near-cap universal FPS claims are not made.

Bonds are optional non-authoritative structure-binding lines. They move with displayed atoms and are not chemical bond inference. Vector and trail geometry is display-only. PNG export remains the existing fixed-view engine capability but is not promoted as a new H5 artifact.
