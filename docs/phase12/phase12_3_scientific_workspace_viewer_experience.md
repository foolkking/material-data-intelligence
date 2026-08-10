# Phase 12-3 Scientific Workspace + Scientific Viewer Experience

Status: implementation in progress; reviewer-authorized presentation change only.

Phase 12-3 closes `UX-002` and `UX-003`. The Workspace remains one persisted
Workspace per Job. This phase changes the visible hierarchy and shared viewer
framing while retaining server Workspace identity, exact panel URLs, Artifact
contracts, renderer registry, selection identity, lazy loading and scientific
payload authority.

The user-facing order is Overview, Data, Analysis, Results, Findings, Evidence
and Report. Plan and Execution are presentation children of Analysis; Provenance
and Developer details are Advanced disclosure. This is not a Workspace schema
or navigation-contract change.

Results lead with a persisted-result summary and a Result gallery. Artifact
identity, checksum, contract/version, source, Evidence and Lineage actions stay
available. Scientific viewer chrome supplies a stable title, state, warning,
focus and close surface; specialized controls and scientific series colors stay
owned by each existing renderer.

## Explicit Boundaries

`FRONTEND_SCIENTIFIC_RECOMPUTATION = 0`

`WORKSPACE_AUTHORITY_CHANGE = 0`

`ARTIFACT_CONTRACT_CHANGE = 0`

`SELECTION_IDENTITY_CHANGE = 0`

`NEW_PUBLIC_API_FAMILIES = 0`

`NEW_DEPENDENCIES = 0`

Evidence: `docs/phase12/evidence/phase12_3_scientific_workspace_viewers/`.
