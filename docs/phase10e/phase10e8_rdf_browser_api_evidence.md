# Phase 10E-8 RDF Browser/API Evidence

## 1. Scope

- evidence added: `structure.rdf` API/job execution, artifact contract captures, real browser-rendered frontend screenshots, security audit, and negative routing evidence.
- not implemented: full interactive 3D viewer, WebGL renderer, Three.js, Brillouin-zone 3D, phonon bands/DOS, advanced local environment classification, experimental PDF fitting, neutron scattering refinement, X-ray total scattering analysis, notebook/script extraction, and external API workflows.

## 2. Baseline

- Phase 10E-7 commit: `f5c4e15 Implement RDF adapter`
- Phase 10E-7 HEAD: `f5c4e15d6f9106b6846158991de5bd1bce6483af`
- current HEAD before evidence: `f5c4e15d6f9106b6846158991de5bd1bce6483af`
- branch: `master`
- git status before: clean

## 3. API Evidence

- service mode: FastAPI local service, deterministic Mock Planner, persisted AnalysisPlan, QueueWorkerRuntime, Tool Registry validation, and local worker.
- backend URL: `http://127.0.0.1:8128`
- frontend URL: `http://127.0.0.1:3128`
- real LLM: not used.
- successful inputs:
  - `simple_cubic_cif`: small CIF fixture.
  - `nacl_poscar`: small POSCAR fixture.
- selected tool: `structure.rdf` for each successful RDF prompt.
- artifacts per job: `rdf.json`, `rdf_plot.json`, `summary.md`, and `recipe.json`.
- redacted captures: `docs/phase10e/browser_api_evidence/phase10e8_rdf/api_redacted/`
- artifact captures: `docs/phase10e/browser_api_evidence/phase10e8_rdf/artifacts/`

## 4. Artifact Contract Evidence

- `rdf.json`: verified `schema_version == phase10e7.rdf.v1`, `tool_id == structure.rdf`, source metadata, structure summary, params, sorted `r_angstrom`, sorted bin edges, aligned `g_r` and counts arrays, ordered partial RDF pairs, limits, warnings, and security flags.
- `rdf_plot.json`: verified `schema_version == phase10e7.static_chart.v1`, `tool_id == structure.rdf`, `chart_type == line`, axes, series, metadata, and security flags.
- `summary.md`: verified Input, Method, Results, Limits, and Security sections, including periodic-image policy and normalization. It does not claim experimental PDF fitting, neutron scattering refinement, X-ray total scattering analysis, phonon DOS, local environment classification, or official example reproduction.
- `recipe.json`: verified `schema_version == phase10e7.recipe.v1`, `tool_id == structure.rdf`, deterministic steps, and `dependencies.new_dependencies_added == false`.

## 5. Browser Evidence

- browser executable: `C:/Program Files (x86)/Google/Chrome/Application/chrome.exe`
- automation tool: existing `E:/mdi-playwright-runner/node_modules/playwright` package with system Chrome `executablePath`.
- viewport: `1440x1000`
- screenshots: `docs/phase10e/browser_api_evidence/phase10e8_rdf/screenshots/`
- screenshots captured:
  - `01_job_completed.png`
  - `02_artifact_list.png`
  - `03_rdf_json_preview.png`
  - `04_rdf_plot_preview.png`
  - `05_summary_preview.png`
  - `06_recipe_preview.png`
- preview behavior: the real Next frontend displays the completed RDF job, summary preview, recipe preview, Artifact Gallery entries for all four artifacts, and the `structure.rdf` ToolCall. `rdf_plot.json` is displayed as a static JSON artifact entry; rendered line chart UI is deferred.
- console/network audit: browser network requests were local `127.0.0.1` frontend/API requests only. The React development console message contains a documentation URL and is recorded as non-artifact false positive; no artifact caused external URL loading.

## 6. Security Evidence

- no JS: verified in generated artifacts and evidence audit.
- no external URLs: verified for artifacts and browser network requests.
- no WebGL: verified.
- no Three.js: verified; no Three.js renderer or bundle was added.
- no notebook/script execution: verified by evidence harness design.
- no real LLM: verified by deterministic Mock Planner use.
- no secrets: generated evidence scan result is `NO_SECRET_PATTERN_HITS`.

## 7. Negative Routing Evidence

- XRD: did not route to `structure.rdf`.
- coordination histogram: did not route to `structure.rdf`.
- full 3D viewer: did not route to `structure.rdf`.
- WebGL: did not route to `structure.rdf`.
- Brillouin zone: did not route to `structure.rdf`.
- phonon: did not route to `structure.rdf`.
- experimental PDF fitting: did not route to `structure.rdf`.
- neutron scattering refinement: did not route to `structure.rdf`.
- VoronoiNN / CrystalNN: did not route to `structure.rdf`.

## 8. Tests / Checks

- generation harness: passed for 2 periodic structure cases.
- artifact contract checks: passed during generation.
- browser screenshot capture: passed with system Chrome / Playwright.
- generated evidence security scan: `NO_SECRET_PATTERN_HITS`.
- local regression checks and CI status are recorded in the final Phase 10E-8 result.

## 9. Deferred Scope

- full `structure.viewer_3d`
- WebGL renderer
- Three.js
- Brillouin-zone 3D
- phonon bands / DOS
- advanced local environment classification
- experimental fitting / scattering refinement

## 10. Conclusion

PASS.

API evidence, artifact evidence, security evidence, negative-routing evidence, and real browser-rendered frontend screenshots are complete. No browser/API evidence was fabricated, and Phase 10E-8 did not change `structure.rdf` calculation semantics.
