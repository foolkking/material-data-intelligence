# Phase 10F-2: Official Examples Coverage Gap Closure

## Goal

Plan closure for official examples coverage gaps found in Phase 10F-1.

Phase 10F-1 audited the local official examples benchmark pack and found no direct-uploadable official cases for:

- `structure.coordination_hist`
- `structure.xrd`
- `structure.rdf`

Phase 10F-2 should prepare coverage-gap closure without executing notebooks, scripts, external APIs, or new adapter implementation.

## Current Baseline

```text
Phase 10F commit: 186c160 Close static structure physics phase
Phase 10F-1 result: PARTIAL_PASS
Static physics tools complete:
- structure.coordination_hist
- structure.xrd
- structure.rdf
Official direct static physics PASS cases: none
```

## Execution Discipline

1. Do not implement a new adapter.
2. Do not modify `structure.coordination_hist`, `structure.xrd`, or `structure.rdf` core semantics.
3. Do not implement full `structure.viewer_3d`.
4. Do not introduce WebGL or Three.js.
5. Do not implement phonon tools.
6. Do not execute notebooks.
7. Do not execute external scripts.
8. Do not call external APIs.
9. Do not access the internet.
10. Do not install dependencies.
11. Do not run a real LLM.
12. Do not mark mapping-only, notebook-only, script-heavy, external-API, missing-input, or screenshot-only cases as PASS.
13. Do not fabricate evidence.

## Scope

Allowed:

- define a direct static physics official fixture policy;
- define how official-like structure inputs may be curated later;
- map current official structure-related examples to extraction requirements;
- plan artifact comparison tolerances for coordination histogram, XRD, and RDF;
- prepare a future direct-verification prompt if safe fixtures become available;
- update docs and persistent records.

Not allowed:

- full viewer implementation;
- WebGL renderer implementation;
- Three.js introduction;
- phonon implementation;
- notebook extraction execution;
- script execution;
- external API execution.

## Direct-Uploadable Gate

Keep the Phase 10F-1 gate:

- local input artifact present;
- direct platform upload/resource flow;
- no notebook/script/API/network/new dependency;
- bounded file size;
- deterministic expected artifact contract;
- maps exactly to `structure.coordination_hist`, `structure.xrd`, or `structure.rdf`.

## Deliverables

Add docs under:

```text
docs/phase10f/
```

Suggested files:

- `phase10f2_official_examples_coverage_gap_closure.md`
- `phase10f2_static_physics_fixture_gap_matrix.md`
- `phase10f3_next_scope_prompt.md`

## Persistent Updates

Update:

- `persistent/DESIGN_PROGRESS.md`
- `persistent/TASK_BOARD.md`
- `persistent/CHANGELOG.md`
- `persistent/OPEN_QUESTIONS.md`
- `persistent/TOOL_REGISTRY_NOTES.md`
- `persistent/ARCHITECTURE_DECISIONS.md`

Record that Phase 10F-2 is coverage-gap planning only and does not implement full viewer, WebGL, Three.js, phonon, or new adapters.

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
git commit -m "Plan official examples coverage gap closure"
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

- coverage gap matrix complete;
- no unsupported case marked PASS;
- no notebook/script/API execution;
- no new adapter/viewer/WebGL/phonon implementation;
- docs/persistent updated;
- checks and CI passed.

PARTIAL_PASS allows:

- official fixture policy still requiring human approval;
- CI pending after local checks pass.

FAIL if:

- unsupported official cases are marked PASS;
- notebooks/scripts/external APIs are executed;
- full viewer/WebGL/Three.js/phonon is implemented;
- evidence is fabricated.
