# API Matrix

All routes are existing additive authorities; M7 adds no endpoint. Project/Workspace/Job scope, strict DTO validation, quoted ETag/If-Match, checksum, and idempotency remain enforced.

| Method | Route | Responsibility |
| --- | --- | --- |
| POST | `/datasets/{dataset_id}/files` | source registration |
| POST | `/datasets/{dataset_id}/profile` | DataProfile |
| POST | `/planner/intents` | Intent |
| POST | `/planner/intents/{intent_id}/clarification` | clarification |
| POST | `/planner/jobs` | Eligibility/decision/Plan/Job |
| GET | `/planner/jobs/{job_id}` | Job |
| GET | `/planner/jobs/{job_id}/events` | events |
| GET | `/planner/jobs/{job_id}/artifacts` | Artifact metadata |
| GET | `/planner/jobs/{job_id}/interpretations` | interpretation |
| POST | `/workspaces` | Workspace projection |
| GET/PATCH | `/workspaces/{workspace_id}` | reload/Save |
| GET | `/workspaces/{workspace_id}/panels` | panels |
| GET | `/workspaces/{workspace_id}/layout-revisions` | history |
| GET | `/workspaces/{workspace_id}/report-composition/sources` | Report sources |
| POST | `/workspaces/{workspace_id}/report-compositions/preview` | no-write preview |
| POST/GET | `/workspaces/{workspace_id}/report-compositions` | finalize/history |
| GET | `/workspaces/{workspace_id}/report-compositions/{report_id}/recipe` | Recipe |
| GET | `/workspaces/{workspace_id}/report-compositions/{report_id}/exports/{format}` | JSON/Markdown export |
