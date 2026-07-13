# Phase 10 Closure CI Contract

The existing required CI jobs remain authoritative:

- Unit installs frozen Python dependencies, runs the exact backend closure,
  then the complete non-integration suite and `uv lock --check`.
- Frontend uses `npm ci`, runs the exact frontend closure and browser evidence
  integrity check, then typecheck and production build.
- Service-backed integration uses PostgreSQL, Redis, and MinIO, includes the
  formal viewer closure, and rejects any skipped/failed result. Minimum pass
  count is 20.

The real browser runner is an explicit local/review entry because the current
CI has no Playwright browser dependency and this phase adds no large testing
dependency. CI validates the committed three-browser evidence and hashes; a
fresh browser run is required when product browser behavior changes.

All entries return nonzero on failure, perform no deployment or push, use no
real LLM, and require no external network at runtime.
