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

## Attempt 2

- SHA: `5aef027d312f462eea72a1ced10b33e4f4664a50`
- CI: `31270117864`
- Result: `SUCCESS`
- Backend: 1210 passed, 1 documented environment skip, 46 deselected
- Frontend: 430 passed
- Service-backed: 45 passed, 0 skipped, 0 failed, 0 errors
- Chromium, Firefox, WebKit, and Chromium 390x844 replay: PASS
- Typecheck, production build, lock, migration, evidence and no-skipped gates: PASS
