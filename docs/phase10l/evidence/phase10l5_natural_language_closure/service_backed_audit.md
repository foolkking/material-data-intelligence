# Phase 10L-5 Service-Backed Audit

Five separately collected cases exercise PostgreSQL repositories, Redis enqueue, MinIO artifacts, exact persisted plans/jobs, QueueWorkerRuntime, lineage, deterministic grounded interpretation, API read-back, checksums, and idempotency.

- Status: `PENDING_EXACT_SHA_CI`.
- Exact-SHA CI run: `PENDING`.
- Required result: 5 L5 cases passed, 0 skipped, 0 failed within the repository-wide service-backed no-skip gate.
- Local Docker absence is not represented as a pass.
- Default service CI uses deterministic Mock transport and `REAL_LLM_CALLS = 0`; live DeepSeek verification is separate.
