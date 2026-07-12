# Phase 10F-16 Legacy Guidance Policy

`phase10d1.viewer_scene.v1`, `structure.viewer_scene_metadata`, and
`structure.viewer_export_package` remain retained legacy contracts. Their UI is
JSON-only and states that interactive rendering is unavailable. Users are guided
to rerun the original structure with `structure.viewer_3d`; no source reference is
guessed, no old artifact is modified, and no automatic migration occurs.
