# Phase 10F-9 Viewer Scene Validator Result

## Validator Location

- `packages/artifact-core/mdi_artifact_core/viewer_scene_contract.py`

## Test Location

- `tests/test_viewer_scene_contract_fixtures.py`

## Implemented Checks

- Identity: `kind`, `version`, `schema_version`
- Required fields: `source`, `metadata`, `scene`, `validation`, `caps`, `warnings`, `provenance`, `security`
- Geometry: sites, species, optional bonds, lattice vectors, optional cell expansion
- Numeric safety: finite coordinates only, no `NaN`, no `Infinity`
- Caps: sites, bonds, species, cell expansion, JSON bytes
- Security: no artifact JavaScript, no external URLs, no renderer requirement, no HTML allowance
- Manifest: JSON-only preview mode, no executable assets, no external resources

## Expected Result Comparison

`docs/phase10f/fixtures/viewer_scene_v1/expected_results.json` is the source of truth for fixture replay expectations. Tests compare validator output with expected validity, error codes, and warning codes.

## Boundary

The validator does not implement a renderer, planner route, Tool Registry entry, runtime API endpoint, or `structure.viewer_3d` adapter.
