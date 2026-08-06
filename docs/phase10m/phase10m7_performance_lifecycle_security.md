# Phase 10M-7 Performance, Lifecycle, and Security

Performance figures are development acceptance evidence, not production
capacity claims.

```text
INITIAL_HEAVY_ARTIFACT_PAYLOAD_REQUESTS = 0
INACTIVE_HEAVY_ARTIFACT_PAYLOAD_REQUESTS = 0
ADJACENT_HEAVY_PANEL_PREFETCH = 0
MAX_ACTIVE_HEAVY_VIEWERS = 1
STALE_RESPONSE_STATE_COMMITS = 0
REPORT_PREVIEW_WEBGL_CONTEXTS = 0
WEBGL_CONTEXT_GROWTH = 0
LISTENER_GROWTH = 0
OBSERVER_GROWTH = 0
ANIMATION_LOOP_GROWTH = 0
DUPLICATE_CANVAS = 0
```

The existing M4 lifecycle runner retains 50 heavy-viewer cycles. M7 adds no
WebGL owner. Artifact, Workspace, URL, Report, and Recipe content remain inert;
cross-Project/Workspace/Job injection, checksum bypass, stale rebinding,
private path/storage key disclosure, provider fallback, recovery execution,
and browser scientific recomputation remain prohibited and regression-tested.
