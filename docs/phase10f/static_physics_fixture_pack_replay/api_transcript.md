# API / Job Replay Transcript

## Replay Mode

- planner provider: `MockLLMProvider(fixed_plan=...)`
- real LLM: not used
- repository: `InMemoryRepositoryBundle`
- runtime: `QueueWorkerRuntime`
- registry: `load_manifests()`
- artifact storage: temporary local artifact roots
- object flow: fixture input text loaded into `object_store["structures"]`

The replay used the same persisted plan/job bridge pattern as the existing service-backed static physics tests.

## coordination_hist_small_crystal

- request path: `planner_jobs(...)`
- prompt: `Create a coordination number histogram for this structure.`
- selected tool: `structure.coordination_hist`
- job status: completed
- artifacts:
  - `coordination_hist.json`
  - `coordination_hist_plot.json`
  - `summary.md`
  - `recipe.json`

## xrd_small_crystal

- request path: `planner_jobs(...)`
- prompt: `Generate an XRD pattern for this structure.`
- selected tool: `structure.xrd`
- job status: completed
- artifacts:
  - `xrd_pattern.json`
  - `xrd_plot.json`
  - `summary.md`
  - `recipe.json`

## rdf_small_crystal

- request path: `planner_jobs(...)`
- prompt: `Create an RDF plot for this structure.`
- selected tool: `structure.rdf`
- job status: completed
- artifacts:
  - `rdf.json`
  - `rdf_plot.json`
  - `summary.md`
  - `recipe.json`

## Boundary

The transcript is fixture-pack replay evidence, not official examples PASS evidence.
