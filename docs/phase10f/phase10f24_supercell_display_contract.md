# Phase 10F-24 Supercell Display Contract

- Representation: integer tuple `[a,b,c]`, each axis 1 through 3; default `[1,1,1]`.
- Origin: `positive_octant`; offsets satisfy `0 <= i < a`, `0 <= j < b`, `0 <= k < c`.
- Caps: 27 cells, 2048 displayed atoms, 8192 displayed bonds, 32 style groups.
- Input is strict: no strings, floats, non-finite values, custom matrices, callbacks, or offset lists.
- Outer boundary is `a*A, b*B, c*C`; canonical unit-cell and outer-boundary visibility are independent.
