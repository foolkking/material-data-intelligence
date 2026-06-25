# Worker Service

Worker service scaffold.

Current library layer:

- `mdi_workers.run_tool_call_job()` wraps the registry-approved adapter executor.
- `InMemoryJobStore` records Job status, ToolCall status, and JobEvent sequence
  semantics for local tests.
- Production Celery queues, PostgreSQL repositories, SSE publishing, retries,
  and cancellation are still future work.
