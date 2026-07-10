# Phase 10F-11 Viewer Scene Real Browser Evidence

## 1. Scope
- Added real browser evidence for the existing `viewer_scene.v1` JSON-only preview surface.
- Covered fixture-backed scene preview, manifest preview, validation state, caps/warnings, and scene summary.
- Did not implement `structure.viewer_3d`, a renderer, WebGL, Three.js, planner routing, a new adapter, or a production runtime route.

## 2. Baseline
- Phase 10F-10 commit: `f11c739 Add viewer scene JSON preview evidence`
- Phase 10F-10 HEAD: `f11c73972bee27b9c380214de6b3d8d2df5cf77d`
- Branch: `master`
- Git status before: clean

## 3. Browser Evidence Command
```text
node apps/web/test/viewer-scene-browser-evidence.mjs
```

The command starts the existing Next.js app on a loopback dev server, drives it with Playwright and system Chrome, provides fixture-backed mock API responses, and captures browser-rendered screenshots and DOM/network evidence. It does not add a production route.

## 4. Evidence Artifacts
- `docs/phase10f/evidence/phase10f11_viewer_scene_real_browser/command_log.md`
- `docs/phase10f/evidence/phase10f11_viewer_scene_real_browser/dom_snapshot.json`
- `docs/phase10f/evidence/phase10f11_viewer_scene_real_browser/network_audit.json`
- `docs/phase10f/evidence/phase10f11_viewer_scene_real_browser/screenshots/01_valid_minimal_crystal.png`
- `docs/phase10f/evidence/phase10f11_viewer_scene_real_browser/screenshots/02_valid_warning_caps.png`
- `docs/phase10f/evidence/phase10f11_viewer_scene_real_browser/screenshots/03_invalid_external_resource_placeholder.png`
- `docs/phase10f/evidence/phase10f11_viewer_scene_real_browser/screenshots/04_invalid_executable_placeholder.png`
- `docs/phase10f/evidence/phase10f11_viewer_scene_real_browser/screenshots/05_invalid_schema_version.png`

## 5. Coverage
| Case | Real Browser Preview | Manifest Preview | Validation Evidence | Screenshot |
|---|---:|---:|---|---|
| `valid_minimal_crystal` | yes | yes | `passed` | `01_valid_minimal_crystal.png` |
| `valid_warning_caps` | yes | yes | `passed`, `VIEWER_SCENE_CAP_NEAR_LIMIT` | `02_valid_warning_caps.png` |
| `invalid_external_resource_placeholder` | yes | yes | `expected_failure`, `VIEWER_SCENE_EXTERNAL_RESOURCE_REFERENCE` | `03_invalid_external_resource_placeholder.png` |
| `invalid_executable_placeholder` | yes | yes | `expected_failure`, `VIEWER_SCENE_EXECUTABLE_FIELD` | `04_invalid_executable_placeholder.png` |
| `invalid_schema_version` | yes | yes | `expected_failure`, `VIEWER_SCENE_SCHEMA_VERSION_INVALID` | `05_invalid_schema_version.png` |

## 6. Result
- Real browser evidence: READY
- Screenshot evidence: READY
- JSON-only preview evidence: READY
- Manifest preview evidence: READY
- Renderer evidence: DEFERRED
- Renderer implementation: NOT_READY
- Full `structure.viewer_3d` implementation: NOT_READY

## 7. Conclusion
PASS
