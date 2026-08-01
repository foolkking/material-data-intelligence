# Phase 10M-1 Workspace Domain Contract

Status: current M1 implementation contract. Corrected implementation exact-SHA
CI and service-backed evidence pass; completion-record and queue-archive CI are
still required before archive.

## Scope

M1 adds the contracts and persistence boundary for a first-class Workspace
that organizes one existing Job. It does not add the Workspace page, panel
renderers, cross-panel selection propagation, Report/Recipe composition, or
any execution authority.

The current implementation is in:

- `packages/schemas/mdi_schemas/workspace.py`
- `packages/schemas/json/workspace-v1.schema.json`
- `packages/schemas/src/index.ts`

## ScientificWorkspace 1.0

`ScientificWorkspace` is bound to `(projectId, sourceJobId)` and has a
deterministic Workspace identity. Its immutable source projection includes
the dataset/version when available, DataProfile and Intent identities and
hashes, and AnalysisPlan identity, hash, and schema version. The source
reference hash is computed from those immutable fields.

Durable mutable state is limited to the title, active panel, pinned exact
selection, bounded durable metadata, and the current revision pointer. The
contract exposes projected status, read-only/historical flags, warnings,
diagnostics, bounded source counts, and explicit `executionAuthorized=false`
and `scientificAuthority=false` markers.

The Workspace stores references and metadata only. It does not copy Artifact
payloads, scientific values, evidence facts, provider text, credentials, or
storage paths. Job, Plan, Artifact, Interpretation, Report, and Recipe remain
the authorities for their own records.

## WorkspacePanel 1.0

Panels are strict descriptors, not UI components. A panel contains a stable
panel ID, kind, title, Workspace membership, exact source references and
hashes, allowlisted renderer contract, projected state, selection declarations,
evidence/provenance references, bounded layout metadata, accessibility text,
and inert unsupported-state information. Panel state and source-reference
hashes are deterministic.

The current allowlist includes overview, data, plan, execution,
artifact-metadata, findings, evidence, provenance, report, and inert-fallback
contracts. A Workspace is capped at 32 panels. Unsupported or unsafe source
artifacts become typed inert fallback descriptors; they do not become ready
scientific panels.

## WorkspaceSelectionContext 1.0

Selection is an exact, versioned value object. It uses stable identity fields,
source scope hashes, a primary selection and at most 16 same-scope secondary
selections. Propagation is `EXACT_COMPATIBLE_ONLY`; it is not a server-side
Workspace state authority in M1.

Validation rejects display labels, array-position identity, fuzzy matching,
latest-version rebinding, unit guessing, arbitrary URLs/paths, prompt text,
payloads, executable expressions, duplicate identities, cross-project
selections, and incompatible resource versions. Selection URL encoding is
bounded to 2,048 bytes and uses the strict contract codec.

## Validation and identity

All three contracts use strict unknown-field rejection, allowlisted enums,
bounded strings and arrays, finite values, prototype-key rejection, bounded
JSON depth, deterministic canonical JSON, and SHA-256 semantic identities
where the contract requires them. The checked-in JSON Schema and TypeScript
contract are intended to remain parity fixtures for the Python models.

## Current verification state

Contract and focused persistence/projection tests are present in
`tests/test_phase10m1_workspace_contracts.py`,
`tests/test_phase10m1_workspace_persistence.py`, and
`tests/test_phase10m1_workspace_projection_api.py`. Full local regression,
browser regression, evidence manifest verification, and corrected exact-SHA
CI pass. PostgreSQL/Redis/MinIO reports `37 passed, 0 skipped, 0 failed, 0
errors`.

`REAL_LLM_CALLS = 0`. M1 does not call DeepSeek or any other LLM.
