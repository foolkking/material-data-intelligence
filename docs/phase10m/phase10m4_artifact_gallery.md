# Phase 10M-4 Typed Artifact Gallery

Status: local implementation in progress; exact-SHA CI and lifecycle closure
are pending.

## Authority Boundary

The Workspace Results panel presents persisted Artifact metadata and opens
payloads through the application-owned renderer layer. It does not create,
modify, or recompute scientific results.

```text
WorkspacePanel metadata
    -> authorized Job Artifact list
    -> exact Artifact type/version lookup
    -> active-only payload load
    -> checksum and scope validation
    -> application-owned renderer or inert fallback
```

Renderer selection never uses a filename, title, MIME type alone, ToolCall
display name, dynamic module name, or user-provided renderer hint. Unknown
contracts produce `CONTRACT_UNSUPPORTED`; known types with an unsupported
version produce `ARTIFACT_CONTRACT_VERSION_UNSUPPORTED`.

## Gallery Surface

Each metadata card exposes the Artifact title, type and version, renderer
classification, source ToolCall and step, producer identity when available,
status, checksum abbreviation, byte size, creation time, lineage metadata,
selection support, and safe open/download actions. Group and display order are
presentation only and never become scientific identity.

The initial Workspace request remains metadata-only. Payload requests begin
only when a user opens an eligible Artifact. Changing the active Artifact,
changing Workspace, or unmounting the route aborts or ignores stale requests.
The Gallery bounds metadata rendering to 256 items and reports loaded and total
counts rather than silently claiming a complete unbounded list.

## State Policy

`PRODUCED` and `PARTIAL` panels may open their exact artifacts. Failed,
dependency-blocked, stale, deleted, unsupported, integrity-mismatched,
over-cap, profile-unavailable, and legacy states remain isolated typed states.
A failure in one Artifact viewer does not blank sibling metadata or viewers.

Legacy and unsupported artifacts receive an inert provenance/download surface.
HTML, SVG, CSV, and other download-only content is not inserted into the DOM.
JSON is rendered as bounded text and Markdown/text uses the existing safe text
path without raw HTML execution.

## Unchanged Contracts

`ScientificWorkspace 1.0`, `WorkspacePanel 1.0`, and
`WorkspaceSelectionContext 1.0` are unchanged. Migration head remains
`0007_phase10m1_workspace_domain`; no renderer, Gallery, cache, or selection
table is introduced. Artifact payloads remain in the existing Artifact storage
authority and are not copied into Workspace persistence.
