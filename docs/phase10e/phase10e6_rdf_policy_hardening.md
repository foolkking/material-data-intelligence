# Phase 10E-6 RDF Policy Hardening

## 1. Scope

- policy hardened: `structure.rdf` numeric policy, artifact contract, params schema, routing plan, readiness gate, and evidence plan.
- not implemented: `structure.rdf`, frontend RDF renderer, browser/API evidence, notebook/script extraction, trajectory RDF, full 3D viewer, WebGL renderer, phonon, experimental fitting, and Rietveld refinement.

This phase is planning-only. It does not add adapters, modify Tool Registry semantics, modify QueueWorkerRuntime, modify AnalysisPlanRepository, change `/planner/jobs`, or relax PlanValidator boundaries.

## 2. Baseline

- Phase 10E-4: `507d12432e3238ffd51453866ac4c9f1614c3511`, `507d124 Implement XRD adapter`.
- Phase 10E-5: `9d8addcbf59dfd2edc5ea425557f6a0f07866430`, `9d8addc Add XRD browser API evidence`.
- Phase 10E-5R2: `4c7e3928b11a5508d27dace20206caf018e8e28b`, `4c7e392 Complete XRD browser screenshot evidence`.
- current HEAD before Phase 10E-6: `4c7e3928b11a5508d27dace20206caf018e8e28b`.
- branch: `master`.
- git status before: clean.

## 3. Static Physics Current State

- coordination histogram: implemented and browser/API evidenced. It emits `coordination_hist.json`, `coordination_hist_plot.json`, `summary.md`, and `recipe.json`.
- XRD: implemented and browser/API evidenced. It emits `xrd_pattern.json`, `xrd_plot.json`, `summary.md`, and `recipe.json`.
- XRD evidence status: PASS after Phase 10E-5R2.
- XRD browser screenshots:
  - `docs/phase10e/browser_api_evidence/phase10e5_xrd/screenshots/01_job_completed.png`
  - `docs/phase10e/browser_api_evidence/phase10e5_xrd/screenshots/02_artifact_list.png`
  - `docs/phase10e/browser_api_evidence/phase10e5_xrd/screenshots/03_xrd_pattern_json_preview.png`
  - `docs/phase10e/browser_api_evidence/phase10e5_xrd/screenshots/04_xrd_plot_preview.png`
  - `docs/phase10e/browser_api_evidence/phase10e5_xrd/screenshots/05_summary_preview.png`
  - `docs/phase10e/browser_api_evidence/phase10e5_xrd/screenshots/06_recipe_preview.png`

## 4. RDF Policy Decisions

### RDF definition

For a periodic crystalline structure, RDF is computed by counting interatomic distances under periodic boundary conditions up to `r_max_angstrom`, binning distances into fixed-width radial bins, and normalizing by shell volume, number density, and center-site count.

This is not experimental pair distribution function fitting, neutron scattering refinement, X-ray total scattering analysis, phonon DOS, coordination histogram, or local environment classification.

### Periodic-image policy

- First implementation supports only periodic crystalline `pymatgen Structure` inputs.
- Require `pbc == [true, true, true]`.
- Require valid lattice and positive unit-cell volume.
- Use existing pymatgen periodic neighbor search, preferably `Structure.get_all_neighbors(r_max_angstrom)`, or an equivalent existing periodic distance helper.
- Reject non-periodic structures with typed error `RDF_NON_PERIODIC_STRUCTURE`.
- Reject missing/non-positive volume with typed error `RDF_INVALID_LATTICE_VOLUME`.

### Cutoff policy

- Parameter: `r_max_angstrom`.
- Default: `8.0`.
- Minimum: `0.5`.
- Maximum: `30.0`.
- Must be finite and recorded in `rdf.json`, `rdf_plot.json`, `summary.md`, and `recipe.json`.
- Warning `RDF_CUTOFF_SENSITIVE` is always emitted because RDF interpretation depends on cutoff.

### Bin policy

- Parameter: `bin_width_angstrom`.
- Default: `0.1`.
- Minimum: `0.01`.
- Maximum: `1.0`.
- Bin count is `ceil(r_max_angstrom / bin_width_angstrom)`.
- Reject params with typed error `RDF_BIN_LIMIT_EXCEEDED` when `bin_count > max_bins`.
- Bin edges are deterministic: `[0, bin_width, 2 * bin_width, ...]` with the final edge equal to `bin_count * bin_width`.
- Bin centers are deterministic: `(r_inner + r_outer) / 2`.
- Round bin edges, centers, counts-derived values, and plotted values to fixed precision.

### Normalization policy

First implementation uses one normalization only:

```text
number_density
```

Definition:

```text
g(r) = counts(r) / (N_center * rho_neighbor * shell_volume)
```

where:

- `N_center` is the number of center sites included.
- `rho_neighbor` is `neighbor_site_count / cell_volume`.
- `shell_volume` is `4*pi/3 * (r_outer^3 - r_inner^3)`.

Rules:

- Global RDF uses all sites as centers and all sites as neighbors.
- Self-pairs at exactly zero distance are excluded.
- Periodic images are counted when within cutoff.
- Normalization uses unit-cell volume and site count.
- If volume is missing or non-positive, return `RDF_INVALID_LATTICE_VOLUME`.
- Emit `RDF_NORMALIZATION_NUMBER_DENSITY_ONLY`.

### Partial RDF policy

- Parameter: `include_partial_pairs`, default `true`.
- Use ordered center-element to neighbor-element pairs.
- Pair keys sort by `center_element`, then `neighbor_element`.
- `A -> B` and `B -> A` are distinct partial RDF series because center-site normalization differs by center species.
- Parameter: `max_partial_pairs`, default `64`, range `1..256`.
- If requested ordered pairs exceed `max_partial_pairs`, retain the first deterministic sorted pairs and emit `RDF_PARTIAL_PAIRS_TRUNCATED`.
- Partial RDF uses the same bin edges and number-density shell normalization, but center and neighbor counts are species-specific.

### Site and runtime caps

- Parameter: `max_sites`, default `500`, range `1..5000`.
- Parameter: `max_neighbors_total`, default `200000`, range `1..2000000`.
- First implementation rejects structures exceeding `max_sites` with `RDF_SITE_LIMIT_EXCEEDED`; it does not silently truncate sites.
- If collected periodic neighbors exceed `max_neighbors_total`, return `RDF_NEIGHBOR_LIMIT_EXCEEDED` rather than silently truncating RDF counts.
- Large structures and trajectory RDF remain deferred.

### Deterministic behavior

- Structures are processed in stable label order.
- Sites are processed in site-index order.
- Periodic neighbor records are sorted by center index, distance, neighbor index, image vector if available, and neighbor element.
- Bin assignment is deterministic and uses half-open bins `[r_inner, r_outer)` except the final bin includes its upper edge.
- `r_angstrom`, `bin_edges_angstrom`, `g_r`, shell volumes, densities, and distances are rounded to 6 decimals.
- Global RDF appears before partial RDF series.
- Partial pairs sort by center element and neighbor element.
- Warnings sort through existing stable de-duplication.

## 5. Params Schema Plan

```json
{
  "r_max_angstrom": {
    "type": "number",
    "default": 8.0,
    "minimum": 0.5,
    "maximum": 30.0
  },
  "bin_width_angstrom": {
    "type": "number",
    "default": 0.1,
    "minimum": 0.01,
    "maximum": 1.0
  },
  "normalization": {
    "type": "string",
    "default": "number_density",
    "enum": ["number_density"]
  },
  "include_partial_pairs": {
    "type": "boolean",
    "default": true
  },
  "max_partial_pairs": {
    "type": "integer",
    "default": 64,
    "minimum": 1,
    "maximum": 256
  },
  "max_sites": {
    "type": "integer",
    "default": 500,
    "minimum": 1,
    "maximum": 5000
  },
  "max_bins": {
    "type": "integer",
    "default": 1000,
    "minimum": 1,
    "maximum": 5000
  },
  "max_neighbors_total": {
    "type": "integer",
    "default": 200000,
    "minimum": 1,
    "maximum": 2000000
  },
  "plot_kind": {
    "type": "string",
    "default": "line",
    "enum": ["line"]
  }
}
```

Validation rules:

- Unknown params rejected.
- `r_max_angstrom > 0`.
- `bin_width_angstrom > 0`.
- `ceil(r_max_angstrom / bin_width_angstrom) <= max_bins`.
- `normalization == "number_density"`.
- `plot_kind == "line"`.
- `max_sites`, `max_partial_pairs`, and `max_neighbors_total` enforced before writing artifacts.

## 6. Artifact Contract Plan

### `rdf.json`

Required semantics:

- `schema_version: "phase10e7.rdf.v1"`.
- `tool_id: "structure.rdf"`.
- source metadata.
- structure summary with formula, site count, species, PBC, and `volume_angstrom3`.
- normalized parameters.
- global RDF arrays:
  - `r_angstrom`.
  - `g_r`.
  - `counts`.
  - `bin_edges_angstrom`.
  - normalization metadata.
- optional `partial_rdf` array with ordered center/neighbor element pairs.
- limits with max sites, max bins, max neighbors, bin count, partial pair count, and truncation flag.
- warnings.
- security flags with `contains_javascript: false`, `external_urls: []`, and `external_urls_allowed: false`.

### `rdf_plot.json`

Required semantics:

- `schema_version: "phase10e7.static_chart.v1"`.
- `tool_id: "structure.rdf"`.
- `chart_type: "line"`.
- x-axis label: `r (angstrom)`.
- y-axis label: `g(r)`.
- deterministic global series named `All pairs`.
- optional partial-pair series only when enabled and within caps.
- metadata with formula, site count, cutoff, bin width, normalization, and pair count.
- same no-JavaScript and no-external-URL security flags.

### `summary.md`

Required sections:

- `Input`.
- `Method`.
- `Results`.
- `Limits`.
- `Security`.

The summary must explicitly state no artifact JavaScript, no external URLs, no WebGL renderer, and no full 3D viewer. It must not claim experimental PDF fitting, trajectory RDF, phonon DOS, or local environment classification.

### `recipe.json`

Required semantics:

- `schema_version: "phase10e7.recipe.v1"`.
- `tool_id: "structure.rdf"`.
- normalized inputs and params.
- deterministic steps:
  - `parse_structure`.
  - `validate_periodic_structure`.
  - `validate_lattice_volume`.
  - `validate_rdf_params`.
  - `build_radial_bins`.
  - `collect_periodic_neighbors`.
  - `count_global_distances`.
  - `normalize_by_number_density`.
  - `aggregate_partial_pairs`.
  - `round_numeric_values`.
  - `write_rdf_json`.
  - `write_static_chart_json`.
  - `write_summary`.
- `deterministic: true`.
- `dependencies.new_dependencies_added: false`.

## 7. Typed Errors / Warnings

Typed errors:

- `RDF_INPUT_MISSING`.
- `RDF_PARSE_FAILED`.
- `RDF_UNSUPPORTED_INPUT`.
- `RDF_INVALID_PARAMS`.
- `RDF_NON_PERIODIC_STRUCTURE`.
- `RDF_INVALID_LATTICE_VOLUME`.
- `RDF_SITE_LIMIT_EXCEEDED`.
- `RDF_BIN_LIMIT_EXCEEDED`.
- `RDF_NEIGHBOR_LIMIT_EXCEEDED`.
- `RDF_PAIR_LIMIT_EXCEEDED`.
- `RDF_ARTIFACT_WRITE_FAILED`.

Warnings:

- `RDF_NORMALIZATION_NUMBER_DENSITY_ONLY`.
- `RDF_CUTOFF_SENSITIVE`.
- `RDF_BIN_WIDTH_SENSITIVE`.
- `RDF_PERIODIC_IMAGES_REQUIRED`.
- `RDF_PARTIAL_PAIRS_TRUNCATED`.
- `RDF_LARGE_STRUCTURE_DEFERRED`.
- `RDF_BROWSER_EVIDENCE_DEFERRED`.
- `RDF_NOT_EXPERIMENTAL_PDF_FITTING`.
- `RDF_NO_PHONON_DOS`.

## 8. Planner Routing Plan

RDF prompts should route to `structure.rdf` after implementation:

- `计算 RDF`
- `生成 RDF`
- `计算径向分布函数`
- `生成径向分布函数`
- `Generate radial distribution function`
- `Create an RDF plot for this structure`
- `Compute pair distribution g(r)`
- `Show radial distribution g(r)`

Prompts that must not route to RDF:

- XRD prompts stay with `structure.xrd`.
- coordination histogram prompts stay with `structure.coordination_hist`.
- full 3D viewer, WebGL, Brillouin-zone, and phonon prompts remain deferred.
- experimental PDF fitting and neutron scattering refinement remain unsupported/future-scope.

Phase 10E-6 does not change routing implementation.

## 9. Official Examples Mapping

Official examples benchmark pack was read from:

```text
C:/Users/86182/Desktop/pymatviz_official_examples_test_suite
```

Audit summary:

- total cases: 61.
- by case type: 16 script-generated data, 11 external API required, 25 README function demos, 7 future-scope widget/structure, 2 direct-uploadable data.
- by verification status: 27 EXTRACTION_REQUIRED, 20 MAPPING_ONLY, 12 FUTURE_SCOPE, 2 DIRECT_VERIFIED.
- audit status: ok.

| Candidate | Official Case | Case Type | Input Data | Direct Uploadable | Expected Artifact | Current Support | Risk | Use As PASS Evidence? |
|---|---|---|---|---:|---|---|---|---:|
| `structure.rdf` | README gallery `element_pair_rdfs(pmg_struct)` | README function demo / mapping reference | official source demonstrates function and SVG gallery output, not a bounded uploadable fixture in current evidence flow | false | RDF figure/static plot | planned only; no adapter implemented in Phase 10E-6 | depends on official script/gallery data and exact pymatviz behavior | false |
| `structure.rdf` | README gallery `element_pair_rdfs({"A": struct1, "B": struct2})` | README function demo / mapping reference | multi-structure dictionary/gallery example | false | RDF multi-series figure | planned only | multi-structure comparison semantics not in Phase 10E-7 first implementation | false |
| `structure.xrd` | README gallery XRD examples | README function demo / mapping reference | gallery/script patterns, not current direct-upload evidence | false | XRD figure | XRD has platform evidence from Phase 10E-5, but not official-example PASS | official examples require separate direct verification | false |

No notebook-only, script-heavy, external-API, missing-input, or screenshot-only official case is marked PASS by this phase.

## 10. RDF Readiness Gate

| Dimension | Status | Notes |
|---|---|---|
| dependency readiness | READY | Existing environment has `pymatgen`, `numpy`, `scipy`, `plotly`, and `pymatviz`; no new dependency is needed for a first implementation. |
| periodic-image readiness | READY | `pymatgen Structure.get_all_neighbors()` is available; existing parser preserves periodic structures, lattice, PBC, and positive volume. |
| normalization readiness | READY | Number-density shell-volume normalization is fixed in this document. |
| cutoff/bin readiness | READY | Defaults, limits, bin count rule, and rejection policy are fixed. |
| partial RDF readiness | READY | Ordered center-element to neighbor-element pair policy and `max_partial_pairs` cap are fixed. |
| fixture readiness | READY | Existing small periodic fixtures include `simple_cubic.cif`, `POSCAR`, `nacl.poscar`, and generated Structure JSON paths. |
| numeric determinism | READY | Sorting, bin assignment, and rounding rules are fixed. |
| artifact contract | READY | `rdf.json`, `rdf_plot.json`, `summary.md`, and `recipe.json` contracts are fixed. |
| params schema | READY | Strict whitelist schema is fixed. |
| planner routing | READY | Prompt boundaries are defined; implementation tests must enforce them. |
| browser/API evidence feasibility | READY | Phase 10E-2 and 10E-5 evidence flows can be reused after implementation. |
| CI runtime risk | LOW | Defaults keep small fixtures and bounded neighbor totals; large structures reject instead of truncating silently. |
| security risk | LOW | Artifacts are JSON/Markdown only with no JS, no external URLs, no renderer bundle. |
| official examples mapping quality | PARTIAL_READY | README RDF examples are mapping references only, not PASS evidence. |
| implementation complexity | MEDIUM | Periodic neighbor counting and normalization are more complex than XRD but now bounded by explicit policy. |
| regression risk | LOW | Implementation can follow existing `_BaseStructureAdapter`, XRD, and coordination artifact patterns. |

Final decision: READY for a single-scope Phase 10E-7 `structure.rdf` implementation, with browser/API evidence deferred to Phase 10E-8.

## 11. Deferred Scope

- RDF browser/API evidence: deferred to Phase 10E-8.
- trajectory RDF / time-averaged RDF: deferred.
- experimental PDF fitting / neutron scattering refinement / X-ray total scattering analysis: deferred.
- full `structure.viewer_3d`: deferred.
- WebGL renderer: deferred.
- Brillouin-zone 3D: deferred.
- phonon bands / DOS: deferred.
- advanced local environment classification: deferred.
- notebook extraction, script execution, and external API workflows: deferred.

## 12. Conclusion

PASS.

Phase 10E-6 fixed the RDF policy needed for implementation readiness without implementing RDF. Phase 10E-7 may implement `structure.rdf` only, using the static artifact contract and policies defined here. Phase 10E-7 must not implement full 3D viewer, WebGL, phonon, notebook/script workflows, or browser/API evidence.
