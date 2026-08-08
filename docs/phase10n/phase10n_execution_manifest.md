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

## Canonical Phase 10N-1 Acceptance Registry

1. `N1-A01 BASELINE_AUTHORITY_ACCEPTANCE_AND_EXACT_CONTRACT_CLOSURE` - verify the N0 lifecycle and decisions, entry baseline, exact acceptance registry, Tool IDs and versions, implementation contracts, documentation reconciliation and queue admission.
2. `N1-A02 DATAPROFILE_REGISTRY_PARAMETER_AND_ARTIFACT_CONTRACTS` - verify additive DataProfile 2.1, exactly two Registry entries, strict algorithm-specific parameter schemas, two unambiguous Artifact contracts, backward compatibility, and no unauthorized migration, API family, dependency or lockfile change.
3. `N1-A03 CRYSTALNN_COORDINATION_EXECUTION` - verify the exact locked CrystalNN algorithm, registered Adapter, bounded parameters, periodic-structure execution, per-site coordination, neighbor identities and weights, coverage, typed errors and reference fixtures.
4. `N1-A04 VORONOINN_COORDINATION_EXECUTION` - verify the exact locked VoronoiNN algorithm, registered Adapter, bounded parameters, periodic-structure execution, per-site coordination, neighbor identities, periodic images, distances and weights, pathological-cell errors and reference fixtures.
5. `N1-A05 EXACT_STRUCTURE_SITE_NEIGHBOR_PERIODIC_IMAGE_IDENTITY_AND_DETERMINISM` - verify exact structure identity, structure-bound site identity, periodic-neighbor identity, deterministic ordering, parameter hash, stable checksum and the absence of fuzzy, latest or index-only rebinding.
6. `N1-A06 ELIGIBILITY_PLANNER_PLANVALIDATOR_RUNTIME_PERSISTENCE_AND_NO_FALLBACK` - verify Profile, Eligibility, Planner, AnalysisPlan, PlanValidator, QueueWorkerRuntime, PostgreSQL, Redis and MinIO integration, partial/failure behavior, algorithm isolation, no fallback and no result substitution.
7. `N1-A07 WORKSPACE_STRUCTURE_VIEWER_SELECTION_AND_INSPECTOR_INTEGRATION` - verify Workspace coordination tables, Structure Viewer overlay, periodic-image rendering, canonical selection, URL restoration, Inspector, mobile and accessibility alternatives, and Viewer lifecycle cleanup.
8. `N1-A08 GROUNDED_INTERPRETATION_REPORT_RECIPE_AND_SCIENTIFIC_WORDING` - verify bounded interpretation facts, algorithm-qualified wording, disagreement disclosure, Report/Recipe provenance, no recomputation, no definitive-bond claims and no execution authority.
9. `N1-A09 REFERENCES_TOLERANCES_PERFORMANCE_ACCESSIBILITY_SECURITY_AND_SERVICE_EVIDENCE` - verify direct numeric fixtures, exact locked-version references, quantity-specific tolerances, small/medium/near-cap performance, Chromium/Firefox/WebKit/390x844, PostgreSQL/Redis/MinIO, accessibility, security, secret scan and evidence manifest.
10. `N1-A10 THREE_COMMIT_EXACT_SHA_LIFECYCLE_AND_N2_REVIEWER_GATE` - verify the implementation, completion-record and queue-archive commits and exact-SHA CI, restoration of `TASK_BLOCK_COUNT = 0`, and the Phase 10N-2 reviewer gate.

## Canonical Phase 10N-2 Acceptance Registry

1. `N2-A01 BASELINE_N1_AUTHORITY_AND_EXACT_CONTRACT_CLOSURE` - baseline, R0 docs, contract integrity and queue evidence.
2. `N2-A02 N1_COORDINATION_ARTIFACT_DEPENDENCY_AND_NO_RECOMPUTATION` - ports, binding, lineage, checksum and no-recomputation evidence.
3. `N2-A03 LOCAL_ENVIRONMENT_GEOMETRY_CLASSIFICATION` - catalog, algorithm, ambiguity and fixture evidence.
4. `N2-A04 COORDINATION_POLYHEDRON_GEOMETRY_AND_DISTORTION` - vertices, faces, metric and degeneracy evidence.
5. `N2-A05 EXACT_SITE_NEIGHBOR_POLYHEDRON_IDENTITY_AND_DETERMINISM` - identity, ordering, hash and stale-rejection evidence.
6. `N2-A06 PROFILE_ELIGIBILITY_PLANNER_PLAN_DEPENDENCY_RUNTIME_AND_PERSISTENCE` - Profile, planning, runtime and service evidence.
7. `N2-A07 WORKSPACE_STRUCTURE_VIEWER_SELECTION_AND_INSPECTOR_INTEGRATION` - renderer, selection, browser/mobile and lifecycle evidence.
8. `N2-A08 GROUNDED_INTERPRETATION_REPORT_RECIPE_AND_SCIENTIFIC_WORDING` - projector, Report/Recipe and wording evidence.
9. `N2-A09 REFERENCES_TOLERANCES_PERFORMANCE_ACCESSIBILITY_SECURITY_AND_SERVICE_EVIDENCE` - reference, tolerance, cap, accessibility and security evidence.
10. `N2-A10 THREE_COMMIT_EXACT_SHA_LIFECYCLE_AND_N3_REVIEWER_GATE` - exact-SHA lifecycle, queue archive and N3 gate evidence.

| ID | Source scope | Test scope | Browser scope | Service scope | Security scope | Exit gate |
| --- | --- | --- | --- | --- | --- | --- |
| N2-A01 | R0 contracts | integrity | n/a | n/a | authority | contracts frozen |
| N2-A02 | N1 ports/runtime binding | dependency/negative | lineage | artifact checksum | no recomputation | exact binding |
| N2-A03 | geometry classifier | references/ambiguity | tables | persisted payload | inert inputs | classification honest |
| N2-A04 | hull/metrics | ideal/distorted/degenerate | overlay/table | persisted payload | bounded geometry | metrics exact |
| N2-A05 | identities | determinism/stale | selection restore | checksum/scope | no fuzzy binding | stable hashes |
| N2-A06 | planner/runtime | Plan 0.2/partial | running/partial | PostgreSQL/Redis/MinIO | no fallback | chain complete |
| N2-A07 | Workspace | renderer/selection | four-browser/mobile | API readback | no frontend science | accessible UI |
| N2-A08 | projector/report | facts/exports | Report/Inspector | persisted lineage | false-claim audit | delivery bounded |
| N2-A09 | evidence | full regression | lifecycle/a11y | zero skipped | secret scan | evidence complete |
| N2-A10 | lifecycle | lifecycle assertions | CI replay | CI services | N3 absent | verified archive |

## N1 Traceability

| ID | Source scope | Test scope | Browser scope | Service scope | Evidence scope | Security scope | Exit gate |
| --- | --- | --- | --- | --- | --- | --- | --- |
| N1-A01 | N0 decisions/R0 | contract integrity | n/a | n/a | entry/R0 | clean baseline | R0 PASS |
| N1-A02 | Profile/Registry/contracts | schema compatibility | Profile surface | generic persistence | contract samples | strict input | contracts exact |
| N1-A03 | CrystalNN Adapter | direct fixtures | result panel | runtime storage | CrystalNN results | bounded execution | complete |
| N1-A04 | VoronoiNN Adapter | direct fixtures | result panel | runtime storage | VoronoiNN results | pathological cells | complete |
| N1-A05 | identity seal | exact/deterministic | selection restore | checksum | identity records | no fuzzy/latest | exact identity |
| N1-A06 | planner/runtime | plan/failure/no fallback | job state | PostgreSQL/Redis/MinIO | runtime cases | scope isolation | integration PASS |
| N1-A07 | Workspace/Viewer | renderer/selection | browser/mobile/a11y | Artifact API | UI captures | inert payload | UI PASS |
| N1-A08 | projector/report | wording/provenance | report journey | immutable records | report/recipe | no execution | delivery PASS |
| N1-A09 | refs/caps/security | full matrix | all browsers | zero skipped | manifest | complete markers | evidence PASS |
| N1-A10 | lifecycle | lifecycle checks | CI replay | CI services | commit history | secret scan | verified archive |

## Canonical Phase 10N-3 Acceptance Registry

1. `N3-A01 BASELINE_THEORETICAL_XRD_AUTHORITY_AND_EXACT_CONTRACT_CLOSURE` - N2 baseline, existing theoretical XRD authority and R0 closure.
2. `N3-A02 EXPERIMENTAL_XRD_RESOURCE_PROFILE_UNITS_AND_SEMANTIC_VALIDATION` - resource/Profile/unit/wavelength validation.
3. `N3-A03 EXPERIMENTAL_PEAK_DETECTION_AND_DETERMINISTIC_NORMALIZATION` - locked detector and independent deterministic normalization.
4. `N3-A04 THEORETICAL_PEAK_BINDING_AND_BOUNDED_ONE_TO_ONE_PEAK_MATCHING` - exact theory binding and bounded one-to-one matching.
5. `N3-A05 EXACT_PEAK_IDENTITY_RESIDUALS_COVERAGE_AND_DETERMINISM` - identity, residual, unmatched, coverage and determinism evidence.
6. `N3-A06 ELIGIBILITY_PLANNER_PLANVALIDATOR_DEPENDENCY_RUNTIME_AND_PERSISTENCE` - dependency planning, runtime and persistence evidence.
7. `N3-A07 WORKSPACE_XRD_OVERLAY_SELECTION_TABLES_AND_INSPECTOR` - overlay, table, selection, Inspector and browser evidence.
8. `N3-A08 GROUNDED_INTERPRETATION_REPORT_RECIPE_AND_SCIENTIFIC_CLAIM_BOUNDARY` - bounded facts, Report/Recipe and wording evidence.
9. `N3-A09 REFERENCES_TOLERANCES_PERFORMANCE_ACCESSIBILITY_SECURITY_AND_SERVICE_EVIDENCE` - full scientific/product/security evidence.
10. `N3-A10 THREE_COMMIT_EXACT_SHA_LIFECYCLE_AND_N4_REVIEWER_GATE` - lifecycle, Registry 57, queue archive and N4 gate evidence.

## N3 Traceability

| ID | Source | Test | Browser | Service | Security | Exit gate |
| --- | --- | --- | --- | --- | --- | --- |
| N3-A01 | N2 archive and structure.xrd | R0 integrity | n/a | n/a | no reimplementation | R0 PASS |
| N3-A02 | resource/Profile contract | input/unit/negative | readiness states | resource identity | untrusted data | semantic PASS |
| N3-A03 | SciPy detector | fixtures/determinism | peak markers | runtime | no match tuning | detector PASS |
| N3-A04 | theory Artifact | matching/ties | overlay | exact binding | no phase search | matcher PASS |
| N3-A05 | identity seal | residual/coverage/hash | selection | checksum | no fuzzy/latest | exact result |
| N3-A06 | Registry/Plan 0.2 | planner/runtime/failure | job state | PostgreSQL/Redis/MinIO | scope isolation | chain PASS |
| N3-A07 | Workspace | tables/Inspector/selection | four-browser/mobile | readback | inert payload | UI PASS |
| N3-A08 | projector/report | facts/exports | report journey | lineage | false-claim audit | delivery PASS |
| N3-A09 | caps/security | full regression | a11y/lifecycle | zero skipped | secret scan | evidence PASS |
| N3-A10 | lifecycle | lifecycle assertions | CI replay | CI services | N4 absent | archive PASS |
