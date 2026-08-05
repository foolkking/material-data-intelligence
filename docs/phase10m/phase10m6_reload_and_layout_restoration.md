# Phase 10M-6 Reload and Layout Restoration

Reload resolves state in this order: Workspace/status/revision metadata, ordered panel metadata, explicit URL panel, explicit URL selection, persisted fallback fields only when the corresponding URL field is absent, active lightweight panel, then active heavy payload on demand.

Panel precedence is valid explicit URL panel, saved valid active-panel fallback, then deterministic default. An explicit invalid panel remains an error. Selection precedence is valid explicit URL selection, valid explicitly pinned fallback when URL selection is absent, then no selection. An explicit invalid/stale selection remains typed and is not rebound.

Reload preserves exact Workspace/Project/Job/Dataset/Profile/Plan/panel/revision identities and finalized delivery history. It does not preserve transient viewer state or draft state and performs no PATCH/finalize/Job/queue operation.

```text
WORKSPACE_RELOAD_HIDDEN_WRITES = 0
INITIAL_HEAVY_ARTIFACT_PAYLOAD_REQUESTS = 0
```
