# Phase 12-3 Heavy Viewer Lifecycle

The existing `WorkspaceHeavyViewerLease` remains the lifecycle authority.
Metadata is loaded on Workspace entry; heavy payloads load only after explicit
result opening. Abort, stale-response suppression and renderer cleanup remain
required, with one active heavy viewer at a time.
