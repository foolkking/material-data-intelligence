# Agent-2.0 Phase 14 — Full Platform Integration & Production Qualification

This document persists the user-authorized Phase 14 execution prompt. It is
the authoritative Phase 14 task and covers integration, same-stack
qualification, cross-surface continuity, security, responsive browser
evidence, regression, and exact-SHA release closure. It does not authorize
Phase 15 or a new scientific architecture.

## Ordered stages

1. Normalize and verify the sealed Phase 13 provenance. Record
   `PHASE13_SEALED_BASE = 56c096a98d082f2ee145c4a1ca4fd89b8d4538df`; do not
   reopen Phase 13.
2. Build `docs/agent2/phase14/PHASE14_COVERAGE_MATRIX.md` covering every
   supported surface and transition from authentication/project/data through
   ResearchTurn, execution, Result, Presentation, Viewer, Evidence, Report,
   History, archive/restore, reuse, security, desktop/mobile, services, and
   CI.
3. Qualify the real same-stack runtime: authenticated browser, frontend, API,
   PostgreSQL, Redis, MinIO, real workers, and configured provider. Health
   output must reflect actual runtime configuration.
4. Repair only evidence-backed integration seams. Preserve the frozen
   authorities: ScientificObject logical identity, immutable
   ScientificObjectVersion, ScientificResult fact authority, deterministic
   presentation, exact historical references, trusted Capability Packs,
   project authorization, archive safety, and Viewer zero-recompute.
5. Qualify the canonical end-to-end journeys: ingestion/versioning, Dataset
   query and sample handoff, Structure, Electronic, historical v1/v2,
   archive/restore, Result reuse, Project History/resume, Viewer,
   Figure/Table, Evidence, and Report.
6. Run authenticated browser evidence at 1280x720 and 390x844; run real
   PostgreSQL/Redis/MinIO service-backed integration; inspect DB/worker/queue
   health; run repeated-flow stability and failure/negative paths.
7. Run fresh Phase 1–13, Phase 14 focused, backend/frontend, typecheck,
   production build, compileall, lock, Ruff, and diff checks. Mandatory paths
   may not be hidden behind skips.
8. After every mandatory gate is green, create P14-A with only legitimate
   Phase 14 changes, obtain exact-SHA CI, then create P14-B containing final
   evidence and obtain exact-current-head CI. Preserve unrelated user files.

## Frozen invariants

```text
duplicate scientific authority = NO
in-place scientific mutation = NO
silent latest substitution = NO
raw Tool exposure = NO
presentation != scientific fact authority
Viewer navigation does not recompute science
archive/restore creates no ScientificObjectVersion
```

Do not add new scientific algorithms, Agent architecture, Result authority,
Viewer architecture, public plugins, arbitrary Pack UI, collaborative editor,
notebook, office suite, or Phase 15 scope. If an external blocker is genuine,
report exact evidence and stop truthfully.

## Required evidence

Create `AGENT2_PHASE14_RESULTS.md` only when evidence is mature. It must
include the Phase 13 seal, authority map, coverage matrix, runtime topology,
Data/Agent/Capability/Result/Presentation/Viewer/Evidence/Report/History
qualification, version/archive/reuse and zero-recompute proofs, browser and
service-backed counts, DB/resource health, security, regression, P14-A,
P14-B, final HEAD/origin/master, and remaining gaps.

Final success is allowed only when:

```text
FUNCTIONAL_PHASE14_CLOSURE = PASS
AGENT2_PHASE14 = COMPLETE
FULL_PLATFORM_INTEGRATION = COMPLETE
PRODUCTION_QUALIFICATION = PASS
READY_FOR_PRODUCTION_RELEASE = YES
```
