# Phase 10E-7: Static Physics Adapter Implementation - RDF

## Goal

Implement the single static physics adapter:

```text
structure.rdf
```

This phase implements only RDF numeric/static artifacts. It does not add browser/API evidence; Phase 10E-8 will handle evidence.

Required artifacts:

```text
rdf.json
rdf_plot.json
summary.md
recipe.json
```

## Current Baseline

```text
Phase 10E-5R2 commit: 4c7e392 Complete XRD browser screenshot evidence
Phase 10E-5 final status: PASS
Phase 10E-6 decision: RDF policy READY for single-scope implementation
branch: master
```

## Execution Discipline

1. Implement only `structure.rdf`.
2. Do not implement full interactive 3D viewer.
3. Do not implement WebGL renderer.
4. Do not introduce Three.js.
5. Do not implement `structure.viewer_3d`.
6. Do not implement `structure.brillouin_zone_3d`.
7. Do not implement phonon bands / DOS.
8. Do not implement trajectory RDF or time-averaged RDF.
9. Do not implement experimental PDF fitting, neutron scattering refinement, or X-ray total scattering analysis.
10. Do not modify `structure.xrd` core semantics.
11. Do not modify `structure.coordination_hist` core semantics.
12. Do not execute notebooks or external scripts.
13. Do not access the network.
14. Do not install new dependencies.
15. Do not run a real LLM.
16. Do not execute artifact JavaScript.
17. Do not load external artifact URLs.
18. Do not modify QueueWorkerRuntime main semantics.
19. Do not modify AnalysisPlanRepository main semantics.
20. Do not modify `/planner/jobs` main semantics.
21. Do not relax PlanValidator security boundaries.
22. Do not mark unsupported official examples as PASS.
23. Do not fabricate browser/API evidence.
24. Browser/API evidence is deferred to Phase 10E-8.

## Preflight

Run:

```powershell
cd "E:\1project\Material Data Intelligence"
git status --short
git log --oneline -35
git branch --show-current
git tag --points-at HEAD
```

Confirm:

- branch is `master`.
- working tree is clean.
- HEAD includes Phase 10E-6 commit.
- Phase 10E-6 docs exist:
  - `docs/phase10e/phase10e6_rdf_policy_hardening.md`
  - `docs/phase10e/phase10e6_rdf_policy_matrix.md`
  - `docs/phase10e/phase10e7_rdf_next_scope_prompt.md`
- `structure.rdf` is not already implemented.

If git status is not clean, stop and report current changes.

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
docs/phase10e/phase10e6_rdf_policy_hardening.md
docs/phase10e/phase10e6_rdf_policy_matrix.md
packages/adapters/mdi_adapters/platform_builtin/structure.py
packages/adapters/mdi_adapters/pymatviz/coordination_hist.py
packages/adapters/mdi_adapters/pymatviz/xrd.py
packages/tool-registry/mdi_tool_registry/loader.py
tool_registry/pymatviz_manifest.yaml
tests/test_phase10e1_coordination_hist.py
tests/test_phase10e4_xrd.py
```

## Implementation Scope

Add an adapter following existing project structure, likely:

```text
packages/adapters/mdi_adapters/pymatviz/rdf.py
```

Update only the necessary exports/registry/manifest/schema/routing/tests/docs/persistent files.

Do not add browser/API evidence in this phase.

## RDF Method

Definition:

```text
For a periodic crystalline structure, RDF is computed by counting interatomic distances under periodic boundary conditions up to r_max, binning distances into fixed-width radial bins, and normalizing by shell volume, number density, and center-site count.
```

Use:

- periodic `pymatgen Structure` input only.
- `Structure.get_all_neighbors(r_max_angstrom)` or equivalent existing pymatgen periodic neighbor helper.
- number-density normalization:

```text
g(r) = counts(r) / (N_center * rho_neighbor * shell_volume)
```

Exclude exact zero-distance self-pairs.

## Params Schema

Use strict whitelist params:

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

Validation:

- reject unknown params.
- reject `ceil(r_max_angstrom / bin_width_angstrom) > max_bins`.
- reject non-periodic structures.
- reject missing/non-positive volume.
- reject structures over `max_sites`.
- reject neighbor totals over `max_neighbors_total`.

## Artifact Contract

### `rdf.json`

Must include:

- `schema_version: "phase10e7.rdf.v1"`.
- `tool_id: "structure.rdf"`.
- source metadata.
- structure summary with formula, site count, species, PBC, and volume.
- normalized parameters.
- global `rdf` arrays: `r_angstrom`, `g_r`, `counts`, `bin_edges_angstrom`.
- normalization metadata: method, center count, neighbor count, density.
- optional `partial_rdf`, ordered by `center_element`, `neighbor_element`.
- limits.
- warnings.
- security flags: no JavaScript, no external URLs.

### `rdf_plot.json`

Must include:

- `schema_version: "phase10e7.static_chart.v1"`.
- `tool_id: "structure.rdf"`.
- `chart_type: "line"`.
- x-axis `r (angstrom)`.
- y-axis `g(r)`.
- deterministic series values.
- metadata.
- security flags.

### `summary.md`

Must include:

- Input.
- Method.
- Results.
- Limits.
- Security.

Must state no artifact JavaScript, no external URLs, no WebGL renderer, and no full 3D viewer.

### `recipe.json`

Must include:

- `schema_version: "phase10e7.recipe.v1"`.
- `tool_id: "structure.rdf"`.
- normalized inputs/params.
- deterministic steps.
- `dependencies.new_dependencies_added: false`.

## Deterministic Behavior

- structure labels sorted.
- site indices sorted.
- neighbors sorted by center index, distance, neighbor index, image vector if available, and neighbor element.
- bins sorted by radius.
- partial pairs sorted by `center_element`, then `neighbor_element`.
- numeric fields rounded to 6 decimals.
- filenames stable.
- warnings stable.

## Typed Errors / Warnings

Errors:

- `RDF_INPUT_MISSING`
- `RDF_PARSE_FAILED`
- `RDF_UNSUPPORTED_INPUT`
- `RDF_INVALID_PARAMS`
- `RDF_NON_PERIODIC_STRUCTURE`
- `RDF_INVALID_LATTICE_VOLUME`
- `RDF_SITE_LIMIT_EXCEEDED`
- `RDF_BIN_LIMIT_EXCEEDED`
- `RDF_NEIGHBOR_LIMIT_EXCEEDED`
- `RDF_PAIR_LIMIT_EXCEEDED`
- `RDF_ARTIFACT_WRITE_FAILED`

Warnings:

- `RDF_NORMALIZATION_NUMBER_DENSITY_ONLY`
- `RDF_CUTOFF_SENSITIVE`
- `RDF_BIN_WIDTH_SENSITIVE`
- `RDF_PERIODIC_IMAGES_REQUIRED`
- `RDF_PARTIAL_PAIRS_TRUNCATED`
- `RDF_LARGE_STRUCTURE_DEFERRED`
- `RDF_BROWSER_EVIDENCE_DEFERRED`
- `RDF_NOT_EXPERIMENTAL_PDF_FITTING`
- `RDF_NO_PHONON_DOS`

## Tool Registry

Register `structure.rdf` only if the adapter is implemented.

Requirements:

- domain `structure`.
- static RDF description.
- no claims for trajectory RDF, experimental fitting, phonon, WebGL, or 3D viewer.
- strict params schema.
- output artifacts:
  - `rdf.json`
  - `rdf_plot.json`
  - `summary.md`
  - `recipe.json`
- resource limits:
  - max structures.
  - max atoms/sites.
  - max bins.
  - max neighbors total.
  - max partial pairs.

## Mock Planner Routing

Route to `structure.rdf`:

- `计算 RDF`
- `生成 RDF`
- `计算径向分布函数`
- `生成径向分布函数`
- `Generate radial distribution function`
- `Create an RDF plot for this structure`
- `Compute pair distribution g(r)`
- `Show radial distribution g(r)`

Must not route to RDF:

- XRD prompts.
- coordination histogram prompts.
- full 3D viewer / WebGL prompts.
- Brillouin-zone prompts.
- phonon prompts.
- experimental PDF fitting / neutron scattering refinement prompts.

## Tests

Add or update tests for:

- basic RDF artifact generation.
- CIF / POSCAR / Structure dict fixtures.
- params validation.
- bin count and bin edge determinism.
- number-density normalization deterministic output.
- partial RDF ordered pairs.
- pair truncation warning.
- non-periodic rejection.
- invalid volume rejection if feasible.
- site limit rejection.
- neighbor limit rejection.
- no JavaScript / no external URL.
- registry schema.
- planner routing.
- negative routing for XRD, coordination, viewer, WebGL, phonon, fitting.
- persisted execution through QueueWorkerRuntime.
- regressions for Phase 10E-1 coordination and Phase 10E-4 XRD.

## Docs

Add:

```text
docs/phase10e/phase10e7_rdf_implementation.md
```

Document:

- scope.
- method.
- params.
- artifact contract.
- security boundary.
- tests.
- evidence deferred to Phase 10E-8.
- deferred scope.

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

- Phase 10E-7 started/completed.
- implemented `structure.rdf`.
- artifact contract.
- registry/routing updates.
- no browser/API evidence in this phase.
- no full viewer/WebGL/phonon/fitting.
- remaining Phase 10E-8 evidence.

## Checks

Run:

```powershell
git status --short
git diff --stat
git diff --check
uv lock --check
npm --prefix apps/web test
npm --prefix apps/web run typecheck
npm --prefix apps/web run build
uv run python -m pytest -q
```

Run a secret scan over changed docs/code and record `NO_SECRET_PATTERN_HITS`.

## Commit / CI

Commit:

```powershell
git add .
git commit -m "Implement RDF adapter"
git push origin master
```

Wait for GitHub Actions current HEAD:

- unit success.
- frontend success.
- service-backed integration success.
- no-skipped assertion passed.
- git status clean.

## Final Output

Report:

- PASS / PARTIAL_PASS / FAIL.
- baseline.
- RDF implementation details.
- artifact contract.
- params schema.
- security.
- tests/checks.
- commit/CI.
- whether Phase 10E-8 browser/API evidence may begin.

## Acceptance

PASS requires:

- only `structure.rdf` implemented.
- artifacts generated.
- registry and routing tests complete.
- negative routing boundaries preserved.
- deterministic tests pass.
- no JS / no external URLs.
- no new dependency.
- no real LLM.
- no RDF browser/API evidence claimed in Phase 10E-7.
- CI passes.

FAIL if:

- RDF implementation expands into full viewer/WebGL/phonon/fitting.
- notebook/script execution is added.
- runtime authority boundaries are relaxed.
- artifact JS or external URL loading is introduced.
- unsupported official examples are marked PASS.
