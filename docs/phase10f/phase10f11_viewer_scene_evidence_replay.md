# Phase 10F-11 Viewer Scene Evidence Replay

## 1. Replay Command
```text
node apps/web/test/viewer-scene-browser-evidence.mjs
```

## 2. Preconditions
- Existing web dependencies are installed.
- Playwright is available from the local evidence runner path used by prior browser evidence phases.
- System Chrome is available from the configured executable path.
- No real LLM, external API, or notebook execution is required.

## 3. Replay Flow
1. Stop any stale listener on the evidence port.
2. Start the existing Next.js app on a loopback dev server.
3. Launch system Chrome through Playwright.
4. Use fixture-backed mock API responses for the existing PlannerWorkbench flow.
5. Load demo data through the existing UI.
6. Submit the existing mock planner form.
7. Open the existing results tab.
8. Assert viewer_scene JSON-only preview and manifest selectors.
9. Assert security/inertness conditions.
10. Save screenshots, DOM snapshot, network audit, and command log.

## 4. Non-Goals
- No production runtime route.
- No new adapter.
- No planner routing change.
- No renderer or 3D viewer.
- No WebGL or Three.js.

## 5. Expected Result
```text
VIEWER_SCENE_BROWSER_EVIDENCE_PASS
```
