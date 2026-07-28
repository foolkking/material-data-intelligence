# Phase 10K-4 Composition Space Evidence

Evidence is stored at
`docs/phase10k/evidence/phase10k4_composition_space/`.

The evidence package records sanitized Profile/Planner/job/tool-call captures,
canonical composition-space/Plotly/summary/recipe artifacts, deterministic PCA
and KMeans fixtures, property and Phase 10K-3 sample-bound coloring, explicit
dataset comparison, negative/security cases, performance metrics, browser and
mobile captures, network/console audits, and SHA-256 integrity metadata.

The service-backed integration test uses the existing PostgreSQL, Redis, MinIO,
Planner, PlanValidator, and QueueWorkerRuntime path when the repository CI
environment enables it. Skipped local service tests remain skipped and are not
represented as passing service evidence.

Required markers:

```text
COMPOSITION_SPACE_RUNTIME_EVIDENCE_PASS
COMPOSITION_SPACE_PCA_EVIDENCE_PASS
COMPOSITION_SPACE_SAMPLE_LINKAGE_EVIDENCE_PASS
COMPOSITION_SPACE_PROPERTY_COLOR_EVIDENCE_PASS
COMPOSITION_SPACE_DATASET_COMPARISON_EVIDENCE_PASS
COMPOSITION_SPACE_CLUSTERING_EVIDENCE_PASS
COMPOSITION_SPACE_BROWSER_EVIDENCE_PASS
COMPOSITION_SPACE_PERFORMANCE_EVIDENCE_PASS
NO_COMPOSITION_SPACE_EXTERNAL_NETWORK_REQUESTS
NO_SECRET_PATTERN_HITS
```
