# Completion-Record CI Attempts

## Attempt 1

- SHA: `e805b8c8d41e69254da21b3209c600f8dce9aa34`
- CI: `31288217113`
- Result: `FAILED`
- Frontend, typecheck, build and full browser replay: PASS
- Service-backed: 45 passed, 0 skipped, 0 failed, 0 errors
- Unit: 1209 passed, 1 failed, 1 documented skip, 46 deselected
- Failure: the retained N2 lifecycle assertion allowed N3 reviewer-gate,
  implementation and archived states, but omitted the legal N3
  `PASS / COMPLETE / AWAITING_COMPLETION_RECORD_CI` state.
- Correction scope: compatibility assertion only; production science,
  contracts, persistence, dependencies and lockfile are unchanged.

## Attempt 2

- SHA: `c7547903faef191c97f35ca0ae2ad1ad1678193f`
- CI: `31288792343`
- Result: `SUCCESS`
- Backend: 1210 passed, 1 documented environment skip, 46 deselected
- Frontend: 430 passed
- Service-backed: 45 passed, 0 skipped, 0 failed, 0 errors
- Full browser replay, typecheck, build, lock and no-skipped gates: PASS
