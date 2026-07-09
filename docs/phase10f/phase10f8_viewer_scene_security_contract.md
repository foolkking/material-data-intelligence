# Phase 10F-8 Viewer Scene Security Contract

## 1. Boundary

`viewer_scene.json` is data, not code. Phase 10F-8 does not approve a renderer, WebGL runtime, Three.js integration, renderer bundle, iframe viewer, notebook execution path, external script workflow, or external API workflow.

## 2. Required Security Flags

```json
{
  "security": {
    "contains_javascript": false,
    "external_urls": [],
    "external_urls_allowed": false,
    "artifact_supplied_js_allowed": false,
    "renderer_required": false,
    "remote_assets_allowed": false,
    "html_allowed": false
  }
}
```

## 3. Prohibited Artifact Content

- JavaScript, HTML, or CSS intended for execution.
- Inline event handlers.
- Callback fields.
- `eval` payloads or function bodies.
- Dynamic import paths.
- Remote textures, fonts, models, shaders, or CDN references.
- Absolute local paths intended for renderer loading.
- Hidden renderer bundle references.
- Notebook or script extraction payloads.

## 4. Renderer Handoff Rule

Future renderer implementation must treat the artifact as untrusted declarative input:

- never execute artifact-provided strings;
- never fetch artifact-provided external resources;
- never import modules named by artifact content;
- never allow artifact content to change sandbox policy;
- enforce caps again at renderer load time;
- keep browser evidence separate from JSON-only artifact evidence.

## 5. Planner and Runtime Boundary

Phase 10F-8 does not change planner routing, Tool Registry runtime behavior, QueueWorkerRuntime semantics, AnalysisPlanRepository semantics, `/planner/jobs`, or PlanValidator boundaries. Any future `structure.viewer_3d` route must be separately approved and tested.

## 6. Future Security Tests

Future implementation or evidence phases should test:

- script-like field rejection;
- `external_urls == []`;
- `renderer_required == false` in JSON-only artifacts;
- oversized structures rejected or truncated with typed warnings;
- invalid lattice and malformed coordinates rejected;
- viewer prompts do not route to XRD/RDF/coordination tools when a viewer tool is approved;
- XRD/RDF/coordination prompts do not route to viewer tools;
- phonon and Brillouin-zone prompts remain deferred unless separately approved;
- browser console/network audit shows no external requests caused by artifact preview.
