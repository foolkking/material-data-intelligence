# Phase 10M-6 Job and Source Recovery

For queued/running sources the shell loads persisted Workspace and Job projection, then performs bounded GET revalidation and a visibility-triggered refresh. PostgreSQL Job, ToolCall, dependency, Artifact metadata, and interpretation records are recovery authority; Redis events are not the sole authority. Route/unmount cancels obsolete observation, and terminal state stops polling.

Successful independent branches remain readable beside failed/blocked panels. Warnings, limitations, missing desired outputs, and partial/all-failed state remain visible. Recovery never recreates or retries execution.

Stale Dataset/Profile/resource/checksum identities remain exact and typed. Missing Artifact metadata shows `ARTIFACT_MISSING`; missing payload retains authorized metadata/lineage and disables Viewer/download. Missing interpretation leaves methods/execution/Artifacts available and findings unavailable. Plan 0.1 never gains invented dependencies; Plan 0.2 retains exact bindings; legacy records remain read-only.

```text
STALE_SOURCE_LATEST_REBINDING = 0
WORKSPACE_REFRESH_PLAN_CREATION_GROWTH = 0
WORKSPACE_REFRESH_JOB_CREATION_GROWTH = 0
WORKSPACE_REFRESH_TOOLCALL_CREATION_GROWTH = 0
WORKSPACE_REFRESH_QUEUE_MESSAGE_GROWTH = 0
WORKSPACE_RECOVERY_AUTOMATIC_RERUN = 0
```
