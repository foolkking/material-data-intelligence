# Phase 10I Readiness

| Capability | Decision | Basis |
|---|---|---|
| reciprocal lattice contract | READY | fixed row-vector physics-`2*pi` convention, duality, volume, transforms |
| first BZ contract | READY | deterministic closed convex Wigner-Seitz topology |
| high-symmetry point contract | READY | safe identity, labels, aliases, coordinates |
| k-path contract | READY | provider-bound variants, segments, discontinuities, time reversal |
| manifest | READY | hash-bound JSON-only inert package |
| fixtures/references | READY | six fixture families and independent NumPy/SciPy checks |
| Phase 10H compatibility | READY | convention, structure, primitive hash, unit spelling, endpoint checks |
| security contract | READY | exact fields, scanner, caps, typed failures |
| production adapter | NOT_READY | intentionally deferred to Phase 10I-1 |
| Tool Registry / planner / runtime | NOT_REGISTERED | no execution authority added |
| Brillouin-zone renderer | NOT_READY | intentionally deferred to Phase 10I-2 |
| electronic/phonon BZ-linked product | NOT_READY | separate scientific/product phases required |

Phase 10I-1 may begin only after this contract's current-HEAD CI closure. It
must not reinterpret finite-decimal transformations, provider metadata, path
variants, or security fields, and it must not introduce network-backed
standardization.
