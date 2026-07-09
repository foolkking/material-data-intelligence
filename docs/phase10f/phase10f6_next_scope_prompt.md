# Phase 10F-6：Static Physics Fixture Pack Evidence Closure

## Goal

Close Phase 10F fixture-pack replay evidence after Phase 10F-5 verified the constructed static physics fixture pack through platform replay.

## Baseline

- Phase 10F-5 result: PASS
- fixture-pack replay PASS: yes
- official examples PASS claims: none
- replayed tools:
  - `structure.coordination_hist`
  - `structure.xrd`
  - `structure.rdf`

## Scope

1. Close fixture-pack replay evidence.
2. Document the boundary between fixture-pack PASS and official examples PASS.
3. Confirm all `official_pass_claim` fields remain false.
4. Prepare optional reviewer approval path for future `official_derived_manual` cases.
5. Decide whether to move next to Advanced Structure Viewer Readiness Planning or official-derived fixture approval planning.

## Out Of Scope

- Do not implement full `structure.viewer_3d`.
- Do not introduce WebGL or Three.js.
- Do not implement phonon bands or DOS.
- Do not execute notebooks.
- Do not execute external scripts.
- Do not use external APIs.
- Do not run a real LLM.
- Do not implement new adapters.
- Do not modify `structure.coordination_hist`, `structure.xrd`, or `structure.rdf` core semantics.
- Do not claim official examples PASS unless provenance and direct verification gates are satisfied.

## Required Checks

1. Confirm repository, branch, HEAD, and clean status.
2. Read Phase 10F-5 replay evidence and fixture pack expected contracts.
3. Verify `official_pass_claim` and `official_pass_claims` remain false.
4. Verify docs/persistent updates.
5. Run `git diff --check`.
6. Run `uv lock --check`.
7. Run project smoke checks if required.
8. Run secret/redaction scan over `docs/phase10f` and `persistent`.

## PASS Criteria

- Fixture-pack evidence closure documented.
- Official PASS boundary documented.
- No official PASS claim added.
- No new adapter implemented.
- No full viewer, WebGL, Three.js, or phonon implementation.
- Persistent docs updated.
- Checks pass.
- CI passes if a commit is pushed.
