# Phase 10F-25 Cell Display Contract

The viewer distinguishes three independent display layers:

- canonical unit cell: 12 edges from the canonical lattice;
- renderer-local supercell boundary: 12 outer edges from the expanded display lattice;
- canonical lattice axes: one shared colored line geometry for a, b, and c.

Axes are disabled by default to preserve the established draw-call budget.
When enabled they add one geometry, one material, and one draw call. Textual
vector names and lengths provide a non-color equivalent. Internal per-cell grid
lines remain deferred to avoid duplicate line geometry and visual noise.
