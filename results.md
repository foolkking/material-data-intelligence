# Task Results

本文件按完成顺序保存 `TASKS.md` 中各任务的最终结果。只追加，不覆盖历史记录。

# Phase 10K-0 Material Intelligence Capability Gap Audit Result

## Status and Completion Time

* status: `PASS`
* completed: `2026-07-27 21:28:51 +08:00`

## Repository and Scope

* baseline: Gate J6-R completion HEAD `34c30c50631771209c90fca049fcff93a8a8bef9` on `master`, clean and equal to `origin/master`.
* task: documentation-only repository capability audit; no Phase 10K-1 implementation.
* audit commit: `cada6fbe473c213f3a05b8e7a8a879ea110ffc2d`.
* no source code, schema, parser, adapter, Tool Registry, Planner, PlanValidator,
  QueueWorkerRuntime, frontend product, dependency, or lockfile changed.

## Main Findings

* `DataProfile 0.1`: `MINIMAL`. It provides narrow table/structure summaries;
  it does not provide material capability discovery, stable sample identity,
  property/unit semantics, model-task semantics, or trajectory/phonon/volumetric
  discovery.
* semantic inference: exact/allowlisted table roles support formula and narrow
  regression/uncertainty aliases; classification and general materials-property
  recognition are missing.
* dataset surface: executable table, composition, and lightweight structure
  adapters are `REUSABLE_FOUNDATION`; they do not constitute a Dataset Materials
  Explorer.
* Materials ML: basic metrics, error distribution, outlier table, and density
  scatter are real; complete regression, uncertainty, classification, chemistry-
  conditioned errors, and model comparison remain Initial Release gaps.
* composition space: formula parsing and aggregate views are reusable;
  deterministic vectors, PCA, clustering, linked inspection, and outlier
  semantics are missing. NumPy/SciPy are available; scikit-learn is transitive;
  UMAP/matminer are not dependencies.
* Planner: `PARTIAL_PROFILE_AWARE / MOSTLY_PROMPT_ROUTED`; capability-aware
  multi-tool planning and interpretation remain Phase 10L.
* frontend: PlannerWorkbench and generic artifacts are reusable, but there is no
  product-level dataset intelligence experience. Unified workspace work remains
  Phase 10M.
* manifest-only V1 proposals without runtime adapter closure were not counted as
  implemented.

## Frozen Implementation Direction

* 10K-1: versioned Material Data Profile 2.0 capability and identity layer.
* 10K-2: bounded Dataset Materials Explorer using existing table/composition/
  structure foundations.
* 10K-3: data-gated regression, uncertainty, and classification evaluation.
* 10K-4: deterministic composition vectors, bounded PCA, reviewed clustering,
  property coloring, and linked inspection.
* 10K-5: real upload/profile/tool/artifact/frontend/report/recipe evidence.
* Future and Not Planned scope remains unqueued.

## Documentation

* audit: `docs/phase10k/phase10k0_material_intelligence_capability_gap_audit.md`
* gap matrix: `docs/phase10k/phase10k0_material_intelligence_gap_matrix.md`
* sequence: `docs/phase10k/phase10k0_phase10k_implementation_sequence.md`
* next scope: `docs/phase10k/phase10k1_next_scope.md`
* index and required persistent project-memory files were updated.

## Verification

* `git diff --check`: PASS.
* `uv lock --check`: PASS; 108 packages resolved, no dependency change.
* frontend: 48 test files / 294 tests PASS.
* typecheck: PASS.
* production build: PASS; `/` first-load JS 228 kB.
* backend: 760 passed, 24 skipped, 62 warnings. Skips remain explicit service-
  gated tests and were not reported as passed locally.
* Phase 10 evidence integrity: `PHASE10_CLOSURE_EVIDENCE_INTEGRITY_PASS`.
* docs links and TASKS structure/processing consistency: PASS.
* security: `NO_SECRET_PATTERN_HITS`; no network operation or real LLM was used
  by the audit.

## Commit / CI / Queue

* audit CI: run `30270323576`, exact SHA `cada6fb`, success.
* CI jobs: Unit Tests, Frontend Typecheck & Build, PostgreSQL/Redis/MinIO
  Service-backed Integration, and no-skipped assertion all succeeded.
* completion-record commit: `ab5a69a79ab5b4ac17357b3bcf8abb051c8f552d`.
* completion-record CI: run `30270636913`, exact SHA, success; Unit, Frontend,
  service-backed integration, and no-skipped assertion all succeeded.
* archive decision: the result, local checks, audit commit/CI, and completion
  record/CI are consistent; the complete 10K-0 task block may be removed.
* Phase 10K-0: `ARCHIVED_BY_VERIFIED_QUEUE_COMMIT`.
* Phase 10K-1: `NEXT / NOT_STARTED`; a complete prompt is now present in the
  user-maintained queue, superseding the earlier awaiting-prompt wording.

# Phase 10K-1 Material Data Profile 2.0 Result

## Status and Completion Time

* status: `PASS`
* completed: `2026-07-28 17:53:01 +08:00`

## Delivered Capability

* Extended the existing additive `DataProfile` contract (`schemaVersion=0.1`,
  `profileContractVersion=2.0`) instead of creating a parallel profile type.
* Added deterministic semantic facts for formula, approved material properties,
  stable sample identity, regression/multiple-model/multi-target/uncertainty,
  classification labels, and class probabilities.
* Used bounded authority levels and explicit model-series bindings. A generic
  uncertainty column is not silently assigned to multiple predictions.
* Added immutable table, composition/structure, trajectory, phonon, and
  volumetric resource semantics. Data readiness remains distinct from actual
  Registry-backed platform availability.
* Added deterministic semantic hashing, typed ambiguity/missing reasons,
  coverage disclosure, bounded inputs, API/persistence serialization, and a
  compact read-only profile surface in the existing frontend.

## Scope and Evidence

* No Dataset Explorer, ML evaluation product, embedding/clustering, capability-
  aware Planner behavior, Tool Registry entry, PlanValidator rule,
  QueueWorkerRuntime behavior, dependency, real LLM call, or external request
  was introduced.
* Real API, performance, and Chromium/Firefox/WebKit/mobile evidence is retained
  in `docs/phase10k/evidence/phase10k1_material_data_profile_2/`.
* Readiness: `READY_WITH_EXPLICIT_LIMITS`; semantic recognition is deterministic
  and bounded, while future analysis products remain correctly unavailable until
  their corresponding Registry-backed implementation phases.

## Verification

* focused profile/API/component tests: `41 passed`.
* full backend: `777 passed, 24 skipped, 62 warnings`; local skips were explicit
  service-gated cases and are not reported as passes.
* frontend: `48 files, 294 tests passed`; typecheck and production build passed.
* `uv lock --check`, `git diff --check`, Phase 10 closure/evidence integrity,
  API/performance evidence, and browser runners passed.
* markers: `MATERIAL_DATA_PROFILE_API_EVIDENCE_PASS`,
  `MATERIAL_DATA_PROFILE_PERFORMANCE_EVIDENCE_PASS`,
  `MATERIAL_PROFILE_BROWSER_EVIDENCE_PASS`,
  `MATERIAL_PROFILE_MOBILE_EVIDENCE_PASS`,
  `NO_MATERIAL_PROFILE_EXTERNAL_NETWORK_REQUESTS`, and
  `NO_SECRET_PATTERN_HITS`.

## Commit / CI / Queue

* implementation: `92a8e98b344b0a819954746f107e765f8f9cf6d2`; exact-SHA CI run
  `30346512968` succeeded, including service-backed integration and no-skipped.
* completion record: `b5a464e1c436f6f7a056511b1a0a6cfcc6cbcb19`; exact-SHA CI run
  `30346686652` succeeded for Unit Tests, Frontend Typecheck & Build, and
  PostgreSQL/Redis/MinIO service-backed integration with the no-skipped gate.
* archive decision: completion record, result, required checks, evidence, and
  both exact-SHA CI gates are consistent; the `Phase 10K-1` task block is
  eligible for verified queue archival.
* Phase 10K-1: `ARCHIVED_BY_VERIFIED_QUEUE_COMMIT`.
* Phase 10K-2: `NEXT / NOT_STARTED`.

# Phase 10K-2 Dataset Materials Explorer Result

## Status and Completion Time

* status: `PASS_PENDING_COMPLETION_RECORD_CI`
* completed: `2026-07-28 19:32:32 +08:00`

## Delivered Capability

* Added one validated product-level `dataset.materials_explorer` tool backed by
  exactly one Material Data Profile 2.0 and explicitly bound canonical table/
  Structure resources.
* Delivered deterministic dataset overview, element and chemical-system
  coverage, exact formula/Structure duplicate classes, canonical structure
  statistics, finite-only property distributions, factual data-quality output,
  explicit group/resource comparison, and stable sample links.
* Emitted one bounded inert `phase10k2.dataset_materials_explorer.v1` product
  bundle plus quality, summary, and recipe artifacts through persisted
  AnalysisPlan, PlanValidator, QueueWorkerRuntime, Registry, and Adapter.
* Added seven accessible responsive Results views: Overview, Composition,
  Structures, Properties, Data quality, Comparison, and Samples. Every
  chart-like view retains numeric/table content and inert JSON fallback.

## Scientific and Security Boundary

* Comparison requires explicit resource or group identity; row order never
  infers a split and unlike property units are not converted.
* Structure duplicates require equal canonical normalized hashes; reduced
  formula duplicates are separate and no near-duplicate, chemical-validity,
  significance, or anomaly authority is claimed.
* Hard caps cover 100,000 rows, 512 columns, 64 properties, 256 categories,
  200 linked rows, 100 bins, 256 structures, 5,000 atoms/structure, 128
  warnings, and 8,000,000 bytes/artifact.
* No dependency, arbitrary Python, notebook/script execution, real LLM,
  external request/asset, artifact JavaScript, ML evaluation, embedding,
  clustering, Agent automation, or workspace redesign was added.

## Evidence and Verification

* Real persisted Planner/job/runtime/API artifacts and Chromium/Firefox/WebKit
  plus 390x844 mobile replay are retained under
  `docs/phase10k/evidence/phase10k2_dataset_materials_explorer/`.
* Performance cases: 4, 5,000, and 100,000 rows; near-cap artifact remained
  bounded at about 24 KB and 100 linked sample rows.
* backend full: `791 passed, 24 skipped, 63 warnings`; skipped tests are explicit
  environment/real-LLM gates and were not reported as passed.
* backend non-integration: `791 passed, 1 skipped, 23 deselected`.
* frontend: `49 files, 300 tests passed`; typecheck and production build PASS.
* manifest/schema focused tests: `22 passed`; Phase 10 closure and evidence
  integrity PASS; `uv lock --check` and `git diff --check` PASS.
* markers: `DATASET_MATERIALS_EXPLORER_RUNTIME_EVIDENCE_PASS`,
  `DATASET_COMPOSITION_EXPLORER_EVIDENCE_PASS`,
  `DATASET_STRUCTURE_STATISTICS_EVIDENCE_PASS`,
  `DATASET_PROPERTY_EXPLORER_EVIDENCE_PASS`, `DATASET_QUALITY_EVIDENCE_PASS`,
  `DATASET_COMPARISON_EVIDENCE_PASS`,
  `DATASET_MATERIALS_EXPLORER_BROWSER_EVIDENCE_PASS`,
  `DATASET_MATERIALS_EXPLORER_PERFORMANCE_EVIDENCE_PASS`,
  `NO_DATASET_EXPLORER_EXTERNAL_NETWORK_REQUESTS`, and
  `NO_SECRET_PATTERN_HITS`.

## Commit / CI / Queue

* implementation commit: `1f495e14ccae72d8b22fa494ca8f6754bffb73d1`.
* cross-platform evidence fix/current implementation HEAD:
  `35c0fc6aa829fb8e9445c3a9d867883c1f10645e`.
* exact-SHA CI run `30355075439`: Unit Tests, Frontend Typecheck & Build,
  PostgreSQL/Redis/MinIO service-backed integration, and no-skipped assertion
  all succeeded.
* completion-record commit/CI: pending this record commit.
* Phase 10K-2 remains in `TASKS.md` until completion-record exact-SHA CI passes.
* Phase 10K-3 remains pending and was not implemented by this task.

## Phase 10K-2 Completion-Record CI and Queue Closure

* closure status: `PASS`
* completion-record commit: `8dc2545fd1f88bc63d6dc281643c96d43ab3679e`
* completion-record exact-SHA CI: run `30355282590`, success.
* CI jobs: Unit Tests, Frontend Typecheck & Build, and PostgreSQL/Redis/MinIO
  Service-backed Integration all succeeded; the integration no-skipped
  assertion succeeded.
* archive decision: the implementation commits, both exact-SHA CI runs,
  completion record, permanent result, required local checks, and retained
  evidence are consistent. The completed Phase 10K-2 task block is eligible
  for verified queue archival.
* Phase 10K-2: `ARCHIVED_BY_VERIFIED_QUEUE_COMMIT`.
* Phase 10K-3: `NEXT / NOT_STARTED`.

# Phase 10K-3 Materials ML Evaluation Result

## 1. Conclusion

`PASS`.

## 2. Baseline

* Phase 10K-2: archived after implementation `35c0fc6`, completion record
  `8dc2545`, and exact-SHA CI `30355282590`.
* initial HEAD: `4ae8afde126765367ad0a17aad1271a812cdf68f` on `master`, clean.
* current implementation/evidence-closure HEAD: `a1e05ee5b0f1affa91183e681b1678d4419cedc4`.

## 3. ML Product Architecture

* Profile 2.0 remains the only target/prediction/uncertainty/classification
  semantic authority. Three product tools bind one explicit canonical table and
  complete semantic task groups; artifacts retain dataset/profile/semantic hash
  and stable sample references.

## 4. Regression and Chemistry

* `ml.regression_evaluation` reports MAE, RMSE, defined-or-null R2, signed
  bias, fixed `prediction_minus_target` residuals, parity/residual/histogram
  data, high-error sample links, element-overlap error summaries, exact
  chemical-system summaries, and bounded common-valid-sample model comparison.

## 5. Uncertainty and Classification

* `ml.uncertainty_evaluation` provides source-defined uncertainty association,
  equal-count mean-uncertainty/mean-absolute-error bins, retained-lowest-
  uncertainty error decay, and linked high-uncertainty samples.
* `ml.classification_evaluation` provides raw confusion counts, support,
  accuracy, per-class/macro metrics with undefined values as null, linked
  misclassifications, and ROC/PR only for explicit binary positive classes with
  validated matching probabilities. Multiclass curves remain typed unavailable.

## 6. Runtime, Frontend, and Artifacts

* Mock Planner emits only explicit, profile-ready evaluation plans; existing
  PlanValidator and QueueWorkerRuntime authority is unchanged. Service-backed
  CI covers all three tools through persisted jobs, PostgreSQL, Redis, MinIO,
  and S3-compatible artifact retrieval.
* Results renders responsive numeric SVG/table panels and inert JSON fallback;
  Dataset Explorer exposes an availability-driven Model evaluation tab. Browser
  evidence covers Chromium, Firefox, WebKit, and 390x844 mobile.

## 7. Caps, Security, and Explicit Limits

* Caps: 100,000 rows, 16 models, 64 classes, 256 chemistry groups, 200 table
  rows, 10,000 plot points, 5,000 curve points, 50 uncertainty bins, 8 MB
  artifacts, and bounded time.
* No model training, AutoML, SHAP, feature-importance suite, PCA/UMAP,
  clustering, Agent interpretation, or workspace redesign was added. No
  arbitrary code, real LLM, artifact JavaScript, external assets, or runtime
  network authority was introduced.

## 8. Evidence and Checks

* Evidence: `docs/phase10k/evidence/phase10k3_materials_ml_evaluation/`;
  includes runtime/API captures, inert artifacts, 4/5,000/100,000-row metrics,
  browser/mobile screenshots, accessibility/network/security audits, and hashes.
* backend: `808 passed, 25 skipped, 63 warnings`; frontend: `50 files, 307
  tests passed`; typecheck/build, `uv lock --check`, `git diff --check`, focused
  evidence tests, Phase 10 closure integrity, trajectory evidence integrity,
  docs/TASKS checks, and K2/K3 browser runners passed.
* local service-backed: `UNAVAILABLE` (4 gated skips), not represented as pass.
  CI service-backed/no-skipped: success. `npm audit`: `UNAVAILABLE` because the
  configured npmmirror audit endpoint returns `404 NOT_IMPLEMENTED`; no
  dependency or lockfile changed.
* markers: `MATERIALS_ML_REGRESSION_RUNTIME_EVIDENCE_PASS`,
  `MATERIALS_ML_UNCERTAINTY_RUNTIME_EVIDENCE_PASS`,
  `MATERIALS_ML_CLASSIFICATION_RUNTIME_EVIDENCE_PASS`,
  `MATERIALS_ML_REGRESSION_BROWSER_EVIDENCE_PASS`,
  `MATERIALS_ML_CHEMISTRY_ERROR_EVIDENCE_PASS`,
  `MATERIALS_ML_UNCERTAINTY_BROWSER_EVIDENCE_PASS`,
  `MATERIALS_ML_CLASSIFICATION_BROWSER_EVIDENCE_PASS`,
  `MATERIALS_ML_PERFORMANCE_EVIDENCE_PASS`,
  `NO_MATERIALS_ML_EXTERNAL_NETWORK_REQUESTS`, and `NO_SECRET_PATTERN_HITS`.

## 9. Commit / CI / Queue

* implementation: `4574cef`; evidence-closure/current implementation:
  `a1e05ee5b0f1affa91183e681b1678d4419cedc4`; exact-SHA CI run `30363719393`
  passed Unit, Frontend Typecheck & Build, PostgreSQL/Redis/MinIO service-backed
  integration, and no-skipped assertion.
* completion record: `c5483d6f609ff21f9b7c06ce7bff88ec583d52c5`; exact-SHA CI
  run `30364098180` passed Unit, Frontend Typecheck & Build,
  PostgreSQL/Redis/MinIO service-backed integration, and no-skipped assertion.
* archive decision: implementation, completion record, retained result,
  required checks, retained evidence, and both exact-SHA CI gates are
  consistent. The verified task block is eligible for queue archival.
* queue after archive: Phase 10K-3 `ARCHIVED_BY_VERIFIED_QUEUE_COMMIT`; Phase
  10K-4 remains `NEXT / AWAITING COMPLETE PROMPT`; Phase 10K-5 remains planned
  and unstarted.

## 10. Next Phase

**Phase 10K-4：Composition Space / Embedding / Clustering**

## 11. Completion-Record CI and Queue Closure

* closure status: `PASS`.
* completion-record exact-SHA CI: `30364098180`, success for Unit, Frontend,
  service-backed integration, and the no-skipped assertion.
* archive eligibility: confirmed before deletion; results/evidence are retained
  permanently and only the complete K3 `---TASK---` block is removed.

# Phase 10K-4 Composition Space / Embedding / Clustering Result

## Status and Completion Time

* status: `PASS`
* completed: `2026-07-28 23:23:54 +08:00`

## Delivered Capability

* Added formal product-level `dataset.composition_space` over Material Data
  Profile 2.0 formula/property semantics and explicitly bound canonical table
  resources.
* Added atomic-number-ordered normalized atomic-fraction vectors, deterministic
  center-only two-dimensional PCA with stable sign convention, optional bounded
  KMeans in the original feature space, descriptive centroid-distance outlier
  candidates, and explicit group/resource comparison on one shared basis/PCA.
* Preserved stable `objectId + sampleRef` identity; Profile property colors and
  Phase 10K-3 error/uncertainty colors are sample-bound and never inferred from
  row order.
* Added an accessible responsive SVG/table Composition Space Explorer with
  linked inspection and inert JSON fallback. The frontend consumes backend
  coordinates and does not recalculate PCA or clustering.

## Scientific and Security Boundary

* Clusters and outliers are exploratory statistical summaries, not material
  families, invalidity proofs, or anomaly authority. No UMAP/t-SNE, learned
  embeddings, model training, scientific cluster naming, external service,
  arbitrary code, real LLM calculation, or Phase 10L behavior was added.
* Caps cover 100,000 resolved rows, 20,000 analyzed samples, 118 elements, 12
  clusters, 10,000 plot points, 1,000 retained table rows, bounded warnings,
  eight-megabyte artifacts, and strict timeout/parameter validation.

## Evidence and Verification

* Real Planner/job/runtime/API artifacts, deterministic hashes, property and K3
  ML coloring, explicit comparisons, rank/cap failures, Chromium/Firefox/WebKit
  and mobile replay, numeric fallback, screenshots, accessibility, performance,
  network, and security evidence are retained under
  `docs/phase10k/evidence/phase10k4_composition_space/`.
* K4 focused backend/evidence/manifest: `24 passed`; full backend: `826 passed,
  26 skipped, 63 warnings`. Skips are explicit environment/integration gates
  and are not represented as passes.
* frontend: `51 files, 314 tests passed`; typecheck and production build PASS.
  Ruff, `uv lock --check`, `git diff --check`, evidence integrity, and historical
  K1-K3 browser/evidence regression checks passed.
* required markers: `COMPOSITION_SPACE_RUNTIME_EVIDENCE_PASS`,
  `COMPOSITION_SPACE_PCA_EVIDENCE_PASS`,
  `COMPOSITION_SPACE_SAMPLE_LINKAGE_EVIDENCE_PASS`,
  `COMPOSITION_SPACE_PROPERTY_COLOR_EVIDENCE_PASS`,
  `COMPOSITION_SPACE_DATASET_COMPARISON_EVIDENCE_PASS`,
  `COMPOSITION_SPACE_CLUSTERING_EVIDENCE_PASS`,
  `COMPOSITION_SPACE_BROWSER_EVIDENCE_PASS`,
  `COMPOSITION_SPACE_PERFORMANCE_EVIDENCE_PASS`,
  `NO_COMPOSITION_SPACE_EXTERNAL_NETWORK_REQUESTS`, and
  `NO_SECRET_PATTERN_HITS`.
* `npm audit`: `UNAVAILABLE`; configured npmmirror endpoint returns
  `404 NOT_IMPLEMENTED`. No dependency or lockfile changed.

## Commit / CI / Queue

* implementation: `c25a815ea4b1e9601287d46a02be16603ce5cf07`; its first CI
  exposed only ignored evidence files while frontend and service-backed passed.
* evidence-closure/current implementation HEAD:
  `fb9d720b9d6009ebecab8eeff7fc60c2080a67c6`; exact-SHA CI run
  `30372914960` passed Unit, Frontend Typecheck & Build,
  PostgreSQL/Redis/MinIO service-backed integration, and no-skipped assertion.
* completion record: `97a07814d4b7c7cfe9d086aedc094cf46cc0368b`;
  exact-SHA CI run `30373474557` passed Unit, Frontend Typecheck & Build,
  PostgreSQL/Redis/MinIO service-backed integration, and no-skipped assertion.
* archive decision: implementation, evidence, permanent result, required local
  checks, and both exact-SHA CI gates are consistent. The completed K4 task
  block is removed by the verified queue archive commit.
* Phase 10K-4: `ARCHIVED_BY_VERIFIED_QUEUE_COMMIT`.
* Phase 10K-5 remains pending and was not implemented by this task.

# Phase 10K-5 Material Intelligence Integration + Browser/API Evidence Result

## 1. Conclusion

`PASS` for implementation and evidence. Completion-record CI and verified
queue archival are recorded in a closure addendum after this record commit.

## 2. Baseline

* Phase 10K-4 implementation: `fb9d720b9d6009ebecab8eeff7fc60c2080a67c6`.
* Phase 10K-4 completion record: `97a07814d4b7c7cfe9d086aedc094cf46cc0368b`.
* Phase 10K-4 archive: `0707fa7773cda57ba283cbfde5310f3e2aa99b7f`,
  exact-SHA CI run `30373921429` success.
* branch: `master`.
* initial HEAD/origin: `0707fa7773cda57ba283cbfde5310f3e2aa99b7f`.
* initial status: clean before K5 execution.

## 3. Phase 10K Component Status

### 10K-1

* Profile: Material Data Profile 2.0 is the deterministic data authority.
* semantics: formula, property, task/model, uncertainty/class, resource and
  sample roles are Profile-owned.
* readiness: data readiness remains separate from executable platform support.

### 10K-2

* Dataset Explorer: bounded overview, composition, canonical Structure
  statistics, properties, quality, comparison, and stable sample links.

### 10K-3

* Materials ML: Profile-bound regression, uncertainty, conditional
  classification, chemistry-conditioned diagnostics, and model comparison.

### 10K-4

* Composition Space: normalized atomic fractions, deterministic 2D PCA,
  bounded KMeans, property/K3 coloring, comparison, and linked inspection.

## 4. Integration Architecture

* dataset identity: exact dataset ID plus version.
* version binding: Profile ID/contract/semantic hash, complete dataset content
  hash, and sorted canonical resource hashes must all match.
* sample identity: immutable `objectId:sampleRef`; array position is forbidden.
* semantic authority: Profile 2.0 facts; Adapters own bounded analyses.
* artifact relationships: K4 accepts only exact allowlisted K3 artifacts with
  matching binding and bounded sample rows.
* frontend organization: one typed product-status surface plus independent
  K2/K3/K4 panels; no global Phase 10M workspace redesign.

## 5. Cross-Artifact Identity

* Dataset Explorer: every linked sample emits object-qualified `sampleKey`.
* ML: high-error/high-uncertainty/misclassification rows retain the same key.
* Composition Space: points and dependent ML colors use exact sample keys.
* sorted/filtered tests: different table, error, and PCA orders preserve links.
* result: `MATERIAL_INTELLIGENCE_SAMPLE_IDENTITY_EVIDENCE_PASS`.

## 6. Version / Cache Binding

* dataset version: exact, not latest-wins.
* profile: QueueWorkerRuntime resolves the persisted plan's exact `profileId`.
* artifacts: carry full deterministic content/resource binding.
* stale protection: missing/mismatched fields are `REJECTED`/`STALE`, never
  wildcarded or silently repaired.
* result: `MATERIAL_INTELLIGENCE_VERSION_BINDING_EVIDENCE_PASS`.

## 7. Capability Availability

* DataProfile readiness: deterministic data-side eligibility.
* actual Tool availability: Registry/Adapter capability is checked separately.
* frontend capability gating: combines validated Profile and product artifacts.
* ambiguous semantics: safely blocked; no first-column or legacy metric guess.
* partial data: independent coverage and product states remain visible.

## 8. Dataset Product

* Overview: PASS.
* Composition: PASS with eligible/excluded coverage.
* Structure: PASS for canonical Structure-backed resources.
* Properties: PASS with Profile-owned identity and units.
* Quality: PASS as factual diagnostics, not anomaly authority.
* Comparison: PASS with explicit dataset/group identity.

## 9. ML Integration

* regression: PASS.
* uncertainty: PASS where Profile semantics are complete.
* classification: PASS where class/probability semantics are complete.
* multiple models: exact target/prediction/model identity retained.
* chemistry: adapter-produced element/system diagnostics, no browser recompute.
* task identity: explicit Profile group; ambiguous groups are blocked.

## 10. Composition Space Integration

* composition semantics: Profile-authorized formulas only.
* property binding: exact semantic property and unit.
* ML binding: validated K3 artifact values, hashes, task/model and coverage.
* comparison: explicit resources/groups on one shared feature/PCA basis.
* sample inspection: object-qualified links survive ordering changes.

## 11. API

* job: real persisted Mock Planner jobs captured for cases A-H and replay.
* plan: validated single-tool AnalysisPlans; no K5 run-everything plan.
* runtime: QueueWorkerRuntime plus Registry/Adapter execution.
* artifacts: persisted inert products, summaries, recipes, and plots.
* retrieval: API-style job/artifact captures include persisted IDs and hashes.
* version/provenance: exact Profile/dataset/resource/params bindings retained.

## 12. Frontend

* Profile: authoritative readiness/status source.
* Dataset Overview, Properties, Data Quality: validated K2 artifact views.
* ML: validated K3 numeric/accessible views.
* Composition Space and Comparison: validated K4 views.
* partial states: `PRODUCED`, `READY_NOT_RUN`, `UNAVAILABLE`,
  `PROFILE_AUTHORITY_UNAVAILABLE`, `REJECTED`, `STALE`, and
  `CAPABILITY_MISMATCH`.
* error isolation: settled endpoint refresh preserves valid sibling products.

## 13. Report / Recipe

* artifact inclusion: persisted K2/K3/K4 artifact IDs and hashes are captured.
* provenance: dataset/Profile/resource/tool identities are exact.
* recipe: complete tool params and resource binding.
* deterministic rerun: structured results replay identically after removing
  runtime-owned IDs.

## 14. Evidence Cases

* materials table: PASS; ML is N/A.
* structure-enriched: PASS; ML and Composition Space are N/A where inapplicable.
* regression: PASS.
* uncertainty: PASS.
* classification: PASS; Composition Space is N/A for this case.
* comparison: PASS; ML is N/A.
* partial capability: PASS; ML correctly reports UNAVAILABLE.
* ambiguous semantics: PASS; ML is SAFELY_BLOCKED and composition is conditional.

## 15. Cross-Product Consistency

* units/property/task/model identity: exact and never inferred by display label.
* sample/dataset identity: exact object-qualified and version-bound.
* coverage disclosure: total, eligible/evaluated, excluded/matched/missing as
  appropriate for each product.

## 16. Partial Failure Isolation

* tested failure: insufficient/stale Composition Space and missing Profile
  authority while valid siblings remain.
* unaffected capabilities: validated Dataset Explorer or ML products remain.
* frontend behavior: typed partial state with independent panels.
* result: `MATERIAL_INTELLIGENCE_PARTIAL_FAILURE_ISOLATION_PASS`.

## 17. Browser Matrix

* Chromium: all A-H product cases, screenshots, keyboard and network audits.
* Firefox: major dataset, ML, composition, partial and ambiguity paths.
* WebKit: major dataset, ML, composition, partial and ambiguity paths.
* mobile: Dataset Overview, Regression, and Composition Space at 390x844.

## 18. Accessibility

* keyboard/labels: interactive controls and selectors are labeled and operable.
* chart alternatives/tables: numeric summaries and bounded tables are retained.
* warnings: textual states do not rely on color.
* mobile: controls and sample details remain readable without catastrophic
  viewport overflow.

## 19. Performance

* small (40): Dataset 24.766 ms/13,558 B; Regression 33.043 ms/29,910 B;
  Composition 56.437 ms/27,177 B.
* medium (5,000): Dataset 411.196 ms/28,114 B; Regression 1,473.496 ms/
  679,932 B; Composition 980.987 ms/2,028,220 B.
* near-cap: Dataset 100,000 rows 7,554.176 ms/28,597 B; Regression 100,000
  rows 28,068.832 ms/699,850 B; Composition 20,000 rows 3,579.665 ms/
  8,063,785 B.
* frontend/memory: bounded display rows/points and no duplicate source table.
* overall envelope: PASS; products measured independently because Phase 10L
  multi-tool planning does not exist.

## 20. Security

* untrusted text remains React/plain JSON text; no raw HTML.
* arbitrary code/artifact JS: none.
* external network: `NO_MATERIAL_INTELLIGENCE_EXTERNAL_NETWORK_REQUESTS`.
* secrets: `NO_SECRET_PATTERN_HITS`.

## 21. Tool Registry Final Phase 10K Surface

* general tools: existing table/composition capabilities remain unchanged.
* dataset: `dataset.materials_explorer`.
* ML: `ml.regression_evaluation`, `ml.uncertainty_evaluation`, and
  `ml.classification_evaluation`.
* composition: `dataset.composition_space`.
* requirements: exact Profile 2.0 semantics and canonical resource bindings.
* outputs/readiness: inert structured artifacts; each capability independent.
* no K5 integration or run-everything Tool ID was added.

## 22. Explicit Phase 10K Limits

Not implemented: capability-aware Agent, automatic multi-tool planning, LLM
result interpretation, Unified Scientific Workspace, CrystalNN/VoronoiNN,
experimental XRD, trajectory analytics, Electronic Band/DOS, or Future advanced
capabilities. These are assigned to later approved phases, not K5 failures.

## 23. Files Changed

* backend: hashing, K2-K4 binding, exact Profile resolution/runtime guard, and
  ambiguity safety.
* frontend: integration mapper/panel and K2-K4 product composition.
* tests/evidence: unit, component, integration, A-H runtime/API/browser,
  identity, replay, performance, accessibility, network, and security.
* docs/persistent: K5 contracts, evidence matrices, Phase 10K summary, next
  scope, schema/index/capability matrix, ADR, board, progress, and changelog.
* dependency/lockfile: unchanged.

## 24. Checks

* git diff --check: PASS.
* uv lock: PASS.
* backend: PASS, `837 passed, 27 skipped, 63 warnings`.
* frontend: PASS, `52 files, 323 tests`.
* typecheck/build: PASS.
* service-backed local: UNAVAILABLE (Docker absent); CI: PASS.
* no-skipped CI assertion: PASS.
* docs/TASKS/evidence integrity/security: PASS.

## 25. Commit / CI

### Integration Implementation

* commit/exact SHA: `e4639a1168f4bac7f4c786c48657559038bd7230`.
* CI run: `30382233569`.
* Unit, Frontend Typecheck & Build, service-backed integration, and no-skipped:
  all success.

### Completion Record

* commit/exact SHA/CI: pending this completion-record commit.

## 26. Queue State

* Phase 10K-5: `COMPLETED_AWAITING_COMPLETION_RECORD_CI_AND_ARCHIVE`.
* Phase 10K: `READY_WITH_EXPLICIT_LIMITS_AWAITING_ARCHIVE`.
* Phase 10L-0: `NEXT / AWAITING COMPLETE PROMPT`, not started.

## 27. Phase 10K Final Readiness

* DataProfile, Dataset Explorer, Materials ML, Composition Space, API,
  frontend, sample identity, version binding, browser, accessibility,
  performance, and security: READY within documented caps.
* overall: `READY_WITH_EXPLICIT_LIMITS` pending completion-record CI/archive.

## 28. Whether Allowed to Enter Phase 10L-0

不可以：completion-record exact-SHA CI 与 verified K5 archive 尚未闭合。

## 29. Next Phase

**Phase 10L-0：Agent / Planner Capability Audit**，仅为 NEXT；本任务未实现。

## 30. Completion-Record CI and Queue Closure

* closure status: `PASS`.
* completion-record commit: `81d44467c9b0d9e8bef3d4dec38d6a85e3d2aebe`.
* completion-record exact-SHA CI run: `30382583135`, success.
* CI jobs: Unit Tests, Frontend Typecheck & Build, and PostgreSQL/Redis/MinIO
  Service-backed Integration all succeeded; the no-skipped assertion passed.
* archive verification: implementation/evidence, permanent result, required
  checks, and both exact-SHA CI gates are consistent. Only the completed K5
  `---TASK---` block is removed; evidence and result history are retained.
* Phase 10K-5: `ARCHIVED_BY_VERIFIED_QUEUE_COMMIT`.
* Phase 10K: `COMPLETE / READY_WITH_EXPLICIT_LIMITS`.
* Phase 10L-0: `NEXT / NOT_STARTED`.

# Phase 10L-0 Agent / Planner Capability Audit Result

## 1. Conclusion

`PASS` for the architecture/capability audit. Completion-record CI and verified
queue archival are recorded in a closure addendum after that gate succeeds.

## 2. Baseline

* Phase 10K: `COMPLETE / READY_WITH_EXPLICIT_LIMITS`.
* Phase 10K-5 archive: `17de1f91cef6e94a5a1f4ae684fb3e1b756f0906`,
  exact-SHA CI run `30382914410` success.
* branch: `master`.
* initial HEAD/origin: `17de1f91cef6e94a5a1f4ae684fb3e1b756f0906`.
* initial status: clean before Phase 10L-0 execution.

## 3. Current Planner Architecture

```text
POST /planner/jobs
  -> persisted DataProfile + Registry snapshot
  -> Mock deterministic router OR optional OpenAI-compatible JSON provider
  -> AnalysisPlan 0.1
  -> PlanValidator
  -> persisted plan/hash + job
  -> QueueWorkerRuntime
  -> Registry lookup + registered Adapter
  -> ToolCalls/events/artifacts
  -> PlannerWorkbench timeline and results
```

The Mock path reads selected Profile 2.0 facts directly. The live-LLM prompt
receives only a shallow table/structure Profile summary and a reduced MVP tool
inventory. PlanValidator receives no Profile.

## 4. Current AnalysisPlan

* schema/version: `AnalysisPlan` schema version `0.1`.
* ToolCall count: a non-empty ordered `steps` array; no plan-level maximum.
* ordering: deterministic list order and unique step IDs.
* dependencies: absent.
* artifact binding: artifact-shaped input refs exist syntactically, but no
  producer-step identity or previous-output runtime injection exists.
* persistence: canonical plan JSON, hash, provider, job binding, events,
  ToolCalls, and artifacts are persisted.
* versioning: provider is stored; model/prompt version and complete provider
  configuration are not.
* failure: first failed step stops later execution, job fails, and already
  written artifacts remain; no partial-success status or automatic retry.

## 5. Multi-Tool Reality

`SEQUENTIAL_INDEPENDENT`.

QueueWorkerRuntime executes multiple steps in order, and the existing phonon
band plus Brillouin-zone test proves a real two-step job. Both steps consume
independent pre-existing inputs. There is no dependency graph or prior-step
artifact binding, so the product is not dependency-aware multi-tool planning.

## 6. Mock Planner

* routing: fixed-priority phrase/substring predicates and named plan builders.
* keyword dependence: high; 34 route predicates and 56 prompt-check sites.
* resource/Profile awareness: partial and strongest for Phase 10K ML and
  Composition Space; selected structure/trajectory/phonon/volume checks exist.
* Registry awareness: verifies fixed IDs exist; it does not rank eligible
  tools from capability metadata.
* ambiguity: selected ML ambiguity routes safely to diagnostics, but no general
  clarification state exists.
* params: exact Profile semantic binding for K3/K4; heuristic/default binding
  remains in older routes.
* classification: `PARTIAL_PROFILE_AWARE`.

## 7. LLM Planner

* architecture: explicit opt-in OpenAI-compatible JSON completion; Mock is the
  default and CI path.
* prompt: raw goal, dataset/Profile IDs, shallow table/structure facts, quality
  count, and 41 MVP IDs/descriptions/artifact types/parameter names.
* missing context: full Profile semantic groups/readiness, trajectory/phonon/
  volumetric facts, full parameter constraints, input schemas, caps, ranking,
  prior plans, and prior errors.
* enforcement: JSON object parsing followed by mandatory PlanValidator.
* retry/repair/fallback: one response-format compatibility retry on HTTP 400 is
  transport handling, not plan repair; no validation repair or Mock fallback.
* `REAL_LLM_CALLS = 0` for this audit.

## 8. DataProfile to Planner Integration

* Mock: resource kind, composition, structure, trajectory, phonon, volumetric,
  regression, uncertainty, classification, and readiness are consumed unevenly;
  K3/K4 are the strongest Profile-aware paths.
* LLM: table columns and a shallow structure summary only; no full Profile 2.0
  semantic groups/readiness.
* Validator: no Profile or semantic-readiness validation.

## 9. Tool Registry Planner Readiness

* inventory: 53 tools, 41 MVP, 11 V1, one V2 across eight domains.
* present: identity, descriptions, input object options, params JSON Schema,
  output artifact metadata, costs, timeout, permissions, and resource caps.
* missing: uniform semantic prerequisites, Profile readiness mapping, planner
  ranking hints, collision groups, and composition constraints.
* classification: `PARTIAL_PLANNER_CAPABILITY_REGISTRY`.

## 10. PlanValidator

* validates Pydantic plan shape, non-empty/unique steps, known MVP tool,
  credential-like parameter rejection, parameter JSON Schema, and known enum
  values.
* does not validate resource kind/existence, Profile readiness, scientific
  semantics, produced-artifact compatibility, explicit dependencies, max step
  count, duplicate calls, or cross-step bindings.
* classification: `SCHEMA_AND_REGISTRY_VALIDATOR`.

## 11. Tool Selection

* table/viz and older ML: phrase routes plus column heuristics/defaults.
* dataset and Phase 10K ML/composition space: product-specific Profile facts,
  readiness, semantic groups, and fixed Registry IDs.
* structure/trajectory/phonon/BZ/volumetric: phrase plus resource-presence
  predicates and approved fixed parameters.
* there is no cross-domain candidate ranking or capability composition pass.

## 12. Representative Prompt Audit

* composition distribution: `dataset.materials_explorer`; coherent single
  product, no element/system-specific composition.
* structure reasonableness: `structure.summary`; no coordination/RDF/XRD/viewer
  composition.
* poor model predictions: `ml.basic_metrics`; misses product regression and
  linked chemistry/sample diagnostics.
* uncertainty trust: `ml.basic_metrics`; misses ready uncertainty evaluator.
* broad phonon quality: `ml.basic_metrics`; resource-incompatible fallback.
* charge-density features: `structure.volumetric_data`; correct preparation,
  no interpretation.
* broad dataset analysis: `dataset.materials_explorer`; no ranked composition.
* explicit `formation_energy` distribution: `viz.histogram` incorrectly binds
  `band_gap`, proving heuristic parameter drift.

## 13. Analysis Intent

No structured intent object exists. The request is raw prompt plus dataset,
Profile, and Registry IDs; `AnalysisPlan.goal` repeats the raw prompt. Decision:
`REQUIRED`, subject to reviewer approval of its exact shape.

## 14. Ambiguity / Clarification

Some Phase 10K ML ambiguity is typed and safely redirected, but there is no
general clarification state, follow-up answer binding, or conversation context.

## 15. Plan Repair

There is no JSON/schema/scientific validation repair loop. Invalid provider
output is rejected and persists no plan/job. Retry limits for repair therefore
do not exist.

## 16. Result Interpretation

Deterministic Adapter summaries, warnings, recipes, and historical report paths
exist. No LLM receives bounded scientific result context, and no grounded
interpretation/no-invention contract or recommendation stage exists.

## 17. Frontend Planner UX

The UI supports prompt/resource selection, create-and-run, plan/timeline/call/
artifact inspection, and typed errors. The generated plan becomes visible only
after create/enqueue. Plan editing, approval-before-run, clarification, cancel,
and same-job retry are absent.

## 18. Security Boundary

The LLM cannot execute Python, shell, filesystem, adapters, or scientific
libraries. Unknown/non-MVP tools, credential-shaped params, and schema-invalid
params are rejected. BYOK is resolved separately. Missing caps include prompt
length, plan step count, Registry prompt budget, and API upper bounds for some
provider tuning fields. Future interpretation requires an explicit untrusted
artifact-content boundary.

## 19. Planner Test Coverage

Existing coverage includes deterministic Mock routes, fake live-provider JSON/
error cases, PlanValidator rejection, persistence/hash, sequential Runtime,
read APIs, frontend PlannerWorkbench, service-backed jobs, and default-Mock
network isolation. It does not prove capability-ranked planning, dependencies,
repair, clarification, or result interpretation.

## 20. Planner Maturity

`CURRENT_LEVEL = 3` on the audited Level 0-5 scale: data/profile-aware tool
selection exists but is uneven. Overall product classification:
`PROFILE_AWARE_SINGLE_TOOL_PLANNER_WITH_NARROW_SEQUENTIAL_INDEPENDENT_COMPOSITION`.

## 21. Gap Matrix

* READY: Profile transport, strict Registry execution metadata, deterministic
  single-tool plans, persisted plans/hashes, timeline/artifacts.
* REUSABLE_FOUNDATION: Profile 2.0, ordered steps, sequential Runtime,
  summaries/recipes.
* PARTIAL: Profile-aware routing, parameter binding, ambiguity, failure
  isolation, Planner provenance, plan preview.
* MISSING_10L: Analysis Intent, capability eligibility/ranking, semantic
  validation, dependencies/artifact binding, caps, repair, interpretation, and
  broad Agent evidence.
* DEFER_10M: plan editing/approval and unified workspace UX.
* DEFER_10N: professional tool coverage.
* FUTURE/NOT_NEEDED: long-term memory and generic workflow/DAG products;
  arbitrary code remains prohibited.

## 22. Recommended Phase 10L Scope

* 10L-1: strict lightweight Analysis Intent and ambiguity outcome.
* 10L-2: capability-aware selection over Profile plus planner-facing metadata,
  uniform binding, typed unsupported outcomes, and plan/prompt caps.
* 10L-3: smallest approved bounded dependency/artifact model, not a generic DAG.
* 10L-4: bounded structured interpretation over computed facts with explicit
  no-invention rules.
* 10L-5: five real natural-language Profile-to-plan-to-runtime-to-artifact-to-
  interpretation evidence cases.

## 23. Reviewer Decisions Required

Reviewer approval is required for intent shape, ambiguity/clarification,
capability metadata ownership, AnalysisPlan evolution, sequence versus
restricted dependencies, failure/cancellation, repair policy, pre-execution
control ownership, and interpretation provider/context policy.

## 24. Production Behavior Changes

```text
Production Planner Behavior Changes:
NONE
```

No AnalysisPlan schema, Registry contract, PlanValidator, Runtime, dependency,
public tool, Adapter, Planner route, or frontend behavior changed.

## 25. Files Changed

Only `TASKS.md`, `results.md`, Phase 10L docs/evidence, `docs/index.md`, and
persistent project-memory files. No production source, dependency, or lockfile
changed.

## 26. Checks

* Planner focused: PASS, `92 passed, 1 skipped, 1 warning`; skip disclosed.
* backend full: PASS, `837 passed, 27 skipped, 63 warnings`.
* frontend full: PASS, 52 files and 323 tests.
* typecheck/build: PASS.
* Phase 10 closure/evidence and trajectory performance integrity: PASS.
* `uv lock --check`, `git diff --check`, docs links, TASKS structure, and Phase
  10L-0 evidence integrity: PASS.
* local service-backed: UNAVAILABLE, Docker absent; `25 skipped, 12 deselected`.
* audit exact-SHA CI service-backed/no-skipped: PASS.

## 27. Security

```text
REAL_LLM_CALLS = 0
NO_PHASE10L0_EXTERNAL_NETWORK_REQUESTS
NO_SECRET_PATTERN_HITS
```

## 28. Commit / CI

### Audit Commit

* commit/exact SHA: `a7f8b143129d4cf3ced95373d8d81199b06f7ca6`.
* CI run `30414233888`: Unit, Frontend Typecheck & Build, service-backed
  integration, and no-skipped all success.

### Completion Record

* commit/exact SHA/CI: pending this completion-record commit.

## 29. Queue State

* Phase 10L-0: `COMPLETED_AWAITING_COMPLETION_RECORD_CI_AND_ARCHIVE`.
* Phase 10L-1: `REVIEWER_GATE / AWAITING REVIEWER PROMPT`.

## 30. Whether Allowed to Enter Phase 10L-1 Automatically

`NO`. Phase 10L-1 requires reviewer review of the real Phase 10L-0 architecture
audit and an explicit complete execution prompt.

## 31. Next Action

Return Phase 10K-5 and Phase 10L-0 results to the reviewer for Phase 10L
architecture decision and Phase 10L-1 execution prompt. Do not implement or
queue Phase 10L-1 automatically.

## 32. Completion-Record CI and Queue Closure

* closure status: `PASS`.
* completion-record commit: `ee86745707d9388b28f85051c5994e403c095c21`.
* completion-record exact-SHA CI run: `30414599167`, success.
* CI jobs: Unit Tests, Frontend Typecheck & Build, and PostgreSQL/Redis/MinIO
  Service-backed Integration all succeeded; the no-skipped assertion passed.
* archive verification: audit docs/evidence, permanent result, local checks,
  audit exact-SHA CI, and completion-record exact-SHA CI are consistent. Only
  the completed Phase 10L-0 `---TASK---` block is removed; evidence and result
  history remain.
* Phase 10L-0: `ARCHIVED_BY_VERIFIED_QUEUE_COMMIT`.
* Phase 10L-1: `REVIEWER_GATE / AWAITING REVIEWER PROMPT` and is not queued.

# Phase 10L-1 Analysis Intent Contract + Bounded Clarification Result

## 1. Conclusion

`PASS` for implementation at corrected implementation HEAD
`844eb149a4c528d28db9fdf70dddfaf015e91d5a`, exact-SHA CI run
`30425804801`. Completion-record CI and verified queue archive are recorded in
a closure addendum after those gates succeed.

## 2. Baseline

* Phase 10K: `COMPLETE / READY_WITH_EXPLICIT_LIMITS`.
* Phase 10L-0: `ARCHIVED_BY_VERIFIED_QUEUE_COMMIT` at `83f5c44`.
* branch: `master`.
* initial HEAD/origin: `83f5c44eb10843f57ae79902d2db5cc85c302b43`.
* initial TASKS state: Phase 10L-1 sole active task; Phase 10L-2 reviewer gate.

## 3. Entry Audit

The existing production flow was `POST /planner/jobs -> provider ->
AnalysisPlan 0.1 -> PlanValidator -> persisted plan/job -> QueueWorkerRuntime`.
The additive canonical v1 flow is `exact DataProfile 2.0 -> AnalysisIntent ->
existing Planner -> existing plan/job/runtime`. Intent-plan-job association is
stored outside AnalysisPlan. Registry, PlanValidator, Runtime, and route
precedence were explicit non-change boundaries.

## 4. AnalysisIntent Contract

* schema/version: independent strict `AnalysisIntent` `1.0` in Python,
  checked-in JSON Schema, and TypeScript.
* identity: deterministic `intentHash` over canonical semantic content and
  deterministic `intentId`; runtime timestamp is excluded.
* goal: secret-redacted original `rawGoal` plus whitespace-only
  `normalizedGoal`; semantic expansion fails validation.
* scope: exact dataset version, Profile ID/contract/semantic hash, object ID,
  object hash, resource kind, and explicit target/model/group identities.
* vocabulary: bounded scientific intent, desired output, capability need,
  ambiguity, diagnostic, constraint, warning, and provenance enums/fields.

## 5. Outcome Semantics

* `READY`: exact scope and required Profile facts exist; no blocking ambiguity.
* `NEEDS_CLARIFICATION`: a real current Profile/resource candidate can resolve
  the ambiguity within one round.
* `UNSUPPORTED`: missing data, Future/Not Planned scope, unsafe execution, or
  ambiguity that cannot be resolved within the bounded policy.
* Blocking ambiguity can never coexist with `READY`.

## 6. Bounded Clarification

* maximum rounds: 1.
* maximum questions: 3.
* types: `SELECT_ONE`, `SELECT_MANY`, and `CONFIRM`.
* options are exact current DataProfile/resource facts, never LLM inventions.
* answers bind intent/question/option/Profile hash and create an immutable child
  Intent with a new ID/hash and parent/answer provenance.
* stale Profile/resource, invalid option, incomplete answers, and second round
  are typed failures.

## 7. Mock / Deterministic Path

The default deterministic builder uses allowlisted raw-goal rules plus exact
Profile 2.0 facts. It performs no network request, tool selection, or silent
fallback and emits deterministic semantic identity. It does not attempt Phase
10L-2 capability ranking.

## 8. LLM Intent Path

The optional path reuses the existing OpenAI-compatible bounded transport and
adds no dependency. Its prompt contains only redacted goal, selected exact
identity, bounded Profile facts, schema, vocabulary, and safety rules. Exactly
one JSON object is accepted; fences, prose, duplicate keys, unknown fields,
invented IDs/candidates, over-cap arrays, and inconsistent outcomes fail with
no repair and no Mock fallback. Default evidence used `REAL_LLM_CALLS = 0`.

## 9. Validation

An independent `AnalysisIntentValidator` validates schema, canonical identity,
caps/depth/bytes, exact Profile/resource/target facts, capability facts,
goal normalization, outcome consistency, unique semantic identities,
Profile-derived question candidates, immutable revision, Future/Not Planned,
and execution boundaries. It does not validate tools, plans, or Runtime.

## 10. Persistence / Migration

* tables: `analysis_intents` and `analysis_intent_executions`.
* migration: Alembic `0003_phase10l1_intents`, upgrade and downgrade defined.
* repositories: in-memory and SQLAlchemy with immutable/idempotent intent save
  and immutable plan/job association.
* PostgreSQL: exact-SHA CI ran migration, verified tables/indexes, persisted the
  Intent and association, and passed no-skipped.

## 11. API

Additive typed create/get/clarify routes were added. `/planner/jobs` opts into
v1 with `intentSchemaVersion` or a persisted `intentId`. Non-READY returns
before AnalysisPlan/job/enqueue. READY invokes the unchanged provider with the
preserved raw goal and stores the external association. Job detail exposes the
associated Intent additively.

## 12. Frontend

PlannerWorkbench opts into v1 and displays original goal, intents, exact scope,
targets, desired outputs, warnings, outcome, provider, bounded questions,
unsupported reasons, disabled Run state, and inert developer JSON. A valid
answer displays the immutable revision and continues the existing Planner.
Keyboard/focus labels, no horizontal overflow, and 390x844 mobile passed.

## 13. Compatibility

AnalysisPlan remains `0.1`; stored plan hashes and historical jobs/artifacts are
unchanged. Legacy API consumers may omit Intent fields and retain the prior
Planner behavior. Gated READY requests preserve current Mock and fake-provider
selection. Tool Registry, PlanValidator, QueueWorkerRuntime, and Phase 10K
products regress without semantic changes.

## 14. Caps / Performance

Caps include 16,384 goal characters; 32 resource refs, targets, desired outputs,
ambiguities, and diagnostics; 16 scientific intents/capability needs; three
questions; one round; JSON depth 12; and serialized size 262,144 bytes. The
near-cap evidence used 16,384 characters and 32 resources, producing about
23.7 KB with about 181 KB peak traced memory and about 11 ms build/validate
time. Failures are typed and bounded.

## 15. Security

```text
REAL_LLM_CALLS = 0
NO_PHASE10L1_EXTERNAL_NETWORK_REQUESTS
NO_ANALYSIS_INTENT_ARBITRARY_CODE_EXECUTION
NO_ANALYSIS_INTENT_ARTIFACT_JAVASCRIPT
NO_SECRET_PATTERN_HITS
```

Raw HTML, script text, prompt injection, and credential-shaped text remain
inert; credential values are redacted before persistence/evidence. Intent has
no shell, filesystem, network, code, artifact-JS, or execution authority.

## 16. Evidence

Evidence is retained at
`docs/phase10l/evidence/phase10l1_analysis_intent/`: sanitized API READY,
clarification, revision, unsupported/no-job, SQLite persistence, PostgreSQL CI
gate, performance, security, browser DOM/network/console, six screenshots, and
an LF-normalized text/raw-PNG SHA-256 manifest.

## 17. Tests

* focused backend: `27 passed`.
* focused PlannerWorkbench: `22 passed`.
* full backend: `864 passed, 28 skipped, 63 warnings` locally.
* full frontend: 52 files / `325 passed`.
* typecheck, production build, `uv lock --check`, `git diff --check`: PASS.
* Phase 10 closure/evidence: PASS.
* browser: Chromium 128, Firefox 128, WebKit 18, mobile 390x844 PASS.
* local service-backed: `UNAVAILABLE`, Docker command absent; 26 service tests
  skipped and not reported as passed.
* exact-SHA CI service-backed/no-skipped: PASS.

## 18. Production Behavior Changes

Canonical PlannerWorkbench requests now generate/persist an Intent before
planning. `READY` preserves old tool selection and params. `NEEDS_CLARIFICATION`
and `UNSUPPORTED` create no plan/job and enqueue nothing. AnalysisPlan,
PlanValidator, Tool Registry, and QueueWorkerRuntime semantics did not change.
Historical unversioned API requests remain compatible.

## 19. Files Changed

Backend/API repositories and migration, schema contracts, provider Intent
builder/validator, PlannerWorkbench/API types, focused/integration/browser
tests, CI service gate, evidence, Phase 10L docs, shared schema/index, TASKS,
and persistent records. Dependency and lock files are unchanged.

## 20. Commit / CI

* initial implementation: `365953f3f89c584fb82aafb9c20774e005141957`;
  CI run `30425561782` failed only the cross-platform evidence byte hash.
* corrected implementation HEAD:
  `844eb149a4c528d28db9fdf70dddfaf015e91d5a`.
* implementation exact-SHA CI: run `30425804801`, Unit, Frontend,
  PostgreSQL/Redis/MinIO, migration, and no-skipped success.
* completion-record commit:
  `b4cd656e1c03bb7d6ea406ed0f2dbd828dfb2dd9`.
* completion-record exact-SHA CI: run `30426248141`, Unit, Frontend,
  PostgreSQL/Redis/MinIO, migration, and no-skipped success.
* archive commit/CI: this verified queue archive change; exact SHA and CI are
  reported after the commit gate closes.

## 21. Explicit Non-Scope Confirmation

No Capability-Aware Planner, Registry planner metadata, Eligibility Resolver,
AnalysisPlan 0.2, dependencies, artifact binding, Runtime partial success, plan
repair, interpretation, Workspace redesign, professional science, Future/Not
Planned capability, new LLM dependency, arbitrary code, or external scientific
API was implemented.

## 22. Remaining Phase 10L Gaps

10L-2 owns capability-aware selection and any approved planner metadata; 10L-3
owns the smallest approved dependency/artifact model; 10L-4 owns grounded
result interpretation; 10L-5 owns full natural-language evidence closure.
These are gaps only, not executable tasks.

## 23. Queue State

* Phase 10L-1: `ARCHIVED_BY_VERIFIED_QUEUE_COMMIT`.
* Phase 10L-2: `REVIEWER_GATE / AWAITING REVIEWER PROMPT`.

## 24. Whether Allowed to Enter Phase 10L-2 Automatically

`NO`.

## 25. Next Action

Return the complete Phase 10L-1 result to the reviewer after the queue archive
commit passes exact-SHA CI. Do not queue or execute Phase 10L-2.

### Completion-record CI and queue archive authorization

* 核验时间：2026-07-29 13:52:25 +08:00。
* completion-record commit：
  `b4cd656e1c03bb7d6ea406ed0f2dbd828dfb2dd9`。
* exact-SHA CI：run `30426248141` success；Unit Tests、Frontend Typecheck &
  Build、PostgreSQL/Redis/MinIO migration/service-backed integration 和
  no-skipped assertion 均成功。
* 归档决定：implementation、evidence、测试、永久结果、completion record、
  两次 exact-SHA CI 和 persistent 状态一致，允许在本次 queue archive commit
  中删除已完成的 Phase 10L-1 task block。Phase 10L-2 保持
  `REVIEWER_GATE / AWAITING REVIEWER PROMPT`，未创建 executable task。

# Phase 10L-2 Capability-Aware Planner + Eligibility Resolver Result

## 1. Conclusion

`PASS` for corrected implementation
`9786e405f1938b514b95ccbeb1cdb6d4b26dde18`, exact-SHA CI run
`30511654404`. Completion-record CI and verified queue archive remain separate
gates and will be recorded in a closure addendum.

## 2. Baseline and Entry Gate

- Phase 10K: `COMPLETE / READY_WITH_EXPLICIT_LIMITS`.
- Phase 10L-0 and 10L-1: archived; L1 archive baseline `dbcda192...`.
- initial branch/HEAD/origin: `master` / `dbcda192...` / `dbcda192...`.
- initial worktree: clean; one L2 task block; L3 reviewer gate only.

## 3. Entry Audit and Previous Failure Modes

The prior READY path used fixed Mock routes or a broad provider Registry
summary without one auditable contextual gate. The new path inserts Registry
snapshot, eligibility, selection, exact binding, and independent context
validation before unchanged AnalysisPlan 0.1.

## 4. Registry Planner-Metadata Contract

`ToolPlannerMetadata 1.0` records stable tool/version, availability, intents,
needs, outputs, resource/object kinds, Profile prerequisites, targets,
cardinality, bindings, existing artifact outputs, cost, collision/composition,
and the registered-adapter-only execution boundary.

## 5. Metadata Validation and Capability Inventory

All 53 Registry entries are covered; 38 are currently available. Entries are
stable-key sorted. Deployment-unavailable/Future entries are non-selectable.
Unknown fields/enums, invalid params/outputs, impossible cardinality,
executable content, and availability contradictions are rejected.

## 6. Eligibility Resolution Contract

`EligibilityResolution 1.0` has deterministic ID/hash and exact Intent,
Profile, dataset/resource, Registry snapshot, candidate, eligible/rejected,
reason, prerequisite, binding-domain, ordering, diagnostic, and resolver
provenance fields. Runtime timestamps do not affect semantic identity.

## 7. Eligibility Rules and Typed Rejections

Candidates must exist, be invocable, have valid metadata, cover exact
intent/need/output facts, accept exact resources/targets, satisfy Profile
facts/cardinality/bindings/caps, and preserve safety/collision boundaries.
Every rejected candidate has bounded typed reasons; caps never truncate
semantics.

## 8. Candidate Projection and LLM Isolation

Providers receive eligible stable IDs, exact accepted identities/bindings,
coverage, cost, and collision facts only. They do not receive rejected tools,
the full Registry, paths, code, secrets, or unbounded Profile data.

```text
PROVIDER_VISIBLE_TOOL_IDS == ELIGIBLE_TOOL_IDS: PASS
NO_REJECTED_CANDIDATE_LEAK_TO_LLM: PASS
```

## 9. Deterministic Ranking and Selection

Mock ranking uses exact intent, need, output, resource/target applicability,
binding completeness, warnings, cost, then stable tool identity. Registry/UI
order has no authority. Independent multi-selection is bounded and rejects
duplicates/collisions; no dependency edge is created.

## 10. Exact Semantic Parameter Binding

Bindings come only from exact Intent identities, declared Profile facts,
bounded literals, or declared repository defaults and retain source identity.
First-column/display-label/fuzzy target, guessed units/models, raw LLM IDs,
code/path/URL, and unrelated-fact substitution are prohibited.

## 11. LLM Selection and Strict Parsing

The existing OpenAI-compatible transport receives the eligible projection and
strict schema. Only one bare JSON object is accepted. Fences, prose,
duplicate/unknown fields, invented IDs, invalid domains, dependencies,
code/path/URL, over-cap content, and inconsistent outcomes fail. No Mock
fallback or new LLM dependency exists.

## 12. One Validation-Guided Repair

Only a strictly parsed repairable LLM decision can receive one repair over the
unchanged candidate/binding domain. Hashes, typed diagnostics, repair count,
and outcome are retained. Exhaustion returns `VALIDATION_FAILED`; Mock output
is never repaired.

## 13. Capability-Context Validation

The independent validator recomputes Intent/Profile/Registry identity,
eligibility, coverage, parameter provenance, caps, duplicates/collisions,
independent composition, and no-dependency boundaries. The unchanged plan then
passes the existing PlanValidator.

## 14. Planning Outcomes and No-Job Semantics

Outcomes are `PLAN_READY`, `NEEDS_CLARIFICATION`, `UNSUPPORTED`,
`CAPABILITY_MISMATCH`, and `VALIDATION_FAILED`. Only PLAN_READY persists a
plan/job or enqueues Runtime work.

```text
NO_PLAN_JOB_OR_ENQUEUE_FOR_NON_READY_OUTCOMES: PASS
ANALYSIS_PLAN_SCHEMA_VERSION = 0.1
```

## 15. Persistence and Migration

Alembic `0004_phase10l2_capability_planning` adds immutable resolution,
decision, and execution-association tables. In-memory, SQLite migration, and
PostgreSQL paths verify identity, idempotency, conflicting-write rejection,
and external Intent/plan/job association. Upgrade/downgrade/re-upgrade pass.

## 16. API Behavior

The canonical Intent path loads exact READY Intent/Profile, resolves,
selects/binds/validates, and creates unchanged plan/job/runtime state only for
PLAN_READY. Responses add outcome, resolution, decision, eligible IDs,
diagnostics, and job association. Legacy behavior remains explicit.

## 17. Frontend and Browser Evidence

PlannerWorkbench shows outcome, scope, capability/tool IDs, output coverage,
exact bindings/provenance, warnings, repair state, failures, and inert JSON.
Run is disabled unless PLAN_READY. Chromium 128, Firefox 128, WebKit 18, and
Chromium 390x844 passed focus/status, console/network, inert-content, and
overflow checks.

## 18. Compatibility

AnalysisIntent remains 1.0; AnalysisPlan remains 0.1. Historical plan hashes,
jobs, and artifacts remain readable. Existing PlanValidator, Registry
execution contracts, route precedence, QueueWorkerRuntime, Phase 10K, and
Phase 10L-1 behavior are not weakened.

## 19. Caps and Performance

Caps are 64 Registry candidates, 32 eligible, 256 diagnostics, 64 binding
values, 4 independent tools, depth 14, and 524,288 serialized bytes. Near-cap:
53 tools, 174 diagnostics, 101,213-byte resolution, 1,967-byte decision,
209.439 ms, and 2,339,126 traced peak bytes. This is bounded local evidence,
not a production capacity claim.

## 20. Security

```text
REAL_LLM_CALLS = 0
NO_PHASE10L2_UNAPPROVED_EXTERNAL_NETWORK_REQUESTS
NO_CAPABILITY_PLANNER_ARBITRARY_CODE_EXECUTION
NO_CAPABILITY_PLANNER_SHELL_OR_FILESYSTEM_AUTHORITY
NO_CAPABILITY_PLANNER_ARTIFACT_JAVASCRIPT
NO_FULL_REGISTRY_LEAK_TO_LLM
NO_REJECTED_CANDIDATE_LEAK_TO_LLM
NO_SECRET_PATTERN_HITS
NO_PLAN_JOB_OR_ENQUEUE_FOR_NON_READY_OUTCOMES
```

Prompt injection, HTML/script, credential text, duplicate JSON keys, invented
or stale IDs, oversized content, and executable strings remain inert or typed
failures. No new dependency/external authority was added.

## 21. Required Audit Regressions

Formation energy/band gap bind distinct targets; prediction does not fall back
to basic metrics; uncertainty selects only explicit support; phonon never falls
through to ML/table/visual tools; broad dataset analysis is not Registry-first;
resource kinds do not interchange; candidate isolation and binding provenance
are retained.

## 22. Evidence Inventory and Manifest

`docs/phase10l/evidence/phase10l2_capability_aware_planner/` retains entry,
metadata/snapshot, eligibility/rejection, isolation, ranking, binding,
regression, strict LLM/repair, API, persistence, performance, security,
browser/mobile, screenshots, captures, and LF-normalized text/raw-PNG SHA-256
manifest evidence.

## 23. Test Results

- focused L2 backend/evidence: `27 passed`; L1 regression: `23 passed`.
- full local backend: `892 passed, 29 skipped, 63 warnings`; corrected CI unit:
  `892 passed, 1 skipped, 28 deselected, 63 warnings`.
- full frontend: 52 files / `327 passed`; PlannerWorkbench: `24 passed`.
- typecheck, build, lock, diff, evidence, Phase 10 closure: PASS.
- local service-backed: UNAVAILABLE (Docker absent), not reported as passed.
- exact-SHA CI service-backed: `27 passed, 0 skipped, 0 failed`.
- browser: Chromium/Firefox/WebKit and 390x844 mobile PASS.
- npm audit: UNAVAILABLE; configured mirror audit endpoint returned
  `404 NOT_IMPLEMENTED`, so no clean claim is made.

## 24. Production Behavior Changes

- Canonical READY requests now resolve Registry eligibility first.
- Selection uses structured capability facts and exact bindings.
- Non-ready outcomes stop before plan/job/enqueue/tool execution.
- LLM sees eligible candidates only and receives at most one repair.
- Resolution/decision/execution records persist externally.
- PlannerWorkbench adds a capability gate/audit surface.
- AnalysisPlan, PlanValidator, Registry execution, Runtime, historical jobs,
  and legacy API semantics remain unchanged.

## 25. Files Changed

Backend/API repositories and migration; shared Python/JSON/TypeScript schemas;
Registry metadata; resolver/selector/binder/validator; Planner API;
PlannerWorkbench/types/styles; focused/integration/browser tests; CI; evidence;
Phase 10L/shared docs; persistent records and TASKS. Dependencies/lock unchanged.

## 26. Commit and Exact-SHA CI History

- `ed880b313bed8d5bea36e5f8995f08bf48844023`, CI `30507612860`: failed
  service-backed because the fixture lacked the material-property fact required
  by its property-distribution goal.
- `c7c6081abda172756d48090d6000670bf6684d68`, CI `30510563999`: failed because
  the new fixture role used invalid authority `profile_exact`; a local fixture
  contract test was then added.
- corrected implementation: `9786e405f1938b514b95ccbeb1cdb6d4b26dde18`.
- corrected exact-SHA CI: `30511654404`, all required jobs PASS.
- completion-record/archive SHA and CI follow in the closure addendum.

## 27. Explicit Non-Scope Confirmation

No AnalysisPlan 0.2, dependency/DAG, prior-artifact binding, Runtime partial
success/failure redesign, plan editor/approval, interpretation, Workspace,
professional science, Fermi surface, arbitrary code, external science API,
new LLM SDK, enterprise infrastructure, or plugin ecosystem was implemented.

## 28. Remaining Phase 10L Gaps

10L-3 may define a reviewer-approved minimal dependency/artifact model; 10L-4
owns grounded interpretation; 10L-5 owns natural-language evidence closure.
These are gaps, not executable tasks.

## 29. Queue State

- Phase 10L-2: `COMPLETE / AWAITING_COMPLETION_RECORD_CI`.
- Phase 10L-3: `REVIEWER_GATE / AWAITING REVIEWER PROMPT`.
- `PHASE_10L3_EXECUTABLE_TASK_CREATED = NO`.

## 30. Whether Phase 10L-3 Was Entered Automatically

`NO`.

## 31. Next Action

Verify completion-record exact-SHA CI, then create and verify the queue-archive
commit. Return the result and stop; do not queue or execute Phase 10L-3.

## Phase 10L-2 Closure Addendum - 2026-07-30 12:16:43 +08:00

- Completion record commit:
  `f62630bef53fc797705683753fbc8d5eca595c98`.
- Completion-record exact-SHA CI: run `30513319990`, `success`.
- Required jobs: Unit Tests `success`; Frontend Typecheck & Build `success`;
  PostgreSQL + Redis + MinIO service-backed integration `success`; no-skipped
  assertion `success`.
- Queue verification: permanent result, corrected implementation CI, browser
  and evidence records, completion record, and completion-record CI agree.
- Archive action: the complete Phase 10L-2 `---TASK---` block is authorized for
  deletion by the verified queue-archive commit; Phase 10L-3 remains only a
  reviewer gate and no executable Phase 10L-3 task exists.
- Archive commit exact SHA and CI run are reported in the reviewer return after
  the final exact-SHA gate; this addendum is not rewritten after archive.

# Phase 10L-5 Natural-Language Analysis Evidence Closure + DeepSeek-Only Provider Result

Completion time: `2026-08-01T17:44:20.0686283+08:00`

## 1. Conclusion

`PASS / COMPLETE_AWAITING_COMPLETION_RECORD_CI`. The implementation and its
exact-SHA CI are complete. The task remains in `TASKS.md` until this record and
the subsequent queue archive each pass exact-SHA CI.

## 2. Phase 10L Closure Status

Phase 10L-0 through 10L-4 remain archived. Phase 10L-5 closes the approved
natural-language evidence scope without entering Phase 10M. Phase 10L becomes
`READY_WITH_EXPLICIT_LIMITS` only after verified queue archive.

## 3. Baseline and Entry Gate

- branch: `master`.
- initial HEAD/origin: `58ee9432f708324636a7226df8f417e7c3c52d09`.
- Phase 10L-4 archive CI: run `30608078520`, success.
- initial worktree: clean; initial active task count: one L5 block.
- `DEEPSEEK_KEY` was configured for controlled live evidence without exposing
  its value, prefix, length, or hash.

## 4. LLM Call-Site Audit

All production provider construction, Intent, capability selection,
dependency composition, grounded interpretation, health/API, and historical
compatibility call sites were audited. Deterministic and fake providers remain
explicit test paths. Browser evidence is offline replay and never calls a
provider directly.

## 5. DeepSeek-Only Provider Policy

`DeepSeekProvider` uses fixed `https://api.deepseek.com`, allowlisted
`deepseek-v4-flash` and `deepseek-v4-pro`, and `DEEPSEEK_KEY` as the sole key
source. OpenAI, custom OpenAI-compatible, and Anthropic real transports return
typed `PROVIDER_NOT_ALLOWED`; there is no key or provider fallback. Injected
fake transport remains test-only.

## 6. Provider Security

Requests are purpose-bounded, redacted, byte/depth capped strict JSON. Duplicate
keys, non-finite values, prose/fences, unsupported models, unknown fields,
secrets, URLs/paths/code, and invented identities are rejected. Provider
responses cannot execute tools or bypass Registry/Plan validation.

## 7. Default CI vs Real Verification

Default CI sets an empty `DEEPSEEK_KEY` and makes zero real calls. Controlled
live verification used the environment key and persisted only sanitized hashes,
token/call metadata, typed diagnostics, selected identities, and outcomes.
No authorization material or raw secret was retained.

## 8. Evidence Contracts

Added strict Python, JSON Schema, and TypeScript parity for
`NaturalLanguageEvidenceCase/Run`, `DeepSeekVerificationRecord/Suite`, and the
Phase 10L closure manifest. Canonical serialization, deterministic hashes,
unknown-field rejection, and count/byte/depth caps are enforced.

## 9. Dataset Case

Real DeepSeek completed DataProfile -> Intent -> eligibility -> plan -> job ->
Runtime -> registered dataset adapters -> artifacts/lineage -> grounded
interpretation. Run ID: `live_run_ceaef0c7168892dd5ed9d0a7da7bb7c1`.

## 10. Structure Case

Exact structure resource identity and supported structure capability completed
through registered adapters with grounded findings. Run ID:
`live_run_d11315ef07ae3cb3bf09295fdd1254b2`.

## 11. Materials ML Case

Exact target/model semantics and ML evaluation artifacts completed without
first-column or broad-metrics fallback. Run ID:
`live_run_28f09af3b53a75170a8850d6ca45f8b3`.

## 12. Phonon Case

AnalysisPlan 0.2 executed the real `phonon.band + phonon.dos ->
phonon.band_dos` typed chain, preserved graph/lineage identities, and produced
grounded interpretation. Run ID:
`live_run_b135271f0ff8102fa42b0102aa8b8d0c`.

## 13. Volumetric Case

Exact volumetric quantity/resource binding executed the registered capability
and grounded only supported range/reference/unit facts. Run ID:
`live_run_89ff5988240b2246dec4adb371deacdb`.

The five-case suite is
`deepseek_suite_ee5a0e9700d1a70787fc060fda274171`: `5/5 PASS`, per-case
calls `3, 3, 3, 4, 3`, total `16`.

## 14. Negative and Boundary Cases

The real-provider suite also verifies bounded clarification, Future Fermi
unsupported, capability mismatch, exact formation-energy/band-gap separation,
and no non-ready execution. Historical scatter behavior that depended on
first-column guessing is now a typed mismatch, not a fabricated success.

## 15. API

Canonical planner/API requests explicitly select DeepSeek and expose sanitized
provider identity, call audit, planning state, persisted job/artifacts, and
interpretation. Non-ready responses create no plan, job, enqueue, ToolCall, or
artifact. Legacy test compatibility is explicit and not counted as live proof.

## 16. Browser

Sanitized real-DeepSeek captures replayed in Chromium, Firefox, WebKit, and
Chromium `390x844` for five ready and three non-ready states. Console/page
errors, external requests, horizontal overflow, raw HTML/script/iframe, and
secret/path exposure were zero. Browser replay made zero live provider calls.

## 17. Service-Backed

Local PostgreSQL/Redis/MinIO live verification passed five real-DeepSeek cases
with zero skips; default local service integration passed `21/21`. Exact-SHA CI
service integration passed `36`, skipped `0`, failed `0`, including migration,
object storage, queue/runtime, L5 contracts, and no-skipped assertion.

## 18. Compatibility

AnalysisIntent remains `1.0`; EligibilityResolution remains `1.0`;
AnalysisPlan remains `0.1/0.2`; ToolPlannerMetadata remains `1.0/1.1`.
Existing PlanValidator, capability validator, QueueWorkerRuntime, dependency
execution, lineage, historical jobs/artifacts, L1-L4, and Phase 10K behavior
remain compatible. No migration or lockfile change was required.

## 19. Caps, Cost and Performance

Per-case live calls are capped at 12; suite calls at 60; provider request,
response, depth, timeout, model, and purpose are bounded. Recorded five-case
calls total 16 and historical supplemental calls total 92. Performance evidence
records bounded elapsed/token/call data without claiming production capacity.

## 20. Security Markers

```text
REAL_LLM_PROVIDER = DEEPSEEK_ONLY
REAL_LLM_KEY_SOURCE = DEEPSEEK_KEY_ONLY
REAL_LLM_CALLS_DEFAULT_CI = 0
REAL_DEEPSEEK_CALLS_CURRENT_SUITE = 16
REAL_DEEPSEEK_CALLS_HISTORICAL_SUPPLEMENTAL = 92
OTHER_REAL_PROVIDER_CALLS = 0
NO_OPENAI_REAL_CALLS
NO_CUSTOM_OPENAI_COMPATIBLE_REAL_CALLS
NO_ANTHROPIC_REAL_CALLS
NO_DEEPSEEK_API_KEY_FALLBACK
NO_OPENAI_API_KEY_FALLBACK
NO_FRONTEND_LLM_KEY_INPUT
NO_BROWSER_TO_DEEPSEEK_DIRECT_CALL
NO_RAW_ARTIFACT_TO_LLM
NO_UNGROUNDED_INTERPRETATION
NO_PLAN_JOB_OR_ENQUEUE_FOR_NON_READY_OUTCOMES
NO_LLM_ARBITRARY_PYTHON_SHELL_FILESYSTEM_AUTHORITY
NO_LLM_TOOL_REGISTRY_BYPASS
NO_SECRET_PATTERN_HITS
PHASE_10M0_EXECUTABLE_TASK_CREATED = NO
```

## 21. Evidence Inventory

Evidence is under
`docs/phase10l/evidence/phase10l5_natural_language_closure/`. Manifest
`phase10l_closure_a273910a7174c9d33898660c0981ab5a` contains 166 LF-normalized
text/raw-PNG SHA-256 entries. It includes live cases, failed-attempt provenance,
historical inventory/replay, API, browser matrix/screenshots, service,
performance, security, and artifact hashes.

Historical suite
`historical_deepseek_suite_dde5218a3d2121fc038bb90d6daa044a` passed 40/40
supplemental scenarios. Combined current plus historical semantic coverage is
45/45. Pure UI/renderer/accessibility/performance/security flows,
deterministic negative/fault-injection paths, infrastructure-only phases,
superseded tools, and unrecoverable damaged prompt text are explicitly
classified rather than falsely counted as byte-for-byte LLM replay.

## 22. Tests

- focused L1-L5: `199 passed`.
- local full backend: `1078 passed, 38 skipped, 63 warnings`.
- implementation CI unit: `1078 passed, 1 skipped, 37 deselected, 63 warnings`;
  focused L5 closure `99 passed`.
- frontend: 52 files, `333 passed`; typecheck and production build passed.
- service-backed CI: `36 passed, 0 skipped, 0 failed`.
- Chromium/Firefox/WebKit/mobile, evidence finalizer, manifest replay,
  `uv lock --check`, dependency listing, diff check, and secret scan passed.
- `npm audit`: `UNAVAILABLE` because the configured mirror returned
  `404 NOT_IMPLEMENTED`; it is not reported clean.
- existing warnings: pymatgen CIF/spglib deprecations and CI action Node 20
  deprecation notices; none failed a required gate.

## 23. Production Behavior Changes

Real provider selection is DeepSeek-only and environment-key-only. Canonical
Intent/provider output authority is stricter; exact visual forms and the
smallest complete eligible selection are validated. Planner/Runtime authority
is unchanged: persisted validated plans and registered adapters alone execute.
PlannerWorkbench adds sanitized provider/evidence state and never accepts a key
or calls DeepSeek directly.

## 24. Files Changed

- backend/provider: API planner/provider routes, LLM provider, Intent,
  capability/dependency/interpretation guards, redaction, runtime health.
- contracts: Python, JSON Schema, TypeScript natural-language evidence models.
- frontend: PlannerWorkbench, API types, tests, browser runner.
- tests/CI: L1-L5 regressions, service-backed L5, provider strictness, CI gates.
- evidence/docs: 45 semantic cases, browser screenshots/captures/manifests,
  Phase 10L-5 architecture/policy/security/cost/compatibility/closure docs.
- persistent/queue: project state, ADR/registry/open questions, TASKS/results.
- dependency/lockfile/migration changes: none.

## 25. Commit and Exact-SHA CI History

- implementation: `bfc43bd39d7cc2fa319b9e88f9a4d37eec57ee37`.
- implementation exact-SHA CI: run `30693848581`, success.
- required jobs: Unit `91353182658`, Frontend `91353182650`, Service-backed
  `91353182660`, all success.
- failed implementation CI SHA/runs: none.
- local live-provider failed attempts are retained as sanitized evidence; the
  final five-case and 40-case suites pass.
- completion-record and archive SHA/CI: pending this lifecycle.

## 26. Explicit Non-Scope

No Phase 10M Workspace implementation, report/recipe productization,
professional-science expansion, Fermi surface, CrystalNN/VoronoiNN,
experimental XRD comparison engine, advanced trajectory analytics, electronic
Band/DOS, generic workflow/agent/RAG framework, runtime LLM/replanning,
arbitrary Python/shell/filesystem/notebook/script, external scientific API,
enterprise SaaS, plugin marketplace, new LLM SDK, dependency, migration, or
deployment productization was added.

## 27. Remaining Roadmap

```text
Phase 10M-0:
Workspace Information Architecture / Contract
```

This is a reviewer-gated roadmap item, not an executable task.

## 28. Queue State

```text
Phase 10L-5 = COMPLETE / AWAITING_COMPLETION_RECORD_CI
Phase 10L = READY_WITH_EXPLICIT_LIMITS / AWAITING_VERIFIED_ARCHIVE
Phase 10M-0 = REVIEWER_GATE / AWAITING REVIEWER PROMPT
TASK_BLOCK_COUNT = 1
```

## 29. Automatic Phase 10M-0 Entry

```text
NO
PHASE_10M0_EXECUTABLE_TASK_CREATED = NO
```

## 30. Next Action

Verify this completion-record exact-SHA CI, then remove only the completed L5
task block in a separate verified queue-archive commit. Do not create, queue,
or execute Phase 10M-0.

## 31. Final Repository State at Completion Record

- implementation HEAD/origin:
  `bfc43bd39d7cc2fa319b9e88f9a4d37eec57ee37`.
- implementation exact-SHA CI: `30693848581`, success.
- completion-record exact-SHA CI: pending this record's commit.
- archive exact-SHA CI: pending completion-record success.

## Phase 10L-5 Closure Addendum - 2026-08-01 18:03 +08:00

- Completion-record commit:
  `e4b0a8f5619cbb1001ef64809db6400729a99d8d`.
- Completion-record exact-SHA CI: run `30694747664`, `success`.
- Required jobs: Unit Tests `success`; Frontend typecheck/build and L4/L5
  browser replay `success`; PostgreSQL/Redis/MinIO service-backed integration
  `36 passed, 0 skipped, 0 failed`.
- Queue verification: implementation, real DeepSeek evidence, browser/service
  evidence, permanent result, implementation CI, completion record, and
  completion-record CI agree.
- Archive action: the complete Phase 10L-5 `---TASK---` block is deleted by the
  queue-archive commit. Phase 10M-0 remains only a reviewer gate and no
  executable Phase 10M task exists.
- Archive exact SHA and CI run are reported in the reviewer return after the
  final exact-SHA gate; this permanent addendum is not rewritten after archive.

# Phase 10L-4 Grounded Scientific Result Interpretation Result

## 1. Conclusion

```text
PASS / COMPLETE / AWAITING_COMPLETION_RECORD_CI
```

The implementation, local gates, permanent evidence, and corrected exact-SHA
implementation CI are complete. The task remains in `TASKS.md` until this
completion record and the subsequent verified queue archive each pass their
own exact-SHA CI.

## 2. Baseline and Entry Gate

- Phase 10L-3 archive: `8026cb15658f35a8f4c59ef312bd519cead778ae`.
- Phase 10L-3 archive CI: run `30543213225`, success.
- Initial branch/HEAD/origin: `master` / `8026cb15658f35a8f4c59ef312bd519cead778ae`
  / same origin; worktree clean.
- Initial TASKS: one admitted L4 block first and in progress; reviewer-supplied
  L5 pending and blocked by L4 archive.
- Entry gate and current Plan/lineage/migration source audit passed.

## 3. Pre-Implementation Audit

- Existing Adapter summaries, reports, and `summary.md` were reusable display
  foundations but not grounded scientific authority.
- No first-class evidence bundle, claims, numeric/unit/entity grounding,
  interpretation persistence, API, or findings UI existed.
- Existing provider transport was reusable, but raw Artifact text and prior
  summaries were excluded from the L4 provider domain.
- Current Job, ToolCall, ArtifactStorage, dependency execution, and lineage
  repositories supplied exact post-execution authority.
- At least five safe structured contracts were available: numeric table
  summary, ML basic metrics, structure summary, phonon band/DOS/combined, and
  volumetric manifest. Readiness was `PASS`.

## 4. Interpretation Architecture

Terminal Job, exact persisted Plan/execution/lineage, and successful validated
Artifacts feed contract-specific projectors. The resulting immutable evidence
bundle feeds deterministic or strict-provider interpretation and an independent
grounding validator. This service is post-execution and read-only: it cannot
select tools, change Intent/Plan/Job/Artifact, create ToolCalls, or enqueue work.

## 5. Scientific Evidence Contracts

- `ScientificEvidenceBundle 1.0`, `ScientificEvidenceItem 1.0`, and
  `ScientificEvidenceRef 1.0` exist as strict Python, checked-in JSON Schema,
  and TypeScript contracts.
- Identity includes exact project/dataset/Profile/Intent/eligibility/decision/
  plan/graph/job/execution/ToolCall/Artifact checksum/lineage facts.
- Field locators are projector-owned semantic field/entity IDs; path, URL,
  filename, fuzzy label, arbitrary JSON pointer, code, and array-index-only
  authority are rejected.
- Canonical JSON and deterministic hashes exclude runtime timestamps from
  semantic identity. Unknown fields, duplicate JSON keys, non-finite values,
  depth/count/byte overflow, and cross-scope evidence fail typed validation.

## 6. Supported Artifact Families

1. Dataset/property: `table.numeric_summary` / `table_json`.
2. Materials ML: `ml.basic_metrics` / `metrics_json`, using the real six-field
   `n`, MAE, RMSE, R2, mean-error, and max-absolute-error contract.
3. Structure: `structure.summary` / `structure_json`.
4. Phonon: `phonon.band`, `phonon.dos`, and the real L3
   `phonon.band + phonon.dos -> phonon.band_dos` chain.
5. Volumetric: `structure.volumetric_data` structured manifest scope.

The complete Registry inventory is classified in the evidence matrix as
interpretation-ready, deterministic-only, display-only, unsupported-contract,
unsafe-untrusted-text, no-structured-facts, or Future. Unsupported contracts
are not coerced into these five families.

## 7. Evidence Projectors

Projectors are deterministic, exact-contract/version aware, identity/unit
preserving, bounded, no-network, and no-LLM. They project already-computed
facts and warnings only. The corrected ML projector validates the exact real
Adapter payload and cross-metric consistency. It performs no new scientific
analysis, generic JSON parsing, image extraction, unit guessing, or raw text
interpretation. Unsupported or malformed artifacts produce typed source or
no-supported-evidence outcomes.

## 8. Scientific Claim Contract

`ScientificClaim 1.0` supports OBSERVATION, COMPARISON, ANOMALY, WARNING,
LIMITATION, RECOMMENDATION, and NO_SUPPORTED_CONCLUSION with allowlisted
predicates. Confidence is DIRECT, QUALIFIED, or LIMITED, never an invented
probability. Every claim has exact subject/supporting and optional limiting or
contradicting evidence IDs. Platform templates render normal scientific text;
provider proposals cannot add free numeric/unit/entity authority.

## 9. Grounding Validator

The independent validator verifies bundle/artifact/lineage identity, evidence
membership, subject scope, allowlisted predicate, numeric tokens and display
rounding, units/references, comparison compatibility, partial-result
limitations, forbidden conclusions, inert text, and caps. It rejects invented
numbers, units, entities, thresholds, evidence IDs, causal/superlative claims,
unsupported stability/confirmation/deployment/generalization/Bader/charge-
transfer conclusions, and evidence from failed or blocked steps.

## 10. Deterministic Interpreter

The default interpreter creates useful bounded direct observations, propagates
source warnings and partial limitations, emits NO_SUPPORTED_CONCLUSION when
needed, deduplicates and orders claims deterministically, and produces stable
semantic hashes. It does not dump raw JSON, recalculate science, or call an LLM.

## 11. Strict Provider Interpreter

- Reuses the existing bounded OpenAI-compatible transport; no new dependency.
- Provider sees only provider-safe evidence IDs and structured facts plus
  allowlisted claim/predicate/schema/boundary rules.
- Raw Artifact payloads, arrays, paths, URLs, bucket keys, source code,
  Registry, rejected candidates, secrets, and execution APIs are absent.
- Exactly one strict JSON object is accepted. Prose, fences, duplicate keys,
  unknown fields, invented evidence/facts, HTML/script/code/path/URL, non-finite
  values, and over-cap output fail.
- At most one interpretation-specific validation repair is permitted with no
  evidence-domain expansion and no deterministic fallback.
- `REAL_LLM_CALLS = 0`; evidence uses deterministic and fake transport only.

## 12. Interpretation Outcomes

Implemented typed outcomes:

```text
INTERPRETATION_READY
INTERPRETATION_READY_WITH_LIMITS
NO_SUPPORTED_EVIDENCE
SOURCE_NOT_TERMINAL
SOURCE_INTEGRITY_FAILED
EVIDENCE_CAP_EXCEEDED
PROVIDER_FAILED
VALIDATION_FAILED
```

Only grounded READY states persist a ready interpretation. Provider failure is
not relabeled as deterministic success; source integrity failures call no
provider and create no claims.

## 13. Partial Execution Interpretation

ALL_SUCCEEDED uses all supported successful artifacts. PARTIAL_RESULTS uses
only successful lineage-complete artifacts, shows failed/blocked steps and
missing desired outputs first-class, limits every claim, and returns
`INTERPRETATION_READY_WITH_LIMITS`. ALL_FAILED yields no scientific finding.
Successful independent-branch artifacts remain available without extending
their claims to the failed plan scope.

## 14. Recommendations

Recommendations are bounded, evidence-linked, non-executable records with
`executionAuthorized=false`, `planCreated=false`, and `jobCreated=false`.
They contain no tool parameters, code, paths, URLs, shell/notebook content, or
enqueue token. PlannerWorkbench does not render them as Run actions.

## 15. Persistence and Migration

- Alembic `0006_phase10l4_interpretation` adds immutable evidence bundles,
  interpretation runs/records, claims, and evidence links.
- Bundle/run/claim/link/execution identities are deterministic and idempotent;
  conflicting semantic writes fail.
- In-memory, SQLite 0005->0006 upgrade/downgrade/re-upgrade, and PostgreSQL
  full-chain behavior pass.
- No provider authorization or secret is stored.
- Interpretation remains a first-class API/persistence record; no fake
  registered Adapter or ToolCall-produced interpretation artifact was created.

## 16. API

Additive create/list/read/evidence endpoints load the exact terminal job,
verify expected plan and source integrity, project evidence, run the requested
mode, validate, and persist immutable records. Responses expose bounded claims,
evidence links, warnings, limitations, recommendations, partial and repair
state, diagnostics, provenance, and explicit no-execution markers. Running,
tampered, unsupported, provider-failed, and validation-failed cases do not
create ToolCall, Plan, Job, queue message, or scientific Artifact. Legacy API
behavior is unchanged.

## 17. Frontend and Browser

PlannerWorkbench additively displays availability/outcome/mode, findings,
warnings, limitations, non-executable recommendations, evidence counts,
partial banners, provider/repair provenance, and inert audit JSON. Each claim
has keyboard-accessible evidence drill-down with exact value/unit/subject,
contract, tool/version, checksum abbreviation, locator, warning/limitation,
and lineage. Chromium, Firefox, WebKit, and Chromium 390x844 passed deterministic,
strict-fake-provider, partial/no-evidence/failure states, focus/accessibility,
zero horizontal overflow, zero console/page errors, and zero unapproved network.

## 18. Real Evidence Cases

- Dataset/property: exact counts, ranges, missingness, and no anomaly-cause
  invention.
- ML: real registered `ml.basic_metrics` Adapter -> QueueWorkerRuntime ->
  Artifact -> interpretation, with exact target and six metrics.
- Structure: exact structure/site/lattice facts without stability, phase, bond,
  or correctness claims.
- Phonon: persisted AnalysisPlan 0.2 band+DOS->band_dos chain with multi-artifact
  refs, source warnings, and no unconditional stability claim.
- Volumetric: exact quantity/range/reference facts without Bader, topology, or
  charge-transfer claims.
- Partial execution: successful independent DOS evidence only, failed producer
  and blocked consumer limitations, READY_WITH_LIMITS.
- Unsupported contract: NO_SUPPORTED_EVIDENCE and no fake findings.
- Integrity tampering: wrong plan/checksum/cross-job/stale/broken lineage gives
  SOURCE_INTEGRITY_FAILED with zero provider calls and claims.

## 19. Adversarial Evidence

Invented number, unit, entity, evidence ID, threshold, failed-artifact result,
forbidden stability/phase/model/Bader/charge-transfer/structure claims,
duplicate keys, prose/fence, HTML/script, code/path/URL, non-finite values,
oversized/deep payload, and Artifact prompt-injection fixtures are rejected or
exhaust the single repair with `VALIDATION_FAILED`. Artifact strings remain
inert and never enter provider semantic facts or execution authority.

## 20. Compatibility

AnalysisIntent 1.0, DataProfile 2.0, EligibilityResolution 1.0, Tool planner
metadata 1.0/1.1, AnalysisPlan 0.1/0.2, dependency bindings, PlanValidator,
QueueWorkerRuntime, Registry/Adapter execution, Job statuses, Artifact lineage,
historical hashes/jobs/artifacts, and L1-L3 API behavior are unchanged. L4 is
an additive read-only post-execution layer.

## 21. Caps and Performance

- source Artifacts <= 16; evidence items <= 256; warnings <= 128;
  limitations <= 64; table rows/series summaries <= 64;
  refs per claim <= 8; claims <= 32; recommendations <= 8; JSON depth <= 14.
- bundle/provider payload <= 262,144 bytes; interpretation <= 131,072 bytes.
- The near-cap fixture requested 256 evidence items across four source
  Artifacts and produced typed `EVIDENCE_CAP_EXCEEDED` rather than semantic
  truncation; measured local projection was 320.909 ms with 1,207,810 traced
  peak bytes. This is bounded fixture evidence, not a production capacity claim.
- Bounded reads avoid binary/full-array provider payloads; replay is idempotent
  and does not grow duplicate persistence rows.

## 22. Security

```text
REAL_LLM_CALLS = 0
NO_PHASE10L4_UNAPPROVED_EXTERNAL_NETWORK_REQUESTS
NO_INTERPRETATION_ARBITRARY_CODE_EXECUTION
NO_INTERPRETATION_SHELL_OR_FILESYSTEM_AUTHORITY
NO_INTERPRETATION_TOOL_EXECUTION_AUTHORITY
NO_INTERPRETATION_PLAN_MUTATION
NO_INTERPRETATION_JOB_OR_ENQUEUE
NO_RAW_ARTIFACT_PAYLOAD_TO_PROVIDER
NO_UNSUPPORTED_ARTIFACT_TO_PROVIDER
NO_PROVIDER_ARTIFACT_PATH_OR_URL
NO_PROVIDER_SECRET_EXPOSURE
NO_PROVIDER_FULL_REGISTRY_EXPOSURE
NO_REJECTED_CANDIDATE_LEAK_TO_LLM
NO_ARTIFACT_JAVASCRIPT
NO_ARTIFACT_HTML_EXECUTION
NO_ARTIFACT_IFRAME
NO_EXTERNAL_ARTIFACT_URL
NO_CROSS_JOB_INTERPRETATION_EVIDENCE
NO_CROSS_PROJECT_INTERPRETATION_EVIDENCE
NO_STALE_RESOURCE_INTERPRETATION
NO_UNGROUNDED_NUMERIC_CLAIMS
NO_UNGROUNDED_UNIT_CLAIMS
NO_UNGROUNDED_ENTITY_CLAIMS
NO_UNSUPPORTED_SCIENTIFIC_CONCLUSIONS
NO_SECRET_PATTERN_HITS
```

L1-L3 security regressions remain green. No dependency or execution authority
was added.

## 23. Evidence Inventory

`docs/phase10l/evidence/phase10l4_grounded_interpretation/` retains entry and
interpretability audits, six strict schema projections, five family cases,
real phonon/partial runtime, provider isolation, adversarial/integrity cases,
API/persistence/migration/grounding/performance/security audits, browser DOM/
network/console/mobile matrices, desktop/mobile raw PNGs, and an LF-normalized
text/raw-PNG SHA-256 manifest. Committed browser semantics replay exactly in CI.

## 24. Tests

- Focused corrected L4: `37 passed, 3 skipped`; skips are local service cases.
- Local full backend: `955 passed, 33 skipped, 63 warnings`.
- Local frontend: 52 files / `333 passed`; typecheck and production build PASS.
- Local browser: Chromium/Firefox/WebKit and 390x844 mobile PASS.
- Evidence/manifest focused: `4 passed`; lock, dependency tree, diff, migration,
  Phase 10 closure, security and secret markers PASS.
- Local service-backed: `UNAVAILABLE` because Docker is not installed; no PASS
  claim is made.
- Corrected exact-SHA unit: `955 passed, 1 skipped, 32 deselected, 63 warnings`.
- Corrected exact-SHA service-backed: `31 passed, 0 skipped, 0 failed`; Alembic,
  PostgreSQL, Redis, MinIO and no-skipped assertion PASS.
- Corrected exact-SHA frontend: closure, evidence integrity, typecheck,
  Chromium/Firefox/WebKit/mobile semantic replay, and build PASS.
- npm audit: `UNAVAILABLE`; configured mirror status is not reported as clean.

## 25. Production Behavior Changes

- Adds post-execution scientific evidence projection and immutable grounded
  interpretation for terminal persisted jobs.
- Adds deterministic and strict-provider modes with one interpretation repair.
- Adds grounded findings/evidence/limitation UI and read APIs.
- Does not modify Planner selection, AnalysisPlan, PlanValidator, Runtime,
  Registry/Adapter execution, job status, queue, or Artifact execution.
- Recommendations remain non-executable.

## 26. Files Changed

- Backend/contracts: interpretation schemas/models, projectors/interpreters,
  grounding validator, repository/db/API, Alembic 0006.
- Frontend/shared: TypeScript contracts, API types, PlannerWorkbench and styles.
- Tests: contract/projector/provider/validator/persistence/API/Runtime/service/
  frontend/browser/security/evidence cases.
- Evidence/docs: L4 architecture/contracts/boundaries/caps/compatibility/
  readiness, browser runner, captures, screenshots, and manifest.
- Persistent/queue/result records updated. Dependency and lock files unchanged.

## 27. Commit and Exact-SHA CI History

- Initial local implementation: `262ec0e937894990fc800edb2899c0884169d265`.
- First pushed hardening: `3336d9f2ec14153063fe3b2bd1c552e96ed13f82`,
  CI `30604842478` failed service-backed (missing AnalysisPlanV02 fixture import;
  phonon chain honestly returned READY_WITH_LIMITS rather than READY).
- First correction: `0d37ea967b314cb920ac8537e3f75df66fd83918`,
  CI `30605450973` failed service-backed (projector fixture omitted two real ML
  fields; one test queried a non-public evidence response field).
- Corrected implementation: `02a9e33b93f96aa99413dc49ca2dabca652679c9`.
- Corrected implementation exact-SHA CI: run `30606774006`, all required jobs
  success. Failed provenance is retained; history was not rewritten.
- Completion-record SHA/CI: pending this record's commit.
- Verified queue-archive SHA/CI: pending completion-record success.

## 28. Explicit Non-Scope Confirmation

No Phase 10L-5 full evidence closure, Workspace, Report/Recipe productization,
RAG/vector DB/literature/web retrieval, autonomous research loop, runtime LLM/
replanning, interpretation tool selection, recommendation auto-execution, new
Intent/Plan/dependency model, Runtime redesign, arbitrary artifact/JSON/Markdown
authority, arbitrary Python/shell/filesystem/notebook/script, external Artifact
URL or science API, cross-job reuse, new scientific algorithm, CrystalNN/
VoronoiNN, experimental XRD, trajectory analytics, electronic Band/DOS, Fermi
surface, enterprise infrastructure, plugin ecosystem, new LLM SDK, or
uncontrolled dependency was implemented.

## 29. Remaining Phase 10L Gap

```text
Phase 10L-5:
Natural-Language Analysis Evidence Closure + DeepSeek-Only Provider Freeze
```

This is the reviewer-supplied pending task, not work executed during L4.

## 30. Queue State

```text
Phase 10L-4 = COMPLETE / AWAITING_COMPLETION_RECORD_CI
Phase 10L-5 = REVIEWER_APPROVED / QUEUED / BLOCKED_BY_PHASE_10L4_ARCHIVE
TASK_BLOCK_COUNT = 2 pending verified L4 archive
```

## 31. Whether Phase 10L-5 Was Entered Automatically

```text
NO
PHASE_10L5_EXECUTABLE_TASK_CREATED = NO
```

The L5 task was supplied explicitly by the reviewer/user and has not started.

## 32. Next Action

Verify this completion-record exact-SHA CI, then remove only the completed L4
task block in a verified queue-archive commit. After archive CI succeeds, begin
the already reviewer-supplied L5 task under normal queue rules.

## 33. Repository State at Completion Record

- corrected implementation HEAD/origin:
  `02a9e33b93f96aa99413dc49ca2dabca652679c9`.
- corrected implementation CI: `30606774006`, success.
- completion-record CI: pending this record's commit.
- archive CI: pending completion-record success.

## Phase 10L-4 Closure Addendum - 2026-07-31 13:46:09 +08:00

- Completion record commit:
  `45af09e9a0a46f4cdbdb136d979649d2b65f0ff7`.
- Completion-record exact-SHA CI: run `30607509775`, `success`.
- Required jobs: Unit Tests `success`; Frontend Typecheck & Build, evidence
  integrity, Chromium/Firefox/WebKit/mobile replay `success`; PostgreSQL +
  Redis + MinIO migration/service-backed integration `success`; 31 selected
  integration tests passed with zero skipped/failed.
- Queue verification: permanent result, corrected implementation CI, browser/
  evidence, completion record, and completion-record CI agree.
- Archive action: the complete Phase 10L-4 `---TASK---` block is deleted by
  the queue-archive commit. The reviewer-supplied Phase 10L-5 block remains
  `待处理` and is not executed before archive exact-SHA CI succeeds.
- Historical `entry_gate.json` is fixed to the actual L4 admission snapshot;
  future queue changes cannot rewrite L4 evidence.
- Archive commit exact SHA and CI run are reported after the final exact-SHA
  gate; this addendum is not rewritten after archive.

# Phase 10L-3 Bounded Multi-Tool Analysis + Typed Artifact Dependency Execution Result

Completed: 2026-07-30 20:26:23 +08:00

## 1. Conclusion

`PASS` for implementation and implementation exact-SHA CI. The task remains
in `TASKS.md` until this completion record passes exact-SHA CI and a separate
verified queue-archive commit succeeds.

## 2. Baseline and Entry Gate

- Phase 10L-2 archive: `7d032a9c1dafd2a4a76522bcfcd1321fb08b20f9`.
- Phase 10L-2 archive CI: run `30513584587`, success.
- initial branch/HEAD/origin: `master` / `7d032a9c...` / `7d032a9c...`.
- initial worktree: clean; task-block count zero before reviewer-approved L3
  admission, then exactly one L3 block; L4 remained reviewer-gated.

## 3. Pre-Implementation Audit

AnalysisPlan 0.1 represented ordered, sequential independent tool calls; list
order was not a graph and no produced-artifact binding existed. The 38
available tools were audited. One real typed producer/consumer family exists:
`phonon.band` and `phonon.dos` produce canonical artifacts that the registered
`phonon.band_dos` Adapter already consumes. Readiness therefore passed without
adding a scientific algorithm or test-only production tool.

```text
CURRENT_MULTI_TOOL_LEVEL = SEQUENTIAL_INDEPENDENT
SELECTED_PRODUCER_TOOLS = phonon.band, phonon.dos
SELECTED_CONSUMER_TOOL = phonon.band_dos
```

## 4. AnalysisPlan 0.2

Strict additive Python, JSON Schema, and TypeScript contracts add up to four
steps and one plan-level `dependencyBindings` list. Canonical serialization,
deterministic binding/graph/plan hashes, strict unknown-field rejection, and
stable topological ordering are implemented. AnalysisPlan 0.1 remains valid,
unchanged, and is never reinterpreted as dependency-aware.

## 5. Dependency Binding Contract

Each binding owns exact producer step/output port, artifact kind/contract/media
type/cardinality, and exact consumer step/input port. It is the sole graph-edge
authority. List position, filename, display label, array index, wildcard,
path, URL, runtime Artifact ID, and previous-job identity have no authority.

## 6. Artifact Port Metadata

ToolPlannerMetadata 1.1 adds strict output/input ports while 1.0 tools remain
valid independent tools. Exact artifact kind, allowlisted contract version,
media type, cardinality, byte cap, determinism, identity scope, provenance,
visibility, and Adapter binding rules form the deterministic compatibility
matrix. Every mismatch has a typed rejection.

## 7. Bounded Composer

The deterministic composer uses only L2-selected tools and compatible ports;
it never infers edges from co-occurrence or wording. The optional fake-provider
path sees selected IDs and compatible pairs only, accepts one strict JSON
object, shares L2's total one-repair budget, and cannot expand tools, targets,
resources, ports, contracts, or caps. There is no Mock fallback.

## 8. Validation

An independent dependency validator recomputes identities, ports, binding IDs,
caps, acyclicity, depth, deterministic topology, eligibility membership,
parameter provenance, collision/composition, and scope before existing
capability-context and PlanValidator gates. Self/two-node/transitive cycles,
unknown or duplicate edges/ports, invented/rejected tools, wildcard/path/URL,
cross-job/project, stale identity, checksum/contract/media/size mismatch, and
cap overflow fail with bounded typed diagnostics.

## 9. Persistence and Migration

Alembic `0005_phase10l3_dependency_execution` adds relational audit storage for
planned bindings, runtime binding resolutions, dependency execution records,
and artifact lineage while plan JSON remains semantic authority. In-memory,
SQLite upgrade/downgrade/re-upgrade, and PostgreSQL paths preserve immutable,
idempotent records and reject conflicting semantic writes. AnalysisPlan 0.1
and 0.2 round-trip through the existing repository.

## 10. QueueWorkerRuntime

Only the 0.2 path loads the exact persisted plan, verifies its hash, revalidates
dependencies, computes deterministic topology, and executes serially through
Tool Registry and registered Adapters. Runtime resolves platform-created,
checksummed, same-plan/job/project artifact refs through ArtifactStorage before
consumer invocation. It never replans, calls an LLM, or falls back to source
data when an artifact is missing.

## 11. Partial Execution Semantics

Producer or consumer failure blocks descendants only. Independent branches
continue; successful artifacts remain; binding failures occur before consumer
Adapter invocation. Step and binding states distinguish failures from
`BLOCKED_DEPENDENCY`. The additive overall record reports `ALL_SUCCEEDED`,
`PARTIAL_RESULTS`, `ALL_FAILED`, or `VALIDATION_ABORTED` while legacy Job status
semantics remain compatible. Replay creates no duplicate calls/artifacts/edges.

## 12. Artifact Lineage

Lineage records exact project/dataset/Profile/Intent/eligibility/decision/plan/
graph/job identities, producer tool/step/call/output port, artifact kind/
contract/media/checksum, upstream artifact and binding IDs, runtime/Adapter
provenance, caps, and warnings. Lineage never depends on array position or
report text.

## 13. Real Dependent Chain Evidence

- `phonon.band:canonical-band` -> `phonon.band_dos:band` using
  `phonon_band_json / phase10h.phonon_band.v1 / application/json`.
- `phonon.dos:canonical-dos` -> `phonon.band_dos:dos` using
  `phonon_dos_json / phase10h.phonon_dos.v1 / application/json`.
- The persisted three-step plan executes `step_001`, `step_003`, then
  `step_002`; both bindings resolve and the result is `ALL_SUCCEEDED`.
- Replay retains the same semantic plan/graph hashes and no duplicate runtime
  records.

## 14. Failure and Rejection Evidence

Producer-failure evidence records the producer `FAILED`, combined consumer
`BLOCKED_DEPENDENCY` without Adapter invocation, independent DOS producer
`SUCCEEDED`, retained DOS artifacts, and `PARTIAL_RESULTS`. Consumer failure,
checksum/contract/media/identity/size/port mismatch, cycles, and graph caps are
also retained as typed captures.

## 15. API

Canonical READY requests compose/validate/persist 0.2 before job creation and
enqueue. Additive responses and `/planner/jobs/{job_id}/dependencies` expose
schema/hash/graph/topology/bindings/execution/lineage. Non-ready and invalid
dependency cases create no plan, job, ToolCall, Artifact, or queue message.
Legacy 0.1 APIs remain readable and executable through their unchanged path.

## 16. Frontend and Browser

PlannerWorkbench additively shows schema version, exact tools/params, dependent
and independent steps, ports/contracts, topology, validation, runtime states,
blocked causes, partial results, lineage, and inert audit JSON. It is an
accessible list/card/table surface, not an editor. Chromium 128, Firefox 128,
WebKit 18, and Chromium 390x844 passed success/partial cases, keyboard focus,
status labels, zero horizontal overflow, zero console/page errors, and zero
external requests.

## 17. Compatibility

AnalysisIntent 1.0 and EligibilityResolution 1.0 are unchanged. AnalysisPlan
0.1 schemas and hashes remain unchanged/readable, and only 0.2 receives
dependency runtime semantics. Registry execution authority, PlanValidator,
L1/L2 candidate isolation/exact binding, historical jobs/artifacts, Phase 10K,
and legacy API behavior remain intact.

## 18. Caps and Performance

Caps are four steps, six bindings, depth four, three incoming/outgoing edges,
one total repair, and 524,288 serialized planning bytes. The legal near-cap
fixture used four steps/six bindings/depth four, 3,619 serialized bytes,
43,486 traced peak bytes, and 2.523 ms local validation/sort time. This proves
bounded behavior only, not production capacity.

## 19. Security

```text
REAL_LLM_CALLS = 0
NO_PHASE10L3_UNAPPROVED_EXTERNAL_NETWORK_REQUESTS
NO_DEPENDENCY_ARBITRARY_CODE_EXECUTION
NO_DEPENDENCY_SHELL_OR_FILESYSTEM_AUTHORITY
NO_ARTIFACT_JAVASCRIPT
NO_ARTIFACT_HTML_EXECUTION
NO_ARTIFACT_CALLBACK
NO_ARTIFACT_SHADER
NO_ARTIFACT_MODULE
NO_EVAL
NO_FUNCTION_CONSTRUCTOR
NO_EXTERNAL_ARTIFACT_URL
NO_CROSS_JOB_ARTIFACT_BINDING
NO_CROSS_PROJECT_ARTIFACT_BINDING
NO_STALE_RESOURCE_BINDING
NO_UNDECLARED_ARTIFACT_PORT
NO_PROVIDER_ARTIFACT_PAYLOAD_EXPOSURE
NO_REJECTED_CANDIDATE_LEAK_TO_LLM
NO_FULL_REGISTRY_LEAK_TO_LLM
NO_PLAN_JOB_OR_ENQUEUE_FOR_NON_READY_OUTCOMES
NO_SECRET_PATTERN_HITS
```

Prompt/artifact injection, HTML/script, credentials, duplicate keys, path/URL,
oversized/nested content, stale/foreign artifacts, and hash/contract/media
tampering remain inert or typed failures. No new dependency or execution
authority was added.

## 20. Evidence Inventory

`docs/phase10l/evidence/phase10l3_bounded_multi_tool/` retains entry/schema,
38-tool inventory, compatibility/real chain, success/partial/failure runtime,
API, migration/persistence, lineage, performance/security, browser DOM/network/
console/accessibility, desktop/mobile PNGs, and an LF-normalized text/raw-PNG
SHA-256 manifest.

## 21. Tests

- local full backend: `917 passed, 30 skipped, 63 warnings`.
- exact-SHA CI unit: `917 passed, 1 skipped, 29 deselected, 63 warnings`;
  Phase 10 closure `3 passed, 6 deselected`.
- final L1/L2/L3 focused backend: `70 passed`.
- L3 persistence/service-local: `5 passed, 1 skipped`; local services are
  `UNAVAILABLE`, not reported as PASS.
- exact-SHA service-backed: `28 passed, 0 skipped, 0 failed`; PostgreSQL,
  Redis, MinIO, Alembic head, tables/indexes, and no-skipped PASS.
- frontend: 52 files / `328 passed`; typecheck and production build PASS.
- browser: Chromium/Firefox/WebKit and 390x844 mobile PASS.
- lock, npm dependency tree, diff, evidence manifest, Phase 10 closure, docs/
  TASKS checks, and secret scan PASS.
- npm audit: `UNAVAILABLE`; configured mirror returned `404 NOT_IMPLEMENTED`,
  so no clean claim is made.

## 22. Production Behavior Changes

- Canonical dependent work can now produce AnalysisPlan 0.2.
- Only 0.2 uses deterministic dependency validation/topological Runtime.
- Runtime creates exact artifact refs and immutable execution/lineage records.
- Failed branches block descendants while independent work continues.
- API and PlannerWorkbench expose additive graph/partial/lineage state.
- AnalysisPlan 0.1 and its Runtime behavior remain unchanged.

## 23. Files Changed

Backend schemas, repositories/API and Alembic migration; Tool Registry port
metadata/validator; Planner composer; QueueWorkerRuntime; TypeScript/shared
schemas; PlannerWorkbench/styles/API types; focused/integration/browser tests;
CI; evidence and screenshots; Phase 10L/shared docs; persistent records and
TASKS. Dependency and lock files are unchanged.

## 24. Commit and Exact-SHA CI History

- implementation: `d395db2a4f59e2f5fb72e0b33b45161b2bcb5670`.
- implementation exact-SHA CI: run `30542148803`, all required jobs success.
- failed implementation CI attempts: none.
- completion-record and archive SHA/CI follow in the closure addendum.

## 25. Explicit Non-Scope Confirmation

No generic DAG/workflow engine, parallel scheduler, loops/conditions/fan-out,
runtime replanning/LLM, extra repair or retry redesign, plan editor/approval,
cross-job/remote artifact input, arbitrary artifact binding, Python/shell/
filesystem/notebook/script authority, external science API, interpretation,
full natural-language evidence closure, Workspace, professional science,
Fermi surface, CrystalNN, experimental XRD, advanced trajectory, Band/DOS,
enterprise infrastructure, plugin ecosystem, new LLM SDK, or uncontrolled
dependency was implemented.

## 26. Remaining Phase 10L Gaps

```text
Phase 10L-4: Grounded Scientific Result Interpretation
Phase 10L-5: Natural-Language Analysis Evidence Closure
```

These are reviewer-gated gaps, not executable tasks.

## 27. Queue State

```text
Phase 10L-3 = COMPLETE / AWAITING_COMPLETION_RECORD_CI
Phase 10L-4 = REVIEWER_GATE / AWAITING REVIEWER PROMPT
TASK_BLOCK_COUNT = 1 pending verified archive
```

## 28. Whether Phase 10L-4 Was Entered Automatically

```text
NO
PHASE_10L4_EXECUTABLE_TASK_CREATED = NO
```

## 29. Next Action

Verify this completion-record exact-SHA CI, then create and verify the separate
queue-archive commit. Return the complete result and stop. Do not create,
queue, or execute Phase 10L-4.

## 30. Repository State at Completion Record

- implementation HEAD/origin: `d395db2a4f59e2f5fb72e0b33b45161b2bcb5670`.
- implementation CI: `30542148803`, success.
- completion-record CI: pending this record's commit.
- archive CI: pending completion-record success.

## Phase 10L-3 Closure Addendum - 2026-07-30 20:32:51 +08:00

- Completion record commit:
  `2bd06f22562a9fb1baf65730d30682c1d0ca6c54`.
- Completion-record exact-SHA CI: run `30542844246`, `success`.
- Required jobs: Unit Tests `success`; Frontend Typecheck & Build `success`;
  PostgreSQL + Redis + MinIO migration/service-backed integration `success`;
  28 selected integration tests passed with zero skipped/failed.
- Queue verification: permanent result, implementation CI, browser/evidence,
  completion record, and completion-record CI agree.
- Archive action: the complete Phase 10L-3 `---TASK---` block is deleted by
  the queue-archive commit; Phase 10L-4 remains only a reviewer gate and no
  executable Phase 10L-4 task exists.
- Archive commit exact SHA and CI run are reported in the reviewer return after
  the final exact-SHA gate; this addendum is not rewritten after archive.

# Phase 10M-0 Unified Scientific Workspace Fact Audit + Information Architecture Seal Result

Completion date: 2026-08-01 (Asia/Shanghai)

## 1. Conclusion

```text
PASS / COMPLETE / REVIEWER_APPROVAL_REQUIRED
```

The repository fact audit, information architecture seal, implementation
backlog, acceptance map, execution lock, and execution manifest are complete.
No Phase 10M production implementation was performed.

## 2. Baseline

- Branch: `master`.
- Initial `HEAD == origin/master`:
  `8f304fa08ddab1cefd69848f621f8438fc2038d5`.
- Phase 10L-5 implementation:
  `bfc43bd39d7cc2fa319b9e88f9a4d37eec57ee37`; CI `30693848581`, success.
- Phase 10L-5 completion record:
  `e4b0a8f5619cbb1001ef64809db6400729a99d8d`; CI `30694747664`, success.
- Phase 10L-5 verified queue archive:
  `8f304fa08ddab1cefd69848f621f8438fc2038d5`; CI `30695065220`, success.
- Entry worktree: clean. `TASK_BLOCK_COUNT = 0`.
- Phase 10M production source implementation at entry: absent.

## 3. Production Behavior Changes

```text
Production Behavior Changes:
NONE
```

Production source, schemas, migrations, API, frontend behavior, Tool Registry,
Adapters, Runtime, dependencies, lockfile, and `TASKS.md` are unchanged.

## 4. Current Workspace Maturity

```text
CURRENT_WORKSPACE_LEVEL = WORKSPACE_LIKE_SINGLE_PAGE
```

PlannerWorkbench on `/` exposes data setup, intent/planning, execution,
artifacts, interpretation/evidence, report/recipe summaries, and audit JSON in
one page. It is not a formal Workspace: there is no Workspace identity, route,
aggregate persistence/API, history browser, deep link, saved layout, or global
canonical selection context.

## 5. Current Route / Component / API Map

The current product has root `/`, framework 404/icon routes, PlannerWorkbench,
product-specific preview panels, timeline/dependency/interpretation sections,
and six independent read paths for plans/jobs/events/tool calls/artifacts and
interpretations. The complete implementation-grounded map is retained in
`docs/phase10m/phase10m0_current_page_route_component_map.md` and evidence
`route_inventory.md`, `component_inventory.md`, and `api_inventory.md`.

## 6. Current Domain / Persistence

Job is the current analysis container. Persisted Plan -> Job -> ToolCall ->
Artifact relations, dependency execution, lineage, evidence bundles,
interpretations, Reports, and Recipes are sufficient for deterministic lazy
Workspace projection. No Workspace/session projection or UI-state persistence
currently exists.

## 7. Current Artifact / Renderer Surface

The audit covers Registry `0.1.0`, 53 registered tools, 38 Planner-visible
tools, typed artifacts, viewers, generic inert fallback, download behavior,
lineage, and 12 grounded projector combinations. Product-specific scientific
renderers are reusable; generic JSON/text preview is not classified as a ready
scientific panel. The full matrix is retained in
`phase10m0_artifact_renderer_matrix.md`.

## 8. Current Interpretation / Evidence Surface

ScientificEvidenceBundle 1.0 and GroundedScientificInterpretation 1.0 are
persisted per terminal Job. PlannerWorkbench shows findings, warnings,
limitations, evidence drill-down, partial disclosure, provider/repair state,
and inert audit JSON. There is no cross-panel evidence inspector or Workspace
deep link today.

## 9. Current Report / Recipe Surface

Report and Recipe are existing persisted first-class records, but current UI
exposes summary/inert preview rather than composition, selection, export, and
history workflows. Phase 10M reuses their ownership and does not create a
second report/recipe authority.

## 10. Identity and Lineage

The audit maps Project, Dataset/version, Profile, object/sample, structure/site,
trajectory atom/frame, phonon q-point/branch, reciprocal point, volumetric
field, Intent, Eligibility, Plan/step/binding, Job, ToolCall, Artifact/lineage,
Evidence, Claim, Interpretation, Report, and Recipe identities. Cross-panel
selection must use exact stable IDs and source versions; array index, display
label, row order, fuzzy matching, and unit guessing are forbidden.

## 11. Current State and Error Taxonomy

Existing Job, ToolCall, dependency execution, binding, interpretation, and
renderer states remain sources of truth. The sealed Workspace/panel taxonomy is
an explicit UI/domain projection over those states; it does not rename or
rewrite historical execution records.

## 12. Browser / Responsive / Accessibility Facts

- Current L5 replay: Chromium, Firefox, WebKit desktop and Chromium 390x844;
  five ready cases plus clarification, unsupported, and capability mismatch.
- Current L4 replay: three desktop browsers and Chromium mobile for findings,
  evidence, partial, no-evidence, validation, and integrity states.
- Console/page errors: 0. Unapproved external requests: 0. Live API/provider
  forwarding: 0. `REAL_LLM_CALLS = 0`.
- Firefox/WebKit mobile: `UNAVAILABLE`; not inferred from desktop.
- Current long expanded audit JSON produces a very tall mobile document and is
  an explicit Phase 10M-6 presentation target, not a false current PASS claim.

## 13. Frontend Scientific Authority Audit

```text
FRONTEND_DUPLICATE_SCIENTIFIC_AUTHORITY = NONE
```

Current scientific authority remains Registered Adapter -> QueueWorkerRuntime
-> persisted Artifact -> validated frontend mapper. Frontend calculations are
limited to display formatting, sorting/filtering, camera/coordinate display,
and contract-approved bounded presentation behavior.

## 14. Workspace Information Architecture Decision

The sealed desktop IA is Workspace header plus side navigation for Data, Plan,
Execution, Results, Findings, Evidence, Provenance, and Report; a central panel
stack; and one exact-identity inspector. PlannerWorkbench remains the `/`
analysis entry and successful persisted Jobs navigate to the Workspace route.

## 15. Workspace Entity / Cardinality Decision

```text
WORKSPACE_IS_FIRST_CLASS_PERSISTED_ENTITY = YES
WORKSPACE_CARDINALITY = ONE_WORKSPACE_PER_JOB
```

ScientificWorkspace 1.0 stores exact source references and version/hash
bindings. It never copies source science or caches Artifact payload as source
of truth. Mutable user layout/title state is separated from immutable runtime
references and revisioned.

## 16. Persistence Decision

Server persistence owns Workspace identity, panel membership/layout revisions,
title, and durable user state. URL owns active panel and exact shareable
selection; memory owns transient camera/expanded-row state. Canonical state is
not stored in localStorage/sessionStorage.

## 17. Database Migration Decision

```text
DATABASE_MIGRATION_REQUIRED = YES
```

Phase 10M-1 adds Alembic `0007_phase10m1_workspace_domain` with
`scientific_workspaces`, `workspace_panels`, and
`workspace_layout_revisions`; exact nullability, defaults, FKs, uniqueness,
indexes, `ON DELETE RESTRICT`, upgrade/downgrade, and no-backfill lazy projection
policy are sealed. No migration was created in Phase 10M-0.

## 18. API Decision

```text
NEW_WORKSPACE_API_REQUIRED = YES
```

Sealed additive endpoints cover create/project, get, patch with `If-Match`,
project list, source-Job projection, panel/history reads, and exact M5
Report/Recipe composition endpoints. Create is idempotent on
`(projectId, sourceJobId)` and does not require `If-Match`. No API was added in
Phase 10M-0.

## 19. Route / Navigation Decision

Canonical route: `/workspaces/{workspaceId}`. `/` remains PlannerWorkbench.
Query state carries `panel` and versioned exact selection only. Browser
back/forward restores those states; missing/stale sources render typed
read-only states rather than silent rebinding.

## 20. Panel Contract Decision

```text
PANEL_CONTRACT_REQUIRED = YES
```

WorkspacePanel 1.0 owns panel ID/kind/title, source refs, renderer contract,
state/error/partial projections, exact selection I/O, evidence/provenance,
layout/mobile/accessibility metadata, capability requirement, and inert
unsupported fallback. Maximum panels per Workspace: 32.

## 21. Selection Context Decision

WorkspaceSelectionContext 1.0 is required. It carries exact identity kind/ID,
source dataset/resource/artifact version and hash, scope, propagation,
compatibility, clearing, bounded multi-selection, URL encoding, subscriptions,
and typed stale/unsupported mapping. The server does not persist ephemeral
selection.

## 22. Report / Recipe Decision

Existing Report and Recipe persistence remains authoritative. M5 adds
composition APIs without new report/recipe tables. Reports retain partial and
failed disclosures, evidence, lineage, selected panels/findings, and export.
Recipes bind exact Profile, Intent, Plan, tool versions, parameters,
dependencies, and artifact contracts.

```text
recommendation != executable plan
```

## 23. Historical Compatibility Decision

Historical Jobs use idempotent lazy Workspace projection, not bulk backfill.
AnalysisPlan 0.1/0.2, old Jobs/Artifacts, jobs without interpretation or graph,
partial execution, missing Profile, stale dataset versions, legacy reports and
recipes are preserved and projected as typed read-only/stale/unsupported states.
Scientific identities are never silently upgraded.

## 24. Mobile / Accessibility Decision

Mobile uses one active panel, a dataset/context drawer, a panel switcher, and
an inspector bottom sheet; it is not a compressed desktop split view. Sealed
accessibility includes deterministic focus order, visible focus, semantic
headings, status announcements, non-color state, table/chart/WebGL text
alternatives, reduced motion, zoom, and at least 44x44 CSS-pixel touch targets.

## 25. Performance / Loading Decision

Workspace loads identity/status/panel metadata first, then lazy artifact data.
Heavy viewers load on activation; requests are cancellable; WebGL contexts and
observers are disposed on unmount. Cache keys include Workspace revision and
source hashes; stale invalidation is exact. Adjacent panel metadata prefetch is
disabled. Limits include 32 panels and 128 layout revisions; revision 129 is a
typed `REVISION_CAP_EXCEEDED` rejection. Targets are development/browser
acceptance targets, not production capacity claims.

## 26. Security Boundary

Artifact content remains inert data: no artifact HTML/JavaScript/iframe/module,
no external artifact URL execution, no arbitrary code/shell/filesystem, no
provider authority, no recommendation-to-plan/job/enqueue, no cross-job or
cross-project artifact access, no stale identity rebinding, and no credential,
path, or stack disclosure. New/changed audit content has zero secret-pattern
or private-path hits.

## 27. Decision Log

M-D001 through M-D025 are all
`SEALED_FOR_REVIEWER_APPROVAL`: Workspace entity/cardinality, persistence,
migration, API, route, historical projection, Panel/renderer/selection,
Report/Recipe, partial/error, mobile/accessibility/performance/WebGL/security,
compatibility, PlannerWorkbench transition, save/recovery, deep links,
staleness, and Phase ordering. No implementation-affecting decision is blocked.

## 28. Phase 10M Implementation Sequence

1. 10M-1: Workspace Domain Contract + Persistence.
2. 10M-2: Unified Workspace Shell.
3. 10M-3: Cross-Artifact Navigation + Canonical Selection.
4. 10M-4: Typed Artifact Gallery + Scientific Viewer Integration.
5. 10M-5: Scientific Report + Recipe Composition.
6. 10M-6: Save / Reload / Recovery / Responsive Closure.
7. 10M-7: Workspace Integration + Browser/API/Service Evidence Closure.

Each phase has exact source/schema/database/API/frontend/test/browser/service/
security scope, entry/exit gates, dependencies, and non-scope in
`phase10m_implementation_backlog.md`.

## 29. Acceptance and Test Plan

The plan defines 53 unique acceptance IDs: M1=8, M2=7, M3=7, M4=8, M5=7,
M6=8, M7=8. The acceptance plan and execution lock contain exactly the same
ID set with zero missing, extra, duplicate, or shorthand entries.

## 30. Execution Lock

`phase10m_execution_lock.md` freezes facts, 25 decisions, files, migration,
API/schema/route/panel/selection/report/security/performance/compatibility
boundaries, M1-M7 order, stop conditions, and reviewer gates.

```text
The implementation agent is not authorized to redesign
Workspace identity, persistence, API, migration, routing,
panel contracts, selection identity, report ownership,
compatibility, security, or Phase ordering.
```

## 31. Execution Manifest

`phase10m_execution_manifest.md` is the sole high-level implementation entry.
It records baseline, canonical docs, decision IDs, phases, modules, migration,
APIs, schemas, routes/components, tests, browsers, services, CI, evidence,
security markers, completion format, stop conditions, and reviewer gates.

## 32. Files Changed

- Audit/planning commit: 156 files, all under `docs/` or `persistent/`.
- Added 22 canonical Phase 10M documents and the retained audit evidence tree.
- Updated docs index/roadmap/shared-schema proposal and seven persistent records.
- `production source = unchanged`.
- `dependencies = unchanged`; `lockfile = unchanged`.
- `TASKS.md = unchanged`.
- This completion record appends `results.md` and updates persistent completion
  state only.

## 33. Checks

- `git diff --check`: PASS.
- `uv lock --check`: PASS, 108 packages resolved; lock unchanged.
- Focused backend: 292 passed.
- Full local backend: 1078 passed, 38 skipped, 63 warnings; local services were
  unavailable, so integration skips are not claimed as service PASS.
- Full local frontend: 52 files, 333 tests passed; focused: 15 files, 129 passed.
- Typecheck/build/npm dependency tree: PASS.
- Current browser audit: Chromium/Firefox/WebKit desktop and Chromium 390x844
  capture replay PASS for the audited current surfaces.
- Exact-SHA CI Unit: 1078 passed, 1 skipped, 37 deselected, 63 warnings;
  Phase 10L-5 closure 99 passed.
- Exact-SHA CI service-backed: 36 passed, 0 skipped, 0 failed, 0 errors.
- Evidence manifest: 123 retained files, zero hash/membership mismatches.
- Docs links: 40 documents checked, zero invalid local links.
- `TASK_BLOCK_COUNT = 0`; `TASKS.md` diff zero.
- New/changed secret scan: PASS; `NO_SECRET_PATTERN_HITS`.
- `LOCAL_SERVICE_BACKED = UNAVAILABLE`; `CI_SERVICE_BACKED = PASS`.
- `npm audit = UNAVAILABLE` because the configured mirror returned
  `404 NOT_IMPLEMENTED`; it is not reported clean.
- Known non-blocking warnings: existing pymatgen/spglib warnings and GitHub
  Actions Node 20 deprecation notices.

## 34. Commit / CI

- Audit/planning commit:
  `4c5d25ef00b2213683a3115febc5f482546cc522`.
- Audit/planning exact-SHA CI: run `30698489359`, success; Unit, Frontend,
  browser replay/build, PostgreSQL/Redis/MinIO, and no-skipped jobs succeeded.
- Completion record: the commit containing this append-only section.
- Completion-record exact-SHA CI: required before final reviewer return; exact
  SHA and run are reported from immutable Git history in the final return.
- Failed audit/planning CI attempts: none.

## 35. Explicit Non-Scope

No Workspace production contract, migration, API, UI, route, panel renderer,
selection runtime, report productization, save/reload behavior, Phase 10N
science, source code, dependency, lockfile, real DeepSeek, or other real LLM
call was implemented. No Workspace/DAG/workflow editor, new scientific
algorithm/tool, arbitrary code/shell/filesystem/network authority, RAG,
memory, multi-agent product, plugin market, or autonomous replanning was added.

## 36. Reviewer Decisions

```text
NO IMPLEMENTATION DECISION IS LEFT TO THE EXECUTION AGENT
```

The reviewer only approves or revises this sealed proposal. Any revision to
identity, cardinality, migration, API, route, Panel/Selection contract,
Report/Recipe ownership, compatibility, security, or phase ordering requires a
new reviewer decision.

## 37. Queue State

```text
Phase 10M-0:
COMPLETE / REVIEWER_APPROVAL_REQUIRED

Phase 10M-1:
REVIEWER_GATE / AWAITING REVIEWER PROMPT

TASK_BLOCK_COUNT = 0

TASKS.md:
UNCHANGED
```

## 38. Automatic Phase 10M-1 Entry

```text
NO
PHASE_10M1_EXECUTABLE_TASK_CREATED = NO
```

## 39. Next Action

```text
Return the complete Phase 10M-0 result to the reviewer.
Do not create, queue, or execute Phase 10M-1.
```

## 40. Final Repository State

- Audit/planning SHA: `4c5d25ef00b2213683a3115febc5f482546cc522`.
- Audit/planning CI: `30698489359`, success.
- Completion record: this results-bearing commit; exact SHA/CI reported in the
  final reviewer return after its required exact-SHA gate.
- Expected final state after that gate: `HEAD == origin/master`, clean,
  `TASK_BLOCK_COUNT = 0`, production source unchanged.

# Phase 10M-1 Scientific Workspace Domain Contract + Persistence Result

## 1. Conclusion

```text
PASS / COMPLETE / AWAITING_COMPLETION_RECORD_CI
```

The reviewer-sealed Workspace domain, persistence, migration, projection, and
API scope is implemented. Corrected implementation exact-SHA CI is successful;
the task remains in `TASKS.md` until completion-record and queue-archive CI
succeed.

## 2. Baseline and Entry Gate

- Phase 10M-0 audit/planning: `4c5d25ef00b2213683a3115febc5f482546cc522`,
  CI `30698489359` success.
- Phase 10M-0 completion: `2f4a5682fbc2adb0fdc487a982ec508f138eb41a`,
  CI `30698988085` success and reviewer approved.
- Initial `HEAD == origin/master == 2f4a5682fbc2adb0fdc487a982ec508f138eb41a`,
  branch `master`, worktree clean, migration head `0006`.
- Queue admission produced one exact M1 block; M2 remained a reviewer gate.

## 3. Phase 10M-0 Decision Compliance

M-D001 through M-D025 remain unchanged. One Workspace per Job, the three-table
schema, explicit projection, reference-only science authority, API ownership,
Panel/Selection contracts, route ownership, compatibility, security, and
M1-M7 ordering were implemented without redesign.

## 4. ScientificWorkspace 1.0

The strict contract binds deterministic Workspace identity to exact
`(projectId, sourceJobId)`, records immutable dataset/Profile/Intent/Plan source
versions and hashes, and permits only bounded title, active-panel, pinned exact
selection, durable metadata, and revision changes. Unknown fields, invalid
IDs/hashes, prototype keys, non-finite values, deep/oversized payloads, and
executable content are rejected. `executionAuthorized=false` and
`scientificAuthority=false` are explicit.

## 5. WorkspacePanel 1.0

Panel descriptors retain exact Workspace/source/Artifact/ToolCall/step and
renderer-contract references, projected state, evidence/provenance links,
layout and accessibility metadata, and deterministic order. Unsupported sources
become inert fallback descriptors. `MAX_PANELS_PER_WORKSPACE=32`; panel 33 is a
typed rejection. Artifact payloads and arbitrary component/module authority are
not stored.

## 6. WorkspaceSelectionContext 1.0

The strict value contract uses exact source-scoped identities, bounded
multi-selection, exact-only propagation, deterministic serialization, and a
2,048-byte URL representation. Display labels, row/array position, fuzzy/latest
rebinding, raw prompts/payloads, URLs, paths, credentials, and expressions are
rejected. M1 implements validation/serialization only; ephemeral selection is
not persisted and propagation remains M3 scope.

## 7. Canonical Identity and Source Binding

Workspace source bindings point to existing Project, Job, dataset/version,
Profile/hash, Intent/hash, Eligibility/decision where available, Plan/hash,
dependency execution, Artifacts/hashes/contracts, interpretation, Report, and
Recipe records. Sources remain immutable; stale or missing identities produce
typed projection state rather than latest-wins substitution.

## 8. Persistence Architecture

Repository protocols, in-memory implementation, and SQLAlchemy implementation
share create/get/list/update, panel, and layout-history semantics. Immutable
source conflicts, stale compare-and-set updates, cross-project access, duplicate
records, cap overflow, and SQL integrity failures are translated to bounded
typed errors. Workspace records store references and durable presentation data,
not source scientific values.

## 9. Database Migration

Alembic `0007_phase10m1_workspace_domain` creates exactly:

- `scientific_workspaces`;
- `workspace_panels`;
- `workspace_layout_revisions`.

It adds project/job and child lookup indexes, one-row-per-project/job uniqueness,
unique Workspace revision ordering, sealed foreign keys and `ON DELETE
RESTRICT` source behavior. SQLite `0006 -> 0007 -> 0006 -> 0007`, fresh
`0001 -> 0007`, and PostgreSQL migration/service inspection pass. There is no
backfill and `metadata.create_all()` is not migration authority.

## 10. Repository Implementations

In-memory and SQLAlchemy repositories pass parity tests for idempotent create,
conflicting create, exact lookup, project list, mutable title/layout update,
immutable source rejection, stale revision conflict, panel order, history,
rollback, cap handling, and project isolation.

## 11. Workspace Creation

Explicit create/project validates the exact Project and source Job, computes
immutable source bindings, projects bounded panel descriptors, appends initial
layout revision, and returns the same Workspace for semantic retries. Ordinary
GET/list operations never create a Workspace. No tool, provider, planner, Job,
enqueue, or Artifact payload read is part of creation.

## 12. Layout Revisions

Layout revisions are immutable, monotonic, canonically serialized, and bound to
panels owned by the Workspace. PATCH uses quoted `If-Match`; stale or malformed
ETags are typed errors. `MAX_LAYOUT_REVISIONS=128`; revision 129 returns
`REVISION_CAP_EXCEEDED` without deleting history.

## 13. Historical Job Projection

Explicit lazy projection covers Plan 0.2 and historical 0.1 Jobs, graph/no-graph,
all-succeeded/partial/failed/running states allowed by the seal, missing
interpretation/Profile/Artifact, stale datasets, legacy Artifacts, and
Report/Recipe presence or absence. Legacy records remain read-only where
required; no graph, interpretation, Artifact, or identity is invented. Repeated
projection is idempotent; there is no bulk backfill or hidden GET write.

## 14. Workspace API

Implemented additive routes:

- `POST /workspaces`;
- `GET|PATCH /workspaces/{workspaceId}`;
- `GET /projects/{projectId}/workspaces`;
- `GET /projects/{projectId}/analysis-jobs`;
- `GET /workspaces/{workspaceId}/panels`;
- `GET /workspaces/{workspaceId}/panels/{panelId}`;
- `GET /workspaces/{workspaceId}/layout-revisions`;
- `GET /workspaces/{workspaceId}/layout-revisions/{revision}`.

Create uses `Idempotency-Key`; PATCH uses `If-Match`; reads are metadata-only
and bounded. Strict duplicate-key/unknown-field/UTF-8/size validation and typed
error envelopes prevent stack, SQL, path, storage-key, secret, or provider
disclosure. TypeScript client functions match these contracts.

## 15. Optimistic Concurrency

Workspace revision and ETag are exact compare-and-set identities. A valid PATCH
appends an immutable revision and advances the current pointer atomically;
stale writes return a typed conflict and cannot overwrite newer state.

## 16. Project and Source Isolation

Project, Job, Workspace, panel, layout, and source Artifact scopes are checked
before reads or writes. Cross-project Jobs, foreign Artifacts, stale hashes,
unknown panels, and cross-Workspace layout references are rejected.

## 17. Scientific Integrity

```text
WORKSPACE_COPIED_ARTIFACT_PAYLOADS = 0
FRONTEND_DUPLICATE_SCIENTIFIC_AUTHORITY = NONE
```

Workspace performs no scientific calculation and does not infer identity from
filenames, MIME labels, display labels, or array positions. Registered Adapter
to Runtime to persisted Artifact remains the scientific authority chain.

## 18. Compatibility

`/` remains PlannerWorkbench. AnalysisIntent 1.0, EligibilityResolution 1.0,
AnalysisPlan 0.1/0.2, PlanValidator, QueueWorkerRuntime, Registry/Adapters,
Job/ToolCall/Artifact, interpretation, Report/Recipe, historical APIs, and the
DeepSeek-only provider policy remain semantically unchanged. Workspace APIs are
additive and do not require existing clients to migrate.

## 19. Caps and Performance

Caps include 32 panels, 128 revisions, 16 secondary selections, 2,048-byte
selection URLs, 131,072-byte mutations, 524,288-byte snapshots, and JSON depth
14. Focused development evidence reports two project-list queries for both one
and five Workspaces, zero Artifact payload reads during projection, no bulk
backfill, full backend 208.26 s, frontend tests 60.71 s, and build 95.8 s.
These are development/service-backed acceptance measurements, not production
capacity claims.

## 20. Security

```text
NO_WORKSPACE_ARBITRARY_CODE_EXECUTION = PASS
NO_WORKSPACE_SHELL_OR_FILESYSTEM_AUTHORITY = PASS
NO_WORKSPACE_PROVIDER_AUTHORITY = PASS
NO_WORKSPACE_TOOLCALL_JOB_OR_ENQUEUE_AUTHORITY = PASS
NO_WORKSPACE_ARTIFACT_JAVASCRIPT = PASS
NO_WORKSPACE_ARTIFACT_HTML_EXECUTION = PASS
NO_WORKSPACE_EXTERNAL_ARTIFACT_URL_EXECUTION = PASS
NO_WORKSPACE_CROSS_PROJECT_SOURCE_ACCESS = PASS
NO_WORKSPACE_CROSS_JOB_ARTIFACT_INJECTION = PASS
NO_WORKSPACE_STALE_IDENTITY_REBINDING = PASS
NO_WORKSPACE_SECRET_OR_PRIVATE_PATH_DISCLOSURE = PASS
NO_RECOMMENDATION_TO_EXECUTION_AUTHORITY = PASS
NO_SECRET_PATTERN_HITS = PASS
REAL_LLM_CALLS = 0
```

HTML/script/Markdown, prototype keys, URL/path/module injection, foreign source,
stale hashes, malformed ETag, deep/oversized JSON, prompt injection, and
credential-shaped text are inert or typed rejection.

## 21. Service-Backed Evidence

Local Docker/services were unavailable: `LOCAL_SERVICE_BACKED=UNAVAILABLE`.
Corrected exact-SHA CI run `30705503707` used PostgreSQL 16, Redis 7, and MinIO
with the full migration chain, repositories, source records, API lifecycle,
scope and `ON DELETE RESTRICT` checks: `37 passed, 0 skipped, 0 failed, 0
errors`. Therefore `CI_SERVICE_BACKED=PASS` and `SERVICE_TESTS_SKIPPED=0`.

## 22. Browser Regression

Existing PlannerWorkbench and L4/L5 findings/evidence browser replays pass on
Chromium, Firefox, WebKit, and Chromium 390x844 mobile with no new console,
network, overflow, HTML/JS, or secret regressions.

```text
WORKSPACE_UI = NOT_IMPLEMENTED_BY_DESIGN
WORKSPACE_ROUTE_PAGE = DEFERRED_TO_PHASE_10M2
```

## 23. Acceptance IDs

```text
M1 expected = 8
implemented = 8
missing = 0
extra = 0
duplicate = 0
```

- M1-A01: Python/JSON Schema/TypeScript contracts and strict caps.
- M1-A02: in-memory/SQLite persistence, immutable refs, idempotency/revisions.
- M1-A03: 0007 upgrade/downgrade/re-upgrade.
- M1-A04: PostgreSQL Workspace/panel/revision zero-skip round trip.
- M1-A05: additive typed APIs, ETag, idempotency.
- M1-A06: scope, identity, deletion, and cap rejection.
- M1-A07: modern and explicit legacy read-only projection.
- M1-A08: no payload copy, disclosure, execution authority, or cross-project
  access.

## 24. Tests

- Focused M1: 26 passed; final migration/evidence subset: 4 passed.
- Full local backend: 1103 passed, 39 skipped, 63 warnings. Local service skips
  are not claimed as service PASS.
- Corrected CI Unit: 1104 passed, 1 skipped, 38 deselected, 63 warnings;
  Phase 10 backend closure 3 passed and L5 closure 99 passed.
- Frontend: 52 files, 333 tests; typecheck and production build PASS.
- Browser: L4/L5 Chromium, Firefox, WebKit, and mobile replay PASS.
- SQLite/PostgreSQL migration, evidence manifest, docs links, TASKS structure,
  secret scan, dependency/lock consistency, and service no-skipped gate PASS.
- `npm audit = UNAVAILABLE` because the configured mirror returned
  `404_NOT_IMPLEMENTED`; it is not reported clean.
- Known non-blocking warnings: existing pymatgen/spglib warnings and GitHub
  Actions Node 20 deprecation notices.

## 25. Production Behavior Changes

Added only ScientificWorkspace/Panel/Selection contracts, Workspace persistence
and repositories, explicit historical projection, additive Workspace APIs and
typed client, layout revisions, and optimistic concurrency.

```text
Planner behavior changes = NONE
AnalysisIntent behavior changes = NONE
Eligibility behavior changes = NONE
AnalysisPlan behavior changes = NONE
QueueWorkerRuntime behavior changes = NONE
Tool Registry behavior changes = NONE
Adapter behavior changes = NONE
Scientific calculation changes = NONE
Interpretation behavior changes = NONE
Real LLM calls = 0
Workspace UI changes = NONE
```

## 26. Files Changed

- Backend/API: Workspace contracts, repository models/implementations,
  projection service, router registration, strict request handling.
- Migration: Alembic env compatibility, SQLite-safe historical migration paths,
  and `0007_phase10m1_workspace_domain`.
- TypeScript: strict Workspace contracts and API client only.
- Tests/CI: contract, migration, persistence, projection/API, performance,
  service-backed, evidence, and existing browser-runner reliability.
- Evidence/docs/persistent/TASKS: Phase M1 records and deterministic manifest.

```text
dependencies = unchanged
lockfile = unchanged
```

## 27. Commit and CI History

- Failed implementation `d39687f7fe5ce39de0fe375a2b5d3068626b74f0`,
  run `30704917567`: Unit/Frontend passed; service was `36 passed, 0 skipped,
  1 failed`. Fixture passed a percent-encoded isolated-schema URL through
  ConfigParser interpolation before migration.
- Failed correction `7d0a16d1be7dadd3dffa17adc3d22f3e12a618f4`,
  run `30705191850`: Unit/Frontend passed; service was `36 passed, 0 skipped,
  1 failed`. Production Alembic `env.py` still passed percent-encoded
  `DATABASE_URL` through ConfigParser unescaped.
- Corrected implementation `27c5aa98138f882a750dc76a402ee2afe2151b72`,
  run `30705503707`: Unit, Frontend, and service-backed all success.
- Completion-record SHA/CI: this commit, pending exact-SHA CI.
- Queue-archive SHA/CI: not created before completion-record CI.

## 28. Explicit Non-Scope

Not implemented: M2 Workspace page/shell/navigation/panel UI; M3 selection
propagation/URL runtime; M4 Artifact Gallery/renderers/WebGL/trajectory/phonon/
volumetric Workspace integration; M5 Report/Recipe composition; M6 save/reload,
recovery, responsive/mobile Workspace UX; M7 final Workspace closure; Phase 10N
science; CrystalNN/VoronoiNN, experimental XRD, trajectory analytics,
Electronic Band/DOS; arbitrary code/shell/notebook/filesystem/external science
API; new LLM dependency or real DeepSeek call; autonomous replanning, generic
workflow, multi-job Workspace, RAG/memory/multi-agent, plugin marketplace, or
enterprise SaaS.

## 29. Phase 10M Readiness

```text
Phase 10M-1:
READY_WITH_EXPLICIT_LIMITS

Phase 10M-2:
REVIEWER_GATE
```

Phase 10M as a whole is not complete.

## 30. Queue State

```text
Phase 10M-1:
COMPLETE / AWAITING_VERIFIED_QUEUE_ARCHIVE

Phase 10M-2:
REVIEWER_GATE / AWAITING REVIEWER PROMPT

TASK_BLOCK_COUNT = 1
```

## 31. Automatic Phase 10M-2 Entry

```text
NO
PHASE_10M2_EXECUTABLE_TASK_CREATED = NO
```

## 32. Next Action

```text
Verify this completion-record exact-SHA CI, then archive only the completed
Phase 10M-1 task by a separate verified queue commit. Do not create, queue, or
execute Phase 10M-2.
```

## 33. Final Repository State

- Corrected implementation SHA: `27c5aa98138f882a750dc76a402ee2afe2151b72`.
- Implementation exact-SHA CI: `30705503707`, success.
- Completion-record SHA/CI: this commit / pending.
- Queue-archive SHA/CI: not created / pending.
- Expected current post-commit state: `HEAD == origin/master`, clean except for
  lifecycle commits in progress, migration head `0007`, task count 1.

# Phase 10M-2 Unified Scientific Workspace Shell Result

## 1. Conclusion

```text
PASS / COMPLETE / AWAITING_COMPLETION_RECORD_CI
```

The corrected implementation exact-SHA CI is complete. The task remains in
`TASKS.md` until this completion record and the separate queue archive each pass
their own exact-SHA CI.

## 2. Baseline and Entry Gate

- M1 implementation `27c5aa98138f882a750dc76a402ee2afe2151b72`, CI
  `30705503707`, success.
- M1 completion `7f6a3fa66236fdcdcaab5d12e515c201ab2a63bd`, CI
  `30706195493`, success.
- M1 archive `08f2133c6a02b64a199f40a0b17ccfa5d0e68cc7`, CI
  `30706443734`, success.
- Initial `HEAD == origin/master == 08f2133c...`, branch `master`, clean
  worktree, migration head `0007_phase10m1_workspace_domain`.
- M2 was admitted as the active task. A later reviewer/user-supplied M3 block
  is pending and was not entered during M2 implementation.

## 3. M0/M1 Decision Compliance

M-D001 through M-D025 remain unchanged. M2 consumes the one-Workspace-per-Job
M1 contracts, immutable source bindings, panel descriptors, layout revisions,
metadata APIs, explicit projection, ETag, and project scope. It adds no schema,
migration, repository, scientific authority, or hidden Workspace creation.

## 4. Workspace Route

Added `/workspaces/{workspaceId}` with Next loading/error boundaries and exact
metadata loading. `/` remains PlannerWorkbench. Unknown or inaccessible
Workspace IDs show typed errors; the route does not create a Workspace.

## 5. PlannerWorkbench Transition

PlannerWorkbench can explicitly project/open the current Job through the M1
idempotent POST and can list metadata-only project Workspace history. Exact
Workspace links are used; GET remains side-effect free.

## 6. Workspace Data Loading

The shell requests only `GET /workspaces/{workspaceId}` metadata. Abort signals
and request identities suppress stale responses. Initial load requests no
Artifact payload, object-store key, full array, provider data, or scientific
recalculation.

## 7. Workspace Header

The header shows exact Workspace title, projected state, source Job, revision,
panel count, and bounded provenance actions. Long identities wrap without
changing layout authority.

## 8. Desktop Information Architecture

Desktop uses the sealed global header, collapsible data/context rail, nine
navigation groups, one active panel, and overlay inspector. Panel descriptor
order is deterministic and does not imply scientific dependency.

## 9. Mobile Information Architecture

At 390x844 the shell presents one active panel, a context/navigation drawer,
and inspector bottom sheet. It does not shrink the desktop three-column layout.

## 10. Panel Switcher and Panel Shell

Exact visible panel IDs drive the switcher. Unknown IDs never select by label
or array position. One active panel is mounted; unsupported and failed panels
remain isolated typed surfaces.

## 11. Dataset/Context Drawer

The drawer exposes bounded source references and panel membership metadata. It
does not copy Artifact content or infer identity from filenames/MIME labels.

## 12. Inspector Shell

The inspector provides metadata, status, provenance links, and inert audit JSON
for the active panel.

```text
CANONICAL_SELECTION_PROPAGATION = NOT_IMPLEMENTED_BY_DESIGN
```

## 13. Active Panel URL State

The `panel` query stores one exact active panel ID. PushState/popstate,
back/forward, direct deep link, and refresh are deterministic. Unknown IDs show
a typed state and are not silently rebound.

## 14. Workspace Status UI

Complete, running, partial, failed, stale, legacy-read-only, missing-source,
and unsupported states are visibly distinct with semantic status text.

## 15. Partial Execution UI

Partial Workspace state and failed/blocked panel descriptors remain visible.
Successful independent panel metadata remains accessible; UI does not rewrite
Job, ToolCall, dependency, or execution outcomes.

## 16. Legacy / Stale / Missing UI

Legacy and stale Workspaces display read-only/source-integrity guidance.
Missing source and unsupported panels are not upgraded, rebound to latest, or
shown as successful scientific results.

## 17. Existing Surface Reuse

M2 reuses existing Workspace API/client contracts and established UI controls.
It does not introduce a second scientific mapper or the M4 renderer registry.

## 18. Findings / Evidence / Provenance

Existing interpretation, evidence, provenance, lineage, report, and recipe
panel descriptors are navigable metadata surfaces. M2 does not regenerate
findings or interpret raw Artifact content.

## 19. Report / Recipe Boundary

Report and Recipe remain references to existing authorities. No composition,
editing, publishing, or replay product behavior is added.

## 20. Scientific Integrity

```text
WORKSPACE_COPIED_ARTIFACT_PAYLOADS = 0
FRONTEND_DUPLICATE_SCIENTIFIC_AUTHORITY = NONE
```

No metrics, structures, trajectories, phonons, volumetric values, claims, or
units are computed in the shell.

## 21. LLM / DeepSeek Compliance

```text
NEW_LLM_CALL_SITES = 0
REAL_LLM_CALLS = 0
M2_CORE_REQUIRES_LLM = NO
DEEPSEEK_POLICY_REGRESSION = PASS
```

Persisted Job/Workspace state is consumed without a provider call. The existing
DeepSeek-only policy and `DEEPSEEK_KEY` boundary remain unchanged.

## 22. Accessibility

Semantic landmarks/headings, named controls, visible focus, keyboard-operated
drawers/sheets, focus restoration, status announcements, and non-color-only
state are covered. Touch targets are at least 44px in mobile evidence.

## 23. Responsive / Mobile

Desktop and 390x844 layouts have zero measured horizontal overflow. Long panel
and source identities wrap; drawers and sheets do not obscure active content.

## 24. Browser Matrix

Chromium, Firefox, WebKit, and Chromium 390x844 replay pass. Deep links,
back/forward, refresh, complete/running/partial/legacy/stale/unsupported states,
1/8/32 panels, and 20 repeated switches pass with zero console/page errors,
zero external requests, and zero Artifact payload requests.

## 25. Performance

Development evidence: 1/8/32-panel metadata payloads are 3,106/11,515/40,089
bytes; one active panel remains mounted after 20 switches; maximum observed
metadata concurrency is one; no listener growth was observed. These are bounded
development acceptance measurements, not production capacity claims.

## 26. Security

```text
NO_WORKSPACE_SHELL_ARBITRARY_CODE_EXECUTION = PASS
NO_WORKSPACE_SHELL_ARTIFACT_JAVASCRIPT = PASS
NO_WORKSPACE_SHELL_ARTIFACT_HTML_EXECUTION = PASS
NO_WORKSPACE_SHELL_IFRAME_EXECUTION = PASS
NO_WORKSPACE_SHELL_EXTERNAL_ARTIFACT_URL_EXECUTION = PASS
NO_WORKSPACE_SHELL_DYNAMIC_ARTIFACT_MODULE = PASS
NO_WORKSPACE_SHELL_CROSS_PROJECT_ACCESS = PASS
NO_WORKSPACE_SHELL_CROSS_JOB_ARTIFACT_INJECTION = PASS
NO_WORKSPACE_SHELL_STALE_IDENTITY_REBINDING = PASS
NO_WORKSPACE_SHELL_SECRET_DISCLOSURE = PASS
NO_WORKSPACE_SHELL_PRIVATE_PATH_DISCLOSURE = PASS
NO_WORKSPACE_SHELL_RECOMMENDATION_EXECUTION = PASS
NO_SECRET_PATTERN_HITS = PASS
```

HTML/script/Markdown, `javascript:`, SVG script, external URLs, prototype keys,
credential-shaped text, unknown panels, stale sources, and oversized query
inputs are inert or typed rejection.

## 27. Acceptance IDs

```text
M2_ACCEPTANCE_IDS_EXPECTED = 7
M2_ACCEPTANCE_IDS_IMPLEMENTED = 7
M2_ACCEPTANCE_IDS_MISSING = 0
M2_ACCEPTANCE_IDS_EXTRA = 0
M2_ACCEPTANCE_IDS_DUPLICATE = 0
```

- M2-A01 routing/root compatibility/direct source states: PASS.
- M2-A02 nine-group IA/one active panel/data rail/inspector: PASS.
- M2-A03 exact panel URL/back-forward/refresh: PASS.
- M2-A04 typed running/partial/failed/stale/legacy states: PASS.
- M2-A05 authorized project history/idempotent open: PASS.
- M2-A06 Chromium/Firefox/WebKit/390x844: PASS.
- M2-A07 landmarks/focus/status/no overflow: PASS.

## 28. Tests

- Focused Workspace frontend: 48 passed; Planner transition regression: 31
  passed; focused M1 backend: 24 passed.
- Local backend: 1107 passed, 1 skipped, 39 deselected, 63 warnings.
- Full frontend: 351 passed across 54 files; typecheck/build PASS.
- Corrected CI Unit: 1107 passed, 1 skipped, 39 deselected, 63 warnings.
- Corrected CI Frontend: Phase 10 closure, L4/L5/M2 browser replay, typecheck,
  and build PASS.
- Corrected CI service-backed: 38 passed, 0 skipped, 0 failed, 0 errors with
  PostgreSQL, Redis, MinIO, migration head 0007, API and idempotency checks.
- Evidence manifest, secret scan, docs/TASKS integrity, `uv lock --check`, and
  dependency listing PASS.
- Local service-backed: `UNAVAILABLE` because Docker CLI is absent.
- `npm audit = UNAVAILABLE`: configured mirror returned `404_NOT_IMPLEMENTED`;
  it is not reported clean.
- Non-blocking warnings: existing pymatgen/spglib warnings and GitHub Actions
  Node 20 deprecation notices.

## 29. Production Behavior Changes

Added only the Workspace route/shell, metadata loader, exact active-panel URL,
typed state UI, Planner transition/history, responsive shell, and inert
inspector. Planner, Intent, Eligibility, Plan, Runtime, Registry, Adapter,
scientific calculation, interpretation, Report/Recipe, and LLM behavior are
unchanged.

## 30. Files Changed

- Frontend: Workspace route, shell/model, Planner transition, scoped CSS.
- Tests/evidence: focused frontend, browser runner, service-backed API gate,
  evidence generator/checker and sanitized screenshots/manifest.
- CI: M2 browser replay and 38-test service no-skipped threshold.
- Docs/persistent/TASKS/results: M2 contracts, evidence and lifecycle records.

```text
migration = unchanged
dependencies = unchanged
lockfile = unchanged
```

## 31. Commit / CI History

- Failed implementation `8429a8da6c701dee33e6d3d71fa6c069bbd502ea`, run
  `30727814090`: Unit passed; Frontend found a 390px historical L5 overflow;
  service-backed Workspace API used the wrong schema and returned 500.
- Failed correction `42fa0db84b7315e9b5d97fc537795ae49e2b5404`, run
  `30728411811`: Unit/Frontend passed; service remained 37/38 because only the
  repository helper, not the Workspace service, was bound to the test bundle.
- Failed correction `f7d099c490379c10bfdd0efa0f3a8aac918c757a`, run
  `30728878630`: Unit/Frontend passed; service remained 37/38 because the
  isolated PostgreSQL search path could fall through to public migration state.
- Corrected implementation `d18097101cdf999b76be1f2da1cf4f3d67fb9c48`, run
  `30729180057`: Unit, Frontend, and service-backed all success.
- Completion-record SHA/CI: this commit / pending exact-SHA CI.
- Queue-archive SHA/CI: not created before completion-record CI.

## 32. Explicit Non-Scope

Not implemented: M3 canonical selection/propagation/URL selection runtime;
M4 typed Artifact Gallery and renderer integration; M5 Report/Recipe
composition; M6 save/reload/recovery product flow; M7 final Workspace closure;
Phase 10N science; new scientific algorithms; cross-Workspace/multi-Job state;
arbitrary code/shell/filesystem/notebook/external science API; RAG/memory/
multi-agent/plugin/enterprise systems; new dependency or LLM SDK.

## 33. Phase 10M Readiness

```text
Phase 10M-2:
READY_WITH_EXPLICIT_LIMITS

Phase 10M-3:
USER_SUPPLIED_TASK_PENDING_M2_ARCHIVE
```

Phase 10M as a whole is not complete.

## 34. Queue State

```text
Phase 10M-2:
COMPLETE / AWAITING_VERIFIED_QUEUE_ARCHIVE

Phase 10M-3:
USER_SUPPLIED / PENDING

TASK_BLOCK_COUNT = 2
```

## 35. Automatic M3 Entry

```text
NO
PHASE_10M3_EXECUTABLE_TASK_CREATED_BY_M2 = NO
```

The pending M3 block was supplied by the user and has not been executed.

## 36. Next Action

```text
Verify this completion-record exact-SHA CI, then archive only Phase 10M-2.
After the verified archive, follow the user-controlled TASKS queue.
```

## 37. Final Repository State

- Corrected implementation SHA: `d18097101cdf999b76be1f2da1cf4f3d67fb9c48`.
- Implementation exact-SHA CI: `30729180057`, success.
- Completion-record SHA/CI: this commit / pending.
- Queue-archive SHA/CI: not created / pending.
- Expected post-commit: `HEAD == origin/master`, clean, migration head 0007,
  M2 complete block retained and M3 pending.

# Phase 10M-3 Cross-Artifact Navigation + Canonical Selection Result

## 1. Conclusion

```text
PASS / COMPLETE / AWAITING_COMPLETION_RECORD_CI
```

## 2. Baseline and Entry Gate

- Phase 10M-2 implementation `d18097101cdf999b76be1f2da1cf4f3d67fb9c48`,
  exact-SHA CI `30729180057`, success.
- Phase 10M-2 completion `89da9c9bad07d906ab508d02cdeb26a212f24ac6`,
  exact-SHA CI `30729587141`, success.
- Phase 10M-2 archive `78bdec18b416a12f8878e602a552c27091f64c06`,
  exact-SHA CI `30729804091`, success.
- Initial `HEAD == origin/master == 78bdec18...`, branch `master`, clean
  worktree, migration head `0007_phase10m1_workspace_domain`, one active M3
  task, no M4 executable task: PASS.

## 3. M0-M2 Decision Compliance

M0-M2 Workspace identity, route, source authority, metadata-only shell,
one-active-panel UX, migration, API, and persistence decisions remain intact.
M3 adds no database table, API route, scientific authority, or contract version.

## 4. WorkspaceSelectionContext Runtime

The existing `WorkspaceSelectionContext 1.0` is activated with strict kind
fields, exact source hashes/versions, max 16 secondary identities, finite and
bounded JSON, prototype-key rejection, deterministic canonical serialization,
and semantic replay suppression.

## 5. URL Selection Codec

Canonical sorted JSON is encoded as base64url with a 2,048-byte token cap.
Recursive duplicate keys, noncanonical encodings, over-depth/over-size payloads,
foreign scope, stale versions, URLs, paths, and executable fields are rejected.

## 6. Selection Store

The store is scoped to one Workspace and exact Project/Job/dataset version,
supports at most 32 subscribers, records origin and transaction identity,
suppresses semantic duplicates, and releases subscribers on cleanup.

## 7. Panel Subscription Registry

Renderer-contract declarations determine accepted/emitted kinds. Current
overview/provenance consumers accept all 13 kinds; data, artifact, findings,
and evidence panels declare bounded subsets. Only
`workspace.artifact-metadata/1.0` is a production emitter in M3.

## 8. Compatibility Resolver

Outcomes are `EXACT`, `NOT_APPLICABLE`, `STALE`, and `UNSUPPORTED`. Exact
source references, Project/Job/dataset version, Artifact checksum/contract,
and panel declarations decide compatibility; registry/UI order does not.

## 9. Selection Propagation

Origin-aware delivery prevents echo loops and cross-Workspace leakage.
Independent subscribers receive only exact compatible references; stale or
unsupported panels receive typed diagnostics and no substitute selection.

## 10. Canonical Identity Support

- Dataset sample: `SUPPORTED` when exact object/sample identities exist.
- Material object: `SUPPORTED` by exact Profile object identity.
- Structure/site/atom: `SUPPORTED` by contract; missing formal IDs are
  `UNSUPPORTED_WITH_TYPED_REASON`.
- Trajectory frame/atom: `SUPPORTED` by contract; index-only records are
  `UNSUPPORTED_WITH_TYPED_REASON`.
- Phonon q-point/branch and reciprocal point: `SUPPORTED` by contract; formal
  IDs are mandatory and array positions are not authority.
- Volumetric field: `SUPPORTED` with exact field and Artifact checksum.
- Evidence item/claim: `SUPPORTED` by strict bundle/interpretation identity;
  production payload emitters remain `NOT_APPLICABLE` in M3.
- Artifact: `SUPPORTED`; whole Artifact metadata is the current production
  emission path.

## 11. Dataset / ML / Composition Linkage

Exact dataset sample/material object contexts are accepted by data, overview,
and provenance panels. No row-order, first-column, display-label, or unit guess
can create linkage.

## 12. Structure Linkage

Structure and periodic-site contexts require stable structure/site identities.
Current Artifacts without those IDs remain typed unavailable.

## 13. Trajectory Linkage

Trajectory frame/atom contexts require stable trajectory and frame/atom IDs.
Index-only trajectory payloads are not promoted to identity.

## 14. Phonon / Reciprocal Linkage

Q-point, branch, and reciprocal contexts require exact Artifact checksum and
formal point/segment IDs. Array order is explicitly rejected.

## 15. Volumetric Linkage

Volumetric contexts require exact field ID, Artifact ID, checksum, and scope;
no coordinate/label inference or frontend scientific calculation occurs.

## 16. Findings / Evidence / Artifact Linkage

Evidence/claim contracts are validated and consumable. Findings/evidence
emitters remain empty until an M4-reviewed formal payload mapper exists.
Whole Artifact selection is produced from metadata source references only.

## 17. Lineage Navigation

Inspector and compatible-panel navigation retain Artifact, ToolCall, Job,
contract/version, checksum, and source-scope identity without reading or
copying Artifact payloads.

## 18. Inspector

The Inspector displays exact kind, IDs, scope/hash/version, origin panel,
compatibility, consumer panels, Pin/Clear/Copy commands, and inert audit JSON.

## 19. Active Panel + Selection Navigation

Selection and active panel are independent canonical URL fields. Navigation
preserves valid selection, switches only to declared consumers, and rejects
unknown panels without fallback.

## 20. Refresh / Back / Forward

Chromium/Firefox/WebKit evidence restores canonical selection on refresh,
restores it with browser Back, and applies the pinned fallback after Forward
when the URL selection is absent. No implicit server write occurs.

## 21. Stale / Unsupported / Missing

Stale tokens are rejected without substitution. API Pin rejects stale scope as
`422 SELECTION_SCOPE_MISMATCH`. Missing formal identity is `UNSUPPORTED` or
`NOT_APPLICABLE`; it is never rebound to latest, nearest, first, or matching
display text.

## 22. Historical Compatibility

M1/M2 persisted panels with empty declarations remain readable. Known formal
renderer contracts receive deterministic read-time declarations without a
migration or hidden repository write. Historical Plan/Job/Artifact semantics
remain unchanged.

## 23. Scientific Integrity

```text
FRONTEND_DUPLICATE_SCIENTIFIC_AUTHORITY = NONE
SELECTION_ARRAY_INDEX_AUTHORITY = NONE
SELECTION_DISPLAY_LABEL_AUTHORITY = NONE
SELECTION_FUZZY_MATCHING = NONE
SELECTION_DATABASE_WRITES = 0
```

Selection maps exact identities only. It performs no metric, chemistry,
trajectory, phonon, reciprocal, volumetric, or interpretation calculation.

## 24. LLM / DeepSeek Compliance

```text
NEW_LLM_CALL_SITES = 0
M3_SELECTION_REQUIRES_LLM = NO
REAL_LLM_CALLS = 0
DEEPSEEK_POLICY_REGRESSION = PASS
```

No provider call is required by M3. The existing policy remains: future real
calls may use DeepSeek only, with the key sourced from `DEEPSEEK_KEY`.

## 25. Accessibility

Named controls, semantic status, visible focus, keyboard operation, focus
restoration, expandable Inspector content, non-color state, and at least 44px
mobile controls pass browser evidence.

## 26. Mobile

Chromium 390x844 uses stacked selection content and an Inspector bottom sheet.
Measured body/root horizontal overflow is zero.

## 27. Browser Matrix

Chromium, Firefox, WebKit, and Chromium 390x844 pass URL restore, Artifact
selection, Back/Forward, stale rejection, explicit Pin, Clear, focus, no
overflow, zero console/page errors, and zero external/Artifact-payload requests.

## 28. Performance

Development acceptance evidence, not a production capacity claim: the complete
runner took 53,731.246 ms; desktop selection cases took 5,033.677 ms Chromium,
4,626.120 ms Firefox, and 4,575.813 ms WebKit; mobile took 1,533.428 ms. The
bounded store passed 1/8/32 subscribers with cleanup and duplicate suppression.

## 29. Security

```text
NO_SELECTION_ARBITRARY_CODE_EXECUTION = PASS
NO_SELECTION_ARTIFACT_JAVASCRIPT = PASS
NO_SELECTION_ARTIFACT_HTML_EXECUTION = PASS
NO_SELECTION_IFRAME_EXECUTION = PASS
NO_SELECTION_EXTERNAL_URL_EXECUTION = PASS
NO_SELECTION_DYNAMIC_MODULE_EXECUTION = PASS
NO_SELECTION_CROSS_WORKSPACE_LEAK = PASS
NO_SELECTION_CROSS_PROJECT_ACCESS = PASS
NO_SELECTION_CROSS_JOB_ARTIFACT_INJECTION = PASS
NO_SELECTION_STALE_IDENTITY_REBINDING = PASS
NO_SELECTION_ARRAY_INDEX_AUTHORITY = PASS
NO_SELECTION_DISPLAY_LABEL_AUTHORITY = PASS
NO_SELECTION_FUZZY_MATCH = PASS
NO_SELECTION_SECRET_DISCLOSURE = PASS
NO_SELECTION_PRIVATE_PATH_DISCLOSURE = PASS
NO_RECOMMENDATION_EXECUTION = PASS
NO_SECRET_PATTERN_HITS = PASS
```

## 30. Acceptance IDs

```text
expected = 7
implemented = 7
missing = 0
extra = 0
duplicate = 0
```

M3-A01 strict identity contract, M3-A02 exact propagation, M3-A03 forbidden
mapping, M3-A04 canonical URL, M3-A05 explicit Pin, M3-A06 Inspector, and
M3-A07 browser/mobile all pass with evidence.

## 31. Tests

- Focused frontend: 38 passed; focused M1 projection: 7 passed; focused backend
  projection/evidence after CI fixes: 10 passed.
- Full backend local: 1111 passed, 41 integration-marked skipped, 63 warnings.
- Full frontend local: 376 passed across 56 files; typecheck/build PASS.
- Corrected implementation CI Unit, lock check, evidence/closure: success.
- Corrected implementation CI Frontend typecheck, L4/L5/M2/M3 browser replay,
  and production build: success.
- Corrected implementation CI PostgreSQL/Redis/MinIO: 39 passed, 0 skipped,
  0 failed, 0 errors; migration head 0007 and no-skipped gate PASS.
- Local service-backed: `UNAVAILABLE` because Docker CLI is absent.
- `npm audit = UNAVAILABLE`: configured mirror returned `404_NOT_IMPLEMENTED`;
  it is not reported clean.

## 32. Production Behavior Changes

Added the strict frontend selection codec/store, exact compatibility and panel
subscription registry, origin-aware propagation, Inspector/URL/history state,
whole Artifact selection, explicit Pin, and read-time declarations for formal
renderer contracts. Planner, execution, science, persistence, and provider
behavior are unchanged.

## 33. Files Changed

- Frontend: selection contract/runtime/tests, Workspace shell/tests, fixture,
  responsive styles, browser/evidence generators.
- Backend/tests: deterministic panel declaration projection, historical
  compatibility, PostgreSQL/Redis/MinIO M3 service gate.
- CI/evidence/docs/persistent/TASKS/results: browser replay, zero-skip gate,
  sanitized manifest, architecture/compatibility/completion records.

```text
migration = unchanged
database schema = unchanged
dependencies = unchanged
lockfile = unchanged
Workspace contracts = unchanged
```

## 34. Commit / CI History

- Failed `41c2d23ca5f1f29fccce07d06f7aceb676a26ae5`, run `30733804796`:
  M2 browser semantic comparison included nonsemantic DOM count; M3 service
  fixture referenced a missing ToolCall.
- Failed `c3c029effdd2f77ce5aac1b60041c582bc477e54`, run `30734288153`:
  ToolCall FK fixed; source Job lacked complete 0.2 identities and correctly
  projected read-only.
- Failed `9cb8fbc76d7d4808fd764196b9b4e5af0247fb54`, run `30734708819`:
  integration reached a stale negative assertion whose expected HTTP/code pair
  did not match the production contract.
- Corrected implementation `fe5353f25e45eb10d3a78fa148727071e84d89e2`,
  run `30734974889`: Unit, Frontend, Browser, Build, Service-backed/no-skipped,
  evidence and security gates all success.
- Completion-record SHA/CI: this commit / pending exact-SHA CI.
- Queue-archive SHA/CI: not created before completion-record CI.

## 35. Explicit Non-Scope

Not implemented: M4 typed Artifact Gallery/scientific renderer integration;
M5 Report/Recipe composition; M6 full save/recovery; M7 Workspace closure;
Phase 10N science; new scientific renderer/calculation; cross-Workspace or
multi-Job selection; selection persistence beyond explicit existing Pin;
database/migration/API redesign; arbitrary code/shell/filesystem/notebook;
external scientific API; recommendation execution; new LLM SDK/dependency.

## 36. Phase 10M Readiness

```text
Phase 10M-3:
READY_WITH_EXPLICIT_LIMITS

Phase 10M-4:
REVIEWER_GATE
```

## 37. Queue State

```text
Phase 10M-3:
COMPLETE / AWAITING_VERIFIED_QUEUE_ARCHIVE

Phase 10M-4:
REVIEWER_GATE / AWAITING REVIEWER PROMPT

TASK_BLOCK_COUNT = 1
```

## 38. Automatic M4 Entry

```text
NO
PHASE_10M4_EXECUTABLE_TASK_CREATED = NO
```

## 39. Next Action

```text
Verify this completion-record exact-SHA CI, then archive only Phase 10M-3.
Do not create, queue, or execute Phase 10M-4.
```

## 40. Final Repository State

- Corrected implementation SHA: `fe5353f25e45eb10d3a78fa148727071e84d89e2`.
- Implementation exact-SHA CI: `30734974889`, success.
- Completion-record SHA/CI: this commit / pending.
- Queue-archive SHA/CI: not created / pending.
- Expected post-commit: `HEAD == origin/master`, clean, migration head 0007,
  M3 completed block retained, task count 1, no M4 executable task.

# Phase 10M-4 Typed Artifact Gallery + Scientific Viewer Integration Result

## 1. Conclusion

```text
PASS / COMPLETE / AWAITING_COMPLETION_RECORD_CI
```

## 2. Baseline and Entry Gate

- M3 implementation `fe5353f25e45eb10d3a78fa148727071e84d89e2`, CI
  `30734974889` success.
- M3 completion `7ec413f226c82e6c9a5c6ff04336a675fb8897a3`, CI
  `30735401732` success.
- M3 archive `86fb69238f1c69e172ad1010cd70ff2c486f2a1c`, CI
  `30735666842` success.
- Initial HEAD/origin were the M3 archive SHA on `master`; worktree was clean,
  migration head was `0007_phase10m1_workspace_domain`, task count was zero.
- M4 was admitted as the sole executable task; M5 remained reviewer-gated.

## 3. M0-M3 Decision Compliance

ScientificWorkspace 1.0, WorkspacePanel 1.0, WorkspaceSelectionContext 1.0,
M1 persistence/API, M2 shell, and M3 selection authority are unchanged. M4 is
an additive read/render integration layer only.

## 4. Artifact Contract Inventory

All 42 shared Artifact types have an exact disposition in the checked-in
registry and evidence inventory. Keys are Artifact type/version plus renderer
contract/version; filenames, titles, MIME alone, URLs, and component names are
not authority.

## 5. Renderer Classification

- `PRODUCTION_NATIVE_RENDERER`: existing Structure, Trajectory, Phonon,
  Brillouin-zone, and Volumetric application-owned viewers.
- `PRODUCTION_ADAPTED_RENDERER`: exact embedded Dataset, ML, and Composition
  product contracts plus bounded generic numeric plot/table paths.
- `CONSUMER_ONLY`: viewers without a formally stable emitted object identity.
- `METADATA_ONLY`: static/binary formats that are listed but not rendered.
- `INERT_FALLBACK`: bounded JSON/text and legacy/unsupported records.
- `UNSUPPORTED`: unknown types and version mismatches, with no guessed renderer.

## 6. Typed Renderer Registry

The finite 42-entry registry declares payload mode, heavy/WebGL ownership,
selection input/output, accessibility fallback, caps, lazy policy, bundle
members, stale/legacy behavior, and inert security classification. Duplicate
or malformed declarations fail tests.

## 7. Artifact Gallery

The Results panel now exposes a semantic metadata Gallery with contract,
version, renderer, ToolCall/step, checksum, size, status, lineage, selection,
safe open/download, partial/stale/legacy indicators, and exact provenance.
The browser sidecar covers 20 mixed typed Artifacts without truncation.

## 8. Artifact Metadata and Payload Loading

Initial Workspace loading makes zero Artifact payload requests. Payloads load
only for the active Artifact. The loader validates Workspace revision,
Project/Job/Artifact scope, type/version, size, content type, exact SHA-256,
JSON depth/finite/prototype constraints, cancellation, stale request identity,
and a cache key containing all semantic renderer inputs.

## 9. Generic Table / Plot / Text / JSON Fallbacks

Tables and plots consume backend-produced values only and retain semantic
table/text alternatives. Histogram bins, metrics, PCA, clustering, and other
science are not recomputed. Text/JSON are bounded inert text; HTML, script,
iframe, module, active SVG, and external assets never execute.

## 10. Dataset Materials Explorer

The existing Dataset Materials Explorer is integrated through exact K2
contract validation. Overview, composition, structures, properties, quality,
comparison, and sample surfaces retain Profile authority and stable
`objectId + sampleRef` identity.

## 11. Materials ML Viewers

Existing regression, uncertainty, and classification products are adapted
only for their exact formal schemas. Metrics, bins, target/model/unit identity,
high-error/high-uncertainty samples, class metrics, and conditional curves are
backend authority; the frontend does not recalculate or substitute metrics.

## 12. Composition Space Viewer

The existing Composition Space component consumes persisted coordinates,
clusters, coloring, and sample identities. It emits exact Dataset sample
selection and does not recompute PCA/KMeans or use point order as identity.

## 13. Structure Viewer

Existing canonical structure scene rendering is lazy-loaded with exact scene
identity, lattice/species/site facts, accessibility summary, context-loss
fallback/retry, and explicit Three.js disposal. No bond/coordination/validity
science was added.

## 14. Trajectory Viewer

Existing bounded trajectory frames, navigation, playback, cell/species and
numeric summaries are integrated. Panel close cancels work and stops playback;
no RDF/MSD/diffusion/unwrapping/smoothing/event analysis was added.

## 15. Phonon Viewer

Existing band, DOS, combined band-DOS, and animation contracts retain exact
q-point/branch/unit/path/imaginary-frequency semantics and dependency lineage.
No interpolation, mode inference, or calculation was added.

## 16. Brillouin Zone Viewer

Existing reciprocal lattice, Brillouin-zone, persisted labels/path, and
manifest artifacts load as one exact bundle. No cell/path regeneration,
nearest-coordinate match, or label-only identity is introduced.

## 17. Volumetric Viewer

Existing grid/field/payload/manifest/binary contracts render active-only with
exact checksum and source identity. The reproducible browser fixture derives
its exact values from checked-in canonical Phase 10J contracts. No Bader,
feature extraction, topology, or external texture/volume loading was added.

## 18. Canonical Selection Integration

- Artifact Gallery: `PRODUCTION_NATIVE_EMITTER` for exact `ARTIFACT` metadata.
- Dataset and Composition: `PRODUCTION_ADAPTED_EMITTER` for exact
  `DATASET_SAMPLE` identity.
- ML, Structure, Trajectory, Phonon, BZ, Volumetric: `CONSUMER_ONLY` or
  `NO_SELECTION_SUPPORT` where a stable emitted identity is absent.
- All delivery reuses the M3 store, URL codec, declarations, resolver, and
  Inspector. There is no second selection authority or fuzzy mapping.

## 19. Inspector / Findings / Evidence / Provenance

Gallery Evidence and Lineage actions navigate exact Artifact selection into
existing persisted interpretation/evidence/provenance reads. Browser replay
verifies Artifact -> Evidence item -> canonical selection and Artifact ->
Provenance identity without copying payloads.

## 20. Partial / Failure Isolation

Successful Artifacts remain usable when sibling steps fail or are dependency
blocked. Partial coverage and producer state remain visible. A Viewer failure
does not blank the Workspace or mutate Job/ToolCall/Artifact state.

## 21. Legacy / Unsupported Contracts

Unknown contracts, old versions, missing payloads, stale/deleted sources,
integrity mismatches, caps, and unsupported Profiles produce typed inert
states. There is no latest rebinding, filename guess, or same-name replacement.

## 22. WebGL Lifecycle

```text
MAX_ACTIVE_HEAVY_VIEWERS = 1
WEBGL_CONTEXT_GROWTH = 0
LISTENER_GROWTH = 0
OBSERVER_GROWTH = 0
DUPLICATE_CANVAS = 0
```

Chromium executes 50 heavy mount/unmount cycles plus context loss/recovery;
Firefox/WebKit execute cross-engine cycles. Peak active contexts are one and
final active contexts are zero. CI uses Xvfb for Firefox/WebKit and explicit
SwiftShader WebGL for Chromium; all three report WebGL2 preflight.

## 23. Scientific Integrity

```text
FRONTEND_DUPLICATE_SCIENTIFIC_AUTHORITY = NONE
FRONTEND_SCIENTIFIC_RECOMPUTATION = NONE
WORKSPACE_COPIED_ARTIFACT_PAYLOADS = 0
ARTIFACT_FILENAME_RENDERER_AUTHORITY = NONE
ARTIFACT_EXTERNAL_EXECUTION_AUTHORITY = NONE
```

## 24. LLM / DeepSeek Compliance

```text
NEW_LLM_CALL_SITES = 0
M4_VIEWERS_REQUIRE_LLM = NO
REAL_LLM_CALLS = 0
DEEPSEEK_POLICY_REGRESSION = PASS
```

M4 renders persisted Artifacts. Existing policy remains DeepSeek-only for any
future real call with `DEEPSEEK_KEY` as the sole key source.

## 25. Accessibility

Gallery and Viewer surfaces expose semantic headings/lists/tables/status,
numeric/text alternatives, keyboard and focus-visible controls, non-color
state, context-lost text, reduced-motion behavior, and named controls.

## 26. Mobile / Responsive

Chromium 390x844 passes one-active-viewer, 44px minimum targets, Inspector
focus/return focus, stacked Gallery layout, and zero body/root overflow.

## 27. Browser Matrix

Chromium, Firefox, WebKit, and Chromium 390x844 pass. Console errors, page
errors, failed responses, and unapproved external requests are zero. Legacy
and HTML payloads remain inert.

## 28. Performance

Development/browser acceptance evidence, not a production capacity claim:
20 metadata Artifacts, zero initial payload requests, zero inactive-heavy
requests, 22/20/22 desktop content requests, one mobile request, one peak
heavy context, zero retained canvas, zero resource growth, and Chromium traced
heap delta zero. Registry/loader caps bound metadata, bundles, depth, bytes,
rows, columns, traces, and points.

## 29. Security

```text
NO_ARTIFACT_GALLERY_ARBITRARY_CODE_EXECUTION = PASS
NO_ARTIFACT_HTML_EXECUTION = PASS
NO_ARTIFACT_JAVASCRIPT_EXECUTION = PASS
NO_ARTIFACT_IFRAME_EXECUTION = PASS
NO_ARTIFACT_DYNAMIC_MODULE_EXECUTION = PASS
NO_ARTIFACT_EXTERNAL_URL_EXECUTION = PASS
NO_ARTIFACT_COMPONENT_NAME_AUTHORITY = PASS
NO_ARTIFACT_FILENAME_RENDERER_AUTHORITY = PASS
NO_CROSS_PROJECT_ARTIFACT_ACCESS = PASS
NO_CROSS_JOB_ARTIFACT_INJECTION = PASS
NO_STALE_ARTIFACT_REBINDING = PASS
NO_ARTIFACT_CHECKSUM_BYPASS = PASS
NO_FRONTEND_SCIENTIFIC_RECOMPUTATION = PASS
NO_SELECTION_ARRAY_INDEX_AUTHORITY = PASS
NO_SELECTION_DISPLAY_LABEL_AUTHORITY = PASS
NO_SELECTION_FUZZY_MATCH = PASS
NO_RECOMMENDATION_EXECUTION = PASS
NO_SECRET_PATTERN_HITS = PASS
```

## 30. Acceptance IDs

```text
expected = 8
implemented = 8
missing = 0
extra = 0
duplicate = 0
```

M4-A01 through M4-A08 pass local, browser, service-backed, and corrected
implementation exact-SHA CI evidence.

## 31. Tests

- Focused M4 frontend: 40 passed; M4 evidence: 3 passed.
- Full backend local: 1115 passed, 41 explicitly gated skips, 63 warnings.
- Full frontend local: 396 passed across 62 files; typecheck/build PASS.
- Browser: Chromium/Firefox/WebKit/mobile PASS; 50-cycle/context-loss PASS.
- Corrected exact-SHA CI `30751689618`: Unit SUCCESS, Frontend/browser/build
  SUCCESS, PostgreSQL/Redis/MinIO 39 passed and 0 skipped.
- `uv lock --check` and dependency tree PASS; no lock/dependency change.
- `npm audit = UNAVAILABLE`: configured mirror returned
  `404_NOT_IMPLEMENTED`; it is not reported clean.

## 32. Production Behavior Changes

Added the typed Gallery, exact renderer registry, metadata/payload loader,
existing scientific Viewer dispatch, exact M3 selection integration, and
heavy/WebGL lifecycle control. Workspace, Planner, Runtime, Registry execution,
Adapters, scientific values, and interpretation behavior are unchanged.

## 33. Files Changed

- Backend/API: exact Artifact content read and interpretation source refs.
- Frontend: registry, loader, Gallery, generic plot, scientific Viewer adapters,
  selection integration, heavy/WebGL lifecycle and responsive styling.
- Tests/CI: focused tests, service-backed content route, historical fixture
  compatibility, three-browser/mobile runner and Xvfb replay.
- Evidence/docs/persistent/TASKS/results: sanitized manifests and lifecycle.

```text
migration = unchanged
database schema = unchanged
dependencies = unchanged
lockfile = unchanged
Workspace contracts = unchanged
Selection contract = unchanged
```

## 34. Commit / CI History

- `197727e`, run `30748799607`: failed M2 fixture metadata route.
- `edd5d58`, run `30749134462`: failed M3 metadata-GET authority assertion.
- `75038ac`, run `30749507123`: failed gitignored volumetric fixture.
- `f370795`, run `30750190137`: failed Linux Chromium software WebGL.
- `61d20a9`, run `30750682966`: incomplete SwiftShader flag set.
- `28625a2`, run `30751255622`: Linux Firefox headless WebGL unavailable.
- Corrected implementation `6287785c26e7bfdb91664fb10e78aa3de87161f7`,
  run `30751689618`: all required jobs success.
- Completion-record SHA/CI: this commit / pending exact-SHA CI.
- Queue-archive SHA/CI: not created before completion-record CI.

## 35. Explicit Non-Scope

Not implemented: new scientific Adapter/algorithm; CrystalNN/VoronoiNN;
experimental XRD; RDF/MSD/diffusion; electronic Band/DOS/Fermi surface; Bader
or new volumetric extraction; new phonon/structure calculation; frontend
scientific recomputation; migration/database change; selection persistence;
cross-Workspace or multi-Job Workspace; M5 Report/Recipe composition;
panel-to-report selection; M6 recovery/offline/collaboration; plan/DAG editor;
recommendation execution; new LLM/provider/SDK; arbitrary Python/shell/
filesystem/notebook; external science API; RAG/memory/multi-agent/plugins/
enterprise SaaS.

## 36. Phase 10M Readiness

```text
Phase 10M-4:
READY_WITH_EXPLICIT_LIMITS

Phase 10M-5:
REVIEWER_GATE
```

## 37. Queue State

```text
Phase 10M-4:
COMPLETE / AWAITING_VERIFIED_QUEUE_ARCHIVE

Phase 10M-5:
REVIEWER_GATE / AWAITING REVIEWER PROMPT

TASK_BLOCK_COUNT = 1
```

## 38. Automatic M5 Entry

```text
NO
PHASE_10M5_EXECUTABLE_TASK_CREATED = NO
```

## 39. Next Action

```text
Verify this completion-record exact-SHA CI, then archive only Phase 10M-4.
Do not create, queue, or execute Phase 10M-5.
```

## 40. Final Repository State

- Corrected implementation SHA: `6287785c26e7bfdb91664fb10e78aa3de87161f7`.
- Implementation exact-SHA CI: `30751689618`, success.
- Completion-record SHA/CI: this commit / pending.
- Queue-archive SHA/CI: not created / pending.
- Expected post-commit: `HEAD == origin/master`, clean, migration head 0007,
  M4 completed block retained, task count 1, no M5 executable task.

# Phase 10M-5 Scientific Report + Recipe Composition Result

## 1. Conclusion

```text
PASS / COMPLETE / AWAITING_COMPLETION_RECORD_CI
```

## 2. Baseline and Entry Gate

- M4 implementation: `6287785c26e7bfdb91664fb10e78aa3de87161f7`, CI `30751689618` success.
- M4 completion: `ee0e913625b627e891e1627f204ebf8e14cfb7c9`, CI `30752527117` success.
- M4 archive: `7f84472d3cd0ca1e8a90eb56a69987bf4c2dadd7`, CI `30752905104` success.
- Initial HEAD/origin: M4 archive SHA; branch `master`; clean worktree; migration head 0007; task count zero before admission.

## 3. M0-M4 Decision Compliance

Workspace identity/persistence, shell, canonical selection, renderer registry,
Gallery, viewers, WebGL lifecycle, Artifact authority, and historical API
semantics remain unchanged. M5 is additive composition only.

## 4. Report / Recipe Authority Audit

Existing `reports.report_json` and `visualization_recipes.recipe_json` remain
the sole persistence authorities. Reports are selected delivery snapshots;
Recipes are exact declarative, non-executable replay manifests.

## 5. Existing Persistence Reuse

```text
new report tables = 0
new recipe tables = 0
migration = unchanged
migration head = 0007_phase10m1_workspace_domain
```

The existing UnitOfWork transaction atomically creates the exact pair.

## 6. Composition Contracts

Implemented strict `ReportCompositionRequest 1.0`,
`ReportCompositionSnapshot 1.0`, `RecipeReplayManifest 1.0`, and
`ReportExportManifest 1.0` in Python, checked JSON Schema, and TypeScript.
Unknown/duplicate fields, non-finite values, invalid IDs/enums, excessive
depth/bytes/counts, and executable text are rejected.

## 7. Canonical Identity and Hashing

Canonical semantic hashes include exact Workspace revision, Project/Dataset/
Job/Plan, ordered selected Panels/Artifacts/Claims/Evidence, checksums,
captions, disclosures, and Recipe bindings. Runtime IDs, timestamps, browser
state, temporary URLs, and secrets are excluded.

## 8. Source Eligibility Classification

The deterministic projector emits `REPORT_FIGURE_SOURCE`,
`REPORT_TABLE_SOURCE`, `REPORT_FINDING_SOURCE`, `REPORT_EVIDENCE_SOURCE`,
`REPORT_PROVENANCE_SOURCE`, `REPORT_DISCLOSURE_ONLY`,
`REPORT_METADATA_ONLY`, or `REPORT_UNSUPPORTED` from exact contract/version,
scope, checksum, lineage, and validated interpretation membership. Filename,
title, MIME-only, array-position, fuzzy, and latest-version inference are absent.

## 9. Scientific Report Composition

Every Report deterministically renders all twelve mandatory sections: title,
goal, scope, methods/plan, execution, results, findings, warnings/limitations,
failed/blocked/missing scope, evidence/provenance, environment/references, and
exact Recipe reference. Empty sections retain typed unavailable state.

## 10. Exact Recipe Replay Manifest

Recipes preserve exact Project/Dataset/Profile/Intent/Eligibility/Decision/
Plan, tools, versions, params, bindings, expected outputs, original Artifact
IDs/checksums, outcome, provenance, warnings, and semantic hash. All execution,
Plan, Job, queue, and automatic replay flags are false.

## 11. AnalysisPlan 0.1 Support

Plan 0.1 remains `planSchemaVersion = 0.1` with no invented dependency graph
or Artifact binding. Exact ordered independent/sequential steps and params are retained.

## 12. AnalysisPlan 0.2 / Dependency Support

Plan 0.2 preserves graph hash, dependency edges, ports, producer/consumer
bindings, contract/version/checksum lineage, independent branches, and
failed/blocked descendants.

## 13. M3 Selection and M4 Gallery Integration

Gallery and eligible Panels add exact source refs to a session draft. The M3
selection authority is not replaced or persisted; unsupported Viewer
sub-selection falls back to whole Artifact, Panel, metadata, or approved numeric/text representation.

## 14. Figures / Tables / Viewer Fallbacks

Formal static/numeric/table projections are eligible. WebGL-only Structure,
Trajectory, BZ, and Volumetric states use exact metadata and approved fallback.

```text
WEBGL_CANVAS_REPORT_AUTHORITY = NONE
BROWSER_SCREENSHOT_SCIENTIFIC_AUTHORITY = NONE
```

## 15. Findings / Evidence / Interpretation

Only persisted grounded ScientificClaims and exact Evidence membership may be
selected. Numeric values, units, subjects, confidence, supporting/limiting
Evidence, and provider/deterministic provenance are unchanged.

## 16. Mandatory Warnings / Limitations / Failures

Source warnings, interpretation limitations, partial coverage, failed steps,
blocked dependencies, missing desired outputs, stale/unsupported sources, and
validation/provider failures are mandatory and cannot be removed.

## 17. Partial / All-Failed / No-Interpretation States

Partial execution produces `REPORT_READY_WITH_LIMITS`; all-failed produces
`REPORT_NO_SCIENTIFIC_RESULTS`; no-interpretation retains methods/Artifacts/
provenance with grounded findings typed unavailable. No positive claim is invented.

## 18. Stale / Missing / Legacy States

Stale identity never rebinds to latest. Missing selected results fail or must
be removed while their disclosure remains. Legacy Report/Recipe records remain
read-only with unchanged hashes and typed unavailable fields.

## 19. Preview

```text
PREVIEW_REPORT_WRITES = 0
PREVIEW_RECIPE_WRITES = 0
PREVIEW_JOB_CREATION = 0
```

Preview revalidates exact sources and deterministically returns Report, Recipe
summary, outcome, caps, and errors without persistence or execution authority.

## 20. Persistence / Atomicity / Idempotency

Finalize revalidates Workspace revision and all exact sources, then creates
the linked Report/Recipe pair in one transaction. Same idempotency key and
semantic request returns the same pair; semantic conflict is typed and creates
no row. Rollback leaves both counts unchanged.

## 21. History

History lists every immutable snapshot by exact IDs, versions, semantic hashes,
source Job, Workspace revision, outcome, limitations, exports, and legacy state.

## 22. Export

Canonical JSON and UTF-8 LF-normalized Markdown are deterministically rendered
from the persisted snapshot, with exact refs, warnings, limitations, no-execution
flags, safe server filenames, authorization, byte caps, and content hashes.

## 23. API

- `GET /workspaces/{workspaceId}/report-composition/sources`
- `POST /workspaces/{workspaceId}/report-compositions/preview`
- `POST /workspaces/{workspaceId}/report-compositions`
- `GET /workspaces/{workspaceId}/report-compositions`
- `GET /workspaces/{workspaceId}/report-compositions/{reportId}`
- `GET /workspaces/{workspaceId}/report-compositions/{reportId}/recipe`
- `GET /workspaces/{workspaceId}/report-compositions/{reportId}/exports/{format}`

All routes are additive, metadata-first, scope checked, and return typed errors.

## 24. Workspace Frontend

The existing Report Panel now provides source inventory, session draft,
bounded captions/order controls, mandatory disclosures, preview, explicit
finalize, immutable history/detail, Recipe inspection, and JSON/Markdown export.

## 25. Authorization

Every read/write validates Project -> Workspace -> Job -> Panel/Artifact/
Claim/Evidence -> Report/Recipe pair. Corrected service-backed evidence uses a
real foreign Project/Job/Artifact and receives typed rejection.

## 26. Scientific Integrity

```text
REPORT_GENERATED_SCIENTIFIC_VALUES = 0
REPORT_GENERATED_SCIENTIFIC_CLAIMS = 0
REPORT_SCIENTIFIC_RECOMPUTATION = 0
WORKSPACE_COPIED_ARTIFACT_PAYLOADS = 0
RECIPE_EXECUTION_AUTHORITY = NONE
RECIPE_PLAN_CREATION_AUTHORITY = NONE
RECIPE_JOB_CREATION_AUTHORITY = NONE
RECIPE_QUEUE_AUTHORITY = NONE
```

## 27. LLM / DeepSeek Compliance

```text
NEW_LLM_CALL_SITES = 0
M5_REPORT_COMPOSITION_REQUIRES_LLM = NO
M5_RECIPE_COMPOSITION_REQUIRES_LLM = NO
REAL_LLM_CALLS = 0
DEEPSEEK_POLICY_REGRESSION = PASS
```

Existing persisted provider-produced interpretation is read-only evidence;
Report and Recipe composition providers are `NONE`.

## 28. Accessibility

Semantic headings, labels, status/warning announcements, keyboard selection
and reorder controls, focus-visible behavior, tables, figure alternatives,
reduced motion, reflow, and named export controls pass automated evidence.

## 29. Mobile / Responsive

Chromium 390x844 passes single-surface source/draft/preview/history navigation,
44px targets, focus return, warning announcements, and zero horizontal overflow.

## 30. Browser Matrix

Chromium, Firefox, WebKit, and Chromium 390x844 pass complete/partial/no-
interpretation/stale/legacy/injection/idempotency/export cases. Console errors,
page errors, failed responses, and unapproved external requests are zero.

## 31. Performance

Development acceptance evidence, not a production capacity claim: source
inventory 12.235 ms, preview 16.489 ms, finalize 22.074 ms; request 335 bytes,
JSON export 11,025 bytes, Markdown 2,097 bytes.

```text
INITIAL_HEAVY_ARTIFACT_PAYLOAD_REQUESTS = 0
REPORT_PREVIEW_WEBGL_CONTEXTS = 0
DUPLICATE_RECORD_GROWTH_ON_IDEMPOTENT_SUBMIT = 0
```

## 32. Security

```text
ARTIFACT_CONTENT_IS_INERT_DATA = PASS
NO_REPORT_ARBITRARY_CODE_EXECUTION = PASS
NO_REPORT_SHELL_OR_FILESYSTEM_AUTHORITY = PASS
NO_REPORT_PROVIDER_AUTHORITY = PASS
NO_RECIPE_EXECUTION_AUTHORITY = PASS
NO_RECIPE_PLAN_CREATION_AUTHORITY = PASS
NO_RECIPE_JOB_CREATION_AUTHORITY = PASS
NO_RECIPE_QUEUE_AUTHORITY = PASS
NO_REPORT_ARTIFACT_JAVASCRIPT = PASS
NO_REPORT_ARTIFACT_HTML_EXECUTION = PASS
NO_REPORT_EXTERNAL_ARTIFACT_URL_EXECUTION = PASS
NO_CROSS_PROJECT_REPORT_SOURCE = PASS
NO_STALE_REPORT_SOURCE_REBINDING = PASS
NO_REPORT_SCIENTIFIC_RECOMPUTATION = PASS
NO_REPORT_GENERATED_SCIENTIFIC_CLAIMS = PASS
NO_SECRET_PATTERN_HITS = PASS
```

## 33. Acceptance IDs

```text
expected = 7
implemented = 7
missing = 0
extra = 0
duplicate = 0
```

- M5-A01: contracts/authority, contract and evidence tests.
- M5-A02: deterministic Report composer, complete/partial/no-result tests.
- M5-A03: exact Plan 0.1/0.2 Recipe, determinism tests.
- M5-A04: Workspace composition/history UI and browser evidence.
- M5-A05: no-write preview and canonical safe exports.
- M5-A06: failure/compatibility/accessibility/performance/security matrix.
- M5-A07: service-backed/browser/evidence and three-commit lifecycle.

## 34. Tests

- Focused M5 backend/evidence: 29 passed.
- Full backend local: 1144 passed, 42 service-gated skips, 63 warnings.
- Full frontend local: 402 passed across 63 files; typecheck/build passed.
- Chromium/Firefox/WebKit/mobile browser evidence passed.
- Corrected CI `30990265619`: Unit, frontend/typecheck/build/browser, service-backed, no-skipped, closure/evidence success.
- Service-backed: 40 passed, 0 skipped, 0 failed, 0 errors.
- `uv lock --check`, dependency tree, docs links, TASKS/acceptance/evidence integrity, and secret scan passed.
- `npm audit = UNAVAILABLE`: configured mirror returned `404_NOT_IMPLEMENTED`; not reported clean.

## 35. Service-Backed Evidence

PostgreSQL migration head 0007, Redis, MinIO payload/checksum, persisted
Workspace/Job/Plan/Artifact/Evidence/Interpretation, metadata inventory,
no-write preview, atomic pair, idempotency, rollback, history/export,
cross-project rejection, and zero execution-object growth passed in CI.
`LOCAL_SERVICE_BACKED = UNAVAILABLE`; CI is the zero-skipped authority.

## 36. Production Behavior Changes

Workspace Report Panel can inventory eligible sources, compose and preview a
deterministic draft, explicitly finalize an immutable Report/Recipe pair,
inspect history and exact Recipe bindings, and export canonical JSON/Markdown.
Mandatory disclosures remain; no Plan/Job/ToolCall/queue is created.

## 37. Files Changed

Backend contracts/services/repositories/API, checked schemas, TypeScript/API
client, Workspace Report UI/styles, focused/service/browser tests, CI gate,
evidence, docs, persistent status, TASKS, and this result.

```text
database schema = unchanged
migration = unchanged
dependencies = unchanged
lockfile = unchanged
Workspace contracts = unchanged
Selection contract = unchanged
renderer registry authority = unchanged
scientific Adapter authority = unchanged
```

## 38. Commit / CI History

- Initial implementation `084ebd29a462ee7232a335d728ef67d4f27b7395`, run `30989213715`: Unit and Frontend succeeded; service-backed failed because the negative fixture's stale caption caused DTO 422 before scope validation.
- Corrected implementation `f294fbd305385eb3fd129ab1f815daaca03d15fa`, run `30990265619`: all required jobs success; 40 service tests, zero skipped.
- Completion-record SHA/CI: this commit / pending exact-SHA CI.
- Queue-archive SHA/CI: not created before completion-record CI.

## 39. Explicit Non-Scope

Not implemented: M6 recovery/responsive closure; M7 final closure; new tables/
migration; collaboration; multi-Job/cross-Workspace Report; rich-text/WYSIWYG;
mandatory PDF/DOCX/LaTeX/PPTX; remote publishing; notebook/script export;
Report-generated science; frontend recomputation; LLM writing/captions/
citations; Recipe execution/rerun; Plan/Job/ToolCall/queue/Adapter execution;
new science/Phase 10N/11/12; RAG/memory/multi-agent/plugins/enterprise;
arbitrary Python/shell/filesystem; external science API; new provider/SDK/dependency.

## 40. Phase 10M Readiness

```text
Phase 10M-5:
READY_WITH_EXPLICIT_LIMITS

Phase 10M-6:
REVIEWER_GATE
```

## 41. Queue State

```text
Phase 10M-5:
COMPLETE / AWAITING_VERIFIED_QUEUE_ARCHIVE

Phase 10M-6:
REVIEWER_GATE / AWAITING REVIEWER PROMPT

TASK_BLOCK_COUNT = 1
```

## 42. Automatic M6 Entry

```text
NO
PHASE_10M6_EXECUTABLE_TASK_CREATED = NO
```

## 43. Next Action

```text
Verify this completion-record exact-SHA CI, then archive only Phase 10M-5.
Do not create, queue, or execute Phase 10M-6.
```

## 44. Final Repository State

- Corrected implementation SHA: `f294fbd305385eb3fd129ab1f815daaca03d15fa`.
- Implementation exact-SHA CI: `30990265619`, success.
- Completion-record SHA/CI: this commit / pending.
- Queue-archive SHA/CI: not created / pending.
- Expected post-commit: `HEAD == origin/master`, clean, migration head 0007,
  M5 completed block retained, task count one, no M6 executable task.

# Phase 10M-6 Workspace Save / Reload / Recovery / Responsive Closure Result

## 1. Conclusion

```text
PASS / COMPLETE / AWAITING_COMPLETION_RECORD_CI
```

## 2. Baseline and Entry Gate

- M5 corrected implementation: `f294fbd305385eb3fd129ab1f815daaca03d15fa`, CI `30990265619`, success.
- M5 completion: `aaef8bf254de3569f4411a85138dfb0c8c79497f`, CI `30991190818`, success.
- M5 archive: `56bec17792fff86a99c3d280ab754a69fff6c51b`, CI `30991896855`, success.
- Initial HEAD/origin: M5 archive SHA; branch `master`; worktree clean.
- Migration head: `0007_phase10m1_workspace_domain`; initial task count: 0.
- M6 admitted as the sole executable task; M7 executable task absent.

## 3. M0-M5 Decision Compliance

All sealed Workspace, Panel, Selection, renderer, Report/Recipe, persistence,
source, security, and phase-order authorities remain unchanged.

## 4. Save/Reload/Recovery Authority Audit

Existing Workspace GET/PATCH/ETag, persisted Job/ToolCall/Artifact records,
Artifact storage, and immutable Report/Recipe history support M6 without a new
authority. Redis events are observational, not the recovery authority.

## 5. Canonical State Ownership

- Server persisted: Workspace title/revision/layout/panel order/saved fallback,
  explicit pinned selection, immutable source bindings, finalized Report/Recipe.
- URL: exact `panel` and versioned canonical selection.
- Memory: pending durable edits, camera/hover/playback/filter/dialog state and
  unfinalized Report draft.
- `LOCAL_STORAGE_CANONICAL_AUTHORITY = NONE`
- `SESSION_STORAGE_CANONICAL_AUTHORITY = NONE`
- `OFFLINE_CANONICAL_WORKSPACE_COPY = NONE`

## 6. Explicit Workspace Save

Save uses the current quoted ETag with `If-Match`, submits only sealed mutable
fields, aborts obsolete requests, suppresses duplicate submission, and applies
the server-returned revision/ETag only after success.

## 7. Dirty-State Semantics

Dirty state compares canonical durable fields only. No-op Save issues no PATCH
and creates no revision; Report draft dirty state remains independent.

```text
WORKSPACE_NOOP_SAVE_REQUESTS = 0
WORKSPACE_NOOP_SAVE_REVISION_GROWTH = 0
```

## 8. Optimistic Concurrency

Typed 412 handling preserves local edits, reports base/server revision, and
requires explicit confirmation before loading server state.

```text
WORKSPACE_CONFLICT_SILENT_OVERWRITE = 0
WORKSPACE_CONFLICT_AUTOMATIC_MERGE = 0
WORKSPACE_CONFLICT_LOCAL_EDIT_LOSS_WITHOUT_CONFIRMATION = 0
```

## 9. Revision Cap

```text
MAX_LAYOUT_REVISIONS = 128
WORKSPACE_REVISION_CAP_HISTORY_DELETION = 0
WORKSPACE_REVISION_CAP_AUTOMATIC_WORKSPACE_REPLACEMENT = 0
```

The 129th revision is rejected with typed UX while Workspace and Report reads
remain available and unsaved edits remain in memory.

## 10. Reload and Layout Restoration

Reload restores exact Workspace revision, panel membership/order, durable
title/layout, valid saved panel fallback, pinned fallback, and finalized
Report/Recipe history without loading inactive heavy payloads.

## 11. Panel Resolution Precedence

Valid explicit URL panel, then valid persisted fallback when URL is absent,
then deterministic default. An invalid explicit panel produces a typed error
and never silently falls back.

## 12. Selection Resolution Precedence

Valid explicit URL selection, then valid pinned fallback only when URL
selection is absent, otherwise none. Invalid/stale explicit selection remains
typed and is never rebound by latest, nearest, label, or index.

## 13. Deep Link

Deep links contain exact Workspace, panel, and bounded canonical selection
only. Transient state, payloads, signed URLs, paths, and secrets are excluded;
over-cap state is rejected without truncation.

## 14. Refresh / Back / Forward

Refresh and history navigation restore exact route state, reject stale async
commits, and create no PATCH, Pin, revision, Report, Recipe, Plan, Job, or queue
write. `WORKSPACE_RELOAD_HIDDEN_WRITES = 0`.

## 15. Running / Interrupted Job Recovery

Nonterminal status is revalidated through bounded persisted GET observation,
visibility recovery, cancellation, and terminal-stop behavior. Missing Redis
events fall back to PostgreSQL Job/ToolCall/dependency/Artifact authority.

```text
WORKSPACE_REFRESH_PLAN_CREATION_GROWTH = 0
WORKSPACE_REFRESH_JOB_CREATION_GROWTH = 0
WORKSPACE_REFRESH_TOOLCALL_CREATION_GROWTH = 0
WORKSPACE_REFRESH_QUEUE_MESSAGE_GROWTH = 0
WORKSPACE_RECOVERY_AUTOMATIC_RERUN = 0
```

## 16. Partial / Failed / Blocked Recovery

Successful independent panels remain readable; failed and blocked scope,
missing outputs, warnings, and limitations remain visible without invented
claims or rewritten runtime authority.

## 17. Stale / Missing / Deleted Source Recovery

Typed states cover stale Dataset/Profile/resource/checksum, missing metadata or
MinIO payload, missing interpretation, foreign scope, and unavailable source.

```text
STALE_SOURCE_LATEST_REBINDING = 0
```

## 18. Historical Compatibility

AnalysisPlan 0.1 remains `LEGACY_READ_ONLY` without invented dependencies;
Plan 0.2 preserves exact graph/bindings. Legacy Artifact and Report/Recipe
records remain read-only with typed unavailable fields and unchanged hashes.

## 19. Finalized Report / Recipe Recovery

Exact immutable history, Report detail, paired Recipe, semantic hashes,
warnings/limitations, and JSON/Markdown exports survive close/reopen and do not
resolve through a latest-record heuristic.

## 20. Session Draft Honesty

```text
REPORT_DRAFT_PERSISTENCE = SESSION_ONLY
REPORT_DRAFT_SERVER_WRITES = 0
REPORT_DRAFT_LOCALSTORAGE_WRITES = 0
REPORT_DRAFT_AUTOMATIC_FINALIZE = 0
```

Persistent disclosure and navigation/unload protection state that refresh or
close discards an unfinalized draft.

## 21. First-Time / Empty / Loading / Error UX

Workspace guidance and distinct metadata/panel/Artifact/interpretation/Report/
Save/revalidation states replace blank or generic-error presentation.

## 22. Terminology and Information Hierarchy

Goal, scope, status, results, warnings, findings/evidence, Report, and recovery
actions lead the UI; audit JSON and exact developer detail remain subordinate.

## 23. Responsive Desktop

The sealed header, side navigation, active central panel, and single Inspector
remain; M6 adds Save/recovery state without redesigning the desktop shell.

## 24. Mobile

```text
mobile viewport = 390x844
horizontal overflow = 0
minimum touch target = 44x44 CSS px
```

One active panel, context drawer, panel switcher, Inspector bottom sheet, and
single-surface Report workflow provide focus trap/return and long-text wrapping.

## 25. Accessibility

Semantic landmarks/headings, keyboard panel/Save/conflict/Report workflows,
visible focus, dialog/sheet focus containment, live status, non-color states,
text/table/WebGL alternatives, reduced motion, and reflow are covered.

## 26. Long Content / Large Artifact

Long titles, warnings, provenance, IDs, tables, audit JSON, 32 panels, 128
revisions, and near-cap metadata remain bounded, wrapped, collapsible, or
internally scrollable without hiding mandatory disclosures.

## 27. Loading / Cancellation / Cache

Cache and request identity include exact Workspace revision, panel, Artifact
checksum/contract, and source hash. Route/panel/revision/checksum/unmount changes
abort or suppress obsolete work.

```text
INITIAL_HEAVY_ARTIFACT_PAYLOAD_REQUESTS = 0
INACTIVE_HEAVY_ARTIFACT_PAYLOAD_REQUESTS = 0
STALE_RESPONSE_STATE_COMMITS = 0
```

## 28. WebGL Lifecycle

```text
MAX_ACTIVE_HEAVY_VIEWERS = 1
WEBGL_CONTEXT_GROWTH = 0
LISTENER_GROWTH = 0
OBSERVER_GROWTH = 0
DUPLICATE_CANVAS = 0
REPORT_PREVIEW_WEBGL_CONTEXTS = 0
```

## 29. API and Persistence

Existing Workspace POST/GET/PATCH/project list/panel/layout-history routes,
Job/Artifact/interpretation reads, and seven M5 Report composition routes are
reused unchanged.

```text
new public endpoints = 0
new tables = 0
migration = unchanged
migration head = 0007_phase10m1_workspace_domain
```

## 30. Scientific Integrity

```text
WORKSPACE_COPIED_ARTIFACT_PAYLOADS = 0
FRONTEND_DUPLICATE_SCIENTIFIC_AUTHORITY = NONE
FRONTEND_SCIENTIFIC_RECOMPUTATION = NONE
WORKSPACE_RECOVERY_GENERATED_SCIENTIFIC_VALUES = 0
WORKSPACE_RECOVERY_GENERATED_SCIENTIFIC_CLAIMS = 0
RECOMMENDATION_EXECUTION_AUTHORITY = NONE
```

## 31. LLM / DeepSeek Compliance

```text
NEW_LLM_CALL_SITES = 0
M6_SAVE_RELOAD_RECOVERY_REQUIRES_LLM = NO
REAL_LLM_CALLS = 0
DEEPSEEK_POLICY_REGRESSION = PASS
```

The permanent real-provider policy remains DeepSeek-only with sole key source
`DEEPSEEK_KEY`; M6 made no provider request.

## 32. Security

```text
NO_WORKSPACE_RECOVERY_ARBITRARY_CODE_EXECUTION = PASS
NO_WORKSPACE_RECOVERY_SHELL_AUTHORITY = PASS
NO_WORKSPACE_RECOVERY_FILESYSTEM_AUTHORITY = PASS
NO_WORKSPACE_RECOVERY_ARTIFACT_JAVASCRIPT = PASS
NO_WORKSPACE_RECOVERY_ARTIFACT_HTML_EXECUTION = PASS
NO_WORKSPACE_RECOVERY_IFRAME_EXECUTION = PASS
NO_WORKSPACE_RECOVERY_DYNAMIC_MODULE_EXECUTION = PASS
NO_WORKSPACE_RECOVERY_EXTERNAL_URL_EXECUTION = PASS
NO_WORKSPACE_RECOVERY_CROSS_PROJECT_ACCESS = PASS
NO_WORKSPACE_RECOVERY_CROSS_JOB_ARTIFACT_INJECTION = PASS
NO_WORKSPACE_RECOVERY_STALE_IDENTITY_REBINDING = PASS
NO_WORKSPACE_RECOVERY_CHECKSUM_BYPASS = PASS
NO_WORKSPACE_RECOVERY_SECRET_DISCLOSURE = PASS
NO_WORKSPACE_RECOVERY_PRIVATE_PATH_DISCLOSURE = PASS
NO_WORKSPACE_RECOVERY_STACK_DISCLOSURE = PASS
NO_WORKSPACE_RECOVERY_AUTOMATIC_RERUN = PASS
NO_WORKSPACE_RECOVERY_PLAN_CREATION = PASS
NO_WORKSPACE_RECOVERY_JOB_CREATION = PASS
NO_WORKSPACE_RECOVERY_QUEUE_AUTHORITY = PASS
NO_LOCALSTORAGE_CANONICAL_BACKUP = PASS
NO_SECRET_PATTERN_HITS = PASS
```

## 33. Acceptance IDs

```text
expected = 8
implemented = 8
missing = 0
extra = 0
duplicate = 0
```

- M6-A01: recovery model/Shell Save tests; save/conflict/cap captures.
- M6-A02: exact snapshot/fallback tests; reload/state-ownership evidence.
- M6-A03: M3/M6 URL/history tests; deep-link/Back/Forward browser evidence.
- M6-A04: persisted recovery service test; running/partial/stale/history captures.
- M6-A05: composer/Shell tests; Report/Recipe and draft-loss evidence.
- M6-A06: typed component states; browser/accessibility evidence.
- M6-A07: focus/mobile implementation; 390x844 capture and metrics.
- M6-A08: lifecycle/security/evidence tests; exact-SHA service and CI gates.

## 34. Tests

- Focused frontend: 34 passed; full frontend: 411 passed.
- Full backend: 1148 passed, 43 skipped; focused backend: 69 passed.
- Evidence integrity: 4 passed; `uv lock --check`, diff check, docs and secret
  scan passed; typecheck and production build passed.
- Local Chromium/Firefox/WebKit/390x844 replay passed.
- Local service-backed: `UNAVAILABLE` (Docker/flag unavailable), not reported as pass.
- CI service-backed: 41 passed, 0 skipped, 0 failed, 0 errors.
- Configured npm audit mirror: `404_NOT_IMPLEMENTED`; `npm audit = UNAVAILABLE`.

## 35. Browser Matrix

Chromium 129, Firefox 130, WebKit 18 at 1440x1050 and Chromium 129 at
390x844 passed Save/conflict/reload, Report recovery, accessibility, network,
console, and overflow assertions with zero unexpected errors/external requests.

## 36. Service-Backed Evidence

Exact-SHA CI used PostgreSQL, Redis, MinIO, migration head 0007, persisted
current Plan 0.2/Job/ToolCall/Artifact/Workspace, explicit Save, typed conflict,
revision cap, missing-event terminal recovery, checksum, and no execution-object
growth. Summary: `41 passed, 0 skipped, 0 failed, 0 errors`.

## 37. Performance

Development/browser evidence, not a production capacity claim: metadata-first
load, no inactive heavy requests, no hidden/no-op writes, no stale commits, one
active heavy Viewer, and zero context/listener/observer/canvas growth.

## 38. Production Behavior Changes

Users can explicitly Save allowed durable state, see dirty/saved/conflict/cap
status, reopen deterministic state, use exact links/history, recover running,
partial, failed, blocked, stale, missing, historical and finalized Report/Recipe
views, and work on desktop/mobile with keyboard and screen-reader support.

## 39. Files Changed

Workspace shell/Report composer/recovery model/styles; tests and CI; browser,
service, evidence runners; Phase 10M docs/evidence; persistent and task records.

```text
database schema = unchanged
migration = unchanged
migration head = 0007_phase10m1_workspace_domain
dependencies = unchanged
lockfile = unchanged
Workspace contracts = unchanged
Panel contract = unchanged
Selection contract = unchanged
Report/Recipe contracts = unchanged
renderer registry authority = unchanged
scientific Adapter authority = unchanged
```

## 40. Commit / CI History

- `3bae949559c1049e0bcfd5de21d4d375e1a488aa`, CI `31017695192`: Unit/Frontend passed; service fixture lacked legacy support tables.
- `c7db3ca4a651847b49a994eb7e4ad9a21d32eca7`, CI `31018789969`: Unit/Frontend passed; fixture expected RUNNING for correct Plan 0.1 legacy projection.
- `ec2a7e572510be08a7d02c5fcd338807b39ba9e3`, CI `31019983444`: Unit/Frontend passed; service fixture actor mismatched TestClient authorization.
- Corrected implementation `65e80ba915140e29db08dc053c1d218206daaa03`, CI `31020968546`: success.
- Completion-record SHA/CI: this commit / pending exact-SHA CI.
- Queue-archive SHA/CI: not created before completion-record CI.

## 41. Explicit Non-Scope

M7/final closure, Phase 10N+, schema/migration/public API/contracts,
localStorage/sessionStorage/IndexedDB authority, durable drafts, offline,
collaboration/merge, multi-Job/cross-Workspace aggregation, latest rebinding,
rerun/execution, new science, frontend recomputation, LLM recovery, new provider,
arbitrary code/shell/filesystem, RAG/memory/multi-agent/plugins are not implemented.

## 42. Phase 10M Readiness

```text
Phase 10M-6:
READY_WITH_EXPLICIT_LIMITS

Phase 10M-7:
REVIEWER_GATE
```

Phase 10M as a whole is not declared complete.

## 43. Queue State

```text
Phase 10M-6:
COMPLETE / AWAITING_VERIFIED_QUEUE_ARCHIVE

Phase 10M-7:
REVIEWER_GATE / AWAITING REVIEWER PROMPT

TASK_BLOCK_COUNT = 1
```

## 44. Automatic M7 Entry

```text
NO
PHASE_10M7_EXECUTABLE_TASK_CREATED = NO
```

## 45. Next Action

```text
Verify this completion-record exact-SHA CI, then archive only Phase 10M-6.
Do not create, queue, or execute Phase 10M-7.
```

## 46. Final Repository State

- Implementation SHA: `65e80ba915140e29db08dc053c1d218206daaa03`.
- Implementation exact-SHA CI: `31020968546`, success.
- Completion-record SHA/CI: this commit / pending.
- Queue-archive SHA/CI: not created / pending.
- Expected post-commit: `HEAD == origin/master`, branch `master`, clean,
  migration head 0007, M6 block retained, task count one, M7 task absent.

# Phase 10M-7 Workspace Integration + Browser/API/Service Evidence Closure Result

## 1. Conclusion

```text
PASS / COMPLETE / AWAITING_COMPLETION_RECORD_CI
```

Phase 10M-7 integration closure is complete. The M7 task remains present until
this completion-record exact-SHA CI succeeds and the separate queue-archive
commit is verified.

## 2. M6 Baseline

- Implementation: `65e80ba915140e29db08dc053c1d218206daaa03`, CI
  `31020968546`, success.
- Completion: `aec09cebb33ae9673063a22f8fc772737c9a47b4`, CI
  `31022245082`, success.
- Archive: `200212b164041e38626d6b948c7fe64c772ca6ce`, CI
  `31060008583`, success.
- Entry HEAD/origin: M6 archive SHA; branch `master`; clean worktree; migration
  head `0007_phase10m1_workspace_domain`; task count zero.

## 3. Corrected Entry Gate

```text
PHASE_10M7_ENTRY_GATE = PASS_WITH_AUTHORIZED_DOCUMENT_RECONCILIATION
PHASE_10M7_ACCEPTANCE_SOURCE = ACCEPTANCE_AND_TEST_PLAN
PHASE_10M7_QUEUE_ADMISSION = AUTHORIZED
PHASE_10M7_READINESS = READY_FOR_R0_RECONCILIATION
ACCEPTANCE_RECONCILIATION_WAS_PART_OF_M7 = YES
PREVIOUS_ACCEPTANCE_GATE_BLOCK_WAS_SUPERSEDED = YES
```

The known backlog/lock/manifest drift matched the corrected reviewer prompt.
No implementation, lifecycle, or contract gate failed at entry.

## 4. Acceptance Source Authority

`docs/phase10m/phase10m_acceptance_and_test_plan.md` was the temporary canonical
source for exact M7 IDs, titles, and responsibilities. Its registry contained
exactly eight non-conflicting definitions.

## 5. Four-Document Reconciliation

The exact registry was synchronized into the acceptance plan, implementation
backlog, execution lock, and execution manifest. A marker-bounded validator
parses only canonical registry sections and treats references elsewhere as
informational.

## 6. Exact M7 Acceptance Registry

- M7-A01 `Service-backed`: PostgreSQL + Redis + MinIO full Workspace lifecycle, 0 skipped/failed.
- M7-A02 `Scientific integrity`: Adapter -> Runtime -> Artifact -> renderer/evidence authority remains exact.
- M7-A03 `Historical compatibility`: 0.1/0.2, modern/legacy/partial/missing-source cases retained.
- M7-A04 `Full tests`: Backend/frontend/typecheck/build/lock/migration/closure all pass.
- M7-A05 `Browser`: Chromium/Firefox/WebKit/mobile/accessibility/WebGL current evidence passes.
- M7-A06 `Security`: All Workspace security markers and secret scan pass.
- M7-A07 `Evidence`: Sanitized API/DOM/network/console/screenshots/performance manifest verifies.
- M7-A08 `Lifecycle`: Implementation, completion, and verified queue archive exact-SHA CI pass.

## 7. Acceptance Integrity Semantics

```text
M7 canonical source = phase10m_acceptance_and_test_plan.md
expected IDs = 8
implemented IDs = 8
missing IDs = 0
extra IDs = 0
duplicate canonical registry entries = 0
conflicting canonical definitions = 0
canonical registry shorthand entries = 0
document-wide references = informational only
```

## 8. Pipeline Authority Map

The verified path is source registration -> DataProfile 2.0 -> AnalysisIntent
1.0 -> EligibilityResolution 1.0 -> Planner decision -> AnalysisPlan 0.1/0.2
-> PlanValidator -> Job/ToolCall/dependency execution -> Artifact/lineage ->
interpretation/claims/evidence -> ScientificWorkspace 1.0 -> typed panels,
selection, and Inspector -> Report/Recipe -> Save/reopen.

DataProfile owns data semantics; Eligibility owns capability applicability;
Plan owns declared execution; Runtime orchestrates; Adapter calculates;
Artifact persists scientific results; interpretation owns grounded narrative;
Workspace owns reference/navigation/presentation; Report is an immutable
delivery snapshot; Recipe is declarative and non-executable.

## 9. Identity Continuity

The retained verified DeepSeek phonon case preserves exact Project,
Dataset/version, Profile/hash, Intent/hash, Eligibility/hash, Decision/hash,
Plan/hash/schema, graph/bindings, Job, three ToolCalls, 21 Artifact checksums,
EvidenceBundle/hash, and Interpretation/hash through current Workspace and
Report/Recipe repositories. Filename, MIME, display label, array index, row
order, latest, nearest, and fuzzy matching provide no identity authority.

```text
retained real DeepSeek calls = 16
M7_NEW_REAL_LLM_CALLS = 0
NEW_LLM_CALL_SITES = 0
NO_PROVIDER_FALLBACK = PASS
DEEPSEEK_KEY_SECRET_DISCLOSURE = 0
```

## 10. AnalysisPlan 0.1

Historical Plan 0.1 remains readable as ordered independent/sequential work.
Workspace and Report/Recipe projection invent no dependency graph or Artifact
binding. Historical records remain read-only where modern identity is absent.

## 11. AnalysisPlan 0.2

The retained replay preserves exact graph hash, two formal bindings,
producer/consumer ports, ToolCalls, Artifact contracts/checksums, immutable
lineage, Workspace panels, and Recipe dependency representation.

## 12. Dependency Success

Topological dependency execution, producer outputs, consumer inputs,
successful Artifact lineage, panel projection, and exact Recipe graph are
covered by L3, M4-M6 regressions and the M7 retained replay.

## 13. Partial / Failed / Blocked

Regression evidence preserves successful independent branches, failed
ToolCalls, blocked descendants, missing desired outputs, and mandatory Report
disclosures. No branch is omitted or rerun.

```text
SUCCESSFUL_BRANCH_ARTIFACT_LOSS = 0
FAILED_BRANCH_OMISSION = 0
BLOCKED_DEPENDENCY_OMISSION = 0
AUTOMATIC_RERUN = 0
LEGACY_DEPENDENCY_INVENTION = 0
```

## 14. Viewer Matrix

Dataset Materials Explorer, Materials ML, Composition Space, Structure,
Trajectory, Phonon, Brillouin Zone, Volumetric, generic numeric/table,
metadata-only, inert legacy fallback, and unsupported contract/version paths
retain their M4 exact contract/version dispositions. Unknown versions do not
guess renderers. WebGL canvas and browser screenshots are not scientific
authority.

## 15. Selection / Inspector

Canonical versioned exact selection retains source Artifact hash, stable sample
or scientific object identity, origin panel, compatibility result, Inspector
identity, URL round trip, Back/Forward, and explicit Pin/Clear/Copy. Only sealed
formal mappings are exercised.

```text
SELECTION_ARRAY_INDEX_AUTHORITY = NONE
SELECTION_DISPLAY_LABEL_AUTHORITY = NONE
SELECTION_FILENAME_AUTHORITY = NONE
SELECTION_FUZZY_MATCHING = NONE
SELECTION_LATEST_REBINDING = NONE
```

## 16. Interpretation / Evidence

Grounded interpretation remains bound to exact Job, Plan, Artifacts, claims,
evidence IDs, source checksums, limitations, and failed/blocked scope. Missing
interpretation yields typed unavailable findings without an automatic LLM
call or invented conclusion.

## 17. Report / Recipe

Current Workspace sources produce deterministic no-write preview, explicit
atomic finalize, idempotent immutable history, exact paired Recipe, canonical
JSON, and UTF-8 LF Markdown. The Recipe retains Profile, Intent, Eligibility,
Plan version, tools/params/bindings/dependencies/contracts and all no-execution
flags.

```text
PREVIEW_REPORT_WRITES = 0
PREVIEW_RECIPE_WRITES = 0
REPORT_GENERATED_SCIENTIFIC_VALUES = 0
REPORT_GENERATED_SCIENTIFIC_CLAIMS = 0
REPORT_SCIENTIFIC_RECOMPUTATION = 0
RECIPE_EXECUTION_AUTHORITY = NONE
RECIPE_PLAN_CREATION_AUTHORITY = NONE
RECIPE_JOB_CREATION_AUTHORITY = NONE
RECIPE_QUEUE_AUTHORITY = NONE
```

## 18. Save / Reopen

Existing PATCH/quoted ETag/If-Match authority verifies explicit Save, revision
advance, no-op suppression, two-client conflict with local edit preservation,
confirmed server reload, close/reopen, deterministic layout and pinned fallback,
deep link, Back/Forward, and zero hidden writes.

## 19. Stale / Missing / Historical

Typed recovery covers stale Dataset/Profile/resource, checksum mismatch,
missing Artifact metadata or MinIO bytes, missing interpretation, foreign scope,
Plan 0.1, legacy contracts, and historical Report/Recipe. Unaffected panels
remain readable; no latest rebinding, replacement Artifact, or identity upgrade
occurs.

## 20. API Matrix

No route was added. Existing routes verified include:

- `POST /datasets/{dataset_id}/files`, `POST /datasets/{dataset_id}/profile`;
- `POST /planner/intents`, `POST /planner/intents/{intent_id}/clarification`;
- `POST /planner/jobs`, `GET /planner/jobs/{job_id}` and `/events`,
  `/artifacts`, `/interpretations`;
- `POST /workspaces`, `GET/PATCH /workspaces/{workspace_id}`;
- `GET /workspaces/{workspace_id}/panels` and `/layout-revisions`;
- all seven existing Workspace Report composition/history/Recipe/export routes.

Strict DTO, scope, ETag, checksum, idempotency, malformed input, duplicate key,
oversize, foreign scope, stale hash, and no-hidden-write behavior remain sealed.

## 21. PostgreSQL

Migration head 0007 and 27 expected tables were verified. Profile, Intent,
decision, Plan, Job, ToolCall, dependency, Artifact metadata, interpretation,
Workspace, panels, revisions, Report, and Recipe persistence remain current
authorities.

## 22. Redis

Queue/event availability and status observation pass. Redis is not durable
scientific authority; missing-event recovery reads persisted PostgreSQL state
and never duplicates enqueue.

## 23. MinIO

Artifact byte persistence, exact checksum retrieval, authorization, missing
object state, and tamper rejection pass without storage-key disclosure.

## 24. Browser Matrix

Chromium, Firefox, WebKit, and Chromium mobile all passed current M7 replay.
M2-M6 selection, Gallery/Viewer, Report/Recipe, Save/recovery runners passed in
the same exact-SHA CI.

```text
unexpected console errors = 0
unexpected page errors = 0
unexpected failed responses = 0
unapproved external requests = 0
```

## 25. Mobile

```text
viewport = 390x844
horizontal overflow = 0
minimum touch target = 44x44 CSS px
```

The one-active-panel model, context drawer, panel switcher, Inspector bottom
sheet, Report single-surface flow, Save, recovery, long text, and exact identity
wrapping remain intact.

## 26. Accessibility

Keyboard core flows, logical headings/landmarks, visible focus, route/panel
focus placement, drawer/dialog/sheet traps and return, live announcements,
non-color states, table/chart/WebGL alternatives, reduced motion, and 200%
reflow pass the retained M3-M6 and current browser gates.

## 27. Performance

```text
INITIAL_HEAVY_ARTIFACT_PAYLOAD_REQUESTS = 0
INACTIVE_HEAVY_ARTIFACT_PAYLOAD_REQUESTS = 0
ADJACENT_HEAVY_PANEL_PREFETCH = 0
MAX_ACTIVE_HEAVY_VIEWERS = 1
STALE_RESPONSE_STATE_COMMITS = 0
```

These are development acceptance results, not production capacity claims.

## 28. WebGL Lifecycle

The existing 50-cycle M4 runner remains authoritative; M7 adds no WebGL owner.

```text
WEBGL_CONTEXT_GROWTH = 0
LISTENER_GROWTH = 0
OBSERVER_GROWTH = 0
ANIMATION_LOOP_GROWTH = 0
DUPLICATE_CANVAS = 0
DUPLICATE_PAYLOAD_REQUEST_GROWTH = 0
REPORT_PREVIEW_WEBGL_CONTEXTS = 0
```

## 29. Scientific Integrity

```text
WORKSPACE_COPIED_ARTIFACT_PAYLOADS = 0
FRONTEND_DUPLICATE_SCIENTIFIC_AUTHORITY = NONE
FRONTEND_SCIENTIFIC_RECOMPUTATION = NONE
WORKSPACE_GENERATED_SCIENTIFIC_VALUES = 0
WORKSPACE_GENERATED_SCIENTIFIC_CLAIMS = 0
REPORT_GENERATED_SCIENTIFIC_VALUES = 0
REPORT_GENERATED_SCIENTIFIC_CLAIMS = 0
STALE_SOURCE_LATEST_REBINDING = 0
RECOMMENDATION_EXECUTION_AUTHORITY = NONE
```

## 30. Security

```text
NO_WORKSPACE_ARBITRARY_CODE_EXECUTION = PASS
NO_WORKSPACE_SHELL_AUTHORITY = PASS
NO_WORKSPACE_FILESYSTEM_AUTHORITY = PASS
NO_ARTIFACT_JAVASCRIPT_EXECUTION = PASS
NO_ARTIFACT_HTML_EXECUTION = PASS
NO_ARTIFACT_IFRAME_EXECUTION = PASS
NO_ARTIFACT_DYNAMIC_MODULE_EXECUTION = PASS
NO_EXTERNAL_ARTIFACT_URL_EXECUTION = PASS
NO_CROSS_PROJECT_ACCESS = PASS
NO_CROSS_WORKSPACE_ACCESS = PASS
NO_CROSS_JOB_ARTIFACT_INJECTION = PASS
NO_CROSS_PROJECT_REPORT_SOURCE = PASS
NO_STALE_IDENTITY_REBINDING = PASS
NO_CHECKSUM_BYPASS = PASS
NO_SECRET_DISCLOSURE = PASS
NO_PRIVATE_PATH_DISCLOSURE = PASS
NO_STACK_DISCLOSURE = PASS
NO_STORAGE_KEY_DISCLOSURE = PASS
NO_RECOVERY_PLAN_CREATION = PASS
NO_RECOVERY_JOB_CREATION = PASS
NO_RECOVERY_TOOLCALL_CREATION = PASS
NO_RECOVERY_QUEUE_AUTHORITY = PASS
NO_PROVIDER_FALLBACK = PASS
NO_SECRET_PATTERN_HITS = PASS
```

Artifact, Report, Recipe, URL, title, caption, warning, and provenance strings
remain inert. No localStorage/sessionStorage canonical backup is introduced.

## 31. Tests

- Focused Phase 10M backend: `78 passed`; focused final M7: `12 passed`.
- Full backend: `1156 passed`, one documented local-environment skip, 43
  integration tests deselected for the separate service gate.
- Full frontend: `411 passed`; typecheck PASS; build PASS with existing
  Plotly/glslify warnings.
- Browser: Chromium/Firefox/WebKit/390x844 PASS.
- Service-backed exact-SHA CI: `42 passed, 0 skipped, 0 failed, 0 errors`.
- Migration, no-skipped, lock, acceptance, evidence manifest, docs links,
  TASKS structure, closure integrity, and secret scan: PASS.
- Local service-backed: UNAVAILABLE because Docker was unavailable; CI is the
  service authority.
- `npm audit`: UNAVAILABLE because the configured mirror returned
  `404_NOT_IMPLEMENTED`; it is not reported clean.

## 32. Files Changed

M7 changed tests, browser/service/evidence runners, CI integrity checks,
canonical documentation, evidence, and persistent lifecycle records. Production
source changes are zero.

```text
database schema = unchanged
migration = unchanged
migration head = 0007_phase10m1_workspace_domain
public API contracts = unchanged
dependencies = unchanged
lockfile = unchanged
Workspace contracts = unchanged
Selection contract = unchanged
Report/Recipe contracts = unchanged
AnalysisPlan contracts = unchanged
renderer registry authority = unchanged
scientific Adapter authority = unchanged
```

## 33. Production Behavior Changes

```text
Production behavior changes: NONE
```

M7 is evidence-only closure; it does not add a Workspace feature or scientific
capability.

## 34. Phase 10M Final Capability Matrix

Workspace persistence/shell, typed Gallery, Dataset Explorer, Materials ML,
Composition Space, Report, Recipe, Save, and Reload are READY. Canonical
selection, scientific Viewers, interpretation, recovery, and accessibility are
READY_WITH_EXPLICIT_LIMITS. Legacy records are LEGACY_READ_ONLY; unknown
contracts are UNSUPPORTED with inert metadata. The full table is retained in
`docs/phase10m/phase10m_final_capability_matrix.md`.

## 35. Known Limitations

One Workspace per Job; no multi-Job/cross-Workspace aggregation or selection;
no collaboration, offline-first authority, durable unfinalized Report draft,
generic workflow editor, arbitrary DAG, runtime replanning, automatic rerun,
Recipe execution, frontend/Report science generation, or identity upgrade.
Missing/tampered/stale sources remain unavailable rather than rebound.

## 36. Commit / CI History

- Implementation: `21ea4559e097cec649515b35c7f45b63f8eb8511`.
- CI `31065250027` attempt 1: cancelled after the unchanged Playwright browser
  runtime download stalled for 31 minutes; Unit and service jobs had passed.
- CI `31065250027` attempt 2: success with unchanged SHA and coverage.
- Completion-record SHA/CI: this commit / pending exact-SHA CI.
- Queue-archive SHA/CI: not created before completion-record CI.

## 37. Queue State

```text
Phase 10M-7:
PASS / COMPLETE / AWAITING_VERIFIED_QUEUE_ARCHIVE

Phase 10M:
COMPLETE / READY_WITH_EXPLICIT_LIMITS / AWAITING_VERIFIED_ARCHIVE

Phase 10N-0:
REVIEWER_GATE / AWAITING REVIEWER PROMPT

TASK_BLOCK_COUNT = 1
```

## 38. Phase 10N Non-Entry

```text
NO
PHASE_10N0_EXECUTABLE_TASK_CREATED = NO
```

Phase 10N science, contracts, migration, API, dependencies, tools, automatic
execution, RAG, memory, multi-agent, and plugin work were not started.

## 39. Final Repository State

- Implementation SHA/CI: `21ea4559e097cec649515b35c7f45b63f8eb8511` /
  `31065250027` attempt 2, success.
- Completion-record SHA/CI: this commit / pending.
- Queue-archive SHA/CI: not created / pending.
- Expected after this commit: `HEAD == origin/master`, branch `master`, clean
  worktree, migration head 0007, M7 task retained as complete awaiting archive,
  task count one, Phase 10N executable task absent.

# Phase 10M-7 Queue Archive Integrity Correction Record

- Queue-archive candidate: `5fc11b0465113ce7ad31fec3fa9d7e42d8d623c8`.
- Exact-SHA CI: `31068038057`, failed in Unit only because
  `test_phase10m7_document_links_and_phase10n_gate` required one active M7 task
  after the verified archive deletion. Frontend/browser/build and
  PostgreSQL/Redis/MinIO passed.
- Root cause: lifecycle integrity test covered implementation/completion state
  but not the sealed zero-task archive state.
- Correction: accept exactly one M7 task before archive or zero tasks after
  archive; preserve balanced delimiters, reject any executable Phase 10N task,
  and require the Phase 10N-0 reviewer gate.
- Corrected queue-archive SHA/CI: this commit / pending exact-SHA CI.
# Phase 10N-0 Professional Scientific Capability Gap Audit + Scope Seal Result

## 1. Conclusion

```text
PASS / COMPLETE / REVIEWER_APPROVAL_REQUIRED
```

## 2. Baseline

- M7 implementation: `21ea4559e097cec649515b35c7f45b63f8eb8511`, CI
  `31065250027` attempt 2, success.
- M7 completion: `95d448815838848e9c8089e8653afc57ab8c740d`, CI
  `31067470666`, success.
- Failed archive candidate: `5fc11b0465113ce7ad31fec3fa9d7e42d8d623c8`,
  CI `31068038057`, Unit lifecycle assertion failed while service/browser/build passed.
- Corrected archive authority: `88e8ba86079fabb96670c497b63eec8c1cc95a7c`,
  CI `31068772689`, success.
- Entry: HEAD and origin/master `88e8ba8`, branch `master`, clean worktree,
  migration `0007_phase10m1_workspace_domain`, task count zero.

## 3. Production Behavior Changes

```text
Production Behavior Changes:
NONE
```

## 4. Current Professional Scientific Maturity

The platform has production-ready composition, Dataset Materials Explorer,
Materials ML, Composition Space, phonon and BZ foundations; structure,
trajectory, theoretical XRD, static RDF and volumetric capabilities are ready
with explicit limits. N1-N5 professional products are not yet implemented.

## 5. Current Capability Inventory

The audited inventory covers 53 Registry tools, current Adapters, Artifact
families, Profile 2.0, renderers, interpretation, Workspace and Report/Recipe.
Registry-only mappings, parsers, Viewers and fixtures are not counted as
production scientific authority.

## 6. Dependency Versions

Locked/runtime versions include pymatgen `2026.5.4`, pymatgen-core `2026.5.18`,
ASE `3.29.0`, NumPy `2.4.6`/`2.5.0` marker branches, SciPy `1.17.1`/`1.18.0`,
pandas `3.0.3`, Plotly `6.8.0`, scikit-learn `1.9.0`, spglib `2.7.0`, pymatviz
`0.18.0`, and Three.js `0.185.1`. Phonopy and seekpath are not top-level locked.

## 7. Dependency Licenses

The audit records pymatgen/Plotly MIT, ASE LGPL-2.1-or-later, pandas and
scikit-learn BSD, spglib BSD-3, and the declared mixed permissive NumPy/SciPy
metadata. No package was installed, upgraded or enabled.

## 8. Upstream Capability Audit

`UPSTREAM_ONLINE_VERIFICATION = UNAVAILABLE`. Locked files, runtime metadata,
current source/tests and official release metadata already retrieved were used.
Upstream library support is never represented as repository implementation.

## 9. Existing Registry / Adapter / Artifact Surface

Current authorities include structure summary/viewing, distance-cutoff
coordination histogram, theoretical XRD, static RDF, trajectory import/viewing,
phonon band/DOS, BZ, volumetric, Dataset/ML/Composition, interpretation and
Workspace delivery. N1-N5 Tools, Adapters and Artifact contracts remain absent.

## 10. DataProfile Readiness

Profile 2.0 provides structure, trajectory, phonon, volumetric, resource,
readiness and sample-identity facts. An additive backward-compatible Profile
2.1 proposal is assigned to future phases for stable site, experimental XRD,
trajectory validity and electronic readiness facts; no N0 contract was registered.

## 11. Workspace / Viewer Readiness

Existing metadata-first Workspace and strict renderer registry are reusable.
Future N1-N5 panels must preserve active-only heavy loading, inert fallback,
exact selection, Inspector detail, mobile presentation and static alternatives.

## 12. Interpretation / Report / Recipe Readiness

Bounded projectors remain the only LLM-visible fact surface. Reports compose
persisted facts without recomputation; Recipes retain exact declarations and
have no Plan, Job, queue or execution authority.

## 13. Identity Seal

Structure/site, periodic neighbor, trajectory atom/frame/time, experimental
peak and electronic spin/k-point/band/channel identities are source-hash bound.
Filename, MIME, display label, row/index, nearest, fuzzy and latest matching are prohibited.

## 14. Units Seal

Canonical proposals cover angstrom, degrees, dimensionless coordination/RDF,
picoseconds, angstrom squared, angstrom squared per picosecond, electronvolts,
states per electronvolt and reciprocal units. Conversion is deterministic,
server-side, provenance-recorded and never silently assumed.

## 15. Scientific Wording Seal

Claims are algorithm- and policy-qualified. Absolute chemical bonding,
experimental phase confirmation, unqualified bulk diffusion, GW correction and
platform-generated electronic structure claims are prohibited.

## 16. Reference Fixture Hierarchy

The sealed order is direct checked-in numeric fixtures, exact-version official
fixtures, controlled analytic fixtures, cross-library references, licensed
public data, then mapping-only evidence. Screenshots are not numeric authority.

## 17. Numeric Tolerance Policy

Each future capability owns quantity-specific absolute/relative, positional,
angular, peak, energy, fit and deterministic-order tolerances with units,
source, platform variance and explicit failure meaning. No pass-driven tuning is allowed.

## 18. Performance Cap Plan

Bounded proposed caps cover N1 structures/sites/neighbors, N2 centers/faces,
N3 points/peaks/bytes, N4 frames/atoms/bins/windows/fits and N5 bands/k-points/
DOS/projections. Future phases must measure small, medium and near-cap fixtures.

## 19. Security Boundary

All inputs remain inert and bounded with UTF-8, depth/size, finite-number,
duplicate/prototype-key, decompression and timeout controls. No Python, shell,
filesystem, notebook, script, external scientific API, HTML/JS/module/URL,
cross-project binding, checksum bypass, secret/path/stack or Recipe execution is authorized.

## 20. N1 Coordination Scope

CrystalNN/VoronoiNN proposals bind exact pymatgen versions, explicit parameters,
periodic-image neighbors, weights, coverage and diagnostics. The scientific term
is `algorithm-derived local coordination`; the distance-cutoff histogram coexists.

## 21. N2 Local Environment / Polyhedra Scope

N2 consumes exact N1 Artifacts through Plan 0.2 and proposes versioned reference
geometry, class/score, vertices/faces and distortion metrics. Bond valence and
oxidation-state inference remain out of scope.

## 22. N3 Experimental XRD Scope

N3 separates experimental ingestion from existing theoretical XRD and seals
normalization, optional preprocessing, SciPy peak detection, deterministic
one-to-one matching and mismatch disclosure. Rietveld, refinement, phase search
and confirmation claims are excluded.

## 23. N4 Trajectory Analytics Scope

N4 seals whole/window/species RDF, server-side unwrapped MSD, directional MSD
and diagnostics-bounded diffusion fitting. Stable atom identity, explicit time,
cell policy and no silent ballistic/transient fitting are mandatory.

## 24. N5 Electronic Band / DOS Scope

N5 only consumes bounded supplied electronic output. It seals energy/Fermi,
spin, k-path, band, total DOS and completeness-qualified element/orbital DOS
projection semantics. Projected bands, Fermi surface and electronic calculation remain future scope.

## 25. N6 Integration / Evidence Scope

N6 is integration/evidence only across Profile, Intent, Eligibility, Plan,
Runtime, Artifact, interpretation, Workspace and Report/Recipe for N1-N5. It is
not a catch-all feature phase.

## 26. Long-List Classification

Fermi surface, Bader/charge topology, Rietveld and phase-fraction refinement,
automatic DFT, defects/surfaces and advanced research capabilities remain
`FUTURE_SCOPE` or outside N1-N6. No Future Scope item was promoted.

## 27. Migration Decisions

N1-N6 propose no database table, column or migration. Migration head remains
`0007_phase10m1_workspace_domain`.

## 28. Public API Decisions

N1-N6 reuse existing Registry/Plan/Job/Artifact/Workspace APIs. New public API
families are `NO` for every phase.

## 29. Contract / DataProfile Decisions

Future versioned Registry/Artifact and additive Profile 2.1 contracts are
`YES_PROPOSED_FOR_REVIEW` with phase ownership and backward compatibility. N0
registered no runtime contract.

## 30. Dependency Decisions

Current locked pymatgen/NumPy/SciPy/pandas/Plotly are sufficient for the sealed
proposals. New dependency and lockfile changes are `NO` for N1-N6.

## 31. Implementation Sequence

The reviewer sequence is sealed unchanged: N1 coordination, N2 local
environment/polyhedra, N3 experimental XRD, N4 trajectory analytics, N5
electronic Band/DOS, N6 integration/evidence.

## 32. Decision Registry

N-D001 through N-D033 are contiguous. All required decisions are:

```text
SEALED_FOR_REVIEWER_APPROVAL
```

## 33. Acceptance IDs

```text
expected = 12
implemented = 12
missing = 0
extra = 0
duplicate registry entries = 0
conflicting definitions = 0
canonical registry shorthand entries = 0
```

The exact registry is:

1. `N0-A01 BASELINE_AND_REPOSITORY_FACT_AUDIT`
2. `N0-A02 DEPENDENCY_VERSION_LICENSE_AND_UPSTREAM_CAPABILITY_AUDIT`
3. `N0-A03 CURRENT_PROFESSIONAL_SCIENTIFIC_CAPABILITY_INVENTORY`
4. `N0-A04 IDENTITY_UNITS_AUTHORITY_AND_SCIENTIFIC_WORDING_SEAL`
5. `N0-A05 N1_COORDINATION_SCOPE_SEAL`
6. `N0-A06 N2_LOCAL_ENVIRONMENT_AND_POLYHEDRA_SCOPE_SEAL`
7. `N0-A07 N3_EXPERIMENTAL_XRD_COMPARISON_SCOPE_SEAL`
8. `N0-A08 N4_TRAJECTORY_ANALYTICS_SCOPE_SEAL`
9. `N0-A09 N5_ELECTRONIC_BAND_AND_DOS_SCOPE_SEAL`
10. `N0-A10 CROSS_CUTTING_CONTRACT_REFERENCE_TOLERANCE_PERFORMANCE_AND_SECURITY_SEAL`
11. `N0-A11 N1_TO_N6_IMPLEMENTATION_SEQUENCE_ACCEPTANCE_AND_EXECUTION_LOCK`
12. `N0-A12 AUDIT_EVIDENCE_DOCUMENTATION_EXACT_SHA_LIFECYCLE_AND_REVIEWER_GATE`

These titles are identical in the backlog, acceptance plan, execution lock and manifest.

## 34. Tests

- Focused N0 integrity: `6 passed`.
- Local backend: `1162 passed, 44 skipped, 0 failed`; service/environment skips
  are not represented as service PASS.
- Exact-SHA Unit: `1162 passed, 1 documented local-environment skip, 43 deselected`.
- Frontend: `411 passed`; typecheck and production build PASS.
- Browser replay: Chromium, Firefox, WebKit and Chromium 390x844 PASS.
- Exact-SHA service-backed: `42 passed, 0 skipped, 0 failed, 0 errors`.
- Migration, no-skipped, lock, evidence, acceptance, decision, docs, TASKS and
  secret gates: PASS.
- Local service-backed: UNAVAILABLE because Docker is absent; CI is authority.
- `npm audit`: UNAVAILABLE because configured mirror returned `404_NOT_IMPLEMENTED`.

## 35. Evidence

The N0 evidence directory contains 41 LF-normalized hashed entries covering
baseline, lifecycle, dependencies/licenses, inventories, identity/units/wording,
fixtures/tolerances/caps/security, N1-N6 scopes and integrity summaries. Missing,
duplicate, secret, Authorization, private-path and stack entries are zero.

## 36. Files Changed

```text
production source = unchanged
database schema = unchanged
migration = unchanged
migration head = 0007_phase10m1_workspace_domain
public API = unchanged
runtime contracts = unchanged
dependencies = unchanged
lockfile = unchanged
TASKS.md = unchanged
```

## 37. Commit / CI

- Failed audit attempts: none. A pre-commit EOF whitespace check blocked commit
  creation and was corrected before any SHA existed.
- Audit/planning: `8f12bdc13720aae9b022301fbe8b0624245b131d`.
- Audit/planning exact-SHA CI: `31074886038`, success.
- Completion-record SHA/CI: this commit / pending exact-SHA CI.

## 38. Explicit Non-Scope

N1-N6 production tools, Adapters, parsers, Artifacts, Profile implementation,
Viewers, projectors and Report behavior were not implemented. No new science,
DB/API/dependency/LLM/execution authority was added.

## 39. Phase 10N Readiness

```text
Phase 10N-0:
COMPLETE / REVIEWER_APPROVAL_REQUIRED

Phase 10N-1:
REVIEWER_GATE
```

## 40. Queue State

```text
TASK_BLOCK_COUNT = 0

Phase 10N-1:
REVIEWER_GATE / AWAITING REVIEWER PROMPT
```

## 41. Automatic N1 Entry

```text
NO
PHASE_10N1_EXECUTABLE_TASK_CREATED = NO
```

## 42. Final Repository State

- Audit/planning SHA/CI: `8f12bdc13720aae9b022301fbe8b0624245b131d` /
  `31074886038`, success.
- Completion-record SHA/CI: this commit / pending exact-SHA CI.
- Expected after this commit: HEAD equals origin/master, branch `master`, clean
  worktree, migration head 0007, task count zero, N1 task absent.

## 43. Next Action

Return the complete Phase 10N-0 audit and scope seal to the reviewer. Do not
create, queue, or execute Phase 10N-1.

# Phase 10N-1 CrystalNN / VoronoiNN Coordination Result

## 1. Conclusion

PASS / COMPLETE / AWAITING_COMPLETION_RECORD_CI

The implementation exact-SHA CI passed. The completion record is this commit;
queue archive remains pending its own exact-SHA CI. The failed implementation
attempts are retained in Git history.

## 2. N0 Baseline

- N0 audit: `8f12bdc13720aae9b022301fbe8b0624245b131d` / CI `31074886038` success.
- N0 completion: `10c60c21c66f7d37b26bf3cc116cd88a416eafae` / CI `31075564935` success.
- Initial N1 HEAD/origin: `10c60c21c66f7d37b26bf3cc116cd88a416eafae`.
- Branch: `master`; worktree clean at entry; migration head `0007_phase10m1_workspace_domain`.
- Registry baseline 53; task count 0; N1 task admitted only in implementation commit; N2 task absent.

## 3. N0 Approval and Authority Extraction

N-D001 through N-D033 and N1-RD001 through N1-RD009 were followed. R0 closed
the exact contracts before production execution. Scientific authority remains in
the registered backend Adapter and persisted Artifact.

## 4. N1 Acceptance Registry

The exact ten-entry registry is synchronized across the four Phase 10N authority
documents:

`N1-A01 BASELINE_AUTHORITY_ACCEPTANCE_AND_EXACT_CONTRACT_CLOSURE`

`N1-A02 DATAPROFILE_REGISTRY_PARAMETER_AND_ARTIFACT_CONTRACTS`

`N1-A03 CRYSTALNN_COORDINATION_EXECUTION`

`N1-A04 VORONOINN_COORDINATION_EXECUTION`

`N1-A05 EXACT_STRUCTURE_SITE_NEIGHBOR_PERIODIC_IMAGE_IDENTITY_AND_DETERMINISM`

`N1-A06 ELIGIBILITY_PLANNER_PLANVALIDATOR_RUNTIME_PERSISTENCE_AND_NO_FALLBACK`

`N1-A07 WORKSPACE_STRUCTURE_VIEWER_SELECTION_AND_INSPECTOR_INTEGRATION`

`N1-A08 GROUNDED_INTERPRETATION_REPORT_RECIPE_AND_SCIENTIFIC_WORDING`

`N1-A09 REFERENCES_TOLERANCES_PERFORMANCE_ACCESSIBILITY_SECURITY_AND_SERVICE_EVIDENCE`

`N1-A10 THREE_COMMIT_EXACT_SHA_LIFECYCLE_AND_N2_REVIEWER_GATE`

## 5. Acceptance Reconciliation

Expected = 10; implemented = 10; missing = 0; extra = 0; duplicate canonical
registry entries = 0; conflicting definitions = 0; canonical registry
shorthand entries = 0. References outside registry sections are informational.

## 6. N-D Decision Compliance

Exactly two tools were approved. Comparison is deterministic consumer-side
presentation and is not a Tool, Adapter, Job or scientific authority.

## 7. Production Behavior Changes

Added the approved CrystalNN and VoronoiNN coordination capabilities, Profile
2.1 readiness, exact Planner/Eligibility/Runtime/Artifact integration, and the
existing Workspace/Viewer/Selection/Report surfaces. Existing persistence,
Workspace identity, selection authority, Recipe non-execution boundary and
DeepSeek-only policy are unchanged.

## 8. Dependency and Locked-Version Compliance

No dependency or lockfile change. Both tools use pymatgen `2026.5.4` with
pymatgen-core `2026.5.18`, MIT licensed, through
`pymatgen.core.local_env.CrystalNN` and `VoronoiNN`.

## 9. Tool Registry Changes

Old count = 53; approved added count = 2; final count = 55. Added:
`structure.coordination_crystalnn@0.1.0` and
`structure.coordination_voronoinn@0.1.0`. No comparison Tool was added.

## 10. DataProfile Integration

DataProfile 2.1 is additive and keeps 2.0 readable. It records periodicity,
lattice status, site count, occupancy/disorder status, exact resource identity,
coordination readiness and typed reasons. Profile execution authority is none.

## 11. Eligibility Integration

Eligibility distinguishes ready periodic structures from missing lattice,
non-periodic, disorder, partial occupancy, stale and over-cap inputs without
running either algorithm or loading heavy payloads.

## 12. Planner Integration

Exact CrystalNN, exact VoronoiNN and two-step comparison requests preserve both
Tool identities and bounded resolved parameters. Unsupported or non-ready input
does not create an executable plan.

## 13. AnalysisPlan / PlanValidator

Existing Plan 0.1/0.2 is reused. Exact input refs, Tool versions, params and
output contracts are validated; invalid or cross-algorithm bindings are rejected.

## 14. Runtime / Adapter Architecture

QueueWorkerRuntime resolves the exact registered Adapter. Computation is server
side, bounded, deterministic and inert; no network, shell, arbitrary filesystem,
dynamic module or user code authority exists.

## 15. CrystalNN Implementation

CrystalNN is independently instantiated with its sealed bounded parameter schema,
per-site results, algorithm-specific weighted coordination semantics and typed
failure behavior.

## 16. VoronoiNN Implementation

VoronoiNN is independently instantiated with solid-angle weight semantics,
periodic-image relations, bounded cutoff/tolerance parameters and typed
pathological-cell handling.

## 17. Algorithm Isolation and No-Fallback

CrystalNN failure never substitutes VoronoiNN and vice versa. Comparison consumes
only successfully persisted exact Artifacts and preserves incomplete inputs.

## 18. Structure / Site Identity

Results retain project, dataset, job, tool call, source resource/hash and exact
structure hash. Site identities are structure-hash bound; no label, filename,
latest or fuzzy rebinding is used.

## 19. Periodic Neighbor Identity

Each relation retains central/neighbor site IDs, exact integer periodic image,
distance in Angstrom, algorithm-specific weight and algorithm-qualified identity.

## 20. Parameter Contracts

CrystalNN and VoronoiNN schemas use `additionalProperties: false`, bounded finite
values, strict booleans/integers, deterministic defaults, canonical serialization
and persisted SHA-256 parameter hashes.

## 21. Units

Distance is canonicalized to Angstrom. Periodic images are exact dimensionless
integer triplets. Weight and coordination values retain algorithm-specific
semantics and are not conflated.

## 22. Artifact Contracts

Separate `phase10n1.crystalnn_coordination.v1` and
`phase10n1.voronoinn_coordination.v1` payloads retain source identity, resolved
parameters, provenance, coverage, diagnostics, warnings, checksums and bounded
derived data without copying the full structure payload.

## 23. Determinism

Canonical site/neighbor ordering, exact image identity, stable parameter hashes,
canonical JSON and checksum stability are covered by focused tests and generated
reference evidence.

## 24. Coverage and Partial Results

Artifacts report total, eligible, successful, failed, unsupported and zero-
neighbor sites, retained rows, ratio and typed reasons. Partial results are not
represented as complete.

## 25. Scientific Wording

Allowed wording is `algorithm-derived coordination`, `CrystalNN-derived
coordination` and `VoronoiNN-derived coordination`. Definitive bonding, absolute
chemical truth, experimental confirmation and a universally correct algorithm
are prohibited.

## 26. Reference Fixtures

Checked deterministic pymatgen fixtures cover both algorithms, periodic images,
disorder rejection, disagreement and bounded payload generation. Numeric fixture
evidence is separate from screenshots.

## 27. Numeric Tolerances

Periodic images and identities require exact equality. Distances and weights use
quantity-specific documented finite tolerances; no global fuzzy matching or
silent deletion is used.

## 28. Workspace Integration

The typed coordination renderer is lazy and metadata-first. Workspace stores
references and presentation state only; comparison is a deterministic view over
two exact algorithm Artifacts.

## 29. Structure Viewer Overlay

The coordination surface provides table and inert text fallbacks. It renders only
persisted site/neighbor relations and never recomputes geometry in the browser.

## 30. Selection and Inspector

Site selection is exact, structure-hash bound and URL-compatible. Inspector data
includes algorithm/version, site/neighbors, image, distance/unit, weight semantics,
resolved parameters, coverage, warnings, provenance and checksum.

## 31. Grounded Interpretation

The projector exposes bounded algorithm, coverage, ranges, warnings and limits;
LLM interpretation cannot recompute neighbors, invent bonds or resolve algorithm
disagreement.

## 32. Report / Recipe

Report uses persisted summary/table/provenance and mandatory limitations. Recipe
retains Tool/version, params, hashes and source identity while remaining
declarative, non-executable and without Plan/Job/queue authority.

## 33. Historical Compatibility

Existing 2.0 profiles, plans, Artifacts, Workspaces, selection URLs and reports
remain readable. N1 does not reprocess historical records or rebind latest data.

## 34. API Evidence

Existing Profile, Planner/Job, Artifact, Workspace and Report/Recipe routes are
reused. New public API family count = 0.

## 35. PostgreSQL / Redis / MinIO

Exact-SHA CI run `31147539225`: PostgreSQL/Redis/MinIO = 43 passed, 0 skipped,
0 failed, 0 errors; migration head `0007_phase10m1_workspace_domain`.

## 36. Browser Matrix

Exact-SHA CI run `31147539225` passed Chromium, Firefox, WebKit and the N1
coordination replay. Historical M3 replay also passed after the fixture-only
responsive correction.

## 37. Mobile

Chromium mobile viewport = `390x844`; one active panel, zero horizontal overflow,
minimum touch target = 44x44 CSS px, Inspector/table fallback retained.

## 38. Accessibility

Named algorithm controls, semantic status, keyboard site selection, visible focus,
non-color differentiation, table/text alternatives, reduced motion and mobile
targets are covered by component and browser evidence.

## 39. Performance Caps

Caps are enforced at 32 structures, 5000 sites, 1000 neighbors/site, 50000
retained rows, 16 MiB Artifact bytes and 120 seconds. Initial and inactive heavy
payload requests remain zero.

## 40. Viewer Lifecycle

Coordination is a light/table renderer and uses zero WebGL contexts. Existing M4
50-cycle lifecycle gate remains green; no duplicate canvas/listener/observer or
payload growth was introduced.

## 41. Security

`NO_COORDINATION_ARBITRARY_CODE_EXECUTION=PASS`, `NO_COORDINATION_SHELL_AUTHORITY=PASS`,
`NO_COORDINATION_FILESYSTEM_AUTHORITY=PASS`, `NO_COORDINATION_EXTERNAL_NETWORK=PASS`,
`NO_COORDINATION_DYNAMIC_MODULE=PASS`, artifact HTML/JavaScript/iframe/external URL
execution = PASS, cross-project/cross-job/foreign binding = PASS, stale rebinding
= 0, checksum bypass = 0, secret/private-path/stack/storage-key disclosure = 0,
algorithm fallback/substitution = 0, secret scan = PASS.

## 42. LLM / DeepSeek Compliance

`NEW_LLM_CALL_SITES = 0`; `N1_COORDINATION_REQUIRES_LLM = NO`;
`N1_REAL_LLM_CALLS = 0`; `DEEPSEEK_POLICY_REGRESSION = PASS`.

## 43. Acceptance Results

Expected = 10; implemented = 10; missing = 0; extra = 0; duplicate registry
entries = 0; conflicting definitions = 0; canonical registry shorthand entries = 0.

## 44. Tests

Local: backend `1177 passed, 45 skipped` (local environment skips only), frontend
`414 passed`, focused N1 `54 passed`, focused Workspace frontend `38 passed`,
typecheck/build/lock/diff checks passed. CI: Unit, Frontend/Typecheck/Build,
browser matrix and service-backed no-skipped gates passed. `npm audit` is
UNAVAILABLE because the configured mirror returns `404_NOT_IMPLEMENTED`.

## 45. Evidence

Evidence directory: `docs/phase10n/evidence/phase10n1_crystalnn_voronoinn_coordination/`.
Manifest, browser captures, reference results, API/service summaries, security,
accessibility, lifecycle and acceptance checks passed with no secret-bearing data.

## 46. Files Changed

Production implementation changed only within approved N1 behavior. Database
schema = unchanged; migration = unchanged; migration head = 0007; public API
family = unchanged; dependencies/lockfile = unchanged; Workspace and Selection
authority = unchanged; Report/Recipe execution authority = unchanged.

## 47. Commit / CI History

- Failed implementation `81eed119121bceb98f725bab8c5a659f4022e00c` / CI `31137374140`:
  M3 exact semantic replay drift and isolated actor fixture failure.
- Failed corrected implementation `7f3efab3357f171884afad2082347d1007741392` / CI
  `31147007026`: M3 was fixed; service Artifact version exceeded the legacy 32-char
  persistence field.
- Corrected implementation `08b5eec39bed4fcc93d0a4ef36eb385ba0e9ecc4` / CI
  `31147539225`: success.
- Completion-record SHA/CI: this commit / pending exact-SHA CI.
- Queue archive SHA/CI: pending; no archive claim is made here.

## 48. Explicit Non-Scope

N2 local environments/polyhedra, N3 experimental XRD, N4 trajectory analytics,
N5 electronic Band/DOS and N6 integration closure are not implemented. No new
science, migration, API family, dependency, Plan architecture, arbitrary code,
Recipe execution or Phase 10N-2 task was created.

## 49. Phase 10N Readiness

Phase 10N-1: PASS / COMPLETE / AWAITING_COMPLETION_RECORD_CI.

Phase 10N-2: REVIEWER_GATE / AWAITING REVIEWER PROMPT.

## 50. Queue State

During completion-record CI: `TASK_BLOCK_COUNT = 1`; the N1 task remains active.
N2 remains a reviewer gate and has no executable task.

## 51. Automatic N2 Entry

NO. `PHASE_10N2_EXECUTABLE_TASK_CREATED = NO`.

## 52. Final Repository State

At completion-record creation: HEAD = `08b5eec39bed4fcc93d0a4ef36eb385ba0e9ecc4`,
origin/master equals HEAD, branch `master`, worktree clean, migration head
`0007_phase10m1_workspace_domain`, Registry count 55, task count 1, N2 task absent.

Return the complete N1 result after completion-record and queue-archive exact-SHA
CI; do not create, queue or execute Phase 10N-2.

# Phase 10N-2 Local Environment + Coordination Polyhedra Result

## 1. Conclusion

PASS / COMPLETE / AWAITING_COMPLETION_RECORD_CI.

## 2. N1 Baseline

N1 implementation `08b5eec39bed4fcc93d0a4ef36eb385ba0e9ecc4` / CI
`31147539225`, completion `3c937c4ecf98358e44687538396facc827ec3a4b` /
CI `31148371587`, and verified archive
`a9319c2da44f8794ef7a66347d8f7a0dffe4aa5b` / CI `31156152013` are successful
ancestors. Entry was clean master at the archive SHA, migration head 0007,
Registry 55 and zero tasks.

## 3. Entry Gate

`PHASE_10N2_ENTRY_GATE=PASS`; N1 authority and reviewer approval were verified,
N2/N3 production and executable tasks were absent, and R0/queue admission were
authorized.

## 4. N2-R0 Contract Closure

R0 froze the single Tool, strict params, catalog, Artifact, identities, metrics,
errors, fixtures, tolerances, caps and no-recomputation boundary with zero
implementation-critical TBDs.

## 5. Acceptance Registry

The four canonical documents define the same ten entries: `N2-A01` baseline/R0;
`N2-A02` N1 dependency; `N2-A03` classification; `N2-A04` polyhedra/metrics;
`N2-A05` identity/determinism; `N2-A06` planning/runtime/persistence; `N2-A07`
Workspace/Viewer/selection; `N2-A08` interpretation/Report; `N2-A09` evidence;
and `N2-A10` lifecycle/N3 gate.

## 6. N-D Decision Compliance

Existing scientific authority, identity, unit, persistence, Plan 0.2, Workspace,
Report/Recipe, security and phase-order decisions remain intact.

## 7. Production Behavior Changes

The platform now computes geometry-derived local environments and coordination
polyhedra from exact persisted N1 results and presents them through existing
planning, Runtime, Artifact, Workspace and delivery authorities.

## 8. Registry Change 55 To 56

Exactly `structure.local_environment_polyhedra@0.1.0` was added. Final Registry
count = 56; comparison Tool and additional scientific Tool count = 0.

## 9. N1 Dependency Authority

N2 binds N1 Artifact ID/checksum, contract, producer Tool/version, algorithm,
structure hash and parameter hash. CrystalNN-derived and VoronoiNN-derived N2
results remain independently attributable.

## 10. No N1 Recomputation

`N2_RECOMPUTED_N1_NEIGHBORS=0`; `N2_INDEPENDENT_NEIGHBOR_SEARCH=0`;
`N2_COORDINATION_ALGORITHM_FALLBACK=0`. N2 consumes and never rewrites N1 rows.

## 11. Algorithm And Version

Classification uses `mdi.angular_spectrum_reference_match@1.0.0`; deterministic
face construction uses locked `scipy.spatial.ConvexHull@1.17.1`. Both operate
server-side over bounded exact N1 neighbor geometry.

## 12. Geometry Reference Catalog

The versioned allowlist contains validated bounded references only; custom code,
coordinates, modules and unverified geometry identifiers are rejected.

## 13. Parameter Contracts

Python, JSON Schema and TypeScript contracts reject extra properties and
non-finite/unbounded values, resolve canonical defaults and persist parameter
hashes.

## 14. Local Environment Classification

Per-site results retain reference candidates, scores, status, source algorithm,
coverage and warnings. Tie handling exposes alternatives or ambiguity rather
than selecting by iteration order.

## 15. Polyhedron Construction

Vertices retain exact N1 neighbor-relation and periodic-image identity. Backend
faces are canonicalized from deterministic bounded hull output; the browser does
not create scientific face authority.

## 16. Distortion Metrics

Approved radial spread, bond-length distortion, angular deviation and bounded
polyhedron volume/area metrics retain explicit definitions and units. No
stability, bond-strength or chemistry score is emitted.

## 17. Structure, Site And Neighbor Identity

Project, Job, structure/resource hashes, structure-bound site identities and
algorithm-qualified N1 neighbor identities are exact. Filename, display label,
latest, row position and fuzzy geometry are never authority.

## 18. Polyhedron Identity

Polyhedron identity binds the N2 Artifact, source N1 checksum, central site,
canonical neighbor-relation set, periodic images, contract and parameter hash.

## 19. Determinism

Site, neighbor, vertex, face, candidate and warning orders are canonical; stable
parameter/content hashes are regression-tested without browser-order dependence.

## 20. Ambiguity

Near-equal candidates preserve scores and alternatives under the sealed tie
tolerance. Numeric minima are not represented as chemical truth.

## 21. Degenerate And Partial Behavior

Insufficient, coplanar, duplicate and degenerate vertices produce typed component
states. Classification or metrics may remain available only where the contract
explicitly permits partial output; no face or label is invented.

## 22. Scientific Wording

UI and delivery use `geometry-derived local environment` and `coordination
polyhedron constructed from the persisted neighbor set`. Definitive bonding,
hybridization, oxidation state, stability and experimental confirmation are
prohibited.

## 23. Profile And Eligibility

DataProfile remains 2.1. Eligibility combines periodic-structure readiness with
exact N1 availability or producibility, contract/checksum compatibility, identity
and caps; Profile contains no N2 computed result.

## 24. Planner

Exact CrystalNN or VoronoiNN requests preserve the requested producer. Ambiguous
algorithm requests require clarification; no latest/first/preferred result is
selected.

## 25. Plan 0.2 Dependency

N1 producer output binds the N2 consumer through existing bounded AnalysisPlan
0.2 ports. An exact persisted N1 Artifact can be reused without rerunning N1.

## 26. PlanValidator

Validation rejects wrong Tool/contract/checksum/structure/project/job bindings,
unbounded params and unsupported dependency outputs without plan repair.

## 27. Runtime

QueueWorkerRuntime resolves the registered Adapter, verifies immutable inputs,
enforces caps and persists inert output. Failed N1 descendants are BLOCKED and
independent successful branches are retained without fallback.

## 28. Artifact Contracts

`phase10n2.local_environment_polyhedra.v1` stores bounded N2-derived site,
classification, vertex, face, metric, coverage and diagnostic data plus exact
lineage; it copies neither full structure nor full N1 payload.

## 29. PostgreSQL

Exact-SHA CI `31258820229` verified Job/ToolCall/Artifact/Workspace/Report state
through PostgreSQL with current migration head.

## 30. Redis

The same CI verified queue/events and dependency state without recovery-created
plans, jobs or ToolCalls.

## 31. MinIO

The same CI verified N1/N2 payload persistence, checksums and exact retrieval.
Service summary: 44 passed, 0 skipped, 0 failed, 0 errors.

## 32. Workspace

The metadata-first local-environment panel provides environment and metric tables,
source provenance, deterministic source comparison and an inert polyhedron SVG
projection without copying scientific payload into Workspace state.

## 33. Structure Viewer

Persisted central sites, vertices, faces and N1 relations are shown distinctly.
No frontend neighbor, face, classification or distortion computation exists.

## 34. Selection

Exact Artifact, environment, polyhedron, vertex and face selections bind project,
job, checksum, structure, site and source N1 identity. Legacy Selection 1.0 URL
tokens remain canonical and Back/Forward restoration passes.

## 35. Inspector

Inspector surfaces N2 and N1 Tool/algorithm versions, checksums, structure/site,
reference scores/status, neighbor images, faces, metrics, units, params, coverage,
warnings, limitations and provenance.

## 36. Interpretation

The deterministic projector exposes bounded distributions, coverage, metrics,
warnings and selected-site facts. LLM authority excludes classification, hulls,
metrics, chemistry and algorithm choice.

## 37. Algorithm-Source Comparison

Consumer-side tables preserve side-by-side CrystalNN/VoronoiNN-derived results,
including disagreement and incomplete inputs. They do not average, merge, rank or
create a new scientific authority.

## 38. Report And Recipe

Report composes persisted figures/tables, lineage, warnings and limits without
recomputation. Recipe records exact N1/N2 dependency bindings and remains
declarative, non-executable and without Plan/Job/queue authority.

## 39. Historical Compatibility

Historical N1 Artifacts, Workspaces, reports and pre-N2 selection URLs remain
readable. Missing N2 is NOT_AVAILABLE and never triggers backfill or read-time
computation.

## 40. References

Direct controlled tetrahedral, octahedral, lower-coordination, distorted,
ambiguous, periodic, degenerate, algorithm-source and near-cap fixtures are stored
with source/version/license/hash provenance.

## 41. Tolerances

Identity, periodic image, reference version and checksum use exact equality.
Coordinates, distances, angles, scores, distortion, volume, area and ties use
quantity-specific documented tolerances; no global fuzzy match exists.

## 42. Performance

Small, medium, near-cap and over-cap cases cover evaluated sites, neighbors,
candidates, vertices, faces, time, memory and bytes. Explicit caps prevent
unbounded permutations and output growth.

## 43. Viewer Lifecycle

Fifty view/source/site switch cycles produced zero WebGL, listener, observer,
animation-loop, canvas, payload-request or stale-overlay growth.

## 44. Accessibility

Keyboard site/environment navigation, named controls, visible focus, non-color
states, text/table alternatives, 44px mobile targets, 200% reflow and reduced
motion are covered; WebGL is not required to read scientific values.

## 45. Security

No arbitrary code, shell, filesystem, notebook, external network or dynamic
module authority exists. Artifact HTML/JS/iframe/URL execution, cross-project/job
binding, stale/fuzzy rebinding, checksum bypass, oxidation inference, bond valence,
definitive-bond claims and secret/path/stack/storage-key disclosure all remain
prohibited and tested.

## 46. LLM And DeepSeek

`NEW_LLM_CALL_SITES=0`; `N2_REQUIRES_LLM=NO`; `N2_REAL_LLM_CALLS=0`;
`DEEPSEEK_POLICY_REGRESSION=PASS`.

## 47. Tests

Local backend: 1196 passed, 1 documented environment skip, 45 integration
deselected; frontend: 424 passed before the compatibility regression test and 23
selection tests after it; focused N2 backend 25 passed and focused N2 frontend 32
passed. Typecheck, build, lock, migration, evidence and diff checks passed.

## 48. Browser Matrix

CI `31258820229` passed Chromium, Firefox, WebKit and Chromium 390x844 N2 replay,
plus prior Workspace replays. Console/page errors, unexpected failed responses,
unapproved external requests and mobile overflow = 0.

## 49. Evidence

`docs/phase10n/evidence/phase10n2_local_environment_coordination_polyhedra/`
contains authority, contracts, fixtures, Runtime, Workspace, browser, lifecycle,
accessibility, security and manifest evidence with 57 normalized entries and zero
secret-bearing content.

## 50. Files Changed

Production changes are limited to approved N2 contracts, one Registry entry,
Adapter/planning/runtime integrations and typed Workspace presentation. Database
schema = unchanged; migration = unchanged; migration head =
`0007_phase10m1_workspace_domain`; public API family = unchanged; dependencies =
unchanged; lockfile = unchanged; DataProfile remains 2.1.

## 51. Commit And CI History

- Initial implementation `6cb7a534faab5a63f1aa197dc9c202e62d8983aa` / CI
  `31253016285`: failed M3 additive selection compatibility and service fixture.
- Corrected implementation `2b4dacf400400f5d1a68352d358346b4638d6cb9` / CI
  `31258820229`: success.
- Completion-record SHA/CI: this commit / pending exact-SHA CI.
- Queue-archive SHA/CI: pending; no archive success is claimed here.

## 52. Explicit Non-Scope

N3 XRD, N4 trajectory analytics, N5 electronic products, additional neighbor or
environment algorithms, oxidation state, bond valence, DFT, generic workflows,
automatic rerun, arbitrary execution and external scientific APIs are absent.

## 53. Acceptance Results

Expected = 10; implemented = 10; missing = 0; extra = 0; duplicate registry
entries = 0; conflicting definitions = 0; canonical registry shorthand entries
= 0.

## 54. Queue State

During completion-record CI, `TASK_BLOCK_COUNT=1`; the N2 task remains active.
Phase 10N-3 is reviewer-gated and has no executable task.

## 55. Automatic N3 Entry

NO. `PHASE_10N3_EXECUTABLE_TASK_CREATED=NO`.

## 56. Final Repository State

At completion-record creation, implementation authority is
`2b4dacf400400f5d1a68352d358346b4638d6cb9` / CI `31258820229`, branch master,
HEAD equals origin/master, migration head 0007, Registry 56, task count 1 and N3
task absent. Completion and archive SHAs remain pending their exact-SHA gates.

Return the complete N2 result only after completion-record and queue-archive
exact-SHA CI. Do not create, queue or execute Phase 10N-3.
