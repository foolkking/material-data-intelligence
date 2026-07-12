# Mathematical Audit

The row-vector convention matches pymatgen and adapter output. Round-trip conversion, determinant/inverse checks, orthogonal, monoclinic/skewed, triclinic, ties, singular matrices, ill-conditioned matrices, angle anchors, and dihedral chains are tested.

The skewed fixture is a counterexample to treating independent fractional component wrapping as a universally correct minimum-image algorithm.
