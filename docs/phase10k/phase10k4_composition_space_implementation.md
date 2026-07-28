# Phase 10K-4 Composition Space Implementation

`dataset.composition_space` is one Profile 2.0-bound product capability. It
consumes one explicitly identified formula-bearing DataFrame, or two explicit
resources/groups for comparison, and emits `phase10k4.composition_space.v1`, an
inert Plotly companion, a summary, and a replay recipe.

The backend is the only scientific calculation authority. It reuses the
Profile `material_formula`, `material_property`, and stable sample identity
contracts, builds one atomic-number-ordered normalized element-fraction matrix,
fits deterministic two-dimensional PCA, and optionally fits bounded KMeans in
the original feature space. The frontend only validates and presents emitted
coordinates, clusters, color values, sample links, and numeric fallbacks.

The formal execution path remains:

```text
Profile 2.0 + canonical DataFrame
  -> Mock Planner explicit composition-space route
  -> PlanValidator
  -> QueueWorkerRuntime
  -> Tool Registry
  -> CompositionSpaceAdapter
  -> inert artifacts
  -> Composition Space Explorer
```

No learned embedding, model training, UMAP, t-SNE, arbitrary code, external
service, real LLM calculation, or browser-side PCA/KMeans is included.
