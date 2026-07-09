# Phase 10F-7 Viewer Artifact Contract Proposal

## 1. Scope

This document proposes a future inert artifact contract for advanced structure viewer work. It does not implement `structure.viewer_3d`, a renderer, WebGL, Three.js, or frontend 3D runtime.

## 2. Existing Baseline

Phase 10D already provides static `viewer_scene.json` metadata using `phase10d1.viewer_scene.v1` for `structure.viewer_scene_metadata` and related export-package evidence. Phase 10F-8 should reconcile that proven static scene shape with a future viewer-facing contract before any renderer work.

## 3. Future Artifact Names

- `viewer_scene.json`
- `viewer_summary.md`
- `viewer_recipe.json`

## 4. Proposed `viewer_scene.json` Shape

```json
{
  "schema_version": "phase10f8.viewer_scene.v1",
  "tool_id": "structure.viewer_3d",
  "source": {
    "resource_id": "...",
    "resource_type": "...",
    "filename": "...",
    "parser": "..."
  },
  "structure": {
    "formula": "...",
    "site_count": 0,
    "species": [],
    "pbc": [true, true, true],
    "lattice": {
      "a": 0.0,
      "b": 0.0,
      "c": 0.0,
      "alpha": 90.0,
      "beta": 90.0,
      "gamma": 90.0
    }
  },
  "scene": {
    "coordinate_system": "cartesian_angstrom",
    "sites": [
      {
        "index": 0,
        "element": "Si",
        "label": "Si1",
        "xyz": [0.0, 0.0, 0.0],
        "radius": 1.1,
        "color": "#808080"
      }
    ],
    "bonds": [],
    "unit_cell": {
      "vectors": [[1, 0, 0], [0, 1, 0], [0, 0, 1]],
      "edges": []
    },
    "style": {
      "representation": "ball_and_stick",
      "background": "transparent"
    }
  },
  "limits": {
    "max_sites": 256,
    "max_bonds": 2048,
    "truncated": false
  },
  "warnings": [],
  "security": {
    "contains_javascript": false,
    "external_urls": [],
    "external_urls_allowed": false,
    "renderer_required": false
  }
}
```

## 5. Contract Policy

1. `viewer_scene.json` is inert JSON.
2. It must not embed JavaScript.
3. It must not reference external textures.
4. It must not reference a CDN.
5. It must not contain executable callbacks.
6. It must not request remote model loading.
7. It must not be an HTML artifact.
8. It must not require notebook execution.
9. It must not require script extraction.
10. Renderer code is separate from the artifact.
11. The artifact can be previewed as static JSON before any renderer exists.
12. A future renderer must treat artifact contents as data only.

## 6. Required Metadata

- schema version
- tool id
- source summary
- structure formula, site count, species, PBC, and lattice
- deterministic site ordering
- deterministic bond ordering if bonds are included
- explicit limits and truncation flags
- stable warnings
- security flags with `contains_javascript: false`, `external_urls: []`, and `external_urls_allowed: false`

## 7. Phase 10F-8 Work

Phase 10F-8 should finalize this artifact contract, decide whether it extends or supersedes the Phase 10D scene metadata schema, define strict params, and add contract tests without implementing a renderer.
