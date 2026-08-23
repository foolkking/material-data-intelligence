# AGENT2_PHASE5_RESULTS

## Scope

Implemented the Phase 5 deterministic production result-projection foundation:
`RESULT_READY`, migration `0021_agent2_scientific_result_projection`, typed
ScientificResultBundle components, canonical projector registry, stable source
fingerprints, immutable snapshot reuse/conflict handling, relevance evaluation,
authorized result/projection endpoints, and the minimal Research activity state.

Projectors read committed Phase 4 facts and injected/production Artifact
storage payloads. No execution authority was changed.

## Starting state

Starting HEAD and `origin/master`: `080350b870d646fa7e72d256c0607c554cc480f4`.
Alembic head before implementation: `0020_agent2_execution_integration`.
The local development database was at `0014` and was upgraded through the
full chain for qualification; it was not treated as the production baseline.

## Migration

`0021_agent2_scientific_result_projection` (down revision
`0020_agent2_execution_integration`) adds `RESULT_READY` to the existing
`research_turns` status constraint. No duplicate result table was created;
Phase 5 reuses `scientific_result_snapshots` and its existing immutable unique
identity `(research_turn_id, projection_version, source_fingerprint)`.

## Result contracts and projectors

The typed bundle now includes result items, facts, figures, tables, evidence,
methods, limitations, warnings and provenance with cross-reference validation.
Numeric facts require a concrete artifact/tool/object locator. Image-only
artifacts may produce a figure but produce zero numeric facts.

Registered canonical projector IDs:

- `agent2.structure.rdf`
- `agent2.diffraction.theoretical_xrd`
- `agent2.diffraction.experimental_theoretical_comparison`
- `agent2.ml.regression_evaluation`
- `agent2.trajectory.msd`
- `agent2.trajectory.diffusion`
- `agent2.phonon.band`
- `agent2.phonon.dos`
- `agent2.phonon.band_dos`

The first implementation uses bounded deterministic structured-payload
projection. It does not infer data from filenames, prose or images. Rich
domain-specific peak/metric extraction remains an explicit follow-up where a
current Artifact contract needs more specialized mapping.

## Lifecycle and API

`RESULT_PENDING → RESULT_READY` is persisted only after an immutable snapshot
is inserted. Projection failures leave execution facts and the turn retryable.
`GET /api/research/turns/{turn_id}/result` reauthorizes the project and returns
a bounded product view. `POST /api/research/turns/{turn_id}/project-result` is
an authorized deterministic processing hook.

Stored exact source references are never upgraded. Effective relevance is
evaluated as `CURRENT`, `STALE`, `SOURCE_MISSING`, or `INVALIDATED` at read time
without mutating the stored bundle.

## No-execution and no-LLM evidence

Projection code does not call `StructuredLLMClient`, create Jobs, create
ToolCalls, rerun tools, or create `ScientificResultSnapshot` rows through any
other path. It only inserts the one existing snapshot for a successful or
partial terminal execution. Assistant final messages and grounded
interpretations remain absent.

## Tests

- Phase 5 deterministic projector/contracts: **5 passed**.
- Focused Agent 2 Phase 1–4/API/migration regression: **55 passed, 1 skipped**.
- Alembic migration test (`0014 → head`, downgrade, upgrade): **1 passed**.
- Full non-integration backend: **1706 passed, 6 skipped, 56 deselected**.
- Frontend Vitest: **85 files, 569 passed**.
- `compileall` and `git diff --check`: passed.
- Frontend `npm run lint` was not declared passing because the repository still
  invokes deprecated interactive `next lint`.

Current-HEAD CI run `32611474526` passed Unit, PostgreSQL/Redis/MinIO
integration with no skips, Frontend test/typecheck/build and responsive
evidence, plus Linux/Windows scientific replay. The integration job validated
migration `0021` and legacy Agent2/runtime coverage, but it did not include a
dedicated fresh Phase 5 RDF/XRD projection worker qualification.

## Explicitly not implemented in Phase 5

Scientific Interpreter, grounding validator, final scientific response,
long-session semantic retrieval, Report Composer, Data Management mutations,
full 62-tool capability mapping, professional Viewer expansion, plugin
ecosystem, and the Phase 2 orchestration lease/reaper.

## Risks / open items

Current canonical projectors intentionally use structured-payload extraction
and should be specialized against each production Artifact contract before
claiming domain-complete metric coverage. Projection worker scheduling is
exposed as an authorized hook; durable automatic result-worker deployment and
dedicated Phase 5 service-backed qualification remain to be completed.

## Verdict

**PARTIAL** — deterministic Phase 5 foundation and local regression are in
place, but service-backed production qualification and full domain-specific
projector coverage were not completed in this turn.
