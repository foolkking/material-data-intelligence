# Phase 10K-5 Material Intelligence Integration

Status: COMPLETE. Implementation exact-SHA CI run `30382233569` and
completion-record exact-SHA CI run `30382583135` passed; the verified queue
block is archived.

## Product Boundary

Phase 10K remains a set of independently executable, bounded products:

* Material Data Profile 2.0 is the deterministic data and semantic authority.
* `dataset.materials_explorer` presents dataset, composition, structure,
  property, quality, comparison, and stable-sample facts.
* `ml.regression_evaluation`, `ml.uncertainty_evaluation`, and
  `ml.classification_evaluation` evaluate explicit complete Profile groups.
* `dataset.composition_space` presents backend-computed atomic-fraction PCA,
  optional bounded KMeans, comparisons, and explicitly bound ML colors.

There is no `material_intelligence.all` tool and no multi-tool Planner feature.
Users may run one current product at a time. Phase 10L owns future selection and
bounded composition of tools.

## Integration Contract

Every current Phase 10K product carries the same application-owned binding:

```text
datasetId
datasetVersion
profileId
profileContractVersion == 2.0
semanticHash
datasetContentHash
resourceBindings[] = objectId + objectType + objectHash
```

The frontend validates this binding before linking products. Missing or
different fields produce `REJECTED` or `STALE`; a filename never enables a
capability. A product remains independently visible when a sibling is stale or
failed.

Stable material identity is `objectId:sampleRef`. Array position, display
sampling order, PCA coordinates, row ordering across resources, and React keys
are not scientific identity. K2 sample rows, K3 linked diagnostic rows, and K4
points all emit and validate the same `sampleKey`.

## Runtime Hardening

Queue execution resolves the exact persisted AnalysisPlan `profileId` for the
job dataset and rejects a mismatched dataset/Profile before tool execution.
Artifact input hashes now include complete deterministic DataFrame/Series and
Pydantic content, including explicit non-finite-value tokens.

Composition Space accepts only exact K3 regression/uncertainty v1 artifacts,
requires an exact current dataset/Profile/resource binding, validates bounded
sample collections, and preserves source units and coverage. It does not
recompute ML values.

Ambiguous Profile 2.0 ML intent cannot fall back to legacy basic metrics and
silently select a column. The deterministic Mock Planner exposes the Dataset
Explorer diagnostic state; the K3 adapter independently retains its typed
ambiguity rejection.

## Frontend

The Material Intelligence status surface combines Profile readiness with
validated artifacts and reports `PRODUCED`, `READY_NOT_RUN`, `UNAVAILABLE`,
`PROFILE_AUTHORITY_UNAVAILABLE`, `REJECTED`, `STALE`, or
`CAPABILITY_MISMATCH`. Endpoint refresh uses settled results, retaining the
last successful slices when one job endpoint fails.

All charts consume artifact values. The browser performs display formatting,
sorting, filtering, and interaction only; it does not calculate scientific
statistics, ML metrics, PCA, clusters, or chemistry groups.

## Explicit Limits

Phase 10K does not provide automatic analysis planning, automatic tool
combination, LLM scientific interpretation, the global Unified Workspace,
CrystalNN/VoronoiNN, experimental XRD comparison, trajectory MSD/diffusion, or
Electronic Band/DOS. These belong to the approved 10L-10N roadmap.
