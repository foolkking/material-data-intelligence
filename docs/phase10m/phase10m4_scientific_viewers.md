# Phase 10M-4 Scientific Viewer Integration

Status: local implementation in progress; exact-SHA CI and service-backed
closure are pending.

## Integration Matrix

| Product | Current Workspace integration | Scientific authority | Selection output |
| --- | --- | --- | --- |
| Dataset Materials Explorer | `PRODUCTION_ADAPTED_RENDERER` over exact K2 product contract | persisted backend product values | exact dataset sample and whole Artifact |
| Materials ML | `PRODUCTION_ADAPTED_RENDERER` over exact K3 regression, uncertainty, or classification contract | persisted metrics and diagnostics | whole Artifact; sample identity is consumed when formally present |
| Composition Space | `PRODUCTION_ADAPTED_RENDERER` over exact K4 product contract | persisted PCA/clustering/product coordinates | exact dataset sample and whole Artifact |
| Structure | `PRODUCTION_ADAPTED_RENDERER` using the existing application-owned viewer | validated structure scene | whole Artifact; site/atom output is not fabricated |
| Trajectory | `PRODUCTION_ADAPTED_RENDERER` using the existing trajectory viewer | validated persisted frames and topology | whole Artifact; frame/atom output remains unavailable unless formal IDs exist |
| Phonon band/DOS/combined | `PRODUCTION_ADAPTED_RENDERER` using existing Plotly/table views | persisted phonon products | whole Artifact; q-point/branch output is not inferred from plot index |
| Phonon animation | `PRODUCTION_ADAPTED_RENDERER` using the existing animation viewer | persisted mode package | whole Artifact |
| Brillouin zone | `PRODUCTION_ADAPTED_RENDERER` using the existing BZ renderer | persisted reciprocal cell/path | whole Artifact; no label-only point emitter |
| Volumetric | `PRODUCTION_ADAPTED_RENDERER` using existing isosurface/slice/direct-volume surfaces | persisted field/grid/payload products | whole Artifact; field identity is consumed only when exact |
| Generic table/plot/text/JSON | bounded application-owned fallback | persisted values only | whole Artifact where declared |

There are no M4 `PRODUCTION_NATIVE_RENDERER` entries. Existing specialized
components are adapted behind the Workspace registry so the registry remains
the single contract-to-component authority. `CONSUMER_ONLY`, `METADATA_ONLY`,
`INERT_FALLBACK`, and `UNSUPPORTED` remain truthful states rather than being
promoted to interactive scientific support.

## Scientific Boundaries

Dataset, ML, and Composition components consume already-produced summaries,
metrics, coordinates, labels, and sample identities. They do not recompute
profiles, distributions, MAE/RMSE/R2, uncertainty bins, positive classes, PCA,
or clusters.

Structure, trajectory, phonon, Brillouin-zone, and volumetric components reuse
their existing validated mappers and application-owned renderers. M4 adds no
CrystalNN/VoronoiNN, bonds or coordination authority, RDF/MSD/diffusion,
phonon solver, reciprocal path generation, Bader analysis, field feature
extraction, or electronic Band/DOS capability.

Plots accept only allowlisted backend-produced traces. Histogram construction
is deliberately refused in the generic renderer because client-side binning
would create a second scientific authority. Every chart or WebGL view retains
a bounded text/table or metadata fallback.

## Partial and Legacy Behavior

Bundle loading is exact ToolCall-scoped and contract-bounded. A missing member,
wrong checksum, unsupported version, stale source, or over-cap payload yields a
typed viewer state. It does not substitute a same-named Artifact, select a
latest version, or modify Job/ToolCall/Workspace state. Successful sibling
artifacts remain available when another branch failed or was blocked.
