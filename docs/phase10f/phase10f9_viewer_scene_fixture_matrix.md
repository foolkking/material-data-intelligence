# Phase 10F-9 Viewer Scene Fixture Matrix

| Fixture | Type | Expected Validity | Expected Errors | Expected Warnings | Renderer |
|---|---|---:|---|---|---|
| `valid_minimal_crystal.viewer_scene.v1.json` | valid | true | none | none | deferred |
| `valid_multi_species_crystal.viewer_scene.v1.json` | valid | true | none | none | deferred |
| `valid_optional_bonds.viewer_scene.v1.json` | valid | true | none | none | deferred |
| `valid_warning_caps.viewer_scene.v1.json` | warning/caps | true | none | `VIEWER_SCENE_CAP_NEAR_LIMIT` | deferred |
| `invalid_nan_coordinate.viewer_scene.v1.json` | invalid | false | `VIEWER_SCENE_COORDINATE_NON_FINITE` | none | not applicable |
| `invalid_infinity_coordinate.viewer_scene.v1.json` | invalid | false | `VIEWER_SCENE_COORDINATE_NON_FINITE` | none | not applicable |
| `invalid_external_resource_reference.viewer_scene.v1.json` | invalid | false | `VIEWER_SCENE_EXTERNAL_RESOURCE_REFERENCE` | none | not applicable |
| `invalid_executable_field.viewer_scene.v1.json` | invalid | false | `VIEWER_SCENE_EXECUTABLE_FIELD` | none | not applicable |
| `invalid_over_cap_sites.viewer_scene.v1.json` | invalid | false | `VIEWER_SCENE_SITE_LIMIT_EXCEEDED` | none | not applicable |
| `invalid_over_cap_bonds.viewer_scene.v1.json` | invalid | false | `VIEWER_SCENE_BOND_LIMIT_EXCEEDED` | none | not applicable |
| `invalid_schema_version.viewer_scene.v1.json` | invalid | false | `VIEWER_SCENE_SCHEMA_VERSION_INVALID` | none | not applicable |

All fixtures are inert JSON files and are not production runtime artifacts.
