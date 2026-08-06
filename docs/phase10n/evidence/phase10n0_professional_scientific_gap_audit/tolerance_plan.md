# Phase 10N-0 Reference Fixture and Tolerance Policy

## Reference hierarchy

Reference status must be one of `DIRECT_VERIFIED`, `OFFICIAL_DERIVED_VERIFIED`,
`SYNTHETIC_CONTROLLED`, `CROSS_LIBRARY_VERIFIED`, `MAPPING_ONLY`,
`EXTRACTION_REQUIRED`, `UNAVAILABLE`, or `FUTURE_SCOPE`.

| Phase | Required fixture | Planned status | Numeric authority |
| --- | --- | --- | --- |
| N1 | ordered/disordered periodic structures with CrystalNN and VoronoiNN site results | OFFICIAL_DERIVED_VERIFIED plus SYNTHETIC_CONTROLLED | exact locked pymatgen result, checked into inert JSON |
| N2 | tetrahedral/octahedral/distorted controlled structures | SYNTHETIC_CONTROLLED and CROSS_LIBRARY_VERIFIED | analytic reference geometry plus N1 neighbor identities |
| N3 | synthetic peaks, overlapping peaks, range mismatch and wavelength controls | SYNTHETIC_CONTROLLED | analytic peak locations and deterministic matching policy |
| N4 | wrapped single-particle walk, immobile lattice, linear controlled diffusion, irregular time | SYNTHETIC_CONTROLLED | analytic positions/MSD and independently checked fit |
| N5 | insulating, metallic, direct/indirect, spin and DOS fixtures | OFFICIAL_DERIVED_VERIFIED plus SYNTHETIC_CONTROLLED | supplied inert electronic arrays and expected classifications |

Every fixture record must include source, exact version, license, extraction method,
expected result, tolerance, provenance and whether executable code was required. Notebook,
script or screenshot content is never executed or accepted as numeric authority.

## Tolerance policy

| Quantity | Proposed tolerance type | Initial bound | Failure meaning |
| --- | --- | --- | --- |
| distance | absolute, angstrom | `1e-6` serialization; algorithm threshold separately explicit | identity/algorithm drift |
| neighbor weight | absolute + relative | `1e-8` / `1e-6` | locked-version regression |
| position | Cartesian and fractional absolute | `1e-6` | source/identity mismatch |
| angle | absolute degree | `1e-5` | geometry regression |
| peak match | absolute 2theta degree | parameter, default proposal `0.15` | unmatched under stated policy |
| electronic/frequency energy | absolute | `1e-6 eV` or source-specific declared unit | source or conversion drift |
| RDF/MSD | absolute + relative | `1e-8` + `1e-6` for controlled fixtures | numerical regression |
| diffusion fit | slope/intercept/R2 separate tolerances | fixture-specific, predeclared | fit implementation drift |
| deterministic order | exact | zero permutation unless tie-break is declared | nondeterminism |
| cross-platform floating point | ULP-informed absolute/relative | fixture-specific and documented | platform drift beyond allowance |

No tolerance may be selected after observing a failure merely to make a test pass. Silent
clipping, unbounded nearest matching, silent peak/frame deletion and omitted diagnostics
are prohibited. N1-N5 must ratify exact values against locked-version fixtures.
