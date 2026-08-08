# Task Queue

Phase 10N-2:
PASS / ARCHIVED_BY_VERIFIED_QUEUE_COMMIT

Phase 10N-3:
IMPLEMENTED / AWAITING_IMPLEMENTATION_CI

Phase 10N-4:
REVIEWER_GATE / AWAITING REVIEWER PROMPT

---TASK---
Task: Phase 10N-3 Experimental XRD Comparison + Peak Matching
Status: IN_PROGRESS
Baseline: N2 verified archive `4f5fa88354027a7b26842e9c71082fe567c84e13`; implementation CI `31258820229`; completion CI `31260256371`; archive CI `31261360100`; Registry 56; migration `0007_phase10m1_workspace_domain`.

N3-R0: Close the exact theoretical XRD authority, Experimental XRD Resource, DataProfile, units, wavelength, peak detection, deterministic one-to-one matching, Artifact, identity, tolerance, cap, security, and evidence contracts before production implementation. Add only `structure.experimental_xrd_comparison@0.1.0`; comparison, detection, and matching are not independent Tools. Add no dependency, API family, migration, or lockfile change.

Canonical acceptance registry:
N3-A01 BASELINE_THEORETICAL_XRD_AUTHORITY_AND_EXACT_CONTRACT_CLOSURE
N3-A02 EXPERIMENTAL_XRD_RESOURCE_PROFILE_UNITS_AND_SEMANTIC_VALIDATION
N3-A03 EXPERIMENTAL_PEAK_DETECTION_AND_DETERMINISTIC_NORMALIZATION
N3-A04 THEORETICAL_PEAK_BINDING_AND_BOUNDED_ONE_TO_ONE_PEAK_MATCHING
N3-A05 EXACT_PEAK_IDENTITY_RESIDUALS_COVERAGE_AND_DETERMINISM
N3-A06 ELIGIBILITY_PLANNER_PLANVALIDATOR_DEPENDENCY_RUNTIME_AND_PERSISTENCE
N3-A07 WORKSPACE_XRD_OVERLAY_SELECTION_TABLES_AND_INSPECTOR
N3-A08 GROUNDED_INTERPRETATION_REPORT_RECIPE_AND_SCIENTIFIC_CLAIM_BOUNDARY
N3-A09 REFERENCES_TOLERANCES_PERFORMANCE_ACCESSIBILITY_SECURITY_AND_SERVICE_EVIDENCE
N3-A10 THREE_COMMIT_EXACT_SHA_LIFECYCLE_AND_N4_REVIEWER_GATE

Scope: Consume the existing persisted `structure.xrd` Artifact. Do not reimplement theoretical XRD, shift patterns, refine lattice/structure, perform Rietveld or phase-fraction refinement, identify phases automatically, execute arbitrary code, access external networks, add LLM calls, or create an N4 task.

Lifecycle: implementation -> exact-SHA CI -> completion record -> exact-SHA CI -> remove this task only after verified archive CI. N4 remains reviewer gate and no N4 executable task may be created.
---END---
