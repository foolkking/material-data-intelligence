# Phase 10F-10 Viewer Scene JSON-only Preview Surface Implementation

## 1. Scope

- Implemented: JSON-only preview support for `viewer_scene.v1` artifacts in the existing Results/export artifact preview surface.
- Implemented: JSON-only manifest preview support for Phase 10F-9 `phase10f9.viewer_scene_manifest.v1` manifest fixtures.
- Implemented: stable frontend selectors for fixture-backed evidence of kind, version, schema version, validation state, errors, warnings, caps, scene summary, and manifest metadata.
- Not implemented: `structure.viewer_3d`, WebGL, Three.js, renderer bundle, 3D viewer component, new adapter, planner routing, Tool Registry runtime behavior, or production runtime route.

## 2. Baseline

- Phase 10F-9 commit: `ae69696 Add viewer scene contract fixtures`
- Phase 10F-9 HEAD: `ae6969675e3c9b6248f4ad8f4a2287d38a694046`
- Branch before edits: `master`
- Git status before Phase 10F-10 edits: clean

## 3. Implementation

Phase 10F-10 extends the existing `ViewerStaticPreviewPanel` path in `apps/web/app/components/PlannerWorkbench.tsx`.

The preview recognizes:

- `kind == "viewer_scene"`
- `version == "viewer_scene.v1"`
- `schema_version == "phase10f8.viewer_scene.v1"`
- `schema_version == "phase10f9.viewer_scene_manifest.v1"` for manifest fixtures

The surface displays inert JSON-derived summary fields only:

- artifact kind
- artifact version
- schema version
- validation state
- error codes
- warning codes
- site count
- bond count
- species count
- coordinate basis
- lattice presence
- manifest preview mode
- renderer required
- executable assets
- external resources

## 4. Evidence Selectors

Stable selectors added for tests and future evidence:

- `viewer-scene-v1-preview`
- `viewer-scene-kind`
- `viewer-scene-version`
- `viewer-scene-schema-version`
- `viewer-scene-summary`
- `viewer-scene-validation-state`
- `viewer-scene-error-codes`
- `viewer-scene-warning-codes`
- `viewer-manifest-json-only-preview`
- `viewer-manifest-preview-mode`
- `viewer-manifest-renderer-required`
- `viewer-manifest-executable-assets`
- `viewer-manifest-external-resources`

## 5. Result Boundary

This is a JSON-only preview surface. It does not render 3D geometry and does not execute artifact content. It consumes the artifact as data and displays a static summary plus raw JSON details through the existing artifact preview model.

## 6. Conclusion

PASS. Phase 10F-10 implements a non-renderer preview surface for `viewer_scene.v1` contract fixtures without adding runtime routes, adapters, planner routing, WebGL, Three.js, or renderer code.
