# Phase 10E-7 RDF Implementation

## 1. Scope

Implemented:

- `structure.rdf`
- periodic-only static radial distribution function generation
- fixed radial bins with deterministic centers and edges
- `number_density` shell-volume normalization
- ordered center-element to neighbor-element partial RDF records
- strict site, bin, neighbor, and partial-pair caps
- `rdf.json`
- `rdf_plot.json`
- `summary.md`
- `recipe.json`
- Tool Registry params schema and resource limits
- Mock Planner routing for RDF prompts
- adapter, fixture, registry, planner-routing, artifact-contract, security, and persisted execution tests

Not implemented:

- browser/API evidence for RDF
- full `structure.viewer_3d`
- WebGL / Three.js renderer
- Brillouin-zone 3D
- phonon bands / DOS
- advanced local environment classification
- experimental PDF fitting
- neutron scattering refinement
- X-ray total scattering analysis
- trajectory or time-averaged RDF
- notebook or script execution
- external API workflows

## 2. Tool ID

- `structure.rdf`

The tool is a static RDF adapter for periodic crystalline structures. It is not an experimental PDF fitting, scattering refinement, phonon DOS, local-environment classification, coordination histogram replacement, or 3D viewer tool.

## 3. Method

- RDF definition: count interatomic distances under periodic boundary conditions up to `r_max_angstrom`, bin into fixed radial bins, and normalize by shell volume, neighbor number density, and center-site count.
- periodic-image policy: require `pbc == [true, true, true]` and positive lattice volume; neighbor distances come from `pymatgen Structure.get_all_neighbors(r_max)`.
- cutoff: bounded finite `r_max_angstrom`, default `8.0`.
- bin width: bounded finite `bin_width_angstrom`, default `0.1`.
- normalization: `number_density` only.
- partial RDF: optional ordered `center_element -> neighbor_element` records, sorted deterministically and capped by `max_partial_pairs`.
- deterministic behavior: bins sorted by radius, partial pairs sorted by element key, warnings sorted by code, numeric values rounded to 6 decimals, and artifact filenames fixed.

Limitations:

- Only periodic crystalline structures are supported in Phase 10E-7.
- Non-periodic structures and missing/non-positive volume return typed errors.
- Large structures, excessive bins, and excessive neighbor records are rejected rather than silently producing ambiguous RDFs.
- Browser/API evidence is deferred to Phase 10E-8.
- Official examples remain mapping references only unless directly evidenced in a later phase.

## 4. Artifact Contract

### `rdf.json`

Required fields include:

- `artifactType: "structure.rdf"`
- `schema_version: "phase10e7.rdf.v1"`
- `tool_id: "structure.rdf"`
- `source`
- `structure`
- `structures`
- `parameters`
- `rdf.r_angstrom`
- `rdf.g_r`
- `rdf.counts`
- `rdf.bin_edges_angstrom`
- `rdf.normalization`
- optional `partial_rdf`
- `limits`
- `warnings`
- `security`

### `rdf_plot.json`

Required fields include:

- `artifactType: "structure.rdf_plot"`
- `schema_version: "phase10e7.static_chart.v1"`
- `tool_id: "structure.rdf"`
- `chart_type: "line"`
- `x_axis`
- `y_axis`
- `series`
- `metadata`
- `security`

### `summary.md`

Human-readable input, method, results, limits, warnings, and security summary. It explicitly states that generated artifacts contain no JavaScript, no external URLs, no WebGL renderer, and no full 3D viewer.

### `recipe.json`

Reproducible recipe with:

- `schema_version: "phase10e7.recipe.v1"`
- `tool_id: "structure.rdf"`
- normalized params
- deterministic steps
- dependency versions
- artifact list
- numeric policy

## 5. Params

```json
{
  "r_max_angstrom": 8.0,
  "bin_width_angstrom": 0.1,
  "normalization": "number_density",
  "include_partial_pairs": true,
  "max_partial_pairs": 64,
  "max_sites": 500,
  "max_bins": 1000,
  "max_neighbors_total": 200000,
  "plot_kind": "line"
}
```

The Tool Registry params schema uses `additionalProperties: false`.

Validation rules:

- unknown params are rejected.
- `normalization` must be `number_density`.
- `plot_kind` must be `line`.
- `ceil(r_max_angstrom / bin_width_angstrom) <= max_bins`.
- `max_sites`, `max_neighbors_total`, and `max_partial_pairs` are enforced.
- non-periodic structures are rejected.
- missing or non-positive lattice volume is rejected.

## 6. Security Boundary

- no artifact JavaScript
- no external URLs
- no HTML app
- no renderer bundle
- no WebGL / canvas viewer
- no full 3D viewer
- no notebook execution
- no script execution
- no external API calls
- no arbitrary local path reads
- no real LLM usage
- no new dependencies

## 7. Planner Routing

Routes to `structure.rdf`:

- RDF
- radial distribution function
- pair distribution
- pair distribution `g(r)`
- Chinese RDF / radial-distribution prompts

Deferred or not routed to RDF:

- XRD
- coordination histogram
- full interactive 3D viewer
- WebGL
- Brillouin-zone 3D
- phonon bands / DOS
- experimental PDF fitting
- neutron scattering refinement
- Rietveld refinement

## 8. Tests

Added:

- `tests/test_phase10e7_rdf.py`

Coverage includes:

- numeric JSON artifact contract
- static chart artifact contract
- summary and recipe generation
- deterministic output
- bin edge and bin center determinism
- global counts and `number_density` normalization
- partial RDF enabled / disabled behavior
- partial pair ordering and cap warnings
- cutoff and bin-width sensitivity
- CIF / POSCAR / Structure dict fixtures
- invalid params
- non-periodic structure rejection
- site, bin, and neighbor caps
- no JavaScript / no external URL assertions
- Tool Registry schema
- Mock Planner routing
- XRD / coordination / 3D / phonon / fitting routing boundaries
- persisted AnalysisPlan execution through QueueWorkerRuntime

## 9. Evidence Policy

Phase 10E-7 does not add browser/API evidence.

Phase 10E-8 should capture browser/API/artifact evidence for `structure.rdf` through the persisted planner/job path.

## 10. Deferred Scope

- RDF browser/API evidence
- full `structure.viewer_3d`
- WebGL renderer
- Three.js
- Brillouin-zone 3D
- phonon bands / DOS
- advanced local environment classification
- experimental PDF fitting / scattering refinement
- trajectory RDF
- notebook/script extraction
- external API workflows
