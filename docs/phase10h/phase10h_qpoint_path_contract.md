# Phase 10H Q-Point Path Contract

Q-points retain source order and carry contiguous zero-based index, three reciprocal-fractional coordinates, optional canonical/source labels, segment index, and global cumulative distance.

Segments are disjoint contiguous index ranges. Adjacent source segments retain duplicated endpoints. A continuous boundary repeats the same endpoint coordinate; a discontinuity is explicit and excludes the gap from path distance. The first point of every later segment therefore has the preceding endpoint distance. Within each segment, every increment equals the reciprocal-Cartesian step derived from the validated lattice.

Common `GAMMA`, `Gamma`, `\Gamma`, and `G` labels normalize to `Γ`. Canonical labels are bounded inert text. HTML, script markers, URLs, and LaTeX execution are forbidden; `source_label` is provenance text only.
