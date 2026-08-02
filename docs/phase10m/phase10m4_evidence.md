# Phase 10M-4 Evidence

Status: local evidence capture in progress; implementation, completion-record,
and queue-archive exact-SHA CI are not yet recorded.

Evidence is retained under:

`docs/phase10m/evidence/phase10m4_artifact_gallery_viewers/`

## Current Local Evidence

The current browser runner passes Chromium, Firefox, WebKit, and Chromium
390x844. It verifies metadata-first loading, exact renderer activation for
Dataset, regression, Composition, Structure, Trajectory, Phonon, BZ,
Volumetric, and generic metrics, inert legacy/HTML behavior, zero console/page
errors, zero external requests, one active heavy canvas, Chromium context-loss
recovery, 50 Chromium heavy-panel cycles, exact Artifact-to-Evidence and
Artifact-to-Provenance navigation in all three desktop browsers, and honest
partial-result isolation with successful Artifacts still usable.

Focused checks already recorded during implementation include Workspace tests,
renderer registry, payload loader, Gallery shell, generic plot, heavy viewer,
selection runtime, specialized scientific viewers, TypeScript typecheck, and
build-oriented checks. These local results are supporting evidence only until
the implementation commit is fixed and exact-SHA CI passes.

The service-backed test now exercises PostgreSQL Workspace/Job/Artifact
metadata with Redis and MinIO, HTTP Artifact content retrieval, exact length
and SHA headers, same-Job scope, cross-Job/Project rejection, and tamper
rejection. Local service execution remains unavailable when the integration
environment is absent; `CI_SERVICE_BACKED = PASS` and `SERVICE_TESTS_SKIPPED =
0` must not be claimed before exact-SHA CI.

## Evidence Integrity

The evidence manifest hashes LF-normalized text and raw PNG bytes. Its pytest
checker requires exact membership, hashes, browser metrics, acceptance IDs,
security markers, DeepSeek policy, screenshot inventory, and absence of key,
Authorization, raw environment, private path, bucket credential, or unbounded
Artifact payload material.

## LLM Record

```text
NEW_LLM_CALL_SITES = 0
M4_VIEWERS_REQUIRE_LLM = NO
REAL_LLM_CALLS = 0
DEEPSEEK_POLICY_REGRESSION = PASS_LOCAL
```

M4 renders persisted scientific Artifacts. It neither needs nor performs a
real DeepSeek request.
