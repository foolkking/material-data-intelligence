# Phase 10N-2 Geometry Reference Catalog

Catalog identity is `mdi.local_geometry_reference_catalog@1.0.0`. The fixed allowlist is:

| ID | CN | Fixed ideal vertices |
| --- | --: | --- |
| `linear` | 2 | opposite x-axis unit vectors |
| `trigonal_planar` | 3 | three equatorial unit vectors at 120 degrees |
| `tetrahedral` | 4 | normalized `(1,1,1)` sign pattern |
| `square_planar` | 4 | Cartesian `+/-x`, `+/-y` |
| `trigonal_bipyramidal` | 5 | trigonal equator plus `+/-z` |
| `square_pyramidal` | 5 | square plane plus `+z` |
| `octahedral` | 6 | Cartesian `+/-x`, `+/-y`, `+/-z` |
| `pentagonal_bipyramidal` | 7 | pentagonal equator plus `+/-z` |
| `cubic` | 8 | normalized cube corners |

References are MIT-licensed application constants derived from standard ideal Cartesian
geometry. Matching uses sorted pairwise cosines, so rotation and vertex permutation do
not alter the result. Unsupported coordination numbers remain unclassified.
