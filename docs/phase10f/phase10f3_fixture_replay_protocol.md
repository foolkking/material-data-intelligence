# Phase 10F-3 Fixture Replay Protocol

## 1. Purpose

This protocol defines how a later phase should replay static physics fixture-pack cases through the platform. Phase 10F-3 does not execute replay.

## 2. Replay Steps

1. Load fixture manifest.
2. Confirm fixture provenance label and PASS eligibility.
3. Upload input through the existing platform resource flow.
4. Submit a deterministic planner/job request for the target tool.
5. Verify selected `tool_id`.
6. Wait for job completion.
7. Download generated artifacts.
8. Validate artifact names and schema versions.
9. Validate no-JS/no-external-URL security fields.
10. Apply exact checks.
11. Apply numeric tolerance checks.
12. Record warnings and limits.
13. Produce evidence docs and a verification matrix.

## 3. Required Platform Boundary

Replay must use:

- existing upload/resource flow,
- deterministic planner or mock planner mode,
- persisted AnalysisPlan,
- PlanValidator,
- QueueWorkerRuntime,
- Tool Registry validation,
- adapter execution.

Replay must not bypass Tool Registry validation or call adapters directly as PASS evidence.

## 4. Prohibited During Replay

- real LLM
- notebook execution
- external script execution
- benchmark extraction scripts
- external APIs
- network-dependent fixture generation
- artifact JavaScript execution
- external URL loading
- WebGL/canvas 3D viewer invocation
- dependency installation
- arbitrary local file read

## 5. Browser Policy

Browser preview is not required for fixture-pack construction. If a later evidence phase adds browser screenshots, they must be real browser-rendered frontend screenshots and must not be used to compensate for missing API/artifact comparison.

## 6. Result Labels

Allowed future replay results:

- `PASS`: direct replay and expected-contract comparison succeeded for an eligible case.
- `PARTIAL_PASS`: direct replay succeeded but expected numeric coverage is intentionally partial.
- `REGRESSION_PASS`: internal or official-like replay succeeded but is not official PASS.
- `MAPPING_ONLY`: not directly executable.
- `EXTRACTION_REQUIRED`: requires extraction not performed.
- `FUTURE_SCOPE`: outside static physics fixture-pack scope.
- `FAILED`: replay or comparison failed.

`official_like_curated` and `internal_regression` cases must not be labeled official PASS.
