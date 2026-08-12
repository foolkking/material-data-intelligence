# Phase 13-1 Integration Fix-Forward #5

Status: `BLOCKED / DEMO5_INITIAL_RELEASE_ENTRY_AUTHORITY_CONFLICT`.

`P13-R5-001` was traced to a dataset-version identity mismatch. Intent and
Eligibility use `DataProfile.version` when `sampleIdentity` is not applicable,
but Workspace projection did not use that fallback. The bounded correction
aligns the comparator and verifies the immutable Workspace snapshot against the
exact execution source. Focused Workspace/Report tests pass `29/29`; the fresh
Demo 4 product smoke was not executed after the Branch C stop, so the full
finding closure gate is not claimed.

`P13-R5-002` selected Branch C. Direct phonon JSON upload remains Phase 11
`MAPPING_ONLY`, and the repository has no normal-user-visible supported action
that creates or selects exact `PhononBand` and `PhononDos` resources. Internal
normalized mappers, test constructors, runtime resolvers and registered
Adapters do not constitute product input support. No input support was
promoted, no Demo 5 smoke was run, and Attempt 6 remains unauthorized.

