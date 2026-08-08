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

## Canonical Phase 10N-1 Acceptance Registry

The registry below is the only canonical N1 definition in this document. References
outside this section are informational and are not duplicate registry entries.

1. `N1-A01 BASELINE_AUTHORITY_ACCEPTANCE_AND_EXACT_CONTRACT_CLOSURE` - verify the N0
   lifecycle and decisions, entry baseline, exact acceptance registry, Tool IDs and
   versions, implementation contracts, documentation reconciliation and queue admission.
2. `N1-A02 DATAPROFILE_REGISTRY_PARAMETER_AND_ARTIFACT_CONTRACTS` - verify additive
   DataProfile 2.1, exactly two Registry entries, strict algorithm-specific parameter
   schemas, two unambiguous Artifact contracts, backward compatibility, and no
   unauthorized migration, API family, dependency or lockfile change.
3. `N1-A03 CRYSTALNN_COORDINATION_EXECUTION` - verify the exact locked CrystalNN
   algorithm, registered Adapter, bounded parameters, periodic-structure execution,
   per-site coordination, neighbor identities and weights, coverage, typed errors and
   reference fixtures.
4. `N1-A04 VORONOINN_COORDINATION_EXECUTION` - verify the exact locked VoronoiNN
   algorithm, registered Adapter, bounded parameters, periodic-structure execution,
   per-site coordination, neighbor identities, periodic images, distances and weights,
   pathological-cell errors and reference fixtures.
5. `N1-A05 EXACT_STRUCTURE_SITE_NEIGHBOR_PERIODIC_IMAGE_IDENTITY_AND_DETERMINISM` -
   verify exact structure identity, structure-bound site identity, periodic-neighbor
   identity, deterministic ordering, parameter hash, stable checksum and the absence of
   fuzzy, latest or index-only rebinding.
6. `N1-A06 ELIGIBILITY_PLANNER_PLANVALIDATOR_RUNTIME_PERSISTENCE_AND_NO_FALLBACK` -
   verify Profile, Eligibility, Planner, AnalysisPlan, PlanValidator, QueueWorkerRuntime,
   PostgreSQL, Redis and MinIO integration, partial/failure behavior, algorithm isolation,
   no fallback and no result substitution.
7. `N1-A07 WORKSPACE_STRUCTURE_VIEWER_SELECTION_AND_INSPECTOR_INTEGRATION` - verify
   Workspace coordination tables, Structure Viewer overlay, periodic-image rendering,
   canonical selection, URL restoration, Inspector, mobile and accessibility alternatives,
   and Viewer lifecycle cleanup.
8. `N1-A08 GROUNDED_INTERPRETATION_REPORT_RECIPE_AND_SCIENTIFIC_WORDING` - verify
   bounded interpretation facts, algorithm-qualified wording, disagreement disclosure,
   Report/Recipe provenance, no recomputation, no definitive-bond claims and no execution
   authority.
9. `N1-A09 REFERENCES_TOLERANCES_PERFORMANCE_ACCESSIBILITY_SECURITY_AND_SERVICE_EVIDENCE`
   - verify direct numeric fixtures, exact locked-version references, quantity-specific
   tolerances, small/medium/near-cap performance, Chromium/Firefox/WebKit/390x844,
   PostgreSQL/Redis/MinIO, accessibility, security, secret scan and evidence manifest.
10. `N1-A10 THREE_COMMIT_EXACT_SHA_LIFECYCLE_AND_N2_REVIEWER_GATE` - verify the
    implementation, completion-record and queue-archive commits and exact-SHA CI,
    restoration of `TASK_BLOCK_COUNT = 0`, and the Phase 10N-2 reviewer gate.

## Canonical Phase 10N-2 Acceptance Registry

1. `N2-A01 BASELINE_N1_AUTHORITY_AND_EXACT_CONTRACT_CLOSURE` - verify the N1 archive,
   exact N1 contracts, N2-R0 closure, one Tool, one Artifact family, decision compliance,
   acceptance reconciliation and queue admission.
2. `N2-A02 N1_COORDINATION_ARTIFACT_DEPENDENCY_AND_NO_RECOMPUTATION` - verify exact
   CrystalNN/VoronoiNN Artifact ports, checksums, structure/site/neighbor lineage,
   AnalysisPlan 0.2 binding, no neighbor rediscovery, no fallback and no substitution.
3. `N2-A03 LOCAL_ENVIRONMENT_GEOMETRY_CLASSIFICATION` - verify the bounded reference
   catalog, exact angular-spectrum method, classified/ambiguous/unclassified states,
   source-algorithm attribution, coverage, warnings and controlled fixtures.
4. `N2-A04 COORDINATION_POLYHEDRON_GEOMETRY_AND_DISTORTION` - verify exact persisted
   vertices/faces, deterministic convex hull, radial/angular distortion metrics, area,
   volume, units and honest degenerate/partial component states.
5. `N2-A05 EXACT_SITE_NEIGHBOR_POLYHEDRON_IDENTITY_AND_DETERMINISM` - verify immutable
   structure/site/source-Artifact binding, exact periodic images, canonical vertices and
   faces, parameter hash, stable ordering/checksum and no fuzzy/latest rebinding.
6. `N2-A06 PROFILE_ELIGIBILITY_PLANNER_PLAN_DEPENDENCY_RUNTIME_AND_PERSISTENCE` - verify
   DataProfile 2.1 reuse, Eligibility, clarification, Planner, PlanValidator, Runtime,
   PostgreSQL/Redis/MinIO, failure blocking, branch isolation and generic persistence.
7. `N2-A07 WORKSPACE_STRUCTURE_VIEWER_SELECTION_AND_INSPECTOR_INTEGRATION` - verify the
   environment/metric tables, persisted polyhedron overlay, N1/N2 exact selection,
   Inspector, URL restoration, mobile/accessibility fallback and lifecycle cleanup.
8. `N2-A08 GROUNDED_INTERPRETATION_REPORT_RECIPE_AND_SCIENTIFIC_WORDING` - verify bounded
   projector facts, source-algorithm disagreement disclosure, Report/Recipe lineage, no
   recomputation, no definitive-bond claims and no Recipe execution authority.
9. `N2-A09 REFERENCES_TOLERANCES_PERFORMANCE_ACCESSIBILITY_SECURITY_AND_SERVICE_EVIDENCE`
   - verify direct fixtures, quantity-specific tolerances, caps, browsers/mobile,
   accessibility, lifecycle, service-backed evidence, security and secret scans.
10. `N2-A10 THREE_COMMIT_EXACT_SHA_LIFECYCLE_AND_N3_REVIEWER_GATE` - verify implementation,
    completion-record and queue-archive exact-SHA CI, Registry 56, task count zero and
    Phase 10N-3 remaining a non-executable reviewer gate.

The N1 integrity target is exactly ten entries with zero missing, extra, duplicate,
conflicting or shorthand registry entries. Document-wide references are informational.
