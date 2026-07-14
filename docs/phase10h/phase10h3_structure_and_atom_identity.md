# Phase 10H-3 Structure and Atom Identity

Band and DOS inputs must have the same canonical structure identity, atom count,
and species at every atom index. Formula-only, species-set-only, and filename
comparisons are insufficient. Primitive/supercell lineage is checked from
canonical source metadata and is never inferred from array dimensions.

Atom projections remain bound to canonical atom indices and species. Species
projections retain declared identity. The composer does not reorder atoms,
merge projections, or fabricate a primitive-cell mapping.
