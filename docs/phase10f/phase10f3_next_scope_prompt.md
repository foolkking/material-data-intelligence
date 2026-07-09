# Phase 10F-3: Static Physics Direct-Uploadable Fixture Pack Planning

## Goal

Plan a small direct-uploadable expected-contract pack for the completed static structure physics tools:

- `structure.coordination_hist`
- `structure.xrd`
- `structure.rdf`

This phase should prepare fixture and expected-contract policy only. It must not create large files, execute notebooks, execute external scripts, implement a new adapter, or claim official PASS.

## Baseline

```text
Phase 10F-1 status: PARTIAL_PASS
Phase 10F-2 scope: official examples coverage gap closure planning
Official static physics direct PASS cases: none
Completed static physics tools:
- structure.coordination_hist
- structure.xrd
- structure.rdf
```

## Execution Discipline

1. Do not implement a new adapter.
2. Do not modify `structure.coordination_hist`, `structure.xrd`, or `structure.rdf` core semantics.
3. Do not execute notebooks.
4. Do not execute external scripts or benchmark extraction scripts.
5. Do not call external APIs.
6. Do not access the internet.
7. Do not install dependencies.
8. Do not run a real LLM.
9. Do not claim official PASS.
10. Do not fabricate expected outputs or evidence.
11. Do not implement full `structure.viewer_3d`.
12. Do not introduce WebGL or Three.js.
13. Do not implement phonon tools.
14. Do not modify QueueWorkerRuntime, AnalysisPlanRepository, `/planner/jobs`, or PlanValidator main semantics.

## Preflight

Run:

```bash
cd "E:\1project\Material Data Intelligence"
git status --short
git log --oneline -55
git branch --show-current
git tag --points-at HEAD
```

Confirm:

- branch is `master`;
- git status is clean;
- HEAD is at or after Phase 10F-2;
- Phase 10F-2 docs exist;
- no official static physics PASS claim exists.

Stop if the working tree is dirty.

## Read Project State

Read:

- `README.md`
- `AGENTS.md`
- `MASTER_PROMPT.md`
- `persistent/PROJECT_BRIEF.md`
- `persistent/DESIGN_PROGRESS.md`
- `persistent/TASK_BOARD.md`
- `persistent/CHANGELOG.md`
- `persistent/OPEN_QUESTIONS.md`
- `persistent/TOOL_REGISTRY_NOTES.md`
- `persistent/ARCHITECTURE_DECISIONS.md`
- `docs/phase10f/phase10f1_official_examples_direct_verification.md`
- `docs/phase10f/phase10f2_official_coverage_gap_analysis.md`
- `docs/phase10f/phase10f2_coverage_gap_matrix.md`
- `docs/phase10f/phase10f2_direct_uploadable_fixture_proposal.md`
- `docs/phase10f/phase10f2_expected_contract_authoring_plan.md`

Read the local benchmark pack metadata only if present:

```text
C:\Users\86182\Desktop\pymatviz_official_examples_test_suite
```

Do not execute any notebook, script, extraction workflow, or external API.

## Fixture Candidate Policy

For each static physics tool, propose one or more tiny direct-uploadable fixture candidates:

- input must be CIF, POSCAR/CONTCAR, or generated Structure JSON already supported by the platform;
- file should be small and text-reviewable;
- no disordered or very large structure in the first pack;
- provenance must be labeled as `official_direct`, `official_derived_manual`, `official_like_curated`, or `internal_regression`;
- fixture candidate does not become official PASS evidence until a later execution phase.

## Expected Contract Policy

For each candidate, plan an `expected_contract.json` shape:

- exact schema/tool/artifact/security assertions;
- tolerance-bounded numeric assertions;
- metadata-only fields;
- allowed-to-vary fields;
- no-PASS-claim status.

## Provenance Policy

Record how each candidate was selected and why it does or does not qualify as official-derived. Internal regression fixtures must stay labeled internal and must not be promoted to official PASS.

## Deliverables

Add docs under `docs/phase10f/`:

- `phase10f3_static_physics_fixture_pack_planning.md`
- `phase10f3_fixture_candidate_matrix.md`
- `phase10f3_expected_contract_templates.md`
- `phase10f4_next_scope_prompt.md`

## Persistent Updates

Update:

- `persistent/DESIGN_PROGRESS.md`
- `persistent/TASK_BOARD.md`
- `persistent/CHANGELOG.md`
- `persistent/OPEN_QUESTIONS.md`
- `persistent/TOOL_REGISTRY_NOTES.md`
- `persistent/ARCHITECTURE_DECISIONS.md`

Record that Phase 10F-3 is planning only and does not create official PASS evidence.

## Checks

Run:

```bash
git status --short
git diff --stat
git diff --check
uv lock --check
```

If project policy requires smoke checks:

```bash
npm --prefix apps/web run typecheck
uv run python -m pytest -q
```

Do not run a real LLM.

## Redaction / Secret Scan

Scan at least:

```text
docs/phase10f
persistent
```

Record:

```text
NO_SECRET_PATTERN_HITS
```

## Commit / CI

Commit:

```bash
git add docs/phase10f persistent
git commit -m "Plan static physics fixture pack"
git push origin master
```

Wait for CI:

- unit success
- frontend success
- service-backed integration success
- no-skipped assertion passed
- default CI does not call real LLM

## PASS / PARTIAL_PASS / FAIL

PASS requires:

- fixture candidate matrix completed;
- expected contract templates completed;
- provenance policy completed;
- no official PASS claim added;
- no notebook/script/API execution;
- no new adapter/viewer/WebGL/Three.js/phonon implementation;
- docs/persistent updated;
- checks and CI passed.

PARTIAL_PASS allows:

- fixture candidates still requiring human approval;
- CI pending after local checks pass;
- official-derived provenance remaining unknown if clearly labeled.

FAIL if:

- any unsupported or unexecuted case is marked PASS;
- notebook/script/API/network workflows are executed;
- a new adapter, full viewer, WebGL, Three.js, or phonon is implemented;
- evidence is fabricated.

