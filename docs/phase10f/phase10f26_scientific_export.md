# Phase 10F-26 Scientific Export and Reporting Foundation

## Scope and architecture

The validated local viewer now exports a bounded current view without changing
the canonical scene, backend job, topology, or source structure. One existing
Three.js renderer is temporarily resized, rendered, encoded, and restored. No
second WebGL context, server renderer, external upload, or remote asset is used.

The export pipeline is:

```text
validated render scene + application-owned view state
  -> strict ViewerExportRequest
  -> temporary renderer size/background/overlay state
  -> PNG Blob and restored interactive renderer
  -> inert JSON state + Markdown summary
  -> ordered manifest with SHA-256 hashes
  -> local browser downloads
```

An export generation token rejects stale work after scene or view changes.
Only one export is active at a time. Blob URLs are revoked after download.

## Product boundary

PNG, JSON, Markdown, and an integrity manifest are ready. PDF is deferred by
design because paginated layout, vector/raster policy, fonts, metadata, and a
new dependency/security review are not yet approved. This phase adds no backend
tool, canonical scene field, planner route, dependency, or execution authority.
