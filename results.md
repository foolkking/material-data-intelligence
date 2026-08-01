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
