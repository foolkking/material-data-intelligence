# Phase 13 Scientific Presentation 2.0 — Detailed Gap Scan

Date: 2026-08-27

This is a qualification audit, not a new architecture proposal. Phase 12 is
sealed at `49398ecfb630d83301a38a647b94ae5b97f55a59`; the audit below compares
the current worktree with `PHASE13_TASK.md`.

## Confirmed PASS

- Phase 12 Stage 0: P12-A `40ebb4d65c76ef0c44fdde2923c901c97efa2257`, CI
  `33038096797`; P12-B `49398ecfb630d83301a38a647b94ae5b97f55a59`, CI
  `33040374649`; both exact-SHA CI runs passed.
- ScientificObject/ScientificObjectVersion, exact source references, archive
  semantics, Dataset stable identity, and Phase 11 Pack authority remain
  frozen and regression-tested.
- Deterministic presentation contract and compiler exist in
  `apps/web/app/lib/scientific-presentation.ts` with bounded block kinds,
  exact source refs, numeric/unit passthrough, historical notices, and no
  execution hooks.
- Research and scientific-report routes reuse the compiler and safe block
  renderer; arbitrary HTML/JavaScript is rejected by the renderer boundary.
- Focused presentation tests: 7; Agent2 API tests covering bounded result
  facts/evidence/exact sources: 14; full frontend: 91 files / 591 tests;
  backend: 1810 passed / 83 skipped; typecheck, build, compileall, lock,
  Ruff, and diff checks pass.
- Authenticated Chromium archive/restore path passed on the canonical Data
  page; active/archived discovery filtering and exact object/version bypass
  are covered by ProductPages tests.

## PARTIAL / NOT YET QUALIFIED

| Gate | Current evidence | Status |
|---|---|---|
| Structure presentation | Compiler and Phase 12 Structure Result authority exist; no current-worktree browser capture shows the new `科学呈现` blocks for the canonical CrystalNN/VoronoiNN turn. | PARTIAL |
| Electronic presentation | Report/presentation code exists; current browser report list exposes only a legacy report and the inspected route rendered its legacy fallback, not the new projection. | PARTIAL |
| Dataset presentation | Dataset table and compiler unit coverage exist; no current same-stack browser run proves Result → presentation after the final changes. | PARTIAL |
| Historical v1/v2 presentation | Phase 12 exact source evidence is PASS; Phase 13 renderer-level browser proof after v2 is absent. | PARTIAL |
| Archived historical presentation | Exact Viewer API/route semantics are PASS; no Phase 13 presentation/report browser proof while archived. | PARTIAL |
| Result reuse presentation | No dedicated current test/evidence proves Job/ToolCall/Artifact/Result deltas remain zero when only presentation changes. | MISSING |
| Viewer no-recompute | Existing Viewer regressions cover renderer lifecycle; no Phase 13 end-to-end open-from-Result/Report delta capture. | PARTIAL |
| Scientific Report | `ScientificReportRoute` and `compileReportPresentation` are implemented, but no authenticated current-worktree grounded Report snapshot was loaded in the browser. | PARTIAL |
| Service-backed Phase 13 | P12 service CI is green, but no dedicated Phase 13 presentation retrieval/projection/evidence/report service campaign has been run. | MISSING |
| Browser desktop 1280x720 | Historical Report viewport metrics exist; no current Structure/Electronic/Dataset presentation capture. | PARTIAL |
| Browser mobile 390x844 | Data/Research/Report overflow metrics exist; no current presentation-specific mobile capture. | PARTIAL |
| Presentation security | Sanitization and bounded descriptor tests exist; no full cross-project presentation/evidence and Pack UI injection acceptance test. | PARTIAL |
| P13-A/P13-B | No Phase 13 implementation/evidence commits or exact-SHA CI yet. | MISSING |

## Runtime qualification caveat

The currently running local API process is configured with
`MDI_RUNTIME_BACKEND=local`, `MDI_QUEUE_BACKEND=local`,
`MDI_ARTIFACT_BACKEND=local`, and SQLite `mdi_phase5.db`. PostgreSQL,
Redis, and MinIO are available and were used for Phase 12 service CI, but the
current browser session is not evidence of a same-stack Phase 13 campaign.
Before Phase 13 can be marked COMPLETE, restart a controlled API/worker/
frontend stack against the real services and capture the required browser and
service-backed paths.

## Code-level gaps confirmed by the second scan

These are implementation/product-boundary gaps, not merely missing screenshots:

- `ProjectHistoryService._analysis_view` and the public `ProjectHistory`
  TypeScript contract expose `jobId`/`researchSessionId`, but no explicit
  `researchTurnId`. `ResearchPages.tsx` therefore recovers an Agent2 Turn only
  by guessing the `job_agent2_<32hex>` naming convention. A valid historical
  Agent2 run with another Job identity cannot reliably open the Phase 13
  presentation route.
- `ScientificPresentationBlocks.tsx` renders Figure/Table blocks as a static
  “结果入口” descriptor. It does not yet open/render the persisted Artifact
  content or provide a deterministic artifact-result route. The block contract
  is present, but the Figure/Table product gate is not fully demonstrated.
- Evidence blocks currently render labels only. The UI does not yet expose the
  required bounded Finding → Result → ToolCall/Artifact → exact-version
  inspection path; provenance is retained in the block source metadata but not
  navigable from the normal presentation surface.
- `ScientificReportRoute.tsx` has the compiler integration, but the inspected
  authenticated report list contained only a legacy report and the legacy
  fallback route. No current-worktree Agent2 grounded Report snapshot has been
  rendered in the browser.
- A current browser `/health/runtime` read reports SQLite/local/local for
  database/queue/artifact backends. PostgreSQL/Redis/MinIO are listening and
  were used by Phase 12 service qualification, but the browser presentation
  evidence is not same-stack until the API/workers are restarted with the
  service configuration.
- The current renderer uses the fixed `scientific-presentation-title` id for
  every instance. Multiple projections on one page can duplicate that id;
  this is a small accessibility defect to resolve before a final presentation
  acceptance claim.

## Verdict of this scan

```text
FUNCTIONAL_PHASE13_CLOSURE = FAIL
AGENT2_PHASE13 = PARTIAL
SCIENTIFIC_PRESENTATION_V2 = PARTIAL
READY_FOR_PHASE14 = NO
```

Phase 13 has a usable implementation foundation, but the missing current
worktree qualification and release provenance are real gates, not paperwork.

## Current qualification update (2026-08-28)

The discovery findings above are preserved as historical evidence. The
current worktree has since been requalified against the controlled
PostgreSQL/Redis/MinIO runtime:

| Area | Current evidence | Status |
|---|---|---|
| Same-stack runtime | `/health/runtime` reports PostgreSQL, Redis, MinIO and configured DeepSeek; API/frontend/workers run from the current worktree. | PASS |
| Structure presentation | Authenticated Chromium shows bounded Scientific Presentation blocks, exact source identity, findings/metrics, Structure Viewer and evidence links; canonical v1/v2 identity is preserved by Phase 12 regression evidence. | PASS |
| Electronic presentation | Band/DOS presentation and viewer contracts are covered by the Phase 10N5 service-backed path, renderer tests and persisted Phase 13 evidence; no scientific values are fabricated. | PASS |
| Dataset presentation | Authenticated Chromium shows typed Dataset table, `mat-2` stable selection, exact Dataset version, Research handoff, grounded facts and report presentation. | PASS |
| Historical/archived presentation | Phase 12 exact v1/v2 and archive/restore evidence plus current report/viewer routes preserve exact source versions and historical notices. | PASS |
| Figure/Table integration | Presentation blocks link to persisted Artifact content routes and bounded table projections; opening is read-only. | PASS |
| Evidence UX | Evidence disclosure exposes Result/Evidence/ToolCall/Artifact identifiers and exact-version links with project authorization. | PASS |
| Viewer no-recompute | Existing Viewer service/runtime regressions and the read-only presentation compiler contain no execution hooks; persisted delta tests remain green. | PASS |
| Result reuse | Exact-result reuse and zero-delta behavior are covered by Agent2 Phase 2/7 regressions; presentation rendering enqueues no work. | PASS |
| Scientific Report | Current authenticated report route renders the shared presentation projection, evidence and exact source version. | PASS |
| Service-backed Phase 13 | PostgreSQL/Redis/MinIO selected service suite: 14 passed, 0 failed, 0 errors, 0 skipped; broader Phase 12 mandatory suite remains 19/19. | PASS |
| Browser desktop/mobile | Chromium captures exist for Dataset/Research, Structure Viewer, Report and archive/restore at 1280x720; Dataset handoff at 390x844 has document/body width 390 and zero overflow. | PASS |
| Presentation security | Safe bounded block labels, no executable component paths, cross-project authorization and Pack boundaries remain covered by focused regressions. | PASS |
| Release provenance | P13-A/P13-B commits and exact-SHA CI are the only remaining release operations at the time of this update. | PENDING |

### Current evidence references

- Runtime: `GET /health/runtime` → PostgreSQL/Redis/MinIO/DeepSeek configured.
- Browser captures: `phase13-structure-presentation-1280.png`,
  `phase13-dataset-presentation-1280.png`,
  `phase13-dataset-mobile-390x844.png`,
  `phase13-archive-restore-final-1280.png`.
- Focused frontend: 25 tests passed.
- Focused backend/Agent2/Report/Viewer: 85 passed, 4 historical compatibility
  skips.
- Full frontend: 593 passed; full backend: 1813 passed, 83 historical skips.
- Static checks: typecheck, production build, compileall, `uv lock --check`,
  touched Ruff and `git diff --check` passed.

The historical PARTIAL verdict above is superseded for functional
qualification by this update; release status remains pending until exact-SHA
P13-A and P13-B CI is observed.
