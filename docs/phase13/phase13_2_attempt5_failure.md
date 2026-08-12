# Phase 13-2 Attempt 5 Failure

Attempt 5 passed its repository, semantic-coverage, Level C/C2, D0, and Demo 1
closure entry dependencies. It then started five fresh canonical demos against
real PostgreSQL, Redis, and MinIO services. Demos 1-3 completed the full product
path, including Chromium UI Report Finalize and paired non-executable Recipe.

The attempt stopped on two new release-critical integration defects:

- `P13-R5-001`: Demo 4 completed the trajectory Job, three registered ToolCalls,
  and twelve persisted Artifacts, but Report eligibility classified the fresh
  Workspace source as `WORKSPACE_SOURCE_NOT_CURRENT`.
- `P13-R5-002`: Demo 5's real phonon upload reached Profile persistence, then
  Intent validation failed with `INTENT_PROFILE_CAPABILITY_MISSING` before Plan
  or Job creation.

No production or scientific code was changed. Demo 6-7 and all downstream
acceptance suites were not executed after the P0 stop. Phase 13-3 remains
blocked pending reviewer-authorized remediation and a future full rerun.
