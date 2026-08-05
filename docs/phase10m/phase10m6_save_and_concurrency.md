# Phase 10M-6 Save and Concurrency

The Workspace shell compares a canonical durable draft (`title`, `activePanelId`) with the current server base. Transient state and Report draft changes do not make the Workspace dirty. A no-op disables Save and emits no PATCH or revision.

Save sends only changed approved fields with the current quoted ETag in `If-Match`. Duplicate submits are disabled, unmount aborts the request, and only a successful response replaces the base revision/ETag and clears dirty state.

A 412 conflict preserves local edits, fetches the exact current server snapshot, announces local/server revisions, and offers explicit confirmed server reload. It does not overwrite or merge automatically. At revision cap, edits remain in memory and the readable Workspace/Report history remains available; history is never deleted or compacted.

```text
WORKSPACE_NOOP_SAVE_REQUESTS = 0
WORKSPACE_NOOP_SAVE_REVISION_GROWTH = 0
WORKSPACE_CONFLICT_SILENT_OVERWRITE = 0
WORKSPACE_CONFLICT_AUTOMATIC_MERGE = 0
MAX_LAYOUT_REVISIONS = 128
WORKSPACE_REVISION_CAP_HISTORY_DELETION = 0
```
