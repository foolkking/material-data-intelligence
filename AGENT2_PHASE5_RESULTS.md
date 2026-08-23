# AGENT2_PHASE5_RESULTS

## Verdict

**COMPLETE**

This closure keeps Phase 5 deterministic and stops before Phase 6. No
Scientific Interpreter, grounding validator, assistant final scientific
response, or Report Composer was added.

## Starting State

- Closure starting `HEAD`: `daa28914b9071a838b284707ce916ababcf1dbfa`.
- `origin/master` matched the starting HEAD.
- Alembic head: `0021_agent2_scientific_result_projection`.
- Existing `scientific_result_snapshots` remains the only result snapshot
  authority; no duplicate result table or migration was added.

## Scope

The closure adds an identity-only Redis/RQ result-projection wakeup, a fresh
result worker entry point, pending-turn reconciliation, production payload
adapters for the nine registered canonical projectors, and a dedicated
PostgreSQL/Redis/MinIO qualification. The Phase 4 execution worker remains the
Job/ToolCall/Artifact authority. Projection runs after the committed
`ExecutionSummary + RESULT_PENDING` transaction and can be retried from the
same `turn_id`.

Normal lifecycle:

```text
terminal Job
  -> committed ExecutionSummary + RESULT_PENDING
  -> enqueue {"turn_id": "..."}
  -> fresh result worker reloads PostgreSQL/MinIO facts
  -> immutable ScientificResultSnapshot
  -> RESULT_READY
```

`POST /api/research/turns/{turn_id}/project-result` remains an authorized
recovery/manual retry hook, not the normal production trigger.

## Canonical Production Artifact Matrix

All nine registered projectors were checked against the current implementation
schemas and fixtures. Numeric coverage means every declared summary field is
mapped only when present, with an artifact JSON locator and preserved unit.
Curves and large arrays remain structured data rather than scalar-fact floods.

| Projector | Production schema | Domain adapter | Numeric facts | Figure | Table | Evidence locators |
| --- | --- | --- | --- | --- | --- | --- |
| `agent2.structure.rdf` | `phase10e7.rdf.v1`, `phase10e7.static_chart.v1` | YES | FULL FOR DECLARED SUMMARY FIELDS | YES | YES | PASS |
| `agent2.diffraction.theoretical_xrd` | `phase10e4.xrd_pattern.v1`, `phase10e4.static_chart.v1` | YES | FULL FOR DECLARED SUMMARY FIELDS | YES | YES | PASS |
| `agent2.diffraction.experimental_theoretical_comparison` | `phase10n3.experimental_xrd_comparison.v1`, `phase10n3.experimental_xrd_comparison_plot.v1` | YES | FULL FOR DECLARED SUMMARY FIELDS | YES | YES | PASS |
| `agent2.ml.regression_evaluation` | `phase10k3.materials_ml_regression.v1` | YES | FULL FOR DECLARED SUMMARY FIELDS | N/A | YES | PASS |
| `agent2.trajectory.msd` | `phase10n4.trajectory_msd.v1`, `phase10n4.trajectory_plot.v1` | YES | FULL FOR DECLARED SUMMARY FIELDS | YES | YES | PASS |
| `agent2.trajectory.diffusion` | `phase10n4.trajectory_diffusion.v1`, `phase10n4.trajectory_plot.v1` | YES | FULL FOR DECLARED SUMMARY FIELDS | YES | YES | PASS |
| `agent2.phonon.band` | `phase10h.phonon_summary.v1`, band plot/table schemas | YES | FULL FOR DECLARED SUMMARY FIELDS | YES | YES | PASS |
| `agent2.phonon.dos` | `phase10h2.phonon_dos_summary.v1`, DOS plot/table schemas | YES | FULL FOR DECLARED SUMMARY FIELDS | YES | YES | PASS |
| `agent2.phonon.band_dos` | `phase10h.phonon_band_dos_summary.v1`, combined plot/table schemas | YES | FULL FOR DECLARED SUMMARY FIELDS | YES | YES | PASS |

No numeric fact is inferred from an image, filename, prose, or a second
peak-detection algorithm. Missing summary fields are omitted; unsupported
eigenvector/animation semantics remain explicit limitations.

## Fresh Service Qualification

Dedicated marker: `agent2_phase5_service`.

- RDF: **PASS**.
- XRD two-step: **PASS**.
- `selected skip = 0`.
- Real PostgreSQL, Redis, and MinIO were used. Phase 4 created the real
  terminal Job/ToolCalls/committed Artifacts in a separate execution worker.
  Two independent result-worker processes then reloaded only `turn_id` plus
  persistent authority. Concurrent RDF deliveries converged to one snapshot.
- A fresh API process returned the bounded Result view for the owner and
  rejected a different-project user.
- The saved 390x844 browser evidence is
  `docs/agent2/evidence/phase5_result_ready_390x844.png`: the result-ready
  Research surface rendered at `innerWidth=390`, `scrollWidth=390`, with no
  horizontal overflow.

## Determinism, Idempotency, and Safety

- Replaying the same production-shaped payloads produces identical semantic
  IDs, fact ordering, locators, and source fingerprints.
- Duplicate and concurrent projection deliveries create one authoritative
  snapshot; a same-version fingerprint conflict fails closed.
- Queue publication failure leaves the committed execution and
  `RESULT_PENDING` recoverable; it never creates a Job or marks execution
  failed.
- Projection-stage `StructuredLLMClient` calls: **0**.
- Projection-stage Job delta: **0**; ToolCall delta: **0**.
- ScientificResultSnapshot delta is one immutable row per qualified turn;
  assistant final message and grounded interpretation deltas remain **0**.
- `CURRENT`, `STALE`, `SOURCE_MISSING`, and `INVALIDATED` remain independent
  of `SUCCESS`/`PARTIAL` execution status and exact source versions never
  upgrade.

## Tests

- Phase 5 deterministic projector/contracts: **15 passed**.
- Queue/automatic-trigger closure tests: **5 passed**.
- Agent2 Phase 1-5 focused regression: **105 passed, 5 skipped**.
- Fresh service-backed Phase 5 qualification: **2 passed, selected skip 0**.
- Alembic migration test: **1 passed**.
- Full backend non-integration: **1691 passed, 6 skipped, 88 deselected**.
- Frontend Vitest: **85 files, 569 passed**.
- Frontend typecheck: **passed**.
- Frontend production build: **passed** using isolated `MDI_NEXT_DIST_DIR`.
- `compileall`, `uv lock --check`, and `git diff --check`: **passed**.
- `npm run lint`: not claimed; the repository still invokes deprecated
  interactive `next lint`.
- Closure implementation commit: `1fd18bf995ee6ffc38cbfacf6f5af1fca54a7b9f`.
- Authoritative pre-Phase-6 closure current-head CI run: `32617347658`; Unit, Service-backed
  Integration, Frontend Typecheck & Build, and Linux/Windows Scientific Replay
  all succeeded.

## Explicitly Not Implemented In Phase 5

Scientific Interpreter; Grounding Validator; Assistant Final Scientific
Response; long-session semantic memory; semantic retrieval; Report Composer;
Data Management mutations; full 62-tool Agent2 capability mapping;
professional Viewer expansion; Viewer linked-selection expansion;
Tool/plugin ecosystem; and the Phase 2 ORCHESTRATING lease/reaper.

## Remaining Authority

Phase 6 alone may consume `RESULT_READY` and create a grounded interpretation
or assistant final scientific message. Phase 5 never interprets facts or
claims that execution completion is a final research answer.
