# Phase 10F-7 Viewer Security Boundary

## 1. Core Boundary

The viewer artifact is inert data. A renderer, if approved later, must not execute code supplied by the artifact.

## 2. Prohibited Artifact Behavior

- no artifact JavaScript
- no script tags
- no inline event handlers
- no external URLs
- no remote textures
- no remote fonts
- no CDN references
- no `eval`
- no dynamic import from artifact data
- no executable callbacks
- no arbitrary local file reads
- no notebook execution
- no external scripts
- no real LLM call

## 3. Required Caps

- bounded site count
- bounded bond count
- bounded unit-cell expansion
- bounded scene JSON size
- bounded screenshot size
- bounded browser memory

## 4. Future Security Tests

- artifact contains no script-like fields
- `security.external_urls == []`
- `security.external_urls_allowed == false`
- `security.renderer_required == false` for the JSON-only phase
- oversized structures are rejected or truncated with warnings
- invalid lattice values are rejected
- malformed site coordinates are rejected
- viewer prompts do not route to XRD, RDF, or coordination histogram
- phonon prompts remain deferred
- Brillouin-zone prompts remain deferred unless a separate scope approves them

## 5. Implementation Boundary

Phase 10F-7 does not add renderer code, WebGL, Three.js, artifact JS, notebook execution, external scripts, or new dependencies.
