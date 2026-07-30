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
