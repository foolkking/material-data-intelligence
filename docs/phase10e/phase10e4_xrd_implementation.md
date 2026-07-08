# Phase 10E-4 XRD Implementation

## 1. Scope

Implemented:

- `structure.xrd`
- deterministic CuKa-only XRD pattern generation with `pymatgen.analysis.diffraction.xrd.XRDCalculator`
- `xrd_pattern.json`
- `xrd_plot.json`
- `summary.md`
- `recipe.json`
- Tool Registry params schema and resource limits
- Mock Planner routing for XRD prompts
- adapter, fixture, registry, planner-routing, artifact-contract, security, and persisted execution tests

Not implemented:

- `structure.rdf`
- full `structure.viewer_3d`
- WebGL / Three.js renderer
- Brillouin-zone 3D
- phonon bands / DOS
- advanced local environment classification
- experimental XRD fitting
- Rietveld refinement
- notebook or script execution
- external API workflows

## 2. Tool ID

- `structure.xrd`

The tool is a static simulated XRD adapter for periodic crystalline structures. It is not an experimental fitting, Rietveld refinement, database lookup, RDF, phonon, or 3D viewer tool.

## 3. Method

- calculator: `pymatgen.analysis.diffraction.xrd.XRDCalculator`
- radiation: `CuKa` only
- default two-theta range: `0.0` to `90.0` degrees
- intensity scale: relative intensity from `XRDCalculator`
- intensity threshold: applied after calculator output
- peak limit: deterministic `max_peaks` truncation after filtering and sorting
- deterministic ordering: peaks sorted by `two_theta_deg`, intensity, and d-spacing; HKL metadata sorted by HKL tuple and multiplicity
- numeric rounding: two-theta, d-spacing, and intensity rounded to 6 decimals

Limitations:

- Phase 10E-4 does not implement additional radiation sources, custom wavelengths, broadening, texture correction, experimental profile fitting, Rietveld refinement, or database lookup.
- Browser/API evidence is deferred to Phase 10E-5.
- Official examples remain mapping references only unless directly evidenced in a later phase.

## 4. Artifact Contract

### `xrd_pattern.json`

Required fields include:

- `artifactType: "structure.xrd"`
- `schema_version: "phase10e4.xrd_pattern.v1"`
- `tool_id`
- `source`
- `structure`
- `structures`
- `parameters`
- `radiation`
- `two_theta_range`
- `pattern.peaks`
- `pattern.peak_count`
- `pattern.intensity_scale`
- `limits`
- `warnings`
- `security`

### `xrd_plot.json`

Required fields include:

- `artifactType: "structure.xrd_plot"`
- `schema_version: "phase10e4.static_chart.v1"`
- `tool_id: "structure.xrd"`
- `chart_type: "stem"`
- `x_axis`
- `y_axis`
- `series`
- `metadata`
- `security`

### `summary.md`

Human-readable input, method, results, limits, warnings, and security summary. It explicitly states that generated artifacts contain no JavaScript, no external URLs, no WebGL renderer, and no full 3D viewer.

### `recipe.json`

Reproducible recipe with:

- `schema_version: "phase10e4.recipe.v1"`
- `tool_id: "structure.xrd"`
- normalized params
- deterministic steps
- dependency versions
- artifact list
- numeric tolerance policy

## 5. Params

```json
{
  "radiation": "CuKa",
  "two_theta_min": 0.0,
  "two_theta_max": 90.0,
  "intensity_threshold": 0.0,
  "peak_merge_tolerance": 0.05,
  "max_peaks": 500,
  "include_hkl": true,
  "plot_kind": "stem"
}
```

The Tool Registry params schema uses `additionalProperties: false`.

Validation rules:

- `radiation` must be `CuKa`.
- `plot_kind` must be `stem`.
- `two_theta_min < two_theta_max`.
- `intensity_threshold` is bounded from `0.0` to `100.0`.
- `peak_merge_tolerance` is recorded and bounded, but Phase 10E-4 relies on `XRDCalculator` peak generation rather than adding a separate physical model.
- `max_peaks` is enforced.

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

Routes to `structure.xrd`:

- XRD pattern
- powder XRD
- X-ray diffraction
- diffraction peaks
- simulated XRD

Deferred or not routed to XRD:

- RDF
- coordination histogram
- full interactive 3D viewer
- WebGL
- Brillouin-zone 3D
- phonon bands / DOS
- Rietveld refinement
- experimental XRD fitting
- peak broadening and profile fitting

## 8. Tests

Added:

- `tests/test_phase10e4_xrd.py`

Coverage includes:

- numeric JSON artifact contract
- static chart artifact contract
- summary and recipe generation
- deterministic output
- two-theta range / intensity / max-peaks filtering
- HKL include/exclude behavior
- CIF / POSCAR / Structure dict fixtures
- invalid params
- malformed input
- no JavaScript / no external URL assertions
- Tool Registry schema
- Mock Planner routing
- deferred RDF/coordination/3D/phonon/fitting boundaries
- persisted AnalysisPlan execution through QueueWorkerRuntime

## 9. Evidence Policy

Phase 10E-4 does not add browser/API evidence.

Phase 10E-5 should capture browser/API/artifact evidence for `structure.xrd` through the persisted planner/job path.

## 10. Deferred Scope

- `structure.rdf`
- full `structure.viewer_3d`
- WebGL renderer
- Three.js
- Brillouin-zone 3D
- phonon bands / DOS
- advanced local environment classification
- experimental XRD fitting
- Rietveld refinement
- notebook/script extraction
- external API workflows
