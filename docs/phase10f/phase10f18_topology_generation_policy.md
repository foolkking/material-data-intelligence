# Topology Generation Policy

The adapter uses pymatgen's bounded periodic neighbor list with the validated cutoff. Candidates are normalized, distances are recomputed from canonical coordinates plus the explicit lattice image, deduplicated, sorted, and capped.

Current emitted source is `distance_cutoff`, always `authoritative: false`. `explicit_input` is reserved by the contract for future trusted explicit connectivity. The graph represents emitted visual topology only: it is not bond order, valence, CrystalNN, VoronoiNN, or authoritative coordination chemistry.
