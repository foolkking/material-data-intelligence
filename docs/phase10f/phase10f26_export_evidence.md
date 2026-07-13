# Phase 10F-26 Export Evidence

Command:

```bash
node apps/web/test/viewer-scene-scientific-export-browser-evidence.mjs
```

The runner uses the existing live adapter/job/artifact harness and local Next.js
application. Chromium, Firefox, and WebKit each produced valid 800 x 600 PNGs.
Chromium additionally covered transparent and dark output, a 2400 x 1800 high-
DPI PNG, clipping, 2 x 1 x 1 supercell, measurement overlay/state, JSON,
Markdown, manifest hash replay, ten repeated exports, mobile controls, console,
and network audits.

Evidence is in
`docs/phase10f/evidence/phase10f26_scientific_export/`. Required markers:

- `VIEWER_SCENE_SCIENTIFIC_EXPORT_BROWSER_EVIDENCE_PASS`
- `VIEWER_SCENE_HIGH_DPI_EXPORT_EVIDENCE_PASS`
- `VIEWER_SCENE_TRANSPARENT_EXPORT_EVIDENCE_PASS`
- `VIEWER_SCENE_EXPORT_ARTIFACT_EVIDENCE_PASS`
- `VIEWER_SCENE_EXPORT_MOBILE_CROSS_BROWSER_EVIDENCE_PASS`
- `NO_EXTERNAL_NETWORK_REQUESTS`
