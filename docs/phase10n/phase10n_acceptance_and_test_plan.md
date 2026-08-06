# Phase 10N Acceptance and Test Plan

This document is the temporary canonical source for the Phase 10N-0 acceptance registry
authorized by the reviewer. The registry is defined once below; later mappings refer to
these IDs and do not redefine them.

## Canonical Phase 10N-0 Acceptance Registry

1. `N0-A01 BASELINE_AND_REPOSITORY_FACT_AUDIT` - verify M7 archive, repository state,
   queue state, migration and absence of unapproved N1-N6 production code.
2. `N0-A02 DEPENDENCY_VERSION_LICENSE_AND_UPSTREAM_CAPABILITY_AUDIT` - audit locked
   versions, license evidence and exact-version upstream capability without changing lock.
3. `N0-A03 CURRENT_PROFESSIONAL_SCIENTIFIC_CAPABILITY_INVENTORY` - classify current
   tools, Adapters, Artifacts, Profiles, Viewers and delivery surfaces conservatively.
4. `N0-A04 IDENTITY_UNITS_AUTHORITY_AND_SCIENTIFIC_WORDING_SEAL` - seal identity, units,
   authority boundaries and allowed scientific language.
5. `N0-A05 N1_COORDINATION_SCOPE_SEAL` - define the CrystalNN/VoronoiNN coordination
   scope, inputs, outputs, limits, fixtures and integration boundary.
6. `N0-A06 N2_LOCAL_ENVIRONMENT_AND_POLYHEDRA_SCOPE_SEAL` - define local environment and
   coordination polyhedra scope without adding unapproved chemistry claims.
7. `N0-A07 N3_EXPERIMENTAL_XRD_COMPARISON_SCOPE_SEAL` - define experimental XRD input,
   peak detection/matching policy and explicit non-scope.
8. `N0-A08 N4_TRAJECTORY_ANALYTICS_SCOPE_SEAL` - define RDF, MSD, diffusion, identity,
   unwrapping, fit diagnostics and trajectory limits.
9. `N0-A09 N5_ELECTRONIC_BAND_AND_DOS_SCOPE_SEAL` - define supplied electronic Band/DOS
   consumption, identity, units, projections and prohibited calculation authority.
10. `N0-A10 CROSS_CUTTING_CONTRACT_REFERENCE_TOLERANCE_PERFORMANCE_AND_SECURITY_SEAL`
    - seal cross-cutting contracts, fixtures, tolerances, caps and inert-data security.
11. `N0-A11 N1_TO_N6_IMPLEMENTATION_SEQUENCE_ACCEPTANCE_AND_EXECUTION_LOCK` - lock the
    reviewer-authorized N1-N6 sequence, acceptance ownership and no-redesign boundary.
12. `N0-A12 AUDIT_EVIDENCE_DOCUMENTATION_EXACT_SHA_LIFECYCLE_AND_REVIEWER_GATE` - close
    audit evidence, documentation integrity, two-commit CI lifecycle and reviewer gate.

## Test ownership

| ID | Required test/evidence |
| --- | --- |
| N0-A01 | baseline, Git history, M7 ancestry and queue/migration checks |
| N0-A02 | lock parser, release metadata capture and license limitation report |
| N0-A03 | Registry/Adapter/Artifact/Profile/Viewer inventory and capability matrix |
| N0-A04 | identity/unit/wording audit and false-claim/security scan |
| N0-A05 | N1 scope, fixtures, tolerances and proposal consistency |
| N0-A06 | N2 scope, dependency and wording consistency |
| N0-A07 | N3 source/matching policy and no-refinement boundary |
| N0-A08 | N4 identity/unwrapping/fit policy and no-direct-wrapped-MSD boundary |
| N0-A09 | N5 supplied-output, reference and no-DFT boundary |
| N0-A10 | cross-cutting caps, security, fixture and tolerance checks |
| N0-A11 | sequence/backlog/lock/manifest consistency |
| N0-A12 | evidence manifest, docs links, secret scan, exact-SHA CI and completion record |

## Integrity result target

```text
expected = 12
implemented = 12
missing = 0
extra = 0
duplicate registry entries = 0
conflicting definitions = 0
canonical registry shorthand entries = 0
```
