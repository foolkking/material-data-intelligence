# Phase 10M-6 Performance and Lifecycle

All figures are development acceptance evidence, not production capacity claims. Initial loading remains metadata-first. Heavy payloads are active-panel-only; Report preview creates no WebGL context. Request identity includes Workspace/revision/panel/Artifact/checksum/contract/source hash and stale responses cannot commit.

Workspace Save and Job observation each own an AbortController. Route, panel, source, checksum, revision, history, and unmount transitions cancel or invalidate prior work. Visibility revalidation reads current server authority rather than trusting background timers.

M4 ownership remains unchanged: one active heavy Viewer, explicit animation/listener/observer/geometry/material/texture/renderer cleanup, context-loss fallback, and no duplicate canvas.

```text
INITIAL_HEAVY_ARTIFACT_PAYLOAD_REQUESTS = 0
INACTIVE_HEAVY_ARTIFACT_PAYLOAD_REQUESTS = 0
MAX_ACTIVE_HEAVY_VIEWERS = 1
STALE_RESPONSE_STATE_COMMITS = 0
WEBGL_CONTEXT_GROWTH = 0
LISTENER_GROWTH = 0
OBSERVER_GROWTH = 0
DUPLICATE_CANVAS = 0
REPORT_PREVIEW_WEBGL_CONTEXTS = 0
```
