# Phase 10F-8 Viewer Scene JSON Contract

## 1. Artifact Identity

| Field | Decision |
|---|---|
| artifact kind | `viewer_scene` |
| artifact filename | `viewer_scene.json` |
| contract version | `viewer_scene.v1` |
| schema version | `phase10f8.viewer_scene.v1` |
| intended consumer | JSON preview first; renderer deferred |
| renderer requirement | `false` for the JSON-only phase |
| execution model | inert data only |

`viewer_scene.json` must not contain embedded JavaScript, HTML, executable callback strings, remote texture references, CDN links, external URLs, notebook payloads, script paths, or renderer bundles.

## 2. Recommended Top-Level Shape

```json
{
  "kind": "viewer_scene",
  "version": "viewer_scene.v1",
  "schema_version": "phase10f8.viewer_scene.v1",
  "source": {},
  "metadata": {},
  "scene": {},
  "validation": {},
  "caps": {},
  "warnings": [],
  "provenance": {},
  "security": {}
}
```

## 3. Field Requirements

| Field | Required | Consumer | Purpose |
|---|---:|---|---|
| `kind` | yes | preview + renderer | Stable artifact-kind discriminator. |
| `version` | yes | preview + renderer | Human-readable contract version. |
| `schema_version` | yes | preview + renderer | Machine-readable schema version. |
| `source` | yes | preview | Resource, parser, file, and origin metadata. |
| `metadata` | yes | preview | Formula, site count, species, title, and summary facts. |
| `scene` | yes | renderer-facing data | Declarative geometry, lattice, optional bonds, and non-authoritative style hints. |
| `validation` | yes | preview + renderer | Producer-side validation result and rejected/truncated field summary. |
| `caps` | yes | preview + renderer | Limits used to produce the scene. |
| `warnings` | yes | preview | Stable warning records; empty array when none. |
| `provenance` | yes | preview | Plan/tool/resource provenance and generation phase. |
| `security` | yes | preview + renderer | No-JS/no-URL/no-renderer-required flags. |

Optional fields must be forward-compatible and ignored by older JSON-only preview consumers unless they weaken security or contradict required fields. Unknown fields must not be executed.

## 4. Scene Geometry Contract

The `scene` object is declarative data only.

```json
{
  "coordinate_basis": "cartesian_angstrom",
  "sites": [
    {
      "index": 0,
      "element": "Si",
      "label": "Si1",
      "xyz": [0.0, 0.0, 0.0],
      "frac": [0.0, 0.0, 0.0],
      "occupancy": 1.0,
      "style": {
        "radius": 1.1,
        "color": "#808080"
      }
    }
  ],
  "lattice": {
    "pbc": [true, true, true],
    "vectors": [[1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]],
    "parameters": {
      "a": 1.0,
      "b": 1.0,
      "c": 1.0,
      "alpha": 90.0,
      "beta": 90.0,
      "gamma": 90.0
    }
  },
  "bonds": [],
  "cell_expansion": [1, 1, 1],
  "style": {
    "representation": "ball_and_stick",
    "background": "transparent"
  }
}
```

## 5. Geometry Rules

- `sites` are ordered by stable site index.
- `element`, `label`, `xyz`, and `index` are required for each site.
- `frac` is optional but recommended when lattice vectors exist.
- `coordinate_basis` must be explicit. The v1 renderer-facing basis is `cartesian_angstrom`; fractional coordinates may be included as supplementary data.
- `lattice.vectors` must be finite numeric 3x3 vectors when a periodic structure is represented.
- `bonds` are optional. If present, they must be generated upstream, capped, sorted deterministically, and treated as advisory by a future renderer.
- `cell_expansion` is metadata only in v1 and must not trigger renderer-side supercell expansion beyond approved caps.
- `style` and per-site style hints are non-authoritative. A future renderer may ignore them.

## 6. Declarative-Only Boundary

The artifact must never contain:

- executable functions;
- callback names to invoke;
- inline HTML;
- script tags;
- event-handler fields;
- dynamic import strings;
- local filesystem paths for renderer loading;
- remote textures or model URLs;
- compressed executable payloads.

A renderer must treat every field as data and must not evaluate or dereference artifact-provided strings.
