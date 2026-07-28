# Phase 10K-2 Fixture Matrix

| Case | Input | Contract assertion |
| --- | --- | --- |
| Composition | Si, NaCl, repeated Si, invalid formula | occurrence semantics, canonical systems, invalid count, formula duplicates |
| Structures | two hash-identical Si structures and NaCl | lattice/density/site/symmetry aggregation and exact-hash duplicate |
| Properties | formation energy and band gap | units, finite-only statistics, histogram, missing/non-finite separation |
| Quality | duplicate explicit ID, invalid formula, missing and infinity | factual typed quality output and stable fallback sample references |
| Group comparison | explicit `split=train/test` | counts, chemistry overlap, property summaries, no row-order inference |
| Resource comparison | two profiled tables | exact resource binding and unit compatibility |
| Partial/empty | empty and formula-only tables | explicit unavailable states without fabricated semantics |
| Negative | missing resource/group, equal groups, over-cap row count | typed rejection before unbounded execution |
| Performance | 4, 5,000, and 100,000 rows | bounded output, at most 200 linked rows, artifact-byte cap |
| Browser | Chromium, Firefox, WebKit, 390x844 mobile | seven views, sample linkage, tables, responsive layout, zero network |

The committed evidence fixture is deterministic and scientifically small. The
100,000-row case is generated locally from four fixed formulas solely for the
near-cap performance measurement.
