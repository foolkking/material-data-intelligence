# Phase 10F-15 Legacy Schema Policy

- `phase10d1.viewer_scene.v1`: `RETAINED_LEGACY`, JSON-only, no canonical rendering.
- `structure.viewer_scene_metadata`: `DIRECT_EXECUTION_ONLY` for explicit legacy intent; ordinary viewer prompts do not select it.
- `structure.viewer_export_package`: `DIRECT_EXECUTION_ONLY` for explicit legacy package intent.
- Automatic migration: none.
- Removal: deferred to a separately reviewed migration window.
- UI: displays `Legacy viewer scene contract` and recommends a canonical rerun.

Old artifacts are never relabeled as `viewer_scene.v1`, and the frontend canonical gate remains the renderer source of truth.
