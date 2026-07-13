# Phase 10F-24 Supercell Performance Policy

Preflight computes cells, atoms, and exact visible replicated bonds before allocation. Up to 1000 atoms/4096 bonds is interactive; larger scenes within hard caps are degraded with DPR 1; over-cap requests are refused while retaining the current view. Atom instancing and shared bond buffers remain bounded. Expansion replaces buffers in one WebGL context; three browsers completed 20 serial cycles without context growth.
