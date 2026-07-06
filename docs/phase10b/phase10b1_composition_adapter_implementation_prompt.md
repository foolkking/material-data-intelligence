# Phase 10B-1 Composition Adapter Implementation Prompt

Use this prompt for the next implementation phase. Do not execute it during
Phase 10B planning.

---

You are executing:

`Phase 10B-1: Composition Visualization Adapter Implementation`

## Goal

Implement or harden composition visualization adapters so the platform can turn
official pymatviz composition examples into validated, persisted, auditable
adapter execution.

Recommended adapter scope:

- `composition.ptable_heatmap`
- `composition.elements_hist`
- `composition.chem_sys_treemap`
- `composition.chem_sys_sunburst`
- `composition.formula_statistics`

This implementation phase must not capture full browser/API evidence. That is
reserved for Phase 10B-2.

## Repository Confirmation

Run first:

```bat
cd /d "E:\1project\Material Data Intelligence"
git status --short
git log --oneline -8
git branch --show-current
git tag --points-at HEAD
```

Confirm:

- branch is `master`
- working tree is clean
- current HEAD is at or after Phase 10B planning
- no unrelated local changes exist

If the working tree is dirty, stop and report.

## Required Reading

Read:

- `AGENTS.md`
- `persistent/PROJECT_BRIEF.md`
- `persistent/DESIGN_PROGRESS.md`
- `persistent/TASK_BOARD.md`
- `persistent/ARCHITECTURE_DECISIONS.md`
- `docs/13_SHARED_SCHEMA_SPEC.md`
- `docs/14_PYMATVIZ_CAPABILITY_INVENTORY.md`
- `docs/15_ADAPTER_IMPLEMENTATION_PLAN.md`
- `docs/phase10a/phase10a1_first_batch_adapter_design.md`
- `docs/phase10a/browser_api_evidence/EVIDENCE_INDEX.md`
- `docs/phase10b/phase10b_second_batch_adapter_planning.md`
- `docs/phase10b/phase10b_candidate_adapter_matrix.md`

Read benchmark pack files without modifying them:

- `C:\Users\86182\Desktop\pymatviz_official_examples_test_suite\BENCHMARK_READINESS.md`
- `C:\Users\86182\Desktop\pymatviz_official_examples_test_suite\NEXT_PHASE_CANDIDATES.md`
- `C:\Users\86182\Desktop\pymatviz_official_examples_test_suite\CASE_INDEX.json`
- `C:\Users\86182\Desktop\pymatviz_official_examples_test_suite\cases\ward_metallic_glasses_csv_xz\expected_contract.json`

## Non-Negotiable Boundaries

Do not break:

- Phase 8B persisted plan exact execution
- Phase 9D gated live LLM path
- Phase 9C UI information architecture
- Tool Registry + Adapter execution boundary
- PlanValidator enforcement
- default CI safety without real LLM calls

Do not:

- let the LLM execute Python, shell, filesystem, or network actions
- access the network from adapters
- read arbitrary filesystem paths from adapters
- write artifacts outside the controlled artifact writer
- store API keys or Authorization headers in plans/events/artifacts/reports
- mark unsupported official examples as PASS
- modify benchmark pack case types or verification status

## Adapter Scope

### `composition.ptable_heatmap`

Purpose: aggregate formula/composition data into periodic-table heatmap artifacts.

Params:

- `formulaColumn?: string`
- `compositionColumn?: string`
- `valueColumn?: string`
- `aggregation?: "count" | "sum" | "mean" | "median" | "fraction"`
- `scale?: "linear" | "log"`
- `title?: string`
- `maxFormulas?: number`

Artifacts:

- `ptable_heatmap.json`
- `ptable_heatmap.html`
- `summary.md`
- `recipe.json`

Errors:

- `missing_formula_column`
- `invalid_formula`
- `unsupported_aggregation`
- `empty_composition_set`
- `artifact_write_failed`

### `composition.elements_hist`

Purpose: count element frequencies/fractions from formulas.

Params:

- `formulaColumn?: string`
- `compositionColumn?: string`
- `countMode?: "formula_presence" | "stoichiometric_count" | "fractional"`
- `topN?: number`
- `sortBy?: "count" | "atomic_number" | "symbol"`

Artifacts:

- `elements_hist.json`
- `elements_hist.html`
- `summary.md`
- `recipe.json`

Errors:

- `missing_formula_column`
- `invalid_formula`
- `empty_composition_set`
- `artifact_write_failed`

### `composition.chem_sys_treemap`

Purpose: aggregate formulas by canonical chemical systems.

Params:

- `formulaColumn?: string`
- `compositionColumn?: string`
- `maxSystems?: number`
- `minCount?: number`
- `groupRareAsOther?: boolean`
- `systemOrder?: "alphabetical" | "count_desc"`

Artifacts:

- `chem_sys_treemap.json`
- `chem_sys_treemap.html`
- `summary.md`
- `recipe.json`

Errors:

- `missing_formula_column`
- `invalid_formula`
- `empty_composition_set`
- `too_many_systems`
- `artifact_write_failed`

### `composition.chem_sys_sunburst`

Purpose: represent chemical systems hierarchically by arity and element set.

Params:

- `formulaColumn?: string`
- `compositionColumn?: string`
- `maxDepth?: number`
- `maxSystems?: number`
- `groupRareAsOther?: boolean`
- `title?: string`

Artifacts:

- `chem_sys_sunburst.json`
- `chem_sys_sunburst.html`
- `summary.md`
- `recipe.json`

Errors:

- `missing_formula_column`
- `invalid_formula`
- `empty_composition_set`
- `too_many_systems`
- `artifact_write_failed`

### `composition.formula_statistics`

Purpose: generate machine-readable formula statistics and parser diagnostics.

Params:

- `formulaColumn?: string`
- `compositionColumn?: string`
- `includeElementFractions?: boolean`
- `includeArity?: boolean`
- `includeReducedFormula?: boolean`
- `maxRows?: number`

Artifacts:

- `formula_statistics.json`
- `formula_statistics.csv`
- `summary.md`
- `recipe.json`

Errors:

- `missing_formula_column`
- `invalid_formula`
- `empty_composition_set`
- `artifact_write_failed`

## Tool Registry Registration

For each new or hardened adapter:

- register tool id in Tool Registry
- use domain `composition`
- define params schema
- define input resource expectations
- define output artifact schema
- define resource limits
- keep stage consistent with MVP/V1 scope
- ensure PlanValidator rejects unknown tools and invalid params

If `composition.ptable_heatmap`, `composition.elements_hist`, or
`composition.chem_sys_treemap` already exist, harden them in place instead of
creating duplicate tool ids.

## Mock Planner Routing

Add deterministic routing:

- "元素分布" / "elements histogram" -> `composition.elements_hist`
- "周期表热力图" / "ptable heatmap" -> `composition.ptable_heatmap`
- "化学体系分布" / "chem sys treemap" -> `composition.chem_sys_treemap`
- "sunburst" / "层级化学体系" -> `composition.chem_sys_sunburst`
- "formula statistics" / "formula 统计" -> `composition.formula_statistics`

Rules:

- Use Ward `composition` column only when profile confirms it exists.
- If no formula/composition field exists, fail clearly.
- Do not route generic Ward analysis to `ml.basic_metrics`.
- Do not fabricate composition outputs.

## Artifact Output Requirements

Every adapter must produce:

- primary JSON artifact
- optional HTML artifact when supported
- `summary.md`
- `recipe.json`

Every artifact must include provenance:

- `jobId`
- `planId`
- `planHash`
- `toolCallId`
- `toolId`
- params

## Tests

Add or update:

- adapter unit tests for all composition adapters
- registry schema tests
- PlanValidator invalid params tests
- Mock Planner routing tests
- persisted one-step execution tests
- artifact existence and content tests
- frontend Results/export rendering tests when needed

Regression commands:

```bat
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

Do not run real LLM tests unless explicitly requested in a separate gated phase.

## Evidence Boundary

Phase 10B-1 should create lightweight implementation/test evidence only.

Do not create full browser/API evidence here. Phase 10B-2 will capture:

- browser screenshots
- redacted API responses
- downloaded artifacts
- evidence manifests

## Commit and CI

Before commit, report:

- modified files
- adapters implemented/hardened
- routing changes
- tests run
- default CI real LLM status
- whether Phase 8B/9D boundaries changed

If all checks pass:

```bat
git add .
git commit -m "Add composition visualization adapters"
git push origin master
```

Wait for GitHub Actions current HEAD:

- unit job success
- frontend job success
- service-backed integration success
- no-skipped integration assertion remains passing
- default CI does not call real LLM

## Final Output Format

```markdown
# Phase 10B-1 Composition Adapter Implementation Result

## 1. Conclusion
PASS / PARTIAL_PASS / FAIL

## 2. Implemented Adapters
- composition.ptable_heatmap:
- composition.elements_hist:
- composition.chem_sys_treemap:
- composition.chem_sys_sunburst:
- composition.formula_statistics:

## 3. Planner Routing
- Ward composition:
- ptable heatmap:
- element histogram:
- chemical-system treemap:
- chemical-system sunburst:
- formula statistics:

## 4. Tests
List commands and results.

## 5. Boundaries
- Phase 8B:
- Phase 9D:
- default CI:
- Tool Registry + Adapter:
- API key leakage:
- external network:

## 6. Commit / CI
- commit:
- HEAD:
- CI run:
- git status:

## 7. Whether Phase 10B-2 Evidence Can Start
yes / no
```
