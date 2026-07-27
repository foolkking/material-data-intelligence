# Phase 10K Implementation Sequence

This sequence freezes ownership and dependency order. It does not register new
tools or implement product behavior.

## 1. Principles

1. The deterministic profile is the fact source for material-intelligence
   eligibility.
2. A manifest entry is not READY until registry, adapter, validator, runtime,
   artifacts, tests, and user surface close.
3. Sample identity and property semantics precede linked plots and outliers.
4. Existing adapters are reused where their contracts are scientifically
   adequate; product bundles compose them without duplicating metric tools.
5. Truncation, sampling, approximation, and unavailable analysis must be explicit.
6. Phase 10K produces deterministic summaries. LLM interpretation remains 10L.
7. The Phase 9C layout and server-side execution boundary remain unchanged.

## 2. Phase 10K-1: Material Data Profile 2.0

### Scope

- evolve the cross-language profile contract with additive/versioned migration;
- align Python and TypeScript dataset kinds;
- add deterministic capabilities and available/unavailable analyses;
- represent table roles, material properties, units, model tasks, uncertainty,
  classification, structures, trajectories, phonons, and volumetric resources;
- introduce stable bounded sample references;
- expose typed quality issues, confidence/provenance, and limitation reasons;
- persist and return the real profile through existing API/repository paths;
- present the richer profile in the existing data-context surface.

### Reuse

Parser normalized objects, repositories, Phase 2 APIs, `FormatAdaptiveProfile`,
and existing profile generation tests.

### Exclusions

No dataset explorer, ML plots, clustering, capability-aware Planner, LLM
interpretation, workspace redesign, or professional science.

## 3. Phase 10K-2: Dataset Materials Explorer

### Scope

- bounded overview of formulas, elements, chemical systems, properties, and
  available structure statistics;
- deterministic dataset comparison and train/test comparison when split identity
  exists;
- exact duplicate analysis and carefully scoped near-duplicate policy;
- data-quality and outlier candidate tables with stable sample references;
- Plotly/table/summary/recipe artifacts and responsive result surfaces.

### Reuse

Existing table summaries, composition adapters, lightweight structure adapters,
Plotly preview, artifact storage, and recipe/report infrastructure.

### Tool granularity

Keep atomic tools reusable. Add a product-oriented dataset overview capability
only if it removes repeated orchestration and has a strict bounded contract.
Candidate identifiers in this document are illustrative, not registered.

## 4. Phase 10K-3: Materials ML Evaluation

### Scope

- complete regression evaluation with parity, residual, distribution, metric,
  chemistry-conditioned, outlier, and comparison views;
- uncertainty calibration, error filtering, and high-uncertainty inspection when
  uncertainty exists;
- classification metrics, confusion matrix, ROC/PR only when labels and scores
  satisfy the profile contract;
- explicit constant-target, missing-data, class-count, and insufficient-sample
  behavior;
- stable sample/model/split binding across every artifact.

### Reuse

Existing basic metrics, error distribution, outlier, density-scatter adapters,
generic Plotly/table outputs, and profile roles.

### Tool granularity

Do not create one public tool per scalar metric. Prefer bounded evaluation
products with typed views while retaining atomic adapters where independent use
is meaningful.

## 5. Phase 10K-4: Composition Space / Embedding / Clustering

### Scope

- deterministic element-fraction vectors with explicit element ordering;
- bounded PCA with variance/projection metadata;
- one reviewed bounded clustering method if justified by repository dependencies;
- property/cluster coloring, cluster table, outlier candidates, and linked stable
  sample inspection;
- deterministic replay and numerical reference tests.

### Dependency policy

NumPy/SciPy are available. Scikit-learn is currently transitive rather than a
declared direct dependency. Implementation must either declare ownership through
normal dependency review or use a bounded application-owned numerical path.
UMAP is not required and no large dependency is approved by this audit.

## 6. Phase 10K-5: Integration / Evidence

Close the real flow:

```text
upload/select
-> deterministic profile
-> eligible material-intelligence capability
-> validated plan/tool execution
-> artifacts/recipe/report
-> browser product surface
```

Evidence must cover representative composition datasets, structures, regression,
uncertainty, classification where supported, composition space, unavailable
analysis, caps, browser/mobile/accessibility, API/service-backed execution,
network isolation, secrets, and current-HEAD CI.

## 7. Recommended Architecture Boundary

Phase 10K should introduce an application-owned capability vocabulary and stable
sample/property/model identities in schemas. It should not make the browser an
execution authority. Tool selection remains Registry-validated, long operations
remain queued, and artifacts remain inert.

Product surfaces should be added to the existing active results workspace before
Phase 10M. Phase 10M, not Phase 10K, owns the final unified navigation and
cross-artifact workspace contract.

## 8. Caps to Freeze During Implementation

Each implementation phase must choose, document, and test exact limits for:

- rows, columns, strings, categories, and profile bytes;
- properties, roles, datasets, splits, models, and classes;
- plot points, table rows, histogram bins, and outliers;
- composition elements, embedding samples/features/components, and clustering
  work;
- warning counts and serialized artifact sizes.

The implementation must reject or explicitly warn on truncation. This audit does
not change existing caps or invent untested values.

## 9. Test Strategy

- schema parity and migration tests in Python and TypeScript;
- parser-to-profile tests for each actually supported input domain;
- tool registry-to-adapter closure tests;
- deterministic numerical references and malformed-input security tests;
- component tests for profile and product states;
- real API/service-backed integration;
- browser evidence on desktop/mobile with accessibility and no external network;
- full repository regression and exact-SHA CI for each phase.
