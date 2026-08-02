# Phase 10M-4 Selection Integration

Status: local implementation in progress.

M4 reuses the M3 `WorkspaceSelectionContext 1.0` codec, Workspace-scoped store,
panel subscription registry, compatibility resolver, Inspector, and URL
authority. It does not create a Viewer-specific selection context or persist
ephemeral selection.

## Emitter Classification

| Renderer | Classification | Emitted identities | Consumed identities |
| --- | --- | --- | --- |
| Artifact Gallery / generic Artifact surface | `PRODUCTION_NATIVE_EMITTER` | `ARTIFACT` | `ARTIFACT` |
| Dataset Materials Explorer | `PRODUCTION_ADAPTED_EMITTER` | `DATASET_SAMPLE`, `ARTIFACT` | `DATASET_SAMPLE`, `MATERIAL_OBJECT`, `ARTIFACT` |
| Composition Space | `PRODUCTION_ADAPTED_EMITTER` | `DATASET_SAMPLE`, `ARTIFACT` | `DATASET_SAMPLE`, `MATERIAL_OBJECT`, `ARTIFACT` |
| Materials ML | `CONSUMER_ONLY` for sample identity; Artifact surface emits `ARTIFACT` | `ARTIFACT` | `DATASET_SAMPLE`, `MATERIAL_OBJECT`, `ARTIFACT` |
| Structure | `CONSUMER_ONLY` for structure/site/atom; Artifact surface emits `ARTIFACT` | `ARTIFACT` | `STRUCTURE`, `PERIODIC_SITE`, `ARTIFACT` |
| Trajectory | `CONSUMER_ONLY` for atom/frame; Artifact surface emits `ARTIFACT` | `ARTIFACT` | `TRAJECTORY_ATOM`, `TRAJECTORY_FRAME`, `ARTIFACT` |
| Phonon band/combined | `CONSUMER_ONLY` for q-point/branch; Artifact surface emits `ARTIFACT` | `ARTIFACT` | `PHONON_Q_POINT`, `PHONON_BRANCH`, `ARTIFACT` |
| Brillouin zone | `CONSUMER_ONLY` for reciprocal point; Artifact surface emits `ARTIFACT` | `ARTIFACT` | `RECIPROCAL_POINT`, `ARTIFACT` |
| Volumetric | `CONSUMER_ONLY` for field identity; Artifact surface emits `ARTIFACT` | `ARTIFACT` | `VOLUMETRIC_FIELD`, `ARTIFACT` |
| Metadata/download-only fallbacks | `NO_SELECTION_SUPPORT` unless the Gallery's exact Artifact action is used | none | none |

Sample emission uses exact `objectId + sampleRef + sampleKey`. Artifact
emission uses exact Artifact ID, checksum, contract/version, Job, Project, and
Workspace scope. Array positions, plot indices, DOM indices, labels, colors,
nearest coordinates, and fuzzy strings never become identity.

The M3 resolver alone decides whether a selection is compatible with another
panel. Opening a Gallery item changes the active panel/viewer but does not
silently clear, broaden, or latest-rebind an incompatible selection. Inspector,
Findings, Evidence, and Provenance navigation continues to use exact source
references. Dedicated claim/evidence link verification remains part of the M4
acceptance closure and must not be claimed complete before the final evidence
and exact-SHA CI gates pass.
