# Phase 10F-7：Advanced Structure Viewer Readiness Planning

## Goal

Enter Phase 10F-7 to plan advanced structure viewer readiness.

This phase is planning only. Do not implement `structure.viewer_3d`, do not introduce WebGL or Three.js, and do not implement phonon, Brillouin-zone 3D, or advanced local environment classification.

## Current Baseline

- Phase 10F-5: static physics fixture-pack replay PASS.
- Phase 10F-6: static physics fixture-pack evidence closure PASS.
- Static physics tools closed:
  - `structure.coordination_hist`
  - `structure.xrd`
  - `structure.rdf`
- Fixture-pack PASS: yes.
- Official PASS: no.
- Reason: replayed fixture cases are `internal_regression`, not `official_direct` or approved `official_derived_manual`.

## Execution Discipline

1. Only do advanced viewer readiness planning.
2. Do not implement full `structure.viewer_3d`.
3. Do not implement WebGL renderer.
4. Do not introduce Three.js.
5. Do not implement `structure.brillouin_zone_3d`.
6. Do not implement phonon bands, phonon DOS, or phonon band/DOS tools.
7. Do not implement advanced local environment classification.
8. Do not execute notebooks.
9. Do not execute external scripts.
10. Do not access external APIs.
11. Do not install dependencies.
12. Do not run a real LLM.
13. Do not execute artifact JavaScript.
14. Do not load external artifact URLs.
15. Do not modify QueueWorkerRuntime, AnalysisPlanRepository, `/planner/jobs`, or PlanValidator semantics.
16. Do not change static physics adapter semantics.
17. Allow docs, matrices, readiness plans, artifact-contract proposals, security-model proposals, and persistent updates.

## Preflight

Run:

```bash
cd "E:\1project\Material Data Intelligence"
git status --short
git log --oneline -75
git branch --show-current
git tag --points-at HEAD
```

Confirm:

- branch is `master`;
- git status is clean;
- Phase 10F-6 docs exist;
- static physics fixture-pack replay evidence is closed;
- no full viewer / WebGL / Three.js / phonon implementation exists.

If git status is not clean, stop and report current changes.

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
- `docs/13_SHARED_SCHEMA_SPEC.md`
- `docs/14_PYMATVIZ_CAPABILITY_INVENTORY.md`
- `docs/15_ADAPTER_IMPLEMENTATION_PLAN.md`
- `docs/phase10d`
- `docs/phase10e`
- `docs/phase10f`

Focus on:

- existing lightweight structure viewer metadata;
- static preview and artifact security model;
- current frontend artifact preview behavior;
- planner routing boundaries;
- browser evidence requirements;
- no-JS/no-external-URL artifact policy;
- static physics closure and fixture-pack replay boundary.

## Required Planning Outputs

Create:

- `docs/phase10f/phase10f7_advanced_viewer_readiness_planning.md`
- `docs/phase10f/phase10f7_viewer_capability_inventory.md`
- `docs/phase10f/phase10f7_renderer_security_matrix.md`
- `docs/phase10f/phase10f7_viewer_artifact_contract_proposal.md`
- `docs/phase10f/phase10f8_next_scope_prompt.md`

## Viewer Capability Inventory

Assess:

- current structure parser support;
- current normalized structure representation;
- current `structure.viewer_scene_metadata` or equivalent metadata;
- current frontend artifact preview constraints;
- current browser evidence method;
- current static chart and static artifact security posture;
- missing pieces for a full viewer.

## Renderer Choice Assessment

Compare planning options without implementing them:

- no renderer / metadata-only continuation;
- static server-generated preview;
- sandboxed in-app renderer;
- future WebGL renderer;
- future Three.js-based renderer.

For each option, record:

- security risk;
- evidence risk;
- artifact-loading model;
- performance risk;
- dependency risk;
- CI/browser screenshot stability.

## Security Boundary

Plan a boundary that covers:

- no artifact JavaScript execution by default;
- no external URLs;
- no arbitrary local file read;
- no notebook/script execution;
- no real LLM;
- renderer isolation if a future renderer is approved;
- explicit artifact schema security flags;
- feature-gated viewer routing.

## Artifact Contract Proposal

Plan, but do not implement, future artifacts such as:

- `viewer_scene.json`
- `viewer_assets_manifest.json`
- `summary.md`
- `recipe.json`

Include:

- schema version proposal;
- source structure metadata;
- atom/site records;
- bond/neighbor policy if any;
- camera/view defaults;
- size caps;
- security flags;
- deterministic ordering.

## Input / Size Caps

Plan caps for:

- max sites;
- max bonds/edges;
- max generated assets;
- max artifact size;
- allowed input formats;
- periodic vs molecular handling;
- fallback behavior for large structures.

## Screenshot / Evidence Model

Plan future evidence:

- API job evidence;
- artifact contract evidence;
- browser screenshot evidence;
- console/network audit;
- no external URL audit;
- no artifact JS execution audit;
- no WebGL/Three.js evidence unless explicitly approved.

## Planner Routing Policy

Plan routing boundaries:

- viewer prompts remain deferred until implementation approval;
- static physics prompts stay routed to `structure.coordination_hist`, `structure.xrd`, and `structure.rdf`;
- phonon, Brillouin-zone, local-environment, and experimental fitting prompts remain out of scope.

## Persistent Updates

Update:

- `persistent/DESIGN_PROGRESS.md`
- `persistent/TASK_BOARD.md`
- `persistent/CHANGELOG.md`
- `persistent/OPEN_QUESTIONS.md`
- `persistent/TOOL_REGISTRY_NOTES.md`
- `persistent/ARCHITECTURE_DECISIONS.md`

Record that this phase is readiness planning only and does not implement full viewer, WebGL, Three.js, or phonon.

## Checks

Run:

```bash
git status --short
git diff --stat
git diff --check
uv lock --check
```

If project policy requires smoke checks, run:

```bash
npm --prefix apps/web run typecheck
uv run python -m pytest -q
```

Do not run a real LLM.

## Secret / Redaction Scan

Scan at least:

- `docs/phase10f`
- `persistent`

Final result must include:

```text
NO_SECRET_PATTERN_HITS
```

## Commit / CI

Commit:

```bash
git add docs/phase10f persistent docs/index.md
git commit -m "Plan advanced structure viewer readiness"
git push origin master
```

Wait for current-HEAD CI:

- unit success;
- frontend success;
- service-backed integration success;
- no-skipped assertion passed;
- git status clean.

Do not fabricate CI.

## PASS / PARTIAL_PASS / FAIL

PASS requires:

- readiness planning docs complete;
- renderer security matrix complete;
- artifact contract proposal complete;
- screenshot/evidence model complete;
- planner routing policy complete;
- persistent updated;
- no full viewer implementation;
- no WebGL / Three.js introduction;
- no phonon implementation;
- checks and CI pass.

PARTIAL_PASS is allowed if CI is externally blocked but local docs checks pass and the blocker is recorded.

FAIL if the phase implements full viewer, introduces WebGL/Three.js, implements phonon, runs notebooks/scripts, calls external APIs, runs a real LLM, changes runtime semantics, or fabricates evidence.
