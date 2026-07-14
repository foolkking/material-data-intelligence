# Phase 10H-2 DOS Source Scope

| Source | State | Boundary |
|---|---|---|
| Canonical `phase10h.phonon_dos.v1` | READY | Strict validation, no mutation |
| Phonopy total DOS text | READY | Exact frequency/total columns and explicit wrapper metadata |
| Phonopy projected DOS text | READY | Exact columns and ordered atom/species descriptors |
| Pymatgen serialized DOS | DEFERRED_BY_DESIGN | No stable repository serialization contract |
| Arbitrary CSV, pickle, archive, URL | REJECTED | No guessing, construction, expansion, or network |

Text is capped at 32 MB. Grid, projection, numeric, atom, metadata, and artifact
caps inherit the Phase 10H contract.
