# Phase 10F-7 Viewer Browser Evidence Model

## 1. JSON-Only Artifact Evidence

The first evidence phase after a viewer artifact contract should verify static preview only:

- `viewer_scene.json` preview as static JSON
- `viewer_summary.md` preview as Markdown/text
- `viewer_recipe.json` preview as static JSON
- no renderer
- no WebGL
- no canvas-based 3D viewer
- no artifact JavaScript execution
- no external requests caused by artifact preview

This mode can follow the Phase 10D/10E artifact-gallery evidence pattern.

## 2. Renderer Evidence After Explicit Approval

Renderer evidence is a later, separate scope and must include:

- real browser screenshot
- console audit
- network audit
- no external requests
- renderer sandbox checks
- no artifact JavaScript execution
- memory and performance caps
- malformed scene rejection tests
- dependency and bundle audit

## 3. Browser Tooling Guidance

Reuse the practical evidence lessons from Phase 10E-5R2 and Phase 10E-8:

- prefer Playwright with an explicit system Chrome or Edge executable path
- do not rely only on `where chrome` or `where msedge`
- record browser executable, version, viewport, frontend URL, artifact names, and timestamp
- capture completed job page, artifact list, JSON preview, summary preview, and recipe preview

## 4. Evidence Boundary

Static JSON preview evidence is not renderer evidence. A raw `viewer_scene.json` preview must not be described as an interactive 3D viewer.
