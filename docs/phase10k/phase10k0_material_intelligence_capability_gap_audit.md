# Phase 10K-0 Material Intelligence Capability Gap Audit

Status: audit complete; no Phase 10K product code is implemented by this record.

## 1. Decision Summary

The repository has a strong execution and scientific-visualization foundation,
but it does not yet provide a material-intelligence product for collections of
materials.

The current state is:

- `DataProfile 0.1`: **MINIMAL**. It provides a narrow table/structure summary,
  not capability discovery.
- dataset-level material intelligence: **REUSABLE_FOUNDATION**, not a product.
- materials ML evaluation: **PARTIAL** for basic regression only.
- composition-space analysis: **MISSING_INITIAL_RELEASE**.
- Planner: **PARTIAL_PROFILE_AWARE / MOSTLY_PROMPT_ROUTED**.
- frontend: **PlannerWorkbench plus generic artifacts**, not a dataset
  intelligence workspace.

Phase 10K should therefore proceed in the approved order: profile contract,
dataset explorer, ML evaluation, composition space, then integrated evidence.
Phase 10L owns capability-aware planning and interpretation. Phase 10M owns the
unified workspace. Phase 10N owns professional scientific completion.

## 2. Audit Method

This conclusion was derived from implementation, registry, tests, and browser
evidence rather than historical planning documents. The primary sources were:

- `packages/schemas/mdi_schemas/models.py`
- `packages/schemas/src/index.ts`
- `packages/material-parsers/mdi_material_parsers/`
- `packages/adapters/mdi_adapters/`
- `packages/tool-registry/mdi_tool_registry/loader.py`
- `tool_registry/platform_builtin_manifest.yaml`
- `services/llm/mdi_llm/providers.py`
- `apps/api/mdi_api/phase2_runtime.py`
- `apps/api/mdi_api/routers/planner.py`
- `apps/web/app/components/PlannerWorkbench.tsx`
- Phase 10A, 10B, and 10C tests and evidence

The presence of a manifest entry, library function, historical phase proposal,
or fixture alone was not counted as a working platform capability.

## 3. Input and Normalization Inventory

| Input | Real parser/normalizer | Profile coverage | Downstream state |
| --- | --- | --- | --- |
| CSV/table | Yes, pandas DataFrame | Basic columns, roles, counts | Generic table and basic regression tools |
| limited JSON table | Yes | Same basic table profile | Same as CSV |
| CIF | Yes, periodic Structure | Basic formula/elements/site counts | Structure tools and viewers |
| POSCAR/CONTCAR | Yes, periodic Structure | Basic formula/elements/site counts | Structure tools and viewers |
| XYZ | Yes, non-periodic ASE Atoms | Object retained; no useful domain summary | Not capability-discovered |
| EXTXYZ | Yes; periodic single structure or bounded trajectory | Trajectory metadata is not surfaced by profile | Trajectory product exists separately |
| canonical trajectory JSON | Yes in trajectory parser | Not surfaced by profile builder | Trajectory product exists separately |
| VASP volumetric files | Yes for approved CHGCAR/CHG/LOCPOT/ELFCAR/PARCHG paths | Volumetric metadata is not surfaced by profile | Volumetric products exist separately |
| CUBE | Yes, bounded | Volumetric metadata is not surfaced by profile | Volumetric products exist separately |
| phonon data | Approved canonical/phonopy-backed product inputs exist | No general material-parser/profile discovery path | Phonon products use explicit inputs/tests |
| model result table | Yes when represented as table columns | Narrow regression detection | Basic regression only |

Archive parsing is bounded by the existing ZIP limits, including file count,
uncompressed bytes, and nesting depth. Phase 10K must not broaden input-format
claims beyond the parsers that actually exist.

## 4. Current DataProfile Contract

The Python contract exposes identity, dataset type, file/object inventories,
optional structure/table/phonon/trajectory summaries, quality issues, recommended
tasks, and creation time. The TypeScript contract narrows `datasetType` to a
fixed union but omits volumetric data. This creates cross-language drift.

The builder currently derives useful content only from `Structure` and
`DataFrame` objects:

- structure summary: formula counts, elements, chemical systems, atom-count
  statistics, and a bounded resource list;
- table summary: row/column counts, inferred columns, and a narrow regression
  task inference;
- recommendations: a small structure/composition set or basic regression tools.

It does not turn trajectory, phonon, volumetric, ASE Atoms, uncertainty,
classification, model identity, property identity, or sample identity into
planner-visible capabilities.

### Semantic detection

Column-role inference uses exact lowercase aliases for formula, target,
prediction, uncertainty, and structure ID. Numeric-like columns are promoted
when a high percentage of non-null values parse as numbers.

Important gaps:

- `label` can become a target without classification semantics;
- class labels, class predictions, probabilities, and model identity have no
  canonical representation;
- common materials properties are not identified as scientific properties;
- structure density, lattice parameters, and space group are not surfaced in
  the profile;
- trajectory and volumetric metadata are discarded by the profile builder;
- no `detectedCapabilities`, `availableAnalyses`, or `unavailableAnalyses`
  contract exists;
- no stable row/sample identity supports cross-artifact inspection.

The current profile is deterministic apart from creation metadata and is safely
persisted, but it is not sufficient to drive the Phase 10K product.

## 5. Existing Executable Tool Surface

### Real reusable adapters

The runtime adapter registry contains working implementations for:

- table numeric and distribution summaries;
- generic scatter, histogram, and correlation plots;
- composition summary, formula statistics, element histogram, periodic-table
  heatmap, and chemical-system treemap/sunburst;
- regression basic metrics, error distribution, outlier table, and density
  scatter;
- structure summary, lattice summary, space-group summary, structure-derived
  composition, and preview metadata.

These are real foundations. They do not by themselves form the Dataset
Materials Explorer or a complete model-evaluation product.

### Manifest-only or planned identities

Several V1 identities are described in the platform manifest without a matching
runtime adapter class in the actual adapter registry, including parity,
uncertainty calibration, chemistry-conditioned errors, composition clustering,
and additional periodic-table plots. They are **PLANNED / NON_EXECUTABLE** for
this audit and must not be reported as current capability.

Manifest loading validates metadata shape but does not prove that a matching
adapter class is executable. Phase 10K implementation must add an explicit
registry-to-adapter closure test for any promoted product tool.

## 6. Dataset-Level Intelligence

Reusable pieces exist for formula parsing, element/chemical-system aggregation,
table distributions, correlation, and structure summaries. Missing initial
release behavior includes:

- one coherent dataset overview;
- property discovery and materials-aware distributions;
- dataset and train/test comparison;
- space-group, density, lattice, volume, and site-count collection analysis;
- deterministic duplicate and reliability-scoped near-duplicate analysis;
- stable sample selection linking tables, plots, structures, and outliers;
- explicit data-quality findings and unavailable-analysis reasons;
- bounded multi-resource aggregation and artifact contracts.

The current tools are useful atomic operations. The product gap is composition,
identity, contracts, and user-facing integration rather than absence of every
low-level calculation.

## 7. Materials ML Evaluation

Basic regression is real: MAE, RMSE, R-squared, signed error distributions,
density scatter, and largest-error rows. Current limitations include:

- no complete parity/residual product with shared sample identity;
- no chemistry-conditioned error analysis;
- no model comparison contract;
- no uncertainty calibration, filtering curve, or high-uncertainty inspection;
- no classification task contract, confusion matrix, ROC, PR, or class metrics;
- no explicit metric edge-case policy for constant targets and insufficient
  samples;
- outlier rows preserve values but not a canonical sample reference.

Phase 10K-3 must build on the existing regression adapters but cannot label the
current surface a complete evaluation suite.

## 8. Composition Space and Dependencies

Composition parsing and aggregate visualization are available. Vectorization,
projection, clustering, linked inspection, and outlier semantics are not.

The installed environment already contains NumPy and SciPy. Scikit-learn is
currently present transitively through pymatviz, not as a declared direct
project dependency. UMAP and matminer are not project dependencies. Historical
references to composition clustering do not establish a supported implementation
in the installed pymatviz version.

Phase 10K-4 should start with application-owned deterministic element-fraction
vectors and bounded PCA. Any use of scikit-learn must make dependency ownership
explicit at implementation time. UMAP or a large embedding dependency is not a
Phase 10K prerequisite.

## 9. Planner and Runtime Coupling

The API loads the real persisted profile for existing datasets, but its failure
fallback is a minimal synthetic profile. The mock provider selects tools through
ordered prompt markers and uses a few profile facts for column binding and input
eligibility. It is not a capability graph planner.

Classification:

```text
PARTIAL_PROFILE_AWARE / MOSTLY_PROMPT_ROUTED
```

Phase 10K may expose deterministic capability facts and improve truthful tool
eligibility. Capability-aware multi-tool planning and scientific interpretation
remain Phase 10L responsibilities. Phase 10K must not add arbitrary planning
loops or move execution into the browser.

## 10. Frontend and Product Surface

`PlannerWorkbench` provides dataset selection/upload, a format-adaptive profile,
plan execution, generic artifact display, and mature scientific product
renderers. It does not provide dedicated Dataset Overview, Composition,
Properties, Model Evaluation, Composition Space, or linked sample-inspection
surfaces.

The Phase 9C layout baseline remains binding. Phase 10K product UI should first
integrate bounded dataset-intelligence result surfaces into the existing active
workspace and artifact flow. A full workspace information architecture and
cross-artifact navigation model remain Phase 10M.

## 11. Artifact, Report, and Identity Gaps

Existing table, Plotly, metrics, summary, recipe, and report artifacts are
reusable. Queue execution and provenance boundaries are established. Missing
contracts include:

- stable dataset sample identity and selection reference;
- dataset overview and comparison payloads;
- property semantic metadata and units;
- model/task identity and split identity;
- uncertainty and classification payloads;
- composition vector/projection/cluster identity;
- product-level findings and limitation summaries.

Phase 10K should produce deterministic structured summaries and artifacts.
LLM-generated interpretation remains Phase 10L, and final report/workspace
productization remains Phase 10M.

## 12. Caps and Security Audit

Current declared limits include table/ML row caps, visualization point caps,
correlation-column bounds, structure caps, and archive-parser limits. Enforcement
is not uniform across all adapter implementations, and some truncation behavior
uses deterministic head selection rather than a shared sampling policy.

Phase 10K implementation must freeze and test:

- table row, column, string, and profile-metadata budgets;
- property and role candidate caps;
- plot/table preview caps and explicit truncation warnings;
- comparison dataset and model count caps;
- embedding sample, feature, component, and iteration caps;
- classification class-count and probability-column caps;
- uncertainty and outlier history/result caps;
- arithmetic overflow and non-finite rejection;
- no external data lookup, artifact code, or browser-side scientific execution.

Exact new limits are implementation decisions and are not fabricated by this
audit. Existing limits remain unchanged.

## 13. Historical Evidence Mapping

Phase 10A evidence proves generic table summaries and scatter/histogram/
correlation products. Phase 10B proves composition statistics and aggregate
composition plots. Phase 10C proves lightweight structure summaries. Later
phases prove individual structure, trajectory, phonon, reciprocal-space, and
volumetric products.

This evidence demonstrates reusable scientific capabilities, not a dataset
intelligence product. Phase 10K-5 must capture a real upload/select to profile to
dataset/ML/composition artifact flow without re-running unrelated GPU evidence.

## 14. Phase Boundary

Phase 10K owns deterministic material capability discovery and bounded dataset,
composition-space, and model-result analysis. It does not implement:

- capability-aware multi-tool planning or LLM findings (10L);
- unified workspace/cross-artifact productization (10M);
- CrystalNN, experimental XRD, trajectory analytics, or electronic Band/DOS
  (10N);
- Future or Not Planned scope.

No tool, schema, dependency, parser, Planner behavior, runtime behavior, or
frontend product was changed by Phase 10K-0.
