# Phase 10F-14 Renderer Lifecycle

Each engine owns one canvas and removes only that canvas. This ownership rule prevents React 19 development Strict Mode stale cleanup from deleting a newer renderer instance.

Disposal removes OrbitControls and context listeners, disconnects resize observation, removes the window resize listener, disposes shared geometries and all materials, disposes the WebGLRenderer, loses the context, clears Three scene references and removes the owned canvas. Tab switching and artifact replacement reinitialize to one canvas. Context loss enters a safe fallback and disposes the engine.
