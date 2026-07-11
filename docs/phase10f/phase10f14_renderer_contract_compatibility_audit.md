# Phase 10F-14 Renderer Contract Compatibility Audit

- canonical schema remains `phase10f8.viewer_scene.v1` / `viewer_scene.v1`.
- manifest remains `phase10f9.viewer_scene_manifest.v1`.
- old `phase10d1.viewer_scene.v1` artifacts remain JSON-only and are not mapped.
- `structure.viewer_scene_metadata` and `structure.viewer_export_package` are unchanged.
- `structure.viewer_scene` remains the canonical producer.
- full 3D prompts and formal `structure.viewer_3d` registration remain unchanged and unsupported.
- no migration or deprecation occurred.
