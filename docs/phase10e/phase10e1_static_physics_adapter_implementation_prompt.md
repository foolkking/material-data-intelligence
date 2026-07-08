# Phase 10E-1 Static Physics Adapter Implementation Prompt

## Goal

Implement the first low-risk static structure physics adapter selected by Phase 10E planning.

Recommended initial scope:

```text
structure.coordination_hist
```

Optional only if tolerance fixtures are pinned before implementation:

```text
structure.xrd
```

Do not implement `structure.rdf` unless the RDF normalization and cutoff policy has been explicitly promoted before starting.

## Repository Confirmation

Run:

```bash
cd "E:\1project\Material Data Intelligence"
git status --short
git log --oneline -10
git branch --show-current
git tag --points-at HEAD
```

Stop if the branch is not `master`, the worktree is dirty, or the HEAD does not include Phase 10E planning.

## Boundaries

- Do not break Phase 8B persisted plan exact execution.
- Do not break Phase 9D live LLM gated path.
- Do not break Phase 10A / 10B / 10C / 10D adapters or evidence.
- Do not implement full `structure.viewer_3d`.
- Do not implement WebGL renderer or Three.js.
- Do not implement phonon.
- Do not execute artifact JavaScript.
- Do not load external URLs.
- Do not run real LLM.
- Do not access external APIs.
- Do not execute notebooks or scripts.
- Do not modify QueueWorkerRuntime, AnalysisPlanRepository, `/planner/jobs`, or PlanValidator main semantics.

## Adapter Scope

### Required: `structure.coordination_hist`

Inputs:

- periodic CIF / POSCAR / Structure JSON / normalized structure dict using existing Phase 10C parser support.

Params:

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

Artifacts:

```text
coordination_hist.json
coordination_hist_plot.json
summary.md
recipe.json
```

Typed errors:

```text
coordination_non_periodic_structure
coordination_missing_lattice
coordination_invalid_params
coordination_generation_failed
artifact_write_failed
```

Warnings:

```text
ambiguous_neighbors
cutoff_sensitive
partial_occupancy_present
large_structure_truncated
empty_species_filter
```

### Optional: `structure.xrd`

Only implement if fixture peak windows and tolerances are pinned before coding.

Artifacts:

```text
xrd_pattern.json
xrd_pattern_plot.json
summary.md
recipe.json
```

Do not implement experimental fitting, Rietveld refinement, phase identification, or database lookup.

## Tool Registry

- Register implemented tools under domain `structure`.
- Use strict params schema with no arbitrary kwargs.
- Require periodic structures.
- Define resource limits for structures, sites, bins/peaks, and artifact size.
- Define deterministic output artifact names.

## Mock Planner Routing

Route:

- "coordination histogram", "coordination number", "neighbor count" -> `structure.coordination_hist`
- "XRD", "diffraction pattern", "powder diffraction" -> `structure.xrd` only if implemented

Return future_scope for:

- full 3D viewer
- WebGL
- Brillouin zone 3D
- phonon bands / DOS
- trajectory RDF
- experimental XRD fitting

## Artifact Contracts

`coordination_hist.json` must include:

```json
{
  "artifactType": "structure.coordination_hist",
  "neighborStrategy": "distance_cutoff",
  "cutoff": 3.0,
  "tolerance": 0.05,
  "structureCount": 0,
  "siteCount": 0,
  "bins": [],
  "byElement": {},
  "failedSites": [],
  "warnings": []
}
```

`coordination_hist_plot.json` must be deterministic Plotly-compatible JSON or a stable platform chart JSON.

`summary.md` must explain the neighbor policy and limitations.

`recipe.json` must include tool id, inputs, params, dependency versions, tolerance policy, deterministic flag, and artifact list.

## Tests

Add or update:

- structure fixture tests for simple cubic and NaCl-like fixtures.
- adapter unit tests for success, malformed input, non-periodic input, invalid params, truncation, warnings, and deterministic output.
- registry tests for schema, domain, resources, and artifacts.
- planner routing tests for coordination and future-scope viewer/phonon prompts.
- API execution tests for plan validation, persisted plan, job completion, tool call, and artifacts.
- frontend artifact preview tests only if new artifact types require UI handling.

## Evidence Policy

Phase 10E-1 only needs adapter-level lightweight evidence. Do not create browser/API evidence; that belongs to Phase 10E-2.

## Checks

Run:

```bash
uv lock --check
python -m pytest tests/test_phase7_llm_planner.py -q
python -m pytest tests/test_phase8b_persisted_plan_queue.py -q
python -m pytest tests/test_phase8c_planner_read_api.py -q
python -m pytest tests/test_phase9b_demo_workspace_api.py -q
python -m pytest -q
npm --prefix apps/web test
npm --prefix apps/web run typecheck
npm --prefix apps/web run build
git diff --check
```

## Commit / CI

If local checks pass:

```bash
git status --short
git diff --stat
git add .
git commit -m "Add static structure physics adapter"
git push origin master
```

Wait for CI current HEAD:

- unit job success
- frontend job success
- service-backed integration success
- no-skipped assertion passed
- default CI does not call real LLM

## Final Output

Use:

```markdown
# Phase 10E-1 Static Physics Adapter Implementation Result

## 1. Conclusion
PASS / PARTIAL_PASS / FAIL

## 2. Implemented Adapter
- structure.coordination_hist:
- structure.xrd:
- structure.rdf:

## 3. Artifact Outputs
- coordination_hist.json:
- coordination_hist_plot.json:
- summary.md:
- recipe.json:

## 4. Planner Routing
- coordination prompt:
- XRD prompt:
- future-scope full viewer / phonon prompt:

## 5. Tests
List local results.

## 6. Boundaries
- real LLM:
- WebGL:
- full structure.viewer_3d:
- phonon:
- notebook/script execution:
- runtime semantics:

## 7. Commit / CI
- commit:
- HEAD:
- CI run:
- git status:

## 8. Next Phase
Phase 10E-2 Browser/API Evidence for Static Physics Adapter.
```
