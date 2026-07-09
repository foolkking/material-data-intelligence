# Phase 10F-9 Viewer Scene Manifest Fixtures

## Manifest Fixture Contract

Manifest fixtures use `phase10f9.viewer_scene_manifest.v1` and are inert JSON files. Each manifest records:

- `artifact_id`
- `artifact_kind`
- `artifact_version`
- `fixture_source`
- `expected_validation_state`
- `expected_errors`
- `expected_warnings`
- `expected_caps`
- `preview_mode`
- `renderer_required`
- `executable_assets`
- `external_resources`

## Implemented Manifests

- `manifest_valid_minimal_crystal.viewer_scene.v1.json`
- `manifest_valid_multi_species_crystal.viewer_scene.v1.json`
- `manifest_valid_optional_bonds.viewer_scene.v1.json`
- `manifest_invalid_nan_coordinate.viewer_scene.v1.json`
- `manifest_invalid_external_resource_reference.viewer_scene.v1.json`
- `manifest_invalid_executable_field.viewer_scene.v1.json`
- `manifest_invalid_over_cap_sites.viewer_scene.v1.json`

## Security Boundary

- `preview_mode == "json_only"`
- `renderer_required == false`
- `executable_assets == "none"`
- `external_resources == "none"`

No manifest is used by runtime routing in this phase.
