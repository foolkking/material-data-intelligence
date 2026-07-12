# Viewer Schema Compatibility Matrix

| Contract | Status | Preview | Renderer | Periodic topology | New production output |
| --- | --- | --- | --- | --- | --- |
| `phase10d1.viewer_scene.v1` | deprecated read-only | JSON only | no | no | forbidden |
| `phase10f8.viewer_scene.v1` | supported legacy same-cell | JSON or existing same-cell renderer | same-cell only | no | forbidden |
| `phase10f18.viewer_scene.v2` | current | JSON or renderer | yes | yes | default |

Manifest v1 contracts remain readable and non-executable. The current
`phase10f19.viewer_assets_manifest.v2` must pair with v2, declares periodic
topology, and declares no included renderer or WebGL asset.

The source of truth is `VIEWER_SCHEMA_COMPATIBILITY` and
`VIEWER_MANIFEST_COMPATIBILITY`; frontend policy mirrors these fixed values.
