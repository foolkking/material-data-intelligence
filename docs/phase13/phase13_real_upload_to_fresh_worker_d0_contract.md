# Phase 13 Real Upload to Fresh Worker D0 Contract

D0 is a Level-D admission smoke, not a demo PASS. It performs a real HTTP upload, durable SQL/MinIO persistence, natural-language Intent, Eligibility, Planner, PlanValidator, Job persistence and Redis enqueue. All uploader nondurable state is then discarded and fresh repositories, resolver and QueueWorkerRuntime execute the first registered ToolCall and persist the first Artifact.

D0 uses PostgreSQL, Redis and MinIO with no in-memory repository, manual normalized-export preload, fixture map, runtime reparse or queue-carried scientific payload. It stops at the first persisted Artifact; Workspace, interpretation, Report, Recipe and seven-demo validation remain Phase 13-2 responsibilities.
