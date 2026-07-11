# Phase 10F-13 Viewer Scene Live Adapter Browser/API Evidence

## Result

PASS.

Phase 10F-13 adds live adapter-backed browser/API evidence for the canonical
`structure.viewer_scene` path. The evidence runner first generates real local
planner/job/runtime artifacts through:

```text
planner_jobs -> persisted AnalysisPlan -> QueueWorkerRuntime.handle_job -> Tool Registry -> StructureViewerSceneAdapter -> artifact metadata listing
```

The runner then opens the existing `PlannerWorkbench` UI in real Chrome and
serves the captured live API responses to the browser. The browser preview is
therefore adapter-generated, not Phase 10F-9 static fixture-backed.

## Commands

```text
uv run python apps/web/test/generate-viewer-scene-live-adapter-evidence.py docs/phase10f/evidence/phase10f13_viewer_scene_live_adapter_browser
node apps/web/test/viewer-scene-live-adapter-browser-evidence.mjs
```

Pass marker:

```text
VIEWER_SCENE_LIVE_ADAPTER_BROWSER_EVIDENCE_PASS
```

## Live Cases

| Case | Runtime status | Evidence |
|---|---:|---|
| `valid_minimal_crystal` | completed | `viewer_scene.json`, manifest, summary, recipe, valid preview |
| `multi_species_crystal` | completed | adapter-generated NaCl scene, species count visible |
| `warning_caps` | completed | real cap/warning behavior visible in JSON-only preview |
| `invalid_multi_structure_rejected` | failed | typed adapter failure before successful viewer artifact generation |

## API Evidence

Evidence is stored under:

```text
docs/phase10f/evidence/phase10f13_viewer_scene_live_adapter_browser/
```

Key files:

| File | Purpose |
|---|---|
| `live_payload.json` | Captured planner/job/runtime/API responses for all live cases |
| `api_transcript.md` | Sanitized request/job/plan/tool/artifact transcript |
| `job_execution_audit.md` | QueueWorkerRuntime and selected-tool audit |
| `artifact_contract_audit.md` | Canonical validator and manifest validator results |
| `artifacts/` | Small copied adapter-generated artifact payloads for review |
| `screenshots/` | Real Chrome screenshots of job, artifact list, previews, and invalid state |

## Browser Evidence

The real Chrome runner captures:

- job completion view
- artifact list view
- canonical `viewer_scene.v1` JSON-only preview
- canonical `viewer_scene_manifest.json` preview
- multi-species adapter-generated preview
- warning/caps adapter-generated preview
- invalid rejected request state
- DOM snapshot
- console snapshot
- network snapshot

No renderer route, renderer bundle, canvas viewer, iframe viewer, WebGL path,
Three.js path, MatterViz path, artifact JavaScript, or external resource request
was added.

## Boundary

The runner reuses the existing preview surface and does not add a production API
route. It uses captured responses from real local planner route functions and
QueueWorkerRuntime execution to drive the browser. Full `structure.viewer_3d`
and renderer implementation remain out of scope.
