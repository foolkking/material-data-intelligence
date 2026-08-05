# State Ownership

| State | Authority | Reload |
| --- | --- | --- |
| title, revision, panel membership/order, approved layout, saved active-panel fallback, pinned selection | server Workspace persistence | exact GET snapshot |
| active panel and exact versioned selection | URL | validated independently |
| camera, hover, playback, filters, dialogs, unsaved edits, Report draft | memory | intentionally discarded |
| finalized Report/Recipe | existing immutable persistence | exact history/detail pair |

`LOCAL_STORAGE_CANONICAL_AUTHORITY = NONE`

`SESSION_STORAGE_CANONICAL_AUTHORITY = NONE`

`OFFLINE_CANONICAL_WORKSPACE_COPY = NONE`
