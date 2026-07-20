# Phase 10J-3 Scientific Semantics

| Product | Accepted source meaning | Unit | Product status |
| --- | --- | --- | --- |
| Electron density | positive electron number density | `electron/angstrom^3` | Ready |
| Signed charge density | explicit source signed electric charge | `elementary_charge/angstrom^3` | Ready when declared |
| Spin difference | source collinear magnetization difference | `bohr_magneton/angstrom^3` | Ready |
| Spin up/down | allowlisted collinear derivation | `electron/angstrom^3` | Ready when relationships validate |
| Non-collinear vector | source Cartesian magnetization components | source-defined | Deferred product |

The adapter preserves source-native fields. Derived channels have fixed
formula IDs `COLLINEAR_SPIN_UP_V1` and `COLLINEAR_SPIN_DOWN_V1`; their
relationships are validated with zero residual. The UI does not claim
oxidation state, valence, atomic charge, coordination, or an authoritative
electron count unless a future contract provides that reference.

VASP augmentation sections are detected and explicitly excluded from the
grid product with a bounded warning. This is visible provenance, not a hidden
correction. The product's grid integral is a full-cell numerical integral.
