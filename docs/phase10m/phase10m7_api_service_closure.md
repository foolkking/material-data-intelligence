# Phase 10M-7 API and Service Closure

The exact routes are recovered from `apps/api/mdi_api/main.py`. M7 adds no
endpoint. The closure covers source registration, DataProfile, Intent and
clarification, planner Job creation, Job/events/Artifacts, interpretation,
Workspace create/get/list/patch/panels/layout history, and all M5 Report/Recipe
routes.

The service-backed CI runs PostgreSQL, Redis, and MinIO. Its selected suite
contains the L1-L5, M1, M5, M6, and M7 service cases. M7's aggregate service
test verifies migration head 0007, all full-chain persistence tables, Redis
availability, MinIO checksum-preserving retrieval, and retained real DeepSeek
provenance. Named service tests must pass with zero skips and zero failures.

| Service | Durable authority | Recovery/security proof |
| --- | --- | --- |
| PostgreSQL | Profile, Intent, decision, Plan, Job, ToolCall, dependency, Artifact metadata, interpretation, Workspace, Report, Recipe | migration and scope tests |
| Redis | queue/event observation | not durable authority; missing-event recovery uses PostgreSQL |
| MinIO | Artifact bytes | authorized retrieval, exact checksum, missing-object typed state |

Local service unavailability is reported as unavailable. Exact-SHA CI is the
service-backed authority.
