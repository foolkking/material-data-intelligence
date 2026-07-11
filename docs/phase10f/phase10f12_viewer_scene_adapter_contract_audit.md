# Phase 10F-12 Viewer Scene Adapter Contract Audit

## Existing Tools

Pre-existing viewer-related tools remain unchanged:

| Tool | Schema | Role |
|---|---|---|
| `structure.viewer_scene_metadata` | `phase10d1.viewer_scene.v1` | Historical static viewer metadata |
| `structure.viewer_export_package` | `phase10d1.viewer_assets_manifest.v1` | Historical static export package |
| `structure.structure_3d` | Plotly structure artifacts | Existing static/interactive Plotly path |
| `structure.viewer_3d` | MatterViz HTML path | Historical full viewer path, not approved by this phase |

## Strategy

Phase 10F-12 adds one new minimal adapter: `structure.viewer_scene`.

The old Phase 10D tools are not upgraded in place because changing their schema
would silently break existing evidence and compatibility. The new tool owns the
canonical Phase 10F contract:

- `kind: viewer_scene`
- `version: viewer_scene.v1`
- `schema_version: phase10f8.viewer_scene.v1`
- manifest `schema_version: phase10f9.viewer_scene_manifest.v1`

## Contract Fit

The adapter emits the required top-level fields:

- `kind`
- `version`
- `schema_version`
- `source`
- `metadata`
- `scene`
- `validation`
- `caps`
- `warnings`
- `provenance`
- `security`

The scene uses canonical `cartesian_angstrom` coordinates with optional
fractional coordinates, finite lattice vectors, declarative sites, optional
bounded bonds, and non-authoritative styling hints.

## Duplicate Tool Risk

The duplicate-tool risk is resolved by keeping old tools under their existing
Phase 10D IDs and adding only one new canonical Phase 10F ID. No semantically
overlapping second `viewer_scene.v1` adapter is registered.

## Deferred Scope

Renderer handoff remains partial. Renderer implementation, full
`structure.viewer_3d`, WebGL, Three.js, MatterViz renderer bundles, atom
picking, camera controls, trajectory animation, Brillouin-zone 3D, and phonon
visualization remain out of scope.
