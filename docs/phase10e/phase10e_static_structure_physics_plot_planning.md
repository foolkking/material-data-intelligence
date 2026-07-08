# Phase 10E Static Structure Physics Plot Planning

## 1. Background

Phase 10A added first-batch table and generic visualization adapters with browser/API/artifact evidence. Phase 10B added composition visualization adapters and evidence. Phase 10C added lightweight structure summary adapters and evidence. Phase 10D added static viewer scene metadata/export package tools, browser/API evidence, and schema-aware static artifact preview hardening.

The platform now has a validated structure parsing and artifact path, but it still has no static structure physics plot adapters. Phase 10E plans those adapters before implementation so dependency, numeric tolerance, fixture, and evidence policies are explicit.

## 2. Current Capability Baseline

- Table / viz adapters: `table.distribution_summary`, `viz.scatter`, `viz.histogram`, `viz.correlation`.
- Composition adapters: `composition.summary`, `composition.formula_statistics`, `composition.elements_hist`, `composition.ptable_heatmap`, `composition.chem_sys_treemap`, `composition.chem_sys_sunburst`.
- Lightweight structure adapters: `structure.summary`, `structure.lattice_summary`, `structure.spacegroup_summary`, `structure.composition_from_structure`, `structure.preview_metadata`.
- Viewer metadata/export package: `structure.viewer_scene_metadata`, `structure.viewer_export_package`.
- Static preview hardening: Phase 10D-3 adds schema-aware frontend preview for `viewer_scene.json`, `viewer_assets_manifest.json`, `summary.md`, and `recipe.json`.
- Evidence status: Phase 10A/10B/10C/10D browser/API evidence is complete for implemented tools only. Static physics tools have no evidence and are not implemented.

## 3. Why This Phase Only Plans

- Dependency uncertainty: local environment has `pymatgen`, `pymatviz`, `numpy`, `scipy`, `matplotlib`, `plotly`, and `spglib`, but implementation must still lock exact APIs and CI behavior.
- Numeric tolerance: XRD peak positions/intensities, RDF bins, and coordination counts all require explicit tolerance policy.
- Fixture complexity: deterministic small structures are needed before official examples can be used as evidence.
- Definition ambiguity: XRD radiation/peak merge policy, RDF normalization, and coordination neighbor strategy can change outputs materially.
- CI runtime: physics calculations must stay bounded and deterministic.
- Official examples readiness: relevant official examples are future-scope widgets or README mappings, not direct-uploadable PASS cases.
- Evidence cost: Browser/API evidence should follow implementation in a separate phase.

## 4. Candidate Adapter Pool

- `structure.xrd`
- `structure.rdf`
- `structure.coordination_hist`

## 5. Recommended Next Scope

Recommended Phase 10E-1 implementation order:

1. `structure.coordination_hist`: lowest dependency risk if it reuses the existing Phase 10C/10D structure parser and a conservative deterministic neighbor policy.
2. `structure.xrd`: good second candidate because `pymatgen` is available and `XRDCalculator` is the likely engine, but peak tolerance and reference fixture assertions must be fixed first.
3. `structure.rdf`: defer until cutoff, binning, periodic wrapping, and normalization policy are fully specified.

Do not proceed to phonon or full 3D viewer work in Phase 10E-1.

## 6. Deferred Scope

- Full interactive 3D viewer.
- WebGL renderer.
- Brillouin zone 3D.
- Phonon bands / DOS.
- Trajectory RDF or time-averaged RDF.
- Experimental XRD fitting, phase identification, Rietveld refinement, or database lookup.
- Notebook extraction.
- Script execution.
- External API workflows.

## 7. Candidate Adapter Design Drafts

### `structure.xrd`

- tool_id: `structure.xrd`
- purpose: generate a deterministic powder XRD pattern from one or more periodic structures.
- input resource: periodic `Structure` or bounded structure collection from uploaded CIF, POSCAR/CONTCAR, Structure JSON, or normalized structure dict.
- params schema: `wavelength`, `twoThetaRange`, `peakMergeTolerance`, `intensityScale`, `maxStructures`, `maxPeaks`.
- output artifacts: `xrd_pattern.json`, `xrd_pattern_plot.json`, optional `xrd_pattern.html`, `summary.md`, `recipe.json`.
- numeric JSON schema: see Section 8.
- static chart artifact schema: Plotly-compatible line/bar pattern with peak hover metadata.
- dependency policy: prefer `pymatgen.analysis.diffraction.xrd.XRDCalculator`; do not add dependencies in Phase 10E-1.
- warning model: non-periodic input, partial occupancy, peak merge, max peak truncation, dependency/version warning.
- typed errors: `xrd_dependency_missing`, `xrd_non_periodic_structure`, `xrd_generation_failed`, `xrd_invalid_params`, `artifact_write_failed`.
- deterministic behavior: fixed wavelength, fixed two-theta range, sorted peaks, rounded numeric fields, stable hkl ordering.
- numeric tolerance: two-theta tolerance initially `1e-3` degrees for fixture assertions; intensity tolerance `1e-3` after normalization.
- fixture strategy: simple cubic Si, NaCl, or rutile TiO2 fixture with pinned expected peak windows; avoid official widget examples as PASS evidence.
- security boundary: no network, no external database lookup, no artifact JS execution.
- evidence strategy: Phase 10E-1 adapter tests only; Phase 10E-2 browser/API evidence after implementation.

### `structure.rdf`

- tool_id: `structure.rdf`
- purpose: compute a static radial distribution function for periodic structures.
- input resource: periodic `Structure` or small structure collection.
- params schema: `cutoff`, `binWidth`, `sigma`, `speciesPairs`, `normalization`, `maxStructures`, `maxSites`.
- output artifacts: `rdf.json`, `rdf_plot.json`, optional `rdf_plot.html`, `summary.md`, `recipe.json`.
- numeric JSON schema: see Section 9.
- static chart artifact schema: Plotly-compatible `r` vs `g(r)` traces, one trace per selected species pair or total RDF.
- dependency policy: reuse `numpy` and existing structure parser first; use `scipy` only for optional smoothing if already available and gated.
- warning model: finite-size warning, small-cell warning, cutoff larger than half effective cell length, sparse pair count, smoothing warning.
- typed errors: `rdf_non_periodic_structure`, `rdf_invalid_cutoff`, `rdf_generation_failed`, `rdf_empty_structure`, `artifact_write_failed`.
- deterministic behavior: fixed bin edges, stable species pair ordering, rounded `r` and `g(r)` values.
- numeric tolerance: bin edge exactness by construction; `g(r)` fixture tolerance must be pinned per normalization policy.
- fixture strategy: start with simple cubic single-species fixture and NaCl-like binary fixture; defer trajectory fixtures.
- security boundary: no trajectory parsing, no notebook/script execution, no external simulation workflow.
- evidence strategy: defer Browser/API evidence to Phase 10E-2 after numeric policy is proven.

### `structure.coordination_hist`

- tool_id: `structure.coordination_hist`
- purpose: compute coordination number histograms from periodic structures using a bounded neighbor policy.
- input resource: periodic `Structure` or small structure collection.
- params schema: `neighborStrategy`, `cutoff`, `tolerance`, `groupByElement`, `speciesPairs`, `maxStructures`, `maxSites`.
- output artifacts: `coordination_hist.json`, `coordination_hist_plot.json`, optional `coordination_hist.html`, `summary.md`, `recipe.json`.
- numeric JSON schema: see Section 10.
- static chart artifact schema: Plotly-compatible bar chart with bins by coordination number and optional grouped element traces.
- dependency policy: first implementation should use a simple deterministic distance-cutoff/minimum-distance policy. Advanced Voronoi/local environment analysis remains deferred unless already stable.
- warning model: ambiguous cutoff, missing lattice, partial occupancy, site truncation, species filter produces empty counts.
- typed errors: `coordination_non_periodic_structure`, `coordination_missing_lattice`, `coordination_invalid_params`, `coordination_generation_failed`, `artifact_write_failed`.
- deterministic behavior: stable site ordering, stable element ordering, fixed bins, rounded distances, sorted output.
- numeric tolerance: neighbor distance comparison uses `cutoff + tolerance`, with default tolerance documented and asserted.
- fixture strategy: simple cubic Si and NaCl fixtures with expected coordination counts under fixed cutoff.
- security boundary: no crystal chemistry judgment, no external lookup, no artifact JS execution.
- evidence strategy: recommended first Phase 10E-1 adapter, then Phase 10E-2 browser/API evidence.

## 8. XRD Design Draft

### Params

```json
{
  "wavelength": "CuKa",
  "twoThetaRange": [0, 90],
  "peakMergeTolerance": 0.01,
  "intensityScale": "max_100",
  "maxStructures": 10,
  "maxPeaks": 200
}
```

### `xrd_pattern.json`

```json
{
  "artifactType": "structure.xrd",
  "wavelength": "CuKa",
  "twoThetaRange": [0, 90],
  "intensityScale": "max_100",
  "structures": [
    {
      "structureId": "structure_1",
      "formula": "Si",
      "peaks": [
        {
          "twoTheta": 28.44,
          "intensity": 100.0,
          "dSpacing": 3.14,
          "hkls": [{"h": 1, "k": 1, "l": 1, "multiplicity": 8}]
        }
      ],
      "warnings": []
    }
  ],
  "warnings": []
}
```

### Explicit Non-Scope

- No phase identification.
- No Rietveld refinement.
- No experimental XRD fitting.
- No crystallographic database lookup.
- No external API workflow.

## 9. RDF Design Draft

### Params

```json
{
  "cutoff": 10.0,
  "binWidth": 0.1,
  "sigma": 0.0,
  "speciesPairs": [],
  "normalization": "number_density",
  "maxStructures": 10,
  "maxSites": 500
}
```

### `rdf.json`

```json
{
  "artifactType": "structure.rdf",
  "cutoff": 10.0,
  "binWidth": 0.1,
  "normalization": "number_density",
  "pairs": [
    {
      "pair": "Si-Si",
      "r": [0.05, 0.15],
      "gR": [0.0, 0.0],
      "counts": [0, 0]
    }
  ],
  "finiteSizeWarnings": [],
  "warnings": []
}
```

### Explicit Non-Scope

- No molecular dynamics trajectory RDF.
- No time-averaged RDF.
- No large trajectory parsing.
- No external simulation workflow.

## 10. Coordination Histogram Design Draft

### Params

```json
{
  "neighborStrategy": "distance_cutoff",
  "cutoff": 3.0,
  "tolerance": 0.05,
  "groupByElement": true,
  "speciesPairs": [],
  "maxStructures": 50,
  "maxSites": 1000
}
```

### `coordination_hist.json`

```json
{
  "artifactType": "structure.coordination_hist",
  "neighborStrategy": "distance_cutoff",
  "cutoff": 3.0,
  "tolerance": 0.05,
  "structureCount": 1,
  "siteCount": 8,
  "bins": [
    {"coordination": 6, "count": 8, "fraction": 1.0}
  ],
  "byElement": {
    "Na": [{"coordination": 6, "count": 4}],
    "Cl": [{"coordination": 6, "count": 4}]
  },
  "failedSites": [],
  "warnings": []
}
```

### Explicit Non-Scope

- No advanced local environment classification.
- No Voronoi polyhedra unless dependency and policy are separately approved.
- No bond valence analysis.
- No crystal chemistry judgment.

## 11. Dependency Matrix

| Candidate | Required Dependency | Already Available | New Dependency Needed | Risk | Recommendation |
|---|---|---:|---:|---|---|
| `structure.xrd` | `pymatgen`, `numpy`, `plotly` | yes | no | medium: XRD API/tolerance/peak assertions | Candidate for Phase 10E-1 only after fixture tolerances are pinned |
| `structure.rdf` | `numpy`, optional `scipy`, existing structure parser | yes | no | medium-high: normalization and cutoff ambiguity | Defer until policy is fixed |
| `structure.coordination_hist` | existing structure parser, `numpy`; optional pymatgen neighbor helpers | yes | no | low-medium: neighbor definition ambiguity | Recommended first if using conservative cutoff policy |
| phonon tools | phonopy/pymatgen phonon objects | not planned | no in 10E | high | Defer to Phase 10G |

Environment check on 2026-07-08 showed `pymatgen`, `pymatviz`, `numpy`, `scipy`, `matplotlib`, `plotly`, and `spglib` available. Phase 10E planning does not add or install dependencies.

## 12. Official Examples Mapping

| Candidate Adapter | Official Case | Case Type | Input Data | Expected Artifact | Current Support | Risk |
|---|---|---|---|---|---|---|
| `structure.xrd` | `widgets_vscode_interactive_demo` | `future_scope_widget_or_structure` | script/widget source with XRD widget | `xrd_pattern.json` / widget output | Mapping only | Widget/script, no direct upload evidence |
| `structure.rdf` | `widgets_vscode_interactive_demo` | `future_scope_widget_or_structure` | script/widget source with RDF widget | `rdf.json` / widget output | Mapping only | RDF widget semantics and data extraction unresolved |
| `structure.coordination_hist` | no direct verified official case | none | deterministic project fixtures first | `coordination_hist.json` | Not supported yet | Neighbor policy needs fixture proof |
| `structure.viewer_3d` | `readme_structure_3d` | `readme_function_demo` | README demo | viewer artifact | Deferred | Full 3D viewer not in Phase 10E |
| phonon tools | `readme_phonon_bands`, `matbench_phonons`, `phonons_mlip_phonons` | README / future / extraction | phonon data | phonon artifacts | Deferred | Requires separate phonon planning |

No mapping row is a PASS claim.

## 13. Tool Registry Plan

- Domain: `structure`.
- Tool ids: `structure.xrd`, `structure.rdf`, `structure.coordination_hist`.
- Params schemas must be whitelist-only and reject arbitrary kwargs.
- Input schema must require periodic structure resources for all three adapters.
- Resource limits must cap structure count, site count, peak count, bin count, and artifact size.
- Outputs must include one deterministic numeric JSON artifact, optional static chart artifact, `summary.md`, and `recipe.json`.
- Permissions must remain local compute only; no network, no notebook/script execution, no external database lookup.

## 14. Planner Routing Plan

| Prompt intent | Planned routing |
|---|---|
| "calculate XRD", "powder diffraction", "diffraction pattern" | `structure.xrd` after implementation |
| "RDF", "radial distribution", "pair distribution" | `structure.rdf` after implementation |
| "coordination number", "coordination histogram", "neighbor count" | `structure.coordination_hist` after implementation |
| "phonon bands", "phonon DOS" | future_scope, do not route in 10E |
| "3D viewer", "WebGL", "Brillouin zone 3D" | future_scope, do not route to static physics tools |

Routing priority should put explicit physics intents before generic structure summary, but unsupported 3D/phonon prompts must not be converted to XRD/RDF/coordination.

## 15. Artifact Contract Plan

- `xrd_pattern.json`: numeric peak list, wavelength, range, intensity scale, hkls, warnings.
- `xrd_pattern_plot.json`: static Plotly-compatible traces.
- `rdf.json`: bin centers/edges, `g(r)`, counts, species pair metadata, normalization, warnings.
- `rdf_plot.json`: static Plotly-compatible traces.
- `coordination_hist.json`: bins, counts, by-element counts, strategy, cutoff, failed sites, warnings.
- `coordination_hist_plot.json`: static Plotly-compatible bar traces.
- `summary.md`: human-readable assumptions, limits, warnings, and non-scope.
- `recipe.json`: tool id, inputs, params, dependency versions, numeric tolerance, artifact list, deterministic flag.

## 16. Frontend Rendering Strategy

- Reuse existing static JSON/Markdown and Plotly artifact preview conventions.
- Do not use WebGL or 3D rendering.
- Show numeric JSON summary in normal mode and raw JSON in Developer mode.
- Static chart fallback must remain available if HTML export is disabled.
- Mobile preview should prioritize summary, warnings, and artifact list before raw numeric arrays.

## 17. Security Boundary

- Do not execute artifact JavaScript.
- Do not load external URLs from artifacts.
- Do not allow arbitrary local path reads.
- No notebook/script execution.
- No external API workflows.
- Enforce artifact size limits and redaction policy.
- Keep recipes free of API keys, tokens, Authorization headers, and user secrets.

## 18. Test Plan

- Unit tests for each adapter and typed error path.
- Numeric deterministic tests with pinned small fixtures and tolerance assertions.
- Fixture tests for CIF, POSCAR, Structure JSON, malformed input, non-periodic input, and partial occupancy warnings.
- Registry tests for domain, params schema, resource limits, and output artifacts.
- Planner routing tests for XRD/RDF/coordination and future-scope 3D/phonon prompts.
- API execution tests for plan validate, persisted plan, job completion, ToolCall status, and artifacts.
- Frontend artifact rendering tests for JSON, static chart, summary, recipe, Developer mode.
- Browser evidence tests in Phase 10E-2, not Phase 10E-1.
- Regression tests for Phase 8B, 9D, 10A, 10B, 10C, and 10D boundaries.

## 19. Risk Assessment

- XRD peak tolerance and wavelength defaults can change fixture expectations.
- Radiation source assumptions must be visible in params and recipes.
- Symmetry/conventional-cell ambiguity can change peak lists.
- RDF cutoff and bin width strongly affect results.
- RDF normalization is not universally defined across use cases.
- Coordination number depends on neighbor strategy and cutoff.
- Partial occupancy/disorder can produce ambiguous physics outputs.
- Large structures can increase runtime and artifact size.
- Dependency APIs may drift across pymatgen/pymatviz versions.
- CI runtime must stay bounded.
- Official examples are not direct verified for these tools.
- HTML/static chart artifacts must not execute artifact JS.

## 20. Recommended Phase Split

### Phase 10E-1 Static Physics Adapter Implementation

Implement one low-risk static physics adapter first. Recommended: `structure.coordination_hist` with deterministic distance-cutoff policy. Add `structure.xrd` only if XRD fixture tolerances are pinned before implementation starts.

### Phase 10E-2 Browser/API Evidence

Capture redacted API, artifact, and browser screenshots for implemented static physics tools.

### Phase 10E-3 Static Physics Preview Hardening

Harden frontend preview for XRD/RDF/coordination numeric JSON and static chart artifacts.

### Phase 10F Interactive 3D Viewer Planning / Prototype

Keep full viewer separate from static physics work.

### Phase 10G Phonon Visualization Planning

Plan phonon input contracts and plots separately.

## 21. Acceptance Criteria

- Planning docs exist and parse as Markdown.
- Candidate matrix exists.
- Phase 10E-1 implementation prompt exists.
- No adapter implementation or registry change is made in Phase 10E.
- Dependency and tolerance policy are documented.
- Official examples are mapped without PASS claims.
- Persistent files record the decision and remaining work.

## 22. Final Recommendation

Proceed next to Phase 10E-1: Static Physics Adapter Implementation.

Recommended first implementation target: `structure.coordination_hist`.

Do not implement full `structure.viewer_3d`, Brillouin-zone 3D, phonon tools, notebook/script extraction, external API workflows, or experimental XRD fitting in Phase 10E-1.
