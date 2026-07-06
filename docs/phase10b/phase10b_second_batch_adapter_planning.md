# Phase 10B Second Batch pymatviz Adapter Planning

## 1. Background

Phase 10A established the first official-example adapter baseline for the two
`DIRECT_VERIFIED` pymatviz benchmark cases:

- `matpes_atomic_energies_csv`
- `ward_metallic_glasses_csv_xz`

Phase 10A-1 implemented the first batch of deterministic table and visualization
adapters:

- `table.distribution_summary`
- `viz.scatter`
- `viz.histogram`
- `viz.correlation`
- `composition.summary`

Phase 10A-2 then added browser/API/artifact evidence for six scenarios:

- `matpes_scatter`
- `matpes_histogram`
- `ward_distribution`
- `ward_histogram`
- `ward_correlation`
- `ward_composition_summary`

Those adapters validate the end-to-end execution boundary, but most of them are
general table or chart capabilities. Phase 10B should move toward pymatviz's
materials-informatics center of gravity without jumping directly to fragile
3D/physics workflows.

The recommended next step is composition visualization: periodic-table heatmaps,
element histograms, chemical-system treemaps/sunbursts, and formula statistics.
These capabilities are closer to pymatviz's official gallery while remaining
small enough for deterministic adapter tests, browser evidence, and CI.

## 2. Current Capability Baseline

The current Tool Registry already includes a wider set of tools than the Phase
10A evidence baseline. The distinction matters:

- Registered tool: a tool manifest exists and PlanValidator can see it.
- Evidence-grade tool: browser/API/artifact evidence exists against an official
  benchmark case.

Evidence-grade Phase 10A tools:

- `table.distribution_summary`
- `viz.scatter`
- `viz.histogram`
- `viz.correlation`
- `composition.summary`

Already registered composition tools that should be productized with stricter
contracts and evidence:

- `composition.ptable_heatmap`
- `composition.elements_hist`
- `composition.chem_sys_treemap`

Additional second-batch candidates:

- `composition.chem_sys_sunburst`
- `composition.formula_statistics`

Execution boundaries remain unchanged:

- LLMs may only produce JSON AnalysisPlans.
- AnalysisPlans must be validated before persistence.
- Jobs must execute persisted plans through QueueWorkerRuntime.
- Executable work must go through Tool Registry + Adapter.
- Secrets must never enter prompts, plans, events, artifacts, reports, or exports.

## 3. Second Batch Candidate Capability Pool

### Composition

Recommended for Phase 10B-1:

- `composition.ptable_heatmap`
- `composition.elements_hist`
- `composition.chem_sys_treemap`
- `composition.chem_sys_sunburst`
- `composition.formula_statistics`

Future composition extensions:

- `composition.ptable_hists`
- `composition.ptable_scatter`
- `composition.ptable_heatmap_splits`
- `composition.cluster_2d`
- `composition.cluster_3d`

### Lightweight Structure

Recommended for planning only in Phase 10B, with implementation deferred:

- `structure.summary`
- `structure.spacegroup_summary`
- `structure.lattice_summary`
- `structure.structure_preview_metadata`

### Advanced Structure and Physics

Keep out of Phase 10B-1:

- `structure.viewer_3d`
- `structure.xrd`
- `structure.rdf`
- `structure.coordination_hist`
- `structure.brillouin_zone_3d`
- `phonon.bands`
- `phonon.dos`
- `phonon.band_dos`

### ML Plot Extensions

Keep as later work after composition/structure coverage:

- `ml.parity_plot`
- `ml.error_by_element`
- `ml.error_by_chem_sys`
- `ml.uncertainty_calibration`
- `ml.classification_confusion_matrix`

## 4. Phase 10B Recommended Scope

Phase 10B-1 should implement or harden only composition visualization adapters:

- `composition.ptable_heatmap`
- `composition.elements_hist`
- `composition.chem_sys_treemap`
- `composition.chem_sys_sunburst`
- `composition.formula_statistics`

Rationale:

- Composition inputs can come from formula/composition columns already present in
  Ward or later extracted tables.
- The platform already has `composition.summary`, so parsing and warning behavior
  can be made consistent.
- Periodic-table and chemical-system outputs are core pymatviz behavior.
- Browser evidence can be captured as JSON/HTML/summary/recipe artifacts without
  needing 3D WebGL stability.
- These tools do not require external APIs, notebook execution, or live LLMs.

## 5. Explicitly Out of Scope

Phase 10B planning does not authorize implementation of:

- `structure.viewer_3d`
- XRD adapters
- RDF adapters
- phonon bands/DOS
- Brillouin zone rendering
- notebook extraction
- script execution
- external API ingestion
- multi-step DAG/data-dependency execution
- production secret encryption/KMS
- new LLM execution authority

These remain future-scope or separate planning items.

## 6. Recommended Adapter Design Drafts

### 6.1 `composition.ptable_heatmap`

- Purpose: aggregate element-level values or counts into a periodic-table heatmap.
- Input resources: formula list, composition list, or table with formula/composition
  column; optional numeric value column.
- Params schema:
  - `formulaColumn?: string`
  - `compositionColumn?: string`
  - `valueColumn?: string`
  - `aggregation?: "count" | "sum" | "mean" | "median" | "fraction"`
  - `scale?: "linear" | "log"`
  - `title?: string`
  - `maxFormulas?: number`
- Output artifacts:
  - `ptable_heatmap.json`
  - `ptable_heatmap.html`
  - `summary.md`
  - `recipe.json`
- Summary content: element coverage, top elements, aggregation mode, skipped formulas.
- Recipe content: input column, aggregation, parser version, warning list.
- Warning model:
  - invalid formula rows
  - unknown element symbols
  - empty element counts
  - log scale with zero values
- Error classification:
  - `missing_formula_column`
  - `invalid_formula`
  - `unsupported_aggregation`
  - `empty_composition_set`
  - `artifact_write_failed`
- Deterministic behavior: stable element ordering by periodic-table atomic number.
- Security boundary: no network, no arbitrary file reads, no code execution.

### 6.2 `composition.elements_hist`

- Purpose: produce element frequency and fraction distributions from formulas.
- Input resources: formula list or table formula/composition column.
- Params schema:
  - `formulaColumn?: string`
  - `compositionColumn?: string`
  - `countMode?: "formula_presence" | "stoichiometric_count" | "fractional"`
  - `topN?: number`
  - `sortBy?: "count" | "atomic_number" | "symbol"`
- Output artifacts:
  - `elements_hist.json`
  - `elements_hist.html`
  - `summary.md`
  - `recipe.json`
- Summary content: formula count, parsed count, top elements, missing/failed rows.
- Warning model:
  - failed formula parse
  - very high cardinality
  - empty valid formula set
- Error classification:
  - `missing_formula_column`
  - `invalid_formula`
  - `empty_composition_set`
  - `artifact_write_failed`
- Deterministic behavior: stable bin order and stable top-N tie breaking.
- Security boundary: local deterministic parser only.

### 6.3 `composition.chem_sys_treemap`

- Purpose: group formulas into chemical systems such as `Fe-O`, `Li-Fe-P-O`.
- Input resources: formula list or table formula/composition column.
- Params schema:
  - `formulaColumn?: string`
  - `compositionColumn?: string`
  - `maxSystems?: number`
  - `minCount?: number`
  - `groupRareAsOther?: boolean`
  - `systemOrder?: "alphabetical" | "count_desc"`
- Output artifacts:
  - `chem_sys_treemap.json`
  - `chem_sys_treemap.html`
  - `summary.md`
  - `recipe.json`
- Summary content: number of systems, top systems, formula parse success rate.
- Warning model:
  - rare systems grouped
  - failed formulas
  - too many unique systems
- Error classification:
  - `missing_formula_column`
  - `invalid_formula`
  - `empty_composition_set`
  - `too_many_systems`
  - `artifact_write_failed`
- Deterministic behavior: canonical chemical-system labels sorted by element symbol.
- Security boundary: no external chemistry service calls.

### 6.4 `composition.chem_sys_sunburst`

- Purpose: hierarchical chemical-system view by arity and element sets.
- Input resources: formula list or table formula/composition column.
- Params schema:
  - `formulaColumn?: string`
  - `compositionColumn?: string`
  - `maxDepth?: number`
  - `maxSystems?: number`
  - `groupRareAsOther?: boolean`
  - `title?: string`
- Output artifacts:
  - `chem_sys_sunburst.json`
  - `chem_sys_sunburst.html`
  - `summary.md`
  - `recipe.json`
- Summary content: unary/binary/ternary/quaternary counts, top systems, parse warnings.
- Warning model:
  - high arity systems collapsed
  - rare systems grouped
  - failed formulas
- Error classification:
  - `missing_formula_column`
  - `invalid_formula`
  - `empty_composition_set`
  - `too_many_systems`
  - `artifact_write_failed`
- Deterministic behavior: canonical tree path ordering.
- Security boundary: deterministic transform only.

### 6.5 `composition.formula_statistics`

- Purpose: produce a machine-readable formula/composition statistics table.
- Input resources: formula list or table formula/composition column.
- Params schema:
  - `formulaColumn?: string`
  - `compositionColumn?: string`
  - `includeElementFractions?: boolean`
  - `includeArity?: boolean`
  - `includeReducedFormula?: boolean`
  - `maxRows?: number`
- Output artifacts:
  - `formula_statistics.json`
  - `formula_statistics.csv`
  - `summary.md`
  - `recipe.json`
- Summary content: valid formula count, invalid formula count, arity distribution,
  common reduced formulas, common elements.
- Warning model:
  - formula parse failures
  - missing composition values
  - output row truncation
- Error classification:
  - `missing_formula_column`
  - `invalid_formula`
  - `empty_composition_set`
  - `artifact_write_failed`
- Deterministic behavior: stable row order inherited from input row order.
- Security boundary: no arbitrary expression evaluation.

## 7. Official Examples Mapping

| Candidate Adapter | Official Case | Case Type | Input Data | Expected Artifact | Current Support | Risk |
|---|---|---|---|---|---|---|
| `composition.ptable_heatmap` | `ward_metallic_glasses_csv_xz` | `direct_uploadable_data` | Ward composition column | `ptable_heatmap.json/html` | Formula parsing evidence exists via `composition.summary`; heatmap evidence missing | Low-medium |
| `composition.elements_hist` | `ward_metallic_glasses_csv_xz` | `direct_uploadable_data` | Ward composition column | `elements_hist.json/html` | Registered MVP tool; official evidence missing | Low |
| `composition.chem_sys_treemap` | `ward_metallic_glasses_csv_xz` | `direct_uploadable_data` | Ward composition column | `chem_sys_treemap.json/html` | Registered MVP tool; official evidence missing | Low-medium |
| `composition.chem_sys_sunburst` | `ward_metallic_glasses_csv_xz` | `direct_uploadable_data` | Ward composition column | `chem_sys_sunburst.json/html` | Not first-batch evidence; may need new manifest/adapter hardening | Medium |
| `composition.formula_statistics` | `ward_metallic_glasses_csv_xz` | `direct_uploadable_data` | Ward composition column | `formula_statistics.json/csv` | Can reuse parser semantics from `composition.summary` | Low |
| `composition.ptable_heatmap` | `readme_ptable_heatmap_*` | `readme_function_demo` | No direct raw data | Mapping contract only | Good design reference; not PASS evidence | Medium |
| `composition.elements_hist` | `readme_elements_hist` | `readme_function_demo` | No direct raw data | Mapping contract only | Good design reference; not PASS evidence | Medium |
| `composition.chem_sys_treemap` | `examples_root_matbench_perovskites_eda`, `camd_2022_explore`, `wbm_explore_wbm` | `script_generated_data`/`external_api_required` | Extraction required | Future evidence after extraction | Do not treat as direct benchmark | High |

## 8. Planner Routing Plan

Mock Planner routing should remain deterministic and single-step unless runtime
multi-step DAG support is introduced later.

Prompt mapping:

- "元素分布", "element distribution", "elements histogram" ->
  `composition.elements_hist`
- "周期表热力图", "periodic table heatmap", "ptable heatmap" ->
  `composition.ptable_heatmap`
- "化学体系分布", "chemical system", "chem sys treemap" ->
  `composition.chem_sys_treemap`
- "sunburst", "层级化学体系" ->
  `composition.chem_sys_sunburst`
- "formula statistics", "formula 统计", "composition statistics" ->
  `composition.formula_statistics`
- Generic "composition summary" remains `composition.summary`.

Routing constraints:

- Select a formula/composition column only when the profile exposes one.
- If no safe formula/composition field exists, return validation failure or a
  clear unsupported message; do not fabricate composition outputs.
- Do not route Ward to `ml.basic_metrics` unless the user explicitly requests a
  target/prediction comparison.
- Do not route mapping-only README examples to completed jobs without real input.

## 9. API / Browser Evidence Plan

Phase 10B-2 should capture evidence for each implemented composition adapter:

- `upload_response.json`
- `profile_response.json`
- `provider_resolve_response.json`
- `planner_preview_response.json`
- `planner_validate_response.json`
- `planner_job_response.json`
- `events_response.json`
- `tool_calls_response.json`
- `artifacts_response.json`
- `result_response.json`
- Browser screenshots:
  - upload/profile
  - conversation/Plan preview
  - Agent process completed
  - Results/export tab
  - redacted developer audit
- Artifact files:
  - primary JSON artifact
  - optional HTML artifact
  - `summary.md`
  - `recipe.json`
  - `artifact_manifest.json`
- `evidence_manifest.json`

Evidence constraints:

- Use Mock Planner/local safe planner unless a separate gated live LLM phase is
  explicitly requested.
- Do not overwrite the desktop benchmark pack.
- Redact Authorization, Bearer tokens, API keys, and secret IDs where needed.
- Do not claim unsupported official examples as verified.

## 10. Test Plan

Adapter unit tests:

- Valid formulas produce deterministic artifacts.
- Invalid formulas produce warnings, not crashes, when at least one formula is
  valid.
- Empty or missing formula column produces typed validation errors.
- `maxSystems`, `topN`, and truncation warnings behave deterministically.

Registry/schema tests:

- New or hardened tools are listed in Tool Registry.
- Params schemas reject invalid enum values and missing required columns.
- V1/V2 guard behavior remains unchanged.

Planner routing tests:

- Ward ptable heatmap prompt -> `composition.ptable_heatmap`.
- Ward elements prompt -> `composition.elements_hist`.
- Ward chemical-system prompt -> `composition.chem_sys_treemap`.
- Ward formula statistics prompt -> `composition.formula_statistics`.
- No formula column -> no fabricated composition plan.

API/execution tests:

- `/planner/validate` accepts valid one-step composition plans.
- `/planner/jobs` persists exact validated plans.
- Worker executes one persisted composition plan as exactly one ToolCall.
- Artifacts include plan provenance and recipe.
- Invalid plans do not save plan, create job, or enqueue.

Frontend tests:

- Results/export tab renders composition artifacts.
- Report and recipe remain visible.
- Developer details are hidden by default.
- No API key or raw secret appears in UI state.

Regression:

- Phase 7 planner tests.
- Phase 8B persisted plan queue tests.
- Phase 8C read API tests.
- Phase 9B workspace API tests.
- Full backend pytest.
- Frontend tests/typecheck/build.

Service-backed integration:

- Default CI continues to run PostgreSQL/Redis/MinIO integration.
- Integration must not all skip.
- Default CI must not call real LLM.

## 11. Risk Assessment

- Formula parsing failure: formula strings can include unusual separators,
  variables, or malformed values. Adapters must report parse failures and counts.
- Invalid element symbols: adapters must warn and skip invalid formulas instead
  of inventing elements.
- Huge formula list: use deterministic limits and truncation warnings.
- Mixed formula/composition fields: profile selection must prefer explicit
  formula/composition columns and document ambiguous choices.
- Optional dependency risk: avoid new heavy dependencies in Phase 10B-1.
- Plotly artifact size: cap point/tree size or aggregate rare categories.
- Browser screenshot stability: use Results/export summaries and artifact
  manifests as primary evidence; screenshots are supporting evidence.
- CI runtime risk: keep adapter tests small and deterministic.
- Benchmark scope risk: README mapping demos are not direct uploadable evidence.

## 12. Recommended Phase Split

### Phase 10B-1 Composition Visualization Adapter Implementation

Implement or harden:

- `composition.ptable_heatmap`
- `composition.elements_hist`
- `composition.chem_sys_treemap`
- `composition.chem_sys_sunburst`
- `composition.formula_statistics`

Add adapter, registry, planner routing, API execution, frontend rendering, and
unit/regression tests. Do not capture large browser/API evidence in this phase.

### Phase 10B-2 Browser/API Evidence for Composition Adapters

Use Phase 9C UI and real backend API to capture Ward composition evidence for
each Phase 10B-1 adapter. Store redacted API captures, screenshots, artifact
files, and evidence manifests under project docs. Do not modify the desktop
benchmark pack unless explicitly requested.

### Phase 10C Lightweight Structure Adapter Planning

Plan:

- `structure.summary`
- `structure.spacegroup_summary`
- `structure.lattice_summary`
- `structure.structure_preview_metadata`

Defer WebGL viewer, XRD, RDF, phonon, and Brillouin zone until direct inputs,
dependencies, artifacts, and screenshot stability are better constrained.

## 13. Acceptance Criteria

Phase 10B planning is complete when:

- The repository baseline is confirmed at Phase 10A-2.
- No new adapter implementation is added.
- Runtime, QueueWorkerRuntime, AnalysisPlanRepository, and `/planner/jobs`
  semantics are unchanged.
- Phase 10B-1 scope is explicitly limited to composition visualization.
- Candidate adapter matrix is complete.
- Official-example mapping separates DIRECT_VERIFIED, MAPPING_ONLY,
  EXTRACTION_REQUIRED, and FUTURE_SCOPE cases.
- Phase 10B-1 implementation prompt is ready for a later execution phase.
- Persistent files record the planning decision and boundaries.
- `git diff --check` passes.

## 14. Final Recommendation

Proceed next to:

`Phase 10B-1: Composition Visualization Adapter Implementation`

Do not jump directly to 3D structure, XRD, RDF, phonon, or Brillouin-zone work.
Those areas are important but require a separate structure/physics planning pass,
dependency review, direct input fixtures, and browser evidence strategy.
