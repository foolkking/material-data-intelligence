# Phase 10M-0 Workspace Domain Contract Proposal

Status: REVIEWER-SEALED RECOMMENDATION
Contract target: `ScientificWorkspace 1.0`

## Entity and cardinality

```text
WORKSPACE_IS_FIRST_CLASS_PERSISTED_ENTITY = YES
WORKSPACE_CARDINALITY = ONE_WORKSPACE_PER_JOB
```

A Workspace is the recoverable, user-facing projection of one exact Job and its immutable analysis lineage. Job remains execution authority; Workspace owns navigation, layout, panel visibility, title, and pinned exact selection only.

## Source authority

Workspace stores references to Project, Dataset/version, DataProfile, Intent, EligibilityResolution, SelectionDecision, AnalysisPlan, Job, ToolCalls, Artifacts, execution records, interpretations, reports, and recipes. It does not copy dataset rows, artifact payloads, evidence bundles, plan JSON, provider payloads, or scientific values. ArtifactStorage and the existing repositories remain scientific authority.

## `ScientificWorkspace 1.0`

Required immutable fields:

- `workspaceId`, `schemaVersion`, `projectId`, `sourceJobId`;
- nullable exact `datasetId`, `datasetVersion`, `profileId`, `profileSemanticHash`, `intentId`, `intentSemanticHash`, `planId`, `planHash`, `planSchemaVersion` for legacy projection;
- `createdAt`, `createdByKind`, and deterministic source-reference hash.

Mutable user-owned fields:

- bounded title;
- active panel ID;
- ordered panel visibility records;
- bounded layout metadata;
- validated pinned `WorkspaceSelectionContext 1.0`;
- optimistic `revision` and `updatedAt`.

Derived-only fields:

- projected Workspace status;
- source availability and staleness;
- panel result states;
- artifact, ToolCall, finding, evidence, report, and recipe counts;
- integrity diagnostics and available commands.

Runtime-owned scientific fields remain in current records and cannot be changed through Workspace APIs.

## Status

Workspace status is a projected composite derived from Job status, DependencyExecutionRecord, source availability, contract support, and integrity. It is not a mutable database enum on the Workspace row. The projection uses the taxonomy in `phase10m0_state_and_error_taxonomy.md`.

## Historical jobs

Opening an eligible historical Job performs idempotent lazy projection:

- exact modern identity chain: a normal Workspace is created;
- missing Profile/Intent/Plan identity: `LEGACY_READ_ONLY` Workspace with no inferred identity;
- missing source Job: creation rejected;
- foreign-project source: authorization rejection;
- unsupported plan/artifact schema: Workspace opens read-only with panel-level `CONTRACT_UNSUPPORTED`.

There is no bulk scientific backfill and no reinterpretation of historical list order, labels, or hashes.

## Deletion and staleness

- Deleted dataset/resource: preserve Workspace tombstone; affected panels become `SOURCE_DELETED`.
- Changed Profile or dataset version: retain exact historical binding and show `STALE`; never remap.
- Missing artifact: affected panel becomes `SOURCE_MISSING`; other panels remain usable.
- Removed Job: Workspace remains an audit tombstone with `SOURCE_MISSING` and no scientific payload.
- Missing interpretation: Findings becomes `READY_NOT_RUN` or `UNAVAILABLE`, according to source terminal state.
- Unsupported schema: read-only inert fallback with `CONTRACT_UNSUPPORTED`.

## Caps

- 32 panels per Workspace;
- 128 layout revisions retained per Workspace;
- one primary and 16 secondary selection refs;
- 2,048-byte URL selection token;
- 131,072-byte mutable Workspace request;
- 524,288-byte metadata-first Workspace snapshot before lazy panel payloads.

Cap overflow is typed rejection; no semantic truncation is permitted.

## Deletion seal

Physical deletion of a Project, Job, Dataset, or Workspace referenced by a
Workspace is rejected with `SOURCE_REFERENCED`. Existing source repositories
retain the source row and expose its deletion/tombstone state to the
projection. The Workspace source reference remains immutable and the panel
shows `SOURCE_MISSING` or `SOURCE_DELETED` according to the source record.
Workspace user deletion is not an M1 operation. This fixes the tombstone and
foreign-key relationship without adding a soft-delete column to existing
scientific records.

## Revision overflow seal

`workspace_layout_revisions` is append-only and retains at most 128 revisions.
Attempting revision 129 returns `REVISION_CAP_EXCEEDED`, leaves the last valid
revision active, and retains every prior revision. No oldest-revision deletion,
compaction, or silent archival is permitted in Phase 10M.
