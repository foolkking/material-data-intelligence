# Phase 10I First Brillouin-Zone Polyhedron

## Definition

The first Brillouin zone is the Wigner-Seitz cell of the standardized primitive
reciprocal lattice, centered at the origin. For each nonzero reciprocal vector
`G`, its generating half-space is:

```text
x.G <= |G|^2/2
```

A face records its integer generator `hkl`, Cartesian generator, outward unit
normal, plane offset, oriented vertex loop, edge loop, area, and centroid.

## Canonical Identity

- Vertices are merged with a fixed reciprocal-space tolerance and sorted by
  Cartesian coordinates; IDs are `vNNN`.
- Faces use counter-clockwise winding viewed from outside, rotate their loop to
  the smallest vertex ID, and sort by generator then loop; IDs are `fNNN`.
- Undirected edges sort their endpoint IDs and then sort globally; IDs are
  `eNNN`.
- Serialization sorts object keys, forbids NaN/Infinity, and hashes the complete
  artifact excluding only its own `content_hash` field.

## Validation Invariants

The validator checks vertex/edge/face identity and order, face plane and
winding, edge and vertex incidence, two faces per edge, closed/manifold graph,
connectivity declaration, convex half-spaces, origin containment, central
symmetry, `V-E+F=2`, surface area, and:

```text
V_BZ = |det(B)| = (2*pi)^3/|det(A)|
```

Topology is never truncated. Over-cap geometry is rejected.

## References

| Real lattice | Reciprocal type | First-BZ solid | V/E/F |
|---|---|---|---|
| simple cubic | simple cubic | cube | 8/12/6 |
| BCC | FCC | rhombic dodecahedron | 14/24/12 |
| FCC | BCC | truncated octahedron | 24/36/14 |
| hexagonal | hexagonal | hexagonal prism | 12/18/8 |

The triclinic fixture additionally exercises general non-orthogonal planes and
produces 24/36/14 for its selected lattice. Independent SciPy Voronoi and
ConvexHull calculations verify counts, volume, convexity, and central symmetry
without calling the contract canonicalizer or validator.
