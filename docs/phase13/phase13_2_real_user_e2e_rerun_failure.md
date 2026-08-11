# Phase 13-2 Full Rerun Failure

## Conclusion

The reviewer-authorized second attempt passed its remediation and scope entry
gates, then stopped during a fresh seven-family production-runtime preflight.
It did not reach the service-backed browser demonstrations and makes no demo
PASS claim.

Attempt history:

- Attempt 1: `FAILED_HISTORICAL / BLOCKED_BY_PRODUCT_ENTRY_DEFECTS`.
- Remediation: `Phase 13-1 Fix-Forward PASS`.
- Attempt 2: `FAILED_RERUN / REVIEWER_ACTION_REQUIRED`.

## New Findings

`P13-RR-001` (P0): the production object-store builder does not expose parsed
`PhononBand` and `PhononDos` exact object IDs. Demo 5 reaches a valid Plan but
the registered phonon Adapters fail with `Unknown input ref`.

`P13-RR-002` (P0): the production object-store builder does not expose parsed
`ElectronicBand` and `ElectronicDos` exact object IDs. Demo 7 reaches a valid
Plan but the registered electronic Adapter fails with `Unknown input ref`.

`P13-RR-003` (P0): Demo 3 reaches and executes its structure Tools, but the
experimental XRD comparison rejects the real theoretical dependency result
because the sealed experimental and theoretical wavelengths are incompatible.

These are product integration defects, not scientific validation defects. No
production patch was authorized or made in Phase 13-2.

## Execution Status

- Fresh parser/Profile/Intent/Eligibility/Planner/Plan/runtime preflights: `7/7`.
- Full service-backed real-user demos executed: `0/7`.
- Demo PASS or explicit-limit claims: `0/7`.
- `P13X2` acceptance: `0/8`.
- Release-critical integration defects: `3`.
- Scientific defects: `0`.
- Security defects: `0`.

The local PostgreSQL, Redis and MinIO instances were reachable, but the defect
discovery stop rule fired before they could become full E2E authority. Browser
and negative-path rerun execution was therefore not started.

## Authority

- Fact Model: `e0248d502e4a442bb9596a8d2f6fe6d7fdefe61c41121ae08736734ce4004a06`.
- Current Scope Baseline: `caf9a67d7eb1f966eb3ea477beb60d0111020c84c3d065ed547ce816d9d98fd4`.
- Registry: `62`.
- DataProfile: `2.4`.
- AnalysisIntent / EligibilityResolution: `1.0 / 1.0`.
- AnalysisPlan: `0.1 / 0.2`.
- Migration: `0007_phase10m1_workspace_domain`.

No scope, scientific, schema, dependency, provider, API or frontend authority
changed. Phase 13-3 remains blocked and Initial Release remains incomplete.

Canonical evidence:
`docs/phase13/evidence/phase13_2_seven_real_user_e2e_rerun/`.
