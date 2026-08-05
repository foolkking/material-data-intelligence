# Phase 10M-6 State Ownership

## Server

Server persistence owns Workspace identity/title/revision, immutable source bindings, panel membership/order, approved layout metadata, saved active-panel fallback, explicitly pinned exact selection, and finalized Report/Recipe history. Mutations use the existing PATCH contract and If-Match.

## URL

`panel` and versioned exact `selection` are independent navigation authorities. An explicit valid URL value wins over its persisted fallback. An explicit invalid/stale value produces a typed state and never silently falls back or pins.

## Memory

Camera, hover, playback, filters, expanded details, dialogs, unsaved durable edits, in-flight requests, and unfinalized Report drafts are session memory. They are intentionally discarded by close/refresh.

```text
LOCAL_STORAGE_CANONICAL_AUTHORITY = NONE
SESSION_STORAGE_CANONICAL_AUTHORITY = NONE
OFFLINE_CANONICAL_WORKSPACE_COPY = NONE
EPHEMERAL_SELECTION_SERVER_PERSISTENCE = 0
```
