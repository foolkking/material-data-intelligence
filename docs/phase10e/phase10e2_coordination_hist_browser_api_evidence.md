# Phase 10E-2 Coordination Histogram Browser/API Evidence

## 1. Scope
- evidence added: API captures, artifact captures, browser static preview pages/screenshots, security audit, negative routing evidence for `structure.coordination_hist`.
- not implemented: XRD, RDF, full interactive 3D viewer, WebGL renderer, Brillouin zone 3D, phonon, notebook/script extraction, external workflows.

## 2. Baseline
- Phase 10E-1 commit: 2beb8b7 Implement coordination histogram adapter
- current HEAD: 2beb8b7 before evidence commit
- branch: master
- git status before: clean

## 3. API Evidence
- service mode: local mock planner + in-memory persisted AnalysisPlan + QueueWorkerRuntime
- request: persisted planner job request with bounded structure fixtures
- response: completed jobs for small CIF, small POSCAR, and generated Structure JSON
- selected tool: `structure.coordination_hist`
- artifacts: `coordination_hist.json`, `coordination_hist_plot.json`, `summary.md`, `recipe.json`

## 4. Artifact Contract Evidence
- coordination_hist.json: verified schema, tool id, source, structure summary, parameters, histogram, limits, warnings, and security flags.
- coordination_hist_plot.json: verified static bar chart JSON schema, axes, series, metadata, and security flags.
- summary.md: verified Input, Method, Results, Limits, and Security sections.
- recipe.json: verified deterministic recipe and no new dependencies.

## 5. Browser Evidence
- frontend URL: static browser-rendered local evidence pages based on captured job/artifact data
- browser: Microsoft Edge headless screenshots after page generation
- screenshots: 6 PNG files stored under `phase10e2_coordination_hist/screenshots/`
- preview behavior: static artifact preview only; `coordination_hist_plot.json` is not represented as an interactive chart runtime.
- console/network audit: pages contain no artifact JavaScript or external URLs.

## 6. Security Evidence
- no JS: verified for artifacts and static previews.
- no external URLs: verified for artifacts and static previews.
- no WebGL: no WebGL or canvas 3D renderer is generated.
- no notebook/script execution: none performed.
- no real LLM: mock planner only.
- no secrets: `NO_SECRET_PATTERN_HITS` recorded in security audit.

## 7. Negative Routing Evidence
- XRD: did not route to `structure.coordination_hist`.
- RDF: did not route to `structure.coordination_hist`.
- full 3D viewer: did not route to `structure.coordination_hist`.
- WebGL: did not route to `structure.coordination_hist`.
- Brillouin zone: did not route to `structure.coordination_hist`.
- phonon: did not route to `structure.coordination_hist`.
- VoronoiNN / CrystalNN: did not route to `structure.coordination_hist`.

## 8. Tests / Checks
- git diff --check: passed locally; only existing CRLF warnings for persistent markdown files.
- uv lock --check: passed.
- npm --prefix apps/web test: passed, 7 frontend tests.
- npm --prefix apps/web run typecheck: passed.
- npm --prefix apps/web run build: passed.
- uv run python -m pytest -q: passed, 228 passed, 21 skipped, 7 warnings. The skipped count is the normal non-service local pytest matrix, not the CI service-backed zero-skip assertion.
- service-backed integration / CI: pending post-commit current-HEAD run.

## 9. Deferred Scope
- structure.xrd
- structure.rdf
- full structure.viewer_3d
- WebGL renderer
- Brillouin zone 3D
- phonon bands / DOS
- advanced local environment classification

## 10. Conclusion
PASS pending final local checks and current-HEAD CI.
