# Phase 10F-8 Viewer Scene Manifest Contract

## 1. Scope

This document plans the future manifest contract for a viewer-scene artifact family. It does not create or rename artifacts and does not modify the Phase 10D `viewer_assets_manifest.json` implementation.

## 2. Manifest Identity

| Field | Decision |
|---|---|
| contract name | viewer scene manifest |
| recommended artifact filename | `viewer_scene_manifest.json` for future contract phases |
| compatible existing artifact | `viewer_assets_manifest.json` from Phase 10D export package evidence |
| schema version | `phase10f8.viewer_scene_manifest.v1` |
| renderer included | `false` |
| renderer required | `false` |

The manifest is an inert JSON index for scene-related artifacts. It is not a renderer descriptor that can load scripts or remote assets.

## 3. Recommended Shape

```json
{
  "kind": "viewer_scene_manifest",
  "version": "viewer_scene_manifest.v1",
  "schema_version": "phase10f8.viewer_scene_manifest.v1",
  "entry_artifact": "viewer_scene.json",
  "artifacts": [
    {
      "path": "viewer_scene.json",
      "kind": "viewer_scene",
      "media_type": "application/json",
      "required": true,
      "sha256": null,
      "size_bytes": null
    }
  ],
  "renderer": {
    "included": false,
    "required": false,
    "renderer_type": "none",
    "future_renderer_contract": "requires_explicit_approval"
  },
  "caps": {},
  "warnings": [],
  "provenance": {},
  "security": {
    "contains_javascript": false,
    "external_urls": [],
    "external_urls_allowed": false,
    "renderer_required": false,
    "remote_assets_allowed": false
  }
}
```

## 4. Required Fields

| Field | Required | Purpose |
|---|---:|---|
| `kind` | yes | Manifest-kind discriminator. |
| `version` | yes | Contract version. |
| `schema_version` | yes | Machine-readable schema version. |
| `entry_artifact` | yes | Primary scene artifact. |
| `artifacts` | yes | Inert artifact index. |
| `renderer` | yes | Explicit renderer absence and future-scope status. |
| `caps` | yes | Limits inherited by the artifact family. |
| `warnings` | yes | Manifest-level warnings. |
| `provenance` | yes | Generation and source metadata. |
| `security` | yes | No-JS/no-URL/no-renderer flags. |

## 5. Manifest Rules

- `artifacts[].path` must be a relative artifact name, not an absolute filesystem path and not an external URL.
- `artifacts[].media_type` must be a data media type such as `application/json` or `text/markdown`.
- `renderer.included` and `renderer.required` must remain `false` in the JSON-only phase.
- The manifest must not contain CDN links, renderer bundle names, dynamic imports, remote textures, iframe sources, or HTML templates.
- `sha256` and `size_bytes` are optional until an implementation phase fixes artifact generation.
- Existing `viewer_assets_manifest.json` can be mapped into this contract in a later compatibility phase; Phase 10F-8 only plans that bridge.
