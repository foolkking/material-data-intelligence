# Phase 10F-27 structure.viewer_3d Tool Contract

## Input

- One normalized periodic `Structure` object.
- Strict parameters: bounded bond generation, coordinate fields, site/bond
  caps, one-cell adapter output, and application-owned style/camera presets.
- `additionalProperties: false`; artifact data cannot select modules,
  callbacks, URLs, shaders, or renderer code.

## Output

- `viewer_scene.json`: `phase10f18.viewer_scene.v2`.
- `viewer_scene_manifest.json`: `phase10f19.viewer_assets_manifest.v2`.
- `summary.md` and `recipe.json`.
- Artifact types: `structure_json`, `table_json`, `summary_md`, `recipe_json`.

Backend success means validated inert artifacts were persisted. Browser
renderer support is a separate client state and cannot fail the backend job.
No renderer bundle, WebGL code, JavaScript, texture, URL, or external asset is
embedded in these artifacts.
