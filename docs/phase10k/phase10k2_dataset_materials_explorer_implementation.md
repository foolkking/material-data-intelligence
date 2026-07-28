# Phase 10K-2 Dataset Materials Explorer Implementation

Status: COMPLETE. Exact implementation-SHA CI run `30355075439` and
completion-record exact-SHA CI run `30355282590` passed. The permanent result
is retained in `results.md`, and the verified queue block is archived.

## Product boundary

`dataset.materials_explorer` is one product-level Tool Registry capability. It
consumes exactly one Material Data Profile 2.0 plus the profiled table and
optional structure resources. It does not repeat formula, property, sample-ID,
or resource-role inference. The execution path remains validated AnalysisPlan
to QueueWorkerRuntime to Registry to `DatasetMaterialsExplorerAdapter`.

The adapter emits one coherent `phase10k2.dataset_materials_explorer.v1`
`table_json` bundle plus `dataset_quality.json`, `summary.md`, and `recipe.json`.
One bundle is intentional: the shared artifact ID is stable per tool call and
artifact type, and the product is not a set of unrelated charts.

## Delivered views

The frontend adds Overview, Composition, Structures, Properties, Data quality,
Comparison, and Samples tabs inside the existing Results workspace. Property
selection renders one bounded histogram at a time. Every chart-like view has a
numeric or tabular representation. Stable sample references link aggregate
results back to source object and row without adding a workspace redesign.

## Integration

- Tool Registry owns strict parameters and resource caps.
- Mock Planner routes explicit dataset-exploration requests to the one product
  tool and can bind only an explicit `split` column for train/test comparison.
- API and worker object stores expose Profile 2.0 and canonical object IDs.
- Existing generic table, composition, structure, trajectory, phonon,
  reciprocal, volumetric, Planner, and runtime semantics remain available.
- No dependency, real LLM, network call, external asset, arbitrary code, ML
  evaluator, embedding, clustering, or global workspace feature was added.

## Resource policy

The hard limits are 100,000 rows, 512 columns, 64 properties, 256 categories,
200 linked sample rows, 100 histogram bins, 256 structures, 5,000 atoms per
structure, 128 warnings, and 8,000,000 bytes per artifact. Over-cap rows,
columns, structures, atoms, and artifact bytes fail explicitly. Display lists
are deterministically bounded and disclose truncation.

## Explicit limits

Formula duplicates are not structure duplicates. Structure duplicates require
equal canonical normalized object hashes. Near-duplicate detection is not
implemented. IQR findings are statistical candidates, not scientific errors.
Space groups are adapter-derived with the explicit fixed `symprec` parameter.
ML evaluation is Phase 10K-3, composition space is Phase 10K-4, and Agent
automation remains Phase 10L.
