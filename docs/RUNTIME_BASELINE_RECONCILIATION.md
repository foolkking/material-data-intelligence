# Runtime Baseline Reconciliation

**Previous freeze:** `FROZEN_BASELINE_V1`
**Current:** `FROZEN_BASELINE_V2`
**Observation date:** 2026-09-06
**Mutation:** none; no service was started, stopped, restarted, or written.
**Reconciliation:** `RECONCILED_STOPPED_WITH_STALE_MANIFEST` for stopped managed services.

## Independent Observations

- TCP/process inspection confirms PostgreSQL PID `8468` on `5432` and Redis-compatible Memurai PID `7284` on `6379`.
- No project API process or listener on `8005` was observed.
- No dedicated frontend process or listener on `3023` was observed. Codex-owned Node processes were excluded by command identity.
- No MinIO process or listener on `9000/9001` was observed.
- No project Python worker process was observed.
- No safe read-only RQ registration query was executed (`redis-cli` is unavailable and importing the application/RQ stack could create cache/startup side effects). Registration is therefore `CURRENT_UNKNOWN`, but it does not contradict the stopped process conclusion.
- The repository-side Alembic revision chain ends at `0032_provider_connections`. Live database migration head was not queried because credentials/connection safety were not established; live DB head is `CURRENT_UNKNOWN`, not silently inferred.

## Service Matrix

| Service / role | OBSERVED_STATE | MANIFEST_STATE | MANIFEST_AGE | PROCESS_STATE | LISTENER_STATE | REGISTRATION_STATE | CONSISTENCY | CONCLUSION |
|---|---|---|---|---|---|---|---|---|
| API | no current API response/process | `.runtime_services/managed/api/api-8005.json` says `RUNNING` | started `2026-09-06T02:31:00Z`; older than observation; stored PIDs no longer exist | stopped | `8005` absent | n/a | conflict reconciled by PID/listener absence | `STOPPED_CONFIRMED` + stale manifest |
| Frontend | no current frontend runtime | no active dedicated manifest found; historical build/log records exist | historical/unknown | stopped | `3023` absent | n/a | consistent with stopped process | `STOPPED_CONFIRMED` |
| PostgreSQL | process tree active | expected infrastructure | process created `2026-09-03T13:56:27` | active PID `8468` and children | `5432` listening | n/a | consistent | `ACTIVE_CONFIRMED` |
| Redis-compatible | Memurai process active | expected infrastructure | process created `2026-09-03T13:56:26` | active PID `7284` | `6379` listening | RQ registration not queried | partially observed | `ACTIVE_CONFIRMED` |
| MinIO | no current process | `.runtime_services/managed/minio/usage-*.json` is an observation cache | captured `2026-09-06T02:32:07Z`; historical for this observation | stopped | `9000/9001` absent | n/a | stale observation, no current server | `STOPPED_CONFIRMED` + stale observation |
| `mdi-agent-turns` | no current worker | manifest `RUNNING`, old runner/child PIDs | last seen `2026-09-06T02:01:46Z` | stopped | no worker listener | unknown | conflict reconciled by absent process | `STOPPED_CONFIRMED` + stale manifest |
| `mdi-agent-plans` | no current worker | manifest `RUNNING`, old PIDs | last seen `2026-09-06T02:01:46Z` | stopped | no worker listener | unknown | same | `STOPPED_CONFIRMED` + stale manifest |
| `mdi-jobs` | no current worker | manifest `RUNNING`, old PIDs | last seen `2026-09-06T02:01:46Z` | stopped | no worker listener | unknown | same | `STOPPED_CONFIRMED` + stale manifest |
| `mdi-agent-results` | no current worker | manifest `RUNNING`, old PIDs | last seen `2026-09-06T02:01:46Z` | stopped | no worker listener | unknown | same | `STOPPED_CONFIRMED` + stale manifest |
| `mdi-agent-interpretations` | no current worker | manifest `RUNNING`, old PIDs | last seen `2026-09-06T02:01:46Z` | stopped | no worker listener | unknown | same | `STOPPED_CONFIRMED` + stale manifest |
| `mdi-agent-reports` | no current worker | manifest `RUNNING`, old PIDs | last seen `2026-09-06T02:01:46Z` | stopped | no worker listener | unknown | same | `STOPPED_CONFIRMED` + stale manifest |

## Exact Worker Identities Observed in Manifests

| Queue | Handler |
|---|---|
| `mdi-agent-turns` | `mdi_api.research_agent_worker.run_queued_turn` |
| `mdi-agent-plans` | `mdi_api.research_agent_planning_worker.run_queued_planning` |
| `mdi-jobs` | `mdi_workers.queue_runtime.run_queued_job` |
| `mdi-agent-results` | `mdi_api.scientific_results.worker.run_queued_result_projection` |
| `mdi-agent-interpretations` | `mdi_workers.interpretation_worker.run_queued_interpretation` |
| `mdi-agent-reports` | `mdi_workers.report_worker.run_queued_report_generation` |

## Reconciliation Decision

The prior conflict is closed as a stale-runtime-manifest condition:

`RECONCILED_STOPPED_WITH_STALE_MANIFEST`

This does not authorize editing or deleting manifests, starting services, or treating stopped product services as a current product PASS. Future runtime verification must use a fresh controlled launch and exact release SHA. The current freeze records PostgreSQL and Redis as infrastructure-active, all managed product/worker services as stopped, and RQ registration as not verified by the read-only audit.
