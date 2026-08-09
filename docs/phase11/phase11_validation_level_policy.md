# Phase 11 Validation Level Policy

| Level | Meaning |
|---|---|
| V0 | Contract only |
| V1 | Runtime and Artifact verified |
| V2 | Controlled reference verified |
| V3 | Independent or official reference verified |
| V4 | Cross-platform reproducibility verified |

Required minimums are role-specific:

- scientific numeric and geometry: V2, with V3 where an authoritative independent reference is feasible;
- scientific classification: V2 plus bounded invariants;
- data intelligence and ML: V2 for quantitative outputs, with analytic metrics where feasible;
- presentation-only: V1 plus browser and accessibility evidence;
- product composition: V1 plus exact source and no-recomputation evidence;
- metadata or utility: contract, deterministic transformation, identity, security, and integration evidence.

Not every Tool must reach V4. A lower current level is an explicit gap, not an implicit failure or hidden PASS.
