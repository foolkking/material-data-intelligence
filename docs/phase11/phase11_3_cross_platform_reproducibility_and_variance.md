# Phase 11-3 Cross-Platform Reproducibility and Variance

Phase 11-3 replays only the eight `PASS_INVARIANT` cases admitted by the sealed Phase 11-2 handoff. Scientific truth remains the Phase 11-1 reference plus the Phase 11-2 comparison; neither Linux nor Windows is a truth source.

The validation-only runner verifies source identity, fixture checksum, tolerance identity, unit semantics, invariant status, and canonical output hash under the same `uv.lock`. Linux and Windows must each pass the reference contract before cross-platform variance is classified. The handoff contains no numeric expected values, so numeric cross-platform comparison is explicitly not applicable and no V4 promotion is made.

`EXACT`, `TOLERANCE_BOUNDED`, `DISPLAY_ONLY_VARIANCE`, `UNSUPPORTED_PLATFORM`, and `KNOWN_LIMITATION` retain their sealed meanings. Browser rendering may vary only at the display layer; browser, screenshot, and service evidence have no numeric scientific authority.

The implementation adds validation-only CI jobs and evidence tooling. Production science, Registry 62, DataProfile 2.4, AnalysisPlan, Artifact families, database schema, migration 0007, APIs, dependencies, and lockfiles remain unchanged.

