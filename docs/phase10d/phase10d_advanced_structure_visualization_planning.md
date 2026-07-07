# Phase 10D Advanced Structure Visualization Planning

## 1. Background

Phase 10A completed the first table and generic visualization adapter batch with browser/API/artifact evidence for direct verified MatPES and Ward workflows. Phase 10B added composition visualization adapters and verified the Ward composition workflows end to end. Phase 10C added lightweight structure adapters and browser/API/artifact evidence for deterministic simple-cubic structure workflows.

The platform can now ingest materials data, generate validated AnalysisPlans, persist those plans, execute jobs through QueueWorkerRuntime, call tools through Tool Registry + Adapter boundaries, and render auditable artifacts in the Phase 9C workspace. This gives enough foundation to plan advanced structure visualization, but not enough reason to implement a full interactive 3D viewer in one step.

Phase 10D is a planning phase only. It defines the product and engineering contract for advanced structure visualization, physics plots, Brillouin-zone scenes, and phonon plots without adding adapters, changing runtime semantics, or claiming new official example verification.

## 2. Current Capability Baseline

### Table / Generic Visualization

- `table.numeric_summary`
- `table.distribution_summary`
- `viz.scatter`
- `viz.histogram`
- `viz.correlation`
- `ml.basic_metrics`

Phase 10A-2 evidence covers the first batch adapter workflows with browser screenshots, redacted API captures, downloaded artifacts, summaries, and manifests.

### Composition

- `composition.summary`
- `composition.formula_statistics`
- `composition.elements_hist`
- `composition.ptable_heatmap`
- `composition.chem_sys_treemap`
- `composition.chem_sys_sunburst`

Phase 10B-2 evidence covers the five composition visualization workflows on the Ward direct verified case. Evidence uses Mock Planner only and does not claim unsupported official examples.

### Lightweight Structure

- `structure.summary`
- `structure.lattice_summary`
- `structure.spacegroup_summary`
- `structure.composition_from_structure`
- `structure.preview_metadata`

Phase 10C-2 evidence covers five simple-cubic structure workflows through the Phase 9C UI, redacted API captures, adapter-generated artifacts, reports, recipes, and manifests. It does not claim support for full 3D viewer, XRD, RDF, coordination histogram, phonon, or Brillouin-zone workflows.

## 3. Why This Phase Does Not Directly Implement a 3D Viewer

Full 3D structure visualization has higher product and verification risk than the previous adapter batches:

- Frontend rendering risk: a real viewer needs a renderer contract, camera model, element styles, large-structure handling, and UI affordances beyond the current artifact summary path.
- WebGL stability: local browser capabilities, GPU state, and headless CI differ across machines.
- Screenshot reproducibility: deterministic browser evidence is harder for animated or interactive scenes than static JSON/Plotly artifacts.
- Security boundary: artifact files must not execute arbitrary JavaScript, load remote URLs, or read arbitrary local files.
- Dependency weight: MatterViz, pymatgen, spglib, phonopy, and Plotly 3D features have different optional dependency and platform assumptions.
- Artifact size: full structure scenes, phonon data, and high-density physics plots can become large enough to affect CI and repository size.
- CI runtime: advanced structure calculations must remain deterministic and bounded.
- Official examples readiness: current direct verified benchmark cases are MatPES and Ward; advanced structure examples are mostly README demos, widgets, notebooks, scripts, external-data, or future-scope cases.

Therefore Phase 10D recommends a metadata-first sequence before any full interactive 3D viewer.

## 4. Advanced Structure Capability Layers

### Layer 1: Viewer Metadata and Static Export Readiness

Candidate tools:

- `structure.viewer_3d_contract`
- `structure.viewer_scene_metadata`
- `structure.viewer_export_package`

Purpose:

Define the scene and export contract before implementing frontend 3D rendering.

Expected outputs:

- `viewer_scene.json`
- `viewer_assets_manifest.json`
- `summary.md`
- `recipe.json`

Planning focus:

- Atom, bond, lattice-vector, and site schema.
- Camera and display settings.
- Element color/radius style policy.
- Bond detection policy and warnings.
- Max site count and truncation policy.
- No JavaScript execution from artifacts.
- Static artifact package with future frontend renderer compatibility.

### Layer 2: Static Physics Plots

Candidate tools:

- `structure.xrd`
- `structure.rdf`
- `structure.coordination_hist`

Purpose:

Add deterministic numeric/static physics plots after the viewer scene contract is stable.

Planning focus:

- Dependency policy for pymatgen/spglib/numpy/scipy.
- Input structure support and resource caps.
- Numeric output JSON.
- Optional Plotly/static chart artifact.
- `summary.md` and `recipe.json`.
- Numeric tolerances.
- Small fixtures for tests.
- Browser/API evidence strategy.

### Layer 3: Interactive 3D Viewer

Candidate tools:

- `structure.viewer_3d`
- `structure.brillouin_zone_3d`

Purpose:

Plan actual interactive rendering only after scene metadata and static export contracts are stable.

Planning focus:

- Renderer choice: Three.js, MatterViz, or a platform-owned viewer.
- Artifact loading model.
- Sandboxing and disabled external resources.
- Screenshot stability.
- CI feasibility.
- WebGL unavailable fallback.
- Large structure handling.
- Mobile/browser limitations.

### Layer 4: Phonon Visualization

Candidate tools:

- `phonon.bands`
- `phonon.dos`
- `phonon.band_dos`

Purpose:

Plan phonon data contracts independently because phonon workflows have specialized input formats and heavy dependencies.

Planning focus:

- Input formats such as phonopy YAML, band path data, DOS tables, and pymatgen-compatible objects.
- Units, frequencies, q-points, path labels, and branch metadata.
- DOS schema and combined band/DOS layout.
- Optional phonopy/pymatgen dependency policy.
- Large artifact risk.
- Official examples are not currently direct-uploadable PASS evidence.

## 5. Candidate Adapter Pool

- `structure.viewer_3d_contract`
- `structure.viewer_scene_metadata`
- `structure.viewer_export_package`
- `structure.xrd`
- `structure.rdf`
- `structure.coordination_hist`
- `structure.viewer_3d`
- `structure.brillouin_zone_3d`
- `phonon.bands`
- `phonon.dos`
- `phonon.band_dos`

## 6. Recommended Next Scope

Phase 10D-1 should implement only the metadata/export layer:

- `structure.viewer_scene_metadata`
- `structure.viewer_export_package`
- optional `structure.viewer_3d_contract`

This establishes the serialized viewer scene format, artifact packaging rules, resource caps, and future UI contract without shipping a full interactive renderer.

Static physics tools should follow after the scene metadata contract:

- `structure.coordination_hist` is the safest first static physics candidate if local neighbor-finding dependencies and definitions are stable.
- `structure.xrd` is a later candidate if pymatgen XRD dependencies and numeric tolerance policy are stable.
- `structure.rdf` should wait until cutoff, binning, and periodic-boundary policy are explicit.

Do not implement full `structure.viewer_3d` in Phase 10D-1.

## 7. Deferred Scope

- Full interactive `structure.viewer_3d`.
- WebGL renderer integration.
- `structure.brillouin_zone_3d`.
- `phonon.bands`, `phonon.dos`, and `phonon.band_dos`.
- Notebook extraction.
- Script execution.
- External API required workflows.

## 8. Candidate Adapter Design Drafts

### `structure.viewer_3d_contract`

- Tool id: `structure.viewer_3d_contract`
- Purpose: Emit the platform contract for future 3D viewer scene artifacts without rendering.
- Input resource: Structure resource or normalized structure collection.
- Params schema: `{ "contractVersion": "1.0", "includeExamples": true }`
- Output artifacts: `viewer_contract.json`, `summary.md`, `recipe.json`
- JSON schema: contract fields for atoms, bonds, lattice, camera, styles, caps, warnings, and renderer expectations.
- Summary: Explain which viewer contract version downstream renderers should support.
- Recipe: Include tool id, version, params, structure resource metadata, and artifact list.
- Dependency policy: No optional rendering dependencies.
- Warning model: Warn when current structures require fields not representable in contract v1.
- Typed errors: `unsupported_structure_resource`, `contract_generation_failed`, `artifact_write_failed`
- Deterministic behavior: Pure schema emission plus deterministic examples.
- Security boundary: No JS, no external URL, no renderer execution.
- Evidence strategy: Adapter tests in Phase 10D-1; browser/API evidence only after Phase 10D-2 if included.

### `structure.viewer_scene_metadata`

- Tool id: `structure.viewer_scene_metadata`
- Purpose: Convert validated structures into a static scene metadata artifact for future rendering.
- Input resource: Single structure or structure collection already uploaded to the platform.
- Params schema: `{ "maxSites": 500, "bondPolicy": "none|covalent_radius|distance_cutoff", "includeBonds": false, "cameraPreset": "auto", "elementStyle": "default" }`
- Output artifacts: `viewer_scene.json`, `summary.md`, `recipe.json`
- JSON schema: atoms, optional bonds, lattice vectors, formula, reduced formula, bounding box, camera, styles, truncation, warnings.
- Summary: Human-readable structure count, site count, elements, truncation status, and future renderer notes.
- Recipe: Include tool id, adapter version, params, resource hash, caps, and artifact list.
- Dependency policy: Reuse existing structure parser; no renderer dependency.
- Warning model: `too_many_sites_warning`, `bond_detection_disabled`, `bond_detection_truncated`, `missing_lattice_warning`
- Typed errors: `structure_parse_failed`, `empty_structure`, `unsupported_structure_format`, `artifact_write_failed`
- Deterministic behavior: Stable ordering by structure id and site order; rounded numeric output.
- Security boundary: No JS, no external URL, no arbitrary file read.
- Evidence strategy: Phase 10D-1 adapter evidence, Phase 10D-2 browser/API evidence.

### `structure.viewer_export_package`

- Tool id: `structure.viewer_export_package`
- Purpose: Package static scene metadata and small style assets for future viewer consumption.
- Input resource: Structure resource or `viewer_scene.json`.
- Params schema: `{ "includeStyles": true, "includeManifest": true, "maxPackageBytes": 5000000 }`
- Output artifacts: `viewer_scene.json`, `viewer_assets_manifest.json`, `summary.md`, `recipe.json`
- JSON schema: manifest with artifact names, hashes, sizes, scene contract version, and renderer compatibility notes.
- Summary: Explain package contents and non-executable nature.
- Recipe: Include tool id, input resource, generated manifest hash, and caps.
- Dependency policy: No rendering dependency and no archive execution.
- Warning model: `package_size_warning`, `style_asset_fallback`, `scene_truncated`
- Typed errors: `missing_scene_metadata`, `package_size_limit_exceeded`, `artifact_write_failed`
- Deterministic behavior: Stable file names, hashes, and manifest ordering.
- Security boundary: Static files only; no JavaScript execution or remote assets.
- Evidence strategy: Adapter evidence first; browser/API evidence after package endpoint behavior is verified.

### `structure.xrd`

- Tool id: `structure.xrd`
- Purpose: Generate deterministic powder XRD pattern data from periodic structures.
- Input resource: Periodic structure or structure collection.
- Params schema: `{ "wavelength": "CuKa", "twoThetaRange": [0, 90], "peakMergeTolerance": 0.01, "maxStructures": 20 }`
- Output artifacts: `xrd_pattern.json`, optional `xrd_plot.json`, `summary.md`, `recipe.json`
- JSON schema: two-theta values, intensities, hkls if available, wavelength, range, tolerance, warnings.
- Summary: Peak count, strongest peaks, wavelength, and limitations.
- Recipe: Structure hash, params, dependency version, numeric tolerances.
- Dependency policy: Requires stable pymatgen XRD path; otherwise typed error.
- Warning model: `dependency_missing`, `non_periodic_structure`, `peak_merge_warning`
- Typed errors: `xrd_dependency_missing`, `xrd_generation_failed`, `non_periodic_structure`, `artifact_write_failed`
- Deterministic behavior: Fixed range, rounding, sorted peaks.
- Security boundary: No network, no external files, no arbitrary code.
- Evidence strategy: Static fixture tests before browser/API evidence.

### `structure.rdf`

- Tool id: `structure.rdf`
- Purpose: Compute radial distribution function data for structure collections or periodic structures.
- Input resource: Structure resource or collection.
- Params schema: `{ "cutoff": 10.0, "binWidth": 0.1, "speciesPairs": [], "maxStructures": 20 }`
- Output artifacts: `rdf.json`, optional `rdf_plot.json`, `summary.md`, `recipe.json`
- JSON schema: bins, g(r), counts, species-pair metadata, cutoff, bin width, normalization policy, warnings.
- Summary: RDF configuration, peak hints, and normalization limits.
- Recipe: Structure hash, params, cutoff policy, rounding policy.
- Dependency policy: Use existing structure/numpy capabilities; no heavy dependency unless justified.
- Warning model: `cutoff_too_large_warning`, `small_cell_warning`, `partial_pair_coverage`
- Typed errors: `rdf_generation_failed`, `non_periodic_structure`, `empty_structure`, `artifact_write_failed`
- Deterministic behavior: Fixed bins and stable numeric rounding.
- Security boundary: No network, no script execution.
- Evidence strategy: Unit tolerance tests first; browser/API evidence later.

### `structure.coordination_hist`

- Tool id: `structure.coordination_hist`
- Purpose: Compute coordination-number distributions from periodic structures.
- Input resource: Structure resource or collection.
- Params schema: `{ "strategy": "distance_cutoff|voronoi|minimum_distance", "cutoff": 3.0, "groupByElement": true, "maxStructures": 50 }`
- Output artifacts: `coordination_hist.json`, optional `coordination_hist_plot.json`, `summary.md`, `recipe.json`
- JSON schema: coordination bins, counts, by-element counts, strategy, cutoff, failed sites, warnings.
- Summary: Strategy, main coordination numbers, and ambiguity warnings.
- Recipe: Structure hash, neighbor policy, params, dependency version if used.
- Dependency policy: Prefer lightweight deterministic strategy first; optional advanced strategies must be gated.
- Warning model: `ambiguous_neighbors`, `cutoff_sensitive`, `large_structure_truncated`
- Typed errors: `coordination_generation_failed`, `missing_lattice`, `empty_structure`, `artifact_write_failed`
- Deterministic behavior: Stable site ordering and fixed cutoff.
- Security boundary: No external reads or code execution.
- Evidence strategy: Candidate for Phase 10E after viewer scene metadata.

### `structure.viewer_3d`

- Tool id: `structure.viewer_3d`
- Purpose: Future interactive structure viewer artifact, not a Phase 10D-1 implementation target.
- Input resource: `viewer_scene.json` or structure resource.
- Params schema: `{ "renderer": "platform|matterviz|threejs", "showBonds": "auto", "showCell": true, "cameraPreset": "auto" }`
- Output artifacts: `viewer.html`, `viewer_scene.json`, `summary.md`, `recipe.json`
- JSON schema: Must reuse `viewer_scene.json` contract and include renderer metadata.
- Summary: Viewer mode, renderer, fallback path, and limitations.
- Recipe: Renderer version, scene hash, params, caps.
- Dependency policy: Requires explicit frontend renderer decision; not enabled by metadata adapters.
- Warning model: `webgl_unavailable`, `renderer_fallback`, `large_structure_lod`
- Typed errors: `renderer_unavailable`, `scene_contract_unsupported`, `viewer_generation_failed`
- Deterministic behavior: Static scene deterministic; user interactions are not part of tests.
- Security boundary: No artifact-supplied JS execution, no external URLs, sandboxed viewer only.
- Evidence strategy: Dedicated Phase 10F prototype/evidence after static contracts.

### `structure.brillouin_zone_3d`

- Tool id: `structure.brillouin_zone_3d`
- Purpose: Future 3D Brillouin-zone scene metadata or interactive view.
- Input resource: Periodic structure with reciprocal lattice.
- Params schema: `{ "includeHighSymmetryPath": true, "renderer": "metadata", "maxPathLabels": 100 }`
- Output artifacts: `brillouin_zone_scene.json`, optional future `brillouin_zone_viewer.html`, `summary.md`, `recipe.json`
- JSON schema: reciprocal lattice vectors, polyhedron vertices/faces, labels, path segments, warnings.
- Summary: Reciprocal cell, available labels, and renderer status.
- Recipe: Structure hash, reciprocal lattice policy, params.
- Dependency policy: Likely pymatgen/spglib dependency; not Phase 10D-1.
- Warning model: `symmetry_dependency_missing`, `path_label_truncated`, `reciprocal_lattice_failed`
- Typed errors: `brillouin_zone_generation_failed`, `non_periodic_structure`, `dependency_missing`
- Deterministic behavior: Stable vertex ordering and rounded values.
- Security boundary: Static JSON first; future 3D renderer sandboxed.
- Evidence strategy: Future scope after viewer scene contract.

### `phonon.bands`

- Tool id: `phonon.bands`
- Purpose: Plot phonon band structures from explicit phonon band data.
- Input resource: Phonon band data, phonopy YAML, or normalized phonon object.
- Params schema: `{ "frequencyUnit": "THz", "pathLabels": [], "maxBranches": 200 }`
- Output artifacts: `phonon_bands.json`, optional `phonon_bands_plot.json`, `summary.md`, `recipe.json`
- JSON schema: q-points, distances, labels, branches, frequencies, units, imaginary-mode flags, warnings.
- Summary: Path, branch count, unit, imaginary modes.
- Recipe: Input hash, unit conversion policy, params.
- Dependency policy: Phonopy/pymatgen optional; no external API.
- Warning model: `missing_labels`, `imaginary_modes_detected`, `large_band_data_truncated`
- Typed errors: `phonon_input_parse_failed`, `phonon_dependency_missing`, `artifact_write_failed`
- Deterministic behavior: Stable q-point ordering and numeric rounding.
- Security boundary: No script/notebook execution.
- Evidence strategy: Separate Phase 10G planning and fixtures.

### `phonon.dos`

- Tool id: `phonon.dos`
- Purpose: Plot phonon density of states from explicit DOS data.
- Input resource: Phonon DOS table or normalized phonon DOS object.
- Params schema: `{ "frequencyUnit": "THz", "normalize": false, "partialDos": false }`
- Output artifacts: `phonon_dos.json`, optional `phonon_dos_plot.json`, `summary.md`, `recipe.json`
- JSON schema: frequency grid, total DOS, optional projected DOS, units, normalization, warnings.
- Summary: Frequency range, DOS grid size, partial DOS coverage.
- Recipe: Input hash, unit policy, params.
- Dependency policy: Prefer direct data parsing before phonopy dependency.
- Warning model: `non_monotonic_frequency_grid`, `partial_dos_missing`, `large_grid_truncated`
- Typed errors: `phonon_dos_parse_failed`, `invalid_frequency_grid`, `artifact_write_failed`
- Deterministic behavior: Stable grid and numeric rounding.
- Security boundary: No external data fetch.
- Evidence strategy: Separate Phase 10G planning.

### `phonon.band_dos`

- Tool id: `phonon.band_dos`
- Purpose: Combine phonon bands and DOS into a coordinated artifact.
- Input resource: Band data plus DOS data or normalized combined phonon object.
- Params schema: `{ "frequencyUnit": "THz", "alignZero": true, "layout": "side_by_side" }`
- Output artifacts: `phonon_band_dos.json`, optional `phonon_band_dos_plot.json`, `summary.md`, `recipe.json`
- JSON schema: band section, DOS section, shared frequency unit, layout, warnings.
- Summary: Combined input coverage and limitations.
- Recipe: Input hashes, unit policy, params.
- Dependency policy: Requires validated `phonon.bands` and `phonon.dos` contracts first.
- Warning model: `unit_mismatch`, `missing_band_or_dos`, `frequency_range_mismatch`
- Typed errors: `phonon_combined_parse_failed`, `incompatible_inputs`, `artifact_write_failed`
- Deterministic behavior: Stable layout and numeric rounding.
- Security boundary: No notebook/script execution.
- Evidence strategy: After standalone phonon tools.

## 9. Official Examples Mapping

| Candidate Adapter | Official Case | Case Type | Input Data | Expected Artifact | Current Support | Risk |
|---|---|---|---|---|---|---|
| `structure.viewer_scene_metadata` | `readme_structure_3d` | readme_function_demo | README structure object example | `viewer_scene.json` | Mapping only | Needs uploadable structure fixture, not README-only PASS |
| `structure.viewer_export_package` | `readme_widgets_structure_widget` | future_scope_widget_or_structure | MatterViz widget demo | `viewer_assets_manifest.json` | Mapping only | Widget semantics are not static package evidence |
| `structure.viewer_3d_contract` | `widgets_jupyter_demo` | future_scope_widget_or_structure | Notebook/widget | `viewer_contract.json` | Mapping only | Notebook/widget not direct-uploadable |
| `structure.xrd` | No direct verified case | future candidate | Requires periodic structure fixture | `xrd_pattern.json` | Not supported | Dependency/tolerance not yet fixed |
| `structure.rdf` | No direct verified case | future candidate | Requires structure collection or periodic fixture | `rdf.json` | Not supported | Cutoff/binning policy unresolved |
| `structure.coordination_hist` | No direct verified case | future candidate | Requires periodic structure fixture | `coordination_hist.json` | Not supported | Neighbor definition ambiguity |
| `structure.viewer_3d` | `readme_structure_3d` | readme_function_demo | README demo | `viewer.html` | Not supported | WebGL/security/screenshot stability |
| `structure.brillouin_zone_3d` | `readme_brillouin_zone_3d` | readme_function_demo / future_scope | README demo | `brillouin_zone_scene.json` | Not supported | Symmetry and 3D viewer dependency |
| `phonon.bands` | `readme_phonon_bands`, `phonons_mlip_phonons`, `matbench_phonons` | readme_function_demo / script_generated_data / external_api_required | Phonon band data not direct-uploadable | `phonon_bands.json` | Not supported | Phonopy/data extraction required |
| `phonon.dos` | `readme_phonon_dos`, `phonons_mlip_phonons` | readme_function_demo / script_generated_data | Phonon DOS data not direct-uploadable | `phonon_dos.json` | Not supported | Data contract and dependency unresolved |
| `phonon.band_dos` | `readme_phonon_bands_and_dos` | readme_function_demo | Combined demo | `phonon_band_dos.json` | Not supported | Requires standalone band/DOS contracts first |

No row in this table is a PASS evidence claim.

## 10. Tool Registry Plan

- Domains:
  - `structure` for viewer scene metadata, export packages, XRD, RDF, coordination, and Brillouin-zone scene tools.
  - `phonon` for phonon band/DOS tools.
- Tool ids must use stable dotted names and avoid claiming unsupported renderer behavior.
- Params schemas must be whitelist-only with `additionalProperties=false`.
- Input schemas must distinguish periodic structure, structure collection, viewer scene metadata, and phonon data.
- Resource limits must cover maximum sites, maximum structures, maximum bonds, maximum artifact size, and maximum numeric arrays.
- Output artifact schemas must name deterministic JSON artifacts and required `summary.md` / `recipe.json`.
- All execution must continue through Tool Registry validation and Adapter execution.

## 11. Planner Routing Plan

| Prompt intent | Phase 10D routing plan |
|---|---|
| "generate structure viewer scene metadata" | `structure.viewer_scene_metadata` |
| "package viewer scene for export" | `structure.viewer_export_package` |
| "show/render/display 3D structure" | Future-scope explanation; do not route to full `structure.viewer_3d` until implemented |
| "compute XRD / diffraction pattern" | Future-scope or `structure.xrd` after static physics phase |
| "compute RDF / pair distribution" | Future-scope or `structure.rdf` after static physics phase |
| "coordination histogram / coordination distribution" | Future-scope or `structure.coordination_hist` after static physics phase |
| "Brillouin zone 3D" | Future-scope explanation; no fake 3D support |
| "phonon bands" | Future-scope `phonon.bands` after phonon data contract |
| "phonon DOS" | Future-scope `phonon.dos` after phonon data contract |
| "phonon bands and DOS" | Future-scope `phonon.band_dos` after standalone phonon tools |

Routing priority should keep implemented lightweight structure tools ahead of generic composition/table/viz routing, but explicit 3D/XRD/RDF/phonon prompts must not be silently converted into unrelated supported tools.

## 12. Artifact Contract Plan

### `viewer_scene.json`

Fields:

- `artifactType: "structure.viewer_scene_metadata"`
- `sceneContractVersion`
- `structureCount`
- `structures`
- `atoms`
- `bonds`
- `latticeVectors`
- `boundingBox`
- `camera`
- `elementStyles`
- `resourceCaps`
- `truncated`
- `warnings`

### `viewer_assets_manifest.json`

Fields:

- `artifactType: "structure.viewer_export_package"`
- `sceneContractVersion`
- `assets`
- `hashes`
- `sizes`
- `rendererCompatibility`
- `executableContent: false`
- `externalResources: []`
- `warnings`

### `xrd_pattern.json`

Fields:

- `artifactType: "structure.xrd"`
- `wavelength`
- `twoThetaRange`
- `peaks`
- `hklAssignments`
- `intensityScale`
- `warnings`

### `rdf.json`

Fields:

- `artifactType: "structure.rdf"`
- `cutoff`
- `binWidth`
- `bins`
- `gOfR`
- `speciesPairs`
- `normalization`
- `warnings`

### `coordination_hist.json`

Fields:

- `artifactType: "structure.coordination_hist"`
- `strategy`
- `cutoff`
- `bins`
- `counts`
- `byElement`
- `failedSites`
- `warnings`

### `brillouin_zone_scene.json`

Fields:

- `artifactType: "structure.brillouin_zone_3d"`
- `reciprocalLattice`
- `vertices`
- `faces`
- `highSymmetryPoints`
- `pathSegments`
- `warnings`

### `phonon_bands.json`

Fields:

- `artifactType: "phonon.bands"`
- `frequencyUnit`
- `qpoints`
- `distances`
- `labels`
- `branches`
- `imaginaryModes`
- `warnings`

### `phonon_dos.json`

Fields:

- `artifactType: "phonon.dos"`
- `frequencyUnit`
- `frequencies`
- `totalDos`
- `projectedDos`
- `normalization`
- `warnings`

## 13. Frontend Rendering Strategy

- Phase 10D-1 should show JSON/summary/recipe artifacts only, using the existing Results/Export tab artifact display.
- Viewer scene metadata should be human-readable in normal mode and expose full JSON only in Developer mode.
- Future renderer work should decide between Three.js, MatterViz, Plotly 3D, or a platform-owned renderer after the static scene contract is stable.
- WebGL unavailable fallback must be a noninteractive metadata view, not a blank canvas.
- Screenshots should use deterministic camera presets, fixed viewport sizes, and disabled animation.
- User mode should show scene summary, structure counts, elements, and truncation warnings.
- Developer mode may show scene contract, caps, provenance, and artifact hashes.

## 14. Security Boundary

- Do not execute JavaScript embedded in artifacts.
- Do not load external URLs from artifacts.
- Do not read arbitrary local paths.
- Do not execute notebooks or scripts.
- Keep artifact package files static and deterministic.
- Enforce max site, max bond, max structure, and max package size limits.
- Redact secrets from API responses, JobEvents, artifacts, reports, and recipes.
- Keep future interactive viewers sandboxed and controlled by platform code, not artifact-provided code.

## 15. Test Plan

- Structure fixture tests for small CIF/POSCAR/normalized structure objects.
- Numeric deterministic tests for scene bounds, lattice vectors, bond policy, XRD peaks, RDF bins, and coordination counts.
- Registry tests for tool registration, params schema, domains, resource limits, and output artifact schemas.
- Planner routing tests for metadata, export package, 3D future-scope, XRD, RDF, coordination, Brillouin zone, and phonon intents.
- API execution tests for plan validation, persisted AnalysisPlan, job completion, ToolCall status, and artifact retrieval.
- Frontend artifact rendering tests for JSON summary, report, recipe, Developer mode raw JSON, and unsupported/future-scope messaging.
- Browser evidence tests only in evidence phases.
- Regression tests for Phase 8B, Phase 9D, Phase 10A, Phase 10B, and Phase 10C boundaries.

## 16. Risk Assessment

- WebGL instability across machines and CI.
- Screenshot nondeterminism from camera, animation, GPU, and font differences.
- pymatgen/spglib/phonopy dependency availability and version drift.
- Large structure size causing slow rendering, huge artifacts, or browser instability.
- Bond detection ambiguity and element radius policy differences.
- XRD tolerance sensitivity and peak merging.
- RDF cutoff/bin-width sensitivity and periodic-boundary assumptions.
- Coordination definition ambiguity across neighbor strategies.
- Phonon input complexity and inconsistent units.
- CI runtime from structure/physics calculations.
- Security risk from HTML/JS artifacts if interactive viewer scope is not separated from static metadata artifacts.

## 17. Recommended Phase Split

### Phase 10D-1 Viewer Scene Metadata / Export Package Implementation

Implement `structure.viewer_scene_metadata` and `structure.viewer_export_package`, optionally with a static `structure.viewer_3d_contract` artifact. Do not implement full 3D rendering.

### Phase 10D-2 Browser/API Evidence for Viewer Scene Metadata

Capture redacted API, browser, and artifact evidence for the metadata/export package path.

### Phase 10E Static Structure Physics Plot Planning / Implementation

Plan or implement `structure.coordination_hist`, `structure.xrd`, and `structure.rdf` after dependency and tolerance policy is settled.

### Phase 10F Interactive 3D Viewer Planning / Prototype

Only consider true `structure.viewer_3d` after scene metadata, static export package, and evidence paths are stable.

### Phase 10G Phonon Visualization Planning

Plan phonon bands, DOS, and combined band/DOS workflows separately.

## 18. Acceptance Criteria

- Phase 10D adds planning documentation only.
- No adapter, runtime, Tool Registry, PlanValidator, QueueWorkerRuntime, AnalysisPlanRepository, or `/planner/jobs` implementation changes.
- Advanced structure capability layers are explicit.
- Phase 10D-1 scope is metadata/export package, not full 3D viewer.
- Candidate adapter matrix and implementation prompt are present.
- Official examples are mapped honestly without PASS claims.
- Security, frontend, artifact, test, and dependency strategies are documented.
- Persistent project state records the decision and remaining work.

## 19. Final Recommendation

Proceed next to Phase 10D-1: Viewer Scene Metadata / Export Package Implementation.

Do not proceed directly to full `structure.viewer_3d`, Brillouin-zone 3D, XRD/RDF implementation, or phonon visualization. The safest next step is to define and implement static viewer scene metadata and export-package artifacts that future renderers can consume without expanding runtime authority or introducing WebGL/JavaScript evidence risk.
