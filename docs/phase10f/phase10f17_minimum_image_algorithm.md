# Minimum-Image Algorithm

The solver converts the fractional delta into an initial rounded image candidate, then enumerates Chebyshev shells through radius 4. It evaluates Cartesian norms and uses lexicographic image offsets for deterministic ties.

Exact bounded completion uses the lower singular-value bound `1 / ||A^-1||F`: once the best distance is below the lower bound for every unexplored shell, the result is proven. Candidate count is capped at 729. Otherwise the solver returns `PERIODIC_SEARCH_LIMIT_EXCEEDED`.

Orthogonal, skewed, and general triclinic cases are cross-checked against `pymatgen.core.Lattice.get_distance_and_image`.
