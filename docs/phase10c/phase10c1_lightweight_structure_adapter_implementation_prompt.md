# Phase 10C-1: Lightweight Structure Adapter Implementation Prompt

## Goal

Implement the Phase 10C-1 lightweight structure adapter batch:

- `structure.summary`
- `structure.lattice_summary`
- `structure.spacegroup_summary`
- `structure.composition_from_structure`
- `structure.preview_metadata`

Do not implement 3D viewers, XRD, RDF, coordination histograms, phonon, or
Brillouin-zone adapters in this phase. Browser/API evidence is Phase 10C-2.

## Repository Confirmation

Start by running:

```bash
cd "E:\1project\Material Data Intelligence"
git status --short
git log --oneline -8
git branch --show-current
git tag --points-at HEAD
```

Confirm:

- repository is Material Data Intelligence;
- branch is `master`;
- HEAD is the Phase 10C planning baseline or later;
- git status is clean.

Stop if the repository or working tree is wrong.

## Non-Regression Boundaries

Do not change:

- `QueueWorkerRuntime` main semantics;
- `AnalysisPlanRepository` main semantics;
- `/planner/jobs` validate/persist/enqueue semantics;
- PlanValidator safety boundary except to validate new registered params schemas;
- Phase 8B persisted plan exact execution;
- Phase 9D gated live LLM path;
- Phase 9C frontend information architecture.

Do not run real LLMs. Default CI must not call real LLM providers.

## Adapter Scope

### `structure.summary`

Inputs:

- CIF;
- POSCAR / CONTCAR;
- pymatgen Structure JSON;
- normalized `Structure` object or structure collection.

Artifacts:

- `structure_summary.json`;
- `summary.md`;
- `recipe.json`.

Required fields:

- `artifactType`;
- `structureCount`;
- formula/reduced formula;
- elements and element counts;
- site count;
- periodicity;
- lattice parameters where available;
- warnings.

Typed errors:

- `unsupported_structure_format`;
- `structure_parse_failed`;
- `empty_structure`;
- `missing_lattice`;
- `artifact_write_failed`.

### `structure.lattice_summary`

Artifacts:

- `lattice_summary.json`;
- `summary.md`;
- `recipe.json`.

Required fields:

- `artifactType`;
- `structureCount`;
- lattice stats for `a`, `b`, `c`, `alpha`, `beta`, `gamma`, `volume`;
- outliers;
- warnings.

Typed errors:

- `missing_lattice`;
- `non_periodic_structure`;
- `structure_parse_failed`;
- `empty_structure_collection`;
- `artifact_write_failed`.

### `structure.spacegroup_summary`

Artifacts:

- `spacegroup_summary.json`;
- `spacegroup_bar.json`;
- `summary.md`;
- `recipe.json`.

Dependency policy:

- Prefer existing `pymatgen`/`spglib` support if already available in the locked
  environment.
- If symmetry dependency is unavailable, return typed
  `symmetry_dependency_missing`; do not silently fabricate space groups.
- Pin default `symprec` and document it in recipe/provenance.

Typed errors:

- `symmetry_dependency_missing`;
- `symmetry_detection_failed`;
- `non_periodic_structure`;
- `structure_parse_failed`;
- `artifact_write_failed`.

### `structure.composition_from_structure`

Artifacts:

- `structure_composition.json`;
- `summary.md`;
- `recipe.json`.

Required fields:

- extracted formulas;
- element counts;
- chemical systems;
- `compositionAdapterCompatible`;
- recommended next composition tools.

This tool must not automatically execute composition adapters. It only emits an
auditable bridge artifact.

### `structure.preview_metadata`

Artifacts:

- `structure_preview_metadata.json`;
- `summary.md`;
- `recipe.json`.

Required fields:

- formula;
- site count;
- elements;
- bounding box;
- lattice vectors;
- truncated site preview;
- warnings.

This is not a 3D viewer. Do not emit arbitrary HTML or WebGL content.

## Tool Registry Requirements

Add or harden registry entries with:

- domain `structure`;
- explicit `paramsSchema`;
- `additionalProperties: false`;
- `inputSchema` requiring Structure objects or structure collections;
- resource limits for `maxStructures` and `maxAtomsPerStructure`;
- output artifacts including JSON, `summary_md`, and `recipe_json`;
- deterministic timeout and cache policy.

## Mock Planner Routing

Route prompts deterministically:

- structure summary / CIF basic info -> `structure.summary`;
- lattice parameters / unit cell -> `structure.lattice_summary`;
- space group / crystal system -> `structure.spacegroup_summary`;
- extract composition from structure -> `structure.composition_from_structure`;
- preview metadata / structure preview info -> `structure.preview_metadata`.

Do not route:

- 3D viewer prompts to these tools unless the prompt asks only for metadata;
- XRD/RDF/phonon/Brillouin-zone prompts to completed tools. Return clear future
  scope or unsupported guidance instead.

## Artifact Output

Every adapter must generate:

- deterministic JSON artifact;
- human-readable `summary.md`;
- `recipe.json` with tool id, adapter version, input identity/hash, params, and
  artifact list.

JSON artifacts must include top-level `artifactType` and `warnings`.

## Parser / Dependency Policy

- Reuse existing material parser outputs where available.
- Prefer `pymatgen` for structures if already installed.
- Do not add heavy dependencies without confirming lockfile impact and CI cost.
- Distinguish periodic structures from non-periodic atoms/molecules.
- Do not read arbitrary filesystem paths from user params.
- Do not access the network.

## Tests

Add or update:

- parser fixture tests for CIF, POSCAR, Structure JSON, malformed inputs;
- adapter unit tests for all five tools;
- registry tests for tool registration and params validation;
- planner routing tests;
- API execution tests covering plan validate, persisted plan, job completed,
  expected ToolCall, expected artifacts;
- frontend result rendering tests if new artifact types require UI handling.

Regression commands:

```bash
uv lock --check
python -m pytest tests/test_phase7_llm_planner.py -q
python -m pytest tests/test_phase8b_persisted_plan_queue.py -q
python -m pytest tests/test_phase8c_planner_read_api.py -q
python -m pytest tests/test_phase9b_demo_workspace_api.py -q
python -m pytest -q
npm test
npm run typecheck
npm run build
git diff --check
```

Do not run real LLM tests unless a separate gated live-verification phase is
explicitly requested.

## Evidence Scope

Phase 10C-1 may add lightweight adapter evidence under:

```text
docs/phase10c/adapter_evidence/
```

It must clearly state:

```text
Evidence level: Tool Registry + Adapter execution only
```

Do not create browser screenshots or API capture evidence in Phase 10C-1.

## Persistent Updates

Update:

- `persistent/DESIGN_PROGRESS.md`
- `persistent/TASK_BOARD.md`
- `persistent/CHANGELOG.md`
- `persistent/OPEN_QUESTIONS.md`
- `persistent/TOOL_REGISTRY_NOTES.md`
- `persistent/ARCHITECTURE_DECISIONS.md`

Record implemented adapters, tests, evidence level, and remaining advanced
structure/physics boundaries.

## Commit / CI

If all checks pass:

```bash
git status --short
git diff --stat
git add .
git commit -m "Add lightweight structure adapters"
git push origin master
```

Wait for GitHub Actions current HEAD:

- unit job success;
- frontend job success;
- service-backed integration success;
- no-skipped assertion passed;
- default CI does not call real LLM.

## Final Output

Use this format:

```markdown
# Phase 10C-1 Lightweight Structure Adapter Implementation Result

## 1. Conclusion
PASS / PARTIAL_PASS / FAIL

## 2. Implemented Adapters
- structure.summary:
- structure.lattice_summary:
- structure.spacegroup_summary:
- structure.composition_from_structure:
- structure.preview_metadata:

## 3. Artifact Output
- structure_summary.json:
- lattice_summary.json:
- spacegroup_summary.json:
- structure_composition.json:
- structure_preview_metadata.json:
- summary.md:
- recipe.json:

## 4. Planner Routing
- summary:
- lattice:
- spacegroup:
- composition from structure:
- preview metadata:

## 5. Tests
List local tests.

## 6. Boundaries
- real LLM:
- runtime main semantics:
- advanced 3D/XRD/RDF/phonon:
- benchmark pack modified:

## 7. Commit / CI
- commit:
- HEAD:
- CI run:
- git status:

## 8. Whether Phase 10C-1 Can Be Frozen
yes / no
```
