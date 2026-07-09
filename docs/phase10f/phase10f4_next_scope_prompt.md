# Phase 10F-4: Static Physics Direct-Uploadable Fixture Pack Construction

## Goal

Construct a small direct-uploadable static physics fixture pack from the Phase 10F-3 planning templates.

Target tools:

- `structure.coordination_hist`
- `structure.xrd`
- `structure.rdf`

This phase may add small text fixtures, manifest files, and expected-contract files only after applying the provenance and size gates. It does not run official PASS verification unless explicitly approved.

## Baseline

```text
Phase 10F-1 status: PARTIAL_PASS
Phase 10F-2 status: PASS
Phase 10F-3 scope: fixture-pack planning
Official static physics direct PASS claims: none
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
9. Do not claim official PASS unless the user explicitly expands the scope to replay verification and the case satisfies official provenance.
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
git log --oneline -60
git branch --show-current
git tag --points-at HEAD
```

Confirm:

- branch is `master`;
- git status is clean;
- HEAD is at or after Phase 10F-3;
- Phase 10F-3 docs exist;
- no official static physics PASS claim exists.

Stop if the working tree is dirty.

## Required Reading

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
- `docs/phase10f/phase10f3_static_physics_fixture_pack_planning.md`
- `docs/phase10f/phase10f3_fixture_candidate_matrix.md`
- `docs/phase10f/phase10f3_fixture_provenance_policy.md`
- `docs/phase10f/phase10f3_expected_contract_templates.md`
- `docs/phase10f/phase10f3_numeric_tolerance_policy.md`
- `docs/phase10f/phase10f3_fixture_replay_protocol.md`

## Fixture Size Limits

- Coordination histogram fixture: maximum 64 sites.
- XRD fixture: maximum 128 sites.
- RDF fixture: maximum 128 sites.
- Prefer CIF, POSCAR/CONTCAR, or supported Structure JSON.
- Do not add large benchmark files.
- Do not add binary screenshots as fixture-pack evidence in this construction phase.

## Provenance Gate

Every fixture must declare one label:

- `official_direct`
- `official_derived_manual`
- `official_like_curated`
- `internal_regression`
- `mapping_only`
- `future_scope`
- `unsupported`
- `unknown`

Only `official_direct` and reviewer-approved `official_derived_manual` can become official PASS after a separate replay verification phase.

## Expected Contract Authoring

Create expected contracts with:

- exact schema/tool/artifact/security assertions;
- tolerance-bounded numeric assertions;
- metadata-only fields;
- allowed-to-vary fields;
- no-PASS-claim status.

Do not overfit local job ids, artifact ids, timestamps, storage keys, or regenerated content hashes.

## No PASS Claim Policy

This phase constructs the pack. It does not mark cases official PASS unless the user explicitly changes the scope to include replay verification.

`official_like_curated` and `internal_regression` cases are never official PASS by themselves.

## Docs / Persistent Updates

Update:

- fixture-pack docs under `docs/phase10f/`;
- `persistent/DESIGN_PROGRESS.md`;
- `persistent/TASK_BOARD.md`;
- `persistent/CHANGELOG.md`;
- `persistent/OPEN_QUESTIONS.md`;
- `persistent/TOOL_REGISTRY_NOTES.md`;
- `persistent/ARCHITECTURE_DECISIONS.md`.

## Checks

Run:

```bash
git status --short
git diff --stat
git diff --check
uv lock --check
npm --prefix apps/web run typecheck
uv run python -m pytest -q
```

Run a secret/redaction scan over `docs/phase10f` and `persistent`, and record `NO_SECRET_PATTERN_HITS`.

## Commit / CI

Commit:

```bash
git add docs/phase10f persistent
git commit -m "Construct static physics fixture pack"
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

- approved fixture pack layout constructed;
- small fixture inputs only;
- expected contracts present;
- provenance labels present;
- no official PASS claim unless explicitly replayed and verified;
- no notebooks/scripts/APIs/network/real LLM/new dependencies;
- no new adapter/full viewer/WebGL/Three.js/phonon;
- docs/persistent updated;
- checks and CI passed.

PARTIAL_PASS allows:

- official-derived provenance still requiring reviewer approval;
- some candidates remaining template-only;
- CI pending after local checks pass.

FAIL if:

- unsupported or unexecuted cases are marked official PASS;
- notebooks/scripts/external APIs are executed;
- a new adapter, full viewer, WebGL, Three.js, or phonon is implemented;
- evidence is fabricated.

## Next Phase Recommendation

If construction succeeds, recommend:

```text
Phase 10F-5: Static Physics Fixture Pack Replay Verification
```

That phase should replay the pack through the platform and compare artifacts to expected contracts. Do not directly enter full `structure.viewer_3d` / WebGL / phonon.
