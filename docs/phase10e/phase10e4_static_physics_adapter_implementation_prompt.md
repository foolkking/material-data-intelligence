# Phase 10E-4: Static Physics Adapter Implementation - XRD

## Goal

Implement the next static structure physics adapter:

```text
structure.xrd
```

This phase must generate deterministic, testable, static artifacts:

```text
xrd_pattern.json
xrd_plot.json
summary.md
recipe.json
```

Phase 10E-4 must not add browser/API evidence. Phase 10E-5 should cover browser/API evidence after implementation passes.

## Current Baseline

- Phase 10E-1 commit: `2beb8b7 Implement coordination histogram adapter`.
- Phase 10E-2 commit: `39e1929 Add coordination histogram browser API evidence`.
- Phase 10E-3 decision: implement `structure.xrd` next; defer `structure.rdf`.
- Existing completed static physics adapter: `structure.coordination_hist`.

## Execution Discipline

1. Only implement `structure.xrd`.
2. Do not implement `structure.rdf`.
3. Do not implement full interactive 3D viewer.
4. Do not implement WebGL renderer or introduce Three.js.
5. Do not implement `structure.viewer_3d` or `structure.brillouin_zone_3d`.
6. Do not implement phonon bands / DOS.
7. Do not execute notebooks or scripts.
8. Do not access external networks or databases.
9. Do not install new dependencies.
10. Do not run a real LLM.
11. Do not execute artifact JavaScript or load external URLs.
12. Do not modify QueueWorkerRuntime, AnalysisPlanRepository, `/planner/jobs`, or PlanValidator main semantics.
13. Do not change `structure.coordination_hist` semantics.
14. Do not claim unsupported official examples as PASS.
15. Do not add browser screenshots or API captures in this phase.

## Prerequisite Confirmation

Run:

```bash
cd "E:\1project\Material Data Intelligence"
git status --short
git log --oneline -25
git branch --show-current
git tag --points-at HEAD
```

Confirm:

- branch is `master`.
- git status is clean.
- current HEAD includes Phase 10E-3 planning.
- Phase 10E-1 and Phase 10E-2 docs exist.
- Phase 10E-3 readiness decision exists.

If the worktree is not clean, stop.

## Read Project State

Read:

```text
README.md
AGENTS.md
MASTER_PROMPT.md
persistent/PROJECT_BRIEF.md
persistent/DESIGN_PROGRESS.md
persistent/TASK_BOARD.md
persistent/CHANGELOG.md
persistent/OPEN_QUESTIONS.md
persistent/TOOL_REGISTRY_NOTES.md
persistent/ARCHITECTURE_DECISIONS.md
docs/13_SHARED_SCHEMA_SPEC.md
docs/14_PYMATVIZ_CAPABILITY_INVENTORY.md
docs/15_ADAPTER_IMPLEMENTATION_PLAN.md
docs/phase10c
docs/phase10d
docs/phase10e/phase10e_static_structure_physics_plot_planning.md
docs/phase10e/phase10e3_xrd_rdf_readiness_decision.md
docs/phase10e/phase10e3_static_physics_next_scope_matrix.md
```

Inspect:

```text
pyproject.toml
uv.lock
packages/adapters/mdi_adapters/platform_builtin/structure.py
packages/adapters/mdi_adapters/pymatviz/coordination_hist.py
packages/adapters/mdi_adapters/registry.py
packages/tool-registry/mdi_tool_registry/loader.py
tool_registry/pymatviz_manifest.yaml
services/llm/mdi_llm/providers.py
tests/fixtures/structures
tests/test_phase10e1_coordination_hist.py
```

## Implementation Scope

### Required Tool

```text
structure.xrd
```

Purpose: generate a deterministic static powder XRD pattern from a bounded periodic structure input.

Use existing structure parser support for:

- CIF text / fixture
- POSCAR / CONTCAR text / fixture
- pymatgen Structure dict / normalized structure dict when already supported

Preferred engine:

```text
pymatgen.analysis.diffraction.xrd.XRDCalculator
```

Do not add dependencies. If `XRDCalculator` is unexpectedly unavailable, return typed dependency error and cover the current environment path in tests.

## Params Schema

Use the existing Tool Registry schema style with `additionalProperties: false`.

Recommended params:

```json
{
  "radiation": {
    "type": "string",
    "default": "CuKa",
    "enum": ["CuKa"]
  },
  "two_theta_min": {
    "type": "number",
    "default": 0.0,
    "minimum": 0.0,
    "maximum": 180.0
  },
  "two_theta_max": {
    "type": "number",
    "default": 90.0,
    "minimum": 1.0,
    "maximum": 180.0
  },
  "peak_merge_tolerance": {
    "type": "number",
    "default": 0.05,
    "minimum": 0.0,
    "maximum": 1.0
  },
  "intensity_threshold": {
    "type": "number",
    "default": 0.0,
    "minimum": 0.0,
    "maximum": 100.0
  },
  "max_peaks": {
    "type": "integer",
    "default": 500,
    "minimum": 1,
    "maximum": 5000
  },
  "plot_kind": {
    "type": "string",
    "default": "stem",
    "enum": ["stem"]
  }
}
```

Reject invalid ranges such as `two_theta_min >= two_theta_max`.

## Artifact Contract

### `xrd_pattern.json`

Required semantics:

```json
{
  "artifactType": "structure.xrd",
  "schema_version": "phase10e4.xrd_pattern.v1",
  "tool_id": "structure.xrd",
  "source": {},
  "structure": {
    "formula": "",
    "site_count": 0,
    "species": [],
    "pbc": [true, true, true]
  },
  "parameters": {
    "radiation": "CuKa",
    "two_theta_min": 0.0,
    "two_theta_max": 90.0,
    "peak_merge_tolerance": 0.05,
    "intensity_threshold": 0.0,
    "max_peaks": 500
  },
  "radiation": {
    "name": "CuKa",
    "wavelength_angstrom": 1.5406
  },
  "two_theta_range": [0.0, 90.0],
  "peaks": [
    {
      "two_theta": 28.44,
      "intensity": 100.0,
      "d_spacing": 3.136,
      "hkls": [
        {"h": 1, "k": 1, "l": 1, "multiplicity": 8}
      ]
    }
  ],
  "limits": {
    "max_peaks": 500,
    "peak_count_before_truncation": 0,
    "truncated": false
  },
  "warnings": [],
  "security": {
    "contains_javascript": false,
    "external_urls": [],
    "external_urls_allowed": false
  }
}
```

### `xrd_plot.json`

Required semantics:

```json
{
  "artifactType": "structure.xrd_plot",
  "schema_version": "phase10e4.static_chart.v1",
  "tool_id": "structure.xrd",
  "chart_type": "stem",
  "title": "XRD Pattern",
  "x_axis": {
    "label": "2theta (degrees)",
    "values": []
  },
  "y_axis": {
    "label": "Relative intensity",
    "values": []
  },
  "series": [
    {
      "name": "XRD peaks",
      "x": [],
      "y": []
    }
  ],
  "metadata": {
    "formula": "",
    "radiation": "CuKa",
    "two_theta_range": [0.0, 90.0]
  },
  "security": {
    "contains_javascript": false,
    "external_urls": [],
    "external_urls_allowed": false
  }
}
```

### `summary.md`

Include:

- input source, parser, formula, site count.
- method: XRDCalculator, radiation, two-theta range, intensity normalization, peak filtering.
- results: peak count, strongest peak, top peaks.
- limits and warnings.
- explicit non-scope: no phase identification, no Rietveld refinement, no experimental fitting, no external database lookup.
- security: no artifact JavaScript, no external URLs, no WebGL renderer, no full 3D viewer.

### `recipe.json`

Include:

```json
{
  "schema_version": "phase10e4.recipe.v1",
  "tool_id": "structure.xrd",
  "inputs": {},
  "params": {},
  "steps": [
    "parse_structure",
    "validate_periodic_structure",
    "configure_xrd_calculator",
    "generate_xrd_pattern",
    "filter_and_sort_peaks",
    "write_xrd_pattern_json",
    "write_static_chart_json",
    "write_summary"
  ],
  "deterministic": true,
  "dependencies": {
    "new_dependencies_added": false
  }
}
```

## Deterministic Behavior

Requirements:

- fixed default radiation: `CuKa`.
- fixed default two-theta range: `[0.0, 90.0]`.
- peaks sorted by `two_theta`, then intensity, then hkl text.
- numeric fields rounded to fixed precision.
- hkl lists sorted deterministically.
- warnings stable and sorted.
- output artifact names stable.
- fixture tests pin expected peak windows, not exact long raw arrays.

Recommended precision:

- `two_theta`: 6 decimals.
- `intensity`: 6 decimals.
- `d_spacing`: 6 decimals.

## Typed Errors / Warnings

Recommended errors:

- `XRD_INPUT_MISSING`
- `XRD_PARSE_FAILED`
- `XRD_UNSUPPORTED_INPUT`
- `XRD_NON_PERIODIC_STRUCTURE`
- `XRD_DEPENDENCY_MISSING`
- `XRD_INVALID_PARAMS`
- `XRD_GENERATION_FAILED`
- `XRD_PEAKS_EMPTY`
- `XRD_ARTIFACT_WRITE_FAILED`

Recommended warnings:

- `XRD_TOLERANCE_SENSITIVE`
- `XRD_PEAKS_TRUNCATED`
- `XRD_PARTIAL_OCCUPANCY_PRESENT`
- `XRD_DISORDER_PRESENT`
- `XRD_EXPERIMENTAL_FITTING_NOT_PERFORMED`
- `XRD_PHASE_IDENTIFICATION_NOT_PERFORMED`
- `XRD_DATABASE_LOOKUP_NOT_PERFORMED`

## Security Boundary

Tests must assert:

- `xrd_pattern.json` contains no JavaScript.
- `xrd_plot.json` contains no JavaScript.
- `summary.md` contains no script tag.
- `recipe.json` contains no script tag.
- artifacts contain no external URL.
- `security.external_urls_allowed` is false.
- no HTML app is generated.
- no WebGL / canvas viewer is generated.
- no notebook/script execution.
- no external API call.
- no real LLM.
- no arbitrary local path read.

## Tool Registry Plan

Register `structure.xrd` as executable only after the adapter is implemented.

Requirements:

- domain: `structure`.
- strict params schema.
- resource limits for structures, sites, and peaks.
- output artifacts: `xrd_pattern.json`, `xrd_plot.json`, `summary.md`, `recipe.json`.
- description must say static XRD pattern, not experimental fitting or phase identification.
- capability tags must not claim RDF, phonon, WebGL, full viewer, Rietveld refinement, or database lookup.

## Mock Planner Routing Plan

Route to `structure.xrd` after implementation:

- "Generate XRD pattern"
- "powder diffraction pattern"
- "simulate CuKa diffraction peaks"
- "show X-ray diffraction peaks"

Do not route these to `structure.xrd`:

- RDF / radial distribution function
- coordination histogram / neighbor count
- full interactive 3D viewer / WebGL
- Brillouin zone 3D
- phonon bands / DOS
- Rietveld refinement
- experimental XRD fitting
- crystallographic database lookup

## Tests

Add or update tests for:

- XRD adapter basic artifact generation.
- CIF fixture success.
- POSCAR fixture success.
- Structure dict fixture success if current parser supports it.
- malformed input typed error.
- non-periodic or missing lattice typed error/warning path.
- invalid params rejected.
- two-theta range validation.
- intensity threshold filters peaks.
- max peaks truncation warning.
- deterministic output.
- peak sorting and rounding.
- hkl metadata presence when available.
- no JavaScript / no external URL assertions.
- Tool Registry registration and strict schema.
- Mock Planner XRD prompt routing.
- negative routing for RDF, coordination, full viewer, WebGL, phonon, Rietveld, database lookup.
- persisted execution through existing QueueWorkerRuntime path.
- Phase 10C structure regression.
- Phase 10D viewer scene regression.
- Phase 10E-1 coordination histogram regression.

## Docs

Add:

```text
docs/phase10e/phase10e4_xrd_implementation.md
```

Include:

- scope and non-scope.
- method and dependency decision.
- params schema.
- artifact contract.
- deterministic behavior and tolerance policy.
- security boundary.
- planner routing.
- tests.
- evidence policy: Phase 10E-5 will add browser/API evidence.
- deferred scope: RDF, full viewer, WebGL, Brillouin-zone, phonon, Rietveld, experimental fitting, notebook/script.

## Persistent Updates

Update:

```text
persistent/DESIGN_PROGRESS.md
persistent/TASK_BOARD.md
persistent/CHANGELOG.md
persistent/OPEN_QUESTIONS.md
persistent/TOOL_REGISTRY_NOTES.md
persistent/ARCHITECTURE_DECISIONS.md
```

Record:

- Phase 10E-4 started/completed.
- `structure.xrd` implemented.
- artifact contract.
- Tool Registry update.
- Mock Planner routing update.
- tests and dependency decision.
- no RDF.
- no full viewer/WebGL/phonon.
- browser/API evidence deferred to Phase 10E-5.

## Checks

Run:

```bash
git status --short
git diff --stat
git diff --check
uv lock --check
npm --prefix apps/web test
npm --prefix apps/web run typecheck
npm --prefix apps/web run build
python -m pytest -q
```

Run a secret scan over changed docs/code and record `NO_SECRET_PATTERN_HITS`.

## Commit / CI

If checks pass:

```bash
git status --short
git diff --stat
git add .
git commit -m "Implement XRD adapter"
git push origin master
```

Wait for current-HEAD CI:

- unit success.
- frontend success.
- service-backed integration success.
- no-skipped assertion passed.
- default CI does not call real LLM.
- git status clean.

## Final Output Format

```markdown
# Phase 10E-4 Static Physics Adapter Implementation - XRD Result

## 1. Conclusion
PASS / PARTIAL_PASS / FAIL

## 2. Baseline
- Phase 10E-3 HEAD:
- branch:
- git status before:

## 3. Implementation
- structure.xrd:
- dependency:
- params validation:
- Tool Registry:
- Mock Planner routing:

## 4. Artifact Contract
- xrd_pattern.json:
- xrd_plot.json:
- summary.md:
- recipe.json:
- schema_version:
- tool_id:
- limits / warnings:

## 5. Explicitly Not Implemented
- structure.rdf:
- full interactive 3D viewer:
- WebGL renderer:
- Three.js:
- structure.viewer_3d:
- structure.brillouin_zone_3d:
- phonon.bands:
- phonon.dos:
- Rietveld refinement:
- experimental XRD fitting:
- notebook/script extraction:
- external API workflows:

## 6. Security
- no artifact JS:
- no external URLs:
- no renderer bundle:
- no real LLM:
- no arbitrary file read:
- no secret pattern hits:

## 7. Tests
- unit tests:
- fixture tests:
- registry tests:
- planner routing tests:
- artifact contract tests:
- regression tests:
- no-skipped assertion:

## 8. Docs / Persistent Updates

## 9. Checks
- git diff --check:
- uv lock --check:
- npm --prefix apps/web test:
- npm --prefix apps/web run typecheck:
- npm --prefix apps/web run build:
- python -m pytest -q:
- CI:

## 10. Commit / CI
- commit:
- HEAD:
- CI run:
- unit:
- frontend:
- service-backed integration:
- no-skipped assertion:
- git status:

## 11. Allow Phase 10E-5
yes / no

## 12. Next Step
Phase 10E-5: Browser/API Evidence for XRD.

Do not proceed to RDF, full structure.viewer_3d, WebGL, or phonon.
```

## PASS Criteria

- `structure.xrd` implemented and registered.
- `structure.rdf` not implemented.
- no full viewer/WebGL/phonon implementation.
- deterministic artifacts generated.
- strict params validation.
- planner routing and negative routing tested.
- artifact contract/security tests pass.
- no new dependencies.
- checks and CI pass.
- persistent and docs updated.

## PARTIAL_PASS Criteria

- Browser/API evidence is absent because it belongs to Phase 10E-5.
- Official examples remain mapping-only.
- CI is pending due to external reasons but local checks pass and are recorded.

## FAIL Criteria

- implements RDF, full viewer, WebGL, phonon, notebook/script, or external API workflow.
- modifies runtime main semantics or PlanValidator boundary.
- artifacts contain JS or external URLs.
- unsupported official examples are marked PASS.
- no XRD artifact contract is generated.
