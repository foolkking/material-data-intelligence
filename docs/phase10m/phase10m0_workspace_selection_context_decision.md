# Phase 10M-0 Workspace Selection Context Decision

Status: REVIEWER-SEALED RECOMMENDATION
Contract target: `WorkspaceSelectionContext 1.0`

```text
WORKSPACE_SELECTION_CONTEXT_REQUIRED = YES
```

## Decision

A formal exact selection contract is required. It carries one primary selection and up to 16 secondary selections of the same compatible kind.

Supported kinds are:

- dataset sample and material object;
- structure and periodic site/atom;
- trajectory atom and frame;
- phonon q-point and branch;
- reciprocal point;
- volumetric field;
- Artifact;
- ScientificEvidenceItem;
- ScientificClaim.

Each ref contains the required fields in this fixed matrix:

| Selection kind | Required fields | Optional fields | Forbidden fields |
| --- | --- | --- | --- |
| `DATASET_SAMPLE` | projectId, datasetId, datasetVersion, objectId, sampleRef | artifactId/checksum | row index as identity |
| `MATERIAL_OBJECT` | projectId, datasetId, datasetVersion, objectId | sampleRef, artifactId/checksum | display label |
| `STRUCTURE` | projectId, datasetId, datasetVersion, objectId, structureId | artifactId/checksum | array position |
| `PERIODIC_SITE` | projectId, datasetId, datasetVersion, objectId, structureId, siteId | atom index as display metadata, artifactId/checksum | row order |
| `TRAJECTORY_ATOM` | projectId, datasetId, datasetVersion, trajectoryId, atomId | artifactId/checksum | frame index as atom identity |
| `TRAJECTORY_FRAME` | projectId, datasetId, datasetVersion, trajectoryId, frameId | artifactId/checksum | timestamp-only identity |
| `PHONON_Q_POINT` | projectId, datasetId, datasetVersion, phononArtifactId, artifactChecksum, qPointId | branchId | array index-only identity |
| `PHONON_BRANCH` | projectId, datasetId, datasetVersion, phononArtifactId, artifactChecksum, branchId | qPointId | display label |
| `RECIPROCAL_POINT` | projectId, datasetId, datasetVersion, reciprocalArtifactId, artifactChecksum, reciprocalPointId | segmentId | coordinate-only fuzzy identity |
| `VOLUMETRIC_FIELD` | projectId, datasetId, datasetVersion, fieldId, artifactId, artifactChecksum | regionId | voxel position-only identity |
| `ARTIFACT` | projectId, jobId, artifactId, artifactChecksum, artifactContract, artifactVersion | toolCallId | filename/path |
| `EVIDENCE_ITEM` | projectId, jobId, bundleId, bundleHash, evidenceItemId, sourceArtifactId, sourceArtifactChecksum, fieldLocator | claimId | provider-created locator |
| `CLAIM` | projectId, jobId, interpretationId, interpretationHash, claimId | evidenceItemId | rendered text as identity |

All refs additionally require `selectionSchemaVersion = "1.0"` and a source-scope hash. Position-only refs are invalid.

## Propagation

Panels subscribe by exact accepted selection kinds. A mapping is permitted only when a checked-in artifact/identity contract supplies the exact shared identity. Incompatible panels keep their current view and show `NOT_APPLICABLE` in the inspector; they never fuzzy-map labels, order, units, coordinates, or nearby values.

Clearing primary selection clears dependent secondaries. Selecting a new resource scope replaces the entire context. Multi-selection is same-kind and same-resource-version only. Stale, deleted, foreign-project, or unsupported refs are rejected and displayed as stale deep-link diagnostics.

## Persistence

- Server: the last explicitly pinned context.
- URL: active context for a shareable deep link, maximum 2,048 encoded bytes.
- React memory: transient hover and playback selections.
- Artifact arrays, row indexes, labels, and renderer-local object handles are never persisted as canonical selections.

## Security and compatibility

Selection does not grant artifact access. Every panel request rechecks project and source ownership. Historical artifacts lacking canonical IDs remain selectable only as whole artifacts; element/site/q-point mapping is disabled instead of guessed.
