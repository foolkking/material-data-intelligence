# Phase 10F-5: Static Physics Fixture Pack Replay Verification

## Goal

Replay the constructed Phase 10F-4 static physics fixture pack through the existing platform/job flow and validate generated artifacts against candidate expected contracts.

Target fixture pack:

```text
docs/phase10f/static_physics_fixture_pack/
```

Target tools:

- `structure.coordination_hist`
- `structure.xrd`
- `structure.rdf`

This phase may record fixture-pack PASS / PARTIAL_PASS / REGRESSION_PASS results only. Do not claim official PASS unless provenance is `official_direct` or approved `official_derived_manual`.

## 1. Preconditions

Run:

```bash
cd "E:\1project\Material Data Intelligence"
git status --short
git log --oneline -65
git branch --show-current
git tag --points-at HEAD
```

Confirm:

1. branch is `master`.
2. git status is clean.
3. HEAD contains Phase 10F-4 fixture-pack construction.
4. `docs/phase10f/static_physics_fixture_pack/manifest.json` exists.
5. all three case directories exist.
6. no official static physics PASS claim exists before replay.

Stop if git status is not clean.

## 2. Read Required Docs

Read:

- `README.md`
- `AGENTS.md`
- `MASTER_PROMPT.md`
- `persistent/PROJECT_BRIEF.md`
- `persistent/DESIGN_PROGRESS.md`
- `persistent/TASK_BOARD.md`
- `persistent/ARCHITECTURE_DECISIONS.md`
- `docs/index.md`
- `docs/13_SHARED_SCHEMA_SPEC.md`
- `docs/phase10f/phase10f4_static_physics_fixture_pack_construction.md`
- `docs/phase10f/static_physics_fixture_pack/README.md`
- `docs/phase10f/static_physics_fixture_pack/manifest.json`
- all case `input_manifest.json`, `expected_contract.json`, and `provenance.json` files.

## 3. Manifest Validation

Validate:

- manifest JSON parses.
- expected contracts parse.
- all paths referenced by manifest exist.
- all `official_pass_claim` values are false before replay.
- provenance labels are valid.
- input files are below size limits.
- fixture pack contains no notebooks, scripts, binary archives, screenshots, or external URL dependencies.

## 4. Replay Protocol

For each case:

1. Upload the input through the existing platform resource flow.
2. Submit a deterministic planner/job request for the target tool.
3. Do not use a real LLM.
4. Verify selected `tool_id`.
5. Wait for job completion.
6. Download generated artifacts.
7. Validate expected artifact filenames.
8. Validate artifact schema versions and security flags.
9. Apply exact checks.
10. Generate or compare numeric checks according to the expected contract.
11. Record warnings and limits.
12. Store sanitized API/artifact transcript evidence.

## 5. Result Labels

Allowed labels:

- `REGRESSION_PASS`: internal or official-like fixture replay and comparison succeeded.
- `PARTIAL_PASS`: replay succeeded but numeric coverage remains partial.
- `FAILED`: replay or comparison failed.
- `MAPPING_ONLY`, `EXTRACTION_REQUIRED`, or `FUTURE_SCOPE` where a case is not directly executable.

Do not use official `PASS` for `internal_regression` or `official_like_curated` cases.

## 6. Security Rules

Do not:

- execute notebooks;
- execute external scripts;
- run benchmark extraction scripts;
- access external APIs;
- use real LLM;
- execute artifact JavaScript;
- load external URLs;
- invoke WebGL/canvas 3D viewer;
- install dependencies;
- implement a new adapter;
- modify runtime main semantics.

## 7. Docs / Persistent Updates

Update:

- Phase 10F-5 replay verification docs under `docs/phase10f/`.
- fixture-pack evidence docs if replay succeeds.
- `persistent/DESIGN_PROGRESS.md`
- `persistent/TASK_BOARD.md`
- `persistent/CHANGELOG.md`
- `persistent/OPEN_QUESTIONS.md`
- `persistent/TOOL_REGISTRY_NOTES.md`
- `persistent/ARCHITECTURE_DECISIONS.md`

## 8. Checks / CI

Run at minimum:

```bash
git status --short
git diff --stat
git diff --check
uv lock --check
npm --prefix apps/web run typecheck
uv run python -m pytest -q
```

If replay uses service-backed integration, record that mode and ensure no real LLM is called.

## 9. PASS / PARTIAL_PASS / FAIL

### PASS

All fixture cases replay successfully through the platform flow, artifacts match candidate contracts, security checks pass, docs/persistent are updated, CI passes, and git status is clean. Results are fixture-pack regression results only unless official provenance eligibility exists.

### PARTIAL_PASS

Allowed if at least one case replays successfully but numeric expected values remain partial, or CI is pending while local checks pass and the status is recorded honestly.

### FAIL

Any official PASS claim without eligible provenance and replay, notebook/script execution, external API use, real LLM use, new adapter implementation, runtime semantic change, full viewer/WebGL/Three.js/phonon implementation, fabricated evidence, failed checks, or dirty final git status.

## 10. Next Phase Recommendation

After successful fixture replay, recommend a single next scope:

- official-derived fixture approval planning, if official provenance can be established; or
- advanced structure viewer readiness planning.

Do not directly enter full `structure.viewer_3d`, WebGL, or phonon implementation.

