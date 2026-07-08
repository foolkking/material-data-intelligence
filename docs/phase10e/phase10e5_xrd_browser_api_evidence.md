# Phase 10E-5 XRD Browser/API Evidence

## 1. Scope

- evidence added: `structure.xrd` API/job execution, artifact contract captures, static preview pages, negative routing, and security audit.
- not implemented: `structure.rdf`, full interactive 3D viewer, WebGL renderer, Three.js, Brillouin-zone 3D, phonon bands/DOS, experimental XRD fitting, Rietveld refinement, notebook/script extraction, and external API workflows.

## 2. Baseline

- Phase 10E-4 commit: `507d124 Implement XRD adapter`
- Phase 10E-4 HEAD: `507d12432e3238ffd51453866ac4c9f1614c3511`
- current HEAD before evidence: `507d12432e3238ffd51453866ac4c9f1614c3511`
- branch: `master`
- git status before: clean

## 3. API Evidence

- service mode: deterministic Mock Planner, persisted AnalysisPlan, QueueWorkerRuntime, Tool Registry validation, and in-memory repository bundle.
- real LLM: not used.
- successful inputs:
  - `simple_cubic_cif`: small CIF fixture.
  - `nacl_poscar`: small POSCAR fixture.
  - `generated_structure_json`: generated pymatgen Structure JSON.
- selected tool: `structure.xrd` for each successful XRD prompt.
- artifacts per job: `xrd_pattern.json`, `xrd_plot.json`, `summary.md`, and `recipe.json`.
- redacted captures: `docs/phase10e/browser_api_evidence/phase10e5_xrd/api_redacted/`
- API capture count: 40.

## 4. Artifact Contract Evidence

- `xrd_pattern.json`: verified `schema_version == phase10e4.xrd_pattern.v1`, `tool_id == structure.xrd`, CuKa radiation, source metadata, structure summary, parameters, sorted peaks, limits, warnings, and security flags.
- `xrd_plot.json`: verified `schema_version == phase10e4.static_chart.v1`, `tool_id == structure.xrd`, `chart_type == stem`, axes, series, metadata, and security flags.
- `summary.md`: verified Input, Method, Results, Limits, and Security sections. It does not claim experimental refinement, Rietveld refinement, profile fitting, peak broadening, or official example reproduction.
- `recipe.json`: verified `schema_version == phase10e4.recipe.v1`, `tool_id == structure.xrd`, `deterministic == true`, and `dependencies.new_dependencies_added == false`.
- artifact captures: `docs/phase10e/browser_api_evidence/phase10e5_xrd/artifacts/`
- artifact capture count: 12.

## 5. Browser Evidence

- static preview pages: `docs/phase10e/browser_api_evidence/phase10e5_xrd/browser_pages/`
- real browser screenshots: `docs/phase10e/browser_api_evidence/phase10e5_xrd/screenshots/`
- preview pages generated:
  - `01_job_completed.html`
  - `02_artifact_list.html`
  - `03_xrd_pattern_json_preview.html`
  - `04_xrd_plot_preview.html`
  - `05_summary_preview.html`
  - `06_recipe_preview.html`
- preview behavior: the real frontend screenshots show the completed job, artifact gallery, static result-page preview, summary preview, and recipe preview. `xrd_plot.json` remains static chart JSON / metadata; rendered stem chart UI and a dedicated single-artifact viewer are deferred.
- screenshot status: repaired in Phase 10E-5R2. System Chrome was launched with Playwright `executablePath` and captured real browser-rendered frontend screenshots.
- screenshots captured:
  - `01_job_completed.png`
  - `02_artifact_list.png`
  - `03_xrd_pattern_json_preview.png`
  - `04_xrd_plot_preview.png`
  - `05_summary_preview.png`
  - `06_recipe_preview.png`
- console/network audit: static preview pages and browser-rendered frontend screenshots contain no external artifact loads, active script tags, JavaScript URLs, inline event handlers, or dynamic loader hooks. Browser network audit recorded local frontend/API requests only.

## 6. Security Evidence

- no JS: verified in generated artifacts and static preview pages.
- no external URLs: verified.
- no WebGL: verified.
- no Three.js: verified; no Three.js renderer or bundle was added.
- no notebook/script execution: verified by evidence harness design.
- no real LLM: verified by deterministic Mock Planner use.
- no secrets: generated evidence scan result is `NO_SECRET_PATTERN_HITS`.

## 7. Negative Routing Evidence

- RDF: did not route to `structure.xrd`.
- coordination histogram: did not route to `structure.xrd`; coordination prompts route to the existing coordination tool.
- full 3D viewer: did not route to `structure.xrd`.
- WebGL: did not route to `structure.xrd`.
- Brillouin zone: did not route to `structure.xrd`.
- phonon: did not route to `structure.xrd`.
- experimental XRD fitting: did not route to `structure.xrd`.
- Rietveld refinement: did not route to `structure.xrd`.
- VoronoiNN / CrystalNN: did not route to `structure.xrd`.

## 8. Tests / Checks

- generation harness: passed for 3 cases.
- artifact contract checks: passed during generation.
- generated evidence security scan: `NO_SECRET_PATTERN_HITS`.
- `git diff --check`: passed.
- `uv lock --check`: passed.
- `npm --prefix apps/web test`: passed, 1 test file / 7 tests.
- `npm --prefix apps/web run typecheck`: passed.
- `npm --prefix apps/web run build`: passed.
- `uv run python -m pytest -q`: passed, 254 passed / 21 skipped / 9 warnings.
- no-skipped assertion: not regressed in local pytest; CI service-backed integration remains the source of truth after push.

## 9. Deferred Scope

- `structure.rdf`
- full `structure.viewer_3d`
- WebGL renderer
- Three.js
- Brillouin-zone 3D
- phonon bands / DOS
- advanced local environment classification
- experimental fitting / Rietveld refinement

## 10. Conclusion

PASS.

API evidence, artifact evidence, security evidence, negative routing evidence, and real browser-rendered frontend screenshots are complete. Phase 10E-5 was originally `PARTIAL_PASS` because real browser screenshots were blocked; Phase 10E-5R2 repaired the gap using system Chrome / Playwright `executablePath`. No browser/API evidence was fabricated.
