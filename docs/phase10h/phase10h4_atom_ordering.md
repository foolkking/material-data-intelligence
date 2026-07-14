# Phase 10H-4 Atom Ordering

Each displacement record is bound to contiguous canonical atom index
`0..N-1`. Structure identity, atom count, and species must match the band at
every index. Species grouping, coordinate sorting, mass sorting, and silent
source reorder are forbidden. Partial occupancy/disorder is unsupported in v1
because stable identity and mass weighting are ambiguous.
