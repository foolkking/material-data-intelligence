# Phase 10F-21 Viewer Performance Hardening

The validated renderer now applies an application-owned performance decision
before engine creation. Small scenes remain interactive; near-cap scenes retain
all validated atoms and bonds while using DPR 1, disabled antialiasing, and a
low-power context preference; over-budget scenes are refused before WebGL.

Atom instancing and shared bond/lattice buffers remain the production path.
Render scheduling is demand-based with no animation frame loop. An explicit
generation token prevents stale async engines from replacing a newer scene.
Context loss disposes resources and offers controlled retry.
