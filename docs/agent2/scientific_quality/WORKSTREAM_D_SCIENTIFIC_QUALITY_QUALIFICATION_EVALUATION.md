# Workstream D — Scientific Quality, Qualification & Evaluation

状态：执行中
授权日期：2026-09-10
Canonical repository：`E:\1project\mdi-b0-5a1`

## Mission

Build scientific qualification on top of the completed Requirement →
Capability → Tool → Adapter → Artifact → ScientificResult platform. Structural
completeness remains distinct from scientific correctness. Workstreams A-C,
repository migration, public/runtime identities and scientific authorities are
not reopened.

## Required implementation

1. Reconcile each of the 17 registered Capabilities with its Adapter,
   scientific method/library, projector, tests, assumptions, units,
   limitations and existing evidence.
2. Extend the existing Capability qualification metadata with evidence-backed,
   version-aware states. A status may not exceed its linked reference,
   invariant, domain, interpretation and report evidence.
3. Define typed reference-case evidence with independent provenance,
   scientifically justified absolute/relative tolerances, units, conventions,
   applicability and limitations.
4. Generate a quality inventory/report from canonical Capability and evidence
   authorities; detect unsupported promotion, stale fingerprints, unknown
   units and incomplete evidence.
5. Reuse genuine Phase 10/11 and current evaluation evidence. Regression-only
   fixtures must remain labelled regression evidence.
6. Establish representative cross-family reference, invariant, negative,
   Adapter/Artifact/ScientificResult, interpretation and report evaluation.
7. Preserve exact ScientificObjectVersion, Artifact, Result and report
   provenance. Do not hide scientific errors behind broad tolerances.
8. Run focused tests and bounded canonical service-backed scientific paths.

## Required outputs

- `docs/scientific-quality/SCIENTIFIC_QUALITY_AND_QUALIFICATION.md`
- `docs/scientific-quality/ADDING_REFERENCE_EVIDENCE.md`
- generated machine-readable and human-readable quality inventory
- `python scripts/scientific_quality_report.py --check`
- focused evidence/test suite
- updates to `PROJECT_STATE.md`, persistent progress/board/changelog and
  `results.md`

## Completion gate

The final result must report qualification counts for all 17 Capabilities,
reference/invariant/domain-negative/interpretation/report case counts,
scientific defects found/fixed, remaining blockers, real-service coverage and
`READY_FOR_AGENT_AUTONOMY = YES | CONDITIONAL | NO`.

No push, deployment, remote release qualification, old-tree runtime, broad
architecture redesign or identity/schema changes are authorized.
