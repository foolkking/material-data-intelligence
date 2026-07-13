# Phase 10F-26 Export Contract

`ViewerExportRequest` is an exact application-owned object. Unknown keys and
unsupported values are rejected before allocation.

| Field | Policy |
| --- | --- |
| format | `png`, `json`, or `markdown` |
| width/height | integer, 256 through the effective 4096 limit |
| pixelRatio | 1 or 2 |
| background | `light`, `dark`, or `transparent` |
| overlays | booleans for cell, axes, bonds, measurements, inspector summary |
| effective pixels | at most 16,777,216 and 67,108,864 estimated RGBA bytes |

`phase10f26.viewer_export_state.v1` records source scene identity, renderer-local
supercell expansion, camera, clipping, visibility, bounded measurements, an
optional selected-site summary, exact request, no-mutation policy, and inert
security declarations. It is a local view-state download, not a canonical
structure artifact and not an executable AnalysisPlan input.

Filenames are normalized, path separators/control characters are removed,
stems are capped at 80 characters, and suffixes come from a fixed allowlist.
