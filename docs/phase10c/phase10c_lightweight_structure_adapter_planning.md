# Phase 10C Lightweight Structure Adapter Planning

## 1. Background

Phase 10A and Phase 10B moved the platform from generic planner execution toward
official pymatviz-oriented evidence:

- Phase 10A implemented and browser-verified table, chart, and basic composition
  adapters for MatPES and Ward.
- Phase 10B implemented and browser/API-verified composition visualization
  adapters for Ward.
- The current execution boundary remains unchanged: natural-language requests
  become validated JSON AnalysisPlans, persisted jobs execute through
  QueueWorkerRuntime, and every executable step goes through Tool Registry +
  Adapter.

The next useful materials-informatics surface is structure data. Phase 10C should
not start with WebGL viewers or physics plots. The safer step is a lightweight
structure adapter batch that turns CIF/POSCAR/pymatgen-style structure inputs
into deterministic JSON summaries, report text, and recipes.

## 2. Current Capability Baseline

Evidence-backed table / visualization adapters:

- `table.distribution_summary`
- `viz.scatter`
- `viz.histogram`
- `viz.correlation`
- `composition.summary`

Evidence-backed composition visualization adapters:

- `composition.formula_statistics`
- `composition.elements_hist`
- `composition.ptable_heatmap`
- `composition.chem_sys_treemap`
- `composition.chem_sys_sunburst`

Registered but not Phase 10C target tools include structure and physics-heavy
capabilities such as `structure.structure_3d`, `structure.viewer_3d`,
`structure.coordination_hist`, `structure.xrd`, `structure.rdf`, and phonon
tools. Registration is not the same as Phase 10C browser/API evidence.

## 3. Why Not Directly Build 3D / XRD / RDF / Phonon

Advanced structure and physics adapters are important but should not be the next
implementation slice:

- 3D viewers require stable browser rendering, iframe or HTML artifact sandboxing,
  and screenshot reliability.
- XRD and RDF require physics parameters, numeric tolerances, periodic boundary
  assumptions, and deterministic fixtures.
- Space-group and symmetry workflows can depend on optional `pymatgen`/`spglib`
  behavior and tolerance choices.
- Phonon bands/DOS require a separate phonon data model and official examples
  are not direct-upload verified.
- Brillouin-zone rendering is reciprocal-space and 3D-heavy.
- Notebook/script examples need extraction before they can become benchmark
  cases.

Lightweight structure summaries reduce risk by first proving parse, metadata,
composition extraction, lattice, and preview payload contracts.

## 4. Lightweight Structure Adapter Scope

Recommended Phase 10C-1 scope:

- `structure.summary`
- `structure.lattice_summary`
- `structure.spacegroup_summary`
- `structure.composition_from_structure`
- `structure.preview_metadata`

Out of Phase 10C-1 scope:

- `structure.viewer_3d`
- `structure.xrd`
- `structure.rdf`
- `structure.coordination_hist`
- `structure.brillouin_zone_3d`
- `phonon.bands`
- `phonon.dos`
- `phonon.band_dos`

## 5. Adapter Design Drafts

### 5.1 `structure.summary`

- Purpose: summarize one structure or a structure collection.
- Input resources: CIF, POSCAR/CONTCAR, pymatgen Structure JSON, ASE
  Atoms-compatible JSON, or normalized structure objects.
- Params schema:
  - `structureId?: string`
  - `maxStructures?: integer`
  - `includeSiteProperties?: boolean`
  - `includeLattice?: boolean`
- Output artifacts:
  - `structure_summary.json`
  - `summary.md`
  - `recipe.json`
- JSON artifact schema:

```json
{
  "artifactType": "structure.summary",
  "structureCount": 1,
  "structures": [
    {
      "structureId": "",
      "formula": "",
      "reducedFormula": "",
      "elements": [],
      "elementCounts": {},
      "numSites": 0,
      "numElements": 0,
      "isPeriodic": true,
      "lattice": {
        "a": 0,
        "b": 0,
        "c": 0,
        "alpha": 0,
        "beta": 0,
        "gamma": 0,
        "volume": 0
      },
      "siteProperties": [],
      "warnings": []
    }
  ],
  "warnings": []
}
```

- Summary: formula, element count, site count, lattice availability, warnings.
- Recipe: source file/object, parser version, params, artifact list.
- Typed errors: `unsupported_structure_format`, `structure_parse_failed`,
  `empty_structure`, `missing_lattice`, `artifact_write_failed`.
- Deterministic behavior: preserve input order, stable structure IDs, stable
  element ordering.
- Security boundary: no network, no shell, no arbitrary path reads.

### 5.2 `structure.lattice_summary`

- Purpose: summarize lattice lengths, angles, volume, and outlier candidates.
- Input resources: single periodic structure or structure collection.
- Params schema:
  - `structureIds?: string[]`
  - `maxStructures?: integer`
  - `outlierZScore?: number`
  - `includeOutliers?: boolean`
- Output artifacts:
  - `lattice_summary.json`
  - `summary.md`
  - `recipe.json`
- JSON artifact schema:

```json
{
  "artifactType": "structure.lattice_summary",
  "structureCount": 0,
  "latticeStats": {
    "a": {"min": 0, "mean": 0, "max": 0},
    "b": {"min": 0, "mean": 0, "max": 0},
    "c": {"min": 0, "mean": 0, "max": 0},
    "alpha": {"min": 0, "mean": 0, "max": 0},
    "beta": {"min": 0, "mean": 0, "max": 0},
    "gamma": {"min": 0, "mean": 0, "max": 0},
    "volume": {"min": 0, "mean": 0, "max": 0}
  },
  "outliers": [],
  "warnings": []
}
```

- Summary: range and mean of lattice parameters, missing/non-periodic count.
- Typed errors: `missing_lattice`, `non_periodic_structure`,
  `structure_parse_failed`, `empty_structure_collection`,
  `artifact_write_failed`.
- Deterministic behavior: fixed statistic names, no random sampling.
- Security boundary: local structure metadata only.

### 5.3 `structure.spacegroup_summary`

- Purpose: summarize space group and crystal system distributions.
- Input resources: periodic structure or structure collection.
- Params schema:
  - `symprec?: number`
  - `angleTolerance?: number`
  - `maxStructures?: integer`
  - `failOnMissingDependency?: boolean`
- Output artifacts:
  - `spacegroup_summary.json`
  - `spacegroup_bar.json`
  - `summary.md`
  - `recipe.json`
- JSON artifact schema:

```json
{
  "artifactType": "structure.spacegroup_summary",
  "structureCount": 0,
  "symmetryEngine": "pymatgen/spglib",
  "symprec": 0.01,
  "spacegroups": [
    {
      "number": 225,
      "symbol": "Fm-3m",
      "crystalSystem": "cubic",
      "count": 0
    }
  ],
  "crystalSystemCounts": {},
  "failedStructures": [],
  "warnings": []
}
```

- Summary: top space groups, crystal system counts, failed structure count.
- Typed errors: `symmetry_dependency_missing`, `symmetry_detection_failed`,
  `non_periodic_structure`, `structure_parse_failed`,
  `artifact_write_failed`.
- Deterministic behavior: fixed `symprec`, deterministic ordering by count then
  space-group number.
- Security boundary: optional dependency check only; no external services.

### 5.4 `structure.composition_from_structure`

- Purpose: extract formulas/compositions from structure objects and bridge into
  existing composition adapters.
- Input resources: single structure or structure collection.
- Params schema:
  - `structureIds?: string[]`
  - `maxStructures?: integer`
  - `includeRecommendedNextTools?: boolean`
- Output artifacts:
  - `structure_composition.json`
  - `summary.md`
  - `recipe.json`
- JSON artifact schema:

```json
{
  "artifactType": "structure.composition_from_structure",
  "structureCount": 0,
  "formulaCount": 0,
  "formulas": [],
  "elementCounts": {},
  "chemicalSystems": {},
  "compositionAdapterCompatible": true,
  "recommendedNextTools": [
    "composition.elements_hist",
    "composition.ptable_heatmap",
    "composition.chem_sys_treemap"
  ],
  "warnings": []
}
```

- Summary: extracted formula count, element coverage, chemical systems.
- Typed errors: `structure_parse_failed`, `empty_structure`, `missing_species`,
  `composition_extraction_failed`, `artifact_write_failed`.
- Deterministic behavior: stable formula extraction and chemical-system labels.
- Security boundary: does not automatically invoke downstream composition tools.

### 5.5 `structure.preview_metadata`

- Purpose: create lightweight frontend preview metadata without implementing a
  real 3D viewer.
- Input resources: one structure or selected representative structure.
- Params schema:
  - `structureId?: string`
  - `maxPreviewSites?: integer`
  - `includeCartesian?: boolean`
  - `includeFractional?: boolean`
- Output artifacts:
  - `structure_preview_metadata.json`
  - `summary.md`
  - `recipe.json`
- JSON artifact schema:

```json
{
  "artifactType": "structure.preview_metadata",
  "structureId": "",
  "formula": "",
  "numSites": 0,
  "elements": [],
  "boundingBox": {
    "x": [0, 0],
    "y": [0, 0],
    "z": [0, 0]
  },
  "latticeVectors": [],
  "sitesPreview": [
    {
      "element": "Fe",
      "fracCoords": [0, 0, 0],
      "cartCoords": [0, 0, 0]
    }
  ],
  "truncated": false,
  "maxPreviewSites": 100,
  "warnings": []
}
```

- Summary: formula, site count, preview truncation, coordinate availability.
- Typed errors: `structure_parse_failed`, `missing_sites`,
  `coordinate_conversion_failed`, `too_many_sites_warning`,
  `artifact_write_failed`.
- Deterministic behavior: preserve site order and truncate by stable prefix.
- Security boundary: metadata only; no WebGL, no iframe, no arbitrary HTML.

## 6. Official Examples Mapping

| Candidate Adapter | Official Case | Case Type | Input Data | Expected Artifact | Current Support | Risk |
|---|---|---|---|---|---|---|
| `structure.summary` | `readme_structure_2d` | `readme_function_demo` / `MAPPING_ONLY` | README structure demo, no direct raw benchmark input | `structure_summary.json` | Mapping reference only | Medium: needs direct CIF/POSCAR fixture for evidence |
| `structure.summary` | `readme_structure_3d` | `readme_function_demo` / `MAPPING_ONLY` | README structure demo, no direct raw benchmark input | `structure_summary.json` | Mapping reference only | Medium |
| `structure.preview_metadata` | `readme_structure_3d` | `readme_function_demo` / `MAPPING_ONLY` | Structure demo data after extraction | `structure_preview_metadata.json` | Future adapter can avoid full 3D viewer | Medium |
| `structure.composition_from_structure` | `readme_structure_2d` | `readme_function_demo` / `MAPPING_ONLY` | Structure demo data after extraction | `structure_composition.json` | Bridges to existing composition adapters | Medium |
| `structure.lattice_summary` | `matbench_expt_gap`, `matbench_mp_gap` | `future_scope_widget_or_structure` / `FUTURE_SCOPE` | Dataset extraction required | `lattice_summary.json` | Not direct evidence | High |
| `structure.spacegroup_summary` | `matbench_expt_gap`, `matbench_mp_gap` | `future_scope_widget_or_structure` / `FUTURE_SCOPE` | Dataset extraction required | `spacegroup_summary.json` | Dependency/tolerance must be pinned | High |
| `structure.viewer_3d` | `readme_widgets_structure_widget` | `readme_function_demo` / `FUTURE_SCOPE` | Widget demo | `matterviz_html` | Explicitly deferred | High |
| `phonon.bands` / `phonon.dos` | `readme_phonon_*`, `phonons_mlip_phonons` | `FUTURE_SCOPE` | Phonon data model required | phonon artifacts | Not Phase 10C | High |
| `structure.brillouin_zone_3d` | `readme_brillouin_zone_3d` | `readme_function_demo` / `FUTURE_SCOPE` | Reciprocal lattice / 3D renderer | Brillouin-zone artifact | Not Phase 10C | Very high |

The current benchmark pack remains partial: MatPES and Ward are direct verified,
while structure examples are mapping or future scope. Phase 10C-1 must not claim
official structure examples as direct PASS until real raw inputs and evidence are
generated.

## 7. Tool Registry Plan

Structure tools should use domain `structure` and explicit `paramsSchema` with
`additionalProperties: false`.

Recommended tool IDs:

- `structure.summary`
- `structure.lattice_summary`
- `structure.spacegroup_summary`
- `structure.composition_from_structure`
- `structure.preview_metadata`

Registry requirements:

- input schema accepts `Structure` objects and structure collections.
- resource limits include `maxStructures` and `maxAtomsPerStructure`.
- output schema declares JSON primary artifact plus `summary_md` and
  `recipe_json`.
- optional dependency requirements are documented in source/provenance metadata.
- non-periodic and periodic requirements are explicit per tool.

## 8. Planner Routing Plan

Mock Planner routing should prefer lightweight structure tools before advanced
viewer or physics tools:

| Prompt intent | Example prompt | Tool |
|---|---|---|
| Structure summary | "请分析这个 CIF 结构的基本信息。" | `structure.summary` |
| Lattice parameters | "请分析晶格参数和晶胞体积。" | `structure.lattice_summary` |
| Space group / crystal system | "请统计空间群或晶系分布。" | `structure.spacegroup_summary` |
| Composition from structure | "请从结构文件中提取元素组成。" | `structure.composition_from_structure` |
| Preview metadata | "请生成结构预览 metadata。" | `structure.preview_metadata` |

Routing constraints:

- If the profile has no structure objects, return a clear unsupported/validation
  message.
- Do not route lightweight summary prompts to `structure.viewer_3d`.
- Do not route XRD/RDF/phonon prompts to lightweight summary tools unless the
  response explicitly says those capabilities are future scope.
- Keep plans single-step until multi-step DAG/data dependency execution exists.

## 9. Artifact / Evidence Plan

Phase 10C-1 should produce adapter-level evidence only:

- unit fixture input
- Tool Registry validation
- adapter execution result
- generated JSON artifact
- `summary.md`
- `recipe.json`
- artifact manifest

Phase 10C-2 should produce browser/API evidence:

- upload/profile response
- planner preview response
- validation response
- job response
- events response
- tool calls response
- artifacts response
- result response
- Phase 9C screenshots for dataset/profile, Plan Preview, Agent process,
  Results/export, and redacted Developer audit.

## 10. Test Plan

Parser tests:

- CIF parse fixture.
- POSCAR parse fixture.
- pymatgen Structure JSON fixture.
- malformed structure fixture.
- non-periodic XYZ boundary.

Adapter unit tests:

- each lightweight structure adapter succeeds on a minimal valid structure.
- missing lattice, missing sites, non-periodic, and malformed inputs return typed
  errors or warnings.
- JSON artifacts include `artifactType`.
- `summary.md` and `recipe.json` are generated.
- outputs are deterministic across repeated runs.

Registry tests:

- all five tools are registered.
- params validation rejects unknown keys.
- domains, resource limits, artifact types, and timeouts are correct.

Planner routing tests:

- summary prompt -> `structure.summary`.
- lattice prompt -> `structure.lattice_summary`.
- space-group prompt -> `structure.spacegroup_summary`.
- composition-from-structure prompt -> `structure.composition_from_structure`.
- preview prompt -> `structure.preview_metadata`.
- viewer/XRD/RDF/phonon prompts do not silently route to completed lightweight
  tools.

API execution tests:

- valid one-step plans validate.
- persisted plan path creates exactly one ToolCall for one-step plans.
- job completes and emits `plan.loaded`, `data.loaded`, `tool.completed`, and
  `job.completed`.
- invalid plans do not save plan, create job, or enqueue.

Frontend artifact rendering tests:

- Results/export tab shows structure JSON artifacts.
- summaries and recipes remain visible.
- Developer mode contains raw JSON/provenance only when enabled.

Regression tests:

- Phase 7 planner.
- Phase 8B persisted plan queue.
- Phase 8C planner read API.
- Phase 9B workspace API.
- Phase 9D gated live path remains gated and not default.
- Phase 10A/10B adapter evidence does not regress.

## 11. Risk Assessment

- CIF parse instability: CIF dialects can vary, and minimal fixtures must be
  pinned.
- POSCAR ambiguity: species lines and selective dynamics can be ambiguous.
- `pymatgen`/`spglib`: optional dependency availability and version behavior must
  be checked before implementation.
- Symmetry tolerance: `symprec` and angle tolerances affect space-group results.
- Large structures: atom/site limits and preview truncation must be deterministic.
- Malformed structures: parser failures must be typed and user-readable.
- Missing coordinates/lattice: tools must distinguish non-periodic atoms from
  periodic structures.
- CI runtime: symmetry and parsing tests must stay small.
- Browser evidence: JSON/summary artifacts are stable; 3D screenshots are deferred.

## 12. Recommended Phase Split

### Phase 10C-1 Lightweight Structure Adapter Implementation

Implement the five lightweight structure adapters, registry entries, planner
routing, unit/API/frontend tests, and adapter-level evidence only.

### Phase 10C-2 Browser/API Evidence for Lightweight Structure Adapters

Run the Phase 9C workspace against real local structure inputs and capture
redacted API responses, screenshots, downloaded artifacts, summaries, recipes,
and manifests.

### Phase 10D Advanced Structure Visualization Planning

Plan 3D viewer, XRD, RDF, coordination, Brillouin zone, and phonon adapters after
lightweight structure contracts are stable.

## 13. Acceptance Criteria

This planning phase is complete when:

- No adapter implementation is added.
- Runtime, QueueWorkerRuntime, AnalysisPlanRepository, `/planner/jobs`, and
  PlanValidator semantics remain unchanged.
- Phase 10C scope is limited to lightweight structure adapters.
- Candidate matrix exists.
- Phase 10C-1 implementation prompt exists.
- Official-example mapping does not claim unsupported cases as PASS.
- Persistent files record the planning decision and remaining boundaries.
- `git diff --check` passes.
- If committed, CI passes without real LLM calls.

## 14. Final Recommendation

Proceed next to:

`Phase 10C-1: Lightweight Structure Adapter Implementation`

Do not jump directly to 3D viewers, XRD, RDF, phonons, or Brillouin-zone work.
