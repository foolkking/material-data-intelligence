# Phase 10N-1 Coordination Contract

Status: implemented within the reviewer-approved N1 scope.

The two registered tools are `structure.coordination_crystalnn@0.1.0` and
`structure.coordination_voronoinn@0.1.0`. They use the locked `pymatgen 2026.5.4`
and `pymatgen-core 2026.5.18` APIs. CrystalNN and VoronoiNN are separate adapters,
separate artifact discriminators, and separate failure states. There is no comparison
Tool and no algorithm fallback.

Only periodic, finite, exact structure resources are eligible. The adapter validates
lattice, sites, occupancy/disorder, source identity, site caps, neighbor caps and
artifact caps before execution. Units are Angstrom for distances and exact integer
triplets for periodic images. Coordination values retain algorithm-specific semantics.

Scientific wording is limited to algorithm-derived coordination, CrystalNN-derived
coordination, VoronoiNN-derived coordination, and neighbor relations identified by
the selected algorithm. Definitive bonding and absolute coordination claims are not
available.

Comparison is a deterministic consumer-side presentation over two persisted results
from the same immutable structure. It never reruns an algorithm or creates a third
scientific authority.
