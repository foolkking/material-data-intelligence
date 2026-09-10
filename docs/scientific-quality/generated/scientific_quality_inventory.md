# Generated Scientific Quality Inventory

> Generated from canonical Capability manifests and evidence-backed quality
> records. Structural completeness and scientific qualification are separate.

## Quality health

- Accepted: **YES**
- Capabilities: **17**
- Structural only: **0**
- Reference validated: **3**
- Domain validated: **6**
- External implementation semantics validated: **8**
- Reference cases: **9**
- Invariant cases: **8**
- Domain-negative cases: **17**
- Result projection cases: **2**
- Interpretation evaluation cases: **7**
- Report evaluation cases: **2**
- Inventory fingerprint: `09e7dc50e6a5bac59ad23b2c221b08caad9629477f49ad68e06f35bee191a3a0`

## Capability quality

| Capability | Qualification | Reproducibility | Evidence R/I/N/P/I/R | Reference authority | Status |
|---|---|---|---|---|---|
| `data.composition_space` | DOMAIN_VALIDATED | DETERMINISTIC | 1/1/1/1/3/2 | ANALYTICAL<br>CURATED_KNOWN_RESULT<br>SYNTHETIC_EXACT | VALID |
| `data.materials_explorer` | DOMAIN_VALIDATED | DETERMINISTIC | 1/1/1/1/3/2 | ANALYTICAL<br>CURATED_KNOWN_RESULT<br>SYNTHETIC_EXACT | VALID |
| `diffraction.experimental_theoretical_comparison` | REFERENCE_VALIDATED | DETERMINISTIC | 1/1/1/1/3/2 | ANALYTICAL<br>CURATED_KNOWN_RESULT<br>SYNTHETIC_EXACT | VALID |
| `diffraction.theoretical_xrd` | EXTERNAL_IMPLEMENTATION_SEMANTICS_VALIDATED | DETERMINISTIC | 0/0/1/1/3/2 | CURATED_KNOWN_RESULT<br>OFFICIAL_LIBRARY_SEMANTICS<br>SYNTHETIC_EXACT | VALID |
| `electronic.band_structure` | EXTERNAL_IMPLEMENTATION_SEMANTICS_VALIDATED | DETERMINISTIC | 0/0/1/1/3/2 | CURATED_KNOWN_RESULT<br>EXTERNAL_SOLVER_SEMANTICS<br>SYNTHETIC_EXACT | VALID |
| `electronic.dos` | EXTERNAL_IMPLEMENTATION_SEMANTICS_VALIDATED | DETERMINISTIC | 0/0/1/1/3/2 | CURATED_KNOWN_RESULT<br>EXTERNAL_SOLVER_SEMANTICS<br>SYNTHETIC_EXACT | VALID |
| `ml.regression_evaluation` | DOMAIN_VALIDATED | SEEDED_STOCHASTIC | 1/1/1/1/3/2 | ANALYTICAL<br>CURATED_KNOWN_RESULT<br>SYNTHETIC_EXACT | VALID |
| `phonon.band` | EXTERNAL_IMPLEMENTATION_SEMANTICS_VALIDATED | DETERMINISTIC | 0/0/1/1/3/2 | CURATED_KNOWN_RESULT<br>EXTERNAL_SOLVER_SEMANTICS<br>SYNTHETIC_EXACT | VALID |
| `phonon.band_dos` | EXTERNAL_IMPLEMENTATION_SEMANTICS_VALIDATED | DETERMINISTIC | 0/0/1/1/3/2 | CURATED_KNOWN_RESULT<br>EXTERNAL_SOLVER_SEMANTICS<br>SYNTHETIC_EXACT | VALID |
| `phonon.dos` | EXTERNAL_IMPLEMENTATION_SEMANTICS_VALIDATED | DETERMINISTIC | 0/0/1/1/3/2 | CURATED_KNOWN_RESULT<br>EXTERNAL_SOLVER_SEMANTICS<br>SYNTHETIC_EXACT | VALID |
| `structure.coordination_crystalnn` | EXTERNAL_IMPLEMENTATION_SEMANTICS_VALIDATED | DETERMINISTIC | 0/0/1/1/3/2 | CURATED_KNOWN_RESULT<br>OFFICIAL_LIBRARY_SEMANTICS<br>SYNTHETIC_EXACT | VALID |
| `structure.coordination_hist` | REFERENCE_VALIDATED | DETERMINISTIC | 1/1/1/1/3/2 | CURATED_KNOWN_RESULT<br>SYNTHETIC_EXACT | VALID |
| `structure.coordination_voronoinn` | EXTERNAL_IMPLEMENTATION_SEMANTICS_VALIDATED | DETERMINISTIC | 0/0/1/1/3/2 | CURATED_KNOWN_RESULT<br>OFFICIAL_LIBRARY_SEMANTICS<br>SYNTHETIC_EXACT | VALID |
| `structure.rdf` | REFERENCE_VALIDATED | DETERMINISTIC | 1/0/1/2/3/2 | CURATED_KNOWN_RESULT<br>SYNTHETIC_EXACT | VALID |
| `trajectory.diffusion` | DOMAIN_VALIDATED | DETERMINISTIC | 1/1/1/1/3/2 | ANALYTICAL<br>CURATED_KNOWN_RESULT | VALID |
| `trajectory.msd` | DOMAIN_VALIDATED | DETERMINISTIC | 1/1/1/1/3/2 | ANALYTICAL<br>CURATED_KNOWN_RESULT<br>SYNTHETIC_EXACT | VALID |
| `trajectory.rdf` | DOMAIN_VALIDATED | DETERMINISTIC | 1/1/1/1/3/2 | CURATED_KNOWN_RESULT<br>INDEPENDENT_IMPLEMENTATION<br>SYNTHETIC_EXACT | VALID |

## Issues

- None.

## Interpretation

- `REFERENCE_VALIDATED` means independent/analytical/curated reference evidence exists.
- `DOMAIN_VALIDATED` additionally requires invariants and negative applicability boundaries.
- `EXTERNAL_IMPLEMENTATION_SEMANTICS_VALIDATED` validates parsing, units, projection and limitations owned by this platform; it does not claim to validate the upstream solver/library.
- Evidence is stale when the qualified scientific contract fingerprint changes.
