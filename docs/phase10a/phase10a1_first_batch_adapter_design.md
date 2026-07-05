# Phase 10A-1 First Batch Adapter Design

## 1. Scope

Phase 10A-1 implements the first adapter batch for the two `DIRECT_VERIFIED` official pymatviz benchmark cases only:

- `matpes_atomic_energies_csv`
- `ward_metallic_glasses_csv_xz`

The implementation adds table and visualization adapters that run through the existing Tool Registry and Adapter boundary. It does not change QueueWorkerRuntime, AnalysisPlanRepository, persisted plan semantics, true LLM gating, or the Phase 9C workspace layout.

Out of scope:

- 27 `EXTRACTION_REQUIRED` cases.
- 20 `MAPPING_ONLY` cases.
- 12 `FUTURE_SCOPE` cases.
- New notebook/script extraction.
- True LLM live verification.
- Production KMS or secret encryption.
- Multi-step DAG/data-dependency execution.

## 2. Adapter Contracts

### 2.1 `table.distribution_summary`

Purpose: produce stricter table distribution statistics than `table.numeric_summary`.

Input schema:

- `inputRefs`: one table-like resource, normally `ml_table`.
- `numericColumns?: string[]`
- `categoricalColumns?: string[]`
- `quantiles?: number[]`, default `[0.25, 0.5, 0.75]`
- `maxCategories?: number`, default `10`

Output artifacts:

- `distribution_summary.json`
- `summary.md`
- `recipe.json`

`distribution_summary.json` includes:

- `rowCount`
- `columnCount`
- `numericColumns`
- `categoricalColumns`
- `recommendedVisualizations`
- `warnings`

Error classes:

- `empty_table`
- `unsupported_profile_type`
- `missing_column`
- `non_numeric_column`
- `artifact_write_failed`

### 2.2 `viz.scatter`

Purpose: generate a scatter plot artifact for two numeric columns.

Input schema:

- `inputRefs`: one table-like resource, normally `ml_table`.
- `xColumn: string`
- `yColumn: string`
- `colorColumn?: string`
- `hoverColumns?: string[]`
- `title?: string`

Output artifacts:

- `scatter.json`
- `scatter.html` when HTML export is requested.
- `summary.md`
- `recipe.json`

`scatter.json` includes:

- `chartType: "scatter"`
- `xColumn`
- `yColumn`
- `pointCount`
- `traces`
- `xRange`
- `yRange`
- `warnings`

MatPES default routing:

- `xColumn = "PBE"`
- `yColumn = "r2SCAN"`

Error classes:

- `missing_column`
- `non_numeric_column`
- `empty_table`
- `too_many_points_warning`
- `artifact_write_failed`

### 2.3 `viz.histogram`

Purpose: generate a histogram/distribution artifact for one numeric column.

Input schema:

- `inputRefs`: one table-like resource, normally `ml_table`.
- `column: string`
- `bins?: number`, default `20`
- `groupBy?: string`
- `title?: string`

Output artifacts:

- `histogram.json`
- `histogram.html` when HTML export is requested.
- `summary.md`
- `recipe.json`

`histogram.json` includes:

- `chartType: "histogram"`
- `column`
- `count`
- `bins`
- `binEdges`
- `binCounts`
- `min`
- `max`
- `mean`
- `median`
- `warnings`

Error classes:

- `missing_column`
- `non_numeric_column`
- `empty_table`
- `artifact_write_failed`

### 2.4 `viz.correlation`

Purpose: generate a numeric correlation matrix and heatmap artifacts.

Input schema:

- `inputRefs`: one table-like resource, normally `ml_table`.
- `numericColumns?: string[]`
- `method?: "pearson" | "spearman"`, default `"pearson"`
- `minNonNullCount?: number`, default `2`
- `title?: string`

Output artifacts:

- `correlation_matrix.json`
- `correlation_heatmap.json`
- `correlation_heatmap.html` when HTML export is requested.
- `summary.md`
- `recipe.json`

`correlation_matrix.json` includes:

- `method`
- `columns`
- `matrix`
- `pairCount`
- `warnings`

Error classes:

- `insufficient_numeric_columns`
- `non_numeric_column`
- `empty_table`
- `artifact_write_failed`

### 2.5 `composition.summary`

Purpose: safely summarize formula/composition columns when a stable formula-like field exists.

Input schema:

- `inputRefs`: one formula list or table-like resource.
- `formulaColumn?: string`
- `compositionColumn?: string`
- `maxSystems?: number`

Output artifacts:

- `composition_summary.json`
- `summary.md`
- `recipe.json`

`composition_summary.json` includes:

- `formulaColumn`
- `formulaCount`
- `parsedFormulaCount`
- `failedFormulaCount`
- `elementCounts`
- `elementFractions`
- `systemTypes`
- `warnings`

Error classes:

- `missing_formula_column`
- `invalid_formula`
- `unsupported_profile_type`
- `artifact_write_failed`

Ward evidence may use this adapter only when the `composition` field is safely recognized as formula-like. Otherwise Ward remains table/viz evidence only.

## 3. Tool Registry Registration

Each adapter is registered in the platform builtin manifest with:

- Tool domain: `table`, `viz`, or `composition`.
- Deterministic params schema.
- Explicit input resource schema.
- Resource limits.
- Output artifact schema.
- V1/V2 safety boundary unchanged.

New `ToolDomain.viz` is added to shared schemas. Existing `ToolDomain.table` remains part of the registry.

## 4. Planner Routing

Mock Planner routing is extended for deterministic demo and test prompts:

- MatPES scatter prompt -> `viz.scatter` with `PBE` and `r2SCAN`.
- MatPES histogram prompt -> `viz.histogram` for `PBE` or `r2SCAN`.
- Ward distribution prompt -> `table.distribution_summary`.
- Ward correlation prompt -> `viz.correlation`.
- Composition prompt -> `composition.summary` only when a formula/composition field exists; otherwise validation fails rather than fabricating composition output.

The routing produces a single executable step unless the runtime later supports true multi-step DAG execution.

## 5. UI Display

The Phase 9C information architecture is unchanged. The Results/Export tab gains display support for:

- Scatter JSON/HTML artifacts.
- Histogram JSON/HTML artifacts.
- Correlation matrix and heatmap artifacts.
- Distribution summary artifacts.
- Composition summary artifacts.

Regular mode shows artifact summaries and report/recipe text. Developer mode remains the place for raw JSON and provenance identifiers.

## 6. Test Plan

Backend:

- Adapter unit tests for table distribution, scatter, histogram, correlation, and composition summary.
- Manifest/registry tests for tool registration and params validation.
- Mock Planner routing tests for MatPES and Ward prompts.
- Persisted plan execution test proving one new tool plan creates exactly one ToolCall and artifact.
- Invalid plan regression proving no plan/job/enqueue on validation failure.

Frontend:

- Results tab renders new artifact types.
- Report and recipe remain visible.
- Developer details remain hidden by default.

Regression:

- Phase 7 planner tests.
- Phase 8B persisted plan queue tests.
- Phase 8C read API tests.
- Phase 9B workspace API tests.
- Full backend pytest.
- Frontend test/typecheck/build.

## 7. Official Examples Evidence Plan

Project-level evidence is stored under:

`docs/phase10a/official_examples_evidence/`

Planned evidence folders:

- `matpes_scatter`
- `matpes_histogram`
- `ward_distribution`
- `ward_correlation`

Each folder records execution logs, platform summaries, artifact manifests, redacted API evidence notes, and screenshot placeholders or browser screenshots when captured. Desktop benchmark pack evidence is not committed unless explicitly requested.

## 8. Non-goals and Safety

The adapters must not:

- Execute shell/Python/user code.
- Access the network.
- Read arbitrary filesystem paths.
- Write artifacts outside the controlled artifact exporter.
- Depend on true LLM calls.
- Store or expose API keys, Authorization headers, or BYOK values.

The implementation must preserve:

- Phase 8B persisted plan exact execution.
- Phase 9D gated live LLM provider path.
- Default CI without real LLM calls.
- Tool Registry + Adapter execution as the only executable path.
