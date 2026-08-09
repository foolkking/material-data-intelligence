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
