# Phase 10F-26 Export Manifest

`phase10f26.viewer_export_manifest.v1` lists exactly three ordered artifacts:

1. `viewer.png` (`image/png`)
2. `viewer_export_state.json` (`application/json`)
3. `viewer_export_summary.md` (`text/markdown`)

Each entry includes byte size and lowercase SHA-256. The browser computes hashes
with Web Crypto over local Blobs. The manifest declares `renderer_included` and
`javascript_included` false, `external_assets` empty, and deterministic order.

The manifest is downloaded separately and does not embed file bytes, scripts,
URLs, renderer modules, secrets, filesystem paths, or callbacks.
