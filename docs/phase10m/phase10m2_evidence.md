# Phase 10M-2 Evidence

Evidence is retained under
`docs/phase10m/evidence/phase10m2_workspace_shell/`.

The browser runner launches the real Next route and supplies only bounded M1
API contract fixtures. It covers complete, running, partial, legacy, stale,
unsupported, exact panel deep links, back/forward/refresh, Planner history,
desktop Chromium/Firefox/WebKit, and Chromium 390x844. Scientific execution
and LLM behavior are not simulated or claimed by this browser fixture.

The service-backed gate uses PostgreSQL, Redis, MinIO, migration head 0007,
the real Workspace API, persisted source Job, explicit projection, panels,
layout revision, ETag, idempotent replay, and hidden-write assertions. The
corrected implementation exact-SHA run `30729180057` passed with `38 passed, 0
skipped, 0 failed, 0 errors`. The manifest hashes LF-normalized text and raw
PNG bytes.
