# Phase 10F-8 Viewer Scene Browser Evidence Contract

## 1. Evidence Phases

### JSON-only artifact evidence

Allowed in Phase 10F-9:

- static preview of `viewer_scene.json`;
- static preview of viewer scene manifest JSON;
- summary/recipe preview if those artifacts are present;
- caps/warnings/security fields visible to the user;
- raw JSON fallback available;
- no renderer bundle, WebGL, Three.js, or artifact JavaScript.

### Renderer evidence

Deferred until explicit approval:

- real browser screenshot of a renderer;
- console/network audit for renderer code;
- sandbox and isolation checks;
- memory/performance caps;
- malicious artifact tests;
- dependency review for any renderer library.

## 2. JSON-Only Browser Evidence Requirements

Browser evidence for the contract-only phase should prove:

| Evidence Item | Requirement |
|---|---|
| job/artifact page | Completed job or fixture result page displays artifact entries. |
| scene preview | `viewer_scene.json` is visible as schema-aware static preview or raw JSON. |
| manifest preview | Manifest is visible as inert JSON/manifest preview. |
| caps/warnings | Caps and warnings are visible or readable in raw JSON. |
| security flags | No-JS/no-external-URL/no-renderer-required flags are visible. |
| network audit | No external URL request is caused by artifact preview. |
| renderer absence | Evidence explicitly states no WebGL/Three.js/full viewer was invoked. |

## 3. Screenshot Policy

If screenshots are captured, they must be real browser-rendered frontend pages. They must not be static HTML substitutes. Phase 10D and Phase 10E evidence show the preferred path: explicit system Chrome or Edge executable path with Playwright where automation is needed. Do not rely only on `where chrome` or `where msedge`.

## 4. Console / Network Policy

If automation captures logs, record:

- browser executable and version;
- frontend URL;
- artifact names;
- console errors attributable to the feature;
- external network requests attributable to artifact preview;
- confirmation that artifact JS did not execute.

## 5. Boundary Statement

Static JSON preview evidence is not renderer evidence. A visible `viewer_scene.json` preview must not be described as an interactive 3D viewer.
