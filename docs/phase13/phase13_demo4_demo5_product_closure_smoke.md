# Demo 4 / Demo 5 Product-Closure Smoke Status

Both smokes are not counted as Attempt 6 execution.

- Demo 4: `NOT_EXECUTED_AFTER_BRANCH_C_STOP`. The currentness implementation
  passed focused positive and stale regressions, but the required fresh
  PostgreSQL/Redis/MinIO/Chromium closure was not run.
- Demo 5: `NOT_APPLICABLE_BRANCH_C`. A legal supported user entry does not
  exist, so running an internal mapper or manual Profile/resource injection
  would violate the release contract.

Attempt 6 remains `NOT_EXECUTED / NOT_QUEUED`.

