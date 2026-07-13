# Phase 10G-3 Trajectory Evidence

Evidence is stored in `docs/phase10g/evidence/phase10g3_trajectory_performance_browser/`.

`scripts/generate_phase10g3_trajectory_product_evidence.py` executes the real parser, Mock Planner, PlanValidator, persisted planner job, QueueWorkerRuntime, formal adapter, artifact persistence/listing, and canonical validators. It captures fixed, 64-frame, variable-lattice, degraded, refused, and invalid jobs. Dynamic IDs/timestamps are normalized only in the evidence serialization.

`apps/web/test/trajectory-performance-browser-evidence.mjs` replays those captures through the production PlannerWorkbench and drives real Chromium, Firefox, WebKit, and mobile contexts. It records API/product identity, playback stress, rapid seek, cache/pending/GPU metrics, variable lattice, supercell, picking/measurement, context loss/retry, artifact switching, accessibility, viewport behavior, screenshots, console/network security, and SHA-256 hashes.

The capture boundary is explicit: backend artifact generation is real in-memory persisted runtime execution; browser HTTP is a local replay of those captures. The separate service-backed CI test covers PostgreSQL/Redis/MinIO persistence.

Markers:

- `TRAJECTORY_FORMAL_API_EVIDENCE_PASS`
- `TRAJECTORY_PERFORMANCE_BROWSER_EVIDENCE_PASS`
- `TRAJECTORY_MOBILE_PERFORMANCE_EVIDENCE_PASS`
- `TRAJECTORY_PERFORMANCE_EVIDENCE_INTEGRITY_PASS`
- `NO_EXTERNAL_NETWORK_REQUESTS`
- `NO_SECRET_PATTERN_HITS`

## Local Verification Summary

Recorded on 2026-07-14:

- trajectory frontend: 30 passed;
- Phase 10G/G1/G3 plus registry backend group: 67 passed;
- full frontend: 146 passed;
- full backend: 434 passed, 23 skipped;
- Phase 10 closure backend: 3 passed, 2 integration tests deselected by the local closure command;
- production build, typecheck, lock check, dependency tree, G2 browser replay, G3 browser matrix, Phase 10 browser closure, and both evidence-integrity checks: passed;
- local service-backed PostgreSQL/Redis/MinIO run: unavailable because Docker CLI and local MinIO were absent; the current-HEAD CI integration job remains the required zero-skip closure;
- `npm audit`: unavailable because the configured npmmirror audit endpoint returned 404 `NOT_IMPLEMENTED`; no clean audit result is claimed.
