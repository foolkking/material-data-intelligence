# Phase 10M-4 Completion State

Status: `IN_PROGRESS / AWAITING IMPLEMENTATION COMMIT AND EXACT-SHA CI`.

The local implementation includes the typed renderer registry, metadata-first
Artifact Gallery, active-only checksum-validating loader, generic safe
fallbacks, existing Dataset/ML/Composition/Structure/Trajectory/Phonon/BZ/
Volumetric integrations, M3 selection reuse, one-active-heavy-viewer control,
WebGL cleanup/context-loss handling, focused tests, and real browser replay.

The following gates remain open and are not claimed complete by this record:

* run full backend/frontend/typecheck/build and regression gates on the final
  implementation tree;
* obtain PostgreSQL/Redis/MinIO zero-skipped service-backed proof;
* commit and verify implementation exact-SHA CI;
* append the permanent result only after implementation CI;
* verify completion-record exact-SHA CI;
* archive the queue task and verify archive exact-SHA CI.

M4 has no migration, database schema, dependency, lockfile, shared Workspace
contract, selection contract, scientific Adapter/algorithm, or LLM call-site
change. `REAL_LLM_CALLS = 0`; future real calls remain DeepSeek-only through
`DEEPSEEK_KEY`.

Phase 10M-5 remains `REVIEWER_GATE / AWAITING REVIEWER PROMPT`. No M5
executable task is created or implied by this in-progress document.
