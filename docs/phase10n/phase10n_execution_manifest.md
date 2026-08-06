# Phase 10N Execution Manifest

Manifest status: `N0 COMPLETE / REVIEWER_APPROVAL_REQUIRED`; N1 is not executable.

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

## Traceability

| ID | Source | Test | Browser | Service | Evidence | Security | Exit gate |
| --- | --- | --- | --- | --- | --- | --- | --- |
| N0-A01 | M7 records | Git/queue/migration | replay | existing CI | baseline/git history | clean-state check | entry PASS |
| N0-A02 | lock/PyPI metadata | version/license parser | n/a | n/a | dependency matrix | license boundary | exact facts |
| N0-A03 | source/registry | inventory check | renderer inventory | existing fixtures | current matrix | no false implementation | complete table |
| N0-A04 | schemas/current source | identity/unit scan | selection contract | API schemas | identity/wording | inert data | seal complete |
| N0-A05 | N1 scope | fixture plan | future panel plan | future Adapter plan | n1 evidence | no chemical overclaim | reviewer approval |
| N0-A06 | N2 scope | dependency plan | overlay plan | future Adapter plan | n2 evidence | no oxidation inference | reviewer approval |
| N0-A07 | N3 scope | peak policy plan | plot/table plan | future Adapter plan | n3 evidence | bounded input | reviewer approval |
| N0-A08 | N4 scope | identity/fit plan | plot/table plan | future Adapter plan | n4 evidence | no direct wrapped MSD | reviewer approval |
| N0-A09 | N5 scope | supplied-output plan | Band/DOS plan | future Adapter plan | n5 evidence | no DFT execution | reviewer approval |
| N0-A10 | cross-cutting docs | caps/security check | inert fallback | generic persistence | policy evidence | complete markers | seal complete |
| N0-A11 | backlog/lock | sequence integrity | n/a | n/a | decision registry | no authority expansion | locked sequence |
| N0-A12 | all N0 docs | manifest/docs/secret | replay regression | full CI | manifest | no secrets | two CI commits |
