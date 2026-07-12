# Phase 10F-15 Browser/API Evidence

Evidence lives under `docs/phase10f/evidence/phase10f15_production_minimal_structure_viewer/`.

The generator drives `planner_jobs`, persisted `AnalysisPlan`, `QueueWorkerRuntime`, registry lookup, formal `structure.viewer_3d`, artifact storage/listing, canonical validators, frontend API retrieval, validation, mapping, and rendering.

Captured cases include minimal Si, multi-species NaCl, warning/caps, bonds disabled, invalid request, near-cap rendering, legacy schema, chunk failure, unsupported capability, context loss, desktop Chromium/Firefox/WebKit, and mobile resize. Screenshots are real browser captures. Console errors and external requests are zero in the final matrix.

Replay: `node apps/web/test/viewer-scene-production-browser-evidence.mjs`.
