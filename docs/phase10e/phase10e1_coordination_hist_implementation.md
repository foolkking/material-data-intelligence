# Phase 10E-1 Coordination Histogram Implementation

## 1. Scope

Implemented:

- `structure.coordination_hist`
- deterministic distance-cutoff neighbor policy
- `coordination_hist.json`
- `coordination_hist_plot.json`
- `summary.md`
- `recipe.json`
- Tool Registry params schema and resource limits
- Mock Planner routing for coordination-number prompts
- unit, fixture, registry, planner-routing, artifact-contract, and persisted execution tests

Not implemented:

- `structure.xrd`
- `structure.rdf`
- full `structure.viewer_3d`
- WebGL / Three.js renderer
- Brillouin zone 3D
- phonon bands / DOS
- notebook or script execution
- external API workflows
- advanced local environment classification

## 2. Tool ID

- `structure.coordination_hist`

The tool is a static structure physics adapter. It is not an advanced crystal-chemistry classifier and does not perform Voronoi, CrystalNN, bond-valence, oxidation-state, or phase-identification analysis.

## 3. Method

- neighbor policy: `distance_cutoff`
- default cutoff: `3.0` angstrom
- comparison rule: `distance <= cutoff_angstrom`
- default max sites: `500`
- default max neighbors per site: `128`
- deterministic ordering: structures by label, sites by index, neighbors by distance/index/element, bins by coordination number, pair counts by center/neighbor element
- numeric rounding: distances and fractions rounded to 6 decimals

Limitations:

- Results are cutoff-sensitive.
- Coordination numbers are geometric neighbor counts, not chemical environment labels.
- Large structures are bounded by site and neighbor limits.

## 4. Artifact Contract

### `coordination_hist.json`

Required fields include:

- `artifactType: "structure.coordination_hist"`
- `schema_version: "phase10e1.coordination_hist.v1"`
- `tool_id`
- `source`
- `structure`
- `structures`
- `parameters`
- `histogram.bins`
- `by_element`
- `pair_counts`
- `site_details`
- `limits`
- `warnings`
- `security`

### `coordination_hist_plot.json`

Required fields include:

- `artifactType: "structure.coordination_hist_plot"`
- `schema_version: "phase10e1.static_chart.v1"`
- `chart_type: "bar"`
- `x_axis`
- `y_axis`
- `series`
- `metadata`
- `security`

### `summary.md`

Human-readable method, results, limits, warnings, and security summary.

### `recipe.json`

Reproducible recipe with:

- `schema_version: "phase10e1.recipe.v1"`
- `tool_id: "structure.coordination_hist"`
- normalized params
- deterministic steps
- dependency versions
- artifact list
- numeric tolerance policy

## 5. Params

```json
{
  "neighbor_policy": "distance_cutoff",
  "cutoff_angstrom": 3.0,
  "max_sites": 500,
  "max_neighbors_per_site": 128,
  "include_site_details": true,
  "group_by_element": true,
  "include_pair_counts": true,
  "plot_kind": "bar"
}
```

The Tool Registry params schema uses `additionalProperties: false`.

## 6. Security Boundary

- no artifact JavaScript
- no external URLs
- no HTML viewer
- no WebGL renderer
- no full 3D viewer
- no notebook execution
- no script execution
- no external API calls
- no arbitrary local path reads
- no real LLM usage

## 7. Planner Routing

Routes to `structure.coordination_hist`:

- coordination histogram
- coordination number histogram
- coordination number
- coordination distribution
- neighbor count
- count neighbors
- fixed cutoff
- 配位数
- 配位数直方图
- 邻居数

Deferred / not routed to coordination:

- XRD
- RDF
- full interactive 3D viewer
- WebGL
- Brillouin zone 3D
- phonon bands / DOS
- Voronoi local environment analysis
- CrystalNN chemical environment classification

## 8. Tests

Added or updated:

- `tests/test_phase10e1_coordination_hist.py`
- `tests/test_adapters.py`
- `tests/test_phase10d1_viewer_scene_metadata.py`

Coverage includes:

- numeric JSON artifact contract
- static chart artifact contract
- summary and recipe generation
- deterministic output
- cutoff-sensitive counts
- CIF / POSCAR / Structure dict fixtures
- invalid params
- malformed input
- site and neighbor truncation warnings
- no JavaScript / no external URL assertions
- Tool Registry schema
- Mock Planner routing
- deferred XRD/RDF/3D/phonon boundaries
- persisted AnalysisPlan execution through QueueWorkerRuntime

## 9. Evidence Policy

Phase 10E-1 does not add browser/API evidence.

Phase 10E-2 should capture browser/API/artifact evidence for `structure.coordination_hist` through the persisted planner/job path.

## 10. Deferred Scope

- `structure.xrd`
- `structure.rdf`
- full `structure.viewer_3d`
- WebGL renderer
- Three.js
- Brillouin zone 3D
- phonon bands / DOS
- advanced local environment classification
- notebook/script extraction
- external API workflows
