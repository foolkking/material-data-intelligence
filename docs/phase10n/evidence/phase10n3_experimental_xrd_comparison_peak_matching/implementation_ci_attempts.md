# Implementation CI Attempts

## Attempt 1

- SHA: `1faa25582107ac3d34efea2e75b61ae3d0f9be13`
- CI: `31269467363`
- Result: `FAILED`
- Unit: PASS
- Frontend, typecheck, build and full browser replay: PASS
- Service-backed: 44 passed, 0 skipped, 1 failed
- Failure: the retained Phase 10M-3 service test expected the pre-N3 seven-kind
  emitted selection list. Production emitted the approved ten-kind list,
  including `EXPERIMENTAL_XRD_PEAK`, `THEORETICAL_XRD_PEAK`, and `XRD_MATCH`.
- Correction scope: compatibility assertion only; no scientific behavior,
  contract, database, migration, API family, dependency, or lockfile change.
