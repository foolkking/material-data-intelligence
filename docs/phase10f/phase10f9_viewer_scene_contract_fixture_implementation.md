# Phase 10F-9 Viewer Scene Contract Fixture / Validator Implementation

## 1. Scope

- Implemented inert `viewer_scene.v1` contract fixtures.
- Implemented manifest fixtures and expected validation results.
- Added isolated contract validator checks in `mdi_artifact_core`.
- Added pytest fixture replay tests.
- Did not implement `structure.viewer_3d`, renderer, WebGL, Three.js, planner routing, Tool Registry runtime behavior, or a new adapter.

## 2. Baseline

- Phase 10F-8 commit: `caeb357 Plan viewer scene artifact contract`
- Phase 10F-8 HEAD: `caeb35710546a12358cb841c4b20b7451d23fe5d`
- Branch: `master`
- Git status before: clean

## 3. Fixture Pack

- Path: `docs/phase10f/fixtures/viewer_scene_v1/`
- Artifact kind: `viewer_scene`
- Artifact version: `viewer_scene.v1`
- Schema version under validation: `phase10f8.viewer_scene.v1`
- Fixture status: contract fixtures only, not production runtime artifacts
- Renderer requirement: none
- Browser/API evidence: deferred to a later JSON-only evidence phase

## 4. Validator

The validator is intentionally isolated in `packages/artifact-core/mdi_artifact_core/viewer_scene_contract.py`.

It checks:

- `kind == "viewer_scene"`
- `version == "viewer_scene.v1"`
- required top-level fields
- scene site shape
- finite coordinates
- no `NaN` / `Infinity`
- max sites, bonds, species, cell expansion, and JSON byte caps
- security flags
- no external resource placeholders
- no executable placeholders or script-like fields
- manifest fixture shape

## 5. Tests

Added `tests/test_viewer_scene_contract_fixtures.py`.

The tests verify:

- all scene fixtures are covered by `expected_results.json`
- valid fixtures pass validation
- invalid fixtures fail validation
- expected error and warning codes match
- manifest fixtures are valid and renderer-free
- fixtures contain no real external URLs, JavaScript markers, or HTML markers
- official PASS claims remain false

## 6. Result Boundary

- Contract fixture replay: implemented.
- Fixture-pack PASS: allowed after tests pass.
- Official PASS: not claimed.
- Browser/API evidence: not claimed.
- Renderer evidence: deferred.

## 7. Conclusion

PASS for the contract fixture and validator implementation slice after local validator replay tests. CI status is recorded in the final Phase 10F-9 result.
