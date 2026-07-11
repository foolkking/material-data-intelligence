# Phase 10F-13 Viewer Schema Compatibility Audit

## Result

DOCUMENTED.

Phase 10F-13 does not migrate, delete, or rewrite old Phase 10D viewer tools.
It documents coexistence between old static viewer metadata/export schemas and
the new canonical `viewer_scene.v1` adapter path.

## Existing Tools

| Tool | Status | Schema |
|---|---|---|
| `structure.viewer_scene_metadata` | unchanged | `phase10d1.viewer_scene.v1` |
| `structure.viewer_export_package` | unchanged | `phase10d1.viewer_assets_manifest.v1` |
| `structure.viewer_scene` | canonical adapter | `phase10f8.viewer_scene.v1` |

## Routing Separation

The compatibility audit records:

- explicit canonical viewer-scene prompts route to `structure.viewer_scene`
- old metadata prompts route to `structure.viewer_scene_metadata`
- old export package prompts route to `structure.viewer_export_package`
- XRD prompts route to `structure.xrd`
- RDF prompts route to `structure.rdf`
- coordination prompts route to `structure.coordination_hist`
- full renderer / Three.js prompts do not route to `structure.viewer_scene`
- phonon prompts do not route to `structure.viewer_scene`

## Preview Separation

The existing preview surface can display old Phase 10D static viewer metadata,
but it recognizes canonical `viewer_scene.v1` only when the payload has:

```text
kind: viewer_scene
version: viewer_scene.v1
schema_version: phase10f8.viewer_scene.v1
```

No old artifact is relabeled as canonical. No automatic migration is performed.

## Remaining Compatibility Debt

A future reviewer must decide whether Phase 10D viewer metadata/export tools
should be deprecated, migrated, or retained as legacy static export paths. That
decision is intentionally outside Phase 10F-13.
