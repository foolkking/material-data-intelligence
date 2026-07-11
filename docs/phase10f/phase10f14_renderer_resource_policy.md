# Phase 10F-14 Renderer Resource Policy

- sites: maximum 256
- bonds: maximum 2048
- species: maximum 32
- cell expansion: `[1, 1, 1]`
- JSON bytes: maximum 1,000,000
- pixel ratio: maximum 2
- sphere geometry: shared, 20 x 14 segments
- materials: shared by safe color
- lattice: exactly 12 line edges
- loop: demand-based, no animation frame loop
- resize: `ResizeObserver` plus window fallback
- hidden/unmounted surface: disposed because renderer exists only while its tab is mounted
- zero-size host: bounded 320 px fallback dimensions

Artifact values cannot control segments, antialiasing, pixel ratio, shader complexity, post-processing or animation rate.
