# Workspace State and Error Taxonomy

## Existing source states

- Job: `created`, `queued`, `running`, `partial_success`, `completed`, `failed`, `cancel_requested`, `cancelled`.
- ToolCall: `planned`, `running`, `completed`, `failed`, `skipped`.
- Dependency execution: `ALL_SUCCEEDED`, `PARTIAL_RESULTS`, `ALL_FAILED`, `VALIDATION_ABORTED`.
- Dependency step: `PENDING`, `READY`, `RUNNING`, `SUCCEEDED`, `FAILED`, `BLOCKED_DEPENDENCY`, `NOT_STARTED`.
- Interpretation: ready, ready-with-limits, no evidence, not terminal, integrity failed, cap exceeded, provider failed, validation failed.

## Sealed Workspace projection

Workspace status is derived, never an independent scientific execution status.

| Workspace status | Deterministic source rule |
|---|---|
| `SOURCE_MISSING` | Job or required immutable source cannot be read |
| `UNSUPPORTED` | source schema has no compatibility projector |
| `LEGACY_READ_ONLY` | source is readable but lacks required modern identity |
| `STALE` | source exists but exact dataset/profile/artifact binding no longer matches |
| `RUNNING` | Job is created, queued, running, or cancel_requested |
| `PARTIAL_RESULTS` | Job is partial_success or dependency outcome is PARTIAL_RESULTS |
| `COMPLETE` | Job completed and source integrity passes |
| `FAILED` | Job failed/cancelled or dependency outcome is ALL_FAILED/VALIDATION_ABORTED |
| `READY` | persisted source is valid and no execution has started |
| `INITIALIZING` | Workspace projection is being assembled |

## Sealed panel projection

`NOT_APPLICABLE`, `READY_NOT_RUN`, `LOADING`, `PRODUCED`, `PARTIAL`, `UNAVAILABLE`, `FAILED`, `BLOCKED_BY_DEPENDENCY`, `STALE`, `CAP_EXCEEDED`, `CONTRACT_UNSUPPORTED`, `SOURCE_DELETED`, and `PROFILE_AUTHORITY_UNAVAILABLE` are UI projections. They do not replace Job, ToolCall, dependency, or interpretation enums.

## Error contract

Every panel error includes a stable code, scope, safe message, source ref, retryability, and next user action. Generic `Something went wrong` is not an accepted final state. Raw stack traces, paths, provider payloads, credentials, object-store keys, and authorization details remain hidden.
